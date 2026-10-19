"""Local face presence for the advertising invitation, without face identity.

The application-bundled OpenCV frontal-face cascade requires no model download or
MediaPipe wheel. It is intentionally a presence hint: lighting, pose and the
camera location affect detection, so the manual start button is always kept.
The existing bounded inference mailbox is reused with a separate detector and
thread. No second camera is opened and no pre-session image is saved.
"""

import gzip
import math
from pathlib import Path

import cv2

from photobooth.palm_gesture import PalmGestureWorker


class OpenCVFaceDetector:
    """Count a sufficiently large frontal face within the central camera area."""

    def __init__(self):
        # Newer OpenCV wheels may omit the data files even while exposing
        # cv2.data.haarcascades. Ship the pinned upstream model with its license
        # instead of relying on that optional wheel payload or a first-run URL.
        bundled = Path(__file__).resolve().parent / 'assets' / 'models' / 'haarcascade_frontalface_default.xml.gz'
        # Read the losslessly compressed upstream model without writing to
        # the checkout, which can be read-only on an installed booth.
        with gzip.open(bundled, 'rt', encoding='utf-8') as source:
            xml = source.read()
        storage = cv2.FileStorage(xml, cv2.FILE_STORAGE_READ | cv2.FILE_STORAGE_MEMORY)
        self.cascade = cv2.CascadeClassifier()
        try:
            self.cascade.read(storage.getFirstTopLevelNode())
        finally:
            storage.release()
        if self.cascade.empty():
            raise RuntimeError('OpenCV frontal-face model is unavailable.')

    def detect(self, frame, captured_at):
        height, width = frame.shape[:2]
        scale = min(1, 480 / width, 360 / height)
        small = cv2.resize(frame, (max(1, round(width * scale)), max(1, round(height * scale))))
        grey = cv2.equalizeHist(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
        height, width = grey.shape
        faces = self.cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=6,
                                             minSize=(max(30, round(width * .12)),) * 2)
        return float(any(.15 * width <= x + w / 2 <= .85 * width
                         and .10 * height <= y + h / 2 <= .90 * height
                         for x, y, w, h in faces))

    def close(self):
        self.cascade = None


class FacePresenceWorker(PalmGestureWorker):
    """Reuse generation tags, fresh-frame checks, CPU limit and cancellation."""

    def __init__(self, enabled=True, detector_factory=None):
        super().__init__('.', enabled=enabled,
                         detector_factory=detector_factory or OpenCVFaceDetector,
                         worker_name='photobooth-face-presence')


class FacePresenceTrigger:
    """One invitation after a stable hold; tolerate brief detection misses.

    A gap in delivered inference is not proof that a person stayed present.
    After an invitation, a sustained absence or cooldown rearms the detector.
    Source timestamps prevent duplicate observations from creating fake time.
    """

    def __init__(self, hold_seconds=5, cooldown_seconds=45, miss_grace=.65):
        self.hold_seconds = hold_seconds
        self.cooldown_seconds = cooldown_seconds
        self.miss_grace = miss_grace
        self._held_since = self._last_positive = self._last_sample = None
        self._absent_since = self._triggered_at = None
        self._samples = 0
        self.progress = 0.0

    def pause(self):
        """Invalidate a partial hold while keeping invitation cooldown intact."""
        self._held_since = self._last_positive = self._last_sample = None
        self._absent_since = None
        self._samples = 0
        self.progress = 0

    def observe(self, present, timestamp):
        if not math.isfinite(timestamp) or (self._last_sample is not None and timestamp <= self._last_sample):
            return False
        if self._last_sample is not None and timestamp - self._last_sample > .8:
            self.pause()
        self._last_sample = timestamp
        if self._triggered_at is not None:
            if not present:
                self._absent_since = timestamp if self._absent_since is None else self._absent_since
            else:
                self._absent_since = None
            if ((self._absent_since is not None and timestamp - self._absent_since >= 2)
                    or timestamp - self._triggered_at >= self.cooldown_seconds):
                self._triggered_at = None
                self._held_since = self._last_positive = None
                self._samples = 0
            else:
                return False
        if not present:
            if self._last_positive is None or timestamp - self._last_positive > self.miss_grace:
                self._held_since = None
                self._samples = 0
                self.progress = 0
            return False
        if self._last_positive is not None and timestamp - self._last_positive > self.miss_grace:
            self._held_since = None
            self._samples = 0
        self._last_positive = timestamp
        if self._held_since is None:
            self._held_since = timestamp
        self._samples += 1
        self.progress = min(1, (timestamp - self._held_since) / self.hold_seconds)
        if self.progress >= 1 and self._samples >= 4:
            self._triggered_at = timestamp
            self._held_since = None
            self.progress = 0
            return True
        return False
