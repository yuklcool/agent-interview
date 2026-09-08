# Multi-Agent State Sharing：Planner / Worker / Reviewer 到底共享什么

> 面试题：多个 Agent 协作时，是共享完整对话、共享 Summary，还是共享结构化状态？Planner、Worker、Reviewer 如何避免互相污染？用户中途改口时怎么 Replan？

## 1. 面试官真正考什么

这道题不是在问“多 Agent 有哪些角色”，而是在考三个核心问题：

1. **状态所有权**：谁能修改 Plan，谁只能提交 Artifact；
2. **上下文投影**：每个角色到底需要看到什么；
3. **并发一致性**：旧 Worker 晚到的结果如何避免污染新计划。

如果答案只是：

```text
Planner 拆任务
Worker 执行
Reviewer 检查
```

还远远不够。

---

## 2. 核心结论

Multi-Agent 最稳的设计不是“大家共享一份聊天记录”，而是：

```text
               Task State / Plan Store
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
     Planner          Worker          Reviewer
  修改 Plan        产出 Artifact     产出 Verdict
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                  Orchestrator
```

角色之间共享：

```text
goal
plan_version
step_id
depends_on
status
constraints
artifact_ref
evidence_ref
error_type
```

而不是共享无限增长的完整历史。

---

## 3. 为什么完整对话共享是一个坏默认值

假设有：

```text
Planner
Flight Worker
Hotel Worker
Visa Worker
Reviewer
```

如果所有角色都收到完整 Conversation：

### 问题一：Token 爆炸

N 个 Agent × M 轮历史，会把同样的信息重复发送多次。

### 问题二：角色污染

Reviewer 看到了 Planner 的“我觉得 A 方案最好”，可能产生确认偏差；Worker 看到其他 Worker 的猜测，也可能把未验证信息当事实。

### 问题三：权限扩大

如果共享完整 Tool Schema，每个 Worker 可能拿到不需要的高风险 Tool。

### 问题四：异步结果不好版本化

聊天记录天然强调时间顺序，但 Multi-Agent 真正需要的是：

```text
这个结果属于哪个 plan_version？
对应哪个 step？
依赖哪些输入？
是否已经 stale？
```

---

## 4. 推荐的数据模型

### Plan

```json
{
  "plan_id": "p-001",
  "version": 7,
  "goal": "安排上海到北京出差",
  "status": "RUNNING"
}
```

### Step

```json
{
  "step_id": "hotel-search",
  "plan_version": 7,
  "owner_role": "hotel-worker",
  "depends_on": ["resolve-date"],
  "required": false,
  "status": "RUNNING",
  "input_ref": "artifact://constraints/23",
  "output_ref": null
}
```

### Artifact

```json
{
  "artifact_id": "a-991",
  "producer": "hotel-worker",
  "plan_version": 7,
  "step_id": "hotel-search",
  "type": "hotel_candidates",
  "content_hash": "...",
  "evidence": ["tool://hotel-search/call-88"]
}
```

这里最重要的是：

> **Agent 不通过修改一大坨共享 Prompt 协作，而是通过提交带版本和证据的结构化 Artifact 协作。**

---

## 5. Planner、Worker、Reviewer 的写权限要不同

推荐：

```text
Planner
  ├─ 可创建/修改 Plan
  ├─ 可新增 Step
  └─ 不直接写业务事实

Worker
  ├─ 可 claim 自己的 Step
  ├─ 可提交 Artifact
  └─ 不允许修改其他 Step

Reviewer
  ├─ 读取 Plan + Artifact + Evidence
  ├─ 输出 PASS / FAIL / NEED_REPLAN
  └─ 不直接执行高风险业务 Tool

Orchestrator
  └─ 真正提交状态迁移
```

这是一个很典型的：

```text
LLM proposes
Runtime commits
```

模式。

---

## 6. 用户中途改口时怎么 Replan

例如：

```text
Plan v10：找最早航班
       ↓
Flight Worker 已经运行
       ↓
用户：改成最便宜
       ↓
Plan v11
```

此时不能只往聊天里追加一句“用户改要求了”。

应该做：

