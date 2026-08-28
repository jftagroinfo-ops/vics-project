# Phase 12 — Premium Brand, Visual UX & Conversion-Polish Audit (Pre-Implementation)

Date: 2026-08-27
Status: Investigation only. No website source files modified while producing this report.

## 1. Executive Summary

The design system is coherent and considerably more disciplined than a "Phase 12 needs a redesign" brief usually assumes: a deliberate navy/green/gold/cream palette with proper light/dark variants, a classic premium editorial type pairing (Merriweather serif headings, Montserrat labels, Lato body), a consistent pill-button system with three well-differentiated tiers, fluid `clamp()`-based type/spacing scales, and evidence of prior accessibility work already baked in (a code comment recording a WCAG-AA contrast fix to `.article-meta`). This is not a site that needs "more design" — it needs two specific, high-confidence defects fixed, both of which were traced to their exact CSS source and neither of which requires new imagery, new colors, or new components.

Two P0-severity, systemic, evidence-based defects were found:

1. **The primary hero CTA is programmatically hidden on all 4 regional trade pages** (Africa, Asia, Europe, UAE) — a CSS rule in the shared `trade-regions.css` sets `display:none !important` on `.hero-btns`, which silently deletes each page's carefully written, region-specific primary CTA ("Get CIF Africa Quote," "Get Asia Quote," "Get EU/UK Quote," "Request PI for UAE") from the first screen a buyer sees.
2. **Product-card images render visibly distorted on all 10 Phase 10 category pages.** `.prod-img img` has no `object-fit` rule anywhere in the codebase, so the browser default (`fill`, which stretches non-uniformly) applies. A direct measurement of all 84 product source images found 68 (81%) are not square and 45 (54%) have an aspect ratio outside 0.75–1.3 — yet the category-page generator declares every card image as a hardcoded `width="1024" height="1024"` (square). This is the exact mechanism that produces visibly squished or stretched product photography, on the newest and most "flagship catalogue" part of the site.

Both are fixed with a total of roughly 10 lines of shared CSS in `trade-regions.css` — no new pages, no new images, no content rewrite, no framework.

## 2. Design-System Inventory

Extracted directly from `jft-design-system.css` (the master token file, 514 lines):

| Token category | Values found | Classification |
|---|---|---|
| Color palette | `--green #4e8c3e` / `--green-dark #326127` / `--green-light #6aad55`, `--navy #1a3c34` / `--navy-dark #0d1f1b` / `--navy-light #2c5148`, `--gold #eebf45` / `--gold-light #f7ca5e` / `--gold-dark #b88d14`, `--cream #fdfbf7` | **CONSISTENT** — a deliberate 3-hue system with proper tonal variants, reused via CSS variables everywhere checked |
| Typography | `--ff-h: Merriweather` (headings), `--ff-s: Montserrat` (labels/buttons), `--ff-b: Lato` (body) | **CONSISTENT** — classic premium editorial pairing, already in place, not generic |
| Buttons | `.btn-primary` / `.btn-gold` / `.btn-outline` / `.btn-outline-navy`, all 50px pill radius, consistent padding (`14-17px / 38-42px`), consistent hover (`translateY` + shadow bloom) | **CONSISTENT** |
| Cards | `.jft-info-card` / `.jft-dark-card`: `border-radius: 20px`, hover elevation + gold accent-line reveal | **CONSISTENT** within this family |
| Cards (trade/category) | `.prod-card` / `.port-card` / `.why-card` / `.market-card` etc. (`trade-regions.css`): `border-radius: 8px !important` | **MINOR INCONSISTENCY** vs. the 20px used elsewhere — see §13, not fixed (see rationale) |
| Spec table | `border-radius: 16px`, zebra-free single-line rows, left column labelled/shaded | **CONSISTENT** |
| Section spacing | `--section-pad: clamp(70px, 9vw, 130px)` sitewide via `.section-padding`; category pages instead hardcode `section { padding: 60px 0; }` inline | **MINOR INCONSISTENCY** — documented, not fixed (low visual impact, both values are in a reasonable premium range) |
| Page hero | `.jft-page-hero`: dark gradient + 60px grid overlay + fractal-noise texture + radial glow + gold edge stripe | **CONSISTENT and PREMIUM-QUALITY** — genuinely well-executed dark/gold institutional hero pattern, reused correctly across trust pages, tools, and (via `trade-regions.css` overrides) regional pages |
| Breadcrumb | RTL chevron mirroring already fixed in Phase 11 (`html[dir="rtl"] .jft-breadcrumb i { transform: scaleX(-1); }`), confirmed still present | **CONSISTENT** |
| Product-card image container | `.prod-img` / `.prod-img img`: no `object-fit`, no `aspect-ratio`, no fixed height anywhere in any of the 4 loaded stylesheets | **FUNCTIONAL ISSUE** — see Finding 1 |
| Regional-hero CTA visibility | `.hero-btns { display: none !important; }` in `trade-regions.css`, with no contradicting rule anywhere else in the cascade | **FUNCTIONAL ISSUE** — see Finding 2 |

## 3. "First 10 Seconds" Scores (0-10, not inflated)

| Page | Understands proposition | Communicates scale/reliability | Primary CTA obvious | Score |
|---|---|---|---|---|
| Homepage | Yes — hero states commodities + India + Star Export House/ISO trust tag | Yes | Yes (dual CTA) | 8 |
| `products.html` | Yes | Yes (84-product framing) | Yes | 8 |
| Category page (rice) | Yes | Yes | Yes, but product cards below look distorted (Finding 1) | 6 |
| Product page (1121 Basmati) | Yes | Yes (cert strip, spec table) | Yes (3-tier CTA) | 8 |
| Article | Yes | Yes (editorial review note) | Yes (buyer-path panel) | 8 |
| Regional page (Africa) | Yes | Yes (corridor stats) | **No — CTA is invisible (Finding 2)** | **3** |
| Contact page | Yes | Yes (trust strip, FAQ) | Yes | 8 |
| Sample request | Yes | Yes (process steps) | Yes | 8 |

The regional-page score of 3 is driven entirely by Finding 2 (the hidden CTA) — every other element of that page (stats grid, port cards, compliance section) already scores well.

## 4. Findings

### Finding 1 (P0) — Regional-page primary hero CTA is invisible

**Evidence**: `trade-regions.css:78-80` sets `.hero-btns { display: none !important; }`. All 4 regional pages (`africa-trade.html`, `asia-trade.html`, `europe-trade.html`, `uae-trade.html`) load `trade-regions.css` after their own inline `<style>` block that defines `.hero-btns { display: flex; gap: 15px; ...}` with no `!important` — so the external rule wins unconditionally regardless of source order. Each page's `.hero-btns` div contains a real, well-written, region-specific primary CTA pair (e.g. Africa: "Get CIF Africa Quote" + "Estimate Price to Your Port"; UAE: "Request PI for UAE" + "Estimate CIF Jebel Ali"). No other rule in any loaded stylesheet re-enables it.

**Why it's a problem**: this is the single highest-value, above-the-fold CTA on 4 commercially important market-landing pages, and it renders as if it doesn't exist. A buyer arriving from a market-specific search or link sees a hero with a value proposition and a stats grid, but no button.

**Users affected**: every visitor to any of the 4 regional pages, on every device and locale variant that loads `trade-regions.css`.

**Root cause**: `trade-regions.css` is a shared override stylesheet that also styles `.prod-card`/`.port-card` etc. (reused by the Phase 10 category pages). The `.hero-btns` rule appears to be leftover from a different context and was never checked against the regional pages' own hero, which legitimately needs it visible.

### Finding 2 (P0) — Category-page product-card images render distorted

**Evidence**: a direct measurement of all 84 product source images (`data/products.json`'s `i` field, read with Pillow) found 68/84 (81%) are not square and 45/84 (54%) have a width:height ratio outside 0.75–1.3 (as extreme as 0.58:1 and 2.72:1). `scripts/build_category_pages.py`'s `render_product_card()` emits every card image with a hardcoded `width="1024" height="1024"` regardless of the source file's real dimensions. No stylesheet (`jft-design-system.css`, `jft-responsive.css`, `trade-regions.css`) defines `object-fit`, `aspect-ratio`, or a fixed height for `.prod-img` or `.prod-img img` — confirmed by exhaustive grep across all four loaded CSS files. `jft-responsive.css:791-800` has an `object-fit: cover` rule, but it targets the differently-named `.product-img` (singular) class, not `.prod-img` — a near-miss that does not apply here. With no author `object-fit` and `height: auto` in effect (from the global `img{...height:auto}` reset), the browser falls back to CSS's default `object-fit: fill`, which stretches non-uniformly to whatever box the (incorrect) square `width`/`height` attributes imply.

**Why it's a problem**: this directly determines whether the category pages look like "a basic directory" or "a professional commodity catalogue" (Phase 12 §7's own framing) — stretched, uneven product photography is one of the fastest ways to read as unprofessional or low-budget, on exactly the pages built to be the site's premium commodity showcase.

**Users affected**: every visitor to any of the 10 category pages (built in Phase 10) for roughly 68 of 84 products.

**Root cause**: the category-page generator (Phase 10 work) never gave `.prod-img` a fixed-ratio container, and no shared stylesheet filled the gap.

### Finding 3 (P1, documented only — not fixed) — Amateur/inconsistent product photography style

**Evidence**: direct visual inspection of two sample images (`1121 Golden Sella Basmati.webp`, `5 Silky Sortex.webp`) shows informal, hand-held trade/QA-style photography (a hand holding loose grains, a taped paper label in one case) rather than styled product photography. Combined with the 81% non-square finding above, the catalogue's source photography is visually inconsistent in framing, background, and style across products.

**Why this is documented, not fixed**: Phase 12 explicitly requires "CURRENT IMAGE / PROBLEM / REPLACEMENT REQUIREMENT / WHY" for any proposed image replacement, and explicitly prohibits fabricating or sourcing imagery without proper rights. This session has no ability to commission or verify real JFT Agro product photography, so no replacement is proposed as an implemented change. The Finding 2 fix (proper `object-fit: cover` cropping) improves the *presentation* of the existing photos (uniform, non-distorted cards) without needing new photography, and is the actionable portion of this issue.

