# JFT Agro SEO Intelligence System — Joint Implementation Contract

Date: 2026-08-20  
Inputs:

1. `JFT AGRO — AUTONOMOUS SEO INTELLIGENCE & EXECUTION AGENT — Technical Codex Implementation Specification`
2. `JFT AGRO — AUTONOMOUS GLOBAL SEO AGENT V3`
3. `reports/seo-system-discovery-2026-08-20.md`

Status: **Compatible and consolidated into one system**

## Review conclusion

The two specifications describe the same product from complementary angles:

- The Technical Codex specification defines modules, data entities, safety boundaries and implementation phases.
- V3 defines the operating loop, striking-distance workflows, programmatic-content protections, monitoring cadence, experiment memory and management outputs.

They should not be implemented as separate codebases. One private `seo_system/` package will serve both. Existing `scripts/`, audits, validators, reports and public pages will be reused rather than replaced.

## Non-negotiable operating contract

The system will operate as:

`DISCOVER → RESEARCH → CLASSIFY → SCORE → PRIORITIZE → PLAN → EXECUTE → VALIDATE → INDEX → MONITOR → MEASURE → LEARN → REPEAT`

At every stage:

- unavailable facts remain `DATA_NOT_AVAILABLE` or `UNKNOWN`;
- estimates are labeled `ESTIMATED` with method and confidence;
- search volume, rankings, conversions, backlinks, credentials, prices and company claims are never fabricated;
- public-site performance and design are protected;
- country/language/programmatic pages require distinct intent and a minimum unique-value score;
- automatic publishing remains disabled by default;
- no indexing request occurs before direct 200, indexability, canonical, robots and useful-content validation;
- human/native approvals cannot be synthesized by code; and
- high-risk changes require explicit approval.

## Unified architecture

Recommended repository structure:

```text
seo_system/
  __init__.py
  cli.py
  config/
  db/
    migrations/
    repositories/
  collectors/
    site/
    search_console/
    bing/
    rankings/
    competitors/
    backlinks/
    analytics/
  models/
  classifiers/
    intent/
    page_type/
    product/
    market/
    language/
  graph/
  scoring/
  opportunities/
  recommendations/
  changes/
  experiments/
  validation/
  alerts/
  reports/
  dashboard/
  scheduling/
tests/seo_system/
data/seo-system/          # private/generated, excluded from production assets
reports/seo-system/       # generated management evidence
```

The public Cloudflare asset allowlist must never include the SQLite database, private exports, logs, credentials or command-center output.

## Unified persistent data model

Minimum entities:

| Entity | Purpose |
|---|---|
| `page` | Canonical URL, locale, type, intent, scores, crawl/update status |
| `keyword` | Query, product, country, language, intents, observed/estimated metrics |
| `keyword_observation` | Engine/provider/date/device/country position, clicks, impressions and confidence |
| `page_observation` | Page/date clicks, impressions, CTR, position, conversions and index state |
| `crawl_run` / `crawl_result` | Status, canonical, robots, schema, timing and errors by run |
| `link_edge` | Source, target, anchor, relevance and first/last observed dates |
| `hreflang_edge` | Reciprocal locale mapping and validation status |
| `schema_observation` | Type, validity, visible-content consistency and run date |
| `product` | Product identity and verified business-value inputs |
| `market` | Country, language, serviceability and evidence gate |
| `competitor` / `competitor_observation` | Configurable competitor and permitted observations |
| `content_cluster` / `cluster_member` | Pillar/support/product/market relationships |
| `opportunity` | Score, confidence, evidence, target, status and dates |
| `task` | Impact, value, difficulty, risk, approval and execution state |
| `change` | Old/new values, reason, risk, timestamps, validation and rollback pointer |
| `experiment` / `experiment_observation` | Hypothesis, controlled variable, windows and outcome |
| `process_run` | Job start/end/result/errors/affected URLs |
| `alert` | Severity, rule, evidence, lifecycle and resolution |
| `lead_outcome` | Aggregate landing-page enquiries/qualified/won outcomes without PII |

SQLite will be the initial storage engine because the project is static, local automation already uses Python, and no production database exists. Migrations and backup/restore tests are mandatory.

## Unified scoring rules

All scores are `JFT AGRO INTERNAL` scores, never search-engine scores.

### Opportunity score

Normalized 0–100 from available evidence:

- observed demand/confidence;
- commercial intent;
- business value;
- ranking feasibility;
- current visibility/striking distance;
- content or SERP gap;
- market priority;
- conversion evidence; and
- implementation risk/difficulty adjustment.

Unavailable inputs do not receive invented neutral numbers. The score records completeness and confidence separately so a 70 with 90% evidence is distinguishable from a 70 with 30% evidence.

### Product opportunity score

Observed query/page visibility + verified business value + buyer intent + feasibility + international demand confidence.

