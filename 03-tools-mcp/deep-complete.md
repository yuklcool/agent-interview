# 03. Tool、Function Calling、MCP 与 Skills——全量深度版

> 覆盖 `03-01`～`03-17`。本章重点：Tool 不是 Prompt 附件，而是正式能力契约；MCP 解决互操作，Runtime 解决执行治理，业务系统解决最终事实。

---

## 03-01. Function Calling 的 JSON Schema 怎么定义？参数写错怎么办

### 核心结论

Schema 只解决“结构是否合法”，不能解决“业务是否允许”。完整执行链至少分四层：

```text
LLM Tool Proposal
      ↓
JSON / Schema Validation
      ↓
Business Semantic Validation
      ↓
Policy / Permission / Risk
      ↓
Effect Execution
```

### Schema 应表达什么

`type/properties/required/enum/range/pattern/format/additionalProperties` 是基础；description 需要写业务语义，而不只是字段翻译。

例如：

```json
{
  "type":"object",
  "properties":{
    "device_id":{"type":"string","description":"当前项目内的灯具唯一 ID"},
    "start_time":{"type":"string","format":"date-time"},
    "end_time":{"type":"string","format":"date-time"}
  },
  "required":["device_id","start_time","end_time"],
  "additionalProperties":false
}
```

即使格式正确，还要验证：`start_time < end_time`、设备属于当前 project、时间跨度没有超过系统上限。

### 参数错怎么办

错误应成为结构化 observation，而不是 Runtime 静默猜测：

```json
{
  "status":"ERROR",
  "code":"INVALID_ARGUMENT",
  "path":"start_time",
  "message":"must be earlier than end_time",
  "retryable":true
}
```

模型可有限修复；超过 `repair_budget` 后终止/澄清。

### nanobot 对照

nanobot 的 Tool Registry/Execution 会在执行前解析 Tool 和参数，异常转换成 Tool observation；workspace/SSRF 类错误则属于更硬的边界，不能靠模型换一种工具绕过。

---

## 03-02. 多 Agent 共享 Tool Registry，如何限制某些角色不能调某些工具

### 两层控制

```text
Full Tool Registry
      ↓ role/scope projection
Model-visible Tool View
      ↓
LLM chooses tool
      ↓
Execute-time Policy
      ↓
Domain Authorization
```

第一层减少模型误选；第二层才是安全边界。

### Tool metadata

```json
{
  "name":"refund_order",
  "risk":"high",
  "required_scopes":["refund:write"],
  "allowed_roles":["worker_refund"],
  "requires_confirmation":true,
  "side_effect":true,
  "idempotent":true
}
```

Planner 可以看到 `query_order`，但不一定看到 `refund_order`；Reviewer 只能有 read/validate 工具。

### 为什么 Prompt 不够

Prompt 写“Reviewer 不要退款”只能降低概率。如果 Tool 仍可执行，Prompt Injection 或模型错误仍能越权。

### AgentDock 落地

AgentDock 适合在 Control Plane/Driver 配置层维护 agent→MCP/Skill/Tool assignment，再在 Runtime Tool Adapter 和 Java Service 再校验 user/workspace/tenant。容器隔离解决进程和文件系统边界，但不能替代业务 RBAC。

---

## 03-03. MCP 和现在用的 Tool Callback 是什么关系？接 MCP 后老工具怎么迁移

Callback 是进程内接口；MCP 是跨进程/跨语言的标准能力协议。

### 迁移方式

```text
Existing Java Service
       ↓
Tool Adapter / MCP Server
       ↓
name + description + input schema + result
       ↓
MCP Client
       ↓
Agent Tool Registry
```

业务 Service 不重写。迁移期 local Tool 与 MCP Tool 可并存，但要避免两个同义工具同时暴露给模型，例如 `query_device` 和 `mcp_query_device` 都指向同一业务。

### MCP 不负责什么

- 业务事务；
- tenant 权限；
- refund idempotency；
- Saga；
- Agent Loop；
- 模型选择。

如果回答“用了 MCP 就解决了所有 Tool 工程问题”，通常是不对的。

