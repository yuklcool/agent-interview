# 06. RAG、检索与知识库——全量深度版

> 覆盖 `06-01`～`06-17`。本章把 RAG 当成一个真正的信息检索系统：解析、Chunk、索引、Query、Filter、召回、融合、重排、Context Assembly、版本、权限、评测，每层都能出问题。

---

## 06-01. RAG 里 Chunk 切大切小各有什么坑？实际怎么切业务文档

### 核心目标

Chunk 不是为了“控制成 500 字”，而是优化：

```text
语义完整性 × 可检索区分度 × Context 成本
```

### 太小

- 标题和正文被拆开；
- 表头和数据行分离；
- 条款前提与例外分离；
- 一个函数签名和实现分离；
- embedding 只看到片段词汇，没有完整语义。

### 太大

- 一个向量混多个主题；
- 精确命中后仍带大量无关文本；
- reranker 和 LLM Context 成本高；
- 权限/版本粒度变粗。

### 实际切分

优先结构，再 token：

```text
Markdown/规范 → heading → section → paragraph
FAQ         → Q+A
代码        → class/function
表格        → header + row groups
SQL Schema  → table + columns + keys + relations
流程        → step group / node
PDF         → layout blocks + logical section
```

Overlap 只用于确实跨边界的语义，不要所有 Chunk 固定重叠 20%。

### 评测

同一 Query-Doc 集比较不同 chunk policy 的 `Recall@K / MRR / nDCG / answer grounding / token cost`。没有评测就无法证明 300、500、800 token 哪个更好。

### OpenViking 启发

OpenViking不是只切平面 chunks，而是保留虚拟目录结构，并给目录/内容生成 L0 abstract、L1 overview、L2 detail。这提供另一种“先定位结构，再逐层展开”的 Context 组织方式。

---

## 06-02. 混合检索怎么融 BM25 和向量？RRF 还是别的

### 为什么需要 hybrid

BM25 强在 exact terms：设备号、道路名、告警码、标准编号；Dense 强在语义：用户口语和文档专业术语不同。

### baseline

```text
ACL / Metadata Filter
       ↓
┌──────┴──────┐
BM25 TopK   Dense TopK
└──────┬──────┘
       ↓
      RRF
       ↓
Cross-Encoder ReRank
       ↓
Context Expansion
```

### RRF

RRF 只用排名：

```text
score(d) = Σ 1 / (k + rank_i(d))
```

优点是不同检索器 score 不需要校准。第一版往往比直接 `0.5*BM25 + 0.5*cosine` 稳。

### 什么时候不用 RRF

如果有足够 click/judgement 数据，可训练 fusion/ranking model；也可做 score normalization + learned weights。但先有稳定 baseline 再复杂化。

### 权限为什么必须前置

先全库召回再让 LLM“过滤权限”已经泄露。tenant/project ACL 应尽量在每个 retrieval backend 前置 filter。

---

## 06-03. ReRank 上线前后召回质量怎么量化

### 先分清指标层

First-stage retrieval：

```text
Recall@K / HitRate@K
```

Reranking：

```text
MRR
nDCG@K
Precision@K
Top1 / Top3 Accuracy
```

### 例子

正确文档本来就在 Top10 第 8 位，rerank 后变第 1 位：

- Recall@10 没变化；
- MRR/nDCG 显著提升。

这才说明增益来自排序。

如果正确文档根本没进候选，reranker 没法“凭空找回来”。Recall 低时应先看 Chunk、Query rewrite、embedding、BM25/Dense coverage。

### 实验设计

固定候选集、模型、Prompt，只切换 reranker；线上记录 `retriever_version/reranker_version`，观察引用覆盖、groundedness、task success 和 latency。

---

## 06-04. RAG 知识库版本变了，线上怎么热更不闪断

把知识索引当软件发布，不在生产索引原地重建。

```text
Source v2
  ↓ parse/chunk
Index v2 build
  ↓ offline eval
Warmup
  ↓ shadow/dual-run
Canary
  ↓
Atomic alias switch: current → v2
  ↓
Observe
  ↓
Keep v1 for rollback
```

### 会话一致性

