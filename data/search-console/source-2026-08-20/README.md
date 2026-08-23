# Google Search Console export provenance

- Property: `jftagro.com`
- Search type: Web
- Reporting period: 19 May 2026 through 18 August 2026
- Export supplied by the site owner on 20 August 2026
- Source tables: Chart, Queries, Pages, Countries, Devices, Search appearance and Filters
- Obvious PII scan before archival: zero email addresses and zero long phone-like strings detected in `Queries.csv`

Google exported each dimension as a separate table. Do not join a query to a page, country or device from these files. Use a Search Analytics API export with the required dimensions for cross-dimensional attribution.
