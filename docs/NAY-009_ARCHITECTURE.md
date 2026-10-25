# NAY-009 — Offline partner contract laboratory

## Boundaries

This is an educational, fully **SIMULATION_ONLY** implementation. It is **not** a carrier sandbox client and **not** a GSMA SGP.22, SM-DP+, LPA, ES9+, or operational MVNO implementation. No URL/host, credentials, IMSI, EID, ICCID, NIN, MSISDN, subscriber account, payments, SMS, voice or real network API calls are accepted or used.

Data flow: **strict fixed local fixture → immutable scenario choice → in-memory synthetic response → exact response allowlist + deterministic deadline/sequence/correlation checks → public read-only report → web/Flutter educational displays**.

The public report lists one nominal response accepted **only as a fictional conformance example**, with eight safely rejected failure cases. This does not establish an external partner passed anything. Flutter uses a compiled offline asset; the web client reads the local demonstration API and makes no write request.

## Future partner acceptance (not available in this milestone)

Require an executed host-network contract, licensed operating model and authorized partner-owned test sandbox. Separately design mTLS, scoped machine identity, key rotation, partner message-signing and replay protection, audited authorization, network segmentation, idempotency, error taxonomy, retry/backoff, schema version negotiation, sensitive-data minimization, key custody, reconciliation and escalation. Formal test specifications must be jointly accepted, and evidence must be independently reviewed.

References (not certification):
- NCC MVNO framework: https://www.ncc.gov.ng/industry/licensing/licensing-documents-frameworks
- GSMA eSIM specifications: https://www.gsma.com/solutions-and-impact/technologies/esim/gsma_resources/sgp-22-v2-7/
- OWASP API Top 10: https://devguide.owasp.org/en/07-training-education/07-api-top-ten/

## Threat considerations

- **Unsafe external consumption:** strict field names/types; no deserialization into operational commands.
- **Replay/duplication:** exactly one expected response; no side effects even if invalid.
- **Deadline:** deterministic simulated threshold; not a real network timeout metric.
- **Correlation/order:** tag and sequence must match fixed fictional values.
- **Data injection/false permissions:** unexpected PII or URLs cause rejection; zero credentials or external endpoints.
- **Misleading assurances:** no certificate, license or partner readiness statuses can be made positive by fixtures.
