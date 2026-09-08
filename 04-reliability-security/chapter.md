# 04. 容错、安全、幂等与 Recovery

> 本章共 12 个专题。每题按“原理 → 工程 → nanobot/Java → 失败边界 → 面试表达”组织。

## 04-01. 场景：模型说“退款成功”但支付网关实际超时，怎么防业务幻觉

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

业务事实必须由状态机/支付系统定义，LLM 只能解释，不能把 UNKNOWN 写成 SUCCESS。

### 3. 深入原理：从概念讲到机制

退款状态至少要区分 INIT、SUBMITTED、SUCCESS、FAILED、UNKNOWN。支付网关超时时，Tool Result 返回 UNKNOWN + request\_id，而不是 success。之后通过业务单号/幂等键查询真实状态；如果实际成功就收敛到 SUCCESS，如果没执行才允许安全重试。异步回调、Outbox/消息表、定时对账可保证最终一致性。

* 业务事实必须由支付/订单状态机定义。网关 timeout 意味着“客户端不知道结果”，不是失败，更不是成功。正确状态是 UNKNOWN，并用 request\_id/idempotency key 查询真实状态。

```
refund request→timeout→UNKNOWN
                   ↓
            query by request_id
          ↙ SUCCESS  ↓ FAILED  ↘ UNKNOWN
      告知成功   可重试判断    等待/人工
```

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 强类型 ToolResult：status=SUCCESS/FAILED/UNKNOWN，只有 SUCCESS 才允许最终文案出现“已退款”。对 UNKNOWN 可进入异步对账/回调。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

Agent Tool 层返回强类型结果，模型只根据 status 生成自然语言。真正安全边界在代码：只有 status==SUCCESS 才允许输出“退款成功”；UNKNOWN 时只能说“请求已提交但当前无法确认结果”。这和 nanobot 的 interrupted Tool 思路一致：Runtime 不确定时宁可 UNKNOWN，也不能自己猜。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 7. 场景推演

```
refund()
  ↓
支付网关超时
  ↓
Tool Result = UNKNOWN + request_id
  ↓
Agent：不能说成功
  ↓
query_refund_status(request_id)
  ├─ SUCCESS → 告知成功
  ├─ FAILED  → 告知失败
  └─ UNKNOWN → 继续等待/人工
```

### 8. 面试官可能继续追问

为什么不能直接 retry？——请求可能已成功但响应丢失，直接重试会重复退款。 Prompt 能解决吗？——只能软约束，最终状态必须由代码层强约束。

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“防这种幻觉不是 Prompt 写‘不要胡说’，而是模型没有业务事实写权限。网关超时只能返回 UNKNOWN，只有支付系统或状态查询确认 SUCCESS 后，Agent 才能对用户说退款成功。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 04-02. Agent 执行到一半进程重启，Session 怎么续跑？工具半成功怎么清理

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

nanobot 恢复的是 runtime checkpoint，不是简单重放聊天历史；不确定 Tool 不自动重放。

### 3. 深入原理：从概念讲到机制

通用理论是 checkpoint + idempotency + reconcile，但必须区分 Runtime 和业务一致性。Runtime 只能知道“Tool 有没有完成并返回”，不能知道外部系统是否已经产生副作用。安全策略应是：未知状态不盲重试，先恢复执行上下文，再由业务幂等/状态查询收敛。

* 恢复必须区分对话恢复和执行恢复。nanobot 当前通过 runtime checkpoint 记录 awaiting\_tools/tools\_completed/final\_response；崩在 Tool 中间时状态是不确定的，恢复逻辑不自动 replay。
* 外部系统是否已产生副作用只能通过业务幂等/状态查询确认。Runtime checkpoint 无法提供分布式 exactly-once。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 副作用 Tool 应携带 business\_request\_id；重试前先查状态。需要跨多个业务系统时再引入 Saga/补偿，而不是让 LLM 自己决定补偿。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot 在模型产生 Tool Call 后、执行前先落 phase=awaiting\_tools ；工具完成后落 tools\_completed ；最终响应落 final\_response 。checkpoint 由 SessionManager 原子写到 .checkpoint.json 。若进程重启时仍是 awaiting\_tools，RecoveryCoordinator 把它视为 tool\_state\_unknown，进入 awaiting\_user；pending Tool Call 会恢复成 interrupted Tool Result，而不是直接 execute。用户确认 Continue 后，才通过 MessageBus 注入内部 continuation 重新进入 Agent Loop。业务级“订单其实已成功”仍需要 Tool 自己做 idempotency key / business\_request\_id / query status；nanobot 没有通用 Saga/Compensation 引擎。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 7. 场景推演

