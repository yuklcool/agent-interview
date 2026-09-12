# 2026 Agent 面试补充：Workflows vs Autonomous Agents、Orchestrator-Workers、Reflection

> 来源：用户提供的「2026 大模型 Agent 面试全攻略」截图中的 Q6～Q8。
>
> 处理原则：**不按截图原答案照抄**。先与仓库现有题目做语义去重，再把它们整理成可应对二面/三面追问的工程答案。
>
> 对应已有主线：
>
> - Q6 → `01-03 / 01-04`：DAG/Workflow 与 Agent 共存、Agent vs Workflow 选型；
> - Q7 → `02-05 / 02-09 / 02-12`：Planner/Worker/Reviewer、多 Agent 拆分、编排模式；
> - Q8 → `04-08` + `07`：Self-Reflection 失败边界、Eval/Verifier/Trajectory。
>
> 本文重点结合 **nanobot、Pi、AgentDock、OpenViking** 做案例对照，但会明确哪些是项目当前能力，哪些是企业级扩展建议。

---

# Q6. 请对比「工作流（Workflows）」与「自主智能体（Autonomous Agents）」的优劣

## 1. 面试官真正考什么

这道题表面在问“Workflow 和 Agent 谁更好”，真正考的是你能不能回答：

1. **什么时候应该允许模型自主决策？**
2. **什么时候必须把执行顺序写进代码/状态机？**
3. **开放推理和确定性副作用如何共存？**
4. **系统出错后，谁负责恢复和审计？**

如果只回答：

```text
Workflow = 稳定
Agent    = 灵活
```

只能算概念题。

---

## 2. 核心结论

不是“复杂任务用 Agent、简单任务用 Workflow”，而应该按 **不确定性 × 风险 × 可枚举性 × 审计要求** 来选。

```text
                    路径是否可枚举？
                         │
             ┌───────────┴───────────┐
             │                       │
            是                       否
             │                       │
     风险/副作用高吗？          是否需要动态探索？
       │         │              │         │
      高         低             高         低
       │         │              │         │
 Workflow   Workflow/Agent     Agent    简单 Agent/Direct
```

更准确的工程原则是：

> **Workflow 负责确定性约束与业务状态，Agent 负责语义不确定性与开放决策。**

生产系统经常是：

```text
Workflow owns state & side effects
                ↓
        Agent owns local decision
```

而不是二选一。

---

## 3. Workflow 到底强在哪里

Workflow 的核心不是“画 DAG”，而是**把控制流变成可执行契约**。

例如订票：

```text
SEARCH
  ↓
QUOTE
  ↓
LOCK
  ↓
CONFIRM
  ↓
PAY
  ↓
ISSUE
```

真正的价值在于每个状态都有明确 precondition：

```text
pay() allowed only if state == CONFIRMED
issue() allowed only if payment == SUCCESS
refund() allowed only if order is refundable
```

即使模型产生错误 Tool Call：

```text
LLM: pay()
```

Runtime/业务状态机仍然可以拒绝：

```text
PRECONDITION_FAILED:
order.state = SEARCHED
required = CONFIRMED
```

所以 Workflow 的优势是：

- 状态可解释；
- 顺序可证明；
- 审计简单；
- 容易实现幂等和恢复；
- 高风险副作用可以做强约束；
- 失败后可以明确知道停在哪一步。

### 但 Workflow 的局限也很明确

如果问题是：

> “研究一下上海未来三年智慧照明行业有哪些可落地机会，并比较政策、项目、竞品和技术路线。”

你很难在编码前枚举所有搜索分支。

这种情况下如果强行写 Workflow：

```text
search_policy
→ search_company
→ search_project
→ compare
→ summarize
```

真实执行中很快会发现：

- 搜索结果会改变下一步；
- 需要根据证据补检索；
- 不同问题需要不同 Tool；
- 计划可能动态变化。

此时过强的固定流程反而限制模型能力。

---

## 4. Autonomous Agent 到底“自主”在哪里

自主不是“模型可以随便做任何事”。

更准确地说：

> Runtime 给模型一个**受约束的动作空间**，模型在每轮 Observation 后决定下一步动作。

```text
Goal
 ↓
Context
 ↓
LLM Decision
 ├─ answer
 ├─ tool A
 ├─ tool B
 └─ ask clarification
       ↓
    Observation
       ↓
  next decision
```

真正生产级的 Agent 仍然会被代码约束：

