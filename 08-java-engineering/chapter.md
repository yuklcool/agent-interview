# 08. Java / Spring / 并发与平台工程

> 这一章不是“传统 Java 八股题的附录”。Agent 真正上线以后，模型只是链路中的一个远程依赖，系统仍然要面对线程、连接池、超时、背压、缓存、数据库、流式协议、隔离和可观测性。高级面试真正想看的是：你能不能把概率模型放进确定性的后端工程体系里。

---

## 08-01. Java 线程池参数怎么配？IO 密集和 CPU 密集在 Agent 服务里怎么取数

### 面试官真正考什么

不是让你背 `corePoolSize = N+1`。Agent 服务里一条请求可能同时等待 LLM、MCP、Redis、数据库和 HTTP API，如果只按 CPU 核数配线程池，很容易把“等待外部 IO”误认为“CPU 消耗”。面试官更关心你是否知道线程池只是并发预算的一层，真正瓶颈还受 DB 连接池、HTTP 连接池、下游 QPS、内存和超时共同约束。

### 核心结论

CPU 密集任务从 `CPU 核数` 附近开始；IO 密集任务可以明显高于 CPU 核数，但不能孤立调线程数。一个常用估算是：

```text
线程数 ≈ CPU 核数 × (1 + IO 等待时间 / CPU 计算时间)
```

它只能作为起点，最终要通过压测看：线程池排队时间、数据库连接等待、下游 P95/P99、GC、上下文切换和拒绝次数。

### Agent 场景怎么拆池

不要让下面三类任务抢同一个池：

```text
HTTP/LLM/MCP IO Pool
        │
DB IO Pool
        │
CPU Compute Pool
```

例如历史压缩、Embedding 本地推理、JSON 大对象处理属于 CPU 或本地计算；LLM/MCP/HTTP 属于高等待 IO；DB 查询虽然也是 IO，但还被连接池硬限制。线程开 200、HikariCP 只有 20 个连接，180 个线程只是在等连接，并不会增加吞吐。

### Spring 落地

我会把线程池和下游连接池一起做容量设计，并为不同资源做 Bulkhead：

```text
Agent request
  ├─ llmExecutor      max=100
  ├─ toolExecutor     max=80
  ├─ dbPool           max=30
  └─ cpuExecutor      max=CPU+1
```

还要把 queue wait、active threads、rejected count、DB acquire latency 和 HTTP connection pending 一起纳入 OTel/Micrometer。

### 追问

**为什么不直接用无界队列？** 因为无界队列把过载从“快速拒绝”变成“无限排队 + 内存风险 + 延迟雪崩”。

**线程池满了怎么办？** Agent 请求通常不能简单 `CallerRunsPolicy` 把网关线程拖死，我更倾向有界队列 + 明确限流/降级 + 返回可解释的 busy 状态。

---

## 08-02. Spring Boot 里怎么把 Agent 能力嵌进已有微服务，不重造轮子

### 核心结论

不要把已有业务服务全部搬进 Agent。Agent 应该是新的“自然语言入口 + 编排层”，领域规则、事务、权限、审计和最终事实继续由原有 Service 掌控。

```text
WebSocket / REST
       ↓
AgentApplicationService
       ↓
Agent Runtime / nanobot
       ↓ Tool Call
Tool Adapter / MCP Adapter
       ↓
Existing Domain Service
       ↓
DB / Payment / Device / WorkOrder
```

### 为什么这样分层

如果让 LLM 直接拼 SQL、直接写订单表、直接改设备状态，等于绕过 Spring Security、事务边界、领域校验、幂等和审计。正确做法是：

```java
@Tool("create_work_order")
public WorkOrderResult createWorkOrder(CreateWorkOrderArgs args) {
    authz.check(...);
    return workOrderService.create(args.toCommand());
}
```

Tool Adapter 负责“模型契约”，Domain Service 负责“业务事实”。以后换模型、换 nanobot、换 MCP，业务核心不动。

### 结合 nanobot

你可以让 nanobot 负责 `Session → Context → LLM → Tool Loop`，Java 服务继续负责：

- 用户/租户权限
- SQL 数据范围
- 工单/设备/支付事务
- 幂等和状态机
- 审计和 OTel Trace

也就是说只允许一个 Runtime owner，避免 Java 侧再造一套 Agent Loop 导致双重状态、双重重试和双重恢复。

---

## 08-03. Redis 在 Agent 系统里存什么？会话状态还是 Tool Result 缓存

### 核心结论

Redis 适合“高频、短生命周期、并发协调”的状态，不应该成为所有 Agent 数据的最终事实库。

适合放：

```text
Session 热状态
run_id → instance 映射
流式游标
Rate Limit
幂等 Key
分布式锁 / Lease
任务短期状态
Tool 查询结果缓存
Pub/Sub / Stream
```

