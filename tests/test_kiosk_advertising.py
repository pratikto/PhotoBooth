"""Real-widget checks for idle media, nonmodal offers, QR pixels and audio ownership."""

from datetime import timedelta
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_GUI') == '1', 'GUI checks are opt-in')
class KioskAdvertisingTests(unittest.TestCase):
    def setUp(self):
        from kivy.core.window import Window
        from photobooth.audio import AudioManager, SOUND_NAMES
        from photobooth.catalog import get_templates
        from photobooth.ui_kivy import KivyHost, PhotoBoothUI
        from test_audio import FakeSound
        self.original_size = Window.size
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.environment = patch.dict(os.environ, {'PHOTOBOOTH_AUDIO': '1', 'PHOTOBOOTH_AD_VIDEO': '0',
                                                   'PHOTOBOOTH_PRINTER_HOST': ''})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.audio = AudioManager(Path(self.directory.name) / 'audio')
        self.audio._sounds = {name: FakeSound() for name in SOUND_NAMES}
        self.ui = PhotoBoothUI(KivyHost(lambda: None), get_templates(), audio_manager=self.audio,
                               kiosk_data_dir=Path(self.directory.name), on_start=lambda *_: None)
        self.ui.callbacks['on_home_start'] = lambda: self.ui.show_template_selection(True, 'Ready')
        Window.add_widget(self.ui.shell)
        self.ui.set_camera_status(True)
        self.settle()

    def tearDown(self):
        from kivy.core.window import Window
        self.ui.dispose()
        Window.remove_widget(self.ui.shell)
        Window.size = self.original_size

    def settle(self, seconds=.15):
        from kivy.base import EventLoop
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            EventLoop.idle()
        EventLoop.idle()

    def payment(self):
        self.ui.show_payment('Special Day x 1', 1, 5000, lambda: None, lambda: None)
        self.settle()

    def test_manual_entry_survives_missing_face_detection_and_idle_returns_only_landing_pages(self):
        self.ui.show_advertisement(False)
        self.settle()
        self.assertFalse(self.ui.advert_start_button.disabled)
        self.assertTrue(self.audio._advertising)
        self.ui.advert_start_button.dispatch('on_release')
        self.assertEqual(self.ui.current_screen, 'templates')
        self.assertFalse(self.audio._advertising)
        self.ui._last_activity = time.monotonic() - 171
        self.ui._kiosk_tick()
        self.assertEqual(self.ui._offer_kind, 'idle-warning')
        self.ui._kiosk_activity()
        self.assertIsNone(self.ui._inline_offer)
        self.ui._last_activity = time.monotonic() - 181
        self.ui._kiosk_tick()
        self.assertEqual(self.ui.current_screen, 'advert')
        self.payment()
        attempt = self.ui.payment.current
        self.ui._last_activity = time.monotonic() - 400
        self.ui._kiosk_tick()
        self.assertEqual(self.ui.current_screen, 'payment')
        self.assertIs(self.ui.payment.current, attempt)

    def test_face_offer_closes_after_fifteen_seconds_and_retired_touch_cannot_start(self):
        self.ui.show_advertisement(True)
        self.assertTrue(self.ui.show_face_invitation())
        retired = self.ui.offer_action
        deadline = self.ui._offer_deadline
        with patch('photobooth.ui_kiosk.time.monotonic', return_value=deadline + .01):
            self.ui._kiosk_tick()
        self.assertIsNone(self.ui._inline_offer)
        retired.dispatch('on_release')
        self.assertEqual(self.ui.current_screen, 'advert')
        self.assertFalse(self.ui.qris_printer.busy)

    def test_payment_offer_never_covers_qr_and_ignoring_it_keeps_same_pending_attempt(self):
        import cv2
        from kivy.core.window import Window
        for size in ((800, 600), (1200, 800), (1920, 1080)):
            with self.subTest(size=size):
                Window.size = size
                self.payment()
                attempt = self.ui.payment.current
                attempt.created_at -= timedelta(seconds=61)
                self.ui._kiosk_tick()
                self.settle()
                card = self.ui._inline_offer
                self.assertIs(card.parent, self.ui._ad_stage)
                left = card.to_window(*card.pos)[0]
                qr_left = self.ui.payment_details.to_window(*self.ui.payment_details.pos)[0]
                self.assertLessEqual(left + card.width, qr_left)
                path = Path(self.directory.name) / f'payment-{size[0]}.png'
                self.ui.shell.export_to_png(str(path))
                decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(path)))
                self.assertEqual(decoded, attempt.payload)
                with patch('photobooth.ui_kiosk.time.monotonic', return_value=self.ui._offer_deadline + .01):
                    self.ui._kiosk_tick()
                self.assertIsNone(self.ui._inline_offer)
                self.assertIs(self.ui.payment.current, attempt)
                self.assertEqual(attempt.state, 'pending')
                self.assertFalse(self.ui.qris_printer.busy)

    def test_print_preserves_qr_and_amount_and_preview_is_not_marked_as_payment(self):
        self.payment()
        attempt = self.ui.payment.current
        original = attempt.snapshot()
        with patch.object(self.ui.qris_printer, 'submit', wraps=self.ui.qris_printer.submit) as submit:
            self.ui.payment_print.dispatch('on_release')
            self.ui.payment_print.dispatch('on_release')
            self.assertEqual(submit.call_count, 1)
        end = time.monotonic() + 3
        while time.monotonic() < end and self.ui._offer_kind != 'print-result':
            self.settle(.05)
            self.ui._kiosk_tick()
        self.assertEqual(self.ui._offer_kind, 'print-result')
        self.assertIn('belum dikonfigurasi', self.ui.offer_message.text)
        self.assertEqual(attempt, original)
        self.assertFalse(self.ui._payment_submitted)
        self.assertEqual(self.ui.current_screen, 'payment')

    def test_renewed_qr_is_the_one_confirmed_and_old_print_touches_are_invalidated(self):
        self.payment()
        old = self.ui.payment.current
        old.expires_at -= timedelta(hours=1)
        self.ui._refresh_payment()
        retired = self.ui.offer_action
        with patch.object(self.ui.qris_printer, 'submit', return_value=True):
            self.ui.offer_action.dispatch('on_release')
        current = self.ui.payment.current
        self.assertNotEqual(current.attempt_id, old.attempt_id)
        self.assertEqual(current.amount, old.amount)
        self.assertEqual(old.state, 'expired')
        retired.dispatch('on_release')
        self.assertIs(self.ui.payment.current, current)
        self.ui.payment_confirm.dispatch('on_release')
        self.assertEqual(current.state, 'paid')
        self.assertIsNone(self.ui._inline_offer)
        self.assertEqual(old.state, 'expired')

    def test_enlargement_uses_the_ad_column_and_pauses_its_exposure_timer(self):
        self.payment()
        self.ui.payment_enlarge.dispatch('on_release')
        self.assertIs(self.ui._enlarged.parent, self.ui._ad_stage)
        self.assertTrue(self.ui._ad_player._paused)
        self.assertIsNotNone(self.ui.payment_qr.texture)
        self.ui._close_enlargement()
        self.assertFalse(self.ui._ad_player._paused)

    def test_a_still_active_qr_near_expiry_prints_without_renewal(self):
        from datetime import datetime, timezone
        self.payment()
        attempt = self.ui.payment.current
        attempt.expires_at = datetime.now(timezone.utc) + timedelta(seconds=10)
        before = attempt.snapshot()
        with patch.object(self.ui.qris_printer, 'submit', return_value=True) as submit:
            self.ui._request_payment_print()
        submit.assert_called_once_with(attempt)
        self.assertEqual(attempt, before)
        self.assertIs(self.ui.payment.current, attempt)

    def test_confirmed_success_from_a_status_tick_advances_exactly_once(self):
        from unittest.mock import Mock
        advance = Mock()
        self.ui.show_payment('Special Day x 1', 1, 5000, advance, lambda: None)
        attempt = self.ui.payment.current
        self.ui.payment.gateway.simulate_success(attempt)
        self.ui._kiosk_tick()
        self.ui._kiosk_tick()
        advance.assert_called_once_with()
        self.assertTrue(self.ui._payment_submitted)

    def test_connection_timeout_preserves_qr_and_order_and_does_not_offer_renewal(self):
        self.payment()
        attempt = self.ui.payment.current
        with patch.object(self.ui.payment.gateway, 'status', side_effect=TimeoutError('offline')):
            self.ui._refresh_payment()
            self.ui._request_payment_print()
            self.ui._renew_and_print()
        self.assertIs(self.ui.payment.current, attempt)
        self.assertEqual(attempt.state, 'pending')
        self.assertFalse(self.ui.qris_printer.busy)
        self.assertIsNone(self.ui._inline_offer)

    def test_changing_advertisements_does_not_replace_or_move_the_payment_qr(self):
        self.payment()
        attempt, texture = self.ui.payment.current, self.ui.payment_qr.texture
        position = self.ui.payment_qr.to_window(*self.ui.payment_qr.pos)
        self.ui._ad_player.next()
        self.settle()
        self.assertIs(self.ui.payment.current, attempt)
        self.assertIs(self.ui.payment_qr.texture, texture)
        self.assertEqual(self.ui.payment_qr.to_window(*self.ui.payment_qr.pos), position)

    @unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_VIDEO') == '1' and shutil.which('ffmpeg'),
                         'Native video checks require opt-in and ffmpeg')
    def test_native_video_has_frames_payment_is_muted_and_retiring_unloads_decoder(self):
        from photobooth.advertising import AdCatalog, summarize_events
        # Generate a tiny video with an audio stream at test time. No sample
        # videos or binaries are downloaded, required in Git, or uploaded.
        root = Path(self.directory.name)
        fixture = root / 'fixture.mp4'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i',
                        'testsrc2=size=192x128:rate=10', '-f', 'lavfi', '-i',
                        'sine=frequency=660:sample_rate=22050', '-t', '2',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(fixture)], check=True)
        config = root / 'fixture.json'
        poster = Path(__file__).resolve().parents[1] / 'photobooth/assets/ads/sample-01.jpg'
        config.write_text(json.dumps({'ads': [
            {'id': 'fixture-video', 'file': str(fixture), 'placements': ['idle', 'payment']},
            {'id': 'fixture-still', 'file': str(poster), 'placements': ['idle', 'payment']},
        ]}))
        self.ui.ad_catalog = AdCatalog(config)
        with patch.dict(os.environ, {'PHOTOBOOTH_AD_VIDEO': '1'}):
            self.ui.show_advertisement(True)
            self.settle(.1)
            player = self.ui._ad_player
            end = time.monotonic() + 8
            while time.monotonic() < end and not player._ready:
                self.settle(.05)
            self.assertTrue(player._ready, 'Native idle video did not deliver a texture')
            video = player.video
            self.assertIsNotNone(video.texture)
            self.assertGreater(video.volume, 0)
            self.ui.show_face_invitation()
            self.assertAlmostEqual(video.volume, self.audio.levels.ads * .35)
            self.ui._close_inline_offer()
            self.assertAlmostEqual(video.volume, self.audio.levels.ads)
            self.ui.advert_start_button.dispatch('on_release')
            self.assertIsNone(video._video)
            self.assertTrue(player._closed)
            self.payment()
            player = self.ui._ad_player
            end = time.monotonic() + 8
            while time.monotonic() < end and not player._ready:
                self.settle(.05)
            self.assertTrue(player._ready, 'Native payment video did not deliver a texture')
            self.audio.set_volume('ads', 1)
            self.ui._update_ad_volume()
            self.assertEqual(player.video.volume, 0)
            self.assertFalse(self.audio._advertising)
            self.ui.pause_media()
            self.assertEqual(player.video.state, 'pause')
            self.ui.resume_media()
            self.assertEqual(player.video.volume, 0)
            end = time.monotonic() + 6
            while time.monotonic() < end and player.ad_id != 'fixture-still':
                self.settle(.05)
            self.assertEqual(player.ad_id, 'fixture-still', 'EOS did not advance to the next photo')
            video_rows = [row for row in summarize_events(self.ui.ad_events.path)
                          if row['ad_id'] == 'fixture-video' and row['placement'] == 'payment']
            self.assertEqual(len(video_rows), 1)
            self.assertEqual(video_rows[0]['completed'], 1)
            self.assertGreater(video_rows[0]['displayed_seconds'], 1)
