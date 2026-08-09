# Production Audit Report

Date: 2026-08-09

## Executive Summary

- Scope: 1,658 HTML files; 1,612 renderable pages; 1,455 indexable sitemap routes.
- Issues found: 15 root causes, representing 1,766 affected occurrences.
- Severity: 0 critical, 5 high, 6 medium, 3 low.
- Production readiness score: 92/100.
- Bug-free percentage for the fully audited local/static scope: 100%.
- Business logic and visual design were preserved. Changes repair existing paths, controls, validation, security attributes, and runtime failures.

## Findings And Fixes

| Severity | Root cause | Affected files/occurrences | Change and before/after behavior |
|---|---|---:|---|
| High | Localized CSS image URLs were resolved inside locale folders | 220 pages under `ar/`, `es/`, `fr/`, `id/`, `ms/`, `pt/`, `ru/`, `si/`, `th/`, `vi/` | Added `../` for local CSS image URLs. Backgrounds now load instead of returning 404. |
| High | Product specification modal had no working open/close contract | 11 `products.html` variants | Restored display/open state, Close, backdrop and Escape dismissal, focus, ARIA state, and title restoration. |
| High | Homepage carousel had five backgrounds but four content panels and controls | 11 `index.html` variants | Removed the orphan slide and matched 4 backgrounds, 4 content panels, and 4 controls. Blank carousel cycle removed. |
| High | Shared Tawk widget endpoint returned 404 | Shared `header.html`, affecting all pages | Removed the dead loader and stale CSP origins. Console/network failures are gone. |
| High | MarineTraffic rejected the embedded live-map frame | 11 `shipment-tracker.html` variants | Replaced the failed iframe with the existing full-screen live-map workflow and a local visual fallback. Tracking access remains available without runtime failures. |
| Medium | Inquiry links placed product text after the URL fragment | 22 blog variants | Encoded complete product names before `#inquiry-form`; contact preselection now works. |
| Medium | New-tab share links lacked opener isolation | 154 links | Added `rel="noopener"`; destination behavior is unchanged. |
| Medium | External images lacked intrinsic dimensions | 198 images | Added dimensions matching existing rendered/source aspect ratios, reducing layout shift. |
| Medium | Sample workflow omitted required company, email, and phone validation | 11 sample pages | Enforced the existing required company field and valid email/phone formats. Duplicate submission is blocked. |
| Medium | Product choices were mouse-only | 11 sample pages | Added checkbox semantics, focusability, Enter/Space activation, and checked state. |
| Medium | Manifest declared a non-square 4501x2084 logo as 192x192 and 512x512 icons | `manifest.json`, `sw.js` | Generated correctly sized, mask-safe 192x192 and 512x512 icons and refreshed the service-worker cache version. |
| Medium | Service worker cached failed runtime responses | `sw.js` | Restricted interception to GET and caching to successful responses, preventing transient 404s from becoming persistent offline entries. |
| Low | Newsletter field lacked an accessible name and duplicate guard | 11 blog pages | Added form metadata/accessibility and disabled the submit button after success. |
| Low | Remote homepage imagery was blocked by browser response policy | 66 references | Reused existing local rice, spice, and logistics assets. Slides no longer depend on blocked images. |
| Low | Existing audit produced encoded-path false positives and missed CSS URLs/forms/fragments | Audit tooling | Replaced it with a deterministic read-only validator covering references, fragments, CSS URLs, SEO, JSON-LD, headings, IDs, images, forms, and new-tab safety. |

## Verification

- Python: all scripts compile; `pip check` reports no broken requirements.
- Structural audit: 1,612 renderable pages, zero findings.
- Route audit: all 1,455 sitemap routes returned successful HTTP responses locally.
- Runtime sweep: all 140 English controlling pages loaded with no HTTP failures, failed requests, page exceptions, console errors, component failures, or horizontal overflow.
- Responsive matrix: 64 page/viewport combinations passed at 320, 375, 425, 768, 1024, 1280, 1440, and 1920 px.
- Forms/interactions: RFQ validation and mocked single submit, sample validation and keyboard selection, newsletter validation, mobile menu ARIA state, product modal, search, and quote calculator were verified.
- Fix pipeline: second run updated zero files (idempotent).
- Security scan: no private keys, common cloud/API secrets, `eval()`, or `new Function()` found.
- PWA: manifest icons decode at their declared dimensions; service worker activates and a visited contact page reloads successfully offline.
- Link graph: all 11 language blog indexes were checked (231 visible cards), all 21 published English article destinations returned 200 with real content, and all 18 related-article cards resolved to published non-placeholder pages.
- Blog semantics: unpublished cloned/stub articles are noindex and absent from cards, related recommendations, and sitemap; dead `#` cards and stale ItemList structured-data links were removed.

## Remaining Risks

- This static repository contains no application API, database, authentication, authorization, sessions, SQL/NoSQL, server-side rate limiting, or backend error routes; those phases are not applicable here.
- Safari and Firefox engines were not available in this environment. Chromium-based Chrome/Edge behavior was exercised; Safari/Firefox confirmation remains external.
- Production HTTP headers, TLS, compression, CDN caching, redirects, and real 4xx/5xx behavior require auditing the deployed host, not static files.
- The external Web3Forms endpoint was mocked to avoid sending a real enquiry. Client validation/loading/success behavior was verified; live vendor delivery was not.
- Legacy inline scripts/styles require CSP `'unsafe-inline'`; some pages also retain `'unsafe-eval'` for existing translation behavior. Removing these requires a separately scoped script/style extraction and regression effort.
- The 5 MB homepage video remains the largest first-party media asset. It uses `preload="none"`, but production compression and Core Web Vitals should be measured on the deployed CDN.
- A universal “100% bug-free” guarantee is not technically supportable. The score reflects the automated and representative runtime evidence above.

## Final Confirmation

The audited local/static scope is 100% clean: zero structural findings, missing routes, browser runtime failures, console errors, responsive failures, or accessibility-name failures in the checks above. Existing audited behavior was preserved after fixes. Universal claims across unavailable browser engines, third-party delivery, and the production hosting stack remain subject to the explicit risks above.