```text
max_iterations
max_tool_calls
deadline
allowed_tools
workspace_scope
tenant_scope
cost_budget
risk_policy
```

所以截图中“由 LLM 决定循环次数和工具调用”这个说法需要修正：

> **LLM 决定下一步候选动作，但循环上限、执行权限和停止预算必须由 Runtime/Harness 控制。**

否则模型一旦进入 Tool Loop，可能无限消耗 Token 和外部 API。

---

## 5. 一个真实场景：城市照明故障处理

用户：

> “分析昨晚 A 路段 49 盏灯异常的原因，如果属于批量故障就生成处理建议，但不要直接派单。”

这里最好不是纯 Workflow，也不是纯 Agent。

### 开放分析交给 Agent

```text
查询能耗
查询报警
查询设备状态
检索历史故障经验
比较可能原因
```

模型可以根据结果动态决定是否补查天气、供电、控制器状态。

### 强约束交给 Workflow/Policy

```text
Constraint: no_auto_work_order = true
```

即使模型最后说：

```text
create_work_order(...)
```

Runtime 仍然：

```text
DENY
reason = user explicitly requested no side effect
```

这就是：

```text
Agent decides what it wants to do
Runtime decides what it is allowed to do
Business system decides what actually happened
```

---

## 6. nanobot 怎么对应

nanobot 当前核心更接近**受约束的 Tool-using Agent Runtime**：

```text
AgentRunner
   ↓
LLM
   ↓
Tool Calls
   ↓
Tool Execution
   ↓
Observation
   ↓
next iteration
```

它适合做 Workflow 某个节点中的“开放决策执行器”。

例如：

```text
Workflow Step: diagnose_fault
        ↓
     nanobot
        ↓
动态查询多个只读 Tool
        ↓
生成 diagnosis artifact
```

但业务级：

```text
CREATE_WORK_ORDER
PAY
REFUND
DELETE
```

不应该仅依赖 nanobot 的自由 Tool Loop 来维护业务状态机。

### 重要边界

nanobot 的 `max_iterations`、Tool Registry、Workspace Scope、Recovery 能提供 Runtime 约束；但它不是一个完整 BPM/交易状态机。

---

## 7. Pi、AgentDock、OpenViking 怎么放进这道题

### Pi

Pi 的价值更适合解释：**Agent Runtime/Harness 如何把一次开放执行做成 durable operation**。

它关注 Session / Operation / Effect / Recovery 这类运行状态，但这仍然不意味着业务订单状态应该由 Agent Harness 取代。

可以理解成：

```text
Business Workflow State
        │
        └── invokes
              Pi Agent Operation
                   ↓
             open-ended reasoning
```

### AgentDock

AgentDock 是上层 Control Plane，可以管理：

- Agent 实例；
- Driver；
- Task；
- Workflow；
- Container；
- Event Stream；
- Workspace / Credentials。

它非常适合承载：

```text
Workflow
  Step 1 → Nanobot Agent
  Step 2 → API Driver
  Step 3 → Reviewer Agent
```

但最终业务交易状态仍然应该在业务服务里。

### OpenViking

OpenViking 属于 Context/Memory Plane，不负责控制流。

它解决：

> “Agent 这一轮应该找回哪些 Resource / Memory / Skill？”

不是：

> “订单下一步能不能支付？”

因此不要用 Context Database 代替 Workflow State Store。

---

## 8. 面试官继续追问：Workflow 一定是 DAG 吗？

不一定。

DAG 是常见工作流形式，但很多真实业务流程存在：

```text
RETRY
REVIEW → REVISE → REVIEW
WAIT_CALLBACK
HITL → RESUME
COMPENSATION
```

这天然包含环或状态回跳。

更准确的说法是：

> Workflow 的核心是**显式状态和可执行转移规则**，而不是必须无环。

所以：

```text
DAG Workflow
State Machine
Graph Workflow with loops
```

都可以是 Workflow。

---

## 9. 1～2 分钟面试口述版

> 我不会用“简单任务 Workflow、复杂任务 Agent”来区分，我主要看路径是否可枚举、环境不确定性、副作用风险和审计要求。支付、退款、审批这类高风险状态转换应该由 Workflow/State Machine 控制，因为前置条件、顺序、恢复和审计都必须可证明；搜索、研究、故障分析这类路径不可预枚举的任务适合 Agent。生产上最常见的是混合架构：外层 Workflow 管状态和副作用，内部某些节点用 nanobot/Pi 这样的 Runtime 做局部自主决策。Agent 可以决定下一步候选动作，但 max iterations、Tool 权限、deadline 和最终业务事实必须由 Runtime 和业务系统控制。

---

# Q7. 详细解释 Orchestrator-Workers 模式

## 1. 先修正一个常见误解

Orchestrator **不一定必须是一个 LLM Agent**。

它可以是：

```text
Deterministic Orchestrator
LLM Planner
Hybrid Orchestrator
```

生产环境里更推荐：

```text
模型负责：任务语义分解
代码负责：状态提交、并发调度、权限和失败收敛
```

也就是：

```text
LLM proposes plan
Runtime commits plan
Scheduler executes workers
```

而不是让一个“Boss Agent”拥有所有控制权。

---

## 2. Orchestrator-Workers 的完整结构

```text
                 User Goal
                    ↓
             Orchestrator
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    Worker A     Worker B     Worker C
      │             │             │
 Artifact A     Artifact B     Artifact C
        └───────────┼───────────┘
                    ↓
             Aggregator/Reviewer
                    ↓
               Final Result
```

真正关键的是中间这层状态：

```text
Plan
Step
Dependency
Worker Assignment
Artifact
Evidence
Status
Deadline
Plan Version
```

如果没有这些结构，只是“主 Agent 给三个 Agent 发三段 prompt”，那更像 Demo，不是可靠 Orchestration。

---

## 3. 推荐的数据模型

### Plan

```json
{
  "plan_id": "p-1024",
  "version": 6,
  "goal": "完成一次仓库功能修改并验证",
  "status": "RUNNING"
}
```

### Step

```json
{
  "step_id": "backend-api",
  "plan_version": 6,
  "owner": "backend-worker",
  "depends_on": [],
  "required": true,
  "status": "RUNNING",
  "deadline": "...",
  "output_ref": null
}
```

### Artifact

```json
{
  "artifact_id": "a-991",
  "producer": "backend-worker",
  "plan_version": 6,
  "step_id": "backend-api",
  "type": "git_patch",
  "evidence": ["test://run-882"]
}
```

Worker 最好**产出 Artifact**，而不是直接把一大段自然语言写回共享 Prompt。

---

## 4. 拆任务的粒度怎么定

这是 Orchestrator-Workers 最核心的难点之一。

### 拆得太细

例如把一个后端改动拆成：

```text
读 Controller
读 Service
读 DTO
修改 DTO
修改 Service
修改 Controller
跑测试
```

每一步都交给不同 Agent，会产生大量：

```text
handoff
token duplication
context rebuild
artifact serialization
state sync
```

通信成本可能比任务本身还高。

### 拆得太粗

例如：

```text
Worker A: “把后端全部搞定”
```

Worker 内部又会变成一个不可观测的大黑盒，失败后无法知道：

- 是理解错？
- 改错文件？
- 测试没过？
- API 契约冲突？

### 一个实用判断

一个 Step 值得成为独立 Worker，最好至少满足：

1. 有清晰输入；
2. 有清晰输出契约；
3. 可独立验证；
4. 可独立重试；
5. 有真正并行价值、权限隔离价值或 Context 隔离价值。

如果一个子任务无法独立验收，通常不值得拆成 Agent。

---

## 5. 软件开发场景怎么用

比如实现一个“用户上传 CSV 后自动生成分析报告”的功能：

```text
Orchestrator
   ↓
Plan v1
   ├─ S1 Backend Worker
   │      → API / storage / parser patch
   │
   ├─ S2 Frontend Worker
   │      → upload / progress UI patch
   │
   ├─ S3 Test Worker
   │      → integration test plan
   │
   └─ S4 Reviewer
          → contract + test + security check
```

但要注意：

```text
Frontend Worker
```

可能依赖后端 API Schema，所以真正的 dependency graph 可能是：

```text
Define Contract
   ├── Backend
   └── Frontend
        ↓
Integration Test
        ↓
Reviewer
```

也就是说 Orchestrator-Workers 和 DAG 往往天然结合。

---

## 6. nanobot 当前能做到什么

nanobot 当前有真实的 `SubagentManager`。

从实现上能看到：

```text
task_id
SubagentStatus
max_concurrent_subagents
asyncio.Semaphore
background task
inline task
isolated ToolRegistry
WorkspaceScope
AgentRunner
max_iterations
```

所以可以形成：

```text
Main Agent
   ↓ spawn
SubagentManager
   ↓ capacity semaphore
Worker
   ├─ isolated tools
   ├─ workspace scope
   ├─ AgentRunner
   └─ status/hook
```

这已经是一个真实的 Worker Runtime 基础。

但不能因此说 nanobot 已经原生拥有完整的：

```text
Plan DAG
plan_version
artifact store
reviewer workflow
distributed orchestrator
```

这些能力如果需要，应该放到 AgentDock / 上层 Orchestrator。

---

## 7. AgentDock 很适合承载 Orchestrator 层

AgentDock 当前已经有：

```text
Agent / Container
Driver Registry
Task
Event Stream
Workflow
Persistent Workspace
Cancel / Pause / Resume
```

所以它比单个 Runtime 更适合保存：

```text
workflow_run_id
step_run_id
agent_id
status
input_artifact
output_artifact
started_at
finished_at
```

例如：

```text
AgentDock Workflow
   ↓
Step 1 → Nanobot Research Agent
Step 2 → API Driver 做结构化抽取
Step 3 → Code Agent 修改仓库
Step 4 → Reviewer Agent
```

这里 AgentDock 负责 Control Plane 和 Workflow 状态，每个 Worker Runtime 只负责自己的局部执行。

---

## 8. OpenViking 在 Orchestrator-Workers 中的角色

多个 Worker 可能需要共享：

- 项目文档；
- 用户长期偏好；
- Skill；
- 历史经验；
- 规范资料。

这些可以由 OpenViking 提供 Context/Memory。

但要区分：

```text
OpenViking = shared context substrate
Workflow DB = current execution state
```

不能把：

```text
plan_version
step lock
worker status
```

写进“长期记忆”然后希望它承担并发控制。

---

## 9. Worker 失败怎么处理

每个 Step 不应该只有：

```text
SUCCESS / FAIL
```

至少考虑：

```text
PENDING
RUNNING
SUCCESS
FAILED
TIMEOUT
CANCELLED
UNKNOWN
STALE
```

并且 Step 还需要：

```text
required: true/false
retry_policy
fallback_worker
deadline
plan_version
```

例如：

```text
Backend Worker = SUCCESS, required
Frontend Worker = SUCCESS, required
Test Worker = TIMEOUT, required
```

最终不能直接说“功能完成”。

正确结果可能是：

```text
IMPLEMENTED_BUT_UNVERIFIED
```

或阻塞到 Reviewer/HITL。

---

## 10. 1～2 分钟面试口述版

> Orchestrator-Workers 不是一个 Boss Agent 给几个 Worker 发 prompt 这么简单。真正生产实现里，我会把 Orchestrator 分成“计划生成”和“状态提交”两部分：LLM 可以产出结构化 Plan，但 Runtime 负责保存 plan_version、step dependency、deadline 和 Worker 状态。Worker 只拿完成当前 Step 所需的最小 Context 和 Tool，并产出带 evidence 的 Artifact；最后由 Aggregator/Reviewer 汇总。任务粒度要求可独立输入、输出、验证和重试，否则拆太细会造成 token 和 handoff 爆炸。nanobot 的 SubagentManager 已经提供 background worker、并发 semaphore、独立 ToolRegistry 和 AgentRunner，但完整 DAG/Artifact/Reviewer 状态机更适合放在 AgentDock 这类平台层。

---

# Q8. 什么是 Reflection / Self-Correction 模式？

## 1. 这道题最容易答错的地方

截图里说“这是提升 Agent 成功率最有效的模式”，这种表述太绝对。

Reflection 有价值，但它不是万能增强器。

模型第一次错，第二次让同一个模型“再想想”，可能发生：

```text
原来错
  ↓
更加自信地错
```

或者：

```text
第一次答案已经对
  ↓
Reflection 继续修改
  ↓
反而改错
```

所以生产中的 Reflection 应该理解为：

> **基于可验证反馈进行受预算约束的再次决策。**

关键不是“多想一次”，而是：

```text
Verifier / Evidence / Tool Result
           ↓
       identify defect
           ↓
       targeted revision
```

---

## 2. 三种 Reflection 形态

### 形态一：Self-Critique

同一个模型：

```text
Generate
  ↓
Critique
  ↓
Revise
```

成本低，但 Critic 和 Generator 共享同一盲点。

### 形态二：Generator + Reviewer

