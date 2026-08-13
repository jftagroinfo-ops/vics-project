#!/usr/bin/env python3
"""Keep localized legal documents out of search until native review is recorded."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LEGAL_PAGES = {"privacy.html", "terms.html", "legal.html"}
ROBOTS_RE = re.compile(r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>', re.I)
MARKER = '<meta name="jft-review-status" content="native-legal-review-required">'


def main() -> int:
    policy = json.loads((ROOT / "localization-review.json").read_text(encoding="utf-8"))
    languages = set(policy.get("priority_locales", {})) | set(policy.get("fallback_locales", []))
    updated = 0
    for language in sorted(languages):
        for name in LEGAL_PAGES:
            path = ROOT / language / name
            if not path.exists():
                continue
            original = path.read_text(encoding="utf-8")
            text = ROBOTS_RE.sub('<meta name="robots" content="noindex,follow">', original, count=1)
            if "name=\"robots\"" not in text:
                text = text.replace("<head>", '<head>\n  <meta name="robots" content="noindex,follow">', 1)
            if MARKER not in text:
                text = text.replace("<head>", f"<head>\n  {MARKER}", 1)
            if text != original:
                path.write_text(text, encoding="utf-8")
                updated += 1
    print(f"Marked {updated} localized legal pages noindex pending native review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
