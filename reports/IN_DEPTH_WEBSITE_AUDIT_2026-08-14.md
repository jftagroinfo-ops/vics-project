# JFT Agro Website — In-Depth Audit

**Audit date:** 14 August 2026  
**Website:** https://jftagro.com/  
**Scope:** production delivery plus the complete static repository

## Executive summary

The website has a strong technical SEO foundation and a notably complete B2B export experience. Its main risks are not basic crawlability: they are slow homepage rendering, accessibility defects, international publishing governance, unverified business claims/content freshness, missing production security headers, and incomplete access to outcome data.

### Overall scorecard

| Area | Rating | Summary |
|---|---:|---|
| Technical SEO | 9/10 | Clean canonical structure, valid sitemap/hreflang, real 404 status, no local crawl defects |
| Performance | 6/10 | Lighthouse 67 mobile / 72 desktop; homepage LCP is the dominant problem |
| Security | 6/10 | Valid TLS 1.3 and Cloudflare, but important HTTP headers and operational controls are unverified |
| On-page SEO | 9/10 | Excellent metadata, headings, internal links, image attributes, and schema coverage |
| Off-page SEO | 4/10 (limited evidence) | Legitimate entity citations exist, but backlink authority cannot be quantified without a backlink index |
| UX and design | 8/10 | Professional and responsive, but dense homepage, oversized consent UI, and competing messages |
| CRO | 7/10 | Strong RFQ paths and event instrumentation; no reliable funnel outcome data was available |
| Content | 6/10 | Broad coverage, but many thin articles and several time-sensitive assertions require evidence/review |
| Accessibility | 6/10 | Good baseline semantics, but repeatable WCAG AA failures remain |
| Analytics | 7/10 | GA4 and conversion events are implemented with consent; production data/configuration was not accessible |
| Legal/compliance | 7/10 | Privacy, terms, consent and photo credits exist; legal/localization review and vendor details need strengthening |

### Highest-priority findings

1. **Critical business risk — verify claims before promotion.** The homepage makes numerous specific claims such as “Top 3%,” “every certification is active,” 250 MT/day, 500+ containers/year, 25+ countries, 382+ TEU/year, carrier slot agreements, “every container” testing, and 48-hour customs clearance. Current documents can be requested, but most claims are not directly substantiated on the page. Some figures also vary between sections. Treat these as claims requiring an owner, source, review date, and public evidence where appropriate.
2. **High — homepage LCP is poor.** Lighthouse measured a 19.5 s mobile LCP and 5.7 s desktop LCP, despite good CLS and zero total blocking time. It estimated 1.20–1.26 MB of image-delivery savings. The homepage transfers about 3.2–3.4 MB and has roughly 1,920 DOM nodes.
3. **High — international publishing policy has drifted.** All ten locale folders now contain 129 indexable pages each, while `localization-review.json` says only four priority locales are published and still require native legal review; six locales are documented as English fallbacks. Technical hreflang is sound, but indexability should be reconciled with actual native commercial/legal approval.
4. **High — accessibility failures are repeatable.** Axe found serious contrast failures, non-keyboard-accessible scrolling regions, undersized targets, and ten blog-card links without accessible names. Lighthouse scored accessibility 94 mobile and 97 desktop, which is good but not WCAG conformance.
5. **High — production security headers are incomplete.** HTTPS and TLS are sound, but the live homepage response lacks HSTS and common defense-in-depth headers. CSP is delivered through HTML metadata, allows `'unsafe-inline'` and `'unsafe-eval'`, and blocks Cloudflare's own injected analytics beacon.
6. **High — content quality is uneven.** Of 27 indexable English blog articles, 23 contain fewer than 800 words in the main article area and several are near 300 words. Thinness alone is not a ranking violation, but many topics claim to be comprehensive buyer guides or market outlooks and need stronger sourcing, authorship, dates, and distinct value.

## Method and evidence

