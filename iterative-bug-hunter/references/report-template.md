# REPORT.md 模板

写入目标项目 `.bug-hunter/REPORT.md`。`scripts/validate_report.py` 校验必含节。

```markdown
# Iterative Bug Hunter Report

**Generated:** <UTC timestamp>  
**Mode:** hunt-and-fix | hunt-only  
**Degrade (final):** L1 | L2 | L3 | L4  
**Runs:** N / max_runs=M  
**K (required_quiet_streak):** 2  

## 范围（Scope）

- Surfaces: web @ <base_url>
- Routes: `/`, `/about`
- Viewports: `375x812`, `1440x900`
- Modalities enabled: code, web-visual
- Modalities covered: ...

## 执行摘要（Summary by modality）

| modality | confirmed | fixed | rejected | deferred |
|----------|----------:|------:|---------:|---------:|
| code | 0 | 0 | 0 | 0 |
| web-visual | 0 | 0 | 0 | 0 |
| canvas | 0 | 0 | 0 | 0 |

## 确认清单（Confirmed）

### code

- [ ] `<title>` — file:line — rule/tool — severity

### web-visual

- [ ] `<title>` — route @ viewport — rule_id — screenshot path — severity

## 已修复与回归（Fixed）

- none | list + whether baselines updated

## 拒绝样本（Rejected）

- `<title>` — reason

## 已知盲区（Blind Spots）

- 未启动的服务 / 未扫 viewport / 无规范 Deferred / 画布未覆盖 / 降级原因

## 建议

- CI axe、视觉 baseline、补测等
```

## 字段约定

- 截图路径相对项目根或 `.bug-hunter/`。
- 每条 Confirmed 必须能回溯到 `bugs/confirmed/*.json` 的 fingerprint 与 rule_id。
- Blind Spots 不得为空句敷衍：至少写清已扫矩阵与未扫项。
