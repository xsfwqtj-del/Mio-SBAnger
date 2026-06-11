# 工具可用性

> 维度类型：通用 | 实现方式：文本注入 + 代码参数 | 验证方式：行为拦截 + 规则匹配

---

## 一、定义

**控制 Agent 能用什么工具、每种工具怎么用、什么时候不该用。**

这是 Agent 行为配置中最"硬"的维度之一。行为策略告诉你"不能做什么"，工具可用性告诉你"用什么做"——两个维度共同构成 Agent 的操作边界。

### 控制什么

- 哪些工具/MCP Server/插件可用
- 每种工具的权限级别（allow / deny / ask）
- 工具的触发条件（什么场景下用哪个工具）
- 工具使用的纪律（调错了怎么办、回退策略）
- 工具的凭证管理（Agent 不能直接读取原始 API 密钥）

### 不控制什么

- 工具的内部实现（那是插件/MCP Server 的事）
- 工具返回结果的质量（那是 POST_TOOL 校验回路的事）

### 为什么这个维度经常被忽略

大部分 Agent 框架的默认行为是"装了就能用"。但"能用"和"用对"之间差了一整套纪律体系：

- 装了 `gh` CLI → Agent 可以直接操作 GitHub → 但它应该在 push 前确认吗？
- 装了 `mcp__github__*` → Agent 可以创建 Issue/PR → 但它应该先读 CONTRIBUTING.md 吗？
- 装了文件系统工具 → Agent 可以删除文件 → `rm -rf` 应该被拦截吗？

这些问题没有默认答案。不配工具可用性，等于把武器库的钥匙交给 Agent 然后说"你自己看着办"。

---

## 二、注入位置

| 注入层 | 注入内容 | 注入方式 |
|--------|---------|---------|
| L1 骨架层 | 工具清单（可用工具的元数据） | BUILD 阶段注入 system prompt |
| L2 人格层 | 工具使用偏好（"优先用 X，避免用 Y"） | BUILD 阶段注入 system prompt |
| 代码参数 | 权限矩阵（allow/deny/ask） | PRE_TOOL Hook 消费 |
| 代码参数 | 凭证映射（工具 → API 密钥，Agent 不可读原始密钥） | 工具执行层消费 |

---

## 三、填写方法论

### 3.1 工具清单

**有效写法**（结构化，LLM 能直接路由）：

```yaml
# ✅ 好：每种工具有清晰的适用场景和纪律
工具清单：
  gh:
    用途: GitHub 操作（PR/Issue/文件）
    适用: "创建 PR" "查看 Issue" "推送文件"
    禁用: "删除仓库" "修改组织设置"
    纪律: push 前确认目标分支，不 force push 到 main

  mcp__context7:
    用途: 查询库/框架的官方文档
    适用: "这个 API 怎么用" "最新版本的参数是什么"
    禁用: 查询业务逻辑、调试代码
    纪律: 同一个问题最多查 3 次，查不到就走 WebSearch

  Bash:
    用途: 执行 shell 命令
    适用: 运行测试、安装依赖、git 操作
    禁用: 生产环境操作、数据库写入
    纪律: 危险命令（rm/mv/force push）需要用户确认
```

**无效写法**（只有名字，没有纪律）：

```
# ❌ 差：LLM 不知道什么时候该用、什么时候不该用
可用的工具：gh, grep, bash, mcp__context7, mcp__github
```

**原则**：工具清单不是"有什么"，是"每种工具怎么用"。LLM 需要一个路由表，不是一个菜单。

### 3.2 权限矩阵

三级权限模型：

| 级别 | 语义 | 行为 | 例子 |
|------|------|------|------|
| **allow** | 直接执行 | 不确认，不拦截 | `ls`、`npm test` |
| **deny** | 直接拒绝 | PRE_TOOL 拦截 + 注入纠正提示 | `rm -rf /`、`git push -f main` |
| **ask** | 执行前确认 | PRE_TOOL 挂起，等待用户确认 | `git push`（非 main）、删除单个文件 |

**规则粒度**：从具体命令到通配符匹配：

```json
{
  "allow": [
    "npm test",
    "npm run build",
    "ls *",
    "cat *"
  ],
  "deny": [
    "rm -rf *",
    "git push -f main",
    "git push -f master",
    "DROP TABLE *"
  ],
  "ask": [
    "rm *",
    "git push *",
    "npm publish *"
  ],
  "default": "ask"
}
```

`default: ask` 意味着任何不在上面三个列表中的命令，默认需要用户确认。这是安全优先的默认行为。

### 3.3 MCP Server 配置纪律

MCP 工具不是装了就完了。每个 MCP Server 需要考虑：

1. **这个 Server 在所有场景下都需要吗？** → 不需要的话应该可切换
2. **这个 Server 的工具有副作用吗？**（写操作 vs 只读）→ 写操作应该 ask
3. **这个 Server 和其他 Server 有功能重叠吗？**（如 `mcp__github` 和 `gh` CLI）→ 定义优先级

```yaml
# ✅ 好：MCP 配置带了启用条件和副作用标注
MCP:
  github:
    启用条件: "当前项目是 GitHub 仓库"
    工具:
      - 只读: [get_file_contents, search_code, list_issues]
      - 写操作: [create_issue, push_files] → 需要确认
  context7:
    启用条件: "询问了库/框架的 API 或配置"
    工具: [resolve-library-id, query-docs]
    纪律: 每问最多查 3 次
```

### 3.4 工具纪律的写法

工具纪律告诉 LLM **什么时候不该用工具**——这和"什么时候该用"同样重要：

