# 2026 Agent 面试补充：核心概念与架构（第 1 组）

> 来源：用户提供的《2026 大模型 Agent 面试全攻略（上）》截图。
>
> 本文件不直接照搬截图中的“回答要点”，而是先和仓库现有题目做语义去重，再按照本仓库的 Deep Complete 标准重新组织：**工程本质 → 运行机制 → 状态/边界 → Pi / nanobot / AgentDock / OpenViking 对照 → 失败路径 → 面试口述版**。

---

# Q1. 请简述 Agent 的基本架构组成，并解释它与传统 LLM Chain 的区别

## 这道题真正考什么

表面上是在问“Agent 有哪些组件”，实际上在看你是否已经从“LLM 调用 API”的思维进入 **Agent Runtime** 思维。

如果只回答：

```text
Agent = LLM + Planning + Memory + Tool
```

只能算概念层答案。它没有解释：

- 谁保存 Session；
- 谁决定本轮给模型什么 Context；
- Tool Call 谁真正执行；
- 权限在哪里校验；
- 进程崩溃后谁恢复；
- 外部副作用如何确认；
- 多租户和实例生命周期谁管理；
- 线上如何 Trace / Eval。

生产 Agent 更准确的结构应该分层。

## 核心结论

我会把 Agent 系统拆成五个责任面：

```text
┌─────────────────────────────────────────┐
│  Control Plane                          │
│  tenant / agent / instance / resource   │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  Agent Runtime / Harness                │
│  loop / stop / tool / recovery / budget │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  Context System                         │
│  transcript / memory / RAG / projection │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  Tool / MCP / Adapter                   │
│  schema / policy / execution / result   │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  Business System                        │
│  transaction / authz / authoritative DB │
└─────────────────────────────────────────┘
```

LLM 是 Runtime 中负责概率决策的一部分，不等于整个 Agent。

## 一次真实运行链路

```text
User
 ↓
Auth / Tenant / Session Resolution
 ↓
Durable Transcript + Runtime State
 ↓
Context Projection
 ├─ System / Policy
 ├─ Recent Messages
 ├─ Summary
 ├─ Memory / RAG
 ├─ Tool Schemas
 └─ Current Observation
 ↓
LLM Round
 ↓
Text or Tool Call Proposal
 ↓
Tool Registry
 ↓
Schema Validation
 ↓
Tool Policy / User Scope / Risk Gate
 ↓
MCP / HTTP / Java Service
 ↓
Tool Result
 ↓
Observation 回注模型
 ↓
下一轮 LLM
 ↓
Stop / Final / Checkpoint / Persist
```

其中有一个关键原则：

> **模型拥有“提议下一步动作”的权力，但不拥有“直接修改业务事实”的权力。**

例如模型可以提出 `create_work_order`，但真正创建工单的是 Java `WorkOrderService`。只有业务服务返回 `SUCCESS + work_order_id` 后，最终回答才能说“工单已创建”。

## Agent 和传统 Chain 到底差在哪里

不要简单说“Chain 是线性的，Agent 是自主的”。这个说法太粗，因为 Chain 也可以有条件分支，Graph 也可以有循环。

真正的区别是 **控制权和下一步路径由谁决定**。

### Chain / Workflow

```text
Step A
 ↓
Step B
 ↓
if condition
 ├─ Step C
 └─ Step D
```

下一步路径主要由开发者预先定义。

适合：

- 固定审批流；
- 数据 ETL；
- Quote → Confirm → Pay；
- 强顺序和强事务流程。

### Agent

```text
Goal
 ↓
Model Decision
 ↓
Action
 ↓
Environment Observation
 ↓
Model Decision
 ↓
...
```

下一步动作由模型根据当前 Observation 动态选择。

适合：

- 开放搜索；
- 复杂排障；
- 资料研究；
- 动态 Tool 选择；
- 无法事先枚举完整路径的任务。

### 实际生产通常不是二选一

更常见的是：

```text
Workflow owns deterministic state
            ↓
       Agent Node
   search / reason / rank
            ↓
Workflow continues
```

例如旅游预订：

```text
Agent：理解需求、查航班、查酒店、排序
                ↓
Workflow：QUOTE → LOCK → CONFIRM → PAY → ISSUE
```

