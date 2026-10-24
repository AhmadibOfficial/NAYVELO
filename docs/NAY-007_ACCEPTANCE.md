# NAY-007 — Administrative Intelligence Dashboard Acceptance

## Scope

**PUBLIC SYNTHETIC DEMONSTRATION, not a production administrator application.** It is intentionally accessible to anyone who runs the local prototype. A mock role selection is NOT authenticated access and must never be wired to privileged backend systems. The target production admin console requires a separate architecture, identity provider, server-side RBAC/ABAC, tenant controls and security assessment.

## Acceptance checks

1. Dashboard shows exactly 4 fictional weeks of visits/onboarding previews/help requests; six invented plan-interest counts and three inert operational scenarios. All metrics are clearly labeled invented, not NAYVELO users, sales, telecom usage, verified revenue or service events.
2. Python model and JavaScript validate exact whitelisted fixture keys, types, bounds, aggregate arithmetic and all mode/source values. Unknown keys (including NIN, phone number, subscriber ID, credentials), real mode or new operational states fail closed.
3. Same bytes of fixture in `shared/synthetic_admin.json` and Flutter assets. Web issues exactly one same-origin read-only GET to `/api/v1/demo-admin` without credentials; Flutter uses the local bundled asset. No external data, persistent storage, payments, logging or actual telecom endpoints.
4. Mock viewer displays 3 summary figures; analyst additionally shows trend/activity and concept interest; operator additionally sees a read-only operational scenario. Neither client role selector confers actual security privilege or changes any backend state. Invalid role defaults to viewer (UI) / rejects (pure domain). No RBAC claims.
5. Protected API paths `/api/v1/admin`, `/api/v1/metrics`, `/api/v1/audit`, `/api/v1/exports`, `/api/v1/subscriber-admin`, `/api/v1/provisioning` are HTTP 403. All POST/PUT/PATCH/DELETE are HTTP 403 including demo admin endpoint, and billing/activation remain HTTP 403.
6. Run `python3 scripts/validate.py`, `node tests/admin_dashboard_test.cjs`, `flutter analyze`, `flutter test` and manual keyboard/narrow-screen accessibility checks on the real project; inspect Git diff before review.

## Restricted release

Only a simulator-only frontend and static test fixture. Do not enable identity management, user-facing real dashboards, production admin access, data exports, real analytics, carrier provisioning, pricing/payment collection, deploys or monitoring. Finish review and merge of NAY-006 before applying. NAY-007 also requires review, passing Flutter gates, and explicit merge approval before advancing to NAY-008.
