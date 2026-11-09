> **Windows CI update:** the first Windows job129268536077 was CANCELLED at its existing15-minute budget, no suite summary; interrupted inside unchanged retention-readiness inventory/Git status. Completed log inspected; not a PASS or a proven application assertion failure. Earlier B4 Windows717 completed653.838s. A single failed/cancelled-job-only retry at the SAME ac804fd is running as129278840319; original timeout/tests/guards unchanged. Ubuntu726 and native88 remain verified SUCCESS. The retry result must be inspected separately.

# PP-05 B5 protected native delivery continuation

9 November 2026. Base9d372804, existing feature/post-preview-qris-checkout.

## Bounded contract before implementation

Connect the existing scoped payment/proof/delivery clients to a distinct native
facade and reuse the original PhotoJobs, capture/retake, checkout views, private
cards and timers. Native code owns neither a provider nor OS/Drive credentials.
The first facade accepts only its own live, originally captured and already
frozen draft; no bootstrap auto-restore, proofless claim or new payable admission.
Backend remains authoritative for paid ticket, receipt, URL, quantities and jobs.
Existing mock-only guards and default merchant-profile/health gates stay intact.

Test original HTTP/backend delivery with fake external transports; ticket before
delivery; truthful pending upload/transport-only submission; original uncertainty
without replay; scope/late-response privacy holds. Next reuse actual native views
at452x900/800x1280, preserve genuine-render clock independently of worker ACK,
automatic purchased batches and result privacy timeout. New-customer admission
must remain held until the protected original proof/collector/worker PREPARE/ACK
protocol is implemented. Do not borrow mock A-to-B acceptance as Sandbox proof.

Reviewed: complete cross-account prompt9d372804; AGENTS/protocol and current
provider-native/B4 continuation, original security/owner decision/CCP/ticket/
shared receipt/Drive delivery contracts, B4 core/API/client and B2/B3 native
card/clock/receipt reports, collector fence, original photo/checkout service,
app/PhotoJobs, host/factory/proof clients and affected original tests. General
status files contain large historical sections; current checkpoint takes
precedence without relabeling historical tests or old acceptance as new PASS.

Focused tests then immediate micro-commit/push/remote verification. Final changed
source regression and exact-source CI separately. No live merchant transaction,
paper, upload, cloud deletion, refund, deployment or production approval.
Rollback scoped source only; retain original ledger/media/custody and OWED,
attempt/print/upload/folder journals.

## B5-A original protected facade

ProtectedCheckoutService reuses PrivatePhotoService and the original payment
transition methods, without invoking any mock constructor or constructing a
provider/custody/Drive transport. It continues only its own live captured/frozen
lease via accept_frozen_checkout; an empty/reopened facade cannot restore an old
visit this way. Proof, ticket, receipt and paid preparation/observations/next
batch use the existing authenticated clients and exact original backend actor.
Hide is immediate, retires clients and clears all display references; late
responses cannot restore a private snapshot. Shared durable retirement retains
the original local intent/generation for backend lifecycle reconciliation.

Nine new actual API/backend facade methods PASS (12.368s). Initial nine-method
run had seven failures because the new fake Drive readiness response used the
wrong envelope field; corrected to the original protocol without changing any
guard. python-escpos was installed in the existing project venv (required by
the original raster builder). Controlled fake external transports and Linux
test-only key lookup; no actual device/account/custody acceptance inferred.
Focused affected regression and exact log/source evidence are recorded in
[the verification manifest](evidence/pp05-protected-native-2026-11-09.json).

This is not a mounted merchant product: protected freeze/admission, native views,
proof-gated claim, exact original worker release, launcher and real configuration
are still unfinished. freeze_checkout explicitly holds until its protected
orchestration is mounted. Existing customer launcher and health stay disabled.
NEXT: reuse shared checkout view/controller code in a protected native app with
genuine-render timer, automatic batches, truthful status and protected Ads; then
implement the original claim/collector/worker release protocol.

