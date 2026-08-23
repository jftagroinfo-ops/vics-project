#!/usr/bin/env python3
"""Prevent shared-component link and hero-contrast regressions on nested pages."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    ROOT / "logistics" / "mundra-rice-exports" / "index.html",
    ROOT / "logistics" / "nhava-sheva-agro-exports" / "index.html",
)


def main() -> int:
    errors: list[str] = []
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        relative = page.relative_to(ROOT).as_posix()
        if "rebaseComponentLinks(host)" not in text:
            errors.append(f"{relative}: injected header/footer links are not rebased to the site root")
        if not re.search(r"\.hero\s+h1\s*\{[^}]*\bcolor\s*:\s*#fff\b", text, re.I | re.S):
            errors.append(f"{relative}: hero H1 does not explicitly override the global heading color")
        for component in ("/header.html", "/footer.html"):
            if component not in text:
                errors.append(f"{relative}: missing root-relative component loader for {component}")
    if errors:
        print("Nested component validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Nested component validation passed for {len(PAGES)} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
