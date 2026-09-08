# Agent 核心 10 题去重索引：Pi × nanobot × AgentDock × OpenViking

> 来源：一组围绕 Agent、Loop、Tool、Security、Context、Memory、RAG、Multi-Agent 与系统设计的 10 道高频面试题。
>
> 本页的目标不是再复制一套答案，而是做**语义去重 + 权威入口映射 + 项目案例选择**。仓库里已有的 Deep Dive 继续作为权威正文；重复题只做索引，不再新建同义文章。

---

## 一、先看结论：10 道题实际上只覆盖 7 个核心能力域

```text
1. Agent 本质 / 系统边界
      ↓
2. Agent Loop / Tool Loop
      ↓
3. Tool 执行 / 并行与依赖
      ↓
4. Permission / Sandbox / Security
      ↓
5. Context / Session / Memory
      ↓
6. RAG / Retrieval / Context Database
      ↓
7. Multi-Agent / Platform / Production Design
```

所以不应该为 10 个不同问法各维护一篇内容高度重叠的答案，而应该把它们归并到现有章节与 Deep Dive。

---

## 二、10 道原题与去重后的权威入口

| # | 原题 | 归并后的主题 | 权威正文 | 最适合结合的项目 | 去重结论 |
|---|---|---|---|---|---|
| 1 | 你如何理解 Agent？相比传统应用具备哪些核心能力？ | Agent 本质、Runtime 与传统应用边界 | [Agent Runtime 主章节](../01-agent-runtime/chapter.md)、[Runtime / Platform / Context Database 边界](../01-agent-runtime/runtime-platform-context-boundaries-deep-dive.md) | nanobot + Pi + AgentDock | 不新增同义 Deep Dive |
| 2 | 描述一下最简单的 Agent Loop 是什么样子？ | Agent Loop 最小闭环 | [Agent Loop 深挖](../01-agent-runtime/agent-loop-deep-dive.md) | Pi + nanobot | 已有权威正文 |
| 3 | Agent Loop 中需要调用多个工具时如何循环交互？ | Tool Call → Tool Result → 下一轮 LLM；并行/串行/依赖 | [Agent Loop 深挖](../01-agent-runtime/agent-loop-deep-dive.md)、[Parallel Tool Calling](../01-agent-runtime/parallel-tool-calling.md) | Pi + nanobot | 合并到 Loop / Parallel Tool Calling |
| 4 | Agent 的权限控制怎么做？如何约束高风险操作？ | Tool Policy、RBAC、Workspace、Sandbox、HITL | [Tool Permission / Policy](../03-tools-mcp/tool-permission-policy-deep-dive.md)、[Prompt Injection / Sandbox](../04-reliability-security/prompt-injection-sandbox-deep-dive.md) | AgentDock + nanobot + Pi | 不再单独维护“权限控制”重复答案 |
| 5 | Agent 运行过程中上下文如何管理？如何避免过长？ | Durable Transcript、Model-facing Context、Compaction | [Context Engineering 深挖](../05-context-memory/context-engineering-deep-dive.md)、[Session / Memory / State](../05-context-memory/memory-session-state-deep-dive.md) | nanobot + Pi + OpenViking | 合并到 Context / Memory |
| 6 | 短期 Memory 和长期 Memory 怎么设计？分别解决什么问题？ | Session、Working Memory、Long-term Memory | [Session / Memory / State](../05-context-memory/memory-session-state-deep-dive.md) | nanobot + OpenViking + Pi | 已覆盖 |
| 7 | 历史记忆如何淘汰？长期记忆冲突怎么办？ | Memory Admission、TTL、Version、Source、Supersede | [Session / Memory / State](../05-context-memory/memory-session-state-deep-dive.md) | OpenViking + nanobot | 已覆盖 Memory 冲突与压缩，不新增同义文章 |
| 8 | RAG 完整流程是什么？文档切分、向量检索、召回、生成怎么串起来？ | Chunking、Hybrid Retrieval、RRF、ReRank、Context Assembly | [RAG / Retrieval 主章节](../06-rag-retrieval/chapter.md)、[Hybrid Search / RRF / ReRank / Context Database](../06-rag-retrieval/hybrid-search-rerank-context-db-deep-dive.md) | OpenViking + 城市照明 Text-to-SQL | 已有权威正文 |
| 9 | 多个 Agent 协同时如何任务分配、状态管理、结果整合？ | Planner/Worker/Reviewer、Artifact、Task State、Merge/Replan | [Multi-Agent State Sharing](../02-planning-routing-multi-agent/multi-agent-state-sharing-deep-dive.md)、[ReAct / Plan / DAG](../02-planning-routing-multi-agent/react-plan-dag-deep-dive.md) | AgentDock + nanobot + Pi | 合并到 Multi-Agent / DAG |
| 10 | 从零设计一个 Agent 应用，会从哪些方面整体规划？ | Capability Boundary、Runtime、Tool、Context、Memory、Security、Platform、Eval | [Runtime / Platform / Context Database 边界](../01-agent-runtime/runtime-platform-context-boundaries-deep-dive.md)、[项目与产品化](../11-project-productization/chapter.md) | 四个项目组合 | 作为综合题，不新建重复技术正文 |

