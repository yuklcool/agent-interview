# Agent Eval + Trace + Replay：为什么“最终答案对不对”远远不够

## 面试题

> Agent 的 Golden Dataset 怎么建？线上错了怎么判断是 Planner、Worker、Tool、RAG 还是模型问题？Tool Mock 和 Trajectory Replay 怎么做？

---

## 1. 面试官真正考什么

Agent 和普通 Chatbot 最大的区别之一，是**一次回答背后有执行轨迹**。

如果只保存：

```text
User Question
Final Answer
```

你几乎无法知道错误来自哪里。

真实链路应该被拆成：

```text
User Input
  ↓
Routing
  ↓
Context Build
  ↓
Model Round 1
  ↓
Tool Call A
  ↓
Tool Result A
  ↓
Model Round 2
  ↓
Planner/Worker/Handoff
  ↓
Final Answer
```

所以 Agent Eval 本质上是：

```text
Outcome Eval
+
Trajectory Eval
+
System/Cost Eval
```

---

## 2. Eval 的基本对象要先定义清楚

建议区分：

### Task

用户要完成的业务目标，例如：

> 找出昨晚能耗异常最多的道路并解释原因。

### Trial

同一个 Task 跑一次得到一条轨迹。因为模型有随机性，一个 Task 可以跑多次 Trial。

### Trajectory

一次 Trial 中完整执行路径：

```text
model → tool → observation → model → ...
```

### Outcome

最终是否完成任务，以及最终业务结果。

### Grader

负责评分的规则/程序/模型/人工。

如果不区分这些对象，团队很容易把“某次跑对了”误认为“系统稳定”。

---

## 3. Golden Dataset 从哪来

最有价值的不是人工凭空造 1000 道题，而是**真实高价值失败样本**。

推荐来源：

```text
线上失败
用户投诉
人工转接
Tool Error 高频问题
高风险业务
长尾 Query
曾经修过的 Regression Bug
边界条件
```

一开始几十到一两百条高质量 Case 就能很有价值。

每个 Case 不只是：

```json
{"question":"...","answer":"..."}
```

而应该至少有：

```json
{
  "task_id": "T1001",
  "input": {...},
  "expected": {
    "required_facts": [...],
    "forbidden_claims": [...],
    "allowed_tools": [...],
    "required_tools": [...],
    "max_tool_rounds": 4,
    "safety_constraints": [...]
  }
}
```

这样才能评 Agent，而不只是评文本。

---

## 4. 为什么不能只用 LLM-as-a-Judge

LLM Judge 很方便，但有三个风险：

- Judge 自己会漂移
- 容易偏爱长答案/流畅答案
- 对精确业务事实和权限边界不可靠

所以最好分层：

```text
Deterministic Grader
   SQL result / exact field / JSON / tests

Rule Grader
   forbidden tool / max steps / permission

LLM Judge
   explanation quality / relevance / coherence

Human Review
   高风险抽检
```

能代码验证的就别让模型判断。

---

## 5. End-to-End Success 为什么不够

假设 Agent 最终回答正确，但轨迹是：

```text
查错数据库
→ 失败
→ 查第二个库
→ 重复 3 次 Tool
→ 最后碰巧答对
```

如果只看 Task Success，它得 1 分。

但生产上它：

- 成本高
- 延迟高
- 容易在下次失败
- 可能触发无关副作用

所以要拆指标：

```text
Routing Accuracy
Plan Quality
Tool Selection Accuracy
Argument Validity
Tool Success Rate
Recovery Quality
Groundedness
Final Task Success
Latency
Token Cost
Tool Cost
Safety Violations
```

---

## 6. Tool Calling Accuracy 怎么量化

“工具调用准确率”不能只看 Tool Name。

至少拆：

```text
Tool Selection Accuracy
Argument Schema Validity
Argument Semantic Correctness
Call Necessity
Call Ordering
Redundant Call Rate
Forbidden Tool Rate
```

例如：

```text
正确 Tool=query_alarm
参数 road_id 错了
```

Tool Name 是对的，但这次调用仍然是失败。

还可以对轨迹计算：

```text
Optimal Tool Path Length / Actual Tool Calls
```

衡量是否绕路。

---

## 7. Trace 应该记录什么

每个 Run 至少贯穿：

```text
trace_id
run_id
turn_id
session_id
user/tenant scope
model
prompt/template version
context token count
retrieval ids
plan_id/version
step_id
iteration
tool_call_id
tool name/args hash
latency
status
error_kind
usage/cost
```

推荐 Span 结构：

```text
agent.run
 ├─ context.build
 │   ├─ memory.retrieve
 │   └─ rag.retrieve
 ├─ llm.round.1
 ├─ tool.query_alarm
 │   └─ db.query
 ├─ llm.round.2
 └─ final.render
```

这样当最终答案错时，可以沿 Span 找到责任层。

---

## 8. Planner 拆错还是 Worker 调错，怎么定位

建立明确的 Artifact Contract。

Planner 输出：

```json
{
  "step_id":"S2",
  "goal":"查询昨晚能耗异常设备",
  "constraints":{
    "time_range":"...",
    "project_scope":["P1"]
  },
  "expected_output":"device_list"
}
```

Worker Trace：

```text
收到的 Step 是什么
选择了哪个 Tool
参数是什么
Tool 返回什么
输出 Artifact 是什么
```

那么失败可以分类：

