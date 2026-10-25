# Approved thermal receipt assets

**Scope — unchanged shared template masters used by v1 and v2.** Quantity
means copies from one session/design. The 640×1920 master canvas is separate
from the printer's configured raster width (commonly 576 dots); do not infer a
640-dot physical printer from the asset size. The QR rectangle is reserved for
a valid assigned folder destination when available; local-only v2 output does
not invent a working Drive QR. [Current v2 flow](../../../docs/portrait-kiosk-v2.md).

> **Release provenance:** Assets are in the source pre-release [v1.0.0](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0), from prior `feature/kivy-gui` work. Keep media/codecs, audio speaker response and printer/QR paper quality distinct from simulated CI; no change to asset bytes in this documentation cleanup.

> **V1 asset baseline (2026-10-19, `master` / immutable `v1.0.0`):** The current Kivy booth uses the twelve approved revision-3 80 mm receipt masters. **FEAT-001 DEMO:** one selected design equals one three-photo capture session; quantity is **identical paper copies** (Rp5.000 per template + Rp5.000 per requested copy). Thermal photo print is integrated in Kivy and defaults to the owner-selected Floyd preprocessing; these unmodified template PNGs are not already-printed output. Folder QR remains separate from DEMO payment QR.

These are the twelve approved revision-3 Meong masters: 80 × 240 mm, eight
dots/mm, 640 × 1920 pixels, with 1 mm paper margins and a 48 mm QR allocation.
The PNGs are the blank masters, not the dummy-QR proof images. Production replaces
the entire reserved QR rectangle with the real transaction-folder destination.

`layout_80mm.json` retains the source millimetre coordinates. Each photo entry
also points to a committed grayscale mask in `masks/`. A white mask pixel accepts
the photograph; a black pixel retains the original paper, border, or ornament.
Some windows differ by one pixel because physical edges are rounded once.

The application loads these masks directly. It does not detect frames at runtime
and does not change a customer's raw photographs. Pillow uses aspect-preserving
cover/crop and clips the result to the selected frame. Review and saved output
share those exact final frame pixels.

If changing an approved blank master or its photo coordinates, regenerate the
masks from the project root with `python tools/build_template_masks.py`, then
inspect every filled design and run `tests/test_templates.py`. The authoring
script flood-fills only the empty white aperture region containing its center;
it must never be run against a composition already containing customer photos.

The original first four template keys remain stable for stored manifest
compatibility. Existing output files are not migrated or rewritten.
