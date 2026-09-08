# 07. Harness、Eval、Trace 与实验体系——全量深度版

> 覆盖 `07-01`～`07-17`。这一章的目标是回答：Agent 上线以后，**怎么知道它为什么成功、为什么失败、改动有没有变好、崩溃后怎么恢复、成本和安全怎么被控制**。

---

## 07-01. Harness 层应该管什么：Loop、恢复、Trace、预算熔断

### 核心结论

Harness 是模型外部的运行保障层。模型提供概率性智能，Harness 提供**执行秩序、硬约束和可恢复性**。

### Harness 的职责

```text
Agent Harness
├─ Loop / stop condition
├─ Context governance
├─ Tool execution
├─ Policy / permission
├─ retry / timeout / deadline
├─ checkpoint / recovery
├─ cost / token / iteration budget
├─ concurrency / bulkhead
├─ sandbox / workspace boundary
├─ trace / event / audit
└─ eval / replay hooks
```

判断一个能力是否该进 Harness，可以问：

> 它是否必须跨模型保持一致？是否是硬约束？是否需要 crash 后仍成立？是否需要测试和审计？

如果是，就不应只存在 Prompt 里。

### Pi 对照

Pi 的 Harness specification 已经把 Session、Branch、AgentLane、operation、effect intent/settlement、replay policy、durable restart point 等做成明确模型，非常适合用来解释“durable Harness”不是一组 callback，而是持久状态机。

### nanobot 对照

nanobot 的 `AgentLoop + AgentRunner + ContextGovernor + Tool Execution + Recovery + AgentHook` 构成轻量 Harness。它更简洁，适合单 Agent Runtime；企业平台可以继续补统一 budget、OTel、policy/eval/replay。

### AgentDock

AgentDock 是 Harness 外一层 Control Plane：tenant、agent/container、driver、task、workspace、resource limit、credentials 和 stream events。面试中要能区分 Runtime Harness 与平台 Control Plane。

---

## 07-02. Java 侧怎么把 LLM 调用、Tool 调用、MySQL 写入放在同一条分布式 Trace

### Trace 结构

```text
HTTP / WebSocket Request [root span]
      ↓
Agent Turn
 ├─ Context Build
 ├─ LLM Round #1
 ├─ Tool Call query_device
 │    └─ HTTP/MCP
 │         └─ Java Service
 │              └─ JDBC SELECT
 ├─ LLM Round #2
 ├─ Tool Call create_work_order
 │    └─ Java Service
 │         └─ JDBC INSERT
 └─ Final Synthesis
```

### 标准传播

跨 HTTP/MCP 服务用 W3C `traceparent/tracestate`。WebSocket 的每个逻辑 Run 仍需创建/传播 Trace Context，不能因为连接长期存在就一个连接只用一个 trace。

### Agent 特有 attributes

```text
run_id
turn_id
session_key
iteration
plan_id / plan_version
step_id
tool_call_id
tool_name
model/provider
prompt_version
```

### Java

Spring Boot 可用 Micrometer Tracing/OpenTelemetry 对 Web、WebClient、HTTP client、JDBC 自动 instrumentation；Agent Gateway/Tool Adapter 负责把 trace context 继续传给 nanobot/MCP。

### nanobot

`AgentHook` 的 `before_iteration / before_execute_tool / after_execute_tool / after_run` 是天然 instrumentation seam。不要要求 nanobot 当前已经开箱提供完整企业 OTel；可以基于 Hook 加 tracing adapter。

### 日志 vs Trace

日志回答“发生了什么细节”，Trace 回答“谁导致了谁”。多 Agent 并发时仅按时间排序日志无法可靠建立因果关系。

---

## 07-03. Agent 效果评测集怎么建？Golden Dataset 从哪来？回归怎么跑

### Golden Set 不是问答题库

一个 Agent case 应包含：

```yaml
case_id: refund_timeout_01
input: "帮我退款"
env_state: order_paid
allowed_tools: [query_order, refund, query_refund_status]
expected_outcome: refund_state_is_known_or_explicit_unknown
trajectory_constraints:
  - must_not_claim_success_when_status_unknown
  - must_not_retry_refund_without_reconcile
graders:
  - outcome
  - tool_sequence
  - policy
```

### 来源优先级

1. 真实高频任务；
2. 高价值/高风险路径；
3. 历史线上事故；
4. 用户投诉/人工接管；
5. 边界和对抗案例；
6. 新功能受影响域。

最初 20～50 个高价值 case 就有意义，不要等“有一千题”才做 Eval。

