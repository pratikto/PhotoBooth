# Meong Photobooth - Test checklist and evidence

## Owner-reported MOCK trial - 2026-10-20

**FEAT-020: OWNER-REPORTED PASS for the discussed main-GUI MOCK flow.** After the explanation that the MOCK trial simulates payment without scanning or transferring money, the owner reported: "udah bisa berjalan dengan lancar" (already running smoothly).

This is a general owner observation about the discussed MOCK trial, not a new automated test or a claim of real Midtrans payment. The exact locally tested commit SHA, launch command, OS/device configuration, scenario/copy counts, logs and individual camera/audio/printer/Drive checks were not supplied. The repository head when this feedback was recorded was `40b2fe47547512a32b6acaf4dae9b04f95ae02fe`; do not treat that as the confirmed local test SHA. No physical-print, provider QR scan, failure-recovery or real merchant acceptance is inferred from this report.

Scope of this update: record field feedback under the existing FEAT-020 development/documentation authorization; documentation only. No code, test execution, deployment, release, production payment or merge approval is implied. The detailed operator/provider gates below remain open until separately evidenced. The next provider acceptance stage remains the actual Midtrans Sandbox trial described in [QRIS_TRIAL.md](QRIS_TRIAL.md).

## Current FEAT-020 gate - 2026-10-20

**Tested source:** `7cf90ea95a32b4cf2feee16c21232069bc1aa9bb`, `feature/qris-payment`. Documentation-only changes after this SHA do not constitute a new hardware test.

| Gate | Result | Reproduction / evidence |
| --- | --- | --- |
| Mandatory backend, Ubuntu/Python 3.11 | **124 PASS, 0 FAIL, 0 SKIP** | `python tools/run_qris_tests.py`; [CI 39367707122](https://github.com/pratikto/PhotoBooth/actions/runs/39367707122), artifact 12239653567 |
| Local backend, Linux/Python 3.13.5 | **124 PASS, 0 FAIL, 0 SKIP** | Same runner; local source matched CI tracked-source artifact byte-for-byte |
| Full Kivy regression, Ubuntu/Python 3.12 | **366 run: 364 PASS, 2 SKIP, 0 FAIL/ERROR** | `xvfb-run -a python tools/run_kiosk_unittests.py`; [CI 39367707169](https://github.com/pratikto/PhotoBooth/actions/runs/39367707169), artifact 12239988498 |
| Existing synthetic screens | **87 renders, 0 errors** | `tools/render_gui.py`; same GUI artifact |
| Main QRIS screens | **6 renders, 0 errors; 2 exact screenshot QR decodes** | `tools/render_qris_gui.py`; WAITING/CANCELLING/RECOVERY at 1200x800 and 800x600 |
| Real loopback HTTP process | **PASS** | Uvicorn factory -> authenticated create -> automatic claim -> replay -> STARTED -> COMPLETED with persistent kiosk journal |

The two full-suite skips are optional native-model inference tests. No required backend/QRIS test is skipped. Backend tests are also included in the full suite, so these counts overlap. The initial unattached-widget QRIS screenshots were rejected and are not accepted evidence; the dedicated running-host renderer replaced them.

### Failure paths actually exercised

Immutable cart/key retry, lost create/claim responses, restart and cross-process journal ownership, 64 concurrent grant calls, two SQLite connections, absent webhook recovery, provider outages, wrong order/amount/currency/method/merchant/reference/fraud status, delayed/duplicate callbacks, expiry/rejection/cancellation and late success, strict bool/string/float rejection, chunked-body early stop, event-loop responsiveness, QR redirect/origin/size/dimension rejection, camera readiness loss, stale DEMO callback denial and storage failure hold.

The main-GUI test captures two templates with their requested copy counts, performs a retake, writes result images and completes the transaction without a manual payment-confirmation click. Fake devices and mock provider data are used; no real printer or bank is contacted.

### Mandatory operator/production gates still open

- [ ] Actual Windows screen/camera/audio/printer acceptance, with exact branch SHA and device configuration.
- [ ] Actual Midtrans Sandbox merchant creation, simulator payment, status polling and public HTTPS webhook acceptance; credentials stay server-side.
- [ ] Provider QR phone scan and remote payment-QR paper-slip implementation/acceptance.
- [ ] Operator recovery/refund procedure for interrupted paid capture or ambiguous provider creation; never auto-resend uncertain paper.
- [ ] Public ingress limits, HTTPS, monitoring/backups, credential rotation and explicit production/release approval.
- [ ] Existing audio BUG-001/007 and Drive retention BUG-009 resolved or explicitly risk-accepted independently.

Complete previous release, field and historical test evidence is preserved verbatim in [the pre-QRIS checklist](test_checklist.pre-qris-20261020.md). Existing owner observations are not changed or upgraded by this work. [Trial runbook](QRIS_TRIAL.md) / [acceptance record](qa/FEAT-020-acceptance-20261020.md).
