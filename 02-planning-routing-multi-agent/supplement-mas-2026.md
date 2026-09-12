# 2026 Agent 面试补充：Multi-Agent Systems（MAS）

> 来源：用户提供的“2026 大模型 Agent 面试全攻略（上）”截图中的 Q4、Q5。
>
> 本文件不重复增加核心题编号，而是将截图里的高频问法映射到现有 `02-planning-routing-multi-agent/deep-complete.md`，并按当前仓库标准重新深挖。
>
> 主要映射：
>
> - Q4 → `02-05` 多 Agent 角色边界、`02-09` 什么时候拆 Subagent、`02-12` 常见编排模式；
> - Q5 → `02-11` 避免 Handoff 死循环、并补充 No-progress Detection、预算、终止状态、消息去重和幂等。
>
> 案例基线：**nanobot + AgentDock + Pi + OpenViking**。

---

# Q4：单 Agent 遇到瓶颈时，为什么需要 Multi-Agent？常见协作模式有哪些？

## 1. 面试官真正考什么

表面上是在问“Multi-Agent 的优点”，实际上是在考三个能力：

1. 你是否知道 **什么时候真的需要拆 Agent**；
2. 你是否理解 Multi-Agent 的难点不在“多开几个模型”，而在**状态、权限、通信和调度**；
3. 你是否能根据任务结构选择合适协作模式，而不是统一用 Boss-Worker。

如果只回答：

```text
单 Agent 上下文太长
所以拆成多个 Agent
```

深度是不够的。

---

## 2. 核心结论

Multi-Agent 不是为了“让系统看起来更智能”，而是为了把一个单 Agent 难以稳定完成的任务，拆成**边界明确、可并行、可隔离、可独立验证**的执行单元。

真正适合拆 Agent 的场景通常满足至少一个条件：

```text
① 可以真实并行
② 不同子任务需要不同 Tool / 权限
③ 不同子任务需要不同 Context
④ 不同子任务需要不同模型/Prompt
⑤ 子任务可以独立验收和重试
⑥ 单 Agent 的上下文/推理深度已经开始失控
```

但如果只是“任务有五个步骤”，并不意味着必须五个 Agent。

很多时候：

```text
一个 Agent + 五个 Step
```

比：

```text
五个 Agent + 四次 Handoff
```

更稳定、更便宜。

---

## 3. 单 Agent 的真正瓶颈是什么

### 3.1 Context 污染，而不仅是 Context 太长

例如一个 Agent 同时处理：

```text
SQL 查询
设备故障分析
维修规范检索
工单生成
结果审查
```

所有信息堆进同一上下文后，问题不是单纯 token 多，而是：

- SQL Schema 干扰故障诊断；
- 工单 Tool Schema 干扰纯分析；
- Reviewer 规则和 Worker 指令混在一起；
- 不同阶段的临时假设容易互相污染。

所以 Multi-Agent 的价值之一是 **Context Isolation**。

### 3.2 Tool 权限过大

单 Agent 如果为了完成全部任务，拿到：

```text
query_db
read_doc
restart_device
create_work_order
refund
send_message
```

那么模型一次错误判断就可能触发高风险 Tool。

拆成多个执行角色后可以做到：

```text
SQL Worker      → query_db
Diagnosis Worker→ read_doc / query_history
Reviewer        → read-only
Action Worker   → create_work_order
```

所以 Multi-Agent 也可以理解为 **Capability Isolation**。

### 3.3 推理链过长

单 Agent 长任务容易出现：

```text
目标漂移
重复 Tool
中间结论丢失
前后约束不一致
失败后不知道从哪里恢复
```

长任务如果拆成：

```text
Plan
  ↓
Step / Artifact
  ↓
Review
```

就能显式管理任务进度，而不是完全依赖模型“记住自己做到哪”。

---

## 4. 常见 Multi-Agent 协作模式

截图里的 Boss-Worker、Pipeline、Joint Discussion 是正确的入门分类，但生产系统里还应该继续细分。

### 模式一：Supervisor / Boss-Worker