## B5-B original native views and automatic output

Shared checkout controls are reused through an internal base. The original
PrivateCheckoutFixtureApp still requires PrivateCheckoutService; the distinct
ProtectedCheckoutApp requires the exact protected facade and refuses synthetic
admission/callback injection. No launcher enables it. Original live/frozen proof
and payment, mandatory ticket/one receipt, paid folder/status/automatic batches
now run through real native controls and the authenticated API/client boundary.
Results retain their independent30s timeout; privacy-retired Ads cannot admit B.

Six new methods plus original checkout/remote-ticket/receipt scope: **35 PASS,
zero failures/errors/skips,119.812s**. Both portrait sizes complete original
2+1 batch submission without a print button, truthful pending upload and paper
uncertainty, then protected result return. NEXT/exact30s wipe during held receipt;
held strip completion cannot restore old pixels or dispatch the remaining design.

BUG-050 reproduced one assertion FAIL: shared generic worker submission disabled
NEXT while the genuine-visible backend ACK blocked. The protected profile now
submits that ACK on the SAME serialized worker without freezing ticket controls;
its clock starts at the original genuine-render callback. Original ACK/receipt
ordering remains required. The five-method correction PASS19.254s precedes the
six-method/35 affected final scope. Earlier new fixture errors were diagnosed:
submission before constructing a photo page and trying to recompute editable
previews after freeze; tests now retain actual pre-freeze preview snapshots.
No immutability/render/financial guard was weakened.

Actual Xvfb/X11 additional journey PASS at452x900/800x1280; both status views
visually inspected. Initial offscreen framebuffer screenshots had black/corrupt
upper regions and are NOT visual acceptance. Official Debian Xvfb package was
extracted under task-private work/ (no sudo/system mutation); real X11 views show
original branding, synthetic-download fixture, pending bytes, transport-only
paper observation and independent result countdown. No private proof screenshots
were saved. Private status captures/logs are not portable; sanitized hashes only.

Next: actual separate backend-child/native delivery test, original proof-gated
claim and exact collector/camera/file/print/upload release with PREPARE/ACK;
protected freeze and trusted launcher/configuration remain gated. This native
increment is not full merchant/customer or commercial readiness. Full changed-
source regression and exact-source CI remain pending.

## B5-C actual child/HTTP/native boundary

One additional actual separate backend-child/loopback HTTP/native proof/card/
original receipt/folder/purchased-strip journey PASS3.279s. Native captures three
originals and one selected-slot retake, freezes the same original approved quote,
then original protected backend authority permits genuine ticket and exactly one
receipt plus one two-copy purchased batch. Contract hash and all raw/retaken JPEG
hashes survive unchanged, one attempt/ticket, upload remains pending/OWED; actual
backend shutdown succeeds after original requests finish. Test-only assembly
injects fake provider/Drive/Linux key lookup/printer and stubs external uploader
scheduling; no production runtime test switch or merchant launcher was added.

First child test failed readiness because its isolated workspace reserve state
was unprepared. Explicit fixture preparation repaired that missing prerequisite.
Next two attempts wrongly required an intermediate PENDING screen: this existing
child fake settles on the independent GET immediately after CREATE. The final
test requires actual independent settlement instead of inventing a visible
PENDING period. No product settlement/readiness/pacing guards changed.

All B5 runtime is published; B5-C test fixture now also pushed. NEXT source:
original protected proof-gated claim/recovery and exact collector/PhotoJobs/
camera/receipt/strip/upload PREPARE/local receipt/ACK handoff. Do not use mock
admission or proofless reopening. Protected freeze and full trusted launcher/
printer/configuration remain explicitly unmounted; new-customer admission holds.
Final changed-source registered regression/CI will be recorded separately.

## Final registered source regression

