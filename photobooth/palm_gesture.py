"""Optional, local open-palm recognition without blocking Kivy or the camera.

There are three independent responsibilities here:
* PalmHoldTrigger turns consecutive observations into one deliberate shutter.
* MediaPipePalmDetector performs actual Open_Palm inference on small RGB frames.
* PalmGestureWorker owns the native detector and a one-frame mailbox. Results
  carry their capture-page revision so a late inference cannot operate a new page.

MediaPipe is imported only in the worker. Missing packages, a first-run model
download failure, or an unsupported device leave normal button capture intact.
Camera pixels are processed locally; only the public model is downloaded.
"""

from dataclasses import dataclass
import hashlib
import logging
import math
import os
from pathlib import Path
import tempfile
import threading
import time

import cv2
import requests


LOGGER = logging.getLogger(__name__)
MODEL_URL = ('https://storage.googleapis.com/mediapipe-models/gesture_recognizer/'
             'gesture_recognizer/float16/1/gesture_recognizer.task')
MODEL_SHA256 = '97952348cf6a6a4915c2ea1496b4b37ebabc50cbbf80571435643c455f2b0482'
MODEL_BYTES = 8373440
HOLD_SECONDS = 1.0
RELEASE_SECONDS = 0.4
MAX_SAMPLE_GAP = 0.4
MAX_RESULT_AGE = 0.5
PALM_CONFIDENCE = 0.6


class PalmHoldTrigger:
    """Require a continuous hold and a deliberate release between shutters.

    This small state machine uses observation timestamps, never GUI tick counts.
    A single positive image, repeated delivery, a long inference gap, and holding
    the same hand across successive photos must not generate repeated captures.
    Manual button capture also calls latch(), requiring release before the next
    gesture. Release can be observed during a countdown without starting another.
    """

    def __init__(self):
        self.needs_release = False
        self.last_sample_at = None
        self._held_since = self._released_since = None
        self._positive_samples = 0
        self.progress = 0.0

    def pause(self):
        """Discard partial holds on a missing frame or page change; keep latch."""
        self._held_since = self._released_since = None
        self._positive_samples = 0
        self.last_sample_at = None
        self.progress = 0.0

    def latch(self):
        """Block the next gesture until non-palm frames confirm a release."""
        self.pause()
        self.needs_release = True

    def expire(self, now):
        """An inference stall is not evidence of a continuous palm or release."""
        if self.last_sample_at is not None and now - self.last_sample_at > MAX_SAMPLE_GAP:
            self.pause()

    def observe(self, open_palm, captured_at, allow_trigger=True):
        """Return True once after a full hold; all inputs are fresh observations."""
        if not math.isfinite(captured_at):
            return False
        if self.last_sample_at is not None:
            if captured_at <= self.last_sample_at:
                return False
            self.expire(captured_at)
        self.last_sample_at = captured_at
        if self.needs_release:
            if open_palm:
                self._released_since = None
            elif self._released_since is None:
                self._released_since = captured_at
            elif captured_at - self._released_since >= RELEASE_SECONDS:
                self.needs_release = False
                self._released_since = None
            return False
        if not allow_trigger or not open_palm:
            self._held_since = None
            self._positive_samples = 0
            self.progress = 0.0
            return False
        if self._held_since is None:
            self._held_since = captured_at
        self._positive_samples += 1
        self.progress = min(1.0, (captured_at - self._held_since) / HOLD_SECONDS)
        if self.progress >= 1.0 and self._positive_samples >= 4:
            self.latch()
            return True
        return False


