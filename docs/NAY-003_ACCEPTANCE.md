# NAY-003 — Subscription Catalog & Plan Comparison

Scope: simulator-only catalog; no pricing, data/voice/SMS entitlements, coverage or service availability claims.

## Canonical data

`shared/plans.json` is canonical; `apps/customer_app/assets/plans.json` is an identical offline shipping copy checked byte-for-byte by Python tests.

## Delivered

- Python catalog validation: rejects non-null allowances/prices, purchasable flags and unsafe status.
- Web duration filter, 2–3 plan comparison, explicit unknown values, keyboard-friendly native controls and read-only API fetch.
- Flutter offline catalog, duration filtering and 2–3 plan comparison.
- Regression tests, including fail-closed payment/subscription/eSIM operations.

## Verification

```bash
python3 scripts/validate.py
cd apps/customer_app && flutter analyze && flutter test
```

The Flutter test command requires Flutter SDK and generated Flutter platform folders only for emulator/device runs; widget tests need a working Flutter SDK and `flutter pub get`.

## Release boundary

Do not claim these concepts are offers. All prices, data, call, SMS, hotspot, rollover, network, purchase and activation capabilities are unconfirmed or blocked. No requests for NIN, SIM credentials or customer financial data.

## Gate for NAY-004

Inspect the proposed diff, verify tests, and merge the NAY-003 feature branch by human review. Mark NAY-003 done only after merge. The autonomous runner must start from clean main/develop.
