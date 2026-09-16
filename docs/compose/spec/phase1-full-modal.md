---
feature: phase1-full-modal
status: delivered
updated: 2026-09-16
branch: feat/phase1
commits: 98e54da..HEAD
---

# Phase 1 — 全模态成型

## Report

**What was built** — Phase 1 全模态通道落地：`capture_web.py`（routes×viewports 矩阵、MANIFEST、Playwright Python/Node 后端、无 backend exit 3）；`layout_probe.py` 扩展为 overflow-x / text-clip / overlap-interactive / zero-size / off-canvas / touch-target；`contrast_probe.py`（WCAG 对比度、字号、行高，背景 depth 回溯）；`visual_diff.py`（snapshot/compare/approve）；`fix_gate.py`（target_cleared + zero_new_layout + pixel_gate + unit_green）；`hunt_round.py` 单轮编排；`init_state` Phase 1 oracle 默认值。demo 注入 touch-target / overlap / zero-size；references 与 SKILL.md 同步。

**Verification** — `python -m unittest discover -s tests`：54 tests OK。`tests/phase1_fixture_e2e.py`：run-1 发现 8 条（overflow-x/touch-target/overlap×2/zero-size×2/contrast×2），overlap 在 375 与 1440 指纹区分；run-2 new=0 known=8；fix_gate 对 overflow-x 修复 target_cleared + zero_new 通过。`capture_web.py` 无 Playwright 时 exit 3 + MANIFEST backend=unavailable。

**Journey log** —
1. 本机 `MIMO_PYTHON` 无 playwright 包且 node 无 playwright 模块 → 采集脚本设计为三层降级，验收用 fixture E2E。
2. `hunt_round --skip-capture` 初版把 probe 写在 `if not capture` 分支内，导致 fixtures 不探测；改为「有 MANIFEST 就 probe」。
3. Windows `shell=True` 下 `node -e '...'` 单引号不生效；dynamic 失败用例改用 `sys.executable -c raise SystemExit(1)`。
4. 默认 degrade=L1 会跳过 web probe；有 MANIFEST 时本轮视为 L2，与「已有采集产物」语义一致。
5. 指纹仍用粗粒度 rule digest，避免 1px 噪声伪造新 finding（沿用 Phase 0 结论）。

## [S1] Problem

Phase 0 已能初始化状态、对单 viewport 做 `overflow-x`、指纹去重、quiet 收敛并写 REPORT。但 skill 仍达不到 DESIGN §10.2「全模态成型」：

1. 无自动化多 viewport 采集（截图 / `elements.json` / AX / MANIFEST），agent 只能手搓 JSON 喂 probe；
2. `layout-geom` 仅 `overflow-x`，缺 overlap / zero-size / off-canvas / touch-target / text-clip；
3. 无 `contrast-type`（demo 上的低对比度文字只是候选，未产出 L3）；
4. 无 `responsive-matrix`（同一逻辑问题在不同 viewport 应独立 Finding，但无矩阵重跑工具）；
5. 无像素 `visual-diff` 基线与「有意变更」放行；
6. Fix Gate 仍是文档约定，无法机器判定「症状消失 + 回归矩阵零新增 + 像素门」；
7. 无 hunt-and-fix 轮次编排：从 capture → probe → register → confirm 字段 → fix gate → converge 缺少可执行入口。

## [S2] Design

### Workspace override

本环境禁止 `git worktree add`（Phase 0 已证实：共享 ref store）。实现继续在主 checkout 分支 `feat/phase1` 上进行，不嵌套 worktree。依赖安装：仓库脚本保持 **stdlib-only**（Pillow 已在 `MIMO_PYTHON`，作可选增强）；浏览器采集不强制 `import playwright`。

### 交付边界（Phase 1 only）

**新增/扩展脚本（`iterative-bug-hunter/scripts/`）**

