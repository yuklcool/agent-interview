# 2026 Agent 面试补充：Agent Loop、Tool Schema、Workflow、Context Compaction、Badcase 与版本发布

> 来源：最新截图中的 Q2～Q7。
>
> 处理原则：这 6 道题与仓库已有 `01 Agent Runtime`、`03 Tools/MCP`、`04 Reliability`、`05 Context/Memory`、`07 Harness/Eval/Trace` 大量重合，所以**不机械新增主问题编号**，而是保留这组高频面试问法，并把答案重新组织到生产级工程深度。
>
> 项目案例优先使用：**nanobot、Pi、AgentDock、OpenViking**。涉及某项目当前实现时，只描述能够从当前源码/项目结构确认的能力；企业级扩展会明确标注为“建议补强”，不把设计建议冒充成项目现状。

---

# Q2. Agent 完整执行链路是什么？每一轮 LLM 调用前后做了哪些预处理和后置校验？

## 面试官真正考什么

这道题看起来像“背 Agent Loop”，实际在考你是否理解：

> **LLM 调用只是 Agent Runtime 的一个步骤，而不是整个 Agent。**

如果回答只有：

```text
用户 → LLM → Tool → LLM → Answer
```

只能说明你理解了 Demo。

生产系统真正关心的是：

```text
每轮模型调用之前，Context 是怎么构造的？
模型返回 Tool Call 后，谁来校验？
Tool 执行前是否持久化状态？
Tool Result 如何进入下一轮？
什么时候停止？
失败后怎么恢复？
```

---

## 核心结论

一个比较完整的 Agent Turn 可以拆成 8 个阶段：

```text
① Request / Session Resolution
          ↓
② Runtime State Load
          ↓
③ Context Build & Governance
          ↓
④ LLM Request
          ↓
⑤ Model Output Validation
          ↓
⑥ Tool Runtime / External Effect
          ↓
⑦ Observation Commit
          ↓
⑧ Stop / Next Iteration / Finalize
```

其中最重要的一句话是：

> **每一轮 LLM 调用前都应该重新构造 model-facing context，而不是简单把历史数组无限 append 后原样发给模型。**

---

## 第一阶段：Request / Session Resolution

先确定这条请求属于谁、属于哪个 Session/Run/Turn：

```text
user_id
tenant_id
session_id
run_id
turn_id
request_id
trace_id
```

同时做：

- 身份认证；
- Tenant/Project Scope；
- rate limit；
- 当前 session 是否已有运行中的 Run；
- 用户这条消息是新 Turn、Cancel、Approval，还是对当前 Run 的 Injection。

这一步决定后面所有状态归属。

---

## 第二阶段：加载 Durable State 与 Runtime State

这里要区分两类状态：

```text
Durable Transcript
= 用户/Assistant/Tool 的历史事实

Runtime State
= 当前 run 的执行进度、iteration、checkpoint、pending tool 等
```

业务系统还有第三类：

```text
Business State
= 订单、退款、设备、工单的真实状态
```

它们不能混成一个 `messages[]`。

---

## 第三阶段：每轮 LLM 前的 Context Build

这是 Agent Runtime 最核心的一步。

```text
Persisted History
     │
     ├─ System / Policy
     ├─ Current User Goal
     ├─ Recent Transcript
     ├─ Summary / Compaction
     ├─ Memory / RAG
     ├─ Current Plan / Runtime State
     ├─ Tool Result / Observation
     └─ Tool Schemas
             ↓
       Context Governor
             ↓
      Token Budget / Ordering
             ↓
       Model-facing Context
```

### 这里通常会做什么

**1. System/Policy 注入**

包括角色约束、安全策略、当前租户信息、执行规则。

**2. Pending User Injection 合并**

如果用户在长任务中途说：

> “不要最早航班了，改成最便宜。”

Runtime 需要在安全边界把这条新要求注入，而不是等整个旧 Run 完成。

**3. Memory/RAG Retrieval**

只召回和当前任务相关的长期信息，不把全部长期记忆塞入 Context。

