# Meong Photobooth documentation — GUI v2

## 29 October — UX-11 synthetic PASS / remaining external gates

Test source `7ca46b5`, **9 focused PASS / zero skip**; CI 40865822670 all three
jobs SUCCESS. Real held process on Windows/Linux; native stalled checkout/QR/
upload Clock/privacy/no-replay on Linux. Windows owned-lease fixture failure at
07734b2 preserved with controlled reproduction/correction. No runtime change;
old full 347e502 1159/1155/4 excludes ten new methods, separately verified.
Matrix **59 PASS / 0 FAIL / 9 BLOCKED / 1 NOT_RUN**, audit IN_PROGRESS.
UX-07 whole purchased-printer gate remains NOT_RUN; provider/webhook/device/
operations/release gates stay separate. No production or Sandbox delivery enabled.
[Exact evidence/next work](qa/portrait-v2-sandbox/evidence/ux11-final-verification.json).

## 29 October — UX-11 stalled worker evidence focused-verified

9 focused PASS, zero skip. Actual blocked-main/worker process remains held
without restart/paid mutation; native checkout/QR/upload stalls leave Kivy Clock
responsive, late results private, original upload files delivered once. No
runtime change; matching CI pending. UX-11 NOT_RUN pending final verification,
UX-07 stronger printer gate remains open; matrix 58/0/9/2.
[Contract/results/limits](qa/portrait-v2-sandbox/UX11-FROZEN-WORKERS.md).

## 29 October — UX-07 Sandbox components verified

Test source `685b994`, **36 focused PASS / zero skip**; CI 40862328219 all three
jobs SUCCESS. Five boundary methods on Windows/Linux; native error/no-QR/retry
method at both portrait sizes on Linux. Runtime unchanged at 347e502; old full
1159/1155/4 retains provenance and excludes new methods. Complete purchased-
printer gate remains NOT_RUN; preserve transport-off Sandbox. Matrix 58/0/9/2,
audit IN_PROGRESS. Next independent UX-11 frozen-worker/GUI evidence audit.
[Exact evidence/remaining limits](qa/portrait-v2-sandbox/evidence/ux07-final-verification.json).

## 29 October — UX-07.b native error/retry verified

36 focused PASS/zero skip. Five boundary methods plus one native method:
eight failures/eight retries at both portrait sizes; QUOTE/message/redaction/
no QR/order and exactly-one healthy retry verified. No runtime change; current
CI pending. UX-07 stronger purchased-printer gate NOT_RUN, matrix 58/0/9/2.
[Evidence/limits/next](qa/portrait-v2-sandbox/UX07-PREPAYMENT-READINESS.md).

## 29 October — UX-07.a Sandbox readiness boundaries verified

34 focused PASS/zero skip, five new integration methods: no charge/order before
readiness, probe cleanup, safe retry and existing identity preserved. No runtime
change; Linux/Windows CI registered/pending. UX-07 stronger purchased-printer
gate NOT_RUN, matrix 58/0/9/2 unchanged. Native message/retry evidence next.
[Contract/results/limits](qa/portrait-v2-sandbox/UX07-PREPAYMENT-READINESS.md).

## 29 October — UX-05 verified / BUG-024 fixed in source

Source `347e502`, 52 focused PASS; full 1159/1155/4, zero failure/error.
CI 40856740113 all three jobs SUCCESS, six UX-05 methods PASS on Windows/Linux.
Unknown cancellation stays held; fresh confirmed unpaid cancellation archives
before new visitor; write failure holds. Late paid/typed isolation/ACK/archive/
return preserves original rights. UX-05 synthetic PASS; BUG-024 regression
verified, actual device acceptance NOT_RUN. Matrix **58/0/9/2**, audit IN_PROGRESS.
Next UX-07 readiness/printer scope audit, preserve Sandbox transport-off.
[Exact evidence/limits](qa/portrait-v2-sandbox/evidence/ux05-final-verification.json).

## 29 October — UX-05.b confirmed cancellation recovery

BUG-024 reproduced: confirmed cancellation held CANCELLING after restart.
Controller now archives/commits unpaid terminal cancellation before new visitor;
write failure/cached evidence/paid rights hold. Six UX-05 scenarios; **52 focused
PASS**, full/CI pending. UX-05 NOT_RUN pending final, matrix 57/0/9/3.
[Contract/results/limits](qa/portrait-v2-sandbox/UX05-AMBIGUOUS-ABANDONMENT.md).

## 29 October — UX-05.a uncertainty holds verified

