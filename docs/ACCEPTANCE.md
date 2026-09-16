# Phase 0 验收 DoD

锁定验收项目：`examples/acceptance-demo/`（零依赖 Node 静态站，2 路由）。

## 启动

```powershell
cd examples/acceptance-demo
npm start
# http://127.0.0.1:5173
```

注入缺陷：

| 类型 | 位置 | 期望发现通道 |
|------|------|----------------|
| L3 视觉 | `/` `.cta-row { min-width: 420px }` → 375px `overflow-x` | `layout-geom` |
| a11y 候选 | `/about` `<img>` 无 alt | `a11y-axe` |
| 对比度候选 | `/about` `.low-contrast` | `contrast-type`（Phase 1）/ axe color-contrast |
| 逻辑/测试 | `src/calc.js` `add` 多加 1 | `dynamic`（`npm test` 红） |

## DoD 勾选表

| # | 检查项 | 通过标准 | 状态 |
|---|--------|----------|------|
| 1 | 可 resume | 删会话后读 `state.json` 能接着 quiet_streak | **PASS** — `init_state --resume-summary` 返回 quiet_streak=2 |
| 2 | 迭代收敛 | 验收项目 ≤4 轮满足 §6.2 quiet 后停 | **PASS** — run-1 发现后 run-2 去重，quiet_streak≥2，`converged=true` |
| 3 | L3 视觉 Finding | ≥1 条 `ui-*`，evidence L3，含截图路径 | **PASS** — `overflow-x` @ `/` 375x812，截图 `runs/run-1/captures/home__375x812__viewport.png` |
| 4 | 假阳性 | Confirmed 中无 L3 证据条数 = 0 | **PASS** — 3 条 confirmed 均 evidence.level=L3 |
| 5 | 去重 | 第 2 轮起可统计已见指纹占比 | **PASS** — run-2 `duplicate_rate=1.0`，new_count=0 |
| 6 | REPORT | 范围、modality 摘要、Blind Spots、规则 ID | **PASS** — `validate_report.py` → OK |
| 7 | 降级演示 | 去掉 dev server → L1，Blind Spots 含 web-visual | **PASS** — `runs/run-l1-degrade/REPORT.md`：degrade=L1，Blind Spots 明确「web-visual：整通道未覆盖」 |
| 8 | 无锁冲突 | 双写第二者失败，state.json 不损坏 | **PASS** — 预置 `.lock` 后 `init_state` 退出码 1 且提示 lock exists |

## 本地验收脚本（agent 执行）

1. `& $env:MIMO_PYTHON -m unittest discover -s tests -v`
2. 启动 demo；用 Playwright 采集 375px elements
3. `layout_probe.py` → finding → `fingerprint.py --register`（run-1 新，run-2 known）
4. `converge_check.py` 两轮 quiet → converged
5. 写 `REPORT.md` → `validate_report.py`
6. 停 server；演示 L1（不启动 server 时 bootstrap 后 static/dynamic only）

## 单元测试覆盖（不依赖浏览器）

- init_state / resume / lock 路径
- fingerprint 稳定与 viewport 区分、register 去重
- converge 四条件
- layout_probe overflow-x
- validate_report 必含节
