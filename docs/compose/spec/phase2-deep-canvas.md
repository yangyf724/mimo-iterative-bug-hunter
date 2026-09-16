---
feature: phase2-deep-canvas
status: in-progress
updated: 2026-09-17
branch: feat/phase2
commits: 4119fd7..HEAD
---

# Phase 2 — 深层与画布

## Report

（交付后填写）

## [S1] Problem

Phase 0/1 已覆盖 code 通道、多 viewport 采集、layout-geom 全规则、contrast-type、visual-diff 与可判定 Fix Gate。DESIGN §10.3 仍缺：

1. **ux-flow**：空状态 / loading / 错误 toast / 死链等 UX 状态问题没有可执行通道；WebTestPilot 式符号化（元素→变量，前后置条件）未落地，agent 只能靠主观看图。
2. **画布通道**：`state.surfaces.canvas` 仅有占位结构，无 `canvas-safe` / `canvas-asset` 探针，无法对 scene-json 做安全区、导出尺寸、分辨率、宽高比判定。
3. **vlm-audit**：无双视角一致协议与合并器；VLM 审图结果无法按 DESIGN §5.5 变成结构化 Candidate，也无法与 layout/contrast 结果交叉去重。
4. **subagent 并行采集**：`capture_web.py` 单进程串行；§5.2b 允许 subagent 写 `runs/run-N/captures/`，但没有分片协议与 MANIFEST 合并入口，主 agent 无法安全汇总。

## [S2] Design

### Workspace override

环境仍禁止 `git worktree add`（共享 ref store）。实现在主 checkout 分支 `feat/phase2` 上进行。脚本保持 **stdlib-only**（Pillow 可选，与 Phase 1 visual_diff 一致）；VLM 不内嵌模型调用——`vlm_audit.py` 只做协议、共识合并与落盘，两次审图由 agent/MCP 产出 JSON。

### 交付边界（Phase 2 only）

| 脚本 | 职责 |
|------|------|
| `ux_flow.py` | 符号化 flow 评估 + 静态 UX 规则（dead-link / empty-state / missing-feedback） |
| `canvas_probe.py` | 统一 canvas item 上的 `canvas-safe` + `canvas-asset` 规则 |
| `vlm_audit.py` | 双视角 VLM 候选合并、与机器 finding 交叉去重 |
| `capture_web.py`（扩展） | `--shard i/n` 分片采集 + `merge` 子命令合并 MANIFEST |

**更新**

- `init_state.py`：`phase: 2`，`visual_oracle` 增加 canvas/ux/vlm 默认值，`surfaces.canvas` 契约字段
- `hunt_round.py`：在 L4 且策略允许时编排 ux-flow / canvas-safe / canvas-asset；可选 `--flows` / `--canvas-root`
- `converge_check.py`：L4 策略映射已有，补 `vlm-audit` 覆盖 `canvas` 时的边界说明（默认仍 web-visual；有 canvas item 且 vlm 附着 canvas 时由 findings 的 modality 统计）
- references：`strategies.md`、`visual-rules.md`、`capture-protocol.md`、新 `ux-flow.md`、`canvas-protocol.md`、`vlm-audit.md`、`subagent-capture.md`
- `SKILL.md`：主循环指向新脚本（正文仍精简）
- demo：注入 Phase 2 可机器判定缺陷 + `canvas/` 场景 + `flows/` 符号化样例
- `docs/ACCEPTANCE.md`：Phase 2 DoD 表

### 1. ux-flow + WebTestPilot 符号化

#### 1.1 Flow 文件契约

路径：默认 `<root>/.bug-hunter/flows/*.json`（运行时）或项目内非忽略路径；验收 demo 使用 `examples/acceptance-demo/flows/`（不被 `.bug-hunter/` ignore 覆盖）。CLI：`--flows DIR`。

```json
{
  "id": "home-submit-empty",
  "route": "/",
  "viewport": "375x812",
  "symbols": {
    "submitBtn": "[data-testid=flow-submit]",
    "errorBanner": "[data-testid=flow-error]",
    "toast": "[data-testid=flow-toast]",
    "formValid": false
  },
  "steps": [
    {
      "action": "click",
      "target": "submitBtn",
      "pre": {"formValid": false},
      "post": {
        "errorBanner.visible": true,
        "toast.visible": false
      }
    }
  ],
  "inferred_oracle": true
}
```

