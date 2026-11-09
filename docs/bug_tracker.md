## BUG-048 — native remote ticket countdown waited for backend ACK (9 November 2026)

FIXED / SOFTWARE VERIFICATION; customer profile still unmounted. Genuine card
visibility now starts the original30s privacy clock immediately; slow backend
ACK cannot extend the screen or reopen it. Regression first FAIL;12 related
native PASS. [Exact failure/fix/evidence](qa/portrait-v2-sandbox/BUG048-REMOTE-TICKET-VISIBILITY-CLOCK.md).
Corrected source3ea1d8c verified:80 local native PASS; CI42591856392 all three
SUCCESS (680 Windows/680 Ubuntu/80 native), completed logs inspected. Commercial
account/device/full-profile acceptance remains open.

## BUG-047 — Ubuntu original vault key rejected after keyring daemon restart (9 November 2026)

**Severity:** S1 protected recovery availability. **Status:** SOURCE FIXED /
local isolated Secret Service and final 638 backend/74 native VERIFIED;
matching CI42563214405 all three SUCCESS, completed logs inspected.
The same persisted original key gains provider-owned xdg:schema metadata on
GNOME Keyring reload. Whole-dictionary equality rejected it although all four
application identity fields matched. Actual restart returned VAULT_UNAVAILABLE;
a one-method regression ERRORed before correction. Required identity fields
now match exactly while provider metadata is ignored, using the service's
subset-search contract. Original ciphertext restores after daemon restart,
unchanged hash, no new key/proof; wrong scope and key guards remain. 24 credential
PASS, zero failures/errors/skips. No owner mini-PC/real-money incident is claimed.
[Evidence and limitations](qa/portrait-v2-sandbox/PP03-UBUNTU-VAULT-2026-11-09.md).

# Meong Photobooth — Bug register

## BUG-046 — Paid results never automatically returned to Advertising (8 November 2026)

**Severity:** S2 session navigation/privacy exposure. **Status:** SOURCE FIXED /
local software VERIFIED: 598 backend + 70 native PASS, zero failures/errors/
skips, actual timer 30.089s. Published `fc8853b` has the identical tested Git tree
as local `1be8d0b`. CI 42427430090 IN_PROGRESS; owner retest NOT_RUN.
Owner reports 11 scoped laptop checklist PASS, PILOT-03 NOT_RUN, and no return
from the paid result screen; laptop SHA unknown. Owner explicitly requires an
automatic return after 30 seconds with no new button. One result deadline now
reuses privacy retirement/protected Ads, survives redraws/status refreshes and
does not reset on interaction. RESULT_TIMEOUT preserves PAID/OWED and exact
worker/ACK admission guards; late delivery replies cannot reopen private pixels.
Three focused methods PASS (both portrait sizes, deadline boundary, blocked
print/UNCERTAIN and original paid API); no actual device acceptance inferred.
[Scope, evidence and retest](qa/portrait-v2-sandbox/BUG046-RESULT-AUTO-RETURN.md).

## BUG-045 — Uncertain Recovery Ticket receipt did not quarantine paid strip output (5 November 2026)

**Severity:** S1 physical-output integrity. **Status:** SOURCE FIXED / focused software VERIFIED; final new-source full regression/CI pending. A synthetic receipt transport timeout produced durable UNCERTAIN and the mandatory ticket screen was dismissed. The direct original paid-strip dispatcher accepted a new strip because its receipt guard only denied PREPARED/SENDING. The paid-delivery snapshot also omitted receipt uncertainty from its review flag, leaving the print action apparently available. One meaningful regression initially FAIL (expected DraftHeld was not raised). No physical paper incident is asserted.

The dispatcher now refuses UNCERTAIN original receipts; delivery inspection propagates the same uncertainty to its existing review flag. Mandatory ticket/NEXT behavior is unchanged, no receipt reprint is introduced, and known non-sending receipt failure remains distinct. Regression asserts zero photo transport calls, original strip PREPARED and PAID/OWED retained. Receipt/paid-output/restoration scope: 54 PASS, zero failure/error/skip, 16.646s. [Campaign](qa/portrait-v2-sandbox/PP07-SIMULATION-CLOSURE-R4-2026-11-05.md).

## BUG-044 — Original checkout stuck after a pre-create readiness/response hold (5 November 2026)

**Severity:** S1 synthetic pilot checkout availability. **Status:** SOURCE FIXED /
focused native VERIFIED; final new-source regression/CI pending.
When initial begin returned no observation (including a readiness HOLD before
POST), the page offered only status reconciliation. Reconcile cannot start an
unsent checkout, so restored readiness left the customer stuck. Two connected
Kivy regressions initially FAIL because no retry action exists. The page now
offers an explicit original-owner retry through the existing backend begin
operation, which sends only PREPARED and reconciles SENT/UNKNOWN without another
POST. Automatic status polling remains read-only. Complete widget scope:
17 PASS, zero failures/errors/skips; same frozen group/media, one charge, exact
old attempt after lost HTTP reply, and no QR4. This is distinct from the earlier
positive-fixture setup error; the initial full-run cause remains unproven.
[Reproduction and continuation](qa/portrait-v2-sandbox/PP07-EXECUTION-CAMPAIGN-R1-2026-11-05.md).

## BUG-043 — Stencil-clipped private proof recorded as genuinely offered (5 November 2026)

**Severity:** S1 proof-opportunity/checkout integrity. **Status:** SOURCE FIXED /
focused software VERIFIED; complete source-matched regression/CI pending.
Two connected native regressions initially FAIL: clipped CCP sets offered_at,
and clipped paid ticket sets VISIBLE despite unusable QR/full code. The shared
card now checks stencil ancestors before its original visibility callback.
Three new methods plus affected native/payment/ticket/classifier scope:
68 PASS, zero failures/errors/skips. Original PAID/OWED remains; printer ACK
alone is not screen evidence. No physical fault, live charge or refund claimed.
[Exact reproduction, evidence and next step](qa/portrait-v2-sandbox/PP07-EXECUTION-CAMPAIGN-R1-2026-11-05.md).

## BUG-042 — Proof-loss label masked independent merchant/financial failure evidence (5 November 2026)

**Severity:** S1 nonbinding policy classification. **Status:** SOURCE FIXED /
AUTOMATED_VERIFIED at acbac15: full all-opt-in 1,744 PASS; CI 41906929920
all 3 SUCCESS (546 Windows/546 Ubuntu/62 native), zero failures/errors/skips.
Refund API remains disabled; no actual funds changed.

The classifier accepted PROOF_LOST_ONLY alongside an independently irrecoverable
service or verified excess settlement and returned NO_AUTO_REFUND_PROOF_LOST.
That contradicts RF-D07: proof loss cannot hide independent merchant failure.
Both combinations now require review, with no candidates or refund authority;
sole proof loss retains the approved no-automatic-refund rule. Two new tests
initially FAIL; corrected refund/payment/claim scope 64 PASS, no failures/errors/
skips.
[Reproduction, exact evidence and remaining campaign](qa/portrait-v2-sandbox/PP07-END-TO-END-SIMULATION-2026-11-05.md).

## BUG-041 — DEMO game win advertised a different post-preview gallery price (5 November 2026)

**Severity:** S1 customer quote consistency. **Status:** SOURCE FIXED / focused
AUTOMATED_VERIFIED at acbac15: full all-opt-in 1,744 PASS; CI 41906929920
all 3 SUCCESS (546 Windows/546 Ubuntu/62 native), zero failures/errors/skips.
No actual charge or physical owner result.

An actual persisted DEMO win followed by two designs/2+1 copies showed Rp22,500
in the gallery, but final post-preview/server pricing was Rp25,000. Both
portrait sizes reproduce it. The private profile now declines DEMO-only gallery
discount eligibility through a small shared policy seam; legacy DEMO/MOCK
eligibility and backend promotion authority are preserved. New N27 runs the
complete game -> tutorial -> capture/retake -> preview -> paid ticket -> virtual
2+1 strip journey. N27 plus existing game-offer/followup checks: 17 PASS, zero
failures/errors/skips.
[Reproduction, evidence and remaining simulation phases](qa/portrait-v2-sandbox/PP07-END-TO-END-SIMULATION-2026-11-05.md).

## BUG-040 — Claim accepted proof invalidated during provider settlement checks (5 November 2026)

