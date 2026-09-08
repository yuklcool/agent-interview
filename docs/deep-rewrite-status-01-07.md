# 01～07 深度重构完成报告

> 状态：**COMPLETE**。01～07 原有 104 道核心题已经全部完成全量深度重构。

原来的 `chapter.md` / `part-*.md` 继续保留作为题目全集、历史版本和快速复习入口；每章新的 `deep-complete.md` 作为当前权威学习版本。已有的单专题 `*-deep-dive.md` 继续保留，用于对少数重点问题做更细的源码级展开。

## 完成度

| 章节 | 题数 | 状态 | 权威深度版 |
|---|---:|---|---|
| 01 Agent Runtime / Loop / 系统边界 | 16 | ✅ 16/16 | [deep-complete.md](../01-agent-runtime/deep-complete.md) |
| 02 Planning / Routing / Multi-Agent | 14 | ✅ 14/14 | [deep-complete.md](../02-planning-routing-multi-agent/deep-complete.md) |
| 03 Tool / Function Calling / MCP / Skills | 17 | ✅ 17/17 | [deep-complete.md](../03-tools-mcp/deep-complete.md) |
| 04 Reliability / Security / Recovery | 12 | ✅ 12/12 | [deep-complete.md](../04-reliability-security/deep-complete.md) |
| 05 Context / Memory / Session / State | 11 | ✅ 11/11 | [deep-complete.md](../05-context-memory/deep-complete.md) |
| 06 RAG / Retrieval / Knowledge Base | 17 | ✅ 17/17 | [deep-complete.md](../06-rag-retrieval/deep-complete.md) |
| 07 Harness / Eval / Trace | 17 | ✅ 17/17 | [deep-complete.md](../07-harness-eval-trace/deep-complete.md) |
| **合计** | **104** | **✅ 104/104** | |

## 这次“完成”指什么

不是把旧答案简单扩写，而是把每章重新按工程主线组织。重点问题已经从“概念解释”推进到以下层次：

```text
问题的工程本质
      ↓
核心设计判断
      ↓
真实运行链路
      ↓
State / ID / Version / Status
      ↓
失败路径与收敛状态
      ↓
真实项目实现对照
      ↓
项目当前能力 vs 企业扩展
      ↓
Java / Spring / Domain Service 落地
      ↓
权限 / 恢复 / 并发 / 成本 / Trace / Eval
      ↓
二面、三面继续追问
```

## 四个项目在 01～07 中的角色

### Pi

主要用于解释：

- Agent Runtime 与 Harness 的区别；
- Session / Branch / AgentLane；
- durable operation state；
- effect intent → uncertain effect → settlement；
- replay policy；
- crash recovery；
- 为什么 Harness 不能承诺外部 exactly-once。

重点章节：01、04、05、07。

### nanobot

主要用于解释当前真实轻量 Runtime：

- `AgentLoop` / `AgentRunner` / `AgentRunSpec`；
- `ContextGovernor`；
- `ToolRegistry` / `execute_tool_calls`；
- `concurrency_safe` 与并发 Tool batch；
- `SubagentManager`；
- user injection；
- runtime checkpoint / recovery；
- workspace scope / SSRF boundary；
- `AgentHook` instrumentation seam。

重点章节：01～05、07。

### AgentDock

主要用于解释 Runtime 上层的平台能力：

- tenant / workspace；
- agent/container 生命周期；
- driver registry；
- task / event stream；
- persistent workspace；
- MCP / Skill assignment；
- credentials；
- Docker resource isolation；
- egress proxy；
- snapshot / recovery；
- 多 Runtime 的统一 Control Plane。

重点章节：01～04、07。

### OpenViking

主要用于解释 Context / Memory / Retrieval：

- `viking://`；
- Resource / Memory / Skill；
- L0 Abstract / L1 Overview / L2 Detail；
- directory recursive retrieval；
- retrieval trajectory；
- Session → long-term memory；
- Progressive Disclosure；
- Context Database 与传统平面向量库的差别。

重点章节：03、05、06、07。

## 各章已经解决的核心深度问题

### 01 Agent Runtime

已经覆盖 Model ≠ Agent、Agent Loop、CoT/ReAct/ToT、Agent vs Workflow、Planner/Executor contract、Plan 震荡、停止条件、带环 Graph、Harness vs Model Training、Control Plane / Runtime / Context / Business State 分层。

