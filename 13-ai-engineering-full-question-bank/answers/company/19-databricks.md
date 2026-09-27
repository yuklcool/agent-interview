# Databricks｜逐题答案

对应原题库公司专项第 19 组，共 9 道。

## DBX-01｜Implement a thread-safe batching logger: many producer threads call log(msg); a background thread flushes batches of up to 100 messages every second or when full.

用 mutex+condition variable 保护队列，log 追加并在满 100 时唤醒；后台线程按 monotonic deadline 一秒或满批触发，在锁内交换队列、锁外写入，避免阻塞生产者。关闭时 flush 剩余并 join；失败保留/重试与背压、最大队列内存、消息顺序要定。测试竞态、恰在定时器边界的日志和重复刷盘。

## DBX-02｜You have a stream of billions of events and need the top-K most frequent keys with bounded memory. Exact is impossible: what do you do?

精确全局 top-k 对无限 ID 固定内存不可能。按窗口使用 Space-Saving/Count-Min Sketch（频率误差 ~N/m），局部 sketch 合并或候选二次计数；热点 key、迟到事件与查询一致性单独处理。向调用方暴露估计误差与统计窗口，不把近似数伪装精确。

## DBX-03｜Given allowed IP ranges as CIDR blocks plus explicit deny ranges, implement is_allowed(ip) efficiently for millions of checks per second.

IPv4/IPv6 地址规范成定长整数，CIDR 前缀构建 Patricia trie/二叉前缀树，查询收集最长匹配允许与拒绝规则；先明确冲突优先级，若显式 deny 一律覆盖 allow 则单独 deny trie 先查。构建 O(前缀总位数)，查询 O(32/128)，读多写少用不可变版本原子替换，测重叠、边界和 IPv4-mapped IPv6。

## DBX-04｜A Spark job joining a 2 TB fact table to a 50 GB dimension table has one straggler task running 100x longer than the rest. Diagnose and fix it.

先看 Spark UI 该 task 输入字节、shuffle read、spill、GC 与 key 分布；常见 skew 某个 join key 极热，亦可能数据倾斜/坏 executor。若维表过滤后足够小可广播，50GB 原始大小不宜盲目广播；热 key 单独处理或 salting 后合并，AQE skew join 与分区数/统计更新。用结果行数/校验和与成本对照，防 salting 重复。

## DBX-05｜A Structured Streaming job reads Kafka and writes to a Delta table. The cluster is killed mid-batch and restarts. Does the customer get duplicate rows? Explain at the level of the checkpoint and the transaction log.

Structured Streaming 到 Delta 的正确实现依赖 checkpoint 保存 batch/offset 和 Delta 事务的幂等 batch 身份：mid-batch 失败后同一 batch 重试，已提交事务不应重复追加；自定义 foreachBatch 外部副作用不自动 exactly-once。检查 checkpoint 路径唯一/持久、事务日志和 sink 语义，演练提交前后宕机、源重放和 checkpoint 删除。

## DBX-06｜When would you fine-tune instead of using RAG or prompt engineering, and if you do, LoRA or full fine-tuning?

事实频繁更新/需要来源与 ACL 用 RAG，行为/格式/专门技能缺失且有高质量样例才 fine-tune；prompt 工程是低成本基线。LoRA 以低秩增量省显存/便于多租户，若领域差距大且资源足可全参微调。固定测试集比较质量、成本、隐私和更新周期，不把内部知识硬塞权重。

## DBX-07｜Take a working GenAI agent prototype to production for an enterprise. What's your checklist between demo and launch?

从 demo 到生产要定义契约与权限、数据/工具版本、幂等/重试和人为审批，建立带真实任务的黄金集与注入/故障回归。加预算、限流、观测轨迹与脱敏、灰度/回滚、用户纠错和事故响应；测端到端完成率、成本与 p95，而非只看单轮漂亮回答。

## DBX-08｜A customer insists on fine-tuning an open model on their support tickets because “we want our own model.” You think RAG solves it. What do you do?

先询问“自己的模型”背后的数据驻留、品牌、性能或控制需求，做少量真实支持工单的盲测：prompt、RAG、LoRA 各方案比较事实正确、引用、更新时效、成本和隐私。若 RAG 优势明显给可复现实验和可逆试点，尊重客户最终约束；必要时 RAG+微调结合。

## DBX-09｜An agent you shipped four months ago runs on a base model being deprecated in 60 days. How do you swap the model without regressing quality, and what had to be in place beforehand?

事先必须有模型/提示/工具/数据版本化、固定黄金集、真实轨迹采样和灰度/回滚。先在同输入上新旧模型并行影子评测工具 schema、引用、安全与长尾，再分阶段迁移，基于任务完成和成本/延迟门槛回滚；弃用前留容量和迁移窗口，避免靠主观手测。
