# NAY-004 — eSIM Readiness Education

## Scope

A browser and Flutter educational wizard with three self-reported, nonidentifying answers: platform family, visibility of eSIM setting, and network-unlock awareness. No collection of IMEI, EID, ICCID, NIN, serial numbers, phone numbers, identities, photos, QR codes, precise model identifiers, or carrier credentials. In-memory only: no API writes, analytics, tracking, storage or native device interrogation.

## Required behavior

- Keyboard focus, `<fieldset>` / `<legend>`, labeled radio buttons, step indicator, status messages, back and reset controls; respect reduced motion.
- iPhone and Android settings guidance has specific manufacturer sources, but no blanket assurance of compatibility.
- All outcomes are unverified and educational, even if a user selects three favorable answers.
- Existing `SIMULATION_ONLY` backend and `403` responses for activation, payment and identity-sensitive routes remain in force.
- Do not add network access, native permissions, device fingerprinting or download any eSIM profiles.
- Keep NAY-002 onboarding, NAY-003 plan catalog, their tests, CI rules and release gates unchanged.

## Official manufacturer documentation (for educational editorial review; accessed 2026-10-21)

- Apple: https://support.apple.com/en-us/118669 — setup and carrier preconditions; models and regional differences.
- Apple: https://support.apple.com/en-us/118227 — carrier lock check under Settings > General > About.
- Samsung: https://www.samsung.com/ca/support/mobile-devices/galaxy-esim-and-supported-network-carriers/ — SIM manager and carrier/country variability.
- Google Pixel: https://support.google.com/pixelphone/answer/16115470 — Network & internet > SIMs > Add SIM.
- Google Pixel: https://support.google.com/pixelphone/answer/7107188 — network unlock and compatibility.

## Test and release record

Execute `python3 scripts/validate.py` and `node tests/esim_wizard_test.cjs` (if Node installed); execute `flutter analyze && flutter test` in `apps/customer_app` on an SDK-equipped workstation. Review changes, update task tracking upon acceptance, and merge manually. No deployment, provisioning, customer identity verification, purchasing or real telecom connectivity is authorized by this milestone.
