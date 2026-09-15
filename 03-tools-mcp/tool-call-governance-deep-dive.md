# 大量无效 Tool 调用怎么治理：从 Tool 暴露、重复检测、Budget 到下游保护

> 对应高频面试题：**“大量无效 Tool 调用会拉高成本、拖慢 QPS，做过哪些限流与拦截机制？”**
>
> 这道题不能只回答“加限流、设置 `max_tool_calls`”。面试官真正想听的是：你能不能把 **模型决策错误、Agent Loop 重复、租户流量放大、下游接口保护、业务副作用安全** 分层治理。

---

## 1. 先说结论：无效 Tool 调用不是一个问题，而是四类问题

生产环境里我会先把“无效调用”分成四类，因为四类问题的治理手段不同：

```text
1. Should-not-call
   本来不需要 Tool，模型却调用了 Tool

2. Wrong-tool
   应该调用 A，模型却调用 B

3. Duplicate-call
   在没有状态变化的情况下，重复执行同一个动作

4. No-progress-call
   参数看起来不同，但没有获得任何新信息，Agent 一直原地打转
```

例如用户问：

```text
“羲和照明平台支持哪些分析能力？”
```

如果知识已经在当前 Context 里，模型还连续调用：

```text
search_docs(...)
search_docs(...)
search_docs(...)
```

这是 `Should-not-call + Duplicate-call`。

如果用户问：

```text
“查询项目 A 昨晚的异常告警”
```

模型调用：

```text
query_energy()
```

但真正应该调用：

```text
query_alarm()
```

这是 `Wrong-tool`。

还有一种更隐蔽：

```text
search("上海酒店")
search("上海的酒店")
search("上海住宿")
```

三个参数字符串不同，但 Goal、数据源和返回结果都没有变化，这属于 `No-progress-call`。

所以完整治理不能只靠 QPS Limit。

---

# 2. 我会把 Tool Governance 放在五层，而不是只在最后加限流

```text
User Request
    ↓
① Tool Exposure / Candidate Selection
    ↓
LLM Tool Proposal
    ↓
② Schema / Permission / Precondition
    ↓
③ Duplicate & No-progress Guard
    ↓
④ Run Budget / Rate Limit / Concurrency
    ↓
⑤ Bulkhead / Circuit Breaker / Timeout
    ↓
Tool Execution
    ↓
Canonical ToolResult
    ↓
Observation → 下一轮 LLM
```

这五层分别解决不同问题。

---

# 3. 第一层：先减少模型“能看到”的 Tool，而不是让模型从 200 个 Tool 里随便挑

大量错误 Tool Call 的根源，往往在 Tool 执行之前就已经发生了。

如果系统注册了 200 个 Tool，每轮都把完整 schema 发送给模型，会同时带来三个问题：

```text
Tool Schema Token 增长
        +
Tool Selection Confusion
        +
模型获得不必要的能力
```

所以生产系统更合理的是 Progressive Disclosure：

```text
User Intent
    ↓
Domain Router
    ↓
Candidate Tool Set
    ↓
Role / Tenant / Permission Filter
    ↓
本轮 Model-visible Tools
```

例如智慧照明问题：

```text
用户：分析 A 项目昨晚异常灯具
```

这一轮只暴露：

```text
query_project
query_device
query_alarm
query_energy
create_work_order（如果角色允许）
```

没必要把：

```text
refund
flight_search
send_mail
admin_delete_user
```

发送给模型。

这里的收益不只是性能，而是：

> **能力没有暴露给模型，比暴露后再告诉模型“不要调用”更可靠。**

在 AgentDock 这类 Control Plane 中，这一层很适合根据 tenant、agent driver、assigned MCP、Skill 和用户角色生成每个 Agent 的能力视图；Runtime 再把当前 Turn 真正需要的 Tool 子集投影给模型。

---

# 4. 第二层：模型选了 Tool，也不是立刻执行

LLM 输出 Tool Call 只能看成：

```text
Action Proposal
```

而不是：

```text
Execution Command
```

执行之前至少经过：