**Severity:** S0 protected-session authorization. **Status:** SOURCE FIXED /
AUTOMATED_VERIFIED at c20479d / CI 41901827925: 544 Windows, 544 Ubuntu,
61 native PASS; zero failures/errors/skips, 3/3 SUCCESS. Owner physical UAT NOT_RUN.

The original CCP or Recovery Ticket could expire or be revoked during the last
provider GET, yet its stale initial verdict still reacquired old occupancy.
Four connected tests originally FAIL. Shared current-proof verification now
runs in the same SQLite transaction as original lease acquisition, after every
provider call. The 81-case affected suite PASS with no failures/errors/skips;
original PAID/OWED, rate-limit behavior, B ownership and no-print/no-charge guards
remain. No actual merchant or persistent pilot restore is enabled.
[Reproduction, flow, evidence and next action](qa/portrait-v2-sandbox/PP07-CONTINUATION-2026-11-05.md).

> **4 November final automated evidence:** BUG-036–039 are source-fixed and
> verified in matching-source [CI 41826366906](https://github.com/pratikto/PhotoBooth/actions/runs/41826366906)
> at `0601354`: 533 Windows + 533 Ubuntu + 61 native PASS, all jobs SUCCESS,
> zero failures/errors/skips. Earlier per-entry pending notes retain their
> checkpoint scope. Physical owner closure remains NOT_RUN. Supervised payment
> simulation is ready for device testing; actual merchant/restart/refund and
> production gates remain separate in the current report.

## BUG-039 — Synthetic pilot reused one fake Drive folder across paid visitors (4 November 2026)

**Severity:** S1 supervised synthetic repeat-visit delivery failure. **Status:**
FIXTURE SOURCE FIXED; J21 complete 12-paid-visit regression and affected cases
18 PASS locally; native N26 all-12 preview PASS at both sizes; final CI pending.

The default synthetic `CheckoutFixture` returned the same folder identity for
every paid transaction. The real ownership guard correctly rejected visit B's
binding. The default owner pilot also uses this fixture. It now returns stable
transaction-specific fake folder identities after the historical first URL.
Actual Drive client and privacy/conflict guards remain unchanged.
J21 checks 72 original captures, 24 exact copy-aware batches, 12 separate folders,
charges, tickets, entitlements/ACKs and unchanged old JPEG hashes. This does not
prove real upload/paper or long-duration hardware soak.
[Full scope, before/after evidence and native preview coverage](qa/portrait-v2-sandbox/PP07-DEVICE-READINESS-2026-11-04.md).

## BUG-038 — Long-lived idle Drive worker blocked every automatic handoff (4 November 2026)

**Severity:** S1 live-Drive pilot admission failure. **Status:** SOURCE FIXED;
85 affected synchronization/Drive/isolation checks PASS locally; current-source
CI pending; actual Drive/device tests NOT_RUN.

Isolation equated a living daemon thread with an active Drive request, so the
normal always-running reserve/upload worker prevented any session ACK even
while idle. A nonblocking request-boundary fence now excludes worker cycles
through the original PREPARE/ACK ledger commit. Active requests still HOLD;
idle worker resumes unchanged without shutdown, lost queue or replacement.
Three real-thread/event regressions cover idle admission, a request racing
PREPARE→ACK, and fence cleanup after financial HOLD. Original paper/finance
guards, folder identity and no-replay remain in force.
[Detailed contract, sequence diagram and executed limits](qa/portrait-v2-sandbox/PP07-DEVICE-READINESS-2026-11-04.md).

## BUG-037 — Historical purchase blocked B's checkout after A's safe isolation ACK (4 November 2026)

**Severity:** S1 repeated-customer checkout failure. **Status:** SOURCE FIXED;
89 affected backend/integration checks and native A→B checkout PASS locally;
matching-source Windows/Linux/native CI pending; device UAT NOT_RUN.

The worker readiness adapter rejected any earlier PP finance row, even for a
closed/ISOLATED visit with a valid exact-generation ACK. B could capture photos
but could never create its own payment. Both original PAID/OWED and verified
cancelled-unpaid A reproduce the failure. Earlier N23 covered only B capture.

Readiness now requires all prior purchases to have exact current-generation
ACKs with complete nonfuture timestamps, no finance review/nonterminal attempt
and no uncertain original paper. The probe remains read-only; historical
PAID/OWED, original proof/media and legacy/current-worker guards are preserved.
Seven new backend cases include malformed/missing/stale ACK and conflict holds;
native N25 completes B through independent payment, preserving A's OWED.
[Full reproduction, contract mapping, flowchart and evidence](qa/portrait-v2-sandbox/PP07-DEVICE-READINESS-2026-11-04.md).

## BUG-036 — Recovery Ticket automatic timeout froze during slow receipt send (4 November 2026)

**Severity:** S1 private-proof visibility/lifecycle. **Status:** SOURCE FIXED;
focused local native regression PASS at 800×1280 and 452×900; matching-source CI
pending and physical owner acceptance NOT_RUN.

`PrivateCheckoutFixtureApp._poll_photos` returned on a busy printer worker before
updating the ticket countdown or checking zero. Manual NEXT still wiped the
code, but automatic 30-second expiry could wait for the slow receipt callback.
The fix advances visible-ticket UI/expiry before the worker-busy return while
keeping durable dismissal serialized after the same original receipt.
No repeat send, paper-success claim, charge or booth release is added.

New native test holds receipt I/O behind an event and injects the ticket clock;
before fix both sizes fail, after fix it and five related checks PASS. Original
receipt SENDING, one submission and PAID/OWED remain intact.
[Exact reproduction, source/environment limits and next checks](qa/portrait-v2-sandbox/PP07-DEVICE-READINESS-2026-11-04.md).

## BUG-035 — New customer inherited previous customer's tutorial/cart transient UI state after safe isolation (2 November 2026)

**Severity:** S1 privacy/visit lifecycle UX regression.  
**Status:** SOURCE FIXED [`15659c94`](https://github.com/pratikto/PhotoBooth/commit/15659c94d96fa1429811082ecd71258e9df18bd5); exact-source [CI #41409614158](https://github.com/pratikto/PhotoBooth/actions/runs/41409614158) **PENDING** until native logs confirm N23/N24. Owner physical check NOT_RUN.

**Root cause:** `PrivateCheckoutFixtureApp._pilot_prepare_new` correctly required previous customer A's safe isolation/ACK before allowing B, but after ACK only reset the temporary photo/ticket view; it did not reset `navigation.tutorial_seen`, `entry_source`, selected copy quantities or game state. Thus a new B visit could jump directly from advertising to A's `TEMPLATES` without B's own required tutorial and could inherit stale visible UI choices. Detected through N23 native Kivy multi-customer test (first failed as `NavigationError` when expected new B tutorial was skipped).

**Fix:** after **successful guarded** `ensure_new_visitor_ready()` only, use existing `_reset_visit()` and explicitly clear tutorial_seen/entry_source. This touches only customer UI state, never original A photo, ticket/proof, provider settlement, PAID/OWED or print/Drive liabilities. If isolation is not safe, reset does **not** occur and B remains blocked.

**New verification:** [N23/N24 native Kivy and P01/P02 OS-boundary test report](qa/portrait-v2-sandbox/PP07-BROAD-SIMULATION-MATRIX-2026-11-02.md). N23 requires fresh B tutorial/zero carried quantities after safe A receipt, then validates no A proof/paid media leak during B capture. N24 injects actual receipt printer TimeoutError to persist original `UNCERTAIN` and asserts B **cannot** be admitted from public Ads. Full physical test and original live merchant/provider release not performed.

## BUG-034 — Direct paid printer dispatcher bypassed purchase-wide uncertainty quarantine (2 November 2026)

**Severity:** S1, paid photo duplicate/overlapping paper risk.  
**Status:** source fix `92717d25` pushed; **new cross-component tests J09/J10 pending execution**, matching-source [CI #41407278546](https://github.com/pratikto/PhotoBooth/actions/runs/41407278546) initially pending. **Do not claim verified until job logs PASS.**

**Reproduction path (source audit):** if design A was `SENDING` or `UNCERTAIN`, kiosk GUI and `PrivateCheckoutService.paid_print_next` blocked printing design B. But a separate direct `OriginalPaidPrintDispatcher.send_once` call only checked **B's job state PREPARED**, with no query for earlier unsettled A. A second dispatcher instance/worker route could therefore send B while A's physical paper outcome remained unknown. This was a lower-layer enforcement gap, not proof an actual customer's paper was duplicated.

**Fix:** within the durable ledger transaction and before changing B state or initiating printer I/O, dispatcher checks *all* `pp_paid_strip_jobs` for the original purchase group and rejects when **any SENDING or UNCERTAIN** row remains. This preserves the original job, PAID/OWED obligation, exact copy count, and no-blind-replay policy, independent of UI/service caller. Normal A=`SUBMITTED` allows the following approved B submission, but no paper is thereby verified physically. No production payment, merchant refund or physical test operation.

**Evidence:** [20-case broad simulation matrix, J09/J10](qa/portrait-v2-sandbox/PP07-BROAD-SIMULATION-MATRIX-2026-11-02.md), new `test_post_preview_journey_matrix` source and exact CI run. Controlled live POS80 classifications, restarts with two actual worker processes, and technician escalation remain physical/unverified gates.

## BUG-033 — Uncertain original paid print permitted next design to dispatch (2 November 2026)

**Severity:** S1 / financial fulfillment and physical paper safety; one job may already have reached the printer.  
**Status:** SOURCE FIXED, **matching-source CI VERIFIED** (Windows 493/493, Ubuntu 493/493, native 53/53; [3/3 SUCCESS #41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221)); physical technician/printer resolution NOT_RUN.  
**Scope:** new synthetic/mock-only post-preview paid-output workflow. No legacy source, merchant provider or production deployment changed.

**Before:** `OriginalPaidPrintDispatcher` correctly persisted design A as `SENDING` then `UNCERTAIN` after a transport timeout and denied a replay of A. However, `PrivateCheckoutService.paid_print_next` and the GUI allowed a different `PREPARED` design B to dispatch while the first job's physical outcome remained unclassified. This was discovered by source review against PP-050/052/095 and owner-approved no-blind-paper rule.

**Fix:** independently enforce `needs_operator_review` in the service before selecting any later PREPARED design. Disable customer print-next in the paid-delivery native UI on any SENDING/UNCERTAIN original job. No auto-reprint, refund, PAID deletion or forced operator reset was introduced. Later recovery requires separately authorized human/device evidence; the original paid service remains `OWED`.

**New test:** `test_native_uncertain_design_print_quarantines_remaining_batches` simulates two designs, one synthetic PAID, one ticket, first print transport timeout, A=`UNCERTAIN`, B=`PREPARED`, disabled button, rejected direct backend call, unchanged send count on upload-status refresh, no physical-paper success claim. Matching-source CI: [workflow #41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221), code `c86a8e64` — **verified all jobs SUCCESS** at source `c86a8e64`; paper or hardware still NOT_RUN.

**Follow-up:** real POS80 timeout/jam, restart at SENDING, physical job classification, worker-lane concurrency and safe claim/admission are still separate tests.

## BUG-032 — Expired third QRIS offered an unusable QR4 continuation (2 November 2026)

**Severity:** S2 / customer-facing checkout logic and failed-action risk; backend financial boundary already enforced.  
**Status:** SOURCE FIXED, **matching-source CI VERIFIED** (Windows 493/493, Ubuntu 493/493, native 53/53; [3/3 SUCCESS #41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221)); real merchant expiry NOT_RUN.

**Before:** The underlying `PostPreviewPayments` safely enforced QR1→QR2→QR3 maximum, but the native `payment_hold` page offered `LANJUTKAN PESANAN ASLI` for any verified `EXPIRED_UNPAID`, including terminal QR3. Clicking the button could only produce a backend refusal; it could confuse a customer or operator.

**Fix:** offer continuation only while fewer than three durable original QR attempts exist. Once QR3 expires, display a truthful three-QR limit notice, without creating QR4, recapturing photos, cancelling an uncertain provider order or erasing original records. Original merchant/account settlement remains verified independently.

**New test:** `test_native_expiry_qr1_qr2_qr3_never_offers_qr4_or_recaptures` sends three distinct **synthetic** provider QR attempts through the native GUI, explicitly verifies each expiry and authorized continuation, asserts six original photos unchanged, one frozen group/quote and no fourth-action button or false PAID obligation. Matching-source CI: [workflow #41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221), source `c86a8e64` — **verified all jobs SUCCESS** at source `c86a8e64`; actual merchant expiry remains NOT_RUN.

**Follow-up:** real Midtrans Sandbox expiry, late webhook/settlement during QR2/3, actual customer presence and terminal unpaid-admission UX remain unverified.

**Full scenario specification:** [PP-07 adversarial GUI fault injection](qa/portrait-v2-sandbox/PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md). Automated subassertions do not promote the 112-case complete acceptance matrix or physical owner UAT to PASS.

## BUG-031 — Synthetic Drive QR could look like a real customer download link (2 November 2026)

**Severity: S3, supervised pilot clarity and false-positive acceptance risk.**  
**Status: SOURCE FIXED / MATCHING-SOURCE CI VERIFIED (493 Windows + 493 Ubuntu + 51 native, 3/3 SUCCESS); actual owner-screen acceptance NOT_RUN.**

**Observed by source audit:** the mock paid-delivery page rendered the synthetic fixture folder URL as a QR under a general "delivery" label. That QR is intentionally **not downloadable**, but the original native label did not clearly say so; a physical tester could confuse expected fixture behavior with a broken Google Drive link.

**Fix:** `photobooth/kiosk_v2/post_preview_checkout_app.py` now uses an explicit boolean synthetic-Drive display mode, and `tools/run_post_preview_checkout_pilot.py` sets it based on the existing double-consent real Drive opt-in. The virtual QR is visibly labeled `QR DEMO • BUKAN LINK DOWNLOAD`; the real test-Drive route is `DRIVE TEST • BAYAR SIMULASI`. The mock checkout remains incapable of making a real Midtrans payment. Existing native multi-template QA asserts the demo label. No cloud operation, real print or charge was executed to make this fix.

**Evidence:** [Source-pinned CI report and exclusions](qa/portrait-v2-sandbox/PP07-AUTOMATED-SIMULATION-2026-11-02.md). Actual phone scan/public Drive share and paper QR still require owner's physical pilot.

## BUG-030 — Pilot preflight could falsely report READY with missing checkout dependencies or conflicting legacy modes (2 November 2026)

**Severity: S2, test-admission correctness; not a demonstrated payment safety regression.**  
**Status: SOURCE FIXED / MATCHING-SOURCE CI VERIFIED (493 Windows + 493 Ubuntu + 51 native, 3/3 SUCCESS, zero failures/errors/skips); physical Windows installation still NOT_RUN.**

**Observed by source review:** `tools/check_post_preview_pilot.py` checked only five Python imports and ignored ambient `PHOTOBOOTH_V2_CHECKOUT_SANDBOX/MOCK/PRINT/DRIVE` flags. The real launcher refuses conflicting flags and requires additional QR/backend/audio dependencies, so earlier "READY" could still fail before GUI test.

**Fix:** full module availability checks for Kivy, Pillow, numpy, requests, cryptography, FastAPI, httpx, Pydantic, qrcode, cv2 and ffpyplayer; fail-closed, redacted flag-name reporting when legacy payment/delivery profiles remain enabled. Existing branch/file/Python checks are retained. Three new unit tests verify a genuine positive READY fixture, missing FastAPI and an incompatible legacy mode. No merchant key or secrets are echoed.

**Evidence:** [Exact CI 41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509) and [QA ledger](qa/portrait-v2-sandbox/PP07-AUTOMATED-SIMULATION-2026-11-02.md). A passing static preflight is never hardware/payment/Drive acceptance.

## BUG-029 — animated Meong header restarts during Sandbox QRIS polling (1 November 2026)

**Severity: S2 (visual / customer experience; no demonstrated payment integrity issue).**
**Status: OPEN — OWNER REPORTED, SOURCE-LEVEL HYPOTHESIS; NOT FIXED / NOT DEVICE-VERIFIED.**
Priority: queue after the currently authorized AR-00–AR-13 payment/privacy/recovery
work and higher-impact defects; do not silently change code on this report.

**Observed:** Owner screenshot of the native Windows Portrait GUI v2 on
`QRIS SANDBOX / MENUNGGU SIMULATOR` shows animated Meong at the left of the
header. Owner reports that it cannot fly fully from one edge of the header
to the other and back. Exact laptop SHA, Kivy display scale, time-series video
and repeat count were not provided. A static screenshot alone cannot prove
the entire motion path; treat the owner's motion report as owner evidence.

**Expected:** Meong travels smoothly left -> right -> left across the
available header space, including its rainbow, animated limbs/film and
contact-triggered wordmark spin, without jumping back to the initial position
when payment polling updates the QRIS status or a harmless button refresh
occurs. Payment/cancellation/receipt status must still update safely.

**Read-only source trace (branch `feature/portrait-kiosk-v2-next`, observed
GitHub HEAD `a1358c6`):**
- `photobooth/kiosk_v2/branding.py`:
  `MeongLogo._start_flight` animates `flight` between 0 and 1, turns
  direction at each completion, and uses roughly `dp(65)`/second.
  `photobooth/kiosk_v2/brand_flight.py` derives horizontal travel from the
  header width. The intended cycle is implemented in the animation itself.
- `photobooth/kiosk_v2/sandbox_views.py::_poll_sandbox` schedules repeated
  `check` requests (typically around two seconds in the QRIS view) and
  calls `_show()` for their successful results.
- `photobooth/kiosk_v2/app.py::_show` calls `_retire_gestures()`, disposes
  existing `MeongLogo` widgets, clears the page, and rebuilds the native
  view, constructing a new logo/animation with initial `flight=0`.
- Therefore **repeated full-page rebuilds are a strong suspected reason**
  that the animation restarts before completing one traversal. This is a
  source-level explanation, **not yet a measured Windows/root-cause proof**.

**Reproduction / required evidence:** Run the dedicated Sandbox GUI on Windows,
reach QRIS Sandbox PENDING without paying, watch continuously across at least
two intended full header traversals while normal status polling continues.
Record screen/video with payment QR and private identifiers redacted; note the
local `git rev-parse HEAD`, viewport/resolution, display scale, observed reset
frequency and actual time of the first interruption. Confirm whether Meong
restarts at each `Page rebuild begin` / `Page ready` log event. Also check
manual CEK STATUS and payment phase transition. Do not use real money or
alter payment/visit journals to reproduce this visual bug.

**Proposed future fix (not authorized by this report):** Keep the decorative
header widget alive across same-page payment status observations, or persist
and restore phase/direction through a narrowly scoped nonvisual update.
Prefer updating QR/status/actions without retiring the whole view. Preserve
existing QRIS reconciliation, quote, privacy, operator hold entry, animated
rainbow/film and source animation; do **not** simply accelerate Meong to
mask resets, and do not borrow/correct mini-game movement unnecessarily.
Regression should cover native 800x1280, 452x900 and Windows compact size,
polling over >=2 full passes, manual check, resize, transition and
pause/minimize, with zero payment/QR/secret leakage or button regressions.

**Status of work:** Documentation/triage only. Code, tests, animation and
printer/payment behavior are unchanged. No focused regression, CI or physical
acceptance result is claimed. This bug is distinct from historical BUG-016
(Meong Fly **gameplay** player anchor after resize).


## BUG-028 — PAID preparation / premature customer-ticket hold

S1 provisional — FIXED IN SOURCE52d69fd / LOCAL REGRESSION VERIFIED; current
matching CI8fc3675 all three SUCCESS; owner retest PENDING, not CLOSED.
Original live STARTING
operation retries same identity; idle/pause before local-ready retains proof.
Full1288run/1284PASS/4optionalSKIP, zero fail/error,481.717s. Corrected focused58
PASS including128 native receipt images through original scanner; four native
scenes reviewed at both portrait sizes. Both previous Linux CI fixture failures
retained/corrected; original runtime
unchanged. Windows214PASS/Linux530PASS/native121run,120PASS/1optional palm SKIP.
Actual owner laptop SHA and exact original cause remain unknown. Printer absent
alone does not block original camera in configured fixture. Old/private/restart
proof rules remain; no payment or journal reset.
[Contract](qa/portrait-v2-sandbox/BUG028-PAID-STARTING.md) ·
[Exact verification](qa/portrait-v2-sandbox/evidence/bug028-final-verification.json).

## BUG-027 — paid ticket detour / direct camera and approved print

S2 — FIXED IN SOURCE / REGRESSION VERIFIED at4c74ece, test-only crash correction
e05a358. Full1280/1276 PASS/4 optional SKIP, zero failure/error; matching
CI 41215811123 all three SUCCESS. Sandbox receipt once after verified PAID, direct
camera, original deliberate countdown/review and approved strip once. Original
privacy/restart/unknown-send/OWED guards retained; no production/Drive. Actual
owner Windows/printer/paper/provider retest NOT_RUN; not formally CLOSED.
[Exact verification and preserved failure](qa/portrait-v2-sandbox/evidence/bug027-final-verification.json).

## BUG-026 — expired unpaid QR trapped in customer recovery (31 October)

S2 — OWNER RETEST FAIL at ecc6733; follow-up SOURCE REGRESSION VERIFIED at118b763,
actual owner/device/provider follow-up pending. No unpaid ticket; first/second
verified unpaid expiry auto-renew same cart, third returns ads. Saved-expired
startup/provider reservation and rebuilt grey claim controls corrected. Full1259/
1255PASS/4optionalSKIP, zero fail/error; matching CI41208622748 all3 SUCCESS.
All12 portable methods Windows/Linux and11 native renewal/control methods Linux
PASS. Six native screenshots +offline guide/export verified. Preserve previous
synthetic1251/CI41205340183 history; it did not resolve the reported owner case.
[Current contract/evidence](qa/portrait-v2-sandbox/BUG026-QR-RENEWAL.md).


## 30 October — BUG-025 — legacy Sandbox session without customer ticket

S1 — FIXED IN SOURCE / REGRESSION VERIFIED at7069bf0; owner retest NOT_RUN. Owner reports PAID/STARTED/OWED and disabled isolation; no saved ticket. Exact laptop SHA/capability unknown. Explicit PIN-authenticated legacy-only Sandbox archive now preserves rights/media via existing fence/isolation/ACK/archive. No customer proof bypass or ticket replacement. Focused backend41 and native28 plus final pair2 PASS. Final source7069bf0 full1236/1232 PASS/4optional SKIP, zero failure/error; CI41001339113 all three SUCCESS. Windows fixture failure/cleanup correction retained in evidence.
[Contract/evidence](qa/portrait-v2-sandbox/BUG025-LEGACY-NO-TICKET.md).


30 October l2 final: ca7827c full1229/1225PASS/4optionalSKIP, zero failure/error; CI40985975287 all three SUCCESS. Six new portable methods Windows/Linux and two native methods Linux at both portrait sizes PASS. No application defect found. Offline l2 fixture checks verified; owner laptop checklist remains NOT_RUN. Whole UX-07 NOT_RUN; matrix59/0/9/1 unchanged; external/operating/commercial host gates remain.

30 October UX-07.l2a: three new original privacy/controller fixture methods PASS locally; source abb086c CI40977963717 all three jobs SUCCESS, portable method Windows/Linux and both native methods Linux PASS. No application defect reproduced. Whole UX-07 NOT_RUN, matrix59/0/9/1 unchanged; combined purchased-job release/drain lifecycle remains next. See UX07-PURCHASED-PRINT-INTEGRATION.md and its l2a receipt.

## BUG-024 — confirmed cancellation remains held after restart (29 October)

**S2 — FIXED IN SOURCE / REGRESSION VERIFIED at `347e502b0f50d231ec05c0cbcf768f87d2002454`.**
52 focused PASS; full 1159 run/1155 PASS/4 optional SKIP, zero failure/
error; CI 40856740113 all three jobs SUCCESS, six UX-05 methods PASS on Windows/
Linux. UX-05 synthetic PASS; actual device acceptance NOT_RUN, no formal closure
or production release. Original six-case baseline at be6f96e: four PASS/two FAIL.
Fresh provider cancellation updated backend after lost reply/restart, but local
phase stayed CANCELLING. No duplicate charge/payment loss/private media leak.
Only explicit unpaid cancel with checked terminal proof now archives exact visit
before final local commit; write failure/cached proof/paid rights remain held.
No provider/schema/version change. Preserve all archives/financial rights on rollback.
[Evidence](qa/portrait-v2-sandbox/evidence/ux05-final-verification.json).

## 29 October — BUG-023 fixed in source / regression verified

Source `3822bb0`, 73 focused PASS; full 1153/1149/4, zero failure/error.
CI 40852458558 all three jobs SUCCESS; four new conflict methods PASS on
Windows/Linux. Recovery-only replay/cross-order denials durably redacted;
SQL failure holds, successful replay idempotent. UX-13 synthetic PASS; matrix
**57 PASS / 0 FAIL / 9 BLOCKED / 3 NOT_RUN**, overall audit IN_PROGRESS.
Actual device acceptance NOT_RUN; no production release. Next UX-05 contract/
source audit, then remaining UX-07/11/external gates.
[Exact evidence/limits](qa/portrait-v2-sandbox/evidence/bug023-conflict-http-verification.json).

## 29 October — BUG-023.d conflict audit focused-verified

Recovery-only 404/409 denials audited with static NOT_OWNED/ACTION_CONFLICT;
SQL failure holds with generic 503, exact successful replay remains idempotent.
73 focused PASS, full/current CI pending. BUG-023 OPEN/UX-13 FAIL pending final
verification; matrix 56/1/9/3 unchanged.
[Contract/results/next](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## 29 October — BUG-023.c PIN audit verified

Source `e6aba5a`, 69 focused PASS; full 1149/1145/4, zero failure/error.
CI 40850382603 all three jobs SUCCESS, journal and HTTP tests on Windows/Linux.
Wrong-PIN and operator 429 now durably audited on all three Sandbox routes;
audit failure denies with generic 503. Replay/cross-order denial audit remains
pending: BUG-023 OPEN/UX-13 FAIL, matrix 56/1/9/3.
[Exact evidence/next step](qa/portrait-v2-sandbox/evidence/bug023-pin-http-verification.json).

## 29 October — BUG-023.c PIN denials integrated

All three Sandbox endpoints audit wrong PIN/429, generic 503 on audit failure.
69 focused PASS; full/current CI pending. Windows now registers journal and
HTTP tests. Replay/cross-order audit pending; BUG-023 OPEN/UX-13 FAIL.
[Contract/evidence/next](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## 29 October — BUG-023.a foundation verified

Source `ab6fbbb`, 45 focused PASS; full 1145/1068/77, followed by 75 GUI/audio
opt-in run/73 PASS/two SKIP (three model and one video skip remain overall). CI 40843692911 all three jobs
SUCCESS; new journal methods PASS on Linux, Windows registration next.
Dormant only: HTTP not integrated, BUG-023 OPEN/UX-13 FAIL, matrix 56/1/9/3.
[Evidence/next step](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## 29 October — BUG-023.a denial journal foundation

Dormant additive bounded redacted journal, no HTTP integration yet. Five new
tests; **45 focused PASS**, zero failure/error/skip. Full/CI pending. BUG-023
OPEN/UX-13 FAIL; matrix 56/1/9/3 unchanged.
[Contract/results/next step](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## BUG-023 — operator wrong-PIN denial has no durable audit (29 October)

**S2 — FIXED IN SOURCE / REGRESSION VERIFIED at `3822bb041d90da9330457d2e4404668be278eee9`.**
73 focused PASS; full 1153 run/1149 PASS/4 optional SKIP, zero
failure/error. CI 40852458558 all three jobs SUCCESS; UX-13 synthetic PASS.
Wrong-PIN/429 and authenticated conflict/cross-order denials now persist bounded
redacted metadata on all recovery routes; SQL failure remains held, successful
same-action replay stays idempotent. Actual device acceptance NOT_RUN; not a
formal CLOSED/release decision. No production/admin activation.
[Current verification](qa/portrait-v2-sandbox/evidence/bug023-conflict-http-verification.json).

Original finding at 4642841: eight wrong PINs returned 401 and ninth 429,
same-PIN app recreation reset the in-memory budget and no durable denial was
written. Per-launch PIN rotation/authentication remained intact; no bypass
observed. [Original failure evidence](qa/portrait-v2-sandbox/evidence/ar-audit-pin-denials.json)
is retained; process-local operator budget and separate persistent customer
ticket budget remain intentional. Financial/action ledgers are never pruned.

## BUG-022 — missing committed PNG accepted during recovery (29 October)

**S1 recovery integrity — FIXED IN SOURCE / REGRESSION VERIFIED at 4642841.** Full 1100 run / 1097 PASS / 3 optional SKIP, zero failure/error; matching CI 40790865010 all three jobs SUCCESS. Actual device acceptance remains NOT_RUN. Audit of
8ebcd12 reproduces metadata inspection returning result for an absent COMMITTED
PNG. Restore then installs transaction state before snapshot raises
FileNotFoundError. No financial mutation, duplicate charge or privacy disclosure
was observed. Corrected validation checks committed output even when absent,
raising the existing held-media error before installing state. No automatic
regeneration, print or record/media changes. Synthetic regression asserts manifest,
original JPEGs and backend OWED rights remain intact. 14-case pre-fix run:
2 FAIL/1 ERROR in new regression; corrected 61 focused PASS, zero failures/errors/
skips. [Review/provenance](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md#increment-3--confirmed-missing-output-reconstruction-defect-bug-022).
Actual device media-loss acceptance NOT_RUN; not blanket CLOSED.


## 29 October — AR-12 source validation findings

The Linux content-priority fixture has a proven host-monotonic-clock dependency;
9592649 sets an explicit due clock with all assertions intact. Its historical
runner clock was not logged, so the exact historical trigger stays unknown.
Fresh CI then exposed recovery scan failure. A local 100-ticket probe reproduces
ten primary OpenCV misses; existing alternate detector recovers those ten.
f72fdbc adds one optional alternate decode then original backend customer proof;
foreign/undecodable QR remains denied. Final regression/CI evidence is in the
[AR-12 record](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical phone/camera and production recognition are NOT_RUN; no general device
certification or blanket P0 closure. BUG-009 remains OPEN pending real retention
acceptance. No previously owner-accepted path was speculatively rewritten.

## BUG-021 — QR image disappears while remaining on Sandbox page (28 October)

S2: owner reports image-only disappearance, without timing/status or tested HEAD.
Offline reproduction proves pending polling replaces a verified image action
with a derived URL; a failed reload then clears the image. Exact laptop cause
is unconfirmed. IN SOURCE: retain/revalidate the stored URL when actions are
absent, preserve explicit-action checks and legitimate QR removal. Source
`4237d3f`: 182 focused PASS; full 933 run / 930 PASS / 3 optional palm SKIP;
CI 40614355442 all three jobs SUCCESS. Owner retest and exact device cause remain
pending; [runbook](qa/portrait-v2-sandbox/QR-POLLING.md).
Already overwritten URLs are not reconstructed; journals are preserved. Not CLOSED.

## BUG-020 — Sandbox dashboard Server Key rejected locally (28 October)

S2: dedicated merchant trial cannot start with the reported `Mid-server-` key
from a visibly Sandbox dashboard. Reproduced in launcher validation before any
provider call; exact installed SHA and complete credential remain unknown.
IN SOURCE: both complete Server Key formats accepted, with Sandbox-only transport
and credential/payment isolation preserved. 136 focused PASS; final regression
and CI in the [runbook](qa/portrait-v2-sandbox/KEY-FORMAT.md): source `6a271de`
has 901 run / 898 PASS / 3 optional palm-assets SKIP, zero failures/errors;
matching CI 40572395949 all three jobs SUCCESS. Actual Windows
hidden-input/authentication/simulator retest pending; not CLOSED.

## BUG-019 — incoming carousel strip absent during held drag (27 October)

S2 visual degradation. Owner screenshots show a blank incoming side before
pointer release. Five-slot/three-texture mismatch reproduced; source correction
retains five cached neighbours. Native held/reverse/wrap checks PASS; exact owner
HEAD and Windows/Ubuntu acceptance remain unknown. IN SOURCE / device retest
pending, not CLOSED. [Correction and evidence](qa/portrait-v2-carousel-hold/README.md).


## 27 October — delivery logging recursion recurrence

Owner reports >10 minutes and supplies RecursionError timing; new queued work
has no worker_start in the extract. Old-folder BIND_FOLDER_CONFLICT is confirmed
for one transaction. Real-Kivy console-active reproduction exposes root/stderr
logging recursion missed by earlier console-disabled QA. Timing now uses the
session file directly, contains sink failures/re-entry, and v2 defaults to MIXED
logging with native diagnostics retained. 54 targeted tests PASS; final checks
are recorded in the [correction runbook](qa/drive-delivery-performance/LOGGING.md).
Code.gs unchanged; no redeploy, reset or known-folder replacement is required.

## 27 October — delivery timing follow-up

Owner reports faster uploads and supplies runtime timings: successful session
122.719s to QR, including 70.782s overlapping old bind attempts. Three old
transactions repeatedly reach a successful bind response then local ValueError;
exact cause unproven. Bounded recovery/backoff and typed diagnosis are published at 8578825;
actual old-folder conflict repair remains unverified and is not automated.
[New source/evidence/retest](qa/drive-delivery-performance/RETRY.md). Original
five-minute incident and BUG-009 cloud deletion remain separate open evidence.

## Delivery latency / result input follow-up — 27 October 2026

Owner reports >5 minutes before large QR, then verified Drive with disabled
Finish/processing footer; printing intentionally disabled. No duration log or
exact failing-source/device evidence is available. Source/controlled tests confirm
maintenance can delay a customer and snapshot busy-state can persist in rebuilt
result controls. Bounded source fixes are in 58dc76f/2e140c1; actual five-minute
root cause is **unproven**, device retest pending. Related FEAT-004/FEAT-022 and
BUG-009 delivery work; privacy deletion BUG-009 stays OPEN. Prior private-link
incident below remains separate evidence. [Tests/runbook](qa/drive-delivery-performance/README.md).

## Drive photo delivery recurrence — OPEN (26 October 2026)

Owner reports private printed QR, empty folder and GUI waiting on upload. Meong account confirms the reported folder is empty and lacks anyone-reader access. Source correction prepared; installed backend version/logs and successful live delivery remain unverified. See docs/qa/drive-photo-layout/README.md.


**26 October BUG-009 continuation:** owner resumed this repair and says setup/
redeployment has not been confirmed. Sources **130aae1 / 887ba39** repair real
CLOCK activation/setup and add safe existing-config diagnosis. **807 full Python
PASS/zero skips, 19 Code.gs VM PASS**; two source defects reproduced before fix.
The installed project's activation and actual eligible synthetic deletion are
still unverified: **OPEN — awaiting cloud evidence**, not CLOSED or still deferred.
That retention-only source increment did not include FEAT-004 sync. The owner
now links the [foldering/global-cache target](photobooth-storage-layout.md) to
FEAT-004 ads + BUG-009. The coordinated source is now implemented at 53e7b4c
(824 full Python PASS/zero skips, 24 Code.gs VM PASS, matching three-job CI
SUCCESS); actual deletion evidence stays separate. The [combined pending
checklist](qa/portrait-v2-pending-acceptance/README.md) records actual gates. [Current guide/proof](qa/bug-009-retention/README.md).

**Current GUI v2 context — 25 October 2026:** latest print/Drive source
`266b2c8` has 800 full local PASS/zero skips, matching three-job CI SUCCESS and
133 verified PNGs; actual paper/phone/cloud acceptance pending. Earlier operator
`ea394e8` has 780 full local PASS/zero skips; matching-source CI succeeds with
one optional native model-assets skip covered locally. `9433010`/688 tests is
the earlier P5 baseline. Preflight `0dc6555` ready is not physical/provider PASS.
BUG-012/013/014/015/016/017 retain owner-reported monitoring, with missing tested
HEAD/device fields kept unknown. BUG-009 remains OPEN; v1 BUG-001/007 stay separate.
Read-only Device Health/report is now in source, not the next unimplemented feature.
[Current status](FEATURE_STATUS.md) · [test ledger](test_checklist.md).

The stable IDs and dated evidence below are preserved. Historical v1 reports
and prior CI counts apply to their original source, not current v2 acceptance.

**Severity:** S0 = unsafe/payment integrity/data loss/kiosk unusable; S1 = core customer session cannot be completed; S2 = material degradation or workaround required; S3 = cosmetic or nonblocking. Higher execution priority may be assigned to customer-flow failures even when individual severities remain provisional.

## CI-only QA issue — separate from operational bugs

**QA-QR-001 (CI-only, P1 stabilization, now MONITORING):** Random DEMO QR attempt UUIDs changed module patterns on each synthetic Kivy screenshot render. GitHub's one-scale OpenCV decoder intermittently failed despite no observed laptop issue. Test-harness-only commit [`e46812b8`](https://github.com/pratikto/PhotoBooth/commit/e46812b8c9f66c548bccebb1e9fc45e3c89afeef) uses deterministic synthetic IDs and bounded screenshot-pixel decoder scales, preserving exact payload assertions and negative QR tests. **Kiosk CI 3/3 SUCCESS** at `e46812b8`: [run 39178452927](https://github.com/pratikto/PhotoBooth/actions/runs/39178452927) with **233 PASS / 2 SKIP and 87 screenshot PASS** each. [Detailed QA record](qa/KIOSK-GUI-REGRESSION-2026-10-18.md). This is **not BUG-003** (QR printing) and not a production failure; monitor future regression runs.

## Current bug queue — operational defects first

BUG-001/002/003/004/005/006/007/008/010/011 rows retain their v1/shared-service
context. A v1 Settings/QR-slip or lab control is not automatically a v2 screen.
The v2-specific monitoring rows and BUG-009 boundary below remain current.

Active defects and deferred retests appear first. Monitoring items and owner-reported passes remain in the register for traceability and possible formal closure, **not as active fix tasks**.

| ID | Latest report / observed impact | Severity | Source vs device status | Next action / evidence |
| --- | --- | --- | --- | --- |
| **BUG-018** | Initially the app reportedly hung after rapid combined Device Health clicks despite raw 8/8. Later targeted R01–R04 retest: **4/4 checked, zero unchecked, no issue notes** on 25 October. | S1 historical/provisional | **OWNER-REPORTED PASS / MONITORING**. Source correction `ebb53fd` has 785 full PASS/0 skips and matching-source three-job CI SUCCESS; the owner's tested HEAD/device fields remain unknown. | Preserve initial failure and later [owner retest](qa/portrait-v2-health-clicks/README.md). No new patch or repeated twenty-cycle gate; investigate only recurrence. Exact-source verification/formal closure and external P5 gates remain separate. |
| **BUG-017** | Owner reports lag specifically switching advertising video→video; video→image and image→video are reported okay. Entered in the lag field; notes box empty. | S2 provisional (duration/frame impact unknown) | **OWNER-REPORTED PASS / MONITORING (2026-10-24).** | Final typography retest V01/V02 checked and owner confirmed “udah clear semua”. Tested HEAD/device metadata and measured latency unknown; no decoder patch or root cause claimed. Preserve prior report. [Acceptance](qa/portrait-v2-sandbox/owner-acceptance.json). |
| **BUG-016** | Owner screenshots show Meong too far right after resize; native landscape reproduction puts its body at 80.12% width. | S2 | **OWNER-REPORTED PASS / MONITORING (unknown HEAD); source fix 848a52d.** | Center the complete original world; preserve speed, wave spacing, sprite/collision/film geometry. 20 focused native PASS; final follow-up 540 full PASS/zero skips and 45 synthetic game captures verified. [Evidence](qa/portrait-v2-player-anchor/README.md). |
| **BUG-015** | Owner reports fast mini-game and wave spacing shrinking after responsive layout. Source reproduces piecewise displayed speed (up to 2.437× near speed at 800×900). | S2 | **OWNER-REPORTED PASS / MONITORING (unknown HEAD); source fix 144bd60.** | Replace nonlinear layout projection with uniform world translation; original speed/spawn constants unchanged. Test actual rendered travel and wave spacing, not only static images. [Evidence](qa/portrait-v2-motion-correction/README.md). |
| **BUG-013** | Historical v2 preview lag while v1 was smooth and first-use page buttons needed extra taps. After the source corrections, owner submits all sixteen focused checks and twenty cycles with no issue notes. | S2 historical | **OWNER-REPORTED PASS / MONITORING (2026-10-23); EXACT-SOURCE ACCEPTANCE UNVERIFIED.** | Preview without touch/countdown, first-use buttons and twenty-cycle/restart checks are explicitly checked. `0d08f07`/`ef0fcb0` remain verified source checkpoints (353 prior full PASS); tested HEAD/device fields are blank, so do not assign the owner result to these SHAs or formally close/release. No new patch while working. [Acceptance and audit](qa/portrait-v2-preview-redraw/README.md). |
| **BUG-014** | Optional open-palm was absent before correction. Owner checks I01–I06 in the earlier forty-item report and B04 in the latest sixteen-item report as working. | S2 historical | **OWNER-REPORTED PASS AT UNKNOWN HEAD / MONITORING; EXACT-SOURCE ACCEPTANCE UNVERIFIED.** | Existing hold/release policy shares the v2 SIAP countdown. Latest twenty-cycle report has no issue notes; no new palm patch or repeat-test requirement is inferred. Preserve blank HEAD/device metadata and monitor regression. [Latest acceptance](qa/portrait-v2-preview-redraw/README.md). |
| **BUG-012** | Portrait GUI v2 previously exited returning to advertising (original V4: 33/35 checked, five cycles, unknown HEAD). After the correction/diagnostic retest instructions the owner says “sudah oke”. | **S1 historical/provisional** | **OWNER-REPORTED PASS / MONITORING (2026-10-23)**; not formally CLOSED. Exact post-update HEAD/cycle count and original native exit cause remain unverified. | Monitor without another speculative patch. Later owner P3/game reports include twenty cycles; preserve them at unknown HEAD without requesting another old gate. Collect diagnostic log/exit code if crash recurs; new Sandbox P5 cycles are separate. [Confirmation and evidence](qa/portrait-v2-return-ad-crash/README.md). |
| **BUG-011** | FEAT-001 previously printed **fewer/different physical sheets than the selected copy quantity**, while DEMO pricing was correct, on the owner's Windows photobooth. After the documented printer fixes, the owner first said **"sip udah bener"** and subsequently explicitly confirmed **"bug 11 udah aku test dan lolos"**: the selected copy quantity now matches the physical printer output according to the owner's hands-on test. The original requested/actual count and precise retest SHA/driver were not provided. | **S1 historical/provisional** (core print-fulfillment impact before patch) | **OWNER TESTED PASS — MONITORING (2026-10-18); NOT formally CLOSED/RELEASED.** In-source fix: the Windows RAW path now uses `EndDocPrinter` before one `ClosePrinter` ([`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93)); `copies=N` is sent as one RAW document containing N identical ESC/POS image+cut streams ([`4608fcc9`](https://github.com/pratikto/PhotoBooth/commit/4608fcc9ec96c8eabeb01ddbd64059830af2bf62), [`e6d2f684`](https://github.com/pratikto/PhotoBooth/commit/e6d2f6840d4b5838e719f904bcc3b8443291193a)). **Targeted GitHub CI [39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707): 15/15 PASS** (11 quote/session/manifest + 4 mock payload/spool). **Owner's explicit on-device TESTED PASS is separately recorded**; no full Kiosk GUI CI PASS or production release implied. | **No active fix needed; owner tested successfully on the Windows booth. Monitor regression without modifying stable printing code.** If the discrepancy returns, record requested/physical sheets, tested local SHA, transport and Windows spool queue; avoid automatically retrying ambiguous partial sends. For formal closure, log per-case 1/2/3 copies and mixed-template physical evidence, full applicable regression results and owner closure decision. See [comprehensive FEAT-001/BUG-011 acceptance record](qa/FEAT-001-BUG-011-acceptance.md). |
| **BUG-009** | **Drive retention registration/activation failure:** 30-day cloud deletion is not yet verified. Original Windows setup/redeploy warnings preserved. | S1 (provisional; cloud privacy/retention risk) | **OPEN — SOURCE REPAIRED / CLOUD EVIDENCE PENDING, owner resumed 2026-10-26.** Existing v1 cleanup is reused. Stale enabled-flag acknowledgement and setup accepting a non-clock trigger reproduced and corrected at 130aae1; safe read-only status/diagnostic delivered at 887ba39. Owner says setup/deployment has not been confirmed. | Verify installed version, owning-account hourly trigger and scoped synthetic cloud deletion after setup/deployment. No live Google configuration/access in the cloud workspace. Retain v2 upload holds, original deadlines and separate photo/ad folders. Source tests/status alone do not close the bug. Coordinate the owner-linked FEAT-004 foldering/global-cache and new retention paths, with independent sync/deletion evidence; this integration is now implemented at 53e7b4c, while real-account acceptance remains pending. [Current repair/evidence](qa/bug-009-retention/README.md). |
| **BUG-001** | Music is still inaudible in tutorial/layout, despite `SoundSDL2 state=play gain=0.59`; button and shutter effects ARE audible in the same GUI | S2 | **PATCHED IN SOURCE — owner audio retest required**; 2026-10-18 code now reacquires music playback after ad fade and on explicit audition. Actual audible output unverified | On Windows pull updated GUI, start from idle ad -> tutorial -> layout, listen for continuous BGM without entering Settings; test music mute/re-enable and check output with `Uji Musik`. Preserve ad mute and SFX; record SHA, sound/mixer and device result |
| **BUG-007** | Owner now confirms all three `Uji` buttons receive taps: Music made only the generic click, Button made click, Camera made shutter. GUI reports accepted callbacks | S2 | **OWNER REPORTED PASS for tap handling; PATCHED IN SOURCE for sample isolation; physical retest pending** | Check `Uji Musik` audibly restarts music without a click, `Uji Tombol` one button cue, and `Uji Efek Kamera` one shutter cue. The playback-request status is not speaker confirmation |
| **BUG-008** | Settings/config popup **previously** opened slowly or seemed to hang. On 2026-10-18, the owner reports Settings is **responsive again** on their local Windows application, without an identified intervention or reliable explanation. | S2 (historical/provisional) | **MONITORING — OWNER REPORTED PASS (2026-10-18); not CLOSED.** No new Settings fix or instrumented reproduction; root cause, triggering conditions and reason for recovery are **unknown**. Removed from active repair queue. | **Do not change working Settings code** just to address this historical symptom. Watch for recurrence; if reproduced, capture branch SHA, screen path (gear/main Settings vs Audio/Printer), click-to-display delay, video/background workload and relevant logs. Investigate only with separate approval; formal closure awaits recorded repeatable owner acceptance evidence. |
| **BUG-004** | Thermal photo-strip previously printed blurry / low quality; the owner now says the result is **OK** after the approved Floyd profile was added to the GUI. | S2 (historical impact) | **OWNER REPORTED PASS (2026-10-18) — removed from active fix queue.** Approved Floyd tuning is in `photobooth/printer.py` ([commit `06370660`](https://github.com/pratikto/PhotoBooth/commit/06370660e024baf070145c0fc8796621b1cae7d6)); improved quality is the owner's latest Windows feedback, not an independently captured comparative paper test. **Not formally VERIFIED/CLOSED.** | For formal closure, record tested commit/config, physical paper photograph or comparison, actual print width and owner acceptance evidence; retain regression tests and `PHOTOBOOTH_PHOTO_TUNING=legacy` rollback if needed. |
| **BUG-010** | Three-column dithering GUI formerly clipped lower sliders and the print/save controls; owner now says Windows GUI scrolling is **OK**. | S2 (historical impact) | **OWNER REPORTED PASS (2026-10-18) — removed from active fix queue.** Scrollable parameter columns and visible actions are patched in source ([commit `f3d836d`](https://github.com/pratikto/PhotoBooth/commit/f3d836d40f599e80ed0a844a9974bdd1b548f598)). Detailed screen-size/scroll evidence and local tested SHA have not been supplied; **not formally VERIFIED/CLOSED**. | For formal closure, document minimum/window-maximized layout, wheel/scrollbar access to all sliders including Threshold, Print Test/Save PNG visibility, tested SHA and owner acceptance; regression after GUI layout changes. |
| **BUG-002** | Video advertisements on both idle and payment now play according to owner | S2 | **OWNER REPORTED PASS — removed from active fixes**, formal closure needs version/evidence | Regression-check actual frames on both screens after audio change; payment stays muted |
| **BUG-003** | Owner confirms payment-page QR slip now physically prints | S2 | **OWNER REPORTED PASS — removed from active fixes**, QR scan and formal closure pending | Verify paper QR scans the intended DEMO payload, including quiet zone; no claim of live payment |
| **BUG-005** | Owner confirms ad → tutorial → layout navigation is satisfactory | S2 (provisional) | **OWNER REPORTED PASS — no active repair** | Keep manual/face paths in later end-to-end regression |
| **BUG-006** | Owner confirms opening advertisement sizing/display is satisfactory | S3 | **OWNER REPORTED PASS — no active repair** | Recheck responsive layout on future visual changes |

## Current execution context

Monitor reported-working paths and prioritize reproducible failures. Read-only
health/report source work is completed; actual operator/P5/merchant acceptance
is separate. BUG-009 remains unresolved. Refer to the [current backlog](next_step.md)
for follow-up; the old failed CI and FEAT-008 candidate ranking below are historical.

<details>
<summary>Historical v1 reports and execution ranking — 18 October 2026</summary>

These statements retain their original date/source. Later source/CI and owner
reports above supersede old active-fix rankings and failed-CI gates.

**Execution ranking (reassessed 2026-10-18 after the owner's successful print retest):** **BUG-011 leaves the active repair queue** and becomes **MONITORING — OWNER TESTED PASS**; the requested-copy/paper discrepancy is reported resolved after printer-source fixes, but formal closure/release remains subject to per-case device evidence and full GUI regression. **BUG-009 stays OPEN / provisional S1** for unresolved 30-day Google Drive photo privacy retention, deferred by owner to FEAT-004; this risk is not cancelled by the print success. BUG-001/007 audio remain deferred; BUG-008 Settings MONITORING; BUG-004/010 and BUG-002/003/005/006 owner-reported passes. [Kiosk GUI CI 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) on `f2f52e33` **FAILED** (full unittest step); evaluate independently before release. The next normal feature candidate remains FEAT-008 device health, subject to explicit approval and quality gates.

## Latest owner feedback and CI distinction — 2026-10-18 (documentation only)

- **Latest full Kiosk GUI quality gate (2026-10-18):** Owner-approved QA-only iteration has **VERIFIED CI PASS at source/test SHA `f129dd9e`**: [Actions 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476), **230 unit-test PASS + 2 skipped, 0 failures/errors, 87 synthetic GUI render PASS**. Historical CI FAIL lines below are **dated pre-repair history, not present current-app failures**. Scope was existing test expectations, runner and workflow—not production app code or Windows device acceptance. Root cause and committed repairs are documented [here](qa/KIOSK-GUI-REGRESSION-2026-10-18.md). This does **not** close BUG-009 or deferred audio or certify release.
- **BUG-011 initial failure → explicit successful user test (2026-10-18):** Pricing was correct while paper count was wrong; missing `EndDocPrinter` and separate spool jobs were corrected. After initially reporting **"sip udah bener"**, owner explicitly stated **"bug 11 udah aku test dan lolos"**. This is affirmative **hands-on OWNER TESTED PASS**, not merely an inference that the UI looks normal. Mark **MONITORING**, not formally CLOSED/RELEASED; local SHA, per-case count log and printer configuration were not provided. Targeted 15/15 mock CI PASS remains a distinct type of evidence. Full details: [FEAT-001/BUG-011 QA](qa/FEAT-001-BUG-011-acceptance.md).
- **BUG-009 owner scheduling decision (2026-10-18):** defer corrective action and coordinate it with future FEAT-004 per-machine Google Drive advertising synchronization. A shared `Code.gs` review/deployment is planned; **retention setup may only require enabling/redeploying existing functionality**, not a retention source-code patch. Both workflows need independent acceptance; no actual backend change, new code, deployment, test, or deletion is authorized by this documentation request. The unresolved 30-day-photo-expiry/privacy risk stays visible.
- **BUG-008 new owner update (2026-10-18):** Settings now opens/responds smoothly in the local application; the owner does not know why the earlier slowdown/hang disappeared. Classify **MONITORING — OWNER REPORTED PASS**, not VERIFIED/CLOSED or fixed-in-source. No evidence of a Settings code change, captured click-timing regression, or proven connection to Drive-retention traffic. Do not patch Settings while it is working; capture evidence only if symptoms return.
- The owner explicitly replied **"udah oke"** to BUG-004 thermal photo image quality and BUG-010 scrolling/access to dithering settings. Record both as **OWNER REPORTED PASS**, without claiming a new test command was run here or that exact tested SHA/screen measurements/physical paper comparisons were captured. Their prior failed states are retained as historical reports.
- The owner also reports the **application/regression runs successfully on local Windows**. Exact local command(s), complete test counts/output, local checkout SHA and coverage were not supplied; this is **OWNER-REPORTED LOCAL WORKS**, **not a verified full unittest suite pass**.
- At the GitHub branch baseline [`8bd5b58`](https://github.com/pratikto/PhotoBooth/commit/8bd5b58cc789fcc63b43e08e7eb9fc1c48dbe3f7), the [Dither tuning lab regression](https://github.com/pratikto/PhotoBooth/actions/runs/39120913800) completed **PASS**, while the [Kiosk GUI regression](https://github.com/pratikto/PhotoBooth/actions/runs/39120913854) completed **FAIL** in its automated test stage. GUI syntax and synthetic rendering stages succeeded; the failing test identity was not established from available logs. Local operational success does not silently override the GitHub workflow status.
- No new Windows hardware test, CI rerun, application-code modification, deployment, merge or release was performed to make this documentation update. A separate owner-approved scope is required for repairs or other document reconciliation.

## Known reproduction context (not independent verification)

- Environment in earlier reports: Windows, Python 3.12, Kivy 2.3.1, POS80ENG/POS80 Printer USB queue. Confirm active device name and persisted `data/printer_settings.json` at next test. Some earlier Windows logs referenced `/dev/usb/lp0` before printer settings were configured.
- Earlier sound probe `python tools/check_audio_output.py` was audible while normal `python main.py` was not. This narrows investigation to app lifecycle/routing, not proof of exact root cause.
- Earlier photo-print job physically yielded a Meong layout and looked blurry; this report is **historical**, superseded by the owner's 2026-10-18 quality-is-OK feedback after Floyd tuning. Owner separately confirmed QR-slip paper print works. Preserve older failures as history, not current status.
- **New evidence 2026-10-18, owner-shared Windows `python main.py` captured terminal log (redacted here):** Kivy 2.3.1 / Python 3.12.10, repeated `Drive retention registration failed` warnings for multiple transaction manifests and repeated Google Apps Script HTTP calls. Also shows `Meong audio test tapped: music/button/shutter` and `Music playback restarted at gain 0.59`. Log lacks timestamped Settings click/render spans and any Python traceback establishing the exact UI stall; a PowerShell `NativeCommandError` wrapper around stderr startup logs is not itself evidence of an app exception. One MP4 image-loader error appears, but the owner reports video ads work, so do not mislabel BUG-002 reopened without confirmed playback regression. No credentials or response URLs should be copied to this public repo.
- Relevant code reviewed read-only: `photobooth/ui_kivy.py::show_settings_menu/show_audio_settings/show_printer_settings`; `drive_sync.py::DriveSyncWorker` runs periodic network work on a background thread; `retention.py::register_drive_retention` logs registration errors and preserves manifest error state; `drive_storage.py::AppsScriptDriveClient.register_retention` requires retention backend acknowledgment. None proves BUG-008 is directly caused by BUG-009.
- Historical QA reported native sound/video test passes using fixtures and mock devices, plus a local 172-test run with failures caused in part by local merge artifacts. Do **not** transfer these results to current device acceptance. See [FEATURE_STATUS.md](FEATURE_STATUS.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and [docs/qa](qa/README.md).


</details>

## Per-bug closure requirements

1. Reproduce and record: branch commit SHA, OS/Python/Kivy, media/device config, steps, expected vs actual, terminal output/screenshot or physical evidence.
2. Trace root cause; distinguish what source implements from what it does on actual printer/speakers/camera.
3. Verify that the fix/commit is within an owner-approved scope; do not ask again for an already authorized small change. Use a focused fix, applicable checks and rollback pointer. New unrelated scope needs its own instruction.
4. Mark **FIXED IN SOURCE** only after code change; **VERIFIED** only after documented applicable tests including physical confirmation where needed; **CLOSED** only after owner acceptance.
5. Distinguish local DEMO/MOCK, merchant Sandbox and production. A QR on paper or a local confirmation button is never proof of provider settlement.

## New bug entry template

### BUG-XXX — Symptom (stable ID)
- Severity S0/S1/S2/S3; priority and rationale; status OPEN/REPRODUCED/FIXED IN SOURCE/VERIFIED/CLOSED/BLOCKED:
- First reported / last reproduced; environment, target commit and device:
- Expected behavior vs actual:
- Reproduction steps and associated logs/images:
- Suspected area vs *proven* root cause:
- Dependencies / related FEAT IDs:
- Explicit fix approval, tests run, on-device verification and rollback commit:

