# ReAct、Plan-and-Execute、DAG：不要把三种控制流当成“框架名”

## 面试题

> Agent 编排到底应该选 ReAct、Plan-and-Execute 还是 DAG Workflow？长任务为什么经常要混合？

---

## 1. 面试官真正考什么

这道题不是让你背三个定义，而是在考你有没有理解 **Agent 的自由度到底应该放在哪一层**。

三个模式真正的差异不是“谁更先进”，而是：

```text
ReAct              每一步都允许模型根据最新 observation 决策
Plan-and-Execute   先形成显式计划，再围绕计划执行和局部重规划
DAG/Workflow       控制流主要由代码/状态机确定，模型只能在节点内发挥
```

所以选择的本质是：

```text
开放性 ↑  →  ReAct
可控性 ↑  →  Plan-and-Execute
确定性/审计 ↑ → DAG/Workflow
```

---

## 2. ReAct 到底是什么

ReAct 的运行结构是：

```text
Observation
   ↓
LLM decides next action
   ↓
Tool Call
   ↓
Tool Result
   └────────────→ 下一轮
```

模型没有一次性承诺完整路径。每次 Tool Result 都可能改变下一步。

### 优点

- 对未知环境适应强
- Tool 失败后容易换方案
- 用户问题短、步骤少时实现简单
- 不需要维护复杂 Plan State

### 缺点

长任务会出现：

```text
目标漂移
重复调用
局部最优
看不到全局依赖
Token 成本不可预测
恢复时不知道“完成到哪一步”
```

例如用户说：

> 查北京三天行程、天气、酒店、交通，再控制预算在 3000 元以内。

纯 ReAct 可能：

```text
先查酒店
→ 又查天气
→ 查景点
→ 发现酒店太贵
→ 再查酒店
→ 又重新算交通
```

它能完成，但执行轨迹很难稳定。

---

## 3. Plan-and-Execute 不是“先让模型输出一串文字步骤”

真正工程化的 Plan 应该是结构化状态，而不是：

```text
1. 查天气
2. 查酒店
3. 查航班
```

至少应该有：

```json
{
  "plan_id": "p-1001",
  "version": 3,
  "goal": "规划北京三日行程",
  "steps": [
    {
      "step_id": "s1",
      "type": "tool_task",
      "depends_on": [],
      "status": "SUCCEEDED",
      "expected_output": "weather_artifact"
    },
    {
      "step_id": "s2",
      "depends_on": [],
      "status": "RUNNING",
      "expected_output": "hotel_candidates"
    }
  ]
}
```

### 为什么 Plan 必须结构化

因为 Runtime 要判断：

- 哪些 step 已完成
- 哪些可以并行
- 哪些失败后只需局部重试
- 用户改需求时哪些 step 作废
- 恢复时从哪继续
- Reviewer 验证的是哪个版本

这些都不能靠一段自然语言稳定实现。

---

## 4. Replan 最大的坑：路径震荡

如果每个 Tool Result 都让 Planner 重新输出一份完整 Plan，就可能出现：

```text
Plan v1: A → B → C
Tool A 返回
Plan v2: A → D → C
Tool D 返回
Plan v3: A → B → E
```

模型不断“觉得有更好的方案”，任务永远收敛不了。

### 工程上怎么防

引入 Replan Policy：

```text
只有以下事件允许 replan：
1. required step failed
2. 关键前提变化
3. 用户目标变化
4. Reviewer 判定无法满足目标
5. 新证据证明原计划不可行
```

普通成功 observation 只更新 artifact，不触发整图重规划。

还可以限制：

```text
max_replans = 2
max_plan_versions = 3
```

超过后需要降级、澄清或终止。

---

## 5. DAG 为什么适合交易型流程

比如订票：

```mermaid
graph LR
A[Search] --> B[Quote]
B --> C[Lock]
C --> D[User Confirm]
D --> E[Pay]
E --> F[Issue Ticket]
```

这里 `Pay` 不能因为模型“觉得可以”就跳过 `User Confirm`。

状态机应该硬编码：

```text
QUOTED -> LOCKED -> CONFIRMED -> PAID -> ISSUED
```

Agent 可以负责：

- 搜索候选
- 解释价格差异
- 推荐最优方案

但交易状态迁移由代码负责。

### 关键原则

> 模型可以决定“选哪个”，不能决定“哪些安全步骤可以省略”。

---

## 6. 生产里为什么经常是混合架构

真正好用的结构通常是：

```text
                 Planner
                    ↓
          结构化 Execution Plan
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
   Deterministic Node      Agentic Node
   Workflow/StateMachine   局部 ReAct
          ↓                   ↓
          └─────────┬─────────┘
                    ↓
                 Reviewer
                    ↓
             complete/replan
```

例如城市照明故障诊断：

```text
固定阶段：
获取事件 → 验证设备 → 收集证据 → 风险判断 → 生成建议

其中“收集证据”节点内部：
Agent 可以根据设备类型自由决定调用
query_alarm / query_energy / query_history / query_weather
```

外层流程稳定，内层允许模型探索。

---

## 7. 用户中途改需求，为什么需要 plan_version

假设：

```text
Plan v1：找最早航班
Worker A 正在查询
用户：不要最早，要最便宜
```

如果只是修改 Prompt，旧 Worker 仍然会返回。

所以每个 Step/Artifact 要带：

```text
plan_id
plan_version
step_id
attempt_id
```

Aggregator 收到结果：

```text
result.plan_version == current_plan_version ?
    yes → 接受
    no  → 丢弃/存为 reusable artifact
```

否则旧计划结果会污染新计划。

---

## 8. nanobot 当前到底是哪一种

nanobot 核心 `AgentRunner` 更接近 **Tool-using ReAct Loop**：模型每轮返回文本或 Tool Call，Tool Result 回注后进入下一轮。

源码的核心形态是：

```text
for iteration in range(max_iterations):
    build/request context
    call model
    if tool_calls:
        execute_tool_calls(...)
        append tool results
        continue
    else:
        final response
        break
```

它有：

- `max_iterations`
- Context Governor
- Tool Registry/Execution
- Checkpoint
- Injection/Continuation
- `concurrent_tools`

但它没有一个通用的：

```text
Plan object
Step dependency graph
plan_version
step status store
Reviewer state machine
```

所以面试时不要说“nanobot 本身就是 Plan-and-Execute/DAG Engine”。

更准确的说法是：

> nanobot 提供了 Agent Loop Runtime；如果业务需要显式长任务计划，我会在上层增加 Planner/Workflow 状态，把某些 step 委托给 nanobot 做局部 Agentic Execution。

---

## 9. Java/Spring 怎么落

可以定义：

```java
record PlanStep(
    String stepId,
    Set<String> dependsOn,
    StepType type,
    StepStatus status,
    long planVersion,
    boolean required,
    String expectedArtifact
) {}
```

状态机：

```text
PENDING → READY → RUNNING
                   ├→ SUCCEEDED
                   ├→ FAILED
                   ├→ UNKNOWN
                   └→ CANCELLED
```

Scheduler 只执行 `READY` 节点；Agentic Step 调 nanobot，Deterministic Step 调 Java Domain Service。

---

## 10. 常见错误回答

### 错误 1：复杂任务用 Plan-and-Execute，简单任务用 ReAct

方向没错，但太浅。还要解释“复杂”的本质：依赖多、执行长、需要恢复、成本可控、强副作用。

### 错误 2：DAG 不够灵活，所以全部交给 Agent

高风险交易恰恰需要 DAG 的不灵活。

### 错误 3：Planner 每轮重新规划更智能

没有 Replan Gate 会造成震荡和成本失控。

---

## 11. 1～2 分钟面试口述版

> 我不会把 ReAct、Plan-and-Execute、DAG 当成互斥框架。ReAct 适合短任务和未知环境，因为每次 Tool Result 后模型都能重新决策，但长任务会有目标漂移、重复调用和恢复困难。Plan-and-Execute 的关键不是先输出几条文字步骤，而是维护结构化 Plan、step status、depends_on 和 plan_version，只有关键失败或目标变化才触发 replan。对于支付、出票、退款这种副作用强的流程，我会用 DAG/状态机硬约束顺序，Agent 只能在允许节点里做搜索、解释和推荐。nanobot 当前更像一个带 Context、Tool、Checkpoint 的 ReAct Runtime，并不是完整 DAG Scheduler，所以企业级长任务我会让外层 Workflow 管状态，局部节点再调用 nanobot 做 Agentic Execution。
