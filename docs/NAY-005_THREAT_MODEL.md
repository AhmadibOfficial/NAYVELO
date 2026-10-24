# NAYVELO NAY-005 — Subscriber Account Takeover and Privacy Threat Model

**Scope:** Fictional, in-memory account lab. **Out of scope and prohibited:** live account enrollment, subscriber identity, carrier provisioning, payment, login, OTP, password reset, SIM-swap, porting, device fingerprinting, analytics telemetry, location collection and real KYC/NIN processing.

| Threat scenario | Potential production harm | Design requirement before a future real implementation | Current demo behavior |
| --- | --- | --- | --- |
| Account enumeration during registration/recovery | Identifies customers and supports targeting | Generic responses, consistent paths/timing where feasible, rate limits | No real account lookup or login routes (403) |
| Credential stuffing and password spraying | Unauthorized account entry | Phishing-resistant MFA/passkeys where available, throttling, anomaly detection and incident response | No credential entry or auth mechanism |
| Recovery/social-engineering bypass | Attacker recovers another subscriber account | Identity proofing consistent with licensed carrier and legal requirements, verified independent recovery channels, step-up and delayed high-risk changes | Locked/closed demo states cannot self-unlock |
| SIM swap, eSIM replacement or port-out takeover | Number takeover, interception and loss of service | Strong fresh authentication and step-up, consent, notification, hold periods where appropriate, reversible fraud controls, auditable human escalation | No network number, eSIM or provisioning requests |
| Insecure direct object reference | Reads or modifies a different customer's data | Server-side per-subject authorization and tenant separation verified with negative tests | Two public, fixed aliases; no API or persistence |
| Token/session theft or fixation | Account impersonation | Server-managed session lifecycle, secure cookies/tokens, reauthentication, revocation and replay detection | No tokens, cookies or sessions |
| Accidental PII in logs/telemetry | Identity exposure and regulatory impact | Field inventory, minimization, retention and deletion rules, access controls, encryption, tested audit-log redaction | No real PII fields or network calls; HTTP access logs suppressed |
| Fake optional consent | Unlawful marketing or tracking | Granular explicit choice, evidence/withdrawal mechanism and vendor review | Both toggles default OFF; no messages or tracking |
| Hostile automation/build changes | Gate bypass or external calls added | CI policy tests, protected branches, review, dependency and secret scanning, manual release | Installer rejects dirty/non-main or unreviewed NAY-004; offline regression tests |

## Trust boundaries

1. UI state is **not authorization** and must never become an entitlement to provision a real eSIM.
2. Static fixture IDs are not customer identifiers; never replace them with realistic-looking phone numbers, NIN, IMEI, EID or names in code or test data.
3. Production identity verification must not inherit demo state transitions. It needs separately designed services, audits, approvals, production authentication, and NCC/data-protection review.
4. Any future partner integration is a separate security project and release authorization, not a runtime flag.

## Security review checklist for later licensed operations

- Independent auth/session threat model and abuse scenarios covering number portability, eSIM replacement, account recovery and social engineering.
- Secure identity verification, consent, retention, controller/processor agreements and a DPIA where required.
- Account and device binding with approved step-up and recovery, lockout denial-of-service protections and customer recourse.
- Rate limits (per IP, account and behavior), opaque enumeration-safe responses, alerting and tested incident procedures.
- Offline/online penetration testing with explicit authorization, and controlled deployment that keeps keys and audit trails separated.

References: OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html ; OWASP MFA Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html . These are design references, not a compliance certification.