```text
1. 生成 v11
2. diff v10 → v11
3. 标记受影响 Step stale/cancel_requested
4. 保留可复用 Artifact
5. 新 Worker 只消费 v11 输入
6. v10 晚到结果不得覆盖 v11
```

结果提交时：

```text
if result.plan_version != current_plan.version:
    mark STALE
    do not mutate current state
```

### 注意：取消不等于结果不会回来

HTTP、MCP、LLM、数据库请求可能无法真正取消，所以系统必须接受：

```text
cancel requested
        ↓
old result still arrives
        ↓
version check
        ↓
ignore / keep as reusable artifact
```

---

## 7. nanobot 当前实现能说明什么

nanobot 当前有真实的 `SubagentManager`，它不是纸面上的“多 Agent”。当前实现里可以看到：

- background subagent task；
- `task_id`；
- `SubagentStatus`；
- phase / iteration / tool events / usage；
- `max_concurrent_subagents`；
- `asyncio.Semaphore` 做并发容量控制；
- 每个 Subagent 构建自己的 `ToolRegistry`；
- 可以绑定 workspace scope；
- Subagent 内部仍然复用 `AgentRunner`。

执行链可以理解成：

```text
Main Agent
   ↓ spawn
SubagentManager
   ↓ capacity semaphore
Subagent
   ├─ isolated tool registry
   ├─ workspace scope
   ├─ AgentRunner
   └─ status/hook
```

这说明 nanobot 已经有“后台 Worker”的真实基础。

但从这个实现不能直接推导出它已经拥有完整的：

```text
Planner DAG
plan_version
shared artifact store
Reviewer state machine
distributed multi-agent transaction
```

这些如果业务需要，应该由更上层 Orchestrator/Platform 补。

---

## 8. Pi 能补充什么视角

Pi 的 AgentHarness 规范很适合说明“共享状态不能随便多写”。

它强调 Session、Branch、AgentLane、Operation 和 durable current state，并明确讨论 writable owner。

这个思路可以映射到 Multi-Agent：

```text
共享 Session / Entry Tree
         │
         ├── Lane A
         ├── Lane B
         └── Lane C
```

与其让三个 Agent 同时直接修改一个 mutable conversation，不如让不同 Lane/Operation 拥有明确执行状态，然后通过有序的 durable mutation 形成结果。

面试里可以总结：

> 多 Agent 的核心不是并发模型调用，而是把共享事实和每个执行 Lane 的局部状态分开。

---

## 9. AgentDock 在平台层怎么用这个思想

AgentDock 更适合承载：

```text
Workspace
  ↓
多个 Agent 实例 / Driver
  ↓
Task / Workflow
  ↓
事件流 / 状态
```

如果未来一个 Workflow 使用：

```text
Research Agent
SQL Agent
Reviewer Agent
```

平台层应保存的是：

```text
workflow_run_id
step_run_id
agent_id
input artifact
output artifact
status
started_at
ended_at
```

而不是让三个容器共享同一个可写聊天 JSON 文件。

容器隔离和 Control Plane 恰好使“Agent 之间用 Artifact/Event 通信”比“共享进程内对象”更自然。

---

## 10. OpenViking 在 Multi-Agent 里应该共享什么

OpenViking 可以成为共享的**Context/Knowledge substrate**：

```text
viking://resources/...
viking://user/{id}/memories/...
viking://user/{id}/skills/...
```

多个 Agent 可以检索相同资源，但要注意：

```text
共享 Knowledge
!=
共享 mutable execution state
```

### 适合放 OpenViking 的：

- 项目文档
- 用户偏好
- 历史经验
- Skill
- 长期知识

### 不适合拿 Context DB 代替的：

- 当前 plan_version
- step lock
- payment state
- Tool execution status
- workflow transaction

这些仍然属于 Runtime/Workflow State Store。

---

## 11. 场景：城市照明故障诊断 Multi-Agent

用户问：

> “昨晚海八路为什么出现 49 盏能耗异常？分析后给我建议，但不要自动派单。”

可以拆成：

```text
Planner
  ↓
Plan v3
  ├─ S1 能耗数据查询 → SQL Worker
  ├─ S2 报警关联分析 → Alarm Worker
  ├─ S3 历史处置经验 → Context Worker(OpenViking)
  └─ S4 综合判断 → Reviewer
```

