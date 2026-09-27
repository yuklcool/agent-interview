# 03｜容错与鲁棒性：超时、报错、误操作的工程化处理

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/03-fault-tolerance/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 38 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 错误恢复与容错

1. **Z2A-03-001** Agent 如何减少幻觉？在工业场景下怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L17)

2. **Z2A-03-002** 你怎么设计 Agent 的失败恢复机制？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L52)

3. **Z2A-03-003** 执行到一半，比如调支付接口超时了，Agent 怎么处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L98)

4. **Z2A-03-004** 如果 Agent 的决策出错了，比如错误删除了数据，系统设计上怎么防范？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L121)

## 幻觉治理与行为约束

5. **Z2A-03-005** 你会如何限制 Agent 的思考深度、工具调用次数和递归层级，避免无限循环？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L144)

6. **Z2A-03-006** 幻觉的各种治理手段，优缺点分别是什么？行为限制在什么阶段做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L212)

7. **Z2A-03-007** 如果 Agent 在中间步骤已经偏了，但表面上还能继续执行，你怎么尽早发现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L270)

## 资源管理与安全防护

8. **Z2A-03-008** Agent 执行 shell 命令怎么保证安全？还有哪些安全问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L320)

9. **Z2A-03-009** Prompt 注入攻击如何防御？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L388)

10. **Z2A-03-010** 工具调用的安全控制是怎么实现的？如何限制模型调用敏感接口？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L458)

11. **Z2A-03-011** 资源紧张怎么处理？资源紧张时候的用户排队机制怎么实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L525)

12. **Z2A-03-012** Skill 间需要传递敏感信息时，如何做到内部可用、对用户不可见？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L582)

## 高风险场景防护

13. **Z2A-03-013** 高风险在线环境中，Agent 的异常管控方案怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L622)

14. **Z2A-03-014** Agent 系统的安全护栏怎么设计？敏感词拦截的工程方案有哪些？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L682)

15. **Z2A-03-015** 为什么在复杂的 Agent 闭环场景中，仅靠 RAG 无法彻底解决幻觉问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L732)

16. **Z2A-03-016** 支付等高敏感操作场景下，Human-in-the-Loop 流程怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L819)

17. **Z2A-03-017** Agent 的 Self-Reflection 机制怎么识别输出中的逻辑错误？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L858)

18. **Z2A-03-018** 金融系统不能让 Agent 真实操作（钱放出去就是大问题），怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L914)

19. **Z2A-03-019** Agent 系统中网络抖动 vs 真实故障，如何区分判断？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L960)

20. **Z2A-03-020** NL2SQL 场景下的 SQL 安全防护怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L979)

## 上下文爆炸与工具循环调用

21. **Z2A-03-021** 如果上下文爆炸或工具循环调用，你是怎么解决的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1003)

## Fallback 机制设计

22. **Z2A-03-022** Agent 系统的 fallback 是怎么做的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1041)

## 多层级失败重试机制

23. **Z2A-03-023** 介绍下整体的失败重试机制——node、RAG 链、tools 分别怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1072)

## 状态机卡死与熔断

24. **Z2A-03-024** Agent 用状态机编排时，状态机卡死悬停、死循环怎么排查和熔断？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1107)

25. **Z2A-03-025** 工具调用返回结果为空或调用失败，Agent 应该怎么处理？是直接重试还是换策略？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1145)

26. **Z2A-03-026** 页面结构变化导致 Skill 失效时，如何检测、降级与修复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1219)

27. **Z2A-03-027** 在跨境汇款等金融业务场景下，Agent 超时/失败如何应对，并保证资金安全？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1242)

28. **Z2A-03-028** Agent 失败通常有哪些原因？如何快速定位责任层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1276)

29. **Z2A-03-029** 所有模型超时或故障时怎么兜底？什么时候用规则引擎，什么时候转人工，服务恢复后怎么回切？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1306)

30. **Z2A-03-030** Agent Workflow 如何保证节点原子性，并在部分成功后安全回滚？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1368)

31. **Z2A-03-031** Agent 无法处理任务时，“求助 / 升级”状态机应该如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1393)

32. **Z2A-03-032** 工具失败后，哪些异常处理应由大模型参与，哪些必须由确定性程序控制？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1409)

33. **Z2A-03-033** 为什么安全攻击检测不能只依赖大模型？规则、专用模型和 LLM 应该如何分工？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1425)

34. **Z2A-03-034** LLM 没有走标准 Tool Call，而是在文本里直接输出命令请求，系统如何识别、执行并拦截风险？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1443)

35. **Z2A-03-035** 长时间运行的 Coding Agent 等待用户决策时，如何避免任务永久卡住？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1468)

36. **Z2A-03-036** 如何对自己的 Agent 做系统化红队测试，而不是只测 Prompt Injection？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1491)

37. **Z2A-03-037** Coding Agent 看到 .env 文件会怎样？如何设计安全边界？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1503)

38. **Z2A-03-038** 如何设计可靠的 Webhook 投递保障？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/03-fault-tolerance/index.md#L1548)

