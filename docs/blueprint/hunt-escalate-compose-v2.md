# Blueprint v2 — Hunt → Fix 路由优化（文献研判版）

> **Move 0**：Taste 层 = 仓库根 `DESIGN.md` + `docs/blueprint/hunt-escalate-compose.md`（v1）。本文是 **v2 研判增量**，不重写 hunt 算法；对 v1 的升格路径做证据驱动修正。
>
> **检索说明**：本会话 WebSearch 插件不可用；权威来源经 arXiv abs/html 抓取。GitHub 网页本轮 transport 失败，星标与仓库定位引自仓内 `DESIGN.md` §2 调研表及论文正文开源链接（不虚构未抓取页面数据）。
>
> **结论一句话**：v1「本地 fix_gate vs compose-next 二分」方向正确但**过粗**；文献支持 **三档路由 + 预算递减 + 结构化交接包 + 可机器判定的升格门**，默认路径应比 v1 **更偏简单流水线**，compose-next 仅保留给「oracle/设计契约缺口」。

---

## Identity

**Information Designer**（流程信息设计）——首问：「读者必须立刻做出的比较是什么？」  
→ **三档：Local Pipeline · Escalate-Lite · Compose-Next**——不是「修不修」，而是「用哪一级修复基础设施」。

## Grounding

**Branch A — 信号充分**（v1 方案 + 仓内 DESIGN 文献表 + 本轮 arXiv 抓取）。

- **假设**：默认修复路径应向 Agentless 式「定位 → 多候选 → 验证」靠拢；compose-next 是**例外升格**，不是第二默认。
- **理由**：Agentless / AutoCodeRover / Art of Repair 显示：简单、可解释流水线在真实 issue 上可超过重 agent，且成本更低、迭代有收益递减。
- **刻意推迟**：`state.json` 最终字段名、脚本 CLI、是否引入本地多候选采样脚本——实施 Spec 再定。

---

## 文献与仓库研判矩阵

| 来源 | 对本方案的核心证据 | 对 v1 的含义 |
|------|-------------------|--------------|
| **Agentless** arXiv:2407.01489（OpenCoder，论文称 OpenAI 用于 GPT-4o/o1 演示；SWE-bench Lite 开源侧 32%、约 $0.70） | 三阶段：层级定位 → 多候选 patch → 复现测试选优；**不**让 LLM 自主决定下一步复杂工具动作 | 升格前应有 **流水线中间档**；复杂 agent 不是修复的默认形态 |
| **SWE-agent** arXiv:2405.15793 | ACI（代理-计算机接口）设计显著影响表现；定制动作面 > 堆模型 | 升格进 compose 时交接面要 **固定**（bug packet 字段），避免自由发挥 |
| **AutoCodeRover** arXiv:2404.05427（ISSTA’24；Lite ~19%，均成本 ~$0.43） | 程序结构（AST/类方法）+ 测试谱系故障定位优于「把仓库当文件堆」 | Local/Lite 档应先 **结构化定位** 再改，禁止从截图直接猜改哪个组件 |
| **SWE-bench** arXiv:2310.06770（ICLR’24） | 真实 GitHub issue 常跨多函数/类/文件；需要可验证 oracle | 「跨子系统」判据要落到 **多编辑点 + 可执行验收**，不是「感觉文件多」 |
| **Trident / Seeing is Believing** arXiv:2407.03037 | 非 crash 视觉/功能 bug：Explorer/Monitor/Detector 角色分离；oracle 常依赖 **页面序列** | 交接与复测要带 route×viewport **序列/流**，禁止只附一张主路径截图 |
| **kAgent** arXiv:2504.20412（ICML’26 workshop 线） | 开发者启发式工作流：执行日志 → 假设 → 候选补丁 → **复现验证** → 迭代 | 升格前强制「执行落地的失败记录」；compose Verify 必须含复现，不只单元绿 |
| **The Art of Repair** arXiv:2505.02931（EASE’25） | 迭代修复优于一次多产出；超过阈值 **收益递减**；复杂基准更吃迭代；预算（如 ≤10 patch/bug） | 本地重试次数与升格次数要有 **硬预算**；两次失败应换策略或升格，禁止同构重试 |
| **MetaGPT** arXiv:2308.00352 | SOP 编码进多角色流水线，中间产物校验抑制级联幻觉 | 交接包 = SOP：结构化字段，禁止纯叙述「帮我修一下 UI」 |
| **MINT** arXiv:2309.10691（ICLR’24） | 多轮 + 工具 + 自然语言反馈有增益；**单轮强 ≠ 多轮强** | 升格质量不能用「hunt 一轮 Confirmed 多」代理；要单独记 escalate 后回归 |
| **LLM Multi-Agents Survey** arXiv:2402.01680 | 多 agent 通信/角色/容量机制有收益，也有协调与幻觉风险 | **拒绝** hunt 与 compose 并行互嵌的「agent 社会」；保持串行门控交接 |
| **More Agents Is All You Need** arXiv:2402.05120（TMLR） | 采样-投票可随 agent 数扩展，且与复杂方法正交 | 仅在 **Local/Lite 候选选优** 可借鉴投票；不靠再加一层技能编排 |
| **ICL for Code** arXiv:2304.07575（ASE’23） | 示例的选择/顺序/数量强烈影响代码任务 ICL | `compose-escalate.md` 必须带 **正反 worked examples**，不能只有规则条文 |
| **仓内 DESIGN 已引** Specula / Agora / SmellBench / WebTestPilot / ConVerTest 等 | 先规格后检验；Detect/Confirm 分角；视觉 FP 可很高；元素级 oracle | Confirm 门不降级；升格 **不能**把 Candidate/Deferred 带进 compose |
| **高星仓（DESIGN §2 + 论文链接）** Playwright 96k+、axe-core 7.5k+、SWE-agent 20k+、OpenHands 88k+、MetaGPT、Agentless、Aider（Agentless 文中：repo map + diff + 回归）、jest-image-snapshot / loki 等 | 生态分裂为：**PR 管道**（Aider/Agentless）vs **重 agent**（OpenHands/SWE-agent） | 产品默认应对齐前者；compose-next 对齐后者的「工程交付」少数场景 |

