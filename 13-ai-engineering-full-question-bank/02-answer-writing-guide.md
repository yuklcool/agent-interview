# 答案编写规范与覆盖映射

## 答案模板

每题按题型选择必要章节：原题与中文表述、公司来源、技术主题和假设；考察点与 30 秒回答；原理、公式和合适的 Mermaid 图；正常链路、失败路径与最终状态；工程实现、估算和 Trade-off；常见错误、面试追问与 3～5 分钟回答。

## 图形标准

- 图表达组件职责、信任边界、输入输出、失败分支和状态变化。
- Transformer、KV Cache、RAG 用 Data Flow；Tool Call、MCP、语音流用 Sequence；Runtime 容错、审批与训练用 Workflow / State Machine。
- 系统设计题可以拆为总体架构图和单请求时序图。
- 图必须配文字解释关键边和取舍。

## 内容质量

- 估算写明模型结构、dtype、上下文长度和单位，区分 GiB/GB。
- 区分改变算法/模型结构的优化与调度、分配、数据搬运优化。
- 区分 exactly-once 理想语义与实际的幂等、去重和状态核对。
- ACL 是硬约束，不能只把权限写进 Prompt。
- 项目现状对照具体版本源码，不把建议冒充现状。
- 来源中的公司是归属线索，不证明公司官方确认题目。

## 与已有深度章节映射

主仓库 01～07 的 deep-complete 文档已经覆盖 104 道核心 Agent 工程题。相近内容应链接既有章节并补充新问法，避免重复维护。

| 主题 | 主知识库 |
|---|---|
| ReAct、Tool、Function Calling、MCP | [03-tools-mcp/deep-complete.md](../03-tools-mcp/deep-complete.md) |
| Retry、Timeout、幂等 | [04-reliability-security/deep-complete.md](../04-reliability-security/deep-complete.md) |
| Planning、Multi-Agent | [01-agent-runtime/deep-complete.md](../01-agent-runtime/deep-complete.md)、[02-planning-routing-multi-agent/deep-complete.md](../02-planning-routing-multi-agent/deep-complete.md) |
| Context、Memory、RAG | [05-context-memory/deep-complete.md](../05-context-memory/deep-complete.md)、[06-rag-retrieval/deep-complete.md](../06-rag-retrieval/deep-complete.md) |
| Eval、Trace、Replay | [07-harness-eval-trace/deep-complete.md](../07-harness-eval-trace/deep-complete.md) |

## 计数口径

598 是来源清单条目数，跨公司高频题与公司专项题可能主题重合，不代表去重后的独立知识点数。引用时同时记录技术分类和分类内序号，因为原始局部序号会重复。
