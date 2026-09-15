# 2026 Agent 生产级面试专题：性能、可靠性、Eval、Session、Memory 与 Token 治理

> 本文不是“12 道题的简答题答案”，而是把这组题当成一套 **生产级 Agent Runtime 设计题** 来回答。
>
> 讨论重点：性能归因、自动化评测、灰度发布、Tool 容错、故障归因、限流与熔断、Redis/Session、多租户隔离、长期记忆、Memory 膨胀、Token 溢出、死循环检测。
>
> 实际项目对照优先使用：**nanobot、AgentDock、OpenViking、Pi 类 Agent Harness**。对于当前项目源码里没有直接实现的能力，会明确写成“企业级补强”，不会把设计建议写成项目现状。

---

# 0. 先用一张图理解这 12 道题到底在考什么

这 12 道题表面分散，其实都在问同一个问题：

> **如何把一个概率性的 LLM Tool Loop，变成一个可观测、可限流、可恢复、可评测、可多租户运行的生产系统？**

可以把整个系统拆成五层：

```text
                         AgentDock
                 ┌────────────────────┐
                 │ Control Plane      │
                 │ tenant / user      │
                 │ agent / container  │
                 │ task / event       │
                 │ quota / lifecycle  │
                 └─────────┬──────────┘
                           │
                           ▼
                    Agent Runtime
         ┌────────────────────────────────┐
         │ nanobot / Pi-like Harness      │
         │ Session → Context → LLM        │
         │        → Tool → Observation    │
         │        → Next Iteration        │
         └───────────┬─────────────┬──────┘
                     │             │
             Context Plane      Tool Plane
                     │             │
                     ▼             ▼
              OpenViking      MCP / Java API
           Memory/Resource     DB / HTTP / MQ
                     │             │
                     └──────┬──────┘
                            ▼
                     Business Truth
```

生产问题几乎都出现在这些“边界”上：

```text
Context 太大                → Token / latency / attention dilution
LLM 决策错误                → wrong tool / wrong args / hallucination
Tool 不稳定                 → timeout / retry storm / UNKNOWN
多用户共享                  → session / memory / permission leakage
版本迭代                    → regression / canary / rollback
Loop 不能收敛               → repeated tool / no-progress / cost explosion
没有完整 Trace              → 最终只知道“答错了”，不知道哪里错
```

所以真正的主线不是“Prompt 怎么写”，而是：

> **Runtime/Harness 用确定性的工程约束，把模型的不确定性限制在可接受范围内。**

---

# Q1. Agent 整套链路性能瓶颈大概率出现在哪一环？检索、推理还是 Tool？怎么排查和优化？

## 1. 面试官真正考什么

这题不是让你猜“LLM 最慢”。它在考：

1. 你是否知道 Agent 是 **多轮循环系统**，不是一次模型请求；
2. 你能否做 **端到端性能分解**；
3. 你是否能区分：单次耗时、排队时间、重复执行、长尾 P99；
4. 你能否证明优化到底优化了哪一层。

真正生产里很常见的情况是：

> 单个组件都不算特别慢，但 Agent 多跑了两轮 LLM、多调了三次 Tool，最终整体从 4 秒变成 15 秒。

## 2. 先建立 Agent Latency Model

一轮 Agent Run 总耗时可以粗略写成：

```text
T_total
≈ T_ingress
+ Σ T_context(i)
+ Σ T_retrieval(i)
+ Σ T_llm(i)
+ Σ T_tool(i)
+ T_queue
+ T_retry
+ T_persist
```

注意不是：

```text
T_total = T_llm
```

例如：

```text
Run = 13.4s

context build             0.6s
retrieval + rerank        0.9s
LLM round #1              2.8s
tool A queue wait         0.7s
tool A HTTP               1.1s
tool A retry              1.3s
LLM round #2              2.6s
tool B                    1.0s
LLM round #3              2.1s
persist/stream            0.3s
```

看到这里，真正问题可能不是模型推理，而是：

```text
Tool retry
+
不必要的第 3 轮 LLM
+
queue wait
```

## 3. 必须做 Span 级 Trace，而不是只记录 request_duration

推荐 Trace：

```text
agent.run
├── session.resolve
├── context.build [iteration=1]
├── retrieval
│   ├── bm25
│   ├── dense
│   ├── fusion
│   └── rerank
├── llm.request [iteration=1]
├── tool.execute [tool=query_energy]
│   ├── queue.wait
│   ├── http.client
│   └── postgres.query
├── context.build [iteration=2]
├── llm.request [iteration=2]
└── persist.final
```

至少记录：

```text
trace_id
run_id
turn_id
iteration
tool_call_id
tool_name
model
input_tokens
output_tokens
context_tokens
queue_wait_ms
provider_latency_ms
tool_latency_ms
retry_count
http_status
error_kind
```

### 为什么 queue_wait 必须单独记

假设 Tool 实际执行只 300ms，但线程池/连接池等了 2 秒：

```text
service time = 300ms
queue wait   = 2000ms
```

如果只看“Tool latency = 2.3s”，很容易误判成业务接口慢。

## 4. 三类典型性能瓶颈怎么判断

### A. Retrieval 瓶颈

现象：

```text
retrieval P99 很高
rerank topK 很大
vector DB CPU 高
metadata filter 低效
```

优化顺序：

```text
先 ACL/metadata filter
→ ANN candidate 控制
→ BM25/Dense 并行
→ fusion
→ 只对小集合 rerank
→ parent/context expansion
```

不要把 200 个候选都送 Cross-Encoder。

### B. LLM 瓶颈

要拆成：

```text
TTFT（首 Token 时间）
generation duration
total input tokens
output tokens
round count
```

很多时候不是“模型慢”，而是 context 太大。

例如：

```text
20k token prompt → 3.8s TTFT
4k token prompt  → 1.2s TTFT
```

这时应该先优化 Context，而不是直接换模型。

### C. Tool 瓶颈

看：

```text
connection pool acquire
DNS/TLS
HTTP RTT
DB lock/query
provider 429
retry amplification
serialization payload
```

尤其要查：

```text
Agent retry 3 次
Tool Adapter retry 3 次
HTTP client retry 3 次
```

理论最坏调用次数：

```text
3 × 3 × 3 = 27
```

这类 Retry Amplification 是 Agent 线上常见灾难。

## 5. Loop Amplification：Agent 性能最容易被忽略的根因

Agent 不是普通 RPC，所以必须监控：

```text
LLM rounds / successful task
tool calls / successful task
repeated tool rate
argument repair count
replan count
```

假设：

```text
Model A 每轮快 20%
但平均需要 4.2 轮

Model B 每轮慢 10%
但平均只需要 2.1 轮
```

最终 Model B 反而可能更快、更便宜。

所以性能优化单位应该是：

> **Cost/Latency per Successful Task**

而不是“单次 LLM latency”。

## 6. nanobot / AgentDock 实际怎么结合

当前 nanobot `AgentHook` 有 iteration 和 Tool execution 生命周期切点，非常适合挂 tracing；`AgentRunner` 是明确的 tool-capable loop，所以可以按 iteration 观测，而不是把整个 Agent 当一个黑盒。

AgentDock 当前 README 明确有：

```text
Task/Event Stream
live token meter
iteration count
elapsed timer
mid-flight cancel
usage dashboard
```

因此更合理的架构是：

```text
AgentDock
  负责 task/container/tenant 级观测
      ↓
nanobot AgentHook
  负责 iteration/tool 级观测
      ↓
Java OpenTelemetry
  负责 HTTP/JDBC/业务服务级观测
```

最后通过同一个 `trace_id/run_id` 串起来。

## 7. 面试口述版

> Agent 性能不能猜“模型最慢”，我会按一次 Run 的真实生命周期做 Span 拆分：Context、Retrieval、每轮 LLM、每个 Tool、下游 HTTP/SQL、排队和 Retry 都单独测 P50/P95/P99。尤其 Agent 有 Loop Amplification，同一个任务多一轮 LLM、多两次 Tool，影响通常比单次模型快 300ms 更大。实际项目里可以用 AgentDock 看 Task/Token/Iteration，再用 nanobot AgentHook 抓每轮和 Tool 边界，把 traceparent 继续传到 Java 服务和 JDBC，最后优化 Cost/Latency per Successful Task，而不是只优化单个接口。

---

# Q2. 如何搭建 Agent 自动化评测体系？如何量化任务成功率、幻觉率、用户解决率？

## 1. 最大误区：把 Agent Eval 做成“答案相似度”

Agent 不只是生成文字，还做：

```text
理解
→ 规划
→ 检索
→ Tool Selection
→ 参数生成
→ 外部执行
→ 状态更新
→ 最终回答
```

所以 Eval 至少要评四个层次：

```text
Outcome      最终业务任务有没有完成
Trajectory   过程是否合理
Safety       有没有越权/错误副作用
Efficiency   花了多少轮、多少 Tool、多少 Token
```

