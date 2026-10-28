# AR-01 — immutable creation attempts and ambiguous-send durability

28 October 2026, Asia/Jakarta. FEAT-007/020/022; required existing branch
`feature/portrait-kiosk-v2-next`. Owner continuation authorizes staged source
implementation and incremental pushes. Base/rollback before AR-01:
`4261236694358c2f3cd2a475a4cd9cd82f436e00` (AR-00 remote verified).
[Source/field review](AUTONOMOUS-RECOVERY-BASELINE.md) ·
[Checkpoint](AUTONOMOUS-RECOVERY-CHECKPOINT.md) ·
[Provider contract/open gate](MIDTRANS-PROVIDER-CONTRACT.md).

## Scope and outcomes

The existing backend already avoided duplicate POST on checkout retry. This
increment makes the first request's immutable scope and uncertain send boundary
explicit and durable; it does not turn an uncertain creation into a safe resend.
Reuses CheckoutStore, CheckoutBackend and unchanged Sandbox transport/API/client.
No production, customer GUI resume, automatic camera/print/Drive or refund action.

1. New order and PREPARED attempt commit together before I/O. Fingerprint v1
   hashes canonical JSON containing provider mode, merchant, booth, checkout key,
   quantities, currency and the exact Legacy charge body (QRIS/order/amount).
   It is an internal digest, never sent as an invented provider header.
2. Only the original new-order request may CAS PREPARED → SENT. SENT is durable
   before invoking provider; it means the call **may** have happened. Abrupt exit
   there remains held. Restarts/retries use GET with the same order even if phase
   is PREPARED; this conservative policy does not infer delivery from local state.
3. Caught provider/validation failures change SENT → UNCERTAIN. Independently
   validated evidence sets VERIFIED in the same DB commit as the payment state.
   QR-display failure after evidence commit cannot regress VERIFIED.
4. Merchant/mode/fingerprint mismatch rejects before provider I/O. Cached claim,
   service, cancel, operator reconciliation and notification paths also check the
   saved context. Evidence cannot switch an attempt's bound merchant.
5. Missing/lagging/404 status preserves original order, amount/key/grant state
   and ambiguity. Existing persisted three-second status reservation bounds calls;
   AR-02 owns longer retry/backoff and fresh admission. No repeat POST is enabled.

## Additive schema and migration/rollback

New `checkout_create_attempts`: order_id primary key, version=1, merchant_id,
provider_mode, request_hash, phase, prepared_at, sent_at, verified_at, updated_at.
Phases PREPARED/SENT/UNCERTAIN/VERIFIED/LEGACY_UNCERTAIN are constrained in SQLite.
Existing checkout/events/recovery-action columns and journal/manifest formats
are unchanged. There is one logical create attempt per order, not a resend queue.

Opening an upgraded store transactionally inserts missing attempt rows as
LEGACY_UNCERTAIN, preserving all existing checkout/payment/service/grant/photo
identity fields. Known historical merchant is retained; unknown hash/mode stays
null rather than guessing what was sent. Missing attempts encountered after an
older writer inserts a row are also conservative; only validated status evidence
can establish provider state. Migration is repeatable and performs no provider I/O.
Prototype migration remains held as before. Full disk/write failures propagate;
no POST follows an unsuccessful local commit.

Rollback uses scoped inverse source commits after reviewing active work. Keep
this additive table, all financial/media journals and consumed rights; do not
down-migrate/drop/reset data. Old source can read its existing columns and write
new rows without knowing this table. On re-upgrade such rows are held. Historical
source lacks the new context protections, so use rollback only under controlled
operator hold, not to bypass them. No separate storage/capture migration here.

## Tests and exact scope of evidence

Before implementation eight new tests produced **2 FAIL / 6 ERROR** (missing
ledger/context validation). [Raw reproduction](ar01-before.txt). After source,
nine new attempt cases plus six AR-00 baseline and prior payment/API/operator
regression cases produce **132 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, Linux cloud,
Python 3.12.14. [Raw focused report](ar01-focused.txt).

```bash
.venv/bin/python tools/run_kiosk_unittests.py test_checkout_creation_attempts test_autonomous_recovery_baseline test_checkout_backend test_checkout_durability test_qris_session test_midtrans_sandbox test_midtrans_verify test_qris_kiosk_client test_payment_quote test_qris_api test_qris_http_v2 test_qris_recovery
```

PAY-01: abrupt process exit with PREPARED and SENT, real WAL reopen, no resend.
PAY-02: synthetic provider acceptance committed before child exits, original order
status recovery. PAY-03/04: never-received and lagging 404 stay held, no new key
or grant. PAY-05: two backend connections competing while POST is blocked send
once. PAY-14 baseline: optional fraud field versus explicit invalid values.
Existing transport tests retain fixed Sandbox host, unchanged charge body and
no redirect/credential forwarding. These do not certify provider API behavior.

Migration fixture uses pinned pre-AR checkout DDL; it needs no git history in
shallow CI and executes no historical code. SQLite handles close explicitly for
Windows. Existing Linux Sandbox and new Windows fixture CI steps include these
modules. Initial/focused source file hashes are recorded in
[ar01-source.json](ar01-source.json); companion checkpoint pins exact commit.

Full regression and CI are pending at this micro-checkpoint, to be recorded with
actual results at the final functional SHA. Windows hardware, Ubuntu mini PC,
merchant simulator/Legacy idempotency contract, paper/Drive and cloud retention
remain NOT_RUN. Abrupt software exit is not power-loss filesystem certification.
No screenshots required for this backend-only change; native UI regression is
part of final applicable checks, not evidence of new recovery GUI.

## Remaining dependency

PAY-22 / same-order charge resubmission is BLOCKED on exact official Legacy
contract plus controlled merchant evidence. Invoice five-minute idempotency is
insufficient. Safe subsequent AR-02 reconciliation can proceed independently
without enabling POST retry. Photo reconstruction/private claim/GUI/operational
release still require AR-03 onward and separate physical/provider acceptance.

## Final source validation and publication

Code `017b417d02d63a79b1c5b21c4f0613b7d15186fc` pushed and remote HEAD independently verified.
Final local complete regression: **968 run / 965 PASS / 3 SKIP / zero failures/errors**. Three optional palm
model-assets cases skipped; no hardware/provider acceptance inferred.
[Full raw output](ar01-full-tests.txt), [exact command/source hashes](ar01-source.json),
[CI job/step evidence](ar01-ci.json). Matching
[40688374416](https://github.com/pratikto/PhotoBooth/actions/runs/40688374416)
completed all three jobs SUCCESS. New Windows fixture step passes. Earlier
"pending" language above records the initial micro-checkpoint; this section
supersedes that validation status without changing runtime. Next: AR-02.a,
while provider repeat-charge activation and unattended release stay blocked.
