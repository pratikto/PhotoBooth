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

## Stage 2 — read-only desktop diagnostic

Stage 1 source **130aae1** is committed/pushed/remote-verified; matching-source
[CI 40254597735](https://github.com/pratikto/PhotoBooth/actions/runs/40254597735)
has all three jobs SUCCESS ([metadata](stage1-ci.json)).

`python tools/check_drive_retention.py` reuses the original
`AppsScriptDriveClient.from_configuration()` and safe P5 metadata inventory.
It makes only `retention_status`, authenticating through the existing private
URL/token. Missing configuration makes **no request**. The report contains
allowlisted state/booleans/counts, source/device metadata and next action; not
credentials, raw errors, account/folder IDs or URLs. It never invokes pool
creation, registration, upload, setup, deployment or deletion.

Report: `data/diagnostics/drive-retention-readiness.json`. Exit 0 means activation
was observed as READY, **not** cloud deletion acceptance. Other states exit 1
and still save a safe report. Existing direct OAuth cleanup works only while
its application is online; this tool specifically checks Apps Script's
independent timer, and does not configure an OAuth installation automatically.

| State | Action |
| --- | --- |
| NOT_CONFIGURED / LOCAL_CONFIGURATION_INVALID | Check the same ignored v1 settings or environment locally; do not send credentials |
| WEB_APP_UPDATE_REQUIRED | Update/redeploy the existing project; an old Web App does not implement the new status action |
| SETUP_REQUIRED / TRIGGER_MISSING | Run setup as the Web App's executing owner, verify one hourly clock, then redeploy |
| DUPLICATE_TRIGGERS | Run existing setup to retain one own cleanup CLOCK |
| TRIGGER_ACCESS_REQUIRED | Authorize trigger access using the executing owner account |
| CONFIGURATION_REQUIRED / DRIVE_PARENT_INVALID | Check the dedicated PHOTO parent in Script Properties, separate from ads |
| DRIVE_API_UNAVAILABLE | Enable Drive API v3 and check the owner's parent access |
| AUTHENTICATION_FAILED / WEB_APP_ACCESS_REQUIRED | Compare private token locally / inspect existing Web App deployment access |
| NETWORK_UNAVAILABLE / CHECK_FAILED | Retry connectivity or inspect setup locally; raw error messages are intentionally excluded |
| READY | Activation/API read observed; verify hourly interval/executions and authorized synthetic expiry separately |

## Windows / Apps Script activation guide

These are reviewable operator steps, **not a cloud action already performed**.
Running setup installs an hourly job that permanently deletes eligible managed
photo folders after 30 days. Confirm the configured parent is the intended
dedicated photo location and that this policy is intended before activation.
Do not use customer photos as test data or change the parent's identity to an
ad/test folder while a kiosk still uses it.

1. Pull the authorized branch. Keep the existing private settings, URL and token:

   ```powershell
   git pull --ff-only origin feature/portrait-kiosk-v2-next
   python tools/check_drive_retention.py
   ```

2. Open the **existing** project in [Apps Script](https://script.google.com/home)
   using its deploying account. Preserve its old code/deployment version locally.
   Replace the complete `Code.gs` with [this repository's file](../../../apps_script/Code.gs).
   In Project Settings → Script Properties, retain `UPLOAD_TOKEN` and
   `DRIVE_FOLDER_ID`. Never publish them in GitHub/chat or create a replacement
   deployment URL just to repair status.
3. Under Services, enable **Drive API v3** (and Google Drive API in a separate
   Cloud project, if applicable). Optional `previewPhotoRetention` is read-only;
   it does not activate cleanup or delete. Its raw candidate identifiers are
   private operational information, not report attachments.
4. Select **setupPhotoRetention → Run** as the Web App's executing owner and
   authorize the requested permissions. Setup performs no immediate sweep, but
   installs the future hourly deletion job. In Triggers, verify exactly one
   `cleanupPhotoRetention`, event type **Time-driven**, hourly interval.
5. Deploy → Manage deployments → edit the **existing Web App** → **New version**
   → Deploy. Keep its `/exec` URL, execute-as-owner and intended existing access
   settings. Saving editor code without redeploying does not update the Web App.
6. Run the diagnostic again. Import its safe JSON into the [eight-item form](windows-checklist.html).
   READY means current activation/parent metadata were observed. It cannot
   guarantee the clock interval (Apps Script exposes no interval getter), future
   executions, child-delete permissions, or actual permanent deletion. Check
   Executions after a real scheduled run and complete only actual observations.

   ```powershell
   python tools/check_drive_retention.py
   Start-Process ".\docs\qa\bug-009-retention\windows-checklist.html"
   ```

7. For GUI v2 delivery use the existing explicit `--drive` profile (or
   `--print --drive`). Never use `python main.py` to test the new v2 UI. A NEW
   transaction must still obtain retention acknowledgement before its files
   upload; older acknowledgements do not continuously prove timer health.

## Actual deletion evidence

The original job and its deletion selection remain unchanged. A live expiry
test needs authorized synthetic data eligible for its existing coarse Drive
creation-age filter (at least 30 days), then uses the immutable registered photo
clock for deletion. A newly created folder with a forged old marker alone is
not an immediate end-to-end test of that filter. No suitable authorized old
fixture is supplied here; mark that check NOT_RUN instead of deleting customer
data, weakening the filter, reducing production retention days, or claiming a
mock deletion proves cloud behavior. An isolated Google test project/parent
must never replace a live kiosk's photo parent during testing.

Use [the Submit form](windows-checklist.html) to retain observations and missing
evidence; imports never tick boxes, and no extra twenty-cycle gate is added.

## Final local validation

[44 focused Python PASS](stage2-python.txt), zero failures/errors/skips, 5.520s.
[Final Python full regression](full-tests.txt): **807 PASS / zero failures/errors/skips**,
238.684s, Linux/Python 3.12.14/Kivy 2.3.1/software GL/dummy PCM and prepared offline
palm assets. [Actual-Code.gs VM](final-node.txt): **19 PASS / zero failures/skips**.
All [238 code/test/workflow/form hashes](tested-source-sha256.json) match the
final tree tested before the stage-2 commit; no actual Google request was made
by the offline suites. A separate invocation without private cloud configuration
correctly returned NOT_CONFIGURED and performed no network action.

[Browser checks](browser-tests.txt) pass: eight fresh unchecked items,
metadata/status import, fabricated READY/verified/pass fields cannot tick cloud
checks, partial Submit 1/8, persistence/download and no horizontal overflow at
360/452/800px. Zero page errors. Initial file:// navigation was blocked by managed
Chromium before loading HTML; the same unchanged form passed via a loopback-only
static server ([environment note](browser-infrastructure-note.txt)).

Form [800×1280](screenshots/bug009-form-800x1280.png) and
[452×900](screenshots/bug009-form-452x900.png) captures were reviewed and hashed
([manifest](form-verification.json)). Their READY/1-of-8 values are explicit
browser fixtures, **not Google observations**. Main GUI layout/assets/flow are
unchanged by this backend/tool increment; its existing cloud renderer remains
in the portrait CI. Actual Windows/cloud acceptance stays NOT_RUN.
