# 03. Tool、Function Calling、MCP 与 Skills

> 本章共 17 个专题。每题按“原理 → 工程 → nanobot/Java → 失败边界 → 面试表达”组织。

## 03-01. Function Calling 的 JSON Schema 怎么定义？参数写错怎么办

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Tool Schema 是接口契约；模型参数错必须由 Runtime 拒绝并返回可修复 observation。

### 3. 深入原理：从概念讲到机制

Schema 应明确 type、properties、required、enum、format、range、additionalProperties。description 要写业务语义，不只是字段翻译。模型生成参数后，服务端必须再次校验；校验失败要返回结构化 Tool Error，例如缺失字段、非法枚举、格式错误，然后 Agent Loop 再决定是否修正重试。重试要有上限，高风险动作还要权限/确认/幂等。

* Schema 不只是类型约束，还应该表达业务语义：字段描述、required、enum、pattern、range、互斥/依赖关系。模型生成参数后必须服务端验证。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 验证分三层：JSON Schema 校验→业务语义校验（日期范围/状态/对象存在性）→Policy/权限校验。错误返回结构化 code/path/message/retryable，供 Agent 有限修正。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot 的 Tool Registry / execution 层会在真正执行前做工具解析和参数准备；工具异常会被转换成 observation 回注模型。对于 workspace/SSRF 等安全边界，execution 层会明确拒绝并避免模型通过换工具绕过。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 7. 场景推演

```
LLM 生成 Tool Call
  ↓
Schema/Registry 校验
  ├─ 不合法 → Tool Error → 回注 LLM → 有限重试
  └─ 合法
       ↓
Policy / 权限 / Risk 校验
       ├─ 拒绝
       └─ 允许 → execute()
```

### 8. 面试官可能继续追问

工具名写错怎么办？——精确匹配，不能模糊执行；可返回 did-you-mean 提示。 Schema 合法但业务不允许？——照样拒绝，Schema 不是权限系统。

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“我把 JSON Schema 当接口契约，不是提示词附件。模型写错参数，Runtime 校验失败后把结构化错误作为 observation 回注；但高风险 Tool 即使参数合法，也必须再过权限、幂等和确认。”
源码/工程落点： nanobot/agent/tools/registry.py；nanobot/agent/tools/execution.py
来源：原深度版答案，已在本次总表中重新归类。

---

## 03-02. 多 Agent 共享 Tool Registry，如何限制某些角色不能调某些工具

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Tool 可见性和真正执行权限必须双层控制；Prompt 不是安全边界。

### 3. 深入原理：从概念讲到机制

第一层 Context/Prompt 构造时按 role/scope 过滤 Tool Schema，让 Reviewer 根本看不到 refund/delete；第二层执行时 Dispatcher/Policy 再按 agent\_role、user、tenant、risk、confirmation 做强校验。高风险工具再叠加幂等和审计。

* Tool Registry 是能力目录，不等于权限系统。第一层按角色裁剪模型可见 Tool Schema，第二层执行时再次按 user/tenant/agent\_role/scope/risk 校验。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 高风险 Tool metadata 可含 risk\_level、required\_scopes、requires\_confirmation、idempotent、side\_effect。可见性降低误选概率，execute-time policy 才是真安全边界。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

nanobot 有 ToolRegistry 和 session/tool policy 基础能力，但 Planner/Worker/Reviewer 细粒度 RBAC 建议由平台层构造不同 registry view，再在 Tool Adapter/Java Service 二次校验。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 7. 场景推演

```
Tool Registry 全量
  ↓ role/scope filter
Worker 看到：query, create_work_order
Reviewer 看到：query, validate
  ↓
execute-time policy 再校验
  ↓
真正调用业务系统
```

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“模型看不到某个 Tool 只是降低误调用概率，真正安全来自 execute-time policy。可见性和执行权限是两层，缺一不可。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 03-03. MCP 和现在用的 Tool Callback 是什么关系？接 MCP 后老工具怎么迁移

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Callback 是进程内编程抽象，MCP 是跨进程/跨语言的标准工具协议。

### 3. 深入原理：从概念讲到机制

原来的 Tool/Service 逻辑不需要推翻，可以外面加 MCP Server 映射 name/description/schema/result；Agent 侧 MCP Client 再适配回统一 Tool Registry。迁移可逐工具进行，本地 Callback 和 MCP Tool 并存。

* Callback 是进程内调用接口，MCP 是跨进程/跨语言的标准化能力暴露。迁移不应改业务 Service，而是增加 Adapter/MCP Server，把已有函数映射成标准 schema/result。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 迁移期允许 local Tool 和 MCP Tool 并存，但 Registry 中要保证 canonical tool name 和能力不重复，避免模型面对两个等价工具。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

你的 Java 微服务可以继续保留原业务 Service，外层暴露 MCP/REST；nanobot 侧接 MCP 后无需复制业务逻辑。MCP 解决协议标准化，不自动解决权限、事务和幂等，这些仍在业务层。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

“MCP 不是重写老工具，而是给现有能力套一个标准协议外壳，让跨进程、跨语言调用变得统一。”
来源：原深度版答案，已在本次总表中重新归类。

---

## 03-04. 模型参数格式对了，但业务语义错了，Tool 层怎么拦？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Schema 只保证“长得像”，业务校验保证“值真的能用”。Tool 执行前至少做语法/类型、业务语义、权限/风险三层校验。

### 3. 深入原理：从概念讲到机制

例如 date 符合 YYYY-MM-DD 但早于当前日期；device\_id 格式合法但不属于当前项目；refund\_amount 是数字但超过可退金额。此类错误必须由确定性 Service 校验并返回结构化 error\_code / repair\_hint，不能让模型猜。

* 格式正确不代表可执行。例如 refund(amount=1000) 类型合法，但可能超过订单可退金额。Tool Adapter 必须使用业务 Service 做对象状态、金额、时间窗口、权限和幂等校验。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 返回错误应区分 INVALID\_ARGUMENT 与 BUSINESS\_RULE\_VIOLATION。前者可让模型修参数，后者通常需要改变计划或向用户解释，不能盲目 retry。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-05. 参数幻觉、JSON 语法错、枚举错，怎么做自动修复？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

先 deterministic repair，后 LLM repair，最后有限重试；任何修复都不能绕过原 Schema 和业务校验。

### 3. 深入原理：从概念讲到机制

可自动做的包括类型转换、日期标准化、默认值补全；涉及语义的缺失字段可把 validation errors 回注模型重新生成。每次重试要记录同一 error signature，若连续相同错误则停止，避免“修复循环”。

* 自动修复只适合低风险、可验证错误。流程应是 parse→schema validate→structured error→模型修复→再次 validate，并限制重试次数。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 不要用“正则修 JSON”把语义错误吞掉。对日期、ID、金额等关键字段优先由确定性 parser/lookup 归一化。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-06. 有 100+ 个工具时，怎么让模型快速选对 Tool？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

不要把 100 个 Schema 全塞给模型；用分层路由 + Tool Retrieval + 轻量 rerank + 动态注入，只暴露当前最相关的小集合。

### 3. 深入原理：从概念讲到机制

流程可做：domain router → metadata/filter → embedding/BM25 检索工具描述 → TopK rerank → 把 5~10 个候选 schema 注入本轮。再结合用户/Agent role 做权限过滤。这样同时降低 token 和误选工具概率。

* 工具很多时不要把 100+ schema 全塞上下文。先做 capability routing：按 domain/intent/embedding/关键词检索候选工具，再把 TopN schema 暴露给模型。
* 工具命名和边界比模型更重要：能力重叠、description 相似会显著降低选择准确率。需要 canonical taxonomy、示例和 negative description（何时不要用）。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 离线评测不仅看 top1 tool accuracy，还看候选召回率：如果真正工具没进候选集，再强的主模型也选不到。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-07. Tool Schema 太多导致上下文爆炸，Progressive Disclosure 怎么做？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

先给能力目录/摘要，需要时再加载详细 Schema；不要把所有工具的完整 description、examples、error contract 常驻上下文。

### 3. 深入原理：从概念讲到机制

三层披露比较实用：一级 domain/skill 名称，二级 tool name+一句描述，三级真正候选的完整 JSON Schema。对模型来说，检索 Tool 和检索知识库本质相似，都是“从能力库里选择本轮必要上下文”。

* Progressive Disclosure 可以分三级：先给 Tool category/name/短描述；模型选域后再加载完整 schema；真正调用前才加载详细使用说明/示例。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 需要缓存和版本控制，避免每轮重复拉取 schema；并记录本轮暴露过哪些工具，保证 trace 可复现。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-08. Tool 返回 HTTP 200 但语义不完整，Runtime 怎么判断？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Transport success 不等于业务 success。Tool Adapter 要把外部响应归一成明确的业务状态：OK / PARTIAL / EMPTY / RETRYABLE\_ERROR / HARD\_ERROR。

### 3. 深入原理：从概念讲到机制

例如第三方 API 200 但 `data=null`、缺关键字段或返回“处理中”，不能直接当成功。Adapter 可做 required-field validation、业务 code 映射、数据完整度评分，再把统一状态回给 Agent。

* HTTP status 只代表传输/接口层成功，不代表业务结果可用。Tool Result 需要自己的 result envelope：status、data、completeness、source\_time、warnings、error\_code。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 例如航班 API 200 但只返回一个机场的数据，应标 partial=true，而不是让模型把 partial 当全量。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-09. 不同 MCP Server 返回格式不一致，应该让模型适配还是系统适配？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

让 Adapter/Server 适配，模型只看稳定的统一契约。格式归一化是工程职责，不是语言模型职责。

### 3. 深入原理：从概念讲到机制

可定义统一 ToolResultEnvelope：status、data、error\_code、message、retryable、artifact\_ref、metadata。外部 REST/MCP/DB 各自转换进这个 envelope。这样 Agent 的 retry、trace、recovery 才能写一次。

* 不要让主模型适配不同 MCP Server 的任意格式。平台应该做 Normalization Layer，把外部结果统一成内部 ToolResult/Artifact contract。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* Adapter 负责字段映射、错误归一化、时间/单位规范、脱敏；模型只消费稳定 contract，这样换 Server 不会污染 Prompt。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-10. MCP Server 怎么构建？它真正负责什么？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

MCP Server 的职责是把外部能力标准化暴露为可发现、可调用的 Tools/Resources/Prompts，并处理连接、鉴权、输入校验和结果封装；不是把任意 API 简单套个壳。

### 3. 深入原理：从概念讲到机制

实现上先定义工具名称/描述/Input Schema，然后绑定业务实现，提供能力发现与调用端点，并考虑 transport、auth、timeout、rate limit、observability。业务事务和权限仍应落在真实 Service，不因为用了 MCP 就消失。

* MCP Server 的核心职责是声明和执行能力：工具/资源的 schema、生命周期、连接、结果。它不应该承载 Agent 的全局计划，也不自动等于权限中心。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* Server 侧仍需 authn/authz、rate limit、业务校验、audit；Host/Client 侧负责选择/调用和上下文集成。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-11. MCP 的完整调用链是什么？Host、Client、Server 各自做什么？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Host 承载 Agent 和用户会话，MCP Client 负责协议连接，Server 暴露能力；典型流程是连接/初始化 → 能力发现 → 模型选择 Tool → Client 发 call → Server 执行 → Result 回到 Host → 作为 observation 进入下一轮。

### 3. 深入原理：从概念讲到机制

这里要分清模型和 MCP：模型并不直接发网络请求。模型输出 Tool Call 意图，宿主 Runtime 把它映射为 MCP 调用。MCP 解决工具连接标准化，Function Calling 解决模型如何表达调用意图。

* Host 是运行 Agent/用户体验的宿主，Client 是 Host 内与某个 MCP Server 通信的协议端点，Server 暴露 tools/resources/prompts 等能力。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 一次调用链要能传播 request/trace/user context，但不要把整个会话私密内容默认透传给 Server；只发送执行所需最小上下文。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-12. CLI Tool、MCP Tool、直接 REST API 怎么选？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

看复用范围、协议稳定性、运行环境和隔离需求：本地已有成熟 CLI 可直接封装，跨语言多客户端优先 MCP，单一服务内部调用可保持 REST/Java 方法。

### 3. 深入原理：从概念讲到机制

不要为了“统一”把所有东西强制改成 MCP。MCP 的价值是跨应用标准化；CLI 的优势是原子、易调试、适合 Coding Agent；REST 的优势是服务治理成熟。最终可以统一成 Runtime 内部 Tool abstraction。

* CLI 适合已有命令行生态、需要沙箱执行；MCP 适合标准化长期能力；REST 适合传统服务间 API。选择依据是生命周期、跨语言、schema 可发现性、安全隔离和现有系统成本。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run\_id / step\_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-13. 多工具调用的优先级怎么定？依赖、风险和时效怎么一起考虑？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

先满足硬依赖，再考虑时效性/资源锁，最后安排不可逆动作；高风险 Tool 必须受状态前置条件和确认门控约束。

### 3. 深入原理：从概念讲到机制

可以先建立依赖 DAG，再为可并行节点根据 deadline、库存变化风险、成本排序。查询类通常可并行；支付、删除、发送等不可逆动作放到证据和用户确认齐全后。模型可以提出排序，Orchestrator 应校验。

* 优先级同时考虑 dependency、risk、freshness、cost。先执行低成本且能缩小搜索空间的只读 Tool；有依赖则拓扑执行；高风险 Tool 必须等前置验证和确认。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把 Tool metadata 中的 side\_effect/risk/cost/concurrency\_safe 纳入 planner/runtime，不要让 LLM 单凭描述决定所有顺序。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-14. Skill、MCP/Tool、Rule 三者是什么关系？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Rule 画红线，Skill 提供做事方法，Tool/MCP 提供可执行能力；三者分别对应约束、方法、手段。

### 3. 深入原理：从概念讲到机制

Skill 通常是可复用的知识/步骤/约束，不等于代码执行；Tool 是外部动作接口；Rule 应是始终生效且可强制的边界。把安全规则只写 Skill 或 Prompt 都不够，因为模型可能忽略。

