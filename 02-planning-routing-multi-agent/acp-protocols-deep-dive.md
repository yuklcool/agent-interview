# ACP 名称歧义：Agent Client Protocol 与 Agent Communication Protocol

> 面试题：ACP 是什么？它和 MCP、A2A 有什么区别？
>
> 首先澄清语境：AI Agent 领域存在两个常用缩写为 ACP 的协议概念，不能混为一谈。

## 1. 两个 ACP 分别解决什么

| 名称 | 主要参与方 | 要解决的问题 |
|---|---|---|
| **Agent Client Protocol** | IDE/编辑器/客户端 ↔ 编码 Agent | 客户端如何统一启动、控制并展示 Agent 的任务、事件和审批 |
| **Agent Communication Protocol** | Agent 服务 ↔ Agent 服务 | 不同框架、团队或组织的 Agent 如何发现能力、委派长任务并协作 |

一句话：**Agent Client Protocol 管“客户端如何使用 Agent”；Agent Communication Protocol 管“Agent 如何使用 Agent”。**

## 2. Agent Client Protocol：客户端与 Agent 的互操作

它的动机类似 LSP：如果每个编辑器都要为每个编码 Agent 写专用插件，适配成本是 `N × M`；双方实现统一协议后，成本接近 `N + M`。

典型本地形态是客户端启动 Agent 子进程，以标准输入输出传输结构化消息：

- `stdin`：客户端发起任务、输入、取消或审批结果；
- `stdout`：Agent 返回响应及流式事件；
- `stderr`：只放诊断日志，避免污染协议流；
- 消息层常使用 JSON-RPC 的 request / response / notification 模型，并用明确帧边界避免粘包。

它标准化的是任务会话、流式输出、进度、工具/文件变更、权限确认和取消等 **Agent 生命周期交互**，而不是模型推理本身。

> 面试注意：协议具体版本、传输和帧格式应以所讨论的 ACP 规范为准；回答时优先说明问题边界和生命周期语义，不要把任一实现细节说成所有 ACP 的通用事实。

## 3. Agent Communication Protocol：多 Agent 服务协作

另一类 ACP 面向网络化的多 Agent 协作。它通常需要：

- Agent 能力描述与发现；
- 身份认证、授权和组织边界；
- 任务提交、异步执行、进度/流式回传、取消与最终结果；
- 长运行任务的状态、超时、重试和可观测性。

常见部署可采用 HTTP/REST、流式响应、异步任务 API 与中心注册/经纪组件。中心注册适合组织内治理、目录、审计和访问控制，但不是所有 Agent-to-Agent 体系都必须使用中心目录。

## 4. 与 MCP、A2A 的区别

| 协议/模式 | 方向 | 核心语义 | 不负责什么 |
|---|---|---|---|
| **MCP** | Agent/Host → Tool、Resource、Prompt Server | 标准化能力发现与工具/资源访问 | 业务事务、幂等、全局工作流状态 |
| **Agent Client Protocol** | Client/IDE → Agent | 启动与控制 Agent 会话、接收流式事件 | Agent 调用外部工具的业务治理 |
| **A2A** | Agent ↔ Agent | 独立 Agent 的任务委派、生命周期与结果交互 | 领域一致性、统一的企业注册架构 |
| **Agent Communication Protocol** | Agent ↔ Agent | 多 Agent 发现、认证、异步协作；常可配合中心 Broker | 业务侧幂等、补偿、领域事实 |

最短记忆法：

```text
MCP：Agent 怎么调用工具和数据
Agent Client Protocol：客户端怎么驱动 Agent
A2A / Agent Communication Protocol：Agent 怎么委派或协作
```

MCP 与 A2A/ACP 不是替代关系。一个合理链路可以是：IDE 通过 Agent Client Protocol 驱动主 Agent；主 Agent 通过 A2A 或组织内协作协议委派专业 Agent；专业 Agent 再用 MCP 调用文件、数据库或业务服务。

## 5. 不要把协议能力误认为生产一致性

协议提供互操作，不自动提供：

```text
租户隔离、业务授权、幂等键、分布式事务、补偿、对账、审计、费用归属
```

这些由 Runtime、Control Plane 和领域服务共同承担。尤其跨 Agent 的长任务，即使使用 A2A 或 ACP，也仍需要任务状态机、稳定 request id、超时后的 UNKNOWN/reconcile，以及最终结果校验。

## 6. 面试可直接回答

> ACP 在 Agent 领域有名称歧义，我会先确认语境。Agent Client Protocol 面向 IDE 或客户端与 Agent 的交互，核心价值是将启动任务、流式输出、进度、审批和取消标准化，类似 LSP 降低编辑器与编码 Agent 的双边适配成本。
>
> Agent Communication Protocol 则面向多个 Agent 服务之间的能力发现、认证、长任务委派和结果回传，企业内部常可以配合注册中心或 Broker 做治理。它和 A2A 都属于 Agent-to-Agent 协作问题域，但中心注册是部署和治理选择，不应简单说成所有 A2A 都没有、所有 ACP 都必须有。
>
> MCP 的边界不同：MCP 让 Agent 标准化调用工具、资源和数据源；客户端协议让客户端驱动 Agent；A2A/协作协议让 Agent 委派 Agent。三者可以串联，但协议本身不会替业务系统解决幂等、事务和最终一致性。
