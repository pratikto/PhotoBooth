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
