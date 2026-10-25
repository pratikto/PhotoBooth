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
# Synthetic captures never inherit an operator's live delivery opt-ins.
os.environ['PHOTOBOOTH_V2_PRINT'] = '0'
os.environ['PHOTOBOOTH_V2_DRIVE'] = '0'
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("PHOTOBOOTH_AUDIO", "0")
os.environ.setdefault("PHOTOBOOTH_AD_VIDEO", "0")
os.environ.setdefault('PHOTOBOOTH_CAMERA', '0')
os.environ.setdefault('PHOTOBOOTH_FACE_TRIGGER', '0')
os.environ.setdefault('PHOTOBOOTH_PALM_TRIGGER', '0')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", required=True)
parser.add_argument("--width", type=int, choices=(360, 452, 800), default=800)
parser.add_argument("--height", type=int, choices=(600, 640, 900, 1280), default=1280)
parser.add_argument('--motion', action='store_true', help='Also capture native carousel motion frames and GIF')
# The renderer sets Config before importing the Window singleton.
options = parser.parse_args() if __name__ == "__main__" else None

from kivy.config import Config

Config.set("graphics", "width", str(options.width if options else 800))
Config.set("graphics", "height", str(options.height if options else 1280))

from kivy.clock import Clock
from kivy.core.window import Window
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.branding import MeongLogo


class VisualRecorder(PortraitKioskV2App):
    def __init__(self, output_dir, dimensions, *, capture_motion=False, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path(output_dir)
        self.dimensions = dimensions
        self.saved = []
        self.evidence = []
        self.capture_motion = capture_motion
        self.motion_frames = []

    def _capture_motion_frame(self, name):
        if self.navigation.page != 'templates':
            raise RuntimeError('Motion capture outside gallery')
        suffix = f'{self.dimensions[0]}x{self.dimensions[1]}'
        path = self.output_dir / f'motion-{name}-{suffix}.png'
        # Native FBO export renders the current widget geometry, including its
        # stencil. This avoids reading a previous swapped Window frame.
        self.stage.export_to_png(str(path))
        self.motion_frames.append({
            'file': path.name, 'selected_index': self.template_index,
            'offset': self._carousel.offset,
            'selected_image_pos': list(self._preview.pos),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        })

    def _capture(self, name):
        expected_page = {
            "01-advert": "advert", "02-invitation": "advert",
            "03-tutorial": "tutorial", "04-templates": "templates",
            "05-copy-cart": "templates", "06-game-placeholder": "game_preview",
        }[name]
        if self.navigation.page != expected_page:
            raise RuntimeError(f"Wrong page for {name}: {self.navigation.page}")
        if self.navigation.page != 'game_preview' and getattr(self, '_brand_capture_ready', None) != name:
            # A live impact flip is briefly edge-on. Freeze a declared neutral
            # pose for static page/ink QA; real-clock motion is checked separately.
            for brand in (w for w in self.stage.walk() if isinstance(w, MeongLogo)):
                brand.set_active(False)
                brand.spin = 0
                brand.flight = 0
            self._brand_capture_ready = name
            Clock.schedule_once(lambda _dt: self._capture(name), .08)
            return
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
                if self.navigation.page == 'game_preview':
                    from photobooth.meong_fly_gui import MeongFlyStage
                    if not isinstance(self._game_field, MeongFlyStage) or self._game_field._screen_seen != 'start':
                        raise RuntimeError('Expected actual latest Meong Fly start stage')
                else:
                    brands = [w for w in self.stage.walk() if isinstance(w, MeongLogo)]
                    if len(brands) != 1:
                        raise RuntimeError(f"Expected one brand on {name}, got {len(brands)}")
                    mark = brands[0].wordmark
                    x, y = mark.to_window(mark.x, mark.y)
                    right, top = mark.to_window(mark.right, mark.top)
                    box = (max(0, int(x)), max(0, int(rgb.height - top)),
                           min(rgb.width, int(right)), min(rgb.height, int(rgb.height - y)))
                    if box[2] <= box[0] or box[3] <= box[1]:
                        raise RuntimeError(f"Offscreen Meong wordmark on {name}")
                    expected_ink = tuple(int(mark.ink.strip('#')[i:i + 2], 16) for i in (0, 2, 4))
                    ink_pixels = sum(1 for pixel in rgb.crop(box).getdata()
                                     if all(abs(channel - target) <= 3
                                            for channel, target in zip(pixel, expected_ink)))
                    if ink_pixels < 20:
                        raise RuntimeError(f"Meong wordmark missing from actual pixels on {name}")
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
        steps = [
            (1.2, lambda: self._capture("01-advert")),
            (.3, self._show_invitation),
            (.6, lambda: self._capture("02-invitation")),
            (.2, self._choose_photo),
            (.6, lambda: self._capture("03-tutorial")),
            (.3, self._complete_tutorial),
            (.6, lambda: self._capture("04-templates")),
        ]
        if self.capture_motion:
            steps.extend([
                (.1, lambda: self._capture_motion_frame('00-rest')),
                (.02, lambda: self._shift_template(1)),
                (.03, lambda: self._capture_motion_frame('01-next')),
                (.03, lambda: self._capture_motion_frame('02-next')),
                (.03, lambda: self._capture_motion_frame('03-next')),
                (.25, lambda: self._capture_motion_frame('04-selected')),
                (.02, lambda: self._shift_template(-1)),
                (.03, lambda: self._capture_motion_frame('05-previous')),
                (.03, lambda: self._capture_motion_frame('06-previous')),
                (.03, lambda: self._capture_motion_frame('07-previous')),
                (.25, lambda: self._capture_motion_frame('08-returned')),
            ])
        steps.extend([
            (.2, lambda: self._change_copies(1)),
            (.5, lambda: self._capture("05-copy-cart")),
            (.2, self._return_ad),
            (.2, self._choose_game),
            (.6, lambda: self._capture("06-game-placeholder")),
            (.4, self.stop),
        ])
        steps = iter(steps)

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
    if (options.width, options.height) not in ((800, 1280), (452, 900),
                                              (360, 640), (452, 600), (800, 600)):
        raise SystemExit("Unsupported QA viewport size")
    app = VisualRecorder(options.output_dir, (options.width, options.height), capture_motion=options.motion)
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
        'motion_frames': app.motion_frames,
        'static_brand_pose_controlled': True,
    }
    report_path = app.output_dir / f"report-{options.width}x{options.height}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if options.motion:
        from PIL import Image as PillowImage
        if len(app.motion_frames) != 9 or len({f['sha256'] for f in app.motion_frames}) < 5:
            raise SystemExit('Incomplete or static carousel motion evidence')
        frames = [PillowImage.open(app.output_dir / f['file']).convert('RGB') for f in app.motion_frames]
        frames[0].save(app.output_dir / f'carousel-{options.width}x{options.height}.gif',
                       save_all=True, append_images=frames[1:], loop=0,
                       duration=[250, 70, 70, 70, 250, 70, 70, 70, 250])
    for path in app.saved:
        print(path, path.stat().st_size, "bytes")
    print(report_path)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        # Kivy may redirect stderr when its console logger is disabled. Preserve
        # the real capture failure instead of returning a silent nonzero status.
        import traceback
        os.write(2, traceback.format_exc().encode('utf-8', errors='replace'))
        raise
