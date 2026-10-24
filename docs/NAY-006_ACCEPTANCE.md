# NAY-006 — Billing and usage sandbox acceptance

**Scope:** Simulator-only UX on top of accepted NAY-005. No commercial product has been activated.

## Acceptance gates

1. The fixture under `shared/synthetic_billing.json` matches the Flutter asset byte-for-byte, uses seven fixed fictional daily usages and three fictional prior-month estimates, and contains no identity or carrier records.
2. The backend refuses extra keys, real/live modes, malformed history, identity fields, invalid amounts and contradictory assumptions. Pure math uses integer kobo, with 1024 MiB per GiB and half-up rounding on the final amount.
3. Web renders daily synthetic bars, 7-day usage, 30-day extrapolation, illustrative historical estimates, scenario rate/budget selectors and a prominent warning. It issues only one same-origin GET to `/api/v1/demo-usage`, and never writes local/browser storage or sends telemetry.
4. Flutter uses its bundled static fixture, displays the same math assumptions and includes widget/fixture safety tests. It cannot reach carrier, account or payment services.
5. All POST/PUT/PATCH/DELETE are HTTP 403, including against the demo endpoint; real billing, wallet, transaction, topup, checkout, invoice, usage and payment routes are HTTP 403 even on GET.
6. `python3 scripts/validate.py`, `node tests/billing_sandbox_test.cjs`, `flutter analyze`, and `flutter test` all pass in the actual NAYVELO repository; keyboard and screen-reader checks are reviewed manually.

## Interpreting the projections

Sample 7-day MiB total is 3,936. The 30-day extrapolation is `round-half-up((3936 / 7) * 30)` MiB. An illustrative rate of **₦1,250 per GiB** is a **chosen assumption**, not a NAYVELO price or quotation. The projected cost is `projected MiB × example kobo per GiB / 1024`, rounded to one kobo. Taxes, network-specific rules, fees, historical consumer behavior, bursts, roaming and real carrier data are all excluded. There is no invoice/payment balance, and the fictional history is *not* proof of actual service.

## Release boundary

No real subscriber information, payment gateway, tariff catalogue, carrier data, activation credentials, KYC, network integration, telemetry, live usage or production publishing. The static fixture is intentionally public test data. Finish NAY-005 and mark it `done` on clean `main` before applying. NAY-006 must receive its own review before being marked `done` and merged. NAY-007 can be queued afterwards; no silent auto-merge or deploy.
