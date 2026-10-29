# AR-03.c — CAP-01–05 exact allocation and STARTED process exits

29 October 2026 (Asia/Jakarta). Owner explicitly continues the next checkpoint.
Base/remote verified `c4c1847bd8086c36f3ec1d3a755728896321495f` on the existing
feature branch. **Contract before tests; scenarios initially NOT_RUN here.**

## Review and intended increments

Reviewed AGENTS/protocol/prompt, current index/handover/checkpoint, roadmap,
master/provider/matrix/operations and AR-03–07 contracts. Re-read allocation,
controller journal/private claim, first-manifest/restore, backend/client/API,
existing allocation/fulfillment/crash tests. Earlier architecture/decisions and
storage/privacy review still applies; PAY-08 did not change these identities.
No protected archive, merchant settings or customer files are inspected.

1. CAP-01/02: actual os._exit before local allocation intent, after local intent
   but before backend request, and after backend allocation COMMIT before local
   reply/folder. Reopen both processes/SQLite, revalidate original customer ticket
   and current provider state; preserve one original key/order/grant/operation.
2. CAP-03–05: actual exit after folder before initial manifest, after initial
   manifest before local-ready/STARTED, and after accepted STARTED before local
   acknowledgment. Recover exact empty/reserved or validated original manifest;
   unknown/orphan bytes remain held without a substitute folder/transaction.

Reuse the actual KioskCheckout/QrisKioskClient/FastAPI/CheckoutBackend/SQLite and
PhotoTest/TransactionStore paths. Persist the synthetic provider independently
with existing MockQrisProvider. Use booth authentication plus original hashed
customer capability, not a manufactured resume permit. Parent holds the original
raw synthetic ticket in memory and passes it to the child via stdin only; no
ticket in argv, journals, committed fixtures, screenshots or reports.

## Exact assertions

- Child exits with a distinct reached-boundary code, not a caught exception.
  Database WAL/FULL integrity, local journal and process-lease reopen are checked.
- Original paid grant/fulfillment/OWED remain. An allocation missing in the backend
  can only be the first proved reserve; a committed mapping replays the original
  operation/transaction. One counter increment, no second provider POST/order.
- Before proof, no prepare/permit/private media; after real ticket redemption,
  require original service ACK before any capture controls. Restore never invokes
  capture/composition/printing/upload. Initial count zero, no automatic countdown.
- First manifest binding/frozen contract and existing media bytes do not change
  during valid reconstruction; orphan bytes are preserved and held. No recency
  lookup, customer ID reset, folder substitution or ordinary counter advance.

## Delivery and limits

Focused tests, doc/matrix/checkpoint/handover updates, immediate commit/push and
remote verification after each safe increment. If tests find a runtime defect,
reproduce before the smallest repair and run one final full regression. If only
coverage is added, retain the prior full/native evidence at its exact source;
focused/Windows/Linux CI verify new fixtures without borrowing a new full PASS.

No intended schema/journal/runtime/UI change. Scoped inverse removes only new
test/docs/CI coverage, retaining all real financial/media/claim/fence/budget
records. Abrupt software exit is not real disk power-loss acceptance. BUG-023,
PAY-18 COMPLETED reply, retake/COMPLETE/disk/physical/provider/privacy gates remain
open. No production/OPS, actual print/Drive/deletion or public deployment.

## AR-03.c1 — CAP-01/02 evidence verified

**34 focused PASS / zero failure/error/skip**, 2.647s, Python 3.12.14/Linux.
Three real child exits exercise before local intent, after durable local intent
before backend request, and backend committed allocation before reply/folder.
Actual customer capability redemption/fresh provider verification, one original
allocation/counter/grant, no repeated order/charge, WAL/provider integrity and
no implicit shutter/render are asserted. CAP-02 initializes the first manifest
only after original proof and sends STARTED for the exact allocation.
[Command, report digest and fixture hashes](evidence/cap01-02-verification.json).

No runtime defect found or runtime/schema/UI change. CAP-01/02 now synthetic
PASS; CAP-03–05 remain NOT_RUN. Matrix **47 PASS / 1 FAIL / 9 BLOCKED /
12 NOT_RUN**. Linux/Windows CI includes the fixture; result pending at this
containing test commit. No new full/native/physical acceptance inferred.
Next AR-03.c2: extend the same child fixture to folder/first-manifest/STARTED
reply boundaries; preserve unknown/orphan bytes with no replacement allocation.

## AR-03.c2 — all five allocation/STARTED scenarios focused-verified

CAP-01/02 micro-push `c87050eeb4f0223577d68796ff0ace4f4a1d2a95` verified on
origin. Extension adds actual child exit after empty folder/before manifest,
after first manifest/before local-ready STARTED, and after STARTED server commit
before client/journal acknowledgment. A repeated folder-crash negative case puts
unknown bytes in the original allocation and a synthetic neighbor: original bytes
remain held, and enumerating the parent transaction root is explicitly forbidden.

**66 focused PASS / zero failure/error/skip**, 5.965s. Six new methods execute
seven real child exits across six distinct boundaries. Original high-entropy
customer proof, current provider evidence, same grant/op/transaction/counter,
WAL/provider integrity, byte-identical existing manifest, zero capture/retake and
no shutter/render/print replay are asserted. A second fresh controller/store
reopen retains original mapping; no unsupported second-process claim is inferred
for that extra parent reopen. [Exact command/source/digest](evidence/cap01-05-verification.json).

No runtime defect or runtime/schema/UI change. CAP-01–05 now synthetic PASS;
matrix **50 PASS / 1 FAIL / 9 BLOCKED / 9 NOT_RUN**. Current CI pending at this
containing test publication. Prior full/native evidence stays pinned to e0dc594/
c94696d; no new complete regression/device/merchant/paper acceptance is claimed.
Next: inspect matching Windows/Linux CI, final docs checkpoint, then PAY-18
combined lost service replies (including COMPLETED), CAP-11–13 retake, CAP-16
compose/COMPLETE, CAP-20 disk/permission and AR-09 BUG-023 denial audit.
