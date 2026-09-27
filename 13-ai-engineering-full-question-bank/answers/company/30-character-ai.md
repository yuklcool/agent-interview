# Character.AI｜逐题答案

对应原题库公司专项第 30 组，共 12 道。

## CAI-01｜Live coding: build the prompt for the next turn under a fixed token budget. The catch is our prefix cache.

预算 B 先固定不变前缀（系统/角色定义）再留最大输出和最新用户消息，剩余用于近几轮原文、结构化摘要和少量长期记忆。前缀缓存要保持 token 序列、顺序、模板版本完全相同，不能每轮把时间戳/摘要插入前面；尾部动态内容可截断。按 persona 保真、长程引用、TTFT 和缓存命中评估。

## CAI-02｜A conversation runs past the context window. What do you keep, and how do you decide?

保留系统安全/角色核心、用户明确偏好与未完成任务、近期原文和经证据支持的远期摘要；长期记忆带来源、时间、置信度和可删除性。按相关性与遗忘代价选，摘要可分层更新但防“摘要漂移”；在历史关键信息召回、 persona 稳定和隐私删除上做长会话测试。

## CAI-03｜Our serving cost is dominated by KV cache, not weights. Get it down by an order of magnitude and tell me what you give up.

KV 公式 `2×层×KV头×头维×token×并发×bytes`；先利用 GQA/MLA（架构支持时）、KV INT8/INT4、滑窗/选择性保留、前缀共享与分层卸载，合计能否 10x 需真实组合测而非简单相乘。代价是长依赖遗忘、量化精度、缓存命中隔离和卸载延迟；分会话长度/角色记忆测质量与 p95。

## CAI-04｜Dialogues here average around 180 messages. Design the cache that sits between turns.

跨轮缓存以模型/模板/角色前缀的内容 hash 为键，动态会话 token block 以用户/会话隔离并带引用计数、TTL 与版本。用户新消息只 append KV，修改历史/系统/权重或删除隐私需失效；并发续聊用乐观版本避免分叉写冲突。监控命中率、节省 prefill、显存占用与泄漏。

## CAI-05｜You train natively in int8 rather than doing post-training quantization. Defend that.

原生 int8 训练让模型在低精度算子/动态范围里适应，训练与推理数值路径更一致，可减少 PTQ 的质量损失；需处理量化 scale、累加精度、梯度/优化器主权重和异常值以保持稳定。比较相同计算预算的 BF16→PTQ 与 int8 训练在困惑度、对话质量、能耗和故障率，不是所有算子都必须 int8。

## CAI-06｜Estimate what one message costs us to serve, and tell me which lever moves it most.

每消息成本按缓存命中后的输入 token prefill、输出 token decode、KV 占用时间、并发冗余和网络/安全服务分摊：`$/消息≈GPU秒×全包单价÷有效利用率`。用真实消息长度/180 轮分布估而非均值，通常长会话 KV/输出长度是关键；比较缩短上下文、量化 KV、前缀缓存、小模型路由的质量/成本弹性。

## CAI-07｜Design discovery and search across millions of user-created characters.

为角色建立名称/描述/标签、embedding、语言、公开权限与质量/安全元数据，词法+向量召回后按相关性、满意度和新角色探索排序；个性化需限制敏感画像和未成年人可见内容。反作弊/重复角色归并，按新作者/语言评估发现率、有效会话和负反馈，不用纯聊天时长优化。

## CAI-08｜Users complain that characters drift out of persona after a long session. Diagnose it.

逐轮检查角色定义是否被截断、摘要是否改写设定、缓存/模板版本是否错、用户持续诱导及后训练数据的 persona 覆盖；复现长会话位置/长度分层。把不可变角色约束固定前缀，远期记忆结构化、按需重注入并训练对抗/长期一致性；测角色事实保持、情节连贯与安全，不让重复角色提示挤掉会话。

## CAI-09｜Engagement metrics and wellbeing metrics disagree. How do you build a system that resolves that?

不能只最大化聊天时长：定义用户自报满意、健康边界、过度依赖/打断睡眠等可测护栏，伦理和专家团队定严重事件处理。用多目标约束优化，重大 wellbeing 风险直接政策层限制；A/B 分龄/高使用切片并人工审查，给用户提醒、退出和报告通道，避免靠模型生成“关怀”掩盖诱导。

## CAI-10｜Design the safety system for open-ended character chat.

内容/角色创建审核、输入与输出风险分类、上下文中的自伤/未成年/性内容等政策状态、流式生成中断和事后抽检/举报复核；不同年龄层不同功能/曝光边界。人格对话的长程情境需人工评估，监控漏检/误拦和复发用户，保护隐私、允许申诉。

## CAI-11｜When is intervening during decoding better than filtering the finished reply?

当危险内容一旦流出便不可收回，或输出前缀会把模型引向不可逆违规则在解码中做 token/短片段约束、语义检测与安全替代；成品过滤可拦整段但可能已流式播出。逐步干预也会延迟/误伤且被对抗绕过，需工具层政策、最终检查和人工反馈共同作用。

## CAI-12｜Design age assurance for a platform where the under-18 experience is fundamentally different.

按法律与产品要求做分层年龄保证：自报/账号信号用于低风险体验，关键功能用合规第三方/家长同意等更强验证，尽量不存身份证原件。默认未成年保护、功能/角色/推荐和数据保留隔离，支持申诉与误判纠正；测绕过率、隐私侵扰、公平错误率，规则随地区合规复核。