- Parsed and validated **1,672 renderable HTML pages** using the repository's exhaustive structural audit: zero findings for references, fragments, canonical basics, headings, IDs, images, forms, schema parsing, and new-tab safety.
- Cross-checked **1,403 sitemap URLs** against **1,403 indexable pages** locally: zero sitemap omissions, duplicates, missing files, or noindex entries.
- Audited **84 English product pages** for commercial completeness and uniqueness: zero rule failures.
- Audited 10 locale directories, 155 renderable pages each, and representative live/browser behavior.
- Ran Chromium at mobile and desktop sizes across representative homepage, catalogue, product, blog, contact, calculator, sample, and Arabic routes.
- Ran axe-core WCAG 2.0/2.1/2.2 A/AA rules on eight representative mobile pages.
- Ran Lighthouse against the live homepage on 14 August 2026.
- Tested live HTTP/HTTPS variants, 404 behavior, TLS, response headers, caching, robots.txt, and `security.txt`.
- Used public search results for competitor/entity discovery. Backlink counts, rankings, Search Console coverage, GA4 outcomes, WAF events, and origin logs require owner account access and are not guessed in this report.

## 1. Technical SEO

### What passes

- `http://jftagro.com/` redirects in one hop to `https://jftagro.com/`.
- `https://www.jftagro.com/` redirects in one hop to the canonical apex hostname.
- A deliberately nonexistent URL returned a real HTTP 404, not a soft 404.
- `robots.txt` is publicly available, permits important content/assets, blocks audit/helper paths, and declares the sitemap.
- The XML sitemap contains 1,403 unique indexable routes and passes local file/noindex parity checks.
- Canonicals are self-referencing and consistent with the public HTTPS hostname under the full-site audit.
- URLs are descriptive and keyword-based, for example `/1121-basmati-rice-exporter.html` and `/blog-how-to-export-india-to-africa.html`.
- Every representative viewport had no horizontal overflow.
- Product and article content is server-rendered HTML; search engines do not depend on client JavaScript for primary copy.
- Pagination is not required for the current catalogue/blog architecture. Filters do not create uncontrolled crawl combinations.

### Findings and actions

**High — reconcile locale indexation with review policy.** Technically, hreflang is comprehensive: alternate links include English, ten locales, and `x-default`, and localized HTML uses appropriate `lang` values. Operationally, the review manifest says Arabic, Spanish, French, and Russian homepage publishing still requires native legal review and identifies Indonesian, Malay, Portuguese, Sinhala, Thai, and Vietnamese as fallback locales. Current files show 129 indexable pages in every locale. Either document native approval for every indexable locale/page family or restore `noindex,follow` and exclude unapproved URLs from sitemap/hreflang clusters.

**Medium — complete the production crawl in a rate-aware job.** An interrupted live sample checked 1,103 routes: 1,102 returned 200 and one Malay product URL transiently returned 503; 14 took more than two seconds. A later full run became excessively slow. This points to intermittent edge/origin latency rather than a confirmed persistent broken route. Update the crawler to use retries, lower concurrency, checkpointing, GET fallback when HEAD is unreliable, p50/p95 latency, and a maximum error-rate threshold.

**Medium — verify actual Google index coverage.** Public search confirms the domain and some English/French pages are indexed, but only Search Console can identify “Crawled — currently not indexed,” duplicate/canonical choices, discovered-not-indexed URLs, manual actions, and per-locale coverage. Submit the sitemap and export the Pages, Sitemaps, Enhancements, and Core Web Vitals reports monthly.

**Low — remove obsolete crawler directives.** `Crawl-delay` is ignored by Google and not necessary for a CDN-backed static site. It is harmless but makes the file noisier. Disallowing source scripts is sensible, although those files should ideally not be deployed at all.

## 2. Performance and speed

### Measured results

| Metric | Mobile | Desktop |
|---|---:|---:|
| Lighthouse performance | 67 | 72 |
| FCP | 3.5 s | 1.2 s |
| LCP | 19.5 s | 5.7 s |
| Speed Index | 4.0 s | 1.5 s |
| CLS | 0.015 | 0.003 |
| Total Blocking Time | 0 ms | 0 ms |
| Root response in Lighthouse | 290 ms | 310 ms |
| Total homepage payload | 3,242 KiB | 3,423 KiB |
| Estimated image savings | 1,261 KiB | 1,202 KiB |

The PageSpeed Insights API was quota-blocked, so this report does not claim CrUX field data. Lighthouse is lab data; Search Console/CrUX should decide whether real users pass Core Web Vitals.

### Findings and actions

**High — repair the homepage LCP candidate and its discovery priority.** The absence of a stable LCP entry in two direct browser traces, together with Lighthouse's extremely late LCP, suggests the rotating/background hero makes the primary paint difficult to prioritize. Use one initial `<picture><img>` hero with `fetchpriority="high"`, explicit dimensions, mobile-specific crops and no lazy loading. Load later carousel images only after interaction/idle. Consider reducing six slides to one or three.

**High — reduce image payload.** Lighthouse identified more than 1.2 MB of potential savings. Generate responsive `srcset` variants, ensure the browser is not downloading desktop images on mobile, increase WebP/AVIF compression where visually acceptable, and keep decorative below-fold images lazy. Repository outliers include a 3.57 MB vessel JPEG, an 843 KB editorial WebP, numerous 300–500 KB product images, and a 5.04 MB homepage video.

**Medium — reduce document/DOM complexity.** `index.html` is 236 KB and produces about 1,920 nodes. `products.html` produces 1,485–1,780 nodes. Split below-fold sections into smaller rendered components, remove repeated marketing blocks, and paginate/virtualize catalogue cards if the product count grows.

**Medium — improve HTML caching.** Static CSS receives a one-year cache lifetime, which is good, but the homepage uses a ten-minute max-age and Cloudflare reports `DYNAMIC`. Add immutable hashed asset names and evaluate caching HTML at the Cloudflare edge with safe purge-on-deploy. Production browser TTFB was usually around 0.6–1.3 s but one catalogue request reached 9 s, confirming variable edge delivery.

**Medium — eliminate render-blocking CSS and font dependencies.** Lighthouse flagged render-blocking requests and about 21 KB of unused CSS. Inline only genuinely critical above-fold rules, defer noncritical CSS, self-host/subset the fonts already present in `assets/fonts`, and avoid loading full Font Awesome sets when a small icon subset/SVG sprite suffices.

## 3. Security

### What passes

- Certificate CN is `jftagro.com`, issued by Google Trust Services, valid 22 July–21 October 2026.
- TLS 1.3 negotiated successfully.
- HTTP and `www` consistently redirect to canonical HTTPS.
- Cloudflare fronts GitHub Pages.
- No authentication, database, session, admin login, checkout, or first-party backend exists in this repository, reducing the application attack surface.
- `/.well-known/security.txt` publishes a contact, policy, canonical URL, and expiry.
- The existing code audit reports no private keys, common cloud/API secrets, `eval()` or `new Function()`.

### Findings and actions

**High — add HTTP security headers at Cloudflare.** Live responses did not include `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, or frame protection. Add these through Cloudflare Transform Rules/Workers. Prefer a response-header CSP because `<meta http-equiv>` cannot enforce every CSP feature.

**High — remove CSP unsafe allowances over time.** Current CSP permits `'unsafe-inline'` and `'unsafe-eval'`. Extract inline scripts/styles, use nonces or hashes, and remove origins no longer needed. Cloudflare's injected beacon currently fails with a CSP error; either explicitly allow `https://static.cloudflareinsights.com` and its reporting endpoint if Cloudflare analytics is desired, or disable beacon injection.

