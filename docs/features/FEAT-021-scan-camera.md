# FEAT-021 — Standalone mirrored receipt-camera preview

## Authorization / baseline

Owner request 2026-10-21: "lanjutin dong.. tapi pas halaman scan qr tolong buka camera buat show capture cam buat scan struk nya ya. output video nya mirror ya."

Approved scope: standalone Scan camera preview, display-only mirror, QR reading into the existing DEMO input, fallback/manual validation, camera lifecycle, tests and synchronized documentation on existing `feature/meong-flappy-challenge`. Baseline `0f8b0a72928af9aaf5fb49bd5d4ce1182844e451`. No master merge, physics changes, POS verification, payment or actual discount.

## Behavior

- Enter Scan: open default camera index 0 in a background worker. Replace decorative QR with aspect-preserving live preview inside scanner frame. Display is horizontally mirrored; camera and QR decoder frames are not mirrored.
- QR decoding is real but supports only `DEMO-...` payloads (same prefix/length rules as manual input). No barcode/OCR/POS validation, URL navigation or network lookup. Ordinary cafe receipts cannot be authenticated with this implementation.
- A valid QR fills the text field and requests **VALIDASI DEMO 1X** / Enter. Decoding alone never claims a receipt or starts a game. Existing SQLite ledger rejects reuse and preserves one attempt.
- Invalid/unsupported QR displays a clear message. Manual input remains available when opening fails, camera disconnects or decoder fails. Re-enter Scan to retry a failed open.
- Back, successful validation, any non-Scan scene and app exit stop capture and clear preview. A still-opening/closing worker cannot launch a second camera handle. Driver shutdown occurs off the GUI thread; a hung driver can delay physical release, but does not stall the UI.
- No captured video/images are written to disk or uploaded. Only the existing DEMO ledger stores the explicitly validated token.

## Architecture and performance

New `meong_fly_scanner.ReceiptScanner` wraps the existing `photobooth.camera.Camera` without modifying production camera code. Camera open/close, RGB conversion, resize and OpenCV QRCodeDetector run off the Kivy thread. Mailbox retains one preview frame; decode at most every .25 s, preview at most 30 Hz, longest edge ≤640 pixels. Texture allocated only on first frame/resolution change and reused; mirror uses explicit UVs `(1,1,0,1,0,0,1,0)` on the display rectangle. No CPU flip or changed saved frame.

Standalone App opts into hardware; `MeongFlyStage(scanner=None)` stays hardware-free for art/QA fixtures. Tests inject synthetic scanner/camera providers. Existing requirements already include Kivy, OpenCV-contrib and qrcode; no new dependency added.

Files: `meong_fly_scanner.py` (new), `meong_fly_gui.py`, `meong_fly_polish.py`, `tests/test_meong_fly_scanner.py` (new).

## Acceptance / rollback

Automatic: actual synthetic QR decoding, raw pixels unchanged, cancellation during open/no overlapping handles, unavailable camera/manual fallback, mirrored UV orientation/texture reuse, decoded code does not consume attempt, explicit Validate uses existing ledger, Back/exit stop preview, full Meong Fly regression.

Windows physical acceptance remains pending: camera permissions/index, live left-right mirror, aspect ratio at portrait/landscape, actual printed QR focus/lighting, invalid/reused token messages, manual typing, disconnect, camera release indicator after Back/Validate/exit, responsiveness/FPS. Synthetic frames and owner-provided earlier screenshots do not prove these cases.

Run from the existing Windows Kivy environment:

```powershell
.\.venv-kivy\Scripts\python.exe -m unittest discover -s tests -p "test_meong_fly*.py" -v
.\.venv-kivy\Scripts\python.exe -m photobooth.meong_fly_demo
```

Show a QR whose text is a fresh `DEMO-...` code. Confirm it fills the field, then explicitly validate. A normal merchant QR is unsupported until a partner/POS integration is separately approved.

Rollback: scoped revert of the scanner implementation commit on the same branch, preserving ledger data. Pre-change baseline above; no force-push/master edits.
