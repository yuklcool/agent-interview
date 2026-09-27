# ElevenLabs｜逐题答案

对应原题库公司专项第 31 组，共 8 道。

## ELEVEN-01｜Write a service that proxies streaming TTS to a browser and cancels cleanly when the user navigates away.

浏览器用 fetch 流/SSE 或 WebSocket 接音频帧，服务端鉴权后转发上游 TTS 的分块和时间戳，应用背压防内存增长；浏览器导航/AbortController 断开时服务器向上游发送 cancel 并释放合成任务/配额。首音和总音频分别计量，测试半开连接、重连重复播音及缓冲区溢出。

## ELEVEN-02｜Serving real-time TTS is a different capacity problem from serving a text LLM. Why, and how do you plan capacity?

TTS 按音频时长、采样率、声码器实时因子、同时会话与首音流式延迟规划，生成输出 byte/s 与音频抖动缓冲不同于文本 token；声音克隆/多语言模型和 GPU/CPU 也有不同瓶颈。容量按峰值实时并发×每秒合成算力+冗余，测首音 p95、连续播放无卡顿、取消释放和每分钟成本。

## ELEVEN-03｜Design the safety stack for voice cloning: consent, watermarking and abuse response.

克隆前验证声源拥有者明确同意和用途，保授权记录/撤回；敏感人物/未成年人及欺诈场景做身份与风险限制。生成音频嵌可检测但可失效的水印/来源标记，配内容政策、速率/异常监测和快速滥用下架、通知、申诉流程；水印不能替代访问控制或取证。

## ELEVEN-04｜Budget the end-to-end latency for a real-time voice agent. Why is time-to-first-audio a different problem from an LLM's time-to-first-token?

语音链路 VAD 端点、流式 ASR、意图/工具/LLM、文本规范化、声学模型与声码器、传输缓冲；首音需产生可播放的连续音频片段，首 token 只是文字，可能仍要等发音上下文和编码。部分 ASR/推理并行、短首句和流式 TTS 降等待，测用户感知首音、打断停止和完整任务，不以“嗯”刷指标。

## ELEVEN-05｜Text normalisation is where TTS quality actually dies in production. Walk me through it.

数字/货币/日期/地址/单位/缩写/URL/专名在语境下有多种读法，要先检测语言与脚本、实体类型，再规则+模型消歧成规范发音/音素；低置信保原文或确认。训练/测试加入语言混写、医疗/法律/金融高风险数字，测发音错误、断句与自然度，版本化词典防回归。

## ELEVEN-06｜Design the dubbing pipeline: an English video becomes Spanish, same speakers, same timing.

ASR 逐句转录与说话人分离，翻译保语义/术语与语气，按目标时长做受限改写，再用经同意的声线合成西语、对齐口型/镜头节奏并混合背景音。人工审核专名、笑声/情绪、文化适配与字幕同步；测语义准确、时间偏差、声线一致和版权/同意边界。

## ELEVEN-07｜A hospital group schedules and confirms outpatient appointments by phone, manually, with three staff on a rota. Design what we would build for them.

先映射预约/确认/取消的真实 SOP、EHR/排班接口和身份核验；语音 agent 只读查询可自动，写入需复述日期/地点/医生并确认，幂等预订与后端回读。病情、紧急/不确定或多次失败转三位工作人员之一，交接摘要脱敏；小范围试点测预约成功、误订、转人工与工作时段容量，医疗数据留存合规。

## ELEVEN-08｜A contact centre wants to replace its IVR with voice agents. Run the engagement.

发现 IVR 失败点和通话类型分布，先做低风险意图（查询/转接）黄金集，电话音质/语言/口音与攻击测试；集成 CRM、身份/支付政策和人工坐席。按阶段灰度，量化一次解决、误操作、首音/打断、投诉与每通话成本，保人工随时接管与回滚；不能只用语音自然度决定替换。
