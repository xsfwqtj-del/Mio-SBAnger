# Mio Taxonomy — 项目上下文

> 新会话冷启动入口。读完就知道项目是什么、做到哪了、下一步做什么。
> **更新记录只追加，不覆盖——每次改动后在上面写当前状态，在下面追加更新记录。**

---

## 当前状态 (每次会话结束时更新此段)

**架构**: 6 技能 + 1 数据
- `mio-taxonomy-orchestrator` — 统筹入口。"检查我的配置"
- `mio-taxonomy-writer` — 写 CLAUDE.md 配置文本
- `mio-taxonomy-tools` — 配置 MCP / Hook / 技能 / 权限
- `mio-taxonomy-discovery` — 搜索发现工具/MCP + 评分推荐
- `mio-jinhua` — 项目自循环完善机制（v3.0，Phase 1-4 架构，策略标签系统+竞争搜索+收敛审计）
- `mio-session-finder` — 从 CC 会话 JSONL 追溯信息/根因
- `error-diagnosis.md` — 症状→根因→修复对照表

**已完成**:
- ✅ 五轴框架 + 9 维度定义
- ✅ 19 份静态文档 (docs/taxonomy/)
- ✅ 4 份 data 文件 (error-diagnosis, questionnaire, routing, memory-mapping)
- ✅ 5 个技能 SKILL.md + 边界声明 + 名词解释
- ✅ evolve 自检清单含减法检查
- ✅ 进化循环 spec v3.0 — 融合 claude进化-skill.md（Phase 结构+策略标签系统）+ v2.1（理论来源）：望闻问切四诊→立意确认→策略标签竞争搜索→比对审计（合规+偏离+收敛，最多3轮）→最终审计→ADR+结果汇报→备份→执行+决策树
- ✅ ADR-0004 — 进化循环 v0.1.0→v2.1 重构决策记录
- ✅ claude进化-skill.md — 已迁移为 `mio-jinhua` 技能（SKILL.md），旧 docs/ 副本已删除

**待定**:
- 非编程场景模板（写作/学习/规划）— 如无实际使用需求可以不补

**设计约束**:
- 技能面向所有用户，不是为某一个人设计。出厂默认、场景模板、触发条件都必须是通用的，不能把个人偏好当通用设计。

**下一步**: 说"进化"跑 `mio-jinhua` v3.0，检验 Phase 1-4 完整流程

---

## 关键路径

| 什么 | 在哪 |
|------|------|
| 技能目录 | `D:\Mio-SBAnger\.claude\skills\mio-taxonomy-*/` |
| 数据文件 | `D:\Mio-SBAnger\docs\taxonomy\data/` |
| 静态文档 | `D:\Mio-SBAnger\docs\taxonomy/` |
| 进化循环 spec | `D:\Mio-SBAnger\docs\evolution-loop-spec.md` (v3.0) |
| 施工方案 | `C:\Users\xsfwq\.claude\plans\jiggly-purring-ripple.md` |
| 蓝图参考 | `D:\Mio-SBAnger\MioForever工程设计蓝图.md` |
| CC 源码分析 | 会话 `b72f465c-081d-4f2a-aa7e-efc62eb25227` |
| ECC 参考 | https://github.com/affaan-m/ECC |

---

## 名词速查

| 术语 | 一句话 |
|------|--------|
| 分类学 | Agent 行为配置的完整维度框架 |
| 五轴 | 内容 → 实现 → 验证 → 元属性 → 注入点 |
| 9 维度 | 行为策略/校验回路/推理模板/工具可用性/技能触发规则/用户画像/交互风格/思维方式/反思提示词 |
| CC | Claude Code |
| ECC | Everything Claude Code (197K★) |
| Hook | CC 生命周期拦截点 (PreToolUse/PostToolUse/Stop) |
| MCP | Model Context Protocol |
| evolve | Claude 自用的项目自检技能 |

---

## 更新记录 (只追加，不覆盖)

### 2026-06-11
- 建立分类学框架：五轴 + 9 维度
- 产出 19 份静态文档 (dimensions/meta/methodology/templates/verification)
- 创建 4 个用户技能: orchestrator, writer, tools-config, discovery
- 创建 1 个 Claude 自检技能: evolve (含减法检查 + 名词解释)
- 创建错误对照自查表 (error-diagnosis.md)
- 创建本文件 (CONTEXT.md) — 新会话冷启动入口
- 参考源: CC 源码泄露分析 (会话 b72f465c), ECC (affaan-m/ECC), evolving-config 社区技能, ECC Continuous Learning v2

