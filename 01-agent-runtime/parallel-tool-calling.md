# Parallel Tool Calling 深挖：并行、依赖链、超时、部分成功与调度正确性

## 面试题

> 工具调用中的并行调用（Parallel Tool Calling）与依赖链调用如何设计调度引擎？当其中某个工具超时时，如何保证整体执行流的正确性？

---

# 一、面试官真正考什么

这道题表面在问“并行”，其实是在考你有没有真正设计过**Agent 执行调度器**。

如果只回答：

```python
await asyncio.gather(tool_a(), tool_b(), tool_c())
```

或者：

```java
CompletableFuture.allOf(...)
```

说明只理解了并发 API，没有回答调度正确性。

真正要解决的是：

1. Tool 之间有没有依赖；
2. 哪些 Tool 可以并行，哪些只能串行；
3. Tool 是否有副作用；
4. 一个 Tool 超时后是 FAILED 还是 UNKNOWN；
5. 下游 Step 的前置条件是否仍然成立；
6. required/optional Tool 怎么决定整体结果；
7. late result 是否还能写入当前 Plan；
8. global deadline 如何约束局部 retry；
9. 并发工具对同一个外部资源是否会互相冲突；
10. 进程重启后这批并行调用怎么恢复。

所以正确抽象应该是：

```text
Execution Graph + Scheduler + State Machine + Policy
```

而不是：

```text
几个 Future
```

---

# 二、第一原则：先区分“同一轮多个 Tool Call”和“显式 DAG”

这两个经常被混在一起。

## 模式 A：LLM 一次返回多个 Tool Call

例如：

```text
query_weather
query_hotel
query_flight
```

它们没有显式依赖关系，Runtime 可以根据 Tool Metadata 决定是否并发。

## 模式 B：任务本身是有依赖的 DAG

例如：

```text
Parse Trip Constraints
   ├─ Flight Search
   └─ Hotel Search
        ↓
Route ETA
        ↓
Final Ranking
```

这里 `Route ETA` 必须依赖 flight + hotel 的结果。

所以：

```text
Parallel Tool Calling
≠
DAG Scheduler
```

前者只是当前 Model Round 的并发执行策略；后者是跨 Step 的任务编排模型。

---

# 三、显式执行图应该怎么建模

建议每个节点至少有：

```json
{
  "step_id": "hotel-search",
  "tool_name": "search_hotel",
  "depends_on": ["parse-constraints"],
  "required": false,
  "side_effect": false,
  "idempotent": true,
  "concurrency_safe": true,
  "timeout_ms": 5000,
  "retry_policy": "read_retry_2",
  "plan_version": 3,
  "status": "PENDING"
}
```

为什么这么多字段？

因为调度器每做一个决定，都要有依据：

```text
是否 ready？            → depends_on
能不能并发？            → concurrency_safe
失败是否影响总任务？     → required
超时是否能重试？         → side_effect + idempotent
旧结果能不能写入？       → plan_version
```

---

# 四、调度器的核心不是线程池，而是 Ready Queue

真正的调度循环：

```text
1. 找出所有依赖已经满足的 PENDING 节点
2. 标记 READY
3. 根据并发/资源限制进入 executor
4. 更新 RUNNING
5. 收到 Result Event
6. CAS 更新节点状态
7. 解锁依赖它的下游节点
8. 判断整个 Graph 是否可继续/降级/终止
```

伪代码：

```text
while graph not terminal:
    ready = findReadyNodes(state)
    dispatch(ready)
    event = await nextResultEvent()
    applyEventByCAS(event)
    unlockDependents(event.stepId)
```

关键是：

> **调度正确性来自状态机和依赖关系，不来自并发库。**

---

# 五、为什么并发安全不能只看“Tool 是查询接口”

两个只读 Tool 也可能争夺同一资源：

```text
DB connection pool
外部 API QPS
同一 Browser Session
同一个 Sandbox
同一个 MCP Server
```

所以并发控制至少有三层：

## 1. Tool-level

```text
concurrency_safe=true/false
```

## 2. Resource-level

例如：

```text
hotel-api semaphore = 5
postgres bulkhead = 20
browser-session = serial
```

## 3. Run-level

例如一个 Agent Run 最多同时 4 个 Tool，防止模型一次吐 50 个调用拖垮系统。

因此：

```text
Tool concurrency-safe
≠
下游资源无限并发
```

---

# 六、nanobot 当前到底怎么并发 Tool

nanobot 当前的实现很值得直接讲源码。

执行入口：

```text
nanobot/agent/tools/execution.py
```

核心函数：

```text
execute_tool_calls(..., concurrent: bool, ...)
```

内部先调用：

```text
_partition_tool_batches()
```

逻辑不是“只要 concurrent=true 就全部 gather”。

它会逐个看 Tool：

```text
tool.concurrency_safe
```

如果安全，就放到当前 batch；遇到不安全 Tool，就先结束当前 batch，然后这个 Tool 单独串行执行。

可以理解为：

```text
Tool A concurrency_safe ✅
Tool B concurrency_safe ✅
Tool C concurrency_safe ❌
Tool D concurrency_safe ✅
Tool E concurrency_safe ✅
```

会被分成：

```text
Batch 1: A, B   → asyncio.gather
Batch 2: C      → serial
Batch 3: D, E   → asyncio.gather
```

这比“一次性 gather 所有 Tool”安全很多。

但要注意：

> **这仍然不是通用 DAG Scheduler。**

它解决的是同一 Model Round 中多个 Tool Call 的并发安全，不负责跨 Step 的 `depends_on`、required/optional、plan_version、global deadline。

---

# 七、为什么返回顺序必须稳定

并发执行完成顺序可能是：

```text
B → A → C
```

但 Tool Call 原顺序可能是：

```text
A → B → C
```

如果 Runtime 只按完成顺序拼回消息，某些 Provider/Tool Call 关联会变得不稳定。

nanobot 当前 `execute_tool_calls()` 会保持：

```text
stable result order
```

也就是批内并发，但最后按调用顺序组织结果。

更一般的工程设计应该永远通过：

```text
tool_call_id
step_id
```

关联，而不是依赖返回顺序。

---

# 八、Tool 状态机为什么必须有 UNKNOWN

建议状态：

```text
PENDING
  ↓
READY
  ↓
RUNNING
  ├─ SUCCEEDED
  ├─ FAILED
  ├─ TIMEOUT
  ├─ CANCELLED
  └─ UNKNOWN
```

其中 `UNKNOWN` 是副作用 Tool 的关键。

场景：

```text
create_order()
   ↓
外部系统成功创建 ORD-1
   ↓
响应回 Runtime 前网络超时
```

Runtime 看到：

```text
TIMEOUT
```

但真实世界是：

```text
SUCCESS
```

所以：

```text
TIMEOUT ≠ FAILED
```

对副作用 Tool，应该：

```text
TIMEOUT
   ↓
UNKNOWN
   ↓
reconcile(business_request_id)
```

---

# 九、read-only Tool 和 side-effect Tool 的 Retry Policy 完全不同

## Read-only

```text
query_weather
query_device
query_alarm
```

常见策略：

```text
retry 1~2 次
exponential backoff
jitter
切 fallback provider
```

## Side-effect

```text
create_order
refund
pay
send_message
create_work_order
```

策略应是：

```text
先幂等 / 状态对账
确认 NOT_FOUND
再安全 retry
```

所以 Tool Metadata 最好明确：

```text
side_effect
idempotent
retryable
reconcile_strategy
```

---

# 十、超时必须区分 4 个层级

## 1. Connect Timeout

连不上外部服务。

## 2. Tool Execution Timeout

单 Tool 最大执行时长。

## 3. Step Deadline

一个 Step 包含 retry/fallback 的总预算。

## 4. Global Run Deadline

整个 Agent Run 的 SLA。

例如：

```text
Run deadline = 20s
Flight Tool timeout = 8s
Hotel Tool timeout = 8s
```

