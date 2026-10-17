# Meong Photobooth — Verification and Regression Checklist
Updated: 2026-10-18 | Branch: `feature/kivy-gui`

**All items are UNVERIFIED for this documentation-only change.** Previous historical tests are described in [docs/FEATURE_STATUS.md](docs/FEATURE_STATUS.md), not treated as current passes.

## Test run metadata
- Commit SHA / date / tester / OS / Python / Kivy versions:
- Camera / speaker / printer / network / media configuration:
- Commands, output, logs and screenshots:
- Known limitations and blocked cases:

## Core functional smoke tests
- [ ] Startup from clean launch without fatal error
- [ ] Idle image and compatible MP4 ads render and rotate
- [ ] Face stable 5s shows offer; 15s timeout and cooldown work
- [ ] Manual Start and face acceptance open tutorial before picker
- [ ] Tutorial -> cyclic layout selection -> cart/quantity works
- [ ] Demo payment QR visible; real payment never falsely claimed
- [ ] Payment ad video visible and muted; optional QR print offer does not cover QR and expires
- [ ] Camera live preview, timer, 3-photo capture, review/retake work
- [ ] Selected layout composition and result screen work
- [ ] Photo thermal print, manual reprint, paper alignment and legibility verified physically
- [ ] Payment QR slip print physically legible and scannable (separate from photo print)
- [ ] App music starts after idle advertising; video/audio ownership and effects work
- [ ] Settings music/SFX test buttons respond and volumes persist across restart
- [ ] Drive sync and local/remote retention tested in configured environment
- [ ] App returns to idle safely after finish, cancellation, timeout and recoverable errors

## Failure and recovery
- [ ] Camera disconnect/reconnect
- [ ] Printer offline/out of paper and retry without unintended duplicate prints
- [ ] Missing/corrupt advertisement media
- [ ] Payment timeout/cancel and duplicate transaction protection
- [ ] App restart mid-session and recovery/data integrity
- [ ] Network/Drive outage and later sync
- [ ] UI checks at 800x600, 1200x800, 1920x1080

## Regression commands (run, do not assume)
```bash
python -m unittest discover -s tests -v
python -m unittest tests.test_audio -v
```
Native audio tests may need documented opt-in environment flags. Record passes, failures and skips. A test reporting `play` does not prove audible sound.

## Release acceptance
- [ ] Acceptance criteria for approved FEAT/BUG IDs met
- [ ] Targeted and broad regression results recorded
- [ ] Physical device tests signed off by owner where relevant
- [ ] Blocking bugs resolved or explicitly accepted
- [ ] Rollback SHA and recovery steps recorded
- [ ] Owner explicitly authorizes release
