"""Camera ownership and stale face-observation guards without native devices."""

import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from photobooth.kiosk_v2.devices import AsyncCamera, FaceInviter


def wait_for(predicate):
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        if predicate():
            return
        threading.Event().wait(.005)
    raise AssertionError('Worker did not reach the expected state')


class CameraAdapterTests(unittest.TestCase):
    def test_slow_open_and_late_completion_do_not_block_gui_or_publish_after_close(self):
        entered, release = threading.Event(), threading.Event()
        service = Mock()
        def slow_open():
            entered.set(); release.wait(2); return True
        service.open.side_effect = slow_open
        service.read.return_value = object()
        factory = Mock(return_value=service)
        device = AsyncCamera(factory=factory)
        try:
            start = time.monotonic(); device.start(); device.start()
            self.assertLess(time.monotonic() - start, .2)
            self.assertTrue(entered.wait(1))
            self.assertIsNone(device.read())
            start = time.monotonic(); device.close()
            self.assertLess(time.monotonic() - start, .2)
            release.set()
            wait_for(lambda: device.state == 'closed')
            self.assertIsNone(device.read())
            factory.assert_called_once_with(0)
        finally:
            release.set(); device.close()

    def test_pause_discards_frames_and_resume_reuses_one_camera_service(self):
        service = Mock()
        service.open.return_value = True
        service.read.side_effect = lambda: object()
        factory = Mock(return_value=service)
        device = AsyncCamera(index=3, factory=factory)
        try:
            device.start();wait_for(lambda: device.read() is not None)
            device.set_active(False)
            self.assertIsNone(device.read())
            wait_for(lambda: service.close.call_count >= 1)
            device.set_active(True)
            wait_for(lambda: device.read() is not None)
            self.assertEqual(service.open.call_count, 2)
            factory.assert_called_once_with(3)
        finally:
            device.close()
            wait_for(lambda: device.state == 'closed')
            device.close()
            self.assertEqual(device.state, 'closed')

    def test_disconnect_reconnect_and_stale_frames_cannot_be_captured(self):
        now = [100.0]
        frame = object()
        service = Mock()
        service.open.return_value = True
        service.read.return_value = frame
        device = AsyncCamera(factory=lambda _: service, retry_seconds=.02, clock=lambda: now[0])
        try:
            device.start();wait_for(lambda: device.read() is frame)
            now[0] += 2
            self.assertIsNone(device.read())
            service.read.return_value = None
            wait_for(lambda: service.close.call_count > 0)
            fresh = object();service.read.return_value = fresh
            wait_for(lambda: device.read() is fresh)
            self.assertGreaterEqual(service.open.call_count, 2)
        finally:
            device.close()

    def test_disabled_or_failed_service_does_not_break_manual_app_entry(self):
        factory = Mock()
        disabled = AsyncCamera(enabled=False, factory=factory)
        disabled.start();self.assertIsNone(disabled.read());factory.assert_not_called();disabled.close()
        factory.side_effect = RuntimeError('camera unavailable')
        device = AsyncCamera(factory=factory, retry_seconds=10)
        try:
            device.start();wait_for(lambda: device.state == 'unavailable')
            self.assertIsNone(device.read())
            self.assertEqual(factory.call_count, 1)
        finally:
            device.close()


class FaceInvitationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.worker, self.trigger = Mock(), Mock()
        self.worker.poll.return_value = None
        self.inviter = FaceInviter(worker=self.worker, trigger=self.trigger)

    def test_only_fresh_same_revision_observations_reach_existing_hold_policy(self):
        for revision,stamp in ((2,100), (3,98), (3,101)):
            self.worker.poll.return_value = SimpleNamespace(context=revision,captured_at=stamp,score=1)
            self.assertFalse(self.inviter.update(object(),3,allowed=True,now=100))
        self.trigger.observe.assert_not_called()
        self.worker.poll.return_value = SimpleNamespace(context=3,captured_at=99.8,score=1)
        self.trigger.observe.return_value = True
        self.assertTrue(self.inviter.update(object(),3,allowed=True,now=100))
        self.trigger.observe.assert_called_once_with(True,99.8)

    def test_other_pages_missing_frames_and_close_invalidate_worker_and_partial_hold(self):
        self.assertFalse(self.inviter.update(object(),3,allowed=False))
        self.assertFalse(self.inviter.update(None,3,allowed=True))
        self.worker.submit.assert_not_called()
        self.assertEqual(self.worker.pause.call_count,2)
        self.assertEqual(self.trigger.pause.call_count,2)
        self.inviter.close()
        self.assertFalse(self.inviter.update(object(),3,allowed=True))
        self.worker.close.assert_called_once_with()

