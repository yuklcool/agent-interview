# 01～07 深度重构状态

> 结论：01～07 **不是完全没有深度整理**，而是“全集题库已迁入，核心题正在逐步升级成源码级 Deep Dive”。`chapter.md` 仍然保留去重全集和早期答案，但不再视为最终权威答案。

## 当前状态

| 章节 | 当前状态 | 已有 Deep Dive | 下一步继续补 |
|---|---|---|---|
| 01 Agent Runtime | 持续深化 | Agent Loop、Parallel Tool Calling、Runtime/Platform/Context Boundary | Stop/Iteration、Framework 选型、长任务 Run Lifecycle |
| 02 Planning / Routing / Multi-Agent | 持续深化 | Model Routing、ReAct/Plan/DAG、Multi-Agent State Sharing/Replan | Handoff、Planner/Reviewer 失败归因、复杂任务取消 |
| 03 Tools / MCP | 持续深化 | Tool Schema Runtime、MCP Runtime、Tool Permission/Policy | Tool Discovery、Skill、Progressive Disclosure、Structured Output |
| 04 Reliability / Security | 持续深化 | nanobot Recovery、Tool Failure/Idempotency、Prompt Injection/Sandbox | HITL、Secret、Risk Gate、业务补偿/Saga |
| 05 Context / Memory | 持续深化 | Context Engineering、Memory/Session/State | Memory Admission、Conflict、Topic Switch、Memory Eval |
| 06 RAG / Retrieval | 持续深化 | Text-to-SQL、Hybrid/RRF/ReRank/Context Database | Query Rewrite、Parent-Child、Graph/Relation Retrieval、RAG Eval |
| 07 Harness / Eval / Trace | 持续深化 | Eval/Trace/Replay、Harness Runtime Comparison | Golden Dataset、Tool Mock、A/B、Failure Attribution、Release Gate |

## 本轮已经补齐的核心薄弱点

这一轮不再只扩 `chapter.md`，而是新增了 7 个源码/架构级专题：

```text
01-agent-runtime/
└── runtime-platform-context-boundaries-deep-dive.md

02-planning-routing-multi-agent/
└── multi-agent-state-sharing-deep-dive.md

03-tools-mcp/
└── tool-permission-policy-deep-dive.md

04-reliability-security/
└── prompt-injection-sandbox-deep-dive.md

05-context-memory/
└── memory-session-state-deep-dive.md

06-rag-retrieval/
└── hybrid-search-rerank-context-db-deep-dive.md

07-harness-eval-trace/
└── harness-runtime-comparison-deep-dive.md
```

这些专题统一使用 **Pi × nanobot × AgentDock × OpenViking** 做真实项目对照，但不会机械地四个项目都写一遍，而是按职责选择案例：

- **Pi**：durable Harness、Session/Operation State、intent/effect/settlement、replay policy；
- **nanobot**：AgentRunner、Context Governance、Tool Execution、Subagent、Injection、Workspace Scope、Recovery；
- **AgentDock**：Control Plane、多租户、多实例容器、Driver、Task/Event、Sandbox/Egress；
- **OpenViking**：Context Database、Memory/Resource/Skill、L0/L1/L2、recursive retrieval、retrieval trajectory。

## 重构规则

以后 `chapter.md` 的作用固定为：

```text
题目全集
+ 去重后的快速答案
+ 指向 Deep Dive 的入口
```

真正的学习主文档由独立 Deep Dive 承担。

### 每道核心题最低完成标准

1. 给出问题的工程本质，而不是定义。
2. 画出真实执行链或状态机。
3. 定义关键数据结构和状态字段。
4. 解释异常路径和最终收敛状态。
5. 对照真实项目源码/架构。
6. 明确“项目已有能力”和“建议扩展能力”。
7. 讲 Trade-off，不写万能最佳实践。
8. 给 Java / Agent 平台落地方式。
9. 给二次、三次追问。
10. 最后才给 1～2 分钟口述版。

## 不再允许的答案模式

下面这种答案后续仍视为待重构：

```text
“RAG 是先检索再生成。”
“Agent 可以用 ReAct。”
“MCP 用来统一工具调用。”
“Redis 可以保存 Session。”
“Tool 失败可以 retry。”
“多 Agent 就是 Planner + Worker。”
“Prompt Injection 用 System Prompt 防。”
```

因为这些只描述名词，没有回答：状态归谁、失败如何恢复、权限谁控制、旧结果怎么识别、真实项目到底怎么实现。

## 合格答案示例：Tool Timeout

不应该只说：

```text
超时 → retry 3 次
```

而要继续追到：

```text
Tool 是 read-only 还是 side-effect？
        ↓
请求有没有到达下游？
        ↓
本地看到 TIMEOUT，但外部是否可能 SUCCESS？
        ↓
如果可能，则进入 UNKNOWN
        ↓
有无 business_request_id / idempotency_key？
        ↓
query_status / reconcile
        ↓
SUCCESS / NOT_FOUND / PROCESSING / UNKNOWN
```

并对照：

- Pi 的 effect intent / settlement / replay policy；
- nanobot 的 interrupted Tool recovery；
- AgentDock 的任务/容器/平台边界；
- Java 业务 Service 的 idempotency / authoritative state。

## 执行顺序

接下来继续按下面顺序重构：

```text
P0：把 01～07 高频主问题全部升级到 Deep Dive
P1：把 chapter.md 每个问题链接到对应 Deep Dive
P2：补 Java/Spring 伪代码、状态表、Mermaid 时序图
P3：加入“源码定位 + 真实项目对比 + 追问树”索引
```

在 `chapter.md` 的核心题都能指向深度正文之前，仍不标记“01～07 已全部深度完成”。
