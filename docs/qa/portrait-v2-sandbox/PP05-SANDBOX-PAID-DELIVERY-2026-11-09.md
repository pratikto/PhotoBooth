# PP-05 B4 — original Sandbox paid-delivery authority

9 November 2026. Existing feature/post-preview-qris-checkout; starting source
89df55a / documentation149ee589, plus recovered historical R4 evidencef92de7e5.

## Implementation contract before source changes

Reuse original Drive binding, approved-media importer, strip preparer, dispatcher
and checksum/upload monitor. Preserve the existing explicitly selected mock path;
never remove its constructor guard or place a dummy payment provider in native UI.
Introduce a distinct exact Sandbox backend binding over the SAME payment ledger,
fixed MidtransSandboxClient, original protected Recovery Ticket presentation and
backend-owned typed Drive client/workspace. No self-described provider/protector
or arbitrary native caller can select Sandbox authority. Recheck original active
owner/group and fresh independent settlement before allocating a paid folder;
require genuine ticket dismissal and classify receipt uncertainty before output.

The downstream original components accept this exact backend binding without
pretending it is an incomplete synthetic fixture. Retain frozen artwork/photo
hashes, same original transaction on lost response, individual verified Drive URL,
SENDING-before-I/O, shared receipt/strip lane and no uncertainty replay. Financial
status does not release a booth or close OWED. Keep default host health/customer
launcher gated until authenticated delivery/client/worker lifecycle integration
is complete. This first increment assembles and tests the core; mounting routes,
native adapter, original worker/claim/release, live printer configuration and full
protected customer profile remain separate unfinished source work.

Reviewed current AGENTS/protocol/handover/provider-native continuation, approved
flow/security/receipt contracts, latest B3 receipt and host reports, original
paid Drive/media/strip/print/delivery and API/protected presentation source/tests.
All provider/Drive/printer transport in this campaign is explicitly synthetic;
no actual payment, cloud publication, paper, refund or deployment is authorized.
Focused tests precede a safe micro-commit/push with remote SHA verification.
Rollback scoped source only; preserve original journals/media/custody/OWED.

## Execution

IN PROGRESS. No new test PASS is assigned by this contract.

## B4-A focused execution

Distinct OriginalSandboxPaidDriveBinding validates exact protected ticket/payment/
fixed Sandbox provider/checkout/typed Drive dependencies, then shares the original
Drive algorithm. Existing mock constructor remains explicitly mock-only. Original
media/strip/monitor/dispatcher constructors accept only this exact backend chain
without fixture flags. Purchased strips must use the SAME actual ThermalPrinter
and lane already owned by the protected receipt presentation. Every original
owner/frozen-media/folder/job/receipt and uncertainty check remains in the core.

Fourteen new methods exercise construction with no I/O; mode/OS/type/identity
refusal; unpaid/not-dismissed/uncertain-ticket denial before reserve consumption;
fresh GET/reopen identity; lost bind reply on the same original transaction;
unverified URL/provider outage; stale/foreign/retired owner; original media/
composition/pending upload and once-only actual ThermalPrinter raster submission
with fake network; wrong-lane denial; partial bytes retained as UNCERTAIN/OWED.
Immediate NEXT reuses the original ticket's existing 30-second independent-GET
window and preserves provider pacing. Stale evidence requires a fresh original
GET; provider failure holds without another Drive call.

Focused connected scope: **85 PASS, zero failures/errors/skips, 25.836s**.
Initial12-method run had8 failures because this old environment lacked ESC/POS;
installed the already-required runtime dependency (no guard bypass). Next run
had6 errors/1 failure from the original polling floor and a fixture attempting a
forbidden SUBMITTED->UNCERTAIN edit. Source now reuses valid recent GET evidence;
receipt uncertainty is produced by an actual synthetic partial send. A later
85-method probe had one error from deliberately advancing the fixture clock
before ticket issue; negative pre-effect cases now keep the original clock.
Historical failures and final logs are retained privately with committed digests.
Windows uses actual DPAPI; positive Linux tests explicitly reuse the existing
wrapped in-memory protected backend fixture, not actual Ubuntu acceptance.

No upload worker is started by these tests; honest pending/not-configured status
is asserted. No customer HTTP delivery route, scoped native adapter, worker
shutdown/claim/release integration, complete merchant launcher or real printer
configuration is mounted. Host health remains fulfillment_enabled=False. Those
are next SOURCE tasks. Final new-source regression/CI remain pending here.

## B4-B contract before mounting the backend seam

Add an optional exact backend actor over B4-A and original BoothDriveWorker.
Expose only authenticated original-owner prepare/status/next-batch requests;
amount, copy count, printer, folder, path and provider evidence are not inputs.
Default factory/host remains unmounted and fulfillment_enabled=False. Trusted
factory opt-in assembles the original chain; a bounded native transport adapter
accepts only exact scoped redacted status, not photo paths or financial authority.

Stop retires new commands immediately, signals the original uploader and checks
its ACTUAL thread completion. stop() returning None or a closed socket is not
quiescence. In-flight binding/printing/upload keeps the ledger/process lease;
API lifespan/host callback must not close beneath it. Preserve one original
receipt/photo printer lane, verified URL, no replay after lost response or
UNCERTAIN, and original OWED. Tests use fake external transports/work queues;
real worker lifecycle is exercised separately at a controlled thread barrier.
Full native screen/profile and proof-gated worker claim/release remain next.

## B4-B focused execution

OriginalSandboxPaidDelivery now serializes original prepare/status/next-batch
operations and owns the actual BoothDriveWorker. Optional authenticated delivery
routes accept only original owner visit/generation; no amount, copy count,
printer, folder, path or provider evidence is caller input. build_sandbox_app
assembles it only with explicit trusted paid_delivery_enabled=True. Default
host/customer launcher stays unmounted and health fulfillment_enabled=False.
The typed PostPreviewDeliveryClient accepts only the exact Sandbox/role/group/
booth/generation envelope, verified-folder URL, bounded counters/original print
states and consistent redacted observations. Retired late responses are denied;
no local paths, physical-paper success, media/financial grant or release claims.

Shutdown retires commands, signals the original worker, refuses while an actor
operation holds its lock, and checks the uploader's actual thread after stop().
The uploader's None-returning stop method is not mistaken for quiescence. API
lifespan suppresses its close callback while active; SandboxHostRuntime retains
its original ledger/kernel lease. Actual live-thread barrier tests prove stop
False, competing-host refusal and successful original release after thread exit.

Thirteen new API/client/lifecycle methods and affected core/host/API/receipt/
print/delivery scope: **100 PASS /zero failures/errors/skips,42.727s**. Initial
25-method API/core probe also PASS (6.787s). External upload scheduling is
explicitly stubbed in request tests; actual worker-thread lifecycle is verified
separately. This is not actual upload, merchant, paper, native-screen or device
acceptance. Final source-matched broad regression and CI remain pending.

NEXT: connect the scoped delivery adapter into the protected native facade and
screens/automatic dispatch, bind exact original collector/worker shutdown into
proof-gated fresh-PAID claim/WAIT/FREE/PREPARE/ACK, then complete customer launcher
and real printer configuration. No dummy provider or mock-guard removal. Default
health remains disabled until the full customer profile is safe. Real refund/
status/operations, supported-device restore and final new-source qualification
remain unfinished. Historical R4 two-hour evidence applies only to824b6ae7.

## BUG-049 — graceful idle-uploader shutdown

A separate lifecycle probe found that zero-wait API shutdown could classify an
idle original uploader as active immediately after stop signalling, suppressing
the shutdown callback. A meaningful new normal-close regression reproduced one
ERROR (RuntimeError), zero skips. API lifespan now grants a bounded one-second
exit wait; direct host close remains nonblocking/truthful by default. The live
blocked-I/O tests still require stop=False and keep ledger/kernel ownership.
No timeout permits force-kill, false worker ACK, booth release or print replay.

Corrected affected scope **101 PASS /zero failures/errors/skips,43.116s**,
including normal idle exit, genuine active-thread refusal, API close callback
retention and actual host kernel-owner retention. The first all-opt-in diagnostic
run at41707ae9 was deliberately interrupted after293.454s when this missing case
was discovered; exit-2/KeyboardInterrupt, no full verdict. Logs/metadata retained.
That source's superseded CI is not the final verification. Run final regression
and current CI against the corrected source; no old count is relabeled new PASS.

## Corrected-source final local regression

Source `8e976a9a8b5ac697a05cce5ca8e6057fdf70deb1`: **1,934 all-opt-in local PASS**, 1843 normalized distinct method IDs, zero failures/errors/skips; **622.324s** process duration. All 28 new method IDs observed PASS. GUI/audio/video/model opt-ins enabled, public assets independently size/hash-verified, virtual transports/devices only. No new actual merchant/paper/cloud or two-hour final-profile qualification. [Exact source hashes, methods, commands/log digests and CI](evidence/pp05-sandbox-paid-delivery-final-2026-11-09.json).

CI42627272293 at the SAME source: Ubuntu717 PASS and native81 PASS, completed logs inspected, zero failure/error/skip; all28 new methods observed PASS in Ubuntu. Native owner packaged preflight and screenshot steps succeeded. Windows remains pending at this checkpoint. Superseded2e38f207/41707ae9 runs were cancelled by normal workflow concurrency; no complete PASS is assigned to them.
