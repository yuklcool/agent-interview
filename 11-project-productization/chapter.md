# 11. 项目拷打、业务落地与产品化

> 这一章考的不是“你做过什么功能”，而是你有没有真正把 Agent 从 Demo 推到可运营、可追责、可扩展的生产系统。二面、三面经常会围绕这里连续追问 20~30 分钟。

---

## 11-01. 自我介绍怎么讲，才能把后续问题引到你擅长的方向

### 不要这样讲

```text
我会 Java、Python、Redis、PostgreSQL、Docker，最近做了 AI Agent。
```

这只是技术名词堆叠，面试官不知道你解决了什么问题。

### 更好的结构

```text
角色定位
  ↓
最近的核心项目
  ↓
真正解决的工程难点
  ↓
业务落地结果
  ↓
你最擅长的方向
```

比如：

> 我主要做 Java/Python 后端和 AI Agent 工程。最近重点是把 nanobot 这类 Agent Runtime 接到城市照明业务，不是做一个聊天壳，而是把数据库查询、设备状态、报警、能耗分析封成 Tool，让模型负责理解和编排，业务系统负责确定执行。我重点解决的是 Session/Context、Tool/MCP、权限、多用户隔离、恢复、Trace 和生产稳定性，也就是怎么把一个概率模型放进可控的企业后端系统。

这样后面面试官自然会追：

- Agent Loop
- Tool 安全
- Session
- 多用户隔离
- RAG/NL2SQL
- Recovery

正好落到你的主场。

---

## 11-02. 你带过 Agent 项目吗？几个人？怎么拆 Harness 和模型实验边界

重点不是人数，而是 ownership。

推荐拆成：

```text
Runtime/Harness
  Session / Context / Tool / Recovery / Trace

Model/Prompt/Eval
  Routing / Prompt / Model / SFT / Eval

Business Integration
  Domain API / Permission / SQL / Workflow

Frontend/Interaction
  WebSocket / Card / HITL / Progress
```

### 为什么必须边界清楚

如果算法同学直接改 Tool Retry，工程同学直接改 Prompt，最后线上效果变化无法归因。

所以每层要有版本：

```text
model_version
prompt_version
tool_schema_version
runtime_version
retriever_version
policy_version
```

通过 Eval 判断哪个变更生效。

---

## 11-03. 算法同学想调 Prompt，工程同学想稳链路，冲突了怎么拍板

不要变成“谁职位高听谁的”。

先看问题属于哪一层：

```text
模型没理解意图            → Prompt/Model
Tool 参数经常不合法        → Schema + Prompt/SFT
支付重复调用               → Runtime/Business
上下文丢历史               → Context/Session
权限越界                   → Policy/DB
```

再看风险。

高风险问题优先代码硬约束，不能用 Prompt 抵消。

### 决策方式

```text
提出假设
  ↓
定义指标
  ↓
最小变更
  ↓
Replay / Eval
  ↓
数据决定
```

不是“工程稳定”天然比“模型效果”重要，而是不同问题必须在正确层解决。

---

## 11-04. 门票 + 租车新业务线接入现有 Agent 平台，接入口子有哪些，最小改动是什么

成熟平台不应该每接一个业务就改 Agent Loop。

应该有稳定扩展点：

```text
Domain Tool/MCP Registration
Policy Registration
Schema/Metadata
Intent/Router Catalog
Prompt/Skill Package
Eval Cases
UI Card Schema（必要时）
```

### 最小接入流程

```text
业务 Service 已存在
   ↓
封装 Tool/MCP
   ↓
注册 schema/risk/auth
   ↓
加入 Router Catalog
   ↓
补业务 Eval
   ↓
灰度
```

如果接一个租车业务需要改 `AgentRunner` 核心循环，说明平台抽象有问题。

---

## 11-05. 两个月搭一套“携程级别” Agent 底座，先写哪层，最后补哪层

“携程级别”不能真的两个月做完，所以要先做风险最高、最不可替代的底座。

### 第一阶段：可运行 + 可控

```text
Session / Run Identity
Tool Registry
Auth/Policy
Agent Loop
Structured Tool Result
Trace
Basic Eval
```

### 第二阶段：可靠性

```text
Checkpoint
Idempotency Contract
Timeout/Retry
HITL
Rate Limit
Cost Budget
```

### 第三阶段：体验和高级智能

```text
Multi-Agent
Planner
Memory
Advanced RAG
Dynamic Model Routing
UI Cards
```

### 为什么不是先 Multi-Agent

没有单 Agent 的 Trace、Tool Contract、权限和 Eval，多 Agent 只会把问题放大。

---

## 11-06. 时间紧，快速上规则还是训练/接入更智能的 AI

先判断问题稳定不稳定。

### 规则优先

- 逻辑明确
- 高风险
- 高频稳定
- 可枚举

### AI 优先

- 表达开放
- 长尾多
- 语义复杂
- 规则成本指数增长

### 常见混合

```text
Rule Gate
  ↓
LLM Interpretation
  ↓
Rule/Workflow Execution
```

例如退款资格是规则，用户说法怎么映射到“退款意图 + 订单号”可以交模型。

---

## 11-07. 设计一个会根据用户行为自适应策略的 AI 系统，怎么做得可控

“自适应”不能等于模型随便改系统策略。

建议分三层：

```text
Behavior Signals
   点击/接受/修改/拒绝
        ↓
Feature/Profile Layer
        ↓
Policy/Ranking Layer
        ↓
Agent Context
```

用户行为先变成结构化 preference，不直接改 Prompt。

### 安全边界

- 有 TTL
- 有置信度
- 用户可覆盖
- 敏感偏好不自动推断
- 新策略灰度/A-B