def ensure_gesture_model(path, stop=None):
    """Cache the pinned public model with integrity and interrupted-write checks.

    The cache lives under data/, already ignored by Git. A unique temporary file
    is replaced atomically only after size/SHA-256 verification. Neither a failed
    download nor closing the application can leave a partial model at its final
    path. Existing valid files work offline and are never fetched again.
    """
    path = Path(path)
    stop = stop if stop is not None else threading.Event()
    if (path.is_file() and path.stat().st_size == MODEL_BYTES
            and hashlib.sha256(path.read_bytes()).hexdigest() == MODEL_SHA256):
        return path
    if stop.is_set():
        raise RuntimeError('Palm model setup was cancelled.')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        # Both per-read timeouts and an overall deadline keep this optional
        # initialization bounded, including servers delivering very slow chunks.
        deadline = time.monotonic() + 90
        with requests.get(MODEL_URL, stream=True, timeout=(15, 15)) as response:
            response.raise_for_status()
            digest, size = hashlib.sha256(), 0
            with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.part', delete=False) as output:
                temporary = Path(output.name)
                for chunk in response.iter_content(65536):
                    if stop.is_set() or time.monotonic() > deadline:
                        raise RuntimeError('Palm model setup was cancelled or timed out.')
                    size += len(chunk)
                    if size > MODEL_BYTES:
                        raise ValueError('Palm model download exceeds the expected size.')
                    digest.update(chunk)
                    output.write(chunk)
        if size != MODEL_BYTES or digest.hexdigest() != MODEL_SHA256:
            raise ValueError('Palm model download failed its size/checksum verification.')
        if stop.is_set():
            raise RuntimeError('Palm model setup was cancelled.')
        os.replace(temporary, path)
        return path
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class MediaPipePalmDetector:
    """Own one CPU GestureRecognizer; all methods run on its worker thread.

    Use the Tasks API rather than the removed legacy mp.solutions interface.
    VIDEO mode reuses hand tracking between observations. A positive palm must
    be classified as Open_Palm at >=60% confidence, rather than merely finding
    a hand-shaped object. Saved photographs are never resized or annotated.
    """

    def __init__(self, model_path, stop=None):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision

        self._mp = mp
        model_path = ensure_gesture_model(model_path, stop)
        options = vision.GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path), delegate=BaseOptions.Delegate.CPU),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self._recognizer = vision.GestureRecognizer.create_from_options(options)
        self._last_timestamp_ms = -1

    def detect(self, frame, captured_at):
        """Return a real model score, keeping aspect ratio within 480x360."""
        height, width = frame.shape[:2]
        scale = min(1.0, 480 / width, 360 / height)
        if scale < 1:
            frame = cv2.resize(frame, (max(1, round(width * scale)), max(1, round(height * scale))),
                               interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = max(self._last_timestamp_ms + 1, int(captured_at * 1000))
        result = self._recognizer.recognize_for_video(image, timestamp_ms)
        self._last_timestamp_ms = timestamp_ms
        # Keep the returned top category, then apply our confidence threshold
        # in the controller. A different top gesture must never count as a palm.
        return max((category.score for hand in result.gestures for category in hand
                    if category.category_name == 'Open_Palm'), default=0.0)

    def close(self):
        self._recognizer.close()


@dataclass(frozen=True)
class PalmObservation:
    """Immutable result tagged with the exact originating capture page."""

    context: int
    captured_at: float
    score: float


class PalmGestureWorker:
    """Keep inference, model downloads, and native resource ownership off Kivy.

    At most one pending input and one latest output are retained. Input frames
    are read-only references supplied by Camera's mailbox. The same array is
    not submitted twice, so repeatedly polling a frozen camera cannot fabricate
    a one-second hold. A context change invalidates in-flight old-page results.
    """

    def __init__(self, model_path, enabled=True, detector_factory=None, worker_name='photobooth-palm'):
        self._model_path = Path(model_path)
        self._factory = detector_factory
        self._worker_name = worker_name
        self._enabled = enabled
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._thread = None
        self._state = 'idle' if enabled else 'disabled'
        self._generation = 0
        self._context = self._pending = self._result = self._last_frame = None

    @property
    def state(self):
        with self._lock:
            return self._state

    def start(self):
        """Start optional initialization once; unavailable detectors do not retry in a loop."""
        with self._lock:
            if self._state != 'idle' or self._stop.is_set():
                return
            self._state = 'loading'
            self._thread = threading.Thread(target=self._run, name=self._worker_name, daemon=True)
            self._thread.start()

    def submit(self, frame, context):
        """Offer the latest frame immediately; recognition never runs here."""
        with self._lock:
            if self._state != 'ready' or self._stop.is_set():
                return
            if context != self._context:
                self._generation += 1
                self._context, self._last_frame, self._result = context, None, None
            if frame is self._last_frame:
                return
            self._last_frame = frame
            self._pending = (frame, context, self._generation, time.monotonic())
        self._wake.set()

    def poll(self):
        """Consume one observation once; duplicate GUI polls cannot extend a hold."""
        with self._lock:
            result, self._result = self._result, None
        return result

    def pause(self):
        """Invalidate a queued/in-flight observation when leaving capture or losing frames."""
        with self._lock:
            self._generation += 1
            self._context = self._pending = self._result = self._last_frame = None

    def _run(self):
        detector = None
        try:
            detector = (self._factory() if self._factory is not None
                        else MediaPipePalmDetector(self._model_path, self._stop))
            with self._lock:
                if self._stop.is_set():
                    return
                self._state = 'ready'
            next_run = 0.0
            while not self._stop.is_set():
                self._wake.wait(0.2)
                self._wake.clear()
                if self._stop.wait(max(0.0, next_run - time.monotonic())):
                    break
                with self._lock:
                    job, self._pending = self._pending, None
                if job is None:
                    continue
                frame, context, generation, captured_at = job
                score = float(detector.detect(frame, captured_at))
                if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                    raise ValueError('Palm detector returned an invalid confidence score.')
                next_run = time.monotonic() + 0.1  # Cap CPU work at ten inferences/second.
                with self._lock:
                    if (context == self._context and generation == self._generation
                            and not self._stop.is_set()):
                        self._result = PalmObservation(context, captured_at, score)
        except Exception:
            # This is an optional input device. A missing native library or
            # failed inference must not crash a paid session or disable buttons.
            LOGGER.warning('Palm recognition unavailable; button capture remains available.', exc_info=True)
            with self._lock:
                if not self._stop.is_set():
                    self._state = 'unavailable'
                self._pending = self._result = self._last_frame = None
        finally:
            if detector is not None:
                try:
                    detector.close()
                except Exception:
                    LOGGER.warning('Could not close the palm recognizer cleanly.', exc_info=True)

    def close(self):
        """Request shutdown; native close stays on its owning worker thread."""
        self._stop.set()
        self._wake.set()
        self.pause()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=0.3)
        with self._lock:
            self._state = 'closed'
