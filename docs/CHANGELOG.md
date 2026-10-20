# Meong Photobooth - Actual change history

## Unreleased - FEAT-020 audit remediation, 2026-10-20

Branch `feature/qris-payment`; **no master merge, release or production payments**. Owner approved audit fixes and a main-GUI trial. Each logical step was committed/pushed sequentially with associated tests and documentation.

| Commit | Actual change |
| --- | --- |
| `9fd1fba7ee5d6acbb502db57a5fc1249e60f1ba7` | Restore explicit mandatory backend suites, missing requests dependency, no-skip gate and reproducible CI artifacts. |
| `4444f34d9cbedf03b47eec7db5379f09eedda5dc` | Durable immutable visits, replayable service grants, separate fulfillment state, late-payment isolation and conservative legacy migration. |
| `612171dc77ee3f6bd14294bdffa2b139cfe21307` | Missing-webhook status reconciliation, strict provider evidence and retry-safe event handling. |
| `7a78b8f989b043986f8ea2dfbac2c868ba5bc22c` | Authenticated strict HTTP v2, streamed input limits, off-thread service work, recoverable kiosk contract and Sandbox-only server factory. |
| `91b4bd6e6c43d9cf24900496bb2452a971123dc7` | Persistent kiosk journal/process lease, capture admission and completion acknowledgement, explicit non-payable mock provider. |
| `95011d1a536fdf429354bb22c5cbfdf2fb60bf42` | Automatic QRIS admission in the main Kivy GUI, inherited existing photo workflow, trial launcher and opt-in physical printing. |
| `7cf90ea95a32b4cf2feee16c21232069bc1aa9bb` | Provider status-code edge cases, bounded QR image tests and a running-host visual QR gate. |

Final source evidence: backend **124 PASS / 0 SKIP**; full Kivy **364 PASS / 2 SKIP**, **87 existing + 6 QRIS renders**, two exact screenshot QR decodes. See [test checklist](test_checklist.md) and [acceptance](qa/FEAT-020-acceptance-20261020.md). No real merchant/hardware acceptance is implied.

The documentation-only closure after the tested source records current status, run commands, approvals, backlog scope and test limits. Previous canonical narratives are retained verbatim as dated `*.pre-qris-20261020.md` files beside the current documents, preserving their relative links and historical evidence. Source tests are not rerun merely by calling documentation changes a release.

## Earlier releases and changes

[Complete pre-QRIS changelog](CHANGELOG.pre-qris-20261020.md) preserves v1.0.0, the old master backup, printer/mirror/audio and prior GUI work. `v1.0.0` remains immutable; existing operational bugs are not closed by this feature.
