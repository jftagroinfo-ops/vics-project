# Phase 13 — Buyer Psychology, Conversion Architecture & Competitive Commercial Audit

Date: 2026-08-28
Status: Investigation complete. One evidence-backed fix implemented (documented at the end); everything else in this report reflects direct source inspection, not speculation.

## 1. Executive Summary

Phases 10-12 already closed most of the structural and visual gaps a commercial-psychology audit would normally surface: the RFQ form already prefills product context, WhatsApp messages already carry page context, trust content already precedes every CTA, and the visual presentation of the catalogue was fixed in Phase 12. This phase's job was narrower and deeper: does the site ask the right question at the right moment, and does the RFQ form itself ask for the right things at the right time? One concrete, externally-validated friction point was found and fixed: the RFQ form requires 10 fields before it can be submitted, including two (Port of Discharge, Target Shipment Month) that a genuine first-time enquiry frequently cannot supply yet. Everything else audited — trust architecture, sample-request differentiation, WhatsApp tone, calculator-to-RFQ bridges, regional-page relevance, article buyer-path — was found already sound, and is documented as such rather than altered without cause.

## 2. Current Commercial Maturity Score (before this phase's fix)

7.7 / 10. The site clearly answers who/what/where/why-trust for a serious buyer; the one material drag is RFQ form friction (see §9).

## 3. Buyer Personas

Modeled directly against what the site currently exposes, not assumed:

- **Persona A (established importer)** — served well: spec tables, HS codes, MOQ, compliance, export-documentation centre, and buyer-security.html's due-diligence checklist all exist and are reachable from a product page in 1-2 clicks.
- **Persona B (trader/distributor)** — served well: category pages surface the full breadth of a commodity group quickly; product cards show HS code + MOQ without needing to open each page.
- **Persona C (food manufacturer/industrial buyer)** — partially served: spec tables exist, but COA/lab-data detail lives on `export-documentation.html` rather than the product page itself (a reasonable information-architecture choice, not a defect, since COA is shipment-specific and not a static per-product fact JFT can publish).
- **Persona D (new importer, cautious)** — this persona is the one most exposed to the RFQ form friction below: `buyer-security.html`'s due-diligence sequence is strong, but a cautious first-time buyer who reaches the RFQ form is then asked for a port and shipment month they may not have decided yet.
- **Persona E (existing buyer)** — served: `shipment-tracker.html` exists, is linked from the footer/tools area, and does not request more information than a reference number.

## 4. Buyer Journey Map (representative paths)

| Path | Entry → Information → Trust → Evaluation → CTA → Form → Submission → Follow-up |
|---|---|
| Homepage → Product → RFQ | Hero states scope/trust tag → category browse → cert strip on product page → spec table → 3-tier CTA → RFQ form (now less friction, see fix) → success panel w/ reference ID → "reviewed Mon-Sat" stated |
| Article → Product → RFQ | `jft-conversion.js`'s buyer-path panel (View Product / Estimate / Request Quote) → product page → same as above | 
| Category → Product → RFQ | Category intro + selection criteria → product card grid (Phase 12-fixed images) → product page → same as above |
| Regional → Product → RFQ | Region-specific hero (Phase 12-fixed CTA) → port/compliance content → product cards → same as above |
| Product → Sample | Clear "Need a trade sample instead?" link next to the RFQ quantity field → sample-request.html's own hero ("Evaluate the product. Confirm the specification.") differentiates intent clearly → 4-step process shown → success panel |
| Product → WhatsApp | Tertiary CTA, page/product context auto-appended to message text (Phase 6/11 work) → opens WhatsApp with pre-filled, professional-sounding message |
| Calculator → RFQ | Every calculator (`quote-calculator.html`, `packing-calculator.html`, `port-transit-calculator.html`) ends in a CTA block with an honest "reference only, not a commitment" disclaimer, then "Request Formal Quote" |
| Tracker → Contact | `shipment-tracker.html` ends in a WhatsApp + "Send Reference Securely" CTA pair |

No path was found with a dead end or a missing next step.

## 5. Conversion Funnel Audit

| Stage | Buyer's question | Answered? | Where |
|---|---|---|---|
| Discovery | "What does JFT sell, and are they real?" | Yes | Homepage hero, trust tag |
| Qualification | "Do they handle my commodity/quantity?" | Yes | Category pages, product spec tables |
| Product evaluation | "Does this match my spec?" | Yes | Product spec table, packaging, MOQ |
| Trust verification | "Can I verify them before paying?" | Yes | `buyer-security.html`, `certificates.html`, `quality-control.html` |
| Commercial enquiry | "How do I ask for a price?" | Yes | 3-tier CTA, consistent site-wide |
| RFQ submission | "What do they need from me to respond?" | Partially — see §9 | `contact.html` |
| Human follow-up | "What happens next, and how fast?" | Yes | Success panel + reference ID + "reviewed Mon-Sat" + "1 Day - Typical Review" stat |

