#!/usr/bin/env python3
"""Translate intentional English fallback pages without touching code or URLs."""

from __future__ import annotations

import json
import socket
from pathlib import Path
import re
import time
from urllib.parse import quote

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString
import requests


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
MARKER = '<meta name="jft-localization" content="english-fallback">'
CACHE_PATH = ROOT / "data" / "localized-copy-cache.json"
TRANSLATABLE_META = {
    ("name", "description"), ("property", "og:title"), ("property", "og:description"),
    ("name", "twitter:title"), ("name", "twitter:description"),
}
SKIP_PARENTS = {"script", "style", "noscript", "code", "pre", "svg"}
LEGAL_NOTICE = "This translation is provided for convenience. If versions differ, the English version governs."


def worth_translating(value: str) -> bool:
    text = " ".join(value.split())
    if not text or not re.search(r"[A-Za-z]", text):
        return False
    if re.fullmatch(r"(?:https?://|mailto:|tel:|wa\.me/).*", text, re.I):
        return False
    if re.fullmatch(r"[A-Z0-9._/+:% -]{1,18}", text) and not re.search(r"[a-z]", text):
        return False
    return True


def collect_strings(paths: list[Path]) -> list[str]:
    values: set[str] = {LEGAL_NOTICE}
    for path in paths:
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
        for node in soup.find_all(string=True):
            if not isinstance(node, (Comment, Doctype)) and node.parent and node.parent.name not in SKIP_PARENTS:
                value = " ".join(str(node).split())
                if worth_translating(value):
                    values.add(value)
        for element in soup.find_all(True):
            for attribute in ("title", "placeholder", "aria-label"):
                value = " ".join(element.get(attribute, "").split())
                if worth_translating(value):
                    values.add(value)
        title = soup.title
        if title:
            value = " ".join(title.get_text(" ", strip=True).split())
            if worth_translating(value):
                values.add(value)
        for attr, key in TRANSLATABLE_META:
            for element in soup.find_all("meta", attrs={attr: key}):
                value = " ".join(element.get("content", "").split())
                if worth_translating(value):
                    values.add(value)
    return sorted(values)


def batches(values: list[str], limit: int = 2800):
    current: list[str] = []
    length = 0
    for value in values:
        addition = len(value) + 30
        if current and length + addition > limit:
            yield current
            current, length = [], 0
        current.append(value)
        length += addition
    if current:
        yield current


def request_translation(session: requests.Session, language: str, text: str) -> str:
    params = {"client": "gtx", "sl": "en", "tl": language, "dt": "t", "q": text}
    last_error: Exception | None = None
    for attempt in range(12):
        try:
            response = session.get("https://translate.googleapis.com/translate_a/single", params=params, timeout=45)
            response.raise_for_status()
            return "".join(part[0] for part in response.json()[0] if part and part[0])
        except (requests.RequestException, ValueError, TypeError, socket.gaierror) as error:
            last_error = error
            time.sleep(min(45, 2.5 * (attempt + 1)))
    raise RuntimeError(f"Translation request failed after retries: {last_error}")


class TranslationCoverageError(Exception):
    """Raised when the governed cache does not yet cover every current source string.

    Callers that must stay offline and deterministic (e.g. build_locale_ui.py,
    part of the CI generator chain) should use require_cached_translations()
    instead of translate_values() and treat this as a hard failure: it means a
    source page changed and the cache needs an explicit authoring pass (running
    translate_values()/this module's CLI entry points, which do call the
    network) before the deterministic build can succeed again.
    """


def require_cached_translations(language: str, values: list[str], cache: dict[str, dict[str, str]]) -> dict[str, str]:
    """Offline, network-free translation lookup for the deterministic build path.

    Every value must already be present in data/localized-copy-cache.json for
    this language. Never calls translate.googleapis.com or any other network
    service, so it is safe to use in CI or with network access disabled. Raises
    TranslationCoverageError (listing every missing string) rather than
    silently falling back to English or attempting a live translation.
    """
    translated = cache.get(language, {})
    missing = [value for value in values if value not in translated]
    if missing:
        preview = "; ".join(repr(value) for value in missing)
        raise TranslationCoverageError(
            f"{language}: {len(missing)} source string(s) not yet in data/localized-copy-cache.json: {preview}"
        )
    return {value: translated[value] for value in values}


