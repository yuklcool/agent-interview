# 2026 RAG 生产面试补充：语义分块、复杂 PDF、多路召回、ReRank、知识时效与低质量 Query

> 来源：最新面试截图题库。以下 6 道题与 `06-rag-retrieval/deep-complete.md` 中已有主题存在高度重合，因此不重复制造新的核心编号，而是作为 **生产级 RAG 高频追问专题** 补充。
>
> 这组题真正考的不是“会不会向量检索”，而是能否把 RAG 设计成完整的信息检索系统：**解析 → 结构化 → 分块 → 索引 → Query 理解 → 多路召回 → 融合 → ReRank → Context 组装 → 版本/权限/时效 → 评测**。

---

# 1. 固定长度分块的致命缺陷是什么？语义分块、层级分块怎么落地？

## 面试官真正考什么

不是让你回答“固定 500 token 不好”，而是看你是否理解：**Chunk 同时决定召回边界、语义完整性、权限粒度、版本粒度和最终 Context 成本。**

如果分块策略错误，后面即使换更强 Embedding、加 ReRank，也只能在一个已经损坏的信息单元上做优化。

## 固定长度分块的致命问题

固定长度本质是：

```text
Document
  ↓ every N tokens
Chunk 1
Chunk 2
Chunk 3
```

它完全不理解文档结构，因此最容易造成四类破坏。

### 1）语义边界被切断

例如旅游退款规则：

```text
第 7 条：不可退票种除外。
退款申请须在出发前 24 小时提交，
如遇航班取消则不受上述限制。
```

如果固定长度把它切成：

```text
Chunk A：退款申请须在出发前 24 小时提交
Chunk B：如遇航班取消则不受上述限制
```

用户问“航班取消还能退款吗”，只命中 A 就会得到错误结论。

### 2）结构信息丢失

PDF/Markdown 中的标题、本节适用范围、表头、注释都可能与正文被拆开：

```text
标题：儿童票退改规则
表头：票种 | 退票费 | 改签费
数据行：学生票 | 10% | 免费
```

只取数据行时，模型甚至不知道它属于哪个表。

### 3）检索单元和生成单元冲突

检索希望 Chunk 小：语义集中、容易命中。
生成希望 Context 稍大：需要上下文、定义和例外。

因此一个大小同时承担“召回”和“回答”通常不是最优。

### 4）版本/权限边界粗糙

如果一个 1500-token Chunk 跨越两个政策版本或两个不同权限章节，就很难对其中一半做 ACL、effective_time 或失效控制。

---

## 我实际会怎么做：Structure First，Token Second

不是先说“512 token”，而是先识别文档结构：

```text
Document
  ↓
Heading / Section / Paragraph / Table / List / Clause
  ↓
Semantic Unit
  ↓
Token Budget Check
  ├─ small enough → keep
  └─ too large    → recursive split
```

例如：

```text
政策文档 → 章 → 条 → 款
FAQ      → Question + Answer
旅游攻略 → 城市 → 景点 → 交通/门票/营业时间
代码     → class / function
SQL      → table + columns + PK/FK + relationships
表格     → table header + row group
```

## 语义分块怎么落地

语义分块不是“每句都算 embedding，相似度下降就切”这么简单。

更稳的是多信号：

```text
Structural Boundary
+ Semantic Similarity Change
+ Length Budget
+ Special Block Rules
```

伪逻辑：

```text
for block in parsed_document:
    if heading_changed:
        flush()
    elif semantic_shift_large and current_chunk_not_too_small:
        flush()
    elif token_budget_exceeded:
        split_recursively()
```

其中标题和版式结构一般比纯 embedding 相似度更可信。

---

## 层级分块：真正解决“召回小块、回答大块”

推荐：

```text
Document
  ↓
Section / Parent
  ↓
Child Chunks
```

例如：

```text
Parent：日本铁路周游券退款规则
  ├─ Child 1：退款时限
  ├─ Child 2：手续费
  ├─ Child 3：自然灾害例外
  └─ Child 4：已激活票券规则
```

搜索阶段命中 Child 3，最终 Context 可以组装：

```text
Parent Summary
+ Child 3 Detail
+ Neighbor Child（必要时）
```

而不是把整篇 20 页规则都交给模型。

