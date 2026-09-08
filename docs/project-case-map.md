# 项目案例对照：Pi × nanobot × AgentDock × OpenViking

> 本文是 01～07 章节后续深度重构时的统一案例基线。原则不是“每题硬塞四个项目”，而是根据问题选择最能解释机制的真实项目，并明确区分“当前源码已经实现”和“企业级应该补什么”。

## 为什么用这四个项目

这四个项目分别覆盖 Agent 工程体系的不同层：

```text
Pi
└─ 更适合看 Agent Runtime / Harness / Operation State / Tool Effect / Session

nanobot
└─ 更适合看轻量 Agent Loop / Context Governance / Tool Registry / Recovery / Injection

AgentDock
└─ 更适合看平台化：多租户、多实例、容器隔离、Driver、任务流、SSE/WebSocket、运维

OpenViking
└─ 更适合看 Context Database / Memory / Resource / Skill / 分层加载 / 检索轨迹
```

它们不是互相替代关系，而是可以拼成一张完整的 Agent Engineering 图：

```text
                        ┌──────────────────────────┐
                        │        AgentDock         │
                        │ Control Plane / Tenant   │
                        │ Container / Driver / API │
                        └─────────────┬────────────┘
                                      │
                     ┌────────────────┼────────────────┐
                     │                │                │
                     ▼                ▼                ▼
              ┌────────────┐   ┌────────────┐   ┌────────────┐
              │  nanobot   │   │     Pi     │   │ Other Agent│
              │ AgentLoop  │   │  Harness   │   │  Drivers   │
              └─────┬──────┘   └─────┬──────┘   └────────────┘
                    │                │
                    └───────┬────────┘
                            ▼
                  Tool / MCP / Service
                            │
                            ▼
                  Java / DB / External API

                  Context / Memory sidecar
                            │
                            ▼
                     ┌────────────┐
                     │ OpenViking │
                     │ viking://  │
                     │ L0/L1/L2   │
                     └────────────┘
```

## 1. Pi：用来讲“真正的 Harness 到底是什么”

Pi 当前仓库把项目明确拆成 `pi-agent-core`、`pi-coding-agent`、统一模型层等；其 Harness 设计进一步把 Session、conversation tree、operation state machine、effect intent/settlement、recovery、usage ledger、hooks、telemetry 等都拉到显式工程层。

### 最适合用于回答的题

- Agent Loop 与 Runtime/Harness 区别
- Session 为什么不能只是 `List<Message>`
- Tool 副作用为什么需要 intent / settlement
- Crash Recovery 如何避免重复副作用
- 多分支 Conversation Tree / Branch / Lane
- Compaction 为什么不等于删除历史
- 中途 steering / follow-up 怎么处理
- Tool replay policy 为什么不能统一
- Harness 与模型能力为什么必须分离

### 面试表达示例

如果面试官问“Agent Harness 是什么”，不要只答：

> Harness 就是包在模型外面的一层工具和 Prompt。

更好的回答是：

```text
Model 只负责概率性决策
        ↓
Harness 持有 durable state
        ↓
Harness 决定 Tool 能不能执行
        ↓
Harness 记录 effect intent
        ↓
外部副作用发生
        ↓
Harness settlement
        ↓
Crash 后根据 durable operation state 恢复
```

Pi 的 Harness 设计尤其适合拿来解释“为什么生产 Agent 必须有 operation state machine”。

### 重要边界

Pi README 也明确说明：Pi 本身默认按启动进程的权限运行，不自带完整的 filesystem/process/network/credential 权限系统；需要更强隔离时，要通过 Docker、micro-VM 或其他 sandbox 方案补。这一点非常适合拿来讲：

> Runtime/Harness 能力和 Sandbox/Security Boundary 是两个层级，不能混为一谈。

---

## 2. nanobot：用来讲“轻量 Agent Runtime 的真实执行链”

nanobot 很适合面试，因为它的主链相对清晰，可以沿源码直接学习：

```text
AgentLoop
   ↓
AgentRunner
   ↓
ContextGovernor / TranscriptBuilder
   ↓
LLM Round
   ↓
ToolRegistry / execute_tool_calls
   ↓
Tool Result Observation
   ↓
下一轮 LLM
```

同时它已经包含一些非常值得讲的工程能力：

