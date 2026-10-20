# Meong Photobooth - Development handover

## Current handover - FEAT-020 audit remediation, 2026-10-20

Repository `pratikto/PhotoBooth`; working branch **`feature/qris-payment` only**. Tested code checkpoint: **`7cf90ea95a32b4cf2feee16c21232069bc1aa9bb`**. The following documentation-only consolidation preserves the code at that checkpoint. `master`, `feature/device-health`, the thermal branch and `v1.0.0` have not been changed by this work.

**Owner authorization:** execute the audit recommendations through a main-GUI trial, using small sequential tested pushes. Do not repeatedly ask to continue within this scope. **Merge to master, release, production QRIS, merchant account actions, cloud deletion and public deployment remain unauthorized.**

### Delivered

The main Kivy application has explicit qris-mock and qris-sandbox modes. Backend reconciliation, immutable visit keys, persistent service grants, strict HTTP input, bounded streaming, nonblocking provider calls and a persistent kiosk journal address the audit's primary failure cases. The previous separate manual preview now forwards to the main GUI. Default DEMO operation remains unchanged.

The actual accepted camera/retake/composition/print/Drive controller is inherited, not replaced. A grant is persisted before capture admission; the local transaction is acknowledged before the first session starts. Completion is acknowledged before a new visit. A partial-capture reboot is held for operator recovery rather than silently allocating another session or resending paper.

### Verified results

- Backend run [39367707122](https://github.com/pratikto/PhotoBooth/actions/runs/39367707122): **124 PASS / 0 FAIL / 0 SKIP**.
- Full GUI run [39367707169](https://github.com/pratikto/PhotoBooth/actions/runs/39367707169): **364 PASS / 2 optional native-model SKIP / 0 FAIL/ERROR**; seven QRIS GUI tests pass.
- **87 existing + 6 QRIS renders**, zero errors; exact QR payload decoded from screenshots at 1200x800 and 800x600. Actual screenshots were visually inspected. Small screens intentionally permit panel scrolling while the payment QR/status and action row stay accessible.
- Actual loopback Uvicorn HTTP smoke passed create, automatic grant, grant replay, STARTED and COMPLETED; no Midtrans call or real money.

See [acceptance ledger](qa/FEAT-020-acceptance-20261020.md) for tested SHA, environments, artifact IDs and limits. Full-suite totals include backend tests; do not add them as independent coverage counts.

### Next safe action

Run `python tools/run_qris_mock.py` in the owner's existing virtual environment after installing `requirements.txt` and `requirements-qris.txt`. This opens the real main GUI and local authenticated backend. No physical printing by default; `--allow-print` is explicit paper consent. [Detailed commands and recovery boundaries](QRIS_TRIAL.md).

Then record actual Windows camera, audio, printer, phone scanning and complete-session results on the tested branch. Actual Midtrans Sandbox requires owner-configured server-only credentials/merchant ID and approved HTTPS webhook ingress. Never ask for secrets in chat or commit them. No claim of merchant compatibility, physical fulfillment or production readiness is made from mock results.

Open limits: public ingress/monitoring/token rotation, a supported operator partial-session recovery/refund procedure, actual merchant Sandbox acceptance and the remote payment-QR paper-slip path. A CREATED request whose provider creation remains unknown stays held for investigation; do not delete databases/journals to bypass it. Existing BUG-001/007 and BUG-009 remain open.

### History and rollback

Earlier handover narratives are preserved verbatim in [the dated pre-QRIS archive](DEVELOPMENT_HANDOVER.pre-qris-20261020.md), not silently deleted. Do not use their historical QRIS deferral as the current approved scope. Other feature details/approvals remain unchanged. Rollback uses scoped feature-branch reverts or default DEMO mode on a development profile; never hard-reset master, rewrite v1.0.0, or erase uncertain paid records. [Changelog](CHANGELOG.md).
