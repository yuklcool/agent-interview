# Palantir｜逐题答案

对应原题库公司专项第 35 组，共 20 道。

## PALANTIR-01｜Implement a set of shape classes that compute area, then extend them to handle a new shape.

抽象 Shape.area()，Circle/Rectangle 等各自实现并验证参数非负；新增 Triangle 只需实现面积公式（底×高/2 或三边 Heron 且验证三角不等式），消费者对接口编程，不用在每处 if-else 扩展。单元测试零/非法尺寸与浮点近似；必要时加周长/序列化接口，避免抽象过度。

## PALANTIR-02｜Write a SQL query that joins and aggregates across tables to answer a business question.

先明确业务口径/键/时间范围与一对多关系；示例订单金额按客户分组：`SELECT c.id, SUM(o.amount) FROM customers c JOIN orders o ON o.customer_id=c.id WHERE o.status='open' GROUP BY c.id`。若再 join order_items 需先预聚合避免金额重复，空结果用 LEFT JOIN/COALESCE；参数化过滤和执行计划/索引验证。

## PALANTIR-03｜Build a function that fetches paginated data from a REST API, handling page size and total-page logic.

循环请求 page，从响应的 next cursor/total_pages（按 API 契约）判终止，page_size 限制与稳定排序，累计结果并以 ID 去重；429/5xx 指数退避、超时、错误分类和断点游标。检测重复/循环 cursor、总页数变化、空页及最后一页；流式处理防内存爆炸，凭证不能写日志。

## PALANTIR-04｜Find and fix a double-counting bug in a function that tallies values in a HashMap.

先用最小数据复现同一 key 被累加两次，检查迭代中是否对 key 既初始化又重复加值、是否从多个源重复 join、计数器共享/重试。定义不变量 `sum(map.values())=有效输入值总和`，记录已处理事件 ID 保幂等，修复后对重复 key、零值、并发和重放做属性测试。

## PALANTIR-05｜Debug a program that models infection spread across a social graph.

先明确感染传播模型（同步轮次/概率/方向/隔离），重现小图：链、环、孤点、重复边；检查是否在同一轮更新集合导致一步传播多跳、是否重访节点或边方向颠倒。用双缓冲状态/队列与固定随机种子、验证感染数单调性及时间步，抽样与手算对照。

## PALANTIR-06｜You inherit an 800-line pipeline script from a previous deployment. It's slow and occasionally produces wrong numbers. The original author is gone. Go.

先冻结输入/输出快照和现行指标，建小样本黄金数据与行级 checksum，profiling 找 I/O、重复 join 和倾斜；定位错误的第一阶段而非立刻重写 800 行。提取纯函数、schema/契约、幂等与日志，分步替换并双跑比对数值及性能，灰度/可回滚。与用户核对业务口径防“优化”改变正确结果。

## PALANTIR-07｜Given exports from three customer systems, each with its own customer records, write code to produce one deduplicated set of entities and explain your design.

先标准化姓名/地址/电话/ID 并保原始值、来源和时间；确定性强 ID 优先，再用 blocking 候选与相似度/概率模型，阈值分自动合并、人工复核、保持分离。输出 canonical entity 与源记录映射/证据，防误合并不同人/公司；测 pair precision/recall、跨系统覆盖和增量更新的撤销/拆分能力。

## PALANTIR-08｜Users ask “how many open orders are blocked on a supplier issue?” Plain RAG gets this wrong. Why, and what's the right architecture?

“开放订单”“被供应商问题阻塞”是动态业务对象/状态关系和权限规则，文档 RAG 只能找文字，不能可靠算当前数量。用类型化 ontology/语义层定义订单、供应商、阻塞事件及有效时间和权限，先结构化过滤/聚合查询，再让 LLM 解释结果并引用对象；用 SQL/状态真值对照。

## PALANTIR-09｜What is an ontology in the Palantir sense, and why put LLM agents on top of one instead of on raw tables and documents?

业务 ontology 把实体、关系、动作、权限和业务状态从底层表映射为可操作对象（如 Order、Supplier、block_reason），让 agent 按受控语义接口查询/操作。好处是统一口径、可审计权限和写操作约束；风险是映射/同步错误，需版本化、数据血缘和与原系统一致性测试。

## PALANTIR-10｜Design an LLM agent that files and updates work orders in a customer's ERP: real writes to a production system. How do you make that safe?

