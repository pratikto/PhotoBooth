# FEAT-022 — Portrait Kiosk GUI v2: engineering architecture and integration contracts

> **P4a implementation (2026-10-23):** `game_engine.py` is the byte-identical read-only reference engine; `demo_game.py` owns isolated SQLite attempts and single-flight I/O; `game_scene.py` / `game_views.py` own native pages and lifecycle. Game outcome is only a DEMO candidate, never payment authority. 377 full PASS; no branch merge. [Evidence](qa/portrait-v2-p4/README.md).

> **P3 implemented boundary (2026-10-23):** `devices.py` owns the asynchronous camera/face adapters. `photos.py` / `PhotoJobs` serialize isolated photo-test work; `photo_views.py` supplies native confirmation/capture/review/result pages. `photo_drive.py` holds uploads until retention acknowledgement. Storage/pool/IDs use a separate v2 namespace; print has a durable no-replay journal. The explicit UJI FOTO admission never sets PAID or grants discounts. Physical Windows device parity remains pending; older proposed/no-approval tables below are historical for P3. [Current implementation and evidence](qa/portrait-v2-p3/README.md).


**Branch:** feature/portrait-kiosk-v2-next  
**Design authority:** [FEAT-022 primary specification](portrait-kiosk-v2.md) and [approved visual reference](portrait-kiosk-v2-visual-spec.md)  
**Status:** the explicitly labelled **CURRENT** items below were found in opt-in source; everything labelled **PROPOSED** is a future interface, not an implemented integration.  
**Base:** stable master, original v1.0.0 remains unchanged; dedicated v2 package descends from feature/portrait-kiosk-gui.

> **P3 authorization/current override (2026-10-23):** Owner explicitly requests
> P3a and P3b. P3a now reuses one asynchronously opened camera and the existing
> nonrecording face worker/hold policy for automatic idle invitations. Native
> imports remain lazy and QA fixtures keep hardware disabled. P3b will connect
> photo/print/Drive via isolated nonfinancial test admission; no real payment,
> scanner, discount, game integration or production transactions are authorized.
> [Current source evidence and remaining physical gates](qa/portrait-v2-p3/README.md).
> Older CURRENT/PROPOSED inventory below describes the pre-P3 snapshot where
> superseded by this update.

## 1. Rebuild principle

Greenfield v2 rebuilds **Kivy customer-facing widgets, navigation, page transitions and audio ownership** from scratch. Reuse only already working, independently testable back-end services and original approved design/media assets; do not copy the legacy v1 screen layout as a new "portrait" presentation. Never rewrite camera JPEG acquisition, print raster/transport, Drive manifest/upload or order accounting merely to change the presentation layer.

- Default launcher remains **python main.py** → legacy stable PhotoBoothApp / v1.
- Opt-in launcher is **python tools/run_portrait_v2.py** → PortraitKioskV2App, currently a safe prototype that must not charge, claim a real struk, take photographs or print paper.
- No feature branch, PR or documentation change implies a merge to master, a tag modification, payment activation or customer deployment.

## 2. CURRENT source inventory, file-by-file

| Path | Current responsibility | Current boundary |
| --- | --- | --- |
| photobooth/kiosk_v2/__init__.py | Python package marker | No service integration |
| photobooth/kiosk_v2/app.py | New Kivy App, screen tree, branded controls, advert, manual invitation overlay, tutorial, template previews and qty; displayed DEMO quote | Does not enter real camera, payment, printer, Drive or game |
| photobooth/kiosk_v2/flow.py | Small pure VisitFlow state machine | Four routes only: advert, tutorial, templates, game_preview; no real game/receipt/discount |
| photobooth/kiosk_v2/theme.py | Starfield, PixelCard, ArcadeButton, text layout and approved theme colors | Presentation-only Kivy elements |
| photobooth/kiosk_v2/audio.py | Independent PortraitAudio: native WAV loading, page-owned music/SFX, SDL2-first desktop provider (unless explicit KIVY_AUDIO override), fallback and stopped-state diagnostic | Does not prove physical speaker audibility; no existing v1 AudioManager lifecycle imported |
| tools/run_portrait_v2.py | Opt-in portrait window launcher | Not the production entry point |
| tools/render_portrait_v2.py | Synthetic portrait visual capture at 800×1280 and aligned 452×900 | Linux/Xvfb screenshot is not actual touch/speaker/print acceptance |
| tests/test_kiosk_v2_flow.py | Navigation/tutorial-once/idle reset tests | No real POS, payment or game engine |
| tests/test_kiosk_v2_audio.py | Fake provider, page lifetimes and fallback diagnostics | Mocks cannot verify audible output |
| tests/test_kiosk_v2_widgets.py | Real Kivy widget smoke with synthetic window | Camera, face presence, QRIS and printer not connected |
| .github/workflows/portrait-kiosk-v2.yml | Separate Python and Xvfb/screenshot checks on v2 branches | No Windows/hardware certification |

