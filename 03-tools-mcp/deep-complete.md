# 03. Tool、Function Calling、MCP、Skills 与 Agent Runtime——高级面试深度版

> 这一章不再把 Tool/MCP 当成“会定义几个 JSON Schema”来背，而是按真实 Agent Runtime 的执行链来理解：**模型只负责提出候选动作，Runtime 决定动作能不能执行，Tool/MCP Adapter 负责怎么执行，业务系统决定这件事在业务上是否合法。**
>
> 建议面试时不要只回答“是什么”，而是始终沿着下面这条主线展开：
>
> ```text
> User Goal
>    ↓
> Capability Discovery
>    ↓
> Tool / Skill Retrieval
>    ↓
> Model-visible Tool View
>    ↓
> LLM Tool Proposal
>    ↓
> Schema Validation
>    ↓
> Authorization / Risk / Business Validation
>    ↓
> Tool Executor / MCP Client
>    ↓
> MCP Server / REST / CLI / Local Tool
>    ↓
> Domain Service / DB / External System
>    ↓
> Canonical Tool Result
>    ↓
> Observation
>    ↓
> Next LLM Turn
> ```
>
> 本页按 6 个模块整理，共 24 道主问题。每道题都给出：**面试主答、追问方向、工程落地、常见误区**。面试时不必逐字背，重点是把执行链和边界讲清楚。

---

# 模块一：Tool Contract 与 Function Calling

## 03-01. Function Calling 到底是什么？LLM 是真的“调用了函数”吗？

### 面试主答

不是。LLM 本身不会直接执行 Python、Java、Shell、数据库或 HTTP API。Function Calling 本质上是：

1. Runtime 把工具名称、描述、参数 Schema 提供给模型；
2. 模型根据上下文生成一个结构化的 **Tool Call Proposal**；
3. Runtime 解析这个 Proposal；
4. Runtime 在自己的 Tool Registry 中找到对应真实实现；
5. Runtime 做权限、参数、风险和业务校验；
6. 真正执行 Tool；
7. Tool Result 作为 observation 再发给模型。

所以：

```text
LLM 负责决定“我想调用什么”
Runtime 负责决定“你能不能调用、怎么调用”
Tool 实现负责真正产生副作用
```

### 完整执行链

```text
User
 ↓
LLM
 ↓ produces
ToolCall(name, arguments)
 ↓
Agent Runtime
 ↓
Tool Registry lookup
 ↓
Validation / AuthZ / Risk
 ↓
Tool.execute()
 ↓
External System
 ↓
ToolResult
 ↓
messages.append(tool_result)
 ↓
LLM next turn
```

### 面试官继续追问：为什么这个区分重要？

因为很多安全问题都来自把“模型建议”误认为“系统命令”。模型输出永远只能是候选动作，不能直接成为系统级 side effect。

例如模型生成：

```json
{
  "name": "delete_user",
  "arguments": {"user_id": "10001"}
}
```

这不代表应该执行。Runtime 至少还要检查：

```text
tool 是否存在
当前 Agent 是否可见
当前 user 是否授权
参数是否合法
业务状态是否允许
是否需要用户确认
是否需要幂等键
```

### 常见错误回答

> Function Calling 就是大模型调用后端函数。

这句话过于粗糙。更准确的是：**LLM 生成调用意图，Runtime 执行调用。**

---

## 03-02. 一个企业级 Tool Schema 应该怎么设计？为什么 JSON Schema 远远不够？

### 面试主答

一个 Tool 不应只看成 `name + description + parameters`，而应该看成至少五层 Contract：

```text
1. Discovery Contract
2. Input Contract
3. Business Validation Contract
4. Execution Policy
5. Result / Error Contract
```

### 第一层：Discovery Contract

主要回答：

> 模型什么时候应该选这个 Tool？什么时候不应该选？

例如差的描述：

```text
query_data
查询数据
```

更好的描述：

```text
query_device_status
查询当前项目内一个或多个照明设备的在线、开关、功率和调光状态。
不要用于查询历史告警，历史告警请使用 list_device_alarms。
```

好的 description 应体现：

```text
能做什么
不能做什么
适用对象
相邻 Tool 的边界
```

### 第二层：Input Contract

```json
{
  "type": "object",
  "properties": {
    "device_ids": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "maxItems": 100
    },
    "fields": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["online", "switch", "power", "dimming"]
      }
    }
  },
  "required": ["device_ids"],
  "additionalProperties": false
}
```

原则：

```text
能 enum 就不要自由文本
能数组就不要逗号字符串
限制 maxItems
时间统一 format
关闭 additionalProperties
字段表达业务概念而不是底层实现
```

### 第三层：Business Validation

Schema 只能证明：

```text
参数“长得对”
```

不能证明：

```text
业务“做得对”
```

例如：

```json
{"refund_amount": 999999}
```

完全可能符合 number 类型，但订单金额只有 100。

所以完整链路应该是：

```text
JSON Parse
 ↓
Schema Validation
 ↓
Domain Validation
 ↓
Authorization
 ↓
Risk Policy
 ↓
Execution
```

### 第四层：Execution Policy

建议 Tool Metadata 至少考虑：

```text
read_only
side_effect
idempotent
concurrency_safe
risk_level
required_scopes
requires_confirmation
retry_policy
timeout
rate_limit_group
```

### 第五层：Result Contract

不要只返回字符串：

```text
success
```

而应尽量有稳定结构，例如：

```json
{
  "status": "OK",
  "data": {},
  "source": "lighting-db",
  "freshness": "2026-09-11T10:00:00+08:00",
  "request_id": "req-123"
}
```

### 一句话总结

> JSON Schema 是 Tool Contract 的一部分，不是整个 Tool Contract。

---

## 03-03. 参数格式正确，但业务语义错误，Runtime 应该在哪一层拦截？

### 典型场景

模型调用：

```json
{
  "device_id": "D001",
  "start_time": "2026-09-10T18:00:00+08:00",
  "end_time": "2026-09-01T18:00:00+08:00"
}
```

Schema 完全可能合法：三个字段都是 string/date-time。

但：

```text
start_time > end_time
```

这是业务语义错误。

另一个例子：

```json
{"device_id":"D001"}
```

D001 格式合法，但属于另一个 tenant。

### 推荐三层 Validator

```text
Structural Validator
  ↓ JSON / required / enum / type
Domain Validator
  ↓ state / range / invariant
Authorization / Policy
  ↓ user / tenant / project / risk
```

业务规则不要复制到 Prompt，也不要全部复制到 Tool Adapter。最终最好调用真实 Domain Service 做 authoritative validation。

### 错误需要分类

建议区分：

```text
INVALID_ARGUMENT
BUSINESS_RULE_VIOLATION
FORBIDDEN
CONFLICT
NO_RESULT
RETRYABLE_ERROR
UNKNOWN
```

因为不同错误应该触发不同 Agent 行为：

```text
INVALID_ARGUMENT → 可以修参数
BUSINESS_RULE_VIOLATION → 应改变计划
FORBIDDEN → 不应继续换写法撞权限
RETRYABLE_ERROR → 可有限重试
UNKNOWN → 先 reconcile，不能盲重试
```

---

## 03-04. 模型参数幻觉、JSON 错、枚举错，怎么做自动修复而不产生危险行为？

### 面试主答

自动修复要分层，不要把所有错误交给一个“再想一次”的 LLM。

```text
Parse Error
  ↓
Deterministic syntax repair（仅安全语法）
  ↓
Schema Error
  ↓
结构化 validation error 返回模型
  ↓
Semantic Error
  ↓
Domain error + allowed alternatives
  ↓
Repeated Failure
  ↓
Stop / clarify / change strategy
```

### Repair Budget

每个 Run 应记录类似：

```text
argument_repair_count
tool_selection_repair_count
same_error_fingerprint_count
```

如果同一个 Tool、同一个参数、同一个错误连续出现多次，就已经不是“偶发格式错”，而是 no-progress loop。

### 不能做什么

高风险 Tool 不能靠模糊纠错直接执行。

例如模型输出：

```text
refundUsr
```

Registry 里有：

```text
refund_user
refund_order
```

可以提示候选，但不能：

```text
字符串相似度最高 → 自动执行 refund_user
```

### Constrained Decoding 能解决什么？

可以提高：

```text
JSON 语法正确率
结构合法率
枚举命中率
```

但解决不了：

```text
业务正确
权限正确
真实世界状态正确
```

一句话：

> Grammar 正确 ≠ Schema 正确 ≠ 业务正确 ≠ 有权限执行。

---

## 03-05. Tool Result 为什么不能只返回自然语言？HTTP 200 为什么不等于成功？

### 面试主答

HTTP 200 只表示 transport 层成功。

真正至少要区分：

```text
Transport Success
Tool Execution Success
Business Success
Result Completeness
Result Freshness
```

例如航班接口 HTTP 200，但返回：

```json
{
  "flight": "CI123",
  "price": null,
  "inventory": null
}
```

不能让模型自己脑补“有票”。

### Canonical ToolResult

推荐统一：

```json
{
  "status": "PARTIAL",
  "code": "PROVIDER_PARTIAL_DATA",
  "data": {},
  "missing": ["price", "inventory"],
  "source": "provider-a",
  "freshness": "2026-09-11T10:00:00+08:00",
  "retryable": true,
  "request_id": "req-123"
}
```

### 为什么统一结果重要

如果每个 Tool/MCP Server 都返回自己的一套错误语言，模型就必须理解几十套 provider-specific 语义。

更好的架构：

```text
Provider A ┐
Provider B ├→ Adapter → Canonical ToolResult → Agent Runtime
REST C     ┘
```

模型看到稳定语义，Adapter 负责兼容差异。

---

# 模块二：Tool Registry、权限与 Progressive Disclosure

## 03-06. Tool Registry 是什么？为什么它是 Agent Runtime 的核心组件？

### 面试主答

Tool Registry 可以理解为 Agent Runtime 的 **Capability Catalog + Name → Implementation 映射表**。

它通常维护：

```text
Tool name
Description
Input schema
Result schema
真实 handler / executor
Metadata
Permissions
Risk
Concurrency capability
Version
```

例如：

```python
registry = {
    "read_file": ReadFileTool(...),
    "query_database": QueryDatabaseTool(...),
    "restart_service": RestartServiceTool(...),
}
```

Runtime 一方面从 Registry 生成模型可见 Tool Schema，另一方面在模型产生 Tool Call 后做：

```text
name lookup
schema validation
permission check
execution dispatch
```

### 为什么 Tool 名必须精确匹配

模型如果输出：

```text
readFile
```

而 Registry 中只有：

```text
read_file
```

应该返回 Unknown Tool，并可提示：

```text
Did you mean read_file?
```

但不能偷偷模糊匹配后执行。

### 一句话总结

> Tool Registry 是 LLM action space 与真实程序能力之间的映射层。

---

## 03-07. 多 Agent 共享一个 Tool Registry，怎么限制某些角色不能调用某些 Tool？

### 面试主答

推荐：

```text
一个 Shared Registry
+
每个 Agent 独立 Capability View
+
执行时强制 Authorization
```

而不是每个 Agent 复制一份 Registry。

### 第一层：Model-visible Tool View

```text
Full Registry
   ↓ role/scope projection
Analyst View
Developer View
Admin View
```

例如 Analyst 只看到：

```text
read_file
query_database
```

Developer 还可以看到：

```text
write_file
exec_shell
```

Admin 才能看到：

```text
restart_service
delete_resource
```

### 第二层：Execute-time Authorization

即使模型手工生成一个未暴露 Tool：

```json
{"name":"restart_service"}
```

Runtime 也必须重新做：

```text
subject = user + agent + role + tenant
resource = tool + target resource
action = execute/restart/delete/query
policy.check(subject, action, resource)
```

### 为什么“不给模型看”不等于权限控制？

因为 Tool Visibility 只减少误调用概率，不是安全边界。

```text
Visibility = action space optimization
Authorization = security boundary
```

### 再往下还要做资源级权限

能调用 `query_database` 不代表可以查所有库：

```text
Tool-level permission
   ↓
Action-level permission
   ↓
Resource-level permission
```

例如：

```text
Analyst 可以 query_database
但只能 query project_001
并且只能 SELECT
```

---

## 03-08. Tool 太多时，为什么不能把所有 Schema 一次性塞给模型？

### 面试主答

当 Tool 从 10 个增长到 100、300、1000 个以后，全量 Schema 注入会产生四类问题：

```text
1. Token 成本急剧增加
2. Prompt cache / latency 增加
3. 相似 Tool 之间 selection confusion
4. 模型注意力被大量无关 capability 稀释
```

因此 Tool 选择应该变成一个 Retrieval 问题：

```text
User Goal
  ↓
Intent / Domain Router
  ↓
Permission Filter
  ↓
Tool Metadata Retrieval
  ↓ Top-K
Candidate Re-rank
  ↓
Full Schema Hydration
  ↓
LLM Tool Selection
```

### Tool Metadata 可以包含什么

```text
name
short_summary
domain
verbs
entities
tags
risk
required_scopes
examples
embedding
version
```

### 关键思想

> 不要先把完整 Tool Schema 加载进上下文后再过滤，而应该先对轻量 Metadata 做检索，只有入选 Tool 才 hydrate 完整 Schema。

---

## 03-09. Tool Schema 太多导致上下文爆炸，Progressive Disclosure 怎么真正落地？

### 面试主答

可以把 Tool 信息拆成三层：

```text
L0: name + one-line capability
L1: detailed description + examples + risk + boundaries
L2: full JSON Schema + edge cases + result contract
```

初始只暴露 L0 或少量 L1，真正候选确定后才加载 L2。

### 一个完整过程

```text
300 Tools
   ↓
10 Tool Domains
   ↓
当前任务命中 database
   ↓
database 下 30 个 Tool Metadata
   ↓ semantic retrieval
Top 5
   ↓
Hydrate 5 个 Full Schema
   ↓
LLM
```

### Tool Registry API 可以怎么设计

```python
candidates = registry.search_tools(
    query=user_message,
    subject=current_subject,
    top_k=6,
)

schemas = registry.hydrate(candidates)
```

这里：

```text
search != hydrate
```

`search` 操作轻量索引；`hydrate` 才把完整执行契约加入模型上下文。

