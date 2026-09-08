# 07. Harness、Eval、Trace 与实验体系

> 本章共 17 个专题。每题按“原理 → 工程 → nanobot/Java → 失败边界 → 面试表达”组织。

## 07-01. Harness 层应该管什么：Loop、恢复、Trace、预算熔断

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

Harness 是模型外面的运行保障层：模型给智能，Harness 给秩序。

### 3. 深入原理：从概念讲到机制

Harness 主要管 Agent Loop 上限/停止条件、Context、Tool execution、Policy、Budget、Retry/Recovery、Trace、Eval Hook、Sandbox/隔离、并发治理。它不负责具体业务答案，而是确保模型行为可控、可观测、可恢复。

* Harness 是模型外部的执行秩序层，至少管：Loop/Stop、Context、Tool execution、Policy、Budget、Retry/Recovery、Trace、Eval hook、Sandbox、并发和版本。
* 判断一个能力该不该放 Harness：是否需要对所有模型一致、是否属于硬约束、是否需要可测试/可恢复。如果答案是，通常不应只写 Prompt。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot 的 AgentLoop + AgentRunner + ContextGovernor + Tool Execution + Session Recovery + AgentHook 已经形成轻量 Harness。你做平台化时可以补 OTel、统一 Tool Policy、Budget、Eval/Replay、租户隔离等。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 7. 场景推演

```
LLM
 ↑↓
Harness
 ├─ Loop / Stop
 ├─ Context
 ├─ Tool Policy
 ├─ Budget
 ├─ Trace
 ├─ Recovery
 └─ Eval / Sandbox
 ↑↓
Business Tools
```

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“Harness 不负责业务答案，它负责让 Agent 别跑飞、能恢复、能追踪、能回归。模型给智能，Harness 给秩序。”
源码/工程落点： nanobot/agent/loop.py；runner.py；context_governance.py；session/recovery.py；agent/hook.py
来源：原深度版答案，已在本次总表中重新归类。

---

## 07-02. Java 侧怎么把 LLM 调用、Tool 调用、MySQL 写入放在同一条分布式 Trace

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

用 W3C Trace Context 贯穿一次用户 Run：request 是根 span，LLM round、Tool、HTTP、SQL 都是子 span。

### 3. 深入原理：从概念讲到机制

Java 侧用 OpenTelemetry/Micrometer Tracing 自动接 Spring Web/WebClient/JDBC；跨 WebSocket/HTTP/MCP 时传播 traceparent。Agent 特有字段 run_id、turn_id、iteration、tool_call_id、session_key 作为 span attributes。日志只补充细节，真正因果关系靠 parent-child span。

* 以一次用户 Run 为 root span，子 span 包含 LLM round、Tool、MCP/HTTP、DB、Subagent。跨进程用 W3C traceparent 传播，run_id/turn_id/tool_call_id 做业务 attributes。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 日志是事件细节，Trace 是因果结构。没有 parent-child，只按时间拼日志无法可靠定位并行 Agent。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot 当前不是开箱即用的一整套 OTel trace，但有 AgentHook 生命周期边界：before_iteration、before_execute_tool、after_execute_tool、after_run。可以实现 tracing hook，在这些 seam start/end span；Java 入口把 traceparent 放进 metadata，Tool Adapter 再向下游传播，MySQL 用 JDBC instrumentation 自动成为子 span。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 7. 场景推演

```
HTTP/WebSocket request [trace_id]
  ↓
Agent turn span
  ├─ LLM round 1
  ├─ Tool query_flight
  │    └─ downstream HTTP
  ├─ Tool create_order
  │    └─ JDBC INSERT
  └─ LLM final
```

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“Trace 不是把日志时间戳拼起来，而是明确 parent-child span。用户请求作为根 span，LLM round、Tool Call、下游 HTTP、JDBC 都挂在同一个 trace_id 下，再用 run_id/tool_call_id 做业务关联。”
源码/工程落点： nanobot/agent/hook.py 可作为 instrumentation seam
来源：原深度版答案，已在本次总表中重新归类。

---

## 07-03. Agent 效果评测集怎么建？Golden Dataset 从哪来？回归怎么跑

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

Golden set 来自真实业务任务、历史失败、关键路径和边界案例；Agent 既评 outcome，也评 trajectory。

### 3. 深入原理：从概念讲到机制

Agent eval 不能只比较最终文本。Case 至少包含 task input、环境初态、允许工具、期望 outcome、关键 trajectory 约束、grader。初期不需要几千题，先从 20-50 个高价值真实任务开始，持续把线上事故、用户反馈、失败样本固化进回归集。由于模型有随机性，同一 case 应跑多次 trial 统计 pass rate。

* Golden case 应包含 task input、环境初态、可用工具、期望 outcome、关键 trajectory constraint、grader。Agent eval 不只是比较最终字符串。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 来源优先真实线上：高价值成功路径、事故、用户投诉、边界案例。模型有随机性，同一 case 要多 trial 看 pass rate/variance。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

你的平台可以把“查灯状态”“多表 SQL”“创建工单”“退款 UNKNOWN”“Tool 参数错”“上下文压缩续聊”“恢复中断 Tool”等变成固定 case。每次 model/prompt/tool schema/context 改动触发离线 replay；通过后再 canary。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 7. 场景推演

