# AR-05 — output durability and exact photo reconstruction

28 October 2026, Asia/Jakarta. Owner requests full dependency-ordered roadmap,
immediate tested pushes, existing branch only. AR-04 preserves immutable JPEGs;
read AR-00–04 contracts, privacy/operations/test matrix, original photo/workflow/
manifest/storage/retention and native handoff source before this extension.

AR-05.a: write-ahead immutable composition output, validated PNG/hash and atomic
manifest output acknowledgment. Existing unknown outputs cannot be replaced by
retry. Snapshot frozen template/final-photo identity before rendering. No print/
upload replay. Test crash/publication/commit boundaries and original compositor.

AR-05.b: metadata-only exact-binding inspection; validate protocol, clocks,
booth/order/grant/allocation, frozen templates, each intent/hash/JPEG/PNG/path,
three-original/one-retake quota, finished/current designs and copies. Deterministic
STAGED/PUBLISHED adoption only when hash and identity are conclusive; unknown
legacy/temp/orphan/corrupt data remains held unchanged. No newest-folder search.

Private restore stays unmounted until AR-06 customer proof. A short-lived in-memory
resume permit from the trusted checkout controller will be required before any
thumbnail/strip restoration, reset at process restart; GUI PAID text is insufficient.
Manual countdown only, no camera/print/Drive work on reconstruction. Rollback
preserves ledgers, intents/media/retention and disables new resume admission.
Focused tests each increment, one final full suite after last functional change.
Device/provider/paper/cloud acceptance NOT_RUN.

## AR-05.a publication and evidence

Composition records output_intents with operation/session/expected paths and
final-photo identities before rendering. Raw hashes are verified first. Unique
PNG temp is fsynced/decoded/hash-checked and atomically linked without overwrite;
output/intent/hash/final selection commit together in the original manifest.
A bound paid order also rechecks frozen template hashes before composition.
Current recovery decoder bounds files to 64 MiB/40 megapixels and never resizes
originals; unsupported/corrupt media is held. V2 Sandbox derives local booth
identity from the authenticated trial profile; ordinary/v1 defaults stay intact.

Initial output tests: two FAIL/one ERROR before implementation. Final focused
**71 PASS / zero FAIL/ERROR/SKIP**. Command:
`.venv/bin/python tools/run_kiosk_unittests.py test_output_journal test_capture_journal test_photo_allocation test_kiosk_v2_photos test_kiosk_v2_photo_delivery test_retention test_workflow test_kiosk_v2_sandbox_widgets`
with SDL offscreen/dummy audio. Tests preserve output after lost publication ACK,
reject tampered original captures, and verify exact committed input/output hashes.
No print/Drive effect or old image regeneration follows retry. Full regression
and actual device/provider gates remain pending; restore is not mounted yet.
