# Harness 到底是什么：Pi、nanobot、AgentDock、OpenViking 四个项目怎么对照

> 面试题：什么是 Agent Harness？它和 Agent Runtime、Workflow、Control Plane、Context Engineering 有什么区别？为什么现在越来越多项目强调 Harness，而不是只强调 Prompt？

## 1. 面试官真正考什么

如果回答：

> “Harness 就是 Agent 外面的一层工程封装。”

定义没错，但没什么信息量。

真正要回答的是：

- 模型输出不确定，系统怎么把它约束成可靠执行；
- Context 超限在哪里处理；
- Tool 失败和副作用如何收敛；
- Run 如何停止、恢复、取消；
- Trace/Eval 如何插入执行链；
- 多模型、多 Tool、多 Session 的状态谁维护；
- 哪些属于 Runtime，哪些属于平台和业务系统。

---

## 2. 核心结论

我把 Harness 理解成：

> **模型周围那套负责“准备输入、约束动作、维护状态、执行 Tool、处理失败、控制预算、提供恢复和可观测性”的运行保障系统。**

可以画成：

```text
                  Harness / Runtime
┌──────────────────────────────────────────────┐
│ Context Build / Compact / Memory Projection  │
│ Model Invocation / Retry / Timeout           │
│ Tool Registry / Validation / Policy          │
│ Loop / Stop / Budget                         │
│ Checkpoint / Recovery / Cancellation         │
│ Hooks / Events / Trace / Eval                │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
                   LLM
```

但 Harness 不是全部系统。

```text
Control Plane   → 管 agent/container/tenant/task
Context DB      → 管长期 memory/resource/skill
Business System → 管订单、设备、退款等事实
Harness         → 管模型一次/多次执行如何安全运行
```

---

## 3. Prompt Engineering、Context Engineering、Harness Engineering 的区别

### Prompt Engineering

重点是：

```text
怎么写 instruction
怎么给 example
怎么表达角色/格式
```

### Context Engineering

重点变成：

```text
模型这一轮到底看到什么
System
History
Summary
Memory
RAG
Tool Schema
Artifacts
```

### Harness Engineering

再向外一层：

```text
什么时候调用模型
调用哪个模型
最多几轮
Tool 怎么执行
失败怎么办
副作用怎么办
超时怎么办
怎么恢复
怎么 trace
怎么 eval
```

所以生产 Agent 的质量不只由 Prompt 决定。

---

## 4. nanobot：一个轻量、可读的 Runtime/Harness 案例

nanobot 当前源码可以直接看到 Harness 的很多组成部分。

### 4.1 `AgentRunSpec`

一次 Run 需要的配置不是只有 model：

```text
initial_messages / transcript_input
tools
runtime
max_iterations
max_tool_result_chars
concurrent_tools
session_key
provider_retry_mode
checkpoint_callback
injection_callback
llm_timeout_s
continuation_callback
provider_state
events
```

这已经体现：

> Agent Run 是一个受预算、状态、Tool、Context 和生命周期约束的运行单元。

### 4.2 `AgentRunner`

负责：

```text
iteration loop
context request construction
LLM call
Tool execution
observation
stop/finalize
checkpoint
injection
hook
```

### 4.3 Tool Execution

`execute_tool_calls()` 不只是函数调用，还处理：

```text
parallel safe batches
prepare_call
Tool error → observation
SSRF/workspace violation
repeated lookup guard
Hook lifecycle
```

### 4.4 Recovery

nanobot 对：

```text
awaiting_tools
tools_completed
final_response
```

保存 runtime checkpoint。

对于 uncertain pending tool，不在恢复时偷偷 replay，而是显式生成 interrupted Tool Result。

这就是典型 Harness 思维：

> 模型可能想继续，但 Runtime 先保证状态不会因为重启而隐式重复副作用。

---

## 5. Pi：为什么它的 Harness 更像 durable state machine

Pi 当前不仅有 `pi-agent-core`，还有更重的 AgentHarness 设计。

它的规范里出现：

```text
Session
immutable entry tree
Branch
AgentLane
Operation
operation metadata
operation current state
usage ledger
intent
settlement
recovery
abort
```

这和简单 Agent Loop 最大的区别是：

> **它把执行位置做成 durable explicit state，而不是从消息列表推断。**

---

## 6. Pi 的 intent → effect → settlement 为什么重要

外部调用最麻烦的窗口是：

```text
本地发出请求
      ↓
外部真的执行
      ↓
本地还没来得及持久化结果
      ↓
进程崩溃
```

此时本地不知道外部到底成功没成功。

Pi Harness 的思路是：

```text
TX: persist intent
      ↓
external effect
      ↓
TX: settle outcome
```

如果死在中间：

```text
state = effect_pending
```

再结合 Tool 的 replay policy：

```text
safe → 可以重放
never → 不重放，合成 interrupted outcome / reconcile
```

这个设计和支付系统的幂等/事务思想非常接近。

面试官如果追问“Exactly Once 怎么做”，正确回答不是保证网络世界 exactly once，而是：

