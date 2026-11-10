# Original worker capability custody — Windows-first L3-C

> **FINAL VERIFIED — source9de0dcd213f741b19cda493cc30d80e9b5c38598:** 948 local backend/100 actual-X11 native/34 offline Apps Script PASS. CI42812100193 ALL FOUR SUCCESS, all completed logs inspected. C1/C2a/C2b remain UNMOUNTED; C2c/C3 recovery incomplete; commercial NOT_READY, default health False. [Machine-readable evidence](evidence/pp06-windows-worker-custody-2026-11-10.json). Earlier pending/failure snapshots below are retained history.

10 November 2026. Base5f9e52e, runtime9054053, existing authorized post-preview
branch only. Pasted continuation fully read; latest remote reconciled, final
L3-A/B CI42801312247 completed logs inspected:917 backend on both platforms,
99 native, all four SUCCESS. Do not repeat that unchanged passing baseline.

## C1 bounded contract BEFORE source

Implement an UNMOUNTED original worker-key cryptographic envelope candidate,
reusing WorkerFenceKey and the exact existing Windows DPAPI/Linux Secret Service
protectors. No new cipher/provider, synthetic fallback, plaintext key sidecar,
key provisioning/unlock, GUI handle or backend mode toggle. Windows is the
priority; Linux fixture coverage preserves prior support, not Ubuntu packaging.

Bind original private root, merchant, booth, fixed Sandbox/order version,
worker epoch, original PID and declared process-birth identity to canonical
scope entropy. These fields are AUTHENTICATED METADATA ONLY: this crypto core
does NOT observe actual OS identity, prove process death/quiescence, own kernel
leases, release/ACK a booth, authorize payment or grant customer media.

Protect the original key_id and secret with distinct ORIGINAL_WORKER_KEY role,
version and same scope hash inside ciphertext. Outer non-secret header must
match the protected payload. Strict bounded typed scope/envelope/plaintext,
malformed/foreign-role/corrupt/unknown protector refusal and redacted repr/errors.
Only ciphertext/non-secret metadata can be serialized. Fail closed on missing/
locked/wrong OS custody, never replace the old key or reseal old customer data.

Test exact original HMAC capability after same-scope open and independent process
open, foreign root/account/booth/epoch/PID/birth, changed ciphertext/header/role,
missing custody, forged/synthetic protector and bounds. Parent/child test pipes
carry only protected envelope/scope and non-secret MAC evidence, never plaintext
key through argv/environment/files/stdout. Real Windows DPAPI in Windows CI;
Linux fixture explicitly patches original key lookup only, not OS acceptance.
No new production test switch. Reuse original bootstrap environment allowlist.

Keep C1 UNMOUNTED until its core is checked. Micro-commit/push/check remote after
focused verification. Next C2 immutable original pre-work escrow + verified OS/
kernel owner lifecycle; then C3 same original receipt verification/reconciliation
for supported pre-ACK/orphan recovery. Do not wire this primitive into old boot
or give native/HTTP callers an unseal/release shortcut.

## Required following boundaries

### C1 implementation and focused verification

Implemented `photobooth/post_preview_worker_custody.py`, still UNMOUNTED.
It serializes only protected original key ciphertext/non-secret metadata and
restores the original WorkerFenceKey using the exact existing OS adapters.
No launcher/backend/GUI/ACK route changed. No key is created by this module.
Both protectors reject non-exact adapter types, including synthetic/forged
adapters and subclasses. Errors are fixed/redacted and payloads are bounded.

Local Linux lookup fixture: 10 new tests PASS (0.353s), then 47 combined original
vault/worker-fence/new custody tests PASS (7.994s), zero failures/errors/skips.
Includes independent Python process restoration, changed six scope bindings
with forged public digest, malformed/noncanonical/duplicate/foreign-role inner
payloads, envelope corruption, unavailable/wrong custody, replacement prohibition
and redacted representations. Child pipes carry ciphertext and a test-vector
MAC only; no plaintext secret argv/env/file/stdout. Windows CI will exercise
actual DPAPI; that result is PENDING here. Linux fixtures do not prove OS vault
acceptance. Existing backend CI registry now includes the ten methods without
omitting the original 917. Full final regression/CI remains pending at this
micro-checkpoint. No commercial/recovery/OS process qualification inferred.