| 脚本 | 职责 |
|------|------|
| `capture_web.py` | 多 route×viewport 采集；写 captures + MANIFEST；浏览器不可用时清晰失败/降级 |
| `layout_probe.py` | 扩展完整 layout-geom 规则集 |
| `contrast_probe.py` | WCAG 对比度 / 字号 / 行高 |
| `visual_diff.py` | 基线建立、像素 diff、有意变更标记 |
| `fix_gate.py` | §6.3 可判定回归门（矩阵复跑 + 目标症状 + 零新增 + 像素门） |
| `hunt_round.py` | 单轮编排：capture→probes→register→converge（不自动改代码） |

**更新 references**

- `capture-protocol.md` — Phase 1 产物契约与脚本入口
- `visual-rules.md` — 完整阈值表
- `fix-gate.md` — 脚本可判定字段与退出码
- `strategies.md` — Phase 1 通道与调度提示
- `SKILL.md` — 主循环步骤指向新脚本（仍保持正文精简）

**验收 demo 扩展（`examples/acceptance-demo/`）**

在 Phase 0 缺陷之上增加可机器判定的 Phase 1 缺陷（注释标明 INTENTIONAL）：

| 缺陷 | 期望 rule_id | viewport |
|------|--------------|----------|
| 既有 CTA 容器溢出 | `overflow-x` | 375x812 |
| 小触控目标 `<button class="btn-tiny">` | `touch-target` | 375x812 |
| 两可点击元素重叠（绝对定位） | `overlap-interactive` | 1440x900 |
| 零尺寸隐藏可点节点 | `zero-size` | 1440x900 |
| 既有低对比度文字 | `contrast-text` | 任意 |
| 既有 `add` off-by-one | dynamic 测试 | — |

另提供 **fixable** 样本：一份可被 `fix_gate` 验证的补丁场景（如 demo 内 `src/fixable.js` 的明显逻辑错误，或 CSS 上可一键修的 `touch-target`），用于 hunt-and-fix 验收；修复由 agent/测试完成，`fix_gate.py` 只判门。

**文档**

- `docs/ACCEPTANCE.md` 增补 Phase 1 DoD 表
- `docs/compose/spec/phase1-full-modal.md` 本文
- `tests/test_phase1_*.py`（或扩展 `test_phase0_scripts.py` 旁新文件）覆盖纯函数

### 采集契约（capture_web.py）

**输入**：`--base-url`、`--routes`、`--viewports`（默认来自 `.bug-hunter/state.json` 或 CLI）、`--out`（默认 `.bug-hunter/runs/run-N/captures`）。

**每 page×viewport 产物**（与 Phase 0 capture-protocol 对齐并扩展）：

```
{route_slug}__{WxH}__viewport.png
{route_slug}__{WxH}__full.png          # 可选，失败不阻断
{route_slug}__{WxH}__elements.json
{route_slug}__{WxH}__ax.json           # 可选
{route_slug}__{WxH}__console.json
MANIFEST.json
```

`elements.json` 每项必填 schema（供 layout/contrast/responsive）：

```json
{
  "selector": "[data-testid=primary-cta]",
  "tag": "button",
  "route": "/",
  "viewport": "375x812",
  "interactive": true,
  "bbox": {"x": 0, "y": 0, "w": 12, "h": 12},
  "scrollWidth": 0,
  "clientWidth": 0,
  "text_overflow": "visible",
  "computed": {
    "color": "rgb(150, 150, 150)",
    "backgroundColor": "rgb(255, 255, 255)",
    "fontSize": "12px",
    "lineHeight": "14px",
    "fontWeight": "400",
    "overflowX": "visible",
    "textOverflow": "clip",
    "cursor": "pointer"
  },
  "text": "…",
  "depth": 0,
  "inViewport": true
}
```

document 根元素仍用 `selector: "html"`。

**浏览器后端选择（降级，禁止静默假成功）**：

1. 若 `playwright` Python 包可用 → 同步 API；
2. 否则若 `npx playwright` / `node` + 可解析 `playwright` 模块可用 → 生成临时 JS runner 执行；
3. 否则 `exit 3`，stderr 说明「无 playwright；请用 playwright-mcp 按 protocol 采集后调用 probes」，并写 `MANIFEST.json` 的 `backend: "unavailable"`。L2 探测据此可降级。

