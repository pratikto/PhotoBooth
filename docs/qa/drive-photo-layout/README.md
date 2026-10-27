# Drive photo layout / QR repair — 26 October 2026

**Latest 27 October contract:** [customer FIFO, early verified-folder QR and
immutable mapping](../drive-delivery-performance/CUSTOMER-PRIORITY.md) supersedes
the completion-only screen QR in this earlier source record. Original test
results remain tied to their source, not the later behavior.

Owner report: `python tools/run_portrait_v2.py --print --drive` printed a QR,
GUI kept waiting for upload, scan asked for access, and photos were absent.
Owner clarification requires `PB001/Photo/00000001/{raw,bw,color}` directly.
Scope: source correction on feature/portrait-kiosk-v2-next; v1/Sandbox and old excluded.
Base: 5639400b45fa833de292884031de0ef366db8e76. Reuse original Drive transport,
checksum queue, compositor, printer and manifest merge. No live deployment/deletion.

Read-only live evidence (Meong account): folder PB001V2S2_00000003 at
https://drive.google.com/drive/folders/1ibAPaMzJUnKu0rz75-daT4Uuhqo4cc29
had zero direct children and owner + named-user permissions, no anyone-reader.
The exact installed Apps Script version, Windows logs and transaction manifest
were unavailable; do not assert a specific live exception caused the empty folder.
Source inspection independently confirmed READY reserves were never link-verified,
and binding errors were swallowed without durable GUI explanation.

## Activate the correction on the booth

1. Update the existing feature/portrait-kiosk-v2-next checkout to the repair commit.
2. In the existing **PhotoBooth Drive Upload** Apps Script project, replace Code.gs
   with this commit's apps_script/Code.gs. Keep all current token/root properties.
3. Run setupBoothStorage only if the sibling roots are not configured. Run the
   existing read-only retention diagnostic; setupPhotoRetention is needed only
   if the owning-account timer is missing. It does not delete photos during setup.
4. Use Deploy → Manage deployments → Edit → New version → Deploy on the existing
   Web App. Preserve the /exec URL, Execute as Me and existing Anyone web-app access.
   This Web App access is separate from individual folder link sharing.
5. Restart `python tools/run_portrait_v2.py --print --drive`. Existing explicitly
   Drive-intended layout-2 queues retry in the background, without recapture or
   automatic print replay. Do not delete counters, pool, manifests or local photos.
6. Confirm a numbered folder under Photobooth/PB001/Photo contains raw, bw, color;
   verify images, then open its QR in a signed-out/private browser. Confirm the
   result-screen QR appears after upload completion. Record real paper/phone results.

Only authenticated empty legacy reserves can be moved by this backend. Existing
nonempty, foreign or conflicting numbered folders require review; never delete
or merge them to bypass the protection. Source cannot repair an unupdated
installed Web App by changing Python alone. No cloud account changes were executed.

## Verification

Fixture commands and actual results are in node-tests.txt, regression.txt and
native-tests.txt in this directory. The Python fixture includes full capture →
color/BW → bind → retention ACK → five verified files → visible QR, with no
second upload or print on retry. Code.gs fixtures cover exact layout, permission
failure, original folder-ID recovery, conflict protection and retention scope.
Physical Windows, live Google upload/deployment and phone scan remain NOT_RUN.

Rollback: inspect and apply a scoped inverse commit; preserve all photo/claim/
print/payment state. Do not roll an installed cloud deployment back across this
path contract without separately checking its in-flight queues.

Final targeted verification: **77 Python PASS**, **10 native Kivy widget PASS**
(SDL offscreen/dummy audio), **28 actual-Code.gs VM PASS**; zero final failures
or skips. Python syntax compilation passed. Earlier native fixture failures
were corrected (new sharing acknowledgement fixture and initialized test worker);
the complete final 10-case rerun passed. A full local monolithic run was attempted later but stalled in native execution and was stopped; no full-suite PASS is claimed.
These results do not certify live Google deployment, actual upload, phone or paper.

## Published source and CI

Repair source `0bd69a91693b87637777d00d2971e2caa368a6c8` is verified on the required branch.
[Matching-source CI 40342788877](https://github.com/pratikto/PhotoBooth/actions/runs/40342788877)
completed with **all three jobs SUCCESS**. Desktop delivery 80, Sandbox 139 and
health 80 cases passed without failures/skips; native widgets 108 ran with one
optional model-assets skip. Windows dummy-audio and pure/backend jobs passed.
These are synthetic checks, not actual speakers, Drive deployment or phone scanning.

The separate full local monolithic run stopped progressing in native execution
(no completed unittest summary). Interrupt and normal termination did not finish
it; it was killed as test-process cleanup. Its cause is not established; do not
infer a product or Drive acceptance result from it. The 77 targeted services,
10 native delivery-widget and 28 Code.gs final passes remain independently recorded.
No runtime source changed after those passes or the matching successful CI.
