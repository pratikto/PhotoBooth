# Meong Photobooth — Next steps / chat handover

**Repository:** https://github.com/pratikto/PhotoBooth  
**Target branch:** `feature/kivy-gui` (**do not create a new branch**).  
**Handover dated:** 2026-10-17.

## Resume checklist

1. Read this file, [Architecture](ARCHITECTURE.md), [Feature status](FEATURE_STATUS.md), [Decisions](DECISIONS.md), `README.md`, and `docs/advertising-and-qris.md`.
2. Fetch the **current** branch head and inspect working files before editing. Never assume older chat claims are committed.
3. Address reported defects **one by one** in small, reviewable commits. Keep detailed English comments. Do not modify the separate thermal-printer branch.
4. Run targeted unit tests, then broad regression suite and real Kivy screen checks; document commands/results and unverified physical tests.
5. Update `FEATURE_STATUS.md` and this file after each fix, then verify commit/push and link the resulting SHA.

## First coding tasks, in priority order

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

> Continue Meong Photobooth from GitHub repository `pratikto/PhotoBooth`, existing branch `feature/kivy-gui` only. Read `README.md` and all four handover docs in `docs/`, inspect current code and commits, then fix the first unresolved task in `docs/NEXT_STEPS.md`. Keep detailed English comments, run tests, commit and push directly to that branch, and update handover/status docs. Do not create a new branch or represent demo QRIS as live payment.

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
