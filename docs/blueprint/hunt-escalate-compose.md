# Blueprint — Hunt → Compose 有条件升格（Fix 阶段桥）

> Move 0 增量规范：**不重写**根目录 `DESIGN.md`（全模态 hunt 真源）。本文只扩展 §6.3 Fix Gate 之外的**工程化升格路径**，与 `iterative-bug-hunter/references/fix-gate.md` 并列，不改 quiet / 指纹 / 探针算法。
>
> 状态：blueprint（未实施）· 对应对话结论：compose-next **不可**内嵌 hunt；hunt **可**在 Fix 门控后升格 compose-next。

---

## Identity

**Information Designer**（流程/系统信息设计）——首问：「读方案的人必须做出的那一次比较是什么？」  
→ **同一条 Confirmed：本地 `fix_gate` 单点修 vs 升格 `compose-next` 工程修。**

## Grounding

对话已给出充分信号（仓库 = iterative-bug-hunter 源码仓；compose-next 契约 *no internal skill hand-offs*；Fix 为可选子阶段）。采用 **Junior Designer mode**：

- **假设**：本方案只改「修复怎么工程化」，不改 hunt 主循环语义；默认路径仍是 `fix_gate.py`，compose 仅作窄口升格。
- **理由**：仓库 DESIGN 与 fix-gate.md 已把小修闭环写死；缺口只在「大修没有 Spec/Worktree/Review」。
- **刻意推迟**：具体脚本签名、`state.json` 新字段名、是否改内置 compose-next（**默认不改**）——实施阶段再定。

---

## DESIGN.md（增量 · Process Foundations）

> 视觉体系的「色票/字阶」在此映射为**流程不变量**。完整九节头保留，深度按中型流程变更缩放。

### 1. Objective

任何一次「修完」都应让读者能立刻回答：**这是不是该进 compose 的那类改动？**  
质量门：证据分层清楚、状态单写、升格可拒绝、结束必须回 hunt 做 quiet——而不是「看起来修了」。

### 2. Product Context

- **产品是什么**：`iterative-bug-hunter`——全模态迭代抓 BUG 直到约定范围内无新增确认项。
- **用户**：在本地 Web/画布项目上做 design QA / hunt-until-clean 的开发者或 agent；常在会话里连续多轮，预算敏感。
- **相邻体感**：GitHub issue → PR 模板 + CI 门禁；SWE-agent 可验证修复；本仓 `fix_gate.py` 回归矩阵。
- **遥远体感（不要像）**：把每条 overflow 都做成「迷你产品需求评审」的重型流程平台——过重、假精确。
- **语域**：技术、可判定、偏契约；不讲故事。

### 3. Process Foundations（映射 Visual Foundations）

#### 3a. 「色票」= 状态与路径契约

| Token | 值 | 用法 |
|-------|-----|------|
| hunt state root | `<target>/.bug-hunter/` | **仅** main agent 写；持 `.lock`（O_EXCL） |
| compose feature doc | `docs/compose/spec/<feature-name>.md`（或用户指定） | 升格后由 compose 拥有 |
| 默认 worktree | `.worktrees/<slug>` | 仅 compose 升格路径创建 |
| probe 指向 | base_url / build 必须指向**当前修复树** | 禁止「改了 workspace、hunt 仍扫旧主仓」 |
| hunt REPORT | `.bug-hunter/REPORT.md` | compose 交付后仍由 hunt 收口写盲区 |

#### 3b. 「字阶」= 升格判据（可陈述，禁止「感觉比较大」）

升格 compose-next **当且仅当**下列 **≥2** 条成立（且 bug 为 Confirmed、`mode=hunt-and-fix`）：

1. **跨子系统**：预计改动 ≥2 个模块/包，或动公共接口/数据契约；
2. **行为重定义**：产品期望行为本身有歧义，需先定 Design（不是「对齐既有 CSS」）；
3. **回归面宽**：`fix_gate` 的回归矩阵预计会连带多个非目标 route×viewport 的 intentional 变更，需要独立 Review；
4. **用户显式要求**工程化交付（分支、Spec、PR）。

**不升格**（走原 `fix-gate.md`）：单点 overflow / contrast / touch-target / aria 补齐 / 一文件内可完成且 acceptance 可机器复述的修复。

#### 3c. 「间距」= 证据分层与节奏

| 阶段 | 主证据 | 不得用来顶替 |
|------|--------|----------------|
| Confirm | 截图/几何 + selector + route×viewport + 机器规则 | compose 测试 PASS |
| compose Verify/Review | 测试/typecheck/diff + 独立 review 结论 | hunt quiet |
| 回到 Converge | 修复后 probe/hunt、quiet 四条件、Blind Spots | 「PR 已合」 |