评估输入优先级：

1. 本轮 `elements.json`（route×viewport 对齐）→ 判定 `visible` / `exists` / 文本类条件；
2. 可选 `state_json`（agent 采集的页面状态快照）→ 判定 `formValid` 等符号；
3. 缺元素或缺状态 → step 结果 `status: "unavailable"`，**不得**记 quiet 成功，写入 Blind Spots。

#### 1.2 静态 UX 规则（无 flow 文件也可跑）

对 MANIFEST 中每个 ok cell 的 `elements.json`：

| rule_id | 判定 | category | digest |
|---------|------|----------|--------|
| `dead-link` | `a[href]` 且 href ∈ {``, `#`, `javascript:void(0)`, `javascript:void(0);`} | ui-ux-flow | `dead-link\|href-stub` |
| `missing-empty-state` | 列表容器（`role=list` / `[data-empty-state]` 预期位）存在但无 `data-empty-state` 子节点且可见子项为 0（启发式：`data-list-empty="expected"` 标记容器） | ui-ux-flow | `missing-empty-state\|no-placeholder` |
| `missing-feedback` | `button[type=submit]` 或 `[data-testid*=submit]` 存在，但同 route 无 `[role=alert]`/`[data-testid*=error]`/`[data-testid*=toast]`/`[data-feedback]` 节点 | ui-ux-flow | `missing-feedback\|no-error-sink` |

启发式规则一律 `evidence_level_target: "L3"` 当且仅当 elements 几何/属性可复现；否则 L2 候选。demo 用显式 `data-*` 标记保证确定性。

#### 1.3 符号化 step 评估

- `exists(selector)`：elements 中存在该 selector；
- `visible(selector)`：存在且 `inViewport` 且 bbox w,h ≥ 1；
- 布尔符号：来自 `symbols.formValid` 或 `--state-json`；
- 文本条件：`text_contains(selector, "...")`；
- 每条失败 step 产出 finding：`rule_id=ux-flow-step`，`category=ui-ux-flow`，`modality=web-visual`，`metrics` 含 step id、pre、post、observed、`inferred_oracle`。

CLI：

```
ux_flow.py --elements PATH --flow PATH [--state-json PATH] [--out findings.json]
ux_flow.py --manifest MANIFEST.json --flows DIR --out-dir DIR   # 静态规则 + flow
```

### 2. canvas-safe / canvas-asset

#### 2.1 统一 item（DESIGN §5.2）

`state.surfaces.canvas.items[]` 或 CLI `--items` / 目录扫描 `*.scene.json`：

```json
{
  "id": "poster-hero",
  "kind": "scene-json",
  "export_size": "1080x1920",
  "source": "examples/acceptance-demo/canvas/poster-hero.scene.json",
  "render_png": "examples/acceptance-demo/canvas/poster-hero.png",
  "spec": {"safe_inset_pct": 5},
  "objects": [
    {
      "id": "title",
      "type": "text",
      "x": 10, "y": 10, "w": 200, "h": 40, "zIndex": 2,
      "text": "标题", "opacity": 1
    }
  ],
  "assets": [
    {"id": "bg", "path": "bg.png", "display_w": 1080, "display_h": 1920,
     "pixel_w": 400, "pixel_h": 400, "aspect": null}
  ]
}
```

- scene 文件也可只有 `objects`/`assets`/`export_size`；`id` 默认取文件 stem。
- 无 `objects` 时 `z-order-occlusion` / `safe-area-violation` 标 `unavailable`（记盲区，不假装通过）。

#### 2.2 规则表

| rule_id | 判定 | category | 默认 |
|---------|------|----------|------|
| `safe-area-violation` | object bbox 超出 `export_size` 的 inset 安全区 | canvas-design | inset 5% |
| `export-mismatch` | `export_size` ≠ 用户目标（`spec.export_target` 或 CLI） | canvas-design | — |
| `z-order-occlusion` | 低 z 完全被更高 z 不透明 bbox 覆盖且 type∈{text,cta} | canvas-design | coverage>0.98 |
| `low-res-asset` | `max(display/pixel) > 2` | canvas-asset | 2.0 |
| `aspect-distort` | `\|display_w/display_h - pixel_w/pixel_h\| / ratio > 0.02` | canvas-asset | 2% |
| `hierarchy-flat` | 主 CTA（`primary: true` 或 type=cta）面积/对比启发式弱于次级 → **仅 Deferred 候选** | canvas-design | — |

