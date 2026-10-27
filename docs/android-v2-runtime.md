# Android v2 runtime — camera, printing and Sandbox

## Runtime APK verification continuation — 28 October 2026

Continued from `ef08696` on the existing Android branch. Reviewed AGENTS, the
root/documentation index, Android development/build/runtime guides, protocol,
architecture/engineering contracts, decisions, status/bug/backlog/test ledgers
and handover before changes. Inspected the current camera/USB/settings adapters,
curated staging/build helpers and both Android workflows. The completed native
runtime is reused; this increment changes build verification, not photo/payment
authority, device behavior or the desktop launcher.

The APK workflow previously printed `aapt` metadata without asserting runtime
identity/permissions. A successfully signed stale 0.1.0 preview could therefore
pass that step. `tools/verify_android_apk.py` now compares the actual APK badging
with the **staged** spec: package/version, minimum/target API, exact permission
set and arm64-only ABI. It reuses the existing nested Python-payload ELF check,
also rejects truncated/non-ELF/foreign-ABI libraries, and requires a Python
bundle with native extensions. It reads archive members without extracting them.

The workflow keeps `apksigner` verification, adds `zipalign -c -P 16`, and uploads
the binary SHA/size/metadata JSON and alignment log with the APK. The verifier
cannot overwrite its input files and removes an old success report before a
failed rerun. Signature and alignment remain separate tool checks; the JSON
does not claim those or physical-device acceptance.

Run portable policy and negative binary fixtures without Android tools:

```bash
python -S -m unittest tests.test_android_preview tests.test_android_apk -v
```

After a real build, use the build-tools version already pinned by A1:

```bash
"$ANDROID_HOME/build-tools/35.0.0/apksigner" verify --verbose "$APK"
"$ANDROID_HOME/build-tools/35.0.0/aapt" dump badging "$APK" > work/apk-manifest.txt
python tools/verify_android_apk.py "$APK" --badging work/apk-manifest.txt \
  --spec work/android-project/buildozer.spec --output work/apk-verification.json
"$ANDROID_HOME/build-tools/35.0.0/zipalign" -c -P 16 -v 4 "$APK"
```

Fixture APKs are deliberately synthetic ZIP/ELF inputs; their successful checks
are not a newly compiled/signed Android artifact. Fresh runtime build and
regression results are tracked in `docs/qa/android-runtime/continuation.md`.
Use the [Android-specific device acceptance checklist](qa/android-runtime/device-acceptance.md)
to record actual installation, camera/USB, lifecycle, media, Sandbox and Drive
results once a fresh runtime APK is available.
Rollback only this verification/workflow increment; preserve app-private state,
photos, claims and uncertain print/payment journals.

Owner continuation, 28 October 2026 (Asia/Jakarta): include QRIS Sandbox,
camera and printing and follow the features currently in GUI v2. Continue on
`feature/portrait-kiosk-android`; no new branch or desktop/master changes.
Base/rollback: f9e1239. Refreshed desktop reference: c001095.

## Review and implementation plan

Reviewed AGENTS, root/index, protocol, decisions, handover, architecture,
feature/bug/backlog/test ledgers, Android A0/A1, v2 product/technical/visual
contracts, branch audit, P3/P5/Sandbox, current printer/Drive/mirroring/storage
contracts and the newer customer FIFO/early-folder-QR and Sandbox-key fixes.
All contents of old remain excluded. Pre-restart local documentation/evidence
is preserved in a named Git stash; recovered A1 final report is 882 run,
879 PASS / 3 optional model skips / zero errors or failures, 266.232s.

Reuse the actual current desktop Python services, UI, original game, all twelve
templates, capture/review/retake/compositor, durable print and payment workers.
Portable delivery changes are taken as exact files from c001095, without a
branch merge. Android-specific camera, permission, lifecycle and configuration
adapters must not instantiate desktop camera drivers. Native camera output must
retain capture resolution and unmirrored originals; only existing display and
compositor paths mirror. Permission denial, pause and disconnect invalidate input
and cancel countdown. Resume never automatically captures or prints.

Printing uses the original ESC/POS renderer and one durable batch per design,
with SENDING before I/O and UNCERTAIN/no replay on ambiguous sends. Network
printing reuses TCP; Android USB requires UsbManager permission/transport rather
than Windows RAW drivers. Owner selected USB OTG and the built-in camera.
No actual paper, merchant transaction or cloud deployment is performed in QA.

