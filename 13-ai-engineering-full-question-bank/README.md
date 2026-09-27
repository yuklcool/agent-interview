# 跨公司 AI Engineering 全量面试题库

本目录是公司维度 AI Engineering 面试题库的原题索引与逐题答案。主仓库侧重 Agent 工程原理、运行时机制和真实项目分析；本目录扩展至 LLM、推理/GPU、RAG、Agent、后训练、安全、多模态、系统设计和编码题。

## 文件

- [00-全量原始题目索引](00-all-598-questions.md)：598 道英文原题，按技术主题与公司分组。
- [01-深度答案样板](01-deep-answer-samples.md)：5 道代表题的中文深度答案，含 Mermaid 图。
- [02-答案编写规范与覆盖映射](02-answer-writing-guide.md)：统一答案结构及与主知识库既有章节的映射。

来源清单统计 598 道题：119 道跨公司高频题、479 道公司专项题，覆盖 35 个公司/公司组和 13 类技术主题。两类可能主题重复，这是来源的双索引设计。题目保留英文原文，中文说明和答案由本项目重新组织。

## 逐题答案（598 / 598）

每道题保持英文原题与原分组顺序，下面的题号可直接对应 [全量题目索引](00-all-598-questions.md)。跨公司题和公司专项题即使主题相近，也分别按原题作答；公司问法会补其特定业务、规模与边界。部分编码题提供算法和复杂度思路，面试实操时可按目标语言补完整实现；行为题是作答结构，需替换为本人真实经历。

### 跨公司高频题（119）

| 序号 | 主题答案 | 题数 |
|---:|---|---:|
| 1 | [LLM 内部原理与架构](answers/01-llm-internals.md) | 16 |
| 2 | [推理、服务与 GPU 性能](answers/02-serving-gpu.md) | 15 |
| 3 | [RAG 与检索](answers/03-rag-retrieval.md) | 12 |
| 4 | [Agent 与工具调用](answers/04-agent-tools.md) | 12 |
| 5 | [微调、后训练与对齐](answers/05-post-training.md) | 12 |
| 6 | [评测与可观测性](answers/06-evaluation-observability.md) | 10 |
| 7 | [安全、Security 与负责任 AI](answers/07-safety-security.md) | 10 |
| 8 | [多模态、语音与 Voice AI](answers/08-multimodal-voice.md) | 10 |
| 9 | [AI 系统设计](answers/09-system-design.md) | 10 |
| 10 | [编码与数据结构](answers/10-coding-data-structures.md) | 12 |

### 公司专项题（479）

| 序号 | 公司答案 | 题数 |
|---:|---|---:|
| 11 | [Anthropic](answers/company/01-anthropic.md) | 37 |
| 12 | [OpenAI](answers/company/02-openai.md) | 31 |
| 13 | [Google DeepMind and Google AI](answers/company/03-google-deepmind.md) | 22 |
| 14 | [Meta (Superintelligence Labs, FAIR, Llama)](answers/company/04-meta.md) | 26 |
| 15 | [xAI](answers/company/05-xai.md) | 10 |
| 16 | [Mistral AI](answers/company/06-mistral.md) | 8 |
| 17 | [Cohere](answers/company/07-cohere.md) | 10 |
| 18 | [DeepSeek](answers/company/08-deepseek.md) | 10 |
| 19 | [Moonshot AI (Kimi)](answers/company/09-kimi.md) | 10 |
| 20 | [Zhipu AI (GLM)](answers/company/10-glm.md) | 11 |
| 21 | [Alibaba (Qwen)](answers/company/11-qwen.md) | 10 |
| 22 | [Sarvam AI](answers/company/12-sarvam.md) | 12 |
| 23 | [Microsoft](answers/company/13-microsoft.md) | 10 |
| 24 | [Amazon (AWS)](answers/company/14-aws.md) | 23 |
| 25 | [Apple](answers/company/15-apple.md) | 11 |
| 26 | [NVIDIA](answers/company/16-nvidia.md) | 13 |
| 27 | [Tesla](answers/company/17-tesla.md) | 11 |
| 28 | [Consumer-Scale ML Companies (Uber, Netflix, LinkedIn, Airbnb, Pinterest, Spotify)](answers/company/18-consumer-ml.md) | 14 |
| 29 | [Databricks](answers/company/19-databricks.md) | 9 |
| 30 | [Groq](answers/company/20-groq.md) | 12 |
| 31 | [Together AI](answers/company/21-together.md) | 7 |
| 32 | [Hugging Face](answers/company/22-hugging-face.md) | 11 |
| 33 | [Scale AI](answers/company/23-scale-ai.md) | 12 |
| 34 | [Perplexity](answers/company/24-perplexity.md) | 15 |
| 35 | [Cursor (Anysphere)](answers/company/25-cursor.md) | 17 |
| 36 | [Cognition (Devin, Windsurf)](answers/company/26-cognition.md) | 9 |
| 37 | [Sierra](answers/company/27-sierra.md) | 12 |
| 38 | [Harvey](answers/company/28-harvey.md) | 11 |
| 39 | [Glean](answers/company/29-glean.md) | 10 |
| 40 | [Character.AI](answers/company/30-character-ai.md) | 12 |
| 41 | [ElevenLabs](answers/company/31-elevenlabs.md) | 8 |
| 42 | [Abridge](answers/company/32-abridge.md) | 11 |
| 43 | [Figure AI](answers/company/33-figure.md) | 12 |
| 44 | [Waymo](answers/company/34-waymo.md) | 12 |
| 45 | [Palantir](answers/company/35-palantir.md) | 20 |

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
