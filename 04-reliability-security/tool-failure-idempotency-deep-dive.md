# Tool Failure、幂等、UNKNOWN：Agent 可靠性的真正分水岭

## 面试题

> Tool 调用失败怎么分类？什么时候重试？为什么副作用 Tool 超时不能直接标失败？幂等、对账、补偿分别解决什么？

---

## 1. 面试官真正考什么

这道题在考你有没有理解：**Agent Tool 不是普通函数调用，它可能跨网络、跨进程、跨业务系统，还可能产生真实副作用。**

最危险的误区是：

```text
try
  call tool
catch
  retry 3 times
```

对查询 Tool 可能没问题，对退款、支付、发消息、创建工单就可能制造重复副作用。

---

## 2. Tool Failure 应该先分类，而不是先决定 retry

推荐至少分：

```text
INVALID_ARGUMENT
PERMISSION_DENIED
NOT_FOUND / NO_RESULT
RETRYABLE_ERROR
HARD_ERROR
TIMEOUT
UNKNOWN
CANCELLED
```

### INVALID_ARGUMENT

参数缺失、类型错误、enum 错。通常应该让模型修参数，不能盲重试原请求。

### PERMISSION_DENIED

权限边界，必须终止该动作，不能换个 Tool 绕过。

### NO_RESULT

不是“错误”，业务上可能需要换条件、澄清或明确告诉用户无结果。

### RETRYABLE_ERROR

429、临时 5xx、网络抖动，满足幂等条件时可以有限退避重试。

### HARD_ERROR

明确业务失败，例如订单状态不允许退款，不应重试。

### TIMEOUT / UNKNOWN

最关键。Timeout 只是“调用方没有在期限内拿到明确结果”，不代表外部系统没有执行。

---

## 3. 为什么 TIMEOUT 和 FAILED 不一样

假设：

```text
Agent Runtime
  ↓ POST /refund
Payment Service
  ↓
退款成功，写库完成
  ↓
返回响应途中网络断开
```

Runtime 看到：

```text
TimeoutException
```

Payment Service 真实状态：

```text
SUCCESS
```

如果 Runtime 把 timeout 直接标 FAILED，再自动重试：

```text
退款 100
退款 100
```

就会重复副作用。

所以对于“请求可能已经到达外部系统”的副作用操作：

```text
TIMEOUT
  ↓
UNKNOWN
  ↓
RECONCILE
```

---

## 4. 幂等到底是什么

幂等不是“接口支持重试”这句口号，而是**同一个业务意图执行多次，最终业务结果仍然等价于执行一次**。

例如创建工单：

```text
business_request_id = RUN123-STEP5
```

第一次：

```text
RUN123-STEP5 → create WO1001
```

第二次相同 ID：

```text
RUN123-STEP5 → return existing WO1001
```

而不是 WO1002。

数据库里可以有唯一约束：

```sql
UNIQUE(tenant_id, business_request_id)
```

服务端逻辑：

```text
查幂等记录
  ├─ SUCCESS → 返回旧结果
  ├─ PROCESSING → 查询/等待
  ├─ FAILED_RETRYABLE → 按策略重试
  └─ 不存在 → 尝试创建
```

---

## 5. idempotency key 不能只存在 Agent 内存里

如果 key 只存在当前进程：

```text
进程重启 → key 丢失 → 重复执行
```

它必须被业务系统或可靠持久层识别。

推荐 key 来源：

```text
business_request_id
= hash(tenant + run_id + step_id + logical_action)
```

不要用随机 UUID 每次重试都重新生成，否则服务端看不出是同一个动作。

---

## 6. Reconcile：UNKNOWN 怎么收敛

每个重要副作用 Tool 最好提供一个查询接口：

```text
refund(order_id, request_id)
query_refund_status(request_id)
```

恢复逻辑：

```text
UNKNOWN
  ↓
query status by request_id
  ├─ SUCCESS     → 收敛为 SUCCEEDED
  ├─ NOT_FOUND   → 可以安全重试
  ├─ PROCESSING  → 等待/轮询
  └─ UNKNOWN     → 人工处理/异步对账
```

这比“失败就 retry”成熟得多。

---

## 7. Retry Policy 怎么设计

至少需要：

```text
max_attempts
backoff
jitter
retryable_error_types
deadline
idempotent flag
side_effect flag
```

查询 Tool：

```text
GET weather
429 → exponential backoff + jitter
```

副作用 Tool：

```text
POST refund
network timeout → 不直接 retry，先 reconcile
```

### 为什么要 jitter