---

# 三、每题面试时应该抓住什么

下面只给“答题主线”，细节统一回到上面的权威正文。

## 1. Agent 和传统应用的区别

最重要的不是说“Agent 会调用工具”，而是讲清：

```text
传统应用
程序员预先决定控制流

Agent
程序员定义能力与边界
模型在运行时决定部分执行路径
Runtime 负责真正执行与约束
```

一句话版：

> Agent 是一个由模型参与运行时决策、由 Runtime 持有状态并执行工具、由业务系统和安全边界约束副作用的闭环执行系统。

项目案例优先级：

```text
Pi       → 最小 Harness / Runtime 思想
nanobot  → AgentLoop / Runner / Session / Tool
AgentDock→ Runtime 外的平台层
OpenViking→ Context Database，不是 Agent Loop 本身
```

---

## 2. 最简单的 Agent Loop

核心闭环：

```text
User
 ↓
LLM
 ↓
tool_call ? ── no ──→ Final
 ↓ yes
Tool
 ↓
Tool Result / Observation
 ↓
LLM
```

面试一定补一句：

> Tool Call 不是执行本身，模型只是提出动作；Runtime 校验、执行并把 Tool Result 回注模型。

源码案例优先：**Pi + nanobot**。

---

## 3. 多工具如何循环

先判断依赖：

```text
无依赖
→ parallel

有数据依赖 / 副作用顺序
→ sequential
```

还要讲清：

```text
assistant tool_call
   ↓
Schema / Policy Validation
   ↓
Tool Execution
   ↓
tool_call_id 对应 Tool Result
   ↓
回注 Context
   ↓
下一轮 LLM
```

这道题不要再和“Agent Loop 是什么”拆成两套重复答案；它是 Agent Loop 的 Tool Execution 子问题。

---

## 4. 权限与高风险操作

不要把 Prompt 当安全边界。

推荐回答结构：

```text
LLM
 ↓
Tool Schema
 ↓
Tool Policy / RBAC / Scope
 ↓
Business Authorization
 ↓
HITL（高风险动作）
 ↓
Sandbox / Container
 ↓
Network / DB Permission
 ↓
Real System
```

案例：

- **Pi**：适合说明 Runtime 默认权限与 Sandbox 是两层；
- **nanobot**：Workspace / Shell / SSRF / Tool 边界；
- **AgentDock**：Container、Tenant、Credential、Egress、CPU/Memory 限制。

---

## 5. Context 如何避免越跑越长

必须区分：

```text
Durable Transcript
= 完整事实与审计历史

Model-facing Context
= 当前一轮真正发给模型的投影
```

典型 Context：

```text
System
+ Session Summary
+ Long-term Memory
+ Retrieved Context
+ Recent Messages
+ Current User Message
+ Tool Schemas
```

旧历史可以被 Compaction / Summary，但不要把“模型视图压缩”误解成“删除原始事实”。

---

## 6. 短期 Memory 与长期 Memory

不要只用“Redis 是短期、向量库是长期”回答。

更准确：

```text
Working / Runtime State
→ 当前 run、iteration、tool、checkpoint

Session Memory
→ 当前 Conversation 的近期状态

Long-term Memory
→ 跨 Session 可复用的稳定偏好、长期背景、经验
```

存储介质不是概念边界，**语义、生命周期和 owner 才是**。

---

## 7. Memory 淘汰和冲突

需要至少考虑：

```text
recency
importance
frequency
confidence
source
TTL / valid_from / valid_to
supersedes
```

冲突不能只靠“最新一条 embedding 更相似”。建议区分：

```text
user stated
system observed
agent inferred
```

