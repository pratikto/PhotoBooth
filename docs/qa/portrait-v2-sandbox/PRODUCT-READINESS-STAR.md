# Meong Photobooth — STAR product-readiness roadmap

8 November 2026 · Existing branch `feature/post-preview-qris-checkout`.
This is the product completion plan requested by the owner. Keep the canonical
PP/UAH/AR policies, case identities and source-specific evidence; no new branch,
master merge, live payment, refund, public upload or operational release follows
automatically from this plan.

## S — Situation

The owner exercised the Windows real-camera, synthetic-payment, no-paper/no-cloud
trial: 11 guided steps reported PASS, PILOT-03 not tried, and a result-page exit
defect. Exact owner-tested commit/device metadata remain unknown. The shortened
web checklist is an initial smoke test, not complete acceptance.

Prior R4 has 1,801 successful software executions (1,711 normalized method IDs),
110/112 cases with partial software evidence and two without complete executable
customer-status/legal scope. The 188-row full acceptance register is not complete.
The two-hour qualification has only a 1,848.279-second interim record. The
post-preview owner launcher is synthetic-payment-only; actual merchant/refund,
paper/cloud and full protected recovery remain separate unfinished gates.

BUG-046 is published at `fc8853b`: paid results return automatically to protected
Ads after their own 30 seconds, without an added finish button. It reuses privacy
retirement and original worker/admission guards. Local 598 backend + 70 native
executions PASS, zero failures/errors/skips; measured synthetic return 30.089s.
This does not finish all work in stage 1 below or grant production readiness.

## T — Task

Deliver the agreed customer journey:

**Ads → designs/copies → three photos and one retake per design → all previews →
verified QRIS → original on-screen/once-printed Recovery Ticket → automatic paid
strip printing with verified customer Drive link and honest upload progress →
results for 30 seconds → protected Ads → safely admitted next customer.**

Recover normal supported faults automatically. Route ambiguous financial, paper,
security or corrupt-media conditions through the already approved operator
matrix. Preserve original PAID/OWED and prevent duplicate charges, service,
capture, ticket presentation and print replay.

## A — Action and finite completion gates

| Stage | Work | Evidence required to finish | Current boundary |
| --- | --- | --- | --- |
| 1. Complete the application journey | Deliver BUG-046; clarify unpaid preview heading and the blank synthetic-payment placeholder; reconcile the current manual paid-strip action with the agreed automatic-print policy. | Native full journey from Ads through original ticket/results back to Ads, with readable states and correct frozen price/copies. No finish button added. | Automatic result return published; Automatic paid-strip dispatch now implemented; see [9 November evidence](PP05-AUTOMATIC-PAID-PRINT-2026-11-09.md). Remaining UI clarity and full stage acceptance stay open. |
| 2. A → B → A customer lifecycle | Exercise actual native controls, both portrait sizes, status redraws, original proof return, busy booth, delayed worker replies and safety holds. | B never sees A media/proof; valid A proof restores only A's original service when free; no extra charge/capture/output. Test final exit and safe next admission explicitly. | Existing partial simulations and BUG-046 race regression pass; comprehensive case acceptance remains open. |
| 3. Real post-preview Midtrans Sandbox integration | Mount a guarded after-preview provider profile using secure existing merchant configuration; verify successful/expired/cancelled/unknown/lost-response/late and duplicate settlement paths. | Provider independently verifies the same original attempt and exact amount; one entitlement; QR1/2/3 cap; no mock PAID authority or duplicate POST after uncertainty. | Current owner launcher remains synthetic-only. Legacy paid-first Sandbox is not this integration. |
| 4. Real paper and Drive | Reuse configured printer and deployed test storage. Verify original ticket and automatic strips, selected copies/cuts, exact customer folder/URL, checksums, background upload and signed-out phone access. | Manually counted real paper matches the purchase; correct photos open from the verified URL; pending upload remains truthful. No foreign-folder binding or uncertain resend. | Requires separately opted-in owned test printer/Drive and actual owner observations. |
| 5. Recovery, refund and operations | Finish supported Windows/Ubuntu original-worker restart/vault integration, device/queue faults, automatic normal recovery, customer refund/status and approved operator procedures. | Original journals/media/financial rights survive; exact worker PREPARE/ACK gates B; uncertain paper is never replayed; actual refund capability/status is verified before claiming success. | Mock process/DPAPI/refund evidence exists; Ubuntu protection, complete integration/provider/status/legal gates remain. |
| 6. Qualify the final source | After deterministic failures are resolved, run a measured two-hour synthetic campaign and four-hour device campaign with repeated visits and controlled delays/outages. Establish resource budgets before declaring performance PASS. | Same runtime fingerprint throughout; no stuck session, cross-customer disclosure, duplicate output or uncontrolled thread/handle/queue growth. Retain actual elapsed/resource records and failures. | Prior interim run is not a completed qualification. Owner device stage remains NOT_RUN. |
| 7. Limited operational pilot | After all applicable gates, verify live-account readiness and conduct explicitly approved real transactions with the owner. Provide startup, shutdown, recovery and fault instructions. | Customer actually receives the correct paid output and booth safely serves the next customer; release scope and owner acceptance explicitly recorded. | Not approved for live customer operation yet. |

Engineering owns source fixes, deterministic simulations and truthful evidence.
The owner participates for actual device/account observations. Do not ask the
owner to repeat the 11 previously reported steps without a relevant change or
unresolved observation. Collect required configuration questions together after
examining existing secure settings; never request secrets in chat.

## R — Results and reporting

Each stage reports: behavior delivered, scenarios actually executed, source
commit, PASS/FAIL/BLOCKED/NOT_RUN, observed defects, remaining concrete dependency
and exact next action. A test-method count is not product completion or a
replacement for the customer journey and independent paper/provider/cloud facts.
Keep already accepted results and dated failures. Do not keep adding unrelated
features or expand the finish line to queued Operator Settings/Android redesign.

The owner-approved product/financial/privacy scope cannot be silently dropped
to call the product ready. External account, policy or hardware blockers must
be named specifically. A new source push is not release approval.

## Current next action

BUG-046 CI 42427430090 is verified SUCCESS. The 9 November automatic-print
increment has 598 backend + 72 native PASS and matching CI42552901917 all three
jobs SUCCESS. The remaining stage-1 unpaid preview/synthetic-payment presentation now has
[a bounded source correction](PP02-PREVIEW-PAYMENT-CLARITY-2026-11-09.md),
35 affected native PASS and clean both-size visual review. Full stage acceptance
remains separate. Next complete the native A→B→A lifecycle using original
admission/claim/worker fixtures, then mount guarded post-preview merchant integration.

References: [BUG-046 evidence/retest](BUG046-RESULT-AUTO-RETURN.md),
[current 112-case R4 review](evidence/pp07-r4-case-review-2026-11-05.json),
[188-row register](evidence/pp07-execution-register-r4-2026-11-05.csv),
[complete test plan](PP07-COMPLETE-TEST-PLAN-2026-11-05.md),
[owner policy](POST-PREVIEW-QRIS-OWNER-APPROVED.md),
[security/state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md).
