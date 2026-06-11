---
name: agent-architecture-audit
description: >-
  Agent/LLM 应用全栈诊断。审计 12 层 Agent 栈：wrapper 回归、记忆污染、工具纪律失败、隐藏修复循环、渲染损坏。
  产出严重度排名的发现 + 代码优先修复方案。
  TRIGGER: 发布 Agent 应用前、添加新 prompt/工具/记忆层后、Agent 行为退化时、同一模型在 playground 正常但包装后异常。
  DO NOT TRIGGER: 通用调试、代码审查、安全扫描、性能基准测试。
origin: oh-my-agent-check (ECC: affaan-m/ECC)
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Agent Architecture Audit

Agent 系统的诊断工作流——隐藏故障在 wrapper 层、陈旧记忆、重试循环或传输/渲染突变背后。

## 何时激活

**强制使用于：**
- 将任何 Agent 或 LLM 驱动的应用发布到生产环境
- 发布带工具调用、记忆或多步工作流的功能
- 添加新 wrapper 层后 Agent 行为退化
- 用户报告"Agent 变差了"或"工具不稳定"
- 同一模型在 playground 正常但在包装器内异常
- 调试 Agent 行为超过 15 分钟仍未找到根因

**不适用于：**
- 通用代码调试 → 用 `agent-introspection-debugging`
- 代码审查 → 用语言特定的 reviewer agent
- 安全扫描 → 用 `security-review`
- Agent 性能基准 → 用 `agent-eval`

## 12 层栈

每个 Agent 系统都有这些层。任何一层都可能破坏答案：

| # | 层 | 哪里会出问题 |
|---|-----|------------|
| 1 | System prompt | 冲突指令、指令膨胀 |
| 2 | Session history | 前轮陈旧上下文注入 |
| 3 | Long-term memory | 跨会话污染、旧话题出现在新对话 |
| 4 | Distillation | 压缩产物作为伪事实重新进入 |
| 5 | Active recall | 冗余的重摘要层浪费上下文 |
| 6 | Tool selection | 错误工具路由、模型跳过必需工具 |
| 7 | Tool execution | 幻觉执行——声称调用但未实际调用 |
| 8 | Tool interpretation | 误读或忽略工具输出 |
| 9 | Answer shaping | 最终响应格式损坏 |
| 10 | Platform rendering | 传输层突变（UI/API/CLI 修改有效答案） |
| 11 | Hidden repair loops | 静默 fallback/retry agent 运行第二次 LLM pass |
| 12 | Persistence | 过期状态或缓存产物作为实时证据复用 |

## 常见失败模式

### 1. Wrapper 回归
基座模型产生正确答案，但 wrapper 层使其变差。
**症状**：模型在 playground 正常但在 Agent 中断裂、添加新 prompt 层后已有行为退化、Agent 听起来自信但自信地错了。

### 2. 记忆污染
旧话题通过历史、记忆检索或蒸馏泄漏到新对话。
**症状**：Agent 提起无关的过去话题、用户纠正不生效（旧记忆覆盖新记忆）、同会话产物作为伪事实重新进入。

### 3. 工具纪律失败
工具在 prompt 中声明但代码不强制执行。模型跳过或幻觉执行。
**症状**："必须用工具 X"在 prompt 中但模型不调用就回答、工具结果看起来正确但实际未执行。

### 4. 渲染/传输损坏
Agent 内部答案正确，但平台层在交付时修改。
**症状**：日志显示正确答案但用户看到损坏输出、隐藏 fallback agent 在交付前悄悄替换答案、终端和 UI 输出不一致。

### 5. 隐藏 Agent 层
静默修复、重试、摘要或召回 agent 无显式契约运行。
**症状**：内部生成和用户交付之间输出变化、"自动修复"循环运行用户不知道的第二次 LLM pass。

## 审计工作流

### Phase 1: 范围
定义审计目标：目标系统、入口点、模型栈、用户报告的症状、时间窗口、适用的层。

### Phase 2: 证据收集
从代码库收集证据：源代码（Agent 循环、工具路由、记忆准入、prompt 组装）、日志、配置、记忆文件。

