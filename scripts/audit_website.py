#!/usr/bin/env python3
"""Read-only structural audit for every renderable page in the static site."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".git", ".github", "__pycache__", "backup"}
HELPERS = {
    "cookie-consent-snippet.html",
    "footer.html",
    "header.html",
    "inner-page-hero-snippet.html",
    "product-page-template.html",
    "seo-universal-head-snippet.html",
}
EXTERNAL_SCHEMES = {"data", "http", "https", "mailto", "tel", "javascript", "whatsapp"}
UNPUBLISHED_BLOGS = {
    "blog-basmati-rice-import-uae-esma-standards.html",
    "blog-black-pepper-powder-export-india-2026.html",
    "blog-cif-fob-explained.html",
    "blog-coriander-seeds-export-india-2026.html",
    "blog-eu-mrl-basmati.html",
    "blog-fennel-seeds-export-india-2026.html",
    "blog-fenugreek-seeds-export-india-2026.html",
    "blog-fssai-apeda-agmark-certifications-explained.html",
    "blog-groundnut-peanut-export-india-2026.html",
    "blog-import-indian-spices-uk-europe.html",
    "blog-indian-spice-export-middle-east-gulf.html",
    "blog-india-uae-cepa.html",
    "blog-indian-white-rice-export-policy-2026-latest-updates.html",
    "blog-ir64-africa.html",
    "blog-lc-vs-tt.html",
    "blog-moringa-powder-export-india-2026.html",
    "blog-phytosanitary-certificate-india-exports.html",
    "blog-private-label-rice.html",
    "blog-sesame-export-2026.html",
    "blog-spice-trends-2026.html",
    "blog-sugar-s30-export-india-2026.html",
    "blog-toor-dal-export-india-2026.html",
    "blog-wheat-flour-atta-export-india-2026.html",
    "blog-yellow-maize-export-india-2026.html",
}


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS or part.startswith("backup_") for part in path.parts)


def page_paths() -> list[Path]:
    pages = []
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if is_ignored(relative) or path.name in HELPERS or path.name.startswith("yandex_"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"<!doctype\s+html|<html\b", text, re.I):
            pages.append(path)
    return sorted(pages)


def local_target(page: Path, raw_url: str) -> tuple[Path | None, str]:
    parsed = urlsplit(raw_url.strip())
    if parsed.netloc.lower() in {"jftagro.com", "www.jftagro.com"}:
        path_text = unquote(parsed.path or "/")
        relative = path_text.lstrip("/")
        if not relative or path_text.endswith("/"):
            relative += "index.html"
        target = ROOT / relative
        return target.resolve(), unquote(parsed.fragment)
    if parsed.scheme.lower() in EXTERNAL_SCHEMES or parsed.netloc or raw_url.startswith("//"):
        return None, parsed.fragment
    path_text = unquote(parsed.path)
    if path_text.startswith("#"):
        return None, path_text[1:]
    if not path_text:
        return page, unquote(parsed.fragment)
    target = ROOT / path_text.lstrip("/") if path_text.startswith("/") else page.parent / path_text
    return target.resolve(), unquote(parsed.fragment)


def label(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def audit() -> dict[str, list[str]]:
    pages = page_paths()
    findings: dict[str, list[str]] = defaultdict(list)
    parsed_pages: dict[Path, BeautifulSoup] = {}

    for page in pages:
        relative = label(page)
        text = page.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(text, "html.parser")
        parsed_pages[page.resolve()] = soup

        title = soup.find("title")
        description = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
        html = soup.find("html")
        robots = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
        noindex = bool(robots and "noindex" in robots.get("content", "").lower())
        localized = page.parent.name in {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}

        for malformed in re.findall(r"https?://([^/\s\"'<>]+)", text, re.I):
            hostname = malformed.lower().rstrip(".")
            if hostname.startswith("jftagro.com") and hostname != "jftagro.com":
                findings["malformed_first_party_url"].append(f"{relative}: {hostname}")

        if localized:
            if re.search(r"\bi:\s*['\"]images/", text):
                findings["broken_dynamic_product_asset"].append(relative)
            if re.search(r"(?:fetch\(|\.href\s*=\s*)['\"]assets/", text):
                findings["broken_dynamic_local_asset"].append(relative)
            if re.search(
                r"(?:loadHTML|loadComponent|loadComp)\([^\n]*?['\"](?:header|footer)\.html['\"]",
                text,
            ):
                findings["broken_dynamic_component_path"].append(relative)
        if page.name == "packing-calculator.html" and (
            "volume:25.8" in text
            or "const PACK_EFF = { 1:.78, 5:.82, 10:.85, 25:.87, 50:.88 }" in text
        ):
            findings["outdated_packing_capacity_model"].append(relative)
        if not title or not title.get_text(strip=True):
            findings["missing_title"].append(relative)
        if not description or not description.get("content", "").strip():
            findings["missing_description"].append(relative)
        if not canonical or not canonical.get("href", "").strip():
            findings["missing_canonical"].append(relative)
        if not html or not html.get("lang", "").strip():
            findings["missing_language"].append(relative)

        headings = soup.find_all("h1")
        if len(headings) != 1:
            findings["invalid_h1_count"].append(f"{relative}: {len(headings)}")

        ids = [tag["id"] for tag in soup.find_all(attrs={"id": True})]
        for duplicate, count in Counter(ids).items():
            if count > 1:
                findings["duplicate_ids"].append(f"{relative}: #{duplicate} ({count})")

        for image in soup.find_all("img"):
            if not image.has_attr("alt"):
                findings["missing_image_alt"].append(f"{relative}: {image.get('src', '<no src>')}")
            source = image.get("src", "")
            if source and "${" not in source and (not image.get("width") or not image.get("height")):
                findings["missing_image_dimensions"].append(f"{relative}: {image.get('src', '<no src>')}")

        for form in soup.find_all("form"):
            for control in form.find_all(["input", "select", "textarea"]):
                hidden = (
                    control.get("type", "").lower() == "hidden"
                    or control.get("aria-hidden") == "true"
                    or "display:none" in control.get("style", "").replace(" ", "").lower()
                )
                if hidden:
                    continue
                control_id = control.get("id", "")
                labelled = bool(
                    control.get("aria-label")
                    or control.get("aria-labelledby")
                    or control.find_parent("label")
                )
                if control_id and soup.find("label", attrs={"for": control_id}):
                    labelled = True
                if not labelled:
                    findings["unlabelled_form_control"].append(
                        f"{relative}: {control.name}#{control_id or '<no id>'}"
                    )

        for control in soup.find_all(["a", "button"]):
            if control.get("aria-hidden") == "true":
                continue
            text_name = control.get_text(" ", strip=True)
            image_name = any(image.get("alt", "").strip() for image in control.find_all("img"))
            named = bool(
                text_name
                or image_name
                or control.get("aria-label", "").strip()
                or control.get("aria-labelledby", "").strip()
                or control.get("title", "").strip()
            )
            if not named:
                findings["unnamed_interactive_control"].append(
                    f"{relative}: {control.name}#{control.get('id', '<no id>')}"
                )

        for click_target in soup.find_all(["div", "span", "li"], onclick=True):
            keyboard_ready = (
                click_target.get("role") in {"button", "checkbox", "link", "tab"}
                and click_target.get("tabindex") == "0"
                and click_target.has_attr("onkeydown")
            )
            if not keyboard_ready and "nav-overlay" not in click_target.get("class", []):
                findings["non_keyboard_click_target"].append(
                    f"{relative}: {click_target.name}.{'.'.join(click_target.get('class', [])) or '<no class>'}"
                )

        for button in soup.find_all("button"):
            if button.find_parent("form") and not button.has_attr("type"):
                findings["implicit_form_button_type"].append(
                    f"{relative}: button#{button.get('id', '<no id>')}"
                )

        for frame in soup.find_all("iframe"):
            if not frame.get("title", "").strip() and not frame.get("aria-label", "").strip():
                findings["unnamed_iframe"].append(f"{relative}: {frame.get('src', '<no src>')}")

        for element in soup.find_all(attrs={"tabindex": True}):
            try:
                positive_tabindex = int(element["tabindex"]) > 0
            except (TypeError, ValueError):
                positive_tabindex = False
            if positive_tabindex:
                findings["positive_tabindex"].append(
                    f"{relative}: {element.name}#{element.get('id', '<no id>')}={element['tabindex']}"
                )

        if not noindex:
            for anchor in soup.find_all("a", href=True):
                href = anchor.get("href", "").strip()
                if href == "#" and anchor.get("id") not in {"m-blog-link", "ctaWA"}:
                    findings["dead_placeholder_link"].append(
                        f"{relative}: {anchor.get_text(' ', strip=True)[:80]}"
                    )
                target, _ = local_target(page, href)
                if target and target.name in UNPUBLISHED_BLOGS:
                    findings["link_to_unpublished_blog"].append(f"{relative} -> {href}")

            if page.name in UNPUBLISHED_BLOGS:
                findings["published_incomplete_blog"].append(relative)
            if "Placeholder article" in text:
                findings["published_placeholder_content"].append(relative)
            if page.name.startswith("blog-") and page.name != "blog-basmati-export-guide.html":
                h1 = soup.find("h1")
                if h1 and "1121 vs 1509 Basmati Rice" in h1.get_text(" ", strip=True):
                    findings["cloned_blog_content"].append(relative)

        if page.name == "blog.html":
            cards = soup.select("a.article-card[data-cat]")
            category_counts = Counter(card.get("data-cat") for card in cards)
            expected_counts = {
                "All Articles": len(cards),
                "Buyer Guides": category_counts["buyer-guide"],
                "Market Intelligence": category_counts["market"],
                "Compliance & Docs": category_counts["compliance"],
            }
            for button in soup.select("button.filter-btn"):
                label_text = button.get_text(" ", strip=True)
                for label_text_prefix, expected in expected_counts.items():
                    if label_text.startswith(label_text_prefix):
                        count = button.select_one(".filter-count")
                        actual = int(count.get_text(strip=True)) if count and count.get_text(strip=True).isdigit() else -1
                        if actual != expected:
                            findings["incorrect_blog_filter_count"].append(
                                f"{relative}: {label_text_prefix}={actual}, expected {expected}"
                            )
            for card in cards:
                image = card.select_one(".card-img img[src]")
                if not image:
                    findings["missing_blog_card_image"].append(
                        f"{relative}: {card.get('href', '<no href>')}"
                    )
                    continue
                target, _ = local_target(page, image.get("src", ""))
                if not target or not target.is_file():
                    findings["broken_blog_card_image"].append(
                        f"{relative}: {image.get('src', '<no src>')}"
                    )
                if "ANIMAL FEED" in image.get("src", ""):
                    findings["generic_blog_card_image"].append(
                        f"{relative}: {card.get('href', '<no href>')}"
                    )

        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                json.loads(script.string or "")
            except (json.JSONDecodeError, TypeError) as error:
                findings["invalid_json_ld"].append(f"{relative}: {error}")

        references = []
        references.extend((tag, tag.get("href", "")) for tag in soup.find_all("a", href=True))
        references.extend((tag, tag.get("src", "")) for tag in soup.find_all(src=True))
        references.extend((tag, tag.get("href", "")) for tag in soup.find_all("link", href=True))
        references.extend((tag, tag.get("poster", "")) for tag in soup.find_all(poster=True))
        references.extend((tag, tag.get("action", "")) for tag in soup.find_all("form", action=True))
        css_urls = re.findall(r"url\(\s*['\"]?([^)'\"\s]+)['\"]?\s*\)", text, re.I)
        references.extend((None, url) for url in css_urls)
        for tag, raw_url in references:
            if not raw_url or "${" in raw_url or "{{" in raw_url:
                continue
            target, fragment = local_target(page, raw_url)
            if target is None:
                if tag and tag.name == "a" and tag.get("target") == "_blank":
                    rel = set(tag.get("rel", []))
                    if "noopener" not in rel:
                        findings["unsafe_blank_target"].append(f"{relative}: {raw_url}")
                continue
            if not target.is_file():
                findings["broken_local_reference"].append(f"{relative} -> {raw_url}")
                continue
            if tag and tag.name == "a" and fragment and target.suffix.lower() == ".html":
                target_soup = parsed_pages.get(target)
                if target_soup is None:
                    target_soup = BeautifulSoup(target.read_text(encoding="utf-8", errors="replace"), "html.parser")
                    parsed_pages[target] = target_soup
                if target_soup.find(id=fragment) is None and target_soup.find(attrs={"name": fragment}) is None:
                    findings["broken_fragment"].append(f"{relative} -> {raw_url}")

    return {name: sorted(set(items)) for name, items in sorted(findings.items())}


def main() -> int:
    pages = page_paths()
    findings = audit()
    print(f"Audited {len(pages)} renderable HTML pages.")
    total = sum(len(items) for items in findings.values())
    for name, items in findings.items():
        print(f"\n{name.upper()} ({len(items)})")
        for item in items[:20]:
            print(f"  - {item}")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")
    print(f"\nTotal findings: {total}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
