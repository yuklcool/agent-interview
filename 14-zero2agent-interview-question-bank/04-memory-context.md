# 04｜记忆与上下文：长对话不丢信息的实战方案

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/04-memory-context/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 66 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 上下文管理基础

1. **Z2A-04-001** 上下文窗口不够用，对话太长了怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L17)

2. **Z2A-04-002** 长上下文里，怎么让 Agent 不忘记关键信息？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L89)

3. **Z2A-04-003** 多 Agent / 多异步任务下，如何防止上下文污染？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L123)

4. **Z2A-04-004** 用户说“按老样子帮我订一下”，这种模糊需求怎么处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L156)

## 记忆架构与优先级

5. **Z2A-04-005** 讲一下 Agent 中的“长短期记忆” [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L177)

6. **Z2A-04-006** 一个 Agent 系统里，什么时候应该追问用户，什么时候应该自己继续推理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L222)

7. **Z2A-04-007** 你怎么理解 Agent 里的“状态”而不是“上下文”？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L287)

8. **Z2A-04-008** Agent 需要同时读知识库、调外部 API、结合用户历史偏好，怎么处理这三类上下文的优先级？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L313)

9. **Z2A-04-009** 对于上下文工程有什么经验？有没有做过 to-do list？为什么让模型更聚焦？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L339)

## 记忆系统工程

10. **Z2A-04-010** Agent 记忆系统里的「做梦机制」（Dreaming）是什么？和 Reflection 有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L373)

11. **Z2A-04-011** 如何处理记忆的“新鲜度”与“重要性”之间的冲突？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L403)

12. **Z2A-04-012** 设计一个能支持亿级用户、千亿级记忆条目的 Agent 记忆系统，你会如何做技术选型和架构设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L434)

13. **Z2A-04-013** Agent 的记忆可能存在偏见（Bias）或事实性错误，如何发现并纠正？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L462)

14. **Z2A-04-014** 如何沉淀部门级 Agent 记忆，既避免经验随人流失，又控制错误、过期和权限风险？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L488)

15. **Z2A-04-015** 什么是记忆的 Reflection 机制？它与简单的 Summarization 有何不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L517)

16. **Z2A-04-016** 在实现长期记忆时，什么情况选向量数据库，什么情况选传统的 KV 或关系数据库？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L550)

17. **Z2A-04-017** 什么是记忆的幻觉问题？它和 LLM 本身的幻觉有何区别？如何缓解？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L579)

18. **Z2A-04-018** 什么是“工具态记忆”（Tool-state Memory）？它在 Agent 工作流中如何发挥作用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L603)

19. **Z2A-04-019** 记忆的容量规划需要考虑哪些因素？如何估算存储成本？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L630)

## 记忆检索与维护

20. **Z2A-04-020** 如何判断当前对话与历史对话是否相关？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L684)

21. **Z2A-04-021** 你会如何判断一条历史信息该进入长期记忆，还是只留在当前会话里？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L734)

22. **Z2A-04-022** 记忆摘要、压缩、去重、合并这几件事，你会怎么设计触发时机？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L768)

23. **Z2A-04-023** 长期记忆检索时，怎么避免把“语义相关但当前无用”的内容召回进来污染理解？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L816)

24. **Z2A-04-024** 如果用户偏好、事实记忆、系统状态三者冲突了，Agent 应该信谁？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L849)

## 上下文工程进阶

25. **Z2A-04-025** 如何减少无关上下文对模型的干扰？当前上下文有哪些优化思路？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L893)

26. **Z2A-04-026** 摘要总结往往会丢失关键细节，在长文本 Agent 中一般怎么来处理这一块？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L965)

27. **Z2A-04-027** Code Agent 的上下文工程，和普通对话 Agent 相比有哪些独特挑战？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1025)

28. **Z2A-04-028** 在电商或导购场景下，用户的请求往往高度模糊，Agent 怎么来精准理解这种需求？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1065)

29. **Z2A-04-029** Agent 的 Checkpoint 用什么数据库存？初始化 session 时如何优化加载 Checkpoint 的速度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1116)

30. **Z2A-04-030** 做上下文工程最关键的工作是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1200)

## 会话记忆与前沿

31. **Z2A-04-031** 会话记忆具体是怎么实现的？滑动窗口设几轮？摘要压缩怎么触发？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1253)

32. **Z2A-04-032** 有没有了解过最前沿的记忆设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1311)