```text
Generator Model
       ↓
Draft / Plan
       ↓
Reviewer Model
       ↓
PASS / REVISE / ESCALATE
```

Reviewer 可以使用不同 Prompt、不同模型，甚至不同 Tool View。

### 形态三：External Verifier

这是生产环境里最可靠的方向。

```text
Agent produces result
       ↓
Deterministic Verifier
 ├─ JSON Schema
 ├─ Unit Test
 ├─ SQL Parser / EXPLAIN
 ├─ Business Precondition
 ├─ Citation Check
 └─ Policy Check
       ↓
structured feedback
       ↓
Agent retries / revises
```

可验证任务最好不要只靠另一个 LLM“觉得答案对”。

---

## 3. Reflection 最适合什么任务

### Code Agent

```text
Generate Patch
   ↓
Run Unit Tests
   ↓
FAILED
   ↓
Feed exact test failure
   ↓
Patch Revision
```

这里反馈是真实测试结果，非常适合 self-correction。

### Text-to-SQL

```text
Generate SQL
   ↓
AST Validation
   ↓
EXPLAIN / DB Error
   ↓
structured error
   ↓
regenerate SQL
```

比一句：

> “请反思你的 SQL 是否正确。”

有效得多。

### Tool Calling

```text
LLM tool arguments
    ↓
Schema / Domain Validator
    ↓
INVALID_ARGUMENT
    ↓
把具体字段错误回注
    ↓
repair arguments
```

这实际上也是一种基于环境反馈的自我纠正。

---

## 4. Reflection 为什么会死循环

最常见的模式：

```text
Generator
   ↓
Reviewer: not good enough
   ↓
Generator revision
   ↓
Reviewer: still not good enough
   ↓
...
```

如果 Reviewer 没有明确 Definition of Done，就会无限迭代。

必须加入：

```text
max_reflections
max_revisions
global_deadline
token_budget
cost_budget
no_progress_detector
terminal verdict
```

Reviewer 最好只输出有限状态：

```text
PASS
REVISE(reason, evidence)
ESCALATE
```

而不是一大段开放评论。

---

## 5. No-progress Detection

仅仅有 `max_iterations=5` 只能防止无限运行，不能识别“已经没有进展”。

可以保存每轮 fingerprint：

```text
input_hash
plan_hash
tool_name + normalized_args
error_type
artifact_hash
reviewer_reason
```

如果连续两轮：

```text
同一个 SQL
→ 同一个 DB error
→ 同一个 revision
```

就应该：

```text
NO_PROGRESS
   ↓
change strategy / stronger model / HITL
```

而不是继续 Reflection。

---

## 6. 「记录失败轨迹作为记忆」要非常谨慎

截图中提到：

> 记录失败轨迹作为长短期记忆，避免重复错误。

方向没错，但不能把所有失败直接写进长期 Memory。

否则会产生：

```text
一次偶发 API Timeout
      ↓
写成“这个 API 不可靠”
      ↓
长期影响未来决策
```

更合理的流程：

```text
Failure Trajectory
      ↓
Classification
      ↓
Is this reusable knowledge?
   ├─ No  → Trace/Eval only
   └─ Yes
        ↓
Generalize
        ↓
Validate
        ↓
Memory Admission
        ↓
Store with provenance/version
```

### 适合进入长期经验的

例如：

```text
设备能耗表本身没有 project_id，权限必须通过 device 表关联 project
```

这是稳定领域知识。

### 不适合直接进入长期记忆的

```text
今天 14:03 MCP Server 超时一次
```

这是运行事件，应进入 Trace/Observability，而不是长期 Memory。

---

## 7. nanobot 中已经存在什么“自我纠正基础”

nanobot 的 Tool Loop 本身已经具备一种最基础的环境纠错机制：

```text
LLM proposes Tool Call
      ↓
Tool Execution / Validation
      ↓
Tool Result / Error
      ↓
next model iteration
```

模型看到真实 Tool Error 后，可以在下一轮修正参数或换 Tool。

这属于：

```text
Observation-driven correction
```

但不能因此说 nanobot 当前原生有一个完整的通用：

```text
Reflection Agent
Critic Agent
Reviewer Loop
Reflection Memory
```

如果需要 Reviewer/Reflection，可以作为上层模式实现，并受 `max_iterations` / deadline / Tool policy 约束。

---

## 8. Pi、AgentDock、OpenViking 怎么对应 Reflection

### Pi

