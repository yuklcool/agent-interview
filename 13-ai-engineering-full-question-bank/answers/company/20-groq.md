# Groq｜逐题答案

对应原题库公司专项第 20 组，共 12 道。硬件数值题以题目给定假设计算。

## GROQ-01｜Our compiler statically schedules every instruction and every chip-to-chip transfer. What does that compiler need to know that an NVCC-style compiler does not, and what breaks when it's wrong?

静态排程需已知算子形状、执行时间、片上内存布局、路由拓扑、每条链路带宽/延迟与同步边界，把计算和芯片间传输排到确定周期。动态分支/变长序列需界限、变体或运行时调度；估计偏差会造成 buffer 溢出、数据竞争或气泡。以模拟器+硬件 trace 比对并做最坏情况容量验证。

## GROQ-02｜Design the IR and pass pipeline for a compiler targeting a spatial dataflow accelerator. Where does the memory-residency decision live, and why?

IR 至少表示张量形状/布局、数据依赖、设备拓扑、时间/通信约束和量化语义；pass 由算子降级、融合/切分、放置、内存驻留/溢出、路由、静态排程到代码生成/校验。驻留决策须在跨算子融合和布局/放置后、最终排程前联合求解，因为它决定数据是否需跨芯片搬运与存活区间。

## GROQ-03｜Write the host-side runtime that feeds a deterministic accelerator across many chips. What is genuinely hard about it?

host 按编译期 schedule 提前准备输入、KV/中间状态及 chip 队列，给请求分配确定的资源槽，处理超时/取消与多芯片同步、错误回传和恢复。难点是变长请求和网络抖动下仍不饿死流水线、无 HBM 时内存压力和版本匹配；测 p99、队列积压、丢包和故障域。

## GROQ-04｜A model passes bit-exact against the functional simulator on one chip but produces wrong output at rack scale. How do you find it?

先定位首个错误层/芯片与对应输入，锁定模型、编译产物、拓扑和时钟/温度；逐级从单芯片→单机→跨机、相同 seed 重放，校验传输包 checksum、路由/同步、buffer 生命周期和数值格式。bit-exact 功能模拟只覆盖算术，不保证时序/链路/硬件故障正确；加硬件 trace 与端到端一致性断言。

## GROQ-05｜An LPU has no HBM at all, just on-die SRAM. Redo the decode roofline argument for that machine and tell me what changes.

GPU decode 常受权重/KV 从 HBM 反复读取的带宽限制；全 SRAM 设计把权重分布在片上，多芯片流水计算，消除 HBM 访问但受 SRAM 总容量、互联、路由和芯片数约束。roofline 要用片上带宽与跨芯片通信/计算并行度，且 KV/注意力若在其他设备则另计传输。比较真实 batch、序列长度与端到端 TTFT，而非只报芯片峰值。

## GROQ-06｜A 70B dense model at 8-bit weights, chips with ~230 MB of SRAM each. Walk me through the deployment and the unit economics.

70B 8bit 权重理论 70GB，230MB/芯片理论至少约 305 芯片（十进制），实际还要 scale、激活、固件和冗余，故更多；按层/矩阵切分与静态跨芯片流水。成本模型包括每台机总拥有成本、电力、利用率、故障副本、prefill/KV 外部资源，以有效输出 token/s 与 p99 定价；单纯权重/容量下界不是采购估算。

## GROQ-07｜On a GPU you batch to amortise weight reads. What is the batching calculus on an SRAM-only machine, and how should that change how we price?

GPU 批处理复用每次 HBM 权重读取，增大吞吐但增加排队/首 token；片上权重常驻后边际批处理收益更多受算力/流水填充和状态容量约束，不能沿用同样的极大 batch 策略。按 batch 测 token/s、p99、空闲成本和每 token 能耗，价格应对应吞吐/延迟 SLA 和专用占用，而非只按理论峰值。

## GROQ-08｜Determinism is the headline claim. What does it actually buy at p99, and why does it matter especially for agentic workloads?

确定性排程减少运行时调度抖动，使同形状负载的计算时间更可预测，p99 容易按可证明容量设界；网络、排队、外部检索仍会带来尾延迟。代理任务串联多次模型调用，总延迟尾部会放大，稳定单步延迟改善可用预算，但还需端到端观测和故障隔离。

## GROQ-09｜How would you serve a large mixture-of-experts model on a statically scheduled fabric when expert selection is data-dependent?

路由 token 到专家是数据依赖，不能假装固定执行路径；可预留每专家容量、批次收集后按模板排程，或为常见路由模式编译变体，溢出/长尾走回退。代价是空槽浪费、复制权重/通信和热专家倾斜；测负载分布、p99、模型质量与专家丢 token 率。

## GROQ-10｜We pair LPX decode accelerators with NVIDIA GPUs doing prefill and attention. Design the serving path across those two machines.

入口先在 GPU 做长输入 prefill/attention，产出首 token 与 KV 状态；把适配的 decode 状态/必要激活传 LPX，decode token 后注意力仍需与 GPU 协作。定义序列所有权、状态传输格式、同步、取消/故障回退，跨机链路延迟可能吞掉加速收益；测端到端首 token/每 token/p99。

## GROQ-11｜A prospective customer runs their workload on H100s. Talk me through when you would tell them not to move.

若客户大量长 prompt 的 prefill/注意力占主导、低并发 batch 已高效、模型/算子不支持、互联/部署成本超收益，建议保持 H100。用客户的输入输出长度、峰值并发、质量和 SLA，在相同条件下对比全链路成本、p95/p99、故障/迁移风险；让数据决定。

## GROQ-12｜Tell me about a performance optimisation you shipped. Give me the numbers, and tell me why I should believe them.

真实案例给基线与目标、profiling 证据、单一变量改动、同硬件/同负载/同质量的前后 p50/p99/吞吐/成本，注明热身、样本量与置信区间；附可重复脚本/监控截图来源。若没有数字就如实说可验证范围，不编优化倍数。