共享状态：

```text
Goal:
  找出异常原因

Constraint:
  禁止自动创建工单

Artifacts:
  S1 → energy_anomaly.json
  S2 → alarms.json
  S3 → historical_cases.md
```

Reviewer 看到的是：

```text
Plan
+ 三个 Artifact
+ Evidence
+ Constraint
```

而不必读取三个 Worker 的完整 Thought/对话历史。

最后如果 Reviewer 想调用 `create_work_order`：

```text
Tool Policy
  ↓
当前 constraint = no-side-effect
  ↓
DENY
```

这体现了：

> 多 Agent 共享 Context，不代表共享权限。

---

## 12. 一致性怎么做

### 单进程版

可以：

```text
Actor per plan
        ↓
一个队列串行修改 Plan State
```

Worker 结果通过消息回 Actor。

### 分布式版

可以使用：

```text
plan.version
CAS / optimistic lock
step lease
idempotent result commit
```

SQL 示例：

```sql
UPDATE plan
SET version = version + 1,
    state = :new_state
WHERE id = :id
  AND version = :expected_version;
```

受影响行数为 0：

```text
说明状态已经被别人修改
→ reload
→ 判断结果是否 stale
```

不要只说“加 Redis 分布式锁”。

锁只能控制临界区，不能自动解决：

- 迟到结果；
- 外部副作用；
- 网络重试；
- 进程崩溃后的 lease；
- plan version 演进。

---

## 13. 失败模式

### 失败一：所有 Agent 共享全部历史

结果：成本高、角色污染、权限面扩大。

### 失败二：Planner 可以直接执行所有业务 Tool

结果：Planner 从“计划者”变成了超级用户。

### 失败三：Artifact 没有 Evidence

Reviewer 只能相信 Worker 的自然语言总结，无法定位真实 Tool Result。

### 失败四：没有 plan_version

用户改需求后，旧 Worker 仍可能覆盖新状态。

### 失败五：把 Context DB 当 Workflow DB

长期记忆适合可检索知识，不适合充当当前事务状态。

---

## 14. 常见追问

### Q1：Worker 之间需要直接聊天吗？

默认不建议。优先通过结构化 Artifact/State 通信；只有真正需要协商的开放任务才增加 Agent-to-Agent 消息。

### Q2：Reviewer 要不要看到 Planner 的原始推理？

一般只给目标、约束、Plan、Artifact、Evidence。减少 confirmation bias。

### Q3：多个 Worker 修改同一 Artifact 怎么办？

不要共享 mutable document。使用 immutable artifact + new version，最后由 owner 合并。

### Q4：Subagent 越多效果是不是越好？

不是。多 Agent 增加模型成本、上下文传递、失败面和调度复杂度。只有存在并行性、专业工具隔离或独立验证价值时才拆。

---

## 15. 1～2 分钟口述版

> 我不会让多个 Agent 共享一整份可写聊天历史，而会把协作建立在结构化 Task State 和 Artifact 上。Planner 拥有 Plan，Worker 只执行分配给自己的 Step 并产出带 plan_version、step_id、evidence 的 Artifact，Reviewer 读取 Plan 和 Artifact 后给 Verdict，真正状态迁移由 Orchestrator 提交。用户中途改目标时生成新 plan_version，旧 Worker 即使结果晚到也不能覆盖当前状态。nanobot 的 SubagentManager 已经有 background task、并发 semaphore、独立 ToolRegistry 和运行状态，但它不是完整 DAG Planner；Pi Harness 的 Lane/Operation 模型可以帮助理解多执行单元的 durable state；AgentDock 适合做跨 Agent/容器的 Workflow 和 Artifact 管理；OpenViking适合共享长期 Knowledge/Memory，但不代替当前 Workflow State。

## 项目落点

- nanobot：`nanobot/agent/subagent.py`
- Pi：`packages/agent/docs/harness.md`
- AgentDock：Task / Workflow / Agent container / Driver 架构
- OpenViking：`viking://resources`、`memories`、`skills`
