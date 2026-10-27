"""Opt-in native reuse smoke; desktop rendering is not Android acceptance."""
import importlib
import os
from pathlib import Path
import tempfile
import unittest
from contextlib import ExitStack
from unittest.mock import patch


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_TEST_ANDROID') == '1', 'Android preview native smoke is opt-in')
class AndroidWidgetTests(unittest.TestCase):
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
            finally:
                app.on_stop()
                for name in ('_game_jobs','_mock_jobs','_health_reports'):
                    getattr(app,name).wait_closed()
                Window.remove_widget(app.stage)
