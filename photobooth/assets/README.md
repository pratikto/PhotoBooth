# Meong Photobooth brand asset

`meong_photobooth.png` is the approved full pixel-art logo: camera-cat mascot,
grayscale trail, and the exact wordmark **MEONG PHOTOBOOTH** without an S.
It is cropped from the approved artwork to remove excessive surrounding white
space; the original mascot, colors, trail, and lettering are retained.

The folder-QR helper loads this bundled asset relative to its Python module.
It uses the complete logo, rather than a head-only or mascot-only substitute.
GUI and saved digital results retain the accent colors. The helper's
`monochrome=True` option dithers only the inserted logo for thermal print tests.
Never blur, dither, or recolor the surrounding QR matrix.
