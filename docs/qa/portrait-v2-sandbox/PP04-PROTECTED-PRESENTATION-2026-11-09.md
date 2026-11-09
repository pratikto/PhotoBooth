# PP-04 B1: original backend CCP presentation adapter

9 November 2026, feature/post-preview-qris-checkout; base7f612a4.

OriginalCCPPresentation now retains the exact original protected credential and
render permit in the backend. Sandbox assembly exposes booth-authenticated
owner/visit/generation-scoped CCP offer, genuinely-visible acknowledgement and
permit retirement. Strict bounded bodies reject caller proof/payment/readiness
fields. Private responses/errors are no-store/no-referrer. No raw proof is
persisted or added to logs, URLs, caches, argv or environment.

Offer retries return the same live original permit; after expiration/retirement
or process restart the original ciphertext/verifier/expiry are reused, with a
new memory-only permit. Old callbacks cannot mark a successor visible. Creation
and decryption alone never set offered_at or authorize a charge. Paid/review
orders cannot use the unpaid checkout route to redisplay old proof. Individual
permit retirement does not globally disable future visitors or erase escrow.

PostPreviewCCPClient uses the original bounded authenticated transport and
PendingCCPOffer type consumed by the existing private renderer. No merchant key,
OS protector or dummy provider is constructed in this client. It checks exact
kind/mode/group/booth/generation/schema and full proof role/scope. An immediate
privacy fence drops delayed responses without waiting for network completion.
Only the genuine renderer callback may invoke mark_visible; this is a trusted
native seam, not a public customer claim API or a paid/media/release capability.

**88 related PASS, zero FAIL/ERROR/SKIP,58.646s**, including ten new presentation
methods and eighteen host methods. Actual isolated child/HTTP test begins with
no CCP escrow, proves charge is held both before creation and before visibility,
restarts the child with identical original ciphertext/expiry, refuses the old
permit, then settles one original attempt/entitlement after genuine callback.
Provider/Drive/Linux custody remain explicit synthetic fixtures; Windows uses
actual DPAPI. Initial fixture run had a wrong lifecycle method name and imported
a TestCase directly (unwanted duplicate discovery); both fixture errors corrected.
[Machine evidence](provider-bootstrap-2026-11-09/presentation-verification.json).

Earlier A2 source7f612a4 is pushed/remote-verified. CI42577500308 Ubuntu/native
SUCCESS; Windows still running at this checkpoint. B1 CI/full final regression
is pending. This report does not turn that prior CI into current-source PASS.

## Next source action and limits

Complete original readiness collector shutdown/admission fencing, then protected
Recovery Ticket/one receipt and paid Drive/strip/delivery/claim/release mounting.
The native launcher/service remains mock-only and must not be relaxed through a
fixture flag. B1 is not a complete customer provider profile and does not expose
actual Sandbox payments to the owner launcher. Preserve 30 visible seconds/NEXT,
shared original receipt/strip lane, verified individual URL, fresh settlement,
WAIT while busy, exact PREPARE/ACK and original PAID/OWED/SENDING/UNCERTAIN.

Read prior child-host/provider/Ubuntu continuation, original security-state and
CCP/ticket/financial/private-renderer contracts and source before this increment.
Full target Ubuntu device/account/refund/qualification/production acceptance
remain unfinished. Rollback scoped source only; never reset original journals,
private media/custody or outstanding paid obligations.