长对话可 pin `knowledge_version=v1`，避免前一轮按旧退改签规则、后一轮突然按新规则。紧急法规可有显式 global override。

### 数据模型

Document/Chunk metadata 至少有：

```text
source_id
content_version
index_version
effective_from/effective_to
created_at
acl_scope
parser_version
embedding_version
```

这样才能回放某次答案到底用了哪个知识版本。

---

## 06-05. Embedding 模型怎么和召回场景对齐？怎么做领域微调或替换

### 不看排行榜直接选

用真实 Query-Doc 集评估：

- exact entity；
- 口语同义；
- 长 query；
- 多语言；
- 领域缩写；
- hard negative。

### 先优化 pipeline 再微调

很多问题不一定是 embedding：Query Rewrite、BM25、metadata filter、chunk policy、rerank 都可能提升更大。

### 微调

有领域数据后可构造 `(query, positive, hard-negative)` 对做 contrastive fine-tuning。Hard negative 要选择“语义很像但业务上错误”的文档，例如同一设备型号但不同项目/版本。

### 替换模型

Embedding model 变化意味着向量空间变化：必须新建索引、重 embedding、dual-run/canary，不能在旧向量库里混用。

---

## 06-06. 如何向非技术人员解释 RAG？

不要只说“检索增强生成”。可以类比：

> 大模型像一个很会理解和写作的人，但它不一定记得你公司的最新制度。RAG 相当于回答前先去公司资料库查相关文件，把真正的材料放到桌面上，再根据材料回答。

但要补一句关键边界：

> 找资料找对了不代表回答一定对，所以我们还要控制资料版本、权限、来源和引用；如果资料没召回，模型也不能自己编。

### 用实际架构解释

```text
用户问题
  ↓
找相关资料
  ↓
选择最可信/最新/有权限资料
  ↓
把资料交给模型
  ↓
带证据回答
```

这样既易懂，又没有把 RAG 说成“彻底消除幻觉”。

---

## 06-07. 企业知识库从原始文档到可检索索引，完整构建管线是什么？

### Offline ingestion

```text
Source Connectors
 ↓
Raw Object Store
 ↓
Parser / Layout / OCR / Code Parser
 ↓
Normalization
 ↓
Document Structure
 ↓
Chunking
 ↓
Metadata / ACL / Version
 ↓
Embedding + Lexical Index
 ↓
Index Validation
 ↓
Publish Version
```

### Online retrieval

```text
Query
 ↓ auth/scope
Query Understanding / Rewrite
 ↓
Metadata+ACL Filter
 ↓
BM25 + Dense / Recursive Retrieval
 ↓
Fusion
 ↓
ReRank
 ↓
Parent/Neighbor Expansion
 ↓
Context Budgeting
 ↓
LLM
```

### 生产关键项

- 原始文件必须保留，方便重新 parse；
- parser/chunker/embedding 都要 version；
- ingestion 幂等；
- delete/update 要能传播；
- ACL 和内容版本必须随索引一起更新；
- 建立 dead-letter queue 处理解析失败文件。

### OpenViking

OpenViking将 resources 处理成目录化 Context 和 L0/L1/L2，可作为传统“文档→平面 chunk→vector DB”之外的实现案例。

---

## 06-08. Query Rewrite 为什么能提升检索？什么时候会把问题改坏？

### 为什么有效

用户问题常包含代词、上下文依赖、口语表达：

> “这个灯昨天为什么那么高？”

检索需要补成：

```text
project=P1
lamp_id=L902
metric=energy_consumption
period=yesterday
question=abnormal high consumption reason
```

Rewrite 可以扩展同义词、解析实体、补当前 Session context。

### 怎么改坏

模型可能：
- 把“最早航班”改成“最快航班”；
- 丢掉否定词；
- 猜错设备/项目；
- 把当前用户假设写成事实；
- 过度扩展导致召回漂移。

### 安全 Rewrite

保留原 query，并生成多个 retrieval query：

```text
original
normalized
entity-focused
semantic expansion
```

最后融合结果；对 ID、日期、金额等关键实体采用 deterministic extraction/validation。

---

