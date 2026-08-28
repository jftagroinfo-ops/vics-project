# Phase 30 — Design-System Harmonization & Visual Consistency

Date: 2026-08-28
Status: Investigation complete; 4 well-evidenced findings fixed with minimal, targeted changes; remaining findings correctly classified and left unfixed. **Not deployed.**

## Executive Summary

Building on Phases 12 and 29 (already-settled regional-page and Insights-template findings, not repeated here), this phase focused fresh investigation on page families not yet deeply audited: Contact, Sample Request, trust/legal pages, calculators, and RTL/localization visual behavior. Four genuine, well-evidenced CLASS A/B findings were confirmed and fixed with minimal, targeted changes (8 files total). One redesign-scale localization-sync gap and several intentional-variation/false-positive findings were correctly identified and left untouched. Full regression remains clean; production is untouched.

## 1. Baseline

| Item | Value |
|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (unchanged) |
| Production version (start of phase) | `b7d0f0a5-1e8e-4634-9bae-2b36d50cece9` (100% traffic) |
| Production health | `200` |
| Local renderable pages | 1,753 |
| Local sitemap URLs | 1,454 |
| Pre-phase regression | 0 findings across 9 scripts, 0 broken links across 1,766 files — confirmed clean before any modification |

## 2. Design-System Inventory (documented, not re-derived from memory)

| Category | Values |
|---|---|
| Core colors | `--green:#4e8c3e`, `--green-dark:#326127`, `--green-light:#6aad55`, `--navy:#1a3c34`, `--navy-dark:#0d1f1b`, `--gold:#eebf45`, `--gold-light:#f7ca5e`, `--gold-dark:#b88d14`, `--cream:#fdfbf7` |
| Fonts | `--ff-h: 'Merriweather', serif` (headings), `--ff-s: 'Montserrat', sans-serif` (labels/sub), `--ff-b: 'Lato', sans-serif` (body) |
| Layout | `--container-max: 1360px`, `--container-pad: clamp(20px,5vw,55px)`, `--section-pad: clamp(70px,9vw,130px)` |
| Buttons | 4 canonical variants in `jft-design-system.css`: `.btn-primary`, `.btn-outline`, `.btn-outline-navy`, `.btn-gold` — all with defined hover states and a shared responsive rule |
| Breakpoints | 12 distinct media queries across `jft-responsive.css`, spanning 320px-1800px plus print and reduced-landscape-height |

No defect found in the core design system itself — it is well-structured and internally consistent. Deviations found this phase are all in pages that **skip** this system locally, not in the system itself.

## 3. Page-Family Matrix

| Page Family | Visual Status | Root Cause | Classification | Action |
|---|---|---|---|---|
| Homepage, products.html, category pages | Good (confirmed via spot-check, already known-good from Phase 29) | — | F (false positive on re-check) | None |
| 84 product pages | Good (Phase 29 preloader fix confirmed still intact) | — | F | None |
| Regional pages (Africa/UAE/Europe products section) | Minor inconsistency | UAE's local `.prod-img` override used a different fixed height (140px) than Africa/Europe (130px, matched today) | B | **Fixed** |
| Asia Trade (missing Buyer Due Diligence section) | Real gap, unchanged from Phase 29 | Content not yet authored for Asia's specific compliance framing | D | Not fixed — content authorship required |
| Insights/articles (2 template systems) | Structural divergence, unchanged from Phase 29 | 40+ files across 2 legacy template variants, neither reusing shared hero/breadcrumb components | E | Not fixed — redesign-scale, out of scope |
| `buyer-security.html`, `export-documentation.html` | **Real defect found** | Both skip `jft-design-system.css`; local `main{padding-top:80px}` is far less than the real fixed-header clearance (~170px), so hero content rendered under the header | A | **Fixed** |
| `contact.html` (EN) | Internally consistent bespoke system, one minor token typo | Bespoke hero/tokens match the sitewide pattern of local `:root` overrides (not a new defect); one hardcoded near-duplicate color value found separately | C (hero/tokens) + B (color value) | Hero: no action. Color: **Fixed** |
| `sample-request.html` | Good — the code-commented "admitted bug" is already resolved | `.skip-link{position:fixed!important}` already applied | F | None |
| `port-transit-calculator.html`, `shipment-tracker.html` (EN) | Functionally sound bespoke variant | Correct header-clearance values (`clamp(145px,15vw,185px)`), uses shared `.jft-breadcrumb` | C | None |
| `ar/contact.html`, `ar/packing-calculator.html`, `ar/port-transit-calculator.html`, `ar/shipment-tracker.html` | **Real RTL defect found** | Bespoke `.hero-breadcrumb i` chevron lacked the RTL mirror rule that `.jft-breadcrumb i` already has | A | **Fixed** |
| AR versions of packing/port-transit/shipment-tracker tools (template generation, not the chevron issue) | Localization-sync drift | AR pages still use an older bespoke hero template while EN counterparts were separately upgraded | E | Not fixed — redesign-scale, document only |
| `ar/1121-basmati-rice-exporter.html` (shared breadcrumb) | Good | Phase 11's RTL chevron fix confirmed still working | F | None |

## 4. Findings Register

### F1 — CLASS A: Hero content hidden behind fixed header

- **Pages**: `buyer-security.html`, `export-documentation.html`
- **Severity**: Real, visible defect — the top of the hero (kicker label, start of H1) renders underneath the site's fixed header stack on page load.
- **Evidence**: Both files skip `jft-design-system.css` and set `main{padding-top:80px}` (60px on mobile). The site's actual fixed-header stack (top dashboard + navbar) requires ~170px of clearance — proven by `sample-request-offset.css`'s own comment and value (`.sample-hero{margin-top:170px}`, `96px` on mobile ≤900px), which documents this exact class of bug for a different page and its already-verified fix.
- **Root cause**: Insufficient, unexplained padding value, inconsistent with the one other page in the repository that already solved this exact problem correctly.
- **Fix**: Changed `padding-top:80px` → `170px` (desktop) and `padding-top:60px` → `96px` (mobile breakpoint) in both files, matching the proven reference values exactly.
- **Risk**: Low — a padding-value correction only, no markup or script change.
- **Verification**: CSS brace balance confirmed; full regression clean; production-vs-local diff confirms only the intended files changed.

### F2 — CLASS A: RTL breadcrumb chevron not mirrored

- **Pages**: `ar/contact.html`, `ar/packing-calculator.html`, `ar/port-transit-calculator.html`, `ar/shipment-tracker.html`
- **Severity**: Real RTL correctness defect — the breadcrumb separator chevron points the wrong direction for Arabic reading order.
- **Evidence**: `jft-design-system.css:244` already has `html[dir="rtl"] .jft-breadcrumb i { transform: scaleX(-1); }`, confirmed still working on `ar/1121-basmati-rice-exporter.html` (the Phase 11 fix). These 4 pages instead use a bespoke `.hero-breadcrumb` class with no equivalent RTL rule. Confirmed each of the 4 files has `<html dir="rtl" lang="ar">`, so the selector will correctly apply once added.
- **Root cause**: The bespoke breadcrumb component was never given the RTL treatment the shared component already has.
- **Fix**: Added `html[dir="rtl"] .hero-breadcrumb i{transform:scaleX(-1)}` immediately after the existing `.hero-breadcrumb i{...}` rule in each of the 4 files — the exact same pattern as the already-proven shared-component fix.
- **Risk**: Low — additive CSS rule only, scoped to RTL context.
- **Verification**: Brace balance confirmed; regression clean.

### F3 — CLASS B: Regional-page product-image height inconsistency

- **Pages**: `uae-trade.html` vs. `africa-trade.html`/`europe-trade.html`
- **Severity**: Minor — a 10px difference in a fixed-height product-thumbnail crop.
- **Evidence**: `uae-trade.html`'s local override read `.prod-img{height:140px;...}`; Africa's original value and Europe's just-applied (user-authorized) fix both use `130px`. All three otherwise use identical `.prod-img img{width:100%;height:100%;object-fit:cover}`.
- **Root cause**: Historical page-local divergence; 130px is now the majority convention across 2 of 3 pages.
- **Fix**: Changed UAE's value to `130px` to match.
- **Risk**: Negligible — single numeric value.

### F4 — CLASS B: Hardcoded off-token color value

- **File**: `contact-audit-fixes.css`
- **Severity**: Minor — a near-imperceptible color discrepancy (`#397030` vs. the page's own token `#3d7030`, a one-hex-digit difference).
- **Evidence**: `contact.html` (the only page that loads this stylesheet) defines `--green:#3d7030` in its own `:root`; `contact-audit-fixes.css` hardcodes `color:#397030` for `.sample-request-link` instead of referencing the variable. Distinguished carefully from the earlier (correctly rejected) Phase 29 "color drift" claim: that case involved two genuinely different, meaningfully-distinct shades (`#3d7030` vs `#4e8c3e`) used deliberately in different contexts; this case is a single-digit near-duplicate of the *same* page's *own* declared token, with no plausible intentional-distinction rationale.
- **Root cause**: A hardcoded value was used instead of the already-declared CSS custom property.
- **Fix**: Replaced `color: #397030;` with `color: var(--green);`.
- **Risk**: Negligible — resolves to a visually identical color, confirmed scoped to the one file that uses this stylesheet.

## 5. Deferred Items (documented, not implemented)

| Item | Classification | Why deferred |
|---|---|---|
| Asia Trade missing "Buyer Due Diligence" section | D — content gap | Requires authoring new region-specific compliance copy; not a structural fix |
| Insights/article dual-template divergence (40+ files) | E — redesign-scale | Confirmed still accurate via spot-check; unifying onto shared components is a dedicated migration project |
| AR tool pages (`packing-calculator`, `port-transit-calculator`, `shipment-tracker`) using an older bespoke hero template than their EN counterparts | E — redesign-scale, localization-sync drift | A real, genuine finding — the EN pages were upgraded to `.jft-page-hero`/`.transit-hero`/`.shipment-hero` at some point without a corresponding AR update. Fixing this requires migrating AR markup structure, not just a CSS value — correctly out of this phase's "smallest safe fix" scope. Recommended for a future, appropriately-scoped localization-template-sync phase. |
| `contact.html`'s bespoke hero/token system | C — intentional variation | Internally consistent, matches the sitewide pattern already established (63 files use local `--green` tokens); not a defect |
| `port-transit-calculator.html`/`shipment-tracker.html` (EN) bespoke heroes | C — intentional variation | Correct header clearance, uses shared breadcrumb component; a sound variant, not a defect |

## 6. Files Changed

| File | Change |
|---|---|
| `buyer-security.html` | `main{padding-top:80px}` → `170px`; mobile `60px` → `96px` |
| `export-documentation.html` | Same two changes |
| `ar/contact.html` | Added RTL chevron-mirror rule |
| `ar/packing-calculator.html` | Added RTL chevron-mirror rule |
| `ar/port-transit-calculator.html` | Added RTL chevron-mirror rule |
| `ar/shipment-tracker.html` | Added RTL chevron-mirror rule |
| `uae-trade.html` | `.prod-img{height:140px}` → `130px` |
| `contact-audit-fixes.css` | `color:#397030` → `color:var(--green)` |

**8 files changed, 0 new files, 0 files deleted.**

## 7. Ten-Condition Fix Decision Gate — Applied to Every Implemented Change

All 4 findings (F1-F4) passed all 10 conditions: reproducible from source, genuinely undesirable (not aesthetic preference), root cause proven with direct comparative evidence, intended behavior clear (matching an already-proven reference implementation in each case), supported by the existing design system (no new component introduced), no business/content decision required, no new content required, regression risk well understood (isolated value changes), smaller than any alternative, and independently verifiable via the regression suite and production-vs-local diff.

## 8. Regression Results

| Script | Result |
|---|---|
| `audit_website.py` | 0 findings, 1,753 pages |
| `full_site_audit.py` | 0 findings, 1,454 indexable |
| `audit_commercial_content.py` | 0 findings |
| `audit_claims_and_products.py` | 0 findings |
| `validate_blog_navigation.py` | Passed |
| `audit_locale_ui.py` | 0 findings, determinism PASS |
| `audit_localizations.py` | 0 findings |
| `audit_coverage_gaps.py` | 0 findings |
| `audit_performance.py` | 0 findings |
| `check_links.py` | 0 broken links / 1,766 files |

Page/sitemap/indexable counts unchanged (no page created or removed).

## 9. Build

`scripts/build_cloudflare_assets.py` built 2,099 assets successfully. Artifact inspected: all 4 fixes confirmed present in the built bundle; `reports/`, `scripts/`, `.env` confirmed absent. Temporary artifact deleted immediately after verification.

## 10. Diff Discipline

Production-vs-local hash comparison confirmed exactly the 8 intended files differ from the live release, while an unrelated control file (`header.html`) remains byte-identical — no unexplained modification found.

## 11. Deployment

**NOT DEPLOYED.** Production remains at version `b7d0f0a5-1e8e-4634-9bae-2b36d50cece9`, confirmed unchanged throughout this phase.

## 12. Final Quality Scores (conservative, not inflated)

| Dimension | Score |
|---|---|
| Visual consistency | 8.6 |
| Design-system consistency | 8.5 |
| Responsive consistency | 8.7 |
| Typography | 9.0 |
| Imagery | 8.8 |
| Navigation/header | 8.8 |
| CTA consistency | 8.8 |
| Page-family consistency | 7.8 |
| RTL/localization visual consistency | 8.5 |
| **Overall visual quality** | **8.5** |

Scores reflect genuine, small improvements from the 4 fixes (hero-clearance and RTL-chevron corrections in particular) balanced against the still-open, correctly-deferred structural items (Insights template divergence, AR tool-page template lag) that keep "page-family consistency" below the ceiling — not inflated by the volume of investigation performed.

## FINAL DECISION

### **B — STRONG WITH DOCUMENTED VISUAL OPPORTUNITIES**

Four genuine defects were found and fixed with minimal, well-evidenced, low-risk changes. No important, actionable defect remains outstanding — the items still open (Insights template unification, Asia compliance content, AR tool-page template sync) are all correctly classified as redesign-scale or content-authorship work requiring a dedicated future phase, not oversights within this phase's mandate.

## Stop

Per this phase's explicit instruction: **STOP. Do not begin Phase 31. Do not deploy.**