### Session Tool Cache

如果用户连续四轮都在分析数据库：

```text
看 schema
查 alarm
按项目统计
看过去 7 天
```

没必要每轮重新从 300 个 Tool 检索。

可以维护：

```text
session.active_toolset
session.active_domains
registry_version
```

只有意图发生明显切换时重新扩展候选集。

### 兜底方式

可以额外暴露：

```text
search_tools(query)
```

让模型在当前 Toolset 不够时主动发现新能力。

推荐组合：

```text
Runtime 自动 Top-K Retrieval
+
LLM search_tools 兜底
```

---

## 03-10. OpenViking 的 L0/L1/L2 和 Tool Progressive Disclosure 是一回事吗？最终 LLM 怎么调用真实 Tool？

### 面试主答

不是完全一回事。

OpenViking 的 L0/L1/L2 主要解决的是 **Context / Skill / Resource 的渐进式加载**，而不是把一个 Tool JSON Schema 自动切成三段。

可以理解为：

```text
L0 = Abstract
L1 = Overview
L2 = Detail / 原始内容
```

例如一个 Skill：

```text
lighting-analysis/
├── .abstract.md
├── .overview.md
├── SKILL.md
├── references/
└── scripts/
```

模型先通过 L0 判断：

```text
这个 Skill 是否相关？
```

再用 L1 判断：

```text
值得不值得继续深入？
```

最后读 L2：

```text
具体应该怎么做？
```

### 最终执行仍然走 Tool Runtime

```text
User
 ↓
OpenViking retrieval
 ↓
Skill / Context L0 → L1 → L2
 ↓
LLM 学会“应该怎么做”
 ↓
LLM 产生具体 Tool Call
 ↓
AgentLoop
 ↓
ToolRegistry
 ↓
Tool Executor
 ↓
DB / MCP / API / OS
```

所以：

```text
OpenViking L0/L1/L2
= 解决“模型需要知道哪些上下文/技能”

Tool Registry
= 解决“模型产生动作后怎么映射到真实能力”
```

### Skill 也不是 Tool

Skill 更像任务操作手册：

```text
遇到照明故障分析
先读 schema
再查 alarm
然后按项目聚合
```

真正执行的是：

```text
read_file
query_database
get_project_info
```

### 面试高分点

> OpenViking 的 Progressive Disclosure 可以和 Tool Retrieval 叠加：前者控制 Skill/Context 注入，后者控制 Tool Schema 注入。两者解决的是两个不同维度的上下文爆炸。

---

# 模块三：MCP 协议与 Runtime

## 03-11. MCP 和普通 Tool Callback / Function Calling 到底是什么关系？

### 面试主答

Function Calling 是 **模型表达 Tool Call 的机制**；本地 Tool Callback 是 **Runtime 内部执行接口**；MCP 是 **Host 与外部能力之间的标准协议层**。

可以这样看：

```text
LLM Function Calling
        ↓
Agent Runtime
        ↓
Tool Adapter
   ┌────┼────┐
Local  REST  MCP Client
              ↓
          MCP Server
```

MCP 并没有取代 Function Calling。

模型仍然需要先决定：

```text
我要调用哪个 Tool
```

只是这个 Tool 的真实实现可能通过 MCP Client 去远程执行。

### 老工具怎么迁移

推荐：

```text
Existing Domain Service
      ↓
MCP Adapter / MCP Server
      ↓
MCP Client
      ↓
Tool Registry
```

不要为了接 MCP 把业务 Service 重写一遍。

### 迁移期注意

不要同时把两个同义能力都暴露给模型：

```text
query_device
mcp_query_device
```

否则模型不知道应该选谁。

MCP 是协议实现细节，不应该污染业务语义名称。

---

## 03-12. MCP Host、Client、Server 分别是什么？完整调用链是什么？

### 面试主答

最容易讲错的是把 Host 和 Client 混成一个概念。

```text
User
 ↓
Host / Agent Runtime
 ↓
MCP Client
 ↓ protocol connection
MCP Server
 ↓
Business Adapter
 ↓
Domain Service / DB / API
```

### Host

负责更大的 Agent 运行环境，例如：

```text
模型调用
Context
Conversation
Agent Loop
Tool Registry
权限
UI
Session
```

### MCP Client

通常是 Host 中负责：

```text
建立 MCP 连接
发现 server capability
list tools/resources/prompts
call tool
read resource
接收 result / notification
```

### MCP Server

负责把某些能力通过标准协议暴露出去。

### 关键点

Tool Result 回到 Host 并不是结束：

```text
MCP Server Result
 ↓
MCP Client
 ↓
Agent Runtime
 ↓
Observation
 ↓
LLM next turn
```

模型可能继续调用其他 Tool，直到完成任务。

---

## 03-13. MCP 中 Tool、Resource、Prompt 有什么区别？为什么不能都设计成 Tool？

### Tool

