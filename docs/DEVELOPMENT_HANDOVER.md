# Meong Photobooth — GUI v2 development handover

**Android verification continuation (28 October):** runtime APK metadata/permission/ABI
checks and nested ELF rejection fixtures are now implemented in the existing
Android build workflow. Current cloud regression/build/access evidence and
remaining device gates: [continuation record](qa/android-runtime/continuation.md).
This is not a new APK or Android hardware PASS.

**Android runtime continuation — 28 October 2026:** Continue Android camera/USB OTG/Sandbox parity at the same branch. Portable c001095 reuse is pushed at 795b64c; current native/runtime stage has focused source checks and a new full regression/build in progress. Preserve the named pre-restart evidence stash and all app-private journals.
[Scope, setup and source evidence](android-v2-runtime.md).

## Android A1 continuation — 27 October

Current owner request continues **feature/portrait-kiosk-android**, no new branch,
through APK build readiness using the current GUI v2. Base c10f9dd; desktop
reference a62721f refreshed read-only. Shared app/gallery and their regression
tests reuse the exact eb0297d five-picture correction. Package original .b85 game
art (missing from A0 staging), preserve Back/game state, pin p4a/NDK/API and
provide a local-cache build helper plus manual APK workflow. Focused package/
native checks pass. Source 293b22b compiled a signed 42.7 MB debug APK:
valid signature, no requested permissions, 144 ARM ELF libraries, 65 exact
assets, twelve masters/game artwork and 16 KB alignment verified. Matching
preview CI 40495526267 SUCCESS. Evidence closure was published 28 October.
The last recovered full local run is 881 cases / 878 PASS / 3 optional palm
SKIP at 6260435; the later 293b22b full summary remains unrecovered after cloud
restart. Do not promote that run to PASS. Build/policy/CI checks are independent.
Next is actual Android install/touch/keyboard/Back/Home/private-persistence QA,
then the native A2 camera bridge. This offline preview keeps camera, audio/video,
print, Drive and provider services off; it is not full Android hardware parity.
[Scope, reviewed documents, commands and results](android-build-readiness.md).

## Android branch continuation — 27 October