```text
Tool exists?
    ↓
JSON Schema valid?
    ↓
用户/Agent 有权限？
    ↓
当前业务状态允许？
    ↓
风险级别是否需要 HITL？
    ↓
是否已经执行过同样动作？
    ↓
是否还有 Budget？
    ↓
Execute
```

比如模型提出：

```text
create_work_order(project=A, device=1001)
```

Runtime / Java Service 仍然要确认：

```text
user can access project A
设备 1001 属于 project A
当前是否已经有未关闭同类工单
当前故障证据是否满足创建条件
```

这一步解决的是“错误调用真的产生副作用”的问题。

---

# 5. Action Fingerprint 到底是什么意思？

这里要先澄清：

> **Action Fingerprint 不是 MCP、LangChain、nanobot 定义的正式协议名，也不是必须背的行业标准术语。**

它只是一个很实用的 Runtime 实现技巧。更直白的名字可以叫：

```text
Action Key
Dedup Key
Tool Call Signature
```

它解决的问题是：

> **当前系统状态没有变化时，Agent 是否准备再次执行刚刚已经执行过的同一个逻辑动作？**

例如模型连续两次输出：

```json
{
  "tool": "query_alarm",
  "arguments": {
    "project_id": "P100",
    "date": "2026-09-15"
  }
}
```

如果第一次已经成功返回数据，第二次没有任何新条件，就没必要真的再访问一次数据库/API。

Runtime 可以构造一个稳定的 Action Key：

```text
ActionKey =
    tool_name
  + normalized_args
  + execution_scope
  + relevant_state_version
```

必要时再做 hash：

```text
fingerprint = SHA256(ActionKey)
```

**Hash 只是为了存储和比较方便，不是这个机制的核心。**

---

## 5.1 为什么必须先做 `normalized_args`

下面两个调用逻辑上完全一样：

```json
{"project_id":"P100","date":"2026-09-15"}
```

```json
{"date":"2026-09-15","project_id":"P100"}
```

如果直接对原始 JSON 字符串做 hash，会得到两个不同结果。

所以先 canonicalize：

```text
补齐确定性默认值
→ key 排序
→ 日期/时区标准化
→ ID 规范化
→ 删除真正不影响语义的字段
→ canonical JSON
```

例如：

```text
query_alarm|date=2026-09-15|project_id=P100
```

再生成 key/hash。

需要注意：**不能过度归一化。**

例如：

```text
refund(amount=100)
refund(amount=1000)
```

绝对不能为了“语义相似”把它们归成同一个动作。

对于高风险副作用，宁可保守，也不能错误合并两个真实业务意图。

---

## 5.2 为什么只有 `tool_name + args` 仍然不够

考虑：

```text
query_order(order_id=1001)
```

10:00 查询：

```text
status = PAYING
state_version = 20
```

10:01 支付回调已经到达：

```text
status = PAID
state_version = 21
```

Agent 此时再次调用：

```text
query_order(order_id=1001)
```

这是合法调用，因为环境发生了变化。

如果 ActionKey 只有：

```text
query_order + order_id=1001
```

第二次查询会被错误拦截。

所以对于依赖状态的 Tool，可以加入：

```text
relevant_state_version
```

最终：

```text
第一次
query_order|1001|state=v20

第二次
query_order|1001|state=v21
```

它们不是同一个 Fingerprint。

这也是 Action Fingerprint 真正有价值的地方：

> 判断的不是“这个 API 以前调用过没有”，而是“在当前状态下，这个动作是否已经做过且没有理由再做一次”。

---

## 5.3 `execution_scope` 为什么也很重要

多租户系统不能只按 Tool 参数做全局去重。

例如两个用户都调用：

```text
query_device(device_id=1001)
```

但属于不同 Tenant。

正确 Key 至少带：

```text
tenant_id
user/project scope
```

类似：

```text
ActionKey(
  tenant=T1,
  tool=query_device,
  args={device_id:1001},
  state_version=33
)
```

否则会出现跨租户缓存/去重污染。

---

