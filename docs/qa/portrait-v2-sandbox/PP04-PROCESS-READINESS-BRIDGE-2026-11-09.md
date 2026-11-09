# Post-preview original-worker readiness across the backend process boundary

9 November 2026 · branch `feature/post-preview-qris-checkout` · base `6c0ee19`.

## Bounded implementation contract (before source changes)

The existing trusted readiness adapter holds the live camera/PhotoJobs/launch
lease in the same process as the payment coordinator. A separate merchant
backend cannot observe those Python objects. Passing caller readiness booleans
or moving merchant credentials into the native GUI would break the PP security
contract. Add one private, bounded local-process bridge for exact scoped worker
observations, reusing LocalChargeReadiness, OriginalWorkerReadiness,
TrustedChargeReadiness and ReadinessScope. No public HTTP readiness input.

Only camera/disk/media/artwork/printer-route/worker-ownership observations cross
this private channel. Payment authorization remains backend-authenticated;
Drive API/sharing/capacity remain independently observed by the backend.
Preserve original timestamps, complete field validation, nonce/scope matching,
existing two-second freshness and same-original create/reconcile policy.
Disconnect/timeout/malformed/stale/foreign data must hold charge, not reconnect
or fabricate READY. Use bounded JSON, never pickle or credentials/media/QR.

Test real independent process transport plus wrong generation/hash/group/nonce,
truncated/oversized frames, timeouts, concurrent use, stale replies and shutdown.
First prove the missing seam with a failing test, then implement/focus-test and
push this independently reviewable increment before mounting the merchant host.
The bridge is not a platform credential vault or full provider integration.

Authority reviewed: AGENTS/protocol; latest handover/checkpoint/STAR and PP
owner/decision/security contracts; Midtrans provider and saved-settings contract;
existing readiness/authority/API/client/payment/lifecycle source and tests.
Original merchant/paper/Drive/refund/production acceptance remains separate.

## Execution

Implemented an anonymous connected socket-pair protocol with bounded JSON frames,
strict field/scope/nonce matching and an absolute round-trip deadline. A partial
read cannot extend the deadline. Concurrent requests cannot consume each other's
reply. Malformed/duplicate/oversized/truncated messages retire the channel;
there is no reconnection or replay fallback. Original observation timestamps
survive transport unchanged. Backend combines the six allowed worker facts with
its own authenticated payment scope and independently observed Drive facts.

The original LocalChargeReadiness and OriginalWorkerReadiness are used in a
connected real local HTTP/ledger checkout test. A live unrelated capture worker
holds readiness even with healthy backend payment/Drive checks. An independent
spawned Python process test exercises the actual socket transfer and shutdown.

Before implementation: the first independent-process method ERROR because the
bridge module did not exist (one run, zero failures/skips). First eight bridge
methods PASS; first connected regression 91 PASS in 23.806s. After adding
absolute-deadline, anonymous/local-stream, duplicate-field/typed-report and
shutdown hardening: final related readiness/authority/payment/API scope **93
PASS in 23.087s**, zero failures/errors/skips, exit 0. Twelve new bridge methods
plus one connected authority method are registered by the existing backend
workflow groups. No workflow expansion or manual broad CI rerun.

The earlier source a97feda has now completed CI42558244702: Windows 598 PASS
(700.794s), Ubuntu 598 PASS (146.042s), native 74 PASS (162.711s), all three
SUCCESS and logs inspected. Those results predate this bridge increment.
New-source full/Windows CI must be inspected separately after publication.

This seam is **unmounted** until the separately owned post-preview Sandbox host
and guarded native profile are wired. It neither moves merchant keys into the
GUI nor changes any mock-only, paid fulfillment, claim, isolation, print or
refund guard. Merchant account, real camera/paper/Drive, Windows socket-process
and full product acceptance remain separate. Local process transport here was
verified on Linux; source-matched Windows execution remains required.

Next: construct the isolated post-preview backend host over this readiness
bridge and the existing fixed MidtransSandboxClient, API, private ledger and
read-only Drive probe, then wire the supported protected native profile. No
production/money activation follows from this increment. Roll back only this
new module and associated tests; preserve original financial/media journals.

## Windows spawn-start boundary refinement

Before final source qualification, the independent-process fixture now waits
for the actual child's ready Event before measuring a readiness request. Spawn
and module-import latency are not the protocol latency. The production socket
round-trip deadline remains two seconds; startup has a separate bounded 10s
fixture wait. This prevents Windows cold import from being mislabeled as an
incorrect transport response. All twelve bridge methods PASS after the change;
final exact-source full regression/CI is recorded in the continuation checkpoint.
