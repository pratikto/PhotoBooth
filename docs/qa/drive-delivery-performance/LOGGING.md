# Delivery logging recursion correction — 27 October 2026

**Later owner correction:** [customer FIFO / held retries / early folder QR](CUSTOMER-PRIORITY.md).
Earlier completion-only QR or interleaved-recovery statements below are dated
source history, superseded by this later contract. Raw evidence stays unchanged.

Base/rollback: **15854e05021e30f65bc0e81074e72338ea88625b**, clean workspace on
feature/portrait-kiosk-v2-next; remote FETCH_HEAD verified unchanged. Owner reports
>10 minutes with no verified file and provides a fresh timing extract. Continue
within the authorized delivery regression fix; no new transport/cloud repair.

## Evidence and diagnostic correction

The new extract shows an old transaction's **BIND_FOLDER_CONFLICT**, followed by
RecursionError inside reserve/request timing. A new transaction was queued, but
no worker_start for it appears in the supplied extract. Repeated LOG.info source
lines and Kivy `stderr:` warnings follow. Exact full traceback, installed HEAD
and triggering handler configuration were not supplied, so do not assert the
precise Windows handler that initiated the loop or independently prove the final
thread-exit point. This evidence supersedes the provisional suggestion that
long backoff alone explains this >10-minute incident.

Source confirms a failure path: delivery_timing propagated through root; Kivy's
default KIVY logging mode redirects stderr back into logging. Kivy 2.3.1 itself
warns that handlers writing to redirected stderr can create loops. A RecursionError
from timing could escape even the worker's error-reporting path and stop it.
A controlled reproduction with **real Kivy**, console enabled and a late root
StreamHandler bound to redirected stderr raised RecursionError before the fix.
Afterward the same fixture's event succeeds and records one timing event.
The test fixture creates this hazardous configuration deliberately; it does not
claim that the user's exact late handler has been identified.

Previous synthetic regressions used KIVY_NO_CONSOLELOG=1 and missed this path.
Their passes remain historical software checks, not successful device acceptance.
The old folder conflict is now confirmed for the transaction identified in the
new trace; do not infer every earlier ValueError has the same cause. Known local
folder identity remains protected. No folder/counter/photo was replaced or deleted.

Reviewed before changes: current AGENTS/protocol, delivery/retry QA and latest
handover/status/bug/architecture/technical/storage/retention contracts in this
session; actual diagnostics/launcher/timing source and Kivy logger documentation.
Scope is logging isolation and worker survival, not increasing backoff again.

## Fix

- `photobooth.delivery` timing no longer propagates to root/Kivy console handlers.
  DiagnosticSession attaches its existing real-file handler directly and removes
  it on close. File output remains in data/diagnostics/portrait-v2-*.log, with
  the same safe JSON fields and export command.
- A per-thread re-entry guard and an exception boundary prevent timing sink or
  formatting failures from changing upload success/retry or terminating a worker.
  If a sink is broken/full, timing can be unavailable; the business operation
  continues. Actual bind/upload exceptions are still raised and retained normally.
- The ordinary v2 launcher defaults to **KIVY_LOG_MODE=MIXED** before Kivy import.
  This leaves stderr as a real stream. Explicit logging-mode overrides remain
  respected; the update command below selects MIXED deliberately for recovery.
- Native Kivy logs are attached to the same persistent diagnostic file when
  MIXED mode keeps them off root, preserving provider/exception evidence without
  double logging. Session teardown removes only its own handlers.

No Code.gs, Drive wire protocol, folder identity, backoff interval, photo manifest,
retention clock, QR readiness, printing or payment behavior changes here.
The existing retry simulation retains identical output. There is no new upload
throughput claim; the correction prevents diagnostics from breaking delivery.

## Validation

```text
python -m unittest tests.test_kiosk_v2_diagnostics tests.test_booth_sync tests.test_upload_revisions tests.test_retention -v
# 54 PASS / zero failures/errors/skips, 1.586s
python tools/run_kiosk_unittests.py test_kiosk_v2_delivery_widgets
# 11 native PASS / zero failures/errors/skips, 14.521s
```

