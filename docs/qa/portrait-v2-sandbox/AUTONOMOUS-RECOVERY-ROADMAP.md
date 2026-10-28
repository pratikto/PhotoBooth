# Autonomous recovery — Codex execution roadmap

**Document status: APPROVED PLANNING / IMPLEMENTATION NOT STARTED**, 28 October 2026  
**Scope:** `feature/portrait-kiosk-v2-next` only; no master/branch/default/production operations  
**Baseline audited:** `2e5efe5d281a93fe8d22e53309a50147764d2939` (subsequent documentation commits do **not** count as new functional source tests)  
**Read first:** [Master specification](AUTONOMOUS-RECOVERY-MASTER-PLAN.md), [Midtrans contract](MIDTRANS-PROVIDER-CONTRACT.md), [Test matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md), [Operations](AUTONOMOUS-RECOVERY-OPERATIONS.md), `AGENTS.md`, `docs/README.md`, `docs/DEVELOPMENT_PROTOCOL.md`, `docs/DEVELOPMENT_HANDOVER.md`, `docs/DECISIONS.md`, `docs/FEATURE_STATUS.md`, `docs/bug_tracker.md`, `docs/portrait-kiosk-v2-technical-design.md`, `docs/next_step.md`, and relevant QA links. Never inspect `old`.

## How Codex must execute

