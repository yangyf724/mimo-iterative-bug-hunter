# 成功度量（观测记录）

阶段说明：Phase 0/1 无历史数据，表为目标带宽，不是承诺。每完成一个验收项目把观测值记入本文件。

## 目标带宽

| 指标 | 目标 | 采集 |
|------|------|------|
| 代码确认率 | ≥40% | confirmed/(confirmed+rejected) |
| 视觉 L3 确认率 | ≥50% | 同上，modality=web-visual 且 L3 |
| VLM 候选→Confirmed | 10%–30% | Phase 2 |
| 收敛轮数（L3） | 3–8 | state.run_count |
| 修复回归率 | ≥80% | fixed 且无 fix-failed |
| 跨轮重复 Finding | 第 3 轮起→0 | fingerprints 命中率 |
| Phase 0 DoD | 8/8 | docs/ACCEPTANCE.md |

## 观测日志

| 日期 | 项目 | runs | confirmed (code/wv) | rejected | duplicate_rate | 备注 |
|------|------|-----:|---------------------|----------|----------------|------|
| | | | | | | |
| 2026-09-18 | examples/second-project | 1 (fixture) | 0/0（hunt 不自动 Confirm） | 0 | 0.05 | L4；new=18；rule 命中 overflow-x/dead-link/missing-feedback/touch-target/contrast-text/ux-flow-step/safe-area/export-mismatch/low-res/aspect/dynamic-fail；backend=fixture-from-html-css（无 Playwright） |
