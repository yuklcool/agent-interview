# 05. Context、Memory、Session 与状态

> 本章共 11 个专题。每题按“原理 → 工程 → nanobot/Java → 失败边界 → 面试表达”组织。

## 05-01. Agent Loop 一次模型调用前会做什么？上下文压缩在哪一步

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

每一轮 LLM 调用前都要重新做 Context Engineering；压缩的是“模型视图”，不是删除 durable history。

### 3. 深入原理：从概念讲到机制

典型顺序：解析 Session → 获取持久化历史 → 拼入系统指令/权限/Memory/RAG/Tool Schema → 计算 token budget → compaction → 构造 model-facing messages → 调模型。Agent Loop 中每轮都可能新增 Tool Result、用户 injection、provider state，因此 context 不是会话开始时拼一次就固定。压缩要以完整 turn/稳定边界为单位，避免产生 orphan tool result。

* 每轮都要重新构造 context projection：System/Policy→Session summary/recent turns→Memory/RAG→Tool schemas→current observation。然后做 token budget 和 compaction，再调用模型。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 压缩应发生在 durable history 和 model request 之间；不能破坏未闭合的 assistant tool_call / tool_result 对。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot 的 AgentRunner 在每轮请求前会通过 ContextGovernor/compaction 得到本轮 request_messages；Session 仍保留完整消息和 summary/archive 水位。也就是说 Durable Transcript 和 Model-facing Context 是两套视图。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 7. 场景推演

```
Session JSONL / Durable Transcript
      ↓
Summary / last_archived / recent raw messages
      ↓
Memory + Runtime Context + Tool Schema
      ↓
Token Budget / Compaction
      ↓
Model-facing Context
      ↓
LLM
```

### 8. 面试官可能继续追问

为什么不能直接删老消息？——审计/恢复/长期记忆还需要；删除会破坏事实来源。 Tool Call 正在进行时能压吗？——不要从未完成的 Tool Call/Result 对中间切断。

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“压缩发生在 durable history 已经存在和真正调用模型之间。Session 里保存事实记录，Context Governor 每轮根据 token budget 生成模型视图；所以压的是 context projection，不是把历史删掉。”
源码/工程落点： nanobot/agent/runner.py；nanobot/agent/context_governance.py；nanobot/session/manager.py
来源：原深度版答案，已在本次总表中重新归类。

---

## 05-02. Agent 间传递上下文是传全量还是传结论？上下文爆炸怎么压

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

传“结构化状态 + 必要证据引用”，不要传整个聊天历史，也不要只传一句模糊总结。

### 3. 深入原理：从概念讲到机制

共享字段通常包括 goal、step、status、关键参数、artifact_id、evidence pointer、constraints。大文件/SQL 结果放外部 Artifact Store，只传引用；已完成步骤压成结论；每个角色根据需要做 context projection。

* 传递原则是“结构化状态 + 必要证据引用 + 当前目标”，而不是全量 transcript，也不是只有一句总结。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 大结果放 Artifact Store；handoff 传 artifact_id、schema、摘要、provenance。这样可以按权限读取且避免 token 重复。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot 已经有 durable session 与 model-facing context 区分、summary/compaction。多 Agent 场景进一步让 subagent 只拿自己的小上下文；大 Tool Result 不要复制给所有 Agent。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

为什么不能只传总结？——可能丢证据、参数和可验证性。 为什么不能全量？——token 爆炸、噪声增大、隐私和权限面扩大。

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“我传的是状态和产物，不是聊天记录。必要证据通过 artifact_id 引用，角色只拿自己完成当前 step 所需的 context projection。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 05-03. Agent 里的“状态”和“上下文”有什么区别？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

Context 是本轮给模型看的材料；State 是系统对任务真实进度的结构化记录。Context 可以被压缩，关键 State 不能靠自然语言猜。

### 3. 深入原理：从概念讲到机制

State 常含 current_step、completed_steps、retry_count、tool_state、user_confirmations、artifacts、plan_version。Context 是 State/History/Memory/RAG/Tool Schema 的投影。把二者混在一起会导致一压缩历史，任务进度也跟着“失忆”。

* State 是系统要长期维护、驱动执行的结构化事实，例如 plan status、订单状态、current_step；Context 是本轮为了帮助模型决策而投影出来的信息集合。
* State 可以决定下一步，即使模型没看到；Context 只影响模型输出。把核心 state 只放自然语言 context 中会导致不可恢复和不可验证。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-04. 长上下文里怎么保证关键约束不被“淹没”？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

关键约束要结构化并分层放置，而不是期待模型在几十万 token 中自己找到。优先把当前目标、硬约束、状态和最近观察放在高权重/近端位置。

### 3. 深入原理：从概念讲到机制

可用“immutable constraints + task state + working set + retrieved evidence + recent turns”的层次。长材料只保引用，需要时按需展开；对关键 ID、日期、权限、用户确认做字段化提取，不能只依赖摘要。

* 关键约束要分层重复但不冗余：硬约束放 System/Policy 和 Runtime，当前任务约束放结构化 state，必要时在每轮 context 末尾做 compact reminder。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 不要依赖“放在最前面就不会忘”。长上下文中关键字段应结构化并可验证，例如 max_budget、deadline、forbidden_actions。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-05. 摘要压缩会丢关键细节，怎么解决？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

摘要只压“叙述”，关键事实和执行状态要单独抽取保存；采用 layered summary + structured facts + artifact refs。

### 3. 深入原理：从概念讲到机制