## 2. Golden Case 不是 input + expected text

生产级 case 建议定义：

```yaml
case_id: lighting_alarm_017
input: "分析昨晚高新区异常能耗，有明确故障才创建工单"
initial_state:
  project_id: p-101
  existing_work_orders: []
fixtures:
  energy_result: abnormal
  alarm_result: device_fault
allowed_tools:
  - query_energy
  - query_alarm
  - create_work_order
forbidden_tools:
  - delete_device
expected_outcome:
  work_order_count: 1
trajectory_constraints:
  - query_energy_before_create_work_order
  - query_alarm_before_create_work_order
  - create_work_order_at_most_once
hard_guards:
  - no_cross_project_access
  - no_false_success_claim
graders:
  - business_state
  - tool_sequence
  - argument_correctness
  - groundedness
```

重点是：

> **最终正确答案不是唯一判定标准。**

## 3. Task Success Rate 怎么定义

不要让 LLM 自评。

例如“创建工单”的 success 不是模型说：

```text
已创建工单
```

而是业务系统真实存在：

```text
work_order_id != null
AND project_id == expected_project
AND status in valid_states
```

因此：

```text
Task Success Rate
= 成功达到业务后置条件的 runs / 总有效 runs
```

对于纯问答类任务，可以用：

```text
Reference-based grader
Evidence-based grader
Human label
LLM-as-judge（只能作为一个 grader，不能是唯一事实源）
```

## 4. 幻觉率不要只定义一个指标

建议拆成：

```text
Unsupported Claim Rate
  没有证据支持的事实性声明比例

Wrong-State Claim Rate
  与业务真实状态冲突的声明比例

Citation Mismatch Rate
  引用存在，但引用内容不支持结论

Fabricated Tool Result Rate
  模型声称 Tool 返回了不存在的数据
```

特别重要：

```text
ToolResult.status = UNKNOWN
```

最终说成：

```text
退款成功
```

这是业务幻觉，严重程度远高于普通知识问答的小事实错误。

## 5. 用户解决率怎么量化

“用户满意”非常模糊，建议建立 proxy：

```text
Resolved without human takeover
No reopen within N hours
No immediate correction
No same-intent repeated query
No escalation/complaint
```

例如：

```text
Resolution Rate
= 完成且 N 小时内未重开 / 有效会话数
```

配合：

```text
human_takeover_rate
reopen_rate
repeat_intent_rate
user_correction_rate
abandon_rate
```

## 6. Offline Eval + Online Eval 必须分开

### Offline

```text
Golden Set
Tool Mock
Trajectory Replay
Failure Fixtures
Adversarial Cases
Multiple Trials
```

### Online

```text
Shadow
Canary
Real Business Outcome
Human Takeover
User Correction
Complaint
Cost/Latency
```

同一个 case 建议多次运行：

```text
pass_rate = passed_trials / total_trials
```

因为 Agent 是随机系统，一次成功不能说明稳定。

## 7. 真正应该建立 Error Taxonomy

例如：

```text
ROUTER_ERROR
RETRIEVAL_ERROR
PLAN_ERROR
TOOL_SELECTION_ERROR
ARGUMENT_ERROR
TOOL_PROVIDER_ERROR
STATE_MERGE_ERROR
POLICY_ERROR
FINAL_SYNTHESIS_ERROR
```

这样每周才能回答：

```text
Task Success -3%
到底是：
模型退化？
RAG 退化？
Tool 503？
还是 Adapter bug？
```

## 8. 项目对照

- nanobot：Hook/iteration/tool boundary 非常适合记录 trajectory。
- AgentDock：Task、Event Stream、token、iteration、success rate 可作为平台级 Eval 数据源。
- OpenViking：有 retrieval path / session-memory 机制，适合做 Memory/Retrieval 归因，而不是只看最终答案。
- Pi 类 Harness：适合把 operation/effect state 纳入 outcome grader，例如操作是否真正 settle，而不是只看模型文本。

---

# Q3. 模型迭代、Prompt 迭代后，如何做基线对比和灰度验证？

## 1. Agent 的“版本”不是一个 model name

一次 Agent 行为受很多版本共同影响：

```text
model_version
prompt_version
tool_schema_version
router_version
context_policy_version
memory_policy_version
retriever_version
reranker_version
knowledge_version
runtime_version
```

建议把它们组成：

```text
Release Fingerprint
```

每个 Run 必须落库。

如果只记：

```text
model = gpt-x
```

出现回归后基本没法重现。

## 2. 基线实验最重要原则：控制变量

错误方式：

```text
模型换了
Prompt 换了
Embedding 换了
Reranker 换了
Tool Schema 也改了
```

上线成功率提高 5%，你不知道为什么；下降也不知道回滚谁。

正确做法：

```text
Experiment A：固定 Tool/RAG/Context，只换 Model
Experiment B：固定 Model，只换 Prompt
Experiment C：固定 Model/Prompt，只换 Retriever
```

复杂改动可以组合发布，但必须先完成局部 ablation。

## 3. 标准发布流水线

```text
        Candidate Release
                ↓
        Offline Golden Replay
                ↓
        Hard Guardrail Gate
                ↓
      High-risk Subset Regression
                ↓
      Cost / Latency Regression
                ↓
             Shadow
                ↓
          Canary 1% / 5%
                ↓
        20% → 50% → 100%
                ↓
        Continuous Monitoring
```

## 4. Hard Guardrail 必须是 blocking gate

例如：

```text
跨租户数据泄漏
错误退款
未确认删除
把 UNKNOWN 说成 SUCCESS
```

即使平均 Task Success：

```text
82% → 87%
```

只要高风险错误：

```text
0 → 0.5%
```

也不能上线。

不要用一个平均总分把严重事故稀释掉。

## 5. 灰度为什么必须 Sticky

长会话如果：

```text
Turn 1 → Model A
Turn 2 → Model B
Turn 3 → Model A
```

你同时改变了：

```text
模型行为
summary
memory write
context trajectory
```

实验已经污染。

应该：

```text
bucket = hash(user_id or session_id, experiment_id) % 100
```

在一次会话/实验周期里保持稳定。

## 6. 回滚不能只回 Prompt

因为 Agent 回归可能来自：

```text
Prompt
Tool Schema
Context Policy
Knowledge Index
Memory Policy
Runtime
```

所以真正可回滚对象应该是整个 Release Fingerprint。

---

# Q4. Tool 接口超时、抖动、返回空数据时，重试、降级、兜底怎么设计？

## 1. 先分类，再决定动作

Tool Failure 推荐至少分成：

```text
INVALID_ARGUMENT
PERMISSION_DENIED
NO_RESULT
RATE_LIMIT
TRANSIENT_NETWORK
PROVIDER_5XX
TIMEOUT_READ_ONLY
TIMEOUT_SIDE_EFFECT
BUSINESS_RULE_ERROR
HARD_ERROR
UNKNOWN
CANCELLED
```

不能：

```text
catch Exception → retry
```

## 2. Read-only Tool 和 Side-effect Tool 完全不同

### 查询 Tool

例如：

```text
query_weather
query_device_status
search_hotel
```

如果发生临时网络错误：

```text
bounded retry
+ exponential backoff
+ jitter
```

通常是安全的。

### 副作用 Tool

例如：

```text
refund
create_order
send_email
delete_device
```

超时只说明：

> 调用方没有收到最终结果。

不代表外部没执行。

正确流程：

```text
POST refund
    ↓
Timeout
    ↓
UNKNOWN
    ↓
query_refund_status(business_request_id)
    ├─ SUCCESS
    ├─ PROCESSING
    ├─ NOT_FOUND → 才考虑安全重试
    └─ UNKNOWN   → reconcile / human
```

## 3. 空数据不是一个语义

`[]` 可能表示：

```text
真的无结果
权限过滤后为空
provider 数据延迟
参数条件过窄
provider 内部异常被吞掉
partial response
```

所以 ToolResult 不应该只返回：

```json
[]
```

更合理：

```json
{
  "status": "NO_RESULT",
  "reason": "NO_FLIGHTS_MATCH_FILTER",
  "retryable": false,
  "provider": "flight-a",
  "request_id": "req-12",
  "data": []
}
```

## 4. Retry 必须有唯一 Owner

常见错误：

```text
HTTP client retry
+
Tool adapter retry
+
Agent retry
```

会指数放大。

建议：

```text
Transport 层：只处理连接级瞬时失败，且次数非常有限
Tool Runtime：拥有统一 retry policy
Agent：看到结构化失败后决定语义策略，不重复同参数 blind retry
```

## 5. Circuit Breaker

状态：

```text
CLOSED
  ↓ failure threshold
OPEN
  ↓ cooldown
HALF_OPEN
  ├─ success → CLOSED
  └─ failure → OPEN
```

当某供应商已经连续失败时，不应该让 1000 个 Agent 各自“聪明地再试一次”。

## 6. Fallback Ladder

例如酒店 Tool：

```text
Primary Provider
    ↓ unavailable
Secondary Provider
    ↓ unavailable
Cached Snapshot
    ↓ stale but acceptable?
Structured Degrade Message
    ↓
Ask user / fail gracefully
```

关键是：

> Fallback 必须显式标注数据时效和能力差异，不能用旧缓存冒充实时数据。

## 7. nanobot 当前源码边界

当前 `nanobot/agent/tools/execution.py` 会：

```text
prepare_call
→ execute
→ error 变 Observation
→ repeated_external_lookup_error 检测
```

并且会阻止重复外部查询。

但当前这段执行代码本身是直接 `await tool.execute(...)`，并没有在这一层自动包一套企业级：

```text
per-tool timeout
circuit breaker
provider fallback
side-effect reconcile
```

这些应由 Tool Wrapper / Runtime Policy / Java Domain Service 补齐。

这正是面试里最应该说明的“当前实现 vs 企业补强”。

---

# Q5. 如何区分是模型输出问题，还是下游 Tool / 业务接口问题？怎么快速定位根因？

## 1. 必须保留完整 Causal Chain

```text
Context Snapshot
      ↓
Model Response
      ↓
Tool Proposal
      ↓
Schema / Policy
      ↓
Normalized Tool Request
      ↓
Downstream Request
      ↓
Raw Provider Response
      ↓
Normalized ToolResult
      ↓
Next Model Input
      ↓
Final Answer
      ↓
Business Outcome
```

任意一段丢失，就容易错误归因。

## 2. 一个真实故障如何归因

用户：

```text
查 A 项目的昨晚异常灯具
```

情况 A：

```text
模型调用 query_energy
但正确应该 query_alarm
```

→ `TOOL_SELECTION_ERROR`

情况 B：

```text
Tool 正确
project_id 却生成 B
```

→ `ARGUMENT_ERROR / CONTEXT_ERROR`

情况 C：

```text
参数正确
Java API 返回 500
```

→ `TOOL_PROVIDER_ERROR`

情况 D：

```text
API 返回 SUCCESS
Adapter 误映射成 UNKNOWN
```

→ `ADAPTER_MAPPING_ERROR`

情况 E：

```text
ToolResult 明确写 NO_RESULT
模型却说找到 10 个异常灯具
```

→ `RESULT_USE / FINAL_SYNTHESIS_ERROR`

## 3. 快速定位需要哪些字段

```text
trace_id
run_id
turn_id
iteration
model_version
prompt_version
context_hash
selected_tool
tool_call_id
args_hash
policy_result
provider_request_id
http_status
raw_result_hash
tool_result_status
business_state
final_answer_hash
```

最重要的一点：

> 不要只记录最终 Prompt 和最终答案。

否则中间 Tool/State 丢了，就无法重放。

## 4. Replay 是故障定位的关键

两种 Replay：

### Freeze Tool，重跑 Model

```text
固定历史 Tool Result
→ 换 Prompt / Model
```

如果问题消失，说明偏模型侧。

### Freeze Model Output，重跑 Harness

```text
固定 Tool Call
→ 重跑 Adapter / Policy / State Transition
```

如果结果变化，说明 Runtime/Tool 侧。

这是比“看日志猜原因”更成熟的方法。

---

# Q6. 大量无效 Tool 调用会拉高成本、拖慢 QPS，做过哪些限流与拦截机制？

> 对应高频面试题：**“大量无效 Tool 调用会拉高成本、拖慢 QPS，做过哪些限流与拦截机制？”**
>
> 这道题不能只回答“加限流、设置 `max_tool_calls`”。面试官真正想听的是：你能不能把 **模型决策错误、Agent Loop 重复、租户流量放大、下游接口保护、业务副作用安全** 分层治理。

---

## 1. 先说结论：无效 Tool 调用不是一个问题，而是四类问题

生产环境里我会先把“无效调用”分成四类，因为四类问题的治理手段不同：

```text
1. Should-not-call
   本来不需要 Tool，模型却调用了 Tool

2. Wrong-tool
   应该调用 A，模型却调用 B

3. Duplicate-call
   在没有状态变化的情况下，重复执行同一个动作

4. No-progress-call
   参数看起来不同，但没有获得任何新信息，Agent 一直原地打转
```

例如用户问：

```text
“羲和照明平台支持哪些分析能力？”
```

如果知识已经在当前 Context 里，模型还连续调用：

```text
search_docs(...)
search_docs(...)
search_docs(...)
```

这是 `Should-not-call + Duplicate-call`。

如果用户问：

```text
“查询项目 A 昨晚的异常告警”
```

模型调用：

```text
query_energy()
```

但真正应该调用：

```text
query_alarm()
```

这是 `Wrong-tool`。

还有一种更隐蔽：

```text
search("上海酒店")
search("上海的酒店")
search("上海住宿")
```

三个参数字符串不同，但 Goal、数据源和返回结果都没有变化，这属于 `No-progress-call`。

所以完整治理不能只靠 QPS Limit。

---

# 2. 我会把 Tool Governance 放在五层，而不是只在最后加限流

```text
User Request
    ↓
① Tool Exposure / Candidate Selection
    ↓
LLM Tool Proposal
    ↓
② Schema / Permission / Precondition
    ↓
③ Duplicate & No-progress Guard
    ↓
④ Run Budget / Rate Limit / Concurrency
    ↓
⑤ Bulkhead / Circuit Breaker / Timeout
    ↓
Tool Execution
    ↓
Canonical ToolResult
    ↓
Observation → 下一轮 LLM
```

这五层分别解决不同问题。

---

# 3. 第一层：先减少模型“能看到”的 Tool，而不是让模型从 200 个 Tool 里随便挑

大量错误 Tool Call 的根源，往往在 Tool 执行之前就已经发生了。

如果系统注册了 200 个 Tool，每轮都把完整 schema 发送给模型，会同时带来三个问题：

```text
Tool Schema Token 增长
        +
Tool Selection Confusion
        +
模型获得不必要的能力
```

所以生产系统更合理的是 Progressive Disclosure：

```text
User Intent
    ↓
Domain Router
    ↓
Candidate Tool Set
    ↓
Role / Tenant / Permission Filter
    ↓
本轮 Model-visible Tools
```

例如智慧照明问题：

```text
用户：分析 A 项目昨晚异常灯具
```

这一轮只暴露：

```text
query_project
query_device
query_alarm
query_energy
create_work_order（如果角色允许）
```

没必要把：

```text
refund
flight_search
send_mail
admin_delete_user
```

发送给模型。

这里的收益不只是性能，而是：

> **能力没有暴露给模型，比暴露后再告诉模型“不要调用”更可靠。**

在 AgentDock 这类 Control Plane 中，这一层很适合根据 tenant、agent driver、assigned MCP、Skill 和用户角色生成每个 Agent 的能力视图；Runtime 再把当前 Turn 真正需要的 Tool 子集投影给模型。

---

# 4. 第二层：模型选了 Tool，也不是立刻执行

LLM 输出 Tool Call 只能看成：

```text
Action Proposal
```

而不是：

```text
Execution Command
```

执行之前至少经过：

```text
Tool exists?
    ↓
JSON Schema valid?
    ↓
用户/Agent 有权限？
    ↓
当前业务状态允许？
    ↓
风险级别是否需要 HITL？
    ↓
是否已经执行过同样动作？
    ↓
是否还有 Budget？
    ↓
Execute
```

比如模型提出：

```text
create_work_order(project=A, device=1001)
```

Runtime / Java Service 仍然要确认：

```text
user can access project A
设备 1001 属于 project A
当前是否已经有未关闭同类工单
当前故障证据是否满足创建条件
```

这一步解决的是“错误调用真的产生副作用”的问题。

---

# 5. Action Fingerprint 到底是什么意思？

这里要先澄清：

> **Action Fingerprint 不是 MCP、LangChain、nanobot 定义的正式协议名，也不是必须背的行业标准术语。**

它只是一个很实用的 Runtime 实现技巧。更直白的名字可以叫：

```text
Action Key
Dedup Key
Tool Call Signature
```

它解决的问题是：

> **当前系统状态没有变化时，Agent 是否准备再次执行刚刚已经执行过的同一个逻辑动作？**

例如模型连续两次输出：

```json
{
  "tool": "query_alarm",
  "arguments": {
    "project_id": "P100",
    "date": "2026-09-15"
  }
}
```

如果第一次已经成功返回数据，第二次没有任何新条件，就没必要真的再访问一次数据库/API。

Runtime 可以构造一个稳定的 Action Key：

```text
ActionKey =
    tool_name
  + normalized_args
  + execution_scope
  + relevant_state_version
```

必要时再做 hash：

