# Autonomous recovery — session checkpoint and resume contract

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

## 29 October — BUG-023 verified source remediation

Source `3822bb041d90da9330457d2e4404668be278eee9` pushed/remote verified.
**73 focused PASS / zero failure/error/skip**, 1.650s; four new HTTP tests had
four expected FAIL before correction (24 run/zero error). Full with GUI/audio
opt-ins **1153 run / 1149 PASS / 4 optional SKIP**, zero failure/error,
411.186s, Python 3.12.14/Linux software GL. Skip reasons preserved in evidence.
**CI 40852458558 all three jobs SUCCESS**; all four conflict methods individually
PASS in both matching Windows/Linux logs, alongside prior journal/PIN tests.
All recovery routes (release PREPARE/ACK included) persist NOT_OWNED and
ACTION_CONFLICT before generic 404/409. Real SQL abort returns generic 503 and
never applies rejected action. Exact successful action replay remains idempotent
with no denial row. Wrong-booth records persist after reopen; no order/action/
request/PIN/ticket/peer/customer bytes stored. Existing bounded 4096-event window
and PIN/429 auditing retained. Ordinary route errors and provider observations
unchanged; no fabricated financial rollback, charge/grant/capture/release replay.
[Exact commands/source/CI/results/digests/limits](evidence/bug023-conflict-http-verification.json).

BUG-023 **FIXED IN SOURCE / REGRESSION VERIFIED**, UX-13 synthetic **PASS**.
Not formally CLOSED or released; actual device/operational acceptance NOT_RUN.
Matrix **69 IDs: 57 PASS / 0 FAIL / 9 BLOCKED / 3 NOT_RUN**; overall audit stays
IN_PROGRESS and AR-13 CONDITIONAL. Original denial failure evidence retained.
Next exact increment: **UX-05 contract/source audit** for ambiguous-payment
abandonment/release. Read AR-01 creation uncertainty, AR-09 release/customer
proof and provider contracts; establish safe durable separation without assuming
cancellation, replacing charge or dropping original rights. Test/document actual
conservative guarantees before proposing runtime changes. UX-07/11 remain
NOT_RUN; PAY-22/WEB-01–08 BLOCKED. No repetition of verified BUG-023 work.
No production/public ingress/new branch/master/default/OPS/deployment or real
external effects. This containing docs-only publication is final safe checkpoint;
exact SHA from Git log/remote. Only work/ scratch local, no unpublished source
patch. Rollback scoped inverse source; retain all financial/audit/claim/fence/media.

## 29 October — BUG-023.d conflict audit focused checkpoint

Base/remote verified `e13216af086a1bd64944bc9619bc7f70d1f7d335`.
Recovery-only invoke context now audits CheckoutMissing as NOT_OWNED and
CheckoutConflict as ACTION_CONFLICT on inspect/resolve/release (PREPARE/ACK).
Original generic 404/409 retained; audit SQL failure -> generic 503, no rejected
action retry/effect. Valid exact action replay is successful and creates no
denial. Ordinary routes/provider outages/validation mapping remain unchanged.
Fresh trusted provider observation may precede conflict; do not erase it to
simulate rollback. No new grant/completion/release/charge/media action from audit.
Four new HTTP tests: baseline 24 run/four expected FAIL; corrected **73 focused
PASS / zero failure/error/skip**, 1.650s, Python 3.12.14/Linux synthetic.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_qris_recovery test_checkout_durability test_checkout_release test_service_fencing test_qris_api test_qris_http_v2`.
Real SQL abort/redaction/reopen, wrong-booth all routes/both release phases,
changed action/reason/transaction/order and unchanged successful replay covered.
Full GUI/audio-opt-in regression running; matching Windows/Linux CI pending for
this containing micro-push. BUG-023 stays OPEN/UX-13 FAIL until full/CI verified;
matrix 56/1/9/3 unchanged. Next final evidence/checkpoint then UX-05 contract/
source audit (ambiguous payment abandonment, preserve claims/rights, no assumed
cancellation/new charge). UX-07/11 and external/OPS/release gates separate.
No production/public ingress/branch/master/default or real external effect.
Only work/ scratch local, no unpublished source patch after push. Rollback scoped
source only; retain bounded audit and all financial/claim/fence/media records.

## 29 October — BUG-023.c PIN audit verified checkpoint

Micro-pushes `c967ac3471c6089cfbc562ab3386acbe5d3d7afb` (Windows registration)
and `e6aba5a45ccdee8f99a3b1cb9f7fafae30b1adb8` (PIN HTTP integration) remote
verified. First CI 40849916482 CANCELLED/superseded; completed Windows ledger
step 80 PASS/17.004s, all five journal methods PASS, not whole-run PASS.
Current **CI 40850382603 all three jobs SUCCESS**, both Windows journal+HTTP
and Linux HTTP/journal method results verified in exact matching job logs.
**69 focused PASS**, zero failure/error/skip, 1.740s. Full with GUI/audio opt-ins:
**1149 run / 1145 PASS / 4 optional SKIP**, zero failure/error,
412.112s, Python 3.12.14/Linux software GL. Skip reasons preserved in evidence.
All three Sandbox endpoints persist INVALID_PIN/429 before denying; write on
thread pool, no request/credential/order data recorded. Audit failure -> generic
503 without service/provider access. Unauthenticated booth/disabled recovery
never writes audit; existing ordinary status and PIN budget/rotation preserved.
Fresh restart retains denial records. No financial/media/claim/fence alteration.
[Exact command/source/results/CI/digests/limits](evidence/bug023-pin-http-verification.json).

BUG-023 OPEN/UX-13 FAIL: wrong-PIN gap fixed in source, but authenticated action
conflicts/replay and cross-order denial audit still pending. Matrix 56/1/9/3,
overall audit IN_PROGRESS and AR-13 conditional. Next exact increment: use
existing invoke/CheckoutConflict/CheckoutMissing seams to audit only recovery
inspect/resolve/release denials; verify changed action body/order, same-action
successful replay remains idempotent, no provider/paid/service mutation from
audit failure. Focused checks/docs/micro-push, final applicable regression after
runtime change. Do not repeat verified PIN/Windows work. External acceptance and
OPS remain separate; no production/public ingress/branch/master/default/real
effects. This containing docs-only publication is final safe checkpoint; exact
SHA from Git log/remote. Only work/ scratch local, no unpublished source patch.
Rollback scoped source only; retain additive audit and all financial records.

## 29 October — BUG-023.c PIN audit integrated, focused verified

Windows-registration micro-push `c967ac3471c6089cfbc562ab3386acbe5d3d7afb`
remote verified. Its CI 40849916482 Windows ledger step SUCCESS, including
registered journal module; entire run not claimed PASS while pending/superseded.
Current increment audits INVALID_PIN and operator RATE_LIMITED on all three
Sandbox endpoints after booth authentication/explicit recovery gates. Static
route/reason only, SQLite write on thread pool, generic 503 if audit fails.
No service/provider call on denied PIN; original 401/429 and status independence
preserved. Four new HTTP tests: original code 20 run/four expected FAIL; corrected
**69 focused PASS / zero failure/error/skip**, 1.740s, Python 3.12.14/Linux.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_qris_recovery test_checkout_durability test_checkout_release test_service_fencing test_qris_api test_qris_http_v2`.
Windows ledger job also registers test_qris_recovery now, so current matching CI
will cover both journal and HTTP tests. Full regression running with GUI/audio
opt-ins; matching CI pending for this containing safe micro-push. Next finish
full/CI checkpoint, then audit replay/cross-order conflicts. BUG-023 OPEN/UX-13
FAIL; matrix 56/1/9/3 unchanged. No production/OPS/new branch/master/default or
external effects. Only work/ scratch local; retain all financial/audit records.

## 29 October — BUG-023.b Windows coverage registration

Base/remote verified `5d74c518c807ab4dbe976e9666df145e1b33ab69`.
Windows ledger job now explicitly runs test_checkout_durability, including all
five denial journal methods. Local Linux module **19 PASS**, zero failure/error/
skip, 0.149s; this is not Windows acceptance. No runtime change. Current hosted
Windows verification pending for this containing micro-push. BUG-023 OPEN,
UX-13 FAIL, matrix 56/1/9/3 unchanged. Next verify Windows methods then integrate
invalid-PIN/429 audit across inspect/resolve/release with generic 503 on audit
failure; replay/cross-order denials follow. No production/OPS/external effects.
Only work/ scratch local. Existing full foundation evidence retains ab6fbbb
source; no repeat full regression for workflow registration. Retain all ledgers.

