# BUG-026 — verified expired QR renewal in the existing Sandbox checkout

## 31 October — latest owner correction (supersedes earlier flow below)

Unpaid customers must see payment QR directly, without generating/rendering or
acknowledging a visitor ticket. Recovery ticket presentation starts only after
confirmed payment, before photo consent. Existing internal capability binding
at order creation remains an ownership safeguard, not a visitor ticket screen.
Fresh Midtrans EXPIRED + unpaid/no entitlement archives the original and
automatically replaces it with a new ID/QR, same designs/copies/amount, including
reopening the reported saved expired session. Show exactly: “QR sebelumnya
kedaluwarsa. Silakan gunakan QR terbaru.” No renewal-button or ticket detour.
Three expirations total per visit: QR1 expires → QR2; QR2 expires → QR3;
QR3 expires → advertising, no QR4. Persist the replacement counter across restart;
core rejects renewals beyond this cap, including manual/stale requests.
Fresh verification, archival-before-creation, unknown/paid/photo/owed/privacy/
readiness guards still apply. The previous manual-button/30-second requirement
is superseded by this explicit automatic three-expiration instruction.
Regression tests must cover real configured factory startup, provider reservation,
three expirations, deferred paid ticket, lost reply/restart and claim buttons.

## 31 October — owner retest FAIL at ecc6733 / startup follow-up

Owner confirms exact laptop SHA ecc6733 and again sees SESI TERSIMPAN with all
four claim actions disabled. Prior full/CI PASS remain historical synthetic
evidence; owner case is NOT resolved. No more owner diagnostic commands required.
Reproduce actual configured factory + persisted EXPIRED/NONE checkout, including
persisted provider reservation/unchecked observation, and native page rebuilt
while reconciliation is busy. Existing live-renewal fixtures did not cover that
combination. Do not delete/edit owner journal, payment or media to unblock it.

Bounded fix: known unused expired checkout awaits provider verification on a
neutral payment-check page (no old-ticket input and no replacement before fresh
proof). Verified saved expiry offers BUAT QR BARU directly in the same checkout,
not the ticket page or an automatic replacement charge. Existing30s untouched
button return applies. Rebuilt private-claim buttons must reflect actual worker
completion without losing typed proof or re-enabling a held release/paid action.
Retain all existing expiry, grant/photo/OWED/review, privacy and provider guards.
Add failing regressions first, focused checks, staged push, final full/current CI.
Real laptop outcome remains pending until owner confirms; do not infer it from CI.

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

## CI installation correction

Core run41203929916 and GUI run41205080811 Linux failed during dependency setup,
not tests: ffpyplayer4.5.4 selected an sdist requiring absent SDL_version.h.
CI-only pin4.5.3 matches installed local runtime; Linux/Windows CPython3.12 wheel
availability validated. Application requirements/source unchanged. Original full
continues at5201c10; matching corrected workflow CI required. Failures retained.

## Final source verification / owner manual next

Functional5201c10 full1251/1247 PASS/4optional SKIP, zero failure/error,491.880s.
Corrected CI source0d92831 (only dependency pin/docs differ) CI41205340183 all
three SUCCESS: Windows194 PASS, Linux recovery493 PASS, native121/120PASS/1skip.
Eleven portable cases individually PASS Windows/Linux and four native cases
PASS Linux; six native views checked. [Exact results/history](evidence/bug026-verification.json).

FIXED IN SOURCE / REGRESSION VERIFIED; owner laptop/provider NOT_RUN.
[Manual renewal/new-ticket/30s instructions](UX07-LAPTOP-CHECK.md#jika-qr-pembayaran-kedaluwarsa-saat-l02).
Current source supports automatic first renewal only for a live acknowledged
visit; each replacement requires its own saved ticket. No old-ticket alias or
customer photo bypass. Pending/review/paid/unknown and physical obligations retain
original guards. No production/commercial certification or transport activation.
