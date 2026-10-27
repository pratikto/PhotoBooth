# Meong Photobooth — Bug register

## BUG-019 — incoming carousel strip absent during held drag (27 October)

S2 visual degradation. Owner screenshots show a blank incoming side before
pointer release. Five-slot/three-texture mismatch reproduced; source correction
retains five cached neighbours. Native held/reverse/wrap checks PASS; exact owner
HEAD and Windows/Ubuntu acceptance remain unknown. IN SOURCE / device retest
pending, not CLOSED. [Correction and evidence](qa/portrait-v2-carousel-hold/README.md).


## 27 October — delivery logging recursion recurrence

Owner reports >10 minutes and supplies RecursionError timing; new queued work
has no worker_start in the extract. Old-folder BIND_FOLDER_CONFLICT is confirmed
for one transaction. Real-Kivy console-active reproduction exposes root/stderr
logging recursion missed by earlier console-disabled QA. Timing now uses the
session file directly, contains sink failures/re-entry, and v2 defaults to MIXED
logging with native diagnostics retained. 54 targeted tests PASS; final checks
are recorded in the [correction runbook](qa/drive-delivery-performance/LOGGING.md).
Code.gs unchanged; no redeploy, reset or known-folder replacement is required.

## 27 October — delivery timing follow-up

Owner reports faster uploads and supplies runtime timings: successful session
122.719s to QR, including 70.782s overlapping old bind attempts. Three old
transactions repeatedly reach a successful bind response then local ValueError;
exact cause unproven. Bounded recovery/backoff and typed diagnosis are published at 8578825;
actual old-folder conflict repair remains unverified and is not automated.
[New source/evidence/retest](qa/drive-delivery-performance/RETRY.md). Original
five-minute incident and BUG-009 cloud deletion remain separate open evidence.

## Delivery latency / result input follow-up — 27 October 2026

Owner reports >5 minutes before large QR, then verified Drive with disabled
Finish/processing footer; printing intentionally disabled. No duration log or
exact failing-source/device evidence is available. Source/controlled tests confirm
maintenance can delay a customer and snapshot busy-state can persist in rebuilt
result controls. Bounded source fixes are in 58dc76f/2e140c1; actual five-minute
root cause is **unproven**, device retest pending. Related FEAT-004/FEAT-022 and
BUG-009 delivery work; privacy deletion BUG-009 stays OPEN. Prior private-link
incident below remains separate evidence. [Tests/runbook](qa/drive-delivery-performance/README.md).

## Drive photo delivery recurrence — OPEN (26 October 2026)

Owner reports private printed QR, empty folder and GUI waiting on upload. Meong account confirms the reported folder is empty and lacks anyone-reader access. Source correction prepared; installed backend version/logs and successful live delivery remain unverified. See docs/qa/drive-photo-layout/README.md.


**26 October BUG-009 continuation:** owner resumed this repair and says setup/
redeployment has not been confirmed. Sources **130aae1 / 887ba39** repair real
CLOCK activation/setup and add safe existing-config diagnosis. **807 full Python
PASS/zero skips, 19 Code.gs VM PASS**; two source defects reproduced before fix.
The installed project's activation and actual eligible synthetic deletion are
still unverified: **OPEN — awaiting cloud evidence**, not CLOSED or still deferred.
That retention-only source increment did not include FEAT-004 sync. The owner
now links the [foldering/global-cache target](photobooth-storage-layout.md) to
FEAT-004 ads + BUG-009. The coordinated source is now implemented at 53e7b4c
(824 full Python PASS/zero skips, 24 Code.gs VM PASS, matching three-job CI
SUCCESS); actual deletion evidence stays separate. The [combined pending
checklist](qa/portrait-v2-pending-acceptance/README.md) records actual gates. [Current guide/proof](qa/bug-009-retention/README.md).

**Current GUI v2 context — 25 October 2026:** latest print/Drive source
`266b2c8` has 800 full local PASS/zero skips, matching three-job CI SUCCESS and
133 verified PNGs; actual paper/phone/cloud acceptance pending. Earlier operator
`ea394e8` has 780 full local PASS/zero skips; matching-source CI succeeds with
one optional native model-assets skip covered locally. `9433010`/688 tests is
the earlier P5 baseline. Preflight `0dc6555` ready is not physical/provider PASS.
BUG-012/013/014/015/016/017 retain owner-reported monitoring, with missing tested
HEAD/device fields kept unknown. BUG-009 remains OPEN; v1 BUG-001/007 stay separate.
Read-only Device Health/report is now in source, not the next unimplemented feature.
[Current status](FEATURE_STATUS.md) · [test ledger](test_checklist.md).

