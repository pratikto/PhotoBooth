# Isolated post-preview Sandbox backend assembly

9 November 2026 · existing authorized branch · base ad2f477.

## Bounded implementation contract before source changes

Assemble the existing post-preview API/payment coordinator and fixed Midtrans
Sandbox transport over the private readiness bridge, original private checkout
and backend-owned read-only Drive probe. The trusted backend host receives
merchant credentials; no GUI readiness booleans, mock PAID callbacks or legacy
paid-first API routes are mounted. Only the original merchant/booth/Sandbox
ledger context may be served. No public listener or native profile is enabled
by constructing the factory.

Before a new charge, independently validate that the original offered CCP's
protected escrow can still be decrypted and matches its existing verifier,
without returning a secret, minting a ticket or recording a new screen offer.
Reuse the original CCP implementation for that check. The host uses the exact
supported Windows current-user DPAPI protector; unsupported Ubuntu protection
fails closed. Missing OS/account/key support is not replaced with a synthetic
protector. Reconciliation of original already-SENT/UNKNOWN attempts remains
possible without new-charge readiness, preserving original identity and OWED.

Test authenticated original checkout via the real API/coordinator/transport
with fake HTTP; independent GET settlement, uncertainty, expired renewal,
late/duplicate settlement and foreign ledger/escrow failure must retain their
existing guards. Windows OS protection is separate from Linux fixture plumbing.
Keep this assembly unmounted until native protected ticket/delivery/claim and
release are integrated. Do not merely remove the mock-only guards.

Reviewed: prior PP security/owner/provider/vault/saved-settings contracts,
current bridge source/results, original API/payment/CCP/readiness/authority,
private-store/checkout/photo and fixed Sandbox server/transport implementations.

## Execution

Implemented `photobooth/post_preview_server.py::build_sandbox_app` over the
existing PP API, coordinator, fixed Sandbox HTTP transport, original checkout,
private worker readiness and independently observed Drive readiness. It checks
original merchant/booth/provider/protector ledger context and rejects mixed
synthetic/foreign history. It constructs no listener and performs no I/O until
an authenticated original API action. No simulated-PAID or legacy route exists.

The exact platform protector must be WindowsDPAPIProtector from the existing
platform_protector factory. Linux unsupported OS custody fails closed in real
use. Positive Linux assembly tests explicitly replace that OS adapter in test
code with in-memory fixture encryption; they prove control flow, not Linux OS
protection. On Windows, the same test setup uses actual current-user DPAPI.
The production factory exposes no synthetic-protector flag or parameter.

OriginalCCPService now shares its original verifier/decryption path between
private_offer and validate_escrow. The latter returns no secret, creates no
render permit/credential/event and cannot claim proof was genuinely offered.
Corrupt/missing/wrong-key custody stops a new charge. Already-SENT/UNKNOWN
transactions keep same-order reconciliation even if escrow later fails, retaining
PAID/OWED rather than minting a replacement payment or discarding money rights.

Actual tests: CCP scope 17 PASS in 3.778s. Initial host scope ran 8 methods with
two subtest ERRORs in the foreign-ledger test because its outer SQL transaction
nested the factory's own transaction. Removed the test's outer transaction;
no production guard changed. Final related API/CCP/ticket/checkout-ticket/
authority/readiness/payment scope **145 PASS in 39.909s**, zero failures/errors/
skips, exit 0. Ten host cases exercise independent GET, original UNKNOWN/404,
cancel/late PAID, expiry followed by duplicate settlements, bad escrow/foreign
ledger, dead bridge, Drive failure and forged readiness fields.

No real merchant request, actual camera/paper/Drive, refund or production action
was performed. Full new-source regression and matching Windows/native CI remain
separate until recorded. The factory is **not a fully mounted native provider
profile**. Existing owner launcher/service/claim/isolation stay mock-only.

Next exact source work: a credential-isolated child-process host/bootstrap over
this assembly, then protected native client/ticket/delivery/claim/release wiring.
Do not use this factory or the old paid-first launcher as proof of a complete
post-preview commercial journey. Ubuntu protected-vault support, actual merchant
credentials/acceptance, real paper/cloud/refund, timed qualification and operating
package remain open. Rollback only this factory, shared CCP extraction and tests;
never alter original paid, credential, provider, print or media journals.
