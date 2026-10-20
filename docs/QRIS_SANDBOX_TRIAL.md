# FEAT-020 - Actual merchant Sandbox trial

Status: **PREPARED, NOT MERCHANT-VERIFIED** (2026-10-20). This is the next stage after the owner's smooth MOCK trial. Branch `feature/qris-payment`; base `cbc9c5cfb4085d64057bc5777f1e47cd8f48b612`. No merge, production enablement, public deployment, or financial transfer is authorized by this trial.

## Local launcher

Use your existing Windows Kivy virtual environment, from the repository root:

```powershell
python -m pip install -r requirements.txt -r requirements-qris.txt
python tools/run_qris_sandbox.py
```

The launcher prompts locally for **Sandbox Merchant ID** and a hidden **Sandbox Server Key**. It can also read those two named environment variables. Do not put credentials in chat, screenshots, command-line arguments, Git or the trial report. Unsupported hidden-input terminals fail closed. A key must have the Sandbox `SB-Mid-server-` prefix; this guards against an operator mix-up, but does not prove Midtrans accepts it.

The launcher starts the existing server factory bound only to `127.0.0.1:8000`, generates an ephemeral booth token, and then opens the main GUI in `qris-sandbox` mode. Merchant credentials are passed only to the backend child; all `MIDTRANS_*` variables are removed from the GUI child. Inherited MOCK mode/timers are discarded. There is **no automatic eight-second settlement** and no call to pay the simulator on your behalf.

Default booth: existing `PHOTOBOOTH_ID` or `PB001`. Optional `--booth-id PB001` and `--port 8000`. An occupied port is refused. Keep the same port/merchant/booth for retries: the journal binds the endpoint. Persistent state is separate from MOCK and stored under `data/qris-sandbox-trial/<merchant>/<booth>/`. Nothing is deleted on exit. Never change profiles or delete a journal to bypass an unresolved payment.

**Printing differs from the no-print MOCK launcher:** normal photo/printer settings are retained. Completing a photo session can use paper. Existing local-storage fallback is enabled; existing Drive configuration is not replaced. New provider-QR paper slips remain unimplemented.

## Merchant setup and payment simulator

1. Open the Midtrans **Sandbox** dashboard and use **Settings > Access Keys**. Use the Merchant ID and **Server Key**, not Client Key and not Production credentials. Sandbox registration/testing does not itself certify production activation.
2. Start the launcher and select a template/copy count in the main GUI. Confirm the page explicitly says **MIDTRANS SANDBOX / UJI COBA**.
3. When a fresh pending order is written to the kiosk journal, the launcher prints the current **QR image URL** and order ID in the local terminal. The helper shows only official Sandbox URLs from a current Sandbox visit; it does not authorize payment or capture.
4. Open the official QRIS simulator: `https://simulator.sandbox.midtrans.com/v2/qris/index`. Paste the **QR image URL**, not the order ID or a screenshot file, into **QR Code Image Url**. Use Scan QR and finish the simulator's payment flow. Confirm its amount matches the GUI.
5. Check the transaction in the Sandbox dashboard and confirm the GUI detects settlement automatically, receives one stable grant, and opens the existing camera flow. Before completing simulator payment, the GUI must remain waiting even after eight seconds.

**Never pay a Sandbox QR using a real banking/wallet application or expose it to customers.** Use only Midtrans's test simulator. Do not weaken signature, merchant, amount or currency validation to get a test through.

The first local trial exercises **provider polling**. Midtrans cannot reach loopback for callbacks. Public webhook delivery is a separate acceptance test requiring an owner-approved HTTPS endpoint and ingress controls; no tunnel/server is deployed by this launcher. A health response means the local backend is running, not that credentials or merchant QRIS capability were verified.

## Report and acceptance checklist

Record tested Git SHA, Python/OS, order ID, expected amount, Sandbox dashboard status, observed GUI transition, and success/failure of each scenario. Return redacted error text or screenshots with all access keys and tokens hidden; do not share full environment dumps. Order/QR references are test metadata, not public sharing links.

- [ ] Real merchant credentials accepted and pending QR returned by Midtrans.
- [ ] No admission before simulator payment.
- [ ] Simulator amount matches the server-calculated price.
- [ ] Provider settlement is detected without manual confirmation in the GUI.
- [ ] A retry/restart before capture preserves the order and grant.
- [ ] A second payment or new session is not created for the same visit.
- [ ] Cancel/expire/deny leave no unauthorized photo session.
- [ ] Interrupted capture is handled via documented operator recovery, not automatic duplicate capture/print.
- [ ] Public HTTPS webhook delivery independently verified.
- [ ] Physical Windows camera/printer/phone-scan acceptance separately recorded.

None of these merchant/hardware boxes is checked by offline tests.

## Preparation evidence (not merchant acceptance)

The existing application source was extracted from the previously downloaded, exact-source CI artifact for `7cf90ea95a32b4cf2feee16c21232069bc1aa9bb`. Live GitHub comparison confirmed that `cbc9c5c` differs only in documentation. Before launcher changes, `python tools/run_qris_tests.py` ran **124 PASS, 0 FAIL, 0 SKIP** locally. The launcher adds **20 offline tests**, including child-environment separation, key/mode rejection, persistent profile paths, bounded journal reading, trusted/current QR selection and process cleanup. The mandatory runner now includes them: **144 PASS, 0 FAIL, 0 SKIP**, Linux/Python 3.13.5 (FastAPI 0.128.2, Pydantic 2.13.5, HTTPX 0.28.1, Requests 2.32.5).

Commands:

```text
python -m unittest discover -s tests -p test_qris_sandbox_launcher.py -v
python tools/run_qris_tests.py
python -m py_compile tools/run_qris_sandbox.py tests/test_qris_sandbox_launcher.py
python tools/run_qris_sandbox.py --help
```

The current execution environment has no configured `MIDTRANS_SERVER_KEY` or `MIDTRANS_MERCHANT_ID`; no actual Midtrans transaction was made. Kivy/Windows GUI was not launched here. New tests use process/HTTP fixtures; they do not prove external provider access. GitHub CI for the new commit must be inspected separately. Existing MOCK acceptance remains unchanged.

Rollback: revert this scoped launcher/test/runbook change on the feature branch. Do not reset `master`, alter `v1.0.0`, or delete runtime payment state.

## Official references checked 2026-10-20

- https://docs.midtrans.com/docs/api-authorization-headers (Sandbox Access Keys and credential confidentiality)
- https://docs.midtrans.com/docs/testing-payment-on-sandbox (QR image URL simulator flow and no-real-payment warning)
- https://simulator.sandbox.midtrans.com/v2/qris/index (current simulator linked by the testing guide)

[Main trial and recovery guide](QRIS_TRIAL.md)
