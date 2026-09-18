---
feature: real-acceptance-install
status: delivered
updated: 2026-09-18
branch: feat/real-acceptance
commits: ced8c04..HEAD
---

# 真机验收 + Skill 安装

## Report

**What was built** — 将 `iterative-bug-hunter/` 安装到 `~/.config/mimocode/skills/iterative-bug-hunter/`（复制、UTF-8 校验）。在 `examples/second-project` 启动 5174 服务，`init_state` + `discover_routes --write` 写入 `/` `/shop` `/contact`。本机无 Playwright（exit 3），按协议用从真实 HTML/CSS 重建的 elements fixtures + live server 跑 `hunt_round`：19 findings / 18 new，命中 overflow-x、dead-link、missing-feedback、touch-target、contrast-text、ux-flow-step、safe-area、export-mismatch、dynamic-fail 等；L3→L4（canvas-items）。`export_report.py` schema v1 ok。观测写入 `docs/METRICS.md`；ACCEPTANCE 增真机验收表。

**Verification** — HTTP 200 @5174；discover routes 含 shop/contact；hunt summary by_rule 见上；export ok；`python -m unittest discover -s tests` 保持全绿。

**Journey log** —
1. worktree 仍禁止，沿用主 checkout 分支。
2. PowerShell `$HOME` 只读 → 改用 Python 脚本写 fixtures。
3. 无 Playwright 时不假装 capture 成功：MANIFEST `backend=fixture-from-html-css`。
4. hunt_round 本身不 Confirm，故 run-1 quiet 不代表「零 bug」。
5. skill 安装需新开对话才会被 MiMo 重载。

## [S1] Problem

Phase 0–3 已在 `main`（v0.4.0）交付并通过 CI/单测，但：
1. skill 未安装到本机 MiMoCode 扫描路径，无法在新对话中被触发；
2. 第二验收项目 `examples/second-project/` 尚未在真机上跑过完整 hunt，`docs/METRICS.md` 无观测记录；
3. 缺少「安装路径正确 + hunt 在 second-project 上产出可确认 finding」的可复现验收。

## [S2] Design

### Workspace override

环境仍禁止 `git worktree add`（共享 ref store）。实现继续在主 checkout 分支 `feat/real-acceptance` 上进行。

### 安装契约

- 目标：`C:\Users\<user>\.config\mimocode\skills\iterative-bug-hunter\`
- 动作：从仓库 `iterative-bug-hunter/` **复制目录**（不用符号链接），覆盖前可先备份同名目录为 `.bak-<ts>`（若存在）。
- 必含：`SKILL.md` frontmatter `name=iterative-bug-hunter`、`scripts/`、`references/`、`locales/`
- 生效：新开对话；本会话不保证重载。

### 验收 hunt 契约（second-project）

1. 启动 `examples/second-project`（`node server.js`，默认 `http://127.0.0.1:5174`）。
2. 在 demo 根下 `init_state.py --force`：routes `/` `/shop` `/contact`，viewports `375x812` `1440x900`，base_url 5174。
3. `discover_routes.py` 校验 package.json/HTML 能列出 `/shop` `/contact`。
4. 采集：
   - 若 Playwright 可用 → `capture_web.py` + `hunt_round.py`；
   - 否则用手工/fixtures elements（沿用脚本契约）并在 METRICS/Blind Spots 标明 `backend: unavailable` 或 fixture 路径。
5. 期望至少命中：`overflow-x`、`dead-link`、`missing-feedback`、`touch-target`、`contrast-text` 中的 ≥3 类（fixture 路径）；真浏览器路径尽力覆盖，失败进 Blind Spots。
6. 可选：`export_report.py` 产出 schema v1。
7. 观测值写入 `docs/METRICS.md` 新行；ACCEPTANCE 增「真机验收」小节勾选。

### Out of relation to code changes

- 本次**不**改探针判定逻辑；hunt 若发现 skill 缺陷，单独立项修复。
- `.bug-hunter/` 仍 gitignore，不提交运行时截图/状态。
- 不自动修改用户全局 AGENTS.md。

## [S3] Out of Scope

- Phase 4+ 新通道
- 把 skill 发到 npm/marketplace
- 对用户其它真实项目的 hunt（除非用户另指定）
- 修改 quiet/指纹算法

## Tasks

- [x] T1: 本 spec + 分支 `feat/real-acceptance` — acceptance: 文档存在且 status=designed (covers: S2)
- [x] T2: 安装 skill 到 `~/.config/mimocode/skills/iterative-bug-hunter/` — acceptance: 目录含 SKILL.md/scripts/references/locales (covers: S2)
- [x] T3: 启动 second-project + init_state + discover_routes — acceptance: server 可访问；state routes 含 shop/contact (covers: S2)
- [x] T4: 跑 hunt（playwright 或 fixture）+ export — acceptance: summary 含≥3 类期望 rule 或明确 Blind Spots；METRICS 有记录 (covers: S1;S2)
- [x] T5: 更新 ACCEPTANCE/METRICS/README + commit — acceptance: 文档一致；分支上有提交 (covers: S1;S2; depends: T2–T4)
