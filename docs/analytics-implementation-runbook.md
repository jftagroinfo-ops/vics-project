# Analytics and Search Measurement Runbook

This site sends analytics only after the visitor accepts analytics cookies. Do not diagnose total traffic without accounting for consented measurement and automated traffic.

## Implemented website events

| Event | Purpose | GA4 key event? |
| --- | --- | --- |
| `generate_lead` | A lead form was accepted by the form endpoint | Yes: primary business conversion |
| `contact_whatsapp` | Visitor opened a WhatsApp contact link | Optional: use as a secondary conversion |
| `contact_phone` | Visitor opened a phone link | Optional: use as a secondary conversion |
| `contact_email` | Visitor opened an email link | Optional: use as a secondary conversion |
| `form_start` | Visitor first interacted with a form | No |
| `quote_calculator_start` | Visitor first interacted with the quote calculator | No |
| `quote_calculator_complete` | Calculator rendered a selected planning scenario | No |
| `quote_to_rfq_click` | Visitor moved from a result to the RFQ | No; use as a funnel step |
| `quote_to_whatsapp_click` | Visitor moved from a result to WhatsApp | No; `contact_whatsapp` is the conversion candidate |
| `rfq_prefill_loaded` | RFQ opened with calculator context | No |
| `article_view` | A blog article was viewed | No |
| `article_read_depth` | A reader reached 50% or 90% | No |
| `article_to_product` | Article reader opened the related product | No |
| `article_to_calculator` | Article reader opened the calculator | No |
| `article_to_rfq` | Article reader opened the RFQ | No |
| `page_not_found` | A missing path loaded the custom 404 page | No; diagnostic |

Never mark calculator completions or page views as conversions. The primary conversion is a successfully accepted lead, not a button click.

## GA4 configuration

1. Open **Admin > Data display > Events** after the events have appeared and mark `generate_lead` as a key event.
2. Decide whether WhatsApp, phone, and email opens meet the sales team's definition of a lead. If they do, mark them as secondary key events and report them separately from submitted forms.
3. Create event-scoped custom dimensions for `lead_type`, `lead_source`, `form_id`, `content_group`, `article_topic`, `requested_path`, `referrer_host`, `product_category`, `destination`, `incoterm`, and `container_size`.
4. Use DebugView after accepting cookies to verify each funnel once on desktop and mobile. Do not submit real personal information in DebugView tests.
5. In **Admin > Data streams > Configure tag settings**, list staging, preview, and payment domains only if cross-domain measurement is genuinely required.

## Funnel explorations

Create these GA4 explorations:

1. Quote funnel: `quote_calculator_start` -> `quote_calculator_complete` -> `quote_to_rfq_click` -> `generate_lead`.
2. Content funnel: `article_view` -> `article_read_depth` at 50% -> any `article_to_*` event -> `generate_lead`.
3. RFQ funnel: `form_start` on `rfqForm` -> `generate_lead`, broken down by `lead_source` and `product_category`.

Use a 30-day and 90-day view. Compare Organic Search, AI Assistant referrals, and tagged campaigns; do not combine them with unqualified Direct traffic.

## Suspicious and internal traffic

The May-August 2026 export showed a large Singapore/China Direct segment with almost no engagement. Treat that as suspicious until verified, not automatically as customer demand.

1. Create a comparison named `Likely qualified traffic` excluding country in Singapore/China **only when** session default channel group is Direct and engagement is near zero. Keep the raw view available.
2. Define office, agency, uptime-monitor, and developer IPs under **Data streams > Configure tag settings > Define internal traffic**. Test the data filter before activating it.
3. Compare hostname, browser, device, landing page, engagement time, and event count. A country alone is never sufficient proof of bot traffic.
4. If Cloudflare is enabled, use Bot Analytics and managed bot controls at the edge. Do not block target markets solely because a GA4 report looks unusual.

## 404 repair workflow

The custom 404 now emits `page_not_found` with `requested_path`, `referrer_host`, and a path-only referrer. Review it monthly:

1. Build an Exploration table with `requested_path`, `referrer_host`, and event count.
2. Test the highest-volume paths manually.
3. For an old valid URL, add one permanent redirect to the closest equivalent page.
4. For a broken internal link, fix the source link rather than relying on a redirect.
5. Leave junk probes and nonexistent URLs as true 404 responses. Do not redirect every unknown URL to the home page.

## Search Console

1. Verify the Domain property for `jftagro.com` using DNS.
2. Submit `https://jftagro.com/sitemap.xml` and confirm that it is fetched successfully.
3. Link Search Console in **GA4 Admin > Product links > Search Console links**.
4. Review indexing, page experience, HTTPS, manual actions, and security issues weekly until stable, then monthly.
5. Use the Search Console landing-page and query reports to expand articles that already earn impressions. Prioritize the cumin outlook, rice-origin comparison, psyllium guide, white-rice policy, and regional trade pages identified in the May-August 2026 GA4 export.

## Campaign attribution

All campaign links should use consistent lowercase UTMs. Recommended naming:

```text
utm_source=linkedin
utm_medium=organic_social
utm_campaign=basmati_buyer_guide_2026
utm_content=carousel_cta
```

The site retains UTM fields plus Google, Microsoft, Meta, TikTok, and LinkedIn click IDs in the current browser session and includes them with lead submissions. Never place names, emails, phone numbers, or other personal data in UTM values.

## Lead-quality feedback

Client-side analytics cannot know whether a lead became qualified or revenue-generating. Add a CRM or controlled lead sheet keyed by the generated `lead_id`, and record:

- `lead_received`
- `sales_accepted`
- `qualified_requirement`
- `sample_or_quote_issued`
- `contract_won`
- `contract_lost` with a controlled reason

Import qualified and won outcomes into the advertising/analytics platform only through an approved server-side or offline-conversion process. Never expose API secrets in website JavaScript.

## Monthly scorecard

Report these separately by channel and destination market:

- Submitted leads and qualified leads
- Lead qualification rate
- Calculator-to-RFQ rate
- RFQ form completion rate
- Article-to-commercial-page rate
- Organic clicks and non-brand query growth
- Top missing URLs and fixed-link status
- Landing-page engagement for qualified traffic

Raw users and sessions are context metrics, not the primary success measure.