强调：

```text
Action / Computation / Side Effect
```

例如：

```text
create_issue
query_database
restart_service
```

### Resource

更像可读取的上下文或内容对象：

```text
文件
文档
配置
数据库 schema
UI resource
```

### Prompt

更像 Server 提供给 Host/用户的可复用提示模板或工作流入口。

### 为什么不能全部 Tool 化

如果所有信息获取都变成 Tool：

```text
模型 action space 过大
语义变乱
无副作用的 context 与有副作用 action 混在一起
治理困难
```

面试时可以这样概括：

```text
Resource = 给模型/Host“看什么”
Prompt   = 提供“怎么问/怎么组织任务”
Tool     = 真正“做什么”
```

但最终具体能力是否由模型直接选择，还取决于 Host 的 Runtime 设计。

---

## 03-14. 一个 MCP Server 应该负责什么？哪些东西绝对不应该全塞进 MCP Server？

### MCP Server 应负责

```text
Capability registration
Tool/resource/prompt declaration
Schema
Protocol handling
Input decoding
调用业务 Service
结果规范化
必要的 server-side auth boundary
```

### 不建议全塞进去

```text
核心交易事务
长期业务规则
订单状态机
复杂 Saga
租户主权限模型
数据库 Repository 细节
Agent Planning
Agent Loop
```

推荐：

```text
MCP Server
   ↓ Adapter
Domain Service
   ↓
Repository / External API
```

### 为什么

同一 Domain Service 未来可能同时被：

```text
MCP
REST
后台任务
Web Controller
CLI
```

调用。如果业务逻辑全部写死在 MCP Server 里，MCP 就从“协议适配层”变成了“业务系统本身”。

---

## 03-15. CLI Tool、REST Tool、本地 Tool、MCP Tool 应该怎么选？

### 本地 Tool

适合：

```text
进程内高性能能力
简单 Python/Java 方法
与 Runtime 强绑定
```

优点：低延迟、实现简单。

缺点：跨语言、跨框架复用差。

### CLI

适合已有成熟命令行生态：

```text
git
kubectl
terraform
ffmpeg
```

问题：

```text
输出可能非结构化
权限继承进程
跨平台差异
stdout/stderr 解析复杂
```

### REST

适合稳定业务服务，尤其已有成熟：

```text
Auth
Gateway
Tracing
Rate Limit
SLA
```

的企业系统。

### MCP

更适合：

```text
希望同一个能力被多种 Agent Host 发现和复用
希望统一 capability discovery / schema / call 协议
需要更标准的 Agent 工具生态
```

### 选择原则

> 不要为了“Agent 化”强行 MCP 化。

如果只有一个内部 Runtime 调一个已有 REST 服务，加一层 MCP 未必有收益；如果同一能力要服务 nanobot、IDE Agent、桌面 Host、其他 Agent Framework，MCP 的互操作收益就明显更大。

---

# 模块四：Skills、MCP Apps 与能力编排

## 03-16. Skill、Tool/MCP、Rule 三者是什么关系？

### 面试主答

这是 Agent 系统中非常容易混淆的三个层次：

```text
Rule
= 不能做什么 / 必须满足什么

Skill
= 这一类任务通常怎么做

Tool
= 真实执行什么动作
```

例如退款场景：

```text
Rule:
退款 > 1000 必须人工确认

Skill:
先查询订单 → 判断可退金额 → 核对用户意图 → 再调用退款 Tool

Tool:
query_order
refund_order
```

### 为什么 Skill 不能当安全边界

Skill 本质仍然是给模型看的上下文/操作知识。

即使 Skill 写：

```text
禁止越权退款
```

真正安全仍然应该在：

```text
Runtime Authorization
Domain Service
```

### Skill 的价值

Skill 主要减少：

```text
Prompt 里重复写 SOP
复杂任务每次都重新规划
跨 Agent 重复工程经验
```

---

## 03-17. Skill Registry / Discovery / Invocation 应该怎么设计？

### Skill Registry Metadata

建议有：

```text
skill_id
version
name
description
domain
capabilities
triggers
required_tools
required_scopes
context_dependencies
examples
source
signature / trust level
```

### Discovery

不要把几百个 Skill 全文全塞进去。

应该：

```text
User Goal
 ↓
Skill Metadata Retrieval
 ↓
Permission / Trust Filter
 ↓
Candidate Skills
 ↓
Load Skill Body
```

### Invocation

Skill 通常不是像 Tool 一样：

```text
skill.execute()
```

而是：

```text
加载 Skill → 改变当前 Context / Plan → 模型再调用真实 Tool
```

### 安全

第三方 Skill 是外部指令源，必须考虑：

```text
来源
版本
审批
签名
恶意 Prompt
依赖 Tool
权限范围
sandbox
```

不能因为它叫 `SKILL.md` 就默认可信。

---

