# BUG-026 — verified expired QR renewal in the existing Sandbox checkout

31 October 2026 (Asia/Jakarta). Base/remote c478bce, same feature branch.
Owner explicitly approves implementation with "oke gass", then requests staged
commit/push checkpoints to survive session limits. Earlier unsolicited draft was
withdrawn, kept privately under work/, never committed/pushed. Its separate
closure-page proposal is NOT this approved customer flow.

## Approved flow and bounded implementation

Verified unpaid expiry → archive original visit → new order/key/QR, identical
designs/copies/amount → remain in Sandbox checkout with renewal notice. PAID
continues original identity; unknown/offline/404/cached timer cannot replace it.
One automatic renewal for a live visit, later expiry requires BUAT QR BARU.
Restart/privacy retirement never automatically creates another customer's order.
After restart conclusively unused expiry may return to idle via the existing
boot path. No closing-page or reselection step during live renewal.

Each replacement is a NEW order and therefore gets its OWN new recovery ticket;
the original save-ticket gate is retained and clearly labels renewed tickets.
An old ticket cannot authorize the replacement order. Do not share/reissue raw
credentials or add an alias spanning unrelated financial identities. Current
selection is reused; fresh camera/storage/template readiness is required before
replacement creation and price changes need a new quote/consent.

Reuse original KioskCheckout/FastAPI/client, bounded provider reconciliation,
Sandbox worker, exact-key archive, atomic journals, ready gate and native views.
No new merchant endpoint, production mode, operator shortcut or print/Drive opt-in.
Fresh raw provider expire + checked true + verification_pending false must match
EXPIRED, service NONE, no grant/fulfillment/issue/photo/allocation/fence/release/
capture intent. Archive BEFORE final journal retirement or new key. Archive/save
failure holds original visit; delayed settlement is retained on old order and
never silently credited to its successor. Backend active-order guards remain.

Renewal verification authority is runtime-only, short-lived and bound to original
key/privacy generation; no GUI boolean or cached journal grants authority.
New key, counter and predecessor metadata are durable before new provider I/O.
Lost replies reuse that key; no second provider charge. Busy/stale widgets and
minimize retire automatic renewal authority. No repeated automatic POST loop.

## Delivery plan / acceptance

1. Core, disabled by default: verified unpaid-expiry archive, runtime proof,
   same-cart replacement and durable identity/counter; focused original HTTP/
   SQLite/lease fixtures; safe micro-commit + push + remote verify and checkpoint.
2. Enable only dedicated native Sandbox, mount auto/manual renewal, original
   prepayment readiness, new-ticket explanation, private/operator/restart states;
   native 800x1280/452x900, focused tests, staged push, one final full/current CI.
3. Final exact source/evidence/checklist handoff, docs-only push. Actual Windows
   merchant simulator/OS clipboard/device result remains owner manual acceptance.

Test fresh vs cached/raw mismatch expiry, grants/photo/release holds, late paid,
off-thread/pause retirement, archive/save failures, one automatic then manual,
preflight rejection, new ticket binding, same selection/amount, lost POST reply
and restart reuse, no mutation of originals/rights/media. Register portable
cases Windows/Linux and strict Linux method receipts. Preserve optional skips.

Reviewed current AGENTS, protocol/index/README, checkpoint/handover, AR roadmap,
operations/provider/reconciliation/customer/native contracts, UX-05/BUG-024,
BUG-025 limits and original backend/controller/adapter/widget/readiness/tests.
No old-directory access or dirty legacy checkout changes. Whole UX-07 NOT_RUN,
matrix59/0/9/1 and AR-13/external/commercial gates unchanged; OPS queued.
Rollback inverse source only, preserving all archives, orders, claims, grants,
financial/media/lease/audit records. No deployment/merge/default/new branch.

Status at contract: IN_PROGRESS / new checks NOT_RUN.

## Core checkpoint

Ten new portable cases; focused original HTTP/controller/privacy/cancel group
**41 PASS**, zero failure/error/skip,2.626s. Private report work/bug026-core.txt.
New core is disabled by default, native mounting/full/current CI are next.
Initial wrapper integration/fixture expectation issue corrected; original backend
late-settlement REVIEW_REQUIRED retained. No actual merchant/device result claimed.

## Owner refinement — 30-second untouched renewal button

Owner requests return to ads if BUAT QR BARU is not pressed for30seconds.
Timer applies only to current original conclusively archived unpaid expiry,
not provider verification, PAID/OWED, active photo work or busy replacement I/O.
It is bound to that checkout key, not reset by a page rebuild/status observation.
Pressing renewal starts a new attempt; stale callbacks retain original guards.
No provider/financial/media operation is performed by the navigation timeout.

## Native checkpoint

Dedicated Sandbox enabled, same-checkout auto/manual renewal + new-ticket gate
and30s untouched-button return implemented. Final15 focused PASS/8.229s. Eleven
portable and four native methods registered with strict Linux receipts; six
nonpayable native views reviewed. Initial regression failures/corrections retained
in [evidence](evidence/bug026-verification.json). Full/current CI now required.
