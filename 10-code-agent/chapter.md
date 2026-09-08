# 10. AI Coding / Code Agent / 自动测试

> Code Agent 是很好的 Agent 工程综合题：它同时涉及 Context Engineering、Tool Calling、Sandbox、文件系统、代码搜索、规划、验证、回滚和权限。面试里如果只回答“让模型读代码然后生成 Patch”，通常是不够的。

---

## 10-01. 分支覆盖率和代码插桩原理是什么

### 核心原理

代码覆盖率并不是“测试工具知道哪些行执行过”，本质上需要在字节码/源码执行路径上插入探针。

例如 Java JaCoCo 会在 class load/bytecode 层插 probe：

```text
if (condition) {
    branch A   → probe_1
} else {
    branch B   → probe_2
}
```

测试运行后 probe 被触发，框架再把执行信息映射回源码。

### Line Coverage vs Branch Coverage

```text
if (x > 0) {
   doA();
}
```

只测试 `x=1`：代码行可能 100% 覆盖，但 false 分支从没验证。

因此自动生成单测时不能只追 line coverage，还要看：

- branch
- condition
- exception path
- mutation score

### Code Agent 怎么用

Code Agent 可以把 coverage 当成反馈信号：

```text
生成测试
  ↓
执行
  ↓
coverage report
  ↓
定位未覆盖 branch
  ↓
补测试
```

但不能陷入“只刷覆盖率”：覆盖一行不等于验证行为正确。

---

## 10-02. 生成单测前要做哪些代码前置分析

不要把整个仓库塞给模型。

建议先做静态分析：

```text
Target Method
  ↓
AST / Symbol Table
  ↓
Call Graph
  ↓
Dependencies
  ↓
Side Effects
  ↓
Existing Tests
  ↓
Build/Test Convention
```

需要识别：

- 输入参数和边界
- return/exception
- 分支条件
- 外部依赖
- static/global state
- DB/HTTP/file IO
- time/random
- private helper

然后只构建“与这个测试目标相关的 Repo Context”。

### Java 实践

可以利用：

- JavaParser / Eclipse JDT
- LSP symbol/reference
- Maven/Gradle dependency graph
- JaCoCo
- Surefire/Failsafe

Code Agent 的价值不是替代这些确定工具，而是把它们的结果组合成决策。

---

## 10-03. 哪些代码不适合让 AI 自动生成测试？怎么过滤

“不适合”不等于永远不能测，而是自动生成的风险/成本可能太高。

典型：

- 强依赖硬件
- 强外部系统副作用
- flaky timing/concurrency
- 大量动态代理/反射
- UI/视觉主观判断
- 高安全/合规逻辑且没有人工审核
- 缺乏稳定 test seam 的遗留代码

### 自动过滤评分

可以为目标方法算 testability score：

```text
pure function              +
clear dependency injection +
small call graph           +
existing fixture           +

static global state        -
network side effect        -
non-determinism            -
```

分数太低时不要让 Agent 硬生成，而是先建议重构 test seam。

---

## 10-04. AI 生成代码怎么验证正确性

不能只看“能编译”。至少四层：

```text
Syntax/Compile
   ↓
Unit/Integration Test
   ↓
Static Analysis
   ↓
Behavioral/Domain Validation
```

还可以加入：

- formatter/linter
- type checker
- security scanner
- mutation testing
- differential test
- benchmark

### Agent Loop

```text
Generate Patch
   ↓
Apply in Sandbox
   ↓
Compile
   ↓ fail
Diagnose
   ↓
Patch again
```

关键是每次失败 observation 要结构化，不要把 5MB build log 全塞回模型。

---

## 10-05. 线下测试都过了，AI 代码上线后仍出问题，怎么处理

说明测试环境没有覆盖真实约束。

常见原因：

```text
生产数据分布不同
并发竞态
配置差异
超时/网络故障
权限差异
依赖版本
资源限制
隐藏 side effect
```

### 生产防线

- feature flag
- canary
- rollback
- shadow traffic
- runtime assertions
- SLO monitoring

Code Agent 输出不能直接“测试通过 → 自动全量上线”。

对于高风险变更，必须 Human Review + CI Gate。

---

## 10-06. 工程级 Code Agent 最大的 Context 挑战是什么

最大的挑战不是 context window 不够长，而是**相关性**。

真正修改一个方法可能需要：

```text
当前文件
接口定义
调用方
测试约定
数据库 schema
配置
README/ADR
最近 git diff
```

但不需要仓库 99% 的文件。

### Repo Context Pipeline

```text
User Task
 ↓
Symbol/Path Retrieval
 ↓
Dependency Expansion
 ↓
Recent-change retrieval
 ↓
Existing tests
 ↓
Context ranking
 ↓
Model
```

这就是 Code Agent 的 Context Engineering。

### Durable Artifact

大文件不要全放消息历史，可保存 artifact reference：

```text
artifact://repo/src/A.java#L30-L100
```

Runtime 需要时再加载。

---

## 10-07. AI Coding 最适合和最不适合哪些场景

### 很适合

- boilerplate
- test generation
- API client
- migration script
- small refactor
- code explanation
- repetitive changes

### 风险高

- 架构级重写
- 安全核心
- 金融交易
- 并发底层
- 隐含业务规则很多的 legacy module

选择标准不是“AI 能不能写”，而是：

```text
任务是否可验证
上下文是否可获取
错误是否可恢复
副作用是否可隔离
```

如果有强自动 verifier，Agent 能承担更大自由度。

---

## 10-08. AI Coding 效果突然变差，怎么判断是模型、Context、Repo 结构还是验证链路的问题

建立 Failure Taxonomy。

### 模型问题

相同 Context、相同 Tool，模型版本变更后决策变差。

### Context 问题

关键文件没召回、错误版本、Token 截断。

### Repo 问题

缺少测试、命名混乱、隐式依赖、文档过期，使任何 Agent 都难理解。

### Validator 问题

测试太弱导致错误 Patch 被判成功；或者 build tooling 本身 flaky。

### 怎么定位

保存完整 Trace：

```text
retrieved files
prompt version
model
patch
compile result
tests
coverage
review result
```

然后做 Replay：固定 Context 比模型；固定模型比 Retrieval；固定 Patch 比 Validator。

---

## 本章总线

> Code Agent 的核心不是“模型会写代码”，而是一个受 Harness 管理的软件工程循环：Repo Retrieval 构建上下文，模型提出 Patch，Sandbox 隔离执行，编译/测试/静态分析提供确定性反馈，失败继续迭代，高风险修改再进入 Review/Canary。真正决定系统可靠性的往往是 Context 和 Validator，而不是单纯换更大的模型。
