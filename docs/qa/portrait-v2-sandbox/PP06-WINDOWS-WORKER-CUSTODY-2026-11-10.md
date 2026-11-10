# Original worker capability custody — Windows-first L3-C

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
