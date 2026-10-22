"""Warm CPU strip previews without doing Pillow work on a button callback.

Only the GUI thread creates/uploads Kivy textures. Worker results are detached
RGB previews of the existing approved masters; no customer images or services.
"""

from concurrent.futures import ThreadPoolExecutor
import logging

LOG = logging.getLogger(__name__)
PREVIEW_SIZE = (320, 960)


def render_preview(template):
    # Lazy import keeps the injected-worker tests independent of Pillow/Kivy.
    from photobooth.catalog import create_template_preview
    return create_template_preview(template, PREVIEW_SIZE).convert('RGB')


class PreviewPreloader:
    def __init__(self, templates, *, renderer=render_preview):
        self.templates = tuple(templates)
        self.renderer = renderer
        self._executor = None
        self._futures = {}
        self._closed = False

    def start(self):
        if self._closed or self._executor is not None or not self.templates:
            return
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='meong-preview')
        # First gallery needs the selected strip and both neighbours first.
        order = (self.templates[0], *self.templates[-1:], *self.templates[1:-1])
        for template in order:
            self._futures[template.template_id] = self._executor.submit(self.renderer, template)

    def get(self, template):
        """Return a ready CPU image, never wait for an unfinished worker."""
        future = self._futures.get(template.template_id)
        if future is None or not future.done() or future.cancelled():
            return None
        try:
            return future.result()
        except Exception:
            LOG.warning('Preview warmup failed: %s', template.template_id, exc_info=True)
            self._futures.pop(template.template_id, None)
            return None

    def close(self):
        self._closed = True
        if self._executor is not None:
            # Current local decode may finish; queued work is cancelled and no
            # callback can subsequently touch a retired Kivy widget or texture.
            self._executor.shutdown(wait=False, cancel_futures=True)
        self._futures.clear()
