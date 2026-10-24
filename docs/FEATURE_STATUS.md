# Meong Photobooth — Current feature status

> **Meong Fly reuse corrected (2026-10-24):** V2 now mounts the original latest MeongFlyStage/MeongFlyFlow from read-only reference `672e3f7`; original renderer, sprite/print compositor and effects are reused directly. All 26 reference files unchanged; 14 native fixture frames pixel-identical at both target sizes. Final 512/512 full tests PASS, 30 screenshots reviewed. Small host preserves v2 ledger/tutorial/gallery/audio/lifecycle; no real scanner/payment/discount. [Correction proof and checkpoints](qa/portrait-v2-meong-reuse/README.md). Older custom-game visuals below are historical.

> **P4a + P4b MOCK in source (2026-10-23):** Native one-use DEMO game and opt-in local checkout are connected at `97b5596` on the existing v2 branch; [matching-source CI 39973934595](https://github.com/pratikto/PhotoBooth/actions/runs/39973934595) has all three jobs SUCCESS. 406/406 final full tests PASS, zero skips; 42 P4 Kivy captures reviewed at 800×1280/452×900. SQLite computes simulated promo/quote, preserves pending/unknown state and permits one admission to existing P3 consent. Production payment/discount/scanner remain off. Real provider Sandbox/merchant validation and P4 Windows acceptance are still OPEN. [Evidence, commands, 28-item Submit form and rollback](qa/portrait-v2-p4/README.md). Earlier P4a-only/P3-blocking notices below are history.

> **P4a native DEMO game in source (2026-10-23):** Manual DEMO code → durable one-use claim → native game → win/loss → tutorial-once → existing gallery. 377/377 full tests PASS; 22 real Kivy captures reviewed at 800×1280/452×900. No replay, real receipt scanner, payable QR or actual discount. P4b MOCK follows. [Evidence/rollback](qa/portrait-v2-p4/README.md).

> **P4 authorized (2026-10-23):** Owner explicitly requests P4 after P3 acceptance. Stage 1 reuses the existing pure Meong Fly engine and adds an isolated durable DEMO attempt ledger/background command owner; 56 focused tests PASS. New game pages are not connected yet. P3 owner PASS remains valid. Real scanner/payment/discount, provider Sandbox acceptance, branch merge and release remain outside this source claim. [P4 scope/evidence](qa/portrait-v2-p4/README.md).

> **Latest P3 Windows owner retest (2026-10-23):** Focused preview/button form is **16/16 raw checked, twenty cycles, no reported issues**. Preview without touch, first-use buttons, capture/retake/palm, resize/audio/lifecycle and physical print guards are owner-reported PASS. BUG-013 moves to MONITORING; no new patch. HEAD and device fields remain blank, so exact-source acceptance and all-P3 certification are not established. Source checkpoints remain `0d08f07`/`ef0fcb0` with 353 prior full tests PASS. [Owner report, audit and limits](qa/portrait-v2-preview-redraw/README.md).


> **P3 stage 2 (2026-10-23):** Optional open-palm now connects the existing v1 worker/hold/release policy to v2’s same SIAP countdown. Native initialization is deferred off GUI; missing MediaPipe/model keeps manual capture available with a truthful hint. Face invitation shows hold progress, retains five seconds/cooldown and handles accepted inference delay. 348 full native-fixture tests PASS, final 71 focused PASS; physical BUG-013/014 acceptance remains OPEN. [Current evidence](qa/portrait-v2-p3-retest/README.md).


> **P3 owner retest (2026-10-23):** Raw 21/34 checked, thirteen open, twenty reported Windows cycles with HEAD/camera/resolution missing. New shutter/retake/audio/resize are owner-reported passes; face invitation, countdown interruption, print and Drive gates remain open. BUG-013 tracks preview/button/face responsiveness, BUG-014 the missing optional open-palm input. Preview preparation now moves off the GUI and busy photo I/O avoids redundant rebuilds; physical correction is unverified. [Audit and staged evidence](qa/portrait-v2-p3-retest/README.md).


> **Current portrait P3 (2026-10-23): IN SOURCE / DEVICE ACCEPTANCE OPEN.** Camera/face invitation, explicit photo-test admission, mirrored live preview, three unmirrored originals, one selected retake per session, full strip composition and optional guarded print/Drive adapters are connected. New original v2 shutter leaves v1 unchanged. Default output is local; payment/scanner/game/discount stay inactive. BUG-009 remains open; unacknowledged Drive retention blocks P3 uploads. Prior BUG-012 remains owner-reported PASS/monitoring, not new exact-HEAD or twenty-cycle acceptance. [Tests, reviewed screenshots, limits and checklist](qa/portrait-v2-p3/README.md). This supersedes older P3a-only and no-P3-approval notices below.


> **P3 execution authorized (2026-10-23):** Owner requests “oke tolong eksekusi p3”. P3a camera/face adapters are implemented on the existing branch; 86 focused PASS, full 321 run / 319 PASS / 2 optional skips, twelve unchanged captures reviewed. P3b follows within this authorization. Physical Windows camera/face and prior twenty-cycle acceptance remain open; payments/scanner/discount/game integration stay inactive. [Current P3 evidence](qa/portrait-v2-p3/README.md). Older no-P3-approval notices below are superseded for this scope.

> **Current portrait v2 update (2026-10-23): BUG-012 OWNER-REPORTED PASS / MONITORING.** Owner follow-up “sudah oke” reports the return-to-advert flow working after the diagnostic/correction update. Post-update HEAD, cycle count and fresh log were not supplied; the twenty-cycle gate remains unverified. Existing 79 focused / 312 full PASS with two optional skips and exact-source CI at `bef4014` remain separate source evidence. No new runtime changes or device checks are claimed. [Confirmation and remaining acceptance](qa/portrait-v2-return-ad-crash/README.md).

> **Portrait v2 follow-up (2026-10-22, feature/portrait-kiosk-v2-next only):** Owner reports 41 checked boxes at ten Windows cycles, unknown tested HEAD; twenty-cycle gate stays open. Faster feedback, larger full strip previews, floating arrows, native image sliding and matching pixel typography are implemented. 71 focused PASS, full 306 run / 304 PASS / 2 optional model skips, thirty reviewed local page captures. Response `67e9da8` and visual source `5a568bf` each have exact-SHA three-job CI SUCCESS; the latter's original screenshot artifact is digest/hash verified and reviewed. New device retest stays open. [Current evidence and checkpoints](qa/portrait-v2-gallery-focus/README.md). No production/game/scanner/payment enablement or master merge.

> **CURRENT AS OF 2026-10-19 — POST-v1 SOURCE RELEASE:** Default branch is `master`; the immutable `v1.0.0` [pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0) points to commit `07ce51d2022ab5673a7a27e744e5e5757fbb3d08`. [Kiosk CI](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245): 235 tests (233 PASS, 2 SKIP), 87 synthetic renders/0 errors; [Dither CI](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273): 48 tests PASS. This is **source/CI evidence, not Windows production or hardware certification**. FEAT-001 DEMO pricing/copy count and FEAT-003 live-preview mirror have owner-tested PASS; BUG-011 monitored; BUG-001/007 speaker/audio retests pending; BUG-009 Drive 30-day cleanup remains OPEN. Real QRIS FEAT-020 and receipt scanner FEAT-002 are not implemented. Dated pre-release statements below are historical when superseded by this notice.

**Reconciled: 2026-10-19 | Current baseline: `master` / `v1.0.0`**  
This status is based on reading selected source files and the latest owner device reports; **no new tests or hardware checks were performed during documentation housekeeping**. Automated/historical test passes are not proof of current Windows booth acceptance.

Status vocabulary: **IN SOURCE** = relevant implementation found, **OWNER REPORTED** = physical observation requiring reproducible evidence, **UNVERIFIED** = no current hardware acceptance, **PLANNED** = not implemented, **BLOCKED** = operational defect. For feature approval/requirements, see [DECISIONS.md](DECISIONS.md) and [next_step.md](next_step.md).

## Latest automated quality gate — Kiosk GUI Regression PASS

**Historical pre-release full CI (retained):** [Kiosk GUI regression Actions 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762) **SUCCESS**, tested SHA `c40f33f5`: `232` unittests (**230 PASS / 2 SKIP / 0 FAIL / 0 ERROR**), Python compilation PASS, **87 synthetic desktop screen renders / 0 errors**. Previous pipeline FAIL was investigated using the new diagnostics runner; 17 initial assertion failures were resolved in **test/CI code only**, to reflect approved FEAT-001 pricing/sessions, ad → tutorial navigation, actual Settings submenu and per-tap music auditions, safe print completion and simulated Windows queue selection. **No runtime `photobooth/` source changed** during this quality-gate repair. [Detailed CI evidence](qa/KIOSK-GUI-REGRESSION-2026-10-18.md).

**Release distinction:** the historical GUI suite was green **at its tested commit**, and the v1.0.0 suite also passed independently; no claim of real-camera, audio speaker, thermal paper, customer-data retention or actual QRIS settlement acceptance. The owner's separate FEAT-001/BUG-011 and FEAT-003 physical PASS statements remain in force; BUG-009 cloud-photo retention and BUG-001/007 audio remain unchanged. The later documentation-only baseline `c40f33f5` also completed CI successfully. This reconciliation adds documentation commits only; verify their own Actions checks separately.

## Historical FEAT-011 isolated dithering experiment (superseded integration status)

> **HISTORICAL / SUPERSEDED:** This lab originally ran on a separate experiment branch. It was subsequently merged into `feature/kivy-gui`, and the owner-approved Floyd preprocessing preset is now the default photo print behavior. Lab JSON presets are still standalone. Any below statement that the experiment is *not* in the kiosk describes the **pre-merge snapshot**, not current source.

**Current follow-on source:** `tools/dither_compare_gui.py` provides one-screen three-way comparison, independent/sync slider tuning, real-time 1-bit previews, zoom, parameter JSON and exact-raster export. `photobooth/dither_print.py` supports **operator-confirmed** physical Print Test per lane/Print All with no second dithering or uncertain automatic retries. [Stage 2 CI](https://github.com/pratikto/PhotoBooth/actions/runs/39112358484) and [Stage 3 CI](https://github.com/pratikto/PhotoBooth/actions/runs/39112474748) passed targeted automated checks. Windows UI and printer-paper behavior **NOT VERIFIED**; no production kiosk changes.


With explicit owner approval, the separate [FEAT-011 thermal dithering lab](dither-tuning-lab.md) has been added **only to this experimental branch**. It uses `photobooth/dither_lab.py`, `tools/dither_tuning_gui.py`, and `tests/test_dither_lab.py`. The GUI can preview and export grayscale-tuned 1-bit PNGs, and save/load JSON lab presets, without using the physical printer. [Dedicated GitHub Actions run 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) passed compile and targeted unit tests. **No Windows GUI/device validation; no production print pipeline change; BUG-004 remains OPEN.** This section must not be mistaken for a feature released in `feature/kivy-gui` or `main`.

## Owner-approved default photo dithering (2026-10-18)

Three-way lab source and docs were fast-forwarded into `feature/kivy-gui`. The user selected Floyd–Steinberg at 576 dots (brightness 0.652, contrast 2.104, gamma 2.352, sharpness 2.073); `photobooth/printer.py` uses that tuning by default for ordinary Floyd photo jobs. `PHOTOBOOTH_PHOTO_TUNING=legacy` safely selects the old processing path; non-Floyd modes, explicit comparison jobs and the QR payment slip have no new tuning. **Physical quality and broader kiosk acceptance still need owner testing; BUG-004 remains OPEN.**

## Current implementation vs reported device behavior

| Feature / concern | Current source / observation | Acceptance status |
| --- | --- | --- |
| Kivy Meong GUI, branding, 12 cyclic 80 mm templates, capture/3-photo session, review/retake | Implemented in `ui_kivy.py`, `catalog.py`, `workflow.py`, `app.py` | IN SOURCE; end-to-end device regression incomplete |
| **FEAT-003 — mirrored live capture preview** | `ui_kivy.py::_new_display_texture(mirrored=True)` flips Kivy GPU horizontal UVs; both first Pillow `update_live_preview` and OpenCV BGR `update_live_frame` use it. Original camera, face/palm input, JPEGs, review/result, thermal print and QR graphics remain unmirrored by design. | **IN SOURCE — OWNER TESTED PASS (2026-10-18)**: "sip udah sesuai. PASS" after Windows camera verification. Dedicated [synthetic mirror CI 39139208320](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320) PASS. No exact local SHA or per-case physical evidence; full GUI synthetic CI now PASS; full hardware/release signoff remains separate. Future FEAT-002 receipt scanner/overlay still absent and not tested. |
| FEAT-001 DEMO pricing: **Rp5.000 per selected template/3-photo session + Rp5.000 per requested copy**; BUG-011 physical copy count | `catalog.py` defines fees; `workflow.quote_order` / `build_session_plans` calculate one capture per selected template; GUI/cart and manifest agree; `app.py` submits **one multi-copy transport batch** and `printer.py` concatenates N identical ESC/POS image+cut streams. Windows `EndDocPrinter` now correctly finalizes the RAW job. | **IMPLEMENTED IN SOURCE; OWNER TESTED PASS (2026-10-18)** for actual pricing **and physical printed-copy quantity**; owner explicitly reconfirmed **"bug 11 udah aku test dan lolos"**, after an earlier BUG-011 failure. Targeted FEAT-001 CI [39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) **15/15 PASS** (11 price/manifest + 4 mock RAW tests). **BUG-011 MONITORING**, not CLOSED/RELEASED; individual device counts and tested local SHA unspecified; historical Kiosk CI FAIL [39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) has been **SUPERSEDED by full PASS [39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762)**; synthetic QA remains separate from owner paper evidence. [Full QA evidence](qa/FEAT-001-BUG-011-acceptance.md). No live QRIS. |
| Initial idle ads, face-trigger invitation, tutorial-before-template | `advertising.py`, `face_presence.py`, `ui_kiosk.py` and Kivy flow | IN SOURCE; **OWNER REPORTED PASS** for navigation (BUG-005); retain regression coverage |
| Video advertisement files on idle and payment | Local playlist/automatic `ad_video/` discovery implemented; video playback/texture depends on local codec/media | **OWNER REPORTED PASS** for both placements (BUG-002); regression required after changes |
| Larger opening advertisement area | GUI sizing changes in source | **OWNER REPORTED PASS** for layout/sizing (BUG-006) |
| Application music and interaction sounds | `audio.py` now explicitly restarts music at full gain after ad fade and on `Uji Musik`; `ui_kivy.py` isolates preview sample from generic button cue | **PATCHED IN SOURCE, NOT PHYSICALLY VERIFIED**: music remains owner-reported silent on tutorial/layout (BUG-001) until Windows retest; SFX shutter/button and `Uji` taps OWNER REPORTED PASS (BUG-007) |
| Demo payment QR + payment advertisement + optional QR print invitation | Demo gateway and QR interface, timed non-modal prompt in `ui_kiosk.py` | IN SOURCE; **no real QRIS gateway**. Owner confirms payment video (BUG-002) plays |
| **Real provider-authorized QRIS settlement (FEAT-020)** | `photobooth/payment.py` currently uses a deliberately **non-payable** DemoPaymentGateway; no provider, signed confirmation or real merchant settlement integration exists | **PLANNED / execution P3 LOW / deferred by owner (2026-10-18)**; **FEAT-001 DEMO pricing/copies is the explicitly approved exception and owner-reported working**; FEAT-007 paid recovery remains deferred. Never treat DEMO paid as live |
| Thermal **photo strip** printing | `printer.py` and `printer_settings.py` are integrated into the GUI branch: Windows RAW (with `EndDocPrinter`), LAN/Wi-Fi/USB, Floyd–Steinberg/Bayer/threshold; multi-copy handled as one image+cut RAW batch | **OWNER REPORTED PASS** for Floyd photo quality (BUG-004) and now physical **copy counts (BUG-011)**. Retain full formal paper/regression signoff and no-auto-retry on uncertain sends; tests are not physical paper verification |
| Payment QR-slip printing | `qris_print.py` uses GUI-provided saved `PrinterConfig`; chooses LAN/Wi-Fi/Windows USB as available; keeps legacy LAN fallback for standalone callers | **OWNER REPORTED PASS** for physical QR print (BUG-003); QR scannability unverified |
| Local transaction manifest and folder counter | `transaction_store.py` records photo-session manifests and output | IN SOURCE; **not equivalent** to FEAT-007 future robust paid-state/print recovery, nor live QRIS integration |
| Photo Drive upload, folder QR, retention | Local manifest/retry queue and retention code exist; target local 15 days, Drive 30 days | IN SOURCE; Google configuration/live service not acceptance-tested. Local bytes may expire despite failed upload; review digital-delivery commitments |
| Real QRIS (FEAT-020), merchant POS/payment verification and receipt promotions | No trusted paid callback, settlement provider or live merchant integration | **PLANNED / execution P3 LOW**; **FEAT-001 DEMO tariff is already in source and owner-reported accepted**, not live pricing/settlement. FEAT-003 camera mirroring remains independent |
| Multi-theme, remote Drive ad management by machine, subscription/ad-slot enforcement, ordering launcher/demo | Not present as delivered production capabilities | PLANNED (FEAT-004/005/006/019), subject to approval and prerequisites |
| Android packaging, unattended fleet administration | Not verified | PLANNED / separate investigation |

## Device-reported defects — latest owner feedback

1. **BUG-001 ACTIVE:** Owner confirms tutorial/layout background music is silent while button and shutter SFX work; native provider reports play with nonzero gain. Music retry after ad fade and test preview patched in source; real speaker retest pending.
2. **BUG-007 PARTIAL OWNER PASS:** All three test buttons register and effects play; sample isolation and actual music audition patched in source. Confirm on Windows after update.
3. **BUG-004 OWNER REPORTED PASS:** Owner previously accepted the tuned Floyd paper image quality. **BUG-011 OWNER TESTED PASS — MONITORING:** user expressly states BUG-011 was tested and passed on Windows after the RAW spool/EndDocPrinter fixes. Per-case count logs and local tested SHA absent; do not mark formally CLOSED.
4. **BUG-002 / BUG-003 / BUG-005 / BUG-006 OWNER REPORTED PASS:** Ad videos, printed payment QR paper, required tutorial navigation and ad sizing accepted by owner; keep regression tests and retain historical incidents.

See [bug_tracker.md](bug_tracker.md) for source-of-truth severity/status, not this descriptive list.

## Historical implementation and QA notes (2026-10-17; NOT current acceptance)

The following chronological notes are retained to preserve past test reports and debugging context. They may describe earlier revisions or planned tests. **Where they conflict with the table above or newer source, the table above is the current reconciled interpretation.** Reports of tests passing cannot override later user-observed failures.

## Audio bug update — 2026-10-17

User reports both Meong music and advertising sound remain silent. The three originally supplied sample advertisement videos were previously recorded as having no audio stream; a silent source must not be treated as a decoder audio failure. The music problem remains unresolved on the actual booth. Check persisted levels, environment flags, Kivy/SDL2 audio-provider startup, native playback state and operating-system output routing before applying another speculative code fix.

## Fade-in regression correction — 2026-10-17

User Windows/Python 3.12/Kivy 2.3.1 test result: 13 tests, 1 failed and 1 optional native audio test skipped. The failure was `test_music_autostarts_when_advertising_fades_into_tutorial`: music incorrectly entered `play` while fade gain was still 0. `_ensure_music` now guards against starting when `_music_mix <= 0`, allowing the fade callback to start playback only once volume rises. Re-run tests on the user's machine; this is a source fix, **not yet confirmation of audible output**.

## User Windows audio test results — 2026-10-17

User ran `python -m unittest tests.test_audio -v` after fade-gain fix: **13 tests run, 12 passed, 1 optional native test skipped, 0 failures**. Then enabled `PHOTOBOOTH_TEST_AUDIO=1` and ran the native provider test: **1 passed**, with Kivy 2.3.1, Python 3.12.10 on Windows, ffpyplayer 4.5.3, and all five WAV files loaded through `SoundSDL2`. This verifies provider initialization and API playback state, **not audible sound on the selected speakers**. User must still confirm whether tutorial music and Settings Uji playback can be heard; silent sample advertising videos also require a separately audio-bearing test clip.

## Diagnostic script import correction — 2026-10-17

The first attempt at `python tools/check_audio_output.py` stopped with `ModuleNotFoundError: No module named 'photobooth'` before any music playback, because direct script execution excluded the repository root from `sys.path`. Fixed the script to insert its checkout root. The user's report of no sound from that attempt does **not** establish an audio-device failure. Rerun after pulling and report output and whether 5 seconds of audio are audible.

## In-app diagnostic update — 2026-10-17

User confirms `python tools/check_audio_output.py` makes audible music, whereas `python main.py` remains silent. Therefore SDL2 can deliver audio on their machine; actual app audio is **not fixed**. Added a live Settings diagnostic line showing `provider`, `state`, `gain`, persisted `level`, fade `mix`, `advert`, `paused`, `started`, number of loaded `sounds` and `enabled`. Reproduce with Settings open on **tutorial** and report the complete diagnostic line and whether `Uji` is audible. `advert=1` on the opening advertising screen is expected (app music suppressed); a silent source MP4 has no ad audio to output. Do not claim audible application music until user confirms.

## HISTORICAL — Cross-branch printer integration staged on 2026-10-17 (superseded by v1)

The active Kivy GUI branch now includes printer transports, Windows RAW spooler,
saved GUI printer configuration, printer settings/test controls, automatic
result-image printing via a worker, manual reprint and three dithering modes.
Preserved recent advertising/tutorial/payment code; older printer branch
remains unchanged for backup. New printer tests are present but the complete
merged integration test suite and real Kivy rendering have **not been run**.
Physical printer testing is also outstanding and in-app audio remains
unresolved. PR #3 **was subsequently merged to `master` on 2026-10-19**. This sentence replaces the original pre-merge warning; see release notes.

## Windows USB field feedback — 2026-10-17
Physical `Out-Printer` text worked earlier with POS80ENG/USB001, but the Kivy
photo result returned `/dev/usb/lp0 not found`. This demonstrates that no
Windows queue was selected in the active saved runtime configuration; it does
not establish a failed cable or Windows print driver. The printer transport now
gives explicit Windows Settings instructions instead of a misleading Linux path
when the Windows queue is empty. Configure **Settings > PENGATURAN PRINTER >
USB Windows > POS80 Printer > SIMPAN**, then run **TEST PRINT**, inspect paper,
and only then test a full strip. The ffpyplayer MP4 image-load error is a separate
unresolved advertising issue. Raster profile width warnings are not transport
failures. No physical RAW print success is claimed.

## Shared printer route for payment QR — 2026-10-17

Confirmed Windows POS80ENG printing of completed photo strips by the operator.
The payment-page QR receipt previously used a separate LAN-only setting
(`PHOTOBOOTH_PRINTER_HOST`), so it showed a *preview only* even when photo
printing through the new saved Windows USB printer worked. The payment QR
worker now obtains the saved `PrinterConfig` from the GUI/controller for each
print, using LAN/Wi-Fi/Windows spooler consistently with photo strips. It keeps
the original active payment attempt and payload; rendering remains one-bit with
a QR quiet zone, and no duplicate automatic retry is introduced. The existing
legacy standalone LAN configuration remains as a fallback for direct worker
callers and historical tests. New mocked Windows spooler test included. Physical
payment QR printing/scannability still needs operator verification.

## Audio Settings input diagnosis — 2026-10-17

Operator reports both Music and Button **Uji** controls not responding and no
terminal feedback. Added an explicit audio-test tap handler, a persistent
on-screen "Uji ... tombol diterima" indicator, console logger, and more
responsive ScrollView touch thresholds. This distinguishes a Kivy popup touch
delivery issue from the unresolved native mixer silence. Actual speaker output
and button usability still require a Windows GUI test; no audible success is
claimed. If the indicator updates but speakers are silent, capture the
provider/state/gain/mix diagnostic in the same popup.


## FEAT-022 — Owner-approved isolated portrait GUI v2 initial source (2026-10-21)

**IN SOURCE ON feature/portrait-kiosk-gui; NOT TESTED/RELEASED.** The user approved a greenfield customer-facing GUI plus an independent audio lifecycle, based on master SHA 27f3801b, and specifically requested a new branch. Initial files: kiosk_v2/flow.py (tutorial completed once per visit), audio.py (separate WAV-only page music and SFX lifecycle), theme.py and app.py (Pixel Arcade Space portrait Kivy advert/tutorial/12 real template previews, copy-count demo quote, inline invitation preview), and tools/run_portrait_v2.py (opt-in launcher). Existing main.py/v1 remains untouched. The game-entry button opens an **explicit unavailable notice**, not a working mini game. The face invitation is operator-triggered preview, not live detection. Checkout, payment, real cafe POS, camera, photo printing and Drive integrations are NOT implemented in this v2 prototype. CI regression workflow/test code committed, execution and Windows 10.1-inch visual/audible acceptance pending. No master merge. See portrait-kiosk-v2.md.

### FEAT-022 P0–P2 synthetic QA update — 2026-10-21

[Portrait CI 39522764587](https://github.com/pratikto/PhotoBooth/actions/runs/39522764587) succeeded: **16/16 pure navigation/audio tests**, Linux/Xvfb Kivy interactive widget smoke, 12 validated screenshots (6 pages at both 800x1280 and aligned 452x900). These are **source / virtual-display PASS**, NOT audible Windows music acceptance or an integrated paid photobooth. Status remains **PARTIAL IN SOURCE / DEVICE QA PENDING**. [Legacy v1 Kiosk CI 39522083946](https://github.com/pratikto/PhotoBooth/actions/runs/39522083946) previously ran 252 tests (250 passed / two skipped), 87 renders; current new branch must still be physically tested and polished. The repaired screenshot renderer avoids unreliable 450px RGB row packing in Linux and does NOT certify Windows touch. DO NOT MERGE pending owner review.


## FEAT-022 — portrait GUI v2 follow-up branch: PCM audio provider hardening (2026-10-21)

**IN SOURCE / DEVICE QA PENDING.** `feature/portrait-kiosk-v2-next` was created from `feature/portrait-kiosk-gui`, leaving the existing working scaffold and `master` untouched. Native SDL2 gets first chance at desktop PCM WAV playback (unless `KIVY_AUDIO` explicitly overrides it), with length-verified provider fallback and failure detection when playback remains stopped. New mocked regressions are committed. **Exact-branch CI is now verified at source-and-artboard SHA 6e7f29a7** ([run 39548798578](https://github.com/pratikto/PhotoBooth/actions/runs/39548798578): 21/21 Python tests, Kivy widget smoke, 12 synthetic screenshots, two jobs SUCCESS). **Actual Windows audible-speaker and physical touchscreen acceptance remain PENDING.** The previously reported BUG-001/007 music issue is **not marked resolved**; this change only affects opt-in v2. Game, live QRIS, camera, printing and Google Drive are not yet connected to v2. Detail: [portrait-kiosk-v2.md](portrait-kiosk-v2.md); source commits `2b743da0` and `caad0e0d`.

## FEAT-022 — comprehensive visual/source reconciliation (2026-10-21)

**DOCS + ART ASSETS COMMITTED ON feature/portrait-kiosk-v2-next; NO NEW PHOTO/TRANSACTION CODE IMPLEMENTATION.** The two last owner-approved 1672×941 artboards are now versioned as [main UI](assets/portrait-v2/meong-main-flow-approved.webp) and [Meong Fly](assets/portrait-v2/meong-fly-revised-approved.webp) (compressed high-quality WebP, [provenance/checksums](assets/portrait-v2/README.md)). [Canonical FEAT-022 specification](portrait-kiosk-v2.md) embeds both, while [the visual screen-by-screen spec](portrait-kiosk-v2-visual-spec.md) documents how user-approved flow corrections override misleading sample arrows in the artwork. [Technical design](portrait-kiosk-v2-technical-design.md) differentiates implemented modules from future service adapters.

**Current opt-in portrait v2 application pages:** advert (real local advertisement player, direct photo and mini-game CTAs), tutorial (mandatory and only once per visit), templates (12 actual approved strip previews, copy quantity and DEMO quote), and game_preview (truthful unavailable notice). Face invitation is **manual-only inline preview**, not a live detector integration. No actual game, real cafe scanner, win-discount checkout, QRIS, v2 camera capture/review, printer or Drive fulfillment code is connected. **Legacy master PhotoBoothApp is unchanged.**

**Verified branch-specific synthetic quality gate:** [GitHub Actions 39548798578](https://github.com/pratikto/PhotoBooth/actions/runs/39548798578), source-and-approved-mockups SHA **6e7f29a769b2ca19d09efa99b3bef21fb7b8bc86** — Python compile PASS, **21/21 pure navigation + audio-provider tests PASS**, Kivy widget smoke PASS, **12 synthetic screen renders** (six UI states at 800×1280 and 452×900), two workflow jobs SUCCESS. Previous [39522764587](https://github.com/pratikto/PhotoBooth/actions/runs/39522764587) belongs to the prior working branch and is historical. New documentation-only commits do not change the application files under test. No physical Windows/speaker, 10.1-inch touch, ad video sound, face camera, print/paper, Midtrans Sandbox, receipt POS or Google Drive acceptance is claimed.

**Design decisions, NOT SOURCE:** same idle/face-invitation surface contains both CTA options; a dedicated mini-game intro precedes receipt input; result of Win/Lose goes to tutorial only if unseen, then the original template gallery; no replay after a consumed receipt; potential Rp2.500 discount must be verified and shown at cart/checkout later. Avoid competing cafe receipt promotions until the owner defines stacking rules. One chosen template prints an 80×240mm strip with three photos and a separate photo-download QR; a payment QRIS is never placed on that strip. See [DEC-022](DECISIONS.md), the [approved artwork](assets/portrait-v2/README.md), and [backlog](next_step.md).

**Next acceptance before photo/backend integration:** owner Windows audio speaker + video sound and actual portrait touchscreen QA, accurate pixel-arcade visual parity to both artboards, then separately approved adapter integration plus regression. Keep BUG-001/007 and BUG-009 unresolved; no master merge without explicit owner approval.

## FEAT-022 — P2.5 true GUI source progress (2026-10-21)

**IMPLEMENTED IN ISOLATED SOURCE / SYNTHETIC CI PASS / DEVICE QA PENDING.** On `feature/portrait-kiosk-v2-next` the earlier simple prototype now has a decorated Pixel Arcade Space starfield, native stateful arcade buttons, **four Kivy-drawn tutorial illustrations**, an ad-primary idle/invitation with both Foto and Meong Fly entry plus Cara Pakai, an actual **three-preview carousel** of the 12 authorized vertical strip masters with horizontal swipe support, and a **dedicated responsive Meong Fly intro** showing the one-struk/one-attempt concept and a potential Rp2.500 win reward. Scan Struk remains **disabled**; there is NO receipt validation/gameplay/discount/granted QRIS. The existing four ViewFlow route names, once-per-visit tutorial guard, real ad decoder and DEMO template quote stay intact; `python main.py` and master have not changed.

**Verification:** [CI 39555036023](https://github.com/pratikto/PhotoBooth/actions/runs/39555036023), code/test SHA `c4e4703a`: two jobs SUCCESS; Python compile and **21/21** audio/navigation tests PASS; updated Kivy widget smoke PASS; 12 rendered screenshots at 800×1280 and aligned 452×900 PASS. Previous intermediate test failures on [39edb3ab](https://github.com/pratikto/PhotoBooth/commit/39edb3ab4f8a9b7f126258be9ed19b7512cbf43a) occurred because the old widget test still expected only one preview texture; test logic was correctly updated for three adjacent real preview textures and the current commit is green.

**Still unimplemented/untested:** physically audible Windows speakers/video audio and touch/swipe, real face trigger, QRIS/Sandbox, cafe POS/scanner, full gameplay, capture/retake, printing and Drive delivery from the v2 GUI. Continue checking [visual design requirements](portrait-kiosk-v2-visual-spec.md) and [P2.5 scope](portrait-kiosk-v2.md); do not call this an end-to-end release.
