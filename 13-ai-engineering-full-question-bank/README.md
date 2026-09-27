# 跨公司 AI Engineering 全量面试题库

本目录是公司维度 AI Engineering 面试题库的补充索引。主仓库侧重 Agent 工程原理、运行时机制和真实项目分析；本目录扩展至 LLM、推理/GPU、RAG、Agent、后训练、安全、多模态、系统设计和编码题。

## 文件

- [00-全量原始题目索引](00-all-598-questions.md)：598 道英文原题，按技术主题与公司分组。
- [01-深度答案样板](01-deep-answer-samples.md)：5 道代表题的中文深度答案，含 Mermaid 图。
- [02-答案编写规范与覆盖映射](02-answer-writing-guide.md)：统一答案结构及与主知识库既有章节的映射。

来源清单统计 598 道题：119 道跨公司高频题、479 道公司专项题，覆盖 35 个公司/公司组和 13 类技术主题。两类可能主题重复，这是来源的双索引设计。题目保留英文原文，中文说明和答案由本项目重新组织。

## 与主知识库的映射

| 题目主题 | 优先阅读 |
|---|---|
| Agent Runtime / Loop | [01-agent-runtime/deep-complete.md](../01-agent-runtime/deep-complete.md) |
| Planning / Multi-Agent | [02-planning-routing-multi-agent/deep-complete.md](../02-planning-routing-multi-agent/deep-complete.md) |
| Tool Calling / MCP | [03-tools-mcp/deep-complete.md](../03-tools-mcp/deep-complete.md) |
| Retry / Timeout / 幂等 | [04-reliability-security/deep-complete.md](../04-reliability-security/deep-complete.md) |
| Context / Memory | [05-context-memory/deep-complete.md](../05-context-memory/deep-complete.md) |
| RAG / Retrieval | [06-rag-retrieval/deep-complete.md](../06-rag-retrieval/deep-complete.md) |
| Evaluation / Trace | [07-harness-eval-trace/deep-complete.md](../07-harness-eval-trace/deep-complete.md) |
| 模型、训练与推理服务 | [09-model-training/chapter.md](../09-model-training/chapter.md) |

原题来自公共仓库 pallavi-shekhar/ai-engineering-interview-questions-company-wise。本目录不是该仓库官方中文译本；“涉及公司”仅表示来源清单的归属线索，不代表公司确认原题。生产方案仍需结合具体模型、框架版本、SLO、安全策略和数据规模验证。
