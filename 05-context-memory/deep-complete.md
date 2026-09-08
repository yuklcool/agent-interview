# 05. Context、Memory、Session 与状态——全量深度版

> 覆盖 `05-01`～`05-11`。这一章必须彻底区分：**Durable Transcript、Model-facing Context、Runtime State、Long-term Memory、Business State**。很多 Agent 系统的问题都来自把这五个东西混在一起。

---

## 05-01. Agent Loop 一次模型调用前会做什么？上下文压缩在哪一步

### 核心结论

每一轮 LLM 调用前都要重新做 Context Engineering。压缩发生在**持久事实已经存在**和**本轮模型请求真正发出**之间；压的是模型视图，不是把 durable history 删除。

### 一轮真实链路

```text
Durable Transcript / Session
        ↓
Runtime State
        ↓
System / Policy
        ↓
Summary + Recent Raw Turns
        ↓
Long-term Memory / RAG / Resources
        ↓
Tool Schemas / Current Observation
        ↓
Token Estimation
        ↓
Compaction / Projection
        ↓
Model-facing Context
        ↓
LLM
```

为什么每轮都要重建？因为上一轮可能新增 Tool Result、用户 injection、summary、provider state、memory recall，Context 不是 Session 开始时拼一次就固定。

### nanobot 对照

`AgentRunner` 在每轮调用前构造 request messages，`ContextGovernor`/compaction 负责 token 治理；`AgentRunSpec` 可传 transcript input/builder、consolidator、tool limits 等。durable session 和真正发给模型的 request_messages 是两套视图。

### 不能怎么压

Assistant 已产生 Tool Call 但 Tool Result 尚未闭合时，不能把 Tool Call 删掉只保 Result，否则出现 orphan observation。压缩应以完整 Turn/稳定边界为单位。

---

## 05-02. Agent 间传递上下文是传全量还是传结论？上下文爆炸怎么压

### 核心结论

传的是**结构化任务状态 + Artifact 引用 + 必要 Evidence**，不是整个 Transcript，也不是一句模糊 Summary。

### Handoff payload

```json
{
  "task_id":"t-1",
  "plan_version":5,
  "step_id":"s-3",
  "goal":"分析三盏灯的异常能耗",
  "constraints":{"project_id":"p9"},
  "artifacts":["artifact://energy-result-82"],
  "evidence":["tool://tc-32"],
  "deadline":"..."
}
```

大 SQL 结果、文件、网页内容放 Artifact Store/OpenViking/resource layer；Subagent 只拿自己完成当前 step 所需的数据。

### 为什么“只传总结”也不行

总结可能遗漏 ID、时间、单位、异常值和证据来源。应把可验证事实字段化，摘要只作为阅读辅助。

### Pi / nanobot

Pi 的 Branch/AgentLane 模型适合解释“多个执行路径共享 conversation tree，但每条 lane 有独立 operation state”；nanobot `SubagentManager` 当前更接近给子任务独立小上下文和 Tool Registry。企业平台再补 shared Task State/Artifact Store。

---

## 05-03. Agent 里的“状态”和“上下文”有什么区别？

### 最关键的一句话

**State 决定系统现在“是什么”；Context 决定模型现在“看到了什么”。**

### State

```text
plan_version
current_step
completed_steps
tool_status
retry_count
user_confirmation
order_status
artifacts
```

State 必须结构化、可持久化、可 CAS、可恢复。

### Context

是从 State、History、Memory、RAG、Policy、Tool Schema 中按本轮需要投影出来的模型输入。

### 典型错误

把 `current_step = PAY` 只写进一段自然语言历史；一旦历史被压缩或模型没关注，就“失忆”。正确做法是 State 独立保存，Context 每轮把必要 State 投影进去；Workflow/Runtime 自己仍然知道真实状态。

### Business State 更不能等于 Agent State

订单 `PAID`、设备 `OFFLINE`、退款 `SUCCESS` 属于业务系统权威状态。Agent Runtime 可以缓存/引用，但不能自己成为事实源。

---

## 05-04. 长上下文里怎么保证关键约束不被“淹没”？

