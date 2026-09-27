# Cursor（Anysphere）｜逐题答案

对应原题库公司专项第 25 组，共 17 道。

## CURSOR-01｜Build a hash tree to organise data in a repository.

叶节点按规范路径与文件内容 hash，目录节点对排序后的 (名称、类型、child hash) hash；内容相同、路径不同仍能区分。增删文件只重新计算祖先节点 O(路径深度+目录排序成本)，跨平台规范化路径/大小写/换行并排除 .git/build 产物；hash 要有域分隔防结构歧义。

## CURSOR-02｜Given a repository snapshot (path → content), build a Merkle tree and write the function returning which files changed between two snapshots without comparing every file's content.

分别构建快照树，递归比较根 hash：相同则整个子树跳过，目录 hash 不同才对子节点名称集合做并集递归，叶 hash 不同报告新增/删除/修改。构建初次 O(总字节) 哈希，已有 hash 的差异遍历接近变化路径数量；需处理重命名为删除+新增或额外检测相同内容。

## CURSOR-03｜Print the top view of nodes in a binary tree.

BFS 遍历并记录每个节点水平距离 hd（左 -1、右 +1），每个 hd 首次遇到的节点为上视图；输出 hd 升序。O(n) 时间、O(n) 队列/映射，空树返回空，需确认“top view”而非树根向下路径。

## CURSOR-04｜Find duplicate files in a file system.

先按文件大小分组，单例跳过；再对候选做快速部分 hash，最后流式完整 SHA-256 和字节对照以消除碰撞/读时变化。跟踪 inode 避免硬链接重复统计，决定是否跟随 symlink 和权限错误；并行 I/O 限流，报告路径及内容版本。

## CURSOR-05｜Implement the core of an editor text buffer: efficient insert/delete at arbitrary positions and fast line lookup. What structure do you pick?

选 piece table 或 rope：piece table 保原文本和 append-only 追加缓冲，平衡树按子树字符数/换行数索引，任意位置插删 O(log n+片段调整)，第 k 行查找 O(log n)。维护 undo、Unicode 字符/字节 offset 和并发编辑版本，测试连续输入、巨大文件与跨行删除。

## CURSOR-06｜Serving a custom completion model to millions of DAU: walk me through the inference-cost model and your top three levers.

成本=DAU×调用/日×输入/输出 token×模型运行单价，加空转容量、缓存、网络与峰值副本；补全短输出高 QPS，TTFT/端到端更敏感。三杠杆：轻量蒸馏模型+量化、上下文/输出控制与前缀/结果缓存、动态批处理/路由；每项用接受率、p95 与单位有效接受建议成本验收。

## CURSOR-07｜Long context windows keep getting cheaper. Why not drop retrieval and stuff the whole repo into context for every request?

100k 文件全塞上下文的 token/TTFT/成本高，且无关内容会稀释注意力；频繁编辑需要重算，权限/忽略文件也难控制。用符号/依赖图、路径/词法和向量多路检索取相关片段，用户当前文件可保长上下文；测真正跨文件任务的 evidence recall、修改正确率和费用，再按需要扩大窗口。

## CURSOR-08｜Design the harness for an agent that makes multi-file changes from a natural-language task. How do you keep it from wrecking a codebase?

在隔离 worktree/容器读库，先 plan 文件与测试，工具写入只允许工作区且带 diff/版本预条件；每步运行格式化/构建/相关测试，失败回滚到检查点或让用户审查。限制网络/凭证/命令和 token 预算，敏感/大范围改动先确认；输出可审查 diff、测试证据及未解决风险。

## CURSOR-09｜Design an agentic AI system that can autonomously adapt to new tasks.

采用观察→目标分解→工具行动→验证环境状态→反思/修订循环，用可扩展工具 schema 和检索适配不同仓库/任务。对新任务先探测环境与成功标准，不让模型自评终态；记忆只存可验证事实，超预算/重复失败触发人工接管。测跨任务泛化、恢复率、成本和安全。

## CURSOR-10｜Design Cursor's tab (next-edit prediction) system: it must feel instant (sub-100 ms perceived latency) for millions of daily users.

本地监听编辑事件与光标上下文，轻量模型或缓存即时给下一编辑候选，较重远端推理异步预取，感知 <100ms 可先展示缓存/确定性候选而非假装最终模型已算完。取消过期请求、版本戳防陈旧建议；度量接受率、编辑后保留率、实际/感知延迟和键入干扰。

## CURSOR-11｜How would you index a 100k-file monorepo so an AI editor can retrieve relevant context, and keep the index fresh as the user edits?

索引分层：文件路径/符号 AST/调用依赖与 chunk embedding，初次并行建库，忽略 generated/vendor 文件；编辑时增量更新受影响文件/依赖，查询合并未落盘的本地 buffer 与旧索引。hash/version 保一致、后台压缩与删除传播，按跨文件召回、索引新鲜度、CPU/磁盘与隐私评价。

## CURSOR-12｜The model is streaming a multi-file edit while the user keeps typing in one of those files. How do you apply the edits without corrupting the buffer?

模型生成基于快照版本，应用时比对每文件当前 buffer hash；未变可原子 apply，已变用三方合并（基线、模型补丁、用户当前内容），冲突局部标记并让用户选择，绝不静默覆盖。多文件修改可先 staging，再原子提交/回滚；测试同时输入、撤销和跨文件引用。

## CURSOR-13｜Your agent model outputs an edited version of a 500-line file. Applying it verbatim is slow and error-prone. How do you make “apply” fast and reliable?

把整文件输出与原始 AST/文本做结构化 diff，只输出最小 hunks，按上下文锚点和文件版本精确应用；若锚点重复/已变化，做三方 merge 或重新生成局部补丁。预览、格式化与相关测试检查语义，比较 apply 成功率、误改行数和延迟。

## CURSOR-14｜An agent needs to iterate on code (run builds, tests, lints) without disturbing what the user sees in their editor. Architect that.

每代理独立 worktree/容器运行命令，资源/网络/凭证最小权限，构建缓存可共享只读但输出隔离；后台作业有状态/超时/取消，结果以 diff 和测试日志回传。用户编辑器只接收审查后的补丁，合并冲突明确处理，避免 agent 测试改动污染当前工作树。

## CURSOR-15｜How do you evaluate a code-editing model before shipping it? Design the offline and online eval story for tab or agent edits.

离线用版本锁定仓库/补丁任务、隐藏测试与 diff 人审，tab 测接受/编辑后保留、agent 测最终环境状态、成本和安全；多次运行看方差及基准污染。线上灰度看建议采纳后撤销率、任务完成、p95、用户修复负担和故障回滚，不能仅凭“建议点击”判断有用。

## CURSOR-16｜You have two days in our codebase and no assigned task. What do you build, and how do you spend the time?

两天：先复现真实用户痛点，读编辑器/索引/推理路径与现有 issue；选一个可交付的小改善（如索引新鲜度可视化和陈旧建议取消），写最小测试与测量，再提交可审查 PR/演示。列出未验证假设、回滚和下一步，不在陌生代码库做大范围重构。

## CURSOR-17｜Tell me about a time you made short-term sacrifices for long-term gains.

真实 STAR：为长期可靠性/成本舍弃的短期功能或速度，如何量化取舍、争取团队支持、阶段性里程碑与最终效果；若结果未如预期，说明修正。用可核实数字和自己的贡献。
