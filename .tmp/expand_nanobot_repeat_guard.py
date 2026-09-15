from pathlib import Path

path = Path('docs/supplement-2026-runtime-reliability-eval-memory-04.md')
text = path.read_text(encoding='utf-8')
start = text.index('# 12. nanobot 当前代码怎么对应这套设计')
end = text.index('# 13. 如果结合 AgentDock，我会怎么落地', start)

replacement = r'''# 12. nanobot 当前代码怎么对应这套设计

当前 nanobot 对“重复外部查询”的实现非常适合做这一题的源码追问，因为它体现了一个典型 Harness 原则：**不要只在 Prompt 里告诉模型“不要重复调用 Tool”，而是在 Tool 真正执行之前，用确定性的 Runtime Guard 做硬拦截。**

当前相关代码主要分布在：

```text
nanobot/agent/runner.py
nanobot/agent/tools/execution.py
nanobot/utils/runtime.py
```

核心调用发生在 `execution.py`：

```python
lookup_error = repeated_external_lookup_error(
    tool_call.name,
    tool_call.arguments,
    external_lookup_counts,
)

if lookup_error:
    event = {
        "name": tool_call.name,
        "status": "error",
        "detail": "repeated external lookup blocked",
    }
    return _with_retry_hint(lookup_error), event
```

最关键的是执行顺序：

```text
LLM 产生 Tool Call
        ↓
repeated_external_lookup_error(...)
        ↓
重复次数超限？
   ├─ Yes → 返回 Tool Error Observation
   │          ↓
   │      不执行真实 Tool
   │
   └─ No  → prepare_call
              ↓
          before_execute_tool hook
              ↓
          tool.execute(...)
```

所以第三次相同外部查询被拦截时，真实 `tool.execute()` 根本不会执行，外部 HTTP 请求、Provider QPS 和 API 配额也不会继续被消耗。

## 12.1 `external_lookup_counts` 是什么？生命周期在哪里？

`AgentRunner._run_core()` 开始一次运行时创建：

```python
external_lookup_counts: dict[str, int] = {}
```

随后每个 iteration 执行 Tool 时，都会把**同一个 dict**传下去：

```text
AgentRunner._run_core()
        │
        ├─ external_lookup_counts = {}
        │
        ├─ Iteration 0
        │     └─ execute_tool_calls(..., external_lookup_counts)
        │
        ├─ Iteration 1
        │     └─ execute_tool_calls(..., external_lookup_counts)
        │
        └─ Iteration 2
              └─ execute_tool_calls(..., external_lookup_counts)
```

因此它可以跨同一次 Agent Run 的多个 LLM iteration 统计重复查询。

但它不是：

```text
Redis 状态
数据库状态
Session 长期状态
跨进程共享状态
```

下一次新的 `_run_core()` 会重新创建空字典，所以它本质是：

> **当前 Run/Turn 内的短生命周期 Loop Guard State。**

这也说明它解决的是“当前 Agent Loop 正在原地重复搜索”，而不是跨会话、跨实例的重复治理。

## 12.2 nanobot 如何判断“这是同一个查询”？

真正生成查询标识的是 `nanobot/utils/runtime.py` 中的 `external_lookup_signature()`。

当前只专门处理两个 Tool：

```text
web_search
web_fetch
```

核心逻辑可以简化成：

```python
def external_lookup_signature(tool_name, arguments):
    if not isinstance(arguments, dict):
        return None

    if tool_name == "web_fetch":
        url = str(arguments.get("url") or "").strip()
        if url:
            return f"web_fetch:{url.lower()}"

    if tool_name == "web_search":
        query = str(
            arguments.get("query")
            or arguments.get("search_term")
            or ""
        ).strip()
        if query:
            return f"web_search:{query.lower()}"

    return None
```

例如：

```text
web_search(query="Nanobot Agent")
```

会生成：

```text
web_search:nanobot agent
```

下一轮：

```text
web_search(query="nanobot agent")
```

生成的仍是：

```text
web_search:nanobot agent
```

于是两次调用命中同一个计数项。

这里要特别注意：nanobot 当前没有做 SHA256，也没有复杂的 `ActionFingerprint` 对象。**这个 signature 字符串本身就是去重 Key。**

所以前面讲的通用设计：

```text
ActionKey = tool_name + canonical_args + scope + state_version
```

在 nanobot 当前实现里，是一个更轻量、更特化的版本：

```text
web_search → tool_name + lower(query)
web_fetch  → tool_name + lower(url)
```

## 12.3 为什么第三次开始拦截？

`runtime.py` 当前定义：

```python
_MAX_REPEAT_EXTERNAL_LOOKUPS = 2
```

计数逻辑是：

```python
count = seen_counts.get(signature, 0) + 1
seen_counts[signature] = count

if count <= _MAX_REPEAT_EXTERNAL_LOOKUPS:
    return None
```

因此真实行为是：

```text
第 1 次相同查询
count = 1
→ Allow

第 2 次相同查询
count = 2
→ Allow

第 3 次相同查询
count = 3
→ Block

第 4 次及以后
→ Block
```

它不是“一出现重复就禁止”，而是给同一查询保留一个非常小的尝试预算。外部查询可能因为瞬时网络异常、Provider 波动等原因需要有限重试，所以这里更像：

```text
Exact Lookup Attempt Budget = 2
```

而不是一个一次性的去重锁。

## 12.4 被拦截后为什么 Agent 还能继续？

超限时，`repeated_external_lookup_error()` 返回的不是 Python Exception，而是一段 Tool Error 文本：

```text
Error: repeated external lookup blocked.
Use the results you already have to answer,
or try a meaningfully different source.
```

`execution.py` 再通过 `_with_retry_hint()` 追加：

```text
[Analyze the error above and try a different approach.]
```

最终这段内容作为 **Tool Observation** 回到模型上下文：

```text
LLM
 ↓
第 3 次提出相同 web_search
 ↓
Runtime Guard 拦截
 ↓
不访问真实 Search Provider
 ↓
生成 Tool Error Observation
 ↓
进入下一轮 LLM
 ↓
模型重新决策
 ├─ 使用已有结果回答
 ├─ 换真正不同的 Query
 ├─ 换信息源
 └─ 停止继续搜索
```

这体现了一个非常重要的 Runtime 思路：

> **Runtime 可以拒绝模型提出的 Action，但不必因此把整个 Agent Run 判失败；更合理的是把拒绝结果作为 Observation 返回，让模型在硬边界内重新规划。**

## 12.5 它统计的是“尝试次数”，不是“成功次数”

计数发生在 `tool.execute()` **之前**。

所以即使：

```text
第 1 次 web_search
→ Provider 网络失败

第 2 次相同 web_search
→ Provider 网络失败

第 3 次相同 web_search
→ Runtime 直接 BLOCK
```

仍然会触发 Guard。

因此 `external_lookup_counts` 的准确含义是：

> **相同 External Lookup Signature 在当前 Run 中被尝试了多少次。**

而不是：

> 成功拿到结果多少次。

所以它更像一个“Loop Retry Budget”，而不是 Cache 计数器。

## 12.6 并发 Tool Call 时会不会计数乱掉？

nanobot 可以把 `concurrency_safe` Tool 通过 `asyncio.gather()` 并发执行，但 `_execute_tool_call()` 一进入函数，首先执行的就是同步的：

```python
repeated_external_lookup_error(...)
```

这个 Guard 之前没有 `await`。

在单个 asyncio event loop 内，同一批协程会先后完成这段同步计数逻辑，之后才进入后续 `await`，并且它们共享同一个 `external_lookup_counts`。因此同一批中出现完全相同的 external lookup，也会消耗同一个重复预算。

但这仍然只是**进程内、当前 Run 内状态**。如果未来把一个逻辑 Run 真正拆到多个进程或节点并行，就不能继续依赖普通 Python dict，需要把 dedup/budget 状态提升到共享 Runtime State、Redis、数据库或统一调度器。

## 12.7 当前实现能识别什么，不能识别什么？

它可以识别：

```text
web_search("Nanobot Agent")
web_search("nanobot agent")
```

因为做了：

```python
.strip().lower()
```

但识别不了语义相同、字符串不同的查询：

```text
web_search("上海酒店")
web_search("上海的酒店")
web_search("上海住宿")
```

也识别不了普通业务 Tool：

```text
query_device(project_id="P1")
query_device(project_id="P1")
query_device(project_id="P1")
```

因为 `external_lookup_signature()` 对 `query_device` 会返回 `None`。

所以 nanobot 当前解决的是：

```text
Exact / Near-exact repeated external lookup
```

没有解决：

```text
Generic Tool Dedup
Semantic No-progress
State-aware Dedup
Cross-run Dedup
Business Idempotency
```

## 12.8 `web_fetch` 还有一个值得追问的实现细节

当前 `web_fetch` 直接把：

```python
url.lower()
```

作为 signature 的一部分。

这是一个轻量防循环实现，但不是严格 URL Canonicalization。hostname 通常大小写不敏感，但 URL path 理论上可能区分大小写：

```text
https://example.com/API/User
https://example.com/api/user
```

当前 Guard 会把它们当成同一个 signature。

如果做更严格的企业实现，应该解析 URL：

```text
scheme   → normalize
host     → lowercase
port     → normalize default port
path     → 按 URL 语义保留
query    → canonical sort / normalize
fragment → 视场景忽略
```

这个细节也说明：nanobot 当前目标不是构建一个通用 Dedup Engine，而是用较低复杂度解决“模型连续重复 Web 查询”这个高频问题。

## 12.9 测试是怎么证明 Guard 真生效的？

当前测试 `tests/agent/test_runner_tool_execution.py` 对行为有明确断言：重复 external lookup 被阻止后，第三个 Tool Message 中包含：

```text
repeated external lookup blocked
```

同时真实 Tool：

```text
execute.await_count == 2
```

两个断言一起才完整：

```text
Tool Message 出现 blocked
```

证明模型收到了 Guard Observation；

```text
真实 execute 只有 2 次
```

证明第三次确实没有继续打到下游。

## 12.10 这段源码真正体现的设计思想

不要只记：

```text
nanobot 有 repeated_external_lookup_error()
```

更重要的是理解这条控制链：

```text
概率性 LLM 提出 Action
        ↓
确定性 Runtime Guard 校验
        ↓
不允许的 Action 不执行
        ↓
把拒绝结果转成 Observation
        ↓
模型在约束范围内重新规划
```

也就是：

> **LLM 负责提出动作，Runtime 决定动作能不能执行。**

这和 Workspace Boundary、SSRF Guard、权限、Budget、HITL 的基本思想是一致的。

## 12.11 它和 Action Fingerprint 是什么关系？

可以这样理解：

```text
通用 Action Fingerprint：
    tool_name
  + canonical_args
  + execution_scope
  + relevant_state_version

nanobot 当前：
web_search
  → "web_search:" + lower(query)

web_fetch
  → "web_fetch:" + lower(url)
```

所以 nanobot 的 `external_lookup_signature()` 可以看作 **Action Fingerprint 思想的一个极简、专用实现**，但不能反过来说 nanobot 已经实现了完整 Action Fingerprint Engine。

企业级还需要进一步补：

```text
canonical args
state-aware dedup
semantic no-progress
per-tool budget
tenant/user quota
provider circuit breaker
side-effect idempotency/reconcile
```

## 12.12 面试口述版

> nanobot 当前没有做一个很重的通用 Action Fingerprint 系统，而是针对 `web_search` 和 `web_fetch` 做了 per-run repeated external lookup guard。`AgentRunner._run_core()` 会创建一个 `external_lookup_counts` 字典，并在整个 Tool Loop 的多个 iteration 中复用。`web_search` 用 lower-case query、`web_fetch` 用 lower-case URL 生成 signature；同一个 signature 第一次和第二次允许执行，第三次开始在真正 `tool.execute()` 之前直接拦截。拦截不是让整个 Agent 抛异常，而是返回一个 `repeated external lookup blocked` 的 Tool Observation，让模型使用已有结果或者换真正不同的搜索策略。这个机制统计的是 attempt，不是 success，而且只解决 exact repeated web lookup，不解决普通业务 Tool、语义 No-progress、跨 Run 去重和业务幂等。如果做企业级扩展，我会继续加入 canonical args、scope、state version 和 progress/evidence 变化判断。

这个边界在面试里必须说准确。

---

'''

path.write_text(text[:start] + replacement + text[end:], encoding='utf-8')