## OpenViking 可以怎么解释

OpenViking 的思路可以作为层级 Context 的真实案例：资源不是只有一层平面 chunk，而是组织成目录化 Context，并可按类似：

```text
L0 Abstract
   ↓
L1 Overview
   ↓
L2 Detail
```

逐层展开。

这和传统 Parent-Child Index 的具体实现并不完全相同，但核心思想一致：

> **先用低成本、高概括层确定“应该去哪”，再加载真正需要的 Detail。**

## 如何证明分块优化有效

不要说“感觉 500 token 最好”。用相同 Query-Doc 数据集比较：

```text
Recall@K
MRR / nDCG
Citation Coverage
Answer Groundedness
Average Context Tokens
Retrieval Latency
```

最终优化目标不是单一 Recall，而是：

```text
信息完整性
× 检索准确率
× Context 成本
× 最终任务成功率
```

## 1～2 分钟口述版

> 固定长度分块最大的缺陷不是长度本身，而是它不理解语义和结构，容易把标题与正文、条件与例外、表头与数据行切开。我的做法是 Structure First、Token Second，先按标题、条款、表格、FAQ、函数等业务语义单元切，再对过大的单元递归拆分。召回粒度和生成粒度我也不会强行统一，而会用 Parent-Child 或层级 Context：小 Child 负责精准命中，命中后再展开 Parent 或邻居上下文。OpenViking 的 L0/L1/L2 也能很好解释这种逐层加载思想。最终是否有效要用 Recall@K、MRR/nDCG、Groundedness 和 Context Token 成本一起评估，而不是拍脑袋定 500 token。

---

# 2. 旅游场景 PDF 混杂图文、表格、政策条款，解析难点是什么？怎么解决？

## 核心结论

复杂 PDF 的主要问题不是“怎么提取文本”，而是：

> **怎么把视觉布局重新恢复成正确的逻辑结构，并保留 provenance。**

如果直接 `pdftotext → split → embedding`，在复杂旅游 PDF 上非常容易失真。

## 六类典型解析难点

### 1）阅读顺序错乱

双栏排版可能被解析成：

```text
左栏第 1 段
右栏第 1 段
左栏第 2 段
右栏第 2 段
```

导致语义交叉。

### 2）表格结构丢失

例如酒店取消政策：

```text
房型 | 入住前 7 天 | 3～6 天 | 0～2 天
A    | 免费         | 30%    | 100%
```

如果解析成散乱文本，模型无法知道 `30%` 属于哪个时间区间。

### 3）扫描件没有文本层

这类才需要 OCR；有正常文字层的 PDF 不应一律 OCR，因为 OCR 反而可能引入字符错误。

### 4）图片承载事实

例如景区地图、票价图、路线图、时间表，文字提取不到真正信息。

### 5）页眉页脚污染

页码、公司名、水印会在每一页重复，进入 embedding 后成为高频噪音。

### 6）跨页逻辑

表格跨页、条款跨页、标题在上一页正文在下一页，都需要恢复关联。

---

## 推荐解析 Pipeline

```text
Raw PDF
  ↓
PDF Type Detection
  ├─ text PDF
  ├─ scanned PDF
  └─ mixed PDF
  ↓
Layout-aware Parser
  ├─ text blocks
  ├─ headings
  ├─ tables
  ├─ images
  ├─ captions
  └─ page coordinates
  ↓
OCR only when needed
  ↓
Table Structure Reconstruction
  ↓
Image/Vision Description（必要时）
  ↓
Reading-order Recovery
  ↓
Noise Removal
  ↓
Logical Document Model
  ↓
Semantic/Hierarchical Chunking
  ↓
Index
```

## 不同对象不能用同一种 Chunk Schema

### 政策条款

建议保留：

```json
{
  "document":"JR Pass Policy",
  "section":"Refund",
  "clause":"7.2",
  "text":"...",
  "effective_from":"2026-08-01",
  "page":18
}
```

### 表格

不能只转 Markdown 后丢掉来源信息。至少保留：

```text
table_title
headers
row_group
page
source_bbox
```

对于问：

> “入住前三天取消多少钱？”

更适合将表结构转为可检索的 row/record 表示，再附原始表格引用。

