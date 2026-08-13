# External website controls

Last reviewed: 14 August 2026

The repository implements every control that can be safely enforced in source code. The controls below require the account owner, registrar, CDN, analytics, advertising, or legal systems and must be completed outside GitHub.

## Search and indexation

- Verify every site variant in Google Search Console and Bing Webmaster Tools.
- Submit `https://jftagro.com/sitemap.xml`, inspect representative English and localized URLs, and monitor excluded/crawled-not-indexed reports monthly.
- Review Core Web Vitals field data after each release; lab Lighthouse results are diagnostic, not a substitute for 28-day field data.
- Obtain documented native-language approval before expanding indexation of localized legal or high-risk commercial copy.

## Cloudflare, hosting, and security

- Apply `cloudflare-response-headers.example.txt` as a Cloudflare Transform Rule, test report-only CSP, then promote a validated policy to enforcement.
- Enable HSTS only after confirming HTTPS works on all subdomains; then consider preload separately.
- Enable Cloudflare managed WAF rules, bot protection, rate limiting on form endpoints, DNSSEC, and account 2FA.
- Restrict the Web3Forms access key to the production domain, rotate it if it has ever been exposed, and add Turnstile when a production site key is available.
- Enable GitHub organization 2FA, protected branches, dependency alerts, secret scanning, and recoverable backups/export copies.
- Run authenticated vulnerability and malware scans from the authorized Cloudflare/Sucuri account; do not rely on an unauthenticated surface scan alone.

## Analytics and CRO

- In GA4, verify consent-mode signals and mark qualified lead, quote, sample, phone, email, WhatsApp, product-view, and calculator events as appropriate conversions.
- Link Search Console to GA4; exclude internal traffic and confirm cross-domain/referral rules if third-party forms or payment systems are added.
- Validate tags in GTM Preview and GA4 DebugView after deployment. No marketing tag should fire before consent in regions where consent is required.
- Create a monthly funnel report: landing page → product view → form start → qualified submission → sales-qualified lead → won order.
- Run A/B tests only after defining one primary metric, minimum sample size, duration, and a rollback rule. Do not claim a winner from low-volume noise.

## Reputation, content, and legal

- Review and evidence every certification, capacity, country, customer, award, laboratory, logistics, and performance claim using `docs/claims-governance.md`.
- Have qualified counsel review privacy, cookies, sales terms, arbitration, sanctions/export controls, and destination-specific consumer/data rules. Repository text is operational drafting, not legal advice.
- Maintain a quarterly editorial refresh using primary sources (APEDA, DGFT, FSSAI, Spices Board, customs authorities) and record reviewer/date/source changes.
- Audit backlinks in Search Console and a licensed SEO platform; pursue relevant editorial/trade links. Do not purchase links or disavow ordinary low-quality links without evidence of a manual-action risk.
- Benchmark named competitors only with licensed traffic/backlink data and documented keyword methodology.

## Commerce systems

The current site is lead-generation, not an online checkout. Inventory synchronization, payment-gateway hardening, cart abandonment, PCI DSS, refunds, and checkout optimization become mandatory only if transactional commerce is introduced.
