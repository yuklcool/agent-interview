# 09. 模型、训练、路由与推理优化

> 这一章的目标不是把你训练成算法研究员，而是让你在 Agent 面试里能正确判断：一个问题应该靠 Prompt、Harness、RAG、SFT、蒸馏还是偏好优化解决，以及模型能力和 Runtime 工程边界分别在哪里。

---

## 09-01. Tool-use 的 SFT 数据应该怎么构造

### 面试官真正考什么

不是问“把工具调用样本拿去微调”这么简单，而是看你是否理解 Tool-use 数据其实是一条完整轨迹：用户请求、工具选择、参数、Tool Result、后续决策和最终答案。

### 数据结构

一条高质量样本至少包含：

```text
System / Tool Schema
User Request
Assistant Tool Call
Tool Result
Assistant Follow-up / Second Tool Call
...
Final Answer
```

只训练 `question → tool_name` 会让模型学不到：参数修正、错误恢复、多工具串联和 Tool Result grounding。

### 样本来源

优先级通常是：

1. 线上高质量真实轨迹，人工清洗。
2. 专家构造的关键边界样本。
3. 强模型 Teacher 生成 + Validator 过滤。
4. 失败轨迹反例，明确告诉模型哪些行为不允许。

### 难点

要覆盖：

- 工具名相近时的区分
- required 参数缺失
- enum 错误
- Tool 返回 empty/error/timeout
- side-effect Tool 需要确认
- 同一问题多个合法 Tool path

如果只堆“正确工具调用成功”的 happy path，模型线上一遇异常就会失控。

### Agent 工程里怎么用

SFT 的目标应该是提高“模型做软决策”的能力，例如工具选择、参数生成、错误修复；权限、幂等、执行顺序和高风险审批仍然必须在 Runtime/业务层做硬约束。

---

## 09-02. LoRA、QLoRA、全参微调怎么选

### 核心结论

不是“显存够就全参”。选择看任务偏移程度、预算、模型规模、可维护性和是否需要频繁迭代。

### LoRA

冻结基础模型，只训练低秩增量矩阵。优点是参数少、训练快、多个业务 Adapter 易管理。适合：领域风格、Tool-use、格式遵循、中等能力偏移。

### QLoRA

基础模型量化后再做 LoRA，进一步压显存。训练成本低，但量化误差和工程复杂度略高。

### 全参微调

所有参数都更新，能力上限高，但成本、灾难性遗忘风险、版本管理和部署成本都更大。只有当任务分布和基础模型差异非常大、数据量足够、收益明确时才值得。

### 面试表达

> 如果我要让一个开源模型学会企业 Tool Calling，我会先用 LoRA/QLoRA 验证能否显著提高工具选择和参数正确率，而不会一上来做全参。只有 Adapter 到了瓶颈，而且数据和收益足够证明需要改动底层能力时，才考虑全参微调。

---

## 09-03. PPO、DPO、GRPO 的差别和应用场景

### PPO

经典 RLHF 路线，需要 Reward Model + Policy + Value/Critic，多轮 rollout 后做 clipped policy update。优点是通用、理论成熟；缺点是系统复杂、显存和训练稳定性要求高。

### DPO

直接用 preference pair `(chosen, rejected)` 优化，不显式训练 Reward Model 和在线 RL。更简单稳定，适合已有高质量偏好对数据的场景。

### GRPO

对同一 prompt 采样一组答案，基于组内相对 reward 计算优势，不依赖单独 value model。适合可自动验证 reward 的推理/代码/数学/Tool-use 任务。

### Agent 场景怎么选

如果任务是“输出风格更符合偏好”，DPO 很合适；如果有可验证 grader，例如 SQL 是否执行正确、Tool path 是否满足约束、代码测试是否通过，GRPO 类方法更自然。

但生产 Agent 很多问题不是模型训练能解决的：重复退款、权限越界、状态恢复仍然属于 Runtime/业务系统。

---

## 09-04. GRPO 的组内优势和信用分配怎么理解

给一个 prompt 采样 `K` 个回答，分别得到 reward：

```text
r1, r2, ..., rK
```

用组内均值/方差归一化得到相对 advantage，奖励高于组平均的轨迹，压低低于平均的轨迹。

