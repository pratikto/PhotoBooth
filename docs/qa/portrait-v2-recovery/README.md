# FEAT-009 stage 2 — recovery review and Ubuntu startup

**27 October 2026, Asia/Jakarta.** Owner requests the next roadmap stage,
clarifies **Windows development / Ubuntu mini-PC deployment**, and makes
comprehensive documentation review before code plus documentation updates after
code the primary rule. Persisted in [AGENTS.md](../../../AGENTS.md) and the
[protocol](../../DEVELOPMENT_PROTOCOL.md).

Stage 1 was committed locally, then rebased to **ae5c62a** after refreshing the
same remote branch at **a7815d97660f9ec30cd65c891b2a4789d45b6fcb**. The refresh
retains the latest numbered-Drive/verified-link repair `0bd69a9`; no other branch
was merged and no master/default/release/deployment operation was performed.
Stage 2 stays on `feature/portrait-kiosk-v2-next`.

## Documentation and compatibility review

Reviewed the current index, root launch guidance, AGENTS, development protocol,
continuation prompt/handover, architecture, decisions, feature status, bug
register, backlog, test ledger, v2 roadmap/engineering/visual specifications,
reference-branch audit and primary-branch transition plan. Followed the affected
[storage contract](../../photobooth-storage-layout.md),
[Drive repair](../drive-photo-layout/README.md),
[print/Drive](../portrait-v2-print-drive/README.md),
[Sandbox](../portrait-v2-sandbox/README.md), [P5](../portrait-v2-p5/README.md),
[retention](../../photo-retention.md), [printer](../../printer-setup.md),
[combined acceptance](../portrait-v2-pending-acceptance/README.md) and
[stage-1 watchdog](../portrait-v2-watchdog/README.md) records.

The review distinguishes later owner instructions from earlier watchdog deferrals,
the current **cloud** Photo/00000001 layout from unchanged private local journals,
and code verification from actual device/provider/cloud acceptance. Old reports
and forms remain dated. No contents of `old` are inspected or changed.

Existing KioskCheckout, PhotoTest, print, storage, MOCK and upload logic are
reused unchanged. The new read-only adapter reads their actual persisted states;
it does not reconstruct fulfillment or introduce a second payment authority.
The existing payment lease imports catalogue/Pillow; the new pre-GUI launch lease
uses the same OS lock primitives without that dependency. Path protection follows
BoothWorkspace's archive/symlink/junction boundary on a stdlib-only path.

## Delivered behavior

- `recovery.py` inventories known local ordinary/layout-2/Sandbox photo manifests,
  saved Sandbox visits and the MOCK ledger. Reads are bounded; reports contain
  categories/counts, not customer IDs, photos, URLs, keys or raw errors.
- Pending/unknown/reserved/started/recovery Sandbox visits, pending/unknown/
  confirmed MOCK orders, interrupted photos and unacknowledged uncertain print
  jobs hold startup. Malformed/unreadable/linked state also holds. SENDING stays
  held even if someone previously acknowledged it. Completed photos with deferred
  Drive upload and empty reserves do not require fulfillment replay.
- The watchdog sets a recovery gate on its child. That child takes the launch
  lease, reviews local state **before Kivy/device/service imports**, and exits 3
  with RECOVERY_HOLD if review is required. Exit 2 is STARTUP_BLOCKED for duplicate
  ownership/unavailable lock. No automatic restart or process kill is added.
- All ordinary v2 launcher processes, including the GUI child of the dedicated
  Sandbox launcher, hold one per-checkout kernel lease through worker teardown.
  Closing/crashing releases the lock; no PID-file deletion or PID-based killing.
- Windows cmd generation remains available. The new systemd **user** service is
  for Ubuntu graphical sessions, has `Restart=no`, and disables forced SIGKILL.
  Generation never installs/enables/starts a service or embeds credentials.

The ordinary direct launcher retains its existing operator recovery behavior;
the extra journal gate applies to the watchdog route. A clear review is advisory,
not a provider reconciliation, print confirmation or automatic restart permit.
The lease is per checkout; other checkouts/v1/independent programs are outside it.
The dedicated Sandbox backend is still launched only by its own wrapper.

