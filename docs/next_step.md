# Meong Photobooth — outstanding work and feature backlog

**Android runtime continuation — 28 October 2026:** Current authorized Android work includes built-in camera, USB OTG auto-print and QRIS Sandbox with current v2 services. Finish native recipe/APK validation and record actual device/provider limits; the old offline A1 scope below is historical.
[Scope, setup and source evidence](android-v2-runtime.md).

**Android stream — 28 October:** A1 debug-APK compilation and binary inspection
are verified on existing feature/portrait-kiosk-android, functional source
293b22b. Next: actual arm64 Android install/portrait/touch/keyboard/Back/Home
and private persistence. Native camera (A2), audio/video/print (A3) and optional
Drive/authenticated Sandbox (A4) remain unavailable in the offline preview.
The last full-run summary after 293b22b awaits workspace recovery; previous
881-case results and exact-source preview CI remain recorded separately.
[Current build and acceptance guide](android-build-readiness.md).

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
