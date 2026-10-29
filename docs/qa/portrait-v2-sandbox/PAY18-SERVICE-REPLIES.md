# AR-03.d — lost claim / STARTED / COMPLETED responses

29 October 2026. Base and remote HEAD verified:
`03189012b5f4c6204ef4f8718bb218a1baac32d5` on the existing feature branch.
Application remains e0dc594. Contract recorded before new test code; results
are NOT_RUN until executed below. No runtime defect is presumed.

## Review and acceptance

Reviewed current AGENTS, protocol/prompt, index/architecture/decisions/status/
backlog/defects/test ledger, handover/checkpoint, master/roadmap/provider/matrix,
AR-00–11 contracts and CAP-01–05 evidence. Reuse AllocationHarness, actual
KioskCheckout, authenticated QrisKioskClient/FastAPI/CheckoutBackend/SQLite,
MockQrisProvider, PhotoTest and the existing crash/durability/customer fixtures.
Historical full/native provenance remains at its original source.

First increment: one original pending order and memory-only customer ticket;
actual child exits after original booth claim, customer-claim, STARTED and
COMPLETED commits, before the corresponding local acknowledgment. The original
booth claim uses its actual authenticated HTTP client; restart ownership/privacy
is still separately enforced by the controller. Recover the same
claim operation/grant/allocation/transaction, synthesize three tiny camera
frames and compose once before completion. Recovery must restore the original
result without capture/render/print/upload; no repeated provider POST/order.
Check private pre-proof hold, fresh provider status/outage/refund denial, OWED,
original manifest/media bytes, WAL/FULL integrity and durable completed archive.
The service acknowledgment identity is the existing order/grant/transaction/
state tuple; do not invent a separate service operation/ACK ID.

Following increment: kill at completion/archive publication boundaries and
prove a local COMPLETING journal cannot release occupancy before durable
history/index. Keep final-compose/pre-request CAP-16 coverage separately tracked.
No physical camera, printer, Drive or merchant account is used. Software exits
are not disk power-loss or Windows/Ubuntu device acceptance.

Focused checks -> docs/checkpoint/handover -> immediate commit/push -> remote
HEAD verification per increment. If a runtime defect appears, reproduce before
a minimal fix and run final applicable full regression. Tests-only increments
retain old full/native results without claiming a new full run. Rollback removes
only these tests/CI/docs; preserve all financial/media/claim/fence/budget records.
BUG-023, remaining media/UX/external gates and queued OPS stay unchanged.
No production, actual payment/printing/upload/deletion, public deployment,
new branch or master/default/merge operation.

## AR-03.d1 — focused verification

85 PASS / zero failures/errors/skips, 12.257s, Python 3.12.14/Linux. Two new
methods execute eight real child exits at four boundaries (90–93), recover the
same original result/ACK tuple, and deny outage/refund without private restore
or lost OWED. Initial fixture errors were a misspelled capability column (two
ERROR) and omitted fresh settlement observation before the original claim (two
FAIL in an 85-case run); corrected fixture only, no runtime/assertion weakening.
The booth claim runs through actual authenticated HTTP after read-only fresh
reconciliation; the controller still requires original customer proof at restart.
No runtime defect found. PAY-18 synthetic PASS; matrix 51/1/9/8, audit IN_PROGRESS.
[Exact command/source/digest](evidence/pay18-replies-verification.json).
Linux/Windows CI now includes the new module; matching result pending.
Next: completion/archive exits; CAP-16 pre-request kill remains NOT_RUN.

## AR-03.d2 — completion/archive durability

First increment pushed/remote verified at
`3ad80da74da2a0fc3c9d5e3dbe3d84f91a483f4a`. New child exits: 94 after the
COMPLETED reply is locally accepted but before archive; 95 after the per-operation
history write/directory sync but before lookup index; 96 after both history/index
and their supported directory syncs, before final COMPLETED visit journal.
Disk journal remains COMPLETING in each case, backend COMPLETED/COMPOSED + OWED.
New-cart admission and archived lookup cannot bypass the active visit. Private
observation changes no archive bytes. Original customer proof/current settlement
restores only original result and replays the same completion tuple, then writes
both exact archives and final journal. No capture/compose/print/upload repeats.

New archive test has three subcases, each reusing the four preceding reply exits:
15 child exits. Together with the two original methods: **23 exits at seven
boundaries**, three new methods. Module-only initial run: 3 PASS, 15.827s.
Final combined focused run: **86 PASS / zero failure/error/skip**, 22.532s.
Two original copies/one design/three JPEGs/one PNG and NOT_SENT remain preserved;
raw synthetic ticket absent from journal and both archives. No runtime defect.
[Exact command/source/digests](evidence/pay18-archive-verification.json).

Linux/Windows matching CI pending at this containing test commit. Prior first
run 40818395624 is in progress at publication; do not infer success. No new full/
native/device/merchant result. PAY-18 stays synthetic PASS, matrix 51/1/9/8.
CAP-16 final-compose/pre-request process exit remains NOT_RUN; it is stronger
than these after-backend-completion exits. Next CAP-11–13 after CI/checkpoint.
