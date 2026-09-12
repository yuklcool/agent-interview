# 2026 Agent 面试补充：Java 接入、Redis、MySQL 索引、意图识别、Chain vs Agent、RAG、向量库与 Tool Calling

> 来源：最新截图题库 Q4～Q11。
>
> 处理原则：先与仓库现有 01～08 章节做语义去重，不因为问法变化重复增加核心题号；本文件作为“高频面试问法 + 深度回答 + 实际项目映射”。
>
> 主要映射：
>
> - Q4 → `08-02 / 08-04 / 08-06 / 08-07`
> - Q5 → `08-03`
> - Q6 → `08-08 / 08-10`
> - Q7 → `02-01 / 02-02`
> - Q8 → `01-04 / 01-05 / 02-04`
> - Q9 → `06-01 / 06-07 / 06-09`
> - Q10 → `06-11 / 06-12`
> - Q11 → `03-02 / 03-03 / 03-04 / Tool Policy`

---

# Q4. Java 侧怎么把现有 Spring Boot 服务对接到大模型 Agent？同步还是异步？

## 面试官真正考什么

不是问你会不会用 `WebClient` 调一个 LLM API，而是在考：

1. 你是否能把 **Agent Runtime** 和已有 **Java Domain Service** 分层；
2. 你是否理解 Agent 请求天然可能是长耗时、多轮、可取消、可恢复的任务；
3. 你是否能设计同步调用、异步任务、流式输出、超时和幂等；
4. 你是否会避免“Java 再造一套 Agent Loop”和“LLM 直接写业务库”这两类架构问题。

## 核心结论

Spring Boot 不应该被改造成另一个 Agent Runtime。更稳的分层是：

```text
Web / App
   ↓
Spring Boot Gateway / Business API
   ↓
AgentDock / Agent Runtime
   ↓
Tool / MCP Adapter
   ↓
Spring Domain Service
   ↓
DB / Device / Order / WorkOrder
```

Agent 负责自然语言理解、开放式规划和 Tool 调度；Spring 保留权限、事务、领域规则、幂等和最终业务事实。

## 同步还是异步，不能只按“快/慢”回答

要先区分两种“同步/异步”含义：

```text
1. Java 线程模型：阻塞 / 非阻塞 / 虚拟线程
2. 业务交互模型：请求响应 / 长任务 Task
```

这两者不是一回事。

### 场景 A：单次推理 / 单 Tool / 2～3 秒完成

可以同步：

```text
HTTP Request
   ↓
Spring
   ↓
Agent/LLM
   ↓
Result
   ↓
HTTP Response
```

即使用同步语义，也可以用 `WebClient` 或 JDK 21 Virtual Thread 实现，不必把“同步业务语义”误解成“一定占死平台线程”。

### 场景 B：Agent 多轮 Tool Loop，可能 10～60 秒甚至更久

更推荐：

```text
POST /agent/tasks
   ↓
return task_id / run_id
   ↓
Agent Runtime background run
   ↓
SSE / WebSocket stream events
   ↓
run.completed / run.failed
```

因为长任务通常需要：

```text
cancel
reconnect
progress
checkpoint
human approval
retry/recovery
streaming tool events
```

如果只做一个长 HTTP request，网关超时、浏览器断线、重试导致重复 Run 都很难治理。

## 结合 AgentDock

AgentDock 当前的思路正适合解释这一题：

```text
Spring / Frontend
      ↓ REST
AgentDock Control Plane
      ↓
Task
      ↓
Nanobot / Pi / other Driver
      ↓
SSE Event Stream
```

Control Plane 负责 task lifecycle，真正 Runtime 可以是 nanobot、Pi 等。这样 Spring 不需要感知每一轮 Tool Loop。

## 结合 nanobot

nanobot 更适合做：

```text
Session
 → Context
 → LLM
 → Tool Call
 → Tool Result
 → next iteration
```

Java Service 只把领域能力暴露成 Tool/MCP：

```java
public WorkOrderResult createWorkOrder(CreateWorkOrderCommand cmd) {
    authz.check(cmd.projectId());
    validateBusinessRule(cmd);
    return service.create(cmd);
}
```

而不是让模型直接：

```text
UPDATE work_order ...
```

## 超时和重试怎么设计

外层至少要有：

```text
request_timeout
run_deadline
per_tool_timeout
max_iterations
idempotency_key
retry_budget
```

尤其是副作用 Tool：

```text
create_order / refund / create_work_order
```

超时不等于失败，可能是外部已经成功但响应丢失，因此要进入 `UNKNOWN`，再用 `business_request_id` 查状态。

## 1～2 分钟口述版

