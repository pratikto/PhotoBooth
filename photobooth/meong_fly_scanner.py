"""Standalone QR demo scanner. Camera/decoder work never blocks the GUI.

Frames stay in memory. Decode the original orientation; mirror only the GUI
texture. A decoded token fills the input, never consumes a receipt by itself.
"""
import threading
import time

SCAN_PREVIEW = (100, 261, 160, 164)
# Bottom-left, bottom-right, top-right, top-left: vertical + horizontal flip
# for top-origin RGB camera bytes. Raw camera/decoder frames are never flipped.
MIRRORED_UV = (1, 1, 0, 1, 0, 0, 1, 0)


def is_demo_token(value):
    return isinstance(value, str) and value.startswith('DEMO-') and 5 < len(value) <= 100


class ReceiptScanner:
    def __init__(self, camera_index=0, camera_factory=None, detector_factory=None):
        self.camera_index = camera_index
        self._camera_factory = camera_factory
        self._detector_factory = detector_factory
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._snapshot = (0, None, None, 'Kamera belum aktif')
        self._serial = 0
        self._disposed = False

    def snapshot(self):
        with self._lock:
            return self._snapshot

    def set_active(self, active):
        if not active or self._disposed:
            self._stop.set()
            with self._lock:
                self._snapshot = (self._serial, None, None, 'Kamera belum aktif')
            return
        # An opening/closing driver must finish before another handle is opened.
        if self._thread is not None and self._thread.is_alive():
            return
        # Keep failures visible; retry only after leaving and entering Scan.
        if self._thread is not None and not self._stop.is_set():
            return
        self._stop = threading.Event()
        with self._lock:
            self._snapshot = (self._serial, None, None, 'Membuka kamera...')
        self._thread = threading.Thread(target=self._run, args=(self._stop,),
                                        name='meong-demo-qr', daemon=True)
        self._thread.start()

    def dispose(self):
        self._disposed = True
        self.set_active(False)

    def _publish(self, stop, frame, code, status):
        with self._lock:
            if stop.is_set() or self._disposed:
                return
            self._serial += 1
            self._snapshot = (self._serial, frame, code, status)

    def _run(self, stop):
        camera = None
        try:
            import cv2
            from .camera import Camera
            camera = (self._camera_factory or Camera)(self.camera_index)
            if not camera.open():
                self._publish(stop, None, None, 'Kamera tidak tersedia. Ketik kode demo.')
                return
            if stop.is_set():
                return
            detector = (self._detector_factory or cv2.QRCodeDetector)()
            next_decode = 0.0
            code = None
            status = 'Arahkan QR DEMO ke kamera'
            while not stop.is_set():
                raw = camera.read()
                if raw is None:
                    self._publish(stop, None, None, 'Kamera terputus. Ketik kode demo.')
                    stop.wait(.10)
                    continue
                h, w = raw.shape[:2]
                scale = min(1.0, 640 / max(w, h))
                frame = cv2.resize(raw, (round(w*scale), round(h*scale))) if scale < 1 else raw
                if time.monotonic() >= next_decode:
                    payload, _, _ = detector.detectAndDecode(frame)
                    payload = payload.strip()
                    if payload:
                        code = payload if is_demo_token(payload) else None
                        status = ('QR terbaca. Tekan VALIDASI DEMO 1X.' if code else
                                  'QR bukan kode DEMO. Struk asli belum didukung.')
                    next_decode = time.monotonic() + .25
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._publish(stop, (rgb.shape[1], rgb.shape[0], rgb.tobytes()), code, status)
                stop.wait(1/30)
        except Exception:
            # Do not expose QR content/device internals in logs or block manual entry.
            self._publish(stop, None, None, 'Kamera/QR gagal. Ketik kode demo.')
        finally:
            if camera is not None:
                camera.close()  # May wait for the driver; this is never the UI thread.