**CURRENT shared services being used:** AdCatalog and AdvertisementPlayer for local idle media playback, actual branding asset, get_templates/create_template_preview for all 12 masters, and quote_order for the DEMO cart display. These are service/data dependencies, not legacy GUI layout reuse.

**CURRENT entry edges:** advert → tutorial → templates; advert → game_preview (informational placeholder) → optional return to tutorial/photo; advert → manual inline invitation overlay; browse timeout → advert. There is **no actual camera-based face invitation** yet in v2.

## 3. PROPOSED separation of responsibilities

| Layer | Planned responsibility | Forbidden shortcut |
| --- | --- | --- |
| PortraitShell / Kivy views | Render UI states and emit typed user intents on GUI thread | Do not calculate payable amount as authorization, claim a receipt or mutate a paid order |
| VisitCoordinator | Own entry origin, tutorial_seen, selected template quantities, safe post-game continuation, promo candidate lifecycle | Do not reset a consumed receipt on idle/new customer |
| MeongFlyAdapter | Own game-pause/result callbacks and single-use receipt claim via durable ledger | Never trust score or client widget text as a financial entitlement |
| Quote/Promotion adapter | Validate eligible receipt, promotion campaign, one-use result and server-side payable total | Never trust GUI-supplied discount amount; never silently stack FEAT-002 and mini-game promos |
| CheckoutAdapter | Run DEMO vs MOCK vs Sandbox explicitly, maintain idempotent visit/order identity and authoritative payment grant | Never admit capture on QR display, local button, paper slip or uncertain payment |
| CameraCaptureAdapter | Acquire 3 original source frames, mirror **preview only**, allow the existing selected one-photo retake | Do not mirror saved bytes or create more poses when copies change |
| PrintAndDeliveryAdapter | Compose actual 80×240mm approved strip, send N copies, track print, upload/Drive QR and result status | Do not confuse QRIS with folder QR or treat queued print as paper acceptance |
| KioskIdlePolicy | Return pre-payment browsing to advertising with warning, protect locked/paid/unknown sessions | Never time out an active payment/capture/print/unknown payment into an unsafe new visit |
| AudioOwner | Explicit page-domain music and SFX vs advertisement media audio | Never let v1 and v2 managers run over each other |

**No new shared-service interface is implemented merely by adding this proposed architecture.** Each adapter requires an owner-approved scoped integration commit plus cross-branch regression.

## 4. PROPOSED visit context and transition invariants

Suggested conceptual fields (not a persistent schema and not production code):

| Field | Meaning | Lifetime |
| --- | --- | --- |
| visit_id | Opaque current customer/booth visit identifier | Created on entry; preserved across game→template→checkout; retire only on safe completion |
| entry_source | manual_photo / face_photo / manual_game / face_game | Visit only |
| tutorial_seen | Explicit tutorial acknowledgement once | Visit only; reset on a new visit |
| selected_copies | Map of template ID → printed copies | Until order finalized; can edit before payment |
| game_result | none / won / lost, bound to the claimed attempt | Visit only display state; must not be source of checkout authority |
| receipt_attempt_id | Durable one-time attempt/claim record identifier | Must remain consumed across game reset, app restart and visitor timeout |
| discount_candidate | Proposed Rp2.500 win badge, not an authorization | Visit/order only; server revalidates prior to creating payable QRIS |
| checkout_key | Idempotent payment visit/order identity | Persist through retry/restart until safe reconciled completion |
| payment_state | Provider-authoritative pending/paid/failed/expired/unknown/recovery | Do not reset on generic idle; preserve until safe disposition |
| fulfillment_state | Capture/compose/print/Drive result and uncertain/recoverable jobs | Persist or recover safely until completed |

Transition expectations:

| From | Event | To / guard |
| --- | --- | --- |
| advert | Foto CTA / accepted face photo invite | tutorial unless tutorial_seen; otherwise templates |
| advert | Game CTA / accepted face game invite | dedicated game intro (not second home) |
| game intro | Continue | receipt scanner/demo code |
| receipt | Valid unclaimed receipt | atomically consume one attempt; then game |
| receipt | Invalid/used/offline | explain reason, no gameplay or discount |
| gameplay | Terminal result | win or lose, never offer replay |
| win or lose | Continue | tutorial iff unseen; else templates — **not payment** |
| tutorial | Explicit completion | set tutorial_seen true → templates |
| templates | Confirm order | authoritative quote/checkout; no camera yet |
| payment | Verified appropriate grant | camera admission once, with recovery guard |
| capture/review | Three photos and accepted review | compose/print/result with original assets |
| result | All required safe completion checks met | retire visit, then advertising |
| tutorial/templates | 180s inactivity; warn at final 10s | abandon pre-payment visit and return to advertising |
| active/unknown paid or printing | Generic idle tick | **no navigation/reset**, perform safe provider/print recovery |

