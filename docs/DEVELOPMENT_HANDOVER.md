# Meong Photobooth — GUI v2 development handover

## 29 October — UX-07 Sandbox evidence verified / purchased-printer gate open

Micro-pushes `4099ca1a80251c53d45c5b0e6a4b9c25f090ef4a` (five HTTP boundary
methods) and `685b994f01efd48cbe0d91d56a71f3143b8b7d11` (native widget method)
remote verified. First CI 40861858317 superseded; **CI 40862328219 all three jobs
SUCCESS**, five boundary methods individually PASS on Windows/Linux, new native
method PASS in Linux Sandbox group at both 800x1280 and 452x900.
First focused **34 PASS**, 2.990s; final **36 focused PASS / zero failure/error/
skip**, 25.080s, Python 3.12.14/Linux software GL. Fifteen failure vectors before
order/provider I/O; active identity protection, synthetic probe cleanup/retained
bytes, seven healthy boundary retries. Native eight failed confirmations/eight
healthy retries keep QUOTE, generic actionable message, no private path/payment
QR/order until readiness succeeds; existing customer ticket gate then appears.
[Exact commands/source/CI/results/digests/limits](qa/portrait-v2-sandbox/evidence/ux07-final-verification.json).

No runtime defect/change. App/tools Git trees match **347e502**; prior full
1159 run/1155 PASS/4 optional SKIP retains that exact source and excludes the six
new methods, which were separately checked above. No new full/native export or
actual hardware/provider/paper/Drive acceptance is borrowed. Tests/CI/docs only.

**UX-07 whole stronger gate remains NOT_RUN**: purchased-print prepayment path/
actual printer readiness is not mounted/certified in this transport-off Sandbox.
PRINT/DRIVE configuration errors correctly block order creation; that is not
certification of physical print service. Existing read-only printer checks prove
only route/spooler observations, not paper. Preserve Sandbox print/Drive OFF.
Matrix **69 IDs: 58 PASS / 0 FAIL / 9 BLOCKED / 2 NOT_RUN**, audit IN_PROGRESS,
AR-13 conditional. UX-11 NOT_RUN; PAY-22/WEB-01–08 BLOCKED, external gates open.

Next exact increment: **UX-11 frozen worker/GUI evidence audit**. Read supervisor/
native worker, crash lease/restart, privacy and no-replay contracts; test stalled
checkout/upload/QR worker without UI-thread blocking, and living-process hold
without watchdog kill/restart/replay or lost paid rights. Keep hardware/provider/
purchased-printer gates separate and do not redo verified UX-07 components.
This containing docs-only publication is final safe checkpoint; exact SHA from
Git log/remote. Only work/ scratch local, no unpublished runtime patch. No
production/OPS/public ingress/new branch/master/default/deployment/real effects.
Rollback inverse tests/docs; retain all financial/claim/fence/media/audit records.

## 29 October — UX-07.b native confirmation/retry verified

First micro-push `4099ca1a80251c53d45c5b0e6a4b9c25f090ef4a` remote verified;
initial CI 40861858317 pending/superseded, not claimed whole-run PASS.
New native widget method covers low disk, probe permission, actual corrupt
synthetic template bytes and accidental PRINT flag at 800x1280/452x900: eight
failed confirmations and eight healthy deliberate retries. Real app/worker/HTTP/
SQLite remains QUOTE with actionable generic message, no private path/QR/order;
retry creates exactly one order, then existing private-ticket gate appears.
**36 focused PASS / zero failure/error/skip**, 25.080s, Python 3.12.14/Linux
software GL; includes five new boundary methods, one new native method and
existing camera/health checks. Command: `.venv/bin/python tools/run_kiosk_unittests.py test_ux07_readiness test_recovery_readiness test_device_health tests.test_kiosk_v2_sandbox_widgets.SandboxWidgetTests.test_ux07_precharge_faults_show_safe_quote_and_retry_at_both_portrait_sizes tests.test_kiosk_v2_sandbox_widgets.SandboxWidgetTests.test_precharge_camera_failure_keeps_quote_without_creating_any_order`.
No runtime defect/change. App/tools remain 347e502; full 1159/1155/4 retains
original provenance and excludes six new methods. Tests/CI/docs only, no repeat
full/native export. Matching CI pending for this containing micro-push; pure
boundary methods run Windows/Linux, new native method Linux virtual display.
UX-07 stronger purchased-printer gate remains NOT_RUN (not mounted/certified in
transport-off Sandbox), matrix 58/0/9/2 unchanged. Next final current CI/checkpoint
then independent UX-11 frozen-worker/GUI evidence audit. Preserve physical/
provider/production/OPS/release gates. Only work/ scratch local, no unpublished
runtime patch. Rollback tests/docs only; retain financial/claim/fence/media data.

## 29 October — UX-07.a offline prepayment boundary verified

