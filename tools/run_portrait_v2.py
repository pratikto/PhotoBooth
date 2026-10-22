r"""Run the opt-in GUI v2 prototype, without changing python main.py.

Windows:
    .\.venv-kivy\Scripts\Activate.ps1
    python tools/run_portrait_v2.py

This stage cannot accept payments, operate a real cafe receipt scanner,
capture camera frames, print or issue discounts.
"""

import os
from contextlib import nullcontext
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Kivy reads these before opening the window. Ignore kiosk framework CLI flags.
os.environ.setdefault("KIVY_NO_ARGS", "1")

def main():
    # Install before importing native window/audio/video providers. Keep the
    # stream open through App.run/on_stop so fatal Windows exceptions can be
    # inspected even when there is no Python traceback in the terminal.
    from photobooth.kiosk_v2.diagnostics import DiagnosticSession
    try:
        diagnostics = DiagnosticSession(PROJECT_ROOT)
    except OSError as exc:
        print(f"MEONG v2 diagnostic file unavailable: {exc}", file=sys.stderr, flush=True)
        diagnostics = nullcontext()
    with diagnostics as session:
        if session is not None:
            print(f"MEONG v2 HEAD={session.head} diagnostic log: {session.path}", flush=True)
        from kivy.config import Config
        Config.set("graphics", "width", "800")
        Config.set("graphics", "height", "1280")
        from photobooth.kiosk_v2.app import PortraitKioskV2App
        logging.getLogger('photobooth.kiosk_v2').info('Window startup')
        print("MEONG v2 PORTRAIT PROTOTYPE - no payment, camera, printing or real game", flush=True)
        PortraitKioskV2App().run()


if __name__ == "__main__":
    main()
