# Meong Photobooth — Current architecture and future boundaries

> **CURRENT AS OF 2026-10-19 — POST-v1 SOURCE RELEASE:** Default branch is `master`; the immutable `v1.0.0` [pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0) points to commit `07ce51d2022ab5673a7a27e744e5e5757fbb3d08`. [Kiosk CI](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245): 235 tests (233 PASS, 2 SKIP), 87 synthetic renders/0 errors; [Dither CI](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273): 48 tests PASS. This is **source/CI evidence, not Windows production or hardware certification**. FEAT-001 DEMO pricing/copy count and FEAT-003 live-preview mirror have owner-tested PASS; BUG-011 monitored; BUG-001/007 speaker/audio retests pending; BUG-009 Drive 30-day cleanup remains OPEN. Real QRIS FEAT-020 and receipt scanner FEAT-002 are not implemented. Dated pre-release statements below are historical when superseded by this notice.

Last reconciled: **2026-10-19** | Branch: `master` | Tagged source snapshot: `v1.0.0`

This document describes **observed source modules**, not guaranteed on-device functionality. User-reported failures and acceptance status are tracked in [FEATURE_STATUS.md](FEATURE_STATUS.md) and [bug_tracker.md](bug_tracker.md). Future requirements are in [next_step.md](next_step.md).

## Existing application modules (in released source on `master`)

| Responsibility | Main files | Current boundary |
| --- | --- | --- |
| Entry, orchestration, ordering and capture transitions | `main.py`, `photobooth/app.py`, `photobooth/workflow.py` | **FEAT-001 in source:** each nonzero template makes one 3-photo capture session; picker quantity means identical paper copies. `quote_order` computes base-per-template and per-copy fees, DEMO only. |
| Kivy pages, tutorial, capture controls, template carousel and animations | `photobooth/ui_kivy.py`, `ui_kiosk.py`, `ui_brand.py`, `ui_motion.py` | GUI source present; **full synthetic GUI regression 87/87 PASS**, independent Windows end-to-end hardware/screensize acceptance still separate. |
| Local advertising playlist, face invitation and event counters | `photobooth/advertising.py`, `face_presence.py` | Bundled configuration plus local `ad_video/` files; no live central ad-entitlement enforcement. Camera presence is not identity recognition. |
| Sound/music and video audio ownership | `photobooth/audio.py`, `ui_kiosk.py` | Playback exists in source; device reports audio/Settings control failures. Payment advertising is intended to remain muted. |
| Camera, optional palm shutter and photo composition; **FEAT-003 live GPU mirror** | `photobooth/camera.py`, `palm_gesture.py`, `face_presence.py`, `app.py`, `ui_kivy.py`, `catalog.py` | The camera mailbox and `app.current_frame` retain original BGR pixels for face/palm inference and captured JPEGs. **Only the Kivy capture-page preview flips horizontal texture UVs**, for both first Pillow upload and streaming BGR, through `_new_display_texture(..., mirrored=True)`. Static saved-photo review, printed strips, image QR/text and detector inputs remain **unmirrored**. Present code has no FEAT-002 receipt scanner or coordinate bounding-box overlay; when implemented, any scanner must reuse this live display policy and mirror overlay coordinates, without reflecting decode inputs. **Owner tested the current Windows capture mirror and reported PASS (2026-10-18).** Dedicated synthetic GPU CI also passed; no claim of full kiosk regression or future scanner acceptance. |
| Demo payment and onscreen QR | `photobooth/payment.py`, `ui_kiosk.py`, `qr_code.py` | Only demo payment; no verified financial transactions or real merchant QRIS integration. Folder-access QR is separate. |
| Photo **and payment QR** thermal printing | `photobooth/printer.py`, `printer_settings.py`, `qris_print.py`, `app.py` | **Both separate routes exist in `feature/kivy-gui`.** Photo print supports LAN/Wi-Fi/Windows USB and Floyd–Steinberg/Bayer/threshold. FEAT-001/BUG-011 sends N repeated image+cut ESC/POS streams as **one RAW transport job**. Windows job finalization uses `StartDocPrinter → StartPagePrinter → WritePrinter → EndPagePrinter → EndDocPrinter → ClosePrinter`. **Owner reports physical copy count now correct** after this fix, while targeted 15/15 mock CI passes. Exact local Windows SHA/per-case paper-count matrix still absent; **full Kiosk CI now PASS** at `c40f33f5`, but sender success alone cannot count physical sheets. Payment QR-slip and folder QR are separate, and checkout QRIS is DEMO. |
| Local transaction IDs, manifests, capture files, optional Drive pool and sync | `photobooth/transaction_store.py`, `drive_pool.py`, `drive_storage.py`, `drive_sync.py`, `retention.py` | Durable capture/manifest operations exist, but a robust payment-state/print recovery ledger (FEAT-007) is **not** implemented. |
| Existing test helpers and historical QA | `tests/`, `tools/`, `docs/qa/` | Mocked tests and screenshot renders do not constitute live printer, sound, camera or payment acceptance. |

