"""Configurable nonproduction true-inactivity recommendations, no visit hard cap."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PrivateInactivityPolicy:
    gallery_seconds: int = 90
    capture_seconds: int = 120
    review_seconds: int = 120
    final_preview_seconds: int = 120
    warning_seconds: int = 15

    def __post_init__(self):
        values = (self.gallery_seconds, self.capture_seconds, self.review_seconds,
                  self.final_preview_seconds, self.warning_seconds)
        if any(type(v) is not int or v < 1 for v in values):
            raise ValueError('Private inactivity limits must be positive integers')
        if self.warning_seconds >= min(values[:-1]):
            raise ValueError('Warning must precede each phase timeout')

    def decision(self, phase, elapsed, *, worker_busy=False, countdown_active=False):
        if (type(elapsed) not in (int, float) or not math.isfinite(elapsed)
                or type(worker_busy) is not bool or type(countdown_active) is not bool):
            raise ValueError('Valid true-inactivity observation required')
        limits = {'templates': self.gallery_seconds, 'confirm': self.gallery_seconds,
                  'capture': self.capture_seconds, 'review': self.review_seconds,
                  'result': self.review_seconds, 'final_preview': self.final_preview_seconds}
        if phase not in limits:
            return 'NONE'
        if worker_busy or countdown_active:
            return 'ACTIVE_WORK'
        if elapsed >= limits[phase]:
            return 'EXPIRED'
        if elapsed >= limits[phase]-self.warning_seconds:
            return 'WARNING'
        return 'NONE'
