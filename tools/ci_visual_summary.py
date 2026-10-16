"""Print compact synthetic GUI contact sheets for remote visual inspection.

This helper reads only the output directory of tools/render_gui.py. It never
opens a real camera, customer folder, settings file, or account credential.
CI keeps the full-resolution PNGs as its normal downloadable artifact. The
small JPEGs in the job log let a reviewer inspect layout even when the local
desktop runtime is unavailable.
"""

import base64
import io
from pathlib import Path
import sys

from PIL import Image


def main():
    directory = Path(sys.argv[1])
    for size in ("1200x800", "800x600"):
        path = directory / f"overview-{size}.png"
        if not path.is_file():
            continue
        with Image.open(path) as source:
            preview = source.convert("RGB")
            preview.thumbnail((1100, 1100))
            stream = io.BytesIO()
            preview.save(stream, "JPEG", quality=76)
        print(f"MEONG_VISUAL_{size}:" + base64.b64encode(stream.getvalue()).decode("ascii"))


if __name__ == "__main__":
    main()