33. **Z2A-04-033** 设计会话记忆系统时需要考虑哪些维度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1416)

34. **Z2A-04-034** Claude Code 的记忆架构是什么？上下文真的等于记忆吗？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1456)

35. **Z2A-04-035** 什么是上下文缓存（Prompt Caching）？它在 Agent 系统中有什么价值？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1518)

36. **Z2A-04-036** 长周期对话（间隔数周后继续）如何管理历史？冷启动怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1549)

37. **Z2A-04-037** 你的向量记忆库是如何更新用户画像的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1590)

38. **Z2A-04-038** 用户对话中频繁切换话题，会话记忆该怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1646)

39. **Z2A-04-039** Lost in the Middle 问题是什么？有哪些解决方案？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1708)

40. **Z2A-04-040** 怎么判断当前用户的提问需不需要去检索长期记忆？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1754)

41. **Z2A-04-041** 怎么实现多轮对话过程中，根据用户反馈自我调整的功能？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1793)

42. **Z2A-04-042** 基于滑动窗口对最近 N 轮进行摘要时，是将之前摘要和新摘要合并还是分别保留？各自适合什么场景？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1847)

43. **Z2A-04-043** 如果让你设计一个三层记忆机制，你会如何设计？从整体架构和具体压缩方法进行描述。 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1891)

44. **Z2A-04-044** 压缩过程中会丢失工具调用历史，导致模型重复调用工具，怎么解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1971)

45. **Z2A-04-045** 记忆冲突怎么解决？比如用户前后说了不同的过敏信息 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L1992)

46. **Z2A-04-046** 短期记忆压缩后，过了很长时间又需要当时完整信息怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2011)

## Prompt 长度 vs 内容对决策的影响

47. **Z2A-04-047** 为什么要区分静态长期记忆和动态长期记忆？各自存什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2034)

48. **Z2A-04-048** 每轮对话都触发长期记忆存储，用户记忆快速积累、存得过多怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2087)

49. **Z2A-04-049** 如何判断是 Prompt 内容影响了决策，还是 Prompt 太长导致注意力涣散影响了决策？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2162)

50. **Z2A-04-050** 云端 Coding Agent 的容器迁移或重启时，如何恢复会话上下文、工作区和进行中的任务？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2196)

51. **Z2A-04-051** 上下文预算不足时，如何按任务依赖压缩，而不是按时间删除旧消息？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2212)

52. **Z2A-04-052** 跨会话记忆如何从对话中提取？哪些信息值得写入长期记忆？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2229)

53. **Z2A-04-053** 前 10 轮都变成了总结，之前的原始上下文就不需要了吗？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2254)

54. **Z2A-04-054** 当用户对话零碎、跨轮次且意图发生跳跃时，如何结合上下文准确判断当前意图？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2303)

55. **Z2A-04-055** Agent 做上下文压缩后，如何验证没有破坏当前任务？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2357)

56. **Z2A-04-056** 为什么长视频通常需要切片和分阶段处理，而不是一次性输入大模型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2382)

57. **Z2A-04-057** 已进行 10 轮并做了总结，第 11 轮开始时，总结怎么处理？是重算前 11 轮还是叠加？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2401)

58. **Z2A-04-058** session 里的临时文件存主服务还是 skill 进程服务，要不要删，什么时候删？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2457)

59. **Z2A-04-059** 如何用 Prompt 提取用户风格偏好？风格偏好应包含哪些内容？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2507)

60. **Z2A-04-060** Codebase Memory 应该如何初始化、增量更新和失效？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2535)

61. **Z2A-04-061** 大体积工具结果落盘后，为什么还要返回预览？预览内容应该如何选择？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2551)

62. **Z2A-04-062** 大模型生成会话摘要时，如何避免摘要内容污染用户偏好？新结论推翻旧结论时怎么保留？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2575)

63. **Z2A-04-063** 金融 Agent 执行股价提醒等定时任务时，应该携带哪些历史上下文？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2603)

64. **Z2A-04-064** 按大纲分章节生成长文时，如何维持跨章节连续性与事实一致性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2619)

65. **Z2A-04-065** Work Memory 如何设计与更新？为什么能提升 Agent 的任务执行效果？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2650)

66. **Z2A-04-066** 大模型输出过长时如何进行长度控制与内容压缩？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/04-memory-context/index.md#L2664)

