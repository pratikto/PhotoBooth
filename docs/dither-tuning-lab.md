# Meong Photobooth — Thermal Dither Tuning Lab

**Experiment:** FEAT-011, investigating open BUG-004 (blurry/low-quality photo print).  
**Branch:** `feature/dither-tuning` (created 2026-10-18 from `feature/kivy-gui` commit `5e0a898`).  
**Scope:** offline photo-rendering sandbox; the existing photobooth application and photo/QR print pipeline have **not** been changed or merged.

## Enhanced Dizzy preprocessing A/B experiment (2026-10-21)

**Owner-authorized scope:** only the experimental `feature/dither-tuning` branch. The GUI now has an independent **Enhanced Dizzy (experimental)** checkbox inside the Dizzy panel. It is **OFF by default**; checking it recomputes **only** the Dizzy preview, while Floyd and Bayer remain unchanged. Both Dizzy variants (`article-8` and `orthogonal-4`) support the same checkbox. The Enhanced Floyd checkbox remains independent.

**Exact shared preprocessing**, applied after native-width Lanczos resize and user brightness/contrast/gamma/sharpness adjustments and **before** either error-diffusion algorithm:

1. PIL `MedianFilter(size=3)` to reduce isolated camera noise.
2. `ImageOps.autocontrast(cutoff=1, preserve_tone=True)`, mixed with the median-filtered image using `Image.blend(..., 0.20)`. This is a mild **global** tonal adjustment, not CLAHE or face-aware enhancement.
3. `UnsharpMask(radius=1.1, percent=55, threshold=3)` for restrained edge sharpening.

The previous Enhanced Floyd math and operation ordering are unchanged, now implemented via one shared function (`_enhance_photo_for_dithering` in `photobooth/dither_lab.py`). With both enhancement flags OFF, the original Floyd and Dizzy raster paths are unchanged. Neither the Dizzy neighborhood rules nor seed nor article-specific contrast correction LUT is modified; a stronger or different preprocessing profile will need separate evaluation.

**Saved presets:** the lab now writes **schema v4**, containing an independent `enhanced_dizzy: bool` field for each validated profile. Old v1, v2 and v3 profiles/comparison files load with `enhanced_dizzy=False` and retain prior Floyd settings, Dizzy variant/seed, hidden Threshold parameters and width. A v4 preset persists both Enhanced Floyd and Enhanced Dizzy separately. `Save All Configs` still writes the four backend lanes (including hidden Threshold); only **three panels** are rendered/printed/exported. Never copy lab presets into kiosk printer settings.

**Export and paper provenance:** the Dizzy native 1-bit PNG name now includes the variant, seed, and `-baseline` or `-enhanced` (e.g., `meong-dizzy-article-8-seed42-enhanced.png`). The lab Print Test header also labels `PREPROCESS: BASELINE` or `PREPROCESS: ENHANCED`; the 1-bit raster below the header stays byte-identical to the latest approved preview/export. Physical Print Test remains manually confirmed, with no uncertain automatic retries. This experimental change never touches the Kivy print path on `master`.

**Recommended controlled comparison:** use a saved original portrait with identical width, brightness, contrast, gamma, sharpening, Dizzy variant/seed, printer darkness and paper. Compare Dizzy baseline vs Enhanced Dizzy first; next compare Enhanced Floyd vs Enhanced Dizzy with identical preprocessing controls. Repeat for both Dizzy variants. Evaluate face details, skin texture, hair, backgrounds, black coverage and on-paper clarity; a screen preview alone cannot determine the best physical output. More preprocessing can also over-smooth detail, especially text and QR portions of a finished photo strip.

