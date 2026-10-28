# Autonomous recovery — session checkpoint and resume contract

**Checkpoint status:** AR-07.b1 focused VERIFIED / roadmap IN PROGRESS, 28 October 2026 (Asia/Jakarta)
**Branch:** `feature/portrait-kiosk-v2-next` (existing; no master merge)
**Recovery implementation:** Source work progressed through AR-08.b1; later stages and external gates remain unfinished
**Latest previously tested/pushed functional source:** `6d53d91fcfcad6083aee9f17ac8f80cf635fdf2f` (AR-07.a); current increment and tests below
**Historical audit baseline:** `2e5efe5d281a93fe8d22e53309a50147764d2939`
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

## Current implementation checkpoint — AR-08.b1

- Base / last verified remote: `4863aa3009d1c23e0b710ea9340db6a931a19623`.
- Completed: persist paid-unfulfilled issues without altering customer financial rights. Focused 56 PASS, zero failures/errors/skips; five new durable/concurrent/migration/authenticated HTTP issue cases; CI registration included.
- Publication SHA: this increment will be pinned after its verified push by the
  next checkpoint; obtain containing commit from Git history.
- Remaining / exact next step: AR-08.b2 persist local reporting intent before API I/O, retry after restart and route native camera/photo faults into the ledger; then AR-09–13.
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