## 03-18. Skill 和长期 Memory 有什么区别？为什么不能互相替代？

### Skill

回答：

```text
“这一类任务应该怎么做？”
```

通常：

```text
相对稳定
可版本化
可共享
与具体用户弱绑定
```

例如：

```text
如何分析 PostgreSQL 慢 SQL
```

### Memory

回答：

```text
“这个用户/项目过去发生过什么？偏好什么？”
```

通常：

```text
有主体
有时间
有来源
会变化
```

例如：

```text
当前项目使用 PostgreSQL 17
用户偏好先看 EXPLAIN ANALYZE
```

### 为什么不能互相替代

把用户偏好写进 Skill：

```text
会污染其他用户
```

把通用操作 SOP 写成每个用户 Memory：

```text
会重复、难升级、难版本管理
```

### OpenViking 的启示

即使 resources / memories / skills 可以统一存储，也不代表它们语义相同。

```text
统一 Storage
≠
统一 Semantic Type
```

---

## 03-19. MCP Apps 是什么？它和普通 MCP Tool 的差别在哪里？

### 面试主答

普通 MCP Tool 主要解决：

```text
模型调用能力 → 返回 text / structured data
```

MCP Apps 在此基础上增加：

```text
Tool + UI Resource
```

也就是说，一个 Tool 可以声明关联的 UI resource；Host 在 Tool 被调用后获取 UI resource，并在受控的嵌入环境中渲染交互界面。

### 典型调用链

```text
LLM
 ↓ calls tool
MCP Server
 ↓ returns tool result
Host
 ↓ sees linked UI resource
Fetch ui:// resource
 ↓
Sandboxed UI / iframe
 ↓
展示 chart / form / dashboard
```

UI 还可以通过 Host 提供的桥接能力继续：

```text
调用 server tool
发送消息
接收 tool input/result
```

### 非常重要的区分

```text
模型上下文
≠
UI 渲染上下文
```

有些结构化数据可以主要给 UI 使用，不一定需要把整份 HTML 或所有界面状态直接发给模型。

### 为什么 Host 能力很重要

MCP Server 提供 UI resource 并不代表所有客户端都能渲染。

最终是否支持：

```text
iframe
AppBridge / SDK
双向交互
UI 生命周期
```

取决于 Host 是否实现 MCP Apps 能力。

这也是为什么“nanobot 支持 MCP Client”不自动等于“nanobot 支持 MCP Apps Host”。

---

# 模块五：可靠性、安全、调度与可观测性

## 03-20. 多个 Tool 有依赖关系时，Runtime 应该怎么调度？为什么不是简单 priority？

### 面试主答

真实多 Tool 执行应该看成 Execution Graph，而不是排序数组。

例如：

```text
search_order
    ↓
validate_refundable
    ↓
refund_order
```

同时：

```text
query_user_profile ─┐
                    ├→ generate_reply
query_policy ───────┘
```

有的步骤有 dependency，有的可以并行。

### Scheduler 应考虑

```text
depends_on
required / optional
risk
side_effect
idempotent
concurrency_safe
timeout
deadline
freshness_ttl
cost
```

### 为什么 freshness 很重要

天气、库存、价格这种数据：

```text
离真正使用越近越好
```

用户偏好、静态配置：

```text
可以提前获取和缓存
```

### 并发执行

只有显式声明：

```text
concurrency_safe = true
```

并且不存在依赖/副作用冲突的 Tool 才适合 batch 并发。

---

## 03-21. Tool 执行到一半超时、返回 UNKNOWN、外部系统其实成功了，怎么处理？

### 面试主答

这是 Agent 工程里比“模型选错 Tool”更危险的问题。

例如：

```text
Agent 调用 refund_order
 ↓
外部支付平台完成退款
 ↓
HTTP 响应在网络层丢失
 ↓
Runtime timeout
```

此时系统不知道：

```text
到底成功还是失败？
```

不能直接 retry。

### 正确做法

```text
PENDING
RUNNING
SUCCEEDED
FAILED
UNKNOWN
```

如果进入 UNKNOWN：

```text
先 reconcile
   ↓
根据 business id / idempotency key 查询外部系统真实状态
   ↓
已经成功 → 标记 SUCCEEDED
确实没执行 → 再决定 retry
无法确认 → 人工介入
```

### 幂等键

写操作尽量传：

```text
operation_id / idempotency_key
```

让外部系统能识别重复请求。

### 面试高分点

> Tool Retry 不是“异常就重试”，而是基于幂等性和外部事实做 retry / reconcile 决策。

---

## 03-22. Prompt Injection、SSRF、文件越界、危险 Shell 为什么必须在 Tool Runtime 防？

### 面试主答

因为模型不是安全边界。

Prompt 里写：

```text
不要访问 127.0.0.1
不要读取 ~/.ssh
不要执行 rm -rf
```

只能降低概率，不能构成安全保证。