纯函数（矩阵展开、slug、schema 归一化、manifest 写入）必须可单测，不依赖浏览器。

MANIFEST 字段：`base_url`, `routes`, `viewports`, `backend`, `items[]`（相对路径、route、viewport、status）、`captured_at`。

### layout-geom 完整规则（扩展 layout_probe.py）

在保留 Phase 0 `overflow-x` 行为与指纹 digest 规则的前提下新增。输入同为 `elements.json`（list 或 `{elements,viewport_width,epsilon…}`）。

| rule_id | 判定 | category | 默认阈值 | digest |
|---------|------|----------|----------|--------|
| `overflow-x` | 既有：根 sw>cw+ε 或元素 right>vw+ε 或 el sw>cw+ε（非 ellipsis） | ui-layout | ε=2 | `overflow-x\|horizontal-overflow` |
| `text-clip` | el sw>cw+ε 且 `text_overflow not in (ellipsis, clip-intentional)` **且** 有文本 | ui-layout | ε=2 | `text-clip\|content-clipped` |
| `overlap-interactive` | 两 interactive 元素 bbox 相交面积 / min(面积) > 0.2 | ui-layout | 0.2 | `overlap-interactive\|bbox-intersect` |
| `zero-size` | 有内容（text 或 interactive）且 w<1 或 h<1 | ui-layout | 1 | `zero-size\|degenerate-box` |
| `off-canvas` | bbox 完全在 viewport 外（right<0 或 left>vw 或 bottom<0 或 top>vh）且 interactive | ui-layout | — | `off-canvas\|outside-viewport` |
| `touch-target` | interactive 且 min(w,h) < `touch_target_px` | ui-layout | 44 | `touch-target\|below-min` |

规则：

- 每条 Finding 必须含 `rule_id`, `modality=web-visual`, `category`, `location.route/viewport/selector/bbox`, `metrics`, `evidence_level_target=L3`, `detected_by=layout-geom`, `core_assertion_digest`。
- **根节点不双计**：`html`/`body` 只参与 page-level `overflow-x`，不参与 text-clip/overlap/touch。
- overlap 对每对元素最多产出一条（排序 selector 保证稳定）。
- viewport 高度来自 `viewport` 字段或 `viewport_height` 参数（用于 off-canvas）。
- CLI：保持 stdin JSON；可选 `--rules overflow-x,touch-target,…` 过滤，默认全部。

### contrast-type（contrast_probe.py）

| rule_id | 判定 | category | 默认 |
|---------|------|----------|------|
| `contrast-text` | 有效前景/背景对比度 < min_contrast；大字（≥24px 或 ≥18.66px bold）用 large_text_min | ui-visual | 4.5 / 3.0 |
| `font-too-small` | computed fontSize < font_too_small_px（忽略 0 尺寸节点，避免与 zero-size 双计） | ui-visual | 12 |
| `line-height-tight` | line-height/fontSize < 1.2 且 text 含换行或多行宽度 | ui-visual | 1.2 |

对比度算法（WCAG 2.x）：

- 解析 `rgb()/rgba()`；忽略 `transparent`；
- 背景：元素 `backgroundColor`；若 alpha≈0 则沿祖先 `depth` 向上找第一个不透明背景；都找不到则用 `rgb(255,255,255)` 并在 metrics 记 `background_assumed: true`；
- 相对亮度与对比度按标准公式；输出 `metrics.contrast_ratio`（保留 2 位）。

Finding 结构与 layout 一致，`detected_by: "contrast-type"`，digest 如 `contrast-text|below-min`。

### responsive-matrix

不单独发明规则，而是**矩阵执行语义**：

- `layout_probe.py` / `contrast_probe.py` 按 page×viewport 独立跑；指纹已含 viewport → 天然区分断点。
- `hunt_round.py` 对 `routes × viewports` 全矩阵跑 probes，汇总到 `runs/run-N/findings/raw/{strategy}__{route}__{viewport}.json`。
- 报告统计：`new_by_viewport`、同一 selector 在多 viewport 的 finding 集合（供人工看「只炸窄屏」）。