### 图片

如果图片包含可查询事实，可以生成：

```text
image caption
entities
structured extracted facts
page/source reference
```

但 Vision 模型提取的数据仍然要标记来源和置信度，不能当原始政策文本同等可信。

---

## 一个旅游 PDF 的真实示例

假设 PDF 有：

```text
Page 1  东京景点介绍
Page 2  地铁路线图
Page 3  酒店价格表
Page 4  酒店取消政策
Page 5  附注/例外条件
```

用户问：

> “如果我住这个酒店，提前 2 天取消，同时因为台风航班取消，会扣多少钱？”

RAG 不能只命中价格表；至少需要：

```text
Hotel Cancellation Policy
        ↓
2-day cancellation rule
        +
Force-majeure / typhoon exception
        +
Hotel rate / booking type
```

也就是一个**结构恢复 + 多块证据组合**问题。

## 生产上一定要保留 Raw + Parsed Version

建议保存：

```text
raw_file_hash
parser_version
ocr_version
vision_model_version
chunker_version
parsed_at
```

这样 parser 升级后可以重新构建索引，也能定位“这次错误是 LLM 错还是 PDF parser 错”。

---

# 3. 多路召回（Dense Vector + BM25）各解决什么？旅游模糊查询怎么平衡？

## 核心结论

Dense 和 BM25 并不是“两个都用效果一定更好”，而是解决不同类型的匹配问题。

```text
BM25   → lexical precision
Dense  → semantic recall
```

旅游场景恰好同时大量需要两者。

## BM25 擅长什么

精确 token / ID / 专有名词：

```text
JR EAST PASS
CI123
台北 101
羽田 T3
景区代码 A1709
政策编号 2026-07
```

这些查询如果只走 Dense，有时会召回“语义类似但不是这个实体”的文档。

## Dense 擅长什么

用户口语和文档表达不一致：

```text
用户：“带小孩坐车有没有优惠？”
文档：“儿童票价适用于 6～11 岁乘客”
```

BM25 可能没有“优惠”这个词，而 Dense 可以建立语义匹配。

---

## 旅游模糊 Query 不应该直接拿原句搜索

例如：

> “东京有个红色塔附近适合晚上去的地方。”

这其实包含：

```text
entity uncertainty     = 红色塔 ? Tokyo Tower
location constraint    = 附近
intent                  = 晚上去
category                = 景点/餐厅/夜景
```

可以先做 Query Understanding：

```text
Original Query
  ↓
Entity Detection / Normalization
  ↓
Intent + Geo + Time Constraints
  ↓
Multiple Retrieval Queries
```

例如生成：

```text
Q1 original: 东京 红色塔 晚上 附近
Q2 normalized: Tokyo Tower evening attractions nearby
Q3 entity-focused: Tokyo Tower
```

再进入 BM25 + Dense。

## Fusion 为什么常先用 RRF

BM25 分数和 cosine similarity 并不是同一尺度：

```text
BM25 score = 18.4
Dense score = 0.83
```

直接：

```text
0.5 * BM25 + 0.5 * Dense
```

没有天然含义。

RRF 使用 rank：

```text
RRF(d) = Σ 1 / (k + rank_i(d))
```

对于第一版系统通常比较稳，因为不要求两个 retrieval score 先做精确校准。

## 还要不要动态调整权重？

可以。

例如 Query Classifier 判断：

```text
ID / policy-code / exact hotel name
→ lexical-heavy

natural-language recommendation
→ semantic-heavy
```

但这里要强调：

> 动态权重需要真实 Query Judgement 数据验证，否则只是把“人工感觉”写进 Router。

## 地理查询还应该有结构化 Geo Filter

例如：

> “台北车站附近 1 公里适合带孩子的酒店”

不要期待 embedding 理解“1 公里”。

应该：

```text
semantic retrieval: family-friendly hotel
+
geo filter: distance <= 1km
+
metadata filter: city=Taipei
```

因此旅游 RAG 的多路召回很多时候其实是：

```text
Lexical
+ Dense
+ Metadata
+ Geo
+ Availability/Structured DB
```

不只是两个向量通道。

---

# 4. 上线 ReRank 前后，怎么量化召回质量提升？

## 最容易答错的地方

很多人只看：

