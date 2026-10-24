## FEAT-011 Dizzy CPU — Stage 2 grayscale fidelity (2026-10-24)

- [x] Full 0..255 input grayscale scan for both CPU Dizzy variants.
- [x] Native mode-1 white-dot fraction measured before/after Tone LUT.
- [x] CSV per-tone results, machine-readable JSON MAE/worst cases,
      and standalone SVG grayscale response graphs.
- [x] GitHub Actions generates downloadable fidelity artifacts and checks
      corrected error is lower than baseline on the 96x96 seed42 calibration.
- [ ] Inspect curves across second seed, printhead widths, and real portraits.
- [ ] Compare on thermal paper using the same printer darkness and speed.


## FEAT-011 — Smart Enhance & 1-bit Post-Processing (2026-10-23)

**Branch:** `feature/dither-tuning`. **No master merge; no Kivy production
print pipeline changes.** Verified reference [GitHub Actions run 39973139694](https://github.com/pratikto/PhotoBooth/actions/runs/39973139694)
(commit `6f2c537952c9a0c4821b00f5aa7e84342a051cbb`):
**compile PASS**, **64 backend/static tests PASS** and **11 Tk GUI/Xvfb tests
PASS** (Linux, Python 3.12, Pillow), including the latest A/B presets, raster
byte-preservation, schema v1-v5 loading, Smart candidate coverage, no paper
printing on UI toggles, and 1-bit print-test header labeling.

- [x] Existing three-lane GUI; no new GUI to launch.
- [x] Separate per-lane Smart Enhance and guarded 1-bit Post-Processing.
- [x] One-click Original / Smart Enhanced / Smart + Post / Post Only presets.
- [x] Collapsible advanced sliders; reset/manual Save/Load/Auto Tune retained.
- [x] 1-bit native PNG and test print reuse the same photo raster; auto search
      never calls the printer; optional processing defaults OFF.
- [x] Full-lab/preset JSON schema v5; older v1-v4 opens with stages OFF.
- [x] Auto Tune considers processing options, preview and Apply modify only
      selected lane with Sync Parameters ON.
- [ ] **Windows screen review:** pull this branch, launch
      `python tools/dither_compare_gui.py`, resize to 1050×620 and maximize.
      Confirm all 3 panels, fixed Print Test/Save PNG/Auto Tune buttons,
      horizontal toolbar and mouse-wheel-scrolling advanced controls.
- [ ] **Manual A/B test:** open the same photo at 576 dots; choose Original,
      then Smart Enhanced, then Smart + Post for each algorithm. Check
      preview differences, full-resolution PNG pixel size, save filename
      suffix and default restoration by Reset. Repeat with 384 dots.
- [ ] **Auto Tune UI test:** start/cancel each lane, review 3 candidates and
      Smart/Post labels; Close without applying, then Save Selected Preset
      and reload. Apply Selected with Sync ON and confirm other lanes
      unchanged; verify no real printer job was created by tuning.
- [ ] **Real thermal paper:** use explicit Print Test confirmation for the
      three combinations with constant paper, darkness, speed and source.
      Assess facial detail, highlights, hair, noisy background and any
      missing halftone dots. Treat heuristic scores as advisory only.
- [ ] **SBC performance acceptance:** test CPU peak/memory/render latency on
      actual hardware before considering adoption beyond the lab.
- [ ] **Production integration decision:** hold until operator compares
      physical prints and explicitly approves rollout.


## FEAT-011 — Auto Tune Enhanced Floyd (2026-10-21)

## Independent Auto Tune GUI — 2026-10-23

FEAT-011: manual sliders retained; Auto Tune uses fixed system search independent
of manual values, with explicit Apply. 53 local regressions and compile PASS;
Tk/Windows/physical acceptance pending. Prior manual-seeded behavior is superseded.
See [current lab workflow and validation](dither-tuning-lab.md#independent-auto-tune-gui--2026-10-23).
Publication remains pending after the previous automatic approval rejection.


## Auto Tune continuation — 2026-10-22

- Owner-authorized FEAT-011 improvement; baseline `26964d8`.
- Local Linux / Pillow 12.3.0: `python -m unittest tests.test_dither_lab tests.test_dither_comparison tests.test_dither_print tests.test_dither_gui_layout tests.test_dizzy_dither tests.test_dizzy_lab_integration tests.test_dither_enhanced tests.test_dither_autotune -q`: **53 PASS**. Compile checks PASS.
- New coverage: small midtone halftone fidelity, exact baseline enhancement ON/OFF, neutral fallback from extreme sliders, search budget, invalid profile type. Existing determinism/cancellation/export tests retained.
- Tk runtime: pending GitHub CI; local display/Xvfb unavailable. Windows layout and printer-paper acceptance NOT RUN.
- Operator: compare manual vs selected candidate with same photo/paper/width/heat; verify signed delta, no automatic Apply/print, cancellation, and Save/Load. Scores are not physical quality certification.


- **Owner-approved implementation scope:** existing `feature/dither-tuning` only. Optional Auto Tune on Enhanced Floyd with bounded parameter search, three digital-fidelity-ranked native 1-bit candidates, explicit Apply Best/Apply Selected/Save Selected Preset, unit/UI test coverage and documentation. No change to production kiosk or `master`; no unattended paper printing.
- **Implementation:** `photobooth/dither_autotune.py` (bounded, deterministic offline search; max 25 reduced-resolution settings plus 8 native-dot finalist evaluations; source-relative fidelity/edge/black-coverage heuristic); `tools/dither_compare_gui.py` (cancelable background worker, safe Tk event queue, generation-token cancellation on source/Floyd changes, three-candidate preview dialog, explicit Floyd-only Apply and schema-v4 full-lab preset Save). Baseline Floyd/Dizzy/Bayer render math remains intact.
- **Code commits:** [engine `f0ac68b`](https://github.com/pratikto/PhotoBooth/commit/f0ac68b6fe18e63a1ea6bd0bac46afae5e01fd4b), [GUI `3d82d1b`](https://github.com/pratikto/PhotoBooth/commit/3d82d1b6949679c0e4db34235a4310f1ec27a330), [algorithm tests `68ddaa8`](https://github.com/pratikto/PhotoBooth/commit/68ddaa8b9106c1f1ade50a66d21528fce755a96e), [CI `5c549ba`](https://github.com/pratikto/PhotoBooth/commit/5c549ba69d8862e24f7cb7580510d367547babed), [real Tk tests `e7365b6`](https://github.com/pratikto/PhotoBooth/commit/e7365b6f761ce55855ce0ca4ff54d2c13df449e6).
- **Final verified CI evidence PASS:** [run 39507090626](https://github.com/pratikto/PhotoBooth/actions/runs/39507090626) at SHA `ddbc9da7176f4fb625d19dea89c55d0ee85e7795`, Ubuntu Python 3.12/Pillow + Xvfb: **compile PASS, 50 targeted unit/static tests PASS, 5 real Tk runtime tests PASS, 0 failures**. Tested deterministic candidate ranking, cancellation, Floyd-only Apply with Sync enabled, native 1-bit rendering and save/reload of a full comparison v4 JSON without applying it. Earlier intermediate run [39506884044](https://github.com/pratikto/PhotoBooth/actions/runs/39506884044) failed because the GUI test expected the previous individual-profile format after the Save Preset UX switched to reloadable comparison JSON; corrected by commit [`8cd1937`](https://github.com/pratikto/PhotoBooth/commit/8cd1937cfb7a81b88ff1160d9a85c1de6acc43b7) and subsequent CI runs passed. **Windows monitor/physical printer acceptance remains outstanding.**
- [ ] **Windows run:** `git fetch origin`; `git switch feature/dither-tuning`; `git pull --ff-only origin feature/dither-tuning`; `python -m unittest tests.test_dither_lab tests.test_dither_comparison tests.test_dither_print tests.test_dither_gui_layout tests.test_dizzy_dither tests.test_dizzy_lab_integration tests.test_dither_enhanced tests.test_dither_autotune -v`; `python tools/dither_compare_gui.py`. Record local SHA, test count and screenshots at default/minimum/full-screen scaling.
- [ ] **Auto Tune interaction:** with a portrait loaded at 576 dots, click Auto Tune in Floyd panel; cancel once via Cancel Tune, then run again. Verify interface stays responsive, progress updates, exactly three scored candidate previews appear, and none automatically changes the Floyd sliders/prints/saves.
- [ ] **Selection/saving:** Save Selected Preset and confirm reloadable four-lane v4 JSON contains Enhanced Floyd/slider values; close dialog without Apply and ensure manual settings unchanged; run again, choose a non-first candidate and click Apply Selected, then Apply Best in another run, verify only Floyd sliders/checkbox change even if Sync Parameters is checked. Re-render, Save All Configs and reopen; keep Bayer/Dizzy/hidden Threshold data intact.
- [ ] **Stale tasks:** start Auto Tune, change width/photo/Floyd slider before it finishes; ensure old candidate dialog never appears and old candidates cannot be applied. Source photo bytes remain unchanged. No printer job occurs until an explicit separate Print Test confirmation.
- [ ] **Paper-level A/B:** compare the previous best manually tuned Enhanced Floyd profile with Auto Tune #1 and #2 on the same picture/paper/printer and settings; judge facial detail, midtones, highlights, hair and print density; record settings, printed samples and operator preference. The highest numerical proxy score is **not guaranteed** to yield the best physical print.
- **Remaining blockers:** operator Windows GUI review, printer-specific quality calibration, physical thermal-photo acceptance (BUG-004 OPEN). No production integration approval or branch merge.

## FEAT-011 — Enhanced Floyd control moved into Floyd panel (2026-10-21)

- **Authorization and isolation:** the owner approved fixing the dithering test GUI to place Enhanced Floyd in the Floyd–Steinberg panel instead of the top toolbar. Only `tools/dither_compare_gui.py`, targeted GUI tests, and relevant lab documentation were changed on `feature/dither-tuning`. No `master` merge, production printing change or dithering math adjustment.
- **Source commits:** [GUI `bfeca1d`](https://github.com/pratikto/PhotoBooth/commit/bfeca1d3659eba6c13d4b7dd3028aa6cb32f2fbd), [Tk runtime regression `4195f3b`](https://github.com/pratikto/PhotoBooth/commit/4195f3b447469dcb1cb9986c9f23eb07700bcf11), [static layout checks `8cdc2b5`](https://github.com/pratikto/PhotoBooth/commit/8cdc2b50a3a5220c839805cf1d6a87155aa1815e).
- **GitHub CI PASS:** [run 39505103668](https://github.com/pratikto/PhotoBooth/actions/runs/39505103668) on `8cdc2b50a3a5220c839805cf1d6a87155aa1815e`: Python 3.12/Pillow on Ubuntu; compile **PASS**; 43 targeted unit/static tests **PASS**; 3 Tk/Xvfb runtime tests **PASS**. Runtime verifies Floyd checkbox has the Floyd panel as actual parent, Dizzy checkbox belongs to Dizzy panel, both are unique, clicking Floyd alters only Floyd even when Sync Parameters is active, Reset clears both flags, and baseline/enhanced raster behavior remains functional.
- [ ] **Windows UI acceptance:** pull the branch, launch `python tools/dither_compare_gui.py` and check 1050×620/minimized and maximized screens; toolbar has no Enhanced Floyd checkbox, Floyd/Dizzy panels show their own controls under the output/dot preview and before Brightness, Bayer shows no checkbox, and sliders/Print Test/Save PNG remain accessible when scrolling.
- [ ] Toggle Enhanced Floyd with Sync Parameters both ON and OFF; confirm Bayer/Dizzy do not change. Toggle Enhanced Dizzy; Save/Load All Configs then Reset; check both flags restore appropriately and output PNG / Print Test remains the same 1-bit raster for unchanged parameter values.
- **Not certified:** real Windows display, user-specific monitor scaling and printed thermal-paper visual quality. Operator confirmation remains necessary.

## FEAT-011 — Shared Enhanced Floyd + Enhanced Dizzy experiment (2026-10-21)

- **Approval/scope:** owner explicitly approved implementing opt-in Enhanced Dizzy in the **isolated** `feature/dither-tuning` lab, with GUI checkbox, tests and docs; no `master` merge or modification to the live Kivy/photo-QR printer route.
- **Code:** `photobooth/dither_lab.py` adds a shared non-default preprocessing function preserving Enhanced Floyd's original MedianFilter(3), 20% blended autocontrast, and UnsharpMask(1.1, 55%, threshold 3). Both Dizzy article-8 and orthogonal-4 use it only when `enhanced_dizzy=True`. `tools/dither_compare_gui.py` adds the Dizzy-only checkbox, reset/loading, status, native 1-bit PNG naming; `photobooth/dither_print.py` identifies the printed option without re-dithering.
- **Commits:** [core `108be4c`](https://github.com/pratikto/PhotoBooth/commit/108be4cf5e089e18fa22df36714ef56419c063be), [GUI `b6941b5`](https://github.com/pratikto/PhotoBooth/commit/b6941b56ea2e644872ad0f0d477d00337e75a9a8), [print label `9423381`](https://github.com/pratikto/PhotoBooth/commit/9423381e41987c5a36ae9a14d09f3941333d9991). Updated tests include `tests/test_dither_enhanced.py`; workflow now runs it alongside existing labs.
- **Verified CI result:** [Dither tuning lab regression 39503134534](https://github.com/pratikto/PhotoBooth/actions/runs/39503134534) at source/workflow SHA `80980f7ba3f7a8270b0d48ee4ec63f72ae5b9cbd`, Linux Python 3.12 + Pillow: **compile PASS; 42 tests PASS; 0 failures**. Tests include identical Enhanced Floyd raster reference, Dizzy baseline unchanged, Enhanced Dizzy on both variants, deterministic seed, strict per-lane flag validation, native print metadata, v1-v3 JSON migration with OFF default, and v4 round-trip. CI success does **not** imply real paper quality.
- **Later GUI runtime CI PASS:** [Actions run 39503625894](https://github.com/pratikto/PhotoBooth/actions/runs/39503625894), SHA `f0df4e9937eba71d91888d17be7f969b2cf5a27a` on Ubuntu Linux Python 3.12: previous **42 tests PASS** plus **2 new actual Tk GUI runtime tests PASS** using Xvfb, 0 failures. Smoke verifies checkbox presence, independent Dizzy-only state changes, reset, background worker finishes and native 1-bit baseline/enhanced output differs. No physical printer touched.
- [ ] **Windows application:** `git switch feature/dither-tuning`, `git pull --ff-only origin feature/dither-tuning`, `python -m unittest tests.test_dither_lab tests.test_dither_comparison tests.test_dither_print tests.test_dither_gui_layout tests.test_dizzy_dither tests.test_dizzy_lab_integration tests.test_dither_enhanced -v`, then `python tools/dither_compare_gui.py`. Capture exact branch SHA and PASS/FAIL/SKIP; Xvfb success is not a Windows GUI screenshot.
- [ ] Toggle Enhanced Dizzy OFF/ON, verify only the Dizzy pane changes, no stale raster can be saved/printed while rendering; repeat for article-8 and orthogonal-4; toggle and reset Enhanced Floyd separately.
- [ ] Save/load v4 profile with both flags ON. Import an existing v3 JSON and confirm Enhanced Dizzy defaults OFF with Floyd/seed/hidden Threshold values preserved. Export All produces exactly three 1-bit PNGs (Floyd/Bayer/Dizzy), with distinct baseline/enhanced Dizzy filenames.
- [ ] Test actual printer on the **same** original portrait, 576-dot width, paper and printer heat/speed settings: Dizzy baseline and Enhanced Dizzy with identical sliders/seed/variant, followed by Enhanced Floyd. Check labeled print header, skin, hair, shadows, QR/text quality and native raster parity; **explicit Print Test confirmation only**. No automated retries on uncertain send.
- **Acceptance remains pending** Windows UI and repeatable real-paper photos. No LUT/GPU or production integration approved.

## FEAT-011 — Hide Threshold comparison panel (2026-10-21)

- **Owner-approved scope:** remove Threshold from the standalone `tools/dither_compare_gui.py` display; keep Floyd/Bayer/Dizzy and retain the Threshold backend, lab JSON keys and legacy tools. Work restricted to `feature/dither-tuning`. GUI commit [`ad6b299`](https://github.com/pratikto/PhotoBooth/commit/ad6b299537791905ba79d27035eac6e27af92f2c).
- **Source checks and CI PASS:** `tests/test_dither_gui_layout.py` guards against a visible Threshold panel or accidental Print All/Export All output; `tests/test_dizzy_lab_integration.py` verifies visible modes, and `tests/test_dither_lab.py` verifies 370 px preview scaling. [Dither tuning lab GitHub Actions run 39499230120](https://github.com/pratikto/PhotoBooth/actions/runs/39499230120) on commit `d0c9cfaff10d9c18f1f3eb7d599661bcb4721ae4`: compile **PASS**, targeted regression **33 tests PASS**, 0 failures, Linux Python 3.12 / Pillow. Nonblocking Pillow `Image.getdata` deprecation warning persists in existing test code. The pass does **not** certify Windows Tk visuals or real printer output.
- **Final source/CI recheck:** [GitHub Actions run 39499411047](https://github.com/pratikto/PhotoBooth/actions/runs/39499411047) at commit `e12a93a5b9e4f0788fb204e689014c41e50e6705`: compile **PASS**, 33 targeted tests **PASS** (0 failures), including three-visible-panel assertions and neutral v3 preset default filename. Runs on Linux Python 3.12; hardware/UI acceptance remains unverified.
- [ ] Repeat `python -m unittest tests.test_dither_lab tests.test_dither_comparison tests.test_dither_print tests.test_dither_gui_layout tests.test_dizzy_dither tests.test_dizzy_lab_integration -v` on the Windows device and capture PASS/FAIL/SKIP.
- [ ] Launch `python tools/dither_compare_gui.py`; confirm three panels in order Floyd–Steinberg / Bayer 8×8 / Dizzy, no Threshold slider, 1050×620 and maximized layouts usable.
- [ ] Toggle Enhanced Floyd and Dizzy variant, adjust/sync sliders, change width 576 ↔ 384, then Save/Load All Configs; verify hidden Threshold profile remains in v3 JSON but never appears in GUI or gets printed by Print All.
- [ ] Export All produces exactly **three 1-bit PNGs**; individual Save PNG works for every visible algorithm; never outputs a Threshold PNG.
- [ ] With explicit physical-print confirmation, **Print All (3 jobs)** sends only Floyd/Bayer/Dizzy and retains stop-on-uncertain behavior; verify against actual printer (a spool success is not proof of printed paper).
- **Isolation:** production printer supports Threshold unchanged; `master` is not touched.

## FEAT-011 / Dizzy experiment — 2026-10-21

- **Source-only scope:** `feature/dither-tuning` (no `master` merge, no kiosk production print-mode modification).
- **Algorithm:** article-8 8-neighbor axial 1 / diagonal 0.1, and orthogonal-4 from follow-up, fixed seed 42, float error and five-round random permutation. Production `DITHER_MODES` unchanged.
- **Local isolated test evidence:** `PYTHONPATH=/mnt/data/dizzy_dev python -m unittest discover -s /mnt/data/dizzy_dev/tests -p 'test_dizzy_dither.py' -v`: **5 PASS**, zero FAIL, in container Python/Pillow. The test used the same prototype core code subsequently uploaded to GitHub; **not** full repository integration/GUI CI.
- **Synthetic performance snapshot:** 576x579 gray image: article-8 ~0.97 sec; orthogonal-4 ~0.65 sec on this execution container. Not a Windows benchmark.
- **GitHub test automation:** `.github/workflows/dither-lab.yml` updated to compile and run `tests.test_dizzy_dither`, `tests.test_dizzy_lab_integration`, and prior dither tests. Actual CI run status **not yet confirmed** by the tool; do not mark green until checked.
- [ ] Local Windows: `python -m unittest tests.test_dither_lab tests.test_dither_comparison tests.test_dither_print tests.test_dither_gui_layout tests.test_dizzy_dither tests.test_dizzy_lab_integration -v`.
- [ ] Open `python tools/dither_compare_gui.py`; verify three visible lanes at 1050px and maximized (Threshold hidden), no clipped preview, scrolling, sync, reset, JSON save/load v1/v2/v3.
- [ ] Same-photo A/B: Floyd baseline, Enhanced Floyd, Dizzy article-8 and orthogonal-4, and Bayer with same width and sliders; inspect exact exported 1-bit rasters.
- [ ] Physical printer only with operator permission: confirm each single Print Test, printed Dizzy variant/seed header, 3-job cancellation/uncertain-state stop, native 576-dot width, print quality and paper density.
- [ ] LUT calibration is **out of scope**: author LUT should not be copied onto a different uncalibrated variant.
- **Acceptance** pending repeatable Windows UI and actual printer-paper inspection, especially faces/hair/skin midtones and monochrome QR/text clarity.

## BUG-010 lab scroll issue — 2026-10-18

- Screenshot/owner confirmed missing access to lower sliders and print controls on Windows.
- Scope authorized: `feature/dither-tuning` GUI layout only. Independent scroll canvas and mouse wheel per lane, compact preview, sticky action buttons; no changes to native raster, printer jobs or kiosk.
- CI compile and static GUI structure tests are evidence of source consistency only; **Windows Tk visual interaction still needs owner retest**.
- [ ] On 1050×620 and maximized, Print Test and Save PNG visible; all three visible algorithms accessible; Threshold is no longer displayed.
- [ ] Mouse wheel/scrollbar affects only hovered algorithm; adjusting slider updates correct preview.
- [ ] Sync Parameters and Save/Load configurations still work; printing still requires confirmation.

## FEAT-011 Stage 1–3 incremental development — 2026-10-18

- Owner approved staged implementation + separate pushes on `feature/dither-tuning` only. **Stage 1** [`9f73f6e`](https://github.com/pratikto/PhotoBooth/commit/9f73f6e4223c98ebc883c70a604a4e47007fb054): independent 3-way config and JSON tests; initial CI **FAIL** due to accidental literal newline escaping in JSON writer. This was fixed in Stage 2.
- **Stage 2** [`15f87a7`](https://github.com/pratikto/PhotoBooth/commit/15f87a71041bd37958711fb0046f72a539323005): new standalone 3-column GUI with per-lane sliders, Sync Parameters, original image, center dot zoom, 1-bit exports, combined config load/save; [CI 39112358484](https://github.com/pratikto/PhotoBooth/actions/runs/39112358484) **PASS**.
- **Stage 3** [`03e7ddf`](https://github.com/pratikto/PhotoBooth/commit/03e7ddf2085f0b0e278b04957e03fbb9b24ee20c): Print Test per lane and Print All with explicit paper confirmation, snapshot of displayed one-bit output, labeled ESC/POS, existing queue/routes and stop-on-uncertain-result. [CI 39112474748](https://github.com/pratikto/PhotoBooth/actions/runs/39112474748) **PASS** (compile/unit tests, *not physical printing*).
- **Windows device QA PENDING:** startup at `python tools/dither_compare_gui.py`; side-by-side preview updates independently, Sync Parameters, rapid dragging, zoom, save/load same three profiles, export native 1-bit raster; physical Print Test each lane, Print All cancel and real output, queue configuration and hardware paper clarity; verify print header, confirm no duplicate retry; full kiosk regression remains separate. **BUG-004 is OPEN.**
- This test evidence is for the dedicated feature branch, not the customer kiosk or main branch.

# Meong Photobooth — Test evidence and regression checklist

**Reconciled: 2026-10-18 | Branch: `feature/kivy-gui`**

**Evidence policy:** `REPORTED-PASS` / `REPORTED-FAIL` = operator's actual on-device statement without a fully captured reproducible test record; `AUTOMATED-HISTORICAL` = earlier code/mock/video-fixture result; `UNVERIFIED` = not tested as part of this housekeeping. This document does **not** certify current build, hardware, payment, or production readiness. All unchecked boxes remain untested in the **current documented acceptance campaign**; they do not imply a failed test.

## Known evidence baseline (not a new test run)

| Item | Report/evidence | Classification | Bug / next proof needed |
| --- | --- | --- | --- |
| Windows USB photo-strip paper output | Owner saw completed photo layout printed | **REPORTED-PASS** for paper output *only* | BUG-004: assess resolution/dithering, actual image quality and page sizing |
| Windows thermal photo sharpness | Owner says layout print looks blurry / poor quality | **REPORTED-FAIL** | BUG-004: compare source PNG to native-dot raster and physical paper |
| Payment QR-slip physical print | Owner now confirms paper QR slip prints | **REPORTED-PASS** for physical output; scanning unverified | BUG-003: validate QR scan of DEMO payload |
| Application music/effects | Button/camera effects audible; tutorial/layout music silent while SDL2 claims `state=play gain=0.59`. Standalone music check audible | **REPORTED-PASS** for SFX and standalone; **REPORTED-FAIL** for in-app music | BUG-001: verify source retry with actual Windows speakers |
| Settings music/button tests | Owner confirms Music, Button and Camera `Uji` taps respond; Music only made default click, Button played click, Camera shutter | **REPORTED-PASS** touch/SFX; **REPORTED-FAIL** music audition | BUG-007: test newly isolated music/button/shutter samples and output on speakers |
| Video on idle and payment | Owner confirms both placements play moving video | **REPORTED-PASS** | BUG-002: ensure audio patch does not regress video and payment mute |
| Ad → tutorial → picker; enlarged ad stage | Owner confirms navigation and video sizing are satisfactory | **REPORTED-PASS** | BUG-005 / BUG-006: regression after UI changes |
| Existing native video/audio, unit/GUI and printer mock tests | Historical results are preserved in [FEATURE_STATUS.md](FEATURE_STATUS.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md), [QA docs](qa/README.md) | **AUTOMATED-HISTORICAL** | Do not mark on-device tests passed from these |
| Current branch test suite after documentation changes | No Python tests executed during docs housekeeping | **UNVERIFIED** | Run after future approved code changes |
| True QRIS payment settlement | No live payment gateway exists | **NOT IMPLEMENTED** | Never use demo `simulate_success` as production acceptance |

## Metadata required for each real device test

- Commit SHA / date / tester / OS / Python / Kivy / ffpyplayer versions:
- Exact machine ID and screen resolution:
- Camera model; active Windows sound output and mixer:
- Printer model, actual queue name, connection route, `data/printer_settings.json` (redact secrets), media width and darkness:
- Ad media file type/codec, local path and **whether the source video has an audio stream**:
- Commands and console log (redact customer photos/QRIS tokens), screenshots/physical paper evidence:
- Reproduction steps, expected outcome, actual outcome, pass/fail/blocked, bug ID and operator acceptance:

## High-priority on-device verification — bug closure

- [ ] **BUG-001:** Opening idle advertisement suppresses app music; after entering tutorial and layout music audibly plays *without opening Settings*. The post-fade full-gain restart and `Uji Musik` must be audible on Windows; test 0% mute, resume, cancellation and next customer. Check OS mixer/provider. `state=play` alone does not pass.
- [ ] **BUG-007:** On updated Windows GUI, confirm `Uji Musik` audibly restarts music WITHOUT a button click; `Uji Tombol` emits one click; `Uji Efek kamera` emits one shutter. Confirm separate diagnostic messages and persisted volume/mute.
- [ ] **BUG-002:** Local supported moving-image video plays on *idle* and *payment*. Payment video is muted; opening ad honors source soundtrack **only if the sample truly has audio**. Verify image fallback, EOS, page changes and no zombie video process.
- [ ] **BUG-003:** Payment `CETAK QR` uses saved Windows printer (same configured photo route), delivers actual paper with complete printed QR, captures worker/queue results, and the printed demo payload scans on a phone. Test expiry/reprint prompt without charging or extending the QR.
- [ ] **BUG-004:** Print controlled source strips using Floyd–Steinberg/Bayer/threshold; save originals, dot width, paper, darkness, print photo and human legibility/edge comparison. Verify no double scaling after dithering.
- [ ] **BUG-005:** Idle manual Start and accepted 5-second face invitation each open mandatory tutorial before layout picker. Confirm 15-second invitation dismiss/cooldown, back navigation and clean idle reset.
- [ ] **BUG-006:** Verify enlarged opening video at 800×600, 1200×800 and 1920×1080 with correct aspect and visible Start controls.

## Core current regression

- [ ] Clean startup on target Windows machine, no unhandled error
- [ ] Image and video ad rotation; manual Start always accessible
- [ ] Tutorial → 12 cyclic template previews and quantity/cart controls
- [ ] **Current tariff only:** two quantity units correspond to **two separate three-capture sessions** and `2 × IDR 5,000`. Do **not** accidentally test future FEAT-001 as if already implemented
- [ ] Demo payment QR visible, labelled DEMO/non-payable; no real-money success claim
- [ ] Payment offer after configured waiting interval (default 60 s) appears without blocking QR and self-dismisses after 15 s
- [ ] Review/retake and output composition preserve expected three captures per *current* session
- [ ] Printer settings persist after restart, test print and result print produce expected physical output
- [ ] Payment QR slip print independent of folder-access QR; QR scan decodes exact DEMO attempt
- [ ] App returns to idle after completion, cancellation and expired session
- [ ] Drive pool/upload/retention on configured service, with no false claim of live API testing

## Failure, security and recovery tests (not currently certified)

- [ ] Camera unplug/plug; UI cannot capture stale frames
- [ ] Printer offline/out-of-paper: job uncertainty and explicit manual retry, **no automatic duplicate print**
- [ ] Missing/corrupt advertising media: safe static image fallback with usable controls
- [ ] Demo payment expiry, cart edits and one-shot confirmation; expired QR cannot silently confirm
- [ ] App restart mid-session preserves intended photo files; document existing gaps, especially FEAT-007 not yet implemented
- [ ] Network/Drive outage and later sync; confirm whether local files expire after 15 days even when upload pending
- [ ] No logging of raw customer photos or QRIS secrets in a future support bundle

## Future-feature acceptance (do not run as current product tests)

- **FEAT-001:** One 3-capture session → 1/2/3 identical prints with proposed amounts IDR 10k/15k/20k; mixed-template pricing and promo accounting only after separate approval.
- **FEAT-002/005:** Receipt demo and same-device dummy ordering promo distinguish code detection from validation and apply one-time merchant-funded base-fee waiver (print fees unaffected). Never claim real POS/payment.
- **FEAT-003:** Mirror **live display only**, not saved photo or printed text, and correctly map scanner overlays.
- **FEAT-004/019:** Assigned ad inventory per machine and tier; Free Meong-managed; Business/Enterprise mixed advertiser inventory with reserved Meong slots, offline-safe playback and truthful impression accounting after entitlement design approval.
- **FEAT-007:** Trusted payment states, crash recovery and idempotent/no duplicate print only once implemented; existing local manifests do not prove this.
- **FEAT-015:** Privacy/retention guarantees need verification before marketing paid photo delivery.

## FEAT-011 / BUG-004 isolated dithering lab evidence — 2026-10-18

- **Owner approval:** create `feature/dither-tuning` from `feature/kivy-gui` and develop a **standalone** GUI to configure dithering algorithm and tuning parameters. Base/rollback commit `5e0a8980968430b85f04ebac1b6c1574c2191a69`; source commit [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229).
- **CI PASS:** [run 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) on `feature/dither-tuning`: Pillow installed, `python -m py_compile photobooth/dither_lab.py tools/dither_tuning_gui.py tests/test_dither_lab.py photobooth/printer.py` **PASS** and `python -m unittest tests.test_dither_lab -v` **PASS**. Tests cover default raster parity, 1-bit and printhead width, alpha, no upscaling, parameter effects, threshold semantics, safe preset validation/round-trip, GUI AST parsing. This is not a full kiosk regression test.
- **NOT RUN / unverified:** launch Tk GUI on user's Windows PC; test slider latency, open/cancel/load/save/export via actual UI; compare 1-bit export to a physical POS80 print; customer session/regression; real photo quality. No physical paper emitted by this tool and no changes to customer kiosk printing.
- [ ] On Windows: `python tools/dither_tuning_gui.py`; use `Buka foto` with an actual saved PNG, switch all three methods, change each enabled slider, compare previews/zoom; save JSON preset; reopen it; export 1-bit PNG; verify PNG mode `1` and image width 576/384.
- [ ] Inspect at least one physical print per mode with identical source, paper, dot width and printer-darkness settings. Photograph and label each print; compare readability of face/edges/details against original, log selected preset and operator ranking.
- [ ] Before integrating into `main.py`, obtain **separate explicit approval** and run production print + payment-QR + audio/video regression tests. Do not copy a lab profile into `data/printer_settings.json` (different schemas).

## 2026-10-18 audio implementation evidence / current acceptance

- Scope approved by owner in conversation: BUG-001 music playback and BUG-007 Settings Uji audio; branch `feature/kivy-gui`, baseline `06dd977c06657c9b56e1de0ad18042b65515bd64`.
- Source patches: restart SDL2 music channel at full gain once after ad fade; force operator music audition; remove extra generic button click for three Uji controls; fix diagnostic newline. Tests added for forced preview, fade replay and isolated GUI button sounds.
- **Pre-change GitHub Actions baseline:** Kiosk GUI regression run [39101639665](https://github.com/pratikto/PhotoBooth/actions/runs/39101639665) FAILED the full discovery suite, but syntax and 87 synthetic visual renders succeeded; root failing test not identified from available logs.
- **Post-change GitHub Actions on code SHA `b69d3837de6220d27a477a10a807fdbdd799cb0b`:** [run 39104614520](https://github.com/pratikto/PhotoBooth/actions/runs/39104614520) **FAILED overall**: `python -m compileall -q photobooth tests tools` **PASS**; `xvfb-run -a python -m unittest discover -s tests -v` **FAIL** (exit 1, individual failing test not available in captured job log); `xvfb-run -a python tools/render_gui.py --output-dir /tmp/meong-gui-qa` **PASS**, 87 renders, 0 reported errors; visual-summary step **PASS**. The **baseline run also failed** at discovery: this does not identify whether any newly added audio tests failed.
- **Owner Windows targeted unit test, 2026-10-18:** `python -m unittest tests.test_audio -v` run in `.venv-kivy` using **Windows, Python 3.12.10, Kivy 2.3.1**. Owner-supplied terminal output: **14 tests, 13 PASS, 0 FAIL, 1 SKIP** in **2.539 seconds**. Specific passes include `test_music_autostarts_when_advertising_fades_into_tutorial` and `test_operator_music_audition_restarts_a_stale_playing_handle`; provider-native audio test **SKIPPED** because `PHOTOBOOTH_TEST_AUDIO=1` not set. Expected incomplete-bank warning is generated by a simulated missing-provider test, not an operational device finding. **Code SHA of owner's checked-out working tree has not been independently confirmed**; log supplied after audio patch push. **Real music output in running `python main.py` / Windows speaker remains UNVERIFIED.** CI uses dummy `SDL_AUDIODRIVER` and `PHOTOBOOTH_AUDIO=0`; provider states and mocked checks cannot certify physical sound.

## Regression commands to execute (historical results do not carry forward)

```bash
python -m compileall -q photobooth tests tools
python -m unittest discover -s tests -v
python -m unittest tests.test_audio -v
python -m unittest tests.test_printer -v
python -m unittest tests.test_tutorial_entry -v
python -m unittest tests.test_advertising -v
```

Native audio/video tests may require explicit opt-in environment flags and compatible Windows codecs. Linux-only `SDL_*` flags from historical QA are not automatically transferable to Windows PowerShell. Record exact commands, pass/fail/skip counts, output and the tested commit. No tests are claimed executed in this documentation-only task.

## Release acceptance (requires owner decision)

- [ ] All approved BUG/FEAT acceptance criteria and regression outputs recorded
- [ ] Physical paper/audio/video/camera acceptance recorded by the owner
- [ ] Payment simulation clearly separated from any future live payment release
- [ ] Blocking defects resolved, or explicit written risk acceptance documented
- [ ] Rollback reference and device configuration backup recorded
- [ ] Owner explicitly authorizes the release
