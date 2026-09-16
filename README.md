# Mimo Iterative Bug Hunter

全模态迭代抓 BUG 的 MiMoCode skill 源码仓：代码通道 + Web 视觉通道，指纹去重、跨模态确认、quiet 四条件收敛。

<!-- github-sync:begin -->
**Version:** 0.1.0  
**Last sync:** 2026-09-16
<!-- github-sync:end -->

## 仓库定位

- `DESIGN.md` — 设计真源（全模态 taxonomy、策略库、收敛与 Fix Gate）
- `iterative-bug-hunter/` — skill 本体（SKILL.md + scripts + references + locales）
- `examples/acceptance-demo/` — Phase 0 本地验收 demo（双路由 + 注入 overflow-x / 测试失败）
- `docs/ACCEPTANCE.md` — Phase 0 DoD 勾选
- `tests/` — 状态机脚本单元测试（stdlib unittest）

## 快速开始

```powershell
# 单元测试
$env:MIMO_PYTHON -m unittest discover -s tests -v

# 在目标项目初始化状态
& $env:MIMO_PYTHON iterative-bug-hunter/scripts/init_state.py --root <project> --routes / /about

# 启动验收 demo
cd examples/acceptance-demo
npm start   # http://127.0.0.1:5173
```

## 安装为 MiMo Desktop skill（可选）

将 `iterative-bug-hunter/` 复制到：

- 全局：`~/.config/mimocode/skills/iterative-bug-hunter/`
- 项目：`<project>/.mimocode/skills/iterative-bug-hunter/`

新开对话后生效。

## License

MIT