**4. Tool View Projection**

不是所有 Agent 都看到所有 Tool。根据 role/user/tenant/scope 投影当前可见 Tool Schema。

**5. Token Budget / Compaction**

如果 History + Tool Result + RAG 超过预算，必须做压缩、截断、Artifact 化或重新检索。

### nanobot 当前实现对照

当前 nanobot 源码中 `AgentRunner` 是 tool-capable loop，`ContextGovernor` 明确负责 **model-request context，同时保留 persisted history**；Runner 里会持有 `max_iterations`、`max_tool_result_chars` 等运行预算。也就是说，Context Governance 属于**每轮模型请求前的 Runtime 职责**，不是等模型报 context overflow 后才补救。

---

## 第四阶段：LLM Request

真正请求模型时还需要：

```text
provider/model
model preset
context window
sampling params
tool schemas
response format
trace attributes
budget
```

如果有 Model Router，也是在这一阶段之前完成 selection。

例如：

```text
extract field       → fast model
planner              → strong model
query database       → no LLM, direct Tool
high-risk side effect→ stronger policy, not merely stronger model
```

---

## 第五阶段：LLM 返回后的后置校验

模型可能返回：

```text
A. Final Text
B. Structured Output
C. Tool Call
D. Multiple Tool Calls
E. Invalid / Empty / Truncated Response
```

不同类型的后置处理不同。

### Tool Call 路径

```text
LLM Tool Proposal
       ↓
Tool Name Resolution
       ↓
JSON Parse
       ↓
JSON Schema / Pydantic
       ↓
Domain Validation
       ↓
Authorization
       ↓
Risk Policy / HITL
       ↓
Idempotency / Precondition
       ↓
Execution
```

模型只是提出：

```json
{
  "name": "refund_order",
  "arguments": {"order_id": "O1", "amount": 100}
}
```

不代表系统就应该退款。

---

## 第六阶段：Tool Execution 前后

高风险副作用 Tool 最关键的是：

```text
Intent Persisted
      ↓
Execute External Effect
      ↓
Settlement / Result Persisted
```

为什么？

如果进程在下面这个位置崩溃：

```text
退款请求已到支付系统
      ↓
支付成功
      ↓
HTTP Response 丢失
      ↓
Agent Process Crash
```

本地不能把它简单标成 FAILED。

正确状态可能是：

```text
UNKNOWN
   ↓
query_status(business_request_id)
   ↓
SUCCESS / NOT_FOUND / PROCESSING / UNKNOWN
```

Pi 的 durable Harness / effect intent / settlement 思路非常适合解释这种问题；nanobot 当前的 recovery 设计也强调在不确定 Tool 阶段不要盲目自动重放副作用。

---

## 第七阶段：Tool Result 变成 Observation

Tool Result 不应该只是：

```text
"success"
```

而应规范成：

```json
{
  "status": "OK",
  "code": "DEVICE_QUERY_OK",
  "data": {},
  "source": "lighting-db",
  "request_id": "req-1",
  "retryable": false,
  "freshness": "2026-09-15T08:00:00+08:00"
}
```

然后 Runtime：

```text
persist Tool Result
       ↓
append observation
       ↓
update checkpoint
       ↓
进入下一轮 Context Build
```

不是直接把外部 API 的巨大 JSON 原样塞回模型。

---

## 第八阶段：停止条件

Agent Loop 不能只靠模型“自己觉得结束了”。

硬停止条件至少包括：

```text
max_iterations
max_tool_calls
global deadline
token budget
cost budget
no-progress detection
cancelled
policy denied
fatal error
```

软停止条件可以包括：

```text
模型给出 final answer
goal satisfied
reviewer pass
workflow reaches terminal state
```

### 一句话口述版