* Rule 是硬约束/确定性策略；Tool/MCP 是可执行能力；Skill 更像可复用的“如何完成一类任务”的知识/流程包。Skill 可以指导模型调用多个 Tool，但不能替代 Tool 的执行权限。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run\_id / step\_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-15. Skill Registry / Discovery / Invocation 应该怎么设计？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

把 Skill 当版本化、可检索、按需加载的知识能力包：有 metadata、触发条件、依赖、权限、版本和内容，不要启动时把所有 Skill 全塞进上下文。

### 3. 深入原理：从概念讲到机制

Registry 保存 name/domain/tags/description/version/dependencies；Discovery 根据任务语义、角色和权限召回候选；Invocation 只把相关 Skill 内容注入当前 context。大 Skill 可再分层加载摘要和详细步骤。

* Skill Registry 需要 metadata：name/version/domain/trigger/inputs/required\_tools/required\_scopes/risk/compatibility。Discovery 先检索候选 Skill，Invocation 再加载完整指令和依赖。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* Skill 必须版本化，否则 Prompt/流程变更无法做 replay。生产最好记录 skill\_version 和 tool versions。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-16. 开源模型 Function Calling 较弱，怎么提升？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

先从 Schema、Tool 数量、示例和约束解码优化；仍不够再做 Tool-use SFT/偏好训练，不要第一步就换超大模型。

### 3. 深入原理：从概念讲到机制

问题要拆成三类：选错工具、参数语义错、输出格式错。格式可用 constrained decoding/JSON grammar；选择可用 Tool Retrieval + negative examples；参数可用 SFT 加真实/困难样本。评测也要分别算 tool selection accuracy 和 argument accuracy。

* 提升 Function Calling 不只靠 SFT。可以组合：更清晰 schema、减少候选工具、约束解码/grammar、两阶段“先选工具再填参数”、失败后结构化修复。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把模型输出变成结构化 contract，Runtime 校验后才进入执行。
* 为关键状态引入 run\_id / step\_id / version / status，使它可持久化、可恢复、可审计。
* 对有副作用行为增加 policy、幂等、deadline、trace 和明确的 failure type。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。
* 模型能力弱时，增加 Harness 约束往往比直接微调更快；当高频稳定错误持续出现，再用高质量 tool-use SFT。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---

## 03-17. Skill 和长期记忆有什么区别？为什么不能互相替代？

> 标签：理论、工程、实践

### 1. 面试官真正考什么

看你是否把 Tool 当作正式接口契约而不是 Prompt 附件。重点是 Schema、语义校验、权限、风险、调用协议、工具发现、MCP 边界，以及工具数量和上下文成本变大后如何治理。

### 2. 核心结论

Skill 是“怎么做某类事”的版本化方法/知识；长期记忆是“这个用户/历史发生过什么”的个体化信息。一个偏程序性知识，一个偏经历/偏好。

### 3. 深入原理：从概念讲到机制

Skill 应由团队/专家维护、可评审和发布；Memory 来自交互，需要准入、纠错和时效管理。把用户偶然经验写进 Skill 会污染全局，把稳定操作规程只存在 Memory 又无法复用。

* Skill 是“怎么做事”的程序化/策略性知识，Memory 是“这个用户/过去发生了什么”的持久化事实。Skill 应可版本化共享；Memory 带用户/会话作用域。

### 4. 工程落地：代码/状态/数据结构应该怎么设计

* 把用户偏好写进 Skill 会污染所有用户；把流程步骤写进 Memory 会导致版本漂移。两者的生命周期和权限完全不同。

**建议落地检查：** 能否回答“状态放哪、谁能改、失败后怎么恢复、旧结果怎么识别、怎么评测”？如果不能，说明方案还停留在概念层。

### 5. 结合 nanobot / Java / 实际项目

结合你现在的架构，可以把 nanobot 作为 Agent Runtime，Java/Spring 保留业务 Service、事务和权限。需要平台级增强时优先放在 AgentDock/Gateway/Tool Adapter/Harness，而不是把所有逻辑塞回 Prompt。

### 6. 失败模式与 Trade-off

* 只做 JSON 语法校验，不做业务语义和权限校验。
* Tool description 含糊，工具间能力重叠导致模型难选。
* MCP 标准化了协议却把权限、幂等、事务也错误地交给协议层。

### 8. 面试官可能继续追问

* 如果这个方案失败，系统最后会收敛到什么状态？
* 哪些属于模型软决策，哪些必须由代码硬约束？
* 你会用什么离线/线上指标证明这个设计真的更好？

### 9. 1～2 分钟口述版

面试时先给结论，再说明核心机制和失败边界，最后用实际项目说明你会如何落地。不要从术语定义开始铺满两分钟。

---
