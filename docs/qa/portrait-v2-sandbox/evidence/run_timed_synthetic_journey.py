"""Real Kivy event-loop replay with synthetic devices and actual 5s/30s timers.

Run from an isolated checkout with the declared test dependencies. No owner
root, real camera, printer, merchant or cloud account is used. Only allowlisted
counts, phases and timings are emitted; no private proof is saved or logged.
"""
from pathlib import Path
import argparse
import json
import os
import sys
import tempfile
import time
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
os.environ.update(PHOTOBOOTH_LOCAL_ONLY='1', PHOTOBOOTH_CAMERA='0',
    PHOTOBOOTH_AUDIO='0', PHOTOBOOTH_AD_VIDEO='0', PHOTOBOOTH_FACE_TRIGGER='0',
    PHOTOBOOTH_PALM_TRIGGER='0', PHOTOBOOTH_V2_PRINT='0', PHOTOBOOTH_V2_DRIVE='0',
    PHOTOBOOTH_V2_CHECKOUT_SANDBOX='0', PHOTOBOOTH_V2_CHECKOUT_MOCK='0')

import numpy as np
from kivy.clock import Clock
from kivy.core.window import Window
from photobooth.kiosk_v2.post_preview_checkout_app import PrivateCheckoutFixtureApp
from photobooth.kiosk_v2.flow import ADVERT, TUTORIAL, TEMPLATES
from tests.post_preview_checkout_fixture import CheckoutFixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', choices=('452x900', '800x1280'), default='452x900')
    args = parser.parse_args()
    layout = tuple(int(value) for value in args.size.split('x'))
    began = time.monotonic()
    record = {'state': 'RUNNING', 'mode': 'SYNTHETIC_ONLY', 'clock': 'REAL_MONOTONIC',
              'countdowns_started': 0, 'retakes_requested': 0, 'layout': args.size}
    with tempfile.TemporaryDirectory(prefix='meong-timed-synthetic-') as folder:
        fixture = CheckoutFixture(Path(folder))
        fixture.enable_paid_ticket()
        fixture.enable_paid_delivery()
        camera = Mock()
        camera.read.side_effect = lambda: np.zeros((32, 48, 3), dtype=np.uint8)
        camera.preview.return_value = None
        camera.capture.isOpened.return_value = True

        def paid(payment):
            fixture.provider.state(payment['attempts'][-1]['provider_order_id'], 'settlement')

        app = PrivateCheckoutFixtureApp(Path(folder), private_service=fixture.service,
            camera_device=camera, synthetic_pay_callback=paid)
        original_build = app.build

        def build():
            stage = original_build()
            fixture.bind_app(app)
            return stage

        app.build = build
        automation = [None]
        original_ticket_next = app._ticket_next

        def ticket_next(*, user=True):
            window = app._ticket_window
            started = window._started_at if window is not None else None
            had_card = app._ticket_card is not None
            original_ticket_next(user=user)
            if had_card and app._ticket_card is None and started is not None:
                # Measure genuine visible ACK -> actual private QR/card wipe,
                # excluding later dismissal/Drive/print worker processing.
                record['ticket_visible_seconds'] = round(time.monotonic()-started, 3)
                record['ticket_auto_dismissed'] = user is False

        app._ticket_next = ticket_next

        def button(text):
            matches = [w for w in app.stage.walk() if getattr(w, 'text', None) == text]
            if len(matches) != 1 or matches[0].disabled:
                raise RuntimeError('EXPECTED_ACTION_UNAVAILABLE')
            matches[0].dispatch('on_release')

        def stop_error(code):
            record.update(state='FAILED', stage=code)
            app.stop()

        def drive(_dt):
            try:
                if time.monotonic()-began > 180:
                    return stop_error('TIMEOUT')
                if not hasattr(app, '_photo_view') or app._photo_jobs.busy:
                    return
                if app._photo_error:
                    return stop_error('PHOTO_WORKER_HOLD')
                view = app._photo_view
                phase = view.get('phase')
                record['last_phase'] = phase
                if app.navigation.page == ADVERT:
                    app._choose_photo()
                elif app.navigation.page == TUTORIAL:
                    app._complete_tutorial()
                elif app.navigation.page == TEMPLATES:
                    app.quantities.update(template_a=2, template_b=1)
                    app._enter_photo_test()
                elif phase == 'confirm' and app._photo_prepared:
                    app._admit_photo_test()
                elif phase == 'capture':
                    if app._countdown_event is None:
                        app._start_countdown()
                        record['countdowns_started'] += 1
                elif phase == 'review':
                    if not view['retake_used']:
                        app._photo_submit('retake', 1)
                        record['retakes_requested'] += 1
                    else:
                        button('PAKAI FOTO INI • BUAT STRIP')
                elif phase == 'result':
                    button('LANJUT')
                elif phase == 'final_preview':
                    record['preview_amount'] = view['amount']
                    button('LANJUT CHECKOUT SIMULASI')
                elif phase == 'checkout_ready':
                    button('SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
                elif phase == 'payment_pending':
                    button('SIMULASI PAID • TANPA TRANSFER')
                elif phase == 'paid_delivery':
                    if not view['delivery']['print_all_submitted']:
                        button('CETAK FOTO YANG SUDAH DIBAYAR')
                    else:
                        record.update(state='PASS', seconds=round(time.monotonic()-began, 3),
                            charges=fixture.provider.charges, receipts=len(fixture.receipt_sizes),
                            print_copies=[copies for _path, copies in fixture.paid_print_sends],
                            private_jpegs=len(list(fixture.service.photos.root.rglob('*.jpg'))),
                            obligation=view['delivery']['service_status'],
                            physical_paper_verified=view['delivery']['physical_paper_verified'])
                        if (record['countdowns_started'] != 8 or record['retakes_requested'] != 2
                                or record['charges'] != 1 or record['receipts'] != 1
                                or record['print_copies'] != [2, 1] or record['private_jpegs'] != 8
                                or record['preview_amount'] != 25000
                                or record.get('ticket_visible_seconds', 0) < 30
                                or not record.get('ticket_auto_dismissed')
                                or record['obligation'] != 'OWED' or record['physical_paper_verified']):
                            return stop_error('FINAL_INVARIANT_MISMATCH')
                        app.stop()
            except Exception:
                stop_error('AUTOMATION_EXCEPTION_AT_'+str(record.get('last_phase')))

        def start(_app):
            Window.size = layout
            automation[0] = Clock.schedule_interval(drive, .05)

        app.bind(on_start=start)
        try:
            app.run()
        finally:
            if automation[0] is not None:
                automation[0].cancel()
            if getattr(app, '_photo_jobs', None):
                app._photo_jobs.close()
                app._photo_jobs.wait_closed(10)
            fixture.close()
    os.write(1, (json.dumps(record, sort_keys=True)+'\n').encode())
    return 0 if record['state'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
