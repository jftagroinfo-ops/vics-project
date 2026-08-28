# Phase 25 — AEO/GEO/LLMO/AI Search Authority Implementation

Date: 2026-08-28
Status: Investigation complete. Two evidence-backed fixes implemented and verified clean; several candidates investigated and correctly deferred with explicit reasoning. **Net website change: 5 new legacy-URL redirects in `.cloudflare/worker.js`, 5 article→category-hub links added, 1 new governed script.**

## 1. Baseline (compared against Phase 24's ending state)

| Item | Value | vs. Phase 24 |
|---|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` | Unchanged |
| Production | `HTTP 200`, sitemap 1,453 URLs | EXPECTED (no deploy between phases) |
| Renderable pages | 1,753 | Unchanged |
| Product schema count | 1 (`product-page-template.html` only — the unused generator template, already documented in Phase 23's `check_unused.py` findings) | EXPECTED, not a regression — 0/84 real product pages, matching Phase 24's confirmed-correct end state |
| `legalName` presence | Confirmed present on sampled root + 2 locale directories | EXPECTED, matches Phase 24's fix |
| `FAQPage` schema count | 86 files | EXPECTED |

No regression found. No unexpected difference found.

## 2. Methodology

Phase 24 already covered entity/E-E-A-T/product-depth/basic AI-query-testing. Phase 25 goes one layer deeper into content architecture that Phase 24 did not audit: whether the 10 category pages function as genuine topic-authority hubs, whether the 37 articles demonstrate real expertise and connect back to the category structure, and whether the buyer-question universe is actually covered. The two large mechanical audits (10 category pages, 37 articles) were delegated to a research agent; I handled expanded AI query testing, a specific investigation triggered by an anomaly in the query results, and implementation directly.

## 3. A Critical Discovery: The Root Cause of Phase 24's "AI Misinformation" Finding

Phase 24 found that an AI-search summary fabricated "Since 1980" and an incorrect page title for JFT. This phase's expanded query testing found the actual, evidence-backed explanation, upgrading that finding from "unexplained external hallucination" to "traceable to a specific, fixable gap."

Testing `"JFT AGRO OVERSEAS LLP"` and `site:jftagro.com` returned search results listing **six page titles from the site's pre-migration WordPress structure**: `About Us - JFT AGRO OVERSEAS LLP` at `/aboutus/`, `PRODUCTS - JFT AGRO OVERSEAS LLP` at `/products/`, `SPICES - JFT AGRO OVERSEAS LLP` at `/spices/`, `RAISINS - JFT AGRO OVERSEAS LLP` at `/raisins/`, `Contact Us - JFT AGRO OVERSEAS LLP` at `/contact-us/`, and `RICE MILL - JFT AGRO OVERSEAS LLP` at `/ricemill/`. These are almost certainly where AI/search systems' training and index data picked up outdated facts like "Since 1980" — a plausible claim on an old WordPress about-page, but one the current, more careful `about.html` deliberately does not make (it states a specific, verifiable 2016 registration with an explicit predecessor-history caveat).

**Verified directly against live production** (not assumed): `/products/` correctly returns `200` (redirects to `/products.html` via the existing `LEGACY_PRETTY_REDIRECTS` map in `.cloudflare/worker.js`). The other five — `/aboutus/`, `/spices/`, `/raisins/`, `/contact-us/`, `/ricemill/` — all returned a bare `404`. This is not a live-content-leak problem (no stale content is actually served), but a **404 tells a crawler "gone," while a 301 tells it "moved to X, update your reference."** Leaving these as bare 404s means Google/AI re-crawls have no signal pointing them to the corrected, current page — the stale index entries can only decay slowly rather than being actively corrected.

**This is Part 13's exact mandate** ("Investigate important facts that AI systems could misinterpret... Improve the authoritative source instead") **with concrete, evidenced root cause** — not a hypothesis.

## 4. Fix 1 (Implemented) — Legacy URL Redirects in `worker.js`

Extended the site's own existing, already-proven `LEGACY_PRETTY_REDIRECTS` mechanism (the same pattern already correctly handling `/products/`, `/blog/`, and 18 other legacy paths) with 5 new entries, each verified against a real, still-indexed legacy URL and mapped to its accurate modern equivalent:

| Legacy URL | Redirect target | Rationale |
|---|---|---|
| `/aboutus/` | `/about.html` | Direct modern equivalent, confirmed to exist |
| `/contact-us/` | `/contact.html` | Direct modern equivalent, confirmed to exist |
| `/raisins/` | `/indian-raisins-kishmish-exporter.html` | Consistent with the existing `LEGACY_PRODUCT_ALIASES["raisins"]` mapping already in the same file, targeting the same product page |
| `/ricemill/` | `/infrastructure.html` | Consistent with the existing `"/the-basic-processes-of-rice-milling/": "/infrastructure.html"` precedent in the same file |
| `/spices/` | `/spices-exporter-india.html` | Modern category-hub equivalent of the old WordPress spice category archive |

**This is the first modification to `.cloudflare/worker.js` in the entire engagement** (Phases 17-24 all left it untouched). Given its significance, verification was handled carefully: all 5 target files were confirmed to exist before writing the redirect; the edit was a minimal, template-following insertion (5 lines, alphabetically ordered, matching the exact existing key/value syntax of the other 20 entries); and the result was visually re-read in full to confirm correctness. **Disclosed limitation**: this session's automated `node`/Python syntax-check execution against this specific file was blocked by the session's own permission classifier (an environment restriction, not a finding about the file) — verification therefore relied on precise `Read`-based inspection and a text-pattern structural check (`grep`-counted key-value pairs) rather than an executed syntax check. **This change was not deployed** — per Phase 25's explicit instruction, production deployment requires separate authorization; the fix exists locally, ready for the next authorized deployment.

## 5. Fix 2 (Implemented) — Article → Category-Hub Links

The delegated article audit (§8) confirmed a real structural gap: **0 of 30 substantive articles link to any of the 10 category hub pages** — the category→article link direction (confirmed present via each category's "Related Buyer Guides" section) was entirely one-way. This directly matches Part 15's "Article → Category → Product → RFQ" semantic-graph objective.

Investigated the site's existing patterns before implementing: found a single, already-governed, reusable component — `<aside class="jft-related-product">` — used on exactly 6 of the 37 articles. For these 6, determined each article's implied category from the **products it already links to** (using each product's own existing, human-verified category link — no new categorization judgment was invented). Result: 5 of the 6 articles link to products from a single, unambiguous category; 1 (`blog-top-indian-agro-commodities-import-2026.html`) references products spanning two categories (Animal Feed and Oilseeds) and was **correctly left unmodified** rather than forcing an arbitrary single-category link that would misrepresent the article's actual multi-commodity scope.

Implemented `scripts/add_article_category_links.py`: appends a small, style-matched `Category: <link>` addition to the existing aside for the 5 unambiguous articles. Verified idempotent (second run: 0 added, 5 already present, 1 correctly still skipped as ambiguous, 31 correctly skipped as lacking the aside component).

**Scope note, explicitly not overreached**: 31 of the 37 articles do not use this reusable aside at all — 18 of those still link to products via ad-hoc inline links in varying templates, and 12 (mostly generic trade-mechanics topics: APEDA registration, bill of lading, letters of credit, proforma invoices, container-loading checklists) have zero product links at all. Extending category-linking to these would require either standardizing the "related products" presentation across differently-structured articles first (a template-design decision, not a mechanical fix) or, for the 12 generic articles, deciding whether forcing any single-category link would even have genuine semantic value (Part 15 explicitly warns against links added merely to increase count) — for cross-cutting logistics/documentation topics that genuinely span all commodities, a category link would likely be arbitrary rather than meaningful. **Documented as a future opportunity, not implemented this phase.**

## 6. Investigated and Correctly NOT Changed — Certificate Number Disclosure

The "how to verify an Indian commodity exporter" query test (§9) surfaced that real buyers specifically look for published IEC codes, GST numbers, and NABL-lab COA references. Checked whether JFT's site exposes these: `about.html` displays trust *badges* ("IEC Holder," "APEDA Registered") and `certificates.html` explicitly discloses certificate *types* and issuers — but the certificate **numbers** are marked `"Not published"` with an explicit note: *"Buyers can request the stamped copy and scope for verification"* plus a `Request` CTA.

**This is not a gap — it is a deliberate, already-good anti-fraud/anti-scraping design** (publishing exact government registration numbers publicly is a plausible impersonation/competitive-intelligence risk; gating them behind a genuine buyer inquiry is a defensible, common B2B practice). This phase's testing **validates** this existing decision rather than finding a defect. No change made or recommended.

## 7. Buyer Question Map (Part 7)

| Category | Sample questions | Status |
|---|---|---|
| Product | What is it? Grades? Specs? Packaging? | **COVERED** — 84/84 products (Phase 24 finding, reconfirmed) |
| Quality | How is quality checked? What parameters? Inspection? | **COVERED** — FAQ answers cite COA/inspection reports; `blog-sgs-inspection-indian-agro-exports.html` and `blog-certificate-of-analysis-food-imports.html` provide dedicated depth |
| Commercial | Quotation? Sample? What information needed? | **COVERED** — 84/84 RFQ + sample-request links; `contact.html` form |
| Logistics | Export documentation? Ports? | **COVERED** — `export-documentation.html`, `port-transit-calculator.html`, HS codes/container-load figures in every product FAQ |
| Logistics | How is cargo shipped (packing/loading mechanics)? | **PARTIALLY COVERED** — container-load math exists in FAQ, but no single dedicated "how shipping works" page; judged non-critical given the calculator + FAQ combination already answers the commercially relevant part (how much fits, what it costs to move) |
| Risk | How can I verify a supplier? | **COVERED**, and more thoughtfully than initially apparent (§6) |
| Geography | Which countries/regions? | **COVERED** — `asia-trade.html`, `africa-trade.html`, `europe-trade.html` |

**Overall: buyer-question coverage is already strong.** No new page or major content addition was justified by this map — the one partial gap (detailed shipping mechanics) does not meet the "new-page threshold" (Part 8): existing pages already answer the commercially meaningful part of the question.

## 8. Category Hub Audit (Part 6, delegated)

All 10 category pages share one consistent template (definition → product grid → buyer-subtopic paragraph → related guides → CTA). **7 of 10** are STRONG or ADEQUATE hubs with genuine buyer-subtopic depth and 1-4 supporting articles each. **3 of 10 — Wheat, Sugar, Raisins — are THIN**: each is a single-SKU category (matching real catalog breadth, not an error) with brief prose and, for Wheat and Raisins, **zero supporting articles**. **None of the 10 category pages has any FAQ content or `FAQPage` schema** (confirmed via direct grep, 0/10) — a consistent, sitewide pattern rather than an isolated gap.

**Disposition: documented, not implemented this phase.** Improving the 3 thin categories or adding category-level FAQ requires genuine content authorship (writing real, non-generic buyer Q&A specific to wheat/sugar/raisins trade) rather than a structural/technical fix — this exceeds a single phase's "smallest safe change" standard and risks exactly the "mass-FAQ-creation" and "generic AI filler" outcomes Phase 25 explicitly warns against. Flagged as a well-scoped candidate for a future, dedicated content-authoring phase.

## 9. Article Authority Audit (Part 14, delegated)

37 `blog-*.html` files: 6 are legitimate redirect-consolidation stubs (`noindex,follow`), leaving 30 substantive articles. All 30 have clear buyer-question purpose and correct `Article` schema (`datePublished`/`dateModified`/organizational author). ~22/30 demonstrate genuinely specific expertise (HS codes, dated regulatory/price figures, named certifying bodies); ~8/30 read more generically. 18/30 link to at least one product; 12/30 have zero product links (concentrated in generic trade-mechanics topics). **One article, `blog-toor-dal-export-india-2026.html`, is an unpublished placeholder** (`noindex`, body text literally reading "Placeholder article — create full content as needed") — a real, if `noindex`-contained (not live-search-facing), content gap for a category (Pulses) that otherwise has full product-page coverage via `toor-dal-split-pigeon-pea-exporter.html`.

**Disposition: documented, not implemented this phase.** Writing genuine, evidence-backed article content is content authorship, not a structural fix — flagged as a specific, ready-to-scope candidate for a future content phase (the product page already provides the factual base to draw from honestly).

## 10. Expanded AI Query Testing (Part 22)

Tool used: the single web-search tool available this session — **explicitly not** Google AI Overviews, Bing Copilot, ChatGPT search, Perplexity, or Gemini, none of which were independently testable.

| # | Query | Type | JFT appears? | Notes |
|---|---|---|---|---|
| 1 | `"JFT AGRO OVERSEAS LLP"` | Brand | Yes | Surfaced the legacy-URL evidence in §3; also a genuine third-party LEI registry listing (`globallei.in`) confirming real legal registration |
| 2 | `"JFT Agro Overseas" rice exporter India` | Brand | Yes | Same misinformation pattern as Phase 24, now root-caused |
| 3 | `site:jftagro.com` | Trust/coverage | Yes | Confirmed same legacy URLs, no new ones found |
| 4 | `IR64 rice exporter India` | Product | No | Competitors: Riceone, Plowexim, Tizara Group |
| 5 | `Indian rice exporters IR64 rice exporter India` | Product | No | Same competitors (Phase 24 repeat, consistent) |
| 6 | `annatto seed exporter India` | Product | No (correct) | JFT does not sell annatto seeds |
| 7 | `Indian spice exporter turmeric cumin coriander bulk` | Category | No | Competitors: Botanika Bharat LLP, White Feather Export |
| 8 | `Indian pulses exporter bulk` | Category | No | Competitors: Damodar Exports, S A Enterprises, Leela Sai Exim |
| 9 | `bulk rice supplier India request quotation` | Commercial | No | Competitors: Indiafeast, Grainville |
| 10 | `how to verify an Indian commodity exporter` | Trust | No (JFT not named) | Yielded the genuinely useful verification-criteria evidence used in §6 |

**Pattern unchanged and now better understood**: JFT appears reliably only for its own exact brand name (where a fixable, root-caused legacy-URL issue currently degrades accuracy — addressed in §4); it does not appear for any tested generic/category/commercial query, consistent with Phase 24's finding of an off-site authority gap rather than an on-page technical one.

## 11. Competitive Comparison (Part 21, light, from the same query evidence)

No new competitor content was fetched or copied. The additional pulses-category competitors found this phase (Damodar Exports, S A Enterprises, Leela Sai Exim) follow the same pattern already noted in Phase 24 for rice/spice competitors — generic differentiator claims ("ethical sourcing," "bulk order support") without the specific figure-level detail JFT's own FAQ content already provides. No competitor-only capability was identified that JFT lacks and should adopt.

## 12. `llms.txt`, robots.txt, Product Schema (Parts 17-19)

No new evidence emerged this phase to revisit any of Phase 22's/24's decisions: `llms.txt` remains correctly absent (Part 19 explicitly instructs re-evaluating "only if new evidence has emerged" — none did); `robots.txt` remains correctly unrestricted for AI crawlers; **Product schema was not reintroduced** on any product page, per Phase 24's now-documented governance rule and this phase's own explicit instruction not to.

## 13. Fix Decision Gate Applied to All Candidates

| Candidate | Gate result |
|---|---|
| Legacy URL redirects (`/aboutus/`, `/contact-us/`, `/raisins/`, `/ricemill/`, `/spices/`) | **Passes all 7 conditions** — real observed gap (confirmed indexed URLs), specific pages, root cause traced to Phase 24's misinformation finding, clear GEO benefit, evidence-backed solution (existing, proven redirect mechanism), low risk (additive map entries only), measurable (production HTTP-status re-check after deployment) |
| Article→category links (5 articles) | **Passes** — real observed gap (0/30 confirmed), specific pages, root cause (one-way linking), clear LLMO/semantic-graph benefit, evidence-backed (used each article's own existing product links, no invented categorization), low risk (additive, idempotent), measurable (regression suite + visual check) |
| Thin category hubs (Wheat/Sugar/Raisins) | **Fails "sufficient first-party expertise readily codifiable without new authorship"** — requires genuine content writing, not a structural fix |
| Toor dal placeholder article | **Fails the same condition** — requires genuine content authorship |
| 12 generic articles' missing category links | **Fails "clear semantic value"** — a forced single-category link on a cross-cutting logistics topic would not accurately represent the content |
| Certificate number disclosure | **Fails "genuine observed gap"** — investigated and found to be a deliberate, correct existing design, not a gap |

## 14. Regression Results

| Script | Result |
|---|---|
| `audit_website.py` | 0 findings, 1,753 pages |
| `full_site_audit.py` | 0 findings, 1,453 indexable |
| `audit_commercial_content.py` | 0 findings |
| `audit_claims_and_products.py` | 0 findings |
| `validate_blog_navigation.py` | Passed — 259 blog cards, 66 legacy redirects, 0 stale images (confirms the 5 article edits did not break blog-navigation validation) |
| `audit_locale_ui.py` | 0 findings, determinism PASS |
| `audit_localizations.py` | 0 findings |
| `audit_coverage_gaps.py` | 0 findings |
| `audit_performance.py` | 0 findings |
| `check_links.py` | 0 broken links / 1,766 files |
| `validate_seo_alignment.py` | Exit 1 — identical pre-existing finding (`P23-R4`), unrelated to and unaffected by this phase |

Page counts, sitemap URL count, and indexable-page count unchanged. `git status` before/after this phase's work: scoped exactly to the 2 fix files (`.cloudflare/worker.js`, 5 article files), 1 new script, and this report pair — no unexplained drift. One stray leftover temporary file from Phase 20 (`p20_final_audits.txt`) was found during cleanup and removed as housekeeping (not a Phase 25 change).

## 15. Changes Implemented

| File(s) | Change |
|---|---|
| `.cloudflare/worker.js` | Added 5 entries to the existing `LEGACY_PRETTY_REDIRECTS` map (`/aboutus/`, `/contact-us/`, `/raisins/`, `/ricemill/`, `/spices/`) |
| 5 article files (`blog-basmati-export-guide.html`, `blog-cumin-jeera-price-outlook-2026.html`, `blog-groundnut-peanut-export-india-2026.html`, `blog-india-rice-export-sri-lanka-bangladesh.html`, `blog-ir64-export.html`) | Added a category-hub link to each article's existing "Related product" aside |
| `scripts/add_article_category_links.py` (new) | Governed, deterministic, idempotent script implementing the above |

## 16. Changes NOT Made, and Why

See §13's Fix Decision Gate table for the specific reasoning on each deferred candidate (thin category hubs, toor dal placeholder, 12 generic articles, certificate numbers).

## 17. Remaining Opportunities (documented, not implemented)

1. Deploy the `worker.js` redirect fix to production (requires separate explicit authorization per Phase 25's own deployment rule) — this is the step that actually starts correcting the stale search-index entries driving Phase 24's misinformation finding.
2. A future, dedicated content-authoring phase to: write the toor-dal article, add light buyer-subtopic depth to the 3 thin category hubs, and decide whether category-level FAQ is warranted.
3. Standardize the "related products" presentation across the 31 articles currently lacking the reusable `jft-related-product` aside, which would then make category-linking mechanically extensible to all of them.
4. Continue monitoring off-site/generic-query visibility — unchanged from Phase 24, still a strategic (non-technical) gap.

## 18. Limitations

Identical to Phase 24's disclosed limitations (no live browser automation; AI query testing scoped to one general search tool, not the specific named AI systems; no backlink/off-site-authority data available). Additionally this phase: `worker.js`'s edit could not be verified via an executed syntax check due to a session permission-classifier restriction on this specific file — verification relied on precise manual inspection and text-pattern structural checks instead, disclosed rather than glossed over.

## 19. Stop

Per Phase 25's explicit instruction: **PHASE 25 COMPLETE — STOPPING FOR AUTHORIZATION.**
