# Agent Runtime、Control Plane、Context Database 的边界怎么划分

> 这篇不是讲“Agent 有哪几层”，而是回答一个在系统设计面试里很容易被追问的问题：**Agent Runtime、平台控制面、业务系统、Context/Memory 系统到底谁负责什么？为什么不能都塞进一个 Agent 进程？**

## 1. 面试官真正考什么

如果只回答：

```text
前端 → Agent → Tool → 数据库
```

只能说明你会搭 Demo。

生产系统真正难的是**责任边界和事实所有权**：

- 谁拥有 Session 的事实状态？
- 谁决定一轮 Agent 是否继续？
- 谁可以真正执行退款、删除、下发设备控制？
- 谁负责多租户和容器资源？
- 谁负责从长期记忆/知识库里取 Context？
- Runtime 挂了，平台如何恢复？
- Context 系统错召回，为什么不能直接导致越权 Tool 执行？

这类问题本质是在考：**你有没有把模型、Runtime、平台和业务系统拆成不同可信域。**

---

## 2. 核心结论

我会把生产 Agent 至少拆成四个责任域：

```text
                        ┌──────────────────────┐
                        │      Control Plane   │
                        │ AgentDock 类平台层   │
                        │ tenant / agent / task│
                        │ container / quota    │
                        └──────────┬───────────┘
                                   │ provision / route / observe
                                   ▼
┌────────────────────────────────────────────────────────────┐
│                    Agent Runtime / Harness                 │
│        nanobot / Pi Agent Core / Pi Harness               │
│  loop / state / context projection / tool dispatch / stop │
└───────────────┬──────────────────────────────┬─────────────┘
                │                              │
                │ retrieve context             │ tool/action
                ▼                              ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│ Context / Memory System  │      │   Business Truth Layer   │
│      OpenViking          │      │ Java Service / DB / API  │
│ memory/resource/skill    │      │ auth/tx/idempotency      │
│ L0/L1/L2 / retrieval     │      │ state machine / audit    │
└──────────────────────────┘      └──────────────────────────┘
```

一句话概括：

> **模型负责提出概率性决策；Runtime/Harness 负责把决策约束成可执行过程；Control Plane 负责实例、租户、资源和运维；Context Database 负责可检索上下文；业务系统负责最终事实和副作用。**

---

## 3. 为什么这四层不能混在一起

### 3.1 Runtime 不应该拥有业务最终事实

例如模型说：

> “退款已经成功。”

这句话本身不是事实。

真正事实应该来自：

```text
refund_service.status(request_id) == SUCCESS
```

所以：

```text
LLM      → 产生 refund Tool Call
Runtime  → 校验、执行、回注 Tool Result
Java 服务 → 真正决定退款状态
DB/支付方 → 保存最终事实
```

如果把业务事实交给 Agent Transcript，一旦模型幻觉、Context 压缩、进程恢复，业务状态就可能被错误推断。

---

### 3.2 Control Plane 不应该自己实现 Agent Loop

平台层经常需要：

```text
create agent
start container
pause/resume
route task
stream events
quota
workspace
backup
RBAC
```

但它不应该再自己维护一套：

```text
LLM → Tool → LLM → Tool → Final
```

否则会出现双 Runtime：

```text
AgentDock retry
    +
nanobot retry
    +
业务 Service retry
```

最终很难回答：**谁才是一次 Tool Call 的 owner？**

AgentDock 当前更适合被理解成 Control Plane：它负责多租户、Agent 实例、Task、Docker 容器、Driver、MCP/Skill 分配和事件流，而具体 Tool Loop 由选中的 driver/runtime 执行。

---

### 3.3 Context Database 不应该直接拥有执行权限

OpenViking 可以把：

```text
memory
resource
skill
```

组织在 `viking://` 下，并通过 L0/L1/L2 分层加载和 recursive retrieval 找到相关内容。

但召回到一句：

> “用户以前偏好自动执行高风险操作”

也不能成为权限依据。

所以：

```text
Context = 影响模型理解
Policy  = 决定动作是否允许
```

必须分开。

---

## 4. 用四个真实项目看这四层

## 4.1 nanobot：轻量 Agent Runtime

nanobot 当前核心更接近：

```text
AgentLoop
   ↓
AgentRunner
   ↓
ContextGovernor / Transcript
   ↓
LLM Runtime
   ↓
ToolRegistry / execute_tool_calls
   ↓
Tool Result observation
   ↓
Checkpoint / Session / Recovery
```