通常明确用户声明和业务事实优先于 Agent 推断。

这部分已经归并进 `memory-session-state-deep-dive.md`，不再单独新建重复文章。

---

## 8. RAG 完整链

建议按两阶段讲：

```text
离线：
Document
 → Parse / Clean
 → Structure-aware Chunk
 → Metadata
 → Embedding / Index

在线：
Query
 → Rewrite / Filter
 → BM25 + Dense
 → Fusion / RRF
 → ReRank
 → Parent / Directory Expansion
 → Context Assembly
 → LLM Generation
```

OpenViking 的价值不是“换一个向量数据库”，而是把：

```text
Memory / Resource / Skill
```

统一到 Context Database，并通过 L0/L1/L2 做分层加载与可观察 Retrieval Trajectory。

---

## 9. Multi-Agent 协作

真正难点不是“创建多个 Agent”，而是：

```text
Task Decomposition
+ State Ownership
+ Artifact Contract
+ Dependency
+ Retry / Replan
+ Stale Result
+ Final Merge
```

外部状态机/数据库应该是事实源，不能让多个 Agent 靠自然语言互相猜“谁已经完成”。

项目案例：

- **AgentDock**：多实例、Workflow、Task/Event、平台生命周期；
- **nanobot / Pi**：单 Runtime 内执行和状态机制；
- 多 Agent 不是目的，能用单 Agent + Tool + DAG 解决时不要强行拆 Agent。

---

## 10. 从零设计 Agent 应用

建议不要从“选哪个模型”开始，而按以下顺序：

```text
1. Capability Boundary
2. Business Truth / Side Effect Boundary
3. Tool Contract
4. Agent Loop / Runtime
5. Context / Session
6. Memory / Retrieval
7. Permission / Sandbox / HITL
8. Recovery / Idempotency / UNKNOWN
9. Multi-user / Container / Credential / Quota
10. Trace / Eval / Replay
```

四个项目可以组成一套非常清晰的分层案例：

```text
AgentDock
→ Control Plane / Multi-tenant / Container / API

nanobot
→ Agent Runtime / Loop / Tool / Session / MCP

Pi
→ Harness / Runtime State / Tool Effect / Recovery 思想

OpenViking
→ Long-term Context / Memory / Resource / Retrieval
```

---

# 四、推荐复习顺序

这 10 题不要按题号死背，建议按真实运行链复习：

```text
Agent 是什么
   ↓
Agent Loop
   ↓
Tool Calling / Parallel Tool
   ↓
Permission / Sandbox
   ↓
Context / Session / Memory
   ↓
RAG / OpenViking
   ↓
Multi-Agent / Workflow
   ↓
AgentDock 平台化
   ↓
从零系统设计
```

对应仓库主线：

1. [Agent Loop 深挖](../01-agent-runtime/agent-loop-deep-dive.md)
2. [Parallel Tool Calling](../01-agent-runtime/parallel-tool-calling.md)
3. [Tool Permission / Policy](../03-tools-mcp/tool-permission-policy-deep-dive.md)
4. [Context Engineering](../05-context-memory/context-engineering-deep-dive.md)
5. [Session / Memory / State](../05-context-memory/memory-session-state-deep-dive.md)
6. [Hybrid Search / OpenViking](../06-rag-retrieval/hybrid-search-rerank-context-db-deep-dive.md)
7. [Multi-Agent State Sharing](../02-planning-routing-multi-agent/multi-agent-state-sharing-deep-dive.md)
8. [Runtime / Platform / Context Database 边界](../01-agent-runtime/runtime-platform-context-boundaries-deep-dive.md)
9. [项目与产品化](../11-project-productization/chapter.md)

---

# 五、维护规则

后续如果再遇到相似题目，例如：

```text
“Agent 和 Workflow 有什么区别？”
“Agent 为什么需要 Loop？”
“Tool Result 为什么要再发给模型？”
“历史消息怎么压缩？”
“Memory 冲突怎么办？”
“多个 Agent 怎么共享状态？”
```

先在上述权威主题里做**语义归并**。

只有满足下面任一条件才新建 Deep Dive：

- 出现新的底层机制；
- 出现新的状态模型；
- 出现新的失败恢复路径；
- 出现值得独立展开的真实源码实现；
- 现有文章无法在不破坏主题聚焦的情况下容纳。

否则优先深化现有文章，避免仓库重新退化成“同一道题换十种问法、维护十份答案”。