```
LLM 返回 Tool Call
      ↓
checkpoint: awaiting_tools
      ↓
execute_tool_calls()
      ├─ 正常完成 → tools_completed → 下一轮 LLM
      └─ 进程崩溃
            ↓
        重启 Recovery
            ↓
     tool_state_unknown / awaiting_user
            ↓
     不自动 replay Tool
            ↓
   用户 Continue → internal continuation
            ↓
        Agent Loop 继续
责任边界： nanobot 负责“安全恢复 Agent Loop”；业务 Service 负责“副作用一致性、幂等、对账、必要时补偿”。
```

### 8. 面试官可能继续追问

为什么不能自动重试 create\_order/refund？——外部系统可能已经成功但响应没回来。 read-only Tool 能自动 retry 吗？——可按 retry policy 做，但仍要限制次数和 deadline。 nanobot 有 Saga 吗？——没有通用 Saga/Compensation，需要业务工作流补。

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“nanobot 不是把聊天历史重新喂一遍来续跑，而是有 runtime checkpoint。Tool 前写 awaiting\_tools，Tool 完成写 tools\_completed；如果崩在 Tool 中间，恢复时它把状态视为 unknown，不自动重放。用户确认后才继续 Agent Loop。业务侧仍要用幂等键和状态查询解决‘外部其实已成功’的问题。”
源码/工程落点： nanobot/agent/runner.py；nanobot/session/recovery.py；nanobot/session/manager.py
来源：原深度版答案，已在本次总表中重新归类。

---

## 04-03. 场景：机票查询 Tool 返回空，是重试、换参数，还是直接告诉用户没票？决策给模型还是代码

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

代码决定“可执行动作空间和重试边界”，模型决定“在允许范围内如何语义调整”。

### 3. 深入原理：从概念讲到机制

先把 Tool Result 分类：FOUND / NO\_RESULT / INVALID\_ARGUMENT / RETRYABLE\_ERROR / HARD\_ERROR。网络超时等 RETRYABLE\_ERROR 可由代码按指数退避有限重试；NO\_RESULT 不应重复相同参数；模型可以在允许范围内扩大机场、日期、舱位，或者向用户澄清。代码还要控制最大调用次数、总 deadline、预算。

* 必须区分 NO\_RESULT 和 ERROR。相同参数的 NO\_RESULT 不应盲重试；timeout/503 属于 RETRYABLE\_ERROR 才适合有限重试。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 代码控制 retry/deadline/budget，模型只在允许 action space 中决定“换日期/机场/条件/询问用户”。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot execution 层把 Tool 结果/异常转成 observation；还有 repeated external lookup guard，重复相同外部查询会被阻止。所以机票 Tool 最好返回结构化原因，例如 no\_inventory / invalid\_date / provider\_timeout，帮助模型做不同策略。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 7. 场景推演

```
Tool Result
 ├─ RETRYABLE_ERROR → code retry (有限)
 ├─ INVALID_ARGUMENT → 修正参数/让模型修
 ├─ NO_RESULT → 模型换搜索策略/询问用户
 ├─ HARD_ERROR → 直接失败/降级
 └─ FOUND → 聚合返回
```

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“重试策略属于 Harness/代码，参数替代属于模型决策，但模型必须在代码允许的 action space 和 budget 里行动，不能无限重试同一查询。”
源码/工程落点： nanobot/agent/tools/execution.py；nanobot/utils/runtime.py
来源：原深度版答案，已在本次总表中重新归类。

---

## 04-04. 模型升级后整体答对率涨了但工具调用乱序，怎么在不回滚模型的前提下修

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

把关键顺序从“模型习惯”升级成“可执行约束”，不要靠 Prompt 记忆。

### 3. 深入原理：从概念讲到机制

先用 trace 找出乱序模式。对于强依赖动作，用 precondition/state/tool policy 拦截，例如 payment 只能在 quote\_confirmed 后执行。Prompt/few-shot 只能软引导；真正必须的顺序应进入 Harness/DAG。这样保留模型质量收益，同时修复执行可靠性。

