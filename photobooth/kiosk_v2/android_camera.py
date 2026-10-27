"""Camera2 adapter for the existing AsyncCamera/BGR and PhotoJobs contracts.

JNI is imported only on Android's camera worker. No desktop OpenCV camera,
second handle, GUI-thread driver call or saved idle frame is used.
"""
import io
import threading
import time


def java_bytes(data):
    """pyjnius byte arrays may expose signed elements, unlike Python bytes."""
    if isinstance(data, bytes):
        return data
    for name in ('tobytes', 'tostring'):
        method = getattr(data, name, None)
        if method is not None:
            return method()
    return bytes(value & 255 for value in data)


def nv21_bgr(data, width, height, rotation=0):
    import numpy as np
    if width % 2 or height % 2 or len(data) != width * height * 3 // 2:
        raise ValueError('Invalid native camera frame')
    raw = np.frombuffer(data, dtype=np.uint8)
    y = raw[:width*height].reshape(height, width).astype(np.int32) - 16
    vu = raw[width*height:].reshape(height//2, width//2, 2).astype(np.int32) - 128
    v = vu[:, :, 0].repeat(2, 0).repeat(2, 1)
    u = vu[:, :, 1].repeat(2, 0).repeat(2, 1)
    y = np.maximum(y, 0) * 298
    bgr = np.stack(((y+516*u+128) >> 8, (y-100*u-208*v+128) >> 8,
                    (y+409*v+128) >> 8), axis=-1).clip(0, 255).astype(np.uint8)
    if rotation not in (0, 90, 180, 270):
        raise ValueError('Invalid native camera rotation')
    return np.ascontiguousarray(np.rot90(bgr, -(rotation//90)))


def preview_pixels(frame):
    """Same bounded RGB presentation contract without desktop OpenCV."""
    from PIL import Image
    image = Image.fromarray(frame[:, :, ::-1].copy(), 'RGB')
    image.thumbnail((640, 480), Image.Resampling.LANCZOS)
    return image.size, image.tobytes()


class Camera2Service:
    def __init__(self, facing=0, *, bridge_factory=None):
        self.facing = facing
        self._bridge_factory = bridge_factory
        self._bridge = None
        self._closing = None
        self._last_sequence = -1
        self._last_frame = None
        self._lock = threading.RLock()

    def open(self):
        with self._lock:
            if self._closing is not None:
                if not self._closing.isClosed():
                    return False
                self._closing = None
            if self._bridge_factory is None:
                from android.permissions import check_permission, Permission
                if not check_permission(Permission.CAMERA):
                    return False
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                bridge = autoclass('id.meong.nativebridge.CameraBridge')(activity, self.facing)
            else:
                bridge = self._bridge_factory(self.facing)
            self._bridge = bridge
        # openAndWait has a bounded wait on this worker, never the Kivy thread.
        if not bridge.openAndWait(8000):
            self.close()
            return False
        deadline = time.monotonic()+3
        while bridge.latestFrame() is None and time.monotonic()<deadline and bridge.isReady():
            time.sleep(.03)
        if bridge.latestFrame() is None:
            self.close()
            return False
        return True

    def read(self):
        with self._lock:
            bridge = self._bridge
            if bridge is None or not bridge.isReady():
                return None
            packet = bridge.latestFrame()
            if packet is None:
                return None
            sequence = int(packet.sequence)
            if sequence != self._last_sequence:
                self._last_frame = nv21_bgr(java_bytes(packet.pixels), packet.width,
                                             packet.height, packet.rotation)
                self._last_sequence = sequence
            return self._last_frame

    def capture(self):
        from PIL import Image, ImageOps
        import numpy as np
        with self._lock:
            bridge = self._bridge
        if bridge is None:
            raise RuntimeError('Camera unavailable')
        jpeg = bridge.captureJpeg(8000)
        if jpeg is None:
            raise RuntimeError('Native capture cancelled or unavailable')
        with Image.open(io.BytesIO(java_bytes(jpeg))) as image:
            rgb = np.array(ImageOps.exif_transpose(image).convert('RGB'))
        return rgb[:, :, ::-1].copy()

    def close(self):
        with self._lock:
            bridge, self._bridge = self._bridge, None
            self._last_frame = None
            self._last_sequence = -1
        if bridge is not None:
            self._closing = bridge
            bridge.close()


class MobileCamera:
    """Expose the existing mailbox plus a guarded full-resolution still call."""
    def __init__(self, facing=0, *, service_factory=Camera2Service):
        from .devices import AsyncCamera
        self._service = None
        self._lock = threading.Lock()
        self._active = True
        self._generation = 0
        def factory(index):
            self._service = service_factory(index)
            return self._service
        self._camera = AsyncCamera(index=facing, factory=factory)

    enabled = True

    @property
    def state(self):
        return self._camera.state

    def start(self):
        self._camera.start()

    def read(self):
        return self._camera.read()

    def set_active(self, active):
        with self._lock:
            self._active = bool(active)
            self._generation += 1
        self._camera.set_active(active)

    def capture(self):
        with self._lock:
            generation = self._generation
            if not self._active or self._service is None or self.read() is None:
                raise RuntimeError('Camera is not active')
            service = self._service
        frame = service.capture()
        with self._lock:
            if not self._active or generation != self._generation:
                raise RuntimeError('Capture interrupted by lifecycle change')
        return frame

    def close(self):
        self.set_active(False)
        self._camera.close()

    def wait_closed(self, timeout=3):
        self._camera.wait_closed(timeout)
