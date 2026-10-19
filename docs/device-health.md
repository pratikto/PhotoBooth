# FEAT-008 — Device Health Monitoring (Stage A backend)

**State (2026-10-19):** Owner-approved **Stage A only** is implemented on `feature/device-health` in [PR #5](https://github.com/pratikto/PhotoBooth/pull/5) as reviewable source and mock tests. **Check the PR for its exact CI and merge state**; the immutable [v1.0.0](releases/v1.0.0.md) tag is unchanged. Stage B (Settings GUI), Stage C (physical Windows acceptance), alarms, auto-recovery and remote monitoring are **not implemented or authorized by this stage**.

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

**No import/startup side effects**: no timers, background watchers, automatic retries, camera restart, print commands, file writes, web uploads or Google Apps Script calls. `collect_health_snapshot` is **only an opt-in synchronous probe**. It can spend time on network/spooler/disk I/O, so Stage B must run it in an explicit worker rather than the Kivy render thread, safely marshal UI updates back to Kivy and avoid scanning while printing if the Windows driver is sensitive. This feature does not gate customer sessions or override the operator's print/camera choices.

The module takes existing `Camera`, `PrinterConfig`, the photos directory and loaded `AdCatalog`; it does **not** import the Kivy UI/controller. Future integration should reuse those existing objects and must not instantiate a second camera or printer. Printer and network dialers are injectable for isolated tests.

## Verification, rollback and next steps

Run targeted tests locally:

```powershell
python -m unittest discover -s tests -p test_device_health.py -v
python -m compileall -q photobooth tests
```

After a PR is opened, record actual GitHub Actions run ID and tested commit SHA in [test_checklist.md](test_checklist.md). Linux/mock tests are **not** camera, Windows queue, ESC/POS paper or codec hardware acceptance.

**Rollback:** revert FEAT-008 Stage A commits/PR if necessary; no existing `main.py` path imports this module, so legacy kiosk behavior is unchanged. **Next approval boundary:** Stage B operator UI and Stage C device tests remain separate follow-ups; do not begin without new owner approval.
