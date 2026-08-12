#!/usr/bin/env python3
"""Audit blind spots: inventory, graph, fragments, forms, schema, locale and encoding."""

from __future__ import annotations

from collections import Counter, defaultdict
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "coverage-gap-audit.json"
LOCALES = {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}
HELPERS = {"header.html", "footer.html", "inner-page-hero-snippet.html", "seo-universal-head-snippet.html", "product-page-template.html"}
MOJIBAKE = ("â€”", "â€“", "â€™", "â€œ", "â€", "Ã©", "Â©", "ï¿½", "�")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def local_target(page: Path, value: str) -> tuple[Path | None, str]:
    parsed = urlsplit(unescape(value.strip()))
    if parsed.scheme in {"mailto", "tel", "javascript", "data", "whatsapp"}:
        return None, ""
    if parsed.scheme in {"http", "https"} and parsed.netloc.lower() not in {"jftagro.com", "www.jftagro.com"}:
        return None, ""
    raw = unquote(parsed.path)
    target = page if not raw else (ROOT / raw.lstrip("/") if raw.startswith("/") else page.parent / raw)
    if raw.endswith("/"):
        target /= "index.html"
    return target.resolve(), unquote(parsed.fragment)


def main() -> int:
    pages: dict[Path, dict] = {}
    findings: dict[str, list[str]] = defaultdict(list)
    inbound: Counter[Path] = Counter()
    outbound: dict[Path, set[Path]] = defaultdict(set)
    classification: Counter[str] = Counter()
    locale_noindex: Counter[str] = Counter()

    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts or "reports" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        renderable = bool(re.search(r"<!doctype\s+html|<html\b", text, re.I))
        noindex = bool(re.search(r'<meta\s+name=["\']robots["\'][^>]*\bnoindex\b', text, re.I))
        fallback = "jft-localization" in text and "english-fallback" in text
        redirect = bool(re.search(r'<meta\s+http-equiv=["\']refresh["\']', text, re.I))
        verification = path.name.startswith("yandex_")
        helper = path.name in HELPERS or verification or not renderable
        temporary = path.name.startswith(("tmp-", "audit-"))
        if temporary:
            kind = "temporary"
        elif helper:
            kind = "helper"
        elif redirect:
            kind = "legacy_redirect"
        elif fallback:
            kind = "locale_fallback"
        elif noindex:
            kind = "utility_noindex"
        else:
            kind = "indexable"
        classification[kind] += 1
        locale = path.parent.name if path.parent.name in LOCALES else "en"
        if noindex:
            locale_noindex[locale] += 1
        pages[path.resolve()] = {"text": text, "kind": kind, "locale": locale, "noindex": noindex}

    for path, info in pages.items():
        if info["kind"] == "helper":
            continue
        text = info["text"]
        soup = BeautifulSoup(text, "html.parser")
        ids = [node.get("id") for node in soup.find_all(attrs={"id": True})]
        duplicates = [key for key, count in Counter(ids).items() if count > 1]
        if duplicates:
            findings["duplicate_ids"].append(f"{rel(path)}: {', '.join(duplicates)}")

        html = soup.find("html")
        lang = (html.get("lang", "") if html else "").lower()
        expected = info["locale"]
        if info["kind"] != "locale_fallback" and expected != "en" and not lang.startswith(expected):
            findings["locale_lang_mismatch"].append(f"{rel(path)}: lang={lang or 'missing'}, expected={expected}")
        if expected == "ar" and info["kind"] != "locale_fallback" and (not html or html.get("dir") != "rtl"):
            findings["arabic_missing_rtl"].append(rel(path))

        for token in MOJIBAKE:
            if token in text:
                findings["encoding_mojibake"].append(f"{rel(path)}: {token}")
                break

        for script in soup.select('script[type="application/ld+json"]'):
            try:
                json.loads(script.string or "")
            except json.JSONDecodeError as error:
                findings["invalid_jsonld"].append(f"{rel(path)}: line {error.lineno}, column {error.colno}")

        for iframe in soup.find_all("iframe"):
            if not iframe.get("title"):
                findings["iframe_missing_title"].append(rel(path))
        for button in soup.find_all("button"):
            if button.find_parent("form") and not button.get("type"):
                findings["form_button_missing_type"].append(f"{rel(path)}: {button.get_text(' ', strip=True)[:50]}")

        for form in soup.find_all("form"):
            if not form.get("aria-label") and not form.get("aria-labelledby") and not form.get("id"):
                findings["unnamed_form"].append(rel(path))
            for control in form.find_all(["input", "select", "textarea"]):
                if control.get("type") in {"hidden", "submit", "button", "reset"}:
                    continue
                cid = control.get("id")
                wrapped = control.find_parent("label") is not None
                labelled = bool(control.get("aria-label") or control.get("aria-labelledby") or (cid and soup.find("label", attrs={"for": cid})))
                if not wrapped and not labelled:
                    findings["form_control_missing_label"].append(f"{rel(path)}: {control.name}[name={control.get('name','')}]")

        for node in soup.find_all(["a", "link"], href=True):
            target, fragment = local_target(path, node["href"])
            if target is None:
                continue
            if not target.exists():
                findings["broken_internal_target"].append(f"{rel(path)} -> {node['href']}")
                continue
            if target in pages:
                inbound[target] += 1
                outbound[path].add(target)
                if info["kind"] == "indexable" and pages[target]["noindex"] and node.name == "a":
                    key = "indexable_links_to_locale_fallback" if pages[target]["kind"] == "locale_fallback" else "indexable_links_to_other_noindex"
                    findings[key].append(f"{rel(path)} -> {rel(target)}")
            if fragment and target.suffix.lower() == ".html":
                target_text = pages.get(target, {}).get("text") or target.read_text(encoding="utf-8", errors="replace")
                if not re.search(rf'\b(?:id|name)=["\']{re.escape(fragment)}["\']', target_text, re.I):
                    findings["broken_fragment"].append(f"{rel(path)} -> {node['href']}")

        for node in soup.find_all(["img", "script", "source"], src=True):
            target, _ = local_target(path, node["src"])
            if target is not None and not target.exists() and "${" not in node["src"]:
                findings["broken_local_asset"].append(f"{rel(path)} -> {node['src']}")

    for path, info in pages.items():
        if info["kind"] == "indexable" and inbound[path] == 0 and path.name != "index.html":
            findings["orphan_indexable_page"].append(rel(path))

    payload = {
        "summary": {
            "html_files": len(pages),
            "classification": dict(classification),
            "noindex_by_locale": dict(locale_noindex),
            "finding_counts": {key: len(set(values)) for key, values in sorted(findings.items())},
        },
        "findings": {key: sorted(set(values)) for key, values in sorted(findings.items())},
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
