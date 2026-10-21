# FEAT-021 to FEAT-022 — Integration Blueprint (planning only)

**Audit date:** 2026-10-21  
**GUI branch:** `feature/portrait-kiosk-v2-next` (baseline `8b41a062a6f071b5c1a285481680e330b6b73f90`)  
**Game branch:** `feature/meong-flappy-challenge` (read-only at `672e3f7089bb40940e5b41644ceb656aa63aafbb`)  
**Status:** PLANNED — **not authorized for integration**. No actual game, payment, scanner or promotion was wired into GUI v2 by this document.

## 1. Source-grounded inventory

| Existing module | Responsibility / interface | Dependency / lifecycle / state | Readiness and integration risk |
| --- | --- | --- | --- |
| `meong_fly.py` | `MeongFly.reset/start/flap/step`, collision, score, 25-second round, target 10 | Pure Python; injected RNG; state in memory | Reuse as-is; engine tests exist; do not fork |
| `meong_fly_flow.py` | `MeongFlyFlow.open_scan/claim_and_start/tick/continue_from_result` | Owns screen, result-once guard, demo ledger, tutorial flag | Needs navigation adapter; standalone tutorial/layout destination must be bypassed |
| `meong_fly_gui.py` | `MeongFlyStage(flow, scanner=None)`, `dispose`, `update`, viewport and Kivy events | Kivy stage schedules 30Hz updates; caches textures; Window mouse binding | Reuse one stage in existing window; prevent duplicate clocks/Window bindings |
| `meong_fly_scanner.py` | `ReceiptScanner.set_active/snapshot/dispose` | Background thread, exclusive camera handle, 640px mailbox, DEMO QR decode | Adapter candidate; physical release timing and device conflicts require QA |
| `meong_fly_receipts.py` | `DemoReceiptLedger.claim/finish` | SQLite unique receipt primary key, result `started/won/lost`; persistent | DEMO-only, atomic single claim; crash-recovery and production receipt auth not covered |
| `meong_fly_sprite.py` | `camera_frames/fit_rect/world_slot` | Bundled authored camera-cat art and slot geometry | Reuse existing artwork; asset provenance/versioning required |
| `meong_fly_game_art.py` | `paint_game_background/make_rock_tile` | Pillow static assets; pre-uploaded Kivy textures | Reuse; benchmark startup/texture footprint |
| `meong_fly_painter.py` | `paint_static_screen`, 5x7 glyphs, palettes/hitboxes | Pillow rasterization in 360x720 logical pixels | Visual authority; avoid two divergent token systems |
| `meong_fly_polish.py` | `arcade_card/arcade_button/paint_polished_menu` | Pillow draw-time pixel-step material | Geometry/style reference for Kivy-native components |
| `meong_fly_visual_v3.py` | `paint_poster_screen/printed_photo_tile` | Cached sprite and background helpers | v5 live compositor supersedes some historical GIF helpers |
| `meong_fly_print_fx.py` | `InstantPhotoEmitter.update/poses/reset` | Pure Python, attached feed → hold → fall; bounded sheets | Reuse; never duplicate a second emitter |
| `meong_fly_photo_handoff.py` | `photo_handoff_screen/layout_hitboxes` | Standalone generic demo tutorial/layouts | Do **not** reuse as production tutorial or 12 thermal templates |
| `meong_fly_demo.py` | `MeongFlyStandaloneApp` launcher | Opens its own standalone Kivy app | Development-only; do not start second Kivy App inside GUI v2 |
| `kiosk_v2/flow.py` | `VisitFlow`: advert/tutorial/templates/game_preview | Visit-scoped tutorial flag; safe idle reset | Future adapter must preserve visit and postgame routing |
| `kiosk_v2/audio.py` | `PortraitAudio.enter_page/cue/suspend/resume/close` | Owns GUI v2 music/SFX | Must become sole application audio coordinator |
| `kiosk_v2/app.py` | Advertising, inline invitation, tutorial, 12 production templates | Kivy ScreenManager, media player, lazy template textures | Keep existing production-facing pages; game preview currently disabled |

**Existing QA evidence:** Meong Fly scanner documentation records 98 Linux PASS at `76761a7`; v5 Phase 1 records 91 Linux PASS at `a83eee8` and 12 Kivy FBO captures. These are historical tested source revisions, not a fresh complete run at current game HEAD. GUI v2 P2.5 records 21 Python tests and Kivy visual CI on earlier source; neither is physical Windows acceptance. Audit all `tests/test_meong_fly*.py` before actual integration.

## 2. Integration readiness and adapter matrix

| Area | Current status | Proposed adapter | Key gate |
| --- | --- | --- | --- |
| Engine / gameplay | IN SOURCE standalone | Embedded stage + lifecycle coordinator | Same engine, no second app or duplicate update loop |
| Scanner | IN SOURCE DEMO | Exclusive camera lease adapter | Mirrored display only, unmirrored decode, release before capture |
| Receipt ledger | IN SOURCE DEMO | Reuse existing SQLite ledger for demo | Crash/restart, duplicate rejection, idempotent terminal result |
| Sprite / art / print FX | IN SOURCE | Versioned shared asset ownership | No duplicate cat or paper emitter; nearest-neighbor rendering |
| Audio | Separate v2 audio; game audio must be audited | Single audio owner | No overlapping video/music/game sounds |
| Win/Lose handoff | Standalone demo routes to generic layouts | Typed result callback into visit coordinator | No direct payment, no retry, once-only terminal event |
| Tutorial | Two implementations exist on separate branches | Use only GUI v2 tutorial | Once per visit; no duplicate tutorial |
| Template picker | GUI v2 has 12 real strips | Use only GUI v2 carousel | Exactly 3 photo slots + folder QR; quantity = copies |
| Discount / QRIS | Not connected | Backend promotion/quote adapter (future) | Authoritative server verification and payment sandbox approval |

