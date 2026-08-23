# Search Console Performance Analysis

- Export date range: 19 May 2026-18 Aug 2026
- Total clicks: 286
- Total impressions: 10,410
- Weighted CTR: 2.75%
- Impression-weighted average position: 10.03
- Exported non-brand query rows: 188
- Visible non-brand query clicks/impressions: 21/1,003
- Brand query rows excluded: 5
- Page rows: 327; country rows: 141; device rows: 3

## Highest observed page opportunities

| Score | Page | Impressions | CTR | Position | Estimated CTR-gap clicks |
|---:|---|---:|---:|---:|---:|
| 100.0 | https://jftagro.com/blog-cumin-jeera-price-outlook-2026.html | 1729 | 0.4% | 6.99 | 79.53 |
| 78.8 | https://jftagro.com/packing-calculator.html | 1444 | 0.76% | 6.9 | 61.23 |
| 20.7 | https://jftagro.com/blog-import-duty-indian-rice-by-country.html | 325 | 1.23% | 7.98 | 12.25 |
| 18.4 | https://jftagro.com/blog-india-vs-thailand-rice-comparison.html | 381 | 2.36% | 6.99 | 10.06 |
| 18.4 | https://jftagro.com/blog-turmeric-finger-export-india-2026.html | 231 | 0.43% | 7.83 | 10.56 |
| 16.2 | https://jftagro.com/port-transit-calculator.html | 528 | 0.76% | 16.05 | 7.81 |
| 16.1 | https://jftagro.com/ms/blog-red-chilli-teja-export-india-2026.html | 177 | 0.0% | 7.34 | 8.85 |
| 16.0 | https://jftagro.com/blog-psyllium-husk-export-india-2026.html | 230 | 1.3% | 7.12 | 8.51 |
| 15.1 | https://jftagro.com/about.html | 245 | 4.9% | 4.23 | 7.59 |
| 13.9 | https://jftagro.com/blog-basmati-export-guide.html | 143 | 0.0% | 8.67 | 7.15 |
| 12.3 | https://jftagro.com/uae-trade.html | 601 | 1.66% | 14.29 | 4.29 |
| 12.2 | https://jftagro.com/privacy.html | 78 | 0.0% | 4.96 | 6.24 |
| 11.9 | https://jftagro.com/ms/port-transit-calculator.html | 112 | 0.0% | 9.06 | 5.6 |
| 11.7 | https://jftagro.com/products.html | 110 | 0.0% | 8.55 | 5.5 |
| 11.5 | https://jftagro.com/certificates.html | 93 | 2.15% | 4.87 | 5.44 |

## Highest visible non-brand query opportunities

| Query | Impressions | CTR | Position | Candidate target |
|---|---:|---:|---:|---|
| 1 million cif price | 136 | 0.0% | 9.8 | https://jftagro.com/quote-calculator.html |
| fob calculator | 212 | 2.36% | 8.42 | https://jftagro.com/quote-calculator.html |
| how many 50kg bags of rice in a 40ft container | 31 | 0.0% | 7.61 | https://jftagro.com/packing-calculator.html |
| how many 25kg bags of rice in a 20ft container | 29 | 0.0% | 8.59 | https://jftagro.com/packing-calculator.html |
| சீரகம் விலை இன்று | 18 | 0.0% | 7.5 | https://jftagro.com/blog-cumin-jeera-price-outlook-2026.html |
| cif value calculator | 16 | 0.0% | 9.5 | https://jftagro.com/quote-calculator.html |
| சீரகம் விலை | 16 | 0.0% | 7.0 | https://jftagro.com/blog-cumin-jeera-price-outlook-2026.html |
| how many 25kg bags in a 20ft container | 15 | 0.0% | 8.4 | https://jftagro.com/packing-calculator.html |
| how many 25kg bags in a 40ft container | 13 | 0.0% | 6.77 | https://jftagro.com/packing-calculator.html |
| 1 million cif price in india | 12 | 0.0% | 9.25 | https://jftagro.com/quote-calculator.html |
| rice export from india to uae | 7 | 0.0% | 5.0 | Needs Query + Page API export |
| indian rice re-export dubai | 22 | 0.0% | 16.05 | https://jftagro.com/uae-trade.html |
| cumin price per kg india 2026 | 9 | 0.0% | 9.89 | https://jftagro.com/blog-cumin-jeera-price-outlook-2026.html |
| cif export calculator | 4 | 0.0% | 3.5 | https://jftagro.com/quote-calculator.html |
| pusa 1509 vs 1121 | 6 | 0.0% | 8.67 | Needs Query + Page API export |

## Decision

This export predates the 20 August production SEO release, so it is the pre-release performance baseline. Preserve the newly deployed pages long enough to collect comparable post-release data. Immediate priorities are measurement validation and snippet monitoring for the calculator, packing and cumin clusters; do not rewrite the site again from this baseline alone.

## Data boundary

Google exported Query, Page, Country and Device as separate tables. Their totals are valid independently, but the rows cannot be joined to claim which query, country or device produced a specific page result. Candidate targets are transparent intent-based suggestions, not observed query-to-page mappings. A Search Analytics API export using Query + Page (+ Country/Device when needed) is required for that attribution. Search Console also suppresses some low-volume queries, so visible query totals do not equal site totals.
