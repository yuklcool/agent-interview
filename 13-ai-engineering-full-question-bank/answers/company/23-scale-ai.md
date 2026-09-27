# Scale AI｜逐题答案

对应原题库公司专项第 23 组，共 12 道。

## SCALE-01｜Build the task-lifecycle core of an annotation platform. Start simple; I'll add consensus of k annotators, then priority re-review, then annotator cooldowns.

状态机 pending→assigned→submitted→reviewed→accepted/rework，任务/标注/审查分表并记录版本、审计与租约。k 人共识时独立派单且隐藏先前标签，聚合按类别/置信度，争议升级专家；优先复审按风险队列，cooldown 在派单事务中检查 annotator 最近任务/时间，防竞争重复。测幂等提交、过期租约与可追溯。

## SCALE-02｜Given annotation sessions as (start, end) timestamps, return the peak number of concurrent annotators and the intervals at peak load.

把每会话转换成 (start,+1),(end,-1)，若区间为 [start,end) 则同一时间先处理 end，再处理 start；排序扫描事件，记录最大并发的连续时间段并合并相邻等值段。时间 O(n log n)，空间 O(n)；过滤负长度/时区/重复边界，空输入返回 0 与空区间。

## SCALE-03｜Compare SFT, RLHF, DPO and RLVR for improving an instruction-tuned model. What data does each need, and when would you pick which?

SFT 需专家示范，提升格式与基础指令；RLHF 需偏好训练奖励模型及在线采样/优化，适合主观目标但复杂；DPO 需成对偏好直接优化，工程简单但依赖数据覆盖；RLVR 需可靠可验证奖励（数学/代码），利于规模化但易奖励投机。按任务主观性、标注/算力与安全约束组合使用，固定外部评测防过拟合。

## SCALE-04｜We sell RL environments. Design one for “book a multi-city trip in a web travel app”, specify the reward, and tell me how you stop the policy hacking it.

旅行环境模拟航班/酒店搜索、预订、支付与取消 API，工具状态可重置、带价格/时区/库存变化；奖励仅在最终多城市行程满足日期、预算、衔接、支付授权与真实预订状态时给，部分奖励不能鼓励假确认。隐藏测试改变库存、恶意网页、超时与重复调用，审计订单/工具调用防 policy hacking 和奖励函数漏洞。

## SCALE-05｜Design an end-to-end pipeline producing RLHF preference data for a frontier lab: 100k prompt-response comparisons a week, with quality guarantees.

每周 10 万对先按任务/语言/风险分层采样并去重，模型生成多个候选，标注平台随机化顺序、盲化模型来源、按资质分配；双标/金标/争议仲裁估一致性和系统偏差。PII 清理、合规、反作弊、标注版本与来源链，按切片看质量、吞吐、时效和人审抽样，重标有争议群体。

## SCALE-06｜Design a private LLM benchmark and leaderboard (SEAL-style). How do you keep it trustworthy as labs optimise against it?

私有集定期增补且切分公开开发/封闭测试，控制提交次数、模板与工具配置，记录模型 hash/采样和运行轨迹；防训练污染、泄漏与人工代答，评审高分异常与严重错误。报告分层能力、置信区间、成本/时延和失败案例，发布分数前让独立审计复现。

## SCALE-07｜Your annotators have no ground truth: the tasks are subjective preference judgments. How do you measure and improve label quality?

主观任务没有绝对真值，先写可操作 rubric 与锚点样例，对少量任务双盲多标，量一致性/分歧类型和标注者漂移；分歧可能来自合理多元偏好而非标注差。专家仲裁并保留分布标签，训练时按可靠度加权但防压制少数观点；定期复训与人审。

## SCALE-08｜How would you benchmark an LLM agent's tool use, say, for enterprise workflows composing 10+ APIs?

构建模拟企业 API 环境，明确用户角色、ACL、状态变化与 10+ API 的依赖链；按最终环境状态而非模型自报评分。注入错误/429/超时、隐藏字段和恶意工具返回，测成功、越权、误写、恢复、工具预算与 p95；固定种子/版本、多次采样和人工复核可疑成功。

## SCALE-09｜An eval pipeline you own suddenly reports a 6-point drop for a customer's model between Tuesday and Wednesday. The model didn't change. Debug it.

模型未变先查评测集/样本、prompt/template、采样随机种子、判分器、工具模拟器、依赖、权限和基础设施版本；重放同一原始请求，对比首个输出差异点。排查数据漂移、第三方服务与评估缓存，检查置信区间；找到根因后版本锁定和回归告警，不能直接把 6 分降幅归因模型。

## SCALE-10｜Some annotators are pasting your tasks into ChatGPT and submitting the output. How do you detect and handle it?

检测异常速度、粘贴行为/相似答案、隐藏哨兵题和与已知模型输出高相似度，但不要凭单一特征惩罚；抽样人工复核并给标注者申诉。保护敏感任务禁止外部上传，最小化界面数据、培训与合理工作量/薪酬，调整奖励机制；记录证据与数据污染回滚。

## SCALE-11｜An enterprise wants a document-Q&A assistant over 2M internal documents, pilot in four weeks, and their security team forbids data leaving their VPC. Scope and design it.

四周先选权限明确的高价值文档/问题，VPC 内部署 embedding、索引、reranker、模型和监控，原始/索引/日志均不出 VPC；同步 ACL 与删除，抽样黄金集含越权和无答案。第 1 周数据/权限与基线，第 2 周检索，第 3 周答案/安全，第 4 周试点与压测；低置信拒答、人工反馈和回滚，按引用正确率/成功率/p95 验收。

## SCALE-12｜A robotics customer asks for 50,000 hours of manipulation demonstrations across 12 tasks and three embodiments. Design the collection pipeline, and tell me what makes one demonstration worth keeping.

按 12 任务×3 embodiment 分层设设备、操作者、场景/物体/失败样本配额，传感器时钟与动作坐标统一，采集许可/隐私/安全流程。每条示范保存视频、状态、动作、成功终态、标定和质量标记；自动检查丢帧/时间错位/重复，再人工抽样复核。值得保留的示范应轨迹完整、任务成功或高价值失败、覆盖新状态且可重放，不能只靠时长凑 5 万小时。
