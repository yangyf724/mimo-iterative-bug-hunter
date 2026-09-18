---
feature: hunt-fix-router
status: delivered
updated: 2026-09-18
branch: feat/hunt-fix-router
commits: 2b705c0..3b07747
---

# Hunt Fix Router (compose-escalate v2)

## Report

**What was built** — 为 `iterative-bug-hunter` Fix 阶段落地三档修复路由（`local` / `lite` / `compose`）：新增 `references/compose-escalate.md`（判据、预算、bug packet、正反例、禁止项）；`SKILL.md` / `fix-gate.md` 挂接分流与指针；`init_state.py` 默认写入 `budget.max_local_attempts` / `lite_max_attempts` / `max_compose_escalations` / 编辑点上限与 `fix_router`；`export_report.py` 可选透出 bug 级 `fix_route` / `fix_reason_codes` / `fix_attempts`（含嵌套 `diminishing`）/ `packet_path` 与顶层 `fix_router` / `budget`；REPORT 模板与 export-schema 同步。`fix_gate.py` 与 quiet/Confirm/指纹算法未改。独立 review AC1–8 全 PASS、无 critical。

### Verify

- `$env:MIMO_PYTHON -m unittest discover -s tests -v` → **PASS**，`Ran 109 tests OK`。
- 导出校验：`validate_export` 仍只要求旧顶层字段；`schema_version=1`；新字段 optional。`test_phase3_scripts.py` 覆盖 slim_bug 透出 `fix_route`/`fix_reason_codes`/`fix_attempts`/`packet_path` 与顶层 `fix_router`/`budget`。
- `init_state` DEFAULT_STATE / `resume_summary` 预算与 `fix_router` 由 `test_phase0_scripts.py` 断言。
- `scripts/fix_gate.py` 相对 HEAD `2b705c0` **无 diff**；`target_cleared` / `zero_new_layout` / `pixel_gate` / `unit_green` 语义不变。

### Independent review（fresh reviewer，working tree vs 2b705c0）

| AC | 结果 |
|----|------|
| S2/Tasks AC1–AC8（compose-escalate / SKILL Fix / fix-gate 分流 / DEFAULT_STATE+resume / export optional+schema v1 / report-template+export-schema / out-of-scope / workspace override） | **全部 PASS** |

- **Critical：无**。
- Major（流程）：本文件此前 `status: in-progress`、Report 为空 —— 本条 Finalize 关闭。
- Minor（不阻塞）：`escalations_used` 增量规则与 `by_route` 唯一性仅文档约定、无脚本自动递增；`max_compose_escalations` 在 `budget` 与 `fix_router` 双存；`lite_max_attempts` 命名前缀混用（Spec 原文如此）；`export-schema.md` 中英混排；`validate_report.py` 不强制 Fix Router 节（向后兼容）。

- 结论：**无未处理 critical** → 可交付。

### Out of scope 核对

- quiet / Confirm / 指纹 / `fix_gate.py` 判定：未改。
- 用户 `AGENTS.md`：未自动改写。
- 内置 compose-next skill：未改。
- compose Review PASS ≠ quiet：已写入 `compose-escalate.md`。

### Journey log

1. 环境拒绝 `git worktree add`（isolated session / 共享 ref）→ Workspace override：主 checkout 实施；分支与提交需用户或后续可写会话完成。
2. `fix_router.escalations_used` / `by_route` **无 Python 递增器**，由 main agent 持锁写 state —— 文档约定优先，避免静默双计。
3. Export `schema_version` 保持 1：新路由字段一律 optional，避免破坏既有 CI 校验。
4. Reviewer 会直接 Finalize Spec；实现方仍需核对 Report 是否符合 compose 模板并补 Journey。

## [S1] Problem

`iterative-bug-hunter` 的 Fix 阶段目前只有「本地 `fix_gate` 小修」与「失败→Deferred」两条路径。对「能写清 oracle 但需重定位」「说不清怎样算修好 / 要改产品行为」的 Confirmed 缺陷，缺少可陈述的路由与交接物，导致：中等问题过早放弃或临场误升重型流程；升级时缺少结构化 bug packet；预算与「禁止同构重试」未编码进 state/export。

研究结论（`docs/blueprint/hunt-escalate-compose-v2.md`）：默认应对齐 Agentless 式本地管道；compose-next 仅作 oracle gap / 契约重定义等窄口升格。

## [S2] Design

### Workspace override

环境拒绝 `git worktree add`（isolated child session / 共享 ref store）。实现落在**主 checkout** 文件上；不嵌套 worktree。后续已在主 checkout 创建分支 `feat/hunt-fix-router` 并提交（见 frontmatter `commits`）。Workspace override 仍适用：未使用独立 worktree。

### 准据

| 维度 | 准据 |
|------|------|
| 算法不变量 | 仓库根 `DESIGN.md`（quiet / 指纹 / Confirm） |
| Local 门禁 | `references/fix-gate.md`（`fix_gate.py` 检查语义不降） |
| 路由 | `references/compose-escalate.md`（本文实现的操作化） |
| 过程 | compose-next；**不**改内置 compose-next skill |

### 三档路由（Fix）

仅 `mode=hunt-and-fix` 且状态 **Confirmed** 进入修复路由。