Finding 结构：`modality=canvas`，`location.surface=canvas`，`location.canvas_id`，`location.canvas_object_id`，`evidence_level_target=L3`（hierarchy-flat 除外）。

CLI：

```
canvas_probe.py --items PATH_OR_DIR [--export-target WxH] [--safe-inset-pct 5] [--out DIR]
canvas_probe.py --root PROJECT   # 读 state.surfaces.canvas
```

### 3. vlm-audit 双视角候选

不调用模型。协议：

1. Agent 对同一截图独立产出两份 audit JSON（视角 A=布局/层级，视角 B=空状态/可用性），路径 `.bug-hunter/runs/run-N/vlm/view-a.json` 与 `view-b.json`（或 CLI 传入）。
2. `vlm_audit.py merge` 规则：
   - 候选含 `title`、`location{route,viewport,selector?}`、`problem`、`confidence`；
   - **位置一致**：route+viewport 相同，且 selector 相同 **或** 归一化 bbox IoU>0.3 **或** 标题编辑距离归一 <0.3 且 route 相同；
   - 两视角都点名 → consensus candidate；
   - 与 `findings/raw/**` 已有机器 finding 交叉：同 rule 族（layout/contrast/a11y）或 selector 重合 → **合并升级**为已有 finding 的 `evidence.vlm_corroboration`，不重复计数；
   - 纯审美且无机器支撑 → `status=candidate`，`allow_subjective=false` 时不得写 Confirmed。
3. 输出 `runs/run-N/findings/vlm/consensus.json` + 可选 merged raw findings。
4. `inferred_oracle: true` 写入每条 vlm 候选。

CLI：

```
vlm_audit.py merge --view-a A.json --view-b B.json --raw-dir DIR --out consensus.json
vlm_audit.py scaffold --screenshot PATH --route / --viewport 375x812 --out-a a.json --out-b b.json
```

### 4. subagent 并行采集

#### 4.1 分片

```
capture_web.py --shard 0/2 ...
capture_web.py --shard 1/2 ...
capture_web.py merge --captures DIR --out DIR
```

- 矩阵 cell 按 `(route_index * num_viewports + viewport_index) % n` 划分；
- 分片写入 `captures/shard-{i}/`（截图、elements、console、`MANIFEST.shard-{i}.json`）；
- **subagent 只写** `runs/run-N/captures/shard-*/` 与 `runs/run-N/findings/raw/`；禁止碰 `state.json` / `fingerprints.json` / `bugs/**`。

#### 4.2 merge

- 读所有 `MANIFEST.shard-*.json`，按 route×viewport 去重（保留 status=ok 优先）；
- 文件软链/复制策略：**复制**到 `captures/` 根（Windows 无强制 symlink）；
- 写根 `MANIFEST.json`：`merged_from`、每 cell `shard`；
- 冲突同 cell 多 ok → 取文件 mtime 较新，记 `conflicts` 字段；
- merge **不**写 state；主 agent 之后在锁内更新。

`references/subagent-capture.md` 写清：spawn 参数模板、禁止路径、汇总步骤。

### 5. hunt_round / state 集成

`init_state.py`：

```json
"phase": 2,
"visual_oracle": {
  "safe_inset_pct": 5.0,
  "z_order_min_coverage": 0.98,
  "low_res_max_ratio": 2.0,
  "aspect_distort_tol": 0.02,
  "ux_empty_state_attr": "data-empty-state",
  "vlm_min_agreement": 2,
  "allow_subjective": false
},
"surfaces": {
  "canvas": {"kind": "scene-json", "items": [], "export_target": null}
}
```

`hunt_round.py` 增量（函数级，保持无浏览器可测）：

- `--flows DIR`：对齐 MANIFEST cell 跑 `ux_flow`；
- 无 `--flows` 时对每个 ok cell 跑静态 ux 规则；
- `--canvas-items` 或 state.canvas.items 非空且 degrade=L4：跑 `canvas_probe`；
- strategies 列表追加已执行的 `ux-flow` / `canvas-safe` / `canvas-asset`；
- canvas findings 计入 `by_modality.canvas`。

