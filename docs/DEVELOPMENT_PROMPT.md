# Continue Meong Photobooth GUI v2

Updated **25 October 2026**. Use the existing project and branch.
[AGENTS.md](../AGENTS.md) and [protocol](DEVELOPMENT_PROTOCOL.md) govern execution.

Current continuation update, 25 October: the owner prioritized print and Drive
only, selecting automatic print after photo approval as v1. Source 266b2c8 has
800 full local PASS/zero skips and matching-source three-job CI SUCCESS, 133
verified PNGs. Reuse nine original v1 services; explicit --print/--drive profile,
background queue startup/resume and verified result QR. Paper/phone/cloud gates
remain pending; watchdog is postponed. [Current package](qa/portrait-v2-print-drive/README.md).

## Copy/paste prompt

> Repository: pratikto/PhotoBooth.
> Required branch: **feature/portrait-kiosk-v2-next**.
> Task/scope: **[DESCRIBE THE REQUESTED WORK]**.
> Constraints/expected result: **[ADD IF APPLICABLE]**.
>
> GUI v2 is the intended future primary branch. GitHub default remains master;
> main.py remains v1. Do not start again from master or create a branch, rename,
> merge, change default, release or deploy without the corresponding instruction.
>
> Read README.md, docs/README.md, portrait-kiosk-v2.md, FEATURE_STATUS.md,
> DEVELOPMENT_HANDOVER.md, bug_tracker.md, next_step.md, DECISIONS.md and
> test_checklist.md. Refresh remote HEAD. At the 25 October documentation audit,
> latest functional source was ea394e8 (780 full local PASS; matching CI SUCCESS,
> one optional native model-assets skip); 9433010/0dc6555 is the earlier P5 baseline.
>
> Preserve P3 photos, actual original game renderer/assets, MOCK/Sandbox and
> readable native typography. Read docs/gui-v2-branch-audit.md and refresh relevant
> reference branches read-only before reuse. Reuse existing UI/controller/worker/
> renderer/assets through small adapters; do not independently rebuild working
> features or automatically port candidates because their docs exist.
>
> Complete the already authorized scope without asking again per small change.
> Give concise updates; use logical stages, relevant local checks, fixes, commits,
> push to the required branch and remote verification before the next stage.
> One final full regression follows the final functional change. Documentation
> uses link/reference/hash/scope checks and skips redundant GUI CI.
>
> For GUI changes review 800×1280 and 452×900 plus relevant compact/wide sizes.
> Preserve uniform game speed/spacing, centered world, retired callback guards,
> one audio owner, unmirrored originals and one retake/design; quantity is copies.
>
> Sandbox requires backend quote/verification/grant/ACK. GUI PAID/score/amount
> is not authority. Trusted QRIS game promotion is absent; require full-price
> consent. Production/POS/scanner stay off. Do not delete journals/data or replay
> charge/capture/print to bypass uncertainty. Enter merchant keys only locally.
>
> Distinguish source PASS, owner reports, preflight, merchant and physical acceptance.
> READY_FOR_MANUAL_TEST at 0dc6555 is not P5 acceptance. Missing metadata stays
> unknown; unchecked boxes do not pass. The operator eight-item form adds no old
> photo/game twenty-cycle retest; new Sandbox cycles use the P5 form.
>
> The owner permits safe approved source work while laptop checks wait. The
> read-only operator health/report increment is complete in source; selection
> remains disabled. This does not authorize unrelated features or deployments.
>
> Update only documents whose facts changed. Report scope, evidence/limits,
> exact tested/pushed source, remote verification, outstanding gates and next
> action. Keep original dated reports and avoid speculative repairs of working paths.

## Quick links

[Handover](DEVELOPMENT_HANDOVER.md) · [P5 runbook](qa/portrait-v2-p5/README.md) ·
[P5 form](qa/portrait-v2-p5/windows-checklist.html) ·
[operator form](qa/portrait-v2-operator-health/windows-checklist.html) ·
[branch audit](gui-v2-branch-audit.md) · [promotion plan](gui-v2-promotion-plan.md).
