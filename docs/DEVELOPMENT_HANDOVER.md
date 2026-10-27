# Meong Photobooth — GUI v2 development handover

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

## Current delivery continuation

Owner-approved Drive/GUI improvement continues from fcabfbb. Background delivery
snapshots no longer lock result buttons/footer during rebuild. The strict
UPLOAD_COMPLETE QR contract and operator-disabled printing remain. Controlled
native regression PASS; actual five-minute delay is unmeasured.
[Scope, v1 comparison, evidence and rollback](qa/drive-delivery-performance/README.md).

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

