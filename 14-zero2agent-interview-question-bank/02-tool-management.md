# 02｜工具管理：参数校验、工具路由与百级工具库

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/02-tool-management/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 40 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 参数校验与工具路由

1. **Z2A-02-001** 工具描述写得再好，模型也瞎传参数怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L17)

2. **Z2A-02-002** 你们工具库有上百个工具，怎么让模型快速选对？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L49)

3. **Z2A-02-003** 多工具场景下的调度策略？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L89)

## 工具返回与中间层

4. **Z2A-02-004** 工具多导致 token 数过多，怎么解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L113)

5. **Z2A-02-005** Mock 是怎么实现的？在自动化生成测试的场景下 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L164)

6. **Z2A-02-006** 如果工具调用是成功的，但返回结果语义不完整，模型很容易误判，你怎么设计中间层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L203)

## MCP 与 Function Calling

7. **Z2A-02-007** 大模型的 Function Call 是什么？Tool Use 一般怎么用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L278)

8. **Z2A-02-008** MCP 和 Skills 的本质区别是什么？都是工具调用，为什么需要两套机制？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L394)

9. **Z2A-02-009** MCP Server 是怎么构建的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L458)

10. **Z2A-02-010** Function Calling 的本质价值是什么？它解决的是“模型能力问题”还是“系统约束问题”？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L500)

11. **Z2A-02-011** 大厂开源的 CLI 工具（如 lark-cli）和 MCP 有什么区别？它们跟直接调 API 又有什么不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L542)

## 工具设计与实现

12. **Z2A-02-012** 手撕一个 ReAct 架构的 Agent，实现文件操作（找文件、删除文件） [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L609)

13. **Z2A-02-013** 同一个能力是做成“一个大而全工具”还是“多个小工具”，怎么权衡？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L717)

14. **Z2A-02-014** 你会如何设计工具 schema，才能降低模型传错参数、漏参数、乱调用的问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L749)

## 高级工具调度

15. **Z2A-02-015** MCP 协议的完整调用过程是怎样的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L798)

16. **Z2A-02-016** LLM 是怎么从用户意图匹配到具体工具参数的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L879)

17. **Z2A-02-017** 如何在多智能体环境中实现动态发现并注册跨协议工具？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L943)

18. **Z2A-02-018** 为什么将 Agent 工具注册到微服务注册中心（如 Nacos）而不是用 MCP？工具的自动注入怎么实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1026)

19. **Z2A-02-019** Agent 做多轮工具调用和单轮调用相比，会面临哪些额外挑战？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1063)

20. **Z2A-02-020** 多工具场景下怎么定工具调用的优先级？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1126)

21. **Z2A-02-021** 推理模型（如 o1/DeepSeek-R1）为什么不支持工具调用？技术原因是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1147)

22. **Z2A-02-022** 开源模型的 Function Calling 能力较弱，如何通过微调或 Prompt Engineering 提升？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1167)

## Skill 边界模糊时的工具披露

23. **Z2A-02-023** 对于边界不好定义的场景，Skill 形式不能很好区分场景披露工具，怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1214)

## 多 Skill 串行嵌套的容错设计

24. **Z2A-02-024** 工具返回了非常大的数据超出了大模型的上下文窗口，怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1247)

25. **Z2A-02-025** 多 Skill 串行/嵌套时，依赖冲突、参数不兼容怎么做容错？有无编排优先级调度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1276)

26. **Z2A-02-026** 你们有没有用 MCP？为什么要把 OAuth2.1 接到 MCP 里？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1311)

27. **Z2A-02-027** 没有 MCP 之前大模型调用工具走的是什么流程？MCP 本身有什么缺点或者挑战？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1353)

28. **Z2A-02-028** 一个 Agent 如何同时连接多个 MCP Server，并保证用户与会话隔离？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1396)

29. **Z2A-02-029** MCP 返回结果支不支持流式？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1417)

30. **Z2A-02-030** Tool-use SFT 的训练目标是什么？基座模型已经具备工具调用能力时，SFT 还需要学习什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1448)

31. **Z2A-02-031** Agent 调用启动较慢的外部工具时，如何设计异步任务和结果回调？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1491)

32. **Z2A-02-032** MCP 工具治理为什么需要审计？应该审计哪些证据？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1507)

33. **Z2A-02-033** Tool Result 回写模型时，消息契约应该包含哪些字段？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1522)

34. **Z2A-02-034** 如何评测 MCP Server / Tool 自身的契约、可用性和效果，并用轨迹 Badcase 持续迭代？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1536)

35. **Z2A-02-035** CLI、Skill 和 sub-agent 应该如何划分职责？CLI 直接调用 LLM 与 Skill 拉起 sub-agent 有什么差异？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1575)

36. **Z2A-02-036** 跨平台工具授权即将过期时，Agent 如何调整调用顺序并安全续权？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1606)

37. **Z2A-02-037** 如何不用多智能体方案让 1000 个 Tools 正常工作？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1618)

38. **Z2A-02-038** 当治理规则需要修改服务代码时，如何安全落地？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1665)

39. **Z2A-02-039** Agent 中 Skill 与 Tool 的职责边界和选型标准是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1681)

40. **Z2A-02-040** 工具调用结果如何在 Agent 工作流中直接传递？什么情况下需要 LLM 参与中转？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/02-tool-management/index.md#L1695)

