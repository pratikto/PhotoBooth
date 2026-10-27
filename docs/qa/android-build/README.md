# Android A1 verification — 27 October 2026

Owner scope: continue the existing Android branch to APK build readiness,
following current GUI v2, with comprehensive documentation review and no new
development branch. [Review/scope/build guide](../../android-build-readiness.md).

Runtime source: **a4ba8aab8ea79858e8a79cb3230ef2ea3591037e**, pushed and remote
verified. Desktop reference **a62721f**, app/gallery/test reuse from **eb0297d**.
The 177 APK input hashes and six correctly sized native PNGs are recorded in
[verification.json](verification.json). PNGs are Linux fixtures, not Android screenshots.

- [Full regression](full-tests.txt): **879 run / 876 PASS / 3 SKIP /
  0 failures/errors**, 330.674s. Linux, Python 3.12.14/Kivy 2.3.1, software GL,
  dummy audio/video and isolated devices/providers. Command:
  `PHOTOBOOTH_TEST_ANDROID=1 PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1 python tools/run_kiosk_unittests.py`
  with SDL offscreen/dummy, KIVY_HOME under work/, KIVY_NO_CONSOLELOG=1,
  LIBGL_ALWAYS_SOFTWARE=1 and command-network permission for local API fixtures.
- Three skips are optional native palm-model fixtures: camera recovery, v2
  palm countdown and standalone model inference. They are not passed cases.
- [Focused A1 checks](focused-tests.txt): **8 PASS**, zero skips/failures/errors,
  11.908s, including a staged app subprocess with no repository assets, original
  game artwork decoding, actual DEMO claim, Back pause, lifecycle and duplicate
  rejection after reopening the private ledger.
- [Earlier carousel checks](carousel-tests.txt): 41 cases / 39 PASS / 2 opt-in
  SKIP, no failures/errors. Those cases are included in the later full run;
  native audio ran there, while the optional palm fixture remains skipped.
- [Matching preview CI 40491067949](https://github.com/pratikto/PhotoBooth/actions/runs/40491067949)
  **SUCCESS** on a4ba8aa. This is package/widget CI, not APK compilation.

Fresh gallery/game-intro views were visually reviewed at 452×900 and 800×1280.
The test now sets/asserts actual Window/stage dimensions even if another test
already imported Kivy; filenames alone are insufficient dimension evidence.

Real APK compilation is recorded separately after completion. Initial local
host-toolchain attempt selected conda's x86 libzstd during ARM CPython configure;
the link failed. Select the system pkg-config (which honors p4a's target
PKG_CONFIG_LIBDIR), remove only the generated failed Python configure/shared-lib
build markers, then resume. A partial libpython output is not successful Python
installation: p4a can otherwise skip to a missing libpythonbin.so. No app source,
SDK CA policy or private journal is changed for this host-toolchain correction.

Later build-only corrections: pin charset-normalizer 3.4.2's independently
downloaded py3-none-any wheel after p4a rejected a newly resolved cp314 Android
wheel; recreate only its generated installer venv on resume after ensurepip
overlaid pip 25.3/26.2.2. Eight focused policy tests pass for curation, hashes,
no native-cache deletion and linked-installer rejection. The earlier 879-case
run remains tied to a4ba8aa; final helper/spec evidence is separate below.

Device installation, real Android touch/insets/keyboard/Back/Home, speaker,
camera, printer, Drive, provider/POS and release acceptance remain NOT_RUN.
Do not erase app-private data, consumed codes, counters or journals for a pass.
