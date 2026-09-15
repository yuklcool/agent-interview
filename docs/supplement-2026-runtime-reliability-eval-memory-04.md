# 2026 Agent 面试补充：性能瓶颈、Eval、Tool 容错、Memory 隔离与 Token 兜底

> 本组来自最新截图题库，共 12 道高频生产级追问。与现有 01/04/05/07/08 章节做语义去重后，作为“跨章节高阶追问专题”保留。重点不是背术语，而是把性能、可靠性、评测、会话、记忆和成本治理串成一套可落地的 Agent Runtime 设计。

## 对应主章节

| 截图问题 | 主要映射 |
|---|---|
| Agent 链路性能瓶颈怎么找 | 07 Harness / Trace + 08 Java Engineering |
| 自动化评测体系 | 07 Eval / Replay |
| 模型/Prompt 迭代怎么做基线和灰度 | 07 Eval + Release Governance |
| Tool 超时/抖动/空数据/重试/降级 | 04 Reliability |
| 怎么区分模型问题和下游接口问题 | 07 Trace / Failure Attribution |
| 无效 Tool 调用怎么限流、拦截 | 03 Tool Runtime + 04 Reliability |
| Redis 在 Agent 中存什么 | 08 Java Engineering + 05 Session |
| 多用户高并发会话/记忆隔离 | 05 Context/Memory + AgentDock Control Plane |
| 短期滑窗与长期用户画像 | 05 Context / Memory |
| Memory 膨胀后怎么治理 | 05 Memory + OpenViking |
| Token 溢出多级兜底 | 05 Context Governance |
| Tool 死循环怎么检测终止 | 04 Reliability + 07 Harness |

---

# Q1. Agent 整套链路性能瓶颈大概率出现在哪一环？检索、推理还是 Tool？怎么排查优化？

## 面试官真正考什么

不是问“哪个最慢”，而是看你是否会做 **分段性能归因**。Agent 不是一个普通 HTTP 接口，而是一条多阶段、可能循环的链路：

```text
Ingress / Session
      ↓
Context Build
      ↓
Retrieval / Memory
      ↓
LLM Round #1
      ↓
Tool Call
      ↓
Downstream API / DB / MCP
      ↓
LLM Round #2
      ↓
Final Synthesis
      ↓
Persist / Stream
```

真正的瓶颈取决于任务形态：RAG 重的系统可能卡检索；复杂规划任务可能卡模型；大量业务 Tool 的系统通常卡外部 API、DB、连接池和重试。

## 核心方法：不要猜，做分段 Trace

一条 Run 至少拆成这些 Span：

```text
run
├─ context.build
├─ retrieval
│  ├─ bm25
│  ├─ dense
│  └─ rerank
├─ llm.round.1
├─ tool.query_device
│  └─ java-service
│     └─ jdbc
├─ llm.round.2
└─ persist
```

每段至少看：

```text
P50 / P95 / P99
queue_wait
active concurrency
retry count
token input/output
tool payload size
DB acquire latency
HTTP connection wait
provider 429/5xx
```

### 一个很常见的误判

表面上：

```text
一次请求 12s
```

你看到 LLM 单次 3s，以为模型最慢。

实际 Trace：

```text
LLM #1       3.0s
Tool API     1.5s
Tool retry   1.5s
Tool retry   1.5s
LLM #2       2.8s
Context      0.8s
Queue Wait   0.9s
```

这时优化模型只省 500ms，真正问题是 Tool retry 和多轮 Loop。

## 优化顺序

先判断是哪一类瓶颈：

```text
Retrieval 慢
→ metadata filter / ANN 参数 / rerank topK / cache / index

LLM 慢
→ 减少 round 数 / context token / model routing / stream / cache

Tool 慢
→ timeout / connection pool / bulkhead / parallel-safe calls / cache / async

Loop 慢
→ 减少重复 Tool / no-progress detection / planner quality / stop condition
```

## AgentDock / nanobot 怎么讲

