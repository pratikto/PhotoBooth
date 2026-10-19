"""Palm timing, nonblocking inference, model caching, and optional native checks.

Normal tests use deterministic observations or a deliberately blocked detector.
Set PHOTOBOOTH_PALM_TEST_ASSETS to a local directory containing the public model
and MediaPipe sample images to run the native inference check as well. Tests do
not fetch models, open a webcam, or contact a Drive/payment service.
"""

import hashlib
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from photobooth.palm_gesture import (
    PALM_CONFIDENCE, MediaPipePalmDetector, PalmGestureWorker,
    PalmHoldTrigger, ensure_gesture_model,
)


class PalmHoldTests(unittest.TestCase):
    def test_one_hold_one_photo_then_confirmed_release_is_required(self):
        gate = PalmHoldTrigger()
        results = [gate.observe(True, t) for t in (0, .2, .4, .6, .8, 1.01, 1.2, 1.4)]
        self.assertEqual(sum(results), 1)
        self.assertTrue(gate.needs_release)
        for t in (1.6, 1.8, 2.01):
            self.assertFalse(gate.observe(False, t))
        self.assertFalse(gate.needs_release)
        results = [gate.observe(True, t) for t in (2.2, 2.4, 2.6, 2.8, 3, 3.21)]
        self.assertEqual(sum(results), 1)

    def test_a_brief_palm_or_broken_stream_cannot_accumulate_a_hold(self):
        gate = PalmHoldTrigger()
        for t in (0, .2, .4):
            self.assertFalse(gate.observe(True, t))
        self.assertFalse(gate.observe(False, .6))
        self.assertEqual(gate.progress, 0)
        for t in (.8, 1, 1.2):
            self.assertFalse(gate.observe(True, t))
        self.assertFalse(gate.observe(True, 2))  # A missing interval restarts the hold.
        self.assertEqual(gate.progress, 0)
        gate.expire(2.5)
        self.assertEqual(gate.progress, 0)
        self.assertIsNone(gate.last_sample_at)

    def test_duplicates_backwards_and_invalid_timestamps_are_not_observations(self):
        gate = PalmHoldTrigger()
        gate.observe(True, 3)
        for t in (3, 2, float('nan'), float('inf')):
            self.assertFalse(gate.observe(True, t))
        self.assertEqual(gate.progress, 0)
        self.assertEqual(gate.last_sample_at, 3)

    def test_manual_shutter_and_pauses_keep_release_latch_without_carrying_a_hold(self):
        gate = PalmHoldTrigger()
        gate.observe(True, 1)
        gate.observe(True, 1.2)
        gate.latch()  # A simultaneous button click wins the same countdown gate.
        gate.pause()
        self.assertTrue(gate.needs_release)
        for t in (2, 2.2, 2.4, 2.6, 2.8, 3.01):
            self.assertFalse(gate.observe(True, t))
        self.assertTrue(gate.needs_release)
        gate.observe(False, 3.2)
        gate.pause()  # A disconnect is not a confirmed hand release.
        gate.observe(False, 4)
        self.assertTrue(gate.needs_release)

    def test_countdown_can_observe_release_but_never_build_the_next_hold(self):
        gate = PalmHoldTrigger()
        gate.latch()
        for t in (0, .2, .41):
            self.assertFalse(gate.observe(False, t, allow_trigger=False))
        self.assertFalse(gate.needs_release)
        for t in (.6, .8, 1, 1.2, 1.4, 1.61):
            self.assertFalse(gate.observe(True, t, allow_trigger=False))
        self.assertEqual(gate.progress, 0)
        self.assertFalse(gate.observe(True, 1.8))
        self.assertEqual(gate.progress, 0)


