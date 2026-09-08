# AI Agent Interview Knowledge Base

> 面向 AI Agent / Java Backend / Agent Runtime / RAG / Multi-Agent / Harness 工程化面试的深度知识库。

这个仓库不再按“题目 + 几段标准答案”维护。现在改成两层：

```text
chapter.md
  └─ 负责题目全集、去重、索引、快速复习

*-deep-dive.md
  └─ 负责真正讲透核心题：源码、状态机、数据结构、失败路径、企业级补强
```

后续核心题以 **Deep Dive** 为权威版本；`chapter.md` 只作为题库入口，不再把几段概念性描述当最终答案。

## 先说明 01～07 当前状态

01～07 **不是完全没有深度整理**，但目前还没有做到“全集题目全部深度化”。准确状态是：

```text
01～07 chapter.md
= 去重后的全集题库 + 早期答案

01～07 *-deep-dive.md
= 已经完成源码级深挖的核心题
```

详细状态：

- [01～07 深度重构状态](docs/deep-rewrite-status-01-07.md)
- [Pi × nanobot × AgentDock × OpenViking 项目案例对照](docs/project-case-map.md)
- [Agent 核心 10 题去重索引：Pi × nanobot × AgentDock × OpenViking](docs/core-agent-10-questions-map.md)

## 深度标准

每个重点问题尽量回答到下面 10 层：

1. **面试官真正考什么**
2. **核心结论**
3. **底层原理与运行机制**
4. **实际执行链路 / 状态机 / 数据结构**
5. **真实开源项目当前如何实现**
6. **项目当前没有实现什么**
7. **企业级 Java / Spring / Agent 平台怎么补**
8. **失败场景、边界条件与 Trade-off**
9. **常见二次/三次追问**
10. **1～2 分钟面试口述版**

> 原则：不把通用 Agent 最佳实践冒充成某个项目已实现能力；模型负责概率性决策，Runtime/Harness 负责约束执行，业务系统负责最终事实和副作用一致性。

## 真实项目案例基线

后续 01～07 的深度回答优先结合以下四个真实项目：

```text
Pi
└─ Agent Runtime / Harness / Session / Operation State / Effect Recovery

nanobot
└─ AgentLoop / Runner / Context Governance / Tool Registry / Recovery / Injection

AgentDock
└─ Control Plane / Multi-tenant / Container / Driver / Task Event / MCP-Skill 分配

OpenViking
└─ Context Database / Memory / Resource / Skill / L0-L1-L2 / Retrieval Trajectory
```

不会机械地每题都写四个项目，而是按题目选最合适的案例：

- Tool Recovery：**Pi + nanobot**
- 多租户 / 多实例：**AgentDock**
- Context / Memory / Retrieval：**OpenViking + nanobot + Pi**
- Harness / Trace：**Pi + nanobot + AgentDock + OpenViking retrieval trajectory**
- Security：**nanobot Workspace/SSRF + Pi Sandbox 边界 + AgentDock Container/Egress**

## 当前目录

```text
agent-interview/
├── 01-agent-runtime/                    # Agent Loop、Workflow、ReAct、DAG
├── 02-planning-routing-multi-agent/     # Intent、Model Router、Planner/Worker/Reviewer
├── 03-tools-mcp/                        # Tool Calling、Schema、MCP、Tool Policy
├── 04-reliability-security/             # Recovery、幂等、UNKNOWN、HITL、安全
├── 05-context-memory/                   # Context、Session、Memory、Compaction
├── 06-rag-retrieval/                    # Chunk、Hybrid、RRF、ReRank、Text-to-SQL
├── 07-harness-eval-trace/               # Harness、Trace、Eval、Golden Set、Replay
├── 08-java-engineering/                 # Spring、线程池、Redis、WebSocket、数据库
├── 09-model-training/                   # SFT、LoRA、DPO/GRPO、MoE、KV Cache
├── 10-code-agent/                       # Code Agent、AST/LSP、测试生成、Sandbox
├── 11-project-productization/           # 项目拷打、Demo→Production、平台化
├── 12-interview-strategy/               # 公司偏好、学习方法、面试表达
└── docs/                                # 项目对照、重构状态、维护规则
```

## 已升级为独立 Deep Dive 的核心题

### 01 Agent Runtime

