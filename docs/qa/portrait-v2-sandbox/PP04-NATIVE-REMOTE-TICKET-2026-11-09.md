# PP-04 B2 original backend Recovery Ticket and native card

9 November 2026; feature/post-preview-qris-checkout; base79d2bb1.

The original Sandbox factory now owns OriginalRecoveryTicketService on the SAME
actual payment coordinator/protector/ledger. Exact authenticated owner/visit/
generation-scoped ticket offer/visible/dismiss/retire routes reuse original paid,
fresh settlement, encrypted escrow, original screen/receipt journals and permits.
Factory startup rejects foreign ticket custody as well as foreign CCP/finance.
The route carries no customer payment/readiness flags or printer transport.

Fixed-role PostPreviewRecoveryClient reuses original bounded authenticated HTTP
and PendingRecoveryOffer. The native RemoteRecoveryTicketSession constructs the
EXISTING PrivateRecoveryTicketCard and VisibleTicketWindow, waits for genuine
complete QR/full-code rendering before backend acknowledgement/timer start,
keeps30 visible seconds/NEXT, and wipes pixels immediately before worker-side
backend dismissal. Network/printing must never extend that screen opportunity.
The controller's prepare/visible-ACK/dismiss methods belong to the serialized
worker; card creation/poll/NEXT/hide belong to the UI. It is not a customer app
launcher or an enabled full merchant profile.

Lost offer-response retry returns the same live original unshown permit. After
child restart only the original never-offered credential can be recovered with
a new memory-only permit; ciphertext/expiry remain unchanged. A shown/dismissed
ticket cannot be offered again. Dismiss ACK retry uses only durable original
presentation identity; plaintext permit references are dropped after dismissal.
Role/mode/booth/group/generation and response shape remain strict. No dummy
payment provider or mock-only service/admission guard was removed.

Test-first import ERROR proved the missing adapter before implementation.
73 host/API/CCP/ticket related PASS (49.717s); final ticket8 focused PASS (see
machine evidence);11 native ticket/card/window PASS (5.626s), each zero failures,
errors/skips. Native tests include both portrait sizes, exact29.999/30.000s,
NEXT during backend outage, privacy hide before rendering/during delayed ACK,
and ACTUAL separate backend child/API/client/real native card after settlement.
Host test also restarts an unshown original paid ticket and refuses redisplay
after genuine visibility/dismissal. Provider/Drive/Linux custody are explicit
synthetic fixtures; no actual merchant/OS login/hardware acceptance is claimed.
No private proof screenshots or raw credential logs are saved.

[Source hashes and actual test evidence](provider-ticket-2026-11-09/verification.json).
New tests are added to existing backend/native workflow commands; no removal,
timeout change or manual broad baseline rerun. Final new-source full regression/
CI remains pending at publication; previous c096504 all-three PASS is preserved.

Next: wire exactly-once original receipt through the owned shared printer lane,
then paid Drive/strip/upload and proof-gated claim/release authority, then full
protected native provider profile. Receipt currently remains PREPARED in this
display-only seam. Existing owner launcher remains mock-only, health still says
fulfillment_enabled=False, and commercial launch is NOT_READY. No paid data,
keyring, media, original jobs or prior eleven owner checks were reset.

Reviewed current handover/AGENTS/protocol, approved security-state and protected
CCP/ticket contracts, original ticket/CCP/coordinator/API/factory/client/native
card/window and original regression fixtures. Preserve original financial,
privacy, generation, once-print and PREPARE/ACK guards in subsequent work.