class PalmWorkerTests(unittest.TestCase):
    def wait_for(self, condition):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            value = condition()
            if value:
                return value
            time.sleep(.005)
        self.fail('Palm worker did not complete within the test deadline.')

    def test_blocked_inference_does_not_block_gui_and_only_latest_page_frame_runs(self):
        started, unblock = threading.Event(), threading.Event()
        calls, closed_on = [], []

        class Detector:
            def detect(self, frame, _timestamp):
                calls.append(int(frame[0, 0, 0]))
                if len(calls) == 1:
                    started.set()
                    unblock.wait(2)
                return .95
            def close(self):
                closed_on.append(threading.current_thread().name)

        worker = PalmGestureWorker('unused.task', detector_factory=Detector)
        worker.start()
        try:
            self.wait_for(lambda: worker.state == 'ready')
            worker.submit(np.full((2, 2, 3), 1, dtype=np.uint8), 1)
            self.assertTrue(started.wait(1))
            start = time.monotonic()
            for number in (2, 3, 4):
                worker.submit(np.full((2, 2, 3), number, dtype=np.uint8), 2)
            self.assertIsNone(worker.poll())
            self.assertLess(time.monotonic() - start, .1)
            unblock.set()
            result = self.wait_for(worker.poll)
            self.assertEqual(result.context, 2)
            self.assertEqual(calls, [1, 4])
            self.assertIsNone(worker.poll())  # A result can be consumed only once.
        finally:
            unblock.set()
            worker.close()
        self.assertEqual(closed_on, ['photobooth-palm'])

    def test_pausing_then_resuming_same_page_rejects_the_inflight_old_result(self):
        started, unblock = threading.Event(), threading.Event()
        next_started, next_unblock = threading.Event(), threading.Event()

        class Detector:
            def detect(self, frame, _timestamp):
                if frame[0, 0, 0] == 1:
                    started.set()
                    unblock.wait(2)
                    return .95
                next_started.set()
                next_unblock.wait(2)
                return .85
            def close(self):
                pass

        worker = PalmGestureWorker('unused.task', detector_factory=Detector)
        worker.start()
        try:
            self.wait_for(lambda: worker.state == 'ready')
            worker.submit(np.full((2, 2, 3), 1, dtype=np.uint8), 5)
            self.assertTrue(started.wait(1))
            worker.pause()
            # The visible capture page can stay the same during frame loss.
            worker.submit(np.full((2, 2, 3), 2, dtype=np.uint8), 5)
            unblock.set()
            self.assertTrue(next_started.wait(1))  # Previous publication has finished.
            self.assertIsNone(worker.poll())
            next_unblock.set()
            self.assertEqual(self.wait_for(worker.poll).score, .85)
        finally:
            unblock.set()
            next_unblock.set()
            worker.close()

    def test_repeated_polling_of_one_camera_array_cannot_fabricate_new_frames(self):
        calls, repeated = [], threading.Event()

        class Detector:
            def detect(self, _frame, _timestamp):
                calls.append(1)
                if len(calls) > 1:
                    repeated.set()
                return .95
            def close(self):
                pass

        worker = PalmGestureWorker('unused.task', detector_factory=Detector)
        worker.start()
        try:
            self.wait_for(lambda: worker.state == 'ready')
            frame = np.zeros((2, 2, 3), dtype=np.uint8)
            worker.submit(frame, 1)
            self.wait_for(worker.poll)
            for _ in range(10):
                worker.submit(frame, 1)
            self.assertFalse(repeated.wait(.2))
            self.assertIsNone(worker.poll())
        finally:
            worker.close()

    def test_missing_or_broken_native_detector_is_an_optional_input_failure(self):
        for error in (ImportError('fixture missing package'), RuntimeError('fixture native failure')):
            with self.subTest(error=type(error).__name__):
                worker = PalmGestureWorker('unused.task', detector_factory=MagicMock(side_effect=error))
                with self.assertLogs('photobooth.palm_gesture', level='WARNING'):
                    worker.start()
                    self.wait_for(lambda: worker.state == 'unavailable')
                worker.submit(np.zeros((2, 2, 3), dtype=np.uint8), 1)
                self.assertIsNone(worker.poll())
                worker.close()
                self.assertEqual(worker.state, 'closed')


class PalmModelCacheTests(unittest.TestCase):
    def test_verified_cache_works_offline_without_requesting_a_model(self):
        data = b'fixture model'
        with tempfile.TemporaryDirectory() as directory, \
                patch('photobooth.palm_gesture.MODEL_BYTES', len(data)), \
                patch('photobooth.palm_gesture.MODEL_SHA256', hashlib.sha256(data).hexdigest()), \
                patch('photobooth.palm_gesture.requests.get') as request:
            path = Path(directory) / 'model.task'
            path.write_bytes(data)
            self.assertEqual(ensure_gesture_model(path), path)
            request.assert_not_called()

    def test_download_integrity_and_atomic_cache_publication(self):
        good = b'fixture model'
        for downloaded in (good, good[:-1], b'wrong model!!', good + b'extra'):
            with self.subTest(data=downloaded), tempfile.TemporaryDirectory() as directory, \
                    patch('photobooth.palm_gesture.MODEL_BYTES', len(good)), \
                    patch('photobooth.palm_gesture.MODEL_SHA256', hashlib.sha256(good).hexdigest()), \
                    patch('photobooth.palm_gesture.requests.get') as request:
                response = request.return_value.__enter__.return_value
                response.iter_content.return_value = [downloaded[:3], downloaded[3:]]
                path = Path(directory) / 'model.task'
                path.write_bytes(b'previous invalid model')
                if downloaded == good:
                    ensure_gesture_model(path)
                    self.assertEqual(path.read_bytes(), good)
                else:
                    with self.assertRaises(ValueError):
                        ensure_gesture_model(path)
                    self.assertEqual(path.read_bytes(), b'previous invalid model')
                self.assertEqual(list(path.parent.glob('*.part')), [])

    def test_cancelled_setup_does_not_start_a_network_request(self):
        stop = threading.Event()
        stop.set()
        with tempfile.TemporaryDirectory() as directory, \
                patch('photobooth.palm_gesture.requests.get') as request:
            with self.assertRaises(RuntimeError):
                ensure_gesture_model(Path(directory) / 'model.task', stop)
            request.assert_not_called()


@unittest.skipUnless(os.environ.get('PHOTOBOOTH_PALM_TEST_ASSETS'), 'Native model assets are opt-in')
class NativePalmModelTests(unittest.TestCase):
    def test_actual_model_accepts_a_palm_and_rejects_other_gestures_and_empty_image(self):
        root = Path(os.environ['PHOTOBOOTH_PALM_TEST_ASSETS'])
        scores = {}
        # Unrelated still images must not inherit the previous hand's tracking
        # ROI. A fresh VIDEO recognizer per fixture tests the actual adapter.
        for name in ('left_hands.jpg', 'fist.jpg', 'thumb_up.jpg', 'pointing_up.jpg', 'blank'):
            frame = (np.zeros((360, 480, 3), dtype=np.uint8) if name == 'blank'
                     else cv2.imread(str(root / name)))
            self.assertIsNotNone(frame)
            original = frame.copy()
            detector = MediaPipePalmDetector(root / 'gesture_recognizer.task')
            try:
                scores[name] = detector.detect(frame, time.monotonic())
            finally:
                detector.close()
            self.assertTrue(np.array_equal(frame, original))
        self.assertGreaterEqual(scores.pop('left_hands.jpg'), PALM_CONFIDENCE)
        for name, score in scores.items():
            with self.subTest(image=name):
                self.assertLess(score, PALM_CONFIDENCE)


if __name__ == '__main__':
    unittest.main()
