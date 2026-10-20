# Meong Photobooth — Development handover

**Repository:** https://github.com/pratikto/PhotoBooth  
**Target branch:** `feature/kivy-gui` (**do not create a new branch**).  
**Handover dated:** 2026-10-17.

## Current lab continuation — Enhanced Dizzy (2026-10-21)

**Branch:** `feature/dither-tuning` only; no `master` merge or Kivy production printer edits. Owner approved sharing the existing conservative Enhanced Floyd preprocessing with both Dizzy algorithms, behind an **independent default-OFF checkbox** in the three-panel lab GUI. Latest operator guide: [dither-tuning-lab.md](dither-tuning-lab.md). The lab now saves v4 JSON, opens v1/v2/v3 JSON without enabling Enhanced Dizzy, preserves hidden Threshold, prints explicit Enhanced/Baseline labels on lab paper headers and exports named native 1-bit PNGs.

**Automated evidence:** [Dither lab GitHub Actions 39503134534](https://github.com/pratikto/PhotoBooth/actions/runs/39503134534) for code/CI SHA `80980f7ba`: compile PASS; 42 targeted tests PASS on Linux Python 3.12, including byte-level parity against the previous Enhanced Floyd recipe and both Dizzy variants. This is **not** Windows kiosk acceptance or physical photo quality verification. **Next on-device actions:** update branch, launch `python tools/dither_compare_gui.py`, compare Dizzy baseline vs Enhanced Dizzy on identical photographs/settings for both variants, compare against Enhanced Floyd, export PNGs, and explicitly confirm optional Print Test for actual thermal-paper quality. Record screenshots/settings/printed samples before choosing any default. No GPU/LUT implementation or further product change approved.

## Isolated owner-authorized experiment — `feature/dither-tuning` (2026-10-18)

The owner expressly requested a **NEW branch** specifically for configuration of dithering algorithms and tuning parameters, overriding the usual no-new-branch default **for this task only**. New branch `feature/dither-tuning` originates from `feature/kivy-gui` at `5e0a8980968430b85f04ebac1b6c1574c2191a69`. First isolated FEAT-011 source commit: [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229). Lab instructions in [dither-tuning-lab.md](dither-tuning-lab.md). [Dedicated CI 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) PASS (compile + targeted unit tests); Windows GUI, native printer output and quality still require owner verification. Kivy GUI app, printer transport and payment QR code are not modified. **Do not merge to `feature/kivy-gui` or `main` without new owner authorization.** This temporary exception does not authorize branching other features.

**FEAT-011 next steps:** test Windows `python tools/dither_tuning_gui.py`; compare actual saved photo PNG and zoomed raster using preset, export binary PNG; confirm the outputs on real paper (same width/brightness/density). Retain BUG-004 OPEN. Known BUG-008 (Settings hang) and BUG-009 (Drive retention deployment) remain unrelated active operational issues; building a standalone lab does not fix them.

## Current handover — reconciled 2026-10-18

**Read this first rather than treating the dated 2026-10-17 notes below as an active work order.** Source-of-truth documents:

- [Documentation index](README.md), [reusable development prompt](DEVELOPMENT_PROMPT.md), and root [README](../README.md) (current status banner and historical project setup).
- [DECISIONS.md](DECISIONS.md): owner-confirmed commercial/product behavior versus proposals.
- [FEATURE_STATUS.md](FEATURE_STATUS.md): actual source implementation versus user-reported physical acceptance.
- [bug_tracker.md](bug_tracker.md): operational defects and stable IDs.
- [test_checklist.md](test_checklist.md): evidence classifications and real on-device acceptance.
- [next_step.md](next_step.md): **one unified provisional feature queue** plus parked business ideas. Detailed old intake ranks are historical, not authorization.

**Current latest owner feedback (2026-10-18):** BUG-002 video in idle/payment, BUG-003 payment QR paper, BUG-005 tutorial route and BUG-006 opening ad size are **OWNER REPORTED PASS** and not in active fix queue. BUG-007 Settings test taps now receive events, button SFX and shutter SFX work, but `Uji Musik` emitted only the standard click; BUG-001 tutorial/layout background music remains inaudible while SDL2 reports `state=play gain=0.59`. The user explicitly approved targeted BUG-001/007 code+documentation changes. BUG-004 thermal print blur remains OPEN and outside the audio patch. Pre-existing CI full-suite run 39101639665 failed despite 87 successful synthetic renders. Audio change requires actual Windows speaker retest; do not infer physical pass from provider state.

**Current source verified by file inspection, NOT physical test:** `photobooth/printer.py` and `printer_settings.py` are already integrated into `feature/kivy-gui` with Windows USB queue/LAN/Wi-Fi and Floyd–Steinberg/Bayer/threshold. `photobooth/qris_print.py` receives saved GUI `PrinterConfig`; legacy LAN-only fallback is for direct callers. Payment remains a *non-payable demo*. `photobooth/catalog.py` still uses IDR 5,000 per independent session/quantity, and `workflow.py` captures 3 photos **per quantity**. Do not describe proposed per-copy pricing as working.

**Future direction is documented, not delivered:** FEAT-001 base fee + per-physical-copy pricing (still 3 captures per chosen session); FEAT-002A dummy external receipt scanner and FEAT-005A standalone ordering demo with automatic same-device photo promo; FEAT-003 mirrored live preview only; FEAT-004 per-machine local-first Drive ads; FEAT-006 GUI themes; FEAT-007–018 reliability, promotional reporting and fleet enhancements; BIZ-001/FEAT-019 sale of hardware with mandatory assigned Free/Business/Enterprise tier. Free remains commercially usable and all its ads belong to Meong; paid users may control some ads while Meong retains **unspecified** reserved slots on every tier. No paid-tier licensing, ad quota enforcement, merchant POS integration, or live QRIS is represented as shipped.

**Funding rule:** merchant pays the waived base-fee promotion only when redeemed; the settlement recipient is the Meong-operated booth owner or a separate sold-machine operator according to who funded the discount and the contract. Do not call every merchant reimbursement Meong revenue.

**Execution gate:** Bug reproduction, device evidence and documentation review first. Before implementing any fix or feature, secure **separate explicit user approval of that code scope**. Use only `feature/kivy-gui`, preserve the thermal-printer branch, avoid accidentally overwriting local Windows changes, run targeted tests + full regression after authorized code, and require real device/owner signoff for printing/audio/video. This housekeeping made **documentation edits only**.

## Audio scope authorized and applied — 2026-10-18 (BUG-001 / BUG-007)

- Base commit: `06dd977c06657c9b56e1de0ad18042b65515bd64`; changes on existing `feature/kivy-gui` only. Audio patch and paired tests/docs committed together; see branch history for the resulting commit.
- `audio.py`: full-gain SDL2 music restart after returning from ad fade, deliberate music audition that reacquires the mixer channel while honoring mute/paused/ad rules. `ui_kivy.py`: Uji buttons bypass the generic click and explicitly audition music, button or shutter; diagnostic text uses a real newline.
- Added unit and real-widget regression expectations. **Post-change CI for code SHA `b69d3837`:** [run 39104614520](https://github.com/pratikto/PhotoBooth/actions/runs/39104614520) had Python compile PASS, full `unittest discover` FAIL (exit 1, test identity not exposed in job log), GUI render PASS (87 renders, no reported render errors), visual summary PASS. The preceding baseline CI already failed the same broad test step; a targeted audio suite has not been independently verified. No Windows speaker verification performed by GitHub Actions.
- **New owner Windows audio-unit evidence (2026-10-18):** `python -m unittest tests.test_audio -v` = **14 run, 13 pass, 1 skipped, 0 failures** in 2.539 s; Windows with Python 3.12.10, Kivy 2.3.1. Includes PASS for both the fade-after-ad test and forced music-audition test. Native audio opt-in check was skipped. Working-tree SHA was not present in shared command output. This test evidence **does not prove speaker audibility**.
- Next owner test: verify `git status` / current HEAD, launch `python main.py`; idle ad -> tutorial -> layout (music must be heard without Settings); open Sound Settings and tap Uji Musik, Uji Tombol, Uji Efek kamera; verify each emits only its intended sound; test 0%/restored music volume, advert muted application BGM and next user round. Record both result and diagnostics if still silent.
- Next repair queue: BUG-004 thermal print blur and independent CI regression investigation only with their own approvals.

## Recommended next engineering investigations (historical 2026-10-18 list; now superseded by owner feedback)

1. Audio settings pointer/touch diagnostic (BUG-007) and application audio lifecycle (BUG-001), with logs distinguishing missed button events from mute/routing.
2. Idle/payment MP4 decoder and texture playback on actual Windows hardware (BUG-002). Test visible moving frames with supported codec; the user's original sample files were noted to lack audio streams.
3. Payment QR print worker and selected saved Windows queue (BUG-003). Collect worker result, spooler messages and paper; never claim successful print from an ESC/POS file alone.
4. Native-width source-to-raster photo quality comparison (BUG-004); compare existing dither modes and physical output, separate photo from QR printing.
5. Manually verify tutorial route, ad stage sizing and complete payment/capture/print flow (BUG-005/006), then revisit feature priorities.

## Resume checklist

1. Read [this updated handover](#current-handover--reconciled-2026-10-18), [Architecture](ARCHITECTURE.md), [Feature status](FEATURE_STATUS.md), [Decisions](DECISIONS.md), [Bug tracker](bug_tracker.md), [Feature backlog](next_step.md), [root README](../README.md), and [Advertising and QRIS](advertising-and-qris.md).
2. Fetch the **current** branch head and inspect working files before editing. Never assume older chat claims are committed.
3. Only after explicit owner authorization, address reported defects **one by one** in small, reviewable commits. Keep detailed English comments. Do not modify the separate thermal-printer branch.
4. Run targeted unit tests, then broad regression suite and real Kivy screen checks; document commands/results and unverified physical tests.
5. Update `FEATURE_STATUS.md` and this file after each fix, then verify commit/push and link the resulting SHA.

## Historical initial coding priorities (2026-10-17; superseded by current bug tracker)

**A. Video playback fails on both idle and payment (partial configuration fix committed 2026-10-17).** Inspect `ui_kiosk.py`, `advertising.py`, `requirements.txt`, ad playlist paths and Kivy video provider/ffpyplayer lifecycle. Distinguish absent local video media, failed decoder, texture not attached, muted media and stalled playback. Ensure payment playback is **muted**, not disabled. Add diagnostic logging and tests for both placements. The bundled playlist now auto-discovers video files from the repository-root `ad_video/` directory (alphabetical order, arbitrary filenames and supported extensions), for both placements. Still-image poster entries remain as fallback. Videos are NOT committed to GitHub; local decoder and actual playback remain to be verified. Custom `PHOTOBOOTH_AD_CONFIG` playlists remain explicit and do not use automatic discovery. Runtime decoder/frame testing is still outstanding; do not claim videos have been uploaded or playback fixed.

**B. Enlarge the initial ad area (source change committed 2026-10-17).** The idle page now uses up to 1920dp width, narrow gutters and a shorter header; video retains `contain` sizing, and Start/face-offer controls remain outside/on the stage. Real-widget render checks at 800×600, 1200×800 and 1920×1080 are still pending.

**C. Fix music initialization (fade-in fix committed 2026-10-17; device verification pending).** Trace `KivyHost.build/on_start`, `AudioManager.start`, initial advertising audio ownership and transition into the guide. Check why opening Settings appears to initialize playback. The audio fade now explicitly restarts music as volume rises from zero, without requiring Settings. Preserve intentionally silent application music while source-video advertising is active; verify this fix on the user's speaker and when entering tutorial/photo flow.

**D. Enforce ad -> tutorial -> layout picker (source change committed 2026-10-17; device QA pending).** Both advertising manual Start and face-invitation acceptance now open the illustrated tutorial. The tutorial's Start control continues to invoke the existing layout-selection controller. Regression coverage added in `tests/test_tutorial_entry.py`; test execution and hardware UI navigation verification remain pending.

## Acceptance criteria

- Both configured image and compatible local MP4 ads render/advance on idle and payment pages; payment ad audio remains muted.
- Idle video is visibly larger without cropping/distorting or hiding Start.
- Music begins on entry to tutorial/photo flow without touching Settings; user-selected mute is respected.
- Both Start routes lead to tutorial before the user can select a layout.
- Existing template/session/retake/QR demo/Drive flows and their tests continue to pass.
- Status and handover docs reflect **observed** behavior, not aspirations.

## Important limitations

Physical machine speakers, local media/codec setup, camera, Google Drive and LAN thermal printer cannot be validated from GitHub alone. Real QRIS is not yet supported. Previous automated QA results are historical, not validation of the four newly reported defects.

## Copy/paste into a new chat

The maintained full and quick prompts are in [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md). The compact starter below references that single canonical prompt rather than maintaining a divergent second checklist:

> Continue Meong Photobooth from GitHub `pratikto/PhotoBooth` on existing `feature/kivy-gui`. Follow `docs/DEVELOPMENT_PROMPT.md` and `docs/DEVELOPMENT_PROTOCOL.md`; read current `docs/DECISIONS.md`, `docs/FEATURE_STATUS.md`, `docs/bug_tracker.md`, `docs/test_checklist.md`, `docs/next_step.md` and `docs/DEVELOPMENT_HANDOVER.md`. Inspect current branch/SHA and relevant source. **Review only unless I approve a named documentation or code scope.** For approved development, record tests and link documentation/commit evidence before claiming a bug fixed. No new branch, merge or real QRIS claims without authorization.

## Current blocker: audio remains silent (reported 2026-10-17)

The prior music fade-in commit has **not** solved output on the user's machine. Do not mark audio done. The original three sample clips are documented as silent video sources, so test advertising sound with a **known audio-bearing video**. On the user's machine, collect console/Kivy provider logs, check `PHOTOBOOTH_AUDIO`, `KIVY_AUDIO`, persisted `data/audio/levels.json`, actual selected sound output, and run `PHOTOBOOTH_TEST_AUDIO=1` native Kivy test with the real output (not dummy SDL driver). Verify whether the music sound handle enters `play` on tutorial and whether it reaches audible output. Fix based on those observations, add targeted regression test and update status.

## Retest after fade-gain fix — 2026-10-17

A Windows test run reported 1 failure in `test_music_autostarts_when_advertising_fades_into_tutorial`: sound state was `play` instead of expected `stop` before gain increased. A follow-up change defers `_ensure_music` when `_music_mix <= 0`. Next run `python -m unittest tests.test_audio -v`; then run the opt-in native audio checks with `$env:PHOTOBOOTH_TEST_AUDIO='1'` and `python -m unittest tests.test_audio.AudioTests.test_real_provider_starts_music_and_loads_every_cue_from_a_fresh_install -v`. Clear this environment flag afterward. For advertising audio, test a video that genuinely contains an audio track. Report whether the tutorial song and Settings' Uji music are audible.

## Audio diagnostic update — Windows checks passed 2026-10-17

The user ran all standard audio unit tests: 12 passed, 1 opt-in native test skipped. The separately enabled native audio test passed and logs show all five WAV handles loaded via SoundSDL2, with ffpyplayer and SDL2 providers available. No assertion failures remain in these checks. This does **not** verify speaker output. Next obtain one direct observation from user: is the song audible when entering the tutorial and/or pressing `Uji Musik` in Settings? If still silent, check Windows Volume Mixer and current output device, user preferences, environment flags, and Kivy logs before more source changes. Advertising samples were documented as containing no audio track; verify with ffprobe or another known audio-bearing video.

## Speaker diagnostic — 2026-10-17

User confirms no audible music in the full app despite passing native provider tests. Added `tools/check_audio_output.py` to isolate SDL2 audio output without Kivy GUI/page ownership. Run `python tools/check_audio_output.py` from repo root, listen for five seconds, and inspect Windows Volume Mixer for Python and the selected device. If direct test sounds, investigate full-app audio lifecycle/mute settings; if it is silent, investigate Windows/SDL2 routing or device. Do not mark the bug fixed based on native `play` state alone.

## Diagnostic script import correction — 2026-10-17

The first attempt at `python tools/check_audio_output.py` stopped with `ModuleNotFoundError: No module named 'photobooth'` before any music playback, because direct script execution excluded the repository root from `sys.path`. Fixed the script to insert its checkout root. The user's report of no sound from that attempt does **not** establish an audio-device failure. Rerun after pulling and report output and whether 5 seconds of audio are audible.

## In-app diagnostic update — 2026-10-17

User confirms `python tools/check_audio_output.py` makes audible music, whereas `python main.py` remains silent. Therefore SDL2 can deliver audio on their machine; actual app audio is **not fixed**. Added a live Settings diagnostic line showing `provider`, `state`, `gain`, persisted `level`, fade `mix`, `advert`, `paused`, `started`, number of loaded `sounds` and `enabled`. Reproduce with Settings open on **tutorial** and report the complete diagnostic line and whether `Uji` is audible. `advert=1` on the opening advertising screen is expected (app music suppressed); a silent source MP4 has no ad audio to output. Do not claim audible application music until user confirms.

## Integration staging — 2026-10-17

The latest advertising/tutorial GUI is the integration base. Thermal printer
modules, saved settings, Windows RAW spooler, three dithering modes, operator
settings popup, test print callback and result-page print worker/reprint have
been copied and adapted to `feature/kivy-gui`. The separate printer branch is
kept as a backup; PR #2 shows the unmodified branch-to-branch merge conflicts.
Hardware tests are pending; the real video/audio bug remains unresolved.

**Do not delete old branches.** Before publishing to `master`, run
`python -m unittest discover -s tests -v`, launch `python main.py`,
verify entry via ad/tutorial, checkout demo and printer settings, and test
Windows RAW paper output. A successful print spooler job does not prove paper
output. Check UI screenshots at desktop resolutions and the persistent
`data/printer_settings.json`. Importantly, this branch now integrates printer
features from the older printer branch without replacing recent advertising
or payment behaviors.

## Windows QA feedback (2026-10-17)

User's local Windows `python -m unittest discover -s tests -v` reported
172 tests, four errors and 69 skips. Three printer import errors originate
from **local unresolved merge artifacts** (`<<<<<<< HEAD` in
`tests/test_printer.py`, and a 661-line `photobooth/printer.py` with an
unterminated string) rather than the current GitHub `feature/kivy-gui` files
(which contain no conflict markers and whose printer module has 625 lines).
Do not overwrite uncommitted local edits; inspect `git status`, abort only
an active unfinished merge/rebase if appropriate, then refresh the working
tree safely. The fourth error was a Windows permission restriction when
creating a symlink in the retention test; that specific `WinError 1314`
condition now skips the symlink-specific test while preserving other errors.
Re-run full and opt-in GUI tests before merging PR #3 into `master`.
