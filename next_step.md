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
| 1 (provisional; after blocking defects) | FEAT-001 | Template fee + per-print pricing | P1 High | High | Partial | Partial | M | REVIEW / NOT APPROVED |

**Existing product work is documented in [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md) and [docs/FEATURE_STATUS.md](docs/FEATURE_STATUS.md).** Do not automatically relabel old defects as new feature requests. No execution rank is finalized until the latest branch and blocker list are reviewed.

## FEAT-001 — Template fee + per-print pricing
- **Status:** REVIEW / NOT APPROVED FOR IMPLEMENTATION. Submitted: 2026-10-18.
- **Requested behavior:** One selected template incurs IDR 5,000 base fee, plus IDR 5,000 for **each physical print copy**. For one selected template: 1 copy = IDR 10,000; 2 = IDR 15,000; 3 = IDR 20,000. General formula per template = 5,000 + (5,000 × print copies). Multiple selected templates: sum each selected template's base fee and copy charges.
- **Business priority:** P1 High; **impact:** High (checkout price, customer expectations, printer usage, transaction consistency).
- **Source compatibility / evidence (inspected 2026-10-18):** Partial. `photobooth/catalog.py` currently defines `PRICE_PER_SESSION = 5000`; `photobooth/app.py` calculates `total_amount=len(plans)*unit_price`; `photobooth/workflow.py` expands template quantity into photo sessions; `photobooth/ui_kivy.py` labels price as `Rp5.000 / sesi` and uses template quantity controls. **Session quantity currently means repeated capture sessions, not print copies.** Do not merely change a price constant.
- **Readiness:** Partial (current code reviewed; requirements and hardware integration need clarification). **Complexity:** M, possibly L if per-template copies require schema migration. **Confidence:** Medium.
- **Dependencies:** Reconcile BUG-003 (payment QR slip printing), BUG-004 (photo print quality), and physical printer integration before operational acceptance. Demo QRIS remains non-payable; do not claim payment verification.
- **Affected components:** catalog/pricing, cart GUI, workflow/session count, payment summary, transaction persistence, photo print jobs, manual reprints, tests, documentation.
- **Risks:** Charging base fee per copy by mistake; interpreting 2 copies as 2 capture sessions; duplicate prints; mismatch between payment display and print count; existing transaction records compatibility.
- **Open product decision:** Confirm whether a template selection corresponds to one 3-photo capture session regardless of print copies, and whether each distinct selected template incurs its own IDR 5,000 fee. Also define zero-print/digital-only orders and maximum print copies if supported.
- **Acceptance criteria (proposed):** 1/2/3 copies correctly total 10k/15k/20k for one template; one capture session produces selected number of identical physical copies; mixed-template orders sum correctly; checkout, persistence, receipts and actual prints agree; regression tests pass; no unapproved code change.
- **Execution rank:** Provisional #1 among new features, **only after blocking existing defects and specification confirmation**. Ranking must be recalculated with every new idea.

## Milestone framework (provisional)
M1 Core Stability; M2 Operational Reliability; M3 Commercial Readiness; M4 Product Enhancement; M5 Scale & Maintenance. See protocol for freeze and release rules.

## Reprioritization history
| Date | Trigger | Change and rationale |
|---|---|---|
| 2026-10-18 | Backlog framework created | No new ideas ranked; baseline/source audit needed before scheduling |\n| 2026-10-18 | FEAT-001 submitted | Provisional feature rank #1 (sole new idea); P1/high impact, partial compatibility; existing defects remain ahead of feature implementation |

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