## 29 October — BUG-023.a verified foundation checkpoint

Source/micro-push `ab6fbbb4e6af4665f4082f66b9a5b9b6a2562c67` remote verified.
Dormant additive denial journal only, no HTTP integration. **45 focused PASS**,
zero failure/error/skip, 0.893s. Full discovery **1145 run / 1068 PASS / 77 SKIP**,
zero failure/error, 260.586s. Follow-up explicitly enables GUI/audio and executes
exactly the 75 previously opt-out cases: **75 run / 73 PASS / two optional SKIP**, 143.139s.
Three optional model skips and one native-video/ffmpeg skip remain across both commands; these are separate commands,
not a relabeled zero-skip full run. Python 3.12.14/Linux software GL/offline fixtures.
**CI 40843692911 all three jobs SUCCESS**. Linux recovery 394 PASS/zero skip,
112.454s, all five new journal tests PASS; native 111/110/one optional palm SKIP,
90.486s. Windows existing recovery/payment/portable/audio groups SUCCESS, but
the new journal methods were NOT_RUN there: their module is not registered yet.

Next exact increment: register test_checkout_durability in Windows CI and verify
new methods; then mount invalid-PIN/429 audit on inspect/resolve/release with
generic unavailable on audit-write failure. Check replay/cross-order denials
before UX-13 can PASS. BUG-023 OPEN, matrix 56/1/9/3 and audit IN_PROGRESS remain.
No authentication/PIN-budget/customer-proof/paid-rights change, no new endpoint.
Only latest 4096 redacted diagnostic events are pruned, never financial/action/
claim/fence/media records. See [evidence](evidence/bug023-foundation-verification.json) for commands/source/digests/limits.
This containing docs-only push is final safe checkpoint; resolve its SHA from
Git log/remote. Only disposable work/ stays local, no unpublished source patch.
No production/OPS/public ingress/new branch/default/master/deployment or actual
device/provider/paper/Drive/deletion acceptance. Retain additive tables on rollback.

## 29 October — AR-09 BUG-023.a dormant denial journal

Base/remote verified `fc73a486288bc35b2244b9f89f2f278044d6ea22`.
Additive checkout_operator_denials stores only sequence/server time/allowlisted
route and reason. Latest 4096 events retained by sequence in the same transaction;
no order, action, customer, peer, PIN, ticket or bearer field. Reuses existing
WAL/FULL/BEGIN IMMEDIATE. Audit failures propagate and roll back; financial,
claim, fence, action and media records untouched. HTTP integration NOT STARTED;
BUG-023 OPEN/UX-13 FAIL, matrix 56 PASS/1 FAIL/9 BLOCKED/3 NOT_RUN unchanged.
Five new tests initially ERROR before implementation; **45 focused PASS / zero
failure/error/skip**, 0.893s, Python 3.12.14/Linux synthetic. Command:
`.venv/bin/python tools/run_kiosk_unittests.py test_checkout_durability test_qris_recovery test_checkout_release test_service_fencing`.
Full regression running; current CI pending. This containing source/tests/docs
commit is the next immediate micro-push; pin exact SHA after remote verification.
Next finish full/CI evidence, then integrate wrong-PIN/429 audit on all three
Sandbox routes, generic unavailable on audit failure; verify replay/cross-order
conflicts before restoring UX-13 PASS. See [contract](BUG023-DENIAL-AUDIT.md).
No production/OPS/public ingress/new branch/master/default/deployment/device
operation. Only work/ diagnostics local; no unpublished source patch after push.
Rollback inverse source only; retain additive audit and all financial records.

## 29 October — CAP-20 verified final checkpoint

- Micro-pushes remote verified: JPEG `2ac9e82ce72de49d6a7ade385c3db37b2e1707d5`,
  full storage `9f3568b0dd6ea5ab67e0c49b1ef6936cedabc8d4`, native test fixture
  `da3f4447b15dc733dba6792394dace6ce1b0644e`. This containing docs-only commit
  publishes the final safe checkpoint; resolve its exact SHA from Git log/remote.
- **57 storage focused PASS / zero failure/error/skip**, 43.617s. Six methods,
  74 ENOSPC/EACCES cases: **48 actual child exits** (JPEG 14, retake 16, PNG 16,
  initial manifest 2), plus 26 parent cases (issue intent 2, atomic writers 24).
- First JPEG-only CI 40838609747 all three jobs SUCCESS. Full-source initial
  40839833482 FAILED at native flip `8 != 7`; storage/recovery Linux and Windows
  passed. Historical triggering callback is unknown. Controlled unrelated Clock
  callback reproduces old fixture failure; corrected fixture isolates existing
  callbacks only during quiet-poll observation, preserves real RGB/flip checks,
  rejects newly scheduled work, and both mutation controls still fail correctly.
- Corrected fixture **111 focused run / 110 PASS / one optional palm SKIP**,
  zero failure/error, 138.089s. **CI 40842036384 all three jobs SUCCESS**, exact
  source da3f444: Windows payment/recovery **72 PASS**, 193.062s;
  Linux Sandbox/recovery **389 PASS**, 125.141s; both zero skip
  and all six CAP-20 methods PASS. Linux native **111 run / 110 PASS / one
  optional palm SKIP**, 102.715s. No retry or runtime patch.
- Original paid binding/proof/grant/allocation/copies/deadlines/OWED preserved;
  failed operation never falsely ACKs. Unknown bytes held; proved bytes recover
  same operation once; previous committed output survives final-status failure.
  Failed issue-intent save preserves existing OWED; later explicit report once.
  No shutter/render/charge/allocation/print/upload replay. Targeted injected calls
  model writable reporting after media fault removal, not a globally full disk.
- No runtime/schema/UI change. App/tools still e0dc594; prior full
  **1117/1114/3** and local native **c94696d 28 PNG/four QR** retain original
  provenance and are not borrowed for new methods. BUG-013 remains monitoring.
- CAP-20 synthetic PASS; **69 IDs: 56 PASS / 1 FAIL / 9 BLOCKED / 3 NOT_RUN**.
  Overall audit IN_PROGRESS, AR-13 conditional, BUG-023/UX-13 OPEN/FAIL.
  [Exact source/commands/results/digests/CI/limits](evidence/cap20-final-verification.json).

Next exact increment: **AR-09 BUG-023 bounded redacted durable operator-denial
audit**. Re-read operator/master/roadmap/privacy/audit contract and current routes/
schema/rate-limit/replay tests before code; reuse existing booth-authenticated
PIN routes and action journal, first reproduce missing durable wrong-PIN/429,
replay/cross-order denials without weakening authentication. Define bounded
redacted storage/retention and fail-closed behavior; no PIN/ticket/raw order/
customer data in audit. Focused tests/docs then immediate micro-push/remote check;
one applicable final full regression if runtime changes. Do not repeat CAP-20.
UX-05/07/11 remain NOT_RUN; PAY-22/WEB-01–08 BLOCKED. Actual Windows/Ubuntu booth,
provider/merchant, phone/paper/Drive/deletion/privacy/operations/release gates and
OPS queued design stay separate. No production/public ingress/new branch/
master/default/deployment or real external effects. Only work/ scratch remains
local, no unpublished runtime patch. Rollback tests/CI/docs only, preserve all
financial/media/claim/fence/budget records.

## 29 October — CAP-20.c native fixture isolation checkpoint

Storage source `9f3568b0dd6ea5ab67e0c49b1ef6936cedabc8d4` pushed/remote verified:
57 focused PASS, 74 injected cases/48 actual children. Its CI 40839833482 has
pure/Windows SUCCESS (Windows payment 72 PASS, zero skip, 221.038s) and Linux
FAILURE at native redraw test `8 != 7`; Linux Sandbox/recovery 389 PASS, zero skip.
This failed run is preserved, never relabeled successful. Historical callback
identity is unknown. Controlled unrelated Clock redraw reproduces the exact
failure on the old fixture and passes after test-only isolation. Six real RGB
readbacks/new-frame flips/texture identity/labels and exact quiet-poll flip count
remain; a new guard rejects additional scheduled same-packet work. Two mutation
controls still fail as expected (missing new-frame redraw, new same-packet timer).

**111 native focused run / 110 PASS / one optional palm SKIP / zero failure/error**,
138.089s, Python 3.12.14/Linux software GL. No retries, relaxed tolerance or
runtime change. Earlier native attempt interrupted before report; no result
claimed. BUG-013 remains owner-reported working/monitoring. Runtime/tools remain
e0dc594; prior full 1117/1114/3 and native c94696d 28/four retain original source.
[Exact command/source/digests](evidence/cap20-native-fixture-verification.json).

CAP-20 synthetic PASS; matrix **56 PASS / 1 FAIL / 9 BLOCKED / 3 NOT_RUN**;
overall audit IN_PROGRESS/AR-13 conditional, BUG-023/UX-13 OPEN/FAIL.
This containing tests/docs micro-push pins the corrected fixture; next matching
CI and final safe checkpoint, then AR-09 bounded redacted durable denial audit.
UX-05/07/11, PAY-22/WEB-01–08 and actual Windows/Ubuntu booth/provider/paper/phone/
Drive/deletion/privacy/operations/release gates stay open. OPS unchanged. No
production/public ingress/new branch/master/default or real external effect.
Only disposable work/ remains local; no unpublished runtime patch. Rollback
tests/docs only, retain all financial/media/claim/fence/budget records.

## 29 October — AR-04/05/08 CAP-20.b focused checkpoint

First micro-push `2ac9e82ce72de49d6a7ade385c3db37b2e1707d5` pushed/remote verified;
JPEG-only CI 40838609747 SUCCESS. Current complete source is this containing
micro-push; pin exact SHA after push/remote verification. **57 focused PASS /
zero failure/error/skip**, 43.617s, Python 3.12.14/Linux. Six methods/74 injected
ENOSPC/EACCES cases: JPEG 14, retake 16, PNG 16, initial manifest 2, issue intent
2, both atomic writers 24; **48 actual child exits**, 26 parent-process cases.
[Exact command/source/digest](evidence/cap20-all-verification.json).

No false failed-operation ACK or paid service completion. Original proof/current
provider, grant/allocation/copies/deadlines/OWED preserved. Partial/unhashed bytes
held; known staged/published bytes adopt once. Retake selection/quota atomic;
previous committed PNG survives failure of final transaction-status write.
Failed issue-intent save cannot erase pre-existing OWED; report succeeds once
when writable again. Both JSON writers retain prior bytes/absence and clean temp
on create/partial-write/fsync faults. Two parent controller/store reopens keep
same ACKs/bytes; no shutter/render/print/upload/charge/allocation replay.
No runtime defect or runtime/schema/UI change; prior full/native retained at
original source. CAP-20 synthetic PASS; matrix **56 PASS / 1 FAIL / 9 BLOCKED /
3 NOT_RUN**, audit IN_PROGRESS/BUG-023 OPEN. Current matching CI pending.
Next verify current Linux/Windows CI and publish final safe checkpoint; then
AR-09 bounded redacted durable denials for BUG-023. UX-05/07/11/external/OPS gates
stay open. No production/public ingress/real paper/Drive/deletion/new branch/
master/default operation. Only work/ scratch local, no unpublished runtime patch.
Rollback tests/CI/docs, retain all financial/media/claim/fence/budget records.

## 29 October — AR-04/08 CAP-20.a JPEG fault checkpoint

Base/remote verified `abc44d67d69783ae429918d8e6a457f9d13724f9`.
One new method/14 actual child exits after injected ENOSPC/EACCES at intent JSON
replace, image open, partial write, fsync, staged JSON replace, publication link
and capture/quota commit JSON replace. **52 focused PASS / zero failure/error/
skip**, 14.598s, Python 3.12.14/Linux. [Exact command/source/digest](evidence/cap20-jpeg-verification.json).

Caller never ACKs failed capture; old frame remains, unknown/unhashed temp held,
proved staged/published frame adopts same operation/slot once without shutter.
Original proof/fresh provider required on both controller/DB reopens; frozen
contract/copies/retention/OWED and durable redacted paid issue survive. Targeted
media fault is removed before issue reporting; no global-full-volume guarantee.
No runtime defect or runtime/schema/UI change, prior full/native retained at
original e0dc594/c94696d. CAP-20 remains NOT_RUN until retake/PNG/initial/reporting
matrix is exercised; scenario totals 55 PASS/1 FAIL/9 BLOCKED/4 NOT_RUN.
This containing test/CI/docs commit is the next micro-push; pin exact SHA after
remote verification. Matching CI pending. Next extend same fixture for retake,
PNG output/status and initial manifest faults, plus issue-intent write failure;
then current CI/final checkpoint and AR-09 BUG-023. UX-05/07/11/external/OPS gates
remain open. No production/public ingress/real paper/Drive/deletion/new branch/
master/default operation. Only disposable work/ local, no unpublished runtime
patch; rollback tests/CI/docs, retain all financial/media/claim/fence/budget data.

## 29 October — AR-05 CAP-16 verified checkpoint

- First micro-push `fcc0ae96b5de96bc962b4a2e9d25285cf9a3c7de`; final test/CI source
  `1ef7d29454a926d6eccc7cb2ba15162fbfbfa0c8`, both pushed/remote verified.
- **74 focused PASS / zero failure/error/skip**, 22.333s, Python 3.12.14/Linux.
  Three new CAP-16 methods/four actual children/two distinct boundaries: final
  COMMITTED composition before completion intent (106), saved COMPLETING before
  COMPLETE request (107), repeated for provider/refund and corrupt-PNG denials.
  Existing PAY-18 methods separately retain 23 child exits in the same module.
- **CI 40834950593 all three jobs SUCCESS**. Windows payment/recovery **66 PASS**
  (48.445s), Linux protocol/recovery **383 PASS** (53.191s), both zero skip and all
  three CAP-16 methods PASS. Native 111 run/110 PASS/one optional palm SKIP.
  First 40834453941 superseded/CANCELLED, not standalone PASS.
- Backend remains STARTED/OWED before COMPLETE despite locally composed result;
  private restart/original fresh proof, immutable three JPEGs/one PNG/two copies,
  frozen contract/retention and same ACK tuples preserved. Both archives precede
  release. Outage/refund/corrupt PNG hold without ACK/replay/rights loss.
- No runtime defect or runtime/schema/UI change. Application/tools match e0dc594;
  prior full 1117/1114/3 and native c94696d 28/four retain original source. No new
  local full/native/device/provider acceptance is claimed.
- CAP-16 synthetic PASS; matrix **55 PASS / 1 FAIL / 9 BLOCKED / 4 NOT_RUN**.
  Overall audit IN_PROGRESS; BUG-023/UX-13 OPEN/FAIL. [Exact evidence](evidence/cap16-final-verification.json).
- This containing docs-only publication is the final safe checkpoint; resolve
  its SHA from Git log/remote. Only disposable work/ diagnostics are untracked/
  not backed up, no unpublished runtime patch.

Next exact increment: **CAP-20**. Reuse capture/output journal, TransactionStore/
manifest atomic writer and existing original-proof fixtures. Inject ENOSPC and
EACCES at intent, temporary image/publication and manifest acknowledgment writes;
assert no false capture/output/quota/service commit, no overwrite/replay and
original paid OWED/binding/bytes retained after reopen. Use temporary synthetic
fixtures, never fill the actual disk or change customer permissions. Focused
checks/docs/commit/immediate push and remote verification per safe increment.
Then AR-09 BUG-023 bounded redacted durable denial audit; UX-05/07/11 still NOT_RUN.
PAY-22/WEB-01–08 BLOCKED; actual Windows/Ubuntu booth, merchant/provider, phone/
paper/Drive/deletion/privacy/operations/release remain separate. No production,
OPS/public ingress/new branch/default/master or real external effect. Rollback
only tests/docs, preserve all financial/media/claim/fence/budget records.

## 29 October — AR-05 CAP-16.a focused checkpoint

Base/remote verified `73451f3f449f97fcec76e52a14db4ad5a3e8027f`.
One new method/two actual child exits after COMMITTED final PNG/local composition
before completion intent (106), and saved COMPLETING before API (107). Backend
remains STARTED/OWED at both exits; restart stays private/active. Fresh original
customer proof restores the same three-JPEG/one-PNG/two-copy result, preserves
retention/frozen contract/manifest and reuses original STARTED/COMPLETED tuple.
No charge/allocation/capture/render/print/upload replay; both archives become
durable before local release. **72 focused PASS / zero failure/error/skip**,
20.830s, Python 3.12.14/Linux. [Command/source/digest](evidence/cap16-composition-verification.json).

