# 10｜训练、数据与模型优化：从数据清洗到 LoRA

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/10-training-and-data/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 126 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

## 数据工程与清洗

1. **Z2A-10-001** 预训练数据清洗方法？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L17)

2. **Z2A-10-002** 构造数据集遇到过什么难点，怎么解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L48)

3. **Z2A-10-003** 自动标注系统的主要难点是什么？如何设计模型预标注、置信度分流和人工复核闭环？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L82)

4. **Z2A-10-004** SFT 数据字段如何映射？instruction 与 input 重叠时如何定义清洗和拼接契约？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L107)

5. **Z2A-10-005** 训练数据标注粒度应该越细越好还是按任务适配？如何权衡成本、信息量和泛化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L134)

6. **Z2A-10-006** Agent 工具调用怎么训练？训练集该包含什么？数据怎么来？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L159)

## 微调与对齐训练

7. **Z2A-10-007** DPO、PPO、GRPO 的区别和优缺点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L190)

8. **Z2A-10-008** 微调方法有哪些？LoRA 和全参数微调的区别？怎么选？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L340)

9. **Z2A-10-009** 给定时间序列，如何用 ML 筛选特征，再基于规则建模？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L410)

10. **Z2A-10-010** XGBoost 相比单棵决策树，在目标函数、正则和集成机制上做了什么改进？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L442)

11. **Z2A-10-011** kernel 级别的优化，比如用 CUTE DSL 或手写 CUDA 做 fusion？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L472)

## Transformer 基础

12. **Z2A-10-012** 手撕 Multi-Head Attention [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L497)

13. **Z2A-10-013** 位置编码的作用是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L567)

14. **Z2A-10-014** 常用解决过拟合的方法？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L592)

15. **Z2A-10-015** 绝对位置编码和相对位置编码的区别？应用场景有什么不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L625)

16. **Z2A-10-016** LayerNorm 和 BatchNorm 的区别？应用场景？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L653)

## 模型能力与部署

17. **Z2A-10-017** 大模型推理加速技术有哪些？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L693)

18. **Z2A-10-018** 多模态是怎么实现的？图片怎么编码？消耗很大怎么缩减 token 使用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L750)

19. **Z2A-10-019** 有没有了解过端侧部署的模型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L806)

20. **Z2A-10-020** OCR、多模态模型、YOLO 与 ONNX 分别处于任务、模型和运行时哪个层次？如何组合？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L839)

21. **Z2A-10-021** 你了解哪些多模态大模型？各自的特点？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L876)

22. **Z2A-10-022** RLHF 中奖励模型（RM）的训练数据如何构建？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L905)

23. **Z2A-10-023** 如何优化大模型在长文本生成中的显存占用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L983)

24. **Z2A-10-024** Transformer 中梯度消失/爆炸是怎么解决的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1018)

## 注意力机制与复杂度

25. **Z2A-10-025** 在 Agent 多轮对话任务中，标准 Attention 机制的平方复杂度在工程落地上主要引发了哪些问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1064)

26. **Z2A-10-026** Token 过长导致的 Attention 稀释现象为什么会导致 Agent 的指令遵循能力下降？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1140)

## 训练策略与实践

27. **Z2A-10-027** SFT、蒸馏、GRPO 的技术选型——什么时候用什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1208)

28. **Z2A-10-028** GRPO 的 Loss 函数、Advantages 计算与信用分配机制 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1304)

29. **Z2A-10-029** vLLM 的 PagedAttention 原理是什么？解决了什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1425)

30. **Z2A-10-030** 什么是灾难性遗忘？微调时如何缓解？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1479)

31. **Z2A-10-031** DP、DDP、TP、PP——分布式训练并行策略的区别与选型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1513)

32. **Z2A-10-032** Token 和字符有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1584)

33. **Z2A-10-033** 深度学习网络中的「残差连接」解决了什么问题？其物理含义是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1632)

34. **Z2A-10-034** GQA 和 MLA 的原理是什么？各自解决什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1670)

35. **Z2A-10-035** BF16 与 FP32 精度差异及训练推理选型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1717)

36. **Z2A-10-036** 现有的大模型性能为什么这么好？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1767)

37. **Z2A-10-037** MoE 架构下为什么参数量大但单 Token 推理成本不一定高？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1820)

38. **Z2A-10-038** QLoRA 的核心设计思想是什么？和标准 LoRA 有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1861)

39. **Z2A-10-039** 模型推理慢，排查思路是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1906)

40. **Z2A-10-040** 垂直领域指令微调后，模型通用能力出现退化，怎么解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1953)

41. **Z2A-10-041** 设计一个训练集构建方案——500 条样本覆盖 200+ 查询模式，如何设计数据生产流？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L1997)

42. **Z2A-10-042** Agent 在细分场景（比如法律、医疗）落地时，微调策略和通用场景有什么不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2109)

43. **Z2A-10-043** 超长上下文是怎么实现的？（如 Kimi 这类模型） [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2139)

## 微调 vs Prompt 做代码生成

