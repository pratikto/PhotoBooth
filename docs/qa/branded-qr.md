# Full-logo folder QR verification

> **Historical QA snapshot.** This record retains its original source, date,
> fixtures and owner-report limits. Its branch, price/session, “current” and
> pending instructions do not override [current GUI v2 status](../FEATURE_STATUS.md)
> or the [current test ledger](../test_checklist.md). No new test pass is claimed
> by adding this context.

> **2026-10-19 v1 SOURCE FOLLOW-UP:** `feature/kivy-gui` has been promoted to `master` and tagged as the immutable [v1.0.0 source pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0) (`07ce51d`). The findings/tests dated below remain **historical snapshots**; current source/bug/physical-device status is tracked in [FEATURE_STATUS.md](../FEATURE_STATUS.md), [bug_tracker.md](../bug_tracker.md) and [release notes](../releases/v1.0.0.md). Linux synthetic CI is not production hardware certification. QRIS remains DEMO and BUG-009 Drive cleanup is OPEN.


> **HISTORICAL QA SNAPSHOT (original logo-in-folder-QR implementation): The [later centered-logo correction](centered-qr.md) supersedes the original placement method below. **CURRENT:** folder photo QR is separate from the DEMO/non-payable payment QR; thermal printer transport is implemented in `feature/kivy-gui`, while independent physical paper QR phone-scanning evidence remains separate.**

The [centering correction](centered-qr.md) supersedes the original placement
rule below: the complete logo now stays exactly at the QR center.

This original follow-up starts from `b7fa8b774915c95da79feeca67472edd78027a7e`
on `feature/kivy-gui`. It implements the selected complete **MEONG PHOTOBOOTH**
logo inside the customer folder QR. The asset includes the wordmark, camera-cat,
and grayscale trail. The name has no final S.

The shared helper supplies the result-screen QR and the QR within every newly
saved three-photo composition. Existing saved customer images are not rewritten.
The payment simulation explicitly requests an unbranded QR and keeps its demo
payload. Actual payment-provider QRIS artwork is not processed by this helper.

## Rendering behavior

- Generate from the transaction's existing cached URL, with no network calls.
- Use error correction H for branded codes and retain a four-module white border.
- Insert the full bundled logo on a small white plate inside the data area.
- Keep the bounded full-logo plate exactly centered and preserve corner/timing
  patterns and the quiet zone. The original rule that moved the logo around a
  central alignment marker caused a visible upward shift; it has been replaced
  by independent decoding and, when needed, another valid QR encoding mask.
- Render the saved footer directly at an integer module scale within 210 pixels.
- Keep the approved accent colors in digital results. `monochrome=True` provides
  a one-bit logo for thermal print tests; the surrounding matrix is unchanged.
- Return independent image copies so one caller cannot corrupt a cached QR.

![Full-logo QR for a fixture Drive folder](branded-folder-qr.png)

The example URL above is a fixture, not a real customer folder.

## Checks performed

Environment: Python 3.12.14, Kivy 2.3.1, OpenCV 5.0.0, Pillow 12.3.0,
SDL2 offscreen, and Mesa software rendering.

```bash
SDL_VIDEODRIVER=offscreen PHOTOBOOTH_TEST_GUI=1 python -m unittest discover -s tests -v
SDL_VIDEODRIVER=offscreen python tools/render_gui.py --output-dir /tmp/meong-branded-qr-qa
```

The Python suite completed **94 tests: 92 passed and 2 optional native-palm
tests skipped** because their optional model/fixture assets were not supplied.
The four new QR tests independently decode short and realistic Drive URLs at
display and final-footer sizes, in color and one-bit output. They also check
recognition cells, the quiet zone, separate payment-demo behavior, invalid
inputs, and cache isolation.

The composition regression decodes the QR from each of the four saved template
images and checks that the logo is present in the saved pixels. The controller
and GUI regressions cover the displayed QR, cached offline destination,
upload retry, and corrected window/header naming.

The real-widget renderer completed **48 views** across **1200x800 and 800x600**.
It checked that stages fit and decoded QR content from exported screen pixels.
The [render report](branded-qr-report.json) records those results. All artwork
uses synthetic portraits and fixture destinations; no real camera or cloud
service was contacted.

![Result screen at 800x600](branded-result-800x600.png)

![Saved three-photo output with the branded folder QR](branded-composition.png)

These are digital checks. Physical thermal output, camera hardware, and actual
QRIS payments have not been tested here. Printer transport remains a separate
integration; its real dot width and final printed QR need device verification.