关键 grep 命令：
```bash
# 仅在 prompt 文本中要求的工具（非代码强制执行）
rg "must.*tool|必须.*工具|required.*call" --type md

# 无验证的工具执行
rg "tool_call|toolCall|tool_use" --type py --type ts

# 主 Agent 循环外的隐藏 LLM 调用
rg "completion|chat\.create|messages\.create|llm\.invoke"

# 无用户纠正优先的记忆准入
rg "memory.*admit|long.*term.*update|persist.*memory"

# 运行额外 LLM 调用的 fallback 循环
rg "fallback|retry.*llm|repair.*prompt|re-?prompt"

# 静默输出突变
rg "mutate|rewrite.*response|transform.*output"
```

### Phase 3: 失败映射
对每个发现记录：症状、机制、来源层、根因、证据（file:line）、置信度（0.0-1.0）。

### Phase 4: 修复策略
默认修复顺序（代码优先，非 prompt 优先）：
1. 代码门禁工具要求——在代码中强制执行，不只是 prompt 文本
2. 移除或缩小隐藏修复 agent——使 fallback 显式化带契约
3. 减少上下文重复——同一信息通过 prompt+history+memory+distillation 四处出现
4. 收紧记忆准入——用户纠正 > agent 断言
5. 收紧蒸馏触发器——不该压缩的不要压缩
6. 减少渲染突变——透传，不转换
7. 转换为类型化 JSON 信封——结构化内部流，非自由文本

## 严重度模型

| 级别 | 含义 | 行动 |
|------|------|------|
| `critical` | Agent 可以自信地产生错误操作行为 | 下次发布前修复 |
| `high` | Agent 频繁降低正确性或稳定性 | 本 sprint 修复 |
| `medium` | 正确性通常保持但输出脆弱或浪费 | 下个周期计划 |
| `low` | 主要是表面或可维护性问题 | backlog |

## 快速诊断问题

| # | 问题 | 如果是 → |
|---|------|---------|
| 1 | 模型能否跳过必需工具仍然回答？ | 工具未代码门禁 |
| 2 | 旧对话内容是否出现在新轮次？ | 记忆污染 |
| 3 | 同一信息是否在 system prompt AND memory AND history？ | 上下文重复 |
| 4 | 平台是否在交付前运行第二次 LLM pass？ | 隐藏修复循环 |
| 5 | 内部生成和用户交付之间输出是否不同？ | 渲染损坏 |
| 6 | "必须用工具 X"规则是否只在 prompt 文本中？ | 工具纪律失败 |
| 7 | Agent 自己的独白能否成为持久记忆？ | 记忆中毒 |

## 反模式

- 不要在排除 wrapper 层回归之前责怪模型
- 不要在没有展示污染路径的情况下责怪记忆
- 不要让干净的当前状态抹去脏的历史事件
- 不要把 Markdown 文本当作可信赖的内部协议
- 不要接受 prompt 文本中的"必须用工具"当代码从未执行
- 保持发现直接、有证据支持、按严重度排名

## 输出格式

1. **严重度排名的发现**（最关键的在前）
2. **架构诊断**（哪层损坏了什么、为什么）
3. **有序修复计划**（代码优先，非 prompt 优先）

不要以赞美或总结开头。如果系统坏了，直接说。

## 报告 Schema

```json
{
  "schema_version": "ecc.agent-architecture-audit.report.v1",
  "executive_verdict": {
    "overall_health": "high_risk",
    "primary_failure_mode": "string",
    "most_urgent_fix": "string"
  },
  "scope": {
    "target_name": "string",
    "model_stack": ["string"],
    "layers_to_audit": ["string"]
  },
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "title": "string",
      "mechanism": "string",
      "source_layer": "string",
      "root_cause": "string",
      "evidence_refs": ["file:line"],
      "confidence": 0.0,
      "recommended_fix": "string"
    }
  ],
  "ordered_fix_plan": [
    { "order": 1, "goal": "string", "why_now": "string", "expected_effect": "string" }
  ]
}
```