## 06-09. Parent-Child Indexing 解决什么问题？

它解决“检索粒度”和“生成上下文粒度”冲突。

### Child 小块负责召回

小块语义集中，容易命中。

### Parent 大块负责回答

命中 child 后，把其父段/章节展开给模型，避免只看到半句话。

```text
Parent: 退款政策第 3 章
  ├─ Child A: 退款时限
  ├─ Child B: 手续费
  └─ Child C: 特殊票种
```

用户问特殊票种，Dense 命中 Child C；Context 中可以加入 Parent overview + C detail。

### 与 OpenViking

OpenViking的目录递归检索和 L0/L1/L2 不是传统 Parent-Child Index 的同一实现，但思想相通：先在更细/更抽象层定位，再加载周边/更详细 Context。

---

## 06-10. 什么时候需要 GraphRAG / 多跳检索，而不是普通向量 RAG？

### 适合多跳的问题

答案依赖多实体关系链：

```text
某告警
 → 哪个设备
 → 属于哪个路段
 → 路段当前调光策略
 → 策略对应哪版规范
```

一个 chunk 不包含完整链路，普通 TopK 可能只找零散片段。

### GraphRAG 的价值

显式实体/关系和 traversal，可做受控多跳，并保留 provenance。

### 不该滥用

FAQ、单文档条款、简单知识查询，Graph 构建和更新成本可能大于收益。

### 混合架构

```text
Vector search 找 seed entities/docs
        ↓
Graph expansion / relation traversal
        ↓
ReRank evidence paths
        ↓
Context synthesis
```

先用 eval 确认大量 failure 真的是 multi-hop missing，而不是 Chunk/Rewrite 问题。

---

## 06-11. 向量数据库怎么选？pgvector、Milvus、ES 各自看什么？

### 不按“谁最快”选

看：数据规模、过滤复杂度、已有运维栈、混合检索、更新频率、HA、成本。

### pgvector

适合已经以 PostgreSQL 为核心、规模中等、需要 transaction/metadata/ACL relational filter 的场景。优点是系统简单、数据和权限关系自然；大规模纯向量吞吐不是它唯一优势。

### Milvus

适合大量向量、专业 ANN、独立向量基础设施；需要额外运维和 metadata/业务数据同步设计。

### Elasticsearch/OpenSearch

强项是 BM25、过滤、聚合、全文生态，同时支持 vector/hybrid；如果企业已有 ES，混合检索落地很自然。

### 面试回答

> 我先问规模、过滤、现有栈和 hybrid 需求，再选库。100 万向量的 Java/Postgres 系统，我可能先 pgvector；亿级向量和独立检索平台再考虑 Milvus；关键词和向量都强依赖则 ES 很有价值。

---

## 06-12. HNSW 和 IVF_FLAT 有什么区别？怎么选索引参数？

### HNSW

构建多层近邻图，查询沿图搜索。通常 recall/latency 优秀，但索引内存和构建成本较高。

常见参数思想：

- `M`：每个节点连接数，越大内存/构建成本高、召回可能更好；
- `efConstruction`：建图搜索宽度；
- `efSearch`：查询搜索宽度，越大 recall 高但 latency 高。

### IVF_FLAT

先聚类成多个 list，查询时只探测 `nprobe` 个簇。

- `nlist`：簇数；
- `nprobe`：查询探测簇数。

### 怎么调

用真实数据画 Recall-Latency-Cost 曲线，不按网上固定值。高 filter 场景尤其要测试：过滤后候选不足会改变 ANN 表现。

---

## 06-13. ES 关键词检索改成向量检索，会得到什么、失去什么？

### 得到

- 同义语义；
- 口语/专业术语映射；
- 问题与答案表述不一致时仍能命中。

### 失去/弱化

- exact ID/型号/告警码能力；
- 可解释 term score；
- 稀有关键字精确匹配；
- 某些复杂 lexical query 功能。

### 正确方向通常不是“替换”

而是 hybrid：BM25 + Dense + fusion + rerank。

城市照明里 `SL-100029`、道路编号、故障码应该让 BM25 发挥优势；“灯一直忽明忽暗是什么问题”这种自然语言由 Dense 补足。