如果运行已经花了 17s，再启动一个 8s Tool 是错误的。

正确：

```text
remaining = run_deadline - now
actual_timeout = min(configured_timeout, remaining)
```

---

# 十一、Required / Optional 决定部分成功是否可接受

场景：

```text
Flight Worker  SUCCESS   required
Hotel Worker   TIMEOUT   optional
Visa Worker    SUCCESS   required
```

不能简单：

```text
any fail → all fail
```

更合理的是：

```text
Required 全成功 → 任务可完成
Optional 失败   → 降级回答 + 标注缺失
```

如果：

```text
Visa Worker = required + TIMEOUT
```

就不能给出“可以出行”的确定性结论。

这叫：

```text
Partial Success Semantics
```

---

# 十二、下游节点的依赖不应该只有“完成/没完成”

有些 Step 可以接受降级输入。

例如：

```text
Hotel Search TIMEOUT
```

最终推荐仍然可以基于 Flight + Visa 输出，只是酒店部分缺失。

因此依赖条件可以更细：

```text
ALL_SUCCESS
ALL_TERMINAL
ANY_SUCCESS
AT_LEAST_N
CUSTOM_PREDICATE
```

这比单纯 `depends_on` 更强。

---

# 十三、用户改口以后，旧并行结果怎么处理

用户：

```text
“我要最早航班”
```

Plan v1 启动多个 Worker。

两秒后用户：

```text
“不要最早了，要最便宜。”
```

Plan v2 生效。

旧 Worker 可能晚回来：

```text
Flight Worker v1 → SUCCESS
```

如果直接写当前 State，就会污染 v2。

所以所有 Result Event 至少带：

```text
plan_id
plan_version
step_id
attempt
```

写入前：

```text
if event.plan_version != current.plan_version:
    discard or archive as stale artifact
```

这叫：

```text
Stale Result Protection
```

---

# 十四、为什么需要 attempt_id

一个 Step 可能 retry：

```text
hotel-search attempt 1
hotel-search attempt 2
```

attempt 1 超时后，attempt 2 已成功。

此时 attempt 1 的迟到响应又回来。

如果只看：

```text
step_id
```

会误覆盖新结果。

所以至少：

```text
step_id + attempt
```

或者一个全局 `execution_id`。

---

# 十五、并行执行中的状态更新要防 Lost Update

三个 Worker 同时更新 Run State：

```text
Worker A writes state version 11
Worker B also based on version 10 writes version 11
```

可能丢掉 A 的状态。

所以共享 State Store 要么：

```text
per-run actor / single writer
```

要么：

```text
optimistic lock / CAS version
```

例如：

```sql
UPDATE run_state
SET state_json=?, version=version+1
WHERE run_id=? AND version=?
```

失败就重新读并合并事件。

不要让多个 Worker 直接覆盖整个 JSON State。

---

# 十六、推荐 Event Sourcing 风格，而不是 Worker 直接改共享对象

Worker 只产生：

```json
{
  "type": "TOOL_SUCCEEDED",
  "run_id": "r1",
  "step_id": "hotel",
  "attempt": 2,
  "plan_version": 3,
  "tool_call_id": "tc9",
  "artifact_id": "a17"
}
```

Orchestrator 单线程/串行应用 Event：

```text
Result Event
   ↓
validate version
   ↓
apply state transition
   ↓
unlock downstream
```

好处：

```text
可回放
可追踪
并发写冲突少
恢复容易
```

---

# 十七、进程崩溃以后并行 Tool 怎么恢复

这是高级追问。

假设同一批：

```text
A → SUCCESS
B → RUNNING
C → SUCCESS
```

但 `tools_completed` 还没整体落盘就崩了。

如果 Runtime 只做 batch-level checkpoint，就可能只知道：

```text
这一批仍是 awaiting_tools
```

而不知道 A/C 已成功。

nanobot 当前恢复策略因此偏保守：

```text
awaiting_tools → uncertain
```

不会自动 replay pending Tool。

如果你要做更强 DAG Runtime，就要将 checkpoint 粒度下沉到：

