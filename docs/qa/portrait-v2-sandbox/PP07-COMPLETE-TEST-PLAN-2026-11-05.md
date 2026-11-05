> **Later R4 execution:** [source-matched simulation campaign](PP07-SIMULATION-CLOSURE-R4-2026-11-05.md), [112-case partial review](evidence/pp07-r4-case-review-2026-11-05.json), [188-row register](evidence/pp07-execution-register-r4-2026-11-05.csv). Historical mappings below remain dated; all full acceptance outcomes are unchanged.

# Complete post-preview test plan — 5 November 2026

[Start a fresh Codex execution session with this comprehensive prompt](PP07-CODEX-TEST-EXECUTION-PROMPT-2026-11-05.md); it resumes this plan from repository evidence without the previous chat.

This is the execution plan and remaining-test register for the active `feature/post-preview-qris-checkout` workstream. It changes documentation only. **All 112 canonical PP full acceptance cases remain NOT_RUN.** Their existing software evidence is partial: 103 cases have source-matched automated evidence; nine have no executable required implementation or external review evidence. Those nine are not the entire remaining test backlog.

Tested runtime/test source: `acbac15842b59d5005075f2fbc7e87978323b158`; documentation baseline: `3bedcb66e0e001cd2d77fea039c20452fdacc831`. The [executed campaign](PP07-END-TO-END-SIMULATION-2026-11-05.md) records 1,744 local PASS and [matching CI](https://github.com/pratikto/PhotoBooth/actions/runs/41906929920) with 546 Windows, 546 Ubuntu and 62 native PASS, zero failures/errors/skips. These are executions, not acceptance-case counts. No new execution or production signoff is claimed by this plan.

| Scope | Plan / authority | Still required |
| --- | --- | --- |
| PP-001–112 | [Detailed 112 case procedures](PP07-COMPLETE-CASE-PROCEDURES-2026-11-05.md), [machine-readable plan](evidence/pp07-complete-test-plan-2026-11-05.json), [canonical acceptance criteria](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) | 112 full acceptance observations, with implementation/external prerequisites where blocked |
| PILOT-01–26 | [Canonical owner worksheet](PP07-SUPERVISED-WINDOWS-UAT.md) | 24 NOT_RUN; 2 BLOCKED; software CI cannot fill owner observations |
| UAH-001–050 | [Versioned handoff acceptance authority](UNATTENDED-SESSION-HANDOFF-OWNER-APPROVED.md) | 50 inherited full acceptance cases; preserve legacy/profile distinction |
| AR-00–13 | [Retained stage definitions](PP07-SOFTWARE-TRACEABILITY-2026-11-04.md#retained-ar-00ar-13-definitions-and-branch-boundary) | 14 regression/release stages, not 14 extra acceptance cases |

The [inherited/device procedures and AR gate appendix](PP07-INHERITED-AND-DEVICE-TEST-PLAN-2026-11-05.md) and [blank 188-row execution register](evidence/pp07-acceptance-execution-register-2026-11-05.csv) complete this inventory.

The scoped inventory is **188 identified case rows (112 PP + 26 PILOT + 50 UAH)** plus 14 AR stage gates. Several rows overlap in intent. They are not 188 unique code paths or 188 executed tests. This plan covers the current post-preview continuation and its inherited safety gates; queued Operator Settings and unrelated product work retain their own matrices.

## Status rules

`AUTOMATED_VERIFIED` means the mapped methods in the [existing source-specific review](evidence/pp07-simulation-case-review-2026-11-05.json) ran successfully for a partial software scope. `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED` are execution outcomes; full acceptance PASS needs a source-specific run and all required evidence. Partial execution never changes a full row to PASS. An unknown result is not a failure. A blocked case requires a recorded missing dependency, not an invented observed result.

`HARDWARE_PENDING`, `INTEGRATION_PENDING`, `PROVIDER_BLOCKED`, `SECURE_RESTORE_PENDING`, `HARDWARE_CLOUD_PENDING`, `REFUND_PROTOCOL_BLOCKED`, `CROSS_COMPONENT_OFFER_EVIDENCE_GAP`, and `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED` in the catalog are **planning labels**, separate from outcomes. Software design can proceed with fakes; they do not mean every prerequisite is implemented or every external test may run now.

## Remaining work, in execution order

| Order / priority | Required work and representative cases | Dependency / owner role | Completion evidence |
| --- | --- | --- | --- |
| 1 / P0 | Close cross-component genuine-proof-offer gaps PP-040/087/088: never-offered CCP, never-rendered screen despite SUBMITTED, independent paid/remedy facts | Engineer: connected UI/payment/presentation journal fixtures; existing guard tests alone are insufficient | Exact-source connected regressions with absent genuine-offer evidence, retained PAID/OWED, no negligence/refund fiction |
| 2 / P0 | Protected original-worker restoration and crash fencing PP-043–045/064–065/070–072/077–078; UAH-017–027/034–041 | Engineer/security: persistent supported OS vault and restore integration; Windows and Ubuntu separately | Independent original worker process/reboot evidence at PREPARE, local receipt, ACK, archive and upload boundaries; exact generations, no print replay |
| 3 / P0 | Guarded actual post-preview merchant Sandbox PP-021–032/073–075/083 | Provider engineer: approved profile, merchant credentials, authoritative endpoint/header semantics, independently verified GET/webhook/account evidence | Same original order under lost response/404/cancel/settlement/duplicate races; one entitlement. Existing fake-HTTP transport passes do not complete this gate |
| 4 / P0 | Receipt/strip exclusive lane and physical outcomes PP-041–052/079–080 | Engineer then device owner: virtual barriers first; separately enabled isolated test printer | 30 actual visible seconds or one NEXT; one same-ticket receipt; no overlapping RAW sends, no uncertain replay; manually counted paper/copies |
| 5 / P0 | Drive readiness, atomic binding, checksum retry, ACL and retention PP-019/053–057/078/081–082 | Integration owner: approved test Drive and signed-out viewer; deletion requires separate scoped authorization | Correct original folder/URL/bytes, truthful upload pending, no unpaid pool consumption or foreign access; retention/deletion observed independently |
| 6 / P0 | Refund implementation and account/legal gates PP-085–112 | Engineer + security/finance/merchant/legal roles; actual refund transport stays OFF | Classifier + future durable protocol + transport/fence/status evidence independently demonstrated; no fake payout claim |
| 7 / P1 with P0 safety assertions | Actual camera/touch/audio/game/privacy and full 12-design workflow PP-001–020/059–069; PILOT owner observations | Owner Windows device, then Ubuntu mini-PC; same interpreter preflight; separate fresh roots | Real capture/mirror/retake/layout/price observations at 800x1280, 452x900 and actual device; B never sees A pixels/proofs |
| 8 / P0 qualification | Long-duration resource/worker lifecycle, repeated visits, outages and final legacy regression | Engineer/device owner after deterministic blockers; agreed performance budgets | Time-series memory/threads/file handles/disk/queue, original liability and no active-work cutoff; budgets signed off before any performance PASS |

The nine cases without executable required scope are **PP-101, 104, 105, 106, 107, 108, 109, 110, 112**. PP-101 needs provider eligibility/window/account facts; PP-104–110 need the absent durable refund intent/reconciliation/fencing/status protocol; PP-112 needs final copy and merchant/legal review. Other refund cases currently prove guards/classification only and still need connected lifecycle acceptance. BUG-042 specifically protects independent service failure/excess payment from being hidden by proof loss.

## Common protocol and entry criteria — COMMON

1. Record exact runtime SHA, documentation revision, platform and interpreter. Remain on the authorized existing branch; preserve the original journal and evidence. Do not reset occupied roots or switch to an unrelated branch. Read the [device start guide](POST-PREVIEW-DEVICE-TEST-START-HERE.md) and [owner worksheet](PP07-SUPERVISED-WINDOWS-UAT.md) before device execution.
2. Use disposable synthetic images/identities, fresh private roots and isolated fixtures. Never use customer media. Negative crash/resource cases run in virtual adapters or isolated test equipment; never unplug/jam an active production printer. Do not advance real retention clocks or delete cloud photos for a simulated expiry.
3. Reuse the selected launch interpreter/venv. Run its documented preflight before device acquisition. Begin with no paper/no cloud synthetic payment; stop if source, dependency, vault or readiness preflight is blocked. Original-worker restore is blocked until its supported protected implementation exists; refusing an occupied root is not a successful restore.
4. Establish the case preconditions and record initial draft/cart/order/attempt/worker identities as redacted aliases. Apply the specific stimulus at a controlled barrier, then observe actual UI and independent journal/provider/transport facts. Test both callback orders where a race is named.
5. Compare expected and observed criteria, reconcile every original payment/obligation/output, and capture E1–E9. Preserve uncertain/paid state on failure. Finish only when fixture workers are safely stopped/fenced; do not erase original journals to make the next test pass.

Do not treat a fake link as cloud access, SUBMITTED as physical paper, an offered-proof journal flag as observed screen rendering, an OS-byte vault test as full worker restoration, or a refund candidate as refunded money.

## Group setup / dependencies

### G-CAPTURE

Executor: Engineer + device tester. Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

Evidence: Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies. Planning dependency: `HARDWARE_PENDING`. Each case below adds its own trigger and criterion.

### G-FREEZE

Executor: Engineer + integration tester. Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

Evidence: Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls. Planning dependency: `INTEGRATION_PENDING`. Each case below adds its own trigger and criterion.

### G-PAYMENT

Executor: Engineer + provider integration tester. Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

Evidence: Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority. Planning dependency: `PROVIDER_BLOCKED`. Each case below adds its own trigger and criterion.

### G-PROOF

Executor: Engineer + security/device tester. Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

Evidence: Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial. Planning dependency: `SECURE_RESTORE_PENDING`. Each case below adds its own trigger and criterion.

### G-DELIVERY

Executor: Engineer + printer/Drive integration tester. Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

Evidence: Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery. Planning dependency: `HARDWARE_CLOUD_PENDING`. Each case below adds its own trigger and criterion.

### G-HANDOFF

Executor: Engineer + security/device tester. Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

Evidence: Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B. Planning dependency: `SECURE_RESTORE_PENDING`. Each case below adds its own trigger and criterion.

### G-BOUNDARY

Executor: Engineer + cross-component integration tester. Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

Evidence: Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract. Planning dependency: `INTEGRATION_PENDING`. Each case below adds its own trigger and criterion.

### G-REFUND

Executor: Engineer + security/finance integration reviewer. Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

Evidence: Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance. Planning dependency: `REFUND_PROTOCOL_BLOCKED`. Each case below adds its own trigger and criterion.

## Execution phases and authority boundaries

Run software-only missing-scope tests first using fake provider/clock/transport/process barriers. Add implementation where needed before attempting its blocked acceptance test. Do not rerun the successful full suite merely for this documentation revision; rerun relevant source-matched regression after runtime/test changes and required CI once per meaningful increment.

The owner synthetic no-paper/no-cloud route can be tested independently of unfinished refund/provider features after device preflight. It does not certify them. Physical paper requires both `--enable-real-printer --accept-real-paper`; real approved test Drive requires both `--enable-real-drive --accept-public-test-upload`. Keep the launcher's required `--synthetic-payment-only`. Follow the canonical worksheet for full commands and fresh-root rules. Writing this plan neither activates these options nor grants permission for new public uploads.

Actual merchant Sandbox is a separate future guarded profile; the old paid-first profile is not a substitute. Use provider simulator facilities only after merchant setup is verified. No actual bank payment, refund POST, production activation, live deletion or release occurs in this planning task. Actual refund provider capability, finance/legal review and original-worker fencing are independent gates even if synthetic classification passes.

For extended qualification, proposed engineering sampling is a two-hour synthetic multi-visit run followed by a four-hour device run with normal and delayed workers. These durations are planning proposals, not approved customer timeouts or existing PASS evidence. Cover all twelve designs, repeated game/retake/privacy/claim transitions, both layouts and resource pressure. Agree resource ceilings and recovery bounds first; report unbounded/missing budgets as BLOCKED rather than inventing a performance PASS. The prior short repeat-visit run is not a multi-hour soak.

## Evidence E1–E9 and result recording

| Field | Required record |
| --- | --- |
| E1 identity | Run ID, case ID, exact tested SHA, documentation revision, executor role, start/end date with timezone |
| E2 environment | OS/version, interpreter/dependencies, layout, adapter/profile, virtual versus actual camera/printer/Drive/provider, preflight result |
| E3 setup | Fresh-root alias, original state and redacted order/attempt/worker aliases, fault barrier, approved external scope where applicable |
| E4 procedure | Actual actions, callback ordering, clock basis, expected criterion and observed result; deviations and reproduction steps |
| E5 finance | Authoritative independently fetched provider state/matching merchant and amount; original intent lineage, entitlement and PAID/OWED before/after |
| E6 privacy/release | Genuine proof render/visibility event without raw QR, generations/fences, exact PREPARE/local receipt/ACK/archive linkage, admission/denial and B isolation |
| E7 outputs | Camera slots/retakes, manifests/checksums, serialized send counts, SUBMITTED/UNCERTAIN separately from manually observed paper, original Drive binding and upload/ACL state |
| E8 artifacts | Redacted log/artifact location and checksum; no secrets, full claim codes, paid QR screenshots, private photos or live customer identifiers in shared Git evidence |
| E9 decision | NOT_RUN/PASS/FAIL/BLOCKED, partial/full scope, blocker or defect ID, remaining dependency, retest SHA and reviewer role |

Use one record per case/platform/profile execution; overlapping case IDs may link one run only when every criterion and required scope was independently witnessed. Keep prior failures and retests. A partial run may PASS its declared sub-scope while the canonical full acceptance row stays NOT_RUN or BLOCKED.

## Exit gates and continuation

The synthetic supervised candidate remains a conditional device-test candidate. Full acceptance requires every applicable case's exact-source evidence, resolved P0 defects, protected Windows/Ubuntu original-worker restore, actual paper/cloud/provider/security observations and the appropriate merchant/legal/release reviews. Refund and production gates remain disabled/unapproved until separately satisfied. Do not infer a release from 1,744 passing software executions or from this plan.

Sources reviewed: canonical 112 matrix, complete owner decision ledger, security/state contract, refund/lost-proof policy, executed 5 November simulation and JSON case review, supervised 26-row worksheet, 50-row unattended handoff contract, AR traceability/readiness and repository development protocol. Canonical meanings and historical evidence remain unchanged.

Documentation validation: [record of inventory, source-method and link checks](evidence/pp07-test-plan-documentation-validation-2026-11-05.json). This record does not contain application-test execution results.