New checks cover real launcher/Kivy with console **enabled**, a handler attached
after Kivy initialization, original stderr preservation, one timing record,
native + ordinary messages in the file, handler cleanup, re-entry and broken
sink survival. An actual BoothDriveWorker thread with a synthetic failing timing
handler remains alive and verifies its queued file once, without false retry.
A failing business action still raises its original exception. The real Kivy
subprocess test removes inherited KIVY_NO_CONSOLELOG/KIVY_LOG_MODE; it cannot
silently inherit the console-disabled test configuration. It requires Kivy
and explicitly skips when that dependency is unavailable (pure CI); native CI
and local installed-Kivy checks run it. No real Drive/camera/printer was used.

## Windows mitigation and update

After closing the current GUI, the existing code can already avoid Kivy stderr
redirection with this temporary mitigation in the normal Python environment:

```powershell
$env:KIVY_LOG_MODE = 'MIXED'
python tools/run_portrait_v2.py --drive
```

For the permanent timing-safety fix, close the GUI, preserve local edits and
update the existing branch/environment, keeping the same data/booth profile:

```powershell
git status --short
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
git rev-parse HEAD
$env:KIVY_LOG_MODE = 'MIXED'
python tools/run_portrait_v2.py --drive
```

**No Apps Script redeploy is required.** Use --drive with printing still disabled;
only retain --print on an already operator-authorized printing booth. Existing
pending local transactions resume; no new photo session, counter reset, manifest
edit, folder replacement or physical print replay is required. The same launcher
and MIXED mode work on Ubuntu; physical-device validation remains separate.

Retest the pending session: worker_start then upload_file/validation/completion
should appear in the latest diagnostic file, followed by gui_qr_visible while
its result page is open. If the customer has left the result, retrieval uses the
existing operator/transaction-reference process; idle never exposes previous
photos. BIND_FOLDER_CONFLICT for an old transaction remains a protected hold,
not permission to replace its known folder or claim live repair success.

Export fresh timing with the [existing command](README.md#capture-timing-for-the-latest-session-safely),
then open `notepad "$env:TEMP\meong-delivery-timing.txt"`. Do not send credentials,
full HTTP logs, manifests or customer images. A missing/broken timing destination
is now diagnostic loss, not automatic business-operation failure.

Rollback: inspect a scoped inverse commit while preserving all durable queues,
claims, counters, files and original deadlines. Retain MIXED as the mitigation;
reverting source alone reintroduces timing propagation/sink fragility. No live
upload/deployment, deletion or old-folder repair is performed by source QA.

## Final local verification and source publication

Functional source **4c31406943ad3a384d217878f7c2aa7fe074dd60** is pushed to the
required branch and remote HEAD verified. Full local [report](logging-full-tests.txt):
**888 run / 885 PASS / 3 optional palm-model assets SKIP / zero failures/errors**,
262.543s. The real-Kivy console-active integration runs in its own clean child
process and passes; it is not hidden by the outer console-disabled configuration.
[Environment and 313 exact functional hashes](logging-tested-source.json) remain
unchanged afterward. Native delivery widgets: 11 PASS; targeted checks: 54 PASS.
The prior retry scheduling simulation is byte-for-byte unchanged.

No GUI layout/artwork/QR-gating change was made. Earlier reviewed native layout
captures retain their source-specific evidence; new-source behavior is tested
through native widgets. Linux software display/dummy audio and Windows CI do not
certify actual speakers, camera, paper, Ubuntu mini-PC or live Google performance.
The user's complete traceback/HEAD and successful pending-session delivery after
this correction remain external evidence to collect. No cloud deployment,
old-folder repair, deletion, branch/default change or master merge occurred.

Matching-source [CI 40460799605](https://github.com/pratikto/PhotoBooth/actions/runs/40460799605)
completed with **all three jobs SUCCESS**, including the Windows diagnostics
module's real-Kivy console-active subprocess. [Job/step result](logging-ci-result.json).
Pure Linux may skip the real-Kivy check when Kivy is absent; installed-Kivy local
and Windows runs cover it. Successful jobs are not a claim of zero optional skips.
Final evidence-only publication skips CI and changes no runtime source.
