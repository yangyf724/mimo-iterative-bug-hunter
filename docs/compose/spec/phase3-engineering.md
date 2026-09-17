---
feature: phase3-engineering
status: in-progress
updated: 2026-09-17
branch: feat/phase3
commits: # filled at delivery
---

# Phase 3 — 工程化

## Report

## [S1] Problem

Phase 0–2 已交付 skill 骨架、全模态通道（layout/contrast/visual-diff/fix-gate/ux-flow/canvas/vlm/shard）。DESIGN §10.4 仍缺工程化闭环：

1. **CI 门禁**：无 axe 机器门禁脚本，也无 baseline 完整性锁；仓库自身无标准 CI 工作流，回归只能靠人工跑 unittest。
2. **路由自动发现**：`state.surfaces.web.routes` 仍靠用户手写；capture-protocol 虽写「默认补全关键链接」，但无脚本，复杂站点开箱即用成本高。
3. **误报反哺**：rejected bugs 未沉淀为可复用白名单/模式库；同一 FP 跨轮/跨项目会重复打扰；无 AGENTS/规则白名单导出物。
4. **Machine-readable 导出**：仅有 Markdown REPORT + 分散 JSON；无版本化单文件 export，CI/下游工具无法稳定消费。
5. **泛化验收**：全部 DoD 都打在 `examples/acceptance-demo/`；无第二项目证明 skill 不是对 demo 路径/缺陷硬编码。

## [S2] Design

### Workspace override

环境仍禁止 `git worktree add`（共享 ref store）。实现在主 checkout 分支 `feat/phase3` 上进行。脚本保持 **stdlib-only**（Pillow 可选，与 Phase 1 一致）；axe-core 不捆绑——仅在 node/npx 可用时调用，否则记 `unavailable`，禁止静默通过。

### 交付边界（Phase 3 only）

| 组件 | 职责 |
|------|------|
| `discover_routes.py` | 从 HTML/sitemap/package.json 发现同源路由并写优先级 |
| `fp_feedback.py` | rejected → FP 模式库；白名单查询；生成 AGENTS 建议片段 |
| `export_report.py` | 汇出版本化 `report.json` |
| `baseline_lock.py` | 基线 sha256 锁定 / 校验 / 与 approvals 对账 |
| `axe_gate.py` | 可选 axe-core 扫描；不可用时明确 unavailable |
| `ci_gate.py` | 编排 unittest + fixture E2E + baseline lock +（可选）axe |
| `.github/workflows/ci.yml` | 仓库 CI 模板：Python unittest + fixture E2E + ci_gate |
| `examples/second-project/` | 第二验收 demo（不同路由与缺陷） |

**更新**

- `init_state.py`：`phase: 3`；`surfaces.web.route_discovery` / `surfaces.web.routes` 元数据；`visual_oracle` 无关新增走独立 `ci`/`export`/`fp` 段
- `hunt_round.py`：注册前查询 FP 白名单，命中则记 `suppressed` 不进 new Confirmed 路径
- `layout_probe.py` / `contrast_probe.py` / `ux_flow.py` / `canvas_probe.py`：可选接收 `--fp-patterns`，命中输出 `status=suppressed` finding（仍落盘，便于审计）
- references：新 `ci-gate.md`、`route-discovery.md`、`fp-feedback.md`、`export-schema.md`；更新 `strategies.md` / `capture-protocol.md` / `fix-gate.md`
- `SKILL.md`：主循环增加 discover / fp / export / ci 指针（正文仍精简）
- `docs/ACCEPTANCE.md`：Phase 3 DoD 表
- `docs/METRICS.md`：第二项目观测行占位

### 1. 路由自动发现（discover_routes.py）

#### 1.1 输入源（按优先级合并）

| 源 | 解析 | 条件 |
|----|------|------|
| `seed` | CLI `--seed / /about` 或已有 `state.surfaces.web.routes` | 始终保留，优先级最高 |
| `package.json` | `routes` 数组（约定字段） | 文件存在且字段为 list[str] |
| `sitemap` | `base_url/sitemap.xml` 或 `--sitemap path/url` 的 `<loc>` | 可解析；仅同源 path |
| `html-links` | 起点页 HTML 中 `<a href>` 同源链接 | `--from-url` 或 `--html` 文件 |

同源判定：无 host 的相对路径；或 host/port 与 `base_url` 一致。忽略：`mailto:`、`tel:`、`javascript:`、纯 hash、外部域、静态资源后缀（`.png/.css/.js/.svg/.ico/.woff*` 等）。

#### 1.2 优先级与上限

```
priority: seed=0, package.json=1, sitemap=2, nav/link=3（文档序）
max_routes 默认 12（state.surfaces.web.route_discovery.max_routes 可改）
去重：normalize（去尾 `/`，保留 query/hash 丢弃）
```

输出项：`{ "route": "/about", "source": "html-links", "priority": 3, "from": "http://…/#nav" }`。

#### 1.3 写回 state

- CLI：`discover_routes.py --root P [--from-url URL] [--html FILE] [--sitemap …] [--seed …] [--max-routes N] [--write]`
- `--write`：持有 `.bug-hunter/.lock`，合并进 `state.surfaces.web.routes`（保留 seed 顺序，追加新发现）；写 `surfaces.web.route_discovery = { last_run, sources, discovered_count, max_routes }`
- 无 `--write` 时只 stdout JSON，便于单测与 dry-run
- 网络失败 / 非 HTML → 该源 `unavailable`，不假装发现；exit 0 仍输出部分结果，exit 2 仅当全部源失败且无 seed

#### 1.4 纯函数边界（可无网单测）

- `extract_links(html: str, base_url: str) -> list[str]`
- `parse_sitemap(xml: str, base_url: str) -> list[str]`
- `parse_package_routes(json_text: str) -> list[str]`
- `filter_same_origin(urls, base_url) -> list[str]`
- `rank_routes(entries, max_routes) -> list[dict]`

### 2. 误报模式与白名单（fp_feedback.py）

#### 2.1 模式库路径

`.bug-hunter/fp_patterns.json`：

```json
{
  "version": 1,
  "updated_at": "…",
  "patterns": [
    {
      "id": "fp-0001",
      "modality": "web-visual",
      "category": "ui-layout",
      "rule_id": "touch-target",
      "route": "/",
      "viewport": "375x812",
      "selector_pattern": "[data-testid=btn-tiny]",
      "core_assertion_digest": "touch-target|below-min",
      "reason": "设计意图：装饰性 chip 非主触控目标",
      "source_bug_id": "bug-0007",
      "created_at": "…",
      "match": "selector+rule+route"
    }
  ]
}
```

`match` 枚举：

| 值 | 命中条件 |
|----|----------|
| `exact` | modality+category+rule_id+route+viewport+selector_pattern 完全一致 |
| `selector+rule+route` | rule_id + selector_pattern + route（viewport 忽略） |
| `rule+route` | rule_id + route |
| `digest` | core_assertion_digest 完全一致 |

#### 2.2 命中语义

- Finding 命中白名单 → 输出保留但 `status: "suppressed"`，`suppressed_by: pattern.id`
- `fingerprint --register` 对 suppressed **仍登记**（防重复扫描噪声），但 `hunt_round` summary 将其计入 `suppressed_count`，**不计入** `new_count`，converge 的「新 Confirmed」路径也不把它们当新问题
- 白名单可撤销：`fp_feedback.py remove --id fp-0001`

#### 2.3 从 rejected 沉淀

```
fp_feedback.py absorb --root P --bug bugs/rejected/bug-0007.json [--match selector+rule+route]
fp_feedback.py add --root P --rule-id … --route … --selector … --reason …
fp_feedback.py list|check --root P [--finding path]
fp_feedback.py agents-snippet --root P --out AGENTS.bug-hunter.snippet.md
```

`absorb` 从 rejected bug JSON 抽 `modality/category/rule_id/location/evidence.core_assertion_digest`；缺 selector 则退化为 `rule+route`。

`agents-snippet` **只生成建议文件**，不直接改项目 `AGENTS.md`。内容示例：已知 FP 规则、白名单路径、hunt 时请尊重 suppressed。

