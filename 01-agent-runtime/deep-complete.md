# 01. Agent Runtime、Loop 与系统边界——全量深度版

> 本文件覆盖 `01-01`～`01-16` 全部问题。它是本章的权威学习版本；原 `chapter.md` 继续保留为快速题库索引。
>
> 案例基线：**Pi、nanobot、AgentDock、OpenViking**。不会把四个项目机械塞进每题，而是根据问题选择最合适的真实实现做对照。

---

## 01-01. 讲一个落地过的 AI Agent 项目：从用户提问到最终回答完整链路

### 面试官真正考什么

不是考“会不会调 LLM API”，而是看你是否能把 Agent 解释成一个**带状态、循环、工具、恢复、权限和观测能力的运行系统**。如果只回答“用户→LLM→Tool→答案”，通常只能算 Demo 级理解。

### 核心结论

一个生产 Agent 至少存在四类 owner：

```text
Control Plane  —— 谁能用、哪个实例、资源/租户/生命周期
Agent Runtime  —— 本轮怎么循环、怎么构造 Context、怎么执行 Tool
Context System —— 记忆/知识/资源从哪里取、给模型哪些信息
Business System—— 订单/设备/退款/工单等最终业务事实
```

模型只拥有**提议权**，不拥有业务事实写权限和最终副作用执行权。

### 运行链路

```text
Browser / App
      ↓
Auth + Tenant + Session Resolution
      ↓
Agent Runtime 接收 Turn
      ↓
Durable Transcript / Runtime State
      ↓
Context Projection
 ├─ System / Policy
 ├─ Recent History / Summary
 ├─ Memory / RAG
 ├─ Tool Schemas
 └─ Current Observation
      ↓
LLM Round
      ↓
Assistant Text / Tool Calls
      ↓
Tool Registry → Schema → Policy → Business Validation
      ↓
MCP / HTTP / DB / Java Service
      ↓
Tool Result / Observation
      ↓
再次 Context Build → 下一轮 LLM
      ↓
Stop / Final / Checkpoint / Persist / Stream
```

关键点是：**每一次 LLM 调用前，Context 都是重新构造的；每一次 Tool Call 都只是模型提出动作，Runtime 才执行。**

### 四个项目怎么对照

- **nanobot**：`AgentLoop` 承接产品层会话，`AgentRunner` 负责 tool-using loop；`AgentRunSpec` 提供 runtime、tools、iteration、checkpoint、injection 等运行参数；`ContextGovernor` 治理 model-facing context。
- **Pi**：`pi-agent-core` 是 Agent Runtime；新的 Harness 设计进一步把 Session、Branch、AgentLane、operation state、effect intent/settlement 明确成持久执行语义，适合解释“真正 durable 的 Agent Runtime”。
- **AgentDock**：不是另一个 Loop，而是平台/Control Plane。它管理 tenant、agent/container、driver、task、workspace、credentials、events、resource limits；运行时可以是 nanobot、Pi 或其他 Driver。
- **OpenViking**：不是 Loop，而是 Context Database；用 `viking://` 统一管理 resource/memory/skill，按 L0/L1/L2 加载，解决“哪些上下文应该找回来”。

### 实际项目场景

例如城市照明：

```text
用户：“分析昨晚异常能耗，并创建需要人工处理的工单”
      ↓
Agent 先调用查询 Tool
      ↓
Java 服务根据 user/project 权限查设备和能耗
      ↓
LLM 对事实结果做异常分析
      ↓
Runtime 判断要调用 create_work_order
      ↓
Tool Policy 检查是否有权限 + 参数是否完整
      ↓
Java WorkOrderService 开事务创建工单
      ↓
返回 work_order_id + status
      ↓
只有业务返回 SUCCESS，LLM 才能说“已创建”
```

### 失败时怎么收敛

必须能回答五件事：

1. LLM 调用超时：本轮是否可重试、预算多少？
2. Tool 调用超时：read-only 还是 side-effect？是否进入 UNKNOWN？
3. 进程崩溃：Session/Checkpoint 从哪里恢复？
4. 用户中途改需求：旧异步结果如何通过 `plan_version`/`run_id` 判为 stale？
5. 最终业务事实由谁确认：永远不是模型自己猜。

### 1～2 分钟口述版

