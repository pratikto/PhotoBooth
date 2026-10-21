# FEAT-021 mirrored scanner — evidence

Tested source: `76761a72ec72eebe43022f25554e0847ac1584a1`, existing `feature/meong-flappy-challenge`, clean runtime source after GitHub fetch, 2026-10-21. Baseline `0f8b0a72928af9aaf5fb49bd5d4ce1182844e451`. Connector source tree matched local tested tree `62d4f42c31b63d6410674cf4b8168fb96638a8a8`.

Command: `KIVY_NO_ARGS=1 python -m unittest discover -s tests -p 'test_meong_fly*.py' -v`.

**98 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, Linux Python 3.12.14, Kivy 2.3.1, SDL2/Mesa llvmpipe, OpenCV 5.0.0. [Raw output](unittest-linux.log). Seven new scanner tests include real QRCodeDetector decoding a generated DEMO QR, unmodified source pixels, lifecycle/cancellation during blocking open, no repeated failed opens, live Kivy texture reuse, display UVs and actual rendered red/blue pixel mirror, explicit validation before receipt claim, Back/exit cleanup. No physical camera or Windows hardware exercised.

## Owner evidence kept separate

Prior Windows log supplied by owner: 91 total, **76 PASS / 15 SKIP**, Kivy unavailable to that interpreter; exact SHA absent. This is not 91 Windows passes. Later screenshots show Start, Scan (old decorative QR), Gameplay, Win, Lose and demo layouts in a desktop GUI. They establish displayed pages only; exact runtime SHA, complete test log, animation video and FPS remain unrecorded. They do not validate the new live scanner or constitute aesthetic sign-off.

## Required Windows checks

Use the existing `.venv-kivy` Python; run the full suite and launch `python -m photobooth.meong_fly_demo`. Record SHA and runtime versions. Enter Scan and verify live view, left-right mirror and unchanged aspect ratio. Show a QR containing a fresh `DEMO-...` token; it must fill the field without beginning gameplay. Validate once, then verify rejection after reuse/relaunch. Check unsupported merchant/URL QR feedback, manual entry, unplug fallback, Back before claim, and camera release after Back/Validate/exit. Resize portrait/landscape and inspect input/caret/performance. **All physical checks NOT RUN here**.

No real merchant eligibility, POS, discount or QRIS enabled. No image/video persistence/upload. Decoder reads unmirrored local frames. [Scope, interface and rollback](../../features/FEAT-021-scan-camera.md).

Rollback: revert `76761a72ec72eebe43022f25554e0847ac1584a1` on the same feature branch; retain receipt database. No master changes.