```text
              Supervisor
          ┌──────┼──────┐
          ↓      ↓      ↓
       Worker A Worker B Worker C
          └──────┼──────┘
                 ↓
              Aggregate
```

适合：

- 可以拆成多个相对独立子任务；
- Supervisor 能判断怎么拆；
- Worker 的输入输出有明确契约。

例如城市照明：

```text
Supervisor
  ├─ 能耗 Worker
  ├─ 告警 Worker
  └─ 历史案例 Worker
          ↓
Reviewer 汇总原因
```

问题在于：Supervisor 不能成为“超级 Agent”。如果所有 Tool、所有状态、所有权限都给 Supervisor，那么只是把单 Agent 问题换了个名字。

---

### 模式二：Pipeline / Sequential

```text
Agent A
  ↓ Artifact A
Agent B
  ↓ Artifact B
Agent C
```

适合前后依赖非常明确的任务，例如 Code Agent：

```text
需求理解
   ↓
代码修改
   ↓
测试生成
   ↓
Code Review
   ↓
修复
```

关键点不是“把自然语言输出直接传给下一个 Agent”，而是使用结构化 Artifact：

```json
{
  "artifact_id": "patch-17",
  "type": "git_patch",
  "producer": "coder",
  "commit": "...",
  "tests": ["..."],
  "evidence": ["..."],
  "version": 3
}
```

这样 Reviewer 才是在审核真实产物，而不是审核另一个模型的总结。

---

### 模式三：Planner / Worker / Reviewer

这是企业 Agent 非常常见的结构：

```text
Planner
   ↓ Plan
Worker(s)
   ↓ Artifact
Reviewer
   ├─ ACCEPT
   ├─ REVISE
   └─ ESCALATE
```

三者职责必须分开：

```text
Planner
→ 决定做什么
→ 不应该直接拥有全部副作用 Tool

Worker
→ 执行当前 Step
→ 只拿完成 Step 所需的最小 Tool 集

Reviewer
→ 检查证据、约束、完成条件
→ 默认不应拥有写操作 Tool
```

这里最重要的一句话是：

> **角色不是 Prompt 里的名字，角色必须体现在 Tool View、State Write Permission 和 Runtime Policy 上。**

---

### 模式四：Fan-out / Fan-in

```text
                Router
         ┌────────┼────────┐
         ↓        ↓        ↓
      Worker A Worker B Worker C
         └────────┼────────┘
                  ↓
               Reducer
```

适合：

- 多来源搜索；
- 多数据库查询；
- 多个候选方案并行生成；
- 多专业角色并行分析。

真正的工程问题是 Fan-in：

```text
谁负责合并？
结果冲突怎么办？
一个 Worker timeout 怎么办？
哪些结果 required？
哪些 optional？
```

所以 Worker 结果至少需要：

```text
step_id
plan_version
status
artifact_id
evidence
confidence / quality
error_type
```

---

### 模式五：Handoff / Router-based Delegation

```text
Router
 ├─ Finance Agent
 ├─ Travel Agent
 └─ Coding Agent
```

这和 Boss-Worker 不完全一样。

Boss-Worker 常常是一个任务被拆开执行；Handoff 更像：

> “这个任务应该由哪个专业 Agent 接管？”

Handoff 最大风险是：

```text
A → B → C → A
```

所以需要限制可转移图、handoff depth 和 owner。

---

### 模式六：Debate / Joint Discussion

截图里提到“民主协作”，它可以用，但不应该是默认模式。

更适合：

- 高价值判断；
- 多个答案都可能合理；
- 单一模型容易有 blind spot；
- 有独立 Judge / Verifier。

例如：

```text
Candidate Agent A
Candidate Agent B
Candidate Agent C
        ↓
     Judge
```

但生产上不建议让 Agent 无限自由讨论，因为成本会快速膨胀，而且多模型互相说服并不等于事实更正确。

更实际的实现是：

```text
有限候选 N
+ 固定轮次
+ 独立 Evidence
+ Judge Rubric
```

---

## 5. 什么时候不要拆 Multi-Agent

如果任务：

```text
只有 1~2 个 Tool
Context 很小
没有独立权限域
没有并行价值
子任务无法独立验收
```

那么拆 Agent 通常是负收益。

因为 Multi-Agent 的成本不是只有 Token：

```text
LLM Call 数 ↑
Handoff ↑
State Sync ↑
Trace 难度 ↑
Failure Surface ↑
权限管理复杂度 ↑
延迟 ↑
```

面试里可以直接说：

> 我把 Multi-Agent 当分布式系统问题，而不是 Prompt 技巧。只有当并行、隔离、专业化或独立验证带来的收益大于协作成本时才拆。

---

## 6. nanobot 当前怎么体现 Multi-Agent

当前 nanobot 源码中已经有真实 `SubagentManager`，不是抽象概念。

当前实现可以看到：

```text
SubagentManager
  ├─ task_id
  ├─ SubagentStatus
  ├─ phase / iteration / tool_events / usage
  ├─ _running_tasks
  ├─ session → task 映射
  ├─ max_concurrent_subagents
  └─ asyncio.Semaphore
```

执行链大致是：

```text
Main Agent
   ↓ spawn / run_inline
SubagentManager
   ↓
Concurrency Semaphore
   ↓
构造独立 ToolRegistry
   ↓
绑定 WorkspaceScope
   ↓
AgentRunner
   ↓
Subagent Result
```

这说明 nanobot 已经具备**受控并发的后台/inline Worker**。

但要注意边界：

nanobot 现在的 `SubagentManager` 并不等于完整的：

```text
Planner DAG
Shared Artifact Store
plan_version state machine
Reviewer workflow
跨 Agent 事务
```

这些仍然更适合由上层 Orchestrator / AgentDock 平台补齐。

---

## 7. AgentDock 怎么看 Multi-Agent

AgentDock 更适合站在 **Control Plane** 视角处理多个 Agent 实例。

当前 AgentDock 已经有：

```text
多实例 Agent Container
Driver Registry
Task / Event Stream
Workflow
Workspace / Tenant
Persistent Workspace
资源限制
暂停 / 恢复 / 取消
```

因此如果做真正平台级 MAS，可以设计成：

```text
Workflow Run
     ↓
Step A → Agent 1 / nanobot
Step B → Agent 2 / API Driver
Step C → Agent 3 / Code Agent
     ↓
Artifact / Event
     ↓
Final Reducer
```

这里 AgentDock 负责：

- 哪个 Agent 实例执行；
- 资源和租户边界；
- Task 生命周期；
- 跨 Agent Workflow；
- 事件和产物汇总。

nanobot/Pi 负责各自 Runtime 内部的一次 Agent 执行。

这就是：

```text
Control Plane
!=
Agent Runtime
```

---

## 8. Pi 和 OpenViking 在 MAS 中分别负责什么

### Pi

Pi 更适合解释 durable execution：

```text
Session
Branch
Agent Lane
Operation
Effect / Settlement
Recovery
```

在 MAS 里，这种思想很重要，因为多个执行单元不能只共享一份 mutable conversation。

更合理的是：

```text
Shared durable state
      +
Independent execution lane
```

### OpenViking

OpenViking 可以作为多个 Agent 的共享 Context/Knowledge substrate，例如：

```text
Resource
Memory
Skill
L0 / L1 / L2
```

但要明确：

```text
共享 Knowledge
!=
共享 Workflow State
```

OpenViking 可以让多个 Worker 查同一份知识和记忆，但 `plan_version`、`step_status`、`task_owner`、支付状态不能交给 Context DB 来管理。

---

## 9. 1～2 分钟口述版

> 我不会因为任务复杂就直接拆 Multi-Agent。只有当子任务可以并行、需要不同 Tool 权限或 Context、需要不同模型，或者可以独立验收和重试时，我才会拆。常见模式包括 Supervisor-Worker、Pipeline、Planner-Worker-Reviewer、Fan-out/Fan-in、Handoff 和有限 Debate。真正难点不是角色 Prompt，而是共享状态、Artifact、权限和失败处理。比如 nanobot 现在已经有 SubagentManager、并发 Semaphore、独立 ToolRegistry 和 SubagentStatus，但它本身不是完整 Planner DAG；AgentDock 更适合做多 Agent 实例和 Workflow 的 Control Plane，Pi 可以提供 durable lane/operation 的设计参考，OpenViking 更适合作为共享 Context/Memory，而不是 Workflow State。