**Medium — protect lead forms from spam/abuse.** The Web3Forms public access key is necessarily client-visible, but the submission payload sets an empty honeypot and there is no visible Turnstile/CAPTCHA. Restrict accepted domains in Web3Forms, add Cloudflare Turnstile or equivalent risk checks, rate-limit the endpoint path where possible, rotate the key if abused, and monitor delivery failures.

**Needs owner verification:** Cloudflare WAF/bot rules, DNSSEC, account 2FA, registrar lock, GitHub branch protection, secret-scanning alerts, malware monitoring, backup restore tests, and incident notification. Git history is useful but is not a documented disaster-recovery backup by itself.

## 4. On-page SEO

### What passes

- Unique titles, descriptions, canonicals, one-H1 structure, image alt/dimensions, internal references, and JSON-LD parsing passed across 1,672 pages.
- Strong keyword-aligned product URLs and titles cover rice, spices, grains, pulses, seeds, feed, and botanicals.
- Structured data coverage is extensive: Organization, Product, AggregateOffer, FAQPage, BreadcrumbList, Article, HowTo, ItemList, WebApplication, and related entities.
- Internal pathways connect articles to products, calculators, samples, regional guides, and RFQs.

### Findings and actions

**High — audit the truth and eligibility of structured data.** Large schema volume is not inherently beneficial. Product `AggregateOffer`, FAQ, certification, rating/review-like, and availability data must exactly match visible content and Google's eligibility policies. Run representative URLs through Rich Results Test and Search Console enhancement reports after every template change.

**Medium — align copy with search intent, not just exact keywords.** Product pages are structurally complete, but many share the same commercial template. Add genuinely product-specific buyer questions: crop calendar, origin, tolerances, pesticide/MRL concerns, target-market documents, use cases, packing, and lab parameters.

**Medium — add source citations and named expert review.** Market outlook and compliance content should cite APEDA, DGFT, Spices Board, FSSAI, customs authorities, Codex/EU/US regulations, or current market sources. Add reviewer credentials and a meaningful `dateModified` when facts change.

## 5. Off-page SEO

Public evidence supports a real entity footprint: Bloomberg LEI lists JFT Agro Overseas LLP and its Navi Mumbai address; corporate-directory listings exist; and a Jawaharlal Nehru Customs public notice includes the company name in a shipping record. These are useful trust/entity signals.

No defensible domain-authority, referring-domain, toxic-link, anchor-text, or competitor-link-gap numbers can be produced without Ahrefs, Semrush, Moz, Majestic, Search Console Links, or equivalent access.

Recommended export:

1. Referring domains and dofollow/nofollow distribution.
2. New/lost links for 12 months.
3. Exact/partial/branded/naked anchor distribution.
4. Links to noncanonical/404/legacy URLs.
5. Competitor intersect against Vilora Impex, Trade Pros, TRION EXIM and two scale-matched exporters selected by the business—not giant consumer brands alone.
6. Prioritize legitimate trade associations, chambers, government/export directories, laboratories, event exhibitor pages, logistics partners, and buyer-relevant editorial coverage. Do not buy bulk directory links.

## 6. UX

### Strengths

- Professional green/gold visual identity and credible factory/logistics imagery.
- Clear product, quote, WhatsApp, sample, calculator, and verification routes.
- Mobile layouts did not overflow at 390 px, and the menu is keyboard-operable in representative checks.
- Buyers receive due-diligence guidance, documentation explanations, and visible contact options.

### Findings

**High — reduce homepage cognitive load.** The homepage contains six hero messages, extensive credentials, roles, origins, catalogue, RFQ, process, logistics, trust marks, markets, due diligence, and multiple final CTAs. Keep a single primary narrative: proof → product → verification → quote. Move secondary corporate detail to dedicated pages.

**Medium — reduce first-screen obstruction.** On mobile the consent panel consumes a large portion of the initial viewport. Make the copy shorter, retain equal clarity for accept/reject, and provide preferences without obscuring core content.

**Medium — avoid negative news in the trust-critical header.** Headlines about “red flags,” poisonous foods, war, and export stress can reduce buyer confidence when shown before the company proposition. Curate the ticker for neutral, decision-useful buyer intelligence or move it below the hero.

**Medium — test real journeys.** Use GA4 explorations or privacy-respecting session recordings to compare these paths: landing → product → quote; article → product → quote; calculator → RFQ; WhatsApp click; and sample request. Segment by mobile/desktop, country, locale, product category, and source.

## 7. Conversion-rate optimization

### What exists

- Clear RFQ, WhatsApp, phone, email, sample, catalogue, and calculator CTAs.
- UTM/click-ID attribution is stored per session and added to forms.
- `form_start`, `generate_lead`, contact-channel clicks, article depth, article-to-product/calculator/RFQ, quote-to-RFQ, downloads, outbound clicks, and 404 events are implemented.
- Forms include validation, submission state, fallback contact information, privacy agreement, lead IDs, and commercial qualification fields.

### Findings and actions

**High — define the measurable funnel in GA4.** Mark `generate_lead` as a key event and create funnel explorations for landing → product_view → form_start → generate_lead. The current code has no explicit universal `view_item`/product-view event, so add consistent product/category parameters.

**Medium — reduce CTA competition.** Browse, quote, WhatsApp, sample, catalogue, pricing and calculators compete across long pages. Choose one primary action per page intent and one secondary reassurance action.

**Medium — add qualified trust at decision points.** Near forms, show concise verified evidence, response time, required buyer inputs, privacy/use statement, and what happens next. Avoid unverified urgency or guaranteed outcomes.

**Medium — establish an experimentation process.** No A/B framework was found. Start with server/static split URLs or a consent-respecting experiment tool. Test one hypothesis at a time: hero proposition, proof module, CTA label, shorter form, and sample-vs-quote path. Determine success using qualified leads, not button clicks.

There is no ecommerce checkout, cart or payment gateway; checkout optimization is not applicable.

## 8. Content

- The catalogue covers 84 products and the English blog has 27 indexable articles plus noindex/legacy content.
- The median main-content length among indexable English articles is approximately 489 words; 23 of 27 are under 800 words. Several buyer/compliance guides are around 276–363 words.
- Dates cluster heavily on 14 May and 12 August 2026. This may be legitimate, but bulk publishing patterns require strong editorial review and differentiated value.
- Time-sensitive market articles include precise production, price, demand and regulatory claims. They need citations, “data as of” labels, and scheduled expiry/review.

Recommended content model:

1. Build pillar pages for rice importing, spice compliance, documentation/payment, quality inspection, and regional market entry.
2. Consolidate overlapping thin posts into stronger resources; redirect retired URLs.
3. Add primary-source citations, named reviewer, last verified date, and correction/contact mechanism.
4. Add first-party evidence: anonymized inspection examples, packing diagrams, sample approval templates, document checklists, and facility/process photography.
5. Use Search Console query/page exports to decide which pages to update, consolidate, retain or noindex. Without impressions/clicks, “low-performing” cannot be reliably classified.

## 9. Accessibility

Representative axe results found:

- 22 contrast failures on the catalogue and 25 on a product detail page in one run; blog cards and calculator helper text also failed contrast.
- Four homepage horizontal/scrolling regions and recurring forex tickers were not keyboard-focusable.
- Footer cookie-preference and sitemap targets failed the WCAG 2.2 target-size rule.
- Ten blog article links had no accessible name because JavaScript applies `role="article"` directly to `<a>` elements. Remove that role or wrap links in a semantic `<article>`.
- Sample and some localized pages contain form controls that need manual label verification beyond the static rule set.

Fix shared header/footer defects first because they affect most pages. Then fix catalogue/product color tokens, blog card semantics, carousel/scrollable regions, and perform manual screen-reader tests in NVDA + Chrome/Firefox and VoiceOver + Safari. Automated scores do not establish WCAG conformance.

## 10. Analytics and tracking

- GA4 measurement ID `G-MWZ2ZWZP4G` is implemented and loads only after explicit analytics consent.
- “Essential Only” prevents GA from loading, and preferences can be reopened.
- No active GTM container is present; the GTM block is only a commented placeholder. This is acceptable if direct GA4 is intentional.
- Event coverage is strong, but DebugView/Realtime verification, cross-domain settings, internal-traffic filters, referral exclusions, key events, retention, audiences, and data accuracy require GA property access.
- Cloudflare's analytics beacon is injected but blocked by CSP. Decide whether to allow it or disable it to avoid noisy failed requests and missing Cloudflare analytics.
- Add a tracking QA matrix and validate event name, parameters, consent state, duplicates, form success-only firing, and locale attribution before each release.

## 11. Ecommerce

The site is a B2B lead-generation catalogue, not an ecommerce store. Cart abandonment, inventory synchronization, checkout and payment gateways are not applicable. Product-page optimization, pricing clarity and trust signals are applicable:

- Keep price ranges clearly labeled as reference-only and timestamp the underlying feed.
- Never imply stock availability unless inventory is verified; many localized product pages contain “Ready stock” messaging.
- Show MOQ, packaging, incoterm, validity, source date and inspection/document assumptions consistently.
- Consider buyer testimonials only when authentic, permissioned and verifiable.

## 12. Design

Branding, palette, typography and component style are consistent and distinctive. Responsive behavior is good. The main design weakness is excess: too many sections, badges, numbers, cards, tickers and CTA styles dilute hierarchy. Standardize one primary button, one secondary button, one proof-card style, and shorter page-level narratives. Ensure small uppercase Montserrat labels meet size/contrast requirements.

## 13. Advanced audit

- **Log files:** unavailable. Cloudflare/GitHub request logs are needed for Googlebot frequency, wasted crawl, status patterns and slow paths.
- **JavaScript SEO:** primary content is server rendered and works without third-party scripts. Shared header/footer are client-injected, so primary navigation may be less robust for non-rendering crawlers; include core internal links in initial HTML or at least a static noscript/navigation fallback.
- **Server/database/API:** no application server or database exists locally. GitHub Pages + Cloudflare reduces tuning options; origin performance, Cloudflare cache rules and third-party APIs are the relevant layer.
- **API reliability:** quote data has validation/fallback documentation. Web3Forms live delivery was deliberately not tested to avoid a real lead. Currency/news/translation endpoints should fail gracefully and be monitored.
- **AI search optimization:** the site already has clear entity/product/schema data and crawlable answer-style content. Improve factual citations, author/reviewer identity, consistent organization identifiers (`sameAs`, LEI where appropriate), concise answer blocks, and verifiable first-party evidence. Do not create extra AI-targeted duplicate pages.

## 14. Legal and compliance

### What exists

- Privacy Policy with data categories, uses, Web3Forms disclosure, 24-month inquiry review, analytics consent, data rights and contact.
- Terms of Trade, payment, shipping, inspection, force majeure and dispute language.
- Equal accept/essential-only consent choices and preference reopening.
- Photo credits identify Pexels images and sources.
- Security contact and policy endpoint.

### Findings

**High — obtain legal review for trade and privacy wording.** This is an operational audit, not legal advice. The terms contain material commercial commitments and should be reviewed for governing law, arbitration mechanism/seat/rules, limitation of liability, title/risk transfer, sanctions/export controls, claims procedure, product tolerances, insurance, cancellations, and precedence of signed contract over website terms.

**High — reconcile multilingual legal publication.** Indexable translated legal/commercial pages require competent native and jurisdiction-aware review. The current manifest still says review is required.

**Medium — expand the privacy notice.** Add legal entity/registered address, controller status, lawful bases where GDPR applies, international transfers, vendor links, complaint/supervisory-authority rights, consent withdrawal consequences, security summary, children's data, and precise newsletter opt-out method.

**Medium — maintain an asset register.** The Pexels credit file is good, but retain source/license records for every third-party photo, logo, flag, certification mark, font and PDF—not only the seven documented photos.

## 15. Competitor audit

The closest public search competitors observed were Vilora Impex, Trade Pros, and TRION EXIM. Larger category incumbents such as KRBL and LT Foods are useful benchmarks for trust and branded search, but they are not always fair SEO peers.

| Dimension | JFT Agro | Competitor pattern | Opportunity |
|---|---|---|---|
| Product breadth | Very broad, 84 products | Competitors often focus on fewer rice/spice/fresh categories | Retain breadth but create clearer category authority hubs |
| Buyer tools | Strong calculators, samples, verification and regional pages | Many competitors use simpler brochure/catalogue funnels | Promote tools as the differentiator and measure tool-to-lead conversion |
| Proof | Many detailed claims and certificates-on-request | Competitors emphasize registrations and destination compliance | Publish current redacted proof and source claims more directly |
| Content | Broad but uneven depth | Search competitors often use long keyword-led landing copy | Win through cited, buyer-useful, expert-reviewed resources rather than volume |
| Regional targeting | Ten languages and dedicated regions | Competitors commonly target Gulf/Africa/SE Asia in English | Only index translations with native review and local market value |
| Brand authority | Some legitimate entity/customs citations | Larger firms have stronger branded demand/distribution | Earn trade-body, event, lab, logistics and buyer-industry citations |

The next competitor phase should use Search Console plus Ahrefs/Semrush exports to compare nonbranded keywords, ranking URLs, referring-domain overlap, content decay and country-specific SERPs. Public search alone cannot estimate traffic or authority accurately.

## Prioritized remediation roadmap

### First 14 days

1. Replace/prioritize the initial hero image and defer later carousel media; rerun Lighthouse.
2. Fix blog link semantics, shared target sizes, scrollable-region keyboard access, and high-volume contrast failures.
3. Add Cloudflare response security headers; resolve the Cloudflare beacon/CSP conflict.
4. Reconcile every locale's index/noindex state with native commercial/legal review.
5. Create a claims register and remove, qualify or substantiate claims lacking current proof.

### Days 15–45

1. Generate responsive AVIF/WebP image variants and introduce strict page-weight/LCP budgets in CI.
2. Consolidate the homepage and reduce CTA competition.
3. Configure GA4 key events/funnels and verify events in DebugView with all consent states.
4. Add form abuse protection and complete Cloudflare/GitHub/account-security review.
5. Consolidate or deepen thin articles; add sources, reviewer and last-verified dates.

### Days 46–90

1. Use Search Console coverage/query exports to prioritize indexation and content work.
2. Run a backlink/competitor intersect and pursue legitimate industry citations.
3. Complete screen-reader/browser testing and document WCAG remediation.
4. Add rate-aware full production crawl, p95 latency monitoring, CWV monitoring, and restore drills.
5. Run controlled CRO tests using qualified-lead rate as the primary metric.

## Access required to close the remaining evidence gaps

- Google Search Console: indexing, queries, CWV, enhancements, links, manual actions.
- GA4: traffic quality, funnels, bounce/engagement, conversions, attribution and locale performance.
- Cloudflare: WAF, bots, DNSSEC, cache hit ratio, Web Analytics, logs and security events.
- GitHub/domain registrar: 2FA, branch protection, account recovery, DNS/registrar lock and backup procedures.
- Web3Forms: allowed domains, spam controls, delivery logs and retention terms.
- Ahrefs/Semrush/Moz: backlink authority, toxicity review, anchor distribution and competitor gaps.

## Bottom line

The website is technically mature and search-engine-readable. The highest return now comes from making it faster, more provable, more accessible and more measurable—not from publishing more pages. A smaller, faster homepage; approved international pages; evidence-backed claims; remediated WCAG defects; and closed-loop lead analytics would materially improve both trust and conversion quality.
