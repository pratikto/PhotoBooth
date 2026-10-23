"""Small aggregate timings in the existing diagnostic log; no image data."""

import logging
import time

LOG = logging.getLogger(__name__)


class PerformanceLog:
    def __init__(self, *, clock=time.monotonic, interval=10):
        self._clock, self.interval = clock, interval
        self._start = clock()
        self._page = None
        self._ticks = self._frames = self._previews = 0
        self._max_gap = self._max_upload = 0
        self._last_frame = self._last_preview = None

    def observe(self, page, dt, frame, preview):
        if self._page != page:
            self.flush()
            self._page = page
        self._ticks += 1
        if self._ticks > 1:
            self._max_gap = max(self._max_gap, dt)
        if frame is not None and frame is not self._last_frame:
            self._frames += 1
            self._last_frame = frame
        if preview is not None and preview is not self._last_preview:
            self._previews += 1
            self._last_preview = preview
        if self._clock() - self._start >= self.interval:
            self.flush()

    def upload(self, seconds):
        self._max_upload = max(self._max_upload, seconds)

    def flush(self):
        seconds = self._clock() - self._start
        if self._page is not None and seconds >= .25 and self._ticks:
            LOG.info('Performance page=%s seconds=%.2f ui_ticks_s=%.1f new_frames_s=%.1f '
                     'preview_frames_s=%.1f max_tick_gap_ms=%.1f max_upload_ms=%.1f',
                     self._page, seconds, self._ticks / seconds, self._frames / seconds,
                     self._previews / seconds, self._max_gap * 1000, self._max_upload * 1000)
        self._start = self._clock()
        self._ticks = self._frames = self._previews = 0
        self._max_gap = self._max_upload = 0
        self._last_frame = self._last_preview = None