No runtime defect or runtime/schema/UI change; prior full/native provenance
retained at e0dc594/c94696d, no new local full/native/device result claimed.
CAP-16 synthetic PASS; matrix **55 PASS / 1 FAIL / 9 BLOCKED / 4 NOT_RUN**;
audit IN_PROGRESS/BUG-023 OPEN. This containing tested commit is the next safe
micro-push; resolve its SHA, push and verify remote before continuing. CI pending.
Next CAP-16.b provider outage/refund and damaged committed PNG denial after
these crashes, then final current CI/checkpoint, CAP-20 and AR-09 denial audit.
UX-05/07/11/provider/device/privacy/retention/release/OPS gates unchanged.
No production/public ingress/real paper/Drive/deletion/branch/master/default
operation. Only work/ scratch local, no unpublished runtime patch. Scoped inverse
of tests/docs retains all financial/media/claim/fence/budget records.

## 29 October — AR-04/05 CAP-11–13 verified checkpoint

- First micro-push `d133e209629c7b6a99927169ef290cf3ed715249`; final test/CI source
  `423d9d2c9096ec897521df565f2c59572057efd5`, both pushed/remote verified.
- **80 focused PASS / zero failure/error/skip**, 20.913s, Python 3.12.14/Linux.
  Five methods/seven actual children at six retake boundaries: selection, intent,
  temporary, staged, published, committed; extra staged tamper case.
- **CI 40831396874 all three jobs SUCCESS**. Windows payment/recovery **63 PASS**
  (53.091s), Linux protocol/recovery **380 PASS** (67.954s), both zero skip and all
  five retake methods PASS. Native 111 run/110 PASS/one optional palm SKIP.
  First CI 40830915281 superseded/CANCELLED, never credited standalone PASS.
- Exact original claim/fresh settlement, grant/allocation, selected index 1,
  three originals/one retake/two copies/retention/OWED retained. Proved bytes
  adopted once; unhashed/tampered bytes held. No replay, overwrite or quota renewal.
  Second parent-process controller/store reopen preserves committed state.
- No runtime defect or runtime/schema/UI change. Application/tools trees match
  e0dc594; prior full (1117/1114/3) and native c94696d (28/four) keep original
  source. No new local full/native/device/provider acceptance claimed.
- Matrix **54 PASS / 1 FAIL / 9 BLOCKED / 5 NOT_RUN**; CAP-11/12/13 synthetic PASS.
  Overall audit IN_PROGRESS, BUG-023/UX-13 OPEN/FAIL. [Exact evidence](evidence/cap11-13-final-verification.json).
- This containing docs-only publication is the final safe checkpoint; obtain
  its exact SHA from Git log/remote. Only disposable work/ diagnostics remain
  untracked/not backed up, no unpublished runtime patch.

Next exact increment: **CAP-16**, reusing tests/service_crash_fixture.py and
current original-proof/result restoration. Exit after final saved composition
while backend remains STARTED/OWED, before COMPLETE API; restore only original
result and replay original ACK without camera/render/print/upload. Then CAP-20
intent/image/manifest write faults and AR-09 BUG-023 durable redacted denial audit.
Remaining NOT_RUN CAP-16/20 and UX-05/07/11; PAY-22/WEB-01–08 BLOCKED. Actual
Windows/Ubuntu booth, provider/merchant, paper/phone/Drive/deletion/privacy/
operations/release remain separate. No production/OPS/public ingress/new branch/
master/default operation. Rollback only tests/CI/docs, preserve all customer data.

## 29 October — AR-04/05.a CAP-11 focused checkpoint

Base/last remote verified `8c5553b77f0264622b19810d86e95a08a105c7eb`.
One new method, two actual os._exit children after durable selection and retake
INTENT before bytes. **76 focused PASS / zero failure/error/skip**, 20.288s,
Python 3.12.14/Linux cloud. Original claim/fresh settlement, index 1, three
unchanged originals/two copies/retention/OWED, VOID audit and one explicit
synthetic retake verified; fresh controller reopen retains consumed quota.
[Command/source/digest](evidence/cap11-verification.json).

Tests/CI/docs only; application unchanged at e0dc594. No runtime defect found,
no schema/UI migration or new full/native run; previous provenance unchanged.
CAP-11 synthetic PASS; matrix **52 PASS / 1 FAIL / 9 BLOCKED / 7 NOT_RUN**.
This containing tested commit is the next micro-push; resolve/push/verify its
exact SHA before continuing. Matching Linux/Windows CI pending at publication.
Next CAP-12 temporary/STAGED/published frame exits, unknown bytes held and proved
bytes adopted once, then CAP-13 post-commit exit/consumed quota; no auto-shutter.
BUG-023 and CAP-16/20, UX-05/07/11/external/OPS gates remain. No production,
real paper/Drive/deletion, branch/default/master change. Only disposable work/
local, no unpublished runtime patch; rollback tests/CI/docs, retain every record.

## 29 October — PAY-18 verified; next CAP-11–13

