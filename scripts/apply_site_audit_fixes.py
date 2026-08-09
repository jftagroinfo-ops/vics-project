#!/usr/bin/env python3
"""Apply deterministic, idempotent fixes found by the full-site audit."""

from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
LANGS = {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}
FULL_ENGLISH_ARTICLES = {
    "blog-green-mung-beans-export-india-2026.html",
    "blog-how-to-read-proforma-invoice-india-export.html",
    "blog-india-rice-export-sri-lanka-bangladesh.html",
    "blog-letter-of-credit-food-imports-india.html",
    "blog-sgs-inspection-indian-agro-exports.html",
    "blog-toor-dal-export-india-2026.html",
}
DOUBLE_H1_PAGES = {
    "africa-trade.html",
    "asia-trade.html",
    "blog.html",
    "certificates.html",
    "europe-trade.html",
    "privacy.html",
    "quote-calculator.html",
    "sample-request.html",
    "terms.html",
    "uae-trade.html",
}
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
PUBLISHED_CARD_LINKS = {
    "rice export to sri lanka": "blog-india-rice-export-sri-lanka-bangladesh.html",
    "proforma invoice": "blog-how-to-read-proforma-invoice-india-export.html",
    "sgs": "blog-sgs-inspection-indian-agro-exports.html",
    "letter of credit": "blog-letter-of-credit-food-imports-india.html",
    "green mung": "blog-green-mung-beans-export-india-2026.html",
}
BLOG_REPLACEMENTS = {
    "blog-cif-fob-explained.html": "blog-bill-of-lading-explained-importers.html",
    "blog-eu-mrl-basmati.html": "blog-red-chilli-teja-export-india-2026.html",
    "blog-india-uae-cepa.html": "blog-import-duty-indian-rice-by-country.html",
    "blog-indian-white-rice-export-policy-2026-latest-updates.html": "blog-ir64-export.html",
    "blog-ir64-africa.html": "blog-ir64-export.html",
    "blog-lc-vs-tt.html": "blog-letter-of-credit-food-imports-india.html",
    "blog-private-label-rice.html": "blog-how-to-choose-indian-agro-exporter.html",
    "blog-sesame-export-2026.html": "blog-top-indian-agro-commodities-import-2026.html",
    "blog-spice-trends-2026.html": "blog-turmeric-finger-export-india-2026.html",
}
BLOG_IMAGES = {
    "blog-basmati-export-guide.html": "images/products/basmati_rice_hd.webp",
    "blog-how-to-export-india-to-africa.html": "images/INFRASTRUCTURE/logistics.webp",
    "blog-turmeric-finger-export-india-2026.html": "images/products/turmeric_finger.webp",
    "blog-red-chilli-teja-export-india-2026.html": "images/products/red_chilli_hd.webp",
    "blog-green-mung-beans-export-india-2026.html": "images/products/pulses_hd.webp",
    "blog-ir64-export.html": "images/products/ir64.webp",
    "blog-how-to-import-rice-nigeria-west-africa.html": "images/products/5 Parboiled Rice (IR-64).webp",
    "blog-india-rice-export-sri-lanka-bangladesh.html": "images/products/basmati_rice_hd.webp",
    "blog-import-indian-agro-kenya-east-africa.html": "images/INFRASTRUCTURE/logistics.webp",
    "blog-how-to-read-proforma-invoice-india-export.html": "images/INFRASTRUCTURE/packing unit.webp",
    "blog-import-duty-indian-rice-by-country.html": "images/products/market_update.webp",
    "blog-apeda-registration-indian-exporter-explained.html": "images/homepage/APEDA.webp",
    "blog-sgs-inspection-indian-agro-exports.html": "images/INFRASTRUCTURE/packing unit.webp",
    "blog-letter-of-credit-food-imports-india.html": "images/INFRASTRUCTURE/logistics.webp",
    "blog-bill-of-lading-explained-importers.html": "images/INFRASTRUCTURE/logistics.webp",
    "blog-india-vs-thailand-rice-comparison.html": "images/products/basmati_rice_hd.webp",
    "blog-top-indian-agro-commodities-import-2026.html": "images/products/market_update.webp",
    "blog-how-to-choose-indian-agro-exporter.html": "images/INFRASTRUCTURE/rice-factory.webp",
    "blog-psyllium-husk-export-india-2026.html": "images/products/Ind Psyllium Husk.webp",
    "blog-cumin-jeera-price-outlook-2026.html": "images/products/cumin_seeds.webp",
    "blog-turmeric-market-outlook-2026.html": "images/products/turmeric_finger.webp",
}