#### 2.4 集成点

- `hunt_round.py`：注册后过滤；`summary.suppressed_count` / `summary.suppressed[]`
- probe CLI：可选 `--fp-patterns PATH`；命中写 `status=suppressed`（detected_by 保留原通道）
- 不改指纹算法（仍粗粒度 digest），避免 Phase 0 结论回退

### 3. Machine-readable 导出（export_report.py）

#### 3.1 输出

默认 `.bug-hunter/export/report.json`（`--out` 可改）。

```json
{
  "schema_version": 1,
  "exported_at": "…",
  "skill": "iterative-bug-hunter",
  "phase": 3,
  "scope": {
    "mode": "hunt-and-fix",
    "modalities_enabled": ["code", "web-visual"],
    "base_url": "…",
    "routes": ["/", "/about"],
    "viewports": ["375x812", "1440x900"],
    "degrade_level": "L3"
  },
  "convergence": {
    "run_count": 3,
    "quiet_streak": 2,
    "required_quiet_streak": 2,
    "converged": true
  },
  "counts": {
    "confirmed": 0, "rejected": 0, "fixed": 0, "deferred": 0,
    "findings_total": 0, "suppressed": 0,
    "by_modality": {}, "by_rule": {}
  },
  "bugs": [ /* 读取 bugs/**/*.json，保留 id/status/modality/category/severity/title/location/rule_id/fingerprint */ ],
  "fingerprints": { "total": 0, "by_status": {} },
  "blind_spots": [],
  "runs": [ /* 每 run：id, new_count, known_count, suppressed_count, strategies, degrade_level */ ],
  "fp_patterns": { "count": 0, "ids": [] },
  "report_md_path": "REPORT.md",
  "notes": []
}
```

#### 3.2 校验

`export_report.py --validate FILE`：stdlib 检查必填键与类型；`schema_version` 未知 → exit 3。不引入 jsonschema 依赖。

#### 3.3 与 REPORT.md 关系

- REPORT.md 仍是人类主文档；export 是机器视图，**不要求**二者逐字同步，但 counts 必须来自同一 state/bugs 读数
- `ci_gate.py` 可调用 export 并校验，作为「报告可机器消费」门

### 4. Baseline 锁（baseline_lock.py）

#### 4.1 锁文件

`.bug-hunter/baselines/lock.json`：

```json
{
  "version": 1,
  "algorithm": "sha256",
  "created_at": "…",
  "files": {
    "web/home__375x812.png": "abc…",
    "web/about__1440x900.png": "def…"
  }
}
```

#### 4.2 命令

```
baseline_lock.py snapshot --baseline-dir DIR --lock PATH
baseline_lock.py verify --baseline-dir DIR --lock PATH [--approvals baselines/approvals.jsonl]
baseline_lock.py verify --project-root P   # 默认路径组合
```

`verify` 规则：

| 情况 | 结果 |
|------|------|
| 锁缺失 | exit 2 `no-lock`（首次需 snapshot；CI 对 skill 仓可用 demo 基线或 skip） |
| 文件 hash 一致 | exit 0 |
| hash 不一致 / 文件删除 | exit 1，列出漂移；**除非** `approvals.jsonl` 存在对应 route×viewport 且 `sha256` 等于**当前**文件 hash（有意变更） |
| 锁中无但目录多出文件 | 记 `unlocked_files`，默认 warn 不 fail（可用 `--strict` fail） |

不自动改基线；批准仍走 `visual_diff.py approve`。

### 5. axe 门禁（axe_gate.py）

#### 5.1 行为

```
axe_gate.py --url http://127.0.0.1:5173/ [--routes / /about] [--out DIR] [--fail-on violations]
axe_gate.py --html-file page.html   # 离线：写临时文件再跑（若 node 可用）
```

