"""One logo source for the header, tutorial and every transaction-folder QR.

Install the approved bright-trail PNG as assets/meong_photobooth_vivid.png, or
point PHOTOBOOTH_LOGO_PATH at the same local artwork. This is a local path only:
customer kiosks must not depend on an authenticated ChatGPT image URL.

The earlier bundled full logo remains available when the preferred file has
not been installed yet. No programmatic recoloring or substitute mascot is
used. Both callers import this module so a future asset replacement cannot
update the header while accidentally leaving the QR on an older logo.
"""

from functools import lru_cache
import os
from pathlib import Path

from PIL import Image, ImageChops


ASSETS = Path(__file__).resolve().parent / "assets"
PREFERRED_LOGO_PATH = ASSETS / "meong_photobooth_vivid.png"
BUNDLED_LOGO_PATH = ASSETS / "meong_photobooth.png"
LOGO_PATH = Path(os.environ["PHOTOBOOTH_LOGO_PATH"]).expanduser().resolve() if (
    os.environ.get("PHOTOBOOTH_LOGO_PATH")) else (
    PREFERRED_LOGO_PATH if PREFERRED_LOGO_PATH.is_file() else BUNDLED_LOGO_PATH)


@lru_cache(maxsize=1)
def load_logo():
    """Read the exact chosen PNG and composite transparency onto white paper.

    Remove empty surrounding white space for display, preserving the artwork's
    colors and proportions. The same crop is used in the QR's centered plate.
    Returning a copy at call sites protects this cached, read-only source.
    """
    with Image.open(LOGO_PATH) as source:
        rgba = source.convert("RGBA")
    paper = Image.new("RGBA", rgba.size, "white")
    logo = Image.alpha_composite(paper, rgba).convert("RGB")
    difference = ImageChops.difference(logo, Image.new("RGB", logo.size, "white"))
    bounds = difference.convert("L").point(lambda level: 255 if level > 24 else 0).getbbox()
    return logo.crop(bounds) if bounds else logo
