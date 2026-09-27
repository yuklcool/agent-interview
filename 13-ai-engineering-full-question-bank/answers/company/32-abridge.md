# Abridge｜逐题答案

对应原题库公司专项第 32 组，共 11 道。此处是工程面试思路，不替代临床和编码人员判断。参考 [CDC ICD-10-CM](https://www.cdc.gov/nchs/icd/icd-10-cm/index.html) 与 [HHS 云端 ePHI 指引](https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html)。

## ABRIDGE-01｜Turn a conversation into billable diagnosis codes. What is the accuracy bar, and how do you build to it?

诊断编码是高风险临床/计费行为，草稿必须由有资质临床人员和编码流程核验，不能从对话里推断未确认疾病。先 ASR/会话事实抽取→与病历核对→候选 ICD-10-CM 及证据/不确定性→规则校验（版本、特异度、排除）→人工确认。以严重错码/漏码、文档支持率、医生修改率和各专科切片设严格门槛，遵循当期官方编码指南。

## ABRIDGE-02｜The note should be ready before the clinician leaves the room. Build me the latency budget, and tell me where the money goes.

目标是结束就诊前有可核验草稿：流式 ASR 和说话人分离与对话同步，分段抽取事实，接近结束生成结构化笔记并核对缺口；语音端点、EHR 拉取、模型摘要和写回分别设 p95 预算。成本拆音频分钟、ASR/分离、长对话上下文、生成与人审；医师确认不应被“快”压缩，后台异步细化可保持交互。

## ABRIDGE-03｜The patient's chart already lists their medications. How would you use that to improve transcription of drug names, and how would you keep it from backfiring?

把当前处方清单当 ASR 候选词/重排序提示，改善罕见药名识别；仍用音频证据与剂量上下文验证，不能把病历旧药自动写成患者今天说了。对药名近音、停药、否定和新药做偏差测试，输出来源标记（说出/病历）与置信度，冲突让医生确认。

## ABRIDGE-04｜Design a service that turns the conversation into draft orders: labs, imaging, referrals, prescriptions, via tool calls against the EHR.

从会话提取明确意向，生成候选 lab/imaging/referral/prescription 结构化草稿，校验患者、过敏、剂量、单位、适应症及 EHR catalog 映射；医生逐项预览/签署后才写入。工具用最小权限、幂等键与回读状态，失败不可口头宣称已下单；记录证据、版本和审计，测误单/漏单/重复。

## ABRIDGE-05｜Walk me through writing a finished note back into Epic. What goes wrong?

用受支持 EHR 集成接口和患者/encounter 标识创建**草稿**笔记，检查字段映射、模板、作者、时区、版本并回读确认；签名由医生完成。常见故障是错误患者/就诊、并发改写、重复创建、丢格式、网络超时后不知提交状态；幂等及事务日志、权限审计与回滚/人工修复不可少。

## ABRIDGE-06｜Two good clinicians write different notes for the same visit. So how do you evaluate note quality at all?

不存在单一“标准措辞”，评价应抓事实集合：主诉、时间线、否定、用药、诊疗计划及来源，不要求逐字一致。多医生标注临床重要事实与严重错误，盲评可读性/完整性/节省时间，按专科和口音分层，记录分歧；任何未有证据的高风险事实比风格差异更严重。

## ABRIDGE-07｜Edit rate is the obvious measure of clinician trust. What does it hide, and what would you instrument instead?

低编辑率可能表示医生未认真读、照单全收、懒得修或模板过短；高编辑率也可能是个性风格。结合打开/核验来源、审阅时间、严重错误发现、补充项、签署率、后续更正和临床反馈，人工抽样盲评；不把更少编辑单独作为安全指标。

## ABRIDGE-08｜A generated note contains a medication the patient never mentioned. Treat that as a safety incident: how do you detect it before a clinician sees it?

在医生看到前把每项药物/剂量断言对齐到对话时间 span 或明确病历来源，检测无来源、否定冲突及旧处方混入；高风险断言自动标记并从草稿移除/待核。触发告警和事件复盘：保留受控轨迹、查 ASR/检索/生成/模板首个错误、补回归测试，必要时暂停发布。

## ABRIDGE-09｜Clinicians will not sign what they cannot verify. How would you build span-level provenance from every line of the note back to the conversation?

ASR 每词带时间/说话人和置信度，事实抽取标注原文 span，笔记每个临床断言保存来源类型、时间、病历资源版本和转换步骤；UI 点击句子能回放相应音频/文字。压缩/重写不能打断出处链，无证据标“需确认”，测 span precision/recall、核验时间和权限。

## ABRIDGE-10｜PHI is in every audio file, transcript and note you touch. How does that shape the architecture, and what can you send to a third-party model API?

全链路按 PHI 设计：最小权限/加密/隔离、审计、保留和删除政策、数据不用于未授权训练；第三方模型 API 只有在合同/适用 BAA、风险评估及最小必要用途获批准后才能接触 ePHI。不能默认去掉姓名就匿名；明确机构所在地区与具体合规要求，验证请求/日志/缓存/备份均受控。

## ABRIDGE-11｜Our audio is a clinic room: two or three speakers, background noise, accents, and a vocabulary full of drug names. How would you build and improve the ASR for that?

采集授权的临床室内多说话人数据，标注 speaker、药名/剂量与噪声场景，做回声/噪声处理、分离和流式 ASR，领域词表辅助解码但不可压过声学证据。按药物名、否定、剂量、说话人归属等关键错误率和延迟评估，主动学习医生纠错样本，持续防隐私泄漏和模型漂移。