---

## DESIGN.md（v2 增量 · 对 v1 的修订）

> 九节头保留；只写 **相对 v1 变了什么** 及仍成立的不变量。

### 1. Objective（微调）

任何 Confirmed 修复都要可路由到：**Local Pipeline**（默认）· **Escalate-Lite**（结构化补强）· **Compose-Next**（设计/契约级）。  
读者决策问题从「要不要 compose」改为「**oracle 与改动结构落在哪一档**」。

### 2. Product Context（补）

生态锚点：对齐 **Agentless / Aider / AutoCodeRover** 的可验证管道气质；**不要像** Devin 式「每条 bug 都端到端自治 agent」。compose-next 仅在需要 durable Spec + 独立 Review + worktree 交付时出现。

### 3. Process Foundations（关键修订）

#### 3a. 路径与状态（v1 保留，补交接 token）

| Token | 值 | v2 用法 |
|-------|-----|---------|
| hunt state | `<target>/.bug-hunter/` | 单写者 + 锁（不变） |
| **bug packet** | `.bug-hunter/bugs/<id>/packet.md` 或 JSON | 升格/Lite 交接的 **SOP 包**（见 Structure） |
| escalate-lite 工作区 | 默认主 checkout / 当前分支（无 worktree） | 中间档 **不**强制 worktree |
| compose workspace | `.worktrees/<slug>`（或用户指定） | 仅 Compose-Next |
| probe 指向 | 必须 = 当前修复树 base_url | 不变；packet 中必填 `serving_tree` |

#### 3b. 升格判据（替换 v1「≥2 条模糊条件」）

**前置（全部）**：`mode=hunt-and-fix` · 状态 ∈ {Confirmed} · degrade 支持复测（或明确 Blind Spot 策略）· 本地预算未耗尽且未锁定为 report-only。

**档位选择（按序判定，先命中先走）：**

