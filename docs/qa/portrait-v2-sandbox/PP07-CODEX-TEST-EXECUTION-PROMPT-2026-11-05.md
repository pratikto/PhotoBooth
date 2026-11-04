# Codex execution prompt — complete post-preview test campaign

This is a portable handover for a fresh Codex account/session. Copy the prompt below into the new session, or instruct Codex to read and execute this file from the authorized repository branch. It relies on repository evidence, not access to the previous chat, credentials, local virtual environments or temporary files. Publishing this prompt is documentation only; it does not record new test executions.

---

You are continuing Meong Photobooth development and executing its complete post-preview test plan. Treat this as an execution-and-repair task, not a request for another plan. Read the repository contracts, inspect the actual source, execute all safely available tests, repair reproduced defects, close approved missing software coverage in small increments, and record truthful remaining dependencies. Continue autonomously until the executable campaign is complete or specific external prerequisites remain. Do not require the owner to test the kiosk before completing the independent software simulations available to you.

Communicate with the owner in Indonesian. Write engineering documentation in English. Do not assume that anything from a previous Codex account exists in this environment.

## 1. Repository, branch and historical checkpoint

- Repository: `https://github.com/pratikto/PhotoBooth`.
- Only authorized delivery branch: `feature/post-preview-qris-checkout`.
- Verified branch HEAD immediately before this prompt was added: `59c63a86ac4dcac6a72150d27f9f57c5334bfbcc`.
- Test-plan delivery commits: `74ab8cb57ffd429fcf4aec12b11ca90450fa5f15` and `59c63a86ac4dcac6a72150d27f9f57c5334bfbcc`.
- Last fully verified runtime/test source: `acbac15842b59d5005075f2fbc7e87978323b158`. Subsequent test-plan commits changed documentation only.
- Historical all-opt-in local result at that source: **1,744 PASS, zero failure/error/skip**, 476.832 seconds. There were 1,654 normalized distinct test IDs because existing imported fixtures repeat some executions. Do not count executions as unique acceptance cases.
- Matching inspected CI: `https://github.com/pratikto/PhotoBooth/actions/runs/41906929920`, all three jobs SUCCESS: **546 Windows + 546 Ubuntu + 62 native Kivy**, zero failures/errors/skips.
- These are historical source-specific results. Verify the current remote HEAD and inspect any later commits; this prompt and future continuation commits will naturally make it newer than `59c63a8`. Never reset to the historical SHA or attribute its PASS results to a new runtime patch without testing.

Start with read-only repository discovery, including `git status --short`, `git branch --show-current`, `git rev-parse HEAD`, `git log -5 --oneline`, the origin URL and `git ls-remote origin refs/heads/feature/post-preview-qris-checkout`. Identify the actual checkout path instead of assuming `/workspace` itself is the repository.

If no checkout exists, a fresh isolated clone of the **existing remote branch** is appropriate. If the attached checkout is on another branch or contains unrelated local changes, preserve it and use a separate clean checkout/snapshot of the authorized remote branch. Do not blindly switch, pull, reset, clean, overwrite or stash unrelated work. Do not create a new branch, merge master, change the default branch, force-push, rewrite history or deploy. In a clean checkout already on the correct branch, updates must be fast-forward only. If the remote advances while you work, fetch and inspect the difference before continuing; never overwrite newer work.

The previous environment's unrelated checkout was left clean on branch `work` at `0fbf15829d1537a7f18990b492b1e5934f21c0f8`; remote work used an independent snapshot and external index. That arrangement is historical context, not a requirement that the new account reproduce those paths. Use an ordinary clean checkout of the correct existing remote branch when available. If constrained to plumbing, verify the exact remote parent and push only an explicitly constructed descendant to the authorized ref; never accidentally commit/push the unrelated checkout's HEAD.

If repository authentication is missing, report the exact access prerequisite without requesting secrets in chat. Do useful available read-only/local work, preserve it accurately, and never claim that a failed or unavailable push saved progress remotely.

## 2. Required reading before any code change

Read `AGENTS.md`, `docs/README.md`, `docs/DEVELOPMENT_PROTOCOL.md`, `docs/DEVELOPMENT_HANDOVER.md`, `docs/FEATURE_STATUS.md`, `docs/bug_tracker.md`, and the relevant architecture, decisions, checkpoint and backlog entries. Read applicable nested instructions. Exclude the entire root `old` tree from searches, archives, scans and tests; do not inspect, copy, modify or use it as a reuse source.

Then read these files under `docs/qa/portrait-v2-sandbox/` thoroughly:

1. `PP07-COMPLETE-TEST-PLAN-2026-11-05.md` — master plan, priorities, dependencies, COMMON protocol and evidence E1–E9.
2. `PP07-COMPLETE-CASE-PROCEDURES-2026-11-05.md` — setup, stimulus, criterion and remaining scope for every PP case.
3. `PP07-INHERITED-AND-DEVICE-TEST-PLAN-2026-11-05.md` — PILOT, versioned UAH and actual AR stage definitions.
4. `evidence/pp07-complete-test-plan-2026-11-05.json` and `evidence/pp07-inherited-device-test-plan-2026-11-05.json` — machine-readable inventory.
5. `evidence/pp07-acceptance-execution-register-2026-11-05.csv` — initially blank execution register; preserve historical observations when adding runs.
6. `POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md` — canonical expected behavior, not something to weaken to make tests pass.
7. `POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md`, `POST-PREVIEW-QRIS-OWNER-APPROVED.md`, `POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md`, `POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md`, and `POST-PREVIEW-QRIS-OPERATOR-AND-REFUND-ESCALATION.md`.
8. `PP07-END-TO-END-SIMULATION-2026-11-05.md`, `evidence/pp07-full-simulation-2026-11-05.json`, `evidence/pp07-simulation-case-review-2026-11-05.json`, and the linked timed synthetic journey evidence/script.
9. `POST-PREVIEW-DEVICE-TEST-START-HERE.md`, `PP07-SUPERVISED-WINDOWS-UAT.md`, `POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md`, and `PP07-SOFTWARE-TRACEABILITY-2026-11-04.md`.
10. Relevant original UAH/AR contracts, particularly `UNATTENDED-SESSION-HANDOFF-OWNER-APPROVED.md`, `AUTONOMOUS-RECOVERY-ROADMAP.md`, `AUTONOMOUS-RECOVERY-TEST-MATRIX.md`, and `AR13-READINESS.md`.

Follow linked specifications when a change affects their contracts. Latest implementation evidence supersedes older dated implementation-status banners; latest approved owner policy remains binding. Historical DESIGN ONLY, branch and CI statements must not override the current explicit execution assignment or the authorized PP branch. Preserve history rather than deleting inconvenient failures or decisions.

## 3. Starting inventory and truthful status

The current campaign inventory is **188 case rows**: PP-001–112, PILOT-01–26 and UAH-001–050. AR-00–13 are **14 stage gates**, not additional acceptance cases. Overlapping case IDs and repeated platform executions do not represent unique code paths. Unrelated queued Operator Settings features are outside this campaign.

At handover:

- PP: 103 cases have executed **partial** software evidence; nine have no executable required implementation/external review scope. **All 112 full acceptance outcomes remain NOT_RUN.**
- The nine missing-scope IDs are **PP-101, PP-104, PP-105, PP-106, PP-107, PP-108, PP-109, PP-110, PP-112**. They are not the entire remaining backlog.
- PILOT: **24 NOT_RUN, 2 BLOCKED** (actual merchant Sandbox and actual refund).
- All 50 UAH full acceptance outcomes remain NOT_RUN in the consolidated plan; original source-specific legacy evidence is retained separately.
- Actual merchant post-preview profile, full protected original-worker restoration, physical device acceptance, cloud retention/ACL evidence, real refund capability and production release remain separate gates.

