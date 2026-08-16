"""Strengthen multilingual SEO metadata without changing visible page content.

The sitemap is the source of truth: only indexable pages listed there are edited.
This keeps intentionally noindex translations out of hreflang/indexing clusters.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://jftagro.com/"
LOCALE_TO_OG = {
    "en": "en_IN",
    "ar": "ar_AE",
    "es": "es_ES",
    "fr": "fr_FR",
    "id": "id_ID",
    "ms": "ms_MY",
    "pt": "pt_BR",
    "ru": "ru_RU",
    "si": "si_LK",
    "th": "th_TH",
    "vi": "vi_VN",
}
CREATIVE_TYPES = {"Article", "Blog", "BlogPosting", "FAQPage", "HowTo", "WebPage"}

ABOUT_TITLES = {
    "ar": "عن JFT Agro Overseas | الشركة والتحقق للمشترين",
    "es": "Sobre JFT Agro Overseas | Empresa y verificación del comprador",
    "fr": "À propos de JFT Agro | Entreprise et vérification acheteur",
    "id": "Tentang JFT Agro Overseas | Profil dan Verifikasi Pembeli",
    "ms": "Tentang JFT Agro Overseas | Syarikat dan Pengesahan Pembeli",
    "pt": "Sobre a JFT Agro Overseas | Empresa e verificação do comprador",
    "ru": "О JFT Agro Overseas | Компания и проверка покупателем",
    "si": "JFT Agro Overseas ගැන | සමාගම සහ ගැනුම්කරු සත්‍යාපනය",
    "th": "เกี่ยวกับ JFT Agro Overseas | บริษัทและการตรวจสอบผู้ซื้อ",
    "vi": "Giới thiệu JFT Agro Overseas | Công ty và xác minh người mua",
}


def sitemap_urls() -> list[str]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(ROOT / "sitemap.xml")
    return [node.text.strip() for node in tree.getroot().findall("s:url/s:loc", ns)]


def path_for_url(url: str) -> Path:
    path = urlparse(url).path.lstrip("/")
    if not path:
        return ROOT / "index.html"
    result = ROOT / path
    if urlparse(url).path.endswith("/"):
        result /= "index.html"
    return result


def page_language(path: Path) -> str:
    relative = path.relative_to(ROOT).parts
    return relative[0] if relative and relative[0] in LOCALE_TO_OG else "en"


def canonical_from(text: str) -> str:
    match = re.search(
        r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*>',
        text,
        re.I,
    )
    return match.group(1) if match else ""


def title_from(text: str) -> str:
    match = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else "JFT Agro Overseas"


def ensure_social_locale(text: str, language: str) -> str:
    # Rebuild the locale family as one deterministic block, avoiding duplicates.
    text = re.sub(r'\s*<meta\b[^>]*property=["\']og:locale(?::alternate)?["\'][^>]*>', "", text, flags=re.I)
    values = [LOCALE_TO_OG[language], *[v for k, v in LOCALE_TO_OG.items() if k != language]]
    block = "\n  ".join(
        [f'<meta property="og:locale" content="{values[0]}">']
        + [f'<meta property="og:locale:alternate" content="{value}">' for value in values[1:]]
    )
    marker = re.search(r'<meta\b[^>]*property=["\']og:type["\'][^>]*>', text, re.I)
    if marker:
        return text[: marker.end()] + "\n  " + block + text[marker.end() :]
    return text.replace("</head>", f"  {block}\n</head>", 1)


def ensure_site_name(text: str) -> str:
    if re.search(r'<meta\b[^>]*property=["\']og:site_name["\']', text, re.I):
        return text
    return text.replace("</head>", '  <meta property="og:site_name" content="JFT Agro Overseas">\n</head>', 1)


def enrich_jsonld(text: str, language: str, canonical: str, indexable_urls: set[str]) -> str:
    pattern = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.I | re.S)

    def update(match: re.Match[str]) -> str:
        raw = match.group(2).strip()
        try:
            data = json.loads(raw)
        except (TypeError, ValueError):
            return match.group(0)

        def visit(obj: object) -> None:
            if isinstance(obj, dict):
                obj_type = obj.get("@type")
                types = set(obj_type if isinstance(obj_type, list) else [obj_type])
                if types & CREATIVE_TYPES:
                    obj.setdefault("inLanguage", language)
                    # A localized CreativeWork must identify its localized canonical,
                    # not the English source URL from which its markup was generated.
                    if "url" in obj:
                        obj["url"] = canonical
                    if "mainEntityOfPage" in obj:
                        value = obj["mainEntityOfPage"]
                        obj["mainEntityOfPage"] = (
                            {**value, "@id": canonical} if isinstance(value, dict) else canonical
                        )
                if "BreadcrumbList" in types and language != "en":
                    for item in obj.get("itemListElement", []):
                        if not isinstance(item, dict) or not isinstance(item.get("item"), str):
                            continue
                        target = item["item"]
                        if target == BASE:
                            candidate = f"{BASE}{language}/"
                        elif target.startswith(BASE) and not target.startswith(f"{BASE}{language}/"):
                            candidate = f"{BASE}{language}/{target[len(BASE):]}"
                        else:
                            continue
                        # Fragments identify an in-page section and are not present
                        # in sitemaps; validate their document URL instead.
                        if candidate.split("#", 1)[0] in indexable_urls:
                            item["item"] = candidate
                for value in obj.values():
                    visit(value)
            elif isinstance(obj, list):
                for value in obj:
                    visit(value)

        visit(data)
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    return pattern.sub(update, text)


def ensure_schema(text: str, language: str, canonical: str) -> str:
    if "application/ld+json" in text:
        return text
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": re.sub(r"<[^>]+>", "", title_from(text)),
        "url": canonical,
        "inLanguage": language,
        "isPartOf": {"@type": "WebSite", "name": "JFT Agro Overseas", "url": BASE},
        "publisher": {"@type": "Organization", "name": "JFT Agro Overseas", "url": BASE},
    }
    tag = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    return text.replace("</head>", f"  {tag}\n</head>", 1)


def localize_internal_links(
    text: str, language: str, canonical: str, indexable_urls: set[str]
) -> str:
    """Keep buyers inside their selected language when a translation exists."""
    if language == "en":
        return text

    anchor = re.compile(r'(<a\b[^>]*\bhref=["\'])([^"\']+)(["\'])', re.I)

    def update(match: re.Match[str]) -> str:
        href = match.group(2)
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            return match.group(0)
        absolute = urljoin(canonical, href)
        document, fragment = urldefrag(absolute)
        if not document.startswith(BASE):
            return match.group(0)
        relative = document[len(BASE) :]
        if relative.startswith(f"{language}/"):
            return match.group(0)
        candidate = f"{BASE}{language}/{relative}"
        if candidate not in indexable_urls:
            return match.group(0)
        localized = candidate + (f"#{fragment}" if fragment else "")
        return match.group(1) + localized + match.group(3)

    return anchor.sub(update, text)


def normalize_homepage_snippets(text: str) -> str:
    title = "Indian Rice, Spices & Pulses Exporter | JFT Agro"
    desc = (
        "JFT Agro Overseas supplies Indian rice, spices, pulses, grains and oilseeds to global buyers "
        "with agreed specifications, export packing and buyer-verification documents."
    )
    text = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", text, count=1, flags=re.I | re.S)
    text = re.sub(
        r'(<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\'])[^"\']*(["\'][^>]*>)',
        lambda m: m.group(1) + desc + m.group(2),
        text,
        count=1,
        flags=re.I,
    )
    for prop in ("og:title", "twitter:title"):
        text = re.sub(
            rf'(<meta\b(?=[^>]*(?:property|name)=["\']{re.escape(prop)}["\'])[^>]*\bcontent=["\'])[^"\']*(["\'][^>]*>)',
            lambda m: m.group(1) + title + m.group(2),
            text,
            count=1,
            flags=re.I,
        )
    for prop in ("og:description", "twitter:description"):
        text = re.sub(
            rf'(<meta\b(?=[^>]*(?:property|name)=["\']{re.escape(prop)}["\'])[^>]*\bcontent=["\'])[^"\']*(["\'][^>]*>)',
            lambda m: m.group(1) + desc + m.group(2),
            text,
            count=1,
            flags=re.I,
        )
    return text


def main() -> None:
    changed = 0
    urls = sitemap_urls()
    indexable_urls = set(urls)
    for url in urls:
        path = path_for_url(url)
        original = path.read_text(encoding="utf-8")
        text = original
        language = page_language(path)
        canonical = canonical_from(text) or url

        text = ensure_social_locale(text, language)
        text = ensure_site_name(text)
        text = ensure_schema(text, language, canonical)
        text = enrich_jsonld(text, language, canonical, indexable_urls)
        text = localize_internal_links(text, language, canonical, indexable_urls)

        if path == ROOT / "index.html":
            text = normalize_homepage_snippets(text)
        if path.name == "about.html" and language in ABOUT_TITLES:
            text = re.sub(r"<title>.*?</title>", f"<title>{ABOUT_TITLES[language]}</title>", text, count=1, flags=re.I | re.S)

        if text != original:
            path.write_text(text, encoding="utf-8", newline="")
            changed += 1

    print(f"Updated {changed} indexable pages from {len(urls)} sitemap URLs")


if __name__ == "__main__":
    main()
