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

## AR-05.b exact reconstruction — 29 October

Metadata-only inspection validates exact binding/booth, protocol/schema/purpose,
frozen template/price/copies, original retention clock, each intent/path/hash/
decoded image and output/final selection. Unknown/legacy/orphan/corrupt/missing
or changed template data stays held; no latest-folder lookup. STAGED bytes are
published/adopted only against their persisted SHA/identity. A proven intent with
no saved bytes is retained as VOID_BEFORE_FRAME audit, permitting a new deliberate
customer capture later; saved quota/bytes are never erased. Unhashed temp bytes
remain held. Complete designs are retained and only unfinished design resumes.

`inspect_resume` returns metadata only. `restore` requires a short-lived, bound,
single-use ResumePermit from a trusted controller, with printer/Drive off. This
in-process seam is not customer authentication; AR-06 validates the actual ticket
before the controller may issue it. No HTTP/view/journal can deserialize a permit.
Restarts lose authorization. Restore never invokes shutter/renderer/print/upload,
and auto-print is disabled. Customer must initiate any fresh countdown.

Initial fixtures ERROR before implementation. Final **63 focused PASS / zero
FAIL/ERROR/SKIP**, plus **nine post-guard reconstruction PASS**. Command:
`.venv/bin/python tools/run_kiosk_unittests.py test_photo_reconstruction test_output_journal test_capture_journal test_photo_allocation test_kiosk_v2_photos test_retention test_workflow`.
Covers 1/2/3 originals, pending/consumed retake, staged JPEG/PNG adoption without
rewrite, two designs/copy preservation, hash corruption, missing ownership and
expired/replayed permits. No raw media exposure in pre-claim inspection.
No private resume is mounted in GUI by this increment. Full regression, real
merchant, Windows/Ubuntu hardware, paper and cloud gates remain NOT_RUN.

## Audit correction — BUG-022, 29 October

A COMMITTED output record requires the original validated PNG even when that
path is missing. Inspection/restore now hold before installing restored state;
no replay/rerender or right cancellation follows media loss. Test-first
reproduction and 61 focused PASS in [audit increment 3](AR00-AR13-CODE-REVIEW.md#increment-3--confirmed-missing-output-reconstruction-defect-bug-022).
Full matching-source regression/CI pending at this source checkpoint.

BUG-022 final verification at `4642841f3e99d8c74b4b379e24922a7ba3f614c9`:
1100 run / 1097 PASS / 3 optional palm SKIP, zero failure/error; matching CI
40790865010 all three jobs SUCCESS. [Pinned audit evidence](evidence/ar-audit-final-verification.json).
