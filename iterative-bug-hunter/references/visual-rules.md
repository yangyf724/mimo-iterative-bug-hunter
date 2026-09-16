# 视觉规则阈值（Phase 0）

| 规则 ID | 判定 | 默认阈值 |
|---------|------|----------|
| `overflow-x` | 根或元素 `scrollWidth > clientWidth + ε`，或元素 right 超出 viewport | ε=2px |

## 判定细节

- document：`document.documentElement.scrollWidth > documentElement.clientWidth + ε`
- 元素：`bbox.x + bbox.w > viewport_width + ε`
- 文本裁切：`scrollWidth > clientWidth` 且非 `ellipsis` / 设计截断
- 指纹含 **viewport**：同一按钮在 375 与 1440 是不同 Finding

## Phase 1+（索引）

`overlap-interactive` (相交>20%) · `zero-size` · `off-canvas` · `touch-target` (44px) · `contrast-text` (4.5:1 / 大字 3:1) · `font-too-small` (12px) · `line-height-tight` · axe 规则映射 · canvas `safe-area-violation` 等。

配置来源：`state.visual_oracle`。
