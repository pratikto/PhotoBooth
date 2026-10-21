"""Render real Kivy GUI v2 prototype pages for visual regression.

Synthetic, non-paying screenshots only. Uses local approved frame art and
advertisement player fallback; does not connect to camera/merchant/printer.
Example: xvfb-run -a python tools/render_portrait_v2.py --output-dir /tmp/v2
"""

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("PHOTOBOOTH_AUDIO", "0")
os.environ.setdefault("PHOTOBOOTH_AD_VIDEO", "0")

from kivy.config import Config

Config.set("graphics", "width", "800")
Config.set("graphics", "height", "1280")

from kivy.clock import Clock
from kivy.core.window import Window
from photobooth.kiosk_v2.app import PortraitKioskV2App


class VisualRecorder(PortraitKioskV2App):
    def __init__(self, output_dir, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path(output_dir)
        self.saved = []

    def _capture(self, basename):
        """Screenshot only what the real Kivy stage drew on this frame."""
        target = self.output_dir / (basename + ".png")
        result = Window.screenshot(name=str(target))
        path = Path(result or target)
        if path.is_file() and path.stat().st_size:
            self.saved.append(path)

    def on_start(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

        def after(seconds, callback):
            Clock.schedule_once(lambda _dt, work=callback: work(), seconds)

        after(1.2, lambda: self._capture("01-advert-800x1280"))
        after(1.5, self._show_invitation)
        after(2.1, lambda: self._capture("02-invitation-800x1280"))
        after(2.3, self._choose_photo)
        after(2.9, lambda: self._capture("03-tutorial-800x1280"))
        after(3.2, self._complete_tutorial)
        after(3.8, lambda: self._capture("04-templates-800x1280"))
        after(4.0, lambda: self._change_copies(1))
        after(4.5, lambda: self._capture("05-copy-cart-800x1280"))
        after(4.7, self._return_ad)
        after(4.9, self._choose_game)
        after(5.5, lambda: self._capture("06-game-placeholder-800x1280"))
        after(5.7, self._return_ad)
        after(6.0, lambda: setattr(Window, "size", (450, 900)))
        after(6.2, self._choose_photo)
        after(6.8, lambda: self._capture("07-tutorial-450x900"))
        after(7.1, self._complete_tutorial)
        after(7.7, lambda: self._capture("08-templates-450x900"))
        after(8.0, self.stop)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="Destination for real Kivy PNGs")
    args = parser.parse_args()
    app = VisualRecorder(args.output_dir)
    app.run()
    if len(app.saved) != 8:
        raise SystemExit(f"Screenshot evidence incomplete: {len(app.saved)} / 8")
    for path in app.saved:
        print(path, path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
