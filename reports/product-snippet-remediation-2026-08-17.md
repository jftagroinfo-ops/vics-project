# Product Snippet Structured Data Remediation

**Date:** 17 August 2026  
**Search Console issue:** Either `offers`, `review` or `aggregateRating` should be specified

## Decision

JFT Agro uses contract/RFQ pricing and does not publish verified customer
ratings on the affected pages. Google requires a Product snippet to contain at
least one truthful `offers`, `review` or `aggregateRating` property, and an
Offer requires a numeric price.

No price, zero-price offer, rating or review was fabricated. Quote-only
`Product` rich-result nodes were replaced with `WebPage` schema that retains:

- canonical URL and page identity;
- product name, description and image;
- language;
- JFT Agro website and publisher identity;
- the product as the page topic.

Breadcrumb and FAQ structured data remain unchanged.

## Scope

- 84 English product pages
- 840 localized product pages across 10 locale folders
- 924 product detail pages in total
- the dynamic product catalogue `ItemList`
- the catalogue remediation generator
- the commercial-content audit

## Validation

- 924/924 product pages contain valid JSON-LD.
- 924/924 contain one root `WebPage` schema.
- Zero root `Product` nodes remain in the prepared product pages.
- The 84-page English commercial-content audit reports zero findings.
- The four Search Console examples are corrected in both source and prepared
  Cloudflare deployment assets.

## Deployment status

Deployed to Cloudflare Worker `jftagro-site` and both custom domains on
17 August 2026.

- **Cloudflare version:** `ca60df25-4978-4f4f-b1cd-657f99bb52c8`
- **Assets published:** 925 new or modified; 2,087 total in the bundle
- **Live verification:** all four Search Console example URLs return HTTP 200
- **Live schema:** `WebPage`, `BreadcrumbList` and `FAQPage`
- **Live Product nodes:** zero on all four example URLs

The production correction is ready for **Validate fix** in Google Search
Console's Product snippets report.
