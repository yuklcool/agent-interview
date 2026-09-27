# 17｜AI Infra：训练、推理与 GPU 平台工程

来源：[zero2Agent 原章节](https://onefly.top/zero2Agent/learn-agent-interview/17-ai-infra/index.html)；[固定版本源文件](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md)。仅整理题目与定位，原站的回答和示例请查看对应章节。按 [MIT 许可](SOURCE-LICENSE.md) 引用，保留来源条目的原始问法与顺序。

本章 36 道题。题号仅用于本仓库检索；原文没有全局唯一编号。

1. **Z2A-17-001** 如何用 Roofline 和算术强度指导 CUDA 算子优化？从 GEMM 分块到寄存器压力如何逐层定位？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L16)

2. **Z2A-17-002** FlashAttention 为什么更快？Online Softmax、Tiling、重计算和不同版本分别解决什么瓶颈？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L30)

3. **Z2A-17-003** 如何从模型结构估算参数量、FLOPs、训练显存、推理访存与 MFU？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L44)

4. **Z2A-17-004** KV Cache 占用如何计算，为什么不能只按请求数做容量规划？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L61)

5. **Z2A-17-005** GPU 内存层次如何使用？Pinned Memory、Shared Memory、Bank Conflict 与异步 H2D/D2H 分别解决什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L87)

6. **Z2A-17-006** 如何估算 All-Reduce/All-to-All 通信量并实现计算通信重叠？拓扑和 RDMA 如何影响结果？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L104)

7. **Z2A-17-007** vLLM/SGLang 的请求调度与 Continuous Batching 如何工作？请求被抢占后如何恢复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L118)

8. **Z2A-17-008** CUDA 的 Thread、Warp、Block、Grid 和 SM 如何映射？SIMT、同步与 Warp 分歧如何影响性能？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L132)

9. **Z2A-17-009** FP8、NVFP4、INT8 与 W4A16 的数值格式、缩放粒度和硬件执行路径有何不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L146)

10. **Z2A-17-010** 量化后为什么不一定更快？量化 Matmul、反量化、Prefill 和 Decode 的瓶颈如何判断？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L160)

11. **Z2A-17-011** 大模型训练吞吐低时，如何用 MFU、Profiler、通信和流水线空泡定位瓶颈？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L174)

12. **Z2A-17-012** 如何设计大模型在线推理服务？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L188)

13. **Z2A-17-013** 流水线并行的 Bubble 从哪里来？1F1B、Zero-Bubble 与 DualPipe 如何调度？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L209)

14. **Z2A-17-014** MoE 的 Expert Parallel 如何做 Dispatch/Combine、负载均衡和通信优化？DeepEP/EPLB 分别解决什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L223)

15. **Z2A-17-015** CPU、GPU 与 NPU 的体系结构和优化目标有什么差异？如何为训练/推理工作负载选硬件？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L237)

16. **Z2A-17-016** 投机采样中 Draft 与 Target 模型如何交互？什么时候会加速，什么时候反而变慢？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L251)

17. **Z2A-17-017** Stride、View/Contiguous 与 NHWC/NCHW 如何影响张量算子的正确性和性能？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L268)

18. **Z2A-17-018** Prefill 与 Decode 的算子形态和瓶颈为何不同？Matmul、KV 传输和量化应如何分别优化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L282)

19. **Z2A-17-019** Attention 与 FFN 的计算量和参数量谁更大？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L296)

20. **Z2A-17-020** CUDA Graph 为什么能降低推理开销？为什么可能额外占显存，Prefill 与 Decode 哪个阶段更适合？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L312)

21. **Z2A-17-021** SpMV 和 GEMM 的计算、访存特征有什么不同？优化方向如何选择？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L326)

22. **Z2A-17-022** PD 分离解决什么问题，Prefill 与 Decode 资源比例怎么定？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L342)

23. **Z2A-17-023** 模型版本升级如何做到可观测、可灰度、可回滚？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L360)

24. **Z2A-17-024** CUDA、Triton、CUTE 与 MLIR 分别位于什么抽象层？算子编译链和选型依据是什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L382)

25. **Z2A-17-025** AIOps 如何结合告警、Metrics、Logs、Trace 和服务拓扑完成证据驱动的 RCA，并安全执行自动处置？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L396)

26. **Z2A-17-026** AI Infra 和 Agent Infra 有什么区别？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L416)

27. **Z2A-17-027** 如果让你设计一个生产级 AI Infra 平台，你会怎么拆？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L439)

28. **Z2A-17-028** 分布式训练为什么容易失败，如何恢复？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L465)

29. **Z2A-17-029** GPU 利用率很低，但请求延迟很高，怎么排查？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L487)

30. **Z2A-17-030** GPU 上的同步方法代码可能有哪些问题，如何排查？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L509)

31. **Z2A-17-031** DeepSpeed ZeRO 的三个阶段分别做什么？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L521)

32. **Z2A-17-032** GPU 峰值性能、计算单元与寄存器等硬件参数如何影响算子性能？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L534)

33. **Z2A-17-033** 大模型训练出现 OOM 时，如何定位原因并进行显存优化？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L548)

34. **Z2A-17-034** Nsight Compute（ncu）和 Nsight Systems（nsys）有什么区别？分别适合分析什么问题？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L562)

35. **Z2A-17-035** 推测解码中如何生成树状候选草稿？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L576)

36. **Z2A-17-036** GPU 调度和普通 CPU 调度有什么不同？ [原文定位](https://github.com/ranxi2001/zero2Agent/blob/39094a8db5e71bc0ef1d1f7f26240536484834d6/learn-agent-interview/17-ai-infra/index.md#L589)

