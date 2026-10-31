# Meong Photobooth — current feature status

## 31 October — BUG-026 Sandbox QR renewal

Same-checkout verified expiry replacement preserves design/copies/amount, new key and ticket; one automatic then manual renewal, untouched button returns to ads after30s. Dedicated Sandbox only, camera/storage/privacy/financial guards retained. Final15 focused PASS; functional5201c10 full1251/1247 PASS/4optional SKIP, zero failure/error; corrected-source0d92831 CI41205340183 all three SUCCESS. Owner laptop NOT_RUN.
[Contract/evidence](qa/portrait-v2-sandbox/BUG026-QR-RENEWAL.md).


## 30 October — BUG-025 — owner-only Sandbox legacy archive

Explicit no-ticket legacy Sandbox operator archive now mounted in native UI with confirmation/cancel and two-phase release. Normal ticket/privacy and printer/Drive-off boundaries preserved. Source7069bf0 full1236/1232 PASS/4optional SKIP, zero failure/error; CI41001339113 all three SUCCESS. User laptop NOT_RUN. Commercial acceptance unchanged.
[Contract/evidence](qa/portrait-v2-sandbox/BUG025-LEGACY-NO-TICKET.md).


## 30 October — UX-07.l2 automatic fixture checks verified / laptop handoff

Final test/fixture source **ca7827c28c02e8fb2650f0a86cacdeb129c8434c**.
Full **1229 run /1225 PASS /0 FAIL/0 ERROR/4 optional SKIP**,544.661s,
Linux/Python3.12.14/Kivy2.3.1/softwareGL/dummy audio. Current CI
**40985975287 all three jobs SUCCESS**, exact sourceca7827c. Six new l2 portable
methods individually PASS Windows/Linux; two l2a native methods individually
PASS Linux at800x1280/452x900. Windows ledger170 PASS; Linux recovery471 PASS;
native121 run/120 PASS/one optional palm SKIP. Full's four skips are three
optional native palm-assets methods and one native-video opt-in.

Source d091 Windows failed job170/169PASS/oneERROR is retained; run40985455735
was superseded/cancelled. The locked-file PermissionError fixture correction
adds post-drain reacquisition proof, preserving original source guards. Earlier
d091 disposable full was interrupted exit130/no final PASS. Final current full
above includes all eight l2 methods; no exclusion or lowered assertion/skip.
[Exact source/results/hashes](qa/portrait-v2-sandbox/evidence/ux07-l2b-verification.json).

The approved offline lifecycle fixture increment is verified: original ticket/
privacy generation, explicit resume, frozen copies/output, separate mock sender,
SENDING/UNCERTAIN hold, original worker isolation, PREPARE/ACK/archive, lost ACK/
restart/return and unexpired same-owner fencing. No application, launcher,
production or Sandbox transport guard changed; no commercial host mounted.
Private mock release wire is not HTTP/operator/merchant acceptance.

**Next owner action:** [nine-item laptop check](qa/portrait-v2-sandbox/UX07-LAPTOP-CHECK.md), recording
actual SHA/device/results and keeping all secrets/private media out of reports.
No further independent l2 fixture source step is pending. Commercial paid-host
mounting still requires its explicit operating/acceptance contract; laptop tests
alone do not close that gap. Whole UX-07 **NOT_RUN**, matrix**59 PASS/0 FAIL/
9 BLOCKED/1 NOT_RUN**; AR-13 conditional/audit IN_PROGRESS. PAY-22 Legacy contract
and WEB01–08 infrastructure stay BLOCKED; Windows/Ubuntu/device/merchant/paper/
Drive/deletion/privacy/support/compensation/release are separate manual/external
gates. OPS stays queued docs only; no default/master/new branch/deployment.

All safe new work is pushed on the same branch; source/CI receipt above pins the
fixture code. The containing follow-up is documentation only; resolve its SHA
from Git/remote. Original dirty legacy workspace /workspace/PhotoBooth remains
untouched/local-only, not reapplied or backed up by these pushes. Current clean
same-branch checkout is /workspace/work/photobooth-ux07-l2; only private work/
scratch remains untracked. Rollback reviewed inverse tests/fixture changes only;
never alter orders, obligations, manifests, photos, copies, grants or retention.


## 30 October — l2b Windows lease portability correction

Source d0911b6 CI40985455735 Windows170 run/169PASS/oneERROR (65.547s):
second owner was correctly denied by native locked-file read PermissionError,
before KioskLease's locking wrapper. Linux returns RuntimeError. Fixture now
accepts either explicit denial AND requires that exact lease be obtainable after
sender drain. No application/lock/assertion invariant weakened. Five corrected
methods PASS/zero failure/error/skip locally,3.432s. Failed run remains historical.
The disposable d091 full invocation was superseded/interrupted exit130 without
final summary/PASS. Final full/current Windows/Linux CI now required; no repeated
functional change. [Receipt](qa/portrait-v2-sandbox/evidence/ux07-l2b-verification.json).

[Owner laptop checklist](qa/portrait-v2-sandbox/UX07-LAPTOP-CHECK.md) lists nine initially NOT_RUN
checks and distinguishes original Sandbox from unmounted commercial paid print.
Whole UX-07 NOT_RUN; matrix59/0/9/1 unchanged, PAY-22/WEB01–08 BLOCKED.
Next finish final full/current CI then publish exact owner/manual handoff;
no production/merchant/physical/OPS/deployment/master/default operation.


## 30 October — UX-07.l2b original release/drain fixture focused-verified

Base3b0bdc1. Five new methods reuse original controller/store two-phase release,
original serialized transport-off PhotoJobs/PhotoTest isolation and separate mock
sender/lease. SENDING/UNCERTAIN hold; drained SUBMITTED permits occupancy release
only after exact isolation/ACK/archive. LostACK/controller restart repeats one
operation/isolation; archive failure blocks new visitor; original ticket returns
only to free booth. Old mock adapter captures original controller privacy
generation/permit, so a fresh claim cannot reactivate a retired adapter.
Original PAID/OWED, identities, frozen copies/requirement/output hash and every
manifest field outside legitimate print-job updates remain unchanged.

The private test wire calls original fresh-payment verifier and release-store
functions; it is NOT a runtime/API/operator-auth host. Original mock HTTP release
is explicitly asserted rejected, and Sandbox PhotoTest still has no transports.
No production guard changed. Initial4methods/3fixture ERROR from budgeted poll
and exception-type mismatch retained privately; corrected fixture uses existing
fresh verifier/actual RuntimeError, no assertion/skip dilution. Expanded final
16 focused PASS/zero failure/error/skip,9.499s (five new methods). New Windows/
Linux CI and final complete-suite evidence PENDING. Application code unchanged.
[Receipt](qa/portrait-v2-sandbox/evidence/ux07-l2b-verification.json).

Next finish current full/CI, synchronize evidence and laptop instructions.
Whole UX-07 remains NOT_RUN; matrix59/0/9/1 and PAY-22/WEB01–08 BLOCKED unchanged.
Commercial host/physical delivery principal/support/compensation and actual
Windows/Ubuntu/provider/paper/privacy/release acceptance remain open.


## 30 October — UX-07.l2a original privacy/controller fixture

Continuation refreshed remote/base to `8ab955b` (same branch); previous source
2cac0ba/full1221 and CI40970539519 remain historical exact-source evidence.
New test-only micro-increment: original Sandbox app/controller/PhotoJobs with
transport OFF exercises pause/resume, original/incorrect/foreign ticket, retired
claim callback and deliberate continuation at800x1280/452x900. Original mock
PRINT_REQUIRED_V1 HTTP/controller + transport-off PhotoTest additionally proves
retired/expired resume permission cannot restore photos; original requirement,
allocation/copies, file/manifest bytes, one provider effect and PAID/OWED preserved.
Two native methods PASS/15.702s; one portable method PASS/0.214s; no skips/errors/
failures in final focused runs. Initial fixture2methods/4subtest ERROR used the
wrong LocalTransaction attribute; fixed fixture to existing folder_path, no
application guard/assertion change. [Receipt](qa/portrait-v2-sandbox/evidence/ux07-l2a-verification.json).
Test source `abb086c`: CI **40977963717 all three jobs SUCCESS**. Exact log
receipts confirm the portable method PASS Windows/Linux and both native methods
PASS Linux at both portrait sizes. Windows ledger165 PASS; Linux recovery466
PASS; native121 run/120 PASS/one optional palm SKIP. No native Windows/device
acceptance. The containing docs-only follow-up preserves these test hashes.
No application/runtime or commercial host change, no physical/provider/cloud
operation; do not rerun unchanged historical full solely for these test additions.

Next UX-07.l2b: original paid-print worker drain, SENDING/UNCERTAIN release holds,
exact PREPARE/isolation/ACK/archive/lostACK/restart/return fixture. Current source
subset is not the complete purchased lifecycle or commercial acceptance. Whole
UX-07 NOT_RUN; matrix59PASS/0FAIL/9BLOCKED/1NOT_RUN unchanged; PAY-22/WEB01–08
remain BLOCKED and AR-13 conditional/audit IN_PROGRESS. Original dirty workspace
at /workspace/PhotoBooth was preserved; this increment uses a clean same-branch
checkout, no new branch or restoration of obsolete local patches.


## 30 October — mock purchased-print chain verified

Seven source/test micro-pushes through2cac0ba (functional e82d0ee); atomic original
order/requirement issuance, mock readiness/purchase, paid print no-replay jobs,
native result-worker fixture and original HTTP/recovery compatibility verified.
Full **1221 run/1217 PASS/4 optional SKIP**, zero failure/error;
CI40970539519 all three jobs SUCCESS,25 pure methods Windows/Linux and2 native
methods Linux. Earlier native-audio full failure retained; isolated unchanged
repeat and final full PASS, initial cause unproven. No runtime guard relaxed.
Whole UX-07 NOT_RUN, matrix59/0/9/1, AR-13 conditional/audit IN_PROGRESS. Next
UX-07.l2 original claim/pause/resume/safe-release lifecycle contract/fixture;
commercial mounting/operating policy and actual devices/provider/release remain.
Sandbox delivery OFF; no production/OPS. [Exact evidence/limits/next](qa/portrait-v2-sandbox/evidence/ux07-paid-chain-final-verification.json).

## 30 October — http focused checkpoint

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
[Full scope/limits/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — replay focused checkpoint

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
[Full scope/limits/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — credential focused checkpoint

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
[Full scope/limits/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — l focused checkpoint

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
[Full scope/limits/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — k focused checkpoint

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
[Full scope/limits/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — j focused checkpoint

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
[Full scope/limits/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — i2 focused checkpoint

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
[Full scope/limits/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — UX-07.i1 explicit schema/read adapter verified

17 focused PASS; full 1194/1190/4, zero failure/error. Current three-job CI
SUCCESS; six new methods PASS Windows/Linux. Adapter/table initialization is
explicit, unmounted; no issuer or default checkout/GUI change. Next UX-07.i2
atomic new-order issuance before POST, then offline purchase/preflight adapter.
Whole UX-07 NOT_RUN, matrix59/0/9/1; actual device/provider/release gates separate.
[Exact evidence/next](qa/portrait-v2-sandbox/evidence/ux07-delivery-requirements.json).

## 30 October — UX-07.i1 explicit requirement schema/read adapter

17 focused PASS/zero skip; six new migration/identity/rollback fixtures.
No default backend/HTTP/GUI mount or issuance API. Full/current CI pending.
Whole UX-07 NOT_RUN, matrix59/0/9/1 unchanged.
[Exact scope/evidence/next](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — UX-07.h purchased-print integration contract audited

Documentation-only source reconciliation: frozen quantities/COMPOSED/OWED and
Sandbox transport isolation preserved. No paid-print runtime is mounted and no
new acceptance claimed. Next UX-07.i offline delivery-requirement migration/
compatibility fixtures, then additive storage, before any future host integration.
Matrix 59/0/9/1 unchanged; previous full/CI retain their original source.
[Exact contract/next increments](qa/portrait-v2-sandbox/UX07-PURCHASED-PRINT-INTEGRATION.md).

## 30 October — UX-07.g earlier printer evidence preserved

Source e7e09fe: explicit probe output collisions return 2 before observation;
prior bytes and incomplete reservations retained, concurrent collectors observe
only once. Default inventory/all application services unchanged. **41 focused
PASS**, final **1188 run/1184 PASS/4 optional SKIP**, zero failure/error.
CI 40959449442 all three jobs SUCCESS; ten collector methods Windows/Linux.
Whole UX-07 purchased-print payment/device gate NOT_RUN; matrix **59/0/9/1**,
audit IN_PROGRESS/AR-13 conditional. Actual device/provider/privacy/release gates
stay separate; Sandbox delivery OFF, queued OPS untouched.
[Exact commands/source/CI/hashes/next](qa/portrait-v2-sandbox/evidence/ux07-printer-evidence-preservation.json).

## 30 October — UX-07.g preserve previous probe reports

Explicit printer-probe CLI reserves output before any observation. Existing or
concurrent output returns 2 without probe/overwrite; failed write keeps incomplete
reservation. Default inventory and all application services unchanged.
41 focused PASS/zero skip; three new causal methods, full/current CI pending.
Whole UX-07 NOT_RUN; matrix 59/0/9/1.
[Contract/evidence/next](qa/portrait-v2-sandbox/UX07-PRINTER-DEVICE-EVIDENCE.md).

## 29 October — UX-07.f read-only device evidence preparation verified

Collector source `45b0b30`, corrected test source `b6c3d01`: **49 focused PASS**;
final full **1185 run/1181 PASS/4 optional SKIP**, zero FAIL/ERROR.
CI **40896422532 all three jobs SUCCESS**; seven collector methods individually
PASS Windows/Linux, four original ad-player methods PASS Linux. Windows
**130/72/55/103 PASS**; Linux Sandbox **431 PASS**, native **116 PASS/1 SKIP**.
Initial full's one ad-fixture ERROR is retained; causal wait correction keeps
all assertions, requires real exposure and fails its held-tick negative control.
Ad GUI/runtime unchanged. [Exact evidence/history](qa/portrait-v2-sandbox/evidence/ux07-printer-device-evidence.json).

Use existing `check_portrait_v2.py --probe-printer` only in ordinary diagnostic
context to collect status-only redacted route evidence; default no printer
probe, dedicated Sandbox refused. [Device commands](qa/portrait-v2-sandbox/UX07-PRINTER-DEVICE-EVIDENCE.md). Route readiness
is not paper proof; Windows spooler API latency remains unbounded. Actual printer
observations/purchased-print prepayment integration still **NOT_RUN**; whole
UX-07 and matrix **59/0/9/1** unchanged. Sandbox printer/Drive OFF; provider,
privacy/operations/retention/release gates remain separate.

## 29 October — UX-07.f device evidence collector focused-verified

Base/remote `c8f0483`. Existing P5 inventory/CLI gains explicit `--probe-printer`:
default no probe; dedicated Sandbox refuses before settings/probe; ordinary
context reuses original settings/health service and exports only allowlisted
status/fixed notes. No print bytes, new order, payment/Drive call or financial/
media mutation; no automatic GUI/prepayment mounting. Route READY never proves
paper or purchased-print acceptance; Windows spooler API remains unbounded.
**45 focused PASS / zero failure/error/skip**, Python 3.12.14/Debian 13, 0.262s.
Seven new causal tests registered Windows/Linux, with actual method annotation
checking on Linux. Full/current CI PENDING after this source micro-push; next
one final full at its exact SHA, verify CI method receipts, then checkpoint.
[Contract/device commands/source evidence](qa/portrait-v2-sandbox/UX07-PRINTER-DEVICE-EVIDENCE.md).
UX-07 whole gate NOT_RUN; matrix **59/0/9/1** unchanged. All actual hardware/
merchant/paper/Drive/deletion/privacy/release gates remain separate. Only private
work/ scratch local; rollback source/tests/docs only, preserve every record.

## 29 October — UX-07 MOCK component final validation verified

CI source `8d0b9bb`, run **40887868676: all three jobs SUCCESS**. Five readiness/
seven MOCK methods individually PASS Windows/Linux; both new native lifecycle
methods individually PASS Linux at both portrait sizes, verified via annotations.
Linux Sandbox **424 PASS**, native **112 PASS/one SKIP**; Windows groups
**123/72/55/103 PASS**. Application/tools/tests unchanged from `3a98ed9`:
fresh **67 + 12 focused PASS**; full **1178 run / 1174 PASS / zero FAIL/ERROR /
four optional SKIP**. Four native error/held-retry images visually PASS; no
clipping/private data/order/QR before readiness. [Exact evidence](qa/portrait-v2-sandbox/evidence/ux07-mock-printer-final-validation.json).

Whole purchased-printer UX-07 **NOT_RUN**; matrix **59/0/9/1** unchanged. Next:
purchased payment/preflight integration and actual Windows/Ubuntu printer/device
evidence; keep Sandbox printer/Drive OFF. Queue/route is not paper readiness;
Windows spooler API latency is not bounded here. PAY-22/WEB-01–08 and actual
merchant/paper/phone/Drive/deletion/privacy/support/release acceptance remain
separate. No runtime/tests or financial/media records changed.

## 29 October — UX-07 final local validation / CI reporting pending

Source `3a98ed9`, runtime `2f598fd` unchanged: fresh **67 + 12 focused PASS**;
full **1178 run / 1174 PASS / zero FAIL/ERROR / four optional SKIP**, 594.860s,
Python 3.12.14/Debian 13 software GL. Four error/held-retry native FBO images
visually PASS at 800x1280/452x900; no private data/order/QR before readiness.
CI 40882031887 three jobs SUCCESS; Windows 123 PASS includes seven MOCK/five
readiness methods, other Windows groups 72/55/103 PASS. Linux native individual
method output inaccessible (blob-host proxy 403), not counted as verified PASS.
New CI-only report checker requires exact 5 readiness/7 MOCK/2 native PASS lines,
emits source/digest/method notices; local actual/missing/skipped/failed controls
PASS. Matching new CI PENDING; next verify notices and checkpoint remote SHA.
[Exact commands/source/counts/image hashes/limits](qa/portrait-v2-sandbox/evidence/ux07-mock-printer-final-validation.json).

Whole UX-07 purchased-printer payment/device gate **NOT_RUN**, matrix **59/0/9/1**.
Sandbox printer/Drive OFF; Windows spooler API latency unbounded by this adapter,
no paper guarantee. PAY-22/WEB-01–08 and all actual hardware/merchant/privacy/
release gates remain separate. No runtime/tests or customer records changed.
Rollback workflow/docs only; no unpublished runtime patch. Private work/ only.

## 29 October — UX-07.d actual MOCK factory/native probe verified

67 focused PASS/zero skip; real configured app worker at both portrait sizes,
Clock progress, duplicate/retired input fences, generic error/one fresh retry
and original-order recovery verified. Runtime remains 2f598fd; full/current CI
pending. UX-07 whole purchased-print gate NOT_RUN, matrix 59/0/9/1 unchanged.
[Exact evidence/limits/next](qa/portrait-v2-sandbox/UX07-MOCK-PRINTER-PREFLIGHT.md).

## 29 October — UX-07.c nonpayable MOCK printer preflight

53 focused PASS/zero skip; seven causal methods. Configured MOCK uses original
read-only printer/config on its worker before a new opt-in print simulation.
Failures deny order/QR; active identity recovers, retry reads fresh settings.
Native/full/current CI pending. Dedicated Sandbox printer/Drive OFF; UX-07 whole
purchased-print gate NOT_RUN, matrix 59/0/9/1 unchanged.
[Contract/evidence/next](qa/portrait-v2-sandbox/UX07-MOCK-PRINTER-PREFLIGHT.md).

## 29 October — UX-11 synthetic PASS / remaining external gates

Test source `7ca46b5`, **9 focused PASS / zero skip**; CI 40865822670 all three
jobs SUCCESS. Real held process on Windows/Linux; native stalled checkout/QR/
upload Clock/privacy/no-replay on Linux. Windows owned-lease fixture failure at
07734b2 preserved with controlled reproduction/correction. No runtime change;
old full 347e502 1159/1155/4 excludes ten new methods, separately verified.
Matrix **59 PASS / 0 FAIL / 9 BLOCKED / 1 NOT_RUN**, audit IN_PROGRESS.
UX-07 whole purchased-printer gate remains NOT_RUN; provider/webhook/device/
operations/release gates stay separate. No production or Sandbox delivery enabled.
[Exact evidence/next work](qa/portrait-v2-sandbox/evidence/ux11-final-verification.json).

## 29 October — UX-11 stalled worker evidence focused-verified

9 focused PASS, zero skip. Actual blocked-main/worker process remains held
without restart/paid mutation; native checkout/QR/upload stalls leave Kivy Clock
responsive, late results private, original upload files delivered once. No
runtime change; matching CI pending. UX-11 NOT_RUN pending final verification,
UX-07 stronger printer gate remains open; matrix 58/0/9/2.
[Contract/results/limits](qa/portrait-v2-sandbox/UX11-FROZEN-WORKERS.md).

## 29 October — UX-07 Sandbox components verified

Test source `685b994`, **36 focused PASS / zero skip**; CI 40862328219 all three
jobs SUCCESS. Five boundary methods on Windows/Linux; native error/no-QR/retry
method at both portrait sizes on Linux. Runtime unchanged at 347e502; old full
1159/1155/4 retains provenance and excludes new methods. Complete purchased-
printer gate remains NOT_RUN; preserve transport-off Sandbox. Matrix 58/0/9/2,
audit IN_PROGRESS. Next independent UX-11 frozen-worker/GUI evidence audit.
[Exact evidence/remaining limits](qa/portrait-v2-sandbox/evidence/ux07-final-verification.json).

## 29 October — UX-07.b native error/retry verified

36 focused PASS/zero skip. Five boundary methods plus one native method:
eight failures/eight retries at both portrait sizes; QUOTE/message/redaction/
no QR/order and exactly-one healthy retry verified. No runtime change; current
CI pending. UX-07 stronger purchased-printer gate NOT_RUN, matrix 58/0/9/2.
[Evidence/limits/next](qa/portrait-v2-sandbox/UX07-PREPAYMENT-READINESS.md).

## 29 October — UX-07.a Sandbox readiness boundaries verified

34 focused PASS/zero skip, five new integration methods: no charge/order before
readiness, probe cleanup, safe retry and existing identity preserved. No runtime
change; Linux/Windows CI registered/pending. UX-07 stronger purchased-printer
gate NOT_RUN, matrix 58/0/9/2 unchanged. Native message/retry evidence next.
[Contract/results/limits](qa/portrait-v2-sandbox/UX07-PREPAYMENT-READINESS.md).

## 29 October — UX-05 verified / BUG-024 fixed in source

Source `347e502`, 52 focused PASS; full 1159/1155/4, zero failure/error.
CI 40856740113 all three jobs SUCCESS, six UX-05 methods PASS on Windows/Linux.
Unknown cancellation stays held; fresh confirmed unpaid cancellation archives
before new visitor; write failure holds. Late paid/typed isolation/ACK/archive/
return preserves original rights. UX-05 synthetic PASS; BUG-024 regression
verified, actual device acceptance NOT_RUN. Matrix **58/0/9/2**, audit IN_PROGRESS.
Next UX-07 readiness/printer scope audit, preserve Sandbox transport-off.
[Exact evidence/limits](qa/portrait-v2-sandbox/evidence/ux05-final-verification.json).

## 29 October — UX-05.b confirmed cancellation recovery

BUG-024 reproduced: confirmed cancellation held CANCELLING after restart.
Controller now archives/commits unpaid terminal cancellation before new visitor;
write failure/cached evidence/paid rights hold. Six UX-05 scenarios; **52 focused
PASS**, full/CI pending. UX-05 NOT_RUN pending final, matrix 57/0/9/3.
[Contract/results/limits](qa/portrait-v2-sandbox/UX05-AMBIGUOUS-ABANDONMENT.md).

## 29 October — UX-05.a uncertainty holds verified

33 focused PASS, zero skip; two new HTTP/controller abandonment/restart cases
preserve original identity/OWED/private proof, deny replacement under 404/outage.
No runtime change. Linux/Windows CI registered/pending; UX-05 NOT_RUN until
terminal/paid-release continuation checks. Matrix 57/0/9/3 unchanged.
[Contract/evidence/next](qa/portrait-v2-sandbox/UX05-AMBIGUOUS-ABANDONMENT.md).

## 29 October — BUG-023 fixed in source / regression verified

Source `3822bb0`, 73 focused PASS; full 1153/1149/4, zero failure/error.
CI 40852458558 all three jobs SUCCESS; four new conflict methods PASS on
Windows/Linux. Recovery-only replay/cross-order denials durably redacted;
SQL failure holds, successful replay idempotent. UX-13 synthetic PASS; matrix
**57 PASS / 0 FAIL / 9 BLOCKED / 3 NOT_RUN**, overall audit IN_PROGRESS.
Actual device acceptance NOT_RUN; no production release. Next UX-05 contract/
source audit, then remaining UX-07/11/external gates.
[Exact evidence/limits](qa/portrait-v2-sandbox/evidence/bug023-conflict-http-verification.json).

## 29 October — BUG-023.d conflict audit focused-verified

Recovery-only 404/409 denials audited with static NOT_OWNED/ACTION_CONFLICT;
SQL failure holds with generic 503, exact successful replay remains idempotent.
73 focused PASS, full/current CI pending. BUG-023 OPEN/UX-13 FAIL pending final
verification; matrix 56/1/9/3 unchanged.
[Contract/results/next](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## 29 October — BUG-023.c PIN audit verified

Source `e6aba5a`, 69 focused PASS; full 1149/1145/4, zero failure/error.
CI 40850382603 all three jobs SUCCESS, journal and HTTP tests on Windows/Linux.
Wrong-PIN and operator 429 now durably audited on all three Sandbox routes;
audit failure denies with generic 503. Replay/cross-order denial audit remains
pending: BUG-023 OPEN/UX-13 FAIL, matrix 56/1/9/3.
[Exact evidence/next step](qa/portrait-v2-sandbox/evidence/bug023-pin-http-verification.json).

## 29 October — BUG-023.c PIN denials integrated

All three Sandbox endpoints audit wrong PIN/429, generic 503 on audit failure.
69 focused PASS; full/current CI pending. Windows now registers journal and
HTTP tests. Replay/cross-order audit pending; BUG-023 OPEN/UX-13 FAIL.
[Contract/evidence/next](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## 29 October — BUG-023.a foundation verified

Source `ab6fbbb`, 45 focused PASS; full 1145/1068/77, followed by 75 GUI/audio
opt-in run/73 PASS/two SKIP (three model and one video skip remain overall). CI 40843692911 all three jobs
SUCCESS; new journal methods PASS on Linux, Windows registration next.
Dormant only: HTTP not integrated, BUG-023 OPEN/UX-13 FAIL, matrix 56/1/9/3.
[Evidence/next step](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## 29 October — BUG-023.a denial journal foundation

Dormant additive bounded redacted journal, no HTTP integration yet. Five new
tests; **45 focused PASS**, zero failure/error/skip. Full/CI pending. BUG-023
OPEN/UX-13 FAIL; matrix 56/1/9/3 unchanged.
[Contract/results/next step](qa/portrait-v2-sandbox/BUG023-DENIAL-AUDIT.md).

## 29 October — CAP-20 verified

Storage source `9f3568b`, corrected native fixture `da3f444`, both pushed/remote
verified. **57 storage focused PASS**, 74 injected faults/48 actual children.
**CI 40842036384 all three jobs SUCCESS**: Windows payment/recovery 72 PASS,
Linux Sandbox/recovery 389 PASS, native 111/110/one optional palm SKIP. All six
CAP-20 methods PASS on Windows/Linux. Initial CI 40839833482 native failure
preserved; corrected test-only Clock isolation retains pixel/flip assertions,
111 focused/110 PASS/one optional SKIP and two effective mutation controls.
Runtime unchanged. Matrix **56 PASS / 1 FAIL / 9 BLOCKED / 3 NOT_RUN**;
audit IN_PROGRESS, BUG-023/UX-13 OPEN/FAIL, external/OPS gates remain.
Next **AR-09 bounded redacted durable denial audit**. [Exact evidence/limits](qa/portrait-v2-sandbox/evidence/cap20-final-verification.json).

## 29 October — CAP-20 native CI fixture correction

Storage source `9f3568b` CI 40839833482: Windows/pure SUCCESS, Linux native
same-packet flip FAIL (`8 != 7`); recovery group 389 PASS. Reproduced unrelated
Clock interference; test-only isolation preserves pixel/flip checks and rejects
new scheduled work. Both negative controls detect mutations. **111 native focused
run / 110 PASS / one optional palm SKIP**, zero failure/error, 138.089s.
57 storage PASS/74 faults/48 children unchanged at 9f3568b. Runtime unchanged;
corrected-fixture CI pending. Matrix 56/1/9/3, BUG-023/external gates OPEN.
Next current CI/final checkpoint, then AR-09. [Evidence/limits](qa/portrait-v2-sandbox/evidence/cap20-native-fixture-verification.json).

## 29 October — CAP-20 storage matrix focused-complete

**57 focused PASS / zero failure/error/skip**, 74 fault cases: 48 real child
exits plus 26 issue/atomic-writer cases. JPEG/retake/PNG/initial-manifest and
reporting rights preserve original ACKs/bytes/quota/OWED or hold safely.
No runtime change. Matrix **56 PASS / 1 FAIL / 9 BLOCKED / 3 NOT_RUN**.
First JPEG-only CI 40838609747 SUCCESS; current matching CI pending.
Next final CI/checkpoint then AR-09 BUG-023. [Evidence/limits](qa/portrait-v2-sandbox/CAP20-STORAGE-FAULTS.md).

## 29 October — CAP-20 JPEG write faults focused-verified

**52 focused PASS / zero failure/error/skip**, 14 child exits covering ENOSPC/
EACCES at seven JPEG write boundaries. No false capture ACK, original paid
OWED/issue/bytes preserved, proved bytes recover once; unknown bytes held.
CAP-20 remains NOT_RUN pending retake/PNG/initial/reporting faults; matrix
55/1/9/4. Tests/CI/docs only; matching CI pending. [Evidence/limits](qa/portrait-v2-sandbox/CAP20-STORAGE-FAULTS.md).

## 29 October — CAP-16 verified

Tests/CI `1ef7d29454a926d6eccc7cb2ba15162fbfbfa0c8` pushed/remote verified.
**74 focused PASS**, zero failure/error/skip; four new CAP-16 children/two
pre-COMPLETE boundaries. CI **40834950593 all three jobs SUCCESS**, all three
CAP-16 methods PASS on Windows/Linux (groups 66/383 PASS, zero skip); native
one optional palm SKIP. Original result/ACK/retention/OWED preserved; outage,
refund/corrupt PNG deny false completion. Tests/docs only, runtime unchanged.
Matrix **55 PASS / 1 FAIL / 9 BLOCKED / 4 NOT_RUN**, audit IN_PROGRESS/BUG-023 OPEN.
Next **CAP-20**, then AR-09; real device/provider/OPS/release gates unchanged.
[Exact evidence/limits](qa/portrait-v2-sandbox/evidence/cap16-final-verification.json).

## 29 October — CAP-16 composition/intent exits focused-verified

**72 focused PASS / zero failure/error/skip**, two new real child exits after
final composition and saved COMPLETING before COMPLETE request. Original result,
proof/ACK/binding/retention/OWED preserved. Tests/docs only; runtime unchanged.
Matrix **55 PASS / 1 FAIL / 9 BLOCKED / 4 NOT_RUN**. CI pending; next provider/
media denial cases, then CAP-20/AR-09. [Evidence/limits](qa/portrait-v2-sandbox/CAP16-COMPOSITION-COMPLETE.md).

## 29 October — CAP-11–13 verified

Test/CI `423d9d2c9096ec897521df565f2c59572057efd5` pushed/remote verified.
**80 focused PASS**, zero failure/error/skip; seven real child exits/six retake
boundaries. CI **40831396874 all three jobs SUCCESS**; all five retake methods
PASS on Windows/Linux (groups 63/380 PASS, zero skip); native one optional palm
SKIP. Tests/CI/docs only, runtime unchanged. Matrix **54 PASS / 1 FAIL / 9 BLOCKED /
5 NOT_RUN**, audit IN_PROGRESS/BUG-023 OPEN. Next **CAP-16**, then CAP-20/AR-09;
external/OPS/production gates unchanged. [Exact evidence/limits](qa/portrait-v2-sandbox/evidence/cap11-13-final-verification.json).

## 29 October — CAP-11 focused evidence

**76 focused PASS / zero failure/error/skip**, two actual retake process exits;
original selection/quota/paid binding/bytes/OWED preserved. Tests/CI/docs only,
no runtime change. Matrix **52 PASS / 1 FAIL / 9 BLOCKED / 7 NOT_RUN**.
CI pending at this containing test commit. Next CAP-12–13, BUG-023/external/OPS
gates unchanged. [Evidence and limits](qa/portrait-v2-sandbox/CAP11-13-RETAKE-CRASHES.md).

## 29 October — PAY-18 verified; next CAP-11–13

Tests/CI source `74155c13787fc608304a6214eb374a20e424ebdd` and first micro-push
`3ad80da74da2a0fc3c9d5e3dbe3d84f91a483f4a` pushed/remote-verified.
**86 focused PASS / zero failure/error/skip**, 22.532s; three methods execute
23 actual child exits at seven claim/STARTED/COMPLETED/archive boundaries.
[CI 40818696969](https://github.com/pratikto/PhotoBooth/actions/runs/40818696969)
**all three jobs SUCCESS**: Windows payment/recovery 58 PASS/zero skip, Linux
protocol/recovery 375 PASS/zero skip; native 111 run/110 PASS/one optional palm
SKIP. First CI 40818395624 superseded/CANCELLED, not standalone PASS.
[Exact source/commands/limits](qa/portrait-v2-sandbox/evidence/pay18-final-verification.json).

No runtime defect/application/schema/UI change. Original paid identities, proof,
OWED, copies and result bytes survive with no repeated charge/capture/render/
print/upload. Final archive interruption remains active/private until durable
history/index/journal. Prior full e0dc594 (1117/1114/3) and native c94696d
(28 PNG/four QR) retain original source; no new local full/native run
or physical acceptance is claimed.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**, BUG-023 OPEN/audit IN_PROGRESS.
Next **CAP-11–13 retake child exits**, then CAP-16 pre-request, CAP-20 and AR-09
redacted denial audit. External/OPS/production gates unchanged; work/ scratch only,
no unpublished runtime patch. This docs-only publication is the final safe
checkpoint; resolve its exact SHA from Git/remote, then continue unfinished work.

## 29 October — AR-03.d2 completion/archive process exits

Previous micro-push `3ad80da74da2a0fc3c9d5e3dbe3d84f91a483f4a` remote verified.
**86 focused PASS / zero failure/error/skip**, 22.532s; three PAY-18 methods,
23 real child exits at seven distinct boundaries. New archive exits hold local
COMPLETING after accepted ACK, operation history and lookup index; no new visit
or archive bypass before original proof and durable final journal. Original
three JPEGs/one PNG/manifest/copies/OWED remain unchanged, no repeated effects.
[Command/source/limits](qa/portrait-v2-sandbox/PAY18-SERVICE-REPLIES.md).

Tests only; no runtime defect/application/schema/UI change. Matching CI pending
at this containing commit; first run 40818395624 still running at publication.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**, BUG-023 OPEN/audit IN_PROGRESS.
Next: matching CI/final checkpoint, then **CAP-11–13 retake child exits**;
CAP-16 pre-request, CAP-20 and AR-09 denial audit follow. Prior full/native stay
at e0dc594/c94696d; no new full/native/device/provider/production/OPS acceptance.
Only disposable work/ local, no unpublished runtime patch. Scoped inverse of
new tests/docs retains every customer record; containing SHA resolved after push.

## 29 October — AR-03.d1 PAY-18 combined lost replies

Base/remote verified `03189012b5f4c6204ef4f8718bb218a1baac32d5`.
**85 focused PASS / zero failure/error/skip**, 12.257s. Two new methods run
**eight actual child exits at four boundaries**: original booth claim, customer
claim, STARTED and COMPLETED committed before local acknowledgment. Same
order/grant/claim operation/allocation/transaction/result; one provider charge,
three synthetic JPEGs/one composition, original OWED and private proof preserved.
Outage HTTP 503/refund HTTP 409 deny cached-PAID recovery; existing bytes remain.
[Contract/commands/provenance](qa/portrait-v2-sandbox/PAY18-SERVICE-REPLIES.md).

Tests/CI/docs only; no runtime defect or application/schema/UI change. Current
CI pending at this containing test commit. Prior full e0dc594 (1117/1114/3) and
native c94696d (28 PNG/four QR) retain original source; no new full/native result.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**; PAY-18 synthetic PASS,
BUG-023 OPEN, overall audit IN_PROGRESS. Next AR-03.d2 completion/archive exits,
then CAP-11–13, CAP-16 pre-request boundary, CAP-20 and AR-09 denial audit.
External/OPS/production gates unchanged; only disposable work/ local, no
unpublished runtime patch. This containing commit is the next micro-push;
resolve its SHA from Git, push and verify remote before continuing.

## 29 October — AR-03.c CAP-01–05 verified checkpoint

Test/CI `e72e28bdf8b0cbb080ef0c35aa8a1e3906bf55cb` pushed/remote-verified; first micro-push
`c87050eeb4f0223577d68796ff0ace4f4a1d2a95`. **66 focused PASS / zero failure/error/skip**,
5.965s; seven real child exits at six allocation/folder/manifest/STARTED boundaries,
including orphan/no-recency hold. [CI 40815197373](https://github.com/pratikto/PhotoBooth/actions/runs/40815197373)
**all three jobs SUCCESS**, Windows payment/allocation group 55 PASS/zero skip.
Original proof/paid identities/counter/manifest/OWED retained; no repeated effects.
[Exact commands/source/evidence](qa/portrait-v2-sandbox/evidence/cap01-05-final-verification.json).

Tests/CI/docs only; no runtime defect, application/schema/UI change or new full/
native run. Prior full e0dc594 (1117/1114/3) and native c94696d (28/four) remain
separately pinned; the six new methods are verified by focused/CI results.
Matrix **50 PASS / 1 FAIL / 9 BLOCKED / 9 NOT_RUN**; overall audit IN_PROGRESS,
BUG-023 OPEN. Next **PAY-18 combined lost service replies including COMPLETED**,
then remaining retake/COMPLETE/disk and AR-09 denial audit. External/OPS/production
boundaries unchanged; only disposable work/ local, no unpublished runtime patch.
This containing docs commit publishes the final safe continuation checkpoint.


## 29 October — AR-03.c CAP-01–05 exact process-exit evidence

**66 focused PASS**, zero failure/error/skip; seven actual child exits across six
allocation/folder/manifest/STARTED boundaries, original proof/identities and orphan
hold verified. Tests/CI/docs only, no runtime defect or behavior change. Matrix
**50 PASS / 1 FAIL / 9 BLOCKED / 9 NOT_RUN**; matching CI pending at this commit.
[Exact source/commands/limits](qa/portrait-v2-sandbox/CAP01-05-ALLOCATION-CRASHES.md).
Prior full/native evidence retains its actual source; BUG-023/external gates OPEN.


## 29 October — AR-02.d PAY-08 verified and remotely checkpointed

Functional `e0dc59435772148be86449c55140d4b9be2f6364`: **1117 run / 1114 PASS /
3 optional palm SKIP / zero failure/error**, 335.317s; native video PASS.
Reader micro-push `52a9a18857580ddcc822fe77cd36af76d489a532`; mounted source e0dc594;
Windows test/setup correction `c94696d243c6a345182857d28d249d2d01d7d05b`, **49 focused PASS**.
[CI 40809459547](https://github.com/pratikto/PhotoBooth/actions/runs/40809459547)
at c94696d **all three jobs SUCCESS**; same application/tools tree as full-run
source, test delta only explicit lease cleanup (full not relabeled). Integration
103 focused PASS; native **28 PNGs / four QR checks PASS**, both portrait sizes,
clean c94696d. Initial Windows qrcode import failure retained in provenance.
[Exact command/source/evidence](qa/portrait-v2-sandbox/evidence/pay08-final-verification.json).

PAY-08 synthetic PASS / AR-AUDIT-002 resolved; matrix **45 PASS / 1 FAIL /
9 BLOCKED / 14 NOT_RUN**, overall audit IN_PROGRESS, **BUG-023 OPEN**.
Next **AR-03 CAP-01–05 exact allocation/STARTED process exits**, PAY-18 lost ACKs,
then remaining media/COMPLETE/disk cases and AR-09 redacted denial audit.
Real OS/device/provider/privacy/retention/operational acceptance stays separate;
no production/OPS/print/Drive activation. Only work/ scratch local; no unpublished
runtime patch. This containing docs checkpoint follows remote-verified c94696d.


## 29 October — AR-02.d PAY-08 focused verification

Passive OS restoration is connected to the native checkout worker: same-order
GET only, existing durable retry/lease and privacy guards preserved. **103
focused PASS**, zero failure/error/skip; final full/CI pending at this functional
publication. Matrix **45 PASS / 1 FAIL / 9 BLOCKED / 14 NOT_RUN**; BUG-023 OPEN.
[Contract/evidence/limits](qa/portrait-v2-sandbox/PAY08-CONNECTIVITY.md).
Next: final verification, then AR-03 CAP-01–05 exact allocation/STARTED crashes.
Actual devices/provider and queued OPS remain unverified/NOT_STARTED.


## 29 October — verified AR audit checkpoint at 4642841

**Functional `4642841f3e99d8c74b4b379e24922a7ba3f614c9`**, pushed/remote-verified. Full
**1,100 run / 1,097 PASS / 3 optional palm SKIP / zero failure/error**, 364.124s;
native video PASS, GUI/audio/video opt-ins, Python 3.12.14/Debian 13.6/offscreen/
dummy audio. Matching [CI 40790865010](https://github.com/pratikto/PhotoBooth/actions/runs/40790865010)
**all three jobs SUCCESS**, including Windows payment/reconstruction cases.
[Exact command/source/digests](qa/portrait-v2-sandbox/evidence/ar-audit-final-verification.json).
Payment micro-push 8ebcd12: 116 focused PASS; BUG-022 fix 4642841: 61 focused PASS;
source audit/docs 5d318f8 pinned. No new local native/physical evidence inferred.

BUG-022 fixed/verified; **BUG-023 OPEN**, no durable wrong-PIN denial audit (UX-13
FAIL), and native connectivity-restored producer absent (PAY-08 NOT_RUN).
Matrix **44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN**. First source pass read;
overall audit **IN_PROGRESS**, no blanket conformity/unattended release verdict.
Next: AR-02 bounded native connectivity event/fixture, AR-03 exact allocation/
STARTED faults, remaining service/media cases, AR-09 redacted denial audit.
External gates/OPS NOT_STARTED unchanged. Current containing docs publication
pins the safe handover; only disposable work/ local, no unpublished runtime patch.


## 29 October — AR source audit first pass and corrected denial verdict

Functional `4642841f3e99d8c74b4b379e24922a7ba3f614c9` pushed and remote HEAD verified. Payment
8ebcd12: 116 focused PASS; BUG-022 correction: 61 focused PASS. Bounded source
pass now covers AR-00–13. **BUG-023 OPEN**: wrong-PIN requests are rejected/rate-
limited but lack durable denial audit; UX-13 corrected from PASS to **FAIL**.
Operator rate budget is process-local, customer ticket budget separately durable.
Native connectivity-restored producer is absent (AR-AUDIT-002/PAY-08 NOT_RUN).
Current matrix **44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN**; no blanket conformity
verdict. [Findings/probe](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md#increment-4--nativeoperational-source-pass-and-remaining-findings).

Full regression at 4642841 running; CI 40790865010 pure/Windows SUCCESS, desktop
still running. Superseded 40790391324 CANCELLED by concurrency. Finish both and
pin actual results, then dependency-ordered PAY-08/CAP-01–05 fault evidence and
AR-09 denial audit. External/device/production gates unchanged, OPS NOT_STARTED.
This containing docs checkpoint preserves exact source/findings; only disposable
work/ diagnostics local, no unpublished runtime patch.


## 29 October — AR audit BUG-022: hold missing committed output before restore

Payment audit `8ebcd123098fe5a937c59f2b88d7fe60c9bedf7b` pushed/remote-verified,
116 focused PASS; PAY-06/PAY-21 closed as synthetic evidence gaps. Matrix now
45 PASS / 9 BLOCKED / 15 NOT_RUN. Subsequent source review confirmed **BUG-022**:
missing COMMITTED PNG was accepted by inspection; restore installed state before
FileNotFoundError. Corrected validation holds before installation, preserves
originals/manifest/OWED and performs no rerender/print or payment mutation.
New test first reproduced 2 FAIL/1 ERROR in a 14-case run; **61 focused PASS**
after correction, zero failures/errors/skips (39.146s). This containing commit
is the functional correction; final full regression and matching CI PENDING.
[Review and exact evidence](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md#increment-3--confirmed-missing-output-reconstruction-defect-bug-022).
Audit IN_PROGRESS; no production/OPS/deployment. Previous f72fdbc full/native
results remain historical. Next: full regression at pushed correction and remaining
native/privacy/operator/launcher review, then exact remaining matrix faults.
Only disposable `work/` local; no unpushed runtime patch after publication.


## 29 October — final AR-12 source evidence and AR-13 readiness

Final runtime/test `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`: **1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors**, 428.924s, Python 3.12.14 / Debian 13.6,
GUI/audio opt-ins with offscreen software GL/dummy audio, tracked tree clean.
[CI 40767441201](https://github.com/pratikto/PhotoBooth/actions/runs/40767441201):
all three jobs SUCCESS at matching source. Native 28 PNGs/both portrait sizes,
four QR checks PASS; payloads private. Previous-session 1094/1091/3 log unavailable;
this is a new independently captured result. Matrix 43 PASS / 0 FAIL / 0 SKIP /
9 BLOCKED / 17 NOT_RUN; exact missing fault windows are not credited as PASS.

[AR-13 assessment](qa/portrait-v2-sandbox/AR13-READINESS.md): **CONDITIONAL** for
controlled acceptance; **NOT READY for unattended commercial release**. Device,
merchant, phone/paper/Drive/deletion, privacy/remedy/operations and owner approval
remain open. First unfinished source-evidence task: PAY-06 abrupt exit between
provider evidence and DB commit, then remaining matrix gaps. AR stays top priority;
all future Settings/Emulate Ticket/QRIS Slip implementation stays NOT_STARTED.
[Exact command/skips/provenance](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md) ·
[checkpoint/next action](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 29 October — AR-12.d: retain Windows pass and expose Linux isolated-photo failure details

CI 40756011109 Windows autonomous/native and pure jobs PASS; desktop P3 group FAIL with unknown cause. Failure-only report annotation added, no assertions/application changes. Final local full rerun still running. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-12.c: correct Windows PNG fsync and verify real output crash boundaries

First full local run 1093 run/1090 PASS/3 optional palm SKIP; Windows CI revealed read-only fsync Errno 9. Fixed non-truncating writable descriptor, added four output child-exit boundaries, retained all assertions; focused outcome recorded in validation. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-12.b: expose Windows autonomous test failures without changing assertions

Pinned source 09788b1 native 28 PNG captures and four QR checks PASS; local full suite running. Initial Windows autonomous CI FAIL, underlying case unavailable because log-storage host is network-denied; diagnostic annotation added. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-12.a: close final archive binding and WAL fault gaps before full regression

Focused 57 PASS, then final durability/core 25 PASS, zero failures/errors/skips. Actual child os._exit, WAL integrity and locked writer checked; Windows recovery CI and release/return renderer extended. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-11: design public webhook boundary and verify unmounted durable inbox prototype

Focused 38 PASS, zero failures/errors/skips; no public listener, runtime mount, merchant callback, deployment or BI-SNAP migration. Infrastructure gates remain explicitly unapproved/NOT_RUN. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-WEBHOOK.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-10: bound opt-in exited-GUI recovery with durable budget and original leases

Focused 93 PASS, zero failures/errors/skips; no live-process kill or automatic business effect, three restarts/ten minutes only with isolated Sandbox and released leases. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-SUPERVISOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c5: mount deliberate isolated booth release and original customer return

Focused 47 PASS plus four isolation PASS, zero failures/errors/skips. Native two-step PIN release waits for local receipt and server ACK; original one-photo session returns without another charge; uncertain printing stays held. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c4: persist worker isolation and exact archived customer recovery

Focused 37 PASS, zero failures/errors/skips; real HTTP and synthetic photo release/new visit/return preserves original bytes, grant and capture count; lost ACK repeats persisted IDs. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c3: authenticate two-phase release and require current service fencing tokens

Focused 58 PASS, zero failures/errors/skips; operator HTTP release and reacquired current-token service covered. No native release control yet. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c2: preserve paid rights through two-phase occupancy release and exact reacquisition

Focused 48 PASS, zero failures/errors/skips; prepare/ACK/restart/replay and original proof/new-token/free-booth invariants covered. Core internal seam only, no release endpoint/UI yet. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c1: fence stale service workers before implementing safe booth release

Focused 86 PASS, zero failures/errors/skips; five migration/CAS/restart/race cases. Dormant internal seam only; no UI/API rotates fences and no booth release is enabled. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.b: mount PIN-protected native operator metadata inspection

Focused 64 PASS, zero failures/errors/skips; wrong/missing/correct PIN, private media denial, journal secrecy and retired callbacks covered. Twenty provisional native PNG fixtures rendered at both required sizes. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.a: isolate a per-launch Sandbox operator PIN from the GUI

Focused 64 PASS, zero failures/errors/skips; backend-only PIN and mocked launcher argv/environment/local-notice isolation covered. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-08.b2: record native postpaid faults with durable same-operation retries

Focused 58 PASS, zero failures/errors/skips; postpaid missing-camera, capture I/O failure and lost-ACK/restart fixtures preserve payment, OWED, manifest and one issue operation. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-08.b1: persist paid-unfulfilled issues without altering customer financial rights

Focused 56 PASS, zero failures/errors/skips; five new durable/concurrent/migration/authenticated HTTP issue cases; CI registration included. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-08.a: gate native new payment on camera storage and template readiness

Focused 57 PASS, zero failures/errors/skips; offline readiness and native no-camera/no-order gates covered; new module registered in CI. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b4: recover original pre-manifest allocation without creating another session

Focused 42 PASS, zero failures/errors/skips; original RESERVED empty allocation recovery and STARTED/orphan denial covered in photo and native HTTP fixtures. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b3: mount native ticket claim and customer-led exact photo recovery

Focused 46 PASS, zero failures/errors/skips; native HTTP-to-photo restore, cached-camera ticket decode, minimize/idle privacy and input-preserving polling covered. Sixteen provisional fixture PNGs rendered at both target sizes. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b2: hide private photo snapshots and fence reconstruction after lock

Focused 35 PASS, zero failures/errors/skips, including same-session reclaim and lock-during-reconstruction fixtures. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b1: revoke stale permits and acknowledge exact resumed service

Focused 37 PASS, zero failures/errors/skips; three added session cases cover privacy revocation, original STARTED acknowledgment/current refund and completed-result-only restore. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.a: native save-ticket gate and neutral privacy-held screen

Two new native gates and focused 37 PASS, zero failures/errors/skips. Twelve native working-tree captures rendered at 800x1280/452x900; both recovery-ticket screenshot QR payloads decode correctly without logging secrets. Payment URL/copy actions remain hidden until ticket acknowledgment. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-06.b: memory-only customer ticket and trusted claim controller

Six new session cases; focused 92 PASS, zero failures/errors/skips, including native Sandbox compatibility. Raw ticket never enters journal/backend views; restart requires original proof. Current settlement is rechecked at resume action, pending proof never issues media permission, and privacy generation rejects late callbacks. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-06.a: hashed customer capability and current-payment redemption

Eight new customer-proof cases and focused 137 PASS, zero failures/errors/skips. Additive capability binding is atomic with order; only SHA-256 persists. Expiry, durable attempt budget, one-use action replay and fresh settlement gate protect redemption without operator privilege bypass. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-05.b: exact private photo reconstruction behind one-use in-memory permit

Nine new reconstruction cases pass; focused 63 PASS plus nine final guard checks, zero failures/errors/skips. Restores partial shots, selected/used retake, staged captures/PNG and multi-design copies without new IDs, shutter, renderer or print. No old media is returned without a bound ephemeral permit; UI mounting remains disabled until AR-06/07. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-05.a: immutable strip publication with frozen input hashes

Three new output cases; focused 71 PASS, zero failures/errors/skips, including native handoff, capture, delivery and v1 retention/workflow. PNG intent and input identities persist before rendering; published-but-unacknowledged output cannot be overwritten on retry. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-04.a: write-ahead immutable JPEG capture and atomic retake quota

Seven new capture cases, five abrupt process boundaries, and focused 73 PASS, zero failures/errors/skips. V2 opts in; v1 writer defaults unchanged. Existing/orphan JPEGs cannot be overwritten; retake selection/quota commit with saved bytes. Native Sandbox and retention checks pass. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CAPTURE.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-03.b: unique allocation before local photo creation

Focused 204 PASS, zero failures/errors/skips, including native HTTP-to-photo handoff, allocation replay/restart, initial binding, v1 workflow and retention. Server atomically assigns one PB001V2AR-style transaction before any folder creation; exact initial manifest binds original payment/permit. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-03.a: frozen order contract and independent fulfillment obligation

Six new fixtures and focused 133 PASS, zero failures/errors/skips. New orders freeze server pricing/template hashes before I/O; payment creates an owed fulfillment independently of UI claims. Legacy duplicate bindings quarantine both mappings without altering original evidence. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-02.c: private restart observation and recovery worker retry

Focused 152 PASS, zero failures/errors/skips, including native Sandbox lifecycle. Four new restart tests and persisted priority-trigger test pass; RECOVERY retains original phase, grant and transaction and never resumes capture. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-02.b: durable bounded reconciliation scheduling and fencing

Focused 126 PASS, zero failures/errors/skips. Fifteen new AR-02 cases cover cached evidence, concurrent workers, jittered backoff, stale responses, additive schema and clock rollback. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-02.a: fresh payment observation and admission guard

Nine new cases; focused 120 PASS, zero failures/errors/skips. Backend-only provider GET observation requires booth authentication; operator mutation remains PIN-gated. Cached PAID cannot authorize claim/STARTED without fresh settlement. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-01 final source evidence

`017b417d02d63a79b1c5b21c4f0613b7d15186fc`: immutable attempt durability verified with
132 focused PASS and full **968 run / 965 PASS / 3 SKIP / zero failures/errors**. Matching CI
40688374416 all three jobs SUCCESS. This is AR-00/AR-01 source verification;
AR-02–13, autonomous private photo resume, actual devices/provider and production
remain pending. [Current checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 28 October — AR-01 creation durability (source, not unattended acceptance)

Backend persists immutable creation request scope/fingerprint and send ambiguity
in an additive table. Old rows remain held; timeout/404/restart cannot create a
replacement charge. Merchant/mode/request mismatches reject before provider I/O.
132 focused PASS; full/CI/device/merchant gates pending at publication.
No customer resume GUI is implemented. [AR-01 evidence](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md).

## 28 October — Autonomous Recovery baseline

AR-00 contract/fixtures verified offline: six new cases, 87 focused PASS, no
runtime/schema change. AR-01–13 remain pending; autonomous photo resume/customer
claim is not delivered. [Exact source contract and gaps](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-BASELINE.md)
and [continuation checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 28 October — Sandbox GUI copy link

IN SOURCE at `39e8c32`: **SALIN LINK QRIS** copies the verified active image
URL for the official web simulator, with success/failure feedback. Existing
payment and lifecycle guards remain. [Usage/checks/limits](qa/portrait-v2-sandbox/COPY-LINK.md).

## 28 October — BUG-021 pending QR polling

IN SOURCE: verified image URLs survive omitted status actions and backend
restart; explicit replacement validation and payment/expiry guards remain.
Source `4237d3f`: 182 focused PASS; full 933 run / 930 PASS / 3 optional palm
SKIP / zero failures/errors; CI 40614355442 all three jobs SUCCESS. Ten native
PNGs and both WAITING screenshot QR decodes verified. Exact device cause/retest
remains separate; [current evidence](qa/portrait-v2-sandbox/QR-POLLING.md).

## 28 October — centered Meong Sandbox QR

IN SOURCE: direct Drive-renderer/artwork reuse, exact provider-payload check,
original-image fallback, nearest filtering and per-order cache. 175 focused
checks PASS. Source `8ed6f11`: full 926 run / 923 PASS / 3 optional palm-assets
SKIP / zero failures/errors; matching CI 40610731638 all three jobs SUCCESS.
Fifteen native PNGs and three screenshot decodes are verified; actual merchant/
phone acceptance remains pending. [Evidence](qa/portrait-v2-sandbox/QR-LOGO.md).

## 28 October — saved Sandbox credentials

IN SOURCE: optional ignored local defaults remove repeated terminal entry;
static literal read, source-pair precedence, safe errors and backend-only
credential forwarding. Source `b496d9f` has 15 new-case PASS on Linux and Windows,
matching CI 40576392500 all three jobs SUCCESS. Results and local-executor limits
are tracked in the [current package](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).
Actual merchant authentication remains a separate acceptance check.

## 28 October — BUG-020 Sandbox key syntax

IN SOURCE: launcher accepts both dashboard Server Key formats; fixed Sandbox
host, redirect refusal and server-only secrets remain. 136 focused tests PASS;
full local source `6a271de` has 901 run / 898 PASS / 3 optional palm-assets SKIP /
zero failures/errors. CI 40572395949 all three jobs SUCCESS; actual merchant
acceptance remains pending. Exact evidence is tracked in the
[source-specific record](qa/portrait-v2-sandbox/KEY-FORMAT.md).

Matching-source CI **40481718367**: all three jobs SUCCESS.
Gallery fix **eb0297d**: final local **898 run / 895 PASS / 3 optional
palm-assets SKIP / zero failures/errors**, 291.903s; 20 targeted checks and
18 exact-source native captures (nine held-pointer frames). Actual device retest
remains pending. [Exact evidence/update](qa/portrait-v2-carousel-hold/README.md).


## 27 October — BUG-019 held gallery drag

Owner reports an empty incoming side while holding a carousel drag. Five pooled
Images existed, but two outer textures were cleared at rest. The existing widget
now retains a five-picture cached window through drag, reversal and release.
Native checks cover all 12 designs, both directions and five sizes, including
wraparound; selection/quantity and lifecycle guards remain. Device acceptance
is separate. [Scope, tests and update](qa/portrait-v2-carousel-hold/README.md).


Final customer-delivery source **311f3d8**: **896 local run / 893 PASS /
3 optional palm-assets SKIP / zero failures/errors**; 73 focused PASS,
14 exact-source native captures and eight exact right-panel QR decodes.
Matching-source CI **40472339778**, all three jobs SUCCESS.
[Exact evidence/update](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md#final-source-and-evidence).


## 27 October — customer upload priority and early folder QR

Latest owner instruction supersedes the earlier completion-only screen QR and
interleaved old-recovery policy. Customer uploads now run FIFO to completion;
old retries/reserves/content wait at request boundaries. Two short retry delays
(5s, 15s) precede release to bounded background retry after a third consecutive
failure. Verified assigned-folder QR can appear while bytes are pending, with
truthful upload/retry messaging and a 30-minute check-back suggestion, not an SLA.
Folder claims/manifest mapping survive restart; duplicate/replaced customer
folders are rejected. Code.gs and physical printing policy are unchanged.
[Current contract, evidence, update and limits](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).

Logging correction source **4c31406**: full local **888 run / 885 PASS /
3 optional palm-model SKIP / zero failures/errors**, 262.543s; real-Kivy
console-active integration, broken-sink worker survival and 11 delivery widget
checks PASS. Matching-source CI 40460799605: all three jobs SUCCESS.
[Update and exact evidence](qa/drive-delivery-performance/LOGGING.md).
The supplied RecursionError incident is distinct from the protected old-folder
conflict; exact on-device handler/exit traceback and post-update timing remain unverified.

## 27 October — delivery logging recursion recurrence

Owner reports >10 minutes and supplies RecursionError timing; new queued work
has no worker_start in the extract. Old-folder BIND_FOLDER_CONFLICT is confirmed
for one transaction. Real-Kivy console-active reproduction exposes root/stderr
logging recursion missed by earlier console-disabled QA. Timing now uses the
session file directly, contains sink failures/re-entry, and v2 defaults to MIXED
logging with native diagnostics retained. 54 targeted tests PASS; final checks
are recorded in the [correction runbook](qa/drive-delivery-performance/LOGGING.md).
Code.gs unchanged; no redeploy, reset or known-folder replacement is required.

Retry source **8578825**: complete local **884 run / 881 PASS / 3 optional
palm-assets SKIP / 0 failures/errors**, 268.095s. 67 focused service and
11 native delivery PASS. Matching-source CI 40455236898: all three jobs SUCCESS.
[Exact proof/update guide](qa/drive-delivery-performance/RETRY.md).
Functional source is unchanged in the final evidence publication; actual
Windows/Ubuntu/Google timing after this update still needs device evidence.

## 27 October — failed-delivery retry isolation

Owner timing identifies repeated old bind failures as 70.782s of a 122.719s
queued-to-QR session; exact ValueError cause/installed SHA remain unknown.
Healthy-first scheduling, one recovery/30s, persisted 30–300s backoff and safe
bind codes are implemented; known folder/transaction conflicts remain protected.
Focused service/native checks PASS; final regression/CI evidence is in the linked runbook.
Code.gs unchanged; no redeploy required. [Scope, evidence, updates and limits](qa/drive-delivery-performance/RETRY.md).

Final delivery source **2e140c1**: full local **877 run / 874 PASS / 3 optional
palm-assets SKIP / zero failures/errors**, 262.743s; 29 Code.gs VM PASS,
11 focused native delivery PASS. Matching-source CI **40448427344**, all three
jobs SUCCESS; 14 native FBO screenshots verified at both required sizes.
[Final evidence, update/manual deployment, timing export and limits](qa/drive-delivery-performance/README.md).
Runtime unchanged in the final evidence publication. No production Drive-speed,
Windows/Ubuntu hardware, cloud deployment or deletion acceptance is inferred.

## Delivery responsiveness

Owner-approved Drive/GUI improvement continues from fcabfbb. Background delivery
snapshots no longer lock result buttons/footer during rebuild. The strict
UPLOAD_COMPLETE QR contract and operator-disabled printing remain. Controlled
native regression PASS; actual five-minute delay is unmeasured.
[Scope, v1 comparison, evidence and rollback](qa/drive-delivery-performance/README.md).

**Final FEAT-009 source `f023029`:** matching-source CI 40423003641 succeeds in
all three jobs (Linux pure, Linux desktop, Windows). Post-fixture-correction local
rerun: 869 run, 866 PASS, 3 optional palm-assets SKIP, zero failures/errors,
272.035s. [Final evidence](qa/portrait-v2-recovery/README.md#final-verification--f023029).
This supersedes the older stage-1/initial Windows CI limits below. Actual
Windows/Ubuntu mini-PC hardware and service installation remain unverified.

**27 October current increment:** FEAT-009 stages 1–2 IN SOURCE: observer,
read-only local recovery review, guarded watchdog startup, per-checkout launcher
lease, Windows cmd and Ubuntu graphical-session service generation. Owner develops
on Windows and deploys to an Ubuntu mini PC; actual deployment/hardware pending.
Documentation-before-code / documentation-after-code is the primary rule.
Final local **869 run: 866 PASS, 3 optional model SKIP, 0 failures/errors**;
47 focused PASS, 16 API/Sandbox PASS, native launcher and systemd unit verification
PASS. No automatic restart, replay, service installation or commercial release.
[Stage-2 scope, reviewed sources and evidence](qa/portrait-v2-recovery/README.md).

**Historical stage-1 checkpoint (superseded by stage 2 above):**
optional external heartbeat observer and Windows startup generator. Automatic
restart/recovery and startup installation remain unimplemented. Device acceptance
is deferred by owner; no remote-source CI claim. [Current scope/evidence](qa/portrait-v2-watchdog/README.md).
Focused checks and native launcher lifecycle pass; complete regression remains
NOT VERIFIED because API/Sandbox fixtures stall (isolated Sandbox: six failures).

## Drive layout and QR source correction (26 October 2026)

Numbered Photo folders, flat raw/bw/color uploads and verified link-sharing acknowledgements are implemented in the repair source. Actual installed deployment, cloud upload and signed-out phone scan remain pending.

Updated **26 October 2026** after documentation baseline `f36ebad` on
`feature/portrait-kiosk-v2-next`. Latest functional source **53e7b4c** is the coordinated [storage integration](qa/feat-004-storage/README.md), after mirrored v2 **fc26e3d**, following BUG-009 diagnosis `887ba39`, tutorial entry `20453fe` and print/Drive `266b2c8`.
The earlier **`9433010` / `0dc6555`** pair is the P5 source/evidence baseline,
not the latest operator checkpoint. GitHub's default remains `master`.

IN SOURCE means implemented; VERIFIED AUTOMATED means a recorded source-specific
check passed; OWNER-REPORTED means a physical observation with the recorded
metadata limits; PENDING/NOT_RUN means acceptance has not been demonstrated.
None of these alone means production-certified or formally released.

**Owner flow refinement, 26 October:** idle no longer has a separate CARA PAKAI
button. Direct/invitation photo entry still requires the four-step tutorial for
a fresh visit, using the existing navigation/actions. [Current change and
validation](qa/portrait-v2-photo-entry/README.md).

**Latest owner retest, 25 October:** targeted R01–R04 **4/4 checked**, zero
unchecked and no issue notes. BUG-018 moves to **OWNER-REPORTED PASS / MONITORING**:
rapid/mixed clicks, close while busy, reopen/minimize and next input/restart are
reported working. Preserve the earlier contradictory raw 8/8/hang report.
Tested HEAD/device fields remain unknown; no exact-source verification, formal
closure or external P5 acceptance is inferred. No new runtime patch is needed.
[Reports and correction](qa/portrait-v2-health-clicks/README.md).

| Feature | Current GUI v2 source | Evidence and boundary |
| --- | --- | --- |
| Advertising/tutorial/twelve templates | Responsive media, inline invitation, tutorial once per visit via photo entry (no separate help button), swipe gallery, native captions and animated header | Source screenshots; final owner visual/audio 8/8 at unknown HEAD; later entry refinement has its own source checks |
| Camera/face/optional palm | Async camera and preview, display-only mirror, existing face/palm services; manual SIAP retained | Owner-reported preview/button/palm PASS and prior twenty cycles; missing source/device fields stay unknown |
| Capture/review/retake | Three original photos/design, one retake/design; v2 review and photo areas in the shared result/print/digital PNG mirror | Raw JPEGs retain original orientation/resolution; template/text/QR and v1 defaults stay normal. Old outputs unchanged; quantity means copies, not more sessions. [Mirror proof/form](qa/portrait-v2-mirrored-output/README.md) |
| Audio | Single v2 owner; GUI loop for still ads/photo journey, video's own audio, distinct game loop; one cue per action | Owner-reported normal. BUG-017 is monitoring after the later report, not a proven decoder fix; v1 BUG-001/007 stay separate |
| Thermal photo printing | Existing v1 backend/config; --print auto-sends one durable batch per approved design, --manual-print optional; uncertainty/no-replay guards | New-source fixtures pass; actual current paper/copy/QR acceptance pending. Prior owner paper reports stay at unknown HEAD. Merchant trial forces printer off |
| Drive/download | --drive resumes existing isolated queue on startup/after visits; offline-safe admission, background binding/retry and large verified on-screen QR, original retention guard | New-source fixtures/pixel decode available; actual phone access/offline/restart and cloud deletion unverified. Default local; merchant trial off. BUG-009 OPEN |
| BUG-009 retention activation | Reused v1 setup/cleanup; real CLOCK required for active registration ACK, incorrect trigger setup repaired; read-only redacted CLI/status and eight-item Submit form | 807 full Python PASS/zero skips; 19 actual-Code.gs VM PASS. Owner setup/deployment unconfirmed. Google timer/deletion NOT_RUN; bug stays OPEN. [Guide/evidence](qa/bug-009-retention/README.md) |
| Meong Fly — FEAT-021 (game) | Original Stage/Flow/renderer/assets/emitter reused; persistent one-use v2 DEMO ledger | 26 reference files pinned to `672e3f7`. V2 uses manual DEMO entry; standalone camera scanner is not mounted |
| Local MOCK checkout | Local SQLite quote/promotion/admission; nonpayable QR and simulated confirmation | Win discount Rp2,500 once per order, capped at subtotal; no bank settlement |
| FEAT-020 QRIS Sandbox | Reused service/client/journal plus native v2 adapter/isolated launcher | Server quote, provider verification, one-use grant/ACK/recovery in source. Actual merchant simulator evidence pending; no trusted game-promo API |
| P5 readiness | Read-only CLI, safe metadata JSON, 26-item Submit/import form, rollback package | Owner preflight `0dc6555` = READY_FOR_MANUAL_TEST, not hardware/provider PASS |
| FEAT-008 operator Device Health | Original v1 backend/panel/worker reused with small v2 adapters and safe report export | Later R01–R04 owner retest 4/4, no issues: BUG-018 monitoring at unknown HEAD/device metadata. Selection/switching disabled |
| Other reference features | Device staging/switching, AI Background Studio, WhatsApp, newer dithering lab | Separate branches; not automatically in v2. [Reference map](gui-v2-branch-audit.md) |
| FEAT-004 ads + BUG-009 booth storage/content | Ordinary v2 launcher uses PB00X roots, 25 empty reserves, Photo/NN/raw,color,bw, saved 1-bit print and verified global/local caches; Code.gs supplies scoped reservations/binding/content/cleanup | 824 full local PASS/zero skips, 24 Code.gs PASS, matching three-job CI SUCCESS; [stage package](qa/feat-004-storage/README.md). Actual Google setup/deploy, phone/paper and deletion NOT_RUN. BUG-009 stays OPEN until real expiry evidence |
| Production payments, merchant POS/scanner, trusted QRIS promo | Disabled/not delivered in v2 | Require their own approved scope, trust contract and acceptance |

## Latest recorded automated evidence

| Checkpoint | Local full regression | Matching-source CI | Screenshot evidence |
| --- | --- | --- | --- |
| Mirror source `fc26e3d` | **808 PASS / zero failures/errors/skips**, 230.670s; earlier focused 42 PASS, renderer/template 19 PASS | [40263151709](https://github.com/pratikto/PhotoBooth/actions/runs/40263151709), all three jobs SUCCESS; native 103 PASS/one optional model-assets skip covered locally | Sixteen clean-source native captures verified, eight selected views and two form views reviewed at required sizes. Actual paper orientation NOT_RUN. [Proof](qa/portrait-v2-mirrored-output/README.md) |
| Storage/content source `53e7b4c` | **824 PASS / zero failures/errors/skips**, 241.156s; 24 Code.gs VM PASS; cold ordinary launcher offline PASS | [40273343183](https://github.com/pratikto/PhotoBooth/actions/runs/40273343183), all three jobs SUCCESS; optional CI model skip covered by the full local run | 133 CI PNGs / source reports checked; 28 final native captures + two form views published. [Proof/setup/checklist](qa/feat-004-storage/README.md). No cloud/paper/phone acceptance inferred |
| BUG-009 source `887ba39` | **807 PASS / zero failures/errors/skips**, 238.684s; 44 focused Python and 19 Node VM PASS | [40255716011](https://github.com/pratikto/PhotoBooth/actions/runs/40255716011), all three jobs SUCCESS; native 103 PASS/one optional model-assets skip covered locally | No main GUI layout change; four native CI and two form views reviewed at 800×1280/452×900, 360px form overflow check; [proof](qa/bug-009-retention/README.md). Fixtures are not Google acceptance |
| Photo-entry source `20453fe` | **800 PASS / zero failures/errors/skips**, 217.888s | [40248962384](https://github.com/pratikto/PhotoBooth/actions/runs/40248962384), all three jobs SUCCESS; native 103 PASS/one optional palm-assets skip covered locally | Twelve clean-source PNGs hash/dimension verified; six affected idle/invitation/tutorial views reviewed at both required sizes; [proof](qa/portrait-v2-photo-entry/README.md) |
| Print/Drive source `266b2c8` | **800 PASS / 0 failures / 0 errors / 0 skips**, 213.823s | [40208966127](https://github.com/pratikto/PhotoBooth/actions/runs/40208966127), all three jobs SUCCESS; delivery 17 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/1 optional model-assets skip | 133 PNGs verified; delivery views reviewed at both sizes, large QR screenshot pixels decoded; [proof/form](qa/portrait-v2-print-drive/README.md) |
| BUG-018 source `ebb53fd` | **785 PASS / 0 failures / 0 errors / 0 skips**, 321.181s | [40189694738](https://github.com/pratikto/PhotoBooth/actions/runs/40189694738), three jobs SUCCESS; health 80 PASS, Sandbox 139 PASS, native 97 PASS/1 optional model-assets skip | 119 PNGs source/hash/dimension verified; operator views reviewed at 800×1280/452×900; [proof](qa/portrait-v2-health-clicks/README.md) |
| Operator source `ea394e8` | **780 PASS / 0 failures / 0 errors / 0 skips**, 270.671s | [40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369), three jobs SUCCESS; health 80 PASS, Sandbox 139 PASS, native 92 PASS/1 optional palm-model-assets skip | 119 PNGs source/hash/dimension verified; required views reviewed; 15 local operator PNGs reviewed |
| Earlier P5 source `9433010` | **688 PASS / 0 failures / 0 errors / 0 skips**, 211.646s | [40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417), three jobs SUCCESS; native includes one optional palm-model-assets skip | 109 PNGs source/hash/dimension verified; required views reviewed |

The optional CI model case is covered by each recorded local full run with
supplied assets. Three successful CI jobs do not mean zero skipped cases.
These are Linux/software-GL/dummy-audio/offline-fixture results, with the Windows
CI audio job also using dummy output. They are not physical acceptance.
[Operator proof](qa/portrait-v2-operator-health/README.md) · [P5 proof](qa/portrait-v2-p5/README.md).

## Outstanding acceptance

Use the [49-item consolidated outstanding checklist](qa/portrait-v2-pending-acceptance/windows-checklist.html)
for current-build Windows/paper/Drive/cache/retention, real Sandbox/recovery
and privacy review. It retains earlier owner passes; only the existing NEW
Sandbox integration gate requires twenty cycles. Import never checks tests.
[Scope and instructions](qa/portrait-v2-pending-acceptance/README.md).

P5 is ready for acceptance, with current Windows integration, actual merchant
Sandbox, physical paper/uncertain-job handling, Drive/download/offline/cloud
retention, privacy and release signoff still awaiting complete evidence. Keep
prior owner reports at their known or unknown tested HEAD; never attribute them
to a newer commit. Safe approved source work continues independently of laptop
availability. [Test ledger](test_checklist.md) · [bug register](bug_tracker.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/FEATURE_STATUS.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