Sandbox reuses QrisKioskClient/KioskCheckout/SandboxViews over an authenticated
HTTPS backend. Merchant keys stay on the backend, never in the APK. App-private
configuration contains only booth credentials. Persist journals before requests;
STARTED ACK precedes countdown. Existing desktop merchant-trial delivery-off
isolation stays; Android's explicitly configured printer can test the combined
Sandbox/photo/print path under this new owner authorization.

Run focused native-adapter and real reused-UI tests, one final regression and
an actual new arm64 build. Record APK signature/manifest/ELF verification and
truthful device/provider limits. Original A1 artifact evidence remains historical.
Do not call feature parity verified without accounting for face/palm, video,
Drive setup, device transport and actual Android hardware acceptance.

## Progress

Portable synchronization: 106 targeted cases initially had one diagnostic
failure because the matching desktop launcher logging hook was missing. The
exact current launcher was then reused too; all ten diagnostic cases pass on
rerun. Remaining 105 initial cases passed. Raw reports are retained in
qa/android-runtime. Camera choice is built-in; printer choice is USB OTG.

Implementation in progress. No new camera/printing APK or Android hardware PASS
is claimed yet. Rollback uses scoped inverse commits and preserves all private
state, photos, counters, consumed attempts and uncertain payment/print jobs.

## Android setup and feature mapping

The packaged entry now selects android_runtime, while create_preview remains an
explicit offline test helper. The package ID stays id.meong.meongpreview and
private root stays files/meong-preview, preserving existing consumed game codes.
Debug version is 0.2.0. CAMERA and INTERNET are the intended manifest permissions;
USB device access is a separate Android UsbManager consent dialog.

| Existing v2 feature | Android implementation | Verification limit |
| --- | --- | --- |
| Ads, tutorial, twelve designs, carousel, original game and DEMO ledger | Actual shared app/renderer/assets; private videos in ad_video | Native layout fixtures; device touch/media pending |
| Camera, three photos, countdown, review and one retake/design | Camera2 preview + separate maximum-supported-resolution JPEG capture, original PhotoJobs/PhotoTest/compositor | Camera2 Java compiles; actual sensor/orientation/permission acceptance pending |
| Mirror | Existing display/review/compositor mirrors only photo pixels; raw saved JPEG stays unmirrored at capture resolution | Existing renderer regression plus actual saved dimensions in mobile fixtures |
| Auto-print/copies/uncertainty | Existing ThermalPrinter/ESC-POS raster and SENDING journal; injected UsbManager bulk OUT sender | Partial-write/no-replay fixtures; physical paper/cutter/QR acceptance pending |
| Face invitation | Original bundled OpenCV detector + FaceInviter/hold/cooldown | Native OpenCV recipe included; real Android face detection pending |
| Optional palm shutter | Same pinned model, PalmGestureWorker/PalmHoldTrigger; Android MediaPipe Java inference | Native dependency/model binding; real device inference pending; manual button retained |
| Audio/video | Same v2 owner/WAVs and Kivy ffpyplayer provider | New native build required; actual speaker/video pending |
| Drive/offline/FIFO/early folder QR | Exact c001095 portable services; app-private local workspace and existing Apps Script client | Source fixtures; deployment/phone/cloud-retention acceptance pending |
| QRIS Sandbox | Same backend/client/journal/UI/grant/ACK protocol; booth-only HTTPS credentials | Offline HTTP-to-GUI/photo/print fixtures; real merchant simulator pending |
| Device Health/report | Original v2 six-row panel/report; read-only Android camera/USB observations | No second camera, print bytes or provider calls during observation |

After installing with adb install -r (same debug signing key), grant camera
permission. Hold the logo for 1.5 seconds at idle to open PENGATURAN ANDROID.
Choose camera 0/front or 1/back. Enable USB OTG auto-print only after confirming
printer VID/PID; defaults 4838:3830 match the documented Caysn/iWare printer.
Select 576 or 384 dots and the existing dithering mode. Save, close and reopen;
use IZINKAN USB PRINTER and grant the selected device's Android dialog. A denied
permission or unplugged printer cannot yield a successful print state.
STATUS PERANGKAT opens the reused read-only panel, including local safe reports.
No print test is sent just by opening settings/status.

Camera uses one Camera2 session for YUV preview and full-resolution JPEG stills.
JPEG orientation is normalized before the existing unmirrored raw save; the
small RGB display texture is never substituted for the original capture.
Pause, Back and permission loss cancel countdown; background time cannot capture.
Reopening waits for native closure before another handle can open. Interrupted
service/uncertain sends remain held; never uninstall/clear data to bypass them.

