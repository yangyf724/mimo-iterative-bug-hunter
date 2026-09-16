# 采集协议（Capture Protocol）— Phase 0

1. **环境**：优先 Playwright / playwright-mcp；dev server 由用户启动或 skill 请求启动，记录 base_url。
2. **路由集**：`state.surfaces.web.routes`；默认补全关键链接，设上限。
3. **Viewport 矩阵**：至少 `375x812`、`1440x900`。
4. **每页产物**（写入 `runs/run-N/captures/`）：
   - `full.png` + `viewport.png`
   - `elements.json`：selector、bbox、text、scrollWidth/clientWidth、必要 computed style
   - `ax.json`：Accessibility tree
   - `console.json`：error/warning
5. **稳定化**：network idle / 显式 wait；`prefers-reduced-motion: reduce` 禁动画。
6. **认证**：storage_state；未授权页跳过并记 Blind Spots。
7. **MANIFEST**：`runs/run-N/captures/MANIFEST.json` 记录产物相对路径，Confirm 引用。

## Playwright 抽取 overflow 所需字段（供 layout_probe）

对每个关键元素及 document：

```json
{
  "selector": "button.cta",
  "route": "/",
  "viewport": "375x812",
  "interactive": true,
  "bbox": {"x": 340, "y": 620, "w": 120, "h": 48},
  "scrollWidth": 120,
  "clientWidth": 102,
  "text_overflow": "visible"
}
```

document 根节点：

```json
{
  "selector": "html",
  "route": "/",
  "viewport": "375x812",
  "scrollWidth": 393,
  "clientWidth": 375,
  "bbox": {"x": 0, "y": 0, "w": 375, "h": 812}
}
```

## 画布（Phase 2 索引）

统一 item：`id`, `export_size`, `source`；可选 `render_png`, `spec.safe_inset_pct`。kind：`scene-json` | `html-canvas-app` | `figma-export`。
