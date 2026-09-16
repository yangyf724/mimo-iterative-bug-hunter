# 视觉规则阈值（Phase 1）

## layout-geom

| 规则 ID | 判定 | 默认阈值 |
|---------|------|----------|
| `overflow-x` | 根/元素 `scrollWidth > clientWidth + ε`，或元素 right 超出 viewport | ε=2px |
| `text-clip` | 有文本节点 `scrollWidth > clientWidth + ε` 且非 `ellipsis` / `clip-intentional` | ε=2px |
| `overlap-interactive` | 两 interactive bbox 相交面积 / min(面积) > 阈值 | 0.2 |
| `zero-size` | 有内容（text 或 interactive）且 w<1 或 h<1 | 1px |
| `off-canvas` | interactive bbox 完全在 viewport 外 | — |
| `touch-target` | interactive 且 min(w,h) < 阈值 | 44px |

脚本：`scripts/layout_probe.py`。根节点（html/body）只参与 page-level `overflow-x`，不参与其他规则。

## contrast-type

| 规则 ID | 判定 | 默认 |
|---------|------|------|
| `contrast-text` | 前景/背景对比度 < min；大字（≥24px 或 ≥18.66px bold）用 large 阈值 | 4.5 / 3.0 |
| `font-too-small` | computed fontSize < 阈值（跳过 zero-size 节点） | 12px |
| `line-height-tight` | line-height/fontSize < 阈值 且多行文本 | 1.2 |

脚本：`scripts/contrast_probe.py`。背景解析：元素 `backgroundColor` → 祖先 depth 更浅的不透明色 → 列表中任一不透明色 → 白色（`background_assumed: true`）。对比度按 WCAG 2.x 相对亮度公式。

## visual-diff

| 规则 ID | 判定 | 默认 |
|---------|------|------|
| `visual-diff` | 与基线像素 diff_ratio > 阈值，或尺寸不一致 | 0.01 |

脚本：`scripts/visual_diff.py`。基线：`.bug-hunter/baselines/web/{route_slug}__{WxH}.png`。Pillow 不可用时 `status: skipped`（记 Blind Spot，不假装通过）。有意变更：`visual_diff.py approve` 写入 `baselines/approvals.jsonl`。

## responsive-matrix

不单独发明规则：对 `routes × viewports` 重复 layout-geom / contrast-type。指纹已含 viewport → 同一逻辑问题在不同断点是不同 Finding。

## 配置来源

`state.visual_oracle`（`init_state.py` Phase 1 默认值含 `overlap_ratio`、`line_height_min_ratio`、`visual_diff_threshold`）。

## Phase 2+（索引）

axe 规则映射 · canvas `safe-area-violation` / `export-mismatch` / `z-order-occlusion` / `low-res-asset` / `aspect-distort` 等。
