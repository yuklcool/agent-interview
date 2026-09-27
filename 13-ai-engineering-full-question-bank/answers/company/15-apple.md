# Apple｜逐题答案

对应原题库公司专项第 15 组，共 11 道。

## APPLE-01｜You need to run a ~3B-parameter language model on a phone with tight memory and power budgets. What changes versus serving the same model in a datacenter?

3B 参数 4-bit 权重理论约 1.5GB，加量化 scale、KV、激活和运行时显存；手机共享 RAM 且带宽/电池/温控约束，真实峰值要测。选硬件原生量化 kernel、分层加载/缓存、短上下文、轻量模型和及时释放；以冷启动 TTFT、持续 token/s、能耗、温升和多语言质量评估，而非服务器 GPU 峰值吞吐。

## APPLE-02｜Explain post-training quantization versus quantization-aware training. What breaks when you push weights to 2–4 bits, and how do you recover quality?

PTQ 用代表性校准集把已训权重/激活映射低 bit，成本低；QAT 在训练中模拟量化噪声，能让模型适应低精度。2–4bit 易受离群值、重要层和量化粒度影响，混合精度、分组 scale、敏感层保持高精度或蒸馏可恢复；比较真实设备内核、内存/能耗与难例质量。

## APPLE-03｜Estimate the KV-cache memory for a 3B on-device model at 4k context, and name the levers that shrink it.

公式 `2×层数×KV头数×头维×4096×每元素字节`；具体 3B 架构未给，先查层数与 GQA 配置。假设 28 层、8 KV 头、128 维、BF16，约 235MB（十进制），并发/系统缓存另计。缩小 KV 头、INT8/INT4 KV、滑窗/分块、短上下文、前缀淘汰需测试长依赖质量。

## APPLE-04｜Time-to-first-token for your on-device feature is 1.8 s. Walk me through diagnosing and fixing it.

用设备 trace 分解启动/模型加载、tokenization、系统提示构造、prefill、调度和首 token 内核，按冷/热启动及机型 p95 分层。缓存权重与安全前缀、压短 prompt、NPU/CPU 调度、编译融合和量化，避免热节流；每项测 TTFT、峰值 RAM、功耗及正确性。

## APPLE-05｜Your on-device model must emit valid, schema-conforming tool calls. How do you guarantee validity rather than hope for it?

采用 grammar/JSON-schema constrained decoding 在每步屏蔽非法 token，使语法有效；完成后宿主再校验 schema、业务规则、权限与实体解析，失败修复或拒绝。语法保证不等于操作正确，敏感动作要二次确认并使用幂等调用。

## APPLE-06｜You have one on-device base model but a dozen features: summarization, rewriting, reply suggestions, tone adjustment. How do you specialise without shipping a dozen models?

共享 3B base，加特性控制模板和少量 adapter/低秩增量；可合并到一版多任务模型或按需加载小 adapter，避免复制主干。评估特性间干扰、更新回归、磁盘/RAM 峰值和切换延迟，离线功能优先在设备端完成。

## APPLE-07｜How would you improve an on-device model using signals from user devices without collecting user content?

设备上记录用户主动纠错的本地统计、选择/撤销等聚合信号；优先本地适配，若需服务端学习，用明确同意、差分隐私聚合/安全聚合及最小化遥测，不收原文。防参与设备选择偏差与隐私预算耗尽，靠自愿标注、合成与设备内离线评测验证，不能声称任何聚合天然匿名。

## APPLE-08｜Design the routing layer that decides whether a user request is handled on-device, by a first-party server model, or by a third-party model.

分类请求的隐私敏感度、离线状态、设备支持、模型能力、用户授权及预估延迟；在设备能完成时本地处理，需要更强模型且获授权才转首方，第三方需明确数据范围与确认。路由可回退并记录不含内容的性能统计；以成功、隐私、耗电、p95 和成本测试边界情况。

## APPLE-09｜A user says “send Maya the photos from Saturday's hike.” Design the on-device path from that utterance to a structured app action with resolved parameters.

解析意图 send、照片时间/场景和收件人 Maya；在本地照片索引按日期/地点/语义召回，联系人消歧展示候选，预览所选照片及接收应用。发送前明确确认，调用系统分享 API 并回读成功状态，不能猜“Saturday”时区或同名 Maya；记录可撤销/失败重试。

## APPLE-10｜You're shipping notification summarization to hundreds of millions of users in 30+ locales, and you cannot log user content. Design the evaluation and regression-detection story.

构建经授权的多地区黄金集与合成通知，覆盖语言、应用类型、敏感/讽刺/多消息冲突；设备内评测可计算聚合通过率和质量信号，不上传原内容。发布按机型/地区灰度，用用户纠错/关闭率、崩溃、延迟、耗电与差分隐私聚合趋势检出回归；严重误摘要本地复现和自愿问题报告。

## APPLE-11｜Tell me about a time you had to make progress with incomplete information: you couldn't be told the full context of what you were building.

用真实 STAR：在保密/上下文不全时明确已知接口、不可见依赖与验收标准，提出可逆原型/契约测试，定期与有权限负责人核对；结果、风险和你后来改善的沟通机制。只讲获准公开的内容，不编项目细节。
