# Meong Photobooth — Bug register

**Reconciled: 2026-10-18 | Branch: `feature/kivy-gui`**  
Authoritative registry of **user-reported operational defects**, not a list of assumed fixes. New IDs never overwrite existing IDs; severity is provisional until reproduction. No application changes were made during this documentation review.

**Severity:** S0 = unsafe/payment integrity/data loss/kiosk unusable; S1 = core customer session cannot be completed; S2 = material degradation or workaround required; S3 = cosmetic or nonblocking. Higher execution priority may be assigned to customer-flow failures even when individual severities remain provisional.

## Current bug queue — operational defects first

| ID | Latest report / observed impact | Severity | Source vs device status | Next action / evidence |
| --- | --- | --- | --- | --- |
| **BUG-001** | App background music and button/camera effects are silent on normal GUI entry; standalone `tools/check_audio_output.py` was audible on owner's Windows PC | S2 | **OPEN — owner device failure**; existing source fade-gain and diagnostics are not verified fixes | Compare app `provider/state/gain/level/mix/advert/paused/started` diagnostic after entering tutorial, OS mixer, actual output and volume. Distinguish intended mute on idle video from silence on tutorial |
| **BUG-007** | Settings **Music** and **Button** `Uji` buttons do not react; owner observed **no terminal callback notification** | S2 | **OPEN — owner device failure**; tap indicator/logger and touch fixes exist in source, not verified on device | Test pointer/touch callback delivery and `Uji tombol diterima` indicator, popup z-order/touch grabs and logger. If callbacks register but no sound, connect to BUG-001 |
| **BUG-002** | Video advertisements do not play on both **idle opening** and **payment** screens | S2 | **OPEN — owner device failure** despite unit/native fixture QA | Use a known-compatible local video with visible moving frames, inspect auto-discovery, decoder/provider, texture/frame rendering and lifecycle on *each* page. Source clips reportedly have no audio streams; absence of soundtrack alone is not proof of broken video decoding |
| **BUG-003** | Payment-page **CETAK QR** does not yield a physical QR slip although a composed photo strip has printed successfully | S2 | **OPEN — owner device failure**; `qris_print.py` appears wired to shared `PrinterConfig` in current GUI source | Record saved USB Windows queue/config, QR print-tap callbacks, spool file, `QrisPrinterWorker` status, Windows job log and actual paper. Verify scanner reads full QR quiet zone and exact **DEMO** payload; do not confuse this with customer folder QR |
| **BUG-004** | Physical thermal photo strip is **burik/buram** despite paper output | S2 | **OPEN — quality/legibility defect**; three dithering options exist in source but are not an accepted quality fix | Compare full-resolution composed PNG vs printer-native dots, configured `print_width_dots`, scaling before dithering, dark/contrast settings, paper/darkness, and printed comparison samples; retain settings and photographs of real prints. `media.width.pixel` warnings alone do not diagnose blur |
| **BUG-005** | Mandatory **ad → tutorial → template picker** should work for manual Start and face invitation | S2 (provisional) | **VERIFY** — route exists in source; no new report of a failed physical retest | Walk both paths, back/cancel, retry and face-offer timeout on booth; promote to OPEN/S1-S2 only if reproduced failure |
| **BUG-006** | Main idle advertisement video should occupy a visibly larger area while keeping controls and aspect ratio | S3 | **VERIFY** — sizing changed in source, actual rendered screen unconfirmed | Compare 800×600, 1200×800 and 1920×1080 live GUI with real video and manual Start, record screenshots |

**Ordering principle:** BUG-001/007/002/003/004 require owner-visible physical confirmation before closure; BUG-005/006 are validation tasks, **not newly proven failures**. Re-rank by operational impact, reproducibility and dependencies before any code fix. Photo printing **working** and QR print **not working** are separate verified-by-report observations, not contradictory outcomes.

## Known reproduction context (not independent verification)

- Environment in earlier reports: Windows, Python 3.12, Kivy 2.3.1, POS80ENG/POS80 Printer USB queue. Confirm active device name and persisted `data/printer_settings.json` at next test. Some earlier Windows logs referenced `/dev/usb/lp0` before printer settings were configured.
- Earlier sound probe `python tools/check_audio_output.py` was audible while normal `python main.py` was not. This narrows investigation to app lifecycle/routing, not proof of exact root cause.
- Earlier photo-print job physically yielded a Meong layout; it looked blurry. QR-slip print still failed in subsequent owner feedback.
- Historical QA reported native sound/video test passes using fixtures and mock devices, plus a local 172-test run with failures caused in part by local merge artifacts. Do **not** transfer these results to current device acceptance. See [FEATURE_STATUS.md](FEATURE_STATUS.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and [docs/qa](qa/README.md).

## Per-bug closure requirements

1. Reproduce and record: branch commit SHA, OS/Python/Kivy, media/device config, steps, expected vs actual, terminal output/screenshot or physical evidence.
2. Trace root cause; distinguish what source implements from what it does on actual printer/speakers/camera.
3. **Ask for explicit owner approval** before any code fix and commit; use one focused change with regression tests and rollback pointer.
4. Mark **FIXED IN SOURCE** only after code change; **VERIFIED** only after documented applicable tests including physical confirmation where needed; **CLOSED** only after owner acceptance.
5. Keep QRIS demo status explicit. A QR on paper or a demo button is never proof of money received.

## New bug entry template

### BUG-XXX — Symptom (stable ID)
- Severity S0/S1/S2/S3; priority and rationale; status OPEN/REPRODUCED/FIXED IN SOURCE/VERIFIED/CLOSED/BLOCKED:
- First reported / last reproduced; environment, target commit and device:
- Expected behavior vs actual:
- Reproduction steps and associated logs/images:
- Suspected area vs *proven* root cause:
- Dependencies / related FEAT IDs:
- Explicit fix approval, tests run, on-device verification and rollback commit:
