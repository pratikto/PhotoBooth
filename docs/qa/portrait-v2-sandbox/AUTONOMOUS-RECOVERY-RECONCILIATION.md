# AR-02 — fresh payment reconciliation

28 October 2026 (Asia/Jakarta), FEAT-007/020/022. Owner explicitly requests all
AR stages in dependency order, retaining immediate safe pushes. Base remote
`6339d13817a74fcaf8c0ae3d76d9b73e73e2ed5c`, runtime `017b417`.

## Pre-implementation review and bounded increments

Reviewed AGENTS, protocol/prompt, current handover/checkpoint, master plan,
roadmap, provider contract, operations/test matrix, AR-00/01 contracts and
existing checkout/backend/store/API/client/session/native adapters and tests.
Previously reviewed project index/architecture/decisions/status/defects/backlog
remain applicable. No unreviewed branch reuse or archive traversal.

AR-02.a: authenticated booth-only provider GET reconciliation separate from
operator resolve; fresh settlement before claim and first STARTED, including
cached PAID. No new grant/service mutation from read-only reconciliation.
Unknown/404/refund/review/terminal are explicit, never payment authority from
cached PAID. Tests first: cached refund/outage, wrong booth/key, no operator
bypass, no duplicate grant, no provider POST, API event-loop independence.

AR-02.b: durable per-order polling reservation, bounded jittered backoff and
fencing against stale provider replies; migrations tested before schema work.
AR-02.c: restart/RECOVERY worker reconciliation preserves existing phases and
private-photo hold, with a single immediate check after reopening. No automatic
camera reentry; customer proof and GUI work belong to AR-06/07.

Acceptance: same identity, current valid settlement before new admission,
fail-closed outages, stable one-use grant, bounded retries, signed-event and
cancel/settlement integrity. Full regression follows final functional increment.
Physical Windows/Ubuntu, merchant account, paper/Drive and production NOT_RUN.
Rollback via inverse source commits; retain additive ledgers and all old data.
Legacy repeat-charge contract stays blocked; never add guessed headers/resend.

## AR-02.a verification

Initial nine new tests: 3 FAIL / 7 ERROR (some cases exercise more than one
assertion); after implementation focused group **120 PASS / zero FAIL/ERROR/SKIP**.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_checkout_reconciliation test_checkout_creation_attempts test_autonomous_recovery_baseline test_checkout_backend test_checkout_durability test_qris_session test_qris_http_v2 test_qris_api test_qris_recovery test_qris_kiosk_client`.
Raw reproduction/result remain in work/ar02a-before.txt and work/ar02a-tests.txt
until final evidence publication. GET-only reconciliation cannot allocate a grant,
resolve an operator action or start capture. Claim and first STARTED independently
require fresh verified settlement. Existing protocol regression passes.