> 我不会把 Spring Boot 改造成第二个 Agent Runtime。更合理的是 Agent 负责 Session、Context、模型和 Tool Loop，Java 保留事务、权限和领域事实。调用方式要看任务语义：单轮短请求可以同步，但长时间多 Tool Agent 更适合提交 Task，返回 run_id，然后通过 SSE/WebSocket 流式拿结果，这样才能支持断线重连、取消、审批和恢复。像 AgentDock 可以做 Control Plane，nanobot 做 Runtime，Spring Domain Service 通过 MCP/REST 暴露工具能力。

---

# Q5. Redis 在 Agent 系统里能干什么？会话上下文和限流怎么设计？

## 核心结论

Redis 适合的是：

> **高频、短生命周期、并发协调、可重建的热状态。**

它不应该成为所有 Agent 数据的最终事实库。

## Redis 在 Agent 里的典型职责

```text
Session hot state
run_id → instance_id mapping
WebSocket/SSE cursor
Rate Limit
Idempotency Key
Distributed Lease
Task transient status
Tool read-cache
Pub/Sub / Stream
```

不适合只放 Redis 的：

```text
完整审计历史
订单/退款最终状态
重要 Tool Effect 事实
长期 Memory 原始事实
不可重建的业务数据
```

## 会话上下文怎么放

不要简单：

```text
session_id → 一整个 messages JSON
```

更稳的方式是拆层：

```text
Redis
├─ session:{id}:hot_state
├─ session:{id}:version
├─ session:{id}:active_run
├─ session:{id}:last_seq
└─ recent message cache

Durable Store
├─ transcript
├─ checkpoint
├─ audit
└─ artifact
```

一个示例：

```json
{
  "session_id": "s1",
  "version": 41,
  "active_run_id": "r8",
  "runtime_instance": "nanobot-17",
  "last_event_seq": 891,
  "updated_at": "..."
}
```

### 为什么要 `version`

两个节点同时处理同一 Session 时：

```text
Node A read version=41
Node B read version=41
```

如果都直接覆盖，就可能丢状态。

应该用：

```text
WATCH/MULTI
Lua CAS
或者 DB optimistic lock
```

保证：

```text
expected_version == current_version
```

才能提交。

## 限流怎么做

不要只回答 `INCR + EXPIRE`。

常见：

```text
Fixed Window
Sliding Window
Token Bucket
Leaky Bucket
```

Agent 更推荐按资源维度限流：

```text
user
workspace/tenant
model provider
agent instance
tool group
```

例如：

```text
rate:llm:{tenant}:{model}
rate:tool:{tenant}:database
rate:user:{user_id}
```

### 为什么 Agent 必须多维限流

因为：

```text
1 个用户请求
可能触发 10 次 LLM
+ 20 个 Tool Calls
```

如果只按 HTTP 请求限流，完全挡不住内部 fan-out。

## 实际场景

城市照明 Agent：

```text
用户 1 个问题
  ↓
SQL Tool × 3
Alarm API × 2
LLM × 4
```

应同时限制：

```text
user request budget
LLM token/QPS budget
DB tool concurrency
external API rate
```

## 面试追问

**Redis 挂了会话是不是就没了？**

如果 Redis 是正确定位的热状态层，不应该。Durable Transcript/Checkpoint 还在持久化层，可以重建热状态。

**为什么不用 Redis 分布式锁解决 Session 并发？**

锁只能保护临界区，不能解决旧结果晚到、进程崩溃后的 lease、外部副作用和版本冲突；仍需要 version/idempotency/state machine。

---

# Q6. MySQL 对话日志表量大后怎么建索引？哪些字段不适合建索引？

## 面试官真正考什么

不是让你背“最左前缀原则”，而是看你是否从 **查询模式** 设计索引，并理解索引的写放大、选择性和覆盖范围。

## 先看真实查询

假设表：

```text
conversation_log
- id
- tenant_id
- user_id
- session_id
- run_id
- role
- content
- status
- created_at
- metadata_json
```

### Query 1：查某 Session 最近 50 条

```sql
SELECT id, role, content, created_at
FROM conversation_log
WHERE tenant_id = ?
  AND session_id = ?
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

推荐复合索引：

```text
(tenant_id, session_id, created_at, id)
```

### Query 2：按 run_id 回放

```text
(run_id, id)
```

### Query 3：某用户最近会话

如果访问模式高频：

```text
(tenant_id, user_id, created_at)
```

重点是：**索引跟 Query Pattern 一一对应，不是见字段就加。**

## 为什么大 OFFSET 很差

```sql
LIMIT 50 OFFSET 1000000
```

数据库仍需要扫描/跳过大量记录。

更适合 Cursor Pagination：

```sql
WHERE session_id = ?
  AND (created_at, id) < (?, ?)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

