# Customer upload priority, early folder QR and immutable mapping — 27 October 2026

Base/rollback: **fcf418d6aab216e455d5fb99a25205c520861cd3**, clean workspace;
remote HEAD verified unchanged. Continue on feature/portrait-kiosk-v2-next.
Owner explicitly authorizes implementing the proposed hold/FIFO/bounded-retry
policy, then requests the real download QR before upload success and emphasizes
that its folder must never serve another transaction. These later instructions
supersede the earlier completion-only screen-QR and interleaved-recovery rules.
No Google deployment, physical printing, cleanup or payment work is performed.

Reviewed before changes: AGENTS, root README/docs index, protocol/handover,
architecture/technical design/roadmap/visual specification, decisions, feature
status/bug register/backlog/test ledger, storage/retention contracts and current
Drive layout/storage setup/performance/retry/logging QA. Reused the actual v1 QR
encoder, checksum upload engine, immutable claims and manifest merge. No second
upload worker, replacement cloud transport or v1 launcher change.

## Customer scheduling

- The single layout-2 BoothDriveWorker discovers customer work first. Monotonic
  transaction IDs provide FIFO across healthy waiting sessions; it uploads one
  file per pass, immediately continuing the same head while more bytes remain.
  Old failures cannot interleave between those customer files.
- Old recovery, reserves and content are held while customer work is pending,
  including short customer-retry waits. Raw capture and composition keep their
  existing notifications. Once all currently saved bytes are verified, no
  capture-waiting/abandoned empty transaction holds maintenance indefinitely;
  a later saved file wakes priority again. A composed complete session retains
  priority through its final required file verification.
- A request already admitted finishes or reaches the existing HTTP timeout.
  A customer arriving during old bind/retention prevents the next old network
  stage. Content and reserve batches retain their existing yield boundaries.
  There is no forced cancellation or promise of zero waiting time.
- A customer failure gets two priority retry deadlines: **5 seconds**, then
  **15 seconds**. The third consecutive failure releases it to background
  recovery (normal exponential deadline, then capped at 300 seconds). Existing
  old failures keep their 30–300-second policy and one failed recovery turn per 30s. Successful old progress stays in a
  durable background lane, runs without that failure throttle while idle, and
  yields to a new customer at the next request boundary.
  Successful progress clears consecutive failures. The same transaction,
  photos, claim and folder survive release. Newer customers can then advance.
- Priority/deadline is persisted in drive_delivery_retry and restored after
  restart. Kicks do not bypass a deadline. Delays are minimum deadlines: polling
  and in-flight requests can add time. No busy loop runs while waiting.
  Background may remain held under a continuous queue of successful customers;
  prolonged failures have bounded priority so they cannot cause that hold.

## Early QR and truthful status

PhotoJobs reuses the original cached QR encoder off the GUI thread. The result
shows that QR when a real assigned destination exists; layout 2 still requires
the verified numbered-layout marker and exact folder ID/URL match. Existing
verified cached reserves can supply it even before binding/upload completes.
No QR is fabricated for an offline visit with no destination, an unverified
legacy reserve, a binding error, local-only, expired or action-required delivery.

Pending message:

> SCAN & SIMPAN LINK  
> Foto sedang diunggah.  
> Cek lagi dalam 30 menit.

This is a **check-back suggestion, not a guarantee of availability within 30
minutes**. Connectivity, service rejection or retention holds can take longer.
The folder may initially be empty or incomplete. Retry/retention holds instead
say upload is delayed and suggest contacting the operator if files stay absent.
UPLOAD_COMPLETE still means the original queue verified all required bytes;
then the hint changes to SCAN UNTUK DOWNLOAD. Polling updates the same widgets/
texture without reconstructing the result or replaying printing. Finish remains
available subject to the existing uncertain-print guard. Upload continues after
returning to ads, and startup resumes pending uploads without another photo.

Timing gui_qr_visible now includes upload_complete=false/true; it measures first
link exposure, independently of upload_complete. Never interpret early QR as
proof of completed upload. The prior export command is unchanged.

## One customer folder per transaction

The durable claim ledger reserves/claims each monotonic transaction exactly
once, never returning a consumed slot/folder to READY. It rejects duplicate
folder IDs across separate reserve batches, ready and claimed entries, and
replacement of an assigned reserve. Offline binding records the original claim's
actual folder in this ledger **before** publishing it in the manifest; repeating
that same binding is idempotent after interruption. Duplicate claims/folders or
changed known folders stop with BIND_FOLDER_CONFLICT and preserve both identities.
Existing manifests also protect pre-update bindings from another transaction
being assigned their folder. No automatic repair/replacement is attempted.

The transaction manifest is the mapping authority:

```text
transaction_id + drive_claim_token
  → local transaction folder / manifest.json
  → drive_folder_id + drive_folder_url
  → upload_files[exact local relative path] + content revision + checksum
```

For example local PB001V2S2_00000008/Photo/01/raw/photo_01.jpg is uploaded only
to the folder recorded for PB001V2S2_00000008; the existing client translates
its remote path to raw/session_001_photo_01.jpg. A later transaction claims
another ID/folder. Printed/saved output, counter, claim tokens and original
15-day local/30-day cloud clocks are unchanged. Retention never recycles an ID.
The backend's existing ownership/claim/parent/link/checksum checks remain required.
There is no new Apps Script deployment or cloud-delete authorization.

## Verification

Targeted command (native Kivy installed, SDL offscreen/software GL/dummy audio):

```text
python tools/run_kiosk_unittests.py test_kiosk_v2_photo_delivery test_kiosk_v2_delivery_widgets test_booth_storage test_booth_sync test_upload_revisions test_retention
# 73 PASS / zero failures/errors/skips, 23.654s
```

