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
