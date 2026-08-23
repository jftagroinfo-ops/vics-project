# SEO Implementation Phase 11 — 20 August 2026

## Outcome

This phase addressed opportunity-map ranks 47–51: fennel seeds, fenugreek seeds, green cardamom, black pepper powder and dry ginger powder.

## Implemented work

### Fennel seeds

- Corrected the visible spelling from “Sounff” to the standard Indian term “saunf” while retaining “sonf” once as a natural transliteration variant.
- Kept the existing URL and canonical to avoid unnecessary migration risk.
- Replaced fixed purity, colour, moisture, volatile-oil, size and origin claims with buyer-defined identity, sieve, physical, composition, safety and lot-release fields.
- Connected fennel to the related fenugreek route and the purchase-specification workflow.

### Fenugreek seeds

- Added separate enquiry paths for ordinary food-ingredient/grinding use and seeds intended for sprouting.
- Clarified that normal spice acceptance does not establish sprouting suitability or pathogen control.
- Added identity, physical, composition, microbiology, residues, treatment, packing and lot-release requirements.
- Replaced universal document promises with an individually contracted commercial, origin, phytosanitary, treatment and analytical document set.

### Green cardamom

- Removed fixed 6/7/8 mm and AGEB/Alleppey/LG grade data because the offered lot had no published measurement evidence.
- Added Codex identity and style fields for whole unopened pods, opened pods and seeds.
- Replaced nominal size labels with a measured capsule/sieve distribution, sampling plan and tolerance.
- Added empty/light, immature, open, damaged, mould, insect, foreign-matter, colour-sample and lot-release controls.

### Black pepper powder

- Separated whole black pepper specifications from ground powder specifications.
- Limited bulk-density fields to whole pepper and added retained/passing mesh, grind uniformity and metal-control fields for powder.
- Added a pre-treatment, process and post-treatment microbiological workflow covering sampling, methods, cross-contact controls, packing environment and COA timing.
- Made treatment availability and microbiological performance conditional on the contracted lot evidence.

### Dry ginger powder

- Separated whole rhizomes, pieces and ground powder according to Codex styles.
- Added retained/passing mesh distribution, moisture, ash, acid-insoluble ash, optional volatile-oil, sensory-sample and treatment fields.
- Required peeling, bleaching, microbial treatment or untreated status to be declared instead of assumed.
- Added destination safety, moisture-barrier packing, representative sampling and lot-release requirements.

## Primary sources

- FSSAI standards for salt, spices, condiments and related products: <https://fssai.gov.in/upload/uploadfiles/files/Chapter%202_9_Salt_Spices_Condiments_and_related_products.pdf>
- Codex Standard for Small Cardamom, CXS 357-2024: <https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B357-2024%252FCXS_357e.pdf>
- Codex Standard for Black, White and Green Peppers, CXS 326-2017: <https://www.fao.org/fao-who-codexalimentarius/sh-proxy/ru/?lnk=1&url=https%3A%2F%2Fworkspace.fao.org%2Fsites%2Fcodex%2FStandards%2FCXS+326-2017%2FCXS_326e.pdf>
- Codex Standard for Dried or Dehydrated Ginger, CXS 343-2021: <https://www.fao.org/fao-who-codexalimentarius/sh-proxy/pt/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B343-2021%252FCXS_343e.pdf>
- Spices Board quality and analytical-services overview: <https://indianspices.com/quality.html>

## Validation

- FAQ/schema and cluster-link validator: 925 FAQPage blocks and 40 cluster pages passed.
- All five pages passed one-title, one-H1, one-canonical, description-length, JSON-LD and removed-claim checks.
- Full static audit: 1,728 renderable pages, 1,428 indexable pages and 1,428 sitemap URLs.
- Existing editorial queue unchanged: 24 title-length flags and 23 description-length flags.
- Diff whitespace and Python compilation checks passed.

## Scope boundary

The pages do not guarantee spice identity, origin, size, colour, composition, sprouting suitability, microbial treatment, microbiological results, residue acceptance, document availability, packing approval or destination compliance. Those outcomes depend on the written specification, current law, named methods, representative sampling, approved lot evidence and buyer verification.

## Deployment status

Local implementation only. No production deployment or indexing request was made.
