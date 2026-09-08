# Session、Memory、State：三者为什么不能混为一谈

> 面试题：Agent 的 Session、短期记忆、长期记忆、业务状态分别应该放在哪里？历史压缩以后还能恢复吗？用户偏好什么时候写入长期 Memory？多个设备同时聊同一个 Session 怎么保证一致性？

## 1. 面试官真正考什么

很多回答会把这些词混在一起：

```text
Session
Memory
History
State
Context
Redis
```

然后给出一句：

> “都存 Redis 就行。”

这其实没有回答问题。

面试官真正想看你是否能回答：

- 哪些是**事实记录**？
- 哪些只是**模型视图**？
- 哪些是**长期可检索经验**？
- 哪些是**当前执行状态**？
- 谁有写权限？
- 多端并发时谁是 single writer？
- Summary 错了以后能不能恢复？
- Memory 冲突如何处理？

---

## 2. 核心结论

我会明确拆成五类：

```text
Durable Transcript
  = 原始会话事实记录

Model-facing Context
  = 本轮真正发给模型的投影

Runtime State
  = 当前 run / iteration / tool / checkpoint 状态

Long-term Memory
  = 从历史中提取、可跨 Session 复用的信息

Business State
  = 订单、退款、设备、工单等最终事实
```

它们可以使用同一种数据库，但**语义和 owner 绝对不能混**。

---

## 3. Durable Transcript 和 Model-facing Context 的根本区别

例如完整历史是：

```text
U1
A1
U2
A2
ToolCall3
ToolResult3
A3
...
U300
```

这是一份 Durable Transcript。

但模型上下文窗口可能只有有限 token，所以真正发送时是：

```text
System Prompt
+ Session Summary
+ Selected Memory
+ Relevant Resource
+ Recent Messages
+ Current Tool Schemas
```

这叫 Model-facing Context。

关键点：

> **压缩的是模型视图，不应该把真实历史本身当场销毁。**

否则 Summary 一旦漏掉关键事实，系统无法回溯。

---

## 4. 为什么 Summary 不能是唯一事实源

假设历史里用户说：

```text
“不要自动控制路灯，只给分析建议。”
```

后来 Summary 错写成：

```text
“用户允许自动控制。”
```

如果系统只保留 Summary：

```text
业务安全边界已经被一个概率模型覆盖
```

正确做法是：

- 原始 Transcript 可审计；
- Summary 是可重建派生数据；
- 高风险 Constraint 应进入结构化 Runtime/Policy State，而不是只存在 Summary。

例如：

```json
{
  "side_effect_policy": "NO_AUTO_ACTION"
}
```

---

## 5. nanobot 当前怎么处理这个问题

nanobot 当前已经把 Transcript 与模型请求的 Context 治理分开。

`AgentRunSpec` 支持：

```text
transcript_input
transcript_builder
consolidate_history
consolidate_provider_compaction
```

`AgentRunner` 创建：

```text
ContextCompactionState
ContextGovernanceConfig
ModelRequestState
```

然后每轮不是机械把所有历史直接发给模型，而是构造 request messages。

这说明一个很重要的 Runtime 原则：

> **Session History 是 durable input；ContextGovernor 决定本轮模型看到什么。**

此外 nanobot recovery 会保存 runtime checkpoint，而不是单纯依赖聊天文本猜测 Tool 是否执行完成。

所以 Session 里其实同时存在：

```text
conversation facts
+
runtime metadata/checkpoint
```

但它们的语义仍然不同。

---

## 6. Pi 的 Session / Branch / Lane 给了更重的状态模型

Pi AgentHarness 规范把 Session 建模得更像 durable runtime database，而不只是聊天列表。

它区分：

```text
entry tree
mutable values/lists
usage ledger
Branch
AgentLane
Operation
```

尤其重要的是：

```text
operation metadata
operation current state
terminal result
```

这让 Runtime 可以明确回答：

> “进程崩溃前最后一次 durable transition 到哪里？”

而不是通过：

```text
最后一条消息是什么？
```

来猜。

这种设计对长任务、并发 Lane、恢复非常有价值。

---

## 7. Long-term Memory 到底应该存什么

不是所有历史都值得进入长期记忆。

我会把 Memory Admission 做成一个独立过程：

```text
Conversation / Experience
        ↓
Candidate Extraction
        ↓
Admission Policy
        ├─ useful?
        ├─ stable?
        ├─ private?
        ├─ duplicated?
        ├─ conflicting?
        └─ TTL?
        ↓
Long-term Memory
```

