# AR-12 — final source validation and external acceptance gates

## Documentation status check and recovered historical provenance — 29 October

Current authority is **f72fdbc / AR-13 CONDITIONAL**, not the earlier AR-09/AR-12
diagnostic checkpoint. Latest published run is 1097 / 1093 PASS / 4 SKIP, matching
CI 40767441201 all three jobs SUCCESS. This documentation check verifies recorded
source-tree IDs against current HEAD and current CI status; it does not rerun or
finish the separately IN_PROGRESS code-conformity review. Matrix remains 43 PASS /
9 BLOCKED / 17 NOT_RUN; PAY-06 and other exact fault windows remain open.

The earlier session's original 635de92 full report is available in this workspace:
its digest and exact 1094 / 1091 PASS / 3 optional SKIP summary match saved metadata,
and all 276 recorded historical source hashes match their pinned Git objects.
[Historical provenance supplement](evidence/historical-635de92-provenance.json)
recovers that previously unavailable provenance. Raw logs stay private/untracked.
This is separate older evidence, not a replacement or revalidation of the newer
f72fdbc run. Dated “unavailable here” statements below describe the earlier review
environment before this supplement was recovered. No runtime/test/OPS change.


## Final source evidence — 29 October 2026

Source `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`: **1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors**, 428.924s, CPython 3.12.14 on Debian 13.6/cloud Linux,
SDL offscreen/software GL/dummy audio; tracked tree clean before and after.
Command: `.venv/bin/python tools/run_kiosk_unittests.py`, with
`PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1` and the isolated environment
recorded in [safe provenance](evidence/ar12-final-verification.json).
Four tests skipped in this full command: three optional palm-model assets and one native-video opt-in. The native-video case subsequently PASSed alone at the same SHA with its opt-in enabled (exact IDs/reasons below).
Both `PHOTOBOOTH_TEST_*` opt-ins were omitted in a preliminary run: 1097 run /
1020 PASS / 77 SKIP / zero failures/errors, 248.048s. That limited run is
superseded; it is not substituted for the applicable final run.

Matching [CI 40767441201](https://github.com/pratikto/PhotoBooth/actions/runs/40767441201)
at the exact final source: **all three jobs SUCCESS**. Earlier requested green
CI 40756922129 at b5931c8 is independently verified historical evidence, not
certification of the later scanner change. Hosted Windows/Linux is not device
acceptance. Prior session 1094/1091/3 counts remain reported/unverified because
their raw log/provenance was unavailable; final counts above come from a new run.

Final native recorder: **28 PNGs** at 800×1280 and 452×900, source `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`,
clean tracked tree; every dimension/hash verified, **four QR decodes PASS**
without payload logging. Ten nonsecret synthetic scenes are retained under
[evidence/ar12-native](evidence/ar12-native); ticket QR pixels remain private.
Selected final neutral-claim, compact release/return and archived-lookup layouts
were inspected without clipping. Native walkthrough covers one-photo return,
ownership, operator inspection/isolation/release and archived reentry. Retake,
multi-design and COMPLETED-result-only invariants have source tests; their
dedicated native screenshot scenes remain **NOT_RUN**, not borrowed from this
single-design walkthrough. Phone/physical-camera scanning remains NOT_RUN.

Matrix ledger: **43 PASS / 0 FAIL / 0 SKIP / 9 BLOCKED / 17 NOT_RUN** across
69 required IDs. Missing exact subprocess/write-fault windows are explicitly
retained despite successful logical/reopen/exception tests. See
[matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md#executed-evidence-ledger--29-october-2026).
AR-13 assessment: **CONDITIONAL for controlled acceptance; NOT READY for
unattended commercial release**, with [owner checklist A01-A12](AR13-READINESS.md).

Native-video supplemental command (same offscreen/dummy environment plus
`PHOTOBOOTH_TEST_VIDEO=1`):
`.venv/bin/python tools/run_kiosk_unittests.py test_kiosk_advertising.KioskAdvertisingTests.test_native_video_has_frames_payment_is_muted_and_retiring_unloads_decoder`:
**1 PASS / zero failures/errors/skips**, 5.472s, at the same final SHA. This
separate pass does not rewrite the four full-run SKIPs. Only three optional
palm-model cases remain unexecuted across this full run plus supplement.

Exact optional skips in the full command:

- `test_real_model_worker_drives_the_actual_controller_and_keeps_button_capture (test_camera_recovery.CameraRecoveryTests.test_real_model_worker_drives_the_actual_controller_and_keeps_button_capture)` — 'Native model assets are opt-in'
- `test_native_video_has_frames_payment_is_muted_and_retiring_unloads_decoder (test_kiosk_advertising.KioskAdvertisingTests.test_native_video_has_frames_payment_is_muted_and_retiring_unloads_decoder)` — 'Native video checks require opt-in and ffmpeg'
- `test_real_palm_model_starts_v2_countdown_without_blocking_manual_capture (test_kiosk_v2_widgets.PortraitKivySmokeTests.test_real_palm_model_starts_v2_countdown_without_blocking_manual_capture)` — 'Native model assets are opt-in'
- `test_actual_model_accepts_a_palm_and_rejects_other_gestures_and_empty_image (test_palm_gesture.NativePalmModelTests.test_actual_model_accepts_a_palm_and_rejects_other_gestures_and_empty_image)` — 'Native model assets are opt-in'

No raw logs, real customer data or ticket payloads are committed. The complete
environment, source trees, report digest, safe native manifest and CI references
are in the evidence JSON. No code changed after the final tested source; later
publication is documentation/evidence only.

## AR-12.e — independently verified CI history and deterministic fixture (29 October)

### AR-12.f — recovery scanner false negatives exposed by the fresh CI

Test-only checkpoint `959264962bb4e64a8a4531a085676b55ad26e660` was pushed and
remote-verified. Its CI [40766621706](https://github.com/pratikto/PhotoBooth/actions/runs/40766621706)
passes the repaired 103-case content group and Windows, but Linux job
`123092367855` fails `test_recovery_scan_uses_existing_camera_and_poll_preserves_typed_ticket`:
customer_claim_required stays true after scanning a synthetic valid ticket.
Do not present the older green run as verification of this newer test source.

A private 100-random-ticket probe at unchanged application source yields ten
primary OpenCV decode misses; integer enlargement recovers none. OpenCV's
already-installed `QRCodeDetectorAruco` decodes all ten identical failed frames.
Deterministic public synthetic seed `AR12 decode fixture 2` also reproduces a
primary miss and alternate exact decode locally (OpenCV 5.0.0). CI did not retain
the random failing ticket, so that specific failure's payload is unrecoverable.

Correction: scan the existing camera owner's copied frame with the original
detector first; on an empty decode only, make one alternate OpenCV attempt when
that API exists. No new dependency, camera, renderer, scanner service, namespace
fallback, payment authority or customer-auth bypass. A foreign nonempty QR is
rejected immediately; absent alternate/undecodable input remains held. Original
customer_claim still verifies booth/order/secret/current settlement. New source
tests reproduce the primary failure before the change (3 run / 1 ERROR), exercise
real alternate pixels, reject foreign roles without fallback, and fail closed
without the optional detector. Physical phone/camera acceptance remains NOT_RUN.

The interim full run at `9592649` was stopped after this newly identified runtime
correction became necessary; it has no authoritative final count. A complete run
and refreshed native evidence follow the committed scanner correction. Preserve
the original previous-session 1094/1091/3 report as unverified historical metadata.

Scanner correction focused command:
`.venv/bin/python tools/run_kiosk_unittests.py test_kiosk_v2_sandbox test_kiosk_v2_sandbox_widgets test_customer_claim_session test_customer_capability`:
**56 PASS / zero FAIL/ERROR/SKIP**, 59.818s, Linux/Python 3.12.14/OpenCV 5.0.0,
SDL offscreen/software GL/dummy audio, permitted local HTTP fixtures.

Refreshed remote `e303cdf4db3f009d2f4ed1a075e160d17aaa8bdb`; clean checkout
fast-forwarded on the required branch. Latest application source is
`635de92c0f8fba9189981ebf2f168bff8b7a52af`; CI/workflow source is
`b5931c8ef2e3d7b800e024c38a653fef5b4b4a1e`. The subsequent twelve commits
change documentation only. No runtime changes are needed for this increment.

Connected GitHub job logs now independently establish:

| Run | Checked-out SHA | Pure / Linux desktop / Windows |
| --- | --- | --- |
| [40754677245](https://github.com/pratikto/PhotoBooth/actions/runs/40754677245) | `09788b1cd18c1dcf4be2357693543323103e2816` | PASS / cancelled / FAIL |
| [40755284102](https://github.com/pratikto/PhotoBooth/actions/runs/40755284102) | `cfacc18370559f4eddc44bda1c0a12572f89b5b3` | PASS / cancelled / FAIL |
| [40756011109](https://github.com/pratikto/PhotoBooth/actions/runs/40756011109) | `635de92c0f8fba9189981ebf2f168bff8b7a52af` | PASS / FAIL / PASS |
| [40756922129](https://github.com/pratikto/PhotoBooth/actions/runs/40756922129) | `b5931c8ef2e3d7b800e024c38a653fef5b4b4a1e` | PASS / PASS / PASS |

Windows diagnostic job `123053061059` records two `test_output_journal` errors:
read-only PNG `os.fsync` raises Errno 9. Commit `635de92` uses non-truncating
`r+b` and adds real output child-exit tests. Final Windows job `123058212487`
runs 47 autonomous cases, 15 creation cases, 55 startup cases and 103 native
audio cases successfully (Windows Server 2025, CPython 3.12.10, dummy audio).

Linux failed job `123055133199` names
`test_booth_sync.BoothSyncTests.test_customer_arrival_inside_content_chunk_uploads_before_remaining_content_and_resumes`:
line 257 `assertTrue(content.pending)` failed, 103 run / 1 failure. Final job
`123058212482` passes the same 103-case group plus 343 Sandbox/recovery cases,
80 Health cases and 111 native cases (one opt-in model SKIP), Ubuntu 26.04,
CPython 3.12.15. Between these runs, `b5931c8` added failure diagnostics only;
it did not repair application code or change test assertions.

Controlled local reproduction at clean `e303cdf`: the original case FAILs at
mock monotonic time 1.0 and PASSes at 100.0. `BoothDriveWorker` initializes
`_content_checked=0` and admits its first content check only at time >=60.
Thus a host-clock-dependent fixture is proven; the failed runner's actual
monotonic value was not logged, so its historical cause is not conclusively
established. The fixture now explicitly sets monotonic time to 100.0. Every
priority/order/pending/pointer assertion remains intact; no sleep, timeout,
tolerance or runtime scheduling policy changes. Initial content scheduling can
still defer on a host with uptime under 60 seconds; device timing is separate.

Focused command: `.venv/bin/python tools/run_kiosk_unittests.py test_booth_sync test_content_cache`.
Focused result: **33 PASS / zero FAIL/ERROR/SKIP**, 2.543s. Final complete regression will be pinned in the next evidence
increment. Original 1094/1091/3 full-run log was not found in this restored
workspace or published AR evidence: treat it as a previous report, not independently
verified metadata. One new complete run is justified by this test correction and
missing provenance, not by the twelve documentation commits. Final native
captures at clean `e303cdf` use unchanged application/renderer source; hashes,
QR checks and coverage limits follow in the evidence package.

Reviewed: repository governance/current status/decisions/bugs/test ledger, all AR
stage contracts and source tests, provider/operations/matrix, and all five queued
OPS documents. OPS remains NOT_STARTED. Rollback this test-only change with a
scoped inverse; retain every customer ledger, claim, image and delivery job.

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

Final-fix CI 40756011109: Windows job SUCCESS (including new autonomous ledgers/
WAL/file tests) and pure job SUCCESS; desktop fails the existing isolated P3 group.
Its annotation again contains only exit 1; underlying case is not established.
Add failure-only desktop report annotations, preserving command/assertions and
artifacts. No speculative application repair or unrelated test relaxation. The
full local rerun at 635de92 remains running; the annotation-only follow-up changes
no application/test source. Original failures remain auditable CI history.
