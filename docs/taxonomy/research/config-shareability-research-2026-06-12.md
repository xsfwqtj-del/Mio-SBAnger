# 配置可分享性与可验证性研究

> 日期: 2026-06-12
> 方法: 进化循环 v3.0 — 竞争搜索 + 收敛审计
> 状态: 归档研究（项目已停止）

---

## 立意

**让 Agent 行为配置可跨用户分享，接收者拿去用之后配置能实际生效，且能自己验证。**

子问题锚点:
1. 什么样的配置格式能做到跨用户可移植？
2. 怎么让接收者验证配置真的生效了？
3. 已有生态在可移植性和可验证性上做了什么、漏了什么？

---

## 竞争搜索（3 Agent × 独立策略标签）

### Agent A — 策略标签: 成功案例型

**搜索结论:**

成功案例和可复用模式:

**ECC (Everything Claude Code)** — 251 skills + 63 sub-agents:
- 格式: SKILL.md (Markdown + YAML frontmatter)
- 分发: git clone + configure-ecc skill 自动安装
- 分层: 用户级 (~/.claude/) / 项目级 (.claude/) / 本地 (.claude.local/)
- 验证: 安装后自动检查文件存在性、路径引用、交叉引用
- 跨工具: 与 OpenAI Codex 共享 Agent Skills 开放标准

**SillyTavern 角色卡** — 真正的"拿走即用":
- 格式: PNG + 嵌入 JSON 元数据（单文件打包）
- 分发: 拖拽导入
- 自我包含: 人格、场景、示例对话、系统提示全打包
- 跨平台: SillyTavern/Chub.ai/RisuAI/SpicyChat 兼容

**SOUL.md (Soul Spec)** — 跨工具身份配置:
- 格式: YAML frontmatter + Markdown
- 工具无关文件名
- 社区注册表: `npx clawsouls install`
- 安全扫描: SoulScan 检测泄露密钥、提示注入

**agent-signing / SkillGuard** — 配置签名防篡改:
- Ed25519 签名
- 启动时校验完整性
- HMAC / JWT 多模式支持

**验证体系（三个层次）:**
1. 文件完整性验证（ECC 模式 — 静态检查）
2. LLM-as-Judge 行为验证（KindLM / JUDGE LLM / agent-regression-testing）
3. 加密签名验证（AIVS / tamperbell / cLaw Framework）

**可移植性模式:**
- 严格分层配置（全局/项目/本地）
- 自我包含打包（单文件）
- 路径无关性设计（工具无关文件名、无绝对路径）
- 跨项目差异: 路径引用检查 + 接收者适配

**推荐方向:**
1. Markdown + YAML frontmatter 格式（兼容 Agent Skills 标准）
2. 三层结构: 通用层 + 项目适配层 + 个人覆盖层
3. 三阶段验证: 静态 → 签名 → 行为
4. 分发: git repo + README（最简方案）
5. 构建在 Agent Skills 开放标准之上

**置信度: 高**

**主要风险:**
1. 行为验证层仍薄弱（无业界公认标准工具）
2. 路径绑定无完美方案
3. 语义移植比语法移植更难

---

### Agent B — 策略标签: 反例型

**搜索结论:**

配置分享失败的 6 大根因:

**1. 环境差异导致失效:**
- 文件路径硬编码（LIChess-Claude 35+ 处，Superpowers 硬编码 Jesse 路径）
- 平台差异（Windows vs Linux/WSL2 命令不兼容）
- 代理框架差异（CLAUDE.md 是 CC 专用，Copilot CLI 不读取）
- 自定义配置目录用户完全失效

**2. LLM 选择性忽略规则:**
- Bug #2544: 强制规则被持续忽略（规则声明 "MANDATORY"，Agent 仍跳过）
- Bug #23696: "只回答不执行" 规则被违反数万次，模型默认"帮助性"压倒用户指令
- Bug #29236: Agent 读取规则、确认规则，下一步就违反
- 遵从率衰减: 禁止型指令从 73% 降到 33%（5→16 轮）

**3. 配置冲突与副作用:**
- 幽灵配置: session override 持久存在，无声覆盖默认值
- 继承未定义: 子 Agent 工具集继承歧义
- 默认值静默覆盖显式配置

**4. 安全攻击:**
- Rules File Backdoor (Pillar Security 2025): 不可见 Unicode 字符植入后门，GitHub Copilot 和 Cursor 均受影响
- MCPoison: MCP 配置指向恶意命令执行任意代码
- CLI 配置 RCE: 项目级配置文件结合 prompt injection 远程代码执行

**5. 技能触发冲突:**
- 重叠描述导致静默跳过（~80% 的技能不触发因描述太泛）
- 优先级遮蔽: 同名技能在高优先级作用域无声遮蔽低作用域版本
- 多技能集成后准确率从 89% 降至 67%

**6. Placebo 效应与验证缺陷:**
- .cursorrules 被 Claude 自己称为 placebo
- LLM self-report 不可靠（语义不变性失败，p < 0.001）
- AI 比人类多 49% 同意用户，强化确认偏误
- "工具被调用" ≠ "工具对结果有正面贡献"

**推荐方向:**
1. 可验证的优先级层级（精确到字段覆盖规则）
2. 内置验证机制（外部检测，不依赖 self-report）
3. 环境无关性检查清单
4. 配置隔离与继承语义（must/should/optional 三级）
5. 跨 Agent 框架兼容层
6. 安全扫描入口
7. 冲突检测和降级策略

**置信度: 高**

**主要风险:**
1. 配置分享放大 supply chain 攻击面
2. LLM 遵从率瓶颈无法通过配置格式解决
3. "生效验证"的 placebo 陷阱

---

### Agent C — 策略标签: 边界条件型

