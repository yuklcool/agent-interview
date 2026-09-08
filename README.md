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

## 深度标准

每个重点问题尽量回答到下面 10 层：

1. **面试官真正考什么**
2. **核心结论**
3. **底层原理与运行机制**
4. **实际执行链路 / 状态机 / 数据结构**
5. **结合 nanobot 当前真实实现与源码文件**
6. **nanobot 当前没有实现什么**
7. **企业级 Java / Spring / Agent 平台怎么补**
8. **失败场景、边界条件与 Trade-off**
9. **常见二次/三次追问**
10. **1～2 分钟面试口述版**

> 原则：不把通用 Agent 最佳实践冒充成 nanobot 已实现能力；模型负责概率性决策，Runtime/Harness 负责约束执行，业务系统负责最终事实和副作用一致性。

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
└── 12-interview-strategy/               # 公司偏好、学习方法、面试表达
```

## 已经迁入并维护的主章节

目前 01～12 主章节已经全部进入仓库维护。其中 01～07 保留原始全集题库 `chapter.md`，08～12 已按新的更深标准重新整理，不再只做提纲式迁移。

## 已升级为独立 Deep Dive 的核心题

### 01 Agent Runtime

- [Agent Loop 深挖](01-agent-runtime/agent-loop-deep-dive.md)
- [Parallel Tool Calling：并行工具调用、依赖链与超时调度](01-agent-runtime/parallel-tool-calling.md)

### 02 Planning / Routing / Multi-Agent

- [Model Routing 深挖](02-planning-routing-multi-agent/model-routing-deep-dive.md)
- [ReAct、Plan-and-Execute、DAG 深挖](02-planning-routing-multi-agent/react-plan-dag-deep-dive.md)

### 03 Tool / MCP

- [Tool Schema 与 Tool Runtime 深挖](03-tools-mcp/tool-schema-runtime-deep-dive.md)
- [MCP Runtime 深挖](03-tools-mcp/mcp-runtime-deep-dive.md)

### 04 Reliability / Security

- [nanobot Recovery 深挖](04-reliability-security/nanobot-recovery-deep-dive.md)
- [Tool Failure、幂等、UNKNOWN 深挖](04-reliability-security/tool-failure-idempotency-deep-dive.md)

### 05 Context / Memory

- [Context Engineering 深挖](05-context-memory/context-engineering-deep-dive.md)

### 06 RAG / Text-to-SQL

- [Text-to-SQL 深挖：300+ 表、复杂 JOIN、权限和性能](06-rag-retrieval/text-to-sql-deep-dive.md)

### 07 Harness / Eval / Trace

- [Agent Eval + Trace + Replay 深挖](07-harness-eval-trace/eval-trace-deep-dive.md)

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

## 学习顺序

建议不要从头背 159 题，先把下面这条主链打通：

```text
Agent Loop
   ↓
Context Engineering
   ↓
Tool Runtime / MCP
   ↓
Recovery / 幂等 / UNKNOWN
   ↓
Planning / Model Routing / Multi-Agent
   ↓
RAG / Text-to-SQL
   ↓
Harness / Trace / Eval
   ↓
Java / Spring 工程化
```

然后再回到各章 `chapter.md` 做题目覆盖。

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
```

这些问题能回答清楚，才算真正掌握。

---

后续维护规则：新题先语义去重；重复题优先深化现有文章，不新增同义文件；核心题逐步从 `chapter.md` 升级成独立 Deep Dive。下一批优先深化 Multi-Agent State Sharing、Memory/Session、Hybrid Search/ReRank、Spring Agent 集成、Sandbox 和 Tool Permission。
