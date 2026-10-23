"""Lazy optional detector initialization outside the native GUI thread."""

from dataclasses import dataclass
import logging
import threading
import time

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetectorParts:
    worker: object
    trigger: object
    confidence: float = .5
    max_age: float = .5


class DeferredDetector:
    def __init__(self, factory, *, enabled=True, parts=None):
        self.enabled = enabled
        self._factory, self._parts = factory, parts
        self._lock = threading.Lock()
        self._thread = None
        self._closed = False
        self._state = 'idle' if enabled else 'disabled'

    @property
    def parts(self):
        with self._lock:
            return self._parts

    @property
    def state(self):
        with self._lock:
            parts, state = self._parts, self._state
        return parts.worker.state if parts is not None and state != 'closed' else state

    def start(self):
        with self._lock:
            if not self.enabled or self._closed:
                return
            if self._parts is not None:
                self._parts.worker.start()
                return
            if self._thread is not None:
                return
            self._state = 'loading'
            self._thread = threading.Thread(target=self._load, name='portrait-v2-detector-init', daemon=True)
            self._thread.start()

    def _load(self):
        parts = None
        try:
            parts = self._factory()
            with self._lock:
                if self._closed:
                    return
            parts.worker.start()
            with self._lock:
                if not self._closed:
                    self._parts = parts
                    parts = None
        except Exception:
            LOG.warning('Optional detector initialization unavailable; manual entry stays active', exc_info=True)
            with self._lock:
                if not self._closed:
                    self._state = 'unavailable'
        finally:
            if parts is not None:
                parts.worker.close()

    def pause(self):
        parts = self.parts
        if parts is not None:
            parts.worker.pause()
            parts.trigger.pause()

    def close(self):
        with self._lock:
            self._closed = True
            self._state = 'closed'
            parts, self._parts = self._parts, None
        if parts is not None:
            parts.worker.close()


def palm_parts(model_path):
    from photobooth.palm_gesture import (
        MAX_RESULT_AGE, PALM_CONFIDENCE, PalmGestureWorker, PalmHoldTrigger,
    )
    return DetectorParts(PalmGestureWorker(model_path), PalmHoldTrigger(),
                         PALM_CONFIDENCE, MAX_RESULT_AGE)


class PalmShutter:
    """Reuse v1's deliberate hold/release; never save or count down by itself."""

    def __init__(self, model_path=None, *, enabled=True, parts=None, clock=time.monotonic):
        from pathlib import Path
        path = model_path or Path(__file__).resolve().parents[2] / 'data' / 'models' / 'gesture_recognizer.task'
        self._detector = DeferredDetector(lambda: palm_parts(path), enabled=enabled, parts=parts)
        self._last_submit = None
        self._clock = clock

    @property
    def state(self):
        return self._detector.state

    @property
    def needs_release(self):
        parts = self._detector.parts
        return bool(parts and parts.trigger.needs_release)

    @property
    def progress(self):
        parts = self._detector.parts
        return parts.trigger.progress if parts else 0

    def update(self, frame, revision, *, active, can_trigger, now=None):
        if not self._detector.enabled or self.state == 'closed':
            return False
        if not active or frame is None:
            self.pause()
            return False
        self._detector.start()
        parts = self._detector.parts
        if parts is None:
            return False
        now = self._clock() if now is None else now
        if self._last_submit is None or now - self._last_submit >= .15:
            parts.worker.submit(frame, revision)
            self._last_submit = now
        result = parts.worker.poll()
        parts.trigger.expire(now - parts.max_age)
        if (result is not None and result.context == revision and
                0 <= now - result.captured_at <= parts.max_age):
            fired = parts.trigger.observe(result.score >= parts.confidence, result.captured_at,
                                           allow_trigger=can_trigger)
            return bool(fired and can_trigger)
        return False

    def latch(self):
        parts = self._detector.parts
        if parts is not None:
            parts.trigger.latch()
            parts.worker.pause()
        self._last_submit = None

    def pause(self):
        self._detector.pause()
        self._last_submit = None

    def close(self):
        self._detector.close()
