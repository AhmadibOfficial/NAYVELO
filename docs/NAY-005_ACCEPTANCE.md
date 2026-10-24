# NAY-005 — Subscriber Account Simulation and Privacy-first Data Model

## Functionality

- Exactly two invented non-identifying aliases: `DEMO-ALPHA` and `DEMO-BETA`.
- No registration, session, KYC, login, user identifiers, eSIM credentials, telephony or financial operations.
- Pure state model: `preview`, `paused`, `locked`, `closed`. `locked` and `closed` are terminal in the demonstration; reset recreates a fictional account but never represents real account recovery.
- Optional preferences `productAnalytics` and `productNews` both default to false. Changing a toggle is a UI illustration, NOT enrollment in marketing or analytics.
- Browser and Flutter hold changes in component memory only; switching examples or resetting discards changes. Refreshing the browser or restarting the app discards all changes. No cookies, IndexedDB, localStorage, network requests or remote telemetry.
- Backend has a pure `DemoAccount` model and locally bundled JSON policy for testable transition rules, but **no read/write account endpoints**.
- Both existing NAY-002/NAY-003/NAY-004 functionality and safety tests must remain unmodified.

## Validation

1. `python3 scripts/validate.py`
2. `node --check web/account_lab.js && node tests/account_lab_test.cjs`
3. On the SDK-equipped Kali system: `cd apps/customer_app && flutter pub get && flutter analyze && flutter test`
4. Confirm every simulated live subscriber/auth/registration/payment/telecom endpoint returns HTTP 403, including GET/POST at `/api/v1/accounts`, `/api/v1/subscribers`, `/api/v1/login`, `/api/v1/sessions`, `/api/v1/recovery`, `/api/v1/sim-swap`.
5. Manually review accessibility: headings, labels, keyboard focus, screen-reader announcements, mobile reflow, optional toggles and terminal-state warning.
6. Review code and commit on a feature branch; only afterward mark NAY-005 done and merge manually. Do not deploy automatically.

This milestone is a domain and UX simulation, not a production identity system or verification of Nigerian telecom/data compliance.
