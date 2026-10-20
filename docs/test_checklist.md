> **CI repair note (2026-10-20):** Initial B.3 completion-evidence run [39365063377](https://github.com/pratikto/PhotoBooth/actions/runs/39365063377) FAILED on Windows/Ubuntu because existing `test_hardware_discovery.py` mocked the superseded `discover_local_devices` call. Commit [`c7e953b`](https://github.com/pratikto/PhotoBooth/commit/c7e953bd847a5b5bdb3ce7d8501ad320ef52a809) updates that regression to `discover_devices_with_evidence` and verifies the `discovery_complete_kinds` field. New device CI [39365154697](https://github.com/pratikto/PhotoBooth/actions/runs/39365154697) and Kiosk GUI CI [39365154604](https://github.com/pratikto/PhotoBooth/actions/runs/39365154604) were QUEUED at record time; do not report SUCCESS until their final conclusions appear. Physical acceptance remains pending.

> **B.3 completion evidence QA (2026-10-20):** Regression added to `tests/test_device_recovery.py` covering successful empty Windows EnumPrinters => saved queue MISSING and failed EnumPrinters => UNKNOWN. CI result for new HEAD must be checked before claiming PASS. Manual Windows restart, camera disconnect/reconnect, actual printer and Linux SBC still NOT verified. `PHOTOBOOTH_TEST_GUI=1` Kiosk GUI suite remains required.

> **B.3 UI branch validation (2026-10-20):** Source `photobooth/ui_health.py` commit `79ffc96` adds selected-device status without modifying printer/camera runtime; `tests/test_device_selection_ui.py` commit `2452f65` adds candidate-status smoke regression. **New head regression not yet verified** at documentation-writing time. Expect `PHOTOBOOTH_TEST_GUI=1` plus `python -m unittest discover -s tests -p test_device_selection_ui.py -v`; cross-platform device health workflow exercises B.3 core mocks. Physical unplug/replug acceptance not run. No merge.

> **LATEST B.3 QA LEDGER (2026-10-19):** Before B.3, owner Windows PowerShell Python 3.12.10 / Kivy 2.3.1 reported **313 run / 223 PASS / 90 SKIP / 0 FAIL** default (19.121 s) and **313 run / 308 PASS / 5 SKIP / 0 FAIL** with `PHOTOBOOTH_TEST_GUI=1` (101.898 s); exact local Git SHA **not provided**, so these are *pre-B.3 owner evidence*, not new-commit acceptance. GUI opt-in Device Health 10/10 and Device Selection UI 6/6 PASS in that run. Non-failing runtime log includes occasional Kivy MP4 image-loader errors; not proof customer ad playback is broken. [B.3 Windows/Ubuntu device CI 39245625653](https://github.com/pratikto/PhotoBooth/actions/runs/39245625653) **SUCCESS** for prior doc HEAD `70f6766`; [Kiosk GUI 39245625676](https://github.com/pratikto/PhotoBooth/actions/runs/39245625676) was **IN PROGRESS** at last check. Post-documentation current HEAD needs its own verification. The new `test_device_recovery.py` targets eight mock cases; **no owner physical disconnect/reconnect/restart evidence**. Stage C, actual print/camera/speaker/media and production QRIS are not certified.

> **B.3 CI launched:** [device health Windows/Ubuntu run 39245547810](https://github.com/pratikto/PhotoBooth/actions/runs/39245547810) and [Kiosk regression run 39245547822](https://github.com/pratikto/PhotoBooth/actions/runs/39245547822) were queued/running for code/workflow commit [d26314ef](https://github.com/pratikto/PhotoBooth/commit/d26314ef0ba8af4bdd22e2d1e84c86e0b1bffec2). Final PASS/FAIL **not established** at record time. CI now includes B.3 test module on both Windows and Ubuntu.

## FEAT-008 B.3 — 2026-10-19 approved branch-only increment

- [x] Source added: `photobooth/device_recovery.py` (non-invasive presence/reappearance classification), linked tests `tests/test_device_recovery.py`.
- [ ] New B.3 regression run: `python -m unittest discover -s tests -p "test_device_recovery.py" -v` — **NOT RUN / no result yet**. Do not infer PASS merely from push.
- [ ] Full regression for post-change branch HEAD — **NOT RUN yet**.
- [x] Earlier owner Windows GUI opt-in regression: **313 tests, 308 PASS, 5 SKIP, 0 failures**, 101.898 seconds; owner screenshot/log supplied in chat; exact owner local SHA not supplied. It predates B.3 commits.
- [ ] B.3 state observation is not wired to live UI; live disconnect/reconnect behavior, printer readiness and camera frames require separate acceptance.
- [ ] Windows/SBC physical disconnect, reconnect, permission and restart tests pending. No automatic hardware switching or merge approved.

## FEAT-008 Windows local test follow-up — selection PASS, stale discovery fixture (2026-10-19)

- [x] **Owner Windows PowerShell:** `test_device_selection.py` — **13/13 PASS**, including `test_linux_camera_symlink_remains_selected_and_is_not_opened`; previous local WinError 1314 for this suite is resolved.
- [ ] **Owner Windows PowerShell:** `test_hardware_discovery.py` — **9/10 PASS, 1 ERROR**. `test_linux_v4l_by_id_alias_is_stable_candidate_not_verified_camera` still attempted `alias.symlink_to(fake)` at local line 62 and raised `WinError 1314`.
- [x] **Repository comparison:** current `feature/device-health` remote test file branches on `os.name == "nt"` at line 63 and only calls `alias.symlink_to(fake)` in the Linux/non-Windows branch at line 76. Therefore the user-provided trace matches an **older local copy of `tests/test_hardware_discovery.py`** (exact local Git SHA not provided), not the current patched repository file. Do not recommend admin rights or Developer Mode.
- [ ] **Next owner action:** confirm `git status` and `git branch --show-current`; fast-forward pull `feature/device-health` if safe; rerun `python -m unittest discover -s tests -p "test_hardware_discovery.py" -v`. Do not overwrite uncommitted changes.
- [x] Prior [GitHub CI 39223474630](https://github.com/pratikto/PhotoBooth/actions/runs/39223474630) PASS for **62/62 Windows** and **62/62 Linux** device tests. This remains software/mock evidence, not physical printer/camera qualification.
- [x] QA record only. No production code modified or permission to merge Draft PR #7.

---

## FEAT-008 — user-run Windows hardware adapter tests: 14/14 PASS (2026-10-19)

- [x] **Owner-reported local Windows/Python 3.12 result:** `python -m unittest discover -s tests -p "test_hardware_adapters.py" -v` ran **14 tests / 14 PASS / 0 failures / 0 errors**, using the owner's `.venv-kivy` PowerShell environment. Exact local Git SHA was not included.
- [x] Covered platform-family detection, configured camera/printer descriptors, Linux path and USB model identifiers, Android **unsupported** bridge reporting, backward-compatible health snapshots.
- [ ] **Separate outstanding owner rerun:** `test_device_selection.py` (13 tests) and `test_hardware_discovery.py` (10 tests) after updating to the latest feature branch; the earlier symlink failure on Windows was fixed in test fixtures but this new message does not confirm those suites locally yet.
- [ ] Not physical-device verification: test cases mentioning Linux/Android use synthetic inputs/mocks; real Linux/SBC and Android devices were not tested. Production QRIS and Android native support remain deferred.
- [x] Record-only change; no application code edits or merge approval; Draft PR #7 remains open.

---

## FEAT-008 cross-OS test compatibility — WinError 1314 (2026-10-19)

- [x] **Owner-reported Windows failure:** running `python -m unittest discover -s tests -p "test_device_selection.py" -v` from an unelevated Windows Python 3.12 environment gave 12 tests OK, 1 ERROR: `test_linux_camera_symlink_remains_selected_and_is_not_opened` raised `OSError: [WinError 1314]` in `Path.symlink_to()`. This is a **test-fixture permission issue**, not evidence that the physical camera or device health is broken.
- [x] **Fix:** `tests/test_device_selection.py` and `tests/test_hardware_discovery.py` mock the Linux symlink Path predicates on Windows, but preserve real filesystem symlink tests on Linux; do not require Developer Mode or elevated PowerShell, do not modify runtime camera code.
- [x] **Cross-platform CI:** [GitHub Actions 39223474630](https://github.com/pratikto/PhotoBooth/actions/runs/39223474630) at implementation/workflow SHA `b83074d9a81822ad68b26ad9a9ca7d88bf034652` **PASS on both Windows and Ubuntu**. Each OS runs 25 base health, 14 adapters, 10 discovery and 13 selection tests = **62/62 PASS on each platform**. The workflow now triggers for changes to these modules/tests and explicitly exercises Windows.
- [ ] Owner rerun locally in PowerShell without administrator: both `test_device_selection.py` and `test_hardware_discovery.py` must pass after pulling `feature/device-health`.
- [ ] Hardware and OS acceptance remain distinct: no real Linux V4L camera, printer/cutter, SBC, QRIS or Android hardware was validated by these mocks. Draft PR #7 still must **not** merge without explicit owner permission.

---

## FEAT-008 — owner-reported Windows GUI smoke test: 7/7 PASS (2026-10-19)

**Evidence source:** Owner ran the booth on a Windows laptop and reported the seven results below. This is a **human-reported on-device GUI/diagnostics smoke test**, not independent hardware telemetry, and the exact local commit SHA was **not supplied**. It does not override outstanding physical acceptance or grant merge permission.

- [x] PASS — Aplikasi terbuka normal tanpa error
- [x] PASS — Menu DEVICE HEALTH dapat dibuka
- [x] PASS — Enam status kesehatan perangkat tampil
- [x] PASS — REFRESH STATUS bekerja tanpa membuat GUI macet
- [x] PASS — Daftar perangkat menampilkan printer Windows
- [x] PASS — PILIH DEVICE menampilkan pilihan kamera dan printer
- [x] PASS — Tutup dan buka kembali Health Monitoring tanpa error

**Still unverified:** saving a selected camera/printer, stopping/restarting Meong and verifying the preference is honored; camera USB disconnect/reconnect; printer physical presence, paper-out/cutter and successful printing; Linux/SBC camera/CUPS; Android (deferred until production QRIS works). No test of payment gateway, QRIS settlement, photo quality or end-to-end kiosk purchase flow was reported here.

**Branch gate:** `feature/device-health` Draft PR #7 remains unmerged. No automatic merge/release or source edits are authorized by these PASS reports.

---

## Scope control — Android depends on real QRIS (2026-10-19)

- [x] Owner postponed native Android B.4 until FEAT-020 **real payable QRIS** works and is verified; QRIS DEMO does not meet the gate.
- [ ] FEAT-020 real production QRIS delivery and end-to-end verification (separately planned and approved; not implemented).
- [ ] Explicit owner decision to resume Android after QRIS gate is met.
- [ ] Continue Windows mini PC and Linux/SBC mock/device compatibility work; physical on-device acceptance still pending.
- [x] Documentation-only priority change; no Python/Android code or deployment, no master merge.

---

## FEAT-008 B.2.1 — restart-only primary device selection (2026-10-19)

- [x] Owner asked to continue staged work while Windows/SBC/Android hardware tests cannot yet be conducted. **No merge permission.**
- [x] Strict atomic versioned JSON preferences with unchanged legacy default when no selection exists, next-start-only activation, and explicit cross-OS/missing-alias rejection.
- [x] Windows manual camera indices (unstable), Linux discovered V4L by-id camera aliases, Windows discovered spooler queues only; no unsupported CUPS/Android runtime selections.
- [x] GUI device chooser from Health, available after scan. Stage never closes camera/changes active printer/prints; old Printer Settings overrides staged queue.
- [x] **B.2.1 exact implementation SHA `e6798c17` CI PASS:** [Dedicated device tests 39206664105](https://github.com/pratikto/PhotoBooth/actions/runs/39206664105) **62/62 PASS** (25 base + 14 adapter + 10 discovery + 13 staged selection). [Kiosk GUI 39206664043](https://github.com/pratikto/PhotoBooth/actions/runs/39206664043) **313 run / 311 PASS / 2 SKIP / 0 failures/errors; 87 synthetic renders / 0 errors**, including staged-picker UI tests. Later docs-only evidence commit does not modify tested Python code.
- [ ] **Owner physical acceptance deferred**: Windows manual index reconnect/reboot and printer queue physically unavailable; SBC V4L/by-id camera/CSI driver and CUPS/USB; Android native bridge. Do not infer READY.
- [ ] **Merge gate:** explicit owner authorization required even if CI PASS.

---

> **Latest B.1/B.2 safety correction CI (2026-10-19):** On `feature/device-health` source/test SHA `b5617679960c585a6fe6ccec298fc4ba31591ae7`, [Device Health Actions 39205072276](https://github.com/pratikto/PhotoBooth/actions/runs/39205072276) **49/49 PASS** (25 original + 14 adapters + 10 discovery). [Kiosk GUI Actions 39205072279](https://github.com/pratikto/PhotoBooth/actions/runs/39205072279) **294 tests / 292 PASS / 2 SKIP, 87 renders / 0 errors**. Printer route probing **and Windows queue discovery** both skip whenever a photo print is in flight. These are mocked Ubuntu CI results, not physical acceptance; docs-only commit after this does not alter tested code. PR #7 stays Draft, unmerged.

## FEAT-008 B.1/B.2 capability/discovery — verified mock QA (2026-10-19)

- [x] Owner approved staged cross-platform development on existing branch `feature/device-health`; PR #7 is Draft, **no merge authorization**.
- [x] B.1 platform/capability descriptors, Android `UNKNOWN` device bridges, no fake stable camera index or USB vendor/product identity.
- [x] B.2 read-only Windows print queue, Linux V4L/by-id candidate, USB node and time-bounded CUPS queue discovery, with **no camera open and no test print**, limited to operator health scans in the worker.
- [x] [Dedicated GitHub CI 39204278785](https://github.com/pratikto/PhotoBooth/actions/runs/39204278785) on exact tested source SHA `6cb4263e97a31cfd2d74a6e0eb2ae6329232269c`: **25 Stage A + 14 adapter + 9 discovery = 48/48 mocked tests PASS** (Ubuntu Python 3.12). Later documentation/source SHA needs its own CI confirmation.
- [x] Full [Kiosk GUI Actions 39204601283](https://github.com/pratikto/PhotoBooth/actions/runs/39204601283) on exact tested source SHA `f8c96a40c7f9fa0a10c7af43f8569b22d78e10a9`: **293 tests / 291 PASS / 2 SKIP / 0 errors or failures, 87 synthetic renders / 0 errors**. Later QA-documentation-only commits do not change the tested Python implementation.
- [ ] Windows physical operator test: compare configured queue vs Windows discovery with real printer connected/disconnected; camera preview and other customer flows unaffected; check disk low warning. Test against actual booth hardware.
- [ ] Linux/SBC physical V4L2, libcamera CSI, queue/node permissions and ESC/POS print output; **not tested** by Ubuntu mocks.
- [ ] Android Camera2 native bridge/permissions, USB Host SDK and packaging; **not implemented or tested**.
- [ ] Safe persistent primary-camera/printer selection for changed devices; **not yet implemented** (existing printer Settings remains, camera index remains env-selected).
- [ ] Explicit separate owner approval before merging/releasing FEAT-008 to `master`.

---

## FEAT-008 Stage B — branch-only GUI/worker regression (2026-10-19)

- [x] Owner approved Stage B on existing `feature/device-health` **without merge authorization**. Prior Stage A PR #5 was reverted out of `master` in [PR #6](https://github.com/pratikto/PhotoBooth/pull/6).
- [x] Kivy Settings now includes DEVICE HEALTH dialog with six statuses, automatic single scan on open, manual REFRESH, scrollable content, and close; main photo GUI is not replaced.
- [x] Probe submission occurs via a daemon worker with Kivy main-thread callback, no new monitoring timer, print-in-flight guard, no automatic printing and stale-popup result rejection.
- [x] **Stage B code Kiosk GUI CI:** on source/tree code SHA `f93dd88ad5435349ff71c9351aaf0430edd74525`, [GitHub Actions 39197763624](https://github.com/pratikto/PhotoBooth/actions/runs/39197763624) **270 tests / 268 PASS / 2 SKIP / 0 FAIL or ERROR, 87 GUI renders / 0 render errors**. New `tests/test_device_health_gui.py` is opt-in under `PHOTOBOOTH_TEST_GUI=1`; all tests run on synthetic Kivy/Xvfb, not on the user's Windows hardware. The later branch documentation-only commits do not change tested implementation code; final PR HEAD CI must be verified separately.
- [x] **Isolated Stage A regression:** [GitHub Actions 39197763719](https://github.com/pratikto/PhotoBooth/actions/runs/39197763719) at code/test SHA `f93dd88ad5435349ff71c9351aaf0430edd74525` **25/25 PASS**, including skipping spooler checks during an active print. Later doc-only SHA reruns tracked by PR checks.
- [ ] **Owner Windows trial:** Settings → DEVICE HEALTH; refresh twice, close/reopen; check existing camera and real printer not blocked; video/Drive/cutter physical status not verified by probe.
- [ ] **Merge:** NOT AUTHORIZED; keep the draft PR unmerged until explicit owner approval.

---

## FEAT-008 Stage A — source / test checklist (2026-10-19)

- [x] Owner-approved backend-only scope and isolated branch `feature/device-health` from `master` `abbdb0d6b0d97a796da14b7edabf21252892c9cb`.
- [x] Non-invasive checks implemented: existing-frame camera, printer TCP/queue/device-node visibility with **zero print commands**, disk, short TCP network reachability, local ad files, optional heartbeat.
- [x] New no-hardware unit tests added in `tests/test_device_health.py` (check results against actual CI after PR). No GUI changes or app startup wiring.
- [x] **Targeted test evidence:** `python -m unittest discover -s tests -p test_device_health.py -v`, Python 3.12 Ubuntu GitHub Actions [39192498537](https://github.com/pratikto/PhotoBooth/actions/runs/39192498537): **24 tests / 24 PASS**, no skips/errors. Tested source/workflow SHA `3ae31dfc933352c293eed682c72f4f8afb6020c`. Later documentation commits require separate full-PR regression check; no Windows physical probes were run.
- [x] **Full Kiosk regression on Stage A code/test SHA `5512ccfd242bed9b8034bf5d9e86652b6c9afbbe`:** Ubuntu/Python 3.12 [Actions 39192396595](https://github.com/pratikto/PhotoBooth/actions/runs/39192396595) **259 tests run / 257 PASS / 2 SKIP / 0 errors or failures; 87 GUI renders / 0 render errors**. The later workflow/docs commits did not change the Stage A application module or tests; GitHub should separately confirm green checks on the final PR SHA.
- [ ] Stage B dedicated admin Settings UI — requires new approval.
- [ ] Stage C physical Windows printer, camera, network and media tests — requires new approval and owner evidence.

See [implementation and limitations](device-health.md). `v1.0.0` remains the independently tagged source baseline; **never claim hardware READY** from successful mocked checks.

---

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