AgentDock 可以在 Task/Event/Driver 层记录端到端耗时、token、agent/container 状态；nanobot 的 `AgentHook` 则更适合插入 iteration、Tool 前后和 Run 结束的细粒度 instrumentation。企业里最好把两层 Trace 打通：

```text
AgentDock task span
      ↓
nanobot run span
      ↓
llm/tool spans
      ↓
Java service / DB span
```

## 1～2 分钟口述版

> 我不会先猜是检索、模型还是 Tool 慢，而会把一次 Agent Run 拆成 Context、Retrieval、每轮 LLM、每次 Tool、下游 HTTP/SQL 和最终持久化几个 Span，分别看 P95/P99、queue wait、retry、token、连接池等待。Agent 最容易出现“单段不慢但循环很多”的问题，所以还要看 LLM round 数和重复 Tool 次数。像 AgentDock 负责平台级 Task/Container 观测，nanobot 可以通过 AgentHook 抓 iteration 和 Tool 边界，再把 traceparent 传给 Java 服务和 DB，就能快速判断瓶颈到底在哪一层。

---

# Q2. 如何搭建 Agent 自动化评测体系？怎么量化任务成功率、幻觉率、用户解决率？

## 不要只做“问答准确率”

Agent 需要评估两层：

```text
Outcome：最终任务有没有完成
Trajectory：完成过程是否正确、安全、高效
```

只看最终答案会漏掉很多问题。例如 Agent 最终给出了正确答案，但中间乱调了 10 次 Tool，线上成本和风险已经不可接受。

## Golden Case 结构

一个案例不应该只是：

```text
input → expected text
```

而应该包含：

```yaml
case_id: workorder_001
input: "分析异常能耗，如果确有故障再创建工单"
env_state: fixture-v3
allowed_tools:
  - query_energy
  - query_alarm
  - create_work_order
expected_outcome:
  work_order_created_if_fault_confirmed: true
trajectory_constraints:
  - must_query_evidence_before_create
  - must_not_create_if_no_fault
  - create_work_order_at_most_once
graders:
  - business_outcome
  - tool_selection
  - argument_accuracy
  - policy
  - groundedness
```

## 指标体系

任务成功率必须来自业务事实，不是模型自评。

```text
Task Success Rate
= 成功达成业务目标的 case / 总 case
```

例如创建工单，最终要查 `work_order_id` 是否真实存在。

幻觉率至少拆：

```text
Unsupported Claim Rate
Wrong Business State Claim Rate
Citation/Evidence Mismatch Rate
```

“用户解决率”更适合线上定义：

```text
Resolved without human takeover
Resolved without repeat contact in N hours
User did not immediately correct/reopen
```

还要配合：

```text
Human takeover rate
User correction rate
Repeat query rate
Abandon rate
```

## Offline + Online 两套体系

```text
Offline
Golden Set
Replay
Tool Mock
Deterministic Fixtures

Online
Shadow
Canary
Real user outcome
Human takeover
Complaint/correction
Business KPI
```

## Pi / nanobot / AgentDock 怎么结合

nanobot 的 Hook 可以采集 trajectory；AgentDock 的 task/event/usage 可以补平台层状态；Pi 更适合解释 durable operation/effect 是否按预期收敛；OpenViking 的 retrieval trajectory 可用来区分“Memory 找错”还是“模型用错”。

## 面试关键句

> Agent Eval 不能只评最终文本，要同时评 outcome、trajectory、safety 和 efficiency。

---

# Q3. 模型或 Prompt 迭代后，如何做基线对比和灰度验证？

## 第一原则：一次尽量只改一类变量

如果同时换：

```text
Model
Prompt
Tool Schema
Retriever
Reranker
Context Policy
```

线上成功率涨了也不知道谁贡献，跌了也无法回滚单点。

## 建立 Release Fingerprint

每个 Run 记录：

```text
model_version
prompt_version
tool_schema_version
router_version
context_policy_version
retriever_version
reranker_version
runtime_version
knowledge_version
```

