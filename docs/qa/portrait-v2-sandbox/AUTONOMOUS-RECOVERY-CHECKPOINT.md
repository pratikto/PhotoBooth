# Autonomous recovery — session checkpoint and resume contract

**Active owner task, 29 October:** fresh AR-00–AR-13 implementation conformity
review, IN_PROGRESS. Evidence baseline checked at f8167d8; functional source f72fdbc
unchanged. [Review checkpoint](AR00-AR13-CODE-REVIEW.md). Finish source review and
confirmed reproductions before making a final conformity claim. Prior readiness
report below retains its dated conclusions and remaining gates.

**Checkpoint status:** AR-12 evidence reconciled / AR-13 assessment COMPLETE (CONDITIONAL); external and exact fault gaps OPEN, 29 October 2026 (Asia/Jakarta)
**Branch:** `feature/portrait-kiosk-v2-next` (existing; no master merge)
**Recovery implementation:** source through AR-12.f; AR-13 readiness report published; full matrix/device acceptance and release are not complete
**Latest application source:** `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`; full 1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors; matching CI 40767441201 three jobs SUCCESS.
**Historical audit baseline:** `2e5efe5d281a93fe8d22e53309a50147764d2939`
**Current documentation handover:** See `docs/DEVELOPMENT_HANDOVER.md` and verify current remote HEAD; never assume the HEAD printed in a dated checkpoint is still current.

## Documentation check — latest AR-13 status confirmed

Current source-tree IDs and live matching CI confirm the newer f72fdbc assessment
above. The 635de92 1094-case report is historical; its recovered provenance is now
linked in [validation](AUTONOMOUS-RECOVERY-VALIDATION.md). Do not restart at AR-09
or equate the AR-13 assessment to complete fault coverage/production approval.
The active conformity review remains IN_PROGRESS, with PAY-06 the first exact
source-evidence gap. No new test run/runtime/OPS work was done by this docs check.

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

**First unfinished source evidence:** PAY-06 exact evidence/pre-DB-commit
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
