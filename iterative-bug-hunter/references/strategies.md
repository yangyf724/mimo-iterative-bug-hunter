# 策略库（Phase 1）

modality 仅三值：`code` | `web-visual` | `canvas`。调度与统计用 modality；策略 ID 决定本轮 rule 集。

## Phase 1 策略集

| ID | modality | 动作 | Oracle | 成本 | 脚本 |
|----|----------|------|--------|------|------|
| `static` | code | typecheck / lint / 安全扫描 | 工具退出码 | 低 | agent |
| `dynamic` | code | 跑测试、复现失败栈 | 测试断言 | 中 | `hunt_round.py --dynamic-cmd` |
| `capture-baseline` | web-visual | 多 viewport 截图 + elements/AX | 采集成功 | 低 | `capture_web.py` |
| `layout-geom` | web-visual | overflow-x / text-clip / overlap / zero-size / off-canvas / touch-target | 几何规则 | 中 | `layout_probe.py` |
| `contrast-type` | web-visual | contrast-text / font-too-small / line-height-tight | WCAG 公式 | 低 | `contrast_probe.py` |
| `responsive-matrix` | web-visual | routes×viewports 重复 layout+contrast | 几何/对比度 | 中 | `hunt_round.py` |
| `visual-diff` | web-visual | 与 baseline 像素 diff | diff_ratio 阈值 | 中 | `visual_diff.py` |
| `a11y-axe` | web-visual | axe-core（若可安装/npx） | axe 违规 | 低 | agent / MCP |

## 单轮编排

```powershell
& $env:MIMO_PYTHON iterative-bug-hunter/scripts/hunt_round.py --root <project> --run-id run-1 `
  [--skip-capture] [--captures DIR] [--dynamic-cmd "npm test"] [--write-candidates]
```

步骤：（可选 capture）→ probe MANIFEST 全矩阵 → register 指纹 → `runs/run-N/summary.json` → converge 评估。**不**自动 Confirm/修代码。

## 轮换规则

1. 首轮（degrade≥L2）：`static` + `dynamic` + `capture-baseline` + `layout-geom` + `contrast-type`（有 axe 再加 `a11y-axe`）。
2. 之后：cursor 轮换；优先上轮有新发现的 modality。
3. `quiet_streak ≥ 1`：加压 `visual-diff` / `responsive-matrix` / Phase 2 通道。
4. **禁止连续两轮完全相同策略集**。

## Degrade Ladder

| 级别 | 条件 | 允许策略 |
|------|------|----------|
| L0 | 无法开工 | （停止） |
| L1 | 有源码，无浏览器 | `static` `dynamic` `generate` `structural` `meta-test` |
| L2 | 可开页，无 axe | L1 + `capture-baseline` `layout-geom` `contrast-type` `responsive-matrix` `visual-diff` |
| L3 | L2 + axe | L2 + `a11y-axe` |
| L4 | L3 + 画布 | L3 + `canvas-safe` `canvas-asset` `vlm-audit` `ux-flow` |

只升不隐式降：中途失败可本轮降级，必须写入 summary 与 REPORT Blind Spots。

**已有 captures 时**：`hunt_round.py --skip-capture` 或 MANIFEST 存在则直接 probe（视为 web-visual 已演练）。

## Phase 2+（未实现，仅索引）

`generate` `structural` `speculative` `meta-test` `ux-flow` `canvas-safe` `canvas-asset` `vlm-audit` — 完整配方见 DESIGN.md §5.1。

## 策略输出约定

每条 raw finding 至少包含：

```json
{
  "title": "...",
  "modality": "code|web-visual|canvas",
  "category": "...",
  "severity": "high|medium|low",
  "statement": "期望 vs 实际",
  "location": {"surface":"web","route":"/","viewport":"375x812","selector":"..."},
  "metrics": {},
  "rule_id": "overflow-x",
  "core_assertion_digest": "overflow-x|horizontal-overflow",
  "evidence_level_target": "L3",
  "detected_by": "layout-geom|contrast-type|visual-diff|dynamic",
  "status": "candidate"
}
```
