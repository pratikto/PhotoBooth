# FEAT-009 stage 1 — observation and Windows startup

**Historical stage-1 evidence.** Current [stage 2](../portrait-v2-recovery/README.md)
adds guarded startup, launch ownership and Ubuntu service generation. Its final
regression is successful with optional skips disclosed. The old API/Sandbox
stalls below reproduce under restricted command-network access and resolve with
network permission; the raw failures remain unchanged. Stage 1 was rebased to
`ae5c62a` on the newer same-branch Drive repair before stage 2.

Date **27 October 2026, Asia/Jakarta**. User request: “kahukan next roadmap
developement.. nanti aku tes belakangan” (continue the next development roadmap;
manual tests later). This continuation selects the next payment-independent
operational candidate, FEAT-009, as a bounded observation/startup increment.
The prior instruction postponed watchdog in favor of print/Drive; that increment
is already delivered. Manual device acceptance remains deferred, not passed.

Base: **5639400b45fa833de292884031de0ef366db8e76**, existing required branch
`feature/portrait-kiosk-v2-next`. Initial tree clean. Remote refresh failed:
the configured proxy at port 8080 was unreachable. This working-tree increment
has no new remote commit or matching-source CI claim. `old` stays excluded.

## Current source

- `photobooth/kiosk_v2/watchdog.py`: main-thread heartbeat, run/PID/sequence
  validation, monotonic startup/stall timeouts and redacted transition reports.
- `tools/run_portrait_v2_watchdog.py`: external observer around the ordinary
  launcher, existing delivery flags and single-supervisor lease.
- `tools/run_portrait_v2.py`: optional heartbeat scheduling/cleanup only when
  the supervisor supplies its private ephemeral heartbeat path/run ID.
- `tests/test_kiosk_v2_watchdog.py` and v2 CI: fixture and real child-process checks.

Status: **stage 1 IN SOURCE; device acceptance PENDING**. FEAT-009 remains PARTIAL.
No automatic restart, hung-process kill, transaction reset, print/capture replay,
startup installation or Sandbox backend supervision is implemented.

## Run later on Windows

Use the same virtual environment, saved printer configuration and private Drive
configuration as the ordinary launcher. Close any existing booth first.

```powershell
python tools/run_portrait_v2_watchdog.py
# Optional existing delivery opt-ins:
python tools/run_portrait_v2_watchdog.py --print --drive
```

The supervisor writes one report per launch under `data/diagnostics/watchdog`.
Statuses: STARTING, RUNNING, SUSPENDED, STOPPING, STARTUP_TIMEOUT, UNRESPONSIVE,
EXITED or CRASHED. Startup grace is 90 seconds; missed heartbeat threshold is
30 seconds, sampled once/second. Only a fresh main-thread pulse establishes
responsiveness. Report age is not proof of a living supervisor; use its console.
Reports contain no customer identifiers, images, URLs, tokens or environment dump.

Minimizing is reported as SUSPENDED while fresh pulses arrive. OS sleep or an
event-loop stall can temporarily report UNRESPONSIVE; new pulses recover the
status. These are liveness observations, not diagnosis or payment/print outcome.
On a stall the supervisor continues observing. On child exit it preserves the
exit code and stops. Close the kiosk normally to exit; Ctrl+C in the supervisor
prints an instruction and keeps observing, leaving fulfillment untouched.

For startup at Windows sign-in, generate a fresh cmd file **on the actual kiosk**:

```powershell
python tools/run_portrait_v2_watchdog.py --write-startup .\meong-start.cmd
# Or include the same explicit delivery flags:
python tools/run_portrait_v2_watchdog.py --write-startup .\meong-start.cmd --print --drive
```

Review the generated file, then manually create its shortcut in `shell:startup`.
Generation never installs anything, overwrites an existing file, or embeds keys.
It records this checkout's absolute path and active Python executable; regenerate
after moving either. Non-Windows generation and unsafe cmd path characters are
rejected. Existing environment delivery settings are still inherited at launch.
Only delivery flags are accepted; use `run_portrait_v2_sandbox.py` for its separate
merchant trial. A supervisor does not host/restart that trial's backend.

