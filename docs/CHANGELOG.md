# Meong Photobooth — Documentation and release changelog

This file tracks **actual verified repository/document changes**, not successful live booth operation. Historical test assertions are kept in [FEATURE_STATUS.md](FEATURE_STATUS.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and [QA evidence](qa/README.md). Application code can be considered released only under [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md).

## [Unreleased] — 2026-10-18

### Approved staged 3-way tuning lab continuation
- Stage 1 `9f73f6e`: independent comparison profiles and schema validation; initial CI failure from literal newline in JSON, fixed in stage 2.
- Stage 2 `15f87a7`: `tools/dither_compare_gui.py` with original plus three live dithering columns, independently tunable sliders, optional sync controls, zoomed dot crop, runtime/coverage information, save/load all configurations and native 1-bit exports. Dedicated CI passed.
- Stage 3 `03e7ddf`: labeled, confirmed physical Print Test and Print All via `photobooth/dither_print.py`, submitting the preview's exact one-bit raster without re-dithering, halting uncertain batches. Dedicated CI passed; **physical print and Windows GUI are not yet verified**. The primary current GUI is `python tools/dither_compare_gui.py`; original single-lane GUI remains as a legacy lab utility.
- Stage 4: updated [operator lab guide](dither-tuning-lab.md), bug/feature status and real-device acceptance checklist; no production kiosk code touched.


### Owner-approved standalone thermal dithering lab (FEAT-011 / BUG-004)
- **New experimental branch:** [`feature/dither-tuning`](https://github.com/pratikto/PhotoBooth/tree/feature/dither-tuning), forked from GUI baseline [`5e0a898`](https://github.com/pratikto/PhotoBooth/commit/5e0a8980968430b85f04ebac1b6c1574c2191a69); source commit [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229).
- Added `photobooth/dither_lab.py` with calibrated 1-bit thermal previews, adjustable brightness/contrast/gamma/sharpness, mode/width/threshold controls and validated atomic JSON profiles. Reuses existing `photobooth.printer.dither_image`; defaults preserve current native printer raster behavior.
- Added standalone `tools/dither_tuning_gui.py` (Tkinter GUI with side-by-side before/after, 3× detail crop, debounce/background render, photo open, JSON preset load/save and 1-bit export); synthetic example only, no customer data sent or real printer submitted.
- Added targeted `tests/test_dither_lab.py`, separate `.github/workflows/dither-lab.yml`, and [operator usage guide](dither-tuning-lab.md). [CI 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) **PASS** for compile and targeted tests; Windows live Tk UI and real paper/quality **NOT VERIFIED**.
- **Scope boundary:** existing `photobooth/printer.py` and Kivy app are **unchanged** in this source commit; no main-branch merge, app integration or production release authorized. BUG-004 is not fixed merely by creating a tuning lab.



### Approved application audio remediation (BUG-001 / BUG-007; Windows verification pending)
- **Base/rollback commit:** [`06dd977c`](https://github.com/pratikto/PhotoBooth/commit/06dd977c06657c9b56e1de0ad18042b65515bd64); implementation and associated docs/tests are in the current audio commit on `feature/kivy-gui`. No branch creation or merge.
- `photobooth/audio.py`: reacquire a native music channel at saved full gain when the ad fade finishes; add an operator-forced music audition that cannot be skipped by a stale `state=play` report and obeys normal mute/pause/ad gates.
- `photobooth/ui_kivy.py`: each Sound Settings Uji control plays its intended sample without a preceding generic button click; refresh feedback displays a true newline and distinguishes playback request from confirmed audible sound.
- `tests/test_audio.py` and `tests/test_kivy_gui.py`: add regression coverage for forced music retry, fade replay and exclusive per-button sample routing.
- Reconcile latest owner-reported device passes for BUG-002/003/005/006 separately from BUG-001/007 audio acceptance in `bug_tracker.md`, `FEATURE_STATUS.md`, `test_checklist.md` and `DEVELOPMENT_HANDOVER.md`.
- **Tests (after code commit [`b69d3837`](https://github.com/pratikto/PhotoBooth/commit/b69d3837de6220d27a477a10a807fdbdd799cb0b)):** [GitHub Actions run 39104614520](https://github.com/pratikto/PhotoBooth/actions/runs/39104614520) **FAIL overall**; Python compile **PASS**; full `unittest discover` **FAIL** (exit 1; test name not captured); 87 GUI renders **PASS**, no reported render errors; visual summary **PASS**. Baseline also failed discovery on [run 39101639665](https://github.com/pratikto/PhotoBooth/actions/runs/39101639665). Audio-only tests not separately executed, and **no sound physically verified yet**. This status was recorded in a linked documentation follow-up commit.

### Owner Windows unit-test confirmation (BUG-001 / BUG-007; docs only)
- Owner shared direct Windows PowerShell results for `python -m unittest tests.test_audio -v`: **14 run, 13 PASS, 1 SKIP, 0 FAIL** (2.539 s) on Python 3.12.10 / Kivy 2.3.1. Both music-fade and explicit music-audition regressions passed; actual native audio test remains skipped and music audibility in the running kiosk still needs owner confirmation. The checked-out commit SHA was not included in the terminal output. This entry records observed test evidence without application-code changes.

### Mandatory development documentation workflow (docs only)
- Added [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md): copy/paste full and quick prompts for new development conversations, with branch/SHA inspection, scope approval, severity/dependency review, code/test boundaries, GitHub documentation mapping and final traceability report. Commit [`de0886b`](https://github.com/pratikto/PhotoBooth/commit/de0886b9fdf491d7e21db403c234656044f9b67b).
- Updated [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) to require the relevant feature/bug/status/test/handover/changelog documents to be kept aligned with **approved** code changes, in the same or a clearly linked companion commit; false claims of physical acceptance remain forbidden. Commit [`5800c56`](https://github.com/pratikto/PhotoBooth/commit/5800c561006966b90dc316f404ec1ddbd9743328).
- Linked the canonical prompt in [docs/README.md](README.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and the repository-root [README.md](../README.md). The handover now points to one maintained prompt rather than duplicating its full operating rules.
- **Scope:** Markdown documentation only; no Kivy/Python application code, media, hardware configuration or runtime behavior changed. No automated or physical booth test executed for this documentation change.


### Documentation governance and folder housekeeping (docs only)
- Introduced the development protocol with approval gates, dynamic bug/feature prioritization, regression evidence levels and rollback requirements.
- Added independent bug register, feature backlog and verification checklist without representing reports as fixes.
- Renamed the technical continuation document to `docs/DEVELOPMENT_HANDOVER.md`; retained `docs/NEXT_STEPS.md` as a legacy-link pointer, not a duplicate backlog.
- Moved the five planning/operations Markdown files from root to `docs/`: `DEVELOPMENT_PROTOCOL.md`, `bug_tracker.md`, `next_step.md`, `test_checklist.md` and `CHANGELOG.md`. Root `README.md` remains at root.
- Added [documentation index](README.md), updated root README links and aligned major internal documentation references.

### Product/business specification intake (documentation only)
- Recorded FEAT-001 base IDR 5,000/session + IDR 5,000/physical-copy target, independent of three-photo capture count. **Current source tariff is unchanged.**
- Documented demo merchant receipt scan, demo ordering-to-photo promotion, mirror-only camera preview, per-machine local-first ad delivery, theme ideas and reliability/scale candidates FEAT-002–018.
- Added BIZ-001/FEAT-019: hardware sales, mandatory assigned **Free/Business/Enterprise** tier including IDR 0 Free, Free fully commercial operation, Meong-controlled Free advertising and Meong-reserved ad slots in Business/Enterprise; reserved percentages/prices remain undecided.
- Parked additional monetization candidates for later owner evaluation without scheduling implementation.

### Latest documentation reconciliation — four successive stages (docs only)
1. **Decisions:** Reconciled owner decisions, existing code versus desired behavior and open contractual/commercial terms in `DECISIONS.md`; distinguished operator photo income from Meong subscription/advertising and merchant subsidy.
2. **Architecture/status/guide:** Aligned `ARCHITECTURE.md`, `FEATURE_STATUS.md`, `advertising-and-qris.md`, and root `README.md` with the source-level printer integration (including shared Windows QR-slip config), existing demo payment, current IDR 5,000/session implementation and live-device failures. Kept historical QA evidence labelled as historical.
3. **Bug/test evidence:** Kept stable BUG-001 through BUG-006, introduced **BUG-007** specifically for unresponsive Music/Button Settings tests and separated audio-output failure. `test_checklist.md` now distinguishes reported physical passes/failures, historical mocked tests, and tests still unverified.
4. **Unified roadmap/handover:** Created one provisional feature execution board covering FEAT-001–019 and deferred POS stages; marked all feature implementations unapproved, fixed model-dependent merchant subsidy recipient, and updated `DEVELOPMENT_HANDOVER.md` so latest blockers and approval gates precede older technical notes.

**No Python, application resources, pricing logic, runtime audio/video/printing, payment gateway or subscription enforcement were changed in these documentation steps. No new automated or physical kiosk test run is claimed.**

## Historical application changes

For changes made before the documentation effort, inspect Git commits and the dated QA evidence. Existing user-confirmed working thermal photo paper output **does not** prove acceptable image quality or QR-slip paper output. Historic sound/video mocked test passes **do not** resolve present Windows audio/video reports. Current defects remain in [bug_tracker.md](bug_tracker.md).