Covers FIFO through every file, old recovery/reserve/content hold, arrival during
an old request, two short retries and third-failure release, restart deadlines,
two distinct transaction/file/folder mappings, recovered old work staying in
background after restart/new arrivals, malformed old metadata isolation,
cross-batch folder reuse rejection,
early QR decode/cache/off-GUI encoding, pending-to-retry-to-complete label changes,
unverified/unsafe QR withholding, immutable photo/claim/clock and no print replay.
Two earlier fixture expectations still assumed completion-only QR; they were
updated to the new owner requirement. An initial checksum assertion referenced
a nonexistent transport argument; it now checks the persisted verified checksum.
No failing behavioral scenario was dropped.

The existing benchmark runs actual baseline/current workers with temporary
fixtures and a fake clock: three failed old binds (5 virtual seconds/request),
five healthy files (8 virtual seconds/file). The older e3ac0f9 baseline completes
in 115 virtual seconds; current completes in 40, with its first old bind after
all five files. This is scheduler evidence, **not Google throughput or an SLA**.
Earlier retry-isolation evidence retains its original 45-second result.

An initial 894-case full run passed (891 PASS / 3 optional SKIP), then small-screen
visual review found a clipped notice. Its wording was shortened; final scheduler
review also added durable background classification and malformed-old-metadata
isolation with two regression cases. An interim full run was stopped as test
process cleanup after these source changes. Final regression and screenshots
cover the completed source; earlier passes are not relabelled as final.

Final native screenshots, regression and CI evidence are recorded below. Actual Windows touchscreen, Ubuntu mini-PC, Google ownership/access,
phone download and paper acceptance remain external checks; BUG-009 is OPEN.

## Update and short device check

No Code.gs change or Apps Script redeploy is required for this increment. Close
the GUI, preserve local edits and keep the existing booth/storage/configuration:

```powershell
git status --short
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
git rev-parse HEAD
$env:KIVY_LOG_MODE = 'MIXED'
python tools/run_portrait_v2.py --drive
```

Keep --drive while the operator deliberately has printing disabled. Ubuntu uses
the same Python launcher in its existing environment. Never clear customer data,
reset counters or replace known folders to get past a conflict.

1. Complete a session: save its early QR while upload is pending. Open signed out;
   the folder is the same after all files eventually appear. Check its pending
   notice, verified-file progress and final complete label separately.
2. With old pending failures, timing should show customer files uninterrupted by
   old recovery/reserve/content, apart from a request already admitted. If the
   customer repeatedly fails, its third consecutive failure releases priority.
3. Compare two visits: different transaction/folder IDs, correct local files in
   each, same destinations after restart, no extra print. An ownership conflict
   must remain held and must never be bypassed by changing the manifest.

Rollback: inspect scoped inverse commits, preserving manifests/claims/counters/
photos/print journals. Keep the logging-recursion fix. Older clients ignore the
new priority flag and do not provide this scheduler/early-QR contract; existing
retention deadlines and cloud configuration remain unchanged.

The older eleven-item delivery form now has a fresh browser storage key for the
changed early-QR contract; previous browser answers remain under the earlier key
and do not automatically pass this new source. No repeated twenty-cycle test is added.

## Final source and evidence

Functional source **311f3d8f5e379ed6647e4318c0c73a690671376c** is pushed on the
required branch; remote HEAD verified. [Full local report](customer-full-tests.txt):
**896 run / 893 PASS / 3 optional palm-model SKIP / zero failures/errors**,
273.159s. The skips are optional real-palm assets in device recovery, v2 palm
countdown and standalone inference. Installed-Kivy native cases, including the
console-active logging regression, run locally. Earlier source passes are kept
as historical evidence; the final run is after all functional changes.

[Matching-source CI 40472339778](https://github.com/pratikto/PhotoBooth/actions/runs/40472339778)
is **SUCCESS in all three jobs**: Linux pure/navigation/audio, Linux native
synthetic GUI, Windows portable startup/native dummy audio. [Actual job/step
result](customer-ci-result.json). Job success does not mean all optional cases ran
or that real hardware/provider acceptance passed.

[313 functional source/asset/test/tool hashes and environment](customer-tested-source.json)
remain unchanged after testing and through this evidence-only publication.
Code.gs is byte-identical to base fcf418d; no server redeploy is needed. The
logging-recursion fix remains intact. No Google operation, physical print,
archive inspection, data deletion, identity reset or master/default change occurred.

Fourteen exact-source native FBO captures at 800×1280 and 452×900 are in
[customer-screenshots](customer-screenshots/), with [hash/dimension/pixel-decoding
results](customer-visual-verification.json) and per-size reports
([800](customer-delivery-report-800x1280.json), [452](customer-delivery-report-452x900.json)).
Pending, retry, verified and retention-held views were visually reviewed at both
sizes. Eight large right-panel screenshot QR crops decode to the exact fixture
folder URL; pending QR and its complete 30-minute notice are readable at 452px.
Earlier clipped-text captures are excluded. The original recorder and existing
[strict FBO adapter](strict-render-driver.py.txt) were reused without image edits.
These are synthetic screenshots, not signed-out phone/Google/paper acceptance.
The separate native test preserves operator-disabled printing/active Finish.

Next device evidence: update the existing environment, let the existing pending
queue resume, compare two actual transaction/local/Drive folder mappings, and
check the early QR plus eventual complete files. No new photo is needed just to
resume a pending queue. BUG-009 cloud deletion and previous old-folder conflicts
remain unverified/protected; this work does not repair or close them.