### Country opportunity score

Observed country/query demand + product fit + language fit + serviceability + compliance evidence + conversion evidence. A high search score cannot override a failed market publication gate.

### Language opportunity score

Observed language/country demand + relevant product intent + native-review availability + localization cost + existing performance. It cannot automatically trigger blanket translation.

### Unique value score

Required before a new programmatic, country or language page:

- distinct search intent;
- verified first-party information;
- unique buyer/compliance/logistics value;
- non-duplication against existing pages;
- serviceability;
- evidence freshness; and
- native quality where applicable.

Below-threshold proposals are rejected rather than published.

## Unified opportunity workflows

### Striking distance

Priority bands:

- positions 4–10: defend/CTR/content-completeness review;
- positions 11–20: intent, internal-link and competitor-gap review;
- positions 21–30: relevance and content-gap validation;
- positions 31–50: invest only when business value and relevance justify it.

Required evidence: meaningful impressions, commercial relevance, actual query-to-page mapping and a stable comparison period.

### CTR opportunity

High impressions + CTR below a clearly disclosed position benchmark. The system proposes non-clickbait title/description experiments; it does not automatically deploy them or change several variables at once.

### Content decay

Classifications: `GROWING`, `HEALTHY`, `STABLE`, `DECLINING`, `CRITICAL`, `INSUFFICIENT_DATA`.

Requires comparable periods, last meaningful update, indexation state and query mix. A partial month cannot independently establish decay.

### Cannibalization

Requires observed multiple-URL ranking for the same query/intent across comparable windows. Similar keywords in HTML are not sufficient evidence. Recommendations may be differentiate, retarget, merge, redirect or canonicalize; the last three are high risk.

### Query-to-content loop

Observed query → actual ranking page → intent/market/product classification → competitor/SERP gap → unique-value gate → task recommendation → approval → controlled change → validation → monitoring windows.

## Risk and approval policy

| Risk | Examples | Default state |
|---|---|---|
| Low | clear broken-link repair, schema serialization, sitemap sync, metadata proposal | recommendation/dry-run; apply only with high confidence and explicit apply mode |
| Medium | content sections, contextual-link architecture, translated copy, title experiment | review required |
| High | URL, redirect, canonical, robots, noindex, deletion, language architecture, mass generation | explicit owner approval required |

`AUTO_APPROVED` means policy-eligible, not silently published. The initial release of the intelligence system will produce patches and validation evidence; it will not deploy automatically.

## Change, version and rollback contract

Every executable change records:

- change ID;
- task/opportunity ID;
- URL/file;
- exact old and new value or snapshot hashes;
- reason and evidence;
- expected outcome;
- risk/confidence;
- approval identity/time where required;
- apply time;
- validation results;
- Cloudflare/Git release identifier when deployed; and
- rollback pointer/result.

Failed experiments enter memory and are not recommended again without new evidence. Successful patterns may generate candidates, never duplicate content automatically.

## Data-source adapters

| Source | Current state | System behavior |
|---|---|---|
| Static site/sitemap | Available | ingest and snapshot |
| Existing audits | Available | wrap/reuse and persist findings |
| GSC separate export | Available for 19 May–18 August | ingest as independent Query/Page/Country/Device aggregates |
| GSC multidimensional/API | Unavailable | show `DATA_NOT_AVAILABLE`; never infer Query → Page |
| GSC post-release indexation | Unavailable | schedule/import when owner supplies it |
| IndexNow | Available and used | changed verified URLs only; record responses |
| Bing Webmaster | Unavailable | adapter returns `DATA_NOT_AVAILABLE` |
| GA4 events | Client implementation exists | import only approved aggregate exports/API data |
| Qualified lead outcomes | Empty template | no commercial result claims |
| Rank provider | Unavailable | architecture only; no estimated position presented as exact |
| Backlink provider | Unavailable | architecture only; no authority count invented |
| Competitor SERPs | Current manual sample | store source/date/query; respect access terms |

## Command-center contract

The private command center will show:

- global internal SEO score and evidence completeness;
- organic clicks, impressions, CTR and average position;
- top striking-distance keyword;
- top opportunity/product/country/language;
- top technical issue and alert;
- top competitor threat/content gap;
- indexation and data-freshness state;
- conversion outcomes when supplied;
- top ten next actions; and
- one clearly justified next-best action.

Every missing metric displays `DATA NOT AVAILABLE`. The dashboard is generated privately and excluded from the public deployment bundle.

## Monitoring and report cadence

### Daily, when data/access exists

- crawl-critical status/canonical/robots/sitemap changes;
- new 4xx/5xx and important-page noindex;
- important schema/hreflang breakage;
- process failures and data freshness.

### Weekly

- new queries and striking-distance movement;
- competitor/SERP samples within permitted limits;
- internal-link and content-gap candidates;
- product/country/language opportunity changes.

### Monthly

- full technical/international/content audit;
- performance and conversion scorecard;
- authority/backlink analysis when provider data exists;
- task/experiment outcomes and roadmap.

### Change observation windows

- Day 0 baseline;
- days 7, 14, 28, 56 and 90;
- no success/failure conclusion from a few hours of data.

## Unified implementation phases

The two source phase lists are reconciled into this order:

### Phase 1 — Foundation and persistence

- package, configuration, SQLite schema/migrations, repositories, logging and CLI;
- import current sitemap/pages/products/locales/top-100/GSC baseline;
- tests for migrations, validation and backup/restore.

### Phase 2 — Audit and technical monitoring

- wrap current audits/crawler;
- snapshot status, canonical, robots, sitemap, hreflang, schema, links, images and performance evidence;
- alert rules and technical health score.

### Phase 3 — Metadata, intent and page scoring

- intent classification;
- metadata recommendation engine;
- transparent page/internal SEO scores;
- no automatic public changes.

### Phase 4 — Product, keyword and opportunity intelligence

- product profiles and clusters;
- GSC query mining;
- long-tail/question classification;
- striking-distance, CTR and business-value scoring.

### Phase 5 — Country, language and international intelligence

- country/language scores;
- unique-value/publication gates;
- centralized language configuration and hreflang health score.

### Phase 6 — Internal-link, content and schema/entity intelligence

- semantic link graph and orphan/weak classification;
- cluster/cannibalization/content-gap models;
- schema recommendation and visible-content consistency;
- central company entity record.

### Phase 7 — Competitor, SERP, rank and authority adapters

- configurable competitor registry;
- permitted observation storage;
- provider interfaces with explicit unavailable states.

### Phase 8 — Task queue, safe execution and experiments

- top ten actions/next-best action;
- approval states;
- snapshots, patch generation, validation and rollback;
- experiment and success/failure memory.

### Phase 9 — Private dashboard and reports

- command center;
- product/country/language/content/technical views;
- daily, weekly and monthly generators.

### Phase 10 — Scheduling and learning

- scheduler entry points;
- data-freshness/cost/rate controls;
- 7/14/28/56/90-day comparisons;
- evidence-driven reprioritization.

## Test and quality-gate contract

Automated tests must cover:

- URL/canonical normalization;
- metadata and intent classification;
- opportunity and evidence-completeness scoring;
- sitemap/robots rules;
- reciprocal hreflang and canonical compatibility;
- JSON-LD validity and visible-content consistency;
- internal-link graph/orphan classification;
- programmatic unique-value rejection;
- risk/approval enforcement;
- snapshot/apply/rollback lifecycle;
- process logging and unavailable-data behavior;
- dashboard private-output exclusion; and
- no-regression integration with current release gates.

No public change may deploy unless the existing release gate plus applicable content, international, performance and indexation gates pass.

## Current evidence-led priorities

1. Import and preserve the pre-release GSC baseline.
2. Build persistent page/keyword/observation/process records.
3. Support true Query + Page data when later supplied; do not join separate tables.
4. Track cumin-price, packing and FOB/CIF calculator clusters as first striking-distance/CTR cases.
5. Add product/country/language scoring with evidence completeness.
6. Keep Tamil cumin as an observed language candidate, not an approved locale.
7. Keep annatto, zedoary and held market pages behind business/evidence gates.
8. Add lead outcomes before claiming business success.
9. Add competitor/backlink/rank providers only when approved and available.
10. Generate the private command center after persistence and scoring are trustworthy.

## Conflicts resolved

| Topic | Resolution |
|---|---|
| Auto implementation | Low-risk/high-confidence actions are policy-eligible, but initial behavior is proposal/dry-run; public apply/deploy is separate. |
| Country/language expansion | Scores recommend; unique-value, serviceability, native-review and approval gates decide publication. |
| Search-volume/rank gaps | Store `UNKNOWN`/`DATA_NOT_AVAILABLE`; do not backfill fabricated values. |
| Dashboard location | Private/admin-generated only; never load data-heavy SEO logic into public pages. |
| Sitemap segmentation | Optional reporting feature, not a current technical requirement. |
| Product schema | Recommend only when verified visible attributes satisfy the page and maintenance contract. |
| Daily automation | Runs only for available, approved, rate-safe sources; no wasteful crawling or spam submissions. |
| Completion | Architecture may be complete with unavailable adapters, but performance learning remains ongoing and cannot be declared from deployment-day data. |

## Joint next-best action

**Implement Phase 1: the typed Python package, centralized configuration, SQLite schema/migrations, repositories, unified process logging and importers for the current sitemap, product master, top-100 opportunities and GSC baseline.**

This is the smallest foundation that unlocks both specifications without modifying the public website or creating SEO debt.
