# Amazon（AWS）｜逐题答案

对应原题库公司专项第 14 组，共 23 道。

## AWS-01｜Find the top-K most frequent items in a high-volume event stream with bounded memory.

精确 top-k 无界独立 key 需要无界计数；近似用 Space-Saving 的 m 个计数器，更新最小槽并记录误差，候选二次精确统计。按事件时间窗口与分片聚合定义语义，局部 top-k 直接合并会遗漏全局热门；监控误差、热点和迟到事件。

## AWS-02｜Divide two integers without using multiplication, division or modulo. Find the number of connected components in a graph. Check balanced parentheses.

整数除法用指数倍增减法：反复找不超过余数的最大 `divisor<<j`，相减并累计 `1<<j`，处理零除和最小负数溢出，O(log² n) 朴素/位扫描 O(log n)。连通分量用 DFS/BFS 或并查集 O(V+E)；括号用栈检查类型及顺序 O(n)，分别测边界。

## AWS-03｜What is the closed-form solution of linear regression, and when do you use gradient descent instead?

OLS 满秩时 `β=(XᵀX)^{-1}Xᵀy`，实际用 QR/SVD 求解以避数值不稳；样本/特征很大、稀疏/流式、非线性或正则目标适合迭代优化。比较条件数、内存 O(d²)、收敛、标准化与数据规模。

## AWS-04｜What are the differences between L1 and L2 regularization in logistic regression?

L1 在逻辑回归目标加 `λ||w||₁`，非光滑且可得到稀疏系数，适合特征选择但强相关特征不稳定；L2 加 `λ||w||₂²` 平滑收缩、一般保留全部特征，相关特征更稳定。偏置项通常不正则，标准化后用验证集选 λ。

## AWS-05｜Write the loss function for logistic regression and prove it has a global minimum.

二分类交叉熵 `L=Σ[log(1+exp(z_i))-y_i z_i]+λR(w)`，`z_i=x_iᵀw`；log-sum-exp 为凸函数、仿射复合和求和保持凸，因此任何局部极小是全局最小。无正则且完全线性可分时有限最小值可能不存在（权重趋于无穷）；加 L2 并具适当条件可保证唯一解。

## AWS-06｜How is KL divergence loss different from cross-entropy loss? And from contrastive loss?

`H(p,q)=H(p)+D_KL(p||q)`，固定标签分布 p 时优化 q 的交叉熵与前向 KL 仅差常数；KL 需要两个分布且非对称，支持集为零须处理。对比损失针对正负样本/相似度拉近拉远表示（如 InfoNCE），与 token 分类目标不同。

## AWS-07｜How do bagging and boosting differ? What is the computational difference between XGBoost and Random Forest?

Bagging 对重采样数据并行训练强学习器、平均降方差，随机森林再随机选特征；Boosting 顺序纠正前轮误差，通常偏差降低但对噪声敏感。XGBoost 是梯度提升树，树依赖前轮残差、正则/直方图与剪枝；随机森林各树可高度并行，训练和调参成本不同。

## AWS-08｜Explain the bias-variance trade-off, cross-validation, and the curse of dimensionality.

偏差/方差指系统误差与采样波动；容量大可能训练好、验证差。交叉验证按时间/实体分组防泄漏，验证用于选择，独立测试只看一次。高维稀疏空间距离区分度下降、样本覆盖指数困难，靠特征选择、正则与表示学习缓解，不能仅盲目增维。

## AWS-09｜How do GRU cells work, and how do they address the vanishing gradient problem? How does a BiLSTM work?

GRU 用更新门混合旧状态与候选状态、重置门控制历史贡献，使梯度有较短的信息通道，但不能保证任意长依赖无衰减。BiLSTM 正向/反向各读序列再拼接表示，适合完整输入的标注/理解；在线因果生成不能读未来。

## AWS-10｜What is Attention in machine learning models? What happens in a neural network if you remove all the hidden layers?

Attention 用 query-key 相似度权重汇总 value，允许按上下文动态选择信息；自注意力时间复杂度在全序列通常 O(T²d)。去掉所有隐藏层只剩输入到输出的仿射变换（加 softmax 仍是线性决策边界），无法表示复杂非线性 XOR，除非输入已映射为合适特征。

## AWS-11｜Discuss precision, recall and F1: when would you prioritise one over the others?

`precision=TP/(TP+FP)`，`recall=TP/(TP+FN)`，`F1=2PR/(P+R)`。漏报高代价如罕见风险先重 recall，误报高代价如自动封禁重 precision；F1 等权且忽略 TN/校准，需结合业务成本、PR 曲线和类别基率挑阈值。

## AWS-12｜How do you handle data imbalance, collinearity, feature selection and regularization?

