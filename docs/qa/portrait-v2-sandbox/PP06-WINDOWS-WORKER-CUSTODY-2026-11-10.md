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