Optional video media belongs in files/meong-preview/ad_video. A private
ad-playlist.json can use the existing explicit playlist format. Local videos,
private configuration, customer photos and credentials never enter staging/APKs.
Audio, face and optional palm can be toggled in the Android settings. Palm's
original 8,373,440-byte SHA-pinned public model downloads on its worker on first
use, then works offline; missing model/inference keeps SIAP available.

## Sandbox backend

The Android device cannot use a PC's 127.0.0.1 address. Use an authenticated HTTPS
backend reachable from it, with a certificate trusted by requests/certifi. Never
turn off TLS verification or put a Midtrans Server Key in the app. The ordinary
Windows/Ubuntu merchant-trial launcher stays loopback and printer/Drive-off.

A new helper reuses trial_environments and the unchanged qris_server factory:

```bash
python -m pip install -r requirements-qris.txt
python tools/run_android_sandbox_backend.py --public-url https://sandbox.example.com --port 8765
```

The default loopback listener requires your existing HTTPS ingress forwarding to
it. For direct LAN TLS use --host 0.0.0.0 --tls-cert /path/certificate.pem
--tls-key /path/private-key.pem with the matching HTTPS hostname/certificate.
This command is a local operator setup instruction, not a deployed server here.
Enter Merchant ID and hidden Sandbox Server Key locally; both dashboard key
formats are accepted. The helper preserves a stable booth token/database on
restart and writes a private mobile-settings.json under ignored
 data/android-sandbox-backend/<merchant>/<booth>/ (file mode 600).
Only booth URL/ID/token go into Android settings; never share that file in chat
or commit it. Set QRIS Sandbox, save and restart. Existing payment profile
identity cannot be changed while an order needs reconciliation.

Gallery then uses the same explicit full-price/no-game-promo Sandbox consent,
QR, authoritative status/one-use permit, photo consent, STARTING/STARTED ACK,
capture/review/auto-print and COMPLETED ACK. SALIN URL QR UNTUK SIMULATOR copies
only a verified allowlisted Sandbox image URL; use the official simulator:
https://simulator.sandbox.midtrans.com/v2/qris/index . Never a real banking app.
Copying a URL or pressing a button cannot authorize payment. Unknown/recovery
cannot return to browsing or create another charge. Android print is explicitly
opted in for this owner-requested combined test; Drive stays off in Sandbox,
matching the existing dedicated v2 trial. Ordinary local mode can opt into the
existing Drive deployment URL/token, retention guard and background queue.

## Build compatibility and observed checks

The pinned p4a toolchain remains unchanged. Added native OpenCV and ffpyplayer
recipes, python-escpos/PyYAML pure dependencies and MediaPipe tasks-vision 0.10.32.
The local FFmpeg recipe pins official 6.1.6 LTS source f1e3a2b and archive SHA;
ffpyplayer is 4.5.3 as in current desktop v2. This is a reproduced compatibility
exception: p4a's FFmpeg 8 removed avfft/channel APIs required by its old player.
Software decoding is forced to avoid the old Android-15 MediaCodec binder path;
the inherited compiler/build method remains. Cross OpenSSL include/link paths
are retained as in p4a. The mirror also avoids ffmpeg.org's observed HTTP 503.
All custom recipes, patches and Java sources enter the curated hash manifest.

Focused runtime checkpoint checks: 23 PASS at 452x900 (15.223s), and 12 runtime PASS
at 800x1280 (11.118s), zero failures/errors/skips. Real saved fixture JPEGs are
1600x1200 while preview input is 32x24; one retake gives four native capture
calls; two identical copies are encoded into one send. Lost STARTED ACK cannot
capture; retry binds the same transaction; partial USB send becomes UNCERTAIN
and cannot replay. Settings/status, masked tokens, stable backend token,
protected payment identity and denied USB permission also pass.
Full regression and new APK verification remain in progress at this checkpoint.

Native close-quarantine follow-up: CameraBridge compiles against API 35; an
additional adapter check confirms a second native handle cannot open until the
previous bridge reports closure. MediaPipe is pinned to current 0.10.32 for the
new Android native build. Physical sensor/gesture/paper acceptance is NOT_RUN.

When enabling ordinary-mode Drive on a second device, choose its own configured
booth ID; do not reuse an active desktop booth counter/profile or edit claim
journals. Existing server ownership/conflict guards remain authoritative.