这就是“Agent 版本”，不能只记一个 Git commit。

## 发布链

```text
Baseline Golden Set
      ↓
Offline Replay
      ↓
Hard Guardrail Gate
      ↓
Quality / Cost / Latency Compare
      ↓
Shadow Traffic
      ↓
1% Canary
      ↓
5% / 20% / 50%
      ↓
Full Rollout
```

### 灰度必须 sticky

长会话按 `user_id` 或 `session_id` 固定分桶，不能这一轮 Model A、下一轮 Model B，否则 Session/Memory/Context 都被实验污染。

## 怎么判“新版本更好”

不能只看平均分。

优先级通常是：

```text
Hard Guardrail 不退化
      ↓
Task Success 不退化
      ↓
High-risk subset 不退化
      ↓
Latency / Cost 可接受
      ↓
长尾 badcase 是否改善
```

严重副作用错误必须是 blocking gate，不能被平均分掩盖。

---

# Q4. Tool 接口超时、抖动、返回空数据时，重试、降级、兜底怎么设计？

## 先分类，后重试

不能写成：

```text
catch Exception → retry 3 次
```

应该先看 Tool Result 类型：

```text
INVALID_ARGUMENT
NO_RESULT
RATE_LIMIT
TRANSIENT_NETWORK
PROVIDER_5XX
TIMEOUT_READ_ONLY
TIMEOUT_SIDE_EFFECT
FORBIDDEN
HARD_ERROR
UNKNOWN
```

## Read-only 与 Side-effect 必须分开

查询天气超时，可以有限重试；退款/下单超时不能直接重试，因为外部可能已经成功。

```text
read-only timeout
→ exponential backoff + jitter
→ bounded retry

side-effect timeout
→ UNKNOWN
→ query_status / reconcile
→ 确认 NOT_FOUND 后才允许重试
```

## 空数据也要分类

```text
[]
```

可能代表：

```text
真的没有数据
provider 返回部分空结果
权限过滤后为空
参数范围不合理
上游异常吞掉了错误
```

所以 Canonical ToolResult 应带：

```json
{
  "status": "NO_RESULT",
  "reason": "NO_FLIGHTS_FOR_DATE",
  "retryable": false,
  "data": [],
  "source": "provider-a",
  "request_id": "r-1"
}
```

而不是只返回空数组。

## Retry Budget

至少包含：

```text
per-attempt timeout
max_attempts
backoff
jitter
global deadline
provider circuit breaker
bulkhead
```

避免 HTTP Client 重 3 次、Tool Runtime 重 3 次、Agent 又重 3 次，最坏放大 27 倍。

## nanobot 当前实现可以怎么讲

当前 Tool execution 会把 Tool Error 变成 Observation，同时已有 repeated external lookup guard；它能阻止模型对同一个外部 lookup 无意义重复调用。但业务级 fallback、provider circuit breaker、side-effect reconcile 仍应由 Tool Adapter / Java 业务服务补齐。

---

# Q5. 怎么区分是模型输出问题，还是下游 Tool/业务接口问题？如何快速定位根因？

## 核心：保留完整因果链

一次失败至少拆成：

```text
Model Input
  ↓
Model Output / Tool Proposal
  ↓
Schema / Policy
  ↓
Tool Request
  ↓
Downstream Response
  ↓
ToolResult Normalization
  ↓
Next Model Turn
  ↓
Final Outcome
```

## 归因规则

如果：

```text
模型选错 Tool
→ Model / Router / Prompt 问题
```

如果 Tool 正确但参数错：

```text
Argument Generation / Context 问题
```

如果请求参数正确，下游 500：

```text
Provider / Service 问题
```

如果下游返回 SUCCESS，但 Adapter 映射成 UNKNOWN：

```text
Tool Adapter 问题
```

如果 ToolResult 正确，模型最终却说错：

```text
Result Use / Final Synthesis 问题
```

## 建议统一 error taxonomy

```text
MODEL_SELECTION_ERROR
ARGUMENT_ERROR
POLICY_DENIED
TOOL_TIMEOUT
TOOL_5XX
TOOL_BAD_DATA
ADAPTER_MAPPING_ERROR
STATE_MERGE_ERROR
FINAL_SYNTHESIS_ERROR
```

有 taxonomy 后，Badcase 才能按根因统计，而不是所有失败都叫“幻觉”。

## Trace 字段

```text
run_id
turn_id
iteration
tool_call_id
model/provider
prompt_version
tool_name
args_hash
http_status
error_kind
result_status
business_request_id
```

这也是为什么 Agent 系统一定要做 trajectory observability。

---

# Q6. 大量无效 Tool 调用会拉高成本、拖慢 QPS，怎么做限流和拦截？

## 无效调用通常分三类

```text
不该调用 Tool 却调用了
选错 Tool
同一个 Tool + 同参数重复调用
```

## 第一层：模型可见 Tool 减少

不要把 100 个 Tool 全塞给模型。先按 domain/role/task 做 capability projection：

```text
Full Registry
   ↓
Role/Intent Filter
   ↓
本轮只暴露 5～15 个候选 Tool
```

## 第二层：Runtime 拦截

维护：

```text
tool_call_count
same_tool_args_count
provider_call_count
repair_count
cost_budget
wall_clock_deadline
```

例如：

```text
same tool + normalized args + same state
连续出现 N 次
→ block
→ NO_PROGRESS
```

nanobot 当前 `execute_tool_calls()` 已经会检查 repeated external lookup，并返回错误 Observation，这就是很好的真实实现案例。

## 第三层：资源级限流

```text
per-user
per-tenant
per-tool
per-provider
per-agent
```

Tool QPS 不能只按 HTTP 入口限，因为一个用户请求可能产生 20 个下游调用。

## 第四层：Bulkhead / Circuit Breaker

不同 Tool 分资源池：

```text
LLM slots
DB slots
external API slots
MCP slots
```

某一个外部供应商雪崩时，不拖死所有 Agent 请求。

---

# Q7. Redis 在 Agent 系统中到底存什么？会话状态、缓存结果、用户记忆怎么区分？

## 核心原则

Redis 更适合：

> 高频、短生命周期、并发协调、允许重建的热状态。

而不是所有 Agent 数据的最终事实库。

## 适合 Redis

```text
session hot state
run_id → instance_id routing
stream cursor
rate limit counter
idempotency hot key
lease / lock
short-lived tool cache
worker heartbeat
pending approval
```

## 不建议只放 Redis

```text
durable transcript
business order/refund state
audit trail
long-term user memory 原始事实
important checkpoint 唯一副本
```

## 三类数据要彻底区分

### Session State

当前对话/Run 的热状态，例如：

```text
current_run
last_seq
active_turn
pending_approval
```

生命周期：分钟～小时。

### Cache

Tool 查询结果，例如天气、设备状态、知识查询结果。

生命周期：秒～分钟，必须带 tenant/scope/version。

### Long-term Memory

用户长期偏好、稳定事实、历史经验。

生命周期：跨 Session，需要 provenance、版本、冲突和删除能力，应该有独立 Memory/Context Store，例如 OpenViking 或持久数据库。

## 面试关键句

> Redis 是 Hot Coordination Layer，不是 Memory System 的同义词。

---

# Q8. 多用户高并发同时在线，如何做 Session 隔离和 Memory 隔离，避免串话？

## 隔离维度至少四层

```text
Tenant
  ↓
User
  ↓
Agent Instance
  ↓
Session / Conversation / Run
```

每条数据都应有明确 scope。

## Key / Record 设计

```text
session:{tenant}:{user}:{session_id}
run:{tenant}:{session_id}:{run_id}
```

Memory 记录则至少包含：

```text
tenant_id
subject_user_id
scope
source_session_id
memory_type
acl
```

