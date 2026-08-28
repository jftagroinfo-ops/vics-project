#!/usr/bin/env python3
"""Generate the 10 commodity-category landing pages (English only).

Governed source chain (see reports/phase10-commodity-architecture-2026-08-27.md,
Part A-E): the commodity taxonomy is derived entirely from data/products.json's
`c` field (already the site's own governed categorization, already reflected
in header.html's Products dropdown and products.html's filter tabs -- this
script gives that existing, already-designed taxonomy a real, indexable,
crawlable landing page for each of the 10 groups instead of a client-side
`?cat=` filter state).

Category-specific narrative content (intro/selection-notes/etc.) lives in
scripts/category_content.py and is hand-authored, grounded only in real
products.json facts -- no fabricated claims, no invented specifications.

English only in this pass. Locale category pages are deliberately deferred
(see the report's Part F) -- this generator does not touch any locale
directory.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from category_content import CATEGORIES  # noqa: E402

HREFLANG_LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

# Articles the site's own audit_website.py already tracks as unpublished
# placeholders (UNPUBLISHED_BLOGS) must never be linked from a new category
# page, even if data/products.json's `b` field names one for a product in
# that category -- see reports/phase10-commodity-architecture-2026-08-27.md.
_audit_website_src = (ROOT / "scripts/audit_website.py").read_text(encoding="utf-8")
import re as _re

_match = _re.search(r"UNPUBLISHED_BLOGS\s*=\s*\{([^}]*)\}", _audit_website_src, _re.S)
UNPUBLISHED_BLOGS = set(_re.findall(r'"([^"]+)"', _match.group(1))) if _match else set()


def products_for(commodity: str) -> list[dict]:
    return [p for p in PRODUCTS if p["c"] == commodity]


def render_product_card(p: dict) -> str:
    name = html.escape(p["t"])
    img = html.escape(p["i"])
    hs = html.escape(p["trade"]["hs_code"])
    moq = html.escape(p["trade"]["moq"])
    return (
        f'<a class="prod-card" href="{html.escape(p["u"])}" aria-label="View {name}">'
        f'<div class="prod-img"><img src="{img}" alt="{name}" width="1024" height="1024" loading="lazy"></div>'
        f'<div class="prod-body"><div class="prod-name">{name}</div>'
        f'<div class="prod-detail">HS {hs} &middot; MOQ {moq}</div>'
        f'<div class="prod-fob">View specification &amp; request pricing</div></div></a>'
    )


def render_article_links(articles: list[str]) -> str:
    articles = [a for a in articles if a not in UNPUBLISHED_BLOGS]
    if not articles:
        return ""
    items = []
    for a in articles:
        path = ROOT / a
        title = a
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            import re

            m = re.search(r"<title>(.*?)</title>", text, re.S)
            if m:
                title = m.group(1).split("|")[0].strip()
        items.append(f'<a class="reg-item" href="{html.escape(a)}" style="display:block"><h4>{html.escape(title)}</h4></a>')
    return "\n".join(items)


def render_logistics_links(logistics: list[tuple]) -> str:
    if not logistics:
        return ""
    items = []
    for href, label in logistics:
        items.append(f'<a class="reg-item" href="{html.escape(href)}" style="display:block"><h4>{html.escape(label)}</h4></a>')
    return "\n".join(items)


def related_categories(current_key: str) -> str:
    items = []
    for key, cat in CATEGORIES.items():
        if key == current_key:
            continue
        items.append(f'<a href="{cat["slug"]}" class="btn-outline" style="margin:4px"><i class="fa-solid {cat["icon"]}"></i> {cat["label"]}</a>')
    return "\n".join(items)


def build_jsonld(key: str, cat: dict, prods: list[dict]) -> str:
    url = f"https://jftagro.com/{cat['slug']}"
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://jftagro.com/"},
            {"@type": "ListItem", "position": 2, "name": "Products", "item": "https://jftagro.com/products.html"},
            {"@type": "ListItem", "position": 3, "name": cat["label"].replace("&amp;", "&"), "item": url},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": cat["title"].replace("&amp;", "&"),
        "description": cat["meta"],
        "url": url,
        "inLanguage": "en",
    }
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{cat['label'].replace('&amp;', '&')} products",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": p["t"], "url": f"https://jftagro.com/{p['u']}"}
            for i, p in enumerate(prods)
        ],
    }
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'
        for obj in (breadcrumb, webpage, item_list)
    )


def render_page(key: str, cat: dict) -> str:
    prods = products_for(key)
    url = f"https://jftagro.com/{cat['slug']}"
    hreflang_tags = "\n  ".join(
        [f'<link rel="alternate" hreflang="en" href="{url}">', f'<link rel="alternate" hreflang="x-default" href="{url}">']
    )
    product_cards = "\n".join(render_product_card(p) for p in prods)
    article_section = render_article_links(sorted({p["b"] for p in prods if p.get("b")}))
    logistics_section = render_logistics_links(cat["logistics"])
    related = related_categories(key)

    optional_sections = ""
    if article_section:
        optional_sections += f'''
  <section class="section-alt">
    <div class="container">
      <div class="brand-tag"><i class="fa-solid fa-book"></i> Buyer Guides</div>
      <h2 class="section-title">Related <span>Buyer Guides</span></h2>
      <div class="reg-grid">
{article_section}
      </div>
    </div>
  </section>
'''
    if logistics_section:
        optional_sections += f'''
  <section>
    <div class="container">
      <div class="brand-tag"><i class="fa-solid fa-ship"></i> Logistics</div>
      <h2 class="section-title">Relevant <span>Shipment Routes</span></h2>
      <div class="reg-grid">
{logistics_section}
      </div>
    </div>
  </section>
'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <link rel="stylesheet" href="/assets/fontawesome/css/all.min.css">
  <link rel="stylesheet" href="/assets/fonts/jft-fonts.css">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{cat["title"]}</title>
  <meta name="description" content="{html.escape(cat['meta'])}">
  <meta property="og:title" content="{cat["title"]}">
  <meta property="og:description" content="{html.escape(cat['meta'])}">
  <meta property="og:image" content="https://jftagro.com/{html.escape(prods[0]["i"]) if prods else "images/jft-logo-transparent.webp"}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_IN">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <meta name="author" content="JFT Agro Overseas">
  <meta name="geo.region" content="IN-MH">
  <meta name="geo.placename" content="Navi Mumbai, Maharashtra, India">
  <meta name="theme-color" content="#1a3c34">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="manifest" href="manifest.json">
  <link rel="stylesheet" href="jft-design-system.css">
  <link rel="stylesheet" href="jft-responsive.css">
  <link rel="stylesheet" href="trade-regions.css">
  {build_jsonld(key, cat, prods)}
  <meta property="og:site_name" content="JFT Agro Overseas">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-jft-agro-32.png">
  <link rel="icon" type="image/png" sizes="48x48" href="/images/favicon-jft-agro-48.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon-jft-agro.png">
  <meta property="og:url" content="{url}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{cat["title"]}">
  <meta name="twitter:description" content="{html.escape(cat['meta'])}">
  <link rel="canonical" href="{url}">
  {hreflang_tags}
</head>
<body>
<a href="https://wa.me/918425057274?text=Hi%20JFT%20Agro%2C%20I%20have%20an%20export%20inquiry." class="wa-fab" target="_blank" rel="noopener" aria-label="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>
<button id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="Back to top"><i class="fa-solid fa-arrow-up"></i></button>
<div id="header-placeholder"></div>
<script data-jft-early-header-loader>
  (function () {{
    var target = document.getElementById('header-placeholder');
    function injectHeader() {{
      return fetch('header.html', {{ credentials: 'same-origin' }}).then(function (r) {{ return r.text(); }}).then(function (h) {{
        target.innerHTML = h;
        target.querySelectorAll('script').forEach(function (old) {{
          var s = document.createElement('script');
          Array.from(old.attributes).forEach(function (a) {{ s.setAttribute(a.name, a.value); }});
          s.textContent = old.textContent;
          old.parentNode.replaceChild(s, old);
        }});
        document.dispatchEvent(new CustomEvent('jft:header-ready'));
      }});
    }}
    injectHeader();
  }}());
</script>
<main id="main-content" tabindex="-1">
<section class="jft-page-hero">
  <div class="jft-page-hero-bg" style="background-image:url('images/editorial/real-jnpt-container-port-india-commons.webp');"></div>
  <div class="jft-page-hero-glow"></div>
  <div class="jft-page-hero-gold-stripe"></div>
  <div class="jft-wide-container jft-page-hero-inner">
    <nav class="jft-breadcrumb" aria-label="breadcrumb">
      <a href="/">Home</a><i class="fa-solid fa-chevron-right"></i>
      <a href="products.html">Products</a><i class="fa-solid fa-chevron-right"></i>
      <span style="color:var(--gold)">{cat["label"]}</span>
    </nav>
    <span class="brand-tag brand-tag-white"><i class="fa-solid {cat["icon"]}"></i> {cat["label"]}</span>
    <h1 style="font-size:clamp(2.2rem,5.5vw,4.2rem);font-weight:900;line-height:1.1;color:#fff;letter-spacing:-1.5px;margin:18px 0 20px;">{cat["h1"]}</h1>
    <p class="jft-page-hero-sub">{cat["hero_sub"]}</p>
    <div style="margin-top:32px;display:flex;gap:16px;flex-wrap:wrap;">
      <a href="contact.html#inquiry-form" class="btn-gold"><i class="fa-solid fa-paper-plane"></i> Request Pricing</a>
      <a href="products.html" class="btn-outline"><i class="fa-solid fa-boxes-stacked"></i> All Products</a>
    </div>
  </div>
</section>

<style>
  .container {{ max-width: 1360px; margin: 0 auto; padding: 0 clamp(20px, 5vw, 55px); }}
  section {{ padding: 60px 0; }}
  .section-alt {{ background: #fdfbf7; }}
  .prod-row{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px;margin-top:24px}}
  .reg-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px}}
  @media(max-width:700px){{.reg-grid{{grid-template-columns:1fr}}}}
</style>

<section>
  <div class="container">
    <div class="brand-tag"><i class="fa-solid {cat["icon"]}"></i> Overview</div>
    <h2 class="section-title">What JFT Agro <span>Supplies</span></h2>
    <p>{cat["intro"]}</p>
  </div>
</section>

<section class="section-alt">
  <div class="container">
    <div class="brand-tag"><i class="fa-solid fa-boxes-stacked"></i> Catalogue</div>
    <h2 class="section-title">{cat["label"]} <span>Products</span></h2>
    <div class="prod-row">
{product_cards}
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="brand-tag"><i class="fa-solid fa-clipboard-check"></i> Selection</div>
    <h2 class="section-title">Specification &amp; <span>Selection Considerations</span></h2>
    <p>{cat["selection"]}</p>
    <p style="margin-top:16px;">{cat["markets_note"]}</p>
  </div>
</section>
{optional_sections}
<section class="section-alt">
  <div class="container">
    <div class="brand-tag"><i class="fa-solid fa-shield-halved"></i> Trust</div>
    <h2 class="section-title">Verify Before You <span>Contract</span></h2>
    <p>Review our <a href="certificates.html">certifications</a>, <a href="infrastructure.html">processing infrastructure</a> and <a href="export-documentation.html">export documentation centre</a> before confirming an order. Independent pre-shipment inspection can be arranged and is described in our <a href="quality-control.html">quality control</a> process.</p>
  </div>
</section>

<section style="background:#1a3c34;color:#fff;padding:64px 0;text-align:center;">
  <div class="container">
    <h2 class="section-title" style="color:#fff;">Ready to Request {cat["label"]} Pricing?</h2>
    <p style="color:rgba(255,255,255,.75);max-width:640px;margin:0 auto 24px;">Share your destination port, quantity and packing requirement for a contract-based quote.</p>
    <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">
      <a href="contact.html#inquiry-form" class="btn-gold"><i class="fa-solid fa-file-invoice-dollar"></i> Request Pricing</a>
      <a href="sample-request.html" class="btn-outline" style="color:#fff;border-color:rgba(255,255,255,.4)"><i class="fa-solid fa-box-open"></i> Request Sample</a>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="brand-tag"><i class="fa-solid fa-diagram-project"></i> Explore</div>
    <h2 class="section-title">Related <span>Categories</span></h2>
    <div style="margin-top:16px;">
{related}
    </div>
  </div>
</section>
</main>
<div id="footer-placeholder"></div>
<script>
(function(){{
  document.addEventListener('jft:header-ready', function(){{
    fetch('footer.html', {{ credentials: 'same-origin' }}).then(function(r){{return r.text();}}).then(function(h){{
      document.getElementById('footer-placeholder').innerHTML = h;
    }});
  }});
}})();
</script>
</body>
</html>
'''


def main() -> int:
    for key, cat in CATEGORIES.items():
        out_path = ROOT / cat["slug"]
        out_path.write_text(render_page(key, cat), encoding="utf-8", newline="\n")
        print(f"wrote {cat['slug']} ({len(products_for(key))} products)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
