"""Android host of the actual GUI v2, native camera and original print/payment jobs."""
import importlib
import os
from pathlib import Path

from .android_settings import load_settings, configure_mobile, validated


def create_mobile(private_root, *, settings=None, camera=None, usb_sender=None, sandbox_jobs=None):
    settings = load_settings(private_root) if settings is None else validated(settings)
    root = configure_mobile(private_root, settings)
    # Original playlist discovery, with operator media in app-private storage.
    import photobooth.advertising as advertising
    advertising.DEFAULT_VIDEO_DIR = root/'ad_video'
    advertising.DEFAULT_VIDEO_DIR.mkdir(parents=True,exist_ok=True)
    os.environ.pop('PHOTOBOOTH_AD_CONFIG',None)
    if (root/'ad-playlist.json').is_file():
        os.environ['PHOTOBOOTH_AD_CONFIG']=str(root/'ad-playlist.json')
    from kivy.config import Config
    Config.set('kivy','exit_on_escape','0')
    from .android_preview import DATA_MODULES
    for name in DATA_MODULES:
        importlib.import_module('photobooth.kiosk_v2.'+name).PROJECT_ROOT = root
    from .app import PortraitKioskV2App
    from .android_camera import MobileCamera, preview_pixels
    from .devices import FaceInviter
    from .android_palm import mobile_palm
    from .live_preview import LivePreview
    from .photos import PhotoTest, PhotoJobs, configured_workspace
    from .android_usb import UsbOtgSender
    from photobooth.printer import ThermalPrinter, PrinterConfig

    mobile_camera = camera if camera is not None else MobileCamera(settings['camera_facing'])
    sender = usb_sender or UsbOtgSender(settings['usb_vendor'], settings['usb_product'])
    printer = ThermalPrinter(PrinterConfig(print_width_dots=settings['print_width'],
                                          dither_mode=settings['dither']), usb_sender=sender)

    class MobilePhotoTest(PhotoTest):
        def capture(self, preview_frame):
            # PhotoJobs invokes this off the GUI after the normal five-second
            # countdown/ACK guard; never save a small displayed preview as raw.
            return super().capture(mobile_camera.capture())

    class AndroidV2App(PortraitKioskV2App):
        title = 'MEONG PHOTOBOOTH — ANDROID V2'
        mobile_settings = settings
        private_root = root

        def build(self):
            stage = super().build()
            self.live_preview.close()
            self.live_preview = LivePreview(prepare=preview_pixels)
            return stage

        def on_start(self):
            from kivy.utils import platform
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                from kivy.clock import Clock
                def camera_permission_result(*_):
                    if settings['print_enabled']:
                        Clock.schedule_once(lambda _dt:self._request_usb_permission() if not self._closed else None, .2)
                request_permissions([Permission.CAMERA],camera_permission_result)

        def _request_usb_permission(self):
            from .android_usb import request_usb_permission
            try:
                request_usb_permission(settings['usb_vendor'], settings['usb_product'])
                return 'Izinkan printer pada dialog Android. Periksa kabel USB OTG.'
            except Exception:
                return 'Printer belum tersedia. Sambungkan USB OTG dan periksa VID/PID.'

        def _ensure_photo_jobs(self):
            if self._photo_jobs is not None:
                return
            photo_root = (self._sandbox_jobs.store.flow.path.parent/'photo-tests'
                          if self._sandbox_enabled else root/'data/kiosk-v2-p3')
            def factory():
                workspace = None if self._sandbox_enabled else configured_workspace(root)
                client = None
                if settings['drive_enabled']:
                    from photobooth.drive_storage import AppsScriptDriveClient
                    from photobooth.booth_sync import BoothDriveClient
                    client = BoothDriveClient(AppsScriptDriveClient.from_configuration(),workspace.booth_id)
                return MobilePhotoTest(photo_root, booth_id=settings['booth_id']+'V2',
                    workspace=workspace, drive_client=client, drive_requested=settings['drive_enabled'],
                    printer=printer if settings['print_enabled'] else None,
                    raster_printer=printer, auto_print=settings['print_enabled'])
            self._photo_jobs = PhotoJobs(factory=factory)

        def _copy_simulator_url(self):
            from photobooth.qris_evidence import sandbox_qr_url
            from kivy.core.clipboard import Clipboard
            view=self._sandbox_view or {}
            order=view.get('order') or {}
            if (view.get('phase')=='WAITING' and order.get('state')=='PENDING'
                    and order.get('mode')=='sandbox' and not order.get('verification_pending')):
                try:
                    Clipboard.copy(sandbox_qr_url(order.get('qr_url')))
                except (TypeError,ValueError):
                    return

        def _build_sandbox_checkout(self,canvas):
            super()._build_sandbox_checkout(canvas)
            if (self._sandbox_view or {}).get('phase')=='WAITING':
                canvas.children[0].add_widget(self._action('SALIN URL QR UNTUK SIMULATOR',
                    self._copy_simulator_url,variant='tertiary',height=44))

        def _operator_key(self, window, key, *args):
            code = key[0] if isinstance(key,(tuple,list)) else key
            if code == 27:
                if self._operator_active:
                    self._close_operator()
                elif not self._closed and not self._suspended:
                    self._cancel_countdown()
                    self._pause_game()
                return True
            return super()._operator_key(window,key,*args)

        def _open_operator(self):
            if not self._operator_allowed():
                return
            from .android_settings_view import MobileSettingsPanel
            self._operator_epoch += 1
            self.face_inviter.pause()
            self.palm_shutter.pause()
            self._operator_panel = MobileSettingsPanel(self)
            self._operator_panel.open()

        def _poll_operator(self):
            from .operator_health import OperatorPanel
            if isinstance(self._operator_panel,OperatorPanel):
                return super()._poll_operator()
            self._health_reports.poll()

        def _open_mobile_health(self):
            if not self._operator_allowed():
                return
            from .operator_health import OperatorPanel, MainThreadScheduler
            from .android_health import MobileHealthController
            self._operator_epoch += 1
            self._operator_panel=OperatorPanel(self,MobileHealthController(self,MainThreadScheduler(self)))
            self._operator_panel.open()

    return AndroidV2App(camera_device=mobile_camera, face_inviter=FaceInviter(enabled=settings['face_enabled']),
                        palm_shutter=mobile_palm(root,enabled=settings['palm_enabled']), sandbox_jobs=sandbox_jobs)


def main(private_root=None):
    if private_root is None:
        from android.storage import app_storage_path
        private_root = Path(app_storage_path())/'meong-preview'
    app = create_mobile(private_root)
    try:
        app.run()
    finally:
        for name in ('camera_device','_game_jobs','_mock_jobs','_sandbox_jobs','_photo_jobs','_health_reports'):
            worker = getattr(app,name,None)
            if worker is not None:
                worker.close()
                worker.wait_closed()