- [Agent Loop 深挖](01-agent-runtime/agent-loop-deep-dive.md)
- [Parallel Tool Calling：并行工具调用、依赖链与超时调度](01-agent-runtime/parallel-tool-calling.md)
- [Runtime、Control Plane、Context Database 与业务事实边界](01-agent-runtime/runtime-platform-context-boundaries-deep-dive.md)

### 02 Planning / Routing / Multi-Agent

- [Model Routing 深挖](02-planning-routing-multi-agent/model-routing-deep-dive.md)
- [ReAct、Plan-and-Execute、DAG 深挖](02-planning-routing-multi-agent/react-plan-dag-deep-dive.md)
- [Multi-Agent State Sharing：Planner/Worker/Reviewer、Artifact、Replan](02-planning-routing-multi-agent/multi-agent-state-sharing-deep-dive.md)

### 03 Tool / MCP

- [Tool Schema 与 Tool Runtime 深挖](03-tools-mcp/tool-schema-runtime-deep-dive.md)
- [MCP Runtime 深挖](03-tools-mcp/mcp-runtime-deep-dive.md)
- [Tool Permission / Policy：RBAC、Scope、Sandbox、业务授权](03-tools-mcp/tool-permission-policy-deep-dive.md)

### 04 Reliability / Security

- [nanobot Recovery 深挖](04-reliability-security/nanobot-recovery-deep-dive.md)
- [Tool Failure、幂等、UNKNOWN 深挖](04-reliability-security/tool-failure-idempotency-deep-dive.md)
- [Prompt Injection、Sandbox 与不可绕过安全边界](04-reliability-security/prompt-injection-sandbox-deep-dive.md)

### 05 Context / Memory

- [Context Engineering 深挖](05-context-memory/context-engineering-deep-dive.md)
- [Session、Memory、Runtime State 与业务 State 的边界](05-context-memory/memory-session-state-deep-dive.md)

### 06 RAG / Retrieval

- [Text-to-SQL 深挖：300+ 表、复杂 JOIN、权限和性能](06-rag-retrieval/text-to-sql-deep-dive.md)
- [Hybrid Search、RRF、ReRank 与 OpenViking Context Database](06-rag-retrieval/hybrid-search-rerank-context-db-deep-dive.md)

### 07 Harness / Eval / Trace

- [Agent Eval + Trace + Replay 深挖](07-harness-eval-trace/eval-trace-deep-dive.md)
- [Harness 到底是什么：Pi、nanobot、AgentDock、OpenViking 对照](07-harness-eval-trace/harness-runtime-comparison-deep-dive.md)

### 08 Java / Spring

- [Java / Spring / 并发与平台工程主章节](08-java-engineering/chapter.md)
- [Agent Streaming / WebSocket 协议深挖](08-java-engineering/streaming-websocket-deep-dive.md)

### 09 模型 / 训练

- [模型、训练、路由与推理优化主章节](09-model-training/chapter.md)

### 10 Code Agent

- [AI Coding / Code Agent / 自动测试主章节](10-code-agent/chapter.md)

### 11 项目 / 产品化

- [项目拷打、业务落地与产品化](11-project-productization/chapter.md)

### 12 面试表达

- [公司偏好与面试表达策略](12-interview-strategy/chapter.md)

## 推荐学习主线

不要从头背题，先把下面这条运行链打通：

```text
Runtime / Platform Boundary
   ↓
Agent Loop
   ↓
Context / Session / Memory
   ↓
Tool Runtime / MCP / Permission
   ↓
Recovery / UNKNOWN / Sandbox
   ↓
Planning / Multi-Agent / Replan
   ↓
RAG / Hybrid / Text-to-SQL
   ↓
Harness / Trace / Eval
   ↓
Java / Spring 工程化
```

然后再回到各章 `chapter.md` 做覆盖。

## 回答质量检查

如果一道题只回答了：

```text
“是什么”
“优点是什么”
“可以用某框架实现”
```

就还不够。

真正需要继续追问到：

```text
状态放哪？
谁能改状态？
失败后收敛到什么状态？
外部副作用如何确认？
旧异步结果如何识别？
Context 超限在哪里处理？
Runtime 如何做硬约束？
如何 Trace 和 Replay？
如何证明这个方案真的更好？
真实项目为什么这样设计？
```

---

后续维护规则：新题先语义去重；重复题优先深化现有文章；核心题逐步从 `chapter.md` 升级为独立 Deep Dive。01～07 在核心题都能指向深度正文之前，不标记“已全部深度完成”。