节奏：**Confirm →（门控）→ compose 瘦路径 → Finalize → 回 hunt Converge → REPORT**。  
不得在 compose 中途静默改 `.bug-hunter` 状态机语义。

#### 3d. 「组件种子」= 门控动作

- **Question gate**：升格前 `question`（或 scope 预授权）；选项：单点修 / 升格 compose / 只出报告。
- **Compose slim**：机械改动 → 跳过 Grill/Spec（compose-next 自带捷径）；有设计面才 Spec。
- **fix_gate 保留**：小修仍用 `scripts/fix_gate.py`；升格修在合入前**同样**要能过目标清除 + 回归策略（可并入 compose Verify，但门禁语义不降）。
- **Budget guard**：升格计入墙钟/`max_runs`/`max_fix_failures` 预算；耗尽则停升格、只报告。

### 4. Accessibility（流程版非协商项）

- 升格必须**可拒绝**；拒绝后仍完成 hunt 报告（含该 Confirmed 与建议修复面）。
- **Blind Spots 强制**：无 dev server / 无 Playwright / axe unavailable → 禁止假装升格成功或假装 quiet。
- **单写者**：`.bug-hunter/` 在 compose 期间仍仅 main agent 持锁写；review/implement subagent **不得**写 state。
- **禁止双会话**同项目并行两场 hunt，或两场 compose 叠同一修复面。

### 5. Voice & Tone

- **语域**：契约式短句；动词+条件；少形容词。
- **用词**：Confirmed、fix_gate、quiet 四条件、Blind Spots、升格、工作区（worktree）。
- **拒绝用词**：「无缝集成」「一站式搞定」「智能修复一切」「大概没问题」。
- **称呼**：对 agent / 同行开发者用「你」；不对最终用户讲故事。

### 6. Implementation Practices

- **准据优先级**：仓库 `DESIGN.md`（hunt 算法）> `fix-gate.md`（小修门）> 本文（升格桥）> compose-next 默认契约；**项目 `AGENTS.md` / 用户明确指令**可覆盖默认工作流选择，但**不得**放宽「Confirmed 才修、状态单写、禁止静默降级」。
- **不改** 内置 `compose-next` skill 来实现反向集成；桥写在 hunt 侧 references + 项目约定。
- **落点（实施时）**：
  - `iterative-bug-hunter/SKILL.md` — Fix 步骤 2–3 句指针（触发条件 + 链到 reference）；
  - `iterative-bug-hunter/references/compose-escalate.md` — 本文操作化全文；
  - `references/fix-gate.md` — 增加「升格路径」交叉链接一行；
  - 可选：项目 `AGENTS.md` snippet（**只生成 snippet，不自动改写用户 AGENTS.md**——遵守 skill 禁止项）。
- **state 字段（实施时再定名）**：`escalations[]` 至少含 bug_id、feature_doc、branch、workspace_path、base_url_override、outcome（delivered|rejected|failed）、returned_to_hunt_at。
- **安装**：改 skill 后需**新开对话**才重载；源仓 `iterative-bug-hunter/` 为真源，复制到 `~/.config/mimocode/skills/` 或项目 `.mimocode/skills/`。

### 7. Anti-Patterns（本方案特有拒绝）

- **No「每条 Confirmed 都走 compose」。** 会把 design QA 变成流程税，且与 fix_gate 重复。
- **No compose-next 内部再 load hunt。** 违反 *no internal skill hand-offs*；反向集成是 hunt 的 Fix 出口，不是 compose 插件。
- **No Review subagent 自写 `.bug-hunter/state.json`。** 破坏单写者与锁协议。
- **No「compose Verify PASS = hunt 收敛」。** 证据层不同；必须回到 Converge。
- **No 空话验收**（「已优化流程」「加强了质量」）。验收必须是命令、指纹、REPORT 字段。
- **No 未批准页面截图当 bug / 纯审美 Confirmed**（继承主 DESIGN，升格不放宽）。

### 8. Decision-Making（冲突时的优先级）

1. **用户明确指令 / 硬约束** — 毁灭性操作、双会话冲突时选非毁灭、可恢复路径。
2. **Confirmed + 机器证据** — 无 Confirmed 不修；升格不降低 Confirm 门。
3. **状态与并发契约** — 锁、单写者、禁止双会话 > 流程便利。
4. **证据分层** — quiet 以 hunt Converge 为准；compose 产物只作实现证据。
5. **成本与默认路径** — 能 `fix_gate` 不升格；升格必须 slim。
6. **可解释性** — 判据可陈述；不可陈述 → 不升格、进 Deferred/报告。

### 9. Workflow（agent 执行序）

