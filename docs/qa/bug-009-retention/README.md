# BUG-009 — Drive retention activation and diagnosis

Owner explicitly resumes BUG-009 on **26 October 2026 (Asia/Jakarta)**, superseding
the earlier deferral to FEAT-004. This is photo retention only, not advertising
sync or watchdog work. Required branch: `feature/portrait-kiosk-v2-next`.

## Baseline and scope

Base/rollback checkpoint **a432acabfd98c0c12607f08f799b569f245cf610**, verified
against remote before edits. Refreshed master **27f3801** and v1 GUI **38fbaa5**;
their existing `apps_script/Code.gs`, `photobooth/retention.py` and
`photobooth/drive_storage.py` are identical to this baseline. Reuse their existing
setup, hourly cleanup, UTC deadlines, scoped deletion and private configuration.

Existing baseline checks: Python retention/client/delivery **25 PASS**, Node
actual-Code.gs VM **12 PASS**, zero failures/skips. There is no Google connector,
private local settings or Drive environment configuration in this workspace;
installed project/version/trigger state cannot be inferred from repository code.

Bounded remediation: reproduce stale activation acknowledgement; require an
actual clock trigger before acknowledging active registration; preserve the
existing setup/cleanup implementation and repair setup of incorrect trigger
types. Add an authenticated read-only status action and a redacted desktop
diagnostic using the existing v1 Apps Script client/config. Prepare activation
instructions and an unchecked Submit form. Test through fixtures before push.

No cloud deployment, trigger installation or real deletion is performed by
source work. Complete source/tools/evidence first; any installed-account change
or synthetic cloud deletion needs the concrete target and separate execution
scope. Keep 15-day local/30-day cloud clocks, v2 upload hold, print/payment
journals, isolated profiles and separate photo/ad parents.

## Validation plan

Preserve before-fix failures, execute actual Code.gs in the existing Node VM,
test the client/CLI with injected HTTP only, run one final full Python regression,
and validate the offline acceptance form. No GUI runtime layout changes are
planned; existing GUI evidence remains at its recorded source.

BUG-009 stays OPEN until deployed Web App, owning-account hourly trigger and
authorized synthetic cloud-expiry evidence are actually verified. An API status
report alone is not proof of a successful permanent deletion.

## Stage 1 — activation repair

Owner reply: **"Belum / belum tahu"** for running setup and redeploying; installed
activation is not confirmed. [Before-fix output](before-node.txt) preserves two
actual failures: an enabled flag with no clock still acknowledges active retention;
setup accepts a same-name ON_OPEN trigger instead of installing CLOCK. The third
expected failure covers the new read-only diagnostic action not existing yet.

The existing setup now retains one actual CLOCK trigger for cleanup and removes
only surplus/incorrect triggers for that handler. Registration checks current
owning-account clock presence before acknowledgement. An authenticated status
action reads activation plus the configured parent's metadata without changing
markers, cursors, triggers, files or configuration. No setup or cleanup is invoked
by diagnosis. [19 Node VM PASS](stage1-node.txt) and [25 focused Python PASS](stage1-python.txt),
zero skips/failures. Existing boundary/migration/deletion checks still pass.
The existing three-job portrait CI now also executes the actual Code.gs VM suite.

## Rollback

Apply a scoped inverse commit on the same branch after review. Preserve all
manifests/counters/queues, existing credentials and original deadlines. Rollback
must not clear retention holds, replay print/charge/capture or reset customer data.
Repository rollback does not change an installed Apps Script deployment.