不能只靠向量相似度召回 Memory，必须先做 tenant/user/scope filter。

## 最危险的串话来源

不是只有 Redis key 写错，还包括：

```text
共享全局 in-memory dict
vector DB 没有 tenant filter
cache key 缺少 user/project
异步 Worker 结果没有 session/run id
WebSocket 重连后旧 run result 写进新 run
```

## AgentDock 作为真实平台案例

AgentDock 的 Workspace/Tenant/Agent/Container 边界很适合解释平台级隔离：不同 Agent 实例可以放独立容器和 workspace；但 Runtime 内的 Session、Memory scope 仍需要继续细分，不能认为“容器隔离了就不会串会话”。

## 一致性

同一 Session 多端并发时建议：

```text
session_version
+ CAS / optimistic lock
+ per-session actor/queue
+ run_id / seq
```

不要只靠一把 Redis Lock。

---

# Q9. 短期滑动窗口记忆、长期用户画像记忆如何分层？

## 先分五层

```text
Durable Transcript
Runtime State
Short-term Working Context
Long-term Memory
Business State
```

短期“记忆”本质上更接近 Working Context，不等于长期 Memory。

## 推荐分层

```text
L0 Current Turn
  当前用户输入、当前 Tool Result

L1 Recent Window
  最近 N 轮原始消息

L2 Session Summary
  当前任务/主题的压缩摘要

L3 Long-term Memory
  跨 Session 的稳定偏好/事实/经验

L4 External Resource
  文档、知识、Skill、项目资料
```

## 写入策略

用户说：

> “今天中午想吃辣一点。”

不应该自动升级成：

```text
用户永远喜欢辣
```

长期 Memory 要走 admission：

```text
Candidate
→ type classify
→ importance/stability/confidence
→ dedup/conflict
→ write/update/ignore
```

## OpenViking 怎么对照

OpenViking 适合把长期 resource/memory/skill 按分层 Context 管理；nanobot `ContextGovernor` 则解决本轮哪些信息真正进入 model-facing context。两者不是同一个层。

---

# Q10. Memory 库持续膨胀，检索精度下降，怎么迭代优化？

## 根因不是只有“向量太多”

Memory 膨胀通常有四种问题：

```text
重复 Memory
过期 Memory
冲突 Memory
低价值 Memory
```

向量数量只是表现。

## 写入侧先治理

比检索侧加更强 Embedding 更重要的是 Admission Precision。

```text
每轮都写
→ 高噪声
→ duplicate/conflict 增长
→ retrieval precision 下降
```

所以先做：

```text
Dedup
Conflict Detection
Scope
TTL / Expiration
Version
Confidence
Importance
Provenance
```

## 检索侧

不要只做全库 TopK embedding：

```text
subject filter
memory_type filter
scope filter
freshness filter
semantic retrieval
rerank
```

用户当前明确指令要优先于旧 Memory。

## Consolidation

定期把相似 episodic memory 合并成更稳定的抽象：

```text
10 条酒店记录
→ “用户通常偏好安静、交通方便的酒店”
```

但原始 evidence/ref 最好保留，不能让抽象成为不可追溯真相。

## 评测

重点看：

```text
Memory precision
stale recall rate
cross-user leakage
wrong-memory usage rate
user correction rate
downstream task success
```

---

# Q11. Token 溢出的多级兜底策略怎么设计？

## Token overflow 不应该等模型 API 报错才处理

每一轮模型调用前，都应有 token budget estimator。

```text
System
+ Policy
+ Tool Schema
+ Active State
+ Recent Turns
+ Summary
+ Memory/RAG
+ Tool Results
= estimated tokens
```

接近阈值时进入分级治理。

## 推荐多级兜底

```text
Level 0
正常 Context Projection

Level 1
截断/摘要超大 Tool Result
→ Artifact + digest

Level 2
减少低优先级 RAG/Memory
→ topK / L0-L1 优先

Level 3
压缩旧对话
→ Summary + Recent Raw Turns

Level 4
减少 Tool Schema
→ Progressive Disclosure

Level 5
切更大 context model（如果策略允许）

Level 6
明确向用户澄清/分任务
```

