# Meong Photobooth — Current feature status

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
