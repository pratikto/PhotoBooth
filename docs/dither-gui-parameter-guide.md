# Dither Comparison GUI — Parameter Guide

**Meong Photobooth | Operator reference | Updated 24 October 2026**

This guide explains **every visible parameter and action** in the existing
`tools/dither_compare_gui.py` laboratory GUI, what each control changes, what
you may see in a portrait, and when a setting can make a thermal print worse.

> **Scope and safety:** This is the offline **Dither Comparison Lab** on
> `feature/dither-tuning`, **not** the production Kivy kiosk. A preview or
> PNG export does not print. `Print Test` and `Print All` send **real paper**
> jobs only after the operator confirms. A better digital preview or higher
> Auto Tune score is **not** evidence of a better physical print.

## 1. Quick map of the GUI

The current window compares **three independent photo algorithms**:

| Panel | How the black/white pattern is made | Characteristics to examine |
| --- | --- | --- |
| **Floyd–Steinberg** | Propagates quantization error to neighboring future pixels. | Smooth perceived gradients and recognizable facial detail; possible fine grain. |
| **Bayer 8×8** | Uses a fixed 8×8 ordered threshold matrix. | Regular, repeatable dot texture; sometimes an obvious grid or pattern on skin. |
| **Dizzy Dithering** | Visits pixels in a pseudorandom permutation and distributes error to unprocessed neighbors. | Irregular dot texture with selectable neighborhood rules; relatively CPU-intensive. |

**Threshold** still exists in the backend and saved four-lane profiles for
compatibility, but **does not have a visible panel** in this GUI. Do not look
for a Threshold selector here.

**Processing order** (this matters when combining controls):

1. Open a source photo, composite transparency over white, and convert to grayscale.
2. Downsample with Lanczos **only if** source width exceeds the selected
   printhead width (384 or 576 dots); never enlarge a smaller image.
3. Apply **Brightness → Contrast → Gamma → Sharpness**, in that order.
4. Apply optional **Enhanced Floyd** *or* **Enhanced Dizzy** (only in its
   matching panel).
5. Apply optional **Smart Enhance**:
   median denoise → CLAHE → tone balancing.
6. For Dizzy only, optionally apply its **per-variant CPU Tone LUT**, then
   run the selected dithering algorithm.
7. Optionally apply **selective 1-bit post-processing** based on the
   pre-dither grayscale reference.
8. Display the preview or export the **native 1-bit raster**. Printing adds
   a separate labeled test header without changing photo pixels.

**Important distinction:** The global **Contrast** slider, Smart Enhance
**CLAHE Strength**, Smart Enhance **Tone Balance**, and Dizzy **CPU Tone LUT**
all affect tonal appearance, but they are different operations. They are not
interchangeable, and enabling everything can over-process faces.

## 2. Four manual sliders (available in ALL THREE panels)

**Neutral value is 1.00 for every slider.** All four can be adjusted
independently for Floyd, Bayer, and Dizzy. The ranges below are the actual
GUI limits, not recommended optimal values.

| GUI slider | Allowed / default | When increased | When decreased | Possible excessive-effect risk |
| --- | --- | --- | --- | --- |
| **Brightness** | `0.50–1.75` / **`1.00`** | Makes the whole photo lighter; may open up dark faces, clothing, and hair. Usually decreases the share of black dots. | Darkens faces and backgrounds; may help washed-out highlights. | Too high: pale/featureless faces and white clothing; too low: merged black hair/shadow regions. |
| **Contrast** | `0.50–2.50` / **`1.00`** | Separates light and dark regions; eyes, face outline, hair, and clothes may appear more pronounced. | Compresses highlights/shadows toward a flatter midgray; useful for harsh lighting. | Too high: blocked shadows, clipped highlights, harsh skin transitions; too low: weak facial definition. |
| **Gamma** | `0.30–3.00` / **`1.00`** | **Above 1.00 brightens midtones** more than the endpoints; can reveal facial texture in a dark portrait. | **Below 1.00 darkens midtones**; can restore density in overly bright skin. | High gamma washes out skin and midtone detail; low gamma merges facial shadows and hair. |
| **Sharpness** | `0.00–3.00` / **`1.00`** | Strengthens edges around eyes, eyelashes, hair, collars, and fine contours. | Softens edges; at 0 becomes notably blurred. | High values can amplify sensor noise, halos and jagged thermal dots; too low erases fine facial details. |

