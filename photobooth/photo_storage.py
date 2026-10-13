from datetime import datetime
from pathlib import Path

import cv2


PHOTO_FOLDER = Path(__file__).resolve().parent.parent / "photos"


def save_photo(frame):
    """Simpan frame sebagai JPG dan kembalikan lokasi file."""
    PHOTO_FOLDER.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    photo_path = PHOTO_FOLDER / f"photo_{timestamp}.jpg"

    if cv2.imwrite(str(photo_path), frame):
        return photo_path

    return None
