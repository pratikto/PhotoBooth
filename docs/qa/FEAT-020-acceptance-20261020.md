# FEAT-020 - Verified main-GUI trial acceptance, 2026-10-20

## Source and scope

Tested source commit **7cf90ea95a32b4cf2feee16c21232069bc1aa9bb**, branch **feature/qris-payment**. Owner approved staged audit remediation through main-GUI trial readiness. No master merge, production payment activation, release or public deployment occurred. Documentation-only closure preserves the tested application/test/workflow source.

## Downloaded and inspected evidence

| Gate | Environment | Exact result / evidence |
| --- | --- | --- |
| Mandatory backend | GitHub Ubuntu, Python 3.11 | **124 PASS, 0 FAIL, 0 SKIP**; [run 39367707122](https://github.com/pratikto/PhotoBooth/actions/runs/39367707122), artifact **12239653567** |
| Same backend locally | Linux, Python 3.13.5 | **124 PASS, 0 FAIL, 0 SKIP**; `python tools/run_qris_tests.py` |
| Complete Kivy unittest suite | GitHub Ubuntu/Xvfb, Python 3.12 | **366 run: 364 PASS, 2 SKIP, 0 FAIL/ERROR**; [run 39367707169](https://github.com/pratikto/PhotoBooth/actions/runs/39367707169), artifact **12239988498** |
| Existing UI regression | Same GUI run | **87 renders, 0 errors** |
| Main QRIS visual gate | Same GUI run | **6 renders, 0 errors**, WAITING/CANCELLING/RECOVERY at 1200x800 and 800x600; **two exact non-payable QR payload decodes from screenshot pixels** |
| Real local HTTP smoke | Linux, Python 3.13.5, Uvicorn socket | Authenticated creation, automatic permit, repeated permit, STARTED and COMPLETED all PASS with persisted journal; not TestClient |

The mandatory backend suite is also in full unittest discovery; counts overlap. The two skips are optional native-model asset/inference tests, not skipped QRIS tests. No physical devices, customer files or actual payment accounts were exercised. GUI data/provider/camera/printer are fixtures.

The final backend artifact includes the exact tracked-source ZIP; each tracked file was compared byte-for-byte with the locally tested working copy: **zero mismatches**. CI also preserves Python/dependency versions and the full report. GUI artifact reports were downloaded, and WAITING at both desktop sizes plus RECOVERY at 800x600 were visually inspected. QR, mode/price, payment status and action row are visible; the small screen intentionally scrolls supporting details. The original unattached-widget screenshots from 95011d1 were rejected and are not accepted visual evidence.

## Audit findings addressed

CI now executes every mandatory backend suite and rejects silent skips. Persistent visit keys/grants prevent duplicate creation and lost-response admission loss. Polling recovers missing webhooks. Full provider identity/amount/method/currency/merchant/fraud checks precede admission. Terminal/late statuses remain tied to the original visit. Webhook failures receive retryable failure rather than false success. Strict JSON/type boundaries, early streamed limits, off-thread service work, authenticated booth isolation and no-redirect/bounded image handling have negative tests. Main GUI payment detection and photo admission are automatic; existing two-template capture/retake/result completion was actually exercised.

## Remaining operational acceptance, not hidden completion claims

Actual Midtrans Sandbox merchant response compatibility, simulator/phone/webhook tests, physical Windows camera/speaker/printer behavior, provider payment-QR slip printing, ingress/monitoring/backup/token rotation and a supported operator recovery/refund procedure remain gates. An ambiguous CREATED order is conservatively held, and a reboot during partial capture is RECOVERY rather than automatic replay. No claim of live or unattended commercial readiness is made.

[Run the owner trial](../QRIS_TRIAL.md). Existing audio/retention defects and other branch work remain unchanged. Merge/release requires explicit owner approval.