它的优势是 Runtime 边界清晰：

- `AgentRunSpec` 描述一次运行所需 runtime/tools/budget/session 等参数；
- `AgentRunner` 负责一轮轮模型调用；
- `ToolRegistry` 和 execution 层负责工具实际执行；
- `ContextGovernor` 负责 model-facing context 治理；
- recovery 层处理 interrupted turn。

因此它很适合作为“**一个 Agent Run 怎么执行**”的案例。

但它不是完整多租户 SaaS Control Plane。

---

## 4.2 Pi：从 Agent Core 继续向 Durable Harness 推进

Pi 项目把 runtime/harness 分得更细。

`pi-agent-core` 负责 Tool Calling 和 Agent State；而 AgentHarness 规范进一步引入：

```text
Session
Branch / AgentLane
Operation
operation state
entry tree
usage ledger
intent
settlement
recovery
replay policy
```

它特别适合回答：

> “如果 Runtime 在 Tool 副作用中间挂了，怎样知道重启后该不该重放？”

Pi Harness 的思路不是“看聊天记录猜进度”，而是保存**完整 durable operation state**。

例如：

```text
operation.state = effect_pending
replay = never
```

重启时就知道这个外部 effect 可能已经发生，不能再直接 replay。

这比普通 Agent Loop 更接近数据库/分布式系统里的 durable state machine。

---

## 4.3 AgentDock：Runtime 外面的平台层

AgentDock 当前已经有比较典型的平台职责：

```text
Workspace / Tenant
      ↓
Agent definition
      ↓
Driver
      ↓
Docker provision
      ↓
Task
      ↓
SSE / WebSocket events
      ↓
Snapshot / backup / quota / audit
```

并且同一个平台可以挂不同 runtime/driver：

```text
Nanobot
Vanilla
OpenCode
Codex
Claude Code
API
```

这说明一个关键架构思想：

> **Agent 产品层不应该和某一个 Runtime 强绑定。**

平台管理的是：

```text
谁的 Agent
在哪个容器
使用哪个 Driver
可以用哪些 Skill/MCP
分配多少资源
任务状态是什么
```

而不是自己参与每一轮模型推理。

---

## 4.4 OpenViking：Context Database，而不是 Runtime

OpenViking 当前强调的是：

```text
viking://
├── resources
├── memories
└── skills
```

并把一个 Context Entry 分成：

```text
L0 Abstract
L1 Overview
L2 Details
```

这和 Runtime 的 Context Compaction 解决的是不同问题。

### OpenViking 解决：

> 整个知识/记忆空间里，**哪些信息应该拿回来？**

### nanobot ContextGovernor 解决：

> 已经得到 Transcript、Tool Result、Memory、Resource 后，**本轮哪些内容真正发给模型？**

这两个层经常会被面试者混为一谈。

---

## 5. 一个真实城市照明 Agent 怎么分层

假设用户问：

> “分析昨晚海八路能耗异常的灯，并创建检修任务。”

合理执行链：

```text
Web UI
  ↓
AgentDock
  ├─ Auth / Workspace / Agent instance
  └─ Route Task → Nanobot container
                ↓
             nanobot
       build model context
                │
        ┌───────┴─────────┐
        │                 │
        ▼                 ▼
   OpenViking          Tool Registry
   召回道路规则          query_energy
   历史处置经验          get_alarm
   项目知识              create_work_order
        │                 │
        └───────┬─────────┘
                ↓
              LLM
                ↓
         Tool Call proposal
                ↓
       Runtime / Policy check
                ↓
          Java Domain Service
                ↓
     PostgreSQL / device platform
                ↓
         authoritative result
                ↓
            observation
                ↓
              LLM
```

这里要特别强调：

```text
道路规则/历史经验 → 可以来自 OpenViking
设备状态/工单状态 → 必须来自业务系统
```

不能反过来。

---

## 6. 状态应该分别放在哪里

可以按“事实寿命 + owner”来划分：

| 状态 | Owner | 典型存储 |
|---|---|---|
| 当前 Agent iteration | Runtime | process + checkpoint |
| Conversation transcript | Session runtime/store | file/DB/event log |
| Tool call pending/completed | Runtime/Harness | checkpoint/operation state |
| Agent instance status | Control Plane | Postgres |
| container/workspace/quota | Control Plane | Postgres + Docker |
| user preference memory | Context DB | OpenViking |
| domain knowledge | Context DB / KB | OpenViking/vector/index |
| alarm/order/refund truth | Business Service | PostgreSQL/domain DB |

