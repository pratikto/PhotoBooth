# BUG-048 — backend ACK could delay the native ticket privacy deadline

9 November 2026; source65208c3; feature/post-preview-qris-checkout.

Review of the new, still-unmounted remote ticket component found its window
started after the backend visible-ACK returned. Slow/lost HTTP acknowledgement
could leave genuinely rendered private QR/code onscreen beyond30 seconds.
This is a source defect, not an owner/device failure or the earlier floating
point fixture issue. Customer merchant profile remains disabled.

A native regression genuinely renders the existing original card, stalls the
visible-ACK worker, advances its exact clock to30 seconds and requires immediate
QR/full-code wipe while that worker remains blocked. Before correction: **one
FAIL, zero errors/skips,1.462s** (window was not active). After correction:
**12 related native PASS, zero failures/errors/skips,8.548s**, including the
same stalled-ACK regression and the prior native/backend child/card/window tests.

RemoteRecoveryTicketSession now starts the ORIGINAL VisibleTicketWindow from
the genuine card-rendered callback on the UI thread. Backend acknowledgement
continues separately on the serialized worker, without starting/resetting that
clock. NEXT/timeout wipe stays immediate; late ACK cannot reopen the window.
Original paid/owner/escrow authority and durable visibility/dismissal remain
backend owned. No proof, media, receipt transport or booth-release guard is
weakened. No private screenshot or raw token log is saved.

At source65208c3 the original full native suite also passed79 methods (294.611s),
but lacked this new case. That prior broad PASS is not claimed to detect this
new defect or verify the correction. Final corrected-source native regression
and source-matched CI remain pending at publication; backend runtime unchanged
by this correction. Synthetic account/custody/Drive/transport fixtures only,
actual native rendering and child HTTP. Not commercial/device acceptance.

[Machine evidence](provider-ticket-2026-11-09/clock-verification.json).
Next remains original once-only receipt/shared lane and paid delivery/claim/
release/full protected customer profile. Rollback only scoped source; retain
original protected ledger, paid rights and uncertain receipt/strip journals.
