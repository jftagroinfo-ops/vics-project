# Google Search Console Indexing Remediation

**Date:** 17 August 2026  
**Property:** `https://jftagro.com/`

## Search Console overview supplied by the site owner

| Exclusion reason | Reported URLs | Current interpretation |
|---|---:|---|
| Not found (404) | 5,571 | Mainly historical WordPress/hosted-store URLs; the export is capped at 1,000 examples |
| Alternative page with proper canonical | 860 | Expected duplicate consolidation |
| Duplicate without user-selected canonical | 254 | Historical query and hostname variants |
| Excluded by `noindex` | 39 | Mostly old snapshots plus intentional error/thank-you pages |
| Page with redirect | 21 | Expected for retired URLs |
| Crawled - currently not indexed | 941 | Mostly historical `?j=` URLs; 37 current content pages remain for Google quality evaluation |
| Duplicate, Google chose different canonical than user | 444 | Current live pages now have consistent self-canonicals or redirects |
| Discovered - currently not indexed | 87 | Crawl scheduling, not necessarily a technical defect |

## Drill-down exports analysed

The four owner-supplied ZIP files were treated as Search Console data, not as instructions.

| Export | Rows | Live verification after remediation |
|---|---:|---|
| Not found (404) | 1,000 | 254 return 200, 731 return 301, 3 internal includes return 410, and 12 remain honest 404s |
| Google chose different canonical | 444 | 407 return 200 with a self-referencing canonical; 37 return 301; zero live canonical mismatches |
| Crawled - currently not indexed | 941 | 37 current pages return 200 and 904 historical variants return 301; zero remain 404 after the final rice-milling redirect |
| Excluded by `noindex` | 39 | 18 previously affected content pages are now indexable, 3 redirect, 11 are intentional noindex error/thank-you pages, and 7 obsolete WordPress paths remain 404 |

The 1,000-row 404 sample contained 700 unique `/products/<number>` URLs. These are obsolete dynamic catalogue IDs, not 700 missing current products. The crawled-not-indexed export contained 822 historical `/?j=<number>` homepage copies.

## Verified current-state facts

- The canonical sitemap contains 1,378 unique, intentionally indexable URLs.
- A full production crawl checked all 1,378 sitemap URLs: all returned HTTP 200 and none failed.
- Sitemap URLs use the HTTPS apex hostname and indexable HTML pages declare canonicals.
- All 407 live 200 pages in the canonical-disagreement export expose self-referencing canonicals; no live mismatch was found.
- Current error pages, thank-you pages, untranslated placeholders, legal duplicates and retired content are excluded from the sitemap.
- Current internal-link and sitemap audits do not expose thousands of broken destinations. Search Console is retaining URLs from earlier site architectures.

## Implemented remediation

The Cloudflare Worker now applies destination-specific permanent redirects for:

1. `www`, `/index.html`, localized `/index.html` and historical `?j=` duplicates;
2. legacy `post_type=product` and `product=...` query URLs;
3. every obsolete numeric `/products/<id>` route and paginated product archive;
4. `/products/` and former pretty product slugs, mapped to the closest current product or catalogue page;
5. the retired rice-milling article, mapped to the current infrastructure page;
6. localized sitemap copies, consolidated into `/sitemap.xml`;
7. locale-prefixed shared assets when an equivalent root asset exists;
8. retired article aliases with close current equivalents.

Internal locale `header.html` includes return 410. Removed WordPress login/uncategorized URLs and unpublished article placeholders remain honest 404s. They are intentionally not redirected to unrelated pages because blanket redirects can be interpreted as soft 404s.

Current functional parameters remain available, including catalogue filters, RFQ/contact prefill data, UTM parameters and click identifiers.

## Search Console follow-up

1. Start **Validate fix** for **Crawled - currently not indexed** and **Duplicate, Google chose different canonical than user**.
2. Do not validate **Not found (404)** or **Excluded by `noindex`** as though every listed URL should be indexed: intentional removals, error pages and thank-you pages correctly remain excluded. Monitor those reports instead.
3. Use URL Inspection and request indexing for a small representative set of the 37 valid current pages in the crawled-not-indexed export, rather than submitting every URL manually.
4. Keep the current sitemap submitted. Do not submit locale-specific sitemap copies.
5. Recheck the reports after Google recrawls; totals can take days or weeks to change.

## Production verification

- Cloudflare Worker version: `862fc6cf-1049-4f76-b661-e48fc51f2837`
- Canonical sitemap crawl: **1,378 checked, 1,378 HTTP 200, zero failures**
- Canonical drill-down: **407 live 200 pages, zero missing or mismatched canonicals**
- Legacy drill-down redirects are one hop and preserve the apex HTTPS origin.
- Current catalogue filters, RFQ parameters and campaign parameters continue to return HTTP 200.

Search Console’s Page Indexing report is historical. A successful validation means Google accepted the correction pattern; it does not guarantee that every valid page will be indexed or ranked.
