#!/usr/bin/env python3
"""Remove templated sales copy and obvious localization residue.

The script uses existing product data and conservative, contract-led language. It
does not approve editorial or native-language review records.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

GENERIC_HERO = re.compile(
    r'<p class="jft-page-hero-sub">Premium quality .*? Available in bulk packaging for B2B wholesale\.</p>',
    re.DOTALL,
)
HERO_PARAGRAPH = re.compile(r'<p class="jft-page-hero-sub">.*?</p>', re.DOTALL)
HUMANIZED_MARKERS = (
    "for bulk rice programmes",
    "for processors, wholesalers and packers",
    "for bulk trade requirements",
    "for buyers who specify intended use",
    "for bulk food, processing or trade requirements",
    "supplied against a written bulk-buying requirement",
)

STANDARD_REPLACEMENTS = {
    "Decades of agricultural trade experience support practical sourcing, quality coordination and export execution.":
        "JFT Agro Overseas LLP was registered in 2016. Current company, facility and shipment-supporting documents are available for buyer verification.",
    "Optical sorting removes discoloured, damaged and foreign particles to achieve 99–99.5% purity.":
        "Cleaning and optical sorting are applied where relevant to the commodity and contracted grade. Final purity and defect limits are confirmed in the approved lot specification.",
    "Commercial Invoice, B/L, COO, Packing List, Phyto Certificate, SGS / Cotecna inspection available on request.":
        "The quotation identifies the standard shipment documents and any product- or destination-specific certificates. Independent inspection is included only when agreed in the contract.",
}

HOMEPAGE_REPLACEMENTS = {
    "Happy Customer Commitment": "Commercial Commitment",
    "Empowering landlocked markets with reliable food security solutions.":
        "Zambia-bound shipments are planned through an agreed regional port and inland transport route.",
}

CONTACT_REPLACEMENTS = {
    "Every international buyer follows the same streamlined path from first contact to container delivery.":
        "The steps below show a typical enquiry-to-shipment workflow. Timing and controls vary by product, destination and contract.",
}

LOCALE_HERO = {
    "id": {
        "tag": "Star Export House · ISO 9001:2015",
        "headline": "Komoditas Pertanian India",
        "emphasis": "untuk Pembeli Global",
        "detail": "Spesifikasi, pemeriksaan, dan pengiriman yang disepakati",
        "description": "Pasokan beras, rempah, kacang-kacangan, biji-bijian, dan minyak nabati dari India berdasarkan spesifikasi lot, pilihan inspeksi independen, dan persyaratan pengiriman yang disepakati.",
        "quote": "Minta Penawaran",
    },
    "ms": {
        "tag": "Star Export House · ISO 9001:2015",
        "headline": "Komoditi Pertanian India",
        "emphasis": "untuk Pembeli Antarabangsa",
        "detail": "Spesifikasi, pemeriksaan dan penghantaran yang dipersetujui",
        "description": "Bekalan beras, rempah, kekacang, bijirin dan biji minyak dari India berdasarkan spesifikasi lot, pilihan pemeriksaan bebas dan syarat penghantaran yang dipersetujui.",
        "quote": "Minta Sebut Harga",
    },
    "pt": {
        "tag": "Star Export House · ISO 9001:2015",
        "headline": "Produtos Agrícolas da Índia",
        "emphasis": "para Compradores Internacionais",
        "detail": "Especificação, inspeção e embarque acordados",
        "description": "Fornecimento de arroz, especiarias, leguminosas, grãos e oleaginosas da Índia com especificação do lote, opção de inspeção independente e condições de embarque acordadas.",
        "quote": "Solicitar Cotação",
    },
    "si": {
        "tag": "Star Export House · ISO 9001:2015",
        "headline": "ඉන්දියානු කෘෂි නිෂ්පාදන",
        "emphasis": "ජාත්‍යන්තර ගැනුම්කරුවන් සඳහා",
        "detail": "එකඟ වූ පිරිවිතර, පරීක්ෂණ සහ නැව්ගත කිරීම",
        "description": "ඉන්දියාවෙන් සහල්, කුළුබඩු, පරිප්පු, ධාන්‍ය සහ තෙල් බීජ සැපයීමේදී තොග පිරිවිතර, ස්වාධීන පරීක්ෂණ විකල්ප සහ එකඟ වූ නැව්ගත කිරීමේ කොන්දේසි තහවුරු කරනු ලැබේ.",
        "quote": "මිල ගණන් ඉල්ලන්න",
    },
    "th": {
        "tag": "Star Export House · ISO 9001:2015",
        "headline": "สินค้าเกษตรจากอินเดีย",
        "emphasis": "สำหรับผู้ซื้อทั่วโลก",
        "detail": "ตกลงสเปก การตรวจสอบ และการจัดส่งให้ชัดเจน",
        "description": "จัดหาข้าว เครื่องเทศ พืชตระกูลถั่ว ธัญพืช และเมล็ดพืชน้ำมันจากอินเดีย โดยยืนยันสเปกของล็อต ตัวเลือกการตรวจสอบอิสระ และเงื่อนไขการจัดส่งก่อนทำสัญญา",
        "quote": "ขอใบเสนอราคา",
    },
    "vi": {
        "tag": "Star Export House · ISO 9001:2015",
        "headline": "Nông sản Ấn Độ",
        "emphasis": "cho Người mua Quốc tế",
        "detail": "Thống nhất quy cách, kiểm định và giao hàng",
        "description": "Cung ứng gạo, gia vị, đậu, ngũ cốc và hạt có dầu từ Ấn Độ theo quy cách từng lô, lựa chọn kiểm định độc lập và điều kiện giao hàng đã thỏa thuận.",
        "quote": "Yêu cầu Báo giá",
    },
}

CONTACT_TRANSLATIONS = {
    "ar": "اتصل بنا", "es": "Contáctenos", "fr": "Nous contacter",
    "id": "Hubungi Kami", "ms": "Hubungi Kami", "pt": "Entre em contato",
    "ru": "Свяжитесь с нами", "si": "අප අමතන්න", "th": "ติดต่อเรา",
    "vi": "Liên hệ với chúng tôi",
}


def join_fields(fields: list[str]) -> str:
    fields = [field.lower() for field in fields]
    if len(fields) == 1:
        return fields[0]
    if len(fields) == 2:
        return f"{fields[0]} and {fields[1]}"
    return f"{', '.join(fields[:-1])}, and {fields[-1]}"


def product_intro(product: dict[str, object]) -> str:
    title = str(product["t"])
    category = str(product["c"])
    packing = str(product.get("p") or "the agreed bulk format")
    origin = str(product.get("identity", {}).get("origin") or "India")
    fields = [str(row[0]) for row in product.get("s", []) if row and row[0] not in {"HS Code", "MOQ"}][:3]
    measures = join_fields(fields or ["grade", "moisture", "purity"])

    if category == "rice":
        copy = (
            f"{title} for bulk rice programmes, with the required values for {measures} agreed before quotation. "
            f"Typical planning uses {packing}; the final crop, origin, lot values, inspection scope and documents are recorded in the approved specification and Proforma Invoice."
        )
    elif category == "spices":
        copy = (
            f"{title} sourced from {origin} for processors, wholesalers and packers. "
            f"The written requirement should cover product form and the relevant {measures} values, together with destination residue or microbiological controls. Typical packing is {packing}, subject to contract."
        )
    elif category == "herbs":
        copy = (
            f"{title} sourced from {origin} for bulk trade requirements. "
            f"The enquiry should state intended use and required form, then define the relevant {measures} values and destination testing needs. Typical packing is {packing}, subject to the approved lot specification."
        )
    elif category == "feed":
        copy = (
            f"Bulk {title} for buyers who specify intended use and destination requirements before contracting. "
            f"The offer records the agreed {measures} values, lot acceptance terms and packing format; typical planning uses {packing}."
        )
    elif category == "oilseeds":
        copy = (
            f"{title} for bulk food, processing or trade requirements, with intended use confirmed by the buyer. "
            f"The lot is offered against agreed values for {measures}, together with packing and destination controls; typical packing is {packing}."
        )
    else:
        copy = (
            f"{title} supplied against a written bulk-buying requirement. "
            f"The offer records the agreed {measures} values, packing, inspection and destination documents before order confirmation; typical planning uses {packing}."
        )
    return f'<p class="jft-page-hero-sub">{html.escape(copy, quote=False)}</p>'


def improve_english_products() -> int:
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    changed = 0
    for product in products:
        path = ROOT / str(product["u"])
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated, count = GENERIC_HERO.subn(product_intro(product), text, count=1)
        if count == 0 and any(marker in text for marker in HUMANIZED_MARKERS):
            updated = HERO_PARAGRAPH.sub(product_intro(product), text, count=1)
        for old, new in STANDARD_REPLACEMENTS.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def improve_core_copy() -> int:
    changed = 0
    for filename, replacements in (("index.html", HOMEPAGE_REPLACEMENTS), ("contact.html", CONTACT_REPLACEMENTS)):
        path = ROOT / filename
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def improve_locale_homepages() -> int:
    changed = 0
    hero_pattern = re.compile(
        r'<span class="hero-tag-modern"><i class="fa-solid fa-star"></i>.*?</span>\s*'
        r'<h1 class="hero-title-modern">Global Export<br/><span class="gold-text">Command Center</span><strong>Powered by\s*Indian Agriculture</strong></h1>\s*'
        r'<p class="hero-desc-modern">.*?</p>',
        re.DOTALL,
    )
    quote_pattern = re.compile(
        r'(<a class="btn-outline" href="contact\.html#inquiry-form"><i class="fa-solid fa-file-invoice"></i>)\s*Get Custom\s*Quote(</a>)',
        re.DOTALL,
    )
    for locale, copy in LOCALE_HERO.items():
        path = ROOT / locale / "index.html"
        text = path.read_text(encoding="utf-8")
        replacement = (
            f'<span class="hero-tag-modern"><i class="fa-solid fa-star"></i> {copy["tag"]}</span>\n'
            f'<h1 class="hero-title-modern">{copy["headline"]}<br/><span class="gold-text">{copy["emphasis"]}</span>'
            f'<strong>{copy["detail"]}</strong></h1>\n'
            f'<p class="hero-desc-modern">{copy["description"]}</p>'
        )
        updated, hero_count = hero_pattern.subn(replacement, text, count=1)
        updated, quote_count = quote_pattern.subn(rf'\1 {copy["quote"]}\2', updated, count=1)
        if hero_count != 1 and copy["headline"] not in text:
            raise RuntimeError(f"Could not replace localized hero in {path}")
        if quote_count != 1 and copy["quote"] not in text:
            raise RuntimeError(f"Could not replace localized quote label in {path}")
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def localize_contact_headings() -> int:
    changed = 0
    for locale, translation in CONTACT_TRANSLATIONS.items():
        path = ROOT / locale / "privacy.html"
        text = path.read_text(encoding="utf-8")
        updated = text.replace("<h2>5. Contact Us</h2>", f"<h2>5. {translation}</h2>")
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def update_schema_node(node: object, *, locale: str, canonical: str, headline: str, description: str) -> bool:
    if not isinstance(node, dict):
        return False
    changed = False
    schema_type = node.get("@type")
    types = set(schema_type if isinstance(schema_type, list) else [schema_type])
    content_types = {"Article", "BlogPosting", "NewsArticle", "WebPage", "HowTo", "FAQPage"}
    if types & content_types and node.get("inLanguage") != locale:
        node["inLanguage"] = locale
        changed = True
    if types & {"Article", "BlogPosting", "NewsArticle"}:
        for key, value in (("headline", headline), ("description", description), ("mainEntityOfPage", canonical)):
            if value and node.get(key) != value:
                node[key] = value
                changed = True
    if "WebPage" in types:
        values = {"@id": f"{canonical}#webpage", "url": canonical, "name": headline, "description": description}
        for key, value in values.items():
            if value and node.get(key) != value:
                node[key] = value
                changed = True
    if "HowTo" in types and headline and node.get("name") != headline:
        node["name"] = headline
        changed = True
    return changed


def correct_localized_schema() -> int:
    script_pattern = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.I | re.DOTALL)
    changed_pages = 0
    for locale in LOCALES:
        for path in (ROOT / locale).rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            canonical = ""
            for tag in re.findall(r"<link\b[^>]*>", text, re.I):
                if re.search(r"\brel=[\"']canonical[\"']", tag, re.I):
                    match = re.search(r"\bhref=[\"']([^\"']+)", tag, re.I)
                    canonical = html.unescape(match.group(1)) if match else ""
                    break
            headline_match = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.I | re.DOTALL)
            headline = ""
            if headline_match:
                headline = html.unescape(re.sub(r"<[^>]+>", " ", headline_match.group(1)))
                headline = re.sub(r"\s+", " ", headline).strip()
            description = ""
            for tag in re.findall(r"<meta\b[^>]*>", text, re.I):
                if re.search(r"\bname=[\"']description[\"']", tag, re.I):
                    match = re.search(r"\bcontent=[\"']([^\"']*)", tag, re.I)
                    description = html.unescape(match.group(1)) if match else ""
                    break
            page_changed = False

            def replace(match: re.Match[str]) -> str:
                nonlocal page_changed
                try:
                    payload = json.loads(match.group(2))
                except json.JSONDecodeError:
                    return match.group(0)
                nodes = payload.get("@graph", []) if isinstance(payload, dict) and isinstance(payload.get("@graph"), list) else [payload]
                schema_changed = False
                for node in nodes:
                    if update_schema_node(
                        node,
                        locale=locale,
                        canonical=canonical,
                        headline=headline,
                        description=description,
                    ):
                        schema_changed = True
                if not schema_changed:
                    return match.group(0)
                page_changed = True
                return f"{match.group(1)}{json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}{match.group(3)}"

            updated = script_pattern.sub(replace, text)
            if page_changed:
                path.write_text(updated, encoding="utf-8", newline="\n")
                changed_pages += 1
    return changed_pages


def main() -> int:
    results = {
        "english_product_pages": improve_english_products(),
        "core_pages": improve_core_copy(),
        "localized_homepages": improve_locale_homepages(),
        "localized_privacy_pages": localize_contact_headings(),
        "localized_schema_pages": correct_localized_schema(),
    }
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
