"""Real main-GUI QRIS admission, capture and result flow with fake devices."""
from contextlib import ExitStack
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class QrisGuiTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        from photobooth.app_qris import QrisPhotoBoothApp
        from photobooth.checkout_backend import CheckoutBackend
        from photobooth.checkout_store import CheckoutStore
        from photobooth.qris_mock import MockQrisProvider
        from photobooth.qris_session import KioskCheckout
        from test_qris_session import LocalClient
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        directory = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.now = [time.time()]
        self.provider = MockQrisProvider(directory/'provider.db', settle_after=8, now=lambda:self.now[0])
        self.store = CheckoutStore(directory/'orders.db', now=lambda:self.now[0])
        self.addCleanup(self.provider.close); self.addCleanup(self.store.close)
        backend = CheckoutBackend(self.store, self.provider, 'mock-key', 'MOCK')
        flow = KioskCheckout(directory/'visit.json', LocalClient(backend), mode='mock',
                             booth_id='PB001', endpoint='http://127.0.0.1:8765')
        frame = np.full((240, 320, 3), (45, 120, 180), dtype=np.uint8)
        camera = SimpleNamespace(open=lambda:True, read=lambda:frame, close=lambda:None)
        self.stack.enter_context(patch('photobooth.app.PROJECT_ROOT', directory))
        self.stack.enter_context(patch('photobooth.app.Camera', return_value=camera))
        self.stack.enter_context(patch('photobooth.app.AppsScriptDriveClient.from_configuration', return_value=None))
        self.stack.enter_context(patch('photobooth.app.GoogleDriveClient.from_environment', return_value=None))
        self.stack.enter_context(patch('photobooth.app.KivyHost.after', return_value=SimpleNamespace(cancel=lambda:None)))
        self.stack.enter_context(patch.dict(os.environ, {'PHOTOBOOTH_LOCAL_ONLY':'1',
            'PHOTOBOOTH_PALM_TRIGGER':'0', 'PHOTOBOOTH_FACE_TRIGGER':'0', 'MEONG_QRIS_MOCK_PRINT':'0'}))
        self.app = QrisPhotoBoothApp(checkout=flow)
        self.addCleanup(self.app.close)
        self.app._connect_camera()
        self.app._open_template_selection()

    def pump_until(self, predicate):
        from kivy.clock import Clock
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            self.app.qris_next = 0
            self.app._qris_tick()
            Clock.tick()
            if predicate(): return
            time.sleep(.005)
        self.fail('QRIS did not reach the expected state: ' + str(self.app.checkout.snapshot()))

    def begin(self, quantities=None):
        self.app._open_dummy_payment(quantities or {'template_a':2})
        self.assertEqual(self.app.ui.current_screen, 'payment')
        self.pump_until(lambda:self.app.checkout.snapshot()['phase'] == 'WAITING' and self.app.qris_image_order)
        self.assertIsNone(self.app.transaction)

    def paid(self):
        self.now[0] += 10
        self.pump_until(lambda:self.app.ui.current_screen == 'capture')

    def test_payment_opens_capture_automatically_exactly_once(self):
        self.begin(); self.paid()
        transaction = self.app.transaction
        visit = self.app.checkout.snapshot()
        self.assertEqual(visit['phase'], 'STARTED')
        self.assertEqual(transaction.manifest['payment']['grant_id'], visit['order']['grant_id'])
        for _ in range(20): self.app._qris_tick()
        self.assertIs(self.app.transaction, transaction)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkouts').fetchone()[0], 1)

    def test_no_camera_retains_paid_permit_until_device_returns(self):
        self.begin()
        self.app.camera_ready = False
        self.app.ui.set_camera_status(False)
        self.now[0] += 10
        self.pump_until(lambda:self.app.checkout.snapshot()['phase'] == 'RESERVED')
        self.assertIsNone(self.app.transaction)
        self.app.camera_ready = True
        self.app.ui.set_camera_status(True)
        self.pump_until(lambda:self.app.ui.current_screen == 'capture')

    def test_pending_checkout_cannot_return_to_another_customer(self):
        self.begin()
        self.app._open_template_selection({'template_a':1})
        self.assertEqual(self.app.ui.current_screen, 'payment')
        self.assertEqual(self.app.checkout.snapshot()['quantities'], {'template_a':2})
        self.app._return_to_advertisements()
        self.assertEqual(self.app.ui.current_screen, 'payment')

    def test_two_template_capture_retake_result_and_completion(self):
        self.begin({'template_a':2, 'template_b':1}); self.paid()
        transaction = self.app.transaction
        for _ in range(3): self.app._save_current_frame(False)
        self.assertEqual(self.app.ui.current_screen, 'review')
        self.app._select_photo(1)
        self.app._save_current_frame(True)
        self.assertTrue(self.app.current_session.retake_used)
        with patch.object(self.app.printer, 'print_image') as paper:
            self.app._accept_current_session()
            self.assertEqual(self.app.ui.current_screen, 'result')
            self.app._start_next_session()
            for _ in range(3): self.app._save_current_frame(False)
            self.app._accept_current_session()
            self.assertEqual(self.app.ui.current_screen, 'result')
            self.app._finish_transaction()
            self.pump_until(lambda:self.app.ui.current_screen == 'advert')
            paper.assert_not_called()
        manifest = json.loads(transaction.manifest_path.read_text())
        self.assertEqual(manifest['status'], 'COMPLETED')
        self.assertEqual(manifest['payment']['amount'], 25000)
        self.assertEqual([row['print_copies'] for row in manifest['sessions']], [2, 1])
        self.assertEqual(self.app.checkout.snapshot()['phase'], 'COMPLETED')
        for row in manifest['sessions']:
            self.assertTrue((transaction.folder_path / row['output_path']).is_file())

    def test_stale_demo_confirmation_cannot_open_unpaid_capture(self):
        self.begin()
        self.assertFalse(self.app._start_transaction({'template_a':2}))
        self.assertIsNone(self.app.transaction)

    def test_manifest_failure_cannot_open_capture(self):
        self.begin()
        self.now[0] += 10
        with patch.object(self.app.store, '_write_manifest', side_effect=OSError('disk full')):
            self.pump_until(lambda:self.app.checkout.snapshot()['phase'] == 'RECOVERY')
        self.assertEqual(self.app.ui.current_screen, 'payment')

    def test_payment_layout_at_two_desktop_sizes(self):
        from kivy.clock import Clock
        from kivy.core.window import Window
        self.begin()
        # Stop only the controller's scheduled polling for stable screenshots;
        # ad/audio/layout still use real Kivy widgets and Clock events.
        self.app.qris_event.cancel()
        output = os.environ.get('MEONG_QRIS_GUI_OUTPUT')
        if not output:
            return
        root = Path(output); root.mkdir(parents=True, exist_ok=True)
        shell = self.app.ui.shell
        old_size = Window.size
        try:
            for width, height in [(1200,800), (800,600)]:
                Window.size = (width,height)
                shell.size_hint = (None,None); shell.size = (width,height); shell.pos=(0,0)
                for _ in range(30):
                    Clock.tick(); shell.do_layout(); time.sleep(.01)
                self.assertGreaterEqual(self.app.qris_page.qr.width, 200)
                self.assertGreaterEqual(self.app.qris_page.qr.height, 180)
                # Pixel evidence is rendered by tools/render_qris_gui.py in
                # a running host, not by exporting an unattached unit-test tree.
        finally: Window.size = old_size
