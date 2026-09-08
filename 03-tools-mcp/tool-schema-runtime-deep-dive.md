# Tool Schema 与 Tool Runtime 深挖：为什么 JSON Schema 正确仍然可能执行错

> 目标：把“Function Calling 就是定义 name/description/parameters”这种浅回答升级成完整的 Tool Contract：模型理解、Schema 约束、业务语义校验、权限、幂等、风险级别、重试策略、Observation 规范。

## 面试题

> 如何为 Agent 设计标准化 Tool Schema？参数格式正确但业务语义错误怎么办？Tool Description 怎么写才更容易让模型选对工具？

---

# 一、Tool Schema 不是给人看的接口文档

它同时服务三类消费者：

```text
LLM
Runtime
Human Developer
```

所以它既是：

```text
模型的 action space
```

也是：

```text
Runtime 的输入契约
```

如果 Tool Schema 设计差，常见后果包括：

- 模型选错 Tool；
- 参数名猜错；
- 同一含义存在多个 Tool；
- 模型传入自由文本，Runtime 无法稳定校验；
- JSON 格式合法，但业务已经越权；
- Tool error 太模糊，模型不断重复同样错误。

---

# 二、一个 Tool Contract 至少有五层

```text
1. Discovery Contract
2. Input Schema
3. Business Validation
4. Execution Policy
5. Result / Error Contract
```

很多项目只做第 2 层，所以工程上很脆弱。

---

# 三、第一层：Discovery Contract——让模型知道“什么时候该用它”

Tool 名字应该是：

```text
动词 + 业务对象
```

例如：

```text
get_device_status
list_active_alarms
create_work_order
query_energy_summary
```

不要：

```text
do_task
service_call
run_api
query_data
```

因为模型无法从名字区分 action space。

## Description 不要只写“查询设备”

更好的：

> 查询一个或多个照明设备在指定时间点/时间范围内的运行状态。用于回答在线、离线、开关灯、功率、调光状态问题。不要用于查询历史报警，报警请使用 `list_device_alarms`。

这里故意包含：

```text
能做什么
不能做什么
适用问题
相邻 Tool 的边界
```

这能显著减少工具误选。

---

# 四、第二层：Input Schema——减少自由度

