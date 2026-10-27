# Delivery retry isolation — 27 October 2026

**Later owner correction:** [customer FIFO / held retries / early folder QR](CUSTOMER-PRIORITY.md).
Earlier completion-only QR or interleaved-recovery statements below are dated
source history, superseded by this later contract. Raw evidence stays unchanged.

**Later incident:** [RecursionError in logging and correction](LOGGING.md).
The ten-minute report is not established as a backoff-only delay.

Owner accepts the recommendation to isolate failed transactions and improve
safe bind diagnosis. Continue on feature/portrait-kiosk-v2-next; base/rollback
**e3ac0f94af1402ae4eec1de0295fa43e6bc8c19e**, remote verified unchanged, clean
workspace. Scope: FEAT-004/FEAT-022 delivery, related BUG-009; no cloud deployment,
repair/deletion, batch-upload protocol, new transport or changed print policy.

Reviewed before code: current AGENTS, root README/docs index, protocol,
handover/status, architecture/technical design/specification, decisions,
bug register/backlog/test ledger, storage contract, drive-photo-layout QA,
FEAT-004 setup, retention and the existing delivery-performance runbook. This is
a bounded continuation of that reviewed pipeline, not a new feature migration.

## Runtime evidence and limits

The owner reports upload is faster and supplies a timing extract. For the
successful session, queued → large QR is **122.719s**. Attribution within that
interval, using monotonic timestamps and clipping requests crossing its start:

| Work | Seconds |
| --- | ---: |
| Other transactions' repeated bind requests | 70.782 |
| Five uploads, 867,677 bytes, all attempt 1 | 41.437 |
| Successful transaction bind | 5.516 |
| Retention spans | 3.110 |
| Upload complete → GUI QR visible | 0.891 |
| Remaining local/transition time | 0.983 |

Initial queue wait 17.890s is contained in these categories; do not add it again.
Neither request nor bind wrappers should be counted twice. Three old transactions
return successful bind responses and then ValueError locally. The trace does not
identify which local check failed; exact installed SHA and deployed server source
were not supplied. A folder conflict is a hypothesis, not a proven live diagnosis.
The unrelated content_sync ValueError occurs after this session's QR and remains
a separate investigation. Original five-minute incident remains unmeasured.
Raw user logs/private state are not published in this package.

Source proves that each old failed bind could return after only eight seconds;
three 4–5s requests exhaust that delay, so failures recur between healthy files.
The new fixture reproduces that scheduling pattern and the folder-conflict guard
without claiming the real old transactions have that exact conflict.

## Implementation and invariants

One worker still writes upload progress. Every healthy transaction gets one file
per pass, then at most **one** due recovery transaction gets a turn. The global
recovery interval is 30 seconds after a completed recovery turn. The oldest due
retry goes first; continuous customer notifications do not starve recovery.
A newly arriving customer can still wait for a request already admitted; there
is no cancellation of a live HTTP request or promise of zero latency.

Per-transaction failures back off **30, 60, 120, 240, 300 seconds**, capped at
300. `drive_delivery_retry` stores safe phase/code/failure count and a wall-clock
not-before value. On restart, the remaining delay is bounded to 0–300s and
converted once to the new process's monotonic clock; subsequent wall-clock changes
do not move it. This scheduling timestamp is separate from created_at and the
15/30-day retention clocks. A capture kick wakes the worker but does not bypass
a failed transaction's deadline. Existing pre-update binding/retention/upload
failure markers enter the bounded recovery queue on first discovery.

Successful recovery clears its retry metadata and resets the failure count.
Stale controller saves preserve both the worker's deadline and explicit cleared
value under the existing manifest lock. Original upload revisions/checksums,
claim ownership, local photos, assigned folder identity, empty reserves, counters,
retention/upload hold and strict UPLOAD_COMPLETE QR gate remain intact. No charge
or print replay, reserve deletion or cloud repair is introduced.

Safe timing additions: worker_start.lane (healthy/recovery),
transaction_error.error_code/phase/retry_seconds/failure_count and
transaction_recovered. No raw exception messages, folder IDs/URLs, tokens,
claim digests, photo payloads or remote response bodies are logged.

| Error code | Meaning / operator interpretation |
| --- | --- |
| BIND_FOLDER_CONFLICT | Returned folder differs from the already known local folder. Both identities remain untouched; inspect the existing claim/history before any repair. |
| BIND_TRANSACTION_CHANGED | Transaction identity differs from its directory or changed during I/O. No diagnostic fields are written onto the mismatched identity. |
| BIND_LAYOUT_UNSUPPORTED | Response lacks current layout acknowledgements. Check the existing server deployment. |
| BIND_RESPONSE_ID_MISMATCH | Server acknowledged a different transaction. Stop automatic rebinding; inspect configuration/ownership. |
| BIND_LINK_UNVERIFIED | Actual link-sharing acknowledgement is missing. No ready QR is fabricated. |
| BIND_RESPONSE_INVALID | Folder ID/URL is malformed or they do not identify the same folder. |
| BIND_LOCAL_STATE_INVALID | Local bind-state read/merge failed; the specific guard did not produce a typed conflict. |
| DRIVE_NETWORK_RETRY / DRIVE_REMOTE_REJECTED | Retryable transport/server error versus rejected API action. Raw response is withheld. |
| RETENTION_HOLD / UPLOAD_RETRY | Retention acknowledgement failed or the attempted file needs retry. Files remain queued. |
| MANIFEST_INVALID / *_LOCAL_STATE_INVALID | Local metadata/I/O cannot be processed safely; no identity replacement or reset. |

