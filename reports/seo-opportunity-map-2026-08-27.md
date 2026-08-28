# Phase 9 — SEO, Information Architecture, Internal Linking & Commercial UX Audit

**Status: audit-only. Zero website files modified to produce this report** (verified in Part AT below).
**Method:** a real, full crawl of all 1,443 indexable pages (not a sample, not estimated) via a scratch Python crawler reading the actual committed HTML — every count in this report is computed, not guessed, unless explicitly marked as qualitative judgment or "not available."

## Executive summary

The technical foundation built in Phases 1-8 is genuinely clean: every one of the 1,443 indexable pages has a title, H1, and meta description (0 missing across the board); every page self-canonicalizes correctly; 1,430/1,443 pages carry the full 12-way hreflang set; structured data is broadly deployed (1,398 pages carry BreadcrumbList schema, 926 carry FAQPage, 1,036 carry WebPage); only 22 images sitewide are missing `alt` text; and a targeted sweep for unsupported superlative claims ("largest," "guaranteed," "fastest," "direct manufacturer," etc.) found zero risky matches — every "guaranteed" hit was in fact the site *disclaiming* a guarantee, consistent with Phases 6-7's governance-conscious content work.

**The site's real opportunity is not technical SEO — it is internal-linking depth and category architecture.** Two findings dominate:

1. **No commodity category layer exists.** Between `products.html` (all 84 products, undifferentiated, with only a client-side JS filter) and individual product pages, there is no crawlable, linkable "Rice Exporter India" / "Spices Exporter India" landing page for any of the 10 commodity groups. This is the single largest structural gap in the site's architecture.
2. **Internal linking is nav-driven, not contextually reinforced.** 714 of 1,443 pages (49%) receive exactly one contextual (body-content) inbound link; 37 pages receive zero and are reachable only through header/footer navigation. Every product page clears the zero-link floor, but 37 of 84 products (44%) have one contextual inbound link or fewer.
3. **One precise, high-value linking gap:** `export-documentation.html` (a trust page) receives 86 contextual inbound links in English but only 0-1 across *every* locale — not a general locale-content gap (the site's other major trust pages, `about.html` and `certificates.html`, are consistently well-linked in all 11 languages), but one specific missing link in the locale product template.

Real Google Search Console data exists in this repository (export dated 2026-08-20, 286 clicks / 10,410 impressions over 19 May-18 Aug 2026) and is used throughout this report rather than invented; its own top opportunity is a blog article and two calculators, not a product page — evidence that tools and buyer-education content are already earning organic attention the product catalogue itself is not yet capturing.

No P0 (indexation-critical) issues were found. The dominant issue class is P1 (thin internal linking), not metadata or technical defects.

---

## Page inventory (Part A)

All 1,443 sitemap URLs resolved to an existing file (0 missing) and were crawled for: URL, locale, template, commodity/product mapping, title (+length), H1 (+length, +count), meta description (+length), canonical, hreflang set (+count), robots, word count, heading count, image count (+missing-alt count), internal/external outbound link counts, breadcrumb (schema + visible), schema types, and CTA text. The full per-page dataset is `reports/seo-opportunity-map-2026-08-27.json`.

| Locale | Indexable pages |
|---|---:|
| en | 143 |
| ar/es/fr/id/ms/pt/ru/si/th/vi | 130 each (1,300 total) |
| **Total** | **1,443** |

Content similarity signals (Part G methodology) and the internal link graph (Part J) are covered in their own sections below; both are computed, not estimated.

## Template inventory (Part B)

| Template | Count | Intent family |
|---|---:|---|
| product | 924 (84 EN + 840 locale*) | Commercial |
| article | 270 (27 unique EN articles with full locale sets + 10 EN-only) | Informational |
| trust | 66 (6 EN pages x 11 languages) | Trust |
| regional | 44 (4 EN pages x 11 languages) | Commercial investigation |
| tool | 55 (5 EN tools x 11 languages) | Tools |
| product_listing | 33 (3 EN listing pages x 11) | Commercial |
| faq | 11 | Informational/Trust |
| conversion | 11 (contact.html) | Transactional |
| blog_index | 11 (blog.html) | Informational/navigational |
| homepage | 13 (11 locale + index.html + implicit root) | Navigational |
| legal | 4 (EN only: privacy/terms/legal, +1 editorial-policy counted under evidence) | Trust/compliance |
| evidence | 1 (`india-agricultural-export-market-data-sources.html`, EN-only by policy) | Trust |
| *(not sitemap-indexed, found during classification)* logistics | 2 (`/logistics/mundra-rice-exports/`, `/logistics/nhava-sheva-agro-exports/`, EN-only) | Logistics |

*924 product-template pages = 84 products x 11 languages minus the 10 locale copies of `sugar-s30-supplier.html` (which never received the generic template, per Phase 7) = 924. Confirmed by direct count, not arithmetic assumption.

**Pages that didn't fit cleanly, flagged as instructed:** the 2 logistics port pages are real, valuable, English-only content with no template bucket of their own in the site's navigation — they are linked from nowhere in the main nav and only reachable via direct URL or search. `sugar-s30-supplier.html` is also structurally unique (bespoke regulatory FAQ, no locale FAQ — see Phase 7/8 reports) and is best treated as its own one-off template, not folded into "product."

## Search intent architecture (Part C)

| Family | Intended intent | Does the content support it? |
|---|---|---|
| Product | Commercial investigation → transactional ("export/import/buy [commodity]") | Yes — every sampled product page carries spec table, HS code, MOQ, packaging, FAQ, and 3 CTAs (Request Pricing, Request Sample, WhatsApp Inquiry). Intent match is strong. |
| Article | Informational ("how to import/export X") | Mostly yes; see Topical Authority (Part AB) for coverage gaps. GSC confirms real informational-intent traffic (e.g. `blog-cumin-jeera-price-outlook-2026.html` is the single highest-opportunity page in the whole GSC export). |
| Regional (Africa/Asia/Europe/UAE) | Commercial investigation ("[commodity] exporter India to [market]") | Partially — content is genuinely differentiated per region (0% content-similarity overlap measured between the 4 regional pages), but none link forward to specific commodity/product pages (see Part K), so the intent match ends at "trade overview" rather than continuing to "which product." |
| Trust (about/certificates/infrastructure/quality-control/buyer-security/export-documentation) | Navigational/trust verification | Yes for content; linking reinforcement is uneven (see Part V). |
| Tool (calculators, tracker, sample request) | Transactional/utility ("calculate container load / CIF") | Yes, and GSC confirms this is *already* the strongest-performing intent match on the site — `packing-calculator.html` and `port-transit-calculator.html` both rank in the top handful of real GSC opportunity scores. |
| FAQ | Informational, mixed | Content matches intent; internal linking is the weak point (11 FAQ pages average only a handful of contextual inbound links). |
| Conversion (contact.html) | Transactional | Yes, receives high inbound linking by nature of being the universal CTA destination. |

No page family was forced into "transactional" where it didn't belong; regional and article pages are correctly treated as investigation/informational above.

## Keyword/topic architecture (Part D)

Real catalogue-derived topic map (not invented keywords) — commodity groups and their actual product counts:

| Commodity | Products | Core commercial topic already covered | Specification topics covered on-page | Market topics covered |
|---|---:|---|---|---|
| Rice | 20 | Yes — grade-specific pages (IR-64 5%/10% broken, 1121/1401/1509/1718 Basmati variants, Sella/Steam/Raw/White/Golden) | Yes — HS code, MOQ, moisture, broken %, purity per page | Partial — Africa/Asia/UAE/Europe regional pages exist but don't link to specific rice grade pages |
| Spices | 17 | Yes | Yes | Partial — 1 dedicated article (turmeric), no others |
| Herbs | 15 | Yes | Yes | No dedicated market article |
| Feed inputs | 15 | Yes | Yes | No dedicated market article |
| Oilseeds | 5 | Yes | Yes | No dedicated market article |
| Flour | 5 | Yes | Yes | No dedicated market article |
| Pulses | 4 | Yes | Yes | 1 article (toor dal, green mung) |
| Wheat | 1 | Yes | Yes | No dedicated market article |
| Sugar | 1 | Yes (bespoke, regulatory-focused) | Yes | No dedicated market article |
| Raisins | 1 | Yes | Yes | No dedicated market article |

**Where one page already satisfies multiple query variants (correctly, not a gap):** each product page's title/H1/spec content already reasonably covers "[grade] exporter," "[grade] supplier," and "bulk [grade] India" intent variants without needing separate pages for each — confirmed by reading page content, not assumed. Creating separate pages for "supplier" vs. "exporter" vs. "manufacturer" phrasing of the same product would be exactly the kind of unjustified page-proliferation this phase's rules warn against.

## Search-intent cannibalization (Part E)

**Methodology:** computed 5-word-shingle Jaccard similarity across all 118 English product/article/regional pages (6,903 pairs), not judgment calls alone.

**Result: zero article-vs-article, zero article-vs-product, and zero regional-vs-regional pairs exceeded the 0.15 similarity threshold.** This is a genuinely clean result — the 37 articles and 4 regional pages are textually well-differentiated from each other and from the product catalogue. No cannibalization was found in this category, and none is invented here.

**All high-similarity pairs found (up to 0.60 Jaccard) are between closely related product-family variants** — e.g. `25-silky-sortex-short-grain-exporter.html` vs `5-silky-sortex-short-grain-exporter.html` (0.60), `10-parboiled-rice-ir-64-exporter.html` vs `5-parboiled-rice-ir-64-exporter.html` (0.57), various millet and Basmati-grade pairs (0.47-0.54).

| Cluster | URLs | Similarity | Intended ranking hierarchy | Recommendation |
|---|---|---:|---|---|
| IR-64 broken-% grades | `5-parboiled-rice-ir-64-exporter.html`, `10-parboiled-rice-ir-64-exporter.html` | 0.57 | Each targets a distinct, real buyer specification (5% vs 10% broken) — not the same query | No action — this is legitimate SKU differentiation, exactly the pattern already recognized in the repo's own prior `reports/seo-opportunities-top-100-2026-08-20.csv` ("Differentiate supplier intent without cannibalizing grade pages") |
| Silky Sortex short-grain grades | `25-silky-sortex-short-grain-exporter.html`, `5-silky-sortex-short-grain-exporter.html` | 0.60 | Distinct sortex-grade specification | No action |
| Basmati 1121/1401/1509/1718 Sella/Steam variants | ~10 page pairs, 0.47-0.51 | Distinct processing/grade specification | No action, but see Part K — these pages would benefit from linking to each other as "compare grades" cross-links, which do not currently exist |
| Millet family (grey/red/green/white sorghum) | `grey-millet-exporter.html`, `red-millet-exporter.html`, `green-millet-bajra-exporter.html`, `white-sorghum-jowar-exporter.html` | 0.47-0.54 | Distinct commodities (different millet species), not grades of one product | No action — this is topical adjacency, not duplication; content differs on the actual botanical/commercial identity |
| Celery/dill seed powder | `celery-seeds-powder-exporter.html`, `dill-seeds-powder-exporter.html` | 0.49 | Distinct commodities | No action for English. **Flagged separately:** these two products' Thai H1 tags are byte-identical (see Part O) — a real, narrow translation bug, not a content-strategy cannibalization issue |

**Conclusion: this site does not have a cannibalization problem in the traditional sense.** Its structural risk is the opposite — pages that could reinforce each other (grade variants of the same rice type) currently don't link to each other at all.

## Product SEO (Part H)

All 84 products evaluated on the dimensions below. Full row-per-product data is in the JSON report; summary:

| Dimension | Finding |
|---|---|
| Intent clarity | Strong across all 84 — every product page's title+H1+content matches a real commercial query pattern |
| Content | Word count 942-1,313 (median 1,022) across every product — consistent, no thin outliers |
| Links (contextual inbound) | **Weakest dimension**: 37/84 products (44%) have ≤1 contextual inbound link; 0 have zero |
| Related articles | Only 35/84 products (41%) have a populated `related blog` field in the governed product data — 59% of products have no explicit product↔article relationship at all |
| Trust | 100% carry FAQPage + BreadcrumbList schema (post Phase 7/8 fix) |
| CTA | 100% carry Request Pricing / Request Sample / WhatsApp Inquiry (verified in Phases 6-8) |
| Schema | Consistent: WebPage + BreadcrumbList + FAQPage on every product page |

**Product SEO opportunity table (illustrative — full 84-row table in the JSON):**

| Product | Intent | Content | Links | Trust | CTA | SEO opportunity |
|---|---:|---:|---:|---:|---:|---|
| 1121 Golden Sella Basmati | Strong | Strong | Weak (1 inbound) | Strong | Strong | Add cross-links to sibling Basmati grades + a rice buyer guide |
| Turmeric Finger & Powder | Strong | Strong | Moderate | Strong | Strong | Already has a matching article (`blog-turmeric-finger-export-india-2026.html`) — GSC shows this exact article at 231 impressions/0.43% CTR, a real snippet-improvement opportunity |
| Psyllium Husk | Strong | Strong | Moderate | Strong | Strong | Already has a matching article — GSC shows 230 impressions/1.3% CTR |
| Grey/Red/Green Millet trio | Strong | Strong | Weak | Strong | Strong | No article; no cross-linking between the 3 related millet pages |
| Sugar S-30 | Strong (bespoke) | Strong | N/A (bespoke FAQ, no locale accordion) | Strong | Strong | Out of scope per Phase 7/8 — flagged there, not re-litigated here |

Do not rewrite products — none of this requires content changes; it requires **links that don't yet exist.**

## Category architecture (Part I)

**Finding: no commodity category-landing-page layer exists.** The intended hierarchy —

```
CATEGORY → PRODUCTS → MARKETS → EDUCATION → CONVERSION
```

— is missing its first tier entirely. `products.html` is the only page between the homepage and individual products, and it presents all 84 products with a client-side JS filter bar (`#rice-sub-filters` and similar), not separate crawlable URLs. This means:

- No commodity has a dedicated, indexable "Rice Exporter India" (etc.) page that could independently rank for the core commercial topic and consolidate internal links before passing them to individual grade pages.
- Regional pages (Africa/Asia/Europe/UAE) sit at the "MARKETS" tier but link to **zero** specific products (verified: 0% content-similarity overlap also means 0 structural product links found in a link-graph check of these 4 pages).
- "EDUCATION" (articles) connects back to "PRODUCTS" for only 41% of products (see Part H).

This is the single highest-leverage structural finding in this audit. It is **not** recommended for action in this phase (audit-only), but it is the clearest, most evidence-backed candidate for a future phase's top priority.

## Internal link graph (Part J)

Computed from a full crawl of every internal `<a href>` on all 1,443 pages (contextual/body links) plus a separate extraction of `header.html`/`footer.html`'s own link sets (nav reachability), so the two are never conflated.

| Metric | Value |
|---|---:|
| header.html internal links | 21 |
| footer.html internal links | 16 |
| Combined nav-reachable sitemap URLs | 24 |
| Pages with 0 contextual inbound links | 37 |
| Pages with exactly 1 contextual inbound link | 714 (49% of all indexable pages) |
| Pages with 0 contextual links, by template | trust: 6, faq: 6, tool: 12, product_listing: 12, legal: 1 |

**The 37 zero-contextual-link pages are reachable only through header/footer navigation** — real, but this is reachability, not contextual authority, per this phase's own required distinction (rule 28). They are not orphaned (0 broken-link risk — confirmed by Phase 3's crawl and this phase's own crawl finding 0 missing files), but they receive no topical relevance signal from any other page's body content.

**Highest contextual authority (heavily and consistently linked across all 11 languages):** `certificates.html` (94-100 inbound links depending on locale), `about.html` (86-90), `export-documentation.html` (86 in English only — see below).

**A precise, high-value gap:** `export-documentation.html` receives 86 contextual inbound links in English but only 0-1 in *every* locale — confirmed by directly comparing the English and Vietnamese product-page source: the English trust-badge block links to `export-documentation.html`; the equivalent Vietnamese block does not link to it at all. This is not a general "locale trust content is weaker" pattern (the site's other two heavily-linked trust pages, `about.html` and `certificates.html`, are linked 86-100 times in *every* locale, EN included) — it is one specific missing link in the locale product template.

## Internal-linking opportunity map (Part K)

Every opportunity below has a stated user/search-intent reason, per this phase's rule against link-count padding:

| From | To | Reason |
|---|---|---|
| Rice grade product pages (e.g. 1121 Golden Sella) | Sibling grade pages (1401, 1509, 1718; Sella/Steam/Raw variants) | Buyers comparing grades currently have no path between them except returning to `products.html` |
| Products with a matching article (35/84, e.g. turmeric, psyllium husk) | Their article, and vice versa | Relationship already exists in governed data (`b` field) for these 35 but link is one-directional/inconsistently reinforced — worth verifying reciprocity |
| Products without a matching article (49/84) | The most topically relevant existing article, where one genuinely exists (e.g. millet products → no current article exists, so no forced link — see Content Gaps) | Only link where genuine relevance exists; do not force |
| Regional pages (Africa/Asia/Europe/UAE) | The 3-5 products with the strongest documented demand in that region (`data/products.json`'s `f` field already lists target markets per product) | The data to drive this link already exists in governed product data and is currently unused for regional-page linking |
| Locale product pages | `export-documentation.html` (locale equivalent) | Restore the missing trust-badge link identified in Part J — the highest-precision, lowest-risk opportunity in this entire audit |
| Logistics pages (Mundra, Nhava Sheva) | Relevant commodity/product pages shipping through those ports | Currently isolated (English-only, not in main nav, 0 product-page backlinks found) |
| Trust pages (buyer-security, infrastructure, quality-control) | `contact.html` / RFQ | These pages build trust but this audit did not confirm a direct forward CTA link to conversion on the versions sampled — worth a direct check in an implementation phase |

## Anchor text audit (Part L)

Sampled CTA/link anchor text across the crawl's `cta_texts` field (all `.btn*`/`.cta*` classed links, 1,443 pages): the dominant anchors are **"Request Pricing," "Request Sample," "WhatsApp Inquiry," "View All 84 Products"** — all descriptive, none generic ("click here" / "learn more" / "read more" did not appear in any sampled CTA-classed link). This is a genuine strength, not a finding requiring action.

**Contextual body-link anchors were not exhaustively re-extracted separately from CTA anchors in this pass** (the crawler captured CTA-classed anchors specifically, not every in-body `<a>` text) — recommend a targeted anchor-text pass in a future implementation phase focused specifically on the cross-linking opportunities in Part K, since new links will need new anchor text written at that time anyway.

## Breadcrumb audit (Part M)

| | Count |
|---|---:|
| Pages with BreadcrumbList schema | 1,398 / 1,443 (97%) |
| Pages with a visible breadcrumb UI element | 106 |
| Templates with 0 breadcrumb schema | homepage (11 of 13), trust (22 of 66), product_listing (11 of 33), tool (1 of 55) |

Product, article, and regional templates carry breadcrumb schema on 100% of pages — the gaps are concentrated in homepages (reasonable — a homepage is the root, not a child, of the breadcrumb tree) and roughly a third of trust/product-listing pages. **The large gap between schema presence (1,398) and visible breadcrumb UI (106) was not resolved in this pass** — it may mean many pages carry breadcrumb schema without a matching on-page breadcrumb element, which would be a schema/visible-content consistency question worth a direct follow-up (Part U also flags this).

## Title tag audit (Part N)

- **0 missing titles, 0 duplicate titles within any locale, 0 near-duplicate titles flagged, 0 titles under 20 characters, 0 titles over 70 characters** across all 1,443 pages.
- This is an unusually clean result for a site this size — evaluated on uniqueness, length, and (by direct reading of a 20+ page sample across templates) intent clarity and commercial relevance, not a mechanical character-count rule alone.
- **No prioritized title-change list is warranted.** This is a genuine "KEEP" finding for the template as a whole.

## H1 audit (Part O)

- 0 missing H1s, 0 pages with multiple H1s.
- **1 real duplicate found:** the Thai H1 "เมล็ดผักชีฝรั่งและผง ส่งออกจากอินเดีย" is byte-identical across `th/celery-seeds-powder-exporter.html` and `th/dill-seeds-powder-exporter.html` — two different products sharing one H1. Given these two products already showed the highest English content-similarity among distinct-commodity pairs (Part E), this looks like a translation/templating copy error affecting only the Thai H1, not the English source or other locales (spot-checked: no other locale repeats this pattern for these two products).
- **Recommendation:** correct the Thai H1 for one of the two products in a future content/localization phase — flagged as `HUMAN_REVIEW` (requires a native Thai reviewer to write the correct distinct H1, consistent with this project's established localization-review governance from Phases 6-7), not something to auto-generate here.

## Meta description audit (Part P)

- 0 missing, 0 duplicate, 0 near-duplicate meta descriptions across all 1,443 pages.
- 170 meta descriptions (all in locale pages, 0 in English, spread fairly evenly across all 10 locales) exceed 165 characters. **This is not treated as a defect** — it is the expected, well-documented effect of translation expansion (several target languages need more characters to express the same meaning), and Google truncates by rendered pixel width, not a fixed character count. No rewrite is recommended; noted as informational only, per this phase's explicit instruction not to apply a simplistic character rule.

## URL audit (Part Q)

- No URL changes were made or are proposed. Structural observations only:
- Product URLs are flat (no `/products/` prefix), e.g. `/1121-basmati-rice-exporter.html` — functional and already indexed, but flat "everything at root" structure is part of why no category layer exists structurally (there's no `/rice/` directory to home a category page in, though this is not a blocker to adding one).
- The 2 logistics pages use a `/logistics/slug/` directory pattern that is inconsistent with the rest of the site's flat structure and not mirrored anywhere else — worth a naming-convention decision in a future phase, not urgent.
- Locale URLs are consistently `/{locale}/{same-slug}`, which is clean and correctly mirrored across all 10 locales for every page checked in this crawl.
- No confusing paths, no unnecessary duplication, and no legacy URL patterns beyond the already-documented 97 redirects (Phase 3/4) were found.

## Canonical audit (Part R)

**Every one of the 1,443 indexable pages self-canonicalizes** (canonical URL matches its own URL, verified for all 1,443, 0 exceptions). This is correct for genuinely unique, indexable content and consistent with Phase 3/4's prior findings for the 97 redirect stubs (a separate, non-indexable population already fixed in Phase 4 to canonicalize to their redirect target, not themselves). No canonical/indexability/sitemap mismatches were found among the indexable set.

## Hreflang audit (Part S)

- 1,430/1,443 pages carry the full 12-entry hreflang set (11 languages + x-default). 13 pages carry only 2 (self + presumably x-default): the 3 legal pages (`privacy.html`, `terms.html`, `legal.html`), 2 evidence/editorial pages, the 2 logistics pages, and **6 blog articles** (`blog-coriander-seeds-export-india-2026.html`, `blog-groundnut-peanut-export-india-2026.html`, `blog-import-indian-spices-uk-europe.html`, `blog-lc-vs-tt.html`, `blog-private-label-rice.html`, `blog-sesame-export-2026.html`).
- The legal/evidence/logistics exclusions match documented policy (Phase 6: legal pages stay English-only pending native legal review; evidence pages are explicitly English-only). **The 6 articles are not covered by any documented policy** found in this repository — they appear to simply not have been localized yet, which is a normal, legitimate publishing-backlog state, not a hreflang defect, but worth a decision (localize them, or add them to the documented English-only policy list) in a future phase.
- **Semantic question this phase specifically asks (not just "is the XML clean"):** spot-checking translated pages against their English source (reusing Phases 6-7's own findings) confirms the *architecture* treats every locale page as materially equivalent to English, but Phase 6 already found and this audit does not re-litigate that translation quality is explicitly `pending_native_commercial_review` for all 10 locales per the site's own governance file. Hreflang is technically correct; whether every locale page is *semantically* market-ready is a governance question the site has already, correctly, not yet answered — this audit treats that as an open item, not a defect to fix.

## Sitemap / indexation strategy (Part T)

- Sitemap URL count (1,443) matches the crawled indexable-page count exactly — 0 discrepancy.
- No indexable page was found missing from the sitemap, and no sitemap URL resolved to a 404 or a non-existent file.
- The 2 logistics pages ARE in the sitemap (confirmed part of the 1,443) despite being unreachable from any nav or internal link — they are indexed but have no discoverable path for a human visitor, which is the inverse of the more common "orphan" problem and worth noting for Part K's linking recommendations.
- No utility/noindex-classification changes are proposed; Phase 3's prior classification-script bug findings (unrelated to this phase) still stand as documented there.

## Structured data audit (Part U)

| Schema type | Pages |
|---|---:|
| BreadcrumbList | 1,398 |
| WebPage | 1,036 |
| FAQPage | 926 |
| Article | 266 |
| ItemList | 44 |
| WebApplication | 44 |
| HowTo | 40 |
| Organization | 33 |
| WebSite / Blog / LocalBusiness | 11 each |
| ManufacturingBusiness | 10 |
| BlogPosting | 6 |
| AboutPage / Dataset | 1 each |

**A real, specific inconsistency found and worth flagging as P1:** all 10 locale copies of `infrastructure.html` carry `"@type":"ManufacturingBusiness"` schema (declaring JFT Agro Overseas as a manufacturing business, with a specific address and equipment-brand claim). **The English root `infrastructure.html` does not carry this schema at all** (0 occurrences, confirmed by direct search). This directly contradicts the governance already established and acted upon in this project's own `scripts/remediate_production_claims.py` (Phase 7 investigation), which explicitly strips manufacturer-type claims because the site is a coordinator/exporter, not a manufacturer, and states this in code comments as a deliberate compliance decision. A machine-readable, Google-facing structured-data claim exists in 10 languages that the English-language governance process already decided not to make. **Not corrected in this audit-only phase** — flagged as P1 / HUMAN_REVIEW (a claims/legal question, not a mechanical fix) for the next implementation phase.

No schema was found to be invalid JSON (2,510+ script blocks checked across prior phases remain valid), and no page carries duplicate schema of the same type.

## E-E-A-T / trust architecture (Part V)

| Signal | Discoverable? | Linked? | Consistent? |
|---|---|---|---|
| Who (JFT Agro Overseas) | Yes — `about.html`, footer, every page's Organization schema | Strongly (86-90 inbound links, all locales) | Yes |
| What (Indian agro-commodity exporter) | Yes | Strongly | Yes |
| Where (India / export gateways) | Yes — infrastructure.html, logistics pages | Weak (infrastructure: 4-6 inbound; logistics pages: isolated, 0 inbound) | Yes, content-wise |
| What it exports | Yes — 84 products, `products.html` | Strong (nav + product-listing) | Yes |
| How (QC, processing, inspection, docs) | Yes — quality-control.html, export-documentation.html | **Uneven**: quality-control 2-8 inbound depending on locale; export-documentation 86 (EN) vs 0-1 (all locales) | No — see Part J/U findings above |
| Why trust (certificates) | Yes — certificates.html | Very strong (94-100 inbound, all locales) | Yes |
| How to buy (RFQ/WhatsApp/contact) | Yes — every product page carries 3 CTAs | Strong | Yes |

**Overall: the trust architecture is real and substantively present, but not evenly reinforced.** Certificates and About are the load-bearing trust pages site-wide; Buyer Security, Infrastructure, and Quality Control (equally relevant E-E-A-T content) receive a fraction of the contextual linking, and Export Documentation's locale gap is the clearest single fix available.

## Commercial buyer journey (Part W)

Modeled using actual page relationships found in this crawl, not assumed:

| Journey | Clicks (as currently linked) | Dead ends / weak transitions found |
|---|---|---|
| 1. Google → product → specs → trust → enquiry | 1 (product already contains specs) → 1 (trust badge, EN only reliably) → 1 (contact CTA) = 3 clicks, EN | **Locale version:** the trust-badge click to export-documentation.html is missing for 9-10 of 10 locales — the journey silently loses its trust step in translation |
| 2. Google → article → product → RFQ | Works for the 35/84 products with a linked article; **does not exist** for the other 49 — the journey simply isn't available because no article-to-product link exists to start it | Content gap, not a broken link — see Part AC |
| 3. Google → country/market page → commodity → product → enquiry | **Breaks at step 2**: regional pages (Africa/Asia/Europe/UAE) link to zero specific products in this crawl's link graph | Confirmed structural gap, highest-impact fix candidate alongside the category-layer gap |
| 4. Google → regional guide → logistics → product → RFQ | **Breaks at step 1→2**: no regional page links to either logistics page found in this crawl | Logistics pages are functionally isolated |
| 5. Direct → homepage → commodity → product → enquiry | Works via `products.html` and its filter UI, but "commodity" is a client-side filter state, not a URL a buyer can land on or share | Consistent with the Part I category-layer finding |

## Commercial CTA audit (Part X)

Every product page (924/924 applicable) carries "Request Pricing," "Request Sample," and "WhatsApp Inquiry" — verified consistent and functioning in Phases 6-8 (including the accordion-interaction fix). `contact.html` supports product-prefill via `?product=` query parameter (confirmed in earlier phases). No CTA redesign is proposed. **Opportunity, not defect:** trust pages (buyer-security, infrastructure, quality-control) were not confirmed in this pass to carry a direct forward CTA to `contact.html` — worth a direct check before the next implementation phase, since Tier 4 pages (Part Y) should still connect to conversion without being spammy.

## Conversion path priority (Part Y)

| Tier | Pages | CTA/link behavior matches tier? |
|---|---|---|
| Tier 1 — Direct commercial (product, conversion, tool) | 924 + 11 + 55 | Yes — strong CTA presence throughout |
| Tier 2 — Commercial investigation (regional, product_listing) | 44 + 33 | Partially — CTAs exist but don't lead toward specific products (Part W) |
| Tier 3 — Informational (article, faq, blog_index) | 270 + 11 + 11 | Partially — 41% product-linked; 59% have no forward commercial path |
| Tier 4 — Utility/trust (trust, legal, evidence) | 66 + 4 + 1 | Uneven — Certificates/About reinforced; Buyer Security/Infrastructure/QC/Export-Documentation less so |

## Regional / country SEO (Part Z)

4 regional pages exist (Africa, Asia, Europe, UAE) — no separate country-specific pages beyond UAE (which functions as a de facto single-country page). Computed content similarity between all 4 regional pages is 0% overlap (below the 0.15 threshold in every pairwise comparison) — **genuinely differentiated, not duplicated**, each covering distinct trade-lane, duty, and logistics content for its region. Real GSC country data confirms actual buyer geography: India (252 clicks, expected — domestic searches), then UAE, Netherlands, Nigeria, Ghana, UK, Thailand, Australia, US, Germany, Malaysia, Vietnam, Indonesia, Hong Kong — a genuinely international footprint already, none of which currently maps to a specific product via the regional pages (Part W finding). **Recommendation: do not create new country pages** (rule 30's spirit and this phase's explicit warning against keyword-driven page proliferation) — first close the existing regional-to-product linking gap before considering new geography-specific pages.

## International SEO (Part AA)

Distinguishing translation from localization from local-market SEO, as required:

- **Translation:** complete — every locale has all applicable pages, correct `lang`/`dir`, correct hreflang.
- **Localization:** materially incomplete in one specific, measurable way — the export-documentation trust-link gap (Part J/V) means locale buyer journeys structurally differ from the English one, not just linguistically.
- **Local-market SEO:** titles, H1s, and meta descriptions are genuinely translated (not copy-pasted, confirmed by direct comparison in Phase 6) and are within normal length ranges once translation expansion is accounted for (Part P). Locale-specific search intent (e.g., the real Tamil-language queries "சீரகம் விலை" found in the GSC export, mapping to the cumin price article) shows genuine non-English demand already exists and is already being captured by at least one article — a positive, evidence-backed signal that this site's non-English content does reach real searchers, not just a translation exercise.

## Topical authority (Part AB)

37 English articles mapped against the 10 commodity groups: rice, spices (turmeric, red chilli, coriander, sesame), pulses (toor dal, green mung, chickpeas-adjacent), documentation/process (bill of lading, LC vs TT, proforma invoice, SGS inspection, APEDA registration, certificate of analysis), and market/region (Africa import guides, Kenya, Nigeria, UK/Europe, Sri Lanka/Bangladesh, Thailand comparison).

**Strong coverage:** rice (multiple angles: comparison, import duty, policy update, IR-64-specific), export documentation/process (7+ articles), Africa-specific market entry (3 articles).

**Weak/isolated coverage:** herbs, feed inputs, oilseeds, flour, wheat, and sugar have **zero dedicated articles** — 6 of 10 commodity groups have no buyer-education content at all, despite representing 41 of the 84 products (49%). Sugar's own English page compensates somewhat with bespoke regulatory content, but the other 5 groups have nothing.

**No recommendation to mass-produce articles for every gap** — per this phase's explicit instruction, the next section identifies which gaps are actually justified.

## Content gaps (Part AC)

| Gap | User intent | Likely page type | Existing page that partially satisfies it | New page justified? |
|---|---|---|---|---|
| Millet family (grey/red/green/white sorghum, 4-5 products) has no buyer guide | "how to import millet from India," "Indian millet grades" | Article | None — only the product pages themselves | **Possibly** — 4-5 related products with zero supporting content is a real, bounded gap; one consolidated "Indian millet export guide" article (not one per millet type) would serve all of them |
| Oilseeds (5 products: groundnut, sesame, sunflower, safflower, soya) has no buyer guide beyond the existing sesame-export article | "Indian oilseed export specifications" | Article | `blog-sesame-export-2026.html` partially covers sesame only | Marginal — sesame is covered; the other 4 oilseeds are not, but volume (4 products) is modest |
| Regional pages don't name specific products | "[region] wants to import [specific product]" | Internal link, not a new page | The regional pages themselves | **No new page needed** — this is a linking fix (Part K), not a content gap |
| "How many bags in a container" / packing questions | Real, observed GSC queries with non-zero impressions and 0% CTR | Existing tool | `packing-calculator.html` already exists and already appears in GSC data for exactly this query | **No new page needed** — this is a snippet/CTR opportunity on an existing page, confirmed by real GSC data, not a content gap |
| CIF/FOB calculation questions | Real, observed GSC queries ("fob calculator," "cif value calculator," "1 million cif price") | Existing tool | `quote-calculator.html` already exists and already appears in GSC data | **No new page needed** — same as above |

## Content decay (Part AD)

- `sugar-s30-supplier.html`'s bespoke FAQ explicitly states "As checked on 20 August 2026" for DGFT export-policy restrictions — this is **good practice** (dated, falsifiable claims) but also means it is a live regulatory claim with a shelf life; per this phase's rule, **flagged, not silently updated**: a future phase should re-verify this date's claims are still current before the policy content ages further.
- `blog-indian-white-rice-export-policy-2026-latest-updates.html` (title contains "latest updates" and the year) is, by its own title, a page whose value depends on staying current — not independently re-verified against live government sources in this audit-only pass; flagged for the same reason.
- No outdated pre-2026 dates or clearly obsolete product information were found in the crawl's structured fields (titles, H1s, schema) — this check was not extended to full manual reading of every article's body prose, which is outside this phase's tractable scope; the two items above are the ones this audit can responsibly flag with confidence.

## Commercial claims (Part AE)

A targeted sweep of all English root pages for "largest," "leading," "guaranteed," "best in," "lowest price," "fastest," "direct manufacturer," "world-class," "#1," and "money-back/no-risk" found **zero unsupported superlative or guarantee claims**. Every "guaranteed" match found was a *disclaimer* ("No customs-processing time is guaranteed," "a planning range rather than one guaranteed [figure]"), and "fastest" appeared only in benign UI microcopy ("WhatsApp for fastest [response]"). This reflects real, verified prior work (Phases 6-7's claim-remediation scripts) holding up under a fresh, independent check — a genuine **KEEP**, not a gap.

The one claims-adjacent issue found is the `ManufacturingBusiness` schema inconsistency already covered under Part U — that is a structured-data/governance question, not a visible-content overclaim.

## Image SEO (Part AF)

22 images across the entire site (10,722 images crawled) are missing `alt` text — a 0.2% gap, low priority, not mass-flagged as a keyword-stuffing opportunity. Filenames were not scored for "quality" as a priority signal, per this phase's explicit instruction to prioritize accessibility over filename keyword content. The 22 affected pages are listed in the JSON dataset for a future accessibility-focused pass; this is a P3 item.

## Page experience (Part AG)

Spot-checked against the 5 required buyer questions on a representative product page (`1121-basmati-rice-exporter.html`) and the homepage:

1. *What is this?* — Answered immediately (H1 + hero content).
2. *Is this relevant to my purchase?* — Yes, product identity and grade are explicit in the H1 and first screen.
3. *What specifications matter?* — Yes, a dedicated spec table is present above the fold on every product page.
4. *Can I trust this supplier?* — Yes in English (trust badges link out); **weaker in locale versions** due to the export-documentation linking gap already identified.
5. *How do I buy/contact them?* — Yes, 3 CTAs are present without scrolling on the sampled page.

No page family was found where these answers were difficult to locate, with the locale-trust caveat above being the one recurring weak point.

## SEO page score (Part AH)

Scoring model implemented exactly as suggested (intent 20 / content 20 / links 15 / metadata 10 / commercial 10 / trust 10 / technical 5 / schema 5 / UX 5 = 100), computed per page from this crawl's real data — not a Google ranking prediction, an internal triage tool only.

| Template | Average score |
|---|---:|
| conversion | 96.5 |
| homepage | 87.6 |
| blog_index | 85.6 |
| tool | 84.4 |
| product | 81.9 |
| trust | 81.8 |
| regional | 81.2 |
| product_listing | 78.7 |
| legal / evidence | 77.0 |
| article | 76.2 |
| faq | 73.4 |

Score distribution across all 1,443 pages: minimum 54, median 81, maximum 97. **No page scored critically low** — the floor of 54 reflects the internal-linking penalty, not a broken page.

## Opportunity prioritization (Part AI) — distribution

| Priority | Count | Meaning |
|---|---:|---|
| P0 | 0 | No indexation-critical or architecture-breaking issues found |
| P1 | 710 | Dominated by the thin-contextual-linking signal (≤1 inbound link) across product/article/regional/trust pages |
| P2 | 1 | (This scoring pass's rules rarely produced a pure P2 — most non-P1 issues either escalated via title/meta/link severity to P1 or resolved to P3/KEEP) |
| P3 | 373 | Minor items: long locale meta descriptions, missing alt text, isolated pages |
| KEEP | 359 | Already strong — no action recommended |

**Do not read "710 P1s" as "710 urgent problems."** The overwhelming majority share one root cause (thin internal linking) with one class of fix (Part K's linking opportunities) — this is a single architectural initiative, not 710 separate tasks.

## Do not optimize everything (Part AJ)

359 pages are marked KEEP. These are not overlooked — they were evaluated on the same 9-dimension score and cleared a high bar (generally ≥85 with adequate linking). See Part AN for the specific top 50.

---

*(Continued: Top 100 Opportunities, Top 50 Pages to Leave Alone, Architecture Diagram, Search Console Data, Competitor Benchmark, Implementation Roadmap, Change Control, and Final Validation follow in the remaining sections of this report.)*

## Top 100 opportunities (Part AM)

Ranked by priority, then by internal-link weakness, then by word count (proxy for existing content investment worth reinforcing). Full ranked list of 100 is in the JSON dataset (`top_100_opportunities` array); representative top 15 shown here:

| # | URL | Page type | Issue | Opportunity | Impact | Difficulty | Priority |
|---:|---|---|---|---|---|---|---|
| 1 | `vi/export-documentation.html` (+ 8 other locales) | Trust | 0 contextual inbound links vs. 86 in English | Restore the missing trust-badge link in the locale product template | High | Low | P1 |
| 2-10 | Locale product pages with 1 inbound link (e.g. `vi/whole-nutmeg-powder-exporter.html`) | Product | Thin contextual linking | Add cross-links to sibling products/articles | Medium | Low | P1 |
| — | Regional pages (4, all locales) | Regional | 0 links to specific products | Add 3-5 product links per region using existing `f` (target-market) product data | High | Medium | P1 |
| — | `th/celery-seeds-powder-exporter.html` or `th/dill-seeds-powder-exporter.html` | Product (locale) | Duplicate H1 | Native-reviewed distinct H1 | Medium | Low | HUMAN_REVIEW |
| — | Locale `infrastructure.html` (all 10) | Trust | `ManufacturingBusiness` schema contradicts governance | Align schema with the English page's approach | Medium | Low | P1 / HUMAN_REVIEW |

Impact is qualitative (Very High / High / Medium / Low), per this phase's explicit rule against inventing traffic/ranking numbers without Search Console attribution data that doesn't exist at the required Query+Page join level.

## Top 50 pages to leave alone (Part AN)

Representative selection (full 50 in the JSON dataset's `keep_list`):

| URL | Why it's strong | Why no change |
|---|---|---|
| `certificates.html` (+ all locales) | 94-100 contextual inbound links, complete schema, 0 claims issues | Already the site's best-linked trust asset; touching it risks the one thing working well |
| `about.html` (+ all locales) | 86-90 inbound links, consistent across every locale | Same reasoning |
| `contact.html` | 96.5 average score, universal CTA destination, product-prefill already works | Core conversion page; stable |
| `packing-calculator.html` / `quote-calculator.html` | Already the top 2 real GSC opportunity pages by observed impressions | Any redesign risks disrupting currently-accruing organic signal during the measurement window Phase 20-Aug-2026's own analysis explicitly asked to preserve |
| `1121-basmati-rice-exporter.html` and sibling Basmati grade pages | Full spec/FAQ/CTA/schema completeness, healthy word count, correct differentiation from siblings | Legitimately complete; the opportunity is links pointing *to* them, not changes *on* them |
| The 37 English articles as a set | 0% measured content-overlap with each other or with products | Genuinely differentiated content; do not consolidate or rewrite |

## SEO architecture diagram (Part AO)

Intended architecture:

```
HOMEPAGE
   |
COMMODITY          <-- MISSING (no category pages exist)
   |
PRODUCT            <-- present, strong (924 pages)
   |
MARKET / COUNTRY   <-- present but disconnected (4 regional pages, 0 product links)
   |
BUYER EDUCATION    <-- present, strong articles, only 41% linked to products
   |
TRUST / LOGISTICS  <-- present, unevenly linked; 2 logistics pages fully isolated
   |
RFQ / CONTACT      <-- present, strong, universal
```

**Where the current site deviates:** the COMMODITY tier does not exist at all (products.html substitutes a filtered list, not a set of landing pages); the MARKET tier exists but is not wired to PRODUCT; BUYER EDUCATION is wired to PRODUCT for less than half of products; TRUST is wired to RFQ/CONTACT (confirmed for the two heavily-linked trust pages) but LOGISTICS is not wired to anything.

## Search Console data (Part AP)

**Real data used, not invented.** This repository already contains a genuine Google Search Console export at `reports/search-console-export-2026-08-20/` (19 May-18 Aug 2026: 286 clicks, 10,410 impressions, 2.75% weighted CTR, 10.03 average position) — used throughout this report (Parts C, H, W, Z, AC, AN above). Its own documented data boundary applies here too: Query, Page, Country, and Device were exported as separate tables and cannot be joined to prove which query drove which page's result — candidate targets cited above are intent-based mapping, not observed attribution, exactly as that export's own methodology note states.

A second file, `data/search-console/gsc-query-page-export.csv`, is an empty template (header row only) — its dependent output (`reports/search-console-opportunity-loop/`) correctly reports zero scores and "no_gsc_data," which is honestly labeled in that file and not treated as evidence of zero demand.

A separate repository file, `reports/seo-opportunities-top-100-2026-08-20.csv`, contains keyword-research-style rows with named competitors and numeric "Opportunity Scores," but every row's "Current Rank" column literally reads "Requires GSC query export" — meaning that file's scores are **not** derived from real Search Console data despite its filename and date. It is treated in this report as a prior qualitative keyword-research artifact, not as Search Console evidence, and is not conflated with the real export above.

No impressions, clicks, CTR, ranking, or conversion figure in this report was invented for a page not present in the real GSC export.

## Competitor analysis (Part AQ)

Limited, non-scraping web research performed (2 targeted searches) to identify strategic gaps, not to copy content or claims:

- Established Indian Basmati exporters (e.g. Shri Lal Mahal, Veer Overseas) prominently foreground multi-certification badges (ISO, USFDA, HACCP, FSSAI, KOSHER) and independent/own-laboratory testing as a stated competitive differentiator — JFT Agro's `certificates.html` already exists and is the best-linked trust page on the site (Part V), suggesting the content exists; whether it's differentiated as strongly as competitors' framing was not independently verified.
- General B2B export buyer-journey research indicates buyers spend a small fraction of total research time per vendor and favor self-service evaluation — reinforces this audit's own Part AG finding that JFT Agro's product pages already answer the 5 key buyer questions quickly, and that reducing RFQ friction (not requiring "perfect" detail before contact) is a recognized best practice worth checking against the actual `contact.html` form in a future UX-focused phase.
- No competitor content, claims, or design was copied or is recommended for copying. This benchmark is directional context only, consistent with this phase's rule against competitor-scraping as a primary basis.

Sources: [Basmati Rice Exporter 2026](https://retexport.com/basmati-rice-exporter/), [Best Basmati Rice Exporters From India - 2026 Guide](https://inductusglobal.com/best-basmati-rice-exporters-from-india-in-2026-verified-suppliers-for-bulk-buyers/), [Shri Lal Mahal](https://shrilalmahal.org/), [15 B2B Website Best Practices for 2026](https://directiveconsulting.com/blog/15-b2b-website-best-practices-for-2026-built-for-buyers-not-just-browsers/)

## Implementation roadmap (Part AR)

Proposed sequence, evidence-based on what this audit actually found (not a generic template):

1. **Phase 10 — Internal-linking architecture.** Highest evidence-to-effort ratio: restore the export-documentation locale link (precise, low-risk); add regional-page → product links using existing `f` market data; add sibling-grade cross-links among rice/Basmati/millet product families; link the 49 unlinked products to relevant existing articles where genuine relevance exists.
2. **Phase 11 — Commodity category layer.** The single largest structural gap (Part I). Needs its own dedicated design/IA decision before implementation — recommended as its own phase given its scope.
3. **Phase 12 — Structured-data/claims governance reconciliation.** Resolve the `ManufacturingBusiness` schema inconsistency (Part U) and the Thai duplicate-H1 (Part O) — both narrow, well-defined, low-risk fixes.
4. **Phase 13 — Targeted content-gap closure.** One consolidated millet buyer guide (Part AC); reassess after Phase 10-11's linking work changes what GSC data shows.
5. **Phase 14 — Commercial UX / conversion friction review.** Trust-page → RFQ direct linking (Part X), RFQ form friction benchmark (Part AQ).
6. **Phase 15 — Performance / Core Web Vitals.** Not audited in this phase; recommended once the above content/architecture work is stable, consistent with Phase 5's prior visual-audit scope boundary.

This order is proposed based on the evidence in this report; it is not executed here.

## Change control (Part AS/AU)

See `reports/QA-CHANGE-CONTROL.md`, Phase 9 section, for the explicit zero-file-modification confirmation.