**Timeout and face policy baseline:** ad catalogue currently configures stable-face hold 5 s, face-invite lifetime 15 s, cooldown 45 s, browsing inactivity 180 s and last-10 s warning. Actual v2 face detection is not attached; its invitation trigger is currently only an operator preview button. Payment validity and game timeout must be determined by their respective authorized services, not by labels in a concept screenshot.

## 5. Audio subsystem — CURRENT and planned gates

**CURRENT v2 behavior:** on advert the application's music/effects must yield to the advertisement media. On tutorial and templates, PortraitAudio loads the bundled original Meong PCM WAV media and starts one music loop; it reuses the handle between those screens without replaying. Leaving these music pages stops it. The game_preview does not start another loop. Test Music explicitly attempts a restart for diagnostics; suspend/resume and unload are centralized.

**Audio provider hardening present on this branch:** desktop SDL2 SoundSDL2 is preferred unless the operator explicitly provides KIVY_AUDIO; plain SoundLoader is a fallback. select_pcm_handle rejects missing/zero/NaN/non-finite duration, unloads a rejected native handle, and reports an error when the provider remains in state=stop after play. It does **not** solve every possible silent-channel, OS mixer or audio-device failure. The main legacy sound code in photobooth/audio.py is unchanged.

**Required Windows acceptance:** correct output-device selection and mixer settings; actual audible auto-play on Tutorial (without Test Music); continuity through Templates; silence of application music on idle video; ad video source audio when the actual file contains it; no duplicate simultaneous music; reliable Test Music effect; correct app pause/resume; recoverable missing-sound behavior. Distinguish provider state acknowledgement from actual audible output.

**PROPOSED post-integration audio policy:** dedicated Meong Fly game channel; music/game effects during gameplay, stop/release on terminal result/return; countdown/shutter effects only while capturing; QRIS payment advertising muted. An explicit audio-bus contract is required before integrating provider playlists with game audio.

## 6. Real payment and discount integrity (PROPOSED)

The existing **feature/qris-payment** branch is a separate QRIS-MOCK/Midtrans-Sandbox experiment; v2 does not inherit it automatically. Its server-side quote currently uses selected templates/sheets and does not validate a Meong Fly promo. The **feature/meong-flappy-challenge** branch has a standalone game and durable single-use DEMO token ledger; no real cafe receipt integration or redeemable Rp2.500 award exists.

Before promising the win discount: define campaign issuer, real merchant eligibility, signed/nonce-backed one-time receipt evidence, whether it discounts base fee vs total, scope of exactly one use per transaction, anti-duplicate/late-result policy, concurrency and restart recovery, provider-side quote calculation, refund/merchant reimbursement rules, and incompatibility/priority relative to FEAT-002's separate cafe receipt promotion. A wallet/checkout must receive a server-approved total, not a GUI-calculated amount. A consumer never needs to hand over bank credentials at the kiosk.

**Payment QR versus photo QR:** checkout QR must come from an authorized payment provider in real modes. The 1:3 printed-strip QR is a separate customer photo-folder access URL. Mock/dummy barcodes in the artboards do not grant money, prove food purchases or authorize downloads.

## 7. UI/media/camera/print performance and safety

- Portrait reference dimensions 800 × 1280; maintain readable text and tappable actions for compact sizes without cropping core CTA, QR or user photo. For 450-wide virtual screenshots, the existing capture script uses 452 pixels to avoid an observed Xvfb/SDL2 RGB-row packing issue; this is a screenshot workaround only.
- Preserve camera preview image ratio and horizontally mirror **the displayed texture only**, never the original captured pixels, print composition or uploaded photos.
- Use fixed approved template masters, keep a crisp/downscale-friendly 1:3 print preview, and draw the photo-folder QR with integer-sized, readable black/white modules rather than applying destructive color dithering to QR blocks.
- Advertising video/image may have different dimensions and codecs; scale with contain/aspect-preserving rules, provide fallback artwork, and keep optional invitation overlay readable above the video without restarting every media frame.
- Use Kivy main-thread widget updates; camera, network provider, AI inference, printer and upload jobs must not block the GUI. Callbacks must check visit ID, page revision and active order to reject stale work from a former visitor.
- Do not allow media playback, logo effects or multiple full-res template texture recreations to overload the target SBC/mini-PC. Profile actual CPU/GPU/frame pacing and memory on the intended hardware before release.
- Preserve durable transaction/print journals, uncertain-payment holds, Drive retention/deletion notices and error propagation; avoid deleting a print job merely because the result screen timed out.
- A Kivy screenshot, a successful RAW spool or an uploaded file request alone cannot certify physical photo print, correct paper count, legitimate payment or verified customer download.

