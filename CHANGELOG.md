# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [SemVer](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-16

### 摘要
Phase 0：可安装的 iterative-bug-hunter skill 骨架，能在本地 demo 上完成扫描 → L3 确认 → 指纹去重 → quiet 收敛 → 带盲区的 REPORT。

### Added
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
