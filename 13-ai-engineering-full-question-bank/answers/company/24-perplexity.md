# Perplexity｜逐题答案

对应原题库公司专项第 24 组，共 15 道。

## PPLX-01｜Implement a client pool over multiple LLM providers with failover: providers fail, time out, or rate-limit, and callers should just get a completion.

定义 provider adapter 统一请求/流与错误分类，池按健康度、速率/成本/质量约束选择；超时/429 用指数退避与熔断，失败仅对幂等、尚未向客户输出的请求安全切换。流式中途失败需显式中断或带版本续传，不能拼接不同模型结果伪装无缝；分租户配额、追踪与可观测性，测试全挂与慢供应商。

## PPLX-02｜You're ingesting millions of web pages a day. Detect near-duplicates (same article, different boilerplate) efficiently.

抽取正文去导航/模板，按段落 shingles 做 MinHash/LSH 或 SimHash 候选，候选再比较内容相似度，保留 URL、发布时间与权威版本。分语言/域去重，不能把转载更新/纠错误删；百万页/日分片流式处理、近似索引控制内存，人工抽样估误并记录簇。

## PPLX-03｜You need to embed millions of text chunks. The embedding service takes batches with a max batch size and a max total-token limit. Write the batcher and make it fast.

按长度先快速 token 计数，贪心填充 batch，使 `len(batch)≤B` 且 token 总数≤T；超长 chunk 明确切分/拒绝。多 worker 队列分配 batch，支持异步调用、429 退避、幂等 chunk ID 与结果按原序归位；测吞吐/填充率/p95，按长度分桶减少 padding，但避免长条目饥饿。

## PPLX-04｜Implement beam search for an autoregressive model. When would an answer engine actually use it?

beam search 每步扩展 B 个部分序列到词表，累加 logprob 并保留分数最高的 B 个，EOS 完成候选与未完成分开，长度归一和早停防短答案偏好；时间约 O(T·B·V) 排序可 top-k 优化。答案引擎开放式事实问答通常优先采样/确定性解码+检索验证，beam 更适合约束翻译/短结构序列，避免重复模板。

## PPLX-05｜p95 time-to-first-token regressed from 1.2 s to 3 s after a release. Walk me through finding and fixing it.

按发布前后 trace 分解 DNS/检索、rerank、队列、prefill、首 token 与流式网络，比较请求长度/缓存命中/模型版本和机房切片，先检查流量混合/实验分桶。用回滚或影子复现实验确认首个退化点，针对根因调 cache、batch/排队或 prompt 长度；质量和成功率设护栏，不能以空 token 伪降 TTFT。

## PPLX-06｜Discuss reranker architecture choices: cross-encoder, ColBERT, LLM-based.

cross-encoder query+doc 联合编码，质量高但每候选成本高；ColBERT 多向量晚交互可预索引 doc token，质量/速度折中但索引大；LLM reranker 可做复杂证据判断，最慢且需约束输出/稳定性。按召回候选规模、预算和语言/领域分层，先轻重排再高价值 query 上 LLM；测 nDCG、引用正确与 p95。

## PPLX-07｜You retrieved 50 candidate passages but the model's useful context budget is ~10. How do you choose, and how do you know your choices are good?

先按 query 子问题覆盖做文档去重/聚类，过滤权限和过期页，基于相关性、权威、新鲜度与互补性选 10 篇，可用 MMR 或集合覆盖目标，留反证/不同观点。人工标注“回答所需证据集合”测 evidence recall、答案支持率与反事实去掉文档的影响；位置排序和长文截断另测。

## PPLX-08｜Design an answer engine: a user types a question and gets a cited, streamed answer. Your end-to-end budget is 3 seconds to a complete short answer.

查询理解与改写并行检索多源，缓存热门结果，召回→轻重排→挑证据→小/快模型流式生成并逐句附引用；预算例：入口/检索 300–700ms、重排 200–400ms、生成约 1–2s，余量留 p95 抖动，需真实压测。新鲜/高风险查询提高核查而非硬凑 3 秒，证据不足清楚说明。
```mermaid
flowchart LR
 A[问题] --> B[并行检索]
 B --> C[重排/证据]
 C --> D[流式回答]
 D --> E[逐句引用验证]
```

## PPLX-09｜Design the retrieval pipeline pulling from 100B web pages with sub-second latency and freshness guarantees.

100B 页全量索引需分层：热/近期内容增量抓取、冷历史分片词法倒排与向量/压缩索引；路由先定位主题/语言/时间 shard 并并行搜索，层级合并 top-k。抓取→解析去重→版本化发布与删除传播，按事件时间 SLA 测 freshness 分布；亚秒检索需缓存/近域部署与 p95 控制，不能承诺全网页即时更新。

## PPLX-10｜Design the ranking system combining BM25, dense retrieval and LLM reranking across multiple indexes.

各索引 BM25/向量检索得候选，做分数校准或 RRF 融合后按权限/新鲜/域规则重排，cross-encoder/LLM 对有限集合精排。对新闻/学术/购物不同 query 动态设源配额，防某索引淹没其它；分层 Recall@k、nDCG、引用支持率、p95 与线上点击/满意度实验。

## PPLX-11｜Design Comet's hybrid browser architecture combining on-device privacy with cloud AI assistance.

浏览器本地保历史、cookie、密码与网页权限；本地模块负责页面解析/敏感字段识别和授权提示，云端只收执行任务所需最小上下文与短期会话 token。工具层域名权限、写操作确认、网页注入隔离和审计，允许完全本地/禁云模式；评估完成率、数据传输量、隐私泄漏和网络故障恢复。

## PPLX-12｜How does an answer engine handle breaking news: a query about something that happened 20 minutes ago?

先走新鲜索引/官方原始来源，检查时间戳、事件发生时间与时区；并行找独立来源核对关键事实，未证实说“目前报道”并附来源与更新时刻。旧缓存设 TTL 和更正机制，删除/撤稿传播；生成时区分已确认事实和推测，遇冲突给并列证据，测 20 分钟内召回与误报。

## PPLX-13｜How would you evaluate answer quality for an answer engine, continuously and at scale, with both automated and human signals?

固定黄金集覆盖事实、复杂综合、无答案和最新事件，自动判引用可达/支持、完整性、矛盾与延迟，判分器定期人工校准；真人盲评事实性、帮助度和来源多样性。线上采样纠错/引用点击/满意度，按语言/主题/时效切片，严重错误独立审查，防只优化容易自动评分的题。

## PPLX-14｜Design the citation-verification system to reduce hallucinations in generated answers. How do you ensure every claim is actually supported by its cited source?

把回答拆成原子主张，逐条映射引用的 passage/span，检查主体、数字、时间与否定关系，NLI/LLM 验证器提供候选，人工抽样校准；无证据的主张删除、改为不确定或补检索。引用 URL 可达不等于主张被支持；以 unsupported claims / all factual claims、严重错误率与误报率衡量。

## PPLX-15｜What makes a Perplexity answer great vs mediocre? Where does Perplexity lose to traditional search, and where does it win? You clearly use it: what's broken, and what would you ship to fix it?

优秀回答应准确、完整、及时、可追溯且篇幅适合；传统搜索在导航、原始页面探索与高歧义/动态内容有优势，答案引擎在跨来源综合省时间。现场要用自己实际遇到的错例，记录 query/时刻/证据，再提出如逐句证据验证或新鲜度显示的最小改动、验收指标和风险；别假称个人使用经历。
