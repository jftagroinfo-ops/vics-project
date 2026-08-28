# Phase 32 — E-E-A-T Evidence Map

Date: 2026-08-28
Status: Audit-only. Distinguishes claims from evidence throughout; no fabricated experience, expertise, or authority is proposed anywhere in this document.

## Experience

| Claim | Evidence type | Verifiable-in-kind? |
|---|---|---|
| 250 MT/Day milling capacity, Balap, Raigad facility | Specific, named, consistently-repeated figure across `index.html` and independently reflected in AI search summaries | Yes — concrete and specific, not a vague claim |
| Real per-product specification data (moisture, purity, HS code, MOQ, packaging) across all 84 products | Structured data (`data/products.json`) driving every product page and FAQ | Yes — internally consistent, previously governed and validated (Phase 7) |
| Functional buyer tools (packing calculator, port-transit calculator, shipment tracker) | Live, working tools, independently re-verified across Phases 5-8 and 27-31 | Yes — functional evidence, not a static claim |
| "Established 2016," explicit predecessor-business disclaimer | Consistent prose + meta description across `about.html` and other pages | Yes — and notably, an honesty signal: most companies do not proactively caveat their own history this way |

**Conclusion: genuinely evidenced, not merely claimed.** No fabrication is needed or recommended here.

## Expertise

| Claim | Evidence type | Verifiable-in-kind? |
|---|---|---|
| Export documentation guidance (`export-documentation.html`) | Detailed, structurally correct content covering real shipping-document categories | Yes |
| Buyer-verification guidance (`buyer-security.html`) | Same | Yes |
| 37 process-education articles (APEDA registration, bill of lading, certificate of analysis, HS codes, market outlooks) | Real, specific process content, not generic filler (spot-checked this phase and in Phases 29-30) | Yes |
| Product FAQ content | Derived from governed per-product specification data (Phase 7 governance) | Yes |

**Conclusion: genuinely evidenced.** The one open item — dual article templates (Phase 29-30) — is a presentation inconsistency, not an expertise or content-quality gap.

## Authoritativeness

| Claim/signal | Independent evidence found this phase | Strength |
|---|---|---|
| LEI registration (`3358008COTZVRF8ZQE38`) | Confirmed present and ACTIVE via `globallei.in`, an independent, verifiable registry — unchanged since Phase 26 | **STRONG** |
| APEDA/Spices Board/AEO/RCMC certifications | Claims are accurate against website source; independent third-party confirmation via APEDA's own public PDF list was inconclusive (name not found in the visible excerpt; full PDF not parsed) | MEDIUM (unresolved, not disproven) |
| FIEO membership | No evidence found either way | **UNKNOWN** |
| LinkedIn company page | Not found | **ABSENT** |
| B2B marketplace presence (Indiamart/TradeIndia/ExportersIndia) | Not found | **ABSENT** |
| Trade press / industry association mentions | None found | **ABSENT** |

**Conclusion: this is the genuinely weak pillar**, and correctly so — it is the one E-E-A-T dimension that cannot be improved by writing better content or fixing code; it requires real external actions taken by the business.

## Trustworthiness

| Signal | Status |
|---|---|
| Consistent NAP (name/address/phone) across Organization/LocalBusiness schema and visible pages | Consistent (postal-code question aside, carried unresolved from Phase 26) |
| Certificate-verification-gate design (`certificates.html`) | Deliberate, previously assessed as sound (Phase 26) — not a defect |
| RFQ/sample-request flow | Functional, previously verified |
| Security posture (HTTPS, security headers) | Verified clean through Phase 31 |
| External consistency with AI-generated summaries | **Compromised by an external actor, not the website** — see main audit §9. A buyer cross-checking JFT's own "Est. 2016" disclaimer against an AI's confident "since 1980" claim encounters a contradiction the website did not create |

**Conclusion: internally strong; the one trust risk identified this phase originates entirely outside the website's control.**

## Summary Table

| Pillar | Assessment | Primary lever for improvement |
|---|---|---|
| Experience | Strong | None needed |
| Expertise | Strong | None needed |
| Authoritativeness | Weak-Medium | External authority building (business-led) |
| Trustworthiness | Strong internally / externally undermined | Not directly fixable; monitor only |

## Stop

No fabricated case studies, author identities, reviews, or claims were created, proposed, or implied anywhere in this document.
