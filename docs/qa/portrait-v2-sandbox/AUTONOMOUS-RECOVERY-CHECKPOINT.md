# Autonomous recovery — session checkpoint and resume contract

**Checkpoint status:** AR-00.a/b VERIFIED OFFLINE, 28 October 2026 (Asia/Jakarta)
**Branch:** `feature/portrait-kiosk-v2-next` (existing; no master merge)
**Recovery implementation:** AR-00 contract/fixtures complete; AR-01–AR-13 pending
**Last audited functional baseline:** `2e5efe5d281a93fe8d22e53309a50147764d2939`
**Current documentation handover:** See `docs/DEVELOPMENT_HANDOVER.md` and verify current remote HEAD; never assume the HEAD printed in a dated checkpoint is still current.

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

## Current implementation checkpoint — AR-00.a/b

- **Done:** [Frozen field/state/migration contract](AUTONOMOUS-RECOVERY-BASELINE.md)
  and six offline baseline tests, including actual abrupt child exit before
  provider call and after synthetic acceptance, same-order retries/404 hold,
  optional fraud decisions and restart capture hold. Runtime source unchanged.
- **Base / last verified remote:** `f6736b7c739e3317e3bcc4506edb250f9e47d92b`.
  The AR-00 commit will be pinned by its companion checkpoint after push.
- **Focused checks:** Linux cloud / Python 3.12.14 / Pillow 13.0.0:
  `.venv/bin/python tools/run_kiosk_unittests.py test_autonomous_recovery_baseline test_checkout_backend test_checkout_durability test_qris_session test_midtrans_sandbox test_midtrans_verify test_qris_kiosk_client test_payment_quote`:
  **87 PASS, zero failures/errors/skips**. `git diff --check` PASS.
- **Changed:** two fixture/test files, baseline contract and associated docs.
  No schema/data migration, private configuration or runtime changes.
- **Not done:** AR-01 attempt migration/fingerprint/phase, AR-02 fresh admission,
  AR-03–13. Full suite/native/Windows/Ubuntu hardware/merchant/print/Drive NOT_RUN.
- **Blocker:** repeating Legacy charge remains disabled pending exact official
  contract and merchant evidence; independent durability work can proceed.
- **Next:** AR-01.a write migration/immutable-attempt tests, then additive
  backend attempt ledger; preserve same-order GET-only retries.
- **Local-only:** `work/` scratch scripts/output; no unpushed runtime code.
- **Rollback:** inverse AR-00 tests/docs only; retain all payment/customer data.

## Historical bootstrap checkpoint — documentation publication

- **Done:** Comprehensive unattended-first master design, provider contract, AR-00–AR-13 roadmap, failure-injection matrix, operator/customer runbook, and repository prompt/process micro-push rules are published to the existing branch.
- **Not done:** AR-00 source baseline test fixtures; provider verification; any recovery runtime code or device/merchant tests. All new stage checks are NOT_RUN.
- **Known previous runtime state:** Existing operator-authenticated recovery HTTP/backend code at `2e5efe5`; native launcher and GUI not yet integrated, and unattended photo reconstruction not yet implemented at the audited baseline.
- **Open provider question:** Exact Legacy Midtrans QRIS charge-idempotency contract; invoice-specific five-minute key rule does not establish the Legacy QRIS charge contract.
- **Next action for Codex:** Verify current branch/HEAD/dirty tree, read all linked docs, then start `AR-00.a`: inventory exact existing payment/fulfillment/photo state and prepare deterministic test fixtures without altering merchant settings or payment state.
- **Sensitive/persistent data:** No account keys, customer photos, SQLite databases, provider payments or journals are changed by documentation publication.

When future code increments begin, replace **only this latest bootstrap status section** with a dated implementation checkpoint while retaining prior distinct evidence by link/appendix as useful. Commit and push the checkpoint after each logical stage and before session cutoff.
