# Meong Photobooth — test evidence and acceptance

Updated **25 October 2026** for `feature/portrait-kiosk-v2-next`.
Recorded execution evidence remains tied to its tested source. BUG-018 final
source has new automatic checks below; actual Windows/provider acceptance is
not inferred. Earlier audit-only evidence remains tied to its original source.

## Automated evidence ledger

| Evidence | Source and result | Limits |
| --- | --- | --- |
| BUG-018 final source / full regression | `ebb53fd`: **785 PASS / 0 failure/error/skip**, 321.181s; focused 37 PASS | Two earlier MOCK fixture timeouts preserved; final helper drains an already-completed result, unchanged deadline/runtime. [Raw evidence](qa/portrait-v2-health-clicks/README.md) |
| BUG-018 matching-source CI/screens | [40189694738](https://github.com/pratikto/PhotoBooth/actions/runs/40189694738): all three jobs SUCCESS; 119 PNGs verified | Health 80 PASS, Sandbox 139 PASS, native 97 PASS/one optional model-assets skip covered locally. Required operator views reviewed; Windows hang retest pending |
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
| Operator Device Health, 25 October | Raw 8/8 checked; issue note reports app hang with rapid clicks, clarified as all buttons pressed in combination. **Not clean PASS**; H03/H04 responsiveness/lifecycle require targeted BUG-018 retest. HEAD/OS/display/device fields unknown. [Record and four-item form](qa/portrait-v2-health-clicks/README.md) |
| Photo/preview/first-use buttons | 16/16 and twenty cycles, no issue notes; tested HEAD/device fields incomplete; [record](qa/portrait-v2-preview-redraw/README.md) |
| Game/header/resize | 14/14 and twenty cycles, unknown HEAD; video→video lag also reported at that stage; [record](qa/portrait-v2-native-controls/README.md) |
| Later typography/audio | 8/8 and “udah clear semua”, unknown HEAD; BUG-017 becomes OWNER-REPORTED PASS / MONITORING; [record](qa/portrait-v2-sandbox/owner-acceptance.json) |
| Windows preflight, 25 October | HEAD `0dc6555` → READY_FOR_MANUAL_TEST; stdout supplied, metadata JSON/P5 form not supplied; [record](qa/portrait-v2-p5/owner-preflight-2026-10-25.json) |
| Merchant/current integration/Drive cloud deletion | Complete new evidence not supplied; BUG-009 remains OPEN |

Keep accepted observations at their original metadata limits. Do not attach
unknown-HEAD reports to a newer source or formally close bugs from preflight.

## Current manual forms

| Form | Purpose | Cycle rule |
| --- | --- | --- |
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
