# NAY-009 acceptance checklist

- [ ] NAY-008 reviewed, marked done and merged to clean main/develop (the installer enforces this).
- [x] Nine strictly fictional scenarios defined: one nominal response, eight fail-closed error cases.
- [x] No socket, requests, subprocess, HTTP client or external partner integration in simulation engine.
- [x] Contract fixtures and Flutter copy have byte-for-byte consistency tests.
- [x] Strict validation rejects fields for IDs, secrets, URLs, false licensing and live activation.
- [x] Read-only demo API + browser scenario selector never issues an external request.
- [ ] Run `python3 scripts/validate.py` and `node tests/partner_lab_test.cjs` on your Kali project.
- [ ] Run `flutter pub get && flutter analyze && flutter test` in `apps/customer_app` on Kali.
- [ ] Review diff and local UI; explicitly approve a merge.

**No commercial activation, payments, provisioning, subscriber KYC or production deployment is in scope.** All certification and third-party approval gates remain unverified.