The historical `feature/thermal-printer` branch remains preserved; it is **not** the only location of thermal photo printing anymore. Do not change or delete that branch during GUI work.

## Actual workflow vs planned commercial workflow

**Current source (demo):** local idle ads → manual Start or face invitation → illustrated tutorial → cyclic template/session picker → **simulated payment** → sessions of 3 captures + retake/review → composed photo results with print path → idle ads. Verify transitions physically. The on-screen payment QR is **not payable**.

**FEAT-001 implemented / owner-reported operational PASS:** each selected frame has one 3-capture session and N identical paper copies at Rp5.000 base + Rp5.000 per requested sheet. `transaction_store` records `print_copies` and `demo_order_pricing`. `app.py` sends **one serialized RAW print batch** for each completed layout; `printer.py` renders once, repeats the image+cut stream N times, and closes Windows spool documents correctly. The owner confirmed pricing and physical counts after BUG-011 fixes. **This is not a machine-generated physical print counter:** the user must wait for the printer to finish, and a partial/uncertain batch must never be automatically resent. One manual retry could duplicate already-printed paper. No robust paid-reprint ledger exists (FEAT-007/016 deferred), full Kiosk GUI CI **is now PASS**; device-level release acceptance remains pending, and checkout stays DEMO. See [FEAT-001/BUG-011 acceptance evidence](qa/FEAT-001-BUG-011-acceptance.md).

**Future FEAT-002 / FEAT-005:** dummy food receipt scanning or local dummy ordering-to-photo discount in one machine; real partner ordering delegates to merchant-supplied, safe customer-facing web ordering. Real receipt/POS verification is deferred until an actual partner provides its format and APIs. Treat demo food payment as simulated and never infer genuine eligibility from decoded receipt text alone.

## Advertising architecture: current vs proposed

- **Current:** `photobooth/assets/ads/playlist.json`, optional `PHOTOBOOTH_AD_CONFIG` and automatic local `ad_video/` media; playback events are locally reportable. Merchant-configured ad playlist is not a centrally authorized subscription/slot service.
- **Required future business rules:** sold devices have assigned Free/Business/Enterprise tiers; Free is fully commercially usable but **100% Meong-managed ad content**; Business/Enterprise can schedule their own ads but Meong retains reserved placements of **TBD percentage**. Per-machine local-first Drive sync (FEAT-004), remote configuration (FEAT-010), licensing/entitlements (FEAT-019), fleet controls (FEAT-018) and reporting (FEAT-013) are related proposals, not present enforcement.
- **Design concerns:** Operators with administrative access to their purchased Windows mini PC can modify local configuration/media. A local playlist is not tamper-proof or sufficient to guarantee Meong ad impressions. Commercial conditions, signed bundles and contractual/venue permissions must be investigated; avoid claiming technical enforcement or advertising revenue until verified.
- **Safety:** Keep ads offline-playable, atomically update local media, fail back without interrupting photo/payment/print, isolate partner campaign content and honor competitor/exclusivity restrictions.

## Printing architecture: routes and separate acceptance

- **Photo layout:** `ThermalPrinter` renders to native ESC/POS raster, applies configured dither (Floyd–Steinberg/Bayer/threshold), then routes via configured LAN, Wi-Fi or Windows USB/spooler. The owner reports actual paper output, **and the owner subsequently reported Floyd print quality PASS** (BUG-004; detailed paper-quality matrix not archived).
- **QR slip:** `QrisPrinterWorker` renders crisp QR pixels with quiet zone, uses GUI-provided saved `PrinterConfig` when present and legacy `PHOTOBOOTH_PRINTER_HOST` only for standalone/fallback usage. **Owner later reported QR-slip paper printing PASS** (BUG-003); spooler/send acknowledgement alone cannot prove physical output or phone scannability.
- **Printing safety:** Do not automatically resend jobs after an uncertain partial transfer, and do not treat a QR-slip job as payment confirmation.

See [advertising-and-qris.md](advertising-and-qris.md) for detailed existing flow, with present/legacy transport distinctions, and [test_checklist.md](test_checklist.md) for physical QA.

## Retention and actual durability

Existing `transaction_store.py` is a photo/session manifest and counter—not the future crash-safe payment → capture → print lifecycle required by FEAT-007. Local photo bytes are currently eligible for expiry after 15 days even if remote upload was unsuccessful; Drive target expiry is 30 days if the related services are correctly configured. Do not advertise unconditional durable digital delivery without a separately proven policy.

## Development controls and run commands

```bash
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
```

Run commands on appropriate operating systems with real dependencies; record passes, failures, skipped tests and actual device results. No code modification is authorized by documentation housekeeping. The [development protocol](DEVELOPMENT_PROTOCOL.md) controls implementation and release approval.

**Cross-references:** [Feature status](FEATURE_STATUS.md) · [Decisions](DECISIONS.md) · [Bug tracker](bug_tracker.md) · [Development handover](DEVELOPMENT_HANDOVER.md).

## FEAT-021 — branch-scoped background processing experiment (2026-10-21)

The owner authorized starting this work on `feature/ai-background-studio`, not a merge or release. Offline processing backend, review-page Original/Clean Studio controls, asynchronous controller integration and optional composition are now in source. The normal printer/dithering/Drive QR path and camera capture remain unchanged. AI requires a model seeded locally in advance; without it, the existing Original path remains the only working customer route. Hardware/model benchmarks and end-to-end GUI validation remain pending. See [FEAT-021 backlog](next_step.md#feat-021--offline-ai-background-studio-2026-10-21).

### FEAT-021 stage-two integration and test distinction — 2026-10-21

- **New source:** `photobooth/ui_kivy.py` review buttons for Original / Clean Studio (AI only enabled if offline cache is detected); `photobooth/app.py` asynchronous post-capture image segmentation with stale-session rejection and Original fallback; `photobooth/catalog.py` composition accepts exactly three in-memory processed images while raw photo references and camera frames stay untouched; `photobooth/transaction_store.py` records the chosen `background_style` as additive manifest metadata.
- **No model bundled:** operator must install optional requirements and pre-seed the model before boot. There is no online AI service; runtime no-download mode is enforced by the precheck of model cache. Quality and runtime speed with true ONNX weights require a Windows booth trial.
- **Synthetic backend CI evidence:** [FEAT-021 run 39506455123](https://github.com/pratikto/PhotoBooth/actions/runs/39506455123) PASS at `b43c1307`, Pillow-only fixture tests (not full GUI). [Draft PR #9](https://github.com/pratikto/PhotoBooth/pull/9) starts Kivy regression; check the latest PR SHA for its final status. No physical thermal, camera, model, Google Drive or privacy-retention verification is claimed.
- **Rollback:** revert FEAT-021 commits only. Branch stays separate; do not merge to `master` without owner approval.
