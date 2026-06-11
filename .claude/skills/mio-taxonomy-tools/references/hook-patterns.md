# CC Hook 配置模板

## settings.json 注册

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "python path/to/guard.py",
          "timeout": 10
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "python path/to/post-check.py"
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "python path/to/on-stop.py"
        }]
      }
    ]
  }
}
```

## Python Hook 脚本模板

```python
#!/usr/bin/env python3
"""PreToolUse guard — 拦截危险命令"""
import sys, json, re

DENY_PATTERNS = [
    r"rm\s+-rf",
    r"git\s+push\s+-f\s+(main|master)",
    r"DROP\s+TABLE",
]
ASK_PATTERNS = [
    r"rm\s+",
    r"git\s+push",
    r"npm\s+publish",
]

def main():
    hook_data = json.loads(sys.stdin.read())
    command = hook_data.get("tool_input", {}).get("command", "")

    for pattern in DENY_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return {"decision": "deny", "reason": f"危险命令已拦截: {command}"}

    for pattern in ASK_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return {"decision": "ask", "reason": f"需要确认: {command}"}

    return {"decision": "approve"}

if __name__ == "__main__":
    print(json.dumps(main()))
```

## 常用匹配器

| matcher | 覆盖的工具 |
|---------|-----------|
| `Edit\|Write` | 文件编辑和写入 |
| `Bash` | Shell 命令 |
| `Grep` | 代码搜索 |
| `.*` | 全部工具 |

## 从已有配置学习

用户生产环境实际运行的 Hook: `D:\mio\.claude\settings.json`