---

## 06-14. 表格、图片、PDF Layout 该怎么进知识库？为什么 OCR 一把梭不够？

OCR 只把像素变成文字，不理解：表格行列、标题层级、页眉页脚、图注、跨页表、单位关系。

### PDF pipeline

```text
PDF
 ↓
Layout Detection
 ├─ heading
 ├─ paragraph
 ├─ table
 ├─ figure
 └─ caption
 ↓
OCR only when needed
 ↓
Logical reconstruction
 ↓
Chunk + metadata
```

### 表格

保留：table title、header、单位、row keys；必要时把一行/一组行序列化成可搜索文本，并保存原始结构 JSON。

### 图片

对于设备图、拓扑图、截图，可生成 vision caption/embedding；但必须保存 page/source/region 作为 evidence pointer。

### 评测

单独建立 table QA / visual QA 集，不要只用纯文本问答指标判断多模态 ingestion。

---

## 06-15. RAG 检索了很多文档但回答反而更差，怎么排查？

先沿 pipeline 分层：

```text
Query quality
 ↓
Candidate recall
 ↓
Fusion/ranking
 ↓
Context diversity/redundancy
 ↓
Context ordering
 ↓
Generation grounding
```

### 常见原因

- TopK 太大，噪声超过信号；
- 重复 chunks 占满 context；
- 旧版本和新版本同时出现；
- 多个文档冲突但没有 effective time；
- reranker 对领域不适配；
- Query Rewrite 漂移；
- Long Context lost-in-the-middle；
- 模型没有被要求区分来源/冲突。

### 诊断方法

对 bad case 保存：原 query、rewrite、每阶段 ranking、score、最终 chosen context、source versions、answer citations。没有 retrieval trace 很难定位。

OpenViking的 observable retrieval trajectory正好体现“检索路径必须可解释”的价值。

---

## 06-16. 如何防止“补检索→还不够→再补检索”无限循环？

### Retrieval Loop 必须有进度函数

维护：

```text
retrieval_round
queries_used
new_unique_evidence_count
covered_subquestions
remaining_unknowns
token/cost budget
deadline
```

### Continue 条件

只有新一轮能解决明确缺口且还在 budget 内，才继续。

```text
Need more evidence?
   ↓ yes
Did last round add useful unique evidence?
   ├─ no → stop/clarify
   └─ yes
Budget available?
   ├─ no → partial answer
   └─ yes → next targeted query
```

相同 query 或高度相似 query 重复检索应被 no-progress guard 阻止。

### 最终收敛

`ANSWER / PARTIAL_WITH_GAPS / NEEDS_USER / NO_EVIDENCE`，而不是永远 Tool loop。

---

## 06-17. 多模态 Embedding 做图文检索时，怎么避免视觉相似压过业务语义？

### 问题

两张夜景路灯图片视觉上很像，但一个是“灯源故障”、一个是“正常低亮调光”。纯视觉 embedding 可能把它们排很近。

### 多信号检索

```text
Visual embedding
Text/caption embedding
Metadata: device type / road / alarm code / time
Domain classifier
        ↓
Fusion / ReRank
```

### 业务语义加权

- exact metadata filter；
- 图像 caption/structured attributes；
- multimodal reranker；
- query intent 决定视觉 vs 文本权重。

例如“找和这张灯杆外观相同的设备”视觉权重高；“找同一故障原因的案例”应提高故障标签、文本和业务 metadata 权重。

### 评测

建立不同 intent 的 multimodal benchmark，不能只看统一 Recall；分别测 visual similarity、semantic fault retrieval、exact asset retrieval。

---

# RAG 排障主线

```text
Source正确吗？
 ↓
Parser正确吗？
 ↓
Chunk合理吗？
 ↓
ACL/Version正确吗？
 ↓
Query/Rewrite正确吗？
 ↓
Recall够吗？
 ↓
Ranking好吗？
 ↓
Context有噪声/冲突吗？
 ↓
模型有没有 grounded 地使用？
```

这条链能比“把 TopK 从 5 改成 10”解决更多真实问题。
