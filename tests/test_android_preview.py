"""A0 policy and package boundaries; no Android SDK/device is implied."""
import configparser
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

from photobooth.kiosk_v2.android_preview import configure_preview

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_android', ROOT/'tools/prepare_android.py')
packaging = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packaging)


class AndroidPolicyTests(unittest.TestCase):
    def test_inherited_desktop_opt_ins_are_forced_off(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {'PHOTOBOOTH_V2_DRIVE': '1', 'PHOTOBOOTH_V2_PRINT': '1',
                   'PHOTOBOOTH_V2_CHECKOUT_SANDBOX': '1', 'PHOTOBOOTH_CAMERA': '1'}
            root = configure_preview(directory, environ=env)
            self.assertEqual(env['KIVY_HOME'], str(root/'kivy'))
            for key in ('PHOTOBOOTH_V2_DRIVE','PHOTOBOOTH_V2_PRINT','PHOTOBOOTH_V2_CHECKOUT_SANDBOX','PHOTOBOOTH_CAMERA'):
                self.assertEqual(env[key], '0')
            self.assertEqual(env['KIVY_VIDEO'], 'null')

    def test_relative_storage_is_rejected(self):
        with self.assertRaises(ValueError): configure_preview('relative', environ={})

    def test_package_allowlist_excludes_credentials_archives_and_customer_data(self):
        for path in ('photobooth/local_settings.py','photobooth/local_settings.example.py',
                     'photobooth/old/private.py','photobooth/data/private.py','photobooth/a.sqlite',
                     '../photobooth/app.py','data/customer.jpg','/photobooth/app.py'):
            self.assertFalse(packaging.eligible(path), path)
        for path in ('photobooth/kiosk_v2/app.py','photobooth/assets/ads/sample-01.jpg',
                     'photobooth/kiosk_v2/assets/meong-fly-camera.png'):
            self.assertTrue(packaging.eligible(path), path)

    def test_spec_is_portrait_offline_and_uses_mobile_recipes(self):
        config = configparser.ConfigParser()
        config.read(ROOT/'android/buildozer.spec')
        self.assertEqual(config['app']['android.permissions'], '')
        self.assertEqual(config['app']['orientation'], 'portrait')
        for desktop in ('pywin32','opencv-contrib-python','ffpyplayer','python-escpos'):
            self.assertNotIn(desktop, config['app']['requirements'])

    def test_staging_has_correct_entry_and_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)/'app'
            manifest = packaging.prepare(destination)
            self.assertEqual((destination/'main.py').read_bytes(), (ROOT/'android/main.py').read_bytes())
            self.assertIn('photobooth/kiosk_v2/android_preview.py',manifest)
            self.assertNotIn('photobooth/local_settings.py',manifest)
            self.assertFalse((destination/'data').exists())
            with self.assertRaises(ValueError): packaging.prepare(destination)


if __name__ == '__main__': unittest.main()
