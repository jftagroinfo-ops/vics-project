# JFT Agro Comprehensive Website Audit

Audit date: 12 August 2026

Scope: repository crawl, production HTTP/TLS checks, representative desktop/mobile browser tests, static SEO and accessibility checks, Lighthouse baseline, content/claims review, analytics consent test, image validation, and public competitor review.

## Executive Summary

The site has a strong organic-search foundation: descriptive product URLs, broad commodity coverage, international folders, canonical and hreflang markup, a valid sitemap, crawlable static HTML, and clear RFQ paths. The audit also found important issues that were corrected in the repository: duplicated GA4 configuration, an accidental temporary sitemap URL, mislabeled/oversized images, unsupported review schema, overly absolute commercial claims, incomplete interaction tracking, and homepage contrast/accessibility defects.

This is not a claim that the site is bug-free or that every private SEO metric is healthy. Search Console, GA4, Cloudflare, backlink-platform, and server-log access are required for several production-only conclusions.

## Verified Baseline

- 1,612 renderable HTML pages audited locally.
- 1,103 indexable pages and 1,103 unique sitemap URLs after remediation.
- Zero sitemap routes missing from the repository.
- Earlier full production crawl: 1,104/1,104 then-live sitemap URLs returned HTTP 200, with no redirects or failures. The removed temporary URL requires a fresh post-deployment crawl.
- 84 commercial product pages passed the structured completeness and uniqueness audit.
- 188 WebP files decode correctly and are genuine WebP files.
- 26 browser checks across key English and French routes, mobile and desktop: HTTP 200, no horizontal overflow, and an H1 on every tested page. One transient local-server asset 404 did not reproduce.
- Lighthouse baseline on the homepage: Accessibility 96, Best Practices 100, SEO 100. Performance could not be scored because Lighthouse did not identify an LCP candidate on the carousel homepage.

## Remediation Completed

1. Removed the temporary `tmp-packing-dom.html` URL from `sitemap.xml` and blocked audit/report/temp paths in `robots.txt`.
2. Centralized GA4 initialization in the consent-aware shared conversion client, removing duplicate page-level configurations from 1,329 pages.
3. Added tracking for telephone, email, WhatsApp, downloads, outbound links, conversion links, and explicitly tagged interactions.
4. Added a working footer Cookie Preferences control and aligned privacy wording with the actual consent behavior.
5. Verified analytics behavior: zero GA requests before consent or with essential-only consent; one GA configuration after acceptance.
6. Removed seven unsupported self-serving aggregate-rating/review schema blocks.
7. Qualified repeated absolute claims concerning samples, response times, fumigation, testing, port coverage, defaults, and container availability.
8. Optimized 19 large images, saving approximately 10.69 MB. Sixteen `.webp` assets that contained JPEG data were converted to real WebP.
9. Improved titles/descriptions on 25 priority English pages.
10. Improved homepage LCP semantics with a prioritized real `<img>`, delayed non-visible carousel image loading, and removed the initial text fade.
11. Corrected homepage manufacturing-section text contrast and region-card accessible names.
12. Added reusable audit scripts and machine-readable reports under `scripts/` and `reports/`.

## 1. Technical SEO

Status: Good foundation; post-deployment validation required.

- The corrected sitemap and indexable page inventory match exactly at 1,103.
- Canonical and hreflang relationships are present across the international structure.
- HTTP redirects to HTTPS and `www` redirects to the apex domain.
- Production returns a real 404 for an unknown path.
- URLs are descriptive and keyword-oriented.
- Remaining metadata debt: 219 titles and 257 descriptions are outside the audit's practical length bands, mostly translated product pages. There are 22 duplicate-title groups and one duplicate-description group, concentrated in Sinhala/Vietnamese variants.
- Search Console must confirm discovered-versus-indexed counts, exclusions, canonical choices, crawl stats, and international targeting after deployment.
- Products are filtered on one catalogue URL, so traditional pagination markup is not currently relevant. If filter states become crawlable URLs, each state needs an intentional canonical/indexing policy.

## 2. Performance And Speed

Status: Functional and stable in local browser tests; two material optimization opportunities remain.

- Representative local LCP values on non-home pages were roughly 0.44-0.84 seconds without network throttling; CLS was generally low, with infrastructure mobile at approximately 0.091.
- The homepage still produces no LCP entry in Lighthouse/PerformanceObserver despite converting the primary visual to a prioritized image. The carousel architecture needs a focused paint-timing investigation.
- `products.html` creates roughly 6,800 DOM nodes because all 84 cards are rendered before most are hidden. Render the first page only and append/replace cards when filtering or paginating.
- Twelve images remain above the audit threshold, plus a 5 MB homepage video. Serve viewport-specific `srcset`/`sizes`, poster imagery, and defer video bytes until interaction or an idle budget.
- The homepage HTML is approximately 235 KB. Moving page-specific CSS/JS into versioned, cacheable assets would reduce document parsing and enable reuse.
- Production homepage TTFB samples were approximately 0.82-0.89 seconds. Cloudflare caching was dynamic with a 10-minute HTML cache policy; cache tuning should be tested carefully around content freshness.

## 3. Security

Status: HTTPS healthy; headers and operational controls need owner action.

- TLS 1.3 was available. The checked certificate covered `jftagro.com` and was valid from 22 July 2026 to 21 October 2026.
- HTTP is redirected to HTTPS.
- Production responses did not include HSTS, CSP, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, or an explicit frame-ancestors policy.
- Because the site is GitHub Pages behind Cloudflare, configure these as Cloudflare Transform Rules/Workers response headers; a repository `_headers` file would not enforce them on this stack.
- A valid `.well-known/security.txt` exists.
- No login, application database, or payment flow was found. Firewall rules, bot protection, malware scanning, account 2FA, deployment permissions, and backups must be checked in Cloudflare/GitHub administration.
- Introduce CSP in report-only mode first because the site currently contains inline styles/scripts and third-party forms/analytics.

## 4. On-Page SEO

Status: Strong coverage; translated metadata requires refinement.

- Priority English titles and descriptions were tightened and 84 product pages passed content/commercial checks.
- Static crawl checks cover H1 presence, canonical tags, image alt text, local references, schema parseability, duplicate IDs, and metadata.
- Product/category/internal trade links provide substantial topical connectivity.
- Remaining work should prioritize human-edited localized titles/descriptions rather than mechanical truncation.
- Keep schema limited to verifiable organization, breadcrumb, article, FAQ, and product facts. Do not restore self-authored aggregate ratings without eligible, visible, independently sourced review evidence.

## 5. Off-Page SEO

Status: Account/tool access required.

- Backlink quality, toxic-link classification, anchor distribution, authority metrics, and competitor link intersections cannot be established reliably from public search snippets.
- Export GSC links and connect Ahrefs/Semrush/Moz before disavowing anything. A disavow file should only be used for a documented manual-action or clearly manipulative-link case.
- Public competitors reviewed include category specialists such as Indian Spice Exports, Daley Global, Ace7 Spices, Alstoe India Exports, and VI Exports. Their recurring strengths are focused category pages, origin stories, compliance evidence, and importer-specific specifications. JFT's advantage is its broader 84-product catalogue and multilingual depth.

## 6. User Experience

Status: Good responsive baseline.

- Key routes passed mobile/desktop overflow and console checks.
- Navigation, RFQ, sample, WhatsApp, and tool pathways are prominent.
- Product catalogue density remains the largest usability/performance concern. Incremental rendering and persistent filter state will improve scanability.
- Avoid unsupported certainty in trust messaging; buyer confidence is better served by downloadable, current evidence and clearly qualified operational terms.

## 7. Conversion Rate Optimization

Status: Measurement foundation improved.

- Conversion interactions now include form start, lead success, contact channels, downloads, outbound clicks, and conversion-link clicks.
- Validate these events in GA4 DebugView and mark only real business outcomes as conversions.
- Add a visible form error summary and preserve entered values after submission failures on every lead form.
- Run experiments only after a stable four-to-six-week baseline. Highest-value tests: RFQ label/placement, sample versus quote intent, and shorter first-step forms.

## 8. Content

Status: Broad topical coverage; evidence and localization are the priorities.

- The site covers products, regions, quality, infrastructure, trade destinations, tools, FAQs, and blogs.
- Content freshness should be governed by visible reviewed dates and an editorial owner, especially rates, regulations, freight, standards, and crop/market commentary.
- Commercial claims were normalized, but certifications, capacity, lab, export-market, and GI statements still require current documentary evidence from the business.
- Use Search Console query/page exports to identify cannibalization, decaying blogs, and keyword gaps; public crawling cannot reveal actual impressions or conversions.

## 9. Accessibility

Status: Strong but incomplete.

- Lighthouse accessibility baseline was 96.
- Homepage contrast and region-card name mismatches found by Lighthouse were corrected.
- Shared skip navigation and consent-dialog labels are present.
- Complete a keyboard-only pass on every menu, carousel, calculator, accordion, modal, and form. Then test VoiceOver/NVDA announcements for validation and dynamic results.
- Automated tests cannot certify WCAG conformance; manual assistive-technology testing remains necessary.

## 10. Analytics And Tracking

Status: Consent behavior verified locally.

- Direct GA4 measurement ID: `G-MWZ2ZWZP4G`.
- GA4 loads only after acceptance and configures once.
- Essential-only consent produces no GA request.
- Attribution parameters and landing/referrer data are retained in session storage and attached to forms.
- No active GTM container is installed; the placeholder is commented out. Direct GA4 is acceptable if the team does not require GTM governance.
- GA4 property settings, data retention, referral exclusions, internal traffic, Search Console linking, and conversion definitions require account access.

## 11. E-Commerce

Status: Not a transactional e-commerce site.

- No cart, checkout, payment gateway, inventory sync, or customer login was found.
- The relevant funnel is product discovery to sample/RFQ/contact. Product pages should state MOQ, specification basis, packaging options, Incoterm basis, lead-time caveat, and evidence availability without implying live inventory or guaranteed pricing.

## 12. Design

Status: Cohesive visual system with some page-weight tradeoffs.

- Green, gold, navy, serif headings, and restrained white surfaces consistently support the export/agriculture brand.
- Header/footer and representative pages remain responsive with no tested horizontal overflow.
- Use the strongest authentic photography selectively. Repeating large image-led sections increases page weight and visual fatigue; alternate photography with compact evidence, specifications, process, and CTA bands.

## 13. Advanced Audit

Status: Partially testable from a static repository.

- JavaScript remains progressively compatible because core page content is static HTML, but filters/calculators and shared injected header/footer require browser testing.
- No application API/database layer was found beyond the external form submission endpoint.
- Log-file crawl analysis is unavailable on GitHub Pages. Use Cloudflare Logpush/analytics and GSC crawl statistics if enabled.
- AI-search readiness benefits from factual entity consistency, concise answer blocks, primary-source citations, author/reviewer identity, and updated Article/FAQ/Breadcrumb schema. Avoid creating repetitive pages solely for AI/search coverage.

## 14. Legal And Compliance

Status: Core pages exist; legal review required.

- Privacy, terms, cookie consent, and cookie preference reopening are present.
- Privacy wording was corrected so it no longer promises that data is never shared while third-party analytics/forms are used.
- Counsel should validate GDPR/UK GDPR, India DPDP applicability, retention periods, processor list, international transfers, lawful bases, and user-rights workflow.
- Keep image licenses/source records and permission for logos, certifications, testimonials, and customer marks.

## 15. Competitor Audit

Status: Public positioning review completed; quantitative comparison needs tools.

- JFT differentiates through catalogue breadth, multilingual product coverage, calculators, quality/infrastructure detail, and multiple region-specific trade hubs.
- Specialist competitors often communicate a narrower promise faster. Strengthen category hubs for rice, spices, oilseeds, feed ingredients, and botanicals with verifiable specifications, downloadable evidence, and destination-focused buying guidance.
- Traffic, ranking overlap, authority, and backlink gaps require Semrush/Ahrefs plus first-party Search Console data.

## Priority Roadmap

### P0: Before/Immediately After Deployment

- Deploy the corrected sitemap, robots, analytics, privacy, content, image, and homepage changes.
- Submit the sitemap in Search Console and inspect several English and translated product URLs.
- Configure security headers in Cloudflare, beginning CSP in report-only mode.
- Validate GA4 events and conversions in DebugView.
- Re-run the production sitemap crawl after Cloudflare cache propagation.

### P1: Next Engineering Cycle

- Refactor the product catalogue to render only visible items.
- Resolve the homepage carousel LCP instrumentation/paint issue and verify under mobile throttling.
- Add responsive derivatives for the 12 remaining large images and defer the homepage video.
- Human-edit localized metadata with priority based on Search Console impressions.

### P2: Growth And Governance

- Establish evidence owners and review dates for certifications, capacities, rates, trade rules, and commercial statements.
- Build GSC/GA4 dashboards for organic landing pages, qualified leads, conversion rate, and content decay.
- Run the authenticated backlink/competitor gap audit.
- Complete keyboard and screen-reader acceptance testing and obtain legal review.

## Audit Artifacts

- `reports/full-site-audit.md`
- `reports/full-site-audit.json`
- `reports/browser-metrics.json`
- `reports/live-sitemap-crawl.json`
- `scripts/full_site_audit.py`
- `scripts/live_sitemap_crawl.py`
- `scripts/browser_metrics.cjs`
- `scripts/audit_commercial_content.py`

## External Access Needed For Closure

Google Search Console, GA4, Cloudflare, GitHub organization/security settings, Semrush/Ahrefs/Moz, and any backup/logging provider. Without these, indexing coverage, real-user Core Web Vitals, backlinks, traffic/conversions, firewall posture, deployment 2FA, and recovery readiness remain explicitly unverified.
