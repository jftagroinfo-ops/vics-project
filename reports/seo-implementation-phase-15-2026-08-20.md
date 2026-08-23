# SEO Implementation Phase 15 — 20 August 2026

## Outcome

This phase addressed opportunity-map ranks 67–71: yellow peas, the psyllium-husk product page and buyer guide, Indian raisins and S30 white sugar.

## Implemented work

### Yellow peas

- Separated whole peas from split/dehulled peas and identified the food product as *Pisum sativum*, without implying planting-seed suitability.
- Replaced fixed foreign origin, moisture, packing and container-payload values with lot-declared crop/origin, defect, treatment, packing and loading fields.
- Added Codex pulse context plus purchase-specification and sample pathways.

### Psyllium husk product page

- Identified psyllium husk as the seed husk of *Plantago ovata* and separated whole husk from milled powder.
- Reframed commercial purity percentages as method-dependent terminology rather than self-proving grades.
- Added swelling-method, moisture, ash, acid-insoluble ash, extraneous-matter, microbiology, residue, heavy-metal, treatment, ethylene-oxide, cross-contact and packing fields.
- Connected the page to the buyer guide, COA guide, purchase-specification guide and sample workflow.

### Psyllium buyer guide

- Replaced unsupported global-share, crop-condition, static FOB-price, freight, grade-performance, market and timing claims with a source-backed importer workflow.
- Added the official FSSAI identity and reference values for moisture, total ash, acid-insoluble ash, swelling volume and organic extraneous matter, while making methods and lot evidence explicit.
- Added COA review, safety/treatment evidence, purchase-order and comparable-quote checklists.
- Updated the visible modification date and Article JSON-LD to 20 August 2026.

### Indian raisins

- Defined raisins as dried *Vitis vinifera* fruit and added seedless/seed-bearing type and Codex style terminology.
- Removed informal A/AA/AAA, long/round and fixed colour descriptions as standalone grades.
- Added measurable sieve/count sizing, approved colour sample, style-specific moisture/defect limits and drying-aid, bleaching, sulphur-dioxide, oil or coating declarations.

### S30 white sugar

- Clarified that S30 is a commercial granulation term, not a Codex sugar category.
- Replaced fixed ICUMSA, polarization, moisture, ash, reducing-sugar, packing, payload and “SGS verified” claims with lot-tested methods and a sieve-distribution specification.
- Added a dated policy notice: as checked 20 August 2026, relevant DGFT Schedule-2 sugar lines remain restricted until further orders, subject to specific permission and stated quota exceptions.
- Prevented the page from implying unconditional export availability before current DGFT/DFPD eligibility is verified.

## Primary sources

- Codex Standard for Certain Pulses, CXS 171-1989: <https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%3A%2F%2Fworkspace.fao.org%2Fsites%2Fcodex%2FStandards%2FCXS+171-1989%2FCXS_171e.pdf>
- FSSAI psyllium-husk notification: <https://fssai.gov.in/docs/food-law/regulations/amendments/nutraceuticals/6138887092069Gazette_Notification_Nutra_08_09_2021.pdf>
- Codex Standard for Raisins, CXS 67-1981: <https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%3A%2F%2Fworkspace.fao.org%2Fsites%2Fcodex%2FStandards%2FCXS+67-1981%2FCXS_067e.pdf>
- Codex Standard for Sugars, CXS 212-1999: <https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FStandards%252FCXS%2B212-1999%252FCXS_212e.pdf>
- DGFT Schedule-2 export-policy notification: <https://content.dgft.gov.in/Website/English-Notification%20No.%2060-2023.pdf>

## Validation

- FAQ/schema and cluster-link validator: 926 FAQPage blocks and 60 priority cluster pages passed.
- All five pages passed one-title, one-H1, one-canonical, description-length and JSON-LD parsing checks.
- Removed-claim scan returned no old fixed payload, origin, price, grade-table or lab-verification statements.
- Full static audit: 1,728 renderable pages, 1,428 indexable pages and 1,428 sitemap URLs.
- Existing editorial queue unchanged: 24 title-length flags and 23 description-length flags.
- Python compilation and targeted diff-whitespace checks passed.

## Scope boundary

The pages do not guarantee crop origin, commercial grade, purity definition, swelling performance, size, colour, treatment status, residue or microbiological results, packing, payload, export permission or destination acceptance. Those outcomes depend on current law, named methods, representative sampling, lot-linked evidence and the signed specification.

## Deployment status

Local implementation only. No production deployment or indexing request was made.
