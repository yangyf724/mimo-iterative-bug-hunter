---
feature: skill-config-opt
status: delivered
updated: 2026-09-18
branch: feat/skill-config-opt
commits: c2cb226..working-tree-uncommitted # git checkout/commit blocked in child session; see Journey log
---

# Skill Config Optimization (iterative-bug-hunter)

## Report

**What was built** — 按 skill-creator 合规与优化标准，重写 `iterative-bug-hunter` 的 SKILL.md frontmatter（去掉 YAML `>` 折叠指示符以免被 validator 判为 XML 尖括号；补全 `compatibility`；保留 Use when / Do NOT 负触发）。正文新增 `## Important`、`## Examples`（含不应触发负例）、`## Troubleshooting`，并把此前 orphan 的 `references/ux-flow.md`、`canvas-protocol.md`、`export-schema.md` 挂到主循环/Scope。技能以目录复制方式安装到全局 `~/.config/mimocode/skills/iterative-bug-hunter/` 与项目级 `universal-agent-engine/.mimocode/skills/iterative-bug-hunter/`，与源仓 `iterative-bug-hunter/` 三路径 SKILL.md 哈希一致，且无 `__pycache__`/`*.pyc`。

**Verification** —
- `validate_skill.py` 源 / 全局 / UAE 三路径：`PASS: 0 error(s), 0 warning(s)`
- 源仓 `$env:MIMO_PYTHON -m unittest discover -s tests`：108 tests OK
- 安装目录 scripts `py_compile`：OK；复验后已删除 `__pycache__`，`pyc_count=0`
- 完整树：每路径 `scripts=19`、`references=14`、locales OK
- SKILL.md 哈希三路径 MATCH：`DA4190817DE5723BF4AE22B8156BFC9979D166499618CBE378E62A411D638760`
- 独立 review：AC1/2/4/5/6 PASS；AC3 的 `__pycache__` critical 已修复并复验

**Journey log** —
1. skill-creator `validate_skill.py` 把 YAML frontmatter 里的字面 `>`（折叠指示符）当成 XML 禁字符——合规解法是改技能内容用无指示符缩进续行，而不是改校验器。
2. 本会话 `git worktree add` / `git checkout` 被 isolated child session 拦截 → Workspace override：主 checkout 文件直写 + 双路径安装；**源仓变更尚未提交**。
3. 对安装路径跑 `py_compile` 会污染 `__pycache__`，validator 不报错；安装验收必须单独查缓存目录。
4. 审查 critical 与“validator PASS”不是同一门禁：内容合规 PASS ≠ 安装目录干净。
5. 生效仍需新开对话；本会话技能目录已可见但内容以磁盘副本为准。

## [S1] Problem

技能 `iterative-bug-hunter` 已安装到全局路径且本会话可见，但存在配置与规范缺口：

1. **skill-creator validator FAIL**：frontmatter 使用 YAML 折叠符 `description: >`，校验器将 `>` 判定为禁止的 XML 尖括号（`validate_skill.py` 对 frontmatter 块做字面 `[<>]` 检查）。技能无法通过官方 skill 规范门禁。
2. **审查优化缺口**：`compatibility` 缺失；`references/ux-flow.md`、`canvas-protocol.md`、`export-schema.md` 在盘上存在但未从 SKILL.md body 链接；缺 skill-creator 推荐的 `## Examples` / `## Troubleshooting`；关键并发/禁止规则埋在正文中后部。
3. **安装面**：全局副本与源仓一致，但校验 FAIL 未修复；目标项目 `universal-agent-engine` 尚无 `.mimocode/skills/iterative-bug-hunter/` 项目级副本；重装需清理 `__pycache__`。

## [S2] Design

### Workspace override

环境禁止 `git worktree add` 与会话内 `git checkout`（共享 ref store / isolated child session）。实现落在源仓主 checkout 工作区文件上；**提交/开分支需用户在主 checkout 手动完成**。不嵌套第二个 worktree。

### 标准与冲突解决

| 维度 | 准据 | 说明 |
|------|------|------|
| 过程 | compose-next | Grill → Workspace → Spec → Implement → Verify → Review → Finalize |
| 产物格式 / 合规 | skill-creator | frontmatter、目录、validator、触发词、body 结构 |
| 设计真源 | 仓库 `DESIGN.md` | 不改 quiet/指纹/探针算法；不把 DESIGN 塞进 SKILL.md |
| MiMo 安装路径 | 全局 AGENTS.md | 只装 `~/.config/mimocode/skills/` 与 `<project>/.mimocode/skills/` |

### Frontmatter 合规契约

