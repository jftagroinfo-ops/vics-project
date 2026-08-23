#!/usr/bin/env python3
"""Run the reproducible local SEO release gate and write one result report."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = ROOT / "reports/seo-release-gate.json"
REPORT_MD = ROOT / "reports/seo-release-gate.md"
CHECKS = [
    ("Editorial governance", [sys.executable, "scripts/validate_editorial_governance.py"]),
    ("Localization governance", [sys.executable, "scripts/validate_localization_governance.py"]),
    ("Localization technical audit", [sys.executable, "scripts/audit_localizations.py"]),
    ("FAQ/schema and cluster alignment", [sys.executable, "scripts/validate_seo_alignment.py"]),
    ("Full static audit", [sys.executable, "scripts/full_site_audit.py"]),
    ("Local link scan", [sys.executable, "scripts/check_links.py"]),
    ("Release manifest", [sys.executable, "scripts/build_seo_release_manifest.py"]),
    ("IndexNow payload dry run", [sys.executable, "scripts/submit_indexnow.py", "--url-file", "reports/seo-release-manifest/post-deploy-crawl-urls.txt", "--dry-run"]),
]
CHECK_TIMEOUT_SECONDS = 300


def main() -> int:
    results = []
    for name, command in CHECKS:
        print(f"{name}: running", flush=True)
        try:
            run = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=CHECK_TIMEOUT_SECONDS,
            )
            results.append({"name": name, "status": "passed" if run.returncode == 0 else "failed", "returncode": run.returncode, "output": (run.stdout + run.stderr).strip()[-4000:]})
        except subprocess.TimeoutExpired as error:
            output = "".join(part for part in (error.stdout or "", error.stderr or "") if isinstance(part, str))
            results.append({"name": name, "status": "failed", "returncode": 124, "output": f"Timed out after {CHECK_TIMEOUT_SECONDS}s.\n{output}".strip()[-4000:]})
        print(f"{name}: {results[-1]['status']}")
    audit = json.loads((ROOT / "reports/full-site-audit.json").read_text(encoding="utf-8"))
    hard_failures = [item for item in results if item["status"] == "failed"]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed_with_editorial_warnings" if not hard_failures else "failed",
        "checks": results,
        "scope": audit["scope"],
        "editorial_warnings": audit["summary"],
        "external_gates": [
            "production deployment and live crawl",
            "real Search Console and aggregate lead outcomes",
            "named article reviewer approvals",
            "native-language commercial/legal approvals",
            "current credential proof",
            "earned third-party citations",
        ],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# SEO Release Gate", "", f"**Status:** {payload['status']}", "", "## Automated checks", "", "| Check | Result |", "|---|---|"]
    lines.extend(f"| {item['name']} | {item['status']} |" for item in results)
    lines.extend(["", "## Local scope", ""])
    lines.extend(f"- {key.replace('_', ' ').title()}: {value}" for key, value in audit["scope"].items())
    lines.extend(["", "## Editorial warnings (not mechanical release blockers)", ""])
    lines.extend(f"- {key}: {value}" for key, value in audit["summary"].items())
    lines.extend(["", "These are localized title/description length heuristics. They require native editorial review and are not changed automatically.", "", "## External gates", ""])
    lines.extend(f"- {item}" for item in payload["external_gates"])
    lines.extend(["", "Passing this local gate does not authorize deployment or indexing submission.", ""])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    return 1 if hard_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
