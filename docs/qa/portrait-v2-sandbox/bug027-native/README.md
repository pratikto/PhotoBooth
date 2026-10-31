# BUG-027 synthetic native evidence

Eight original app captures at 800×1280 and 452×900 show direct camera after one
receipt submission, the approved strip after one submission, private claim after
pause, and a readable warning when receipt submission is uncertain. Every frame
uses colored synthetic camera input and injected printer/provider transports.
No physical paper, customer photo, merchant credential or recovery QR is exported.

The original recovery receipt is checked in memory at 384/576 dots. Its QR and
bitmap are deliberately absent here. Exact hashes, source and limits are in
[the final verification receipt](../evidence/bug027-final-verification.json).

For development reproduction from the repository root, use the existing Kivy
virtual environment and the offline driver below. It clears delivery settings
and injects synthetic transports before starting the original app. No actual
merchant or printer configuration is needed. Outputs go to private `work/`.

```bash
KIVY_NO_ARGS=1 KIVY_NO_CONSOLELOG=1 SDL_VIDEODRIVER=offscreen SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1 python docs/qa/portrait-v2-sandbox/bug027-native/capture-fixture.py.txt --width 800 --height 1280
```

Repeat with `--width 452 --height 900`, and add `--failure` for the uncertain
receipt scene. A fresh process per invocation owns the native window. The
public driver only normalizes repository discovery compared with the executed
scratch driver; rendering and assertions are identical. These are source/GUI
fixtures, not Windows hardware, physical printer or merchant acceptance.

For actual laptop testing, follow the [owner guide](../UX07-LAPTOP-CHECK.md).
