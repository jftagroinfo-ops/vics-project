# Google Search Console Indexing Remediation

**Date:** 17 August 2026  
**Property:** `https://jftagro.com/`

## Search Console snapshot supplied by the site owner

| Exclusion reason | Reported URLs | Initial assessment |
|---|---:|---|
| Not found (404) | 5,571 | Historical URL inventory; examples required before safe redirect decisions |
| Alternative page with proper canonical | 860 | Usually expected duplicate consolidation |
| Duplicate without user-selected canonical | 254 | Legacy/query variants need consolidation |
| Excluded by `noindex` | 39 | Expected subset of intentional exclusions unless examples show otherwise |
| Page with redirect | 21 | Expected when old URLs permanently redirect |
| Crawled – currently not indexed | 941 | Quality/duplication evaluation; examples and query data required |
| Duplicate, Google chose different canonical than user | 444 | Re-evaluation pending; legacy duplicates were still accessible |
| Discovered – currently not indexed | 87 | Crawl scheduling, not necessarily a technical defect |

## Verified current-state facts

- The canonical sitemap contains 1,378 unique, intentionally indexable URLs.
- The source audit contains the same 1,378 indexable pages and no sitemap/noindex conflicts.
- Indexable pages have self-canonicals and the sitemap uses the HTTPS apex hostname.
- `www`, `/index.html`, localized `/index.html` and the historical `?j=` homepage copies already return HTTP 301.
- Exactly 300 HTML documents intentionally use `noindex`, including error pages, thank-you pages, untranslated placeholders, legal duplicates and retired content. They are excluded from the sitemap.
- Current internal-link and sitemap audits do not expose thousands of broken destinations. Therefore the 5,571 total cannot represent the current canonical page inventory.

## Root cause evidence

Google’s public results still expose URLs from the previous website/catalogue architecture, including:

- `/?post_type=product`
- `/?product=senna-leaves`
- `/?product=grey-millet`
- `/?product=raisins`
- `/?product=sesame-seeds`
- `/products/20325959`
- `/index.html`

The query URLs rendered the homepage, creating duplicate clusters. The hosted-store path is an obsolete catalogue route. Search Console retains historical crawl records until Google revisits or drops those URLs, so totals do not fall immediately after a correction.

## Implemented remediation

The Cloudflare Worker now applies permanent, destination-specific redirects for:

1. legacy `post_type=product` and `product=...` homepage URLs;
2. the former `/products/20325959` catalogue route;
3. nine retired article filenames across English and all locale folders, covering 96 former meta-refresh documents;
4. known product aliases such as raisins, grey millet, senna leaves and sesame seeds;
5. exact current product slugs when a matching static product page exists.

Current functional parameters remain available:

- catalogue `q` and `cat` filters;
- RFQ/contact prefill parameters;
- campaign attribution parameters such as UTM and click IDs.

Unknown 404s are not redirected to the homepage. A blanket redirect would obscure genuine missing URLs and can be treated as a soft 404.

## Search Console follow-up

1. Open **Not found (404)** and export the example table as CSV, including URL and last-crawled date.
2. Export examples for **Google chose different canonical**, **Crawled – currently not indexed**, and **Excluded by noindex**.
3. Compare each example to the current sitemap and redirect policy.
4. Add redirects only where an old URL has a closely equivalent current destination; leave genuinely removed junk URLs as 404/410.
5. Start validation for a reason only after its sampled URLs have been classified and corrected. Do not start validation for intentional `noindex` or expected canonical alternatives.
6. Use URL Inspection on a small representative set: homepage, one product, one translated product and one new buyer guide.

## Expected timing

Deployment changes take effect at the edge immediately, but Search Console counts change only after Google recrawls affected URLs. Validation and reprocessing can take days or weeks and do not guarantee indexing. The Page Indexing report is a historical crawl view, not a live count of current website files.

## Production verification

- Cloudflare Worker version: `a96f4813-f2c0-48e6-b0d0-a4674dab17bc`
- Canonical sitemap crawl: **1,378 checked, 1,378 HTTP 200, zero failures**
- Verified one-hop HTTP 301 responses for the publicly visible legacy product queries and archive path.
- Verified English articles sharing filenames with retired locale placeholders remain HTTP 200.
- Verified only the retired locale article paths redirect to their current English replacements.
- Verified catalogue filters, RFQ prefill parameters and campaign parameters continue to return HTTP 200.