## 哪些字段通常不适合直接建普通 B+Tree 索引

### 1. `content` 超长文本

聊天正文大、重复度高，而且常做语义/全文搜索，不适合普通 B+Tree 全字段索引。

需要全文检索时考虑：

```text
FULLTEXT
Elasticsearch/OpenSearch
独立检索系统
```

### 2. 大 JSON / BLOB

`metadata_json` 整字段建普通索引意义很弱。如果固定查询 JSON 内某几个键，可以：

```text
generated column
+ index generated column
```

### 3. 极低选择性字段单列索引

例如：

```text
role = user/assistant/tool
status = 0/1
is_deleted = 0/1
```

单独索引往往过滤能力很弱。

但注意：低选择性字段不是“永远不能进索引”。

例如：

```text
(tenant_id, status, created_at)
```

如果访问模式合理，仍可能有效。

### 4. 高频更新字段

索引越多，INSERT/UPDATE 写放大越严重。对日志类写多表尤其明显。

## 量再大怎么办

索引不是无限扩容方案。进一步要考虑：

```text
冷热分层
按时间归档
分区表
历史对象存储
读模型/Materialized View
检索系统分离
```

## Agent 场景特殊点

一次 Run 可能产生：

```text
user msg
assistant msg
Tool Call
Tool Result
checkpoint
trace event
```

几十甚至上百记录。

所以最好区分：

```text
conversation transcript
run/step state
tool events
trace
```

不要所有内容全塞一个“对话日志表”。

---

# Q7. 意图识别怎么做？全部交给大模型还是规则 + 模型混合？

## 核心结论

我会做分层 Hybrid Router，而不是“全部 LLM”或“全部规则”。

```text
Request
  ↓
Deterministic Rule Layer
  ↓
Light Classifier / Semantic Router
  ↓
LLM Router（长尾/组合意图）
  ↓
Policy Decision
```

## 规则适合什么

```text
/help
/status
固定命令
明确高风险入口
稳定业务编号
确定性正则/实体
```

优势：快、便宜、可解释、100% 可控。

劣势：规则爆炸，长尾语义维护困难。

## 分类器/Semantic Router 适合什么

标签相对固定，例如：

```text
设备查询
告警分析
能耗分析
工单
知识问答
```

可以用 embedding/classifier 做低延迟路由。

## LLM Router 适合什么

组合意图和上下文依赖：

> “看一下昨晚异常能耗，关联告警，如果确实异常帮我生成处置建议，但别创建工单。”

这里包含：

```text
query
analysis
cross-domain evidence
negative constraint
```

单标签分类就不够。

## 一个更稳的 Router 输出

```json
{
  "intent": ["energy_analysis", "alarm_correlation"],
  "requires_tools": true,
  "multi_step": true,
  "risk": "low",
  "side_effect_allowed": false,
  "confidence": 0.86
}
```

注意：Router 只能给建议，不应该直接决定权限。

```text
Intent = create_work_order
```

并不代表：

```text
user 有 create_work_order 权限
```

## 低置信度怎么办

```text
confidence high → route
confidence medium → LLM fallback / secondary classifier
confidence low + critical slot → clarify
```

不要为了追求“永不追问”让模型乱猜。

## nanobot / AgentDock 怎么结合

nanobot 当前更像执行 Runtime：模型基于 Context 和 Tool Schema 做动作选择；通用的业务 Intent Router 更适合放在 AgentDock/Gateway 上层。

```text
AgentDock/Gateway Router
  ↓
选择 runtime / agent / model / workflow
  ↓
nanobot AgentRunner
```

---

# Q8. LangChain 的 Chain 和 Agent 有什么区别？复杂场景为什么不能只用简单 Chain？

## 先纠正一个常见说法

不能说：

> “复杂场景一定不能用 Chain。”

很多高风险复杂业务反而应该主要用 Workflow/Chain/State Machine。

真正判断标准是：

```text
路径能不能预先枚举？
环境反馈是否高度不确定？
是否需要动态选择 Tool？
副作用风险有多高？
是否要求可审计顺序？
```

## Chain / Workflow

```text
A → B → C → D
```

或者明确状态图：

```text
QUOTE → CONFIRM → PAY → ISSUE
```

优势：

```text
可预测
可测试
易审计
容易恢复
成本稳定
```

## Agent

```text
Goal
 ↓
LLM decides action
 ↓
Tool
 ↓
Observation
 ↓
LLM decides next action
```

优势：适合事前难以枚举的路径：

