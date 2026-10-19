# FEAT-020 — QRIS full-auto payment (stage 1: mock ledger)

Status: **PARTIAL / MOCK ONLY**. Owner approved phased implementation on 2026-10-20. Branch: `feature/qris-payment` from stable `master`; no merge or production payment approval.

## Scope implemented in this stage
- `photobooth/payment_ledger.py`: standalone SQLite mock payment evidence/one-time session-claim ledger.
- `tests/test_payment_ledger.py`: tests unverified denial, idempotent recording, conflicting evidence, one-time claim and restart persistence.
- Existing `photobooth/payment.py` / Kivy UI unchanged. No bank API, webhook, real QRIS, backend, customer money movement or live automatic photo unlock.

## Important security boundary
The `verified=True` parameter is **not cryptographic proof**. This is only an isolated mock seam and must never be wired to kiosk/UI or an untrusted HTTP request. Before any production use, move payment verification and authoritative claim into a server-side trust boundary with signed provider notifications, independent status reconciliation, amount/order/merchant checks, authenticated kiosk identity, idempotency and race-safe durable transactions. A locally writable SQLite file is not sufficient payment authority.

## Next stages
1. Reconcile this prototype with existing `PaymentCoordinator`, `transaction_store`, and session lifecycle; design order and provider interfaces.
2. Implement server-side order pricing validation and sandbox QRIS provider; isolate credentials and verify callbacks.
3. Kivy status polling, expiry/cancellation and payment-page UI integration; keep muted ads and separate Drive QR.
4. Test duplicate notifications, stale/late payments, disconnected/reconnected kiosk, crash recovery and physical hardware. No live production until explicit acceptance.

## Local targeted test
`python -m unittest discover -s tests -p "test_payment_ledger.py" -v`

Initial isolated Python 3 container check: **5 PASS, 0 FAIL** (mock tests only; not a full repository regression or Windows hardware acceptance).

## Stage 2 (2026-10-20)
Checkout price validation module and five unit test methods committed. Targeted tests and full regression have not been run in this session. No backend or live payment enabled.

## Stage 3 (2026-10-20)
Added isolated SQLite order lifecycle `photobooth/payment_orders.py` and six regression tests in `tests/test_payment_orders.py`. Local Python 3 isolated test run: 6 PASS, 0 FAIL; full repository CI not verified. Code commits: `f757ae59`, `1ab2f41e`. No API, Midtrans connection, webhook verification, kiosk integration, merchant keys, or live payment. The `confirm_provider_status` method is an internal-only seam and must not be exposed to an untrusted caller; provider signature/status verification and booth authentication are still required. No merge to master.

## Stage 4 (2026-10-20)
Added `photobooth/midtrans_verify.py` and `tests/test_midtrans_verify.py` in commits `6ec7e836` and `3aacd137`. Verifier checks SHA-512 callback signature, positive whole-IDR amounts and independent provider status parity. This is an offline primitive only; it does not fetch the provider status, accept webhooks, create QRIS, or unlock the booth. Tests not executed in this session. Provider order IDs, status mapping, merchant configuration and actual sandbox response format must be validated before integration.

## Stage 5 (2026-10-20)
Added sandbox-only Midtrans Core API HTTP transport `photobooth/midtrans_sandbox.py` and five mocked-transport tests `tests/test_midtrans_sandbox.py` (commits `56bc1bba`, `08fb980f`). Endpoint is hard-coded to `api.sandbox.midtrans.com`, with server-side Basic Auth, timeout, bounded response and no production endpoint. **Tests not run or independently verified in this session.** No server, webhook route, real Midtrans sandbox transaction, merchant credentials or kiosk integration. Do not place MIDTRANS_SERVER_KEY in the kiosk or repository. Next: authenticated backend API, independently fetched provider status, webhook handler, and full regression.

## Stage 6 (2026-10-20)
Added `photobooth/checkout_service.py` (commit `f08ed287`) and six offline service tests `tests/test_checkout_service.py` (commit `6dad9543`). Server-side orchestration calculates price, requests sandbox QR, verifies signed settlement against an independent provider status query, and grants at most one claim through the order store. **Tests have not been executed or CI verified.** Service is not an authenticated HTTP API. Kiosk must not invoke service methods or provider credentials directly. Pending blockers: real Midtrans Sandbox response compatibility, QR action URL trust, provider outage recovery, expired/cancelled status handling, durable multi-process concurrency, authenticated booth HTTP routes, actual Kivy integration, full regression and hardware acceptance. No production or master merge.

## Stage 7 — Booth authentication primitive (2026-10-20)
Added `photobooth/booth_auth.py` (`bc876fa9`) and six offline test methods in `tests/test_booth_auth.py` (`525ba571`). Per-booth bearer tokens are validated against configured SHA-256 digests with constant-time comparison; cross-booth credential reuse is denied. **Tests have not been executed in this session.** This is not yet an HTTP backend or production credential provisioning. Token distribution, rotation, TLS, rate limits, deployment, signed provider callbacks, session handoff and full regression remain outstanding. Branch-only; do not merge into master without owner approval.

## Stage 8 — Incremental FastAPI staging routes (2026-10-20)
`photobooth/qris_api.py` introduced in commits `9273ef9`, `9772a67`, `d7a8bb0`: health, authenticated create/status/claim and webhook route. Six HTTP route tests added in `tests/test_qris_api.py` (`e26bdfa`). **No tests executed/CI verified in this session.** Server deployment, TLS, secret provisioning, webhook rate limits, provider error handling, request validation, real Sandbox integration, Kivy and Windows hardware testing are open. This API is NOT approved for public deployment. No master merge without explicit owner approval.
