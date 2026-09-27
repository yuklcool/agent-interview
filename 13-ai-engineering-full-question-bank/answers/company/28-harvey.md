# Harvey｜逐题答案

对应原题库公司专项第 28 组，共 11 道。法律判断须由有资质人员复核，答案侧重系统设计。

## HARVEY-01｜Paired coding: write a chunker for a legal document that never splits a clause and carries enough context that a retrieved chunk is self-contained.

先用文档解析识别条款编号、标题、定义、子条款与交叉引用，按最小完整 clause 建节点，超长 clause 按子条款边界拆并保共同父条款/定义链接。chunk 保存文档 ID、页/段 span、层级路径和有效版本；检索时附父标题及相关定义，不任意字符窗口截断。测试表格、脚注、OCR 错位和重号条款。

## HARVEY-02｜A lawyer asks about a 200-page credit agreement where the operative clause on page 140 depends on a defined term on page 8. How do you build retrieval that gets this right?

条款索引除了语义/BM25，还建定义术语→定义 span 和交叉引用图；查 page140 clause 后解析大写定义词，递归拉取 page8 定义及例外，控制依赖深度。生成前把原文与定义并列，回答引用各自页/段；评估跨页依赖召回与是否遗漏否定/例外。

## HARVEY-03｜When would you put a whole contract in the context window instead of retrieving over it? Defend the answer with numbers.

若 200 页约 100k–200k token，按模型价和 prefill 延迟估一次完整读入成本并留输出/工具余量；单合同多处交叉条款且需全局比较可考虑长上下文。大量合同/重复查询或频繁更新则索引检索更省，且能给可审计证据；比较长文位置敏感、引用正确、首 token 和每份审查成本。

## HARVEY-04｜Design an agent that takes a draft NDA and returns a redlined Word document reflecting the firm's playbook, not a chat response.

解析 docx 保留段落/run、表格、编号与批注，firm playbook 版本化成可执行规则/例外；模型只建议变更与理由/引用，先校验不与条款定义冲突。用 Word 修订记录（track changes）插入/删除而非只返回聊天文本，生成前后渲染 diff、文件可打开且格式不坏，律师审批高风险改动。

## HARVEY-05｜Present the architecture for a workflow reviewing 5,000 contracts against an 18-question diligence checklist, returning a review grid.

5000 合同×18 问先批量 OCR/结构解析和权限校验，按问题检索条款+定义，模型返回结构化 {结论、证据 span、置信度、例外}，跨文件聚合 review grid；缺证据/冲突转律师。并行队列、缓存条款表示与幂等重试，记录每格来源/版本；抽样审查漏检、误检、吞吐及成本。

## HARVEY-06｜A new frontier model is released and scores better on your benchmarks. What happens before it reaches customers?

冻结原任务/合同/地区/提示和评测版本，同旧模型比较法律事实、引用、漏条款、playbook 遵循、格式、延迟/成本及安全。律师盲评高风险差异，检查模型输出/工具 schema 变化、数据驻留和供应商条款；影子→小客户灰度→放量，设置回滚和客户通知。

## HARVEY-07｜Every assertion in a Harvey answer needs to link back to a specific passage. Design the grounding system, and tell me how you would measure the unsupported-claim rate.

答案拆成原子断言，要求每句关联原文 clause/span 和文档版本；验证器检查主体、金额、否定、条件与例外，自动支持分类加律师抽样。无支持证据删去或显式不确定，引用必须在用户权限内；unsupported-claim rate=无足够证据断言/全部事实断言，分高风险类型报告置信区间。

## HARVEY-08｜An agentic research query returns a memo citing a case that was overruled. Where does that get caught?

检索时不仅查判例文本，还要查当前有效性/引用关系和权威法律数据库的后续处理标记；生成前验证每个法源的辖区、时间、是否被推翻/限制引用。无法核实就标记并转律师复核，禁止凭模型记忆断言有效；发布后持续更新引证索引和审计。

## HARVEY-09｜Two partners at the same firm are on opposite sides of a deal. Design the data isolation for that, on top of normal multi-tenancy.

除了租户隔离，还按 matter/ethical wall 建隔离域：文档、向量、缓存、日志、工具令牌和人员角色都绑定 matter，检索前后 ACL 校验，跨 matter 共享需正式授权。即使同 firm 两位 partner，也不能通过相似搜索/聚合答案泄露对方资料；用对抗权限矩阵与撤权测试。

## HARVEY-10｜Estimate the cost and turnaround of running your diligence workflow over a 5,000-document data room, and tell me which lever you'd pull first.

设每合同平均 token/页、每问检索证据与模型调用数；总成本=OCR+索引+5000×18×(检索/模型 token)+复核人时/失败重试，吞吐按并发配额与最长合同估完成时间。先抽样 50 份测真实 token/准确与复核负载，再优先复用合同解析/定义和批量缓存，避免对每问重读全文；保质量护栏。

## HARVEY-11｜A partner reports that Harvey missed a change-of-control clause in a contract it reviewed. Debug it.

锁定漏检合同/版本，追踪 OCR→条款切分→索引→召回→重排→提示→结构化输出→review grid 首个丢失点；特别检查标题/定义/同义词、表格和阈值。补该样本及相似条款到回归集，必要时扩大混合召回/交叉引用图并重跑受影响合同，及时通知负责律师。
