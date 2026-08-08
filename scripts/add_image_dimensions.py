#!/usr/bin/env python3
"""Add intrinsic dimensions to local images to prevent layout shifts."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
SRC_RE = re.compile(r"\bsrc=[\"']([^\"']+)[\"']", re.I)


def image_path(page: Path, source: str) -> Path | None:
    parsed = urlsplit(source)
    if parsed.scheme or parsed.netloc or not parsed.path or "${" in parsed.path:
        return None
    relative = unquote(parsed.path)
    return ROOT / relative.lstrip("/") if relative.startswith("/") else page.parent / relative


def update_tag(page: Path, tag: str) -> str:
    source_match = SRC_RE.search(tag)
    if not source_match:
        return tag
    target = image_path(page, source_match.group(1))
    if not target or not target.is_file():
        return tag
    has_width = bool(re.search(r"\bwidth\s*=", tag, re.I))
    has_height = bool(re.search(r"\bheight\s*=", tag, re.I))
    if has_width and has_height:
        return tag
    try:
        with Image.open(target) as image:
            width, height = image.size
    except Exception:
        return tag
    attributes = ""
    if not has_width:
        attributes += f' width="{width}"'
    if not has_height:
        attributes += f' height="{height}"'
    return tag[:-1] + attributes + ">"


def main() -> None:
    changed = 0
    for page in ROOT.rglob("*.html"):
        original = page.read_text(encoding="utf-8")
        updated = IMG_RE.sub(lambda match: update_tag(page, match.group(0)), original)
        if updated != original:
            page.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"Added missing intrinsic image dimensions in {changed} pages.")


if __name__ == "__main__":
    main()
