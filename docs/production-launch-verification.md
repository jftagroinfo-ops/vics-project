# Production launch verification

The repository now defaults to evidence-led wording. The items below require account access, signed records, independent testing or legal approval and therefore cannot be completed by static-code changes alone.

## Release blockers

1. **Entity and registrations** — obtain current MCA master data and LLP incorporation records for JFT Agro Overseas LLP. Match the legal name, LLPIN, registered office and 2016 registration date. Add the LLPIN to the site only after a responsible officer approves publication.
2. **Export and food credentials** — verify current DGFT status-holder, IEC, APEDA RCMC, FSSAI, Spices Board, ISO, HACCP and any AEO documents against the exact holder, site, product scope, issuer/accreditation, issue date and expiry date. Update `docs/claim-verification-matrix.csv`; do not restore certification badges from a logo or old scan alone.
3. **Facility evidence** — reconcile the public Balap, Raigad processing-unit address with the ownership/lease/operating agreement, machinery list, rated and demonstrated capacity, licences and recent operating records. Keep capacity unpublished until Operations and Legal sign off.
4. **Payment controls** — Finance must confirm beneficiary name and bank instructions for each transaction. Never publish live bank details in an article/template. Use callback verification through a known phone number before a buyer changes payment instructions.
5. **Legal review** — Indian trade counsel should approve `terms.html`, `privacy.html`, liability wording, governing-law fallback, cookie consent, retention periods and international-transfer wording. The signed Proforma Invoice or Sales Contract must remain controlling.

## Cloudflare and hosting

1. Apply `cloudflare-response-headers.example.txt` as Response Header Transform Rules. Start CSP in Report-Only mode; inspect violations before enforcement.
2. Apply `cloudflare-redirect-rules.example.txt`. Confirm `/products/20325959`, `/products/20325959/` and `/products/` make one `301` hop to `/products.html`.
3. Enable “Always Use HTTPS.” Enable the HSTS preload directive only after every production subdomain is HTTPS-ready for the full max-age.
4. Configure WAF managed rules, bot/rate limiting for forms, account MFA, least-privilege access and origin/registrar MFA. GitHub Pages cannot implement these controls from repository files.
5. Test backups by restoring the site into a disposable environment. Record owner, frequency, retention, encryption and the last successful restore date.

## Search and analytics accounts

1. In Google Search Console, verify the preferred HTTPS property, submit `https://jftagro.com/sitemap.xml`, inspect canonical/indexing reports and request validation after deployment.
2. After the edge redirect is live, inspect the legacy product URL and monitor it until Google selects `/products.html`. Do not use the removal tool as a substitute for a permanent redirect.
3. Connect GA4 only under analytics consent. In DebugView verify: `product_view`, `rfq_start`, `rfq_submit`, `sample_request_start`, `sample_request`, `whatsapp_click`, `quote_calculator_start`, `quote_calculator_complete`, `brochure_download` and `file_download`.
4. Mark genuine lead-completion events as conversions. Exclude internal traffic and test submissions; confirm no name, email, phone, WhatsApp number or free-text requirement enters analytics parameters.
5. Validate Web3Forms delivery, spam controls, rate limits, retention and deletion procedures with test leads. Never paste real buyer or payment data into public issue trackers.

## Final production tests

1. Run Lighthouse/PageSpeed Insights on deployed Home, Products, one product, Contact, Sample Request and Quote Calculator pages on mobile and desktop. Record LCP, INP, CLS, TTFB and the test URL/date; local static checks cannot substitute for origin/CDN measurements.
2. Run WAVE/axe plus manual keyboard, focus, zoom, screen-reader and reduced-motion checks on the same templates.
3. Submit one test RFQ and sample request end-to-end; verify success, duplicate-submit protection, CRM/mail delivery, owner, timestamp and follow-up workflow.
4. Test calculator output against a current supplier quote and forwarder quote. Confirm source, update time, expiry, exclusions and route/container assumptions before calling any feed “live.”
5. Obtain written sign-off from Legal, Compliance, Operations, Finance, Sales and the site owner. A “100%” score is not a safe launch criterion; documented controls and monitored production behavior are.
