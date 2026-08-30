# Phase 37 — External Authority & Backlink Recovery Forensic Audit
**Domain:** https://jftagro.com · **Date:** 2026-08-29 · **Baseline SHA:** 4535656d
**Mode:** Read-only audit + strategy + implementation plan. No outreach, no website change, no deploy, no commit.

---

## 0. Evidence-status preamble (READ FIRST)
- A repository-wide search of all 5,807 files found **no backlink/referring-domain export**. Zero matches for the 10 named domains.
- Phase 36 resolved the backlink profile as **UNKNOWN** (`referring_domains: None → UNKNOWN`).
- The brief's "61 backlinks / 44 referring domains / 2 dofollow / 10 named domains" figures are **USER-PROVIDED / UNVERIFIED**. They are NOT present in the repo and are treated as such throughout.
- Per governing contract §31, **no backlink/credential/price/company claim is fabricated**. Where data is absent, the record is labeled UNKNOWN.

---

## 1. Scope & method
- **In scope:** forensic classification of the 10 named domains (via live, read-only HTTP inspection), authority-concentration review, toxicity posture, recovery strategy, opportunity mapping, prioritization model, and an implementation/roadmap plan.
- **Out of scope (not authorized):** creating backlinks, sending outreach, disavowing, editing the website, deploying, or pushing commits.
- **Evidence classes used:** `PROVEN` (in repo), `OBSERVED` (live HTTP check this session), `INFERRED` (reasoned from observed), `UNKNOWN` (no data).

---

## 2. Data-availability finding
The 44-domain dataset is **not in the repo**. Only 10 domains were named; the other ~34 are **DATA NOT PROVIDED**. See `backlink-data-requirements.md` for the exact export columns needed. The brief's numeric claims (61/44/2-dofollow) remain UNVERIFIED.

---

## 3. Live HTTP probe — 10 named domains (OBSERVED, read-only)
| Domain | HTTP | Mentions jftagro? | Title pattern | Observed type |
|---|---|---|---|---|
| seo-tip.com | 200 | No | (blank) | automated SEO-tool |
| wants.cfd | 200 | No | "seo domain research" | automated SEO-tool |
| takes.sbs | 200 | No | "seo domain research" | automated SEO-tool |
| quero.party | 200 | No | "…Keyword Rankings" | SEO rank/backlink DB |
| urls-shortener.eu | (blank/timeout) | — | — | shortener / SEO |
| bye.fyi | (blank/timeout) | — | — | SEO-tool pattern |
| domains.com.bz | (blank/timeout) | — | — | domain / SEO |
| drjack.world | (blank/timeout) | — | — | SEO-tool pattern |
| backlink.wiki | 200 | No | (blank) | backlink DB / scraper |
| atomizelink.icu | 200 | No | "…Keyword Rankings" | SEO rank/backlink DB |

**Interpretation (OBSERVED + INFERRED):** These homepages exhibit automated SEO / backlink-database / keyword-rank generator patterns. None of the homepages references `jftagro.com`. A live `jftagro` link on each domain is therefore **UNCONFIRMED** (homepage-only check; per-page link-context fetch not performed). They are tentatively classified as **D — automated SEO / backlink-database pages**, pending verification.

---

## 4. Classification summary (see `referring-domain-classification.csv`)
- 10 named domains → class **D (SPAM-LIKE / automated SEO)**, action **INVESTIGATE — no auto-disavow**.
- ~34 unlisted domains → **DATA NOT PROVIDED / UNKNOWN** (not invented).

---

## 5. Authority-concentration (per brief, UNVERIFIED)
- Brief asserts **60 of 61 links target the homepage** → extreme concentration on `/` (root). If true, this is an unnatural footprint: internal pages (products, commodities, certifications, contact, blog) carry ~0 external authority.
- **Action (recommendation):** diversify future link acquisition toward commercial/commodity landing pages and any content assets, not just the root. This is a structural-SEO recommendation, not a website change.

---

## 6. Toxicity & disavow posture
- **No disavow recommendation is made.** The 10 observed domains are automated-SEO pages of unclear individual value, but a live link to jftagro was not confirmed and manual-action risk is not established.
- Recommended posture: **monitor**; if a future export shows a genuine spike of low-quality/parked/PBN links, revisit with evidence. Do not pre-emptively disavow (avoids accidental loss of legitimate links).

---

## 7. Phase 36 carry-over (UNKNOWN / INACCESSIBLE)
- APEDA 404, FIEO timeout, DGFT generic, ExportHub/Kompass 403, LinkedIn company page 404, IndiaMART/TradeIndia/Go4WorldBusiness 404.
- These confirm **no verified authoritative external footprint** as of Phase 36 — consistent with the UNKNOWN backlink baseline.

---

## 8. Forensic conclusion
The only **OBSERVED** backlink-related evidence this session is the automated-SEO nature of the 10 named domains. The broader 44-domain profile is **USER-PROVIDED / UNVERIFIED**. No toxic action is recommended; the priority is (a) obtain a real export and (b) build legitimate authority (see opportunity database & strategies). All metrics are labeled; none are guaranteed.