模型提议 create/update work order 的结构化参数，后端验证用户权限、状态机、工单约束和版本，再给预览/高风险确认；执行使用幂等键、乐观锁和 ERP 事务，回读确认并审计。注入源数据不获写权限，超时先查询事务状态防重复；评估误单、越权、恢复和人工审批负担。

## PALANTIR-11｜Your platform must support multiple LLM providers, including deployments in restricted environments where only some models are available. How do you architect model selection?

统一模型网关暴露能力契约（文本/工具/多模态、上下文、地域、成本），路由只在租户获批模型和数据驻留范围内选，适配器规范化提示/错误/流。部署受限环境可本地模型回退，但质量和工具行为须分模型回归，记录选择原因与版本，不能静默把敏感数据送外部服务。

## PALANTIR-12｜How do you evaluate an LLM workflow before and after giving it access to production operations?

先在影子/沙箱运行真实流程与模拟 ERP，核对最终状态、越权/误写、失败恢复与人工工作量；上线后以最小权限/限额灰度，采集审计和独立回读，对每个变更可追溯/撤销。按严重度而非平均正确率设门槛，事故触发暂停/回滚；版本化模型、ontology、规则和工具。

## PALANTIR-13｜A freight rail operator loses tens of millions a year to unplanned locomotive downtime. Decompose this into an engineering plan.

把损失拆成故障类型、维修时间、备件/调度及停运机会成本，先建资产/事件/传感器/维护记录的时间线和基线。预测故障风险/剩余寿命结合维修容量与备件库存做优化，现场专家核验误报/漏报；小车队试点 A/B 或准实验，测非计划停机小时、维修成本、安全与数据覆盖，避免把相关报警当因果节省。

## PALANTIR-14｜Design a system to improve traffic in NYC.

先选走廊/时段及目标（总延误、公交可靠、行人安全），融合交通灯、探针、事件和天气数据；仿真/数字孪生评估信号配时与公交优先，逐路口灰度。约束行人通行、紧急车辆和社区公平，监控跨区拥堵转移、污染与事故，不把车速最大化当唯一目标。

## PALANTIR-15｜Design a sync system between two employee record systems.

双系统明确主记录与字段级所有权，CDC/增量游标传变化，统一员工 ID/状态、冲突规则和删除/离职传播；写回用幂等事件 ID、版本戳与循环检测防 ping-pong。加密/审计/最小权限，失败进死信队列可重放，比较源目标行级 checksum 和更新延迟；特别测并发改名/再入职。

## PALANTIR-16｜Design a system that lets multiple teams query a shared dataset without exposing raw data.

在可信计算层按用户/团队行列权限过滤，再提供语义聚合/预定义视图或隐私预算下的统计 API，不把原始数据交给查询方。限制小群体重识别、查询组合/差分攻击，审计与配额；数据血缘和口径版本化，验证合法团队仍能得到足够分析价值。

## PALANTIR-17｜Design an application to catalog and log species while exploring an unfamiliar environment.

移动端离线采集 GPS/时间、照片/音频、候选物种与置信度，专家校验、去重/不确定性记录后同步中央目录。模型给相似物种而不强制确定，位置敏感物种做模糊化与权限控制；断网冲突、地图/分类法版本和证据溯源处理。测识别准确、专家复核负担与观察覆盖。

## PALANTIR-18｜A customer executive says “the AI keeps getting things wrong” and wants to cancel the pilot. Walk me through your next 48 hours.

前 48 小时先承认并冻结可复现错例、评估是否涉及生产写入/安全，必要时停用危险功能；与业务负责人定义“错”并拿 20–50 真实样本追踪数据→ontology→检索→模型→工具首个失配点。给客户具体修复/回滚和验证时间表，盲测修复前后与严重错误率；不以平均 benchmark 驳斥其体验。

## PALANTIR-19｜Why Palantir, and why this team? Tell me about a time you pushed back on a customer request.

Why Palantir/团队要结合可验证的产品特点（复杂数据集成、操作系统、现场交付）与你真实技能，避免空泛赞美。推回客户请求的故事按 STAR：澄清用户目标、指出证据/风险、提出更安全可行试点、如何达成决定和结果；不编履历。

## PALANTIR-20｜Palantir works with defence and intelligence agencies. How do you think about that, and what would you do if asked to build something you're uncomfortable with?

先了解具体用途、授权、受影响人群和可追责边界，按个人伦理与法律/公司政策审视隐私、误用和伤害风险；有疑虑向负责人/合规渠道提出具体问题与替代方案。若仍不符合自己的底线，明确拒绝参与/请求调岗，必要时按适用程序升级；面试诚实表达原则和可执行的决策过程。
