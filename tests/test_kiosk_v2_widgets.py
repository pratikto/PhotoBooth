"""Real-widget smoke for the isolated portrait v2 (run under Xvfb/Windows)."""

import os
import unittest

os.environ.setdefault("PHOTOBOOTH_AUDIO", "0")
os.environ.setdefault("PHOTOBOOTH_AD_VIDEO", "0")
os.environ.setdefault('PHOTOBOOTH_CAMERA', '0')
os.environ.setdefault('PHOTOBOOTH_FACE_TRIGGER', '0')
os.environ.setdefault('PHOTOBOOTH_PALM_TRIGGER', '0')
os.environ.setdefault("KIVY_NO_ARGS", "1")

try:
    import kivy  # noqa: F401
except ImportError:
    HAS_KIVY = False
else:
    HAS_KIVY = True
    # After Kivy is installed, errors in v2 imports must FAIL, not be skipped.
    from photobooth.kiosk_v2.app import PortraitKioskV2App, SwipeGallery
    from photobooth.kiosk_v2.illustrations import TutorialIcon
    from photobooth.kiosk_v2.theme import ArcadeButton
    from photobooth.kiosk_v2.flow import ADVERT, TEMPLATES, TUTORIAL, GAME_PREVIEW


@unittest.skipUnless(HAS_KIVY, "Kivy not available in pure-Python test environment")
class PortraitKivySmokeTests(unittest.TestCase):
    def test_idle_warmup_prepares_one_asset_per_turn_and_first_gallery_reuses_textures(self):
        from unittest.mock import patch
        from PIL import Image
        from photobooth.kiosk_v2.app import _portrait_strip_texture

        app = PortraitKioskV2App()
        app.build()
        preview = Image.new('RGB', (32, 96), '#8060c0')
        try:
            revision = app._view_revision
            with patch.object(app.audio_v2, 'prepare') as audio, \
                    patch.object(app._preview_preloader, 'get', return_value=preview), \
                    patch('photobooth.kiosk_v2.app._portrait_strip_texture', wraps=_portrait_strip_texture) as upload:
                for _ in range(4 + len(app.templates)):
                    before = audio.call_count + upload.call_count
                    app._warm_idle_assets(0)
                    self.assertEqual(audio.call_count + upload.call_count, before + 1)
                self.assertEqual([call.kwargs['names'] for call in audio.call_args_list],
                                 [('count',), ('shutter',), ('success',), ('game_music',)])
                self.assertEqual(len(app._textures), 12)
                self.assertEqual(app._view_revision, revision)
                self.assertFalse(any(app.quantities.values()))
                self.assertIs(app._warm_idle_assets(0), False)
                app._choose_photo()
                app._complete_tutorial()
                app._shift_template(1)
                self.assertEqual(upload.call_count, 12, 'First gallery navigation uploaded a new texture')
                self.assertIsNotNone(app._preview.texture)
        finally:
            app.on_stop()

    def test_idle_warmup_never_waits_for_cpu_or_runs_on_capture_minimize_or_close(self):
        from unittest.mock import patch
        from photobooth.kiosk_v2.flow import CAPTURE

        app = PortraitKioskV2App()
        app.build()
        app._idle_audio_pending.clear()
        try:
            with patch.object(app._preview_preloader, 'get', return_value=None) as get, \
                    patch('photobooth.kiosk_v2.app._portrait_strip_texture') as upload:
                self.assertIsNone(app._warm_idle_assets(0))
                self.assertEqual(get.call_count, 12)
                upload.assert_not_called()
                get.reset_mock()
                app.navigation.page = CAPTURE
                app._warm_idle_assets(0)
                app.navigation.page = ADVERT
                app.on_pause()
                app._warm_idle_assets(0)
                get.assert_not_called()
                app.on_stop()
                self.assertIs(app._warm_idle_assets(0), False)
                upload.assert_not_called()
        finally:
            app.on_stop()

    def test_reused_camera_texture_redraws_without_touch_countdown_or_text_changes(self):
        """Pixel uploads must reach the window even when all labels stay still."""
        from types import SimpleNamespace
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.graphics.opengl import glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE
        from kivy.uix.image import Image
        from kivy.uix.label import Label
        from photobooth.kiosk_v2.flow import CAPTURE
        from photobooth.kiosk_v2.live_preview import PreviewFrame
        from photobooth.kiosk_v2.performance import PerformanceLog
        from photobooth.kiosk_v2.photo_views import PhotoViews

        view = PhotoViews()
        view._init_photos()
        view.navigation = SimpleNamespace(page=CAPTURE)
        view._photo_jobs = SimpleNamespace(busy=False)
        view._live_image = Image(fit_mode='contain')
        view._camera_hint, view._count_label = Label(), Label()
        view._capture_button = SimpleNamespace(disabled=False)
        view.performance = PerformanceLog()
        frame = object()
        flips = []
        def record_flip(*_):
            flips.append(tuple(glReadPixels(int(Window.width / 2), int(Window.height / 2),
                                           1, 1, GL_RGBA, GL_UNSIGNED_BYTE)[:3]))
        Window.add_widget(view._live_image)
        Window.bind(on_flip=record_flip)
        try:
            def upload(color):
                packet = PreviewFrame(1, 0, (16, 12), bytes(color) * (16 * 12))
                view._update_live_photo(frame, packet)
                EventLoop.idle()
            upload((255, 0, 0))
            for _ in range(8):
                EventLoop.idle()
            texture = view._live_image.texture
            hint, count = view._camera_hint.text, view._count_label.text
            for color in ((0, 255, 0), (0, 0, 255), (255, 0, 0)) * 2:
                before = len(flips)
                upload(color)
                self.assertGreater(len(flips), before, 'New camera pixels never reached a window redraw')
                self.assertEqual(flips[-1], color, 'The window still displays old camera pixels')
                self.assertIs(view._live_image.texture, texture)
                self.assertEqual(view._camera_hint.text, hint)
                self.assertEqual(view._count_label.text, count)
            # Polling the same packet must not force an unnecessary redraw.
            for _ in range(4):
                EventLoop.idle()
            before = len(flips)
            view._update_live_photo(frame, view._last_preview)
            EventLoop.idle()
            self.assertEqual(len(flips), before)
        finally:
            Window.unbind(on_flip=record_flip)
            Window.remove_widget(view._live_image)

    @unittest.skipUnless(os.environ.get('PHOTOBOOTH_PALM_TEST_ASSETS'), 'Native model assets are opt-in')
    def test_real_palm_model_starts_v2_countdown_without_blocking_manual_capture(self):
        import time
        import cv2
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import Mock, patch
        from kivy.base import EventLoop
        from photobooth.kiosk_v2.photos import PhotoTest
        from photobooth.kiosk_v2.sensors import PalmShutter
        assets = Path(os.environ['PHOTOBOOTH_PALM_TEST_ASSETS'])
        hand = cv2.imread(str(assets / 'left_hands.jpg'))
        self.assertIsNotNone(hand)
        camera, face = Mock(), Mock()
        camera.read.side_effect = lambda: hand.copy()
        face.update.return_value = False
        palm = PalmShutter(model_path=assets/'gesture_recognizer.task')
        with TemporaryDirectory() as root, patch('photobooth.kiosk_v2.photos.configured_test',return_value=PhotoTest(root)):
            app = PortraitKioskV2App(camera_device=camera,face_inviter=face,palm_shutter=palm)
            app.build()
            def settle():
                end=time.monotonic()+3
                while app._photo_jobs.busy and time.monotonic()<end:
                    app._poll_photos();EventLoop.idle()
                self.assertFalse(app._photo_jobs.busy)
            try:
                app._choose_photo();app._complete_tutorial();app._change_copies(1)
                app._enter_photo_test();settle();app._admit_photo_test();settle()
                self.assertFalse(app._capture_button.disabled)
                end=time.monotonic()+15
                while app._countdown_event is None and time.monotonic()<end:
                    app._devices_tick(.033);EventLoop.idle()
                self.assertIsNotNone(app._countdown_event, palm.state)
                self.assertEqual(app._photo_view['captured'],0)
                timer=app._countdown_event
                end=time.monotonic()+.3
                while time.monotonic()<end:
                    app._devices_tick(.033);EventLoop.idle()
                self.assertIs(app._countdown_event,timer)
                app.on_pause()
                self.assertIsNone(app._countdown_event)
            finally:app.on_stop()

    def test_optional_palm_shares_countdown_and_requires_release_before_the_next_photo(self):
        import time
        import numpy as np
        from tempfile import TemporaryDirectory
        from types import SimpleNamespace
        from unittest.mock import Mock, patch
        from photobooth.kiosk_v2.photos import PhotoTest
        from photobooth.kiosk_v2.sensors import PalmShutter, DetectorParts
        from photobooth.palm_gesture import PalmHoldTrigger
        camera, face, worker = Mock(), Mock(), Mock()
        camera.read.return_value = np.zeros((40, 60, 3), dtype=np.uint8)
        face.update.return_value = False
        worker.state = 'ready'; worker.poll.return_value = None
        now = [10.0]
        palm = PalmShutter(parts=DetectorParts(worker, PalmHoldTrigger(), .6, .5), clock=lambda:now[0])
        with TemporaryDirectory() as root, patch('photobooth.kiosk_v2.photos.configured_test',return_value=PhotoTest(root)):
            app = PortraitKioskV2App(camera_device=camera,face_inviter=face,palm_shutter=palm)
            app.build()
            def settle():
                end=time.monotonic()+2
                while app._photo_jobs.busy and time.monotonic()<end:
                    app._poll_photos();time.sleep(.005)
                self.assertFalse(app._photo_jobs.busy)
            def observe(stamp, score=1, revision=None):
                now[0]=stamp
                worker.poll.return_value=SimpleNamespace(context=app._view_revision if revision is None else revision,
                                                         captured_at=stamp,score=score)
                app._devices_tick(.033)
            try:
                app._choose_photo();app._complete_tutorial();app._change_copies(1)
                app._enter_photo_test();settle();app._admit_photo_test();settle()
                for stamp in (10,10.2,10.4,10.6,10.8):observe(stamp)
                self.assertIsNone(app._countdown_event)
                observe(11.01)
                timer=app._countdown_event
                self.assertIsNotNone(timer)
                observe(11.2);self.assertIs(app._countdown_event,timer)
                app._countdown_deadline=time.monotonic()-.01
                app._countdown_tick(0);settle()
                self.assertEqual(app._photo_view['captured'],1)
                for stamp in (11.4,11.6,11.8,12,12.2,12.41):observe(stamp)
                self.assertIsNone(app._countdown_event)
                self.assertIn('Turunkan telapak',app._palm_hint.text)
                for stamp in (12.6,12.8,13.01):observe(stamp,0)
                for stamp in (13.2,13.4,13.6,13.8,14,14.21):observe(stamp)
                self.assertIsNotNone(app._countdown_event)
                old_revision=app._view_revision
                app.on_pause();app.on_resume()
                self.assertIsNone(app._countdown_event)
                observe(14.4,revision=old_revision)
                self.assertIsNone(app._countdown_event)
                self.assertEqual(app._photo_view['captured'],1)
            finally:app.on_stop()

    def test_photo_io_keeps_the_live_view_and_retires_pending_button_releases(self):
        import threading
        import time
        import numpy as np
        from tempfile import TemporaryDirectory
        from unittest.mock import Mock, patch
        from photobooth.kiosk_v2.photos import PhotoTest
        frame = np.zeros((40, 60, 3), dtype=np.uint8)
        camera, face = Mock(), Mock()
        camera.read.return_value = frame
        face.update.return_value = False
        with TemporaryDirectory() as root, patch('photobooth.kiosk_v2.photos.configured_test', return_value=PhotoTest(root)):
            app = PortraitKioskV2App(camera_device=camera, face_inviter=face)
            app.build()
            def settle():
                end = time.monotonic() + 2
                while app._photo_jobs.busy and time.monotonic() < end:
                    app._poll_photos();time.sleep(.005)
                self.assertFalse(app._photo_jobs.busy)
            entered, release = threading.Event(), threading.Event()
            try:
                app._choose_photo();app._complete_tutorial();app._change_copies(1)
                app._enter_photo_test();settle();app._admit_photo_test();settle()
                page, live, old = app.stage.current_screen, app._live_image, app._capture_button
                original = app._photo_jobs.service.capture
                def slow(frame):
                    entered.set();release.wait(2);return original(frame)
                with patch.object(app._photo_jobs.service, 'capture', side_effect=slow):
                    app._photo_submit('capture', frame)
                    self.assertTrue(entered.wait(1))
                    self.assertIs(app.stage.current_screen, page)
                    self.assertIs(app._live_image, live)
                    self.assertTrue(old.disabled)
                    old.dispatch('on_release');self.assertIsNone(app._countdown_event)
                    release.set();settle()
                old.dispatch('on_release')
                self.assertIsNone(app._countdown_event)
                self.assertEqual(app._photo_view['captured'], 1)
            finally:
                release.set();app.on_stop()

    def test_p3_photo_pages_save_three_retake_once_and_only_shutter_after_success(self):
        import time
        import numpy as np
        from tempfile import TemporaryDirectory
        from unittest.mock import Mock, patch
        from photobooth.kiosk_v2.photos import PhotoTest
        from photobooth.kiosk_v2.flow import CAPTURE, REVIEW, RESULT
        from kivy.core.window import Window
        from kivy.base import EventLoop
        device, inviter = Mock(), Mock()
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        frame[:, :80] = (0, 0, 255)
        device.read.return_value = frame
        inviter.update.return_value = False
        with TemporaryDirectory() as root:
            service = PhotoTest(root)
            with patch('photobooth.kiosk_v2.photos.configured_test', return_value=service):
                app = PortraitKioskV2App(camera_device=device, face_inviter=inviter)
                Window.add_widget(app.build())
                def settle():
                    deadline = time.monotonic() + 3
                    while app._photo_jobs.busy and time.monotonic() < deadline:
                        app._poll_photos()
                        time.sleep(.005)
                    self.assertFalse(app._photo_jobs.busy)
                def shoot():
                    app._start_countdown()
                    app._countdown_deadline = time.monotonic() - .01
                    app._countdown_tick(0)
                    settle()
                try:
                    app._choose_photo(); app._complete_tutorial(); app._change_copies(2)
                    app._enter_photo_test(); settle()
                    original_size = Window.size
                    try:
                        for size in ((452, 900), (360, 640), (800, 1280)):
                            Window.size = size
                            for _ in range(5):
                                EventLoop.idle()
                            card = app._photo_confirm_card
                            for child in card.children:
                                self.assertGreaterEqual(child.y, card.y)
                                self.assertLessEqual(child.top, card.top)
                    finally:
                        Window.size = original_size
                    app._admit_photo_test(); settle()
                    self.assertEqual(app.navigation.page, CAPTURE)
                    deadline = time.monotonic() + 2
                    while app._live_image.texture is None and time.monotonic() < deadline:
                        app._devices_tick(.033)
                        EventLoop.idle()
                    self.assertIsNotNone(app._live_image.texture)
                    for _ in range(5):
                        EventLoop.idle()
                    host = app._live_image.parent
                    self.assertEqual(app._live_image.pos, host.pos)
                    self.assertEqual(app._live_image.size, host.size)
                    with patch.object(app.audio_v2, 'cue') as cue:
                        with patch.object(service.store, 'save_raw_photo', side_effect=OSError('disk full')):
                            shoot()
                        self.assertNotIn(('shutter',), [call.args for call in cue.call_args_list])
                        self.assertEqual(service.session.initial_photo_paths, [])
                        for _ in range(3):
                            shoot()
                        self.assertEqual(sum(call.args == ('shutter',) for call in cue.call_args_list), 3)
                    self.assertEqual(app.navigation.page, REVIEW)
                    app._photo_submit('retake', 1); settle(); shoot()
                    self.assertTrue(app._photo_view['retake_used'])
                    self.assertTrue(all(w.disabled for w in app.stage.walk()
                                        if isinstance(w, ArcadeButton) and w.text == 'RETAKE'))
                    app._photo_submit('compose'); settle()
                    self.assertEqual(app.navigation.page, RESULT)
                    self.assertIn('MODE LOKAL', app._delivery_label.text)
                    self.assertIn('tanpa QR', app._delivery_label.text)
                    self.assertEqual(app._photo_view['copies'], 2)
                    app._photo_submit('next'); settle()
                    self.assertEqual(app.navigation.page, ADVERT)
                    self.assertFalse(any(app.quantities.values()))
                    # Keep one service alive so queued delivery continues while idle.
                    self.assertFalse(service._closed.is_set())
                    app._choose_photo(); app._complete_tutorial(); app._change_copies(1)
                    app._enter_photo_test(); settle()
                    app._admit_photo_test(); settle()
                    self.assertEqual(app._photo_view['captured'], 0)
                    self.assertFalse(app._photo_view['retake_used'])
                finally:
                    app.on_stop()
                    Window.remove_widget(app.stage)

    def test_p3_missing_camera_minimize_and_retired_controls_cannot_capture(self):
        import time
        import numpy as np
        from tempfile import TemporaryDirectory
        from unittest.mock import Mock, patch
        from photobooth.kiosk_v2.photos import PhotoTest
        from photobooth.kiosk_v2.flow import CAPTURE, PHOTO_CONFIRM, NavigationError
        device, inviter = Mock(), Mock()
        device.read.return_value = np.zeros((40, 60, 3), dtype=np.uint8)
        inviter.update.return_value = False
        with TemporaryDirectory() as root, patch('photobooth.kiosk_v2.photos.configured_test',
                                                 return_value=PhotoTest(root)):
            app = PortraitKioskV2App(camera_device=device, face_inviter=inviter)
            app.build()
            def settle():
                deadline = time.monotonic() + 3
                while app._photo_jobs.busy and time.monotonic() < deadline:
                    app._poll_photos(); time.sleep(.005)
                self.assertFalse(app._photo_jobs.busy)
            try:
                app._choose_photo(); app._complete_tutorial(); app._change_copies(1)
                app._enter_photo_test(); settle()
                device.read.return_value = None
                app._admit_photo_test()
                self.assertEqual(app.navigation.page, PHOTO_CONFIRM)
                device.read.return_value = np.zeros((40, 60, 3), dtype=np.uint8)
                app._admit_photo_test(); settle()
                self.assertEqual(app.navigation.page, CAPTURE)
                with self.assertRaises(NavigationError):
                    app.navigation.to_advertising()
                old_button = app._capture_button
                app._start_countdown()
                self.assertIsNotNone(app._countdown_event)
                app.on_pause()
                self.assertIsNone(app._countdown_event)
                app.on_resume()
                old_button.dispatch('on_release')
                self.assertIsNone(app._countdown_event)
                self.assertEqual(app._photo_view['captured'], 0)
                app._start_countdown()
                device.read.return_value = None
                app._countdown_tick(0)
                self.assertIsNone(app._countdown_event)
                self.assertEqual(app._photo_view['captured'], 0)
                app._photo_submit('abort'); settle()
                self.assertEqual(app.navigation.page, ADVERT)
            finally:
                app.on_stop()

    def test_automatic_face_invitation_keeps_ad_player_and_retired_overlay_is_inert(self):
        from unittest.mock import Mock, patch
        device, inviter = Mock(), Mock()
        device.read.return_value = object()
        inviter.update.side_effect = lambda frame, revision, allowed: allowed
        app = PortraitKioskV2App(camera_device=device, face_inviter=inviter)
        app.build()
        try:
            player = app._ad_player
            app._devices_tick(0)
            panel = app._invitation
            self.assertIsNotNone(panel)
            self.assertIs(app._ad_player, player)
            app._devices_tick(0)
            self.assertIs(app._invitation, panel)
            retired = next(w for w in panel.walk() if isinstance(w,ArcadeButton) and w.text=='AYO FOTO')
            app._close_invitation()
            with patch.object(app.audio_v2,'cue') as cue:
                retired.dispatch('on_release')
                cue.assert_not_called()
            self.assertEqual(app.navigation.page, ADVERT)
            app._devices_tick(0)
            accept = next(w for w in app._invitation.walk() if isinstance(w,ArcadeButton) and w.text=='AYO FOTO')
            accept.dispatch('on_release')
            self.assertEqual(app.navigation.entry_source,'face')
            self.assertEqual(app.navigation.page,TUTORIAL)
            app._devices_tick(0)
            self.assertIsNone(app._invitation)
            app.on_pause();device.set_active.assert_called_with(False)
            app.on_resume();device.set_active.assert_called_with(True)
        finally:
            app.on_stop()
            device.close.assert_called_once_with()

    def test_video_source_is_not_probed_as_an_image_and_explicit_poster_still_loads(self):
        from unittest.mock import Mock, patch
        from photobooth.ui_ads import GuardedVideo
        from photobooth.kiosk_v2.branding import CAMERA_ART
        with patch.object(GuardedVideo, 'set_texture_from_resource') as image_load:
            video = GuardedVideo(Mock(), source='advertising-clip.mp4', state='pause')
            try:
                video.texture_update()
                self.assertNotIn(video.source, [call.args[0] for call in image_load.call_args_list])
                video.preview = str(CAMERA_ART)
                video.texture_update()
                image_load.assert_called_once_with(str(CAMERA_ART))
            finally:
                video.retire()

    def test_gallery_focus_keeps_full_strips_and_floating_arrows_inside_preview(self):
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from photobooth.kiosk_v2.branding import PixelWordmark, MeongLogo
        original = Window.size
        app = PortraitKioskV2App()
        Window.add_widget(app.build())
        try:
            app._choose_photo()
            app._complete_tutorial()
            for size in ((800, 1280), (452, 900), (360, 640), (452, 600), (800, 600)):
                with self.subTest(viewport=size):
                    Window.size = size
                    for _ in range(6):
                        EventLoop.idle()
                    self.assertFalse(any(getattr(w, 'text', '') == 'CETAK' for w in app.stage.walk()))
                    for label in (app._order_total_label, app._order_summary):
                        self.assertIsNotNone(label.parent)
                        self.assertGreater(label.width, label.texture_size[0] - 1)
                        self.assertGreaterEqual(label.height, label.texture_size[1])
                    gallery = app._carousel
                    left, bottom = gallery.viewport.to_window(*gallery.viewport.pos)
                    right, top = gallery.viewport.to_window(gallery.viewport.right, gallery.viewport.top)
                    for image in (app._previous_preview, app._preview, app._next_preview):
                        x, y = image.to_window(*image.pos)
                        x1, y1 = image.to_window(image.right, image.top)
                        self.assertGreaterEqual(x, left - 1)
                        self.assertGreaterEqual(y, bottom - 1)
                        self.assertLessEqual(x1, right + 1)
                        self.assertLessEqual(y1, top + 1)
                        self.assertAlmostEqual((x1 - x) / (y1 - y), 1 / 3, places=4)
                    x, y = app._preview.to_window(*app._preview.pos)
                    x1, y1 = app._preview.to_window(app._preview.right, app._preview.top)
                    self.assertGreater(y1 - y, Window.height * .49)
                    for text in ('SEBELUMNYA', 'BERIKUTNYA'):
                        button = next(w for w in app.stage.walk()
                                      if isinstance(w, ArcadeButton) and w.text == text)
                        bx, by = button.to_window(*button.pos)
                        br, bt = button.to_window(button.right, button.top)
                        self.assertGreaterEqual(bx, left - 1)
                        self.assertLessEqual(br, right + 1)
                        self.assertGreaterEqual(by, bottom - 1)
                        self.assertLess(bt, bottom + (top - bottom) * .25)
                        self.assertTrue(br <= x or bx >= x1, 'arrow obscures selected strip')
                    brand = next(w for w in app.stage.walk() if isinstance(w, MeongLogo))
                    self.assertIsInstance(brand.wordmark, PixelWordmark)
                    self.assertIsInstance(brand.caption, PixelWordmark)
                    self.assertEqual((brand.wordmark.text, brand.caption.text), ('MEONG', 'PHOTOBOOTH'))
        finally:
            app.on_stop()
            Window.remove_widget(app.stage)
            Window.size = original

    def test_carousel_has_real_motion_and_rapid_input_replaces_without_late_page_actions(self):
        import time
        from kivy.base import EventLoop
        from kivy.core.window import Window
        app = PortraitKioskV2App()
        Window.add_widget(app.build())
        try:
            app._choose_photo()
            app._complete_tutorial()
            for _ in range(5):
                EventLoop.idle()
            gallery = app._carousel
            origin = app._preview.x
            observed = []
            gallery.bind(offset=lambda widget, offset: observed.append((offset, app._preview.x)))
            app._shift_template(1)
            deadline = time.monotonic() + 1
            while gallery._moving and time.monotonic() < deadline:
                EventLoop.idle()
            self.assertTrue(any(offset < 0 and x < origin for offset, x in observed))
            self.assertFalse(gallery._moving)
            for step in (1, -1, 1, 1, -1):
                app._shift_template(step)
            self.assertEqual(app.template_index, 2)
            deadline = time.monotonic() + 1
            while gallery._moving and time.monotonic() < deadline:
                EventLoop.idle()
            self.assertFalse(gallery._moving)
            self.assertEqual(gallery.offset, 0)
            self.assertIs(app._preview.texture, app._textures[app.templates[2].template_id])
            app._shift_template(1)
            app.on_pause()
            self.assertFalse(gallery._moving)
            self.assertEqual(gallery.offset, 0)
            app.on_resume()
            app._shift_template(-1)
            app._return_ad()
            self.assertTrue(gallery._disposed)
            self.assertFalse(gallery._moving)
            self.assertFalse(gallery._touch_origins)
            for _ in range(5):
                EventLoop.idle()
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertEqual(app.template_index, 0)
        finally:
            app.on_stop()
            Window.remove_widget(app.stage)

    def test_finger_drags_strip_before_selection_and_secondary_touch_cannot_commit_twice(self):
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent

        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ['pos']
                super().depack(args)

        app = PortraitKioskV2App()
        Window.add_widget(app.build())
        try:
            app._choose_photo()
            app._complete_tutorial()
            for _ in range(5):
                EventLoop.idle()
            gallery = app._carousel
            x, y = gallery.to_window(*gallery.center)
            first = Pointer('drag-test', 'primary', (x / Window.width, y / Window.height), is_touch=True)
            second = Pointer('drag-test', 'secondary', (x / Window.width, y / Window.height), is_touch=True)
            origin = app._preview.x
            EventLoop.post_dispatch_input('begin', first)
            EventLoop.post_dispatch_input('begin', second)
            self.assertEqual(len(gallery._touch_origins), 1)
            first.move(((x - 90) / Window.width, y / Window.height))
            EventLoop.post_dispatch_input('update', first)
            self.assertEqual(app.template_index, 0)
            self.assertLess(app._preview.x, origin)
            self.assertLess(gallery.offset, 0)
            EventLoop.post_dispatch_input('end', first)
            self.assertEqual(app.template_index, 1)
            EventLoop.post_dispatch_input('end', second)
            self.assertEqual(app.template_index, 1)
            self.assertFalse(gallery._touch_origins)
        finally:
            app.on_stop()
            Window.remove_widget(app.stage)

    def test_button_feedback_precedes_expensive_callback_and_copy_does_not_render_previews(self):
        from unittest.mock import patch
        app = PortraitKioskV2App()
        app.build()
        try:
            events = []
            with patch.object(app.audio_v2, 'cue', side_effect=lambda *_: events.append('click')):
                action = app._action('test', lambda: events.append('route'))
                action.dispatch('on_release')
            self.assertEqual(events, ['click', 'route'])
            app._choose_photo()
            app._complete_tutorial()
            with patch.object(app, '_update_template') as render:
                app._change_copies(1)
                render.assert_not_called()
            self.assertEqual(app.quantities[app.templates[0].template_id], 1)
        finally:
            app.on_stop()
        app._prepare_idle_assets(0)  # Queued idle callback after close is inert.
        self.assertFalse(app._preview_preloader._futures)

    @unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_AUDIO') == '1',
                         'native audio route requires PHOTOBOOTH_TEST_AUDIO=1')
    def test_start_photo_with_enabled_native_audio_keeps_gui_on_tutorial_and_gallery(self):
        from unittest.mock import patch
        from kivy.core.audio.audio_sdl2 import SoundSDL2

        with patch.dict(os.environ, {'PHOTOBOOTH_AUDIO': '1', 'PHOTOBOOTH_AD_VIDEO': '0',
                                    'KIVY_AUDIO': ''}), \
                patch('kivy.core.audio.SoundLoader.load') as ff:
            app = PortraitKioskV2App()
            app.build()
            try:
                for _ in range(5):
                    start = next(w for w in app.stage.walk()
                                 if isinstance(w, ArcadeButton) and w.text == 'MULAI FOTO')
                    start.dispatch('on_release')
                    self.assertFalse(app._closed)
                    self.assertEqual(app.navigation.page, TUTORIAL)
                    self.assertIsInstance(app.audio_v2._handles['music'], SoundSDL2)
                    self.assertIsInstance(app.audio_v2._handles['button'], SoundSDL2)
                    self.assertEqual(app.audio_v2.status()['music_state'], 'play')
                    done = next(w for w in app.stage.walk() if isinstance(w, ArcadeButton)
                                and w.text == 'LANJUT PILIH TEMPLATE')
                    done.dispatch('on_release')
                    self.assertEqual(app.navigation.page, TEMPLATES)
                    self.assertEqual(app.audio_v2.status()['music_state'], 'play')
                    app._return_ad()
                ff.assert_not_called()
            finally:
                app.on_stop()

    def test_live_resize_preserves_gallery_cart_audio_owner_and_real_touch_coordinates(self):
        from unittest.mock import patch
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent
        from photobooth.kiosk_v2.viewport import PortraitViewport

        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ['pos']
                super().depack(args)

        def settle():
            for _ in range(5):
                EventLoop.idle()

        def gesture(start, end):
            touch = Pointer('resize-test', 'pointer',
                            (start[0] / Window.width, start[1] / Window.height), is_touch=True)
            EventLoop.post_dispatch_input('begin', touch)
            touch.move((end[0] / Window.width, end[1] / Window.height))
            EventLoop.post_dispatch_input('update', touch)
            EventLoop.post_dispatch_input('end', touch)
            settle()

        original = Window.size
        app = PortraitKioskV2App()
        Window.add_widget(app.build())
        try:
            app._choose_photo()
            app._complete_tutorial()
            app._change_copies(2)
            gallery = next(w for w in app.stage.walk() if isinstance(w, SwipeGallery))
            screen = app.stage.current_screen
            revision = app._view_revision
            with patch.object(app.audio_v2, 'enter_page', wraps=app.audio_v2.enter_page) as enter:
                for dimensions in ((800, 1280), (452, 900), (360, 640),
                                   (452, 600), (800, 600), (800, 1280)):
                    with self.subTest(viewport=dimensions):
                        Window.size = dimensions
                        settle()
                        self.assertIs(app.stage.current_screen, screen)
                        self.assertEqual(app._view_revision, revision)
                        self.assertEqual(app.quantities[app.templates[0].template_id], 2)
                        self.assertIs(next(w for w in app.stage.walk()
                                           if isinstance(w, SwipeGallery)), gallery)
                        viewport = next(w for w in app.stage.walk()
                                        if isinstance(w, PortraitViewport))
                        bottom = app._preview.to_window(app._preview.x, app._preview.y)[1]
                        top = app._preview.to_window(app._preview.right, app._preview.top)[1]
                        self.assertGreater(top - bottom, 100, 'strip preview collapsed')
                        self.assertGreater(bottom, 0)
                        self.assertLess(top, Window.height)
                        for button in (w for w in app.stage.walk() if isinstance(w, ArcadeButton)):
                            x, y = button.to_window(button.x, button.y)
                            right, top = button.to_window(button.right, button.top)
                            self.assertGreaterEqual(x, -.1)
                            self.assertGreaterEqual(y, -.1)
                            self.assertLessEqual(right, Window.width + .1)
                            self.assertLessEqual(top, Window.height + .1)
                            self.assertGreaterEqual(top - y, 48 * viewport.viewport_scale - .1)
                        # Actual grabbed input must still use inverse scaled coordinates.
                        x, y = gallery.to_window(gallery.x, gallery.center_y)
                        right, _ = gallery.to_window(gallery.right, gallery.center_y)
                        before = app.template_index
                        gesture((x + (right - x) * .75, y), (x + (right - x) * .25, y))
                        self.assertEqual(app.template_index, (before + 1) % 12)
                        gesture((x + (right - x) * .25, y), (x + (right - x) * .75, y))
                        self.assertEqual(app.template_index, before)
                        gesture((x + (right - x) * .5, y), (x + (right - x) * .5, y + 40))
                        self.assertEqual(app.template_index, before)
                        gesture((x + (right - x) * .5, y), (x + (right - x) * .52, y))
                        self.assertEqual(app.template_index, before)
                        for preview in (app._previous_preview, app._preview, app._next_preview):
                            # This check targets stable left/centre/right hit
                            # regions. Motion interruption is verified separately.
                            import time
                            deadline = time.monotonic() + .6
                            while app._carousel._moving and time.monotonic() < deadline:
                                EventLoop.idle()
                            self.assertFalse(app._carousel._moving)
                            start = preview.to_window(*preview.center)
                            delta = (right - x) * (.3 if start[0] <= (right + x) / 2 else -.3)
                            before = app.template_index
                            gesture(start, (start[0] + delta, start[1]))
                            self.assertEqual(app.template_index, (before + (-1 if delta > 0 else 1)) % 12)
                        # Restore selection using the arrow model, preserving the cart.
                        app._shift_template(-app.template_index)
                        plus = next(w for w in app.stage.walk()
                                    if isinstance(w, ArcadeButton) and w.text == '+')
                        point = plus.to_window(*plus.center)
                        gesture(point, point)
                        self.assertEqual(app.quantities[app.templates[0].template_id], 3)
                        app._change_copies(-1)
                enter.assert_not_called()  # Resizing must never restart page audio.
            # A drag interrupted by resize must release its grab without navigation.
            start = gallery.to_window(*gallery.center)
            touch = Pointer('resize-test', 'interrupted',
                            (start[0] / Window.width, start[1] / Window.height), is_touch=True)
            EventLoop.post_dispatch_input('begin', touch)
            Window.size = (452, 600)
            settle()
            end = gallery.to_window(*gallery.center)
            touch.move((end[0] / Window.width, end[1] / Window.height))
            EventLoop.post_dispatch_input('end', touch)
            self.assertEqual(app.template_index, 0)
            self.assertFalse(gallery._touch_origins)
            self.assertNotIn(gallery, [ref() for ref in touch.grab_list])
            plus = next(w for w in app.stage.walk() if isinstance(w, ArcadeButton) and w.text == '+')
            point = plus.to_window(*plus.center)
            gesture(point, point)
            self.assertEqual(app.quantities[app.templates[0].template_id], 3)
        finally:
            app.on_stop()
            Window.remove_widget(app.stage)
            Window.size = original

    def test_advert_game_invitation_tutorial_and_real_12_strip_gallery(self):
        from photobooth.workflow import quote_order

        app = PortraitKioskV2App()
        app.build()
        try:
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertEqual(app.stage.current, ADVERT)
            self.assertIsNotNone(app._ad_player)
            # Invitation is a nonmodal overlay on the advertising media host.
            app._show_invitation()
            self.assertIs(app._invitation.parent, app._advert_host)
            self.assertEqual(app.navigation.page, ADVERT)
            app._choose_game("face_preview")
            self.assertEqual(app.navigation.page, GAME_PREVIEW)
            self.assertIsNone(app._ad_player)
            # Safe skip-to-photo: no receipt claim or discount in this prototype.
            app._choose_photo("skip_game")
            self.assertEqual(app.navigation.page, TUTORIAL)
            app._complete_tutorial()
            self.assertEqual(app.navigation.page, TEMPLATES)
            self.assertTrue(app.navigation.tutorial_seen)
            self.assertEqual(len(app.templates), 12)
            self.assertEqual(len(app._textures), 3)  # selected + adjacent master strips
            self.assertIsNotNone(app._preview.texture)
            self.assertEqual(app.quantities[app.templates[0].template_id], 0)
            app._change_copies(1)
            self.assertEqual(app.quantities[app.templates[0].template_id], 1)
            self.assertEqual(quote_order(app.templates, app.quantities).total_amount, 10000)
            app._shift_template(1)
            self.assertEqual(app.template_index, 1)
            self.assertEqual(len(app._textures), 4)  # only next new strip loaded
            app._return_ad()
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertFalse(app.navigation.tutorial_seen)
            self.assertEqual(sum(app.quantities.values()), 0)
        finally:
            app.on_stop()


    def test_illustrated_tutorial_and_game_intro_are_real_pages_not_payment(self):
        app = PortraitKioskV2App()
        app.build()
        try:
            def widgets(root):
                yield root
                for child in root.children:
                    yield from widgets(child)

            app._choose_photo("help")
            self.assertEqual(app.navigation.page, TUTORIAL)
            figures = [w for w in widgets(app.stage)
                       if isinstance(w, TutorialIcon)]
            self.assertEqual({w.kind for w in figures},
                             {"template", "payment", "camera", "print"})
            app._return_ad()
            app._choose_game("manual")
            self.assertEqual(app.navigation.page, GAME_PREVIEW)
            buttons = [w for w in widgets(app.stage)
                       if isinstance(w, ArcadeButton)]
            from photobooth.meong_fly_gui import MeongFlyStage
            self.assertIsInstance(app._game_field,MeongFlyStage)
            self.assertEqual(app._game_field.flow.screen,'start')
            self.assertIsNone(app._game_field._scanner)
            self.assertFalse(hasattr(app.navigation, "discount_amount"))
            self.assertFalse(hasattr(app.navigation, "paid"))
            app._choose_photo("skip_game")
            self.assertEqual(app.navigation.page, TUTORIAL)
        finally:
            app.on_stop()

    def test_shared_advert_entry_has_help_and_game_without_second_home(self):
        app = PortraitKioskV2App()
        app.build()
        try:
            def buttons(root):
                all_buttons = []
                if isinstance(root, ArcadeButton):
                    all_buttons.append(root)
                for child in root.children:
                    all_buttons.extend(buttons(child))
                return all_buttons

            labels = {w.text for w in buttons(app.stage)}
            self.assertIn("MULAI FOTO", labels)
            self.assertIn("MAIN MEONG FLY", labels)
            self.assertIn("CARA PAKAI", labels)
            app._show_invitation()
            self.assertEqual(app.stage.current, ADVERT)
            labels = {w.text for w in buttons(app._invitation)}
            self.assertEqual({"AYO FOTO", "MAIN MEONG FLY",
                              "NANTI SAJA"}, labels)
            app._return_ad()
            self.assertEqual(app.stage.current, ADVERT)
        finally:
            app.on_stop()


    def test_unavailable_actions_keep_readable_text_without_becoming_touchable(self):
        from photobooth.kiosk_v2.theme import MUTED, rgba
        button = ArcadeButton("PEMBAYARAN (BELUM TERHUBUNG)")
        button.disabled = True
        self.assertEqual(tuple(button.disabled_color), rgba(MUTED))
        self.assertTrue(button.disabled)

    def test_retired_buttons_and_swipes_cannot_change_next_visit(self):
        app = PortraitKioskV2App()
        app.build()
        try:
            app._choose_photo()
            old_done = next(w for w in app.stage.walk()
                            if isinstance(w, ArcadeButton) and w.text == "LANJUT PILIH TEMPLATE")
            app._complete_tutorial()
            old_gallery = next(w for w in app.stage.walk() if isinstance(w, SwipeGallery))
            app._return_ad()
            app._choose_photo()
            old_done.dispatch("on_release")
            self.assertEqual(app.navigation.page, TUTORIAL)
            self.assertFalse(app.navigation.tutorial_seen)
            app._complete_tutorial()
            old_gallery._on_swipe(1)
            self.assertEqual(app.template_index, 0)
        finally:
            app.on_stop()

    def test_pause_blocks_touch_and_timeout_resume_starts_fresh_idle_period(self):
        import time
        app = PortraitKioskV2App()
        app.build()
        try:
            app._choose_photo()
            done = next(w for w in app.stage.walk()
                        if isinstance(w, ArcadeButton) and w.text == "LANJUT PILIH TEMPLATE")
            app.on_pause()
            done.dispatch("on_release")
            app._last_activity = time.monotonic() - app.catalog.timing.landing_idle - 1
            app._tick(0)
            self.assertEqual(app.navigation.page, TUTORIAL)
            app.on_resume()
            app._tick(0)
            self.assertEqual(app.navigation.page, TUTORIAL)
            done.dispatch("on_release")
            self.assertEqual(app.navigation.page, TEMPLATES)
            app._change_copies(1)
            app._last_activity = time.monotonic() - app.catalog.timing.landing_idle - 1
            app._tick(0)
            self.assertEqual(app.navigation.page, ADVERT)
            self.assertEqual(sum(app.quantities.values()), 0)
            self.assertFalse(app.navigation.tutorial_seen)
        finally:
            app.on_stop()

    def test_touch_targets_and_tutorial_scroll_at_portrait_and_short_sizes(self):
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent
        from kivy.uix.scrollview import ScrollView

        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ['pos']
                super().depack(args)

        def settle():
            for _ in range(4):
                EventLoop.idle()

        original = Window.size
        try:
            for width, height in ((800, 1280), (452, 900), (360, 640), (452, 600), (800, 600)):
                with self.subTest(viewport=(width, height)):
                    Window.size = (width, height)
                    app = PortraitKioskV2App()
                    Window.add_widget(app.build())
                    try:
                        settle()
                        start = next(w for w in app.stage.walk()
                                     if isinstance(w, ArcadeButton) and w.text == "MULAI FOTO")
                        x, y = start.to_window(*start.center)
                        event = Pointer('portrait-test', f'{width}',
                                        (x / Window.width, y / Window.height), is_touch=True)
                        EventLoop.post_dispatch_input('begin', event)
                        EventLoop.post_dispatch_input('end', event)
                        settle()
                        self.assertEqual(app.navigation.page, TUTORIAL)
                        guide = next(w for w in app.stage.walk() if isinstance(w, ScrollView))
                        guide.scroll_y = 0
                        settle()
                        final_icon = next(w for w in app.stage.walk()
                                          if isinstance(w, TutorialIcon) and w.kind == 'print')
                        _, icon_y = final_icon.to_window(*final_icon.center)
                        _, guide_y = guide.to_window(guide.x, guide.y)
                        _, guide_top = guide.to_window(guide.right, guide.top)
                        self.assertGreater(icon_y, guide_y)
                        self.assertLess(icon_y, guide_top)
                        for route in (lambda: None, app._complete_tutorial,
                                      app._return_ad, app._choose_game):
                            route()
                            settle()
                            from photobooth.kiosk_v2.branding import MeongLogo
                            brands = [w for w in app.stage.walk() if isinstance(w, MeongLogo)]
                            if app.navigation.page == GAME_PREVIEW:
                                from photobooth.meong_fly_gui import MeongFlyStage
                                self.assertIsInstance(app._game_field,MeongFlyStage)
                                self.assertEqual(app._game_field._screen_seen,'start')
                                self.assertIsNotNone(app._game_field._camera_layers['hero'][1])
                            else:
                                self.assertEqual(len(brands), 1)
                                brand = brands[0]
                                for part in (brand.art, brand.wordmark, brand.caption):
                                    self.assertGreaterEqual(part.x, brand.x - 1)
                                    self.assertGreaterEqual(part.y, brand.y - 1)
                                    self.assertLessEqual(part.right, brand.right + 1)
                                    self.assertLessEqual(part.top, brand.top + 1)
                            for button in (w for w in app.stage.walk() if isinstance(w, ArcadeButton)):
                                x, y = button.to_window(button.x, button.y)
                                right, top = button.to_window(button.right, button.top)
                                self.assertGreaterEqual(button.height, 48)
                                self.assertGreaterEqual(x, 0)
                                self.assertGreaterEqual(y, 0)
                                self.assertLessEqual(right, width + 1)
                                self.assertLessEqual(top, height + 1)
                    finally:
                        app.on_stop()
                        Window.remove_widget(app.stage)
        finally:
            Window.size = original

    def test_every_enabled_button_clicks_once_even_on_ads_and_game_preview(self):
        from unittest.mock import patch
        app = PortraitKioskV2App()
        app.build()
        try:
            def button(text):
                return next(w for w in app.stage.walk()
                            if isinstance(w, ArcadeButton) and w.text == text)

            with patch.object(app.audio_v2, 'cue', return_value=True) as cue:
                labels = ('UNDANGAN (DEMO)', 'NANTI SAJA', 'MAIN MEONG FLY',
                          'LANJUT FOTO TANPA GAME', 'LANJUT PILIH TEMPLATE',
                          '+', 'BERIKUTNYA', 'SELESAI / KEMBALI IKLAN')
                for count, label in enumerate(labels, 1):
                    if label == 'LANJUT FOTO TANPA GAME':
                        app._game_field._handle_action('photo')
                    else:
                        old = button(label)
                        old.dispatch('on_release')
                    self.assertEqual(cue.call_count, count, label)
                # The old return button must not affect a new visitor or click.
                old.dispatch('on_release')
                self.assertEqual(cue.call_count, len(labels))
                app._choose_photo()
                app._complete_tutorial()
                button('PEMBAYARAN (BELUM TERHUBUNG)').dispatch('on_release')
                self.assertEqual(cue.call_count, len(labels))
        finally:
            app.on_stop()

    def test_real_gallery_swipe_grabs_stream_and_moves_once_at_both_sizes(self):
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from kivy.input.motionevent import MotionEvent

        class Pointer(MotionEvent):
            def depack(self, args):
                self.sx, self.sy = args
                self.profile = ['pos']
                super().depack(args)

        def settle():
            for _ in range(4):
                EventLoop.idle()

        original = Window.size
        try:
            for width, height in ((800, 1280), (452, 900)):
                with self.subTest(viewport=(width, height)):
                    Window.size = (width, height)
                    app = PortraitKioskV2App()
                    Window.add_widget(app.build())
                    try:
                        app._choose_photo()
                        app._complete_tutorial()
                        settle()
                        gallery = next(w for w in app.stage.walk() if isinstance(w, SwipeGallery))
                        x, y = gallery.to_window(*gallery.center)
                        def drag(dx, dy, identity):
                            touch = Pointer('portrait-swipe', identity,
                                            (x / Window.width, y / Window.height), is_touch=True)
                            EventLoop.post_dispatch_input('begin', touch)
                            self.assertIn(gallery, [ref() for ref in touch.grab_list])
                            touch.move(((x + dx) / Window.width, (y + dy) / Window.height))
                            EventLoop.post_dispatch_input('update', touch)
                            EventLoop.post_dispatch_input('end', touch)
                            settle()
                            self.assertNotIn(gallery, [ref() for ref in touch.grab_list])
                            self.assertFalse(gallery._touch_origins)
                        drag(-90, 0, 'left')
                        self.assertEqual(app.template_index, 1)
                        drag(90, 0, 'right')
                        self.assertEqual(app.template_index, 0)
                        drag(0, 65, 'vertical')
                        drag(-15, 0, 'short')
                        self.assertEqual(app.template_index, 0)
                        drag(-90, 0, 'left-again')
                        self.assertEqual(app.template_index, 1)
                        pending = Pointer('portrait-swipe', 'retired',
                                          (x / Window.width, y / Window.height), is_touch=True)
                        EventLoop.post_dispatch_input('begin', pending)
                        self.assertIn(gallery, [ref() for ref in pending.grab_list])
                        app._return_ad()
                        self.assertNotIn(gallery, [ref() for ref in pending.grab_list])
                        self.assertFalse(gallery._touch_origins)
                        EventLoop.post_dispatch_input('end', pending)
                        self.assertEqual(app.navigation.page, ADVERT)
                    finally:
                        app.on_stop()
                        Window.remove_widget(app.stage)
        finally:
            Window.size = original

    def test_minimize_restore_and_retired_gallery_release_ownership(self):
        from kivy.core.window import Window
        app = PortraitKioskV2App()
        app.build()
        try:
            Window.dispatch('on_minimize')
            self.assertTrue(app._suspended)
            Window.dispatch('on_restore')
            self.assertFalse(app._suspended)
        finally:
            app.on_stop()
        Window.dispatch('on_minimize')
        self.assertFalse(app._suspended)

    def test_ad_media_notification_precedes_video_load_and_recovers_to_image(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import Mock, patch
        from PIL import Image as PillowImage
        from photobooth.advertising import Advertisement
        from photobooth.ui_ads import AdvertisementPlayer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            PillowImage.new('RGB', (20, 20), 'red').save(root / 'image.png')
            (root / 'clip.mp4').write_bytes(b'synthetic-decoder-failure')
            items = [Advertisement('still', 'Still', root / 'image.png', ('idle',)),
                     Advertisement('video', 'Video', root / 'clip.mp4', ('idle',))]
            kinds = []
            catalog = SimpleNamespace(items=items, available=lambda _: items)
            player = AdvertisementPlayer(catalog, 'idle', Mock(), on_media_change=kinds.append)
            try:
                player.next()
                self.assertEqual(kinds, ['image'])
                def decoder(*args, **kwargs):
                    self.assertEqual(kinds[-1], 'video')
                    raise RuntimeError('simulated decoder failure')
                with patch.dict(os.environ, PHOTOBOOTH_AD_VIDEO='1'), patch('photobooth.ui_ads.GuardedVideo', decoder):
                    player.next()
                self.assertEqual(kinds, ['image', 'video'])
                player.next()
                self.assertEqual(kinds, ['image', 'video', 'image'])
                catalog.available = lambda _: []
                player.next()
                self.assertEqual(kinds[-1], 'fallback')
            finally:
                player.close()

    def test_shared_brand_uses_original_transparent_reference_art(self):
        import hashlib
        from PIL import Image as PillowImage
        from photobooth.kiosk_v2.branding import CAMERA_ART
        self.assertEqual(hashlib.sha256(CAMERA_ART.read_bytes()).hexdigest(),
                         'bd5513c0ba6b1d6eb355dd89ff4d5abbc7fe99341134f64b1381e8d515b0d227')
        with PillowImage.open(CAMERA_ART) as source:
            self.assertEqual(source.size, (224, 152))
            self.assertEqual(source.convert('RGBA').getchannel('A').getextrema(), (0, 255))

    def test_tutorial_keeps_four_numbered_steps_in_display_order(self):
        from kivy.uix.scrollview import ScrollView
        app = PortraitKioskV2App()
        app.build()
        try:
            app._choose_photo()
            guide = next(w for w in app.stage.walk() if isinstance(w, ScrollView))
            cards = list(reversed(guide.children[0].children))
            expected = [('template', '01  PILIH TEMPLATE'), ('payment', '02  BAYAR'),
                        ('camera', '03  AMBIL 3 FOTO'), ('print', '04  CETAK & SCAN QR')]
            self.assertEqual(len(cards), 4)
            for card, (kind, title) in zip(cards, expected):
                self.assertEqual(next(w.kind for w in card.walk() if isinstance(w, TutorialIcon)), kind)
                self.assertTrue(any(getattr(w, 'text', '') == title for w in card.walk()))
        finally:
            app.on_stop()

    def test_carousel_swipe_uses_horizontal_direction_and_rejects_vertical(self):
        self.assertEqual(SwipeGallery.swipe_step(-90, 5), 1)
        self.assertEqual(SwipeGallery.swipe_step(90, -4), -1)
        self.assertEqual(SwipeGallery.swipe_step(12, 0), 0)
        self.assertEqual(SwipeGallery.swipe_step(80, 160), 0)


if __name__ == "__main__":
    unittest.main()
