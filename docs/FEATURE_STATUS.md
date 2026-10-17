# Meong Photobooth — Feature status

Snapshot: 2026-10-17, `feature/kivy-gui`. Statuses distinguish **implemented in source/docs** from **verified on the user's machine**. User-reported defects are open even if earlier automated QA passed.

| Area | Status | Evidence / limitation |
| --- | --- | --- |
| Kivy branded GUI, original Meong logo, animated pages | Implemented; on-device validation ongoing | `ui_kivy.py`, `ui_brand.py`, `ui_motion.py` |
| 12 cyclic template previews, quantity/cart at Rp5,000 per session | Implemented | `README.md`, `catalog.py` |
| Capture 3 photos/session, five-second timer, review, selected-photo retake | Implemented | `app.py`, `workflow.py`, `ui_kivy.py` |
| Optional palm-trigger shutter and face-presence invitation | Implemented; physical validation needed | `palm_gesture.py`, `face_presence.py` |
| Idle advertising and separate payment ad playlist (images/videos) | Implemented in code; **video playback reported broken** | `advertising.py`, `ui_kiosk.py`; investigate media backend, local files and event loop |
| Larger main advertising video | **Requested / pending visual adjustment** | User says current idle video is too small |
| Audio startup, independent sliders and effects | Implemented in code; **startup audio reported broken** | Starts only after opening Settings on user installation; reproduce and fix |
| Idle ad -> mandatory tutorial -> layout picker | **Requested / pending behavior change** | Current documented navigation may bypass guide |
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
