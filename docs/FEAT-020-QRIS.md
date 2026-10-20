# FEAT-020 - Automatic QRIS in the main MEONG GUI

**Current, 2026-10-20:** implemented for an explicit **mock main-GUI trial**, with Sandbox provider wiring. **Not production-ready, not merged.** Tested source `7cf90ea95a32b4cf2feee16c21232069bc1aa9bb` on `feature/qris-payment`. Owner approved the audit recommendations and sequential execution through GUI trial readiness, not live money or master merge.

## Current architecture

`main.py` defaults to the original DEMO application. Only `MEONG_PAYMENT_MODE=qris-mock` or `qris-sandbox` selects `QrisPhotoBoothApp`. The latter inherits the existing camera, retake, template composition, result, printing and Drive flow; it replaces payment admission/acknowledgement rather than rewriting those subsystems.

`QrisKioskClient` -> strict authenticated `qris_api` -> `CheckoutBackend` -> `CheckoutStore` -> fixed `MidtransSandboxClient`. Merchant keys stay in the backend. The explicit local mock uses `MockQrisProvider` and never contacts Midtrans. Client and server modes must match; an actual Sandbox kiosk cannot accept a mock backend response.

A visit key/cart is persisted before network creation. The backend freezes price and returns the same order for retries. Independently verified payment grants the same durable permit on repeated claim calls. The kiosk links that permit to one local transaction before starting camera work. Payment state and RESERVED/STARTED/COMPLETED service state are distinct. Lost responses and restart do not imply a second charge/session. Interrupted capture is held for operator recovery rather than automatic repeat printing.

Signed webhook fields are authenticated, then current provider status is independently fetched and checked against order, amount, IDR, QRIS, merchant, transaction reference and fraud status. Polling recovers missing webhooks. Expiry/rejection/cancellation/refunds and late success are explicit states. Transient/unapplied notifications get HTTP 503 and retained event status, not a false success acknowledgement. The HTTP boundary rejects coerced counts and duplicate JSON, limits streamed bodies, and runs blocking operations off the event loop.

The GUI displays the provider's QR image from the allowlisted Sandbox endpoint, not a QR encoding of its URL. The order is persisted before image download. Mock QR payloads explicitly say NOT QRIS. Payment detection and camera admission are automatic; normal ad/tutorial/template and capture/retake/result behavior are retained.

## Try it

```powershell
python -m pip install -r requirements.txt -r requirements-qris.txt
python tools/run_qris_mock.py
```

No merchant credentials or real payments are needed for this trial. Physical printing is disabled by default. Use `--allow-print` only for an intentional paper test. [Full Windows/Sandbox instructions, expected flow and recovery limits](QRIS_TRIAL.md).

## Evidence and remaining acceptance

Backend **124 PASS / 0 SKIP**; full Kivy **364 PASS / 2 optional native-model SKIP**; **87 existing + 6 QRIS renders**, zero errors and exact QR decode at two desktop sizes. [Verified acceptance record](qa/FEAT-020-acceptance-20261020.md), [test checklist](test_checklist.md), [commit history](CHANGELOG.md).

Actual Midtrans merchant Sandbox compatibility, Windows camera/audio/phone/printer acceptance, public ingress/monitoring/secret rotation and an operator partial-session recovery/refund procedure remain separate gates. The new remote QRIS page currently supports onscreen QR only; existing DEMO QR-slip printing remains unchanged. There is no production endpoint or public mark-paid bypass.

## Historical prototype record

[Stages 1-11 preserved verbatim](FEAT-020-QRIS.pre-qris-20261020.md) describe the superseded isolated/manual prototype. Their old startup commands and statements that the main GUI is not connected are no longer current. Earlier isolated 5/6 PASS statements had insufficient execution evidence and must not be used as acceptance; the linked exact-SHA CI evidence above replaces them. The old `payment_ledger.py`, `payment_orders.py` and `checkout_service.py` remain isolated compatibility prototypes, not the current authoritative server path. A local `verified=True` value is never payment proof.
