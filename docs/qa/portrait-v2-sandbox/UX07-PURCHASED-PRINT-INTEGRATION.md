# UX-07.h — purchased-print integration contract and source audit

30 October 2026 (Asia/Jakarta). Status: UX-07.i1/i2 schema and atomic mock issuance, j/k offline
purchase/paid-print fixtures and l native result-widget subset focused-verified;
commercial host remains unmounted; final full/current CI verified below.
Historical pre-i1 branch/remote base:
`613243ab956001b24cde8f7a76bf1b3673a63d2a`. Pre-implementation baseline evidence was
e7e09fe: 1188 run / 1184 PASS / 4 optional SKIP, CI 40959449442 SUCCESS.

Reviewed AGENTS/protocol/prompt, checkpoint/handover, AR roadmap/master,
readiness/fulfillment/operations, print/Drive contract, current device evidence
and preservation records. Audited the source seams below; no archive access.

## Baseline source audit before i1/i2/j/k integration

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

UX-07.i1/i2 and j/k fixtures are verified; l result-worker/close subset is
verified. Next UX-07.l2: audit the original customer-claim/pause/resume/safe-release
lifecycle and write its offline fixture contract before source. Commercial host
mounting and operating delivery/support policy are separate. Do not enable
dedicated Sandbox delivery or treat UI close/SUBMITTED as safe paid release.
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

Final review refinement before code: newly issued PRINT_REQUIRED_V1 mock orders
must include the existing validated customer capability hash. Legacy/default
orders retain their optional-field behavior. This ensures the new fixture policy
cannot create a paid-print obligation with no original self-claim credential.
No token is generated/logged by the backend. Missing hash rejects before any
order/requirement/provider effect. An initial full invocation at 9417e9d is
superseded/interrupted, not counted as a final regression; repeat after this fix.

## 30 October — credential focused source checkpoint

Base/remote 9417e9d5985319fa6f30d147f95b8f36ff93047c.
Final mock-policy refinement: new PRINT_REQUIRED_V1 orders require the existing
validated customer capability hash before any order/requirement/provider effect.
Default/legacy optional-field behavior remains unchanged; no backend token logging
or automatic token generation. Missing hash is now an explicit issuance rejection
vector; healthy purchase fixtures carry a hash of a known synthetic capability.
29 combined native/job/purchase/issuance/schema PASS, zero failure/error/skip,
12.580s. Initial full invocation at 9417e9d was deliberately interrupted/superseded
(exit137, no final report), never counted PASS; disposable unittest only, no live
customer process or records. Next final full at this source and current Windows/
Linux CI, then checkpoint. No further functional edits planned before final checks.
Continue session until verified; actual customer-facing host remains unmounted.

Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/
release and PAY-22/WEB gates remain separate. No Sandbox delivery opt-in/OPS/
production/public ingress/new branch/master/default/deployment or real external
effect. Rollback scoped inverse code; retain additive requirements and all
financial/media/audit records. Only private work/ and superseded docs stash local.
Containing source commit is the safe checkpoint; exact SHA via Git log/remote.

Post-regression review: source 520b1a6 full 1217/1213/4 and CI 40967942002
SUCCESS remain historical. A new targeted counterexample shows active mock-print
replay still depends on current artwork via backend frozen_contract(). Same order
and one provider effect are preserved, but recovery raises when artwork is absent.
For explicit mock delivery configuration only, replay must read/validate the
original persisted frozen contract, not today's assets. Missing/corrupt historical
snapshot stays held; no fallback repair/adoption. Default backend behavior stays
unchanged. Add exact regression, then rerun final applicable full/current CI.

## 30 October — replay focused source checkpoint

Base/remote 520b1a6791c6e8da4b891bf230a8bd5709bf25f4.
Mock print recovery now reads the original persisted frozen contract on existing
keys instead of requiring current artwork. Original source 520b1a6 passes its
1217/1213/4 full suite (627.965s) and CI40967942002, but a new targeted missing-
artwork counterexample correctly exposed this new-profile recovery gap; those
results remain historical, not final evidence for the correction. One original
order/provider effect was preserved even in the failing probe; no payment loss.
New regression verifies recovery with no current templates/assets and holds a
corrupt old snapshot without repair/adoption. Default backend behavior unchanged.
53 focused PASS/zero failure/error/skip, 10.702s, including both native methods,
all paid fixture stages and original backend/polling regression. Seven purchase
methods now required in CI receipts. Next one final full/current CI at corrected
source, then final checkpoint. Continue session; no live customer-facing host.

Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/
release and PAY-22/WEB gates remain separate. No Sandbox delivery opt-in/OPS/
production/public ingress/new branch/master/default/deployment or real external
effect. Rollback scoped inverse code; retain additive requirements and all
financial/media/audit records. Only private work/ and superseded docs stash local.
Containing source commit is the safe checkpoint; exact SHA via Git log/remote.

Additional test-only compatibility increment while the corrected final functional
source regression runs: exercise the original FastAPI/TestClient/QrisKioskClient/
KioskCheckout path with the explicitly configured mock policy. Verify generated
recovery-ticket hashes, private restart/customer proof and preserved requirements;
reject a client-supplied delivery policy, missing hash and foreign booth. These
are additional tests, not a new endpoint/launcher or live HTTP server. The full
functional-source snapshot excludes these later tests; focused/current CI must
verify them separately without borrowing counts or rerunning unchanged runtime.

## 30 October — http focused source checkpoint

Base/remote e82d0eef032edfcbedec0a9f4c172e9c5edaad5e.
UX-07 HTTP/client/controller compatibility: three new methods use original
FastAPI API, QrisKioskClient and KioskCheckout against explicitly selected mock
backend with no live network/provider. Original recovery ticket survives local
journal restart and customer claim, retains the same frozen requirement and OWED
obligation; one provider effect only. Original HTTP idempotent replay reads the
original DB snapshot without current artwork, rejects changed cart. Client-sent
delivery_policy, missing recovery credential and foreign-booth reads reject.
18 focused PASS, zero failure/error/skip, 0.825s. Initial fixture invocation
omitted refresh (begin only journals locally): 18 run/one ERROR, then corrected
test sequencing; no runtime guard change. Added all three tests to Windows/Linux
ledgers and exact Linux method receipts. Application code unchanged from e82d0ee.
Full regression already running at functional e82d0ee excludes these three later
test-only methods; this focused receipt plus matching current CI cover them.
No endpoint/controller/launcher mounting or commercial lifecycle claim. Next:
finish full regression, actual matching CI receipts, reconcile all docs and push
a final verified safe checkpoint; do not repeat already verified source work.

Whole UX-07 NOT_RUN, matrix59/0/9/1; actual devices/provider/paper/privacy/
release and PAY-22/WEB gates remain separate. No Sandbox delivery opt-in/OPS/
production/public ingress/new branch/master/default/deployment or real external
effect. Rollback scoped inverse code; retain additive requirements and all
financial/media/audit records. Only private work/ and superseded docs stash local.
Containing source commit is the safe checkpoint; exact SHA via Git log/remote.

## 30 October — owner-requested durable progress checkpoint / final regression pending

All seven source/test increments are pushed on feature/portrait-kiosk-v2-next.
Latest verified GitHub/source HEAD: **2cac0ba0dda4df996ab514080a071e99f79272dd**.
Application functional source: **e82d0eef032edfcbedec0a9f4c172e9c5edaad5e**;
2cac0ba adds only three HTTP compatibility methods and CI/docs registration.
Atomic mock requirement issuance, mock purchase/preflight fixture, paid print
intent/no-replay fixture, original native result-widget fixture, mandatory original
recovery credential, original-contract artwork-independent replay and original
HTTP/client/controller compatibility are all focused-verified/pushed. Exact stage
SHAs and historical file hashes are pinned in evidence/ux07-{stage}-verification.json.

Latest HTTP-focused **18 PASS/0 FAIL/0 ERROR/0 SKIP**, 0.825s. Source e82d0ee CI
**40969577970: all three jobs SUCCESS**; current 2cac0ba CI **40970539519 pending**.
The e82d0ee full attempt is **1218 run/1213 PASS/1 FAIL/0 ERROR/4 optional SKIP**,
463.881s: unchanged native audio PCM test, cycle7, empty samples. Preserve this
failure; do not report final full PASS. Isolated unchanged native audio then
**2 PASS**, 12.866s, including its20-cycle PCM check; exact initial cause unknown.
A fresh full regression is RUNNING at 2cac0ba, including HTTP3; no code/assertion
changes or skip introduced to hide the failure. Source520's earlier1217/1213/4
full success is historical only, before the replay correction.