### 例子

用户连续多次选择“价格优先”，可以提升便宜酒店 ranking，但不能推断用户财务状况，更不能跨租户共享偏好。

---

## 11-08. Multi-Agent 客服怎么让用户感觉是“一个客服”

用户不应该看到：

```text
Billing Agent 把你转给 Refund Agent
Refund Agent 再转 Order Agent
```

前端应该只有一个 Conversation Owner。

内部：

```text
Conversation Agent
   ↓
Router
  ├─ Order Worker
  ├─ Refund Worker
  └─ Logistics Worker
   ↓
Shared Task State
   ↓
Conversation Agent 统一回答
```

Handoff 是内部机制，不是用户体验。

### 关键点

- 共享 identity/session
- Handoff 有最大次数
- Worker 不直接对用户输出
- 统一语气和 final synthesis
- 用户确认只由 owner 发起

---

## 11-09. 客服系统怎么在纯 RAG、RAG+Agent、Multi-Agent、GraphRAG 之间选

不要按“越复杂越先进”选。

### Pure RAG

适合政策/FAQ/文档问答。

### RAG + Agent

需要查订单、退款资格、物流、执行动作。

### Multi-Agent

业务域很多、Tool/权限差异大、团队独立维护时有价值。

### GraphRAG

问题需要多跳实体关系，例如集团→子公司→合同→设备→告警。

判断标准：

```text
是否需要行动
是否需要跨域
是否需要多跳关系
是否需要独立权限/状态
```

而不是“项目大就 Multi-Agent”。

---

## 11-10. Agent Demo 到企业生产要补哪些工程能力

Demo 往往只有：

```text
Prompt + LLM + Tools
```

生产至少要补：

```text
Identity / Tenant
Session / Durable Transcript
Context Governance
Tool Registry / Policy
Idempotency
Timeout / Retry / UNKNOWN
Checkpoint / Recovery
HITL
Rate Limit / Budget
Trace / Audit
Eval / Regression
Canary / Rollback
Data Privacy
Sandbox
```

面试里这道题最能看出有没有真正上线经验。

---

## 11-11. “你的 Agent 和别人有什么差异？”怎么回答才不变成“我用了更好的模型”

不要把差异点放在 provider。

更有价值的差异：

- 业务数据/Tool 深度
- 权限和状态一致性
- Context Engineering
- Recovery
- Eval/Trace
- 人机协作 UI
- Domain workflow

比如城市照明 Agent 的差异不是“用了某个大模型”，而是：

```text
自然语言
→ 设备/报警/能耗 Tool
→ 数据权限
→ 多表业务关系
→ 诊断证据
→ 事件/任务闭环
```

模型可替换，领域闭环才是壁垒。

---

## 11-12. 你的 Agent 还有哪些没优化？怎么给路线图排优先级

不要回答“以后换更大的模型”。

用风险 × 收益 × 成本排：

```text
P0 安全/正确性
P1 稳定性/可恢复
P2 效果
P3 成本/性能
P4 体验
```

例如：

```text
P0 细粒度数据权限
P0 side-effect idempotency
P1 checkpoint/recovery
P1 trace/eval
P2 schema retrieval
P2 model routing
P3 token cache
P4 richer UI
```

说明你有工程优先级，而不是追热点。

---

## 11-13. “怎么提升模型回答性能？”应该怎么拆，不要只说换模型

先定义“性能”是哪种：

```text
正确率
延迟
吞吐
成本
稳定性
```

然后分层：

### Context

减少无关历史、Tool Schema、RAG 噪音。

### Retrieval

提高召回和 Rerank。

### Model

路由、量化、更适配的模型。

### Runtime

并行 Tool、缓存、连接复用、减少无效轮次。

### Product

把确定性结果直接结构化展示，不必全部让 LLM 再生成。

---

## 11-14. 项目面试开场怎么讲，才能让后续追问落到你擅长的方向

推荐：

```text
业务问题
  ↓
为什么需要 Agent
  ↓
你的架构选择
  ↓
最难的 2~3 个工程问题
  ↓
你亲自负责什么
  ↓
结果和不足
```

不要先讲 10 分钟背景。

例如：

> 原来照明运维的数据和操作分散在多个系统，用户要靠 SQL/页面切换。我用 nanobot 做 Agent Runtime，通过 WebSocket 接自建前端，把数据库查询、报警、能耗和工单封成 Tool。最难的不是 Prompt，而是历史压缩、Tool 权限、NL2SQL 数据范围、长任务恢复和多用户隔离。我主要负责 Runtime 接入和工程化边界。

这段已经为后面的深入问题埋好入口。

---

## 11-15. 项目为什么选某个 Agent 框架/Runtime？怎么回答 Trade-off

不要说“GitHub Star 多”“社区活跃”。

从这些维度比较：

```text
Loop controllability
Context model
Tool contract
Checkpoint/recovery
Streaming
MCP
Observability
Deployment
Language ecosystem
Extensibility
```

你选 nanobot 可以强调：轻量、Agent Loop 清晰、Tool/MCP/Session 可研究和改造，适合自建前端和二次集成。

同时承认边界：如果业务需要强 DAG、持久 Workflow、复杂 Human Task，需要在外层补 Workflow Runtime，而不是硬说 nanobot 什么都有。

---

## 本章总线

> 项目类问题要始终围绕“为什么这么设计、我负责了什么、失败时怎么收敛、未来怎么演进”来讲。高级面试官不在乎你背了多少 Agent 名词，更关心你能否识别模型、Runtime、业务系统和产品层的边界，并用工程手段把不确定性控制住。