### 随机性

同一个 case 建议多 trial，记录 pass rate/variance，而不是单次通过即认为稳定。

### 回归链

```text
Prompt/Model/Schema/Context change
        ↓
Offline replay
        ↓
Hard guardrails
        ↓
Quality gates
        ↓
Shadow / Canary
        ↓
Production
```

---

## 07-04. 任务完成率、工具调用准确率、幻觉率、P99、单轮 Token 成本打架时先保哪个

### 不用一个总分

把指标分层：

```text
Level 0 Hard Guardrail
- unauthorized side effect
- wrong payment/refund
- sensitive data leakage
- severe factual claim without evidence

Level 1 Quality
- task success
- tool correctness
- groundedness

Level 2 SLA
- P95/P99
- availability

Level 3 Efficiency
- token
- model cost
- tool cost
```

红线不应该被平均分稀释。一次错误退款不能用“整体成功率 +2%”交换。

### 风险分场景

知识问答可以更积极使用缓存、小模型、压缩；支付/设备控制宁可多一次状态查询、多 1 秒延迟，也不能把 UNKNOWN 说成 SUCCESS。

### Pareto

在 guardrail 满足后，再看 success/cost/latency 的 Pareto front，而不是人为给一个 `0.5*accuracy + 0.3*latency + ...` 把严重失败隐藏掉。

---

## 07-05. 多 Agent 线上答错，怎么定位 Planner 拆错还是 Worker 调错工具

### 最终答案只是 symptom

必须有 trajectory：

```text
Router decision
 ↓
Plan v3
 ├─ Step s1 → Worker A
 │   └─ Tool tc1 args/result
 ├─ Step s2 → Worker B
 │   └─ Tool tc2 args/result
 ↓
Reviewer verdict
 ↓
Final answer
```

### 归因 taxonomy

- Router error；
- Planner goal/dependency error；
- Context projection error；
- Worker tool selection error；
- Argument error；
- Tool/provider error；
- State merge/stale result；
- Reviewer error；
- Final synthesis error。

### 字段

每个 Span/Event 带：

```text
plan_version
step_id
agent_id/role
tool_call_id
input_hash
artifact_id
status/error_kind
```

### 例子

Planner 把“查最便宜”写成 step goal“查最早”，Worker 按 goal 正确调用 Tool，这应该归 Planner；如果 Planner goal 正确，Worker 却选了 `flight_by_departure_time`，归 Worker/Tool Selection。

---

## 07-06. Harness 工程化里 Tool Mock 和 Trajectory Replay 怎么搭？失败样本怎么复现

### Tool Mock

按 canonical `tool_name + normalized_args + fixture_version` 返回稳定结果：

```text
flight_search({date, from, to})
      ↓
fixture: FOUND / NO_RESULT / TIMEOUT / 503
```

支持延迟、错误和 partial response，才能测试恢复逻辑。

### 两种 Replay

**Freeze Tool，变模型/Prompt**：验证新模型在相同环境 observation 下是否更好。

**Freeze Model Outputs，变 Harness**：验证 Tool execution、state transition、recovery 是否正确。

### Replay 需要保存什么

```text
model input projection
model response/tool calls
tool results
state snapshots
prompt/model/schema/context versions
random seed（若可用）
timing/error fixtures
```

### 线上 failure 回流

对生产 trace 脱敏后，把关键 Tool Result 固化成 fixture；这样“网关 timeout 后重复退款”可以每次 CI 重放，而不是等下一次事故。

### nanobot

AgentHook 可抓 iteration/tool boundaries；测试中可以用替代 ToolRegistry/Tool 实现返回 fixture。Recovery/injection 都应有 deterministic test case。

---

## 07-07. RAG 检索层和生成层分别怎么 AB？实验流量怎么隔离

### 分层实验

**Retrieval A/B**：固定生成模型/Prompt，比较 retriever/chunk/embedding/rerank；指标 `Recall/nDCG/citation coverage`。

**Generation A/B**：固定同一 retrieved docs，比较 model/prompt；指标 `groundedness/answer quality/task success`。

一次同时换 embedding、reranker、prompt 和 model，线上涨了你也不知道谁贡献。

### Sticky Assignment

按 `user_id` 或 `session_id` 做稳定 hash 分桶：

```text
bucket = hash(subject_id, experiment_id) % 100
```

同一长会话不能每轮换桶，否则 Context、Memory、knowledge_version 都被实验污染。

### 记录版本

`experiment_id / retriever_version / embedding_version / reranker_version / prompt_version / model_version / knowledge_version`。