一个很重要的面试判断是：

> **“这个状态丢了，是聊天体验变差，还是业务事实发生错误？”**

如果是后者，就不能只存在 Agent Memory 或 Prompt 中。

---

## 7. Java / Spring 企业平台怎么补

如果以 Java 业务服务为中心，我会设计：

```text
AgentGateway
 ├─ IdentityContext
 ├─ TenantContext
 ├─ ModelRoutingPolicy
 └─ AgentRuntimeClient

ToolGateway
 ├─ ToolRegistryView
 ├─ AuthorizationPolicy
 ├─ ArgumentValidator
 ├─ RiskPolicy
 ├─ IdempotencyManager
 └─ AuditPublisher

Domain Service
 ├─ DeviceService
 ├─ AlarmService
 ├─ WorkOrderService
 └─ Payment/Order Service
```

Runtime 可以替换：

```text
nanobot / Pi / other agent runtime
```

但 `Domain Service` 不需要跟着变。

---

## 8. 常见错误设计

### 错误一：把 Redis 叫“Agent Memory”

Redis 是存储介质，不是 Memory 语义。

你仍然必须回答：

```text
保存什么？
什么时候写？
什么时候读？
谁能覆盖？
冲突怎么办？
过期策略是什么？
```

### 错误二：把容器隔离当 Tool 权限

AgentDock 的 Docker/container sandbox 解决 OS/资源边界；Tool RBAC 解决业务权限。

```text
Container isolation != business authorization
```

### 错误三：把 RAG 结果当业务事实

RAG 可以回答制度/说明/经验；实时余额、报警状态、设备开关状态必须实时查询 authoritative service。

### 错误四：平台和 Runtime 双重拥有 Session

如果两边都可以修改完整 Session，会出现 version conflict、重复 Tool、断线恢复歧义。

需要明确 single writer 或 version/CAS。

---

## 9. 面试官继续追问

### Q1：为什么不把 OpenViking 直接嵌入 nanobot 进程？

可以嵌入，但生产上仍建议逻辑分层。Context 数据寿命通常比某个 Agent 进程长，而且可能被多个 Agent/Runtime 共享。

### Q2：AgentDock 里一个用户开两个会话，需要两个容器吗？

不一定。**Agent instance、container、conversation 是三个不同概念。** 是否一会话一容器由隔离和成本要求决定，不能混为一谈。

### Q3：Pi 和 nanobot 谁更“高级”？

不要这么回答。它们关注面不同。nanobot 是轻量实用 Runtime；Pi 的 Harness 规范对 durable operation/effect recovery 建模更重。应该按需求边界比较。

### Q4：谁应该决定 Tool 能不能执行？

模型只能提出 Tool Call。最终权限必须在 Runtime/Tool Gateway/Domain Service 的代码边界校验。

---

## 10. 1～2 分钟口述版

> 我不会把生产 Agent 看成一个大进程，而会拆成 Runtime、Control Plane、Context Database 和业务事实层。nanobot 很适合说明 Agent Loop、Context Governance、Tool Execution 和 Recovery；Pi 更适合说明 durable Harness、operation state 和副作用恢复；AgentDock 是外层多租户 Control Plane，负责 Agent 实例、容器、Driver、Task、资源和事件流；OpenViking 则负责 Memory、Resource、Skill 的可检索 Context。真正订单、退款、设备、工单状态仍由 Java 业务服务和数据库负责。这个分层的关键是确定事实 owner：模型做概率决策，Runtime 约束执行，平台管生命周期，Context 系统提供信息，业务系统保存最终事实。这样换模型、换 Runtime、做多租户或进程恢复时，系统不会因为职责混在一起而失控。

## 源码/项目落点

- nanobot：`nanobot/agent/runner.py`、`nanobot/agent/tools/execution.py`、`nanobot/security/workspace_access.py`、`nanobot/session/recovery.py`
- Pi：`packages/agent/src/agent.ts`、`packages/agent/docs/harness.md`
- AgentDock：根 README 的 Architecture / Drivers / Multi-tenant / Sandbox / Tasks
- OpenViking：根 README 的 Context Database、L0/L1/L2、recursive retrieval、session memory
