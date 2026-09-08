# 12. 公司偏好与面试表达策略

> 技术准备做得再深，如果表达方式把问题带到自己不熟悉的方向，也会吃亏。这一章不是教“话术套路”，而是教你如何把真实工程经验组织成高信号回答。

---

## 12-01. 你怎么学 Harness / Context Engineering 这种中文资料少的东西

### 面试官真正考什么

不是考你会不会搜英文，而是看你是否有一套面对快速变化领域的学习方法。

### 推荐回答框架

```text
先找原始定义
  ↓
读一手源码/官方文档
  ↓
找真实失败场景
  ↓
自己做小实验
  ↓
形成可复用抽象
```

例如学 Context Engineering，不应该只看二手文章，而是：

1. 看模型 API 的 message/tool schema/context limit。
2. 看 nanobot `context_governance`、compaction、transcript builder 源码。
3. 构造长会话，观察历史什么时候被压缩、Tool Result 怎么裁剪。
4. 对比完整历史 vs summary + recent messages 的效果和 Token。
5. 总结出 durable transcript / model-facing context / context budget 这些概念。

### 面试表达

> 我习惯把新概念先还原成系统问题。比如 Harness，我会问它到底管哪些模型外能力：Loop、Tool、权限、恢复、Trace、Eval，然后直接看开源 Runtime 的代码和失败路径。最后通过实际实验验证，而不是只记一个定义。

---

## 12-02. 最近半年哪篇 Agent 工程文章你觉得偏营销，哪篇真能落地

这题不要直接攻击作者，也不要只背文章标题。

### 判断一篇工程文章有没有含金量

看它有没有：

```text
明确问题
Baseline
Failure Cases
可复现实验
成本/延迟
Trade-off
Ablation
真实架构约束
```

偏营销文章通常：

```text
只展示成功 Demo
没有失败率
没有成本
没有对照组
把模型能力包装成平台能力
```

真正可落地的文章会讲“哪里不工作”。

### 回答方式

> 我不会简单评价某篇文章好坏，我更关注有没有工程证据。比如一篇 Agent 文章如果只说多 Agent 能提高效果，但不讲额外 Token、延迟、失败传播和什么时候不该拆，我会认为工程价值有限。真正有价值的是能给 baseline、失败轨迹、成本和 ablation 的文章，因为我可以把结论转成自己的 Eval。

---

## 12-03. 面试最后的反问怎么问得有深度

不要问网上能搜到的：

```text
公司用什么模型？
团队多少人？
```

更好的问题围绕“这个岗位真正的工程难点”。

例如：

- 你们当前 Agent 最大的线上 failure mode 是模型问题、Tool 问题还是业务集成问题？
- Tool/Workflow 的安全边界现在是在 Agent Runtime 还是业务服务里？
- 你们评测更关注最终 task success，还是已经有 trajectory/tool-level eval？
- 当前系统是单 Agent 为主，还是已经进入 Planner/Worker、多 Agent？拆分后最大的收益和成本分别是什么？
- 这个岗位入职三个月最希望解决的一个技术问题是什么？

这些问题同时能让你判断岗位成熟度。

---

## 12-04. 不同公司 Agent 面试侧重点不一样，怎么做针对性准备

不要给每家公司准备完全不同的一套知识，而是建立“核心能力 + 公司偏好映射”。

### 核心能力不变

```text
Agent Loop
Context
Tool/MCP
RAG
Recovery
Eval/Trace
Java 工程
```

### 偏业务平台型团队

重点准备：

```text
多租户
权限
稳定性
成本
工作流
接入效率
```

### 偏模型/算法团队

重点：

```text
SFT
RL/DPO/GRPO
Tool-use data
Reranker
Model Routing
Eval
```

### 偏 AI Coding

重点：

```text
Repo Context
AST/LSP
Sandbox
Patch Validation
Test Generation
Trajectory
```

### 偏搜索/RAG

重点：

```text
Hybrid Search
Rerank
Index
Query Rewrite
GraphRAG
Offline/Online Eval
```

策略不是临时背题，而是把同一项目从不同角度讲。

---

## 12-05. 热门 Coding Agent 怎么比较，避免变成“谁最强”争论

不要用排行榜式回答：

> A 最强，B 第二。

因为模型和产品变化很快，而且不同任务结论不同。

### 比较维度

```text
Runtime 架构
Context 获取
Tool/Shell/File 能力
Sandbox
Checkpoint
Git workflow
MCP/Plugin
模型可替换性
Observability
权限边界
扩展成本
```

### 举例回答结构

> 我比较 Coding Agent 更看“它怎么工作”而不是单次 Benchmark。比如有的产品优势是模型和工具闭环强，有的优势是开源、可替换 Provider，有的优势是 MCP/插件生态。真正做企业接入时，我还会看工作区隔离、Shell 权限、Git diff、失败恢复和 Trace，因为这些决定它能不能安全进入开发流程。

---

# 面试表达的六条总原则

## 原则一：先给结论，再展开

不要让面试官听两分钟还不知道你的答案。

```text
结论
 ↓
为什么
 ↓
怎么实现
 ↓
场景
 ↓
边界
```

---

## 原则二：不要把“我知道”说成“我做过”

例如 nanobot 当前没有通用 DAG Scheduler，就不要说：

> 我们 nanobot 里已经用 DAG 管所有长任务。

可以说：

> nanobot 当前核心是 Tool-using Agent Loop；我研究过如果要支持长任务 DAG，需要在上层补 step state、plan version 和 scheduler。

真实比包装更能经得住追问。

---

## 原则三：每道 Agent 题都尽量讲“失败时怎么办”

浅回答：

> Tool 超时就重试。

深回答：

> 查询类 Tool 可以有限重试；副作用 Tool 超时可能是 UNKNOWN，要先对账，不能直接 replay。

高级面试的差距经常就在失败路径。

---

## 原则四：区分模型软决策和代码硬约束

这是整套资料最重要的主线之一：

```text
模型：
理解、推荐、规划、解释

代码/业务：
权限、状态机、幂等、安全、预算、事务
```

任何高风险题都可以回到这条原则。

---

## 原则五：不要堆术语，要串运行链

不要：

```text
我们用了 RAG、MCP、Agent、Memory、Redis、Kafka。
```

要说：

```text
用户消息通过 WebSocket 进入，按 session 加载 summary 和 recent messages；模型需要业务数据时返回 Tool Call，Runtime 先做 schema/权限校验，再通过 MCP 调 Java Service，Tool Result 回注，最终答案流式返回；全过程用 run_id/tool_call_id 做 Trace。
```

运行链比名词更能证明理解。

---

## 原则六：回答完主动给出边界

例如：

> 这个设计解决了单 Run 的恢复，但不等于业务 Exactly-once，副作用 Tool 仍要幂等和状态对账。

主动讲边界会让回答显得成熟，因为真实系统没有万能方案。

---

# 推荐复习方法

不要按 159 道题逐题死背。先建立 8 条主线：

```text
1. Agent Loop / Runtime
2. Context / Memory / Session
3. Tool / MCP / Permission
4. Recovery / Idempotency / Safety
5. RAG / Text-to-SQL
6. Multi-Agent / Planning
7. Harness / Eval / Trace
8. Java / Spring / Platform
```

每条主线先能画图，再能讲状态机，再能讲一个真实失败案例。做到这一步，大多数换皮问题都能现场推导，而不是靠记答案。
