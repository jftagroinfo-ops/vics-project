#!/usr/bin/env python3
"""Fast, read-only SEO/accessibility/static integrity audit for the whole site."""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
LOCALES = {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}
HELPERS = {"header.html", "footer.html", "product-page-template.html", "inner-page-hero-snippet.html", "seo-universal-head-snippet.html"}
IGNORED_DIRS = {".git", ".cloudflare", ".cloudflare-dist", ".wrangler", "__pycache__", "backup", "reports"}
ATTR = re.compile(r"\b([\w:-]+)\s*=\s*([\"'])(.*?)\2", re.S)


def attrs(tag: str) -> dict[str, str]:
    return {key.lower(): html.unescape(value.strip()) for key, _, value in ATTR.findall(tag)}


def clean_text(raw: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)).strip())


def label(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_ignored(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return any(
        part in IGNORED_DIRS
        or part.startswith(".cloudflare-dist")
        or part.startswith(".wrangler")
        or part.startswith("backup_")
        for part in relative.parts
    )


def expected_url(path: Path) -> str:
    rel = label(path)
    if rel == "index.html":
        return "https://jftagro.com/"
    if rel.endswith("/index.html"):
        return "https://jftagro.com/" + rel[:-10]
    return "https://jftagro.com/" + rel


def local_path(page: Path, value: str) -> Path | None:
    parsed = urlsplit(value.strip())
    if parsed.scheme in {"mailto", "tel", "javascript", "data", "whatsapp"}:
        return None
    if parsed.netloc and parsed.netloc.lower() not in {"jftagro.com", "www.jftagro.com"}:
        return None
    raw = unquote(parsed.path)
    if not raw:
        return page
    if raw.endswith("/"):
        raw += "index.html"
    return (ROOT / raw.lstrip("/")) if raw.startswith("/") else (page.parent / raw)


def main() -> int:
    pages = sorted(
        p for p in ROOT.rglob("*.html")
        if not is_ignored(p)
        and p.name not in HELPERS
        and not p.name.startswith(("yandex_", "tmp-", "audit-"))
    )
    findings: dict[str, list[str]] = defaultdict(list)
    titles: dict[str, list[str]] = defaultdict(list)
    descriptions: dict[str, list[str]] = defaultdict(list)
    canonicals: dict[str, list[str]] = defaultdict(list)
    indexable: set[str] = set()
    page_data: dict[str, dict] = {}

    for page in pages:
        rel = label(page)
        text = page.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"<!doctype\s+html|<html\b", text, re.I):
            continue
        lower = text.lower()
        head_match = re.search(r"<head\b[^>]*>(.*?)</head>", text, re.I | re.S)
        head = head_match.group(1) if head_match else text
        title_match = re.findall(r"<title[^>]*>(.*?)</title>", head, re.I | re.S)
        title = clean_text(title_match[0]) if len(title_match) == 1 else ""
        metas = [attrs(t) for t in re.findall(r"<meta\b[^>]*>", head, re.I | re.S)]
        descs = [m.get("content", "") for m in metas if m.get("name", "").lower() == "description"]
        desc = descs[0].strip() if len(descs) == 1 else ""
        robots = " ".join(m.get("content", "").lower() for m in metas if m.get("name", "").lower() == "robots")
        noindex = "noindex" in robots
        if not noindex:
            indexable.add(rel)
            if len(title_match) != 1:
                findings["seo_title_missing_or_multiple"].append(rel)
            elif not 30 <= len(title) <= 65:
                findings["seo_title_length"].append(f"{rel} ({len(title)})")
            if len(descs) != 1 or not desc:
                findings["seo_description_missing_or_multiple"].append(rel)
            elif not 90 <= len(desc) <= 170:
                findings["seo_description_length"].append(f"{rel} ({len(desc)})")
            if title:
                language_key = rel.split("/", 1)[0] if "/" in rel else "en"
                titles[f"{language_key}:{title.casefold()}"].append(rel)
            if desc:
                language_key = rel.split("/", 1)[0] if "/" in rel else "en"
                descriptions[f"{language_key}:{desc.casefold()}"].append(rel)

        links = [attrs(t) for t in re.findall(r"<link\b[^>]*>", head, re.I | re.S)]
        canonical = [x.get("href", "") for x in links if x.get("rel", "").lower() == "canonical"]
        if len(canonical) != 1:
            findings["seo_canonical_missing_or_multiple"].append(rel)
        else:
            if not noindex:
                canonicals[canonical[0].casefold()].append(rel)
            if not noindex and canonical[0].rstrip("/") != expected_url(page).rstrip("/"):
                findings["seo_canonical_mismatch"].append(f"{rel} -> {canonical[0]}")

        html_tag = re.search(r"<html\b[^>]*>", text, re.I | re.S)
        language = attrs(html_tag.group(0)).get("lang", "") if html_tag else ""
        if not language:
            findings["accessibility_missing_html_lang"].append(rel)
        hreflangs = [x for x in links if x.get("rel", "").lower() == "alternate" and x.get("hreflang")]
        if not noindex and rel.split("/", 1)[0] in LOCALES and not any(x.get("hreflang", "").lower() == "x-default" for x in hreflangs):
            findings["international_missing_x_default"].append(rel)

        h1_count = len(re.findall(r"<h1\b", text, re.I))
        if h1_count != 1:
            findings["seo_h1_count"].append(f"{rel} ({h1_count})")

        ids = []
        for tag in re.findall(r"<[a-z][^>]*>", text, re.I | re.S):
            value = attrs(tag).get("id", "")
            if value and "${" not in value and "{{" not in value:
                ids.append(value)
        duplicates = [name for name, count in Counter(ids).items() if count > 1]
        if duplicates:
            findings["accessibility_duplicate_ids"].append(f"{rel}: {', '.join(duplicates[:5])}")

        images = [attrs(t) for t in re.findall(r"<img\b[^>]*>", text, re.I | re.S)]
        for image in images:
            source = image.get("src", "")
            if not source or "${" in source or "{{" in source:
                continue
            if "alt" not in image:
                findings["accessibility_image_missing_alt"].append(f"{rel}: {source}")
            if not image.get("width") or not image.get("height"):
                findings["performance_image_missing_dimensions"].append(f"{rel}: {source}")
            target = local_path(page, source) if source else None
            if target and not target.resolve().is_file():
                findings["crawl_missing_asset"].append(f"{rel}: {source}")

        tags_with_urls = re.findall(r"<(?:a|link|script|img|source|iframe)\b[^>]*>", text, re.I | re.S)
        for tag in tags_with_urls:
            data = attrs(tag)
            value = data.get("href") or data.get("src")
            if (
                not value
                or value.startswith("#")
                or any(token in value for token in ("${", "{{", "encodeURIComponent(", "' +", '" +'))
            ):
                continue
            if value.startswith("http://"):
                findings["security_insecure_http_reference"].append(f"{rel}: {value}")
            target = local_path(page, value)
            if target and not target.resolve().is_file():
                findings["crawl_broken_internal_reference"].append(f"{rel}: {value}")
            if tag.lower().startswith("<a") and data.get("target", "").lower() == "_blank" and "noopener" not in data.get("rel", "").lower():
                findings["security_new_tab_without_noopener"].append(f"{rel}: {value}")

        for block in re.findall(r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", text, re.I | re.S):
            try:
                json.loads(block)
            except json.JSONDecodeError:
                findings["seo_invalid_jsonld"].append(rel)

        # Raw HTML is compressed at the CDN. Keep this aligned with the
        # explicit 250 KB interactive-document budget in audit_performance.py.
        if page.stat().st_size > 250_000:
            findings["performance_oversized_html"].append(f"{rel} ({page.stat().st_size})")
        page_data[rel] = {"title": title, "description": desc, "canonical": canonical[0] if len(canonical) == 1 else "", "noindex": noindex, "h1_count": h1_count, "images": len(images), "hreflang_count": len(hreflangs)}

    for name, values in (("seo_duplicate_title", titles), ("seo_duplicate_description", descriptions), ("seo_duplicate_canonical", canonicals)):
        for _, affected in values.items():
            if len(affected) > 1:
                findings[name].append(", ".join(affected))

    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [node.text.strip() for node in tree.findall(".//s:loc", ns) if node.text]
    for url, count in Counter(sitemap_urls).items():
        if count > 1:
            findings["sitemap_duplicate_url"].append(url)
    sitemap_rels: set[str] = set()
    for url in sitemap_urls:
        parsed = urlsplit(url)
        rel = parsed.path.lstrip("/") or "index.html"
        if rel.endswith("/"):
            rel += "index.html"
        sitemap_rels.add(rel)
        if not (ROOT / unquote(rel)).is_file():
            findings["sitemap_missing_file"].append(url)
        elif rel in page_data and page_data[rel]["noindex"]:
            findings["sitemap_contains_noindex"].append(url)
    for rel in sorted(indexable - sitemap_rels):
        if rel not in {"404.html", "thank-you.html"}:
            findings["sitemap_indexable_page_missing"].append(rel)

    for path in ROOT.rglob("*"):
        if not path.is_file() or is_ignored(path) or path.name.startswith(("tmp-", "audit-")):
            continue
        suffix = path.suffix.lower()
        size = path.stat().st_size
        if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"} and size > 500_000:
            findings["performance_large_image"].append(f"{label(path)} ({size})")
        if suffix in {".mp4", ".webm"} and size > 3_000_000:
            findings["performance_large_video"].append(f"{label(path)} ({size})")

    summary = {key: len(value) for key, value in sorted(findings.items())}
    payload = {"scope": {"html_files": len(pages), "renderable_pages": len(page_data), "sitemap_urls": len(sitemap_urls), "indexable_pages": len(indexable)}, "summary": summary, "findings": dict(findings)}
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "full-site-audit.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Full Site Static Audit", "", f"- HTML files: {len(pages)}", f"- Renderable pages: {len(page_data)}", f"- Sitemap URLs: {len(sitemap_urls)}", f"- Indexable pages: {len(indexable)}", "", "## Findings", ""]
    for key, count in summary.items():
        lines.append(f"### {key} ({count})")
        lines.extend(f"- {item}" for item in findings[key][:20])
        if count > 20:
            lines.append(f"- ... {count - 20} more (see JSON report)")
        lines.append("")
    (REPORTS / "full-site-audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload["scope"], indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
