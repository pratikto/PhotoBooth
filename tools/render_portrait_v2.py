"""Capture the real v2 Kivy pages using one clean process per display size.

Never resize an active software-GL framebuffer during screenshot QA: on some
Xvfb/SDL2 providers this shears and corrupts pixels, hiding real layout truth.

Examples:
    xvfb-run -a python tools/render_portrait_v2.py --output-dir /tmp/v2 --width 800 --height 1280
    xvfb-run -a python tools/render_portrait_v2.py --output-dir /tmp/v2 --width 452 --height 900
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

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", required=True)
parser.add_argument("--width", type=int, choices=(452, 800), default=800)
parser.add_argument("--height", type=int, choices=(900, 1280), default=1280)
# The renderer sets Config before importing the Window singleton.
options = parser.parse_args() if __name__ == "__main__" else None

from kivy.config import Config

Config.set("graphics", "width", str(options.width if options else 800))
Config.set("graphics", "height", str(options.height if options else 1280))

from kivy.clock import Clock
from kivy.core.window import Window
from photobooth.kiosk_v2.app import PortraitKioskV2App


class VisualRecorder(PortraitKioskV2App):
    def __init__(self, output_dir, dimensions, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path(output_dir)
        self.dimensions = dimensions
        self.saved = []

    def _capture(self, name):
        suffix = f"{self.dimensions[0]}x{self.dimensions[1]}"
        target = self.output_dir / f"{name}-{suffix}.png"
        # 452 pixels is the nearest 4-byte-aligned screenshot width to 450.
        # Kivy's SDL2 readback distorts 450-wide RGB PNGs in the CI Xvfb
        # renderer (450*3=1350 is not divisible by 4). This is a capture
        # limitation, not evidence that the live 450-wide widget is distorted.
        written = Window.screenshot(name=str(target))
        path = Path(written or target)
        if path.is_file() and path.stat().st_size > 1000:
            # Detect the Kivy/OpenGL RGB row-packing screenshot defect instead
            # of accepting a corrupt PNG as genuine 450-pixel visual evidence.
            from PIL import Image as PillowImage, ImageChops, ImageStat
            with PillowImage.open(path) as original:
                rgb = original.convert("RGB")
                left = rgb.crop((2, int(rgb.height * .10),
                                 min(12, rgb.width), int(rgb.height * .90)))
                rows = ImageChops.difference(
                    left.crop((0, 0, left.width, left.height - 1)),
                    left.crop((0, 1, left.width, left.height)),
                )
                vertical_noise = sum(ImageStat.Stat(rows).mean) / 3
            if vertical_noise > 12:
                raise RuntimeError(
                    f"Corrupt OpenGL screenshot row stride at {path.name}: "
                    f"mean adjacent row difference={vertical_noise:.1f}"
                )
            self.saved.append(path)

    def on_start(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

        def later(seconds, function):
            Clock.schedule_once(lambda _dt, task=function: task(), seconds)

        later(1.2, lambda: self._capture("01-advert"))
        later(1.5, self._show_invitation)
        later(2.1, lambda: self._capture("02-invitation"))
        later(2.3, self._choose_photo)
        later(2.9, lambda: self._capture("03-tutorial"))
        later(3.2, self._complete_tutorial)
        later(3.8, lambda: self._capture("04-templates"))
        later(4.0, lambda: self._change_copies(1))
        later(4.5, lambda: self._capture("05-copy-cart"))
        later(4.7, self._return_ad)
        later(4.9, self._choose_game)
        later(5.5, lambda: self._capture("06-game-placeholder"))
        later(5.9, self.stop)


def main():
    if (options.width, options.height) not in ((800, 1280), (452, 900)):
        raise SystemExit("Only approved portrait preview sizes are supported")
    app = VisualRecorder(options.output_dir, (options.width, options.height))
    app.run()
    if len(app.saved) != 6:
        raise SystemExit(f"Incomplete {options.width}x{options.height} QA evidence: {len(app.saved)}/6")
    for path in app.saved:
        print(path, path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