例如：

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
    "start_time": {
      "type": "string",
      "format": "date-time"
    },
    "end_time": {
      "type": "string",
      "format": "date-time"
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

几个设计原则：

- 能 enum 就不要 free text；
- 能数组就不要让模型拼逗号字符串；
- 限制 maxItems，防止一次塞 10 万设备；
- `additionalProperties=false`，减少幻觉字段；
- 时间格式统一；
- 语义不同的字段不要复用一个 `query` 字符串。

---

# 五、为什么 Schema 合法还远远不够

例如：

```json
{
  "refund_amount": 999999
}
```

完全可能符合：

```json
{"type":"number"}
```

但业务上可能：

```text
订单总金额只有 100 元
```

所以要分：

```text
Grammar Validation
        ↓
Schema Validation
        ↓
Business Validation
        ↓
Authorization
        ↓
Execution
```

这几层不能合并。

---

# 六、Structured Output / Grammar-based Decoding 解决什么

Grammar/Constrained Decoding 能保证：

```text
生成出来是合法 JSON
```

JSON Schema 能进一步保证：

```text
字段类型/必填/枚举/结构合法
```

但它们都不能保证：

```text
业务正确
权限正确
外部状态允许
```

所以：

```text
语法正确 ≠ 语义正确 ≠ 业务允许执行
```

这是面试里非常重要的分层。

---

# 七、第三层：Business Validation 应该校验什么

例如 `create_work_order`：

```text
设备是否存在
设备是否属于当前项目
用户是否有创建工单权限
同一个事件是否已有未关闭工单
故障状态是否仍然存在
设备数量是否超过一次操作上限
```

这些都不能依赖模型。

推荐 Runtime 返回结构化错误：

```json
{
  "status": "INVALID_ARGUMENT",
  "code": "DEVICE_OUT_OF_SCOPE",
  "message": "3 devices are outside current project scope",
  "retryable": false,
  "invalid_fields": ["device_ids"]
}
```

而不是：

```text
Error.
```

结构化错误能帮助模型修正。

---

# 八、第四层：Execution Policy——Tool 不是都一样

Tool Metadata 可以增加：

```text
read_only
side_effect
idempotent
concurrency_safe
risk_level
required_scopes
requires_confirmation
retry_policy
rate_limit_group
```

例如：

```yaml
name: query_device_status
read_only: true
idempotent: true
concurrency_safe: true
risk_level: low
```

而：

```yaml
name: switch_off_devices
read_only: false
side_effect: true
idempotent: false
risk_level: high
requires_confirmation: true
```

这样 Runtime 才能根据 Tool 性质决定：

- 是否允许并发；
- 是否允许自动 retry；
- 是否需要用户确认；
- 是否需要审批；
- 是否允许某 Agent role 看见它。

---

# 九、Tool Visibility 和 Tool Authorization 必须分两层

## 第一层：不给模型看

根据：

```text
agent_role
user_permission
tenant
current workflow state
risk policy
```

过滤 Tool Schema。

例如 Reviewer 根本不看到：

```text
refund
pay
delete_user
```

## 第二层：执行时还要再校验

即使模型幻觉出：

```text
refund_order
```

Runtime 仍然必须：

```text
ToolRegistry lookup
AuthZ
Risk Policy
Schema Validation
Business Validation
```

所以：

```text
Prompt / Visibility = UX 层约束
Runtime Authorization = 安全边界
```

---

# 十、Tool Error 应该怎么设计

推荐状态至少区分：

```text
OK
NO_RESULT
INVALID_ARGUMENT
PERMISSION_DENIED
RETRYABLE_ERROR
HARD_ERROR
UNKNOWN
```

为什么 `NO_RESULT` 不能等于 ERROR？

机票搜索没结果，可能只是：

```text
当前条件没有航班
```

模型可以：

```text
换机场
扩大时间窗口
询问用户
```

如果 Runtime 直接抛 Exception，模型会误以为系统故障。

---

# 十一、Tool Error 如何引导模型修正，而不是循环

好的 Tool Result：

```json
{
  "status": "INVALID_ARGUMENT",
  "code": "DATE_RANGE_TOO_LARGE",
  "message": "maximum range is 31 days",
  "retryable": true,
  "suggested_fix": "split query into ranges <= 31 days"
}
```

比：

```text
Bad request
```

更适合 Agent。

但也要防模型无限重试，因此 Runtime 还要记录：

```text
same_tool
same_target
same_error
retry_count
```

超过阈值就终止或换策略。

---

# 十二、结合 nanobot 当前怎么讲

nanobot 的 Tool 执行层位于：

```text
nanobot/agent/tools/registry.py
nanobot/agent/tools/execution.py
```

`execution.py` 中可以看到几个很实际的 Runtime 设计：

```text
prepare_call
before_execute_tool / after_execute_tool
on_execute_tool_error
repeated_external_lookup_error
workspace violation
SSRF guard
concurrency_safe batch
```

这说明 nanobot 已经把 Tool Execution 当成独立安全边界，而不是直接：

```python
await tool.execute()
```

尤其 `_partition_tool_batches()` 会根据：

```text
tool.concurrency_safe
```

决定哪些 Tool 可以放入并发 batch。

所以 Tool Metadata 不只是文档，它会真正影响 Runtime 调度。

---

# 十三、为什么 SSRF 是 Tool Runtime 问题，不是 Prompt 问题

模型可能尝试：

```text
http://127.0.0.1
169.254.169.254
内网地址
```

你不能只在 System Prompt 写：

> 不要访问内网。

因为模型不是安全边界。

真正应该：

```text
URL parse
DNS/IP resolve
Private range check
Redirect re-check
Whitelist
```

放在 Tool/HTTP Runtime。

nanobot 当前对 SSRF 会返回明确的 non-bypassable boundary note，并阻止模型换 curl/wget/编码 IP 等方式绕过。

这就是 Harness 的意义。

---

# 十四、一个企业级 Tool Registry 可以长什么样

```json
{
  "name": "create_work_order",
  "description": "Create a maintenance work order for confirmed lighting faults.",
  "schema": {},
  "metadata": {
    "read_only": false,
    "side_effect": true,
    "idempotent": true,
    "concurrency_safe": false,
    "risk_level": "medium",
    "required_scopes": ["workorder:create"],
    "requires_confirmation": false,
    "retry_policy": "reconcile_then_retry"
  }
}
```

然后：

```text
Registry = Capability Catalog
Policy Engine = Who can use it
Dispatcher = How to execute it
Business Service = What actually happens
```

不要把所有责任塞到 Tool 类里。

---

# 十五、场景：Text-to-SQL Tool

模型生成：

```json
{
  "sql": "select * from device"
}
```

Schema 完全合法。

但 Runtime 还要：

```text
SQL Parse AST
 ↓
只允许 SELECT
 ↓
表白名单 / Schema scope
 ↓
tenant/project predicate
 ↓
禁止危险函数
 ↓
LIMIT
 ↓
EXPLAIN / cost guard
 ↓
只读连接执行
```

所以 SQL Tool 的安全性几乎和 JSON Schema 无关。

Schema 只保证：

```text
参数长得像 SQL
```

真正安全靠执行前的 deterministic validation。

---

# 十六、Tool Schema 怎么评测

可以做 Tool Selection Eval：

给一批真实 Query：

```text
用户问题
expected tool
expected arguments constraints
```

测：

```text
Tool Selection Accuracy
Argument Validity
Business Validation Pass Rate
Unnecessary Tool Call Rate
Tool Retry Rate
Wrong-tool Confusion Matrix
```

如果：

```text
get_device_status
```

经常被误选成：

```text
list_device_alarms
```

优先改：

```text
名字/description/边界示例
```

不一定要换模型。

---

# 十七、常见错误

## 错误 1：Tool Description 越长越好

不一定。太长会占 Context，且边界不清更糟。

## 错误 2：Schema 有类型校验就安全

远远不够。

## 错误 3：Tool 不给 Reviewer 展示就万事大吉

执行层仍然必须授权。

## 错误 4：所有错误都返回 Exception 文本

模型无法稳定修正。

## 错误 5：Tool 名字设计随意

工具路由准确率会显著下降。

---

# 十八、2 分钟面试口述版

> 我会把 Tool 定义看成五层 Contract，而不只是 JSON Schema。第一层是 discovery，名字和 description 要明确告诉模型什么时候用、什么时候不要用；第二层是 Schema，把参数自由度压缩到 enum、format、required、additionalProperties 这些可验证结构；第三层是业务校验，比如设备是否属于当前项目、退款金额是否超过订单金额；第四层是执行策略，包括 read-only、side-effect、idempotent、concurrency_safe、risk level、required scopes；第五层是结构化 Tool Result 和 Error，让模型知道是 NO_RESULT、INVALID_ARGUMENT、RETRYABLE_ERROR 还是 UNKNOWN。结合 nanobot，它的 `tools/execution.py` 已经有 prepare_call、hook、SSRF/workspace boundary、repeated lookup guard 和 concurrency_safe batch，所以真正安全边界是在 Tool Runtime，不是 Prompt。JSON 合法只说明语法没问题，绝不代表业务允许执行。