### 2026-06-11 (第八次)
- 验升级：3 子 Agent 独立验证。主 Agent 只调度和汇报，不参与判断
- 防自欺机制：随机性+独立上下文 = 低成本锚定。3/3→通过；2/3→通过但下次回验；1/3→纠
- 验升级：立意→可验子条件拆解→逐条对照（参考 Constitutional AI 思路）
- 纠升级：失败≠浪费，记录"为什么没通过"作为方向性梯度信号（参考 STaR / Failure-as-Gradient）
- 研究来源：STaR/B-STaR/HS-STaR(自举循环)、SuperIntelliAgent(学习者/验证者对)、Constitutional AI(宪法自监督)、ANCHOR(人类监督最佳投入点)
- 补全进化后四步：记(最少快照)、验(立意三问)、纠(回退→追问→重搜→重改)、进(分类型沉淀)
- 创建 `change-log.md`——快照存储文件
- 进化全环现在可跑：望闻问切搜索写装记验纠进均已定义
- 重构进化技能：从"检查清单"升级为"项目自循环完善"机制（望→闻→问→立意→切→搜→写→装→记→验→纠→进）
- 产出 ADR-0003：记录循环设计决策、和 GPT DR/TIDE/中医 AI/r-web-plan 的对比、立意位置、记进保留理由
- 立意置于问之后：基于观察+用户确认形成精确目标
- 分类学是进化循环的第一个承载项目

### 2026-06-11 (第四次)
- 新增 `mio-session-finder` 技能 — 从 CC 会话 JSONL 中搜索追溯信息、根因分析
- 技能统计：6 技能 + 1 数据文件

### 2026-06-11 (第三次)
- 查会话 `7ae0849d` 追溯死链接根因：方案中 `workflows/`/`tools-per-workflow/` 在建技能时被 discovery 动态搜索替代，但 routing.json 和 SKILL.md 引用未同步更新
- 修复 3 处死引用: dimension-routing.json → 路由到 scenario_template + discovery；writer SKILL.md → 引用实际存在的 methodology 文件；tools SKILL.md → MCP 配置标注为内联
- 结论: 应清理而非补建——那些"缺失"的模块已被更好的设计替代

### 2026-06-11 (第九次) — 进化循环 v2.1 重构
- 审计 spec vs 技能：发现记的执行者矛盾、流程图并行关系画错、分类学路径硬编码等问题
- 重写 `evolution-loop-spec.md` v2.1：十二步→九步流程
  1. 理解与拓展（望+闻+切合并，主动理解需求）
  2. 立意确认（反问用户确认理解，不再"提方向让用户选"）
  3. 竞争搜索（≥3 子 Agent 独立搜索，空上下文，防锚定）
  4. 比对审计（合规检查+偏离审查+方向收敛，循环到一致）
  5. 最终合规审计（收敛后的最终检查）
  6. 结果汇报（方向+理由+操作清单，附带 ADR 存档）
  7. 备份（改动前留快照）
  8. 执行（方案已有，直接执行或调 plan）
  9. 决策树（append-only+时间戳，只新增不替换）
- 核心变化：竞争搜索替代单人搜索、事中收敛替代事后打分、用户确认后主 Agent 自己完成（缓存友好）、ADR+决策树替代分散沉淀
- 产出 ADR-0004：记录重构决策及与旧版的对比
- `mio-jinhua` 技能标记为待重构（v1→v2.1）
- 设计来源新增：LLM-as-Judge、Debate-style alignment、ADR (Nygard 2011)

### 2026-06-12 — 进化循环 v3.0 融合
- 发现 `claude进化-skill.md`——独立编写的高质量进化技能，Phase 1-4 结构 + 策略标签系统 + 打回重搜 + 产出边界表
- 对比审计：claude进化-skill.md 在 9 个方面优于 spec v2.1（策略标签/收敛判定精确性/偏离打回/ADR格式/产出边界表等）
- 融合产出 `evolution-loop-spec.md` v3.0：以 claude进化-skill.md Phase 结构为主体，补入 v2.1 的设计来源、边界条件、项目接入、名词解释
- 核心机制升级：
  - 空上下文 → **策略标签驱动**（成功案例/反例/边界条件/竞品参照/第一性原理）：结构化多样性
  - "全部同一方向" → **收敛三条件**（有效方向一致 + 差异仅限实现细节 + 无互斥）
  - 偏离丢弃 → **打回重搜**（给修正指令，保留 Agent 上下文积累）
  - "多轮" → **3 轮硬上限**（满 3 轮上抛用户）
  - 产出不可变性制度化（**产出边界表**：谁写/何时/是否可修改）
  - ADR 格式补全"**放弃的方向 + 信息来源（策略标签列表）**"

### 2026-06-12 (第二次) — 技能替换
- 删除旧 `mio-jinhua` v1（十二步闭环），用 `claude进化-skill.md` 直接替换
- 旧 `docs/claude进化-skill.md` 副本删除——唯一版本在 `.claude/skills/mio-jinhua/SKILL.md`
- `mio-jinhua` 现在 = v3.0 Phase 1-4 架构 + 策略标签系统
- CONTEXT.md 移除"进行中-重构技能"，更新下一步为"跑进化验证"
