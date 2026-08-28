# Phase 4 — Locale Redirect Canonicals & Internal-Link Coverage

**Baseline:** Phase 1 `e64a3f2b` + Phase 2/3 (uncommitted working-tree changes).
**Scope:** (A) fix 90 locale redirect-stub canonicals, (B) restore internal-link coverage for 36 pages. No redesign, no product/content/translation changes beyond what's documented below.

---

## Part A — 90 locale redirect stub canonicals: FIXED

### A1 — Identification

All 90 pages were pulled directly from `reports/technical-crawl-2026-08-26.json`'s `canonical_points_to_redirect` list (not reconstructed from memory). Confirmed count: 90, spanning all 10 locales, 9 unique English source articles.

### A2 — Studied the correct English pattern

English legacy-redirect stubs (e.g. `blog-cif-fob-explained.html`) already implement:
```html
<meta name="robots" content="noindex,follow">
<meta http-equiv="refresh" content="0;url=blog-bill-of-lading-explained-importers.html">
<link rel="canonical" href="https://jftagro.com/blog-bill-of-lading-explained-importers.html">
```
Canonical = the absolute URL of wherever the redirect actually points. This is the pattern the fix replicates exactly.

### A3/A4 — The fix and an important side-finding

For every one of the 90 stubs, the redirect's `content="0;url=..."` target was resolved exactly as a browser would (relative to that file's own directory), and the canonical `href` was rewritten to that resolved absolute URL — **nothing else on any of the 90 pages was touched** (verified: each diff is exactly 1 line).

