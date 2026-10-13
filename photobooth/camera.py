import sys

import cv2


class Camera:
    """Membuka kamera dan menyediakan frame terbaru."""

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.capture = None

    def open(self):
        """Buka kamera. Kembalikan True jika berhasil."""
        self.close()

        if sys.platform.startswith("win"):
            # DirectShow sering membantu pada webcam Windows.
            self.capture = cv2.VideoCapture(
                self.camera_index,
                cv2.CAP_DSHOW,
            )

            # Jika DirectShow gagal, coba backend default OpenCV.
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
        """Baca satu frame. Kembalikan None jika frame gagal dibaca."""
        if self.capture is None or not self.capture.isOpened():
            return None

        success, frame = self.capture.read()

        if not success:
            return None

        return frame

    def close(self):
        """Lepaskan kamera ketika aplikasi ditutup."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
