# 07. Harness、Eval、Trace 与实验体系 — Part 3

## 07-10. Agent 端到端成功率为什么不够？应该怎么分解？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

因为同样一个失败结果可能来自 Planner、Tool 选择、参数、外部系统、Reviewer 或最终生成；只看 final pass 无法优化。

### 3. 深入原理：从概念讲到机制

把任务拆成 trajectory checkpoints：intent/plan correctness、tool selection、argument accuracy、tool execution、state transition、evidence quality、final outcome。既可做阶段 grader，也可做 end-to-end grader。

* 端到端指标只能告诉“坏了”，不能告诉哪层坏。应分解 intent/router、retrieval、planner、tool selection、argument、tool execution、review、final synthesis。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 07-11. 怎么量化“工具调用准确率”？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

至少拆成 Should-Call、Tool-Selection、Argument、Ordering、Result-Use 五类指标。

### 3. 深入原理：从概念讲到机制

有些请求本来不该调工具，因此单纯“调用是否成功”会失真。可以构造带期望 trajectory 的 eval case：该不该 call、正确 tool set、关键 args、依赖顺序、是否正确使用 Tool Result。

* 至少拆 Tool Selection Accuracy、Argument Accuracy、Sequence/Dependency Accuracy、Unnecessary Call Rate、Forbidden Call Rate。只有“工具调用成功率”会掩盖选错工具但接口返回 200。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 07-12. 线上日志很多，怎么抽成有限的离线评测集？为什么不能随机抽样？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

随机样本会被高频简单问题淹没。应按任务类型、风险、失败类型、用户群、长尾和版本变化做分层采样。

### 3. 深入原理：从概念讲到机制

推荐组成：高频代表性任务 + 高价值/高风险任务 + 历史事故 + 边界/对抗样本 + 新功能样本。每次线上新 failure 经过脱敏和归因后入库，设置 case owner 和 expected outcome。

* 随机样本会被大量简单正常流量淹没。离线集应分层采样：高价值路径、错误类型、长尾、风险动作、新版本受影响域，再按真实流量权重做总体估计。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 07-13. 业务指标提升怎么证明是 AI 带来的，而不是别的改动？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

用目标指标 + Guardrail + 控制变量的 A/B/灰度实验，模型准确率不能替代业务收益。

### 3. 深入原理：从概念讲到机制

先从业务目标倒推 metrics，再保持 UI/流量/其他逻辑尽量不变，只改变 AI 策略；按稳定用户/会话 hash 分桶；逐步放量并观察投诉率、错误率、成本等 guardrail。

* 要用实验设计证明增量：随机/准随机分桶、控制同期其他产品改动、定义 primary metric/guardrail、统计显著性和长期效应。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。
