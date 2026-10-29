# UX-07.h — purchased-print integration contract and source audit

30 October 2026 (Asia/Jakarta). Status: UX-07.i1 explicit schema/read adapter VERIFIED;
issuance and host integration remain PLANNED, not mounted or certified. Branch/remote base:
`613243ab956001b24cde8f7a76bf1b3673a63d2a`. Pre-implementation baseline evidence was
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
infrastructure/operations remain BLOCKED. The UX-07.h audit supplied no new automated, merchant or device PASS.
UX-07.i1 below adds explicit schema/read validation; physical gates stay open.

UX-07.i1 fixtures/schema/read validation are now verified below. Next UX-07.i2
adds atomic new-order issuance before POST, with unchanged legacy contracts. Review this contract plus existing fulfillment/allocation and
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

## 30 October — UX-07.i1 schema/read adapter regression verified

Source `0b8aaa85ff692cf21d4c1c390815f1e4c634ef2b` pushed/remote verified. Explicit additive table and read-only
adapter remain unmounted: default CheckoutStore/backend/HTTP/GUI do not initialize
or call it. No issuance API. Candidate requirements are seeded only by fixture SQL.
Reads validate original order/booth/merchant, frozen hash and exact copies; absent
owned records are unspecified, unknown legacy merchant context stays held. Existing
paid OWED rows, frozen JSON/hash and all financial rows remain unchanged. Duplicate
insertion rolls back; independent reopen returns the same requirement identity.

17 focused PASS/zero failure/error/skip, 0.097s. Final full **1194 run / 1190 PASS /
4 optional SKIP**, zero failure/error, 409.581s, Python 3.12.14/Linux
software GL/dummy audio. Three palm assets and one native video skipped, not PASS.
CI 40962843450 all three jobs SUCCESS on exact source; six new methods individually
PASS on Windows/Linux. [Commands/source/results/receipts/hashes](evidence/ux07-delivery-requirements.json).
No screenshot rerun: no GUI change. Original backend/store/native/tools/OPS remain
unchanged from d458012; the only application addition is the unmounted module.

Next UX-07.i2: atomically issue requirements inside original new-order creation
before POST; policy/absence replay conflicts must hold, never retrofit old orders
from today's settings. Then UX-07.j offline fake-provider/fake-printer adapter.
Whole UX-07 NOT_RUN; matrix59/0/9/1, audit IN_PROGRESS/AR-13 conditional. Real device/
provider/paper/privacy/support/release gates remain separate. Sandbox printer/Drive
OFF; no OPS/production/public ingress/branch/master/default/deployment or actual
external effects. Rollback disables adapter but preserves its additive table and
all original financial/media/audit records. Only work/ scratch and superseded docs
stash local; no unpublished runtime patch. This containing docs-only push is the
final safe checkpoint; exact SHA from Git log/remote. Do not repeat verified work.

## 30 October — i2/j execution contract before code

Continue through dependent safe source increments without ending the session at
micro-push boundaries (owner request). UX-07.i2 adds a keyword-only trusted
storage policy, default None. PRINT_REQUIRED_V1 is allowed only in mock creation
context with a frozen quote; dedicated Sandbox issuance rejects. Initialize the
additive table explicitly before begin, then insert the requirement inside the
same BEGIN IMMEDIATE as original order/frozen/capability/attempt rows. Any failure
rolls everything back. Same-key replay must match stored policy/absence; never
attach a new policy to an existing order. Freeze copies from the original hash,
not caller print quantities. Add independent-connection concurrency, SQL rollback
and actual child exit tests before accepting the transaction seam.

UX-07.j then exposes that storage option only through an explicit mock-provider
backend configuration, default None, not through HTTP request bodies or launcher
flags. An offline fixture host reuses camera/storage/template readiness plus
original read-only printer probe off the UI; freshness is rechecked after probe.
A same-key existing order reconciles without a new probe or POST, but must still
match original cart/policy. Probe failure cannot create an order or consume a
capability. All provider/printer transports in the host are synthetic. Physical
acceptance and customer-facing mounting remain separate external gates.

## 30 October — i2 focused source checkpoint

Base/remote f90bcea79a10d735f5b7c6dd2c4c564317e6d683.
UX-07.i2 atomic mock-only issuance: trusted storage policy defaults None;
PRINT_REQUIRED_V1 requires mock creation context and frozen quote. Original new
order, attempt, frozen JSON/hash, capability and requirement commit in one
transaction. Existing policy/absence conflicts hold, no retrofit/downgrade.
Default store does not initialize the schema. Sandbox issuance rejects.
Eight new methods include two actual child exits before/after commit, SQL and
invalid frozen-contract rollback, independent-connection concurrency, replay and
old default compatibility. 73 focused PASS, zero failure/error/skip, 0.632s.
Initial missing-interface baseline seven run/one FAIL/nine ERROR (subtests),
not a pre-existing payment defect. Intermediate 72 PASS/0.620s retained locally.
No backend/HTTP/GUI mounting. Next UX-07.j offline purchase/readiness host;
continue this session after immediate source push. Full/current CI pending,
one full after final functional chain increment.

Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/
release and PAY-22/WEB gates remain separate. No Sandbox delivery opt-in/OPS/
production/public ingress/new branch/master/default/deployment or real external
effect. Rollback scoped inverse code; retain additive requirements and all
financial/media/audit records. Only private work/ and superseded docs stash local.
Containing source commit is the safe checkpoint; exact SHA via Git log/remote.