> 我把 Agent 当作 Runtime，而不是聊天模型。入口先完成身份和 Session 解析，Runtime 从 durable transcript、summary、memory/RAG 和 Tool Schema 生成本轮 model-facing context；LLM 只负责提出文本或 Tool Call，真正执行前 Runtime 还要做 Schema、权限和业务校验，Tool Result 再作为 observation 回注，循环直到满足停止条件。像 nanobot 负责轻量 Agent Loop，Pi 更强调 durable Harness，AgentDock 负责多租户和容器化 Control Plane，OpenViking负责 Context/Memory。真正订单、退款、工单状态仍由 Java 业务系统作为事实源。

---

## 01-02. 最近在看什么 AI 工程化？Spring AI 还是 LangGraph？说一个不喜欢的点

### 核心判断

框架选型不是比较 API 好不好看，而是比较**谁拥有状态、谁拥有控制流、谁拥有恢复语义、谁拥有工具和业务事务**。

Spring AI 更适合“把模型能力嵌入现有 Spring 应用”；LangGraph 更适合“显式 state/graph/checkpoint 编排”。如果系统已经用 nanobot/Pi 作为 Runtime，再在 Java 里叠一套第二 Agent Loop，很容易产生：

```text
两个 Session owner
两个 retry 机制
两个 checkpoint
两个 tool registry
两个 trace
两个取消语义
```

这比框架本身的优缺点更重要。

### 怎么做真实选型

我会按以下问题判断：

- 控制流是否必须显式成图？
- 长任务是否需要 durable checkpoint？
- Java 事务和权限是否是核心？
- Tool 是本地 Bean 还是跨语言 MCP？
- Runtime 是嵌入式还是独立服务？
- 失败恢复发生在哪一层？
- 团队是否需要 Python Runtime？

### 结合实际项目

如果用 **AgentDock + nanobot**：

```text
AgentDock = Control Plane
nanobot   = Runtime owner
Java      = Domain Service
```

Java 侧不需要再造一套 Agent Loop；Spring AI 可以用于某些纯 Java 模型调用、结构化生成或独立服务，但不要同时争夺 Session/Loop owner。

如果某一条交易链必须 `QUOTE → LOCK → CONFIRM → PAY → ISSUE`，可以在 Java Workflow/State Machine 中控制；节点内部再让 nanobot 做开放搜索，而不是让整个支付链交给 LangGraph/nanobot 自由推理。

### 我不喜欢的点怎么说

不要说“LangGraph 太复杂”“Spring AI 功能少”这种情绪评价。可以说：

> 我不喜欢把高层框架抽象误认为业务可靠性。无论 Spring AI 还是 LangGraph，当进入权限、幂等、恢复、人工确认、跨服务事务时，最终都需要显式 Runtime contract。框架能减少样板代码，但不能替代系统边界设计。

---

## 01-03. DAG 工作流和自主 Agent 在订票订酒店场景怎么共存

### 核心结论

**开放决策交给 Agent，确定性副作用交给 Workflow。** 不是二选一，而是外层确定性、内层自主性。

```text
User Intent
    ↓
Agent：理解偏好 / 搜索 / 排序 / 解释
    ↓
Workflow：Quote → Lock → Confirm → Pay → Issue
                   ↑
            高风险节点前可 HITL
```

### 为什么

搜索酒店、比较航班、解释签证要求具有开放空间，路径无法完全枚举；支付、锁库存、退款存在强前置条件和副作用，必须可审计、可恢复、可证明顺序。

Workflow state 应该是事实源，例如：

```text
SEARCHED → QUOTED → LOCKED → CONFIRMED → PAID → ISSUED
```

`pay()` 的 precondition 是 `state == CONFIRMED`。即使模型直接请求 `pay`，Dispatcher 也应拒绝。

### 项目对照

- nanobot：适合作为某个 DAG 节点内的开放 Tool Loop，不是完整交易状态机。
- Pi Harness：适合解释 durable operation/effect，但业务交易状态仍属于业务服务。
- AgentDock：可以在平台层承载跨 agent task/workflow，但 Domain State 不能只存在平台任务状态里。

### 追问：Agent 能不能自己规划完整支付流程？

可以“提出计划”，不能成为唯一执行规则。模型计划属于 proposal；真实状态机和 precondition 属于 executable contract。

---

## 01-04. Agent 和 Workflow 到底怎么选？判断标准是什么？

不要按“简单/复杂”选，而按四个维度：

| 维度 | 更偏 Agent | 更偏 Workflow |
|---|---|---|
| 路径 | 事前不可枚举 | 可枚举 |
| 环境反馈 | 高不确定、需动态探索 | 稳定 |
| 副作用 | 低/可逆 | 高风险/不可逆 |
| 审计要求 | 允许概率路径 | 必须可证明顺序 |

### 一个非常重要的反例

