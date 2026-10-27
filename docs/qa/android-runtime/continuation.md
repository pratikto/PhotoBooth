# Android runtime verification continuation

Date: 28 October 2026 (Asia/Jakarta). Base: `ef08696` on
`feature/portrait-kiosk-android`. This record distinguishes the fresh cloud
checks from historical A1 preview-APK evidence.

## Delivered source

Added a stdlib APK metadata/native-payload verifier and rejection fixtures.
The existing Android workflows run these portable checks and enforce runtime
package/version/API/permissions/ABI after a native build. APK signature and
16 KB ZIP alignment use the pinned Android build tools separately. There are
no changes to the shared UI, camera, USB sender, payment services or journals.
[Contract and commands](../../android-v2-runtime.md#runtime-apk-verification-continuation--28-october-2026).

## Validation record

Initial existing Android group: **23 PASS**, zero failures/errors/skips,
7.280s, with `PHOTOBOOTH_TEST_ANDROID=1`, Kivy offscreen/software GL/dummy audio.
Second required viewport (`ANDROID_PREVIEW_WIDTH=800`): **14 PASS**, zero
failures/errors/skips. These run actual shared widgets with synthetic devices;
they do not certify an Android sensor, printer or merchant.

Portable package/verifier group and the final complete regression are recorded
below once completed. Optional external palm-model cases remain separate from
the manual shutter and Android Java inference acceptance.

## Native build and access

Pinned Buildozer/Cython/setuptools were installed into a separate ignored build
venv. A real `tools/build_android.py` invocation staged the current curated app,
then stopped at **Java compiler (javac) not found** in this fresh cloud machine.
JDK/SDK provisioning continues through official download hosts with checksum
verification; no TLS or artifact checks are disabled.

A read-only GitHub workflow API request returned **Forbidden**. No remote APK
workflow was dispatched, and no matching-source CI/build PASS is claimed from
that request. Git HTTPS fetch succeeded independently; API and Git access have
different scopes.

Actual Android install/camera rotation/resolution/permission loss, USB paper and
cutter/uncertain-job recovery, speakers/video, real Sandbox simulator and
Drive/download/deletion remain **NOT_RUN** in this cloud session. Use the current
runtime guide for device setup. Never uninstall/clear private state or reset
claims to pass an acceptance check.

## Current native build blocker and required settings

Official Temurin JDK 17.0.16+8 was SHA-256 verified and installed under
`/workspace/android-toolchain`. Official Android CLI revision 13114758 was
verified against Google's repository checksum. SDK platform 35, build-tools
35.0.0 and NDK 28.2.13676358 are now installed. The Java CameraBridge compiles
against API 35 (deprecation notes only). The first p4a retry exposed the SDK
layout mismatch described in the corrected A1 guide; standard
`cmdline-tools/latest` resolves it.

The next real build reaches recipe downloads, then fails fetching FreeType
2.14.1 at `download.savannah.gnu.org` with proxy CONNECT **403 Forbidden**.
This is a network-policy blocker, not a compiler diagnostic. No runtime 0.2.0
APK was produced. The pinned OpenSSL recipe also declares `www.openssl.org`.
A configuration draft now preserves existing presets and adds those two source
hosts plus `api.github.com` for the documented remote workflow route. Draft
persistence is confirmed; runtime access is not yet changed. Review/save the
network settings and publish the environment, then retry the staged build.
Further recipe redirects may require their own observed domain additions.

All TLS/checksum verification remains enabled. GitHub source fetches worked;
the workflow API request was Forbidden and no remote build was dispatched.
The prepared SDK/NDK/native caches remain in the workspace for resumption.
