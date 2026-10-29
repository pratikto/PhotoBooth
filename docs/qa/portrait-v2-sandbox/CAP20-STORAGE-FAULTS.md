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
