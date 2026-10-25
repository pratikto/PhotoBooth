r"""Run the opt-in GUI v2 prototype, without changing python main.py.

Windows:
    .\.venv-kivy\Scripts\Activate.ps1
    python tools/run_portrait_v2.py

Photo tests and P4 Meong Fly DEMO are local by default. Production payment,
cafe receipt scanner and actual discounts stay disabled. Print/Drive are opt-in.
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

def configure_kivy(config):
    """V2 process defaults; never persist settings into the user's Kivy file."""
    config.set('graphics', 'width', '800')
    config.set('graphics', 'height', '1280')
    # Right/Ctrl clicks otherwise create persistent red multitouch markers.
    # This only disables mouse emulation; physical touchscreen input remains.
    config.set('input', 'mouse', 'mouse,disable_multitouch')

def main(argv=()):
    from photobooth.kiosk_v2.delivery_options import configure_delivery
    configure_delivery(argv)
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
        configure_kivy(Config)
        from photobooth.kiosk_v2.app import PortraitKioskV2App
        logging.getLogger('photobooth.kiosk_v2').info('Window startup')
        print("MEONG v2 P4 DEMO - no production payment, scanner or actual discount", flush=True)
        app = PortraitKioskV2App()
        try:
            app.run()
        finally:
            if getattr(app, 'camera_device', None):
                app.camera_device.close()
                app.camera_device.wait_closed()
            if getattr(app, '_photo_jobs', None):
                app._photo_jobs.close()
                app._photo_jobs.wait_closed()
            if getattr(app, '_game_jobs', None):
                app._game_jobs.close()
                app._game_jobs.wait_closed()
            if getattr(app, '_health_reports', None):
                app._health_reports.close()
                app._health_reports.wait_closed()
            if getattr(app, '_sandbox_jobs', None):
                app._sandbox_jobs.close()
                app._sandbox_jobs.wait_closed()
            if getattr(app, '_mock_jobs', None):
                app._mock_jobs.close()
                app._mock_jobs.wait_closed()


if __name__ == "__main__":
    main(sys.argv[1:])
