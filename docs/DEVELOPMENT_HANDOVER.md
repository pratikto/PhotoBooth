# Meong Photobooth — GUI v2 development handover

Updated **25 October 2026**. Repository `pratikto/PhotoBooth`; required branch
**`feature/portrait-kiosk-v2-next`**. Audit baseline **`5f09eff`**, latest functional
source **`ea394e8`**. Refresh remote HEAD before continuing. GitHub's default is
still `master`; `main.py` launches v1. Do not restart the project or P3/P4 work.

## Latest completed increment

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

Use scoped inverse commits for code rollback after inspection; preserve all
payment journals, consumed attempts, reports, photo/print manifests and customer
data. Do not reset data to make an uncertain order disappear.

## Authorized continuation and acceptance

The owner's 25 October instruction permits safe approved source work while
laptop acceptance waits; it supersedes older “wait for P5 before any source work”
sequencing. The bounded health/report increment is completed. Additional feature
scope follows the owner's next instruction; do not treat the backlog as approval.
The current request authorizes cross-checking and correcting documentation.

- Review the [operator form](qa/portrait-v2-operator-health/windows-checklist.html)
  without imposing another old photo/game twenty-cycle run.
- Collect the [P5 form](qa/portrait-v2-p5/windows-checklist.html) and actual merchant
  simulator evidence when available; the new Sandbox integration cycle checks
  are distinct from earlier photo/game reports.
- Owner preflight **`0dc6555` → READY_FOR_MANUAL_TEST** is recorded, but its JSON
  metadata/form were not supplied. Do not borrow missing device fields from older reports.
- Preserve owner-reported P3/visual/audio/game passes and BUG-012–017 monitoring.
  Investigate recurrence with evidence rather than patching reported-working paths.
- BUG-009 cloud retention is OPEN. V2 retention acknowledgement is an upload guard,
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
