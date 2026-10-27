"""Opt-in native reuse smoke; desktop rendering is not Android acceptance."""
import importlib
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
import time
from contextlib import ExitStack
from unittest.mock import patch


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_ANDROID') == '1', 'Android preview native smoke is opt-in')
class AndroidWidgetTests(unittest.TestCase):
    def test_curated_project_runs_without_repository_assets(self):
        from tools.prepare_android import prepare
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)/'project'
            prepare(stage)
            code = '''
from pathlib import Path
import tempfile
from photobooth.kiosk_v2.android_preview import create_preview
with tempfile.TemporaryDirectory() as private:
    app = create_preview(private)
    from kivy.base import EventLoop
    from kivy.core.window import Window
    from photobooth.meong_fly_sprite import camera_frames
    import photobooth
    assert Path(photobooth.__file__).resolve().is_relative_to(Path.cwd())
    assert camera_frames()['hero'].front.size == (224, 152)
    Window.add_widget(app.build())
    try:
        for _ in range(4): EventLoop.idle()
        assert len(app.templates) == 12
        assert Path(app.events.path).is_relative_to(private)
        app._choose_photo()
        app._complete_tutorial()
        app._change_copies(1)
        assert app._test_photo_button.disabled
        assert len(app._carousel._textures) == 5
        app._return_ad()
        app._choose_game()
        for _ in range(4): EventLoop.idle()
        assert app._operator_key(None, 27)
        app.on_pause()
        app.on_resume()
        assert not app._suspended
    finally:
        app.on_stop()
        for name in ('_game_jobs', '_mock_jobs', '_health_reports'):
            getattr(app, name).wait_closed()
        Window.remove_widget(app.stage)
print('STAGED_ANDROID_PASS')
'''
            env = os.environ.copy()
            env.pop('PYTHONPATH', None)
            result = subprocess.run([sys.executable, '-c', code], cwd=stage, env=env,
                                    capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, (result.stdout+result.stderr)[-6000:])
            self.assertIn('STAGED_ANDROID_PASS', result.stdout)

    def test_original_ui_private_data_and_hardware_gates(self):
        from photobooth.kiosk_v2.android_preview import configure_preview, create_preview, DATA_MODULES
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}), ExitStack() as stack:
            configure_preview(directory)
            from kivy.config import Config
            width = int(os.environ.get('ANDROID_PREVIEW_WIDTH', '452'))
            height = 1280 if width == 800 else 900
            Config.set('graphics','width',str(width))
            Config.set('graphics','height',str(height))
            from kivy.base import EventLoop
            from kivy.core.window import Window
            previous_size = Window.size
            Window.size = (width, height)
            for name in DATA_MODULES:
                module = importlib.import_module('photobooth.kiosk_v2.'+name)
                stack.enter_context(patch.object(module,'PROJECT_ROOT',module.PROJECT_ROOT))
            app = create_preview(directory)
            Window.add_widget(app.build())
            def settle(name):
                for _ in range(4): EventLoop.idle()
                output = os.environ.get('MEONG_ANDROID_RENDER_DIR')
                if output:
                    Path(output).mkdir(parents=True,exist_ok=True)
                    app.stage.export_to_png(str(Path(output)/f'{name}-{width}x{height}.png'))
            try:
                settle('idle')
                self.assertEqual(tuple(map(int, app.stage.size)), (width, height))
                self.assertFalse(app.camera_device.enabled)
                self.assertFalse(app._operator_allowed())
                self.assertEqual(len(app.templates),12)
                self.assertTrue(str(app.events.path).startswith(directory))
                app._choose_photo(); app._complete_tutorial(); app._change_copies(1)
                self.assertTrue(app._test_photo_button.disabled)
                app._shift_template(1); app._change_copies(1)
                self.assertEqual(app.template_index,1)
                settle('gallery')
                self.assertTrue(app._test_photo_button.disabled)
                app._enter_photo_test()
                self.assertEqual(app.navigation.page,'templates')
                self.assertIsNone(app._photo_jobs)
                app._return_ad(); app._choose_game()
                settle('game-intro')
                self.assertEqual(app.navigation.page,'game_preview')
                self.assertFalse(app._sandbox_enabled)
                self.assertFalse(app._mock_enabled)
                app._open_game_demo()
                app._demo_code.text = 'DEMO-ANDROID-A1'
                app._claim_game_demo()
                deadline = time.monotonic()+5
                while app.navigation.page == 'game_receipt' and time.monotonic() < deadline:
                    app._poll_game()
                    EventLoop.idle()
                    time.sleep(.005)
                self.assertEqual(app.navigation.page, 'game_play')
                self.assertTrue(app._operator_key(None, 27))
                self.assertEqual(app.navigation.page, 'game_play')
                self.assertTrue(app._game_paused)
                self.assertFalse(app._closed)
                app.on_pause()
                self.assertTrue(app._suspended)
                app.on_resume()
                self.assertFalse(app._suspended)
                self.assertTrue(app._game_paused)
                from photobooth.kiosk_v2.demo_game import DemoGameStore, DemoClaimError
                reopened = DemoGameStore(Path(directory)/'data/kiosk-v2-p4')
                with self.assertRaisesRegex(DemoClaimError, 'used'):
                    reopened.claim('DEMO-ANDROID-A1')
            finally:
                app.on_stop()
                for name in ('_game_jobs','_mock_jobs','_health_reports'):
                    getattr(app,name).wait_closed()
                Window.remove_widget(app.stage)
                Window.size = previous_size
