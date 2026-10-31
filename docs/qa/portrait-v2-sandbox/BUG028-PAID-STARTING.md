# BUG-028 — PAID remains on preparing photo permission

Owner screenshot: official Sandbox simulator shows PAID, native app shows
MENYIAPKAN IZIN FOTO / COBA PEMERIKSAAN LAGI. Owner confirms printer is not
connected. Actual laptop SHA, duration and backend error are unknown. This is
an owner-reported failure under investigation; do not infer provider settlement
verification, a lost payment or a proven printer cause from the screenshot.

Expected current BUG-027 scope: unavailable receipt printer is UNCERTAIN and
must not prevent original paid photo admission. No payment, receipt or photo
may be repeated to escape the screen. Keep original order, grant, allocation
operation, transaction, media, obligation and private customer proof intact.

Reviewed before changes: AGENTS/protocol/prompt, current checkpoint/handover,
BUG-027/AR-03 fulfillment and CAP01-05 allocation contracts, native photo/session/
backend/client/API implementation, exact-source prior full/CI and configured
printer/native/capture/recovery fixtures. Existing tests cover process-restart
allocation recovery; a transient live allocation reply failure also needs a
bounded retry of the SAME operation and one local handoff, without a reset.

First diagnostic fixtures: actual configured Sandbox photo worker with injected
unavailable sender, plus before-accept/after-commit allocation reply loss followed
by the existing check action. These tests distinguish printer absence from a
live STARTING recovery gap. The owner's exact cause stays unconfirmed until
reproduced with corresponding evidence. No actual merchant/printer/customer
journals are accessed, no archive inspection, new branch/production/Drive/OPS/
refund/deletion/deployment. Runtime fix only after a failing regression; preserve
fresh provider verification, original proof/privacy epochs and all existing
no-overwrite/no-replay/paid rights. Focused checks and micro-push, final full and
matching CI after the final functional change, then accurate owner instructions.

## 31 October — BUG-028 live STARTING allocation recovery focused-verified

Owner reports simulator PAID/native MENYIAPKAN IZIN FOTO and confirms no printer.
Owner follow-up returns to ticket page after wait/retry; actual laptop SHA,
duration and original API error unknown. Do not
claim the exact owner cause proven. Base/remote1df9d80576788aa5f0843c666e4d412b450fb6bf.
Configured missing-printer worker reaches camera at both sizes in a direct test;
receipt becomes UNCERTAIN, one attempted send, one original payment. A separate
before-accept/after-commit allocation reply fault reproduces a permanent live
STARTING hold. Initial2-method run: printer case PASS, allocation method two
subtest FAIL/zero ERROR,5.617s. Old process-restart tests did not cover live retry.

Controller check now retries the exact durable original allocation operation
only while transaction is missing; backend still freshly verifies settlement.
Late/retired proof rejects. Existing check result performs the original bound
local handoff once; original local-ready/STARTED confirmation still gates camera.
No new financial identity, allocation counter, capture, receipt or print replay.
Five portable methods cover original-operation replay, same committed ID,
outage/refund, missing operation and privacy-lock/late reply; two native methods
exercise actual configured missing-printer and both fault windows at both sizes.
**57 focused PASS/0 FAIL/ERROR/SKIP,28.677s**. Prior38 PASS/19.307s and56
PASS/30.268s preceded the live idle/pause correction. The held STARTING worker
also reproduced unwanted ticket lock at both sizes (one method/two subtest FAIL,
zero ERROR,2.863s). During the partial patch,57run/3FAIL/zeroERROR retained;
complete correction now passes without removing local-ready/private holds.
Original live STARTING ownership survives idle/pause before local worker ready;
UI keeps original consent, clears pixels, fences stale callbacks. It does not
unlock an old process or an admitted private photo session. Existing receipt
fixture now explicitly marks local-ready before asserting the private hold.
Five portable +three native methods registered, exact Linux receipt notices
required. Full/current CI pending; no full PASS yet for this source.
[Focused scope/receipt](evidence/bug028-focused-verification.json).

Next one applicable final full + current CI, native proof and accurate owner
retest instructions. Keep the actual current app/session private; no payment or
file reset to clear it. Restarted sessions still require original ticket: absent
printer means no saved paper proof; do not promise an update will unlock private
old photos. Operator release preserves rights; it is not a refund/fulfillment.
Whole UX07 NOT_RUN, matrix59/0/9/1, AR13 conditional; real owner/device/provider
acceptance pending. No production/Drive/OPS/deletion/public ingress/master/new
branch/default/deployment. Only private work/ and superseded docs stash local.
Source micro-commit is the safe checkpoint; exact SHA via Git log/remote.

Owner follow-up: after waiting/retry, app returns to SESI TERSIMPAN and asks for a
customer ticket; owner dislikes repeated ticket requirements. No printer means
there is no printed proof. Preserve live ownership through the original STARTING
handshake before local photo admission, including a delayed reply/idle/minimize.
This is not authority to unlock an old process, existing private photo session,
unknown local media or another visitor's allocation. Once locally admitted,
existing privacy/restart proof rules remain. Add a held-worker regression before
adjusting the narrow prephoto predicate; keep old financial/media rights intact.