```text
fingerprint = SHA256(ActionKey)
```

**Hash 只是为了存储和比较方便，不是这个机制的核心。**

---

## 5.1 为什么必须先做 `normalized_args`

下面两个调用逻辑上完全一样：

```json
{"project_id":"P100","date":"2026-09-15"}
```

```json
{"date":"2026-09-15","project_id":"P100"}
```

如果直接对原始 JSON 字符串做 hash，会得到两个不同结果。

所以先 canonicalize：

```text
补齐确定性默认值
→ key 排序
→ 日期/时区标准化
→ ID 规范化
→ 删除真正不影响语义的字段
→ canonical JSON
```

例如：

```text
query_alarm|date=2026-09-15|project_id=P100
```

再生成 key/hash。

需要注意：**不能过度归一化。**

例如：

```text
refund(amount=100)
refund(amount=1000)
```

绝对不能为了“语义相似”把它们归成同一个动作。

对于高风险副作用，宁可保守，也不能错误合并两个真实业务意图。

---

## 5.2 为什么只有 `tool_name + args` 仍然不够

考虑：

```text
query_order(order_id=1001)
```

10:00 查询：

```text
status = PAYING
state_version = 20
```

10:01 支付回调已经到达：

```text
status = PAID
state_version = 21
```

Agent 此时再次调用：

```text
query_order(order_id=1001)
```

这是合法调用，因为环境发生了变化。

如果 ActionKey 只有：

```text
query_order + order_id=1001
```

第二次查询会被错误拦截。

所以对于依赖状态的 Tool，可以加入：

```text
relevant_state_version
```

最终：

```text
第一次
query_order|1001|state=v20

第二次
query_order|1001|state=v21
```

它们不是同一个 Fingerprint。

这也是 Action Fingerprint 真正有价值的地方：

> 判断的不是“这个 API 以前调用过没有”，而是“在当前状态下，这个动作是否已经做过且没有理由再做一次”。

---

## 5.3 `execution_scope` 为什么也很重要

多租户系统不能只按 Tool 参数做全局去重。

例如两个用户都调用：

```text
query_device(device_id=1001)
```

但属于不同 Tenant。

正确 Key 至少带：

```text
tenant_id
user/project scope
```

类似：

```text
ActionKey(
  tenant=T1,
  tool=query_device,
  args={device_id:1001},
  state_version=33
)
```

否则会出现跨租户缓存/去重污染。

---

# 6. Action Fingerprint、Idempotency Key、Cache Key、Rate Limit 必须区分

这是面试很容易追问的地方。

| 机制 | 解决什么 | 典型生命周期 | 谁负责 |
|---|---|---|---|
| Action Fingerprint / Dedup Key | Agent 是否正在重复做同一个动作 | 单 Run / 短窗口 | Agent Runtime / Harness |
| Idempotency Key | 副作用请求重复到达时不能产生两次业务效果 | 必须持久，跨重试/重启 | Java/业务服务 |
| Cache Key | 相同查询能否复用旧结果 | TTL/版本控制 | Tool/Cache 层 |
| Rate Limit Key | 谁在某时间窗口消耗了多少容量 | 时间窗口 | Gateway/Control Plane/Tool Runtime |

例如退款：

```text
Action Fingerprint
→ 防止 Agent Loop 在同一轮逻辑里连续提议 refund

Idempotency Key
→ 即使请求真的重复到达支付服务，也只产生一次退款
```

两者完全不是一个东西。

不能拿 Action Fingerprint 去代替业务幂等。

---

# 7. Fingerprint 只能发现“完全重复”，还需要 No-progress Detection

这是比 Action Fingerprint 更重要的一层。

模型可能这样循环：

```text
search_web("上海酒店")
search_web("上海的酒店")
search_web("上海住宿")
search_web("上海酒店推荐")
```

四个 ActionKey 都不一样，但 Agent 实际没有前进。

因此 Runtime 还需要观察“任务有没有产生新信息”。

可以维护一个 Progress State：

```text
goal_id
state_version
known_artifact_ids
evidence_count
last_error_kind
last_result_class
completed_subgoals
```

每轮结束计算：

```text
new_evidence_count
state_changed
subgoal_completed
result_class_changed
```

例如连续三轮：

```text
new_evidence_count = 0
state_changed       = false
subgoal_completed   = false
last_result         = NO_RESULT
```

即使 Tool 参数每次都不一样，也可以进入：

```text
NO_PROGRESS
```

然后 Runtime 要求换策略，而不是继续放任模型探索：

```text
NO_PROGRESS
   ↓
扩大/改变搜索条件
   ↓
切换 Tool / Provider
   ↓
询问用户补充约束
   ↓
Fallback
   ↓
Graceful Stop
```

---

# 8. 第三层：Budget，不是只有 `max_iterations`

Agent 一轮 LLM 可能一次提出多个 Tool Call，所以：

```text
max_iterations = 10
```

并不等于：

```text
最多调用 10 次 Tool
```

更完整的 Budget 应包括：

```text
max_iterations
max_tool_calls
max_calls_per_tool
max_duplicate_calls
max_external_lookups
max_argument_repairs
max_replans
max_subagent_depth
max_tokens
max_cost
wall_clock_deadline
```

还可以按 Tool 风险给不同预算：

```text
query_device       10/run
query_alarm         5/run
web_search          5/run
create_work_order   1 logical action
refund              1 logical action + HITL
```

这里的 Budget 是 **Run 级行为约束**。

---

# 9. 第四层：Rate Limit 必须考虑 Agent 的 Fan-out

传统 Web API 常按：

```text
100 requests/min/user
```

但 Agent 中：

```text
1 个用户请求
   ↓
4 次 LLM
   ↓
8 次 Tool
   ↓
12 次 HTTP/SQL
```

所以只限制入口 QPS 不够。

建议至少分：

```text
Tenant Limit
User Limit
Agent/Run Limit
Tool Limit
Provider Limit
Downstream Service Limit
```

例如用 Token Bucket：

```text
tenant:T1:web_search = 1000/min
user:U7:web_search    = 50/min
provider:maps         = 200 QPS
```

同时 Runtime 的 `max_tool_calls` 控制单任务行为。

也就是：

```text
Rate Limit
保护“系统总容量”

Budget
限制“一个 Agent Run 能花多少资源”
```

二者不能混成一个概念。

---

# 10. 第五层：Bulkhead + Circuit Breaker 防止一个 Tool 拖垮全站

假设旅游 Agent 同时有：

```text
flight_search
hotel_search
weather
maps
web_search
```

如果 `flight_search` Provider 卡住，不应该把整个 Agent 平台线程/连接全部吃光。

可以按 Tool/Provider 建独立并发池：

```text
flight provider  max 20
hotel provider   max 40
web search       max 30
DB analytical    max 15
```

这就是 Bulkhead。

再配合 Circuit Breaker：

```text
CLOSED
  ↓ failure threshold
OPEN
  ↓ cooldown
HALF_OPEN
  ↓ probe
CLOSED / OPEN
```

OPEN 时 Runtime 不继续把请求压给坏 Provider，而是：

```text
fallback provider
cache
partial result
explicit degradation
```

这样才能真正保护 QPS 和线程/连接池。

---

# 11. Retry 也必须统一 owner，否则无效调用会指数放大

非常典型的错误：

```text
HTTP Client retry 3
Tool Adapter retry 3
Agent 自己再 retry 3
```

最坏：

```text
3 × 3 × 3 = 27 次下游请求
```

所以一定要明确 Retry Ownership：

```text
HTTP Client
→ 只处理非常底层、明确安全的瞬时错误

Tool Runtime
→ 统一 retry policy / deadline / backoff

Agent
→ 负责语义换策略，不重复相同请求
```

尤其副作用 Tool timeout：

```text
refund timeout
```

不能因为“还剩 Tool Budget”就继续重试，而要进入：

```text
UNKNOWN → reconcile
```

---

# 12. nanobot 当前代码怎么对应这套设计

当前 nanobot 对“重复外部查询”的实现非常适合做这一题的源码追问，因为它体现了一个典型 Harness 原则：**不要只在 Prompt 里告诉模型“不要重复调用 Tool”，而是在 Tool 真正执行之前，用确定性的 Runtime Guard 做硬拦截。**

当前相关代码主要分布在：

```text
nanobot/agent/runner.py
nanobot/agent/tools/execution.py
nanobot/utils/runtime.py
```

核心调用发生在 `execution.py`：

```python
lookup_error = repeated_external_lookup_error(
    tool_call.name,
    tool_call.arguments,
    external_lookup_counts,
)

if lookup_error:
    event = {
        "name": tool_call.name,
        "status": "error",
        "detail": "repeated external lookup blocked",
    }
    return _with_retry_hint(lookup_error), event
```

最关键的是执行顺序：