Pi 更适合回答“修正过程如何成为 durable operation”。

如果 revision 过程中进程中断，真正可靠的系统需要知道：

```text
当前 operation 到哪一步？
上一轮 effect 是否已经发生？
恢复后应该 replay 还是等待确认？
```

Reflection 不能脱离 Recovery 语义。

### AgentDock

AgentDock 可以把 Reflection 组织成多个 Task/Workflow Step：

```text
Generate Task
   ↓
Verify Task
   ↓
Revision Task
```

Task Event Stream 还能记录：

```text
iteration
Tool Calls
Tool Result
file changes
status
```

这样比在一个大 prompt 里隐藏多轮修正更容易观察和评估。

### OpenViking

OpenViking 可以存真正经过 admission 的长期经验，但更适合存：

```text
validated lesson
stable user preference
reusable skill
reusable resource
```

而不是把每一轮失败 Trace 都自动转成 Memory。

Trace Store 和 Memory Store 应该分开。

---

## 9. 一个实际案例：Agent 自动修复 SQL

用户：

> “查询最近 30 天当前用户有权限的所有灯杆异常能耗。”

第一次模型生成：

```sql
SELECT *
FROM energy_history
WHERE created_at >= now() - interval '30 day';
```

Validator 发现：

```text
PERMISSION_PATH_MISSING
energy_history has no project_id
required relation:
energy_history.device_id
→ device.device_id
→ device.project_id
→ allowed_project
```

系统不直接让模型“反思”，而是回给结构化反馈：

```json
{
  "error_type": "PERMISSION_PATH_MISSING",
  "required_join_path": [
    "energy_history.device_id=device.device_id",
    "device.project_id IN allowed_projects"
  ]
}
```

第二轮生成：

```sql
SELECT eh.*
FROM energy_history eh
JOIN device d ON d.device_id = eh.device_id
WHERE d.project_id = ANY(:allowed_projects)
  AND eh.created_at >= now() - interval '30 day';
```

然后继续：

```text
AST Security Check
      ↓
EXPLAIN Cost Guard
      ↓
Read-only Execution
```

这就是比“Critic 再看一遍”更真实的 Self-Correction。

---

## 10. Reflection 的正确位置

可以把 Agent 的纠错层级理解成：

```text
Level 0: Schema Validator
Level 1: Tool / Environment Feedback
Level 2: Deterministic Verifier
Level 3: Reviewer Model
Level 4: Human-in-the-loop
```

优先使用越靠下成本越低、确定性越高的验证机制。

不要所有错误都直接升级成：

```text
“再请一个大模型反思一下”
```

---

## 11. 1～2 分钟面试口述版

> Reflection 不是简单让模型“再想一遍”，而是基于可验证反馈做受预算约束的修正。最弱的是同模型 self-critique，更可靠的是 Generator + Reviewer，而在代码、SQL、Tool Calling 这类可验证任务里，我更倾向用单测、Schema、AST、数据库错误或业务 precondition 作为 external verifier，再把结构化错误回注模型。Reflection 一定要有 max revision、deadline、no-progress detection 和明确 Definition of Done，否则 Reviewer 和 Generator 可能无限互相打回。nanobot 的 Tool Result→下一轮 LLM 已经具备基础的 observation-driven correction，但不是完整 Reflection 框架；AgentDock 可以把 Generate/Verify/Revise 做成可观测 Workflow，OpenViking 只保存经过 admission 的稳定经验，而不是把每次失败轨迹直接写成长记忆。

---

# 三道题放到一张图里

```text
                         Control Plane
                           AgentDock
                              │
                              ▼
                   Workflow / Orchestrator
                状态 / 依赖 / Budget / Deadline
                  │                     │
        ┌─────────┴─────────┐           │
        ▼                   ▼           ▼
    Agent Worker         Agent Worker  Verifier
    nanobot / Pi         nanobot / Pi    │
        │                   │            │
        └──────────┬────────┘            │
                   ▼                     │
                Artifact ────────────────┘
                   │
             PASS / REVISE
                   │
                   ▼
               Final Result

      Context / Memory Plane: OpenViking
      Business Truth Plane: Java / DB / API
```

这三道题真正应该形成的统一认识是：

> **Workflow 决定系统允许如何流转，Orchestrator 决定任务如何拆和调度，Worker 负责局部开放执行，Verifier/Reflection 负责基于证据修正，Context System 提供相关信息，最终业务事实仍由业务系统掌控。**
