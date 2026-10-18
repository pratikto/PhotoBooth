# Meong Photobooth Development Protocol v1.0
Effective: 2026-10-18 | Branch: `feature/kivy-gui`

## Non-negotiable rules
1. New ideas are **documentation-only** until the owner explicitly approves a named implementation scope. Approval to document is not approval to code.
2. Review each incoming idea against the **latest branch source** for business priority, user/operational impact, compatibility, technical readiness, complexity, dependencies, and regression risk. If code has not been inspected, mark readiness **Unverified**, not Ready.
3. Re-rank the entire backlog after every new idea or material bug discovery. Stable IDs (`FEAT-001`, `BUG-001`) never change; execution order may change.
4. Prioritize critical defects and operational stability. Do not allow attractive enhancements to mask unresolved defects.
5. Use existing `feature/kivy-gui` branch unless owner expressly changes the policy; no automatic new branches or merges.
6. Small, scoped, reviewable changes; explanatory English code comments; never assert tests passed without evidence.
7. No implementation, code commit, push, merge, or release without explicit approval of the relevant action/scope. Documentation-only approval authorizes documentation commits on the agreed branch.

## Idea review fields
ID; title; problem/user value; proposed behavior; business priority (P0 critical, P1 high, P2 medium, P3 low); impact (high/medium/low); current-version compatibility; readiness (Ready/Partial/Blocked/Unverified); complexity (S/M/L/XL); confidence; dependencies; affected modules/hardware; risks; acceptance criteria; proposed execution rank; justification; status; date/reviewer.
Priority and execution rank are distinct: prerequisites may be implemented before a higher-business-priority feature.

## Lifecycle
IDEA -> REVIEW -> BACKLOG -> APPROVED -> IN PROGRESS -> IMPLEMENTED -> VERIFIED -> RELEASED. BLOCKED can interrupt any unfinished stage. Implemented means written, Verified means evidence-backed tests passed, Released means approved for operational use. DONE is reserved for released/accepted work.

## Quality gates
- **Before work:** establish current commit SHA, inspect relevant code, known defects and dependencies, define acceptance criteria, tests and rollback target.
- **During work:** preserve unrelated functionality, use focused commits and traceable IDs.
- **Before verification:** run targeted tests and full applicable regression suite; record actual outputs, environment, limitations and failures.
- **Hardware acceptance:** owner validates actual camera, speakers, printer, screen and payment behavior where applicable; simulated success does not imply physical success.
- **Before release:** resolve blocking defects, get explicit approval, record baseline SHA, release notes and rollback procedure.

## Bug severity
S0 Blocker: unsafe operation, payment integrity risk, data loss, or core kiosk unusable.
S1 Critical: main customer journey fails (e.g., cannot complete capture/print).
S2 Major: substantial degradation or workaround required.
S3 Minor: cosmetic/non-blocking inconvenience.
Severity reflects observed impact; reproducibility, environment, owner and evidence must be recorded.

## Risk-based testing
Low: targeted visual/navigation; Medium: affected module + integration; High: end-to-end + regression + physical checks; Critical: full transaction/data integrity, failure recovery, rollback and explicit release approval.

## Roadmap and freeze
M1 Core Stability -> M2 Operational Reliability -> M3 Commercial Readiness -> M4 Product Enhancement -> M5 Scale & Maintenance.
These are provisional milestones, not certified product status. Freeze feature scope during a milestone's release-candidate testing; only approved blocker fixes enter the frozen candidate.

## Source of truth (paths relative to repository root)
- [docs/DECISIONS.md](DECISIONS.md): binding **owner-confirmed product direction**, not evidence of implementation; open commercial terms must be labelled.
- [docs/FEATURE_STATUS.md](FEATURE_STATUS.md): observed **current source** versus **owner-reported device behavior**; do not collapse those categories.
- [docs/bug_tracker.md](bug_tracker.md): one authoritative defect register with stable IDs (including distinct BUG-001 audio output and BUG-007 unresponsive Settings test taps).
- [docs/test_checklist.md](test_checklist.md): evidence ledger (reported physical pass/fail, historical automated tests, unverified) and release acceptance.
- [docs/next_step.md](next_step.md): one **unified provisional** future-feature board, including deferred/parked ideas, not an approved plan.
- [docs/DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md): current session technical context, followed by dated historical notes; not a second backlog.
- [docs/ARCHITECTURE.md](ARCHITECTURE.md): source architecture; [docs/advertising-and-qris.md](advertising-and-qris.md): operational ad/demo QR instructions; [docs/CHANGELOG.md](CHANGELOG.md): actual commits and changes.
- [docs/README.md](README.md) is the documentation index; the root [README.md](../README.md) includes historical setup and milestones.

**Reconciliation rule:** when legacy README/QA/handover wording conflicts with a later owner report or the current source, retain historical evidence with its date, flag discrepancies, and update canonical documents. Neither historical passed tests nor a source-level feature should be treated as a physical acceptance. No documentation update permits application code changes; the owner must approve the exact implementation scope separately.