def translate_values(language: str, values: list[str], cache: dict[str, dict[str, str]]) -> dict[str, str]:
    translated = cache.setdefault(language, {})
    missing = [value for value in values if value not in translated]
    session = requests.Session()
    session.headers.update({"User-Agent": "JFT-Agro-Localization/1.0"})
    groups = list(batches(missing))
    for number, group in enumerate(groups, 1):
        separators = [f"__JFT_SPLIT_{index:04d}__" for index in range(1, len(group))]
        payload_parts: list[str] = []
        for index, value in enumerate(group):
            if index:
                payload_parts.append(separators[index - 1])
            payload_parts.append(value)
        output = request_translation(session, language, "\n".join(payload_parts))
        pattern = "|".join(re.escape(separator) for separator in separators)
        pieces = re.split(rf"\s*(?:{pattern})\s*", output) if pattern else [output]
        if len(pieces) != len(group):
            pieces = [request_translation(session, language, value) for value in group]
        translated.update({source: target.strip() or source for source, target in zip(group, pieces)})
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        if number % 10 == 0 or number == len(groups):
            print(f"{language}: translated {number}/{len(groups)} batches", flush=True)
        time.sleep(0.08)
    return translated


def replace_node_text(node: NavigableString, mapping: dict[str, str]) -> None:
    raw = str(node)
    normalized = " ".join(raw.split())
    if normalized not in mapping:
        return
    leading = raw[: len(raw) - len(raw.lstrip())]
    trailing = raw[len(raw.rstrip()) :]
    node.replace_with(leading + mapping[normalized] + trailing)


