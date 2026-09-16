---
name: iterative-bug-hunter
description: >
  全模态迭代抓 BUG 直到收敛：代码通道（静态/动态/生成式）+ 视觉通道
  （布局几何、对比度、axe 无障碍、响应式矩阵、UX 状态）+ 画布通道
  （安全区/导出/层级/资源），指纹去重、跨模态确认、可选修复+回归门。
  Use when: 抓BUG / 找bug / 修到没有 / bug hunt / hunt until clean /
  网页视觉问题 / 布局炸了 / 无障碍 / 画布设计检查 / UI不对 / 对比度 /
  响应式问题 / design QA / visual bug。
  Do NOT use for one-shot lint 汇总, pure feature dev, or when no
  runnable app/assets and user only wants static code review.
---

# Iterative Bug Hunter

对当前项目持续抓 BUG，直到「在约定范围内无新增确认 BUG」。代码 + 视觉（Web）通道；Phase 0 含最小布局几何 `overflow-x` 与 axe 探测入口。

## 触发

用户明确要求：抓 BUG / 找 bug / hunt until clean / 视觉问题 / design QA / 修到没有，且目标是当前项目或指定本地 Web 应用。

**不要**在仅需一次 lint 汇总、纯写功能、或用户只想要静态 code review 且无任何可运行应用时启用本 skill。

## Scope（开始前必须确认）

用 `question` 工具或直接从仓库/用户已给信息收集；缺省值写入 `state.json`：

| 项 | 默认 | 说明 |
|----|------|------|
| mode | `hunt-and-fix` | 或 `hunt-only` |
| modalities | `code, web-visual` | 有画布资产再加 `canvas` |
| routes | `/`, `/about` 或探测 | 以 `state.surfaces.web.routes` 为准 |
| viewports | `375x812`, `1440x900` | 指纹区分 viewport |
| base_url | 用户 dev server | 无则先尝试探测，失败进 L1 |
| K | 2 | `required_quiet_streak` |
| max_runs | 20 | 预算护栏 |

## 降级阶梯（摘要）

| 级别 | 条件 | 允许 |
|------|------|------|
| L0 | 无法识别项目/无工具 | 立即停止并报告 |
| L1 | 有源码，无浏览器/dev server | 仅 code 通道 |
| L2 | 可开页，暂无 axe | L1 + capture / layout-geom / contrast-type / responsive-matrix |
| L3 | L2 + axe-core | 默认 Web 全开 |
| L4 | L3 + 画布场景/导出 + 规范 | 全模态 |

细节与完整策略表：[`references/strategies.md`](references/strategies.md)。探测失败必须记入 Blind Spots，禁止静默跳过。

## 主循环

1. **Bootstrap** — `scripts/init_state.py`（已有 `state.json` 则 resume：`--resume-summary`）。
2. **Probe** — 探测 dev server / 路由可达性，写 `degrade_level`。
3. **Plan** — 选策略集；禁止连续两轮完全相同；quiet_streak≥1 时加压。
4. **Capture** — L≥2 时按 [`references/capture-protocol.md`](references/capture-protocol.md) 采集截图/DOM/AX。
5. **Execute** — 跑策略；写 `runs/run-N/findings/raw/`。
6. **Fingerprint** — `scripts/fingerprint.py --register` 去重。
7. **Confirm** — 按 [`references/confirm-protocol.md`](references/confirm-protocol.md)，L3/L4 才 Confirmed。
8. **Fix（可选）** — 仅 Confirmed；回归门见 [`references/fix-gate.md`](references/fix-gate.md)。
9. **Converge** — `scripts/converge_check.py` 实现 quiet 四条件。
10. **Report** — 按 [`references/report-template.md`](references/report-template.md) 写 `.bug-hunter/REPORT.md`。

### quiet 四条件（K 默认 2）

本轮 quiet 当且仅当：

1. 执行了 ≥1 条「当前 degrade 允许」的策略；
2. 策略集覆盖 `modalities_enabled` 中每个**仍可用**的 modality；
3. 新 Confirmed == 0；
4. 无新回归（功能失败 / 视觉 diff 超阈 / 新 axe 违规）。

违反任一条则 `quiet_streak` 清零。`quiet_streak ≥ K` 且预算未耗尽 → 收敛。

## Confirm 门槛

- **L3**：截图或元素几何 + 可定位 selector/bbox + 复现（route×viewport）+ 机器规则命中（axe id / 溢出像素 / 对比度数值）→ 可 Confirmed。
- **L4**：L3 + 用户规范条文 → 优先 Confirmed。
- 纯审美 / 无规则 VLM 主观 → **Deferred**（`allow_subjective=false` 时不得 Confirmed）。

分类枚举与指纹字段：见 DESIGN.md §1.4 / §3.2；规则阈值：[`references/visual-rules.md`](references/visual-rules.md)。

## 状态与并发（必须遵守）

- 只在目标项目 cwd 的 `.bug-hunter/` 读写。
- **单写者**：只有 main agent 写 `state.json` / `fingerprints.json` / `bugs/**`。
- 写 `state.json` 前必须持有 `.bug-hunter/.lock`（`O_EXCL`）；失败重试 3 次后中止本轮。
- 禁止双会话对同一项目同时跑本 skill。

## 用户合同

> 我会用代码分析 + 浏览器截图/DOM/无障碍树（以及画布场景）反复扫你的项目：能机器判定的用规则和数字说话，拿不准的先当候选；能修的修完会做功能与视觉回归；连续两轮（在当前能力级别下）扫不出新的确认问题我就停，并明确告诉你扫过哪些页面和分辨率、降到了哪一档能力、还有哪些盲区。

## 停止条件

- `converged == true`（quiet 四条件连续 K 轮）；
- 或达到 `max_runs` / 墙钟 / 连续 fix 失败护栏；
- 或 degrade=L0。

停止时 REPORT 必须写清：已扫 route×viewport、degrade 级别、Blind Spots、确认/拒绝/暂缓计数。

## 禁止

- 把 DESIGN.md 整篇塞进本文件；
- 无锁覆盖 `state.json`；
- 未授权页面截图当作 bug；
- 纯主观审美直接 Confirmed；
- 静默降级不记 Blind Spots。
