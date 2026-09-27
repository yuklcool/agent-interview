# 公司专项深度答案：OpenAI

> 按来源清单原题号顺序整理。题目归属是来源仓库标注，不代表公司官方确认。

## OAI-01｜Design and implement an in-memory key-value store supporting set, transactional begin, commit and abort.

**分类**：编码与数据结构。

### 回答

事务语义先明确：BEGIN 创建 overlay，SET 写当前层；GET 从当前层向父层逐级查找，删除用 tombstone 区分“本层已删除”和“本层没有记录”；COMMIT 把本层修改合并到父层（最外层才写基础 store），ABORT 丢弃当前层。若只支持单层，结构可简化，但要向面试官确认嵌套、无事务 commit、覆盖与读已写值的行为。

```text
base: key -> value
transactions: stack[dict(key -> value | TOMBSTONE)]
get(k): search overlays from newest to oldest; fall back to base
commit(): pop child; merge into parent or base
abort(): pop child
```

单线程内存实现每个操作平均 O(事务深度)，可用额外索引优化；并发事务需要隔离级别、版本检测和持久化，不能把栈模型直接宣称为 ACID 数据库。测试嵌套覆盖/删除、回滚后可见性、同键多次写和无效状态转换。


## OAI-02｜Create a database ORM, step by step.

**分类**：编码与数据结构。

### 回答

ORM 从可验证的最小链路开始：模型字段元数据→SQL 参数化生成→连接/事务→行映射→查询构造器。字段类型、NULL、默认值、主键和标识符转义要单独处理；值必须绑定参数，不能用字符串拼接防 SQL 注入。查询表达式编译为 AST 后生成 SQL，比靠链式方法任意拼接更容易保证括号和运算符优先级。

```mermaid
flowchart LR
    M[Model schema] --> A[Query AST]
    A --> S[Dialect SQL compiler]
    S --> P[Parameterized execution]
    P --> R[Row mapper and identity]
```

后续再加关联加载、迁移、乐观锁和方言；避免 N+1 查询与隐式事务。测试 SQL 快照、参数顺序、NULL 比较、回滚、并发更新及不同数据库方言。


## OAI-03｜Code a trivial web crawler using Go.

**分类**：编码与数据结构。

### 回答

Go 爬虫用 net/http Client，设置 Timeout、连接池、最大响应体与重定向策略；URL Parse/ResolveReference 处理相对链接，规范化 host/path/fragment 并限定同域。单线程先写队列与 visited，再用 goroutine worker pool 加速；visited 的 check-and-add 要原子，否则并发重复爬取。请求 Context 支持取消和整体 deadline。

```text
queue → worker fetch → HTML parser → normalize links
      → same-host/allowed check → atomic visited → queue
```

限制并发与每域速率，检查 robots/站点政策；防重定向到内网地址的 SSRF、无限链接空间与压缩炸弹。测试相对链接、循环、404、429、超时与取消。


## OAI-04｜Implement a UI from a mockup with provided CSS and API.

**分类**：编码与数据结构。

### 回答

先把 mockup 拆为布局网格、间距、字体、颜色、组件状态和响应式断点，再核对提供的 CSS token 与 API contract。优先做静态结构与语义标签，接入数据时区分 loading/empty/error/success；列表分页、按钮禁用、提交中和失败重试都要有明确状态。逐步对照截图而非一次性堆大量内联样式。

用浏览器截图在规定 viewport 做视觉回归，检查键盘导航、焦点、对比度和小屏溢出。API 数据不可信，文本转义、URL 校验；提交动作避免重复点击，用 request ID 或服务端幂等。说明哪些视觉差异是字体/浏览器渲染造成。


## OAI-05｜Refactor bad code: here are ~120 lines of working but messy code with passing tests. Improve the architecture without breaking them. What do you change first?

**分类**：编码与数据结构。

### 回答

先运行现有测试建立基线并阅读调用方，找职责混杂、重复逻辑、隐式状态和高风险边界；选最小可验证的重构单元，先补行为特征测试（尤其错误和边界），再提取纯函数/模块、隔离副作用、命名类型与接口。每一步保持外部行为不变并跑测试，避免把“重构”与功能改动混在同一提交。

优先处理会妨碍理解/测试的边界，不为了套设计模式引入抽象。对 120 行代码可用一页图说明数据流与状态，标出输入验证、核心计算、IO；最终解释改动如何降低耦合并没有改变兼容契约。