---

## 07-08. 线上最难监控的 Agent 指标是什么？

最难不是 HTTP error 或 latency，而是**表面完成但决策错误**。

### Decision Quality Metrics

```text
Should-Call Accuracy
Tool Selection Accuracy
Argument Validity
Unnecessary Tool Rate
Forbidden Tool Rate
Repeated Action Rate
Clarification Quality
Evidence Coverage
No-progress Ratio
Trajectory Efficiency
```

### Outcome 必须从业务侧确认

Agent 回复“已创建工单”不等于 task success。真正 success 应查询业务系统是否存在 work_order_id、状态是否有效。

### AgentDock

Control Plane 已有 task/event/usage 这类平台数据，可以作为 Runtime trajectory 之外的第二视角：container/task 是否成功、耗时、token、取消、资源状态。最终还要和 Domain outcome join。

---

## 07-09. Memory 系统怎么评估？只看 Recall 行不行？

不够。Memory 的坏处常来自“找到了不该找的东西”。

### Retrieval 指标

- Recall/Precision/MRR；
- cross-user leakage；
- stale recall；
- conflict retrieval。

### Write 指标

- admission precision；
- duplicate rate；
- wrong fact write；
- preference scope accuracy；
- update/expiration correctness。

### Downstream 指标

- personalized task success；
- 用户重复解释率；
- user correction rate；
- wrong-memory usage rate；
- latency/token。

### OpenViking

OpenViking有 session→memory extraction 和 observable retrieval trajectory，因此 Eval 可以区分“写错 memory”“检索错 path”“LLM 用错 evidence”三个阶段，而不是只看最终答案。

---

## 07-10. Agent 端到端成功率为什么不够？应该怎么分解？

End-to-end success 只告诉你“坏了”，无法告诉优化位置。

### Funnel

```text
Intent/Router Correct
      ↓
Retrieval/Context Correct
      ↓
Plan Correct
      ↓
Tool Selection Correct
      ↓
Arguments Correct
      ↓
Tool Execution Correct
      ↓
State Transition Correct
      ↓
Evidence Use Correct
      ↓
Final Outcome Correct
```

每层可以有局部 grader，同时保留最终 E2E grader。

### 为什么局部指标也不能独立看

Tool selection 100% 但业务 task success 低，可能是参数、外部数据、final synthesis 出错；所以要联合 trajectory + outcome。

---

## 07-11. 怎么量化“工具调用准确率”？

至少拆五维：

### 1 Should-Call

本来不用 Tool 的问题有没有乱调？

### 2 Tool Selection

在应该调用时选择了正确 Tool set 吗？

### 3 Argument Accuracy

关键参数、单位、日期、ID、范围正确吗？

### 4 Ordering/Dependency

调用顺序是否满足 precondition？

### 5 Result Use

Tool 返回 NO_RESULT/UNKNOWN 后，模型有没有正确使用，还是编成成功？

进一步还可以看：

```text
Unnecessary Call Rate
Forbidden Call Rate
Duplicate Call Rate
Repair Count
Tool Cost per Successful Task
```

接口 HTTP 200 不代表 Tool Call“准确”。

---

## 07-12. 线上日志很多，怎么抽成有限离线评测集？为什么不能随机抽样？

随机抽样会被大量简单、正常、高频 Query 淹没，高风险长尾根本抽不到。

### 分层采样

```text
40% high-frequency representative
20% high-value/high-risk
15% historical failures
10% long-tail
10% adversarial/boundary
5% new feature/domain
```

比例只是示意，最终按业务调。

### Failure-based mining

从 Trace 自动筛：
- repeated tool calls；
- multiple repairs；
- UNKNOWN；
- human takeover；
- user correction；
- policy denied；
- very high token/latency；
- low grader score。

这些样本比纯随机更有回归价值。

### 统计总体效果

Eval 集可以故意提高风险 case 比例，但线上总体 KPI 估计要按真实流量权重还原，避免“测试集成功率”冒充生产分布。

---

## 07-13. 业务指标提升怎么证明是 AI 带来的，而不是别的改动？

### 需要因果实验

确定 Primary Metric 与 Guardrail；使用随机/稳定分桶，控制同时期 UI、价格、运营策略等改动。

例如照明运维 Agent：

```text
Primary: 人工定位异常平均耗时
Secondary: 工单创建完成率
Guardrail: 错误工单率 / 越权率 / P99 / cost
```

A 组旧规则/旧 Agent，B 组新 Agent；用户/项目稳定分桶。

### 不要拿模型离线准确率当业务收益

