#!/usr/bin/env python3
"""Release gate for unsupported claims and master-product/page consistency."""

from __future__ import annotations

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "products.json"
FORBIDDEN = {
    "absolute customs timing": re.compile(r"48[- ]hour customs", re.I),
    "absolute zero-claim wording": re.compile(r"zero[- ]claim|zero claim guarantee", re.I),
    "unsupported container volume": re.compile(r"(?:382\+?\s*TEU|500\+?\s*containers)", re.I),
    "unsupported capacity": re.compile(r"250\s*MT(?:\s*/\s*day|\s+per\s+day)", re.I),
    "unsupported country count": re.compile(r"25\+\s*(?:countries|global destinations)", re.I),
    "mis-scoped laboratory claim": re.compile(r"(?:in-house\s+)?NABL[- ]certified\s+lab", re.I),
    "unqualified ISO claim": re.compile(r"ISO 9001:2015 certified", re.I),
    "unqualified APEDA claim": re.compile(r"APEDA registered(?: exporter)?", re.I),
    "unqualified HACCP claim": re.compile(r"HACCP certified", re.I),
    "unqualified status-holder claim": re.compile(r"Government recogn(?:is|iz)ed Star Export House", re.I),
    "unsupported company-history date": re.compile(r"\b1980\b", re.I),
    "fixed response-time promise": re.compile(r"(?:within one business day|4 business hours|under 24 hours)", re.I),
    "named-carrier guarantee": re.compile(r"(?:Maersk).{0,160}(?:MSC).{0,160}(?:CMA).{0,160}(?:guarantee|ensure|committed slot)", re.I | re.S),
    "fixed split payment terms": re.compile(r"30\s*%.{0,160}70\s*%", re.I | re.S),
    "unsafe large sample promise": re.compile(r"(?:1\s*[–-]\s*5\s*kg|DHL within 48 hours)", re.I),
    "unsupported factory-direct claim": re.compile(r"factory[- ]direct", re.I),
}

RAW_FORBIDDEN = {
    "unsafe illustrative IEC": "AABFJ1234C",
    "unsafe illustrative GSTIN": "27AABFJ1234C1ZX",
    "unsafe illustrative SWIFT": "YESBINBB",
}

# These product pages intentionally omit a fixed Purity/Moisture/Foreign
# Matter/Broken figure in favour of lot- or form-dependent contract language
# (e.g. tamarind's spec varies by pod/pulp/paste form; pulses and spices vary
# by crop year and grade). The master catalogue keeps a representative value
# for the products.html table, structured data and PDF catalogue, but the
# page copy is a deliberate, already-reviewed editorial choice, not a bug.
# Keyed by (product URL, master spec key).
VARIABLE_SPEC_EXCEPTIONS = {
    ("fennel-seeds-sounff-exporter.html", "Purity"),
    ("fenugreek-seeds-methi-exporter.html", "Purity"),
    ("dry-red-chilli-exporter.html", "Broken"),
    ("dry-red-chilli-exporter.html", "Foreign Matter"),
    ("tamarind-exporter.html", "Moisture"),
    ("tamarind-exporter.html", "Foreign Matter"),
    ("tamarind-exporter.html", "Purity"),
    ("ajwain-seeds-powder-exporter.html", "Purity"),
    ("senna-leaves-exporter.html", "Purity"),
    ("senna-leaves-exporter.html", "Moisture"),
    ("moringa-powder-exporter.html", "Moisture"),
    ("psyllium-husk-exporter.html", "Purity"),
    ("psyllium-husk-exporter.html", "Moisture"),
    ("henna-powder-exporter.html", "Moisture"),
    ("sesame-seeds-naturalhulled-exporter.html", "Purity"),
    ("soya-bean-exporter.html", "Purity"),
    ("black-cumin-seeds-nigella-exporter.html", "Purity"),
    ("safflower-seeds-exporter.html", "Foreign Matter"),
    ("deoiled-rice-bran-dorb-exporter.html", "Moisture"),
    ("sugar-s30-supplier.html", "Moisture"),
    ("indian-raisins-kishmish-exporter.html", "Moisture"),
    ("yellow-peas-matar-exporter.html", "Moisture"),
    ("yellow-peas-matar-exporter.html", "Foreign Matter"),
    ("chickpeas-kabuli-exporter.html", "Moisture"),
    ("green-mung-beans-exporter.html", "Purity"),
    ("green-mung-beans-exporter.html", "Moisture"),
    ("toor-dal-split-pigeon-pea-exporter.html", "Moisture"),
    ("toor-dal-split-pigeon-pea-exporter.html", "Broken"),
}


