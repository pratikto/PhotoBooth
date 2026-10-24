# P4b Sandbox → P5 readiness (FEAT-020 / FEAT-022)

Owner explicitly approved QRIS Sandbox and subsequent P5 preparation on 2026-10-24,
with Windows manual tests at the end. Production payments, scanner activation,
deployment, merge and release remain outside scope. Baseline/rollback:
`d6fb5d4e57c86073437748360576c7e4b8adac8b` on `feature/portrait-kiosk-v2-next`.

The last visual/audio retest is owner-reported **8/8 PASS**, followed by “udah
clear semua”; tested HEAD/device metadata remain unknown. Earlier twenty-cycle
reports remain preserved. BUG-017 is owner-reported PASS / monitoring: no new
decoder patch or measured cause is claimed. See [raw record](owner-acceptance.json).

## Stage 1 — reuse existing payment service

Reuse the latest QRIS branch `3cc8a8e360e8c2100a3077b755664eb61d0216ea` read-only.
[Hashes](reused-source.json) cover the unchanged backend/client/session, launcher
helpers and relevant original tests. No branch merge or v1 GUI replacement.
Server quotes, authenticated booth identity, durable idempotency, one-use grants,
provider reconciliation and restart recovery remain in the original code.

The legacy `app_qris`/`ui_qris` binds v1 capture and layouts. The v2 presentation
adapter will use accepted v2 widgets and the existing payment client/session;
this compatibility exception does not replace backend logic. The original
service has no trusted Meong Fly promotion contract: local wins cannot authorize
a provider discount. Sandbox full-price checkout must show explicit consent
before discarding a local DEMO offer. Trusted merchant promo remains an external
gate. No merchant credentials or external provider calls are used in cloud QA.

Stages: unchanged service + focused tests; native v2 handoff + isolated Sandbox
launcher + focused integration; P5 readiness tooling, one final regression,
800×1280/452×900 evidence and a final Windows form. Real merchant, hardware,
printer/Drive/privacy/retention acceptance cannot be certified by fixtures.

Stage 1 verification: 124 original focused tests PASS (0 errors/failures), Linux Python 3.12; command loads the twelve test modules recorded in reused-source.json. Initial migration-test missing dependency was corrected by retaining unchanged historical `payment_orders.py`; the active backend does not use that prototype. [Output](reuse-tests.txt).