---

## 03-04. 模型参数格式对了，但业务语义错了，Tool 层怎么拦？

典型错误：

```text
refund_amount = 99999  JSON 合法
但订单可退金额 = 100
```

或：

```text
device_id 格式合法
但不属于当前 tenant/project
```

### 三层 validator

1. Structural Validator：JSON/schema。
2. Domain Validator：对象状态、时间窗口、金额、依赖关系。
3. Authorization/Policy：当前用户/Agent 是否允许执行。

Tool Adapter 不应该自己复制业务规则；最终语义最好调用真实 Domain Service 校验。

### 错误分类

`INVALID_ARGUMENT` 可让模型修参数；`BUSINESS_RULE_VIOLATION` 通常需要改变计划；`FORBIDDEN` 不应该让模型换写法继续碰撞；`UNKNOWN` 要对账。

---

## 03-05. 参数幻觉、JSON 语法错、枚举错，怎么做自动修复？

### 修复分层

```text
Parse Error
  ↓ deterministic parser repair? only safe syntax fixes
Schema Error
  ↓ structured validation error to model
Semantic Error
  ↓ domain error + allowed alternatives
Repeated Error
  ↓ stop / clarify / stronger model
```

不要做危险的“自动猜参数”。例如模型写错 tool name，可以提示 canonical names，但不能模糊匹配后直接执行高风险工具。

### Repair budget

建议记录：

```text
argument_repair_count
tool_selection_repair_count
same_error_fingerprint_count
```

相同错误重复 2～3 次说明 no-progress，应升级模型或向用户澄清，不要无限反思。

### Grammar/constrained decoding 的边界

Grammar-based decoding 能显著提高 JSON 语法正确率，但不能保证业务正确。`{"refund_amount":99999}` 可以语法/schema 都正确，仍必须被业务层拒绝。

---

## 03-06. 有 100+ 个工具时，怎么让模型快速选对 Tool？

把 100 个完整 Schema 全塞给模型会导致：token 成本上升、相似工具混淆、Tool selection accuracy 下降。

### Tool Retrieval

先把 Tool 当文档做候选检索：

```text
User Goal
  ↓
Domain/Capability Router
  ↓
Tool Metadata Retrieval
  ↓ Top 5~15
Policy Filter
  ↓
Full Schema Injection
  ↓
LLM Tool Selection
```

Metadata 可包括 domain、verbs、entities、risk、examples、required scopes。

### 两阶段选择

第一阶段只给 `name + short description`；选出候选后，再展开完整 input schema。这和 Context Progressive Disclosure 本质一致。

### Tool 设计本身也很重要

如果 20 个工具 description 高度重叠，检索器再强也难。应该合并碎片化 API、规范命名、明确能力边界。

---

## 03-07. Tool Schema 太多导致上下文爆炸，Progressive Disclosure 怎么做？

### 三层信息

```text
L0: tool name + one-line capability
L1: detailed description + examples + risk
L2: full JSON Schema + edge cases
```

默认只注入 L0；候选后加载 L1/L2。

这个思路和 OpenViking 的 L0/L1/L2 Context 层次非常相似：先用 abstract 判断相关性，再按需加载 overview/details。

### 注意

Schema 本身是执行契约，最终真正调用前 Runtime 必须有完整 canonical schema；“不把完整 Schema 给模型”不等于执行层不知道 Schema。

### 缓存

同一 session/domain 的 candidate tool set 可以短期缓存，但要带 `tool_registry_version`，工具版本变更后失效。

---

## 03-08. Tool 返回 HTTP 200 但语义不完整，Runtime 怎么判断？

HTTP 200 只表示 transport 成功，不表示业务成功。

### Tool Result Envelope

```json
{
  "status":"PARTIAL",
  "code":"PROVIDER_PARTIAL_DATA",
  "data":{...},
  "missing":["price","inventory"],
  "freshness":"2026-09-08T...",
  "retryable":true
}
```

建议至少有：`status/code/data/missing/freshness/source/retryable/request_id`。

### Result Validator

