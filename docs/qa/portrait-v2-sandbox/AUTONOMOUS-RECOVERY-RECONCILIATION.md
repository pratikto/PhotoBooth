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

## AR-02.b durability and verification

Additive `checkout_reconciliation` table: order_id, generation, token,
lease_until, next_at, failures, evidence_revision, checked_at, outcome,
provider_state, observed_at. No old field/journal migration. A transaction
reserves one bounded 45-second GET lease, then releases SQLite before network
I/O. Valid evidence and schedule commit together; every evidence writer advances
revision. A stale/replaced/expired token or changed revision cannot authorize
admission or overwrite a newer observation. Claim/STARTED may demand an urgent
fresh check, but cannot bypass an active lease. Ordinary observation polling is
10 seconds; unknown/404 failures use jittered 10/20/40/60 seconds capped at 60.
No cached proof is returned as checked when throttled. Clock rollback reanchors
a bounded hold; it never extends payment/photo expiry or manufactures a proof.

Initial scheduler tests: 2 FAIL/1 ERROR before implementation. Final focused
command as AR-02.a: **126 PASS / zero FAIL/ERROR/SKIP**, including three extra
migration/lease-expiry/clock cases. Temporary-db upgrade preserves payment/grant
bytes. Rollback preserves this table; old source may ignore it and all prior
financial records remain readable. Actual process/power-loss and deployment
acceptance remain separately gated; final full regression still pending.

## AR-02.c restart and existing native worker integration

Source retains interrupted STARTING/STARTED and a fixed recovery reason in
version-1 journal metadata. On reopen, RECOVERY makes a private provider GET
observation through the existing single-flight worker; phase/transaction/grant
remain held and no old images or countdown are exposed. Local monotonic retry
matches backend retry_after, bounded 1–60 seconds. Legacy clients without this
method keep the original hold. Native RECOVERY/UNCERTAIN now participates in
worker checks, without new permission/reset controls or auto-shutter.

Authenticated restart/connectivity trigger may bypass error backoff once, then
its persisted priority_after prevents another immediate bypass for ten seconds.
It cannot bypass an active request. The additional column migrates under a write
transaction; row/financial state are preserved. No unauthenticated force flag.
Initial four restart tests: three FAIL; priority test initially ERROR before
implementation. Final source: **152 focused PASS / zero FAIL/ERROR/SKIP**, including
native Sandbox HTTP→photo handoff and existing lifecycle/QR tests. Command extends
AR-02.b group with test_qris_reconciliation_session, test_kiosk_v2_sandbox and
test_kiosk_v2_sandbox_widgets, in SDL offscreen/dummy-audio cloud environment.
Full regression follows final functional roadmap increment; actual devices and
merchant acceptance remain NOT_RUN. Next dependency: AR-03 durable fulfillment.

## AR-02.d — native connectivity restoration, 29 October

The earlier AR-02.c priority seam now has a passive Windows NLM/Ubuntu
NetworkManager producer mounted on the existing Sandbox worker. Five-second
sampled offline→online edges bypass local retry only for same-order observation;
persisted backend priority/lease/revision and customer ownership remain intact.
103 focused PASS; actual OS/merchant reconnection and final full/CI are separate.
[Contract, exact evidence and limitations](PAY08-CONNECTIVITY.md).

## Final AR-02.d verification — 29 October 2026

PAY-08 / AR-AUDIT-002 **SOURCE VERIFIED**. Functional source `e0dc59435772148be86449c55140d4b9be2f6364`:
**1117 run / 1114 PASS / 3 optional palm SKIP / zero failure/error**, 335.317s,
GUI/audio/video opt-ins, Python 3.12.14/Debian 13.6, SDL offscreen/software GL/
dummy audio. Native video PASS. Reader: 9 focused PASS; integration: 103 focused
PASS. Test/workflow-only portability source `c94696d243c6a345182857d28d249d2d01d7d05b`: **49 focused PASS**,
zero failure/error/skip, 1.389s Linux and 11.955s Windows CI.

[CI 40809459547](https://github.com/pratikto/PhotoBooth/actions/runs/40809459547)
at c94696d: **all three jobs SUCCESS**. Its application/tools Git trees exactly
match the full-run e0dc594 source. Tests differ only by explicit fixture lease
cleanup; no assertion changed. The full run is not relabeled as a c94696d test
run. Initial Windows missing-qrcode failure at 40808591124 is retained;
reader CI 40807439692 also succeeded. [CI steps/counts](evidence/pay08-final-ci.json).

**28 clean native PNGs / four QR checks PASS**, both 800×1280 and 452×900 at
c94696d. Dimensions/hashes/phase transitions checked; selected claim/resume/
capture/isolation layouts inspected. Raw ticket QR pixels/payloads/logs remain
untracked private work/; only safe verdicts/manifests/digests are published.
[Exact commands/trees/skips/digests/native hashes](evidence/pay08-final-verification.json).

Current matrix **45 PASS / 1 FAIL / 0 SKIP / 9 BLOCKED / 14 NOT_RUN**.
Overall AR conformity audit remains IN_PROGRESS; BUG-023/UX-13 denial audit OPEN.
Actual Windows/Ubuntu OS reconnection, merchant/provider, phone/paper/Drive/
retention/privacy/operations and release gates remain NOT_RUN/BLOCKED.
Unknown/unavailable OS hints fall back to existing polling; this is no universal
Internet/provider reachability guarantee. No production or future OPS activation.

Next dependency: **AR-03 CAP-01–05 exact allocation/STARTED process-exit fixtures**
plus PAY-18 lost service replies, then remaining retake/COMPLETE/disk evidence and
AR-09 denial audit. Never repeat completed charge/reconciliation work or clear
customer state. No unsafe unpublished runtime patch; only disposable work/ local.
