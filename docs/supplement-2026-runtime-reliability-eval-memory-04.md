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

## 1. 先定义什么叫“无效 Tool”

至少四类：

```text
Should-not-call
  本来不需要 Tool，却调用了

Wrong-tool
  应该调用 A，却调用 B

Duplicate-call
  相同 Tool + 相同参数重复

No-progress-call
  参数略变，但没有获取任何新信息
```

最后一种比“完全相同参数”更难发现。

## 2. 第一层：减少模型可见 Tool

如果系统有 200 个 Tool，不应该每轮把 200 个 schema 全塞给模型。

可以：

```text
Intent / Domain Router
      ↓
Candidate Tool Set
      ↓
Role/Permission Filter
      ↓
Model-visible Tool View
```

例如照明项目问设备：

```text
query_device
query_alarm
query_energy
```

不要暴露：

```text
refund
flight_search
send_marketing_email
```

这同时降低：

```text
Token
Tool confusion
Security surface
```

## 3. 第二层：Action Fingerprint

```text
fingerprint = hash(
  tool_name,
  normalized_args,
  relevant_state_version
)
```

同一 Run 里：

```text
same fingerprint
+
same observation
+
no new evidence
```

重复出现时直接拦截。

当前 nanobot 已经有 `repeated_external_lookup_error(...)`，这就是很实际的 Runtime Guard，而不是靠 Prompt 说“不要重复查询”。

## 4. 第三层：多维 Budget

```text
max_iterations
max_tool_calls
max_calls_per_tool
max_duplicate_calls
max_argument_repairs
max_external_lookups
max_cost
wall_clock_deadline
```

例如：

```text
search_web max 5/run
query_order max 3/run
refund max 1 logical action
```

## 5. 第四层：QPS / Concurrency Control

建议按：

```text
tenant
user
agent
provider
tool
```

分别做 token bucket / semaphore。

为什么不能只按 HTTP Request 限流？

因为：

```text
1 个用户请求
→ 5 次 LLM
→ 12 次 Tool
→ 8 次 DB
```

真实资源消耗是 fan-out 的。

## 6. Bulkhead

不要让慢 Tool 把整个系统拖死。

例如：

```text
flight provider pool  = 20 concurrent
hotel provider pool   = 50 concurrent
web search pool       = 30 concurrent
DB query pool         = 40 concurrent
```

某一个 provider 卡死，不应该耗尽所有 worker。

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