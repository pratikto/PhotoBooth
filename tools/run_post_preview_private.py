"""Run the unfinished private-preview development UI (no payment/print/Drive).

This is not the full physical-UAT candidate. Use an explicit isolated private
storage root; unresolved visits remain held on restart until PP-06 is implemented.
"""
import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root', type=Path, required=True,
                        help='Dedicated development-only private draft storage')
    args = parser.parse_args(argv)
    os.environ.setdefault('KIVY_NO_ARGS', '1')
    os.environ.setdefault('KIVY_LOG_MODE', 'MIXED')
    from photobooth.kiosk_v2.recovery import LaunchLease
    try:
        lease = LaunchLease(ROOT)
    except (OSError, ValueError):
        print('MEONG startup held: another kiosk launcher is active.', file=sys.stderr)
        return 2
    with lease:
        from tools.run_portrait_v2 import configure_kivy
        from kivy.config import Config
        configure_kivy(Config)
        from photobooth.kiosk_v2.post_preview_app import PrivatePreviewApp
        app = PrivatePreviewApp(args.private_root)
        try:
            app.run()
        finally:
            if getattr(app, '_photo_jobs', None):
                app._photo_jobs.close()
                app._photo_jobs.wait_closed(10)
                if app._photo_jobs.service:
                    app._photo_jobs.service.wait_closed(10)
            if getattr(app, 'camera_device', None):
                app.camera_device.close()
                app.camera_device.wait_closed(10)
    return 0


if __name__ == '__main__': sys.exit(main())