```text
Recall@K
```

然后发现上线 ReRank 后没变化，就认为 ReRank 没效果。

这是因为 ReRank 负责的是**排序**，不是 first-stage recall。

## 指标分层

### 第一阶段召回

关注：正确文档有没有进入候选池。

```text
Recall@K
HitRate@K
```

### ReRank

关注：正确文档在候选池里有没有被排到更靠前。

```text
MRR
nDCG@K
Precision@K
Top1 Accuracy
Top3 Accuracy
```

例子：

正确文档上线前位于第 8 名：

```text
Recall@10 = 1
MRR       = 1/8
```

ReRank 后变第 1：

```text
Recall@10 = 1   # 没变
MRR       = 1   # 大幅提升
```

这就是典型 ReRank 收益。

---

## 但最终不能只看 IR Metric

线上 RAG 最终目标是回答/任务效果，所以至少还应关联：

```text
Citation Coverage
Groundedness
Answer Correctness
Task Success Rate
Tool Selection Accuracy（Agent 场景）
Context Tokens
P95 Retrieval Latency
Rerank Cost
```

例如 ReRank 把 nDCG 提升 10%，但增加 1.5 秒延迟，最终用户任务成功率没有提升，那上线价值就值得质疑。

## 正确 A/B 设计

想证明“提升来自 ReRank”，要尽量固定其他变量：

```text
Same Query Set
Same Chunk Version
Same Embedding
Same Candidate TopK
Same Prompt/LLM
Only ReRank changes
```

然后比较：

```text
Before: Candidate → original rank
After : same Candidate → reranked
```

否则同时换 embedding、chunk、query rewrite 和 reranker，最后无法归因。

## 数据集怎么做

至少要覆盖：

```text
exact entity query
fuzzy semantic query
multi-hop query
negative/no-answer query
freshness-sensitive query
policy exception query
```

特别是旅游领域要加入：

```text
同名酒店
相似景点
旧价格 vs 新价格
相同政策不同日期版本
```

这些 hard negative 才真正考验 ReRank。

---

# 5. 政策、票价、酒店规则实时更新，怎么避免过期内容和新旧冲突幻觉？

## 核心结论

RAG 的时效性不能靠 Prompt 写：

> “请优先参考最新资料。”

必须把 **版本、有效时间、发布时间、来源优先级** 做成可执行的数据规则。

## 文档 Metadata 至少要有

```text
source_id
document_id
content_version
published_at
effective_from
effective_to
supersedes
status: draft/active/expired
retrieved_at
index_version
```

例如：

```text
Hotel cancellation v3
published_at   = 2026-09-01
effective_from = 2026-10-01
```

在 9 月 15 日回答当前入住规则时，**v3 虽然发布时间最新，但尚未生效**。

所以：

```text
latest published
!=
currently effective
```

这是非常重要的生产边界。

---

## Retrieval 必须做 Temporal Filter

用户问：

> “今天买东京地铁票多少钱？”

应该先解析：

```text
query_time = today
```

然后 Retrieval Filter：

```text
effective_from <= query_time
AND
(effective_to IS NULL OR effective_to > query_time)
AND
status = active
```

不是把新旧版本都召回后让 LLM 猜谁有效。

## 新旧数据冲突怎么办

如果确实召回冲突内容，Context Builder 应优先做确定性 Resolution：

```text
same source + same rule
    ↓
compare effective time/version
    ↓
select active version
```

如果来源不同且无法确定权威性：

```text
Official provider
  > Contracted partner
  > Aggregator
  > User-generated content
```

优先级应该是业务定义的 Source Policy，而不是模型自己决定。

## 价格和库存不应该完全走知识库

旅游里最典型：

```text
票价
酒店库存
航班余票
实时营业状态
```

这类高度动态信息更适合：

```text
RAG → 查询规则/解释
Tool/API → 查询实时事实
```

例如：

```text
用户：“明天这个酒店多少钱，能不能免费取消？”

Hotel API
→ 明天实时价格 / availability

RAG Policy
→ cancellation rule

Agent
→ 合并解释
```

不要把昨天爬进知识库的房价当今天事实。

## 热更新怎么做

不要生产索引原地全量重建：

