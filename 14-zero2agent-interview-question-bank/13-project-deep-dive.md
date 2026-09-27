# 13｜简历项目拷打：面试官追着你的 Agent 项目问到底

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/13-project-deep-dive/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 25 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 项目整体与选型

1. **Z2A-13-001** 你的 Agent 项目用了什么框架？为什么选它？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L27)

2. **Z2A-13-002** 你的 Agent 项目有没有真正上线部署？线上效果怎么样？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L79)

## 意图识别与工具设计

3. **Z2A-13-003** 意图识别模块具体怎么做的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L117)

4. **Z2A-13-004** 你的 Agent 有哪些工具？工具是怎么设计的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L167)

5. **Z2A-13-005** 怎么提升工具调用的正确率？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L204)

6. **Z2A-13-006** 工具调用时怎么保证参数提取准确？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L245)

## 知识库与检索

7. **Z2A-13-007** 知识库是怎么构建的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L277)

8. **Z2A-13-008** 分块策略是怎么设计的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L330)

9. **Z2A-13-009** 构建知识库时如何解析上传的表格或图片文件？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L382)

10. **Z2A-13-010** 知识检索时如何提升模型回答正确率？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L431)

## 架构与性能优化

11. **Z2A-13-011** 你的 Agent 系统还有哪些未充分优化的地方？你的改进路线图是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L483)

12. **Z2A-13-012** 你的 Agent 和别人开发的相比，核心差异是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L522)

13. **Z2A-13-013** 你的系统有没有用到 ReAct 模式？怎么用的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L555)

14. **Z2A-13-014** 项目为什么选择 E2B 沙箱？选型理由和优势是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L592)

15. **Z2A-13-015** 开发 Agent 过程中遇到的最大问题是什么？如果重新设计某一模块会怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L627)

16. **Z2A-13-016** 你做过的不同 AI 项目之间，核心技术差异是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L651)

17. **Z2A-13-017** 怎么提升模型回答的性能？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L679)

18. **Z2A-13-018** LangGraph 中的 State 怎么定义和流转？节点多了怎么防止状态膨胀？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L713)

19. **Z2A-13-019** 先做自我介绍，然后简单讲一下自己做过的 Agent 项目 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L757)

20. **Z2A-13-020** 新闻交易 Agent 项目管线如何搭建？Agent 响应延迟是多久？新闻到交易完成需要的时间？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L793)

21. **Z2A-13-021** 视频 AI Agent 项目主要解决什么业务问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L848)

22. **Z2A-13-022** 视频 Agent 的 VideoContext 数据结构应如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L864)

## 推荐阅读

23. **Z2A-13-023** 跨机票、地铁与导航的地图 Agent，如何划定 Agent、数据和工具边界？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L884)

24. **Z2A-13-024** 表格解析后如何保证结构和数值正确？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L903)

25. **Z2A-13-025** 如何介绍 PPT 自动生成管线的技术栈并说明选型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/13-project-deep-dive/index.md#L916)