直觉上不是问“这个答案绝对有多好”，而是问“在同一个问题的多个候选里，它比同组其他答案好多少”。

### Agent Tool-use 的信用分配难点

一个轨迹可能 8 步，最终成功并不意味着每一步都好。例如：

```text
错调 Tool A → 失败 → Tool B → 修正 → 成功
```

只给 final reward 会把整条轨迹一起奖励，模型可能学到冗余步骤。工程上可结合：

- step-level reward
- Tool validity
- cost penalty
- latency penalty
- safety violation penalty

让 reward 不只看最终成功。

---

## 09-05. 14B 级别模型够不够做 Agent

不能只按参数量回答。

14B 模型是否够用取决于：

```text
任务开放度
Tool 数量
Schema 复杂度
上下文长度
推理深度
语言/领域
Function Calling 训练质量
Harness 约束强度
```

如果业务是固定几十个 Tool、Schema 清晰、RAG 负责知识、Harness 有严格校验，14B 甚至更小模型可能足够。

如果任务是开放网页研究、多跳推理、代码大仓库修改，模型规划和纠错能力可能成为瓶颈。

### 正确评估方法

不要看排行榜，直接构造业务 Eval：

- Tool selection accuracy
- argument exact match / semantic validity
- end-to-end success
- average tool rounds
- hallucination
- token cost / latency

让数据决定是否够用。

---

## 09-06. MoE 为什么总参数很大，但单 Token 计算量没同比增长

MoE 把 FFN 换成多个 Expert。Router 对每个 Token 只激活 Top-k 个 Expert：

```text
Token
 ↓ Router
Expert 3 + Expert 7
```

因此模型可以有很大的总参数容量，但一个 Token 实际只经过少量 Expert，FLOPs 不按总参数线性增长。

### 工程代价

- Expert load imbalance
- all-to-all communication
- 显存仍要容纳大量参数
- batch 小时硬件利用率可能差
- Router instability

所以“参数大但计算便宜”不等于部署简单。

---

## 09-07. GQA 和 MLA 为什么能降低 KV Cache 压力

自回归推理时，每层都需要保存历史 Token 的 K/V。长上下文时 KV Cache 成为显存大头。

MHA 每个 Query Head 都有独立 K/V；GQA 让多个 Query Head 共享较少的 K/V Head，因此 KV Cache 大幅下降。

```text
MHA: Q1-K1V1, Q2-K2V2, Q3-K3V3...
GQA: Q1/Q2/Q3/Q4 → 共用 K1V1
```

MLA 的思路是把 K/V 表示压缩到低维 latent，再在需要时恢复或参与 attention，从而进一步减少缓存。

### 为什么 Agent 面试也会问

Agent 常常带长历史、RAG、Tool Schema，Context 大。理解 KV Cache 能帮助你解释为什么长上下文不只是“Token 贵”，还会影响吞吐和显存。

---

## 09-08. BPE / Tokenizer 为什么会影响中文 Agent 的成本和效果

LLM 按 Token 计费和做上下文窗口管理，而不是按字符。Tokenizer 对中文、代码、JSON、设备编码的切分方式会直接影响：

- Token 成本
- 可容纳历史长度
- 模型对实体边界的学习
- Tool 参数复制准确率

例如一个业务设备编号如果被拆成很多碎片，模型复制/生成时更容易出错。

### 评估

对自己的真实业务 corpus 做：

```text
tokens / Chinese char
tokens / JSON payload
tokens / SQL schema
tokens / code line
```

而不是只看模型标称 context window。

---

## 09-09. Reranker 蒸馏数据怎么做

目标是用昂贵 Cross-Encoder/LLM Teacher 教一个便宜 Reranker。

### 数据构造

对 Query 先从 Retriever 取 hard candidates：

```text
Query
 ↓
BM25/Vector Top100
 ↓
Teacher 打相关性分数
 ↓
正样本 / hard negative
```

最有价值的不是随机负样本，而是“检索器很容易召回、但实际上不相关”的 hard negatives。

### 训练目标

可以做 pointwise score、pairwise ranking 或 listwise ranking。上线评估看 nDCG/MRR/Top1，而不只是训练 loss。

