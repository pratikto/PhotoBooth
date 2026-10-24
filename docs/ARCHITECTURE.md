# Meong Photobooth — Current architecture and future boundaries

> BUG-015 correction: game_layout now applies one uniform world translation; no position-dependent motion projection. MeongLogo uses one native decorative animation with explicit pause/retirement hooks; centered wordmark, gallery floating title and equal quote columns share existing widgets. [Contracts/evidence](qa/portrait-v2-motion-correction/README.md).

> Responsive original-art adapter (2026-10-24): game_layout.py reflows cached original card/glyph pixels over one full-stage source sky. Original Stage dynamic drawing, engine, camera/film compositor and audio owner are reused unchanged; transformed hitboxes and film corners share the layout. [Contract and evidence](qa/portrait-v2-responsive-scene/README.md).

> **Portrait v2 P4 addition (2026-10-23):** Read-only reference engine → native game pages; `demo_game.py` and `mock_checkout.py` share a separate P4 SQLite ledger for consumed DEMO attempts, simulated quotes/orders and one-use admission. `GameJobs` serializes off-GUI I/O. MOCK checkout is opt-in and only hands off to existing explicit nonfinancial P3 consent. Legacy services remain unchanged; real merchant/provider integration is still external. [Evidence/contracts](qa/portrait-v2-p4/README.md).

> **V2 input/preview follow-up (2026-10-23):** `live_preview.py` prepares bounded RGB bytes in one latest-frame worker; Kivy only uploads a prepared texture, preserving original BGR capture pixels. `sensors.py` defers optional native imports and adapts the existing palm hold/release worker to the shared v2 countdown. Face progress and optional-palm readiness are visible; no second camera, paid admission or new recognition model is introduced. [Contracts/tests](qa/portrait-v2-p3-retest/README.md).


> **Portrait v2 P3 addition (2026-10-23, feature branch only):** Dedicated `tools/run_portrait_v2.py` now hosts native camera/capture/review/result pages via `kiosk_v2/devices.py`, `photos.py`, `photo_views.py` and `photo_drive.py`. Existing camera/workflow/store/composer/printer/Drive implementations are reused without launching or editing the legacy GUI. Test storage and pool use `data/kiosk-v2-p3` / `PB001V2`; worker threads perform disk/device/network work, and current-page UI polls outcomes. Live-only UV mirroring preserves saved pixels. A persisted SENDING journal prevents uncertain print replay. [Adapter contracts and evidence](qa/portrait-v2-p3/README.md).


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


## FEAT-022 — Greenfield portrait kiosk v2 (branch-only design / source, 2026-10-21)

Working prototype only: photobooth/kiosk_v2/ is a separate Kivy presentation and visit-state boundary, started via python tools/run_portrait_v2.py. It does NOT replace the released python main.py, ui_kivy.py, ui_kiosk.py, or PhotoBoothApp transaction/controller routes. The v2 UI has fresh Space theme/panels, explicit VisitFlow navigation, and new PortraitAudio (no photobooth.audio.AudioManager imports). Bundled WAVs are reused as assets only. The already-tested AdCatalog and AdvertisementPlayer are reused as **media adapters**, not as v1 page layouts.

Current v2 route: advertising with optional inline **preview-only** invitation -> direct photo -> mandatory tutorial once per visit -> true 12-template gallery and copy-count/DEMO quote, or advertising -> Meong Fly **integration notice** -> skip to tutorial/photo. Game, real face detection, verified cafe receipt, valid promo discount, real QRIS, camera capture, retake, printing, and Drive upload are explicitly not connected to this launcher. The normal v1 program remains operational and unchanged. Data-sensitive backends will be introduced behind safeguards only after staged approval/QA. See portrait-kiosk-v2.md.

## FEAT-022 architecture update — approved mockups and safe adapter boundaries (2026-10-21)

**Development head:** feature/portrait-kiosk-v2-next (derived from feature/portrait-kiosk-gui); no master merge. Canonical design: [portrait GUI v2](portrait-kiosk-v2.md); actual last approved artboards: [main](assets/portrait-v2/meong-main-flow-approved.webp) and [mini-game](assets/portrait-v2/meong-fly-revised-approved.webp); behavioral corrections: [visual specification](portrait-kiosk-v2-visual-spec.md); module/adapter contract: [technical design](portrait-kiosk-v2-technical-design.md).

**Current opt-in implementation only:**

- photobooth/kiosk_v2/app.py owns fresh portrait screen widgets and a separate Kivy ScreenManager; existing Kivy UI and PhotoBoothApp remain the production path, not reused as new layouts.
- flow.py owns visit-scoped advert/tutorial/templates/game_preview routing and explicit tutorial_seen; game_preview is a **nonfunctional notice**, not gameplay or discount.
- audio.py owns portrait WAV sound handles independently, with desktop SDL2-first provider selection, SoundLoader fallback and bounded diagnostics. Native provider PASS is *not* an audible Windows speaker test.
- theme.py renders Pixel Arcade Space UI primitives, backed by the original approved Meong logo and 12 actual printer template previews. AdCatalog and AdvertisementPlayer are **reused services**, not layout widgets from v1.
- The current v2 face invitation is a **manual-preview overlay on advertising**; real live camera face trigger has not been connected.
- The current v2 photo checkout, QRIS, camera capture/retake, printer, Drive and single-use real café receipt interfaces do not exist. Calling their source modules in v1/other branches does not prove their v2 integration.

**Proposed integration contract (NOT IN SOURCE):** Kivy presentation → visit coordinator → typed adapters for face detector, standalone Meong Fly + receipt ledger, server-authorized discount/QRIS checkout, camera, strip composition, spooler and Drive. A future customer visit must preserve tutorial-once state, game Win/Lose routing to *template selection* (with tutorial if unseen), durable consumed receipt attempts and provider-verified paid state. Generic browsing timeout may only clear pre-payment visitors; it must not destroy active/unknown payment or printing. The print master remains 80×240mm, 3 photographs plus photo-folder QR; payment QRIS must stay distinct.

**Evidence:** [run 39548798578](https://github.com/pratikto/PhotoBooth/actions/runs/39548798578) on code/mockup SHA 6e7f29a7 succeeded with 21/21 fake audio/navigation cases and synthetic Kivy widgets/screenshots, not Windows camera, speakers, touchscreen, physical paper or provider payments. Never merge other task branches automatically; FEAT-021 ID collision (Meong Fly versus Background Studio) must be reconciled before cross-branch feature registration.

## FEAT-022 — P2.5 isolated UI component update (2026-10-21)

`photobooth/kiosk_v2/illustrations.py` adds non-scannable decorative tutorial vector icons. `theme.py` updates Starfield/PixelCard/ArcadeButton rendering only; `app.py` now contains SwipeGallery, which accepts horizontal gestures only from within the three real-strip gallery, with no routing to payment. The isolated app still shows advertising with photo/Meong Fly/Cara Pakai CTAs; Meong Fly has a **responsive introduction screen** but scan remains disabled. Core visit manager (`flow.py`) retains four routes, tutorial-once and browsing-only timeout protections. [Synthetic CI 39555036023](https://github.com/pratikto/PhotoBooth/actions/runs/39555036023) passes; no shared production camera, payment, printer, Drive or legacy audio code changed. The adapters described in [technical design](portrait-kiosk-v2-technical-design.md) are future work requiring separately verified integration.
