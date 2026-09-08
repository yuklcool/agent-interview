# AI Agent Interview Knowledge Base

> 面向 AI Agent / Java Backend / Agent Runtime / RAG / Multi-Agent / Harness 工程化面试的深度知识库。

这个仓库不是简单的“题目 + 标准答案”集合，而是把每一道题整理成可学习、可追问、可结合真实工程实践回答的技术专题。

## 整理原则

每个重点问题尽量按以下结构展开：

1. **面试官真正考什么**
2. **核心结论**
3. **底层原理与运行机制**
4. **实际执行链路 / 状态机 / 数据结构**
5. **结合 nanobot 当前真实实现**
6. **nanobot 当前没有实现什么**
7. **企业级 Java / Spring / Agent 平台怎么补**
8. **失败场景、边界条件与 Trade-off**
9. **常见追问**
10. **1～2 分钟面试口述版**

> 原则：不把通用 Agent 最佳实践冒充成 nanobot 已实现能力；模型负责概率性决策，Runtime/Harness 负责约束执行，业务系统负责最终事实和副作用一致性。

## 知识体系

```text
agent-interview/
├── 01-agent-runtime/          # Agent Loop、ReAct、Plan-and-Execute、模型路由
├── 02-context-memory/         # Context Engineering、Session、Memory、Compaction
├── 03-tools-mcp/              # Tool Calling、JSON Schema、MCP、Structured Output
├── 04-reliability-security/   # Recovery、幂等、超时、UNKNOWN、HITL、安全
├── 05-rag-retrieval/          # Chunk、Hybrid Search、RRF、ReRank、Query Rewrite
├── 06-multi-agent/            # Planner / Worker / Reviewer、并发、状态共享
├── 07-harness-eval-trace/     # Harness、Eval、Golden Set、Replay、OpenTelemetry
├── 08-java-engineering/       # Spring Boot、线程池、Redis、WebSocket、数据库
├── 09-model-training/         # SFT、Prompt、Semantic Router、量化、Model Routing
├── 10-nanobot-source/         # nanobot 源码级实现与工程边界
└── interview-index/           # 高频题、第一面/二面/三面、复习路线
```

## 当前整理重点

- Agent Loop / Harness / Runtime
- Tool Calling / MCP / Tool Policy
- Context Engineering / Session / Recovery
- Parallel Tool Calling / DAG / Multi-Agent
- RAG / Text-to-SQL / Query Rewriting
- Trace / Eval / Tool Mock / Trajectory Replay
- Java / Spring Boot 中的 Agent 工程化
- nanobot 源码与企业级补强方案

## 学习方式

不要只背最后的“口述版”。建议按照：

```text
原理
  ↓
运行链路
  ↓
失败场景
  ↓
nanobot 源码
  ↓
企业级补强
  ↓
面试表达
```

逐层掌握。

---

后续题目会持续去重、分类、深化，并通过 Markdown + Mermaid 图维护。
