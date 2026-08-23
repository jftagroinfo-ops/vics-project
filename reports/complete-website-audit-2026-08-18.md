# JFT Agro Complete Website Audit — 18 August 2026

## Executive result

The post-rollback website is operational and technically healthy. Static auditing found no broken internal links, schema parsing failures, commercial-content defects, claim-policy defects, or blog navigation failures. The principal remaining issue is homepage rendering cost on throttled mobile hardware.

## Scope and evidence

- Full static crawl: 1,678 renderable HTML pages.
- Indexable pages: 1,378; sitemap URLs: 1,378.
- Link scan: 3,404 HTML files including the deployment copy; 0 unique broken links.
- Commercial audit: 84 English product pages; 0 findings.
- Blog audit: 229 published cards and 66 legacy redirects; passed.
- Live route checks: homepage, products, representative product, blog, article, contact, sitemap and robots returned HTTP 200; a deliberately missing route returned HTTP 404.
- Recorded full production sitemap crawl: all 1,378 URLs returned HTTP 200 with no failures.
- Desktop and mobile Lighthouse navigation audits: 100 SEO, 100 Accessibility, 100 Best Practices and 100 Agentic Browsing.

## Performance

| Test | LCP | CLS | Assessment |
|---|---:|---:|---|
| Desktop, unthrottled | 1.817 s | 0.00 | Good |
| Mobile, Slow 4G and 4× CPU slowdown | 4.110 s | 0.01 | LCP poor; CLS good |

The responsive WebP hero downloaded quickly. Mobile LCP was dominated by 3.536 seconds of element render delay, not image transfer. The homepage contains about 1,781 DOM elements and produced approximately 708 ms of forced reflow under the throttled mobile test. Primary sources are carousel measurements using `scrollWidth`, `getComputedStyle`, `getBoundingClientRect`, and repeated layout work during initialization.

## SEO and indexing

- Every current indexable page is represented in the sitemap.
- Canonical tags and the representative live product canonical are correct.
- Product pages now use WebPage/Thing schema rather than unsupported Product rich-result markup without offers or reviews.
- Structured-data, title, metadata and claim audits passed.
- HTTPS and `www` consolidate to the canonical HTTPS apex origin with permanent redirects.
- Three new English buyer articles are not yet available in the ten locale directories. This produces 30 multilingual coverage gaps but no fallback or high-English-residue pages.

## Security, privacy and legal

Present and correct: HTTPS, one-year HSTS with subdomains, `X-Content-Type-Options`, `X-Frame-Options`, referrer policy, permissions policy, COOP, privacy policy, terms, cookie preferences and security contact file.

The Content Security Policy remains `Report-Only`. It records violations but does not block disallowed resources. Moving it to enforcement should happen only after reviewing violation reports and testing forms, translation, analytics and embedded maps.

## UX, accessibility and contact

- Desktop and mobile Lighthouse accessibility passed at 100.
- Contact page accessibility tree includes skip navigation, named regions, labelled controls, visible CTAs and cookie controls.
- No console warnings or errors were found on the contact-page check.
- Public contact details use `jftagro.info@gmail.com`, primary `+91 84250 57274`, and secondary `+91 86523 62771`.
- Privacy and terms links are available from the footer.

## Images and caching

- No image or asset in the audited `images` and `assets` directories exceeds 500 KB.
- The hero uses a responsive mobile WebP variant and high request priority.
- Static images use a seven-day browser cache. DevTools estimated zero FCP/LCP savings from extending it, so this is not an immediate priority.
- A few logos lack explicit dimensions, but observed layout shift remains very small.

## Priority actions

1. Reduce mobile render delay by batching homepage DOM construction and layout measurement, and calculate carousel geometry once after content is ready.
2. Reduce the homepage DOM size, especially duplicated ticker/carousel/certificate nodes.
3. Translate the three newest buyer articles into the ten supported locale directories and add them to locale navigation/hreflang clusters.
4. Add explicit dimensions or aspect ratios to navigation and certificate logos.
5. Review CSP violation telemetry, then progressively enforce the CSP.

## External-data limitation

This audit verifies the live website and repository. Google Search Console indexing decisions, GA conversion accuracy, backlink toxicity, search rankings and real-user Core Web Vitals require access to those provider datasets and are not inferred from the site code.

## Implementation update — 18 August 2026

All five priority actions above were implemented and deployed to Cloudflare Worker version `aa1ddc08-7cf3-45af-a33a-52a037eaa706`.

- Homepage certificate, region and trade-network work now initializes near the viewport. Mobile uses ten native-scroll certificate cards instead of twenty animated/cloned cards.
- The comparable mobile Slow 4G / 4× CPU lab trace measured LCP at 0.928 s, CLS at 0.01, 1,547 DOM elements and 90 ms total forced-reflow time. The original audit measured 4.110 s, 0.01, about 1,781 elements and about 708 ms respectively.
- The three newest buyer guides were fully translated into all ten supported languages and linked from every localized blog index. No English fallback markers remain.
- Canonical and hreflang metadata was regenerated across 1,428 indexable URLs. The sitemap now contains the same 1,428 URLs.
- Navigation and certification logos now reserve their display geometry.
- CSP is enforced by the Worker response header. Live homepage, localized article and product checks produced no CSP console errors.
- Final audit: 3,456 renderable source/deployment documents, zero findings; mobile Lighthouse scored 100 for SEO, Accessibility, Best Practices and Agentic Browsing.