适合长期保存：

```text
稳定用户偏好
长期项目背景
重复验证过的操作经验
长期约束
```

不适合：

```text
一次性验证码
临时订单状态
今天的天气
一次 Tool timeout
模型自己的未验证推测
```

---

## 8. OpenViking 为什么适合说明 Long-term Context

OpenViking 当前把：

```text
resources
memories
skills
```

统一放在 `viking://` 虚拟文件系统中。

例如：

```text
viking://user/{user_id}/memories/
viking://user/{user_id}/skills/
viking://resources/project-x/
```

而且内容在写入后会形成：

```text
L0 Abstract
L1 Overview
L2 Details
```

检索时可以先浅后深。

这和简单“把每条聊天做 embedding”相比有两个很好的工程启发：

1. Context 不是平铺 chunk，而是有层级/目录语义；
2. 召回可以保留 retrieval trajectory，错误时能看出从哪个目录/路径召回。

OpenViking 还支持 session commit 后异步提取用户偏好和 agent experience 到长期 memory。

这正好对应：

```text
Session != Memory
```

Memory 是 Session 的派生长期资产，而不是 Session 本身。

---

## 9. Memory 冲突怎么处理

例如历史：

```text
2026-01 用户：回答尽量简洁
2026-08 用户：技术问题要深入展开
```

不能把两个 embedding chunk 都召回后让模型自己猜。

至少需要：

```text
memory_id
subject
value
valid_from
valid_to
source
confidence
updated_at
supersedes
```

冲突策略：

```text
同 subject
  ↓
最新明确声明优先
  ↓
旧记录标 superseded
  ↓
必要时保留历史审计
```

对于事实类 Memory 还要区分：

```text
user stated
system observed
agent inferred
```

推断类置信度应该低于用户明确声明。

---

## 10. 多端同时操作同一个 Session 怎么办

假设手机和 Web 同时发送：

```text
M1: 查最早航班
M2: 不对，改成最便宜
```

如果两个 Runtime 并行读同一个 History：

```text
Runtime A sees version 10
Runtime B sees version 10
```

然后都写 version 11，会丢更新。

### 方案一：per-session actor / single writer

```text
所有消息
   ↓
Session Queue
   ↓
唯一 Actor
   ↓
按顺序执行/注入
```

适合一个 Session 一次只允许一个 owner。

### 方案二：optimistic version / CAS

```text
session_version = 100
```

更新：

```sql
UPDATE session
SET version = 101,
    state = :state
WHERE id = :id
  AND version = 100;
```

失败就 reload/reconcile。

### 方案三：Append-only events + materialized view

```text
seq=101 user_message
seq=102 plan_changed
seq=103 tool_started
```

Current State 是事件投影。

这对审计和 replay 最友好，但复杂度最高。

---

## 11. nanobot 的 Injection 能怎么解释用户中途改口

nanobot 的 AgentRunner 当前支持：

```text
injection_callback
terminal_injection_callback
continuation_callback
```

并对每个 turn 的 injection 数量/cycle 有限制。

这意味着用户在 Agent 正在执行时，可以在安全边界把新的 user message 注入后续 iteration。

但要区分：

```text
message injection
!=
完整 plan versioning
```

Injection 让模型“看到用户改口”；企业级 Workflow 还要自己管理：

```text
plan_version
cancel_requested
stale tool result
```

---

## 12. AgentDock 中 Session、Agent、Container 不要混

平台上常见三个对象：

```text
User Conversation
Agent Instance
Runtime Container
```

它们可以是不同生命周期。

例如：

```text
一个 Agent Container
   ├─ Conversation A
   ├─ Conversation B
   └─ Conversation C
```

或者为了隔离：

```text
Conversation A → Container A
Conversation B → Container B
```

取决于：

- 安全隔离；
- Runtime 是否支持多 Session；
- 资源成本；
- Workspace 是否共享；
- 恢复粒度。

AgentDock 当前强调的是 Agent 实例/container 的持久 workspace、Task、生命周期和多租户管理；这不等于它必须把“一个会话”直接映射成“一个容器”。

面试时能把这三个概念拆开，会比“Session 存 Redis”高级很多。

---

## 13. 城市照明场景怎么分

用户第一天问：

> “以后分析能耗异常时，优先结合报警和前一晚数据。”