```text
研究
诊断
代码修改
开放搜索
多工具探索
```

## 最佳实践不是 Chain vs Agent 二选一

通常是：

```text
Workflow owns critical state
         ↓
Agent owns local semantic uncertainty
```

例如旅行预订：

```text
Agent
→ 搜航班、酒店、比较偏好

Workflow
→ quote → lock → confirm → pay → issue
```

## 和 nanobot / AgentDock 对照

nanobot 的 `AgentRunner` 适合开放 Tool Loop；AgentDock 的 Workflow/Task 可以承担外层固定流程。支付、退款、派单等最终 Domain State 仍应该由 Java Service 状态机控制。

## 面试口述版

> Chain/Workflow 的控制流主要由代码决定，Agent 的下一步更多由模型根据 observation 动态决定。复杂不等于一定要 Agent，高风险交易流程即使复杂也应该保持确定性；真正实用的是 Workflow 约束边界，Agent 只在搜索、理解、诊断等开放步骤里拥有局部自主权。

---

# Q9. RAG 基础流程怎么讲？Chunk 大小怎么定，太大太小分别有什么问题？

## 完整 RAG 不是“Embedding → Vector DB → LLM”

Offline：

```text
Source
 ↓
Parser / OCR / Layout
 ↓
Normalization
 ↓
Structure-aware Chunking
 ↓
Metadata / ACL / Version
 ↓
Embedding + Lexical Index
 ↓
Publish
```

Online：

```text
User Query
 ↓
Query Understanding / Rewrite
 ↓
ACL / Metadata Filter
 ↓
BM25 + Dense Retrieval
 ↓
Fusion / RRF
 ↓
ReRank
 ↓
Parent / Neighbor Expansion
 ↓
Context Budget
 ↓
LLM
 ↓
Grounded Answer + Citation
```

## Chunk 核心不是固定数字

优化目标是：

```text
语义完整性
× 检索区分度
× Context 成本
```

### 太小

```text
标题和正文分离
表头和数据分离
条件和例外分离
函数签名和实现分离
上下文不足
```

### 太大

```text
一个向量混多个主题
召回粒度变粗
rerank 成本高
LLM token 浪费
权限/版本粒度变粗
```

## 实际怎么切

优先按结构：

```text
Markdown → Heading/Section
FAQ → Q + A
代码 → Class/Function
表格 → Header + Row Group
SQL Schema → Table + Columns + Keys + Relations
PDF → Layout Block + Section
```

Token 大小只是二次约束。

`300～800 tokens` 可以当 baseline，而不是标准答案。

## Parent-Child

为了同时获得“小块好召回”和“大块有上下文”：

```text
Child Chunk → Retrieval
      ↓
Parent Section → LLM Context
```

## OpenViking 可以怎么讲

OpenViking 的思路不是只做平面 Chunk，而是组织：

```text
L0 Abstract
L1 Overview
L2 Detail
```

先找到相关 Context，再逐层展开，也是在解决“召回粒度和上下文粒度不一致”。

## 怎么证明 Chunk 选对了

不能凭感觉。

同一业务 Query Set 比较：

```text
Recall@K
MRR / nDCG
answer grounding
citation coverage
token cost
latency
```

---

# Q10. 向量库用过哪个？Milvus 和 Chroma 怎么选？

## 面试官真正考什么

不是看你背过多少产品，而是看你会不会从 workload 和运维条件选型。

## 先给判断维度

```text
向量规模
查询 QPS
过滤复杂度
是否需要 HA
更新频率
部署复杂度
metadata/ACL
hybrid search
团队运维能力
```

## Chroma

通常更适合：

```text
本地开发
PoC
小中规模应用
嵌入式/轻运维场景
快速实验
```

优势是 API 简单、开发体验好、起步快。

面试里不要说“Chroma 不能生产”，而应说：

> 如果系统需要大规模分布式向量检索、复杂容量规划和独立 HA，我通常不会优先把 Chroma 作为核心检索基础设施；但在开发、原型和轻量业务里它非常合适。

## Milvus

更适合：

```text
大规模向量
专业 ANN
较高吞吐
分布式检索基础设施
独立扩缩容
```

但代价是：

```text
部署/运维更复杂
metadata 与业务库同步
容量/索引参数治理
集群成本
```

## 一个真实选型例子

### 场景 A

```text
50 万文档
内部知识库
单团队
QPS 很低
```

我会优先简单方案：

```text
pgvector / Chroma
```

而不是先上 Milvus 集群。

### 场景 B

```text
5 亿向量
多租户
高并发 ANN
独立检索团队
```

Milvus 这类专业向量基础设施更合理。