### 02 Planning / Multi-Agent

已经覆盖混合 Intent Router、最小澄清、任务依赖图、ReAct + Plan-and-Execute 混合、Router/Planner/Worker/Reviewer 边界、required/optional Worker、plan_version、用户中途改口、Model Routing、Subagent 拆分、Handoff contract、死循环防护、MCP vs A2A、Shared State / Artifact / Event 通信。

### 03 Tool / MCP / Skill

已经覆盖 JSON Schema、业务语义校验、Tool 可见性 vs 执行权限、MCP 迁移、参数自动修复、100+ Tool Retrieval、Progressive Disclosure、HTTP 200 但业务失败、Canonical ToolResult、MCP Host/Client/Server、CLI/REST/MCP 选择、Execution Graph、Rule/Skill/Tool 边界、Skill Registry、Function Calling SFT 前的工程优化。

### 04 Reliability / Security

已经覆盖业务 UNKNOWN、nanobot/Pi recovery 对照、Retry ownership、precondition、删除/退款等高风险防护、Prompt Injection、Workspace/Sandbox/SSRF、Tool Failure taxonomy、Reflection no-progress、预算继承、NL2SQL 七层安全、HITL action hash、全链路 hallucination taxonomy。

### 05 Context / Memory / Session

已经彻底区分 Durable Transcript、Runtime State、Long-term Memory、Model-facing Context、Business State，并覆盖 compaction、跨 Agent handoff、关键约束、防摘要失真、Rolling/Segment Summary、Memory Admission、Memory Retrieval Gate、Topic Switch、Memory Conflict、Memory Hallucination。

### 06 RAG / Retrieval

已经覆盖结构化 Chunk、Hybrid Search、RRF、ReRank 指标、知识版本热更新、Embedding 选型/迁移、企业 ingestion pipeline、Query Rewrite、Parent-Child、GraphRAG、多向量数据库选型、HNSW/IVF、ES vs Dense、多模态 PDF/Table/Layout、RAG bad-case 排查、retrieval loop stop、多模态语义融合，以及原有 Text-to-SQL 深挖。

### 07 Harness / Eval / Trace

已经覆盖 Harness responsibilities、W3C Trace、Golden Dataset、Hard Guardrail vs Optimization Metric、Multi-Agent failure attribution、Tool Mock / Trajectory Replay、RAG A/B、Agent decision quality metrics、Memory Eval、E2E funnel、Tool accuracy decomposition、线上样本分层、业务因果实验、failure taxonomy、版本发布门禁、Prompt/Context/Harness 分层和 Eval-driven 开发闭环。

## 保留的专项 Deep Dive

`deep-complete.md` 解决全量覆盖；已有专项文档继续承担更细的源码级学习：

```text
01: Agent Loop / Parallel Tool Calling / Runtime Boundary
02: Model Routing / ReAct-Plan-DAG / Multi-Agent State Sharing
03: Tool Schema Runtime / MCP Runtime / Tool Permission
04: nanobot Recovery / Idempotency-UNKNOWN / Prompt Injection-Sandbox
05: Context Engineering / Memory-Session-State
06: Text-to-SQL / Hybrid-RRF-ReRank-OpenViking
07: Eval-Trace-Replay / Harness Runtime Comparison
```

## 完成后的学习方式

建议优先学习：

```text
01 Agent Runtime
      ↓
05 Context / Memory / State
      ↓
03 Tool / MCP / Policy
      ↓
04 Recovery / Security / Idempotency
      ↓
02 Planning / Multi-Agent
      ↓
06 RAG / Retrieval
      ↓
07 Harness / Eval / Trace
```

不要背结论。每道题至少要能继续回答：

```text
状态到底放哪？
谁拥有写权限？
模型只有提议权还是执行权？
崩溃在哪个窗口最危险？
副作用超时为什么是 UNKNOWN？
旧异步结果怎么识别？
为什么不能只靠 Prompt？
这个项目现在真的实现了吗？
如果没实现，企业平台在哪层补？
如何 Trace、Replay、Eval？
```

能够沿这些问题继续展开，才算真正掌握。

---

**状态结论：01～07 的原始未完成块已经从“部分 Deep Dive”升级为 `104/104 Deep Complete`。后续维护进入“新增题先去重、已有题持续用源码变化校正”的阶段。**