Keep separate fields for existing software evidence, new run result, declared sub-scope, full acceptance result and remaining dependency. Planning labels such as HARDWARE_PENDING or SECURE_RESTORE_PENDING are not executed outcomes. A synthetic sub-scope can PASS while full acceptance stays NOT_RUN/BLOCKED. PASS requires observed evidence; SKIP is not PASS; a cancelled CI run is not success or product failure. Record unavailable prerequisites rather than marking a whole group passed from one related unit test.

## 4. Authority and safety boundaries for this execution

You may execute isolated software tests, add meaningful missing tests, fix reproduced defects and implement the approved software behavior needed to exercise these cases in small guarded increments. You may prepare provider/refund adapters and test them against deterministic fake transports. Preserve existing architecture and reuse working features. Do not invent product policy, provider semantics, timeouts, cryptography, refund promises or legal approval. New unresolved policy decisions remain explicit dependencies; continue independent work instead of blocking the entire campaign.

Use synthetic media, ephemeral isolated state and redacted identifiers. No real bank payments, production activation, live refund requests, public uploads, photo deletion, printer paper consumption or actual customer-data access are authorized merely by this prompt. Separate existing scoped owner approval and provisioned test resources are required for external effects. Do not activate real printer/Drive flags automatically or remove restrictions to get a green result. Physical acceptance requires actual observation; offscreen CI cannot supply it.

Read managed environment/skill instructions when applicable. Inspect capability names and readiness without printing secret values. Use provisioned secure credentials only through their intended interface; never commit tokens, provider keys, vault material, paid/proof QR screenshots, customer photos, SQLite databases or unredacted logs. Do not disable TLS/proxy or platform security to work around access problems.

Do not request permission for every routine test, reversible fix, documentation update, commit or push already covered by this task. If a genuinely missing external prerequisite is required, state the exact missing resource/approval and case IDs; finish unrelated authorized work. Do not automatically delegate to subagents without applicable authorization.

## 5. Invariants every repair must preserve

1. Three original photos and at most one retake **per selected design**, up to twelve designs. Copies do not create captures. Retake consumption does not reset after deselect/reselect or restart. Protect committed image/manifest lineage and pinned artwork.
2. All purchased previews before checkout; edits permitted only before durable provider-create intent. UI price, immutable server quote, artifacts and provider amount must match. No unpaid paid-strip print, public photo upload/download, or completed paid obligation from compose callbacks.
3. One logical purchase and entitlement across all attempts. QR1→QR2→QR3 only after freshly verified unpaid expiry and continuation by the original active visitor; no QR4. Cancel, departure, minimize, 404 and UNKNOWN are distinct. Webhooks require independent fresh authoritative verification. Never repeat ambiguous create POST or invent a provider idempotency header.
4. Distinct pre-PAID CCP and post-PAID Recovery Ticket. Proof cannot become a public paid-photo capability before PAID; reject wrong scope/type, forged, revoked, expired or replayed proof. Verify proof atomically through final occupancy mutation, including changes during provider GET.
5. For new post-preview PAID orders, **always** display the original ticket QR + full code for 30 actually visible seconds or one NEXT, while the **same** original receipt is enqueued once concurrently. Successful/late printer SUBMITTED must not skip, dismiss, reset or re-present the screen. No extra CCP scan for the intact original paid owner lease. Clear private pixels on dismissal/privacy boundaries.
6. SUBMITTED is transport acknowledgment, not physical paper. Serialize exclusive receipt/strip sends. SENDING/UNCERTAIN and partial bytes never cause blind replay; preserve actual partial delivery and original obligations.
7. A/B separation: no stale camera, GUI, compose, payment, print or upload callback from A can mutate B, reveal A pixels/proofs or allocate service again. Safe isolation requires exact PREPARE → local worker receipt → ACK → durable archive identities/generations. Financial status alone never frees an uncertain camera/print lease.
8. Protected persistent credentials must use supported OS protection. Windows cross-process DPAPI byte tests do not prove original-worker/device/reboot/reinstall restoration. Ubuntu protection is not supplied by the existing platform adapter; no plaintext fallback or fresh invented token. Missing/corrupt vault state fails closed while PAID/OWED remains.
9. Unpaid visitors cannot claim READY Drive capacity/public upload. Paid binding uses the correct original booth/folder and independently verified URL. Hold strips when URL is unverified; report upload pending truthfully. Idempotent upload retry must not resend paper. Cloud/local retention and ACL access need their own evidence.
10. Genuine proof loss alone is NO_AUTO_REFUND_PROOF_LOST and never authorizes tokenless private recovery. A proof never actually offered, independent irrecoverable merchant failure, or excess verified settlement is not customer negligence. Refund-first is conditional on verified original settlement, worker safety, durable idempotency, merchant capability and legal controls. Classifier candidates are not payouts. Requested/processing is not confirmed money in the customer's account.
11. Preserve legacy paid-first BUG-027/028 and Meong Fly behavior in their own profiles. Legacy UAH printer-success/fallback expectations must not weaken mandatory post-preview screen policy. Post-preview DEMO game wins cannot create untrusted discounts. Do not start unrelated settings or production work.

