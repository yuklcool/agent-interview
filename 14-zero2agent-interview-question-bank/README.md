# zero2Agent Agent 面试题整理

来源：[zero2Agent「Agent 面试通关」页面](https://onefly.top/zero2Agent/learn-agent-interview/index.html)及其 17 个章节。按原章节顺序收录 **757 道以“Q：”标出的题目**；第 14 章没有独立 Q 标题，另列 **11 条公司代表性问题**，合计 **768 条来源条目**。这是条目数，相近题未按知识点合并，也不等同于来源页面提到的真实面经统计题量。

- [一份完整 Markdown：全部 768 条](00-all-768-questions.md)
- [来源 MIT 许可与署名](SOURCE-LICENSE.md)

题目保留来源原问法，逐条附固定版本源文件的行号链接；本目录整理问题与位置，原作者的“新手答／高手答”留在原站阅读。与已有的 [598 道跨公司 AI Engineering 答案](../13-ai-engineering-full-question-bank/README.md)和 [104 道 Agent 深度章节](../README.md#当前完成状态)是不同来源的题库，可能有主题重合，不能直接相加作为去重后的题数。

## 分章目录

| 章节 | 方向 | 条目 | 文件 |
|---:|---|---:|---|
| 01 | 架构选型：ReAct、Plan-and-Execute 与 ToT 怎么选 | 50 | [阅读](01-architecture-design.md) |
| 02 | 工具管理：参数校验、工具路由与百级工具库 | 40 | [阅读](02-tool-management.md) |
| 03 | 容错与鲁棒性：超时、报错、误操作的工程化处理 | 38 | [阅读](03-fault-tolerance.md) |
| 04 | 记忆与上下文：长对话不丢信息的实战方案 | 66 | [阅读](04-memory-context.md) |
| 05 | 评估与全局观：怎么量化 Agent 好坏、落地最大挑战 | 55 | [阅读](05-eval-and-vision.md) |
| 06 | 多智能体协作：角色分工、通信机制与冲突仲裁 | 35 | [阅读](06-multi-agent-collab.md) |
| 07 | 工程化踩坑：死循环、状态丢失与成本控制 | 72 | [阅读](07-engineering-pitfalls.md) |
| 08 | Prompt 工程与框架原理：模板构建、Skills 机制 | 31 | [阅读](08-prompt-engineering.md) |
| 09 | RAG 与检索系统：从 chunk 设计到多路召回 | 79 | [阅读](09-rag-retrieval.md) |
| 10 | 训练、数据与模型优化：从数据清洗到 LoRA | 126 | [阅读](10-training-and-data.md) |
| 11 | AI 代码分析与测试：覆盖率、插桩、代码过滤 | 21 | [阅读](11-ai-code-testing.md) |
| 12 | 业务 AI 工程分析 | 31 | [阅读](12-business-ai-engineering.md) |
| 13 | 简历项目拷打：面试官追着你的 Agent 项目问到底 | 25 | [阅读](13-project-deep-dive.md) |
| 14 | 各公司面试偏好：按公司备战的高频题速查 | 11 | [阅读](14-company-preferences.md) |
| 15 | 概念考察：Harness Engineering、Context Engineering 与前沿范式 | 22 | [阅读](15-agent-concepts.md) |
| 16 | Agent Infra：Runtime、Sandbox 与可靠执行 | 30 | [阅读](16-agent-infra.md) |
| 17 | AI Infra：训练、推理与 GPU 平台工程 | 36 | [阅读](17-ai-infra.md) |

## 阅读方法

1. 从总索引按题号检索，例如 `Z2A-09-001`。编号为本仓库新编，不是来源的官方题号。
2. 进入对应章节查看小节分组；每题的“原文定位”链接指向 [ranxi2001/zero2Agent](https://github.com/ranxi2001/zero2Agent) 固定提交 `39094a8` 的具体行。
3. 需要详细作答时打开各章的原网页；本站原有的 Agent Runtime、Tool、RAG、评测等深度章节可作工程实践对照。

## 对应本仓库深度章节

| 来源方向 | 本仓库参考内容 |
|---|---|
| 架构选型、执行循环 | [Agent Runtime](../01-agent-runtime/deep-complete.md)、[Planning](../02-planning-routing-multi-agent/deep-complete.md) |
| 工具、MCP 与权限 | [Tools / MCP](../03-tools-mcp/deep-complete.md)、[可靠性与安全](../04-reliability-security/deep-complete.md) |
| 记忆和检索 | [Context / Memory](../05-context-memory/deep-complete.md)、[RAG](../06-rag-retrieval/deep-complete.md) |
| 评估与轨迹 | [Harness / Eval / Trace](../07-harness-eval-trace/deep-complete.md) |

## 来源与计数

来源采用 MIT 许可，著作权归原项目作者；本目录保留许可文本及原文链接。题目标题和公司归属是来源材料的整理信息，不代表所列公司官方确认出题。整理基于上述固定提交；原网站或源仓库后续新增题目时，应重新核对，不自动纳入当前计数。
