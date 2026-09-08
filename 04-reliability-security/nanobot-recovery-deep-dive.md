# nanobot Recovery 深挖：进程重启、Checkpoint、UNKNOWN Tool 与副作用一致性

> 目标：回答“Agent 执行到一半进程挂了怎么办”时，不再停留在 `Checkpoint + 幂等` 的概念，而是把 nanobot 当前真实恢复机制、它能保证什么、不能保证什么，以及企业级业务还要补什么讲清楚。

## 面试题

> Agent 执行到一半进程重启，Session 怎么续跑？Tool 已经部分成功但 Runtime 没拿到结果时，如何保证不重复产生副作用？

---

# 一、先分清两个完全不同的问题

```text
Conversation Recovery
恢复“聊到哪里”

Execution Recovery
恢复“执行到哪里”
```

聊天系统只恢复 Conversation 就够了。

但 Agent 可能已经做过：

```text
查库存
 ↓
锁库存
 ↓
创建订单
 ↓
支付
```

此时最危险的不是模型忘了，而是：

> **外部世界已经发生变化，但 Runtime 不确定变化发生到哪一步。**

所以 Agent Recovery 的核心问题是：

```text
“哪些副作用已经发生？”
```

而不是：

```text
“怎么重新把聊天记录喂给模型？”
```

---

# 二、为什么“进程挂了以后把用户问题重放一遍”是错误设计

用户：

> 帮我创建一个工单。

第一次运行：

```text
LLM → create_work_order
            ↓
      Java Service 成功创建 WO-1001
            ↓
      返回 HTTP Response 前进程挂了
```

如果重启后直接：

```text
重新发送用户原问题
```

模型可能再次：

```text
create_work_order
```

于是：

```text
WO-1001
WO-1002
```

所以真正恢复必须建立在：

```text
Durable execution checkpoint
```

而不是只靠 conversation replay。

---

# 三、nanobot 当前的关键 Checkpoint Phase

nanobot 的 Runtime Recovery 使用：

```text
runtime_checkpoint
```

当前关键 phase 包括：

```text
awaiting_tools
tools_completed
final_response
error
```

其中最重要的三个边界：

```text
LLM 返回 Tool Call
      ↓
awaiting_tools
      ↓
执行 Tool
      ↓
tools_completed
      ↓
继续 LLM
      ↓
final_response
```

这三个 phase 的意义不是 UI 状态，而是**副作用安全边界**。

---

# 四、为什么 Tool 执行前必须先写 awaiting_tools

假设模型返回：

```text
create_order(flight_id=MU5101)
```

正确顺序应该是：

```text
1. 记录 assistant tool_call
2. 记录 pending_tool_calls
3. checkpoint phase = awaiting_tools
4. 持久化 checkpoint
5. 真正执行 Tool
```

而不是：

```text
先执行
再保存状态
```

否则进程如果在执行瞬间挂掉，Runtime 连：

> “我刚才准备调用哪个 Tool？”

都不知道。

---

# 五、awaiting_tools 为什么被视为“不确定状态”

这是整个 Recovery 最核心的逻辑。

假设：

```text
checkpoint = awaiting_tools
        ↓
create_order 已经发出
        ↓
订单系统执行成功
        ↓
Runtime 还没写 tools_completed
        ↓
进程崩溃
```

磁盘只能证明：

```text
“这个 Tool 被准备执行了”
```

不能证明：

```text
“Tool 没成功”
```

因此：

```text
awaiting_tools ≠ FAILED
```

更准确是：

```text
UNKNOWN
```

nanobot 的 `session/recovery.py` 明确把：

```text
_UNCERTAIN_TOOL_PHASES = {"awaiting_tools"}
```

视为 uncertain tool phase。

这个设计非常重要，因为它体现的是分布式系统里经典的：

```text
At-least-once / Exactly-once illusion
```

问题。

---

# 六、nanobot 恢复时为什么不自动重放 pending Tool

`restore_runtime_checkpoint()` 的关键行为是：

```text
pending tool call
      ↓
不会 execute
      ↓
转换成 explicit interrupted tool result
```

恢复出来的消息类似：

```json
{
  "role": "tool",
  "tool_call_id": "tc-123",
  "name": "create_order",
  "content": "Error: Task interrupted before this tool finished.",
  "_recovery_interrupted": true
}
```

这句话背后的含义不是：

> Tool 一定失败了。

而是：

> Runtime 没有可信结果，不能把它当成功，也不能安全 replay。

所以 nanobot 做的是：

```text
把“不确定性”显式写回 Context
```

而不是猜。

---

# 七、为什么这是正确的安全策略

对查询类 Tool：

```text
query_weather
query_device
query_alarm
```

自动重试通常没问题。

但对副作用 Tool：

```text
refund
create_order
pay
send_message
create_work_order
```

自动 replay 可能产生重复副作用。

所以 Recovery 默认选择：

```text
Safety > Convenience
```

即：

```text
宁可 UNKNOWN
也不盲目 replay
```

---

# 八、Checkpoint 本身也要做完整性校验

nanobot 当前 Recovery 不是拿到一个 JSON 就无脑 Continue。

`_runtime_checkpoint_is_well_formed()` 会校验：

- `assistant_message` 必须存在且 role=assistant；
- completed tool result 必须有稳定 `tool_call_id`；
- pending tool call 必须有 `id/function/name`；
- tool call IDs 不能重复；
- `awaiting_tools` 时 assistant tool_calls 必须和 pending IDs 完全一致；
- `tools_completed` 时 completed IDs 必须和 assistant tool_calls 对齐；
- `final_response` 时不能残留 tool calls。

为什么需要这么严格？

因为恢复阶段如果“静默丢掉一条 Tool Result”，模型可能误以为没执行，然后再次调用副作用 Tool。

所以恢复数据：

```text
宁可拒绝恢复
也不能猜测修复
```

---

# 九、provider state 为什么不是任何时候都能保留

很多模型 Provider 还有自己的 conversation/cache/state。

但如果 checkpoint 与持久化 transcript 不完全同步，继续使用 provider-native state 可能导致：

```text
模型供应商看到的上下文
        ≠
本地恢复出来的上下文
```

nanobot 当前只有在确认 checkpoint phase 和 provider state 同步时才保留，否则：

```text
session.provider_state = None
```

这说明恢复不是只恢复文本，还要考虑：

```text
Model-side conversation state consistency
```

---

# 十、用户中途 Follow-up 也需要 Durable Journal

nanobot Recovery 里还有一个很容易忽视的设计：

```text
pending_user_followups
```

WebSocket 用户在 Agent 正在运行时发来的 follow-up，不只是塞进内存 queue。

会先持久化 journal：

```text
followup_id
sender_id
chat_id
content
media
metadata
```

为什么？

因为：

```text
用户消息已经被系统确认接收
        ↓
但 Agent 还没来得及把它写进历史
        ↓
Gateway 重启
```

如果只存在内存 queue，用户这条消息就丢了。

所以：

```text
内存 injection queue
≠
Durable follow-up journal
```

这是很典型的 Runtime 工程细节。

---

# 十一、nanobot 能解决什么，不能解决什么

## nanobot 当前解决的是

```text
Runtime Checkpoint
Interrupted Tool Detection
Pending Tool 不自动重放
恢复消息一致性
恢复状态验证
Continuation / 用户确认恢复
Follow-up durable journal
```

## nanobot 当前不能替你解决的是

```text
业务 Exactly-once
订单幂等
支付对账
库存补偿
Saga
分布式事务
业务状态查询
```

这是面试时必须明确区分的边界。

---

# 十二、为什么业务层仍然必须有幂等键

假设 Runtime 最终允许用户 Continue，模型再次决定调用：

```text
create_order
```

业务服务必须支持：

```json
{
  "business_request_id": "run-1001-step-4",
  "flight_id": "MU5101"
}
```

服务端逻辑：

```text
business_request_id 是否已存在？
      ↓
YES → 返回原结果
NO  → 创建并记录
```

于是：

```text
第一次 → ORD001
第二次同 id → ORD001
```

而不是：

```text
ORD002
```

这才是真正把 Recovery 闭环。

---

# 十三、超时后为什么先对账，不直接 retry

支付类 Tool：

```text
POST /refund
      ↓
Timeout
```

Runtime 看见：

```text
TIMEOUT
```

外部支付系统可能已经：

```text
SUCCESS
```

所以状态转换应该是：

```text
TIMEOUT
  ↓
UNKNOWN
  ↓
query_status(request_id)
  ├─ SUCCESS → 收敛成功
  ├─ NOT_FOUND → 允许安全重试
  └─ UNKNOWN → 等待/人工
```

而不是：

```text
TIMEOUT → retry
```

---

# 十四、企业级 Tool 状态机建议

nanobot checkpoint phase 是 Runtime 级别；业务 Tool 还可以有自己的执行状态：

```text
PENDING
  ↓
DISPATCHED
  ↓
RUNNING
  ├─ SUCCEEDED
  ├─ FAILED
  ├─ UNKNOWN
  ├─ CANCELLED
  └─ COMPENSATING
```

为什么区分：

```text
DISPATCHED
```

和：

```text
RUNNING
```