Next C2 first bounded seam: observe original process identity from actual OS
(Windows process creation FILETIME plus PID; Linux boot ID/start ticks for
existing support), require fail-closed read-only exit observation, no claimed
PID/birth accepted as a kernel/descendant-drain proof. Keep this separate from
custody and unmounted until tested. Then immutable pre-work escrow and original
kernel/collector/backend receipt reconciliation; unknown old roots stay held.

Persist original protected capability and immutable owner/epoch binding BEFORE
child/native work begins. Reuse original private bootstrap and exact worker
receipt/handoff authority. New or legacy-root eligibility must be independently
reviewed before first key creation; unknown/un-ACKed roots without original
escrow remain held. Never retroactively sign for a dead old worker using a new
capability. Already ACKed verified immutable receipts keep their original durable
verification path and do not require key replacement.

Actual global/native/backend kernel ownership, original OS process birth/exit,
collector/PhotoJobs/camera/file/HTTP/printer/upload drain and fresh original
financial state must be independently proved before any ACK/admission. Customer
images still require original proof and fresh legitimate PAID. A restored key
alone does NONE of this. Actual Windows reboot/device/DPAPI backup/restore and
account qualification remain separate; production/commercial NOT_READY.

Reviewed original credential_vault/Linux adapter, worker key/receipt/verifier,
protected custody/CCP contracts, host/fulfillment/private bootstrap, original
launch/visits/control and process fixtures; current owner/security/handoff/boot
contracts already read in this continuation. Rollback source only, retain every
original key/ciphertext/root/DB/WAL/SHM/media/PAID/OWED/receipt and uncertain job.

## C2a read-only process identity implementation

Implemented `photobooth/post_preview_process_identity.py`, also UNMOUNTED.
Windows uses one actual read/wait-only process handle to bind creation FILETIME
and wait status, closes its handle and never terminates a process. Missing valid
PID is distinct from access/query/wait failure; failures hold. Linux observes
numeric /proc stat start ticks plus kernel boot ID for existing support. PID
reuse/birth mismatch holds; live original processes never count as exited.
Neither this module nor an arbitrary identity is a worker/descendant drain,
kernel lease, financial release, authenticated escrow or admission proof.

Six new tests cover actual current process, actual independent child cooperative
exit, fresh read before exit, foreign birth/platform, invalid PID, denied OS
access/redaction and exited observations. Combined C1+C2a:16 PASS in0.325s,
zero failures/errors/skips on local Linux. Windows ctypes path and real DPAPI
are PENDING CI, not claimed from Linux. Existing core registry includes all16
new methods plus original917; native99 remain unchanged.

NEXT: C2b immutable pre-work escrow plus actual original global/native/backend
kernel owner lifecycle. Carefully review first-key eligibility BEFORE mounting:
existing unresolved roots without an original escrow must stay held. Then C3
same original backend receipt reconciliation before supported pre-ACK/orphan
recovery. Current boot behavior is unchanged; complete recovery NOT implemented.

## C2b bounded contract BEFORE source

Implement an UNMOUNTED, new-root-only immutable ciphertext file seam. Require
the exact original LaunchLease for that private root and actual current process
birth from C2a, then protect the caller's existing key with C1. No key minting,
new provider, history adoption, startup flag or GUI API. Allow only the original
lock's known data directory and this one epoch's escrow entry; any ledger,
WAL/SHM, media, prior epoch or foreign file holds before writes. Never descend
old or inventory customer files. Preserve partial/foreign files and fail closed.

Use exclusive creation, original checked_path, canonical bounded/duplicate-free
JSON, file fsync and original directory-sync helper. Same-scope/same-original-key
retry may validate/re-sync the same bytes; never overwrite or replace them.
Ciphertext record binds the full scope and original key ID. Reading returns
protected metadata only, under the exact original root lease; no unseal, worker
death, ACK, finance or media admission is implied. A restarted writer cannot
claim the old process birth, mint a replacement or overwrite an old epoch.

Tests must prove actual kernel contention, fresh-root write, immutable retry,
wrong original key/scope, foreign/partial history and file preservation,
failed OS custody before file creation, interrupted/failed sync preservation,
strict reads, same epoch/account/root binding and archive exclusion. Windows
directory fsync is NOT a physical power-loss guarantee. This narrow seam does
NOT support safe-history rotation yet, and is NOT mounted into the manager.
Next integration needs independent original-history eligibility and a durable
backend-child identity before any backend work; then actual global/native/
backend locks and worker/finance reconciliation. Unknown old roots stay held.

### C2b implemented new-root-only file seam

Implemented `photobooth/post_preview_worker_escrow.py`, UNMOUNTED, with11 new
methods. C1+C2a+C2b focused27 PASS in0.430s on Linux lookup fixtures, zero
failures/errors/skips. Actual original kernel contention, child process birth/
exit and ciphertext restoration are exercised; no worker kill or old-root reset.
Fault injection of file fsync failure holds the writer and retains the complete
original envelope. Same live writer/same original key retry re-syncs identical
bytes. Empty/truncated/foreign/oversized metadata remains held and unchanged.
Replacing a key with the same public key ID but a different secret also holds.
No production defect/recovery PASS is inferred from deliberate fault fixtures.

Storage uses exclusive create and actual file fsync; the retry opens the same
file read/write solely for Windows-compatible fsync and does not write bytes.
Directory sync reuses the existing helper; Windows returns unsupported/False,
so this is not power-loss qualification. `read_worker_escrow` returns structurally
checked ciphertext/non-secret metadata ONLY. Its public metadata is not an OS
authenticated identity observation; actual unseal and independent ownership
must still succeed before any future use. No key is minted or logged.

This candidate intentionally refuses all existing customer/history roots and
prior epochs. It does not support rotation, backend-child birth capture, manager
mounting, startup recovery, ACK or booth release yet. C2c must prove original
history eligibility, global/native/backend kernel ownership and durable child
identity BEFORE original backend work, using original manager/bootstrap.
Do not simply enable this writer in `_open`: that method currently mints a key
and starts a child before `_free_history`; unknown boot could be misbound.

### BUG-060 adversarial reproduction and correction

At d9876d8 one actual hard-link fixture was accepted by the new candidate's
metadata read. New test-first case FAIL0.012s (`WorkerEscrowHeld not raised`).
Corrected original candidate file reader/re-sync: bounded regular file, one
link, same path/descriptor device+inode, no-follow/nonblocking open when the OS
supports them. Actual Linux FIFO and Windows directory fixtures hold before
open; original and alias bytes are preserved. Still UNMOUNTED; no operational
customer/key/finance incident or worker-release bypass occurred.

Corrected66 combined original vault/worker-fence/C1/C2a/C2b methods PASS8.500s,
zero failures/errors/skips. New methods now29 (10 custody,6 process,13 escrow),
so final complete backend registry946. Final broad source-matched regression
and Windows actual DPAPI/process/escrow CI remain PENDING at this checkpoint.
Superseded micro-push CI runs must not be represented as final source results.

## CI-discovered original ticket timer investigation (before source correction)

Final-candidate be44bd5 CI42810724202 native job129811284579 completed99
tests with1 FAILURE281.942s: original protected widget's exact30-second timeout
left QR texture present while receipt HTTP was blocked (NEXT case passed).
Local99 PASS297.454s is retained and does not supersede the CI failure.
Investigate the original VisibleTicketWindow arithmetic with deterministic
clock values crossing a float exponent boundary. Reproduce before source fix;
if confirmed, compare the same absolute original start+30 deadline, never add
an epsilon, reduce genuine visibility, reset time or weaken widget assertions.
Preserve real visibility gating, NEXT and independent receipt worker semantics.

### BUG-061 confirmed and corrected

Deterministic unit test at be44bd5: start=math.nextafter(127,+infinity), exact
deadline=start+30. Elapsed subtraction rounded below30 and returned remaining1:
1 FAIL0.000s. Original timer now uses the same absolute start+30 deadline,
clamped before ceil, no epsilon or shorter visible window. Nonrepresentable
deadlines refuse start rather than instantly finishing. Genuine native rendering
and NEXT/receipt journal semantics are unchanged.

Corrected8 tests PASS11.363s (six original/new timer methods plus original
blocked-HTTP NEXT/timeout case and new deterministic actual-native boundary
case). New case verifies visible QR immediately before deadline, immediate
texture/code wipe exactly at deadline while worker remains busy, then original
once-only automatic output. Full final source now expects948 backend/100 native.

Pre-fix be44bd5 CI completed logs inspected: Windows core425 PASS377.136s,
all29 custody/process/escrow methods observed (actual DPAPI and Windows ctypes);
Ubuntu946 PASS471.621s. Native99 had1 FAILURE281.942s as above. Windows delivery
was still running at the fix checkpoint; this run is NOT ALL FOUR SUCCESS.
Keep this failed CI evidence and require new source-matched final verification.

## Exact next mounting boundary (C2c, NOT implemented)

Review the actual original `OriginalSandboxVisits._open` and `start` before
mounting. Current code creates a new WorkerFenceKey and starts its child BEFORE
`_free_history`. Do not insert the new-root writer there and call old boot safe.
First share the original history/financial/verified-receipt eligibility policy,
without creating replacement DBs or copying an independent finance engine.
Unresolved roots with no original escrow stay held. Preserve all prior epochs.
Later visitor rotations need a separately checked immutable epoch-to-original
draft/generation binding; the present new-root-only writer intentionally refuses
prior epochs/customer roots and cannot provide that policy by itself.

The original private bootstrap has a useful pre-work boundary: after actual
Popen, capture child creation identity and persist its original epoch binding
BEFORE `_send(parent, request, deadline)`. `run_child` waits for that original
START before constructing SandboxHostRuntime. No config/key is to move into
argv/env/files, no synthetic child/provider, and no START may bypass durable
original child identity. Partial bootstrap/custody must retain handles and hold;
never terminate/recreate a possibly live old worker merely to obtain a lock.

Global project LaunchLease, original private-root native lease and original
backend-owner lease are independent. A dead parent/key unseal proves none of
the others. Verify fresh actual OS identity/exit and actual original kernel
ownership, including live backend orphan, before metadata retirement. Prove
collector/PhotoJobs/camera/file/HTTP/printer/upload obligations independently.
Do not retroactively publish the old native's receipt or sign it with a new key.
Original already-published PREPARED receipts may only be verified with their
original capability under independently established ownership; no receipt/key/
epoch history may be fabricated. Durable ACKED verification remains unchanged.

Only after that C3 original receipt/finance/uncertainty reconciliation may admit
a new visitor. Old customer media still needs original role-correct proof and
fresh independently verified legitimate PAID. Source rollback never deletes
escrow, keys, ledger/WAL/SHM, media, receipts, OWED or uncertain jobs.

## Final source-matched verification

Runtime/source9de0dcd213f741b19cda493cc30d80e9b5c38598; following commits
are documentation/evidence only. All new source/tests and original workflow
hashes are retained in the linked JSON. No passing baseline was repeated for
onboarding; broad verification repeated only after actual functional increments
and the CI-discovered BUG-061 correction. Superseded/cancelled runs and both
first failures remain recorded, not relabelled PASS.

| Execution | Tests | Seconds | Result |
| --- | ---: | ---: | --- |
| Local complete backend | 948 | 439.734 | PASS |
| Local actual X11 native | 100 | 302.852 | PASS |
| Local Apps Script offline VM | 34 | — | PASS |
| CI Windows core129815889212 | 425 | 441.270 | SUCCESS |
| CI Windows delivery129815889586 | 523 | 506.117 | SUCCESS |
| CI Ubuntu129815889385 | 948 | 331.172 | SUCCESS |
| CI native129815889407 | 100 | 255.159 | SUCCESS |

[Final CI42812100193](https://github.com/pratikto/PhotoBooth/actions/runs/42812100193)
ALL FOUR SUCCESS at the exact source, all completed logs and step outcomes
inspected. Zero unit failures/errors/skips. Windows core ran all29 new custody/
process/escrow methods, Windows delivery ran both new timer methods. Native ran
the deterministic genuine-card/blocked-receipt boundary case. Actual Windows
PowerShell existing-entry setup, unconfigured protected-entry hold, explicit
new-booth local enrollment and subsequent check-only all succeeded using public
fixture settings without device/provider/Drive effects. CI native also completed
the original entry preflight and both original portrait screenshot renders.

These are software/test-runner results, not owner Windows account/DPAPI backup,
reboot/power-loss, real camera/POS80/paper, merchant Sandbox, phone/Drive, full
112/26 acceptance or commercial qualification. The eleven credited owner smoke
observations stay credited; do not demand repeat of unchanged checks. Owner
configurations are available; their values are not requested in chat.

No runtime/test WIP or active local app/backend/test remains. Private raw logs,
venv/cache and lab Xvfb are local only; obsolete privacy stash is superseded and
must not be applied. Source rollback only; retain all original data/custody.
FIRST next task is C2c above, then C3; never enable recovery from a restored key
or claimed process birth alone. Windows remains first; Ubuntu packaging deferred.