Exact source **ac804fd008162a34e0b14ad32f23e6693794ee1c**: **726 backend
PASS270.631s +88 native PASS224.936s**, zero failures/errors/skips and both
process exits0.34 original Apps Script VM PASS, syntax PASS, pip check clean.
Actual Xvfb/X11, software GL and original device-off profile. These are the
complete current registered PP backend/native workflow groups, not a claim to
rerun the older1,934 all-opt-in whole-repository suite. Commands, log digests,
all eight changed source/test/workflow hashes and CI are in
[the final manifest](evidence/pp05-protected-native-final-2026-11-09.json).

CI42648574582 at the SAME ac804fd: Ubuntu726 PASS201.258s; native88 PASS181.353s,
zero failures/errors/skips, both jobs SUCCESS and completed logs inspected.
All nine new backend and seven new native methods observed PASS, including
actual child delivery and BUG-050. Owner Linux packaged preflight and screenshot
steps succeeded. Windows is still pending; do not infer three-job PASS yet.
Earlier88114a0/43b4c2a CI was superseded normally by the next source/test push.

## New method to scenario traceability (partial software evidence only)

Names below are method suffixes in ProtectedCheckoutTests (backend) or
ProtectedNativeWidgetTests (native); the final manifest identifies full IDs.
No full PP/provider/device acceptance row is promoted from these subassertions.

| Added scenario/method | Existing acceptance scope | Actual boundary |
| --- | --- | --- |
| same_frozen_photos_paid_ticket_original_folder_and_batches_over_http | PP-004/014/041/049/054/058 | Original2+1 contract/jobs, one charge/ticket/folder, pending bytes, OWED |
| native_original_ticket_then_automatic_2_1_delivery_and_protected_result_return | PP-041/049/054/058/071 | Both actual native layouts, auto original batches, protected Ads; no admitted B |
| next_and_exact_30_seconds_wipe_ticket_while_receipt_http_is_blocked | PP-042/051/079 | Original native NEXT/exact30s independent of real request barrier |
| slow_visible_ack_cannot_delay_genuine_native_timer_or_next | PP-041/042/051 | Genuine native callback starts clock; blocked backend ACK cannot disable NEXT |
| actual_separate_backend_child_to_native_original_paid_delivery | PP-001/004/014/041/054/058 | Actual child/HTTP/native original retake and hashes; fake external effects |
| partial_photo_holds_all_following_batches_and_never_replays; uncertain_first_photo_prevents_every_later_native_automatic_batch | PP-050/052/071 | Partial original driver bytes, quarantine later designs, no paper assumption |
| original_receipt_uncertainty_holds_delivery_without_replay | PP-042/050/051 | UNCERTAIN original receipt prevents folder/photo work |
| lost_bind_reply_retries_same_original_purchase | PP-053/054/081 | Same original transaction after lost binding response, no recharge |
| late_delivery_reply_cannot_restore_private_snapshot_after_hide; result_timeout_wipes_during_blocked_original_strip_and_late_reply_stays_private | PP-063/071 | Old response cannot reopen retired A; protected B admission remains disabled |
| wrong_mode_and_reopened_root_do_not_authorize_original_takeover; original_fixture_guard_and_protected_profile_reject_cross_authority | PP-038/046/062 | No mock/provider authority mix, tokenless reboot adoption or synthetic admission |

Still NOT IMPLEMENTED/MOUNTED: protected original customer claim/free/busy WAIT
and exact local worker/collector PREPARE-receipt-ACK/archive protocol; protected
freeze orchestration and complete trusted customer launcher/printer configuration.
The existing mock A-to-B-to-A remains regression only. Actual provider/refund/
Drive ACL/retention/paper/Ubuntu startup/backup and final-profile2h/actual4h remain
separate. No unchanged repetition of the owner's eleven passing smoke steps.

All completed runtime/tests are pushed, no local runtime/test WIP remains.
Final documentation is a companion checkpoint; local logs/display packages,
private fixture roots/caches/screenshots are not portable through GitHub.
No active local test/backend process after regression; Xvfb is a test display
only and will be stopped before handoff. Roll back reviewed source only; never
reset or replace original journals/custody/photos/PAID/OWED or replay uncertainty.
