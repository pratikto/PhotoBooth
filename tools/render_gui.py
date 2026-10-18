"""Render repeatable visual evidence without a camera, Drive, or credentials.

Run from the repository root, for example on Linux with Mesa offscreen support:
    SDL_VIDEODRIVER=offscreen python tools/render_gui.py --output-dir /tmp/booth-qa

The script uses the real Kivy application loop, layouts, and GPU textures. Every
photo is a generated geometric illustration and every folder URL is a fixture.
It never creates a customer transaction, opens a webcam, or contacts a service.
"""

import argparse
from collections import Counter
from datetime import timedelta
from itertools import count
import json
import os
from pathlib import Path
import sys
import tempfile
import time

# Running a file under tools/ does not automatically put the project on sys.path.
# Add only this checkout; do not depend on a different working copy or venv.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Kivy otherwise consumes this script's --output-dir option before argparse.
os.environ.setdefault('KIVY_NO_ARGS', '1')

import cv2
from PIL import Image, ImageDraw, ImageFont
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image as KivyImage
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.text import Label as CoreLabel

from photobooth.catalog import compose_result, get_templates
from photobooth.qr_code import create_qr_image
from photobooth.payment import PaymentAttempt
from tools.ci_qr_pixels import decode_rendered_qr_pixels
from photobooth.ui_kivy import KivyHost, PhotoBoothUI


FOLDER_URL = 'https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz123456'
STATUS = 'Drive siap · 25 slot folder tersedia.'
LONG_STATUS = ('Slot Drive perlu diperiksa: Folder fixture belum terverifikasi. '
               'Salinan lokal tetap tersimpan. Periksa konfigurasi deployment lalu coba lagi. ') * 8
SIZES = ((1200, 800), (800, 600), (1920, 1080))
OVERVIEW_SCREENS = ('welcome', 'templates', 'payment', 'capture', 'review', 'result')
STATE_SCREENS = ('payment-waiting', 'capture-waiting', 'review-used', 'review-waiting')
SELECTION_SCREENS = ('templates-empty', 'templates-one', 'templates', 'templates-last')
DIAGNOSTIC_SCREENS = ('templates-status', 'templates-one')
RETAKE_SCREENS = ('retake-ready', 'retake-countdown')
PALM_SCREENS = ('palm-ready', 'palm-hold', 'palm-release', 'palm-loading', 'palm-unavailable')
ADVERTISING_SCREENS = ('advert', 'advert-invitation', 'payment', 'payment-print-offer',
                       'payment-enlarged', 'payment-expired')


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
    # Decode actual captured screen pixels, not the pre-render QR texture.
    # OpenCV's detector is sensitive to a single downsampled module scale.
    # Nearest-neighbour 2x/3x views do not restore unreadable or missing bits.
    return decode_rendered_qr_pixels(crop)


def button_contrast(image_path, widget):
    """Measure a disabled label against its actually painted background.

    Kivy's disabled atlas can tint a nominal background, so comparing configured
    colors alone misses the final appearance. Sample only the inset button box,
    take its dominant fill, and find the strongest painted glyph color nearest
    the configured disabled ink. Intermediate antialias pixels are not mistaken
    for the foreground. This is a text-color check, not an accessibility audit.
    """
    left, bottom, right, top = bounds(widget)
    with Image.open(image_path) as source:
        crop = source.convert('RGB').crop((round(left + 4), round(Window.height - top + 4),
                                            round(right - 4), round(Window.height - bottom - 4)))
        colors = Counter(crop.getdata())
    background = colors.most_common(1)[0][0]
    target = [channel * 255 for channel in widget.disabled_color[:3]]
    foreground = min(colors, key=lambda rgb: sum((a - b) ** 2 for a, b in zip(rgb, target)))

    def luminance(rgb):
        channels = [value / 255 for value in rgb]
        linear = [value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4
                  for value in channels]
        return sum(value * weight for value, weight in zip(linear, (.2126, .7152, .0722)))

    dark, light = sorted((luminance(background), luminance(foreground)))
    return {'text': widget.text, 'background_rgb': list(background),
            'foreground_rgb': list(foreground), 'ratio': round((light + .05) / (dark + .05), 3)}