## 3. Proposed architecture and choice

**Recommended:** embed the existing `MeongFlyStage` as a Kivy child of the GUI v2 ScreenManager, wrapped by a small lifecycle/navigation adapter. Preserve `MeongFly`, `MeongFlyFlow`, scanner and ledger implementations. A coordinator owns entry, exit, resource release, visit identity and result callbacks. This combines the reusable-widget, embedded-stage, scene-adapter and lifecycle-coordinator approaches without running two Kivy App instances. The exact implementation interface is **proposed**, not already exported by the game.

At integration time, transfer reviewed/versioned source and assets into one repository branch via scoped, reviewed commits; **no runtime Git branch imports**. Never merge the entire game branch blindly.

## 4. Unified route / invariants

`Idle advertising + face invitation overlay → Meong Fly intro → Scan DEMO QR/manual → explicit validation → atomic claim → gameplay → Win/Lose → GUI v2 tutorial iff not seen → GUI v2 12 thermal template carousel → future checkout`.

Direct photo: `Idle → tutorial iff unseen → templates`. No game retry. Win yields only a **candidate** Rp2.500 promotion; Lose yields none. A terminal result must be delivered at most once and must not reset the consumed receipt. Tutorial flag belongs to visit, not the durable ledger. A generic pre-payment idle timeout must not discard any paid/uncertain transaction.

## 5. Ledger, session, recovery

Create a future opaque visit/session ID at entry. Bind the consumed DEMO receipt, terminal outcome and candidate reward to that visit. On restart, `started` must remain consumed; define an explicit interrupted-game outcome and never regrant the attempt. Use an idempotent terminal handoff key to prevent repeated callbacks from granting two rewards. Keep SQLite persisted across restarts, but do not use the DEMO ledger as merchant/POS proof. A future backend must verify actual merchant eligibility and reward redemption separately.

## 6. Camera ownership

One physical camera owner at a time. Enter Scan → acquire scanner camera asynchronously; decode unmirrored raw frame, display mirrored texture UV; Back/Validate/Exit → request stop and wait for actual driver release before later photo capture. A still-closing scanner cannot open another handle. On driver errors, allow manual DEMO entry; on stale worker callbacks, ignore by page revision/session ID. Do not save scanned video frames.

## 7. Audio ownership

The GUI v2 `PortraitAudio` (or its future single coordinator) owns transitions: Idle ad audio → game intro → scanner → gameplay → result SFX → tutorial music → template music. On every page change stop/pause prior track and release inactive callbacks. Existing game has no proven unified audio bus. Test physical Windows speakers before claiming audio fixed; mock provider states are not audible evidence.

## 8. Financial boundary — no implementation permission

`Game Win → reward candidate → template/cart → server-side eligibility and one-use verification → authoritative payable quote → QRIS Mock/Sandbox → verified payment → capture`.

Resolve FEAT-002 receipt promotion conflicts, stackability, issuer/POS identity, claim/redeem idempotency, checkout restart, provider callbacks and refund/reimbursement rules before touching actual payment. GUI game score and local SQLite alone must never reduce the QRIS amount. Production payment remains prohibited.

## 9. Performance, cancellation, recovery and security gates

- Cache Kivy textures; do not upload Pillow frames every game tick.
- Measure Kivy 30Hz scheduling, FPS, texture/memory growth and UI touch latency on actual 10.1-inch target hardware.
- Use Kivy main-thread callbacks for widgets; background camera/decoder workers must never update widgets directly.
- Cancel game clock, mouse bindings, scanner worker and visual animation when leaving stage.
- Reject stale result/scan callbacks using visit ID and page revision.
- Test app pause/resume, camera disconnect, scanner close/open race, interrupted SQLite write, duplicate QR, abandoned visit, timeout and recovery.
- No production receipt ledger reset or real payment during fixture tests.

## 10. Staged roadmap — requires separate owner approval

| Milestone | Proposed deliverable | Gate |
| --- | --- | --- |
| I1 | Game lifecycle adapter + embedded stage | Single Kivy window, disposal and stage tests |
| I2 | Unified navigation + tutorial-once | Direct and postgame flow tests |
| I3 | Existing DEMO scanner + SQLite ledger | Single-use, mirror, release and crash tests |
| I4 | Win/Lose handoff into real template/cart UI | One terminal callback, no replay or payment jump |
| I5 | Server-side promo model + QRIS Mock/Sandbox | Explicit owner approval; idempotent authoritative quote |
| I6 | Full regression and physical hardware acceptance | Windows touch/camera/audio/printer, measured FPS, exact SHA and owner sign-off |

**Stop gate:** I1–I6 are NOT AUTHORIZED by P2.6–P2.8 visual development approval. No implementation or merge of game, scanner, QRIS or payment until this blueprint is reviewed and separately approved.

## 11. Checkpoint and rollback

This is a planning document only. Its presence is not a tested integration checkpoint. Reference baseline GUI `8b41a062a6f071b5c1a285481680e330b6b73f90` and read-only game `672e3f7089bb40940e5b41644ceb656aa63aafbb`. Revert scoped documentation commits if needed, without force-push; preserve receipt databases and customer records. Physical Windows acceptance: PENDING.