```text
LLM 产生 Tool Call
        ↓
repeated_external_lookup_error(...)
        ↓
重复次数超限？
   ├─ Yes → 返回 Tool Error Observation
   │          ↓
   │      不执行真实 Tool
   │
   └─ No  → prepare_call
              ↓
          before_execute_tool hook
              ↓
          tool.execute(...)
```

所以第三次相同外部查询被拦截时，真实 `tool.execute()` 根本不会执行，外部 HTTP 请求、Provider QPS 和 API 配额也不会继续被消耗。

## 12.1 `external_lookup_counts` 是什么？生命周期在哪里？

`AgentRunner._run_core()` 开始一次运行时创建：

```python
external_lookup_counts: dict[str, int] = {}
```

随后每个 iteration 执行 Tool 时，都会把**同一个 dict**传下去：

```text
AgentRunner._run_core()
        │
        ├─ external_lookup_counts = {}
        │
        ├─ Iteration 0
        │     └─ execute_tool_calls(..., external_lookup_counts)
        │
        ├─ Iteration 1
        │     └─ execute_tool_calls(..., external_lookup_counts)
        │
        └─ Iteration 2
              └─ execute_tool_calls(..., external_lookup_counts)
```

因此它可以跨同一次 Agent Run 的多个 LLM iteration 统计重复查询。

但它不是：

```text
Redis 状态
数据库状态
Session 长期状态
跨进程共享状态
```

下一次新的 `_run_core()` 会重新创建空字典，所以它本质是：

> **当前 Run/Turn 内的短生命周期 Loop Guard State。**

这也说明它解决的是“当前 Agent Loop 正在原地重复搜索”，而不是跨会话、跨实例的重复治理。

## 12.2 nanobot 如何判断“这是同一个查询”？

真正生成查询标识的是 `nanobot/utils/runtime.py` 中的 `external_lookup_signature()`。

当前只专门处理两个 Tool：

```text
web_search
web_fetch
```

核心逻辑可以简化成：

```python
def external_lookup_signature(tool_name, arguments):
    if not isinstance(arguments, dict):
        return None

    if tool_name == "web_fetch":
        url = str(arguments.get("url") or "").strip()
        if url:
            return f"web_fetch:{url.lower()}"

    if tool_name == "web_search":
        query = str(
            arguments.get("query")
            or arguments.get("search_term")
            or ""
        ).strip()
        if query:
            return f"web_search:{query.lower()}"

    return None
```

例如：

```text
web_search(query="Nanobot Agent")
```

会生成：

```text
web_search:nanobot agent
```

下一轮：

```text
web_search(query="nanobot agent")
```

生成的仍是：

```text
web_search:nanobot agent
```

于是两次调用命中同一个计数项。

这里要特别注意：nanobot 当前没有做 SHA256，也没有复杂的 `ActionFingerprint` 对象。**这个 signature 字符串本身就是去重 Key。**

所以前面讲的通用设计：

```text
ActionKey = tool_name + canonical_args + scope + state_version
```

在 nanobot 当前实现里，是一个更轻量、更特化的版本：

```text
web_search → tool_name + lower(query)
web_fetch  → tool_name + lower(url)
```

## 12.3 为什么第三次开始拦截？

`runtime.py` 当前定义：

```python
_MAX_REPEAT_EXTERNAL_LOOKUPS = 2
```

计数逻辑是：

```python
count = seen_counts.get(signature, 0) + 1
seen_counts[signature] = count

if count <= _MAX_REPEAT_EXTERNAL_LOOKUPS:
    return None
```

因此真实行为是：

```text
第 1 次相同查询
count = 1
→ Allow

第 2 次相同查询
count = 2
→ Allow

第 3 次相同查询
count = 3
→ Block

第 4 次及以后
→ Block
```

它不是“一出现重复就禁止”，而是给同一查询保留一个非常小的尝试预算。外部查询可能因为瞬时网络异常、Provider 波动等原因需要有限重试，所以这里更像：

```text
Exact Lookup Attempt Budget = 2
```

而不是一个一次性的去重锁。

## 12.4 被拦截后为什么 Agent 还能继续？

超限时，`repeated_external_lookup_error()` 返回的不是 Python Exception，而是一段 Tool Error 文本：

```text
Error: repeated external lookup blocked.
Use the results you already have to answer,
or try a meaningfully different source.
```

`execution.py` 再通过 `_with_retry_hint()` 追加：

```text
[Analyze the error above and try a different approach.]
```

最终这段内容作为 **Tool Observation** 回到模型上下文：

```text
LLM
 ↓
第 3 次提出相同 web_search
 ↓
Runtime Guard 拦截
 ↓
不访问真实 Search Provider
 ↓
生成 Tool Error Observation
 ↓
进入下一轮 LLM
 ↓
模型重新决策
 ├─ 使用已有结果回答
 ├─ 换真正不同的 Query
 ├─ 换信息源
 └─ 停止继续搜索
```

这体现了一个非常重要的 Runtime 思路：

> **Runtime 可以拒绝模型提出的 Action，但不必因此把整个 Agent Run 判失败；更合理的是把拒绝结果作为 Observation 返回，让模型在硬边界内重新规划。**

## 12.5 它统计的是“尝试次数”，不是“成功次数”

计数发生在 `tool.execute()` **之前**。

所以即使：

```text
第 1 次 web_search
→ Provider 网络失败

第 2 次相同 web_search
→ Provider 网络失败

第 3 次相同 web_search
→ Runtime 直接 BLOCK
```

仍然会触发 Guard。

因此 `external_lookup_counts` 的准确含义是：

> **相同 External Lookup Signature 在当前 Run 中被尝试了多少次。**

而不是：

> 成功拿到结果多少次。

所以它更像一个“Loop Retry Budget”，而不是 Cache 计数器。

## 12.6 并发 Tool Call 时会不会计数乱掉？

nanobot 可以把 `concurrency_safe` Tool 通过 `asyncio.gather()` 并发执行，但 `_execute_tool_call()` 一进入函数，首先执行的就是同步的：

```python
repeated_external_lookup_error(...)
```

这个 Guard 之前没有 `await`。

在单个 asyncio event loop 内，同一批协程会先后完成这段同步计数逻辑，之后才进入后续 `await`，并且它们共享同一个 `external_lookup_counts`。因此同一批中出现完全相同的 external lookup，也会消耗同一个重复预算。

但这仍然只是**进程内、当前 Run 内状态**。如果未来把一个逻辑 Run 真正拆到多个进程或节点并行，就不能继续依赖普通 Python dict，需要把 dedup/budget 状态提升到共享 Runtime State、Redis、数据库或统一调度器。

## 12.7 当前实现能识别什么，不能识别什么？

它可以识别：

```text
web_search("Nanobot Agent")
web_search("nanobot agent")
```

因为做了：

```python
.strip().lower()
```

但识别不了语义相同、字符串不同的查询：

```text
web_search("上海酒店")
web_search("上海的酒店")
web_search("上海住宿")
```

也识别不了普通业务 Tool：

```text
query_device(project_id="P1")
query_device(project_id="P1")
query_device(project_id="P1")
```

因为 `external_lookup_signature()` 对 `query_device` 会返回 `None`。

所以 nanobot 当前解决的是：

```text
Exact / Near-exact repeated external lookup
```

没有解决：

```text
Generic Tool Dedup
Semantic No-progress
State-aware Dedup
Cross-run Dedup
Business Idempotency
```

## 12.8 `web_fetch` 还有一个值得追问的实现细节

当前 `web_fetch` 直接把：

```python
url.lower()
```

作为 signature 的一部分。

这是一个轻量防循环实现，但不是严格 URL Canonicalization。hostname 通常大小写不敏感，但 URL path 理论上可能区分大小写：

```text
https://example.com/API/User
https://example.com/api/user
```

当前 Guard 会把它们当成同一个 signature。

如果做更严格的企业实现，应该解析 URL：

```text
scheme   → normalize
host     → lowercase
port     → normalize default port
path     → 按 URL 语义保留
query    → canonical sort / normalize
fragment → 视场景忽略
```

这个细节也说明：nanobot 当前目标不是构建一个通用 Dedup Engine，而是用较低复杂度解决“模型连续重复 Web 查询”这个高频问题。

## 12.9 测试是怎么证明 Guard 真生效的？

当前测试 `tests/agent/test_runner_tool_execution.py` 对行为有明确断言：重复 external lookup 被阻止后，第三个 Tool Message 中包含：

```text
repeated external lookup blocked
```

同时真实 Tool：

```text
execute.await_count == 2
```

两个断言一起才完整：

```text
Tool Message 出现 blocked
```

证明模型收到了 Guard Observation；

```text
真实 execute 只有 2 次
```

证明第三次确实没有继续打到下游。

## 12.10 这段源码真正体现的设计思想

不要只记：

```text
nanobot 有 repeated_external_lookup_error()
```

更重要的是理解这条控制链：

```text
概率性 LLM 提出 Action
        ↓
确定性 Runtime Guard 校验
        ↓
不允许的 Action 不执行
        ↓
把拒绝结果转成 Observation
        ↓
模型在约束范围内重新规划
```

也就是：

> **LLM 负责提出动作，Runtime 决定动作能不能执行。**

这和 Workspace Boundary、SSRF Guard、权限、Budget、HITL 的基本思想是一致的。

## 12.11 它和 Action Fingerprint 是什么关系？

可以这样理解：

```text
通用 Action Fingerprint：
    tool_name
  + canonical_args
  + execution_scope
  + relevant_state_version

nanobot 当前：
web_search
  → "web_search:" + lower(query)

web_fetch
  → "web_fetch:" + lower(url)
```

所以 nanobot 的 `external_lookup_signature()` 可以看作 **Action Fingerprint 思想的一个极简、专用实现**，但不能反过来说 nanobot 已经实现了完整 Action Fingerprint Engine。

企业级还需要进一步补：

```text
canonical args
state-aware dedup
semantic no-progress
per-tool budget
tenant/user quota
provider circuit breaker
side-effect idempotency/reconcile
```

## 12.12 面试口述版

> nanobot 当前没有做一个很重的通用 Action Fingerprint 系统，而是针对 `web_search` 和 `web_fetch` 做了 per-run repeated external lookup guard。`AgentRunner._run_core()` 会创建一个 `external_lookup_counts` 字典，并在整个 Tool Loop 的多个 iteration 中复用。`web_search` 用 lower-case query、`web_fetch` 用 lower-case URL 生成 signature；同一个 signature 第一次和第二次允许执行，第三次开始在真正 `tool.execute()` 之前直接拦截。拦截不是让整个 Agent 抛异常，而是返回一个 `repeated external lookup blocked` 的 Tool Observation，让模型使用已有结果或者换真正不同的搜索策略。这个机制统计的是 attempt，不是 success，而且只解决 exact repeated web lookup，不解决普通业务 Tool、语义 No-progress、跨 Run 去重和业务幂等。如果做企业级扩展，我会继续加入 canonical args、scope、state version 和 progress/evidence 变化判断。

这个边界在面试里必须说准确。

---

# 13. 如果结合 AgentDock，我会怎么落地

AgentDock 当前已经有 Task/Event、iteration/token 可观测性、多租户 workspace、独立 Agent Container、CPU/Memory limit 和统一 Driver API。

因此更适合把平台级治理放在：

```text
AgentDock Control Plane
├─ tenant quota
├─ user quota
├─ task/run budget
├─ provider concurrency
├─ usage accounting
└─ global kill/cancel

Agent Runtime (nanobot/Pi/...)
├─ model-visible tool set
├─ duplicate lookup guard
├─ no-progress detection
├─ iteration/tool budget
└─ observation loop

Java Domain Service
├─ authorization
├─ business precondition
├─ idempotency
├─ transaction
└─ reconcile
```

也就是说，不要要求一个 Runtime 同时承担租户平台、模型循环和业务一致性三种职责。

---

# 14. 实际指标怎么证明这些机制有效

如果你说“我做了限流”，面试官下一句很可能问：

> 怎么证明它有效？

我会看：

```text
Tool Calls / Successful Task
Unnecessary Tool Rate
Wrong Tool Rate
Duplicate Tool Rate
Repeated External Lookup Block Rate
No-progress Termination Rate
Argument Repair Count
Provider 429 Rate
Provider P95/P99
Tool Queue Wait
Circuit Breaker Open Rate
Cost / Successful Task
Latency / Successful Task
```

还必须监控 Guard 的误伤：

```text
False-positive Block Rate
```

因为如果重复检测过于激进，会把“状态已经变化后的合法重新查询”也挡掉。

这也是为什么前面 ActionKey 建议考虑 `relevant_state_version`。

---

# 15. Java 侧可以怎么实现

可以抽象一个 `ToolExecutionGuard`：

```java
public record ToolActionKey(
    String tenantId,
    String toolName,
    String normalizedArgsHash,
    long stateVersion
) {}

public sealed interface GuardDecision {
    record Allow() implements GuardDecision {}
    record Reject(String reason) implements GuardDecision {}
}
```

Runtime 调用：

```text
LLM Tool Call
    ↓
ToolRegistry.resolve()
    ↓
Schema Validator
    ↓
Authorization
    ↓
ToolExecutionGuard.check()
    ├─ duplicate?
    ├─ budget exceeded?
    ├─ no progress?
    ├─ rate limited?
    └─ circuit open?
    ↓
execute
```

注意 Guard 不应该把所有逻辑塞进一个巨大 `if`；真正实现时通常把：

```text
DedupPolicy
BudgetPolicy
RateLimitPolicy
CircuitBreakerPolicy
RiskPolicy
```

组合成 Policy Chain。

---

# 16. 面试官继续追问：几个最容易混淆的问题

### “为什么不用 Redis SETNX 直接防重复？”

可以作为实现手段之一，但先要定义**什么才算同一个逻辑动作**。如果 Key 设计错误，SETNX 只能稳定地做错事。

### “Action Fingerprint 要永久保存吗？”

通常不需要。它主要服务当前 Run/短时间窗口的 Loop Dedup；副作用跨重启幂等必须靠持久的 `idempotency_key`。

### “参数变一点就绕过 Fingerprint 怎么办？”

Fingerprint 只解决 exact/logical duplicate。跨参数的重复探索靠 No-progress Detection、Goal/State/Evidence 变化判断。

### “缓存和 Duplicate Guard 有什么区别？”

缓存的意思是：这个调用允许发生，但可以复用旧结果；Duplicate Guard 的意思是：当前 Agent 行为已经没有必要再次执行，应该把控制权交还给规划/模型去换策略。

### “是不是所有重复查询都应该拦截？”

不是。状态变化、TTL 到期、用户显式要求刷新、强一致读取，都可能允许重复调用。Guard 必须知道状态版本或 freshness policy。

---

# 17. 1～2 分钟面试口述版

> 我不会只用一个 QPS Limit 解决无效 Tool 调用，因为无效调用至少有四类：本来不该调、选错 Tool、完全重复、以及参数略变但没有新进展。第一层我会做 Progressive Tool Disclosure，按领域、角色和权限只把本轮需要的 Tool 暴露给模型；第二层模型产生 Tool Call 后，Runtime 先做 Schema、权限和业务前置校验。对于重复调用，我会生成一个运行时 Dedup Key，也可以叫 Action Fingerprint，本质是 `tool_name + canonical args + scope + relevant state version`，它不是行业协议，只是用来判断当前状态下是否已经执行过同一动作；真正跨重启的副作用安全仍然靠业务 idempotency key。第三层做 `max_tool_calls/max_calls_per_tool/deadline/cost` 等 Run Budget，第四层按 tenant、user、provider、tool 做 Rate Limit 和并发 Semaphore，第五层用 Bulkhead、Circuit Breaker 和统一 Retry Ownership 保护下游。另外 Fingerprint 抓不到“上海酒店/上海住宿”这种语义上原地打转，所以还要看 state、evidence、subgoal 是否变化做 No-progress Detection。nanobot 当前已经有 repeated external lookup guard，但它不是完整的语义去重系统；企业版可以在 Runtime/AgentDock 层继续补齐这些策略。

---

## 最后记住一句话

> **治理无效 Tool Call 的核心不是“把 Tool 调用次数限制小”，而是让每一次 Tool 调用都必须证明：它有权限、有预算、当前状态下有必要，并且有机会给任务带来新的信息或状态变化。**

---

# Q7. Redis 在 Agent 系统中到底存什么？会话状态、缓存结果、用户记忆怎么区分？

## 1. 最重要的答案：Redis 不是“Agent 数据库”

Redis 最适合：

```text
短生命周期
高频读写
协调型
可重建
```

不应该因为它快，就把所有长期事实塞进去。

## 2. 推荐的五层数据模型

```text
Redis
  → Hot Session State / Routing / Rate Limit / Lease / Cursor

Postgres
  → Durable Task / Audit / Tenant / Business Metadata

Transcript Store
  → Durable Conversation / Tool Event

OpenViking / Memory Store
  → Long-term Memory / Resource / Skill

Business DB
  → Order / Device / Refund / WorkOrder 真相
```

## 3. Redis 具体可以放什么

### Session Hot State

```text
agent:session:{tenant}:{session_id}
```

内容：

```json
{
  "active_run_id":"r-91",
  "instance_id":"agent-3",
  "last_seq":391,
  "state_version":12,
  "expires_at":"..."
}
```

### Run Routing

```text
run:{run_id}:instance → container_id
```

用于 WebSocket/SSE 断线重连后找到当前 Runtime。

### Rate Limit

```text
quota:{tenant}:{tool}:{window}
```

### Idempotency / Short Lease

