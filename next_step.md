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
| 2 (after FEAT-001 and POS validation design) | FEAT-002 | Merchant receipt QR/barcode promotion | P1 High | High | Partial | Blocked pending merchant integration | L/XL | REVIEW / NOT APPROVED |

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
- **Confirmed by owner (2026-10-18):** One selected template = **one photo session with 3 captures**, regardless of the number of printed copies. Printing 3 copies means three identical prints of that one session's composed layout, **not** three capture sessions.
- **Remaining product decisions:** Confirm whether each distinct selected template incurs its own IDR 5,000 fee; define zero-print/digital-only orders and maximum copies if supported.
- **Acceptance criteria (proposed):** 1/2/3 copies correctly total 10k/15k/20k for one template; one capture session produces selected number of identical physical copies; mixed-template orders sum correctly; checkout, persistence, receipts and actual prints agree; regression tests pass; no unapproved code change.
- **Execution rank:** Provisional #1 among new features, **only after blocking existing defects and specification confirmation**. Ranking must be recalculated with every new idea.

## FEAT-002 — Merchant receipt QR/barcode promotion
- **Status:** REVIEW / NOT APPROVED FOR IMPLEMENTATION. Submitted: 2026-10-18.
- **User story:** On the photobooth payment page, a customer scans a participating café/restaurant's food/beverage purchase receipt barcode or QR code. Example promotion: purchase of at least IDR 50,000 grants one free template fee. Apply the eligible discount to the photobooth amount payable.
- **Pricing proposal (subject to merchant terms):** FEAT-001 base IDR 5,000/template + IDR 5,000/physical print. A valid receipt waives **one template base fee (IDR 5,000)**, not printing. One template with 1/2/3 copies would cost IDR 5,000/10,000/15,000 after this example promotion. Discount cannot exceed eligible template charges or create a negative total.
- **Business priority:** P1 High; **impact:** High (merchant partnership, conversion, checkout accuracy).
- **Source compatibility / evidence (inspected 2026-10-18):** Partial. `photobooth/app.py` has `_open_dummy_payment` and computes `total_amount=len(plans)*unit_price` with no receipt-discount calculation; `photobooth/ui_kivy.py` contains payment UI flow. QR helpers in `photobooth/qr_code.py` serve existing QR workflows, not proof of receipt authenticity. **Current payment is non-payable demo**, not an integrated QRIS gateway.
- **Readiness:** Blocked pending merchant receipt format/POS validation approach and FEAT-001 pricing design. **Complexity:** L/XL; **confidence:** Medium (unknown POS API, receipt payload and scanning hardware).
- **Dependencies:** FEAT-001 pricing model, merchant agreement and eligibility rules, receipt/POS API or signed one-time vouchers, camera/scanner UX, persistent claim ledger, payment recalculation, live gateway only when separately approved. BUG-003 printing is a separate QR-slip issue; do not conflate payment QR scanning with receipt scanning.
- **Risks and controls:** Ordinary barcode/QR may encode only receipt ID and cannot independently prove value; validate purchase amount, store, date and authenticity against merchant POS or cryptographically signed token. Enforce atomic one-time redemption (including multiple kiosks), replay prevention, expiry, offline policy, data minimization and clear error/fallback UI. Do not treat a scan as payment confirmation. Recompute payment amount **before** generating any payable QRIS; invalidate stale payment requests if discount changes.
- **Affected areas:** checkout UI, scanning input (camera or external reader), promotion rules, pricing calculation, transaction store/redemption state, merchant API, test harness, receipt/discount display and audit logs.
- **Proposed acceptance:** Valid eligible receipt >= IDR 50,000 discounts exactly one template fee by IDR 5,000; print fees remain unchanged; ineligible, duplicate, expired, invalid or unverifiable receipts receive no discount; mixed-template carts cap discounts correctly; checkout totals and payment requests stay consistent; no duplicate redemption across concurrent kiosks; scan failures preserve the normal payment path.
- **Open decisions:** Merchant POS vendor and receipt barcode format; one receipt per customer/transaction and cross-booth reuse; eligibility window and eligible products; one discount per receipt vs per template; whether discounts combine with other promotions; scanner type and offline behavior. Example threshold and benefit are illustrative merchant-configurable campaign settings, not global fixed rules.
- **Execution rank:** Provisional #2 after FEAT-001 because it requires a reliable base pricing model, then POS/anti-fraud design and payment integration. Existing operational blockers remain ahead of feature releases.

## Milestone framework (provisional)
M1 Core Stability; M2 Operational Reliability; M3 Commercial Readiness; M4 Product Enhancement; M5 Scale & Maintenance. See protocol for freeze and release rules.

## Reprioritization history
| Date | Trigger | Change and rationale |
|---|---|---|
| 2026-10-18 | Backlog framework created | No new ideas ranked; baseline/source audit needed before scheduling |
| 2026-10-18 | FEAT-001 submitted | Provisional feature rank #1 (sole new idea); P1/high impact, partial compatibility; existing defects remain ahead of feature implementation |
| 2026-10-18 | FEAT-001 behavior confirmed | One 3-capture session per selected template; print-copy count only duplicates the same finished layout, not the photo session |

| 2026-10-18 | FEAT-002 submitted | Re-ranked full backlog: FEAT-001 stays #1 as prerequisite; FEAT-002 enters #2 pending merchant validation and pricing integration. Existing bugs still take precedence. |

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
