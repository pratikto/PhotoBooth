# Meong Photobooth — test evidence and acceptance

## 28 October — BUG-020 Sandbox key syntax

Baseline reproduction: two new-format checks error at the unchanged prefix
guard. Corrected source: 136 focused launcher/provider/backend/session checks
PASS, zero failures/errors/skips, 0.420s. Both key formats retain Sandbox-only
requests and server-only credentials; HTTP 401 never falls back to Production.
Final full regression/CI and actual merchant NOT_RUN limits are tracked in the
[correction evidence](qa/portrait-v2-sandbox/KEY-FORMAT.md).

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

## 27 October — Drive delivery priority and timing

The owner prioritizes customer upload/GUI responsiveness. Source now uses one
file per transaction per pass, chunk-yielding content sync, incremental five-slot
reserve batches with startup/periodic reconciliation, and verified cross-version
asset reuse. Structured monotonic timing distinguishes queue/request stages.
Known-delay production root cause remains unmeasured; native/fixture evidence
and exact update/rollback steps are in the [delivery runbook](qa/drive-delivery-performance/README.md).
No deployed Google version, actual throughput or cloud deletion is certified.

**Final FEAT-009 verification — 27 October:** source `f023029` / matching-source
CI [40423003641](https://github.com/pratikto/PhotoBooth/actions/runs/40423003641),
all three jobs SUCCESS. Windows fixture cleanup preserves assertions and runtime;
final local rerun 869 cases / 866 PASS / 3 optional palm-assets SKIP / zero
failures/errors, 272.035s. Raw final reports, source hashes, initial failed runs
and target-device NOT_RUN gates: [stage-2 package](qa/portrait-v2-recovery/README.md).

## FEAT-009 stage 2 — 27 October 2026

Initial stage-2 local **869 run / 866 PASS / 3 SKIP / 0 failures/errors**, 261.246s;
the three skips require optional native palm assets (camera recovery, v2 palm
countdown and standalone palm inference). 47 focused stdlib-only checks PASS;
16 real-API/Sandbox fixture checks PASS. Native launcher rejects duplicate
ownership while UI runs, resumes after suspension and releases its lock after
teardown. Generated Ubuntu user unit passes systemd-analyze verification.
Source hashes, raw reports, review scope and manual Windows/Ubuntu gates are in
the [stage-2 evidence](qa/portrait-v2-recovery/README.md). No physical acceptance.
Prior API hangs were reproduced with command-network restriction; granting
network permission resolves the fixture without changing payment/API source.
Keep older failed reports below as dated evidence, not current unresolved tests.

## FEAT-009 stage 1 — 27 October 2026 local continuation

New-source validation and pending Windows/startup checks are tracked in the
[watchdog runbook](qa/portrait-v2-watchdog/README.md). Baseline `5639400`, working
tree changes; existing dated CI below does not cover this increment. User defers
manual device testing. Hardware/provider/cloud/startup sign-in checks NOT_RUN.
New-source checks: 22 focused PASS, 15 package-free PASS, native launcher
pause/resume/exit PASS; twelve synthetic render hashes/dimensions verified.
Full regression NOT VERIFIED: two terminated attempts, latest blocked in existing
API TestClient after 715 case starts. Separate unchanged Sandbox widget fixtures:
6 tests / 6 FAIL (`Worker did not settle`). Raw reports/stacks are in the runbook.

## Drive layout repair acceptance (26 October 2026)

Verify PB001/Photo/eight-digit-number/{raw,bw,color}, actual bytes and signed-out QR access after updating both Python and the existing Web App deployment. Automatic fixture passes do not close live delivery or BUG-009. See qa/drive-photo-layout/README.md.

Updated **26 October 2026** for `feature/portrait-kiosk-v2-next`.
Recorded execution evidence remains tied to its tested source. BUG-018 final
source has new automatic checks below; actual Windows/provider acceptance is
not inferred. Earlier audit-only evidence remains tied to its original source.

## Automated evidence ledger

| Evidence | Source and result | Limits |
| --- | --- | --- |
| Latest storage/content source | 53e7b4c: **824 full Python PASS / zero failures/errors/skips**, 24 Code.gs VM PASS; matching-source CI 40273343183 all three jobs SUCCESS | 28 final native captures + two form views; 133 CI PNGs verified. No real Google/paper/phone/provider acceptance. [Evidence](qa/feat-004-storage/README.md) |
| Foldering source audit, 26 October | Source `19e3f4d`: **38 existing-service tests PASS / zero failures/errors/skips**, 5.660s; temporary visit/pool/native-raster experiments PASS | Proves current behavior/gaps, **not** target implementation or live Drive readiness. `old` contents excluded/untouched. [Audit](qa/storage-layout-audit-2026-10-26/README.md) |
| Mirrored v2 output | `fc26e3d`: **808 full PASS / zero failures/errors/skips**, 230.670s; 42 focused PASS; 19 shared renderer/template checks PASS | Asymmetric all-twelve tests preserve QR/art/masks/original hashes and actual print path/copies; first 808-PASS source 977d26b kept separately. [Proof](qa/portrait-v2-mirrored-output/README.md) |
| Mirror visual/form checks | Sixteen clean-source native captures hash/dimension verified, eight selected native + two form views reviewed at 800×1280/452×900; browser 360px overflow check | Five fresh unchecked items, safe import/Submit/persistence/download; old P03 passes do not transfer. Actual paper/Windows NOT_RUN |
| Mirror final-source CI | [40263151709](https://github.com/pratikto/PhotoBooth/actions/runs/40263151709): all three jobs SUCCESS; delivery/retention/renderer 63 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/one optional model-assets skip | Skipped model case covered locally; Windows audio dummy output. [Raw proof](qa/portrait-v2-mirrored-output/README.md) |
| BUG-009 source repair/diagnosis | `887ba39`: **807 full Python PASS / zero failures/errors/skips**, 238.684s; 44 focused Python PASS; 19 actual-Code.gs VM PASS | Reproduced stale enabled flag/missing clock and setup accepting wrong trigger type. Original cleanup reused; no live Google setup/deploy/delete. [Raw evidence](qa/bug-009-retention/README.md) |
| BUG-009 Submit form | Eight fresh unchecked items; metadata/READY/forged pass fields do not pass cloud checks; partial Submit/persistence/download; 360/452/800px no overflow, zero browser errors | Form screenshots are synthetic fixtures, reviewed 800×1280/452×900. Windows/Google evidence NOT_RUN; no new twenty-cycle gate |
| BUG-009 matching-source CI | [40255716011](https://github.com/pratikto/PhotoBooth/actions/runs/40255716011): all three jobs SUCCESS; delivery/retention 44 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/one optional model-assets skip | Skipped model case covered locally; four clean-source native views reviewed at both required sizes. [Raw reports/visual manifest](qa/bug-009-retention/README.md) |
| Simpler photo entry | `20453fe`: **800 PASS / zero failures/errors/skips**, 217.888s; preliminary focused 55 PASS/two opt-in skips covered by final full run | Twelve clean-source PNGs verified; six idle/invitation/tutorial views reviewed at 800×1280/452×900. Windows spot checks NOT_RUN. [Raw proof/checklist/rollback](qa/portrait-v2-photo-entry/README.md) |
| Photo-entry matching-source CI | [40248962384](https://github.com/pratikto/PhotoBooth/actions/runs/40248962384): all three jobs SUCCESS; delivery 17 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/one optional palm-assets skip | Skipped model case covered locally; Windows audio uses dummy PCM. [Raw reports](qa/portrait-v2-photo-entry/ci-reports/) |
| Print/Drive final source | `266b2c8`: **800 PASS / zero failures/errors/skips**, 213.823s; 15 new-feature focused PASS | Linux/software GL/dummy PCM/offline assets; nine reused v1 files unchanged. Physical paper/phone/cloud acceptance NOT_RUN. [Raw proof](qa/portrait-v2-print-drive/README.md) |
| Print/Drive CI/screens | [40208966127](https://github.com/pratikto/PhotoBooth/actions/runs/40208966127): all three jobs SUCCESS; 133 PNGs source/hash/dimension verified | Delivery 17 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/1 optional model-assets skip covered locally; large right-panel QR screenshot pixels decode at both sizes |
| BUG-018 final source / full regression | `ebb53fd`: **785 PASS / 0 failure/error/skip**, 321.181s; focused 37 PASS | Two earlier MOCK fixture timeouts preserved; final helper drains an already-completed result, unchanged deadline/runtime. [Raw evidence](qa/portrait-v2-health-clicks/README.md) |
| BUG-018 matching-source CI/screens | [40189694738](https://github.com/pratikto/PhotoBooth/actions/runs/40189694738): all three jobs SUCCESS; 119 PNGs verified | Health 80 PASS, Sandbox 139 PASS, native 97 PASS/one optional model-assets skip covered locally. Required operator views reviewed; subsequent owner retest 4/4 at unknown HEAD, monitoring |
| Earlier operator full regression | `ea394e8`: **780 PASS / 0 failure/error/skip**, 270.671s | Linux/Python 3.12/Kivy 2.3.1, software GL/dummy PCM, synthetic I/O and supplied offline face/palm assets |
| Operator matching-source CI | [40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369), three jobs SUCCESS | Health 80 PASS; Sandbox 139 PASS; native 92 PASS/1 optional palm-model-assets skip, covered locally |
| Operator screenshot package | 119 PNGs verified against source/hash/dimensions; required views reviewed | Fifteen local operator PNGs also reviewed; all observations are fixtures |
| Earlier P5 full regression | `9433010`: **688 PASS / 0 failure/error/skip**, 211.646s | Earlier baseline, before health/report integration |
| P5 matching-source CI | [40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417), three jobs SUCCESS; 109 PNGs verified | Native optional model-assets skip retained; no merchant/hardware PASS |

[Operator raw outputs/manifests](qa/portrait-v2-operator-health/README.md) ·
[P5 raw outputs/manifests](qa/portrait-v2-p5/README.md).
CI job success does not imply all optional cases ran. Dummy playback and native
window rendering do not prove audible speakers or touchscreen accuracy.

## Owner reports

| Report | Recorded result and limits |
| --- | --- |
| BUG-018 targeted Windows retest, later 25 October | **4/4 checked, zero unchecked, no issue notes**. Repeated/mixed input, busy close, lifecycle and next input/restart owner-reported PASS; BUG-018 MONITORING. HEAD/OS/display/device fields remain unknown; specific tested resolutions not inferred. [Raw report and assessment](qa/portrait-v2-health-clicks/owner-retest-2026-10-25.json) |
| Initial Operator Device Health, 25 October | Raw 8/8 checked; issue note reports app hang with rapid clicks, clarified as all buttons pressed in combination. **Not clean PASS at that stage**; H03/H04 prompted the later targeted retest above. HEAD/OS/display/device fields unknown. [Record and four-item form](qa/portrait-v2-health-clicks/README.md) |
| Photo/preview/first-use buttons | 16/16 and twenty cycles, no issue notes; tested HEAD/device fields incomplete; [record](qa/portrait-v2-preview-redraw/README.md) |
| Game/header/resize | 14/14 and twenty cycles, unknown HEAD; video→video lag also reported at that stage; [record](qa/portrait-v2-native-controls/README.md) |
| Later typography/audio | 8/8 and “udah clear semua”, unknown HEAD; BUG-017 becomes OWNER-REPORTED PASS / MONITORING; [record](qa/portrait-v2-sandbox/owner-acceptance.json) |
| Windows preflight, 25 October | HEAD `0dc6555` → READY_FOR_MANUAL_TEST; stdout supplied, metadata JSON/P5 form not supplied; [record](qa/portrait-v2-p5/owner-preflight-2026-10-25.json) |
| Merchant/current integration/Drive cloud deletion | Complete new evidence not supplied; BUG-009 remains OPEN |

Keep accepted observations at their original metadata limits. Do not attach
unknown-HEAD reports to a newer source or formally close bugs from preflight.

## Consolidated outstanding acceptance — 26 October

[49-item combined checklist + Submit](qa/portrait-v2-pending-acceptance/windows-checklist.html)
covers current Windows integration, physical print/mirror, actual Drive/offline,
per-booth global/local cache, BUG-009 activation/expiry, official merchant
Sandbox/recovery, its twenty NEW integration cycles, privacy and operator review.
[Coverage/scope/run instructions](qa/portrait-v2-pending-acceptance/README.md) ·
[plain checkboxes](qa/portrait-v2-pending-acceptance/checklist.md).

Earlier owner PASS/monitoring and twenty local photo/game cycles stay recorded;
no new old-cycle gate or production action is inferred. All new checkboxes start
empty. Imported metadata/READY/CI does not pass physical/provider tests. Missing
Sandbox access leaves F/G NOT_RUN while other groups can proceed. G01/G02 require
twenty new Sandbox integration cycles, as the existing P5 form already did.
Public webhook, trusted provider game promotion, v1-specific audio/Settings and
unapproved production/repository operations remain separately scoped.

## Current manual forms

| Form | Purpose | Cycle rule |
| --- | --- | --- |
| [Mirror five-item form](qa/portrait-v2-mirrored-output/windows-checklist.html) | Live/review/strip/paper orientation, unchanged raw JPEGs, frame/QR and no replay | No new twenty-cycle gate; paper requires actual sheets |
| [BUG-009 eight-item form](qa/bug-009-retention/windows-checklist.html) | Existing project/setup/new-version deployment, safe status, authorized synthetic deletion and actual clock execution | No new photo/game cycle gate; READY/import does not pass cloud tests |
| [Print/Drive eleven-item form](qa/portrait-v2-print-drive/windows-checklist.html) | New automatic print, actual paper/phone download, offline queue/restart, layout/lifecycle | No new twenty-cycle gate; paper/phone items require actual evidence and start unchecked |
| [BUG-018 four-item form](qa/portrait-v2-health-clicks/windows-checklist.html) | Repeated/mixed operator clicks, close while busy, reopen/minimize and normal next input | No additional twenty-cycle run; fresh unchecked results |
| [P5 26-item form](qa/portrait-v2-p5/windows-checklist.html) | New Windows/Sandbox integration, metadata, source/device/provider/privacy gates | G01/G02 concern twenty cycles of the new integration; old photo/game reports do not pass these |
| [Operator eight-item form](qa/portrait-v2-operator-health/windows-checklist.html) | F12/hold, observations/refresh, resize, lifecycle and safe local report | No additional twenty-cycle photo/game requirement |

Run `python tools/check_portrait_v2.py`; import
`data/diagnostics/windows-readiness.json` into the form. Import fills metadata,
not pass checkboxes. Verify the actual kiosk display and supply missing camera/
speaker fields. Check only completed successful tests; blank means failed/not run.
Submit prepares text for chat; it does not transmit it automatically.

Use [root launch instructions](../README.md) for local/MOCK modes and
[Sandbox runbook](qa/portrait-v2-sandbox/README.md) for the isolated merchant trial.
Leave unavailable provider/device checks NOT_RUN; preserve journals and reconcile
uncertain orders rather than replaying charge/capture/print.

## Remaining external evidence

Actual merchant simulator create/status/settlement/cancel/restart/outage behavior;
current Windows touch/scaling/camera/speakers/video and prolonged use; ordinary
opt-in physical printing and uncertain-send recovery; Drive/download/offline
synchronization, privacy and 30-day cloud deletion; explicit release signoff.

A public HTTPS webhook is a separate deployment/operational scope, not a
prerequisite for the current loopback launcher and simulator/polling trial. It
has not been deployed or acceptance-tested. Trusted QRIS game promotion is also
separate: the current Sandbox uses full-price consent.

## Recording new evidence

Record date, exact source/dirty state, OS/dependencies/display/device, command or
manual steps, PASS/FAIL/SKIP/NOT_RUN, observation and limits. Exclude secrets and
customer photos. Distinguish automated source results, owner reports, preflight,
merchant acceptance and physical acceptance. Keep dated failures when recording
later successful retests. [Current bugs](bug_tracker.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/test_checklist.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

