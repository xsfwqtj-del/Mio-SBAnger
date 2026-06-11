---
name: mio-taxonomy-discovery
description: >-
  工具/技能/MCP 的搜索发现范式。不预写清单，而是帮用户搜、评价、推荐。
  TRIGGER: "帮我搜工具" "有什么工具能做X" "推荐一个MCP" "找技能" "搜索发现" "我想做X需要什么"
  DO NOT TRIGGER: 通用代码搜索、文档查询（那是 Grep/Context7 的事）
---

# Mio Taxonomy Discovery — 搜索发现

> 分类学技能 4。不维护静态工具清单。给搜索策略 + 评价框架，Agent 自己去搜。

## 触发条件

- 用户说"我想做 {领域}，需要什么工具/MCP/技能？"
- 统筹技能路由过来，发现工具可用性维度有盲区
- 用户想扩展 Agent 的能力但不知道有什么可用的

## 执行流程

### 1. 生成搜索策略

根据用户的目标领域，生成：

```yaml
搜索策略:
  目标: "{用户想做的事}"
  关键词: [{3-5 个精准搜索词}]
  搜索位置:
    - GitHub: mcp__github search_repositories
    - WebSearch: 搜索 "{领域} MCP server" "{领域} CLI tool"
    - npm: "@anthropic-ai" 相关包
    - Context7: 查相关库的文档（如果已有候选）
```

**关键词生成原则**:
- 包含技术名词变体: "video editing" + "ffmpeg" + "media processing"
- 包含集成关键词: "MCP server" + "Claude Code plugin" + "AI agent tool"
- 包含排除关键词: 如果用户有技术栈偏好，限定语言/平台

### 2. Agent 自行搜索

对每个搜索位置，搜 3-5 个关键词变体。收集候选列表：

```
候选: {名称}
  来源: {GitHub / WebSearch / npm}
  描述: {一句话}
  URL: {链接}
```

不限制候选数量，但建议每轮 ≤10 个候选提交评价。

### 3. 评分

```python
def score(candidate):
    community = stars_to_score(candidate.stars)      # 0-40 分
    activity = recent_to_score(candidate.last_commit) # 0-30 分
    fit = fit_to_score(candidate, user_env)           # 0-20 分
    license = license_to_score(candidate.license)     # 0-10 分
    return community + activity + fit + license
```

| 维度 | 权重 | 评分规则 |
|------|------|---------|
| **社区验证** | 40% | 0-100★→0分, 100-1K→10分, 1K-10K→25分, 10K+→40分 |
| **活跃度** | 30% | commit < 1月→30分, < 3月→20分, < 1年→10分, > 1年→5分 |
| **适用性** | 20% | 匹配用户环境+语言→20分, 需适配→10分, 不匹配→0分 |
| **许可证** | 10% | MIT/Apache→10分, GPL→5分, 无许可证→0分 |

总分 → ★ 评级:
- 85-100: ★★★★★ 强烈推荐
- 70-84: ★★★★ 推荐
- 50-69: ★★★ 可用，注意风险
- 30-49: ★★ 需评估
- <30: ★ 不推荐

### 4. 输出

```markdown
## {领域} 工具搜索报告

### 推荐: {名称} ★★★★☆ (82分)
- 社区: 5.2K stars (25分)
- 活跃: 最近 commit 2 周前 (30分)
- 适用: Python, 支持 MCP (20分)
- 许可: MIT (7分)
- 安装: `npx @scope/package`
- 注意: {需要用户注意的限制}

### 备选: {名称} ★★★ (58分)
...

### 下一步
- 要安装推荐的工具 → 说"帮我配 {工具名}"
- 不满意搜索结果 → 说"换个方向搜 {新领域}"
```

## 关键原则

- **不预写清单**: 不维护静态的工具/技能清单——每次都是现场搜索
- **不替用户选**: 给评分和推荐，让用户决定
- **不限制领域**: 从视频编辑到数据库到游戏开发，什么都行
- **结果可复现**: 每条推荐带来源 URL，用户可以自己去验证

## 边界

**负责**:
- 根据用户目标生成搜索策略（关键词 + 搜索位置）
- 评价搜索结果（★ 评分）
- 推荐 top 1-2 个，给出理由和风险
- 搜索结果对接 tools-config（安装和配置）

**不负责**:
- 不安装工具 → 给安装命令，用户自己执行
- 不配置工具 → 交给 tools-config
- 不写配置文本 → 交给 writer
- 不维护静态工具清单
- 不替用户决定"这个工具好不好"→ 给评分依据，用户自己判断

**交接**:
- 选中了工具 → "建议调 tools-config: 帮我配 {工具名}"
- 需要新的行为规则来配合这个工具 → "建议调 writer: 帮我写 {维度}"
- 不确定是否需要这个工具 → "建议调 orchestrator: 检查我的配置，看这个工具是否填补了盲区"