## 6. Trust / Commercial-Anxiety Audit

| Risk category | Addressed? | Evidence |
|---|---|---|
| Quality risk | Yes | `quality-control.html`, spec tables, inspection-on-request language |
| Payment risk | Yes | `buyer-security.html`'s LC/TT comparison table and beneficiary-verification warning |
| Supplier risk | Yes | Star Export House / ISO 9001:2015 / APEDA / FSSAI documentation-available language (Phase 9 confirmed no exaggerated claims) |
| Documentation risk | Yes | `export-documentation.html`'s full document matrix |
| Logistics risk | Yes | Regional pages' port/corridor detail, logistics pages |
| Communication risk | Yes | Multiple channels (form, WhatsApp, phone, email) all consistently presented |
| Specification risk | Yes | Per-product spec tables; explicit "signed specification and approved sample control the actual order" language throughout (governed, not a new claim) |
| Delivery risk | Partially | Calculators are explicit that outputs are "reference only," which is honest but leaves a first-time buyer without any general sense of typical lead time until they enquire — not fixed, since inventing a lead-time figure would violate the no-fabrication rule, and the existing "confirmed in the commercial offer" framing is the correct, honest answer given no governed lead-time data exists |

No commercial-anxiety category was found unaddressed in a way that could be fixed without inventing information.

## 7. RFQ Friction Audit (the phase's central finding)

**Evidence**: `contact.html`'s RFQ form requires 10 fields to submit: full name, company, email, phone, product, quantity, destination country, **port of discharge**, required packing, incoterm (has a default), **target shipment month**. External research on B2B RFQ form best practice is explicit and consistent: *"If you can write a preliminary quote based on name, email, product, and quantity — those four are required. Everything else is optional... A buyer who sees 15 required fields is more likely to close the tab and call a competitor than fill out your form."* ([ChatSKU](https://chatsku.com/rfq-form-best-practices/))

Of JFT's 10 required fields, two are genuinely likely to be unknown at first contact for a real buyer, not just theoretically optional:
- **Port of Discharge** — many buyers do not finalize the discharge port until their own freight forwarder is engaged, which often happens after (not before) a supplier is shortlisted.
- **Target Shipment Month** — a scheduling detail normally negotiated after commercial terms are agreed, not needed to request a price indication.

Country, packing, and product remain required because they are genuinely price-determining for a bulk agro-commodity quote (different destinations, pack formats, and grades carry materially different FOB/CIF economics) — relaxing those would mean JFT literally cannot return a meaningful quote, which the external research also implies ("preliminary quote based on... product and quantity" assumes the responder already knows what and how much).

**Fix implemented**: made Port of Discharge and Target Shipment Month optional (not required) on `contact.html` and all 10 locale copies (port only — shipment month does not exist as a field on the locale copies, a pre-existing, separate form-structure gap between English and locale versions, documented in §22 as not fixed this phase). See §"Implementation" below for full detail.

## 8. Sample-Request Funnel

Already clearly differentiated from the RFQ path: `sample-request.html`'s hero ("Evaluate the product. Confirm the specification.") and its own distinct 4-step "what happens after you submit" sequence make the sample path feel like a genuinely different, lower-commitment step from "Request Your Export Quote." `contact.html` also cross-links to it directly next to the quantity field ("Need a trade sample instead?"). No changes made — already sound.

## 9. WhatsApp Commercial Flow

Unchanged and confirmed still working: messages carry page/product context (Phase 6/11), the CTA is consistently tertiary (never visually dominant), and wording ("WhatsApp Inquiry," "Chat on WhatsApp Now") reads as a legitimate B2B channel rather than an escape hatch, consistent with external research confirming WhatsApp is a normal, expected channel alongside forms for agricultural B2B trade.

## 10. Calculator → RFQ Bridges

All three calculators already end in a contextually appropriate CTA block with an honest "reference only, not a commitment" disclaimer (confirmed unchanged from Phase 11). No gap found.

## 11. Regional-Page Commercial Intent

Africa/Asia/Europe/UAE pages are not generic SEO landing pages: each has region-specific port/corridor detail, region-specific CTA copy (fixed to be visible again in Phase 12), and (for Africa/UAE/Europe) real product cards tied to that region's actual documented markets. No gap found.

## 12. Article Commercial-Intent Analysis

`jft-conversion.js`'s `addArticleBuyerPath()` adds a "Buyer next step" panel (View Product / Build Reference Estimate / Request Export Quote) to every blog article uniformly. Reviewed against Phase 13's instruction to only add a commercial CTA "when it logically matches the article's buyer intent": the three actions offered (view the closest-matching product, build a non-binding cost estimate, or request a quote) are generically appropriate for *any* buyer-education article regardless of specific topic — none of the three actions presumes a stage of readiness the reader hasn't reached, and the "View [Product]" link degrades gracefully to `products.html` when no specific product keyword matches. No change made — the existing blanket approach is not a mismatch.