> 我会把一次 Agent 执行拆成 Session/State、Context Build、LLM、Tool Validation、Tool Execution、Observation、Checkpoint 和 Stop 几个阶段。每轮模型调用前都重新构造 model-facing context，做 Memory/RAG、Tool View、Token Budget 和 Compaction；模型返回后先做结构、业务、权限和风险校验，Tool Result 再作为 observation 进入下一轮。像 nanobot 的 AgentRunner/ContextGovernor 就体现了这种 Runtime 思路；高风险副作用还需要像 Pi Harness 那样考虑 intent、settlement 和 crash recovery，而不是只做一个 while-loop。

---

# Q3. Function Calling 的 JSON Schema 怎么设计？参数校验失败、格式错乱怎么兜底？

## 核心结论

JSON Schema 只解决：

> **结构是否符合预期。**

企业级 Tool Contract 至少需要：

```text
Grammar / Parse
      ↓
JSON Schema / Pydantic
      ↓
Domain Validation
      ↓
Authorization
      ↓
Risk / Confirmation
      ↓
Idempotency / Preconditions
      ↓
Execution
```

所以：

```text
JSON 合法
≠
Schema 合法
≠
业务合法
≠
用户有权限
≠
可以安全执行
```

---

## Schema 设计原则

### 1. 参数尽量表达业务语义

不要：

```json
{"sql":"..."}
```

如果场景可以抽象为：

```json
{
  "project_id":"P1",
  "device_ids":["D1","D2"],
  "metric":"energy",
  "period":{"start":"...","end":"..."}
}
```

后者更容易校验，也更安全。

### 2. 能 enum 不用任意字符串

```json
"status": {
  "type":"string",
  "enum":["OPEN","CLOSED","UNKNOWN"]
}
```

### 3. 明确 required

不要依赖模型“猜默认值”。

### 4. 限制边界

```text
min/max
minItems/maxItems
pattern
format
additionalProperties=false
```

### 5. 不把权限字段交给模型决定

例如：

```text
user_id
tenant_id
allowed_project_ids
```

这些应来自 Runtime/Auth Context，不应该让模型自己填写。

---

## 格式错误怎么处理

### 第一层：Constrained / Grammar Decoding

如果模型/API支持 Structured Outputs，可在生成阶段减少：

```text
括号不闭合
字段类型错误
额外文本
枚举非法
```

但它只能提高“结构正确率”。

### 第二层：Parse + Schema Validation

失败后给模型返回**结构化错误**：

```json
{
  "status":"INVALID_ARGUMENT",
  "errors":[
    {"path":"period.end","reason":"must be after period.start"}
  ]
}
```

不要只返回：

```text
参数错了，请重试
```

### 第三层：Repair Budget

例如：

```text
argument_repair_count <= 2
same_error_fingerprint_count <= 2
```

超过后：

```text
stop / clarify / switch strategy
```

否则模型可能无限重复同一个错误。

---

## 为什么不能模糊匹配 Tool 名后偷偷执行

模型输出：

```text
refundUser
```

Registry 有：

```text
refund_user
refund_order
```

可以提示：

```text
Did you mean refund_user?
```

但不能：

```text
字符串相似度最高 → 自动执行
```

因为安全动作必须精确匹配。

---

## Tool Error 分类

建议统一：

```text
INVALID_ARGUMENT
BUSINESS_RULE_VIOLATION
FORBIDDEN
CONFLICT
NO_RESULT
RETRYABLE_ERROR
HARD_ERROR
UNKNOWN
```

对应策略：

```text
INVALID_ARGUMENT
→ 修参数

NO_RESULT
→ 改查询范围，不要同参数盲重试

RETRYABLE_ERROR
→ Runtime 有限退避重试

FORBIDDEN
→ 立即停止，不允许换说法撞权限

UNKNOWN
→ reconcile，不允许直接重放副作用
```

### 面试口述版

> 我不会把 JSON Schema 当完整 Tool 安全边界。Schema 只负责结构校验，后面还要 Domain Validation、AuthZ、Risk Policy、Idempotency 和真实业务 Service。格式错误先通过 constrained decoding 尽量减少，再用 Pydantic/JSON Schema 给模型返回结构化错误，并设置 repair budget；高风险 Tool 名必须精确匹配，不能做模糊自动执行。