## 30 October — j focused source checkpoint

Base/remote 6aebbc0e538f637a45a821556c1e270527abcbc3.
UX-07.j nonpayable purchase/preflight fixture host on original backend/store.
Explicit backend delivery policy is mock-only/default None; HTTP bodies and
launchers unchanged. Fixture checks original camera/storage/template readiness,
printer observation and post-probe freshness before create. Existing key returns
same original order without a probe; different key/cart cannot replace it.
Lost provider reply retains requirement and retries only GET for same identity.
Six new methods; 47 focused PASS/zero failure/error/skip, 0.612s. Provider callback
checks requirement persisted before its one synthetic effect. No real QRIS URL,
printer send, Drive or customer-facing mounting. Next UX-07.k exact paid job binding
and real exit/no-replay fixtures, then native worker/UI evidence. Full/current CI
pending until the final functional chain increment; continue after source push.

Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/
release and PAY-22/WEB gates remain separate. No Sandbox delivery opt-in/OPS/
production/public ingress/new branch/master/default/deployment or real external
effect. Rollback scoped inverse code; retain additive requirements and all
financial/media/audit records. Only private work/ and superseded docs stash local.
Containing source commit is the safe checkpoint; exact SHA via Git log/remote.

## k/l fixture contract before implementation

Do not attach a printer to a bound Sandbox PhotoTest or relax its start/restore
transport-off guards. The separate mock-only fixture print host must authenticate
original customer capability and fresh settlement, reconstruct exact committed
media using the original validator/ResumePermit and own an original KioskLease.
Reuse PhotoTest.print_result and its manifest writer through a distinct adapter,
with a synthetic injected printer only. Add requirement/binding/output-hash to the
original pre-send job intent. Existing unknown/unbound intents cannot be adopted.
No new printer driver or application mount. Own lease through in-flight teardown;
closed/retired callbacks cannot show media or initiate a fresh send. SUBMITTED and
operator_checked never satisfy OWED or authorize replay. Real child exits after
intent and after a modeled send must hold the same job on restart without resend.
Native fixture tests use existing PhotoJobs/PhotoViews/result layout at both sizes;
UI retirement is not proof of safe paid booth release or physical fulfillment.

## 30 October — k focused source checkpoint

Base/remote a349996d988bebac45d11c38940add43ab646938.
UX-07.k separate mock-only fixture print host authenticates original customer
capability and fresh settlement, validates original allocation/copies/output with
original reconstruction/ResumePermit, owns original KioskLease, reuses actual
PhotoTest.print_result/_edit without attaching a printer to bound Sandbox photos.
Requirement/binding/output-hash persist in SENDING before synthetic transport.
SUBMITTED/UNCERTAIN never satisfy OWED or permit replay. Close retires media but
holds native lease through in-flight worker completion. Seven new methods include
two real child exits after intent/after modeled effect, duplicate/restart hold,
wrong customer/refund/corrupt media/fence denial and two-design copy mapping.
63 focused PASS/zero failure/error/skip, 15.568s. Initial fixture used two-digit
session IDs (actual original IDs have three digits): 26 run/two FAIL/five ERROR;
corrected intermediate 26 PASS/4.889s. Expanded initial invocation was interrupted
without a final report; exact hang cause unknown. Fresh software-GL/network-enabled
repeat at unchanged source gives the 63 PASS above; no runtime patched for that.
Next native fixture registration/push (tests/test_purchased_print_widgets.py is
local-only until that next micro-push), then one final full/current CI. Continue
this session. No customer-facing host or physical send enabled.

Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/
release and PAY-22/WEB gates remain separate. No Sandbox delivery opt-in/OPS/
production/public ingress/new branch/master/default/deployment or real external
effect. Rollback scoped inverse code; retain additive requirements and all
financial/media/audit records. Only private work/ and superseded docs stash local.
Containing source commit is the safe checkpoint; exact SHA via Git log/remote.

## 30 October — l focused source checkpoint

Base/remote 9739ce4d0a06b9e112662ffdd323bff94df25bde.
UX-07.l native fixture subset uses original PhotoJobs/PhotoViews/result layout
with the separate paid mock print adapter, at 800x1280 and 452x900. Real Clock
progresses while send is held; duplicate taps remain single-flight, displayed
SUBMITTED says inspect physical paper and never satisfies OWED. Closing a retired
view prevents queued results/private strip from reappearing and retains ownership
through worker completion. No forced advertising transition or paid booth release.
29 combined focused PASS, zero failure/error/skip, 8.736s; includes two new native
methods and all 27 issuance/purchase/job/schema methods. Initial native attempt:
two run/two ERROR because existing navigation correctly refused active-photo
return to advertising. Next 29 run/two ERROR from fixture Window.walk misuse;
fixed to inspect Window child widgets. Original app/guards/layout unchanged.
No commercial native paid host or automatic pause/resume claim journey mounted;
these and actual device/provider/paper/privacy/release acceptance remain separate.
Next one final full regression and current Windows/Linux CI, then final safe
checkpoint. Earlier intermediate source CI runs may be superseded; do not claim
whole-run success without final matching receipts. Continue session until verified.

Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/
release and PAY-22/WEB gates remain separate. No Sandbox delivery opt-in/OPS/
production/public ingress/new branch/master/default/deployment or real external
effect. Rollback scoped inverse code; retain additive requirements and all
financial/media/audit records. Only private work/ and superseded docs stash local.
Containing source commit is the safe checkpoint; exact SHA via Git log/remote.
