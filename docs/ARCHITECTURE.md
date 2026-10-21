# Architecture / evolution

Current (prototype): a static customer web app, local read-only Python `http.server` API, Flutter source app, and local coding/verification orchestration. No database is required for the mock. There is no production authentication or remote hosting.

Proposed future service platform (gated): Flutter and Next.js clients, a separately threat-modeled API (e.g. FastAPI), PostgreSQL with encryption/tenant boundaries, idempotent billing, an audit/event system, sandboxed telecom adapter, authorized host-network agreement, eSIM lifecycle services, and compliance controls.

The mock service uses locally defined catalog concepts only; no made-up prices, coverage or guaranteed device compatibility. Never deploy the present development HTTP server as a production telecom service.