- `AgentRunSpec`
- `AgentRunner`
- Context Governance / Compaction
- Tool Registry / Tool Execution
- `concurrent_tools`
- `concurrency_safe`
- Hook 生命周期
- Mid-turn Injection
- Runtime Checkpoint
- Restart Recovery
- `awaiting_tools / tools_completed / final_response`

### 最适合用于回答的题

- ReAct / Agent Loop 实际如何跑
- Tool Call 如何从模型建议变成 Runtime 执行
- Context 在每一轮 LLM 前如何重建
- Tool Error 如何作为 Observation 回注
- Tool 并发调用怎么做
- 用户中途改变目标如何 Injection
- 进程重启时如何恢复 Session
- 为什么 `awaiting_tools` 不能直接自动重放
- AgentHook 如何做 Trace / Eval 扩展

### 面试时一定要区分

```text
nanobot 当前已经实现
        ≠
企业级 Agent 平台应该具备的全部能力
```

例如 nanobot 支持一轮响应内对 `concurrency_safe` Tool 做并发执行，但它不是一个完整 DAG Scheduler；它有 Restart Recovery，但没有通用 Saga/Compensation 框架；它有运行时 model 配置，但没有一个通用的“问题复杂度自动 Model Router”。

回答里必须把这些边界说清楚。

---

## 3. AgentDock：用来讲“Agent 怎么从单机 Runtime 变成平台”

AgentDock 的价值不在于再造一个 LLM Loop，而是在 Runtime 外面补平台层能力。

当前项目定位包括：

- Nanobot 多实例容器化运行
- 多租户 Workspace
- Driver Registry，可挂 Nanobot / Vanilla / OpenCode / Codex / Claude Code / API 等执行引擎
- Agent 实例生命周期管理
- 持久 Workspace
- REST + SSE + WebSocket
- Task Event Stream
- MCP / Skill 分配
- Snapshot / Git Backup
- Container 隔离
- Egress Proxy
- CPU / Memory 限制
- Credential 管理
- Workflow / Schedule

### 最适合用于回答的题

- Java/Spring 系统如何接 Agent Runtime
- 多用户 Agent 如何做隔离
- 一个用户多个 Agent 实例怎么管理
- Session 和 Container 生命周期是不是一回事
- Driver/Runtime 如何抽象
- 为什么 Control Plane 和 Agent Runtime 要分开
- 流式消息协议怎么设计
- Agent 平台如何做资源配额、审计、凭证管理
- Tool/MCP/Skill 如何按 Tenant/Agent 分配
- Agent 为什么需要 Workspace 持久化
- 多实例如何实现可观测、暂停、恢复和自动唤醒

### 一个很实用的面试架构

```text
前端 / Java Service
        ↓ REST / WebSocket / SSE
AgentDock Control Plane
        ↓
Auth / Tenant / Agent Instance / Task
        ↓
Driver Registry
   ┌────┼─────┐
   ▼    ▼     ▼
nanobot Pi  Other Runtime
        ↓
Container / Workspace / Egress Boundary
        ↓
Tool / MCP / Business Service
```

这样回答“企业里怎么部署 Agent”会比单纯讲 LangChain、LangGraph 更像真实系统设计。

---

## 4. OpenViking：用来讲 Context Engineering，而不是只讲向量库

OpenViking 的核心定位是 **Context Database for AI Agents**。它把 Memory、Resource、Skill 放在统一的 `viking://` 虚拟文件系统中，并对内容构建：

```text
L0 Abstract
L1 Overview
L2 Details
```

Agent 不需要一上来把完整资料塞进 Context，而是可以逐层判断相关性再按需深入。

### 最适合用于回答的题

- Context Engineering 和传统 RAG 有什么区别
- 为什么 Memory / Skill / Resource 不应该完全分散管理
- 长上下文为什么不能只依赖超大 Context Window
- 分层加载如何节省 Token
- Parent/Child Retrieval 与目录递归检索
- Memory Admission / Session Commit
- Retrieval 为什么要可观察
- Agent 如何知道自己为什么召回了某段内容
- RAG Debugging 为什么不能只有最终 Top-K

### 一个典型 Context 构造过程

```text
User Query
    ↓
当前 Session / Goal
    ↓
OpenViking 找到高相关目录
    ↓
先读取 L0 Abstract
    ↓
需要进一步判断？
    ↓ yes
读取 L1 Overview
    ↓
确定需要原文
    ↓
读取 L2 Details
    ↓
组合进 Model-facing Context
```

