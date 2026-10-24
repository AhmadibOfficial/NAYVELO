# NAY-007 — Mock Administrative Analytics Threat Model

**Assets:** no real assets: fictional aggregate activity, synthetic interest counters, unpriced plan concepts, simulated role views, inert operational statuses.

**Trust boundary:** anything in the local web page, Flutter assets or read-only fixture endpoint is **public test data**. Client-side role selection is an illustration of potential navigation scope, not authentication or authorization; there are no credentials, secrets or production permissions anywhere.

| Threat | Mitigation/acceptance | Future production requirement |
|---|---|---|
| Fake role escalation | All mock roles operate only on public aggregate fixture; role selection never drives a backend privilege or write | Centralized identity, MFA and per-operation server-side authorization |
| Personal information inserted into fixture | Strict exact-key whitelist at all nesting levels in Python/Dart/JS; poisoned fixtures refused | Legitimate privacy impact assessment, least-privilege data classification and redaction |
| Real activity confused for genuine metrics | Persistent visible fiction disclaimers; unpriced plans, no subscriber numbers or revenue claims | Verified data lineage, aggregation, reconciliation and definition of business metrics |
| Malicious admin requests | Read-only public demo fixture route; all methods other than GET blocked, real admin and export paths 403 | Network isolation, request authorization, audit, just-in-time elevation, approval workflows |
| Cross-tenant leakage | No tenants/identities exist in public fixtures | Tenant scoping, negative cross-tenant tests and secure audited querying |
| XSS / untrusted content | DOM elements use `textContent`, no HTML injection; strict fixture validator, CSP | Content and output encoding controls, audit logging and independent review |
| Release mistake | Installer clean-branch and milestone prerequisite checks, no commits/deploy/CI changes | Operational sign-off, independent security tests and explicit regulatory approvals |

**Important:** This demo does not provide an operational, internal, access-controlled admin console. Production access control has not been implemented or tested.
