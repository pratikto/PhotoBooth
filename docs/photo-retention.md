# Photo retention

> **CURRENT SOURCE (2026-10-19):** This functionality and related documentation are now part of `master` at the published, immutable `v1.0.0` [source pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0). The previous `feature/kivy-gui` and other feature branches remain historical references. CI passed on the tagged SHA (`07ce51d`, [Kiosk](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245), [Dither](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273)), but physical Windows acceptance is separate. BUG-001/007 audio and BUG-009 Drive retention remain unresolved; payment stays DEMO. **BUG-009 OPEN:** Local 15-day retention exists in source, but Drive 30-day deletion trigger, deployment and permanent deletion are **not verified**. Do not promise automatic Drive cleanup; separately approved deployment and evidence are required.

The platform in this desktop application is the booth's local `photos/` storage.
**Configured targets** are **15 days locally** and **30 days in Google Drive**. Local cleanup is implemented in Python; Drive cleanup requires a separately deployed and authorized Apps Script timer and is **NOT CONFIRMED ACTIVE (BUG-009)**.
Both clocks use the actual transaction's `created_at` in UTC. A pre-created
empty folder's age is not the transaction's age. Assignments, upload retries,
application restarts, and a late upload never renew a deadline.

This applies to all raw captures, original photos retained after a retake, and
finished template images in a transaction. Even offline, failed, incomplete,
or abandoned transactions lose local photos at 15 days. A failed upload can
therefore become unrecoverable after that deadline. Metadata and counters stay
on the booth; they prevent upload resumption and transaction-ID reuse without
retaining the customer's image bytes.

## Activate Google Drive cleanup

The repository includes backend implementation **only**; no GitHub code/documentation update deploys Apps Script or installs the Google-account timer. **The following steps are operator instructions, not an activity performed by this review.**
Use the **existing** Apps Script project that supplies `WEB_APP_URL`:

1. Open the project in [Apps Script](https://script.google.com/home) using the
   account that owns the dedicated booth Drive folder. Replace `Code.gs` with
   the complete current [`apps_script/Code.gs`](../apps_script/Code.gs).
2. Keep the existing **Project Settings → Script Properties** values for
   `UPLOAD_TOKEN` and `DRIVE_FOLDER_ID`. The parent must be dedicated to booth
   photo folders. Do not change the token, parent ID, or Python credentials.
3. Under **Services → +**, add **Drive API**, version **v3**. For a default
   Apps Script Cloud project this also enables Google Drive API. If the project
   uses a separate Google Cloud project, enable Google Drive API there too.
   Deletion calls the REST API with the script's OAuth token.
4. Optionally select and run **`previewPhotoRetention`**. Its execution log
   lists expired candidates under the configured parent without deleting files,
   writing markers, advancing a cursor, or enabling cleanup. Large backlogs are
   bounded to 100 candidates / 20 seconds per pass.
5. Select **`setupPhotoRetention`** in the editor and run it once. Authorize
   Drive access, external requests, and trigger management when Google asks.
   Setup verifies Drive API access and installs one hourly
   **`cleanupPhotoRetention`** trigger for this account. Repeating setup does
   not duplicate that account's trigger. Setup itself does not delete photos.
6. Open **Deploy → Manage deployments**, edit the existing Web App, select
   **New version**, and deploy. Keep **Execute as: Me**, the existing access
   setting **Anyone**, and the same deployment `/exec` URL in
   `photobooth/local_settings.py`.
7. Restart the booth with `python main.py`. In Apps Script's **Triggers**, check
   the hourly `cleanupPhotoRetention` entry. Check **Executions** after its
   first run for authorization/API failures. To perform an immediate expired
   photo sweep, run `cleanupPhotoRetention` from the editor after setup.

Google Drive cleanup uses permanent `files.delete`, not a move to Trash. The
managed transaction folder and its photo descendants are removed together.
The customer QR will stop opening that folder after deletion. The deploying
account needs permission to permanently delete its managed photo folders.

An hourly cloud trigger works while the booth is switched off. A cleanup pass
deletes due photos on its next run, so the sweep can occur up to approximately
one interval after the deadline. Google scheduling delays, service outages, or
permission failures can delay it further; inspect failed executions and retry.
The job resumes large folder backlogs with a continuation cursor and reports
individual deletion failures rather than claiming they succeeded.

## Local operation and synchronization

`PhotoRetentionWorker` cleans local images at startup and then hourly on a
background thread, even in local-only mode. While the booth is powered off,
its disk cannot be cleaned; the next startup sweeps overdue photos. Deletion
holds the same per-manifest lock as photo writes. A persisted expiry marker is
written before unlinking files, so an old capture/review page or delayed upload
callback cannot recreate images or requeue an expired transaction.

The worker removes the dedicated `raw/` and `output/` trees. It keeps
`manifest.json`, `data/booth_state.json`, the Drive-slot ledger, and application
settings. It does not follow symbolic links or Windows junctions into external
directories. Unknown transaction identities or unreadable timestamps are left
for inspection, rather than guessing when or what to delete. Errors are logged
and retried by the next sweep.

Drive registration uses the original manifest time, including offline claims.
The backend accepts an earlier clock but never a later replacement for an
existing one. A registration also claims the slot so an assignment
acknowledgement that is still being retried cannot leave it protected as READY.
Local purge occurs before network work, so an unreachable backend cannot
postpone the local deadline. Expired manifests remain available for registering
the original cloud deadline after the image bytes have gone.

The manifest records `drive_retention_registered_at`, `drive_photos_expire_at`,
and any `drive_retention_error`. An old Web App or a new backend without its
timer enabled is not recorded as an acknowledged policy. Existing uploads can
continue while the operator completes activation, but **cloud expiry is not
active until setup and deployment succeed**.

Direct OAuth installations also register folder deadlines and sweep expired
marked folders while the Python application is online. That fallback alone
cannot provide deletion while the booth is off. For an independent cloud
schedule, install this Apps Script job against the same dedicated parent using
the owning account and complete the setup above.

## Existing photos and deletion scope

Existing local transaction manifests use their original `created_at`. Early
prototype files directly under `photos/` are recognized only by the exact
`photo_YYYYMMDD_HHMMSS_microseconds.jpg` generated-name pattern and expire by
their local saved/modified time. Arbitrarily named root images are untouched.

For Drive transaction folders created before this policy, the cloud job can
adopt a recognizable `raw/` / `output/` / `session_NNN` photo hierarchy. It uses
the oldest actual image's Drive creation time when the original manifest date
has not yet been registered. Subsequent booth registration can shorten that
clock to the true original start, but cannot extend it. A very old folder with
recent first photos therefore does not expire because it was preallocated early.
An empty READY slot has no transaction lifetime and is preserved.

Cloud deletion is restricted to the configured parent's direct transaction
folders bearing the exact policy marker and matching identity, plus recognized
early-prototype root photos. New legacy-API uploads also receive explicit policy
markers. Foreign descriptions, malformed policies, unknown migration contents,
other folders, and corrupt slot ledgers do not authorize deletion. A folder's
Drive creation date is only a coarse search filter; its registered photo clock
decides whether it is due.

## Verify without customer data

```bash
python -m unittest discover -s tests -v
node --test tests/test_apps_script_retention.cjs
```

The Python tests use temporary photo files and fake clients. The JavaScript
tests execute the actual `Code.gs` in a Node VM with a scoped in-memory Drive
and synthetic dates. They cover the exact 15/30-day boundaries, pending/offline
uploads, late callbacks, immutable clocks, unused old slots, safe migration,
permanent deletion, permission failures, preview/setup, authentication, expired
uploads, and bounded backlogs. They do not delete or test a live user's Drive.
