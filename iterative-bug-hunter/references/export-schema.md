# Export Schema (v1)

`scripts/export_report.py` writes a machine-readable snapshot for CI and downstream tools.

Default path: `.bug-hunter/export/report.json`

## Top-level fields

| Field | Type | Required |
|-------|------|----------|
| `schema_version` | `1` | yes |
| `exported_at` | ISO UTC | yes |
| `skill` | string | yes |
| `phase` | int | no |
| `scope` | object | yes |
| `convergence` | object | yes |
| `counts` | object | yes |
| `bugs` | array | yes |
| `fingerprints` | object (`total`, `by_status`) | yes |
| `blind_spots` | array | yes |
| `runs` | array | yes |
| `fp_patterns` | `{count, ids}` | no |
| `report_md_path` | string | no |

`scope` requires `modalities_enabled`, `routes`, `viewports`.
`counts` requires `confirmed`, `rejected`, `fixed`, `deferred`, `findings_total`.
`convergence` requires `run_count`, `quiet_streak`, `required_quiet_streak`, `converged`.

## CLI

```bash
python scripts/export_report.py --root .
python scripts/export_report.py --validate .bug-hunter/export/report.json
```

Validate exit `0` when schema checks pass; unknown `schema_version` → exit `3`; other validation errors → exit `1`.

REPORT.md remains the human document; export is a parallel machine view derived from the same `.bug-hunter` state.
