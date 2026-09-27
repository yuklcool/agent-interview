# 05｜评估与全局观：怎么量化 Agent 好坏、落地最大挑战

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/05-eval-and-vision/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 55 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## Agent 评测体系

1. **Z2A-05-001** 如何量化评估一个上线的 Agent 好坏？除了准确率。 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L17)

2. **Z2A-05-002** 在你看来，当前阻碍 Agent 大规模落地的最大挑战是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L40)

3. **Z2A-05-003** 如何对 Agent 记忆系统的效果进行量化评估？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L58)

4. **Z2A-05-004** 你觉得 Agent 在线上最难监控的指标是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L96)

## AI 工具与开发经验

5. **Z2A-05-005** 从开发者角度，做 Agent 最难的部分是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L122)

6. **Z2A-05-006** 有没有遇到过 AI 应用或者工具无法解决的场景？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L147)

7. **Z2A-05-007** 你觉得 AI 工具最大的帮助场景是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L167)

8. **Z2A-05-008** 你觉得 Agent 框架（如 Claude Code）还有哪些地方可以改进？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L188)

## RAG 与 Agent 评测指标

9. **Z2A-05-009** 你会怎么给 Agent 建立评测体系？只看最终成功率为什么不够？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L210)

10. **Z2A-05-010** RAG 系统（如 oncall 机器人）的回答准确率怎么计算？用知识问答对比还是文档相似度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L268)

11. **Z2A-05-011** 如何从真实 Issue 构建可复现的缺陷修复 Agent Benchmark，并防止污染和假修复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L312)

12. **Z2A-05-012** 如果线上反馈“这个 Agent 有时候很好，有时候很差”，你第一步会看什么指标和日志？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L347)

## 落地风险与行业趋势

13. **Z2A-05-013** 了解最近 AI 的新方向吗？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L393)

14. **Z2A-05-014** 2026 年做 Agent 应用开发，跟去年相比最大的变化是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L432)

15. **Z2A-05-015** 要把 Agent 真正上线到生产环境，你认为最容易被低估的三个风险点是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L462)

## 评测方案设计与实践

16. **Z2A-05-016** 通过什么方式去验证 Skill 的提升效果，指标是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L496)

17. **Z2A-05-017** RAG 系统如何评测？有哪些评测维度和指标？评测数据集怎么构建？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L538)

18. **Z2A-05-018** Agent 的端到端成功率和工具误调用率怎么量化？怎么改进？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L638)

19. **Z2A-05-019** Ragas 评测框架是什么？Answer Relevance 偏低时，怎么区分是检索问题还是模型问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L695)

20. **Z2A-05-020** 如何为 Word、PDF、Markdown 等文档生成与编辑能力设计通用自动评测框架？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L747)

21. **Z2A-05-021** 怎么理解 Vibe Coding？你有哪些实践经验？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L780)

22. **Z2A-05-022** 如何衡量 Agent 的 Planning 能力 vs Hallucination Rate？请列举具体的量化评估指标或自动化评估框架 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L812)

23. **Z2A-05-023** 设计一个电商客服 Agent 的评测方案——商品咨询、售后处理、投诉安抚三类任务如何分别评估？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L902)

24. **Z2A-05-024** 用户在线反馈怎么收集？不同模型和 Prompt 的 AB 测试怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L977)

25. **Z2A-05-025** AI 写代码越来越强，算法工程师的角色会怎么变？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1034)

26. **Z2A-05-026** 哪些类型的 Agent 产品在未来 2 年内最可能被淘汰？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1063)

27. **Z2A-05-027** 线上 log 是海量的，怎么转化成有限的线下评测集？随机抽样为什么不行？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1089)

28. **Z2A-05-028** 能不能不走“线上转线下评测集”，直接对线上 case 做无 GT 的打分和效果观测？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1154)

29. **Z2A-05-029** 你怎么看 Agent 后续的发展？哪些场景你觉得更容易落地？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1234)

30. **Z2A-05-030** 面试最后的反问环节，怎么提出有深度的问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1265)

31. **Z2A-05-031** Text2SQL 系统的准确性怎么评测？用户反馈 SQL 不可用时，系统怎么回流优化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1296)

32. **Z2A-05-032** RAG 召回链路的监控怎么做？怎么判断召回漂移？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1344)

33. **Z2A-05-033** Agent 自进化闭环如何设计？怎样判断沉淀出的经验值得进入系统？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1383)

34. **Z2A-05-034** 如何通过两套 Harness 的同任务对照与组件消融定位效果差异？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1418)

35. **Z2A-05-035** 如何证明 Agent 的最终答案真正使用了工具或检索证据，而不是凭模型常识猜中？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1445)

36. **Z2A-05-036** 树形意图识别和逐层路由应该如何设计，并构造评测集避免误差级联？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1464)

37. **Z2A-05-037** Skill 路由应该如何构造测试集并评估？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1482)

38. **Z2A-05-038** Multi-Agent 出现 Badcase 时，如何定位责任 Agent，并判断是否需要 SFT？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1512)

39. **Z2A-05-039** 独立 Verifier 和 LLM-as-Judge 应该如何分工？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1535)

40. **Z2A-05-040** 什么是 AI-native 团队？如何判断团队离 AI-first 还有多远？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1549)

41. **Z2A-05-041** 如何实现基于 VLM 的 Benchmark 系统，并避免评测模型自说自话？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1564)

42. **Z2A-05-042** 哪些业务场景不适合引入 Agent？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1581)

43. **Z2A-05-043** 供应商不返回 usage 时，如何核算 Agent 的 Token 和成本？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1594)

44. **Z2A-05-044** 如何判断用户反馈真的让 Agent 变好，而不是噪声或选择偏差？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1606)

45. **Z2A-05-045** 评审 Agent 为什么要左移？应该左移到需求、设计还是编码阶段？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1618)

46. **Z2A-05-046** 如何设计消融实验并判断模块贡献？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1630)

47. **Z2A-05-047** Skill 的调用量、Token 成本和效果埋点应该放在哪一层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1643)

48. **Z2A-05-048** 如何为跨任务重复出现的安全或质量问题生成稳定 Fingerprint，并安全接入自动修复 Agent？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1659)

49. **Z2A-05-049** 串行链路修改一个节点后，如何做精确归因？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1680)

50. **Z2A-05-050** 智能问数结果出现误差时，如何区分数据链路问题与模型数值理解问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1696)

51. **Z2A-05-051** 如何搭建微调任务的效果评估体系，并量化模型优化收益？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1710)

52. **Z2A-05-052** 如何设计一个通用的图像质量评估模型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1724)

53. **Z2A-05-053** 故障诊断系统如何降低误报率并平衡漏报率？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1738)

54. **Z2A-05-054** 生成内容常见的质量 Bad Case 有哪些，如何分类与评估？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1752)

55. **Z2A-05-055** 如何通过统计显著性和重复实验排除实验结果的随机波动？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/05-eval-and-vision/index.md#L1766)

