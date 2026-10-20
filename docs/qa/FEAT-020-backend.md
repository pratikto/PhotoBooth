# FEAT-020 provider reconciliation - 2026-10-20

Approved scope: audit remediation on `feature/qris-payment` only. No master merge, release or live payments.

The new `CheckoutBackend` + `CheckoutStore` service is the intended authoritative server path; the older `checkout_service.py` is retained as an isolated prototype until server wiring is updated. No production deployment is implied.

## Implemented and tested

- Duplicate checkout uses the same persistent order/key; lost charge responses are recovered by GET Status, never by blindly charging again. An order never confirmed by the provider remains held for investigation instead of being silently replaced.
- Polling reconciles pending/unknown orders with the provider, with a persisted three-second minimum between polls. Network failure preserves the order and returns `verification_pending`.
- Callback signed fields are authenticated before a status query. The independently fetched response must match order, amount, IDR, QRIS, merchant, transaction reference and fraud status when supplied.
- Pending, settlement, expiry, cancellation, rejection and refunds have explicit handling. Late/out-of-order callbacks reconcile the latest provider status. An old paid order cannot unlock another visit.
- Valid notifications are acknowledged only after application (or safe unknown-order ignore). A transient verification problem records RETRY and raises an error for HTTP 503; no false success acknowledgement.
- QR image URLs are restricted to the official Sandbox origin, port 443 and known QR endpoint paths. Missing actions during GET Status use the documented transaction-ID endpoint.

## Actual validation before push

Linux/Python 3.13.5: `python tools/run_qris_tests.py`: **85 PASS, 0 FAIL, 0 SKIP**. Includes the original 58 tests, 14 ledger durability tests, and 13 realistic offline service tests. These are synthetic provider responses; no merchant credentials, actual Midtrans transactions, Windows capture or physical printing were used. HTTP v2 wiring and GUI integration are subsequent steps, not completed by this service-only commit.

References checked: https://docs.midtrans.com/reference/qris ; https://docs.midtrans.com/reference/get-transaction-status ; https://docs.midtrans.com/reference/best-practices-to-handle-notification .
