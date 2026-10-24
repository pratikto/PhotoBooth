# Meong Photobooth — Thermal Dither Tuning Lab


> **Operator reference (English):** [Dither Comparison GUI — Complete Parameter Guide](dither-gui-parameter-guide.md). It explains every visible slider, checkbox, algorithm mode, toolbar action, Auto Tune control and print/export action, including their effects on face, hair, highlights, shadows and native 1-bit thermal dots. Use it before manual A/B testing or real-paper printing.


### Final staged GitHub CI evidence — 2026-10-24

**Stages 1–3 now pass** in
[GitHub Actions run 40043510521](https://github.com/pratikto/PhotoBooth/actions/runs/40043510521)
at commit `49799515c0555227983d929da1c50458f0582b2c`:
**75 targeted backend/static tests PASS**, **12 real Tk/Xvfb smoke tests PASS**,
256-tone digital calibration scan PASS, Python compile PASS and author
reference comparison PASS. Exported artifacts:

- [256-tone CSV/JSON/SVG](https://github.com/pratikto/PhotoBooth/actions/runs/40043510521/artifacts/12539824481)
- [Reference source, optimized raster PNG/difference PNG/JSON](https://github.com/pratikto/PhotoBooth/actions/runs/40043510521/artifacts/12540132879)

Measured digital MAE: article-8 0.3896pp -> 0.0259pp; orthogonal-4
1.3590pp -> 0.0495pp. On the separate synthetic reference image,
Meong orthogonal-4 disagrees with the shuffled Gist-style output at
31.75% of pixels, but only 0.65% when visitation order is held fixed.
Meong article-8 differs by 32.54% from independent shuffled-order
eight-neighbor pseudocode. Similar average black/white coverage does not
guarantee visual similarity or print quality. The reference is an
**independent adaptation**, not byte-identical official author code.

**Remaining acceptance gates:** Windows operator GUI test, calibration
generalization across photographs/seeds, measured SBC throughput and actual
thermal-paper A/B test. None of these have been performed by GitHub Actions.
`feature/dither-tuning` is still lab-only; no merge into `master`,
Kivy kiosk/QR pipeline change or uncontrolled print action.


## Stage 3: controlled author-reference comparison (2026-10-24)

Run from repository root:

```powershell
python tools/dizzy_reference_compare.py --width 144 --height 168 --seed 42 --output-dir data/dizzy_reference
```

This creates **no real print job** and never touches kiosk/QR code.
By default it uses a reproducible synthetic gradient with an edge/portrait-like
shape. Supply `--image path/to/photo.png` to use your own test photo;
the image is processed locally without upload.

**Reference provenance is explicit:**

1. **`orthogonal-4`:** independently written adaptation of [Liam Appelbe's
   published Python Gist](https://gist.github.com/liamappelbe/c2c76ad1ba655aa1caae5da40bcadc7e).
   Retains its shuffled *column-major* coordinate order, rounded/clamped
   8-bit neighbor updates, four orthogonal directions, and `<128`
   black decision. Uses a fixed local seed for reproducibility (author's
   sample uses ambient `random.shuffle`).
2. **`orthogonal-4`, equal order:** the same Gist-style 8-bit math, but
   substitutes Meong's five-round index permutation. This intentionally
   holds iteration order constant and isolates the effect of intermediate
   8-bit rounding/clamping versus Meong's float32 buffer.
3. **`article-8`:** independent implementation of the 2024
   [article pseudocode](https://liamappelbe.medium.com/dizzy-dithering-2ae76dbceba1),
   using a seeded full shuffle, 8 neighbors with diagonal weight 0.1, and
   float64 accumulation. **This is not an official published 8-neighbor
   Python Gist.**

Outputs include per-variant `*_meong.png`, `*_reference.png`,
`*_difference.png` (white pixels mark disagreements), a special
`*_gist_equal_order.png` for the four-neighbor numeric comparison, and
`dizzy_reference_comparison.json`. The JSON reports percent disagreeing
pixels, white-dot coverage for both images and signed coverage difference.
Since author and Meong use different visitation order/precision, pixelwise
identity is **not** expected and percent-difference alone is not a photo
quality score. Tone LUT stays **OFF** during these comparisons to isolate
the original dithering math.

The GitHub Actions dither-lab workflow runs an offline reference comparison
and uploads `meong-dizzy-reference-comparison` artifacts with the test.
No GPU Layered Dizzy implementation, GPU LUT copy, or production integration
is authorized by this experiment.


## Stage 2: complete grayscale fidelity test and plots (2026-10-24)

Run from the repository root on Windows/Linux:

```powershell
python tools/dizzy_fidelity.py --width 96 --height 96 --seed 42 --output-dir data/dizzy_fidelity
```

The default is **all 256 input gray values 0..255** on synthetic, uniform
96x96 test fields, separately for `article-8` and `orthogonal-4`. It
measures physical dot *count* in the native one-bit output (not appearance
on the screen), both **Tone LUT OFF and Tone LUT ON**. Results:

- `dizzy_grayscale_0-255.csv`: one row per shade and algorithm, target
  % white dots, baseline %, corrected %, and signed errors in percentage points.
- `dizzy_fidelity_summary.json`: reproducible metadata, every measured
  row, MAE and worst-case errors, and relative improvement percentages.
- `dizzy_fidelity.svg`: two independent response plots with ideal linear,
  baseline, and corrected coverage curves. Open the SVG in any browser.

The GitHub Actions dither-lab workflow automatically runs the same **256-level
audit** and uploads the three files as `meong-dizzy-cpu-fidelity-256`
artifacts. The CI gate requires corrected MAE to beat uncorrected MAE for
both CPU variants. A smoke test uses fewer tones; the actual workflow uses
all 256 levels. Vary `--seed`, `--width`, or `--height` to check
generalization (sizes limited to 16..256 to bound CPU processing).

Note: digital white-dot-density fidelity does not measure spatial noise,
edge preservation, actual printer density, face quality, thermal heat or paper
response. Real-photo and paper comparisons remain mandatory.


**Verified Stage-2 CI:** [run 40043294118](https://github.com/pratikto/PhotoBooth/actions/runs/40043294118)
compiled, passed 69 backend/static tests and 12 Tk/Xvfb tests and uploaded
[CSV/JSON/SVG](https://github.com/pratikto/PhotoBooth/actions/runs/40043294118/artifacts/12539718225).
Full 256-level seed42 digital MAE **article-8 0.3896 -> 0.0259
percentage points (93.4% less)** and **orthogonal-4 1.3590 -> 0.0495
percentage points (96.4% less)**. This is on the same calibration grid; test
other seeds and physical paper separately.

## Stage 1: CPU Dizzy inverse-tone LUT (2026-10-24)

Opt-in per-variant calibration follows Liam Appelbe's inverse tone-response
method. Meong uses its **own CPU** 96x96/seed-42 measurements, not the author's
separate `Layered Dizzy` GPU LUT. The two Q16 tables are in
`photobooth/dizzy_calibration.py`: `article-8` (8 neighbors) and
`orthogonal-4` (4 neighbors), digitally calibrated independently.

- Checkbox **Dizzy CPU Tone LUT (experimental)** is inside the Dizzy panel.
  It is OFF by default. The old byte-for-byte uncorrected result remains
  available (and the default for old v1-v5 JSON).
- The inverse table maps each grayscale input byte to float in [0,1] *before*
  Dizzy error propagation; output stays native binary dots and is not
  re-dithered. The toggle never changes Floyd, Bayer, hidden Threshold or
  production Kivy/ESC-POS code. Save PNG uses suffix `-tone-lut`; the real
  Print Test remains an explicit confirmation and prints the LUT ON/OFF label.
- Auto Tune considers corrected and uncorrected Dizzy candidates, with the
  same explicit Apply / Save / Cancel behavior. Preset schema advances to v6,
  backwards-loading v1-v5 with this feature disabled.
- Measured uniform 96x96 grayscale response (all 0..255, fixed seed):
  `article-8` mean absolute white-dot-density error ~0.00390 before,
  ~0.00025 after; `orthogonal-4` ~0.01359 before, ~0.00050 after.
  These are digital lab statistics only, not a guarantee for other seeds,
  real faces or thermal paper. Stage 2 will measure/plot all levels and
  cross-seed generalization in the reproducible fidelity tool.

Source method: https://liamappelbe.medium.com/dizzy-dithering-on-the-gpu-84f2d2c12a82
Author's DIFFERENT CPU/GPU curves: https://gist.github.com/liamappelbe/cc6bdfd94fdf19ffe1cee1ed2c808fea


## Smart Enhance + Selective 1-bit Post-Processing — 2026-10-23

**Implementation status:** opt-in **in the existing three-panel comparison GUI** on
`feature/dither-tuning`. This experiment deliberately does not modify the
Kivy kiosk GUI, the production printer code, the receipt/QR pipeline, or master.
Each Floyd–Steinberg, Bayer 8×8 and Dizzy panel keeps existing manual
Brightness/Contrast/Gamma/Sharpness, the existing enhanced checkboxes where
applicable, native preview, **Auto Tune**, Print Test and Save PNG buttons.

### Use it

1. Run `python tools/dither_compare_gui.py` on Windows and open a
   representative photo. Select the correct 576/384-dot printer width.
2. In the desired algorithm panel use **Quick Processing A/B** to select
   **Original**, **Smart Enhanced**, **Smart + Post**, or **Post Only** without
   altering manual strength values. Alternatively switch on
   **Smart Enhance (optional)** and/or **1-bit Post-Processing (optional)**
   individually. Smart Enhance performs median noise removal,
   clip-limited adaptive histogram equalization
   (CLAHE), and gentle tone balancing. Expand **Image Processing Options**
   in the existing *scrollable* panel to adjust CLAHE Strength (0.0–1.0),
   Median Denoise (0–2), and Tone Balance (0.0–1.0).
3. Optionally switch on **1-bit Post-Processing (optional)**. Under advanced
   controls set Selective Dot Cleanup (0–3) and Edge Refinement (0–3). Cleanup
   only acts in near-white/near-black flat source regions, preserving the
   1-bit halftone grain around actual midtones. Edge refinement only anchors
   high-contrast source edges with extreme light/dark pixel values.
4. Use manual tuning as before, or press **Auto Tune** within *that same
   algorithm panel*. The bounded offline search additionally evaluates
   opt-in processing combinations, and includes an enhanced/post candidate
   for human review even if the digital metric prefers the baseline.
   Inspect the three 1-bit candidates and their enable flags/levels.
   **Apply Best / Apply Selected** updates only the selected lane, even if
   Sync Parameters is enabled. Close/cancel/save candidates without applying
   whenever desired.
5. **Print Test** requires separate positive operator confirmation.
   Compare original, Smart only, and Smart + Post on the same paper and
   printer heat/darkness settings. Small on-screen digital-score gains are
   not a physical print-quality guarantee. Export PNG raster to inspect dots
   without touching a printer. The photo raster stays native 1-bit
   throughout; no secondary dithering is performed after post-processing.

### Compatibility and safe defaults

- Both new enable flags default **OFF**, so legacy Floyd/Bayer/Dizzy raster
  output remains byte-identical when enhancements are not enabled.
- `DitherProfile` and comparison preset schemas are now **v5**, with strict
  bounds for new parameters; old v1/v2/v3/v4 JSON loads with the new stages
  disabled. Save All Configs, Save Selected Preset, and Load All Configs
  remain **lab-only** (never automatically imported into production).
- No OpenCV, NumPy, external model, cloud service, or new hardware dependency:
  CLAHE uses clipped local histograms and interpolated tile LUTs in
  Pillow/Python; processing runs in the GUI's existing daemon render worker.
  Heavy photos can take longer on SBCs. Auto Tune uses reduced-resolution
  proxy searches; Dizzy uses a smaller search budget.
- Post-process is guarded by the **source grayscale**, not a generic binary
  erosion/dilation. Unmasked Floyd/Dizzy/Bayer halftone pixels are left
  unchanged. Never post-process QR or text: the experiment only handles the
  photo raster before the separately-added labeled test-print header.

### Verification

CI compiles `photobooth/dither_processing.py`, covers CLAHE deterministic
output, uniform patches, 1-bit retention, midtone halftone preservation,
selective speck removal, edge anchors, validation/serialization, legacy
v4 compatibility and GUI lane isolation under Sync Parameters. Linux Xvfb
also exercises expanded controls, toggle and Reset. Windows layout and
actual thermal-paper fidelity still require real-world acceptance.


## All-algorithm Auto Tune — 2026-10-23

The comparison GUI now displays **Auto Tune** independently in the Floyd–Steinberg, Bayer 8×8, and Dizzy panels. This supersedes the earlier Floyd-only restriction described below. Threshold continues to be hidden from the 3-panel GUI, but is supported by the auto-tune backend for compatibility with stored lab profiles.

- Each visible algorithm searches its own bounded parameters, independent of the current manual slider values. Floyd searches Enhanced Floyd; Bayer keeps its fixed 8×8 screen; Dizzy evaluates baseline/enhanced preprocessing and both article variants. Hidden Threshold can optimize its threshold cutoff as well as tonal preprocessing.
- Each search uses reduced-resolution proxy scoring, native-dot verification, a system-neutral baseline and up to three ranked preview candidates. Dizzy uses a smaller proxy and search budget due to its CPU cost. The heuristic score is **not** calibrated print quality.
- The per-lane Auto Tune button becomes **Cancel Tune** while busy. Running a different algorithm cancels the old search. Source/width changes invalidate the current search; altering parameters of the actively tuned lane invalidates its candidates.
- **Apply Best / Apply Selected** updates only the matching algorithm's profile and controls, even if Sync Parameters is ON. The manual sliders, Print Test, Save PNG and Save All Configs still work. Save Selected Preset remains lab-only and does not apply silently.
- No auto-printing, changes to the production print engine, or merging to master. Always validate the recommended recipe on the actual paper and printhead.

Validation is through the branch's targeted backend tests and real Tk runtime smoke tests on GitHub Actions; paper and Windows visual assessment still require operator testing.


## Independent Auto Tune GUI — 2026-10-23

Owner-approved FEAT-011 continuation: Auto Tune ignores manual parameter values.
The existing Floyd **Auto Tune** button starts a reproducible system search:
16 seeded random samples across bounded brightness/contrast/gamma/sharpness,
then coarse-to-fine coordinate refinement from neutral and the best sampled
profile. At most 65 proxy + 8 native evaluations. Only print width is inherited;
photo grayscale is the scoring target. Neutral Enhanced Floyd is always a native
finalist and the dialog reports score differences against this system reference.
Manual sliders and their current values remain available and unchanged until
**Apply Best / Apply Selected**. Closing/cancelling keeps manual settings;
Save Selected Preset exports without applying. After Apply, sliders remain editable.
Print Test is still a separate operator action. Search remains Enhanced Floyd only.

Validation: 53 targeted backend/static regressions PASS on Linux/Pillow 12.3.0;
compile PASS. Regression verifies identical candidates, scores and raster bytes
with opposite manual parameter extremes. Tk runtime and Windows/paper checks
remain pending (no local display/Xvfb). Supersedes the manual-seeded search and
manual-baseline dialog described in historical entries below. Local checkpoint:
`05f699d`; remote baseline/rollback `26964d8`. Publication previously blocked by
automatic approval review; no new push attempted without explicit authorization.


**Experiment:** FEAT-011, investigating open BUG-004 (blurry/low-quality photo print).  
**Branch:** `feature/dither-tuning` (created 2026-10-18 from `feature/kivy-gui` commit `5e0a898`).  
**Scope:** offline photo-rendering sandbox; the existing photobooth application and photo/QR print pipeline have **not** been changed or merged.

## Auto Tune improvement — 2026-10-22

Owner request: continue improving Auto Tune (FEAT-011 / BUG-004) on
`feature/dither-tuning`. Base/rollback: `26964d89f4a7761799480b6bd54e9e4ba2b0e649`.
Scope: bounded manual + neutral search, dot-averaged scoring for small images,
and exact original-profile comparison in the review dialog. No printer transport
or production settings changes. Acceptance: deterministic native 1-bit outputs,
original checkbox/profile preserved in baseline, best score at least as good as
neutral Enhanced Floyd, cancellation and independent Floyd Apply retained.
Tests: lab regression suite, new metric/baseline/search regressions, Tk runtime CI.
Hardware and Windows visual acceptance remain pending.

## Auto Tune Enhanced Floyd — manual-review experiment (updated 2026-10-22)

**Status:** Owner-approved scope in existing `feature/dither-tuning` only (FEAT-011 / BUG-004). The three-pane GUI now includes an **Auto Tune** button in the Floyd–Steinberg panel next to the existing Print Test / Save PNG actions. **This feature does not change the Kivy production printer, existing photo/QR pipeline, or `master`.**

**Workflow (no physical printer accessed while searching):**

1. Run `python tools/dither_compare_gui.py` and open a representative photograph. Choose print width 576 or 384. Keep or adjust the Floyd starting sliders; enable/disable the current checkbox as desired. **Auto Tune always evaluates Enhanced Floyd**, without silently changing the current checkbox.
2. Click **Auto Tune**. A cancellable background search tries bounded combinations of **Brightness, Contrast, Gamma, Sharpness**, starting from the current Floyd sliders. During calculation the button becomes **Cancel Tune**, and the footer reports progress. Closing the GUI or changing the source, paper width, Floyd enhancement state or Floyd sliders cancels/invalidate the old results. While Sync Parameters is ON, changes to synced sliders also invalidate the search.
3. A separate comparison dialog displays **three native 1-bit raster candidates**, each shown with a BOX-downsampled monitor preview, heuristic **digital-fidelity score**, selected slider values, edge/tonal error and black-dot coverage. It offers **Apply Best**, **Apply Selected**, **Save Selected Preset** and **Close**.
4. **Apply** updates **only the Floyd lane** (including Enhanced Floyd checked), then re-renders it. Bayer/Dizzy are untouched even if `Sync Parameters` is checked. **Save Selected Preset** exports a **Load All Configs-compatible full lab configuration** (schema-v4 JSON) containing the chosen Floyd candidate and current Bayer, Dizzy, and hidden Threshold settings. It does **not** change the currently active GUI settings. You can reopen the file with **Load All Configs** later; alternatively, click Apply and then Save All Configs. Closing the dialog never changes settings. **Print Test** is a separate, explicit, confirmed real-paper action.
5. For controlled A/B tests, print the **previous manual profile** and the chosen candidate on the same paper at the same printer speed/darkness, assess portraits/skin/hair/shadows and QR/text separately, and record the settings and physical outcome. Prefer the physical result if it disagrees with the on-screen ranking.

**How ranking works:** `photobooth/dither_autotune.py` performs a small deterministic coarse-to-fine coordinate search. It evaluates at most **50 distinct proxy settings** from both manual and neutral starting points on a reduced sample (max 384×520 px), shortlists up to **8 candidates**, then rerenders and ranks them using the **actual requested native-dot output** (up to **59 evaluations**, including a separate exact original-profile baseline when needed). Both manual Enhanced Floyd and neutral Enhanced Floyd are guaranteed native finalists. The exact original profile (including enhancement OFF) is scored separately; the dialog shows its score and each candidate’s signed difference. Small images now blend dots over at least roughly three horizontal pixels rather than comparing individual binary dots directly. Scores from the older metric are not comparable. The score combines distance to the original image's grayscale after downsampled dot-coverage reconstruction, approximate local edge differences, a source-relative black coverage penalty and a small extreme-slider penalty. A score out of 100 is **only a within-photo heuristic**; it is **not SSIM, a learned perceptual model, a face-quality or biometric assessment, a physical printer calibration, or a guarantee of optimal output**. Noise, contrast, printer heat, paper and viewing distance can reverse the ranking. Search processing is offline and uses Pillow only; no uploads, external APIs or automatic thermal printing.

**Safety / compatibility:** the baseline/Enhanced Floyd render math is untouched; all three suggested raster outputs are exactly mode `1` and can be reproduced using their stored `DitherProfile` parameters. The GUI dispatches computation to a daemon worker; only Tk's main thread manipulates widgets. A generation token and thread cancellation signal discard stale results when source or Floyd settings change. Saving a lab comparison preset never changes production settings. Existing schema-v1/v2/v3/v4 presets and hidden Threshold values remain supported. **Rollback point before Auto Tune:** [`0924ea6`](https://github.com/pratikto/PhotoBooth/commit/0924ea6d6422e52711ef0a7aa1c6a1f9c0fd1999) on the lab branch (do not reset unrelated commits without first reviewing branch differences).

**Automated evidence:** [GitHub Actions 39506646986](https://github.com/pratikto/PhotoBooth/actions/runs/39506646986) on commit `e7365b6f761ce55855ce0ca4ff54d2c13df449e6`: **compile PASS**, **50 unit/static tests PASS**, **5 real Tk runtime smoke tests PASS** using Ubuntu Python 3.12/Pillow and Xvfb. Tests cover ranked deterministic 1-bit candidates, cancellation, score fidelity, independent Floyd-only Apply with Sync ON, candidate JSON save without apply and baseline 3-lane GUI. **Windows GUI layout and printed thermal-photo quality remain unverified** until operator review.

## Three-panel GUI — local enhancement controls (2026-10-21)

The **Enhanced Floyd (experimental)** checkbox now sits **inside the Floyd–Steinberg panel**, directly below the preview/output metadata and above the Brightness slider, mirroring the **Enhanced Dizzy (experimental)** checkbox inside the Dizzy panel. The global/top toolbar no longer contains a Floyd enhancement toggle. Bayer has no enhancement checkbox.

Each checkbox affects **only its own algorithm**; `Sync Parameters` continues to synchronize brightness/contrast/gamma/sharpness slider adjustments only. Save/Load All Configs persists both flags independently (schema v4); Reset sets both OFF. The 1-bit raster, Floyd/Dizzy preprocessing, preview scaling, output file naming, physical Print Test behavior and printing defaults are **unchanged**.

**Automated regression evidence:** [GitHub Actions 39505103668](https://github.com/pratikto/PhotoBooth/actions/runs/39505103668), commit `8cdc2b50a3a5220c839805cf1d6a87155aa1815e`: **43 targeted unit/static tests PASS** and **3 actual Tk GUI runtime tests PASS** on Linux Python 3.12/Xvfb. Tk tests verify the checkbox belongs to the correct panel, click effects are lane-specific even with Sync enabled, Reset restores flags OFF, and Dizzy worker still renders 1-bit. Real Windows screen layout and photo printing are **not** physically validated by this CI.

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

**Verified automated evidence:** [Dither tuning lab CI 39503625894](https://github.com/pratikto/PhotoBooth/actions/runs/39503625894) at `f0df4e9937eba71d91888d17be7f969b2cf5a27a`: compile **PASS**, **42 unit/regression tests PASS**, plus **2 actual Tk GUI tests PASS** under Linux Xvfb (44 total). Tests cover v1/v2/v3 migrations, byte-identical Enhanced Floyd recipe, deterministic baseline/Enhanced Dizzy, GUI checkbox state/worker rendering, one-bit export and print metadata. This is **not a visual Windows acceptance test or thermal-paper quality certification**. The operator must still inspect actual Windows layout and printed image quality.

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

An opt-in **Enhanced Floyd (experimental)** checkbox is available **inside the Floyd panel** of `tools/dither_compare_gui.py`, immediately below the preview metadata; it was moved from the top toolbar to match Enhanced Dizzy in the Dizzy panel. It affects the Floyd lane only, and Enhanced Dizzy separately opts into the same preprocessing helper. Unchecked uses the byte-identical legacy baseline path; checked applies a 3x3 median noise filter, a 20% blend with gently autocontrasted grayscale, and restrained unsharp masking (radius 1.1, strength 55%, threshold 3), after the existing brightness/contrast/gamma/sharpness controls and before Pillow Floyd–Steinberg error diffusion. This is conservative *global* tonal processing, **not CLAHE, face-aware enhancement, or printer heat control**. Existing control values still matter and aggressive settings may degrade results.

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
