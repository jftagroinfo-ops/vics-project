# Production Operations

## Automated Checks

`site_quality.yml` validates all renderable pages, product-page commercial content, blog navigation, deterministic generators, and static performance budgets on every pull request and push to `main`.

`uptime.yml` probes the homepage, catalog, inquiry form, blog, and quote calculator every 15 minutes. Configure repository notification rules so failed workflow runs alert the operations owner.

## Lead Delivery

RFQs, sample requests, and newsletter subscriptions are submitted through Web3Forms and include a generated lead ID, landing page, referrer, and available UTM fields. WhatsApp remains the sample-request fallback.

Confirm the Web3Forms access key routes to the monitored trade-desk mailbox. Rotate the key in `jft-conversion.js` and `contact.html` together if ownership changes.

## Analytics and Search

Google Analytics measurement ID `G-MWZ2ZWZP4G` loads only after explicit analytics consent. Conversion events include `form_start`, `generate_lead`, `contact_whatsapp`, and `conversion_link_click`.

Google Search Console still requires the property owner's verification token. After verification, submit `https://jftagro.com/sitemap.xml` and monitor indexing, Core Web Vitals, manual actions, and structured-data reports.

## Localization

Arabic, Spanish, French, and Russian homepages are indexable localized pages. Other localized URLs remain `noindex,follow` English fallbacks. Before expanding indexation, record native-language commercial and legal review in `localization-review.json` and rerun:

```bash
python scripts/generate_hreflang.py
python scripts/generate_sitemap.py
```

## Incident Checks

For lead incidents, test an RFQ with a controlled address and confirm the received lead ID. For availability incidents, inspect the Production Uptime workflow, DNS/TLS status, the hosting provider, and the most recent deployment. Security reports are directed through `/.well-known/security.txt`.