Tests/CI source `74155c13787fc608304a6214eb374a20e424ebdd` and first micro-push
`3ad80da74da2a0fc3c9d5e3dbe3d84f91a483f4a` pushed/remote-verified.
**86 focused PASS / zero failure/error/skip**, 22.532s; three methods execute
23 actual child exits at seven claim/STARTED/COMPLETED/archive boundaries.
[CI 40818696969](https://github.com/pratikto/PhotoBooth/actions/runs/40818696969)
**all three jobs SUCCESS**: Windows payment/recovery 58 PASS/zero skip, Linux
protocol/recovery 375 PASS/zero skip; native 111 run/110 PASS/one optional palm
SKIP. First CI 40818395624 superseded/CANCELLED, not standalone PASS.
[Exact source/commands/limits](evidence/pay18-final-verification.json).

No runtime defect/application/schema/UI change. Original paid identities, proof,
OWED, copies and result bytes survive with no repeated charge/capture/render/
print/upload. Final archive interruption remains active/private until durable
history/index/journal. Prior full e0dc594 (1117/1114/3) and native c94696d
(28 PNG/four QR) retain original source; no new local full/native run
or physical acceptance is claimed.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**, BUG-023 OPEN/audit IN_PROGRESS.
Next **CAP-11–13 retake child exits**, then CAP-16 pre-request, CAP-20 and AR-09
redacted denial audit. External/OPS/production gates unchanged; work/ scratch only,
no unpublished runtime patch. This docs-only publication is the final safe
checkpoint; resolve its exact SHA from Git/remote, then continue unfinished work.

### Exact next implementation step

Start AR-04/05 retake evidence, not completed AR-03/PAY-08/PAY-18 work.
Reuse tests/capture_crash_fixture.py, test_capture_journal.py,
test_photo_reconstruction.py and the original bound AllocationHarness/customer
proof. Add real exits after saved retake selection, after saved retake frame
before quota/manifest acknowledgment, and after committed retake. Check selected
original index, exactly three retained originals/one immutable retake, original
consumed quota, frozen copies/retention and OWED; no automatic shutter or media
replacement. Unknown/unhashed bytes remain held. Then focused tests, docs,
commit/push and exact remote verification before the next increment.

Remaining NOT_RUN: CAP-11/12/13/16/20 and UX-05/07/11. UX-13/BUG-023 is FAIL,
PAY-22 and WEB-01–08 BLOCKED. Physical Windows/Ubuntu, provider/merchant, paper/
phone/Drive/deletion/privacy/operations/release remain separate. No production,
OPS, public listener, branch/default/master change. Rollback only tests/CI/docs;
preserve all financial/media/claim/fence/budget records. Local work/ diagnostics
are untracked and not backed up; no unsafe source patch remains.

## 29 October — AR-03.d2 completion/archive process exits

Previous micro-push `3ad80da74da2a0fc3c9d5e3dbe3d84f91a483f4a` remote verified.
**86 focused PASS / zero failure/error/skip**, 22.532s; three PAY-18 methods,
23 real child exits at seven distinct boundaries. New archive exits hold local
COMPLETING after accepted ACK, operation history and lookup index; no new visit
or archive bypass before original proof and durable final journal. Original
three JPEGs/one PNG/manifest/copies/OWED remain unchanged, no repeated effects.
[Command/source/limits](PAY18-SERVICE-REPLIES.md).

Tests only; no runtime defect/application/schema/UI change. Matching CI pending
at this containing commit; first run 40818395624 still running at publication.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**, BUG-023 OPEN/audit IN_PROGRESS.
Next: matching CI/final checkpoint, then **CAP-11–13 retake child exits**;
CAP-16 pre-request, CAP-20 and AR-09 denial audit follow. Prior full/native stay
at e0dc594/c94696d; no new full/native/device/provider/production/OPS acceptance.
Only disposable work/ local, no unpublished runtime patch. Scoped inverse of
new tests/docs retains every customer record; containing SHA resolved after push.

## 29 October — AR-03.d1 PAY-18 combined lost replies

Base/remote verified `03189012b5f4c6204ef4f8718bb218a1baac32d5`.
**85 focused PASS / zero failure/error/skip**, 12.257s. Two new methods run
**eight actual child exits at four boundaries**: original booth claim, customer
claim, STARTED and COMPLETED committed before local acknowledgment. Same
order/grant/claim operation/allocation/transaction/result; one provider charge,
three synthetic JPEGs/one composition, original OWED and private proof preserved.
Outage HTTP 503/refund HTTP 409 deny cached-PAID recovery; existing bytes remain.
[Contract/commands/provenance](PAY18-SERVICE-REPLIES.md).

Tests/CI/docs only; no runtime defect or application/schema/UI change. Current
CI pending at this containing test commit. Prior full e0dc594 (1117/1114/3) and
native c94696d (28 PNG/four QR) retain original source; no new full/native result.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**; PAY-18 synthetic PASS,
BUG-023 OPEN, overall audit IN_PROGRESS. Next AR-03.d2 completion/archive exits,
then CAP-11–13, CAP-16 pre-request boundary, CAP-20 and AR-09 denial audit.
External/OPS/production gates unchanged; only disposable work/ local, no
unpublished runtime patch. This containing commit is the next micro-push;
resolve its SHA from Git, push and verify remote before continuing.

**Historical CAP-01–05 task, 29 October:** AR conformity/development IN_PROGRESS.
**Completed now:** AR-03.c / CAP-01–05 exact process exits, 66 focused PASS;
matching CI 40815197373 all three jobs SUCCESS. **Matrix 50 PASS / 1 FAIL /
9 BLOCKED / 9 NOT_RUN**, BUG-023 still OPEN.
**Branch:** `feature/portrait-kiosk-v2-next` (existing).
**Application runtime:** `e0dc59435772148be86449c55140d4b9be2f6364`, unchanged.
**Latest test/CI source:** `e72e28bdf8b0cbb080ef0c35aa8a1e3906bf55cb`.
**Native/full baseline:** retained at original e0dc594/c94696d sources; not rerun
or relabeled for this tests-only coverage increment.

## Latest verified continuation — AR-03.c / CAP-01–05

- **Exact pushed/remote-verified tests:** `c87050eeb4f0223577d68796ff0ace4f4a1d2a95` CAP-01/02,
  `e72e28bdf8b0cbb080ef0c35aa8a1e3906bf55cb` CAP-03–05/orphan. This containing final docs publication
  is the next safe checkpoint; resolve its exact SHA from Git log/remote.
- **Completed:** seven os._exit children at six distinct boundaries; original
  customer proof/current provider evidence, one paid order/grant/operation/
  allocation/counter, first manifest/existing-byte preservation, no automatic
  shutter/render/print/upload. Unknown/orphan bytes remain held without recency
  scanning. No runtime defect, schema/journal/UI/application change.
- **Tests/CI:** 66 focused PASS / zero failure/error/skip, 5.965s. CI 40815197373
  at e72e28b **three jobs SUCCESS**, Windows payment/allocation group 55 PASS,
  zero skip. First 40814744796 superseded/CANCELLED, not standalone PASS.
  [Exact command/hashes/counts](evidence/cap01-05-final-verification.json).
- **Retained evidence:** prior full 1117 run/1114 PASS/3 optional palm SKIP at
  e0dc594, native 28 PNGs/four QR at c94696d. New methods are focused/CI-verified;
  no new full/native/physical outcome claimed. Application/tools tree IDs match.
- **Remaining:** matrix 50 PASS / 1 FAIL / 9 BLOCKED / 9 NOT_RUN; audit IN_PROGRESS.
  BUG-023/UX-13 durable operator-denial audit OPEN, no blanket conformity/release.
- **Next exact increment:** PAY-18 combined lost claim/STARTED/COMPLETED replies.
  Reuse tests/test_checkout_durability.py, current real-process fixture and
  qris_session COMPLETING/archive path. Prove same original grant/transaction/
  ACK, no service/capture/print replay; do not mark completed from a GUI flag.
  Then CAP-11–13 retake, CAP-16 compose/COMPLETE, CAP-20 disk/permission, AR-09
  denial audit. UX-05/07/11 and all external provider/device/privacy gates remain.
- **Boundaries:** no production, OPS, actual printer/Drive/deletion, public ingress,
  branch/default/master change. Five queued OPS docs unchanged/NOT_STARTED.
- **Local-only/rollback:** work/ disposable synthetic reports/diagnostics, not
  remotely backed up; no unsafe unpublished runtime patch. Inverse tests/CI/docs
  only, preserve every financial/media/claim/fence/budget record.

## Historical focused checkpoint — AR-03.c2 CAP-01–05

Prior micro-push `c87050eeb4f0223577d68796ff0ace4f4a1d2a95` pushed/remote-verified.
Added folder/pre-manifest, manifest/pre-STARTED and committed STARTED/lost-reply
process exits plus orphan/no-parent-scan denial. **66 focused PASS**, zero
failure/error/skip, 5.965s; seven real exits/six distinct boundaries. Actual
original customer claim and current provider status restore only the same paid
allocation; existing manifest bytes preserved, zero shutter/render/print replay.
[Exact evidence](CAP01-05-ALLOCATION-CRASHES.md).
No runtime defect or runtime/schema/UI change. Matrix **50 PASS / 1 FAIL /
9 BLOCKED / 9 NOT_RUN**, CAP-01–05 synthetic PASS. This containing commit is the
next tested micro-push; CI pending. Prior full/native source results retained,
no new full/device/provider evidence inferred. Next matching CI then PAY-18
combined service-reply faults, retake/COMPLETE/disk and AR-09 BUG-023. External/
OPS gates unchanged; only disposable work/ local, no unpublished runtime patch.

## Historical focused checkpoint — AR-03.c1 CAP-01/02

Base/remote verified `c4c1847bd8086c36f3ec1d3a755728896321495f`. Added three
actual child exit boundaries against unchanged runtime e0dc594: before local
intent, before backend request and after committed allocation/lost response.
Authenticated original customer proof, one grant/order/operation/transaction,
WAL/FULL/provider integrity and no repeated charge/counter/media action verified.
**34 focused PASS**, zero failure/error/skip, 2.647s. No runtime defect or source/
schema/UI change. [Contract/evidence](CAP01-05-ALLOCATION-CRASHES.md).
CAP-01/02 synthetic PASS; matrix **47 PASS / 1 FAIL / 9 BLOCKED / 12 NOT_RUN**.
This containing test/workflow/docs commit is the next micro-push; current CI
pending. Existing full/native source evidence stays separately pinned.
Next CAP-03–05 exact folder/first-manifest/accepted STARTED exits. BUG-023/external/
OPS gates unchanged. Only disposable work/ local; no unpublished runtime patch.

## Latest verified continuation — AR-02.d / PAY-08

- **Pushed and remote verified:** reader `52a9a18857580ddcc822fe77cd36af76d489a532`;
  mounted runtime `e0dc59435772148be86449c55140d4b9be2f6364`;
  Windows test/CI-only correction `c94696d243c6a345182857d28d249d2d01d7d05b`.
  This containing docs publication is the next safe checkpoint; resolve its SHA
  from Git HEAD and verify remote before continuing.
- **Completed:** passive Windows NLM/Ubuntu NetworkManager sampled restoration
  on existing Sandbox worker; same-order observation only, durable backend
  priority/lease, no repeated charge/grant/service/media effect, private late
  callback denial. Unknown/missing OS hints retain existing bounded polling.
- **Tests:** reader 9 PASS; integrated 103 PASS; portable 49 PASS Linux/Windows;
  full **1117 run / 1114 PASS / 3 optional palm SKIP / zero failure/error** at
  e0dc594, 335.317s. No full rerun asserted for c94696d cleanup-only test change.
  [Exact commands/trees/skips/digests](evidence/pay08-final-verification.json).
- **CI/native:** 40809459547 at c94696d **three jobs SUCCESS**. Initial missing
  qrcode Windows failure preserved; reader CI also SUCCESS. Clean c94696d native
  **28 PNGs / four QR checks PASS** at both portrait targets. Raw pixels/logs
  private untracked work/; only safe manifests/verdicts published.
- **Remaining:** matrix 45 PASS / 1 FAIL / 9 BLOCKED / 14 NOT_RUN. Overall audit
  IN_PROGRESS; BUG-023/UX-13 durable denial audit OPEN, no blanket conformity.
- **Next exact increment:** AR-03 CAP-01–05 child exits before/after allocation
  intent, first folder/manifest, STARTED accepted before local ACK. Start from
  tests/test_checkout_fulfillment.py, tests/test_photo_allocation.py and existing
  crash fixtures; bind original key/grant/operation/transaction and no new charge/
  counter/media rewrite. Then PAY-18, remaining retake/COMPLETE/disk and AR-09.
- **External gates unchanged:** actual Windows/Ubuntu reconnection, merchant/
  provider/phone/paper/Drive/deletion/privacy/operations, public ingress/release.
  Future Settings/Emulate Ticket/QRIS Slip runtime NOT_STARTED; OPS docs unchanged.
- **Local-only:** disposable work/ synthetic diagnostics/images/raw logs, not
  remotely backed up; no unfinished runtime patch. No schema/journal migration.
  Scoped inverse unmounts OS hint and retains all financial/media/claim/fences;
  never reset or replay effects to recover usability.

## Historical intermediate — AR-02.d3 Windows fixture/CI correction

Mounted e0dc594 pushed/remote verified; full **1117 run / 1114 PASS / 3 optional
palm SKIP / zero failure/error**, 335.317s. Windows CI 40808591124 fails at fixture
import (qrcode missing, 43 run / 1 ERROR); independent 61-case recovery step PASS.
This containing increment adds the missing Windows QR dependency and explicitly
closes the direct-use current flow before temp cleanup. **49 focused PASS**,
zero failure/error/skip, 1.389s. Runtime/assertions unchanged; prior full retains
exact e0dc594 test tree, newer test/CI revision verified separately.
[Failure/command/evidence](PAY08-CONNECTIVITY.md).
Next: verify new CI, clean native captures/QRs, publish final source checkpoint;
then AR-03 CAP-01–05. Matrix 45 PASS / 1 FAIL / 9 BLOCKED / 14 NOT_RUN. BUG-023,
external and OPS gates unchanged. No unpublished runtime patch, only work/ local.

## Historical intermediate — AR-02.d2 mounted, focused PASS

Previous reader micro-push `52a9a18857580ddcc822fe77cd36af76d489a532` pushed/remote-verified.
Native known-order recovery now coalesces OS offline→online on the existing
single worker and immediately requests same-order read-only reconciliation;
backend persisted priority/lease still bounds GET. No refresh/claim follows in
that iteration; ownership/media/service remain held. **103 focused PASS**,
zero failure/error/skip, 39.392s. Test-first integrated run: 7 run, 3 FAIL/3 ERROR.
[Contract/command/source evidence](PAY08-CONNECTIVITY.md).
This containing functional commit is the mounted source; final full/CI PENDING.
PAY-08 synthetic PASS / AR-AUDIT-002 resolved; matrix **45 PASS / 1 FAIL /
9 BLOCKED / 14 NOT_RUN**, BUG-023 and physical/provider/OPS gates unchanged.
No schema/journal migration or new layout; unknown OS hint retains bounded polls.
Next: final full/matching CI at pushed source, then AR-03 CAP-01–05 crash fixtures.
Only disposable work/ local; scoped inverse retains every order/claim/media/fence.

## Historical intermediate — AR-02.d1 reader checkpoint

Base/remote verified `e0f4bb663f25247003176da555dbd30744c0e2e3`. Added an
**unmounted** passive Windows NLM/Ubuntu NetworkManager hint reader and five-second
edge coalescer, reusing the existing worker/backend design. **9 focused PASS**,
zero failure/error/skip, 0.004s; OS output injected, no external probes. Child
helpers exclude booth/merchant/PIN/customer credentials. No checkout behavior,
schema or journal change; PAY-08 remains NOT_RUN, matrix 44 PASS / 1 FAIL /
9 BLOCKED / 15 NOT_RUN. This containing commit publishes the safe independent
reader/test/CI/docs increment; exact SHA will be pinned after remote verification.
Next AR-02.d2: mount on active known-order recovery worker and test one immediate
GET after offline→online plus duplicate/backoff/reopen/privacy guards. Final full
regression/CI follows that functional source. BUG-023/external/OPS gates unchanged.
Only disposable work/ local; no unpublished runtime patch after push. Rollback
unmounts/inverses this additive source only, retaining all financial/media state.

## Latest verified continuation — audit evidence and BUG-022

- **Latest functional SHA / pushed and remote-verified:** `4642841f3e99d8c74b4b379e24922a7ba3f614c9`.
  Payment evidence: `8ebcd123098fe5a937c59f2b88d7fe60c9bedf7b`.
  Previous docs checkpoint: `5d318f803df9e7570ceb6f1f8124691f7051540d`.
  Current docs publication SHA is this containing Git commit (resolve via Git log).
- **Completed:** bounded first source pass AR-00–13, PAY-06/PAY-21 exact synthetic
  evidence and BUG-022 committed-PNG loss hold correction. Focused 116 and 61 PASS;
  full **1,100 run / 1,097 PASS / 3 optional palm SKIP / zero failure/error**,
  364.124s. Native video PASS. [Command/source/digests](evidence/ar-audit-final-verification.json).
- **Matching CI:** 40790865010 at 4642841, all three jobs SUCCESS. Prior
  40790391324 superseded/CANCELLED, not standalone PASS. Source trees unchanged
  through docs updates. No new local native PNG/phone/physical evidence claimed.
- **Open audit findings:** AR-AUDIT-002 missing native connectivity-restored
  producer (PAY-08 NOT_RUN); BUG-023 missing durable wrong-PIN denial audit
  (UX-13 FAIL). PIN budget is process-local; customer ticket budget durable.
  Matrix **44 PASS / 1 FAIL / 0 SKIP / 9 BLOCKED / 15 NOT_RUN**. Audit IN_PROGRESS;
  AR-13 historical CONDITIONAL report is not full conformity or release approval.
- **Next exact action:** AR-02 define/wire a bounded native connectivity-restored
  signal and test repeated outage→restore→one immediate GET/throttled duplicates
  with unchanged order/grant; then AR-03 CAP-01–05 exact allocation/STARTED exits,
  PAY-18/COMPLETE/retake/disk evidence and AR-09 bounded redacted denial audit.
- **Blockers unchanged:** merchant/provider contract, actual Windows/Ubuntu/
  phone/paper/Drive/deletion/privacy/operations, public webhook and release gates.
  No production/OPS code, print/Drive activation, new branch/default/master change.
- **Local-only:** work/ disposable synthetic logs, private fixture pixels and
  diagnostics; not remotely backed up, no unfinished runtime patch. Scoped inverse
  rollback retains all records/media/fences, never recharges/renders/reprints.

## Historical documentation check — f72fdbc AR-13 status confirmed

Current source-tree IDs and live matching CI confirm the newer f72fdbc assessment
above. The 635de92 1094-case report is historical; its recovered provenance is now
linked in [validation](AUTONOMOUS-RECOVERY-VALIDATION.md). Do not restart at AR-09
or equate the AR-13 assessment to complete fault coverage/production approval.
The active conformity review remains IN_PROGRESS, with PAY-06 the first exact
source-evidence gap. No new test run/runtime/OPS work was done by this docs check.

## Historical interim source audit checkpoint — full/CI still running

- Exact pushed/remote-verified functional SHA: `4642841f3e99d8c74b4b379e24922a7ba3f614c9`.
  Payment evidence commit: `8ebcd123098fe5a937c59f2b88d7fe60c9bedf7b`.
- Completed: bounded source-reading pass AR-00–13; PAY-06/PAY-21 new evidence
  (116 focused PASS), BUG-022 missing committed PNG correction (61 focused PASS).
- Confirmed remaining findings: AR-AUDIT-002 has no native connectivity-restored
  producer (PAY-08 NOT_RUN); **BUG-023 OPEN**, wrong-PIN denials are rate-limited
  but have no durable audit (UX-13 **FAIL**, previous PASS corrected). Operator
  PIN counter is process-local; customer-capability budget is separately durable.
- Current matrix **44 PASS / 1 FAIL / 0 SKIP / 9 BLOCKED / 15 NOT_RUN**. Earlier
  45/0/9/15 and 43/0/9/17 below remain dated historical classifications.
- Full regression at 4642841 running; CI 40790865010 has pure/Windows SUCCESS,
  desktop still running at this checkpoint. Superseded 40790391324 CANCELLED by
  existing concurrency policy, not recorded as PASS. No full result inferred.
- Next: finish current full/CI verification and pin results. Then AR-02 PAY-08
  native event contract/fixture, AR-03 CAP-01–05 exact allocation/STARTED faults,
  remaining media/COMPLETE faults, and AR-09 bounded redacted denial audit with
  wrong-PIN/replay/cross-order tests. Preserve stage dependency order.
- Audit IN_PROGRESS; no blanket conformity verdict. External provider/device/
  retention/public ingress/release gates, future OPS NOT_STARTED remain unchanged.
- This docs/evidence checkpoint adds no runtime changes. Local-only `work/` raw
  synthetic diagnostics, no unsafe/unpublished runtime patch. Scoped rollback
  retains every financial/claim/media/fencing record.

## Previous audit micro-increment — BUG-022 missing committed PNG

- Base / exact last pushed and remote-verified SHA:
  `8ebcd123098fe5a937c59f2b88d7fe60c9bedf7b` (payment audit, 116 focused PASS).
- Current functional correction: this containing Git commit. Confirmed S1
  reconstruction defect: missing COMMITTED PNG passed inspection, then restore
  installed state before FileNotFoundError. Now both paths hold before state
  installation. No rerender, media rewrite, payment/obligation change or migration.
- Test-first: 14 run, 2 FAIL/1 ERROR in new synthetic regression. After correction
  **61 focused PASS**, 39.146s, zero failures/errors/skips.
  [Exact command/digests](evidence/ar-audit-missing-output.json).
- Matrix remains 45 PASS / 9 BLOCKED / 15 NOT_RUN; source audit IN_PROGRESS.
  Full regression/matching CI PENDING at publication; previous f72fdbc full run
  must not be credited to this correction. Windows reconstruction module added.
- Next: final full suite at this pushed SHA and remaining native/privacy/operator/
  launcher review; then exact CAP-01–05/PAY-08/PAY-18 fault evidence. External
  provider/device/retention/public-ingress/release gates remain unchanged.
- No production, OPS, paper/Drive activation. Local-only disposable `work/` logs;
  no unfinished runtime patch after publication. Preserve all records on rollback.

## Previous audit micro-increment — payment evidence, 2026-10-29 06:52 WIB

- Base/last verified remote: `647991ec013e75477c5c8564133beb68947984f4`; runtime stays
  `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`. Audit remains IN_PROGRESS.
- Completed: PAY-06 actual pre-commit process exits and PAY-21 bounded/redacted
  provider failures, tests/workflow/docs only. **116 focused PASS**, 1.977s,
  zero failures/errors/skips. [Command/hashes](evidence/ar-audit-payment.json).
  No runtime defect confirmed in this bounded review. Matrix now 45 PASS,
  9 BLOCKED, 15 NOT_RUN; older counts below are dated baseline evidence.
- Publication SHA: this containing commit (resolve via Git history); next
  checkpoint records the exact remote-verified SHA. CI pending at publication;
  full regression/native evidence remains at f72fdbc, not rerun for tests-only.
- Next: review exact allocation/STARTED/COMPLETE and media-reconstruction paths;
  first exact remaining fault sequence CAP-01–05, with PAY-08/PAY-18 still open.
  Continue privacy/operator/supervisor review; no blanket conformity claim.
- Blockers: original external provider/device/public ingress/retention/release
  gates unchanged. No production, OPS, real print/Drive or new branch.
- Local-only: disposable `work/` logs; no unpushed runtime patch. Rollback only
  this test/workflow/docs increment and retain all financial/media records.

## Mandatory workflow

The owner prefers **frequent small tested commits AND remote pushes** because a five-hour ChatGPT/Codex usage limit can interrupt development. Treat a verified remote push as the durable cross-session checkpoint; a local commit, stash, or uncommitted working tree is **not** a remotely recoverable checkpoint.

1. Read `AGENTS.md`, the development protocol and the five autonomous recovery documents before touching implementation. Refresh remote branch, inspect `git status`, and read recent commits and this checkpoint.
2. Divide every approved AR stage into small, independently understandable substeps (`AR-01.a`, `AR-01.b`, etc.). Prefer completing, testing, documenting, committing and pushing each safe substep, rather than delaying to the end of an AR stage. Checkpoint opportunities around 30–45 minutes of active work are useful; do not create artificial empty commits.
3. After each safe substep: run focused tests, update affected English docs, commit only relevant safe files, push to `feature/portrait-kiosk-v2-next`, verify remote HEAD, and record the exact pushed SHA and whether tests PASS/FAIL/SKIP/NOT_RUN. Continue only after verifying.
4. Before chat context/usage limit interrupts work, finish the smallest safe unit and push it. Update this document plus `docs/DEVELOPMENT_HANDOVER.md` with the finished and unfinished substeps, exact next action, blockers, and any **dirty local-only changes that are NOT on GitHub**. Push that handover as a docs commit and verify its remote SHA.
5. If runtime code is incomplete or unsafe, do **not** push it merely to save time. Commit safe independent docs/tests or disabled code only if it cannot break behavior. Leave unsafe uncommitted code local and explicitly tell the owner it is NOT backed up remotely. No force-push, new branch, master merge, secret commit, reset of payment/customer journals, or unrelated changes.
6. At the next Codex/chat session inspect local branch/working tree and actual remote HEAD first, reconcile local modifications safely, read handover and stage evidence, and resume **only the first unfinished** substep. Do not repeat completed, verified, pushed tasks; do not infer tests from older SHAs.

## Fill this table after each implementation increment

| Field | Required value |
| --- | --- |
| Date/time and platform | YYYY-MM-DD HH:MM Asia/Jakarta; Windows/Ubuntu/Android |
| Branch and origin HEAD before | Exact full SHA |
| AR stage/substep | e.g. AR-01.b; status PLANNED/IN_PROGRESS/IMPLEMENTED/VERIFIED/BLOCKED |
| Work done | Exact scope, changed files, state/schema/migration notes |
| Latest pushed code SHA | Exact remote-verified full SHA; distinguish docs-only SHA |
| Focused checks | Exact command, PASS/FAIL/SKIP/NOT_RUN, test IDs |
| Full suite/device/provider | Exact source/evidence or NOT_RUN |
| Local dirty/unpushed work | Paths and safety caveat, or explicitly NONE |
| Open blockers/approval | External contract, device, merchant, privacy or other blocker |
| Next *small* action | File/function, intended test and AR substep |
| Safe rollback | Previous commit and retained-data plan |

## Current implementation checkpoint — AR-12 evidence / AR-13 assessment

Final application/test source `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88` remotely verified. **1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors**, 428.924s;
command `.venv/bin/python tools/run_kiosk_unittests.py`, GUI/audio opt-ins,
Python 3.12.14 / Debian 13.6 / SDL offscreen/dummy audio, tracked tree clean.
CI [40767441201](https://github.com/pratikto/PhotoBooth/actions/runs/40767441201)
all three jobs SUCCESS at the same SHA. Native 28 PNGs / four redacted QR
checks PASS at both portrait sizes. Matrix **43 PASS / 0 FAIL / 0 SKIP /
9 BLOCKED / 17 NOT_RUN**, not blanket matrix completion.

AR-13 [readiness assessment](AR13-READINESS.md): **CONDITIONAL** for controlled
owner acceptance; **NOT READY for unattended commercial release**. Hardware,
merchant, phone/paper/Drive/retention/privacy/operations gates A01-A12 remain
NOT_RUN/BLOCKED. Original previous-session 1094/1091/3 provenance unavailable;
do not replace it with this new run or infer all old optional cases ran.

**Historical first unfinished source evidence (closed by audit increment 2 above):** PAY-06 exact evidence/pre-DB-commit
child exit. Refresh remote, preserve local state, inspect existing
`tests/test_checkout_reconciliation.py` and WAL crash fixtures; add an isolated
process-exit fixture proving fresh GET after reopen and no duplicate grant.
Then close CAP-01–05, CAP-11–13, CAP-16, CAP-20, PAY-21 and remaining explicit event/hang
gaps. Do not alter production or weaken tests. If runtime changes, focused checks
then one complete final applicable regression; docs alone need no rerun.

Owner next: execute AR13 A01/A02/A04/A06/A09 with current source and record
actual device/provider results; confirm operational/retention/remedy terms and
separate approvals for public webhook, actual deletion, pilot or release.
No OPS runtime, production activation, deploy/default/master/merge change.
All five future OPS documents byte-identical to owner baseline, Emulate Ticket
name retained. AR remains top priority until remaining gates are resolved.

Delivery: `9592649` test clock and `f72fdbc` scanner fix each pushed and checked;
this containing docs/evidence publication is the next checkpoint (obtain SHA
from Git history/remote). Local `work/` only holds disposable synthetic diagnostics,
private QR pixels and raw logs, untracked/not remotely backed up; no unpushed
runtime patch. No customer data inspected. Rollback via scoped inverse of scanner
against preceding `9592649`; preserve every ledger/fence/claim/image/job/budget.
Full command, source trees, digests/skips, historical failures, native limits:
[validation](AUTONOMOUS-RECOVERY-VALIDATION.md) / [safe JSON](evidence/ar12-final-verification.json).

## Historical implementation checkpoint — AR-12.e/f

**Superseding AR-12.f:** `959264962bb4e64a8a4531a085676b55ad26e660` pushed;
CI 40766621706 passes content and Windows, exposes separate Linux recovery scan
failure. A 100-ticket probe reproduces ten primary OpenCV false negatives; its
installed alternate decodes all ten. Scanner now makes one optional alternate
attempt on empty primary result, then retains original ownership verification.
Three new source tests: primary miss, foreign role, absent alternate; no test
assertions removed. See [investigation](AUTONOMOUS-RECOVERY-VALIDATION.md).
Next: commit/push focused-checked correction, one final full run, fresh native
captures/QRs and matching three-job CI, then matrix and AR-13 readiness. Interim
full run at 9592649 was stopped; no final result is claimed. External gates and
OPS restrictions remain unchanged. Rollback: scoped inverse; retain all state.

Remote baseline `e303cdf4db3f009d2f4ed1a075e160d17aaa8bdb` independently verified;
clean required-branch checkout fast-forwarded without losing the prior `work`
branch. All four requested CI runs/jobs/logs reconciled. Windows Errno 9 repair
is confirmed. Linux failed the content-priority fixture; controlled monotonic
1.0 reproduces the exact assertion, 100.0 passes. Historical runner uptime
is unknown. Fixture clock now explicitly 100.0; all assertions/runtime unchanged.
Focused **33 PASS / zero failures/errors/skips**, 2.543s:
`.venv/bin/python tools/run_kiosk_unittests.py test_booth_sync test_content_cache`.
See [investigation](AUTONOMOUS-RECOVERY-VALIDATION.md#ar-12e--independently-verified-ci-history-and-deterministic-fixture-29-october).

Next: one complete regression at this test commit; verify native 28 PNGs/QRs
captured at clean `e303cdf` (same runtime), pin evidence/matrix and publish AR-13
readiness. The previous reported 1094/1091/3 log is unavailable here; do not
invent its command/source/dirty metadata. Actual devices/merchant/phone/paper/
Drive/public HTTPS remain NOT_RUN/BLOCKED. No OPS runtime or production enabled.
Only disposable `work/` local evidence remains untracked; no customer data.
Rollback: inverse the test-only patch, preserve all durable customer state.

## Historical implementation checkpoint — AR-12.d

- Base / last verified remote: `635de92c0f8fba9189981ebf2f168bff8b7a52af`.
- Completed: retain Windows pass and expose Linux isolated-photo failure details. CI 40756011109 Windows autonomous/native and pure jobs PASS; desktop P3 group FAIL with unknown cause. Failure-only report annotation added, no assertions/application changes. Final local full rerun still running.
- Publication SHA: this increment will be pinned after its verified push by the
  next checkpoint; obtain containing commit from Git history.
- Remaining / exact next step: Inspect precise Linux P3 failure, fix only proven cause, verify final complete local regression and matching three-job CI, then publish AR-13 readiness.
- Full suite: deferred to final functional SHA. Actual Windows/Ubuntu devices,
  merchant, paper/Drive and production: NOT_RUN / not enabled.
- Migration/rollback: see stage contract; preserve all ledgers/media/claims,
  never drop additive tables or replay a charge/capture/print.
- Local unpushed work: disposable work/ only; no unrelated customer/secret data.

## Historical verified checkpoint — AR-01.a/b

- **Date/platform:** 2026-10-28 19:36 Asia/Jakarta; Linux cloud, Python 3.12.14,
  SQLite WAL/FULL. Windows development / Ubuntu device acceptance remain separate.
- **Completed AR-00 / last verified remote:** `4261236694358c2f3cd2a475a4cd9cd82f436e00`.
  Contract plus six baseline cases, focused **87 PASS / zero FAIL/ERROR/SKIP**.
- **AR-01 changes:** additive `checkout_create_attempts` table; atomic frozen
  merchant/mode/booth/order/key/cart/charge fingerprint before I/O; PREPARED →
  SENT → UNCERTAIN/VERIFIED. Legacy rows retain financial/service fields and
  receive LEGACY_UNCERTAIN. Only original new-order request may send once;
  duplicate/restart/404 uses same-order status, never another charge.
- **Focused tests:** nine new migration/attempt cases, including real PREPARED
  crash, plus six AR-00 baseline and existing payment/HTTP/operator tests:
  `.venv/bin/python tools/run_kiosk_unittests.py test_checkout_creation_attempts test_autonomous_recovery_baseline test_checkout_backend test_checkout_durability test_qris_session test_midtrans_sandbox test_midtrans_verify test_qris_kiosk_client test_payment_quote test_qris_api test_qris_http_v2 test_qris_recovery`:
  **132 PASS / zero failures/errors/skips**. Initial eight tests before source:
  **2 FAIL / 6 ERROR**, preserved as test-first reproduction, then corrected.
- **Latest pushed code SHA / verified remote:** `017b417d02d63a79b1c5b21c4f0613b7d15186fc`.
  [Exact source hashes/raw reports](AUTONOMOUS-RECOVERY-CREATION.md). This final
  companion publication changes documentation/evidence only; obtain its SHA from
  git log and independently verify remote before the next implementation.
- **Full regression:** **968 run / 965 PASS / 3 SKIP / zero failures/errors** on exact source above;
  [raw report](ar01-full-tests.txt). Three optional palm-model assets cases SKIP.
  **Matching CI [40688374416](https://github.com/pratikto/PhotoBooth/actions/runs/40688374416):
  all three jobs SUCCESS**, including new Windows creation fixtures.
  Real Windows/Ubuntu hardware, merchant, paper/Drive/retention NOT_RUN; production
  not authorized. Software offscreen/dummy audio is not hardware acceptance.
- **Blocker:** Legacy repeat-charge semantics unproven; repeat POST/header remains
  disabled. This blocks repeat-charge activation, not independent AR-02 work.
- **Next first unfinished increment:** AR-02.a tests for a narrow
  booth-authenticated fresh reconciliation (including cached PAID/refund/offline)
  separate from operator resolve. No GUI/photo restore before AR-03–06.
- **Local-only:** work/ scratch evidence/scripts only, disposable and NOT backed
  up; all needed test evidence is published here. No unpushed runtime/test changes
  or merchant/customer data. Do not redo verified AR-00/AR-01 work.
- **Rollback:** inverse scoped AR-01 source; retain additive attempt table and all
  journals/media. Old writers remain readable; upgrade marks their new rows held.

## Historical bootstrap checkpoint — documentation publication

- **Done:** Comprehensive unattended-first master design, provider contract, AR-00–AR-13 roadmap, failure-injection matrix, operator/customer runbook, and repository prompt/process micro-push rules are published to the existing branch.
- **Not done:** AR-00 source baseline test fixtures; provider verification; any recovery runtime code or device/merchant tests. All new stage checks are NOT_RUN.
- **Known previous runtime state:** Existing operator-authenticated recovery HTTP/backend code at `2e5efe5`; native launcher and GUI not yet integrated, and unattended photo reconstruction not yet implemented at the audited baseline.
- **Open provider question:** Exact Legacy Midtrans QRIS charge-idempotency contract; invoice-specific five-minute key rule does not establish the Legacy QRIS charge contract.
- **Next action for Codex:** Verify current branch/HEAD/dirty tree, read all linked docs, then start `AR-00.a`: inventory exact existing payment/fulfillment/photo state and prepare deterministic test fixtures without altering merchant settings or payment state.
- **Sensitive/persistent data:** No account keys, customer photos, SQLite databases, provider payments or journals are changed by documentation publication.

When future code increments begin, replace **only this latest bootstrap status section** with a dated implementation checkpoint while retaining prior distinct evidence by link/appendix as useful. Commit and push the checkpoint after each logical stage and before session cutoff.