def product_images() -> dict[str, str]:
    products = (ROOT / "products.html").read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    for line in products.splitlines():
        url = re.search(r"\bu:\s*'([^']+\.html)'", line)
        image = re.search(r"\bi:\s*'([^']+)'", line)
        if url and image:
            mapping[url.group(1)] = image.group(1)
    return mapping


def replace_second_h1(text: str) -> str:
    starts = list(re.finditer(r"<h1\b", text, flags=re.I))
    if len(starts) < 2:
        return text
    start = starts[1].start()
    end = text.find("</h1>", start)
    if end == -1:
        return text
    text = text[:start] + "<h2" + text[start + 3 :]
    end = text.find("</h1>", start)
    return text[:end] + "</h2>" + text[end + 5 :]


def secure_blank_targets(text: str) -> str:
    def update_anchor(match: re.Match[str]) -> str:
        tag = match.group(0)
        if not re.search(r'\btarget=["\']_blank["\']', tag, re.I):
            return tag
        rel = re.search(r'\brel=(["\'])(.*?)\1', tag, re.I)
        if not rel:
            return tag[:-1] + ' rel="noopener">'
        values = rel.group(2).split()
        if "noopener" not in values:
            values.append("noopener")
            tag = tag[: rel.start(2)] + " ".join(values) + tag[rel.end(2) :]
        return tag

    return re.sub(r"<a\b[^>]*>", update_anchor, text, flags=re.I)


def add_external_image_dimensions(text: str) -> str:
    def update_image(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r"\bwidth\s*=", tag, re.I) and re.search(r"\bheight\s*=", tag, re.I):
            return tag
        source = re.search(r'\bsrc=["\']([^"\']+)["\']', tag, re.I)
        if not source:
            return tag
        url = source.group(1)
        dimensions = None
        if "World_map_-_low_resolution.svg" in url:
            dimensions = (1024, 512)
        elif "flagcdn.com/w80/my.png" in url:
            dimensions = (80, 40)
        elif "flagcdn.com/w80/th.png" in url:
            dimensions = (80, 53)
        elif "flagcdn.com/w40/" in url:
            dimensions = (24, 16) if "width:24px" in tag else (28, 20)
        elif "images.unsplash.com/photo-" in url and "w=800" in url:
            dimensions = (800, 533)
        elif "Monocrystals_of_sucrose.jpg/1280px-" in url:
            dimensions = (1280, 960)
        if not dimensions:
            return tag
        return tag[:-1] + f' width="{dimensions[0]}" height="{dimensions[1]}">'

    return re.sub(r"<img\b[^>]*>", update_image, text, flags=re.I)


def fix_blog_links(text: str) -> str:
    unpublished_pattern = "|".join(re.escape(name) for name in sorted(UNPUBLISHED_BLOGS))
    text = re.sub(
        rf'<a\b(?=[^>]*\bhref=["\'](?:\.\./)?(?:{unpublished_pattern})["\'])[^>]*class=["\'][^"\']*(?:article-card|related-card)[^"\']*["\'][^>]*>.*?</a>\s*',
        "",
        text,
        flags=re.I | re.S,
    )
    for unpublished, published in BLOG_REPLACEMENTS.items():
        text = re.sub(
            rf'(<a\b[^>]*\bhref=["\'])(?:\.\./)?{re.escape(unpublished)}(["\'])',
            rf"\1{published}\2",
            text,
            flags=re.I,
        )
    text = re.sub(
        rf'<a\b(?=[^>]*\bhref=["\'](?:\.\./)?(?:{unpublished_pattern})["\'])[^>]*>.*?Read Article.*?</a>\s*',
        "",
        text,
        flags=re.I | re.S,
    )

    def replace_dead_anchor(match: re.Match[str]) -> str:
        tag = match.group(0)
        if 'id="m-blog-link"' in tag or 'id="ctaWA"' in tag:
            return tag
        plain = re.sub(r"<[^>]+>", " ", tag)
        normalized = re.sub(r"\s+", " ", plain).strip().lower()
        for phrase, target in PUBLISHED_CARD_LINKS.items():
            if phrase in normalized:
                return tag.replace('href="#"', f'href="{target}"', 1).replace("href='#'", f"href='{target}'", 1)
        if "article-card" in tag or "related-card" in tag or "Read Article" in tag:
            return ""
        return tag

    text = re.sub(r'<a\b[^>]*\bhref=["\']#["\'][^>]*>.*?</a>', replace_dead_anchor, text, flags=re.I | re.S)
    text = text.replace(
        'href="blog-spice-trends-2026.html" style="color:#3d7030;font-weight:700;">Spice market trends 2026',
        'href="blog-turmeric-finger-export-india-2026.html" style="color:#3d7030;font-weight:700;">Turmeric export guide 2026',
    )
    text = text.replace(
        'href="blog-sesame-export-2026.html" style="color:#3d7030;font-weight:700;">Sesame export outlook',
        'href="blog-top-indian-agro-commodities-import-2026.html" style="color:#3d7030;font-weight:700;">Indian agro export outlook',
    )
    return text


def synchronize_blog_filters(text: str) -> str:
    categories = {"buyer-guide": 0, "market": 0, "compliance": 0}

    def update_card(match: re.Match[str]) -> str:
        card = match.group(0)
        if "Buyer's Guide" in card:
            category = "buyer-guide"
        elif "Market Outlook" in card or "Market Insight" in card:
            category = "market"
        else:
            category = "compliance"
        categories[category] += 1
        return re.sub(r'data-cat=["\'][^"\']+["\']', f'data-cat="{category}"', card, count=1)

    text = re.sub(
        r'<a\b[^>]*class=["\'][^"\']*article-card[^"\']*["\'][^>]*data-cat=["\'][^"\']+["\'][^>]*>.*?</a>',
        update_card,
        text,
        flags=re.I | re.S,
    )
    total = sum(categories.values())
    for label, count in {
        "All Articles": total,
        "Buyer Guides": categories["buyer-guide"],
        "Market Intelligence": categories["market"],
        "Compliance & Docs": categories["compliance"],
    }.items():
        text = re.sub(
            rf'({re.escape(label)}\s*<span class="filter-count">)\d+(</span>)',
            rf"\g<1>{count}\2",
            text,
            count=1,
        )
    text = re.sub(
        r'\s*<script\s+type=["\']application/ld\+json["\']>\s*\{[^<]*["\']@type["\']\s*:\s*["\']ItemList["\'][^<]*</script>',
        "",
        text,
        count=1,
        flags=re.I | re.S,
    )
    return text


def apply_blog_images(text: str, localized: bool) -> str:
    prefix = "../" if localized else ""

    def update_card(match: re.Match[str]) -> str:
        card = match.group(0)
        href = re.search(r'href=["\'](?:\.\./)?([^"\']+\.html)["\']', card, re.I)
        if not href or href.group(1) not in BLOG_IMAGES:
            return card
        image = prefix + BLOG_IMAGES[href.group(1)]
        title_match = re.search(r'class=["\'][^"\']*card-title[^"\']*["\'][^>]*>(.*?)</h[23]>', card, re.I | re.S)
        title = re.sub(r"<[^>]+>", " ", title_match.group(1)) if title_match else "JFT Agro trade insight"
        title = html.escape(re.sub(r"\s+", " ", title).strip(), quote=True)
        with Image.open(ROOT / BLOG_IMAGES[href.group(1)]) as source:
            width, height = source.size
        image_html = (
            f'<div class="card-img"><img src="{image}" alt="{title}" loading="lazy" '
            f'width="{width}" height="{height}"></div>'
        )
        return re.sub(r'<div class="card-img">.*?</div>', image_html, card, count=1, flags=re.I | re.S)

    return re.sub(
        r'<a\b[^>]*class=["\'][^"\']*article-card[^"\']*["\'][^>]*>.*?</a>',
        update_card,
        text,
        flags=re.I | re.S,
    )


