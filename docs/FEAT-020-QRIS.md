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