def localize_page(path: Path, language: str, mapping: dict[str, str]) -> None:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html5lib")
    was_fallback = bool(soup.select_one('meta[name="jft-localization"][content="english-fallback"]'))
    for marker in soup.select('meta[name="jft-localization"][content="english-fallback"]'):
        marker.decompose()
    if soup.html:
        soup.html["lang"] = language
        if language == "ar":
            soup.html["dir"] = "rtl"
        elif soup.html.has_attr("dir"):
            del soup.html["dir"]
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, (Comment, Doctype)) and node.parent and node.parent.name not in SKIP_PARENTS:
            replace_node_text(node, mapping)
    for element in soup.find_all(True):
        for attribute in ("title", "placeholder", "aria-label"):
            raw = element.get(attribute, "")
            normalized = " ".join(raw.split())
            if normalized in mapping:
                element[attribute] = mapping[normalized]
    for attr, key in TRANSLATABLE_META:
        for element in soup.find_all("meta", attrs={attr: key}):
            raw = " ".join(element.get("content", "").split())
            if raw in mapping:
                element["content"] = mapping[raw]
    if was_fallback:
        source_path = ROOT / path.name
        source_noindex = False
        if source_path.exists():
            source_soup = BeautifulSoup(source_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
            source_robots = source_soup.find("meta", attrs={"name": lambda value: value and value.lower() == "robots"})
            source_noindex = bool(source_robots and "noindex" in source_robots.get("content", "").lower())
        robots = soup.find("meta", attrs={"name": "robots"})
        if robots:
            robots["content"] = "noindex,follow" if source_noindex else "index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1"
        elif soup.head:
            tag = soup.new_tag("meta")
            tag["name"], tag["content"] = "robots", "noindex,follow" if source_noindex else "index,follow,max-snippet:-1,max-image-preview:large"
            soup.head.append(tag)
        localized_url = f"https://jftagro.com/{language}/{path.name}"
        canonical = soup.find("link", rel="canonical")
        if canonical:
            canonical["href"] = localized_url
        og_url = soup.find("meta", attrs={"property": "og:url"})
        if og_url:
            og_url["content"] = localized_url
    if path.name in {"legal.html", "terms.html"}:
        notice = soup.new_tag("div", attrs={"class": "jft-legal-translation-note", "role": "note"})
        notice.string = mapping.get(LEGAL_NOTICE, LEGAL_NOTICE)
        target = soup.find(id="main-content") or soup.find("main")
        if target:
            target.insert(0, notice)
        style = soup.new_tag("style")
        style.string = ".jft-legal-translation-note{margin:16px auto;padding:12px 18px;max-width:1180px;background:#fff8e3;border-inline-start:4px solid #eebf45;color:#25453c;font:700 .82rem/1.5 Arial,sans-serif}"
        if soup.head:
            soup.head.append(style)
    rendered = str(soup)
    if not re.match(r"\s*<!doctype\s+html>", rendered, re.I):
        rendered = "<!DOCTYPE html>\n" + re.sub(r"^[^<]*?(?=<html\b)", "", rendered, count=1, flags=re.I | re.S)
    path.write_text(rendered, encoding="utf-8", newline="\n")


def main() -> int:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    total = 0
    for language in LOCALES:
        paths = sorted(
            path for path in (ROOT / language).glob("*.html")
            if BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
            .select_one('meta[name="jft-localization"][content="english-fallback"]')
        )
        if not paths:
            print(f"{language}: no fallback pages")
            continue
        values = collect_strings(paths)
        print(f"{language}: {len(paths)} pages, {len(values)} unique strings", flush=True)
        mapping = translate_values(language, values, cache)
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        for path in paths:
            localize_page(path, language, mapping)
            total += 1
    print(f"Localized {total} fallback pages.")
    return 0


def localize_all_pages() -> int:
    """Translate source-matched visible English residue across every locale page."""
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    source_paths = sorted(
        path for path in ROOT.glob("*.html")
        if path.name not in {"header.html", "footer.html", "inner-page-hero-snippet.html", "seo-universal-head-snippet.html"}
        and "<html" in path.read_text(encoding="utf-8", errors="replace").lower()
    )
    values = collect_strings(source_paths)
    total = 0
    for language in LOCALES:
        paths = [ROOT / language / path.name for path in source_paths if (ROOT / language / path.name).exists()]
        print(f"{language}: completing {len(paths)} pages against {len(values)} source strings", flush=True)
        mapping = translate_values(language, values, cache)
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        for path in paths:
            localize_page(path, language, mapping)
            total += 1
    print(f"Completed full visible-copy localization for {total} pages.")
    return 0


def translate_remaining_residue() -> int:
    """Translate visible English strings still present after exact source matching."""
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    total = 0
    for language in LOCALES:
        paths = sorted(
            path for path in (ROOT / language).glob("*.html")
            if path.name not in {"inner-page-hero-snippet.html", "seo-universal-head-snippet.html"}
            and "<html" in path.read_text(encoding="utf-8", errors="replace").lower()
        )
        values: set[str] = set()
        for path in paths:
            soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
            for node in soup.find_all(string=True):
                if isinstance(node, (Comment, Doctype)) or not node.parent or node.parent.name in SKIP_PARENTS:
                    continue
                value = " ".join(str(node).split())
                if len(value.split()) >= 4 and worth_translating(value) and re.search(r"\b(?:the|and|with|from|this|that|your|buyer|export|import|request|quality|product|shipping|document|price|market)\b", value, re.I):
                    values.add(value)
        print(f"{language}: translating {len(values)} remaining English strings", flush=True)
        mapping = translate_values(language, sorted(values), cache)
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        for path in paths:
            localize_page(path, language, mapping)
            total += 1
    print(f"Applied residue cleanup to {total} pages.")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(translate_remaining_residue() if "--residue" in sys.argv else localize_all_pages() if "--all" in sys.argv else main())
