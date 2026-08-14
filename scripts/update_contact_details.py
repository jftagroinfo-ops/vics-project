#!/usr/bin/env python3
"""Standardize JFT Agro's public email address across site source files."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
NEW_EMAIL = "jftagro.info@gmail.com"
OLD_DOMAIN = "jftagro" + ".com"
TEXT_SUFFIXES = {".html", ".js", ".json", ".xml", ".txt", ".md", ".py", ".yml", ".yaml"}
LOCALES = {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}
PRIMARY_PHONE_LINK = '<a href="tel:+918425057274">+91 84250 57274</a>'
SECONDARY_PHONE_LINK = '<a href="tel:+918652362771">+91 86523 62771</a>'


def main() -> int:
    changed = 0
    replacements = 0
    email_pattern = re.compile(rf"[\w.%+-]+@{re.escape(OLD_DOMAIN)}", re.I)
    encoded_pattern = re.compile(rf"[\w.%+-]+%40{re.escape(OLD_DOMAIN)}", re.I)

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if ".git" in path.parts or "reports" in path.parts or path == Path(__file__).resolve():
            continue
        original = path.read_text(encoding="utf-8", errors="strict")
        updated, plain_count = email_pattern.subn(NEW_EMAIL, original)
        updated, encoded_count = encoded_pattern.subn("jftagro.info%40gmail.com", updated)
        if (
            path.name == "index.html"
            and path.parent.name in LOCALES
            and PRIMARY_PHONE_LINK in updated
            and SECONDARY_PHONE_LINK not in updated
        ):
            updated = updated.replace(
                PRIMARY_PHONE_LINK,
                f"{PRIMARY_PHONE_LINK} · {SECONDARY_PHONE_LINK}",
                1,
            )
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
            replacements += plain_count + encoded_count

    print(f"Updated {replacements} email references in {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
