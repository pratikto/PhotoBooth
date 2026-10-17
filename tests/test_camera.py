"""Prove a blocked native camera read cannot block GUI reads of the mailbox."""
import threading
import time
import unittest
from unittest.mock import patch
import numpy as np
from photobooth.camera import Camera


class CameraThreadTests(unittest.TestCase):
    def test_blocked_acquisition_does_not_block_preview_and_releases_once(self):
        frame = np.zeros((10, 12, 3), dtype=np.uint8)
        blocked = threading.Event()
        unblock = threading.Event()
        class Device:
            def __init__(self):
                self.reads = 0
                self.releases = 0
            def isOpened(self):
                return True
            def set(self, *args):
                return False
            def read(self):
                self.reads += 1
                if self.reads > 1:
                    blocked.set()
                    unblock.wait(3)
                return True, frame
            def release(self):
                self.releases += 1
        device = Device()
        with patch('photobooth.camera.cv2.VideoCapture', return_value=device):
            camera = Camera()
            self.assertTrue(camera.open())
            try:
                self.assertTrue(blocked.wait(1))
                start = time.monotonic()
                self.assertIs(camera.read(), frame)
                self.assertLess(time.monotonic() - start, 0.1)
                with camera._lock:
                    camera._latest_time -= 2
                self.assertIsNone(camera.read())
            finally:
                unblock.set()
                camera.close()
            self.assertFalse(camera._thread.is_alive())
            self.assertEqual(device.releases, 1)