---

## 09-10. 预训练/微调数据清洗为什么重要？常见清洗维度有哪些

模型最后学到的是数据分布。脏数据会直接变成行为问题。

常见清洗：

- dedup / near-dup
- 语言检测
- 长度异常
- 乱码/HTML 模板
- PII/secret
- unsafe content policy
- 低质量生成文本
- 格式一致性
- label/reward consistency

Tool-use 数据还要额外校验：Tool 名存在、参数符合 Schema、Tool Result 与调用匹配、Assistant 不伪造 Tool Result。

---

## 09-11. SFT、蒸馏、偏好优化/GRPO 什么时候各自更合适

可以按“你到底缺什么”来选：

```text
不会做 → SFT
会做但模型太大/太贵 → Distillation
会做但行为偏好/策略不好 → DPO/RL/GRPO
```

例如 Tool Calling：

- 连 JSON Schema 都不会遵循：先 SFT。
- 大模型效果好但成本太高：Teacher→小模型蒸馏。
- 能调对 Tool，但总是多调 3 次浪费成本：可通过 preference/RL reward 加 cost penalty 优化策略。

---

## 09-12. Attention 的基本计算和长上下文成本为什么重要

标准 Attention：

```text
Attention(Q,K,V) = softmax(QK^T / sqrt(d))V
```

训练时完整 self-attention 的时间/显存复杂度近似随序列长度平方增长。推理时有 KV Cache 后，新 Token 不必重新算所有历史 K/V，但仍要对历史 Key 做 attention，长 Context 依然增加计算和内存。

因此 Agent 的 Context Engineering 不是“为了省钱的小优化”，它直接影响模型吞吐、P99 和服务容量。

---

## 09-13. Transformer 训练为什么会有梯度不稳定？工程上怎么缓解

常见原因：深层网络累积、学习率过大、初始化、混合精度 overflow、Attention logits 极端、数据异常。

常见手段：

- AdamW + 合理 beta
- warmup + cosine decay
- gradient clipping
- RMSNorm/LayerNorm
- bf16 优先于 fp16
- loss scaling
- 初始化和 residual scaling
- 监控 grad norm / loss spike

面试时不要说“梯度爆炸就 clip”结束，要说明训练稳定性通常是优化器、精度、归一化、学习率和数据共同问题。

---

## 09-14. 多模态模型接 Agent 时，图片 Token 和成本怎么控制

图片不是“免费附件”。Vision Encoder 会把图片切成 patch/视觉 token 或压缩表示，高分辨率、多图会迅速放大上下文和延迟。

### 工程做法

```text
原图
 ↓
尺寸/质量判断
 ↓
Crop / ROI / Thumbnail
 ↓
OCR/Layout/Detector（必要时）
 ↓
只把相关视觉区域送模型
```

如果用户上传 50 页 PDF，不应该 50 页全部原图进入一个模型请求；可以先做 page retrieval，再对候选页做视觉理解。

---

## 09-15. RLHF 的 Reward Model 怎么训练，为什么 Reward 设计容易被钻空子

Reward Model 通常从 preference pair 学习：给同一 Prompt 两个回答，标注哪个更好，训练模型输出一个 scalar reward，使 chosen 分数高于 rejected。

### Reward Hacking

如果 reward 只看“答案长、包含引用、格式完整”，模型可能通过堆格式而不真正提高质量。

Agent 里更危险：如果 reward = task success，模型可能走不安全捷径完成任务。

因此 reward 要组合：

```text
Task Success
+ Groundedness
+ Tool Correctness
- Cost
- Safety Violation
- Redundant Steps
```

并保留代码层硬约束。RL 只能优化策略，不能取代安全边界。

---

## 本章总线：面试里怎么把“模型训练”与“Agent 工程”讲到一起

> 我会先区分问题是模型能力不足，还是 Runtime/Context/Tool contract 不好。Tool Schema 太差、权限缺失、状态恢复错误，这些不该靠训练修；模型确实不会做工具选择、参数生成或复杂推理时，再考虑 SFT、蒸馏和偏好优化。模型训练负责提高概率性决策质量，Harness 和业务系统负责把错误概率控制在可接受边界内。