L4 探测：state 同时满足 web 可开页 + canvas items 有效 source 存在 → `degrade_level` 可写 L4（由 agent/`init_state --resume-summary` 或 hunt 轮前 probe 写入；脚本只消费不擅自静默升级——有 canvas items 且 L3 时 **允许** hunt_round 将 degrade 记为 L4 并在 summary 标明 `degrade_elevated_by: canvas-items`）。

### 6. Demo 扩展（`examples/acceptance-demo/`）

在 Phase 0/1 缺陷上增加（注释 INTENTIONAL）：

| 缺陷 | 期望 rule_id | 位置 |
|------|--------------|------|
| 死链 `<a href="#">` | `dead-link` | `/` |
| 有 submit 无 error sink | `missing-feedback` | `/` |
| flow：empty submit 期望 errorBanner，实际无 | `ux-flow-step` | `examples/acceptance-demo/flows/empty-submit.json` |
| canvas 安全区：标题 y=2 且 inset 5% → 越界 | `safe-area-violation` | `canvas/poster.scene.json` |
| canvas 导出 800x600 vs 目标 1080x1920 | `export-mismatch` | 同上 + demo state |
| asset display 200px / pixel 80px | `low-res-asset` | 同上 |
| 双 VLM fixture：两视角都报「主按钮被裁切」与 overflow 交叉 | consensus 且不双计 | `tests/fixtures/vlm_*.json` |

提供 `scripts/demo_phase2_setup` 或文档步骤把 canvas/flows 链到 `.bug-hunter`（也可直接把 items 写进 demo state 样例）。

### 7. 测试边界（不依赖浏览器 / 不调 VLM）

- ux_flow：flow 通过/失败/元素缺失 unavailable；dead-link / missing-feedback / empty-state 正反例；
- canvas_probe：safe-area、export-mismatch、low-res、aspect、z-order 遮挡正反例；hierarchy-flat 仅 candidate；
- vlm_audit：双视角一致合并；不一致丢弃；与 raw layout finding 交叉不双计；scaffold 产出合法空模板；
- capture shard：矩阵划分稳定、merge 去重与冲突、subagent MANIFEST 合并；
- hunt_round：fixtures MANIFEST + canvas items + flow → summary 含新 rule/modality；
- 单测：`python -m unittest discover -s tests` 全绿（在 Phase 1 61 用例上增量）。

### 8. SKILL.md 增量

- Scope 增加 canvas items / flows 可选项；
- 主循环 Capture/Hunt 指向 shard 与 Phase 2 probes；
- Confirm：vlm 仅候选；hierarchy-flat 默认 Deferred；
- 并发：subagent 写路径白名单。

## [S3] Out of Scope

- Phase 3：CI 门禁、路由自动发现、误报反哺、第二项目回归验收；
- 真实 axe 自动安装捆绑；
- 内嵌 VLM/多模态 API 客户端（只提供 merge 协议）；
- 自动 git 回滚执行器；
- Figma API 拉取（仍接受用户导出 JSON/PNG）；
- 将 skill 安装到 `~/.config/mimocode/skills/`。

## Tasks

- [ ] T1: 本 spec + 分支 `feat/phase2` — acceptance: 文档存在且 status=designed (covers: S2)
- [ ] T2: `canvas_probe.py` + 统一 item 解析 + 规则 — acceptance: safe-area/export/low-res/aspect/z-order 正反例单测通过 (covers: S2)
- [ ] T3: `ux_flow.py` 静态规则 + 符号化 step — acceptance: dead-link/missing-feedback/flow-step 正反例与 unavailable 路径通过 (covers: S2)
- [ ] T4: `vlm_audit.py` merge/scaffold + 交叉去重 — acceptance: 一致合并、不一致丢弃、与 raw 不双计 (covers: S2)
- [ ] T5: `capture_web.py --shard` + `merge` — acceptance: 分片划分与 MANIFEST 合并单测通过 (covers: S2)
- [ ] T6: `init_state` phase2 默认 + `hunt_round` 编排 + references/SKILL — acceptance: fixtures 编排单测通过；文档指向新脚本 (covers: S2; depends: T2–T5)
- [ ] T7: demo 注入 Phase 2 缺陷 + canvas/flows + ACCEPTANCE DoD + unittest 全绿 — acceptance: `python -m unittest discover -s tests` OK；DoD 表完整 (covers: S1;S2; depends: T2–T6)
