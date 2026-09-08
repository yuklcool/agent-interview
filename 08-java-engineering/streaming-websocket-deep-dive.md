# Agent Streaming 深挖：真正难的不是 Token 流，而是 Run/Event 协议

## 面试题

> Agent 流式输出用 SSE 还是 WebSocket？Tool Call、用户中途改口、恢复、取消这些事件怎么设计？前端如何避免旧 Run 的迟到消息污染当前界面？

---

## 1. 面试官真正考什么

很多回答停在：

```text
SSE 单向，WebSocket 双向。
```

这只是网络协议基础。

真正的 Agent Streaming 要解决：

- 文本增量
- Tool 生命周期
- 进度事件
- 用户中途追加要求
- 取消
- Human-in-the-Loop
- Recovery
- 断线重连
- 顺序和去重
- 多 Run 并发

因此核心不是 transport，而是**事件模型**。

---

## 2. 不要把 Agent Stream 设计成“字符串流”

错误：

```text
"我"
"查"
"到"
"了"
```

一旦出现 Tool Call，前端不知道：

- 当前文本是不是结束
- Tool 正在执行还是完成
- 下一段文本属于哪个 Round
- 用户是否还能取消

正确做法是事件流：

```text
run.started
message.segment.started
message.delta
tool.call.created
tool.call.running
tool.call.completed
message.segment.started
message.delta
run.completed
```

---

## 3. 一个推荐事件 Envelope

```json
{
  "event": "tool.call.completed",
  "trace_id": "trace-1",
  "run_id": "run-42",
  "turn_id": "turn-9",
  "seq": 31,
  "timestamp": "2026-09-08T10:30:00+08:00",
  "payload": {
    "tool_call_id": "tc-3",
    "tool": "query_alarm",
    "status": "SUCCESS"
  }
}
```

### 为什么要这些字段

`run_id`：隔离不同执行。

`turn_id`：用户一轮消息的逻辑边界。

`seq`：排序、去重和断线恢复。

`trace_id`：和后端 OTel 对齐。

`tool_call_id`：把 Tool lifecycle 串起来。

---

## 4. 前端应该是状态机，不是 append string

推荐状态：

```text
IDLE
 ↓
RUNNING
 ├─ STREAMING_TEXT
 ├─ WAITING_TOOL
 ├─ WAITING_USER
 ├─ RECOVERING
 └─ CANCELLING
 ↓
COMPLETED / FAILED / CANCELLED
```

每种事件只能触发合法状态迁移。

例如：

```text
tool.call.created
  RUNNING → WAITING_TOOL

tool.call.completed
  WAITING_TOOL → RUNNING
```

如果当前 Run 已经 `CANCELLED`，晚到的 `message.delta` 应该丢弃。

---

## 5. 为什么一定要 `seq`

WebSocket 在单连接内通常有消息顺序，但业务系统里事件可能来自：

```text
LLM streaming task
Tool task
Recovery task
Java downstream callback
```

如果多个异步生产者直接向 socket 写，业务顺序仍然可能乱。

所以建议由一个 Session/Run Event Dispatcher 统一分配递增 `seq`。

前端保存：

```text
last_seq = 31
```

收到 31：重复，丢弃。
收到 33：发现 gap，可请求 replay 32~33 或刷新 run snapshot。

---

## 6. 断线重连怎么做

不要认为 WebSocket 断开就等于 Run 结束。

Run 应该是服务端独立状态：

```text
Socket Connection
≠
Agent Run
```

断线后 Agent 可以继续执行。

客户端重连：

```json
{
  "action":"resume",
  "run_id":"run-42",
  "last_seq":31
}
```

服务端：

```text
有 Event Log → replay seq > 31
没有完整 Event Log → 返回 current snapshot + latest seq
```

因此事件最好短期持久化到 Redis Stream/DB/Event Store，而不只存在 socket 内存。

---

## 7. 用户中途改口怎么建模

用户原来：

> 找最早航班。

Tool 正在跑，用户又说：

> 改成最便宜。

有两种语义：

### New Turn

旧 Run 停止/结束，用户消息开启新 Turn。

### In-Run Injection

把新消息注入当前 Run，让 Agent 在下一安全边界看到。

两者必须协议显式区分：

```json
{"action":"send_message","mode":"new_turn",...}
```

或：

```json
{"action":"inject","target_run_id":"run-42",...}
```

不要让后端靠时间猜。

---

