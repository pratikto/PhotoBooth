# AR-01/09 — UX-05 ambiguous payment abandonment

29 October 2026 (Asia/Jakarta). Base/remote verified
206f408efd369d85d40774861edd7746c4a6050a; existing feature branch only.
Contract before code. Reviewed governance/protocol/prompt, checkpoint/handover,
current index/status/backlog/decisions/matrix, master/roadmap, AR-01/02 creation/
reconciliation, AR-06 capability, AR-09 operator/release, operations/privacy and
Midtrans provider contract. Reviewed actual backend/store/client/controller/
Sandbox adapter, release worker and existing HTTP/creation/cancel/claim tests.
Reuse tests.qris_v2_fixture and real HTTP/SQLite/controller/worker boundaries.

1. Lost creation reply, outage and repeated provider 404: explicit cancel/leave
   intent cannot replace identity, bill again, close uncertainty, discard claim
   hash/frozen order, release booth or expose prior customer data. Restart keeps
   same identity; operator abandon/release cannot invent a terminal state.
2. Cancel reply/status unavailable and settlement race: keep original claim,
   authoritative paid OWED and one grant, private until fresh original proof.
   Only deliberate typed worker isolation + exact two-phase ACK/archive can
   free occupancy for a new visitor after payment is known paid.
3. Cancellation independently confirmed terminal after restart: evaluate actual
   behavior, require durable local separation before accepting another visit.
   No cancellation from local timeout/QR countdown/404 or stale cached evidence.
   Test archive write failure and exclude any prior paid/grant/photo entitlement
   from an unpaid-terminal shortcut. Never clear ambiguous state to meet UX.

First micro-increment covers conservative uncertainty/race holds; UX-05 remains
NOT_RUN until combined safe release/terminal evidence completes. Tests first,
minimal runtime change only if a defect is reproduced; focused checks/docs/
commit/immediate push/remote verification per increment. Tests-only changes keep
prior full/native source provenance; one full regression after final runtime fix.
Only synthetic fixtures, no actual merchant/charge/cancel, camera/paper/Drive or
production/OPS/public ingress/branch/default/master operation. Reopens are new
controller/DB connections, not a claim of actual power loss. Raw tickets stay in
memory; no logs/images/databases/customer data published. Rollback inverse source
only; preserve all financial/action/claim/fence/manifest/history records.

## 29 October — UX-05.a conservative abandonment holds

Base/remote verified `206f408efd369d85d40774861edd7746c4a6050a`.
Two new real HTTP/SQLite/controller cases cover lost creation reply + repeated
404 + operator abandon/release denial, and cancel outage/reopen/late settlement.
One original order/key/fingerprint/hash/OWED preserved, no replacement POST,
private restart/no QR; original ticket alone later obtains one grant. Expected
409/503 codes asserted, not arbitrary exceptions. Reopen uses explicit lease
retirement (initial fixture attempt two ERROR corrected, no runtime defect).
**33 focused PASS / zero failure/error/skip**, 2.337s, Python 3.12.14/Linux.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_ux05_abandonment test_checkout_creation_attempts test_checkout_release test_release_session test_customer_claim_session` (SDL offscreen/dummy audio).
Tests/workflow/docs only, runtime unchanged at 3822bb0. New module registered
in both Linux/Windows ledger groups; matching CI pending. UX-05 stays NOT_RUN
until confirmed-terminal and combined paid isolation/archive acceptance tested.
Matrix 57/0/9/3 unchanged. Next test confirmed cancellation after restart and
paid proof -> PREPARE -> typed worker isolation -> ACK/archive -> new visitor;
fix only a reproduced defect. No production/OPS/public ingress/new branch/
master/default/device/provider effects. Only work/ scratch local. Rollback
inverse tests/docs only; retain all financial/claim/fence/media/history records.

## UX-05.b / BUG-024 — confirmed cancellation held after restart

New six-method module at test base be6f96e: **four PASS/two FAIL**, zero error,
0.577s. Real cancel succeeded but its response/status was unavailable; after
restart fresh provider cancellation is applied server-side, yet controller stays
CANCELLING forever because private reconciliation only updates the order view.
No double charge, payment loss or unauthorized media observed; S2 kiosk
availability gap. Paid isolation/lost ACK/archive/return and unchecked cached
terminal tests already PASS before fix. Preserve baseline failure evidence.

Minimal fix contract: only persisted CANCELLING intent, independently checked
terminal state, no service/grant/fulfillment/issue/local transaction/allocation
can finalize as CANCELLED. Reuse immutable exact-key archive before final journal
commit. Archive/save failure must keep active CANCELLING; retry/reopen is safe.
Never unlock from cached terminal, outage, 404, paid rights or a local countdown.
No new provider request/header, charge/cancel behavior or paid release policy.
Clear old in-memory ownership only after local completion. Full regression/CI
follow final runtime fix; real merchant/device cancellation remains unverified.

## 29 October — UX-05.b / BUG-024 focused remediation

First test/workflow push `be6f96e579796a6f7e23b732a80cb972a86aa234` remote
verified; first matching CI 40855861581 pending/superseded, not claimed PASS.
New extended module baseline six run/four PASS/two FAIL/zero error, 0.577s:
fresh confirmed cancellation after lost reply/restart remained CANCELLING.
S2 availability BUG-024, no payment loss/duplicate charge/media leak observed.
Minimal controller fix archives exact unpaid cancelled visit before final
CANCELLED journal commit, only explicit CANCELLING + independently checked
terminal + no service/grant/fulfillment/issue/local photo/allocation identity.
Archive/save failure stays active; cached terminal and paid rights stay held.
Existing typed paid PREPARE/isolation/ACK/archive/replay/return path preserved.
No provider call/header, schema or journal-version change; existing archive
format reused. Rollback retains all archives and financial/claim/fence/media.
**52 focused PASS / zero failure/error/skip**, 2.833s, Python 3.12.14/Linux.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_ux05_abandonment test_checkout_creation_attempts test_checkout_release test_release_session test_customer_claim_session test_qris_reconciliation_session test_qris_session`.
Six UX-05 methods include real HTTP, lost cancel and release replies, cached
terminal denial, actual worker receipt, new visitor/return and archive/final-save
faults. Full GUI/audio-opt-in regression running; matching Windows/Linux CI
pending for this containing micro-push. BUG-024 fixed in source/focused verified,
final verification pending. UX-05 remains NOT_RUN until final evidence, matrix
57/0/9/3. Next full/CI checkpoint, then UX-07 preflight scope/readiness evidence.
UX-11, PAY-22/WEB-01–08 and device/provider/release/OPS gates remain separate.
No production/public ingress/branch/master/default or real external effects.
Only work/ scratch local, no unpublished source patch after push.

## 29 October — UX-05 verified / BUG-024 source remediation

First test/workflow micro-push `be6f96e579796a6f7e23b732a80cb972a86aa234` and
final runtime/test micro-push `347e502b0f50d231ec05c0cbcf768f87d2002454` pushed/
remote verified. First CI 40855861581 CANCELLED/superseded; current **CI 40856740113 all
three jobs SUCCESS**, all six UX-05 methods individually PASS on Windows/Linux.
First holds increment 33 focused PASS/2.337s; final **52 focused PASS**, zero
failure/error/skip, 2.833s. Full with GUI/audio opt-ins **1159 run / 1155 PASS /
4 optional SKIP**, zero failure/error, 412.727s, Python 3.12.14/Linux
software GL. Native asset/video skips retain exact reasons; no real hardware.

Six integrated HTTP/SQLite/controller/worker scenarios: lost creation reply,
404/outage and denied replacement/operator abandonment; cancelled response lost
then restart/late settlement preserving private claim/OWED; checked terminal
cancellation archives before new visitor; archive/final-save failures hold;
unchecked cached terminal holds; paid PREPARE/typed isolation/lost ACK/reopen/
archive/new visit/return preserves exact original claim/grant with no new charge.
No automatic media/capture/print/upload/refund or ambiguous charge replacement.

BUG-024 S2 reproduced at be6f96e (six run/four PASS/two FAIL): confirmed
cancellation after restart stayed CANCELLING. Fixed only for explicit unpaid
cancellation with current checked terminal proof and no service/grant/OWED/
photo allocation. Exact-key archive precedes final CANCELLED journal; failed
write remains active. No provider/schema/version change; keep archives on rollback.
**FIXED IN SOURCE / REGRESSION VERIFIED**, not formally CLOSED or released.
[Exact sources/commands/tests/CI/hashes/limits](evidence/ux05-final-verification.json).

UX-05 synthetic **PASS**; matrix **69 IDs: 58 PASS / 0 FAIL / 9 BLOCKED /
2 NOT_RUN**. Audit IN_PROGRESS/AR-13 conditional. UX-07 and UX-11 NOT_RUN,
PAY-22/WEB-01–08 BLOCKED; actual merchant/device/privacy/operations/release remain
separate. Next exact increment: **UX-07** prepayment readiness/printer scope and
fixture evidence audit; reuse existing v1/readiness services, preserve Sandbox
printer/Drive-off, do not enable actual printing to certify a test. UX-11 follows.
Do not repeat verified UX-05/BUG-023. This containing docs-only publication is
final safe checkpoint; resolve exact SHA from Git log/remote. Only work/ scratch
local, no unpublished source patch. No production/OPS/public ingress/new branch/
master/default/deployment or real external effects. Rollback inverse scoped source,
retain all financial/action/claim/fence/media/history and additive audit records.