---

# Q4. 项目里什么时候使用自主 Agent 推理，什么时候强制走固定 Workflow？业务取舍标准是什么？

## 不要按“简单问题 / 复杂问题”来选

更准确的判断维度是：

| 维度 | 偏 Agent | 偏 Workflow |
|---|---|---|
| 路径 | 事前无法枚举 | 可以枚举 |
| 外部反馈 | 高不确定性 | 相对稳定 |
| 副作用 | 低风险、可逆 | 高风险、不可逆 |
| 顺序约束 | 弱 | 强 |
| 审计要求 | 可接受概率路径 | 必须证明执行顺序 |
| 恢复 | 可重新推理 | 必须从明确 State 恢复 |
| SLA/成本 | 可动态探索 | 强预算约束 |

因此：

> **复杂度和风险不是同一个维度。**

“退款 10 元”推理不复杂，但风险高，应强 Workflow/State Machine；“解释 200 页技术规范”推理很复杂，但没有副作用，可以高度 Agent 化。

---

## 最常见的生产模式：Workflow 约束 Agent

```text
User Goal
   ↓
Agent：理解 / 搜索 / 推荐 / 比较
   ↓
Workflow：Quote → Lock → Confirm → Pay → Issue
                       ↑
                      HITL
```

这里：

```text
Agent owns semantic uncertainty
Workflow owns executable state transitions
```

例如：

```text
pay()
precondition = state == CONFIRMED
```

即使模型直接输出 `pay`，Dispatcher 也拒绝。

---

## 结合 AgentDock / nanobot

可以把：

```text
AgentDock
→ Task / Workflow / Driver / Container / Control Plane

nanobot
→ 某一步内部的 Tool-using Runtime
```

理解为：

```text
AgentDock Workflow
   ↓
Step A: nanobot 搜索分析
   ↓
Step B: deterministic Java validation
   ↓
Step C: HITL
   ↓
Step D: side-effect service
```

而不是让一个自由 Agent 从头到尾掌控所有高风险副作用。

---

## 面试官追问：Workflow 会不会降低 Agent 灵活性？

会，所以不是“所有地方 Workflow 化”。

正确设计是：

```text
确定性骨架
+
局部自主决策
```

例如一个照明异常处置任务：

```text
固定：权限校验 → 数据获取 → 风险分级 → 人工确认 → 工单写入

Agent：
- 选择需要查询哪些指标
- 解释异常可能原因
- 查历史相似事件
- 生成处置建议
```

这样既有灵活性，又不牺牲业务可靠性。

---

# Q5. 长对话上下文膨胀严重，Context Compression 放在 Agent Loop 哪一步？具体压缩策略是什么？

## 核心结论

Context Compression 应发生在：

> **每一轮 LLM Request 构造阶段。**

不是等 Context Window 超限才做，也不是直接删除 durable history。

正确关系：

```text
Durable Transcript
       ↓
Context Projection
       ↓
Context Governance / Compaction
       ↓
Model-facing Context
       ↓
LLM
```

压缩的是：

```text
本轮模型看到什么
```

不是：

```text
系统永久保存什么
```

---

## 为什么不能直接删 History

因为历史里可能包含：

```text
Tool Call
Tool Result
用户确认
权限决定
业务 request_id
失败原因
```

这些以后可能用于：

```text
恢复
审计
重放
Debug
Eval
```

所以最好保持 Durable Transcript，另外构造 Model-facing Context。

---

## 一个实用的 Token Budget

假设模型 Context Window 128K，不要把 128K 全部塞满。

可以预留：

```text
System + Policy          8K
Current User / Goal      4K
Recent Turns            20K
Tool Schemas             10K
RAG / Memory             25K
Tool Results             20K
Summary                  10K
Reserved Output          16K
Safety Margin            15K
```

实际比例根据模型和任务调整。

---

## 压缩策略不是一种

### 1. Sliding Recent Window

最近 N 轮保留原文：

```text
Recent raw turns = high fidelity
Older turns      = summary
```

