"""Capture the real v2 Kivy pages using one clean process per display size.

Never resize an active software-GL framebuffer during screenshot QA: on some
Xvfb/SDL2 providers this shears and corrupts pixels, hiding real layout truth.

Examples:
    xvfb-run -a python tools/render_portrait_v2.py --output-dir /tmp/v2 --width 800 --height 1280
    xvfb-run -a python tools/render_portrait_v2.py --output-dir /tmp/v2 --width 452 --height 900
"""

import argparse
import hashlib
import json
import subprocess
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
        self.evidence = []

    def _capture(self, name):
        expected_page = {
            "01-advert": "advert", "02-invitation": "advert",
            "03-tutorial": "tutorial", "04-templates": "templates",
            "05-copy-cart": "templates", "06-game-placeholder": "game_preview",
        }[name]
        if self.navigation.page != expected_page:
            raise RuntimeError(f"Wrong page for {name}: {self.navigation.page}")
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
                if original.size != self.dimensions:
                    raise RuntimeError(f"Wrong screenshot size: {original.size}")
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
            self.evidence.append({
                "state": name, "page": expected_page, "file": path.name,
                "width": self.dimensions[0], "height": self.dimensions[1],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })

    def on_start(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Schedule relative to the completed previous action. Slow font/texture
        # startup must not collapse several routes and captures into one frame.
        steps = iter((
            (1.2, lambda: self._capture("01-advert")),
            (.3, self._show_invitation),
            (.6, lambda: self._capture("02-invitation")),
            (.2, self._choose_photo),
            (.6, lambda: self._capture("03-tutorial")),
            (.3, self._complete_tutorial),
            (.6, lambda: self._capture("04-templates")),
            (.2, lambda: self._change_copies(1)),
            (.5, lambda: self._capture("05-copy-cart")),
            (.2, self._return_ad),
            (.2, self._choose_game),
            (.6, lambda: self._capture("06-game-placeholder")),
            (.4, self.stop),
        ))

        def advance():
            try:
                delay, action = next(steps)
            except StopIteration:
                return

            def execute(_dt):
                action()
                advance()

            Clock.schedule_once(execute, delay)

        advance()


def main():
    if (options.width, options.height) not in ((800, 1280), (452, 900)):
        raise SystemExit("Only approved portrait preview sizes are supported")
    app = VisualRecorder(options.output_dir, (options.width, options.height))
    app.run()
    if len(app.saved) != 6:
        raise SystemExit(f"Incomplete {options.width}x{options.height} QA evidence: {len(app.saved)}/6")
    report = {
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "tracked_changes": bool(subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT)),
        "synthetic_only": True,
        "screenshots": app.evidence,
    }
    report_path = app.output_dir / f"report-{options.width}x{options.height}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for path in app.saved:
        print(path, path.stat().st_size, "bytes")
    print(report_path)


if __name__ == "__main__":
    main()
