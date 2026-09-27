# Cohere｜逐题答案

对应原题库公司专项第 7 组，共 10 道。

## COHERE-01｜Design a token-based rate limiter for a multi-tenant LLM API. Implement the core, then tell me what changes when it's distributed.

单机用每租户 token bucket：保存余额和上次更新时间，`tokens=min(capacity,tokens+rate*elapsed)`，按预计输入+最大输出预留，生成结束退还未用额度。分布式原子状态在 Redis Lua/配额服务，复用请求 id 保幂等；额外限制并发占用的 KV、模型权重和突发，防小请求与长输出不公平。超时、重试和跨地域网络分区时定义 fail-open/closed 策略，返回 retry-after。

## COHERE-02｜Our flagship is a sparse MoE with ~10x more total than active parameters. Why is that architecture a good fit for private enterprise deployment, and where does it hurt?

稀疏 MoE 以部分活跃专家获得较高总容量且每 token 计算较低，适合多个企业任务/语种共存；私有部署的难点是**全部专家权重仍需显存/存储**，小 batch 路由不均与专家并行通信会损害吞吐。评估单租户低并发、GPU 数、量化后的质量和故障恢复；不把参数活跃比例等同总拥有成本。

## COHERE-03｜You have an embedding model and a reranker. Why sell both? Design the two-stage retrieval pipeline and tell me when the reranker earns its latency.

embedding 做高召回 ANN，reranker 对少量候选做 query-document 深交互以提高排序精度。先 ACL/元数据过滤，混合词法与向量召回 k=100–500，再对候选重排、截取证据交生成模型；测 Recall@k、nDCG、答案引用和 p95。复杂查询/高价值回答通常值得重排，简单导航查询可跳过或动态减 k；绝不能让重排恢复召回阶段漏掉的文档。

## COHERE-04｜An enterprise wants semantic search over ~100M documents but is balking at vector-index cost. Walk me through embedding compression options and the maths.

原始 float32 向量成本 `N×d×4`；1 亿条、1024 维即约 409.6GB 原始向量，尚不含索引和副本。降维 1024→256 约四分之一；float16 约减半；8-bit PQ 如每向量 64B，纯码约 6.4GB，加粗聚类、ID、元数据和多副本。可选 OPQ/PQ、标量量化、磁盘 ANN、冷热分层，但用按语言/租户 Recall@k、检索时延和重排质量验证，不只看压缩率。

## COHERE-05｜How would you evaluate multilingual retrieval quality when employees query in French and Korean over mostly-English documents?

建立法/韩查询与英文文档的人工相关性集，包含专名、缩写、跨语概念及无答案案例；同语和跨语分开测 Recall@k、nDCG、MRR 和权限过滤。比较多语 embedding、查询翻译、双路召回与多语 reranker；译文可能丢实体，保留原文路径。人工双语审核答案证据与语义，按语言、业务域和脚本切片监控线上零结果率。

## COHERE-06｜A customer 10x'd their indexed documents and reports answer quality “got noticeably worse.” Drive the investigation.

先复现并固定查询/用户权限/索引版本，拆分检索 Recall@k 与生成质量；文档暴涨可带来 ANN 参数退化、分片热点、噪声候选、重复文档、过期 ACL 或重排截断。抽样分析新旧数据分布、索引召回与过滤顺序、top-k 命中；调分层索引/参数、去重、混合召回和重排容量。回放旧查询与新查询，比较质量、成本、延迟后灰度。

## COHERE-07｜Design an agent that automates an enterprise workflow, say, drafting RFP responses from internal documents and a CRM. What does “enter-prise-grade” add?

RFP 任务按问题拆分→内部文档和 CRM 权限检索→证据引用→草稿→人工审批→写回。企业级要求用户身份透传到每条检索和工具调用、租户隔离、外部内容注入防护、PII/合同保密、版本追踪、可撤销与审计；CRM 写入是显式授权的事务。评估引用真实性、政策正确性、审批负载、失败恢复和每份 RFP 节省时间。

## COHERE-08｜A bank wants the whole stack (model, RAG, agents) deployed air-gapped on their own GPUs. What actually changes versus your SaaS?

气隙环境中模型、向量索引、embedding、reranker、OCR、依赖包和监控都必须本地化；交付签名离线制品和 SBOM，更新经人工导入扫描。对接本地 IdP/KMS/审计，离线文档增量同步和 ACL 撤销，容量按峰值 GPU/KV 预留，内网灾备与镜像回滚。评测与标注不能依赖外部服务，验证无外联并压测安全/性能。

## COHERE-09｜An enterprise customer wants to deploy your RAG system but has no labelled data. How do you evaluate it before and after launch?

先从业务流程抽样真实查询，让领域专家标注少量“可回答、相关文档、正确答案、禁止访问”黄金集；无标注时用合成查询做覆盖探索，但必须人工抽检，不能只用 LLM 自评。上线前看检索 Recall@k、引用支持率、权限泄漏、拒答与延迟；上线后记录反馈、人工复核和抽样盲评，事故进入固定回归集。

## COHERE-10｜Tell me about a time you owned an ambiguous problem end-to-end without much direction.

按个人真实案例讲 STAR：界定模糊目标和谁能决定，拿基线/用户访谈缩小范围，选最小可检验里程碑，明确跨团队接口与风险，展示指标和结果；如结果不理想，交代复盘。不要虚构自己做过的系统或影响数字。