Tool Adapter 可做：
- 必填字段；
- 数量/范围；
- freshness；
- response provenance；
- 业务 invariant。

例如航班接口 200 但结果里没有 inventory 状态，不能直接被模型解释成“有票”。

### 关键思想

**Transport success、Tool execution success、Business success 是三件事。**

---

## 03-09. 不同 MCP Server 返回格式不一致，应该让模型适配还是系统适配？

应该由系统适配成统一 Tool Result Contract，不应把 provider-specific 差异推给模型。

```text
MCP Server A → Adapter A ┐
MCP Server B → Adapter B ├→ Canonical ToolResult → Agent
REST Service C→Adapter C ┘
```

### 为什么

如果模型要记住几十个 MCP Server 的错误格式：
- Prompt 复杂；
- provider 变化影响模型；
- Eval 很难统一；
- 错误分类不一致；
- 业务逻辑进入 Prompt。

### Canonical Error Taxonomy

`INVALID_ARGUMENT / NO_RESULT / RETRYABLE_ERROR / HARD_ERROR / FORBIDDEN / UNKNOWN / PARTIAL`。

模型看到的是稳定语义，Adapter 负责协议兼容。

---

## 03-10. MCP Server 怎么构建？它真正负责什么？

一个合理 MCP Server 主要负责：

```text
Capability registration
Schema/description
Protocol handling
Input decoding
Business service invocation
Result normalization
Server-side auth boundary（若部署需要）
```

### 不要把业务都塞 MCP Server

建议：

```text
MCP Server
   ↓ adapter
Java Domain Service
   ↓
Repository / external API
```

交易规则、事务、权限、幂等仍放 Domain Service。这样同一业务既能被 MCP 调，也能被 REST、批处理、后台任务使用。

### Tool 设计

工具应该是面向 Agent 的业务动作，不一定等于数据库 CRUD。例如 `analyze_device_energy` 比同时暴露 10 个底层表 CRUD 更容易安全使用。

---

## 03-11. MCP 的完整调用链是什么？Host、Client、Server 各自做什么？

### 调用链

```text
User
 ↓
Agent Host / Runtime
 ↓ discovers tools
MCP Client
 ↓ protocol
MCP Server
 ↓ adapter
Business Service
 ↓
DB / External API
```

Host 负责 Agent 生命周期、模型、Context、权限和 UI；MCP Client 是 Host 中负责协议连接的一部分；Server 暴露工具/资源能力。

### 返回后不是结束

Tool Result 还要回到 Host/Runtime，成为 model observation，模型再决定是否继续。

### 与 AgentDock

AgentDock 可以负责把某 MCP 配置分配给某 agent 实例；实际 MCP Client 可能在 nanobot/driver 内。Control Plane 管“谁拥有哪个 MCP”，Runtime 管“这一轮何时调用”。

---

## 03-12. CLI Tool、MCP Tool、直接 REST API 怎么选？

### CLI

适合已有成熟 CLI、代码/运维工具、本地开发场景；缺点是输出经常非结构化、权限继承进程、跨平台差。

### REST

适合稳定业务服务、服务间调用、已有 API 治理体系；实现简单、观测成熟。

### MCP

适合需要标准化供多种 Agent/Host 发现和调用的工具生态，减少每个 Agent 框架各写 Adapter。

### 选择原则

不为了“Agent 化”强行 MCP 化。内部单服务若已有稳定 REST Tool Adapter，MCP 的收益可能不大；需要同时服务 nanobot、Pi、IDE Agent、桌面 Agent 时，MCP 的互操作价值更高。

---

## 03-13. 多工具调用的优先级怎么定？依赖、风险和时效怎么一起考虑？

不要用一个简单 priority 数字解决全部问题。

### 先看 dependency

有前置依赖的必须等待：

```text
search_order → validate_refundable → refund
```

### 再看风险

写操作/高风险 Tool 即使“优先级高”，也不能绕过 confirmation/precondition。

### 再看 deadline / freshness

天气、库存、价格具有时效性，应靠近真正使用时再查；静态用户偏好可提前获取。

### Scheduler 元数据

