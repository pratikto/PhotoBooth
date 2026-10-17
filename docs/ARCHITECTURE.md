# Meong Photobooth — Architecture and handover

Last reviewed: 2026-10-17. Target branch: `feature/kivy-gui`.

## Entry point and separation of responsibilities

`main.py` starts `photobooth.app.PhotoBoothApp`. `photobooth/app.py` is the workflow controller, builds the camera, local transaction store, optional Drive pool/synchronizer and retention worker, then connects callbacks to `PhotoBoothUI`.

`photobooth/ui_kivy.py` provides the Kivy host, pages, customer controls and controller callbacks. `photobooth/ui_kiosk.py` provides the advertising/payment kiosk behavior mixin; `photobooth/ui_brand.py` owns branding and cyclic template carousel; `photobooth/ui_motion.py` owns page-scoped animation and countdown visuals.

`photobooth/advertising.py` loads scheduled local playlists and timing configuration. `photobooth/face_presence.py` handles optional face-presence detection for the idle invitation; `photobooth/palm_gesture.py` handles the separate, optional palm-trigger shutter. These are presence/gesture triggers, not identity recognition.

`photobooth/audio.py` owns original background music, UI sounds, camera cues and advertising gain. `photobooth/catalog.py` loads approved 80 mm layouts and composes photos. `photobooth/camera.py` owns camera capture. `photobooth/workflow.py` models individual ordered photo sessions.

`photobooth/transaction_store.py`, `drive_pool.py`, `drive_storage.py`, `drive_sync.py`, `retention.py`, and `qr_code.py` handle local persistence, pre-created folder allocation, optional uploading, retention and folder QR output. See the code and main README for exact interfaces.

## Runtime flow

Intended customer flow: idle advertisement -> illustrated tutorial -> cyclic layout selection -> demo payment -> photo sessions/review/retake -> results -> idle advertisement.

IMPORTANT: The README and existing advertising setup describe some flow differently (manual entry to picker, tutorial accessible separately). The requested **mandatory tutorial before picker** is a pending user-reported change, not a verified shipped behavior.

The advertising and payment playlists are independent. Idle video sound is allowed; payment advertising must stay muted. Application music/effects own the other photography screens. Payment currently uses a **non-payable demonstration**, never actual verified QRIS.

## Development boundary

Photo image-printing and dithering work belongs to the separate `feature/thermal-printer` branch. The GUI branch can handle a LAN ESC/POS *payment QR slip* without implying photo-printing integration.

The application targets desktop Kivy with OpenCV/Pillow. Android packaging, physical printer support, actual camera/light conditions, and live QRIS require further validation or implementation.

## Run and validate

```bash
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
```

Optional GUI/audio-specific environment flags and validation instructions are documented in `README.md`, `docs/advertising-and-qris.md` and `docs/qa/`. Historical QA results must not be treated as proof that all current user-reported bugs are fixed.

**Cross-references:** [Feature status](FEATURE_STATUS.md) · [Decisions](DECISIONS.md) · [Next steps](NEXT_STEPS.md).
