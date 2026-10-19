# Meong Photobooth — Thermal Dither Tuning Lab

> **CURRENT SOURCE (2026-10-19):** This functionality and related documentation are now part of `master` at the published, immutable `v1.0.0` [source pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0). The previous `feature/kivy-gui` and other feature branches remain historical references. CI passed on the tagged SHA (`07ce51d`, [Kiosk](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245), [Dither](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273)), but physical Windows acceptance is separate. BUG-001/007 audio and BUG-009 Drive retention remain unresolved; payment stays DEMO. Dither lab FEAT-011 and the approved Floyd default are included in v1; the saved standalone lab JSON still does **not** automatically control kiosk printing.

**CURRENT state:** FEAT-011 lab and the approved default Floyd photo profile are available on `master` / `v1.0.0`; BUG-004/010 owner-reported PASS (not a complete printer/media test matrix).  
**HISTORICAL origin:** `feature/dither-tuning` was created 2026-10-18 from `feature/kivy-gui` at `5e0a898` and initially kept its experiment separate. The standalone lab remains a tool, while the approved Floyd preprocessing is now on the Kivy photo-print path.

## BUG-010 layout usability

Each algorithm has an independently scrollable parameter area. Hover its slider region and turn the mouse wheel, or drag the adjacent vertical scrollbar. The preview remains visible, and Print Test / Save PNG remain on screen outside the slider scroll region. This must still be checked on the operator's actual Windows screen.

## Three-algorithm comparison GUI (current)

**Primary GUI for this branch**: `python tools/dither_compare_gui.py`. It shows the **same original image plus three live raster previews**: Floyd–Steinberg, Bayer 8×8, Threshold. Each column owns its own brightness, contrast, gamma and sharpening sliders; Threshold alone has a threshold slider. Tick **Sync Parameters** to copy a subsequent brightness/contrast/gamma/sharpness slider change to all three columns. Toggle it off to resume independent tuning. Width (384 or 576 dots) is deliberately shared for fair paper comparison. A central dot crop can be zoomed 1×, 2×, or 4×, rendered nearest-neighbor.

Controls are debounced and images are rendered on workers; stale results are dropped. The GUI also reports native output size, percentage of black pixels and render time (informational, not a physical quality score). **Save All Configs** and **Load All Configs** use a versioned JSON file that is strictly independent of the kiosk's printer settings. **Export 3 PNG** saves the three exact full-resolution 1-bit rasters; **Save PNG** in each column saves just that lane.

### Real-paper Print Test

- Configure the **existing kiosk printer** via `python main.py` → gear → **Pengaturan Printer** first. The lab reads `data/printer_settings.json` (USB Windows queue, LAN or Wi-Fi). It does not edit that file. On Windows, the active printer queue requires `pywin32` and an ESC/POS-capable driver.
- After the latest previews finish, click **Print Test** under one algorithm or **Print All (3 jobs)**. An explicit confirmation explains the number of real print jobs; cancel prints nothing.
- The lab snapshots the currently displayed one-bit raster and chosen parameters. The ESC/POS spool includes a parameter label above the original dot image, then sends it via the existing `ThermalPrinter` route logic. **No second dithering or resize of the original raster occurs**.
- **Print All** sends the algorithms in Floyd/Bayer/Threshold order, stops on the first failure or uncertain status, and never automatically retries that image through a different transport after transmission may have begun. The user must inspect the physical paper and decide on any repeat manually. Success means data was accepted by the transport—not confirmed physical printing.
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
2. Choose **Floyd–Steinberg**, **Bayer** (fixed 8×8 ordered screen), or **Threshold**.
3. Choose **576 dots** (typical 80 mm printhead image area) or **384 dots** (typical 58 mm area). The renderer preserves aspect ratio and downsizes using the same Lanczos method as the existing printer pipeline; smaller sources are **not upscaled**.
4. Adjust **Brightness**, **Contrast**, **Gamma**, and **Sharpness**. Each starts at **1.0** (no correction). Gamma above 1 lightens midtones. The **Threshold** slider is enabled only for the Threshold algorithm, because that parameter has no effect on Floyd–Steinberg or Bayer.
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
- **CURRENT evidence:** the owner later accepted the Floyd photo improvement (BUG-004 OWNER REPORTED PASS). No controlled before/after paper matrix was archived, so do not treat this as formal cross-printer quality certification.
- Physical print comparison remains an **explicit separate operator action**: existing `tools/print_dither_comparison.py` can print a saved composition when configured for the correct real printer; it sends actual paper jobs. Never automatically submit several prints when a job's outcome is uncertain.

## Test evidence and next acceptance

Source commit [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229), [dedicated GitHub Actions run 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478): **PASS** for compile and targeted unit tests. Run locally:

```powershell
python -m unittest tests.test_dither_lab -v
```

**Remaining evidence (not a claim the operator's PASS did not happen):** a recorded 3-algorithm same-photo Windows paper comparison, exact device SHA/media width and repeatable slider/print results. **Kiosk GUI full CI now PASS** ([run 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762)) and Dither CI PASS ([run 39145145764](https://github.com/pratikto/PhotoBooth/actions/runs/39145145764)) at `c40f33f5`; neither proves every real printer medium.

**CURRENT rollback/isolation:** The lab is **included in the `master` v1 source** (originally integrated through `feature/kivy-gui`), and `photobooth/printer.py` uses approved Floyd preprocessing for photo output by default. For troubleshooting, `PHOTOBOOTH_PHOTO_TUNING=legacy` restores prior preprocessing without reverting unrelated commits. Future *different lab JSON presets* still need explicit approval before changing the main app; never replace `data/printer_settings.json` with incompatible lab JSON. Do not merge to `master` without explicit release authorization.
