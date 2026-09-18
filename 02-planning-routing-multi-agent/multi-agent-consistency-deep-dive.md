# 多 Agent 协作一致性：从任务分发到生产级收敛

> 面试题：如何设计多 Agent 协作中的一致性体系？
>
> 这题考的不是“能否把任务分给多个模型”，而是多个执行单元并发、重试、超时、重启后，如何保证全局业务结果仍然正确、可追踪、可收敛。

## 1. 先定义一致性的边界

多 Agent 一致性至少包含四件事：

1. **结果正确**：最终聚合的结果满足业务约束；
2. **状态统一**：全局任务、计划版本和子任务状态没有互相矛盾；
3. **副作用至多生效一次**：消息至少一次投递、超时重试都不能重复扣款、建单或写入；
4. **异常可收敛**：部分成功、晚到结果、调度重启和异构协议错误都有明确终态或补偿路径。

它不等于分布式“exactly once”。跨消息队列、外部 API 和 Agent Runtime，通常只能做到 **at-least-once delivery + 业务幂等 + 对账/补偿**。

## 2. 典型失效场景

- 拆分粒度重叠，两个 Worker 做了同一业务片段；
- Worker 已成功执行，但 ACK 丢失，调度端将其再次投递；
- 多个 Worker 基于同一旧版本共享状态写回，发生覆盖；
- 用户变更需求后，旧 Plan 的晚到结果污染新 Plan；
- 调度实例宕机或发生主从切换，造成漏发、重发或双重领取；
- Agent 输入输出、错误码和重试语义不同，聚合器无法判断结果是否可信。

## 3. 基线：状态机 + 幂等 + 最终一致性补偿

### 3.1 持久化模型

不要只把任务放在 Prompt、内存队列或聊天历史中。至少有全局任务与子任务两类记录：

```text
global_task
- global_task_id, tenant_id, plan_version, status, result, version
- deadline, compensation_status, created_at, updated_at

collab_subtask
- sub_task_id, global_task_id, agent_id, status, attempt
- semantic_fingerprint, idempotency_key, lease_until, version
- input_artifact_ref, result_artifact_ref, error_code, compensation_status
```

建议的唯一约束：

```sql
UNIQUE (global_task_id, semantic_fingerprint)
UNIQUE (tenant_id, idempotency_key)
```

前者防止一次计划内的语义重复拆分；后者保证同一业务意图重试时不会重复产生副作用。语义指纹可由**业务对象 + 操作类型 + 规范化关键参数 + 时间窗口 + plan_version**计算；它用于去重，不应替代业务侧的幂等键。

### 3.2 全局与子任务状态机

全局任务可采用：

```text
PENDING_SPLIT → RUNNING → AGGREGATING → SUCCEEDED
                       ↘ COMPENSATING → SUCCEEDED | FAILED
```

子任务可采用：

```text
PENDING → LEASED → RUNNING → SUCCEEDED | FAILED | UNKNOWN | CANCELLED
```

关键规则：

- 只允许合法边迁移；已终态不得被普通重试覆盖；
- 状态更新必须携带版本号或 compare-and-set 条件；
- 领取任务使用 lease/visibility timeout，Worker 失联后才允许重新领取；
- `UNKNOWN` 不等于 `FAILED`：外部调用超时只说明本地未知，应先根据业务请求号对账，再决定成功、重试或补偿；
- 聚合器按 `global_task_id + plan_version` 接收结果，拒绝旧计划的晚到写入。

典型 CAS：

```sql
UPDATE collab_subtask
SET status = 'SUCCEEDED', version = version + 1, result_artifact_ref = :result
WHERE sub_task_id = :id
  AND status = 'RUNNING'
  AND version = :expected_version;
```

更新行数为 0 时，不把结果直接覆盖回去；先读取当前状态并按幂等、过期或冲突路径处理。

### 3.3 写入与投递不能靠“两步操作”赌运气

“先写 DB，再发 MQ”会在中间故障时丢消息；“先发 MQ，再写 DB”会产生幽灵任务。常见基线是 **事务内写任务状态和 Outbox 事件**，由独立 Publisher 可靠投递。消费者按幂等键处理，因此允许重复投递。

