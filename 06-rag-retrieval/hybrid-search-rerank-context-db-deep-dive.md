# Hybrid Search / RRF / ReRank / Context Database：RAG 为什么不是“向量搜一下”

> 面试题：为什么 RAG 不能只用向量检索？BM25、Dense Retrieval、RRF、ReRank 各自解决什么问题？OpenViking 这种 Context Database 和普通向量库有什么区别？如何评估检索链是否真的变好？

## 1. 面试官真正考什么

这类题表面在问检索算法，真正考的是：

- 你是否理解不同检索阶段解决不同误差；
- 你是否知道 Recall 和 Ranking 是两个问题；
- 你是否能把权限、版本、结构、上下文层级放到检索链里；
- 你是否知道“ReRank 好”也救不回第一阶段没召回的文档；
- 你是否能从离线指标走到线上 Agent 成功率。

只回答：

> “BM25 关键词匹配，Embedding 做语义匹配，然后加个 ReRank。”

还是太浅。

---

## 2. 核心结论

我会把生产 RAG 拆成：

```text
Query Understanding
      ↓
Hard Filter
 tenant / ACL / version / time
      ↓
Candidate Retrieval
 ┌────────────┬─────────────┐
 │ BM25       │ Dense       │
 │ exact term │ semantic    │
 └──────┬─────┴──────┬──────┘
        └───── Fusion ┘
              ↓
             RRF
              ↓
        Cross-encoder / LLM ReRank
              ↓
       Context Assembly
              ↓
         Model-facing Context
```

如果是 Context Database，还要加入：

```text
目录/层级
L0 / L1 / L2
recursive retrieval
retrieval trajectory
memory/resource/skill type
```

---

## 3. 为什么 Dense Retrieval 不是万能的

Dense Embedding 擅长：

```text
“怎么给数据库做权限隔离？”
≈
“如何限制不同用户查询的数据范围？”
```

即使词面不一样，也可能语义接近。

但它可能对下面场景不稳定：

```text
错误码 ORA-00942
设备编号 SL-100981
类名 ContextGovernor
SQL 字段 project_id
法规条款 GB/T 5700-2023
```

这些 Exact Token 对 BM25 更友好。

所以 Hybrid Search 的本质不是“两个算法效果叠加”，而是：

> **用互补错误分布提高候选召回。**

---

## 4. BM25 解决什么

BM25 基于词频、逆文档频率和文档长度归一化。

直觉上：

```text
一个词在当前文档频繁出现
+
这个词在全库不常见
→ 更有区分度
```

适合：

- API 名称；
- 产品型号；
- 函数名；
- 精确术语；
- 错误码；
- 数据库字段；
- 组织内部缩写。

但 BM25 不懂：

```text
退款
≈
原路退回支付款项
```

所以 Dense 仍然有价值。

---

## 5. 为什么融合常用 RRF，而不是直接把分数相加

BM25 的分数和 cosine similarity 不在同一个尺度。

例如：

```text
BM25 score = 18.7
Dense score = 0.83
```

直接：

```text
18.7 + 0.83
```

没有统计意义。

Reciprocal Rank Fusion 使用排名：

```text
RRF(d) = Σ 1 / (k + rank_i(d))
```

优点：

- 不要求两个 retriever score calibration；
- 工程简单；
- 对某一个 retriever 极端高分不敏感；
- 适合多路候选合并。

例如：

```text
Doc A
BM25 rank = 1
Dense rank = 8

Doc B
BM25 rank = 4
Dense rank = 2
```

RRF 会综合两个排名，而不是比较完全不同的原始分数。

---

## 6. ReRank 到底解决什么

第一阶段 Retriever 目标：

> **快 + 高 Recall。**

ReRank 目标：

> **在候选集里更准确地判断 Query-Document relevance。**

典型链：

```text
100 万 chunks
   ↓
BM25/Dense 召回 100
   ↓
RRF merge → 50
   ↓
Cross Encoder ReRank → Top 8
```

Cross Encoder 能同时看 Query + Document，比独立 embedding 更能捕捉细节，但成本更高，所以不能拿来全库扫描。

关键面试点：

> 如果正确文档没有进入 Candidate Set，ReRank 再强也没有用。

因此先看：

```text
Recall@K / HitRate@K
```

再看：

```text
MRR / nDCG / Precision@K
```

---

## 7. 权限过滤应该在什么时候做

最危险的做法：

```text
全库召回
   ↓
模型看到 unauthorized docs
   ↓
最后再过滤答案
```

这已经造成数据泄露。

应该尽量：

```text
Identity / Tenant / ACL
        ↓
retrieval filter
        ↓
candidate search
```

如果向量系统 filter 能力有限，也至少要保证未经授权内容不进入最终 Context。

对于高敏感系统：

```text
ACL-aware index
+ retrieval filter
+ final context validation
```

多层校验。

---

## 8. Chunking 为什么会直接决定 Retrieval 上限

错误 Chunk：

```text
一个 3000 token 文档
里面同时有：
- 登录
- 支付
- 退款
- 会员
```

Query：

```text
“退款到账要多久？”
```

Embedding 可能因为多个主题混合导致向量表示变模糊。

但切得太碎：

```text
“到账时间为 1-3 天。”
```

又失去：

```text
什么类型退款？
哪个支付方式？
工作日还是自然日？
```

所以更合理的是 semantic / structure-aware chunking。

例如 API 文档：

```text
endpoint + description + params + response
```

数据库 Schema：

```text
table + columns + foreign keys + business meaning
```

不要按固定 500 字机械切。

---

## 9. Parent-Child Retrieval 解决什么

一种实用模式：

```text
Child Chunk
  小、适合精确检索
      ↓ hit
Parent Document/Section
  大、适合给模型理解上下文
```

也就是：

```text
search small
read big
```

这样兼顾 Recall 精度和最终 Context 完整性。

OpenViking 的 L0/L1/L2 分层其实提供了另一个类似思想：

```text
先看 Abstract
      ↓
相关再看 Overview
      ↓
必要时读 Details
```

---

## 10. OpenViking 为什么叫 Context Database，而不是单纯 Vector DB

OpenViking 当前的核心抽象不是：

```text
collection
  └─ chunks
```

而是：

```text
viking://
├── resources
├── user/{id}/memories
└── user/{id}/skills
```

它强调几个区别：

### 10.1 Context 有类型

```text
Resource
Memory
Skill
```

不是所有东西都扁平化成 Document。

### 10.2 Context 有目录结构

可以像文件系统一样：

```text
ls
tree
find
```

目录本身也有 Abstract/Overview。

### 10.3 Context 有层次加载

```text
L0 Abstract
L1 Overview
L2 Full Details
```

能在 token budget 内逐步深入。

### 10.4 Retrieval 可观察

它保留 directory browsing / retrieval trajectory。

这对调试很有价值：

```text
为什么模型回答错？
   ↓
是没召回？
还是走错目录？
还是只读了 L0？
还是 L2 内容本身错误？
```

---

## 11. OpenViking 和 nanobot ContextGovernor 怎么组合

不要把二者当替代关系。

```text
OpenViking
负责从巨大 Context Space 找 Candidate

nanobot ContextGovernor
负责把最终 Candidate + Transcript + Tool Result
压进模型上下文窗口
```

组合：

```text
User Query
   ↓
OpenViking Retrieval
   ↓
L0/L1/L2 candidates
   ↓
Runtime Context Builder
   ├─ System
   ├─ Session Summary
   ├─ Recent Messages
   ├─ Retrieved Memory/Resource
   └─ Tool Schema
   ↓
ContextGovernor / Token Budget
   ↓
LLM
```

如果 Retrieval 拿回 50 个好文档，但 Context Builder 全塞进去，仍然会失败。

---

## 12. Query Rewrite 什么时候有用

用户说：

> “它昨天怎么又坏了？”

孤立 Query 几乎无法检索。

需要利用 Session：

```text
上一轮：海八路 3 号控制柜
当前：它昨天怎么又坏了？
```

Rewrite：

```text
“海八路 3 号控制柜 2026-09-07 再次故障原因”
```

但 Query Rewrite 也会带来风险：

- 改错实体；
- 引入模型幻觉；
- 把用户模糊问题变成过度具体问题。

所以建议保留：

```text
original_query
rewritten_query
rewrite_reason
```

并在 Eval 里单独测 rewrite。

---

## 13. 城市照明知识库案例

用户问：

> “灯源故障报警高发的时候一般怎么排查？”

候选源：

```text
运维手册
历史事件
设备型号说明
道路照明技术规范
历史 Agent 处置经验
```

可以设计：

```text
Query
 ↓
ACL(project/user)
 ↓
BM25
  捕捉“灯源故障”“报警”精确术语
 ↓
Dense
  捕捉“排查”“故障诊断”语义
 ↓
RRF
 ↓
ReRank
 ↓
OpenViking directory/context expansion
 ↓
选 Top Context
 ↓
LLM
```