| 档 | 命中条件（机器/可陈述） | 动作 |
|----|-------------------------|------|
| **L — Local Pipeline** | 预计编辑点可层级定位到 ≤N 处（默认 N=3）且同属既有契约；验收 = **同 rule_id @ route×viewport 不再命中** + 回归矩阵零新增；无行为歧义 | `fix-gate.md`：定位 →（可选）1–3 候选补丁 → 复现 probe → `fix_gate.py` |
| **Lite — Escalate-Lite** | Local 验收 **oracle 可写但一次未过**，或编辑点 4–6 / 跨包但仍沿既有契约，或需要 **独立复盘假设**（kAgent 式）却尚不需产品 Spec | 不 load compose-next：主 agent 写 packet → 重定位（AutoCodeRover 式结构/测试线索）→ 最多 `lite_max_attempts`（默认 2）→ 仍过 `fix_gate.py` |
| **C — Compose-Next** | **Oracle 缺口**：无法写出机器可判定的「修好了」；或 **契约重定义**：期望行为本身需产品/设计决策；或 **回归面** 将系统性改非目标 intentional 语义且需独立 Review+Spec；或用户明确要求 PR/Spec 交付 | 门控 `question`/预授权 → load compose-next（**slim**：无设计面跳 Grill/Spec）→ Finalize 后 **强制回 hunt Converge** |

**明确不升到 C（仍 L 或 Lite）**：单点 overflow/contrast/touch-target/aria；已有明确 selector+数值规则可验收的项。

**预算与递减（Art of Repair）：**

| 参数 | 默认 | 含义 |
|------|------|------|
| `max_local_attempts` / bug | 3 | Local 候选修复尝试上限 |
| `lite_max_attempts` / bug | 2 | Lite 结构化重试上限 |
| `max_compose_escalations` / hunt session | 2 | 一次 hunt 会话内 compose 升格上限 |
| 同构重试 | 禁止 | 两次失败后必须：重定位 / 换 oracle / 降级报告 / 升档——不得复制同一 diff 策略 |
| 收益递减 | 同 bug 连续修复失败 ≥2 | 记 `diminishing=true`，REPORT 强制可见 |

#### 3c. 证据分层（v1 保留，补序列 oracle）

- Confirm：机器规则 + **可复现步骤**（Trident：尽量 route×序列，不只单帧）。
- Local/Lite Verify：`fix_gate` 四检查（目标清除 / 零新增 layout / pixel gate / 可选 unit_green）。
- Compose Verify/Review：测试与独立 review；**不得**代替 quiet。
- Converge：以 hunt 复测为准；packet 与 REPORT 双记录 outcome。

#### 3d. 组件（替换/增加）

- **默认 Local**，Lite 仅在 oracle 仍在且需重定位/二次候选时；**C 最窄**。
- **Bug Packet SOP**（MetaGPT/SWE-agent ACI）：见 Structure；compose 入口只接受 packet，不接受口头「有个视觉 bug」。
- **候选与选优**：Local/Lite 可对同一 Confirmed 生成 ≤3 补丁，用复现 probe + 回归选优（Agentless/More-Agents 采样思想的 **轻量**落地）；禁止无验证的「感觉更好的 patch」。
- **角色分离（轻）**：Detect/Confirm 已在 hunt；Compose Review = Monitor；**禁止** Review subagent 写 `.bug-hunter` state。

### 4. 非协商项（不变 + 强化）

- Candidate/Deferred **永不**自动进 C。  
- axe unavailable / 探测失败 → Blind Spots，禁止假 quiet、假升格成功。  
- 单写者、禁双会话、禁 compose 内嵌 hunt。  
- 升格可拒绝；拒绝后仍出 REPORT。

### 5. Voice

契约短句；拒绝「无缝 / 智能升格一切 / 多 agent 协同搞定」；用词增加：`bug packet`、`oracle gap`、`local pipeline`、`escalate-lite`、`diminishing`、`serving_tree`。

### 6. Implementation Practices（落点）

| 产物 | 动作 |
|------|------|
| `iterative-bug-hunter/references/compose-escalate.md` | 以本文 v2 替代 v1 操作化：三档树、预算、packet schema、正反例（ICL） |
| `references/fix-gate.md` | 保留 Local 门禁；增加「失败→Lite/C 分流」与 packet 指针 |
| `SKILL.md` Fix 段 | 3–5 句：三档路由 + 链 compose-escalate.md；**不**把 DESIGN 全文塞入 |
| 可选 AGENTS snippet | 只生成不自动改写 |
| 实施文档 | 若走 compose-next 落地本方案，另开 `docs/compose/spec/<name>.md`（本文仍是 blueprint） |

**准据**：仓库 DESIGN（quiet/指纹/Confirm）> fix-gate（Local 门）> 本文 v2（路由）> compose-next 默认契约；用户指令可选流程，**不可**放宽 Confirm/单写者。

### 7. Anti-Patterns（文献驱动）

