# Meong Photobooth — Reusable Development & Documentation Prompt

> **CURRENT RELEASE BASELINE (2026-10-19):** Default branch `master` contains Meong Photobooth Kivy GUI. Immutable source snapshot `v1.0.0` / `07ce51d2022ab5673a7a27e744e5e5757fbb3d08` is published as a [GitHub pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0). Release-SHA CI: [Kiosk GUI 39185986245](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245) (**233 pass, 2 skipped, 87 synthetic renders, 0 errors**) and [Dither 39185986273](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273) (**48 tests pass**). Linux mock/screenshot QA is **not** certification on Windows hardware or customer deployment. Outstanding: BUG-001/007 audio speaker retest, BUG-009 30-day Drive cloud retention **OPEN**; QRIS is DEMO/non-payable (FEAT-020 not implemented), receipt scanner FEAT-002 not implemented. The earlier `feature/kivy-gui` branch and dated narratives below are **historical** where they conflict with this baseline.

Last reviewed: 2026-10-19 | Repository: `pratikto/PhotoBooth` | Stable branch: `master` | Immutable release: `v1.0.0`

**Purpose:** Copy the prompt below into a new chat or use it when continuing a task. GitHub documentation is the durable project record; chat history by itself is **not** the status ledger.

**Authority:** [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) is the binding governance document. [DECISIONS.md](DECISIONS.md) records owner-approved product direction. This file is a **workflow prompt**, not a second protocol or permission to implement unapproved work.

## Copy/paste prompt — planning, implementation and documentation

> **MEONG PHOTOBOOTH — Continue Development with GitHub Traceability**
>
> Repository: `pratikto/PhotoBooth`. Use **`master`** only as the stable baseline; for specifically approved work use a scoped **`feature/*`, `fix/*`, or `docs/*`** branch and propose a PR. Never update the immutable `v1.0.0` tag, merge, change application code or deploy beyond my explicit task authorization.
>
> **My requested task:** [DESCRIBE THE BUG, FEATURE OR REVIEW]
>
> **Work ID:** [BUG-XXX / FEAT-XXX / DOC-XXX if applicable; propose an ID if new]
>
> **Authorization:** [REVIEW ONLY / DOCS ONLY / APPROVED CODE SCOPE: ...]. If not clearly authorized, **inspect and propose only**; ask me before making application-code changes or committing/pushing code outside the approved scope.
>
> **Acceptance criteria / constraints / relevant hardware:** [EXPECTED RESULT, WINDOWS PRINTER / CAMERA / AUDIO / PAYMENT CONDITIONS, KNOWN LIMITATIONS].
>
> 1. **Read current GitHub state first.** Fetch the latest branch ref/commit SHA, then read `docs/README.md`, `docs/DEVELOPMENT_PROTOCOL.md`, `docs/DECISIONS.md`, `docs/FEATURE_STATUS.md`, `docs/bug_tracker.md`, `docs/next_step.md`, `docs/test_checklist.md` and `docs/DEVELOPMENT_HANDOVER.md`. Inspect affected source files, their dependencies and any relevant old change/QA history. Do not substitute older chat recollections for current GitHub state.
> 2. **Review the proposed task.** Check whether it duplicates an existing BUG/FEAT, assign/use a stable ID, distinguish reported symptoms from proven causes, and evaluate business/user impact, severity/priority, compatibility, readiness, complexity, dependencies, risks and rollback. Give me a concise proposed implementation plan, acceptance criteria and tests. **Prioritize open operational bugs before new features.**
> 3. **Respect authorization.** Approval to review or document is NOT approval to code. Perform only the specifically approved scope. When approval allows code work, make small, reviewable changes using detailed, helpful **English code comments**; preserve unrelated behavior. Do not touch the separate thermal-printer branch or local uncommitted changes.
> 4. **Test truthfully.** Run targeted tests and applicable regression tests only when available; capture exact commands, OS/runtime, commit SHA and PASS/FAIL/SKIP results. Record test limitations. Hardware claims (thermal photo/QR print, video, speakers, camera, payment) require actual on-device/operator evidence. A mock or successful spooler send is **not** proof of physical success; demo QRIS is **not** live payment.
> 5. **Update the GitHub documentation relevant to the work:**
>    - `docs/bug_tracker.md` — new symptoms, status, root cause **only when proven**, fix/validation evidence, next reproduction and IDs.
>    - `docs/FEATURE_STATUS.md` — what is actually in source, what was reported on-device, and what remains unverified.
>    - `docs/next_step.md` — proposed ideas/features, ranking, dependencies and approval status; keep the **one unified active queue** and parking lot; do not present ideas as implemented.
>    - `docs/DECISIONS.md` — only confirmed owner decisions; label unresolved terms as TBD, without inventing approvals.
>    - `docs/test_checklist.md` — commands, machine/environment, commit, actual outputs, skips, physical evidence and outstanding tests.
>    - `docs/DEVELOPMENT_HANDOVER.md` — current status, blockers, relevant commits, next safe action; distinguish old dated notes.
>    - `docs/ARCHITECTURE.md` / specific technical guides — only when modules, interfaces, routing or setup instructions actually change.
>    - `docs/CHANGELOG.md` — actual changes, with commit references or explicit uncommitted status, never aspirational fixes.
>    Update **only relevant files** and keep one canonical source of truth per topic. Each significant approved code behavior change must have a corresponding relevant documentation update, in the same commit or a clearly associated documentation commit.
> 6. **Commit and verify only when authorized.** Verify changes on the approved task branch. Keep code and documentation commits scoped and traceable with BUG/FEAT IDs when applicable; record before/after commit SHA and link. Do not claim a push, check or physical test succeeded unless verified from GitHub/test evidence. Do not merge, publish, release or mark CLOSED without the required owner approval and evidence.
> 7. **Final report to me:** Summarize **(a)** work ID/scope/approval, **(b)** changed files and reason, **(c)** tests and unverified hardware items, **(d)** updated documents, **(e)** commit links/before-after SHA, **(f)** remaining bugs, risks, next action and any pending approval. If no change was authorized, report findings and proposed doc edits without implementing.
>
> **Important:** Never silently overwrite decisions, remove historical evidence, infer live QRIS capability, or mark a user-reported device bug fixed because unit tests passed.

