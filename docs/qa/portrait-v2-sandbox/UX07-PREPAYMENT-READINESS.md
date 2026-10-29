# AR-08 — UX-07 prepayment readiness evidence

29 October 2026 (Asia/Jakarta). Base/remote verified
858944cf1ef79483892b2c08f07de7d2a5be5a7e; existing feature branch only.
Reviewed AGENTS/protocol/prompt, checkpoint/handover, current index/status/
backlog/decisions, AR-08 readiness/remedy, master/roadmap/operations/matrix and
native technical design. Source review: camera mailbox/freshness, check_disk,
original read-only check_printer and tests, frozen contract/image validation,
prepayment_readiness, SandboxCheckout.begin_ready, native begin/poll error flow,
existing HTTP fixture/native widget tests. No archive traversal or branch reuse.

Current authorized contract: Sandbox printer/Drive OFF. A delivery opt-in is a
configuration error that blocks order creation, never permission to probe/send
paper or upload. check_printer observes routes/spooler only, not paper supply;
it is not mounted as a purchased-print prepayment gate in this trial. Therefore
new Sandbox tests cannot certify purchased real-printer acceptance. Keep UX-07
NOT_RUN for its complete stronger requirement; annotate verified components.
No artificial PASS by enabling printing or weakening this scope.

Bounded increments:
1. Real API/client/controller/SQLite causal tests: missing/stale/future camera,
   low/unknown disk, writable/open/fsync failure, absent/corrupt artwork/mask,
   freshness expiring during checks, PRINT/DRIVE flags. No visit/order/provider
   charge before readiness success; probe cleanup and existing bytes retained.
   Safe retry creates exactly one order. Existing active order may reconcile
   without creating a replacement, despite current failed device observations.
2. Native widgets at both portrait sizes: rejected readiness remains QUOTE,
   no payment QR/order, generic actionable message/redaction, healthy deliberate
   retry works. Reuse original controller/UI; patch runtime only on reproduction.
3. Focused results/docs/micro-push/remote check per increment; final matching CI
   and checkpoint. No full repeat for tests-only work; retain 347e502 full source
   provenance. If runtime changes, one applicable final full regression.

Fixtures only, no physical camera/printer/merchant/network/Drive/refund/deletion.
No production/OPS/public ingress/new branch/default/master operation. Raw logs,
images, DBs and ticket pixels stay in private work/; publish source/counts/hashes
only. Rollback tests/docs only unless a runtime defect is reproduced; preserve
financial, claim, fence, media and audit records. After safe UX-07 components are
verified, continue independent UX-11 while purchased-printer/device gates wait.

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
[Exact commands/source/CI/results/digests/limits](evidence/ux07-final-verification.json).

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

Subsequent dependency update: UX-11 synthetic validation is complete at
7ca46b5; [exact evidence](evidence/ux11-final-verification.json). Do not repeat
those verified tests. The complete purchased-printer gate above remains NOT_RUN.