The stable IDs and dated evidence below are preserved. Historical v1 reports
and prior CI counts apply to their original source, not current v2 acceptance.

**Severity:** S0 = unsafe/payment integrity/data loss/kiosk unusable; S1 = core customer session cannot be completed; S2 = material degradation or workaround required; S3 = cosmetic or nonblocking. Higher execution priority may be assigned to customer-flow failures even when individual severities remain provisional.

## CI-only QA issue — separate from operational bugs

**QA-QR-001 (CI-only, P1 stabilization, now MONITORING):** Random DEMO QR attempt UUIDs changed module patterns on each synthetic Kivy screenshot render. GitHub's one-scale OpenCV decoder intermittently failed despite no observed laptop issue. Test-harness-only commit [`e46812b8`](https://github.com/pratikto/PhotoBooth/commit/e46812b8c9f66c548bccebb1e9fc45e3c89afeef) uses deterministic synthetic IDs and bounded screenshot-pixel decoder scales, preserving exact payload assertions and negative QR tests. **Kiosk CI 3/3 SUCCESS** at `e46812b8`: [run 39178452927](https://github.com/pratikto/PhotoBooth/actions/runs/39178452927) with **233 PASS / 2 SKIP and 87 screenshot PASS** each. [Detailed QA record](qa/KIOSK-GUI-REGRESSION-2026-10-18.md). This is **not BUG-003** (QR printing) and not a production failure; monitor future regression runs.

## Current bug queue — operational defects first

BUG-001/002/003/004/005/006/007/008/010/011 rows retain their v1/shared-service
context. A v1 Settings/QR-slip or lab control is not automatically a v2 screen.
The v2-specific monitoring rows and BUG-009 boundary below remain current.

Active defects and deferred retests appear first. Monitoring items and owner-reported passes remain in the register for traceability and possible formal closure, **not as active fix tasks**.

