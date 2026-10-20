# MEONG main-GUI QRIS trial

**Scope:** `feature/qris-payment`, explicit mock or Midtrans Sandbox. No production payments, release or master merge. The default `python main.py` still runs the existing DEMO application unless `MEONG_PAYMENT_MODE` is set. The former separate manual preview is replaced by this main-GUI flow.

## Quick trial without merchant credentials

In the existing Windows virtual environment, from the repository root:

```powershell
python -m pip install -r requirements.txt -r requirements-qris.txt
python tools/run_qris_mock.py
```

This starts an authenticated backend bound only to 127.0.0.1 and the main MEONG GUI. Choose a template/copy count normally. The payment page is explicitly **MOCK / NOT FOR TRANSFER**; after eight seconds the mock provider simulates payment. Status polling and a durable service permit then admit the existing camera flow automatically. No manual payment-confirmation button is needed. The camera must be connected, and the selected photo/retake/result flow stays the existing application flow.

**Default mock printing is disabled**, so trying checkout does not consume paper. To explicitly test the saved physical printer configuration:

```powershell
python tools/run_qris_mock.py --allow-print
```

The launcher does not erase photos, journals or Drive settings. It allows local storage when no Drive slot is ready; an existing configured Drive integration is not replaced. Use a development machine/profile rather than a customer deployment. The launcher clears merchant-key variables for its mock child processes and generates an ephemeral booth token without logging it. Closing the GUI stops its local backend.

Other test scenarios: `--scenario expire`, `--scenario deny`, `--scenario pending`. An active payment cannot be silently replaced by another visit. Finish or use the verified cancellation path before starting a new order. Never delete a journal/database to bypass a paid or uncertain transaction.

## Actual Midtrans Sandbox trial

Backend-only environment: `MIDTRANS_SERVER_KEY` (Sandbox), `MIDTRANS_MERCHANT_ID`, `MEONG_QRIS_BOOTH_ID`, `MEONG_QRIS_BOOTH_TOKEN` (random >=32 characters), and optionally `MEONG_QRIS_DB_PATH`. Keep secrets outside Git and chat. Start:

```powershell
python -m uvicorn photobooth.qris_server:build_sandbox_app --factory --host 127.0.0.1 --port 8000
```

Kiosk environment: `MEONG_PAYMENT_MODE=qris-sandbox`, `MEONG_QRIS_API_URL`, matching booth ID/token and `PHOTOBOOTH_ID`. For a same-machine loopback trial only, set `MEONG_QRIS_API_URL=http://127.0.0.1:8000` and `MEONG_QRIS_LOCAL_PREVIEW=1`, then `python main.py`. Remote endpoints require HTTPS. Never put the Midtrans server key on a separate kiosk.

Configure the Midtrans simulator/webhook to reach an approved HTTPS endpoint for full webhook testing. A loopback endpoint is not reachable by Midtrans. Provider status polling can recover missed callbacks, but the webhook path also needs independent acceptance. The payment QR image must come from the official Sandbox endpoint; it is not a locally invented payment code. Merchant compatibility and real Sandbox notification testing are not certified by offline mock tests.

## Recovery and limits

- `data/qris-mock-visit.json` (or the configured journal) binds booth, backend, mode, visit key, order and grant. Database and journal are persistent, not throwaway payment authority.
- A timeout preserves the same visit. Retrying does not blindly create a second charge. An ambiguous CREATED order stays held until verified or investigated.
- Restart before capture resumes the same checkout. Restart during partially started capture shows **operator recovery required**; it never starts a second session or resends uncertain paper. Operators must reconcile the stored order/grant/local manifest before fulfilment/refund decisions. There is no public bypass/mark-paid endpoint.
- A camera interruption before capture keeps the paid permit; restoring camera readiness allows admission. Printer success still means transport acknowledgement, not proof of correct physical output.
- QR Google Drive remains a separate result-delivery QR. Existing DEMO QR-slip printing is preserved. The new remote QRIS page currently supports onscreen provider QR only; provider-image QR-slip printing is not enabled in this test stage.
- Public production remains blocked on merchant acceptance, TLS/ingress controls, token rotation, operator recovery procedures, physical Windows/photo/QR/print acceptance and explicit owner approval. No production mode is provided.

## Automated checks

`python tools/run_qris_tests.py` runs every required backend test and fails any skip. The Kiosk GUI workflow on this feature branch also runs the full existing regression and the new QRIS controller tests, with fake hardware and no real provider. Evidence is in GitHub Actions artifacts. A green mock run is not live payment or hardware certification.
