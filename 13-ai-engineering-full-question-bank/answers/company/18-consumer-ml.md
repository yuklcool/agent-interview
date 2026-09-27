# 消费级机器学习公司｜逐题答案

对应原题库公司专项第 18 组，共 14 道。

## CONSUMER-01｜Implement a streaming top-k with a bounded-memory sketch; implement a sliding-window rate counter.

top-k 用 Space-Saving m 槽位保近似频数与误差，精确无界 key 做不到固定内存；滑动窗口计数用按秒环形桶，更新对应时间戳桶、过期清零，查询求最近 W 桶。桶粒度带边界误差，事件时间迟到另需水位线；分布式合并需二次计数或可合并 sketch。

## CONSUMER-02｜Your offline metric improved but the online A/B did not. Enumerate the reasons this happens and how you would tell them apart.

先验证实验随机化、SRM、触发人群和统计功效，再核对离线指标是否代表业务目标；检查位置偏差、数据泄漏、训练服务特征、冷启动、延迟/缓存及竞争/网络效应。按分群、时间、曝光链路做差异归因，回放和小流量实验隔离原因；报告置信区间与护栏，不把不显著说成没效果。

## CONSUMER-03｜Explain position bias in ranking data and how you would debias training.

高位更易被点击，即使相关性相同；直接用点击标签训练会放大已有排序。用随机小流量位置扰动估 examination propensity，逆倾向加权/截断或双稳健估计，并结合人工相关性标注。按位置/设备/群体测校准和在线目标，防高方差权重及干扰。

## CONSUMER-04｜How do you design a feature store, and what causes training/serving skew?

离线/在线共用特征定义、键、事件时间和版本；离线点时间回放避免未来数据泄漏，在线低延迟 KV 读取并设新鲜度/缺失默认。偏斜来自计算逻辑、窗口边界、空值、时间滞后、编码和 join 不一致。以线上请求影子回放比对特征值和模型输出，监控新鲜度、空值与 schema 变化。

## CONSUMER-05｜Design the ETA prediction system for a ride-hailing marketplace. What features, what model, how do you serve it in <100 ms?

按路线/交通、时段、天气、司机与上下车位置构造特征，训练分段/图网络或梯度提升基线预测行程与等待时间的分布。路由服务先给候选路径，在线特征缓存使 <100ms，异常时退回路段历史分位数；按地域/高峰/恶劣天气测 MAE、p90 误差、校准与延迟，避免训练测试同一行程泄漏。

## CONSUMER-06｜Design a personalised feed ranking system with a two-stage candidate generation and ranking architecture.

候选生成用关注、协同、内容相似和热门探索控制千万级池，精排使用用户/内容/上下文与多目标预测，重排加新鲜度、多样性、频控和安全。曝光日志训练需位置/选择偏差校正，实时特征处理已读/负反馈；评估 NDCG、留存、满意度、公平覆盖和 p95。

## CONSUMER-07｜Design a content recommendation system for a streaming catalogue, including cold-start for new titles and new users.

新标题靠剧情/演员/语言、音视频表示做内容召回并给予受控探索；新用户靠明确偏好、会话行为与热门多样化。协同过滤与内容召回混合，精排预测有效观看与长期满意，重排控制重复/年龄限制。分新旧用户/标题测观看完成、留存、曝光覆盖及冷启动学习速度。

## CONSUMER-08｜Design “people you may know” / job-recommendation ranking at a professional network's scale.

社交图共同联系人/职业/技能产生候选，job 推荐再加资历、地点、薪资和资格过滤；排序预测有意义连接/申请与长期结果。强制隐私可见性与“不要推荐”设置，防从共同好友泄露私密关系；离线按新用户/弱连接分层，线上测接受率、申请质量、负反馈和公平。

## CONSUMER-09｜Design dynamic pricing / surge for a two-sided marketplace and describe the feedback loops that can go wrong.

价格受需求、供给、等待时间和地理约束影响，目标是在乘客体验与司机供给激励之间平衡；可用需求预测+约束优化/实验，而非盲目最大化单次收入。涨价会改变需求/供给数据本身，产生反馈回路和跨区域外溢；设置上限、透明展示、应急规则与因果评估，监控取消/等待/收入公平。

## CONSUMER-10｜Design a visual search system: user uploads an image, you return visually similar in-catalogue items.

上传图像脱敏/安全检查、检测主体和视觉编码，ANN 检索目录商品向量，再用类别、库存、颜色/价格和区域约束重排；多目标/复杂背景可裁剪多个候选区域。离线测 Recall@k、精排准确与零结果，线上转化和延迟；目录更新与删除要及时同步索引。

## CONSUMER-11｜Design a fraud-detection system with heavy class imbalance and an adversarial opponent.

用真实基率下的 PR、成本曲线和固定误报预算评估，模型融合设备/交易/图网络特征，在线低延迟打分；高风险拦截，中风险二次验证/人工复核。欺诈标签延迟、对手适应和概念漂移需时间切分、主动标注与规则快反；监控受影响正常用户和群体误伤。

## CONSUMER-12｜Design an LLM-powered customer-support assistant on top of an existing help centre, with escalation to humans.

帮助中心按版本/权限切块，混合召回、重排并带引用回答；意图分类决定能否直接答、是否调用只读账户工具，个人数据必须授权。低置信、投诉/敏感或多轮无进展转人工并提供上下文摘要；评估正确解决率、引用支持、升级率、CSAT、成本和注入。

## CONSUMER-13｜How do you monitor a deployed ranking model for drift, and what triggers a retrain?

监控输入/特征分布、embedding、候选覆盖、标签延迟后的校准/排序质量及新旧用户切片；分布漂移只是告警，不能单独证明质量下降。触发再训需样本充分、线上目标/公平护栏恶化或业务规则改变；先回放和离线验证，再灰度/回滚，保留模型/特征版本。

## CONSUMER-14｜Tell me about a model you shipped that made a measurable business difference, and one that did not.

准备两个真实故事：有效模型讲基线、实验随机化、指标与业务价值、个人贡献；无效模型讲离线/线上差异、如何定位、停止或改造及吸取的经验。只引用可核实数字，不把相关性当因果。
