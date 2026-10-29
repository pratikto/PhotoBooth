# UX-07.h — purchased-print integration contract and source audit

30 October 2026 (Asia/Jakarta). Status: CONTRACT/AUDIT COMPLETE; implementation
below is PLANNED, not mounted or certified. Branch/remote base:
`613243ab956001b24cde8f7a76bf1b3673a63d2a`. Last functional evidence remains
e7e09fe: 1188 run / 1184 PASS / 4 optional SKIP, CI 40959449442 SUCCESS.

Reviewed AGENTS/protocol/prompt, checkpoint/handover, AR roadmap/master,
readiness/fulfillment/operations, print/Drive contract, current device evidence
and preservation records. Audited the source seams below; no archive access.

## Existing behavior and precise missing integration

| Source seam | Existing behavior | Purchased-print requirement |
| --- | --- | --- |
| `fulfillment_contract.frozen_contract` | Version 1 freezes tariff, quantities, per-design copies, assets and geometry | Copies do not identify a physical delivery policy; preserve existing JSON/hash |
| `SandboxCheckout.begin_ready` / `prepayment_readiness` | Camera/storage/templates checked before a new order; delivery opt-in rejects | Keep this dedicated trial unchanged; add a distinct future host rather than weakening isolation |
| `PhotoTest.start_bound` / `restore` | Paid allocation/resume rejects printer, Drive and ordinary workspace | Preserve these methods; future purchased host needs an explicit binding adapter and its own acceptance |
| `CheckoutStore.service_transition` | COMPLETED maps to COMPOSED; obligation remains OWED | Composition or a spool response must not satisfy a paid print obligation |
| `PhotoTest.print_result` | Durable SENDING intent precedes original transport; success is SUBMITTED, uncertainty is held | Reuse transport/no-replay choreography, bind a purchased job to the original paid order and exact output |
| `PhotoTest.acknowledge_print` | Records operator_checked on a local test job | This boolean alone is not an authenticated paid delivery receipt/refund |
| `PhotoTest.isolate` | SENDING/UNCERTAIN blocks safe release | Keep that hold; release requires original financial/privacy/fence isolation |
| `PhotoViews` composition callback | May auto-print once after approval in ordinary opt-in mode | No print while restoring/reconciling or before original customer consent |

The missing connection is not another printer driver or a missing PRINT flag.
The ordinary printer is working source reused by local tests; the paid binding
deliberately excludes delivery. Route observations and MOCK orders cannot close
this gap. No defect or lost payment is inferred from that intentional boundary.

## Target contract for the next isolated source increments

The first integration host is an **offline test fixture**, reusing the original
checkout backend/client/store with a fake provider and fake printer. No new
launcher, payment endpoint, merchant trial opt-in or production profile is
created by this document. A customer-facing host remains unmounted pending its
explicit operating contract and controlled acceptance.

Keep frozen-order version 1 byte-for-byte compatible. Prepare a separately
versioned, additive delivery requirement record linked to the immutable order,
booth, merchant, original contract hash and later fulfillment/transaction.
Its policy and per-design required copies come from backend configuration and
the frozen quote, never from a client ready flag or current cart. Proposed
table/API names are implementation choices to resolve in the migration increment.
An absent record means legacy/unspecified delivery, not proof that printing was
bought, unnecessary or fulfilled. Do not backfill an obligation from today's
settings or rewrite historical hashes. Rollback retains additive records.

For a new fixture purchase requiring print, original camera/storage/template
checks and a fresh original printer-route observation must precede create/order
I/O. Unknown/warning/exception/stale observations deny creation with fixed text.
An active order always recovers the original identity without a new charge.
The device observation is point-in-time only; paper readiness is separately
unverified. Windows spooler API latency remains unbounded; use the existing
single-flight worker, not UI-thread I/O or a competing print transport.

After verified payment and original customer proof, bind one print intent per
original design/output and frozen copy quantity. Persist before send. Recovery
of SENDING/UNCERTAIN must hold without resending; SUBMITTED is evidence of
submission only. Preserve the PAID/OWED obligation through printer failure,
lost acknowledgement and booth suspension. Do not allocate a new visit, reset
quota, regenerate a composed strip, fabricate a refund or extend retention.

Physical delivery acceptance/principal/evidence, compensation and support policy
remain operating decisions. No endpoint to mark a paid print delivered and no
automatic OWED-to-satisfied transition is authorized or implemented here.
Drive stays independent: preserve its existing offline/deferred-binding and
retention rules; do not add an always-online prerequisite for printing.