```text
Planner goal/constraint 就错了 → Planner Error
Planner 对，Worker 选错 Tool → Worker Decision Error
Worker 对，Tool 数据错 → Tool/Data Error
前面都对，最终总结错 → Synthesis Error
```

没有结构化 Step Contract，就很难归因。

---

## 9. Tool Mock 为什么重要

如果 Eval 每次都真的调用：

```text
支付
短信
航班
数据库
第三方搜索
```

会有三个问题：

- 不可重复
- 成本高
- 外部数据会变化

所以离线 Eval 需要 Tool Mock：

```text
(tool_name, normalized_args)
        ↓
Fixture / Scenario Store
        ↓
固定 Tool Result
```

例如：

```json
{
  "tool":"query_flight",
  "match":{"from":"SHA","to":"BJS"},
  "result":{"status":"SUCCESS","flights":[...]}
}
```

模型版本变化时，外部世界保持不变，才能做公平回归。

---

## 10. Mock 不能只做 happy path

要专门设计故障场景：

```text
timeout
empty result
429
permission denied
malformed response
partial result
UNKNOWN side effect
stale data
```

Agent 的工程质量往往就是在这些 Case 里体现出来。

---

## 11. Trajectory Replay 是什么

线上记录一条真实 Trajectory：

```text
User Input
Tool A Result
Tool B Result
...
```

Replay 时冻结外部 observation，只重新执行模型决策：

```text
旧模型 / 新模型
        ↓
面对相同 observation
        ↓
比较下一步 Tool/Answer
```

用途：

- 模型升级回归
- Prompt 变更
- Tool Schema 变更
- Routing 逻辑变更

### 注意

Replay 不能完全替代在线 Eval，因为新模型可能选择不同 Tool Path，旧轨迹没有对应 observation。此时需要 Tool Mock/Simulator 补全分支。

---

## 12. Prompt/Model/Schema 发布门禁

任何影响 Agent 决策的变更都应该作为版本化 artifact：

```text
model_version
system_prompt_version
tool_schema_version
retriever_version
reranker_version
policy_version
```

CI 中跑：

```text
Golden Set
  ↓
Regression Eval
  ↓
Safety Cases
  ↓
Cost/Latency Budget
  ↓
Pass Gate
```

例如要求：

```text
Task Success 不下降 > 1%
Forbidden Tool = 0
P95 Tool Calls <= 旧版本 + 10%
Token Cost <= +15%
关键高风险 Case 100% 通过
```

再进入 Canary。

---

## 13. A/B 怎么做才不污染实验

RAG A/B 最容易犯的错：

```text
A 用 Retriever v1 + Prompt v1
B 用 Retriever v2 + Prompt v2
```

最后不知道收益来自哪层。

应尽量一次只改变一个变量：

```text
Retriever A/B：固定模型、Prompt、Reranker
Generator A/B：固定检索结果
```

Agent 端还要按 user/session sticky 分流，不能同一 Session 里一会 A 一会 B。

---

## 14. 最难监控的指标是什么

不是 Token，也不是 P99，而是：

> **Decision Quality**

因为模型可能：

- 选了一个能用但不是最优 Tool
- 多调了两个 Tool 最终也成功
- 给了正确答案但证据不足

这些不能靠基础监控直接看出来。

所以需要把线上 Trace 抽样回流到 Eval Pipeline，做持续标注和自动评分。

---

## 15. Eval-driven 开发流程

不应该：

```text
改 Prompt
→ 手工问 5 次
→ 感觉不错
→ 上线
```

而应该：

```text
发现失败
   ↓
加入 Golden Set
   ↓
明确 failure taxonomy
   ↓
修改 Prompt/Schema/Code/Model
   ↓
Replay + Eval
   ↓
Canary
   ↓
线上 Trace
   ↓
新失败继续回流
```

这才是 Agent 工程的反馈闭环。

---

## 16. 结合 Java + nanobot 怎么落

nanobot 负责 Agent Loop，可以在 Hook/Event 层采集：

```text
iteration
model
usage
tool_events
stop_reason
checkpoint phase
```

Java 业务 Tool 通过 OTel 继续 trace：

```text
Agent Span
  ↓ traceparent
MCP/HTTP Tool
  ↓
Spring Service
  ↓
JDBC/Redis
```

关键是把：

```text
trace_id + run_id + tool_call_id
```

贯穿两边。

离线评测则把生产 Trace 转成标准 Trial Schema，Tool 走 Mock/Replay。

---

## 17. 1～2 分钟面试口述版

> Agent 评测不能只看最终答案，因为一个答案可能碰巧答对但轨迹非常差。我会把评测拆成 Task、Trial、Trajectory、Outcome 和 Grader：Task Success 看最终目标，Trajectory 还看 Router、Plan、Tool 选择、参数、顺序、冗余调用、恢复和安全。线上每个 Run 用 trace_id、run_id、step_id、tool_call_id 贯穿 LLM、Tool、数据库，错误时能定位是 Planner、Worker、Tool 还是最终 synthesis。离线 Golden Set 优先从真实线上失败和高风险 Case 构建；Tool 用 Mock 固定外部世界，历史轨迹可以 Replay 比较模型/Prompt/Schema 新旧版本。最终把 Golden Set、Safety、Latency、Token Cost 做成发布门禁，再用 Canary 和线上 Trace 持续回流，这样开发才是 Eval-driven，而不是靠人工试几次 Prompt。