44. **Z2A-10-044** 为什么要通过微调模型来做代码生成？为什么不用纯 Prompt 或 Spec Coding？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2160)

## 模型参数大小与 Agent 能力

45. **Z2A-10-045** 外部模型参数更大，14B 在 Agent 层面会不会不够？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2202)

## Rerank 模型蒸馏

46. **Z2A-10-046** 对 Rerank 模型进行了蒸馏，蒸馏的数据是什么样的？训练数据大概有多少条？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2246)

## BERT 与 GPT 架构对比

47. **Z2A-10-047** BERT 和 GPT 架构的区别是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2287)

## 为什么大模型都是 Decoder-only

48. **Z2A-10-048** 为什么现在的大模型都是 Decoder-only 架构？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2323)

## 训练 AI Coding Agent 的策略

49. **Z2A-10-049** 如果训练一个 AI Coding Agent，是端到端训练还是分阶段训练？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2360)

## Agent 奖励函数设计

50. **Z2A-10-050** 客服 Agent 的奖励函数有 Reward Hacking、稀疏、区分度太大（只有完全正确和错误）三个问题，请设计新的 reward 解决至少两个。 [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2401)

51. **Z2A-10-051** 多轮 Agent 的 RL reward 怎么设计？Turn 级信用分配怎么做？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2444)

52. **Z2A-10-052** 多轮对话 Agent 没有现成对话数据，如何从 UI 操作流合成 SFT 训练语料？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2480)

53. **Z2A-10-053** 训练后量化的完整流程是什么？粒度、校准方法和离群值如何共同影响精度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2508)

54. **Z2A-10-054** 为什么 Step-level SFT 之后再进行 GRPO，通常比直接从基座模型开始做 GRPO 稳定？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2526)

55. **Z2A-10-055** GPTQ、AWQ、SmoothQuant 与 AdaQuant 的核心思路有什么不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2571)

56. **Z2A-10-056** GRPO 中相对奖励是如何计算的？同一组奖励方差接近零时如何处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2589)

57. **Z2A-10-057** Agent 交互轨迹与普通语言模型语料有什么区别？如何仿真高质量轨迹？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2638)

58. **Z2A-10-058** LoRA 应该挂在哪些层？rank、alpha 和 dropout 如何共同影响效果？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2656)

59. **Z2A-10-059** Agentic RL 与普通 LLM RL 的核心差异是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2672)

60. **Z2A-10-060** 长时序任务中的 Agent RL 为什么容易训练失稳？如何缓解？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2684)

61. **Z2A-10-061** DAPO 为什么可以不使用额外 KL 惩罚？它如何维持策略更新稳定？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2703)

62. **Z2A-10-062** Tool-use 强化学习中的内容奖励应如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2722)

63. **Z2A-10-063** Agentic CPT、SFT、RL 三阶段分别训练什么能力？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2744)

64. **Z2A-10-064** 预训练与 SFT 在数据、目标函数、计算形态和基础设施上有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2768)

65. **Z2A-10-065** Tool-use SFT 训练时，长轨迹采用截断、切分还是掩码？如何避免破坏工具依赖关系？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2786)

66. **Z2A-10-066** Tool-use 轨迹长度与任务复杂度有什么关系？训练数据应如何分布？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2827)

67. **Z2A-10-067** 多工具调用存在依赖关系时，Reward 应如何做信用分配？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2852)

68. **Z2A-10-068** 训练实验如何对 YAML 配置做规范化哈希，并保证单变量变化可复现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2881)

69. **Z2A-10-069** 如何训练模型做高精度抽取式摘要？数据、目标、Loss 和评测如何设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2899)

70. **Z2A-10-070** Agentic RL 数据筛选为什么会排除部分学生错误轨迹？哪些可恢复错误反而值得保留？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2928)

71. **Z2A-10-071** 业界通常如何处理长视频理解？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2950)

72. **Z2A-10-072** KV Cache Block 的哈希和逻辑到物理映射应该怎么设计？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2965)

73. **Z2A-10-073** Agentic CFT 与 SFT、RL 的目标有何不同？为什么训练时要 Mask Observation Token？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L2981)

74. **Z2A-10-074** 如何处理训练数据中的类别不平衡？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3001)

75. **Z2A-10-075** Transformer 的整体架构、核心模块与实现流程是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3013)

76. **Z2A-10-076** OPD（On-Policy Distillation）是什么？与强化学习有什么关系，对教师模型有什么要求？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3027)

77. **Z2A-10-077** 大模型温度参数的作用是什么？实际使用时如何选择？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3041)

78. **Z2A-10-078** 多轮对话 RL 如何设计过程奖励与终局奖励，并避免用户模拟器过拟合？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3055)

79. **Z2A-10-079** 为什么 SFT 后继续做 DPO/PPO 等偏好优化可能导致基础能力退化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3075)

80. **Z2A-10-080** Agent 动作空间过大导致探索低效时，如何裁剪和分层？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3091)

