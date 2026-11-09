# Post-preview automatic purchased-strip dispatch

9 November 2026 · `feature/post-preview-qris-checkout` · base `f926fc99d469fc11f138a96d12e64bdd31318bcb`.

## Delivered behavior and scope

The existing post-preview customer page required a separate print tap for every
design, contrary to the agreed automatic paid-output policy. After the original
Recovery Ticket is dismissed and the existing paid worker verifies the customer
Drive URL and prepares immutable strip jobs, the GUI now submits the next
PREPARED job to that same serialized worker automatically. Each successful
observation may advance the next purchased design with its original copy count.
The customer print button is replaced by a short automatic-print status message.

The existing service and dispatcher still verify payment, original ownership,
ticket dismissal, exact output digest, verified folder URL and shared printer
lane. SENDING/UNCERTAIN stops all remaining batches. A worker error stops
automatic polling dispatch; an unconfigured printer does not produce a retry
loop. Redraw/upload observations cannot resend SUBMITTED jobs. Privacy lock,
suspend and the separate 30-second result timeout retire automatic dispatch;
late replies cannot reopen old media or admit another visitor without PREPARE/ACK.

This closes the manual-dispatch seam in STAR stage 1 only. The current launcher
still uses synthetic payment. No merchant/refund transport, real printer/Drive
test, production release, database reset or legacy paid-first behavior changes.
Original PAID/OWED remains separate from submitted bytes and physical paper.

## Evidence

- Before source correction: new native no-tap case FAIL at both 452×900 and
  800×1280; expected copies `[2, 1]`, observed no sends. One method, two failing
  subtests, zero errors, 14.646s.
- After correction: that same method PASS at both sizes, 8.473s. It asserts
  original copy counts, one charge/receipt, no repeat on redraw/status, unchanged
  result deadline, OWED and no physical-paper claim.
- Missing-printer/uncertain-receipt case PASS, 11.576s. The first fixture tried
  changing an already SUBMITTED receipt to UNCERTAIN; the existing ledger
  correctly rejected this with IntegrityError. The final fixture injects the
  real receipt adapter's failed acknowledgment instead; no guard was changed.
- Expanded native checkout/customer/actual-launcher regression: 28 methods
  PASS, zero failures/errors/skips; this started before the additional hold
  method, which was separately verified above.
- Published/remote-verified source **0fe373401ba3cb2501abf3a305df62f8c4054eac**:
  existing registered workflow groups **598 backend PASS (269.942s) + 72 native
  PASS (192.626s)**, zero failures/errors/skips. No later runtime changes.
- Both portrait paid-result views reviewed in separate clean native processes:
  original 2+1 submitted jobs, truthful upload/demo QR and result countdown;
  no customer print button. Multi-resize offscreen text artifacts are not PASS
  evidence; unavailable xvfb-run was replaced with clean per-size native capture.
  [Source/results/hashes](automatic-paid-print-2026-11-09/verification.json),
  [452×900](automatic-paid-print-2026-11-09/result-452x900.png),
  [800×1280](automatic-paid-print-2026-11-09/result-800x1280.png),
  [exact rendering driver](automatic-paid-print-2026-11-09/render-driver.py.txt).
- Matching-source [CI42552901917](https://github.com/pratikto/PhotoBooth/actions/runs/42552901917)
  is verified COMPLETED SUCCESS in all three jobs at exact source 0fe3734. Earlier BUG-046 CI42427430090 was
  independently verified completed SUCCESS at fc8853b.

Tests use original Kivy widgets, actual local service/API/ledger/dispatcher and
synthetic camera/provider/paper/Drive. Linux SDL offscreen/software GL/dummy audio
cannot certify Windows paper, phone download or real merchant acceptance.

## Reviewed contracts and rollback

Reviewed AGENTS, protocol, latest handover, STAR roadmap, original post-preview
owner flow/decision ledger/security contract, PP-041–058 printing/Drive matrix,
refund/worker-fencing and exception rules, BUG-046 and physical quick start;
source worker, immutable print dispatcher, Drive monitor and original native
customer/pilot tests. PP-048/049/050/051/052/053/054 and PP-063 receive related
synthetic regression evidence, not full hardware/provider acceptance.

Rollback only this GUI-dispatch/test change via a scoped inverse commit. Preserve
all customer data, paid jobs, ticket/print/Drive journals, grants and fences.
Never restore or resend a SENDING/UNCERTAIN/SUBMITTED job to test rollback.

Next product work: clarify remaining unpaid preview/synthetic-checkout display,
then the STAR A→B→A and real post-preview merchant integration gates. Preserve
the owner's earlier 11 accepted checks and avoid unrelated feature work.
