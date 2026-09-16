---
feature: phase0-iterative-bug-hunter
status: delivered
updated: 2026-09-16
branch: feat/phase0
commits: a6ae06adda282aab6ff7effd97cebba455ad27c1..16f6442ca3b0f5d1d43ffcd302036cfe408cac0f
---

# Phase 0 — Iterative Bug Hunter 骨架

## Report

**What was built** — 落地了 Phase 0 skill 本体 `iterative-bug-hunter/`：精简 `SKILL.md`（触发/Scope/主循环/quiet 四条件/Confirm L3-L4/用户合同）、六份 `references/`、`locales/`，以及状态脚本 `init_state.py`（含 O_EXCL 单写锁与 resume）、`fingerprint.py`（DESIGN §3.2 粗粒度断言指纹 + 持锁注册去重）、`converge_check.py`（§6.2 quiet 四条件）、`layout_probe.py`（overflow-x 最小集，根节点不双计）、`validate_report.py`。验收 demo `examples/acceptance-demo/`（零依赖双路由站）注入 375px 横向溢出与 `add` off-by-one；`docs/ACCEPTANCE.md` DoD 8 项已勾选。

**Verification** — `python -m unittest discover -s tests`：23 tests OK。demo `npm test`/`node --test`：预期失败（注入逻辑 bug）。Playwright 375x812 采集 → `layout_probe` 产出 3 条 L3（修复双计后）→ `fingerprint --register` run-1 new=3 / 噪声重采 known=1 / run-2 known=3（duplicate_rate=1.0）→ quiet_streak≥2 `converged=true` → 主 REPORT `validate_report` OK。L1 降级报告在 `runs/run-l1-degrade/REPORT.md`，Blind Spots 含 web-visual 未覆盖。预置 `.lock` 后 `init_state` 失败退出，state 不损坏。

**Journey log** —
1. 环境禁止 `git worktree add`（共享 ref store），改在主 checkout 的 `feat/phase0` 分支实现。
2. PowerShell `Set-Content -Encoding utf8` 写 BOM 导致 `json.load` 失败 → 读侧统一 `utf-8-sig`，写侧用 Python 重写。
3. `Path.replace` 参数方向写反曾使 fingerprint 落盘失败；Windows 上已用 `os.replace`。
4. 首轮审查 5 个 critical（根 overflow 双计、register 无锁、init TOCTOU、像素级指纹、DoD 7 缺 E2E）全部修复后二次复审通过。
5. 指纹刻意不含精确 `overflow_px`，否则 1px 采集噪声会伪造新 bug、破坏 quiet 收敛。

## [S1] Problem

`DESIGN.md` 已定义全模态迭代抓 BUG skill，但仓库目前只有设计文档，没有可安装的 skill 本体、状态机脚本、报告模板，也没有可验收的本地 demo。需要落地 **Phase 0 骨架 + 验收 DoD**，使 skill 在真实本地 web demo 上能：初始化状态 → 多轮扫描 → 确认 L3 视觉/代码 finding → 按 quiet 四条件收敛 → 产出含盲区的 REPORT。

## [S2] Design

### 交付边界（Phase 0 only）

- Skill 根：`iterative-bug-hunter/`（与 DESIGN §7.1 一致）。
- 必含脚本：`init_state.py`、`fingerprint.py`、`converge_check.py`。
- 最小通道集：`static`、`dynamic`；degrade≥L2 时 `a11y-axe`、`layout-geom`（仅 `overflow-x` 规则）。
- 文档：`references/strategies.md`、`references/capture-protocol.md`、`references/confirm-protocol.md`、`references/report-template.md`、`references/fix-gate.md`、`references/visual-rules.md`（Phase 0 规则子集）。
- 验收：`examples/acceptance-demo/` 本地可启动 web demo（≥2 路由、≥1 L3 视觉 bug、≥1 静态/测试问题）；`docs/ACCEPTANCE.md` DoD 8 项。
- 不在 Phase 0：完整 contrast-type / responsive-matrix / canvas 通道 / vlm-audit / 像素 visual-diff / Fix Gate 自动回归矩阵。

### Workspace override

本环境禁止 `git worktree add`（共享 ref store 保护）。实现改在主 checkout 的 `feat/phase0` 分支上进行；不嵌套 worktree。

### 状态与数据契约

