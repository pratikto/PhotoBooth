# Android A1 — APK build readiness

**Android runtime continuation — 28 October 2026:** The current 0.2.0 packaged entry is Android v2 runtime with CAMERA/INTERNET and native camera/USB/Sandbox support. The zero-permission 0.1.0 APK evidence below identifies historical source 293b22b only; it is not evidence for this new runtime. New native build verification is in progress.
[Scope, setup and source evidence](android-v2-runtime.md).

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

**Debug APK build VERIFIED on functional source 293b22b**, observed 27 October
2026; final evidence published 28 October. Signature v2 valid; zero requested permissions; 144 AArch64 ELF libraries; 65 exact asset hashes; all twelve original template masters and .b85 game artwork; 16 KB ZIP alignment PASS.

Package id.meong.meongpreview; Android minimum API 24 / target API 35;
arm64-v8a. The inspected APK is 42,731,442 bytes; SHA-256:
`ec5d4fca5bbafc467605697cf1298eca6fc06c29077c72d5aeaa964eb083bc59`.
[Structured build evidence](qa/android-build/apk-verification.json).
Other machines' debug keys/build metadata can change APK bytes; this identifies
the inspected artifact, not every future rebuild.

Matching-source [preview CI 40495526267](https://github.com/pratikto/PhotoBooth/actions/runs/40495526267)
is SUCCESS at 293b22b. The last recovered complete local result is 881 run /
878 PASS / 3 optional palm-assets SKIP / zero failures/errors at 6260435.
Nine packaging-policy tests passed after the final build corrections.
A further full run at 293b22b was launched; its final summary has not been
recovered after the cloud restart and is not counted as a confirmed PASS.
APK inspection and CI results remain independently verified.

The APK binary remains in the previous cloud build workspace, which is not
currently accessible. It has not been published as a release or attached to
this repository. Use the manual workflow below to produce a downloadable
`meong-android-debug` artifact. Actual Android install/device acceptance is NOT_RUN.

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
  cmake make gcc g++ patch curl openjdk-17-jdk python3.12-venv \
  libffi-dev libssl-dev zlib1g-dev
python3.12 -m venv work/android-build-venv
work/android-build-venv/bin/python -m pip install -r android/requirements-build.txt
mkdir -p work/android-sdk
curl -fL https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip \
  -o work/android-commandlinetools.zip
unzip -q work/android-commandlinetools.zip -d work/android-sdk
mkdir -p work/android-sdk/cmdline-tools/latest
mv work/android-sdk/cmdline-tools/{bin,lib,NOTICE.txt,source.properties} \
  work/android-sdk/cmdline-tools/latest/
work/android-sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root="$PWD/work/android-sdk" \
  'platform-tools' 'platforms;android-35' 'build-tools;35.0.0' 'ndk;28.2.13676358'
work/android-build-venv/bin/python tools/build_android.py \
  --sdk-dir work/android-sdk --ndk-dir work/android-sdk/ndk/28.2.13676358 \
  --accept-sdk-license
```

Review/accept SDK licenses when sdkmanager prompts. The last helper flag also
permits Buildozer SDK license prompts; without it they remain interactive.
Use the current official command-line tools above (revision 13114758 / 19.0),
matching the local validation. Buildozer's default SDK bootstrap is older and is
not the validated path. Choose JDK 17 in
JAVA_HOME if the host has multiple JDKs. Never copy a Windows venv into WSL.
Ubuntu versions without a Python 3.12 package need an existing Python 3.12
installation; the manual workflow below already supplies it.

The `latest` directory is required by pinned p4a's `get_targets`, even though
the Buildozer wrapper itself can locate `cmdline-tools/bin/sdkmanager`. A fresh
runtime build reproduced that mismatch; installing the official tools in their
standard `cmdline-tools/latest` layout resolves target discovery. These setup
commands assume a fresh SDK directory; preserve existing installations.

Native toolchain: Buildozer **1.6.0**, host Cython **0.29.37**, host setuptools
**80.9.0**, p4a **v2026.05.09 / 58d21141f17c889bf8585f5665921d72028f8831**,
NDK **r28c / 28.2.13676358**, Android target **35**, minimum/NDK API **24**,
**arm64-v8a**, Kivy **2.3.1**. The pinned p4a uses Python **3.14.2** in the APK
and its own recipe build environments; host Python/Cython are separate.
Its numpy recipe requires minimum API 24 (Android 7), so A0's API 23 candidate
cannot be retained. No x86/32-bit APK or Play Store release is implied.

`charset-normalizer==3.4.2` is explicitly pinned to its verified py3-none-any
wheel. With the floating dependency, the current resolver selected a new
3.5.2 cp314 Android wheel, then p4a's host-side pip installation rejected that
platform tag. This is a reproduced packaging failure, not a native Kivy failure.
The compatibility pin preserves the existing requests API and offline profile.
All native recipes and application code remain unchanged; six stdlib package
checks pass after the spec-only correction. Final APK verification follows.

The helper also applies android/constraints.txt to both p4a's resolver dry-run
and final installation: this p4a release drops requirement versions in its
dry-run, so the spec pin alone does not prevent the incompatible transitive
wheel. The constraints retain charset-normalizer 3.4.2 and installer pip 26.2.2.
Use the helper rather than a raw Buildozer invocation for this validated path.
All ten pure runtime dependencies are locked to the inspected versions; chardet
uses **5.2.0**'s pure-Python wheel. A complete APK inspection detected seventeen
x86 ELF extensions from floating chardet 7.7.0, even though compilation/signing
succeeded. The manual workflow now checks every ELF both in lib/ and p4a's
gzip libpybundle.so payload, rejecting anything other than AArch64.

An empty android.permissions value also produced the invalid
android.permission. declaration in the real APK. The key is now omitted; the
final manifest must have no requested permissions.

Resuming also exposed p4a's installer-venv overlay: ensurepip restored pip 25.3
over an upgraded pip 26.2.2, leaving incompatible files/metadata. The build
helper now recreates only `.buildozer/.../build/venv` before invoking p4a.
Native objects, SDKs, packaged runtime and app-private journals remain intact.
It refuses linked installer paths. Eight focused policy tests pass, including
native-cache preservation and symlink rejection; actual resume follows the
same path. This is build-tool source, not a new application/payment/data feature.

p4a also reused a completed distribution containing old dependencies after
constraints changed. The helper now reconstructs its generated dists/ output
on invocation, preserving the expensive build/other_builds native objects,
SDKs and private app state. The constraints file is included in staging hashes,
so --resume rejects changed constraints too. Nine policy checks pass, including
distribution-cache/native-object separation. Repackaging uses the newly locked
pure dependencies rather than a stale signed runtime.

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
