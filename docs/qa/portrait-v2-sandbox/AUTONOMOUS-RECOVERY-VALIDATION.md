# AR-12 — final source validation and external acceptance gates

29 October 2026. Read all AR contracts/checkpoint/matrix/provider/operations and
new release/supervisor/inbox tests plus original full runner, workflow and native
renderer before final validation. Existing branch, no production/deployment.

Plan before changes: close conclusive fault-matrix gaps with actual child-process
release/SQLite WAL exits, locked writer rollback, and complete-session late return
coverage. A normally completed customer's ticket must keep an exact bounded archive
before another visit replaces the live journal, with current proof and busy-booth
guards; completed service may reopen saved result only. Extend native fixture
capture through two-phase release/return, record source hash/dirty state and verify
screen QR formats without emitting payloads. Add portable Windows backend/file
checks with their dependencies. Then commit/push final functional source, run one
complete applicable regression and pinned native captures, inspect matching CI,
and publish exact PASS/FAIL/SKIP/NOT_RUN matrix. Device/provider gaps stay explicit.
No source test can certify actual merchant, camera, paper, retention or public TLS.

## AR-12.a — final functional fault-gap increment

Normal COMPLETED journals now archive before becoming replaceable. Original valid
ticket can reopen saved result only after current proof and a free-booth check;
it cannot admit another capture or interrupt another visitor. PREPARE recovers
only an exact server allocation whose operation matches local intent after a lost
binding ACK. Local isolation can retire a previously done session when the newly
paid order has no allocation; active/uncertain ownership still refuses.
Journal and archive renames fsync their parent directories on supported POSIX;
Windows lacks this Python directory-fsync primitive, so actual filesystem/power-loss
acceptance remains open rather than claimed equivalent. No media is rewritten.

Fault fixtures now use actual os._exit after PREPARE/ACK, reopen SQLite WAL with
integrity_check, and verify failed locked-writer BEGIN cannot partially fence or
release rights. Native recorder extends through worker isolation, release/ads,
lookup and original returning capture; source SHA plus dirty state are recorded.
Windows CI installs backend/OpenCV extras and checks the ledgers/file/crash gates
separately from actual hardware. Existing startup/default checks remain.

Focused **57 PASS / zero FAIL/ERROR/SKIP**:
`test_autonomous_recovery_faults test_release_session test_kiosk_v2_sandbox_widgets test_customer_claim_session test_qris_session test_checkout_release`.
After parent-directory durability change, focused core rerun recorded below.
Full suite and final-source native evidence follow the committed source; no actual
Windows/Ubuntu/merchant/paper/Drive/public HTTPS acceptance inferred.
Final durability/core rerun: **25 PASS**, zero failures/errors/skips,
`test_release_session test_autonomous_recovery_faults test_qris_session test_checkout_release`.
Includes a new paid/unallocated visit safely isolating the previous already-done
photo worker while retaining its original output. Source is ready for the single
final full regression and pinned visual/CI checks; release acceptance is not implied.

## Initial final-source CI and Windows diagnosis

Source 09788b1 local native captures: 28 PNGs at both target sizes, clean tracked
tree/source SHA recorded; four screenshot QR identities/formats decode correctly
without logging payloads. Compact isolation/lookup and portrait returning capture
visually inspected without clipping. Full local regression is running separately.
CI run 40754677245 passes the pure job, but its newly added Windows autonomous
step fails; annotation initially exposes exit code 1 only. Direct log retrieval
redirects to a storage host denied by the environment network policy. No Windows
PASS or cause is inferred. Add failure-first check annotation using the existing
portable-step pattern, preserving the failing test command/exit and raw artifact.
This is evidence plumbing only, not an application change or weakened assertion;
the complete local run still tests functional source 09788b1. Rerun required to
identify the actual Windows failure, then fix that cause with focused evidence.

## Windows cause established and portable correction

Diagnostic CI 40755284102 exposes two errors in test_output_journal: Windows
os.fsync on the renderer's reopened read-only PNG descriptor raises OSError
[Errno 9] Bad file descriptor. Source now reopens the completed temporary PNG
with r+b, without truncating/changing bytes, before fsync. No assertion is removed.
Add actual output-process os._exit fixtures at INTENT/STAGED/PUBLISHED/COMMITTED;
originals/hash/visibility/manifest ACK remain conclusive at each boundary.
The Windows step now emits only its aggregate result as a success notice so raw
log-storage access is unnecessary to distinguish PASS/SKIP. Existing failure
annotations and artifact remain. Final matching Windows rerun is required.

The first complete local run at 09788b1 finished **1093 run / 1090 PASS / 3 optional
palm-assets SKIP / zero failures/errors**, 326.951s. This remains dated pre-portable-
fix evidence. Because runtime source changed, repeat full regression at the final
fixed source; do not relabel the earlier full pass as Windows certification.
Portable-fix focused checks: **31 PASS / zero FAIL/ERROR/SKIP**,
`test_output_journal test_capture_journal test_photo_reconstruction test_release_session`.
