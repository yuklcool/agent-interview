# Sarvam AI｜逐题答案

对应原题库公司专项第 12 组，共 12 道。

## SARVAM-01｜Write code to measure a tokenizer's fertility across languages, and explain what you would do with the result.

对每种语言取同分布文本，按 Unicode grapheme/词边界计分母，`fertility = 总 token 数 / 词数`，同时报告每千字符 token、脚本、词长与 code-mix 切片。代码可遍历 `for lang,texts in corpus.items(): ids=tokenizer.encode(text,add_special_tokens=False)` 累计长度；需同样规范化和断句，避免不同语言的空格分词偏差。高 fertility 会抬高上下文和计费成本，可能需重训词表/扩充语料并验证英文退化。

## SARVAM-02｜Why is tokenization the first bottleneck for Indian-language LLMs, and how does a low-fertility tokenizer change the economics?

多种印度文字及复合字符若被英文主导词表切成许多 token，同样语义需要更多上下文、训练计算和生成时间。低 fertility 让预算覆盖更多文本和低资源现象，但大词表也增加 embedding/softmax 成本，不能牺牲罕见词鲁棒性。测每脚本、罗马化、口语混写与部署实际 token 成本。

## SARVAM-03｜How do you deploy a capable assistant on cost-sensitive or on-device hardware without a datacentre GPU? Walk through the efficiency toolkit.

先蒸馏到任务适配小模型，选 INT8/INT4 与量化感知训练，配合小 batch、KV 压缩/滑窗、缓存与受限上下文；端侧用支持的 NPU/CPU kernel、分段流式响应。针对低资源语言测准确、安全、每 token 能耗、内存峰值和温控持续性能；复杂任务可授权切换到本地服务器，离线隐私约束明确。

## SARVAM-04｜Design cross-lingual RAG: the knowledge base is in English and Hindi, but users ask in Tamil, Telugu or transliterated Hinglish.

查询做语言/脚本识别和转写归一，同时保留原文；多语 embedding 跨语召回+翻译后 BM25 双路，按 ACL 过滤、跨语 reranker、引用原文及必要翻译后生成。Tamil/Telugu/Hinglish 分层标注跨语相关性与无答案案例，衡量 Recall@k、引用支持率、实体/数字保真、p95；防翻译抹掉专名和跨语言权限泄漏。

## SARVAM-05｜Sarvam-M ships hybrid think/non-think modes and was post-trained with SFT then RLVR. How would you build that, and why RLVR over vanilla RLHF?

SFT 同时训练短答与受控思考格式，带模式 token；RLVR 利用可检验数学/代码奖励提升推理，弱标签不应覆盖非客观语用/安全任务。推理服务显式 thinking budget 和停止规则，比较各语言的正确性、延迟、成本，检测奖励漏洞及代码混写偏差；开放问题仍要人工偏好评估。

## SARVAM-06｜A regional government wants an assistant in a low-resource language with only a few thousand sentences of clean text. How do you adapt a model to it?

先与本地语言专家建小规模高质量语料、正字法/转写规范与保密许可；用多语基座、持续预训练或 adapter，平行数据与回译可辅助但需人工核查，防把低质合成数据放大。服务首版聚焦具体政务意图并接检索/规则，低置信转人工；测方言、数字/姓名、尊称、安全及公平，迭代主动学习。

## SARVAM-07｜Design a real-time voice agent for a citizen helpline in Hindi and three regional languages, targeting sub-250 ms perceived latency over a phone line.

电话音频先 VAD/降噪，流式 ASR 给部分转写，意图/检索与 TTS 并行准备，检测打断即时停止播报；把 250ms 定义为首个可听响应（可先短确认音），不承诺复杂最终答案 250ms。接入多语路由、电话音质、低带宽缓冲与人工坐席，权限和 PII 脱敏；测首音 p95、WER、任务完成、误转接与中断恢复。
```mermaid
flowchart LR
 A[电话流] --> B[VAD与流式ASR]
 B --> C[意图/检索]
 C --> D[流式TTS]
 D --> E[打断与坐席转接]
```

## SARVAM-08｜How would you evaluate an Indic LLM properly? Why is running translated English benchmarks not enough?

本地母语者编写原创题，覆盖脚本、方言、混写、文化/政务场景、数字单位及低资源知识；控制训练污染。译制英语题会留下英语知识分布、语法和歧义，不能代表真实使用。报告各语言任务成功、事实/安全、人工评分、token 成本与最差切片，评审者一致性和错例公开。

## SARVAM-09｜Build a Voice Activity Detector from scratch. How do you make it robust for phone-quality Indian-language audio?

用短帧提 log-mel 能量、频谱/神经特征，轻量分类器输出语音概率，阈值与 hangover 平滑避免切断弱辅音；噪声自适应、端点判断与回声消除处理电话信道。以真实语言/口音/背景噪声数据测漏检、误检、端点延迟、首音时延，保留无语音/嘈杂样本。

## SARVAM-10｜Whisper transcribes Hinglish poorly, often forcing output into one language or hallucinating. Why, and how would you build an ASR that handles code-mixed speech?

训练语料偏单语及转写规范会把混写语音强制译成单语，静音与噪声也易触发语言模型幻觉。收集授权的 Hinglish 真实电话语料并标注脚本与切换点，训练多语/代码混写流式 ASR、解码中保留原词/专名，VAD 后过滤空白音频。按语种转换区间 WER/CER、专名、幻觉率和延迟测。

## SARVAM-11｜Bulbul-style TTS has to speak code-mixed, mixed-script text naturally. What are the hard parts of text normalization and prosody for Indian-language TTS?

文本正规化必须决定数字、日期、货币、缩写、外语品牌的读法，并在多脚本/罗马化间映射发音；标注语言 span 与音素，跨语切换时保持说话人音色、重音/停顿和自然语速。测试易歧义金额/身份号的准确朗读、母语者自然度、发音一致性与流式首音；敏感号码先做隐私策略。

## SARVAM-12｜A state agency wants to move a paper-and-call-centre welfare-scheme service onto a multilingual assistant, on-prem for data residency. How do you scope and ship it?

从资格查询、申请状态与材料清单三种高频意图试点，梳理官方规则来源和更新时间，纸件 OCR/双人校验后建带版本和地区的知识库。内网部署多语 ASR/RAG/TTS，身份核验后才访问个人记录；不确定或政策冲突转人工，不自动承诺福利资格。按任务完成率、申诉/误导率、人工接管与语言公平做小范围试运行和审计。
