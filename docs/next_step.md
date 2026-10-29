# Meong Photobooth — outstanding work and feature backlog

## 29 October — current AR audit continuation after verified 4642841

PAY-06/PAY-21 verified, BUG-022 corrected; full 1100 run / 1097 PASS / 3 optional
palm SKIP, zero failure/error, matching CI 40790865010 three jobs SUCCESS.
Audit first source pass read; **IN_PROGRESS**, matrix **44 PASS / 1 FAIL /
9 BLOCKED / 15 NOT_RUN**. **Next small AR-02 task:** define and wire a bounded
native connectivity-restored signal, proving one immediate original-order GET
and durable duplicate throttling; backend/client seam already exists. Then
AR-03 CAP-01–05 exact allocation/STARTED exits, remaining PAY-18/COMPLETE/retake/
disk cases and AR-09 **BUG-023** bounded redacted durable operator-denial audit.
Do not repeat completed creation/payment/source fixes or start queued OPS.
[Current checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md) ·
[Confirmed findings](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md).
External device/merchant/privacy/production gates remain open.


## Historical 29 October — f72fdbc AR-12 evidence and AR-13 readiness

Final runtime/test `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`: **1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors**, 428.924s, Python 3.12.14 / Debian 13.6,
GUI/audio opt-ins with offscreen software GL/dummy audio, tracked tree clean.
[CI 40767441201](https://github.com/pratikto/PhotoBooth/actions/runs/40767441201):
all three jobs SUCCESS at matching source. Native 28 PNGs/both portrait sizes,
four QR checks PASS; payloads private. Previous-session 1094/1091/3 log unavailable;
this is a new independently captured result. Matrix 43 PASS / 0 FAIL / 0 SKIP /
9 BLOCKED / 17 NOT_RUN; exact missing fault windows are not credited as PASS.

[AR-13 assessment](qa/portrait-v2-sandbox/AR13-READINESS.md): **CONDITIONAL** for
controlled acceptance; **NOT READY for unattended commercial release**. Device,
merchant, phone/paper/Drive/deletion, privacy/remedy/operations and owner approval
remain open. First unfinished source-evidence task: PAY-06 abrupt exit between
provider evidence and DB commit, then remaining matrix gaps. AR stays top priority;
all future Settings/Emulate Ticket/QRIS Slip implementation stays NOT_STARTED.
[Exact command/skips/provenance](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md) ·
[checkpoint/next action](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## CURRENT DEVELOPMENT PRIORITY — AR-00 through AR-13 FIRST (29 October owner reaffirmation)

**TOP PRIORITY: continue and finish the existing AR-00 → AR-13 autonomous QRIS/photo-session recovery roadmap, in dependency order, from the [latest real checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).** Do not restart completed AR increments; consult the [AR roadmap](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md) and [current handover](DEVELOPMENT_HANDOVER.md) for the actual unfinished step. AR-12/13 source validation/readiness and external NOT_RUN gates are distinct from new features. No production release or owner go/no-go is implied.

**NEXT, NOT NOW — approved future GUI v2 Operator Settings design:** [Full operator Settings contract](qa/portrait-v2-operator-settings/README.md) · [OPS-00–OPS-10 post-AR roadmap](qa/portrait-v2-operator-settings/IMPLEMENTATION-ROADMAP.md) · [129 acceptance cases](qa/portrait-v2-operator-settings/ACCEPTANCE-MATRIX.md) · [complete approved decisions and supersessions](qa/portrait-v2-operator-settings/DECISION-REGISTER.md) · [Codex continuation prompt](qa/portrait-v2-operator-settings/CODEX-HANDOVER.md). **Documentation only; not implemented and tests NOT_RUN.**

The existing secret F12 / Meong-header hold must eventually open **static QR Operator Login**, followed by exactly **Device Health, Audio Settings and Emulate Ticket**. Full Settings entry requires **both first-page Advertising and authoritative SAFE_IDLE**; keep AR-09 protected RECOVERY/PIN path separate. Static per-booth QR operator login, persistent Music/Button SFX/Other SFX plus Master/Mute/Test, and reusable **static MOCK-only** Merchant Promo/Meong Fly DEMO QR presets/80-mm thermal print/test history are approved future design. For Meong Fly, the same QR grants **only one attempt per durable test visit**, but may work once in a truly new test visit. Never accept DEMO QR in real merchant payment, disable original one-use ledger safeguards, stack promo rewards initially, or bypass Sandbox printer/Drive-off.

**Separate planned v2 QRIS Payment Slip** remains tracked under FEAT-020 below and [the GUI roadmap](portrait-kiosk-v2.md): it is an optional printed copy of an *active existing provider QR*, NOT an Emulate Ticket or proof of payment.

The following dated AR-00/AR-01 narrative and older "design only" descriptions are **historical snapshots**, not current remote code status; always follow the latest checkpoint/source tests.

## Historical autonomous recovery continuation — 28 October

Owner now explicitly requests implementation in AR dependency order. AR-00 is
verified/pushed at `4261236694358c2f3cd2a475a4cd9cd82f436e00`. AR-01 local attempt
durability source `017b417d02d63a79b1c5b21c4f0613b7d15186fc` has 132 focused PASS,
968 full run / 965 PASS / 3 optional palm SKIP and matching three-job CI SUCCESS. Legacy
repeat-charge activation is blocked on provider contract/evidence. Next independent
increment: AR-02.a fresh reconciliation tests, preserving separate operator auth.
[Current checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).
Earlier DESIGN ONLY entries below describe their original publication.

## 28 October — priority roadmap: autonomous QRIS + photo recovery (DESIGN ONLY)

The owner requested a comprehensive, Codex-readable **unattended-first** design and staged implementation reference. [Master engineering contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-MASTER-PLAN.md) · [AR-00–AR-13 execution roadmap](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md) · [official Midtrans research](qa/portrait-v2-sandbox/MIDTRANS-PROVIDER-CONTRACT.md) · [crash/acceptance tests](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-TEST-MATRIX.md) · [operational safeguards](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATIONS.md).

**Current state:** Documentation/planning only; the prior backend PIN recovery protocol `2e5efe5` is in source, but unattended native recovery, customer claim, photo reconstruction, ledger split and guarded automatic restart are **not yet implemented**. Do not mark roadmap stages complete, rerun stable tests merely due to docs, or claim merchant/device certification. Begin at AR-00, preserve protected `old` and original journal evidence, and use stage-local tests/commits on the existing branch. Existing prioritization/feature IDs remain in force; this scope adds implementation detail to FEAT-007/009/020/022 without treating unapproved production integration as delivered.


Latest owner Sandbox report is BUG-021: image disappears while remaining on the
payment page. Pending action-URL overwrite is reproduced and corrected with
182 focused PASS; exact laptop cause and retest remain unconfirmed.
[Current evidence and final checks](qa/portrait-v2-sandbox/QR-POLLING.md).
The earlier BUG-020 key-format correction remains in source; actual merchant
authentication/simulator acceptance is separate.

## 27 October — BUG-019 held gallery drag

Owner reports an empty incoming side while holding a carousel drag. Five pooled
Images existed, but two outer textures were cleared at rest. The existing widget
now retains a five-picture cached window through drag, reversal and release.
Native checks cover all 12 designs, both directions and five sizes, including
wraparound; selection/quantity and lifecycle guards remain. Device acceptance
is separate. [Scope, tests and update](qa/portrait-v2-carousel-hold/README.md).


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

## Current delivery recurrence — 27 October

Prioritize on-device retest of the console-recursion correction after the new
RecursionError trace. Timing failures are isolated from upload and v2 uses MIXED
logging; actual owning-account performance/recovery still needs fresh evidence.
Keep old bind-folder conflicts protected and the post-QR content error separate.
Do not optimize upload protocol or remove checks to compensate for a dead worker.
[Source, evidence and restart command](qa/drive-delivery-performance/LOGGING.md).

## 27 October — failed-delivery retry isolation

Owner timing identifies repeated old bind failures as 70.782s of a 122.719s
queued-to-QR session; exact ValueError cause/installed SHA remain unknown.
Healthy-first scheduling, one recovery/30s, persisted 30–300s backoff and safe
bind codes are implemented; known folder/transaction conflicts remain protected.
Focused service/native checks PASS; final regression/CI evidence is in the linked runbook.
Code.gs unchanged; no redeploy required. [Scope, evidence, updates and limits](qa/drive-delivery-performance/RETRY.md).

## 27 October — Drive delivery priority and timing

The owner prioritizes customer upload/GUI responsiveness. Source now uses one
file per transaction per pass, chunk-yielding content sync, incremental five-slot
reserve batches with startup/periodic reconciliation, and verified cross-version
asset reuse. Structured monotonic timing distinguishes queue/request stages.
Known-delay production root cause remains unmeasured; native/fixture evidence
and exact update/rollback steps are in the [delivery runbook](qa/drive-delivery-performance/README.md).
No deployed Google version, actual throughput or cloud deletion is certified.

**27 October continuation:** FEAT-009 stages 1–2 now supply external observation,
read-only recovery review/pre-GUI holds, per-checkout launcher ownership and
Windows/Ubuntu startup generation. Next: actual Ubuntu mini-PC graphical-session/
device acceptance, then a separately bounded safe-idle restart policy. Automatic
restart remains off. Primary rule: read documentation comprehensively before
code, update it afterward. Windows is development; Ubuntu is deployment.
Existing merchant/Drive/privacy gates remain pending.
[Current runbook/evidence](qa/portrait-v2-recovery/README.md).

Updated **26 October 2026**. Continue on `feature/portrait-kiosk-v2-next`.
P3 photo, original game reuse, MOCK/Sandbox and P5 tooling already exist; do not
reimplement them. The read-only Device Health/report increment is now complete
in source (`ea394e8`, input correction `ebb53fd`). Later operator retest R01–R04
is 4/4/no issues, OWNER-REPORTED PASS / MONITORING at unknown HEAD/device metadata.

The owner permits safe approved source development while laptop tests wait.
Evidence gates below do not block every source task. The backlog is not blanket
approval for features, production, deployments or repository transitions.

## Current follow-up

**Owner foldering request, 26 October:** the [source audit/target contract](photobooth-storage-layout.md)
records per-booth roots, at least 25 READY directories, Photo/NN/raw-color-bw,
booth-local assets and complete local copies of global ads/templates. Owner
selects local photo/print with deferred upload/QR if Drive/reserves are absent.
That audit-only snapshot predates the delivered local implementation and the
later `0bd69a9` numbered-cloud/verified-link repair. Source is integrated; actual
installed Google deployment and delivery/retention acceptance remain pending.
Coordinate paths, counters/pool, raster persistence, upload, retention and asset
snapshots before switching storage. Entire `old` contents remain excluded.

Owner clarification: this is **FEAT-004 ads + BUG-009**, one coordinated
storage/content/retention workstream. Share booth-root/backend/path integration
while verifying asset sync and real photo deletion independently. The older
retention-only increment below did not include sync; it is not a reason to
treat the newly linked foldering target as unrelated work.

**BUG-009 resumed by owner, 26 October:** source 130aae1/887ba39 repairs actual
CLOCK activation and adds read-only existing-config diagnosis/Submit form, reusing
v1 cleanup. Full 807 Python PASS/zero skips and 19 Code.gs VM PASS; cloud project
setup/deployment and actual synthetic deletion are unverified. The owner says
setup is not confirmed. Use the [activation guide](qa/bug-009-retention/README.md);
keep BUG-009 OPEN. That delivered retention-only increment did not include
FEAT-004 sync; the later foldering target is now owner-linked to FEAT-004 +
BUG-009 as described above. Watchdog remains separate.

**Owner-selected increment delivered, 25 October:** v2 automatic print and
background Drive at 266b2c8, reusing v1; 800 full PASS and matching three-job CI
SUCCESS. Actual paper/phone/cloud checks use the eleven-item form. Watchdog is
postponed. Explicit
launch opt-ins, existing printer config/Drive credentials, verified queue/QR and
uncertain-print guards remain; no deployment/cloud deletion/production.
[Scope, staged evidence and rollback](qa/portrait-v2-print-drive/README.md).

| Order | Focus | Next action / boundary |
| --- | --- | --- |
| 1 | FEAT-022 P5 current Windows integration | Collect the [P5 report](qa/portrait-v2-p5/windows-checklist.html); preflight `0dc6555` alone is not acceptance. Fix reproducible failures within authorized scope |
| 2 | FEAT-020 actual merchant Sandbox | Enter keys locally; test official simulator/status/cancel/restart/recovery. New integration cycles are separate from old reports |
| 3 | BUG-009 / Drive/privacy and printing | Source activation/diagnosis repaired at 887ba39; complete installed-project setup/deployment and authorized synthetic cloud evidence using the current guide. Verify download/offline, paper/uncertain sends separately; bug remains OPEN |
| 4 | Game → trusted QRIS promotion | Backend eligibility/redeem contract absent; preserve full-price Sandbox consent. Define approved scope before implementation |
| 5 | Intended primary-branch transition | Follow the [promotion plan](gui-v2-promotion-plan.md) when the owner specifies the repository operation; not yet performed |

Source evidence: [feature status](FEATURE_STATUS.md), [test ledger](test_checklist.md).
BUG-012/013/014/015/016/017/018 are monitoring per recorded owner reports; do not
speculatively patch working paths. Missing tested HEAD/device metadata stays unknown.

## Stable feature inventory and candidates

Business priority is distinct from execution order. Candidate scope requires a
fresh source/readiness review and relevant owner instruction before code work.

| ID / topic | Current state or retained proposal | Dependency / boundary |
| --- | --- | --- |
| FEAT-001 pricing/copies | Implemented: Rp5,000/design + Rp5,000/copy, one three-photo session/design | Quantity zero deselects; mixed A×2+B×1 = Rp25,000/two sessions; digital-only and commercial maximum policy remain undecided |
| FEAT-002A/B merchant receipt promotion | Separate design: receipt scan at checkout; example Rp50,000 food purchase waives one Rp5,000 base fee | Existing POS receipt first; scan is not purchase proof. Partner/API, one-use eligibility, offline/stacking and reimbursement terms unresolved; not the game discount |
| FEAT-003 mirror | V2 live/review and photo areas of result/printed/digital strip mirror; v1 defaults unchanged | Full-resolution original JPEGs and detector inputs stay original; template/text/QR stay normal |
| FEAT-004 ads + BUG-009 storage/global content | Local storage/content integrated; `0bd69a9` corrects numbered cloud folders and verified QR links | Installed Web App deployment, actual upload/phone/deletion acceptance pending; preserve local journals and exclude all `old` contents |
| FEAT-005A/B ordering | Small standalone DEMO proposal; real merchant supplies compatible customer-facing ordering | Same-kiosk DEMO order-to-photo offer needs no receipt scan; retain external-receipt path. Do not build a full production POS by default |
| FEAT-006 themes | Proposed configurable shared-codebase themes | Final admin/preset policy and approval pending |
| FEAT-007 transaction recovery | Some durable Sandbox admission already implemented; broader operational paid fulfillment remains future scope | No replay on restart; paid reprint/refund/production recovery not implied |
| FEAT-008 Device Health | Read-only panel/report integrated; active selection/staging/switching not mounted | Reuse `feature/device-health` / `dbbe055`; actual device acceptance separate |
| FEAT-009 watchdog/autostart | Stages 1–2: observation, read-only recovery gate, launch ownership, Windows/Ubuntu startup generation | Actual Ubuntu session/device acceptance and bounded automatic-restart policy pending; never replay capture/charge/print |
| FEAT-010 device identity/config | Candidate | Authenticated per-machine config; tenant separation and offline behavior |
| FEAT-011 dithering | Existing lab/printer baseline present; newer branch lab separate | Refresh `feature/dither-tuning` (audit `e89e6ee`) before reuse; Auto Tune/enhancement is not automatically the kiosk preset |
| FEAT-012 diagnostics | Existing local diagnostics/readiness and safe health reports present; broader support scope candidate | Data minimization and explicit upload/remote-support policy |
| FEAT-013 promo/subsidy reporting | Proposed | Verified redemption and contract-defined revenue recipient; not merely qualifying food spend |
| FEAT-014 branded frames | Proposed | Approved artwork, print/QR readability and existing templates preserved |
| FEAT-015 paid digital upsell | Proposed | Current folder QR is separate; delivery/consent/retention/provider acceptance required |
| FEAT-016 paid reprints | Proposed | Payment/fulfillment idempotency and uncertain-paper handling |
| FEAT-017 event mode | Proposed | Shared theme/media/config; event prices/bundles not approved by theme scope |
| FEAT-018 fleet monitoring | Candidate after demonstrated multi-device need | Health/config/log privacy and tenant isolation |
| FEAT-019 / BIZ | Free/Business/Enterprise direction recorded, billing/license enforcement not implemented | Commercially usable Free; Meong controls Free ads and retains TBD slots on paid tiers; [decisions](DECISIONS.md) |
| FEAT-020 QRIS | MOCK and opt-in Sandbox source integrated | Actual merchant acceptance/production/merchant promotion remain separate |
| FEAT-020 follow-up — GUI v2 QRIS Payment Slip | **PLANNED (owner request 29 October 2026)**: optional CETAK QRIS on the native v2 payment page; reuse `photobooth/qris_print.py` and shared printer configuration, preserve the on-screen active QR | Printed QR must match the existing pending provider order without generating a charge/confirming payment/extending expiry; durable print-attempt/uncertain-send no-replay; keep Sandbox physical printer OFF until separately approved test/production scope. [GUI v2 plan](portrait-kiosk-v2.md#planned-gui-v2-follow-up--qris-payment-slip-owner-request-29-october-2026) |
| FEAT-021 — Meong Fly | Original game renderer/flow integrated as DEMO | Manual one-use input in v2; standalone scanner/POS not enabled |
| FEAT-021 — AI Background Studio | Separate candidate branch (`eb368c1` at audit) | Reuse offline/cache/fallback implementation, preserve raw originals; hardware latency/paper evidence |
| FEAT-021 — WhatsApp delivery | Separate documentation proposal (`aebde84` at audit) | Additional optional channel; retain Drive QR, require consent/provider/privacy scope |
| FEAT-022 GUI v2 | Development focus; P5 ready for acceptance plus health increment | Current [roadmap](portrait-kiosk-v2.md); default/master/release operations separate |

FEAT-021 has three historical branch-local meanings. Always append the topic
and branch; do not silently renumber history or combine their authorization.
Reference SHAs are dated snapshots; refresh before reuse.
[All 19 reference branches](gui-v2-branch-audit.md).

## Evaluation fields and parked business ideas

For new work record ID/date, problem/value/behavior, priority/impact, current-code
compatibility/evidence, readiness, complexity/confidence, dependencies/risks,
affected modules/devices, acceptance, approval, execution rank and rollback.
Re-rank when a material defect or new decision appears.

Premium templates/sponsored frames, event passes, analytics, support/warranty,
white-label, campaigns, digital upsells, reprints, fleet licenses and a Meong ad
network remain parked for evaluation. No example price or revenue is committed.
Check demand, unit economics, hardware/partner compatibility, privacy/venue rights
and overlap with tier entitlements before proposing implementation.

Photo income and reimbursement for waived fees generally belong to the operator
bearing those fees on sold hardware; Meong's hardware/software/ad/platform fees
require their own contracts. Subsidies apply to redeemed eligible discounts,
not every qualifying food order. [Binding business direction](DECISIONS.md).

Detailed original proposals, acceptance examples and the former execution
rankings remain in the dated historical record below; their old implementation
statuses do not override this inventory.

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/next_step.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.