落盘目录以目标项目 cwd 下的 `.bug-hunter/` 为准（DESIGN §4.2）。`state.json` 关键字段：

- `modalities_enabled`, `surfaces.web.{base_url,routes,viewports,degrade_level}`, `visual_oracle`, `budget`, `convergence`, `run_count`, `quiet_streak`, `last_strategy_set`, `stats`
- `fingerprints.json`：`fingerprint -> {bug_id, status, modality, category, first_seen, last_seen, runs}`
- 单写者：`.bug-hunter/.lock`（`O_EXCL`）；脚本读写 state 时持有锁。

### 指纹

`fingerprint.py` 按 DESIGN §3.2：

```
sha256_hex16(
  modality | normalize(route_or_file) | viewport_or_export_size |
  category | normalize(element_ref) | core_assertion_digest
)
```

同一 viewport 同一问题跨轮去重；不同 viewport 视为不同 Finding。

### 收敛（converge_check.py）

实现 §6.2 quiet 四条件，输出 JSON：

```
{
  "quiet": true|false,
  "quiet_streak": n,
  "required_quiet_streak": K,
  "converged": bool,
  "reasons": [...]
}
```

quiet 要求：本轮执行 ≥1 允许策略；覆盖 `modalities_enabled` 中每个仍可用 modality；新 Confirmed=0；无新回归。违反则 `quiet_streak` 清零。

### SKILL.md 契约

正文仅含：触发、Scope 问答、L0–L4 摘要、主循环步骤、quiet/K、Confirm L3/L4、用户合同（附录 B）、禁止项。细节指向 `references/`。frontmatter 使用 DESIGN §7.2 草案。`locales/zh-CN.json` + `en-US.json`。

### 验收 demo 契约

`examples/acceptance-demo/`：

- Node 零依赖静态服务器 `server.js`，路由 `/` 与 `/about`。
- `/` 含宽按钮容器，`375x812` 下 `overflow-x`（L3 `layout-geom`）。
- `/about` 含缺 alt 的 img 或低对比度文本（供 axe/contrast 候选；Phase 0 至少保证 overflow-x 可确认）。
- 故意注释掉的/失败的单元测试或类型错误文件，供 `static`/`dynamic` 通道发现。
- `package.json` scripts：`start` / `test`（test 应能失败以演示 dynamic）。

### 测试边界

- 对 `init_state.py` / `fingerprint.py` / `converge_check.py` / 最小 `layout_probe` 用 stdlib `unittest`（无第三方依赖）。
- 验收运行：初始化 state → 模拟/真实两轮扫描 → quiet 收敛 → 写出 `REPORT.md` 骨架并含 Blind Spots。

## [S3] Out of Scope

- Phase 1/2/3 的完整视觉通道、Fix Gate 像素门、canvas、VLM 双审、CI。
- 自动 `git` 修复与回滚执行器（Fix Gate 仅文档与报告字段约定）。
- 多项目并行会话协调（单项目单写者已覆盖）。
- 将 skill 安装到 `~/.config/mimocode/skills/`（本仓为源码仓；安装属发布动作）。

## Tasks

- [x] T1: 编写 feature 文档与目录骨架 — acceptance: 本 spec + `iterative-bug-hunter/` 树存在 (covers: S2)
- [x] T2: 实现 `init_state.py` — acceptance: 在空目录生成 state/fingerprints/目录树/锁约定 (covers: S2)
- [x] T3: 实现 `fingerprint.py` — acceptance: 相同输入稳定哈希；viewport 差异产生不同指纹 (covers: S2)
- [x] T4: 实现 `converge_check.py` — acceptance: 四条件用例通过；违规清零 quiet_streak (covers: S2)
- [x] T5: 最小 `layout_probe.py`（overflow-x）— acceptance: 对含溢出 HTML 的 bbox 数据能产出 L3 finding 结构 (covers: S2)
- [x] T6: SKILL.md + locales + references — acceptance: 正文≤5000 词，含触发/Scope/循环/合同/指针 (covers: S2)
- [x] T7: 验收 demo + package.json + server — acceptance: `npm start` 可开 2 路由；375px 存在 overflow；test 可红 (covers: S1;S2)
- [x] T8: docs/ACCEPTANCE.md + 单元测试跑通 — acceptance: DoD 表完整；`python -m unittest` 全绿 (covers: S1;S2; depends: T2–T5,T7)