不适合只放 Redis 的：完整审计历史、订单事实、最终工单状态、重要 Tool Result、长期 Memory 原始事实。

### Tool Result 缓存最容易踩的坑

不是所有 Tool 都能缓存。`query_weather`、`query_device_status` 可以按 TTL 缓存；`refund`、`create_order`、`send_message` 是副作用动作，不能用“缓存命中”代替真实业务状态。

缓存 Key 还必须包含权限范围：

```text
tool:{tenant}:{user_scope}:{tool}:{args_hash}:{version}
```

否则同一个 SQL 参数可能把 A 项目的结果串给 B 项目。

### Session 一致性

如果同一个 session 可能被多实例处理，Redis 只是协调层，最好配：

```text
session_version / CAS
+ per-session queue/actor
+ durable event log
```

不要简单依赖一把分布式锁解决所有并发问题，因为进程宕机、网络分区、锁续租失败仍然会产生双写风险。

---

## 08-04. JDK 21 虚拟线程适合 Agent 服务吗？用了就不用线程池了吗

### 核心结论

虚拟线程非常适合“大量阻塞式 IO 等待”的 Agent 服务，但它解决的是“线程承载成本”，不是“下游容量无限”。

传统平台线程：一个阻塞请求长期占一个 OS Thread；虚拟线程阻塞时可以卸载 carrier thread，因此调用 LLM、MCP、HTTP、DB 这种高等待链路写同步代码也能获得很高并发。

但：

```text
Virtual Thread 数量 ≠ 可无限放大下游并发
```

如果 LLM QPS 只有 50，数据库连接只有 30，开 10 万虚拟线程只会让更多请求同时卡在限流/连接等待上。

### 正确做法

虚拟线程 + Semaphore/Bulkhead：

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    // 每个请求可用虚拟线程
}

Semaphore llmSlots = new Semaphore(50);
Semaphore dbSlots  = new Semaphore(30);
```

所以“是否还要线程池”的答案是：不一定要传统固定线程池来控制 IO 并发，但仍然需要**资源并发限制、deadline、队列和背压**。

---

## 08-05. 高并发 Agent 服务扩容，瓶颈一般在哪里

不要第一反应只加 Pod。Agent 链路的瓶颈通常沿依赖图出现：

```text
Ingress
 ↓
Agent Instance CPU/Mem
 ↓
LLM Provider QPS / TPM
 ↓
Tool/MCP QPS
 ↓
DB Connection Pool
 ↓
Redis / Vector DB
```

真正要看的是每一层的 saturation。典型现象：

- Agent Pod CPU 只有 30%，但 LLM provider 已被 429 限流；加 Pod 无效。
- DB connection acquire P99 飙升；说明瓶颈在连接池/慢 SQL。
- Tool 结果很大导致 Context Token 暴涨；瓶颈变成 LLM Token 和内存。
- WebSocket 长连接多，但实际活跃 Run 少；连接数和执行并发要分开容量规划。

### 容量模型

可以粗略用 Little's Law：

```text
并发数 ≈ 到达率 × 平均响应时间
```

例如 20 req/s，平均 Run 8 秒，系统天然就会有约 160 个并发 Run。只看 QPS 不看长任务时延，很容易低估 Agent 的并发占用。

---

## 08-06. Kafka/消息队列放进 Agent Pipeline 会不会增加延迟？什么时候值得用

会增加一次序列化、broker 和消费调度延迟，所以实时对话主链不要为了“架构高级”而全 MQ 化。

适合 MQ 的地方：

```text
长任务异步执行
审计/Trace 异步落库
Tool 后置任务
Event-driven Workflow
Outbox / 最终一致性
批量 Embedding / Index Build
```

不适合强行 MQ 的地方：用户等着当前轮回答、延迟敏感且步骤必须同步返回的 Tool 调用。

### 一个典型划分

```text
WebSocket → Agent Runtime → LLM/Tool   # 同步主链
                       └→ Kafka → Audit/Analytics/Async Work
