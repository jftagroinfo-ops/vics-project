#!/usr/bin/env python3
"""Phase 36 - Stage T: Reusable AI-search & external-authority MONITORING HARNESS TEMPLATE.

This is a TEMPLATE. It is read-only and produces a comparison report against the
2026-08-29 baseline. It is designed to be run NEXT MONTH (and monthly thereafter)
to detect deltas in: production page status, hreflang/canonical integrity, AI-answer
platform citation presence (if access becomes available), external authority signals.

HOW TO USE (next month):
  1. Ensure this repo is at or ahead of sha 4535656d.
  2. (Optional) Provide credentials via environment variables for AI platforms / GSC
     IF access is granted in a future phase. Without them, those dimensions stay UNKNOWN.
  3. Run:  python scripts/phase36/monitor_template.py --compare reports/phase36/ai-search-baseline-2026-08-29.json
  4. Review the generated reports/phase36/monitor-YYYY-MM-DD.json for REGRESSIONS.

This script never modifies website/source/config and never deploys/pushes.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
REP = ROOT / "reports" / "phase36"
PROD_BASELINE = REP / "production-baseline-2026-08-29.json"
BASELINE_JSON = REP / "ai-search-baseline-2026-08-29.json"

# These must be filled by the operator in a future phase if/when access is granted.
# Until then every AI-answer-platform check returns UNKNOWN (never zero).
AI_PLATFORMS = [
    {"name": "Perplexity", "reachable": None, "state": "UNKNOWN",
     "note": "Returned HTTP 403 to unauthenticated curl on 2026-08-29. Requires API key (future phase)."},
    {"name": "Google AI Overviews", "reachable": None, "state": "UNKNOWN",
     "note": "Not renderable in unauthenticated SERP HTML on 2026-08-29."},
    {"name": "Bing Copilot / Chat", "reachable": None, "state": "UNKNOWN",
     "note": "Not renderable in unauthenticated SERP HTML on 2026-08-29."},
    {"name": "ChatGPT browse", "reachable": None, "state": "UNKNOWN",
     "note": "No credentialed access."},
]

# External authority sources carried from external-authority-baseline CSV for delta tracking.
EXT_SOURCES = [
    "APEDA directory", "FIEO member directory", "DGFT", "LinkedIn company page",
    "Facebook", "Instagram", "ExportHub", "IndiaMART", "TradeIndia",
    "Go4WorldBusiness", "Kompass", "Google web index", "Bing web index",
]


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def monitor() -> dict:
    """Captures a current snapshot against the frozen baseline (structure only)."""
    prod = load_json(PROD_BASELINE)
    baseline = load_json(BASELINE_JSON)

    snap = {
        "monitor_date": date.today().isoformat(),
        "baseline_date": "2026-08-29",
        "repository_sha_baseline": "4535656d830c4fb5ede7928cab7f6920597aaa67",
        "production_baseline_present": prod is not None,
        "scoring_baseline_present": baseline is not None,
        "ai_platforms": AI_PLATFORMS,
        "external_authority_sources_expected": EXT_SOURCES,
        "regressions_detected": None,  # populated by compare mode
        "note": ("Template harness. AI-answer-platform dimensions remain UNKNOWN until a future "
                 "phase grants credentialed access. This script does not modify production."),
    }
    return snap


def compare(baseline_path: Path) -> dict:
    baseline = load_json(baseline_path)
    snap = monitor()
    regressions = []
    if baseline and "ai_visibility" in baseline:
        base_obs = baseline["ai_visibility"].get("observed_score")
        # No current measurement of ai platforms possible -> cannot compute delta.
        regressions.append({
            "dimension": "ai_citation_rate",
            "status": "NO DELTA POSSIBLE",
            "reason": "AI-answer platforms still UNKNOWN/inaccessible; baseline dimension was UNKNOWN.",
        })
    snap["regressions_detected"] = regressions
    snap["comparison_mode"] = True
    snap["compared_against"] = str(baseline_path)
    return snap


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 36 monitoring harness template (read-only).")
    p.add_argument("--compare", metavar="BASELINE_JSON", help="Compare against a baseline JSON")
    p.add_argument("--out", metavar="OUT_JSON", help="Output path (default reports/phase36/monitor-YYYY-MM-DD.json)")
    args = p.parse_args()

    REP.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else REP / f"monitor-{date.today().isoformat()}.json"

    if args.compare:
        result = compare(Path(args.compare))
    else:
        result = monitor()

    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Monitor snapshot written -> {out_path}")
    print(f"  AI platforms tracked as UNKNOWN: {len(AI_PLATFORMS)}")
    print(f"  External sources tracked: {len(EXT_SOURCES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
