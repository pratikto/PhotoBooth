"""Native Android inference; reuse v2's actual one-frame worker/hold/release guards."""
from pathlib import Path


class AndroidPalmDetector:
    def __init__(self, path, stop):
        from photobooth.palm_gesture import ensure_gesture_model
        from jnius import autoclass
        model = ensure_gesture_model(path, stop)
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        self.native = autoclass('id.meong.nativebridge.PalmBridge')(activity, str(model))

    def detect(self, frame, captured_at):
        from PIL import Image
        image = Image.fromarray(frame[:, :, ::-1].copy(), 'RGB')
        image.thumbnail((480,360))
        return self.native.detect(image.tobytes(), *image.size)

    def close(self):
        self.native.close()


def mobile_palm(root, *, enabled=True):
    from photobooth.palm_gesture import PalmGestureWorker, PalmHoldTrigger, PALM_CONFIDENCE, MAX_RESULT_AGE
    from .sensors import PalmShutter, DetectorParts
    model = Path(root)/'data/models/gesture_recognizer.task'
    worker = PalmGestureWorker(model, enabled=enabled,
        detector_factory=lambda:AndroidPalmDetector(model, worker._stop))
    return PalmShutter(enabled=enabled, parts=DetectorParts(worker,PalmHoldTrigger(),PALM_CONFIDENCE,MAX_RESULT_AGE))
