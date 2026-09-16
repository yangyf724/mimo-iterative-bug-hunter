# 策略库（Phase 0 子集 + 全表指针）

modality 仅三值：`code` | `web-visual` | `canvas`。调度与统计用 modality；策略 ID 决定本轮 rule 集。

## Phase 0 默认策略集

| ID | modality | 动作 | Oracle | 成本 |
|----|----------|------|--------|------|
| `static` | code | typecheck / lint / 安全扫描 | 工具退出码 | 低 |
| `dynamic` | code | 跑测试、复现失败栈 | 测试断言 | 中 |
| `capture-baseline` | web-visual | 多 viewport 截图 + DOM/AX | 采集成功 | 低 |
| `layout-geom` | web-visual | bbox：当前仅 `overflow-x` | 几何规则 | 中 |
| `a11y-axe` | web-visual | axe-core（若可安装/npx） | axe 违规 | 低 |

## 轮换规则

1. 首轮（degrade≥L2）：`static` + `dynamic` + `capture-baseline` + `a11y-axe` + `layout-geom`。
2. 之后：cursor 轮换；优先上轮有新发现的 modality。
3. `quiet_streak ≥ 1`：加压 `responsive-matrix` / `ux-flow` / `canvas-safe` / `vlm-audit`（若 degrade 允许）。
4. **禁止连续两轮完全相同策略集**。

## Degrade Ladder

| 级别 | 条件 | 允许策略 |
|------|------|----------|
| L0 | 无法开工 | （停止） |
| L1 | 有源码，无浏览器 | `static` `dynamic` `generate` `structural` `meta-test` |
| L2 | 可开页，无 axe | L1 + `capture-baseline` `layout-geom` `contrast-type` `responsive-matrix` |
| L3 | L2 + axe | L2 + `a11y-axe` |
| L4 | L3 + 画布 | L3 + `canvas-safe` `canvas-asset` `vlm-audit` `ux-flow` |

只升不隐式降：中途失败可本轮降级，必须写入 summary 与 REPORT Blind Spots。

## Phase 1+（未实现，仅索引）

`generate` `structural` `speculative` `meta-test` `visual-diff` `contrast-type` `responsive-matrix` `ux-flow` `canvas-safe` `canvas-asset` `vlm-audit` — 完整配方见 DESIGN.md §5.1，实现随 Phase 1/2 扩展本文件。

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
  "evidence": {"level":"L2|L3|L4","screenshot":"...","rule_id":"...","repro":"..."},
  "detected_by": "static|layout-geom|...",
  "status": "candidate"
}
```
