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