```
线上真实任务/事故
      ↓ 脱敏
Golden Case
  ├─ input
  ├─ env snapshot
  ├─ tool fixtures
  ├─ expected outcome
  └─ trajectory constraints
      ↓
每次版本变更自动 replay
      ↓
Regression Gate → Canary → Production
```

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“Golden dataset 不是人工编一千道题，而是持续把真实成功路径、失败样本和关键业务边界固化成可复现任务。Agent 既看最终结果，也看过程中有没有调错工具、越权或乱序。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 07-04. 任务完成率、工具调用准确率、幻觉率、P99、单轮 Token 成本打架时先保哪个

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

先保安全/正确性红线，再保任务完成，之后在 SLA 内优化延迟和成本。

### 3. 深入原理：从概念讲到机制

可以把指标分成 Hard Guardrail 和 Optimization Metric。错误支付、错误退款、越权、严重幻觉属于不可交换红线；任务完成率和工具正确率属于质量目标；P99/Token/成本属于资源目标。不要用一个加权总分掩盖灾难性问题，应做多目标 gate 或 Pareto 优化。

* 全链路治理要区分知识幻觉、工具事实幻觉、状态幻觉和 memory hallucination。不同类型用不同机制：RAG/引用、强类型 ToolResult、状态机、memory provenance。
* RAG 只能降低知识缺失导致的幻觉，无法解决错误 Tool、过期数据、业务状态不确定或模型错误归纳。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

退款/下单 Agent 宁可多一次状态查询、多耗一点 token，也不能把 UNKNOWN 说成 SUCCESS；纯知识问答可以更积极地用小模型、缓存、压缩换成本。不同风险级别业务有不同优先级。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“我不会用 2% 的任务完成率提升去交换一次错误退款。先定义不可破的 guardrail，再在满足安全和正确性的前提下优化成功率、P99 和 Token 成本。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 07-05. 多 Agent 线上答错，Trace 里只有最后答案错，怎么定位是 Planner 拆错还是 Worker 调错工具

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

必须做 trajectory observability：计划、路由、每次 Tool 输入输出、状态变化都要可追踪。

### 3. 深入原理：从概念讲到机制

一个 run 应有层级 span：Router → Planner → Step → Worker → Tool → Artifact → Reviewer，并记录 plan_version、step_id、tool_call_id、input_hash、output_summary、error_type。如果只存最终答案，就只能看到 symptom，不能做根因定位。

* 需要 trajectory observability。一个 Run 至少能还原 Router→Planner→Step→Worker→Tool→Artifact→Reviewer 的输入输出和版本。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 错误定位树：Plan goal 错→Planner；Plan 对但 Tool 选错→Worker；Tool 对参数错→argument generation；Tool/数据错→domain layer。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

例如 Planner 把“最便宜”拆成“最早”，在 Planner span 就能看到目标偏差；Plan 正确但 Worker 调错 Tool，是 Worker/tool selection；Tool 对但 city 参数错，是 argument generation；Tool 正确但数据源错，是 Tool/domain 层。nanobot 的 AgentHook 能提供单 Agent 迭代/Tool 边界，多 Agent 的 Planner/step span 要平台层补。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“最终答案只是 symptom。Agent 调试必须看 trajectory：Plan 怎么生成、Worker 拿到什么 context、调了什么 Tool、参数是什么、状态怎么变。没有这些 trace 就无法判断问题在哪一层。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 07-06. Harness 工程化里 Tool Mock 和 Trajectory Replay 怎么搭？失败样本怎么复现

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

把外部不稳定依赖从 Agent 行为评测中隔离，才能可重复比较模型/Prompt/Harness。

### 3. 深入原理：从概念讲到机制

Tool Mock 根据 tool name + normalized args 返回固定结果、错误或延迟；Trajectory Replay 保存 model input、tool call、tool output、state snapshot。回放时可以冻结 Tool 只换模型，或冻结模型输出只测 Harness，从而做变量隔离。失败样本必须保存版本：prompt/model/tool schema/context policy。

* Tool Mock 的目标是冻结外部世界，Replay 的目标是冻结一次运行的可观测输入/输出，使变量隔离成为可能。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 保存 model/prompt/tool_schema/context_policy 版本和 fixtures。Replay A 固定 Tool 换模型；Replay B 固定模型输出只测 Harness。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

线上失败先脱敏固化 session/context snapshot、tool schema version、mock fixtures、expected outcome。对 nanobot 可以通过 AgentHook 记录 Tool call/params/result，在测试里替换 ToolRegistry 的工具实现；Recovery/Injection 也可以用 deterministic fixtures 重现。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 7. 场景推演

```
Production Failure
   ↓ capture
Trajectory + Tool Fixtures + Versions
   ↓
Replay Mode A：固定 Tool，换 Model/Prompt
Replay Mode B：固定 Model 输出，测 Harness
   ↓
定位是谁导致回归
```

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“不做 Mock 和 Replay，网络波动、库存变化、模型变化会混在一起，你根本不知道回归是谁造成的。我要把 failure case 固化成可重复实验。”
来源：原深度版答案，已在本次总表中重新归类。

---
