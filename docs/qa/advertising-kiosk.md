# Advertising kiosk validation — 17 October 2026

Implemented on the existing `feature/kivy-gui` branch in separate, tested
uploads. No new branch was created and no original, converted or fixture video
was uploaded. The default playlist contains local still-image posters.

## Verification results

| Check | Result |
| --- | --- |
| Python suite, real Kivy widgets and native audio/video enabled | 162 tests: 160 passed, 2 optional native palm-model tests skipped |
| Apps Script retention regression | 12 passed |
| Real-widget renders at 800×600, 1200×800 and 1920×1080 | 87 passed; zero render errors |
| Painted payment QR, including print-offer/enlarged states | Decoded to the active attempt payload on every tested screen size |
| QR slip PNG and reconstructed ESC/POS raster at 384/576 dots | Decoded to the same payment payload; black/white pixels only |
| Native H.264/AAC video fixture generated during testing | Textures, payment mute, EOS to photo, duration and decoder retirement passed |
| Offline compressed face model | Loads without downloading; original XML SHA-256 matches the retained notice |
| Timezone fallback without an operating-system IANA database | Venue schedules and printed QR expiry pass using the `tzdata` dependency |
| Python compilation and whitespace | Passed |

The two skipped tests require the optional MediaPipe palm model and image
fixtures. Face presence is a separate bundled OpenCV model and its tests ran.

## Covered behavior

- Immediate advertisement opening, manual entry, five-second face invitation,
  fifteen-second dismissal and cooldown; stale/background observations cannot
  invite or reset browsing inactivity.
- Independent playlists, dates and overnight daily hours; corrupt media,
  fallback branding, video-load cancellation and coarse decoder-position
  accounting. Reports exclude paused and poster-only video time.
- Three-minute browsing timeout with a final warning, while payment/capture and
  the existing capture/retake/upload/result workflow retain their own lifetimes.
- Stable payment QR during ad changes and left-column print offers; pending
  QR printing preserves payload, amount and expiry even near expiration.
- Status timeout preserves the order and blocks unsafe renewal. Confirmed
  success advances once; expired renewal rechecks status before replacing QR.
- Single outstanding print job through result delivery, cancellation, invalid
  printer settings, unconfigured-preview mode and uncertain partial TCP sends.

These automated checks use synthetic camera frames, temporary transactions,
stub Drive/payment backends and controlled printer sockets. Physical paper,
booth lighting, speakers and the selected LAN printer still need an on-device
check. Payment remains a deliberately non-payable demo.

## Reproduce

Install `requirements.txt` and `ffmpeg`, then use the commands in
[advertising-and-qris.md](../advertising-and-qris.md#validation).
Run `node --test tests/test_apps_script_retention.cjs` for the JavaScript checks.
[advertising-report.json](advertising-report.json) retains the 87 render
records. The renderer regenerates full-size PNGs and advertising contact sheets;
GitHub Actions also retains these as its `meong-gui-qa` artifact for seven days.
