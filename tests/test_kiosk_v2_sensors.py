"""Deferred native imports and optional input routing without native packages."""

import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from photobooth.kiosk_v2.sensors import DeferredDetector, DetectorParts, PalmShutter


def wait_for(predicate):
    end = time.monotonic() + 2
    while time.monotonic() < end:
        if predicate(): return
        threading.Event().wait(.005)
    raise AssertionError('Detector initialization timed out')


class DeferredDetectorTests(unittest.TestCase):
    def test_slow_initialization_never_blocks_and_late_worker_is_closed(self):
        entered, release = threading.Event(), threading.Event()
        worker = Mock()
        def factory():
            entered.set();release.wait(2);return DetectorParts(worker, Mock())
        detector = DeferredDetector(factory)
        start = time.monotonic();detector.start();detector.start()
        self.assertLess(time.monotonic()-start, .1)
        self.assertTrue(entered.wait(1))
        self.assertEqual(detector.state, 'loading')
        detector.close();release.set()
        wait_for(lambda: worker.close.call_count == 1)
        worker.start.assert_not_called()
        self.assertIsNone(detector.parts)
        self.assertEqual(detector.state, 'closed')

    def test_missing_optional_dependency_is_unavailable_without_repeated_retries(self):
        factory = Mock(side_effect=ImportError('optional provider unavailable'))
        detector = DeferredDetector(factory)
        detector.start();wait_for(lambda: detector.state == 'unavailable')
        detector.start();factory.assert_called_once_with()
        self.assertIsNone(detector.parts);detector.close()
        disabled = DeferredDetector(factory, enabled=False)
        disabled.start();self.assertEqual(disabled.state, 'disabled')
        factory.assert_called_once_with()


class PalmShutterAdapterTests(unittest.TestCase):
    def setUp(self):
        self.worker, self.trigger = Mock(), Mock()
        self.worker.state = 'ready'
        self.worker.poll.return_value = None
        self.parts = DetectorParts(self.worker, self.trigger, .6, .5)
        self.palm = PalmShutter(parts=self.parts)
        self.addCleanup(self.palm.close)

    def test_only_fresh_same_page_palm_uses_existing_hold_and_countdown_gate(self):
        for revision,stamp in ((2,100),(3,99),(3,101)):
            self.worker.poll.return_value = SimpleNamespace(context=revision,captured_at=stamp,score=1)
            self.assertFalse(self.palm.update(object(),3,active=True,can_trigger=True,now=100))
        self.trigger.observe.assert_not_called()
        self.worker.poll.return_value = SimpleNamespace(context=3,captured_at=99.8,score=.8)
        self.trigger.observe.return_value = True
        self.assertFalse(self.palm.update(object(),3,active=True,can_trigger=False,now=100))
        self.trigger.observe.assert_called_once_with(True,99.8,allow_trigger=False)
        self.trigger.expire.assert_called_with(99.5)
        self.assertTrue(self.palm.update(object(),3,active=True,can_trigger=True,now=100))

    def test_button_latches_and_other_pages_or_missing_frames_invalidate_old_holds(self):
        self.palm.latch();self.trigger.latch.assert_called_once_with()
        self.worker.pause.assert_called_once_with()
        self.assertFalse(self.palm.update(object(),1,active=False,can_trigger=True))
        self.assertFalse(self.palm.update(None,1,active=True,can_trigger=True))
        self.worker.submit.assert_not_called()
        self.assertEqual(self.trigger.pause.call_count,2)
        self.palm.close()
        self.assertFalse(self.palm.update(object(),1,active=True,can_trigger=True))

    def test_submission_is_bounded_but_polling_keeps_results_responsive(self):
        for stamp in (10,10.03,10.06,10.1,10.16):
            self.palm.update(object(),1,active=True,can_trigger=True,now=stamp)
        self.assertEqual(self.worker.submit.call_count,2)
        self.assertEqual(self.worker.poll.call_count,5)


if __name__ == '__main__': unittest.main()