A0 source `0cacc27` pushed/remote verified; matching Android-preview CI
40425864227 SUCCESS. Full 875 local cases: 872 PASS, 3 optional palm-assets SKIP,
zero failures/errors, 266.642s. Evidence-only second push follows. Next Android
stage: SDK/NDK/recipe and APK validation, then actual device tests; not completed
by Linux renders. [Final evidence](android-development.md#final-a0-evidence-and-staged-publication).

Owner explicitly requests a new branch, parallel Android development and staged
pushes. `feature/portrait-kiosk-android` forks `fcabfbb`; desktop stays on
`feature/portrait-kiosk-v2-next`. Read [Android review/scope/commands](android-development.md)
before changes. A0 reuses the actual UI/game/templates, directs state to private
app storage, gates unavailable hardware and stages only approved source/assets.
Five policy checks and native 452×900/800×1280 UI reuse checks pass. Full
regression/Android-preview CI are recorded separately; APK/SDK/device NOT_RUN.

**Final published checkpoint, 27 October:** FEAT-009 source `f023029` is on the
required branch; matching [CI 40423003641](https://github.com/pratikto/PhotoBooth/actions/runs/40423003641)
has all three jobs SUCCESS. Windows fixture connections are explicitly closed
before database replacement; production runtime is unchanged from `b99c613`.
Final local rerun: 869 cases, 866 PASS, three optional palm-assets SKIP, zero
failures/errors, 272.035s. [Final proof](qa/portrait-v2-recovery/final-verification.json).
Docs-first primary rule and Windows-development/Ubuntu-deployment direction
are persisted in AGENTS/protocol/prompt. Next: actual target-device acceptance;
automatic restart remains off and no service was installed.

## Current — 27 October FEAT-009 stage 2 and primary working rule

Owner requires comprehensive/careful documentation review before code, then
documentation updates after code. Persisted in AGENTS, protocol and continuation
prompt. Windows is development; Ubuntu mini PC is deployment. Continue on this
branch; read [stage-2 review/runbook](qa/portrait-v2-recovery/README.md) first.
Current source adds read-only recovery review, pre-GUI watchdog holds,
per-checkout launcher ownership and Ubuntu graphical-session unit generation.
No automatic restart, replay, service installation or production/deployment.

Remote refresh works with network permission; synchronized remote `a7815d9`
(includes Drive/QR repair `0bd69a9`) before rebasing the unpublished watchdog
checkpoint to `ae5c62a`. Do not undo the current cloud numbered-Photo correction.
The older source/ordering paragraphs below are dated historical checkpoints.
Initial stage-2 local regression: **869 run / 866 PASS / 3 optional palm-assets SKIP /
0 failures/errors**, 261.246s. Focused 47 PASS with site packages disabled;
API/Sandbox 16 PASS and actual native launch/pause/resume/lease/exit PASS.
Earlier HTTP stalls reproduce under restricted command-network access and clear
with network permission; no payment/fixture code patch was needed. Raw old
failures stay preserved. [Current evidence/limits](qa/portrait-v2-recovery/README.md).

Ubuntu mini-PC/Windows hardware, graphical sign-in/service start, paper, actual
merchant and Google deployment/retention acceptance remain NOT_RUN. No source
success grants release or closes BUG-009. Future FEAT-009 automatic recovery
requires a durable safe-idle contract; the current unit deliberately uses Restart=no.

**Historical stage-1 checkpoint (before stage 2):** user requests next roadmap
development while manual tests wait. FEAT-009 stage 1 adds an opt-in external
liveness observer and Windows startup-script generator. It never kills/restarts
the kiosk or replays fulfillment. Ordinary launch behavior is retained; merchant
Sandbox keeps its dedicated launcher. Base `5639400`; remote refresh currently
fails because the configured proxy is unreachable. No push/CI claim.
[Scope, commands, limitations, acceptance and rollback](qa/portrait-v2-watchdog/README.md).
Focused 22 PASS, package-free 15 PASS and actual native launcher lifecycle PASS;
full suite NOT VERIFIED (blocked in existing API TestClient), isolated Sandbox
widget checks 6 FAIL (`Worker did not settle`). Trace/raw reports preserved in
the runbook; no full-source certification or payment fix is claimed.
Earlier latest-source references below describe the prior committed baseline.

## Latest Drive/QR repair (26 October 2026)

Continue from the correction in docs/qa/drive-photo-layout/README.md. The earlier per-transaction-root cloud tree is superseded by owner instruction. The existing Web App needs a new deployment version; this session performed read-only Drive inspection only.

Updated **26 October 2026**. Repository `pratikto/PhotoBooth`; required branch
**`feature/portrait-kiosk-v2-next`**. Documentation baseline **`f36ebad`**, latest functional
source **`53e7b4c`** (coordinated per-booth storage/content; mirror `fc26e3d`, BUG-009 `887ba39`, print/Drive `266b2c8`). Refresh remote HEAD before continuing. GitHub's default is
still `master`; `main.py` launches v1. Do not restart the project or P3/P4 work.

## Latest requested acceptance checklist

Owner asks for every still-untested gate. The [49-item combined form](qa/portrait-v2-pending-acceptance/windows-checklist.html)
and [coverage/runbook](qa/portrait-v2-pending-acceptance/README.md) reuse the existing
offline Submit/metadata/persistence implementation. Prior passes remain recorded;
twenty cycles apply only to the existing NEW Sandbox gate. This is documentation,
not runtime/provider/production work or a newly reported device failure.

## Latest completed increment

**Latest owner instruction — FEAT-004 + BUG-009 implementation:** application
and Code.gs integration is implemented in the ordinary launcher: per-booth
25 empty local/remote reserves, Photo/NN/raw,color,bw, immutable offline claims,
verified global/local caches and original deadline retention. Foundation 76bb9a0
and backend 6e2f777 are pushed/verified. Final integration source/evidence and
setup/Submit checklist live in the [implementation package](qa/feat-004-storage/README.md).
Final source 53e7b4c has 824 full local PASS/zero skips, 24 Code.gs PASS and
matching three-job CI SUCCESS (40273343183); 28 final native PNGs verified.
Actual Google deployment/deletion, phone/paper and release remain NOT_RUN. Keep
all archive contents excluded and v1/Sandbox state isolated.

**26 October foldering audit:** owner asks to check current organization against
per-booth/25-reserve/Photo/NN/raw-color-bw/global-cache requirements and excludes
all contents of `old` from inspection/change. Owner selects continued local
photo/print when Drive/reserves are unavailable, with upload/QR later. The
[audited target contract](photobooth-storage-layout.md) is documentation, not a
runtime/cloud cutover. Existing source fixtures: 38 tests PASS plus controlled
two-session/three-copy/retake, native raster and pool checks. At that audit checkpoint the runtime
still had target 2 and its prior active paths; real Drive was not accessible. Do not
infer new-layout implementation or scan/migrate the archive from this audit.

Owner then clarifies that this target belongs to **FEAT-004 ads + BUG-009**.
Keep storage roots/reserves/session paths, shared content caches and retention
in one coordinated implementation sequence; content-sync success and actual
photo-deletion acceptance remain distinct. The earlier retention-only source
scope describes what was delivered then, not an exclusion of this new linkage.

**26 October mirrored outputs:** owner explicitly chooses mirrored review,
result/printed/digital strips. Source 977d26b extends the v1 compositor via a
default-off photo-only option; v2 opts in. Full-resolution original JPEGs and
detector inputs remain original; frame/text/logo/QR and v1 defaults stay normal.
One saved PNG serves result/print/Drive, no old output migration/replay. Source
fc26e3d corrects obsolete preview/consent wording found by screenshot review.
Final 808 full PASS/zero skips (230.670s); 42 focused PASS, all-twelve-renderer
checks pass. Sixteen clean-source native captures verified; eight selected
native and two form views reviewed at 800×1280/452×900. Matching-source CI
40263151709 has all three jobs SUCCESS; optional native model-assets skip covered
locally. Paper orientation NOT_RUN.
Use the fresh five-item Submit form; no extra twenty-cycle gate. Updated older
delivery P03 has a new storage key, preserving old answers without passing the
new orientation automatically. [Evidence/rollback](qa/portrait-v2-mirrored-output/README.md).

**26 October BUG-009:** owner explicitly resumes this previously deferred bug;
setup/redeployment not confirmed. Source 130aae1 repairs stale-flag ACK and
incorrect same-handler trigger setup, reusing v1 cleanup unchanged. Source
887ba39 adds one authenticated read-only status request/CLI with original private
configuration, redacted report and eight-item Submit form. Full 807 Python
PASS/zero skips, 44 focused PASS, 19 actual-Code.gs VM PASS; matching-source CI
40255716011 all three jobs SUCCESS, optional native model-assets skip covered
locally, four native and two form views reviewed at both required sizes. Original 15/30-day
clocks, v2 upload hold and deletion selection preserved. No Google deployment,
trigger write or actual deletion performed; BUG-009 remains OPEN until owning
account and authorized synthetic evidence. No ad sync/watchdog scope.
[Current guide, checkpoints and proof](qa/bug-009-retention/README.md).

**26 October owner flow refinement:** remove only idle CARA PAKAI; reuse the
existing Start/invitation/postgame tutorial gate and acknowledgement/reset rules.
Full-width UNDANGAN (DEMO) replaces the redundant split row. Source `20453fe`
has 800 full PASS/zero skips and twelve clean-source PNGs verified, six affected
views reviewed. Matching-source CI 40248962384 has all three jobs SUCCESS
(one optional native palm-assets skip covered locally). [Scope, exact
evidence and rollback](qa/portrait-v2-photo-entry/README.md). This does not start
retention/watchdog or any other backlog candidate.

**Owner-selected print/Drive continuation:** user postponed proposed watchdog
work and selected automatic print as v1 with background Drive. Stage 1 **7b691c7**
exposes launch options/contracts (29 focused PASS, matching CI SUCCESS); native
stage 2 **266b2c8** connects the existing durable print worker, startup queue resume,
verified-folder consent and large verified result QR. Nine original v1 backend
files are unchanged. Default local and dedicated merchant-trial boundaries stay.
Fifteen new-feature checks and 92 earlier native regressions pass. Final source
has **800 full PASS/zero skips**, matching-source CI 40208966127 all three jobs
SUCCESS and 133 verified PNGs; large screenshot QR decodes at both required sizes.
Actual paper/phone/cloud acceptance remains pending.
[Current print/Drive runbook and eleven-item form](qa/portrait-v2-print-drive/README.md).

**Latest owner retest / BUG-018:** targeted R01–R04 **4/4 checked**, zero
unchecked and no issue notes. Rapid/mixed buttons, busy close, reopen/minimize
and next input/restart are owner-reported PASS; move BUG-018 to **MONITORING**,
not formally CLOSED. Tested HEAD/device fields and specific display sizes remain
unknown. Preserve the earlier raw 8/8 plus hang note as the initial failure.
Delivered input guard `ebb53fd` has 785 full PASS/zero skips, 37 focused PASS,
matching-source CI 40189694738 all three jobs SUCCESS and 119 verified PNGs.
No new runtime patch or old twenty-cycle repetition follows this passing report.
Watchdog remains a proposed feature scope, not implemented by recording this retest.
[Raw reports, evidence and rollback](qa/portrait-v2-health-clicks/README.md).

Read-only operator Device Health now reuses the original v1 panel/backend and
extracted worker from **`dbbe055`**. Small adapters connect v2 scheduling,
cached-camera observations, audio/input lifecycle and redacted local reports.
F12 or a 1.5-second header hold opens it at idle; protected Sandbox RECOVERY also
allows observations. Selection remains disabled; no second camera, print payload,
automatic restart, order mutation or upload is introduced.

Recorded checks: **780 full local PASS / zero skips**; matching-source
[CI 40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369)
three jobs SUCCESS, with one optional native model-assets skip covered locally;
119 PNGs verified. [Proof and eight-item operator form](qa/portrait-v2-operator-health/README.md).
These results predate this documentation-only reconciliation.

## Checkpoints

| Commit | Purpose |
| --- | --- |
| `d6fb5d4` | Visual/local baseline before Sandbox service imports |
| `37da798` | Reused QRIS service/client/journal; 124 original focused PASS |
| `ce603c2` | Native Sandbox → P3 handoff; 195 focused PASS; later full CI exposed a standalone hook regression |
| `9433010` | Corrected final P5 source/readiness/ACK guards; 688 full PASS |
| `0dc6555` | P5 evidence: matching CI, 109 verified PNGs; owner preflight later reported ready |
| `ae90269` / `fdafbe2` | Dated 19-branch audit / consolidated documentation baseline |
| `4c89e4f` | Reused v1 health foundation; 73 focused PASS |
| `ea394e8` | Mounted original health panel/worker and safe reports; 780 full PASS |
| `5f09eff` | Operator matching-source evidence/documentation |
| `f36ebad` | Completed English documentation consistency baseline |
| `ebb53fd` | BUG-018 fresh-press/repeat guard; final 785 full PASS, three-job CI SUCCESS |
| `edeec47` | Later BUG-018 owner 4/4/no issues at unknown HEAD; monitoring |
| `7b691c7` | Explicit print/Drive options and worker setup/QR contracts; 29 focused PASS |
| `266b2c8` | Native automatic print, background queue startup/resume and verified result QR; 800 full PASS, matching three-job CI SUCCESS |
| `20453fe` | Remove redundant idle help action; mandatory Start/invitation/postgame tutorial unchanged; 800 full PASS/zero skips |
| `130aae1` | BUG-009 real-CLOCK activation/setup correction and authenticated read-only backend status; 19 VM + 25 Python PASS |
| `887ba39` | Safe existing-config diagnosis/report and Submit form; 807 full Python PASS/zero skips, 19 VM PASS |
| `977d26b` | Mirror photo areas consistently via existing compositor; 808 full PASS, first matching three-job CI SUCCESS |
| `fc26e3d` | Preview/consent copy correction after visual review; final 808 full PASS/zero skips |

Use scoped inverse commits for code rollback after inspection; preserve all
payment journals, consumed attempts, reports, photo/print manifests and customer
data. Do not reset data to make an uncertain order disappear.

## Authorized continuation and acceptance

The owner's 25 October instruction permits safe approved source work while
laptop acceptance waits; it supersedes older “wait for P5 before any source work”
sequencing. The bounded health/report increment is completed. Additional feature
scope follows the owner's next instruction; do not treat the backlog as approval.
The English documentation audit completed at f36ebad. The next owner report
authorizes this BUG-018 correction; proposed watchdog work is not started.

- Preserve the [later operator 4/4 retest](qa/portrait-v2-health-clicks/owner-retest-2026-10-25.json)
  at unknown HEAD/device metadata; BUG-018 monitoring, no new patch while working.
  Do not impose another old photo/game twenty-cycle run.
- Collect the [P5 form](qa/portrait-v2-p5/windows-checklist.html) and actual merchant
  simulator evidence when available; the new Sandbox integration cycle checks
  are distinct from earlier photo/game reports.
- Owner preflight **`0dc6555` → READY_FOR_MANUAL_TEST** is recorded, but its JSON
  metadata/form were not supplied. Do not borrow missing device fields from older reports.
- Preserve owner-reported P3/visual/audio/game passes and BUG-012–017 monitoring.
  Investigate recurrence with evidence rather than patching reported-working paths.
- BUG-009 cloud retention is OPEN; owner resumed source remediation at 130aae1/887ba39.
  Use the new read-only diagnostic/activation guide; installed-account evidence is pending.
  V2 retention acknowledgement is an upload guard,
  not proof of deployed 30-day deletion. V1 BUG-001/007 are not closed by v2 audio.

## Implementation invariants

Reuse the actual original game Stage/Flow/render/assets/emitter (`672e3f7`, 26
reference files), QRIS service/client/journal (`3cc8a8e`) and health panel/worker
(`dbbe055`). Refresh relevant remote references before new reuse.

Preserve uniform game motion/spacing and centered world (BUG-015/016), native
readable main-button captions without mandatory icons, large animated Meong,
three original unmirrored captures and one retake per design. Quantity means copies.

Sandbox uses server quotes, independently verified status, a one-use grant,
durable STARTING before allocation and STARTED ACK before countdown. Pending,
unknown or paid states cannot be discarded by browsing timeout. No trusted QRIS
game-promo contract exists; require full-price/no-promo consent. Dedicated merchant
trial keeps printer/Drive off. Local MOCK remains a simulation.

[Roadmap](portrait-kiosk-v2.md) · [source status](FEATURE_STATUS.md) ·
[technical contracts](portrait-kiosk-v2-technical-design.md) ·
[reference audit](gui-v2-branch-audit.md) · [promotion plan](gui-v2-promotion-plan.md) ·
[continuation prompt](DEVELOPMENT_PROMPT.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/DEVELOPMENT_HANDOVER.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