Base/remote verified `858944cf1ef79483892b2c08f07de7d2a5be5a7e`.
Five new HTTP/controller/SQLite methods cover 15 failure vectors (camera 5,
storage/template 7, delivery opt-in 2, expiry during validation 1), plus active
order protection. Rejected readiness creates no visit/order/attempt/provider
I/O; temporary probes cleaned, existing synthetic bytes unchanged, seven healthy
retries each create one order. Active original identity reconciles despite new
bad observations. Sandbox PRINT/DRIVE flags reject before printer probe/order.
**34 focused PASS / zero failure/error/skip**, 2.990s, Python 3.12.14/Linux.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_ux07_readiness test_recovery_readiness test_device_health` (headless SDL/dummy audio).
No runtime defect/change. New module registered in Linux/Windows ledger CI;
matching CI pending for this containing micro-push. Prior full 1159/1155/4 at
347e502 retained, excludes five new methods; no redundant full repeat.
Next native QUOTE/error/no-QR/healthy-retry checks at both portrait sizes, then
final current CI/checkpoint. UX-07 complete stronger gate remains NOT_RUN on
purchased-printer integration/actual acceptance absent from transport-off
Sandbox; verified components will be recorded without a blanket PASS. Matrix
58/0/9/2 unchanged; UX-11 independent validation follows. No production/OPS/
public ingress/branch/master/default/printer/Drive effect. Only work/ scratch
local. Rollback tests/docs only; retain all financial/claim/fence/media records.

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
[Exact sources/commands/tests/CI/hashes/limits](qa/portrait-v2-sandbox/evidence/ux05-final-verification.json).

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
[Exact commands/source/CI/results/digests/limits](qa/portrait-v2-sandbox/evidence/bug023-conflict-http-verification.json).

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
[Exact command/source/results/CI/digests/limits](qa/portrait-v2-sandbox/evidence/bug023-pin-http-verification.json).

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
claim/fence/media records. See [evidence](qa/portrait-v2-sandbox/evidence/bug023-foundation-verification.json) for commands/source/digests/limits.
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
conflicts before restoring UX-13 PASS. See [contract](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).
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
  [Exact source/commands/results/digests/CI/limits](qa/portrait-v2-sandbox/evidence/cap20-final-verification.json).

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
[Exact command/source/digests](qa/portrait-v2-sandbox/evidence/cap20-native-fixture-verification.json).

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
[Exact command/source/digest](qa/portrait-v2-sandbox/evidence/cap20-all-verification.json).

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
skip**, 14.598s, Python 3.12.14/Linux. [Exact command/source/digest](qa/portrait-v2-sandbox/evidence/cap20-jpeg-verification.json).

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
  Overall audit IN_PROGRESS; BUG-023/UX-13 OPEN/FAIL. [Exact evidence](qa/portrait-v2-sandbox/evidence/cap16-final-verification.json).
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
20.830s, Python 3.12.14/Linux. [Command/source/digest](qa/portrait-v2-sandbox/evidence/cap16-composition-verification.json).

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
  Overall audit IN_PROGRESS, BUG-023/UX-13 OPEN/FAIL. [Exact evidence](qa/portrait-v2-sandbox/evidence/cap11-13-final-verification.json).
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
[Command/source/digest](qa/portrait-v2-sandbox/evidence/cap11-verification.json).

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
[Exact source/commands/limits](qa/portrait-v2-sandbox/evidence/pay18-final-verification.json).

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

## 29 October — AR-03.d2 completion/archive process exits

Previous micro-push `3ad80da74da2a0fc3c9d5e3dbe3d84f91a483f4a` remote verified.
**86 focused PASS / zero failure/error/skip**, 22.532s; three PAY-18 methods,
23 real child exits at seven distinct boundaries. New archive exits hold local
COMPLETING after accepted ACK, operation history and lookup index; no new visit
or archive bypass before original proof and durable final journal. Original
three JPEGs/one PNG/manifest/copies/OWED remain unchanged, no repeated effects.
[Command/source/limits](qa/portrait-v2-sandbox/PAY18-SERVICE-REPLIES.md).

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
[Contract/commands/provenance](qa/portrait-v2-sandbox/PAY18-SERVICE-REPLIES.md).

Tests/CI/docs only; no runtime defect or application/schema/UI change. Current
CI pending at this containing test commit. Prior full e0dc594 (1117/1114/3) and
native c94696d (28 PNG/four QR) retain original source; no new full/native result.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**; PAY-18 synthetic PASS,
BUG-023 OPEN, overall audit IN_PROGRESS. Next AR-03.d2 completion/archive exits,
then CAP-11–13, CAP-16 pre-request boundary, CAP-20 and AR-09 denial audit.
External/OPS/production gates unchanged; only disposable work/ local, no
unpublished runtime patch. This containing commit is the next micro-push;
resolve its SHA from Git, push and verify remote before continuing.

## 29 October — AR-03.c CAP-01–05 verified checkpoint

Test/CI `e72e28bdf8b0cbb080ef0c35aa8a1e3906bf55cb` pushed/remote-verified; first micro-push
`c87050eeb4f0223577d68796ff0ace4f4a1d2a95`. **66 focused PASS / zero failure/error/skip**,
5.965s; seven real child exits at six allocation/folder/manifest/STARTED boundaries,
including orphan/no-recency hold. [CI 40815197373](https://github.com/pratikto/PhotoBooth/actions/runs/40815197373)
**all three jobs SUCCESS**, Windows payment/allocation group 55 PASS/zero skip.
Original proof/paid identities/counter/manifest/OWED retained; no repeated effects.
[Exact commands/source/evidence](qa/portrait-v2-sandbox/evidence/cap01-05-final-verification.json).

Tests/CI/docs only; no runtime defect, application/schema/UI change or new full/
native run. Prior full e0dc594 (1117/1114/3) and native c94696d (28/four) remain
separately pinned; the six new methods are verified by focused/CI results.
Matrix **50 PASS / 1 FAIL / 9 BLOCKED / 9 NOT_RUN**; overall audit IN_PROGRESS,
BUG-023 OPEN. Next **PAY-18 combined lost service replies including COMPLETED**,
then remaining retake/COMPLETE/disk and AR-09 denial audit. External/OPS/production
boundaries unchanged; only disposable work/ local, no unpublished runtime patch.
This containing docs commit publishes the final safe continuation checkpoint.


## 29 October — AR-03.c2 CAP-01–05 focused evidence complete

Prior micro-push `c87050eeb4f0223577d68796ff0ace4f4a1d2a95` pushed/remote-verified.
Added folder/pre-manifest, manifest/pre-STARTED and committed STARTED/lost-reply
process exits plus orphan/no-parent-scan denial. **66 focused PASS**, zero
failure/error/skip, 5.965s; seven real exits/six distinct boundaries. Actual
original customer claim and current provider status restore only the same paid
allocation; existing manifest bytes preserved, zero shutter/render/print replay.
[Exact evidence](qa/portrait-v2-sandbox/CAP01-05-ALLOCATION-CRASHES.md).
No runtime defect or runtime/schema/UI change. Matrix **50 PASS / 1 FAIL /
9 BLOCKED / 9 NOT_RUN**, CAP-01–05 synthetic PASS. This containing commit is the
next tested micro-push; CI pending. Prior full/native source results retained,
no new full/device/provider evidence inferred. Next matching CI then PAY-18
combined service-reply faults, retake/COMPLETE/disk and AR-09 BUG-023. External/
OPS gates unchanged; only disposable work/ local, no unpublished runtime patch.


## 29 October — AR-03.c1 CAP-01/02 abrupt allocation evidence

Base/remote verified `c4c1847bd8086c36f3ec1d3a755728896321495f`. Added three
actual child exit boundaries against unchanged runtime e0dc594: before local
intent, before backend request and after committed allocation/lost response.
Authenticated original customer proof, one grant/order/operation/transaction,
WAL/FULL/provider integrity and no repeated charge/counter/media action verified.
**34 focused PASS**, zero failure/error/skip, 2.647s. No runtime defect or source/
schema/UI change. [Contract/evidence](qa/portrait-v2-sandbox/CAP01-05-ALLOCATION-CRASHES.md).
CAP-01/02 synthetic PASS; matrix **47 PASS / 1 FAIL / 9 BLOCKED / 12 NOT_RUN**.
This containing test/workflow/docs commit is the next micro-push; current CI
pending. Existing full/native source evidence stays separately pinned.
Next CAP-03–05 exact folder/first-manifest/accepted STARTED exits. BUG-023/external/
OPS gates unchanged. Only disposable work/ local; no unpublished runtime patch.


## 29 October — AR-02.d PAY-08 verified and remotely checkpointed

Functional `e0dc59435772148be86449c55140d4b9be2f6364`: **1117 run / 1114 PASS /
3 optional palm SKIP / zero failure/error**, 335.317s; native video PASS.
Reader micro-push `52a9a18857580ddcc822fe77cd36af76d489a532`; mounted source e0dc594;
Windows test/setup correction `c94696d243c6a345182857d28d249d2d01d7d05b`, **49 focused PASS**.
[CI 40809459547](https://github.com/pratikto/PhotoBooth/actions/runs/40809459547)
at c94696d **all three jobs SUCCESS**; same application/tools tree as full-run
source, test delta only explicit lease cleanup (full not relabeled). Integration
103 focused PASS; native **28 PNGs / four QR checks PASS**, both portrait sizes,
clean c94696d. Initial Windows qrcode import failure retained in provenance.
[Exact command/source/evidence](qa/portrait-v2-sandbox/evidence/pay08-final-verification.json).

PAY-08 synthetic PASS / AR-AUDIT-002 resolved; matrix **45 PASS / 1 FAIL /
9 BLOCKED / 14 NOT_RUN**, overall audit IN_PROGRESS, **BUG-023 OPEN**.
Next **AR-03 CAP-01–05 exact allocation/STARTED process exits**, PAY-18 lost ACKs,
then remaining media/COMPLETE/disk cases and AR-09 redacted denial audit.
Real OS/device/provider/privacy/retention/operational acceptance stays separate;
no production/OPS/print/Drive activation. Only work/ scratch local; no unpublished
runtime patch. This containing docs checkpoint follows remote-verified c94696d.


## 29 October — AR-02.d3 Windows fixture/CI correction

Mounted e0dc594 pushed/remote verified; full **1117 run / 1114 PASS / 3 optional
palm SKIP / zero failure/error**, 335.317s. Windows CI 40808591124 fails at fixture
import (qrcode missing, 43 run / 1 ERROR); independent 61-case recovery step PASS.
This containing increment adds the missing Windows QR dependency and explicitly
closes the direct-use current flow before temp cleanup. **49 focused PASS**,
zero failure/error/skip, 1.389s. Runtime/assertions unchanged; prior full retains
exact e0dc594 test tree, newer test/CI revision verified separately.
[Failure/command/evidence](qa/portrait-v2-sandbox/PAY08-CONNECTIVITY.md).
Next: verify new CI, clean native captures/QRs, publish final source checkpoint;
then AR-03 CAP-01–05. Matrix 45 PASS / 1 FAIL / 9 BLOCKED / 14 NOT_RUN. BUG-023,
external and OPS gates unchanged. No unpublished runtime patch, only work/ local.


## 29 October — AR-02.d2 connectivity recovery mounted, focused PASS

Previous reader micro-push `52a9a18857580ddcc822fe77cd36af76d489a532` pushed/remote-verified.
Native known-order recovery now coalesces OS offline→online on the existing
single worker and immediately requests same-order read-only reconciliation;
backend persisted priority/lease still bounds GET. No refresh/claim follows in
that iteration; ownership/media/service remain held. **103 focused PASS**,
zero failure/error/skip, 39.392s. Test-first integrated run: 7 run, 3 FAIL/3 ERROR.
[Contract/command/source evidence](qa/portrait-v2-sandbox/PAY08-CONNECTIVITY.md).
This containing functional commit is the mounted source; final full/CI PENDING.
PAY-08 synthetic PASS / AR-AUDIT-002 resolved; matrix **45 PASS / 1 FAIL /
9 BLOCKED / 14 NOT_RUN**, BUG-023 and physical/provider/OPS gates unchanged.
No schema/journal migration or new layout; unknown OS hint retains bounded polls.
Next: final full/matching CI at pushed source, then AR-03 CAP-01–05 crash fixtures.
Only disposable work/ local; scoped inverse retains every order/claim/media/fence.


## 29 October — AR-02.d1 passive connectivity reader checkpoint

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


## 29 October — verified AR audit checkpoint at 4642841

**Functional `4642841f3e99d8c74b4b379e24922a7ba3f614c9`**, pushed/remote-verified. Full
**1,100 run / 1,097 PASS / 3 optional palm SKIP / zero failure/error**, 364.124s;
native video PASS, GUI/audio/video opt-ins, Python 3.12.14/Debian 13.6/offscreen/
dummy audio. Matching [CI 40790865010](https://github.com/pratikto/PhotoBooth/actions/runs/40790865010)
**all three jobs SUCCESS**, including Windows payment/reconstruction cases.
[Exact command/source/digests](qa/portrait-v2-sandbox/evidence/ar-audit-final-verification.json).
Payment micro-push 8ebcd12: 116 focused PASS; BUG-022 fix 4642841: 61 focused PASS;
source audit/docs 5d318f8 pinned. No new local native/physical evidence inferred.

BUG-022 fixed/verified; **BUG-023 OPEN**, no durable wrong-PIN denial audit (UX-13
FAIL), and native connectivity-restored producer absent (PAY-08 NOT_RUN).
Matrix **44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN**. First source pass read;
overall audit **IN_PROGRESS**, no blanket conformity/unattended release verdict.
Next: AR-02 bounded native connectivity event/fixture, AR-03 exact allocation/
STARTED faults, remaining service/media cases, AR-09 redacted denial audit.
External gates/OPS NOT_STARTED unchanged. Current containing docs publication
pins the safe handover; only disposable work/ local, no unpublished runtime patch.


## 29 October — AR source audit first pass and corrected denial verdict

Functional `4642841f3e99d8c74b4b379e24922a7ba3f614c9` pushed and remote HEAD verified. Payment
8ebcd12: 116 focused PASS; BUG-022 correction: 61 focused PASS. Bounded source
pass now covers AR-00–13. **BUG-023 OPEN**: wrong-PIN requests are rejected/rate-
limited but lack durable denial audit; UX-13 corrected from PASS to **FAIL**.
Operator rate budget is process-local, customer ticket budget separately durable.
Native connectivity-restored producer is absent (AR-AUDIT-002/PAY-08 NOT_RUN).
Current matrix **44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN**; no blanket conformity
verdict. [Findings/probe](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md#increment-4--nativeoperational-source-pass-and-remaining-findings).

Full regression at 4642841 running; CI 40790865010 pure/Windows SUCCESS, desktop
still running. Superseded 40790391324 CANCELLED by concurrency. Finish both and
pin actual results, then dependency-ordered PAY-08/CAP-01–05 fault evidence and
AR-09 denial audit. External/device/production gates unchanged, OPS NOT_STARTED.
This containing docs checkpoint preserves exact source/findings; only disposable
work/ diagnostics local, no unpublished runtime patch.


## 29 October — AR audit BUG-022: hold missing committed output before restore

Payment audit `8ebcd123098fe5a937c59f2b88d7fe60c9bedf7b` pushed/remote-verified,
116 focused PASS; PAY-06/PAY-21 closed as synthetic evidence gaps. Matrix now
45 PASS / 9 BLOCKED / 15 NOT_RUN. Subsequent source review confirmed **BUG-022**:
missing COMMITTED PNG was accepted by inspection; restore installed state before
FileNotFoundError. Corrected validation holds before installation, preserves
originals/manifest/OWED and performs no rerender/print or payment mutation.
New test first reproduced 2 FAIL/1 ERROR in a 14-case run; **61 focused PASS**
after correction, zero failures/errors/skips (39.146s). This containing commit
is the functional correction; final full regression and matching CI PENDING.
[Review and exact evidence](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md#increment-3--confirmed-missing-output-reconstruction-defect-bug-022).
Audit IN_PROGRESS; no production/OPS/deployment. Previous f72fdbc full/native
results remain historical. Next: full regression at pushed correction and remaining
native/privacy/operator/launcher review, then exact remaining matrix faults.
Only disposable `work/` local; no unpushed runtime patch after publication.


## 29 October — AR audit increment 2: exact payment crash/provider evidence

Remote base `647991ec013e75477c5c8564133beb68947984f4`; application runtime unchanged at
`f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`. Reviewed payment/store/API/provider/
release paths against current AR contracts; no confirmed runtime defect in this
bounded review, no full conformity verdict. Added PAY-06 real child pre-commit
crashes and PAY-21 oversized/auth-failure redacted holds. **116 focused PASS /
zero failures/errors/skips**, 1.977s; matrix **45 PASS / 9 BLOCKED / 15 NOT_RUN**.
[Test command/hashes](qa/portrait-v2-sandbox/evidence/ar-audit-payment.json).
Windows CI now includes reconciliation module; CI pending at publication.
No new full regression/screenshots; previous full 1097/1093/4 remains pinned to
f72fdbc. This containing commit publishes tests/workflow/docs; exact pushed SHA
will be pinned in the next checkpoint after remote verification.

Next: allocation/STARTED/COMPLETE and media reconstruction source review plus
CAP-01–05 exact fault sequences; PAY-08/PAY-18 still open. Then remaining privacy,
operator and supervisor review. Audit IN_PROGRESS; external gates/CONDITIONAL
readiness retained. No OPS or production/print/Drive activation, no migration.
Only disposable `work/` local; no unpublished runtime patch. Scoped rollback of
these tests/workflow/docs preserves all customer records and media.


## 29 October — documentation status cross-check (no runtime change)

Remote baseline be0efae / functional f72fdbc reconciled. Current docs correctly
place development at AR-13 readiness **CONDITIONAL**, with 1097 run / 1093 PASS /
4 SKIP and CI 40767441201 all three jobs SUCCESS. Recorded application/test/tools/
workflow tree IDs match current HEAD. Conformity audit still IN_PROGRESS; matrix
43 PASS / 9 BLOCKED / 17 NOT_RUN and PAY-06 next remain authoritative.
Recovered original historical 635de92 report has 1094 / 1091 PASS / 3 SKIP; its
SHA-256 plus 276 Git-object source hashes check out. [Provenance supplement](qa/portrait-v2-sandbox/evidence/historical-635de92-provenance.json)
keeps that older run separate. No new full suite/runtime/OPS/production change.
Only disposable work/ remains untracked. Continue the active AR review/exact
fault gaps, not previously completed stages; do not start queued Settings work.

## 29 October — AR-00–13 code review checkpoint 1 (IN_PROGRESS)

Owner requests a fresh implementation-versus-specification review and staged
pushes. Remote/local f8167d8 reconciled; runtime/test source stays f72fdbc.
Recorded source-tree IDs, final raw-report digest/counts, ten published screenshot
hashes and 69 unique matrix IDs checked successfully. This is evidence integrity,
not a blanket code-conformity finding or new test/acceptance result.
[Review record and next action](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md).
Next: complete all stage reviews and publish only confirmed synthetic reproductions
with exact source locations. Runtime unchanged; `work/` scratch only remains local.
AR remains top priority; OPS NOT_STARTED; no production/deployment/master changes.

## 29 October — final AR-12 source evidence and AR-13 readiness

Final runtime/test `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`: **1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors**, 428.924s, Python 3.12.14 / Debian 13.6,
GUI/audio opt-ins with offscreen software GL/dummy audio, tracked tree clean.
[CI 40767441201](https://github.com/pratikto/PhotoBooth/actions/runs/40767441201):
all three jobs SUCCESS at matching source. Native 28 PNGs/both portrait sizes,
four QR checks PASS; payloads private. Previous-session 1094/1091/3 log unavailable;
this is a new independently captured result. Matrix 43 PASS / 0 FAIL / 0 SKIP /
9 BLOCKED / 17 NOT_RUN; exact missing fault windows are not credited as PASS.

[AR-13 assessment](qa/portrait-v2-sandbox/AR13-READINESS.md): **CONDITIONAL** for
controlled acceptance; **NOT READY for unattended commercial release**. Device,
merchant, phone/paper/Drive/deletion, privacy/remedy/operations and owner approval
remain open. First unfinished source-evidence task: PAY-06 abrupt exit between
provider evidence and DB commit, then remaining matrix gaps. AR stays top priority;
all future Settings/Emulate Ticket/QRIS Slip implementation stays NOT_STARTED.
[Exact command/skips/provenance](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md) ·
[checkpoint/next action](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 29 October — AR-12.f recovery scanner false negatives

CI 40766621706 at pushed `9592649` passes content/Windows but fails Linux's native
recovery scan claim assertion. Ten of 100 random synthetic QR matrices fail the
primary OpenCV detector locally; installed alternate recovers all ten. Add only
one optional alternate decode on empty primary output, then keep original
customer proof. Foreign QR, missing alternate and undecodable frames fail closed.
Test-first scanner group: 3 run / 1 ERROR before source. Focused final results
are recorded in validation; exact next action is final full regression and fresh
native/CI evidence at this scanner commit, followed by matrix/AR-13 assessment.
Interim 9592649 full run stopped, no final count. `work/` contains only private
synthetic diagnostics; no customer/merchant data, OPS or deployment changed.

## 29 October — AR-12.e verified CI history and deterministic content fixture

Baseline `e303cdf4db3f009d2f4ed1a075e160d17aaa8bdb` refreshed/fast-forwarded cleanly.
Latest runtime `635de92`; three successful jobs at CI `40756922129` / `b5931c8`.
Linux failed the content-priority test at `content.pending`, not an identified
photo renderer failure. Mock monotonic 1.0 reproduces that assertion; 100.0 passes.
Historical runner clock unknown. Set that fixture's clock explicitly; unchanged
runtime/assertions. Focused **33 PASS / zero failures/errors/skips**, 2.543s.
Next: final full run at this test commit, native manifest/QR checks, full matrix
classification and AR-13 conditional acceptance/readiness report. Previous
1094/1091/3 raw log unavailable here; never invent its provenance. Disposable
`work/` only local; no unpushed runtime changes or customer state. External
Windows/Ubuntu/merchant/paper/Drive gates stay open; OPS NOT_STARTED.
Detailed [investigation](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).

## 29 October — owner-approved future Operator Settings package (DOCS ONLY; AFTER AR-13 priority)

**Do not switch implementation from current AR-00 → AR-13 recovery work to OPS.** Continue the first unfinished safe AR micro-increment recorded in the [live checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md), latest commits and the stage-specific handover below; do not trust historical stale stage headings. AR-12/AR-13 validation, explicit readiness, merchant/device NOT_RUN gates and separate release approval remain higher priority. This paragraph records a **queued follow-up**, not a completed feature or changed AR plan.

The owner explicitly approved the entire discussed **Meong Settings** design for future GUI v2 work: hidden F12/1.5-second Meong hold at first Advertising **AND SAFE_IDLE** → camera-based **static per-booth Operator QR Login** → three tabs **Device Health, Audio Settings, Emulate Ticket** → logout/return to Advertising. Preserve AR-09 Recovery exception and separate operator PIN, OS maintenance fallback, privacy/camera exclusivity. Audio includes Master, Music, Button SFX, Other SFX, Mute/Test, persistent per booth. **Emulate Ticket** (the final name replacing Ticket Master) provides static reusable MOCK-only QR presets for Merchant Promo and Meong Fly, with true per-visit consumption/Already Used validation, print preview/80-mm thermal, honest uncertain-print handling and safe history; real payment/Sandbox printer/Drive restrictions unchanged. Dynamic operator/game/merchant QR is an operational-phase future design, not the current implementation.

**Codex-authoritative new documents:** [full master spec](qa/portrait-v2-operator-settings/README.md) · [OPS-00..OPS-10 post-AR roadmap](qa/portrait-v2-operator-settings/IMPLEMENTATION-ROADMAP.md) · [129-case acceptance matrix](qa/portrait-v2-operator-settings/ACCEPTANCE-MATRIX.md) · [50 decisions/supersessions](qa/portrait-v2-operator-settings/DECISION-REGISTER.md) · [copy/paste handover prompt](qa/portrait-v2-operator-settings/CODEX-HANDOVER.md). **OPS code NOT_STARTED; OPS tests NOT_RUN; physical/device evidence NOT_RUN.** This documentation commit does not reverify any old functional source or imply production payment, merge or deployment. Continue using small independently checked commits + immediate pushes on existing `feature/portrait-kiosk-v2-next`, and publish exact remote HEAD to survive the 5-hour usage limit.


## 29 October — AR-12.d: retain Windows pass and expose Linux isolated-photo failure details

Base / last remote-verified commit `635de92c0f8fba9189981ebf2f168bff8b7a52af`. CI 40756011109 Windows autonomous/native and pure jobs PASS; desktop P3 group FAIL with unknown cause. Failure-only report annotation added, no assertions/application changes. Final local full rerun still running.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, unclaimed private
photo display or customer state reset. Next: Inspect precise Linux P3 failure, fix only proven cause, verify final complete local regression and matching three-job CI, then publish AR-13 readiness.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).

## 29 October — AR-12.c: correct Windows PNG fsync and verify real output crash boundaries

Base / last remote-verified commit `cfacc18370559f4eddc44bda1c0a12572f89b5b3`. First full local run 1093 run/1090 PASS/3 optional palm SKIP; Windows CI revealed read-only fsync Errno 9. Fixed non-truncating writable descriptor, added four output child-exit boundaries, retained all assertions; focused outcome recorded in validation.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, unclaimed private
photo display or customer state reset. Next: Push fixed source, repeat full regression because runtime changed, regenerate pinned native evidence, verify Windows and Linux CI, then finish AR-13 readiness/blocked production decision.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).

## 29 October — AR-12.b: expose Windows autonomous test failures without changing assertions

Base / last remote-verified commit `09788b1cd18c1dcf4be2357693543323103e2816`. Pinned source 09788b1 native 28 PNG captures and four QR checks PASS; local full suite running. Initial Windows autonomous CI FAIL, underlying case unavailable because log-storage host is network-denied; diagnostic annotation added.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, unclaimed private
photo display or customer state reset. Next: Inspect failure-first Windows annotation, correct actual portable issue and reverify; finish full local run, final CI and AR-13 readiness document.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).

## 29 October — AR-12.a: close final archive binding and WAL fault gaps before full regression

Base / last remote-verified commit `f502bbf8adb3ed73f8f7388903f50a860e633152`. Focused 57 PASS, then final durability/core 25 PASS, zero failures/errors/skips. Actual child os._exit, WAL integrity and locked writer checked; Windows recovery CI and release/return renderer extended.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, unclaimed private
photo display or customer state reset. Next: Run one complete regression at this final functional source; capture/decode native 800x1280 and 452x900; inspect matching Linux/Windows CI; map remaining external gates and publish AR-13 readiness decision.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).

## 29 October — AR-11: design public webhook boundary and verify unmounted durable inbox prototype

Base / last remote-verified commit `57048882609bfeb6ff0b315dce244934a77959ce`. Focused 38 PASS, zero failures/errors/skips; no public listener, runtime mount, merchant callback, deployment or BI-SNAP migration. Infrastructure gates remain explicitly unapproved/NOT_RUN.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, unclaimed private
photo display or customer state reset. Next: AR-12 fault-matrix gap checks, final functional regression, pinned native captures and Windows CI evidence; AR-13 production readiness/owner release gates after validation.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-WEBHOOK.md).

## 29 October — AR-10: bound opt-in exited-GUI recovery with durable budget and original leases

Base / last remote-verified commit `a7f4dfdd087b47fa7a87e4e2c64bdb0a1ec42ddc`. Focused 93 PASS, zero failures/errors/skips; no live-process kill or automatic business effect, three restarts/ten minutes only with isolated Sandbox and released leases.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, unclaimed private
photo display or customer state reset. Next: AR-11 secure public-backend design and opt-in offline inbox/adapter tests without infrastructure deployment, then AR-12 final validation and AR-13 readiness decision gates.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-SUPERVISOR.md).

## 29 October — AR-09.c5: mount deliberate isolated booth release and original customer return

Base / last remote-verified commit `f9aaaa2c5c39c6a1168cb1f72bb3c3b01919bcc7`. Focused 47 PASS plus four isolation PASS, zero failures/errors/skips. Native two-step PIN release waits for local receipt and server ACK; original one-photo session returns without another charge; uncertain printing stays held.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-10 bounded opt-in supervisor after proven child exit, preserving default observer and business isolation; AR-11 design/offline fixture boundary, AR-12 final matrix/regression/evidence, AR-13 readiness gates.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-09.c4: persist worker isolation and exact archived customer recovery

Base / last remote-verified commit `f341b1154034cbf7d609b5df3d38960cb73ae82e`. Focused 37 PASS, zero failures/errors/skips; real HTTP and synthetic photo release/new visit/return preserves original bytes, grant and capture count; lost ACK repeats persisted IDs.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.c5 mount deliberate native two-step PIN release, isolated-worker ACK and returning-ticket entry; then AR-10–13.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-09.c3: authenticate two-phase release and require current service fencing tokens

Base / last remote-verified commit `51ab21c25340856de1218dd54b5bb26486869fc3`. Focused 58 PASS, zero failures/errors/skips; operator HTTP release and reacquired current-token service covered. No native release control yet.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.c4 durable local release intent/isolation/archive and exact returning-customer lookup, then native worker-stop and release ACK flow; AR-10–13 follow.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-09.c2: preserve paid rights through two-phase occupancy release and exact reacquisition

Base / last remote-verified commit `e52f143b07a6511c4e7eda30ad5b16b55628e896`. Focused 48 PASS, zero failures/errors/skips; prepare/ACK/restart/replay and original proof/new-token/free-booth invariants covered. Core internal seam only, no release endpoint/UI yet.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.c3 authenticated release API and token-aware service calls, then durable local worker-stop/archive/returning-customer native flow; AR-10–13 afterwards.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — published safe checkpoint through AR-09.c1

Exact tested/pushed functional source `b38e030d2a8586f2de61dd96e8b4a590e85dde54`; remote HEAD verified.
AR-07 native customer recovery and AR-08 readiness/paid remedy source increments
are locally verified. AR-09 PIN launcher/inspection and dormant service fencing
are locally verified; safe release/reacquisition remains unfinished. Latest 86
focused PASS, zero FAIL/ERROR/SKIP. Final full suite deferred; CI pending, external
Windows/Ubuntu/merchant/paper/Drive NOT_RUN. No production or release enabled.
[Ten commits, exact tests, blockers and continuation](qa/portrait-v2-sandbox/CONTINUATION-2026-10-29.md).
Next: AR-09.c2 two-phase audited release, token-aware service API, worker-stop ACK
and exact returning-customer lookup. Then AR-10–13. Tracked source clean before
this docs checkpoint; only disposable work/ local, no unpushed runtime patch.
Do not redo published work. Documentation checkpoint's own SHA is git HEAD.

## 29 October — AR-09.c1: fence stale service workers before implementing safe booth release

Base / last remote-verified commit `ed1612bd8f35d785d8c617db1343f9a0fc396f33`. Focused 86 PASS, zero failures/errors/skips; five migration/CAS/restart/race cases. Dormant internal seam only; no UI/API rotates fences and no booth release is enabled.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.c2 implement two-phase audited suspend/release and token-aware service API, then archived exact returning-customer reacquisition and native worker-stop/ACK; AR-10–13 remain pending.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-09.b: mount PIN-protected native operator metadata inspection

Base / last remote-verified commit `cc6032c6556dbe4fcd2f26f8a32d9b611b948ed6`. Focused 64 PASS, zero failures/errors/skips; wrong/missing/correct PIN, private media denial, journal secrecy and retired callbacks covered. Twenty provisional native PNG fixtures rendered at both required sizes.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.c define and implement audited fenced suspend/release plus returning-customer lookup without losing OWED or allowing stale worker effects; then AR-10–13.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-09.a: isolate a per-launch Sandbox operator PIN from the GUI

Base / last remote-verified commit `4e4f95b8396f585966c9e98e9fb7ebd3f06bb28e`. Focused 64 PASS, zero failures/errors/skips; backend-only PIN and mocked launcher argv/environment/local-notice isolation covered.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.b native operator PIN entry/metadata inspection, then audited fenced suspension/release without losing OWED or exposing previous photos; AR-10–13 pending.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-08.b2: record native postpaid faults with durable same-operation retries

Base / last remote-verified commit `e84af128d296e4acae37132569e09f3f2da14049`. Focused 58 PASS, zero failures/errors/skips; postpaid missing-camera, capture I/O failure and lost-ACK/restart fixtures preserve payment, OWED, manifest and one issue operation.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09 integrate separate operator PIN launcher/UI and safe fenced suspension/release; AR-10 bounded restart, AR-11 design/opt-in fixtures, AR-12 validation and AR-13 release gates remain.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).

## 29 October — AR-08.b1: persist paid-unfulfilled issues without altering customer financial rights

Base / last remote-verified commit `4863aa3009d1c23e0b710ea9340db6a931a19623`. Focused 56 PASS, zero failures/errors/skips; five new durable/concurrent/migration/authenticated HTTP issue cases; CI registration included.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-08.b2 persist local reporting intent before API I/O, retry after restart and route native camera/photo faults into the ledger; then AR-09–13.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).

## 29 October — AR-08.a: gate native new payment on camera storage and template readiness

Base / last remote-verified commit `d65fb97c7244d7aff8b0242d060a7de7c072bde1`. Focused 57 PASS, zero failures/errors/skips; offline readiness and native no-camera/no-order gates covered; new module registered in CI.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-08.b durable idempotent paid-unfulfilled issue ledger/API and native postpaid fault reporting; then AR-09–13.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).

## 29 October — AR-07.b4: recover original pre-manifest allocation without creating another session

Base / last remote-verified commit `0745f754288d4ef58e07b93685209d619c796005`. Focused 42 PASS, zero failures/errors/skips; original RESERVED empty allocation recovery and STARTED/orphan denial covered in photo and native HTTP fixtures.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-08 prepayment camera/storage/template readiness and durable paid-unfulfilled remedy; then AR-09–13 in dependency order.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.b3: mount native ticket claim and customer-led exact photo recovery

Base / last remote-verified commit `7cedee5b0145720c9f1eaee04ab57ca8b183ec9c`. Focused 46 PASS, zero failures/errors/skips; native HTTP-to-photo restore, cached-camera ticket decode, minimize/idle privacy and input-preserving polling covered. Sixteen provisional fixture PNGs rendered at both target sizes.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: Finish AR-07 interrupted pre-manifest allocation handling and extra stale-callback/reboot fixtures, then AR-08 prepayment readiness and durable paid-unfulfilled remedy; AR-09–13 still pending.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.b2: hide private photo snapshots and fence reconstruction after lock

Base / last remote-verified commit `61571841786f5109f866157fe68e4c479d5c710f`. Focused 35 PASS, zero failures/errors/skips, including same-session reclaim and lock-during-reconstruction fixtures.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.b3 mount ticket claim/scan, exact restore and original ACK in native UI; wire minimize/60-second idle lock with stale callback guards.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.b1: revoke stale permits and acknowledge exact resumed service

Base / last remote-verified commit `6d53d91fcfcad6083aee9f17ac8f80cf635fdf2f`. Focused 37 PASS, zero failures/errors/skips; three added session cases cover privacy revocation, original STARTED acknowledgment/current refund and completed-result-only restore.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.b2 mount customer ticket input/scan and exact photo restore; add minimize/inactivity privacy lock and late native callback guards.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.a: native save-ticket gate and neutral privacy-held screen

Base / last remote-verified commit `064bf384f46a10eb9cf3d25cf94462feb463b626`. Two new native gates and focused 37 PASS, zero failures/errors/skips. Twelve native working-tree captures rendered at 800x1280/452x900; both recovery-ticket screenshot QR payloads decode correctly without logging secrets. Payment URL/copy actions remain hidden until ticket acknowledgment.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.b customer ticket input/scan, exact restore/STARTED handoff, inactivity/minimize lock and late-callback guards.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-06.b: memory-only customer ticket and trusted claim controller

Base / last remote-verified commit `c10998cace1c869139f17b55796ff3367e992054`. Six new session cases; focused 92 PASS, zero failures/errors/skips, including native Sandbox compatibility. Raw ticket never enters journal/backend views; restart requires original proof. Current settlement is rechecked at resume action, pending proof never issues media permission, and privacy generation rejects late callbacks.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.a native save-ticket gate before payment QR, then claim/scan/resume and privacy-lock integration.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).

## 29 October — AR-06.a: hashed customer capability and current-payment redemption

Base / last remote-verified commit `adf87496479d4647b8248e8880acf691e87f8e38`. Eight new customer-proof cases and focused 137 PASS, zero failures/errors/skips. Additive capability binding is atomic with order; only SHA-256 persists. Expiry, durable attempt budget, one-use action replay and fresh settlement gate protect redemption without operator privilege bypass.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-06.b original-process ticket generation and private controller authorization; then native customer recovery AR-07.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).

## 29 October — AR-05.b: exact private photo reconstruction behind one-use in-memory permit

Base / last remote-verified commit `3c04e31f56e5ed7e4fc30c971fc7ead28e1cc446`. Nine new reconstruction cases pass; focused 63 PASS plus nine final guard checks, zero failures/errors/skips. Restores partial shots, selected/used retake, staged captures/PNG and multi-design copies without new IDs, shutter, renderer or print. No old media is returned without a bound ephemeral permit; UI mounting remains disabled until AR-06/07.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-06.a hashed customer capability, expiry/action CAS/rate limiting and fresh-payment redeem API.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).

## 28 October — AR-05.a: immutable strip publication with frozen input hashes

Base / last remote-verified commit `879d69bf4553e84befb21705033d9eb84759b571`. Three new output cases; focused 71 PASS, zero failures/errors/skips, including native handoff, capture, delivery and v1 retention/workflow. PNG intent and input identities persist before rendering; published-but-unacknowledged output cannot be overwritten on retry.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-05.b exact metadata/intent reconstruction behind an ephemeral resume permit; then AR-06 customer capability.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).

## 28 October — AR-04.a: write-ahead immutable JPEG capture and atomic retake quota

Base / last remote-verified commit `075e97319762cfd73a089b444340fcf0eb2deb36`. Seven new capture cases, five abrupt process boundaries, and focused 73 PASS, zero failures/errors/skips. V2 opts in; v1 writer defaults unchanged. Existing/orphan JPEGs cannot be overwritten; retake selection/quota commit with saved bytes. Native Sandbox and retention checks pass.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-05.a output publication and deterministic manifest/intent reconstruction; customer disclosure stays gated until AR-06.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CAPTURE.md).

## 28 October — AR-03.b: unique allocation before local photo creation

Base / last remote-verified commit `4e0dadee16c3596d7575ee2ce2ed32a43bc0b7cf`. Focused 204 PASS, zero failures/errors/skips, including native HTTP-to-photo handoff, allocation replay/restart, initial binding, v1 workflow and retention. Server atomically assigns one PB001V2AR-style transaction before any folder creation; exact initial manifest binds original payment/permit.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-04.a write-ahead immutable capture intents and crash-boundary tests; then photo reconstruction AR-05.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).

## 28 October — AR-03.a: frozen order contract and independent fulfillment obligation

Base / last remote-verified commit `30ebd0bad394046f99286b0f0f90785cb9e12161`. Six new fixtures and focused 133 PASS, zero failures/errors/skips. New orders freeze server pricing/template hashes before I/O; payment creates an owed fulfillment independently of UI claims. Legacy duplicate bindings quarantine both mappings without altering original evidence.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-03.b unique allocation operation and preallocated local transaction, then native handoff.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).

## 28 October — AR-02.c: private restart observation and recovery worker retry

Base / last remote-verified commit `949d8e35c44f92d9a22c852df81dd3527ee041c6`. Focused 152 PASS, zero failures/errors/skips, including native Sandbox lifecycle. Four new restart tests and persisted priority-trigger test pass; RECOVERY retains original phase, grant and transaction and never resumes capture.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-03.a frozen quote/template contract and additive fulfillment/allocation migration tests.
Only work/ scratch files local; scope and rollback in
[AR-02 contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).

## 28 October — AR-02.b: durable bounded reconciliation scheduling and fencing

Base / last remote-verified commit `877268f46d7360e4a6e3ef021862d93103d07f00`. Focused 126 PASS, zero failures/errors/skips. Fifteen new AR-02 cases cover cached evidence, concurrent workers, jittered backoff, stale responses, additive schema and clock rollback.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-02.c restart and existing RECOVERY observations without photo reentry, then AR-03 immutable fulfillment/allocation ledger.
Only work/ scratch files local; scope and rollback in
[AR-02 contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).

## 28 October — AR-02.a: fresh payment observation and admission guard

Base / last remote-verified commit `6339d13817a74fcaf8c0ae3d76d9b73e73e2ed5c`. Nine new cases; focused 120 PASS, zero failures/errors/skips. Backend-only provider GET observation requires booth authentication; operator mutation remains PIN-gated. Cached PAID cannot authorize claim/STARTED without fresh settlement.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-02.b durable per-order reservation, bounded backoff and stale-reply fencing tests/implementation.
Only work/ scratch files local; scope and rollback in
[AR-02 contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).

## 28 October — final verified AR-00/AR-01 handover

Latest functional source pushed and remote verified: `017b417d02d63a79b1c5b21c4f0613b7d15186fc`.
AR-00.a/b contract/baseline and AR-01.a/b attempt durability are implemented and
verified automatically. Focused **132 PASS / zero skips**; final complete local
**968 run / 965 PASS / 3 SKIP / zero failures/errors**, at that exact source. Optional skips require
external palm assets. Matching [CI 40688374416](https://github.com/pratikto/PhotoBooth/actions/runs/40688374416)
completed **all three jobs SUCCESS**, including Windows creation fixtures.
No actual merchant/Windows/Ubuntu hardware, paper/Drive/retention acceptance.

First unfinished step **AR-02.a**: deterministic tests for narrow booth-authenticated
fresh reconciliation of cached PAID/refund/offline, separate from operator resolve;
then rate-limited/backoff implementation. Read current checkpoint/source before
continuing. Do not repeat AR-00/AR-01 or enable repeat POST: Legacy provider
resend contract is still BLOCKED. AR-02–13 remain unfinished; new recovery GUI,
photo reconstruction, customer capability and unattended pilot are not delivered.
All source/tests and required evidence are on GitHub. Only disposable work/
scratch files remain local. [Checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md)
contains rollback/data preservation and [evidence](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md).
This final safe companion checkpoint is documentation-only; no extra GUI rerun.

## 28 October — AR-01 creation-attempt durability

AR-00 pushed/remote verified at `4261236694358c2f3cd2a475a4cd9cd82f436e00`.
AR-01.a/b adds a backend-only additive attempt ledger with frozen request and
merchant/mode binding before provider I/O; uncertain creation never retries POST.
Nine new attempt/migration tests plus baseline/protocol/HTTP group: **132 PASS,
zero failures/errors/skips** on Linux/Python 3.12.14. Initial failing tests are
recorded. Full regression/CI pending at this code checkpoint; source SHA will be
pinned after push. [AR-01 contract/evidence](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md)
and [latest checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).
Next: full validation, then AR-02.a fresh reconciliation tests. Legacy repeat-charge
contract remains BLOCKED; independent stages may proceed without enabling resend.
Only work/ scratch files local; no customer data/credentials or unsafe WIP pushed.

## 28 October — AR-00 contract and crash-fixture checkpoint

Current owner continuation authorizes dependency-ordered AR work with immediate
safe pushes. Refreshed existing branch from clean remote
`f6736b7c739e3317e3bcc4506edb250f9e47d92b`; no new remote branch or master change.
AR-00.a/b freezes the actual schema/state/legacy fallback contract and adds six
offline characterization cases, including abrupt subprocess exit/reopen of WAL.
Focused suite **87 PASS / zero failures/errors/skips** on Linux/Python 3.12.14.
Runtime source unchanged; full/device/merchant checks NOT_RUN. Exact command,
changed scope, rollback and first unfinished AR-01.a are in the
[checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md) and
[baseline contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-BASELINE.md).
Companion publication will pin the exact pushed AR-00 commit. Only scratch files
under work/ are local; no unpushed runtime work. Provider repeat-charge contract
remains open; no speculative resend/header or production activation.

## 28 October — owner preference: push in small increments for five-hour continuity

The owner explicitly asks Codex to **commit and push safe, tested
micro-increments continuously** rather than accumulating changes until a long
ChatGPT/Codex session finishes. Continue from remote-verified Git history
without redoing completed work after the five-hour limit. Follow
[checkpoint and resume instructions](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md),
[AR roadmap](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md)
and [development prompt](DEVELOPMENT_PROMPT.md). Each checkpoint must record
the last verified remote SHA, completed vs pending substeps, test evidence,
blockers and any explicitly **unpushed** local changes. Never push unsafe
source or sensitive values solely to manufacture a checkpoint. **No runtime
recovery implementation or new test verification is claimed by this change.**

## 28 October — autonomous recovery master design and Codex handover (no runtime changes)

Authoritative planning entrypoint: [Master](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-MASTER-PLAN.md), [Codex stages AR-00–AR-13](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md), [official Midtrans contract and open verification](qa/portrait-v2-sandbox/MIDTRANS-PROVIDER-CONTRACT.md), [fault-injection test matrix](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-TEST-MATRIX.md), [operator/customer runbook](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATIONS.md). This documentation-only increment preserves the existing operator-first backend source; target policy is unattended-first when provider/payment, photo identity and customer ownership are independently proven. Five-minute invoice idempotency does **not** establish the same TTL/header for Legacy `/v2/charge`. No implementation, fixtures, live merchant or physical tests were run for the new plan. Codex must refresh remote HEAD and start at AR-00 on `feature/portrait-kiosk-v2-next`. No new branch or master merge.


## 28 October — Sandbox GUI link for the web simulator

Owner requests a GUI action to copy the current QRIS link for pasting into
Midtrans's simulator, keeping the existing branch. Source `39e8c32` adds
**SALIN LINK QRIS** and feedback using native widgets/Clipboard and the shared
URL validator. Backend/payment authority is unchanged. Exact checks and device
limits: [copy-link runbook](qa/portrait-v2-sandbox/COPY-LINK.md).

## 28 October — BUG-021 pending QR polling

Owner confirms image-only disappearance on the Sandbox page, with no duration
or status text. Reproduced pending action-URL overwrite and native image loss.
The shared backend now retains/revalidates saved URLs when actions are omitted;
no new order, endpoint guessing or relaxed payment guards. Source `4237d3f`:
182 focused PASS; full 933 run / 930 PASS / 3 optional palm SKIP / zero
failures/errors; CI 40614355442 all three jobs SUCCESS. Ten exact-source native
PNGs and two screenshot QR decodes verified; device limits/update in the
[runbook](qa/portrait-v2-sandbox/QR-POLLING.md).

## 28 October — centered Meong logo on Sandbox QR

Owner requests reuse of the Drive QR logo. The v2 adapter now calls that exact
renderer with locally decoded provider data, checks equivalence and retains
original pixels on failure. Renderer algorithm/artwork, download URL and payment
authority are unchanged. Source `8ed6f11`: 175 focused PASS; final full 926 run /
923 PASS / 3 optional palm-assets SKIP / zero failures/errors, 290.905s.
Matching CI 40610731638 all three jobs SUCCESS; 15 exact-source native PNGs and
three screenshot QR decodes. [Evidence/update](qa/portrait-v2-sandbox/QR-LOGO.md).

## 28 October — saved Sandbox credentials

Owner requests ignored local Merchant ID/Server Key defaults. The shared launcher
reads only the two Sandbox literal fields without executing local settings,
keeps environment-pair precedence and missing-value prompts, and forwards the
key only to the backend child environment. Existing Drive values/profile/payment
journals are preserved. Source `b496d9f`: all three CI jobs SUCCESS; 15 new cases
PASS on both Linux and Windows. Exact results and local-executor limits are recorded
in the [setup/evidence package](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).

## 28 October — BUG-020 Sandbox Server Key format

Owner's Sandbox dashboard shows `Mid-server-`; the launcher previously rejected
it locally. Both Server Key spellings are accepted without changing the fixed
Sandbox endpoint, credential isolation or payment authority. 136 focused protocol/
launcher checks PASS. Source `6a271de`: full local 901 run / 898 PASS / 3 optional
palm-assets SKIP / zero failures/errors; CI 40572395949 all three jobs SUCCESS.
Exact source, raw reports and update instructions are recorded in the
[correction runbook](qa/portrait-v2-sandbox/KEY-FORMAT.md). Actual merchant
authentication and simulator acceptance still need the owner's local test.

Matching-source CI **40481718367**: all three jobs SUCCESS.
Gallery fix **eb0297d**: final local **898 run / 895 PASS / 3 optional
palm-assets SKIP / zero failures/errors**, 291.903s; 20 targeted checks and
18 exact-source native captures (nine held-pointer frames). Actual device retest
remains pending. [Exact evidence/update](qa/portrait-v2-carousel-hold/README.md).


## 27 October — BUG-019 held gallery drag

Owner reports an empty incoming side while holding a carousel drag. Five pooled
Images existed, but two outer textures were cleared at rest. The existing widget
now retains a five-picture cached window through drag, reversal and release.
Native checks cover all 12 designs, both directions and five sizes, including
wraparound; selection/quantity and lifecycle guards remain. Device acceptance
is separate. [Scope, tests and update](qa/portrait-v2-carousel-hold/README.md).


Final customer-delivery source **311f3d8**: **896 local run / 893 PASS /
3 optional palm-assets SKIP / zero failures/errors**; 73 focused PASS,
14 exact-source native captures and eight exact right-panel QR decodes.
Matching-source CI **40472339778**, all three jobs SUCCESS.
[Exact evidence/update](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md#final-source-and-evidence).


## 27 October — customer upload priority and early folder QR

Latest owner instruction supersedes the earlier completion-only screen QR and
interleaved old-recovery policy. Customer uploads now run FIFO to completion;
old retries/reserves/content wait at request boundaries. Two short retry delays
(5s, 15s) precede release to bounded background retry after a third consecutive
failure. Verified assigned-folder QR can appear while bytes are pending, with
truthful upload/retry messaging and a 30-minute check-back suggestion, not an SLA.
Folder claims/manifest mapping survive restart; duplicate/replaced customer
folders are rejected. Code.gs and physical printing policy are unchanged.
[Current contract, evidence, update and limits](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).

Logging correction source **4c31406**: full local **888 run / 885 PASS /
3 optional palm-model SKIP / zero failures/errors**, 262.543s; real-Kivy
console-active integration, broken-sink worker survival and 11 delivery widget
checks PASS. Matching-source CI 40460799605: all three jobs SUCCESS.
[Update and exact evidence](qa/drive-delivery-performance/LOGGING.md).
The supplied RecursionError incident is distinct from the protected old-folder
conflict; exact on-device handler/exit traceback and post-update timing remain unverified.

## 27 October — delivery logging recursion recurrence

Owner reports >10 minutes and supplies RecursionError timing; new queued work
has no worker_start in the extract. Old-folder BIND_FOLDER_CONFLICT is confirmed
for one transaction. Real-Kivy console-active reproduction exposes root/stderr
logging recursion missed by earlier console-disabled QA. Timing now uses the
session file directly, contains sink failures/re-entry, and v2 defaults to MIXED
logging with native diagnostics retained. 54 targeted tests PASS; final checks
are recorded in the [correction runbook](qa/drive-delivery-performance/LOGGING.md).
Code.gs unchanged; no redeploy, reset or known-folder replacement is required.

Retry source **8578825**: complete local **884 run / 881 PASS / 3 optional
palm-assets SKIP / 0 failures/errors**, 268.095s. 67 focused service and
11 native delivery PASS. Matching-source CI 40455236898: all three jobs SUCCESS.
[Exact proof/update guide](qa/drive-delivery-performance/RETRY.md).
Functional source is unchanged in the final evidence publication; actual
Windows/Ubuntu/Google timing after this update still needs device evidence.

## 27 October — failed-delivery retry isolation

Owner timing identifies repeated old bind failures as 70.782s of a 122.719s
queued-to-QR session; exact ValueError cause/installed SHA remain unknown.
Healthy-first scheduling, one recovery/30s, persisted 30–300s backoff and safe
bind codes are implemented; known folder/transaction conflicts remain protected.
Focused service/native checks PASS; final regression/CI evidence is in the linked runbook.
Code.gs unchanged; no redeploy required. [Scope, evidence, updates and limits](qa/drive-delivery-performance/RETRY.md).

Final delivery source **2e140c1**: full local **877 run / 874 PASS / 3 optional
palm-assets SKIP / zero failures/errors**, 262.743s; 29 Code.gs VM PASS,
11 focused native delivery PASS. Matching-source CI **40448427344**, all three
jobs SUCCESS; 14 native FBO screenshots verified at both required sizes.
[Final evidence, update/manual deployment, timing export and limits](qa/drive-delivery-performance/README.md).
Runtime unchanged in the final evidence publication. No production Drive-speed,
Windows/Ubuntu hardware, cloud deployment or deletion acceptance is inferred.

## Current delivery continuation

Owner-approved Drive/GUI improvement continues from fcabfbb. Background delivery
snapshots no longer lock result buttons/footer during rebuild. The strict
UPLOAD_COMPLETE QR contract and operator-disabled printing remain. Controlled
native regression PASS; actual five-minute delay is unmeasured.
[Scope, v1 comparison, evidence and rollback](qa/drive-delivery-performance/README.md).

**Final published checkpoint, 27 October:** FEAT-009 source `f023029` is on the
required branch; matching [CI 40423003641](https://github.com/pratikto/PhotoBooth/actions/runs/40423003641)
has all three jobs SUCCESS. Windows fixture connections are explicitly closed
before database replacement; production runtime is unchanged from `b99c613`.
Final local rerun: 869 cases, 866 PASS, three optional palm-assets SKIP, zero
failures/errors, 272.035s. [Final proof](qa/portrait-v2-recovery/final-verification.json).
Docs-first primary rule and Windows-development/Ubuntu-deployment direction
are persisted in AGENTS/protocol/prompt. Next: actual target-device acceptance;
automatic restart remains off and no service was installed.

## Current — 27 October FEAT-009 stage 2 and primary working rule

Owner requires comprehensive/careful documentation review before code, then
documentation updates after code. Persisted in AGENTS, protocol and continuation
prompt. Windows is development; Ubuntu mini PC is deployment. Continue on this
branch; read [stage-2 review/runbook](qa/portrait-v2-recovery/README.md) first.
Current source adds read-only recovery review, pre-GUI watchdog holds,
per-checkout launcher ownership and Ubuntu graphical-session unit generation.
No automatic restart, replay, service installation or production/deployment.

Remote refresh works with network permission; synchronized remote `a7815d9`
(includes Drive/QR repair `0bd69a9`) before rebasing the unpublished watchdog
checkpoint to `ae5c62a`. Do not undo the current cloud numbered-Photo correction.
The older source/ordering paragraphs below are dated historical checkpoints.
Initial stage-2 local regression: **869 run / 866 PASS / 3 optional palm-assets SKIP /
0 failures/errors**, 261.246s. Focused 47 PASS with site packages disabled;
API/Sandbox 16 PASS and actual native launch/pause/resume/lease/exit PASS.
Earlier HTTP stalls reproduce under restricted command-network access and clear
with network permission; no payment/fixture code patch was needed. Raw old
failures stay preserved. [Current evidence/limits](qa/portrait-v2-recovery/README.md).

Ubuntu mini-PC/Windows hardware, graphical sign-in/service start, paper, actual
merchant and Google deployment/retention acceptance remain NOT_RUN. No source
success grants release or closes BUG-009. Future FEAT-009 automatic recovery
requires a durable safe-idle contract; the current unit deliberately uses Restart=no.

**Historical stage-1 checkpoint (before stage 2):** user requests next roadmap
development while manual tests wait. FEAT-009 stage 1 adds an opt-in external
liveness observer and Windows startup-script generator. It never kills/restarts
the kiosk or replays fulfillment. Ordinary launch behavior is retained; merchant
Sandbox keeps its dedicated launcher. Base `5639400`; remote refresh currently
fails because the configured proxy is unreachable. No push/CI claim.
[Scope, commands, limitations, acceptance and rollback](qa/portrait-v2-watchdog/README.md).
Focused 22 PASS, package-free 15 PASS and actual native launcher lifecycle PASS;
full suite NOT VERIFIED (blocked in existing API TestClient), isolated Sandbox
widget checks 6 FAIL (`Worker did not settle`). Trace/raw reports preserved in
the runbook; no full-source certification or payment fix is claimed.
Earlier latest-source references below describe the prior committed baseline.

## Latest Drive/QR repair (26 October 2026)

Continue from the correction in docs/qa/drive-photo-layout/README.md. The earlier per-transaction-root cloud tree is superseded by owner instruction. The existing Web App needs a new deployment version; this session performed read-only Drive inspection only.

Updated **26 October 2026**. Repository `pratikto/PhotoBooth`; required branch
**`feature/portrait-kiosk-v2-next`**. Documentation baseline **`f36ebad`**, latest functional
source **`53e7b4c`** (coordinated per-booth storage/content; mirror `fc26e3d`, BUG-009 `887ba39`, print/Drive `266b2c8`). Refresh remote HEAD before continuing. GitHub's default is
still `master`; `main.py` launches v1. Do not restart the project or P3/P4 work.

## Latest requested acceptance checklist

Owner asks for every still-untested gate. The [49-item combined form](qa/portrait-v2-pending-acceptance/windows-checklist.html)
and [coverage/runbook](qa/portrait-v2-pending-acceptance/README.md) reuse the existing
offline Submit/metadata/persistence implementation. Prior passes remain recorded;
twenty cycles apply only to the existing NEW Sandbox gate. This is documentation,
not runtime/provider/production work or a newly reported device failure.

## Latest completed increment

**Latest owner instruction — FEAT-004 + BUG-009 implementation:** application
and Code.gs integration is implemented in the ordinary launcher: per-booth
25 empty local/remote reserves, Photo/NN/raw,color,bw, immutable offline claims,
verified global/local caches and original deadline retention. Foundation 76bb9a0
and backend 6e2f777 are pushed/verified. Final integration source/evidence and
setup/Submit checklist live in the [implementation package](qa/feat-004-storage/README.md).
Final source 53e7b4c has 824 full local PASS/zero skips, 24 Code.gs PASS and
matching three-job CI SUCCESS (40273343183); 28 final native PNGs verified.
Actual Google deployment/deletion, phone/paper and release remain NOT_RUN. Keep
all archive contents excluded and v1/Sandbox state isolated.

**26 October foldering audit:** owner asks to check current organization against
per-booth/25-reserve/Photo/NN/raw-color-bw/global-cache requirements and excludes
all contents of `old` from inspection/change. Owner selects continued local
photo/print when Drive/reserves are unavailable, with upload/QR later. The
[audited target contract](photobooth-storage-layout.md) is documentation, not a
runtime/cloud cutover. Existing source fixtures: 38 tests PASS plus controlled
two-session/three-copy/retake, native raster and pool checks. At that audit checkpoint the runtime
still had target 2 and its prior active paths; real Drive was not accessible. Do not
infer new-layout implementation or scan/migrate the archive from this audit.

Owner then clarifies that this target belongs to **FEAT-004 ads + BUG-009**.
Keep storage roots/reserves/session paths, shared content caches and retention
in one coordinated implementation sequence; content-sync success and actual
photo-deletion acceptance remain distinct. The earlier retention-only source
scope describes what was delivered then, not an exclusion of this new linkage.

**26 October mirrored outputs:** owner explicitly chooses mirrored review,
result/printed/digital strips. Source 977d26b extends the v1 compositor via a
default-off photo-only option; v2 opts in. Full-resolution original JPEGs and
detector inputs remain original; frame/text/logo/QR and v1 defaults stay normal.
One saved PNG serves result/print/Drive, no old output migration/replay. Source
fc26e3d corrects obsolete preview/consent wording found by screenshot review.
Final 808 full PASS/zero skips (230.670s); 42 focused PASS, all-twelve-renderer
checks pass. Sixteen clean-source native captures verified; eight selected
native and two form views reviewed at 800×1280/452×900. Matching-source CI
40263151709 has all three jobs SUCCESS; optional native model-assets skip covered
locally. Paper orientation NOT_RUN.
Use the fresh five-item Submit form; no extra twenty-cycle gate. Updated older
delivery P03 has a new storage key, preserving old answers without passing the
new orientation automatically. [Evidence/rollback](qa/portrait-v2-mirrored-output/README.md).

**26 October BUG-009:** owner explicitly resumes this previously deferred bug;
setup/redeployment not confirmed. Source 130aae1 repairs stale-flag ACK and
incorrect same-handler trigger setup, reusing v1 cleanup unchanged. Source
887ba39 adds one authenticated read-only status request/CLI with original private
configuration, redacted report and eight-item Submit form. Full 807 Python
PASS/zero skips, 44 focused PASS, 19 actual-Code.gs VM PASS; matching-source CI
40255716011 all three jobs SUCCESS, optional native model-assets skip covered
locally, four native and two form views reviewed at both required sizes. Original 15/30-day
clocks, v2 upload hold and deletion selection preserved. No Google deployment,
trigger write or actual deletion performed; BUG-009 remains OPEN until owning
account and authorized synthetic evidence. No ad sync/watchdog scope.
[Current guide, checkpoints and proof](qa/bug-009-retention/README.md).

**26 October owner flow refinement:** remove only idle CARA PAKAI; reuse the
existing Start/invitation/postgame tutorial gate and acknowledgement/reset rules.
Full-width UNDANGAN (DEMO) replaces the redundant split row. Source `20453fe`
has 800 full PASS/zero skips and twelve clean-source PNGs verified, six affected
views reviewed. Matching-source CI 40248962384 has all three jobs SUCCESS
(one optional native palm-assets skip covered locally). [Scope, exact
evidence and rollback](qa/portrait-v2-photo-entry/README.md). This does not start
retention/watchdog or any other backlog candidate.

**Owner-selected print/Drive continuation:** user postponed proposed watchdog
work and selected automatic print as v1 with background Drive. Stage 1 **7b691c7**
exposes launch options/contracts (29 focused PASS, matching CI SUCCESS); native
stage 2 **266b2c8** connects the existing durable print worker, startup queue resume,
verified-folder consent and large verified result QR. Nine original v1 backend
files are unchanged. Default local and dedicated merchant-trial boundaries stay.
Fifteen new-feature checks and 92 earlier native regressions pass. Final source
has **800 full PASS/zero skips**, matching-source CI 40208966127 all three jobs
SUCCESS and 133 verified PNGs; large screenshot QR decodes at both required sizes.
Actual paper/phone/cloud acceptance remains pending.
[Current print/Drive runbook and eleven-item form](qa/portrait-v2-print-drive/README.md).

**Latest owner retest / BUG-018:** targeted R01–R04 **4/4 checked**, zero
unchecked and no issue notes. Rapid/mixed buttons, busy close, reopen/minimize
and next input/restart are owner-reported PASS; move BUG-018 to **MONITORING**,
not formally CLOSED. Tested HEAD/device fields and specific display sizes remain
unknown. Preserve the earlier raw 8/8 plus hang note as the initial failure.
Delivered input guard `ebb53fd` has 785 full PASS/zero skips, 37 focused PASS,
matching-source CI 40189694738 all three jobs SUCCESS and 119 verified PNGs.
No new runtime patch or old twenty-cycle repetition follows this passing report.
Watchdog remains a proposed feature scope, not implemented by recording this retest.
[Raw reports, evidence and rollback](qa/portrait-v2-health-clicks/README.md).

Read-only operator Device Health now reuses the original v1 panel/backend and
extracted worker from **`dbbe055`**. Small adapters connect v2 scheduling,
cached-camera observations, audio/input lifecycle and redacted local reports.
F12 or a 1.5-second header hold opens it at idle; protected Sandbox RECOVERY also
allows observations. Selection remains disabled; no second camera, print payload,
automatic restart, order mutation or upload is introduced.

Recorded checks: **780 full local PASS / zero skips**; matching-source
[CI 40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369)
three jobs SUCCESS, with one optional native model-assets skip covered locally;
119 PNGs verified. [Proof and eight-item operator form](qa/portrait-v2-operator-health/README.md).
These results predate this documentation-only reconciliation.

## Checkpoints

| Commit | Purpose |
| --- | --- |
| `d6fb5d4` | Visual/local baseline before Sandbox service imports |
| `37da798` | Reused QRIS service/client/journal; 124 original focused PASS |
| `ce603c2` | Native Sandbox → P3 handoff; 195 focused PASS; later full CI exposed a standalone hook regression |
| `9433010` | Corrected final P5 source/readiness/ACK guards; 688 full PASS |
| `0dc6555` | P5 evidence: matching CI, 109 verified PNGs; owner preflight later reported ready |
| `ae90269` / `fdafbe2` | Dated 19-branch audit / consolidated documentation baseline |
| `4c89e4f` | Reused v1 health foundation; 73 focused PASS |
| `ea394e8` | Mounted original health panel/worker and safe reports; 780 full PASS |
| `5f09eff` | Operator matching-source evidence/documentation |
| `f36ebad` | Completed English documentation consistency baseline |
| `ebb53fd` | BUG-018 fresh-press/repeat guard; final 785 full PASS, three-job CI SUCCESS |
| `edeec47` | Later BUG-018 owner 4/4/no issues at unknown HEAD; monitoring |
| `7b691c7` | Explicit print/Drive options and worker setup/QR contracts; 29 focused PASS |
| `266b2c8` | Native automatic print, background queue startup/resume and verified result QR; 800 full PASS, matching three-job CI SUCCESS |
| `20453fe` | Remove redundant idle help action; mandatory Start/invitation/postgame tutorial unchanged; 800 full PASS/zero skips |
| `130aae1` | BUG-009 real-CLOCK activation/setup correction and authenticated read-only backend status; 19 VM + 25 Python PASS |
| `887ba39` | Safe existing-config diagnosis/report and Submit form; 807 full Python PASS/zero skips, 19 VM PASS |
| `977d26b` | Mirror photo areas consistently via existing compositor; 808 full PASS, first matching three-job CI SUCCESS |
| `fc26e3d` | Preview/consent copy correction after visual review; final 808 full PASS/zero skips |

Use scoped inverse commits for code rollback after inspection; preserve all
payment journals, consumed attempts, reports, photo/print manifests and customer
data. Do not reset data to make an uncertain order disappear.

## Authorized continuation and acceptance

The owner's 25 October instruction permits safe approved source work while
laptop acceptance waits; it supersedes older “wait for P5 before any source work”
sequencing. The bounded health/report increment is completed. Additional feature
scope follows the owner's next instruction; do not treat the backlog as approval.
The English documentation audit completed at f36ebad. The next owner report
authorizes this BUG-018 correction; proposed watchdog work is not started.

- Preserve the [later operator 4/4 retest](qa/portrait-v2-health-clicks/owner-retest-2026-10-25.json)
  at unknown HEAD/device metadata; BUG-018 monitoring, no new patch while working.
  Do not impose another old photo/game twenty-cycle run.
- Collect the [P5 form](qa/portrait-v2-p5/windows-checklist.html) and actual merchant
  simulator evidence when available; the new Sandbox integration cycle checks
  are distinct from earlier photo/game reports.
- Owner preflight **`0dc6555` → READY_FOR_MANUAL_TEST** is recorded, but its JSON
  metadata/form were not supplied. Do not borrow missing device fields from older reports.
- Preserve owner-reported P3/visual/audio/game passes and BUG-012–017 monitoring.
  Investigate recurrence with evidence rather than patching reported-working paths.
- BUG-009 cloud retention is OPEN; owner resumed source remediation at 130aae1/887ba39.
  Use the new read-only diagnostic/activation guide; installed-account evidence is pending.
  V2 retention acknowledgement is an upload guard,
  not proof of deployed 30-day deletion. V1 BUG-001/007 are not closed by v2 audio.

## Implementation invariants

Reuse the actual original game Stage/Flow/render/assets/emitter (`672e3f7`, 26
reference files), QRIS service/client/journal (`3cc8a8e`) and health panel/worker
(`dbbe055`). Refresh relevant remote references before new reuse.

Preserve uniform game motion/spacing and centered world (BUG-015/016), native
readable main-button captions without mandatory icons, large animated Meong,
three original unmirrored captures and one retake per design. Quantity means copies.

Sandbox uses server quotes, independently verified status, a one-use grant,
durable STARTING before allocation and STARTED ACK before countdown. Pending,
unknown or paid states cannot be discarded by browsing timeout. No trusted QRIS
game-promo contract exists; require full-price/no-promo consent. Dedicated merchant
trial keeps printer/Drive off. Local MOCK remains a simulation.

[Roadmap](portrait-kiosk-v2.md) · [source status](FEATURE_STATUS.md) ·
[technical contracts](portrait-kiosk-v2-technical-design.md) ·
[reference audit](gui-v2-branch-audit.md) · [promotion plan](gui-v2-promotion-plan.md) ·
[continuation prompt](DEVELOPMENT_PROMPT.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/DEVELOPMENT_HANDOVER.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