81. **Z2A-10-081** TTS 音频如何被离散化为 Token，语义与音色信息如何取舍？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3103)

82. **Z2A-10-082** LLaMA-Factory 和 TRL 等 SFT / RL 工具如何对比和选型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3119)

83. **Z2A-10-083** 自研自动驾驶方法与 UniAD 的主要区别应如何比较？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3135)

84. **Z2A-10-084** 决策任务的 label 如何定义？预测任务如何设计监督信号？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3147)

85. **Z2A-10-085** 如何把“减速多少”映射为是否碰撞的风险？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3159)

86. **Z2A-10-086** LightGBM 和 XGBoost 有什么区别，如何选型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3171)

87. **Z2A-10-087** 树模型需要哪些特征工程？缺失值、初始化、默认值和分桶怎么处理？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3183)

88. **Z2A-10-088** 连续特征离散化有什么作用和代价？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3195)

89. **Z2A-10-089** 机器学习、LSTM 和大语言模型之间是什么关系？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3207)

90. **Z2A-10-090** LSTM 的核心设计原理是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3219)

91. **Z2A-10-091** 为什么选择 AC 自动机、TextCNN、FastText 和 TinyBERT，而不是更深的模型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3231)

92. **Z2A-10-092** 使用大模型生成标签时，会遇到哪些问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3243)

93. **Z2A-10-093** 交叉熵损失的数学形式和含义是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3255)

94. **Z2A-10-094** 若真实标签分布为 P、预测分布为 Q，KL 散度如何表示？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3267)

95. **Z2A-10-095** 图召回主要解决什么问题？如何划分负责环节？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3279)

96. **Z2A-10-096** 为什么用图召回，而不是用户—物品行为模型、矩阵分解或双塔模型？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3291)

97. **Z2A-10-097** 为什么在排序链路中同时使用 LightGBM 和 LambdaRank？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3303)

98. **Z2A-10-098** 静态分和动态分在推荐链路中分别起什么作用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3315)

99. **Z2A-10-099** 模型剪枝有哪些方法，如何评估是否值得？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3327)

100. **Z2A-10-100** 序列较稀疏时，建模如何处理稀疏性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3339)

101. **Z2A-10-101** 视频没有语音时，视觉与多模态分析如何降级？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3351)

102. **Z2A-10-102** 一条 VideoSegment 数据结构应保存哪些内容？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3363)

103. **Z2A-10-103** 持续学习有哪些方法，如何避免旧能力退化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3375)

104. **Z2A-10-104** Qwen-VL 的动态分辨率如何实现？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3387)

105. **Z2A-10-105** GRPO 训练数据如何构建与筛选？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3401)

106. **Z2A-10-106** GRPO 训练如何优化并提升稳定性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3415)

107. **Z2A-10-107** SFT 训练数据如何获取、构造与清洗？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3429)

108. **Z2A-10-108** 重要性采样机制的原理、估计偏差与适用场景是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3443)

109. **Z2A-10-109** SFT 冷启动有哪些常见问题，如何诊断和解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3457)

110. **Z2A-10-110** Transformer 自注意力机制的原理、计算过程与作用是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3471)

111. **Z2A-10-111** 如何进行样本难度分层、课程学习与有效样本选择？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3485)

112. **Z2A-10-112** 强化学习训练中的 reward、KL 与 clip fraction 等指标如何解读并定位异常？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3499)

113. **Z2A-10-113** VLM 中如何减少 vision token？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3513)

114. **Z2A-10-114** 多模态训练中的模态偏置如何诊断与纠正？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3527)

115. **Z2A-10-115** 图文对比学习如何训练？InfoNCE 损失与温度系数如何设计和调节？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3541)

116. **Z2A-10-116** 大模型生成复读和语句冗余的成因是什么？如何从数据、算法和参数侧优化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3555)

117. **Z2A-10-117** 模块化、端到端与 VLA/VLM 路线在自动驾驶中如何演进和取舍？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3569)

118. **Z2A-10-118** OCR 系统的主要技术难点有哪些？如何分别解决？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3583)

119. **Z2A-10-119** 数字人或 TTS 生成中如何保证音色一致性？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3597)

120. **Z2A-10-120** 深度学习中的正向传播、反向传播与参数更新是如何工作的？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3611)

121. **Z2A-10-121** VLA 和 ViT 的原理分别是什么？二者在视觉语言动作模型中的关系是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3625)

122. **Z2A-10-122** Semantic ID 在内容表示与推荐系统中的作用是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3639)

123. **Z2A-10-123** 一条完整的 Agent trajectory 数据结构应包含哪些字段？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3653)

124. **Z2A-10-124** MLP Adapter 和 Q-Former Adapter 有什么区别？为什么 MLP 更常用？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3667)

125. **Z2A-10-125** 什么是模型熵坍塌？如何诊断、定位原因并进行缓解？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3681)

126. **Z2A-10-126** SFT 训练阶段不使用测试集时，如何评估训练效果？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/10-training-and-data/index.md#L3695)