## 8. Dependencies and planned delivery sequence

| Gate | Activity | Hard dependency / exit evidence |
| --- | --- | --- |
| P0 | VisitFlow, tutorial-once + safe idle | CURRENT; pure tests and no legacy modification |
| P1 | New page-owned audio manager + provider fallback | CURRENT; synthetic tests pass, **audible Windows acceptance remains OPEN** |
| P2 | Portrait idle media, manual invitation overlay, tutorial and real template gallery | CURRENT; synthetic Kivy screenshot/widget QA available, real touch/device QA OPEN |
| P2.5 | Visual parity with owner-approved pixel-arcade boards and corrected CTA/flow | Gallery/side-by-side screenshot review and design approval |
| P3a | Actual face detector entry (if enabled) and safe overlay | Physical camera and privacy/nonrecording checks |
| P3b | Camera / countdown / review / one-retake / print/Drive via adapters | Exact v1 functionality parity, mock + real printer/camera/Drive evidence |
| P4a | Meong Fly intro/receipt DEMO and result→tutorial/template | Single-attempt durable ledger; no true promo settlement claim |
| P4b | Conditional promo and QRIS-MOCK/Sandbox integration | Backend-calculated amount, idempotent payment, no duplicate admission, merchant approval |
| P5 | Commercial release certification | Multi-branch full regression, Windows hardware, provider acceptance, privacy and explicit merge/release signoff |

Preserve the existing branch scope and do not auto-merge Meong Fly, QRIS or AI Background Studio branches. Reconcile the conflicting use of FEAT-021 by standalone Meong Fly and Background Studio before merging development histories; this GUI is tracked as **FEAT-022**.

## 9. Test and evidence contract

Reference checklist: [test_checklist.md](test_checklist.md).

- Automated: Python syntax, VisitFlow valid/invalid transitions, audio provider handling and page ownership, Xvfb Kivy widget interactions, 800 × 1280 and aligned 452 × 900 visual regressions.
- Integrations when approved: duplicate receipt/restart, tutorial seen/unseen game outcomes, promotion one-use and authoritative pricing, payment callbacks/reconnect/retries/cancel/unknown state, three original captures, one-photo retake, multiple template sessions, physical-copy output, QR scan, Drive offline queue/retention.
- Device: Windows target portrait display and touchscreen mapping, actual camera and face light thresholds, native sound output, video codecs, thermal printer paper, QR scanning from phone and offline fallback.

Record *exact test SHA, command, OS/versions, PASS/FAIL/SKIP, screenshot artifacts and physical observations*. Prior branch's green synthetic CI must not be misrepresented as Windows operator acceptance. Do not close BUG-001/007 legacy music or BUG-009 Drive retention based on this prototype.

## 10. Operational ownership, rollback and governance

Stable **master / v1.0.0** remains the rollback route and customer baseline. The v2 window is opt-in and is not permitted to allocate real transactions. Do not edit or delete existing customer manifests, receipts, payment journals, key material or cloud setup to test v2. Never force-push/delete feature branches.

Use scope-specific commits with required documentation and CI proof. Follow [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md). No merge to master, live payment enablement, production deployment or real commercial promo requires anything less than separate explicit owner approval.

## P2.5 implementation update — validated arcade UI (2026-10-21)

**Code delivered on this branch, opt-in only:** new `photobooth/kiosk_v2/illustrations.py` scales four symbolic tutorial graphics with Kivy canvas vectors; `theme.py` paints sharper stars, decorated PixelCards and native ArcadeButtons with pressed/disabled visual states; `app.py` renders an ad-dominant invite entry with separate Foto/Game/Cara Pakai actions, illustrated tutorial, side-by-side previous/current/next **real print master** gallery, DEMO-only copy quote, and a distinct Meong Fly intro with an explicitly disabled scanner. A `SwipeGallery` Kivy BoxLayout handles user horizontal drags within the gallery, rejecting vertical/short motion. The VisitFlow continues to expose exactly advert/tutorial/templates/game_preview, and owner-of-visit tutorial_seen behavior is unchanged.

**No integrated new services:** real face trigger, receipt capture/ledger, gameplay result, discount entitlement, Midtrans provider, camera and printing are not connected to this UI prototype. The Meong Fly intro is not a POS scanner or one-time voucher issuer. The uploaded approved artboards are documentation only, not runtime bitmaps. Kivy still uses current default fonts; exact visual parity is open.

**Source regression:** [Actions 39555036023](https://github.com/pratikto/PhotoBooth/actions/runs/39555036023) at source SHA `c4e4703a` — 21/21 pure tests PASS, updated Kivy widget smoke PASS, 12 screenshots PASS at 800×1280 and 452×900. Physical Windows audio and gesture/touch QA are unverified. Proposed backend adapter and protected transaction boundaries above remain unchanged.