def redirect_cloned_blog(path: Path, text: str, localized: bool) -> str:
    destination = BLOG_REPLACEMENTS.get(path.name)
    is_clone = "1121 vs 1509 Basmati Rice: Which Variety Should You Import in 2026?" in text
    is_redirect = "This article has moved to a verified related guide." in text
    if not destination or not (is_clone or is_redirect):
        return text
    href = ("../" if localized else "") + destination
    title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    label = re.sub(r"\s*\|.*$", "", title.group(1)).strip() if title else "Article moved"
    language = path.parent.name if localized else "en"
    direction = ' dir="rtl"' if language == "ar" else ""
    return f'''<!DOCTYPE html>
<html lang="{language}"{direction}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="This article has moved to a verified related JFT Agro import and export guide.">
  <meta name="robots" content="noindex,follow">
  <meta http-equiv="refresh" content="0;url={href}">
  <link rel="canonical" href="https://jftagro.com/{destination}">
  <title>{label} | JFT Agro Insights</title>
</head>
<body>
  <main id="main-content">
    <h1>{label}</h1>
    <p>This article has moved to a verified related guide.</p>
    <p><a href="{href}">Continue to the article</a></p>
  </main>
  <script>location.replace({href!r});</script>
</body>
</html>
'''


def fix_html(path: Path, image_map: dict[str, str]) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original
    localized = path.parent.name in LANGS

    text = redirect_cloned_blog(path, text, localized)

    text = text.replace("info@jftagro.com", "exports@jftagro.com")
    text = text.replace("export@jftagro.com", "exports@jftagro.com")
    text = re.sub(
        r'\s*<link\s+rel=["\']preload["\']\s+as=["\']image["\']\s+href=["\'](?:\.\./)?images/homepage/BASMATI\.webp["\'][^>]*>',
        "",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"contact\.html#inquiry-form\?product=([^\"'\s<]+)",
        r"contact.html?product=\1#inquiry-form",
        text,
    )
    text = text.replace(
        "contact.html?product=Cumin#inquiry-form Seeds",
        "contact.html?product=Cumin%20Seeds#inquiry-form",
    )
    text = text.replace(
        "contact.html?product=Psyllium#inquiry-form Husk",
        "contact.html?product=Psyllium%20Husk#inquiry-form",
    )

    asset_prefix = "../" if localized else ""
    if path.name == "index.html":
        text = re.sub(
            r'\s*<div class="hero-slide"\s*style="background-image:url\(\'https://images\.unsplash\.com/photo-1618897996318-5a901fa4f5c3\?w=1920&q=85&auto=format&fit=crop\'\);">\s*</div>',
            "",
            text,
        )
        replacements = {
            "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=1920&q=85&auto=format&fit=crop": f"{asset_prefix}images/products/basmati_rice_hd.webp",
            "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=1920&q=85&auto=format&fit=crop": f"{asset_prefix}images/homepage/SPICES.webp",
            "https://images.unsplash.com/photo-1605000797498-6f2145b1d53d?w=1920&q=85&auto=format&fit=crop": f"{asset_prefix}images/INFRASTRUCTURE/logistics.webp",
            "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&q=85&auto=format&fit=crop": f"{asset_prefix}images/products/basmati_rice_hd.webp",
            "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=800&q=85&auto=format&fit=crop": f"{asset_prefix}images/homepage/SPICES.webp",
            "https://images.unsplash.com/photo-1605000797498-6f2145b1d53d?w=800&q=85&auto=format&fit=crop": f"{asset_prefix}images/INFRASTRUCTURE/logistics.webp",
        }
        for remote, local in replacements.items():
            text = text.replace(remote, local)

    if path.name == "sample-request.html":
        validation_block = (
            "      if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) { alert('Please enter a valid email address.'); return; }\n"
            "      if (!/^[\\d\\+\\-\\s\\(\\)]+$/.test(phone)) { alert('Please enter a valid phone number.'); return; }\n"
            "      sampleSubmitting = true;\n"
        )
        text = re.sub(
            r"(        if \(missing\.length\).*?\n      }\n).*?(      const msg = encodeURIComponent)",
            lambda match: match.group(1) + validation_block + match.group(2),
            text,
            count=1,
            flags=re.S,
        )
        text = text.replace(
            r"if(event.key===\'Enter\'||event.key===\' \')",
            "if(event.key==='Enter'||event.key===' ')",
        )
        text = re.sub(
            r'<div class="prod-pick" onclick="([^"]+)">',
            r'''<div class="prod-pick" role="checkbox" tabindex="0" aria-checked="false" onclick="\1" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();this.click();}">''',
            text,
        )
        text = text.replace(
            "el.classList.remove('selected');\n        selectedProducts.delete(name);",
            "el.classList.remove('selected');\n        el.setAttribute('aria-checked', 'false');\n        selectedProducts.delete(name);",
        )
        text = text.replace(
            "el.classList.add('selected');\n        selectedProducts.add(name);",
            "el.classList.add('selected');\n        el.setAttribute('aria-checked', 'true');\n        selectedProducts.add(name);",
        )
        text = text.replace(
            '<button class="btn-submit" onclick="submitSampleRequest()">',
            '<button type="button" class="btn-submit" onclick="submitSampleRequest()">',
        )
        text = text.replace(
            "if (!name || !email || !phone || !addr || !city || document.getElementById('s-country').value === '')",
            "if (!name || !company || !email || !phone || !addr || !city || document.getElementById('s-country').value === '')",
        )
        text = text.replace(
            "if (!name) missing.push('Full Name');\n        if (!email) missing.push('Email');",
            "if (!name) missing.push('Full Name');\n        if (!company) missing.push('Company Name');\n        if (!email) missing.push('Email');",
        )
        text = text.replace(
            "    function submitSampleRequest() {\n      if (selectedProducts.size === 0)",
            "    let sampleSubmitting = false;\n    function submitSampleRequest() {\n      if (sampleSubmitting) return;\n      if (selectedProducts.size === 0)",
        )
        if "Please enter a valid email address." not in text:
            text = text.replace(
                "      const msg = encodeURIComponent(`Sample Request from JFT Website",
                validation_block + "      const msg = encodeURIComponent(`Sample Request from JFT Website",
            )
        text = text.replace(
            "      window.open(`https://wa.me/918425057274?text=${msg}`, '_blank');",
            "      const popup = window.open(`https://wa.me/918425057274?text=${msg}`, '_blank', 'noopener');\n      if (popup) popup.opener = null;",
        )

    if path.name == "blog.html":
        text = text.replace(
            '<input type="email" class="nl-input" placeholder="your@company.com" required id="nl-email">',
            '<input type="email" class="nl-input" placeholder="your@company.com" required id="nl-email" name="email" autocomplete="email" aria-label="Email address">',
        )
        text = text.replace(
            "      window.open(`https://wa.me/918425057274?text=${msg}`, '_blank');\n      e.target.querySelector('.nl-btn').textContent = '✓ Subscribed!';",
            "      const popup = window.open(`https://wa.me/918425057274?text=${msg}`, '_blank', 'noopener');\n      if (popup) popup.opener = null;\n      const button = e.target.querySelector('.nl-btn');\n      button.disabled = true;\n      button.textContent = 'Subscribed!';",
        )

    if path.name == "products.html":
        text = text.replace(
            "#product-modal.open {\n      opacity: 1;\n    }",
            "#product-modal.open {\n      display: flex;\n      opacity: 1;\n    }",
        )
        text = text.replace(
            '<div id="product-modal">',
            '<div id="product-modal" role="dialog" aria-modal="true" aria-labelledby="m-title" aria-hidden="true">',
        )
        text = text.replace(
            "      } else {\n        document.getElementById('m-cultivation').innerText = \"Year-Round Arrivals\";\n      }\n    }\n\n    function downloadPDF()",
            "      } else {\n        document.getElementById('m-cultivation').innerText = \"Year-Round Arrivals\";\n      }\n\n      modal.classList.add('open');\n      modal.setAttribute('aria-hidden', 'false');\n      const closeButton = modal.querySelector('[onclick=\"closeModal()\"]');\n      if (closeButton) closeButton.focus();\n    }\n\n    const catalogueTitle = document.title;\n    function closeModal() {\n      const modal = document.getElementById('product-modal');\n      modal.classList.remove('open');\n      modal.setAttribute('aria-hidden', 'true');\n      document.body.classList.remove('modal-open');\n      document.title = catalogueTitle;\n    }\n    document.getElementById('product-modal').addEventListener('click', function (event) {\n      if (event.target === this) closeModal();\n    });\n    document.addEventListener('keydown', function (event) {\n      if (event.key === 'Escape' && document.getElementById('product-modal').classList.contains('open')) closeModal();\n    });\n\n    function downloadPDF()",
        )

    if path.name == "shipment-tracker.html":
        logistics_image = "../images/INFRASTRUCTURE/logistics.webp" if localized else "images/INFRASTRUCTURE/logistics.webp"
        replacement = (
            '<a href="https://www.marinetraffic.com/en/ais/home/centerx:72.88/centery:18.96/zoom:8" '
            'target="_blank" rel="noopener noreferrer" '
            'style="min-height:420px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:16px;'
            f"background:linear-gradient(rgba(13,31,27,.72),rgba(13,31,27,.72)),url('{logistics_image}') center/cover;"
            'color:#fff;text-align:center;padding:32px;" '
            'aria-label="Open live vessel tracking map in a new tab">'
            '<i class="fa-solid fa-location-dot" style="font-size:2.4rem;color:var(--gold)"></i>'
            '<strong style="font-family:var(--ff-s);font-size:1.1rem">Open Live Vessel Map</strong>'
            '<span style="font-size:.85rem;color:rgba(255,255,255,.75)">MarineTraffic AIS - Indian Ocean and Gulf</span>'
            '</a>'
        )
        text = re.sub(
            r'<iframe\s+src="https://www\.marinetraffic\.com/en/ais/embed/[^"]+"\s+loading="lazy"\s+title="Live vessel tracking map[^>]+></iframe>',
            replacement,
            text,
            count=1,
            flags=re.I,
        )

    text = secure_blank_targets(text)
    text = fix_blog_links(text)
    if path.name == "blog.html":
        text = synchronize_blog_filters(text)
        text = apply_blog_images(text, localized)

    blog_image = BLOG_IMAGES.get(path.name)
    if blog_image:
        image_url = f"https://jftagro.com/{blog_image.replace(' ', '%20')}"
        local_image = ("../" if localized else "") + blog_image
        text = re.sub(
            r'(<meta\s+property=["\']og:image["\']\s+content=["\'])[^"\']+(["\'])',
            rf"\1{image_url}\2",
            text,
            count=1,
            flags=re.I,
        )
        text = re.sub(
            r'(<meta\s+name=["\']twitter:image["\']\s+content=["\'])[^"\']+(["\'])',
            rf"\1{image_url}\2",
            text,
            count=1,
            flags=re.I,
        )
        text = re.sub(
            r'(["\']image["\']\s*:\s*["\'])https://jftagro\.com/[^"\']+(["\'])',
            rf"\1{image_url}\2",
            text,
            count=1,
            flags=re.I,
        )
        def update_hero(match: re.Match[str]) -> str:
            tag = match.group(0)
            return re.sub(r'(\bsrc=["\'])[^"\']+(["\'])', rf"\1{local_image}\2", tag, count=1, flags=re.I)

        text = re.sub(
            r'<img\b(?=[^>]*class=["\'][^"\']*article-hero[^"\']*["\'])[^>]*>',
            update_hero,
            text,
            count=1,
            flags=re.I,
        )
    text = add_external_image_dimensions(text)
    text = re.sub(
        r'<script\s+async\s+src="https://www\.googletagmanager\.com/gtag/js\?id=G-MWZ2ZWZP4G"></script>\s*',
        "",
        text,
    )
    text = re.sub(
        r'\s*<!--Start of Tawk\.to Script-->\s*<script[^>]*>.*?embed\.tawk\.to.*?</script>\s*<!--End of Tawk\.to Script-->\s*',
        "\n",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r'\s*<!-- Tawk\.to(?: Live Chat)? -->\s*<script[^>]*>.*?embed\.tawk\.to.*?</script>\s*',
        "\n",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r'\s*<script\b[^>]*>[^<]*(?:embed\.tawk\.to|googletagmanager\.com/gtag/js\?id=G-MWZ2ZWZP4G)[^<]*</script>\s*',
        "\n",
        text,
        flags=re.I,
    )

    if "Content-Security-Policy" in text:
        text = re.sub(r"\s+https://(?:embed|va)\.tawk\.to", "", text)
        text = re.sub(r"\s+https://\*\.tawk\.to", "", text)
        text = re.sub(r"\s+wss://\*\.tawk\.to", "", text)

    if localized:
        if path.parent.name == "ar":
            text = re.sub(r'<html\s+lang="ar"(?![^>]*\bdir=)', '<html lang="ar" dir="rtl"', text, count=1)

        for asset in ("jft-design-system.css", "jft-responsive.css", "manifest.json"):
            text = re.sub(
                rf'((?:href|src)=["\'])(?!\.\./|/){re.escape(asset)}(["\'])',
                rf"\1../{asset}\2",
                text,
            )
        text = re.sub(
            r"((?:fetch|loadComponent|loadComp)\([^\n]*?[\"'])(header|footer)\.html([\"'])",
            r"\1../\2.html\3",
            text,
        )
        text = re.sub(
            r'((?:href|src)=["\'])(?!\.\./|/)assets/',
            r"\1../assets/",
            text,
        )
        text = re.sub(
            r"(url\(\s*['\"]?)(?!\.\./|/)images/",
            r"\1../images/",
            text,
            flags=re.I,
        )
        for article in FULL_ENGLISH_ARTICLES:
            if not path.with_name(article).exists():
                text = re.sub(
                    rf'((?:href|src)=["\'])(?!\.\./|/){re.escape(article)}([?#"\'])',
                    rf"\1../{article}\2",
                    text,
                )
                text = re.sub(
                    rf"(\bb:\s*['\"])(?!\.\./){re.escape(article)}(['\"])",
                    rf"\1../{article}\2",
                    text,
                )

        canonical = (
            f"https://jftagro.com/{path.parent.name}/"
            if path.name == "index.html"
            else f"https://jftagro.com/{path.parent.name}/{path.name}"
        )
        text = re.sub(
            r'(<link\s+rel=["\']canonical["\']\s+href=["\'])[^"\']+(["\'])',
            rf"\1{canonical}\2",
            text,
            count=1,
            flags=re.I,
        )
        text = re.sub(
            r'(<meta\s+property=["\']og:url["\']\s+content=["\'])[^"\']+(["\'])',
            rf"\1{canonical}\2",
            text,
            count=1,
            flags=re.I,
        )

    if "Placeholder page" in text or "Placeholder:" in text:
        if not re.search(r'<meta\s+name=["\']robots["\']', text, flags=re.I):
            text = text.replace("<head>", '<head>\n  <meta name="robots" content="noindex,follow">', 1)

    if path.name in UNPUBLISHED_BLOGS:
        if re.search(r'<meta\s+name=["\']robots["\']', text, flags=re.I):
            text = re.sub(
                r'<meta\s+name=["\']robots["\'][^>]*>',
                '<meta name="robots" content="noindex,follow">',
                text,
                count=1,
                flags=re.I,
            )
        else:
            text = text.replace("<head>", '<head>\n  <meta name="robots" content="noindex,follow">', 1)

    if path.name == "products.html":
        for unpublished, replacement in {
            "blog-indian-white-rice-export-policy-2026-latest-updates.html": "blog-ir64-export.html",
            "blog-spice-trends-2026.html": "blog-turmeric-finger-export-india-2026.html",
            "blog-sesame-export-2026.html": "blog-top-indian-agro-commodities-import-2026.html",
            "blog-sugar-s30-export-india-2026.html": "blog-top-indian-agro-commodities-import-2026.html",
            "blog-yellow-maize-export-india-2026.html": "blog-top-indian-agro-commodities-import-2026.html",
        }.items():
            text = text.replace(f"b: '{unpublished}'", f"b: '{replacement}'")

    if path.name == "sugar-s30-supplier.html":
        text = re.sub(
            r'\s*<!-- Blog Cross-Link -->\s*<div[^>]*>.*?blog-sugar-s30-export-india-2026\.html.*?</div></div>',
            "",
            text,
            count=1,
            flags=re.I | re.S,
        )

    if path.name in DOUBLE_H1_PAGES:
        text = replace_second_h1(text)

    if path.name == "certificates.html":
        text = text.replace(
            "Download JFT Agro Overseas official certificates: ISO 9001:2015, APEDA, FSSAI, Spices Board, HACCP, Star Export House. All documents verified and current.",
            "Review JFT Agro Overseas certifications and request current stamped copies for trade verification. Download our corporate introduction.",
        )
        text = text.replace(
            "Download our full accreditation portfolio — ISO, APEDA, FSSAI, HACCP, Star Export House and more.",
            "Review our accreditation portfolio and request current stamped copies from the trade desk.",
        )
        text = text.replace(
            "Every certificate on this page is current, verified, and available for immediate download by our trade partners.",
            "Certificate summaries are provided for buyer reference. Request current stamped copies from our trade desk for formal verification.",
        )
        text = text.replace(
            'Click "Download" to get a PDF copy. For original stamped copies, use the "Request Copy" button.',
            'Download our company introduction below. For current stamped certificate copies, use the "Request" button on the relevant card.',
        )
        text = text.replace(
            '<i class="fa-solid fa-download"></i> Download</a>',
            '<i class="fa-solid fa-file-pdf"></i> Company Profile</a>',
        )

    if path.name == "404.html":
        text = re.sub(
            r'\s*<div class="bg-text">404</div>\s*<div class="content">.*?</div>\s*',
            "\n",
            text,
            count=1,
            flags=re.S,
        )
        text = text.replace(
            '<section style="min-height:100vh;',
            '<section id="main-content" tabindex="-1" style="min-height:100vh;',
            1,
        )
        text = re.sub(
            r'<div style="position:absolute;inset:0;background-image:url\([^>]+></div>',
            '<div style="position:absolute;inset:0;background:radial-gradient(circle at center,rgba(238,191,69,.06),transparent 65%);pointer-events:none;"></div>',
            text,
            count=1,
        )

    if path.name == "thank-you.html":
        text = text.replace('<div class="card">', '<div class="card" id="main-content" tabindex="-1">', 1)

    if 'id="header-placeholder"' in text and 'id="main-content"' not in text:
        if re.search(r"<main\b", text, flags=re.I):
            text = re.sub(r"<main\b", '<main id="main-content" tabindex="-1"', text, count=1, flags=re.I)
        else:
            text = re.sub(
                r'(<div\s+id=["\']header-placeholder["\']\s*>\s*</div>)',
                r'\1\n<div id="main-content" tabindex="-1"></div>',
                text,
                count=1,
                flags=re.I,
            )

    if path.name == "blog-how-to-export-india-to-africa.html":
        text = re.sub(
            r"win\.document\.write\('</style>\s*.*?</head><body>'\);",
            "win.document.write('</style></head><body>');",
            text,
            count=1,
            flags=re.S,
        )

    if path.name == "products.html" and 'id="product-page-directory"' not in text:
        links = "\n".join(
            f'          <li><a href="{url}">{url[:-5].replace("-", " ").title()}</a></li>'
            for url in sorted(image_map)
        )
        directory = f'''\n  <section id="product-page-directory" class="jft-wide-container" aria-labelledby="product-directory-title" style="padding:0 24px 60px;">
    <details style="background:#fff;border:1px solid rgba(26,60,52,.14);border-radius:12px;padding:18px 22px;">
      <summary id="product-directory-title" style="cursor:pointer;font-family:var(--font-sub);font-weight:800;color:var(--jft-navy);">Browse all product specification pages</summary>
      <ul style="columns:3 240px;column-gap:28px;margin:18px 0 0;padding-left:20px;line-height:1.9;">
{links}
      </ul>
    </details>
  </section>
'''
        text = text.replace('  <div id="footer-placeholder"></div>', directory + '  <div id="footer-placeholder"></div>', 1)

    expected_image = image_map.get(path.name)
    if expected_image:
        expected_path = ("../" if localized else "") + expected_image
        # Product-detail pages only use the product image in metadata, preload,
        # and the hero image; replace any stale product asset consistently.
        text = re.sub(
            r'(?:\.\./)?images/products/[^"\']+\.(?:webp|png|jpe?g)',
            expected_path,
            text,
            flags=re.I,
        )

    # Product asset replacement must not introduce a relative segment into
    # absolute metadata URLs. Encode spaces there for valid social-card URLs.
    text = text.replace("https://jftagro.com/../images/", "https://jftagro.com/images/")
    text = re.sub(
        r'https://jftagro\.com/images/products/[^"\']+',
        lambda match: match.group(0).replace(" ", "%20"),
        text,
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    image_map = product_images()
    changed = [path for path in ROOT.rglob("*.html") if fix_html(path, image_map)]
    print(f"Updated {len(changed)} HTML files; product map contains {len(image_map)} entries.")
    if 0 < len(changed) <= 20:
        for path in changed:
            print(f"  - {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
