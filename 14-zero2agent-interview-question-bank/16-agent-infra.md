# 16｜Agent Infra：Runtime、Sandbox 与可靠执行

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/16-agent-infra/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 30 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

1. **Z2A-16-001** 一次 Agent 请求的完整执行链路是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L18)

2. **Z2A-16-002** 如果让你设计一个 Agent Runtime，你会怎么拆？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L44)

3. **Z2A-16-003** 为什么需要 Checkpoint，恢复时从哪里继续？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L79)

4. **Z2A-16-004** 如何支撑几十万并发 Agent Task，并把它观测清楚？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L105)

5. **Z2A-16-005** Tool 已成功但 Runtime 在写状态前宕机，如何避免重复副作用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L127)

6. **Z2A-16-006** Agent Sandbox 解决什么问题，为什么容器不一定够？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L154)

7. **Z2A-16-007** Kubernetes Pod/Deployment 从提交到就绪经历哪些控制链路？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L182)

8. **Z2A-16-008** Ray 的核心调度链路是什么，节点 OOM 或上游故障后如何恢复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L198)

9. **Z2A-16-009** Agentic RL 采用同步还是异步 Rollout，如何权衡吞吐与稳定性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L214)

10. **Z2A-16-010** Agentic RL 的 Rollout、Training 与推理引擎如何编排？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L230)

11. **Z2A-16-011** Agent Router 应以什么运行形态存在，请求数据流如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L249)

12. **Z2A-16-012** Agent 平台或 Runtime 出现新框架时，如何评估迁移收益、兼容老旧服务并决定是否淘汰旧方案？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L265)

13. **Z2A-16-013** 如何让 Agent 执行过程可观测、可调试？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L288)

14. **Z2A-16-014** Kubernetes 在 Agent Infra 中负责什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L307)

15. **Z2A-16-015** Kubernetes 的 Request 与 Limit 分别怎样影响调度和资源隔离？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L325)

16. **Z2A-16-016** Kubernetes Scheduler 的三个队列如何流转？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L341)

17. **Z2A-16-017** Agent Worker 或 Sandbox 滚动发布时，如何逐步切流并保护长任务？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L357)

18. **Z2A-16-018** Agent Infra 为什么能提升 Agent 的能力上限和任务成功率？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L373)

19. **Z2A-16-019** 大量本地端 Agent 与云端 Agent 如何协同？身份、状态、离线和任务迁移边界怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L389)

20. **Z2A-16-020** Agent 调用 Sandbox 的链路如何容错？Sandbox 运行中崩溃后怎么恢复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L416)

21. **Z2A-16-021** Agent Task 适合建模为 Kubernetes CRD 吗？如何权衡声明式管理与高频任务吞吐？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L434)

22. **Z2A-16-022** verl AgentLoop 的运行模型、状态与扩展点是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L454)

23. **Z2A-16-023** Agent 状态放在 Sandbox 内、用户状态放在 Sandbox 外时，边界如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L489)

24. **Z2A-16-024** 周期性 Agent 任务如何把 Schedule 与每次 Run 分离，并处理时区、漏跑、并发、幂等和失败通知？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L514)

25. **Z2A-16-025** Agent 如何实现主动向用户推送消息？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L533)

26. **Z2A-16-026** Agent 执行过程中如何提供安全停止功能？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L545)

27. **Z2A-16-027** 用户点击停止后，系统需要完成哪些清理和收尾？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L557)

28. **Z2A-16-028** 如何降低 Agent 依赖技术人员逐个配置的成本？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L569)

29. **Z2A-16-029** Agent Workbench 解决什么问题？应具备哪些核心能力？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L581)

30. **Z2A-16-030** 如何判断一个 Agent 基础设施是否完备？应从哪些能力和质量指标评估？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/16-agent-infra/index.md#L595)