```text
depends_on
risk
required/optional
timeout
deadline
freshness_ttl
side_effect
concurrency_safe
```

最终是 Execution Graph，不是简单排序数组。

---

## 03-14. Skill、MCP/Tool、Rule 三者是什么关系？

### Rule

确定性的约束/策略，例如“退款 > 1000 必须人工确认”“禁止访问内网”。Rule 不应该依赖模型是否记住。

### Tool/MCP

可执行能力，改变或查询外部世界。

### Skill

一套可复用的任务方法/操作知识，通常告诉 Agent “遇到某类任务如何组合工具和上下文”。Skill 可以引用 Tool，但不是 Tool 本身。

```text
Rule: 不能做什么 / 必须满足什么
Skill: 这类任务建议怎么做
Tool: 真正执行什么动作
```

### OpenViking

OpenViking把 Skill 也作为 Context 类型统一存入 `viking://`，说明 Skill 可以被检索/加载；但被加载的 Skill 仍然是指导信息，实际执行仍经过 Tool Runtime。

---

## 03-15. Skill Registry / Discovery / Invocation 应该怎么设计？

### Registry metadata

```text
skill_id/version
name/description
domain
triggers/capabilities
required_tools
required_scopes
context_dependencies
examples
source/repository
```

### Discovery

不要所有 Skill 全注入。和 Tool Retrieval 一样：先按任务语义、domain、权限检索候选，再加载 Skill 正文。

### Invocation

Skill 不是直接“执行”，而是影响本轮 Context/Plan；真正动作仍走 Tool。

### AgentDock

AgentDock 已支持 skills 从 Git repo/inline 分配给 agent。企业版可进一步做：workspace scope、skill version pin、审批、签名、依赖 Tool 检查、灰度。

### 安全问题

Skill 本质是外部指令源，也可能被污染。第三方 Skill 应有来源、版本、review、sandbox 与 tool permission 限制，不能因为名字叫 Skill 就信任。

---

## 03-16. 开源模型 Function Calling 较弱，怎么提升？

不要一上来就 SFT。

### 优化顺序

1. Tool 数量裁剪；
2. Schema 简化、描述去歧义；
3. few-shot Tool examples；
4. constrained/grammar decoding；
5. 参数修复 loop；
6. semantic router；
7. 仍然不够，再做 Tool-use SFT/LoRA。

### 为什么

很多“模型工具能力差”实际上是工具设计差：20 个重叠工具、Schema 1000 token、字段命名晦涩，换更大模型也不一定稳定。

### 评测

拆为：Should-Call、Tool Selection Accuracy、Argument Accuracy、Ordering、Forbidden Call Rate，而不是只看“最终答对”。

---

## 03-17. Skill 和长期记忆有什么区别？为什么不能互相替代？

### Skill

描述“如何做某类任务”，通常相对稳定、可版本化、可多人共享。

### Memory

描述“这个用户/Agent 过去发生过什么、偏好什么、学到了什么”，具有主体、时间、来源和更新语义。

```text
Skill: 如何处理 PostgreSQL 慢 SQL
Memory: 用户当前项目使用 PostgreSQL 17，偏好先看 EXPLAIN ANALYZE
```

### 为什么不能替代

把用户偏好写进 Skill 会污染所有用户；把操作流程写成每个用户的 Memory 会造成重复、难版本升级。

### OpenViking 对照

OpenViking明确区分 `resources / memories / skills` 三种 Context 类型，只是统一用 `viking://` 管理。这正好说明“统一存储”不等于“语义相同”。

---

# 本章统一执行模型

```text
Candidate Capability Discovery
        ↓
Tool/Skill Projection
        ↓
LLM Proposal
        ↓
Canonical Schema
        ↓
Business Validation
        ↓
Policy / Permission / Risk
        ↓
MCP / REST / CLI Adapter
        ↓
Domain Service
        ↓
Canonical ToolResult
        ↓
Observation / Trace / Eval
```

面试时要反复强调：**模型负责选择和生成候选动作；Runtime 决定动作能不能执行；业务 Service 决定动作在业务上是否合法。**
