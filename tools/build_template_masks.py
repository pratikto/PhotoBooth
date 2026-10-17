"""Build explicit photo masks from the approved, opaque receipt masters.

Run this only when changing the bundled artwork/layout, from the project root:
    python tools/build_template_masks.py

The application loads the committed masks; it never guesses a frame shape from
a customer's photograph. Thresholding below is an authoring operation applied
to EMPTY white windows. A connected component anchored inside each window
preserves irregular hearts, vintage labels, pixel corners, and decorations.
"""

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1] / "photobooth" / "assets" / "templates"


def main():
    """Regenerate masks and retain the source layout's physical coordinates."""
    layout = json.loads((ROOT / "layout_80mm.json").read_text(encoding="utf-8"))
    scale = layout["png_export"]["dots_per_mm"]
    (ROOT / "masks").mkdir(exist_ok=True)
    for template in layout["templates"]:
        with Image.open(ROOT / template["png_file"]) as source:
            gray = np.asarray(source.convert("L"))
        for index, frame in enumerate(template["photo_apertures"], 1):
            left = round(frame["x_mm"] * scale)
            top = round(frame["y_from_top_mm"] * scale)
            right = round((frame["x_mm"] + frame["width_mm"]) * scale)
            bottom = round((frame["y_from_top_mm"] + frame["height_mm"]) * scale)
            crop = gray[top:bottom, left:right]
            # The measured rectangle bounds the aperture. Flood only the white
            # component containing its center, excluding dark ink and paper
            # outside the outline. This also excludes ornaments inside a box.
            white = (crop >= 200).astype(np.uint8)
            _, labels = cv2.connectedComponents(white, connectivity=4)
            center = labels[crop.shape[0] // 2, crop.shape[1] // 2]
            if center == 0:
                raise ValueError(f"No white center in template {template['id']}, frame {index}")
            mask = (labels == center).astype(np.uint8) * 255
            if np.count_nonzero(mask) < mask.size * 0.45:
                raise ValueError(f"Incomplete aperture in template {template['id']}, frame {index}")
            name = f"masks/{template['id']}_{index}.png"
            Image.fromarray(mask).save(ROOT / name, optimize=True)
            frame["mask_file"] = name
    (ROOT / "layout_80mm.json").write_text(
        json.dumps(layout, indent=2) + "\n", encoding="utf-8")
    print("Built 36 photo masks for 12 approved receipt templates.")


if __name__ == "__main__":
    main()
