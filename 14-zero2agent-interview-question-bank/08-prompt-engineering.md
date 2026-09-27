# 08｜Prompt 工程与框架原理：模板构建、Skills 机制

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/08-prompt-engineering/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 31 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## Prompt 模板方法

1. **Z2A-08-001** 提示词模板是怎么构建的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L17)

## Skill 与框架原理

2. **Z2A-08-002** Skills 的原理有没有了解过？怎么实现的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L44)

3. **Z2A-08-003** Claude Code 的架构有什么比较创新的设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L122)

## Prompt 标准与 Skill 体系

4. **Z2A-08-004** 如果让你从零设计一个 Skill 系统，需要实现哪些核心能力？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L179)

### 设计时必须考虑的问题

5. **Z2A-08-005** 为什么已经有了 MCP，Anthropic 还要做 Skill？Skill 里面有没有工具？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L309)

### Skill 里面有没有工具？

6. **Z2A-08-006** 一个好的 Prompt 和一个差的 Prompt 的区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L368)

7. **Z2A-08-007** LobeChat 的插件和 Claude Code 的 Skills 有什么本质区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L399)

## Prompt 结构化设计

8. **Z2A-08-008** Harness Engineering 是什么？它如何演进的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L445)

9. **Z2A-08-009** Skill 的渐进式披露（Progressive Disclosure）怎么实现？Skill 之间的沙箱隔离和通信机制是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L483)

10. **Z2A-08-010** 通常 Prompt 包含哪些结构？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L526)

11. **Z2A-08-011** 在调优 Prompt 时，你有哪些实战经验？如何利用 AI 辅助自己优化 Prompt？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L587)

12. **Z2A-08-012** 什么是一个好的提示词？如何做好提示词的评估？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L631)

13. **Z2A-08-013** 用户的某个需求，你会沉淀为 Skill 还是长期记忆？判断标准是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L670)

14. **Z2A-08-014** DSPy 是什么？它在 Agent 提示词优化和流程构建上有什么优势？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L705)

15. **Z2A-08-015** 你觉得一个 Skill 写得好不好，应该看哪些标准？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L746)

16. **Z2A-08-016** 单看 Prompt 层面，有哪些办法能让模型回答更快、更稳定？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L777)

17. **Z2A-08-017** OpenSpec/Spec 驱动开发与普通开发流程有什么区别？如何治理 Spec 过期？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L804)

18. **Z2A-08-018** Skill 和 Agent 的关系，为什么不用 Skill 而用子 Agent？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L818)

19. **Z2A-08-019** Skill 分层体系怎么设计？为什么这么分层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L884)

20. **Z2A-08-020** 如何给 Agent 工具系统设计动态 Skill，而不让版本升级破坏历史任务？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L995)

21. **Z2A-08-021** 团队里的 Skill 数量持续膨胀，如何治理重复能力、路由冲突和上下文占用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1065)

22. **Z2A-08-022** Skill 的多后端可插拔加载应该如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1081)

23. **Z2A-08-023** 如果让你设计一个代码审查的 Skill，你会如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1102)

24. **Z2A-08-024** 如果 Agent 挂 100 个 Skill，如何提升召回率、准确度、F1 综合值？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1215)

25. **Z2A-08-025** 为什么 Coding Agent 的 Skills 通常放在 System 上下文，而不是用户 Query 中？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1276)

26. **Z2A-08-026** Skill 的 Prompt 配置上线后出错，如何快速止损和修复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1292)

27. **Z2A-08-027** 如何让 Agent 自动沉淀 Skill，同时保证生成的 Skill 准确、无害且不会无限膨胀？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1316)

28. **Z2A-08-028** 动态 Prompt 和静态 Prompt 有什么区别？各自在什么场景下用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1332)

29. **Z2A-08-029** 为什么一个很短的 Skill 也可能有效？如何验证效果来自哪里？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1430)

30. **Z2A-08-030** 可演进能力为什么应封装为 Skill，而不是不断塞进 Prompt？Skill 的知识进化流水线如何治理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1442)

31. **Z2A-08-031** 如何让大模型从混乱的非结构化文档中稳定提取结构化 JSON？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/08-prompt-engineering/index.md#L1460)

