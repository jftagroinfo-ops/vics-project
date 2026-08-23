# Native-Language SEO Quality Governance

## Publication rule

Language-folder completeness and correct `lang`/hreflang markup do not prove native commercial quality. New or materially changed localized commercial copy may be approved only through `data/localization-review-register.csv`.

An approved record requires:

1. A real named native-language reviewer.
2. The reviewer's language and relevant commercial or legal qualification.
3. The market and URL scope reviewed.
4. The exact source batch/version.
5. A completed review date.
6. Separate commercial and legal status.
7. Search Console country/query/page evidence and a recorded demand decision.

If Search Console evidence is unavailable, use `hold`; do not enter invented zero-demand conclusions. If a reviewer has not approved the copy, use `pending_native_commercial_review`; do not add a visible “native reviewed” claim.

## Demand decisions

- `proceed`: positive non-brand demand evidence supports creating or materially expanding the localized intent.
- `maintain`: retain an approved existing page while monitoring demand.
- `hold`: evidence or human review is incomplete.
- `retire`: evidence supports consolidation/removal and the redirect/indexing plan has been reviewed.

## Validation

Run:

```powershell
python scripts/validate_localization_governance.py
python scripts/audit_localizations.py
```

The first command validates governance evidence. The second checks renderable-page parity, fallback markers, language metadata and English sentence residue. Neither command substitutes for a native human review.
