# AR-04/05/08 — CAP-20 storage write-fault evidence

29 October 2026 (Asia/Jakarta). Base/remote verified
`abc44d67d69783ae429918d8e6a457f9d13724f9`, existing feature branch.
Owner continues CAP-20; BUG-023 and device/provider gates stay open.
Contract recorded before test code; no runtime defect is presumed.

## Review and bounded increments

Re-read governance/protocol, checkpoint/handover, current index/status/backlog/
defects/matrix, AR-04 capture, AR-05 reconstruction and AR-08 paid remedy contracts.
Earlier unchanged master/roadmap/provider/privacy/retention and architecture/
decision reviews still apply. Reviewed complete capture/output journal, both
atomic JSON writers, TransactionStore capture/retake/output/complete writers,
PhotoTest operations/restore, original AllocationHarness and existing file tests.

1. JPEG: ENOSPC and EACCES at intent-manifest atomic replacement, temporary
   image open, partial image write, image fsync, staged-manifest replacement,
   publication link and capture/quota commit-manifest replacement.
2. Retake and PNG: same applicable faults, selected-retake manifest, final
   transaction status write and initial bound-manifest failure; verify original
   quota/copies/retention/paid mapping/OWED and no fabricated completion.
3. Reporting failure: failure saving local paid-issue intent must retain the
   already durable OWED even when no new issue can be written immediately.
4. Both atomic JSON writers: temporary-create, partial JSON write and fsync
   faults, with no prior file and with prior durable bytes; no false destination
   replacement, temporary files cleaned, later explicit write succeeds. These
   shared-writer cases complement the business-stage replacement faults.

Faults target actual writer/renderer/filesystem calls in disposable profiles;
never fill the host disk or chmod customer files. Child catches only the injected
errno, records no successful operation ACK, invokes existing redacted paid-issue
report after the targeted fault is removed, then exits abruptly. This models a
media-write failure with reporting storage available; it is not a guarantee that
another write succeeds on a globally full volume. Existing OWED precedes faults.
Original ticket stays only in memory/stdin, never argv/journal/committed evidence.

Before restart recovery no false raw/output/quota ACK. No bytes/intent permits
only later deliberate work; unhashed/partial bytes remain held; verified staged/
published bytes recover the same operation once without shutter or render. A
previously committed output remains valid if only final transaction status fails.
Every paid claim/issue survives, original media/frozen contract/deadlines retained,
no charge/allocation/capture/composition/print/upload replay. Fresh original
customer proof/current provider status protect every private restore.

Focused checks -> docs/checkpoint/handover -> immediate commit/push/remote check
per safe increment. Runtime fixes require reproduction and final applicable full
regression. Tests-only changes retain older full/native provenance. Linux/Windows
hosted injected faults are separate from real filesystem/power-loss/device/
merchant/paper/Drive/deletion/release acceptance. Rollback tests/CI/docs only;
preserve all financial/media/claim/fence/budget records. No production/OPS/public
ingress/new branch/default/master operation; never inspect protected archives.

## Increment 1 — JPEG write faults

52 focused PASS, zero failure/error/skip, 14.598s. One method executes 14 real
children (seven JPEG boundaries × ENOSPC/EACCES). Injection reaches actual atomic
replace/open/partial image save/fsync/link operations; child verifies matching
errno, hides private state, records existing paid issue after fault removal and
exits with no capture ACK. Original saved frame, immutable paid binding/copies/
deadlines/OWED survive two controller/store reopens. Unknown bytes remain held;
proved staged/published bytes recover the same operation once with no capture.
No runtime defect found; tests/CI/docs only. CAP-20 aggregate remains NOT_RUN,
retake/PNG/initial/reporting faults next. [Exact evidence](evidence/cap20-jpeg-verification.json).

## Increment 2 — full storage matrix focused-verified

First micro-push 2ac9e82ce72de49d6a7ade385c3db37b2e1707d5 remote verified;
its JPEG-only CI 40838609747 SUCCESS. Expanded module initially 5 PASS/39.700s,
then 56 focused PASS/43.893s; added shared atomic-writer coverage and final
**57 focused PASS / zero failure/error/skip**, 43.617s. Six new methods cover:

| Kind | Error cases | Actual child exits |
| --- | --- | --- |
| Original JPEG, seven business boundaries × two errno | 14 | 14 |
| Retake plus selected-index manifest, eight × two | 16 | 16 |
| PNG plus final transaction status, eight × two | 16 | 16 |
| First bound manifest, two errno | 2 | 2 |
| Local paid-issue intent, two errno | 2 | 0 |
| Both atomic writers × create/partial-write/fsync × prior/absent × two errno | 24 | 0 |
| Total | 74 | 48 |

After failed first manifest, actual backend remains RESERVED and only original
allocation may initialize once. Retake failure cannot falsely consume/renew quota;
known saved retake restores original selected index. Output INTENT/partial bytes
remain held; validated staged/published PNG adopts once without renderer. If only
final transaction-status write fails after output ACK, that valid committed PNG
remains authoritative, while backend service stays STARTED/OWED. No fake rollback
of previously committed output and no fake fulfillment. A failed local issue
intent makes no API call, leaves durable OWED intact; later report/replay creates
one event. Shared atomic-writer failures preserve exact prior bytes or absence,
clean temporary files, and allow a later explicit successful write.

[Exact command/source/digest](evidence/cap20-all-verification.json).
No runtime defect found; no runtime/schema/UI change. Matrix 56/1/9/3; CAP-20
synthetic PASS, matching CI pending at this containing commit. Faults are targeted
injected operations, not full-host disk filling or real permission/power-loss/
device certification. Extra successful/held reopens are parent-process, distinct
from the 48 child exits. Next current CI/checkpoint, then AR-09 BUG-023.