## 6. Execute in meaningful waves

### Wave A — preflight, inventory and first connected gaps

Create a dated execution campaign record, actual environment/capability inventory and append-only or versioned run ledger. Reference every PP/PILOT/UAH ID and AR stage without copying a PASS from a different source/profile. Record source SHA before running tests.

Reuse a working Python 3.12 venv/interpreter where available. Windows and Ubuntu need separate environments; never recreate a working owner venv blindly. Follow current requirements, runner and workflow instead of assuming packages/models from the previous account exist. Inspect `tools/run_kiosk_unittests.py` and `.github/workflows/post-preview-qris.yml`; keep safety defaults and real delivery OFF.

Start with connected **PP-040/087/088**: original payment becomes PAID when CCP was never offered, or receipt SUBMITTED occurs while the mandatory first screen never actually rendered. Observe real connected presentation/payment/remedy journals, not only a mocked boolean named “offered.” Add focused regressions for genuinely missing scope and repair actual defects. Keep genuine proof-loss-only cases distinct from independent merchant fault. Preserve BUG-040/041/042.

Do not run the entire already-passing historical suite just to demonstrate activity. Use focused tests to validate setup and current changes. If current HEAD contains later runtime changes or evidence is missing, select baseline verification appropriate to that uncertainty and explain why.

### Wave B — process death, secure restore and handoff

Execute virtual and independent-process fault barriers around save/retake, create ambiguity, paid proof presentation, worker isolation, upload and release. Cover PREPARE success/worker failure, local receipt/ACK loss, ACK success/reply loss, archive/fsync failure and stale generations in both callback orders. Exercise A locks → Ads → B admission/checkout → A returns busy/free, original paid obligations and original media/quota.

Implement missing approved software seams where possible. A new fixture, SQLite reopen or occupied-root refusal is not full original-worker restoration. Run Windows/Ubuntu protected integration only where supported; otherwise document the exact remaining implementation/device dependency. Continue executable crash/fencing tests even if OS hardware acceptance is blocked.

### Wave C — payments, ticket/strip lane, Drive and refund protocol

Use the actual payment client through fake HTTP transport for ambiguous POST/404/expiry/cancel/late/duplicate settlement and same-order restart races. Preserve one entitlement. Guarded actual post-preview merchant Sandbox is separate; the legacy paid-first profile and mock PAID button do not certify it.

Use barriers to hold receipt transport while the 30-second screen and NEXT proceed, then queue photo strips; prove exclusive sends, exact copies and no uncertain replay. Run both portrait layouts and cross-component timing. Use an actual event loop/monotonic elapsed time when claiming visible-timer behavior; fake-clock guards alone do not prove render duration.

Exercise Drive precharge readiness versus postpaid binding failure, checksum retry, authorized upload during uncertain print, foreign folder rejection and zero unpaid allocation. Real ACL/download/retention remain separate authorized external tests.

