## Version 1.0.0 — release-source verification (2026-10-19)

**Immutable release SHA:** `07ce51d2022ab5673a7a27e744e5e5757fbb3d08` (`v1.0.0`, GitHub pre-release). [Kiosk GUI](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245) **SUCCESS**: 235 tests (233 PASS, 2 SKIP, 0 failures/errors), 87 synthetic screenshots / 0 errors. [Dither lab](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273) **SUCCESS**: 48 tests. GitHub Linux mocked tests verify code/screenshot behavior, **not** physical Windows camera/audio/printer/QR phone scan or actual settlement; QRIS is DEMO only. BUG-001/007 audio retest and BUG-009 Drive cloud retention remain unresolved. Earlier `c40f33f5`, `f129dd9e`, and `e46812b8` results are retained as *historical* evidence.

- [x] Old `master` preserved at `backup/master-pre-v1-20261019` (`d4852cb5`); [merge PR #3](https://github.com/pratikto/PhotoBooth/pull/3) landed.
- [x] Source tag `v1.0.0` verified against the release SHA; [GitHub pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0) published.
- [x] Kiosk 233/235 pass with 2 skips + 87 screenshots; Dither 48/48 pass on *exact release commit*.
- [ ] Independent repeatable Windows end-to-end audio (BUG-001/007), physical thermal/QR scanning, and 30-day Drive cleanup (BUG-009) verification before claiming hardware/product certification.
- [ ] Production payable QRIS FEAT-020 not delivered: never infer real payment acceptance from DEMO.

**Evidence rule:** Checkbox items below describing historical pre-v1 milestones or per-device tests are preserved; do not reinterpret them as missing GitHub source release or completed physical acceptance.

---

## Current CI screenshot QR stabilization — 2026-10-19

**QA-QR-001 — CI-only / monitoring:** The owner reports the QR is working normally on their Windows laptop. GitHub's QR screenshot decoder previously failed intermittently (e.g. [run 39176198126](https://github.com/pratikto/PhotoBooth/actions/runs/39176198126) attempt 1) with **identical production code**; a rerun succeeded. The synthetic QR used random DEMO attempt IDs, leading to changing rendered QR matrices; OpenCV sometimes failed at one raster scale.

**Test-harness-only fix** [`e46812b8`](https://github.com/pratikto/PhotoBooth/commit/e46812b8c9f66c548bccebb1e9fc45e3c89afeef): deterministic DEMO IDs **only in `tools/render_gui.py`**, independent bounded native/2x/3x pixel-reading of **the captured PNG crop**, strict equality to payload, and three new positive/negative unittest checks (including blank/obscured QR still FAIL). Production `photobooth/qr_code.py`, `payment.py`, kiosk UI and actual printer unchanged.

- [x] [Kiosk Actions 39178452927](https://github.com/pratikto/PhotoBooth/actions/runs/39178452927) **attempts 1, 2, 3 ALL SUCCESS** on one code SHA `e46812b8`: each **235 tests (233 PASS / 2 SKIP / 0 FAIL or ERROR)** and **87 GUI renders / 0 errors**.
- [x] [Dither Actions 39178452898](https://github.com/pratikto/PhotoBooth/actions/runs/39178452898) PASS at the same SHA.
- [x] Both workflows confirmed PASS on final immutable `v1.0.0` release SHA; newer documentation-only PR commits are **not** part of that tag. Do not conflate SHAs.
- [ ] Monitor future Kiosk runs for repeated screen-QR decode failures (the 3/3 sample is not a permanent guarantee).
- [ ] Real Windows QR scan/thermal paper and legitimate QRIS remain separate; owner reports laptop unaffected and payment QR is still DEMO.

Detailed cause/boundaries: [Kiosk QA history and 2026-10-19 addendum](qa/KIOSK-GUI-REGRESSION-2026-10-18.md).

---

## Historical Kiosk GUI full regression — VERIFIED CI PASS (2026-10-18)

> **PRE-v1 historical evidence:** The earlier verified **full Kiosk GUI CI at `c40f33f5` PASS** ([run 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762): 230 passing/2 skipped, 87 simulated renders), and [dither CI PASS](https://github.com/pratikto/PhotoBooth/actions/runs/39145145764). FEAT-001/003 **OWNER TESTED PASS**; BUG-011 monitored. Specific individual hardware test boxes remain unchecked **if logs, counts or local SHA were not supplied**; unchecked does *not* negate the owner's overall acceptance. BUG-009 Drive cloud retention and audio BUG-001/007 still require separate attention; no production release verified.

**Authoritative outcome:** [GitHub Actions run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476), commit `f129dd9e`, completed **SUCCESS**. `xvfb-run -a python tools/run_kiosk_unittests.py` (standard unittest discovery with Kivy-log-safe reporting): **232 run, 230 PASS, 2 SKIP, 0 FAIL, 0 ERROR**. `tools/render_gui.py` and `ci_visual_summary.py`: **87 simulated GUI screenshots / 0 errors**, including camera, cart, ads, QR DEMO and both supported desktop sizes. Python syntax check also PASS. Environment is Linux GitHub Actions / Python 3.12 / Xvfb / software GL / mocked devices—not Windows hardware.

**Root cause and repair:** 17 initial assertions after the diagnostic runner worked were chiefly stale tests for FEAT-001 session-plus-copy pricing, the approved advertisement → tutorial → template flow, the Settings submenu, deliberate UJI MUSIK restarts and asynchronous print/job completion. The test runner now emits all test names and tracebacks directly to CI stdout and retains the full text as an artifact. All repairs limited to `tests/`, `tools/run_kiosk_unittests.py` and `.github/workflows/kiosk-gui.yml`; **no runtime modules changed, no tests suppressed**. Full chronology, each commit and exact error classifications: **[Kiosk GUI CI repair / acceptance](qa/KIOSK-GUI-REGRESSION-2026-10-18.md)**.

- [x] GitHub broad Kiosk unit suite succeeds at tested `f129dd9e` (230 PASS, 2 SKIP).
- [x] GitHub 87 screenshot render/QR checks succeed at the tested commit.
- [x] GitHub complete Kiosk workflow concludes **SUCCESS** at `f129dd9e`.
- [x] Baseline post-previous-documentation Kiosk CI green on `c40f33f5` ([Actions](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762)).
- [ ] Verify the final HEAD after this **new** documentation reconciliation independently; do not conflate SHAs.
- [ ] Windows end-to-end camera, printer, audio and QR/device acceptance remain **separate**; existing FEAT-001/003 owner-tested passes stand, audio issues stay deferred. This CI cannot verify paper or speaker output.
- **Watch item:** Intermediate run once failed the `payment-enlarged-800x600` rendered QR scan, whereas the completed final 87-render run passed. No QR UI production patch was made; retain this check to detect recurrence.

## FEAT-003 — Display-only Kivy live camera mirror (2026-10-18)

**Latest owner field result (2026-10-18): OWNER TESTED PASS.** After installing FEAT-003, owner explicitly confirmed **"sip udah sesuai. PASS"**. This is direct user acceptance of the currently implemented live capture-preview mirroring, in addition to the independent [dedicated synthetic Kivy GPU test PASS](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320). **Exact local Git checkout SHA, camera model, per-scenario left/right transitions and printed-image comparisons were not supplied.** Keep the granular checkboxes below unchecked until those individual tests are recorded; **do not imply FEAT-002 scanner or full Kiosk regression has been tested or released**. No code was changed to record this evidence.

- **Authorization and implementation:** Owner explicitly selected FEAT-003 on existing `feature/kivy-gui` after FEAT-001 / BUG-011. Baseline `c0cb0d846512233ebff3f625e3c002e2c942485c`. The **currently implemented live camera view is capture only**; no FEAT-002 receipt scanner viewport or detector-box overlay has been implemented yet. Photo capture/retake uses both a first-frame Pillow preview and an ongoing OpenCV BGR frame stream.
- **Source change:** `photobooth/ui_kivy.py` commit [`6f8c8ddf`](https://github.com/pratikto/PhotoBooth/commit/6f8c8ddfcb53d35070213c6fda72b8485232f280) creates preview textures with the usual vertical UV correction and a **horizontal UV flip** for live camera only. `update_live_preview` and `update_live_frame` use the same orientation with texture reuse (no repeated `cv2.flip`, no BGR/Pillow source mutation). Static review/result images, QR/logo/text and the saved-photo/print path stay unmirrored.
- **Targeted automated evidence — VERIFIED PASS:** [FEAT-003 live camera mirror regression Actions run 39139208320](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320) on commit [`307e779e`](https://github.com/pratikto/PhotoBooth/commit/307e779e271ba6deb439b3bbf91343d02c9b30c7), GitHub Ubuntu Python 3.12 + xvfb/software GL: **SUCCESS** for Python compile and `tests.test_kivy_gui.KivyFlowTests.test_live_camera_mirrors_texture_only_not_capture_or_result`. This test checks horizontal/vertical UV orientation of first/stream/resized/retake/countdown previews, GPU texture reuse, unchanged original PIL/BGR bytes, and nonmirrored saved/review/result data. **One dedicated test**, not the full GUI regression or physical camera acceptance.
- **Full Kiosk GUI workflow has now independently PASSED**: [run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476) at `f129dd9e`, 230 passing unittest cases / 2 skips / 87 GUI renders with 0 errors. Earlier FAIL assertions were repaired as QA-only test updates. Full suite success is still **not** a physical Windows camera test or app release.
- [ ] **Windows hardware:** pull the FEAT-003 branch, record tested SHA, camera model/orientation and run `python main.py`. Hold a letter `R` or other asymmetric writing on the viewer's left: the *live* preview must move like a mirror; the original saved JPG, photo-review card, final composed layout and paper must show their **original readable orientation**, not mirrored.
- [ ] **Transition:** before the first shutter, during the 3-2-1 countdown, before a retake and during the retake countdown, the preview must never suddenly swap left/right. Switching capture → review → retake → result does not invert a stored photo.
- [ ] **Gesture/face:** open-palm shutter and face-triggered landing behavior still use unmodified camera frames; optional gesture regions/labels remain aligned with their intended target. Retake quota and three-camera-shot session count remain unchanged.
- [ ] **Performance and error handling:** initial frame, live refresh and camera reconnect reuse/replace UV-mirrored textures safely; no additional CPU image flip, unexpected black frame or noticeable FPS regression.
- [ ] **Cross-feature checks:** printed Floyd photos, copy quantities (BUG-011), payment DEMO QR, Drive folder QR and advertising video retain orientation/playback, since their images should never inherit the live-camera UV transform.
- **Future dependency, not a current test:** Once FEAT-002 scanner is *separately approved and implemented*, show its live camera viewport mirrored using the same Kivy texture policy while decoding barcode/QR from original frames and reflecting bounding boxes from original source X coordinates to the mirrored contained viewport. Do **not** check this item off today; currently that scanner UI does not exist.
- **Rollback plan:** Revert only the scoped FEAT-003 camera-preview UV code and test/workflow changes if Windows hardware fails after owner approval, not the full branch to baseline (which contains unrelated working printer fixes). No printer, QRIS, Drive, audio or `Code.gs` code changed for FEAT-003.

## FEAT-001 — scoped DEMO price / print-copy regression (2026-10-18)

**Updated owner hardware acceptance — FEAT-001 / BUG-011 (2026-10-18):** Initial Windows feedback said **pricing correct, printed-sheet count wrong**; source review found omitted `EndDocPrinter` (with duplicate `ClosePrinter`) and N separate Windows RAW jobs. The fixes now send **one batch of N complete ESC/POS image+cut streams** and finalize the Windows RAW document correctly. After the update, the owner confirmed **"sip udah bener"** and explicitly **"bug 11 udah aku test dan lolos"**. This records an affirmative **OWNER TESTED PASS** of the BUG-011 paper quantity, with the bug retained as **MONITORING** (not CLOSED/RELEASED). The exact 1/2/3 case-by-case paper counts, Windows local SHA/queue name and photographs were not supplied; leave each per-case checkbox below unchecked until evidence is captured. Targeted [CI 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) **PASS: 11 pricing/manifest + 4 mock printer/Windows spool tests**. [Complete evidence/chronology](qa/FEAT-001-BUG-011-acceptance.md). On an uncertain print outcome, **never auto-retry a possibly partial batch**.

- **Authorization:** owner chose to implement FEAT-001 now as a narrow exception to the general P3 payment-feature deferral. Baseline before this change: `5842a09f` on `feature/kivy-gui`. The goal is one chosen template = **one 3-capture session**, even when requesting 2 or 3 identical thermal copies, with **Rp5.000 session fee + Rp5.000 per physical copy**; no real QRIS integration.
- **FEAT-001 isolated headless CI — VERIFIED PASS at commit `dfd6e5fb`:** [Actions run 39131731784](https://github.com/pratikto/PhotoBooth/actions/runs/39131731784) completed **SUCCESS**: `python -m unittest tests.test_workflow.WorkflowTests tests.test_workflow.TransactionStoreTests -v` ran **11 tests, all PASS (0 failures/errors)**; Python compilation step passed. The first broad lightweight run [39131533295](https://github.com/pratikto/PhotoBooth/actions/runs/39131533295) failed only because an unrelated QR decoder test required missing OpenCV; the dedicated workflow was scoped correctly in [`5f82c9e7`](https://github.com/pratikto/PhotoBooth/commit/5f82c9e744fe461e83f719897b014c880bcf74c1). Scope: pricing/session/retake/manifest, **not Kivy GUI, QR decoder, actual printer or real QRIS**. See [workflow file](../.github/workflows/feat001-pricing.yml).
- **Test coverage and evidence:** `tests/test_workflow.py` checks 1/2/3 copy quotes, mixed order and manifest; `tests/test_controller_flow.py` checks editing the DEMO cart, one RAW batch dispatch with requested copies and failure without auto-retry; `tests/test_printer.py` checks repeated ESC/POS image+cut bytes and one transport send; `tests/test_windows_printer_spooler.py` checks one StartDoc/Write/EndDoc/Close lifecycle; `tests/test_kivy_gui.py` covers count display and print-busy UI; `tools/render_gui.py` has aligned fixtures. **The focused 15-test CI run passed; the full Kivy suite is not passing on the documented baseline.**
- **Suggested focused Windows tests:** `python -m unittest tests.test_workflow -v`; set `$env:PHOTOBOOTH_TEST_GUI = "1"` then run `python -m unittest tests.test_controller_flow tests.test_kivy_gui -v`; run `python main.py` using a configured Windows thermal-printer queue. These commands are **not claimed as executed by the owner during this update**. GitHub Kiosk GUI Actions starts automatically on every push; capture completed job URLs, PASS/FAIL and exact SHA separately.
- [ ] On Windows, order **one template ×1 copy**: DEMO cart/QR shows **Rp10.000**, exactly 3 shots, exactly 1 paper print with the selected Floyd profile.
- [ ] **One template ×2 copies**: cart/QR **Rp15.000**, exactly 3 shots, both sheets contain the *same* completed layout (same QR/download destination), and no additional camera session.
- [ ] **One template ×3 copies**: cart/QR **Rp20.000**, same 3 captures and **three** identical physical sheets.
- [ ] **Two different templates ×2 and ×1 copies**: cart/QR **Rp25.000**, only two sessions of 3 captures each, correct distinct composition per template, total **three** sheets; manifest `demo_order_pricing.total_amount`=25000 and session `print_copies` [2,1].
- [ ] Test return from DEMO payment to edit cart without retaining an old amount/QR; switching template carousel does not change quantity; zero deselects a template.
- [ ] Simulate an interrupted/uncertain thermal send: **no automatic resubmission of the uncertain sheet or remaining batch**. Manual "CETAK ULANG" submits a single sheet only after the operator checks paper. Confirm no cross-session printer concurrency and result-page timing does not interrupt a batch.
- [ ] Regression-test camera/retake, template layout/output, Drive upload/folder QR, demo payment QR-slip printing, idle/payment video, existing BUG-001/007 audio symptoms, and other printer modes (Floyd/Bayer/Threshold). **Real QRIS FEAT-020 remains NOT IMPLEMENTED**.
- **Evidence status:** assistant **did not directly operate a Windows printer**, but the owner explicitly confirmed they **tested BUG-011 and it passed**; classify as **owner-tested on-device acceptance** (not an independently collected printer telemetry log). Device test SHA, per-copy counts and photographs are not recorded. [historical Kiosk GUI CI FAIL 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) (superseded by [full PASS 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762)) **FAIL** for full unittest discovery on `f2f52e33`; **not covered by the targeted 15/15 PASS**. Live payment/QRIS is still absent. Rollback baseline: `5842a09f`; do not discard later commits or change stable Floyd settings.

## GUI merged lab + owner Floyd photo default (2026-10-18)

- Owner explicitly approved merging `feature/dither-tuning` into existing `feature/kivy-gui`; fast-forward merge baseline `5e0a898` -> `f3d836d` (no new branch). Dedicated lab CI on `f3d836d` passed; Windows operator verification BUG-010 is pending.
- Owner supplied `meong-dither-3way.json`: Floyd brightness 0.652, contrast 2.104, gamma 2.352, sharpness 2.073, threshold 128 at 576 dots; explicitly approved it as the default for photo compositions in the GUI kiosk. No customer photo is uploaded to the repo.
- Regression test `python -m unittest tests.test_printer tests.test_photo_default -v`: verify raster parity, legacy environment rollback, Bayer/Threshold unchanged, explicit comparisons unchanged. Native Windows paper quality and QRIS scanning still require operator evidence.
- To force old Floyd output if necessary, set `$env:PHOTOBOOTH_PHOTO_TUNING = "legacy"` before `python main.py`; remove that environment setting to return to approved Floyd profile.
- [ ] Confirm 576-dot output on physical photo paper with approved preset and capture side-by-side old/new results.
- [ ] Re-test actual QRIS slip readability, Bayer/Threshold test prints and Windows kiosk video/audio/Settings interactions.
- [ ] Do not mark BUG-004 CLOSED without owner's visual/physical acceptance.

## BUG-010 lab scroll issue — 2026-10-18

- Screenshot/owner confirmed missing access to lower sliders and print controls on Windows.
- Scope authorized: `feature/dither-tuning` GUI layout only. Independent scroll canvas and mouse wheel per lane, compact preview, sticky action buttons; no changes to native raster, printer jobs or kiosk.
- CI compile and static GUI structure tests are evidence of source consistency only; **Windows Tk visual interaction still needs owner retest**.
- [ ] On 1050×620 and maximized, Print Test and Save PNG visible; threshold slider accessible by scrolling Threshold.
- [ ] Mouse wheel/scrollbar affects only hovered algorithm; adjusting slider updates correct preview.
- [ ] Sync Parameters and Save/Load configurations still work; printing still requires confirmation.

## FEAT-011 Stage 1–3 incremental development — 2026-10-18

- Owner approved staged implementation + separate pushes on `feature/dither-tuning` only. **Stage 1** [`9f73f6e`](https://github.com/pratikto/PhotoBooth/commit/9f73f6e4223c98ebc883c70a604a4e47007fb054): independent 3-way config and JSON tests; initial CI **FAIL** due to accidental literal newline escaping in JSON writer. This was fixed in Stage 2.
- **Stage 2** [`15f87a7`](https://github.com/pratikto/PhotoBooth/commit/15f87a71041bd37958711fb0046f72a539323005): new standalone 3-column GUI with per-lane sliders, Sync Parameters, original image, center dot zoom, 1-bit exports, combined config load/save; [CI 39112358484](https://github.com/pratikto/PhotoBooth/actions/runs/39112358484) **PASS**.
- **Stage 3** [`03e7ddf`](https://github.com/pratikto/PhotoBooth/commit/03e7ddf2085f0b0e278b04957e03fbb9b24ee20c): Print Test per lane and Print All with explicit paper confirmation, snapshot of displayed one-bit output, labeled ESC/POS, existing queue/routes and stop-on-uncertain-result. [CI 39112474748](https://github.com/pratikto/PhotoBooth/actions/runs/39112474748) **PASS** (compile/unit tests, *not physical printing*).
- **Windows device QA PENDING:** startup at `python tools/dither_compare_gui.py`; side-by-side preview updates independently, Sync Parameters, rapid dragging, zoom, save/load same three profiles, export native 1-bit raster; physical Print Test each lane, Print All cancel and real output, queue configuration and hardware paper clarity; verify print header, confirm no duplicate retry; full kiosk regression remains separate. **BUG-004 is OPEN.**
- **HISTORICAL / SUPERSEDED branch note:** these lab-stage tests originally ran on the dedicated experiment branch. The lab was subsequently merged into `feature/kivy-gui`, and the approved Floyd preset is active for photo printing. This is still not a release to `master`.

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

## Feature acceptance and outstanding regression (current FEAT-001 plus future work)

- **FEAT-001 (IMPLEMENTED / owner-reported operational PASS; formal matrix still pending):** One 3-capture session per chosen template → 1/2/3 identical paper prints at DEMO Rp10k/Rp15k/Rp20k. The owner accepted pricing and corrected paper quantity; keep explicit per-case and mixed-template physical records pending rather than labeling them automatically verified. Promotional settlement still separately deferred. See [FEAT-001 / BUG-011 QA](qa/FEAT-001-BUG-011-acceptance.md).
- **FEAT-002/005:** Receipt demo and same-device dummy ordering promo distinguish code detection from validation and apply one-time merchant-funded base-fee waiver (print fees unaffected). Never claim real POS/payment.
- **FEAT-003 (capture live preview in source; dedicated GPU CI PASS; OWNER TESTED PASS):** Camera capture/countdown/retake preview mirrors using Kivy UVs only; saved, review, result, QR and printed photos remain original. **Owner explicitly confirmed overall Windows PASS**. Exact local checkout SHA and individual asymmetric-object test log remain unrecorded. The FEAT-002 scanner viewport and its overlay mapping are **not implemented**; test those only after separately approved scanner development. See the latest FEAT-003 section at the top of this checklist.
- **FEAT-004/019:** Assigned ad inventory per machine and tier; Free Meong-managed; Business/Enterprise mixed advertiser inventory with reserved Meong slots, offline-safe playback and truthful impression accounting after entitlement design approval.
- **FEAT-007:** Trusted payment states, crash recovery and idempotent/no duplicate print only once implemented; existing local manifests do not prove this.
- **FEAT-015:** Privacy/retention guarantees need verification before marketing paid photo delivery.

## FEAT-011 / BUG-004 isolated dithering lab evidence — 2026-10-18

- **Owner approval:** create `feature/dither-tuning` from `feature/kivy-gui` and develop a **standalone** GUI to configure dithering algorithm and tuning parameters. Base/rollback commit `5e0a8980968430b85f04ebac1b6c1574c2191a69`; source commit [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229).
- **CI PASS:** [run 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) on `feature/dither-tuning`: Pillow installed, `python -m py_compile photobooth/dither_lab.py tools/dither_tuning_gui.py tests/test_dither_lab.py photobooth/printer.py` **PASS** and `python -m unittest tests.test_dither_lab -v` **PASS**. Tests cover default raster parity, 1-bit and printhead width, alpha, no upscaling, parameter effects, threshold semantics, safe preset validation/round-trip, GUI AST parsing. This is not a full kiosk regression test.
- **NOT RUN / unverified:** launch Tk GUI on user's Windows PC; test slider latency, open/cancel/load/save/export via actual UI; compare 1-bit export to a physical POS80 print; customer session/regression; real photo quality. No physical paper emitted by this tool and no changes to customer kiosk printing.
- [ ] On Windows: `python tools/dither_tuning_gui.py`; use `Buka foto` with an actual saved PNG, switch all three methods, change each enabled slider, compare previews/zoom; save JSON preset; reopen it; export 1-bit PNG; verify PNG mode `1` and image width 576/384.
- [ ] Inspect at least one physical print per mode with identical source, paper, dot width and printer-darkness settings. Photograph and label each print; compare readability of face/edges/details against original, log selected preset and operator ranking.
- [x] **Historical integration milestone:** the owner approved incorporating the selected Floyd preset as Kivy photo-print default and merging the standalone lab code into this branch. This has been implemented; **no extra integration into `main.py` is pending for that approved preset**. Preserve the distinct JSON schemas. Broader printer/QR/audio physical checks remain a separate release gate.

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


## FEAT-021 — Windows prototype Step 3 acceptance (owner report, 2026-10-21)

- **Branch:** `feature/meong-flappy-challenge`; tested runtime SHA not supplied; Windows Kivy manual run, exact OS build/screen dimensions not supplied.
- **Manual GUI:** owner confirms **6/6 PASS**: app launches and renders; asteroid collision respects visible camera-cat body and excludes rainbow trail; tap controls respond; portrait/landscape resize remains proportional and clickable; reused `DEMO-` receipt is rejected after restart; win/loss screens show appropriate demo outcome without replay.
- **Earlier targeted automated tests:** owner-supplied Windows Python 3.12 output: `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts -v` — **10 tests, OK**. No new automated tests run for this documentation entry.
- **Evidence level:** owner-reported, not independently reproduced or GitHub CI verified. No claim of hardware/production acceptance.
- **Open:** exact logo sprite, kiosk welcome-screen integration, full GUI regression, real POS receipt and payment/discount verification; master remains unchanged.


## FEAT-021 — Step 4 rewritten standalone UI QA plan (2026-10-21)

**New code on:** `feature/meong-flappy-challenge`. Historical Step 3 owner-reported Windows GUI 6/6 PASS and Windows Python 3.12 10/10 PASS describe the **older renderer**; they do NOT certify the new mockup-styled GUI. Environment used for assistant-side proof did not have Kivy nor network access to clone GitHub.

- **LOCAL MIRROR (not the GitHub checked-out branch):** Python `compileall -q` PASS for local modules, pure Pillow rendered five 360x720 pixel-art scene frames with user-supplied GIF stand-in, and a headless smoke script PASS on demo claim/replay/back/skip/pause/win and no retry. Do not represent this as Windows/Kivy PASS.
- **New source-level tests written, execution pending on exact GitHub SHA:** `tests/test_meong_fly_flow.py`, `tests/test_meong_fly_painter.py`.
- [ ] Windows: `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts tests.test_meong_fly_flow tests.test_meong_fly_painter -v` -> record Python/Kivy/Pillow versions, actual totals, branch SHA.
- [ ] Visually compare **Start, Scan, Gameplay, Win, Lose** with the owner's selected mockup. Confirm branded logo uses approved PNG, no white logo box/cropped cat; buttons, scoreboard and fonts are readable.
- [ ] Demonstrate the 10-point win target and Game Over, asteroid collision visible relative to camera-cat body (rainbow excluded), stars/rainbow move smoothly, and pause stops physics.
- [ ] Receipt `DEMO-MOCKUP-001` works once, never replays after loss/win/restart; KEMBALI before claim does not consume it; invalid/reused codes show errors.
- [ ] Resize portrait and landscape; no sprite distortion, missing button, hidden voucher input or misplaced touch hitboxes. Record render FPS/performance.
- [ ] MAIN GAME -> SCAN -> GAME -> terminal, plus LANGSUNG FOTO -> demo exit; no real QR scanning, no payment or discount redemption; **no MAIN LAGI** on either terminal screen.
- [ ] Obtain owner visual acceptance only after above checks; **do not merge to master** until separately authorized.

Screen-by-screen source and precise limitations: [FEAT-021](features/FEAT-021-meong-fly.md).


## BUG-012 — FEAT-021 demo receipt text entry (2026-10-21)
- **Observed before fix:** owner Windows screenshot of Scan Struk screen; painted input visible but user cannot type; versions/commit unspecified. This invalidates Step 4 GUI acceptance for receipt entry until retested.
- **Source fix:** `974b8c7c`; tests added `38d00d41`. Full Kivy drawing moved to `canvas.before` to preserve child `TextInput` and `Label` graphics. No evidence of new Windows PASS at time of record.
- [ ] After `git pull`, run `python -m unittest tests.test_meong_fly_gui -v`. Expected: 2 Kivy-independent tests and 3 Kivy widget tests (if Kivy installed). Record actual output and exact commit/OS/Python/Kivy versions.
- [ ] Run `python -m photobooth.meong_fly_demo` on Windows, Start > Scan > click input: cursor and `DEMO-123` hint visible, typed `DEMO-BUG012-001` visible, Back/Validate still respond.
- [ ] Press Enter or Validasi, verify Gameplay; close and restart app and verify used code is rejected. Repeat with a *new* demo code.
- [ ] Resize to portrait and landscape and confirm the typing hotspot tracks the painted input. No production checkout/scanner testing implied.


## FEAT-021 — Visual Polish v2 Batch A QA gate (2026-10-21)

**Source branch:** `feature/meong-flappy-challenge`; `master` unchanged. Source commits `74bdef6a`, `cbc74372`, `f8bc996b`, `e18a0936`, `f7b0598e`. Targeted tests `05fccdd6` and `6df4d498`. **Assistant-side local mirror:** `PYTHONPATH=/mnt/data/meong_step4 python -m unittest discover -s /mnt/data/meong_step4/tests -p test_meong_fly_polish.py -v` -> **7 tests, OK** (Pillow 12.3.0, Linux container), followed by `python -m compileall -q /mnt/data/meong_step4/photobooth /mnt/data/meong_step4/tests` -> no errors. This is **not** an exact GitHub SHA unit run or a Windows/Kivy GUI test; Kivy is not installed in the container. Preview logo is the supplied GIF frame, not the official PNG byte-for-byte.

- [ ] Windows after `git pull`: `python -m unittest tests.test_meong_fly_polish tests.test_meong_fly_gui tests.test_meong_fly_flow tests.test_meong_fly_receipts tests.test_meong_fly tests.test_meong_fly_painter -v`; record Python/Pillow/Kivy versions, exact SHA and final summary.
- [ ] Start screen: official logo fully visible, halo behind mascot, voucher and Rp2.500 demo disclaimer do not overlap, CTA pink/cyan hierarchy and icons visible; both buttons respond on touch/click, Direct Photo exits standalone demo only.
- [ ] Scan screen: corner brackets and animated horizontal line do NOT imply real scanning; `ILUSTRASI QR` and `QR ASLI BELUM TERHUBUNG` readable.
- [ ] Click real light TextInput: caret and `DEMO-123` hint are visible; type, paste, backspace, press Enter or Validate with `DEMO-V2-001`, and confirm gameplay starts; observe focus/error ring and disabled input after claim.
- [ ] Back from Scan before claim returns Start and leaves new code valid; reused code remains rejected on restart; no Main Lagi or gameplay reset bypass.
- [ ] Resize to 450x900 portrait and landscape/windowed; exact letterbox touch hitboxes for input/CTA, no clipped footer, no stretched mascot, no screen lockup or FPS regression.
- [ ] Send actual Windows screenshots of Start and Scan, record owner visual acceptance. **Batch A not VERIFIED until then; Batch B/C not yet implemented in this pass.**


## FEAT-021 — Batch B Gameplay art/regression evidence (2026-10-21)

**Status:** IN SOURCE only; **NOT owner-Windows-GUI VERIFIED**. Branch `feature/meong-flappy-challenge`; pre-Batch-B rollback baseline `c1498217`. Source changes `72658e55`, `b60c0d68`, `a08952fd`, `7b7b448a`, `ad4a2e49`, `1cea6794`. Test additions `9ed6ab19`, `f5349bef`.

**Assistant local-mirror checks:** Linux container Python 3.13.5 / Pillow 12.3.0, no Kivy. `PYTHONPATH=/mnt/data/meong_step4 python -m unittest discover -s /mnt/data/meong_step4/tests -p 'test_meong_fly_*.py' -v`: **19 run / 15 PASS / 4 SKIP (Kivy unavailable) / 0 FAIL / 0 ERROR**. `python -m compileall -q /mnt/data/meong_step4/photobooth /mnt/data/meong_step4/tests`: no errors. Standalone `DemoReceiptLedger` smoke: claim/one attempt/pause/loss/persistent replay denial PASS. This local mirror is **not** a verified checkout of the exact resulting GitHub commit. Sample Pillow frame is conceptual only; do not report Windows/UI/hardware PASS based on it.

- [ ] On Windows after pull: `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts tests.test_meong_fly_flow tests.test_meong_fly_painter tests.test_meong_fly_polish tests.test_meong_fly_gui tests.test_meong_fly_game_art tests.test_meong_fly_gameplay_gui -v`.
- [ ] Start and Scan remain functional; `DEMO-BATCHB-001` works once and is denied after restart; no `Main Lagi` anywhere.
- [ ] Gameplay Score 0, midgame, near-asteroid screenshots and collision fairness; camera-cat pose, rainbow and asteroid belts never imply smaller hitboxes than physics.
- [ ] Pause freezes score, elapsed time, objects and input; resume restores gameplay; score +1 only once per completed obstacle pass.
- [ ] Crash burst displays ~220 ms, does not accept an invisible Continue button, then shows correct actual Game Over score.
- [ ] 450×900 portrait / 800×600 / 1200×800 layout, smooth >=30 FPS on intended mini-PC; real Kivy gameplay performance and input coordinates.
- [ ] Owner visually accepts Gameplay before Batch C. Historical 6/6 Windows Step 3 and 7/7 Batch A Pillow evidence do NOT certify this renderer.


## FEAT-021 — Batch A/B Windows Kivy automated regression reported PASS (2026-10-21)

**Evidence:** user-pasted Windows console log in ChatGPT; reported run includes the targeted 8 FEAT-021 test modules. **`Ran 55 tests in 6.272s` / `OK`**, i.e. **55 PASS / 0 FAIL / 0 ERROR / 0 SKIP**. All Kivy-specific tests actually executed (no conditional skip). Reported environment: **Windows**, Python **3.12.10**, Kivy **2.3.1**, SDL2 window, OpenGL **4.6**, Intel **Iris Xe Graphics**. Exact tested feature-branch SHA, Pillow version, screenshots, and FPS measurements **not supplied**; do not label "CI certified" or "independently verified".

**Covered automated test categories:** 6 new pure Pillow Batch B geometry/art tests, 2 source contract tests, 4 Kivy Batch B runtime tests (GPU textures, pause, +1 scoring, loss animation), 7 input/canvas/hover tests, 10 flow tests, 2 receipt persistence tests, 8 physics tests, 9 painter tests, and 7 Batch A art/layout tests, totaling **55**. BUG-012 receipt TextInput redraw regression passes in the shared Kivy suite; that does not replace live typing/visual acceptance.

- [x] Owner reports new targeted Windows automated 55/55 PASS (Kivy **not skipped**); reported output retained in conversation.
- [ ] Record exact `git rev-parse HEAD` from tested checkout and `python -m pip show pillow` version before tying result to a precise source baseline.
- [ ] Inspect live Start/Scan on Windows: visible caret/hint, actual typing/paste, scanner decoration, usable CTA at portrait/landscape, no clipping.
- [ ] Inspect live Gameplay with screenshots at score 0/midgame/near asteroid; ensure camera-cat remains recognizable, rocks never visually mislead about full rectangular hitbox, and HUD+trail clarity.
- [ ] Manually play pause/resume, observe score +1, hit burst, 10-point target and single attempt after application restart.
- [ ] Check physical device FPS (goal >=30), input hit regions and letterboxing at 450x900, 800x600 and 1200x800.
- [ ] Owner aesthetic acceptance of Batch A/B after live GUI review; Batch C Win/Lose still not implemented in this pass.


## FEAT-021 — Tutorial/layout handoff test gate (2026-10-21)

Scope `feature/meong-flappy-challenge` standalone demo. **New code pushed; latest tests NOT YET REPORTED on Windows.** Previous owner Windows **55/55 PASS** refers to the older, pre-handoff revision and cannot verify this change.

- [ ] Run `python -m unittest tests.test_meong_fly_flow tests.test_meong_fly_painter tests.test_meong_fly_gui tests.test_meong_fly_gameplay_gui -v` plus the remaining FEAT-021 regressions; record tested SHA, actual output.
- [ ] Win CTA shows **PILIH LAYOUT FOTO**, never payment; when tutorial unseen it opens Tutorial before the demo layout selector. Win hint Rp2.500 remains demo-only.
- [ ] Lose CTA shows **PILIH LAYOUT FOTO**, never payment; identical tutorial routing, with zero demo discount.
- [ ] Direct Photo skips game/receipt and still opens Tutorial if unseen, or demo layout selector if previously completed.
- [ ] Completing tutorial sets local standalone-only marker; reopening demo skips tutorial. Preserve production tutorial preference isolation. Simulate read-only marker failure, ensure current-session flow is still accessible.
- [ ] 12 generic **demo** layout cards are visible and clickable, but do not masquerade as approved actual thermal templates or trigger camera/payment. Selecting a card exits the standalone demo.
- [ ] No second game attempt, no retry button, and SQLite receipt replay protection after restart.
- [ ] Verify portrait/landscape touch mapping and readable screen text before owner visual acceptance; NOT marked production integrated.