## OAI-06｜Write a Python function that displays the first n Fibonacci numbers.

**分类**：编码与数据结构。

### 回答

先澄清 n 是“前 n 个数”还是“直到数值 n”，以及 F0=0、F1=1。迭代版避免指数递归，时间 O(n)、额外空间 O(1)（若返回列表则输出空间 O(n)）；n<0 抛参数错误，n=0 返回空列表。Python 大整数不会溢出，但结果位数随 n 增长，输出与内存仍有成本。

```python
def first_fibonacci(n: int) -> list[int]:
    if n < 0:
        raise ValueError("n must be non-negative")
    result, a, b = [], 0, 1
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result
```

测试 n=0/1/2、前十项以及大 n；不要用递归版本不加缓存来显示“优雅”。


## OAI-07｜Infection-spread simulation.

**分类**：编码与数据结构。

### 回答

感染传播仿真先明确图/网格、离散还是连续时间、传播概率、潜伏/恢复、同步更新或即时更新。确定性最短传播时间可用多源 BFS：初始感染点入队，每层扩散一次，O(V+E)；带随机概率则固定随机种子，逐时间步用当前状态生成 next_state，不能一边遍历一边修改造成同一时间步连锁传播。

```mermaid
flowchart LR
    I[Initial infected set] --> E[Enumerate contacts]
    E --> P[Apply transmission rule]
    P --> N[Write next-state buffer]
    N --> T{Stop condition?}
    T -- no --> E
    T -- yes --> R[Time and affected count]
```

验证空感染源、隔离节点、周期图、概率 0/1、恢复与并发接触。若是真实流行病模型，参数需数据校准，模拟输出不能被当作预测事实。


## OAI-08｜Compute the KL divergence given different random variables.

**分类**：机器学习与深度学习基础。

### 回答

离散分布 KL(P||Q)=Σ_x P(x)log[P(x)/Q(x)]，P(x)=0 的项取 0；若 P(x)>0 而 Q(x)=0，则 KL 为无穷。连续分布是对密度的积分，需相同支撑/基准测度。KL 不对称且非距离，KL(P||Q) 与 KL(Q||P) 往往不同。

对高斯 P=N(μp,σp²)、Q=N(μq,σq²)，KL(P||Q)=log(σq/σp)+(σp²+(μp-μq)²)/(2σq²)-1/2。若“不同随机变量”不在同一空间，先定义映射到共同事件空间或联合分布，不能直接把两个样本数组代公式。数值计算用 log-sum-exp、epsilon 的引入必须说明会改变分布。


## OAI-09｜If the accuracy of a classifier is 1, what is the lower/upper bound on the loss function for a single training example?

**分类**：机器学习与深度学习基础。

### 回答

分类准确率 1 只说明所有样本的 argmax 类别正确，不固定某个样本交叉熵。若正确类概率 p_y 在多类中严格大于其他类别，单样本交叉熵 -log p_y 的下界接近 0（p_y→1），上界取决于类别数 K：在 K 类且 argmax 正确时，p_y 至少约 1/K，故交叉熵最多接近 log K；若有平局判定、标签平滑、类别权重或采用非交叉熵 loss，结论需重写。

二分类用阈值 0.5 正确时，p_y≥0.5，未加权交叉熵上界 log 2。若 accuracy 是全数据集 1，但问“某个训练样本的 loss”，要先确认损失定义和预测规则；不要说 accuracy=1 就 loss=0。


## OAI-10｜We have two models, 85% and 82% accuracy. Which do you pick?

**分类**：机器学习与深度学习基础。

### 回答

85% 与 82% 不能直接选。先看同一测试集、样本量、置信区间、类别不平衡、错误成本和评估是否有数据泄漏。若正例稀少，总准确率可能被多数类主导；应看 precision/recall、PR-AUC、校准、不同群体和严重错误，并计算业务效用。比如误放行风险远高于误拒，阈值与成本矩阵比总体 accuracy 更关键。

再比较延迟、推理成本、稳定性、可解释/审计需求和分布漂移。用配对样本做显著性分析；若 3 个百分点来自小样本噪声，不应做强结论。上线灰度 A/B 看真实业务指标与护栏。


## OAI-11｜How do you handle missing data in Pandas?

**分类**：机器学习与深度学习基础。

### 回答

