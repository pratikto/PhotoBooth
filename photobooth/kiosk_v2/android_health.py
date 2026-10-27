"""Read-only native observations presented by the unchanged v2 health panel."""
from datetime import datetime, timezone
import threading
import time

from photobooth.device_health import HealthCheck, HealthSnapshot, check_disk, check_media, check_heartbeat, READY, UNKNOWN


class MobileHealthController:
    def __init__(self, app, scheduler):
        self.app, self.scheduler = app, scheduler
        self._lock = threading.Lock()

    def refresh(self, callback):
        if not self._lock.acquire(blocking=False):
            return
        app = self.app
        frame = app.camera_device.read()
        tick = app._operator_last_tick
        def run():
            try:
                printer = HealthCheck('printer', UNKNOWN,'Belum dikonfigurasi; kertas fisik belum diperiksa.')
                if app.mobile_settings['print_enabled']:
                    try:
                        from .android_usb import usb_context, find_device
                        _, manager = usb_context()
                        s=app.mobile_settings
                        device=find_device(manager,s['usb_vendor'],s['usb_product'])
                        allowed=manager.hasPermission(device)
                        printer=HealthCheck('printer', READY if allowed else UNKNOWN,
                            'USB terdeteksi dan diizinkan; kertas belum diperiksa.' if allowed else 'Izin USB diperlukan; tidak ada data cetak dikirim.')
                    except Exception:
                        printer=HealthCheck('printer',UNKNOWN,'USB belum tersedia; tidak ada data cetak dikirim.')
                checks=(HealthCheck('camera',READY if frame is not None else UNKNOWN,
                            'Frame kamera terbaru tersedia; tanpa membuka kamera kedua.' if frame is not None else 'Belum ada frame; periksa izin kamera.'),
                        printer,check_disk(app.private_root),
                        HealthCheck('network',UNKNOWN,'Status jaringan/provider belum diuji; tidak ada transaksi dibuat.'),
                        check_media(app.catalog),check_heartbeat(tick))
                snapshot=HealthSnapshot(datetime.now(timezone.utc).isoformat(),checks,platform='android')
                self.scheduler.after(0,lambda:callback(snapshot))
            finally:
                self._lock.release()
        threading.Thread(target=run,name='android-read-only-health',daemon=True).start()