### 2. Hierarchical Summary

不是一个 summary 无限重写，而可以：

```text
Turn Summary
   ↓
Episode Summary
   ↓
Session Summary
```

### 3. Tool Result Truncation / Artifact

巨大 Tool JSON：

```text
100,000 chars JSON
```

不要直接回注。

变成：

```text
Artifact ID
+ schema
+ important fields
+ statistics
+ provenance
```

需要细节时再次读取 Artifact。

### 4. Preserve Unfinished Tool Pair

不能出现：

```text
保留 Tool Call
删除 Tool Result
```

或者反过来。

未完成的 tool call/result pair 必须整体保留。

### 5. Semantic Memory Retrieval

旧历史里真正长期有价值的信息，可以抽成 Memory，再按当前任务检索。

OpenViking 的价值就在这里：

```text
Resource / Memory / Skill
        ↓
L0 Abstract
L1 Overview
L2 Detail
        ↓
按当前任务 progressive retrieval
```

不是把所有历史全文放进 Context。

---

## nanobot 当前实现对照

当前 nanobot 的 `ContextGovernor` 明确“own model-request context while preserving persisted history”，并考虑 `max_tool_result_chars` / `context_window_tokens`。这非常适合面试中解释：

```text
Durable Transcript
≠
Model-facing Context
```

压缩应该发生在 Runner 每次请求模型前，而不是修改模型返回结果后才处理。

---

## 压缩质量怎么评估

不能只看 Token 降了多少。

至少要看：

```text
Task Success
Critical Fact Retention
Tool Selection Accuracy
Follow-up Consistency
Groundedness
Token Cost
Latency
```

特别设计 compaction regression case：

```text
早期用户说：禁止自动创建工单
      ↓
经过 30 轮对话 + Summary
      ↓
用户问：分析异常
```

如果压缩后丢掉“禁止自动创建工单”，这是严重错误。

---

# Q6. 线上遇到哪些 Badcase？幻觉、错调工具、重复调用分别怎么修？有无量化优化数据？

## 面试官真正想听什么

不是想听：

> “我们做 Prompt 优化，效果变好了。”

而是：

```text
Badcase 怎么分类？
如何从 Trace 定位是哪一层错？
改动针对哪一层？
用什么离线/线上指标证明改善？
是否引入新的回归？
```

---

## 建议把 Badcase 分成 6 类

```text
A. Understanding Failure
B. Planning / Routing Failure
C. Tool Selection Failure
D. Argument / Execution Failure
E. Context / Memory Failure
F. Final Answer / Grounding Failure
```

不要所有问题都叫“幻觉”。

---

## Case 1：模型幻觉业务成功

### 错误现象

Tool timeout，模型回答：

> “退款成功。”

### 根因

Runtime 没有强制：

```text
Business SUCCESS
→ 才能生成 success claim
```

### 修复

```text
Timeout
  ↓
UNKNOWN
  ↓
query_status
  ↓
SUCCESS / NOT_FOUND / PROCESSING / UNKNOWN
```

并在 final verifier 做：

```text
如果答案包含“已退款/已创建/已发送”
必须存在对应 authoritative Tool Result
```

这不是单纯 Prompt 问题。

---

## Case 2：错调 Tool

例如用户问：

> “昨天设备的历史报警。”

模型调用：

```text
query_device_status
```

而正确 Tool 是：

```text
list_device_alarms
```

### 修复层次

```text
Tool description 改边界
→ 增加负例
→ Progressive Disclosure
→ Domain Router
→ Tool-use Eval
```

Description 要写：

```text
query_device_status
只查询当前实时状态。
不要用于历史报警；历史报警使用 list_device_alarms。
```

---

## Case 3：重复调用同一个 Tool

```text
Tool A(args=x)
   ↓ NO_RESULT
Tool A(args=x)
   ↓ NO_RESULT
Tool A(args=x)
   ↓ NO_RESULT
```

### 修复

Runtime 记录 fingerprint：

```text
hash(tool_name + normalized_args + result_code)
```

