# AR-03 — frozen orders and durable fulfillment identity

28 October 2026 (Asia/Jakarta). Owner requests all AR stages in order, safe
incremental pushes, no new branch/master/production. AR-02 source follows AR-01;
refresh exact remote before editing. Reviewed the full recovery specification,
field baseline, provider/reconciliation contracts, checkout store/backend/API/
client/session, native Sandbox handoff, PhotoTest/TransactionStore/workflow/catalog
and original HTTP/native fixtures. This contract is recorded before source work.

## Small increments and acceptance

AR-03.a freezes server quote, template asset/geometry hashes and copy counts
atomically with new order creation; introduces additive fulfillment ledger and
conservative legacy migration. Tests first: byte-preserving upgrade, independent
connections, one order/grant/fulfillment, no false completion on closure, immutable
quote/template hash, data conflict quarantine. Legacy missing frozen evidence is
held rather than using today's templates to invent historical proof.

AR-03.b persists one allocation operation and one server-chosen local transaction
ID before local folder creation; unique both directions. Native adapter passes
that exact binding into the existing PhotoTest/store. Duplicate/lost ACK replays
same identity; old missing allocation stays held. Sandbox uses an explicitly
separate ID namespace, leaving ordinary/v1 counters and Drive mapping unchanged.

No destructive migration or implicit legacy photo adoption. Rollback retains all
additive tables/fields, media and rights. Existing service COMPLETED can describe
composition, never alone a settled financial/service obligation. Abandon/closed
never erases an owed service. Current fulfillment fields remain authoritative
separately from old service/GUI state. No printer/Drive activation in Sandbox.

Focused checks each increment; final full regression after final functional work.
Actual merchant/device/Windows/Ubuntu/paper/cloud acceptance NOT_RUN.

## AR-03.a schema and evidence

`checkout_frozen_orders` stores canonical JSON/hash/created_at keyed by order;
server tariff, amount/quantities, template identity/artwork/mask hashes and
geometry are frozen atomically with new payment. No customer pictures or paths
enter the snapshot. Historical orders get no invented current-art snapshot.
`checkout_fulfillments` binds unique fulfillment/order/grant/transaction/action
IDs, merchant/booth, contract hash, state and independent obligation_state.
Paid evidence creates OWED even before client claim; abandon suspends but never
refunds/delivers. Old COMPLETED ack records COMPOSED, still OWED pending actual
service/delivery acknowledgement. Operator action audit remains unchanged.

Migration preserves original financial rows/grants/transactions. Missing evidence
is LEGACY_REVIEW; duplicate historic local bindings hold both fulfillment mappings
without choosing the first row and without deleting either original binding.
Tables are additive and retained on rollback. Current source can read/write old
rows; allocations of held legacy entries will be refused in AR-03.b.

Six new fixtures, initial five ERROR and duplicate-migration FAIL before fixes;
final focused **133 PASS / zero FAIL/ERROR/SKIP**. Command:
`.venv/bin/python tools/run_kiosk_unittests.py test_checkout_fulfillment test_checkout_reconciliation test_checkout_creation_attempts test_autonomous_recovery_baseline test_checkout_backend test_checkout_durability test_qris_session test_qris_http_v2 test_qris_api test_qris_recovery test_qris_kiosk_client`.
Full/device/provider acceptance remains separate; next increment binds allocation.