### SSRF

真正应该在 HTTP Tool 做：

```text
URL parse
DNS resolve
private IP range check
metadata endpoint deny
redirect re-check
allowlist / denylist
```

### 文件系统

应该在 Runtime 做：

```text
workspace root
path canonicalization
symlink check
allowed roots
read/write policy
```

### Shell

应该考虑：

```text
sandbox
command allowlist
working directory
network policy
resource limit
timeout
secret filtering
```

### 为什么模型不能“换一种工具绕过”

如果 HTTP Tool 拒绝内网地址，但模型还能换：

```text
curl
wget
python requests
```

那说明安全边界放错层了。

真正约束应该尽量作用于最终系统资源，而不是某一个表面 Tool。

---

## 03-23. Tool Runtime 怎么做 Observability 和 Eval？只记录聊天日志够吗？

### 面试主答

不够。

Agent Tool Runtime 至少要记录：

```text
run_id
turn_id
tool_call_id
agent_id
user/tenant/workspace
tool_name
tool_version
arguments hash / redacted arguments
start/end time
latency
status
error code
retry count
permission decision
result size
external request id
```

### Trace 链

```text
User Request
  ↓ run_id
LLM Turn
  ↓ tool_call_id
Tool Runtime
  ↓ external_request_id
MCP / API / DB
```

这样才能回答：

```text
是模型选错 Tool？
还是参数错？
还是权限拒绝？
还是 MCP Server 超时？
还是业务服务失败？
```

### Tool Eval 应拆开

不要只看“最后回答正确率”。

应该至少评估：

```text
Should-Call Accuracy
Tool Selection Accuracy
Argument Accuracy
Tool Ordering Accuracy
Forbidden Call Rate
Unnecessary Tool Call Rate
Retry Rate
Loop Rate
Execution Success Rate
Business Success Rate
Latency / Cost
```

### Wrong-tool Confusion Matrix

如果模型总把：

```text
get_device_status
```

选成：

```text
list_device_alarms
```

优先检查：

```text
命名
Description
边界示例
Tool 粒度
Retrieval
```

不一定第一反应就是换大模型。

---

# 模块六：综合系统设计题

## 03-24. 现在让你设计一个生产级 Agent Tool Runtime，你会怎么分层？

这是非常适合高级面试的综合题。

### 第一层：Capability Catalog

维护系统拥有的所有能力：

```text
Local Tools
MCP Tools
REST Tools
CLI Tools
Skills
Resources
```

Tool Registry 保存 canonical metadata，而不是把所有 Schema 每轮都发给模型。

### 第二层：Discovery / Retrieval

```text
User Goal
 ↓
Intent / Domain Router
 ↓
Permission-aware Retrieval
 ↓
Top-K Tools / Skills
 ↓
Progressive Disclosure
```

解决工具多、Skill 多导致的上下文问题。

### 第三层：Model-facing Capability View

每个 Agent、用户、Workspace 看到不同 action space：

```text
Full Registry
 ↓
Role / Tenant / Workflow State / Risk Filter
 ↓
Visible Tool View
```

### 第四层：Agent Loop

```text
Context Build
 ↓
LLM
 ↓
Tool Proposal
 ↓
Tool Result
 ↓
Context Update
 ↓
LLM
```

直到：

```text
final answer
stop condition
error budget exhausted
max iterations
```

### 第五层：Execution Gateway

所有 Tool Call 必须经过统一入口：

```text
name resolution
schema validation
business precheck
authorization
risk policy
confirmation
idempotency
rate limit
timeout
tracing
```

而不是每个 Tool 自己随便执行。

### 第六层：Adapters

```text
Local Adapter
REST Adapter
MCP Adapter
CLI Adapter
Database Adapter
```

对上统一 Tool Contract，对下适配不同协议。

### 第七层：Domain Service

最终业务事实由真实业务系统决定：

```text
Agent Runtime 不应该自己发明订单状态
MCP Server 不应该自己复制核心业务规则
LLM 更不能决定权限
```

### 第八层：Result Normalization

所有 Provider 返回：

```text
Canonical ToolResult
```

统一错误语义和 observation。

### 第九层：Reliability

```text
retry budget
idempotency
reconciliation
checkpoint
circuit breaker
fallback
no-progress detection
```

### 第十层：Security

```text
Tool visibility
Runtime authorization
resource-level permission
sandbox
SSRF
workspace boundary
secret management
approval / confirmation
```

### 第十一层：Observability / Eval

```text
trace
metrics
audit log
selection eval
argument eval
forbidden-call eval
business outcome eval
```

### 最终架构图