先报告缺失机制与比例：MCAR、MAR、MNAR 的假设不同，不能一律填均值。按列类型、业务语义和时间分组决定删除、固定哨兵、组内统计填补、前向填充或模型插补；对“缺失本身有信息”的特征加 is_missing 指示。所有填补统计只在训练折计算，再应用到验证/测试，避免数据泄漏。

```python
train["age_missing"] = train["age"].isna().astype(int)
median = train["age"].median()
train["age"] = train["age"].fillna(median)
valid["age_missing"] = valid["age"].isna().astype(int)
valid["age"] = valid["age"].fillna(median)
```

时间序列 forward fill 只能用过去信息，不能穿越用户/设备边界；评价填补前后分群性能与校准。对 Pandas 的 NA/None/NaN 与 dtype 转换要显式测试。


## OAI-12｜Explain self-attention. What is its computational complexity, and what are your options when contexts get long?

**分类**：LLM 内部原理与架构。

### 回答

Self-attention 的 QKᵀ 与 attention×V 时间约 O(S²d)，若物化概率矩阵空间约 O(S²)；FlashAttention 降低 IO/中间存储但不改变精确全注意力的二次算术量。长上下文选项包括分块/稀疏/滑动窗口以减少交互，线性/状态空间结构改变记忆机制，RAG 把外部事实召回为较短证据；解码 KV Cache 避免重算历史投影，但缓存随 S 增长。

选方案先明确任务要全局逐 token 关系还是只需特定证据、训练与推理长度、可接受质量损失、硬件/延迟和数据更新频率。测长距离定位、多跳、短上下文退化，而不是只看能否接受 1M token 输入。


## OAI-13｜What is the relationship between cross-entropy, KL divergence and perplexity, and why is cross-entropy the training loss for language models?

**分类**：LLM 内部原理与架构。

### 回答

交叉熵 H(P,Q)=E_{x~P}[-log Q(x)]；KL(P||Q)=H(P,Q)-H(P)，目标真实分布 P 固定时，最小化交叉熵等价最小化 KL。语言模型对每个上下文的真实 next-token 样本做负 log likelihood，整个数据集的平均 token loss 是经验交叉熵；perplexity=exp(平均自然对数交叉熵)，若用 log2 则是 2 的对应幂。报告 perplexity 时要注明 tokenizer/数据集，不同词表的数值不能盲比。

训练时 teacher forcing 用真实前缀，推理用自身生成前缀，存在 exposure bias；降低交叉熵不保证事实性、安全或工具成功。实现上对目标 token 取 log_softmax，mask padding，按有效 token 数归一化；用融合算子避免先 softmax 再 log 的数值问题。


## OAI-14｜What is the effect of adjusting an LLM's context window size?

**分类**：LLM 内部原理与架构。

### 回答

上下文窗口变大增加可放入的 prompt 与历史，但不代表模型能可靠利用所有位置。Prefill 的 attention 计算、KV 缓存与 TTFT 增长；长文可能有 lost-in-the-middle、证据冲突和更高成本。位置编码扩展、长上下文训练/微调、chunked prefill 与 KV 管理分别解决表示、能力、调度和显存问题，不能互相替代。

决策按任务检验：全文必须逐句比较时可能需要长窗口；经常变化的企业文档适合 RAG+引用；复杂问题可先检索再在有限长窗口里综合。衡量证据位置敏感性、引用支持率、短任务退化、p99 与单位任务成本。


## OAI-15｜You are building a production agent that calls tools (function calling). What makes the loop reliable enough to ship?

**分类**：Agent 与工具调用。

### 回答

可靠性来自 Host/Runtime 的硬约束而非模型“会调用函数”：工具注册与版本、参数 schema、身份/权限、风险等级、超时、错误分类、有限重试、幂等与 UNKNOWN 状态核对、结构化 observation、审计和终止预算。读操作可按策略重试；发信/下单等写操作在丢响应时先查 operation ID，不能直接再执行。

```mermaid
flowchart TD
    M[Model proposes tool] --> P[Policy and schema]
    P --> E[Execute with deadline and key]
    E --> R{Observed state}
    R -- success --> S[Persist receipt]
    R -- timeout --> U[Reconcile UNKNOWN]
    R -- permanent error --> F[Typed failure]
    U --> S
    U --> H[Human if unresolved]
```

以故障注入 eval 验证 429、5xx、超时、重复调用、权限撤销和取消，且每个用户只看自身允许的工具/数据。