重复超过阈值：

```text
same_error_fingerprint_count >= 2
→ no-progress
→ force replan / clarify / stop
```

不能只靠 Prompt：“请不要重复调用工具”。

---

## Case 4：Context 压缩后遗忘约束

例如早期要求：

```text
“只分析，不要派单。”
```

经过 20 轮后 Summary 丢掉这条约束。

修复：

```text
Critical Constraints
```

从普通聊天 Summary 中独立出来，作为 Runtime State/Policy 持久化。

---

## Case 5：旧异步结果污染新目标

```text
Plan v1: 最早航班
       ↓ Worker running
User: 改最便宜
       ↓ Plan v2
v1 Worker late result
```

修复：

```text
result.plan_version != current_plan.version
→ STALE
→ 不允许更新 Current State
```

这不是 LLM 幻觉，而是并发状态问题。

---

## 怎么量化

### Tool 层

```text
Tool Selection Accuracy
Argument Validation Pass Rate
First-call Tool Accuracy
Duplicate Tool Call Rate
No-progress Loop Rate
Tool Error Recovery Rate
```

### Agent Outcome

```text
Task Success Rate
Completion Rate
Grounded Answer Rate
Unauthorized Action Rate
False-success Claim Rate
Human Escalation Rate
```

### 成本与性能

```text
LLM Calls / Task
Tool Calls / Task
Input Tokens / Task
P50/P95/P99 Latency
Cost / Successful Task
```

### Recovery

```text
Interrupted Run Recovery Success
Unknown Effect Reconciliation Rate
Duplicate Side-effect Rate
```

---

## 面试时如果没有真实数字怎么办

不要编造。

可以说：

> 我们会围绕 Tool Selection Accuracy、Argument Pass Rate、Duplicate Tool Rate、Task Success、False-success Claim 和 Token/Latency 建立基线；每次改 Prompt/Tool Schema/Model 后离线 replay 同一批 Golden Cases，再做 canary。没有可靠线上数据时我不会随口给出“提升 30%”这种无法解释来源的数字。

这是比虚构数字更专业的回答。

---

## nanobot / AgentDock 怎么帮助定位 Badcase

当前 nanobot 的 `AgentHook` 提供 iteration/tool execution lifecycle surface，例如 `before_iteration`、`before_execute_tool`、`after_execute_tool` 等，非常适合接 Trace/Eval Hook。

AgentDock 平台层则更适合保存：

```text
Task
Driver
Agent instance
Event stream
Tool event
Token usage
Elapsed time
```

这样可以形成：

```text
User Request
  ↓
Agent Turn
  ↓
Iteration
  ↓
Tool Call
  ↓
Tool Result
  ↓
Final
```

的完整 Trace，而不是只保存最终答案。

---

# Q7. 项目怎么做版本迭代？Prompt 迭代、模型切换、框架升级如何保证稳定性？

## 核心结论

Agent 的“版本”不是一个版本号。

真正影响行为的是一整个组合：

```text
Agent Release
├─ Prompt Version
├─ Model / Provider Version
├─ Tool Schema Version
├─ Tool Implementation Version
├─ Routing Policy Version
├─ Context Policy Version
├─ Memory/RAG Index Version
├─ Embedding/Reranker Version
├─ Runtime/Harness Version
└─ Safety/Authorization Policy Version
```

如果只记录：

```text
model = gpt-x
```

线上失败后很难重放。

---

## 一次请求要记录完整 Release Fingerprint

例如：

```json
{
  "agent_release":"2026.09.15-03",
  "prompt_version":"p17",
  "model":"provider/model-x",
  "tool_schema_version":"tools-12",
  "router_version":"r5",
  "context_policy":"ctx-9",
  "knowledge_index":"kb-20260914",
  "runtime_version":"nanobot-commit-xxx"
}
```

这样才能回答：

> “为什么昨天这条 Query 能成功，今天失败？”

---

## Prompt 迭代不能只看 Demo

流程：

