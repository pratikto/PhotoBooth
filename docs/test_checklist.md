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
