# Meong Photobooth development protocol

> **Current post-preview continuation — 4 November 2026:** Work stays on existing `feature/post-preview-qris-checkout`. Start with the [current device guide](qa/portrait-v2-sandbox/POST-PREVIEW-DEVICE-TEST-START-HERE.md), [source-specific evidence and known limits](qa/portrait-v2-sandbox/PP07-DEVICE-READINESS-2026-11-04.md), and [112-case / AR traceability](qa/portrait-v2-sandbox/PP07-SOFTWARE-TRACEABILITY-2026-11-04.md). The later implementation and evidence record takes precedence over older status snapshots below; approved policy and dated history remain preserved. The owner pilot uses synthetic payment. Actual merchant Sandbox, protected cross-process recovery, physical acceptance and production are separate gates. No prior test root, uncertain print or PAID/OWED may be reset to bypass them.

> **2 November 2026 source/test trace:** `0548bc89` and [GitHub Actions #41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) completed **3/3 SUCCESS** (494 Windows, 494 Linux, 54 native, 1,042 test executions, zero failures/errors/skips). [Current PP-07 adversarial QA record](qa/portrait-v2-sandbox/PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md) records the first failed test assertion and correction; no real merchant or physical UAT acceptance inferred.

> **P0 source-to-test verification addendum (2 November 2026):** Refer to [PP-07 adversarial GUI fault-injection record](qa/portrait-v2-sandbox/PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md) for late QR1/QR2 settlement, QR3 no-QR4 UX, uncertain print quarantine and persistent SENDING mock-restart. Keep test-only fixes, production behavior, actual provider/device acceptance and original financial entitlements distinct. Do not use CI green as refund enablement or automatic physical release.

> **Current engineering checkpoint (2 November 2026):** The owner-authorized post-preview branch is running a synthetic pilot, not merely a design. [PP-07 executed CI and limits](qa/portrait-v2-sandbox/PP07-AUTOMATED-SIMULATION-2026-11-02.md): first source b071a5cc passes 490 Windows + 490 Linux + 51 native; newer safety/label code now has exact-source [CI 41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509) **3/3 SUCCESS** (493 Windows + 493 Ubuntu + 51 native, no failures/errors/skips). Historical 'design-only/not-implemented' sections below are dated records. No actual Midtrans/refund/production/physical acceptance has been approved.

> **LATEST owner-approved policy on `feature/post-preview-qris-checkout` (1 November 2026, DESIGN ONLY):** **All** previously agreed post-preview capture/retake/template/payment/Drive/CCP/Recovery Ticket/isolation/privacy/Meong Fly decisions remain binding. **The original Recovery Ticket must ALWAYS appear on-screen for 30 genuinely visible seconds + NEXT while the SAME original ticket is dispatched to the printer ONCE concurrently**, even on printer success. **Refund-first** is now the owner-approved *future* handling for independently verified irrecoverable **PAID merchant-service failures** (MVP preference: original FULL refund) and unambiguously excess duplicate-settled QRIS charges (refund excess only), but **only if merchant-specific Midtrans refund capability, worker safety, idempotency and legal controls are verified**. **Customer loss of a genuinely offered CCP/Recovery Ticket alone => NO_AUTO_REFUND_PROOF_LOST, no tokenless old-photo access**; Meong's failure to offer proof or separately deliver paid photos remains PAID/OWED/remedy and is NOT called customer negligence. Older unconditional NO_AUTO_REFUND and conditional-screen-only prose below is historical/current **legacy paid-first** scope, not new-order authority. **112 new PP tests NOT_RUN; refund API not proven active; no code/refund/production change.**
>
> **Canonical read order:** [Full no-loss owner decision ledger](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) · [refund and proof-loss RF-D01..26](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) · [new operational escalation](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OPERATOR-AND-REFUND-ESCALATION.md) · [master PP flow](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [state security](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [PP-001..112 NOT_RUN QA](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) · [future Codex handover](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-CODEX-HANDOVER.md).


> **Branch-specific owner-approved design — 1 November 2026, NOT IMPLEMENTED.** For NEW orders only on `feature/post-preview-qris-checkout`: select template(s)/copies -> **3 captures and at most one retake per template** -> approve every design -> editable final preview (until provider CREATE_PREPARED) -> immutable one-cart QRIS checkout with private **pre-PAID Checkout Claim Proof** -> independently verified PAID -> original Recovery Ticket **ALWAYS visible 30 seconds + NEXT while exactly one SAME ticket is printed concurrently** -> photo strips only after exact Drive customer URL is verified, with original background upload. Approved: guarded encrypted credential escrow, adaptive phase-aware inactivity without active-session hard cap, QR1/QR2/QR3 renewal **only** for active original visitors after verified expiry, distinct explicit cancel/abandonment, automatic isolation only after worker fence/ACK, and PAID_UNCLAIMED/OWED proof-gated return. No automatic refund, unpaid public media/print, duplicate service or uncertain print replay.
>
> **Execution precedence:** On THIS PP branch, PP-00..07 is the implementation workstream **when separately authorized**; AR-00..13/UAH financial, privacy, ticket, reconciliation, worker isolation, and legacy PAID-before-camera behaviors remain mandatory safety/regression dependencies. On parent `feature/portrait-kiosk-v2-next`, the original AR work priority remains. Historical source status/CI PASS below is not new-flow evidence; **all 112 PP acceptance cases NOT_RUN**; no code, payment, actual Drive, device or master change is authorized here. Read [24 owner decisions and 11 revised flowcharts](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md), [state/security](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md), [112 NOT_RUN cases](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md), [Codex staged handover](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-CODEX-HANDOVER.md).


## Primary rule — 27 October 2026 owner instruction

Read documentation thoroughly, comprehensively and carefully **before any code
change**, then update documentation **after the code change**. Start at the index
and read the current authoritative scope, architecture, decisions, status,
defects, roadmap, contracts and evidence; follow affected links and reconcile
later owner corrections. A keyword-only search is insufficient. Record reviewed
sources and keep code, tests, limitations and handover synchronized. If scope
changes, review its additional documents before further code. This rule is also
persisted in [AGENTS.md](../AGENTS.md) and the continuation prompt.

Development platform: Windows. Intended mini-PC deployment: Ubuntu. Validate
portable behavior and document platform-specific startup/device acceptance;
Windows success alone is not Ubuntu acceptance.

Effective **18 October 2026**; current GUI v2 policy reconciled **25 October 2026**.
Current explicit owner instructions take precedence over earlier historical rules.

## Current scope and branch

For historical original AR work, continue on **`feature/portrait-kiosk-v2-next`**. For new post-preview design or separately authorized implementation, work only on **`feature/post-preview-qris-checkout`**. Never automatically switch branches. GUI v2 is the
intended future primary branch; GitHub default remains `master`, and `main.py`
remains v1. Do not create a new branch or restart completed P3/P4 work by default.
Default change, rename, merge, launcher replacement, release and deployment are
separate operations requiring the owner's corresponding instruction.

The owner approved P3, P4 DEMO/MOCK, P4b Sandbox/P5 preparation and staged pushes,
then safe source continuation while laptop acceptance waits. The read-only
Device Health/report increment is complete in source. The English documentation
reconciliation completed at f36ebad; the subsequent owner report authorizes the
BUG-018 operator input correction on the same branch. Existing scope
approval does not need to be requested again for each small change.
The owner then prioritized printing and Drive only, selecting automatic printing
as v1 with background upload; watchdog is postponed. Existing opt-in, isolation,
uncertainty and retention boundaries remain.
[Handover](DEVELOPMENT_HANDOVER.md) · [decisions](DECISIONS.md).

## Reuse and delivery

1. Inspect current source/HEAD, defects, roadmap and relevant reference branch
   before implementation. Refresh its remote SHA read-only; reuse working UI,
   renderer, controller, worker, assets and logic. Record source/provenance and
   concrete adapter exceptions. See [AGENTS.md](../AGENTS.md).
2. Keep changes small and reviewable. Preserve unrelated local/user work.
   Test the affected behavior, fix failures, commit, push to the authorized branch
   and verify remote HEAD before the next stage. Report the delivered stage.
3. Run one applicable full regression after the final functional change; repeat
   broad checks only for new changes/failures/unresolved concerns. Review GUI
   screenshots at 800×1280/452×900 and relevant additional sizes.
4. Documentation-only changes use link/anchor/reference/hash and scope checks;
   do not spend Actions credits rerunning successful GUI workflows. Preserve
   functional/PR checks and the existing concurrency policy.
5. Plans/backlog are not permission for new code. Follow the authorized task;
   stop only the dependent part when evidence/access is missing, continue safe
   independent work, and state the actual remaining blocker.

## Session-limit continuity and incremental Git pushes — 28 October 2026

The owner explicitly prefers **micro-commit + immediate push** as work progresses,
not a single push at the end of a long Codex conversation. ChatGPT/Codex may hit
its five-hour usage limit unexpectedly; the last verified remote commit and a
durable handover must be sufficient to restart without repeating completed work.

1. Break every numbered roadmap stage into narrowly scoped, testable
   micro-increments. Commit/push each safe meaningful unit to
   `feature/portrait-kiosk-v2-next` after focused checks; independently verify
   local and origin HEAD. Target checkpoint opportunities roughly every 30–45
   minutes of active work, without empty or unreviewed commits.
2. Prefer remote, auditable, reversible checkpoints over local-only commits or
   stashes. Keep tests, code and corresponding documentation traceable to the
   exact source SHA. Do not push unrelated work, credentials, customer photos,
   local SQLite databases, logs or broken/unsafe runtime changes.
3. At the end of **each micro-increment** and before a session cutoff, update
   [the recovery checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md)
   (when on the recovery roadmap) and keep
   [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) synchronized. Record
   current AR-stage/substep, done vs pending, last remote verified SHA,
   tests with PASS/FAIL/SKIP/NOT_RUN, source/OS, blocking facts, changed paths,
   unpushed/dirty files and the precise next command/decision. Push the
   checkpoint even if the next implementation step remains incomplete.
4. Do not push a knowingly unsafe partial code patch to meet a time limit.
   Instead commit safe separable tests/docs or disabled functionality, record
   incomplete local-only work and state that it cannot be reconstructed from
   GitHub. Never claim an unpushed local patch was saved remotely.
5. On the next session, inspect branch, `git status`, last commits and remote
   HEAD before `git pull --ff-only`; preserve any dirty work, read the
   checkpoint and resume from the first **unfinished** verified substep.
   No new branch, reset, reimplementation of completed increments, force push,
   merge, production activation or relaxation of safety gates.

## Feature, bug and approval discipline

Review ideas for business priority, impact, compatibility, readiness, complexity,
dependencies and regression risk using current source. Re-rank the unified
backlog after material new evidence; stable IDs do not imply execution order.
Distinguish stage names P0–P5 from priority labels P0–P3.

Lifecycle: IDEA → REVIEW → BACKLOG → APPROVED → IN PROGRESS → IMPLEMENTED →
VERIFIED → RELEASED, with BLOCKED where needed. Implemented means written;
verified means applicable evidence passed; released requires explicit operational
acceptance. Reserve DONE/CLOSED for the relevant acceptance/owner decision.

Severity: S0 unsafe/payment integrity/data loss/unusable kiosk; S1 failed core
session; S2 material degradation/workaround; S3 cosmetic/nonblocking. Preserve
observed impact, environment, reproducibility and limits. Monitor accepted fixes;
do not patch a working path solely because an old failure remains in history.

## Evidence and rollback

Before code work record task/scope, base branch/SHA, affected modules, acceptance,
known blockers, tests and rollback. During work retain exact commands, tested
source, OS/dependencies, PASS/FAIL/SKIP/NOT_RUN and artifacts. A successful CI job
can contain skipped cases; identify them rather than relabeling them PASS.

Keep automated fixture results, owner-reported device behavior, preflight,
merchant simulator and physical acceptance separate. Do not borrow missing
HEAD/device values from a different report. Sound state is not audible output;
spool success is not paper; retention acknowledgement is not cloud deletion;
QR/GUI PAID is not provider settlement.

Preserve dated failures and later retests. Use scoped inverse source commits
after inspection for rollback; preserve all transaction journals, consumed
attempts, photo/print manifests, reports and customer data. No automatic
charge/capture/print replay or deletion to clear an uncertain state.

Before a release, assess blocking defects, physical/provider/privacy gates,
source/CI evidence, owner signoff, baseline and rollback. A source tag or default
branch change does not certify a customer deployment. The immutable v1 source
release remains [v1.0.0](releases/v1.0.0.md); its 2026-10-19 approved merge does
not authorize a future v2 merge.

## Documentation synchronization and authority

| Document | Authority |
| --- | --- |
| [DECISIONS.md](DECISIONS.md) | Owner-confirmed product/scope direction, not implementation proof |
| [FEATURE_STATUS.md](FEATURE_STATUS.md) | Current source and acceptance boundaries |
| [bug_tracker.md](bug_tracker.md) | Stable defect register and monitoring |
| [test_checklist.md](test_checklist.md) | Source-specific evidence, owner reports and manual gates |
| [next_step.md](next_step.md) | Unified outstanding work/proposed feature inventory |
| [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) | Current checkpoints/continuation, not a second backlog |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Source layers; detailed interfaces in the technical design |
| [CHANGELOG.md](CHANGELOG.md) | Actual dated changes |
| [README.md](README.md) | Documentation index; root README is current launch guidance |

Update changed facts in the same or linked companion commit; do not duplicate a
detailed record everywhere. Current source and later owner instructions/reports
supersede older status/ordering statements, while original evidence stays dated.
Historical references cannot silently approve new implementation or close bugs.
Before completion check links, scope, exact published commit/remote and evidence
limits. Final reports identify changes, checks, commits, outstanding gates and any
material limitation. [Continuation prompt](DEVELOPMENT_PROMPT.md).