模型准确率从 85→90%，如果人工处理时间不变、投诉升高，就不能说业务成功。

### 长期效应

Agent 可能初期新鲜感高，过几周用户使用方式变化，因此重要功能要观察长期 retention/纠正/人工接管趋势。

---

## 07-14. 业务方只说“AI 效果差”，你怎么系统排查？

不要第一反应改 Prompt。

### 先把模糊反馈变 failure taxonomy

```text
理解/路由
检索/Memory
规划
Tool selection
Tool args
外部系统
状态/恢复
最终生成
UI/Streaming/Latency
```

### Bad Case Review

对每个 case 拉完整 Trace：

```text
Input
→ model-facing context
→ router/plan
→ tool calls/args
→ tool results
→ state transitions
→ final evidence
→ answer
```

### 常见误判

业务说“模型不聪明”，结果发现 Tool API 返回旧数据；说“RAG 差”，实际 Query 的 tenant filter 把正确文档过滤了；说“Agent 乱”，其实用户新消息到达后旧 Worker result 覆盖新 Plan。

只有 Trace/Replay 能把这些问题分开。

---

## 07-15. Prompt、模型、Tool Schema 变更怎么做发布门禁？

### 全部版本化

```text
prompt_version
model_version
model_routing_policy_version
tool_schema_version
context_policy_version
retrieval_version
skill_version
```

### Gate

```text
Change
 ↓
Static/schema checks
 ↓
Golden regression
 ↓
Safety/adversarial suite
 ↓
Trajectory diff
 ↓
Shadow
 ↓
Canary 1%→5%→20%
 ↓ guardrails
Full rollout
```

### Tool Schema 特别危险

字段重命名、required 变化会影响旧 Session/checkpoint 和模型行为；需要 version/compatibility strategy，而不是直接覆盖线上 Schema。

### Rollback

必须能快速 pin 旧 model/prompt/schema/context policy。发布系统没有版本 pin，就无法可靠 replay 历史失败。

---

## 07-16. Harness Engineering、Context Engineering、Prompt Engineering 三者怎么区分？

### Prompt Engineering

“如何表达指令”：角色、格式、示例、任务说明。

### Context Engineering

“这一轮给模型什么”：history、summary、memory、RAG、tool schemas、current state、budget 下的投影。

### Harness Engineering

“模型在什么规则下运行”：Loop、Tool、Policy、Budget、Recovery、Sandbox、Trace、Eval。

```text
Prompt ⊂ Context Strategy
Context lives inside Harness-controlled runtime
```

不是严格代码集合包含关系，但工程视角范围逐渐扩大。

### 四项目映射

- OpenViking：Context data/retrieval；
- nanobot：Context + lightweight Harness；
- Pi：更强 durable Harness 语义；
- AgentDock：Harness 外的多租户 Control Plane。

这样回答比背三个定义更有系统感。

---

## 07-17. Agent 开发流程怎么做成 Eval-driven，而不是“改 Prompt→人工试几次”？

### 闭环

```text
Define task + risk
      ↓
Minimal Golden Set
      ↓
Build baseline
      ↓
Capture trajectory
      ↓
Failure taxonomy
      ↓
Change one layer
      ↓
Replay/regression
      ↓
Canary
      ↓
Production failures feed back
      └──────────────→ Golden Set
```

### 开发者工作流

每个 PR 如果修改 Prompt、Tool Schema、Router、Context policy，CI 自动跑对应 eval subset；核心 case 有 hard gate。线上新事故脱敏后变 fixture/test。

### 为什么这比人工试几次强

人工测试：不可重复、样本偏、看不到回归、无法比较版本。

Eval-driven：每个 failure 都能转成资产，系统随着事故和真实流量逐步变得更难退化。

### 最终目标

不是追求“100% 自动评分”，而是建立稳定反馈回路：能复现、能归因、能比较、能灰度、能回滚。

---

# 本章统一观测数据模型

```text
Run
├─ trace_id
├─ run_id / turn_id
├─ tenant/user/session
├─ prompt/model/context versions
├─ total latency/token/cost
├─ final outcome
└─ guardrail status

Trajectory Event
├─ sequence
├─ plan_version / step_id
├─ agent role
├─ event type
├─ tool_call_id
├─ input/output hashes
├─ artifact/evidence ids
└─ status/error_kind
```

真正生产级 Agent 的标志不是 Demo 回答很惊艳，而是：**一次失败能定位、一个改动能评估、一个版本能回滚、一次崩溃能恢复、一个副作用能审计。**