33 focused PASS, zero skip; two new HTTP/controller abandonment/restart cases
preserve original identity/OWED/private proof, deny replacement under 404/outage.
No runtime change. Linux/Windows CI registered/pending; UX-05 NOT_RUN until
terminal/paid-release continuation checks. Matrix 57/0/9/3 unchanged.
[Contract/evidence/next](qa/portrait-v2-sandbox/UX05-AMBIGUOUS-ABANDONMENT.md).

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

## 29 October — CAP-20 verified

Storage source `9f3568b`, corrected native fixture `da3f444`, both pushed/remote
verified. **57 storage focused PASS**, 74 injected faults/48 actual children.
**CI 40842036384 all three jobs SUCCESS**: Windows payment/recovery 72 PASS,
Linux Sandbox/recovery 389 PASS, native 111/110/one optional palm SKIP. All six
CAP-20 methods PASS on Windows/Linux. Initial CI 40839833482 native failure
preserved; corrected test-only Clock isolation retains pixel/flip assertions,
111 focused/110 PASS/one optional SKIP and two effective mutation controls.
Runtime unchanged. Matrix **56 PASS / 1 FAIL / 9 BLOCKED / 3 NOT_RUN**;
audit IN_PROGRESS, BUG-023/UX-13 OPEN/FAIL, external/OPS gates remain.
Next **AR-09 bounded redacted durable denial audit**. [Exact evidence/limits](qa/portrait-v2-sandbox/evidence/cap20-final-verification.json).

## 29 October — CAP-20 native CI fixture correction

Storage source `9f3568b` CI 40839833482: Windows/pure SUCCESS, Linux native
same-packet flip FAIL (`8 != 7`); recovery group 389 PASS. Reproduced unrelated
Clock interference; test-only isolation preserves pixel/flip checks and rejects
new scheduled work. Both negative controls detect mutations. **111 native focused
run / 110 PASS / one optional palm SKIP**, zero failure/error, 138.089s.
57 storage PASS/74 faults/48 children unchanged at 9f3568b. Runtime unchanged;
corrected-fixture CI pending. Matrix 56/1/9/3, BUG-023/external gates OPEN.
Next current CI/final checkpoint, then AR-09. [Evidence/limits](qa/portrait-v2-sandbox/evidence/cap20-native-fixture-verification.json).

## 29 October — CAP-20 storage matrix focused-complete

**57 focused PASS / zero failure/error/skip**, 74 fault cases: 48 real child
exits plus 26 issue/atomic-writer cases. JPEG/retake/PNG/initial-manifest and
reporting rights preserve original ACKs/bytes/quota/OWED or hold safely.
No runtime change. Matrix **56 PASS / 1 FAIL / 9 BLOCKED / 3 NOT_RUN**.
First JPEG-only CI 40838609747 SUCCESS; current matching CI pending.
Next final CI/checkpoint then AR-09 BUG-023. [Evidence/limits](qa/portrait-v2-sandbox/CAP20-STORAGE-FAULTS.md).

## 29 October — CAP-20 JPEG write faults focused-verified

**52 focused PASS / zero failure/error/skip**, 14 child exits covering ENOSPC/
EACCES at seven JPEG write boundaries. No false capture ACK, original paid
OWED/issue/bytes preserved, proved bytes recover once; unknown bytes held.
CAP-20 remains NOT_RUN pending retake/PNG/initial/reporting faults; matrix
55/1/9/4. Tests/CI/docs only; matching CI pending. [Evidence/limits](qa/portrait-v2-sandbox/CAP20-STORAGE-FAULTS.md).

## 29 October — CAP-16 verified

Tests/CI `1ef7d29454a926d6eccc7cb2ba15162fbfbfa0c8` pushed/remote verified.
**74 focused PASS**, zero failure/error/skip; four new CAP-16 children/two
pre-COMPLETE boundaries. CI **40834950593 all three jobs SUCCESS**, all three
CAP-16 methods PASS on Windows/Linux (groups 66/383 PASS, zero skip); native
one optional palm SKIP. Original result/ACK/retention/OWED preserved; outage,
refund/corrupt PNG deny false completion. Tests/docs only, runtime unchanged.
Matrix **55 PASS / 1 FAIL / 9 BLOCKED / 4 NOT_RUN**, audit IN_PROGRESS/BUG-023 OPEN.
Next **CAP-20**, then AR-09; real device/provider/OPS/release gates unchanged.
[Exact evidence/limits](qa/portrait-v2-sandbox/evidence/cap16-final-verification.json).

