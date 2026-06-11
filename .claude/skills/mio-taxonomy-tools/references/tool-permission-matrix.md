# 工具权限矩阵模板

## 三级权限

```yaml
allow:  # 直接执行，不确认
  - "ls *"
  - "npm test"
  - "git status"

deny:   # 直接拒绝
  - "rm -rf *"
  - "git push -f main"
  - "DROP TABLE *"
  - "修改 .git 目录"
  - "修改系统文件"

ask:    # 执行前确认
  - "rm *"
  - "git push *"
  - "npm publish *"
  - "Write (修改配置文件)"

default: ask  # 未列出 → 默认确认
```

## 按工具类型的默认权限

| 工具 | 默认权限 | 原因 |
|------|---------|------|
| Read / Grep / Glob | allow | 只读，无副作用 |
| Edit / Write | ask | 写操作，可能改坏 |
| Bash | ask | 任意命令执行 |
| MCP (只读) | allow | 无副作用 |
| MCP (写操作) | ask | 有副作用 |

## 安全优先原则

- 不确定 → 默认 ask（不是 allow）
- 危险命令 → deny（不随松弛度变化）
- 安全红线不可被"creative"模式放松
