# Phase 10 — Commodity Architecture + Internal Linking + Governance Fixes

Date: 2026-08-27
Status: Implementation complete, full regression suite green, not deployed.

## 1. Executive Summary

Phase 10 delivered all four authorized objectives from the Phase 9 opportunity map: (1) a new 10-page commodity/category architecture, (2) improved contextual internal linking between existing high-value pages, (3) closure of the export-documentation locale link gap, and (4) two confirmed governance defects fixed (locale `infrastructure.html` schema type, Thai duplicate H1). No page was deleted, no URL was migrated, no header navigation was changed, and no unrelated content was rewritten. The full audit suite passes clean (0 findings across all scripts), a byte-for-byte determinism check confirms the generators are stable, and a full comparison against the Phase 9 baseline (1,443 pages) found zero unexplained regressions — the only detected differences are the two authorized governance fixes.

## 2. Scope & Authorized Objectives

Phase 10's mandate was narrow and explicit:

1. Design and implement a proper commodity/category architecture.
2. Improve contextual internal linking between existing high-value pages.
3. Fix the isolated export-documentation contextual-link gap.
4. Correct two confirmed governance defects (ManufacturingBusiness schema; Thai duplicate H1).

Explicitly out of scope: broad SEO rewriting, mass metadata changes, mass content rewriting, a new article program, keyword stuffing, URL migration, page deletion, mass redirects, redesign, or unauthorized changes to the visual design system. Every change below is traced back to one of the four objectives.

## 3. Part A Recap — Architecture Before Phase 10

Investigation (documented in full in `reports/phase10-current-architecture.md`) established the baseline:

- `products.html` filtered all 84 products client-side via a `?cat=` JS parameter; there was no server-rendered, crawlable, linkable category page for any commodity.
- `header.html`'s Products dropdown already listed 10 commodity categories with icons (Rice, Spices, Wheat, Flour & Grains, Pulses, Oilseeds, Herbs & Seeds, Animal Feed, Sugar, and a "Fruits" label mapped to raisins — a pre-existing label mismatch, left untouched as out of scope) but none of these linked anywhere except the filtered `products.html` view.
- Product breadcrumbs were `Home > Products > [Product]` — no category level.
- `header.html`'s internal links are deliberately root-relative without locale prefixes, resolved correctly by the browser regardless of injection context (root or locale page) — this is why English-only category pages could not safely be added to the shared header nav this phase without themselves being localized first (would 404 from locale pages).
- Regional trade pages: `africa-trade.html` and `uae-trade.html` already had 5 `.prod-card` product showcases each; `asia-trade.html` had 5 contextual prose links; `europe-trade.html` had zero — this corrects Phase 9's report, which had claimed all four had zero (a crawler blind spot: Phase 9 searched only for `.prod-card` markup, missing `asia-trade.html`'s prose links).
- The `.jft-document-path` component (linking to `export-documentation.html`) existed on 46 English product pages and 13 English blog/tool pages, but had never been added to any of the 460 locale copies of those 46 products.
- Locale `infrastructure.html` pages carried `"@type":"ManufacturingBusiness"` with no `@id`, contradicting the current English page's `"@type":"Organization"` with `"@id":"https://jftagro.com/#organization"`.
- `th/dill-seeds-powder-exporter.html` had a governed-cache copy-paste bug: 21 occurrences of Celery's Thai name instead of Dill's.

## 4. Commodity Taxonomy Design

The 10 categories map 1:1 onto the taxonomy already implicit in `header.html`'s dropdown and `data/products.json`'s `c` (commodity) field, so no new classification scheme was invented: rice, spices, herbs (labelled "Herbs & Seeds"), oilseeds, feed (labelled "Animal Feed Inputs"), flour (labelled "Flour & Milled Grains"), wheat, sugar, raisins, pulses. Product counts per category were computed directly from `data/products.json`, not estimated: rice 20, spices 17, herbs-seeds 15, animal-feed 15, oilseeds 5, flour 5, pulses 4, wheat 1, sugar 1, raisins 1 — totalling exactly 84.

## 5. Category Page Content & SEO Strategy

Each category page (`scripts/category_content.py`) carries hand-authored, fact-grounded copy: an intro paragraph naming every product in the group, a "selection" section explaining what buyers actually specify for that commodity class (e.g. curcumin content for turmeric, sennoside content for senna, oil content for oilseeds), a markets-note computed from the most frequent `f` (target market) values across the group's products, and — where applicable — links to relevant logistics pages and non-placeholder blog articles. No content was invented that isn't traceable to `data/products.json`.

A first regression pass (`full_site_audit.py`) flagged 6 of the 10 pages for title (30–65 char) or meta-description (90–170 char) length violations — a real defect introduced by this phase's own new pages, not a pre-existing issue. Titles and descriptions for spices, herbs-seeds, oilseeds, animal-feed, flour, pulses, and rice's description were shortened (e.g. spices' title dropped from 66 to 60 chars, animal-feed's description from 173 to 165 chars) while preserving their factual content. Re-running the audit after the fix returned `finding_counts: {}` — confirmed resolved, with all 10 pages regenerated byte-consistently afterward (see §18).

## 6. Locale Strategy for Category Pages (English-Only Deferral)

The 10 category pages are English-only by design, following the established precedent already used for `editorial-policy.html`, `privacy.html`, two logistics pages, and six blog articles (documented in Phase 9): a 2-entry hreflang set (`en` + `x-default`, both self-referencing), no locale directory required. This was a deliberate scope decision, not an oversight — localizing 10 new pages × 10 locales would be a translation-governance undertaking of its own, outside Phase 10's four objectives. `scripts/audit_localizations.py`'s `IGNORED` set was extended with the 10 new filenames so its `missing_pages` check does not false-flag this intentional deferral (see §16 for the regression this required fixing).

## 7. Navigation & Header Decision

`header.html` was deliberately **not modified**. Its Products dropdown links are root-relative and rely on being interpreted relative to whatever page injected them — safe only for pages/paths that exist in every locale. Since the category pages are English-only (§6), adding them to the shared header nav would silently 404 when the header is injected into any of the 10 locale trees. `products.html` was updated instead with an on-page "Browse by Category" section (10 buttons, reusing existing icon classes) placed above the existing JS filter tabs — fully discoverable, zero risk to locale pages.

## 8. Breadcrumb Architecture Changes

All 84 English product pages were updated from `Home > Products > [Product]` to `Home > Products > [Category] > [Product]`, in both the visible nav and the `BreadcrumbList` JSON-LD (position 3 inserted, product renumbered to position 4). `scripts/add_category_breadcrumbs.py` initially assumed `products.json`'s `t` field matched the breadcrumb's rendered product name; this was false for at least one product (`t`: "1121 Golden Sella Basmati" vs. rendered breadcrumb name "Premium 1121 Basmati Rice") and was corrected by extracting the actual name via regex from each file rather than reconstructing it from governed data. Verified: all 84 pages, both visible nav and JSON-LD updated consistently, 0 errors. Locale product breadcrumbs were **not** touched — they retain their existing structure, since retrofitting the category level into 10 locales' worth of breadcrumb translations is outside this phase's four objectives (candidate for a future phase).

## 9. Internal Linking — Commodity Category Layer

- **Inbound to category pages**: 10 links from `products.html`'s new "Browse by Category" section; 84 links from product breadcrumbs (§8); a 9-way cross-link mesh between the 10 category pages themselves (90 links total) via a "related categories" section.
- **Outbound from category pages**: exactly 84 `.prod-card` links across all 10 pages — full 1:1 coverage of every product, each appearing in exactly one category grid — plus filtered links to non-placeholder blog articles and, for rice specifically, the two existing rice logistics pages.
- Full numeric breakdown in `reports/phase10-link-graph-before-after.json`.

## 10. Internal Linking — Export-Documentation Locale Gap

`scripts/fix_export_documentation_locale_links.py` restores the generic variant of the existing `.jft-document-path` component to the 460 locale copies (46 products × 10 locales) that were missing it, using the same governed-cache pattern established in Phases 6–7. Anchor point: immediately before `<div id="footer-placeholder">`, matching the English original's position. Cache entries for the label, body text, and link text were added for all 10 locales in `data/localized-copy-cache.json`. Inbound links to `export-documentation.html` grew from 59 (English only) to 519 (English unchanged + 460 new locale links). Blog/tool locale pages were deliberately left untouched — they never had this component in English either, so adding it to their locale copies would be new content, not a gap fix.

