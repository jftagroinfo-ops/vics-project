# Buyer brief card visibility fix

Date: 2026-08-22  
Production version: `576b2681-9eb7-43b3-b123-4c39c74e46c3`

## Cause

Fifteen English product-page buyer briefs placed `.jft-dark-card` components on white section backgrounds. The component was designed for dark sections, so its white headings and translucent white paragraphs became effectively invisible. The global ultra-wide heading rule also made these explanatory brief headings unnecessarily dominant.

## Implementation

- Preserved all product-specific buyer and SEO content.
- Added a narrowly scoped light-card presentation for the fifteen brief grids identified by their existing structural marker.
- Changed the cards to white surfaces with visible navy headings, grey-green body text, borders and restrained shadows.
- Changed the grid to responsive `auto-fit` columns so three- and four-card briefs use the available space naturally.
- Reduced only these brief headings to a maximum of `2.65rem`; other section headings and legitimate dark-section cards are unchanged.
- Added `scripts/validate_buyer_brief_cards.py` to enforce the expected fifteen-page scope and required CSS rules.
- No localized page contains this newer buyer-brief block, so no translation duplicate required modification.

## Validation

- Buyer-brief regression validator: 15 pages passed.
- Full source link crawl: 1,745 HTML files, 0 unique broken internal links.
- Wrangler dry run: passed.
- Production stylesheet: HTTP 200 and contains the scoped correction.
- Live browser validation: all 15 pages returned HTTP 200 with 0 failures.
- Computed card background: `rgb(255, 255, 255)`.
- Computed card heading colour: `rgb(26, 60, 52)`.
- Computed card paragraph colour: `rgb(89, 100, 95)`.
- Ultra-wide brief heading size: `42.4px` in the validation viewport.

