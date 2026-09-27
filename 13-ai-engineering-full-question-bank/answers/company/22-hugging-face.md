# Hugging Face｜逐题答案

对应原题库公司专项第 22 组，共 11 道。

## HF-01｜`transformers` famously repeats code: each model gets its own self-contained modeling file. Defend that decision, then critique it.

每模型独立 modeling 文件让架构细节可读、社区维护者能局部审查，新模型不受巨型继承树限制；重复也导致 bug 修复不一致、API 漂移和测试成本。抽象稳定底层组件/工具函数与共同契约，保留架构级显式实现，配跨模型回归测试而非强行统一所有模型。

## HF-02｜Why did Hugging Face create safetensors when pickle-based checkpoints already worked everywhere?

pickle 反序列化可执行任意代码，下载未知 checkpoint 有远程代码执行风险；safetensors 只存张量数据和元信息，可在加载前校验偏移/形状，支持按需读取。仍需验证模型代码、来源签名与依赖安全，格式安全不等于模型内容可信。

## HF-03｜A user loads a 2 TB dataset with `datasets` on a 64 GB RAM machine and it works. How? And when does it stop working?

datasets 常用 Arrow 列式文件与 memory mapping，操作系统按页读取，2TB 不会一次全入 64GB RAM；流式模式可逐条迭代远端 shard。随机 shuffle、复杂 map、全量排序/转换、索引/缓存和高并发读会耗内存/磁盘，需批处理/分片与监控 page faults。

## HF-04｜Walk me through what actually happens when someone calls AutoModelForCausalLM.from_pretrained(…, device_map=“auto”, torch_dtype=“auto”).

Auto 类先解析 config/model type，定位模型实现、加载权重索引/shard，`torch_dtype=auto` 按配置/权重推断；`device_map=auto` 根据可用设备/内存估算放置，可能 CPU/磁盘 offload。初始化与加载过程受版本和 trust_remote_code 影响；核验最终 `hf_device_map`、实际 dtype、峰值 RAM 与推理行为，不把 auto 当最优性能保证。

## HF-05｜Compare BPE, WordPiece and Unigram tokenization. Why is `tokenizers` written in Rust, and what tokenizer bugs bite people in practice?

BPE 反复合并高频字节对，WordPiece 逐步选子词以词汇概率/似然准则，Unigram 从候选词表删减优化概率模型；边界和未知字符策略依具体实现。Rust 提供快速并行 tokenization 与内存安全。常见 bug：训练/服务规范化、special token、空格前缀、Unicode、offset mapping 与 chat template 不一致；用多语言回归。

## HF-06｜What problem do chat templates solve, and what goes wrong when they're ignored?

chat template 将 role、工具调用/结果、开始/结束与 assistant generation prefix 转为模型训练时见过的 token 序列。忽略它可能令角色边界失效、工具参数格式错或模型把用户文本当系统指令；固定 tokenizer 与 template 版本，测试多轮、工具和截断。

## HF-07｜Fine-tune an 8B model on a single 24 GB GPU. Walk me through the memory maths and the exact stack you'd use.

8B BF16 权重约 16GB，Adam 全参训练还需梯度/优化器远超 24GB。4-bit QLoRA 权重理论约 4GB 加 scale、LoRA 参数/优化器、激活和 KV，配梯度检查点、小 microbatch、累积、paged optimizer 可试；具体显存由序列长度/层数决定。先 profile 峰值与 loss，验证量化/LoRA 相对全精度的质量。

## HF-08｜You're building a web-scale pretraining corpus (FineWeb-style). Walk me through the pipeline and how you decide whether each filter earns its place.

抓取保留 URL/许可与时间，解析正文、语言识别、质量/安全/PII 过滤、exact/near dedup、跨站重复与基准污染检查，然后分层采样/分片发布。每个 filter 做保留率与抽样人审、语言/领域覆盖和小模型训练消融；过严过滤会损害长尾和少数语言。版本化参数可回溯单文档来源与删除请求。

## HF-09｜Design the Hugging Face Hub: millions of git repos where individual files are tens to hundreds of GB.

元数据和权限在控制面，Git 对小文件/版本管理，巨大权重/数据块用内容寻址对象存储、分块上传/断点续传与 CDN；commit 引用不可变对象，原子发布清单。带宽、热度缓存、配额、病毒/恶意模型扫描、访问控制与删除传播是关键；测全球下载 p95 与高并发热门模型。

## HF-10｜Design the serverless inference layer: any of thousands of Hub models can receive a request at any moment.

热模型常驻、温模型共享池、冷模型按需加载/排队，路由依据权重大小、硬件和流量预测；大模型冷启动可达分钟级，须给明确 SLA/失败状态。租户隔离、配额、版本固定、量化/批处理与缓存，监控 TTFT、载入耗时、GPU 利用和拒绝率；长尾模型可转专用端点。

## HF-11｜A community contributor opens a PR adding a new model architecture to `transformers`. You're the reviewing maintainer: what do you check, and how do you handle the interaction?

审查 config/权重映射、forward/generate/cache 语义、chat template、分词器、梯度与不同设备/dtype、序列/批量边界、安全远程代码；要求最小可复现测试、文档和许可证。与贡献者明确接口约定、指出具体失败与修复建议，保持架构特色，尽量不让重复模板掩盖错误。