它非常适合和 nanobot 的 ContextGovernor 放在一起比较：

```text
OpenViking
负责：外部 Context 的组织、召回、分层加载、长期记忆

nanobot Context Governance
负责：一次 Agent Run 内真正发给模型的消息如何控制在预算内
```

两者解决的是不同层的问题。

---

# 01～07 章节应该如何结合这四个项目

## 01 Agent Runtime

主案例：**nanobot + Pi**

辅助案例：AgentDock

重点回答：

- Loop 是怎么跑的
- Harness 到底持有什么状态
- Tool Effect 怎么落 durable state
- Agent Runtime 和 Control Plane 的边界

## 02 Planning / Routing / Multi-Agent

主案例：**nanobot + Pi**

平台案例：**AgentDock Driver Registry / Workflow**

重点回答：

- ReAct 与 Plan-and-Execute
- Model Router
- Planner/Worker/Reviewer
- Mid-turn Replan
- Parallel Worker / stale result

注意：不要为了“多 Agent”而多 Agent。很多问题用单 Runtime + Tool Loop + Workflow 就能解决。

## 03 Tool / MCP

主案例：**nanobot ToolRegistry + AgentDock MCP/Skill 分配 + Pi Tool/Extension**

重点回答：

- Tool Schema
- Tool Registry
- Tool Policy
- MCP 是协议，不是权限系统
- Tool 发现与 Tool 执行必须分层
- Tenant / Agent / Role 作用域

## 04 Reliability / Security

主案例：**Pi Harness + nanobot Recovery + AgentDock Sandbox**

重点回答：

```text
Pi      → durable operation state / intent / settlement / replay policy
nanobot → checkpoint / interrupted tool / explicit recovery
AgentDock → container / egress / credential / tenant boundary
```

这一章必须把：

- Retry
- Idempotency
- UNKNOWN
- Reconcile
- Compensation
- Sandbox
- Prompt Injection

拆开，不能都叫“容错”。

## 05 Context / Memory

主案例：**OpenViking + nanobot + Pi**

重点回答：

```text
OpenViking → 长期 Context Database
nanobot    → 本轮 Model-facing Context Governance
Pi         → Session / Conversation Tree / Compaction / Branch
```

这里会形成非常完整的“长期上下文 + 当前运行上下文 + durable conversation”三层结构。

## 06 RAG / Retrieval

主案例：**OpenViking**

业务案例：城市照明 Text-to-SQL / 300+ 表 Schema Retrieval

平台案例：AgentDock 可以作为集成和运行入口，但不是检索算法本身。

重点回答：

- BM25 + Dense
- RRF
- ReRank
- Query Rewrite
- Parent/Child
- Directory Recursive Retrieval
- Retrieval Trajectory
- Schema Retrieval
- Permission-aware Retrieval

## 07 Harness / Eval / Trace

主案例：**Pi Harness + nanobot Hook + AgentDock Event Stream + OpenViking Retrieval Trajectory**

重点回答：

```text
Agent Trace
├─ model round
├─ tool call
├─ tool result
├─ state transition
├─ checkpoint
├─ context selection
└─ retrieval trajectory
```

这样才能真正做：

- Golden Dataset
- Tool Mock
- Trajectory Replay
- Failure Attribution
- Model/Prompt/Retriever A/B
- Online Regression Detection

---

# 后续每一道深度题统一增加“真实项目对照”

核心题以后至少增加下面一节：

```markdown
## 真实项目对照

### nanobot 当前怎么做
### Pi 当前怎么做
### AgentDock 平台层怎么做
### OpenViking 在这个问题里解决哪一层
### 如果让我做企业版，我会怎么组合
```

但不会机械地四个项目都写。比如 Tool Recovery 重点用 Pi + nanobot；Context Retrieval 重点用 OpenViking；多租户隔离重点用 AgentDock。

## 最终目标

不再把资料写成：

```text
问题
→ 定义
→ 优点
→ 缺点
→ 结束
```

而是写成：

```text
问题
  ↓
底层机制
  ↓
状态 / 数据结构
  ↓
真实源码项目怎么做
  ↓
不同项目为什么设计不同
  ↓
失败场景
  ↓
企业版如何组合
  ↓
面试官追问
  ↓
最终口述版
```

这才是 01～07 后续重构的标准。
