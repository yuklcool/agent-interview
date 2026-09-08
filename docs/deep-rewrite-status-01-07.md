# 01～07 深度重构状态

> 结论：01～07 **不是完全没有深度整理**，而是“全集题库已迁入，但只有部分核心题已经升级成源码级 Deep Dive”。`chapter.md` 目前仍包含大量早期批量迁移内容，不能视为最终答案。

## 当前状态

| 章节 | 当前状态 | 已有 Deep Dive | 后续方向 |
|---|---|---|---|
| 01 Agent Runtime | 部分深化 | Agent Loop、Parallel Tool Calling | Session/Stop/Iteration/Framework boundary 全量升级 |
| 02 Planning / Routing / Multi-Agent | 部分深化 | Model Routing、ReAct/Plan/DAG | Planner/Worker/Reviewer、Replan、State Sharing、Handoff |
| 03 Tools / MCP | 部分深化 | Tool Schema Runtime、MCP Runtime | Tool Discovery、RBAC、Skill、Progressive Disclosure、Structured Output |
| 04 Reliability / Security | 部分深化 | nanobot Recovery、Tool Failure/Idempotency | Timeout、Retry、UNKNOWN、HITL、Prompt Injection、Sandbox |
| 05 Context / Memory | 部分深化 | Context Engineering | Session、Long-term Memory、Memory Admission、Conflict、Compaction |
| 06 RAG / Retrieval | 部分深化 | Text-to-SQL | Chunk、Hybrid、RRF、ReRank、Query Rewrite、OpenViking Recursive Retrieval |
| 07 Harness / Eval / Trace | 部分深化 | Eval / Trace | Golden Dataset、Tool Mock、Replay、A/B、Failure Attribution |

## 重构规则

以后 `chapter.md` 的作用调整为：

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

## 真实项目案例基线

后续 01～07 统一优先从以下四个真实项目选案例：

- **Pi**：Agent Runtime / Harness / Session / Operation State / Effect Recovery
- **nanobot**：AgentLoop / Runner / Context Governance / Tool Registry / Recovery / Injection
- **AgentDock**：Control Plane / Multi-tenant / Container / Driver / Task Event / MCP-Skill distribution
- **OpenViking**：Context Database / Memory / Resource / Skill / L0-L1-L2 / Retrieval Trajectory

详细映射见：[项目案例对照](project-case-map.md)。

## 不再允许的答案模式

下面这种答案后续视为待重构：

```text
“RAG 是先检索再生成。”
“Agent 可以用 ReAct。”
“MCP 用来统一工具调用。”
“Redis 可以保存 Session。”
“Tool 失败可以 retry。”
```

因为这些只描述名词，没有解决工程问题。

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

- Pi 的 effect intent / settlement / replay policy
- nanobot 的 interrupted Tool recovery
- AgentDock 的平台重试、任务状态和隔离边界

这才算深度答案。

## 执行顺序

01～07 将按以下顺序逐步重构：

```text
P0：Agent Runtime / Tool / Recovery / Context
P1：Planning / Multi-Agent / RAG
P2：Harness / Eval / Trace
P3：把 chapter.md 中每道题链接到对应 Deep Dive 或补齐深度正文
```

在 P3 完成前，不再标记“01～07 已全部深度完成”。