```text
per-step / per-tool attempt
```

例如：

```text
A SUCCEEDED durable
B UNKNOWN
C SUCCEEDED durable
```

恢复后只 reconcile B。

这就是通用 Agent Loop 与 durable workflow engine 的差距。

---

# 十八、三个 Worker 并行的完整场景

```text
         ┌──────────── Flight ────────────┐
Parse ───┼──────────── Hotel ─────────────┼─→ Aggregator
         └──────────── Visa ──────────────┘
```

假设：

```text
Flight = SUCCESS
Hotel  = TIMEOUT (optional)
Visa   = SUCCESS
```

Aggregator 先判断：

```text
required nodes terminal & success ? YES
```

于是可以输出：

```text
航班：已找到
签证政策：已确认
酒店：查询超时，暂未纳入最终推荐
```

同时可以后台或下一轮允许用户：

```text
“是否继续重试酒店？”
```

而不是为了等酒店把整个 20s SLA 拖到 60s。

---

# 十九、Java 实现推荐

数据结构：

```java
record ToolNode(
    String stepId,
    String toolName,
    Set<String> dependsOn,
    boolean required,
    boolean sideEffect,
    boolean idempotent,
    boolean concurrencySafe,
    Duration timeout,
    long planVersion,
    int attempt
) {}
```

调度线程可以用：

```text
Virtual Thread / CompletableFuture / Reactor
```

但这只是执行原语。

真正核心组件：

```text
DependencyResolver
ReadyQueue
ExecutionPolicy
StateStore
ResultEventBus
Aggregator
Reconciler
```

---

# 二十、常见错误

## 错误 1：所有 Tool 一把 gather

忽略 concurrency safety 和依赖。

## 错误 2：any timeout = all fail

无法支持 partial success。

## 错误 3：timeout = failed

副作用 Tool 可能其实已成功。

## 错误 4：只存 step_id

retry 后迟到旧结果会覆盖新 attempt。

## 错误 5：没有 plan_version

用户改口后 stale result 污染新计划。

## 错误 6：只配置 Tool timeout，没有 global deadline

局部 retry 会拖垮整体 SLA。

---

# 二十一、面试官继续追问

### Q1：为什么 nanobot 还不是 DAG Scheduler？

因为当前并发主要是“一次模型响应里的多个 Tool Call”按 `concurrency_safe` 分 batch 执行，没有显式 `depends_on/required/plan_version` 的跨 Step 调度状态机。

### Q2：一个 concurrent-safe Tool 为什么还可能不能并发？

因为底层共享资源可能有 QPS、连接池、Browser Session、Sandbox 互斥等更细的 bulkhead。

### Q3：Worker 超时后能不能 cancel？

可以发 cancellation，但必须接受“取消不一定成功”。对于已发到外部系统的副作用请求，仍然要 reconcile。

### Q4：如何判断整体任务终态？

根据 graph terminal predicate，而不是 `all futures done`。例如 required nodes 成功且所有会影响决策的节点终结，就可完成。

---

# 二十二、2 分钟面试口述版

> Parallel Tool Calling 我不会只用 `gather` 来理解，而会把它分成两层：同一模型 Round 的多个 Tool 并发，以及跨 Step 的 DAG 调度。nanobot 当前在 `agent/tools/execution.py` 里会根据 `tool.concurrency_safe` 先分 batch，只对安全 Tool 使用 `asyncio.gather`，而且保持 Tool Result 顺序稳定；这解决的是 Round 内并发，但不是完整 DAG。真正企业级调度还要有 `depends_on`、required/optional、side_effect、timeout、global deadline、plan_version、attempt_id 和状态存储。查询 Tool 超时可以有限 retry，副作用 Tool 超时必须进入 UNKNOWN，再用 business_request_id 对账。并发 Worker 只产生 Result Event，由单一 Orchestrator/CAS 更新 State，用户改口后通过 plan_version 丢弃 stale result。这样才能保证并行带来吞吐，而不是把状态一致性搞乱。
