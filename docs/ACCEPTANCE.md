# Phase 0 / Phase 1 验收 DoD

锁定验收项目：`examples/acceptance-demo/`（零依赖 Node 静态站，2 路由）。

## 启动

```powershell
cd examples/acceptance-demo
npm start
# http://127.0.0.1:5173
```

注入缺陷：

| 类型 | 位置 | 期望发现通道 | Phase |
|------|------|----------------|-------|
| L3 视觉 | `/` `.cta-row { min-width: 420px }` → 375px `overflow-x` | `layout-geom` | 0 |
| a11y 候选 | `/about` `<img>` 无 alt | `a11y-axe` | 0 |
| 对比度 | `/about` `.low-contrast` | `contrast-type` | 1 |
| 触控目标 | `/` `.btn-tiny` 24×20 | `touch-target` | 1 |
| 重叠 | `/` `.overlap-a` / `.overlap-b` | `overlap-interactive` | 1 |
| 零尺寸 | `/` `.zero-btn` | `zero-size` | 1 |
| 逻辑/测试 | `src/calc.js` `add` 多加 1 | `dynamic`（`npm test` 红） | 0 |

## Phase 0 DoD 勾选表

| # | 检查项 | 通过标准 | 状态 |
|---|--------|----------|------|
| 1 | 可 resume | 删会话后读 `state.json` 能接着 quiet_streak | **PASS** — `init_state --resume-summary` 返回 quiet_streak=2 |
| 2 | 迭代收敛 | 验收项目 ≤4 轮满足 §6.2 quiet 后停 | **PASS** — run-1 发现后 run-2 去重，quiet_streak≥2，`converged=true` |
| 3 | L3 视觉 Finding | ≥1 条 `ui-*`，evidence L3，含截图路径 | **PASS** — `overflow-x` @ `/` 375x812，截图 `runs/run-1/captures/home__375x812__viewport.png` |
| 4 | 假阳性 | Confirmed 中无 L3 证据条数 = 0 | **PASS** — 3 条 confirmed 均 evidence.level=L3 |
| 5 | 去重 | 第 2 轮起可统计已见指纹占比 | **PASS** — run-2 `duplicate_rate=1.0`，new_count=0 |
| 6 | REPORT | 范围、modality 摘要、Blind Spots、规则 ID | **PASS** — `validate_report.py` → OK |
| 7 | 降级演示 | 去掉 dev server → L1，Blind Spots 含 web-visual | **PASS** — `runs/run-l1-degrade/REPORT.md`：degrade=L1，Blind Spots 明确「web-visual：整通道未覆盖」 |
| 8 | 无锁冲突 | 双写第二者失败，state.json 不损坏 | **PASS** — 预置 `.lock` 后 `init_state` 退出码 1 且提示 lock exists |

## Phase 1 DoD 勾选表

| # | 检查项 | 通过标准 | 状态 |
|---|--------|----------|------|
| 1 | 多 viewport 采集 | `capture_web.py` 矩阵产物 + MANIFEST；无 backend 时 exit 3 | **PASS** — 单测 `test_expand_matrix` / `test_manifest_unavailable_backend`；backend 探测见脚本 |
| 2 | 完整 layout-geom | overflow-x / text-clip / overlap / zero-size / off-canvas / touch-target 正反例 | **PASS** — `tests/test_phase1_scripts.py` TestLayoutPhase1 |
| 3 | contrast-type | WCAG 数值、大字阈值、背景回溯；demo `.low-contrast` 可判 | **PASS** — TestContrastProbe；known ratio 测试 |
| 4 | responsive-matrix | 同 finding 不同 viewport 指纹不同；hunt_round 全矩阵 probe | **PASS** — Phase 0 fingerprint 测试 + hunt_round fixtures |
| 5 | visual-diff | snapshot / compare / approve；超阈 finding；无 Pillow skipped | **PASS** — TestVisualDiff |
| 6 | Fix Gate | target_cleared + zero_new + pixel + unit_green 退出码 | **PASS** — TestFixGate |
| 7 | hunt_round | skip-capture fixtures 出 ≥2 类 L3 规则；二次 round 去重 | **PASS** — TestHuntRound |
| 8 | 单测全绿 | `python -m unittest discover -s tests` | **PASS** — 54 tests OK |

## 本地验收脚本（agent 执行）

1. `& $env:MIMO_PYTHON -m unittest discover -s tests -v`
2. 启动 demo；`capture_web.py` 或 playwright-mcp 采集 375/1440
3. `hunt_round.py --run-id run-1`（或 `--skip-capture` + 已有 MANIFEST）
4. 确认 `by_rule` 含 overflow-x / touch-target / overlap-interactive / contrast-text 等
5. 修一条 Confirmed → 重新 capture → `fix_gate.py`
6. 第二轮 hunt_round → `new_count=0` → converge

## 单元测试覆盖（不依赖浏览器）

- Phase 0：init_state / fingerprint / converge / layout overflow-x / validate_report / lock
- Phase 1：capture 矩阵与降级、layout 全规则、contrast、visual_diff、fix_gate、hunt_round 编排