- **No「Confirmed 全走 compose」**（Agentless/成本证据）。  
- **No「复杂度偏见」**：以「更重的流程」代替「更好的 oracle」。  
- **No 单帧视觉验收**（Trident：序列/状态机）。  
- **No 同构无限重试**（Art of Repair 递减）。  
- **No 叙述式交接**（MetaGPT SOP / SWE-agent ACI）。  
- **No 多技能并行互嵌**（Multi-agent survey 幻觉与协调成本）。  
- **No 空指标**（「质量提升 x%」无基线则不写）。

### 8. Decision-Making（优先级，v2）

1. 用户指令与可恢复性  
2. Confirmed + 机器 oracle（无 oracle → C 或 Deferred，**禁止**假修）  
3. 状态单写 / 并发  
4. **档位成本递增原则**：能 L 不 Lite，能 Lite 不 C  
5. 证据分层：Converge 最终裁定「修完」  
6. 预算与递减护栏  
7. 可解释：判据可陈述，否则降档报告  

### 9. Workflow（v2 执行序）

1. Hunt…→ Confirm。  
2. 对每条 Confirmed 跑 **三档判定**（3b），写入 state `route: local|lite|compose` + 理由码（`oracle_ok` / `needs_relocalize` / `oracle_gap` / `contract_change` / `user_pr`…）。  
3. **Local**：结构化定位 → ≤3 候选 → 复现 → `fix_gate.py` → 失败记 attempt；达上限改 Lite 或 C（若 oracle_gap/contract）否则 Deferred+报告。  
4. **Lite**：生成/更新 bug packet → 重定位 → ≤2 次 → 仍 `fix_gate.py`；失败且判 C 条件 → 门控升 C；否则 Deferred。  
5. **C**：门控 → load compose-next（slim）→ 仅消费 packet → Verify/Review 按 compose → Finalize。  
6. **回 hunt**：`serving_tree` 对齐后的 Capture/Probe/Hunt → Converge → REPORT（含 route 理由、budget、Blind Spots、escalations）。  
7. 关闭动作（merge/PR/删 worktree）不自动；报告路径与 SHA。

---

## Structure（研判后的方案结构）

### 控制流

```
Confirm
   │
   ├─ oracle 可判定 + 编辑点小 ──► L Local Pipeline
   │         │ success → 继续 hunt / Converge
   │         └ fail×预算 ──► Lite 或 Deferred
   │
   ├─ oracle 在但需重定位/二次结构化 ──► Lite Escalate-Lite
   │         │ success → fix_gate → hunt
   │         └ fail + oracle_gap/contract ──► C（门控）
   │
   └─ oracle gap / 契约重定义 / 用户要 PR ──► C Compose-Next (slim)
             └ Finalize → 回 hunt Converge
```

### Bug Packet（交接 SOP，最小字段）

```yaml
bug_id: bug-0001
fingerprint: "..."
status_at_handoff: confirmed
route: local|lite|compose   # 命中档
reason_codes: [oracle_ok, multi_edit]
modality: web-visual
category: ui-layout
location:
  surface: web
  routes: ["/login"]
  viewports: ["375x812"]
  selectors: ["[data-testid=submit]"]
  bbox: {x: 340, y: 620, w: 120, h: 48}
repro:
  steps: ["打开 /login", "375x812", "观察主按钮右缘"]
  sequence_routes: ["/", "/login"]   # Trident：尽量序列
oracle:
  type: rule+geometry   # rule+geometry | contrast-wcag | axe-id | ...
  rule_id: overflow-x
  pass_condition: "同 rule_id 在同 route×viewport 不再命中"
  regression_matrix: "all_scanned_cells_zero_new"
attempts:
  local: 1
  lite: 0
  last_fix_gate: {result: fail, file: runs/run-N/fix-verify.json}
serving_tree: "path-or-worktree"   # probe 必须对齐
base_url: "http://127.0.0.1:5173"
budget: {max_local: 3, max_lite: 2, diminishing: false}
deferred_notes: null
```

### 与 v1 差异一览

| 项 | v1 | v2 |
|----|----|----|
| 路由 | 二分：fix_gate vs compose | **三档** + Lite |
| 判据 | 模糊 ≥2 条 | **oracle 前置** + 结构/契约/预算编码 |
| 交接 | 叙述 + escalation 字段 | **Bug Packet SOP** |
| 预算 | 计入墙钟 | **每 bug / 每 session 参数 + 禁止同构重试** |
| 视觉验收 | route×viewport | **+ 序列/流** 可选但推荐 |
| 默认气质 | 已偏本地 | **更偏 Agentless 管道**；C 更窄 |
| 文档 | 无强制示例 | **强制正反 worked examples**（ICL） |

