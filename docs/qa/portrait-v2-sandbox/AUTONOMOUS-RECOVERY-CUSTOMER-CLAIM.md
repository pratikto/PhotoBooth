# AR-06 — private customer recovery capability

29 October 2026 (Asia/Jakarta). Owner repeatedly requests all AR stages, dependency
order, no new branch/master/production. Review the full master/provider/privacy/
operations/matrix contracts and AR-00–05 source/evidence before this stage.

## Contract recorded before implementation

Customer capability is independent of merchant credentials, booth bearer and
operator PIN. Mint 256 random bits locally for the original live checkout;
persist/send only its SHA-256, bound atomically to immutable order/checkout key/
merchant/booth. Raw ticket remains only in original process memory and the
customer's saved QR; never in journals, URLs, logs or reports. No secret reissue
on restart. Legacy sessions without a capability stay operator-held.

AR-06.a: additive hashed-capability table and strict authenticated redeem API,
constant-time verification, expiry, durable rate limit and one-use action CAS.
Bad/expired/wrong-booth proof reveals no private data or provider details. Verify
current settlement before any resume permission; same original action may replay
a lost ACK, never create a new grant/transaction. Preserve paid entitlement even
when a credential expires or the device fails.

AR-06.b: original-process ticket issuance and customer-proof controller seam;
redemption creates only a short-lived bound in-memory ResumePermit. It cannot be
restored from GUI PAID text or old journal. Reset proof at process restart;
actual private restore is mounted only in AR-07 after validation.

Sandbox policy: credential expires 24 hours after order creation. This is a
bounded trial default, not commercial terms; production ticket lifetime/support
and refund policy still require acceptance at AR-13. Numeric reference alone
never authorizes media. Repeat redemption uses the exact persisted action ID
and original capability; new actions with a consumed ticket are rejected.

Tests first: migration, absent/guessed/replayed/expired/misbound tokens, fresh
provider outage/refund, action/body mismatch, one-use CAS and no raw secret in
persisted metadata. Full regression after final functional roadmap work. Real
merchant and Windows/Ubuntu/device acceptance remain NOT_RUN. Rollback preserves
hashed claims/obligations and disables disclosure; never reset customer state.

## AR-06.a backend delivery and evidence

Additive checkout_customer_capabilities binds unique order/hash, booth, original
24-hour expiry, claimed action/time, attempt window/count and revocation flag.
New-order hash is committed before provider I/O and cannot be replaced on retry;
legacy rows receive no guessed credentials. Invalid/expired/wrong-booth proof
cannot invoke provider or grant service. Eight failed attempts per persisted
60-second window survive restart; clock rollback fails closed. Raw tokens never
enter backend order views or persisted records. Existing financial fields stay
intact; token expiry/revocation does not erase OWED fulfillment.

Authenticated customer-claim API validates strict body and current provider
settlement, then atomically redeems exact action and original grant. Lost ACK
replays only the same capability/action; another action is denied. No PIN/public
reset/operator mutation is supplied. The capability remains separate from booth
auth and does not expose old photo bytes itself. Client ticket/UI integration
follows; this increment does not yet issue a ResumePermit in the GUI.

Initial six new tests ERROR before source. Final **137 focused PASS / zero
FAIL/ERROR/SKIP**, including eight claim cases. Command:
`.venv/bin/python tools/run_kiosk_unittests.py test_customer_capability test_checkout_fulfillment test_checkout_reconciliation test_checkout_creation_attempts test_checkout_backend test_checkout_durability test_qris_session test_qris_http_v2 test_qris_api test_qris_recovery test_qris_kiosk_client`.
HTTP fixtures use explicit command network permission; an earlier restricted
HTTP fixture attempt was terminated and the permitted run passed. No provider
network, customer data or actual hardware was used. Full regression remains
reserved for the last functional roadmap source; commercial token/support
policy and device/merchant acceptance stay separate.

## AR-06.b original-process ticket and claim controller

QrisKioskClient advertises capability support. KioskCheckout mints 256-bit raw
secret in original-process memory and persists only SHA-256 before first I/O;
API atomically binds hash with order. Restart cannot redisplay/reissue the raw
ticket and cannot admit a saved RESERVED grant without original proof. Old
clients/journals without this feature remain conservative; no guessed migration.

Original ticket format binds version/booth/checkout key/secret. Authenticated
claim validates exact original context and saves only claim action ID. Pending
ownership may reopen the payment path but cannot grant media; settled ownership
can reuse exact allocation. In-memory proof expires for resume issuance after
60 seconds, and the deliberate resume action rechecks the original secret/action
and current settlement before issuing one bound ResumePermit. Close/privacy lock
clears memory credentials; a generation check fences late claim replies.

Initial four fixtures: one FAIL/three ERROR; pending-ownership test initially
ERROR before its safe observation-only path. Final **92 focused PASS / zero
FAIL/ERROR/SKIP**, including six new session cases and native Sandbox compatibility.
Command extends the earlier AR-06.a groups with test_customer_claim_session,
test_kiosk_v2_sandbox and test_kiosk_v2_sandbox_widgets (SDL offscreen/dummy audio).
Late callbacks after privacy lock, raw-secret absence from journal, rebooted
RESERVED denial, wrong-booth ticket and one-use restore permission are covered.
Ticket display/claim/restore UI remains the next AR-07 increment; no photo resume
is mounted by this source alone. Device/merchant/production gates remain separate.