这样开放决策交给 Agent，高风险副作用交给确定状态机。

## 四个项目怎么对照

### nanobot：轻量 Agent Runtime

可以用它解释“一次 Tool-using Agent Loop 到底怎么跑”。核心关注：

```text
AgentLoop
AgentRunner / AgentRunSpec
ContextGovernor
ToolRegistry
execute_tool_calls
Checkpoint / Recovery
Injection
```

也就是说 nanobot 更接近上面架构中的 **Agent Runtime / Harness**。

### Pi：更强调 Durable Harness

Pi 很适合解释：

```text
Session / Branch / AgentLane
operation state
intent / effect
settlement
replay / recovery
```

它告诉你一个 Agent 如果要跑长任务，不能只保存聊天记录，还要保存“操作执行到了什么阶段”。

### AgentDock：Control Plane

AgentDock 更适合解释：

```text
tenant
agent definition
runtime driver
container
workspace
credentials
task/event
resource limits
```

AgentDock 管“哪个用户运行哪个 Agent 实例”，nanobot/Pi 管“这个实例内部一次 Agent Run 怎么执行”。

### OpenViking：Context Database

OpenViking 更适合解释 Context / Memory 层：

```text
Resource
Memory
Skill
viking://
L0 Abstract
L1 Overview
L2 Detail
Retrieval Trajectory
```

它解决“哪些外部上下文应该找回来”，不是 Agent Loop 本身。

## 城市照明实际案例

用户说：

> “帮我查昨晚 XX 路异常能耗的路灯，并分析原因，如果确实异常就创建工单。”

不能简单做：

```text
LLM → SQL → CREATE WORK ORDER
```

更合理的是：

```text
WebSocket
 ↓
nanobot Runtime
 ↓
理解目标
 ↓
query_energy Tool
 ↓
Java Service
 ├─ user/project authz
 ├─ SQL / PostgreSQL RLS
 └─ result
 ↓
LLM 分析 Observation
 ↓
query_device_history
 ↓
LLM 判断候选异常
 ↓
create_work_order proposal
 ↓
Tool Policy
 ↓
Java WorkOrderService transaction
 ↓
SUCCESS / FAILED / UNKNOWN
 ↓
最终回答
```

这就是“Agent 架构”和“LLM Chain”真正的工程区别。

## 失败边界

面试官继续问时，要能回答：

1. Tool Timeout 是失败还是 UNKNOWN？
2. LLM 想跳过确认直接执行高风险操作怎么办？
3. Context 超限后哪些内容可以压缩，哪些 State 不能丢？
4. Agent 进程重启时恢复 Conversation 还是恢复 Operation？
5. 多实例同时处理同一个 Session，谁是 Single Writer？

## 1～2 分钟口述版

> 我不会把 Agent 简单定义成 LLM+Planning+Memory+Tool。生产 Agent 至少还需要 Session/State、Context 构造、Tool Registry、Policy、Recovery、Trace 和业务事实层。传统 Chain 的核心是下一步控制流主要由代码预先定义，而 Agent 的下一步动作可以根据环境 Observation 动态决定。实际系统通常是混合架构：开放搜索和语义判断交给 Agent，支付、退款、工单状态这种强副作用步骤交给 Workflow/业务状态机。比如 nanobot 负责轻量 Agent Loop，Pi 更强调 durable Harness，AgentDock 管多租户实例和容器，OpenViking 管 Memory/Resource/Skill Context；最终业务事实仍由 Java/数据库系统定义。

### 仓库关联

- `01-agent-runtime/deep-complete.md`
- `01-agent-runtime/agent-loop-deep-dive.md`
- `01-agent-runtime/runtime-platform-context-boundaries-deep-dive.md`

---

# Q2. 解释 ReAct 模式的工作原理

## 面试官真正考什么

这道题不是让你把 `Reasoning + Acting` 背出来，而是看你能不能解释：

> **为什么 Agent 能利用外部世界的新 Observation 改变下一步决策，以及 Runtime 在这个循环里负责什么。**

## 核心结论

ReAct 的工程本质不是“模型把 Thought 打印出来”，而是：

```text
当前 Context
    ↓
模型做 Decision
    ↓
提出 Action / Tool Call
    ↓
Runtime 执行 Tool
    ↓
获得 Observation
    ↓
Observation 进入下一轮 Context
    ↓
模型重新 Decision
```