### 非目标（不变）

- 改内置 compose-next 以自动调用 hunt  
- 自动 PR/merge  
- 改 quiet/指纹/Confirm 门  
- 强制所有 UI compose 任务必须 hunt  
- 把 Multi-agent「社会」写进生产路径  

### 验收契约（实施后 Verify）

| ID | 项 | 观察 |
|----|----|------|
| R1 | 三档判定可复述 | 样例 Confirmed 能说出 route + reason_codes |
| R2 | 默认不升 C | 无 oracle_gap/contract/user_pr 时 agent 不 load compose-next |
| R3 | Packet 必填 | 升 C/Lite 交接含 serving_tree 与 oracle.pass_condition |
| R4 | 预算护栏 | 同 bug 第 2 次 Local 失败后不出现同构第 3 次尝试 |
| R5 | 回 hunt 强制 | C 结束后有复测或 Blind Spot，而非仅 compose Report |
| R6 | Local 门不降 | `fix_gate` 检查语义与 v1/现网一致 |
| R7 | 可拒绝 | 用户拒 C 后 REPORT 仍含该 Confirmed |

---

## Decision Trace（v2）

```json
[
  {
    "decision": "在 v1 二分之上插入 Escalate-Lite 中间档",
    "reason": "Agentless/AutoCodeRover 表明定位+多候选+复现验证可在无 compose 工程流程下修复相当多真实缺陷；二分迫使中等问题过早进重流程",
    "alternatives": ["维持 v1 二分", "取消 Local 全走 compose", "取消 compose 只留 fix_gate"],
    "tradeoff": "路由状态与文档变复杂；agent 误判档位的概率上升，需 reason_codes 与示例压住"
  },
  {
    "decision": "升格 C 以 oracle gap / 契约重定义为主门，而非「≥2 模糊条件」",
    "reason": "SWE-bench/Agentless 强调可验证 oracle；无机器「修好了」时 compose Spec/Review 才有独特价值",
    "alternatives": ["v1 的跨子系统+回归面 ≥2", "仅 severity=high", "仅用户要求"],
    "tradeoff": "纯多文件但 oracle 清晰的改动可能停在 Lite，缺少独立 Review——用 max_compose_escalations 外的 user_pr 覆盖"
  },
  {
    "decision": "默认路径进一步偏向 Local Pipeline（Agentless 气质）",
    "reason": "论文与高星生态显示简单管道性能/成本占优；复杂 agent 有工具误用、决策失控、自反不足等问题（Agentless §1）",
    "alternatives": ["每条 Confirmed 进 compose", "hunt 与 compose 并行"],
    "tradeoff": "设计债与跨模块重构发现更慢；依赖 Confirm 是否把 oracle_gap 类问题标出来"
  },
  {
    "decision": "引入 Bug Packet 作为唯一升档交接物",
    "reason": "MetaGPT SOP 与 SWE-agent ACI：固定接口降低级联幻觉与口头交接损耗；MINT 提示多轮反馈需要稳定工件",
    "alternatives": ["自由文本给 compose", "只传 fingerprint", "会话记忆不落盘"],
    "tradeoff": "多一次落盘成本；packet 字段错误会污染下游——需 schema 必填与 validate"
  },
  {
    "decision": "硬预算 + 禁止同构重试 + diminishing 标记",
    "reason": "The Art of Repair：迭代有益但超过阈值收益递减；无预算时 agent 易在同一 diff 策略上空转",
    "alternatives": ["无限重试直到 quiet", "仅全局墙钟", "失败即永久 Deferred"],
    "tradeoff": "可能过早放弃可修 bug；用 reason_codes + 用户可调预算缓解"
  },
  {
    "decision": "视觉复测强调页面序列 oracle（Trident），单帧仅作最低证据",
    "reason": "非 crash 功能/布局问题常跨页转移才暴露；单帧不足以作 Compose/Local 的通过证据",
    "alternatives": ["仅 route×viewport 单帧", "强制全流程 E2E 录像"],
    "tradeoff": "采集成本上升；degrade=L1/L2 时序列可能不可得→必须记 Blind Spots"
  },
  {
    "decision": "Local/Lite 允许 ≤3 候选补丁用复现 probe 选优",
    "reason": "Agentless 多候选+复现选择；More Agents 采样-投票与复杂编排正交且轻量",
    "alternatives": ["永远单补丁", "引入完整 agent 投票子系统"],
    "tradeoff": "修复耗时增加；仅在第一次失败或 oracle 脆弱时默认多候选更划算"
  },
  {
    "decision": "拒绝 hunt↔compose 并行互嵌，保持串行门控",
    "reason": "Multi-agent survey 与 MetaGPT 指出朴素链式多 LLM 级联幻觉；compose-next 亦禁内部 skill hand-off",
    "alternatives": ["双技能并行 agent 社会", "compose Verify 自动 spawn hunt"],
    "tradeoff": "端到端墙钟更长；换来状态单写与证据分层可审计"
  },
  {
    "decision": "escalate 参考文档强制正反 worked examples",
    "reason": "ICL 研究：示例选择/顺序/数量强烈影响代码任务行为；纯规则条文在 agent 上执行漂移大",
    "alternatives": ["只有规则表", "示例放 DESIGN 不放 references"],
    "tradeoff": "文档更长；错例若质量差会教坏 agent——示例须与判据同源"
  },
  {
    "decision": "GitHub 星标与仓库事实以仓内 DESIGN §2 + 论文链接为准，不编造本轮未打开的页面数据",
    "reason": "本轮 webfetch GitHub 传输失败；蓝图需可审计来源",
    "alternatives": ["凭记忆填 2026 星标", "忽略仓库证据只写论文"],
    "tradeoff": "星标可能过时；实施前应用 webfetch 复核一次 OpenHands/Agentless/SWE-agent 页面"
  },
  {
    "decision": "本文件落 docs/blueprint/hunt-escalate-compose-v2.md，不覆盖 v1 与根 DESIGN",
    "reason": "Move 0 复用 Taste；v1 保留可 diff；实施前双真源风险靠「v2 为准」标注约束",
    "alternatives": ["直接改写 v1", "改根 DESIGN §6.3"],
    "tradeoff": "目录多一份文档；实施 compose Spec 时必须引用 v2 而非 v1"
  }
]
```