**Side finding, not fixed (per Step A3's explicit "canonical only" scope):** resolving each redirect's actual target revealed that **all 90** locale redirects point to the **English-language** replacement article, not a locale-specific one (e.g. `ar/blog-cif-fob-explained.html`'s redirect target resolves to `blog-bill-of-lading-explained-importers.html` at the root, not `ar/blog-bill-of-lading-explained-importers.html` — even though an Arabic version of that destination exists). The canonical fix mirrors this faithfully (pointing to the same English destination the redirect already uses), so canonical and redirect are now internally consistent — but a locale visitor hitting one of these 90 old URLs is still dropped into an English article. This is a distinct, real content-routing question or possibly deliberate consolidation choice (worth a human confirmation) — genuinely out of Part A's authorized scope ("do not change redirect destination... unless investigation proves it is also defective," and this needs a decision, not just a mechanical fix), so it was left untouched and is flagged here for a future phase.

### Validation

| Check | Result |
|---|---|
| All 90 canonicals now match their redirect's actual resolved target | Confirmed programmatically, 0 mismatches |
| HTML validity (html5lib) on all 90 files | Valid |
| Diff scope | Exactly 90 files, 1 line changed each |
| Re-crawl: `canonical_points_to_redirect` finding | 90 → **0** |
| Re-crawl: `duplicate_canonical_target` | 6 → 9 (expected increase — see below) |

The 9 "duplicate canonical target" entries after the fix are the **correct, intended** consolidation pattern: each destination article now shares its canonical with every locale (and English, where applicable) redirect stub that points to it — exactly matching the one English case that was already correct before this phase. Inspected all 9; none are a defect.

---

## Part B — 36-page internal-link coverage: investigated, no code change needed

### B1/B2 — Structural comparison

Compared homepage section structure (`id`-tagged containers) between the 4 rebuilt homepages (ar/es/fr/ru) and the 6 older ones (id/ms/pt/si/th/vi). The real difference is **much larger than the 36 missing links**: the 4 rebuilt homepages carry an entire additional UI layer — a Google Translate widget, scroll-progress bar, live forex-rate ticker, a full mobile-nav accordion system, a nav overlay, a cookie-consent bar, a quick-quote widget, and an RFQ-status widget — none of which exist on the 6 older homepages (which instead have a `preloader` element the other 4 lack). I flagged this to the user before proceeding, since replicating all of it would be a large, high-risk change bordering on a redesign/new-feature addition, contrary to this phase's own rules. **Directed to scope this narrowly: fix only what's needed to resolve the 36-page link-coverage finding, not full feature parity.**

### B3 — Investigating the narrow fix uncovered the finding was already resolved

Before writing any content, I traced exactly which HTML element the 6 missing links belong to on `ar/index.html`: a "Tools" (`href="faq.html"`, `packing-calculator.html`, etc.) menu that lives in the **shared, universal `header.html`** fragment — not in `ar/index.html`'s own markup. `header.html` is fetched via JavaScript and injected into `#header-placeholder` on **every single page of the site**, using plain relative hrefs (`href="faq.html"`), which a real browser resolves against the *current page's own URL* — meaning on `id/index.html` the exact same shared markup already resolves to `id/faq.html`.

I verified this directly rather than assuming it: loaded `id/index.html` in a real headless browser (against a local HTTP server, so the header's `fetch()` call behaves as in production) and read the live DOM's resolved `href` values for the three most telling of the six pages:

```
faq.html              -> http://.../id/faq.html   (correctly locale-scoped)
packing-calculator.html -> http://.../id/packing-calculator.html
whatsapp-catalog.html -> http://.../id/whatsapp-catalog.html
```

**All 6 pages, on all 10 locales, are already reachable through the universal header navigation.** The Phase 3 "36 accidental orphans" finding was a **static-crawl methodology limitation** — already flagged explicitly in Phase 3's own report (Section 8: "a static crawl... cannot see links that exist only inside these two shared fragments") — not a real, user-facing content or architecture gap.

**Action taken:** I initially wrote and applied a small supplementary "Tools" quick-links block to the 6 homepages (reusing the site's existing `.case-links` CSS and exclusively governed, already-approved cache translations — no new translation was invented). After the browser verification above proved the links were already live and working, I reverted this change: adding it would have meant a third/fourth copy of navigation that already exists and works, which conflicts with this phase's own Step B6 ("do not repeat the same link unnecessarily") and Absolute Rule 7 ("do not create artificial SEO links"). **No file was changed for Part B.**

### Link coverage (36 pages) — final status

| Page (× 6 locales: id, ms, pt, si, th, vi) | Discovery path |
|---|---|
| `export-documentation.html`, `faq.html`, `packing-calculator.html`, `port-transit-calculator.html`, `product-catalogue.html`, `whatsapp-catalog.html` | Already reachable via the shared header's "Tools" dropdown menu on every page (verified live, all 6 locales) |

`legal.html` (the one English-locale orphan from Phase 3) is the same story: reachable via the shared `footer.html`'s "Legal" link, universal on every page — already correctly classified as a "legitimate orphan" in Phase 3.

---

## Localization — confirmed clean

- No English leakage introduced: not applicable, since no locale content was changed.
- No machine translation used: the (reverted) Tools block used only pre-existing, human-reviewed cache entries (`Tools`, `Documentation Center`, `Trade FAQ`, `Packing Calculator`, `Port Transit Time`, `PDF Brochure & Catalogue`, `WhatsApp Catalog` — all 6 locales, all already in `data/localized-copy-cache.json` from earlier work) — moot since the change was reverted, but confirms the governed-translation path was followed correctly while it was in place.
- No translation corrupted: the 90 canonical-only edits never touch visible text, `lang`, `dir`, or any translated string.

## SEO safety — confirmed for all 90 modified pages

| Check | Result |
|---|---|
| Canonical | Now resolves to the article the redirect actually serves (was self-referencing) |
| Hreflang | Unchanged — 0 findings before and after |
| Robots | Unchanged (`noindex,follow` preserved on all 90) |
| Sitemap | Unchanged — these are non-indexable redirect stubs, never in the sitemap |
| Title / meta description | Unchanged |
| Schema | Unchanged (none of these stub pages carry JSON-LD) |
| OpenGraph | Unchanged |

## Browser testing (Part E) — actually tested, not assumed

Loaded all 10 non-English locale homepages plus English in a real headless browser against a local HTTP server. For each: HTTP status, `lang`/`dir` attributes, header/footer presence, nav and footer link counts, product-card count, language-selector presence, and full console/page-error/failed-request capture.

**Result — all 11 homepages: HTTP 200, correct `lang` (and `dir="rtl"` for Arabic only), header and footer present, 81-82 nav links, 26 footer links, 11 product cards, 0 console errors, 0 page errors, 0 failed resource requests.**

## Full technical crawl re-run (Part F)

| Metric | Before (Phase 3) | After (Phase 4) |
|---|---|---|
| `canonical_points_to_redirect` | 90 | **0** |
| `duplicate_canonical_target` | 6 | 9 (expected — see Part A validation) |
| `accidental_orphan_candidate` | 37 | 37 (unchanged — confirmed already-correct, no fix needed) |
| Crawl depth / unreachable-via-static-crawl counts | unchanged | unchanged (same reason) |
| Hreflang findings | 0 | 0 |
| Broken internal links (`check_links.py`) | 0 | 0 |

## Audits (Part D)

| Audit | Result |
|---|---|
| `audit_locale_ui.py` (Phase 2) | PASS, 0 findings |
| `audit_website.py` | PASS, 0 findings |
| `audit_commercial_content.py` | PASS, 0 findings |
| `audit_claims_and_products.py` | PASS, 0 findings |
| `validate_blog_navigation.py` | PASS, 0 findings |
| `audit_localizations.py` | PASS, 0 findings |
| `audit_performance.py` | PASS, 0 findings |
| `full_site_audit.py` | PASS, 0 findings |
| `audit_coverage_gaps.py` | PASS, 0 findings |
| `check_links.py` | PASS, 0 broken links (1,756 files) |

## Cloudflare build

`scripts/build_cloudflare_assets.py`: succeeded, 2,089 files (matches baseline), `locale-ui.js` byte-identical (MD5 unchanged from Phase 2/3). No scripts/reports/internal files leaked. Build artifact deleted after inspection. **Not deployed.**

## Files changed this phase

| File | Reason |
|---|---|
| 90 locale redirect-stub `.html` files (listed in `reports/locale-architecture-fix-2026-08-26.json`) | Canonical corrected to point to the redirect's actual destination, per Part A |
| `reports/locale-architecture-fix-2026-08-26.md` / `.json` | This report |

No homepage, no locale content, no product data, no translations, no CSS, no unrelated JS, no Cloudflare config was changed.
