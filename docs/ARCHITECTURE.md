# Meong Photobooth - Current architecture

## FEAT-020 feature branch, 2026-10-20

`main.py` selects the unchanged DEMO PhotoBoothApp by default. Explicit qris-mock/qris-sandbox selects QrisPhotoBoothApp, inheriting the existing camera, template, capture, retake, composition, printing and Drive behavior. Unknown payment modes fail closed.

| Boundary | Modules and responsibility |
| --- | --- |
| Main GUI/controller | app_qris.py, ui_qris.py: worker-based polling, provider QR image display, automatic admission, existing photo/results flow and completion acknowledgement |
| Kiosk durable state | qris_session.py: frozen visit/journal before network, process lease, one local capture binding, restart recovery hold; no merchant secret |
| HTTP client | qris_kiosk_client.py: per-booth auth, persistent Idempotency-Key, strict environment/order/grant checks, bounded responses and no redirects |
| Server boundary | qris_api.py, qris_server.py: strict input, authenticated order scope, bounded streaming, off-thread blocking calls, factory/lifespan, Sandbox-only credentials |
| Authoritative payment service | checkout_backend.py, checkout_store.py: server pricing, idempotent order/grant, independent payment/service state, reconciliation and redacted event ledger |
| Provider boundary | midtrans_sandbox.py, qris_evidence.py: fixed Sandbox API, authenticated transport, signature and independent provider-response validation |
| Offline trial provider | qris_mock.py: persistent explicitly non-payable simulation; both server and kiosk must opt in |
| QR pixels | qris_images.py: validated provider image, bounded stream/dimensions; mock QR clearly marked NOT QRIS |

The old payment_ledger.py/payment_orders.py/checkout_service.py remain isolated prototypes, not the server entrypoint's payment authority. Existing photo manifests gain an additive payment block (mode/order/visit/grant/amount). Payment QR and photo-folder QR remain different artifacts.

No network work runs on the Kivy UI thread; widget/texture updates do. One GUI worker prevents overlapping operations. Server SQLite uses explicit transactions and persistent deduplication; deployment is a single-worker Sandbox trial, not a certified multi-region payment service. Default mock trials do not print paper. A partial-capture restart requires operator reconciliation instead of automatic recapture/reprint.

[Current QRIS contract](FEAT-020-QRIS.md), [trial/deployment boundaries](QRIS_TRIAL.md), [test evidence](test_checklist.md). The complete previous architecture of the unaffected application subsystems is preserved verbatim in [ARCHITECTURE.pre-qris-20261020.md](ARCHITECTURE.pre-qris-20261020.md). Its dated no-provider statements are superseded for this feature branch only; no live QRIS or master merge is implied.
