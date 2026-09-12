# AI Agent Interview Knowledge Base

> 面向 AI Agent / Java Backend / Agent Runtime / RAG / Multi-Agent / Harness 工程化面试的深度知识库。

这不是“题目 + 标准答案”题库，而是一套以 **运行机制、状态机、源码、失败路径、真实项目和企业落地** 为核心的 Agent Engineering 学习手册。

## 最新补充

- [2026 Agent 面试补充：Agent 架构 vs Chain、ReAct、Long-term Memory](docs/supplement-2026-agent-core-concepts-01.md)
- [2026 Agent 面试补充：Multi-Agent Systems（协作模式、无限循环、通信冗余）](02-planning-routing-multi-agent/supplement-mas-2026.md)
- [2026 Agent 面试补充：Workflows vs Autonomous Agents、Orchestrator-Workers、Reflection](docs/supplement-2026-agent-design-patterns-02.md)
- [2026 Agent 面试补充：Java/Spring、Redis、MySQL 索引、意图识别、RAG、向量库、Tool Calling](docs/supplement-2026-java-backend-rag-tooling.md)

这些补充题来自最新截图题库，但不会因为问法不同就重复增加核心题号；先与现有 01～08 章节做语义去重，再作为高频追问入口补充深度答案。

## 当前完成状态

### 01～07：已完成全量深度重构

原来的 `chapter.md` / `part-*.md` 继续保留，主要用于题目索引和快速复习；每章新的 **`deep-complete.md`** 是权威学习版本，已经覆盖原章节全部题目：

| 章节 | 题数 | 权威深度版 |
|---|---:|---|
| 01 Agent Runtime / Loop | 16 | [deep-complete.md](01-agent-runtime/deep-complete.md) |
| 02 Planning / Routing / Multi-Agent | 14 | [deep-complete.md](02-planning-routing-multi-agent/deep-complete.md) |
| 03 Tool / Function Calling / MCP / Skills | 17 | [deep-complete.md](03-tools-mcp/deep-complete.md) |
| 04 Reliability / Security / Recovery | 12 | [deep-complete.md](04-reliability-security/deep-complete.md) |
| 05 Context / Memory / Session | 11 | [deep-complete.md](05-context-memory/deep-complete.md) |
| 06 RAG / Retrieval | 17 | [deep-complete.md](06-rag-retrieval/deep-complete.md) |
| 07 Harness / Eval / Trace | 17 | [deep-complete.md](07-harness-eval-trace/deep-complete.md) |

**01～07 共 104 道核心题，已经全部进入 Deep Complete。**

详细覆盖状态见：[01～07 深度完成报告](docs/deep-rewrite-status-01-07.md)。

### 08～12

08～12 已按更深工程标准整理，继续作为后续补题和专项深化区域：

- [08 Java / Spring / 并发与平台工程](08-java-engineering/chapter.md)
- [09 模型、训练、路由与推理优化](09-model-training/chapter.md)
- [10 AI Coding / Code Agent / 自动测试](10-code-agent/chapter.md)
- [11 项目拷打、业务落地与产品化](11-project-productization/chapter.md)
- [12 公司偏好与面试表达策略](12-interview-strategy/chapter.md)

## 深度标准

一道题如果只回答：

```text
是什么
优点是什么
可以用哪个框架
```

仍然不算完成。

Deep Complete 要尽量回答到：

1. **面试官真正考什么**；
2. **核心判断和设计边界**；
3. **底层运行机制**；
4. **执行链 / 状态机 / 数据结构**；
5. **失败路径与最终收敛状态**；
6. **真实项目当前怎么实现**；
7. **项目没有实现什么，不能把建议能力冒充成现状**；
8. **Java / Spring / 企业平台如何补强**；
9. **并发、恢复、权限、成本、可观测性 Trade-off**；
10. **二面/三面继续追问时还能展开**。

## 四个主要真实项目案例

后续答案优先从以下项目选择真正相关的实现做对照，而不是机械堆项目名。

### Pi

定位：**Agent Runtime / Harness / Durable Session / Operation State / Effect Recovery**。

重点：

```text
pi-agent-core
Session / Branch / AgentLane
operation state machine
effect intent / settlement
replay policy
recovery / abort
```

Pi 很适合回答“一个真正 durable 的 Agent Harness 应该怎么设计”。

### nanobot

定位：**轻量 Agent Runtime**。

重点：