| ID | Latest report / observed impact | Severity | Source vs device status | Next action / evidence |
| --- | --- | --- | --- | --- |
| **BUG-018** | Initially the app reportedly hung after rapid combined Device Health clicks despite raw 8/8. Later targeted R01–R04 retest: **4/4 checked, zero unchecked, no issue notes** on 25 October. | S1 historical/provisional | **OWNER-REPORTED PASS / MONITORING**. Source correction `ebb53fd` has 785 full PASS/0 skips and matching-source three-job CI SUCCESS; the owner's tested HEAD/device fields remain unknown. | Preserve initial failure and later [owner retest](qa/portrait-v2-health-clicks/README.md). No new patch or repeated twenty-cycle gate; investigate only recurrence. Exact-source verification/formal closure and external P5 gates remain separate. |
| **BUG-017** | Owner reports lag specifically switching advertising video→video; video→image and image→video are reported okay. Entered in the lag field; notes box empty. | S2 provisional (duration/frame impact unknown) | **OWNER-REPORTED PASS / MONITORING (2026-10-24).** | Final typography retest V01/V02 checked and owner confirmed “udah clear semua”. Tested HEAD/device metadata and measured latency unknown; no decoder patch or root cause claimed. Preserve prior report. [Acceptance](qa/portrait-v2-sandbox/owner-acceptance.json). |
| **BUG-016** | Owner screenshots show Meong too far right after resize; native landscape reproduction puts its body at 80.12% width. | S2 | **OWNER-REPORTED PASS / MONITORING (unknown HEAD); source fix 848a52d.** | Center the complete original world; preserve speed, wave spacing, sprite/collision/film geometry. 20 focused native PASS; final follow-up 540 full PASS/zero skips and 45 synthetic game captures verified. [Evidence](qa/portrait-v2-player-anchor/README.md). |
| **BUG-015** | Owner reports fast mini-game and wave spacing shrinking after responsive layout. Source reproduces piecewise displayed speed (up to 2.437× near speed at 800×900). | S2 | **OWNER-REPORTED PASS / MONITORING (unknown HEAD); source fix 144bd60.** | Replace nonlinear layout projection with uniform world translation; original speed/spawn constants unchanged. Test actual rendered travel and wave spacing, not only static images. [Evidence](qa/portrait-v2-motion-correction/README.md). |
| **BUG-013** | Historical v2 preview lag while v1 was smooth and first-use page buttons needed extra taps. After the source corrections, owner submits all sixteen focused checks and twenty cycles with no issue notes. | S2 historical | **OWNER-REPORTED PASS / MONITORING (2026-10-23); EXACT-SOURCE ACCEPTANCE UNVERIFIED.** | Preview without touch/countdown, first-use buttons and twenty-cycle/restart checks are explicitly checked. `0d08f07`/`ef0fcb0` remain verified source checkpoints (353 prior full PASS); tested HEAD/device fields are blank, so do not assign the owner result to these SHAs or formally close/release. No new patch while working. [Acceptance and audit](qa/portrait-v2-preview-redraw/README.md). |
| **BUG-014** | Optional open-palm was absent before correction. Owner checks I01–I06 in the earlier forty-item report and B04 in the latest sixteen-item report as working. | S2 historical | **OWNER-REPORTED PASS AT UNKNOWN HEAD / MONITORING; EXACT-SOURCE ACCEPTANCE UNVERIFIED.** | Existing hold/release policy shares the v2 SIAP countdown. Latest twenty-cycle report has no issue notes; no new palm patch or repeat-test requirement is inferred. Preserve blank HEAD/device metadata and monitor regression. [Latest acceptance](qa/portrait-v2-preview-redraw/README.md). |
| **BUG-012** | Portrait GUI v2 previously exited returning to advertising (original V4: 33/35 checked, five cycles, unknown HEAD). After the correction/diagnostic retest instructions the owner says “sudah oke”. | **S1 historical/provisional** | **OWNER-REPORTED PASS / MONITORING (2026-10-23)**; not formally CLOSED. Exact post-update HEAD/cycle count and original native exit cause remain unverified. | Monitor without another speculative patch. Later owner P3/game reports include twenty cycles; preserve them at unknown HEAD without requesting another old gate. Collect diagnostic log/exit code if crash recurs; new Sandbox P5 cycles are separate. [Confirmation and evidence](qa/portrait-v2-return-ad-crash/README.md). |
| **BUG-011** | FEAT-001 previously printed **fewer/different physical sheets than the selected copy quantity**, while DEMO pricing was correct, on the owner's Windows photobooth. After the documented printer fixes, the owner first said **"sip udah bener"** and subsequently explicitly confirmed **"bug 11 udah aku test dan lolos"**: the selected copy quantity now matches the physical printer output according to the owner's hands-on test. The original requested/actual count and precise retest SHA/driver were not provided. | **S1 historical/provisional** (core print-fulfillment impact before patch) | **OWNER TESTED PASS — MONITORING (2026-10-18); NOT formally CLOSED/RELEASED.** In-source fix: the Windows RAW path now uses `EndDocPrinter` before one `ClosePrinter` ([`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93)); `copies=N` is sent as one RAW document containing N identical ESC/POS image+cut streams ([`4608fcc9`](https://github.com/pratikto/PhotoBooth/commit/4608fcc9ec96c8eabeb01ddbd64059830af2bf62), [`e6d2f684`](https://github.com/pratikto/PhotoBooth/commit/e6d2f6840d4b5838e719f904bcc3b8443291193a)). **Targeted GitHub CI [39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707): 15/15 PASS** (11 quote/session/manifest + 4 mock payload/spool). **Owner's explicit on-device TESTED PASS is separately recorded**; no full Kiosk GUI CI PASS or production release implied. | **No active fix needed; owner tested successfully on the Windows booth. Monitor regression without modifying stable printing code.** If the discrepancy returns, record requested/physical sheets, tested local SHA, transport and Windows spool queue; avoid automatically retrying ambiguous partial sends. For formal closure, log per-case 1/2/3 copies and mixed-template physical evidence, full applicable regression results and owner closure decision. See [comprehensive FEAT-001/BUG-011 acceptance record](qa/FEAT-001-BUG-011-acceptance.md). |
| **BUG-009** | **Drive retention registration/activation failure:** 30-day cloud deletion is not yet verified. Original Windows setup/redeploy warnings preserved. | S1 (provisional; cloud privacy/retention risk) | **OPEN — SOURCE REPAIRED / CLOUD EVIDENCE PENDING, owner resumed 2026-10-26.** Existing v1 cleanup is reused. Stale enabled-flag acknowledgement and setup accepting a non-clock trigger reproduced and corrected at 130aae1; safe read-only status/diagnostic delivered at 887ba39. Owner says setup/deployment has not been confirmed. | Verify installed version, owning-account hourly trigger and scoped synthetic cloud deletion after setup/deployment. No live Google configuration/access in the cloud workspace. Retain v2 upload holds, original deadlines and separate photo/ad folders. Source tests/status alone do not close the bug. Coordinate the owner-linked FEAT-004 foldering/global-cache and new retention paths, with independent sync/deletion evidence; this integration is now implemented at 53e7b4c, while real-account acceptance remains pending. [Current repair/evidence](qa/bug-009-retention/README.md). |
| **BUG-001** | Music is still inaudible in tutorial/layout, despite `SoundSDL2 state=play gain=0.59`; button and shutter effects ARE audible in the same GUI | S2 | **PATCHED IN SOURCE — owner audio retest required**; 2026-10-18 code now reacquires music playback after ad fade and on explicit audition. Actual audible output unverified | On Windows pull updated GUI, start from idle ad -> tutorial -> layout, listen for continuous BGM without entering Settings; test music mute/re-enable and check output with `Uji Musik`. Preserve ad mute and SFX; record SHA, sound/mixer and device result |
| **BUG-007** | Owner now confirms all three `Uji` buttons receive taps: Music made only the generic click, Button made click, Camera made shutter. GUI reports accepted callbacks | S2 | **OWNER REPORTED PASS for tap handling; PATCHED IN SOURCE for sample isolation; physical retest pending** | Check `Uji Musik` audibly restarts music without a click, `Uji Tombol` one button cue, and `Uji Efek Kamera` one shutter cue. The playback-request status is not speaker confirmation |
| **BUG-008** | Settings/config popup **previously** opened slowly or seemed to hang. On 2026-10-18, the owner reports Settings is **responsive again** on their local Windows application, without an identified intervention or reliable explanation. | S2 (historical/provisional) | **MONITORING — OWNER REPORTED PASS (2026-10-18); not CLOSED.** No new Settings fix or instrumented reproduction; root cause, triggering conditions and reason for recovery are **unknown**. Removed from active repair queue. | **Do not change working Settings code** just to address this historical symptom. Watch for recurrence; if reproduced, capture branch SHA, screen path (gear/main Settings vs Audio/Printer), click-to-display delay, video/background workload and relevant logs. Investigate only with separate approval; formal closure awaits recorded repeatable owner acceptance evidence. |
| **BUG-004** | Thermal photo-strip previously printed blurry / low quality; the owner now says the result is **OK** after the approved Floyd profile was added to the GUI. | S2 (historical impact) | **OWNER REPORTED PASS (2026-10-18) — removed from active fix queue.** Approved Floyd tuning is in `photobooth/printer.py` ([commit `06370660`](https://github.com/pratikto/PhotoBooth/commit/06370660e024baf070145c0fc8796621b1cae7d6)); improved quality is the owner's latest Windows feedback, not an independently captured comparative paper test. **Not formally VERIFIED/CLOSED.** | For formal closure, record tested commit/config, physical paper photograph or comparison, actual print width and owner acceptance evidence; retain regression tests and `PHOTOBOOTH_PHOTO_TUNING=legacy` rollback if needed. |
| **BUG-010** | Three-column dithering GUI formerly clipped lower sliders and the print/save controls; owner now says Windows GUI scrolling is **OK**. | S2 (historical impact) | **OWNER REPORTED PASS (2026-10-18) — removed from active fix queue.** Scrollable parameter columns and visible actions are patched in source ([commit `f3d836d`](https://github.com/pratikto/PhotoBooth/commit/f3d836d40f599e80ed0a844a9974bdd1b548f598)). Detailed screen-size/scroll evidence and local tested SHA have not been supplied; **not formally VERIFIED/CLOSED**. | For formal closure, document minimum/window-maximized layout, wheel/scrollbar access to all sliders including Threshold, Print Test/Save PNG visibility, tested SHA and owner acceptance; regression after GUI layout changes. |
| **BUG-002** | Video advertisements on both idle and payment now play according to owner | S2 | **OWNER REPORTED PASS — removed from active fixes**, formal closure needs version/evidence | Regression-check actual frames on both screens after audio change; payment stays muted |
| **BUG-003** | Owner confirms payment-page QR slip now physically prints | S2 | **OWNER REPORTED PASS — removed from active fixes**, QR scan and formal closure pending | Verify paper QR scans the intended DEMO payload, including quiet zone; no claim of live payment |
| **BUG-005** | Owner confirms ad → tutorial → layout navigation is satisfactory | S2 (provisional) | **OWNER REPORTED PASS — no active repair** | Keep manual/face paths in later end-to-end regression |
| **BUG-006** | Owner confirms opening advertisement sizing/display is satisfactory | S3 | **OWNER REPORTED PASS — no active repair** | Recheck responsive layout on future visual changes |

## Current execution context

Monitor reported-working paths and prioritize reproducible failures. Read-only
health/report source work is completed; actual operator/P5/merchant acceptance
is separate. BUG-009 remains unresolved. Refer to the [current backlog](next_step.md)
for follow-up; the old failed CI and FEAT-008 candidate ranking below are historical.

<details>
<summary>Historical v1 reports and execution ranking — 18 October 2026</summary>

These statements retain their original date/source. Later source/CI and owner
reports above supersede old active-fix rankings and failed-CI gates.

**Execution ranking (reassessed 2026-10-18 after the owner's successful print retest):** **BUG-011 leaves the active repair queue** and becomes **MONITORING — OWNER TESTED PASS**; the requested-copy/paper discrepancy is reported resolved after printer-source fixes, but formal closure/release remains subject to per-case device evidence and full GUI regression. **BUG-009 stays OPEN / provisional S1** for unresolved 30-day Google Drive photo privacy retention, deferred by owner to FEAT-004; this risk is not cancelled by the print success. BUG-001/007 audio remain deferred; BUG-008 Settings MONITORING; BUG-004/010 and BUG-002/003/005/006 owner-reported passes. [Kiosk GUI CI 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) on `f2f52e33` **FAILED** (full unittest step); evaluate independently before release. The next normal feature candidate remains FEAT-008 device health, subject to explicit approval and quality gates.

## Latest owner feedback and CI distinction — 2026-10-18 (documentation only)

- **Latest full Kiosk GUI quality gate (2026-10-18):** Owner-approved QA-only iteration has **VERIFIED CI PASS at source/test SHA `f129dd9e`**: [Actions 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476), **230 unit-test PASS + 2 skipped, 0 failures/errors, 87 synthetic GUI render PASS**. Historical CI FAIL lines below are **dated pre-repair history, not present current-app failures**. Scope was existing test expectations, runner and workflow—not production app code or Windows device acceptance. Root cause and committed repairs are documented [here](qa/KIOSK-GUI-REGRESSION-2026-10-18.md). This does **not** close BUG-009 or deferred audio or certify release.
- **BUG-011 initial failure → explicit successful user test (2026-10-18):** Pricing was correct while paper count was wrong; missing `EndDocPrinter` and separate spool jobs were corrected. After initially reporting **"sip udah bener"**, owner explicitly stated **"bug 11 udah aku test dan lolos"**. This is affirmative **hands-on OWNER TESTED PASS**, not merely an inference that the UI looks normal. Mark **MONITORING**, not formally CLOSED/RELEASED; local SHA, per-case count log and printer configuration were not provided. Targeted 15/15 mock CI PASS remains a distinct type of evidence. Full details: [FEAT-001/BUG-011 QA](qa/FEAT-001-BUG-011-acceptance.md).
- **BUG-009 owner scheduling decision (2026-10-18):** defer corrective action and coordinate it with future FEAT-004 per-machine Google Drive advertising synchronization. A shared `Code.gs` review/deployment is planned; **retention setup may only require enabling/redeploying existing functionality**, not a retention source-code patch. Both workflows need independent acceptance; no actual backend change, new code, deployment, test, or deletion is authorized by this documentation request. The unresolved 30-day-photo-expiry/privacy risk stays visible.
- **BUG-008 new owner update (2026-10-18):** Settings now opens/responds smoothly in the local application; the owner does not know why the earlier slowdown/hang disappeared. Classify **MONITORING — OWNER REPORTED PASS**, not VERIFIED/CLOSED or fixed-in-source. No evidence of a Settings code change, captured click-timing regression, or proven connection to Drive-retention traffic. Do not patch Settings while it is working; capture evidence only if symptoms return.
- The owner explicitly replied **"udah oke"** to BUG-004 thermal photo image quality and BUG-010 scrolling/access to dithering settings. Record both as **OWNER REPORTED PASS**, without claiming a new test command was run here or that exact tested SHA/screen measurements/physical paper comparisons were captured. Their prior failed states are retained as historical reports.
- The owner also reports the **application/regression runs successfully on local Windows**. Exact local command(s), complete test counts/output, local checkout SHA and coverage were not supplied; this is **OWNER-REPORTED LOCAL WORKS**, **not a verified full unittest suite pass**.
- At the GitHub branch baseline [`8bd5b58`](https://github.com/pratikto/PhotoBooth/commit/8bd5b58cc789fcc63b43e08e7eb9fc1c48dbe3f7), the [Dither tuning lab regression](https://github.com/pratikto/PhotoBooth/actions/runs/39120913800) completed **PASS**, while the [Kiosk GUI regression](https://github.com/pratikto/PhotoBooth/actions/runs/39120913854) completed **FAIL** in its automated test stage. GUI syntax and synthetic rendering stages succeeded; the failing test identity was not established from available logs. Local operational success does not silently override the GitHub workflow status.
- No new Windows hardware test, CI rerun, application-code modification, deployment, merge or release was performed to make this documentation update. A separate owner-approved scope is required for repairs or other document reconciliation.

## Known reproduction context (not independent verification)

- Environment in earlier reports: Windows, Python 3.12, Kivy 2.3.1, POS80ENG/POS80 Printer USB queue. Confirm active device name and persisted `data/printer_settings.json` at next test. Some earlier Windows logs referenced `/dev/usb/lp0` before printer settings were configured.
- Earlier sound probe `python tools/check_audio_output.py` was audible while normal `python main.py` was not. This narrows investigation to app lifecycle/routing, not proof of exact root cause.
- Earlier photo-print job physically yielded a Meong layout and looked blurry; this report is **historical**, superseded by the owner's 2026-10-18 quality-is-OK feedback after Floyd tuning. Owner separately confirmed QR-slip paper print works. Preserve older failures as history, not current status.
- **New evidence 2026-10-18, owner-shared Windows `python main.py` captured terminal log (redacted here):** Kivy 2.3.1 / Python 3.12.10, repeated `Drive retention registration failed` warnings for multiple transaction manifests and repeated Google Apps Script HTTP calls. Also shows `Meong audio test tapped: music/button/shutter` and `Music playback restarted at gain 0.59`. Log lacks timestamped Settings click/render spans and any Python traceback establishing the exact UI stall; a PowerShell `NativeCommandError` wrapper around stderr startup logs is not itself evidence of an app exception. One MP4 image-loader error appears, but the owner reports video ads work, so do not mislabel BUG-002 reopened without confirmed playback regression. No credentials or response URLs should be copied to this public repo.
- Relevant code reviewed read-only: `photobooth/ui_kivy.py::show_settings_menu/show_audio_settings/show_printer_settings`; `drive_sync.py::DriveSyncWorker` runs periodic network work on a background thread; `retention.py::register_drive_retention` logs registration errors and preserves manifest error state; `drive_storage.py::AppsScriptDriveClient.register_retention` requires retention backend acknowledgment. None proves BUG-008 is directly caused by BUG-009.
- Historical QA reported native sound/video test passes using fixtures and mock devices, plus a local 172-test run with failures caused in part by local merge artifacts. Do **not** transfer these results to current device acceptance. See [FEATURE_STATUS.md](FEATURE_STATUS.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and [docs/qa](qa/README.md).


</details>

## Per-bug closure requirements

1. Reproduce and record: branch commit SHA, OS/Python/Kivy, media/device config, steps, expected vs actual, terminal output/screenshot or physical evidence.
2. Trace root cause; distinguish what source implements from what it does on actual printer/speakers/camera.
3. Verify that the fix/commit is within an owner-approved scope; do not ask again for an already authorized small change. Use a focused fix, applicable checks and rollback pointer. New unrelated scope needs its own instruction.
4. Mark **FIXED IN SOURCE** only after code change; **VERIFIED** only after documented applicable tests including physical confirmation where needed; **CLOSED** only after owner acceptance.
5. Distinguish local DEMO/MOCK, merchant Sandbox and production. A QR on paper or a local confirmation button is never proof of provider settlement.

## New bug entry template

### BUG-XXX — Symptom (stable ID)
- Severity S0/S1/S2/S3; priority and rationale; status OPEN/REPRODUCED/FIXED IN SOURCE/VERIFIED/CLOSED/BLOCKED:
- First reported / last reproduced; environment, target commit and device:
- Expected behavior vs actual:
- Reproduction steps and associated logs/images:
- Suspected area vs *proven* root cause:
- Dependencies / related FEAT IDs:
- Explicit fix approval, tests run, on-device verification and rollback commit:

