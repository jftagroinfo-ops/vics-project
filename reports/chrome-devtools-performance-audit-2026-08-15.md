# jftagro.com Chrome DevTools Performance Audit

Audit date: 2026-08-15  
Production host: `https://jftagro.com/`  
Deployment tested: Cloudflare Worker Static Assets

## Results

| Profile | LCP | CLS | TTFB | Assessment |
|---|---:|---:|---:|---|
| Desktop, Fast 4G, 1x CPU | 1.80 s | 0.01 | 338 ms | Good |
| Mobile confirmation, Slow 4G, 4x CPU | 3.27 s | 0.012 | 645 ms | LCP needs improvement |
| Mobile worst observed, Slow 4G, 4x CPU | 7.10 s | 0.01 | 718 ms | Poor LCP |

Mobile cold-load LCP varied from 3.27 s to 7.10 s across confirmation runs. No Chrome UX Report field data was available, so these are lab measurements rather than real-user percentiles.

Lighthouse navigation audit (mobile):

- Accessibility: 100
- Best Practices: 100
- SEO: 100
- Agentic Browsing: 100
- 57 passed, 0 failed

## Changes deployed during the audit

- Added breakpoint-specific preload hints for the hero image.
- Preloaded the navigation logo and marked it high priority.
- Removed duplicate font and Font Awesome stylesheet tags from the inlined header.
- Added an early `font-display: swap` override for the Font Awesome solid and brand fonts.
- Cached the certification-slider width instead of reading `scrollWidth` on every animation frame.
- Corrected a failing heading color contrast rule.
- Removed `upgrade-insecure-requests` from the report-only CSP because browsers ignore it in report-only mode and log a warning.

## Remaining priorities

1. Reduce the homepage DOM (1,771 elements) and split below-the-fold sections out of the initial HTML. The document is about 300 KB decoded and the hero element appears around 64% into the markup.
2. Generate smaller responsive assets for `images/14.webp`, `images/homepage/spices-category-card.webp`, the navigation logo, and certificate thumbnails. Chrome estimated 493 KB of image savings and up to 450 ms of LCP savings in the slow-mobile trace.
3. Reduce the mobile hero render delay. In the worst trace, 3.26 s of the 7.10 s LCP occurred after the hero image finished downloading; large incremental layout/style work is the principal structural risk.
4. Defer non-critical `locale-ui.js` work and keep below-the-fold sliders dormant until they approach the viewport.
5. Collect real-user Core Web Vitals after traffic accumulates; CrUX did not yet have field data for this origin.

Third-party impact was limited: Cloudflare used about 11.6 KB and 91 ms of main-thread time; flagcdn.com used 8.5 KB and the exchange-rate API used 1.4 KB. Chrome estimated no Core Web Vitals savings from third-party or cache findings.

## Improvement pass

Deployment: `beef4916-8288-4490-9412-9b41572e82c4`

- The English homepage no longer downloads `locale-ui.js`; localized URLs continue to load it conditionally.
- All Font Awesome bundled font faces now use `font-display: swap`. The post-deployment trace no longer reported the Font Display insight.
- Below-the-fold homepage sections use `content-visibility: auto` with an intrinsic block size, reducing initial layout and paint work while retaining the HTML for SEO and accessibility.
- DOM interactive improved from approximately 11.9 s to 7.3 s under the same Slow 4G / 4x CPU profile.
- The first post-deployment trace measured LCP at 5.70 s and CLS at 0.012. That run's TTFB was 1.62 s, about one second slower than the earlier confirmation run; Chrome attributed 1.10 s of possible LCP savings to document latency.
- Hero resource discovery remained healthy: 161 ms load delay, high request priority, no redirect, and compressed HTML.

The remaining dominant cost is the late hero render (2.46 s after image download) plus variable edge/network response time. The 1,771-element DOM remains a longer-term structural optimization target.