```

高风险业务可以用 Outbox：事务内先写业务表 + outbox，提交后再异步发送事件，避免“订单成功但消息没发出去”。

---

## 08-07. SSE 和 WebSocket 在 Agent 流式输出里怎么选

### SSE

优点：HTTP 语义简单、浏览器原生 `EventSource`、服务端单向流很自然；缺点是客户端→服务端实时控制能力弱。

### WebSocket

适合真正双向 Agent：用户可以在 Tool 执行中追加消息、取消、确认、修改目标。

你的场景已经不只是 token streaming，而是：

```text
run.started
message.delta
tool.call.created
tool.call.running
tool.call.completed
recovery.required
user.confirmed
run.completed
```

因此 WebSocket 更合适。

### 协议设计比 transport 更重要

不要只发字符串 delta。事件至少包含：

```json
{
  "event": "tool.call.completed",
  "run_id": "r1",
  "turn_id": "t7",
  "seq": 31,
  "tool_call_id": "tc3",
  "payload": {...}
}
```

客户端用 `seq` 去重/补序，用 `run_id` 隔离旧 Run。用户中途修改要求时，也能明确告诉服务端是“新 turn”还是“当前 run injection”。

---

## 08-08. Agent 运行大量 Checkpoint/Session 查询，数据库索引怎么设计

先从访问模式设计，而不是“给每个字段都加索引”。

如果常见查询是：

```sql
SELECT ... FROM agent_run
WHERE tenant_id=? AND session_id=?
ORDER BY updated_at DESC
LIMIT 20;
```

更合理的是复合索引：

```sql
(tenant_id, session_id, updated_at DESC)
```

Run/Step 常见索引：

```text
run_id unique
(session_id, created_at)
(run_id, step_id)
(run_id, status)
(tenant_id, updated_at)
```

如果恢复时经常查 `status IN ('RUNNING','UNKNOWN')`，PostgreSQL 可以考虑 partial index。

### 为什么 Agent 场景尤其敏感

一次用户请求可能产生几十条 step/tool/trace 记录，如果每轮都做 N+1 查询，量很快放大。应把：

- session header
- recent transcript
- checkpoint
- run state

分清热路径，必要时 materialized state + append-only events，而不是每次从完整事件表重放全部历史。

---

## 08-09. Sandbox 为什么是 Code Agent / 高风险 Tool 的基础设施？Docker、远程沙箱怎么选

Prompt 不是安全边界。模型只要能执行 shell/代码，就必须假设它可能生成：

```text
rm -rf
读取 ~/.ssh
访问 metadata service
扫描内网
fork bomb
无限占用 CPU/Mem
```

因此 Code Agent 必须有真正的 OS/Container 隔离：文件系统、网络、进程、CPU、内存、PID、syscall、凭证都要限制。

### Docker 本地沙箱

优点：部署简单、启动快、适合可信代码和开发环境。缺点：与宿主共享内核，强多租户场景的隔离强度有限。

### 远程/微虚机沙箱

Firecracker/Kata/独立 VM/云沙箱隔离更强，适合多租户、不可信代码、企业 Agent 平台，但启动/调度/成本更高。

选择标准是 threat model，不是“Docker 能不能跑”。

---

## 08-10. 数据库索引为什么会失效？Agent 服务里为什么也要懂传统后端基础

常见失效不是数据库“突然不认索引”，而是优化器判断全表扫描更便宜，或者你的表达式无法利用现有索引：

- 对索引列做函数/计算
- 隐式类型转换
- 复合索引不满足最左前缀
- 低选择性字段
- `LIKE '%xxx'`
- 统计信息过旧
- 返回行数太大

Agent 最终会调用业务系统和数据库。LLM 再强，如果生成一个对 3 亿行表做全表扫描的 SQL，P99 一样会炸。因此 NL2SQL 还应该配 `EXPLAIN`、cost threshold、limit、statement timeout 和只读账户。

---

## 08-11. LangGraph Fan-out/Fan-in、Reducer 的核心问题是什么？并行节点怎么合并 State

Fan-out 本身不难，真正难的是多个并行节点同时写同一个 State 字段时的**合并语义**。

错误设计：

```text
Worker A → state.result = A
Worker B → state.result = B
```

最后谁覆盖谁取决于执行时序。

正确做法是每个字段声明 reducer：

```text
results: append/merge by step_id
cost: sum
errors: append
status: deterministic state transition
```

对于不能交换/不能结合的字段，不应该并行写共享 State，而要变成单写者 Aggregator。

这本质上和分布式系统里的 CRDT/Reducer/Single Writer 是同一类问题。

---

## 08-12. LangGraph / 图式 Agent 项目最容易踩的状态设计坑是什么

最大的坑通常不是 Graph 画错，而是把所有东西都塞进一个巨大 State：完整消息、Tool Result、大文档、临时缓存、业务事实、UI 状态全部混在一起。

结果是：

- Checkpoint 越来越大
- 每次节点执行序列化成本高
- 并行更新冲突
- 历史状态无法迁移
- 难以判断哪个字段是事实源

### 推荐分层

```text
Control State
  plan/status/current_step/version

Artifact Store
  large tool result / file / report

Conversation Transcript
  durable messages

Business State
  order/device/work-order truth
```

Graph State 只存控制面和引用，不要复制所有大对象。

---

## 本章面试总线

把这一章串起来，可以形成一句很强的工程回答：

> Agent 服务本质上仍然是一个分布式后端系统，只是多了一个高延迟、概率性、Token 计费的 LLM 依赖。所以我会把线程/虚拟线程、连接池、Bulkhead、Redis、MQ、数据库索引、流式协议、Sandbox 和 OTel 都纳入同一套容量与可靠性设计，而不会认为“用了 Agent 框架以后传统后端基础就不重要了”。
