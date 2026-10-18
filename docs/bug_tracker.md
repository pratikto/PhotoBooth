# Meong Photobooth — Bug Tracker
Updated: 2026-10-18 | Branch: `feature/kivy-gui`
Reported symptoms are **not** independently verified resolutions. Cross-check [docs/FEATURE_STATUS.md](FEATURE_STATUS.md) and [docs/DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) against current code and hardware before changing status.

| ID | Symptom / evidence | Severity (provisional) | Status | Next verification |
|---|---|---|---|---|
| BUG-001 | App music/sound effects silent or Settings test controls unresponsive in full GUI; standalone diagnostic previously audible | S2 | OPEN / needs reproduction | Capture current logs, Settings diagnostic, sound levels, callback behavior and speaker output |
| BUG-002 | Ad video does not play on idle and payment screens | S2 | OPEN / hardware validation pending | Validate local media, decoder, playlist, frame output and payment mute |
| BUG-003 | Payment-page QR printing not working although photo-layout printing works | S2 | OPEN / needs reproduction | Distinguish payment QR slip path from photo printer path; capture exact error and configured transport |
| BUG-004 | Printed photo-layout quality appears blurry/poor | S2 | OPEN / quality investigation | Compare source image, resize, printer DPI, dithering and actual paper output |
| BUG-005 | Mandatory ad -> tutorial -> picker navigation needs device confirmation | S2 | VERIFY / source implementation reported | Check both manual Start and face invitation; ensure tutorial cannot be bypassed |
| BUG-006 | Main ad video sizing needs visual confirmation | S3 | VERIFY / source implementation reported | Inspect 800x600, 1200x800 and 1920x1080 |
 
These entries consolidate **user-reported issues and existing handover notes**; severities are provisional and should be revised after reproduction. No fix is approved by creating this tracker.

## Bug entry template
### BUG-XXX — Short title
- Severity S0/S1/S2/S3; status OPEN/REPRODUCED/IN PROGRESS/FIXED IN SOURCE/VERIFIED/CLOSED/BLOCKED
- First reported; environment and current commit SHA:
- Steps to reproduce; expected vs actual:
- Logs/screenshots; affected feature IDs:
- Root cause (only when proven):
- Fix approval; test evidence; hardware acceptance; rollback reference:
