## FEAT-001 — scoped DEMO price / print-copy regression (2026-10-18)

**Updated owner hardware acceptance — FEAT-001 / BUG-011 (2026-10-18):** Initial Windows feedback said **pricing correct, printed-sheet count wrong**; source review found omitted `EndDocPrinter` (with duplicate `ClosePrinter`) and N separate Windows RAW jobs. The fixes now send **one batch of N complete ESC/POS image+cut streams** and finalize the Windows RAW document correctly. After the update, the owner confirmed **"sip udah bener"**: physical copy quantity now matches the order. Record **OWNER REPORTED PASS — MONITORING**, not formally CLOSED/RELEASED. The exact 1/2/3 case-by-case paper counts, Windows local SHA/queue name and photographs were not supplied; leave each per-case checkbox below unchecked until evidence is captured. Targeted [CI 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) **PASS: 11 pricing/manifest + 4 mock printer/Windows spool tests**. [Complete evidence/chronology](qa/FEAT-001-BUG-011-acceptance.md). On an uncertain print outcome, **never auto-retry a possibly partial batch**.

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
- **Evidence status:** assistant **did not directly operate a Windows printer**, but the **owner explicitly confirmed its physical copy output is now correct**, which is valid owner-reported field acceptance. Device test SHA, per-copy counts and photographs are not recorded. [Kiosk GUI CI 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) **FAIL** for full unittest discovery on `f2f52e33`; **not covered by the targeted 15/15 PASS**. Live payment/QRIS is still absent. Rollback baseline: `5842a09f`; do not discard later commits or change stable Floyd settings.

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

## Feature acceptance and outstanding regression (current FEAT-001 plus future work)

- **FEAT-001 (IMPLEMENTED / owner-reported operational PASS; formal matrix still pending):** One 3-capture session per chosen template → 1/2/3 identical paper prints at DEMO Rp10k/Rp15k/Rp20k. The owner accepted pricing and corrected paper quantity; keep explicit per-case and mixed-template physical records pending rather than labeling them automatically verified. Promotional settlement still separately deferred. See [FEAT-001 / BUG-011 QA](qa/FEAT-001-BUG-011-acceptance.md).
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