```
# ✅ 好：明确了"不该用"的场景
工具使用纪律：
1. 能用专用工具解决的，不用 Bash——"查文件"用 Grep，不用 grep 命令
2. 工具返回结果不理想时，最多重试 3 次，然后换策略——不要陷入修理循环
3. 同一个工具连续调用超过 10 次？停下来解释为什么需要这么多轮
4. 写了文件之后必须验证——调 Read 确认内容正确
5. 不要为了一件小事调 5 个工具——先想好需要什么，再一次性调用
```

---

## 四、验证方式

### 4.1 行为拦截（PRE_TOOL Hook）

这是验证轴的"行为拦截"类的核心应用。在工具调用前拦截：

```python
# PRE_TOOL Hook 伪代码
def pre_tool_check(tool_name, tool_args):
    # V1 参数校验
    if tool_name == "Bash":
        command = tool_args.get("command", "")
        if matches_deny_list(command):
            return BLOCK, "此命令已被禁止执行"
        if matches_ask_list(command):
            return ASK_USER, "此命令需要确认"

    # V2 语义合理性
    if tool_name == "Write" and not tool_args.get("content"):
        return REJECT, "Write 操作必须提供内容"

    # 回环保护
    if consecutive_same_tool_calls(tool_name) > 10:
        return BLOCK, "工具回环已达上限 (10)，强制停止"

    return ALLOW
```

### 4.2 ECC 诊断（配置失效排查）

当工具"明明装了但 Agent 不调"时，用 ECC 的 12 层栈诊断：

- **Layer 6 (Tool selection)**：Agent 是否没识别到该用这个工具？→ 检查工具描述是否足够清晰
- **Layer 7 (Tool execution)**：Agent 声称调用了但实际没调用？→ 检查 Hook 是否拦截了
- **Layer 8 (Tool interpretation)**：Agent 调了但忽略了工具输出？→ 检查 POST_TOOL 的处理逻辑

---

## 五、场景模板

### 编程场景

```yaml
工具可用性（编程场景 · strict 级）:

  工具清单:
    - {代码搜索工具}: 查找代码、文件、符号
    - {编辑工具}: 修改代码文件
    - {Shell}: 运行测试、构建、git 操作
    - {GitHub MCP}: 创建 PR、查看 Issue
    - {文档查询 MCP}: 查库/框架的官方文档

  权限:
    allow: [代码搜索, 文档查询, 运行测试]
    deny: [force push, rm -rf, 修改 .git 目录]
    ask: [git push, 删除文件, 修改配置文件]

  纪律:
    - 改代码前先读文件（不能盲改）
    - 写完代码后运行测试验证
    - 同一文件连续编辑超过 5 次 → 先读再继续
    - MCP 查文档每问最多 3 次
```

### 写作场景

```yaml
工具可用性（写作场景 · flexible 级）:

  工具清单:
    - {文件操作}: 读写 Markdown 文档
    - {搜索工具}: 查资料、找引用
    - {Shell}: 运行字数统计、格式检查

  权限:
    allow: [读写文档, 搜索资料]
    deny: [删除文档, 修改系统文件]
    ask: [批量改名, 移动文件]

  纪律:
    - 写新内容前先读已有内容（避免重复）
    - 修改只做必要改动，不做全文重写
```

---

## 六、ECC 对标

| ECC 模块 | 对应本维度 |
|----------|-----------|
| MCP Configs (14 个) | 3.3 MCP Server 配置纪律 |
| Hooks (8 类, PreToolUse) | 4.1 行为拦截 |
| Rules → 安全规则 | 3.2 权限矩阵 deny 列表 |
| AgentShield (安全扫描) | 4.1 V1 参数校验的自动检查版 |

ECC 的 MCP 配置是按 Server 分文件的——每个 Server 一个 JSON。缺点是缺少跨 Server 的优先级和纪律统一描述。本维度的"工具纪律"填补了这个空。

---

## 七、常见陷阱

| 陷阱 | 为什么错 | 怎么改 |
|------|---------|--------|
| 只列工具名，不写适用场景 | LLM 不知道什么时候用哪个 → 要么不用，要么乱用 | 每个工具配一个"适用/禁用"表 |
| 权限矩阵只有 allow 和 deny，没有 ask | 大量灰色地带的操作（如删除单个文件）被粗暴归类 | 加 `default: ask` 处理灰色地带 |
| 工具回环没有上限 | Agent 可能在"调工具→不满意→重调"中无限循环 | 连续同一工具调用 max=10 |
| 多个工具功能重叠时不定义优先级 | LLM 在 `gh` CLI 和 `mcp__github` 之间随机选 | 明确"有 mcp__github 时优先用 mcp__github" |
| 忘记工具的副作用 | 读操作用了写工具的权限设置 | 区分只读工具和写工具，写工具默认 ask |

---

## 八、真实样例

以下来自生产环境中的 CC settings.json Hook 配置（`D:\mio\.claude\settings.json`）：

```json
{
  "PreToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {"type": "command", "command": "python gitnexus-guard.py"}
      ]
    },
    {
      "matcher": "Grep",
      "hooks": [
        {"type": "command", "command": "python gitnexus-guard.py"}
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {"type": "command", "command": "python gitnexus-guard.py"}
      ]
    }
  ]
}
```

这套配置的纪律逻辑：
- Edit/Write 前 → 提醒跑 impact 分析
- Grep 前 → 提醒可能有更好的搜索方式
- Bash 前 → git 操作后检查索引是否过期

**关键特征**：不是"允许/禁止"的二元开关，而是"在执行前插入一个检查步骤"。
