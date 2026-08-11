# Quote market-rate feed

`quote-market-rates.json` is the single rate source used by `quote-calculator.html`.
The browser requests it with caching disabled and refreshes it every 15 minutes.

The checked-in values are reference benchmarks, not live quotations. For automatic
commercial updates, configure these GitHub Actions secrets:

- `QUOTE_RATE_FEED_URL`: HTTPS endpoint returning the validated feed schema.
- `QUOTE_RATE_FEED_TOKEN`: optional bearer token for that endpoint.

The existing global sync workflow checks the endpoint every 12 hours. The refresh
script rejects incomplete, malformed, future-dated or invalid date-order data and keeps
the last valid feed when a provider call fails.

Product inputs should come from a verified export pricing source. Domestic mandi
prices must not be copied directly into `fob` because processing, quality, packing,
testing, inland transport and export costs are different. Freight inputs should be
current FCL lane indications for the named load and should include a clear validity
period and source label.
