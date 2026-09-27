# 07｜工程化踩坑：死循环、状态丢失与成本控制

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/07-engineering-pitfalls/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 72 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 踩坑与经验总结

1. **Z2A-07-001** Agent 的成本怎么控制？线上烧钱太快怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L17)

2. **Z2A-07-002** 开发 Agent 时踩过什么坑？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L56)

### 坑四：成本失控——一个任务烧掉几十块

3. **Z2A-07-003** 为什么很多 Agent Demo 很惊艳，但一上线就不稳定？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L94)

## AI 工具与框架

4. **Z2A-07-004** 平时用过哪些 AI Agent 工具？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L120)

5. **Z2A-07-005** 平时写的代码有多少是 AI 生成的？怎么保证质量？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L144)

6. **Z2A-07-006** 用过哪些 Code Agent？优缺点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L174)

7. **Z2A-07-007** 你熟悉的 Agent 框架，在架构设计上有什么优势？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L248)

8. **Z2A-07-008** 自己做 Agent 时，踩过最大的坑是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L271)

## 代码质量与测试

9. **Z2A-07-009** 如何保证 AI 代码生成的质量与掌控性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L296)

10. **Z2A-07-010** 如何解决大模型 API 服务的响应延迟问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L353)

11. **Z2A-07-011** AI Coding 产品怎么测试？从 Demo 到生产可交付还差什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L407)

12. **Z2A-07-012** 什么是 SDD（Spec-Driven Development）？它和 Skills 有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L447)

## 基础设施与算法

13. **Z2A-07-013** 分布式限流算法——令牌桶、漏桶、滑动窗口的区别和实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L496)

14. **Z2A-07-014** 数据库索引失效的常见场景？LIKE 查询会不会导致索引失效？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L580)

15. **Z2A-07-015** 大规模数据处理场景设计——从千条到百万级如何扩展？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L623)

16. **Z2A-07-016** LangGraph 定义的搜索节点做不到并发执行吗？怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L679)

17. **Z2A-07-017** PostgreSQL 的索引结构是什么？索引如何优化查询速度？在 Checkpoint 场景下如何用索引加速？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L754)

18. **Z2A-07-018** 用 Claude Code 做一个比较长的任务，如果遇到单次 session 跑不完、中间断网怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L824)

19. **Z2A-07-019** 布隆过滤器的原理？会出现什么问题？如何控制误判率？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L878)

## 性能与延迟优化

20. **Z2A-07-020** AI 应用中 SSE 流式数据怎么处理？数据格式是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L948)

21. **Z2A-07-021** 针对包含 3 个以上工具调用且高频请求的任务，通过什么方式可以压低系统整体的端到端延迟？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1027)

22. **Z2A-07-022** AI 应用的前端资源缓存怎么配的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1134)

23. **Z2A-07-023** 开发 Agent 的时候，你用的是什么开发流程？为什么选这个流程？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1170)

### 什么做法是错的

24. **Z2A-07-024** 任务执行远大于单次 Token 限制时，如何设计以支持断点继续生成？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1251)

## 扩展与排查

25. **Z2A-07-025** 用 AI Coding 工具写代码达不到预期怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1372)

26. **Z2A-07-026** AI Coding 检查错误的时间比自己写还长，怎么提效？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1410)

27. **Z2A-07-027** 使用 LangGraph 开发 Agent，遇到最大的困难是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1451)

28. **Z2A-07-028** 模型离线 AUC 很高但上线后效果暴跌，怎么排查？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1513)

29. **Z2A-07-029** Agent 系统的缓存选型——本地缓存 vs Redis，怎么选？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1564)

30. **Z2A-07-030** Agent 异步任务管线中引入消息中间件（如 Kafka），会不会反而变慢或成为瓶颈？扫表和消息驱动各有什么优缺点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1612)

31. **Z2A-07-031** 数据量和 QPS 增大后，Agent 架构怎么改进？需要什么硬件？RT 要求高时怎么部署？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1660)

### Agent 特有的扩容挑战

32. **Z2A-07-032** 高并发场景下同时调 10 个 Embedding 接口，asyncio.gather 相比多线程有什么资源优势？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1701)

33. **Z2A-07-033** LangGraph 的 State Snapshot（状态快照）机制是怎么实现的？解决什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1801)

34. **Z2A-07-034** Agent 系统可观测性设计——怎样的结构才能更好地追踪整个 Trace？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1861)

35. **Z2A-07-035** SSE 流式输出中断后如何保证之前的输出不丢失？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1889)

36. **Z2A-07-036** 产品的用户量、每日 token 消耗和底层模型选型怎么估算？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1911)