- 探测顺序：`npx --yes @axe-core/cli` → 项目本地 `node_modules/.bin/axe` → `node` 脚本 require `axe-core` + `playwright`/`jsdom` 均不可得则 **exit 0 + `status: unavailable`**（写 `axe-report.json`），并在 stdout 标明盲区
- 有违规且 `--fail-on violations` → exit 1
- 输出 `.bug-hunter/runs/run-N/axe/axe-report.json`：`{status, violations: [{id, impact, nodes, route}], backend}`
- **禁止**在 skill 仓库依赖里锁死 axe-core；文档写明 CI 如何 `npm i -D axe-core @axe-core/cli`

#### 5.2 quiet / CI 语义

- axe unavailable ≠ quiet 成功；converge 已有 modality 覆盖条件，不在此改 quiet 定义
- CI：demo 若可启动则尝试 axe；失败仅当 `status=ok` 且有 violations（门禁模式）

### 6. CI 编排（ci_gate.py + workflow）

#### 6.1 ci_gate.py（本地与 CI 同一入口）

```
ci_gate.py --root . [--skip-e2e] [--skip-axe] [--demo-root examples/acceptance-demo] [--second-root examples/second-project]
```

步骤（任一步 FAIL 则最终 exit 1，但继续跑完已开始步骤以便汇总）：

1. `python -m unittest discover -s tests`
2. `tests/phase1_fixture_e2e.py` 与 `tests/phase2_fixture_e2e.py`（若存在）
3. `baseline_lock.py verify`（对 demo 若有 baselines；无锁则 skip 并记 warn）
4. `export_report.py` 在临时 `.bug-hunter` 上 smoke（或对 second-project fixture）
5. 可选 axe：若未 `--skip-axe` 且探测到 node，对 second-project HTML fixtures 跑 axe_gate
6. stdout JSON summary：`{ok, steps: [{name, status, detail}]}`

#### 6.2 GitHub Actions

`.github/workflows/ci.yml`：

- trigger: push/PR
- setup-python 3.11+
- run: `python -m unittest discover -s tests`
- run: fixture E2E scripts
- run: `python iterative-bug-hunter/scripts/ci_gate.py --root . --skip-axe`（axe 在无浏览器 job 可 skip；有 node 的 job 可启用）
- 不强制安装 playwright/axe（与本机降级哲学一致）；workflow 注释写明如何扩展

### 7. 第二验收项目（examples/second-project/）

#### 7.1 定位

与 `acceptance-demo` **不同路由名、不同缺陷组合、不同视觉问题**，证明 discover/hunt/export/fp 不绑死第一 demo。

零依赖 Node 静态服务（与 demo 同风格），端口默认 `5174` 避免冲突。

#### 7.2 结构

```
examples/second-project/
  package.json          # start / test；"routes": ["/", "/shop", "/contact"]
  server.js
  public/
    index.html
    shop.html
    contact.html
    styles.css
  src/checkout.js       # 注入逻辑 bug，npm test 可红
  canvas/promo.scene.json
  flows/contact-submit.json
```

#### 7.3 注入缺陷（INTENTIONAL 注释；与 demo 不重复）

| 缺陷 | 期望 rule_id | 位置 |
|------|--------------|------|
| 商品卡在 375px 下容器过宽 | `overflow-x` | `/shop` 375x812 |
| 外链死链 `<a href="#">加入心愿单` | `dead-link` | `/shop` |
| contact 表单 submit 无 error sink | `missing-feedback` | `/contact` |
| 小图标按钮 20×20 | `touch-target` | `/contact` 375x812 |
| 低对比度辅助文案 | `contrast-text` | `/` |
| `checkout.js` 优惠券计算 off-by-one | dynamic `npm test` | code |
| canvas：促销图标题出安全区 + 导出尺寸不符 | `safe-area-violation` / `export-mismatch` | `canvas/promo.scene.json` |
| flow：空联系表提交期望 alert | `ux-flow-step` | `flows/contact-submit.json` |

#### 7.4 泛化 DoD

- `discover_routes.py --html public/index.html --seed /` 能列出 `/shop` `/contact`
- `hunt_round --skip-capture` + fixtures（或真采集）summary 的 `by_rule` 覆盖上表至少 6 类（含 code 1 类）
- `export_report.py` 在 second-project state 上产出合法 `schema_version: 1`
- 白名单 absorb 一条 second-project rejected 后，同指纹再 hunt 进入 `suppressed_count` 而非 `new_count`