## OAI-16｜How would you build an LLM-powered enterprise search system?

**分类**：AI 系统设计。

### 回答

企业搜索先明确语料类型、权限和更新率。连接器增量拉取原件与 ACL，解析/OCR/切块并保留 doc ID、版本、来源 span，写入 BM25、向量索引与元数据。查询时解析用户身份和组，检索前过滤租户/ACL，融合候选后再授权复核、精排和引用生成；权限撤销要短时传播或查询时 fail-closed。不能在检索出未授权文本后才让模型“不要说”。

```mermaid
flowchart LR
    S[Sources and ACL changes] --> I[Parse chunk version]
    I --> X[Keyword and vector indexes]
    U[User identity and query] --> P[Policy prefilter]
    P --> R[Hybrid retrieval]
    X --> R
    R --> A[ACL recheck]
    A --> C[Context and citations]
```

指标分检索 Recall@k、答案支持率、越权测试、索引滞后、p99 与成本。失败时返回可解释的无证据或权限不足，不能编造答案。


## OAI-17｜Design the serving stack for a ChatGPT-scale consumer assistant: hundreds of millions of weekly users, streaming chat, multiple model tiers.

**分类**：AI 系统设计。

### 回答

先算峰值而非周活跃：并发流、平均输入/输出 token、长尾长度、地区和模型 tier 比例。区域入口做鉴权、配额、会话路由；控制面维护模型路由、灰度、预算；推理池分别管 prefill、decode、continuous batching、KV 和弹性扩容；会话事件与工具副作用在持久层记录，GPU 实例不当唯一状态源。

```mermaid
flowchart TD
    U[Regional clients] --> G[Edge auth and quotas]
    G --> S[(Session event store)]
    G --> R[Model tier router]
    R --> P[Prefill GPU pools]
    P --> D[Decode pools with KV]
    D --> V[Streaming response]
    D --> M[Usage trace and billing]
```

容量按目标 SLO 下每 GPU 的可持续 tokens/s 而非理论 FLOPs 算，加冗余和长短混合压测。故障覆盖部分流输出、客户端重试、GPU 失联和跨区；读写工具另有权限与幂等。


## OAI-18｜Design and build a webhook delivery system that reliably delivers events to customer-registered URLs.

**分类**：AI 系统设计。

### 回答

Webhook 投递是至少一次语义：事件入事务性 outbox，dispatcher 读取并为每个订阅者生成 delivery ID、目标 URL、签名、attempt 与 next_retry；worker 限速投递，2xx 才确认，429/5xx/网络失败按 Retry-After 与指数退避重试，永久 4xx 或过期进 dead letter。用户端通过 event ID 去重；服务端不承诺跨所有目标的全局严格顺序，若需要按对象顺序则分区/序列号。

```mermaid
flowchart LR
    E[Business transaction] --> O[(Outbox)]
    O --> Q[Delivery queue]
    Q --> W[Worker with signature and timeout]
    W --> C[Customer URL]
    C --> A[ACK or retry schedule]
    A --> D[Delivery log and dead letter]
```

防 SSRF、DNS rebinding、内网目标和凭据泄露；签名含时间戳并支持密钥轮换。指标是延迟分布、最终成功率、重复投递、死信与单客户积压。


## OAI-19｜Design a system to schedule jobs in a distributed environment.

**分类**：AI 系统设计。

### 回答

分布式调度分 schedule owner 与执行 worker。任务表保存 id、run_at、payload、状态、租约、attempt、幂等键；调度器按时间索引扫描到期任务并原子 claim，发布到队列，worker 带 fencing token 执行并回写。调度器多副本用分区所有权或数据库原子 claim，避免重复派发；但崩溃仍可能导致至少一次执行，任务逻辑必须幂等。

周期任务要定义 fixed-rate/fixed-delay、时区/DST、错过执行补偿；任务取消和重试需状态机。监控 scheduled-to-start 延迟、执行成功率、租约超时、重复执行和死信；故障演练在 claim 后、执行成功回执前、数据库故障各点杀进程。


## OAI-20｜Design an in-memory database. / Design Slack.

**分类**：AI 系统设计。

### 回答

