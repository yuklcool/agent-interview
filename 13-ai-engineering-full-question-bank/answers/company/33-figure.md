# Figure AI｜逐题答案

对应原题库公司专项第 33 组，共 12 道。

## FIGURE-01｜Behaviour cloning on teleoperation data has a well-known failure mode. What is it, and what do you do about it on a real humanoid?

行为克隆在专家轨迹分布训练，执行时小误差进入未见状态、错误累积（covariate shift）。用扰动/恢复示范、DAgger 式在策略访问状态请专家纠正、离线数据扩覆盖和安全约束，先仿真再低风险实机；测独立场景成功、恢复率、碰撞/力矩越界，不能只看一步动作 MSE。

## FIGURE-02｜A whole-body controller trained entirely in simulation has to run on real hardware. What transfers, what does not, and how do you close the gap?

仿真能学低层动力学/步态先验，但摩擦、接触、执行器迟滞、传感器噪声和物体变化难精确转移。域随机化/系统辨识、状态估计与残差控制缩小 sim-to-real，真实硬件按安全封闭环境渐进微调；评价跌倒率、能耗、扰动恢复与不同地面的稳定性。

## FIGURE-03｜Where does reinforcement learning fit on top of imitation learning for manipulation, and what makes the reward the hard part?

模仿先得到安全可行策略，RL 在仿真/受约束实机优化成功率、速度或鲁棒性，并补难以示范的恢复动作。奖励难在可测代理（抓起物体）可能导致挤压/投机、忽略人和设备安全；以真实任务终态、接触力/损伤、轨迹平滑多目标，隐藏场景和人工审查防 reward hacking。

## FIGURE-04｜A colleague wants to move the semantic layer to the cloud so you can use a much bigger model. Walk me through the latency budget.

语义规划可容忍数百毫秒到秒级，但平衡/接触控制须本地高频闭环；云端大模型通过网络增加 RTT、抖动和断网风险，不能进实时安全环。分层本地快速控制器与本地安全监控，云端可做低频任务分解/场景解释且有缓存/超时回退；量测 p99 网络和中断状态下安全。

## FIGURE-05｜Design the teleoperation data pipeline. Why is data collection the bottleneck in robotics rather than compute?

遥操作需设备状态、双手/全身动作、视觉/深度/触觉、操作者与任务终态的精确时间同步，保安全停机、隐私与设备版本。采集成本受训练有素操作者、机器故障、重置场景、罕见失败与质量复核限制，算力不能创造真实接触数据；用覆盖、成功/恢复示范比例和每小时有效轨迹衡量。

## FIGURE-06｜You have 10 hours of demonstrations for a new task and budget for 50 more. How do you decide what to collect, and what return do you expect?

先对 10 小时数据做失败聚类和状态覆盖，找最薄弱的物体/光照/姿态/恢复阶段；用少量策略 rollout 触发主动学习，优先采策略真正访问的未知状态与关键失败。50 小时按预期信息增益和安全成本分配，分批收集并画学习曲线/独立实机成功率，不承诺固定提升百分比。

## FIGURE-07｜How do you evaluate a manipulation policy when every trial costs robot time and every failure has physical consequences?

用仿真/回放先筛选，实机按难度与风险分层、小批随机化对照，设速度/力/空间硬约束和急停，必要时人工接管。指标包括任务成功、完成时间、物体损伤、碰撞/近失、恢复率及置信区间；高风险失败单独报告，停止规则预先定义，不能靠大量危险试错。

## FIGURE-08｜You ship a policy to 300 robots. It works in the lab and degrades in the field. Debug it.

锁定模型/硬件/标定/软件版本，分工厂/物体/光照/人群/网络/磨损切片比较实验室与现场轨迹；定位感知、规划、控制或执行器的首个失配点。若接触安全风险升高先暂停/回滚，收集匿名合规难例、重标/模拟并做影子与小规模实机回归，监控硬件漂移。

## FIGURE-09｜Design the safety architecture for a learned whole-body policy operating near people.

学习策略只给期望动作，独立安全控制层限制速度/力矩/接触力与禁入区，碰撞预测、冗余传感器、急停和通信丢失安全姿态。任务授权和人在场检测不能由模型自判，故障注入/形式化或硬件在环验证最坏情况；按近失事件和响应时延审计。

## FIGURE-10｜What is a vision-language-action model, and how is it different from an LLM with tools?

VLA 将视觉观测与语言任务映射到机器人动作/动作 chunk，包含时间、身体状态和控制频率；LLM+tools 多为离散符号调用，缺少接触动力学与连续闭环。VLA 仍可分层：语义模型规划，低层控制器执行并受安全约束；用实机任务成功/碰撞而非语言基准评估。

## FIGURE-11｜Helix splits into a large slow model and a small fast one. Why not run a single end-to-end network?

慢大模型负责理解场景/语义目标和较低频的动作意图，小快模型在高频率跟踪身体状态与接触，满足实时控制和算力预算；单大端到端模型可能延迟/功耗过高，单小模型语义泛化不足。接口定义目标和置信度、状态反馈与紧急覆盖，测总任务成功和延迟失配。

## FIGURE-12｜Explain action chunking. Why predict a sequence of future actions instead of the next one?

预测未来 H 步动作块能利用时间结构、减推理调用次数并产生平滑控制；执行时可滚动重规划、只用前几步或重叠块做时间集成。H 太长遇动态环境响应迟，块间衔接也可能抖动；按变化速度、推理时延和安全约束调 H，比较实机恢复与轨迹平滑。