```text
idem:{tenant}:{business_request_id}
lock:{session_id}
```

注意：真正副作用幂等最好仍由业务服务识别，不能只靠 Redis key。

### Short-lived Tool Cache

缓存查询型 Tool：

```text
device_status:{project}:{device}:{version}
```

需要 TTL + source version。

## 4. 用户长期记忆不应该直接等于 Redis Value

用户偏好需要：

```text
provenance
scope
confidence
validity
updated_at
conflict policy
```

这些更像 Memory Store / Context DB 的职责。

OpenViking 当前明确把：

```text
resources
memories
skills
```

组织在 `viking://` 下，并且 Session commit 后会做 Memory extraction/merge/skip，这比“Redis 存 user_profile JSON”成熟很多。

## 5. AgentDock 实际边界

当前 AgentDock README 明确 Control Plane 以 Postgres 做持久化，而且是多租户 workspace 模型，并不是“Redis 原生 Session 平台”。

所以面试时应该说：

> 如果在 AgentDock 上加 Redis，我会用它做 hot routing、stream cursor、rate limit、lease、短缓存；Tenant/Agent/Task 的耐久状态仍然放 Postgres，不能为了快把 Source of Truth 搬进 Redis。

这类回答比“Redis 存 Session”更有工程含量。

---

# Q8. 多用户高并发同时在线，怎么做 Session 隔离、Memory 隔离，避免会话串扰？

## 1. 隔离必须至少有四个维度

```text
tenant_id
user_id
agent_id
session_id
```

不是只有 `session_id`。

一个典型资源主键：

```text
(tenant_id, user_id, agent_id, session_id)
```

## 2. 每一层都必须携带 Scope

### Session

```text
session_key = tenant/user/agent/session
```

### Memory

```text
memory.subject_id
memory.tenant_id
memory.scope
```

### RAG

检索前必须 ACL filter：

```text
WHERE tenant_id = current_tenant
AND visibility in allowed_scope
```

不能先向量召回全库，再在最终答案里“希望模型不要泄露”。

### Tool

每次调用都带 authenticated principal：

```text
user_id
tenant_id
roles
project_scope
```

Java Service 必须二次授权。

## 3. 高并发同一个 Session 怎么办

最简单的安全模型：

```text
single writer per session
```

也就是：

```text
Session Actor / Queue
```

同一个 Session 的状态变更串行；不同 Session 并行。

如果一定支持并发写，就必须：

```text
state_version
CAS
plan_version
message_seq
```

例如：

```text
worker result.plan_version = 7
current plan_version       = 8
```

结果必须标记 `STALE`，不能写回当前状态。

## 4. AgentDock 的实际案例

AgentDock 当前 README 明确：

```text
multi-tenant workspaces
owner/admin/member
每用户绑定实例
独立 agent container
persistent workspace
```

这是平台级隔离。

但即使每个 Agent 在独立容器，业务 Tool 仍必须检查：

```text
user/project permission
```

容器隔离解决的是 Runtime/Filesystem 边界，不能替代业务授权。

## 5. OpenViking 的路径模型很适合解释 Memory 隔离

当前 README 示例：

```text
viking://user/{user_id}/memories/
viking://user/{user_id}/resources/
viking://user/{user_id}/skills/
```

这说明长期 Context 应该天然带 subject scope。

企业多租户进一步加：

```text
tenant → user → scope
```

避免 A 用户 memory 召回给 B 用户。

---

# Q9. 短期滑动窗口记忆、长期用户画像记忆如何分层设计？

## 1. 先纠正概念

下面几个东西不是同一个 Memory：

```text
Recent Conversation Window
Session Summary
Runtime State
Long-term User Memory
Business State
```

尤其：

```text
Context Window ≠ Memory Store
```

Context Window 只是本轮模型能看到的输入。

## 2. 推荐四层设计

```text
L1 Recent Raw Turns
   最近 N 轮原文

L2 Session Summary
   较老对话的语义摘要

L3 Structured Session Facts
   当前 goal / constraints / IDs / state

L4 Long-term Memory
   跨 Session 的稳定偏好/事实/经验
```

最终 Context：

```text
System/Policy
+ Active State
+ Recent Raw Turns
+ Summary
+ Relevant Long-term Memory
+ RAG/Resource
+ Latest Tool Results
```

## 3. Long-term Memory 不能每轮都写

需要 Admission：

```text
Conversation
    ↓
Candidate Extraction
    ↓
Memory Type
    ├─ stable fact
    ├─ preference
    ├─ episodic experience
    └─ discard
    ↓
Importance / Stability / Confidence
    ↓
Dedup / Conflict
    ↓
Write / Merge / Skip
```

OpenViking 当前 README 也明确：Session commit 后做后台 extraction，并将 candidate 与已有 memory 比较，决定 create / merge / skip。

这就是很好的真实案例。

## 4. 用户画像要做 Scope

错误：

```text
用户喜欢夜生活酒店
```

可能只是这一次旅行。

更合理：

```text
scope = trip:tokyo-2026
preference = nightlife
```

而全局偏好可能是：

```text
scope = global
preference = quiet_room
```

Context Builder 按“更具体 scope 优先”加载。

---

# Q10. Memory 库持续膨胀、检索精度下降，迭代优化方案是什么？

## 1. Memory 膨胀的本质不是“数据太多”

真正问题是：

```text
重复
冲突
陈旧
低价值
错误写入
scope 太宽
embedding space 噪声增加
```

所以“换更大的向量库”解决不了根因。

## 2. 先做 Memory Write Quality

指标：

```text
Admission Precision
Duplicate Rate
Conflict Rate
Correction Rate
Wrong-memory Write Rate
```

如果 50% 写入本身就是垃圾，检索层再调 TopK 也没用。

## 3. Dedup / Merge / Supersede

Memory Record 建议：

```json
{
  "memory_id":"m-1",
  "subject":"u-1",
  "type":"preference",
  "scope":"global",
  "content":"prefers quiet rooms",
  "confidence":0.92,
  "source":"session-99",
  "valid_from":"...",
  "valid_to":null,
  "supersedes":null,
  "last_verified_at":"..."
}
```

更新时不是无限 append：

```text
NEW
├─ same fact          → merge/update confidence
├─ conflicts          → supersede or scope split
├─ lower confidence   → keep old / ignore
└─ unrelated          → create new
```

## 4. TTL 不能简单按时间删除

有些 Memory：

```text
用户生日
```

几年仍有效。

有些：

```text
这周出差上海
```

一周就失效。

所以需要：

```text
memory_type-specific retention
valid_from / valid_to
last_verified_at
freshness score
```

## 5. Retrieval 不要全库裸搜

先过滤：

```text
subject
scope
domain
memory_type
freshness
permission
```

再向量检索。

例如：

```text
WHERE subject_id = user
AND scope in current_scope_chain
AND valid_to > now
```

之后 Dense/BM25 才有意义。

## 6. Memory Retrieval 也要 Eval

不能只看 Recall。

至少：

```text
Precision@K
Wrong-memory Usage Rate
Stale Recall Rate
Cross-user Leakage Rate
User Correction Rate
Downstream Task Success
```

一个“召回率 95%”的 Memory 系统，如果经常多召回错误偏好，反而比不召回更差。

## 7. OpenViking 对这题的启发

OpenViking 当前把 Context 做成目录结构，并有：

```text
L0 Abstract
L1 Overview
L2 Detail
```

以及 Session Memory extraction/create/merge/skip。

这说明长期 Memory 治理的方向不是：

```text
全量向量化 → topK
```

而是：

```text
组织
→ 分层
→ 筛选
→ 再检索
→ 按需加载
```

---

# Q11. Token 溢出的多级兜底策略是什么？

## 1. Token Overflow 不应该到 API 报 400 才处理

Context Builder 在发 LLM 前就应该维护 Budget。

例如：

```text
context_window = 128k
reserve_output = 8k
safety_margin  = 5k

input_budget = 115k
```

然后按优先级分配。

## 2. 推荐 Context Priority

```text
P0 System / Security Policy
P1 Active Goal / Hard Constraints
P2 Runtime State
P3 Current Tool Observation
P4 Recent User/Assistant Turns
P5 Relevant Memory / RAG
P6 Older Summary
P7 Low-value History
```

Token 不够时从低优先级开始降级。

## 3. 多级兜底 Ladder

```text
Level 0  正常 Context
   ↓ overflow risk
Level 1  Tool Result 截断 / Artifact 化
   ↓
Level 2  RAG topK / memory candidate 减少
   ↓
Level 3  Older Turns → Segment Summary
   ↓
Level 4  Rolling/Hierarchical Summary
   ↓
Level 5  只保 Active State + Recent Window
   ↓
Level 6  Stronger compaction / larger-context model
   ↓
Level 7  要求用户开启新任务 / 明确上下文边界
```

## 4. 大 Tool Result 不应该直接塞回模型

例如 SQL 返回 20MB：

错误：

```text
全部 stringify → Tool Message
```

正确：

```text
Raw Result
   ↓
Artifact Store / File / DB
   ↓
Digest
+ schema
+ row_count
+ anomalies
+ artifact_id
   ↓
LLM
```

模型需要细节时再读取指定部分。

## 5. 不能压掉什么

绝不能因为 Token 紧张就丢：

```text
pending tool call/result pair
current business state
user confirmation
security constraint
critical IDs
```

否则 Runtime 语义被破坏。

## 6. nanobot 当前真实实现

当前 `ContextGovernor` 明确负责：

> model-request context while preserving persisted history

并且 `AgentRunSpec` 有 `max_tool_result_chars`、`context_window_tokens` 等治理参数。

这说明 nanobot 的正确设计方向本身就是：

```text
Durable History
≠
Model-facing Context
```

Token 超限应该裁剪模型视图，而不是把 durable transcript 真删掉。

## 7. OpenViking 的 L0/L1/L2 怎么配合

OpenViking 当前的三层：

```text
L0 Abstract
L1 Overview
L2 Full Detail
```

适合做 Progressive Disclosure：

```text
先拿 L0 判断相关性
→ 需要时拿 L1
→ 真正用到再拿 L2
```

它解决“外部 Context 加载多少”；nanobot ContextGovernor 解决“本轮最终发送多少”。

两者是互补关系。

---

# Q12. Agent 出现 Tool 死循环、重复调用同一接口，如何检测、截断并终止流程？

## 1. 这题不能只答 max_iterations

`max_iterations=20` 只能保证：

```text
最迟第 20 轮死
```

不能保证第 4 轮发现它已经没有进展。

真正需要：

```text
Loop Budget
+
Repeated Action Detection
+
No-progress Detection
+
Progress State Machine
```

## 2. 第一层：Exact Duplicate Detection

定义：

```text
fingerprint = hash(
  tool_name,
  normalize(args),
  relevant_state_version
)
```

连续出现：

```text
search_flight({from:A,to:B,date:D})
```

且没有新增 Context，直接 block。

当前 nanobot `execute_tool_calls()` 在真正执行前就调用 `repeated_external_lookup_error()`，发现重复外部 lookup 后返回：

```text
repeated external lookup blocked
```

而不是继续访问 provider。

这个就是实际源码级案例。

## 3. 第二层：Semantic No-progress Detection

有时模型会“假装换参数”：

```text
search(q="上海酒店")
search(q="上海的酒店")
search(q="上海住宿")
```

fingerprint 不同，但本质没进展。

可以维护：

```text
ProgressState
- evidence_ids
- known_facts
- unresolved_constraints
- state_version
- last_error_kind
```

如果 N 轮后：

```text
new_evidence_count = 0
state_version unchanged
same error category
```

进入：

```text
NO_PROGRESS
```

## 4. 第三层：Loop Budget

```text
max_iterations
max_tool_calls
max_same_tool_calls
max_external_lookups
max_argument_repairs
max_replans
max_cost
wall_clock_deadline
```

注意：

> 一轮 LLM 可以产生多个 Tool Call，所以 `max_iterations` 不能代替 `max_tool_calls`。

## 5. 第四层：Escalation Ladder

检测 no-progress 后不要立刻粗暴失败，可以：

```text
1. structured feedback
      ↓
2. 禁止重复 action
      ↓
3. 要求换 Tool / strategy
      ↓
4. stronger model / reviewer
      ↓
5. clarify user
      ↓
6. human escalation
      ↓
7. graceful stop
```

但是每一级都必须受总 Budget 约束。

## 6. Tool Error 要提供“下一步语义”

比：

```text
Error 400
```

更好的是：

```json
{
  "status":"NO_PROGRESS",
  "tool":"search_flight",
  "reason":"same logical query repeated without new evidence",
  "retryable":false,
  "allowed_next_actions":[
    "CHANGE_CONSTRAINT",
    "ASK_USER",
    "STOP"
  ]
}
```

模型才更容易收敛。

---

# 13. 把 12 道题串起来：生产级 Agent 的真正闭环

这组题最终可以收敛成一张图：

```text
User Request
    ↓
Tenant / User / Session Resolution
    ↓
Load Runtime State
    ↓
Context Budgeting
 ├─ Recent turns
 ├─ Summary
 ├─ OpenViking memory/resource
 └─ Tool schemas
    ↓
LLM Decision
    ↓
Tool Proposal
    ↓
Visibility / Schema / Policy / Rate Limit
    ↓
Duplicate / No-progress Guard
    ↓
Tool Runtime
 ├─ timeout
 ├─ retry budget
 ├─ circuit breaker
 ├─ bulkhead
 └─ fallback
    ↓
Canonical ToolResult
    ↓
State Transition / Checkpoint
    ↓
Trace + Eval Event
    ↓
Next Iteration or Final
    ↓
Business Outcome Verification
    ↓
Golden Failure Mining / Replay
    ↓
Prompt / Model / Runtime Release
    ↓
Shadow / Canary / Rollback
```

这才是这 12 道题真正应该形成的知识体系。

---

# 14. 四个项目在这组题里分别应该怎么用

## nanobot

最适合讲：

```text
AgentRunner
ContextGovernor
Tool execution
AgentHook
repeated external lookup guard
iteration budget
checkpoint/recovery
```

它回答的是：

> **一次 Tool-using Agent Run 在 Runtime 里面到底怎么跑。**

不要把平台级多租户、完整熔断、业务 Exactly-once 都说成 nanobot 当前已经原生解决。

## AgentDock

当前项目非常适合讲：

```text
multi-tenant workspace
agent/container lifecycle
Task/Event Stream
persistent workspace
Driver Registry
usage dashboard
iteration/token/elapsed observation
Docker resource isolation
egress proxy
Postgres durable control-plane state
```

它回答的是：

> **怎么把一批 Agent Runtime 运营成一个真正的平台。**

## OpenViking

当前 README 明确是 Context Database，并提供：

```text
viking://
Resource / Memory / Skill
L0 / L1 / L2
Session → Memory extraction
create / merge / skip
```

它回答的是：

> **长期 Context 怎么组织、检索、分层加载和演化。**

## Pi 类 Harness

更适合作为“Agent Harness / Coding Agent Runtime”的对照案例，用来解释：

```text
Session
Operation
Tool effect
Recovery
Context/Tool extensibility
```

但面试时不要为了显得项目多，把所有问题都硬套 Pi；只有涉及 Runtime/Harness、长任务、Tool Effect、Session 生命周期时再引用。

---

# 15. 这组题真正应该记住的 10 句话

1. **Agent 性能看的是每个成功任务的总 Loop 成本，不是单次 LLM latency。**
2. **Eval 必须同时看 Outcome、Trajectory、Safety、Efficiency。**
3. **Agent 版本是 Model + Prompt + Tool Schema + Context/RAG/Memory + Runtime 的组合。**
4. **Retry 前先分类，副作用 Timeout 应进入 UNKNOWN，而不是盲目 FAILED。**
5. **故障归因必须保留从 Model Input 到 Business Outcome 的完整因果链。**
6. **无效 Tool 需要 Tool Visibility、Budget、Fingerprint、Bulkhead、Rate Limit 多层治理。**
7. **Redis 更适合 Hot State/协调，不应该直接等同于长期 Memory 或业务事实库。**
8. **Session、Memory、RAG、Tool、Business Service 每一层都必须携带 tenant/user scope。**
9. **Memory 的首要问题是写入质量和冲突治理，不是向量库容量。**
10. **max_iterations 只是保险丝，真正防死循环要做 repeated-action + no-progress detection。**

---

# 16. 面试时如何把这组题回答出“高级工程感”

不要一上来堆名词：

```text
Redis
RAG
OTel
Circuit Breaker
Vector DB
```

更好的回答顺序永远是：

```text
先说问题的根因
    ↓
再定义状态/指标
    ↓
再讲 Runtime 约束
    ↓
再讲失败路径
    ↓
最后拿真实项目代码/架构做验证
```

例如问 Tool 死循环：

错误回答：

> 设置最大迭代次数 10。

更好的回答：

> 我会分三层处理。第一层对 `tool_name + normalized_args + state_version` 做 exact fingerprint，阻止完全重复；第二层维护 evidence/state/error 的 progress fingerprint，即使参数略变但连续几轮没有新增证据也判定 `NO_PROGRESS`；第三层才是 max_iterations/max_tool_calls/deadline/cost 这种总 Budget。nanobot 当前源码里已经有 repeated external lookup guard，这是第一层的真实实现；语义级 no-progress 和跨 Tool budget 则可以在 Harness/AgentDock 平台层继续补。

这种回答才能真正体现你理解的是 **Agent Runtime Engineering**，而不是只背 Agent 框架 API。