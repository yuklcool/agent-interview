# Context Engineering 深挖：Durable Transcript、Model-facing Context、压缩与上下文爆炸

> 目标：把“上下文太长就做摘要”这种浅回答升级成真正的 Context Runtime 设计：哪些信息是事实、哪些信息应该进入模型、压缩边界在哪、Tool Result 太大怎么办、如何防止摘要漂移。

## 面试题

> Agent 的历史记录到底怎么发送给模型？Durable Transcript 和 Model-facing Context 有什么区别？什么时候压缩？Tool Result 太大时怎么裁剪？

---

# 一、为什么 Context Engineering 是 Agent 的核心

LLM 每一轮看到的世界只有 Context。

所以 Agent 的能力上限不只由模型决定，还由：

```text
你给了什么
没给什么
给的顺序
给的格式
哪些事实被压缩了
哪些 Tool Schema 占用了窗口
```

决定。

很多 Agent “变笨”其实不是模型变差，而是 Context 被污染、截断或摘要丢信息。

---

# 二、必须区分三类数据

## 1. Durable Transcript

完整事实记录：

```text
user messages
assistant messages
tool calls
tool results
system-generated recovery rows
```

它服务于：

```text
审计
回放
恢复
评测
长期记忆原材料
```

## 2. Session Summary / Memory

是从历史中提炼的高层信息。

例如：

```text
用户正在分析 A 项目的照明异常
已确认时间范围是昨晚 18:00-07:00
已排除通信中断作为主要原因
```

它不是完整事实，只是压缩表示。

## 3. Model-facing Context

真正发给模型的是一个动态投影：

```text
System Prompt
+ 当前角色/权限/运行约束
+ Summary
+ 最近原始消息
+ 检索到的 Memory/RAG
+ Tool Schemas
+ 当前用户消息
```

所以：

```text
Durable Transcript ≠ Model-facing Context
```

这是这类题最重要的一句话。

---

# 三、为什么不能每次把全部历史都发给模型

三个问题：

## 1. Token 成本

历史越长，每一轮都重复计费。

## 2. Attention 稀释

长上下文并不意味着模型一定更准确。大量旧消息会把当前任务的关键约束稀释。

## 3. 历史冲突

用户前面说：

```text
我要最早航班
```

后面改成：

```text
我要最便宜
```

如果上下文构造不强调最新约束，模型可能继续受旧目标影响。

---

# 四、Context Budget 怎么算

粗略预算：

```text
context_window
- generation_budget
- safety_margin
= available_prompt_budget
```

然后再分配：

```text
System / Policy       15%
Tool Schema           20%
Recent Conversation  30%
Summary / Memory      15%
RAG / Tool Artifacts  20%
```

不是固定比例，但需要有预算意识。

尤其 Tool 很多时，Tool Schema 本身可能吃掉大量 token。

---

# 五、压缩不是“把前面全部总结成一段”

更合理的策略是分层：

```text
最近消息：保留原文
较旧消息：摘要
非常旧但重要：Memory
大体积 Tool Result：Artifact / 摘要 / 引用
```

可以理解成：

```text
Hot Context
Warm Summary
Cold Memory
```

其中：

- Hot：最近原始对话，最高保真；
- Warm：当前会话摘要；
- Cold：跨会话长期记忆或外部知识。

---

# 六、压缩边界为什么不能切断 Tool Call / Tool Result

比如历史：

```text
Assistant: tool_call query_alarm
Tool: result {...}
Assistant: 根据结果继续分析
```

如果压缩时只保留：

```text
Assistant: tool_call query_alarm
```

却丢掉 Tool Result，模型会看到一个未闭合调用。

因此压缩应该以：

```text
完整 Turn
完整 Tool Call/Result pair
完整已结束执行段
```

为边界。

这也是 Durable Transcript 和 Model Context 分离后才容易实现的。

---

# 七、摘要漂移怎么防

Summary 本质上也是模型生成内容，可能出现：

```text
遗漏
误归因
数字变形
把 tentative 结论写成事实
```

所以不要把 Summary 当唯一事实源。

建议：

```text
Summary = Navigation Layer
Transcript = Source of Truth
```

关键事实最好保存结构化字段：

```json
{
  "time_range": "2026-09-07T18:00/2026-09-08T07:00",
  "project_id": "p-17",
  "confirmed_constraints": ["只读分析"],
  "open_questions": ["异常主因待确认"]
}
```

这样重要约束不完全依赖自然语言摘要。

---

# 八、Tool Result 很大怎么办

这是 Agent 实战非常常见的问题。

例如 SQL 返回：

```text
50,000 行 JSON
```

直接回注模型会导致：

```text
Token 爆炸
上下文污染
延迟增加
真正关键字段被淹没
```

推荐四层处理：

## 1. Tool 端先限制

```text
limit
pagination
projection
aggregation
```

能在数据库算的，不要拉回来再让 LLM 算。

## 2. Runtime Truncation

保留：

```text
row_count
schema
first N samples
统计摘要
artifact_id
```

## 3. Artifact Store

完整结果放：