这可以作为长期工作偏好/经验：

```text
OpenViking Memory / Skill
```

第二天问：

> “昨晚海八路能耗异常有多少盏？”

实时结果应该来自：

```text
PostgreSQL / Device Service
```

本次会话执行中的：

```text
当前 Tool Call
当前 iteration
等待哪个结果
```

属于：

```text
nanobot/Pi Runtime State
```

会话完整消息属于：

```text
Durable Transcript
```

模型本轮看到的：

```text
Summary + Recent + Retrieved Memory + Tool Schema
```

属于：

```text
Model-facing Context
```

一张图：

```text
           Durable Transcript
                  │
        ┌─────────┴───────────┐
        │                     │
        ▼                     ▼
Context Projection       Memory Extraction
        │                     │
        │                 OpenViking
        │                     │
        └──────────┬──────────┘
                   ▼
              Model Context
                   │
                   ▼
                 LLM
                   │
              Tool Runtime
                   │
                   ▼
             Business Truth
```

---

## 14. Redis 到底放什么

Redis 很适合：

```text
session routing
hot run status
stream cursor
rate limit
idempotency key
short lease
cache
pub/sub
```

但不建议默认把以下事实只放 Redis：

```text
长期 transcript
支付/退款最终状态
关键审计记录
长期 memory 原始来源
```

理由不是“Redis 不可靠”，而是这些信息需要更明确的 durability/audit/query 语义。

---

## 15. Context Compaction 的正确目标

压缩不是：

```text
把 100 条消息总结成 1 条，越短越好
```

而是：

> 在有限 token budget 下，保留完成当前任务所需的最小充分信息。

应该保护：

```text
当前用户目标
未完成约束
Tool Call ↔ Tool Result 配对
关键业务事实
高风险确认状态
当前计划状态
```

可压缩：

```text
重复解释
已完成低价值中间推理
大段 Tool 原始输出（可转 artifact ref）
早期闲聊
```

---

## 16. 失败模式

### 失败一：Summary 覆盖原始 History

无法审计和重新压缩。

### 失败二：所有消息自动进入 Long-term Memory

会积累噪声、过期状态和模型幻觉。

### 失败三：Memory 没有 source/version

无法处理冲突和过期。

### 失败四：多个 Runtime 同时写一个 Session

会发生重复 Tool、消息乱序、恢复不确定。

### 失败五：把业务状态存进 Memory

实时事实被过期召回污染。

---

## 17. 常见追问

### Q1：Long-term Memory 应该同步写还是异步写？

通常异步 extraction + admission 更合适，不阻塞主响应；但用户明确“记住这个”时可以提高优先级并返回已提交的 Memory Operation 状态。

### Q2：Memory 召回错误怎么办？

记录 source/trajectory，允许 supersede；关键行为不能只依赖 Memory，仍要走 Policy/Business validation。

### Q3：Context 超限在哪一层处理？

Runtime 的 Context Governance 层，而不是业务 Service；外部 Context DB 负责召回候选，不负责最终 token packing。

### Q4：同一个 User 的多个 Session 要共享什么？

共享长期 Memory/Resource；不要默认共享当前 Runtime State 和未完成 Tool 状态。

---

## 18. 1～2 分钟口述版

> 我会把 Session、Context、Memory 和业务 State 明确分开。Durable Transcript 是完整会话事实，Model-facing Context 是每轮按 token budget 构造的视图，Runtime State 保存当前 iteration、Tool、checkpoint，Long-term Memory 是从 Session 异步提取出的稳定偏好和经验，而订单、设备、退款这些业务事实仍在 Domain DB。nanobot 的 ContextGovernor/CompactionState 很适合说明 Transcript 和模型 Context 的分离，它还有 injection 和 recovery；Pi Harness 更进一步把 Session、Branch、Lane、Operation 做成 durable state machine；OpenViking 则把 Memory、Resource、Skill 放在 viking:// 下，并用 L0/L1/L2 分层召回。多端并发时我会用 per-session single writer 或 version/CAS，而不是一句‘存 Redis’解决。核心原则是每种状态必须有明确 owner、寿命和恢复语义。

## 项目落点

- nanobot：`nanobot/agent/runner.py`、context governance、session recovery
- Pi：`packages/agent/docs/harness.md`
- OpenViking：Context Database / Session Memory / L0-L1-L2
- AgentDock：Agent instance / Task / Container / Workspace 生命周期
