#!/usr/bin/env python3
"""Minimal layout-geom probe: overflow-x (Phase 0)."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def check_overflow_x(
    elements: list[dict[str, Any]],
    *,
    viewport_width: float,
    epsilon_px: float = 2.0,
) -> list[dict[str, Any]]:
    """Detect horizontal overflow from element/viewport metrics.

    Each element dict may include:
      selector, text, scrollWidth, clientWidth, bbox {x,y,w,h}
    """
    findings: list[dict[str, Any]] = []

    # Root-level overflow
    root = next((e for e in elements if e.get("selector") in ("html", "body", "document", ":root")), None)
    if root:
        sw = float(root.get("scrollWidth") or 0)
        cw = float(root.get("clientWidth") or viewport_width)
        if sw > cw + epsilon_px:
            findings.append(
                {
                    "rule_id": "overflow-x",
                    "modality": "web-visual",
                    "category": "ui-layout",
                    "severity": "high",
                    "title": "Horizontal page overflow",
                    "statement": (
                        f"期望 document.scrollWidth <= viewport width {cw:.0f}px；"
                        f"实际 scrollWidth={sw:.0f}px，溢出 {sw - cw:.0f}px"
                    ),
                    "location": {
                        "surface": "web",
                        "route": root.get("route"),
                        "viewport": root.get("viewport") or f"{int(viewport_width)}x?",
                        "selector": "html",
                        "bbox": root.get("bbox"),
                    },
                    "metrics": {
                        "scrollWidth": sw,
                        "clientWidth": cw,
                        "overflow_px": round(sw - cw, 2),
                        "epsilon_px": epsilon_px,
                    },
                    "evidence_level_target": "L3",
                    "detected_by": "layout-geom",
                }
            )

    # Element boxes extending past viewport right edge
    for el in elements:
        if root is not None and el is root:
            continue
        bbox = el.get("bbox") or {}
        if not bbox:
            continue
        right = float(bbox.get("x", 0)) + float(bbox.get("w", 0))
        if right > viewport_width + epsilon_px:
            selector = el.get("selector") or el.get("id") or "unknown"
            overflow = right - viewport_width
            findings.append(
                {
                    "rule_id": "overflow-x",
                    "modality": "web-visual",
                    "category": "ui-layout",
                    "severity": "high" if el.get("interactive") or "button" in str(selector).lower() else "medium",
                    "title": f"Element overflows viewport horizontally: {selector}",
                    "statement": (
                        f"期望元素右缘 ≤ viewport {viewport_width:.0f}px；"
                        f"实际 right={right:.0f}px，超出 {overflow:.0f}px"
                    ),
                    "location": {
                        "surface": "web",
                        "route": el.get("route"),
                        "viewport": el.get("viewport") or f"{int(viewport_width)}x?",
                        "selector": selector,
                        "bbox": bbox,
                    },
                    "metrics": {
                        "right": round(right, 2),
                        "viewport_width": viewport_width,
                        "overflow_px": round(overflow, 2),
                        "epsilon_px": epsilon_px,
                    },
                    "evidence_level_target": "L3",
                    "detected_by": "layout-geom",
                }
            )

    # Element scroll overflow (clipped text/content) — skip document root
    # already reported as page-level overflow-x above.
    root_selectors = {"html", "body", "document", ":root"}
    for el in elements:
        if el is root:
            continue
        if el.get("selector") in root_selectors:
            continue
        sw = el.get("scrollWidth")
        cw = el.get("clientWidth")
        if sw is None or cw is None:
            continue
        swf, cwf = float(sw), float(cw)
        if swf > cwf + epsilon_px and el.get("text_overflow") not in ("ellipsis", "clip-intentional"):
            selector = el.get("selector") or "unknown"
            findings.append(
                {
                    "rule_id": "overflow-x",
                    "modality": "web-visual",
                    "category": "ui-layout",
                    "severity": "medium",
                    "title": f"Element content clipped horizontally: {selector}",
                    "statement": (
                        f"期望 scrollWidth ≤ clientWidth {cwf:.0f}px；"
                        f"实际 scrollWidth={swf:.0f}px，超出 {swf - cwf:.0f}px"
                    ),
                    "location": {
                        "surface": "web",
                        "route": el.get("route"),
                        "viewport": el.get("viewport") or f"{int(viewport_width)}x?",
                        "selector": selector,
                        "bbox": el.get("bbox"),
                    },
                    "metrics": {
                        "scrollWidth": swf,
                        "clientWidth": cwf,
                        "overflow_px": round(swf - cwf, 2),
                        "epsilon_px": epsilon_px,
                    },
                    "evidence_level_target": "L3",
                    "detected_by": "layout-geom",
                }
            )

    return findings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Layout geom probe (Phase 0: overflow-x)")
    p.add_argument("--viewport-width", type=float, required=True, help="viewport width in px")
    p.add_argument("--epsilon", type=float, default=2.0, help="overflow epsilon px")
    p.add_argument(
        "--route",
        default=None,
        help="optional route stamped onto findings",
    )
    p.add_argument(
        "--viewport",
        default=None,
        help="optional viewport label e.g. 375x812",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"invalid JSON: {e}"}), file=sys.stderr)
        return 2

    if isinstance(payload, dict):
        elements = payload.get("elements") or []
        viewport_width = float(payload.get("viewport_width") or args.viewport_width)
        epsilon = float(payload.get("epsilon_px") or args.epsilon)
        route = payload.get("route") or args.route
        viewport = payload.get("viewport") or args.viewport
    else:
        elements = payload
        viewport_width = args.viewport_width
        epsilon = args.epsilon
        route = args.route
        viewport = args.viewport

    for el in elements:
        if route and "route" not in el:
            el["route"] = route
        if viewport and "viewport" not in el:
            el["viewport"] = viewport

    findings = check_overflow_x(elements, viewport_width=viewport_width, epsilon_px=epsilon)
    # Coarse assertion: rule + direction, not exact pixel values.
    for f in findings:
        f["core_assertion_digest"] = f"{f['rule_id']}|horizontal-overflow"

    print(json.dumps({"findings": findings, "count": len(findings)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
