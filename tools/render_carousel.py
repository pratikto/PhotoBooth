"""Render real MEONG carousel boundary animations as a small repeatable GIF.

Run from the project root with Kivy and an available graphics provider:
    SDL_VIDEODRIVER=offscreen python tools/render_carousel.py --output-dir /tmp/meong-loop

Every frame comes from the actual running Kivy widget tree. No browser, account,
webcam, payment, or customer photographs are used. The animation demonstrates
12→01 and 01→12 while preserving independent cart quantities.
"""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('KIVY_NO_ARGS', '1')
# Import the existing camera/QR dependency before the offscreen graphics provider,
# matching the application's and primary renderer's initialization order.
import cv2
from PIL import Image
from kivy.clock import Clock
from kivy.core.window import Window
from photobooth.catalog import get_templates
from photobooth.ui_kivy import KivyHost, PhotoBoothUI


def main():
    """Capture two genuine cyclic snaps and verify the visible endpoints."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    host = KivyHost(lambda: None)
    ui = PhotoBoothUI(host, get_templates(), on_start=lambda *_: None)
    Window.size = (1200, 800)
    frames, durations, errors = [], [], []
    record = {'size': [1200, 800], 'endpoints': [], 'cart_total': 'Rp15.000'}
    temporary = tempfile.TemporaryDirectory()
    path = Path(temporary.name) / 'frame.png'

    def capture(duration=60):
        # Export, flatten, and resize a COPY for the GIF; do not alter source
        # receipt art or any of the full-size QA screenshots.
        ui.shell.export_to_png(str(path))
        with Image.open(path) as source:
            rgb = source.convert('RGB').resize((900, 600), Image.Resampling.LANCZOS)
        frames.append(rgb.convert('P', palette=Image.Palette.ADAPTIVE, colors=128))
        durations.append(duration)

    def endpoint(expected, name):
        assert ui.template_carousel.index == expected, (
            f'Expected carousel index {expected}, got {ui.template_carousel.index}')
        assert ui.cart_total.text == 'Rp15.000'
        assert ui.quantities == {t.template_id: (2 if t.template_id == 'template_a' else
                                                1 if t.template_id == 'template_b' else 0)
                                 for t in ui.templates}
        ui.shell.export_to_png(str(output / f'{name}.png'))
        record['endpoints'].append({'index': expected, 'counter': ui.template_counter.text,
                                    'name': ui.template_name.text})

    def animate(button, expected, name, after):
        button.dispatch('on_release')
        remaining = [7]
        def tick(_dt):
            try:
                capture()
                remaining[0] -= 1
                if remaining[0] == 0:
                    endpoint(expected, name)
                    capture(700)
                    Clock.schedule_once(after, .2)
                    return False
            except Exception as error:
                errors.append(str(error))
                host.stop()
                return False
        Clock.schedule_interval(tick, .06)

    def finish(_dt):
        host.stop()

    def backward(_dt):
        animate(ui.carousel_previous, 11, 'carousel-wrapped-left', finish)

    def forward(_dt):
        try:
            endpoint(11, 'carousel-last')
            capture(700)
            animate(ui.carousel_next, 0, 'carousel-wrapped-right', backward)
        except Exception as error:
            errors.append(str(error))
            host.stop()

    def focus_last(_dt):
        ui.template_carousel.index = 11
        Clock.schedule_once(forward, .35)

    def present(_dt):
        # Build the screen AFTER App.run attaches the root to the Window.
        # A pre-loop screenshot can otherwise capture default 100-pixel widget
        # geometry and start an animation before its layout has been resolved.
        ui.show_template_selection(True, 'Drive siap · 25 slot folder tersedia.',
                                   quantities={'template_a': 2, 'template_b': 1})
        Clock.schedule_once(focus_last, .15)

    Clock.schedule_once(present, .1)
    host.run()
    if errors:
        raise SystemExit(str(errors))
    frames[0].save(output / 'meong-cyclic-carousel.gif', save_all=True,
                   append_images=frames[1:], duration=durations, loop=0, optimize=True)
    (output / 'carousel-report.json').write_text(json.dumps(record, indent=2) + '\n')
    temporary.cleanup()
    print('Verified carousel endpoints 12→01→12; order remains Rp15.000.')


if __name__ == '__main__':
    main()
