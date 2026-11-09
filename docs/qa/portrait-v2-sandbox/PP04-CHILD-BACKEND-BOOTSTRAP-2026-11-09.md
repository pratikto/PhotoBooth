# PP-04 original child backend/bootstrap continuation

9 November 2026 · existing feature/post-preview-qris-checkout · base71d8160.
Owner explicitly authorizes continued implementation, staged pushes and Ubuntu
mini-PC target; no live money/refund/deployment or data resets.

## A1: original stable host ownership

Implemented post_preview_host.SandboxHostConfig/SandboxHostRuntime. Exact stable
storage_root/post-preview-sandbox/merchant/booth holds original drafts.sqlite3
and media; backend has an independent kernel LaunchLease in backend-owner.
Non-secret host-context binds mode/merchant/booth/order-version. Partial, duplicate,
wrong-type or foreign context fails closed without replacement. Config rejects
archive/linked/relative paths, invalid identity and untrusted Drive URL; repr
omits all credentials. Same existing factory assembles original checkout,
private readiness bridge, backend Drive observation, supported OS custody and
fixed Sandbox transport, without constructing a GUI, opening a listener or
performing provider/Drive/device I/O. No mock-only guard was removed.

Close returns False and retains ledger/lock if original financial worker cannot
stop; otherwise resources close idempotently. This is backend ownership only,
never proof that original native collector stopped or booth is FREE.

Test-first import ERROR before source existed. Eight host methods and related
original API/authority/readiness/CCP tests: **96 PASS /0 FAIL/ERROR/SKIP,28.508s**.
[Exact command/hash/limits](provider-bootstrap-2026-11-09/ownership-verification.json).
Windows host fixture uses original DPAPI; Linux factory control-flow fixture
patches key lookup explicitly. This does not replace prior actual Linux vault
integration or certify Ubuntu hardware. Registered the new host module in both
existing backend CI jobs; no tests removed or budget changed.

Reviewed AGENTS/current protocol, latest provider/Ubuntu continuation and
source-matched evidence; PP owner/security/CCP/ticket/payment/Drive/print/claim/
release contracts, latest bridge/host/vault reports, original ledger/photos/
checkout factory and LaunchLease. Prior a748db2 full/CI evidence remains at its
original source; do not rerun startup baseline solely to confirm it.

## A2: isolated child process and actual HTTP integration

Implemented post_preview_bootstrap.SandboxBackendProcess/run_child. Merchant and
Drive credentials travel only over a bounded anonymous private socket after
spawn, never argv/environment/stdout. Separate original readiness capability is
transferred by inherited POSIX descriptors or Windows shared socket handles.
Child mounts the original API/factory/ledger, binds only loopback on an OS chosen
port, and acknowledges exact startup nonce/PID/mode/version. Parent environment
is allowlisted; no GUI is imported in the child. Startup failures are redacted.

STOP/parent disconnect requests graceful shutdown. A bounded parent stop returns
False while any financial worker or HTTP thread remains; there is no force kill,
replacement host or premature original database/kernel-lock release. Uvicorn
must wait for original HTTP threadpool calls as well as the lifecycle worker.
Backend exit still does not prove native collector stop or booth FREE.

Actual subprocess/socket/HTTP tests cover typed client PENDING to original
settlement/one entitlement, lost create-response reconciliation after restart,
crash preserving the same lease/media, parent disconnect, secret redaction and
worker/foreground-call shutdown holds. Provider HTTP/Drive and Linux key lookup
are explicitly synthetic child-only fixtures; Windows uses actual DPAPI. No
production runtime test switch or mock-only guard removal was introduced.

**105 focused PASS, zero FAIL/ERROR/SKIP, 57.181s**, including 17 host/process
methods. An initial integration assertion expected fresh settlement immediately;
the fixture now respects the original one-second reconciliation pacing. A1
CI42575112638 passed Ubuntu/native but Windows failed two fixture cleanups
(WinError32: TemporaryDirectory removed before original lock cleanup). A2 fixes
cleanup ordering, retaining kernel-lock behavior; fresh Windows CI is pending.
[Exact source/log hashes and limits](provider-bootstrap-2026-11-09/process-verification.json).

## Next exact increment

Protected native provider facade/QR/ticket/delivery/claim/release, using original
backend settlement/protected proof authority and existing native UI. Do not put
a dummy provider in the GUI or remove mock-only admission guards. No native
merchant profile is mounted by A2 alone. Collector stop=False remains a separate
admission hold. Full final-source regression/current CI and actual Ubuntu device,
merchant/Drive/refund acceptance remain separate and unfinished.

Rollback scoped inverse source only; preserve original ledgers, contexts,
customer media, secrets/keyrings, paid rights and uncertain print/upload jobs.
