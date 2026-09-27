# NVIDIA｜逐题答案

对应原题库公司专项第 16 组，共 13 道。

## NVIDIA-01｜Here's a CUDA kernel that's 10x slower than expected. Without running it, what are the usual suspects, and how do you confirm each?

先看 launch 配置与形状：全局内存是否合并访问、stride/对齐、重复读写、寄存器过多导致 occupancy 低、shared memory bank 冲突、分支发散、原子热点与 kernel 启动开销。用 Nsight Compute 的带宽、SM 利用、stall 原因、寄存器/occupancy、访存事务和 roofline 验证；先用最小输入核对正确性，逐项改动做基准，避免凭猜测并行优化。

## NVIDIA-02｜Implement the block manager for a paged KV cache: allocate, append, free, and copy-on-write prefix sharing.

每个逻辑 block 维护物理 block ID、有效 token 数、引用计数和空闲链表；allocate 原子取空闲块，append 在尾块有空间时写入，否则新分配；free 减引用到零回收。前缀共享增加引用，写共享尾块前 copy-on-write 复制并换映射；请求取消/失败回收全部引用，避免 double-free，锁/代际 ID 防 ABA。测试跨 block、fork、取消和内存耗尽。

## NVIDIA-03｜A model runs fine in FP32 but produces garbage after conversion to FP16. Debug it.

排查首个非有限/偏离层，比较 FP32/FP16 的激活范围、softmax logits、norm、累加与权重转换，尤其 FP16 最大值约 65504。敏感运算用 FP32 累加或 BF16 更宽指数，稳定 logsumexp、合适的 loss scaling；逐层对照误差与最终质量，不只看全局 loss。

## NVIDIA-04｜Explain strategies to combat overfitting in tree-based classification models.

按时间/实体切分验证，限制树深、叶最小样本、特征/样本子采样、剪枝与早停；梯度提升调学习率与树数，随机森林关注树相关性和叶子大小。排查数据泄漏与标签噪声，比较训练/验证曲线和分层性能，而不是盲目增加正则。

## NVIDIA-05｜Summarize the differences and benefits of the Adam optimizer compared with other methods for neural-network image classification.

Adam 保存一阶/二阶梯度动量并做偏差校正，通常对不同参数尺度较稳、早期收敛快；SGD+momentum 计算/状态更省，某些图像分类设置可有不同泛化。AdamW 将 weight decay 解耦，更容易解释超参；比对相同训练预算、学习率调度、精度与验证准确率，而非泛称 Adam 必然更优。

## NVIDIA-06｜A network confuses pugs and pit bulls and some training labels are wrong. How do you modify the model and the data?

先人工审查混淆矩阵和 pug/pit bull 错例，修错误标签/重复与背景捷径；扩充困难负样本、光照/姿态/体型多样性，按个体/来源分组防泄漏。再调骨干表示、输入分辨率与类别权重，做分层精确率/召回率和置信度校准；识别无法从图像可靠区分的样本并允许“不确定”。

## NVIDIA-07｜How do you evaluate a clustering model's effectiveness without pre-labelled groups?

无真标签可用内部紧密度/分离度（silhouette、Davies–Bouldin），但这些偏好特定形状；再看 bootstrap/不同随机种子稳定性、业务约束（同实体 must-link）、人工抽样可解释性和下游检索效用。检查规模不平衡、噪声点及嵌入距离是否有意义，不能靠一个 silhouette 分数宣布成功。

## NVIDIA-08｜You want to serve a 70B-parameter model on a single 80 GB GPU. Walk me through whether it fits and what single-stream tokens/sec you'd expect.

70B BF16 权重约 140GB，单张 80GB 不可装下；INT8 理论 70GB 加 scale/KV/运行时可能仍紧，INT4 理论 35GB 加开销较可行。估单流速度看 decode 每 token 需读量化权重规模/可用显存带宽，再加反量化、attention 和调度开销；例如理想 40GB/3TB/s 仅是约 13ms 下界，不等于实际 75 token/s。给硬件型号、上下文、内核和实际基准范围，不能脱离配置精确报速。

## NVIDIA-09｜What does TensorRT / TensorRT-LLM actually do to a model to make it faster, and when will it not help?

TensorRT-LLM 通过图/内核融合、权重布局与量化、attention/KV 管理、批处理和特定 GPU 的算子选择降低延迟/提高吞吐；收益取决于模型算子是否受支持、形状和并发。若主要瓶颈在检索/网络、低 batch 启动、专家跨机通信或量化质量约束，编译优化可能有限；用同质量/同硬件 p95 与成本比较。

## NVIDIA-10｜Design the parallelism strategy for serving a 405B-parameter dense model. TP, PP, EP: what goes where and why?

405B BF16 权重约 810GB，不适用 EP（专家并行针对 MoE），应在节点内高速互联上用 TP 分矩阵，跨节点用 PP 切层，必要时权重/上下文量化。PP 单请求低并发有流水空泡，TP 跨节点 all-reduce 昂贵；选切分以显存、互联和批量为约束，KV 按序列分片。测试首 token、decode、吞吐与单卡故障域。

## NVIDIA-11｜Design a podcast search engine with transcript indexing. / Design a recommendation algorithm for type-ahead search.

播客搜索：ASR 转录按时间戳分段，保留节目/说话人、置信度，BM25+向量召回后重排并返回可播放时间片；测 WER、片段 Recall@k 与引用准确。Type-ahead：前缀索引/Trie 候选，按频次、个性化、时效与安全重排，亚百毫秒缓存；离线 MRR 与线上完成率，防热门词垄断。

## NVIDIA-12｜A customer's LLM chatbot on 8 GPUs is “too slow and too expensive.” You have one week with them. What do you do?

一周内先拿真实长度/并发 trace 和质量集：第 1 天定位排队、prefill、decode 或检索成本；第 2–3 天试 batch/KV/前缀缓存、量化、输入裁剪和路由；第 4–5 天用同质指标压测与灰度。给客户成本分解、p95、质量回归和回滚计划，避免为了 throughput 让尾延迟恶化。

## NVIDIA-13｜Describe a time you dealt with conflicting priorities or stakeholder feedback. What would your current manager say about you?

用真实 STAR 案例：冲突方各自目标、你如何量化取舍与展示数据、如何达成/执行决定、结果和复盘。对“经理会如何评价”给可核实的具体工作方式及改进点，别代替经理编造评价。
