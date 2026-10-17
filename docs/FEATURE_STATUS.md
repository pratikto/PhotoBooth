# Meong Photobooth — Feature status

Snapshot: 2026-10-17, `feature/kivy-gui`. Statuses distinguish **implemented in source/docs** from **verified on the user's machine**. User-reported defects are open even if earlier automated QA passed.

| Area | Status | Evidence / limitation |
| --- | --- | --- |
| Kivy branded GUI, original Meong logo, animated pages | Implemented; on-device validation ongoing | `ui_kivy.py`, `ui_brand.py`, `ui_motion.py` |
| 12 cyclic template previews, quantity/cart at Rp5,000 per session | Implemented | `README.md`, `catalog.py` |
| Capture 3 photos/session, five-second timer, review, selected-photo retake | Implemented | `app.py`, `workflow.py`, `ui_kivy.py` |
| Optional palm-trigger shutter and face-presence invitation | Implemented; physical validation needed | `palm_gesture.py`, `face_presence.py` |
| Idle advertising and separate payment ad playlist (images/videos) | Automatic root `ad_video/` discovery implemented with arbitrary names; **playback still unverified on device** | `advertising.py`, `ui_kiosk.py`; local video files required; decoder and display remain to be tested |
| Larger main advertising video | **Expanded in source; desktop render not yet verified** | Idle page now uses up to 1920dp width, smaller gutters and header; aspect ratio still uses contain |
| Audio startup, independent sliders and effects | **User reports music still silent after fade-in fix; issue reopened** | Fade-in source fix alone did not resolve observed output; capture audio provider/OS mixer diagnostics |
| Idle ad -> mandatory tutorial -> layout picker | **Implemented in source; on-device testing pending** | Manual Start and face invitation now open guide first; guide Start leads to picker |
| Face invitation after stable 5 s; 15 s dismiss/cooldown | Implemented in source; verify behavior on hardware | Configurable kiosk timing |
| Demo payment QR, ad column and optional print-offer after 60 s | Implemented demo; not real QRIS | `docs/advertising-and-qris.md` |
| LAN ESC/POS payment QR slip | Adapter documented; physical printer unverified | Printer host defaults unset; preview is not printing |
| Physical photo print + Floyd–Steinberg/Bayer/threshold | Separate printer development branch | Do not assume merged into Kivy GUI |
| Google Drive folder queue and local sync, 15-day local/30-day Drive retention | Implemented in code and documented; credentials/service validation needed | Remote cleanup requires separate Apps Script setup |
| Live QRIS payment confirmation | **Not implemented** | No gateway is connected |
| Android packaging, real camera/audio/printer acceptance tests | **Not verified** | Hardware/environment dependent |

## Priority open defects from latest conversation

1. Videos fail to play on both initial advertising and payment pages.
2. Main/idle advertising video should occupy more screen area.
3. Application music does not start automatically; opening Settings triggers it.
4. Pressing Start from main ad must open the illustrated tutorial **before** layout selection.

No code change or physical test is claimed by this documentation update. See [Next steps](NEXT_STEPS.md).

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