题目同时提内存数据库/Slack，应先问面试官选择哪个并确定验收范围。内存数据库设计参见键值 store：WAL、MVCC/事务、索引、TTL、快照恢复和并发读写；先做单节点最小契约，再谈复制与一致性。Slack 设计则拆消息写入、频道成员授权、持久事件、扇出/在线推送、离线通知、搜索与多设备游标；消息顺序通常按频道有序而非全局有序。

```mermaid
flowchart LR
    C[Client] --> A[Auth and channel policy]
    A --> M[Message write with sequence]
    M --> L[(Durable log)]
    L --> F[Online fan-out]
    L --> S[Search index and offline sync]
```

两者不能在面试中含糊混答；先锁定非功能要求如 QPS、持久性、跨区、权限，再做容量和失败路径。


## OAI-21｜A customer says “the model got worse” after you upgraded model versions in their deployment. How do you verify and respond?

**分类**：评测与可观测性。

### 回答

先建立升级前后同一批真实请求的配对比较，保存模型、prompt、工具 schema、检索索引、解码参数和业务数据版本；确认升级是否只改了模型。对投诉样本分桶：事实性、遵循格式、工具调用、拒答、长上下文、语言和延迟。固定 gold/专家判据与可回放环境复测，不用一次主观对话判断。

给客户 24 小时内说明已复现范围、缓解方案（路由回旧版/灰度回退/特定任务固定模型）与后续实验；对重大安全/业务错误立即回滚。回归门禁按任务切片和严重度设置，允许用户反馈成为新测试集，但避免仅针对几例提示词过拟合。


## OAI-22｜An enterprise customer reports that responses from your deployed system have gotten slow. Walk me through the diagnosis.

**分类**：评测与可观测性。

### 回答

把慢请求分解为入口排队、鉴权、RAG 连接器/检索/精排、模型排队、prefill、decode、工具网络、出口。收集同时间段前后 trace，按 prompt/output 长度、QPS、租户、区域、模型/硬件、缓存命中、429 与重试切片；总平均不够，要看 TTFT、ITL/TPOT 和 p95/p99。模型没变也可能是长 prompt 比例增加、prefix cache 失效、KV 抢占或外部工具变慢。

```text
total latency = queue + retrieval + prefill + decode + tools + network
```

用固定流量回放隔离配置/负载，GPU 监控看利用率、HBM、KV blocks、preemption 和 CPU 调度。先回滚导致回归的版本或限流降级，并说明恢复指标与根因验证。


## OAI-23｜How do you approach GenAI safety in consumer products?

**分类**：安全、Security 与负责任 AI。

### 回答

消费产品要按风险类别设计分层控制：直接危险内容、隐私泄露、虚假高风险建议、未成年人场景、工具越权、滥用成本。模型层训练/拒答、入口风险分类、出口核查、工具权限/人审和用户申诉各有作用；输出过滤无法撤销已执行动作。策略版本与例外应可审计，避免系统提示词成为唯一安全边界。

指标除拒答率，还要看严重错误漏报、误杀、有用性、群体差异和真实投诉。灰度发布对高严重度用硬门禁；事故发生可按版本回滚、限制工具范围并回放 trace。


## OAI-24｜How would you design safeguards for an AI system that can take actions on behalf of a user?

**分类**：安全、Security 与负责任 AI。

### 回答

Agent 代表用户行动时，用用户身份委托的最小权限令牌，按资源/动作/时限授权；模型只提议，Runtime 校验参数、目的地、业务前置条件和风险。高风险写入提供精确预览与人审，批准绑定动作哈希和有效期；执行记录幂等键、operation ID 与业务回执。超时进入 UNKNOWN 后查询状态，不能盲重试。

```mermaid
flowchart TD
    M[Model proposal] --> P[User scope and policy]
    P --> V[Exact action preview]
    V --> H{Approval if risky}
    H -- yes --> E[Idempotent execution]
    H -- no --> X[Cancel]
    E --> R[Business receipt and audit]
```

撤权、用户取消、参数变更使先前批准失效。用对抗性网页/邮件和跨租户数据做端到端测试，确保 prompt injection 即使成功影响模型，也无法越过工具门禁。


## OAI-25｜An enterprise customer says: “We want AI to automate our claims processing.” You're the engineer in the room. What do the first two weeks look like?

**分类**：应用与 Forward-Deployed 场景。

### 回答