## 11. Internal Linking — Regional Trade Pages

Per the corrected finding in §3, only `europe-trade.html` needed work. Five `.prod-card` links were added (1121 Raw Basmati Rice, Senna Pods, Sunflower Seeds In Shell, Red Millet, Indian Raisins) — each selected because Europe is that product's **primary** documented market in `data/products.json`'s `f` field, not an arbitrary sample. `africa-trade.html`, `asia-trade.html`, and `uae-trade.html` were not modified.

## 12. Internal Linking — Reciprocal Article↔Product Links

`scripts/add_reciprocal_article_links.py` handled three distinct cases found during investigation, each verified individually rather than mechanically applied:

- **7 mismatched links corrected**: existing "Further reading" links that pointed to the wrong article (e.g. four Silky Sortex variants and Samba/PR-11 rice — all non-Basmati — wrongly linked to the Basmati export guide; corrected to the IR-64 or Sri Lanka/Bangladesh export articles as appropriate; Black Cumin corrected from a turmeric article to the cumin/jeera price-outlook article).
- **5 new forward links added** where none existed (yellow maize, maize grits, corn flour, S-30 sugar, toor dal).
- **6 new back-link asides added** to articles, grouped by article to avoid stacking duplicate boxes when multiple products share one article — 14 distinct product links across the 6 asides.
- **2 products deliberately left unchanged** (turmeric-finger, groundnut-oil-cake) — both already had a different, genuinely relevant link; forcing a second link was judged to reduce quality rather than improve it, consistent with "one highly relevant link beats five artificial ones."

A regression this surfaced (`blog-toor-dal-export-india-2026.html` is a placeholder stub in `audit_website.py`'s own `UNPUBLISHED_BLOGS` set) is covered in §16.

## 13. Governance Fix — ManufacturingBusiness Schema

`scripts/fix_infrastructure_schema_type.py` changes `"@type":"ManufacturingBusiness"` to `"@type":"Organization"` and adds `"@id":"https://jftagro.com/#organization"` on all 10 locale `infrastructure.html` files, matching the current English page. This is narrowly scoped: locale infrastructure pages also carry stale, more-specific capacity claims (exact throughput numbers, named machinery brands) that predate a claims-softening edit already applied to the English page — this broader content staleness was identified but **deliberately not touched**, since rewriting it would be content rewriting, outside this phase's authorization. Verified on all 10 files: correct `@type`, correct `@id`, valid JSON.

## 14. Governance Fix — Thai Duplicate H1

Root cause: a governed-cache copy-paste bug, not a rendering defect — `data/localized-copy-cache.json`'s Thai entry for "Dill Seeds & Powder" held Celery's Thai translation. Fixed at the source (cache) and directly in the one affected file, `th/dill-seeds-powder-exporter.html` (21 occurrences: H1, title, breadcrumb, JSON-LD name fields, FAQ text — all corrected consistently in one pass).

## 15. Files Created and Modified

**New scripts** (8): `category_content.py`, `build_category_pages.py`, `add_category_breadcrumbs.py`, `fix_infrastructure_schema_type.py`, `fix_export_documentation_locale_links.py`, `add_reciprocal_article_links.py` (plus the Part A investigation had no script — direct inspection only).

**New pages** (10): `rice-exporter-india.html`, `spices-exporter-india.html`, `herbs-seeds-exporter-india.html`, `oilseeds-exporter-india.html`, `animal-feed-exporter-india.html`, `flour-exporter-india.html`, `wheat-exporter-india.html`, `sugar-exporter-india.html`, `raisins-exporter-india.html`, `pulses-exporter-india.html`.

**Modified — English root** (94 files, verified via `git diff --shortstat`): 84 product pages (breadcrumb category insertion; 7 of these also got corrected further-reading links, 5 also got new forward links), `products.html`, `europe-trade.html`, 2 logistics `index.html` files, and 6 blog articles (new back-link asides).

**Modified — locale** (471 files via Phase 10 scripts specifically): 460 product pages (export-documentation block, 46 × 10 locales), 10 `infrastructure.html` files (schema fix), 1 `th/dill-seeds-powder-exporter.html` (H1 fix). Note: the working tree's total locale diff count is larger than 471 because it also carries forward uncommitted work from Phases 1–9 that predates this phase and was never committed to git — see §21 for how this was disentangled and verified.

**Data/config**: `data/localized-copy-cache.json` (Thai fix + 30 new export-doc-block cache entries across 10 locales), `scripts/audit_localizations.py` (`IGNORED` set extended by 10 filenames), `sitemap.xml` (regenerated, +10 URLs, 0 reordering).

## 16. Regression Audit Suite Results

All audit scripts were re-run against the final state and pass clean:

| Script | Result |
|---|---|
| `audit_locale_ui.py` | pass |
| `audit_website.py` | 0 findings after fix (see below) |
| `audit_commercial_content.py` | pass |
| `audit_claims_and_products.py` | 0 findings |
| `validate_blog_navigation.py` | pass, 0 stale images |
| `audit_localizations.py` | 0 findings after fix (see below) |
| `audit_performance.py` | 0 findings |
| `full_site_audit.py` | 0 findings after fix (see §5) |
| `audit_coverage_gaps.py` | 0 findings |
| `check_links.py` | 0 broken links across 1,766 HTML files |

Two real regressions were found and root-caused during this pass (not suppressed):

1. **`audit_website.py` `LINK_TO_UNPUBLISHED_BLOG`**: the category-page generator and reciprocal-link script both initially linked to `blog-toor-dal-export-india-2026.html`, a literal placeholder stub already in `audit_website.py`'s own `UNPUBLISHED_BLOGS` set. Fixed by extracting that set via regex from `audit_website.py`'s own source in both generators, filtering it out, removing the one already-inserted bad link, and regenerating. Re-run: 0 findings.
2. **`audit_localizations.py` `missing_pages`**: flagged all 10 new English-only category pages against all 10 locales (`{locale}_missing_pages: 10`), since they have no locale copies by design (§6). Fixed by adding the 10 filenames to the existing `IGNORED` set. Re-run: `rc=0`, `finding_counts: {}`, informational cache-self-identical counts unchanged from the established Phase 6–9 baseline (ar:8, es:59, fr:74, id:69, ms:155, pt:52, ru:26, si:99, th:12, vi:40) — confirming zero unintended side effects.

## 17. Browser/Manual Validation & Performance

Ad hoc, per-fix browser verification was performed during implementation (before this report was compiled): the 10 category pages (header/footer injection, product-card navigation, 0 console errors, 0 failed requests, mobile viewport, RTL not applicable since English-only), and the export-documentation locale block on Arabic/Thai/Vietnamese samples (correct translated text, correct href, 0 console errors).

**Disclosure**: no live browser-automation tool was available in this continuation of the session for a final consolidated Part Y pass. In its place, the following static-equivalent verification was run and is a closer proxy for "will this render and execute correctly" than it might first appear: full HTML5 parse validation (`html5lib`, non-strict) and JSON-LD `json.loads` validation across all 10 category pages, all 84 English product pages, a 50-page locale sample, `products.html`, `europe-trade.html`, both modified logistics pages, and all 10 locale `infrastructure.html` files — **0 parse errors, 0 malformed JSON-LD** across all of them — plus `check_links.py`'s 0-broken-link result across the entire 1,766-file site (which would catch a broken asset or href a browser pass would also catch). This does not substitute for an actual rendered-DOM/console check, and that gap is disclosed here rather than papered over.

**Performance** (Part Z): the 10 category pages are lightweight — 11.6KB to 25.4KB each (average 16.8KB), versus 150KB for `products.html`. Every `<img>` tag across all 10 pages has explicit `width`/`height` and `loading="lazy"` (0 exceptions). Zero new external `<script src>` tags and zero new stylesheets — all 10 pages reuse the 3 existing shared CSS files (`jft-design-system.css`, `jft-responsive.css`, `trade-regions.css`), adding no new network requests beyond the product images already served elsewhere on the site.

## 18. Determinism Verification

| Script | Result |
|---|---|
| `build_category_pages.py` | Byte-identical output on 3 separate runs (md5 verified on all 10 files) — fully idempotent. |
| `fix_export_documentation_locale_links.py` | Self-guarding: second run reports "Added 0 new locale pages, Skipped 460 (already present)". |
| `add_reciprocal_article_links.py` | `add_forward_links()`/`add_back_links()` report 0/0 on second run (self-guarding). `fix_mismatched_links()` unconditionally rewrites each time but is a pure function of static data — diff-inspected and confirmed byte-identical output across runs, no drift. |
| `fix_infrastructure_schema_type.py` | Not re-runnable as-is: it is a one-shot migration that raises a clear "expected pattern not found" error on a second run once the target text has already changed. Confirmed via diff inspection that the second (failed) run wrote nothing and caused no corruption — it fails loudly rather than silently double-applying or corrupting. |
| `add_category_breadcrumbs.py` | Same one-shot-migration profile as above: raises "JSON-LD breadcrumb fragment not found" on a second run against already-migrated pages. Confirmed via JSON-LD validity spot-checks on 3 sample pages (including the edge case `toor-dal-split-pigeon-pea-exporter.html`) that no partial/corrupt write occurred. |

The two one-shot scripts are consistent with Phase 10's own constraint to ship narrow, targeted governance fixes rather than general-purpose reusable tooling; their failure mode on re-run is safe (loud error, no write) rather than dangerous (silent double-application).

## 19. Full Crawl Comparison vs. Phase 9 Baseline

All 1,443 pages from `reports/seo-page-inventory-2026-08-27.json` (the Phase 9 baseline) were re-checked against the current file tree for canonical URL, hreflang-alternate count, and schema-type presence:

- **1,443/1,443 files found** (0 missing).
- **10 mismatches, all expected**: the 10 locale `infrastructure.html` pages, each showing `ManufacturingBusiness` present in the baseline but absent now — this is exactly the authorized §13 fix, not a regression.
- **0 unexplained mismatches** across the remaining 1,433 pages.

`full_site_audit.py`'s own scope counters confirm the growth is fully explained: `html_files` 1,753, `indexable_pages` 1,453 (1,443 baseline + 10 new category pages). `generate_sitemap.py` grew the sitemap from 1,443 to 1,453 URLs with `git diff --stat` showing 80 insertions and 0 deletions — no reordering, no unrelated churn.

## 20. Cloudflare Build, Git Diff Discipline, Deferred Items & Success Criteria

**Cloudflare build**: `scripts/build_cloudflare_assets.py` ran clean, producing 2,099 public assets (135.5 MiB) in `.cloudflare-dist-next/` (gitignored, not deployed). All 10 new category pages are present in the output; the required/forbidden-file assertions built into the script passed (no `scripts/`, `reports/`, or credential files leaked into the public bundle; only the existing allowlisted `data/*.json` files are present). **Not deployed.**

**Git diff discipline**: the working tree carries substantial uncommitted content from Phases 1–9 that was never committed (visible as ~1,040 total modified files in `git status`). Phase 10's own contribution was isolated by cross-referencing against the explicit action log kept during implementation: 94 modified English-root HTML files (exactly accounted for: 84 products + 6 blog back-links + `products.html` + `europe-trade.html` + 2 logistics pages) and 471 locale files via Phase 10 scripts specifically (460 export-doc + 10 infra-schema + 1 Thai fix). Sample diff inspection (e.g. `ar/coriander-seeds-exporter.html`) confirms Phase 10's own edit is a small, correctly-anchored, isolated insertion that neither touches nor is confused with the pre-existing Phase 6–8 content already sitting uncommitted in that same file.

**Deferred / explicitly out of scope** (documented, not silently dropped): locale product breadcrumbs do not yet carry the category level (§8); the pre-existing "Fruits→raisins" header label mismatch was not corrected; locale `infrastructure.html` pages' stale capacity/brand claims beyond the schema `@type` were not rewritten (§13); the 10 category pages are not localized (§6); a live browser-automation pass could not be re-run in this session (§17, disclosed rather than fabricated).

**Success criteria**: all four authorized objectives delivered; no page deleted; no URL migrated; no mass redirect; header nav unchanged; full audit suite green; determinism verified (with the one-shot-script caveat documented in §18); full crawl comparison shows zero unexplained regressions; Cloudflare build verified, not deployed. `reports/QA-CHANGE-CONTROL.md` has been updated with a Phase 10 section (see separate diff).

**STOP.** Per Phase 10's explicit instruction, this concludes the phase. Phase 11 has not begun and will not begin without a new, separate authorization.
