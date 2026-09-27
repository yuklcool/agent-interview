# 01｜架构选型：ReAct、Plan-and-Execute 与 ToT 怎么选

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/01-architecture-design/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 50 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 推理范式与架构选型

1. **Z2A-01-001** 你用 ReAct 还是 Plan-and-Execute？为什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L17)

2. **Z2A-01-002** Tree of Thoughts (ToT) 在线上系统里能用吗？成本不高？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L96)

## Agent 组成与设计边界

3. **Z2A-01-003** Agent 的架构设计？从系统角度来拆分 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L117)

4. **Z2A-01-004** 了解过 Agent 的设计范式吗？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L143)

5. **Z2A-01-005** Agent 在学术上由哪些部分组成？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L201)

6. **Z2A-01-006** 如果让你设计一个 Agent 的规划器，怎么避免它每一步都重新规划，导致路径震荡？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L226)

7. **Z2A-01-007** 如果模型特别擅长生成，但不擅长严格遵守流程，你会怎么把它放进一个强约束工作流里？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L249)

## 系统设计原则与模式

8. **Z2A-01-008** 什么时候该做 Agent？和 Workflow 的边界在哪？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L277)

9. **Z2A-01-009** 生产级 Agent 的执行循环包含哪些阶段？哪些必须显式状态化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L314)

10. **Z2A-01-010** 现在的 Agent 架构和之前有什么本质不同？渐进式披露是什么思路？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L357)

11. **Z2A-01-011** 设计一个 AI Agent 爬取短视频平台内容，如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L400)

12. **Z2A-01-012** Agent 系统里，模型和系统代码的职责边界怎么划？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L447)

13. **Z2A-01-013** 如果面试官说“Agent 本质上就是套壳调用工具”，你怎么反驳？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L478)

14. **Z2A-01-014** 为什么很多团队做到最后是“Workflow + Agent 节点”的混合架构？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L500)

15. **Z2A-01-015** 什么样的任务适合先全局规划再执行，什么样的任务更适合边走边决策？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L532)

## 系统集成与规划保障

16. **Z2A-01-016** Skill、MCP、Rule 三者有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L568)

17. **Z2A-01-017** Agent 的任务规划是怎么做的？规划由模型完成还是规则实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L657)

18. **Z2A-01-018** 如何保证规划 Agent plan 的结果正确？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L722)

19. **Z2A-01-019** 微服务怎么接入一个 Agent 系统？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L764)

20. **Z2A-01-020** 规划完成后需要人工介入修改大纲，SSE 怎么实现这种 Human-in-the-Loop？前端怎么让用户输入？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L823)

## 场景设计与可靠性

21. **Z2A-01-021** LangChain 和 LangGraph 有什么区别？分别适合什么场景？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L903)

22. **Z2A-01-022** 模型和 Agent 的区别到底是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L950)

23. **Z2A-01-023** 如果设计一个科研辅助 Agent，整体流程应该怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1004)

24. **Z2A-01-024** Agent 的 Self-Reflection 机制是什么？它怎么识别输出中的逻辑错误？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1085)

25. **Z2A-01-025** 场景题——如果有一个监控日志，给 Agent 分析，需要得到分析结果，怎么设计这个 Agent？怎么设计工具？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1132)

26. **Z2A-01-026** 设计一个智能导购助手 Agent，描述其感知、规划、记忆和执行四大模块在分布式架构下的协同逻辑 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1202)

27. **Z2A-01-027** 多角色智能客服场景（B/C/D 端），用 RAG 还是 Skill？怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1289)

28. **Z2A-01-028** 在“推理-行动”循环中，如何设计来纠正逻辑塌缩或无效工具调用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1342)

29. **Z2A-01-029** 如何保障自然语言任务描述能精准转化为稳定、可靠的执行路径？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1411)

30. **Z2A-01-030** Skill 和 Workflow 的区别是什么？什么场景该用 Skill 而不是 Workflow？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1456)

31. **Z2A-01-031** DAG 与含循环图在 Agent 编排中的区别和适用场景 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1517)

32. **Z2A-01-032** 基于强化学习的 Agent 与传统基于 Prompt 的 Agent 有何区别？各自的适用场景？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1545)

## Agent 中间件（Middleware）

33. **Z2A-01-033** AI 系统该做单域工具还是跨团队通用平台？怎么选？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1579)

34. **Z2A-01-034** 讲一讲 Agent 的 Middleware（中间件）是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1617)

35. **Z2A-01-035** Coding Agent 的完整链路是怎么运转的？从用户输入到代码产出的全流程 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1664)

36. **Z2A-01-036** 只有模型 API 和 VS Code，如何从零搭建一套可用的 Agent 应用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1720)

37. **Z2A-01-037** 用拓扑排序（规则式）管理任务依赖 vs 让大模型自己推理决策执行顺序，各有什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1738)

38. **Z2A-01-038** Agent 如何判断已经收集了足够的信息，最终给出输出结论？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1807)

39. **Z2A-01-039** Agent 的 thinking 阶段怎么决定是调用工具还是直接回复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1844)

40. **Z2A-01-040** 设计一个内部的多源文档问答 AI，架构设计是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1881)

41. **Z2A-01-041** ReAct 在工程实现中，消息和状态协议应该怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1931)

42. **Z2A-01-042** Agent 如何持续推进 Goal，并避免行为漂移和目标漂移？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1960)

43. **Z2A-01-043** 在 AI/Agent 辅助编码时代，为什么 DDD 和清晰的领域边界反而更重要？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1976)

44. **Z2A-01-044** Agent 组件拆解为什么适合责任链模式？与状态机、DAG 的边界是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L1992)

45. **Z2A-01-045** 设计一个预订机票的 Agent，如何处理澄清、支付确认和失败补偿？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L2024)

46. **Z2A-01-046** AI Coding Agent 的 Solo 模式和 Plan 模式应该如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L2036)

47. **Z2A-01-047** 什么时候需要自研或改造方案，而不是直接采用开源实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L2051)

48. **Z2A-01-048** 自研业务 Agent 与基于通用 Base Agent 开发插件，如何进行架构选型？各有什么优缺点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L2067)

49. **Z2A-01-049** 如何设计多用户 AI 服务接入、配置隔离与模型路由？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L2081)

50. **Z2A-01-050** 交易系统如何选择直连第三方支付还是统一支付抽象层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/01-architecture-design/index.md#L2095)