## Recovery and limitations

The lease prevents two supervisors from starting together; it is not a global
lock on every possible direct v1/v2 launcher. Do not run a second kiosk manually.
A supervisor crash is not itself supervised. Before any manual restart, verify
that the prior kiosk/worker process has exited and resolve uncertain fulfillment
using existing journals and operator recovery. A frozen UI can have a live worker.
Repeated report/heartbeat I/O failure leaves the app running; console warnings
identify unavailable evidence. No watchdog transition grants business recovery.

Stage 2 (future): scoped recovery/autostart policy may build on this observer
only with durable paid/unknown/print safeguards and separate failure evidence.
Do not enable a blind restart loop from this stage's liveness status.

## Validation and acceptance

Automated commands use Python 3.12 in the existing Linux cloud environment,
software GL/dummy PCM and isolated fixtures. Results below distinguish completed
checks from blocked regression. No merchant, camera, printer or Google account
was exercised.

```bash
python -m unittest tests.test_kiosk_v2_watchdog tests.test_kiosk_v2_diagnostics -v
python -S -m unittest tests.test_kiosk_v2_watchdog -v
PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 python tools/run_kiosk_unittests.py
python tools/run_kiosk_unittests.py test_kiosk_v2_sandbox_widgets
```

- [22 focused watchdog/launcher/diagnostics checks PASS](focused-tests.txt).
- [15 watchdog checks PASS with site packages disabled](without-packages-tests.txt):
  the help path works without Pillow/Kivy. An initial eager lease import failed
  this check and was moved to the actual launch path before final verification.
- [Native Kivy launcher lifecycle PASS](native-smoke.json): STARTING → RUNNING →
  SUSPENDED → RUNNING → EXITED, code 0, using disabled camera/delivery and a
  temporary game store. This observes the actual launcher heartbeat hook.
- [Source and visual manifest](source-visual-manifest.json): five final runtime/test/CI
  file hashes, twelve verified screenshot dimensions/hashes at both required
  viewports; [idle](idle-800x1280.png) and [compact gallery](gallery-452x900.png)
  inspected. Renderer truthfully records a modified working tree over the base.
- Compile and `git diff --check` PASS. No new GitHub CI/push evidence.

The first full-suite attempt stopped making progress and was terminated after
more than ten minutes, without a completed report. It is **not a pass**. A second
run uses the unchanged test suite with per-case progress and periodic native
stack recording. It started 715 cases, reached all new watchdog checks, then
blocked in `test_qris_api.QRISApiTests.test_authenticated_order` and was terminated.
Neither attempt has a completed full-suite PASS or reliable aggregate pass count.
[Progress](full-suite-progress.txt), [stack traces](full-suite-stacks.txt) and
[machine-readable status](regression-status.json) preserve this limitation.

The [separate Sandbox widget run](sandbox-isolated-tests.txt) completed **6 tests,
6 failures, 0 errors**, 230.953 seconds: `Worker did not settle`. These tests
instantiate the existing app/API fixture directly and do not run the new launcher
or attach its opt-in heartbeat. The trace shows Starlette/AnyIO in-process HTTP
calls awaiting completion. The underlying cause is unresolved; this is a current
validation blocker, not evidence of a production payment defect or an established
watchdog regression. Payment/API/fixture source was not changed to hide it.
**Full regression NOT VERIFIED; Sandbox fixture checks FAIL in this environment.**

Operator checks for later (all **NOT_RUN**):

1. Launch the wrapper; confirm a responsive UI and RUNNING report.
2. Minimize/restore; confirm audio/input behavior and status recovery.
3. Close normally; confirm worker teardown completes and supervisor exits once.
4. With synthetic/unpaid data, confirm crash/stall reports and no restart/replay.
5. Inspect the generated cmd/shortcut; sign out/in only when no active job exists.
6. Recheck ordinary photo/game, selected delivery and protected recovery behavior.

Rollback: use the ordinary `python tools/run_portrait_v2.py` launcher and remove
only a manually installed startup shortcut. Preserve all existing photo, payment,
receipt, reserve, print/upload journals and diagnostic evidence. Never reset data.