如果最终回答错误，要沿链定位：

```text
Retrieval Failure?
Ranking Failure?
Context Assembly Failure?
Generation Failure?
```

而不是笼统说：

> “Embedding 模型不行。”

---

## 14. 300+ 表 Text-to-SQL 和普通 RAG 的区别

Schema Retrieval 虽然也是检索，但不能只找“最像的表”。

还需要：

```text
table relevance
+ join path
+ FK relationship
+ permission path
+ business meaning
```

例如 Query 命中：

```text
energy_history
```

但权限需要：

```text
energy_history → device → project
```

所以 Retriever 需要做 relation expansion，而不是只拿 TopK table descriptions。

这也是为什么 Text-to-SQL 的 RAG 更像：

```text
semantic retrieval
+
graph expansion
+
business metadata
```

---

## 15. Retrieval Eval 应该怎么做

### 第一阶段：Candidate Recall

构造真实 Query → Relevant Docs 标注。

指标：

```text
Recall@5
Recall@10
Recall@50
HitRate@K
```

### 第二阶段：Ranking

指标：

```text
MRR
nDCG@K
Precision@K
Top1 / Top3 accuracy
```

### 第三阶段：Generation

固定 Retrieval，测试：

```text
groundedness
citation correctness
answer correctness
```

### 第四阶段：Agent Task

最终还要看：

```text
task success
wrong tool rate
unnecessary retrieval count
latency
token cost
```

---

## 16. A/B 怎么拆 Retrieval 和 Generation

不要一次同时换：

```text
Embedding
Reranker
Prompt
LLM
Chunk
```

否则不知道提升来自哪里。

### Retrieval A/B

固定：

```text
LLM + Prompt
```

比较：

```text
BM25 only
Dense only
Hybrid
Hybrid + ReRank
```

### Generation A/B

固定同一批 retrieved docs，再换模型/Prompt。

这样才能做因果归因。

---

## 17. 常见失败

### 失败一：只看最终答案正确率

不知道是 Retrieval 还是 Generation 出错。

### 失败二：TopK 越大越好

Recall 可能上升，但噪声和 token cost 也上升。

### 失败三：ReRank 代替 Retriever

候选没召回，无法补救。

### 失败四：权限最后过滤

可能在 Context 层已经泄露。

### 失败五：所有 Memory / Skill / Docs 平铺一个 collection

类型、层级、生命周期全部丢失。

---

## 18. 常见追问

### Q1：RRF 的 k 怎么选？

它是平滑参数，不是固定真理。用真实 Eval Dataset 调，重点看多个 retriever 的 rank 稳定性，而不是死背 60。

### Q2：什么时候不需要 Dense？

高度结构化、精确 token 主导、数据规模小的场景，BM25/SQL/filter 可能已经足够。

### Q3：什么时候用 LLM ReRank？

候选数较小、语义判断复杂且延迟/成本可接受时。高 QPS 更常见 cross-encoder 或轻量 reranker。

### Q4：OpenViking 能替代所有向量库吗？

不要绝对化。它提供 Context Database 和层次/trajectory 抽象；底层具体检索和企业规模要求仍要按数据量、部署、性能选择。

---

## 19. 1～2 分钟口述版

> 我不会把 RAG 简化成向量 TopK。第一阶段目标是高 Recall，所以先做权限/版本等 hard filter，再用 BM25 和 Dense 召回互补候选，通过 RRF 用排名融合，避免不同 score scale 直接相加；然后用 ReRank 优化候选顺序。评估也要分层，Retriever 看 Recall@K/HitRate，ReRank 看 MRR/nDCG，最后再看 groundedness 和 Agent task success。OpenViking 给了一个更强的 Context Database 视角：Memory、Resource、Skill 不是平铺 chunk，而是 viking:// 层级空间，内容有 L0 Abstract、L1 Overview、L2 Details，并保留 retrieval trajectory。它负责‘从巨大 Context Space 找什么回来’，nanobot ContextGovernor 再负责‘本轮哪些内容真正发给模型’。这两个问题不能混在一起。

## 项目落点

- OpenViking：README / retrieval docs / L0-L1-L2 API
- nanobot：Context Governance / Transcript Builder
- 业务案例：300+ 表 Text-to-SQL Schema Retrieval + relation expansion