**Brightness vs Gamma:** Brightness scales the overall image intensity;
Gamma changes the midtone transfer curve. If only the **face midtones** are
too dark but the background is acceptable, try a small Gamma increase
before aggressively raising Brightness.

**Contrast vs Sharpness:** Contrast changes tonal separation;
Sharpness changes local edge emphasis. Extra sharpening does **not**
recover details that have already clipped to pure white or black.

### A practical way to adjust

Start from `1.00 / 1.00 / 1.00 / 1.00`. Change **one slider at a time**,
with small increments, on the same photo. Start with tonal fixes, then add
sharpening last. The “right” direction is conditional on the photo, paper,
printer darkness/speed and ambient lighting; there is no universal recipe.

## 3. Algorithm-specific controls

### 3.1 Enhanced Floyd (experimental) — Floyd panel only

- **Type:** ON/OFF checkbox; **default OFF**.
- **What it does:** after the four manual tonal sliders, applies a fixed
  **3×3 median filter**, a gently blended **autocontrast** adjustment, then
  **Unsharp Mask** (radius 1.1, percent 55, threshold 3). There are **no
  separate sliders** for this fixed recipe.
- **Potential improvement:** removes small noise while recovering some
  contrast and definition before Floyd's error diffusion; useful for soft
  portraits and hair/eye details.
- **Risk:** skin can look artificially textured or edges can get harsh. If
  Smart Enhance is also ON, some denoising/contrast operations run **twice**
  in sequence; more processing is not automatically better.
- **Compare:** check OFF vs ON while leaving the four sliders unchanged.

### 3.2 Enhanced Dizzy (experimental) — Dizzy panel only

- **Type:** ON/OFF checkbox; **default OFF**.
- **What it does:** uses the **same fixed median + mild autocontrast +
  Unsharp Mask** preprocessing recipe as Enhanced Floyd, but passes the
  result to the selected Dizzy variant.
- **Potential improvement:** clearer outlines and less image noise before
  Dizzy's randomized error diffusion.
- **Risk:** enhanced edges may turn into obvious hard-dot boundaries;
  combining with high Sharpness or Smart Enhance may over-sharpen.
- **Not the same as Tone LUT:** this changes local texture and contrast;
  the Dizzy CPU Tone LUT aims to correct the algorithm's grayscale
  dot-density response.

### 3.3 Dizzy variant — top toolbar, Dizzy only

| Variant | Neighbors and weights | Visible tradeoff |
| --- | --- | --- |
| **`article-8`** (**default**) | Four orthogonal neighbors, weight **1.0** each; four diagonal neighbors, weight **0.1** each; normalize among still-unprocessed neighbors. | A more distributed irregular dot texture and usually a less extreme digital tonal distortion than `orthogonal-4` in the project's fixed-seed synthetic tests. |
| **`orthogonal-4`** | Four orthogonal neighbors only, equal weight. | Different grain/clustering and potentially more aggressive tone response without correction; the look may still suit some photos. |

Changing this selection affects only the **Dizzy** panel. Neither choice
is inherently the best on every face or paper. These are both
**CPU** algorithms; `orthogonal-4` is **not** a Layered GPU implementation.

### 3.4 Dizzy CPU Tone LUT (experimental) — Dizzy panel only

- **Type:** ON/OFF checkbox; **default OFF**.
- **What it does:** applies a **separate inverse grayscale-response lookup
  table** to each Dizzy variant's grayscale input **before** pixel
  quantization/error diffusion. It compensates for the tendency of
  uncorrected Dizzy to make dark zones too dark and light zones too light.
- **Potential improvement:** a more faithful average proportion of
  white/black dots for skin midtones, shadows and highlights.
