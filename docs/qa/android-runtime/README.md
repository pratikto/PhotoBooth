# Android native runtime evidence

Source and reviewed contracts: [runtime runbook](../../android-v2-runtime.md).
Portable reuse published at 795b64c (desktop reference c001095).
focused.txt: 23 PASS at 452x900; portrait.txt: 12 runtime PASS at 800x1280.
Fixtures use fake camera/native USB/provider transports and real v2 widgets,
full-size JPEG storage, composition, ESC/POS payloads, grants/journals and workers.
They do not certify actual Android sensor/USB paper/media/provider behavior.
New full regression and APK build/inspection are in progress.