```text
Source v2
  ↓
Parse / Chunk
  ↓
Index v2
  ↓
Offline Eval
  ↓
Warmup / Shadow
  ↓
Atomic Alias Switch
  ↓
Observe
  ↓
Keep v1 rollback
```

长 Session 若需要一致性，可记录 `knowledge_version`；紧急法规更新再通过 explicit override 处理。

## 回答必须携带 freshness/provenance

建议 Agent 获取的证据里带：

```json
{
  "source": "JR Official",
  "effective_from": "2026-09-01",
  "retrieved_at": "...",
  "version": "v7"
}
```

这样回答和 Trace 才能定位“为什么当时这么答”。

---

# 6. 低质量 Query、模糊诉求、冷门目的地，如何避免检索空召回/错召回？

## 这是一个“失败检测 + Query Recovery”问题

不要一看到低分就直接：

```text
再检索一次
```

真正需要区分：

```text
Query 不清楚？
实体没识别？
索引没有资料？
Embedding 不匹配？
过滤条件过严？
拼写/语言问题？
用户问的是实时数据而不是知识库？
```

不同原因对应不同恢复动作。

---

## 第一层：Query Normalization

例如：

> “那个日本北边看雪的小地方住哪比较好？”

先提取：

```text
country = Japan
theme = snow
location = uncertain
intent = hotel recommendation
```

但不要直接猜成札幌然后当事实。

可以构造：

```text
Original Query
+ normalized query
+ entity candidates
```

如果 entity 置信度太低，再最小澄清：

> “你说的是北海道一带，还是东北地区？”

## 第二层：拼写、别名、多语言归一

旅游地名非常常见：

```text
Kyoto / 京都
Jiufen / 九份
Shinjuku / 新宿
Taoyuan Airport / TPE
```

维护 entity alias / canonical ID 往往比单纯换更强 embedding 更有效。

## 第三层：Multi-query Retrieval

对于模糊自然语言，可以生成有限多个 Query：

```text
original
entity-focused
intent-focused
keyword-expanded
```

再融合，不要无限 rewrite。

## 第四层：Fallback Ladder

```text
Hybrid Retrieval
     ↓ low confidence
Relax non-critical metadata filter
     ↓ still empty
Query Rewrite / Alias Expansion
     ↓ still empty
Broader Parent/Directory Retrieval
     ↓ still empty
External Tool / Search（如果允许）
     ↓ still empty
Clarify / explicit no evidence
```

注意：

> 空召回是一个合法结果。

不能为了“必须回答”而降低阈值到随便拿几篇不相关文档。

---

## 错召回比空召回更危险

空召回至少可以告诉用户“当前资料不足”。

错召回会让模型得到一份看起来很可信、实际不相关的证据，从而产生**有引用的幻觉**。

所以建议对 Retrieval 做 Confidence：

```text
top1 score
score gap(top1-top2)
lexical/entity match
reranker score
metadata consistency
source quality
```

再决定：

```text
ANSWER
RETRIEVE_MORE
CLARIFY
NO_EVIDENCE
```

## 冷门目的地的典型处理

用户问：

> “格陵兰某个小镇 11 月有哪些餐厅开门？”

知识库可能根本没有覆盖。

此时正确策略不是把“格陵兰旅游攻略”召回来后猜餐厅营业状态，而是：

```text
knowledge coverage check
        ↓
local KB insufficient
        ↓
real-time/local search Tool（若允许）
        ↓
带来源和时间返回
```

没有外部搜索能力时明确告诉用户：

```text
当前知识库没有足够证据
```

这比错误回答更专业。

---

# 七、把 6 道题放到一条完整 RAG 生产链理解

这六题其实不是六个孤立知识点，而是同一条 Pipeline 的六个故障面：

```text
Raw Documents
    ↓
[Q2] Complex PDF Parsing
    ↓
Logical Document Structure
    ↓
[Q1] Semantic / Hierarchical Chunking
    ↓
Index
    ↓
User Query
    ↓
[Q6] Query Understanding / Recovery
    ↓
[Q3] BM25 + Dense + Metadata + Geo
    ↓
Fusion
    ↓
[Q4] ReRank
    ↓
Temporal / ACL / Version Filter
    ↑
[Q5] Freshness / Conflict Resolution
    ↓
Context Assembly
    ↓
LLM / Agent
    ↓
Answer + Citation + Freshness
```

