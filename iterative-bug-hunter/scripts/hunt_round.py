#!/usr/bin/env python3
"""Single-round hunt orchestration (Phase 1): capture → probes → register → summarize."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import capture_web  # noqa: E402
import converge_check as cc  # noqa: E402
import contrast_probe  # noqa: E402
import fingerprint as fp  # noqa: E402
import layout_probe as lp  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    import os

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def parse_vp(label: str | None) -> tuple[float, float]:
    text = (label or "").strip().lower().replace(" ", "")
    if "x" in text:
        a, _, b = text.partition("x")
        try:
            return float(a), float(b)
        except ValueError:
            pass
    return 0.0, 0.0


def probe_manifest_cells(
    captures_dir: Path,
    *,
    oracle: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest_path = captures_dir / "MANIFEST.json"
    if not manifest_path.exists():
        return []
    manifest = load_json(manifest_path)
    findings: list[dict[str, Any]] = []
    for item in manifest.get("items") or []:
        if item.get("status") != "ok":
            continue
        elements_name = item.get("elements_json")
        if not elements_name:
            continue
        elements_path = captures_dir / elements_name
        if not elements_path.exists():
            continue
        payload = load_json(elements_path)
        elements = payload.get("elements") or []
        w, h = parse_vp(item.get("viewport") or payload.get("viewport"))
        route = item.get("route") or payload.get("route")
        viewport = item.get("viewport") or payload.get("viewport")
        for el in elements:
            el.setdefault("route", route)
            el.setdefault("viewport", viewport)
        layout = lp.run_layout_rules(
            elements,
            viewport_width=w,
            viewport_height=h,
            epsilon_px=float(oracle.get("overflow_epsilon_px", 2)),
            touch_target_px=float(oracle.get("touch_target_px", 44)),
            overlap_ratio=float(oracle.get("overlap_ratio", 0.2)),
        )
        contrast = contrast_probe.run_contrast_rules(
            elements,
            min_contrast=float(oracle.get("min_contrast", 4.5)),
            large_text_min_contrast=float(oracle.get("large_text_min_contrast", 3.0)),
            font_too_small_px=float(oracle.get("font_too_small_px", 12)),
            line_height_min_ratio=float(oracle.get("line_height_min_ratio", 1.2)),
        )
        cell_findings = layout + contrast
        raw_name = f"{item.get('stem') or capture_web.route_slug(str(route))}__findings.json"
        save_json(
            captures_dir.parent / "findings" / "raw" / raw_name,
            {"route": route, "viewport": viewport, "findings": cell_findings},
        )
        findings.extend(cell_findings)
    return findings


def run_dynamic(cmd: str, *, root: Path) -> list[dict[str, Any]]:
    try:
        proc = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True)
    except Exception as e:  # noqa: BLE001
        return [
            {
                "rule_id": "dynamic-fail",
                "modality": "code",
                "category": "logic",
                "severity": "high",
                "title": f"Dynamic command crashed: {cmd}",
                "statement": str(e),
                "location": {"file": cmd, "viewport": "n/a"},
                "metrics": {"cmd": cmd},
                "evidence_level_target": "L3",
                "detected_by": "dynamic",
                "core_assertion_digest": "dynamic|command-crash",
            }
        ]
    if proc.returncode == 0:
        return []
    tail = ((proc.stderr or "") + "\n" + (proc.stdout or ""))[-800:]
    return [
        {
            "rule_id": "dynamic-fail",
            "modality": "code",
            "category": "logic",
            "severity": "high",
            "title": f"Dynamic test/command failed: {cmd}",
            "statement": f"exit={proc.returncode}",
            "location": {"file": cmd, "viewport": "n/a"},
            "metrics": {"cmd": cmd, "exit_code": proc.returncode, "output_tail": tail},
            "evidence_level_target": "L3",
            "detected_by": "dynamic",
            "core_assertion_digest": "dynamic|command-fail",
        }
    ]


def summarize(findings: list[dict[str, Any]], reg: dict[str, Any]) -> dict[str, Any]:
    by_rule: dict[str, int] = {}
    by_viewport: dict[str, int] = {}
    by_modality: dict[str, int] = {}
    for f in findings:
        rule = f.get("rule_id") or "unknown"
        by_rule[rule] = by_rule.get(rule, 0) + 1
        vp = (f.get("location") or {}).get("viewport") or "n/a"
        by_viewport[str(vp)] = by_viewport.get(str(vp), 0) + 1
        mod = f.get("modality") or "unknown"
        by_modality[mod] = by_modality.get(mod, 0) + 1
    return {
        "findings_total": len(findings),
        "new_count": reg.get("new_count", 0),
        "known_count": reg.get("known_count", 0),
        "duplicate_rate": reg.get("duplicate_rate", 0.0),
        "by_rule": by_rule,
        "by_viewport": by_viewport,
        "by_modality": by_modality,
    }


def load_state(root: Path) -> dict[str, Any]:
    path = root / ".bug-hunter" / "state.json"
    if not path.exists():
        return {}
    return load_json(path)


def run_hunt_round(
    *,
    root: Path,
    run_id: str,
    skip_capture: bool = False,
    captures: Path | None = None,
    dynamic_cmd: str | None = None,
    write_candidates: bool = False,
    strategies: list[str] | None = None,
) -> dict[str, Any]:
    state = load_state(root)
    web = (state.get("surfaces") or {}).get("web") or {}
    oracle = state.get("visual_oracle") or {}
    degrade = web.get("degrade_level") or "L1"
    previous_quiet = int(
        (state.get("convergence") or {}).get("quiet_streak", state.get("quiet_streak", 0))
    )
    required_quiet = int((state.get("convergence") or {}).get("required_quiet_streak", 2))
    modalities = state.get("modalities_enabled") or ["code", "web-visual"]

    captures_dir = captures or (root / ".bug-hunter" / "runs" / run_id / "captures")
    findings: list[dict[str, Any]] = []
    used_strategies: list[str] = list(strategies or [])
    capture_result = None

    web_probe_allowed = cc.degrade_allows_strategy(degrade, "layout-geom")

    if not skip_capture and web_probe_allowed:
        capture_result = capture_web.run_capture(
            root=root,
            base_url=web.get("base_url"),
            routes=web.get("routes"),
            viewports=web.get("viewports"),
            out=captures_dir,
            run_id=run_id,
            timeout_ms=20000,
        )
        if capture_result.get("backend") == "unavailable":
            degrade = "L1"
            web_probe_allowed = False

    # Probe existing captures whenever MANIFEST is present (fixtures / resume / L2+).
    # Degrade only gates *new* capture attempts above, not consuming already-collected artifacts.
    if (captures_dir / "MANIFEST.json").exists():
        if "layout-geom" not in used_strategies:
            used_strategies.append("layout-geom")
        if "contrast-type" not in used_strategies:
            used_strategies.append("contrast-type")
        if "responsive-matrix" not in used_strategies:
            used_strategies.append("responsive-matrix")
        cell_findings = probe_manifest_cells(captures_dir, oracle=oracle)
        findings.extend(cell_findings)
        # Consuming captures implies web-visual was exercised this round.
        if degrade in ("L0", "L1"):
            degrade = "L2"

    if dynamic_cmd:
        if "dynamic" not in used_strategies:
            used_strategies.append("dynamic")
        findings.extend(run_dynamic(dynamic_cmd, root=root))

    if not used_strategies:
        used_strategies = ["static"]

    fp_path = root / ".bug-hunter" / "fingerprints.json"
    reg = fp.register_fingerprints(findings, fp_path=fp_path, run_id=run_id, now=utc_now())

    if write_candidates:
        cand_dir = root / ".bug-hunter" / "runs" / run_id / "findings" / "candidates"
        cand_dir.mkdir(parents=True, exist_ok=True)
        for item in reg.get("new") or []:
            save_json(cand_dir / f"{item.get('fingerprint')}.json", item)

    new_confirmed = 0  # hunt_round never confirms; agent does
    conv = cc.evaluate_round(
        strategies=used_strategies,
        degrade_level=degrade,
        modalities_enabled=modalities,
        new_confirmed=new_confirmed,
        new_regressions=[],
        previous_quiet_streak=previous_quiet,
        required_quiet_streak=required_quiet,
    )

    summary = summarize(findings, reg)
    summary.update(
        {
            "run_id": run_id,
            "degrade_level": degrade,
            "strategies": used_strategies,
            "convergence": conv,
            "capture_backend": (capture_result or {}).get("backend"),
            "captured_at": utc_now(),
        }
    )
    save_json(root / ".bug-hunter" / "runs" / run_id / "summary.json", summary)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run one hunt round (capture→probe→register)")
    p.add_argument("--root", default=".")
    p.add_argument("--run-id", default="run-1")
    p.add_argument("--skip-capture", action="store_true")
    p.add_argument("--captures", default=None)
    p.add_argument("--dynamic-cmd", default=None)
    p.add_argument("--write-candidates", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    captures = Path(args.captures).resolve() if args.captures else None
    summary = run_hunt_round(
        root=root,
        run_id=args.run_id,
        skip_capture=args.skip_capture,
        captures=captures,
        dynamic_cmd=args.dynamic_cmd,
        write_candidates=args.write_candidates,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