前两周先做业务发现而非直接训练模型。第 1～3 天梳理理赔类型、现有 SOP、合法数据来源、人工权限、错误成本和量化基线；第 4～7 天选一个低风险子流程（材料分类/字段抽取/证据摘要），建立带人工审核的样本集和严重错误清单；第 2 周做最小试点，串起文档解析、规则核验、异常转人工与审计，不直接自动拒赔/付款。

验收看字段级正确率、漏件、人工复核时间、严重错误和用户申诉；预算/合规由客户确定。每个建议保留原文页码与版本，敏感数据按租户隔离。试点结果用对照组验证工时节省，明确不自动化的边界和扩展条件。


## OAI-26｜Do you have experience working with APIs? Are you used to working with C-suite executives?

**分类**：应用与 Forward-Deployed 场景。

### 回答框架

API 经历用真实接口说明：鉴权、幂等、分页、速率限制、错误分类、版本兼容、观察与回滚，描述自己负责的接口契约和上线问题。C-suite 交流不需装作所有技术细节都适合高管；先将目标翻译成业务指标、风险、时间和决策选项，再备技术附录给实施团队。若没有直接向 C-suite 汇报经历，明确说明与谁沟通过、自己做的资料/演示和实际结果。

可用 AgentDock 或照明运维项目的真实经验举例，但不要编造职级和成交结果。回答结构是对象→决策问题→你给的选项与证据→对方选择→交付结果。


## OAI-27｜What is your favourite product and why?

**分类**：行为面试与文化。

### 回答框架

选你长期使用、能具体剖析的产品，而非追热门。结构：用户任务与核心体验→一个设计细节如何降低摩擦→产品指标的可验证假设→失败或不满意之处→你会做的实验。若选开发工具，可从任务恢复、错误透明、权限确认与反馈闭环切入；若选照明运维平台，可谈对话式任务计划如何体现业务状态。

避免把个人偏好直接当市场事实，区分“我观察到”与“我推测”；在批评时给可衡量的改进方案。


## OAI-28｜Tell me about a time you made a mistake.

**分类**：行为面试与文化。

### 回答框架

用真实错误讲背景、当时掌握的证据、自己的判断、影响、止损、根因、机制改进与后续结果。选择有技术细节和责任的例子，例如错误的事件去重条件、工具超时被当失败、缓存权限版本遗漏等；只用你实际发生的案例，不照搬这些假设。数字和时间可用准确范围，不虚构。

面试官通常追问“你为何当时没看出来”“谁发现”“如何避免复发”。回答要能指出新增的测试、指标、评审或回滚门槛，并说明它是否在后来起作用。


## OAI-29｜Tell me about a time you had a conflict with someone. How did you resolve it and what did you learn?

**分类**：行为面试与文化。

### 回答框架

具体描述冲突的共同目标与差异假设，而不是说对方“不懂技术”。先听对方限制，提出可验证方案和决策标准，例如 UI 全面重构的交付周期与增量迭代风险；用小实验、用户数据或原型把争议转成证据。若最终不是你的方案，说明如何执行团队决定并监测风险。

结果包括关系修复和产品/工程影响；反思自己的沟通方式。避免把技术分歧包装成个人胜利或泄露同事隐私。


## OAI-30｜Tell me about a time you had conflicting priorities with stakeholders and how you secured alignment.

**分类**：行为面试与文化。

### 回答框架

列出冲突优先级的利益相关方、不可移动的约束与可调整范围。建立统一的目标/成本/风险表，例如用户权限修复、MCP 入口和 UI 重构分别对安全、可用性、交付日期的影响；拿方案 A/B 与验收指标让决策者取舍。把决定写成可执行里程碑、负责人和依赖，后续用进度/风险更新避免再次分歧。

强调你个人推动的沟通与技术验证，而不只是“大家开会达成一致”。若牺牲了某些需求，说明如何保护核心目标与何时复评。


## OAI-31｜What is the project you are most proud of?

**分类**：行为面试与文化。

### 回答框架

选择你参与最深、能解释技术决策和业务结果的项目。按目标→制约→架构/实现→最难故障→验收数字→个人贡献讲述。你可以选照明智能体的事件闭环/一路一策研究，或 AgentDock 多租户运行平台，但只陈述已经真实实现和测过的部分；设计稿、计划和上线结果必须区分。

准备架构图与一次请求链路、权限/失败路径、两个重要 trade-off 和可证伪指标。面试官追问“你具体写了什么”时给模块/接口和测试证据，不只讲产品愿景。