- `name: iterative-bug-hunter`（不变，kebab-case，与目录一致）
- `description`：**禁止** YAML 折叠/块指示符 `>` `<`；用无指示符的续行缩进或单行文本；保留 WHAT + Use when 触发词 + Do NOT 负触发；长度 < 1024
- 新增 `compatibility`：声明 Python 3.10+（bundled scripts）；web 采集需 Playwright 或 playwright-mcp；axe-core 可选（L3）；canvas scene 可选（L4）；1–500 字符
- 不设置 `disable-model-invocation`（保持 agent 可主动触发）
- `locales/zh-CN.json`、`en-US.json` 保持 `displayName`/`brief` 字段不变（已合规）

### SKILL.md body 优化契约

1. 文首增加短 `## Important`：必须遵守项指针（`.bug-hunter/` 单写者 + 锁、禁止静默降级、禁止把 axe unavailable 当通过），细节仍在原章节。
2. 主循环 Hunt / 相关步骤补全 orphan 引用链接：
   - `references/ux-flow.md`（Hunt / flows）
   - `references/canvas-protocol.md`（Hunt / canvas）
   - `references/export-schema.md`（Report / export）
3. 新增 `## Examples`：≥2 条 Trigger → Steps → Result（含一个不应触发的负例）。
4. 新增 `## Troubleshooting`：覆盖无 dev server、无 Playwright、锁冲突、axe unavailable、quiet 误收敛。
5. **不**把阈值/脚本参数正文化；**不**重写收敛算法；body 保持 ≤ ~5000 词。

### 安装契约

| 目标 | 路径 | 动作 |
|------|------|------|
| 全局 | `C:\Users\<user>\.config\mimocode\skills\iterative-bug-hunter\` | 从源仓 `iterative-bug-hunter/` 复制覆盖；排除 `__pycache__`/`*.pyc` |
| 项目 | `D:\BaiduSyncdisk\project\universal-agent-engine\.mimocode\skills\iterative-bug-hunter\` | 同上复制；创建 `.mimocode/skills/` 若不存在 |

- 复制**目录**，不用符号链接（与 AGENTS.md / 既往 install spec 一致）。
- 源真源：`D:\BaiduSyncdisk\project\Mimo Iterative Bug Hunter\iterative-bug-hunter\`。
- 生效：新开对话；本会话不保证重载。
- 安装后两路径 + 源路径的 `SKILL.md` 前 N 行哈希一致；validator 对源路径与两个安装路径均 PASS。

### 验收契约（Verify）

1. `validate_skill.py` 对源 / 全局 / 项目三路径 → `PASS: 0 error(s)`（warning 允许但应尽量 0）。
2. 源仓 ` $env:MIMO_PYTHON -m unittest discover -s tests ` 全绿（或标记 PRE-EXISTING 并点名）。
3. 全部 `scripts/*.py` `py_compile` 通过。
4. SKILL.md 中出现的 `references/*` 与 `scripts/*` 均存在于对应安装目录。
5. frontmatter 扫描无 `[<>]`；description 含 Use when / Do NOT use。
6. UAE 项目路径存在完整 skill 树（SKILL.md + scripts + references + locales）。

### Review 契约

- 独立 subagent 审查完整 diff + Spec 验收项。
- 结论分列：Spec compliance / Correctness / Codebase consistency。
- critical 未关闭不得 Finalize。

## [S3] Out of Scope

- 修改 quiet 四条件、指纹算法、探针判定逻辑、fix_gate 语义
- 发布到 npm/marketplace 或改版本号/changelog（除非 Finalize 时仓库惯例要求且用户同意）
- 对 universal-agent-engine 或其它业务项目实际执行 hunt
- 修改 skill-creator 内置 `validate_skill.py`
- 自动改写任何项目的 `AGENTS.md`
- 推送远程 / 开 PR（除非用户 Finish 时明确选择）

## Tasks

- [x] T1: 分支 `feat/skill-config-opt` + 本 Spec 就位 — acceptance: Spec 文件存在且 status=designed；workspace override 已记录 (covers: S2) — 注：分支创建被会话隔离拦截；override 已写入 Spec；文件已就位
- [x] T2: 修复 frontmatter（去 `>`，补 compatibility，保留触发/负触发） — acceptance: 源 SKILL.md frontmatter 无 `[<>]`，字段合规 (covers: S1;S2)
- [x] T3: body 优化（Important + Examples + Troubleshooting + orphan refs 链接） — acceptance: 三个 orphan 被链接；Examples/Troubleshooting 章节存在且含负例/常见故障 (covers: S2)
- [x] T4: 源仓同步与单测 — acceptance: unittest 全绿或 PRE-EXISTING 记录；scripts py_compile OK (covers: S2)
- [x] T5: 全局重装 + UAE 项目级安装 — acceptance: 两路径含完整树且无 `__pycache__`；SKILL.md 与源一致 (covers: S2)
- [x] T6: Verify 三路径 validator PASS + 链接完整性 — acceptance: 三路径 `PASS: 0 error(s)` (covers: S2)
- [x] T7: Review subagent + Finalize Spec（status=delivered + Report） — acceptance: review 无未处理 critical；Spec 勾选任务并写 Report (covers: S1;S2; depends: T2–T6)
