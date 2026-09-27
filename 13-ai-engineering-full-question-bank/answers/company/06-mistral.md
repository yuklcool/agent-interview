# Mistral AI｜逐题答案

对应原题库公司专项第 6 组，共 8 道。

## MISTRAL-01｜Pair-programming: build a service that takes a user question, enriches it with data from a third-party API, and answers via a chat-model API. How do you structure it?

用三层：API handler 验证输入/鉴权，enrichment adapter 调第三方 API（超时、重试、缓存、熔断），answer service 将可信数据与原始问题分别结构化喂模型。第三方内容视作不可信数据，做长度/HTML 清洗、来源时间戳，禁止其中的“指令”支配系统提示；模型只基于已取数据回答并附来源。契约测试模拟超时/空结果/429，集成测试评估事实性、成本与 p95。

## MISTRAL-02｜Mistral 7B shipped with grouped-query attention and sliding-window attention. What does each buy you, and what does each cost?

GQA 共享多个 Q 头对应的 KV 头，减少 KV 内存和生成阶段带宽，代价是头间表达独立性减少。滑动窗口只注意最近 W token，长序列单层 attention/缓存不随全上下文线性增大，但丢失远处细节；跨层信息可传播却不能保证准确全局记忆。选 W 与 KV 头数通过长依赖质量、首 token/每 token 延迟和显存基准共同决定。

## MISTRAL-03｜Explain how a Mixtral-style sparse mixture-of-experts model works. Why does a ~47B-parameter model run at roughly the cost of a ~13B one?

门控路由为每个 token 选少量专家，非激活专家不参加该 token 的主要 FFN 计算；总参数约 47B、活跃路径常按约 13B 量级讨论，但真实 FLOPs/吞吐还受注意力、路由、all-to-all 和 batch 影响，不能直接等同 13B dense。容量限制与负载均衡防热点，专家并行使显存仍需容纳全部权重，低 batch 可能受通信拖累。

## MISTRAL-04｜Estimate the KV-cache memory for serving Mistral 7B, and design the rolling-buffer cache that sliding-window attention enables.

KV 估算式 `2×L×n_kv×d_head×T×B×bytes`。Mistral 7B 常见配置按 32 层、8 KV 头、128 维、BF16、窗口 4096 计，单序列约 0.54GB；窗口上限内线性增加。环形 buffer 用绝对 position 控制写指针 `pos % W`，防覆盖尚需注意的 token；按 block/序列管理取消与重用，位置编码用真实位置而非槽位索引。具体模型版本先核配置。

## MISTRAL-05｜You need to quantize a model for a customer's hardware. How do you choose a scheme, and how do you prove quality hasn't regressed?

先收集硬件显存、算力、内核支持与目标 p95；比较 FP16/BF16、INT8、INT4（权重独立或含激活）以及 KV 量化。选有代表性的校准集，针对异常值和长上下文测困惑度、任务成功率、幻觉/拒答、安全与分语言切片；基于真实并发测首 token、token/s、内存及每请求成本。混合精度保护敏感层，设置可接受质量下降阈值和回滚。

## MISTRAL-06｜How does function calling actually work with an LLM, and how do you make it reliable enough for production agents?

模型输出受约束的结构化 tool name/args，宿主验证 JSON schema、授权与业务不变量后执行，返回结果供模型继续推理；模型文本本身没有工具权限。用工具白名单、幂等键、超时重试、参数化 API、人工审批高风险写操作和审计日志；评估调用选择、参数正确性、失败恢复、越权与提示注入。

## MISTRAL-07｜After fine-tuning on a customer's task, target accuracy is up but the model got worse at everything else. What happened and what do you do?

先确认旧任务的真实回归而非评测漂移：比较固定数据/模板和训练配置、分语言/领域切片。可能是小任务数据过拟合、灾难性遗忘、SFT 学习率过高或混入错误标签；混合通用 replay、降低 LR/步数、LoRA 冻结主干或多任务训练，必要时任务路由到专用 adapter。发布门槛要求新旧任务和安全同时达标。

## MISTRAL-08｜Design an on-prem deployment of an open-weight model for a European bank that cannot send data to any external API.

银行内网部署需离线镜像/权重校验、驱动与 GPU 容量评估、私有 registry、无外联的模型与 embedding/reranker、内部 IdP 与文档 ACL 同步。数据驻留、密钥、日志脱敏、审计和模型版本审批落实到网络与存储；受控更新包扫描签名，灾备/回滚演练。按峰值 token 与并发压测容量，使用本地评测集和人工审核验证检索权限及拒答。
