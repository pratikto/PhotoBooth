# FEAT-004 / BUG-009 / FEAT-022 delivery performance — 27 October 2026

Owner authorizes investigation, implementation, tests, documentation and staged
pushes on feature/portrait-kiosk-v2-next. Base/rollback source:
fcabfbb8559778055631ff3a066f14108392ef71 (remote verified unchanged).
No live deployment, cloud deletion, physical print or payment action.

Reviewed before code: AGENTS, root README, documentation index, protocol,
handover, feature status, architecture, decisions, bug register, backlog,
v2 specification/technical design/test ledger, storage layout, drive-photo-layout
QA, FEAT-004 storage QA/setup, photo retention and print/Drive QA.
Current numbered-cloud/offline-admission contracts supersede older linked setup
paragraphs that required an online reserve before consent.

## Findings and scope

The owner reports over five minutes before the large QR, then a disabled Finish
button/processing footer. No session timing log was supplied, so the cause of
that delay is **not proven**. Source confirms synchronous content maintenance,
whole-pool reserve validation after a single claim and a snapshot busy-state
presentation defect. Print was deliberately disabled and stays disabled.

V1 comparison at origin/master 27f3801: `_should_show_result_qr` accepts a real
folder URL before uploads finish; the upload label describes incompleteness.
That explains earlier QR availability, not measured upload throughput. V2 keeps
its stricter UPLOAD_COMPLETE requirement. No v1 early-screen-QR behavior is copied.
The existing v1 upload/checksum/revision engine and QR encoder remain reused.

## Stage 1 — foreground state

PhotoJobs distinguishes foreground commands from background snapshots. A result
rebuilt during a pending snapshot keeps Finish enabled and the footer clear;
foreground commands and uncertain-print guards still block the relevant input.
Snapshot completion updates the footer without rebuilding/reprinting. Result
progress uses real verified-file counts; no percentage/ETA. Only UPLOAD_COMPLETE
can expose the large QR. Safe `delivery_timing` events use a transaction ID and
numeric fields, with a GUI QR-publication event.

Local controlled native regression: one test PASS, 2.080s, Linux/Python 3.12,
Kivy 2.3.1/SDL offscreen/dummy audio. Rebuild during blocked snapshot, disabled
operator printing, restored Finish/footer and return to ads verified. This is
not Windows touchscreen, cloud upload or physical paper acceptance.

Rollback: scoped inverse source commit; preserve photos, counters, claims,
manifest revisions, print/payment journals and original 15/30-day clocks.

## Stage 2 — scheduling, maintenance and timing

A single BoothDriveWorker remains the manifest/network writer. Each pass attempts
one file per transaction in stable transaction order, so old and new transactions
both advance. Successful pending files get another pass immediately; errors wait
the eight-second retry interval. A kick during I/O remains pending. Photo start,
raw capture and composition notify delivery, enabling bind/raw upload before
composition finishes. Foreground photo/print work stays on PhotoJobs.

Reserve requests contain at most five slots, yield before the next batch on a
customer kick, and validate only new/changed/unacknowledged slots. Startup and
15-minute periodic reconciliation revalidate the entire 25-slot pool in batches.
Only acknowledged ownership/link responses populate the process validation cache;
persisted URLs alone never suppress startup checks. Target 25, empty-slot checks,
claim identities and monotonic counters remain unchanged.

Content sync yields after each inventory request, file or 512-KiB chunk. Its
single-worker generator retains staged ranges while customer work runs. Completed
staged files also survive restart, with MD5/size revalidation; an unfinished
file restarts after a process exit. This is not a persistent resumable transfer
protocol. The current snapshot/pointer changes only after all files, checksums,
art decoding and final inventory comparison pass. Unchanged same-path/size/MD5
assets are copied and rehashed from the previous published generation. Corrupt
copies download again. Active generations are retained, with no asset deletion.

Timing records (`delivery_timing` JSON) cover queued/worker_start, bind, retention,
upload_file, request, upload_validation, reserve, content_sync/yield,
upload_complete and gui_qr_visible. Every event has a monotonic timestamp and
transaction correlation ID where applicable; requests include their action,
files include bytes/attempt/index/count. Queue wait is measured from local
notification; restart/discovered work has unknown queue wait, explicitly null.
Request durations include the server, redirects and network together; the protocol
does not let us split them. Error records contain type/status, not raw exceptions,
URLs, tokens, claims, photos or Base64 payloads. Compare monotonic values only
within the same process/log session. Retention clocks remain original UTC clocks.

### Apps Script audit and compatibility

Code.gs changes are limited to avoiding an ACL write when the actual folder
getters already confirm Anyone-with-link/Viewer, and reading the upload retention
description once under the existing action lock. Private/wrong-policy folders
still require a successful setter and post-check. Ownership/parent/path, decoded
size/MD5, existing-file blob comparison and ScriptLock scope remain unchanged.
Repeated ancestors and retry blob reads remain because caching metadata or
shrinking locks needs a separate consistency design. Upload remains serial
Base64 JSON; Apps Script ignores resume_url and retries the full file. Direct
OAuth's resumable implementation is a different transport; no new resumable
Apps Script capability is claimed. More upload threads are not introduced.

No wire/schema change: baseline layout-2 client/new server and new client/baseline
layout-2 server remain compatible. Earlier servers without numbered-layout or
verified-link ACKs still fail explicitly with 409/setup-required; never fake QR
success. Local improvements do not require redeploy if the existing deployment
already meets that contract. Redeploy to receive the two server optimizations.
No live server version was inspected or deployed by this task.

## Reproducible checks and comparison

```text
python -m unittest tests.test_booth_sync tests.test_content_cache tests.test_upload_revisions tests.test_drive_workflow tests.test_apps_script_drive tests.test_retention tests.test_retention_readiness tests.test_kiosk_v2_photo_delivery -v
# 64 PASS, zero skips/failures/errors, 2.050s
python tools/run_kiosk_unittests.py test_kiosk_v2_delivery_widgets
# 11 native PASS, zero skips/failures/errors, 11.835s (offscreen/dummy audio)
node tests/test_apps_script_retention.cjs
# 29 actual-Code.gs VM PASS, zero skips/failures/errors
python tools/benchmark_drive_delivery.py
```

The benchmark executes the baseline worker/cache from pinned Git source and
current implementations using a fake clock/client, temporary data and no sleep,
network or credentials. Assumptions: eight content chunks at one virtual second
each, inventory 0.2s, reserve slot validation 0.1s. Arrival occurs at a completed
chunk boundary. An in-flight request remains non-preemptible (up to configured
HTTP timeout); the result does not promise zero real-world waiting.

| Simulated observation | Baseline fcabfbb | Current |
| --- | ---: | ---: |
| Arrival → worker bind start behind content | 7.2s | 0s after the completed chunk |
| Reserve slots validated after one claim | 25 in one request | 1 in one request |
| New-generation asset chunk requests (one 3-byte addition) | 9 | 1 |
| New-generation download bytes | 4,194,307 | 3 |

These are controlled scheduler/request-count results, **not production Drive
performance**, and do not establish the cause of the reported five-minute wait.
Existing retry/revision/offline/restart/checksum/retention guards remain covered.
Initial service checks intentionally exposed the old all-files-in-one-pass test
assumption and immediate-retry assumption; tests now exercise multiple fair passes
and advance a fake clock past the backoff. An initial wrong test-module name was
corrected; no test case was removed. Raw results are retained with this package.

## Windows update and manual acceptance

Close the GUI first. In the existing checkout/environment, preserve local edits
and reuse the current storage root, booth identity, printer and Drive configuration:

```powershell
git status --short
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
git rev-parse HEAD
python tools/run_portrait_v2.py --drive
```

Use `--drive` while printing is intentionally disabled. Keep `--print --drive`
only on booths whose operator already wants automatic printing. Do not change
the current PHOTOBOOTH_V2_STORAGE_ROOT/BOOTH_ID, delete state or reset counters.
Ubuntu uses the same Python entrypoint in its existing virtual environment;
actual mini-PC/display/device acceptance remains separate. main.py remains v1.

To update the server optimization manually, use the **same Apps Script project**:
copy this source's complete apps_script/Code.gs; preserve UPLOAD_TOKEN,
DRIVE_FOLDER_ID, booth/global root properties and the retention configuration.
Deploy → Manage deployments → Edit existing Web App → New version → Deploy.
Keep existing execute-as/access policy and /exec URL. Record the commit SHA in
the version description and check that Manage deployments selects that version.
No new deployment/token/root is needed. Do not run cleanup or change clocks.
`python tools/check_drive_retention.py` is read-only and can verify the existing
layout/timer contract, but READY does not attest exact deployed source or speed.
Verify reserve/bind numbered-layout/link ACKs through a normal authorized session;
local timing does not independently attest the deployed Code.gs version.

Short manual checklist (record actual HEAD/device and durations):

- Normal session: raw/color/BW files eventually verify; large QR stays hidden
  before completion, then phone opens the correct numbered folder signed out.
- During content sync: start a photo session; timing shows content_yield then
  customer bind/upload before remaining chunks; last good ads/templates remain.
- Disconnect/reconnect: local files remain safe, no new transaction identity or
  duplicate remote file, no print replay; restart resumes pending delivery.
- At result/after completion: progress reflects known stages, footer clears,
  Finish returns to ads; upload continues durably after leaving. Deliberately
  disabled printing stays disabled. Uncertain print still requires inspection.

### Capture timing for the latest session safely

The ordinary launcher prints the diagnostic path. Use the newest
`data/diagnostics/portrait-v2-*.log` (not a readiness JSON). Export only new,
allowlisted timing lines, rather than the whole diagnostic file:

```powershell
$timingLog = Get-ChildItem .\data\diagnostics\portrait-v2-*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Select-String -Path $timingLog.FullName -Pattern 'delivery_timing ' | ForEach-Object { $_.Line } | Set-Content -Encoding utf8 "$env:TEMP\meong-delivery-timing.txt"
Get-Content "$env:TEMP\meong-delivery-timing.txt"
```

For the relevant transaction compare queue_wait_ms, bind/retention/request/file
elapsed_ms and upload_complete → gui_qr_visible monotonic_ms. Match file attempts
and bytes; request timing is nested inside file timing, so do not sum both.
Send only that timing extract plus HEAD and test steps. Do not send private
local_settings.py, raw HTTP logs, tokens, claim ledger, manifests or photo data.
Runtime evidence still needed: actual Windows/Ubuntu network, payload sizes,
server contention/deployed version, five-minute stage breakdown and phone access.
BUG-009 deletion acceptance remains OPEN; no cloud deletion test was run.

## Native visual verification at functional source 2e140c1

Fourteen native screenshots (seven states at 800×1280 and 452×900) are stored in
[screenshots](screenshots/), with source SHA/size/hash/state reports beside this
runbook. Verified result views at both sizes visibly show the large QR, active
Finish and empty processing footer; automatic print remains unavailable for a
completed batch. The separate native test covers operator-disabled printing.
Right-panel screenshot pixels decode to the exact fixture folder URL at both
sizes; this is not a real phone or signed-out Google test.

An initial standard 800px Window screenshot captured an older frame although
worker state had advanced. It is excluded from final evidence. Reused the
existing storage QA approach: original recorder/actions, settled worker state,
then native Widget FBO export, without editing image pixels or application code.
[Reproducible adapter](strict-render-driver.py.txt); source hashes in
[tested-source.json](tested-source.json). No GUI geometry was changed.

## Final regression and publication

Functional source **2e140c1a169fe1a10830ccecd4a6cb63a6e1ac0b**:
[complete local regression](full-tests.txt), **877 run / 874 PASS / 3 SKIP /
0 failures / 0 errors**, 262.743s. Skips are optional real-palm assets in device
recovery, v2 countdown and standalone inference. Native GUI/audio/video opt-ins
were enabled; Linux/Python 3.12, SDL offscreen/software GL and dummy audio.
[Tested-source metadata](tested-source.json) pins all 311 functional source/test/
tool hashes and exact dependency versions. Hashes remain unchanged after testing.
The ordinary DiagnosticSession was separately checked to persist the new safe
INFO timing records. Physical speakers/camera/paper and Google remain unverified.

[Matching-source CI 40448427344](https://github.com/pratikto/PhotoBooth/actions/runs/40448427344)
is **SUCCESS in all three jobs**: pure/Linux, desktop/Linux, Windows portable
startup/native dummy audio. [Recorded jobs/steps](ci-result.json). Job success
is not a claim that optional cases all ran or that hardware passed.

Staged source pushes and remote HEAD verified: **58dc76f** foreground fix →
**2e140c1** scheduling/cache/reserve/Apps Script. This final evidence/documentation
publication changes no runtime and skips CI. Baseline is fcabfbb; the prior local
work branch and unrelated changes were preserved. Standard Git transport became
available with the environment's supported command network permission; no proxy
policy was bypassed. No archive contents were read or modified. No master merge,
default-branch change, Apps Script deployment or cloud deletion occurred.
