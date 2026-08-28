# Phase 29 — Targeted Visual UX Polish & Template Consistency

Date: 2026-08-28
Status: Investigation complete; 2 of 4 issues fixed with confirmed root causes; 2 investigated thoroughly and correctly left unfixed (one requires content authorship, one would require a redesign-scale change). **Local only — no deployment performed.**

## 1. Baseline

| Item | Value |
|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (unchanged) |
| Production version (start of phase) | `88ead829-b2b4-45d1-95c4-748cf25ee165` (Phase 28's deployment, 100% traffic) |
| Production health | `200` |
| Stale build artifacts present | No |
| Phase 28 reports confirmed present | Yes (`phase28-production-release-2026-08-28.md`/`.json`) |
| Local renderable pages | 1,753 |
| Local sitemap URLs | 1,454 |

**Disclosed limitation, stated upfront per the phase's own instruction**: no live browser automation was available in this session. All investigation and verification is source/CSS/HTML-level; visual rendering was not directly observed.

## 2. P29-1 — Header Loading / Render Order

### Investigation

Traced the exact injection mechanism for every page family:

| Page family | Header mechanism | Preloader present? | Timing risk |
|---|---|---|---|
| Homepage (`index.html`) | **Header content inlined directly into the HTML source** at the `<!-- JFT_INLINE_HEADER_START -->` marker — no fetch, no JS injection at all | Yes, but its timing is unrelated to header loading (nothing to wait for) | None — this is exactly why the homepage "loads together" |
| 84 product pages (83 of which have a preloader; `sugar-s30-supplier.html` does not) | `data-jft-early-header-loader` inline script, placed 6 lines after `<body>` (as early as structurally possible), `fetch('header.html')` | Yes, on 83/84 | **Confirmed defect**: preloader hides on a fixed timeout (900ms touch / 1400ms non-touch) with no relationship to whether the header fetch has actually completed |
| 10 category pages + `product-page-template.html` + `sugar-s30-supplier.html` | Same `data-jft-early-header-loader` fetch mechanism | **No preloader at all** | Any header-fetch delay is directly visible, unmasked |
| 37 articles (via `article-shell.js`) | `fetch()` gated behind `DOMContentLoaded` (i.e., does not even start until the entire document has been parsed) | **No preloader at all** | Most exposed case — the fetch starts later AND has nothing to mask it |

### Root Cause

Confirmed precisely: on 83 of 84 product pages, the header-loading script already dispatches a `jft:header-ready` custom event the instant the header is actually injected — but the preloader-hide logic was never connected to it, instead hiding on a guessed fixed delay. On a connection where the header fetch takes longer than 900-1400ms, the preloader disappears (revealing page content) before the header has arrived — precisely the reported symptom.

### Fix (Implemented)

`scripts/fix_preloader_header_timing.py`: made the preloader hide only once **both** the original minimum delay has elapsed **and** the header is confirmed ready (listening for the already-dispatched `jft:header-ready` event). The existing hard 3000ms fallback is left untouched as a safety net for the case where the header fetch fails outright (the ready event is only dispatched on success, never in the `.catch()` path — verified by reading the exact catch handler).

**Why this is safe**: in the common case (header loads well within 900-1400ms, which is virtually guaranteed for a same-origin static file), the preloader hides at exactly the same moment as before — **zero behavior change**. Only the failure case (header slower than expected) changes: the preloader now correctly waits instead of revealing content prematurely. Nothing about the mobile menu, locale switching, Google Translate, forex ticker, cookie bar, or analytics initialization was touched — all of those are independent of this specific preloader-hide timing.

**Scope**: 83 files (all product pages with this exact, verified-identical preloader block; `sugar-s30-supplier.html` correctly excluded — it has no preloader).

### Category Pages and Articles — Investigated, Not Fixed (documented per Rule 4)

These 47+ files have **no preloader at all**, so there is nothing to "fix" in the sense of correcting existing logic. Adding a brand-new preloader UI element to them would be a **new UI component** — explicitly forbidden by Phase 29's Rule 4 ("Do not add: new widgets... new UI components"). The only alternative fix (restructuring `article-shell.js`'s `DOMContentLoaded`-gated fetch to start earlier) would require modifying a single shared file used by 37+ pages with behavior I cannot verify visually without live browser access — this exceeds the "smallest safe fix" bar and risks the footer/back-to-top functionality `article-shell.js` also handles.

**Status: FIXED (83 product pages) / NOT FIXED, documented as an architectural limitation (category pages, articles) / INTENTIONAL, no fix needed (homepage)."**

## 3. P29-2 — Asia/Europe Trade Page Design Inconsistency

**Correction to the phase's own file list**: `middle-east-trade.html` does not exist in the repository. The actual Middle East regional page is `uae-trade.html` — confirmed by direct `ls`. All comparison below uses the real file.

Delegated a full source-level comparison of all 4 pages (`africa-trade.html`, `uae-trade.html`, `asia-trade.html`, `europe-trade.html`) plus `trade-regions.css` (the shared stylesheet Phase 12 already fixed for image-distortion/hidden-CTA bugs).

### Findings

- **CSS targeting is correct for all 4 pages** — `trade-regions.css` explicitly styles `.market-card`/`.market-tag` (Asia's components) and `.comply-card`/`.cert-badge` (Europe's components) alongside the shared `.port-card`/`.prod-card`/`.reg-item` used by Africa/UAE. There is no orphaned or unstyled class on either page — this is not a CSS-targeting bug.
- **The real divergence is structural completeness, not styling**: Asia (246 lines) is missing three whole sections present on the other three pages — a dedicated Ports/destinations section, a Products showcase, and a generic "Buyer Due Diligence" trust-signal block. Europe (291 lines) keeps the same section count as Africa/UAE but uses a self-consistent alternate compliance-grid pattern (`.comply-grid`/`.comply-card` instead of `.reg-grid`/`.reg-item`) — not a defect, a legitimate content-driven variant given Europe's dual EU/UK regulatory regime.
- **Most of Asia's differences are legitimately content-driven** — it covers 6 non-homogeneous countries better served by per-country market cards than a ports/products triad.
- **One specific, well-evidenced exception**: the "Buyer Due Diligence" block is byte-for-byte identical in Africa/UAE/Europe (same inline styling, same generic due-diligence framing, not region-specific in nature) and has no apparent reason to be entirely absent from Asia.

### Fix Decision: NOT FIXED