---

# Q5：Multi-Agent 系统中如何解决“无限循环”和“通信冗余”？

## 1. 面试官真正考什么

这道题真正考的是：

> 你是否把 Multi-Agent 当成一个有预算、有状态、有终止条件的分布式执行系统。

截图里的：

```text
最大迭代次数
摘要压缩
Definition of Done
```

都对，但还不够。

生产系统必须同时处理：

```text
控制流循环
Handoff 循环
相同状态无进展循环
Tool 重复调用
消息重复
旧结果迟到
Token 爆炸
并发 Agent 互相覆盖状态
```

---

## 2. 首先区分四种“循环”

### 2.1 正常业务循环

例如：

```text
Worker → Reviewer
          ↓ REVISE
Worker → Reviewer
```

这是允许的，但必须有限：

```text
max_revision = 2
```

### 2.2 Handoff 环

```text
Agent A → Agent B → Agent C → Agent A
```

通常是角色边界不清或没有 owner。

### 2.3 No-progress Loop

例如：

```text
Agent 第 1 轮：query_device(1001)
Agent 第 2 轮：query_device(1001)
Agent 第 3 轮：query_device(1001)
```

虽然路径没有形成 A→B→A，但状态没有进展。

### 2.4 Retry Storm

```text
Worker timeout
 ↓
Supervisor retry
 ↓
Worker 自己 retry
 ↓
HTTP Client retry
 ↓
Gateway retry
```

一层超时可能被放大成几十次真实调用。

所以不能只靠 `max_iterations`。

---

## 3. 正确的终止体系：Hard Stop + Semantic Stop

### Hard Stop

Runtime 必须有硬预算：

```text
max_iterations
max_handoffs
max_subagent_depth
max_tool_calls
max_replans
max_tokens
max_cost
global_deadline
```

这些属于 Harness，不由模型自行决定。

### Semantic Stop

还要定义任务是否真的完成：

```json
{
  "goal": "找出异常原因并给出建议",
  "required_artifacts": [
    "energy_analysis",
    "alarm_correlation"
  ],
  "forbidden_actions": [
    "create_work_order"
  ],
  "acceptance": {
    "evidence_required": true,
    "unresolved_required_steps": 0
  }
}
```

这比 Prompt 里写一句“完成后停止”可靠得多。

---

## 4. No-progress Detection 是防循环的关键

每轮结束后生成一个状态指纹：

```text
fingerprint = hash(
  current_goal,
  plan_version,
  completed_steps,
  unresolved_steps,
  tool_call_name,
  normalized_args,
  key_artifact_hashes
)
```

如果连续多轮：

```text
fingerprint 不变
```

或者：

```text
same tool + same args + same result
```

就说明没有取得新信息。

Runtime 应该触发：

```text
NO_PROGRESS
  ↓
STOP / REPLAN / ASK_USER / ESCALATE
```

而不是继续让 LLM“再想一次”。

---

## 5. Handoff Loop 怎么防

建议维护明确的 Handoff Graph：

```text
Router
  ↓
Planner
  ↓
Worker
  ↓
Reviewer
```

只允许：

```text
Reviewer → Planner : NEED_REPLAN
Reviewer → Worker  : REVISE
```

而不是任意：

```text
Any Agent → Any Agent
```

状态字段至少包括：

```text
task_owner
handoff_from
handoff_to
handoff_count
max_handoff_count
visited_roles
reason
```

例如：

```text
if handoff_count > 5:
    status = ESCALATE
```

如果出现：

```text
A → B → A
```

而没有新的 Artifact / Evidence，就直接识别为循环。

---

## 6. 通信冗余为什么发生

最常见错误是：

> 每个 Agent 都把完整历史复制给下一个 Agent。

假设：

```text
5 个 Agent
× 20k Token 上下文
× 多轮 Handoff
```

成本会很快放大。

而且全量历史还有两个副作用：

- 角色污染；
- 敏感信息传播范围扩大。

---

## 7. 不要“Agent 互相聊天”，优先传结构化 Artifact

推荐：

```text
Agent A
  ↓
Artifact Store
  ↓ artifact_id
Agent B
```

Handoff Contract：

```json
{
  "task_id": "t-91",
  "plan_version": 5,
  "goal": "分析报警与能耗相关性",
  "constraints": {
    "project_id": "p-11",
    "no_side_effect": true
  },
  "input_artifacts": [
    "artifact://energy/78",
    "artifact://alarm/33"
  ],
  "evidence_refs": [
    "tool://query-energy/1",
    "tool://query-alarm/2"
  ],
  "allowed_tools": [
    "query_alarm_history"
  ],
  "deadline": "..."
}
```

这样 Agent B 不需要知道 Agent A 之前完整说了什么，只需要知道：

```text
我要做什么
输入是什么
约束是什么
证据在哪里
能用什么 Tool
什么时候必须结束
```

---

## 8. 摘要不是万能压缩方案

截图提到 Token 控制时对 Agent 间对话做摘要，这个方向没问题，但要注意：

```text
Summary != State
Summary != Evidence
```

例如：

```text
Summary：设备大概率离线
```

这不能替代：

```json
{
  "device_id": "D1001",
  "last_seen": "2026-09-11T03:18:00+08:00",
  "alarm_code": "COMM_LOST",
  "source": "tool_call_88"
}
```

所以正确做法应该是：

```text
结构化 State
+ Artifact / Evidence
+ 必要 Summary
```

而不是只剩 Summary。

---

## 9. 并发结果晚到怎么处理

Multi-Agent 中非常常见：

```text
Plan v7
  ↓
Worker A / B / C 开始
  ↓
用户修改目标
  ↓
Plan v8
  ↓
Worker B(v7) 晚到
```

如果没有版本控制，旧结果会污染新任务。

因此结果必须携带：

```text
plan_id
plan_version
step_id
attempt_id
artifact_version
```

提交时：

```text
if result.plan_version != current_plan.version:
    mark STALE
    do not mutate current state
```

这其实也是防“隐性循环”的一部分，因为旧结果不能重新激活已经作废的执行路径。

---

## 10. 消息重复和幂等

在跨进程/跨容器 MAS 中，消息可能：

```text
重复投递
延迟投递
乱序投递
```

所以状态提交最好使用：

```text
message_id
step_id
attempt_id
result_hash
idempotency_key
```

例如：

```text
UNIQUE(step_id, attempt_id, result_hash)
```

或保存 processed message id。

不要假设“发一次就收一次”。

---

## 11. nanobot 当前有哪些防失控机制

当前 `SubagentManager` 明确有：

```text
max_iterations
max_concurrent_subagents
asyncio.Semaphore
SubagentStatus.phase
iteration
tool_events
usage
stop_reason
```

这意味着 nanobot 已经在 Runtime 层限制：

- 单个 Subagent 最大循环轮次；
- 并发 Subagent 数量；
- 可观察运行阶段和停止原因。

这是防止无限 spawn / 无限执行的重要基础。

但它不是完整 MAS Orchestrator，所以类似：

```text
全局 handoff graph
plan_version
跨 Agent no-progress fingerprint
跨容器 message dedup
```

仍需要平台层补。

---

## 12. AgentDock 如何进一步治理

AgentDock 当前已经有：

```text
Task
Event Stream
Workflow
Container Lifecycle
cancel
pause / resume
Driver
resource limits
```

所以平台层可以进一步做：

```text
WorkflowRun
 ├─ max_steps
 ├─ deadline
 ├─ max_agent_handoffs
 ├─ max_cost
 ├─ current_owner
 └─ terminal_status
```

并在 Task/Event 层做：

```text
duplicate event detection
stale result detection
retry policy
cancel propagation
```

注意：AgentDock 的 Workflow/Task 状态依然不能替代真正业务系统的订单/退款/设备状态。

---

## 13. Pi 能补充的 durable 思路

Pi Harness 很适合解释为什么 MAS 不应该只依赖内存里的“Agent 正在讨论”。

长任务需要 durable：

```text
operation state
intent
external effect
settlement
abort/recovery
```

如果 Worker 执行一个副作用动作后进程崩溃：

```text
没有 durable intent
→ 不知道是否已经发起

没有 settlement
→ 不知道是否确认完成
```

这比“最大循环次数”更深一层：

> 防失控不仅是让 Agent 停下来，还要保证停下来以后系统知道自己处于什么状态。

---

## 14. 一个城市照明实际例子

用户：

> “分析昨晚所有离线灯杆，找出可能是网关故障的区域。”

Planner：

```text
S1 查询离线设备
S2 按网关聚合
S3 查询通信告警
S4 历史案例匹配
S5 Reviewer 判断
```

如果 S2 和 S3 互相重复请求相同区域：

```text
query_gateway(G-11)
query_gateway(G-11)
query_gateway(G-11)
```

Runtime 通过 `(tool_name + normalized_args + result_hash)` 判断没有新信息：

```text
NO_PROGRESS
```

然后不是继续 Tool Loop，而是：

```text
Replan
or
Finalize with uncertainty
or
Ask user
```

如果 Reviewer 连续两次返回 `REVISE`：

```text
revision_count == max_revision
```

则：

```text
ESCALATE / FINAL_WITH_LIMITATION
```

而不是无限：

```text
Worker ↔ Reviewer ↔ Worker ↔ Reviewer
```

---

## 15. 推荐状态机

```text
CREATED
   ↓
PLANNING
   ↓
RUNNING
   ├─ WAITING_SUBAGENTS
   ├─ WAITING_USER
   ├─ REPLANNING
   └─ REVIEWING
        ↓
   ┌────┼─────────────┐
   ↓    ↓             ↓
SUCCESS PARTIAL     ESCALATED
                    
异常路径：
TIMEOUT / CANCELLED / FAILED / UNKNOWN
```

终止必须是 Runtime 可以明确判断的状态，而不是“模型觉得聊完了”。

---

## 16. 1～2 分钟口述版

> Multi-Agent 防无限循环不能只靠 max iteration。我会同时做 Hard Budget 和 Semantic Stop：限制 iteration、handoff、tool call、replan、token、cost 和 global deadline；同时用 Definition of Done 判断 required artifact 是否齐全。对于 A→B→A 这种 Handoff 环，要维护 task owner、allowlist graph 和 handoff_count；对于一直调相同 Tool 的情况，用 state fingerprint / tool+args+result 做 no-progress detection。Agent 间也不应该传完整历史，而应该传结构化 State、Artifact 和 Evidence。nanobot 当前已经有 SubagentManager、max_iterations、并发 Semaphore、phase/usage/stop_reason 等 Runtime 控制；更上层的 plan version、handoff graph、跨容器消息幂等可以放到 AgentDock；Pi 的 durable operation/effect 思路可以解决“系统停了以后状态到底是什么”的问题。

---

# 与现有主章节的关系

本文件是“截图高频问法”的专项补充，不新增重复核心编号：

```text
Q4 单 Agent 瓶颈 / MAS 协作模式
  → 02-05 Router/Planner/Worker/Reviewer
  → 02-09 什么时候拆 Subagent
  → 02-12 Multi-Agent 编排模式

Q5 无限循环 / 通信冗余
  → 02-10 Handoff Contract
  → 02-11 Handoff / Dead Loop
  → 02-14 Agent 间通信方式
```

继续深入时优先阅读：

- `02-planning-routing-multi-agent/deep-complete.md`
- `02-planning-routing-multi-agent/multi-agent-state-sharing-deep-dive.md`
- `04-reliability-security/tool-failure-idempotency-deep-dive.md`
- `07-harness-eval-trace/harness-runtime-comparison-deep-dive.md`
