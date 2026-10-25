# Meong Photobooth development protocol

Effective **18 October 2026**; current GUI v2 policy reconciled **25 October 2026**.
Current explicit owner instructions take precedence over earlier historical rules.

## Current scope and branch

Continue authorized work on **`feature/portrait-kiosk-v2-next`**. GUI v2 is the
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