def fully_visible(widget):
    """Exclude gallery controls clipped by a viewport from pixel sampling."""
    box = bounds(widget)
    if box[0] < 0 or box[1] < 0 or box[2] > Window.width or box[3] > Window.height:
        return False
    parent = widget.parent
    while parent is not None and parent is not Window:
        if isinstance(parent, ScrollView):
            clip = bounds(parent)
            if (box[0] < clip[0] - 1 or box[1] < clip[1] - 1
                    or box[2] > clip[2] + 1 or box[3] > clip[3] + 1):
                return False
        parent = parent.parent
    return True


def overview(output, size, screens=OVERVIEW_SCREENS, prefix='overview'):
    """Flatten widget transparency into paper when assembling visual evidence."""
    width, height = size
    thumb = (width // 2, height // 2)
    label_height = 30
    rows = (len(screens) + 1) // 2
    paper = '#f3f5fa'
    sheet = Image.new('RGB', (thumb[0] * 2, (thumb[1] + label_height) * rows), paper)
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', 14)
    except OSError:
        font = ImageFont.load_default()
    for index, name in enumerate(screens):
        x = (index % 2) * thumb[0]
        y = (index // 2) * (thumb[1] + label_height)
        draw.text((x + 12, y + 7), f'{name.upper()}  |  {width} × {height}', fill='#111620', font=font)
        with Image.open(output / f'{name}-{width}x{height}.png') as image:
            # Rounded widget exports contain transparent corners. An RGBA paste
            # into RGB without a mask discards alpha and exposes hidden black
            # channels. Composite before resampling to keep translucent edges
            # correct too; leave the original full-size PNG entirely untouched.
            flattened = Image.new('RGBA', image.size, paper)
            flattened.alpha_composite(image.convert('RGBA'))
            sheet.paste(flattened.convert('RGB').resize(thumb, Image.Resampling.LANCZOS),
                        (x, y + label_height))
    sheet.save(output / f'{prefix}-{width}x{height}.png')


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

    # Visual CI must re-render IDENTICAL test inputs across retries. Production
    # DemoPaymentGateway.create() includes uuid4, so each CI run previously
    # produced different QR modules and occasionally defeated OpenCV at one
    # desktop sampling size despite a visibly intact code. Only this synthetic
    # GUI harness uses stable, distinct attempt IDs; payment.py and actual
    # booth QR generation remain untouched. All assertions still decode the
    # screenshot and compare with the full, exact payload.
    fixture_attempts = count(1)

    def create_fixture_payment(amount):
        current = ui.payment.gateway.now()
        attempt_id = f'DEMO-CI{next(fixture_attempts):010X}'
        return PaymentAttempt(
            attempt_id, amount,
            f'PHOTOBOOTH DEMO ONLY - NOT QRIS - IDR {amount} - {attempt_id}',
            current, current + timedelta(seconds=ui.payment.gateway.validity),
        )

    ui.payment.gateway.create = create_fixture_payment

    def cart():
        ui.show_template_selection(True, STATUS)
        for template in templates:
            ui._change_quantity(template.template_id, 2)

    def single_template():
        ui.show_template_selection(True, STATUS)
        ui._change_quantity(templates[0].template_id, 2)

    def result_screen(local=False, has_next=False):
        ui.show_result(local_result if local else result, 'Sesi 1 dari 24 · Special Day',
                       'PB001_00000001', has_next, None if has_next else 60,
                       None if local else create_qr_image(FOLDER_URL), False,
                       'Hasil digital tersimpan di perangkat ini.' if local else
                       'Internet terputus. QR membuka folder tujuan; foto akan muncul '
                       'setelah upload dilanjutkan.')

    def focus_last_template():
        ui.template_carousel.index = len(templates) - 1

    def palm_screen(state='ready', progress=0.0, needs_release=False):
        ui.show_capture('Sesi 1 dari 24 · Special Day', 1, synthetic_portrait(0))
        ui.set_palm_status(state, progress, needs_release)

    def payment_demo():
        ui.show_payment('Special Day · 1 lembar', 1, 10000, lambda: None, lambda: None)

    def expired_payment():
        from datetime import timedelta
        ui.payment.current.expires_at -= timedelta(hours=1)
        ui._refresh_payment()

    # Additional states catch issues hidden by the six happy-path screenshots:
    # scrolling to the last template, active countdown, an exhausted retake,
    # local-only output, and a next-session action without a completion timer.
    scenes = (
        ('advert', lambda: ui.show_advertisement(True, 'Kamera siap'), None),
        ('advert-invitation', lambda: ui.show_advertisement(True, 'Kamera siap'), ui.show_face_invitation),
        ('welcome', lambda: ui.show_welcome(True, STATUS), None),
        ('templates', cart, None),
        ('templates-empty', lambda: ui.show_template_selection(True, STATUS), None),
        ('templates-one', single_template, None),
        ('templates-status', lambda: ui.show_template_selection(
            True, LONG_STATUS, storage_ready=False, quantities={'template_a': 2}), None),
        ('templates-last', cart, focus_last_template),
        ('payment', lambda: ui.show_payment('\n'.join(f'{t.name} × 2' for t in templates),
                                           len(templates), len(templates) * 15000,
                                           lambda: None, lambda: None), None),
        ('payment-waiting', lambda: ui.show_payment('Template 1 · 2 lembar',
                                                   1, 15000, lambda: None, lambda: None),
         lambda: ui.set_camera_status(False)),
        ('payment-print-offer', payment_demo, ui._offer_payment_print),
        ('payment-enlarged', payment_demo, ui.show_payment_enlargement),
        ('payment-expired', payment_demo, expired_payment),
        ('capture', lambda: ui.show_capture('Sesi 1 dari 24 · Special Day', 1, synthetic_portrait(0)), None),
        ('capture-waiting', lambda: ui.show_capture('Sesi 1 dari 24 · Special Day', 1, synthetic_portrait(0)),
         lambda: ui.set_camera_status(False)),
        ('countdown', lambda: (ui.show_capture('Sesi 1 dari 24 · Special Day', 1, synthetic_portrait(0)),
                               ui.set_countdown(5)), None),
        ('retake-ready', lambda: ui.show_capture('Sesi 1 dari 24 · Special Day', 3, synthetic_portrait(0),
                                                action_label='AMBIL FOTO PENGGANTI', is_retake=True), None),
        ('retake-countdown', lambda: (ui.show_capture('Sesi 1 dari 24 · Special Day', 3, synthetic_portrait(0),
                                                     action_label='RETAKE FOTO TERPILIH', is_retake=True),
                                      ui.set_countdown(5, is_retake=True)), None),
        ('palm-ready', palm_screen, None),
        ('palm-hold', lambda: palm_screen(progress=.7), None),
        ('palm-release', lambda: palm_screen(needs_release=True), None),
        ('palm-loading', lambda: palm_screen(state='loading'), None),
        ('palm-unavailable', lambda: palm_screen(state='unavailable'), None),
        ('review', lambda: ui.show_review(paths, 'Sesi 1 dari 24 · Special Day', 1, True), None),
        ('review-used', lambda: ui.show_review(paths, 'Sesi 1 dari 24 · Special Day', 1, False), None),
        ('review-waiting', lambda: ui.show_review(paths, 'Sesi 1 dari 24 · Special Day', 1, True),
         lambda: ui.set_camera_status(False)),
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
            stage = next((w for w in ui.content.children if isinstance(w, ScrollView)), None)
            fits = stage is None or stage.children[0].height <= stage.height + 1
            if not fits:
                raise AssertionError(f'{name} has a clipped desktop stage at {size}')
            if ui.current_screen == 'capture':
                # Window visibility alone does not detect overlap with the
                # camera footer. The image and empty state must fit their slot.
                slot = bounds(ui.preview.parent)
                for widget in (ui.preview, ui.camera_wait_hint):
                    box = bounds(widget)
                    if (box[0] < slot[0] - 1 or box[1] < slot[1] - 1
                            or box[2] > slot[2] + 1 or box[3] > slot[3] + 1):
                        raise AssertionError(f'Preview overlay leaves its slot in {name} at {size}')
                # Labels constrained to a fixed text_size can hide overflow in
                # texture_size. Measure their natural wrapped height instead.
                hint = ui.capture_hint
                natural = CoreLabel(text=hint.text, font_name=hint.font_name,
                                    font_size=hint.font_size, text_size=(hint.width, None))
                natural.refresh()
                if not fully_visible(hint) or natural.texture.size[1] > hint.height + 1:
                    raise AssertionError(f'Capture guidance is clipped in {name} at {size}')
                if name in PALM_SCREENS and ui.capture_button.disabled:
                    raise AssertionError(f'Palm state must preserve button capture in {name}')
            decoded = None
            if name in ('payment', 'payment-waiting', 'payment-print-offer', 'payment-enlarged'):
                decoded = screenshot_qr(path, ui.payment_qr)
                if decoded != ui.payment.current.payload:
                    raise AssertionError(f'Demo QR is unreadable in {path}')
                if ui._inline_offer is not None:
                    offer = bounds(ui._inline_offer)
                    qr_column = bounds(ui.payment_details)
                    if offer[2] > qr_column[0]:
                        raise AssertionError(f'Payment offer covers the QR column in {path}')
            elif name in ('result', 'result-next'):
                decoded = screenshot_qr(path, ui.qr_view)
                if decoded != FOLDER_URL:
                    raise AssertionError(f'Folder QR is unreadable in {path}')
            elif name == 'result-local' and ui.qr_view.texture is not None:
                raise AssertionError('A local-only result must not have a fabricated Drive QR')
            if name == 'capture-waiting' and ui.preview.texture is not None:
                raise AssertionError('A stale frame must not be displayed as a live preview')
            if name in RETAKE_SCREENS:
                if not fully_visible(ui.capture_button) or not fully_visible(ui.countdown):
                    raise AssertionError(f'Retake shutter/countdown is clipped in {name} at {size}')
                if name == 'retake-ready':
                    if (ui.countdown.text != 'Siap?' or ui.capture_button.disabled
                            or ui.capture_button.text != 'AMBIL FOTO PENGGANTI'):
                        raise AssertionError('Retake preview must wait with an enabled shutter')
                elif ui.countdown.text != '5' or not ui.capture_button.disabled:
                    raise AssertionError('Retake countdown must disable the shutter')
            if name == 'payment-waiting' and not ui.payment_confirm.disabled:
                raise AssertionError('Payment confirmation needs a fresh camera frame')
            if name in ('review-used', 'review-waiting') and not ui.retake_button.disabled:
                raise AssertionError('Retake must be disabled when its quota or camera is unavailable')
            record = {'screen': name, 'size': list(size), 'file': path.name,
                      'stage_fits': fits, 'decoded_qr': decoded}
            if name in PALM_SCREENS:
                record['palm_hint'] = ui.capture_hint.text
                record['button_capture_available'] = not ui.capture_button.disabled
            if name == 'templates-status':
                if (not ui.status.is_shortened or ui.status_details.disabled
                        or ui.status_details.parent is not ui._footer_row
                        or not fully_visible(ui.status_details)):
                    raise AssertionError('Long status needs a visible, reachable details action')
                if not ui.start_button.disabled or ui.cart_total.text != 'Rp15.000':
                    raise AssertionError('Showing diagnostics must preserve the order/storage gate')
                record['status_shortened'] = True
                record['status_details_visible'] = True
            elif ui.status_details.parent is not None:
                raise AssertionError(f'A short status should not reserve a details action in {name}')
            disabled = [widget for widget in ui.content.walk()
                        if isinstance(widget, Button) and widget.disabled and fully_visible(widget)]
            if disabled:
                measured = [button_contrast(path, widget) for widget in disabled]
                for control in measured:
                    if control['ratio'] < 4.5:
                        raise AssertionError(f'Unreadable disabled label in {name}: {control}')
                record['disabled_text_contrast'] = measured
            if ui.current_screen == 'review':
                # A visible thumbnail can still misrepresent the final crop.
                # Compare its real texture against the saved composition, not
                # against a second call to the same thumbnail implementation.
                thumbnails = sorted((widget for widget in ui.content.walk()
                                     if isinstance(widget, KivyImage)), key=lambda w: w.x)
                if len(thumbnails) != 3:
                    raise AssertionError(f'{name} must show all three review frames')
                with Image.open(result) as composition:
                    for index, widget in enumerate(thumbnails):
                        frame = templates[0].apertures[index]
                        if widget.texture.size != frame.size:
                            raise AssertionError(f'{name} shows a different photo aperture')
                        shown = Image.frombytes('RGBA', widget.texture.size,
                                                widget.texture.pixels).convert('RGB')
                        saved = composition.crop(frame.box)
                        if shown.tobytes() != saved.tobytes():
                            raise AssertionError(f'{name} differs from its saved result frame')
                record['review_frame_sizes'] = [list(frame.size) for frame in templates[0].apertures]
                record['review_matches_output'] = True
            if ui.current_screen == 'templates':
                selected = [key for key, card in ui._template_cards.items() if card.selected]
                expected = [key for key, quantity in ui.quantities.items() if quantity > 0]
                if selected != expected:
                    raise AssertionError(f'Selection outline disagrees with the order in {name}')
                for key, quantity in ui.quantities.items():
                    if ui.quantity_buttons[key][0].disabled != (quantity == 0):
                        raise AssertionError(f'Decrement gate disagrees with quantity in {name}')
                record['selected_templates'] = selected
                record['quantities'] = dict(ui.quantities)
            records.append(record)
            print(f'PASS {name} {width}x{height}', flush=True)
        except Exception as error:
            errors.append(str(error))
            host.stop()

    # Schedule each capture relative to its own completed setup, not relative
    # to process startup. Font/plugin initialization can take longer than the
    # first absolute deadline; the old schedule then ran setup and capture in
    # one frame, before layout, and falsely reported a clipped welcome screen.
    # Chaining also prevents expensive pixel checks from overlapping the next
    # scene. Keep layout assertions strict instead of hiding a failed render.
    jobs = iter((size, name, build, after_layout)
                for size in SIZES for name, build, after_layout in scenes)

    def advance(_dt):
        job = next(jobs, None)
        if job is None:
            host.stop()
            return
        size, name, build, after_layout = job
        Window.size = size
        # A waiting-camera fixture must not leak into the next healthy scene.
        ui.set_camera_status(True)
        ui.set_palm_status('disabled')  # A gesture fixture must not leak into the next scene.
        build()
        if after_layout is not None:
            Clock.schedule_once(lambda _dt: after_layout(), .15)

        # Clock time is fixed for the duration of one frame. Creating twelve
        # preview textures can take longer than 350ms on a software-rendered
        # runner, so schedule_once(.35) can already be due on the first layout
        # frame. Wait in wall time and require stable widget geometry instead.
        # Keep every clipping, QR and contrast assertion below unchanged.
        prepared_at = time.monotonic()
        last_geometry = None
        stable_frames = 0

        def capture_when_settled(_dt):
            nonlocal last_geometry, stable_frames
            elapsed = time.monotonic() - prepared_at
            geometry = tuple((round(widget.x, 2), round(widget.y, 2),
                              round(widget.width, 2), round(widget.height, 2))
                             for widget in ui.content.walk(restrict=True))
            if geometry == last_geometry and ui.content.opacity >= .999:
                stable_frames += 1
            else:
                stable_frames = 0
            last_geometry = geometry
            if elapsed >= .35 and stable_frames >= 2:
                capture(name, size)
                if not errors:
                    Clock.schedule_once(advance, .15)
                return False
            if elapsed > 5:
                errors.append(f"Layout did not settle in {name} at {size}")
                host.stop()
                return False
            return True
        Clock.schedule_interval(capture_when_settled, 0)

    Clock.schedule_once(advance, .1)
    host.run()
    (output / 'report.json').write_text(json.dumps({'renders': records, 'errors': errors}, indent=2) + '\n')
    if errors:
        raise SystemExit('\n'.join(errors))
    for size in SIZES:
        overview(output, size)
        overview(output, size, STATE_SCREENS, 'states')
        overview(output, size, SELECTION_SCREENS, 'selection')
        overview(output, size, DIAGNOSTIC_SCREENS, 'diagnostics')
        overview(output, size, RETAKE_SCREENS, 'retake')
        overview(output, size, PALM_SCREENS, 'palm')
        overview(output, size, ADVERTISING_SCREENS, 'advertising')
    print(f'{len(records)} real-widget renders saved in {output}')


if __name__ == '__main__':
    main()
