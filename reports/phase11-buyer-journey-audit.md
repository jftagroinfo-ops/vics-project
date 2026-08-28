# Phase 11 — Buyer Journey Audit (Pre-Implementation)

Date: 2026-08-27
Status: Audit only. No website files modified while producing this report.

## Method

Direct inspection of source HTML/CSS/JS for: homepage, `products.html`, all 10 Phase 10 category pages, 5 representative product pages across different commodities (`1121-basmati-rice-exporter.html`, a Silky Sortex variant, a spice, a pulse, an oilseed), `contact.html` (+ 3 locale copies), `sample-request.html`, `buyer-security.html`, `export-documentation.html`, `quality-control.html`, `infrastructure.html`, `quote-calculator.html`, `packing-calculator.html`, `port-transit-calculator.html`, `shipment-tracker.html`, `europe-trade.html`, `header.html`, `footer.html`, `jft-conversion.js` (the site's shared conversion/analytics layer), `sample-request.js`, and the inline RFQ-handling script in `contact.html`.

This audit deliberately does not assume the Phase 9/10 findings are still the current state, and does not assume common CRO gaps exist just because they're common elsewhere — every finding below is backed by a specific file/line/measurement.

## Headline Finding: the commercial UX foundation is more mature than a typical "Phase 11 CRO audit" assumes

Before listing gaps, it is important to record what is **already correctly built**, because several things this kind of phase brief usually expects to find missing are in fact already present and working:

- **Analytics already exists** and is privacy-respecting: `jft-conversion.js` implements a consent-gated GA4 integration (`anonymize_ip`, `allow_google_signals: false`), tracks `form_start`, `rfq_start`, `sample_request_start`, `generate_lead`, `rfq_submit`, `sample_request_submit`, `view_item`, `article_view`, `article_read_depth`, `whatsapp_click`, `contact_phone`, `contact_email`, `file_download`, `outbound_click`, and `page_not_found`. This is not a measurement gap to flag — it is a working system to audit and preserve.
- **Article → Product → RFQ flow already exists**: `jft-conversion.js`'s `addArticleBuyerPath()` injects a "Buyer next step" panel after every blog article's body with three actions (View [matched product], Build Reference Estimate, Request Export Quote via `contact.html?product=X&source=article#inquiry-form`) — this is exactly the `ARTICLE → PRODUCT → QUOTE` flow the phase brief describes as a target state (Part 46).
- **WhatsApp messages are already enriched with page/product context** by `enrichWhatsAppLinks()`, which appends `Product/page: <H1>` and `Source page: <path>` to every `wa.me` link's prefilled text site-wide.
- **RFQ form (`contact.html`) already reads and prefills from URL query params** (`product`, `port`, `quantity`, `incoterm`, `packing`, `container`, `reference`) via an inline script — used successfully today by the article buyer-path and by `quote-calculator.js`'s handoff.
- **The trust→RFQ pattern (Part 41) is already implemented consistently**: `buyer-security.html`, `export-documentation.html`, `quality-control.html`, and all three calculators (`quote-calculator.html`, `packing-calculator.html`, `port-transit-calculator.html`) each end in a page-appropriate CTA block, and every calculator carries an honest "reference/planning only — not a commitment" disclaimer rather than a fabricated guarantee.
- **The product-page CTA hierarchy already matches the phase's own recommendation**: gold/filled "Request Pricing" (primary) → outlined "Request Sample" (secondary) → WhatsApp (tertiary), repeated consistently at the top and bottom of the page.
- **The sticky WhatsApp FAB is already implemented safely**: it is hidden while the in-hero WhatsApp button is visible (via `IntersectionObserver`, no scroll-jank) and appears only once scrolled past, so it never competes with the primary CTA, and it is positioned `bottom:95px` — deliberately offset above whatever else sits at the true bottom of the viewport.
- **`sample-request.html` already has good process transparency**: a 4-step "what happens after you submit" sequence, a visible "no courier charge, no dispatch confirmed by submitting" disclaimer, and a success panel with a reference ID.

Treating these as broken and rebuilding them would violate the phase's own non-negotiable rule against redoing settled work. They are recorded here as the baseline and are **not** modified.

## Real Gaps Found (Evidence-Based)

### Gap 1 — Product/category CTAs do not pass product context into the RFQ or sample forms (P0)

Measured directly: **0 of 84 English product pages** pass a `?product=` (or any) query parameter on their "Request Pricing" / "Request Sample" CTAs — every one links to the bare `contact.html#inquiry-form` or `sample-request.html`. This is despite the exact mechanism already existing and working for articles and the quote calculator (see above). The result: a buyer who has already selected a specific product (e.g. "1121 Golden Sella Basmati") and clicks "Request Pricing" lands on a form that has forgotten which product they were looking at, and must find it again in a 20-option dropdown that does not even list all 84 SKUs by name — this is precisely the friction Part 9 and Part 11 of the brief describe.

`sample-request.html` has the same gap: it presents 8 generic category buttons with no way to arrive pre-selected, so a buyer coming from, say, `black-cumin-seeds-nigella-exporter.html` must manually figure out that "Spices" is the closest matching button.

**Root cause**: the CTA hrefs on product pages were never updated to use the parameter-passing convention that the article/calculator code paths already use; `contact.html`'s dropdown also only covers ~20 broad categories, not all 84 specific product names, so even a naive fix (just adding `?product=<full product name>`) would silently fail to preselect anything for the majority of products unless the dropdown-matching logic is also made more forgiving.

### Gap 2 — RTL breadcrumb chevrons point the wrong direction on every Arabic page (P1)

`.jft-breadcrumb` (`jft-design-system.css:235`) is an unmodified `display:flex` row containing `Home <i class="fa-solid fa-chevron-right"></i> Products <i class="fa-solid fa-chevron-right"></i> ...`. On Arabic pages (`<html dir="rtl">`), the flex row correctly reverses visually (Home renders on the right, later crumbs progress leftward, matching Arabic reading order) — but the chevron glyph itself is a static rightward arrow, so it visually points back toward the already-visited crumb instead of forward in the direction of reading progression. This is present on every single Arabic page that uses `.jft-breadcrumb` (homepage, all product pages, all utility pages) — a genuine, previously-uncaught RTL defect matching Part 28's explicit callout for directional icons.

## Findings Considered and Deliberately Not Acted On

- **Homepage hero CTA order** (`index.html`): primary CTA is "Browse Products", secondary is "Request Export Quote" — the opposite order to the brief's illustrative example. This is a defensible choice for a first-time, low-intent homepage visitor (DISCOVER stage) rather than a defect, and there is no measured evidence of harm. Left unchanged; documented as a P3/hypothesis only (see main report).
- **Product comparison tool** (Part 19): no evidence was found that buyers are struggling to distinguish variants (all 84 products already carry a spec table with broken %, grain length, packing, etc. directly on the page). Not built — documented as a future opportunity requiring real evidence (e.g. search-console query data on comparison terms) before investment.
- **Category-page CTA context-passing**: deliberately *not* extended to the 10 category pages' "Request Pricing" links. A category page represents interest in a whole commodity group, not one SKU; forcing a `?product=` guess (e.g. "Rice") would fuzzy-match the *first* rice option in `contact.html`'s dropdown regardless of which grade the buyer actually wants — a misleading preselection is worse than none. Category CTAs are left pointing at the bare form.
- **Sticky CTA additions elsewhere**: the product-page WhatsApp FAB already covers this need safely; no additional sticky bars were added on other page types, per the brief's own caution against adding sticky UI without justification.
- **Header "Fruits" label for the raisins category**: a pre-existing mismatch already identified and deliberately deferred in Phase 10; still out of scope here (not a Phase 11 objective).
- **New analytics/tracking**: none added — analytics already exists and was audited, not rebuilt, per Part 30.

## Buyer Journey Table (representative pages)

| Page | Next action obvious? | CTA above fold? | Trust before ask? | Friction |
|---|---|---|---|---|
| Homepage | Yes — dual hero CTA | Yes | Trust tag in hero (Star Export House/ISO), fuller trust below fold | None found |
| `products.html` | Yes — category browse + filter | Yes | — | None found |
| Category pages (10) | Yes — product cards → CTA | Yes | Selection-criteria copy before CTA | None found |
| Product pages (84) | Yes — 3-tier CTA | Yes | Cert strip on page | **Gap 1**: context lost on click |
| `contact.html` | Yes — single form | Yes | Cert strip + FAQ before/beside form | None found once Gap 1 is fixed upstream |
| `sample-request.html` | Yes | Yes | Process steps shown | **Gap 1**: no product preselection |
| `buyer-security.html` | Yes — 3 CTAs at end | N/A (informational page) | Entire page is trust content | None found |
| `export-documentation.html` | Yes — 2 CTAs at end | N/A | Entire page is trust content | None found |
| `quality-control.html` | Yes — CTA in hero + mid + end | Yes | Accreditation tags in hero | None found |
| Calculators (3) | Yes — CTA after result | N/A (tool page) | Honest "reference only" disclaimers | None found |
| `shipment-tracker.html` | Yes — WhatsApp/contact CTA | N/A | — | None found |
| Arabic pages (any) | Yes | Yes | Yes | **Gap 2**: breadcrumb chevron direction |

Full per-page notes are in `reports/phase11-buyer-journey-audit.json`.

## What Happens Next

Sections 3 (scoring) and implementation are covered in `reports/phase11-commercial-ux-2026-08-27.md`, produced after this audit and after the two evidence-based fixes above were implemented.