## 绝不能被压掉的东西

```text
Hard Policy
Current Goal
Current Runtime State
User confirmed irreversible action
Unclosed Tool Call / Tool Result pair
Critical IDs / amounts / deadlines
```

## nanobot 当前怎么对照

`ContextGovernor` 的职责就是治理 model request context，同时不破坏 persisted history；因此可以把“Durable Transcript”和“Model-facing Context”分开。企业层可以再在其前面加入 Memory/RAG 优先级和 Tool Schema progressive disclosure。

---

# Q12. Agent 出现 Tool 死循环、重复调用同一接口，怎么检测、截断并终止流程？

## 只设 max_iterations 不够

如果模型每轮都：

```text
weather(city=Taipei)
→ NO_RESULT
→ weather(city=Taipei)
→ NO_RESULT
→ ...
```

等到 max_iterations 才停，成本已经浪费。

## No-progress Fingerprint

对每次动作生成：

```text
fingerprint = hash(
  tool_name,
  normalized_args,
  relevant_state_version,
  result_code
)
```

连续出现相同 fingerprint：

```text
N >= threshold
→ REPEATED_ACTION
→ block same call
→ ask model to change strategy
```

如果后续仍无新 evidence：

```text
NO_PROGRESS
→ stop / clarify / fallback / human
```

## 不只检查“完全相同参数”

模型可能做这种伪变化：

```text
query(city="Taipei")
query(city="Taipei City")
query(city="台北")
```

所以还可以记录：

```text
semantic action class
provider endpoint
normalized entity set
same error code
new evidence count
```

## Budget

最终还要有硬预算：

```text
max_iterations
max_tool_calls
max_same_tool_calls
max_argument_repairs
max_replans
max_subagent_depth
token budget
cost budget
global deadline
```

## nanobot 当前真实案例

当前 `nanobot/agent/tools/execution.py` 在 Tool 执行前会调用 `repeated_external_lookup_error(...)`，检测重复外部 lookup；如果命中，会返回 `repeated external lookup blocked` 的错误 Observation，而不是继续真正执行 Tool。它还会把 Tool 执行事件记录为 `name/status/detail`。这非常适合面试时解释：

> 死循环不能只靠 Prompt 说“不要重复”，Runtime 必须保存动作历史并在执行边界硬拦截。

## 收敛策略

```text
same action blocked
      ↓
change tool / change params
      ↓
仍无新 evidence
      ↓
clarify user
      ↓
fallback / graceful failure
```

---

# 一张图串起这 12 道题

```text
                    AgentDock
           Task / Tenant / Container / Stream
                        │
                        ▼
                    Agent Runtime
                        │
     ┌──────────────────┼──────────────────┐
     ▼                  ▼                  ▼
 Context / Memory      LLM Round          Tool Runtime
     │                  │                  │
OpenViking          model/prompt      timeout/retry
ContextGovernor      routing           circuit breaker
     │                  │             no-progress guard
     └──────────────────┼──────────────────┘
                        ▼
                    Java Service
                        │
                 DB / External API

全链路外面再包：
Trace + Eval + Budget + Canary + Recovery
```

# 面试回答总纲

如果这 12 道题连续追问，可以始终回到一条工程主线：

> Agent 的核心难点不是“模型会不会回答”，而是怎么把一个概率性的多轮决策系统变成可观测、可归因、可限流、可恢复、可评测、可灰度的生产系统。性能问题靠分段 Trace 定位；Tool 失败先分类再决定 retry；死循环用 Runtime fingerprint 和 budget 硬拦截；Session/Memory 按 tenant/user/session scope 隔离；Token 和 Memory 都通过分层 Context 治理；所有模型/Prompt 改动最终都要经过 Golden Replay、Shadow 和 Canary，而不是凭主观感觉上线。
