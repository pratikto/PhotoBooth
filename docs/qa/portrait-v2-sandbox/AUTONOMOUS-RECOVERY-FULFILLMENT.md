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

## AR-03.b unique allocation and native handoff

Authenticated `/allocate` freezes a single operation ID and transaction before
local filesystem I/O. Per-booth additive allocation counter uses the isolated
`PB001V2AR_00000001` namespace, compatible with existing retention IDs; ordinary
PB001V2/PB001V2S2 counters/Drive slots remain unchanged. Fulfillment/order/grant/
transaction/action uniqueness survives replay and restart. Legacy missing
contract or pre-existing ambiguous capture cannot allocate a replacement.

Kiosk journal saves allocation action before API, retains returned identity,
and requires a separate local-ready ACK before STARTED. The original PhotoTest
creates only that exact folder using the existing TransactionStore; binding and
frozen contract are in its very first manifest. No counter reset/reserve replay.
Current template-byte/geometry hash must match; mismatched art remains held.
Duplicate calls return the current same run, and an existing folder after restart
is held unchanged until AR-05 reconstruction. Sandbox printer/Drive stay off.

Initial allocation tests: two ERROR before implementation. Native focused checks
caught the first proposed namespace's incompatibility with strict retention IDs;
corrected source uses the existing eight-digit format, without weakening retention.
Final group **204 PASS / zero FAIL/ERROR/SKIP** including three exact-binding
fixtures, native handoff/ACK loss, workflow/copy/retake and retention regression.
Command extends AR-03.a with test_photo_allocation, test_qris_reconciliation_session,
test_kiosk_v2_sandbox, test_kiosk_v2_sandbox_widgets, test_kiosk_v2_photos,
test_retention and test_workflow in SDL offscreen/dummy audio. Full regression
follows final functional change; device/provider checks remain NOT_RUN.

## AR-03.c — exact allocation/STARTED crash evidence, 29 October

Existing runtime passes CAP-01–05 actual child exits, including lost allocation/
STARTED replies, empty-folder initialization, existing manifest preservation and
orphan hold without recency scanning. **66 focused PASS**, no runtime defect or
schema/UI change. [Source/command/limits](CAP01-05-ALLOCATION-CRASHES.md).
Full combined PAY-18 completion-reply and physical power-loss gates stay open.

Final AR-03.c evidence at e72e28b: **66 focused PASS**, matching CI 40815197373
three jobs SUCCESS (Windows payment/allocation group 55 PASS/zero skip).
Tests-only, application unchanged; full/native baseline not rerun.
[Exact source/limits](evidence/cap01-05-final-verification.json).

## 29 October — AR-03.d1 PAY-18 combined lost replies

Base/remote verified `03189012b5f4c6204ef4f8718bb218a1baac32d5`.
**85 focused PASS / zero failure/error/skip**, 12.257s. Two new methods run
**eight actual child exits at four boundaries**: original booth claim, customer
claim, STARTED and COMPLETED committed before local acknowledgment. Same
order/grant/claim operation/allocation/transaction/result; one provider charge,
three synthetic JPEGs/one composition, original OWED and private proof preserved.
Outage HTTP 503/refund HTTP 409 deny cached-PAID recovery; existing bytes remain.
[Contract/commands/provenance](PAY18-SERVICE-REPLIES.md).

Tests/CI/docs only; no runtime defect or application/schema/UI change. Current
CI pending at this containing test commit. Prior full e0dc594 (1117/1114/3) and
native c94696d (28 PNG/four QR) retain original source; no new full/native result.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**; PAY-18 synthetic PASS,
BUG-023 OPEN, overall audit IN_PROGRESS. Next AR-03.d2 completion/archive exits,
then CAP-11–13, CAP-16 pre-request boundary, CAP-20 and AR-09 denial audit.
External/OPS/production gates unchanged; only disposable work/ local, no
unpublished runtime patch. This containing commit is the next micro-push;
resolve its SHA from Git, push and verify remote before continuing.

## 29 October — AR-03.d2 completion/archive process exits

Previous micro-push `3ad80da74da2a0fc3c9d5e3dbe3d84f91a483f4a` remote verified.
**86 focused PASS / zero failure/error/skip**, 22.532s; three PAY-18 methods,
23 real child exits at seven distinct boundaries. New archive exits hold local
COMPLETING after accepted ACK, operation history and lookup index; no new visit
or archive bypass before original proof and durable final journal. Original
three JPEGs/one PNG/manifest/copies/OWED remain unchanged, no repeated effects.
[Command/source/limits](PAY18-SERVICE-REPLIES.md).

Tests only; no runtime defect/application/schema/UI change. Matching CI pending
at this containing commit; first run 40818395624 still running at publication.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**, BUG-023 OPEN/audit IN_PROGRESS.
Next: matching CI/final checkpoint, then **CAP-11–13 retake child exits**;
CAP-16 pre-request, CAP-20 and AR-09 denial audit follow. Prior full/native stay
at e0dc594/c94696d; no new full/native/device/provider/production/OPS acceptance.
Only disposable work/ local, no unpublished runtime patch. Scoped inverse of
new tests/docs retains every customer record; containing SHA resolved after push.
