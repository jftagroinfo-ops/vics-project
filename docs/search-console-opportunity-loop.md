# Search Console Opportunity Loop

## Inputs

Export Google Search Console performance with at least `Query`, `Page`, `Clicks`, `Impressions` and `Position`. Include `Country` and `Device` in separate exports when diagnosing market or mobile differences. Replace the header-only template at `data/search-console/gsc-query-page-export.csv`.

Aggregate consented first-party lead outcomes by landing page into `data/search-console/page-lead-outcomes.csv`. Do not place personal data in this file.

## Run

```powershell
python scripts/build_search_console_opportunity_loop.py
```

Outputs:

- `reports/search-console-opportunity-loop/search-console-page-opportunities.csv`
- `reports/search-console-opportunity-loop/search-console-query-opportunities.csv`
- `reports/search-console-opportunity-loop/search-console-opportunity-loop.md`

## Monthly operating cycle

1. Export the same complete date range and compare it with the preceding equivalent period.
2. Keep branded queries excluded from discovery prioritization, but monitor them separately for reputation/navigation issues.
3. Review high-impression pages in positions 4–20 for intent and snippet gaps.
4. Review positions 21–40 for content depth, source quality and internal-link support.
5. Join page-level enquiries, qualified requirements and wins; never optimize solely for clicks.
6. Confirm country, language and device before expanding localized content.
7. Record the implemented change, hypothesis and review date in the SEO change log.
8. Recheck after enough impressions accrue; reduce priority when the hypothesis repeatedly fails.

## Guardrails

- `no_gsc_data` means evidence is unavailable, not that demand is zero.
- CTR benchmarks in the script are triage assumptions, not universal targets.
- Do not merge partial and complete periods without labelling them.
- Do not expose query exports containing personal or sensitive data.
- Search Console reports clicks and impressions, not qualified enquiries or revenue.
