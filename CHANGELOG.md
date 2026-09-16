# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [SemVer](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-09-16

### 摘要
Phase 1 全模态成型：多 viewport 采集、完整 layout-geom / contrast-type / responsive-matrix、像素 visual-diff 与可判定 Fix Gate、hunt_round 单轮编排。

### Added
- `capture_web.py` — routes×viewports 采集，MANIFEST + elements schema；Playwright Python/Node 后端，不可用时 exit 3
- `layout_probe.py` 扩展 — `text-clip` / `overlap-interactive` / `zero-size` / `off-canvas` / `touch-target`
- `contrast_probe.py` — WCAG `contrast-text` / `font-too-small` / `line-height-tight`，背景 depth 回溯
- `visual_diff.py` — baseline snapshot / 像素 compare / intentional approve（approvals.jsonl）
- `fix_gate.py` — target_cleared + zero_new_layout + pixel_gate + unit_green，写 fix-verify.json
- `hunt_round.py` — 单轮 capture→probe→register→summary→converge 评估
- `init_state.py` Phase 1 默认值 — overlap_ratio / line_height_min_ratio / visual_diff_threshold
- demo 注入 touch-target / overlap-interactive / zero-size 缺陷
- `tests/test_phase1_scripts.py` + `tests/phase1_fixture_e2e.py` — 54 unit + fixture E2E

### Changed
- `references/` capture-protocol / visual-rules / fix-gate / strategies 更新为 Phase 1 契约
- `SKILL.md` 主循环指向 capture_web / hunt_round / fix_gate
- `docs/ACCEPTANCE.md` 增补 Phase 1 DoD 8 项

## [0.1.0] - 2026-09-16

### 摘要
Phase 0：可安装的 iterative-bug-hunter skill 骨架，能在本地 demo 上完成扫描 → L3 确认 → 指纹去重 → quiet 收敛 → 带盲区的 REPORT。

### Added
- `LICENSE` — MIT 许可证 → 仓库可被他人合法复用与分发
- `iterative-bug-hunter/SKILL.md` — 触发、Scope、主循环、quiet 四条件、Confirm 门槛与用户合同 → agent 可按协议迭代抓 bug 而非一次 lint 汇总
- `iterative-bug-hunter/scripts/init_state.py` — O_EXCL 单写锁 + state/fingerprints/目录树初始化与 resume → 多会话安全、可断点续跑
- `iterative-bug-hunter/scripts/fingerprint.py` — DESIGN §3.2 粗粒度指纹注册与去重 → 同 viewport 同问题跨轮不重复计数，1px 采集噪声不伪造新 bug
- `iterative-bug-hunter/scripts/converge_check.py` — §6.2 quiet 四条件判定 → 明确「何时停」并支持 K 轮收敛
- `iterative-bug-hunter/scripts/layout_probe.py` — Phase 0 overflow-x 几何规则 → 375px 下可产出 L3 视觉 Finding
- `iterative-bug-hunter/scripts/validate_report.py` — REPORT 必含节校验（含 rule_id）→ 报告结构可机器验收
- `iterative-bug-hunter/references/` — 策略库、采集/确认协议、视觉规则、Fix Gate、报告模板 → 细节不塞进 SKILL.md
- `examples/acceptance-demo/` — 零依赖双路由站 + 注入 overflow 与 add off-by-one → Phase 0 DoD 可复现
- `docs/ACCEPTANCE.md` / `docs/METRICS.md` — DoD 8 项勾选与指标观测表 → 验收与后续度量有落点
- `tests/test_phase0_scripts.py` — 23 个单元测试覆盖状态机/指纹/收敛/探针/锁 → 回归安全网
