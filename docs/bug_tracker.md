# Meong Photobooth — Bug register

**Reconciled: 2026-10-18 | Branch: `feature/kivy-gui`**  
Authoritative registry of **user-reported operational defects**, not a list of assumed fixes. New IDs never overwrite existing IDs; severity is provisional until reproduction. No application changes were made during this documentation review.

**Severity:** S0 = unsafe/payment integrity/data loss/kiosk unusable; S1 = core customer session cannot be completed; S2 = material degradation or workaround required; S3 = cosmetic or nonblocking. Higher execution priority may be assigned to customer-flow failures even when individual severities remain provisional.

## Current bug queue — operational defects first

| ID | Latest report / observed impact | Severity | Source vs device status | Next action / evidence |
| --- | --- | --- | --- | --- |
| **BUG-001** | Music is still inaudible in tutorial/layout, despite `SoundSDL2 state=play gain=0.59`; button and shutter effects ARE audible in the same GUI | S2 | **PATCHED IN SOURCE — owner audio retest required**; 2026-10-18 code now reacquires music playback after ad fade and on explicit audition. Actual audible output unverified | On Windows pull updated GUI, start from idle ad -> tutorial -> layout, listen for continuous BGM without entering Settings; test music mute/re-enable and check output with `Uji Musik`. Preserve ad mute and SFX; record SHA, sound/mixer and device result |
| **BUG-007** | Owner now confirms all three `Uji` buttons receive taps: Music made only the generic click, Button made click, Camera made shutter. GUI reports accepted callbacks | S2 | **OWNER REPORTED PASS for tap handling; PATCHED IN SOURCE for sample isolation; physical retest pending** | Check `Uji Musik` audibly restarts music without a click, `Uji Tombol` one button cue, and `Uji Efek Kamera` one shutter cue. The playback-request status is not speaker confirmation |
| **BUG-002** | Video advertisements on both idle and payment now play according to owner | S2 | **OWNER REPORTED PASS — removed from active fixes**, formal closure needs version/evidence | Regression-check actual frames on both screens after audio change; payment stays muted |
| **BUG-003** | Owner confirms payment-page QR slip now physically prints | S2 | **OWNER REPORTED PASS — removed from active fixes**, QR scan and formal closure pending | Verify paper QR scans the intended DEMO payload, including quiet zone; no claim of live payment |
| **BUG-004** | Physical thermal photo strip is **burik/buram** despite paper output | S2 | **OPEN — quality/legibility defect**; three dithering options exist in source but are not an accepted quality fix | Compare full-resolution composed PNG vs printer-native dots, configured `print_width_dots`, scaling before dithering, dark/contrast settings, paper/darkness, and printed comparison samples; retain settings and photographs of real prints. `media.width.pixel` warnings alone do not diagnose blur |
| **BUG-005** | Owner confirms ad → tutorial → layout navigation is satisfactory | S2 (provisional) | **OWNER REPORTED PASS — no active repair** | Keep manual/face paths in later end-to-end regression |
| **BUG-006** | Owner confirms opening advertisement sizing/display is satisfactory | S3 | **OWNER REPORTED PASS — no active repair** | Recheck responsive layout on future visual changes |

**Ordering principle (2026-10-18):** Active work: BUG-001/007 audio, followed by BUG-004 print quality and the independently failing CI quality gate. Owner reports BUG-002/003/005/006 now work; retain these as historical records and regression coverage, not active fixes. BUG-001/007 patches require Windows speaker acceptance; do not infer a fix from SDL2 state or GitHub CI dummy audio.

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
