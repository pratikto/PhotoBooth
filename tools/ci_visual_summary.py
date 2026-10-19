"""Print compact synthetic GUI contact sheets for remote visual inspection.

This helper reads only the output directory of tools/render_gui.py. It never
opens a real camera, customer folder, settings file, or account credential.
CI keeps the full-resolution PNGs as its normal downloadable artifact. The
small JPEGs in the job log let a reviewer inspect layout even when the local
desktop runtime is unavailable.
"""

import base64
import io
import json
from pathlib import Path
import sys

from PIL import Image


def main():
    directory = Path(sys.argv[1])
    report_path = directory / "report.json"
    report = json.loads(report_path.read_text()) if report_path.is_file() else {}
    print("MEONG_GUI_REPORT:" + json.dumps({
        "renders": len(report.get("renders", [])), "errors": report.get("errors", [])
    }))
    if report.get("errors"):
        # Preserve the failed frame for inspection rather than relying on an
        # overview that is only built after every render has passed.
        candidates = list(directory.glob("*.png"))
        if candidates:
            latest = max(candidates, key=lambda path: path.stat().st_mtime_ns)
            with Image.open(latest) as source:
                preview = source.convert("RGB")
                preview.thumbnail((1200, 900))
                stream = io.BytesIO()
                preview.save(stream, "JPEG", quality=80)
            print("MEONG_VISUAL_FAILURE:" + base64.b64encode(stream.getvalue()).decode("ascii"))
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