## Dependency-ordered micro-increments

| Increment | Concrete deliverable | Exit evidence |
| --- | --- | --- |
| UX-07.i | Offline delivery-requirement migration/compatibility fixtures, then additive storage only | Existing financial/frozen JSON/hash unchanged; absent/legacy/conflicting/wrong-tenant records held; exact replay stable |
| UX-07.j | Offline fake-provider/fake-printer purchase adapter on original workers | Every failed readiness vector causes zero new order/POST; healthy deliberate retry creates one original order; recovery ignores new readiness without changing identity |
| UX-07.k | Original paid binding to durable print job in fixture only | Before-send/after-send/lost-ACK/restart faults preserve output/copies/OWED and never resend uncertain work |
| UX-07.l | Native fixture host, privacy/fencing and truthful submission UI | Both portrait sizes, worker stalls, stale callbacks, original ticket proof, safe release and no unearned completion |
| External gate | Explicit customer-facing host/merchant and physical acceptance | Real Windows/Ubuntu observations, controlled provider result, paper/phone/privacy/support evidence and separate release approval |

Each source increment needs focused tests, documentation, commit/immediate push
and remote verification. One final applicable full regression follows its final
functional change; current Windows/Linux receipts must identify actual methods.
Do not rerun the verified MOCK/collector/preservation work to inflate evidence.

## Current acceptance and next exact step

UX-07 whole gate stays NOT_RUN, matrix 59 PASS / 0 FAIL / 9 BLOCKED / 1 NOT_RUN;
AR-13 conditional. PAY-22 official Legacy contract and WEB-01..08 public
infrastructure/operations remain BLOCKED. This audit supplies no new automated,
merchant, physical-paper or provider PASS. No runtime/schema/GUI changes.

Next implement UX-07.i migration fixtures against disposable SQLite using the
original frozen-order/fulfillment APIs, before adding a delivery-requirement
storage seam. Review this contract plus existing fulfillment/allocation and
schema tests before code. Do not mount the new policy in the dedicated Sandbox.
In parallel, collect actual reports using the existing
[read-only commands](UX07-PRINTER-DEVICE-EVIDENCE.md); preserve each report with
a fresh filename. Local cloud fixtures cannot supply those physical observations.

No production payments, physical print/Drive action, live provider call, OPS,
public ingress, branch/master/default change, deployment or data deletion.

## 30 October — UX-07.i1 implementation boundary before code

Begin with an explicitly initialized additive table and validated read-only
adapter on the existing CheckoutStore connection. No default store/HTTP/backend/
launcher calls it. Missing records return unspecified (None), never print-free
or fulfilled. Fixture-only SQL seeds candidate records for validation. Validate
order/booth/merchant, original frozen hash, version/policy and exact frozen copies;
reject corruption/foreign identity. Creating the table must leave every existing
financial/frozen/fulfillment row unchanged and survive reopen/rollback compatibility.
No public issuer is added: atomically freezing a requirement during original new-
order creation is UX-07.i2, before any provider POST. Do not provide an attachment
API that could retrofit an old PREPARED/paid order from today's settings.

## 30 October — UX-07.i1 additive requirement schema/read fixtures

Base/remote d4580122cc34375d1ac44d6ce5663ee503a5950a. Explicitly initialized
DeliveryRequirements adds only a separate table on the existing store connection;
default CheckoutStore/backend/HTTP/GUI never calls it. Validated reads bind original
order/booth/merchant/frozen hash/copies; absent record is unspecified, corrupt or
foreign records hold. Fixture SQL seeds candidates; no public issuance API can
retrofit old orders. Six new fixtures preserve old financial/frozen/OWED rows,
reopen exact identity and roll back duplicate insertion without replacement.
17 focused PASS, zero failure/error/skip, 0.097s. Intermediate 16 PASS/0.093s
preceded the duplicate-rollback case. Windows/Linux registration includes actual
six-method receipt checking on Linux. Full/current CI pending for this containing
source micro-push. Next final applicable full/current receipts, then UX-07.i2
atomic issuance during original new-order creation, before provider POST.
[Implementation boundary](UX07-PURCHASED-PRINT-INTEGRATION.md) / [source/results/hashes](evidence/ux07-delivery-requirements.json).
Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/release
separate, Sandbox printer/Drive OFF and OPS unchanged. No schema rewriting or
automatic backfill; rollback disables adapter and retains additive table/records.
Only existing work/ and superseded docs stash local; no unpublished source after
push. This source micro-push is a safe checkpoint; resolve containing SHA via Git.
