# Glean｜逐题答案

对应原题库公司专项第 29 组，共 10 道。

## GLEAN-01｜Merge ranked results from N connector shards into a global top-k, applying a per-user permission filter. Do it efficiently.

每 shard 返回按分数排序候选及 ACL 元数据，用大小 N 的最大堆做 k-way merge，弹出最高项时执行当前用户权限过滤，拒绝后继续拉该 shard 下一个，直到得到 k 个或耗尽；复杂度约 O((k+拒绝数)log N)。高拒绝率需 shard 内预过滤与 overfetch，权限撤销在返回前再校验，分数跨 shard 要校准。

## GLEAN-02｜Walk me through the latency budget of a query: query understanding → retrieval → rerank → LLM answer. Where do you spend and where do you cut?

trace 分查询理解、并行连接器检索、重排和生成，例预算可给检索 200–500ms、重排 100–300ms、LLM 首 token 500–1000ms，按真实 p95 调整。缓存授权安全前缀/热门查询，动态候选 k、并行检索、按任务选模型；不能为了速度省掉 ACL 和证据支持。

## GLEAN-03｜How would you chunk and embed heterogeneous enterprise content: Slack threads, Jira tickets, Google Docs, PDFs?

不同内容保结构：Slack 按线程/时间/参与者，Jira 按 ticket+评论/状态，Docs 按标题/段落/表格，PDF 先 OCR 与页码/阅读顺序。chunk 保父层级、来源、更新时间和 ACL，不跨权限边界合并；以多种内容的 evidence recall、引用页/消息正确与更新延迟验证。

## GLEAN-04｜Why is RAG the right architecture for an enterprise assistant instead of fine-tuning on the company's data? Where does RAG break?

企业知识频繁更新、按用户权限访问且需引用，RAG 可实时检索授权版本；把内容 fine-tune 到共享权重难撤权和追溯。RAG 会在召回失败、相互矛盾、长程关系和源系统延迟时出错，需图关系/定义扩展、冲突处理与拒答；专门格式/流程可用微调补充。

## GLEAN-05｜Design an agent that takes actions in enterprise tools (file a Jira ticket, draft an email) on a user's behalf. How do you handle permissions and evaluate it?

用户意图拆成检索/草稿/写入，tool registry 声明权限/副作用，执行时以用户委托令牌做实时授权，邮件发出或 Jira 创建前预览/确认且带幂等键。评估最终状态、误写/越权、重试恢复和人工接管；模型仅建议参数，不能自己裁定权限。

## GLEAN-06｜Design agent orchestration across dozens of connected SaaS systems. Where is authorization enforced, and why can it not live in the model?

编排器维护计划、状态和工具依赖，连接器统一 schema/错误/速率限制，但每次读写都由工具服务和源 SaaS 以用户令牌授权；模型输出不可信，prompt 不是安全边界。跨系统记录审计与补偿动作，缓存/索引的 ACL 也实时复核；测试用户撤权和恶意文档注入。

## GLEAN-07｜Design a connector framework that syncs content and permissions from 100+ SaaS apps into one index.

连接器框架支持初次全量与增量 webhook/游标、内容规范化、ACL/组成员同步、删除 tombstone、重试/限流和版本化 schema；数据索引原子切换版本，保来源 ID/更新时间。源系统权限语义各异，用契约测试和跨租户红队验证，不把“抓到文本”当同步完成；监控内容/ACL 延迟与失败队列。

## GLEAN-08｜Glean's ranking leans on a knowledge graph of people, content and activity. How would you build that graph, and how does it improve retrieval beyond embedding similarity?

从源系统导入人-团队-文档-项目-互动图，边记录来源/时间/权限并随删除撤销；排序可用作者关系、项目上下文、时效与用户任务特征补 embedding 的语义相似。图特征不能越过 ACL，也要防热门人物/团队偏差；测导航/检索质量的增量和权限泄漏。

## GLEAN-09｜You have dozens of ranking signals and a brand-new tenant with zero interaction data. How do you rank, and how do you improve?

冷租户先用词法/语义相关、文档权威、时效和明确组织结构做稳健排序，权重从跨租户匿名基线迁移但不跨租户泄露数据。早期用少量领域标注/专家反馈及受控探索学习，线上校准点击位置偏差；分新租户/无交互用户测 Recall@k、满意和 p95。

## GLEAN-10｜Design the evaluation framework for an enterprise AI assistant when you cannot look at customer data.

客户数据留在租户环境或以客户允许的盲运行方式执行固定黄金集，系统只收聚合指标/匿名故障类型；客户专家可本地标注相关性、支持/越权案例。评估检索、回答、工具状态、权限与延迟分层，使用差分/隐私聚合时解释其统计误差；生产抽样让客户自行审查并回传聚合反馈。
