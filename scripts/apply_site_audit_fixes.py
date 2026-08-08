#!/usr/bin/env python3
"""Apply deterministic, idempotent fixes found by the full-site audit."""

from __future__ import annotations

import re
from pathlib import Path


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


def fix_html(path: Path, image_map: dict[str, str]) -> bool:
    original = path.read_text(encoding="utf-8")
    text = original
    localized = path.parent.name in LANGS

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
    text = re.sub(
        r'<script\s+async\s+src="https://www\.googletagmanager\.com/gtag/js\?id=G-MWZ2ZWZP4G"></script>\s*',
        "",
        text,
    )
    if path.name != "header.html":
        text = re.sub(
            r'\s*<!--Start of Tawk\.to Script-->\s*<script[^>]*>.*?embed\.tawk\.to.*?</script>\s*<!--End of Tawk\.to Script-->\s*',
            "\n",
            text,
            flags=re.I | re.S,
        )
        text = re.sub(
            r'\s*<!-- Tawk\.to -->\s*<script[^>]*>[^<]*embed\.tawk\.to[^<]*</script>\s*',
            "\n",
            text,
            flags=re.I,
        )
        text = re.sub(
            r'\s*<script\b[^>]*>[^<]*(?:embed\.tawk\.to|googletagmanager\.com/gtag/js\?id=G-MWZ2ZWZP4G)[^<]*</script>\s*',
            "\n",
            text,
            flags=re.I,
        )

    if "Content-Security-Policy" in text and "https://embed.tawk.to" not in text.split("Content-Security-Policy", 1)[1].split(">", 1)[0]:
        text = text.replace("script-src 'self'", "script-src 'self' https://embed.tawk.to", 1)
        text = text.replace("connect-src 'self'", "connect-src 'self' https://*.tawk.to wss://*.tawk.to", 1)
        text = text.replace("frame-src ", "frame-src https://*.tawk.to ", 1)

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

        canonical = f"https://jftagro.com/{path.parent.name}/{path.name}"
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


if __name__ == "__main__":
    main()
