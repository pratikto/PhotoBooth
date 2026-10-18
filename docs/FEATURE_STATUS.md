# Meong Photobooth — Current feature status

**Reconciled: 2026-10-18 | Branch: `feature/kivy-gui`**  
This status is based on reading selected source files and the latest owner device reports; **no new tests or hardware checks were performed during documentation housekeeping**. Automated/historical test passes are not proof of current Windows booth acceptance.

Status vocabulary: **IN SOURCE** = relevant implementation found, **OWNER REPORTED** = physical observation requiring reproducible evidence, **UNVERIFIED** = no current hardware acceptance, **PLANNED** = not implemented, **BLOCKED** = operational defect. For feature approval/requirements, see [DECISIONS.md](DECISIONS.md) and [next_step.md](next_step.md).

## Current implementation vs reported device behavior

| Feature / concern | Current source / observation | Acceptance status |
| --- | --- | --- |
| Kivy Meong GUI, branding, 12 cyclic 80 mm templates, capture/3-photo session, review/retake | Implemented in `ui_kivy.py`, `catalog.py`, `workflow.py`, `app.py` | IN SOURCE; end-to-end device regression incomplete |
| Current pricing: **IDR 5,000 per quantity/session** | `catalog.py: PRICE_PER_SESSION=5000`; `app.py` total = `len(plans)*unit_price`; `workflow.py` expands quantity to multiple **independent 3-capture sessions** | IN SOURCE; future base-fee + per-copy model is PLANNED (FEAT-001) |
| Initial idle ads, face-trigger invitation, tutorial-before-template | `advertising.py`, `face_presence.py`, `ui_kiosk.py` and Kivy flow | IN SOURCE; **OWNER REPORTED PASS** for navigation (BUG-005); retain regression coverage |
| Video advertisement files on idle and payment | Local playlist/automatic `ad_video/` discovery implemented; video playback/texture depends on local codec/media | **OWNER REPORTED PASS** for both placements (BUG-002); regression required after changes |
| Larger opening advertisement area | GUI sizing changes in source | **OWNER REPORTED PASS** for layout/sizing (BUG-006) |
| Application music and interaction sounds | `audio.py` now explicitly restarts music at full gain after ad fade and on `Uji Musik`; `ui_kivy.py` isolates preview sample from generic button cue | **PATCHED IN SOURCE, NOT PHYSICALLY VERIFIED**: music remains owner-reported silent on tutorial/layout (BUG-001) until Windows retest; SFX shutter/button and `Uji` taps OWNER REPORTED PASS (BUG-007) |
| Demo payment QR + payment advertisement + optional QR print invitation | Demo gateway and QR interface, timed non-modal prompt in `ui_kiosk.py` | IN SOURCE; **no real QRIS gateway**. Owner confirms payment video (BUG-002) plays |
| Thermal **photo strip** printing | `printer.py` and `printer_settings.py` integrated in this **same GUI branch**, Windows RAW printer queue + LAN/Wi-Fi/USB routes; Floyd–Steinberg, Bayer, threshold in source | **OWNER REPORTED paper output works** on Windows POS80ENG, but blurry/poor print quality (BUG-004). No current comparison/quality acceptance |
| Payment QR-slip printing | `qris_print.py` uses GUI-provided saved `PrinterConfig`; chooses LAN/Wi-Fi/Windows USB as available; keeps legacy LAN fallback for standalone callers | **OWNER REPORTED PASS** for physical QR print (BUG-003); QR scannability unverified |
| Local transaction manifest and folder counter | `transaction_store.py` records photo-session manifests and output | IN SOURCE; **not equivalent** to FEAT-007 future robust paid-state/print recovery, nor live QRIS integration |
| Photo Drive upload, folder QR, retention | Local manifest/retry queue and retention code exist; target local 15 days, Drive 30 days | IN SOURCE; Google configuration/live service not acceptance-tested. Local bytes may expire despite failed upload; review digital-delivery commitments |
| Real QRIS/merchant POS verification, receipt-scanner promotions, new pricing, global camera mirroring | Not found as completed production features | PLANNED (FEAT-001/002/003; real partner integration deferred) |
| Multi-theme, remote Drive ad management by machine, subscription/ad-slot enforcement, ordering launcher/demo | Not present as delivered production capabilities | PLANNED (FEAT-004/005/006/019), subject to approval and prerequisites |
| Android packaging, unattended fleet administration | Not verified | PLANNED / separate investigation |

## Device-reported defects — latest owner feedback

1. **BUG-001 ACTIVE:** Owner confirms tutorial/layout background music is silent while button and shutter SFX work; native provider reports play with nonzero gain. Music retry after ad fade and test preview patched in source; real speaker retest pending.
2. **BUG-007 PARTIAL OWNER PASS:** All three test buttons register and effects play; sample isolation and actual music audition patched in source. Confirm on Windows after update.
3. **BUG-004 ACTIVE:** Physical thermal photo-strip output remains blurry/low quality. Not in scope of this audio-only implementation.
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

## Cross-branch printer integration staged — 2026-10-17

The active Kivy GUI branch now includes printer transports, Windows RAW spooler,
saved GUI printer configuration, printer settings/test controls, automatic
result-image printing via a worker, manual reprint and three dithering modes.
Preserved recent advertising/tutorial/payment code; older printer branch
remains unchanged for backup. New printer tests are present but the complete
merged integration test suite and real Kivy rendering have **not been run**.
Physical printer testing is also outstanding and in-app audio remains
unresolved. PR #3 targets `master` as a draft review/QA gate. **Do not report
the default branch as already merged.**

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
