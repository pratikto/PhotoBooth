# FEAT-008 — Device Health Monitoring (Stage A backend + Stage B operator GUI)

**Current branch (2026-10-19):** FEAT-008 **Stage A backend** and explicitly approved **Stage B operator Settings GUI** are under development in `feature/device-health`. The earlier [Stage A PR #5](https://github.com/pratikto/PhotoBooth/pull/5) was merged without separate approval and **reverted from `master` by owner request in [PR #6](https://github.com/pratikto/PhotoBooth/pull/6)**. Both stages remain on the feature branch only; do **not** merge without separate owner approval. The immutable [v1.0.0](releases/v1.0.0.md) tag is unchanged. Stage C (physical Windows acceptance), alarms, crash recovery and remote monitoring remain out of scope.


## Stage B — Kivy Settings panel (branch-only)

**Operator path:** On the `feature/device-health` branch, launch the normal Kivy booth, tap the **gear (Settings)** in the header, then choose **DEVICE HEALTH**. The panel runs **one nonblocking diagnostic sweep on opening**; **REFRESH STATUS** starts another sweep only when the previous result finished. **TUTUP** closes the popup. It does not navigate away from or reset the ongoing photo session.

Six rows show camera, printer, disk, network, media, and the existing application's Kivy heartbeat. Statuses are `READY`, `PERHATIAN`, `TIDAK TERSEDIA`, and `BELUM DIKETAHUI`. The last probe timestamp uses the Windows local clock. **The app never automatically prints, reopens the camera, deletes photos, restarts services, or blocks a customer solely because of a health status.** The existing face/palm shutter guard also inhibits gesture actions while this operator modal is open.

The controller `PhotoBoothApp._refresh_device_health` captures the active camera, printer configuration, photos directory, ad catalog, and current Kivy heartbeat **on the main thread**, then executes the existing `collect_health_snapshot` in a **daemon worker**; only UI-result delivery runs on the main Kivy clock. A lock prevents duplicate overlapping scans. The Kivy panel ignores results received after dismissal or reopening. The UI heartbeat reuses the already scheduled `_kiosk_tick` (no new monitor timer). Printer route checks are **skipped** while an in-flight photo print is registered, returning `unknown` rather than interfering with print spool submission.

**Stage B limitations:** printer queue/TCP readiness does not certify physical paper/cutter; network TCP is not a Drive or payment check; file presence does not certify video decoding; no hardware camera is opened for probing. Default disk warning is below **10% free or 1 GiB free**, not 15%. A heartbeat `ready` confirms only that the existing Kivy tick was recent when the operator requested a sample. Cloud 30-day retention BUG-009 remains OPEN.

### Windows smoke test (no automatic physical print)

```powershell
git fetch origin
git switch feature/device-health
git pull origin feature/device-health
python -m unittest discover -s tests -p test_device_health.py -v
python main.py
```

With the Kivy app open: Settings gear → DEVICE HEALTH → read all six rows → REFRESH STATUS → TUTUP. Check that closing/reopening the panel never displays stale results, and that camera preview/photo workflow and existing printer controls still work. **Do not start a real print test just to validate this read-only feature.** Windows hardware acceptance is Stage C and requires separate approval/evidence.

Synthetic GUI/controller tests live in `tests/test_device_health_gui.py` and are run by Kiosk GUI regression CI (`PHOTOBOOTH_TEST_GUI=1` with a Kivy/Xvfb display). The 25 isolated Stage A tests run without physical hardware. **Reviewed Stage B code SHA `f93dd88`:** [Device Health tests 25 PASS](https://github.com/pratikto/PhotoBooth/actions/runs/39197763719) and [full Kiosk GUI synthetic regression](https://github.com/pratikto/PhotoBooth/actions/runs/39197763624) **270 run (268 PASS, 2 SKIP), 87 synthetic renders / 0 errors**. This evidence is not a Windows physical device signoff; later documentation-only PR head checks must be assessed separately.

### Separate merge authorization

The Stage B PR is **review-only** until the owner approves merging its precise tested SHA to `master`. Do not infer merge permission from test PASS. The prior Stage A branch and this branch are the same `feature/device-health`, so a later approved merge would introduce both Stage A and B together.


## Cross-platform capability work — phased continuation (2026-10-19)

The owner approved staged implementation for heterogeneous cameras, printers,
Windows mini PCs, Linux/SBCs and Android **on the existing feature branch**.
This does **not** approve merging Draft PR #7 or changing the v1 source release.

### B.1 — Capability inventory (implemented, code verification in CI)

`photobooth/hardware_adapters.py` defines immutable `DeviceDescriptor`
with `kind`, `device_id`, `name`, `transport`, `platform`,
`identity_quality`, `presence`, `capabilities` and a limitations `note`.
`platform_family` separates Windows, Linux, Android and unsupported runtimes;
the adapter **describes** selected camera / printer routes without opening
devices or switching hardware. A configured printer IP, a Windows queue name,
a Linux USB path or a camera index are **not stable serial-number identities**.
Manufacturer/product USB IDs alone do not uniquely identify one printer.

`collect_health_snapshot` includes `platform` and `devices` while
retaining the existing six health status rows. Desktop checks only run on
desktop backends; Android camera/printer report **UNKNOWN** until genuinely
supported native bridges exist (no simulated Camera2 success).

The existing `Camera` and `ThermalPrinter` still own **actual photo and
printing operations**. This is a capability and identity foundation, **not yet
a fully interchangeable runtime camera/printer HAL**. Do not declare Windows
device codes ready for Android merely because the inventory class exists.

### B.2 — Read-only device discovery (implemented; selection deferred)

`photobooth/hardware_discovery.py` enumerates only possible OS candidates:

| Platform | Non-invasive sources | Important limitation |
| --- | --- | --- |
| Windows | `win32print.EnumPrinters` local/connected print queues | Queue enumeration does **not** verify printer physically present, driver readiness, paper or cutter. Windows camera scanning intentionally does **not** brute-force `VideoCapture(index)`. |
| Linux mini PC / SBC | `/dev/v4l/by-id/` aliases and `/dev/video*`; `/dev/usb/lp*`; `lpstat -e` queue names with 1.5-second command timeout | Paths/queues do not prove permissions, frames, ESC/POS support or paper. CSI/libcamera modules may require a separate adapter; `video*` indices may change after USB reconnect. |
| Android | No desktop bus enumeration | A platform-native Camera2/USB Host bridge, permissions and real device trials are prerequisites. Empty discovery is **unknown**, not proof of no camera/printer. |

Discovery runs only as part of the explicit operator Settings health scan,
off the Kivy thread. The panel displays **configured** route entries and
**OS-detected candidate** entries separately in the scrollable list. It does
not auto-select a different printer or camera, alter the existing printer
configuration or write a selection file. Zero discovered devices may mean
the OS enumeration API is unavailable rather than no devices existing.

A reliable **B.2 selection follow-up** requires validating unique device
identity, appropriate permissions and reconnect behavior on Windows/SBC.
The current printer Settings already saves an operator-selected LAN/Wi-Fi/
Windows queue route; Windows camera index remains configured using
`PHOTOBOOTH_CAMERA_INDEX`. Do **not** replace camera `index=0` automatically
with another camera if an extra USB webcam is connected. Proposed selection
changes should be explicit, persisted safely and normally take effect only
after a controlled restart.

### B.3 / B.4 — Pending implementation and acceptance boundary

- **B.3:** Extend runtime printer and camera adapters after verifying actual
  Windows printer-driver status APIs, Linux V4L2/CUPS/libcamera support and
  specific transport capabilities. No universal paper or cutter indicator
  without an actual supported sensor/protocol.
- **B.4:** Android native Camera2 / USB Host / vendor printer SDK bridge,
  packaging, runtime permissions, activity lifecycle and real Android hardware
  tests. Desktop OpenCV/pywin32 code is not an Android driver.
- **Stage C:** owner-run physical acceptance matrix by OS, actual printer
  model/transport, camera model, USB disconnect/reconnect, restart, paper-out,
  camera permission denial, low disk, no network, and working checkout. All
  unsupported sensors must remain `UNKNOWN` / `NOT SUPPORTED`.

### Verification commands

Run from the repository root after checking out `feature/device-health`:

```powershell
python -m unittest discover -s tests -p test_device_health.py -v
python -m unittest discover -s tests -p test_hardware_adapters.py -v
python -m unittest discover -s tests -p test_hardware_discovery.py -v
python main.py
```

In Meong's Settings > DEVICE HEALTH, confirm a platform label, six diagnostic
rows and a **DAFTAR PERANGKAT / ADAPTER** section listing configured and
detected candidates. Try Refresh, close/reopen and compare with Windows
printer Settings. Device discovery makes **no print job** and does **not**
open new camera handles. Preserve test logs without customer photos or cloud
tokens. The Draft PR and automated Linux tests do not replace Windows/SBC/
Android hardware testing. **No merge to master without explicit owner approval.**

## Scope and interface

`photobooth/device_health.py` provides a read-only `HealthCheck(name, status, message)`, immutable `HealthSnapshot(checked_at, checks)`, individual `check_*` probes and `collect_health_snapshot(...)`. Status vocabulary: `ready` (only the stated check passed), `warning` (degraded or reachability not confirmed), `unavailable` (e.g. camera closed), and `unknown` (not supplied or not safely inspectable). Do **not** map `ready` to "booth fully operational" or "paper present".

Checks cover:
- **Camera:** Inspect the *existing* controller capture handle and nonblocking `Camera.read()` latest-frame mailbox. Never open a competing camera or force a new frame.
- **Printer:** Check configured LAN then Wi-Fi TCP port, Windows spooler visibility, or Linux USB device-path presence; send **zero ESC/POS bytes** and never execute a test print. A TCP/spooler/USB presence result **cannot confirm** paper, cutter, physical connection or job completion. USB VID/PID without a safe presence proof returns `unknown`.
- **Disk:** `shutil.disk_usage` on the closest existing parent of the photo directory. Default warning thresholds are <10% free **or** <1 GiB free. Read-only; no photo creation/deletion.
- **Network:** One bounded TCP handshake to the fixed endpoint `1.1.1.1:443` (0.75s connect timeout), with no payload, login or credential exposure. Failed probe warns of *possible* connectivity trouble, **not** proof that all internet/Drive services are offline. OS resource resolution may still introduce delays.
- **Media:** Inspect the existing `AdCatalog` playlist path and referenced local file presence/nonzero lengths, including poster files; do not decode videos, check codecs, fetch ads or change playlists.
- **Heartbeat:** Compare an optionally provided monotonic UI timestamp to a five-second age limit; it remains `unknown` until future UI integration supplies actual ticks.

## Safety and integration boundary

**Stage A has no import/startup side effects**: no timers, background watchers, automatic retries, camera restart, print commands, file writes, web uploads or Google Apps Script calls. `collect_health_snapshot` is **only an opt-in synchronous probe**. It can spend time on network/spooler/disk I/O, so Stage B must run it in an explicit worker rather than the Kivy render thread, safely marshal UI updates back to Kivy and avoid scanning while printing if the Windows driver is sensitive. This feature does not gate customer sessions or override the operator's print/camera choices.

The module takes existing `Camera`, `PrinterConfig`, the photos directory and loaded `AdCatalog`; it does **not** import the Kivy UI/controller. Future integration should reuse those existing objects and must not instantiate a second camera or printer. Printer and network dialers are injectable for isolated tests.

## Verification, rollback and next steps

Run targeted tests locally:

```powershell
python -m unittest discover -s tests -p test_device_health.py -v
python -m compileall -q photobooth tests
```

Standalone mocked regression: [FEAT-008 GitHub Actions 39192498537](https://github.com/pratikto/PhotoBooth/actions/runs/39192498537) **24/24 PASS** at source/test SHA `3ae31dfc933352c293eed682c72f4f8afb6020c` on Ubuntu Python 3.12. [test_checklist.md](test_checklist.md) tracks the PR's full Kiosk CI and any later head SHA separately. Linux/mock tests are **not** camera, Windows queue, ESC/POS paper or codec hardware acceptance.

**Rollback:** discard or revert this unmerged branch's Stage B commits; `master` already has the original Stage A unauthorized merge safely reverted. **Next approval boundary:** Stage C physical device signoff and any future merge/release remain subject to separate explicit owner permission.
