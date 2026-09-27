# Alibaba（Qwen）｜逐题答案

对应原题库公司专项第 11 组，共 10 道。模式相关描述参照 [Qwen3 技术报告](https://arxiv.org/abs/2505.09388)。

## QWEN-01｜Qwen2.5-Coder trains with repository-level fill-in-the-middle using tokens like <|fim_prefix|>, <|fim_suffix|>, <|repo_name|>. Write the function that formats a repo-level FIM example, and explain why repo-level beats file-level.

格式函数接收 repo 名、目标文件路径、prefix、suffix 和检索到的同仓文件；按训练协议转义/隔离特殊 token，构造 `<|repo_name|>repo ... <|fim_prefix|>prefix<|fim_suffix|>suffix<|fim_middle|>`，相关文件需明确文件边界与顺序。只从提交时间前的同仓内容采样，避免答案泄漏；repo 级上下文能提供跨文件 API/命名习惯，但成本高且可能引入无关噪声。具体标记序列以模型 tokenizer/chat template 为准。

## QWEN-02｜Qwen uses byte-level BPE with a ~151K vocabulary, augmented for multilingual coverage and with digits split into single characters. Why those choices, and what are the trade-offs?

字节级 BPE 可编码任意脚本而不依赖未知字符；较大词表使多语言常用片段更少 token，代价是 embedding/输出层变大、稀有 token 学习不足。单字符数字拆分有利于一致的数字表示与算术泛化，但长数字占更多 token。按语言和代码领域测 fertility、训练稳定性、推理成本，而不是仅看词表大小。

## QWEN-03｜Qwen3 unifies a thinking mode and a non-thinking mode in one model with a caller-settable thinking budget. How would you train that, and how would you serve it?

统一模式需在 SFT/偏好训练中包含明确模式控制 token 或模板：短答学直接作答，长推理学在预算内探索后给最终答；训练时兼顾相同任务的双模式和安全一致性。服务 API 显式传模式及预算，超预算时有终止/继续策略，比较正确率、p95 与 token 成本；使用官方 chat template 以免控制失效。

## QWEN-04｜Qwen ships both dense and MoE models (30B with ~3B active; 235B with ~22B active). When would you pick the 30B-A3B MoE over a 32B dense?

30B-A3B MoE 在每 token 主要计算接近小模型，同时参数总量给更大容量，适合高吞吐且可容纳所有专家的服务；32B dense 结构简单、低并发延迟可预测，显存与通信需求可能更好。比较端到端质量、权重驻留、路由通信、batch 规模和量化兼容性，不能仅按“激活 3B”推断速度或价格。

## QWEN-05｜Qwen2.5 extends context to 128K (and ~1M for Turbo) using YaRN plus Dual Chunk Attention, mostly training-free. Explain how, and why post-hoc extension is attractive.

YaRN 对 RoPE 频率作长度外推缩放，Dual Chunk Attention 把注意力按块与跨块路径组织，以减轻极长位置的计算/位置分布变化；后扩展可复用已训权重，比全长预训练省算力。质量并不由配置开关保证：按模型版本、块策略和长度验证跨段依赖、位置偏差、吞吐/KV 成本；超训练长度仍可能明显退化。

## QWEN-06｜Qwen3 uses strong-to-weak distillation, bootstrapping smaller models from flagship ones. How does that work and why is it cheaper?

大模型作为教师生成经验证的解题/工具轨迹、概率分布或偏好，小模型用 SFT/KL 蒸馏，再可做短期 RL/直接偏好优化；严格去重训练/测试、过滤教师幻觉。相较小模型从头做同样大规模探索，离线生成和监督学习通常更省在线 RL 样本；测难题、长上下文、安全和 token 效率，防学生只模仿表面格式。

## QWEN-07｜Qwen's reasoning models train with RL using verifiable rewards on maths and code. Why is that preferred over PPO with a learned reward model for these domains?

数学和代码有答案/测试可自动验证，奖励更客观、可规模化，避免学习型奖励模型的偏好漂移；可用组内相对优势等方法优化。验证器仍可能被投机：弱测试、超时、格式漏洞及训练集污染。隐藏测试、对抗题、长度和成本控制与人审必不可少；开放域任务仍需要偏好/人工评估。

## QWEN-08｜Qwen ships open weights that top public leaderboards. As the release engineer, how do you make sure the benchmark numbers are trustworthy and not contaminated?

发布前记录数据来源、去重和可能污染，封存独立时间后/私有测试；冻结模型 hash、推理模板、采样、工具和评分脚本，给每项基准明示版本与 pass@k。复现实验由非训练者执行，报告方差、成本与子项失败，避免挑最好的一次。公开可核验日志/权重卡，发现污染则撤回受影响数字。

## QWEN-09｜Qwen2.5-VL uses a native dynamic-resolution ViT with window attention and multimodal RoPE. Why native resolution instead of fixed tiling, and what does MRoPE encode?

动态分辨率保持细小文字与画面长宽比，按图像内容产生不同视觉 token 数，比粗暴固定尺寸少丢信息；代价是长尾高分辨率推理成本和批处理不均。window attention 控制局部视觉计算，MRoPE 对多模态序列编码时间与空间坐标关系；需要测 OCR、定位、视频时序、延迟和 token 上限。

## QWEN-10｜Alibaba open-sources Qwen under Apache 2.0 while running a commercial cloud business. Walk me through the strategy, and tell me about an ambiguous technical decision you owned end to end.

开源许可促进开发者采用、微调、第三方部署和生态反馈；云端提供托管推理、弹性容量、企业安全/运维与模型更新获得服务收入。技术决策案例按真实经历叙述：列不确定选项、成本/质量实验、利益相关者、决定和复盘，不要虚构业务结果；许可范围与具体版本以发行条款核对。
