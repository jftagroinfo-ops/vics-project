# JFT Agro SEO System Discovery Report

Date: 2026-08-20  
Scope: current working tree, production deployment, completed SEO evidence and owner-supplied Search Console performance export  
Decision boundary: discovery only; no new mass implementation was started before this report

## Executive decision

JFT Agro already has a strong public-site SEO implementation. The missing layer described by the new specification is not another metadata or content rewrite: it is a persistent, historical, configurable intelligence system that ingests first-party and permitted external data, calculates evidence-aware opportunities, keeps a task/change history and produces a private command-center view.

The recommended architecture is a local/server-side Python SEO application with SQLite storage, configuration files, CLI jobs and generated private reports. It should reuse the existing validators and keep all heavy data and dashboards out of the public static frontend. Automatic publishing must remain disabled; low-risk changes should be proposed as reviewable patches with snapshots and rollback metadata.

## 1. Current technology stack

- Static HTML/CSS/JavaScript website; no `package.json`, frontend framework, CMS or application database.
- Cloudflare Worker entry point: `.cloudflare/worker.js`.
- Cloudflare static assets binding configured in `wrangler.jsonc`; `html_handling: none` and `run_worker_first: true`.
- Production custom domains: `jftagro.com` and `www.jftagro.com`, with apex canonicalization in the Worker.
- Python automation and validation scripts under `scripts/`.
- JSON/CSV content and governance records under `data/`.
- GA4 consent-aware measurement ID `G-MWZ2ZWZP4G` in `jft-conversion.js`.
- Contact/lead submission currently uses a browser-side Web3Forms endpoint and access token.
- No authenticated SEO admin interface, persistent SEO database, unified job log or scheduler is present.

## 2. Current page count

- HTML files in the public source structure: 1,778, including 46 helpers/templates.
- Renderable audited pages: 1,732.
- Canonical indexable sitemap URLs: 1,432.
- Live production sitemap crawl: 1,432 direct HTTP 200 responses; zero failures.
- English/indexable root set: 142 URLs.
- Each of the ten configured locale folders: 129 indexable URLs.
- Nonindexable/helper/utility inventory remains deliberately outside the sitemap.

## 3. Current product pages

- 84 canonical products in `data/products.json`.
- 84 English `*-exporter.html` pages plus the separate S30 sugar supplier page: 85 English commercial product pages.
- Product landing-page equivalents exist across the ten locale folders.
- Product catalogue, product master and commercial-content validators already exist.
- Product schema is conservative; general product pages mainly use WebPage, Breadcrumb and FAQ markup because verified offer/price/availability attributes are not maintained for every product.

## 4. Current language pages

Configured indexable languages:

| Language | Folder | Indexable URLs | Governance state |
|---|---|---:|---|
| English | `/` | 142 | source/default |
| Arabic | `/ar/` | 129 | native commercial approval pending |
| Spanish | `/es/` | 129 | native commercial approval pending |
| French | `/fr/` | 129 | native commercial approval pending |
| Indonesian | `/id/` | 129 | native commercial approval pending |
| Malay | `/ms/` | 129 | native commercial approval pending |
| Portuguese | `/pt/` | 129 | native commercial approval pending |
| Russian | `/ru/` | 129 | native commercial approval pending |
| Sinhala | `/si/` | 129 | native commercial approval pending |
| Thai | `/th/` | 129 | native commercial approval pending |
| Vietnamese | `/vi/` | 129 | native commercial approval pending |

The technical localization audit reports 158 renderable pages in each locale with zero missing, fallback or high-residue pages. Ten governance records remain correctly on hold until named native review and market evidence exist.

## 5. Current country pages

Current indexable regional/market resources include:

- Africa trade hub;
- UAE trade hub;
- Europe trade hub;
- Asia trade hub;
- Nigeria/West Africa rice guide;
- Kenya/East Africa import guide;
- Bangladesh/Sri Lanka rice guide;
- India-to-Africa export guide; and
- country-oriented duty, rice-comparison and compliance guides.