Private progress files: work/paid-chain-replay-full.txt (failed full),
work/paid-chain-audio-isolated.txt (2 PASS), work/paid-chain-final-retry-full.txt
(final full report written on completion), work/paid-chain-final-retry-console.txt.
Active local test session20325 is disposable synthetic unittest only. On a new
session, inspect current Git/remote and those reports; process IDs may be stale.
Next: finish/check retry, investigate any repeat failure, read actual current CI
job/method receipts, publish aggregate exact-source evidence and final verified
checkpoint. No additional functional change is pending locally. Do not redo the
seven delivered stages or mistake an interrupted test for PASS.

UX-07 whole NOT_RUN; matrix59 PASS/0 FAIL/9 BLOCKED/1 NOT_RUN. Native commercial
claim/pause/release host remains unmounted; operating paper acceptance/support/
compensation and actual Windows/Ubuntu/provider/privacy/release gates remain.
AR-13 conditional/audit IN_PROGRESS; Sandbox delivery OFF, OPS queued docs only.
No real provider/printer/Drive/deletion/public ingress/production/default/master/
branch change. Only private synthetic work/ and old superseded docs stash remain
local; no unpublished application patch. This docs-only checkpoint must be
micro-pushed immediately and remote HEAD verified before continuing tests.

## 30 October — mock paid-print chain regression and current CI verified

Latest source/test GitHub HEAD **2cac0ba0dda4df996ab514080a071e99f79272dd**; functional source **e82d0eef032edfcbedec0a9f4c172e9c5edaad5e**.
Owner-requested interim checkpoint **9ea05be4142ec856e33c913d2a7a1156c6dd4f36** also pushed/remote verified.
Seven safe micro-increments were committed/pushed independently with focused
tests and documentation: atomic mock requirement issuance (i2), original
prepayment/printer-readiness purchase fixture (j), bound durable print jobs and
two real crash exits/no resend (k), original native result-worker/close fixture
(l subset), mandatory original recovery capability, artwork-independent replay
of original DB contract, and original HTTP/client/controller compatibility.
Exact seven commit SHAs and historical focused results/hashes are in the receipt.
Default/legacy contracts, Sandbox transport guards, original printer/controller/
renderer/audio/Drive services and queued OPS remain unchanged. Requirement,
original order/attempt/frozen snapshot/capability commit together before POST;
recovery never creates a new identity. Fake SUBMITTED/UNCERTAIN remains OWED.

Final full at2cac0ba: **1221 run / 1217 PASS /0 FAIL/0 ERROR/
4 optional SKIP**, 449.903s, Python3.12.14/Linux.
Includes all three later HTTP methods; no exclusion in this final full. The four
skips are three opt-in palm-model asset tests and one optional native video test.
CI **40970539519 all three jobs SUCCESS**, exact source2cac0ba;25 new pure methods
individually PASS Windows/Linux;2 new native methods PASS Linux at800x1280 and
452x900. Windows ledger164 PASS; Linux recovery
465 PASS; native119 run/
118 PASS/one optional palm SKIP. Native result tests are
worker/truthful-submission/privacy assertions, not new commercial host screens.

Preserved e82 full attempt:1218 run/1213 PASS/one FAIL/zero ERROR/four SKIP,
463.881s. Unchanged native PCM cycle7 collected no samples in its observation;
exact cause unknown. Isolated unchanged20-cycle audio test then2 PASS/12.866s;
final full retry above passes without source/assertion/skip changes. This
unresolved failure justified repeating the broad suite. Earlier520 full success
is historical before replay refinement; interrupted9417 full has no final PASS.
No failing report discarded or relabelled. [Exact source/results/hashes](evidence/ux07-paid-chain-final-verification.json).

Whole UX-07 **NOT_RUN**;69 matrix IDs remain **59 PASS/0 FAIL/9 BLOCKED/1 NOT_RUN**.
AR-13 conditional/audit IN_PROGRESS. PAY-22 official Legacy contract and WEB-01..08
approved infrastructure/operations BLOCKED. Actual Windows/Ubuntu devices,
provider/paper/phone/Drive/deletion/privacy/support/release acceptance separate.
Next: UX-07.l2: use the recorded lifecycle source audit to define and test the offline original customer-claim/pause/resume/safe-release fixture on original controllers/fences/leases. The source audit is documentation only; l2 fixtures remain NOT_RUN. The current l subset verifies result worker and close retirement only; do not claim commercial host mounting or paid release. Refuse uncertain/SENDING replay, preserve OWED and privacy, no new financial identity. Operating physical-delivery principal/evidence, support/compensation and controlled Windows/Ubuntu/provider/paper/phone/Drive/privacy/release acceptance remain separate. Keep dedicated Sandbox delivery OFF, PAY-22/WEB-01..08 BLOCKED, OPS queued docs only.

Do not redo these seven stages or reapply the superseded local documentation
stash. In a new account/session first inspect branch/status/latest remote and
this checkpoint; review l2 contracts before further source work. Raw private
synthetic work/ remains local; no unpublished application patch. Rollback uses
scoped reviewed inverse code while retaining additive requirement/financial/
capability/audit/media records. This final docs-only publication is the safe
checkpoint; resolve its containing SHA from Git log/remote after push. No real
provider/print/Drive/deletion, production/public ingress/deployment/OPS/new
branch/master/default operation. All checked/pushed progress is recoverable
from GitHub; scratch data is intentionally excluded.

## UX-07.l2 remaining lifecycle source audit — not executed acceptance

Read-only source at2cac0ba, after reviewing original AR-06 customer claim,
AR-09 operator/release and operations contracts. Reuse these exact seams:

| Original seam | Audited behavior | Next fixture evidence required |
| --- | --- | --- |
| `PortraitKioskV2App.on_pause` / `SandboxViews._sandbox_lock_customer` | Bound Sandbox flow clears customer proof, photo media, QR/input and privacy epoch; ordinary result injection has Sandbox flags OFF | Pause/late callback must remain private after resume until original ticket is revalidated; do not infer this from the current close-only fixture |
| `PhotoViews._photo_pause` | Cancels countdown; does not implement customer re-claim by itself | No automatic shutter/print on resume; original customer proof and deliberate continuation |
| `KioskCheckout.lock_customer` / `customer_claim` | Retires in-memory proof/generation, original capability/action and fresh settlement required | Wrong/expired/foreign ticket and late reply deny, original paid identity/copies/OWED unchanged |
| `PhotoTest.hide_private` / `isolate` | Original transport-off worker issues typed isolation receipt; SENDING/UNCERTAIN holds | Run on serialized original worker only after synthetic sender drains; no boolean or forced advertising |
| `KioskCheckout.prepare_release` / `acknowledge_release` | Durable original operation, exact allocation/isolation generation, archive before suspended/new visit | Lost ACK/restart preserves one original release; no new visit before durable ACK/archive |
| `KioskCheckout.open_archived` / original service fence | Original ticket may reacquire only a free booth, same allocation and new current fence | New visitor cannot see old strip; returning customer cannot preempt active visitor or replay old print |

The existing fixture adapter must not simply become active again when its
`active` predicate returns true after resume. Its current native tests deliberately
cover result/close only; this audit does not establish a production privacy bug
in the unchanged Sandbox host. Use the original proof/privacy generation, not a
new UI boolean or a permit minted without original customer authentication.

Next source micro-increment: isolated lifecycle fixture/test contract on the
original controller and transport-off photo worker, with the mock print job kept
separate and lease held through its in-flight completion. Test SENDING and
UNCERTAIN refusal before any release, then exact original PREPARE/isolation/ACK
for an eligible drained worker; ACK releases occupancy only, never satisfies OWED
or proves paper. Do not attach a printer to bound Sandbox PhotoTest, weaken its
transport guard, fabricate delivery/compensation, auto-restart/print or mount a
commercial host. Focused fixtures, Windows/Linux receipts and both portrait sizes
precede any PASS claim. Operating physical-delivery/support/compensation and real
device/provider/release acceptance remain open. No l2 tests or source added by
this audit; original existing release tests retain their own earlier evidence.
