# Meong Photobooth documentation — GUI v2

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
