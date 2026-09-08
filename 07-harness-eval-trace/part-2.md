# 07. Harness、Eval、Trace 与实验体系 — Part 2

## 07-07. RAG 检索层和生成层分别怎么 AB？实验流量怎么隔离

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

检索和生成分开实验，一次只改一个主要变量；用户/会话按稳定 hash sticky 分桶。

### 3. 深入原理：从概念讲到机制

检索 AB 固定生成模型/Prompt，对比 Recall/nDCG/引用覆盖；生成 AB 固定 retrieved docs，对比 groundedness、answer quality、task completion。线上实验要 sticky assignment，避免同一会话跨桶；记录 experiment_id、retriever_version、embedding_version、reranker_version、prompt_version、model_version。

* 一次实验只改主要变量。检索 A/B 固定生成模型，看 recall/nDCG；生成 A/B 固定 retrieved docs，看 groundedness/task success。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 用户/会话按稳定 hash sticky 分桶，避免一段会话跨实验导致状态污染。

### 5. 结合 nanobot / Java / 实际项目

实践上检索层可以先 offline dual-run/shadow；生成层可以在同一 retrieved docs 上离线 replay，这样不会被检索变化干扰。长会话更要固定实验桶和知识版本。

### 6. 失败模式与 Trade-off

* 只看最终文本，不记录工具轨迹。
* 线上失败不能 replay，导致改一次 Prompt 靠人工肉眼验证。
* 用一个加权总分掩盖安全红线。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“RAG 不能检索器、reranker、prompt、模型一次全换，否则指标涨跌不知道是谁贡献的。我会固定一层，只 AB 另一层，并用稳定 hash 保证同一会话不跨桶。”

---

## 07-08. 线上最难监控的 Agent 指标是什么？

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

最难的是“表面成功但决策错”的质量指标，而不是 HTTP 200、延迟或错误率。

### 3. 深入原理：从概念讲到机制

系统指标要和决策指标分开。后者包括 tool selection accuracy、argument validity、重复动作率、无效 step 比例、应澄清未澄清率、evidence coverage、policy violation、trajectory efficiency。要从 trace/trajectory 中计算，而不是只看最终文本。

* 最难通常不是 latency，而是“决策质量”和“任务真实完成”。最终文本看起来正确不代表调用路径安全，工具成功也不代表业务目标达成。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 需要把 outcome、trajectory、cost、latency、safety 联合观察，并建立分层 failure taxonomy。

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

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。

---

## 07-09. Memory 系统怎么评估？只看 Recall 行不行？

### 1. 面试官真正考什么

看你是否具备把 Agent 做成可运营平台的能力。重点不是“效果不错”，而是是否能定义指标、捕获 trajectory、复现失败、做回归、灰度、A/B、Trace 和变更门禁。

### 2. 核心结论

不够。既要评“找没找到”，还要评“该不该找、用没用对、有没有用过期/错误记忆”。

### 3. 深入原理：从概念讲到机制

离线可看 memory retrieval precision/recall/MRR、answer consistency、wrong-memory usage；在线可看个性化任务成功率、重复询问率、用户纠正率、memory-trigger latency。还要专门测 conflict 和 stale memory。

* Memory 不只看 Recall，还要看 precision、freshness、conflict rate、usefulness、privacy leakage、write quality。召回很多错误记忆反而更差。

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

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。