```text
persistent intent
+ idempotency
+ status reconciliation
+ effect-specific replay policy
```

---

## 7. nanobot 和 Pi 不是谁替代谁

可以粗略理解：

```text
nanobot
优势：轻量、直接、Agent Loop 代码清晰、WebUI/Tool/Context/Recovery 实用

Pi Harness
优势：对 durable session/operation/effect/recovery 建模更系统、更重
```

面试时不要说：

> “Pi 比 nanobot 高级。”

而应该说：

> 两者的工程目标和复杂度预算不同。轻量个人/单实例 Agent 和长生命周期、强恢复 Agent 对 durable Harness 的要求不同。

---

## 8. AgentDock 为什么不应该被叫成 Harness 本身

AgentDock 更接近 Harness 外面的 Control Plane / Agent Platform。

它当前负责：

```text
multi-tenant workspace
agent instance
Docker provision
Driver registry
Task
SSE/WebSocket event
persistent workspace
snapshot
quota
credential
MCP/Skill assignment
workflow/schedule
```

而实际运行一个 Agent Tool Loop 的可能是：

```text
Nanobot driver
Vanilla driver
Codex
OpenCode
Claude Code
```

因此：

```text
AgentDock = platform/runtime host
Driver     = execution engine
Harness    = driver/runtime 内部或旁路的执行保障机制
```

这个区分很重要。

---

## 9. OpenViking 为什么也不是 Harness

OpenViking 是 Context Database。

它解决：

```text
Memory
Resource
Skill
Context hierarchy
L0/L1/L2
recursive retrieval
retrieval trajectory
session → long-term memory
```

这些可以被 Harness 调用，但不是 Harness 本身。

例如：

```text
Harness Before Model Call
     ↓
query OpenViking
     ↓
selected context
     ↓
ContextGovernor
     ↓
LLM
```

所以更合理关系是：

```text
OpenViking plugs into Context phase of Harness
```

---

## 10. 把四个项目组合成一个企业 Agent 架构

```text
                       Web / API
                           │
                           ▼
                    AgentDock
              Auth / Tenant / Agent / Task
                           │
                    select Driver
               ┌───────────┴───────────┐
               ▼                       ▼
            nanobot                    Pi
         lightweight loop        durable harness
               │                       │
               └───────────┬───────────┘
                           │ before model
                           ▼
                      OpenViking
            Memory / Resource / Skill recall
                           │
                           ▼
                         LLM
                           │
                        Tool Call
                           │
                    Runtime Policy
                           │
                           ▼
                  Java Business Service
                           │
                   PostgreSQL / APIs
```

这张图在系统设计面试里非常实用，因为它说明：

- 平台不是模型；
- Context DB 不是 Runtime；
- Runtime 不是业务系统；
- Tool Call 不是业务事实。

---

## 11. 一个 Harness 最低应该包含什么

我会分为九个模块：

```text
1. Run Lifecycle
2. Context Governance
3. Model Runtime
4. Tool Runtime
5. Policy / Security Boundary
6. Budget / Timeout / Retry
7. Checkpoint / Recovery
8. Event / Hook / Trace
9. Eval / Replay hooks
```

### 11.1 Run Lifecycle

至少：

```text
run_id
turn_id
iteration
status
started_at
deadline
stop_reason
```

### 11.2 Context Governance

```text
transcript
summary
memory
retrieval
tool schema
artifact
budget
```

### 11.3 Tool Runtime

```text
schema validation
permission
execution
error normalization
idempotency metadata
side-effect classification
```

### 11.4 Recovery

必须回答：

```text
如果 crash 在 LLM 前？
LLM streaming 中？
Tool 前？
Tool effect 中？
Tool 完成但结果没落库？
Final streaming 中？
```

不同窗口策略不同。

---

## 12. Harness 的状态机示例

```text
ACCEPTED
   ↓
CONTEXT_READY
   ↓
MODEL_PENDING
   ↓
MODEL_COMPLETED
   ├─ FINAL → COMPLETED
   │
   └─ TOOL_CALLS
        ↓
     TOOL_INTENT
        ↓
     TOOL_EFFECT_PENDING
        ↓
   ┌────┼───────────┐
   ▼    ▼           ▼
DONE  ERROR       UNKNOWN
   │    │           │
   └────┴─────┬─────┘
              ↓
         OBSERVATION_READY
              ↓
          NEXT ITERATION
```

状态不是为了画图，而是为了明确：

```text
每个 crash 点恢复后应该去哪里？
```

---

## 13. Trace 为什么是 Harness 的组成部分

Agent 错误经常不能从最终答案判断。

例如答案错，可能是：

```text
Router route wrong model
Planner missed step
Retriever missed doc
Tool wrong args
Tool returned stale data
Context compaction dropped constraint
Reviewer failed
```

因此 Trace 要对应运行层次：

```text
run
 └─ turn
    ├─ context.build
    ├─ retrieval
    ├─ llm.round
    ├─ tool.call
    │   └─ downstream http/sql
    └─ finalization
```

字段至少：