For refund cases, keep existing classifier tests distinct from absent durable original refund intent/key, response-loss reconciliation, verified status, original-charge binding, stale output suppression and in-flight worker fencing. Build approved missing software behind disabled external transport and use mocks where feasible. Never invent merchant activation, eligibility windows, issuer/acquirer/balance facts, financial authorization or legal signoff. Keep PP-101/104–110/112 blocked at any unimplemented/external scope until its exact prerequisite is satisfied; update the inventory if software scope is actually implemented and tested.

### Wave D — complete journeys, native UI, optional inference and qualification

Run connected journeys across one/two/twelve designs; retakes and copies; previews and quote freeze; CCP; synthetic PAID; mandatory ticket; serialized virtual receipt and strips; safe upload; privacy; A/B handoff; return claim; duplicate/late callbacks; legacy regression. Cover 800x1280, 452x900 and any genuinely available device layout.

Historical full execution used Python 3.12, the repository runner, `PHOTOBOOTH_TEST_GUI=1`, `PHOTOBOOTH_TEST_AUDIO=1`, `PHOTOBOOTH_TEST_VIDEO=1`, an appropriate SDL/Xvfb software display and dummy audio. Keep camera/face/palm/live delivery disabled outside explicitly isolated fixtures. Inspect current opt-in tests for their actual environment and asset requirements before running. Use verified public MediaPipe samples/model with pinned hashes from `evidence/pp07-full-simulation-2026-11-05.json` if executing model inference; keep large assets outside Git. Fake inference does not count as real model execution. Missing platform/dependency/model capability must be resolved or reported explicitly, never hidden by an unexplained skip.

After the final meaningful runtime change, run one appropriate complete regression and required source-matched CI; inspect actual job conclusions/logs, counts and artifacts. Wait for completion without blocking progress communication. A source push or queued run is not CI PASS. Preserve failures, fixture mistakes, corrections and retests. Repeat broad runs only after a relevant new change, failure or unresolved concern. Documentation-only checkpoint pushes do not require successful CI to be retriggered; inspect workflow path filters.

The timed synthetic diagnostic is under `evidence/run_timed_synthetic_journey.py`. Inspect it before reuse; keep it isolated and never point it at an occupied owner root. Historical measured ticket duration was 30.033 visible seconds in a 73.362-second synthetic journey; this is evidence for that recorded run, not a promised result for a future patch or device.

The master plan proposes two-hour synthetic and four-hour device soak samples; these are proposed qualification durations, not approved inactivity rules or existing PASS results. Conduct useful bounded resource/lifecycle sampling after deterministic fixes, recording duration, memory, threads, handles, disk, queues and repetitions. Do not impose an arbitrary acceptance ceiling: unresolved budgets/recovery bounds need review, and shortened runs cannot be called multi-hour qualification. Preserve checkpoints during long runs and before session limits.

### Wave E — owner/device and external remainder

Only after independent executable software simulations are completed or precisely blocked, prepare the remaining owner worksheet with actual source/interpreter/preflight and outstanding case IDs. Keep camera, touch, speaker, actual paper/cutter, signed-out Drive access, Windows device behavior and Ubuntu mini-PC acceptance as actual observations. Never mark owner rows passed from synthetic CI.

Default owner pilot remains `--synthetic-payment-only` with a fresh private root, no paper and no cloud. Full protected restore is separate from the launcher's refusal of old/nonempty/symlink roots. Real paper requires both `--enable-real-printer --accept-real-paper`; real approved test Drive requires both `--enable-real-drive --accept-public-test-upload`, and both need appropriate existing scoped authorization. Do not turn them on during cloud testing. Never deliberately unplug/jam an active production printer; use virtual adapters or isolated test equipment.

## 7. Evidence, issue discipline and status updates

