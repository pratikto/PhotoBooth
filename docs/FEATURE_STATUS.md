# Meong Photobooth - Current feature status

## Current feature branch: FEAT-020, 2026-10-20

**`feature/qris-payment`: automatic main-GUI mock trial is implemented and verified in synthetic CI. Not production-ready, not merged.** Tested source: `7cf90ea95a32b4cf2feee16c21232069bc1aa9bb`. Default `master` / immutable `v1.0.0` remain separate stable baselines; this feature does not rewrite that release.

| Capability | Current evidence and limit |
| --- | --- |
| Main Kivy checkout -> automatic payment detection -> photo session | Implemented through `app_qris.py`, `ui_qris.py`, durable kiosk journal and authenticated backend. Real-widget tests cover automatic single admission and the existing two-template capture/retake/result/completion path. |
| Order/claim retry and restart | Same checkout key/order/grant replay; no blind duplicate charge. Interrupted capture is held for operator recovery, not automatically recaptured or reprinted. |
| Provider verification and lifecycle | Signed notifications plus independently fetched order/amount/IDR/QRIS/merchant/transaction checks; missed webhook recovery, expiry, cancellation, rejection and late-payment isolation. Actual merchant Sandbox responses still need owner acceptance. |
| Mock GUI trial | `python tools/run_qris_mock.py`: loopback-only backend, no merchant key, explicitly non-payable QR, automatic simulation after eight seconds. Physical print disabled unless `--allow-print`. |
| Midtrans Sandbox mode | Wired to the same main GUI; requires backend-only Sandbox credentials and merchant ID. No production endpoint or live payment enablement. |
| Existing DEMO, camera, templates, retake, photo printing, ads and Drive QR | Original `app.py`, core Kivy UI, printer, catalog and Drive modules retained. Full synthetic regression remains green. This does not certify physical devices or resolve existing retention/audio defects. |
| Payment QR paper slip | Existing DEMO slip remains; the new remote QRIS page currently displays the provider QR onscreen only. Provider-image slip printing remains pending. |

**Verified:** backend [39367707122](https://github.com/pratikto/PhotoBooth/actions/runs/39367707122) **124 PASS / 0 SKIP**; full GUI [39367707169](https://github.com/pratikto/PhotoBooth/actions/runs/39367707169) **364 PASS / 2 SKIP / 0 failures**, **87 existing renders + 6 QRIS renders**, two exact screenshot-QR decodes. The two skips are optional native-model tests, not QRIS tests. [Evidence and acceptance](qa/FEAT-020-acceptance-20261020.md).

## Unchanged field status and scope boundaries

Earlier owner-reported template pricing/copy count, mirrored preview, Floyd printing, QR-slip paper and ad/navigation observations remain unchanged; no new physical PASS is inferred. BUG-001/007 audio and BUG-009 Drive retention remain unresolved; BUG-011 and other monitored items are not closed by this work. Other branches, including device health, are untouched and their separate approvals/status are not overridden.

The complete previous source/owner-report matrix and chronological evidence are preserved verbatim in [the pre-QRIS status archive](FEATURE_STATUS.pre-qris-20261020.md). That file describes its dated baseline; its statements that FEAT-020 is deferred/unimplemented are superseded only for this approved feature branch. [Bug register](bug_tracker.md) remains authoritative for defects.

Start with [QRIS trial instructions](QRIS_TRIAL.md), [current architecture/status](FEAT-020-QRIS.md), [handover](DEVELOPMENT_HANDOVER.md) and [test checklist](test_checklist.md). No merge/release without explicit owner approval.
