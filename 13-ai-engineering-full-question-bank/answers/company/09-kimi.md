# Moonshot AI（Kimi）｜逐题答案

对应原题库公司专项第 9 组，共 10 道。

## KIMI-01｜Kimi's headline feature is very long context. When you push from 8K to hundreds of thousands of tokens, what actually breaks first, and why?

先区分训练长度外推和服务容量。全注意力 prefill 计算/中间工作随 T² 增长（优化内核可降内存但不消除算量），KV 缓存随 T 线性增长，RoPE/位置外推、远处检索准确率与“lost in the middle”也会退化。通过分块/稀疏注意力、上下文并行、KV 压缩和长序列继续训练缓解；用 needle、跨段综合、真实任务与 p95/cost 一起评估。

## KIMI-02｜Kimi K2 uses Multi-head Latent Attention (MLA). Explain what it does and how it compares to GQA for KV-cache reduction.

MLA 将 KV 投影到更小的潜在向量存储，解码时按数学等价变换恢复需要的注意力计算，RoPE 部分需单独设计位置分量；GQA 则减少 KV 头数。比较每 token KV bytes、投影开销、训练改造与内核支持；不能以“低秩维度越小越好”，压缩率受质量约束。参考 [DeepSeek-V2](https://arxiv.org/abs/2405.04434) 的 MLA 原理，Kimi 具体配置看其报告。

## KIMI-03｜Kimi K2 is a 1T-parameter MoE with ~32B active per token and hundreds of experts. Explain the routing and the systems cost of training it.

每 token 路由激活少数专家+共享层，总参数约 1T 决定权重驻留和部署节点数，约 32B 激活决定主要 FFN 算量；专家并行的 all-to-all、负载倾斜、容量溢出与 checkpoint 是关键。训练按网络拓扑布置并行，路由均衡、通信重叠与故障恢复；面试时把报告标称值和实际 token/s、峰值显存分开。

## KIMI-04｜How do you take a model trained at 8K–32K and make it work at 128K or more?

先做位置编码扩展（如 RoPE 频率缩放/YaRN）与长序列 continued pretraining，按长度课程逐步扩展，加入跨段依赖、检索和问答训练。只在 8K 学得短程模式的模型不能靠修改配置可靠理解 128K；评估不同位置的事实定位、多跳推理、长文总结、幻觉和成本，避免仅测孤立 needle。服务侧处理 KV 与 prefill 峰值。

## KIMI-05｜Walk me through why you would disaggregate prefill and decode onto separate machines, as Mooncake does. What does that buy you and what does it cost?

prefill 是大矩阵计算、长输入高吞吐；decode 通常按 token 迭代且受显存带宽/KV 约束，分池可分别优化 GPU 利用和排队。跨池传 KV 带来网络带宽、传输延迟、缓存所有权与故障恢复复杂度；前缀缓存命中和请求长度分布决定收益。按 TTFT、每 token 延迟、goodput、KV 传输量做同硬件 A/B。

## KIMI-06｜A chat assistant re-sends a long conversation history on every turn. How do you avoid recomputing all of it, and what are the pitfalls?

对会话前缀用规范化 token 序列及模型/采样相关配置建前缀 KV 缓存，append 新轮 token 只计算后缀；缓存按 block 引用计数并做租户隔离、TTL/LRU。系统提示版本、工具返回、截断策略或模型权重变化都会使旧 KV 失效，不能按“文本相似”重用；重复上文若被改写/删减需重算，测命中率与显存占用。

## KIMI-07｜For a long-context assistant, when is a 1M-token context window the right tool, and when should you use retrieval instead?

上下文窗口适用于要按原文精读、跨多段细节推理且资料规模能放下的任务；检索适用于海量/持续更新/权限复杂的文档库，能降低 prefill 成本并提供来源。混合策略先检索筛选、再把关键证据及必要长上下文送模型，必要时分层摘要；比较证据召回、答案准确、首 token、每问成本及权限撤销时效。

## KIMI-08｜Training a trillion-parameter model, attention logits can blow up and destabilise the run. What is going on, and how does something like MuonClip address it?

注意力 logits 是 QKᵀ/√d，训练中 Q/K 范数增长或极端样本可使 logits 过大、softmax 饱和、梯度异常；大规模低精度放大问题。MuonClip 一类方法约束更新或相关权重/激活范数以控制 logits，配合监控头级最大值、学习率、混合精度和梯度裁剪；具体算法按原论文实现验证，不能把普通 global clip 当成等价替代。

## KIMI-09｜Kimi K1.5 scaled RL for reasoning without a process reward model or tree search. Why deliberately keep the RL recipe that simple?

可验证的数学/代码任务有较明确的最终奖励，简化 RL 流程便于扩展采样与 credit assignment，并减少过程奖励模型/树搜索的偏差和工程成本。仍需控制长度奖励黑客、错误测试/作弊、探索多样性和训练稳定性；用独立隐藏验证集与人工审查检验推理是否真的可泛化，而非只提升可见基准。

## KIMI-10｜Kimi K2 targets agentic and coding tasks. How would you evaluate whether an agentic model is actually good, beyond a single benchmark number?

以可复现环境运行真实多步任务：代码修复看隐藏测试、构建/回归与补丁质量；工具代理看调用序列、权限、恢复和最终状态。按难度、语言、仓库规模和工具失败分层，记录完整轨迹与成本/时延、成功率和安全违例；多次采样估计方差，防基准污染和人工介入不一致，灰度看真实用户完成率。
