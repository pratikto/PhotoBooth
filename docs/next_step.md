# Meong Photobooth — outstanding work and feature backlog

Updated **25 October 2026**. Continue on `feature/portrait-kiosk-v2-next`.
P3 photo, original game reuse, MOCK/Sandbox and P5 tooling already exist; do not
reimplement them. The read-only Device Health/report increment is now complete
in source (`ea394e8`, input correction `ebb53fd`). Later operator retest R01–R04
is 4/4/no issues, OWNER-REPORTED PASS / MONITORING at unknown HEAD/device metadata.

The owner permits safe approved source development while laptop tests wait.
Evidence gates below do not block every source task. The backlog is not blanket
approval for features, production, deployments or repository transitions.

## Current follow-up

**Owner-selected source work, 25 October:** finish v2 automatic print and
background Drive delivery first, reusing v1. Watchdog is postponed. Explicit
launch opt-ins, existing printer config/Drive credentials, verified queue/QR and
uncertain-print guards remain; no deployment/cloud deletion/production.
[Scope, staged evidence and rollback](qa/portrait-v2-print-drive/README.md).

| Order | Focus | Next action / boundary |
| --- | --- | --- |
| 1 | FEAT-022 P5 current Windows integration | Collect the [P5 report](qa/portrait-v2-p5/windows-checklist.html); preflight `0dc6555` alone is not acceptance. Fix reproducible failures within authorized scope |
| 2 | FEAT-020 actual merchant Sandbox | Enter keys locally; test official simulator/status/cancel/restart/recovery. New integration cycles are separate from old reports |
| 3 | BUG-009 / Drive/privacy and printing | Verify download/offline behavior, physical paper and uncertain sends; cloud retention remains OPEN and deployment/deletion needs its own authorization |
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
| FEAT-003 live mirror | In source; display-only mirror across implemented live previews | Originals/review/print/QR/decode input unmirrored; future scanner inherits policy |
| FEAT-004 ads + BUG-009 | Proposed per-machine local-first Drive ad sync; coordinate retention work | Separate ad/photo folders, atomic updates/offline cache; verify deployment/trigger and deletion independently |
| FEAT-005A/B ordering | Small standalone DEMO proposal; real merchant supplies compatible customer-facing ordering | Same-kiosk DEMO order-to-photo offer needs no receipt scan; retain external-receipt path. Do not build a full production POS by default |
| FEAT-006 themes | Proposed configurable shared-codebase themes | Final admin/preset policy and approval pending |
| FEAT-007 transaction recovery | Some durable Sandbox admission already implemented; broader operational paid fulfillment remains future scope | No replay on restart; paid reprint/refund/production recovery not implied |
| FEAT-008 Device Health | Read-only panel/report integrated; active selection/staging/switching not mounted | Reuse `feature/device-health` / `dbbe055`; actual device acceptance separate |
| FEAT-009 watchdog/autostart | Candidate | Preserve pending/started/uncertain state; never automatic capture/charge/print replay |
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
