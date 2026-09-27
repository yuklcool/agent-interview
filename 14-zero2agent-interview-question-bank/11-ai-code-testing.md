# 11｜AI 代码分析与测试：覆盖率、插桩、代码过滤

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/11-ai-code-testing/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 21 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 代码分析与过滤

1. **Z2A-11-001** 对于代码解析有没有前置分析？有效性判断怎么实现的？未来让你来优化这些指标你会怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L16)

2. **Z2A-11-002** 分支覆盖率是怎么统计的？原理有没有了解过？代码插桩具体是怎么实现的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L46)

3. **Z2A-11-003** 有没有思考过哪些代码会让模型生成的准确度和覆盖率降低？这些用 AST 和 LSP 都生成不了单测的代码如何过滤？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L85)

## 生成代码验证

4. **Z2A-11-004** 如何测试 AI 生成代码的正确性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L118)

5. **Z2A-11-005** AI 生成的代码线下测试没问题，上线后出了问题怎么办？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L189)

6. **Z2A-11-006** 如何用 Agent 自动化测试一个现有软件项目，并划分规划、执行、Oracle 与人工门禁？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L235)

7. **Z2A-11-007** 工程级 Code Agent 处理项目上下文、生成代码时有哪些核心挑战？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L270)

8. **Z2A-11-008** Coding Agent 如何做增量代码审查，避免大仓库全量逐行扫描？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L292)

9. **Z2A-11-009** AI 生成代码在哪些场景更具落地价值？应用边界在哪？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L304)

10. **Z2A-11-010** Coding Agent 如何执行人工交互测试，例如操作浏览器并验证页面行为？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L329)

11. **Z2A-11-011** AI 测试平台中，人和 AI 的职责边界如何划分？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L351)

12. **Z2A-11-012** AI Coding 如何完成多来源账单分析应用，并证明交付结果可信？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L377)

13. **Z2A-11-013** TDD 如何接入 Coding Agent？测试门禁应该放在生成流程的哪个阶段？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L389)

14. **Z2A-11-014** Coding Agent 能否自举开发自身？如何避免生成器与验证器同源导致循环确认？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L405)

15. **Z2A-11-015** 什么是 AST，代码测试中如何使用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L422)

16. **Z2A-11-016** 污点分析通常包含哪三类核心节点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L435)

17. **Z2A-11-017** 请举例说明业务中的污点源和污点汇。 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L448)

18. **Z2A-11-018** 代码 Agent 评测中，worktree 对照实验解决什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L461)

19. **Z2A-11-019** 如何用工程手段治理代码规范，而不是只依赖模型提醒？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L474)

20. **Z2A-11-020** 如何评估并保证 AI Code Reviewer 的审查正确性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L490)

21. **Z2A-11-021** HumanEval、MBPP、APPS 的数据集结构与评估方式是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/11-ai-code-testing/index.md#L504)