## 8. nanobot 的 Injection 对前端意味着什么

nanobot `AgentRunner` 有 `injection_callback` / `terminal_injection_callback`，允许在运行边界 drain pending user messages。

因此 WebSocket 层可以：

```text
收到 follow-up
  ↓
durably journal
  ↓
进入 pending injection queue
  ↓
AgentRunner 在安全边界 drain
  ↓
追加为 user message
```

但前端还要知道：

```text
该消息已经 received
还是已经 injected
还是已经 applied 到新 plan
```

所以最好有：

```text
user.followup.accepted
user.followup.injected
plan.revised（如果上层有 Planner）
```

---

## 9. Tool 事件为什么不能只发“开始/结束”

更完整：

```text
tool.call.created
    模型提出 Tool Call

tool.call.authorizing
    Runtime 权限/Schema 检查

tool.call.running
    真正外部执行

tool.call.completed

tool.call.failed

tool.call.unknown
```

尤其 `unknown` 很重要：副作用 Tool timeout 时前端不能展示红色“失败”然后鼓励用户重试，而应该显示：

> 正在确认实际执行状态。

---

## 10. Human-in-the-Loop 怎么走流式协议

模型提出高风险 Tool：

```text
refund 1000
```

Runtime 不执行，发：

```json
{
  "event":"approval.required",
  "payload":{
    "approval_id":"a1",
    "action":"refund",
    "summary":"退款 1000 元",
    "expires_at":"..."
  }
}
```

前端确认：

```json
{
  "action":"approval.respond",
  "approval_id":"a1",
  "decision":"approve"
}
```

这里需要防：

- 重复点击
- 过期 approval
- approval 属于旧 run
- 参数在确认后被模型修改

因此 approval 必须绑定 action hash / tool_call_id。

---

## 11. Cancel 到底取消什么

用户点 Stop，可能需要取消：

```text
LLM streaming
pending Tool
subagent tasks
future retries
```

但已经进入外部系统的副作用 Tool 不一定能取消。

所以 Cancel 不是事务回滚。

```text
cancel requested
   ↓
stop new model/tool scheduling
   ↓
cancel cancellable tasks
   ↓
正在执行的 side-effect Tool
   └→ UNKNOWN / reconcile
```

前端不能把 `CANCELLED` 解释成“所有业务动作都没发生”。

---

## 12. Java Gateway 怎么实现单写者事件流

推荐：

```text
RunEventBus
   ↓
per-run serial dispatcher
   ↓
assign seq
   ↓
Redis Stream / short event log
   ↓
WebSocket Session(s)
```

模型线程、Tool callback 不直接写 socket，只提交 Event：

```java
runEventBus.publish(runId, event);
```

Dispatcher 统一排序。

这样更容易实现多浏览器/多端订阅同一个 Session。

---

## 13. SSE 什么时候仍然更适合

如果产品只是：

```text
用户发请求
→ 服务端流式返回文本
```

没有中途 Tool UI、取消、HITL、Injection，SSE 更简单，也更容易经过传统 HTTP infra。

所以不要说 WebSocket 永远比 SSE 高级。

选择：

```text
单向结果流 → SSE
双向长生命周期交互 → WebSocket
```

---

## 14. 观测指标

Agent Streaming 要监控：

```text
TTFT
first meaningful token
stream duration
socket disconnect rate
resume success rate
event lag
seq gap rate
tool waiting time
approval waiting time
cancel convergence time
```

Token 流畅不代表体验好；用户经常真正卡在 Tool 等待阶段。

---

## 15. 1～2 分钟面试口述版

> Agent Streaming 我不会只设计成 token delta，而会做成一个带 run_id、turn_id、seq、tool_call_id 的事件协议。前端按状态机消费 `run.started、message.delta、tool.call.*、approval.required、recovery.required、run.completed`，这样 Tool、HITL、取消和恢复都有明确语义。WebSocket 适合我们这种双向场景，因为用户可能在 Run 中追加要求或确认动作；SSE 更适合单向文本流。服务端 Run 和 Socket 要解耦，断线后 Run 可以继续，重连根据 last_seq replay 或返回 snapshot。所有异步任务不直接写 socket，而进入 per-run event dispatcher 统一编号，防止乱序和旧 Run 迟到消息污染当前 UI。nanobot 本身已经有 injection/recovery 相关 Runtime 能力，上层 WebSocket 协议要把这些状态显式暴露给前端。