## 13. Mobile Conversion

No layout was touched this phase (the only change is two HTML attributes plus one small CSS rule). Reviewed against the existing breakpoints validated in Phases 10-12; removing `required` cannot introduce overflow, stacking, or touch-target regressions, since it does not change any element's size or position.

## 14. International Conversion

`contact.html`'s port-field fix was applied identically (structure-only, no new translated text) to all 10 locale copies. Arabic RTL: the `<span class="opt">` marker inherits the same RTL-safe inline-flow behavior as the existing `<span class="req">` marker it replaces — no new RTL risk introduced.

## 15. Competitive Benchmark

Three targeted searches were run (full queries and sources retained in this session's record):

| Pattern | Why it works | Does JFT have it? | Relevant? | Implement? |
|---|---|---|---|---|
| RFQ forms should require only name/email/product/quantity; everything else optional | Reduces abandonment; a buyer who sees many required fields disengages | Partially — most fields were required | Yes | **Yes — implemented this phase** (§7) |
| Spice/commodity exporters display ISO/HACCP/FSSAI/Spices Board + COA/lab documentation | Establishes verifiable, industry-standard trust | Yes — confirmed present (FSSAI, APEDA, ISO 9001:2015, Star Export House, COA described on export-documentation.html) | Yes | No change needed — already present |
| WhatsApp used alongside (not instead of) a contact form for agro B2B trade | Matches buyer expectation for fast, informal follow-up without abandoning a structured lead-capture form | Yes — both already coexist | Yes | No change needed |

No pattern found that JFT is missing and that would be safe/evidence-backed to add.

## 16. Differentiation Analysis

Genuine, already-supported differentiators that are appropriately surfaced (not buried): commodity breadth (10 categories, 84 products), documentation depth (`export-documentation.html`'s full stage-by-stage matrix — unusually thorough compared to the competitive benchmark, which found most exporters only list certificate names), and multilingual support (11 languages, more than typical for a company this size). No new surfacing work was found necessary — these already have dedicated, linked pages and are referenced from product pages.

## 17. Findings Summary

| ID | Severity | Finding | Action |
|---|---|---|---|
| P13-F1 | P1 | RFQ form requires Port of Discharge and Target Shipment Month, which a first-time buyer often cannot supply | **Fixed** — made optional, site-wide across 11 language copies |
| P13-F2 | documented, not a defect | Locale `contact.html` copies lack a `shipment_month` field entirely (pre-existing structural drift from English) | Documented only — a locale form-parity project is a separate, larger undertaking outside this phase's narrow RFQ-friction scope |
| — | — | All other audited areas (trust, WhatsApp, sample funnel, calculators, regional pages, articles) | No defect found; no change made |

## 18. Rejected/Not-Implemented Ideas

- **Making `packing` optional too** (the external benchmark's stricter "only 4 fields required" standard) — rejected: packing format materially changes FOB/CIF unit economics for a bulk commodity, so JFT genuinely cannot return a meaningful first quote without it, unlike port/shipment-month which are refined later in negotiation.
- **Building locale form-field parity** (adding `quantity`/`incoterm`/`shipment_month` to the 10 locale copies) — documented as a real, separate gap (P13-F2) but not implemented: this is a larger, distinct localization-architecture project, not a narrow psychology/friction fix, and mixing it into this phase would violate the "no while-I'm-here cleanup" rule.
- **A/B testing the required-field change** — explicitly out of scope per the phase's own rule; the change is instead grounded in external published best-practice evidence plus the direct, verifiable fact that port/timing are pre-quote unknowns for many buyers.
- **Adding invented response-time guarantees** — rejected; the existing "1 Day - Typical Review" and "reviewed Mon-Sat" language is already the honest, correct answer and was not touched.

## 19. Expected Impact

Fewer complete-but-abandoned RFQ attempts from qualified buyers who have a real product/quantity/destination need but don't yet have a firm port or ship-month — without losing any information from buyers who do have it (the fields remain visible and functional, just not blocking).

## 20. Risk Assessment

Very low. The change removes a browser-native validation constraint (`required`) and a visual marker; it does not remove the fields, does not change what data is collected from buyers who fill them in, does not touch the submission handler, and does not touch any translated copy. The main risk considered — JFT's sales team receiving RFQs with no port/timing information — is judged acceptable because that information is now explicitly framed as "(optional)" rather than silently missing, and remains directly requestable in the team's first follow-up reply.

**Implementation, verification, and full regression results are in `reports/phase13-commercial-psychology-final-2026-08-28.md`.**