- **What it does NOT do:** remove background noise, sharpen eyes, perform
  CLAHE, or calibrate a real printhead/thermal paper.
- **Risk:** the digital LUT was derived from **96×96 uniform-gray patches,
  seed 42**. It may behave differently on other seeds, sizes, portrait
  textures or after other enhancements. The printed result may look
  smoother or simply different rather than objectively better.
- **Evidence:** with all 256 grayscale levels on the calibration grid,
  measured mean absolute digital white-dot error improved by about
  **93.4% for `article-8`** and **96.4% for `orthogonal-4`**.
  These are **not physical photo-quality percentages**. See the
  [Dizzy staged audit](dither-tuning-lab.md) and
  [CI calibration plots](https://github.com/pratikto/PhotoBooth/actions/runs/40043510521/artifacts/12539824481).
- **Best comparison:** keep the same variant, seed, photo and other
  parameters, and compare **Tone LUT OFF vs ON**.

### 3.5 Dizzy Seed — displayed label (not an editable slider)

- **Default:** `42`, shown as `Seed: 42`.
- **Purpose:** selects a deterministic visit order/pixel arrangement.
  Different seeds can redistribute the dot texture while keeping the
  intended image content broadly similar.
- **Visibility:** **read-only in the current GUI**; it can be retained
  when loading an appropriately validated lab profile, but the GUI
  currently has no seed editor or randomize button.
- **Practical effect:** do not treat the seed as a brightness control.
  Hold it fixed when comparing variants or tone correction, otherwise
  two variables change at once. Auto Tune starts from its neutral seed.

### 3.6 Bayer 8×8 — no special checkbox

The Bayer panel uses the **fixed ordered 8×8 threshold pattern**. Its
editable image controls are the four tonal sliders and the shared optional
Smart Enhance/Post-Processing controls. There is no Floyd/Dizzy-specific
enhancement checkbox or seed field in this panel.

## 4. Quick Processing A/B — per-panel dropdown

This dropdown switches **only two processing enable flags** for the
chosen algorithm. It **does not reset** the manual sliders, the Enhanced
Floyd/Dizzy checkbox, the Dizzy variant, or the Dizzy CPU Tone LUT.

| Preset label | Smart Enhance | 1-bit Post-Processing | What to compare |
| --- | --- | --- | --- |
| **Original** | OFF | OFF | Current algorithm + all other already-active settings, **not** necessarily a completely neutral photo. |
| **Smart Enhanced** | ON | OFF | Grayscale preprocessing alone. |
| **Smart + Post** | ON | ON | Grayscale preprocessing plus selective cleaning of the final 1-bit dots. |
| **Post Only** | OFF | ON | Cleaning only, using grayscale after the other selected tonal/Enhanced controls. |

The dropdown **preserves all strength values** under Image Processing
Options. The individual Smart Enhance and Post-Processing checkboxes
can be used instead; the dropdown updates to reflect them.

**A common misunderstanding:** Selecting **Original** does **not** switch
off Enhanced Floyd/Dizzy, Tone LUT or non-neutral Brightness/Contrast/
Gamma/Sharpness. For a truly unmodified-lab baseline use **Reset**, then
reselect the required print width if needed.

## 5. Smart Enhance and its three advanced sliders

**Smart Enhance (optional):** ON/OFF per panel, **default OFF**.
It is a grayscale **preprocessing stage**, performed **before** dithering.
Expand **Image Processing Options ▸** in the relevant panel to edit its
three controls. When Smart Enhance is OFF, their saved numeric values
do not affect the pixels.

| Advanced control | Range / stored default | Increase or enable → possible benefit | Excessive-setting risk |
| --- | --- | --- | --- |
| **CLAHE Strength** | `0.00–1.00` / **`0.35`** | Increases **local** tonal separation within image regions. Can reveal shaded facial features, hair strands, clothing folds and small contrast differences. `0.00` disables this CLAHE stage even with Smart Enhance ON. | Emphasizes noise, blemishes, uneven skin shading, and visible tile/texture artifacts; may make an otherwise smooth face look harsh. |
| **Median Denoise** | **`0, 1, 2`** / **`1`** | Runs a **3×3 median filter** 0, 1, or 2 passes. Can reduce salt-and-pepper/sensor noise that otherwise turns into unwanted dither dots. | At 2, freckles, eyelashes, fine hair or small text-like details may be softened or removed. `0` preserves original texture. |
| **Tone Balance** | `0.00–1.00` / **`0.20`** | Blends in gently histogram-stretched **global autocontrast** (cutoff 1%). Can use more of the black-to-white range when lighting is flat. `0.00` disables this stage. | Too much may crush dark hair, blow out highlights or exaggerate changing light levels between shots. |

**CLAHE vs Contrast:** CLAHE adjusts contrast **locally** (separate
regions blended across their boundaries), whereas the ordinary Contrast
slider operates more globally. A high value for both can make skin
look blotchy and cause small shadows around the eyes to darken.

**Processing cost:** this implementation uses **Pillow/Python**, not a
GPU model. Increasing CLAHE on a large image and combining it with
Dizzy can increase CPU time; **SBC performance has not been certified**.

## 6. 1-bit Post-Processing and its two advanced sliders

**1-bit Post-Processing (optional):** ON/OFF per panel, **default OFF**.
This stage operates **after** dithering, on already-black/white raster
pixels. It consults a grayscale reference to **protect normal midtone
halftone dots**, so it is *not* generic erosion/dilation across the
whole photo. Its controls live under **Image Processing Options ▸**.
When the stage is OFF, their stored numeric values have no effect.

| Advanced control | Range / stored default | Increase → possible benefit | Excessive-setting risk |
| --- | --- | --- | --- |
| **Selective Dot Cleanup** | **`0–3`** / **`1`** | Replaces some isolated 1-bit specks using a 3×3 majority/mode operation, but **only in near-white or near-black source regions with little local variation**. Can clean distracting dots in an otherwise solid paper-white background or black area. | At 3, more extreme-tone pixels are eligible, so tiny legitimate black/white features can disappear. Midtone texture is generally protected. |
| **Edge Refinement** | **`0–3`** / **`1`** | Anchors binary pixels along **strong grayscale edges close to black or white**. Can reinforce selected edges around glasses, silhouettes or high-contrast facial features. | At 3, may produce hard/unnatural contours, harsher skin boundaries, or loss of delicate edge texture. It is not universally beneficial. |

For both controls, **`0` disables that individual operation**, even if
1-bit Post-Processing is enabled. Higher numbers are **more aggressive**,
not a quality score. Post-processing is applied to the **photo raster
only**, not to separately added test-print headings, QR codes or
application UI text.

## 7. Global toolbar and display controls

| Control | Choices / default | What it actually changes |
| --- | --- | --- |
| **Open Image** | PNG, JPG/JPEG, BMP, WebP | Replaces the sample/photo source for all three panels. The small SOURCE IMAGE thumbnail is for inspection only; rendering uses the loaded original, subject to native-width downsampling. |
| **Width** | **576 dots** (default), **384 dots** | Maximum **print raster width** for all panels and the hidden stored Threshold lane. Choose based on your printer's **actual dot width**, not only the paper roll label. A smaller width discards some fine facial/hair detail when downsampling. |
| **Sync Parameters** | OFF (default) / ON | When ON, a manual change to **Brightness, Contrast, Gamma or Sharpness** in one panel copies that value to the other two visible panels. It **does not sync** Enhanced flags, Tone LUT, Dizzy variant/seed, Smart/Post enable flags or advanced values. Auto Tune **Apply** still changes just its own lane. |
| **Dot zoom** | **1×, 2× (default), 4×** | Enlarges a **small central crop** of native dots with nearest-neighbor scaling. It changes **only the inspection view**, not photo pixels, export dimensions, printer resolution or print darkness. |
| **SOURCE IMAGE** | Thumbnail + filename | Displays the loaded source identity. It is not the print-resolution image. |
| **Black %** | Measured after rendering | Percent of native raster pixels that are black. Useful for comparing coverage/paper usage, **not** the printer's darkness setting or a calibrated image-quality score. |
| **Ready … ms** | Per-lane status | Shows latest render state, selected Dizzy variant/seed/Tone LUT state (where applicable) and approximate render time. Not an SBC throughput benchmark. |

**Width clarification:** `576 dots` and `384 dots` do **not** mean
576 dpi and 384 dpi. They are the number of printable dot columns across
the photo. Physical thermal-dot pitch and darkness are set by the actual
printer/driver; this GUI does not calibrate them.

## 8. Buttons that save, tune, and print

| Button | Behavior and effect | Safety/interaction detail |
| --- | --- | --- |
| **Auto Tune** (each panel) | Runs an offline, bounded search on that algorithm for a group of candidate tonal and optional processing settings; Dizzy candidates also consider variants and Tone LUT ON/OFF. | Starts from **system-neutral settings**, **ignoring your current manual slider values**. A score is a digital proxy combining reconstructed grayscale, edge differences and black coverage; it is **not** a physical print-quality grade. |
| **Cancel Tune** | Appears on the active panel while Auto Tune is running. | Cancels/discards its pending results without modifying current GUI settings. |
| **Apply Best** | Applies the first ranked candidate in the Auto Tune dialog. | Changes **only the selected algorithm's settings**; even with Sync Parameters ON, it does not synchronize other lanes or print. |
| **Apply Selected** | Applies the candidate whose radio option you selected. | Same one-lane safeguard; compare its preview and settings first. |
| **Save Selected Preset** | Writes a full, four-lane **lab-only JSON v6**, substituting the selected candidate in its own lane. | **Does not apply it** to the live GUI. Load later using **Load All Configs**. |
| **Close** (candidate dialog) | Closes candidate comparison. | **No apply and no print.** |
| **Save PNG** (each panel) | Exports the currently rendered **native 1-bit PNG**, without a printer header. | Filenames distinguish algorithm, Dizzy variant/seed, Enhanced, Tone LUT, Smart and/or Post flags. Only ready/latest rasters can be saved. |
| **Export 3 PNG** | Writes the three currently ready panel rasters to a selected folder. | No print; may overwrite same-named exports in that folder, so use an A/B-specific destination. |
| **Save All Configs** | Writes all four validated lanes, including hidden Threshold, to lab JSON **schema v6**. | Does not print or automatically update kiosk printer settings. |
| **Load All Configs** | Loads a valid lab preset; supports earlier schemas **v1–v6**. | Restores each lane's settings and requires consistent paper width across lanes. Old files load new flags as OFF. |
| **Reset** | Restores all algorithm controls to their default profile values, including switches, Dizzy variant/seed, and Width 576. | Does **not** replace the currently open source image. Make a saved config before Reset if you want to preserve a tuned recipe. |
| **Print Test** (each panel) | Sends **one real paper job** for that algorithm using exactly the native ready 1-bit raster, plus a separate parameter header. | Requires configured printer settings and an explicit yes/no confirmation. It is not a simulated print. |
| **Print All (3 jobs)** | Sends **three separate real paper jobs**, one per visible algorithm. | One confirmation covers the batch; remaining jobs stop on failed/uncertain delivery. Uses paper, so check the current settings first. |

**Test-print header — Threshold visibility:** The physical **Print Test**
header includes a `THRESHOLD: <value>` line **only if the raster was produced
with the global `threshold` algorithm**. It is **not** shown for
Floyd–Steinberg, Bayer 8×8, or Dizzy because their output does not use
the profile's global threshold setting. This is a **header-only change**;
it does not adjust the dither calculation, native 1-bit photo raster,
printhead darkness, or existing JSON presets.

**Candidate-screen terms:**

- **Score /100:** a *relative* digital heuristic; higher is preferred
  within its search, but is not printer calibration or a guarantee.
- **Vs neutral:** the score difference from that algorithm's
  system-neutral comparison recipe, not necessarily your current sliders.
- **Tonal error:** grayscale mismatch after box-averaging the dot raster
  (lower tends to preserve large-scale tone better).
- **Edge error:** coarse edge/structure mismatch against the source
  (lower is better for that metric; it does not score facial aesthetics).
- **Black dots:** the raster's black-pixel percentage, not thermal
  head temperature or guaranteed optical darkness.
- **Three candidate previews:** intentionally include different
  processing possibilities for a human to review; they are not
  guaranteed to be the three visually best physical prints.

## 9. Which parameter should I adjust for a specific problem?

| Symptom seen on a real photo/print | First thing to try | What could go wrong |
| --- | --- | --- |
| Face too dark, but white background looks fine | Slight **Gamma increase above 1.00**; compare with a small Brightness increase. | Too much gamma makes highlights/pale skin disappear. |
| Entire photo too dark | Small **Brightness increase**, then reconsider Contrast. | Washed-out forehead, teeth, white clothing. |
| Face washed out / too white | Slight **Gamma decrease below 1.00** or lower Brightness. | Shadows and hair may become too dark. |
| Hair/shadow regions merge into solid black | Reduce **Contrast** or raise **Gamma** slightly; for Dizzy compare **Tone LUT ON**. | Decreasing contrast too far flattens eyes/nose and background separation. |
| Skin tones look flat; eyes lack separation | Mild **Contrast** increase, then test modest **CLAHE Strength**. | Skin pores/noise can become prominent. |
| Strong sensor grain or random dark specks | Turn on **Smart Enhance** and use **Median Denoise 1**. | Eyelashes, eyebrows and fine hair may soften. |
| Soft facial outlines | Very modest **Sharpness increase**, or compare Enhanced Floyd/Dizzy ON vs OFF. | Halos, jagged outline, crunchy dot texture. |
| Isolated dots in nearly blank white background | Enable Post-Processing and try **Selective Dot Cleanup 1**. | Valuable small details in extreme-tone areas may be erased. |
| Strong black/white contours appear broken | Test **Edge Refinement 1** vs OFF. | Hard or unnatural silhouettes at higher levels. |
| Dizzy shadow/highlight tone seems exaggerated | Compare **Dizzy CPU Tone LUT ON vs OFF** with unchanged variant and seed. | LUT can change the aesthetic of textured real photos despite synthetic-tone gains. |
| Regular checkerboard-like pattern | Compare **Bayer 8×8 vs Floyd/Dizzy**. | Another algorithm may have finer grain or take longer to render. |
| Photo prints narrower or with less detail than expected | Verify **Width 384/576** matches printer specifications and source size. | Choosing a width above the printhead's actual capability can fail or crop. |

These are **diagnostic experiments**, not automatic fixes. Always keep the
same photo and paper for comparisons.

## 10. Suggested operator test sequence (thermal portrait)

1. **Match the printhead width.** Open an actual portrait under your
   booth's lighting conditions, preferably with both shadowed hair and
   bright skin/highlights. Do not use only the synthetic sample.
2. **Start neutral:** press **Reset**, set width correctly, leave all four
   tonal sliders at 1.00, turn Enhanced Floyd/Dizzy OFF, Tone LUT OFF, and
   choose **Original** (Smart/Post OFF). Export the three baseline PNGs
   to a separate folder.
3. **Assess the dominant defect:** if it is global darkness, start with
   Brightness; midtone shadows, Gamma; missing tonal separation,
   Contrast; weak edges, a mild Sharpness increase. Change **one**
   slider per comparison. Keep **Sync Parameters OFF** for different
   per-algorithm experiments; turn it ON only when intentionally
   applying the same tonal slider change to all three.
4. **Compare preprocessing:** for each algorithm separately, switch
   **Original → Smart Enhanced**. Try **Median Denoise 1, CLAHE 0.20,
   Tone Balance 0.10** as *illustrative experimental starting values*,
   **not validated defaults**. Compare this against its original
   stored slider values, then change only one advanced strength.
5. **Check double preprocessing:** compare Enhanced Floyd/Dizzy alone,
   Smart Enhance alone and both together. If both look over-processed,
   prefer the simpler option; do not assume the combination is best.
6. **Dizzy-specific A/B:** use one variant/seed, with Enhanced and
   Smart/Post unchanged, and export **Tone LUT OFF** and **ON**. Then
   compare `article-8` vs `orthogonal-4` as a **separate** experiment.
7. **Try Post last:** compare **Smart Enhanced vs Smart + Post**
   (or Original vs Post Only), starting with Dot Cleanup 1 and
   Edge Refinement 1. Check the native 1-bit crop, not just the
   downscaled preview.
8. **Optional Auto Tune:** run it per algorithm. Compare its three
   suggestions with your manual versions; **Apply Selected** only if
   you prefer it. An algorithm can rank well digitally but print worse.
9. **Export, then test paper:** save native PNGs and the v6 lab config,
   and only then confirm **Print Test**. Keep the same roll, printer
   speed/darkness and viewing distance. Examine eyelashes, face
   identity, hair/shadows, highlights and background specks.
10. **Record your winner:** note photo, dot width, printer/paper,
    parameter recipe, chosen algorithm/variant, Tone LUT state,
    printed result and print duration. Keep separate A/B folders.
    Do not promote a lab preset to the production kiosk without
    explicit approval.

### What is a real baseline?

The code's **saved default values** for Smart sliders are
CLAHE `0.35`, Median Denoise `1`, Tone Balance `0.20`;
for Post they are Dot Cleanup `1` and Edge Refinement `1`.
**Those nonzero values have NO effect while their matching checkbox
is OFF.** Choosing **Original** merely turns off Smart/Post. To
compare an entirely default recipe, Reset also restores the
manual sliders, Enhanced checkboxes and Tone LUT state.

## 11. Interpretation limits, preset compatibility and source code

- **On-screen previews are not print calibration.** The big preview uses
  **BOX** downscaling that blends white/black dots into display grays.
  The small central dot crop uses **nearest-neighbor** magnification.
  These are display-only transformations. **Save PNG** uses the native
  mode-1 raster without re-dithering.
- **Digital grayscale calibration is not physical paper calibration.**
  Temperature, printhead, thermal sensitivity, moisture, speed, dot gain
  and printer darkness settings can all change perceived output.
- **No universal best settings.** Bright skin, black clothing,
  eyeglasses, fluorescent lighting, high ISO noise and camera focus
  require different tradeoffs; do not assume higher settings are better.
- **Resource constraints.** CLAHE is implemented in Pillow/Python,
  and CPU Dizzy is relatively heavy. Measure real SBC response before
  enabling expensive combinations in a kiosk.
- **Lab-only schema v6.** Old v1–v5 JSON profiles load with newer
  optional stages disabled. Saving a JSON config or applying a candidate
  does not change the kiosk's live production printer configuration.
- **Hidden Threshold:** this legacy profile has a backend `threshold`
  integer (0–255; default 128), but there is **no Threshold slider or
  print panel** in the current three-way comparison GUI. It is saved
  for compatibility only.

**Source-of-truth code:** [GUI](../tools/dither_compare_gui.py),
[profile + pipeline](../photobooth/dither_lab.py),
[Smart/Post routines](../photobooth/dither_processing.py),
[Dizzy implementation](../photobooth/dizzy_dither.py),
[CPU Tone LUT](../photobooth/dizzy_calibration.py),
[Auto Tune](../photobooth/dither_autotune.py), and
[test-print path](../photobooth/dither_print.py).

**Related documents:** [Dither Tuning Lab development and test history](dither-tuning-lab.md)
and [test checklist](test_checklist.md).

### How to open the lab on Windows

```powershell
git fetch origin
git switch feature/dither-tuning
git pull --ff-only origin feature/dither-tuning
python tools/dither_compare_gui.py
```

**Do not change the production Kivy photobooth, merge to `master`, or
automatically print based solely on a digital-score recommendation.**
