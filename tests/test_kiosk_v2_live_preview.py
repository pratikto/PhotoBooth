"""Bounded preview preparation and stale-frame guards without OpenCV/Kivy."""

import threading
import time
import unittest
from unittest.mock import Mock

from photobooth.kiosk_v2.live_preview import LivePreview
from photobooth.kiosk_v2.performance import PerformanceLog


def wait_for(predicate):
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        if predicate():
            return
        threading.Event().wait(.005)
    raise AssertionError('Preview worker timed out')


class LivePreviewTests(unittest.TestCase):
    def test_slow_conversion_never_blocks_submit_and_only_latest_pending_frame_runs(self):
        entered, release = threading.Event(), threading.Event()
        first, skipped, latest = object(), object(), object()
        seen = []
        def prepare(frame):
            seen.append(frame)
            if frame is first:
                entered.set(); release.wait(2)
            return (1, 1), b'RGB'
        view = LivePreview(prepare)
        try:
            started = time.monotonic();view.submit(first, 1)
            self.assertLess(time.monotonic()-started, .1)
            self.assertTrue(entered.wait(1))
            view.submit(skipped, 1);view.submit(latest, 2)
            self.assertIsNone(view.read(2))
            release.set();wait_for(lambda: view.read(2) is not None)
            self.assertEqual(seen, [first, latest])
            self.assertIsNone(view.read(1))
            self.assertEqual(view.read(2).pixels, b'RGB')
        finally:
            release.set();view.close()

    def test_frozen_camera_does_not_renew_age_and_pause_invalidates_queued_pixels(self):
        now = [100.0]
        prepare = Mock(return_value=((1, 1), b'RGB'))
        view = LivePreview(prepare, clock=lambda: now[0])
        frame = object()
        try:
            view.submit(frame, 1);wait_for(lambda: view.read(1) is not None)
            now[0] += 1
            view.submit(frame, 1)
            self.assertIsNone(view.read(1));prepare.assert_called_once_with(frame)
            view.pause();self.assertIsNone(view.read(1))
            view.submit(object(), 2);wait_for(lambda: view.read(2) is not None)
            view.submit(None, 2);self.assertIsNone(view.read(2))
        finally:view.close()

    def test_close_discards_late_conversion_and_failure_can_recover_on_a_new_frame(self):
        prepare = Mock(side_effect=[ValueError('bad image'), ((1, 1), b'RGB')])
        view = LivePreview(prepare)
        view.submit(object(), 1)
        wait_for(lambda: prepare.call_count == 1)
        self.assertIsNone(view.read(1))
        view.submit(object(), 1);wait_for(lambda: view.read(1) is not None)
        view.close();view.close()
        view.submit(object(), 1)
        self.assertIsNone(view.read(1));self.assertEqual(prepare.call_count, 2)

    def test_performance_log_reports_aggregates_without_pixels_and_resets_between_pages(self):
        from unittest.mock import patch
        now = [0.0]
        meter = PerformanceLog(clock=lambda: now[0], interval=10)
        with patch('photobooth.kiosk_v2.performance.LOG.info') as log:
            frame, preview = object(), object()
            meter.observe('capture', .033, frame, preview)
            now[0] = 1
            meter.observe('capture', .033, frame, preview)
            meter.upload(.004)
            now[0] = 10
            meter.observe('capture', .1, object(), object())
            self.assertEqual(log.call_count, 1)
            args = log.call_args.args
            self.assertEqual(args[1], 'capture')
            self.assertEqual(args[4:6], (.2, .2))
            self.assertEqual(args[-1], 4)
            self.assertNotIn(frame, args);self.assertNotIn(preview, args)


if __name__ == '__main__':
    unittest.main()
