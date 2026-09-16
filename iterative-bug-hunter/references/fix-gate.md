# Fix Gate（可判定回归门）— Phase 1

1. 只修 **Confirmed**；Deferred 需用户点头。
2. 一次一修。
3. 回归门由 `scripts/fix_gate.py` 机器判定（禁止主观「看起来还行」）：

| 检查 | 通过条件 |
|------|----------|
| `target_cleared` | 同 `rule_id` 在同 route×viewport 不再命中（对修复后 captures 重跑 probe） |
| `zero_new_layout` | 回归矩阵重跑 layout+contrast，相对已有 fingerprints **零新增** |
| `pixel_gate` | 仅目标 route×viewport 允许 diff；其他已扫 cell 超阈 → fail，除非 intentional 审批 |
| `unit_green` | 若提供 `--test-cmd` 则 exit 0 |

4. 失败 → agent 回滚（`git checkout` 等），记 `fix-failed`；同一 bug 失败 ≥ `max_fix_failures` → Deferred。

## 用法

```powershell
# 修复后重新采集
& $env:MIMO_PYTHON iterative-bug-hunter/scripts/capture_web.py --root <project> --run-id run-fix --out <project>/.bug-hunter/runs/run-fix/captures

# 跑门
& $env:MIMO_PYTHON iterative-bug-hunter/scripts/fix_gate.py --root <project> `
  --bug bug-0001 `
  --captures <project>/.bug-hunter/runs/run-fix/captures `
  --baseline-dir <project>/.bug-hunter/baselines/web `
  --test-cmd "npm test" `
  --regression-mode matrix
```

退出码：`0` 门通过 · `1` 任一检查失败 · `2` bug 未找到。

结果写入 `runs/run-N/fix-verify.json`。

## intentional_visual_change

非目标路由像素 diff 默认 fail。放行方式：

1. `visual_diff.py approve --route … --viewport … --reason "..."`（写 `baselines/approvals.jsonl` 并更新基线）；或
2. 提供 `--fix-verify` JSON，含 `"intentional_visual_change": true` 与 `intentional_cells: ["/about@375x812"]`。

## 脚本不做的事

- 不修改源码；
- 不自动 `git` 回滚（回滚是 agent/SKILL 动作）；
- 不写 `bugs/**`（状态迁移由 main agent 持锁完成）。
