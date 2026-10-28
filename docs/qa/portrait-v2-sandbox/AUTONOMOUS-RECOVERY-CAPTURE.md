# AR-04 — write-ahead capture and immutable photo publication

28 October 2026, Asia/Jakarta. Continues owner-authorized full AR roadmap on the
existing branch after AR-03. Review: master/test/provider/operations contracts,
AR-00–03 records, photo/storage/retention specs, PhotoTest, TransactionStore,
workflow, manifest locking, checked_path and existing photo/retention tests.
No `old` archive or customer data inspected. Contract recorded before source.

## Intended increments and acceptance

AR-04.a adds an opt-in capture protocol to existing TransactionStore; v2 opts
in, v1 defaults unchanged. Persist intent/session/slot/role/operation/target before
image I/O, write unique exclusive temp, fsync and validate image/hash/size, persist
staged identity, then atomically publish without replacing an existing target.
POSIX uses link/unlink publication because rename can overwrite; Windows uses
same-directory hardlink support. Unsupported filesystem stays held, never uses
an unsafe overwrite fallback. Directory fsync where supported; Windows/power-loss
certification remains separate. Commit raw/upload metadata and intent together.

Retake selection is durable before frame; saved retake and quota/selection commit
atomically. Old/orphan/existing targets remain unchanged and held. Recovery of
staged data requires exact intent/hash/path/manifest and later ownership proof;
no automatic recapture on reopen. No retention deadline renewal.

Tests first: real child abrupt exits after intent/temp/stage/publication/commit,
actual JPEG validation and SHA, no overwrite/orphan replay, quota, symlink/archive
exclusion, disk/write failure and v1/default compatibility. Focused checks then
immediate push. Rollback preserves new manifests/intents/media; disable new
admission and inspect rather than opening protocol-1 files with an old writer.
AR-05 reconstructs exact progress only after intent integrity checks.

## Delivered AR-04.a and evidence

V2 TransactionStore sets capture_protocol=1; legacy/v1 defaults remain protocol 0.
Manifest capture_intents include immutable operation/session/slot/role/attempt,
expected target/temp path, selected retake, state and staged SHA-256/size/dimensions.
JPEG is exclusively staged/fsynced/decoded, intent updated, then linked to an
absent final target and temp unlinked. File publication never replaces an orphan.
Atomic manifest commit records raw/upload/intent and retake quota together.
Archive/link roots are rejected before creation/descent. Original 15/30-day
retention lock/clock is reused. New allocation I/O also releases the snapshot
lock, keeping observations responsive while the worker waits for backend.

Initial five fixtures ERROR before source. Final **73 focused PASS / zero
FAIL/ERROR/SKIP**, including seven capture cases, five actual child-process abrupt
exits (intent/temp/staged/published/committed), actual image hashes, lost retake
reply, no overwrite, links/archive rejection, native Sandbox handoff and v1
workflow/retention compatibility. Command:
`.venv/bin/python tools/run_kiosk_unittests.py test_qris_session test_capture_journal test_photo_allocation test_kiosk_v2_photos test_retention test_workflow test_kiosk_v2_sandbox_widgets`
with SDL offscreen/dummy audio. Reports remain work/ar04-before.txt and
work/ar04-focused.txt pending final evidence publication. No real shutter,
printer, provider, Drive, Windows or Ubuntu hardware acceptance is claimed.
AR-05 handles exact intent reconciliation; this increment intentionally holds
uncertain files rather than silently adopting or overwriting them.