### 8. state / hunt_round 集成

`init_state.py` 增量（向后兼容）：

```json
"phase": 3,
"surfaces": {
  "web": {
    "route_discovery": {
      "enabled": true,
      "max_routes": 12,
      "sources": ["seed", "package.json", "sitemap", "html-links"],
      "last_run": null
    }
  }
},
"ci": {
  "axe_backend": "auto",
  "baseline_lock": true,
  "fail_on_axe": false
},
"export": {
  "path": "export/report.json",
  "schema_version": 1
},
"fp": {
  "patterns_path": "fp_patterns.json",
  "default_match": "selector+rule+route"
}
```

`hunt_round.py`：

- 可选 `--fp-patterns`；默认读 `.bug-hunter/fp_patterns.json`
- summary 增加 `suppressed_count`、`suppressed[]`
- 不改变 quiet 四条件定义；suppressed 不制造「新 Confirmed」

### 9. 测试边界（不依赖浏览器 / 不强制 node）

- discover：extract_links / sitemap / package routes / 同源过滤 / 排序上限；`--write` 锁写路径
- fp_feedback：absorb/add/list/check/remove；四种 match；hunt_round suppressed 不增 new
- export：从临时 state+bugs 产出并 `--validate`；缺字段 fail
- baseline_lock：一致 / 漂移 / approvals 放行 / strict unlocked
- axe_gate：无 node 时 `status=unavailable` exit 0（mock 探测函数）
- ci_gate：用 mock 步骤或仅跑 unittest 子集验证编排 JSON
- second-project：package.json routes 字段、注入 HTML 可被静态规则命中（喂 elements fixtures 而非真浏览器）

单测：`python -m unittest discover -s tests` 在 Phase 2 的 88 用例上增量全绿。

### 10. SKILL.md / references 增量

- Scope：可选 `route_discovery`、`fp_patterns`、`export`
- 主循环：Bootstrap 后可选 Discover → Hunt（可 suppress）→ Export；CI 指针
- 禁止：静默把 axe unavailable 当通过；自动改写用户 AGENTS.md；无锁改 fp_patterns / state

## [S3] Out of Scope

- 真实 axe-core / playwright 依赖捆绑与锁版本进本 skill 包
- 自动修改用户项目 `AGENTS.md`（只生成 snippet）
- 云端视觉回归 SaaS、Figma API
- 多项目并行调度与远程 CI 秘钥管理
- 将 skill 安装到 `~/.config/mimocode/skills/`（仍属发布动作）
- Phase 0–2 行为回归重写（指纹算法、quiet 定义、Fix Gate 判定语义保持不变）

## Tasks

- [ ] T1: 本 spec + 分支 `feat/phase3` — acceptance: 文档存在且 status=designed (covers: S2)
- [ ] T2: `discover_routes.py` + 纯函数单测 + `--write` 锁写 — acceptance: HTML/sitemap/package 正反例通过；max_routes 生效 (covers: S2)
- [ ] T3: `fp_feedback.py` + probe/hunt 集成 — acceptance: absorb/check/suppress 单测；summary.suppressed_count 正确 (covers: S2)
- [ ] T4: `export_report.py` + validate — acceptance: fixture state 产出合法 report.json；缺字段 exit≠0 (covers: S2)
- [ ] T5: `baseline_lock.py` + `axe_gate.py` 降级路径 — acceptance: hash/approvals/unavailable 单测通过 (covers: S2)
- [ ] T6: `ci_gate.py` + `.github/workflows/ci.yml` + references/SKILL/init_state phase3 — acceptance: ci_gate JSON 步骤可跑 unittest；workflow 文件存在 (covers: S2; depends: T2–T5)
- [ ] T7: `examples/second-project/` 注入 + ACCEPTANCE Phase 3 DoD + unittest 全绿 — acceptance: discover 能列出 shop/contact；fixtures 覆盖≥6 类 rule；`python -m unittest discover -s tests` OK (covers: S1;S2; depends: T2–T6)
