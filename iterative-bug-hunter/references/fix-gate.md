# Fix Gate（可判定回归门）

1. 只修 **Confirmed**；Deferred 需用户点头。  
2. 一次一修。  
3. 回归门（禁止主观「看起来还行」）：
   - 目标症状消失（同 `rule_id` 在同 route×viewport 不再命中）；
   - 原绿测试仍绿；
   - （Phase 1）对回归矩阵重跑 `layout-geom` + `a11y-axe`，零新增违规；
   - 像素 diff 仅比较影响路由；非目标页面 diff 默认 fail，除非 `intentional_visual_change: true` 且 baseline 已更新。
4. 失败 → 回滚，记 `fix-failed`；同一 bug 失败 ≥ `max_fix_failures` → Deferred。

Phase 0：文档约定 + 报告字段；自动矩阵与像素门在 Phase 1 落地。
