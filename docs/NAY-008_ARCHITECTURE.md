# NAY-008 — Carrier integration architecture (NO LIVE CONNECTION)

## Scope and non-claims

This milestone builds interface-only definitions, a **permanently blocked local adapter**, synthetic public readiness data and offline contract tests. NAYVELO remains **SIMULATION_ONLY**. This project is **not** licensed as an MVNO, an eSIM provisioning platform, a subscriber-management system, a certification result or a working mobile network.

## Logical ownership and trust boundaries

```text
Customer web/Flutter simulator (no identity or network access)
       |
       v
Local demo HTTP service (GET /api/v1/demo-carrier-readiness only)
       |
       v
Immutable public readiness fixture ----> Web and Flutter read-only views

Future *separate* implementation after approvals:
NAYVELO internal APIs -> policy/auth/KYC gates -> carrier integration gateway
   -> mutually authorized host MNO interfaces
   -> authorized SM-DP+ provisioning service (consumer RSP)
   -> subscriber/network usage and service reconciliation systems
```

No future box above is implemented or wired. `FutureCarrierPort` documents the interface intention; `BlockedCarrierAdapter.execute()` always raises `CarrierOperationDenied` and cannot be enabled by toggling an environment variable.

## Interface catalog (all blocked)

1. **Host connectivity**: validate contractual partner identity, endpoints, mTLS requirements, credential custody and version negotiation *only in a separate approved implementation*.
2. **eSIM provisioning**: possible future SM-DP+ and consumer RSP status contracts. The present simulator cannot issue, install, download, or swap profiles and contains no EID, ICCID, IMSI, activation code or QR credential.
3. **Service management**: conceptual interface for number assignment and controlled activate/suspend/resume flows; no lifecycle operations, voice/SMS, numbering, porting or authorization engine exists.
4. **Usage and charging**: future signed usage events, UTC windows, deduplication/idempotency, reconciliation and dispute processes; no real network feeds, rates, invoices or payment execution.
5. **Subscriber registration**: future regulator/operator-approved identity process and data minimization; the demonstration does not request or handle NIN, biometric, phone-number or customer records.

The JSON schema defines only an *example* action name and `EXAMPLE_ONLY` marker. It is not a carrier-specific request body, implementation specification, or evidence that NAYVELO conforms to GSMA protocols.

## Future security and privacy design requirements

**Requirements, not features**: documented legal basis/permissions; strict service-to-service authentication and mTLS; isolated partner gateway; encrypted secrets with rotation and access approval; replay protection and idempotency; signed callbacks; policy-enforced request validation; per-tenant/partner isolation; least-privilege, independent approval of subscriber-sensitive changes; SIM-swap/fraud controls; emergency/legal obligations; tamper-evident limited-retention audit records; device/partner lifecycle testing; incident response; independent security reviews; disaster recovery and host-network acceptance testing.

**Data classification**: no real personal or sensitive identifiers are included or accepted in synthetic interface fixtures. Future personal/sensitive subscriber data requires an explicitly separate privacy impact assessment and documented retention, encryption, disclosure, consent/registration and deletion policies. No production traffic, credentials, private customer data or test-profile secrets in git/CI.

## External dependencies and references

- NCC MVNO framework: https://ncc.gov.ng/sites/default/files/2024-12/Final_FrameworkDocument_for_Upload.pdf
- NCC licensing application process: https://www.ncc.gov.ng/industry/licensing/licensing-application-process
- GSMA consumer eSIM specification index: https://www.gsma.com/solutions-and-impact/technologies/esim/esim-specification/
- GSMA consumer RSP technical specification (SGP.22 v2.7): https://www.gsma.com/solutions-and-impact/technologies/esim/gsma_resources/sgp-22-v2-7/

Check applicable versions and NCC policies again before negotiating an actual deployment. The specification references are *design research*, not certifications, integrations or claims of compliance.