1. 按主 SKILL 完成 Bootstrap→…→**Confirm**；`mode` 非 hunt-and-fix 或 degrade 过低时**不进入**修复/升格。
2. 对每条 Confirmed：用 §3b 判据判定 **local fix** 还是 **escalate**。
3. local → `fix-gate.md`：一次一修 → `fix_gate.py` → 失败回滚记 `fix-failed`。
4. escalate → 若 scope 无预授权则 `question`；通过后 **load `compose-next`**，在 slim/worktree 约定下修该 bug（Spec 名可 `fix-<bug-id>`）。
5. compose Verify + Review 按其契约执行；**不**把 `.bug-hunter` 交给 subagent 写。
6. Finalize 后：**回 hunt** — 用与修复树一致的 base_url 重跑相关 probe/`hunt_round`，更新指纹与 Confirmed→Fixed。
7. `converge_check` / quiet 四条件；写 `REPORT.md`（已扫面、degrade、Blind Spots、升格清单与 outcome）。
8. 用户关闭动作（merge/PR/保留分支）**不自动做**；报告 branch/base/head/workspace/feature-doc 路径后由用户决定。

---

## Structure（本优化方案的结构描述）

非视觉工件；按**读者执行路径**组织，而非页面层级。

### A. 问题切片

| # | 问题 | 方案回应 |
|---|------|----------|
| P1 | compose-next 默认禁止内嵌 skill hand-off | 不把 hunt 塞进 Verify；改反向、窄口升格 |
| P2 | 大修缺 Spec/Worktree/Review | Fix 阶段条件升格 compose-next |
| P3 | 小修被流程税压死 | 默认 `fix_gate`；判据 ≥2 才升格 |
| P4 | 双流程「谁算修完」 | 证据分层；终点仍是 hunt quiet |
| P5 | 并发与状态 | 单写者保留；compose 不写 `.bug-hunter` |

### B. 控制流（升格支）

```
Confirm(Confirmed)
    │
    ├─ 判据不足 ──► fix_gate（一次一修）──► 复测 ──► 下一条 / Converge
    │
    └─ 判据满足且已门控 ──► load compose-next（slim）
                              │
                              ├─ Workspace (+ worktree)
                              ├─ Spec（仅当有设计面）
                              ├─ Implement / Verify / Review
                              └─ Finalize
                                    │
                                    ▼
                              回 hunt：指向修复树的 Capture/Probe
                                    │
                                    ▼
                              Converge + REPORT（含 escalation 结果）
```

### C. 交付物（实施后应存在的东西）

1. `references/compose-escalate.md` — 判据、门控、状态字段、回 hunt 协议  
2. `SKILL.md` Fix 步骤短指针  
3. `fix-gate.md` 一行交叉链接  
4. 可选 AGENTS snippet（非自动安装）  
5. 验收：单测/fixture 证明「不升格路径」不被改坏；人工或第二会话演练 1 次升格 + 回 Converge  
6. `docs/compose/spec/<name>.md` — **若**用 compose-next 实施本方案本身，再开正式 feature 文档（本 blueprint 不是 Spec 替代品）

### D. 非目标（Out of scope）

- 修改 compose-next 内置 skill 正文以支持「自动调用 hunt」  
- 自动 PR/merge  
- 升级 quiet 算法、指纹算法、VLM 确认门  
- 把本方案写成「所有 UI compose 任务必须 hunt」的反向强制  

### E. 验收契约（将来 Verify 用）

| ID | 验收项 | 观察结果 |
|----|--------|----------|
| A1 | 判据可执行 | 文档中 local vs escalate 可对照 Confirmed 样例复述 |
| A2 | 无预授权不升格 | agent 在缺授权时走 question 或 local，而非静默 load compose |
| A3 | 状态单写 | compose 过程中 state 仅 main 持锁变更 |
| A4 | 回 hunt 强制 | 升格交付后存在复测记录或明确 Blind Spot，不只有 compose Report |
| A5 | 小修不回归 | 原 `fix_gate` 路径行为与门禁语义不变 |
| A6 | 可拒绝 | 用户拒绝升格后仍产出含该 Confirmed 的 REPORT |

---

## Decision Trace