Dedicated Nigeria, Saudi Arabia, Bangladesh, Sri Lanka, Kenya and Vietnam URLs are intentionally held behind documented publication gates. They must not be created until demand, importer/compliance route, serviceability and unique transactional evidence are supplied.

## 6. Current blog/content inventory

- 37 English `blog-*.html` files, of which 29 are currently in the English sitemap and the remainder are legacy redirect/helper content.
- Blog hub plus localized equivalents.
- Major clusters cover rice, specifications, inspection, documents, payment, packing, duties, market comparisons, spices, pulses, regional trade and exporter due diligence.
- 926 visible/schema-aligned FAQPage blocks.
- 83 priority cluster pages protected by automated regression assertions.
- Automatic article publishing is not an approved workflow; editorial review records correctly remain pending where a named reviewer would be claimed.

## 7. Current sitemap

- One root XML sitemap: `https://jftagro.com/sitemap.xml`.
- 1,432 unique canonical/indexable URLs.
- Current production response: HTTP 200 with XML content type.
- Sitemap and indexable-page counts are aligned.
- The sitemap is well below protocol size/URL limits; segmentation would be useful only for reporting and operational diagnosis, not technical eligibility.

## 8. Current robots

- One universal `User-agent: *` group allows crawling.
- Internal utilities, reports, scripts, audit files and non-search destinations are excluded.
- Root sitemap is declared.
- CSS, JavaScript and images are not blocked.
- No current important sitemap URL is blocked by robots.

## 9. Current canonical implementation

- Indexable pages have one self-referencing canonical.
- HTTP, `www`, `/index.html` and supported historical duplicate patterns redirect to the HTTPS apex canonical.
- Unknown paths return true HTTP 404 rather than a homepage soft redirect.
- Latest full local and production checks found no canonical mismatch among sitemap URLs.

## 10. Current hreflang

- The primary translated clusters use reciprocal language alternates plus `x-default`.
- The current technical localization validator reports no errors.
- English-only documents do not falsely claim unavailable translations.
- The system has generation/repair scripts, but language configuration is still distributed across scripts rather than owned by one central SEO configuration model.

## 11. Current schema

Observed structured-data coverage includes:

- BreadcrumbList: 1,461 objects;
- WebPage: 1,029;
- FAQPage: 926;
- Article: 266;
- WebApplication: 44;
- HowTo: 40;
- ItemList: 33; plus Organization, WebSite, Blog and limited Product/entity types.

The release audit found syntactically valid JSON-LD and visible/schema FAQ alignment. Product markup remains intentionally conservative until visible, verified commercial attributes can be maintained.

## 12. Current metadata

- Titles, descriptions, canonical tags, language declarations and social metadata are broadly complete and unique.
- The consolidated audit retains 24 title-length and 23 description-length heuristic warnings across localized pages.
- These 47 warnings are editorial review items, not search-engine errors; they must not be mechanically shortened without native review and query evidence.

## 13. Current internal linking

- The products page exposes a crawlable catalogue.
- Product, market, guide, documentation and calculator clusters have contextual-link coverage.
- 83 priority pages have enforced cluster/link assertions.
- The latest full static audit and link scan found no release-blocking broken internal links or sitemap orphans.
- The missing intelligence feature is persistent link-graph history, link equity/change comparison and a configurable recommendation queue.

## 14. Current image SEO

- 278 files are present in the main `images/` directory.
- More than 10,000 image references exist across the generated/localized HTML inventory.
- Existing audits found no systemic missing-alt or missing-dimension blocker.
- Remaining opportunity: original, authorized shipment/process/product proof imagery, modern-format coverage, duplicate-asset detection and historical image performance—not fabricated company photography.

## 15. Current technical problems and system gaps

There is no current crawl/indexability release blocker. The important gaps are:

1. 24 localized title-length editorial warnings.
2. 23 localized description-length editorial warnings.
3. No unified persistent SEO database.
4. No historical page/keyword/ranking snapshot model.
5. Separate GSC CSV dimensions cannot establish Query-to-Page attribution.
6. No post-release Search Console index-coverage export yet.
7. No Bing Webmaster performance/crawl dataset.
8. No licensed backlink/referring-domain dataset.
9. No real qualified-enquiry rows in `page-lead-outcomes.csv`.
10. No field Core Web Vitals dataset for the deployed release.
11. Ten locale programmes lack named native commercial approval.
12. Four controlled articles lack genuine named-reviewer approval.
13. No central configurable competitor registry.
14. No rank-provider/API adapter or confidence labeling.
15. No unified daily/weekly/monthly job scheduler.
16. No standard process-run/error log shared by SEO scripts.
17. No private authenticated command-center dashboard.
18. No structured per-change snapshot/rollback database beyond Git/change reports.
19. Static components are replicated across many generated pages, increasing drift risk despite validators.
20. The browser-side form access token should be restricted/abuse-monitored or moved behind a server-side boundary when operationally feasible; no secret should be added to public JavaScript.

## 16. Current indexation problems

The most recent owner-provided Page Indexing evidence predates this release and contained historical WordPress/store URLs, `?j=` copies, duplicate host/path variants and intentional noindex pages. Those patterns were remediated through direct 301, 410 or honest 404 behavior. The current canonical sitemap has 1,432 direct 200 URLs.

Current unknowns—not confirmed defects—are:

- Google index coverage/canonical selection after the 20 August release;
- whether all four new URLs have been crawled/indexed;
- post-release crawled/discovered-not-indexed totals; and
- Bing/Yandex index coverage.

These require new webmaster-tool exports after recrawl. IndexNow acceptance does not prove indexing.

## 17. Current SEO score

Comparable internal implementation-quality score: **89/100**, improved from **83/100**.

This is not a Google score or ranking forecast. Technical implementation is strong; authority, human evidence, post-release performance, first-party proof and earned citations limit the current ceiling.

## 18. Top 20 SEO opportunities

The first 16 are observed in the 19 May–18 August Search Console baseline; the remaining four are evidence-gated strategic opportunities.

| Priority | Opportunity | Evidence | Next safe action |
|---:|---|---|---|
| 1 | Cumin/jeera price outlook CTR | 1,729 impressions, 0.40% CTR, position 6.99 | Preserve deployed refresh; compare post-release CTR and queries |
| 2 | Packing calculator/snippet cluster | 1,444 impressions, 0.76% CTR, position 6.90 | Build query-to-page evidence for bag/container questions; monitor new copy |
| 3 | FOB/CIF calculator intent | `fob calculator` and CIF variants show page-one visibility | Defend quote calculator and validate qualified-use events |
| 4 | Indian rice import-duty guide | 325 impressions, 1.23% CTR, position 7.98 | Monitor freshness and snippet after release |
| 5 | India versus Thailand rice comparison | 381 impressions, 2.36% CTR, position 6.99 | Strengthen only from observed post-release queries |
| 6 | Turmeric finger guide | 231 impressions, 0.43% CTR, position 7.83 | Monitor snippet and country intent |
| 7 | Port/transit calculator | 528 impressions, 0.76% CTR, position 16.05 | Improve conversion measurement; validate route-intent queries |
| 8 | Malay chilli guide | 177 impressions, zero clicks, position 7.34 | Native-review Malay snippet before changing it |
| 9 | Psyllium export guide | 230 impressions, 1.30% CTR, position 7.12 | Monitor revised buyer evidence and CTA path |
| 10 | Basmati buyer guide | 143 impressions, zero clicks, position 8.67 | Diagnose actual queries before a title experiment |
| 11 | UAE trade hub | 601 impressions, 1.66% CTR, position 14.29 | Segment UAE query/page data and qualified enquiries |
| 12 | Product catalogue | 110 impressions, zero clicks, position 8.55 | Determine queries; avoid turning catalogue into keyword blocks |
| 13 | Certificates/trust page | 93 impressions, 2.15% CTR, position 4.87 | Publish only current verified proof with authorization |
| 14 | Nigeria/West Africa guide | 97 impressions, zero clicks | Retain guide; do not publish thin Nigeria landing page without gate evidence |
| 15 | French homepage | 102 impressions, 0.98% CTR | Native-review top French queries and commercial wording |
| 16 | White-rice policy article | 134 impressions, zero clicks, position 10.75 | Maintain current official-policy date and monitor |
| 17 | IR64 specialist cluster | Current SERPs reward narrow grade comparisons and buyer paths | Measure 5%/10% query-to-page attribution before further edits |
| 18 | Tamil cumin demand test | Two visible Tamil cumin-price queries total 34 impressions | Record as a language experiment candidate; do not create a locale yet |
| 19 | United States visibility diagnosis | 1,563 impressions but 0.06% CTR across the separate country table | Obtain Country + Query/Page API data before investing |
| 20 | Desktop visibility/CTR gap | Desktop: 6,364 impressions, 2.48% CTR, position 12.12; mobile position 6.71 | Diagnose device/query mix and field UX; do not infer a technical defect |

## 19. Top 20 technical issues

The prioritized list is the same 20-item gap/risk list in section 15. None currently justifies emergency public-site changes. The highest system-building priorities are persistent storage, trustworthy multidimensional ingestion, unified logging, post-release index monitoring and conversion outcomes.

## 20. Top competitor gaps

Current public search sampling shows:

- `ir64.com`/Haji Rice: specialist IR64 focus, grade comparison, direct price/sample paths and deep FAQ coverage. JFT needs measurable query-to-grade attribution and verified proof, not copied claims.
- Govindu Brothers: focused parboiled-rice landing page with concise grade/specification and pre-shipment sample framing. JFT's broader control/document workflow is stronger but less narrowly presented.
- Globemiles: clear category segmentation, buyer roles, visible entity/location claims and rapid-quote framing. JFT should surface only verified entity/operational proof.
- Trion Exim: concise category breadth and registration-led trust positioning. JFT should not repeat registration claims without current holder/scope evidence.
- Specialist/product marketplaces: strong exact-product and price intent, but often weak evidence, originality or buyer education. JFT can win with cited specification, inspection, document and calculator content.

JFT's competitive advantages are multilingual breadth, 84-product master coverage, calculators, buyer-security/document resources, schema/hreflang consistency and a source-backed evidence discipline. Its disadvantages are weak earned authority, limited public operational proof and absent current backlink/ranking-provider data.

## 21. Missing product pages

- **Annatto seeds:** referenced in the strategic business scope but absent from the current product master and public pages. Publication requires confirmation that JFT currently offers the exact product/form, botanical identity, specification, origin, packing, testing and serviceability.
- **Zedoary root:** referenced in the strategic business scope but absent from the current product master and public pages. Publication requires verified botanical/plant-part identity, intended use, specification, regulatory boundaries and operational availability.

No other product page should be inferred from competitor catalogues. The 84-product master is the authoritative current catalogue until the business approves additions.

## 22. Missing country pages

Documented, intentional holds:

1. Nigeria rice;
2. Saudi Arabia Basmati rice;
3. Bangladesh rice;
4. Sri Lanka rice;
5. Kenya pulses; and
6. Vietnam agricultural market.

These are opportunities, not approved pages. Each needs unique demand, regulatory, importer, route and serviceability evidence.

## 23. Missing language opportunities

- Tamil is the only newly observed language signal in the supplied query export: two cumin-price queries totaling 34 impressions. This is enough to track, not enough to create a Tamil site section.
- Simplified Chinese, Korean and Japanese remain unvalidated possibilities; no first-party query/country evidence currently supports investment.
- French and Malay already have impressions and should receive native review before adding languages.
- Language configuration should be centralized in the proposed SEO system instead of being hardcoded across individual scripts.

## 24. Missing content clusters

1. Calculator query-support cluster for FOB/CIF definitions and worked, clearly non-quotational examples.
2. Container packing question cluster for bag-size/container-capacity intent.
3. Query-led cumin price terminology cluster, potentially including a controlled Tamil brief if demand persists.
4. Verified company proof/registration cluster, pending publication authority.
5. Annatto seed product/guide cluster, pending product verification.
6. Zedoary root product/guide cluster, pending product verification.
7. Post-release indexation and canonical-status reporting cluster inside the private SEO system.
8. Qualified-enquiry feedback model connecting landing pages to business outcomes.

These are candidate clusters. Only the private measurement/indexation layers are immediately implementation-ready; new public content remains evidence- or observation-gated.

## 25. Recommended implementation sequence

### Phase A — Intelligence foundation

1. Create a private `seo_system/` Python package suited to the static repository.
2. Add centralized YAML/JSON configuration for languages, markets, competitors, thresholds and safe-action policy.
3. Add SQLite entities for pages, keywords, observations, crawls, links, schemas, opportunities, tasks, changes, experiments and process runs.
4. Import the current sitemap, page inventory, top-100 opportunity map and Search Console baseline.
5. Add migration, backup and schema-validation tests.

### Phase B — Measurement and history

6. Wrap the existing crawler/audits as read-only collectors that store timestamped snapshots.
7. Add adapters for separate GSC CSV exports and future multidimensional Search Analytics API input.
8. Add Bing, backlink and rank-provider interfaces that explicitly return `DATA NOT AVAILABLE` until configured.
9. Join aggregate landing-page lead outcomes without personal data.
10. Add unified structured process logging and alert thresholds.

### Phase C — Opportunity and governance

11. Implement transparent 0–100 opportunity scoring with confidence and source fields.
12. Implement search-intent, product, market, language and cluster relationships.
13. Generate a prioritized task queue with impact, difficulty, risk, evidence and required approval.
14. Create before/after snapshots and rollback metadata for proposed low-risk changes.
15. Keep automatic publish off; generate patches only for approved low-risk actions.

### Phase D — Private command center

16. Generate a private static/local dashboard from SQLite; never ship its database or heavy analytics to the public assets directory.
17. Show global health, observed performance, data freshness, opportunities, technical alerts and one next-best action.
18. Add daily/weekly/monthly CLI entry points suitable for GitHub Actions or Cloudflare scheduling only after secrets and costs are approved.

### Phase E — Learning cycle

19. Compare the 20 August release with a like-for-like post-release window beginning after sufficient recrawl/observation time.
20. Re-score only from observed GSC, indexation, rank-provider and qualified-enquiry evidence; preserve `UNKNOWN` for unavailable data.

## First next-best action

**Build the persistent intelligence foundation and import the existing sitemap, audit, top-100 and Search Console baseline.**

Reason: the public site is technically healthy, while the new specification's core requirement—historical Discover → Analyze → Score → Prioritize → Measure → Learn state—does not yet exist. Building more pages now would add content without solving the measurement and learning gap.

## Quality-gate status

- Important URL noindex/robots accidents: none detected.
- Canonical/hreflang/sitemap/schema/local-link gates: passed.
- Production crawl: 1,432/1,432 direct 200.
- Metadata uniqueness/H1 architecture: passed; 47 native editorial heuristics remain.
- Search intent and keyword opportunities: documented.
- Fake data/claims: prohibited and evidence-gated.
- Rollback/change record: Cloudflare version plus repository change reports exist; structured per-change rollback database is pending.
- Existing functionality: production smoke and interaction checks passed.

## Evidence references

- `reports/seo-baseline-2026-08-20.md`
- `reports/seo-top-100-completion-2026-08-20.md`
- `reports/seo-release-gate.md`
- `reports/seo-implementation-phase-23-2026-08-20.md`
- `reports/seo-implementation-phase-24-2026-08-20.md`
- `reports/search-console-export-2026-08-20/search-console-performance-analysis.md`
- `reports/seo-market-page-publication-gates-2026-08-20.md`
- Current competitor examples: `https://ir64.com/`, `https://govindubrothers.com/parboiled-rice/`, `https://globemiles.com/`, `https://trionexim.in/agro-products.html`.
