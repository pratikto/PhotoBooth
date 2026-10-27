# Android A1 — APK build readiness

Owner continuation, 27 October 2026 (Asia/Jakarta): continue the existing
`feature/portrait-kiosk-android` to APK build readiness, follow current GUI v2,
read documentation comprehensively, and create no new development branch.
Base/rollback: `c10f9dd4d25e7b14c59021eae5fc30f6c6952025`.

## Review before implementation

Reviewed AGENTS, root README, documentation index, protocol, continuation prompt,
handover, architecture, decisions, feature/bug/backlog/test ledgers, Android
A0 scope/evidence, v2 roadmap/technical/visual specifications and artwork
provenance, reference-branch audit/promotion plan, storage/retention contracts,
P3/print-Drive/mirror, original-game reuse, Sandbox/P5/pending acceptance and
recovery runbooks. Historical P2 gates/integration plans remain dated history.
The entire `old` archive is excluded.

Refreshed existing Android and desktop remote tips. Current desktop reference:
`a62721fe185d360367472e968ca7ec2f97823c50`; reviewed the held-carousel and
console-logging correction contracts before borrowing source. Reuse the actual
five-image carousel (`eb0297d`) through the existing shared app, not a new UI.
Delivery-only desktop changes remain outside the offline Android profile.

## Acceptance and implementation scope

- Curated staged package must run independently of the source checkout, with
  all original game artwork, twelve templates and tutorial/gallery/game flow.
- Pin and verify native toolchain requirements, provide repeatable Ubuntu/WSL2
  debug-build commands, and attempt a real arm64 APK build.
- Preserve app-private state, consumed attempts, pause/resume and worker cleanup;
  Back must not silently abandon an active game or erase state.
- Keep native camera, printer, Drive, scanner and provider gates truthful.
  A buildable preview is not a camera/printing release or hardware acceptance.
- Run focused package/native checks and one final applicable regression; record
  exact results and blockers. Preserve desktop/master and their entry points.

Rollback uses scoped inverse commits on this same Android branch and retains
all private state. No operational cloud/provider deployment or data migration.

## Results

Implementation and verification in progress. No new APK success is claimed yet.

Initial focused verification: **8 Android policy/native tests PASS**, zero
skips/failures/errors (11.908s). This includes a completely isolated staged-app
subprocess, original camera-art decoding, actual DEMO claim, Back pausing active
gameplay, Home-style pause/resume retaining pause, and duplicate-code rejection
after reopening the private SQLite ledger. Earlier combined carousel regression:
41 cases / 39 PASS / 2 opt-in SKIP, no failures/errors (37.760s); the two cases
need audio and optional palm fixture opt-ins. Final full results follow below.
Fresh native captures have asserted **452×900** and **800×1280** stage sizes;
gallery and original game intro were reviewed at both required sizes.

## Build on Ubuntu / WSL2

Use the existing Android branch. Native Windows is not a python-for-android
build host; keep the checkout/build on the WSL Linux filesystem. Host Python
3.12, JDK 17, roughly 15 GB free disk and network access are required.

```bash
sudo apt-get update
sudo apt-get install -y git zip unzip autoconf automake libtool pkg-config \
  cmake make gcc g++ patch openjdk-17-jdk python3.12-venv \
  libffi-dev libssl-dev zlib1g-dev
python3.12 -m venv work/android-build-venv
work/android-build-venv/bin/python -m pip install -r android/requirements-build.txt
work/android-build-venv/bin/python tools/build_android.py --accept-sdk-license
```

The last flag explicitly accepts SDK licenses for automatic SDK installation.
Without it Buildozer retains its interactive license prompts. Choose JDK 17 in
JAVA_HOME if the host has multiple JDKs. Never copy a Windows venv into WSL.
Ubuntu versions without a Python 3.12 package need an existing Python 3.12
installation; the manual workflow below already supplies it.

Native toolchain: Buildozer **1.6.0**, host Cython **0.29.37**, host setuptools
**80.9.0**, p4a **v2026.05.09 / 58d21141f17c889bf8585f5665921d72028f8831**,
NDK **r28c / 28.2.13676358**, Android target **35**, minimum/NDK API **24**,
**arm64-v8a**, Kivy **2.3.1**. The pinned p4a uses Python **3.14.2** in the APK
and its own recipe build environments; host Python/Cython are separate.
Its numpy recipe requires minimum API 24 (Android 7), so A0's API 23 candidate
cannot be retained. No x86/32-bit APK or Play Store release is implied.

The helper creates a fresh curated `work/android-project`, never builds the
desktop root main.py, and keeps caches in `work/android-build-cache`. To retry
an unchanged package add `--resume`. When source changes, choose a fresh
`--project-dir work/android-project-next`; resume refuses mismatched hashes.
Do not delete private app data/journals to resolve build or device problems.

Existing official SDK/NDK installations are supported without redownload:

```bash
work/android-build-venv/bin/python tools/build_android.py \
  --sdk-dir /absolute/path/to/sdk \
  --ndk-dir /absolute/path/to/sdk/ndk/28.2.13676358 --accept-sdk-license
```

Install platforms;android-35 and build-tools;35.0.0 in that SDK first. The
helper supports official cmdline-tools/latest/bin/sdkmanager and the legacy
tools/bin location. An optional --p4a-dir must match the pinned Git commit.
HTTP/HTTPS proxies and CA trust remain inherited. Java/Gradle additionally
need the environment's configured Java proxy/trust-store options where used;
never disable TLS verification. Build failures omit full environment dumps.

## Manual GitHub build

Actions → **Android preview foundation** → Run workflow → select
**feature/portrait-kiosk-android** and enable **build_apk**. Or use the existing
registered workflow from GitHub CLI:

```bash
gh workflow run android-preview.yml --ref feature/portrait-kiosk-android -f build_apk=true
```

The APK job runs only on explicit manual dispatch, to preserve Actions credits.
It calls the reusable **Build Android debug APK** workflow on the same source.
A newly added dispatch-only workflow on a nondefault branch is not registered
automatically; reusing the already registered preview workflow avoids requiring
a master/default-branch change. The job provisions Ubuntu 24.04/Python 3.12/JDK 17/official SDK,
checks packaging, compiles, verifies debug signing and uploads
**meong-android-debug** (APK, source hashes, build log, manifest and SHA-256).
Automatic A0 policy/native CI remains independent; green preview CI alone
does not certify the separate APK workflow.

## Install and acceptance

The APK is in the selected project's bin/ directory. With Android platform-tools:

```bash
adb install -r work/android-project/bin/<generated-debug-name>.apk
adb shell am start -n id.meong.meongpreview/org.kivy.android.PythonActivity
adb logcat -s python PythonActivity SDL
```

Use -r to preserve existing app-private state/consumed DEMO codes. Do not
uninstall or clear storage to grant another attempt. Verify on an arm64 Android
7+ device: launch/portrait, tutorial once, all twelve designs/held swipe,
original DEMO game/one-use code, Back pauses active gameplay, Home/resume
requires manual game resume, force-stop/relaunch preserves consumed attempts.
Check real display insets, keyboard and touch on the actual device.

Camera, live face/palm, print, Drive, provider checkout, scanning, sound/video
remain disabled in this offline profile. The gallery explicitly says KAMERA
BELUM AKTIF; no synthetic capture/paid/printed/uploaded success is invented.
Their native adapters are A2–A4, separate from debug APK build readiness.
No release key, store publication, device-owner kiosk lock or deployment is supplied.
