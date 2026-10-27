# Android parallel development

**Android runtime continuation — 28 October 2026:** The owner now authorizes the full Android v2 runtime with built-in camera, USB OTG printing and Sandbox. The earlier A0/A1 offline plans/results below remain historical; the packaged entry has changed. New build/device verification is tracked separately.
[Scope, setup and source evidence](android-v2-runtime.md).

**Current A1 build result — recorded 28 October:** functional source 293b22b
compiled a signed arm64 debug APK on 27 October. Signature v2 valid; zero requested permissions; 144 AArch64 ELF libraries; 65 exact asset hashes; all twelve original template masters and .b85 game artwork; 16 KB ZIP alignment PASS.
[Build guide and current evidence](android-build-readiness.md). Native Android
installation, camera, sound/video, printing, Drive and provider acceptance stay
NOT_RUN. The earlier A0 plan/results below are retained as dated history.

**Current continuation (27 October):** the owner requests APK build readiness
on this existing branch, without creating another development branch. A1 pins
the native toolchain, fixes missing original-game artwork in staging, reuses
the current GUI v2 five-image carousel and adds isolated staged-app checks.
Use [the current build guide and verification](android-build-readiness.md);
the original A0 record below remains dated evidence, including its NOT_RUN
APK result. The current recipe requires API 24+, superseding A0's API 23 candidate.

Owner authorization: **27 October 2026, Asia/Jakarta** — create a new branch and
develop Android in parallel, with staged Git pushes. Branch
`feature/portrait-kiosk-android` starts from desktop checkpoint
`fcabfbb8559778055631ff3a066f14108392ef71`. Remote desktop HEAD was refreshed and
matched; no pre-existing Android branch was found. Windows/Ubuntu development
remains on `feature/portrait-kiosk-v2-next`; master and desktop launchers remain
unchanged. Android code is an opt-in host of shared v2 modules, not a second UI.

## Documentation and source review

Read AGENTS, documentation index, protocol, current handover, architecture,
engineering contracts, decisions, backlog, source/acceptance status and test
ledger before code. Existing shared printer and platform adapters distinguish
Windows/Ubuntu behavior from unimplemented Android native bridges. Parallel
read-only dependency audit confirms no existing Android launcher/Buildozer spec.
Reused source: actual PortraitKioskV2App, original Meong Fly scene/renderer,
gallery, twelve approved template masters, tutorial/visit guards and DEMO ledger.
All `old` contents are excluded. No account/service deployment is performed.

## Original A0 stages and boundaries (retained history)

| Stage | Deliverable | State |
| --- | --- | --- |
| A0 | Offline Android preview host, private data root, curated package, Buildozer spec and Linux UI reuse checks | Implemented; native Android build/device gates remain NOT_RUN |
| A1 | Verify SDK/NDK/p4a recipes; produce/install debug APK; test orientation, touch, Back/Home/resume and private persistence | Next; not certified by a desktop screenshot |
| A2 | Camera2/native camera bridge, runtime permission, rotation, original JPEGs, preview/review parity and retake | Future; camera is disabled in A0 |
| A3 | Native audio/video and device-tested LAN/USB printer transports | Future; desktop OS drivers are not Android adapters |
| A4 | Optional Drive and hosted authenticated Sandbox client with durability/recovery gates | Future; no production payment or embedded merchant key |

A0 mounts the **same real UI** for bundled still ads, tutorial, template browsing
and original DEMO game. Source-relative artwork stays packaged; mutable events,
game/MOCK/report state is redirected to app-private storage before build across
all six modules holding imported PROJECT_ROOT constants. It never opens desktop
camera, face/palm detectors, printer, Drive, payment or operator device probes.
The disabled gallery camera action says KAMERA BELUM AKTIF. Audio/video are off
for this first preview. No synthetic photo success is presented as native capture.
Existing demo reward remains a simulation, never merchant authority.

The Android entry obtains `android.storage.app_storage_path()` before Kivy loads,
sets its private KIVY_HOME and reuses normal pause/resume/worker teardown.
No desktop subprocess watchdog/systemd launcher is called. Existing Android
hardware descriptors remain truthful about unavailable native bridges.

## Prepare the build project

From this Android branch, using Python/Git (Windows or Linux):

```bash
python tools/prepare_android.py --output-dir work/android-project
```

Choose a new destination on each run; existing directories are never overwritten.
The tool takes only tracked photobooth Python files and runtime assets, excluding
local_settings, user data, archives, virtualenvs and local videos. Links/junctions
are rejected. It copies `android/main.py` as the staged root main.py and emits a
source/assets hash manifest. Never point Buildozer at the repository root: that
root's main.py is the legacy desktop launcher, and local private state must not
enter an APK. The packaging test verifies this boundary.