# 6. Action Fingerprint、Idempotency Key、Cache Key、Rate Limit 必须区分

这是面试很容易追问的地方。

| 机制 | 解决什么 | 典型生命周期 | 谁负责 |
|---|---|---|---|
| Action Fingerprint / Dedup Key | Agent 是否正在重复做同一个动作 | 单 Run / 短窗口 | Agent Runtime / Harness |
| Idempotency Key | 副作用请求重复到达时不能产生两次业务效果 | 必须持久，跨重试/重启 | Java/业务服务 |
| Cache Key | 相同查询能否复用旧结果 | TTL/版本控制 | Tool/Cache 层 |
| Rate Limit Key | 谁在某时间窗口消耗了多少容量 | 时间窗口 | Gateway/Control Plane/Tool Runtime |

例如退款：

```text
Action Fingerprint
→ 防止 Agent Loop 在同一轮逻辑里连续提议 refund

Idempotency Key
→ 即使请求真的重复到达支付服务，也只产生一次退款
```

两者完全不是一个东西。

不能拿 Action Fingerprint 去代替业务幂等。

---

# 7. Fingerprint 只能发现“完全重复”，还需要 No-progress Detection

这是比 Action Fingerprint 更重要的一层。

模型可能这样循环：

```text
search_web("上海酒店")
search_web("上海的酒店")
search_web("上海住宿")
search_web("上海酒店推荐")
```

四个 ActionKey 都不一样，但 Agent 实际没有前进。

因此 Runtime 还需要观察“任务有没有产生新信息”。

可以维护一个 Progress State：

```text
goal_id
state_version
known_artifact_ids
evidence_count
last_error_kind
last_result_class
completed_subgoals
```

每轮结束计算：

```text
new_evidence_count
state_changed
subgoal_completed
result_class_changed
```

例如连续三轮：

```text
new_evidence_count = 0
state_changed       = false
subgoal_completed   = false
last_result         = NO_RESULT
```

即使 Tool 参数每次都不一样，也可以进入：

```text
NO_PROGRESS
```

然后 Runtime 要求换策略，而不是继续放任模型探索：

```text
NO_PROGRESS
   ↓
扩大/改变搜索条件
   ↓
切换 Tool / Provider
   ↓
询问用户补充约束
   ↓
Fallback
   ↓
Graceful Stop
```

---

# 8. 第三层：Budget，不是只有 `max_iterations`

Agent 一轮 LLM 可能一次提出多个 Tool Call，所以：

```text
max_iterations = 10
```

并不等于：

```text
最多调用 10 次 Tool
```

更完整的 Budget 应包括：

```text
max_iterations
max_tool_calls
max_calls_per_tool
max_duplicate_calls
max_external_lookups
max_argument_repairs
max_replans
max_subagent_depth
max_tokens
max_cost
wall_clock_deadline
```

还可以按 Tool 风险给不同预算：

```text
query_device       10/run
query_alarm         5/run
web_search          5/run
create_work_order   1 logical action
refund              1 logical action + HITL
```

这里的 Budget 是 **Run 级行为约束**。

---

# 9. 第四层：Rate Limit 必须考虑 Agent 的 Fan-out

传统 Web API 常按：

```text
100 requests/min/user
```

但 Agent 中：

```text
1 个用户请求
   ↓
4 次 LLM
   ↓
8 次 Tool
   ↓
12 次 HTTP/SQL
```

所以只限制入口 QPS 不够。

建议至少分：

```text
Tenant Limit
User Limit
Agent/Run Limit
Tool Limit
Provider Limit
Downstream Service Limit
```

例如用 Token Bucket：

```text
tenant:T1:web_search = 1000/min
user:U7:web_search    = 50/min
provider:maps         = 200 QPS
```

同时 Runtime 的 `max_tool_calls` 控制单任务行为。

也就是：

```text
Rate Limit
保护“系统总容量”

Budget
限制“一个 Agent Run 能花多少资源”
```

二者不能混成一个概念。

---

# 10. 第五层：Bulkhead + Circuit Breaker 防止一个 Tool 拖垮全站