## 不要忘了 pgvector / Elasticsearch

真正面试里最好补一句：

```text
Java + PostgreSQL 为主、ACL relational filter 很重 → pgvector
BM25 + vector hybrid 很重、已有 ES → Elasticsearch/OpenSearch
大规模独立 ANN → Milvus
本地/PoC/轻量 → Chroma
```

这说明你在做工程选型，而不是产品站队。

---

# Q11. Tool Calling 怎么约束大模型传参？Pydantic 校验够不够，还需要什么兜底？

## 核心结论

Pydantic / JSON Schema 只能解决：

> **结构正确。**

企业级 Tool Runtime 至少还要解决：

```text
结构正确
业务正确
权限正确
状态正确
风险可接受
副作用可恢复
```

## 完整链路

```text
LLM Tool Proposal
       ↓
Grammar / JSON Parsing
       ↓
Pydantic / JSON Schema
       ↓
Domain Validation
       ↓
Authorization
       ↓
Risk / Approval Policy
       ↓
Idempotency / Preconditions
       ↓
Rate Limit / Timeout
       ↓
Sandbox / Network Boundary
       ↓
Tool Execution
       ↓
Canonical ToolResult
```

## 第一层：Pydantic / JSON Schema

负责：

```text
required
类型
enum
range
format
additionalProperties
array limits
```

例如：

```python
class RefundArgs(BaseModel):
    order_id: str
    amount: Decimal = Field(gt=0)
```

它可以挡住：

```text
amount = "abc"
amount = -10
```

但挡不住：

```text
订单总额 100
模型请求退款 99999
```

## 第二层：Domain Validation

必须去业务系统确认：

```text
订单是否存在
订单属于谁
可退款金额是多少
当前状态是否允许退款
是否已经退款过
```

例如：

```text
refund_amount <= refundable_amount
order.status ∈ REFUNDABLE_STATES
```

## 第三层：Authorization

必须检查：

```text
user
tenant
project
agent role
resource scope
```

一个合法的 `device_id=D001` 也可能属于别的项目。

## 第四层：Risk / Human-in-the-loop

高风险动作：

```text
refund
delete
restart
send_message
execute_shell
write_sql
```

可根据风险级别要求：

```text
explicit confirmation
four-eyes approval
workflow precondition
```

## 第五层：Idempotency + UNKNOWN

副作用 Tool 必须考虑：

```text
request sent
 ↓
external succeeded
 ↓
network timeout
```

Agent 看到 Timeout 时不能直接重试。

需要：

```text
business_request_id
idempotency_key
query_status
reconcile
```

## 第六层：Tool Result 也要有 Contract

不要只返回：

```text
success
```

建议：

```json
{
  "status": "OK",
  "code": "SUCCESS",
  "data": {},
  "request_id": "req-1",
  "retryable": false,
  "freshness": "..."
}
```

## nanobot / AgentDock 怎么映射

nanobot 可以负责 Tool Registry、Tool Call、参数解析、执行和 observation loop；AgentDock 可以在平台层做租户、凭证、容器、Egress 和 Runtime 分配；真正业务规则仍由 Java Domain Service 校验。

因此安全边界不是：

```text
LLM → Pydantic → Tool
```

而是：

```text
LLM
 ↓ proposal
Runtime Schema
 ↓
Policy
 ↓
Business Service
 ↓
Authoritative State
```

## 1～2 分钟口述版

> Pydantic 只保证参数结构符合 Schema，不能保证业务合法、权限合法或副作用安全。生产 Tool Calling 我会分成结构校验、Domain Validation、Authorization、Risk/HITL、Idempotency、Timeout/Rate Limit 和结果契约几层。模型只有提出动作的权力，真正执行必须经过 Runtime 和业务系统。尤其退款、下单这类 Tool，如果超时可能是 UNKNOWN，不能简单 retry，要通过幂等键和状态查询做 reconciliation。

---

# 这 8 道题的统一工程主线

把它们放到同一个系统里，其实是同一条链：

```text
User
 ↓
Intent Router
 ↓
Workflow / Agent Decision
 ↓
AgentDock / Gateway
 ↓
nanobot / Pi Runtime
 ↓
Tool Proposal
 ↓
Schema + Policy
 ↓
Spring Boot Domain Service
 ↓
MySQL/PostgreSQL / External API

与此同时：
Redis
→ hot session / rate limit / idempotency / coordination

RAG
→ chunk / retrieval / vector store / rerank / context
```

高级面试真正看的是：

> 你能不能把 LLM 的概率决策嵌入到已有的 Java、数据库、Redis、检索、权限和分布式系统里，而不是只会调用模型 API。