| 档 | 命中（可陈述） | 动作 |
|----|----------------|------|
| **local** | oracle 可判定（rule_id + route×viewport 等）；预计编辑点 ≤ `max_local_edit_sites`（默认 3）且沿既有契约 | 定位 →（可选）≤3 候选 → 复现 → `fix_gate.py` |
| **lite** | oracle 在但 Local 未过且预算未尽，或编辑点 4–`max_lite_edit_sites`（默认 6）/ 跨包仍沿既有契约，或需重定位假设 | 写/更新 bug packet → 重定位 → ≤ `lite_max_attempts` → 仍 `fix_gate.py`；**不** load compose-next |
| **compose** | `oracle_gap`（无法写出机器「修好了」）或 `contract_change`（期望行为需产品/设计决策）或用户明确要 PR/Spec（`user_pr`） | `question`/预授权 → load compose-next（slim）→ Finalize 后**强制**回 hunt Converge |

**不升 compose**：单点 overflow/contrast/touch-target/aria 等已有机器验收项。

**前置**：Candidate/Deferred 不进入修复路由；探测/axe 失败记 Blind Spots，禁止假通过。

### 预算（state.budget）

| 字段 | 默认 |
|------|------|
| `max_local_attempts` | 3 |
| `lite_max_attempts` | 2 |
| `max_compose_escalations` | 2 |
| 既有 `max_fix_failures` | 5（保留） |

同 bug 连续修复失败 ≥2 → `diminishing=true`（记入 bug / REPORT）。禁止同构重试：失败后必须重定位、换策略、升档或 Deferred。

### fix_router（state）

```json
{
  "fix_router": {
    "enabled": true,
    "escalations_used": 0,
    "max_compose_escalations": 2,
    "by_route": {"local": 0, "lite": 0, "compose": 0, "deferred": 0}
  }
}
```

### Bug / packet 字段（bugs/**.json 扩展，均可选）

- `fix_route`: `local` | `lite` | `compose`
- `fix_reason_codes`: string[]（如 `oracle_ok`, `needs_relocalize`, `oracle_gap`, `contract_change`, `user_pr`, `edit_breadth`, `budget_exhausted`）
- `fix_attempts`: `{local, lite, diminishing}`
- `packet_path`: 相对路径 `.bug-hunter/bugs/<id>/packet.json`（升 lite/compose 时建议写）

Packet 最小字段见 `references/compose-escalate.md`（bug_id, fingerprint, route, reason_codes, location, repro, oracle, attempts, serving_tree, base_url, budget）。

### Export / REPORT

- `export_report.slim_bug` 透出 `fix_route`, `fix_reason_codes`, `fix_attempts`（内含 `local`/`lite`/`diminishing`）, `packet_path`（有则写）。
- 顶层可选 `fix_router` 与 `budget`（来自 state）；`schema_version` 保持 **1**（新增字段均为 optional，不破坏旧校验）。
- REPORT 模板增加「修复路由（Fix Router）」节：route 计数、compose 升格、diminishing、Blind Spots。

### SKILL / references

- `SKILL.md` Fix 步骤：三档一句话 + 链 `compose-escalate.md`。
- `fix-gate.md`：失败后按路由分流，不再仅「≥ max_fix_failures → Deferred」。
- 不改 quiet、Confirm、指纹、`fix_gate.py` 检查逻辑。

### 非目标见 [S3]

## [S3] Out of Scope

- 修改内置 `compose-next` skill 以自动调用 hunt
- 自动 git commit / PR / merge / 删除 worktree
- 修改 Confirm 门、quiet 四条件、指纹算法、`fix_gate.py` 判定语义
- 在本 feature 中把 skill 安装到 `~/.config/mimocode/skills/`（发布动作，另做）
- 自动改写用户项目 `AGENTS.md`
- 实现完整的 compose-next 运行时（本 skill 只提供路由文档与 packet 契约）

## Tasks

- [x] T1: Spec 就位 — acceptance: 本文件存在且 status=in-progress (covers: S2)
- [x] T2: `references/compose-escalate.md` — acceptance: 含三档判据、预算、packet schema、≥2 正例与 ≥2 负例、禁止项 (covers: S2)
- [x] T3: `SKILL.md` + `fix-gate.md` + `report-template.md` + `export-schema.md` 指针与分流 — acceptance: Fix 主循环链到 compose-escalate；fix-gate 写明 local/lite/compose 分流；模板含 Fix Router 节 (covers: S2)
- [x] T4: `init_state.py` 预算与 `fix_router` — acceptance: DEFAULT_STATE 含 max_local_attempts/lite_max_attempts/max_compose_escalations 与 fix_router；resume_summary 透出 budget 与 fix_router (covers: S2)
- [x] T5: `export_report.py` 透出路由字段 — acceptance: slim_bug/build_export 含 fix_* 与顶层 fix_router/budget；validate 仍对旧必填字段通过 (covers: S2)
- [x] T6: 单元测试 — acceptance: `unittest discover` 全绿；新增 init_state/export 路由断言 (covers: S2; depends: T4,T5)
- [x] T7: Verify + Review + Finalize Spec — acceptance: 测试/导出校验 PASS 记录在 Report；独立 review 无未处理 critical；status=delivered (covers: S1;S2; depends: T2–T6)
