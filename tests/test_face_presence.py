"""Offline playlist schedules, exposure accounting and deliberate face holds."""

from datetime import datetime
import json
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

import numpy as np
from PIL import Image

from photobooth.face_presence import FacePresenceTrigger, OpenCVFaceDetector


class FacePresenceTests(unittest.TestCase):
    def test_v2_adapter_preserves_face_hold_with_accepted_inference_delay(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from photobooth.kiosk_v2.devices import FaceInviter
        worker = Mock()
        trigger = FacePresenceTrigger()
        inviter = FaceInviter(worker=worker, trigger=trigger)
        fires = []
        try:
            for index in range(11):
                stamp = index * .6
                worker.poll.return_value = SimpleNamespace(context=7,captured_at=stamp,score=1)
                if inviter.update(object(),7,allowed=True,now=stamp+.3):fires.append(stamp)
            self.assertEqual(len(fires),1)
            self.assertGreaterEqual(fires[0],5)
            worker.poll.return_value = None
            inviter.update(object(),7,allowed=True,now=20)
            self.assertEqual(inviter.progress,0)
        finally:inviter.close()

    def test_face_requires_five_seconds_and_rearms_only_after_absence_or_cooldown(self):
        trigger = FacePresenceTrigger()
        fired = [t for t in np.arange(0, 7, .2) if trigger.observe(True, float(t))]
        self.assertEqual(len(fired), 1)
        self.assertGreaterEqual(fired[0], 5)
        self.assertFalse(trigger.observe(True, fired[0]))  # Duplicate result.
        for t in np.arange(7, 10, .2):
            self.assertFalse(trigger.observe(False, float(t)))
        fired_again = [t for t in np.arange(10, 16, .2) if trigger.observe(True, float(t))]
        self.assertEqual(len(fired_again), 1)
        self.assertGreaterEqual(fired_again[0], 15)

    def test_short_misses_are_tolerated_but_camera_gaps_and_page_changes_reset_a_hold(self):
        trigger = FacePresenceTrigger()
        for t in np.arange(0, 4, .2):
            self.assertFalse(trigger.observe(True, float(t)))
        self.assertFalse(trigger.observe(False, 4.0))
        self.assertFalse(trigger.observe(True, 4.2))
        fired = [t for t in np.arange(4.4, 5.5, .2) if trigger.observe(True, float(t))]
        self.assertEqual(len(fired), 1)
        trigger = FacePresenceTrigger()
        for t in np.arange(0, 4.5, .2):
            trigger.observe(True, float(t))
        self.assertFalse(trigger.observe(True, 6))  # Missing inference interval.
        trigger.pause()
        self.assertFalse(trigger.observe(True, 10))
        self.assertEqual(trigger.progress, 0)

    def test_bundled_opencv_detector_loads_offline_and_rejects_an_empty_scene(self):
        detector = OpenCVFaceDetector()
        try:
            self.assertEqual(detector.detect(np.zeros((240, 320, 3), dtype=np.uint8), 0), 0)
        finally:
            detector.close()


if __name__ == '__main__':
    unittest.main()