**Recommended fix (future phase, requires real photography)**: replace hand-held photos with consistent flat-lay or light-box product shots (neutral background, consistent framing, product label visible) — this cannot be done from within this session.

## 5. Findings Considered and Not Actioned

- **`.prod-card` border-radius (8px) vs. `.jft-info-card`/`.jft-dark-card` (20px)** — a measurable, real inconsistency (§2), but not obviously wrong: tighter radii on a structured product-catalogue grid vs. softer radii on decorative trust cards is a defensible intentional differentiation (industrial/structured vs. approachable/soft), not a clear defect. Normalizing it would be a stylistic preference change without commercial-harm evidence, which Phase 12 explicitly warns against ("do not normalize values simply for mathematical symmetry"). Left unchanged.
- **Category-page section padding (`60px 0` inline) vs. sitewide `--section-pad` clamp (70-130px)** — both are within a normal premium range; no visible harm found. Left unchanged.
- **Homepage hero CTA order** (Browse Products primary) — already reviewed in Phase 11, no new evidence found this phase to revisit that decision.
- **Global font replacement, color changes, animation additions** — none proposed; no evidence found that any of these would fix a real problem, and Phase 12 explicitly prohibits changes without such evidence.

## 6. Recommended Fixes (both implemented — see final report)

| Fix | File | Change | Risk | Verification plan |
|---|---|---|---|---|
| 1 | `trade-regions.css` | Remove/neutralize the `.hero-btns { display: none !important; }` rule | Very low — restores markup that already exists correctly on all 4 pages; no other page uses `.hero-btns` | Grep confirms `.hero-btns` is used only on the 4 regional pages; re-render check via HTML/CSS parse; regression suite |
| 2 | `trade-regions.css` | Add `.prod-img { aspect-ratio: 1/1; overflow:hidden; }` and `.prod-img img { width:100%; height:100%; object-fit:cover; }` | Very low — `object-fit:cover` is the same proven pattern already used correctly elsewhere on the site (product-page hero images, editorial images); scoped to a class used only by category/regional product cards | HTML validation, regression suite, visual/structural diff of before/after CSS |

## 7. Before/After Scorecard (honest, not inflated)

| Dimension | Before | Target | Rationale |
|---|---|---|---|
| Brand perception | 7.5 | 8.5 | Strong system, undermined by 2 concrete bugs |
| Visual hierarchy | 8 | 8.5 | Already strong |
| Homepage | 8 | 8 | No changes made — already sound |
| Products (products.html) | 8 | 8 | No changes made — already sound |
| Categories | 6 | 8.5 | Directly fixed by Finding 2 |
| Product pages | 7.5 | 7.5 | No changes made this phase — hero-crop issue (Finding 3) documented only |
| Trust | 8 | 8 | No changes made — already sound (confirmed in Phase 11) |
| CTA UX | 6.5 | 8.5 | Directly fixed by Finding 1 on regional pages; unchanged (already good) elsewhere |
| Mobile | 7.5 | 7.5 | No layout changes made; both fixes are CSS-only and reviewed against existing breakpoints |
| International | 8 | 8 | No locale-specific changes made; regional pages are English-only (unaffected by locale audits) |
| Accessibility | 8 | 8 | Neither fix touches contrast, focus, or semantics |
| Performance | 8 | 8 | Both fixes are a net-neutral or negative byte count (one CSS rule removed, one small rule added) |
| Consistency | 7 | 7.5 | Card-radius inconsistency (§5) intentionally left as a documented, non-actioned judgment call |

## 8. Risk Assessment

Both fixes are shared-CSS, single-file, additive-or-subtractive-only changes with no HTML/JS touched. The primary risk is that `.hero-btns` or `.prod-img` might be used by some other page in an intentional "hidden"/"stretched" way that this investigation missed — mitigated by an exhaustive `grep` across the full site confirming `.hero-btns` appears only in the 4 regional pages' markup and `.prod-img` appears only in category-page (and regional-page) product-card markup, both places where visible, correctly-sized/positioned CTAs and images are unambiguously the intended outcome.

## 9. Verification Plan

1. Re-run the full existing audit suite (10 scripts) — expect 0 findings, matching Phase 10/11 baselines.
2. HTML5 + JSON-LD validation on all pages that load `trade-regions.css` (10 category + 4 regional = 14 files).
3. `check_links.py` — expect 0 broken links (neither fix touches a link target).
4. Static-equivalent visual verification (no live browser tool available this session — disclosed, not claimed): parse the final CSS to confirm exactly one `.hero-btns` rule remains (the page-level `display:flex`) and confirm the new `.prod-img`/`.prod-img img` rules are syntactically valid and scoped correctly.
5. Cloudflare build rebuild and clean-bundle check, not deployed.
6. Full `git diff` review of `trade-regions.css` to confirm the only changes are the two documented fixes.