For each run, capture the master plan's E1–E9: case/run ID, exact tested source and documentation revision, time/timezone, OS/interpreter/profile, setup/fault barrier, redacted original identities, actual procedure/expected/observed, authoritative provider and liability facts, proof visibility/privacy/release generations, capture/output/cloud observables, redacted artifact location/checksum, outcome, dependency/defect and retest reference.

Use the current date/time, not the historical November date, for new execution. Record Asia/Jakarta when reporting owner-local time and label UTC when used. Keep raw sensitive artifacts outside version control; share only sanitized evidence. Do not scan/print secrets while collecting diagnostics.

Record reproducible product defects in `docs/bug_tracker.md` using the next unused ID after inspecting the current register. Do not reopen or renumber BUG-040/041/042 because their original reproduction appears in historical logs. Separate an incorrect test harness/expectation or unavailable environment from a product defect. Prefer a failing meaningful regression before a targeted fix; do not weaken contracts, delete a failing assertion, skip a risk, mock away the failure or reduce durability just to pass CI.

Update current campaign evidence, affected matrix/register, feature/checkpoint/handover/index references and code documentation together. Preserve canonical criteria, all 188 case identifiers, actual AR definitions and profile/version boundaries. If one run covers multiple IDs, state exactly which criteria it independently witnessed. Do not invent an overall “all tests PASS” while platform/provider/hardware/legal acceptance is outstanding.

Send concise progress updates during work: what was actually verified, which defect/gap is being addressed, what was pushed and what remains blocked. Do not replace execution with repeated plans or unnecessary confirmation questions.

## 8. Mandatory incremental commit, push and continuation policy

This owner explicitly wants progress saved before account/session limits. After **each meaningful safe tested increment**:

1. Review the diff and explicit changed-file list; keep unrelated files, secrets and local data out. Run focused verification and `git diff --check` as appropriate.
2. Commit the coherent source/tests/documentation or evidence-only increment to the authorized existing branch. Do not push knowingly broken, unsafe or misleading partial runtime code to meet a deadline.
3. Immediately push normally to `feature/post-preview-qris-checkout` and independently verify the remote SHA, for example with `git ls-remote origin refs/heads/feature/post-preview-qris-checkout`. A local commit or stash alone is not a backup.
4. Record the tested source SHA separately from a later documentation-only checkpoint SHA. If using an external index/snapshot, compare the staged diff to its explicit verified parent, not the unrelated attached checkout's HEAD.
5. Preserve concurrency: on push rejection, inspect remote changes and reconcile safely; never force or overwrite newer work. Report any access/push blocker honestly.

Aim for reviewable checkpoint opportunities around 30–45 minutes of active work, without empty/time-based commits. Before reaching context/usage limits, stop starting large new tasks and publish a continuation record containing: current verified remote commit, first unfinished case/substep, exact next command or action, tested source/results/platform/profile, changed files, active jobs, remaining blockers, and any local-only work that is **not** recoverable from GitHub. Push and verify that record. Never end with only an unpushed patch while claiming progress is safe.

## 9. Required completion report

Finish with links to the updated execution report, case register, bug/evidence records, pushed commits and exact-source CI when applicable. State:

- What was actually executed and fixed, with counts separated by software executions, unique mapped case IDs, platforms and full acceptance.
- Which PP/PILOT/UAH/AR requirements still need implementation, hardware, secure OS restore, provider capability, finance/legal review or owner observation, and the concrete prerequisite for each remaining group.
- Any skips, failures, blocked cases and retests; original paid obligations and uncertain output must remain preserved.
- Final remote SHA and whether it was verified; any unsaved/local-only work and the exact next step.
- Whether the owner may begin the supervised synthetic device worksheet after preflight. Do not declare actual refund capability, full merchant readiness, AR-13 approval or production readiness without their independent required evidence and authorization.

Begin now with source/remote verification and the required document review. Then execute the first genuinely unfinished software increment, starting with the connected proof-offer/remedy gaps unless newer verified repository evidence has already closed them. Continue through the remaining executable campaign; do not stop after merely restating this prompt.