## Quick resume prompt

> Continue Meong Photobooth in `pratikto/PhotoBooth`, stable `master` at (or following) tagged source version `v1.0.0`; create a scoped working branch only for approved changes. Follow [docs/DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md) and [docs/DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md), inspect the newest GitHub commit and the canonical documentation before proposing actions. Tell me the top open bugs and today's safe next task. **Review only until I approve a specific code/documentation scope.**

## How updates should be recorded

| Change category | Primary record | When to update |
| --- | --- | --- |
| User-reported defect or root-cause investigation | [bug_tracker.md](bug_tracker.md) | When reported and after each evidence-backed investigation |
| Approved product requirement / unresolved commercial term | [DECISIONS.md](DECISIONS.md) | When owner confirms or changes a decision |
| Proposed feature, dependency or execution priority | [next_step.md](next_step.md) | During approved documentation intake and reprioritization |
| Source implementation behavior or module integration | [FEATURE_STATUS.md](FEATURE_STATUS.md), [ARCHITECTURE.md](ARCHITECTURE.md) if architecture changes | Alongside approved implementation |
| Test results, hardware evidence, regressions | [test_checklist.md](test_checklist.md) | After actual test runs/owner validation |
| Progress, blockers and next continuation | [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) | At the end of an authorized development stage |
| Actual code/docs changes | [CHANGELOG.md](CHANGELOG.md) | With corresponding verified GitHub commit |

**No background GitHub write is implied:** updates happen when an authorized development/documentation task is actually performed. Never imply that a file was updated if it was not successfully committed to GitHub.
