"""CPU warmup/cancellation tests; no Kivy, Pillow or native device required."""

from threading import Event, current_thread
from types import SimpleNamespace
import unittest

from photobooth.kiosk_v2.previews import PreviewPreloader


class PreviewPreloaderTests(unittest.TestCase):
    def setUp(self):
        self.templates = tuple(SimpleNamespace(template_id=str(i)) for i in range(4))

    def test_pending_decode_does_not_block_gui_and_close_cancels_queued_assets(self):
        started, release = Event(), Event()
        worker_threads = []

        def render(template):
            worker_threads.append(current_thread())
            started.set()
            release.wait(2)
            return template.template_id

        cache = PreviewPreloader(self.templates, renderer=render)
        try:
            cache.start()
            self.assertTrue(started.wait(2))
            self.assertIsNone(cache.get(self.templates[0]))
            self.assertIsNot(worker_threads[0], current_thread())
            futures = list(cache._futures.values())
            cache.close()
            self.assertTrue(all(f.cancelled() for f in futures[1:]))
            self.assertIsNone(cache.get(self.templates[0]))
            cache.start()  # Retired owner cannot start a replacement worker.
            self.assertFalse(cache._futures)
        finally:
            release.set()
            cache.close()

    def test_ready_detached_preview_is_reused_and_first_gallery_has_priority(self):
        order = []

        def render(template):
            order.append(template.template_id)
            return object()

        cache = PreviewPreloader(self.templates, renderer=render)
        try:
            cache.start()
            cache.start()  # Duplicate warmup must not decode twice.
            results = {key: future.result(timeout=2) for key, future in cache._futures.items()}
            self.assertEqual(order, ['0', '3', '1', '2'])
            for template in self.templates:
                self.assertIs(cache.get(template), results[template.template_id])
        finally:
            cache.close()

    def test_decoder_failure_returns_cache_miss_for_existing_synchronous_fallback(self):
        def broken(_template):
            raise ValueError('invalid local artwork')

        cache = PreviewPreloader(self.templates[:1], renderer=broken)
        try:
            cache.start()
            with self.assertRaises(ValueError):
                next(iter(cache._futures.values())).result(timeout=2)
            self.assertIsNone(cache.get(self.templates[0]))
        finally:
            cache.close()


if __name__ == '__main__':
    unittest.main()
