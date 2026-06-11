---
name: mio-taxonomy-tools
description: >-
  帮用户配置 MCP Server、Hook 规则、技能触发规则、工具权限矩阵。
  TRIGGER: "帮我配 MCP" "加一个 Hook" "工具权限怎么设" "这个工具该不该允许" "怎么让 Agent 不调这个工具" "MCP 配置"
  DO NOT TRIGGER: 通用代码审查、bug 修复
---

# Mio Taxonomy Tools — 配置工具

> 分类学技能 3。帮用户配置 Agent 的工具生态：MCP、Hook、技能、权限。

## 触发条件

- 用户说"帮我配 XXX 工具/MCP/Hook"
- 统筹技能路由过来，指示工具/权限方面有盲区
- 用户说"Agent 总是乱调工具"

## 配置类型与路由

根据用户需求，选择对应配置类型：

| 用户说的 | 配置类型 | 参考 |
|---------|---------|------|
| "MCP 怎么配" | MCP 配置 | 见本文件 §执行流程 → 1. MCP 配置（模板已内联） |
| "加一个拦截" "危险命令" | Hook 配置 | `references/hook-patterns.md` |
| "工具权限" "能不能调" | 权限矩阵 | `references/tool-permission-matrix.md` |
| "技能触发" "什么时候调技能" | 技能规则 | 分类学维度 `skill-trigger-rules` |

## 执行流程

### 1. MCP 配置

```yaml
输出模板:
  {MCP名称}:
    用途: {一句话}
    启用条件: {什么时候需要这个 MCP}
    工具:
      只读: [{列表}]
      写操作: [{列表}] → 需要确认
    纪律: {使用限制，如"每问 ≤3 次"}
    和其他工具的关系: {如果有功能重叠的工具，说明优先用谁}
```

### 2. Hook 配置

Hook 模板（CC settings.json 格式）:
```json
{
  "hooks": {
    "{PreToolUse | PostToolUse | Stop}": [
      {
        "matcher": "{工具匹配正则}",
        "hooks": [
          {
            "type": "command",
            "command": "python {hook脚本路径}",
            "timeout": {秒}
          }
        ]
      }
    ]
  }
}
```

Python Hook 脚本模板:
```python
import sys, json
def main():
    # 读取 CC 传入的 hook 上下文
    hook_data = json.loads(sys.stdin.read())
    # 判断逻辑
    if should_block(hook_data):
        return {"decision": "deny", "reason": "原因"}
    return {"decision": "approve"}
```

### 3. 工具权限矩阵

```yaml
allow: [{可以直接执行的操作}]
deny: [{绝对禁止的操作}]
ask: [{需要确认的操作}]
default: ask  # 灰色地带默认确认
```

rules.json 格式:
```json
{
  "deny": ["rm -rf *", "git push -f main", "DROP TABLE *"],
  "ask": ["rm *", "git push *"],
  "default": "ask"
}
```

### 4. 技能触发规则

```yaml
{技能名}:
  触发: {关键词/语义/手动}
  不触发: {排除场景}
  优先级: {高/中/低}
  恢复: {立即 / 会话级覆盖}
```

## 关键原则

- **安全优先**: 写操作默认 ask，危险操作默认 deny
- **最简可用**: 从 1-2 条最重要的 Hook 开始，不要一次配全套
- **验证生效**: 每个配置给出验证方法
- **跨框架标注**: 如果配置只适用于 CC，明确标注

## 注意事项

- Hook 脚本需要用户自行验证可在本地 Python 环境运行
- MCP 不要全装——context window 会爆。建议 <10 个活跃 MCP
- 多个 MCP 功能重叠时，必须定义优先级

## 边界

**负责**:
- 配置 MCP Server（启用条件 + 工具分类 + 纪律）
- 配置 CC Hook（PreToolUse/PostToolUse/Stop）
- 配置工具权限矩阵（allow/deny/ask）
- 配置技能触发规则（触发条件 + 优先级 + 恢复机制）
- 输出可直接使用的 JSON/YAML/Python 脚本

**不负责**:
- 不写 CLAUDE.md 文本配置 → 交给 writer
- 不搜索新工具/技能 → 交给 discovery
- 不审查代码/修复 bug
- 不保证 Hook 脚本在用户环境可运行（用户需自行测试）

**交接**:
- 需要配置文本（行为策略/交互风格等）→ "建议调 writer: 帮我写 {维度}"
- 不知道有什么工具可用 → "建议调 discovery: 帮我搜 {领域} 的工具"
- 配置后行为未改善 → "建议调 orchestrator: 检查我的配置"
