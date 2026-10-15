# PhotoBooth source file
# Small local helper for saving a frame as a JPEG.

from datetime import datetime
from pathlib import Path

import cv2


PHOTO_FOLDER = Path(__file__).resolve().parent.parent / "photos"


def save_photo(frame):
    # Save a camera frame as a JPEG in the simple local-photo workflow and return the path that was
    # written.
    """Save a frame as a JPG and return the file path."""
    PHOTO_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    photo_path = PHOTO_FOLDER / f"photo_{timestamp}.jpg"

    if cv2.imwrite(str(photo_path), frame):
        return photo_path

    return None