“退款 10 元”语义上很简单，但风险高，因此不能因为“简单”就让 Agent 自由执行。相反，“解释一份 100 页规范”推理复杂，但没有副作用，可以高度 Agent 化。

### 企业设计

最常见的是：

```text
Workflow owns state & side effects
          ↓
Agent nodes own semantic uncertainty
```

这也是回答“Agent 会不会取代所有 BPM/Workflow”的关键：不会。Agent 解决的是传统流程难以预枚举的决策空间，不是取消确定性流程。

---

## 01-05. 从学术和工程两个角度看，Agent 由哪些部分组成？

### 学术抽象

可以抽象为：

```text
Agent = Policy / Reasoner + State/Memory + Actions + Environment Feedback
```

模型根据 observation 和内部上下文选择下一动作，环境返回新的 observation，形成闭环。

### 工程抽象

生产环境更应该拆成：

```text
Transport/Auth
Session/State
Context Builder
Model Runtime
Tool Registry
Policy/Permission
Execution Engine
Recovery/Checkpoint
Observability/Eval
Sandbox/Resource Governance
```

### 为什么差别重要

学术定义帮助理解“为什么 Agent 是闭环决策系统”；工程定义解决“怎么让它线上不出事故”。很多面试回答的问题就是把这两个层次混为一谈。

### 项目映射

- nanobot：Loop、Runner、Context、Tool、Recovery、Hook。
- Pi：Agent runtime + durable Harness state machine。
- AgentDock：runtime 之外的 Control Plane、Container、Tenant、Driver。
- OpenViking：Context/Memory/Resource/Skill 数据层。

如果能把四者放到同一张架构图上，基本已经超出“背框架 API”的层次。

---

## 01-06. CoT 和 ReAct 的核心区别是什么？

### 不要把答案说成“一个思考，一个思考+行动”就结束

更准确地说，CoT 是模型内部/生成侧的多步推理策略；ReAct 是**推理决策和外部环境交互交替进行的控制模式**。

```text
CoT：Input → Reasoning → Answer

ReAct：
Input
 ↓
Decision → Action
          ↓
      Observation
          ↓
       Decision
          ↓
         ...
```

### 工程关键点

现代模型的私有 reasoning 往往不会、也不应该要求暴露。生产系统关注的不是保存模型完整“Thought”，而是保存可审计的：

```text
assistant action/tool call
arguments
observation/tool result
state transition
final answer
```

因此面试中最好说“reasoning/decision”而不是要求系统把隐藏思维链作为运行协议。

### nanobot 对照

nanobot 的核心是 tool-using loop：模型响应里若有 Tool Calls，Runtime 执行并把 Tool Result 回注，下一轮再决策。这个行为具备 ReAct 风格的 observation loop，但不等于必须暴露显式 `Thought:` 文本。

---

## 01-07. Tree of Thoughts（ToT）适不适合线上 Agent？为什么？

### 核心结论

ToT 的思想有价值，但“完整树搜索”通常不适合作为所有线上请求的默认路径；更实用的是**受预算约束的 candidate branching / beam search / verifier selection**。

### 成本为什么会爆

若每层产生 `b` 个候选，深度 `d`，理论搜索空间接近 `b^d`。在线 Agent 还会叠加 Tool 调用、Context、网络延迟，所以不仅 Token 贵，外部副作用也不能随便复制分支。

### 线上怎么轻量化

```text
High-value difficult step
       ↓
Generate 2~3 candidates
       ↓
Rule / Verifier / small judge
       ↓
Keep top 1~2
       ↓
Execute only safe selected branch
```

副作用 Tool 绝不能因为三个思路就真的执行三次。分支应停留在 planning/simulation 层，真正 effect 只有 winner 执行。

### 适合场景

复杂代码修复方案、长规划、关键 SQL 生成、配置迁移可以用少量分支；普通 FAQ、一次查询没有必要。

---

## 01-08. Planner 和 Executor 应该怎么通信？为什么不能只传自然语言？

### 核心结论

Planner 输出应该是**结构化计划协议**，自然语言只做说明，不做唯一控制面。

```json
{
  "plan_id": "p-17",
  "version": 3,
  "steps": [
    {
      "step_id": "s1",
      "goal": "query flight",
      "depends_on": [],
      "allowed_tools": ["flight_search"],
      "status": "READY"
    }
  ]
}
```

Executor 返回：

```json
{
  "plan_id": "p-17",
  "plan_version": 3,
  "step_id": "s1",
  "status": "SUCCEEDED",
  "artifact_id": "a-92",
  "evidence": ["tool_call:tc-8"]
}
```

### 为什么不能只传自然语言

自然语言容易出现：步骤 ID 丢失、依赖不明确、状态无法 CAS、旧结果无法识别、权限无法投影、Trace 无法关联。

### Multi-Agent 进一步要求

Planner、Worker、Reviewer 共享的应该是 task state/artifact/evidence，而不是各自复制全量聊天记录。这样 Worker 失败后可以重新调度，Reviewer 也能验证具体 evidence。

---

## 01-09. Planner 怎么避免每一步都重规划导致路径震荡？

### 问题本质

重规划不是越多越聪明。每得到一点 observation 就推翻整个计划，会造成：

- Tool 重复调用；
- 目标漂移；
- Plan v1/v2/v3 相互污染；
- 无法恢复和审计；
- 成本和延迟爆炸。

### 正确设计

使用**局部修复 + replan trigger**：

```text
正常结果 → 继续原 Plan
可恢复局部失败 → retry / alternative step
关键假设失效 → replan affected subtree
用户改变目标 → new plan_version
硬约束改变 → full replan
```

同时维护：

```text
plan_id
plan_version
step_id
assumption_version
artifact provenance
```

旧 Worker 返回 `plan_version=3`，当前已经是 4，则不能写回 current state。

### 面试口径

> Planner 不是每轮都“重新想一遍”。我会定义明确 replan trigger，只重算受影响子图；用户改目标时递增 plan_version，旧异步结果只能作为历史 artifact，不能覆盖新计划。

---

## 01-10. 如果模型生成能力很强，但流程遵循能力一般，怎么放进强约束工作流？

### 核心原则

**把顺序从 Prompt 变成 executable precondition。**

模型可以生成优秀内容，但不擅长稳定遵守 `A→B→C`，就让模型只决定开放字段，代码决定状态转换。

```text
Model: proposal
     ↓
Runtime: validate
     ↓
Workflow state machine
     ↓
Tool policy
     ↓
Effect
```

例如：

```text
quote()    requires state=SEARCHED
lock()     requires state=QUOTED
pay()      requires state=CONFIRMED
issue()    requires state=PAID
```

模型想越级调用 `pay()`，Tool Dispatcher 返回 `PRECONDITION_FAILED`。模型可以调整计划，但不能绕过状态机。

### 为什么比 Prompt 靠谱

Prompt 是概率性约束；状态机是确定性约束。模型升级后行为分布变化时，显式 precondition 仍成立。

---

## 01-11. Agent Loop 什么时候应该停止？怎么判断“信息已经够了”？

### 停止条件不是一句“模型返回 final”

至少有五类：

1. **Task satisfied**：模型给出 final，且 required evidence/steps 已满足。
2. **Budget exhausted**：iteration/token/cost/deadline 超限。
3. **No progress**：重复 Tool、重复错误、状态不变化。
4. **Hard failure**：不可恢复外部错误、权限拒绝。
5. **Human boundary**：需要确认/澄清/审批。

### 怎么判断“够了”

不是让模型纯自评，可以由 Runtime 维护 completion contract：

```text
required_fields
required_evidence
required_steps
forbidden_unknowns
```

例如“分析 10 个异常设备并生成工单建议”至少要有设备列表、指标证据、原因解释；如果必须创建工单，还需要 `work_order_id`。缺证据就不能判成功。

### no-progress guard

可维护 `(tool_name, normalized_args)` 次数、连续无新增 evidence 次数、step state 是否变化。nanobot 当前已经有 repeated external lookup guard 的思路，企业平台可进一步做 generic progress detector。

---

## 01-12. Model 和 Agent 的差别是什么？为什么不能把“会调工具的模型”直接等同于 Agent？

### 核心结论

Model 是一个概率函数；Agent 是**把模型放进有状态的感知—决策—执行闭环后的系统**。

```text
Model:
input → output

Agent:
state/context → model decision → action → environment → observation
      ↑                                             ↓
      └──────────────── update / loop ─────────────┘
```

会 Function Calling 只代表模型能生成结构化 action proposal，不代表它拥有：Session、Tool execution、retry、recovery、permission、sandbox、budget、trace、memory、multi-user isolation。

### 项目对照

- `pi-ai` 是统一模型 API；`pi-agent-core` 才是 Agent runtime。
- nanobot provider 负责 LLM 请求，`AgentRunner` 才组织 Agent Loop。
- AgentDock 甚至可以有 `API` driver：纯单次 LLM 调用，没有 Tool/Workspace；这恰好说明“模型调用”和“Agent Runtime”是两个层级。

---

## 01-13. DAG 工作流和带环的 Agent Graph 有什么区别？什么时候必须允许环？

