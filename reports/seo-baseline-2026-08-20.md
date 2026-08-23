# JFT Agro SEO, GEO and AEO Baseline

**Audit date:** 20 August 2026  
**Scope:** current working tree and production at `https://jftagro.com/`  
**Method:** complete static audit, complete production sitemap status crawl, rendered-browser checks, mobile Lighthouse and performance trace, localization audit, internal-link review, and current public SERP sampling.  
**Ranking disclaimer:** this report identifies opportunities and technical eligibility; it does not promise rankings.

## Executive outcome

The site has a strong technical foundation. Production serves all **1,428 sitemap URLs as direct HTTP 200 responses**, and the local project contains exactly **1,428 indexable pages and 1,428 sitemap URLs**. The audit found no missing canonicals, canonical mismatches, invalid JSON-LD, broken local assets, invalid H1 counts, sitemap/noindex conflicts, duplicate titles, or duplicate descriptions.

The largest growth constraint is not crawlability. It is the gap between broad catalogue coverage and the evidence, authority, demand validation, native-language review, original market information, and page-level performance data needed to earn durable non-brand visibility.

The highest-impact safe code correction in this pass synchronized localized visible breadcrumb labels with localized `BreadcrumbList` schema on **1,170 pages**. Previously, localized breadcrumb URLs were correct but schema labels remained English; several labels were also truncated mid-word. No visible content, URL, canonical, hreflang, or routing changed.

## A. Technical SEO audit

| Severity | Scope | Finding | Why it matters | Recommended fix | Status |
|---|---|---|---|---|---|
| Passed | 1,428 production URLs | Every sitemap URL returns direct HTTP 200 | Clean discovery and no redirect waste inside sitemap | Continue monitoring | Validated |
| Passed | Whole site | Indexable-page count equals sitemap URL count | No detected sitemap coverage gap | Continue monitoring | Validated |
| Passed | Whole site | Self-canonicals, one H1, language declarations and valid JSON-LD present | Strong indexation and parsing baseline | Preserve | Validated |
| Passed | Domain variants | HTTP and `www` permanently redirect to HTTPS apex | Consolidates duplicate hosts | Preserve | Validated |
| Passed | Error handling | Unknown URL returns true HTTP 404 | Prevents soft-404 indexing | Preserve | Validated |
| Passed | Homepage | Mobile Lighthouse SEO 100; accessibility 97; best practices 100 | Strong rendered technical baseline | Address the single accessibility failure separately | Validated |
| Passed | Homepage | Lab LCP 1.59 s and CLS 0.01 on Fast 4G/4x CPU | Good mobile lab experience | Monitor field CWV in Search Console | Validated |
| Low | 47 localized metadata fields | 24 titles and 23 descriptions exceed internal audit heuristics | Snippets may truncate, but length is not a search-engine error | Review for clarity with native speakers; do not trim mechanically | Open |
| Medium | 1,170 localized pages | Breadcrumb schema names did not match visible localized breadcrumbs | Weak entity consistency and localized structured-data quality | Synchronize schema to existing visible labels | **Fixed** |
| Medium | International programme | Ten languages cover almost the full catalogue, but native commercial review and query demand are not documented in-repo | Technically valid localization can still underperform if market fit or language quality is weak | Require native review plus Search Console country/query evidence | Open |
| Medium | Market/data articles | Dated policy, duty and price pages need recurring source review | Stale trade information damages trust and search usefulness | Quarterly for regulations; monthly for market data | Open |
| Medium | Product schema | Product pages use WebPage, Breadcrumb and FAQ schema but generally not Product | Not a technical error; unsupported commercial markup would be worse | Add Product only when visible verified product attributes can be maintained | Open |
| High | Authority | No repository audit can prove backlink quality, branded entity coverage, or third-party reputation | Authority is a primary competitive gap | Build evidence-led digital PR and measure referring domains | Open/external |
| High | Measurement | Exact queries, positions, CTR, indexed state and organic enquiries are unavailable without first-party console/analytics exports | Priorities cannot learn from performance without data | Connect GSC/Bing/analytics exports to a monthly page-query model | Open/external |

Google states that titles and descriptions have no fixed element-length limit and may be truncated to device width, so the 47 length flags are editorial review items rather than blockers. The current 2.17 MB, 1,428-URL sitemap is safely below Google's 50 MB and 50,000-URL limits. Splitting it is optional for Search Console reporting, not technically required.

## B. Keyword opportunity map

The ranked database is in [seo-opportunities-top-100-2026-08-20.csv](seo-opportunities-top-100-2026-08-20.csv). It contains exactly 100 opportunities with product/cluster, keyword, market, language, intent, qualitative competition, relative opportunity score, target URL, page status and next action.

The scores are prioritization estimates, not Google scores or paid-tool search-volume estimates. Exact current rank and query demand must come from Search Console and a chosen keyword dataset.

Top opportunity themes:

1. IR64 grade intent: 5%, 10%, bulk supply and West Africa.
2. Basmati variety/form intent: 1121, 1509, 1718, 1401; raw, steam and sella.
3. High-value products: wheat flour/atta, maize, cumin, coriander, turmeric, chilli, sesame, groundnut, chickpeas, mung, toor dal and psyllium.
4. Decision content: specifications, COA review, inspection, documents, packing, payment safety and exporter verification.
5. Controlled market/logistics pages only where demand, serviceability and unique first-hand facts are confirmed.

## C. Competitor gap report

This is a public-SERP sample, not a complete top-20/rank/backlink dataset. A complete competitor movement report requires a repeatable rank source and backlink provider.

| Competitor | Observed query cluster | What it currently does well | JFT gap/opportunity |
|---|---|---|---|
| `ir64.com` / Haji Rice | IR64 supplier/exporter | Single-topic domain, prominent grade choices, market/port language, direct quote/sample paths, deep IR64 FAQ | Consolidate JFT's IR64 cluster with stronger hub-to-grade links, original evidence and buyer decision content; do not copy claims |
| Alstoe Exports | Basmati exporter India | One focused Basmati hub covering varieties/forms and quick specifications | Make the 1121 hub the clear parent and improve form/variety comparison paths |
| SHC Global Trade | Basmati and agro exporter | Visible company registrations, named location, ports and concise specification/entity information | Publish only genuine current registration evidence, ownership/reviewer identities and operational proof |
| Voyager Exim | Rice, spices and pulses | Clear buyer promise, category segmentation, MOQs and document language | Clarify JFT's buyer pathways by product category and qualification step without unsupported blanket MOQs |
| Botanika Bharat | Basmati supplier | Broad variety terminology and sourcing-region coverage | Use precise semantic variety coverage while avoiding repetitive wholesaler/exporter stuffing |
| TradeIndia/Zauba | Product/exporter discovery | Marketplace/data authority and price/shipment intent | Win informational and specification intent with original guides; do not imitate marketplace inventory pages |

Current SERP sampling also surfaced JFT's wheat-flour page for the relevant exporter query, showing that precise product pages can be discovered. Exact rank was not asserted because search results vary by location and time.

## D. International SEO map

| Language | Folder | Hreflang | Current coverage | Primary strategic market | Decision |
|---|---|---|---:|---|---|
| English | `/` | `en` + `x-default` | 139 English indexable pages | Global | Primary source set |
| Arabic | `/ar/` | `ar` | Broad | Gulf/MENA | Retain; require native commercial QA |
| Spanish | `/es/` | `es` | Broad | Spanish-speaking import markets | Retain; validate demand by country |
| French | `/fr/` | `fr` | Broad | Francophone Africa/Europe | High-priority native review |
| Indonesian | `/id/` | `id` | Broad | Indonesia | Validate product-market demand |
| Malay | `/ms/` | `ms` | Broad | Malaysia | Validate product-market demand |
| Portuguese | `/pt/` | `pt` | Broad | Lusophone markets | Validate country-specific demand |
| Russian | `/ru/` | `ru` | Broad | Russia/CIS | Retain; keep policy content current |
| Sinhala | `/si/` | `si` | Broad | Sri Lanka | Validate import-policy and demand fit |
| Thai | `/th/` | `th` | Broad | Thailand | Validate exporter-versus-local-supply intent |
| Vietnamese | `/vi/` | `vi` | Broad | Vietnam | Validate product-market demand |

Do not add Chinese, Korean, Japanese or new country folders merely to increase URL count. Google recommends separate language URLs and hreflang, but also uses visible page content to determine language and warns against automatic language redirects. The technical architecture already follows the separate-URL model; quality governance is now the priority.

## E. Content roadmap

### First 30 days

- Export and join Search Console page/query/country/device data with enquiry conversions.
- Refresh the IR64 hub/grade cluster and Basmati hub using verified, visible facts.
- Native-review the top five landing pages in Arabic and French.
- Refresh rice-duty, policy and 2026 market pages against current primary sources.
- Publish a verified company/entity evidence page update using genuine registration and operational proof.

### Days 31–60

- Build original, cited buyer resources for sample approval, packing-list review and document comparison.
- Improve cumin, coriander, turmeric, chilli, sesame, groundnut, chickpea, mung and psyllium clusters.
- Earn relevant citations through trade bodies, logistics partners, event listings and commodity publications.
- Test one market page only where GSC demand, serviceability and unique information converge.

### Days 61–90

- Expand the best-performing cluster based on impressions, CTR and enquiries.
- Prune, consolidate or differentiate pages only after query-level cannibalization evidence.
- Review localized pages by commercial performance; do not use noindex or redirects without approval.
- Publish an original market/logistics dataset or inspection template designed to earn citations.

## F. Internal-link plan

| Source | Target | Suggested anchor theme | Reason |
|---|---|---|---|
| IR64 export guide | 5% and 10% IR64 pages | grade-specific IR64 options | Moves informational users to exact buying intent |
| 1121 hub | raw, steam and white-sella pages | 1121 processing forms | Establishes parent-child cluster |
| Basmati comparison guide | 1121, 1509, 1718 and 1401 pages | variety decision anchors | Supports comparison-to-product journey |
| Africa trade hub | IR64, broken rice and maize pages | products commonly evaluated for African markets | Deepens real market-product paths |
| UAE trade hub | Basmati, atta, spices and pulses | UAE sourcing categories | Connects market and product intent |
| Europe trade hub | spice guides, documentation and quality control | EU buyer compliance resources | Builds trust path |
| Wheat flour page | maida and semolina pages | related wheat products | Cross-sell without keyword overlap |
| Cumin product page | cumin outlook | cumin market outlook | Adds informational support |
| Coriander product page | coriander grade guide | coriander grade comparison | Helps specification decisions |
| Turmeric product page | variety guide and market outlook | turmeric buyer guides | Supports topic authority |
| Groundnut product page | groundnut buyer guide | groundnut testing and shipment controls | Adds risk-control context |
| Quality control | COA and container inspection guides | laboratory and loading controls | Strengthens evidence cluster |
| Export documentation | bill of lading, LC/TT and specification guides | export document guides | Makes the documentation hub useful |

Anchor text should vary naturally. The products page already exposes a static crawlable list of product URLs, so the issue is contextual prominence, not orphan discovery.

## G. Priority technical fix list

1. **Completed:** synchronize localized visible breadcrumb labels and JSON-LD labels.
2. Add an automated assertion for visible breadcrumb/schema label equality to the main audit.
3. Native-review the 47 long localized snippet fields for clarity; do not enforce arbitrary character limits.
4. Monitor field Core Web Vitals; lab performance is already good.
5. Add Product schema only where verified visible data supports it and maintenance ownership is clear.
6. Consider sitemap segmentation by content type/language only for reporting convenience.
7. Keep accurate `lastmod`; never touch dates without substantive change.

## H–I. SEO score before and after

This internal score is a prioritization framework, not a Google ranking score.

| Dimension | Before | After | Evidence |
|---|---:|---:|---|
| Technical SEO | 96 | 96 | Complete 200 crawl, canonical and sitemap alignment |
| Content quality | 78 | 78 | Broad coverage; freshness and original evidence gaps remain |
| Search intent | 81 | 81 | Strong product specificity; market and buyer paths need validation |
| Internal links | 74 | 74 | Crawlable catalogue exists; contextual clustering can improve |
| Structured data | 82 | 89 | 1,170 localized breadcrumb-label mismatches fixed |
| Metadata | 97 | 97 | Unique/complete; 47 editorial length reviews remain |
| Image SEO | 90 | 90 | No missing alt/dimension flags; original proof imagery remains an opportunity |
| International SEO | 78 | 80 | Technical hreflang strong; schema localization fixed; native QA still required |
| Page experience | 90 | 90 | Mobile lab LCP 1.59 s and CLS 0.01; field data unavailable |
| Authority/entity | 55 | 55 | Needs third-party citations and verifiable first-party evidence |
| Conversion readiness | 86 | 86 | Quote, contact, sample and buyer-resource paths present |
| **Weighted baseline** | **82/100** | **83/100** | Improvement is deliberately modest; one systemic issue fixed |

## Validation evidence

- Local audit: 1,728 renderable files, 1,428 indexable pages, 1,428 sitemap URLs.
- Production crawl: 1,428/1,428 direct HTTP 200; p50 1.093 s, p95 1.231 s, maximum 1.652 s; zero retries.
- Homepage rendered metadata: unique title/description, self-canonical, one H1, 12 hreflang links, valid Organization/WebSite/FAQ schema, 60 images with alt and dimensions.
- Wheat-flour rendered page: self-canonical, one H1, 12 hreflang links, visible specification table, visible FAQ, WebPage/Breadcrumb/FAQ schema.
- Arabic wheat-flour rendered page: `lang="ar"`, `dir="rtl"`, self-canonical, Arabic title/H1 and 12 hreflang links.
- Mobile Lighthouse homepage: SEO 100, best practices 100, accessibility 97.
- Mobile performance trace: LCP 1.59 s, CLS 0.01; no field CrUX data returned for the page.

## Data required for the next evidence-based cycle

- Google Search Console: 16 months of page/query/country/device data and indexing exports.
- Bing Webmaster Tools: search performance, crawl and IndexNow history.
- Analytics/CRM: organic landing page to qualified enquiry and product/country outcome.
- Backlink dataset: referring domain, topical relevance, link target and lost/new history.
- Verified company evidence register: registration/certification holder, number, scope, issuer and validity.
- Native reviewer sign-off for priority language-market pairs.

## Reference standards

- [Google: multilingual and multi-regional sites](https://developers.google.com/search/docs/advanced/crawling/managing-multi-regional-sites)
- [Google: localized versions and hreflang](https://developers.google.com/search/docs/advanced/crawling/localized-versions)
- [Google: build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google: title-link guidance](https://developers.google.com/search/docs/appearance/title-link)
- [Google: snippet and meta-description guidance](https://developers.google.com/search/docs/appearance/snippet)
- [Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)

