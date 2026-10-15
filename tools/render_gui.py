"""Render repeatable visual evidence without a camera, Drive, or credentials.

Run from the repository root, for example on Linux with Mesa offscreen support:
    SDL_VIDEODRIVER=offscreen python tools/render_gui.py --output-dir /tmp/booth-qa

The script uses the real Kivy application loop, layouts, and GPU textures. Every
photo is a generated geometric illustration and every folder URL is a fixture.
It never creates a customer transaction, opens a webcam, or contacts a service.
"""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

# Running a file under tools/ does not automatically put the project on sys.path.
# Add only this checkout; do not depend on a different working copy or venv.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Kivy otherwise consumes this script's --output-dir option before argparse.
os.environ.setdefault('KIVY_NO_ARGS', '1')

import cv2
from PIL import Image, ImageDraw, ImageFont
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView

from photobooth.catalog import compose_result, get_templates
from photobooth.qr_code import create_qr_image
from photobooth.ui_kivy import KivyHost, PhotoBoothUI


FOLDER_URL = 'https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz123456'
STATUS = 'Drive siap · 25 slot folder tersedia.'
SIZES = ((1200, 800), (800, 600))
OVERVIEW_SCREENS = ('welcome', 'templates', 'payment', 'capture', 'review', 'result')


def synthetic_portrait(index):
    """Draw visibly artificial fixtures instead of reading real user photos."""
    image = Image.new('RGB', (640, 480), ('#e7e9dd', '#efe5d9', '#dee8ed')[index])
    draw = ImageDraw.Draw(image)
    offset = (0, -35, 25)[index]
    draw.ellipse((225 + offset, 65, 415 + offset, 255), fill='#c9ac8b')
    draw.rounded_rectangle((170 + offset, 260, 470 + offset, 500), radius=70,
                           fill=('#637d6c', '#8f6e63', '#607b8b')[index])
    return image


def bounds(widget):
    """Convert ScrollView-transformed positions to screenshot coordinates."""
    x, y = widget.to_window(*widget.pos)
    return x, y, x + widget.width, y + widget.height


def screenshot_qr(image_path, widget):
    """Decode painted screen pixels; a valid source texture is not sufficient."""
    pixels = cv2.imread(str(image_path))
    left, bottom, right, top = bounds(widget)
    crop = pixels[round(Window.height - top):round(Window.height - bottom),
                  round(left):round(right)]
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(crop)
    return decoded


def overview(output, size):
    """Keep a compact comparison of the six main screens beside full PNGs."""
    width, height = size
    thumb = (width // 2, height // 2)
    label_height = 30
    sheet = Image.new('RGB', (thumb[0] * 2, (thumb[1] + label_height) * 3), '#f6f5f0')
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', 14)
    except OSError:
        font = ImageFont.load_default()
    for index, name in enumerate(OVERVIEW_SCREENS):
        x = (index % 2) * thumb[0]
        y = (index // 2) * (thumb[1] + label_height)
        draw.text((x + 12, y + 7), f'{name.upper()}  |  {width} × {height}', fill='#1a302e', font=font)
        with Image.open(output / f'{name}-{width}x{height}.png') as image:
            sheet.paste(image.resize(thumb, Image.Resampling.LANCZOS), (x, y + label_height))
    sheet.save(output / f'overview-{width}x{height}.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path,
                        default=Path(tempfile.gettempdir()) / 'photobooth-gui-qa')
    output = parser.parse_args().output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for index in range(3):
        path = output / f'synthetic-{index + 1}.png'
        synthetic_portrait(index).save(path)
        paths.append(path)
    templates = get_templates()
    result = compose_result(paths, templates[0], output / 'composition.png',
                            'PB001_00000001', 'session_001', FOLDER_URL)
    local_result = compose_result(paths, templates[0], output / 'composition-local.png',
                                  'PB001_00000001', 'session_001')
    host = KivyHost(lambda: None)
    callbacks = {name: lambda *args: None for name in (
        'on_home_start', 'on_start', 'on_capture', 'on_select_photo', 'on_retake',
        'on_accept_session', 'on_next_session', 'on_finish', 'on_close')}
    ui = PhotoBoothUI(host, templates, **callbacks)

    def cart():
        ui.show_template_selection(True, STATUS)
        for template in templates:
            ui._change_quantity(template.template_id, 2)

    def result_screen(local=False, has_next=False):
        ui.show_result(local_result if local else result, 'Sesi 1 dari 8 · Template 1',
                       'PB001_00000001', has_next, None if has_next else 60,
                       None if local else create_qr_image(FOLDER_URL), False,
                       'Hasil digital tersimpan di perangkat ini.' if local else
                       'Internet terputus. QR membuka folder tujuan; foto akan muncul '
                       'setelah upload dilanjutkan.')

    def scroll_last_template():
        last = ui._template_cards[templates[-1].template_id]
        last.parent.parent.scroll_y = 0

    # Additional states catch issues hidden by the six happy-path screenshots:
    # scrolling to the last template, active countdown, an exhausted retake,
    # local-only output, and a next-session action without a completion timer.
    scenes = (
        ('welcome', lambda: ui.show_welcome(True, STATUS), None),
        ('templates', cart, None),
        ('templates-bottom', cart, scroll_last_template),
        ('payment', lambda: ui.show_payment('\n'.join(f'{t.name} × 2' for t in templates),
                                           8, 40000, lambda: None, lambda: None), None),
        ('capture', lambda: ui.show_capture('Sesi 1 dari 8 · Template 1', 1, synthetic_portrait(0)), None),
        ('countdown', lambda: (ui.show_capture('Sesi 1 dari 8 · Template 1', 1, synthetic_portrait(0)),
                               ui.set_countdown(5)), None),
        ('review', lambda: ui.show_review(paths, 'Sesi 1 dari 8 · Template 1', 1, True), None),
        ('review-used', lambda: ui.show_review(paths, 'Sesi 1 dari 8 · Template 1', 1, False), None),
        ('result', result_screen, None),
        ('result-local', lambda: result_screen(local=True), None),
        ('result-next', lambda: result_screen(has_next=True), None),
    )
    records, errors = [], []

    def capture(name, size):
        try:
            width, height = size
            path = output / f'{name}-{width}x{height}.png'
            ui.shell.export_to_png(str(path))
            stage = next(w for w in ui.content.children if isinstance(w, ScrollView))
            fits = stage.children[0].height <= stage.height + 1
            if not fits:
                raise AssertionError(f'{name} has a clipped desktop stage at {size}')
            decoded = None
            if name == 'payment':
                decoded = screenshot_qr(path, ui.payment_qr)
                if decoded != 'PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR 40000':
                    raise AssertionError(f'Demo QR is unreadable in {path}')
            elif name in ('result', 'result-next'):
                decoded = screenshot_qr(path, ui.qr_view)
                if decoded != FOLDER_URL:
                    raise AssertionError(f'Folder QR is unreadable in {path}')
            elif name == 'result-local' and ui.qr_view.texture is not None:
                raise AssertionError('A local-only result must not have a fabricated Drive QR')
            records.append({'screen': name, 'size': list(size), 'file': path.name,
                            'stage_fits': fits, 'decoded_qr': decoded})
            print(f'PASS {name} {width}x{height}', flush=True)
        except Exception as error:
            errors.append(str(error))
            host.stop()

    elapsed = .1
    for size in SIZES:
        for name, build, after_layout in scenes:
            def setup(_dt, size=size, build=build):
                Window.size = size
                build()
            Clock.schedule_once(setup, elapsed)
            if after_layout is not None:
                Clock.schedule_once(lambda _dt, fn=after_layout: fn(), elapsed + .15)
            Clock.schedule_once(lambda _dt, name=name, size=size: capture(name, size), elapsed + .35)
            elapsed += .5
    Clock.schedule_once(lambda _dt: host.stop(), elapsed + .1)
    host.run()
    (output / 'report.json').write_text(json.dumps({'renders': records, 'errors': errors}, indent=2) + '\n')
    if errors:
        raise SystemExit('\n'.join(errors))
    for size in SIZES:
        overview(output, size)
    print(f'{len(records)} real-widget renders saved in {output}')


if __name__ == '__main__':
    main()