## Commands for Windows development

```powershell
python tools/run_portrait_v2_watchdog.py --check-recovery
python tools/run_portrait_v2_watchdog.py
```

Recovery inspection returns 0 for CLEAR_FOR_MANUAL_START, 3 for OPERATOR_REVIEW;
it does not create files or launch devices. Active-launch ownership is separately
enforced by the actual launcher. Treat a report from an active instance as an
observation, never authorization to start another process.

Generate an Ubuntu unit **from Windows** using explicit paths on the mini PC
(these `/opt/meong` paths are examples, replace both with the real installation):

```powershell
python tools/run_portrait_v2_watchdog.py --write-startup .\meong-photobooth.service --startup-format systemd --target-root /opt/meong/PhotoBooth --target-python /opt/meong/PhotoBooth/.venv/bin/python
```

Add `--print --drive` only after the mini PC's own printer/Drive configuration
and physical delivery checks are ready. A Windows spool queue is not an Ubuntu
printer configuration; use the existing [network/USB guide](../../printer-setup.md).
Keys remain in the existing private local configuration, not in the service.
The same command on Ubuntu can default to its local checkout/active Python.
Windows cmd generation remains `--startup-format windows` on Windows itself.

## Ubuntu mini-PC setup and manual installation

Use Ubuntu **with a graphical desktop/session** for this Kivy application. Exact
Ubuntu release, mini-PC hardware, X11/Wayland and touch/camera/printer/audio remain
unverified. A headless server session is not a graphical acceptance environment.

