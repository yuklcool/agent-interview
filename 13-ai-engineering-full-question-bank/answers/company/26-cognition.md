# Cognition（Devin / Windsurf）｜逐题答案

对应原题库公司专项第 26 组，共 9 道。

## COG-01｜You have eight hours to build a coding agent from scratch. Describe what you build and, more importantly, what you cut.

八小时做单仓库、单任务闭环：读取 repo/搜索→计划→补丁→运行指定测试→检查 diff→提交供审查；隔离 worktree、命令白名单与 token/时间预算。前两小时搭环境和最小基线，中间实现工具状态机与回退，最后真实任务测；砍多代理、自训练、通用浏览器和自动发布，保证能解释失败。

## COG-02｜Cognition published an argument against multi-agent systems and later published what actually works. Reconcile those two positions.

多代理并非天然增益：无清晰任务分解会增加通信、冲突和错误累积；当子任务可独立、接口/验证器明确（并行检索、测试、代码审查）时有用。比较相同计算/时间预算下单代理与多代理的成功率、延迟、冲突和成本；依据实际文章上下文说明条件，而非把观点变化简化为自相矛盾。

## COG-03｜Your agent spends over half its first turn just finding the relevant code. How do you fix that?

先记录首轮 token、工具调用和定位耗时；建仓库地图（路径、符号、依赖、测试）、用户问题到关键词/stack trace 的多路检索，先窄搜后扩散。缓存相同 commit 的索引与过去验证路径，避免把整仓塞上下文；以定位正确文件 Recall@k、首轮耗时和最终任务成功评估。

## COG-04｜You are training an agent model with end-to-end RL in your own harness. Walk through the environment and reward design.

容器化仓库快照、工具 API（搜索/编辑/运行测试）、可重置状态和隐藏验证器；奖励以最终测试/行为正确为主，惩罚越权、误删、成本和无效循环，稀疏奖励可加经验证的阶段信号。防公开测试作弊/奖励投机和训练集污染，隔离网络与凭证，按未见仓库/任务评估。

## COG-05｜Design the execution environment for thousands of concurrent cloud coding agents. It must survive the agent waiting forty minutes for CI.

每任务容器/VM 隔离文件、网络和凭证，持久化工作树与执行日志；长 CI 等待时把 agent 控制状态 checkpoint 到存储、释放昂贵 GPU/CPU，事件或 webhook 唤醒后恢复。任务队列、租约/幂等、配额和 TTL 清理处理数千并发；测冷启动、恢复、泄漏与失败隔离。

## COG-06｜Devin runs asynchronously in the cloud; Windsurf's Cascade runs in the editor next to the user. What actually changes between those two products, technically?

云端异步代理可拥有长任务生命周期、隔离工作树、排队/CI 持续运行和最终 PR；编辑器侧需毫秒级交互、读取未保存 buffer、尊重用户同时编辑与撤销、低延迟取消。二者都需权限与验证，但状态同步、反馈节奏、资源预算、冲突合并和成功指标不同。

## COG-07｜How would you evaluate an autonomous software engineering agent? Explain why SWE-bench pass rates mislead.

SWE-bench pass 受仓库污染、测试覆盖不足、环境差异、尝试次数和补丁质量影响；通过隐藏测试不等于生产可维护。按未见项目、任务类型/难度、完整环境状态、人工代码审查、回归与安全、成本/时延/方差评估；上线看用户接受、后续修复与事故率。

## COG-08｜An autonomous agent has write access to a customer's repository, CI credentials and network access. What is your threat model?

威胁含恶意 repo/README/测试输出提示注入、凭证外泄、依赖安装供应链、越权推送/删除、网络渗出及拒绝服务。隔离容器、最小权限短期令牌、网络 allowlist、命令审计、敏感写操作审批与密钥屏蔽；测试对抗仓库和工具输出，事后可撤销凭证/补丁。

## COG-09｜As a Deployed Engineer, you are rolling Devin into a 2,000-engineer organisation. What do the first ninety days look like?

前 30 天选低风险任务/试点团队，设权限、隔离、数据合规与基线成功率；30–60 天培训、工作流/CI 集成、失败分类和人工审查；60–90 天分团队扩大、容量与成本优化、事故/回滚演练。比较完成任务时间、审查负担、缺陷、安全事件和采用率，避免只看创建的 PR 数量。
