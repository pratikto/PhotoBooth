# AR-05 — CAP-16 final composition before COMPLETE

29 October 2026 (Asia/Jakarta). Base/remote verified
`73451f3f449f97fcec76e52a14db4ad5a3e8027f`, existing feature branch.
Owner continues the first unfinished checkpoint; BUG-023 and real-device/
provider acceptance remain open. Contract recorded before test code changes.

## Review and acceptance

Re-read AGENTS/protocol, current index/status/backlog/defects, checkpoint/handover,
AR-05 reconstruction and PAY-18 service/archive evidence. Earlier unchanged
architecture/decisions/master/roadmap/provider/privacy/retention reviews still
apply. Reviewed existing service crash worker/tests, actual AllocationHarness,
PhotoTest composition/restore and KioskCheckout private restart, proof, service
ACK and archive paths. Reuse these implementations; no replacement engine.

1. Actual child exit after final COMMITTED PNG/local composition before local
   completion intent; disk visit STARTED, backend STARTED/OWED.
2. Actual child exit after saved COMPLETING intent before any COMPLETE request;
   backend still STARTED/OWED, no completed archive. Original proof/current
   settlement restores only the original result, then same STARTED/COMPLETED
   ACK tuples. No charge/allocation/capture/render/print/upload replay.
3. Following increment: prove provider outage/refund and damaged committed PNG
   cannot fabricate completion or bypass privacy after these exact crashes.

Use three tiny synthetic frames/two frozen copies and actual authenticated
HTTP/controller/SQLite/photo paths. Original ticket only in memory/stdin, never
argv/journal/committed evidence. Assert exact identities, manifest/media bytes,
original retention/frozen contract, independent OWED, WAL/FULL/integrity and
durable history/index before release. Service ACK identity remains the existing
order/grant/transaction/state tuple; no invented operation ID.

Focused tests -> docs/checkpoint/handover -> immediate commit/push/remote check
per meaningful increment. Tests-only changes retain old full/native provenance;
a reproduced runtime defect requires minimal repair and final full regression.
No runtime/schema/UI change presumed. Software exits are separate from actual
disk power-loss/Windows/Ubuntu/merchant/camera/paper/Drive/deletion acceptance.
Rollback tests/docs only, preserve all financial/media/claim/fence/budget records.
No production, OPS, public ingress, new branch/default/master operation.

## Increment 1 — final composition/pre-request exits verified

72 focused PASS / zero failure/error/skip, 20.830s. One CAP-16 method runs two
actual child exits (106/107). Reuses existing service crash worker and actual
HTTP/controller/backend/PhotoTest; no replacement runtime. Backend remains
STARTED/OWED after local composition at both boundaries. Restart cannot expose
media or release occupancy; original ticket/current settlement restores only
result, then acknowledges original STARTED and COMPLETED tuples without any
new allocation or media/delivery effect. Two exact archives precede release;
second controller/store reopen preserves original identities/manifest/media.
No runtime defect found, no runtime/schema/UI change. CI pending at containing
commit; prior full/native provenance retained. [Exact evidence](evidence/cap16-composition-verification.json).
Next provider/refund/damaged-PNG denial cases, then matching CI/checkpoint.

## Increment 2 — denied recovery cannot fake completion

First micro-push fcc0ae96b5de96bc962b4a2e9d25285cf9a3c7de remote verified.
Two additional CAP-16 methods each run the actual saved-COMPLETING/pre-request
child exit (107). Provider outage yields HTTP 503, then current refund HTTP 409;
even an explicit local request_complete intent cannot bypass private worker
reconciliation and create an ACK. Original STARTED/OWED/grant/allocation and
composed bytes remain. A corrupted synthetic committed PNG fails typed restore
before any private session installation; no rerender/service ACK/archive/release.
Two fresh parent controller/store reopens retain those corrupt bytes, exact
manifest and owed service. No actual customer data is damaged or inspected.

Initial denial run 2 PASS, 1.951s. Final focused **74 PASS / zero failure/error/
skip**, 22.333s. Three CAP-16 methods/four new children/two distinct boundaries;
the reused PAY-18 methods retain their separate 23-exit coverage. No runtime
defect found or runtime/schema/UI change. [Exact evidence](evidence/cap16-denials-verification.json).
Matching CI pending at this containing test commit; matrix 55/1/9/4, audit and
BUG-023 remain open. Next current CI/checkpoint, then CAP-20 and AR-09.
