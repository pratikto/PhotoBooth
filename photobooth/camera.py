"""Desktop camera reader with a single-slot, latest-frame mailbox.

OpenCV read() can block while a USB camera waits for its next exposure. Only
our acquisition thread calls it after startup; the GUI reads a cached frame
without waiting. There is deliberately no frame queue: displaying old queued
frames creates visible delay even when the UI renders at a reasonable FPS.
"""
import sys
import threading
import time
import cv2


class Camera:
    """Keep draining the camera independently of Kivy's rendering loop."""

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = None
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._latest = None
        self._latest_time = 0.0

    def open(self):
        """Verify one frame before starting the nonblocking preview reader.

        The initial open/read is synchronous so the existing controller can
        correctly decide whether to enable the welcome screen. Subsequent reads
        happen exclusively in the worker. No resolution is forced: the saved
        photo keeps the camera's negotiated resolution.
        """
        self.close()
        # A broken driver may remain blocked during shutdown. Do not open a
        # second handle or reset its stop signal until that worker has exited.
        if self._thread is not None and self._thread.is_alive():
            return False
        if sys.platform.startswith('win'):
            capture = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not capture.isOpened():
                capture.release()
                capture = cv2.VideoCapture(self.camera_index)
        else:
            capture = cv2.VideoCapture(self.camera_index)
        if not capture.isOpened():
            capture.release()
            return False
        # Backends may ignore this hint; continuous acquisition below is the
        # main mechanism preventing buffered frames from building up.
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        success, frame = capture.read()
        if not success or frame is None:
            capture.release()
            return False
        self.capture = capture
        with self._lock:
            self._latest = frame
            self._latest_time = time.monotonic()
        self._stop.clear()
        self._thread = threading.Thread(target=self._acquire,
                                        args=(capture,), daemon=True,
                                        name='photobooth-camera')
        self._thread.start()
        return True

    def _acquire(self, capture):
        """Publish complete frames; release the device from its owning thread."""
        try:
            while not self._stop.is_set():
                success, frame = capture.read()
                if self._stop.is_set():
                    break
                with self._lock:
                    self._latest = frame if success else None
                    self._latest_time = time.monotonic() if success else 0.0
                if not success:
                    # Avoid a busy loop if a camera is unplugged or its driver
                    # returns immediately with failure. Event.wait is cancellable.
                    self._stop.wait(0.03)
        finally:
            # Never call release concurrently with a blocked capture.read().
            capture.release()

    def read(self):
        """Return the newest frame immediately, or None when it is stale.

        OpenCV supplies new arrays for successive reads. Consumers must treat
        this shared frame as read-only; processing that mutates pixels must copy
        first. Returning a reference avoids another full-resolution memory copy.
        A one-second age limit prevents capturing an old frame after a disconnect.
        """
        with self._lock:
            if self._stop.is_set() or time.monotonic() - self._latest_time > 1.0:
                return None
            return self._latest

    def close(self):
        """Request shutdown without racing the camera driver's native read call."""
        self._stop.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=2.0)
        with self._lock:
            self._latest = None
            self._latest_time = 0.0
        self.capture = None
