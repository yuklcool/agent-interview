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
├── 08-java-engineering/                 # Spring、线程池、Redis、WebSocket、OTel
├── 09-model-training/                   # SFT、Router、量化、推理模型
├── 10-code-agent/                       # Code Agent、AST/LSP、测试生成
├── 11-project-productization/           # 项目拷打、Demo→Production、多租户平台
├── 12-interview-strategy/               # 高频题、不同轮次、表达策略
└── interview-index/                     # 复习路线与索引
```

## 已升级为源码级 Deep Dive 的核心题

### Agent Runtime

- [Agent Loop 深挖：一次用户消息到底如何经过 Context、Tool、Checkpoint 与停止条件](01-agent-runtime/agent-loop-deep-dive.md)
- [Parallel Tool Calling：并行工具调用、依赖链与超时调度](01-agent-runtime/parallel-tool-calling.md)

### Planning / Routing

- [Model Routing 深挖：简单/复杂问题如何分流，并在运行时动态升级](02-planning-routing-multi-agent/model-routing-deep-dive.md)

### Tool Runtime

- [Tool Schema 与 Tool Runtime 深挖：为什么 JSON Schema 正确仍然可能执行错](03-tools-mcp/tool-schema-runtime-deep-dive.md)

### Reliability

- [nanobot Recovery 深挖：Checkpoint、UNKNOWN Tool 与副作用一致性](04-reliability-security/nanobot-recovery-deep-dive.md)

### Context Engineering

- [Context Engineering 深挖：Durable Transcript、Model-facing Context 与动态压缩](05-context-memory/context-engineering-deep-dive.md)

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

然后再回到 `chapter.md` 做题目覆盖。

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

后续维护规则：新题先语义去重；重复题优先深化现有文章，不新增同义文件；核心题逐步从 `chapter.md` 升级成独立 Deep Dive。
