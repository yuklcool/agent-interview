# 09｜RAG 与检索系统：从 chunk 设计到多路召回

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/09-rag-retrieval/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 79 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 检索基础与原理

1. **Z2A-09-001** 多维度的查询改写是什么？改写遇到需要用户补充信息时怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L17)

2. **Z2A-09-002** 讲一下项目里召回的流程 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L68)

3. **Z2A-09-003** RAG 的检索如何实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L101)

4. **Z2A-09-004** 并行化意图识别是什么？为什么要并行化？如何实现的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L135)

5. **Z2A-09-005** 如果 RAG 召回了很多相互矛盾的文档，Agent 应该怎么处理，而不是直接让模型自己总结？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L165)

## 检索算法与微调

6. **Z2A-09-006** RAG 中如何提高文档召回率？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L193)

7. **Z2A-09-007** RAG 为什么需要向量检索？和传统关键词检索有什么本质区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L243)

8. **Z2A-09-008** 什么是余弦相似度？在 RAG 系统中用来做什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L285)

9. **Z2A-09-009** RAG 系统检索到的文档很多但回答质量差，怎么排查？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L320)

10. **Z2A-09-010** 如何用通俗易懂的方式向非技术人员解释 RAG？有没有好的类比？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L364)

11. **Z2A-09-011** Embedding 和 ReRank 模型具体怎么做的微调？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L408)

12. **Z2A-09-012** 什么是嵌入（Embedding）？为什么 RAG 系统需要将文本转为向量？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L444)

13. **Z2A-09-013** 双路召回的 TopK，K 是如何确定的？有没有试过一个多召回点、一个少召回点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L505)

14. **Z2A-09-014** 如何快速上手一个没接触过的技术（如向量数据库）？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L533)

15. **Z2A-09-015** 如果用全量生产文档做关联性检索，用户每个问题要交互多少轮？有没有更高效的方案？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L572)

## RAG 在 Agent 中的角色

16. **Z2A-09-016** 在渐进式披露的架构下，还需要 RAG 吗？RAG 的角色会怎么变？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L620)

17. **Z2A-09-017** 如果检索结果很多但质量参差不齐，你会把控制点放在召回、重排，还是 Agent 规划层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L664)

18. **Z2A-09-018** RAG 在 Agent 体系里应该被看成工具、记忆，还是推理前置步骤？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L717)

19. **Z2A-09-019** Agent 场景下，什么时候该做一次检索、多次使用；什么时候该边执行边检索？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L757)

20. **Z2A-09-020** 如果 RAG 返回了看似可信但实际过时的信息，你会怎么降低 Agent 被误导的概率？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L813)

## 召回与排序优化

21. **Z2A-09-021** 为什么在检索阶段引入BM25？它和向量检索怎样组合？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L858)

22. **Z2A-09-022** 如何系统性提升 RAG 的检索相关度与生成效果？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1012)

23. **Z2A-09-023** Rerank 后一般返回几个块？TopK 截断策略怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1096)

24. **Z2A-09-024** RAG 中为什么引入父子索引？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1162)

25. **Z2A-09-025** RAG 系统的端到端性能如何优化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1210)

## 知识库与索引工程

26. **Z2A-09-026** 分块策略怎么设计？不同策略的优缺点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1277)

27. **Z2A-09-027** 知识库整体怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1395)

28. **Z2A-09-028** GraphRAG 在处理 Agent 复杂关联查询时的优势在哪里？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1472)

29. **Z2A-09-029** RAG 召回数据层应如何设计文档、Chunk、Embedding、版本和权限 Schema？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1648)

30. **Z2A-09-030** 向量数据库怎么选型？不同规模下该用什么方案？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1674)

31. **Z2A-09-031** Embedding 模型怎么选？选型时考虑哪些因素？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1720)

32. **Z2A-09-032** 为什么 Claude Code 不用 RAG 检索代码，而是直接用 grep？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1777)

33. **Z2A-09-033** Coding Agent 应从代码反向理解领域知识，还是维护独立知识库/规则库？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1837)

34. **Z2A-09-034** 升级 Embedding 模型后，怎么保证索引和检索向量的逻辑一致性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1858)

## 进阶检索架构

35. **Z2A-09-035** RAG 架构与模型微调（Fine-tuning）相比，各自的适用场景和优缺点是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1931)

36. **Z2A-09-036** 如何处理 RAG 过程中的权限隔离和时效性问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L1984)

37. **Z2A-09-037** PDF 解析用什么工具？Layout-aware Parsing 是怎么做的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2031)

38. **Z2A-09-038** 图检索、向量检索、混合检索有什么区别？怎么选？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2070)

39. **Z2A-09-039** 向量数据库中 IVF_FLAT 和 HNSW 索引的区别是什么？各自适合什么场景？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2111)