大量请求同时失败，如果都在 1s、2s、4s 重试，会形成 thundering herd。Jitter 把重试时间打散。

---

## 8. Deadline 比 retry 次数更重要

如果：

```text
max retries = 5
```

但用户整轮 SLA 只有 10 秒，每次 Tool timeout 3 秒，根本不可能完整重试 5 次。

所以实际 timeout：

```text
remaining = run_deadline - now
attempt_timeout = min(tool_timeout, remaining)
```

重试必须服从全局 budget。

---

## 9. Compensation 和 Idempotency 不是一回事

### Idempotency

解决：同一个动作重复执行不要产生重复副作用。

### Compensation

解决：多个已经成功的动作组成的长事务，后续失败后如何撤销/补偿前面结果。

例如：

```text
Lock Inventory   SUCCESS
Create Order     SUCCESS
Payment          FAILED
```

补偿：

```text
Cancel Order
Release Inventory
```

这属于 Saga/Workflow 层。

所以：

```text
幂等 ≠ 分布式事务
```

---

## 10. Compensation 也可能失败

不要以为调用 `cancel_order()` 就结束。

补偿本身也要有状态：

```text
COMPENSATION_PENDING
RUNNING
SUCCEEDED
FAILED
MANUAL_REQUIRED
```

对账任务要能发现“主流程失败 + 补偿未完成”的悬挂状态。

---

## 11. Agent Runtime 与业务系统的责任边界

```text
┌────────────────────────────┐
│ Agent Runtime              │
│ timeout/error classify     │
│ retry budget               │
│ checkpoint                 │
│ UNKNOWN                    │
│ no blind replay            │
└─────────────┬──────────────┘
              ↓
┌────────────────────────────┐
│ Business Service           │
│ idempotency key            │
│ business state machine     │
│ transaction                │
│ status query/reconcile     │
│ compensation/Saga          │
└────────────────────────────┘
```

Runtime 不能凭空保证 Exactly-once，因为真实副作用发生在业务系统。

---

## 12. nanobot 当前真实实现怎么讲

nanobot 的 Recovery 对 `awaiting_tools` 很谨慎：如果进程中断在 Tool 执行阶段，它不会自动 replay pending Tool，而会把它视为不确定状态，恢复成 interrupted Tool Result，并等待恢复流程继续。

这解决的是：

```text
Runtime 不盲目重放
```

但 nanobot 不可能知道外部支付/订单系统真实是否已经成功。

所以企业级 Tool 仍然需要：

```text
business_request_id
idempotency
query_status
reconcile
```

不要把 Runtime Recovery 和业务 Exactly-once 混为一谈。

---

## 13. 一个 ToolResult Contract 示例

```json
{
  "status": "UNKNOWN",
  "tool_call_id": "tc-123",
  "business_request_id": "run1-step4",
  "retryable": false,
  "reconcile_required": true,
  "error_kind": "NETWORK_TIMEOUT",
  "message": "Request may have reached payment gateway",
  "data": null
}
```

模型看到这个 observation 后，只能说：

> 当前无法确认退款是否成功，系统正在核验。

不能把 UNKNOWN 解释成 SUCCESS。

---

## 14. 面试常见追问

### “查询 Tool 也需要幂等吗？”

通常没有副作用，所以主要关心缓存和 retry；但如果查询接口内部会刷新状态/触发计费，也要重新评估。

### “数据库事务能不能解决所有问题？”

不能，数据库事务只覆盖单数据库事务边界，跨支付、MQ、第三方 API 仍需要幂等、Outbox、Saga 等。

### “怎么避免模型无限换 Tool 重试？”

Runtime 维护 retry budget、external lookup count、max iterations，达到上限后必须收敛到澄清/降级/失败。

---

## 15. 1～2 分钟面试口述版

> 我会先把 Tool Failure 分类，而不是一出错就 retry。参数错让模型修，权限错直接阻断，临时 429/5xx 对幂等查询可以有限退避重试。最关键的是副作用 Tool：支付、退款、创建工单出现 timeout 时，timeout 只说明本地没拿到结果，外部可能已经成功，所以状态应该进入 UNKNOWN，而不是 FAILED。之后用稳定的 business_request_id 查询外部真实状态，确认 NOT_FOUND 才允许安全重试。幂等保证同一逻辑动作多次执行不会产生重复副作用，Compensation/Saga 则处理跨步骤部分成功后的回滚，两者不是一回事。nanobot 当前 Recovery 已经做到中断 Tool 不盲目 replay，但业务级 Exactly-once 仍然必须由 Java/支付/订单服务自己通过幂等、状态机和对账保证。
