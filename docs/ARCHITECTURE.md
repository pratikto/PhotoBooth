# Meong Photobooth — Current architecture and future boundaries

Last reconciled: **2026-10-18** | Branch: `feature/kivy-gui`

This document describes **observed source modules**, not guaranteed on-device functionality. User-reported failures and acceptance status are tracked in [FEATURE_STATUS.md](FEATURE_STATUS.md) and [bug_tracker.md](bug_tracker.md). Future requirements are in [next_step.md](next_step.md).

## Existing application modules (in this branch)

| Responsibility | Main files | Current boundary |
| --- | --- | --- |
| Entry, orchestration, ordering and capture transitions | `main.py`, `photobooth/app.py`, `photobooth/workflow.py` | **FEAT-001 in source:** each nonzero template makes one 3-photo capture session; picker quantity means identical paper copies. `quote_order` computes base-per-template and per-copy fees, DEMO only. |
| Kivy pages, tutorial, capture controls, template carousel and animations | `photobooth/ui_kivy.py`, `ui_kiosk.py`, `ui_brand.py`, `ui_motion.py` | GUI exists; complete physical-navigation/screen-size regression pending. |
| Local advertising playlist, face invitation and event counters | `photobooth/advertising.py`, `face_presence.py` | Bundled configuration plus local `ad_video/` files; no live central ad-entitlement enforcement. Camera presence is not identity recognition. |
| Sound/music and video audio ownership | `photobooth/audio.py`, `ui_kiosk.py` | Playback exists in source; device reports audio/Settings control failures. Payment advertising is intended to remain muted. |
| Camera, optional palm shutter and photo composition | `photobooth/camera.py`, `palm_gesture.py`, `catalog.py` | Existing captured/saved images must not be confused with future mirrored *preview-only* requirement. |
| Demo payment and onscreen QR | `photobooth/payment.py`, `ui_kiosk.py`, `qr_code.py` | Only demo payment; no verified financial transactions or real merchant QRIS integration. Folder-access QR is separate. |
| Photo **and payment QR** thermal printing | `photobooth/printer.py`, `printer_settings.py`, `qris_print.py`, `app.py` | **Both separate routes exist in `feature/kivy-gui`.** Photo print supports LAN/Wi-Fi/Windows USB and Floyd–Steinberg/Bayer/threshold. FEAT-001/BUG-011 sends N repeated image+cut ESC/POS streams as **one RAW transport job**. Windows job finalization uses `StartDocPrinter → StartPagePrinter → WritePrinter → EndPagePrinter → EndDocPrinter → ClosePrinter`. **Owner reports physical copy count now correct** after this fix, while targeted 15/15 mock CI passes. Exact local SHA/count matrix and full GUI CI PASS still absent; sender success alone cannot count physical sheets. Payment QR-slip and folder QR are separate, and checkout QRIS is DEMO. |
| Local transaction IDs, manifests, capture files, optional Drive pool and sync | `photobooth/transaction_store.py`, `drive_pool.py`, `drive_storage.py`, `drive_sync.py`, `retention.py` | Durable capture/manifest operations exist, but a robust payment-state/print recovery ledger (FEAT-007) is **not** implemented. |
| Existing test helpers and historical QA | `tests/`, `tools/`, `docs/qa/` | Mocked tests and screenshot renders do not constitute live printer, sound, camera or payment acceptance. |

The historical `feature/thermal-printer` branch remains preserved; it is **not** the only location of thermal photo printing anymore. Do not change or delete that branch during GUI work.

## Actual workflow vs planned commercial workflow

**Current source (demo):** local idle ads → manual Start or face invitation → illustrated tutorial → cyclic template/session picker → **simulated payment** → sessions of 3 captures + retake/review → composed photo results with print path → idle ads. Verify transitions physically. The on-screen payment QR is **not payable**.

**FEAT-001 implemented / owner-reported operational PASS:** each selected frame has one 3-capture session and N identical paper copies at Rp5.000 base + Rp5.000 per requested sheet. `transaction_store` records `print_copies` and `demo_order_pricing`. `app.py` sends **one serialized RAW print batch** for each completed layout; `printer.py` renders once, repeats the image+cut stream N times, and closes Windows spool documents correctly. The owner confirmed pricing and physical counts after BUG-011 fixes. **This is not a machine-generated physical print counter:** the user must wait for the printer to finish, and a partial/uncertain batch must never be automatically resent. One manual retry could duplicate already-printed paper. No robust paid-reprint ledger exists (FEAT-007/016 deferred), full Kiosk CI still needs remediation, and checkout stays DEMO. See [FEAT-001/BUG-011 acceptance evidence](qa/FEAT-001-BUG-011-acceptance.md).

**Future FEAT-002 / FEAT-005:** dummy food receipt scanning or local dummy ordering-to-photo discount in one machine; real partner ordering delegates to merchant-supplied, safe customer-facing web ordering. Real receipt/POS verification is deferred until an actual partner provides its format and APIs. Treat demo food payment as simulated and never infer genuine eligibility from decoded receipt text alone.

## Advertising architecture: current vs proposed

- **Current:** `photobooth/assets/ads/playlist.json`, optional `PHOTOBOOTH_AD_CONFIG` and automatic local `ad_video/` media; playback events are locally reportable. Merchant-configured ad playlist is not a centrally authorized subscription/slot service.
- **Required future business rules:** sold devices have assigned Free/Business/Enterprise tiers; Free is fully commercially usable but **100% Meong-managed ad content**; Business/Enterprise can schedule their own ads but Meong retains reserved placements of **TBD percentage**. Per-machine local-first Drive sync (FEAT-004), remote configuration (FEAT-010), licensing/entitlements (FEAT-019), fleet controls (FEAT-018) and reporting (FEAT-013) are related proposals, not present enforcement.
- **Design concerns:** Operators with administrative access to their purchased Windows mini PC can modify local configuration/media. A local playlist is not tamper-proof or sufficient to guarantee Meong ad impressions. Commercial conditions, signed bundles and contractual/venue permissions must be investigated; avoid claiming technical enforcement or advertising revenue until verified.
- **Safety:** Keep ads offline-playable, atomically update local media, fail back without interrupting photo/payment/print, isolate partner campaign content and honor competitor/exclusivity restrictions.

## Printing architecture: routes and separate acceptance

- **Photo layout:** `ThermalPrinter` renders to native ESC/POS raster, applies configured dither (Floyd–Steinberg/Bayer/threshold), then routes via configured LAN, Wi-Fi or Windows USB/spooler. The owner reports actual paper output, **but print quality is still poor** (BUG-004).
- **QR slip:** `QrisPrinterWorker` renders crisp QR pixels with quiet zone, uses GUI-provided saved `PrinterConfig` when present and legacy `PHOTOBOOTH_PRINTER_HOST` only for standalone/fallback usage. Printing QR currently **fails on the user's device** (BUG-003); spooler/send acknowledgement cannot prove physical output or phone scannability.
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