## 4. 幂等、补偿与结果校验各自解决什么

- **幂等**：同一个业务意图执行多次，业务效果等价于一次；用于抵抗重复投递与安全重试。
- **补偿 / Saga**：多个步骤部分成功后，按业务语义撤销、修正或完成后续动作；它不是简单数据库回滚。
- **结果校验**：在聚合前校验 schema、证据、约束、版本和可信度；避免“格式正确但业务错误”的 Agent 输出进入最终结果。

例如 A 创建草稿、B 写索引、C 发送通知：C 失败时可重试通知；如果任务要求全有或全无，再按领域规则撤销索引、废弃草稿。补偿动作本身也必须幂等并可审计。

## 5. 并发控制与共享状态

共享事实应由领域服务或状态存储维护，不应让 Agent 互相复制整段聊天历史后各自修改。实践上：

- 不可变输入、证据和大产物放 Artifact Store，以引用传递；
- 可变工作流状态放数据库或事件流，并带 `plan_version`、`version` 和 ownership；
- 独立子任务可以并行；同一业务对象的冲突写要串行化、分区或使用乐观锁；
- 汇总器是全局结果的唯一 writer，Worker 只能提交结构化结果和证据；
- 对删除、支付、通知等副作用使用领域层幂等键，不把“模型说已完成”当作事实。

## 6. 调度高可用、异构 Agent 与降级

调度器应无状态多副本，任务事实留在持久存储；通过 lease、幂等消费者、Outbox 和死信队列处理重启与重复。不要用“分布式锁”作为唯一可靠性方案。

异构 Agent 前增加 Adapter 层，统一以下契约，而不侵入各 Agent 原生实现：

```text
TaskRequest / idempotency_key / deadline / cancellation
CanonicalTaskResult / error_code / evidence / retryability
heartbeat / progress / completion callback
```

状态机或核心依赖不可用时，按风险降级：暂停副作用操作，转为单 Agent 串行执行或人工审核，并以最终对账和结果校验兜底。

## 7. 监控与归档

至少观测：任务重复率、幂等命中率、状态冲突率、超时/重试率、`UNKNOWN` 滞留时间、补偿成功率、死信积压、端到端时延、调度可用性和晚到结果丢弃率。

任务归档前必须确认：已是终态、没有活跃 lease、没有待投递 Outbox、补偿已结束，并且超过重试/对账窗口。归档不是“超过七天直接删除”。

## 8. 面试可直接回答

> 多 Agent 一致性不是避免重复分配这么简单，而是保证拆分、执行、汇总和恢复全过程的结果正确、状态统一、无重复副作用且异常可收敛。我会以全局任务状态机、子任务幂等、语义去重、乐观锁和最终一致性补偿为基线。
>
> 任务和子任务必须持久化；拆分时为规范化后的业务意图生成语义指纹，并用唯一约束避免重复分配。所有副作用请求带稳定 idempotency key。全局任务和子任务都有受约束的状态机，状态更新用 CAS，超时的外部调用先进入 UNKNOWN 并对账，不能盲目重试。
>
> 调度层用 Outbox 保证状态写入与投递最终一致，消费者允许至少一次消费但依赖幂等。Worker 只提交结构化结果和证据，聚合器按 plan version 校验并作为最终结果唯一写入者。部分成功用 Saga 式补偿；调度多副本、Adapter 统一异构协议；最后通过重复率、冲突率、补偿成功率和死信积压做持续观测。这样我设计的是可恢复的协作系统，而不只是任务分发。

## 9. 追问：它与现有章节的关系

- 本文聚焦 **跨 Agent 的任务状态与业务收敛**；
- [Multi-Agent State Sharing](multi-agent-state-sharing-deep-dive.md) 侧重共享 State、Plan Version 与晚到结果；
- [Tool Failure、幂等与 UNKNOWN](../04-reliability-security/tool-failure-idempotency-deep-dive.md) 侧重单个外部副作用调用的失败分类、对账和幂等；
- MCP、A2A 或 ACP 解决互操作协议，不替代状态机、权限、事务、幂等和领域对账。