面试时如果能画出这条链，再把每一道题定位到对应层次，回答就会从“会几个 RAG 名词”上升到“真正设计过检索系统”。

---

# 八、结合 nanobot、AgentDock、OpenViking 怎么回答

## nanobot

nanobot 更偏 Agent Runtime。RAG/Context 结果进入 Runtime 后，最终需要面对：

```text
Retrieved Context
+ Transcript
+ Tool Results
+ System Policy
        ↓
ContextGovernor
        ↓
Model-facing Context
```

因此 RAG 检索到 20 个 Chunk 不意味着 20 个都应该塞给 LLM。检索系统负责“找候选证据”，Context Governor 负责“本轮预算下真正给哪些内容”。

## AgentDock

AgentDock 适合承载平台层的：

```text
Knowledge Connector
Index Version
Tenant/Workspace ACL
Task/Trace
Retriever Config
Embedding/Reranker Version
```

这样多个 Runtime/Driver 可以共享同一套 Knowledge/Index 治理，而不是每个 Agent 容器各建一套不可控知识库。

## OpenViking

OpenViking 很适合解释：

```text
Resource / Memory / Skill
目录组织
层级 Context
L0 / L1 / L2
Retrieval Trajectory
```

尤其可以用来回答：

- 为什么 Context 不应该只有扁平 Chunk；
- 为什么要 Progressive Disclosure；
- 为什么需要看到检索路径，而不只看最终 TopK。

## Pi

Pi 在这组题里不是主要 RAG 实现案例，但它能补充一个边界：检索结果属于本轮 Agent Operation 的输入证据，而 durable execution state、effect state 与知识内容本身是两套不同状态，不要把知识库当 Workflow State Store。

---

# 九、面试高频追问

### 追问 1：Chunk 越小 Recall 一定越高吗？

不一定。太小会丢语义和实体关系，query 与孤立片段反而更难匹配；而且召回后需要更多 Chunk 才能恢复完整证据。

### 追问 2：用了 ReRank 还需要 BM25 + Dense 吗？

需要。ReRank 只能重新排序候选，无法救回 first-stage 根本没有召回的正确文档。

### 追问 3：为什么不用 LLM 判断新旧版本？

因为版本有效性属于确定性规则，应在 Retrieval/Context 层通过 metadata 和时间逻辑处理。让 LLM 在冲突文档中猜有效版本会增加不必要的不确定性。

### 追问 4：没有相关文档时应该怎么办？

把 `NO_EVIDENCE` 当正式状态，而不是强行把低分文档塞给模型。根据任务可选择澄清、外部搜索、Tool 查询或明确回答证据不足。

### 追问 5：PDF 解析错和 Embedding 差怎么区分？

Trace 必须保留 raw page、parsed block、chunk、retrieval score 和最终 evidence。先验证正确事实是否进入 parsed/chunk 层，再看是否被 retrieval 找到；否则很容易把 Parser 的问题误判成 Embedding 问题。

---

# 十、2 分钟综合口述版

> 我把 RAG 当成一个完整的信息检索系统，不只是向量库。文档端先做 layout-aware parsing，复杂 PDF 要分别处理文本块、表格、图片和 OCR，然后按结构和语义做层级 Chunk，而不是固定 500 token 硬切；检索端对 Query 做实体、时间、地理和意图解析，同时走 BM25 和 Dense，必要时叠加 metadata/geo filter，再通过 RRF 融合和 ReRank 排序。评测要分清 first-stage Recall@K 和 rerank 的 MRR/nDCG，最终还要看 groundedness、任务成功率和 token/latency。对于旅游政策、票价、酒店规则，我会把 effective_from/effective_to、source/version 做成硬 metadata filter，实时价格库存直接走 Tool/API，而不是依赖旧知识库。低质量 Query 则用 alias、multi-query、逐级 fallback 和 confidence 判断，实在没有证据就返回 NO_EVIDENCE，不能为了回答而错召回。OpenViking 的 L0/L1/L2 很适合解释分层 Context，nanobot 的 ContextGovernor 则负责检索结果进入 Agent 后怎样受 token budget 治理。