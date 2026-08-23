# SEO Implementation Phase 20 — 20 August 2026

## Outcome

This phase addressed opportunity-map ranks 92–96: the Certificate of Analysis review guide, food-container loading checklist, Indian agro-exporter due diligence guide, buyer payment security page and original proof asset programme.

The four buyer guides now form a connected verification path from entity and payment checks through specification, lot-level laboratory evidence, container loading and export documents. The certificates page was converted from a credential-summary presentation into an evidence-status register. No proof asset was fabricated: the repository contains issuer badges and marketing material, but no current original/redacted credential suitable for honest publication.

## Implemented work

### Certificate of Analysis review

- Added a five-record lot-identity reconciliation example covering contract/specification, supplier lot, sample/custody, COA and loading/shipment records.
- Added a clear stop decision for inconsistent lot identifiers and labelled the example as illustrative rather than a real shipment report.
- Updated Article recency and source-review language to 20 August 2026.
- Added a direct export-documentation path.

### Container loading checklist

- Added a direct contextual link from `quality-control.html`; the existing infrastructure-page link was retained.
- Connected the checklist to the export-documentation centre and updated Article recency.
- Added documentation-centre paths to both quality-control and infrastructure learning sections.

### Indian exporter due diligence

- Retargeted title, H1, description, social metadata and Article schema to “Indian agro exporter due diligence checklist” intent.
- Removed unsupported numerical claims and absolute registration statements.
- Corrected product-scope distinctions for APEDA, Spices Board, FSSAI, GST and MCA checks.
- Added official DGFT, GST, MCA, FSSAI and APEDA verification routes.
- Replaced universal payment, inspection, laboratory, sample-timing and first-order prescriptions with transaction-specific controls.
- Added cross-document legal-entity, signatory and beneficiary reconciliation, plus LC, proforma invoice, buyer security, COA, loading and documentation paths.
- Removed the unsupported “APEDA certified” CTA statement.

### Buyer payment security

- Retargeted title and H1 to Indian exporter payment safety, LC, TT and verification intent.
- Added an LC-versus-TT control table without claiming that either route is universally safer.
- Connected due diligence, proforma invoice, LC, proof verification and export-documentation guides.
- Added schema recency and strengthened beneficiary/legal-entity matching.

### Proof asset programme

- Replaced credential-claim ItemList schema with neutral WebPage schema describing the verification process.
- Added a dated public proof register stating that current original/redacted credentials are not published.
- Labelled issuer logos as navigation labels rather than proof and the company overview as marketing background.
- Changed credential-card status from “Copy on Request” to “Verification Data Not Published.”
- Added official registry paths and a ten-point future redacted-asset publication gate.
- Changed shipment-document and organic/Halal language to conditional, product/destination/scope-dependent wording.
- Recorded the repository evidence inventory and owner action in `reports/seo-proof-asset-publication-register-2026-08-20.md`.

## Primary sources

- DGFT IEC portal and official IEC guidance: <https://www.dgft.gov.in/CP/>
- GST Search Taxpayer guidance and service: <https://services.gst.gov.in/services/quicklinks/searchtxp>
- MCA company/LLP master data: <https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html>
- APEDA exporter status: <https://apeda.gov.in/exporter-status>
- APEDA exporter-directory disclaimer: <https://agriexchange.apeda.gov.in/Home/ExporterLogin>
- FSSAI public licence verification: <https://www.fssai.gov.in/citizen/about-license-verification>
- ISO/IEC 17025 overview: <https://www.iso.org/standard/66912.html>
- Codex methods and sampling reference CXS 234-1999: <https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B234-1999%252FCXS_234e.pdf>

## Validation

- FAQ/schema and cluster-link validator: 926 FAQPage blocks and 81 priority cluster pages passed.
- All seven expanded trust/quality cluster pages contain their required contextual links and documentation-centre paths.
- Target pages passed title/H1 presence and JSON-LD parsing checks.
- Unsafe legacy due-diligence phrases were absent after the rewrite.
- Focused `git diff --check` passed after whitespace cleanup.
- Sitemap count remains 1,430 URLs because this phase improved existing indexable pages and added reports only.
- Temporary transformation scripts were removed.

## Scope boundary

The implementation does not assert that any registration, recognition, certification, laboratory report or shipment document is current unless a buyer verifies the original holder, number, scope and validity. It does not promise that a destination document is applicable or issuable, and it does not prescribe a universally safe payment method.

## Deployment status

Local implementation only. No production deployment or indexing request was made.