* 如果顺序是业务必需，就不应该依赖模型“记住”。把顺序升级为 executable precondition/state transition。模型升级后即使行为分布变化，硬约束仍然不变。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run\_id / step\_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

例如新模型先 book 再 quote，Tool Dispatcher 在 book\_ticket 前检查 state==CONFIRMED，否则返回 structured error requires confirmed quote 。短期可优化 Tool description，长期把关键流程做显式 workflow。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“模型升级暴露了 Harness 里原本靠模型自觉维护的隐含顺序。正确修法是把隐含依赖变成显式 precondition/状态机，而不是回滚一个整体更好的模型。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 04-05. Agent 调错工具可能删除数据，怎么防止“模型一次判断错误=生产事故”？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

把模型权限限制为“提出动作”，真正执行必须经过 Policy、Scope、Risk、Confirmation、Idempotency 等代码门禁。

### 3. 深入原理：从概念讲到机制

高风险 Tool 应有 risk\_level、requires\_confirmation、allowed\_roles、allowed\_tenants、preconditions。删除/支付类还可采用 dry-run→展示影响→人工确认→短时授权 token→执行→审计。Prompt 只能降低误调用概率，不能作为安全边界。

* 高风险 Tool 需要 defense in depth：不可见/最小权限、执行时 policy、参数白名单、dry-run、用户确认、幂等、审计、Sandbox。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* delete\_\* 最好改成软删除/回收站或“prepare→confirm→commit”两阶段，避免单次模型输出直接造成不可逆后果。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 04-06. Prompt Injection 怎么防？尤其是 RAG/网页里带恶意指令时。

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

核心是区分“数据”和“指令”，并在代码层限制能力；不能靠“告诉模型忽略恶意内容”作为唯一防线。

### 3. 深入原理：从概念讲到机制

防线包括：来源分级和内容隔离、工具最小权限、禁止未授权数据外传、危险参数校验、URL/路径白名单、输出编码、敏感操作 HITL、检索内容标注为 untrusted data。还要用对抗样本做回归评测。

* 核心原则是把“数据”和“指令”分开。来自网页/RAG 的内容默认是不可信数据，不能获得更高指令优先级。
* 防护层包括内容标记/隔离、工具最小权限、敏感数据不默认进上下文、输出/Tool Call policy、URL/SSRF 控制、可疑内容检测。没有单一 Prompt 可以彻底解决。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run\_id / step\_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 04-07. Tool Failure 应该怎么分类，重试策略怎么定？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

至少分 INVALID\_INPUT、EMPTY/NO\_RESULT、RETRYABLE、RATE\_LIMIT、TIMEOUT\_UNKNOWN、HARD\_ERROR、POLICY\_DENIED；不同类型的处理完全不同。

### 3. 深入原理：从概念讲到机制

网络瞬时错误可指数退避；参数错误可让模型修一次；空结果不是失败，不应原样重复；副作用请求超时可能是 UNKNOWN，必须查状态而不是直接 retry；Policy denied 不允许通过换工具绕过。

* 错误分类建议至少：INVALID\_ARGUMENT、BUSINESS\_REJECTED、AUTH/POLICY、RETRYABLE\_INFRA、TIMEOUT\_UNKNOWN、HARD\_ERROR。每类对应不同动作。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* retry policy 要考虑幂等性、side\_effect、deadline、backoff/jitter、最大次数。对 UNKNOWN 的副作用调用优先 reconcile，不直接 retry。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 04-08. Self-Reflection 连续失败怎么办？为什么不能无限反思？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

Reflection 也是概率模型调用，会耗成本且可能在同一个错误模式里打转；必须有次数、错误签名和降级策略。

### 3. 深入原理：从概念讲到机制

常见做法：第一次自修复，第二次换策略/模型，第三次收集最小诊断信息后停止或转人工。若连续输出相同 Tool/参数或相同 error hash，直接触发 circuit breaker。

* Reflection 本质是额外模型调用，不能假设一定提升。连续失败可能是信息缺失、Tool 错、Prompt 错或任务不可达；继续反思只会烧 token。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 设 reflection\_budget，连续两次没有产生新 evidence/plan change 就停止，切换策略、升级模型或人工。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 04-09. 如何限制 Agent 的推理深度、Tool 次数和递归层级？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

Budget 必须是 Runtime 的一等公民：step、token、wall-clock、tool-call、subagent-depth、money 都要有上限，并支持动态收紧。

### 3. 深入原理：从概念讲到机制

预算不能只设一个 max\_steps。复杂任务可以根据风险和用户等级分配不同 budget；每轮估算 remaining budget，若剩余不足则强制进入 summarize/ask-user/fail-safe。对子 Agent 还要把父任务预算切片，避免递归扩散。

* 需要多维 Budget：max\_iterations、max\_tool\_calls、max\_subagent\_depth、token\_budget、wall\_clock\_deadline、cost\_budget。单一“最多 10 轮”不足以防失控。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 预算应由任务风险/价值决定，并在 Trace 中记录 stop\_reason，方便分析是成功停止还是预算耗尽。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 04-10. NL2SQL 的安全防护应该做到哪几层？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

把 NL2SQL 当“受限查询编译器”，不是让模型拿数据库账号自由执行。最少要有只读账号/事务、SQL AST 校验、表列白名单、行级权限、LIMIT/timeout 和审计。

### 3. 深入原理：从概念讲到机制

不要只用正则禁止 DROP/DELETE，CTE、函数、子查询都可能绕过。建议 parse SQL AST，拒绝 DDL/DML、多语句、危险函数；把 user/tenant scope 通过 RLS、secure view 或查询重写强制加入；执行前 EXPLAIN/成本限制避免扫库。

* 安全应至少五层：Schema/表列可见性、SQL AST 解析、只读/语句类型限制、行级/租户权限、执行资源限制。不能只靠 Prompt 写“禁止 DELETE”。
* 多表权限尤其不能只看单表。真正的用户数据范围应由数据库 RLS、视图、受控 Service 或 SQL 重写层强制注入。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 执行前 EXPLAIN/成本估算、LIMIT、statement\_timeout、只读账号；执行后审计 query/user/session。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 04-11. 高风险操作什么时候必须 Human-in-the-Loop？怎么避免把用户体验做得很差？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

不是所有 Tool 都确认；只对不可逆、高金额、权限提升、批量影响、敏感数据外发等动作做确认，并把确认放在“参数都确定、影响可解释”的最后一步。

### 3. 深入原理：从概念讲到机制

确认卡应展示动作、对象范围、关键参数、影响/风险、幂等 request\_id；用户确认后签发一次性/短时 action token，防止旧确认被复用。低风险查询和可撤销动作不要频繁打断。

* HITL 不是所有操作都弹确认，而是基于 risk × reversibility × financial/privacy impact。低风险可自动，高风险必须确认，不确定状态也可转人工。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 确认页面应展示“将做什么、影响对象、关键参数、为什么”，确认 token 必须绑定具体 action hash，防止用户确认后模型换参数。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 04-12. Agent 幻觉怎么做全链路治理？RAG 能不能彻底解决？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你能不能把“概率模型”放进有副作用的生产系统。核心不是 Prompt 写得更严，而是状态机、幂等、重试、UNKNOWN、HITL、权限、安全边界、恢复与对账。

### 2. 核心结论

RAG 只能补证据，不能消除幻觉。治理要覆盖输入/检索、模型生成、Tool/业务状态和输出验证四层，并按风险决定是否允许模型自由回答。

### 3. 深入原理：从概念讲到机制

事实问答做引用和 groundedness；实时业务事实必须 Tool 查询；高风险状态用强类型结果/状态机；不确定状态只能 UNKNOWN；输出可做 rule/grader 检查。训练/Prompt 可以降低概率，但最终安全边界必须在代码。

* 全链路治理要区分知识幻觉、工具事实幻觉、状态幻觉和 memory hallucination。不同类型用不同机制：RAG/引用、强类型 ToolResult、状态机、memory provenance。
* RAG 只能降低知识缺失导致的幻觉，无法解决错误 Tool、过期数据、业务状态不确定或模型错误归纳。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run\_id / step\_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 对有副作用 Tool 直接自动 retry。
* 把超时解释成失败或成功，而不是 UNKNOWN。
* 依赖 Prompt 防越权，没有后端强校验。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---