---

## Anti-slop self-check

**flagged 并纠正：**

| 模式 | 风险写法 | 纠正 |
|------|----------|------|
| U7 空话 | 「结合前沿论文全面增强修复能力」 | 每条修订绑定具体论文结论与参数 |
| 流程 slop：堆 agent | 「引入多 agent 投票平台」 | 仅 Local ≤3 候选 + 复现选优；拒绝并行技能社会 |
| 伪精确 | 「修复成功率提升 40%」 | 不写无基线比例；预算与 reason_codes 可审计 |
| 二分简化惯性 | 维持 v1 两档并润色措辞 | 明确插入 Lite，给出判据与预算 |
| 无来源星标 | 随手写 GitHub stars | 引 DESIGN §2 + 论文；标明本轮 GitHub 页失败 |

**通用 U1–U6、U8**：流程规格，无渐变英雄/卡片网格/emoji 标题/假数据三连；正文避免 em-dash 装饰堆叠。

**结论：clean（纠正后）。**

---

## 实施优先级（供下一跳，不在本轮改 skill）

1. **P0** 按 v2 写 `references/compose-escalate.md` + SKILL Fix 短指针 + fix-gate 分流一句。  
2. **P1** Bug packet schema + 与 `export_report`/state 字段对齐；正反示例各 ≥2。  
3. **P2** 预算参数进 `state`（可被 scope 覆盖）；REPORT 增加 route 理由码与 diminishing。  
4. **P3** 有 dev server 时补「序列复测」采集约定；无浏览器降级写 Blind Spots。  
5. **P4** 用 compose-next 正式 Spec 落地本 skill 变更（blueprint ≠ delivered）。

---

*v2 research blueprint — 未修改 skill 源码、未改 AGENTS、未覆盖 v1/DESIGN。*  
*主参考：arXiv 2407.01489, 2405.15793, 2404.05427, 2310.06770, 2407.03037, 2504.20412, 2505.02931, 2308.00352, 2309.10691, 2402.01680, 2402.05120, 2304.07575 + 仓内 DESIGN.md §2。*
