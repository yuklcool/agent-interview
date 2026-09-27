# 06｜多智能体协作：角色分工、通信机制与冲突仲裁

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/06-multi-agent-collab/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 35 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 多 Agent 协作基础

1. **Z2A-06-001** 多智能体怎么协作？比如一个写代码一个审查 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L17)

2. **Z2A-06-002** 多 Agent 系统里，怎么防止 Agent 之间“踢皮球”或死循环？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L39)

3. **Z2A-06-003** 多 Agent 之间需要共享状态吗？怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L58)

## 单多 Agent 决策与模式

4. **Z2A-06-004** 怎么判断一个 Agent 该做成单 Agent，还是多 Agent？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L80)

5. **Z2A-06-005** 在多 Agent 协作系统中，记忆应该如何共享？是全局共享还是每个 Agent 独立？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L102)

6. **Z2A-06-006** 单 Agent 还是多 Agent 的？子 Agent 的任务是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L145)

7. **Z2A-06-007** 多 Agent 设计里，按“职能拆分”和按“阶段拆分”各有什么优缺点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L173)

## 通信协议与 Handoff

8. **Z2A-06-008** MCP 和 A2A 分别解决什么层面的问题？如果系统同时用了两者，架构上怎么分工？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L224)

9. **Z2A-06-009** Handoff 的核心难点是什么？是路由问题、状态传递问题，还是权限边界问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L277)

## SubAgent 设计

10. **Z2A-06-010** 什么时候该用 subagent？为什么工具调用多就倾向用 subagent？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L324)

11. **Z2A-06-011** 任务简单但工具调用多，用 subagent 是否浪费 token？怎么解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L391)

12. **Z2A-06-012** 图片信息怎么在 subagent 之间流转？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L421)

## 编排与路由

13. **Z2A-06-013** Multi Agent 系统中 Router 节点依据什么规则把任务分给子 Agent？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L474)

14. **Z2A-06-014** 多 Agent 怎么编排的？用的什么编排模式？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L547)

15. **Z2A-06-015** 详细介绍多智能体协同策略——三层 Agent（Root / Main+Fallback / Sub-Agent）是怎么配合流转的？主 Agent 越过中间层直接调子 Agent 时，上下文怎么跨层传递？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L608)

16. **Z2A-06-016** Multi-Agent 中心化编排模式 vs 点对点架构，核心区别和优势是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L670)

17. **Z2A-06-017** 为什么大家都在用 Multi-Agent？从一开始到现在原因是否有变化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L705)

18. **Z2A-06-018** Multi-Agent 如何通信？不同项目分别用了哪些通信方法？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L746)

19. **Z2A-06-019** 如果让两个不同的 Agent 产品进行对话（比如 Claude Code 和 Cursor），在协议层面应该怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L805)

20. **Z2A-06-020** 智能体可信通信怎么实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L835)

21. **Z2A-06-021** 主 Agent 与子 Agent 的通信和进度同步怎么做？是推还是拉？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L856)

22. **Z2A-06-022** 多 Agent 协作常见模式有哪些？各自适合什么任务类型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L927)

23. **Z2A-06-023** 多个 Agent 并发操作数据库或文件，这种并发怎么处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1003)

24. **Z2A-06-024** 子 Agent 之间的上下文怎么传递？传什么、不传什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1037)

25. **Z2A-06-025** 大规模 Multi-Agent 如何做调度、背压和资源隔离？调度器崩溃或 Leader 派错任务时怎么恢复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1107)

26. **Z2A-06-026** 复杂 Agent 为什么拆成 LangGraph 子图而不是单条 Pipeline？子图的状态与 IO 契约如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1138)

27. **Z2A-06-027** 校验 Agent 和推理 Agent 结论冲突时怎么处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1156)

28. **Z2A-06-028** 业务模块增删时，如何治理 Multi-Agent 能力拓扑，避免 Agent 增殖和路由配置失控？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1209)

29. **Z2A-06-029** 如何保证多 Agent 通信结果明确、可验证，而不是自然语言互相猜？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1239)

30. **Z2A-06-030** 多人、多 Agent、跨设备协同与“群聊式多 Agent”有什么不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1251)

31. **Z2A-06-031** 多个 Agent 并行跑的时候状态竞争怎么避免？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1270)

32. **Z2A-06-032** 如果拆成感知/推理/校验 Agent，哪些能并行哪些要顺序，什么时候需要反向通信？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1336)

33. **Z2A-06-033** 在 A2A 场景下，如何防止两个 Agent 陷入递归对话？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1399)

34. **Z2A-06-034** 如何按租户、任务和 Agent 层级设置分层并发预算？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1461)

35. **Z2A-06-035** 多 Agent 执行策略如何根据任务动态选择，并在运行中安全切换？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/06-multi-agent-collab/index.md#L1475)