Create the mini PC's own Linux venv (do not copy `.venv-kivy` from Windows):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/run_portrait_v2.py
python tools/run_portrait_v2_watchdog.py --check-recovery
```

Install OS packages for venv, desktop/OpenGL/video/audio and camera/USB access as
needed for the actual Ubuntu version. Reuse the original application transports;
do not replace drivers or run the kiosk as root merely to bypass permissions.
Run the GUI manually in the signed-in kiosk account first.

After reviewing/copying the generated unit and finishing active jobs, the operator
can install it manually on that Ubuntu account:

```bash
mkdir -p ~/.config/systemd/user
cp meong-photobooth.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user import-environment DISPLAY WAYLAND_DISPLAY XAUTHORITY XDG_RUNTIME_DIR
systemctl --user enable --now meong-photobooth.service
systemctl --user status meong-photobooth.service
journalctl --user -u meong-photobooth.service
```

It starts with `graphical-session.target` where supported by the desktop. This
does not configure auto-login, a system daemon, root execution or a headless boot
session. Import display variables from the actual desktop session; do not invent
DISPLAY=:0 or copy Windows environment paths. Services do not inherit arbitrary
PowerShell/shell exports; reuse private saved settings or separately configured
operator environment. Never copy full environment dumps or secrets into reports.

Finish customer work and close the GUI before planned logout/shutdown/service
stop. SIGINT requests normal shutdown; the generated unit does not force SIGKILL
after its stop timeout. OS power loss/forced account teardown is still an uncertain
interruption requiring existing journal review, not certified safe recovery.

## Handling a hold and rollback

Run `--check-recovery` and inspect its redacted categories. Before any manual
restart, confirm the old process has actually exited. For Sandbox, use its
existing isolated launcher/operator RECOVERY and reconcile backend order/grant/
service state against the local manifest; never delete a journal or manufacture
completion. Inspect actual paper before resolving an uncertain send. Do not edit
counters, clear consumed game attempts, recapture/reprint or reset databases to
make this gate pass. Interrupted local tests also need operator disposition;
this stage supplies no destructive reset/automatic repair command.

Rollback: disable/remove only a manually installed startup service/shortcut after
jobs stop; use scoped inverse source commits if necessary. Preserve all existing
photo/payment/claim/print/upload state. `Restart=no` remains intentional; bounded
automatic restart with a durable safe-idle admission contract is a future stage.

## Verification

Results and exact source hashes are recorded in the companion reports. Linux
cloud/software GL/dummy audio and synthetic providers do not certify Ubuntu
mini-PC hardware, Windows hardware or a merchant/Google account.

- [Final full suite](full-tests.txt): **869 run / 866 PASS / 3 SKIP /
  0 failures/errors**, 261.246s. Skips: camera-recovery native palm inference,
  v2 palm-countdown native inference and standalone palm inference, all requiring
  optional external test assets. Do not count these cases as passed.
- [Focused stdlib-only checks](focused-tests.txt): **47 PASS**, including actual
  cross-process locking, all recovery states, no journal mutation, archive/link
  exclusion and cross-platform startup generation. Command:
  `python -S -m unittest tests.test_kiosk_v2_recovery tests.test_kiosk_v2_watchdog tests.test_kiosk_v2_diagnostics -v`.
- [API/Sandbox rerun](sandbox-tests.txt): **16 PASS**, including all six previously
  failing Sandbox widget cases; no payment/API/fixture edits.
- [Actual native launcher](native-launcher.json): STARTING → RUNNING → SUSPENDED
  → RUNNING → STOPPING → EXITED, code 0. Duplicate launch rejected while UI runs;
  lease available after teardown. Camera/delivery disabled, temporary game profile.
- Generated Ubuntu unit validated with `systemd-analyze --user verify --man=no`
  using temporary XDG_RUNTIME_DIR and command network permission. Initial parser
  QA rejected quoting the WorkingDirectory directive; final generator fixes it
  and verification exits 0. ExecStart arguments remain correctly quoted.
  [Mini-PC example](meong-photobooth.service.example) uses illustrative `/opt/meong`
  paths; the validated fixture instead used actual existing cloud paths.
- [Final source hashes and structured results](tested-source.json); compilation
  and whitespace checks pass. The workflow adds the recovery fixtures to Linux
  pure and Windows jobs; GitHub results are recorded only after they exist.

Final full command (existing headless environment, explicit command network
permission for local ASGI internals):

```bash
PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1 MEONG_CI_TEST_REPORT=<report> python tools/run_kiosk_unittests.py
```

The prior HTTP/API stalls reproduced with a minimal FastAPI TestClient under
the command sandbox's restricted network setting. The same fixture works with
network permission, without payment/API/fixture code edits. The targeted rerun
passes 16 cases including all six previously failing Sandbox widgets. Previous
failures remain in the [stage-1 evidence](../portrait-v2-watchdog/README.md).

Stage 2 acceptance: both platforms' script generation, kernel ownership,
read-only/bounded recovery decisions and pre-GUI hold are checked automatically;
actual Ubuntu sign-in/service/desktop/device behavior remains NOT_RUN. Global
recovery, refunds, automatic restart, Google deployment and production are outside
this stage. The docs-first rule and Windows/Ubuntu distinction persist in AGENTS.

## Publication and Windows CI diagnosis

Source `b99c613542139e0ca666b1d990dd811731da12a1` was pushed and its remote HEAD
verified on the required branch. Matching run
[40421965274](https://github.com/pratikto/PhotoBooth/actions/runs/40421965274)
passed the Linux pure job but failed the new Windows portable-check step.
Direct job-log access redirected to a denied log-storage endpoint; the check
annotation exposed only exit code 1, so the underlying case was not established.
No Windows PASS is inferred from the local Linux regression.

The follow-up reuses the existing `run_kiosk_unittests.py` raw-report runner for
this step, retains `-S`, preserves a Windows report artifact and emits the
synthetic unittest failure as a check annotation if needed. This is CI evidence
plumbing, not a weakened assertion or payment/recovery implementation change.
The original failed run is retained; final verification is recorded separately.

Follow-up `abb95b5` / run 40422635023 identifies an ERROR in
`test_game_only_ledger_is_valid_but_corrupt_database_is_held`; passing-case text
filled the annotation before its traceback. Inspection finds the test's SQLite
connection context committed but did not close its file handle before the fixture
overwrote that file. Both SQLite fixture creators now explicitly close connections
with `contextlib.closing`, preserving assertions and production behavior. The
annotation now starts at the failure section. Final Windows verification must
confirm this correction; no earlier failed run is relabelled successful.
