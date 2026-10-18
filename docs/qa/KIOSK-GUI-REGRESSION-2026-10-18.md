# Kiosk GUI Regression — 2026-10-18 iterative repair and verification

**Branch:** `feature/kivy-gui` · **Source/test verification SHA:** [`f129dd9e`](https://github.com/pratikto/PhotoBooth/commit/f129dd9ecb14b2d554dd83022745452764f5282d)  
**Final verified workflow:** [Kiosk GUI regression Actions run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476) — **SUCCESS**  
**Environment:** GitHub Actions `ubuntu-latest`, Python 3.12, Xvfb, Kivy software OpenGL, dummy sound driver, mock camera/Drive/payment/printer, synthetic image assets.  
**Verification command:** `xvfb-run -a python tools/run_kiosk_unittests.py` in `.github/workflows/kiosk-gui.yml` followed by `xvfb-run -a python tools/render_gui.py --output-dir /tmp/meong-gui-qa` and `python tools/ci_visual_summary.py /tmp/meong-gui-qa`.

## 1. Outcome and evidence boundaries

| Check | Result at `f129dd9e` | Interpretation |
| --- | --- | --- |
| `python -m compileall -q photobooth tests tools` | **PASS** | Syntax for production modules, tests and tooling |
| Full unittest discovery via diagnostic runner | **PASS: 232 executed, 230 passing, 2 skipped; 0 failures, 0 errors** | Unit and synthetic GUI behavior for present source code |
| Kiosk synthetic renders | **PASS: 87 screenshots, 0 reported errors** | Kivy desktop layouts, QR decode checks and simulated states in supported test matrix |
| Kiosk GUI workflow overall | **SUCCESS** ([run](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476)) | Full CI gate green at that SHA, not production release |
| Dither tuning lab regression | Continued **PASS** on intermediate code/test-only commits | Independent lab testing; not live thermal-paper test |
| Windows printer/camera/audio, actual QRIS settlement | **NOT EXECUTED by this CI** | Existing owner-accepted FEAT-001/003 device evidence is separate; real QRIS is still DEMO |

**Precise CI log evidence:**
`Ran 232 tests in 101.275s`; `KIOSK_UNITTEST_SUMMARY: run=232 failures=0 errors=0 skipped=2 success=True`; `MEONG_GUI_REPORT:{"renders": 87, "errors": []}`. The two skipped cases are ordinary unittest skips; no production device claim is inferred from CI green.

**Limit:** Status applies to **tested commit `f129dd9e`**, and newer documentation-only commits must be checked against their own GitHub run before assigning a current-HEAD green status. No merge to `main`, release, deployment, Windows-driver rewrite or customer-data use is authorized.

## 2. Investigation history and diagnostic reliability

- Older [Kiosk GUI run 39141592635](https://github.com/pratikto/PhotoBooth/actions/runs/39141592635) returned FAIL from `python -m unittest discover -s tests -v`, but unittest tracebacks were missing from the Actions console because Kivy redirects Python stderr. Syntax checks and visual screens could pass while unit tests failed.
- [`88f517ea`](https://github.com/pratikto/PhotoBooth/commit/88f517ea8a3e5360da4213964984c426717a6690) attempted enabling Kivy console logging; this **did not** expose the failure details.
- [`28745cda`](https://github.com/pratikto/PhotoBooth/commit/28745cdabdee69bcd7c21e79aba611c2d2aa4dc8) adds `tools/run_kiosk_unittests.py`, a standard unittest TextTestRunner that writes the report directly to OS stdout using `os.write(1, ...)` and optionally saves `/tmp/meong-kiosk-unittests.txt` for artifact access. [`9dcebfd2`](https://github.com/pratikto/PhotoBooth/commit/9dcebfd27d9e0f22688cecf9842fef9764fd2978) wires this runner and uploads the report alongside visual screenshots.
- First new-run failure was **diagnostic-runner import configuration only**: invoking `tools/*.py` made the repo package unavailable. [`b5a9ee1a`](https://github.com/pratikto/PhotoBooth/commit/b5a9ee1a6bb0e09a2af78ec31ed0389a1f8d1d92) restores the repository to `sys.path`; [`2efb76d7`](https://github.com/pratikto/PhotoBooth/commit/2efb76d796b120fe400361044c427dccce19f827) restores the original test directory's non-package unittest discovery semantics.
- The readable baseline at `2efb76d7` now showed **232 tests: 17 failures, 0 errors, 2 skipped**. Unlike an infrastructure import error, these 17 were concrete assertions against old pricing, old ad/navigation flow, old Settings menu, and unmocked Windows sender.
- A later [intermediate run 39144022412](https://github.com/pratikto/PhotoBooth/actions/runs/39144022412) reduced failures to **four**; the visual suite already reached **87 renders / 0 errors** on that intermediate run. An earlier intermediate run had intermittently failed QR decode in `payment-enlarged-800x600` during screenshot analysis; the complete final run passed that same full render matrix. **No QR rendering production patch was made**, so monitor if that intermittent case recurs rather than misrepresenting it as a separately fixed cause.
- Final [run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476) is **fully green**; no tests were disabled to achieve it and the two skipped tests remain identified by the normal unittest runner.

## 3. Changes applied, grouped by reason

### A. FEAT-001 DEMO pricing and session-count expectations

**Contract preserved:** each **selected template = one three-photo session**, regardless of requested paper copies; total **Rp5,000 per chosen template + Rp5,000 per printed copy**. No actual QRIS integration.

- [`9e252f66`](https://github.com/pratikto/PhotoBooth/commit/9e252f6690d16d90a3402fad3bf8dd2bba0c60ac): camera recovery uses *two chosen templates* when testing two sessions instead of assuming two prints create two photo sessions; updates cart totals, pending/old callback assertions and quantity preservation.
- [`0a765189`](https://github.com/pratikto/PhotoBooth/commit/0a7651895f4951177f814122b6e7031bd30b705e): carousel cart totals, per-copy labels and responsive behavior align with FEAT-001 quote.
- [`26ac53e4`](https://github.com/pratikto/PhotoBooth/commit/26ac53e43735b0126d96c9f111486f5ab887fb92): audio/motion GUI tests that inspect cart totals now expect FEAT-001 amounts.
- These are assertion/fixture updates; the pricing constants, actual print-copy batching and photos remain unchanged.

### B. Approved advertising → tutorial → templates navigation

- [`600a94ec`](https://github.com/pratikto/PhotoBooth/commit/600a94ec86fd1ffc43fd9186af330204857fe54e) and [`4c16d239`](https://github.com/pratikto/PhotoBooth/commit/4c16d23992e1d369c1142318f8f61b71ad292e99): both manual advertising entry and controller face invitation must show the tutorial *before* opening the template picker; test both transitions.
- [`47c6be48`](https://github.com/pratikto/PhotoBooth/commit/47c6be48d9d699f765a9cf41c61fb7e082523870): when camera is missing, tutorial Start stays disabled; once camera becomes ready, Start enables and the user can proceed. This preserves the existing safety gate; no bypass to make CI green.

### C. Settings submenu and explicit music audition

- [`35b2c1f3`](https://github.com/pratikto/PhotoBooth/commit/35b2c1f3d038ef95a41f76e9da36e17b34c26246): tests now tap the **gear → general Settings menu → Pengaturan Audio** path and verify real pointer interaction before examining sliders, including across all tested screens.
- [`f129dd9e`](https://github.com/pratikto/PhotoBooth/commit/f129dd9ecb14b2d554dd83022745452764f5282d): an explicit operator **UJI MUSIK** tap deliberately restarts the native music handle for audible testing, even while ordinary background-music playback does not rewind. Validate one extra playback per explicit tap rather than expecting the original loop never to restart.

### D. Asynchronous print gating and fake Windows queue

- [`9826d3cf`](https://github.com/pratikto/PhotoBooth/commit/9826d3cf95bdde0f297bb26af6ada914f0a396a5): transaction-completion/stale-button tests now explicitly simulate **accepted transport** so that they exercise their intended screen/transaction guards. The production FEAT-001 result-page NEXT/SELESAI protection remains **busy until print job outcome**; this protection has its own independent tests and is not disabled.
- [`11587cb8`](https://github.com/pratikto/PhotoBooth/commit/11587cb8924e53a17e358b937b5aace0911a7516): Windows QR-slip routing test mocks **only** the printer module's OS platform indication plus `_send_windows_raw`, to exercise the Windows spooler branch on Linux CI without rewriting global `os.name` and breaking `pathlib`.

## 4. Scope and regression safety

**Source files changed in this QA repair:** `tests/test_camera_recovery.py`, `tests/test_carousel.py`, `tests/test_kiosk_motion_audio.py`, `tests/test_kiosk_advertising.py`, `tests/test_kiosk_controller.py`, `tests/test_shared_printer_payment.py`, `tools/run_kiosk_unittests.py`, and `.github/workflows/kiosk-gui.yml`.

**No changes:** `photobooth/*.py` production modules, ESC/POS byte pipeline, Windows print queue handling, previously accepted Floyd settings, mirror camera UV logic, live camera worker, `apps_script/Code.gs`, demo payment behavior, adverts, audio engine or customer data.

**Existing issues remain distinct:** BUG-009 cloud-photo 30-day deletion/registration remains OPEN and owner-deferred with FEAT-004. Audio BUG-001/007 intentionally deferred; an automated audio mock PASS does not imply speakers work in the booth. FEAT-001/BUG-011 paper count and FEAT-003 mirror remain owner-tested PASS, but real hardware acceptance remains separate from CI.

## 5. Re-run, ongoing monitoring and rollback

On GitHub: run [Kiosk GUI regression](https://github.com/pratikto/PhotoBooth/actions/workflows/kiosk-gui.yml) on the appropriate branch; confirm **final commit SHA**, `KIOSK_UNITTEST_SUMMARY`, `MEONG_GUI_REPORT`, and whole workflow SUCCESS. Do not use the success of a previous SHA as proof for later commits.

On a configured Windows dev machine:
```powershell
git status
git switch feature/kivy-gui
git pull --ff-only origin feature/kivy-gui
$env:PHOTOBOOTH_TEST_GUI = "1"
$env:PHOTOBOOTH_TEST_AUDIO = "1"
$env:PHOTOBOOTH_TEST_VIDEO = "1"
python tools/run_kiosk_unittests.py
```
The Kivy full suite requires suitable desktop dependencies/graphics runtime and may use mocked adapters. Do not run tests against production transactions or camera/printer hardware without an isolated environment.

**Rollback:** Do not reset `feature/kivy-gui` or lose unrelated accepted changes. If a QA runner change regresses, narrowly revert its test/tool/workflow commit after owner review; do not revert stable application features. Since this stage changed no production code, the core booth has no runtime modification to roll back.

**Disposition:** The specific **Kiosk GUI regression quality gate is VERIFIED PASS at `f129dd9e`**. This is not permission to mark the whole Meong Photobooth `RELEASED`, close unrelated bugs, or start another feature without explicit owner approval.