37. **Z2A-07-037** Agent 如何做版本管理与灰度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1959)

38. **Z2A-07-038** 怎么设计一个大模型网关系统？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L1980)

39. **Z2A-07-039** 如何设计 Agent 的流式输出以提升用户体验，特别是包含工具调用和多次大模型交互时？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2003)

40. **Z2A-07-040** Claude Code 用久了感觉响应越来越慢，这是什么原因？怎么解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2063)

41. **Z2A-07-041** 高并发场景下，如何设计 Agent 服务的弹性伸缩策略？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2091)

## 流式返回中的非文本事件

42. **Z2A-07-042** 流式返回时，如何插入非文本事件（工具调用标记、思考过程、错误提示、分段标识），且不影响前端渲染？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2114)

## SSE、WebSocket 与单次调用

43. **Z2A-07-043** SSE 和 WebSocket、单次调用的区别是什么？Agent 场景该怎么选？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2169)

## AgentState vs 全局变量

44. **Z2A-07-044** AgentState 的作用是什么？为什么不使用全局变量？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2207)

## 基础工程能力

45. **Z2A-07-045** 多模型如何动态路由？根据视频特征、任务特征、成本、延迟和效果选模型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2245)

46. **Z2A-07-046** 系统里多租户隔离是怎么实现的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2312)

47. **Z2A-07-047** LangGraph 图状态机里，怎么捕获每个节点的执行结果并实时推前端？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2344)

48. **Z2A-07-048** Redis 在 Agent 系统中适合承担哪些职责，哪些数据不应只放 Redis？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2413)

49. **Z2A-07-049** 在浏览器输入一个 URL 到页面显示，完整经历了哪些过程？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2431)

50. **Z2A-07-050** 如何记录 Agent 的非确定性边界，实现可重复的故障回放？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2453)

51. **Z2A-07-051** 进程、线程、协程有什么区别？什么场景下协程更有优势？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2465)

52. **Z2A-07-052** 自动回滚阈值如何设置，避免固定阈值误杀或放过回归？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2504)

53. **Z2A-07-053** 接入多个外部 Agent 时，如何用 Adapter 统一异构事件、工具调用和生命周期协议？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2516)

54. **Z2A-07-054** 从原始诉求到可执行 PRD/Spec，谁负责清洗？如何判断需求完备，质量门禁放在哪层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2543)

55. **Z2A-07-055** 了解 Kubernetes 吗？在 Agent 项目里有没有实际用到？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2572)

56. **Z2A-07-056** 多个子 Agent 延迟退出，同时更新同一对话的 Token 统计数据，线程竞争怎么解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2597)

57. **Z2A-07-057** Agent 框架如何实现流式并行？了解 Claude Code 的流式并行是怎么做的吗？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2689)

58. **Z2A-07-058** 什么是死锁？死锁产生的条件、检测和解决方法是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2773)

59. **Z2A-07-059** 如何设计同时兼顾吞吐、首 Token 延迟和租户公平性的推理调度器？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2796)

60. **Z2A-07-060** 如何设计类似 LangFlow 的 Agent 工作流可视化编排画布？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2812)

61. **Z2A-07-061** 编译器从源代码到可执行程序经历哪些阶段？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2839)

62. **Z2A-07-062** 云端 Agent 的沙盒应该常驻还是按任务创建？如何优化启动和通信开销？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2863)

63. **Z2A-07-063** Agent 的中间与最终交付物应该如何版本化、校验和交接？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2879)

64. **Z2A-07-064** 多模型供应商如何抽象统一 Provider，而不丢失差异能力？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2891)

65. **Z2A-07-065** 如何可靠采集 Coding Agent 轨迹，避免崩溃或异步退出时丢数据？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2903)

66. **Z2A-07-066** 如何统计 Agent 各模块耗时并定位瓶颈？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2916)

67. **Z2A-07-067** 如何估算 Agent 使用模型的月度成本？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2929)

68. **Z2A-07-068** 大型项目重构如何规划，如何处理模块正交与冗余？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2942)

69. **Z2A-07-069** 子 Agent 和工具调用的 Token 用量统计缺失，怎么做容错补偿？（用户断连、子 Agent 延迟退出场景） [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L2962)

70. **Z2A-07-070** 如何保证 AI 生成内容的版权合规并避免侵权？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L3034)

71. **Z2A-07-071** 语音 Agent 如何处理噪声、用户打断与多轮对话？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L3048)

72. **Z2A-07-072** 如何设计面向用户的 AI 服务用量配额、限流与容量规划？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/07-engineering-pitfalls/index.md#L3062)