假设旅游 Agent 同时有：

```text
flight_search
hotel_search
weather
maps
web_search
```

如果 `flight_search` Provider 卡住，不应该把整个 Agent 平台线程/连接全部吃光。

可以按 Tool/Provider 建独立并发池：

```text
flight provider  max 20
hotel provider   max 40
web search       max 30
DB analytical    max 15
```

这就是 Bulkhead。

再配合 Circuit Breaker：

```text
CLOSED
  ↓ failure threshold
OPEN
  ↓ cooldown
HALF_OPEN
  ↓ probe
CLOSED / OPEN
```

OPEN 时 Runtime 不继续把请求压给坏 Provider，而是：

```text
fallback provider
cache
partial result
explicit degradation
```

这样才能真正保护 QPS 和线程/连接池。

---

# 11. Retry 也必须统一 owner，否则无效调用会指数放大

非常典型的错误：

```text
HTTP Client retry 3
Tool Adapter retry 3
Agent 自己再 retry 3
```

最坏：

```text
3 × 3 × 3 = 27 次下游请求
```

所以一定要明确 Retry Ownership：

```text
HTTP Client
→ 只处理非常底层、明确安全的瞬时错误

Tool Runtime
→ 统一 retry policy / deadline / backoff

Agent
→ 负责语义换策略，不重复相同请求
```

尤其副作用 Tool timeout：

```text
refund timeout
```

不能因为“还剩 Tool Budget”就继续重试，而要进入：

```text
UNKNOWN → reconcile
```

---

# 12. nanobot 当前代码怎么对应这套设计

当前 nanobot `nanobot/agent/tools/execution.py` 在真正执行 Tool 前，会调用：

```python
repeated_external_lookup_error(
    tool_call.name,
    tool_call.arguments,
    external_lookup_counts,
)
```

命中后并不会继续 `tool.execute()`，而是返回：

```text
repeated external lookup blocked
```

作为 Tool Error Observation 交回模型。

所以 nanobot 当前已经有一个非常具体的：

> **Repeated External Lookup Guard**

可以用它解释“Runtime 在 Tool 执行之前做重复行为拦截”。

但要注意，不应该说：

> “nanobot 已经实现了完整的 Action Fingerprint / Semantic No-progress Engine。”

从当前执行代码看，它解决的是**部分重复 external lookup**；企业级 Harness 如果要做到：

```text
canonical args
state-aware dedup
semantic no-progress
per-tool budget
tenant quota
provider circuit breaker
```

仍然需要在 Runtime / Tool Adapter / AgentDock Control Plane 继续补强。

这个边界在面试里要说准确。

---

# 13. 如果结合 AgentDock，我会怎么落地

AgentDock 当前已经有 Task/Event、iteration/token 可观测性、多租户 workspace、独立 Agent Container、CPU/Memory limit 和统一 Driver API。

因此更适合把平台级治理放在：

```text
AgentDock Control Plane
├─ tenant quota
├─ user quota
├─ task/run budget
├─ provider concurrency
├─ usage accounting
└─ global kill/cancel

Agent Runtime (nanobot/Pi/...)
├─ model-visible tool set
├─ duplicate lookup guard
├─ no-progress detection
├─ iteration/tool budget
└─ observation loop

Java Domain Service
├─ authorization
├─ business precondition
├─ idempotency
├─ transaction
└─ reconcile
```

也就是说，不要要求一个 Runtime 同时承担租户平台、模型循环和业务一致性三种职责。

---

# 14. 实际指标怎么证明这些机制有效

如果你说“我做了限流”，面试官下一句很可能问：

> 怎么证明它有效？

我会看：

```text
Tool Calls / Successful Task
Unnecessary Tool Rate
Wrong Tool Rate
Duplicate Tool Rate
Repeated External Lookup Block Rate
No-progress Termination Rate
Argument Repair Count
Provider 429 Rate
Provider P95/P99
Tool Queue Wait
Circuit Breaker Open Rate
Cost / Successful Task
Latency / Successful Task
```

还必须监控 Guard 的误伤：

