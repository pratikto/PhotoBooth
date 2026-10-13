import sys

import cv2


class Camera:
    """Open a camera and provide its latest frame."""

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = None

    def open(self):
        """Open the camera. Return True if it is available."""
        self.close()

        if sys.platform.startswith("win"):
            # DirectShow can work well with webcams on Windows.
            self.capture = cv2.VideoCapture(
                self.camera_index,
                cv2.CAP_DSHOW,
            )

            # Fall back to OpenCV's default backend if DirectShow fails.
            if not self.capture.isOpened():
                self.capture.release()
                self.capture = cv2.VideoCapture(self.camera_index)
        else:
            self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            self.close()
            return False

        return True

    def read(self):
        """Read one frame. Return None if the frame cannot be read."""
        if self.capture is None or not self.capture.isOpened():
            return None

        success, frame = self.capture.read()

        if not success:
            return None

        return frame

    def close(self):
        """Release the camera when the application closes."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