因此 ReAct 的价值来自 **闭环反馈**。

## 为什么不应该把 `Thought:` 当成必要协议

很多旧资料会把 ReAct 描述成：

```text
Thought → Action → Observation → Thought
```

概念上没错，但现代生产系统不应该要求模型暴露完整私有思维链。

运行时真正需要持久化、审计的是：

```text
Model Request
Tool Call
Arguments
Policy Decision
Tool Result
State Transition
Final Answer
```

因此在面试中更稳妥的说法是：

> ReAct 是模型决策与外部 Action/Observation 交替进行的 Agent 控制模式，而不是要求系统保存可见的完整 CoT。

## 一轮 ReAct 在 Runtime 里的真实过程

```text
Round 1 Context
    ↓
LLM
    ↓
Tool Call: query_device_alarm(device_id=123)
    ↓
Tool Registry 找 Tool
    ↓
Schema 校验
    ↓
Permission / Scope 校验
    ↓
执行
    ↓
Tool Result:
{
  "status": "SUCCESS",
  "alarm": "power_overload"
}
    ↓
作为 Observation 加入 Context
    ↓
Round 2
    ↓
LLM 决定继续 query_energy_history
    ↓
...
```

这里模型只决定“想做什么”，Runtime 负责“这个动作能不能做、怎么做、失败如何表达”。

## nanobot 中怎么理解

nanobot 是很适合解释 ReAct 工程实现的例子。

可以把核心链路理解成：

```text
AgentLoop
   ↓
AgentRunner
   ↓
provider/model request
   ↓
assistant response
   ├─ final text → stop
   └─ tool calls
         ↓
   execute_tool_calls()
         ↓
   Tool Result
         ↓
下一轮 model request
```

同时 Runtime 还要负责：

- 最大 iteration；
- Tool 并发是否安全；
- Context budget；
- checkpoint；
- interrupted Tool recovery；
- 用户中途 injection；
- workspace / security boundary。

这说明 ReAct 不是一个 Prompt 模板，而是一个 **Runtime Loop**。

## ReAct 的最大工程问题

### 1. 无限 Tool Loop

例如：

```text
search → 没找到
search → 换个 query
search → 再换
search → ...
```

需要：

```text
max_iterations
max_tool_calls
deadline
token_budget
repeated-call guard
```

### 2. Tool Result 越来越大

每轮 Observation 都进入 Context，可能导致：

```text
Context growth
→ token cost
→ latency
→ attention dilution
```

所以必须配 Context Governance / Artifact / Summary / Dynamic Truncation。

### 3. 副作用 Tool 不能自由 ReAct

如果 Tool 是：

```text
refund
create_order
delete_file
control_device
```

不能让模型在 ReAct 中“试试看”。

需要：

```text
Tool Policy
precondition
idempotency
HITL
business state machine
```

### 4. Observation 可能不可信

网页、RAG 文档、外部 API 都可能包含恶意内容，Observation 不是 System Instruction。

必须把：

```text
instruction authority
≠
retrieved content
```

明确分层。

## ReAct vs Plan-and-Execute

```text
短任务 / 高不确定反馈
        ↓
      ReAct

长任务 / 多依赖 / 要恢复
        ↓
Plan-and-Execute

实际复杂系统
        ↓
Plan
 ├─ Step A：局部 ReAct
 ├─ Step B：确定 Tool
 └─ Step C：局部 ReAct
```

因此最常见的高级设计不是二选一，而是“结构化 Plan + Step 内 ReAct”。

## Pi / AgentDock 怎么补充这个理解

### Pi

Pi 可以帮助解释 ReAct Loop 为什么还需要 durable operation/effect state。模型的下一轮决策只是认知层，真实外部副作用必须有持久执行语义。

### AgentDock

AgentDock 则说明 ReAct Runtime 只是单实例内部机制。平台还要管理：

```text
tenant
container
runtime driver
task lifecycle
streaming event
resource limit
```

## 1～2 分钟口述版