## 29 October — CAP-16 composition/intent exits focused-verified

**72 focused PASS / zero failure/error/skip**, two new real child exits after
final composition and saved COMPLETING before COMPLETE request. Original result,
proof/ACK/binding/retention/OWED preserved. Tests/docs only; runtime unchanged.
Matrix **55 PASS / 1 FAIL / 9 BLOCKED / 4 NOT_RUN**. CI pending; next provider/
media denial cases, then CAP-20/AR-09. [Evidence/limits](qa/portrait-v2-sandbox/CAP16-COMPOSITION-COMPLETE.md).

## 29 October — CAP-11–13 verified

Test/CI `423d9d2c9096ec897521df565f2c59572057efd5` pushed/remote verified.
**80 focused PASS**, zero failure/error/skip; seven real child exits/six retake
boundaries. CI **40831396874 all three jobs SUCCESS**; all five retake methods
PASS on Windows/Linux (groups 63/380 PASS, zero skip); native one optional palm
SKIP. Tests/CI/docs only, runtime unchanged. Matrix **54 PASS / 1 FAIL / 9 BLOCKED /
5 NOT_RUN**, audit IN_PROGRESS/BUG-023 OPEN. Next **CAP-16**, then CAP-20/AR-09;
external/OPS/production gates unchanged. [Exact evidence/limits](qa/portrait-v2-sandbox/evidence/cap11-13-final-verification.json).

## 29 October — CAP-11 focused evidence

**76 focused PASS / zero failure/error/skip**, two actual retake process exits;
original selection/quota/paid binding/bytes/OWED preserved. Tests/CI/docs only,
no runtime change. Matrix **52 PASS / 1 FAIL / 9 BLOCKED / 7 NOT_RUN**.
CI pending at this containing test commit. Next CAP-12–13, BUG-023/external/OPS
gates unchanged. [Evidence and limits](qa/portrait-v2-sandbox/CAP11-13-RETAKE-CRASHES.md).

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

## Current Autonomous Recovery evidence and readiness — 29 October

**CAP-01–05 source evidence verified:** test/CI `e72e28bdf8b0cbb080ef0c35aa8a1e3906bf55cb`,
**66 focused PASS / zero failure/error/skip**, seven actual child exits, same
paid identities and orphan hold. [CI 40815197373](https://github.com/pratikto/PhotoBooth/actions/runs/40815197373)
**all three jobs SUCCESS**; Windows payment/allocation group 55 PASS/zero skip.
[Contract/evidence](qa/portrait-v2-sandbox/CAP01-05-ALLOCATION-CRASHES.md).

Application unchanged from e0dc594; prior full **1117 run / 1114 PASS / 3 optional
palm SKIP** and native c94696d **28 PNGs / four QR checks** retain original sources.
No new full/native/physical result inferred from this tests-only increment.
Matrix **50 PASS / 1 FAIL / 9 BLOCKED / 9 NOT_RUN**, audit IN_PROGRESS,
BUG-023/UX-13 durable denial audit OPEN. Next **PAY-18 lost service replies including
COMPLETED**, then remaining retake/COMPLETE/disk and AR-09. [Checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).
Device/merchant/privacy/retention/public ingress/release gates remain; queued
Settings/Emulate Ticket/QRIS Slip runtime NOT_STARTED, no production approval.

## Active priority and newly approved future design — 29 October 2026

**Keep AR-00 → AR-13 autonomous payment/photo recovery as the #1 implementation priority.** The dated historical paragraph below is not the current stage: inspect the [live AR checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md), [roadmap](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md), [handover](DEVELOPMENT_HANDOVER.md) and fresh remote Git HEAD, and continue its first unfinished tested increment. **Do not begin the new Settings OPS work ahead of AR.**

**New future GUI v2 design (owner-approved, DOCUMENTATION ONLY, OPS NOT_STARTED):** [Meong Settings complete contract](qa/portrait-v2-operator-settings/README.md), [OPS-00..OPS-10 staged Codex roadmap](qa/portrait-v2-operator-settings/IMPLEMENTATION-ROADMAP.md), [129 test cases](qa/portrait-v2-operator-settings/ACCEPTANCE-MATRIX.md), [all decisions/supersessions](qa/portrait-v2-operator-settings/DECISION-REGISTER.md), [Codex handover prompt](qa/portrait-v2-operator-settings/CODEX-HANDOVER.md). Final tabs: **Device Health / Audio Settings / Emulate Ticket**. Normal operator login uses a **static booth-bound QR** at **Advertising + SAFE_IDLE**; DEMO promo/game QR tickets remain static in development but require durable once-per-visit consumption. Physical/merchant production gates stay separate.


## Historical Autonomous Recovery implementation checkpoint — earlier 29 October

AR-00–08 source increments and AR-09 PIN inspection/service-fence foundation have
focused automated evidence. Safe booth release/reacquisition (AR-09.c2), AR-10–13
and actual device/merchant gates remain unfinished. Read the
[checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md) and
[exact published source/tests](qa/portrait-v2-sandbox/CONTINUATION-2026-10-29.md).
The dated design-only notices below describe initial planning, not current source
or completed unattended/production acceptance.

## 28 October 2026 — autonomous QRIS and photo recovery planning (design only)

**New Codex execution entrypoint:** [Autonomous recovery master specification](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-MASTER-PLAN.md) · [numbered implementation roadmap AR-00–AR-13](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md) · [Midtrans provider and idempotency research register](qa/portrait-v2-sandbox/MIDTRANS-PROVIDER-CONTRACT.md) · [fault-injection/acceptance matrix](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-TEST-MATRIX.md) · [customer/operator operations runbook](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATIONS.md).

Owner direction: unattended-first safe recovery, not blind replay; maintain separated payment/fulfillment/kiosk ownership, original provider order and customer privacy. **Planning docs only**; functional source remains as previously recorded and recovery GUI/automatic process is **NOT IMPLEMENTED / NOT TESTED**. Read existing [operator recovery implementation record](qa/portrait-v2-sandbox/RECOVERY.md) as historical source; this design defines future staged work. Existing branch remains `feature/portrait-kiosk-v2-next`, with no default/master/production change. Codex starts at AR-00 and must record exact functional SHA and new evidence before advancing.


Latest QRIS correction: [BUG-021 stable pending image URL during polling](qa/portrait-v2-sandbox/QR-POLLING.md).

Latest Sandbox presentation: [centered Meong logo using the existing Drive renderer](qa/portrait-v2-sandbox/QR-LOGO.md).

Latest Sandbox setup: [saved local credentials without repeated terminal entry](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).

Latest Sandbox correction: [BUG-020 dashboard Server Key formats](qa/portrait-v2-sandbox/KEY-FORMAT.md).

Latest gallery correction: [BUG-019 held-drag incoming neighbours](qa/portrait-v2-carousel-hold/README.md).

Latest delivery contract: [customer FIFO, held background retries, early verified
folder QR and immutable mapping](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).
This supersedes earlier completion-only screen-QR guidance below.

Updated **26 October 2026 (Asia/Jakarta)**. Continue on
`feature/portrait-kiosk-v2-next`; the GitHub default remains `master` and
`python main.py` remains the v1 entry point.

## Find the authoritative document

| Subject | Document |
| --- | --- |
| Installation, launchers and test modes | [Repository README](../README.md) |
| Implemented roadmap and customer flow | [GUI v2 specification](portrait-kiosk-v2.md) |
| Approved future operator Settings after AR-00–AR-13 | [Master design](qa/portrait-v2-operator-settings/README.md) · [OPS implementation order](qa/portrait-v2-operator-settings/IMPLEMENTATION-ROADMAP.md) · [QA](qa/portrait-v2-operator-settings/ACCEPTANCE-MATRIX.md) · [Codex prompt](qa/portrait-v2-operator-settings/CODEX-HANDOVER.md) |
| Per-booth folders and offline global/local assets | [Current storage contract](photobooth-storage-layout.md) — local source integrated; corrected numbered cloud layout still needs installed-account deployment/acceptance |
| Current implementation and acceptance boundaries | [Feature status](FEATURE_STATUS.md) |
| Modules, workers and service contracts | [Technical design](portrait-kiosk-v2-technical-design.md) · [architecture](ARCHITECTURE.md) |
| Current visual decisions and artwork provenance | [Visual specification](portrait-kiosk-v2-visual-spec.md) · [artboards](assets/portrait-v2/README.md) |
| Owner-confirmed product decisions | [Decision log](DECISIONS.md) |
| Defects and monitoring | [Bug register](bug_tracker.md) |
| Outstanding work and proposed features | [Backlog](next_step.md) |
| Resume work | [Handover](DEVELOPMENT_HANDOVER.md) · [continuation prompt](DEVELOPMENT_PROMPT.md) |
| Scope, reuse, checks and staged pushes | [AGENTS.md](../AGENTS.md) · [development protocol](DEVELOPMENT_PROTOCOL.md) |
| Tests, owner reports and manual acceptance | [Test ledger](test_checklist.md) · [QA index](qa/README.md) |
| Change history | [Changelog](CHANGELOG.md) |
| Reference branches and repository transition | [Branch audit](gui-v2-branch-audit.md) · [promotion plan](gui-v2-promotion-plan.md) |
| This documentation cross-check | [Reconciliation report](qa/documentation-consistency-2026-10-25.md) |

## Current acceptance packages

- [Delivery logging recursion correction](qa/drive-delivery-performance/LOGGING.md):
  console-active regression, durable queue survival and MIXED-mode update.


- [Failed Drive retry isolation](qa/drive-delivery-performance/RETRY.md): runtime
  timing, healthy-first scheduling, persistent backoff and safe bind diagnosis.


- [Drive delivery performance and GUI state](qa/drive-delivery-performance/README.md):
  customer-priority scheduling, bounded reserves/content yield/cache reuse, monotonic
  timing, v1 comparison, Windows update/manual deployment and short manual checks.
  Production five-minute delay remains unmeasured.


- [FEAT-009 stage 2: recovery and Ubuntu startup](qa/portrait-v2-recovery/README.md):
  Windows development/Ubuntu deployment, docs-first rule, guarded startup and
  single-instance ownership; generated user service requires manual installation.

- [Mirrored v2 output](qa/portrait-v2-mirrored-output/README.md): consistent
  review/result/printed/digital photo areas, unchanged original JPEGs/art/QR,
  all-twelve renderer checks and [five-item Submit form](qa/portrait-v2-mirrored-output/windows-checklist.html).

- [BUG-009 retention](qa/bug-009-retention/README.md): existing v1 activation
  repair, read-only diagnostic, setup/deployment guide and [eight-item Submit
  form](qa/bug-009-retention/windows-checklist.html). Source proof is separate
  from actual owning-account timer/permanent-deletion evidence.

- [Simpler photo entry](qa/portrait-v2-photo-entry/README.md): 26 October removal
  of the separate idle CARA PAKAI button; mandatory tutorial flow and short
  Windows spot checks remain.

- [Automatic print and background Drive](qa/portrait-v2-print-drive/README.md):
  owner-selected v1 reuse, ordinary --print/--drive profile, durable auto batch,
  startup queue resume and verified result QR; [eleven-item Submit form](qa/portrait-v2-print-drive/windows-checklist.html).
  Source/fixture evidence remains separate from paper/phone/cloud acceptance.

- [Operator Device Health](qa/portrait-v2-operator-health/README.md): earlier
  operator source `ea394e8`, original v1 panel/worker reuse, local safe reports;
  [eight-item form](qa/portrait-v2-operator-health/windows-checklist.html).
- [P5 baseline and runbook](qa/portrait-v2-p5/README.md): source `9433010`,
  [26-item Windows form](qa/portrait-v2-p5/windows-checklist.html), metadata import,
  new Sandbox integration checks and recovery. Its 688-test result predates the
  operator increment; [the test ledger](test_checklist.md) distinguishes both.
- [Sandbox](qa/portrait-v2-sandbox/README.md): isolated keys/backend,
  official simulator, full-price consent and durable photo admission.
- [P3 source record](qa/portrait-v2-p3/README.md) and
  [later preview/button acceptance](qa/portrait-v2-preview-redraw/README.md).
- [Original game reuse](qa/portrait-v2-meong-reuse/README.md) and
  [readable typography](qa/portrait-v2-readable-type/README.md): source-specific history.

P5 is ready for acceptance; merchant/device/cloud/privacy evidence and release
signoff remain separate. The preflight at `0dc6555` is not physical acceptance.
Safe authorized source work may continue while laptop checks wait. The operator
form does not require repeating old photo/game twenty-cycle reports.

## Historical and shared references

Dated QA records, the [P2 gate](portrait-v2-p2-6-to-p2-8-qa-gate.md),
[original integration blueprint](FEAT-021-to-FEAT-022-integration-plan.md),
and v1 release describe their original source and authorization. Their former
“not integrated”, “OPEN”, test counts and next actions do not override current
status or later owner reports. Raw evidence is retained without translation or
rewriting its results; active guidance and audit corrections are in English.

[Advertising/QR slips](advertising-and-qris.md), [printer setup](printer-setup.md),
[retention](photo-retention.md) and [dithering lab](dither-tuning-lab.md) identify
which instructions apply to v1/shared services versus v2. Newer reference-branch
features require their own authorized integration; the 19-branch audit is dated.
