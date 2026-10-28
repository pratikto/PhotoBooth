# AR-07 — native customer recovery and privacy

29 October 2026, Asia/Jakarta. Owner requests full AR roadmap on the existing
branch, incremental safe pushes. Read master/operations/test/privacy/provider,
AR-00–06 and current native Sandbox/photo/app/theme/input/worker source and
fixtures before this stage. No new branch, default change or production.

AR-07.a: original-process recovery ticket screen before payment QR; explicit
customer acknowledgment, no credential clipboard/log/journal. Distinguish recovery
QR from payment/download QR. Reuse existing QR renderer/native widgets and
single-flight worker. Rebooted unknown owner gets neutral claim screen, no old
photo or payment-admission controls before proof.

AR-07.b: customer input or cached-camera QR decode, backend customer proof,
metadata inspection, deliberate Resume action, typed one-use permit, exact
PhotoTest restoration and original STARTED acknowledgment before camera controls.
No new camera handle/scanner/POS mode; scanner adapter uses existing OpenCV on
an in-memory frame because the DEMO-only scanner owns a separate camera and
rejects recovery credentials. No old thumbnails before proof, no auto-shutter or
print. Unknown/missing/expired data remains held with explicit action/error.

Privacy lock on minimize/inactivity hides pixels immediately, clears memory
credentials, fences late callbacks and requires original ticket again; it never
resets financial/media state. Do not start a new customer's order from a held
paid session. Safe release is AR-09, watchdog AR-10.

Validate native 800x1280/452x900 views, QR identity, busy/stale input, resize,
minimize, old-view denial and actual HTTP-to-photo recovery with fixtures.
Original full-price/no-promo, brand QR/copy link, printer/Drive-off and default/
MOCK/v1 behavior remain. Real device/provider and commercial privacy/operating
acceptance are separate; final complete regression follows last functional source.

## AR-07.a delivered and checked

The original process renders a dedicated save-ticket QR with the shared QR
encoder before exposing the provider payment QR/copy link. Explicit acknowledgment
clears raw ticket/cache memory; it never confirms payment. A privacy-held visit
shows neutral content with no old media or photo-admission action. Existing
payment URL validator, centered brand payment QR and full-price consent remain.
Native fixtures explicitly acknowledge their synthetic ticket before exercising
payment actions; renderer adds a distinct recovery-ticket scene/QR-role metadata.

Initial two new native cases ERROR before source. Final **37 focused PASS / zero
FAIL/ERROR/SKIP** (customer session/capability/native adapter/widgets). Twelve
working-tree native PNGs render at both required sizes; both ticket screens were
visually inspected and actual screenshot QR decode confirms the recovery format.
No payload was logged. Pre-commit captures are provisional, not final-source
merchant/device evidence; final AR-12 captures follow later functional work.
Customer restore remains unmounted until the next AR-07.b increment.

## AR-07.b1 — revocable permit and exact resume acknowledgment

Privacy lock now invalidates an already issued, unused in-memory permit through
its controller generation. Reclaiming the original ticket can issue a new permit;
old permits cannot become valid again. The original binding acknowledgment checks
current customer proof and payment again, reuses STARTED with the same transaction,
and fences a late acknowledgment after lock. A server-COMPLETED service permits
only restored result/done, never capture/review or a regressing STARTED request.
This controller seam is not mounted in native navigation until AR-07.b2.

Tests first: nine session cases yielded one FAIL/two ERROR before source.
Final focused **37 PASS / zero FAIL/ERROR/SKIP**:
`.venv/bin/python tools/run_kiosk_unittests.py test_customer_claim_session test_customer_capability test_photo_reconstruction test_qris_session`
with offscreen SDL/dummy audio and permitted local HTTP fixtures. No real provider,
photo, print or Drive access. Full regression remains at final functional source.

## AR-07.b2 — private photo barrier

PhotoTest now exposes an immediate memory-only hide barrier while the I/O worker
runs. Hidden snapshots contain only claim_required, with no old thumbnail, strip,
download QR or folder. Exact same-session restoration is allowed after a fresh
permit; the worker checks privacy generation and permit validity again after slow
reconstruction. Locking during reconstruction cannot republish private pixels.
Manifest/capture/print/delivery state is preserved. Native lifecycle wiring follows
in AR-07.b3; this seam does not itself enable a new customer flow.

Focused **35 PASS / zero FAIL/ERROR/SKIP**, including two new privacy cases:
`.venv/bin/python tools/run_kiosk_unittests.py test_photo_reconstruction test_customer_claim_session test_kiosk_v2_photos test_photo_allocation`.
Synthetic images only; no actual merchant/device/print/Drive acceptance inferred.