def visible_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    # The site owner can explicitly approve a narrowly scoped claim block. Keep
    # that approval visible in source while continuing to audit every other page.
    text = re.sub(
        r'<section\b[^>]*data-claim-status="owner-directed"[^>]*>.*?</section>',
        " ",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    # The site owner explicitly approved exactly one family-heritage history
    # sentence (Phase 33, A2) that intentionally carries the literal token "1980"
    # as a predecessor-trading tradition year, paired with the verifiable 2016 LLP
    # formation year. Suppress ONLY that exact wording from the 1980 gate so the
    # gate keeps firing on every other unexpected "1980" claim (e.g. a "Star Export
    # House since 1980" badge). Approved wording is kept visible in source.
    text = text.replace(
        "Building on a family trading tradition in Indian agricultural commodities "
        "since 1980, JFT Agro Overseas LLP was formed in 2016.",
        " ",
    )
    return text


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or "reports" in path.parts:
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        content = visible_text(path)
        for label, pattern in FORBIDDEN.items():
            if pattern.search(content):
                findings.append(f"{path.relative_to(ROOT).as_posix()}: {label}")
        for label, value in RAW_FORBIDDEN.items():
            if value in raw:
                findings.append(f"{path.relative_to(ROOT).as_posix()}: {label}")

    products = json.loads(MASTER.read_text(encoding="utf-8"))
    if len(products) != 84:
        findings.append(f"data/products.json: expected governed catalogue count 84, found {len(products)}")
    names = set()
    urls = set()
    required_specs = {"HS Code", "MOQ"}
    for product in products:
        name = product.get("t", "").strip()
        url = product.get("u", "").strip()
        specs = {row[0] for row in product.get("s", []) if isinstance(row, list) and row}
        if not name or name.casefold() in names:
            findings.append(f"data/products.json: missing or duplicate product name {name!r}")
        names.add(name.casefold())
        if not url or url in urls or not (ROOT / url).is_file():
            findings.append(f"data/products.json: missing, duplicate, or unresolved product URL {url!r}")
        urls.add(url)
        missing = required_specs - specs
        if missing:
            findings.append(f"{name}: missing master fields {sorted(missing)}")
        for section in ("identity", "trade", "compliance"):
            if not isinstance(product.get(section), dict) or not product[section]:
                findings.append(f"{name}: missing governed {section} data")
        trade = product.get("trade", {})
        for field in ("hs_code", "moq", "container_20ft", "container_40ft", "packaging", "private_label", "fob", "cif", "port_of_loading"):
            if not trade.get(field):
                findings.append(f"{name}: missing trade.{field}")
        page_html = (ROOT / url).read_text(encoding="utf-8") if url and (ROOT / url).is_file() else ""
        page_text = BeautifulSoup(page_html, "html.parser").get_text(" ")
        if 'data-product-specific-faq="true"' not in page_html:
            findings.append(f"{url}: missing product-specific FAQ generated from the master")
        normalized_page = re.sub(r"[^a-z0-9%]+", "", page_text.casefold())
        for key, value in product.get("s", []):
            if key in {"HS Code", "Moisture", "Purity", "Broken", "Foreign Matter", "Length", "MOQ"}:
                if (url, key) in VARIABLE_SPEC_EXCEPTIONS:
                    continue
                normalized_value = re.sub(r"[^a-z0-9%]+", "", str(value).casefold())
                if normalized_value and normalized_value not in normalized_page:
                    findings.append(f"{url}: master/page mismatch for {key}={value}")

    catalogue = (ROOT / "products.html").read_text(encoding="utf-8")
    if "fob_usd_min" in catalogue or "AggregateOffer" in catalogue or "InStock" in catalogue:
        findings.append("products.html: stale hard-coded price/availability schema remains")
    if "const PRODUCT_DATA = window.JFT_PRODUCT_DATA;" not in catalogue:
        findings.append("products.html: catalogue is not consuming the canonical product master")

    print(f"Claims/product findings: {len(findings)}")
    for finding in findings[:100]:
        print("-", finding)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
