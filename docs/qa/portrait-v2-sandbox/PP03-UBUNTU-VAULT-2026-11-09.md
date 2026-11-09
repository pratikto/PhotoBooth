# Ubuntu mini-PC protected credential vault

9 November 2026 · owner explicitly confirms Ubuntu mini PC as commercial target.
Windows development/support stays intact. This supersedes any generic Windows
booth assumption in the dated consolidated ledger, not prior Windows evidence.

## Bounded adapter contract before code

Implement an isolated Ubuntu Secret Service AES-GCM protector candidate. Master
key lives only in the existing unlocked OS keyring, accessed over an encrypted
local Secret Service session. Every operation rechecks custody; no plaintext key
file, synthetic fallback, automatic unlock or customer prompt. Missing key,
locked/missing collection, unencrypted session, duplicate/wrong key or changed
ciphertext/scope must fail closed. Store only ciphertext and non-secret key ID in
the ordinary ledger. Never automatically replace a lost original key.

Provisioning is explicit operator setup, separate from routine construction.
Serialize first-key provisioning with a protected per-user runtime kernel lock;
reuse the existing exact key, never overwrite or delete it. Session-bus calls
have a bounded total deadline. Use SecretStorage 3.5.0's existing encrypted-session
implementation, rejecting its plaintext fallback before any secret is accessed.
No other keyring item is searched or read. No real keyring provisioning here.

Keep this first adapter unmounted while its code/tests are qualified. The
platform selector, merchant host and native/restore guards require a subsequent
reviewed integration; do not infer Ubuntu product acceptance from mock keyring
fixtures. Actual mini-PC keyring login/autostart/reboot/backup acceptance remains
separate from software tests.

Reviewed: owner Ubuntu answer; AGENTS platform rule; PP credential/security and
original-proof/OWED contract; credential_vault, process fixtures, Windows DPAPI
and current Sandbox host; SecretStorage/Jeepney source for session encryption,
locked collections, bounded calls and noninteractive item creation.

## Executed candidate evidence

Implemented the isolated LinuxSecretServiceProtector candidate with per-operation
keyring checks, key-ID/scope-authenticated AES-GCM envelopes, explicit one-time
provisioning, duplicate/locked-key rejection and no prompt execution. First-key
creation additionally requires the exact original private ledger to contain no
CCP or Recovery Ticket credentials; missing custody with old proofs cannot be
replaced by a new key. Provisioning never overwrites or deletes keyring items.

Initial import probe ERRORed because the adapter did not exist. Fourteen new
Linux vault fixture methods plus nine existing protection methods: **23 PASS in
0.408s**, zero failures/errors/skips. Windows fixture branches explicitly reject
unsupported Linux runtime operations; they do not certify Ubuntu integration.

An actual isolated Secret Service exercise then passed seven expected outcomes:
initial key provision, seal, two independent Python-process restores, wrong-scope
refusal, keyring lock, and locked-key refusal. No existing user bus/keyring was
used. Debian 13, GNOME Keyring 48.0-1 and official Debian libgck/libgcr packages
were extracted under ignored workspace work/, without system package changes.
SecretStorage 3.5.0 / Jeepney 0.9.0 used the encrypted Secret Service session.
The test's own runtime/data/config and encrypted keyring were isolated; daemon
PIDs were stopped at completion. Only sanitized states/package hashes/driver
are published, never master keys, ciphertext fixtures or private proofs.

This is actual Secret Service integration on a Linux lab, **not** target mini-PC
Ubuntu login/reboot/autostart/backup or production acceptance. The selector and
merchant host still require the next reviewed integration; native payment, claim
and worker restart remain separately guarded. No real merchant, cloud, paper or
refund operation occurred. Roll back only this candidate/dependency/tests, never
original protected credentials, paid rights or keyring records.

## Platform selector and backend integration

After the real isolated-service exercise, platform_protector now selects the
Linux Secret Service adapter on Linux and preserves Windows DPAPI on Windows.
It performs lookup only; missing keyring/key never provisions or unlocks during
runtime. protection_status identifies the implemented provider but explicitly
returns readiness NOT_CHECKED and device_acceptance NOT_VERIFIED. The guarded
Sandbox backend accepts only exact implemented Windows/Linux protector types.
Existing synthetic/Windows-mock admission and restore opt-ins stay unchanged.

Focused credential/API/CCP/ticket/protected-restore scope: **87 PASS in 22.344s**,
zero failures/errors/skips, exit 0. Independent ordinary OS fixtures use their
own QA key identity on Linux; they never read the commercial app master key.

A fresh isolated GNOME Keyring/D-Bus lab then passed eight expected outcomes,
including the actual platform selector and Sandbox backend with an original CCP
protected by the real Linux keyring. Its authenticated original API moved from
PENDING to independently verified PAID/OWED through the real fixed Sandbox
transport with fake HTTP only; one synthetic charge. No fake Windows protector
was used for this Linux backend exercise. Both test daemons stopped cleanly.
Source-matched full regression/Windows CI follows separately.

Deployment boundary: an encrypted login keyring needs a valid OS unlock path.
Desktop auto-login alone does not establish unlocked custody. Verify mini-PC
login/PAM or an approved hardware-protected unlock, encrypted keyring backup,
reboot and service environment before unattended commercial operation. Do not
store an unlock passphrase in app files or disable keyring encryption to pass
startup. These device/OS acceptance facts remain NOT_RUN here. Child backend
bootstrap and protected native payment/ticket/delivery/claim/release integration
are still unfinished source work.
