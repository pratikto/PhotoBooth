"""Render the main QRIS page in a running Kivy host and decode screen pixels.

All QR payloads are explicitly non-payable fixtures. No camera, merchant key,
real provider, customer file, or physical printer is used.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('KIVY_NO_ARGS', '1')
os.environ.setdefault('PHOTOBOOTH_AUDIO', '0')
os.environ.setdefault('PHOTOBOOTH_AD_VIDEO', '0')

from kivy.clock import Clock
from kivy.core.window import Window
from photobooth.catalog import get_templates
from photobooth.qr_code import create_qr_image
from photobooth.ui_kivy import KivyHost, PhotoBoothUI
from photobooth.ui_qris import QrisPaymentPage
from tools.render_gui import fully_visible, screenshot_qr

PAYLOAD = 'MEONG MOCK ONLY - NOT QRIS - MOCKGUI0001'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    output = parser.parse_args().output_dir
    output.mkdir(parents=True, exist_ok=True)
    host = KivyHost(lambda: None)
    callbacks = {key: lambda *_: None for key in ('on_home_start','on_start','on_capture',
        'on_select_photo','on_retake','on_accept_session','on_next_session','on_finish','on_close')}
    ui = PhotoBoothUI(host, get_templates(), **callbacks)
    jobs = iter((size, phase) for size in [(1200,800), (800,600)]
                for phase in ['WAITING', 'CANCELLING', 'RECOVERY'])
    results, errors = [], []

    def advance(_dt):
        job = next(jobs, None)
        if job is None:
            host.stop(); return
        size, phase = job
        Window.size = size
        visit = {'context': {'mode':'mock'}, 'checkout_key':'a'*32, 'amount':15000,
            'phase':phase, 'order':{'order_id':'MOCKGUI0001', 'expires_at':time.time()+240}}
        page = QrisPaymentPage(ui, visit, retry=lambda:None, cancel=lambda:None, edit=lambda:None)
        page.image(create_qr_image(PAYLOAD, with_logo=False))
        page.update(visit, False, 'Order tetap tersimpan. Jangan bayar ulang.' if phase == 'RECOVERY' else '')
        prepared = time.monotonic()
        last, stable = None, 0

        def settle(_dt):
            nonlocal last, stable
            geometry = tuple((round(w.x,2),round(w.y,2),round(w.width,2),round(w.height,2))
                             for w in ui.content.walk(restrict=True))
            stable = stable + 1 if geometry == last and ui.content.opacity >= .999 else 0
            last = geometry
            if time.monotonic()-prepared > 6:
                errors.append(f'{phase} {size}: layout did not settle')
                host.stop(); return False
            if time.monotonic()-prepared < .35 or stable < 2:
                return True
            name = f'qris-{phase.lower()}-{size[0]}x{size[1]}.png'
            try:
                ui.shell.export_to_png(str(output/name))
                if phase == 'WAITING':
                    if not fully_visible(page.qr):
                        raise AssertionError('Payment QR is clipped by the viewport')
                    decoded = screenshot_qr(output/name, page.qr)
                    if decoded != PAYLOAD:
                        raise AssertionError('Rendered QR payload is not readable/identical')
                if not fully_visible(page.cancel) or not fully_visible(page.retry):
                    raise AssertionError('Payment controls leave viewport')
                results.append({'file':name,'size':size,'phase':phase,
                                'qr_decoded':phase == 'WAITING'})
            except Exception as error:
                errors.append(f'{phase} {size}: {error}')
                host.stop(); return False
            Clock.schedule_once(advance, .1)
            return False
        Clock.schedule_interval(settle, 0)

    Clock.schedule_once(advance, .1)
    host.run()
    (output/'qris-report.json').write_text(json.dumps({'renders':results,'errors':errors}, indent=2))
    if errors or len(results) != 6:
        raise SystemExit('\n'.join(errors) or 'Missing QRIS renders')
    print('QRIS visual gate: 6 renders, 2 exact screenshot QR decodes, 0 errors')


if __name__ == '__main__':
    main()
