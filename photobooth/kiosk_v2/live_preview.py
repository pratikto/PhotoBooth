"""Bounded view-only RGB preparation, never on the Kivy/touch thread."""

from dataclasses import dataclass
import logging
import threading
import time

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreviewFrame:
    context: int
    captured_at: float
    size: tuple
    pixels: bytes


def prepare_pixels(frame):
    """Resize a copy for display; retain original BGR camera pixels for saving."""
    import cv2
    height, width = frame.shape[:2]
    scale = min(1, 640 / width, 480 / height)
    if scale < 1:
        frame = cv2.resize(frame, (max(1, round(width * scale)), max(1, round(height * scale))),
                           interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return (rgb.shape[1], rgb.shape[0]), rgb.tobytes()


class LivePreview:
    """One pending input/latest output; page changes discard in-flight work."""

    def __init__(self, prepare=prepare_pixels, *, clock=time.monotonic):
        self._prepare, self._clock = prepare, clock
        self._lock = threading.Lock()
        self._wake, self._stop = threading.Event(), threading.Event()
        self._thread = None
        self._context = self._pending = self._result = self._last_frame = None
        self._generation = 0

    def submit(self, frame, context):
        with self._lock:
            if self._stop.is_set():
                return
            if context != self._context:
                self._generation += 1
                self._context, self._result, self._last_frame = context, None, None
            if frame is None:
                self._invalidate()
                return
            if frame is self._last_frame:
                return
            self._last_frame = frame
            self._pending = (frame, context, self._generation, self._clock())
            if self._thread is None:
                self._thread = threading.Thread(target=self._run, name='portrait-v2-preview', daemon=True)
                self._thread.start()
        self._wake.set()

    def read(self, context):
        with self._lock:
            result = self._result
            if (self._stop.is_set() or result is None or result.context != context or
                    not 0 <= self._clock() - result.captured_at <= .5):
                return None
            return result

    def _invalidate(self):
        self._generation += 1
        self._context = self._pending = self._result = self._last_frame = None

    def pause(self):
        with self._lock:
            self._invalidate()

    def _run(self):
        while not self._stop.is_set():
            self._wake.wait(.2)
            self._wake.clear()
            with self._lock:
                job, self._pending = self._pending, None
            if job is None:
                continue
            frame, context, generation, stamp = job
            try:
                size, pixels = self._prepare(frame)
                packet = PreviewFrame(context, stamp, size, pixels)
            except Exception:
                LOG.warning('Preview preparation failed; original capture remains available', exc_info=True)
                continue
            with self._lock:
                if generation == self._generation and not self._stop.is_set():
                    self._result = packet

    def close(self):
        self._stop.set()
        self.pause()
        self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=.05)