```text
object storage / temp file / DB
```

模型只拿：

```text
artifact_id + summary
```

需要时再用 Tool 按页读取。

## 4. Semantic Reduction

对长文本/文档先做：

```text
chunk → filter → summarize
```

而不是一刀字符截断。

---

# 九、动态截断要看“信息价值”，不是只看时间

最近消息不一定最重要。

比如 20 轮前用户确认了：

```text
“绝对不能执行写操作。”
```

这个约束即使很旧，也必须保留。

因此 Context Item 最好有 metadata：

```text
priority
source
recency
relevance
must_keep
sensitivity
```

Context Builder 可以按：

```text
hard constraints > current task > recent turns > related memory > background
```

排序。

---

# 十、结合 nanobot 当前怎么讲

nanobot 当前 `AgentRunner` 已经有：

```text
TranscriptInput
TranscriptBuilder
ContextCompactionState
ContextGovernor
ContextGovernanceConfig
ModelRequestState
```

这说明它内部已经不是简单：

```python
messages = session.messages
```

然后直接发模型。

`AgentRunSpec` 还包含：

```text
max_tool_result_chars
context_window_tokens
max_tokens
consolidate_history
consolidate_provider_compaction
```

也就是说：

```text
历史构造
Tool Result 大小
Provider Context Window
生成预算
历史压缩
```

都属于 Runtime Context Governance 的一部分。

---

# 十一、Context 和 Memory 的边界

不要把所有旧消息都叫 Memory。

推荐区分：

```text
Conversation History
当前会话原始事实

Session Summary
当前会话压缩

Long-term Memory
跨会话稳定信息

RAG Knowledge
外部知识库

Runtime State
当前执行状态
```

例如：

```text
“Tool 3 正在 RUNNING”
```

这是 Runtime State，不是 Memory。

```text
“用户习惯用 PostgreSQL”
```

可能是 Long-term Memory。

```text
“上一轮 query_alarm 返回 46 条”
```

是当前 Turn/Session 的 observation。

---

# 十二、Context Injection 风险

外部 Tool/RAG 返回内容可能包含：

> Ignore previous instructions...

如果直接拼进 System Prompt，就会形成 Prompt Injection。

所以外部数据应该标记来源：

```text
UNTRUSTED TOOL OUTPUT
RAG DOCUMENT
USER CONTENT
SYSTEM POLICY
```

并保持明确优先级。

系统政策永远不能被低信任内容覆盖。

---

# 十三、城市照明场景示例

用户连续问：

```text
1. 昨晚 A 路多少灯异常？
2. 这些异常是不是能耗突增？
3. 再结合报警看看。
4. 重点看刚才那 17 盏。
```

Model-facing Context 不应该每次塞完整夜间报告。

可以变成：

```text
System/Policy
Project Scope=A
Summary:
- 昨晚 A 路检测到 17 盏异常灯
- 主要表现为功率突增
Recent:
User: 再结合报警看看
Tool Result Summary:
- 17 个 device_ids = artifact://abnormal-17
Current:
User: 重点看刚才那 17 盏
```

模型如果需要完整明细：

```text
read_artifact(artifact://abnormal-17)
```

按需读取。

---

# 十四、如何评测 Context Engineering

不能只看“没超 Token”。

至少评估：

```text
Task Success Rate
Constraint Retention Rate
Critical Fact Recall
Hallucination Rate
Context Tokens / Turn
Latency
Summary Drift
Tool Repetition Rate
```

特别推荐做一个测试：

> 在 20 轮前埋一个关键约束，后面多轮 Tool Call 后，看系统还能不能正确遵守。

这比单纯测问答准确率更能发现 Context Governance 问题。

---

# 十五、常见错误

## 错误 1：历史越全越好

不对。关键是 relevance 和 budget。

## 错误 2：Summary 是事实源

不对。Summary 只是压缩表示。

## 错误 3：Tool Result 直接全部回注

容易爆上下文。

## 错误 4：只按最近时间裁剪

会丢掉旧但重要的硬约束。

## 错误 5：把 Memory、Session、Runtime State 混成一层

后续恢复和权限会非常混乱。

---

# 十六、2 分钟面试口述版

> 我会把 Durable Transcript 和 Model-facing Context 明确分开。Transcript 保存完整事实，用于审计、恢复和回放；每次调用模型前，Context Builder 再根据 token budget 动态投影 System Policy、Summary、Recent Turns、Memory/RAG、Tool Schema 和当前请求。旧历史不会全部原样发送，而是分成最近原文、会话摘要、长期 Memory。压缩时不能切断 Tool Call/Tool Result pair，而且 Summary 不是事实源，关键业务约束最好结构化保存。Tool Result 很大时我也不会直接塞进模型，而是先分页/聚合，再用 artifact_id + summary，模型需要细节时按需读取。nanobot 当前已经有 ContextGovernor、ContextCompactionState、TranscriptBuilder 和 max_tool_result_chars 这些 Runtime 组件，所以这部分我会理解为 Agent Harness 的核心，而不是简单的聊天历史拼接。
