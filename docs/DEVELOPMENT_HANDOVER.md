# Meong Photobooth — Development handover

> **CURRENT RELEASE BASELINE (2026-10-19):** Default branch `master` contains Meong Photobooth Kivy GUI. Immutable source snapshot `v1.0.0` / `07ce51d2022ab5673a7a27e744e5e5757fbb3d08` is published as a [GitHub pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0). Release-SHA CI: [Kiosk GUI 39185986245](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245) (**233 pass, 2 skipped, 87 synthetic renders, 0 errors**) and [Dither 39185986273](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273) (**48 tests pass**). Linux mock/screenshot QA is **not** certification on Windows hardware or customer deployment. Outstanding: BUG-001/007 audio speaker retest, BUG-009 30-day Drive cloud retention **OPEN**; QRIS is DEMO/non-payable (FEAT-020 not implemented), receipt scanner FEAT-002 not implemented. The earlier `feature/kivy-gui` branch and dated narratives below are **historical** where they conflict with this baseline.

> **Next continuation:** Prioritize owner retesting of BUG-001/007 Windows audio and documented risk management of BUG-009 cloud retention; FEAT-008 remains only a proposed feature requiring separate approval. The PR #3 promotion is **complete**, not pending.

**Repository:** https://github.com/pratikto/PhotoBooth  
**Target baseline:** `master` for stable code; new approved changes go to a dedicated task branch (`fix/*`, `feature/*`, or `docs/*`) and through PR review. **Tag:** `v1.0.0` stays unchanged.  
**Handover updated:** 2026-10-19 (historical handover began 2026-10-17).

## Historical QA handover — Kiosk GUI Regression FULL CI PASS (2026-10-18)