```text
False-positive Block Rate
```

因为如果重复检测过于激进，会把“状态已经变化后的合法重新查询”也挡掉。

这也是为什么前面 ActionKey 建议考虑 `relevant_state_version`。

---

# 15. Java 侧可以怎么实现

可以抽象一个 `ToolExecutionGuard`：

```java
public record ToolActionKey(
    String tenantId,
    String toolName,
    String normalizedArgsHash,
    long stateVersion
) {}

public sealed interface GuardDecision {
    record Allow() implements GuardDecision {}
    record Reject(String reason) implements GuardDecision {}
}
```

Runtime 调用：

```text
LLM Tool Call
    ↓
ToolRegistry.resolve()
    ↓
Schema Validator
    ↓
Authorization
    ↓
ToolExecutionGuard.check()
    ├─ duplicate?
    ├─ budget exceeded?
    ├─ no progress?
    ├─ rate limited?
    └─ circuit open?
    ↓
execute
```

注意 Guard 不应该把所有逻辑塞进一个巨大 `if`；真正实现时通常把：

```text
DedupPolicy
BudgetPolicy
RateLimitPolicy
CircuitBreakerPolicy
RiskPolicy
```

组合成 Policy Chain。

---

# 16. 面试官继续追问：几个最容易混淆的问题

### “为什么不用 Redis SETNX 直接防重复？”

可以作为实现手段之一，但先要定义**什么才算同一个逻辑动作**。如果 Key 设计错误，SETNX 只能稳定地做错事。

### “Action Fingerprint 要永久保存吗？”

通常不需要。它主要服务当前 Run/短时间窗口的 Loop Dedup；副作用跨重启幂等必须靠持久的 `idempotency_key`。

### “参数变一点就绕过 Fingerprint 怎么办？”

Fingerprint 只解决 exact/logical duplicate。跨参数的重复探索靠 No-progress Detection、Goal/State/Evidence 变化判断。

### “缓存和 Duplicate Guard 有什么区别？”

缓存的意思是：这个调用允许发生，但可以复用旧结果；Duplicate Guard 的意思是：当前 Agent 行为已经没有必要再次执行，应该把控制权交还给规划/模型去换策略。

### “是不是所有重复查询都应该拦截？”

不是。状态变化、TTL 到期、用户显式要求刷新、强一致读取，都可能允许重复调用。Guard 必须知道状态版本或 freshness policy。

---

# 17. 1～2 分钟面试口述版

> 我不会只用一个 QPS Limit 解决无效 Tool 调用，因为无效调用至少有四类：本来不该调、选错 Tool、完全重复、以及参数略变但没有新进展。第一层我会做 Progressive Tool Disclosure，按领域、角色和权限只把本轮需要的 Tool 暴露给模型；第二层模型产生 Tool Call 后，Runtime 先做 Schema、权限和业务前置校验。对于重复调用，我会生成一个运行时 Dedup Key，也可以叫 Action Fingerprint，本质是 `tool_name + canonical args + scope + relevant state version`，它不是行业协议，只是用来判断当前状态下是否已经执行过同一动作；真正跨重启的副作用安全仍然靠业务 idempotency key。第三层做 `max_tool_calls/max_calls_per_tool/deadline/cost` 等 Run Budget，第四层按 tenant、user、provider、tool 做 Rate Limit 和并发 Semaphore，第五层用 Bulkhead、Circuit Breaker 和统一 Retry Ownership 保护下游。另外 Fingerprint 抓不到“上海酒店/上海住宿”这种语义上原地打转，所以还要看 state、evidence、subgoal 是否变化做 No-progress Detection。nanobot 当前已经有 repeated external lookup guard，但它不是完整的语义去重系统；企业版可以在 Runtime/AgentDock 层继续补齐这些策略。

---

## 最后记住一句话

> **治理无效 Tool Call 的核心不是“把 Tool 调用次数限制小”，而是让每一次 Tool 调用都必须证明：它有权限、有预算、当前状态下有必要，并且有机会给任务带来新的信息或状态变化。**
