# AR-09 — BUG-023 bounded operator denial audit

29 October 2026. Base/remote verified fc73a486288bc35b2244b9f89f2f278044d6ea22.
Documentation contract before implementation. Reviewed governance/protocol,
checkpoint/handover, index/status/backlog/decisions, master/roadmap/operator/
operations/privacy requirements, bug register, original denial evidence,
CheckoutStore schema/transaction locking and HTTP PIN/rate-limit/action tests.

First increment: additive server-side SQLite denial journal, dormant until the
next HTTP integration. Reuse CheckoutStore BEGIN IMMEDIATE/FULL/WAL and locking.
Store only generated sequence, server timestamp and allowlisted route/reason;
never accept PIN, ticket, order/action ID, request body, peer, bearer, free text
or customer identity. Fixed engineering capacity: latest 4096 events per database,
ordered by generated sequence (clock rollback cannot choose eviction victims).
This rolling diagnostic window is not a compliance archive or financial ledger;
no financial/action/claim/fence/media records may be pruned. No time-based privacy
retention policy or production audit certification is inferred.

Write plus pruning is one transaction; failures propagate and roll back the
entire event write. Future endpoint integration must preserve denial and return
a generic unavailable response when audit cannot commit, never grant authority.
No read/export endpoint, PIN-budget change or authentication bypass is added.
Migration/reopen, allowlist/secret rejection, capacity/clock rollback, atomic
failure and independent-connection concurrency tests precede implementation.

Next: integrate wrong-PIN and rate-limit denials across inspect/resolve/release,
then action replay/cross-order conflicts. Preserve booth authentication, Sandbox
gates, same-action idempotency, ordinary status independence and customer proof.
BUG-023/UX-13 remains OPEN/FAIL until all required HTTP paths are verified.
No production, OPS, new branch/master/default, deployment or physical effects.
Rollback retains additive audit/financial tables; inverse source only.

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
conflicts before restoring UX-13 PASS. See the contract above.
No production/OPS/public ingress/new branch/master/default/deployment/device
operation. Only work/ diagnostics local; no unpublished source patch after push.
Rollback inverse source only; retain additive audit and all financial records.

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
claim/fence/media records. See [evidence](evidence/bug023-foundation-verification.json) for commands/source/digests/limits.
This containing docs-only push is final safe checkpoint; resolve its SHA from
Git log/remote. Only disposable work/ stays local, no unpublished source patch.
No production/OPS/public ingress/new branch/default/master/deployment or actual
device/provider/paper/Drive/deletion acceptance. Retain additive tables on rollback.

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

## PIN endpoint contract before integration

Reuse existing operator identity guard after booth authentication and explicit
Sandbox/PIN gates. Audit only INVALID_PIN and operator RATE_LIMITED in this
increment; pass a static route label, never request path/body/order/credential.
Run SQLite write on existing thread pool, including failure handling, before
returning the original 401 or 429. If audit cannot commit, return generic 503;
never continue into service/provider. Keep same eight-attempt/minute in-memory
budget, ordinary status independence, per-launch PIN rotation and no audit for
unauthenticated booth requests/disabled recovery. Four new HTTP tests reproduce
missing audit/fail-closed behavior: 20 run / four expected FAIL / zero error.
Later replay/cross-order conflict audit remains separate; UX-13 stays FAIL.

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
