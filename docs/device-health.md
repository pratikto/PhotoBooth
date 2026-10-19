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

Synthetic GUI/controller tests live in `tests/test_device_health_gui.py` and are run by Kiosk GUI regression CI (`PHOTOBOOTH_TEST_GUI=1` with a Kivy/Xvfb display). The 25 isolated Stage A tests run without physical hardware.

### Separate merge authorization

The Stage B PR is **review-only** until the owner approves merging its precise tested SHA to `master`. Do not infer merge permission from test PASS. The prior Stage A branch and this branch are the same `feature/device-health`, so a later approved merge would introduce both Stage A and B together.

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