```text
AgentLoop
AgentRunner / AgentRunSpec
ContextGovernor
ToolRegistry / execute_tool_calls
concurrency_safe
AgentHook
SubagentManager
Injection
Checkpoint / Recovery
Workspace / SSRF boundary
```

它适合用来解释一次 Tool-using Agent Loop 在代码里到底如何运行。

### AgentDock

定位：**Agent Control Plane / 多租户多实例平台**。

重点：

```text
Tenant / Workspace
Agent / Container
Driver Registry
Task / Event Stream
Persistent Workspace
MCP / Skill assignment
Credentials
Docker resource isolation
Egress proxy
Snapshot / Recovery
```

它解决的是“如何把 nanobot、Pi 等 Runtime 运营成一个可管理的平台”，而不是替代 Runtime 本身。

### OpenViking

定位：**Context Database for AI Agents**。

重点：

```text
viking://
Resource / Memory / Skill
L0 Abstract
L1 Overview
L2 Detail
Directory Recursive Retrieval
Retrieval Trajectory
Session → Long-term Memory
```

它适合回答 Context Engineering、Memory、RAG、Progressive Disclosure 和 Retrieval Observability。

## 一张图理解四者边界

```text
                         AgentDock
                    Control Plane / Platform
                tenant / instance / task / driver
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
          nanobot                         Pi
     lightweight Runtime            Runtime / Harness
 Loop / Context / Tool / Recovery   durable operation/effect
              │                           │
              └─────────────┬─────────────┘
                            ▼
                   MCP / Tool / Service
                            ▼
                 Java Domain / DB / API

                 Context / Memory plane
                            │
                            ▼
                       OpenViking
              Resource / Memory / Skill
                   L0 → L1 → L2
```

## 已保留的专项 Deep Dive

`deep-complete.md` 负责全量覆盖；下面这些文件继续作为重点专题的源码级加深材料：

- [Agent Loop 深挖](01-agent-runtime/agent-loop-deep-dive.md)
- [Parallel Tool Calling](01-agent-runtime/parallel-tool-calling.md)
- [Runtime / Control Plane / Context Database 边界](01-agent-runtime/runtime-platform-context-boundaries-deep-dive.md)
- [Model Routing](02-planning-routing-multi-agent/model-routing-deep-dive.md)
- [ReAct / Plan-and-Execute / DAG](02-planning-routing-multi-agent/react-plan-dag-deep-dive.md)
- [Multi-Agent State Sharing](02-planning-routing-multi-agent/multi-agent-state-sharing-deep-dive.md)
- [Tool Schema / Runtime](03-tools-mcp/tool-schema-runtime-deep-dive.md)
- [MCP Runtime](03-tools-mcp/mcp-runtime-deep-dive.md)
- [Tool Permission / Policy](03-tools-mcp/tool-permission-policy-deep-dive.md)
- [nanobot Recovery](04-reliability-security/nanobot-recovery-deep-dive.md)
- [Tool Failure / Idempotency / UNKNOWN](04-reliability-security/tool-failure-idempotency-deep-dive.md)
- [Prompt Injection / Sandbox](04-reliability-security/prompt-injection-sandbox-deep-dive.md)
- [Context Engineering](05-context-memory/context-engineering-deep-dive.md)
- [Session / Memory / State](05-context-memory/memory-session-state-deep-dive.md)
- [Text-to-SQL](06-rag-retrieval/text-to-sql-deep-dive.md)
- [Hybrid Search / RRF / ReRank / OpenViking](06-rag-retrieval/hybrid-search-rerank-context-db-deep-dive.md)
- [Eval / Trace / Replay](07-harness-eval-trace/eval-trace-deep-dive.md)
- [Harness Runtime 对照](07-harness-eval-trace/harness-runtime-comparison-deep-dive.md)

## 推荐学习顺序

```text
01 Agent Runtime / Loop
       ↓
05 Context / Memory / State
       ↓
03 Tool / MCP / Policy
       ↓
04 Recovery / Idempotency / Security
       ↓
02 Planning / Multi-Agent
       ↓
06 RAG / Retrieval
       ↓
07 Harness / Eval / Trace
       ↓
08 Java / Spring Engineering
```

然后再回到各章节做题目覆盖。

## 最重要的工程主线

> **模型负责概率性的理解、规划和候选动作；Runtime/Harness 负责硬约束、执行、恢复和观测；Context System 负责给模型正确的信息；业务系统负责最终事实和副作用一致性；Control Plane 负责多租户、多实例和资源生命周期。**

真正理解这条边界，Agent 面试就不会退化成背 Prompt、Function Calling 和框架 API。