```text
trace_id
run_id
turn_id
iteration
plan_version
step_id
tool_call_id
model
prompt_version
context_version
```

---

## 14. AgentHook / Event 为什么重要

nanobot 当前有 Hook 生命周期，例如 Tool 执行前后和 Run 前后。

这类 Hook 可以用来实现：

```text
Tracing
Audit
Metrics
Eval capture
Policy checks（需谨慎定义 owner）
Debug timeline
```

AgentDock 的 Task event stream 则更适合平台层展示：

```text
assistant message
tool call
tool result
file change
token/iteration/progress
```

OpenViking retrieval trajectory 则补充：

```text
Context 为什么被召回
```

把三种观察面结合，才有完整故障定位能力。

---

## 15. Eval 为什么不能只测最终回答

Harness 变化可能让最终答案偶尔看起来一样，但轨迹变差。

例如新模型：

```text
最终 answer 正确
但调用了 8 次 Tool
旧模型只调用 2 次
```

或者：

```text
答案正确
但先错误执行 side-effect Tool，再补救
```

所以要测：

```text
Outcome
+
Trajectory
+
Safety
+
Cost/Latency
```

Golden Case 应包含：

```text
initial state
input
allowed tools
expected outcome
forbidden actions
trajectory constraints
```

---

## 16. Harness 和 Workflow 的区别

Harness 是：

```text
“一个开放 Agent 怎么可靠地运行”
```

Workflow 是：

```text
“确定业务步骤按照什么图/状态机执行”
```

可以嵌套：

```text
Workflow Node
    ↓
Agent Harness
    ↓
LLM + Tools
```

例如：

```text
Quote → User Confirm → Pay
```

必须是 Workflow。

其中 Quote 节点内部：

```text
理解偏好 → 多 Tool 搜索 → 排序
```

可以用 Agent Harness。

---

## 17. Harness 和 Sandbox 的区别

Harness 可以做：

```text
Tool policy
workspace validation
SSRF guards
```

但如果 Tool 能执行 shell，最终安全还依赖系统层：

```text
container
seccomp/capabilities
network namespace
egress proxy
filesystem mount
resource limits
```

Pi 明确说明默认运行在启动用户权限下，需要额外 container/sandbox；AgentDock 则把 per-agent container 作为平台能力。

所以：

```text
Harness Security != OS Sandbox
```

---

## 18. 常见错误

### 错误一：Harness = Prompt Template

缺失状态、Tool、Recovery、Trace。

### 错误二：用了 LangGraph/nanobot/Pi 就“自动有 Harness”

框架提供基础能力，企业风险策略、业务 idempotency、tenant policy、eval dataset 仍需自己做。

### 错误三：所有失败都 retry

副作用 effect 可能 UNKNOWN。

### 错误四：Recovery 只靠重新发送最后一条用户消息

可能重复外部 Tool。

### 错误五：平台 Control Plane 也实现一遍 Tool Retry

造成 ownership 混乱。

---

## 19. 常见追问

### Q1：Harness 是不是越重越好？

不是。可靠性要求越高，durable state 越值得；低风险短任务可能不值得付出复杂状态机成本。

### Q2：为什么 Pi 要把 operation state 做得这么重？

因为长生命周期、进程崩溃和外部 effect 的恢复不能只靠对话文本推断。

### Q3：nanobot 的 Checkpoint 能不能等价 Pi Harness？

不能简单等价。nanobot 已有实用的 runtime checkpoint/recovery；Pi Harness 的规范覆盖更完整 durable operation/store/effect 模型。比较要看目标，不要只看名词。

### Q4：OpenViking 属于 Harness 还是 Memory？

属于外部 Context/Memory substrate，可以接入 Harness 的 context-building 阶段。

---

## 20. 1～2 分钟口述版

> 我把 Harness 理解为模型外部的运行保障系统，不只是 Prompt 包装。它负责 Context 构造、模型调用、Tool Registry、权限、Loop/Stop、预算、Timeout、Checkpoint、Recovery、Trace 和 Eval。nanobot 是一个很好的轻量案例：AgentRunSpec、AgentRunner、ContextGovernor、Tool execution、Hook、Checkpoint 都能看到这些组成；Pi 的 AgentHarness 更进一步把 Session、AgentLane、Operation、intent/effect/settlement 和 replay policy 做成 durable state machine，适合解释 crash recovery；AgentDock 属于 Harness 外面的 Control Plane，负责租户、Agent 实例、容器、Driver、Task 和资源；OpenViking 是 Context Database，为 Harness 提供 Memory/Resource/Skill 召回。真正企业架构的关键是把这些 owner 分开：Harness 保证执行过程可靠，Workflow 保证确定性业务顺序，业务 Service 保存最终事实，平台管理实例和资源。

## 项目落点

- nanobot：`nanobot/agent/runner.py`、`nanobot/agent/tools/execution.py`、`nanobot/session/recovery.py`、`nanobot/agent/hook.py`
- Pi：`packages/agent/docs/harness.md`
- AgentDock：README Architecture / Drivers / Tasks / Sandbox
- OpenViking：Context Database / Retrieval Trajectory
