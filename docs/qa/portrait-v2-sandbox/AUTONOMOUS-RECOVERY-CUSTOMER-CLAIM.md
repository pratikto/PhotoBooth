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