因为请求已经发出但对方是否真正开始执行，在跨服务环境里并不总能知道。

---

# 十五、Compensation 在哪里做

比如：

```text
Reserve Inventory → SUCCESS
Create Order      → SUCCESS
Payment           → FAILED
```

此时可以：

```text
Payment FAILED
      ↓
Compensation Workflow
      ↓
Cancel Order
      ↓
Release Inventory
```

这不是 LLM 自己“想出来再调用”。

应该是：

```text
确定性 Workflow / Saga
```

因为补偿顺序属于业务一致性。

模型最多可以：

```text
解释当前失败状态
建议人工处置
```

不能成为交易补偿事实源。

---

# 十六、Java/Spring 怎么落

建议至少有一张 `agent_tool_execution` 表：

```text
id
run_id
step_id
tool_call_id
business_request_id
tool_name
status
request_payload_hash
response_summary
started_at
finished_at
reconcile_status
retry_count
version
```

配合唯一索引：

```text
UNIQUE(business_request_id, tool_name)
```

如果业务服务是你自己控制的，最好幂等再下沉到真实领域服务。

例如：

```java
@Transactional
public OrderResult createOrder(CreateOrderCommand cmd) {
    var existing = requestRepository.find(cmd.businessRequestId());
    if (existing != null) {
        return existing.toResult();
    }
    // create order + persist request mapping in one transaction
}
```

---

# 十七、场景：城市照明工单创建

Agent：

> 发现 17 个异常设备，帮我生成维修工单。

流程：

```text
LLM
 ↓
create_work_order(device_ids)
 ↓
checkpoint awaiting_tools
 ↓
Java WorkOrderService 创建 WO-2201
 ↓
进程崩溃
```

重启后 nanobot：

```text
看到 awaiting_tools
 ↓
不自动 replay
 ↓
materialize interrupted Tool Result
 ↓
进入 recovery/continuation
```

业务层再根据：

```text
business_request_id
```

查询：

```text
WO-2201 已存在
```

于是继续时直接返回已有工单，不重复创建。

---

# 十八、常见错误

## 错误 1：Session 恢复 = 重放聊天记录

错。Agent 需要 execution recovery。

## 错误 2：超时 = 失败

错。副作用调用超时经常是 UNKNOWN。

## 错误 3：有 checkpoint 就不需要幂等

错。checkpoint 只能说明 Runtime 看到什么，不能保证外部世界 exactly-once。

## 错误 4：让模型决定补偿

高风险业务补偿应该是确定性 Workflow。

## 错误 5：所有 Tool 都自动 retry

read-only 和 side-effect 必须区分。

---

# 十九、面试官继续追问

### Q1：为什么 pending Tool 恢复成 error observation，而不是删掉？

因为 Tool Call 已经是 durable conversation 的一部分。直接删会篡改执行历史；显式 interrupted observation 能让后续模型知道发生了中断。

### Q2：如果 Tool 其实成功了怎么办？

Runtime 无法凭 checkpoint 判断，必须业务对账或幂等查询。

### Q3：如果 checkpoint 自己损坏？

不要猜。恢复校验失败时应进入 review/dismiss/人工，而不是自动补全 Tool Result。

### Q4：为什么用户确认后才能继续？

重启是生命周期边界，自动继续可能在用户不知情的情况下重新触发动作；显式确认更安全。

---

# 二十、2 分钟面试口述版

> nanobot 的恢复不是重新放一遍聊天记录。它会在 AgentRunner 的关键阶段保存 runtime checkpoint，尤其是模型产生 Tool Call 后先进入 `awaiting_tools`，Tool 都执行完成以后再进入 `tools_completed`，最终答案是 `final_response`。如果进程挂在 `awaiting_tools`，恢复时它把这个阶段当成 uncertain state，因为外部 Tool 可能已经成功但结果没回到 Runtime。`restore_runtime_checkpoint()` 不会自动 replay pending Tool，而是把它转成显式的 interrupted Tool Result，再通过 recovery continuation 让用户确认后继续。这个机制解决的是 Runtime 层“不盲目重放”，但业务系统仍然必须用 business_request_id、幂等、状态对账和必要时 Saga 解决副作用一致性。我的理解是：nanobot 负责安全恢复 Agent Loop，业务系统负责外部世界的一致性。

---

## 源码重点

```text
nanobot/session/recovery.py
  - _UNCERTAIN_TOOL_PHASES
  - _runtime_checkpoint_is_well_formed
  - restore_runtime_checkpoint
  - pending follow-up journal

nanobot/agent/runner.py
  - checkpoint_callback
  - awaiting_tools / tools_completed / final_response producer

nanobot/session/manager.py
  - runtime checkpoint durable storage
```