**Owner-approved remediation completed:** Prior **Kiosk GUI regression FAIL** is now **VERIFIED PASS** on [run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476) at source/test SHA [`f129dd9e`](https://github.com/pratikto/PhotoBooth/commit/f129dd9ecb14b2d554dd83022745452764f5282d). The full Kivy `unittest` suite performed **232 tests: 230 passed, 2 skipped, 0 failed/errors**; the visual renderer produced **87 scenarios / 0 errors** and the workflow concluded **SUCCESS**. A later [**HEAD `c40f33f5` CI run 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762) also completed SUCCESS**. Reconciliation documentation commits after that snapshot must be verified separately.

**Diagnosis:** Kivy swallowed unittest stderr in GitHub logs; `tools/run_kiosk_unittests.py` now captures a full standard unittest report to OS stdout and a CI artifact. The readable full-suite baseline exposed **17 outdated assertions**, reduced to four then zero. Repairs affected test expectations for FEAT-001 base-plus-copy pricing and one capture per template; ad → tutorial → layout flow; current Settings → Audio submenu and explicit music audition restart; deterministic fake completion of async print batches; mock Windows QR print routing without touching the real host OS. A one-off intermediate `payment-enlarged-800x600` visual decode failure was not reproduced in the final complete **87/87** render; continue monitoring rather than falsely claiming a separate QR production fix.

**Touched code is QA-only:** `.github/workflows/kiosk-gui.yml`, `tools/run_kiosk_unittests.py`, selected `tests/test_*.py`. **Zero production `photobooth/` modules**, zero `Code.gs`, no payment or printer modifications, no branch merge/deployment. The earlier physical FEAT-001/BUG-011 print and FEAT-003 mirror successes remain owner-tested evidence, independent of this Linux CI pass. Deferred BUG-009 Google Drive retention and BUG-001/007 speaker/audio symptoms are **not** closed.

**Next work:** no additional Kiosk CI remediation is warranted while the latest SHA stays green. Verify the current reconciliation's final HEAD workflow, then return to the backlog after fresh approval; FEAT-008 health checks remains the next normal feature candidate. No further development is approved merely because the CI quality gate is green. Canonical evidence: [Kiosk GUI full regression record](qa/KIOSK-GUI-REGRESSION-2026-10-18.md) and [test checklist](test_checklist.md). Roll back only QA tooling/tests if needed; never reset the accepted printer/camera branch to a pre-feature state.

## Historical FEAT-003 implementation/acceptance detail — CURRENT PASS remains valid (2026-10-18)

**Scope/approval:** Owner explicitly requested proceeding with FEAT-003 on the existing `feature/kivy-gui` branch. Baseline `c0cb0d84`. The present GUI implements only **capture-page** live camera previews; FEAT-002 receipt scanner and detection bounding boxes are **still backlog**. The user wants **all current and future live camera views mirrored**, but the approved delivery here implements only the existing live screen and establishes the shared rendering policy for later screens.

**Code delivered:** [`6f8c8ddf`](https://github.com/pratikto/PhotoBooth/commit/6f8c8ddfcb53d35070213c6fda72b8485232f280) adds `PhotoBoothUI._new_display_texture(..., mirrored=False)`, the existing mandatory vertical UV flip and an opt-in horizontal UV flip. Both first Pillow/ready/countdown/retake preview `update_live_preview` and streamed BGR `update_live_frame` request mirrored=True. There is **no `cv2.flip` on the shared frame**: capture, face/palm recognition, JPEG, review, final layout, QR and thermal printing remain unmirrored. No changes to `app.py`, `camera.py`, payment, printer or `Code.gs`. Synthetic GPU test committed in [`e99cbb26`](https://github.com/pratikto/PhotoBooth/commit/e99cbb26b485d7497642953c04e09c223dab0c6c) with callback cleanup; [dedicated CI workflow `feat003-mirror.yml`](../.github/workflows/feat003-mirror.yml).

**Verified independent CI and field evidence:** [FEAT-003 run 39139208320](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320) at `307e779e` **PASS**, 1 focused synthetic Kivy GPU test plus Python compile on Ubuntu/Python 3.12/Xvfb. It checks preview UVs, texture reuse and resize, unmodified BGR/Pillow inputs, saved/review/result orientation. **The owner has now separately tested the feature on Windows and explicitly said "sip udah sesuai. PASS"**. The assistant did not operate a physical camera or receive the exact checkout SHA or a per-case recorded test matrix. **Status: FEAT-003 IN SOURCE — OWNER TESTED PASS for current capture preview**, not a full Kiosk GUI regression/release signoff. **HISTORICAL failure is SUPERSEDED:** the full Kiosk GUI workflow later PASSED at `c40f33f5`; this does not represent a Windows hardware or release signoff.

**Next safe step:** FEAT-003 current capture behavior **is owner-tested PASS**; no further camera-mirror patch is warranted while working. For formal release evidence, collect exact local Windows SHA, per-case initial/countdown/retake checks and original saved/photo print comparison when convenient; a user acceptance statement alone should not be misrepresented as an instrumented matrix. The next normal backlog item is **FEAT-008 device health**, subject to explicit owner approval and existing CI gates. The future FEAT-002 receipt scanner/overlay remains separate and unimplemented. Full checklist: [test_checklist.md](test_checklist.md). **Do not change stable FEAT-001/BUG-011 printer logic.**

**Priorities unchanged otherwise:** FEAT-008 device health and FEAT-009 auto-start are still normal pending priorities, with FEAT-003 an owner-selected exception. Audio BUG-001/007 deferred; BUG-011 owner-tested PASS/monitoring; BUG-009 Drive 30-day-retention risk still OPEN/deferred with FEAT-004. FEAT-020 real QRIS deferred. More detailed current scope: [next_step.md](next_step.md) and [FEATURE_STATUS.md](FEATURE_STATUS.md).

## Historical FEAT-001 delivery and BUG-011 resolution — OWNER TESTED PASS (2026-10-18)

> **HISTORICAL / SUPERSEDED incident narrative below:** Initial copy-count failure and earlier Kiosk CI failures are retained as the debugging timeline. Current: owner-confirmed copies work; full Kiosk CI is green. This section is not an active repair instruction.

### BUG-011 paper-copy mismatch — owner confirms working after Windows RAW fix

Owner reports FEAT-001 **pricing correct but printed-sheet count wrong** on Windows (actual requested/output counts not yet recorded). Read-only investigation of `photobooth/printer.py` found **concrete RAW Windows spool finalization error**: `_send_windows_raw()` called `ClosePrinter` twice and **never called `EndDocPrinter`**. Fixed at [`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93). FEAT-001 previously sent N independent RAW jobs; changed to **one Windows RAW spool document** with N complete, identical image+cut payloads in [`4608fcc9`](https://github.com/pratikto/PhotoBooth/commit/4608fcc9ec96c8eabeb01ddbd64059830af2bf62) and [`e6d2f684`](https://github.com/pratikto/PhotoBooth/commit/e6d2f6840d4b5838e719f904bcc3b8443291193a). Mock Windows spooler and payload tests exercise one StartDoc/Write/EndDoc and N cut sequences; [targeted FEAT-001 Actions 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) **PASS**, but does not establish successful actual paper output.

**Latest owner physical retest (2026-10-18):** After printer changes, the owner first replied **"sip udah bener"**, then explicitly confirmed **"bug 11 udah aku test dan lolos"**. Treat this as **OWNER TESTED PASS** on the Windows physical print-copy defect, alongside the accepted DEMO pricing; it is not merely inferred from the screen. Retain BUG-011 **MONITORING / not formally CLOSED or RELEASED** and FEAT-001 **IMPLEMENTED / owner-tested core behavior**. Exact per-case 1/2/3 cut-sheet counts, tested local SHA and printer queue name were not supplied, so do not retroactively mark each hardware checklist row VERIFIED. The [canonical QA dossier](qa/FEAT-001-BUG-011-acceptance.md) separates field report, targeted 15-test CI PASS ([run 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707)), and current full [Kiosk GUI CI FAIL 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) at source/documentation baseline `f2f52e33`. **No further changes to the now-working print transport are recommended unless a regression is observed.** Other tasks (BUG-001/007 audio, BUG-009 Drive photo retention, FEAT-020 QRIS) retain their prior deferrals.

**The owner explicitly requested "kita lanjut feat1 aja"**, approving FEAT-001 as a narrowly scoped exception to general P3 transaction/payment feature sequencing. Do not infer approval for FEAT-007 durable paid-state recovery, FEAT-020 real QRIS, FEAT-002 promo settlement or any actual merchant charge. The QR shown at checkout must continue to say DEMO / non-payable.

**Current source:** `catalog.py` defines Rp5.000 per selected template/session plus Rp5.000 per physical copy; `workflow.py` quotes one 3-shot session per chosen template; `ui_kivy.py` labels copy counts; `app.py` sends **one batch per saved layout** with requested copy count; `printer.py` repeats N identical ESC/POS image+cut streams and finalizes Windows via `EndDocPrinter`/single `ClosePrinter`; `transaction_store.py` persists the copies and a `demo_order_pricing` record. This supersedes the earlier separate N-job print implementation described by historical commits. No automatic replay when transport status is uncertain. A manual `CETAK ULANG` is a deliberately requested **one extra sheet**, not a paid transaction. [Detailed code/test map and field-evidence gaps](qa/FEAT-001-BUG-011-acceptance.md).

**Print navigation:** `ui_kivy.show_result` now locks NEXT/SELESAI while `print_busy=True` and unlocks after `_finish_print_job` reports that the batch has stopped/completed; `test_kivy_gui.py` validates this gate, while the template-navigation test uses a deterministic stub printer. **Isolated FEAT-001 headless CI** was added via [`.github/workflows/feat001-pricing.yml`](../.github/workflows/feat001-pricing.yml) (commit `35775128`), to distinguish quote/session/manifest test results from the pre-existing Kiosk GUI full-suite failure. **Verified CI result:** [FEAT-001 pricing run 39131731784](https://github.com/pratikto/PhotoBooth/actions/runs/39131731784) on `dfd6e5fb` = **11 tests PASS, 0 errors/failures**. Initial broad lightweight QR test failed from absent `cv2` and was narrowed to the pricing/session/manifest suite; full Kivy/physical printing not certified.

**Quality/risk:** Owner-reported physical paper success is now recorded, but does not provide a per-case 1/2/3 log or certify all configurations. Formal release still needs mixed-template paper checks, crash/fault behavior, full GUI regression (subsequently **PASS at `f129dd9e` on [run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476)**), supported printer variations and explicit release approval. No live QRIS payment was implemented. Pre-implementation rollback reference: [`5842a09f`](https://github.com/pratikto/PhotoBooth/commit/5842a09f6a4c6c771ef7f5f0d1a330d0b1040b42); a hard reset would discard many later unrelated commits, so use a **targeted reviewed revert only if ever necessary**.

**Other priorities unchanged:** FEAT-008/009 remain normal top-of-backlog features after this owner-selected work. BUG-001/007 postponed, BUG-008 monitoring, BUG-009 still OPEN/deferred alongside FEAT-004 with cloud privacy risk. Current canonical prioritization and FEAT-001 exception: [next_step.md](next_step.md).

## Earlier priority handover — owner decision 2026-10-18 (superseded by FEAT-001/BUG-011 update above)

**Target:** `feature/kivy-gui`; use the [unified execution board](next_step.md) rather than historical sections below. Owner explicitly deferred **all payment, transaction, checkout/pricing, receipt-promo settlement and paid-reprint development to execution P3 LOW** while real QRIS is absent. **NEW FEAT-020** captures future provider-backed real QRIS; the existing QR and payment confirmation are DEMO / non-payable. Before any real-money release, FEAT-001 pricing, FEAT-007 durable paid-state recovery and FEAT-020 provider verification must be coordinated. **This is a documentation decision, not approval for code or deployment.**

**CURRENT proposed nonpayment queue:** (1) FEAT-008 device health, (2) FEAT-009 generic Windows auto-start/crash recovery **without paid-transaction resume**, (3) **FEAT-003 already owner-tested PASS (removed from pending work)**, (4) FEAT-012 diagnostics, (5) FEAT-010 per-machine nonpayment config/identity, (6) FEAT-004 Drive advertising sync together with deferred, still-unverified BUG-009 cloud-photo retention, then visual/campaign features. GitHub Kiosk GUI CI remains an independent test gate, not proof of a payment defect.

**Existing owner deferrals and acceptance:** BUG-001/007 Windows audio remains failing but intentionally deferred; BUG-008 Settings currently responds and is MONITORING; BUG-004/010 print quality and dither-scroll are owner-reported PASS; BUG-009 remains OPEN/deferred to FEAT-004 with unresolved 30-day Drive privacy risk. Old handover notes below (including 'BUG-004 OPEN' and an isolated lab not yet merged) are **historical**, superseded by later [bug tracker](bug_tracker.md), [feature status](FEATURE_STATUS.md) and current branch commits. No new hardware validation, unit tests, payment onboarding, gateway changes or release is claimed by this documentation update.

## Isolated owner-authorized experiment — `feature/dither-tuning` (2026-10-18)

The owner expressly requested a **NEW branch** specifically for configuration of dithering algorithms and tuning parameters, overriding the usual no-new-branch default **for this task only**. New branch `feature/dither-tuning` originates from `feature/kivy-gui` at `5e0a8980968430b85f04ebac1b6c1574c2191a69`. First isolated FEAT-011 source commit: [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229). Lab instructions in [dither-tuning-lab.md](dither-tuning-lab.md). [Dedicated CI 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) PASS (compile + targeted unit tests); Windows GUI, native printer output and quality still require owner verification. Kivy GUI app, printer transport and payment QR code are not modified. **Do not merge to `feature/kivy-gui` or `main` without new owner authorization.** This temporary exception does not authorize branching other features.

**FEAT-011 next steps:** test Windows `python tools/dither_tuning_gui.py`; compare actual saved photo PNG and zoomed raster using preset, export binary PNG; confirm the outputs on real paper (same width/brightness/density). Retain BUG-004 OPEN. Known BUG-008 (Settings hang) and BUG-009 (Drive retention deployment) remain unrelated active operational issues; building a standalone lab does not fix them.

## Historical handover snapshot — reconciled 2026-10-18 (superseded by v1 top section)

**Read this first rather than treating the dated 2026-10-17 notes below as an active work order.** Source-of-truth documents:

- [Documentation index](README.md), [reusable development prompt](DEVELOPMENT_PROMPT.md), and root [README](../README.md) (current status banner and historical project setup).
- [DECISIONS.md](DECISIONS.md): owner-confirmed commercial/product behavior versus proposals.
- [FEATURE_STATUS.md](FEATURE_STATUS.md): actual source implementation versus user-reported physical acceptance.
- [bug_tracker.md](bug_tracker.md): operational defects and stable IDs.
- [test_checklist.md](test_checklist.md): evidence classifications and real on-device acceptance.
- [next_step.md](next_step.md): **one unified provisional feature queue** plus parked business ideas. Detailed old intake ranks are historical, not authorization.

**Current latest owner feedback (2026-10-18):** BUG-002 video in idle/payment, BUG-003 payment QR paper, BUG-005 tutorial route and BUG-006 opening ad size are **OWNER REPORTED PASS** and not in active fix queue. BUG-007 Settings test taps now receive events, button SFX and shutter SFX work, but `Uji Musik` emitted only the standard click; BUG-001 tutorial/layout background music remains inaudible while SDL2 reports `state=play gain=0.59`. The user explicitly approved targeted BUG-001/007 code+documentation changes. BUG-004 thermal print blur remains OPEN and outside the audio patch. Pre-existing CI full-suite run 39101639665 failed despite 87 successful synthetic renders. Audio change requires actual Windows speaker retest; do not infer physical pass from provider state.

**Current source verified by file inspection, NOT physical test:** `photobooth/printer.py` and `printer_settings.py` are already integrated into `feature/kivy-gui` with Windows USB queue/LAN/Wi-Fi and Floyd–Steinberg/Bayer/threshold. `photobooth/qris_print.py` receives saved GUI `PrinterConfig`; legacy LAN-only fallback is for direct callers. Payment remains a *non-payable demo*. `photobooth/catalog.py` still uses IDR 5,000 per independent session/quantity, and `workflow.py` captures 3 photos **per quantity**. Do not describe proposed per-copy pricing as working.

**Future direction is documented, not delivered:** FEAT-001 base fee + per-physical-copy pricing (still 3 captures per chosen session); FEAT-002A dummy external receipt scanner and FEAT-005A standalone ordering demo with automatic same-device photo promo; FEAT-003 mirrored live preview only; FEAT-004 per-machine local-first Drive ads; FEAT-006 GUI themes; FEAT-007–018 reliability, promotional reporting and fleet enhancements; BIZ-001/FEAT-019 sale of hardware with mandatory assigned Free/Business/Enterprise tier. Free remains commercially usable and all its ads belong to Meong; paid users may control some ads while Meong retains **unspecified** reserved slots on every tier. No paid-tier licensing, ad quota enforcement, merchant POS integration, or live QRIS is represented as shipped.

**Funding rule:** merchant pays the waived base-fee promotion only when redeemed; the settlement recipient is the Meong-operated booth owner or a separate sold-machine operator according to who funded the discount and the contract. Do not call every merchant reimbursement Meong revenue.

**Execution gate:** Bug reproduction, device evidence and documentation review first. Before implementing any fix or feature, secure **separate explicit user approval of that code scope**. Use only `feature/kivy-gui`, preserve the thermal-printer branch, avoid accidentally overwriting local Windows changes, run targeted tests + full regression after authorized code, and require real device/owner signoff for printing/audio/video. This housekeeping made **documentation edits only**.

## Audio scope authorized and applied — 2026-10-18 (BUG-001 / BUG-007)

- Base commit: `06dd977c06657c9b56e1de0ad18042b65515bd64`; changes on existing `feature/kivy-gui` only. Audio patch and paired tests/docs committed together; see branch history for the resulting commit.
- `audio.py`: full-gain SDL2 music restart after returning from ad fade, deliberate music audition that reacquires the mixer channel while honoring mute/paused/ad rules. `ui_kivy.py`: Uji buttons bypass the generic click and explicitly audition music, button or shutter; diagnostic text uses a real newline.
- Added unit and real-widget regression expectations. **Post-change CI for code SHA `b69d3837`:** [run 39104614520](https://github.com/pratikto/PhotoBooth/actions/runs/39104614520) had Python compile PASS, full `unittest discover` FAIL (exit 1, test identity not exposed in job log), GUI render PASS (87 renders, no reported render errors), visual summary PASS. The preceding baseline CI already failed the same broad test step; a targeted audio suite has not been independently verified. No Windows speaker verification performed by GitHub Actions.
- **New owner Windows audio-unit evidence (2026-10-18):** `python -m unittest tests.test_audio -v` = **14 run, 13 pass, 1 skipped, 0 failures** in 2.539 s; Windows with Python 3.12.10, Kivy 2.3.1. Includes PASS for both the fade-after-ad test and forced music-audition test. Native audio opt-in check was skipped. Working-tree SHA was not present in shared command output. This test evidence **does not prove speaker audibility**.
- Next owner test: verify `git status` / current HEAD, launch `python main.py`; idle ad -> tutorial -> layout (music must be heard without Settings); open Sound Settings and tap Uji Musik, Uji Tombol, Uji Efek kamera; verify each emits only its intended sound; test 0%/restored music volume, advert muted application BGM and next user round. Record both result and diagnostics if still silent.
- Next repair queue: BUG-004 thermal print blur and independent CI regression investigation only with their own approvals.

## Recommended next engineering investigations (historical 2026-10-18 list; now superseded by owner feedback)

1. Audio settings pointer/touch diagnostic (BUG-007) and application audio lifecycle (BUG-001), with logs distinguishing missed button events from mute/routing.
2. Idle/payment MP4 decoder and texture playback on actual Windows hardware (BUG-002). Test visible moving frames with supported codec; the user's original sample files were noted to lack audio streams.
3. Payment QR print worker and selected saved Windows queue (BUG-003). Collect worker result, spooler messages and paper; never claim successful print from an ESC/POS file alone.
4. Native-width source-to-raster photo quality comparison (BUG-004); compare existing dither modes and physical output, separate photo from QR printing.
5. Manually verify tutorial route, ad stage sizing and complete payment/capture/print flow (BUG-005/006), then revisit feature priorities.

## Resume checklist

1. Read [this updated handover](#current-handover--reconciled-2026-10-18), [Architecture](ARCHITECTURE.md), [Feature status](FEATURE_STATUS.md), [Decisions](DECISIONS.md), [Bug tracker](bug_tracker.md), [Feature backlog](next_step.md), [root README](../README.md), and [Advertising and QRIS](advertising-and-qris.md).
2. Fetch the **current** branch head and inspect working files before editing. Never assume older chat claims are committed.
3. Only after explicit owner authorization, address reported defects **one by one** in small, reviewable commits. Keep detailed English comments. Do not modify the separate thermal-printer branch.
4. Run targeted unit tests, then broad regression suite and real Kivy screen checks; document commands/results and unverified physical tests.
5. Update `FEATURE_STATUS.md` and this file after each fix, then verify commit/push and link the resulting SHA.

## Historical initial coding priorities (2026-10-17; superseded by current bug tracker)

**A. Video playback fails on both idle and payment (partial configuration fix committed 2026-10-17).** Inspect `ui_kiosk.py`, `advertising.py`, `requirements.txt`, ad playlist paths and Kivy video provider/ffpyplayer lifecycle. Distinguish absent local video media, failed decoder, texture not attached, muted media and stalled playback. Ensure payment playback is **muted**, not disabled. Add diagnostic logging and tests for both placements. The bundled playlist now auto-discovers video files from the repository-root `ad_video/` directory (alphabetical order, arbitrary filenames and supported extensions), for both placements. Still-image poster entries remain as fallback. Videos are NOT committed to GitHub; local decoder and actual playback remain to be verified. Custom `PHOTOBOOTH_AD_CONFIG` playlists remain explicit and do not use automatic discovery. Runtime decoder/frame testing is still outstanding; do not claim videos have been uploaded or playback fixed.

**B. Enlarge the initial ad area (source change committed 2026-10-17).** The idle page now uses up to 1920dp width, narrow gutters and a shorter header; video retains `contain` sizing, and Start/face-offer controls remain outside/on the stage. Real-widget render checks at 800×600, 1200×800 and 1920×1080 are still pending.

**C. Fix music initialization (fade-in fix committed 2026-10-17; device verification pending).** Trace `KivyHost.build/on_start`, `AudioManager.start`, initial advertising audio ownership and transition into the guide. Check why opening Settings appears to initialize playback. The audio fade now explicitly restarts music as volume rises from zero, without requiring Settings. Preserve intentionally silent application music while source-video advertising is active; verify this fix on the user's speaker and when entering tutorial/photo flow.

**D. Enforce ad -> tutorial -> layout picker (source change committed 2026-10-17; device QA pending).** Both advertising manual Start and face-invitation acceptance now open the illustrated tutorial. The tutorial's Start control continues to invoke the existing layout-selection controller. Regression coverage added in `tests/test_tutorial_entry.py`; test execution and hardware UI navigation verification remain pending.

## Acceptance criteria

- Both configured image and compatible local MP4 ads render/advance on idle and payment pages; payment ad audio remains muted.
- Idle video is visibly larger without cropping/distorting or hiding Start.
- Music begins on entry to tutorial/photo flow without touching Settings; user-selected mute is respected.
- Both Start routes lead to tutorial before the user can select a layout.
- Existing template/session/retake/QR demo/Drive flows and their tests continue to pass.
- Status and handover docs reflect **observed** behavior, not aspirations.

## Important limitations

Physical machine speakers, local media/codec setup, camera, Google Drive and LAN thermal printer cannot be validated from GitHub alone. Real QRIS is not yet supported. Previous automated QA results are historical, not validation of the four newly reported defects.

## Historical copy/paste prompt (2026-10-17; superseded — use DEVELOPMENT_PROMPT.md)

The maintained full and quick prompts are in [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md). The compact starter below references that single canonical prompt rather than maintaining a divergent second checklist:

> Historical 2026-10-17 resume advice (superseded): the then-current `feature/kivy-gui` branch was the development target. **Do not copy this old branch instruction.** Use the maintained [reusable prompt](DEVELOPMENT_PROMPT.md), start from `master`/`v1.0.0`, and seek explicit task approval for new changes, PR merges, deployment and physical signoff.

## Current blocker: audio remains silent (reported 2026-10-17)

The prior music fade-in commit has **not** solved output on the user's machine. Do not mark audio done. The original three sample clips are documented as silent video sources, so test advertising sound with a **known audio-bearing video**. On the user's machine, collect console/Kivy provider logs, check `PHOTOBOOTH_AUDIO`, `KIVY_AUDIO`, persisted `data/audio/levels.json`, actual selected sound output, and run `PHOTOBOOTH_TEST_AUDIO=1` native Kivy test with the real output (not dummy SDL driver). Verify whether the music sound handle enters `play` on tutorial and whether it reaches audible output. Fix based on those observations, add targeted regression test and update status.

## Retest after fade-gain fix — 2026-10-17

A Windows test run reported 1 failure in `test_music_autostarts_when_advertising_fades_into_tutorial`: sound state was `play` instead of expected `stop` before gain increased. A follow-up change defers `_ensure_music` when `_music_mix <= 0`. Next run `python -m unittest tests.test_audio -v`; then run the opt-in native audio checks with `$env:PHOTOBOOTH_TEST_AUDIO='1'` and `python -m unittest tests.test_audio.AudioTests.test_real_provider_starts_music_and_loads_every_cue_from_a_fresh_install -v`. Clear this environment flag afterward. For advertising audio, test a video that genuinely contains an audio track. Report whether the tutorial song and Settings' Uji music are audible.

## Audio diagnostic update — Windows checks passed 2026-10-17

The user ran all standard audio unit tests: 12 passed, 1 opt-in native test skipped. The separately enabled native audio test passed and logs show all five WAV handles loaded via SoundSDL2, with ffpyplayer and SDL2 providers available. No assertion failures remain in these checks. This does **not** verify speaker output. Next obtain one direct observation from user: is the song audible when entering the tutorial and/or pressing `Uji Musik` in Settings? If still silent, check Windows Volume Mixer and current output device, user preferences, environment flags, and Kivy logs before more source changes. Advertising samples were documented as containing no audio track; verify with ffprobe or another known audio-bearing video.

## Speaker diagnostic — 2026-10-17

User confirms no audible music in the full app despite passing native provider tests. Added `tools/check_audio_output.py` to isolate SDL2 audio output without Kivy GUI/page ownership. Run `python tools/check_audio_output.py` from repo root, listen for five seconds, and inspect Windows Volume Mixer for Python and the selected device. If direct test sounds, investigate full-app audio lifecycle/mute settings; if it is silent, investigate Windows/SDL2 routing or device. Do not mark the bug fixed based on native `play` state alone.

## Diagnostic script import correction — 2026-10-17

The first attempt at `python tools/check_audio_output.py` stopped with `ModuleNotFoundError: No module named 'photobooth'` before any music playback, because direct script execution excluded the repository root from `sys.path`. Fixed the script to insert its checkout root. The user's report of no sound from that attempt does **not** establish an audio-device failure. Rerun after pulling and report output and whether 5 seconds of audio are audible.

## In-app diagnostic update — 2026-10-17

User confirms `python tools/check_audio_output.py` makes audible music, whereas `python main.py` remains silent. Therefore SDL2 can deliver audio on their machine; actual app audio is **not fixed**. Added a live Settings diagnostic line showing `provider`, `state`, `gain`, persisted `level`, fade `mix`, `advert`, `paused`, `started`, number of loaded `sounds` and `enabled`. Reproduce with Settings open on **tutorial** and report the complete diagnostic line and whether `Uji` is audible. `advert=1` on the opening advertising screen is expected (app music suppressed); a silent source MP4 has no ad audio to output. Do not claim audible application music until user confirms.

## Integration staging — 2026-10-17

The latest advertising/tutorial GUI is the integration base. Thermal printer
modules, saved settings, Windows RAW spooler, three dithering modes, operator
settings popup, test print callback and result-page print worker/reprint have
been copied and adapted to `feature/kivy-gui`. The separate printer branch is
kept as a backup; PR #2 shows the unmodified branch-to-branch merge conflicts.
Hardware tests are pending; the real video/audio bug remains unresolved.

**Do not delete old branches.** Before publishing to `master`, run
`python -m unittest discover -s tests -v`, launch `python main.py`,
verify entry via ad/tutorial, checkout demo and printer settings, and test
Windows RAW paper output. A successful print spooler job does not prove paper
output. Check UI screenshots at desktop resolutions and the persistent
`data/printer_settings.json`. Importantly, this branch now integrates printer
features from the older printer branch without replacing recent advertising
or payment behaviors.

## Windows QA feedback (2026-10-17)

User's local Windows `python -m unittest discover -s tests -v` reported
172 tests, four errors and 69 skips. Three printer import errors originate
from **local unresolved merge artifacts** (`<<<<<<< HEAD` in
`tests/test_printer.py`, and a 661-line `photobooth/printer.py` with an
unterminated string) rather than the current GitHub `feature/kivy-gui` files
(which contain no conflict markers and whose printer module has 625 lines).
Do not overwrite uncommitted local edits; inspect `git status`, abort only
an active unfinished merge/rebase if appropriate, then refresh the working
tree safely. The fourth error was a Windows permission restriction when
creating a symlink in the retention test; that specific `WinError 1314`
condition now skips the symlink-specific test while preserving other errors.
Re-run full and opt-in GUI tests before merging PR #3 into `master`.


## 2026-10-21 — FEAT-021 Step 3 owner-reported GUI acceptance

Branch `feature/meong-flappy-challenge` contains isolated Meong Fly Space Edition prototype; owner reports **6/6 Windows GUI checklist PASS**, alongside earlier **10/10 Windows Python 3.12 targeted unit tests PASS**. Exact GUI runtime SHA, screenshot and display dimensions were not supplied; evidence is operator-reported and limited to standalone prototype. No production integration, real POS receipt or QRIS discount; no merge to master. See [FEAT-021](features/FEAT-021-meong-fly.md) and [test checklist](test_checklist.md).

**Next safe action:** propose Step 4 welcome-screen integration design and regression plan, request explicit code approval, and keep the work isolated on a feature branch. Existing operational BUG-001/007 audio and BUG-009 Drive retention priorities are not superseded by this prototype milestone.


## 2026-10-21 — FEAT-021 revised Step 4 standalone mockup build

Owner requested a **genuinely redesigned independent mini-game UI** to follow the selected five-panel pixel-art mockup and explicitly postponed any production photobooth GUI integration. Work stayed entirely on `feature/meong-flappy-challenge` (no master merge). New `photobooth/meong_fly_painter.py` paints five screens with approved bundled logo display crop; `photobooth/meong_fly_gui.py` renders art in standalone Kivy with correct portrait/landscape touch mapping and game HUD; `photobooth/meong_fly_flow.py` owns receipt claim and navigation independently of Kivy. `meong_fly_demo.py` remains the standalone entry, target score now 10. Tests added for flow/art. No camera/POS QR scan, live Rp2.500 discount or checkout wiring; buttons that suggest photo/payment exit the demo only. **Old Step 3 Windows 6/6 acceptance is historical**; new GUI on Windows and precise GitHub branch tests remain pending. Local mirrored code had passing compile/Pillow image render and headless smoke, not an actual Kivy acceptance. See [feature design and source record](features/FEAT-021-meong-fly.md) and [test checklist](test_checklist.md).

**Next action (no new code scope automatically approved):** owner `git switch feature/meong-flappy-challenge`, `git pull`, run `python -m photobooth.meong_fly_demo` and `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts tests.test_meong_fly_flow tests.test_meong_fly_painter -v`; send five Windows screenshots and complete terminal output. Fix exact deviations from mockup on branch after evidence. Real photobooth welcome/checkout integration remains BLOCKED until separately authorized; operational BUG-001/007 audio and BUG-009 Drive retention priorities remain unchanged.


## 2026-10-21 — BUG-012 FEAT-021 Windows input blocker
Owner screenshot shows the painted demo-code box but cannot enter a receipt. Root cause identified in mockup GUI source: parent `canvas.clear` erased actual TextInput/Label child drawing when screens refreshed. Applied isolated `canvas.before` fix `974b8c7c`, added source-layout + optional Windows Kivy GUI regression `38d00d41`. **Status source patched; Windows retest not yet reported.** Run `python -m unittest tests.test_meong_fly_gui -v` and `python -m photobooth.meong_fly_demo` from `feature/meong-flappy-challenge`, checking visible caret, typing, Enter/Validate and one-receipt-once rule. Continue visual polish only after bug acceptance. Never merge to `master` without authorization.


## 2026-10-21 — FEAT-021 Visual Polish v2 Batch A handover

The owner approved Batch A only (Start/Scan/shared visual primitives). Work pushed to `feature/meong-flappy-challenge`: new `meong_fly_polish.py` painter and Start/Scan delegation, Kivy animated decorative QR sweep, TextInput focus/error and button-hover borders, and stop-time event cleanup. Layout preserves the BUG-012 input canvas fix and original `ACTIONS`/receipt ledger. Real POS scanning/payment and production photobooth GUI untouched. [Approved implementation specification](features/FEAT-021-visual-polish-v2.md).

**Tests:** local pure Pillow 7/7 PASS and local compileall no errors; Windows Kivy and exact GitHub source SHA regression are still pending. Original Step 3 owner GUI 6/6 PASS applies only to older renderer. Operator next: `git switch feature/meong-flappy-challenge && git pull`, run `python -m unittest tests.test_meong_fly_polish tests.test_meong_fly_gui tests.test_meong_fly_flow tests.test_meong_fly_receipts tests.test_meong_fly tests.test_meong_fly_painter -v`, launch `python -m photobooth.meong_fly_demo`, capture Start/Scan/screenshots and validate typed code and responsive resize. Do **not** mark verified before operator report; defer visual Batch B gameplay and Batch C win/lose until instructed. Do not merge to `master`.


## 2026-10-21 — FEAT-021 Batch B Gameplay Visual Polish handover

**Authorized scope completed IN SOURCE** on `feature/meong-flappy-challenge`; pre-stage ref `c1498217` serves as non-destructive rollback baseline. New `photobooth/meong_fly_game_art.py` creates pixel arcade background, HUD, 5 deterministic textured asteroid variants, logo camera-cat pose trio and hitbox mapping. `meong_fly_painter.py` delegates the Gameplay background to it. `meong_fly_gui.py` preloads all rock/sprite assets, uses GPU Kivy rectangles for parallax/starfield/asteroids/rainbow and performs score pop/short impact before the existing terminal screen. User's one-receipt-one-attempt rule, no retry and demo-only scan/discount remain unchanged; production `master` GUI, audio, camera, printing and payment are untouched.

**Actual checks:** 19 local-mirror targeted tests, 15 PASS/4 SKIP because Kivy unavailable; Python compileall PASS; standalone flow smoke PASS. This is not an exact GitHub SHA or Windows device verification. New test files: `tests/test_meong_fly_game_art.py`, `tests/test_meong_fly_gameplay_gui.py`. Related UI tests exist from Batch A and need Windows regression (BUG-012). Source/test commits are recorded in [v2 visual spec](features/FEAT-021-visual-polish-v2.md) and [test checklist](test_checklist.md).

**Operator next:** update branch, run `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts tests.test_meong_fly_flow tests.test_meong_fly_painter tests.test_meong_fly_polish tests.test_meong_fly_gui tests.test_meong_fly_game_art tests.test_meong_fly_gameplay_gui -v`; launch `python -m photobooth.meong_fly_demo` in Windows Kivy; check Start/Scan text entry, Gameplay/asteroid fairness, score +1, pause, Game Over delay, reuse refusal and frame rate at portrait/landscape resolutions. Obtain owner visual acceptance before any Batch C Win/Lose finishing. **No master merge**. Existing production BUG-001/007 audio and BUG-009 retention priorities remain.
