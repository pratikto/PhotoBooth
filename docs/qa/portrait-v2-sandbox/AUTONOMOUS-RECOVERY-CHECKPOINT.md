# Autonomous recovery — session checkpoint and resume contract

**Checkpoint status:** AR-01.a/b IMPLEMENTED / focused VERIFIED OFFLINE, 28 October 2026 (Asia/Jakarta)
**Branch:** `feature/portrait-kiosk-v2-next` (existing; no master merge)
**Recovery implementation:** AR-00 complete; AR-01 local attempt durability implemented; provider repeat-charge gate BLOCKED; AR-02–13 pending
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

## Current implementation checkpoint — AR-01.a/b

- **Date/platform:** 28 October 2026, Asia/Jakarta; Linux cloud, Python 3.12.14,
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
- **Publication:** AR-01 code commit pending; exact remote/tested SHA will be
  pinned in companion evidence after push. Source hashes and raw focused output
  are recorded in the [AR-01 package](AUTONOMOUS-RECOVERY-CREATION.md).
- **Full regression/CI:** pending at this checkpoint. Real Windows/Ubuntu hardware,
  merchant simulator, paper/Drive/retention and production NOT_RUN/not authorized.
- **Blocker:** Legacy repeat-charge semantics unproven; repeat POST/header remains
  disabled. This blocks repeat-charge activation, not independent AR-02 work.
- **Next:** verify AR-01 push/full regression, then AR-02.a tests for a narrow
  booth-authenticated fresh reconciliation (including cached PAID/refund/offline)
  separate from operator resolve. No GUI/photo restore before AR-03–06.
- **Local-only:** work/ scratch evidence/scripts only; no unpushed runtime code
  after the pending commit. No merchant/customer data accessed.
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