> ReAct 的核心不是让模型显式打印 Thought，而是让模型的决策和外部 Action/Observation 交替进行。模型先根据当前 Context 提出 Tool Call，Runtime 做 Schema、权限和执行校验，拿到 Tool Result 后作为 Observation 回注下一轮模型，直到满足停止条件。像 nanobot 的 AgentRunner 就是典型 tool-using loop。生产上 ReAct 一定要配 max iteration、deadline、context budget、repeated-call guard 和高风险 Tool Policy，否则非常容易出现死循环、成本爆炸和副作用事故。长任务我一般会用 Plan-and-Execute 管结构，再在单个 Step 内使用 ReAct。

### 仓库关联

- `01-agent-runtime/deep-complete.md`
- `01-agent-runtime/agent-loop-deep-dive.md`
- `02-planning-routing-multi-agent/react-plan-dag-deep-dive.md`

---

# Q3. 如何实现 Agent 的长期记忆（Long-term Memory）？

## 面试官真正考什么

这道题最容易被回答浅。

如果回答：

```text
短期记忆 = Context Window
长期记忆 = RAG + Vector DB
```

只能算入门。

真正要回答的是：

> **什么信息值得成为长期记忆？什么时候写？怎么去重和更新？什么时候读？和 Session/History/RAG/业务 State 有什么区别？错误记忆怎么治理？**

## 先把五种东西分开

```text
1. Durable Transcript
   完整对话/Tool 事实记录

2. Model-facing Context
   本轮真正给 LLM 看的信息

3. Runtime State
   当前任务执行到哪一步

4. Long-term Memory
   跨 Session 仍可能有价值的用户/Agent经验

5. Business State
   订单、工单、设备、退款等最终事实
```

长期记忆只是其中一层。

## 为什么“长 Context”不等于长期记忆

把过去几十万 Token 全塞模型，有三个问题：

```text
成本高
噪声高
缺少语义更新/冲突治理
```

例如用户半年前说：

> “我喜欢住经济型酒店。”

今天说：

> “以后出差都住五星。”

如果只是把历史全部塞进去，模型需要自己猜哪个是最新偏好。

真正的 Memory 系统应该有：

```text
old preference
   ↓
new evidence
   ↓
conflict detection
   ↓
version / supersede
   ↓
current memory
```

## 一个完整的 Memory Write Pipeline

```text
Conversation / Tool Events
          ↓
Memory Candidate Extraction
          ↓
Admission Policy
  ├─ 是否长期有价值？
  ├─ 是否稳定？
  ├─ 是否敏感？
  └─ 是否只是本轮临时状态？
          ↓
Normalize / Entity Resolve
          ↓
Dedup / Conflict Detection
          ↓
Provenance + Timestamp + Confidence
          ↓
Persist
```

### 什么适合写 Memory

例如：

```text
用户稳定偏好
长期项目背景
长期角色关系
反复验证过的工作习惯
Agent 过去任务中的可迁移经验
```

### 什么不应该写

```text
一次性临时参数
本轮 Tool 中间状态
没有验证的模型猜测
支付/订单真实状态副本
敏感信息的无边界复制
```

尤其不能把模型自己推断出的内容直接当长期事实。

## Memory Retrieval 也不能每轮都做

一个更合理的读取流程：

```text
User Turn
   ↓
Memory Router / Retrieval Trigger
   ↓
判断当前任务是否需要长期记忆
   ↓ yes
Query Rewrite / Intent
   ↓
Memory Retrieval
   ↓
Freshness / Permission / Conflict Filter
   ↓
Top Memories
   ↓
Context Projection
```

如果每轮都检索 Memory，会造成：

- token 浪费；
- 旧记忆干扰当前问题；
- 隐私暴露面扩大；
- 不相关偏好误导模型；
- latency 上升。

## OpenViking 怎么理解长期 Context

OpenViking 是一个很适合解释“长期 Context Database”的项目。

它把 Agent 的外部上下文统一组织为：

```text
Resource
Memory
Skill
```

并通过：

```text
viking://
```

统一寻址。

内容支持分层：

```text
L0 = Abstract
L1 = Overview
L2 = Detail
```

因此不是每次都把完整内容装进模型，而是先低成本找到相关目录/摘要，再按任务需要逐步展开。

这和传统“Vector DB TopK 文本块全塞 Prompt”相比，更接近 Context Engineering。

## nanobot 中要区分什么

nanobot 当前很适合说明：

```text
Session history
Summary / archive
Context Governance
Model-facing Context
```

但这些能力不能简单等同于一个完整的“跨 Session 长期 Memory 平台”。

换句话说：

```text
nanobot ContextGovernor
解决：本轮给模型哪些已有信息

OpenViking
解决：外部长周期 Context/Memory 如何组织、检索、逐层加载
```

两者是互补关系。

## Pi 中的 Session/Conversation Tree 也不是 Memory 的同义词

Pi 的 durable session / branch / operation state 解决的是：

```text
“这段 Agent 运行发生了什么、现在执行到哪”
```

而长期 Memory 解决的是：

```text
“过去哪些信息值得在未来其他任务里再次使用”
```

所以 Session ≠ Memory。

## AgentDock 的 Workspace 也不是长期 Memory

AgentDock 的持久 Workspace 解决：

```text
文件 / 工作目录 / Agent 实例持久资产
```

它不等于语义长期记忆。

例如一个 Markdown 文件一直存在于 Workspace，不代表每个 Turn 都应该被检索进 Context。

## 城市照明案例

用户长期负责“浦东新区 A 项目”。

可以把稳定信息写成 Memory：

```json
{
  "type": "project_preference",
  "subject": "user-123",
  "project": "pudong-a",
  "confidence": 0.98,
  "source": "explicit_user_statement",
  "updated_at": "..."
}
```

但设备实时状态：

```text
lamp_10086 = OFF
```

不应该保存成长期 Memory 作为未来事实，因为设备状态会变化。

下一次用户问：

> “帮我看看昨晚异常的灯。”

系统可以用 Memory 推断默认项目是浦东 A，但真实灯具状态仍必须通过数据库/Tool 查询。

## Memory Hallucination 怎么来的

例如系统错误记住：

> “用户只看 A 项目。”

但这个信息其实只是一次会话临时筛选条件。

以后所有查询都默认过滤 A 项目，这就是 **Memory Hallucination / Memory Pollution**。

所以 Memory 必须有：

```text
source / provenance
confidence
valid_from / valid_to
last_verified
scope
superseded_by
```

必要时允许用户纠正和删除。

## 如何评估长期 Memory

不能只看 Recall。

至少要看：

```text
Write Precision
应该记的是否记住
不该记的是否误写

Retrieval Precision / Recall
该取时能否取到

Conflict Resolution Accuracy
新旧记忆冲突是否正确更新

Freshness
是否使用了过期信息

Usefulness
召回后是否真的提升任务成功率

Privacy Leakage
是否跨 tenant/user 泄漏
```

## 1～2 分钟口述版

> 长期记忆不能简单理解成把聊天历史 Embedding 到向量库。我会先区分 durable transcript、model-facing context、runtime state、long-term memory 和 business state。真正的 Memory 系统要有写入 admission：只保存跨 Session 稳定、有长期价值的信息，并做去重、冲突更新、provenance、时间和权限；读取时也不是每轮都搜，而是由 Memory Router 判断是否需要，再做 freshness 和 scope 过滤。像 OpenViking 可以用 Resource/Memory/Skill 和 L0/L1/L2 做长期 Context Database；nanobot 更擅长 Session/Context Governance，两者是互补的。长上下文模型可以减少压缩频率，但不能替代长期 Memory 的治理、检索和冲突处理。

### 仓库关联

- `05-context-memory/deep-complete.md`
- `05-context-memory/context-engineering-deep-dive.md`
- `05-context-memory/memory-session-state-deep-dive.md`
- `06-rag-retrieval/hybrid-search-rerank-context-db-deep-dive.md`

---

# 去重结论

这三道题都不是全新主题，因此不新增到 104 道核心题计数里，而是作为 **高频问法 / 追问入口** 补充：

```text
Q1 Agent 架构 vs Chain
→ 01 Agent Runtime / Workflow Boundary

Q2 ReAct 工作原理
→ 01 Agent Loop + 02 ReAct/Plan/DAG

Q3 Long-term Memory
→ 05 Context/Memory + 06 OpenViking/Retrieval
```

这样后续遇到相同题，不会在仓库里形成多份互相冲突的答案，而是保持“一个主题、一套权威工程解释、多个面试问法入口”。