### DAG

保证无环，节点按依赖最终终止，适合确定业务流程和可证明执行顺序。

### Agent Graph 为什么需要环

Agent 天然存在“执行→观察→修正”：

```text
Plan
 ↓
Execute
 ↓
Observe
 ↓
Validate
 ├─ enough → Finish
 └─ not enough → Replan / Retry ──┐
                                  └→ Execute
```

检索补充、Tool 参数修复、代码测试失败后修复都需要环。

### 允许环不等于允许无限环

每条环必须有：

```text
max_attempts
progress predicate
deadline
cost budget
state transition
fallback
```

例如 Code Agent 连续测试失败 3 次且 failure fingerprint 没变化，应停止或升级模型，而不是 Reflection 无限循环。

---

## 01-14. Agent 和 Siri/传统意图助手的本质差别是什么？

传统助手通常是：

```text
Intent Classification
      ↓
Slot Filling
      ↓
Fixed Handler / Workflow
```

Agent 更像：

```text
Open-ended Goal
      ↓
Dynamic Context
      ↓
Model chooses actions
      ↓
Environment feedback
      ↓
Adaptive loop
```

本质差异不是“用了大模型”，而是**控制流是否可以在运行时根据环境反馈动态产生**。

但企业系统不会把所有传统确定性能力都扔掉。账户登录、付款、权限校验、设备控制等仍然适合确定 handler。Agent 是扩大可处理任务空间，不是取消确定性软件。

---

## 01-15. Vibe Coding 和 Harness Engineering 怎么看？

### Vibe Coding 的价值

快速探索、让模型直接修改代码、运行测试、迭代，适合低成本原型和开发者个人循环。

### 到生产为什么需要 Harness

一旦 Agent 可以写文件、执行 shell、访问网络、提交代码，就必须回答：

```text
允许读哪里？
允许写哪里？
命令在哪个 sandbox 里跑？
能否访问内网/metadata？
失败能否恢复？
每次 Tool 调用能否 trace？
修改能否 diff/review/test？
```

### Pi 与 AgentDock 是很好的反例/正例对照

Pi README 明确说明本身默认以启动进程权限运行，不内建完整 filesystem/process/network/credential permission system，因此官方建议需要强边界时用 Docker、Gondolin/OpenShell 等隔离。AgentDock 则从平台层把每个 agent 放进独立容器，配 read-only root、capability drop、资源限制、egress filtering、workspace volume。

这说明 Harness Engineering 的核心不是“多写 Prompt”，而是**把模型自由度放到一个受约束的执行环境里**。

---

## 01-16. Harness 和“把 Agent 能力训练进模型”这两条路线是什么关系？

### 不是替代关系

可以把能力拆成两类：

**适合进模型的软能力：**
- Tool 选择先验；
- 参数生成；
- 长任务分解；
- 错误理解和修复；
- 领域语言理解。

**必须留在 Harness/代码的硬约束：**
- 权限；
- 预算；
- Tool precondition；
- 幂等；
- 审计；
- crash recovery；
- sandbox；
- 业务状态机。

### 判断原则

如果能力要求“100% 不能越界”“进程重启后仍然成立”“不同模型都必须一致”，就不应该只训练到模型里。

### 真实系统形态

```text
Better Model
  ↓ 提高 proposal quality
Harness
  ↓ 保证 execution safety/reliability
Business Service
  ↓ 保证 domain truth
```

模型升级可以减少错误 Tool Call、减少重试、提升计划质量；Harness 仍然是最后执行秩序。两条路线一起推进，而不是模型越强就把 Harness 删除。

---

# 本章复习主线

把 16 道题串起来，真正要掌握的是：

```text
Model ≠ Agent
     ↓
Agent = decision loop
     ↓
Loop 需要 Context / Tool / State / Stop
     ↓
开放决策用 Agent
确定副作用用 Workflow
     ↓
Planner/Executor 用结构化状态通信
     ↓
循环必须有 progress/budget/stop
     ↓
强约束放 Harness，不放 Prompt
     ↓
Control Plane / Runtime / Context / Business 分层
```

源码与项目建议阅读：

- Pi：`packages/agent/src/agent.ts`、`packages/agent/docs/harness.md`
- nanobot：`nanobot/agent/loop.py`、`nanobot/agent/runner.py`、`nanobot/agent/tools/execution.py`
- AgentDock：根 `README.md` 的 Architecture / Drivers / Tasks / Security
- OpenViking：根 `README.md` 的 Context Database / L0-L1-L2 / Session / Retrieval