These codes diagnose the next trace. They do not retrospectively prove the
ValueError cause in the owner's supplied extract. Conflicting old folders are
preserved and periodically rechecked; this update does not claim to repair them.

## Validation and controlled comparison

```text
python -m unittest tests.test_booth_sync tests.test_upload_revisions tests.test_drive_workflow tests.test_content_cache tests.test_retention tests.test_retention_readiness tests.test_kiosk_v2_photo_delivery -v
# 67 PASS / zero failures/errors/skips, 2.256s
python tools/run_kiosk_unittests.py test_kiosk_v2_delivery_widgets
# 11 native PASS / zero failures/errors/skips, 13.165s
python tools/benchmark_drive_retry.py
```

Native uses Linux/Python 3.12/Kivy 2.3.1/SDL offscreen/software GL/dummy audio,
with synthetic camera/printer/Drive. Tests cover priority/global cap/continuous
arrivals, fairness, exponential cap, restart deadlines, capture-kick throttling,
clearing/reset, exact bind codes, unchanged folder/photo/clock, identity races,
stale-save merging, existing revision/offline/QR/print/retention invariants.
The existing restart test now verifies the persisted delay before allowing a
fake clock to reach retry time; its previous immediate-restart expectation was
intentionally superseded. No failing behavioral case was removed.

[Simulation](retry-benchmark.json) runs actual baseline/current worker code with
temporary fixtures and fake clocks, no sleep/network. Assumptions: three old
failed transactions, five healthy files, failed bind 5s, upload 8s. Over five
passes, baseline completed the healthy transaction in **115 virtual seconds**
with 15 old bind requests; current completes in **45 virtual seconds**, with two
old bind requests across the five passes (one occurs after completion). First
network work is healthy rather than an old failure; original folder identities
remain unchanged. This is **not** production speed or a predicted 45-second SLA.
The prior content/reserve benchmark also retains its original output unchanged.

## Windows update and short retest

**Code.gs does not change in this increment. No Apps Script redeploy is needed.**
Client/server wire contract and existing auth/configuration stay the same. An
older client ignores the new local metadata and returns to its earlier short
retry behavior; do not downgrade expecting the new scheduling guarantees.

Close the GUI, preserve local edits, keep the existing booth/storage settings:

```powershell
git status --short
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
git rev-parse HEAD
python tools/run_portrait_v2.py --drive
```

Use --drive while printing is intentionally disabled. Retain --print only if
already authorized by the operator. Ubuntu uses the same launcher in its
existing environment; physical Windows/Ubuntu/Google acceptance is not inferred.

- Run a normal session with old failed transactions present. Healthy worker_start
  should precede bounded recovery; the five files verify before QR appears.
- Export timing using the [existing command](README.md#capture-timing-for-the-latest-session-safely).
  Its output is `$env:TEMP\meong-delivery-timing.txt`; open it with
  `notepad "$env:TEMP\meong-delivery-timing.txt"`. Look for lane, exact error_code,
  failure_count/retry_seconds and upload_complete → gui_qr_visible.
- Restart while a retry is cooling down: pending files/identity remain, and
  restart does not cause all old binds to fire immediately.
- Confirm Finish/footer and deliberately disabled printing retain their behavior.
  Never delete manifests/counters or replace a known folder to clear a conflict.

Source rollback: scoped inverse changes from the base after inspection, preserve
all photos/state/claims and deadline metadata. No cloud deletion or live folder
repair was tested. BUG-009 privacy deletion remains OPEN. Batch uploads and the
post-QR content error are separate follow-ups, not implemented here.

## Final functional-source verification

Functional source **85788251ac6434267185feae99fb3f6b288474c0** was pushed to the
required branch and remote HEAD verified before final regression. Full local
[report](retry-full-tests.txt): **884 run / 881 PASS / 3 optional real-palm
model-assets SKIP / zero failures/errors**, 268.095s. Native GUI/audio/video opt-ins
were enabled; this remains software-display/dummy-audio/synthetic-I/O evidence.
[Exact environment and 313 functional hashes](retry-tested-source.json) match the
committed functional source; no later runtime edits. No GUI geometry/copy changed;
existing reviewed 800×1280/452×900 layout evidence is retained for that unchanged
presentation, and current 11 native delivery tests verify its behavior.

[Initial targeted result](retry-initial-tests.txt) retains the superseded
immediate-restart fixture failure (one expected assertion mismatch). It was
updated to check that restart preserves cooldown before a fake-clock advance;
all final tests pass. No assertion was dropped to hide a runtime failure.
Code.gs remains byte-identical to e3ac0f9; no Google redeploy or deletion occurred.

Matching-source [CI 40455236898](https://github.com/pratikto/PhotoBooth/actions/runs/40455236898)
completed with **all three jobs SUCCESS**: Linux pure, Linux synthetic desktop,
Windows portable startup/native dummy audio. [Job/step result](retry-ci-result.json).
Job success does not imply zero optional skips or physical/provider acceptance.
Final evidence-only publication skips CI and changes no runtime source.
