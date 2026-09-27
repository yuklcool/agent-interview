# Together AI｜逐题答案

对应原题库公司专项第 21 组，共 7 道。

## TOGETHER-01｜Write the server-side handler for streaming token generation. Handle client disconnects correctly.

SSE/HTTP streaming handler 先鉴权/限流、创建 request id 与取消 token，逐 token 写出并 flush；写失败、客户端断开或 deadline 到达时立即向调度器 cancel，释放 KV/配额，最后在 finally 清理资源。仅成功生成 token 计费并处理重试幂等，测试半开连接、慢客户端背压及解码尚未开始的取消。

## TOGETHER-02｜Design the scheduler for a continuous-batching inference engine.

维护等待队列与运行中请求，每步根据可用 KV blocks、每请求剩余 token、优先级和公平预算选择新 prefill/继续 decode；连续批处理允许不同请求进入退出。chunked prefill 防长输入饿死 decode，申请失败排队或拒绝，完成/取消立即释放页。以 TTFT、每 token 延迟、吞吐、饥饿和碎片率压测长短混合。

## TOGETHER-03｜Explain speculative decoding. When does it help, when does it hurt, and why adapt the speculator to live traffic?

小 draft 模型预测若干 token，大模型并行验证并采纳匹配前缀，在精确接受规则下保持目标分布；收益取决于草稿成本、接受率、验证批量与输出长度。草稿不准/短输出或主模型验证受限时反而慢。按实时请求类型、语言和上下文选择/训练 speculator，并按同质量 p95 与 token/s 控制启停。

## TOGETHER-04｜Price a dedicated endpoint: estimate cost per million output tokens for a 70B model, and explain the throughput-latency trade.

成本/百万输出 token = 年化 GPU+网络/机房+运维+冗余成本 / 实际可售输出 token（按实际利用率和 SLA）。70B 权重/量化、输入长度和并发决定资源；大 batch 可增吞吐降低单位成本，却使排队和 p95 恶化。给峰值/平均负载场景与保底容量，不用理论峰值 token/s 定价。

## TOGETHER-05｜A customer's distributed training job on your GPU cluster gets 55% scaling efficiency at 64 nodes. Debug it.

从每节点 MFU、跨节点 all-reduce/all-to-all、数据加载、检查点、straggler 与故障重试 trace 分解 55% 效率。做 1→2→8→64 节点强扩展曲线，核网络拓扑、TP/PP/DP 布置和微批空泡；逐项调整重叠/分片/批量，比较有效 token/s 和 loss 一致性，别只追 GPU 利用率。

## TOGETHER-06｜Design a serverless inference platform serving 100+ open models on a shared GPU fleet.

模型目录标记权重大小、内核、授权、质量与热度；路由热门模型常驻 GPU、温模型弹性池、冷模型异步加载并返回明确等待/容量错误。多租户 token/并发配额、负载隔离、缓存安全与模型版本路由，预热/逐出考虑冷启动成本；监控成功率、TTFT、GPU 驻留与每模型毛利，避免 100+ 模型全部常驻。

## TOGETHER-07｜A customer wants to migrate from a proprietary frontier-model API to an open model. How do you run that engagement?

先拿客户真实任务/安全/延迟/成本样本做基线和对照，不用公共榜单代替业务评测；选许可证可用的候选模型，补工具 schema/prompt/检索或 LoRA。迁移按影子→小流量→扩大，比较质量、隐私、回退、每任务成本和线上成功率；提供可逆网关与监控，明确长尾不达标场景。