**搜索结论:**

**1. LLM 遵从率硬边界:**
- 256 模型整体遵从率仅 43.7% (When Models Can't Follow, 2025)
- 推理追踪中的指令遵从率最佳模型不足 25% (ReasonIF, 2025)
- 系统/用户 prompt 分离的平均主遵从率仅 9.6%-45.8% (Control Illusion, 2025)
- 模型间差异: x-ai 79.3% > Google 58.8% > OpenAI 57.5% > DeepSeek 53.3%
- 20+ 同时约束时遵从率断崖下降
- 格式约束 > 内容约束 > 情境约束 > 风格约束（遵从率排序）
- 中等长度 prompt (~27 词) 为危险区
- 100K token 处超过 50% 性能下降
- Instruction Hierarchy 在 6 个 SOTA 模型上不可靠

**2. 跨框架可移植性硬约束:**
- Hook 机制: CC 14 种事件（含 LLM 判断钩子），Gemini 10 种（BeforeModel 可 mock），Codex 0 种
- system prompt 结构不可通用
- MCP 配置格式不兼容（JSON vs TOML vs YAML）
- 开箱即用只可能在同一个框架内实现

**3. 验证可行性的语义缺口:**
- 可自动化: 安全红线（regex）、工具调用纪律（Hook）、输出格式（schema）
- 只能 LLM 判定: 语气（Alpha 0.326-0.788）、行为模式、复杂度判断
- LLM-as-judge 自一致性仅 0.79 Alpha（可接受阈值 0.8）
- 温度 0 反而损害与人类判断对齐
- 道歉性语言可将偏好扭曲 98%
- 精确约束与语义约束之间无平滑过渡 — 这是二值缺口

**4. 跨用户移植的分类:**
- 必须绑定个人: 用户画像、交互风格、历史行为、安全敏感信息
- 可以完全通用: 安全红线、工具纪律、输出规范、工作流约束、编码规范

**5. 分发/版本管理空白:**
- 无版本号、无自动更新、无依赖管理
- 配置分享本质是"复制文件"

**推荐方向:**

可行路线（现在就能做）:
1. 分层分享模型（通用安全层/行为调优层/个人层）
2. 验证层分级（static/runtime/semantic 标注）
3. 框架锁定优先
4. 约束容量控制（10-15 条规则）

有代价路线（需基础设施）:
5. 配置注册表 + 语义化版本
6. 合并引擎（语义冲突检测）
7. 运行期遵从率监测

不可行路线:
8. 跨模型无损分享
9. 纯 LLM 判定规则可验证
10. 100% 遵从保证

**置信度: 高**

**主要风险:**
1. 模型间遵从率差异 30%+ → 信任崩溃
2. 语义合并不可实现
3. 验证循环的递归风险（谁验证验证器？）

---

## 收敛审计

审计 Agent 结论: **✅ 收敛 — 三个 Agent 无偏离，方向一致，差异仅在实现细节层面。**

### 统一方向

**1. 配置格式: Markdown + YAML frontmatter，三层分层结构**
- 文件格式兼容 Agent Skills 标准
- 三层: 通用层 → 项目适配层 → 个人覆盖层
- 继承语义: must（不可覆盖）/ should（可协商）/ optional（自由覆盖）
- 约束容量控制: 单配置包 ≤15 条核心规则

**2. 验证体系: 三阶段 + 分级**
- 阶段 1 — 静态验证（安装时，完全可自动化）: regex/schema 校验
- 阶段 2 — 加密签名: Ed25519 防篡改
- 阶段 3 — 行为验证: LLM-as-Judge 辅助 + 运行期监测（置信度天花板 Alpha≈0.79）

**3. 可移植性约束**
- 路径无关性: 相对路径或符号名
- 框架锁定: 标注目标框架，不做跨框架无损承诺
- 安全扫描前置: Unicode 检测、规则注入检测

**4. 分发基准**
- git repo + README（最低门槛）
- 通过现有生态分发，不另建平台

### 已知风险矩阵

| 风险 | 严重度 | 缓解 |
|------|--------|------|
| LLM 遵从率硬上限（~43% 平均） | 高 | 约束容量控制 + 非 LLM 验证兜底 |
| 语义合并不可自动化 | 高 | 合并在接收者侧手动确认 |
| 安全攻击面放大 | 高 | 签名验证 + 安全扫描 + 不信任未签名配置 |
| Placebo 效应 | 中 | 验证体系不依赖 self-report |
| 跨框架差异不可消除 | 中 | 框架锁定优先 |
| 模型间遵从率差异 30%+ | 中 | 标注模型兼容性 |

---

## 研究来源

- ECC (Everything Claude Code): https://github.com/affaan-m/ECC
- SillyTavern 角色卡: CCv2/CCv3 规范
- SOUL.md (Soul Spec): 跨工具身份配置标准
- Agent Skills open standard: Claude Code / OpenAI Codex 共享标准
- agent-signing / SkillGuard: 配置签名验证
- KindLM / JUDGE LLM: LLM-as-Judge 行为验证
- AIVS (IETF draft): 便携式 Agent 会话档案格式
- tamperbell: MCP 配置完整性验证
- cLaw Framework: Agent 行为法签名验证
- When Models Can't Follow (2025): 256 模型遵从率研究
- Control Illusion (2025): 系统/用户 prompt 角色分层不可靠
- ReasonIF (2025): 推理追踪指令遵从
- Offscript (2025): GPT-5 违规率
- Rules File Backdoor (Pillar Security, 2025): Unicode 后门攻击
- Prompt Contracts (PCSL): observe/assist/enforce/auto 四级执行模式
- CodeJudgeBench (2025): LLM-as-Judge 可靠性