1. Refresh origin of **existing** branch. Record remote HEAD, dirty state, platform and relevant provider/service versions. Confirm original implementation and tests before modifying any code. Never use a new branch; do not merge or change default/master.
2. Read relevant authoritative docs **fully before** each code stage (owner's primary rule). The master spec is target intent, not proof of completed behavior. Record differences with existing source/decision history.
3. Stage in the numbered order below; start with **documentation-only contract/QA work**, then backend durability, then local photo durability, then GUI, then operations. No speculative provider keys, real refund, webhook deployment or production connectivity.
4. For every stage record: issue ID, prior HEAD, scope and owner decision, source modules, data migration/rollback, contracts, failure windows, exact focused tests, expected PASS/FAIL and device/merchant NOT_RUN items. Write migration tests before schema change.
5. Implement minimal reuse-based increments; commit and push each logical stage to existing branch; verify remote HEAD before next stage. Do **not** force-push. CI credits: targeted/focused first, one full applicable regression after final code stage, no full CI on documentation-only commits.
6. Update changelog, feature status, test ledger, bug register and handover **after code**, never preemptively mark an implementation or test complete. Record source SHA, command, OS, exact PASS/FAIL/SKIP/NOT_RUN, screenshot and provider evidence. Keep source-specific historical reports intact.
7. Stop only the dependent substep if external merchant API guarantee/credential, laptop, Linux hardware, refund policy or security contract is missing. Continue isolated safe code/tests; never guess results or ask to reset/delete journal.
8. Release requires a separate explicit owner instruction. Complete a controlled pilot, compare to acceptance criteria and preserve all financial/photo obligations.

## Mandatory micro-increment checkpoint and five-hour session continuity

**Owner preference (28 October):** Do not defer Git pushes until an entire AR
stage or the end of a ChatGPT/Codex session. The five-hour usage limit can
interrupt progress; each meaningful, safely tested substep must be remotely
recoverable.

- Break AR-00–AR-13 into small, independent substeps (AR-XX.a, AR-XX.b, etc.).
  After each safe, reviewable substep: focused tests -> update related docs ->
  commit -> push existing branch -> verify remote HEAD. Prefer checkpoint
  opportunities every ~30–45 minutes of active coding, never empty commits.
- Update [the single recovery checkpoint](AUTONOMOUS-RECOVERY-CHECKPOINT.md)
  and the repository handover with current substep, pushed SHA, tests, open
  risks, next exact action, and any local-only changes. Publish a docs-only
  checkpoint before the chat/session limit; preserve full report accuracy.
- Never push unsafe/incomplete runnable code simply to save progress. Use
  self-contained tests/docs or explicitly disabled safe increments; label
  partial work NOT VERIFIED. If dirty changes remain on the local machine,
  record that they are **not backed up to GitHub**. Do not commit merchant keys,
  recovery tokens, customer photos, local databases or unrelated edits.
- In a new session inspect branch/dirty status and remote history first, read
  the latest checkpoint and source evidence, and start at the first incomplete
  substep. Do not repeat completed stages, force-push, reset journals or merge
  to master. Preserve one final full regression after the final functional
  change and the existing security/merchant gates.

## Canonical stage ledger

| Stage | ID | Deliverable | Precondition | Required exit gate |
| --- | --- | --- | --- | --- |
| 0 | AR-00 | Baseline, schema/state invariants and review | Read all authoritative docs and current source | Written field/state contract and replayable offline fixtures |
| 1 | AR-01 | Safe ambiguous charge-creation recovery | AR-00; provider uncertainty documented | Charge before-send/after-send/no-provider/status-404 scenarios hold same identity |
| 2 | AR-02 | Fresh payment reconciliation & background retry | AR-01 | Reconciliation never trusts local PAID alone; no duplicate grant; retry bounded |
| 3 | AR-03 | Durable entitlement/fulfillment ledgers | AR-02 | Unique order -> grant -> one local transaction; paid obligation survives client closure |
| 4 | AR-04 | Capture-intent/manifest crash consistency | AR-03 | No overwrite after every injected crash point; orphan checkpoint deterministic/held |
| 5 | AR-05 | Photo reconstruction/retake/multi-design resume | AR-04 | Three-photo/one-retake/outputs/copies restored without replay |
| 6 | AR-06 | Customer capability and private self-service claim | AR-05 | Old private data not shown to next customer; stolen/expired token rejects |
| 7 | AR-07 | Native recovery GUI and checkout flow | AR-06 | No dead-end RECOVERY/UNCERTAIN; responsive, bounded, customer-led countdown |
| 8 | AR-08 | Prepayment health + paid-unfulfilled remedy | AR-03 and AR-07 | Camera/storage/print preflight; postpaid faults create durable claim without double billing |
| 9 | AR-09 | Operator exception + safe kiosk-release policy | AR-03/AR-06/AR-08 | Audited operator, no false refund/completion; new visitor cannot steal old grant |
| 10 | AR-10 | Watchdog/restart and hardware isolation | AR-07/AR-09 | Bounded non-replay restart only with provably safe gate and leases |
| 11 | AR-11 | Public webhook backend / provider adaptation DESIGN + opt-in test | AR-02 and merchant approval | HTTPS/auth/inbox/retries proven; no automatic deployment |
| 12 | AR-12 | Failure injection, regression, Windows/Ubuntu/merchant evidence | All applicable | Required test matrix PASS at pinned SHA; external gates separately recorded |
| 13 | AR-13 | Production readiness and owner release decision | AR-12 + provider/operational contracts | Explicit approval; no automatic merge/production enablement |

**P0 before unattended pilot:** AR-01 through AR-09 and payment/capture/privacy/crash tests. **P1 for safe automatic restart:** AR-10. **P1 for production-ready external callback:** AR-11. AR-12/13 are mandatory gates. There is no acceptance of unsafe shortcuts to meet a schedule.

### AR-00 — contract and fixture freeze

Read the exact SHA baseline for `checkout_store.py`, `checkout_backend.py`, `qris_session.py`, `qris_api.py`, `midtrans_sandbox.py`, `kiosk_v2/photos.py`, `transaction_store.py`, `kiosk_v2/sandbox_views.py` and tests. Enumerate all existing local and server fields, schema versions, allowed transitions, recovery actions and legacy ambiguity. Freeze a normalized state machine and interface design, including optional fraud-status semantics and provider evidence. Define migration vs fallback; source-only. **Do not claim success from publishing planning documents.**

### AR-01 — uncertain charge creation / provider idempotency

Write failing deterministic tests for crash before network, provider accepted-but-response-lost, provider never received request, GET not-found/lag and multiple retries; preserve one local order ID, amount, merchant, booth, checkout key and request fingerprint. Build durable create-attempt state and bounded reconciliation. **Important external gate:** the five-minute `X-Idempotency-Key` note in Midtrans *Invoice* documentation is NOT a proven Legacy `/v2/charge` contract. Do not blindly add that header or repeat a charge. Only enable repeat same-order charge if official confirmation and controlled Sandbox evidence prove semantics, with explicit blocked state otherwise.

### AR-02 — provider evidence and automatic reconciliation

Implement a narrow, booth-authenticated, **read-only provider reconciling** path for any unfinished payment, including existing `RECOVERY` and previously cached `PAID`. Maintain separation from operator `recovery/resolve`. Add rate-limited polling ~10s pending, proposed jittered 10/20/40/60s network backoff and immediate single recovery after restart/connectivity restoration. Differentiate `unknown`, `pending`, `terminal`, `paid`, `refund/review` and `provider-not-found-unproven`. Verify signed notifications, amounts, merchant and source; no new grant from stale status. Test cancellation/settlement race, repeated stale events and out-of-order reports.

### AR-03 — distinct ledgers and durable atomic admission

Introduce a migration-safe fulfillment representation linking one payment to one claim/grant, frozen quote/template/copy hashes and one preallocated local transaction ID. One unique allocation record per paid order and one unique order per transaction, separate payment obligation from UI visit and media delivery; `closed` or `abandon` never equals `fulfilled`. Write exact operation IDs before invoking external effects, one-use CAS/grants, reconciliation after lost response and restart, strong booth/merchant isolation and no arbitrary 'latest folder' recovery. Preserve existing active journal and historic fixtures.

### AR-04 — photo write-ahead capture

Write intent `CAPTURE_INTENT(session,slot,attempt,expected filename,operation ID)` before hardware/file I/O. Save to unique temp file, fsync file (and directory on supported OS), atomically rename, verify size/hash/image decode and commit manifest metadata with a consistent state; do not replace an existing target on uncertain retry. On restart check intent+file+manifest combinations, either deterministic finalization or quarantine with reason. Retake operation separate from first captures with durable selection and consumed quota. Cross-platform Windows/Ubuntu filesystem semantics tested; no false atomic-multi-file claim.

### AR-05 — reconstruct original customer photo workflow

Restore exact catalog template snapshot, session plan, copy count, originals and retakes using metadata and validated images. Keep 3 originals per design and 1 retake per design; validate completed outputs and not rewrite. Restore partial capture (1/2/3), selected retake before commit, retake after commit, review/result, completed design and current design in multi-design. After recovery, never auto-trigger shutter or print, require a new customer consent/countdown. Expired/missing files go to paid-unfulfilled remedy rather than silently starting over.

### AR-06 — secure customer self-claim

Generate high-entropy booth/order-bound customer capability early and only after durable order write; hash at rest and never log. Show a QR ticket/short reference label and optionally a convenience code, but **six digits alone must never authorize private photo access**. Test token binding, expiry, single-use, replay, brute-force limits, device loss, claims after purchase and late customer return; require ownership proof before photo preview. The token is not merchant key, operator PIN or a verified payment result. Decide token validity, ticket delivery/support and remaining retention window before release.

### AR-07 — native unattended UX

Replace RECOVERY blank page with background `RECONNECTING/VERIFYING/RECOVERING` and eventual `CLAIM_REQUIRED/RESUME_READY/SUSPENDED/OPERATOR_REQUIRED`. Keep old order unchanged, display actionable recovery status without leaking PII, never show previous photos before customer claim, throttle worker/event revisions, prevent duplicate taps, reenter camera only on deliberate user action. Render 800×1280 and 452×900, include mouse/touch/minimize/resize/close; preserve Sandbox copy-link and centered brand QR, full price/no game promo and sandbox printer/Drive-off.

### AR-08 — readiness and paid remedy

Before starting charge, check camera, disk free capacity, writable output, template data, printer when purchased and readiness age; do not require always-online Drive when existing offline policy allows a verified slot. After paid fail, separate `PAID_UNFULFILLED` from `CLOSED`; preserve receipt/evidence, issue claim, retry safe fulfillment only after device health restored and customer's proof, otherwise open explicit approved remedy. Never fabricate refund or complete.

### AR-09 — operator path and safe customer release

Complete existing PIN-based Sandbox operator inspect/resolve UI/launcher integration, but reserve it for ambiguous cases. Keep PIN only in backend startup secrets, not child GUI env, args, journals or reports; audit exact reason/action. Design new 'suspend and release booth' operation with fencing and acknowledgments. Free camera/UI for subsequent customer **only after** prior financial/service rights are isolated and new customer cannot obtain them. Never simply abandon a paid order and clear ledger. Require remote admin auth design before production; no default public reset.

### AR-10 — watchdog & recovery supervisor

Existing watchdog is intentionally observation-only. Preserve it until after AR-09. Define bounded restart count, startup probe, false-positive detection, safe worker stop and one-owner lease; avoid restarting while photo writes/print submission are in unknown window. On reboot automatically reconcile private state, but never auto-display old photos, start shutter, print, charge or unlock another entitlement. Windows development and Ubuntu mini-PC service checks distinct; target tablet/Android architecture needs separate platform-specific supervisor acceptance, not assumptions from desktop Kivy.

### AR-11 — webhook/backend separation

Do not expose `127.0.0.1` loopback as a production callback. Design secure HTTPS backend with verified signature, inbox/durable acknowledgment, idempotent/out-of-order event reconciliation, bounded queue and monitoring. Implement only with separately approved infrastructure; use official Midtrans merchant settings and controlled merchant Sandbox tests. Prepare legacy-vs-BI-SNAP adapter boundary but no automatic migration, no key leaks or unsupported request header guesses.

### AR-12 — comprehensive validation

Use [mandatory failure-injection matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md): provider failures, file intent and manifest crash points, retakes, multi-design, privacy takeover, retention/print idempotency, long offline, server restart, DB/WAL/checkpoint locks, stale callback and paid-unfulfilled. Focused tests each stage, one final full regression at last functional SHA, native pixel captures both sizes, Windows actual restart + camera + display, Ubuntu actual service/mini PC, merchant actual simulator, paper/Drive separately if included. Preserve existing P5 new Sandbox integration cycles and old monitoring reports without replaying unrelated accepted tests. Never infer live merchant PASS from fake provider.

### AR-13 — release controls

Explicit owner decision only, with defect severity triage S0/S1, current legal/merchant/compensation policy, BI-SNAP migration determination, real device/provisioning logs, rollback/fencing migration, bounded staged pilot, monitoring/alerts and privacy retention validation. No default/master change, production charge, deployment or cloud deletion from this roadmap.

## Codex per-stage handoff template (fill each iteration)

```text
Task: AR-XX / title
Status: PLANNED | IN_PROGRESS | IMPLEMENTED | VERIFIED | BLOCKED
Branch: feature/portrait-kiosk-v2-next
Remote HEAD before: <full sha>
Tested functional SHA: <full sha>
Current source compatibility + files read: <list>
User approval/constraints: <explicit source>
Changed files: <list>
Persisted data migration and rollback: <evidence>
Failure cases tested: <IDs from test matrix>
Focused command/results: <PASS/FAIL/SKIP/NOT_RUN>
Final full regression: <ONLY after last functional stage>
Windows device: <PASS/FAIL/SKIP/NOT_RUN>
Ubuntu device: <PASS/FAIL/SKIP/NOT_RUN>
Midtrans merchant: <PASS/FAIL/SKIP/NOT_RUN>
Print and Drive: <PASS/FAIL/SKIP/NOT_RUN>
Unresolved dependency: <fact, no guess>
Commit/push and verified remote SHA: <full sha>
Next permitted stage: <AR-XX>
```

Codex must not cherry-pick feature branches, mutate historical customer data, reset orders, infer approvals, or mark entire roadmap 'DONE' after docs publication.
