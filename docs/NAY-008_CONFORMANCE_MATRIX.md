# NAY-008 — Certification and partner readiness evidence matrix

**Current engineering outcome: prototype PASS (offline tests only).** **Carrier certification: NOT STARTED.** **Operational license/authorization: NOT VERIFIED.** No partner tests, network traffic or eSIM provisioning occurred.

| ID | Capability / control | Offline check | Required real-world evidence | Current status |
|---|---|---|---|---|
| C01 | Host carrier interface contract | Fictional allowlisted action values and protocol shape | Executed host-network agreement, approved commercial model, detailed service SLA and technical interface specification | NOT VERIFIED |
| C02 | eSIM RSP / SM-DP+ | Fail-closed action test, no activation codes | Authorized SM-DP+ partner, selected SGP.22/SGP.23 applicability, eUICC/device compatibility and partner test results | NOT VERIFIED |
| C03 | Service state and numbering | Deny all state-changing commands and routes | Approved numbering, provisioning state machine, number portability rules, rollback, emergency services as applicable | NOT VERIFIED |
| C04 | Subscriber registration | Reject subscriber identity fields in fixture | Current NCC subscriber registration review, lawful procedures, operator acceptance, privacy assessment | NOT VERIFIED |
| C05 | Usage reporting | Synthetic data only, prevent `/usage` write | Signed usage events, deduplication, rating audits, time sync, settlement/reconciliation, dispute resolution | NOT VERIFIED |
| C06 | Network security | Socket-denial tests and zero external URLs | mTLS, keys/HSM, secrets isolation, signing, callback verification, pen test and independent assurance | NOT VERIFIED |
| C07 | Resilience / operations | Predictable denial and no hidden enable switch | SLAs, support playbooks, customer protection, fault/incident response, disaster recovery, fraud response | NOT VERIFIED |
| C08 | Commercial authorization | No charges/subscriptions, all gates blocked | NCC licensing, security clearance where applicable, lawful tariffs/disclosures, partner contracts, authorized launch approval | NOT VERIFIED |

## Gate rules

- Offline passing tests **never** mark a legal or third-party certification as passed.
- Do not change `SIMULATION_ONLY` or the existing release gates to green based on mock tests.
- No network credentials, host URL, EID, ICCID, MSISDN, NIN, activation code, QR credential, webhook secret, payment token or test subscriber data may be added to this milestone.
- Production requires separately reviewed code, secure infrastructure, authorized partner test accounts, legal review, explicit launch decision and independent evidence.
- The development agent may draft contracts and tests but may not negotiate licenses, connect to carriers, provision subscribers, deploy, collect charges or certify its own work.

## Acceptance evidence to retain

- The complete `python3 scripts/validate.py` output and `node tests/carrier_readiness_test.cjs` result.
- `git diff --check`, branch name, git status, and code review findings.
- Local Flutter `flutter analyze`, `flutter test`, and emulator checks, including keyboard/screen-reader review.
- A trace showing attempted provisioning and network calls are rejected without any socket access.
