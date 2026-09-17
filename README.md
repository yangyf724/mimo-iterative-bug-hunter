# Mimo Iterative Bug Hunter

全模态迭代抓 BUG 的 MiMoCode skill 源码仓：代码通道 + Web 视觉通道 + 画布通道，指纹去重、跨模态确认、quiet 四条件收敛。

<!-- github-sync:begin -->
**Version:** 0.4.0-dev  
**Last sync:** 2026-09-17
<!-- github-sync:end -->

## 仓库定位

- `DESIGN.md` — 设计真源（全模态 taxonomy、策略库、收敛与 Fix Gate）
- `iterative-bug-hunter/` — skill 本体（SKILL.md + scripts + references + locales）
- `examples/acceptance-demo/` — Phase 0–2 本地验收 demo（双路由 + overflow / touch-target / overlap / contrast / 死链 / 无反馈 submit / canvas 场景 / flows）
- `examples/second-project/` — Phase 3 第二验收 demo（泛化：`/shop` `/contact` + 不同缺陷组合）
- `docs/ACCEPTANCE.md` — Phase 0–3 DoD 勾选
- `docs/compose/spec/` — 各 Phase feature 文档
- `tests/` — 状态机与探针单元测试（stdlib unittest）

## 快速开始

```powershell
# 单元测试
$env:MIMO_PYTHON -m unittest discover -s tests -v

# Phase 2 fixture E2E（无浏览器）
$env:MIMO_PYTHON tests/phase2_fixture_e2e.py

# 在目标项目初始化状态
& $env:MIMO_PYTHON iterative-bug-hunter/scripts/init_state.py --root <project> --routes / /about

# 启动验收 demo
cd examples/acceptance-demo
npm start   # http://127.0.0.1:5173

# Phase 1：采集 + 单轮 hunt（需 Playwright；否则用 MCP 采集后 --skip-capture）
& $env:MIMO_PYTHON ../../iterative-bug-hunter/scripts/capture_web.py --root . --run-id run-1
& $env:MIMO_PYTHON ../../iterative-bug-hunter/scripts/hunt_round.py --root . --run-id run-1 --skip-capture --dynamic-cmd "npm test"

# Phase 2：分片采集 / ux flows / canvas
& $env:MIMO_PYTHON ../../iterative-bug-hunter/scripts/capture_web.py --root . --run-id run-1 --shard 0/2
& $env:MIMO_PYTHON ../../iterative-bug-hunter/scripts/hunt_round.py --root . --run-id run-2 --skip-capture `
  --flows .bug-hunter/flows --canvas-items canvas/poster.scene.json

# Phase 3：路由发现 / FP 白名单 / 导出 / CI
& $env:MIMO_PYTHON ../../iterative-bug-hunter/scripts/discover_routes.py --root . --seed / --html public/index.html --write
& $env:MIMO_PYTHON ../../iterative-bug-hunter/scripts/export_report.py --root .
& $env:MIMO_PYTHON ../../iterative-bug-hunter/scripts/ci_gate.py --root ../..
```

## 安装为 MiMo Desktop skill（可选）

将 `iterative-bug-hunter/` 复制到：

- 全局：`~/.config/mimocode/skills/iterative-bug-hunter/`
- 项目：`<project>/.mimocode/skills/iterative-bug-hunter/`

新开对话后生效。

## License

MIT
