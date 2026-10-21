# NAYVELO Release Gates — Safety and Compliance

## Current policy: SIMULATION_ONLY

Live cellular connectivity, eSIM activation, phone-number assignment, carrier integrations, sensitive identity verification, SMS/voice, paid subscriptions and payment capture are NOT permitted in the prototype.

## To unlock real services (separately, never by autonomous agent)

- Obtain legal assessment of applicable NCC MVNO licensing requirements and approvals.
- Execute enforceable host-network agreement covering eSIM capability, prices, subscriber eligibility, network service, numbers, support, incident handling and customer protection.
- Engage an authorized SM-DP+ eSIM provisioning partner or approved host integration.
- Approve a compliant NIN-based subscriber identity verification design and Nigeria Data Protection Act controls; protect sensitive information.
- Complete threat modeling, architecture/security review, independent penetration test, fraud controls, privacy impact assessment and operational readiness checks.
- Confirm customer consent, cancellation/refund policies, accurate terms and operator-specific tariff rules.
- Require explicit authorized human approval and audited production rollout.

The prototype has no runtime switch, environment variable, mock toggle or hidden endpoint that enables real provisioning. A separate reviewed implementation is required.

## Always-blocked automated changes

- Direct network provisioning or SIM profile issuance; operator credential access.
- KYC/NIN biometric collection or storing real national identifiers in the demo.
- Charging a card, wallet, bank account or collecting actual subscription fees.
- Modifying infrastructure, secrets, branch protection, CI privileges, production DNS, or publishing a live service.
- Silent merging, unreviewed production publishing or relaxing these release gates.
