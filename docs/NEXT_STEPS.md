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

**D. Enforce ad -> tutorial -> layout picker.** Update navigation for manual Start and face-invitation acceptance; preserve back navigation, timers and audio transitions. Use regression tests to prohibit accidental direct ad -> layout routing.

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
