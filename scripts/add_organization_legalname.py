#!/usr/bin/env python3
"""Add the schema.org "legalName" property to every JSON-LD Organization
node identifying JFT Agro Overseas, so the registered legal entity name
("JFT Agro Overseas LLP", already present on about.html and privacy.html)
is consistently machine-readable everywhere the same Organization @id is
declared, not only in one place.

Walks and reparses each JSON-LD block (rather than a blind string
replace) so nested references (e.g. an article's "author" object) are
handled identically to a standalone Organization declaration. Idempotent:
any node that already has "legalName" is left untouched.
"""

from __future__ import annotations

import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORG_ID = "https://jftagro.com/#organization"
ORG_NAME = "JFT Agro Overseas"
LEGAL_NAME = "JFT Agro Overseas LLP"

SCRIPT_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def add_legal_name(node: object) -> bool:
    """Recursively add legalName to matching Organization nodes. Returns True if any change was made."""
    changed = False
    if isinstance(node, dict):
        if (
            node.get("@type") == "Organization"
            and node.get("name") == ORG_NAME
            and node.get("@id") in (ORG_ID, None)
            and "legalName" not in node
        ):
            node["legalName"] = LEGAL_NAME
            changed = True
        for value in node.values():
            if add_legal_name(value):
                changed = True
    elif isinstance(node, list):
        for item in node:
            if add_legal_name(item):
                changed = True
    return changed


def process_file(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    updates = 0

    def replace(match: re.Match) -> str:
        nonlocal updates
        prefix, body, suffix = match.group(1), match.group(2), match.group(3)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return match.group(0)
        if add_legal_name(data):
            updates += 1
            body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return prefix + body + suffix

    new_source = SCRIPT_RE.sub(replace, source)
    if updates:
        path.write_text(new_source, encoding="utf-8")
    return updates


LOCALES = ["ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"]


def main() -> None:
    candidates = sorted(glob.glob(str(ROOT / "*.html")))
    for locale in LOCALES:
        candidates += sorted(glob.glob(str(ROOT / locale / "*.html")))
    files_changed = 0
    blocks_changed = 0
    for candidate in candidates:
        path = Path(candidate)
        count = process_file(path)
        if count:
            files_changed += 1
            blocks_changed += count
    print(f"Files changed: {files_changed}. Organization blocks updated: {blocks_changed}.")


if __name__ == "__main__":
    main()