```text
Prompt v17
   ↓
Golden Dataset Replay
   ↓
Trajectory Diff
   ↓
Hard Guardrail Check
   ↓
Shadow
   ↓
Canary 5%
   ↓
Metrics
   ↓
25% → 50% → 100%
```

特别关注：

```text
Task Success
Tool Selection
Unauthorized Action
False-success Claim
Latency
Token Cost
```

Prompt 版本必须可 rollback。

---

## 模型切换怎么做

不要直接全量改 provider/model。

### Offline

固定：

```text
Prompt
Tool Schema
Context
Tool Mock Result
```

只切换模型。

比较：

```text
task pass
Tool call trajectory
argument correctness
repair count
token
latency
cost
```

### Online

使用 sticky routing：

```text
hash(user/session) → experiment bucket
```

避免一个 Session 今天上一轮用 A、下一轮随机切 B，导致行为漂移难定位。

---

## Tool Schema 改版也要当 API Version

例如：

```text
Tool v1:
query_alarm(device_id, start, end)

Tool v2:
query_alarm(device_ids[], period, severity)
```

模型行为会变化。

所以：

```text
Tool Schema
```

本身就是 Agent Release 的一部分，不应该“后端改了一个 Pydantic 类”就直接上线。

---

## RAG / Knowledge 版本

采用：

```text
Build v2
 → offline retrieval eval
 → shadow dual-run
 → warmup
 → atomic alias switch
 → keep v1 rollback
```

长 Session 必要时 pin：

```text
knowledge_version
```

否则同一对话前后可能引用不同制度版本。

---

## Runtime / Framework 升级

框架升级的风险往往比 Prompt 更隐蔽，因为它可能改变：

```text
Tool serialization
Context ordering
Retry policy
Streaming events
Checkpoint format
Recovery semantics
Provider adapter
```

所以不能只跑“应用能启动”。

必须回归：

```text
Agent Loop
Tool Call
Parallel Tool
Context Compaction
Interrupted Recovery
Mid-turn Injection
Streaming Resume
High-risk Tool Policy
```

### nanobot 这种快速演进 Runtime

建议固定：

```text
commit / image digest
```

而不是永远追 `latest`。

AgentDock 这种 Control Plane 可以把不同 Runtime Driver/镜像版本纳入 Agent Template/Driver 配置，通过小流量实例先升级，再逐步迁移。

---

## Release Gate

真正生产发布建议至少有四层：

```text
Gate 1：Static / Unit
Schema、Tool、业务代码

Gate 2：Offline Agent Eval
Golden Dataset + Tool Mock + Replay

Gate 3：Shadow / Canary
真实流量，不影响主结果或小流量

Gate 4：Production Guardrail
实时监控 + rollback
```

其中 Hard Guardrail 优先级最高：

```text
unauthorized action = 0 tolerance
wrong side effect   = 0 tolerance
```

不能为了 Task Success +2%，接受错误退款增加。

---

# 六道题串起来，其实是一道“生产 Agent”系统设计题

```text
User Request
     ↓
Agent Runtime
     │
     ├─ Context Governance / Compaction
     ├─ Model / Prompt / Routing Version
     ├─ Tool Schema / Validation / Policy
     ├─ Agent vs Workflow Decision
     ├─ Trace / Badcase Attribution
     └─ Release / Eval / Canary
     ↓
Tool / MCP
     ↓
Java Domain Service
     ↓
Authoritative Business State
```

四个项目可以分别帮助解释不同层：

```text
nanobot
→ 真实 AgentRunner / ContextGovernor / Tool Loop / Hook

Pi
→ Durable Harness / Operation / Effect / Recovery

AgentDock
→ Runtime Driver、Agent 实例、Task/Event、Workflow、版本化部署的 Control Plane

OpenViking
→ Context / Memory / Resource / Skill 的外部组织与 Progressive Retrieval
```

如果面试官把 Q2～Q7 连续追问，本质上是在确认你是否真正做过：

> **可运行、可恢复、可评测、可灰度、可回滚的 Agent 系统，而不仅是调用过一次 LLM API。**
