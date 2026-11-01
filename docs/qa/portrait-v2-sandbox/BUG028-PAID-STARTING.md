# BUG-028 — PAID remains on preparing photo permission

## 1 November 2026 — Existing PAID->camera regression boundary

BUG-028 concerns **historical paid-first Sandbox** whose original customer may reach camera after confirmed PAID and original STARTED. This checkpoint remains relevant for **legacy existing PAID orders** and must be regression-tested, not removed when adding new orders on `feature/post-preview-qris-checkout`. New post-preview orders instead finish photo capture/retake/preview before QRIS; verified PAID advances to original Recovery Ticket and exact paid print/Drive fulfillment without generating a *new* photo allocation or asking the live original owner to re-scan CCP. Late PAID without a live owner is PAID_UNCLAIMED/OWED with secure claim and free-booth proof. Do not treat earlier BUG-028 source/device PASS as proof of the new route; all 84 PP cases NOT_RUN. [Owner master](POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [implementation handover](POST-PREVIEW-QRIS-CODEX-HANDOVER.md).


## 31 October — BUG-028 source/full/current CI verified; owner retest next

Functional source **52d69fd57b69201e3af1b016a90690945e8e1e1a**; latest tested
micro-push **8fc3675877177a9c216dae132e9950ceae9c51a4**, remote HEAD verified.
Application/runner unchanged after52d69fd; later24ead05/8fc3675 fix test isolation
and reuse the existing recovery scanner. Complete functional full **1288run/
1284PASS/0FAIL/0ERROR/4optionalSKIP,481.717s**, exit0. Final focused **58PASS/
0FAIL/ERROR/SKIP,34.029s**. Current matching CI **41223201896 all three SUCCESS**:
Windows214/214; Linux recovery530/530; native121run/120PASS/1optional palm SKIP.
Five STARTING portable methods Windows/Linux, three new native methods Linux,
13 receipt methods Windows/Linux and seven paid-camera methods Linux all PASS.
Includes128 full native receipt bitmaps through original primary/alternate
scanner with exact payload and actual worker/backend proof for photo restoration.

Original live STARTING retains ownership through delayed setup/idle/pause before
local-ready and retries only the original allocation operation. Original backend
settlement and local-ready/STARTED still gate camera. Missing-printer fixture
enters camera, one charge/receipt attempt, zero capture; no payment/print replay.
Four original App.run synthetic screens reviewed at800×1280/452×900, source52;
original receipt QR matched in memory, never published. Guide/form9groups/44steps
match;10 loopback Chromium cases PASS, actual offline-file/laptop use NOT_RUN.
Earlier CI41221421520 optional-encoder failure and41222182150 primary-only
fixture failure, red controls and abandoned QR experiments are preserved; no
experimental renderer change published. [Exact evidence and source hashes](evidence/bug028-final-verification.json).

Owner actual laptop SHA/duration/API cause unknown; owner follow-up PENDING.
Update prevents this demonstrated live-preparation detour; it does not unlock an
already locked/private/restarted/released session. Original ticket/operator safe
handling remains; no journal deletion, replacement payment, false refund or
fulfillment. Operator release retains PAID/OWED rights. WholeUX07 NOT_RUN;
69-ID matrix59PASS/0FAIL/9BLOCKED/1NOT_RUN unchanged;AR13conditional. Actual
Windows/paper/provider/privacy/Ubuntu/Drive/retention/operating/release evidence
is next. No production/Drive/OPS/deployment/master/default/new branch actions.
Do not redo verified AR source. Final documentation-only checkpoint records this
published test/source SHA; its own containing commit is available in Git log.
Latest remote documentation **b27f95f9928326c24703e9c40ef2897fa90a55c4**
(1 November owner requirement) was read and preserved before this docs checkpoint:
[30-second on-screen ticket fallback](RECOVERY-TICKET-ONSCREEN-FALLBACK.md) is **DOCUMENTATION ONLY /
NOT_IMPLEMENTED / NOT_TESTED**. It is a separate queued extension, not current
BUG-028 behavior or acceptance. Its explicit scope does not authorize runtime/
test/deployment changes; retain current validated direct-camera path. Final
docs-only commit was rebased onto that remote document without overwriting it;
no force-push or published-source rewrite. Source/CI8fc3675 remains applicable.

Only private work/ and superseded docs stash remain outside GitHub.

## 31 October — BUG-028 scanner-fixture correction focused-verified

Functional **52d69fd57b69201e3af1b016a90690945e8e1e1a**, previous test-only
**24ead05a45cd6cda70ad3630d4a62ca85395b7e5** (pushed/remote verified).
Current increment changes tests/workflow only; original receipt renderer/scanner,
all application and runner files remain identical to52d69fd. Its complete full
1288run/1284PASS/4optionalSKIP, zero fail/error,481.717s and native4 scenes apply.
Current focused **58 PASS/0 FAIL/ERROR/SKIP,34.029s**, including128 full native
receipts (64 public synthetic payloads ×384/576), original primary/alternate
scanner exact-text assertion and real paid-photo restore worker/backend proof.

Previous CI41222182150: Windows/navigation SUCCESS; Linux529run/1FAIL/0ERROR,
164.661s, old fixture decoded with primary only. All five portable and three
new STARTING native methods PASS. Existing scanner already has one bounded
Aruco fallback; reuse it rather than mock decoded tickets or change production.
Primary-only corpus13run/4subtestFAIL/0ERROR,6.926s; experimental Q-level focused
58run/9subtestFAIL/0ERROR,33.978s not a fix, restored original M renderer. No
runtime experiment published. Earlier optional-encoder CI failure also retained.
[Exact focused fixture receipt](evidence/bug028-scanner-fixture-verification.json).

Original live slow STARTING survives idle/pause before local-ready, retries same
operation and reaches camera with unavailable printer; no new payment/capture/
receipt. Old/private/restarted proof rules remain; owner laptop SHA/cause unknown,
actual retest PENDING. Native/full source52 unchanged, actual paper/webcam not
verified. Next matching-source CI, final evidence/guide checkpoint and docs-only
micro-push; no redundant full rerun for these tests-only corrections. WholeUX07
NOT_RUN;matrix59/0/9/1;AR13conditional. No production/Drive/OPS/device/customer
operations. Other final docs/artifacts remain local pending matching CI; work/
and superseded docs stash private. Containing micro-commit SHA via Git log;
next final checkpoint pins it exactly and verifies remote HEAD.

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

## 31 October — BUG-028 minimum-CI encoder fixture correction

Functional source **52d69fd57b69201e3af1b016a90690945e8e1e1a** full regression
completed: **1288 run /1284 PASS /0 FAIL /0 ERROR /4 optional SKIP,481.717s**,
process exit0. Optional native video and three palm-model opt-ins are not PASS.
CI41221421520: Windows and navigation SUCCESS; Linux recovery529 methods failed
8 subcases because optional python-escpos was absent before the injected sender.
Controlled encoder-absence reproduction:3 methods/8 subtest FAIL/0 ERROR,11.959s.
Test-only correction injects synthetic ESC/POS bytes, as existing receipt fixtures
do, preserving every original one-send/one-charge/no-capture assertion. Application,
workflow and test runner unchanged from52d69fd. Controlled corrected3 PASS/15.357s;
corrected focused **57 PASS/0 FAIL/ERROR/SKIP,27.197s**. This fixture correction
micro-commit requires matching current CI; no current CI success is claimed yet.
Native original App.run captures at800×1280 and452×900 show live slow preparation
surviving120s simulated idle +pause/resume and reaching camera without a ticket,
with one unavailable sender attempt and no capture. Four synthetic screenshots
visually reviewed; final artifact publication pending. No receipt QR/token saved.

Next: verify matching-source CI, publish native/final receipts and update owner
laptop instructions, then docs-only micro-push/remote verification. Actual owner
retest remains pending; exact owner laptop SHA/cause unknown. Already locked old
sessions retain original proof rules; no reset/new payment to unlock. WholeUX07
NOT_RUN; matrix59PASS/0FAIL/9BLOCKED/1NOT_RUN; AR13conditional. No production,
Drive, real printer/provider/customer data, OPS, deployment or branch changes.
Only private work/ and superseded local docs stash remain outside GitHub.

## Current CI follow-up — receipt decoder fixture under investigation

Run41222182150 corrected all eight new STARTING subcases; Linux recovery529
methods instead failed one existing printed-ticket restore assertion (OpenCV
returned empty text for the randomized synthetic receipt). Exact failed random
payload was never logged/saved. No assertion waived and no current CI PASS.
Before another source change, distinguish receipt-renderer behavior from random
fixture/OpenCV sensitivity; preserve original QR equality/recovery assertions.
Actual physical-paper/scanner acceptance remains NOT_RUN.

## Bounded receipt-readability follow-up contract

The unchanged native renderer with error correction M fails exact OpenCV decode
for two of64 deterministic public synthetic payloads (indexes24/59), both384/576
native widths, including QR-only controls. Local OpenCV5.0.0; CI4.14.0.94 had one
empty randomized decode; its payload was not saved, so exact identity unconfirmed.
Changing QR error correction to Q passes all128 QR-only controls; H also fails
some patterns, so it is not a blanket fix. Before runtime change add a deterministic
64-payload/two-width full-receipt regression and reproduce failure. Then use Q in
the original encoder, retaining native integer dots, quiet zone, minimum module
size, exact original capability, no saved token and original send/recovery rules.
Do not replace actual QR decode/equality with a mocked ticket or remove assertions.
Focused checks and immediate micro-push, then a new final functional full/current
CI and fresh original native proof. This is bounded synthetic readability evidence,
not universal decoder, paper/printer or webcam acceptance.

### Follow-up finding — reuse existing scanner, renderer unchanged

Q-only experimental full-receipt focused run58/9subtest FAIL/0ERROR,33.978s;
not a correction and never published. Border6/8 experiments also did not solve
all full-receipt primary detections. The original Sandbox scan_claim ALREADY
performs one bounded QRCodeDetectorAruco fallback before original backend proof,
with existing false-negative/foreign/missing-alternate guards. The failing native
fixture bypassed that working scanner and called only the primary decoder.
Restore original renderer unchanged; test the real scanner worker and real
backend claim in the paid-photo restoration case. Corpus now uses both original
installed detectors on unchanged full native receipts, with only downstream
claim intercepted to assert exact original synthetic payload. No decoder mock,
resizing, QR alteration or financial/privacy assertion removed. Functional52
full/native evidence stays applicable; corrected focused/current CI required.
Physical printer/webcam acceptance remains separate.