不平衡先看 PR/按成本阈值、分层采样或 class weight，验证保持自然基率并做校准；共线性用相关/条件数诊断，正则或删冗余特征。特征选择必须在训练折内完成防泄漏，L1/L2 强度经分组或时间验证选；报告稳定性和公平切片。

## AWS-13｜Explain how you would design and evaluate an A/B test. What is a p-value and how do you interpret it here?

预注册主指标、护栏、最小可检测效应及随机化单位，按用户稳定分桶避免干扰，做样本量/功效计算；AA 检查、实验期间盯 SRM 和异常，结束按预设检验/置信区间解释。p 值是在零假设为真时观察到至少如此极端数据的概率，并非“假设为真的概率”；多重比较和提前偷看需校正。

## AWS-14｜What is Maximum Likelihood Estimation and how does it differ from Bayesian inference?

MLE 选使观测数据似然最大的参数，常等价最小负对数似然；Bayesian 在先验与似然下得到后验 `p(θ|D)∝p(D|θ)p(θ)`，可表达参数不确定性。MAP 是后验众数，正则可对应先验，但后验预测需要积分；比较数据量、先验影响及计算代价。

## AWS-15｜Why did transformers displace RNNs for language modelling, and what exactly does the KV cache buy you at inference time?

Transformer 训练时能并行处理 token 且注意力连接长程信息，RNN 的时序依赖限制并行和梯度传播；代价是全注意力长序列计算。推理 KV cache 保存历史 K/V，增量解码不重复投影前缀，每新 token 仍需读历史缓存、显存随序列与并发增长。

## AWS-16｜A customer's Bedrock-hosted workload costs too much. Cut inference cost dramatically without unacceptable quality loss.

取请求长度/并发/模型/质量分布，拆 token、排队、检索与冗余调用成本；先缓存、裁剪无关上下文、批处理、限制输出、选择小模型/量化及按复杂度路由。每项以固定离线集和线上 A/B 测准确、拒答、安全与 p95，不牺牲难例；设置预算、监控每有效完成任务成本。

## AWS-17｜Design an agent that operates a web browser to complete multi-step tasks. How do you make it reliable enough to ship?

浏览器代理按观察 DOM/截图→计划→受限点击/输入→验证状态循环，工具层严格域名、权限和敏感操作确认。点击用稳定定位器与版本快照，失败重观测而非盲重试，幂等键防重复下单；每步日志/超时/预算，评估真实任务成功、错误写入、恢复率与注入。

## AWS-18｜Design a multi-tenant inference platform that serves many foundation models to thousands of customers (Bedrock-shaped).

控制面管理租户认证、配额、模型版本和计费；数据面按模型/地区路由到隔离的推理池，按 token/KV 预算 admission、连续批处理、自动扩缩容。每租户访问控制、加密、日志与缓存隔离，压测 noisy neighbor、故障域、回滚；监控 TTFT、吞吐、成功率、成本及模型安全。

## AWS-19｜How would you design a recommendation system to suggest books to users? How would you model a warehouse inventory problem?

图书推荐多路召回（协同、内容、热门/新书）→排序（阅读/购买长期价值）→多样性/库存过滤，冷启动用作者/主题；评估 NDCG 与购买/留存。仓库库存问题明确需求预测、补货提前期、缺货与持有成本，通过安全库存/服务水平优化，再用仿真测季节、滞后和极端事件，不能把两题混成单一模型。

## AWS-20｜How would you decide an LLM-powered assistant is ready to launch to millions of customers?

建立离线固定能力/安全/群体测试、真人盲评和工具故障/注入演练，定义严重错误率、成功率、p95 与成本门槛；污染检测、可复现版本。先小流量灰度，监控申诉、漂移和护栏，准备回滚与人工接管；上线决策基于最差关键切片，不只看平均分。

## AWS-21｜Tell me about a time you disagreed with your team's technical direction. What did you do? (Have Backbone; Disagree and Commit)

按真实 STAR：阐明业务目标、你反对的技术假设及证据、如何公开讨论与小实验、决策后如何执行和监控。即使意见未被采纳也说明 commitment 与复盘，避免虚构冲突或指标。

## AWS-22｜Tell me about your most significant failure. What happened, and what did you change afterward?

选真实失败：你负责的决定、受影响范围、早期信号、及时告知/回滚与客户补救，随后修改测试、监控或流程，给可核实结果。不要包装成“完美主义”或推给同事。

## AWS-23｜Tell me about a time you saw an opportunity to do something bigger than the initial scope. (Think Big)

选真实案例：发现原目标之外可量化的用户问题，提出扩大方案与成本/风险、获取利益相关者支持，先试点验证，再量化影响及学习。明确哪些超出原范围、你本人做了什么，不编结果。
