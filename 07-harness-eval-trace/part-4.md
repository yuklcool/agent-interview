# 07. Harness、Eval、Trace 与实验体系 — Part 4

## 07-14. 业务方只说“AI 效果差”，你怎么系统排查？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

先把主观反馈转成 failure taxonomy，再沿 Agent pipeline 回放；不要第一反应就是调 Prompt。

### 3. 深入原理：从概念讲到机制

常见桶：理解/路由错、检索错、Tool 选错、参数错、外部数据错、生成错、体验/延迟。对每个 bad case 看输入→context→plan→tool→result→final，统计主要失败集中在哪一层，再做针对性实验。

* 先做 failure decomposition：输入/意图→知识→规划→工具→状态→生成→UI/业务流程。没有 trace 就先补 trace，再谈改模型。

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

## 07-15. Prompt、模型、Tool Schema 变更怎么做发布门禁？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

把这些都当版本化软件变更：离线 regression → shadow/replay → canary → 指标 gate → 全量，且随时可回滚。

### 3. 深入原理：从概念讲到机制

记录 prompt_version、model_version、tool_schema_version、context_policy_version。一次实验尽量只改一个主要变量；高风险 Tool 的 contract 变更还要兼容旧 session/checkpoint。

* Prompt、模型、Tool Schema 都是生产代码，应版本化。发布前离线 regression，之后 shadow/canary，监控 guardrail，保留快速 rollback。

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

## 07-16. Harness Engineering、Context Engineering、Prompt Engineering 三者怎么区分？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

Prompt 解决“怎么说指令”，Context 解决“给模型哪些信息”，Harness 解决“模型外如何约束、增强、验证、恢复和观测”。三者是层次关系，不是互相替代。

### 3. 深入原理：从概念讲到机制

一个系统可以 Prompt 很短但 Context 很复杂，也可以 Context 很好但 Harness 很弱导致越权、死循环。生产 Agent 的工程重心正在从“调一句 Prompt”转到上下文治理和外部运行保障。

* Prompt Engineering 管“如何表达指令”；Context Engineering 管“这轮给模型哪些信息”；Harness Engineering 管“模型在什么运行环境和硬约束下行动”。范围逐级扩大。

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

## 07-17. Agent 开发流程怎么做成 Eval-driven，而不是“改 Prompt→人工试几次”？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

先定义可复现任务和指标，再开发，再把每次线上 failure 回流评测集。评测是开发反馈回路，不是上线前最后一道考试。

### 3. 深入原理：从概念讲到机制

一个实用流程：定义任务/风险→建立最小 golden set→实现 baseline→记录 trajectory→按 failure taxonomy 优化→离线 replay→canary→线上回流。每次改 Prompt/model/tool schema 都触发相同 gate。

* Eval-driven 开发把“失败样本→可复现 case→改动→自动回归→灰度”变成循环。没有 eval 的 Prompt 调优，本质上是不可重复的人肉试错。

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