`fix_gate.py` 的回归矩阵 = **当前 state 中已扫过的全部 route×viewport**（不是仅修复页）。

### visual_diff.py（Pillow 可选）

**基线布局**：`.bug-hunter/baselines/web/{route_slug}__{WxH}.png`

命令面：

- `visual_diff.py snapshot --captures DIR --baseline-dir DIR`：将本轮 `*__viewport.png` 复制为基线（仅当基线不存在或 `--force`）。
- `visual_diff.py compare --captures DIR --baseline-dir DIR --threshold 0.01 --out findings.json`：
  - 尺寸不一致 → 视为 fail（`size-mismatch`）；
  - 逐像素比较，`diff_ratio = differing_pixels / total_pixels`；
  - `diff_ratio > threshold` → finding `visual-diff` / category `ui-visual` / digest `visual-diff|pixel-delta`；
  - metrics: `diff_ratio`, `threshold`, `baseline`, `current`。
- Pillow 不可用 → compare 写 `status: "skipped"` 且 exit 0（记录盲区），不假装通过；snapshot 若目标是 PNG 文件操作可用 stdlib `shutil`，不依赖 Pillow。

**intentional_visual_change**：

- `visual_diff.py approve --route / --viewport 375x812 --captures DIR --baseline-dir DIR --reason "..."` 将当前截图提升为新基线，并写 `.bug-hunter/baselines/approvals.jsonl`（route, viewport, reason, sha256, at）。
- fix_gate 检查：若非目标路由 diff 超阈 → fail，除非该 route×viewport 在本次 fix 的 approvals 中，或 `verify.md` 旁路文件 `.bug-hunter/runs/run-N/fix-verify.json` 含 `"intentional_visual_change": true` 且列出的 route×viewport 与 diff 集合一致。

### fix_gate.py（§6.3 可判定）

输入：

- `--root` 项目根（含 `.bug-hunter/`）
- `--bug` confirmed bug JSON 路径或 id
- `--captures` 修复后 captures 目录（或自动触发 capture_web）
- `--baseline-dir`
- `--elements-map` 可选：route→elements.json
- `--regression-mode matrix|target-only`（默认 matrix）

检查项与退出码：

| check | 通过条件 | 失败 exit |
|-------|----------|-----------|
| `target_cleared` | 同 `rule_id` + 同 route×viewport 的 finding 不再出现（对修复后 captures 重跑对应 probe） | 1 |
| `zero_new_layout` | 回归矩阵重跑 layout+contrast，相对「修复前 fingerprints/已知 confirmed」零新增 rule 命中（新增 = 新指纹） | 1 |
| `pixel_gate` | 仅目标 route×viewport 允许 diff；其他已扫 cell 超阈 → fail，除非 intentional 审批 | 1 |
| `unit_green` | 若 `--test-cmd` 提供则执行，exit 0 | 1 |
| `lock` | 全程持有 `.bug-hunter/.lock` 写 verify 结果 | 1 |

输出：stdout JSON + 写 `runs/run-N/fix-verify.json`：

```json
{
  "bug_id": "bug-0001",
  "ok": false,
  "checks": {
    "target_cleared": {"ok": true, "rule_id": "overflow-x"},
    "zero_new_layout": {"ok": true, "new_fingerprints": []},
    "pixel_gate": {"ok": false, "unexpected_diffs": [{"route": "/about", "viewport": "375x812"}]},
    "unit_green": {"ok": true, "cmd": "npm test"}
  },
  "intentional_visual_change": false
}
```

不修改源码；不自动 `git checkout` 回滚（回滚仍是 agent/SKILL 动作，文档写明）。同一 bug 连续失败计数由调用方维护 `bug.fix_failures`。

### hunt_round.py（单轮编排）

```
hunt_round.py --root P --run-id run-1 [--skip-capture] [--captures DIR]
```

步骤：

