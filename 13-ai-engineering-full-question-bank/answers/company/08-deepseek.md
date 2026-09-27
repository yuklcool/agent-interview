# DeepSeek｜逐题答案

对应原题库公司专项第 8 组，共 10 道。特定架构与训练口径以 [DeepSeek-V3 技术报告](https://arxiv.org/abs/2412.19437) 为参考。

## DEEPSEEK-01｜Walk me through DeepSeekMoE. How is it different from a standard top-2 MoE like Mixtral?

普通 top-2 MoE 每 token 从所有路由专家选两个；DeepSeekMoE 将专家细粒度拆分，同时设共享专家承载共通知识，路由专家承载专门知识，在相近激活计算下可组合更多专家。收益是知识隔离与灵活路由；成本是专家管理、负载和跨设备通信。讨论时要区分 V2/V3 的专家数与机制，不把“共享”误写成所有参数每 token 都独立路由。

## DEEPSEEK-02｜DeepSeek-V3 uses auxiliary-loss-free load balancing. What was wrong with the auxiliary loss, and how does the bias trick work?

辅助均衡损失给路由梯度施压，可能为了负载而牺牲主任务最优路由。loss-free 方法在选专家时给各专家路由分数加动态 bias：超载则调低、欠载则调高，bias 不直接参与最终门值/主 loss 的梯度优化；按全局负载更新。仍需防 token dropping、专家容量溢出及训练初期不稳定，并用主任务 loss 和路由熵验证。

## DEEPSEEK-03｜What is multi-token prediction (MTP) and why train with it?

MTP 在当前 token 之外增加后续多个 token 预测目标/模块，提供更丰富的训练信号与未来信息结构；训练总损失中给辅助目标权重，避免压倒主 next-token 任务。推理可仅用主头保持成本，或将多步预测当候选草稿做验证加速；加速取决于接受率和实现，不能直接把预测步数当倍数。

## DEEPSEEK-04｜Implement top-k MoE routing with a shared expert in PyTorch, and point out the efficiency and correctness traps.

逻辑代码：`logits=router(x.float())`；按 `topk(logits,k)` 得专家索引和归一化门值；每专家 gather 所属 token、运行 FFN、用 scatter_add 按门值累加；共享专家输出另加。实际要按 token 扁平化、稳定处理空专家、重复索引和 dtype，跨卡 all-to-all 与容量/负载控制是瓶颈；检查输出与稠密参考实现的梯度，避免 Python per-token 循环。

## DEEPSEEK-05｜Sketch how you would serve a 671B-parameter MoE model with low latency under GPU-memory constraints.

671B 总权重 BF16 约 1.34TB，不能用“每 token 37B 激活”忽略全部专家驻留。用专家并行把权重跨节点分布，张量/流水并行处理共享部分，路由尽可能本地化且大 batch 聚合 all-to-all；MLA 压 KV，预填充/解码分离、连续批处理与量化权重。按 p95、吞吐、热点专家和 KV 容量测成本，准备专家节点故障与请求迁移。

## DEEPSEEK-06｜R1-Zero was trained with RL and essentially no SFT first. What did that show, and why did full R1 add SFT back?

R1-Zero 显示在可验证奖励下，纯 RL 能涌现较长推理和自我检查行为；但可读性、语言混杂与输出可用性不稳。完整 R1 引入冷启动 SFT、推理 RL、拒绝采样及进一步 SFT/RL，以提高格式与通用能力。不要把“无 SFT”理解为从随机初始化训练：起点仍是预训练模型。

## DEEPSEEK-07｜FP8 training at 671B scale is hard. What actually breaks in low precision, and how do you make it stable?

FP8 的窄动态范围使激活/梯度异常值溢出或下溢，矩阵乘累加误差及不同 rank 的缩放不一致可引发不稳定。按张量/块缩放，敏感算子（归一化、softmax、路由、主权重/优化器状态）保高精度，监控 amax、NaN、梯度范数；混合精度与通信压缩分别验证。以 BF16 小规模对照检查 loss 轨迹和最终质量。

## DEEPSEEK-08｜How do you build a training dataset without triggering model collapse when much of your data is synthetic?

先保留高质量真实语料作锚，并记录来源、许可、时间与合成比例；合成数据按任务和难度分层，用验证器/人工抽检筛除模式化错误与自我循环，再跨模型来源去重。固定纯真实测试集监控多样性、稀有知识、校准与长尾能力，做合成比例消融。模型坍塌并非“合成一律不能用”，关键是错误反馈和分布尾部丢失。

## DEEPSEEK-09｜DualPipe overlaps computation and communication in training. Why is that overlap the whole game at this scale, and what is the trade-off?

大 MoE 的专家 all-to-all 和流水 stage 通信若串行叠加，会使有效吞吐受网络而非算力限制。DualPipe 类调度把前向/反向计算与跨节点通信交错，尽量同时占用计算与链路；代价是更多在途微批、缓冲显存和调度复杂度。用 trace 测空泡、链路利用率、MFU 与峰值显存，避免只比较理论 FLOPs。

## DEEPSEEK-10｜DeepSeek claims frontier-class results at a fraction of the usual training cost. If an interviewer asks “how is that even possible,” what is your structured answer?

结构化回答：模型架构（MLA/MoE 降 KV 和激活计算）、训练栈（FP8、并行/通信重叠与高 goodput）、数据/后训练（高质量数据、RL 和蒸馏）共同作用；把**报告训练 GPU 小时**与全生命周期成本、硬件采购、数据、人力和推理成本分开。公开数字来自技术报告，应标明统计口径，不能据此断言任意团队可用同等预算复制质量。参阅 [DeepSeek-V3 报告](https://arxiv.org/abs/2412.19437)。
