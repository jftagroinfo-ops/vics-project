# Logistics navigation and hero contrast production fix

Date: 2026-08-22  
Production version: `f9579380-4a97-4895-9f9c-424cb68a487b`

## Reported symptoms

- Shared header and footer links on nested logistics URLs resolved inside `/logistics/.../`, producing invalid destinations such as `/logistics/mundra-rice-exports/certificates.html`.
- Logistics hero headings inherited a global dark heading colour and had insufficient contrast against the dark green hero background.

## Corrections

- Rebased relative links in dynamically injected header and footer components to root-relative paths on both logistics pages.
- Changed the component fetch paths to root-relative `/header.html` and `/footer.html` paths.
- Set `.hero h1` explicitly to white on both logistics pages.
- Changed dynamically generated language-menu paths to root-absolute paths and limited the menu to languages declared by each page's `hreflang` links.
- Added a nested-component regression validator and excluded generated deployment directories from the source link crawler.

## Production validation

- Wrangler dry run: passed.
- Uploaded assets: 3 (`header.html` and both logistics `index.html` files).
- Both production logistics URLs: HTTP 200.
- Both rendered H1 elements: visible with computed colour `rgb(255, 255, 255)`.
- Rendered Certificates link on both pages: `/certificates.html`.
- Remaining relative header/footer links: 0.
- Unique rendered internal header/footer destinations checked: 39.
- Destinations returning HTTP 4xx/5xx: 0.
- Full source crawl: 1,745 HTML files and 0 unique broken internal links.
- Language links on each English-only logistics page: one correct self-referencing English path.

## Affected production URLs

- `https://jftagro.com/logistics/mundra-rice-exports/`
- `https://jftagro.com/logistics/nhava-sheva-agro-exports/`
