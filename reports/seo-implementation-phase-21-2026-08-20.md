# SEO Implementation Phase 21 — 20 August 2026

## Outcome

This phase addressed opportunity-map ranks 97–100: author/reviewer entities, native-language quality governance, digital-PR evidence assets and the Search Console opportunity loop.

Two items are operational but intentionally evidence-gated. The repository does not prove that a named person approved each guide, so no false “reviewed by” markup was added. It also contains no native-reviewer or Search Console demand evidence for the ten locale programmes, so every locale remains recorded as pending rather than falsely approved.

## Author and reviewer entities

- Published `editorial-policy.html` with the three real leadership entities already shown on the About page: Mr. Ganpatlal Jain, Managing Director; Mr. Vicky Jain, Director of Exports; and Mr. Mithun Jain, Director of Imports.
- Limited their stated credentials to published company roles; no unverified degree, licence or professional certification was added.
- Defined author, reviewed-by, source-reviewed, updated and correction labels.
- Added visible organisational-author and reviewer-status disclosures to four priority buyer guides.
- Added `data/editorial-review-register.csv` and `scripts/validate_editorial_governance.py`.
- Recorded all four guides as `pending_human_approval`; a named reviewer, relevant role/qualification, scope and exact review date are required before approval.

## Native-language quality governance

- Expanded `localization-review.json` into a versioned approval policy.
- Added a controlled ten-locale register covering market, URL scope, status, reviewer evidence, legal status, source batch, GSC evidence and demand decision.
- Added a validator that rejects an approved row without a named native reviewer, language, qualification, review date, source version and Search Console evidence period.
- Prevented a `proceed` decision without positive non-brand impressions.
- Recorded all ten locales as pending/hold because no human or first-party performance evidence was supplied.
- Kept the English editorial policy and research dataset English-only until native review and demand justify localization.

## Digital PR evidence asset

- Published `india-agricultural-export-market-data-sources.html` as a new English canonical research asset.
- Added a downloadable eight-row CSV covering annual and monthly TradeStat, APEDA custom/quick/overview reports, Spices Board statistics and AGMARKNET.
- Documented dimensions, observed data status, buyer use and a material limitation for every source.
- Added Dataset JSON-LD, a CC BY 4.0 reuse statement and a transparent methodology.
- Did not combine incompatible sources into an invented market-size figure.

## Search Console opportunity loop

- Added a standard GSC query/page input template and aggregate landing-page lead-outcome template.
- Added a Python workflow that maps every sitemap URL, filters branded queries, calculates CTR-gap opportunity, joins enquiries/qualified/won outcomes and emits page- and query-level CSVs plus a Markdown scorecard.
- Preserved no-data pages as `no_gsc_data`; absence of impressions is not interpreted as no demand.
- Tested the workflow with two non-brand rows, one branded row and lead outcomes. The branded row was excluded, both non-brand pages were ranked, and the fixtures were removed.
- Current production-data output maps 1,432 URLs with zero supplied non-brand rows; performance priorities remain gated until a real export is supplied.

## Primary sources

- TradeStat annual commodity exports: <https://tradestat.commerce.gov.in/eidb/commodity_wise_export>
- TradeStat commodity × country exports: <https://tradestat.commerce.gov.in/eidb/commodityx_countries_wise_export>
- TradeStat monthly foreign trade: <https://tradestat.commerce.gov.in/ftspcc/export_commodity_wise>
- APEDA custom product reports: <https://agriexchange.apeda.gov.in/India/GenerateAPEDAProductReport/>
- APEDA quick reports: <https://agriexchange.apeda.gov.in/India/Home/QuickReports>
- APEDA agri-export overview: <https://farmerconnect.apeda.gov.in/Home/ExportFromIndia?PaccessID=0>
- Spices Board trade statistics: <https://www.indianspices.com/box2info>
- AGMARKNET: <https://agmarknet.gov.in/>

## Validation

- Editorial governance: four controlled records passed; zero approved and four correctly gated.
- Localization governance: ten records passed; zero approved and ten correctly gated.
- Localization technical audit passed after excluding the two explicitly English-only governance/research assets from parity requirements.
- Search Console loop mapped all 1,432 sitemap URLs and passed synthetic brand-exclusion and aggregation tests.
- FAQ/schema and cluster validator passed 926 FAQPage blocks and 83 priority cluster pages.
- New pages passed one-title, one-H1, one-canonical and JSON-LD parsing checks.
- Full local link scan found zero unique broken links across 3,508 HTML files.
- Sitemap parsed with 1,432 URLs and retained both clean logistics URLs.
- Python compilation passed for the new and updated governance/measurement scripts.
- Temporary test inputs and outputs were removed.

## External evidence still required

1. Signed article-level approval before publishing a named reviewer.
2. Named native reviewers and market-level GSC evidence before localized commercial approval/expansion.
3. A real Search Console export and aggregate lead outcomes before page priorities can learn from performance.
4. Outreach and earned third-party citations for the new research asset.
5. Current original/redacted company proof before public credential claims.

## Deployment status

Local implementation only. No production deployment, indexing request or external outreach was performed.