40. **Z2A-09-040** Deep Research 在代码层面是怎么实现的？和普通 RAG 有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2159)

41. **Z2A-09-041** Agentic RAG 是什么？和传统 RAG 的核心区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2277)

42. **Z2A-09-042** RAG 检索到的 Chunk 不足以回答问题，后续怎么处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2328)

43. **Z2A-09-043** RAG 知识库的噪声剔除和文档去重怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2384)

44. **Z2A-09-044** 补充检索是如何评估数据质量并触发的？怎么保证二次检索能搜到之前没搜到的内容？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2423)

45. **Z2A-09-045** 向量数据库里两个同义词是什么关系？完全同义的词会在同一个点上吗？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2478)

46. **Z2A-09-046** 多模态 Embedding 检索中，文本语义与图像视觉特征的权重怎么平衡？用户检索图纸参数却召回外观相似零件，根源是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2522)

47. **Z2A-09-047** 向量数据库中需要限定时间范围检索时，标量条件过滤怎么高效实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2580)

48. **Z2A-09-048** RAG 过程中如何处理文件里的图片？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2644)

49. **Z2A-09-049** 随着大模型上下文窗口持续扩容（100K→1M+），传统 RAG 技术是否会被完全替代？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2666)

50. **Z2A-09-050** 如何避免模型回复过度依赖检索到的外部知识，导致回答生硬、缺乏共情能力和自然度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2707)

## ES 切换向量检索的能力变化

51. **Z2A-09-051** 如果从 ElasticSearch 切换到向量检索，哪些能力会下降，哪些能力会提升？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2744)

## 语义切分与文档聚类

52. **Z2A-09-052** 笔试题：多路召回结果合并去重 + 加权排序 + TopK [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2784)

53. **Z2A-09-053** 父文档是怎么得到的？语义切分具体是怎么做的？聚类后怎么区分不同文档？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2846)

54. **Z2A-09-054** 手动干预切片是怎么做的？为什么需要这一步？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2893)

55. **Z2A-09-055** Text2SQL 的 RAG 架构里，DDL 层和规则层分别解决什么问题？业务表频繁变更时怎么保持可用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2925)

56. **Z2A-09-056** RAG 项目里，MySQL 和 Elasticsearch 的数据一致性怎么保证？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L2981)

57. **Z2A-09-057** RAG 文档切分中遇到代码块、表格、标题等特殊内容怎么处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3022)

58. **Z2A-09-058** 处理一万个长文档构建 RAG 知识库，工程上怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3127)

59. **Z2A-09-059** RAG 知识库更新怎么不停服？热更新方案怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3253)

60. **Z2A-09-060** 基于关键词的命令行代码搜索与基于 Embedding/RAG 的代码搜索，各有什么优缺点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3291)

61. **Z2A-09-061** 混合检索到底在哪个环节比单独用效果好？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3333)

62. **Z2A-09-062** RAG 如何防止引用漂移和跨版本证据拼接？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3375)

63. **Z2A-09-063** RAG 前端如何展示长文档，并让引用稳定跳转到原文证据？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3387)

64. **Z2A-09-064** 知识图谱如何从文档构建、增量维护，并处理实体与关系冲突？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3420)

65. **Z2A-09-065** MMR 为什么还能提高效果？重排后为什么还要设置 MMR 截断？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3445)

66. **Z2A-09-066** 知识库持续更新时，如何保证一次 RAG 回答读取同一逻辑快照？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3485)

67. **Z2A-09-067** 如何设计支持版本过滤和时间旅行查询的向量索引？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3497)

68. **Z2A-09-068** 图召回如何缓解热门内容被过度推荐的问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3509)

69. **Z2A-09-069** RAG 检索结果如何安全地组装到提示词中？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3522)

70. **Z2A-09-070** RAG 组装上下文后，如何选择最终生成模型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3535)

71. **Z2A-09-071** 生成教学蓝图时，如何识别语义歧义和超纲内容？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3548)

72. **Z2A-09-072** 视频没有语音时，如何保持检索效果？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3561)

73. **Z2A-09-073** BGE 类文本 Embedding 模型的基本结构是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3574)

74. **Z2A-09-074** RAG 中如何解析文档引用并完成跨文档内容检索？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3590)

75. **Z2A-09-075** 双塔模型与单塔模型的原理、差异和适用场景是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3604)

76. **Z2A-09-076** 如何从技术和工程维度选择两套 RAG 方案？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3618)

77. **Z2A-09-077** 如何设计一个支持图文检索的多模态搜索 Agent？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3632)

78. **Z2A-09-078** 数据库检索与 RAG 检索有什么区别？什么场景下应优先选择数据库检索？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3646)

79. **Z2A-09-079** RRF（Reciprocal Rank Fusion）是什么？如何融合多路检索结果？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/09-rag-retrieval/index.md#L3660)

