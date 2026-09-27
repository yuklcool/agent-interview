# Waymo｜逐题答案

对应原题库公司专项第 34 组，共 12 道。安全部署须依据实际运行设计域和独立验证。

## WAYMO-01｜In NumPy, compute minADE and minFDE for multi-modal trajectory predictions with variable-length ground truth. No Python loops.

设 pred 形状 [B,K,T,2]，gt [B,T,2]，mask [B,T]；`d=norm(pred-gt[:,None],axis=-1)`，每 mode ADE=`sum(d*mask[:,None],axis=-1)/max(sum(mask),1)`，FDE 用每样本 `last=mask.sum(-1)-1` gather 最后有效帧距离，最后分别沿 K 取 min。无有效帧需排除/报错，ADE 与 FDE 的最优 mode 可不同；若要求同一 mode 需明确定义。全程 NumPy broadcasting/gather 无 Python 循环。

## WAYMO-02｜Modular perception, prediction and planning, or end-to-end learned driving? Make the case, then tell me what you would actually build.

模块化感知/预测/规划便于接口诊断和硬约束，端到端可能学到联合表示并减少手工接口信息损失；实际可用混合：学习式感知/预测与候选规划，独立安全校验和可解释 fallback。以场景覆盖、闭环安全、延迟和故障归因决定，不凭单一离线 loss 宣布路线优越。

## WAYMO-03｜Design the output representation for a behaviour prediction model. What metrics would you gate it on?

预测多模态未来轨迹、每模式概率、参与者交互和不确定性，表示可用轨迹点/样条与时间戳、物理约束；概率需要校准，模式多样性不能只是同一路径微扰。门槛按 minADE/minFDE、miss rate、概率校准、碰撞风险与难例闭环 planner 影响分层，尤其行人/骑行者。

## WAYMO-04｜Where do vision-language models and foundation models genuinely help in an autonomy stack, and where are they a liability?

VLM 可辅助场景语义标注、长尾检索、仿真参数和离线评估/解释；在线安全闭环要求确定性延迟、几何精度、校准和可验证约束，开放式语言输出不能直接操舵。模型可能幻觉、域外失效或泄露训练偏差；用受控接口/安全监视器与真实场景数据验证增量。

## WAYMO-05｜Budget the compute and latency for the onboard stack. What breaks when a model gets bigger?

从传感器采样/同步、感知、跟踪/预测、规划到控制列每阶段 p99 及 CPU/GPU/内存预算，留安全监控与最坏情况冗余。模型变大增加功耗、温升、延迟、内存带宽竞争，可能错过控制周期，即使平均精度提高也不可用；profile 真实机型/天气/拥挤场景，超时降级到安全状态。

## WAYMO-06｜You have hundreds of millions of fleet miles. How do you find and use the rare scenarios that matter?

用场景触发（近失、急刹、稀有物体、地图变化）、embedding 相似检索与不确定性选择，去重并保留自然分布基线；人工复核/仿真扰动构造高价值长尾。数据分区按场景/城市/时间防泄漏，评估难例闭环风险和误报而非只看里程数，避免选择偏差影响安全声明。

## WAYMO-07｜Design a system that finds driving segments similar to a given one across the entire fleet archive.

从传感器对齐后的时段提交通参与者轨迹、地图拓扑、天气/光照和交互行为表示，分层元数据过滤+ANN 候选，再时序相似度/轨迹动态重排；保原始视频和地理时段权限。按专家标注相似场景 Recall@k、覆盖与检索延迟评估，不能仅依全局视觉 embedding。

## WAYMO-08｜You are opening in a new city. Structure the safety case.

定义新城市运行设计域：道路/法规、天气、交通参与者和地图，做数据采集/本地标注、场景库与危害分析；仿真/封闭场/影子/有限运营逐级验证。每层有安全门槛、置信区间、应急响应、远程协助/最小风险状态与回滚，独立审查难例；参照 [Waymo 安全框架](https://waymo.com/blog/2020/10/sharing-our-safety-framework) 与 [NHTSA 指引](https://www.nhtsa.gov/vehicle-manufacturers/automated-driving-systems)。

## WAYMO-09｜Disengagement rate is a weak safety proxy. How would you actually measure whether the Driver is safe enough to ship?

以碰撞/伤害严重度、近失、违规及场景暴露率评估，基线应匹配地点、时间、天气和道路类型，并报不确定性；脱离率受安全员介入阈值影响很大。证据结合道路数据、场景仿真/回放、独立审查与灰度监控，稀有严重事故需要更长暴露和保守门槛；不从平均里程数推断所有场景安全。

## WAYMO-10｜How do you build a simulator you would trust to gate a release?

模拟器须还原参与者交互、传感器噪声/遮挡、地图/交通规则和闭环响应；用真实日志对齐轨迹/传感器与事故/近失分布，保 holdout 城市/天气。评估 sim-to-real 差异，针对已知危害做参数扫描和故障注入，模拟通过只是证据之一；版本化场景和可重放 seed，事故复盘回灌。

## WAYMO-11｜Two days before a release decision, simulation shows a 15% increase in hard-braking events in one scenario cluster. Walk me through what you do.

先暂停发布决策，确认 15% 是统计显著且同版本场景/度量，回放 hard-brake 样本检查真实危险减少还是规划抖动/传感器误差。按严重度、场景和人类交通影响切片，与上一版实车/仿真/影子对比，设局部修复或回滚；两天内无法排除安全恶化则不放行，并记录审查决定。

## WAYMO-12｜Why carry lidar, radar and cameras rather than cameras alone? Where would you fuse them?

lidar 给直接 3D 距离，radar 在恶劣天气与速度测量有优势，camera 给语义与细节；各有遮挡/反射/成本限制。早融合原始点/图像信息丰富但标定敏感，中融合 BEV/对象特征更可控，晚融合利于故障隔离；IMU/定位用于时序配准。做传感器失效和天气消融，不能认为任一传感器单独保证安全。