Correcting this specific gap requires **writing new, region-specific compliance copy** for Asia (framed around halal/permit/testing considerations relevant to that region, per the investigating agent's own recommendation) — this is content authorship, not a structural/CSS correction. Per this phase's own instruction ("If a finding requires... content authorship... document it and STOP that item"), this is documented for a future phase with business/editorial input, not implemented here.

**Status: CONFIRMED FINDING, NOT FIXED (requires content authorship).** All other observed differences: **INTENTIONAL** (content-driven, not template defects).

## 4. P29-3 — Insights / Site-Wide Template Consistency

Delegated a 12-page-family inventory comparing stylesheets, header mechanism, heading/hero style source, content-width approach, and inline-style reliance.

### Findings

- **Confirmed structural pattern**: 6 page families (products, category pages, all 84 product pages, trade-region pages, `privacy.html`, calculators) share the same canonical `.jft-page-hero`/`.jft-breadcrumb`/`.btn-gold` component system defined once in `jft-design-system.css`. Insights articles use **two different, locally-reinvented template systems** instead (an older per-page `<style>`-block approach on ~27 of 37 files, and a newer shared `seo-article.css` approach on ~10 files) — neither reuses the shared hero/breadcrumb/button components.
- **Not isolated to articles**: the same underlying pattern (skipping `jft-design-system.css`, redeclaring local `:root` color tokens in an inline `<style>` block) also appears on `buyer-security.html`, `export-documentation.html`, and `sample-request.html` — the last of which contains a code comment *acknowledging* a layout bug caused by skipping the core stylesheet.
- **A proposed sub-finding was investigated and found to be incorrect, not implemented**: the investigating agent flagged a "color drift" between article templates (`--jft-primary: #4e8c3e` in some files vs. `#3d7030` in others) and proposed normalizing `#3d7030` to the canonical `--green: #4e8c3e`. **Verified directly against `jft-design-system.css`'s actual token definitions** (`--green:#4e8c3e`, `--green-dark:#326127`, `--green-light:#6aad55`) and against this repository's own established, cross-phase-verified `jft-related-product` component (the exact aside component this session's own Phase 25 and Phase 27 work extended, following its pre-existing pattern) — `#3d7030` is a **long-established, intentional secondary "leaf" accent color**, distinct from the primary brand green, used consistently for border/link accents across many already-deployed pages. It is not a typo or drift. **This proposed fix was correctly rejected after verification** — implementing it would have replaced a legitimate, established design choice with an incorrect "correction," exactly the "different ≠ wrong" trap this phase's own rules warn against.

### Fix Decision: NOT FIXED

The genuine structural finding (articles and 3 other page families using locally-reinvented styling instead of the shared component system) spans 40+ files across 4+ page families. Unifying it would require a repository-wide template migration — a redesign-scale change explicitly forbidden by Rule 3 ("No Redesign... do not change... typography system... unless directly necessary"). No evidence was found that this causes broken spacing, broken typography, or a poor buyer experience (the phase's own bar for classifying "different" as "defective") — each affected page family renders as an internally consistent, already-reviewed design (confirmed for `buyer-security.html`/`export-documentation.html` in Phase 26's own direct read).

**Status: CONFIRMED ARCHITECTURAL PATTERN, NOT FIXED (redesign-scale scope, exceeds Phase 29). One proposed sub-fix (color normalization) INVESTIGATED AND REJECTED as factually incorrect.**

## 5. P29-4 — Contact Page FSSAI Image Distortion

### Investigation

Located the exact component: the "Secure Trade Desk → Request Your Export Quote" section's `.trust-strip` div, containing 3 certificate badge images (FSSAI, APEDA, Star Export House).

- **Image files**: verified via direct pixel-dimension extraction — all three `.webp` files are genuinely 720×347 (≈2.07:1), and the HTML `width="720" height="347"` attributes correctly match the actual files. No file-vs-attribute mismatch.
- **The actual defect**: the page's inline `<style>` block sets `.trust-strip img{height:26px; ...}` — constraining height only, **never setting `width`**. Correct, non-distorted scaling then depends entirely on the browser's implicit aspect-ratio-from-attributes inference rather than an explicit declaration. Combined with `.trust-strip{display:flex}` (a flex container) and the sitewide generic `img{max-width:100%;height:auto}` reset (which the local `height:26px` overrides, but which never had a `width` counterpart to override), this is a fragile pattern with no explicit guarantee against stretching.

### Fix (Implemented)

`scripts/fix_trust_strip_image_distortion.py`: added `width:auto;` explicitly to the `.trust-strip img` rule, guaranteeing proportional scaling regardless of browser/engine behavior. This is the standard, minimal correction for "image looks stretched when only one dimension is CSS-constrained."

**Scope, confirmed via search**: the exact same inline CSS rule (byte-for-byte identical) appears in `contact.html` and its 10 locale copies (`ar`, `es`, `fr`, `id`, `ms`, `pt`, `ru`, `si`, `th`, `vi`) — **11 files total**. `certificates.html` uses the identical class name `.trust-strip` but for a completely unrelated component (a background/border banner, no image-height rule at all) — confirmed via direct inspection and correctly excluded from the fix.

**Status: FIXED (11 files: root `contact.html` + 10 locale copies).**

## 6. Site-Wide Consistency Check (from the P29-3 investigation)

No additional, previously-undiscovered defect was found beyond what's documented in §4. The "locally-reinvented styling" pattern is the one confirmed cross-page-family observation, already fully documented above.

## 7. Findings Register

| ID | Finding | Status |
|---|---|---|
| P29-1a | Product-page preloader hides on a fixed timeout unrelated to actual header-ready state | **FIXED** (83 files) |
| P29-1b | Category pages / `sugar-s30-supplier.html` / `product-page-template.html` have no preloader to mask header-fetch delay | **NOT FIXED** — adding one would be a new UI component (Rule 4) |
| P29-1c | Articles fetch the header only after `DOMContentLoaded`, with no preloader | **NOT FIXED** — would require modifying a shared file (`article-shell.js`) beyond safe verification without live browser access |
| P29-1d | Homepage header-loading behavior | **INTENTIONAL**, no defect (header is build-time inlined) |
| P29-2 | Asia Trade page missing the generic "Buyer Due Diligence" block present on 3 sibling pages | **CONFIRMED, NOT FIXED** — requires new region-specific compliance copy (content authorship) |
| P29-2b | All other Asia/Europe structural differences (market cards vs. ports/products, compliance-grid variant) | **INTENTIONAL**, content-driven, not defects |
| P29-3 | Articles (+ 3 other page families) use locally-reinvented styling instead of the shared design-system hero/breadcrumb/button components | **CONFIRMED ARCHITECTURAL PATTERN, NOT FIXED** — redesign-scale scope |
| P29-3b | Proposed "color drift" correction (`#3d7030` → `#4e8c3e`) | **INVESTIGATED AND REJECTED** — `#3d7030` is a distinct, intentional, established accent color, not a defect |
| P29-4 | FSSAI/APEDA/Star-Export-House badge images distorted on Contact page (root + 10 locales) | **FIXED** (11 files) |

## 8. Files Affected

| File(s) | Change | Reason |
|---|---|---|
| 83 product pages (all `*-exporter.html`/`*-supplier.html` except `sugar-s30-supplier.html`) | Preloader-hide logic now also waits for `jft:header-ready` | P29-1a |
| `contact.html` + 10 locale copies | `.trust-strip img` rule gains explicit `width:auto` | P29-4 |
| `scripts/fix_preloader_header_timing.py` (new) | Governed, deterministic, idempotent script implementing P29-1a | — |
| `scripts/fix_trust_strip_image_distortion.py` (new) | Governed, deterministic, idempotent script implementing P29-4 | — |

## 9. Files Intentionally Not Affected

- Homepage (`index.html`) — no defect found.
- 10 category pages, `product-page-template.html`, `sugar-s30-supplier.html` — no preloader exists to fix; adding one is out of scope (Rule 4).
- 37 articles — same reasoning; `article-shell.js` not modified.
- `asia-trade.html`, `europe-trade.html` — no structural section added; requires content authorship.
- All 37 article files' local styling, `buyer-security.html`, `export-documentation.html`, `sample-request.html` — architectural pattern documented, not migrated (redesign-scale, out of scope).
- `certificates.html` — shares the `.trust-strip` class name but is a genuinely different, unaffected component.

## 10. Regression Results

| Script | Result |
|---|---|
| `audit_website.py` | 0 findings, 1,753 pages |
| `full_site_audit.py` | 0 findings, 1,454 indexable |
| `audit_commercial_content.py` | 0 findings |
| `audit_claims_and_products.py` | 0 findings |
| `validate_blog_navigation.py` | Passed — 260 blog cards, 66 legacy redirects, 0 stale images |
| `audit_locale_ui.py` | 0 findings, determinism PASS |
| `audit_localizations.py` | 0 findings |
| `audit_coverage_gaps.py` | 0 findings |
| `audit_performance.py` | 0 findings |
| `check_links.py` | 0 broken links / 1,766 files |

Page counts, sitemap count, and indexable-page count all unchanged from the Phase 28 baseline (no page created/removed this phase, only in-place edits). Determinism verified: both new scripts run twice, second run reported 0 changes (fully idempotent).

## 11. Build Results

`scripts/build_cloudflare_assets.py` (existing, unmodified) built 2,099 assets successfully. Artifact inspected: both fixes confirmed present in the built bundle; `reports/`, `scripts/`, `.env`, `.dev.vars`, `.git` all confirmed absent. Temporary artifact deleted immediately after verification — **not deployed**.

## 12. Production/Local Diff Discipline

Verified via production-vs-local hash comparison (the meaningful signal for this repository's never-committed history, established in Phase 28): `contact.html` and a sample product page (`1121-basmati-rice-exporter.html`) correctly **differ** from production (expected — these are the files Phase 29 changed); `header.html` and a category page correctly **match** production exactly (confirmed untouched). No unexplained modification found.

## 13. Limitations

- No live browser automation was available this session; all findings and fixes were verified via source/CSS/HTML inspection and static-equivalent checks, not rendered-pixel observation, per this phase's own required disclosure.
- The P29-1 fix's real-world effect (whether the preloader now genuinely masks slow header loads) cannot be visually confirmed without live browser testing under a throttled-network condition — the fix is verified correct by code logic and event-wiring inspection, not by observing an actual slow-network scenario.

## 14. Remaining Findings / Recommendations

1. **P29-1 (category pages, articles)**: if eliminating the header-flash risk on these 47+ pages is a priority, a future phase should evaluate either (a) extending the homepage's build-time header-inlining approach site-wide (a larger, dedicated build-system project), or (b) adding a lightweight, consistent preloader to these families as a deliberate UI decision (not a "fix," a real design choice requiring sign-off).
2. **P29-2**: a future content-authorship pass should write Asia-specific "Buyer Due Diligence" copy (halal/permit/testing framing) to close the one confirmed structural gap.
3. **P29-3**: if template consistency across articles/trust pages is a priority, a dedicated, appropriately-scoped design-system migration phase should unify them onto the shared `.jft-page-hero`/`.jft-breadcrumb` components — this is a real, multi-file undertaking, not a quick fix.

## Stop

Per Phase 29's explicit instruction, no deployment was performed. **Phase 29 implementation is complete locally and verified. No deployment performed. Deployment requires separate explicit authorization.**
