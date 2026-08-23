# SEO Release Runbook

## Before deployment

Run the local gate:

```powershell
python scripts/seo_release_gate.py
```

Review:

- `reports/seo-release-gate.md`
- `reports/seo-release-manifest/seo-release-manifest.md`
- `reports/seo-release-manifest/changed-html-manifest.csv`
- `reports/seo-release-manifest/post-deploy-crawl-urls.txt`

Do not mechanically shorten localized metadata warnings. Resolve them only through the native-review register.

## Deployment boundary

Deployment requires the site owner's authorization and the hosting release procedure. The local SEO gate does not deploy, submit a sitemap or notify IndexNow.

## Immediately after deployment

1. Fetch `robots.txt` and `sitemap.xml` from production.
2. Confirm production sitemap count and compare local-versus-production URLs.
3. Crawl the changed-URL list and require direct HTTP 200 for indexable pages.
4. Verify one rendered page from each affected template for title, H1, canonical, hreflang, JSON-LD, images and navigation.
5. Confirm new URLs are linked from indexable pages and not blocked by robots/noindex.
6. Test true 404 behavior on a nonexistent URL.
7. Test the RFQ/contact/sample routes without sending real personal data through diagnostics.

## Indexing notification

Only after the live checks pass:

1. Resubmit the sitemap in Google Search Console and Bing Webmaster Tools when appropriate.
2. Use URL inspection for the four new high-value URLs; avoid mass manual requests.
3. If IndexNow is authorized, submit the verified changed URLs in batches of no more than 10,000.
4. Record submission time and response; notification does not guarantee crawling or indexing.

Validate the payload without submitting:

```powershell
python scripts/submit_indexnow.py --url-file reports/seo-release-manifest/post-deploy-crawl-urls.txt --dry-run
```

After live verification and explicit submission authorization, remove `--dry-run`.

## First monitoring windows

- 24–48 hours: status codes, canonical selection, server errors and form delivery.
- 7 days: sitemap discovery/indexing differences and query anomalies.
- 28 days: non-brand impressions, CTR, average position and qualified enquiries by landing page.
- 90 days: retain, improve, consolidate or retire hypotheses using comparable periods.