每次压缩前提取 stable facts、open loops、decisions、IDs、user preferences、tool results references；摘要可以更新，但这些结构化字段有自己的生命周期。重要原文用 pointer 保留，必要时重新取回。

* Summary 不是事实数据库。要保留 provenance：关键事实链接到原消息/Artifact；高风险事实（金额、日期、用户确认）不只存在摘要中。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 可以定义“不可压缩字段”或 pinned facts；其余历史才由 LLM summary。恢复时能从 source pointer 回看原始证据。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-06. Rolling Summary、分段 Summary 和混合方案怎么选？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

短会话可 rolling；长任务/多主题更适合 topic/episode summaries + 一个全局索引，避免滚动摘要反复重写造成信息漂移。

### 3. 深入原理：从概念讲到机制

Rolling Summary 简单但每次重写会累积损失；分段 Summary 保留阶段边界，回溯更容易；混合方案用全局简短摘要指向多个阶段摘要。

* Rolling Summary 简单但容易累积误差；分段 Summary 可追溯但 context 组装复杂；混合方案通常最好：长期章节摘要 + 最近滚动摘要 + raw recent turns。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 摘要更新要记录 source range/last_archived，避免同一消息重复总结或遗漏。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-07. 长期记忆是每轮都写吗？如何做 admission、去重和更新？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

长期记忆必须有准入门槛：稳定、未来有用、用户相关、可信；每轮全写会把噪声永久化。

### 3. 深入原理：从概念讲到机制

Memory write pipeline 可做候选抽取→重要度/稳定性判断→相似记忆检索→merge/update→版本和来源记录。临时情绪、一次性 Tool 结果通常不进入长期记忆。错误记忆要可纠正，不能简单 append。

* Memory write 必须经过 admission：稳定性、未来价值、敏感性、是否已存在、可信来源。一次性的“我今天有点累”通常不值得长期记忆。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 更新采用 upsert/version，而不是无限 append。偏好变化要有时间和置信度，避免旧偏好长期污染。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-08. 什么时候才去检索长期记忆？每轮都检索有什么问题？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

做 Memory Retrieval Router：只有当前问题依赖历史偏好、过去决策、长期关系或前次任务时才检索；否则不引入无关记忆噪声。

### 3. 深入原理：从概念讲到机制

判断信号包括代词/历史引用（“上次”“还是那个”）、个性化需求、缺少关键当前信息但可能在历史里、明确跨会话 continuation。可先用规则+轻量 classifier，再根据召回置信度决定是否注入。

* Memory Retrieval 应按需要触发：用户显式引用过去、需要个性化、当前任务与历史项目关联。每轮都搜会增加噪声、成本和隐私暴露。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* Memory Router 可以先判断需要哪些 memory namespace，再检索 TopK；结果仍应做权限和相关性过滤。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-09. 用户频繁切换话题，记忆怎么设计才不会接不上？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

不要只按时间线管理；建立 topic/episode id，让每个话题保留摘要、关键实体和 artifact，用户回到旧话题时按主题召回。

### 3. 深入原理：从概念讲到机制

可用 topic detection 将 turn 归到 conversation threads，当前 context 以活跃 topic 为主，同时保留 global user constraints。一个新问题同时匹配多个 topic 时再做澄清。

* 需要区分 conversation thread 与 user memory。话题切换时 recent context 应快速衰减旧主题，但稳定用户偏好可以跨主题保留。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 可维护 topic_id/thread_id，summary 按 topic 分段；新话题默认不把旧任务 state 混入，除非显式引用。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-10. 用户偏好、事实记忆、系统状态冲突时听谁的？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

先定义事实来源优先级：系统/业务真实状态 > 当前用户明确指令 > 已确认长期偏好 > 模型推断。不同类型的信息不能同权覆盖。

### 3. 深入原理：从概念讲到机制

例如长期记忆写“偏好经济舱”，但当前用户说“这次商务舱”，当前指令优先；记忆写“订单未支付”，但订单系统显示已支付，业务事实优先。每条 memory 最好带 source、timestamp、confidence、scope。

* 定义权威层级：实时业务状态/用户当前明确指令 > 近期可验证事实 > 旧 memory/偏好 > 模型推断。冲突必须可解释并更新 memory。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run_id / step_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 05-11. 什么叫 Memory Hallucination？怎么和 LLM Hallucination 区分？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否理解 Context、Memory、Session、State 是不同层次：什么应该持久化、什么只供模型本轮查看、什么能被总结、什么必须作为事实保留，以及长期对话如何在 token 预算内保持正确性。

### 2. 核心结论

LLM hallucination 是生成阶段编造；Memory hallucination 是系统写入、召回或合并了错误/过期记忆，随后模型“基于错误证据认真回答”。

### 3. 深入原理：从概念讲到机制

后者更危险，因为错误会跨会话传播。治理要做 source provenance、TTL/version、conflict resolution、业务事实不写入软记忆、回收过期 memory，以及评估“错误记忆使用率”。

* Memory Hallucination 是系统错误保存/召回了并不存在或已过期的“用户事实”，之后模型把它当真；普通 LLM Hallucination 是当轮生成错误。前者会跨轮传播，危害更持久。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* Memory 必须保存 provenance、timestamp、confidence、source type，并允许失效/纠正。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 把完整历史每轮原样塞给模型。
* 把摘要当事实源，丢失可追溯证据。
* 长期记忆每轮都写、每轮都搜，造成噪声和错误强化。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---