```text
                        User
                          │
                          ▼
                    Agent Runtime
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
        Context / Memory       Capability Catalog
        Skill / OpenViking     Tool Registry / MCP
                │                   │
                └─────────┬─────────┘
                          ▼
                  Retrieval / Policy
                          │
                          ▼
                 Model-visible View
                          │
                          ▼
                         LLM
                          │
                    Tool Proposal
                          │
                          ▼
                 Execution Gateway
       ┌──────────────────┼───────────────────┐
       │                  │                   │
       ▼                  ▼                   ▼
 Schema/Domain      AuthZ / Risk         Reliability
 Validation         Confirmation         Idempotency
       │                  │                   │
       └──────────────────┼───────────────────┘
                          ▼
                      Dispatcher
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
      Local Tool       MCP Client       REST / CLI
                          │
                          ▼
                      MCP Server
                          │
                          ▼
                    Domain Service
                          │
                          ▼
                  DB / External System
                          │
                          ▼
                   Canonical Result
                          │
                          ▼
                    Observation
                          │
                          └──────→ LLM next turn
```

### 两分钟口述版

> 我不会把 Tool Runtime 理解成“模型返回一个 function name，然后直接执行”。生产级系统应该先有统一 Capability Catalog 和 Tool Registry，再根据用户、Agent、tenant、workflow state 和当前任务做 capability projection 和 Tool Retrieval，只把少量候选 Tool Schema 暴露给模型。模型产生 Tool Call 后，必须经过统一 Execution Gateway 做名称解析、Schema 校验、业务语义校验、AuthZ、风险控制、用户确认、幂等和 tracing，再由 Local/REST/MCP/CLI Adapter 去执行真实能力。执行结果统一成 Canonical ToolResult 作为 observation 回到 Agent Loop。对于写操作还要考虑 UNKNOWN 状态、reconcile 和 idempotency，而不能异常就盲目重试。安全上 Prompt 不是边界，真正的 SSRF、文件越界、资源权限必须在 Runtime 或最终资源层强制执行。这样模型只负责选择候选动作，Runtime 负责执行治理，Domain Service 负责最终业务事实。

---

# 面试高频追问清单

完成上面 24 题后，面试官很可能继续从这些角度追问：

1. Tool name 写错后，Registry 为什么可以提示 `read_file`，但不能直接模糊执行？
2. Planner、Worker、Reviewer 三种 Agent 应该分别看到哪些 Tool？
3. `Tool Visibility` 和 `Tool Authorization` 的安全等级为什么不同？
4. 300 个 MCP Tool 时，你会先做 domain router、embedding retrieval，还是让 LLM 自己搜索？
5. Tool Retrieval 的 Top-K 设置多少？如何评估 recall 和 selection accuracy？
6. 当前 Session 已经进入 database domain，为什么还要做 active toolset cache？
7. OpenViking 的 L0/L1/L2 为什么主要是 Context Progressive Disclosure，而不是 Tool Schema Progressive Disclosure？
8. Skill 被加载后，为什么仍然需要 ToolRegistry？
9. MCP Client 和 Host 为什么不是同一个概念？
10. MCP Server 能不能直接连接数据库？可以，但为什么不建议把全部业务逻辑都放进去？
11. MCP Tool 返回成功，但 Domain Service 实际失败，最终 status 应该怎么定义？
12. 写 Tool 超时以后为什么不能直接 retry？
13. 什么样的 Tool 可以并发？什么样的 Tool 必须串行？
14. 如果一个 Tool 是 read-only，是不是就一定低风险？不一定，例如读取 secrets、跨租户数据仍然高风险。
15. 如果 Tool Schema 非常复杂，是拆 Tool 还是做 Progressive Disclosure？如何权衡？
16. MCP Apps 中 Tool Result、structured data、UI Resource 和 LLM Context 应该如何解耦？
17. Agent 支持 MCP Client，为什么不代表它自动支持 MCP Apps？
18. Skill 来源于第三方 Git 仓库，怎么防止恶意指令污染 Agent？
19. Text-to-SQL Tool 如何同时做 SQL AST 校验、RLS、只读连接和 LIMIT/cost guard？
20. 线上发现 Tool selection accuracy 下降，你如何定位是模型、Schema、description、retrieval 还是 registry version 的问题？

---

# 最后必须记住的 8 句话

```text
1. LLM 不执行 Tool，LLM 只提出 Tool Call。
2. Tool Registry 是模型 action space 与真实程序能力之间的映射层。
3. JSON Schema 正确，不代表业务正确，更不代表有权限执行。
4. Tool Visibility 是优化和防误选；Execute-time Authorization 才是安全边界。
5. 工具很多时，不应该全量注入，而应该 Retrieval + Progressive Disclosure + Schema Hydration。
6. Skill 告诉 Agent 怎么做，Tool 负责真正做，Rule 决定什么绝对不能做。
7. MCP 解决标准化互操作，不负责替你解决业务权限、事务、幂等和 Agent Loop。
8. 生产级 Agent 的核心不是“会调用 Tool”，而是“能治理 Tool 的发现、选择、执行、权限、可靠性和可观测性”。
```
