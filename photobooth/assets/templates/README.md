# Approved thermal receipt assets

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