### 不要只相信“放最前面”

关键约束应多层承载：

```text
Hard Security Rule   → Runtime / Policy
Task Hard Constraint → Structured State
Current Reminder     → Model Context near active turn
Evidence             → Artifact / Retrieved Source
```

例如：

```json
{
  "max_budget":5000,
  "deadline":"2026-09-10T18:00:00+08:00",
  "forbidden_actions":["delete_device"],
  "confirmed_amount":100
}
```

这比把“预算不要超过 5000”藏在 100k token 前面的用户聊天中可靠。

### Context prioritization

可以按：

1. System/Policy；
2. Active Goal + hard constraints；
3. Current State；
4. Latest observation；
5. relevant memory/RAG；
6. recent raw turns；
7. older summary。

### OpenViking

OpenViking L0/L1/L2 允许先加载 abstract/overview，再按需读 details，可以避免大量资源正文一次性进入 Context；但真正硬约束仍不能只依赖检索系统。

---

## 05-05. 摘要压缩会丢关键细节，怎么解决？

### 摘要不是事实数据库

Summary 适合压缩语义脉络，不适合独占：

- 订单 ID；
- 用户确认金额；
- Tool Result 原始证据；
- 错误代码；
- 权限状态；
- 关键时间戳。

### Hybrid Compaction

```text
Structured facts / state → 不摘要
Recent raw turns         → 保留
Old semantic dialogue    → Summary
Large Tool Results       → Artifact + short digest
Important evidence       → pointer/provenance
```

### Summary checkpoint

摘要应带：

```text
summary_version
covers_until_message_id / archive watermark
source range
created_at
model/prompt version
```

这样可以判断 Summary 覆盖了哪些历史，避免重复或缺口。

### 错摘要怎么办

Durable Transcript 仍存在，必要时可以重新生成 Summary；如果摘要是唯一历史副本，就失去了可修复性。

---

## 05-06. Rolling Summary、分段 Summary 和混合方案怎么选？

### Rolling Summary

每次把旧 summary + 新段继续总结。

优点：简单、Context 固定。

缺点：误差会累积，早期细节逐轮衰减。

### Segment Summary

把历史分段，各段独立 summary。

优点：可追溯、局部更新；缺点：多个 summary 仍可能变长。

### Hybrid

更适合生产：

```text
Recent Raw Turns
+
Recent Segment Summaries
+
Global Task/Session Summary
+
Structured Facts / State
```

按 token budget 动态决定加载多少层。

### Pi / OpenViking 的启发

Pi conversation tree/compaction 强调“保留 durable entry tree，provider context 是另一个视图”；OpenViking则把长期 resource/memory 以分层 Context 按需加载。两者共同说明：**存储结构和模型输入结构不应该是一回事。**

---

## 05-07. 长期记忆是每轮都写吗？如何做 admission、去重和更新？

### 不能每轮都写

如果每句话都进 Memory：

- 临时意图变成永久偏好；
- 错误信息被强化；
- 向量库噪声爆炸；
- 隐私面扩大；
- 后续召回冲突增多。

### Memory Admission Pipeline

```text
Conversation / Event
       ↓
Memory Candidate Extraction
       ↓
Type Classification
       ├─ preference
       ├─ stable fact
       ├─ episodic experience
       └─ discard
       ↓
Importance / Stability / Confidence
       ↓
Dedup / Conflict Check
       ↓
Write / Update / Ignore
```

### Memory record

建议包含：

```text
memory_id
subject
memory_type
content
source_session/evidence
confidence
created_at
last_verified_at
valid_from/valid_to
version
```

### OpenViking

OpenViking当前明确支持 Session commit 后异步抽取 user preference 和 agent experience 进入长期 memory，这比“每一轮同步写向量库”更符合生产 admission 思路。

---

## 05-08. 什么时候才去检索长期记忆？每轮都检索有什么问题？

### Retrieval Gate

先判断当前任务是否需要用户历史/经验：

```text
当前请求
  ↓
Is memory relevant?
 ├─ No  → skip
 └─ Yes → retrieve by subject/type/time/domain
```

例如“1+1 等于几”不需要用户长期偏好；“按我之前喜欢的酒店风格推荐”明确需要。

### 每轮都检索的问题

- latency；
- token；
- 错 memory 干扰；
- 隐私泄露面；
- stale preference 覆盖当前明确指令。

### Query 构造

Memory retrieval 不一定直接拿用户原句做 embedding；可以基于 current task + Session context 做 intent-aware query，同时过滤 `memory_type/subject/freshness`。

OpenViking文档中区分无 Session Context 的简单查找与需要 Session/Intent Analysis 的语义检索，也是很好的工程对照。

---

## 05-09. 用户频繁切换话题，记忆怎么设计才不会接不上？

### 不要把整个 Session 当一个主题

维护 topic/task boundaries：

```text
Session
 ├─ Thread A: 数据库性能
 ├─ Thread B: AgentDock
 └─ Thread C: 旅游计划
```

当前 Turn 先识别 active topic，Context Builder 优先加载该 topic 的 recent context；跨 topic 的稳定用户偏好通过长期 Memory 按需召回。

### Reference resolution

用户说“刚才那个方案”时，需要从 recent working set 解析；用户说“上个月说过的 PostgreSQL 权限方式”才进入长期 retrieval。

### Branching

Pi 的 conversation tree/Branch 概念可以很好解释多分支上下文：不同分支共享过去，但各自 tip 独立；这比把所有话题线性塞进一个 summary 更清楚。

---

## 05-10. 用户偏好、事实记忆、系统状态冲突时听谁的？

### 先建立优先级

```text
Authoritative System/Business State
        >
Current Explicit User Instruction
        >
Verified Stable Fact
        >
Stored Preference
        >
Inferred/Low-confidence Memory
```

例如 Memory 写“用户喜欢经济舱”，当前用户说“这次必须商务舱”，当前指令优先；订单系统显示退款 SUCCESS，而旧 Memory 写“退款待处理”，业务状态优先。

### Memory Conflict

不能简单 last-write-wins。要看 memory type、source、timestamp、confidence、validity。

```text
old: likes quiet hotel, confidence .8
new: this trip wants nightlife area, explicit current goal
```

这不是覆盖全局偏好，而是 scoped override。

### 设计 scoped memory

`global / project / trip / session / task` 不同 scope 可以并存，Context 时按最近且最具体原则投影。

---

## 05-11. 什么叫 Memory Hallucination？怎么和 LLM Hallucination 区分？

### Memory Hallucination

系统把错误、过期、错误归属或不该召回的 Memory 当成事实。例如：

- 把 A 用户偏好召回给 B 用户；
- 旧公司职位仍当当前职位；
- Agent 曾经错误推断的信息被写成永久事实；
- 一个临时旅行偏好被推广成长期偏好。

### LLM Hallucination

模型在当前证据之外自行生成不可靠内容。

两者可能叠加：错误 Memory 被召回后，LLM 又进一步扩展。

### Memory 防护

```text
Provenance
Freshness
Subject/Tenant Scope
Confidence
Conflict Detection
Admission Quality
User Correction
Deletion/Expiration
```

### 评测

不能只看 memory Recall。至少还要：
- precision；
- wrong-memory usage rate；
- stale recall rate；
- cross-user leakage；
- user correction rate；
- downstream task success。

OpenViking 的 retrieval trajectory 很有价值，因为错误答案可以追查到底是“找错 Memory”还是“模型用错 Memory”。

---

# 五层模型总结

```text
1 Durable Transcript
  完整对话/工具事实，审计和恢复

2 Runtime State
  当前 Run/Plan/Step/Checkpoint

3 Long-term Memory / Resource
  跨 Session 可召回信息

4 Model-facing Context
  本轮模型真正看到的投影

5 Business State
  订单/设备/退款等权威事实
```

如果面试能把这五层清楚区分，再结合 nanobot ContextGovernor、Pi Session/Harness、OpenViking Context DB、AgentDock 生命周期说明，Context/Memory 类问题基本就能经住连续追问。