**Automated evidence:** [Dither tuning lab CI 39503134534](https://github.com/pratikto/PhotoBooth/actions/runs/39503134534), commit `80980f7ba`: compilation and **42 unit tests PASS**, including backward-compatible v1/v2/v3 preset loading, unchanged Floyd raster, deterministic baseline/Enhanced Dizzy variants, output one-bit and metadata preservation. **Windows Tk UI acceptance and thermal-paper visual quality remain pending operator testing.**

## Current three-panel GUI (2026-10-21)

The main experiment window (`python tools/dither_compare_gui.py`) now displays **Floyd–Steinberg, Bayer 8×8 and Dizzy** only. The Threshold preview, its slider and its individual print/export buttons are hidden. **Export 3 PNG** exports only those three visible outputs; **Print All (3 jobs)** submits those same three in Floyd/Bayer/Dizzy order, with the existing explicit confirmation and stop-on-uncertain-outcome protections.

Only the Tkinter comparison interface changes. The Threshold algorithm remains available in `photobooth/printer.py`, `photobooth/dither_lab.py`, and the legacy standalone tools. **Save All Configs** still writes the four-mode lab JSON (including the hidden Threshold profile) to preserve v4 schema and backward compatibility with existing presets; Load All Configs accepts v1/v2/v3/v4. Selecting a new print width also updates the hidden profile so the saved shared width remains consistent. No changes to live Kivy printing or `master`. Paper-quality acceptance remains pending.

## Article-aligned Dizzy Dithering experiment (2026-10-21)

**Current test GUI:** `python tools/dither_compare_gui.py` now shows **three visible lanes**: Floyd, Bayer and Dizzy. Threshold remains saved but hidden. The Dizzy lane has two selectable variants:

- `article-8` (default): from Liam Appelbe's 2024 article. Process pixels in a pseudorandom order, diffuse error only to unprocessed neighbors among all 8 directions, weight axial neighbors 1.0 and diagonals 0.1, and normalize by the **sum of eligible neighbors' weights**.
- `orthogonal-4`: from the 2026 follow-up and sample Gist. Propagate evenly only to unprocessed horizontal/vertical neighbors (4 directions).

Both use a local fixed seed (`42`), a five-round odd-multiply/XOR permutation on a padded power-of-two pixel-index domain (first article optimization), float-valued error accumulation (avoids repeated integer rounding), and exact Pillow mode `1` output with no secondary halftone. The author's minimal Gist uses a shuffled list and rounded 8-bit updates; Meong is an **article-aligned adaptation**, not guaranteed pixel-identical to his Gist or GPU shader.

The 2026 contrast-correction lookup tables are specific to the author's calibrated algorithm variants. **No LUT is applied** in this first experiment: article-8 needs separate calibration; orthogonal-4 should be checked against the author's response curves before considering the author's lookup values.

Lab profiles and four-lane comparisons save as **v4 JSON**, including `dizzy_variant` and `dizzy_seed`; loading v1/v2 profiles retains prior lanes and adds Dizzy with defaults. Printer settings, production `photobooth.printer.DITHER_MODES`, `main.py` and the main photo-prints are **unchanged**.

For a fair evaluation: open the same photo, use equal brightness/contrast/gamma/sharpness/width across algorithms, disable Enhanced Floyd for the initial algorithm-only comparison, then export each exact 1-bit raster. Switch Dizzy to orthogonal-4 and export that separately; Dizzy filenames contain variant and seed. The reduced GUI overview uses BOX area averaging for screen display; the nearest-neighbor crop, exported PNG and Print Test raster remain exact printer dots.

`Print All (3 jobs)` still requires explicit approval and stops when a job is failed or uncertain. Test print headers include Dizzy variant and seed. Do not treat successful transport as physical paper-quality proof. Compare the same face/hair/shadows/gradients on the actual printer and record paper type and printer darkness; keep QR/text legibility as a separate criterion.

Code: `photobooth/dizzy_dither.py`, `tests/test_dizzy_dither.py`, `tests/test_dizzy_lab_integration.py`. Preliminary isolated Python/Pillow test: 5 Dizzy core tests passed; on a synthetic 576x579 image, about 0.97 seconds (article-8) and 0.65 seconds (orthogonal-4) in that local test environment. This is **not** measured Windows/GUI or physical-printer acceptance. The GitHub workflow is configured to run broader regression tests; verify its actual run status separately.

References: [original article](https://liamappelbe.medium.com/dizzy-dithering-2ae76dbceba1), [GPU follow-up](https://liamappelbe.medium.com/dizzy-dithering-on-the-gpu-84f2d2c12a82), [author Python Gist](https://gist.github.com/liamappelbe/c2c76ad1ba655aa1caae5da40bcadc7e), [author calibration LUT](https://gist.github.com/liamappelbe/cc6bdfd94fdf19ffe1cee1ed2c808fea).

**Scope:** `feature/dither-tuning` only, no `master` merge, no Kivy customer journey change, no production printer change. Rollback: switch back to the previous 3-lane branch revision.

## Experimental enhanced Floyd preprocessing (2026-10-21)

An opt-in **Enhanced Floyd (experimental)** checkbox is available in `tools/dither_compare_gui.py`. It affects the Floyd lane only; Enhanced Dizzy now separately opts into the same preprocessing helper in the Dizzy panel. Unchecked uses the byte-identical legacy baseline path; checked applies a 3x3 median noise filter, a 20% blend with gently autocontrasted grayscale, and restrained unsharp masking (radius 1.1, strength 55%, threshold 3), after the existing brightness/contrast/gamma/sharpness controls and before Pillow Floyd–Steinberg error diffusion. This is conservative *global* tonal processing, **not CLAHE, face-aware enhancement, or printer heat control**. Existing control values still matter and aggressive settings may degrade results.

The check box allows A/B comparison by exporting/printing Floyd baseline, then toggling on and exporting/printing Floyd enhanced with the same image, width and sliders. Exports include `-baseline` or `-enhanced` suffix; only the native 1-bit result should be used for dot-level comparison. The comparison GUI now displays Floyd/Bayer/Dizzy. Save/Load All Configs persists both enhancement switches; v4 JSON files are written, while v1/v2/v3 presets remain readable. Do not copy these JSONs into printer settings.

Scope is `feature/dither-tuning` only. **The customer-facing `main.py`, `master` printer preset, printer ESC/POS path and production configuration have not been changed.** Preview is not proof of printed quality. Physical comparison must use identical photographs, paper, speed and printer settings, and operator-confirmed test printing. Automated regression tests were added, but physical acceptance remains pending.

## Screen preview fidelity fix (2026-10-21)

The GUI overview previously shrank a 1-bit dithered raster with NEAREST, aliasing away many black/white dots and making the monitor look worse than physical paper. The reduced overview now uses BOX area averaging in display grayscale to preserve approximate visual dot coverage. The overview's grays are *screen-only* representations of black/white dot density. The nearest-neighbor detail crop, native 1-bit PNG export, and ESC/POS paper payload are unchanged. Compare actual dots using the detail crop and final fidelity on paper.

## BUG-010 layout usability

Each algorithm has an independently scrollable parameter area. Hover its slider region and turn the mouse wheel, or drag the adjacent vertical scrollbar. The preview remains visible, and Print Test / Save PNG remain on screen outside the slider scroll region. This must still be checked on the operator's actual Windows screen.

## Three-algorithm comparison GUI (current)

**Primary GUI for this branch**: `python tools/dither_compare_gui.py`. It shows the **same original image plus three live raster previews**: Floyd–Steinberg, Bayer 8×8 and Dizzy (article-8/orthogonal-4). Each visible column owns its own brightness, contrast, gamma and sharpening sliders; Threshold is not displayed. Tick **Sync Parameters** to copy a subsequent brightness/contrast/gamma/sharpness slider change to all three columns. Toggle it off to resume independent tuning. Width (384 or 576 dots) is deliberately shared for fair paper comparison. A central dot crop can be zoomed 1×, 2×, or 4×, rendered nearest-neighbor.

Controls are debounced and images are rendered on workers; stale results are dropped. The GUI also reports native output size, percentage of black pixels and render time (informational, not a physical quality score). **Save All Configs** and **Load All Configs** use a versioned JSON file that is strictly independent of the kiosk's printer settings. **Export 3 PNG** saves the three visible exact full-resolution 1-bit rasters; **Save PNG** in each column saves just that lane.

### Real-paper Print Test

- Configure the **existing kiosk printer** via `python main.py` → gear → **Pengaturan Printer** first. The lab reads `data/printer_settings.json` (USB Windows queue, LAN or Wi-Fi). It does not edit that file. On Windows, the active printer queue requires `pywin32` and an ESC/POS-capable driver.
- After the latest previews finish, click **Print Test** under one algorithm or **Print All (3 jobs)**. An explicit confirmation explains the number of real print jobs; cancel prints nothing.
- The lab snapshots the currently displayed one-bit raster and chosen parameters. The ESC/POS spool includes a parameter label above the original dot image, then sends it via the existing `ThermalPrinter` route logic. **No second dithering or resize of the original raster occurs**.
- **Print All** sends the visible algorithms in Floyd/Bayer/Dizzy order, stops on the first failure or uncertain status, and never automatically retries that image through a different transport after transmission may have begun. The user must inspect the physical paper and decide on any repeat manually. Success means data was accepted by the transport—not confirmed physical printing.
- During printing, further slider edits will not change the queued snapshot; Print buttons refuse another batch until the current batch finishes. Avoid stopping the application mid-spool.

**Known limitations:** the preview display is scaled for the screen; only native PNG export and physical paper reveal actual dot pattern. A fixed 8×8 Bayer matrix and existing Pillow Floyd–Steinberg are retained. Device heat/darkness is not tunable through this lab. Windows GUI interactions and physical print remain **owner verification pending**; no customer-facing production integration is approved.

## Open the standalone GUI (Windows / VS Code PowerShell)

From the repository root, after safely storing any uncommitted work:

```powershell
git fetch origin
git switch feature/dither-tuning
git pull --ff-only origin feature/dither-tuning
python -m pip install Pillow
python tools/dither_compare_gui.py
```

Python on Windows normally includes Tkinter; if `import tkinter` fails, use a Python build with Tcl/Tk installed. **Do not run `python main.py` to access this lab**; it opens a separate desktop window with no camera, Drive, sound, payment or printer dependency.

## How to test

1. Initially a **synthetic gradient/sample image** is shown. Click **Buka foto** to load an actual locally saved composition PNG/JPG. Photos are processed in memory on the local computer; the lab does not upload them.
2. Compare **Floyd–Steinberg**, **Bayer** (fixed 8×8 ordered screen), or **Dizzy** (article-8/orthogonal-4). Threshold remains available only in backend and legacy tooling.
3. Choose **576 dots** (typical 80 mm printhead image area) or **384 dots** (typical 58 mm area). The renderer preserves aspect ratio and downsizes using the same Lanczos method as the existing printer pipeline; smaller sources are **not upscaled**.
4. Adjust **Brightness**, **Contrast**, **Gamma**, and **Sharpness**. Each starts at **1.0** (no correction). Gamma above 1 lightens midtones. There is no Threshold slider in the current three-panel comparison GUI.
5. Inspect **Sumber**, **Raster 1-bit**, and the **3× nearest-neighbor center-crop dot preview**. The full preview is display-scaled for convenience; actual exported image pixels are not rescaled after dithering.
6. Click **Simpan preset** to save an independent JSON recipe, **Load All Configs** to restore it later, and **Save PNG** / **Export 3 PNG** to export the complete native-width raster. Export is blocked until preview for the current controls is ready.

| Parameter | Allowed range | Default | Affects |
| --- | --- | --- | --- |
| Dither mode | `floyd-steinberg`, `bayer`, `threshold` | `floyd-steinberg` | Halftone algorithm |
| Width | 384 or 576 dots | 576 | Native downsample target |
| Brightness | 0.5–1.75 | 1.0 | Grayscale intensity before dithering |
| Contrast | 0.5–2.5 | 1.0 | Grayscale contrast before dithering |
| Gamma | 0.3–3.0 | 1.0 | Midtone mapping before dithering |
| Sharpness | 0.0–3.0 | 1.0 | Edge sharpening before dithering |
| Threshold | 0–255 | 128 | **Threshold mode only** |

Image pipeline: **composite transparency onto white → grayscale → proportional Lanczos downsampling (only when too wide) → brightness → contrast → gamma → sharpness → selected existing `dither_image` → 1-bit PNG**. The defaults match the existing 1-bit raster for the same source dimensions and dither mode.

### What saved presets do NOT do

- JSON lab profiles are **NOT** loaded by `main.py`, `PrinterConfig`, or `data/printer_settings.json`. Different schemas; do not copy/overwrite that file.
- Exporting a PNG **does not print**. It does not configure physical printer darkness/heat, paper quality or firmware. An on-screen preview is **not proof** of physical dot reproduction.
- This branch is not a fix/closure for BUG-004 until controlled real-paper results are reviewed and owner-approved.
- Physical print comparison remains an **explicit separate operator action**: existing `tools/print_dither_comparison.py` can print a saved composition when configured for the correct real printer; it sends actual paper jobs. Never automatically submit several prints when a job's outcome is uncertain.

## Test evidence and next acceptance

Source commit [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229), [dedicated GitHub Actions run 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478): **PASS** for compile and targeted unit tests. Run locally:

```powershell
python -m unittest tests.test_dither_lab -v
```

**Still pending:** Windows GUI screenshot and interactions, preview/slider responsiveness, physical printer samples for each mode with the same photograph and settings, and the operator's assessment of clarity. The baseline Kivy kiosk suite remains a separate pre-existing issue; this lab's passing CI must not be represented as a full kiosk release test.

**Rollback/isolation:** checkout `feature/kivy-gui` without merging; its printer behavior is unchanged. Any transfer of lab profile behavior into the customer kiosk needs a **new explicit approval**, printer quality regression tests, and device evidence.