## APK build — not yet executed

Use Ubuntu or **WSL2 on Windows** for python-for-android/Buildozer. Install its
documented Linux build prerequisites, JDK and Android SDK/NDK; the exact toolchain
and native recipes must be verified at A1. Do not copy a Windows venv into WSL.
Use a dedicated build environment and review Android SDK license prompts locally.

```bash
python3 -m venv work/android-build-venv
source work/android-build-venv/bin/activate
python -m pip install buildozer
cd work/android-project
buildozer android debug
```

The initial spec targets portrait arm64-v8a, API 35/minimum 23. These are initial
build candidates, not a validated Android version/device matrix. It includes
Kivy/Pillow/numpy/requests/qrcode/tzdata, native sqlite3 and pyjnius recipes.
Numpy is required by the reused legacy-audio import seam even while playback is
off. Desktop pywin32/OpenCV-contrib/python-escpos/ffpyplayer are not copied from
requirements.txt. KIVY_VIDEO=null uses the verified Kivy null provider.
The A0 spec requests no camera, Internet, USB or shared-storage access; inspect
the merged APK manifest at A1, since a build tool/recipe may add defaults.
SDK license auto-accept is off. No release signing key, package publication,
background service or production endpoint is supplied.

No Buildozer executable/Android SDK was available in this cloud environment.
**APK compilation, installation and Android hardware behavior are NOT_RUN.**
Linux native screenshots prove code reuse/layout only. They do not prove a
successful Android recipe build or device camera/audio/touch performance.

## Automated verification and staged delivery

Stage 1 source checks: five stdlib packaging/policy tests pass; real Kivy tests
pass at 452×900 and 800×1280. Six native views cover idle/gallery/game intro;
compact gallery and portrait game intro were inspected. A readiness bug found
by the native test was fixed in the Android subclass: the existing `_update_order`
can re-enable photo controls after quantity changes, so the Android override
applies its camera gate there, preserving the original carousel signature.
Direct capture entry is also blocked. Desktop modules are not edited for this.

```bash
python -S -m unittest tests.test_android_preview -v
PHOTOBOOTH_TEST_ANDROID=1 python -m unittest tests.test_android_widgets -v
ANDROID_PREVIEW_WIDTH=800 PHOTOBOOTH_TEST_ANDROID=1 python -m unittest tests.test_android_widgets -v
```

Android CI runs these policies/staging checks and real reused widgets on Linux.
It does not claim to compile an APK. The existing desktop workflow is not added
to the Android push branch; this avoids redundant unrelated native builds.
One final complete regression is recorded separately after completion.
Staged delivery: first push A0 source/docs/focused checks; then evidence-only
push after full regression/CI. No successful workflow is rerun for documentation.

Rollback: switch back to the existing Windows/Ubuntu branch, preserving its data.
Android package/private data are separate. Never erase journals, game claims or
uncertain jobs to pass a check. Future shared fixes should be reviewed as small
portable commits instead of blindly merging one platform branch into another.

## Final A0 evidence and staged publication

**Stage 1:** `0cacc272625f83d495117ed8a814edfa02d70500` pushed to the new Android
branch and remote HEAD verified. Desktop's branch remained `fcabfbb` at the fork.
Five [policy tests](qa/android-preview/policy-tests.txt) PASS and real-widget
checks PASS at [452×900](qa/android-preview/native-452.txt) and
[800×1280](qa/android-preview/native-800.txt). Six synthetic screenshots are
preserved in [the QA directory](qa/android-preview/); compact gallery and portrait
game intro were reviewed. These are Linux/Kivy fixtures, not Android screenshots.

**Final regression:** [875 cases](qa/android-preview/full-tests.txt), **872 PASS /
3 optional palm-assets SKIP / zero failures/errors**, 266.642s. Command in the
existing headless environment with command network permission for local ASGI:
`PHOTOBOOTH_TEST_ANDROID=1 PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1 python tools/run_kiosk_unittests.py`.

**Matching source CI:** [40425864227](https://github.com/pratikto/PhotoBooth/actions/runs/40425864227)
SUCCESS at `0cacc27`, validating policy/staging plus the real UI at both sizes
without installing desktop ffpyplayer/OpenCV. [Job record](qa/android-preview/final-ci.json).
[Source/render hashes and limits](qa/android-preview/verification.json).

**Stage 2:** evidence-only documentation push; no redundant successful CI rerun.
Shared desktop production modules/entry points remain unchanged. APK compilation,
native recipes and physical Android camera/audio/touch/device acceptance remain
NOT_RUN. The next Android increment is A1 toolchain/APK validation; the first
preview must not be presented as a working Android camera/printing release.
