import os
from datetime import datetime

base_url = "https://jftagro.com/"
directory = os.path.abspath(os.path.dirname(__file__))

LANGS = ["ar","es","fr","id","ms","pt","ru","si","th","vi"]

EXCLUDE = {
    "header.html","footer.html","inner-page-hero-snippet.html",
    "seo-universal-head-snippet.html","product-page-template.html",
    "cookie-consent-snippet.html","thank-you.html","404.html"
}

today = datetime.now().strftime("%Y-%m-%d")
url_count = 0

xml  = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
xml += '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'

for root_dir, dirs, files in os.walk(directory):
    dirs[:] = [d for d in dirs if not d.startswith(".")]

    for file in sorted(files):
        if not file.endswith(".html") or file in EXCLUDE:
            continue

        rel = os.path.relpath(os.path.join(root_dir, file), directory).replace(os.sep, "/")

        # Skip lang sub-directories (ar/, fr/, etc.) – hreflang handled below
        top_dir = rel.split("/")[0]
        if top_dir in LANGS:
            continue

        url = base_url if rel == "index.html" else base_url + rel

        # Priority & changefreq
        if rel == "index.html":
            priority, changefreq = "1.0", "weekly"
        elif rel == "products.html":
            priority, changefreq = "0.9", "weekly"
        elif rel in ("about.html","contact.html","quality-control.html"):
            priority, changefreq = "0.85", "monthly"
        elif "-exporter.html" in rel or "-supplier.html" in rel:
            priority, changefreq = "0.80", "monthly"
        elif rel.startswith("blog"):
            priority, changefreq = "0.70", "monthly"
        elif rel in ("africa-trade.html","asia-trade.html","europe-trade.html","uae-trade.html"):
            priority, changefreq = "0.75", "monthly"
        else:
            priority, changefreq = "0.50", "yearly"

        # Hreflang block
        hreflang = f'    <xhtml:link rel="alternate" hreflang="en" href="{url}"/>\n'
        for lc in LANGS:
            lang_url = base_url + lc + "/" + rel
            hreflang += f'    <xhtml:link rel="alternate" hreflang="{lc}" href="{lang_url}"/>\n'
        hreflang += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url}"/>\n'

        xml += "  <url>\n"
        xml += f"    <loc>{url}</loc>\n"
        xml += f"    <lastmod>{today}</lastmod>\n"
        xml += f"    <changefreq>{changefreq}</changefreq>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += hreflang
        xml += "  </url>\n"
        url_count += 1

xml += "</urlset>"

with open(os.path.join(directory, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(xml)

print(f"[OK] sitemap.xml regenerated — {url_count} URLs with hreflang for {len(LANGS)} languages.")