```json
[
  {
    "decision": "反向集成：hunt 的 Fix 门控后升格 compose-next，而不是 compose 内嵌 hunt",
    "reason": "compose-next 明文 no internal skill hand-offs；hunt 的 Fix 本就是可选出口，主状态机仍在 .bug-hunter",
    "alternatives": ["compose Verify 强制跑 hunt_round", "改写内置 compose-next 支持插件", "完全禁止两技能同项目出现"],
    "tradeoff": "compose 流程内的 UI 任务仍不会自动获得全模态视觉门禁，需另开 hunt 或项目 AGENTS 另约定"
  },
  {
    "decision": "升格判据：Confirmed + 机器可陈述条件中 ≥2 条，而非「实现者觉得复杂」",
    "reason": "仓库 DESIGN 强调可判定；无阈值会把每条视觉修复都拖进 Grill/Spec",
    "alternatives": ["仅按 severity=high", "任何多文件 diff 都升格", "全部 Confirmed 升格"],
    "tradeoff": "边界案例（单模块但行为歧义）可能仍需 agent 判断，文档需允许 question 兜底"
  },
  {
    "decision": "默认路径保持 fix_gate.py，compose 只作窄口",
    "reason": "与现有 fix-gate.md、一次一修、max_fix_failures 护栏连续，避免小修流程税",
    "alternatives": ["Fix 一律 compose", "废弃 fix_gate 只留 compose"],
    "tradeoff": "团队若希望「所有修复都有 PR 模板」会感到默认偏轻，需在 scope 预授权里拉高升格率"
  },
  {
    "decision": "compose 走 slim：机械修跳过 Grill/Spec，有设计面才 Spec",
    "reason": "compose-next 自带该捷径；升格若强制全阶段会与 hunt 预算护栏冲突",
    "alternatives": ["升格必全量九阶段", "升格永远不开 worktree"],
    "tradeoff": "无 Spec 的大修可追溯性下降，依赖 REPORT escalation 字段补叙事"
  },
  {
    "decision": "终点仍是 hunt Converge + REPORT；compose Finalize 不算收敛",
    "reason": "quiet 四条件与 Blind Spots 是本 skill 用户合同；测试绿 ≠ 视觉面无新增确认项",
    "alternatives": ["compose Review PASS 即结束 hunt", "双报告互相引用即可免复测"],
    "tradeoff": "升格单交付成本更高；无浏览器时只能以 Blind Spots 收口，体验上像「没验完」"
  },
  {
    "decision": "不修改内置 compose-next；桥落在 hunt references + 可选 AGENTS snippet",
    "reason": "内置 skill 升级会漂移、多项目互相覆盖；且 skill 禁止自动改写用户 AGENTS.md",
    "alternatives": ["fork compose-next", "把判据写进全局 AGENTS 并自动安装"],
    "tradeoff": "跨项目复用要靠复制 snippet 或再装项目级 skill，不能「改一处全局生效」"
  },
  {
    "decision": "probe/base_url 必须与修复树一致（worktree override 写入 escalation 状态）",
    "reason": "常见失效是改了 workspace 仍扫旧主仓，出现假 quiet 或假回归",
    "alternatives": ["始终用主仓端口", "升格时暂停 hunt 复测"],
    "tradeoff": "升格步骤多一步环境对齐；隔离会话禁 git worktree 时需记录 override（参见既往 skill-config-opt journey）"
  },
  {
    "decision": "本文件落 docs/blueprint/，不覆盖根 DESIGN.md，也不冒充 docs/compose/spec 已交付 feature",
    "reason": "Move 0：既有 DESIGN 为 taste；blueprint ≠ compose Spec；避免双真源",
    "alternatives": ["直接改 DESIGN.md §6.3", "写成 status=delivered 的 compose spec"],
    "tradeoff": "实施前 repo 里只有设计意图，没有合规 feature 文档；实施 compose 流程时还要再写 Spec"
  }
]
```

---

## Anti-slop self-check

**flagged 并已纠正：**

| 模式 | 原风险写法 | 纠正 |
|------|------------|------|
| U7 空话 | 「实现技能深度协同，提升修复质量」 | 改为可陈述判据、状态 token、验收 ID A1–A6 |
| 流程 slop：一律重型 | 「Confirmed 均可走 compose-next」 | 默认 fix_gate；≥2 判据 + 门控 |
| 伪精确 | 「升格后效率提升约 40%」 | 不写虚构指标；成本以墙钟/预算护栏表达 |
| 反向插件叙事 | 「在 compose Verify 自动调用 hunt」 | 明确 Out of scope，遵守 no internal hand-offs |
| 空组件列表 | 只写「加强 Fix 阶段」 | 落到 SKILL 指针 / compose-escalate.md / fix-gate 交叉链 / escalation 状态字段 |

**通用 U1–U6、U8**：本文为流程规格，无渐变英雄区、卡片网格、emoji 标题、等距插画、假数据三连、全按钮化 CTA；正文避免 em-dash 堆叠作为文风装饰。

**结论：clean（经上表纠正后）。**

---

## 附录 — 与既有文档的关系

| 文档 | 关系 |
|------|------|
| `/DESIGN.md` | Taste 真源；本文不改 §1–§5 算法与 taxonomy |
| `iterative-bug-hunter/references/fix-gate.md` | 小修门禁保持；实施时加一行「升格见 compose-escalate.md」 |
| `docs/compose/spec/*.md` | 历史 compose 交付记录；**实施本方案时**应新建 spec，不把 blueprint 当 delivered |
| compose-next skill | 只作为被**有条件加载**的目标流程，不在其内部写 hunt |

---

*Blueprint only — 未改 skill 源码、未改 AGENTS、未创建 compose feature 文档。*
