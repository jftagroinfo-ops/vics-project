#!/usr/bin/env python3
"""Apply deterministic remediations from the 22 August forensic SEO audit.

The script intentionally does not approve editorial or localization records and
does not change indexation policy. Human review remains an external gate.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
LOCALES = {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}
IGNORED = {".git", ".cloudflare-dist", ".cloudflare-dist-predeploy", ".wrangler", "reports", "node_modules"}
DEFAULT_SOCIAL_IMAGE = "https://jftagro.com/images/homepage/export-trust-og.webp"
LINKEDIN_URLS = {
    "https://www.linkedin.com/company/jft-agro-overseas",
    "https://www.linkedin.com/company/jft-agro-overseas/",
}
BROKEN_URL_REPLACEMENTS = {
    "https://u.ae/en/information-and-services/health-and-fitness/food-safety-and-health-tips/national-food-accreditation-and-registration-system":
        "https://u.ae/en/information-and-services/health-and-fitness/food-safety-and-health-tips",
    "https://www.imexport.gov.lk/images/pdf/progresreport/2025/D_of_Import_and_Export_Control_E-PR-2024.pdf":
        "https://www.imexport.gov.lk/index.php/en/statistics-main/performance-reports.html",
}
PLACEHOLDER_LINK_REPLACEMENT = {
    '<p>Read the <a href="blog-toor-dal-export-india-2026.html">toor dal buyer guide</a>, compare <a href="green-mung-beans-exporter.html">green mung</a>, <a href="blog-how-to-write-agro-commodity-purchase-specification.html">write a specification</a> or <a href="sample-request.html">request a sample</a>.</p>':
        '<p>Compare <a href="green-mung-beans-exporter.html">green mung</a>, <a href="blog-how-to-write-agro-commodity-purchase-specification.html">write a measurable purchase specification</a>, review the <a href="export-documentation.html">export document centre</a> or <a href="sample-request.html">request a trade sample</a>.</p>',
}
CHART_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"
CHART_INTEGRITY = "sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ"
ADDRESS = "Godown N-2, APMC Market, Danabunder, Phase II, Sector 19, Vashi"
ENGLISH_DESCRIPTION_REFINEMENTS = {
    "index.html": "Source Indian rice, spices, pulses, grains and oilseeds with agreed specifications, export packing, lot controls and buyer-verification documents.",
    "1121-raw-basmati-rice-exporter.html": "Source Indian 1121 raw Basmati rice by variety identity, grain length, moisture, broken percentage, crop or age, packing, sampling and lot evidence.",
    "1121-steam-basmati-rice-exporter.html": "Source Indian 1121 steam Basmati rice by grain length, moisture, broken percentage, cooking performance, crop or age, packing and lot evidence.",
    "1121-white-sella-basmati-exporter.html": "Source Indian 1121 white Sella Basmati rice by processing form, grain length, moisture, broken percentage, cooking test, packing and lot evidence.",
    "1509-steam-basmati-rice-exporter.html": "Source Indian 1509 steam Basmati rice by variety identity, grain length, moisture, broken percentage, cooking performance, packing and lot evidence.",
    "blog-apeda-registration-indian-exporter-explained.html": "Verify an Indian exporter's APEDA registration, RCMC scope, IEC and Basmati-related documentation through current official records before contracting.",
    "blog-green-mung-beans-export-india-2026.html": "Import Indian green mung beans with measurable requirements for identity, form, size, defects, moisture, crop origin, food safety, packing and lot release.",
    "blog-how-to-choose-indian-agro-exporter.html": "Verify an Indian agro exporter through entity, IEC, GST and food-licence records, then match the contract, beneficiary bank and shipment evidence.",
    "blog-lc-vs-tt.html": "Compare letter of credit and telegraphic transfer for food imports by risk allocation, document control, bank charges, milestones and contract safeguards.",
    "blog-private-label-rice.html": "Plan private-label rice from India through variety selection, packaging, artwork approval, quality controls, MOQ, production workflow and export documents.",
    "celery-seeds-powder-exporter.html": "Source Indian celery seed or powder by botanical identity, whole or ground form, purity, moisture, volatile oil, microbiology, packing and lot evidence.",
    "certificates.html": "Verify JFT Agro registration, certification and shipment evidence, understand document scope and record the fields required before relying on any copy.",
    "chickpeas-kabuli-exporter.html": "Source Indian Kabuli chickpeas by botanical identity, verified calibre or count method, size distribution, crop origin, defects, moisture and lot evidence.",
    "coriander-seeds-exporter.html": "Source Indian coriander seed by identity, splits, purity, colour, volatile oil, residue plan and approved sample instead of relying on trade grade names.",
    "corn-gluten-meal-exporter.html": "Source Indian corn gluten meal for feed by material identity, protein basis, nutrients, contaminants, packing, destination approvals and lot evidence.",
    "corn-starch-exporter.html": "Source Indian native corn starch for food use by analytical and microbiological tests, application trial, packing requirements and lot documents.",
    "cotton-seed-oil-cake-exporter.html": "Source Indian cottonseed oil cake by extraction process, protein and fibre basis, moisture, residual oil, feed-safety limits, packing and lot evidence.",
    "deoiled-rice-bran-dorb-exporter.html": "Source Indian de-oiled rice bran by extraction and form, protein and fibre basis, moisture, ash, feed-safety limits, traceability and lot evidence.",
    "green-millet-bajra-exporter.html": "Source Indian green millet or Bajra by species identity, crop origin, moisture, foreign matter, grain condition, intended use, packing and lot evidence.",
    "green-mung-beans-exporter.html": "Source Indian whole green mung beans by botanical identity, size distribution, crop origin, defects, moisture, intended use, packing and lot evidence.",
    "india-agricultural-export-market-data-sources.html": "Download a source-reviewed directory of official Indian agricultural export, spice trade, commodity price and policy datasets with coverage notes.",
    "maize-grits-exporter.html": "Source Indian maize grits by degermed identity, sieve distribution, intended process, release tests, packing requirements and approved application sample.",
    "mustard-seeds-powder-exporter.html": "Source Indian mustard seed or powder by species, whole or ground form, purity, moisture, volatile oil, residue plan, packing and lot evidence.",
    "port-transit-calculator.html": "Plan indicative port-to-port transit and arrival windows from JNPA, Mundra or Chennai to 29 container ports with an adjustable contingency allowance.",
    "safflower-seeds-exporter.html": "Source Indian safflower seed by botanical identity, crop origin, intended crushing or feed use, moisture, defects, oil content, packing and lot evidence.",
    "terms.html": "Read JFT Agro Overseas terms covering payment, delivery, force majeure, disputes and liability. The signed contract controls each transaction.",
    "whatsapp-catalog.html": "Browse JFT Agro rice, spices, pulses and grains, then message the export desk with product, specification, quantity, destination and packing requirements.",
    "white-sorghum-jowar-exporter.html": "Source Indian white sorghum or Jowar by species identity, crop origin, moisture, foreign matter, intended use, packing and lot evidence.",
    "whole-nutmeg-powder-exporter.html": "Source Indian whole nutmeg or powder by botanical identity, whole or ground form, moisture, volatile oil, microbiology, packing and lot evidence.",
    "yellow-maize-corn-exporter.html": "Source Indian yellow maize by food, feed or processing intent with an agreed grade, testing and treatment plan, packing and destination requirements.",
}


def sitemap_paths() -> set[Path]:
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(ROOT / "sitemap.xml")
    paths: set[Path] = set()
    for node in tree.getroot().findall("s:url/s:loc", namespace):
        relative = (node.text or "").strip().removeprefix("https://jftagro.com/")
        paths.add(ROOT / (relative or "index.html") / "index.html" if relative.endswith("/") else ROOT / (relative or "index.html"))
    return paths


def eligible(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return not any(part in IGNORED or part.startswith("backup_") for part in relative.parts)


def meta_value(soup: BeautifulSoup, attribute: str, name: str) -> str:
    node = soup.find("meta", attrs={attribute: re.compile(rf"^{re.escape(name)}$", re.I)})
    return (node.get("content") or "").strip() if node else ""


def canonical_value(soup: BeautifulSoup) -> str:
    node = soup.find("link", rel=lambda value: value and "canonical" in value)
    return (node.get("href") or "").strip() if node else ""


def absolute_image(source: str, canonical: str) -> str:
    if not source:
        return ""
    if source.startswith(("https://", "http://")):
        return source.replace("http://jftagro.com/", "https://jftagro.com/")
    path = source.lstrip("./")
    if source.startswith("/"):
        return "https://jftagro.com" + source
    locale = urlsplit(canonical).path.strip("/").split("/")[0]
    if locale in LOCALES and source.startswith("../"):
        path = source[3:]
    return "https://jftagro.com/" + path


def social_metadata(source: str) -> str:
    soup = BeautifulSoup(source, "html.parser")
    if not soup.head:
        return source
    title = soup.title.get_text(" ", strip=True) if soup.title else "JFT Agro Overseas"
    description = meta_value(soup, "name", "description")
    canonical = canonical_value(soup)
    if not canonical or not description:
        return source
    og_title = meta_value(soup, "property", "og:title") or title
    og_description = meta_value(soup, "property", "og:description") or description
    og_url = meta_value(soup, "property", "og:url") or canonical
    og_image = meta_value(soup, "property", "og:image")
    if not og_image:
        image = soup.select_one('main img[src], article img[src], img[fetchpriority="high"][src]')
        og_image = absolute_image(image.get("src", ""), canonical) if image else DEFAULT_SOCIAL_IMAGE
    additions: list[str] = []
    values = [
        ("property", "og:title", og_title),
        ("property", "og:description", og_description),
        ("property", "og:url", og_url),
        ("property", "og:image", og_image),
        ("name", "twitter:card", "summary_large_image"),
        ("name", "twitter:title", og_title),
        ("name", "twitter:description", og_description),
        ("name", "twitter:image", og_image),
    ]
    for attribute, name, value in values:
        if not meta_value(soup, attribute, name):
            additions.append(f'  <meta {attribute}="{name}" content="{html.escape(value, quote=True)}">')
    if not additions:
        return source
    return re.sub(r"</head>", "\n".join(additions) + "\n</head>", source, count=1, flags=re.I)


def normalize_jsonld(source: str) -> str:
    def walk(value):
        if isinstance(value, list):
            return [walk(item) for item in value]
        if not isinstance(value, dict):
            return value
        result = {key: walk(item) for key, item in value.items()}
        node_type = result.get("@type")
        types = set(node_type if isinstance(node_type, list) else [node_type])
        if "Organization" in types and result.get("name") in {"JFT Agro Overseas", "JFT Agro Overseas LLP"}:
            result["name"] = "JFT Agro Overseas"
            result.setdefault("@id", "https://jftagro.com/#organization")
            if result.get("legalName"):
                result["legalName"] = "JFT Agro Overseas LLP"
        if "PostalAddress" in types and result.get("addressCountry") == "IN" and "Danabunder" in result.get("streetAddress", ""):
            result["streetAddress"] = ADDRESS
            result["addressRegion"] = "Maharashtra"
        if "sameAs" in result and isinstance(result["sameAs"], list):
            result["sameAs"] = [item for item in result["sameAs"] if item not in LINKEDIN_URLS]
            if not result["sameAs"]:
                result.pop("sameAs")
        return result

    def replace(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        updated = walk(data)
        if updated == data:
            return match.group(0)
        return '<script type="application/ld+json">' + json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + "</script>"

    return re.sub(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        replace,
        source,
        flags=re.I | re.S,
    )


def remove_broken_linkedin_anchors(source: str) -> str:
    pattern = r'<a\b[^>]*href=["\']https://www\.linkedin\.com/company/jft-agro-overseas/?["\'][^>]*>.*?</a>'
    return re.sub(pattern, "", source, flags=re.I | re.S)


def normalize_home_links(source: str, path: Path) -> str:
    relative = path.relative_to(ROOT)
    locale = relative.parts[0] if relative.parts and relative.parts[0] in LOCALES else ""

    def replace(match: re.Match[str]) -> str:
        quote, href = match.group(1), html.unescape(match.group(2))
        parsed = urlsplit(href)
        clean = parsed.path.replace("\\", "/")
        replacement = None
        if clean in {"/index.html", "../index.html"}:
            replacement = "/"
        elif clean == "index.html":
            replacement = f"/{locale}/" if locale else "/"
        else:
            found = re.fullmatch(r"/?(ar|es|fr|id|ms|pt|ru|si|th|vi)/index\.html", clean, re.I)
            if found:
                replacement = f"/{found.group(1).lower()}/"
        if replacement is None:
            return match.group(0)
        if parsed.query:
            replacement += "?" + parsed.query
        if parsed.fragment:
            replacement += "#" + parsed.fragment
        return f'href={quote}{replacement}{quote}'

    return re.sub(r'href=(["\'])([^"\']*index\.html(?:[?#][^"\']*)?)\1', replace, source, flags=re.I)


def pin_chart_js(source: str) -> str:
    pattern = r'<script\b([^>]*)\bsrc=["\']https://cdn\.jsdelivr\.net/npm/chart\.js["\']([^>]*)></script>'
    replacement = (
        f'<script src="{CHART_URL}" integrity="{CHART_INTEGRITY}" '
        'crossorigin="anonymous" defer></script>'
    )
    return re.sub(pattern, replacement, source, flags=re.I)


def correct_image_attributes(source: str) -> str:
    def update_logo(match: re.Match[str]) -> str:
        tag = re.sub(r'\swidth=["\'][^"\']*["\']', "", match.group(0), flags=re.I)
        tag = re.sub(r'\sheight=["\'][^"\']*["\']', "", tag, flags=re.I)
        return tag[:-1] + ' width="4501" height="2084">'

    def update_cert(match: re.Match[str]) -> str:
        tag = re.sub(r'\swidth=["\'][^"\']*["\']', "", match.group(0), flags=re.I)
        tag = re.sub(r'\sheight=["\'][^"\']*["\']', "", tag, flags=re.I)
        return tag[:-1] + ' width="720" height="347">'

    source = re.sub(r'<img\b[^>]*\bsrc=["\'][^"\']*jft%?20logo\.png["\'][^>]*>', update_logo, source, flags=re.I)
    source = re.sub(r'<img\b[^>]*\bsrc=["\'][^"\']*(?:FSSAI|APEDA|STAR HOUSE)\.webp["\'][^>]*>', update_cert, source, flags=re.I)
    source = re.sub(r'<span class="stat-bg">', '<span class="stat-bg" aria-hidden="true">', source)
    return source


def protect_lead_forms(source: str) -> str:
    source = re.sub(
        r'\s*<input\b[^>]*\bname=["\']access_key["\'][^>]*>',
        "",
        source,
        flags=re.I,
    )
    source = source.replace("https://api.web3forms.com/submit", "/api/lead")
    source = source.replace(" https://api.web3forms.com", "")
    return source


def fix_product_heading_order(source: str) -> str:
    return re.sub(
        r'(<div\s+class=["\']sfi-text["\']>\s*)<h4>([^<]*)</h4>',
        r'\1<h3>\2</h3>',
        source,
        flags=re.I,
    ).replace(".sfi-text h4", ".sfi-text h3")


def refine_english_description(source: str, path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    description = ENGLISH_DESCRIPTION_REFINEMENTS.get(relative)
    if not description:
        return source

    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        target = re.search(r'\b(?:name|property)=["\']([^"\']+)["\']', tag, re.I)
        if not target or target.group(1).casefold() not in {"description", "og:description", "twitter:description"}:
            return tag
        escaped = html.escape(description, quote=True)
        if re.search(r'\bcontent=(?:"[^"]*"|\'[^\']*\')', tag, re.I):
            return re.sub(r'\bcontent=(?:"[^"]*"|\'[^\']*\')', f'content="{escaped}"', tag, count=1, flags=re.I)
        return tag[:-1] + f' content="{escaped}">'

    return re.sub(r'<meta\b[^>]*>', replace, source, flags=re.I)


def remediate(path: Path, indexable: bool) -> bool:
    original = path.read_text(encoding="utf-8", errors="strict")
    updated = original.replace(" 'unsafe-eval'", "")
    for old, new in BROKEN_URL_REPLACEMENTS.items():
        updated = updated.replace(old, new)
    for old, new in PLACEHOLDER_LINK_REPLACEMENT.items():
        updated = updated.replace(old, new)
    updated = remove_broken_linkedin_anchors(updated)
    updated = normalize_jsonld(updated)
    updated = normalize_home_links(updated, path)
    updated = pin_chart_js(updated)
    updated = correct_image_attributes(updated)
    updated = protect_lead_forms(updated)
    updated = fix_product_heading_order(updated)
    updated = refine_english_description(updated, path)
    if indexable:
        updated = social_metadata(updated)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8", newline="")
    return True


def main() -> int:
    indexable = sitemap_paths()
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if eligible(path) and remediate(path, path in indexable):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"Applied forensic audit remediation to {len(changed)} HTML files.")
    print(f"Indexable pages considered for social metadata: {len(indexable)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
