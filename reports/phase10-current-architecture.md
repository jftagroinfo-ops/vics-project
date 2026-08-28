# Phase 10, Part A — Current Architecture (Investigation, Before Any Change)

Traced from the actual source files, not assumed from the Phase 9 report alone.

## All-products page
`products.html` is the only page between the homepage and individual products.
It lists all 84 products with a client-side JS filter (`filterProducts(cat)`,
`.cz-tab[data-cat="..."]` buttons) that shows/hides already-loaded product
cards by category. It also reads a `?cat=` query-string parameter on load
(`urlParams.get('cat')`) to pre-activate a filter tab, which is what
`header.html`'s Products dropdown currently links to
(`products.html?cat=rice`, etc.). None of this produces a separate, crawlable
URL per category — Google sees one URL (`products.html`) regardless of filter
state.

## Existing commodity references (already-designed taxonomy)
`header.html`'s "Products" dropdown already lists exactly the 10 commodity
groups with icons and labels: Rice (`fa-seedling`), Spices (`fa-pepper-hot`),
Wheat (`fa-wheat-awn`), Flour & Grains (`fa-bowl-food`), Pulses (`fa-circle`),
Oilseeds (`fa-droplet`), Herbs & Seeds (`fa-leaf`), Animal Feed (`fa-cow`),
Sugar (`fa-cubes`), and "Fruits" (`fa-apple-whole`, mapped to the `raisins`
commodity — an existing label mismatch, not something this phase introduced;
noted, not changed, since `header.html` navigation itself was not modified
this phase). `products.html`'s own filter tabs use the same 10-way split
(labelled "Pulses" uses `fa-seedling` there, inconsistent with the header's
`fa-circle` — another pre-existing, minor inconsistency, not touched).

## Product directories
Products are flat files at repository root (e.g.
`1121-basmati-rice-exporter.html`), no `/products/` directory. No existing
`/rice/`, `/category/`, or similar directory exists.

## Navigation structure
`header.html` is a single shared file, fetched client-side
(`fetch('../header.html')` from locale pages, `fetch('header.html')` from
root pages) and injected into `#header-placeholder` on every page. Its
relative hrefs (e.g. `href="products.html"`) are deliberately unprefixed so
they resolve relative to *whichever page injected them* — meaning the same
header correctly points to `/ar/products.html` on an Arabic page and
`/products.html` on an English page. This is why any header link that does
not yet have an equivalent file in every locale (which describes the new
category pages, English-only this phase) cannot safely be added to the shared
header without either prefixing it as a root-relative absolute path (serving
every locale visitor an English-only page from a nav click) or waiting until
locale category pages exist. This phase did not modify `header.html` for
that reason — see Part F.

## Product breadcrumbs (before this phase)
Every product page (English and all 10 locales): `Home > Products > [Product
Name]`, both in the visible `.jft-breadcrumb` nav and the `BreadcrumbList`
JSON-LD. No category level existed anywhere.

## Category-like pages that already exist
None, beyond the client-side filter described above. The 4 regional pages
(`africa-trade.html`, `asia-trade.html`, `europe-trade.html`,
`uae-trade.html`) are market-focused, not commodity-focused, and are a
separate concept from a commodity category page.

## Locale equivalents
Every English page in scope for this phase (84 products, 2 regional pages,
`products.html`, 2 logistics pages) has full locale coverage already,
**except** the new category pages, which are new, English-only files with no
locale directory conflicts to worry about.

## Sitemap behavior
`scripts/generate_sitemap.py` and `scripts/generate_hreflang.py` scan
`ROOT.glob("*.html")` plus each locale directory — a fully generic scan, not
a hardcoded page list. Any new HTML file at repository root with `<html>`,
no `noindex`, and not in a small `EXCLUDED` set (partials/templates only) is
automatically picked up. This is the mechanism this phase used to add the 10
new category pages to the sitemap and hreflang graph, rather than hand-editing
either file (see Part E/Q).

## Internal-link patterns (verified, corrected one prior-phase error)
Two discoveries corrected a Phase 9 claim before any implementation began
(documented in full in the main report's Executive Summary): `africa-trade.html`
and `uae-trade.html` already contain a 5-product `.prod-card` showcase
section linking to real product pages; `asia-trade.html` already contains 5
distinct contextual product links embedded in its market-card prose (not in
`.prod-card` format, which is why a naive class-name search missed them in
Phase 9). Only `europe-trade.html` had zero product links of either kind.
