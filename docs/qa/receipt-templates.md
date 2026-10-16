# Approved receipt templates in the Kivy workflow

The application now loads the twelve approved revision-3 80 mm designs instead
of four illustrative cards. Each session's selected template determines its
three aspect-preserving crops, explicit masks, and QR footer. The same rendered
frame pixels appear during review and in the saved result, including retakes.

The master geometry is 640 × 1920 pixels at 203.2 dpi, or 80 × 240 mm. The original
eight-dot paper margins are retained. The complete QR placeholder is replaced,
using an integer dot size per module within its 384-dot/48 mm allocation. The
approved full logo is centered and monochrome in this receipt QR.

![All twelve approved designs with synthetic photo fixtures](receipt-templates.png)

![Actual template picker](receipt-gallery-1200x800.png)

![Actual result screen](receipt-result-1200x800.png)

![Read-only, scrollable detail viewer](receipt-detail-1200x800.png)

## Validation

- Full Python suite with GUI checks enabled: **100 passed, 2 skipped**; 122 subtests passed. The two native gesture-model checks require optional test assets and remain skipped.
- Real Kivy screenshot renderer: **48 renders passed** at 1200 × 800 and 800 × 600. [Machine-readable report](receipt-report.json).
- All twelve saved PNGs decode to the exact synthetic Drive-folder URL. QR checks use the final PNG pixels, not just encoder metadata.
- All 36 photo windows contain the intended photo in the correct position. Pixels outside their explicit clip masks retain the original paper, borders, and ornaments. All four paper margins are unchanged.
- Landscape, portrait, square, and EXIF-rotated images preserve their aspect ratio and source bytes. All twelve previews are distinct and independent of their cached originals.
- The real controller is driven through heart selection, capture, a third-photo retake, saving, advancing to an arcade session, and completion. Review uses each session's own apertures. Retake initially waits for its shutter.
- The new result viewer was additionally checked after its final styling change: full-resolution texture, proportional vertical scrolling, source bytes unchanged, and automatic dismissal when the result page retires.
- The command-line compositor was exercised with three fixture files and the arcade template. `git diff --check` passed.

Repeat the suite and screenshots from the repository root using the application's
environment. Offscreen SDL is for this Linux validation environment:

```bash
PHOTOBOOTH_TEST_GUI=1 SDL_VIDEODRIVER=offscreen KIVY_NO_ARGS=1 python -m pytest -q
SDL_VIDEODRIVER=offscreen KIVY_NO_ARGS=1 python tools/render_gui.py --output-dir /tmp/receipt-gui
```

Photo fixtures are geometric illustrations. Folder URLs are test fixtures; no
real customer photos, Google credentials, uploads, QRIS charges, or printer jobs
were used. Physical printable width, thermal photo dithering, printer transport,
and phone-camera scanning on an actual paper print need device testing.