1. 读 state，解析 routes/viewports/base_url/degrade；
2. degrade≥L2 且未 `--skip-capture` → 调 `capture_web.py`；
3. 对每个 captures cell 跑 `layout_probe` + `contrast_probe`（函数级调用，不必须子进程）；
4. 可选 `--dynamic-cmd` 跑 code 动态通道，stderr 失败写入 findings（category `logic` / modality `code`）；
5. 全部 finding `fingerprint.py --register`；
6. 写 `runs/run-N/summary.json`（new/known counts、by rule、by viewport）；
7. 调 `converge_check.py` 逻辑，打印 quiet 结果。

**不**自动确认/修复代码；confirm 仍由 agent 按 confirm-protocol 写 bugs/confirmed。脚本可提供 `--write-candidates` 把 L3-shaped findings 拷到 `findings/candidates/` 供确认。

### state 扩展

`init_state.py` 增加（向后兼容缺省）：

```json
"phase": 1,
"visual_oracle": {
  "overlap_ratio": 0.2,
  "line_height_min_ratio": 1.2,
  "visual_diff_threshold": 0.01,
  "...": "phase0 fields retained"
}
```

已存在 Phase 0 state 时：`init_state --resume-summary` 与 `hunt_round`/`fix_gate` 读取时对缺失键用默认值合并，不强制重 init。

### 测试边界（不依赖浏览器）

- layout：overflow-x 回归 + touch-target / overlap / zero-size / off-canvas / text-clip 正反例；
- contrast：已知 rgb 对比度数值（如 #969696 on #fff ≈ 2.8）、大字阈值、背景沿 depth 回溯；
- visual_diff：两张合成 PNG（Pillow）diff_ratio；无 Pillow 时 skipped 路径；
- fix_gate：用临时 elements fixtures 模拟修复前后，测 target_cleared / zero_new / pixel intentional；
- hunt_round：`--skip-capture` + 临时 fixtures 全流程；
- capture_web：矩阵 slug / manifest schema / backend unavailable 退出码 3（不启真浏览器）。

E2E（手动/验收脚本，不进默认 unittest）：启动 demo → capture → hunt_round → 至少 2 条 Phase 1 L3（touch-target + contrast-text）→ 修 touch-target → fix_gate 过。

### SKILL.md 增量（正文仍精简）

- 主循环 Capture/Hunt 步骤指向 `capture_web.py` / `hunt_round.py`；
- Fix Gate 指向 `fix_gate.py` 与退出码语义；
- quiet 条件 4 补充：visual-diff 未超阈或 intentional 已批。

## [S3] Out of Scope

- Phase 2：`ux-flow`、WebTestPilot 符号化、canvas-safe/asset、vlm-audit、subagent 并行采集协议落地；
- axe-core 自动安装与 a11y-axe 脚本化（仍可由 agent/MCP 跑，Phase 1 不捆绑 npm 依赖）；
- CI 门禁、路由自动发现、误报反哺（Phase 3）；
- 自动 git 回滚执行器；
- 将 skill 安装到 `~/.config/mimocode/skills/`。

## Tasks

- [x] T1: 本 spec + 分支 `feat/phase1` — acceptance: 文档存在且 status=designed (covers: S2)
- [x] T2: `capture_web.py` + MANIFEST/schema + 降级 exit 3 — acceptance: 单测覆盖矩阵/manifest/无浏览器路径；真浏览器可选 (covers: S2)
- [x] T3: `layout_probe.py` 完整规则 + `contrast_probe.py` — acceptance: 各 rule 正反例单测通过；overflow-x 行为不回归 (covers: S2)
- [x] T4: `visual_diff.py` 基线/diff/approve + `fix_gate.py` 可判定门 — acceptance: fixtures 下 target/zero_new/pixel/intentional 单测通过 (covers: S2)
- [x] T5: `hunt_round.py` + `init_state` phase1 默认值 + references/SKILL 增量 — acceptance: skip-capture 编排单测通过；文档指向新脚本 (covers: S2)
- [x] T6: demo 扩展缺陷 + `docs/ACCEPTANCE.md` Phase 1 DoD + unittest 全绿 — acceptance: `python -m unittest discover -s tests` OK；DoD 表完整 (covers: S1;S2; depends: T2–T5)
