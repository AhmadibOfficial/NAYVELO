# NAY-006 — Billing simulation threat model

## Trust boundaries

- **Safe:** checked-in, fictional shared fixture; in-memory interactive assumptions; local development web server binding to `127.0.0.1`; bundled offline Flutter asset.
- **Untrusted:** manipulated JSON fixture, browser DOM inputs, external service routes, inputs to hypothetical money calculations, future carrier files, real subscribers.
- **Absolutely outside scope:** actual payments, top-ups, refunds, chargebacks, debit instructions, invoicing, real tariffs, real usage feeds, PCI handling, NIN or identity records.

## Key risks and mitigations

| Risk | Mitigation / validation |
| --- | --- |
| Demo costs mistaken for real tariffs | Explicit fictional labels on every display; hypothetical user-controlled rate, no prices in sellable plans |
| Unauthorized money movement | All mutating endpoints return 403, no payment provider SDK, no checkout or wallet routes |
| Synthetic values replaced with real identifiers | Exact fixture schema, fixed dates, allowed keys, no identity fields; fail closed |
| Billing overflow/precision defects | Integer MiB and kobo with bounds, half-up rounding, repeatable cross-platform checks |
| Network tracking of users | No beacon, analytics, browser storage or subscriber auth; only read-only same-origin fixture request |
| Incorrect inference from projections | State formula, limited 7-day synthetic basis, exclude fees/taxes, do not imply financial certainty |
| User spoofing real telecom services | Localhost only; conspicuous SIMULATION_ONLY labels and blocked live endpoints |
| Account takeovers via billing changes | No accounts, credentials, sessions, plans or identity bindings; no state-changing API |

## Future production requirements (not implemented)

Formal regulated partnerships, privacy impact assessment, consent and retention policies, metering reconciliations, billed-vs-rated event attestation, price versioning, idempotent ledger and reversals, dispute resolution, audit trails, authorization and role segregation, anti-fraud monitoring, data minimization and finance/telecom counsel review are required separately before a real service.
