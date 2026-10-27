"""Android A0 host of the existing GUI; native hardware adapters come later."""
import importlib
import os
from pathlib import Path

DATA_MODULES = ('app', 'game_views', 'checkout_views', 'photo_views',
                'sandbox_views', 'operator_health')


def configure_preview(private_root, *, environ=None):
    """Force offline preview regardless of inherited desktop opt-ins."""
    env = os.environ if environ is None else environ
    root = Path(private_root)
    if not root.is_absolute():
        raise ValueError('Use an absolute app-private storage path')
    root.mkdir(parents=True, exist_ok=True)
    env.update({key: '0' for key in (
        'PHOTOBOOTH_CAMERA', 'PHOTOBOOTH_FACE_TRIGGER', 'PHOTOBOOTH_PALM_TRIGGER',
        'PHOTOBOOTH_V2_PRINT', 'PHOTOBOOTH_V2_AUTO_PRINT', 'PHOTOBOOTH_V2_DRIVE',
        'PHOTOBOOTH_V2_CHECKOUT_MOCK', 'PHOTOBOOTH_V2_CHECKOUT_SANDBOX',
        'PHOTOBOOTH_AD_VIDEO', 'PHOTOBOOTH_AUDIO')})
    env.update(PHOTOBOOTH_V2_STORAGE='1', KIVY_VIDEO='null', KIVY_NO_ARGS='1',
               KIVY_HOME=str(root / 'kivy'))
    env.setdefault('KIVY_LOG_MODE', 'MIXED')
    return root


def create_preview(private_root):
    root = configure_preview(private_root)
    from kivy.config import Config
    Config.set('kivy', 'exit_on_escape', '0')
    # These are data consumers of the desktop PROJECT_ROOT constant. Artwork
    # and catalogue/media paths remain relative to their original source files.
    for name in DATA_MODULES:
        module = importlib.import_module('photobooth.kiosk_v2.' + name)
        module.PROJECT_ROOT = root
    from .app import PortraitKioskV2App

    class AndroidPreviewApp(PortraitKioskV2App):
        title = 'MEONG ANDROID PREVIEW'

        def _operator_key(self, window, key, *args):
            code = key[0] if isinstance(key, (tuple, list)) else key
            if code == 27:  # Android Back: keep durable game state and the app alive.
                if not self._closed and not self._suspended:
                    self._pause_game()
                return True
            return super()._operator_key(window, key, *args)

        def _operator_allowed(self):
            return False  # No desktop device probes on the Android preview.

        def _enter_photo_test(self):
            return  # No synthetic capture or bypass of future camera consent.

        def _update_order(self):
            super()._update_order()
            self._disable_mobile_capture()

        def _disable_mobile_capture(self):
            button = getattr(self, '_test_photo_button', None)
            if button is not None:
                button.disabled = True
                button.text = 'KAMERA\nBELUM AKTIF'

    return AndroidPreviewApp()


def main(private_root=None):
    if private_root is None:
        from android.storage import app_storage_path
        private_root = Path(app_storage_path()) / 'meong-preview'
    app = create_preview(private_root)
    try:
        app.run()
    finally:
        # Reuse existing teardown, then wait for the durable local game worker.
        for name in ('_game_jobs', '_mock_jobs', '_photo_jobs', '_health_reports'):
            worker = getattr(app, name, None)
            if worker is not None:
                worker.close()
                worker.wait_closed()
