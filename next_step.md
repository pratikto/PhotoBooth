# Meong Photobooth — Dynamic Feature Backlog
Protocol: [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) | Updated: 2026-10-18
Branch: `feature/kivy-gui`

**Planning only. No idea below authorizes implementation.** Every incoming idea triggers a fresh current-code compatibility/readiness review and a full execution-order re-ranking. Stable feature IDs are not execution sequence numbers.

## Intake and evaluation
For each new idea record:
- Stable ID, submitted date, problem statement, expected customer/business value and proposed behavior
- Business priority P0/P1/P2/P3; impact H/M/L; compatibility and current source/commit evidence
- Readiness Ready/Partial/Blocked/Unverified; complexity S/M/L/XL; confidence
- Dependencies (including BUG IDs), affected components, risk, acceptance criteria
- Proposed **execution order**, reason for placement, status and approval reference

## Candidate execution queue
| Execution order | ID | Feature | Business priority | Impact | Compatibility | Readiness | Complexity | Status |
|---|---|---|---|---|---|---|---|---|
| — | — | No newly submitted feature ideas yet | — | — | — | — | — | IDEA intake open |

**Existing product work is documented in [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md) and [docs/FEATURE_STATUS.md](docs/FEATURE_STATUS.md).** Do not automatically relabel old defects as new feature requests. No execution rank is finalized until the latest branch and blocker list are reviewed.

## Milestone framework (provisional)
M1 Core Stability; M2 Operational Reliability; M3 Commercial Readiness; M4 Product Enhancement; M5 Scale & Maintenance. See protocol for freeze and release rules.

## Reprioritization history
| Date | Trigger | Change and rationale |
|---|---|---|
| 2026-10-18 | Backlog framework created | No new ideas ranked; baseline/source audit needed before scheduling |

## Template
### FEAT-XXX — Title
- Status: IDEA; submitted: YYYY-MM-DD; approval: none
- User value / proposed behavior:
- Business priority / impact:
- Compatibility / code SHA evidence:
- Readiness / complexity / confidence:
- Dependencies / affected modules / risks:
- Acceptance criteria / tests:
- Execution order and rationale:
