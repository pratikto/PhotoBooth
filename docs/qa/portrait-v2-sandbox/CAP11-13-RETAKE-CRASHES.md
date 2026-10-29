# AR-04/05 — CAP-11–13 retake process-exit evidence

29 October 2026 (Asia/Jakarta). Owner explicitly requests completion through
CAP-13. Base/remote verified `8c5553b77f0264622b19810d86e95a08a105c7eb`, existing
feature branch; work/ scratch only. Contract recorded before new test code.

## Review and independently testable increments

Re-read AGENTS/protocol, current index/status/defects, checkpoint/handover,
master/roadmap/matrix and AR-04 capture/AR-05 reconstruction contracts. Earlier
architecture/decisions/provider/privacy/retention reviews remain applicable at
the unchanged application tree. Reviewed complete capture_journal, photo_recovery,
PhotoTest retake/capture/restore, workflow, existing capture/reconstruction tests
and actual authenticated AllocationHarness. No archive/customer data inspected.

1. CAP-11: abrupt exit after durable retake selection and after retake INTENT
   before saved bytes. Recover the same selected original index, three originals,
   unconsumed retake quota and original paid binding. Empty intent may become
   VOID_BEFORE_FRAME audit; only a new deliberate synthetic capture consumes quota.
2. CAP-12: abrupt exit after fsynced temporary frame, STAGED hash and published
   JPEG, before manifest/quota acknowledgment. Unknown/unhashed bytes stay held;
   proved staged/published bytes may be adopted once without shutter/overwrite.
3. CAP-13: abrupt exit after atomic retake/quota manifest commit, before worker
   memory acknowledgment. Restore review with the original quota consumed,
   selected index and final replacement; preserve all original bytes.

Reuse actual KioskCheckout/QrisKioskClient/FastAPI/backend/SQLite/PhotoTest paths,
one original synthetic payment/grant/allocation, three distinct tiny originals,
two frozen copies and one distinguishable retake. Raw customer ticket only in
parent/child memory and stdin, never argv/journal/evidence. Require original
customer proof and fresh provider settlement before typed restore permission.
No automatic capture/compose/print/upload, replacement allocation, ordinary
counter advance, retention extension or lost OWED. Reopen after repair/commit
again and check the same quota/path/operation remains authoritative.

Focused tests, docs/checkpoint/handover, commit and immediate push/remote HEAD
verification after each safe increment. A runtime defect requires reproduction,
minimal repair and final applicable full regression. Tests-only changes retain
prior full e0dc594/native c94696d provenance without borrowing a new run.
Linux/Windows hosted CI is separate from real camera/device/power-loss evidence.
Rollback only new tests/CI/docs; retain all financial/media/claim/fence/budget
records. No schema/UI/runtime change is presumed; no production/OPS, actual
payment/print/Drive/deletion, public ingress, branch/default/master operation.
CAP-16/20, UX-05/07/11, BUG-023 and external gates remain outside this increment.

## Increment 1 — CAP-11 verified

One new method/two actual child exits, codes 100 (selection), 101 (INTENT before
saved bytes). Focused **76 PASS / zero failure/error/skip**, 20.288s. Original
customer claim/current provider status required on every reopen; original index,
three JPEGs, frozen two copies/deadlines, grant/allocation/OWED unchanged. Empty
intent retained as VOID audit, quota untouched until explicit new synthetic frame;
second controller reopen restores review/consumed quota without a new capture.
No runtime defect found. Linux/Windows CI includes the new module, result pending.
Matrix 52/1/9/7; CAP-12/13 NOT_RUN until next increment. [Exact command/hashes](evidence/cap11-verification.json).
