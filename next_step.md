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
| 2 (shared camera UX dependency) | FEAT-003 | Global mirrored live camera previews | P1 High | High | Partial | Partial | M | REVIEW / NOT APPROVED |
| 3 (after FEAT-001 and FEAT-003) | FEAT-002A | Dummy receipt scanner + simulated promotion | P1 High | High | Partial | Partial | M | REVIEW / NOT APPROVED |
| 4 (after core stability) | FEAT-004 | Per-machine local-first Drive ad sync | P2 Medium | High | Partial | Partial | M/L | REVIEW / NOT APPROVED |
| 5 (demo after stability) | FEAT-005A | Local dummy ordering demo + kiosk launcher | P2 Medium | High | Partial | Partial | M | REVIEW / NOT APPROVED |
| Deferred unless required by partner | FEAT-005B | Optional deeper ordering/POS integration | P3 Deferred | Medium | Unverified | Blocked: partner need | L/XL | DEFERRED / NOT APPROVED |
| Deferred until merchant partnership | FEAT-002B | Real merchant POS integration | P2 Deferred | High | Unverified | Blocked: no partner | L/XL | DEFERRED / NOT APPROVED |

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

## FEAT-002 — Merchant receipt QR/barcode promotion (two-phase delivery)
- **Status:** REVIEW / NOT APPROVED FOR IMPLEMENTATION. Submitted: 2026-10-18.
- **User story:** On the photobooth payment page, a customer scans a participating café/restaurant's food/beverage purchase receipt barcode or QR code. Example promotion: purchase of at least IDR 50,000 grants one free template fee. Apply the eligible discount to the photobooth amount payable.
- **Pricing proposal (subject to merchant terms):** FEAT-001 base IDR 5,000/template + IDR 5,000/physical print. A valid receipt waives **one template base fee (IDR 5,000)**, not printing. One template with 1/2/3 copies would cost IDR 5,000/10,000/15,000 after this example promotion. Discount cannot exceed eligible template charges or create a negative total.
- **Business priority:** P1 High; **impact:** High (merchant partnership, conversion, checkout accuracy).
- **Source compatibility / evidence (inspected 2026-10-18):** Partial. `photobooth/app.py` has `_open_dummy_payment` and computes `total_amount=len(plans)*unit_price` with no receipt-discount calculation; `photobooth/ui_kivy.py` contains payment UI flow. QR helpers in `photobooth/qr_code.py` serve existing QR workflows, not proof of receipt authenticity. **Current payment is non-payable demo**, not an integrated QRIS gateway.
- **Owner decision (2026-10-18):** **Real POS integration is deferred until a merchant partner exists.** For machine demonstrations, build only a dummy receipt scan and simulated discount path. This is scope confirmation, **not approval to modify application code**.
- **Confirmed scanner UX (2026-10-18):** On payment page, tapping receipt scan **stops/hides payment advertising video** and replaces the advertisement region with a **live camera preview** (no separate screen). Keep payment QRIS and order summary visible. Show framing guides, active detection indicator, explicit distinction between code detected and receipt validated, success confirmation and applied discount, or failure reason with scan-again action. **Owner-approved UX (2026-10-18):** after successful receipt validation, automatically close scanner, update payable total and resume payment advertisement; after failed scan/validation, keep camera preview active and offer retry without forcing the customer to reposition. When scanning exits, release scanner resources and restore payment advertising as appropriate. Apply this same interaction pattern to demo and future real merchant receipts. Camera ownership must not interfere with photo capture or ad playback; handle unavailable camera, timeout, duplicate detections and scan retry.
- **Phase A / FEAT-002A — demo:** Use printed or on-screen dummy receipt QR/barcode encoding a demo transaction ID; look up the ID in a local deterministic fixture (e.g., DEMO-001 IDR 65,000 eligible, DEMO-002 IDR 35,000 ineligible, DEMO-003 already redeemed). Apply IDR 5,000 template-fee discount only to eligible demo orders, with a clearly visible DEMO label; no live merchant API, no real receipt validation, no real payment verification. Specify test reset behavior and prevent accidental presentation as live integration.
- **Phase B / FEAT-002B — deferred:** Only after merchant partnership, obtain sample real receipts, POS vendor/API access, merchant authorization and security/privacy requirements. Implement adapter, server-side verification and durable cross-kiosk redemption then.
- **Readiness:** Phase A Partial (needs UI/scanner behavior and fixtures); Phase B Blocked (no partner). **Complexity:** Phase A M; Phase B L/XL. **Confidence:** Medium.
- **Dependencies:** FEAT-001 pricing model, merchant agreement and eligibility rules, receipt/POS API or signed one-time vouchers, camera/scanner UX, persistent claim ledger, payment recalculation, live gateway only when separately approved. BUG-003 printing is a separate QR-slip issue; do not conflate payment QR scanning with receipt scanning.
- **Risks and controls:** Ordinary barcode/QR may encode only receipt ID and cannot independently prove value; validate purchase amount, store, date and authenticity against merchant POS or cryptographically signed token. Enforce atomic one-time redemption (including multiple kiosks), replay prevention, expiry, offline policy, data minimization and clear error/fallback UI. Do not treat a scan as payment confirmation. Recompute payment amount **before** generating any payable QRIS; invalidate stale payment requests if discount changes.
- **Affected areas:** checkout UI, scanning input (camera or external reader), promotion rules, pricing calculation, transaction store/redemption state, merchant API, test harness, receipt/discount display and audit logs.
- **Proposed acceptance:** Valid eligible receipt >= IDR 50,000 discounts exactly one template fee by IDR 5,000; print fees remain unchanged; ineligible, duplicate, expired, invalid or unverifiable receipts receive no discount; mixed-template carts cap discounts correctly; checkout totals and payment requests stay consistent; no duplicate redemption across concurrent kiosks; scan failures preserve the normal payment path.
- **Confirmed by owner (2026-10-18):** Use the merchant's **existing POS-issued purchase receipt** and its existing barcode/QR first; do **not** require the café to issue a separate Meong voucher as the initial approach. Scan alone is not evidence of eligibility; inspect actual receipt encoding and determine whether merchant POS lookup is available before selecting validation architecture.
- **Open decisions:** Merchant POS vendor and receipt barcode format/sample; one receipt per customer/transaction and cross-booth reuse; eligibility window and eligible products; one discount per receipt vs per template; whether discounts combine with other promotions; scanner type and offline behavior. Example threshold and benefit are illustrative merchant-configurable campaign settings, not global fixed rules.
- **Execution rank:** FEAT-002A provisional #2 after FEAT-001; FEAT-002B deferred until merchant partner. Existing operational blockers remain ahead of feature releases.

## FEAT-003 — Global mirrored live camera previews
- **Status:** REVIEW / NOT APPROVED FOR IMPLEMENTATION. Submitted: 2026-10-18.
- **Problem:** Live photo preview behaves non-mirrored; user moves hand right but perceives movement left, making posing confusing.
- **Owner-confirmed scope (2026-10-18):** **Every live camera preview throughout the app** must appear horizontally mirrored by default, including photo capture, receipt scanning (dummy and future merchant), and all future camera-based features. Mirror is a **display-only transform**: preserve original unmirrored capture files, composed template output, QR graphics, logos, text and printed photos; decode QR/barcodes using original frames. Detection overlays/bounding boxes must be mapped into mirrored display coordinates so the visual indicator stays aligned.
- **Priority / impact:** P1 High / High customer experience. **Compatibility:** Partial pending exact camera-to-texture pipeline review. **Readiness:** Partial. **Complexity:** S/M. **Confidence:** Medium.
- **Affected components:** Shared Kivy live-camera preview renderer, image texture transformation, capture vs saved-image pipeline, receipt-scanner detection overlays, camera orientation across hardware and future camera consumers.
- **Dependencies / risks:** Validate camera device orientation and any existing flips to avoid double-mirroring; no changes to saved photos or printer outputs; performance and scanner camera ownership.
- **Acceptance criteria:** Left/right movement matches mirror intuition in **every live camera preview**; saved photos and printed layout preserve normal orientation and readable text; scanner detects unmirrored original data while QR/barcode bounding box overlays align with mirrored preview; countdown and other overlays align; test with actual camera on photo and scanner pages.
- **Execution rank:** Provisional #3 among feature ideas; may move ahead of FEAT-002A after stability blockers are resolved because the shared preview renderer is a dependency for scanning UX. Re-rank again at next intake.

## FEAT-004 — Per-machine local-first Google Drive advertising sync
- **Status:** REVIEW / NOT APPROVED FOR IMPLEMENTATION. Submitted: 2026-10-18.
- **Owner decisions:** Advertisements always play from local storage; dedicated Meong Photobooth Google account/Drive is the centralized content source; venue/customer supplies Wi-Fi; updates typically weekly; each machine (e.g. BB01, BB02, BB03) receives only its own ads. Existing slot filename syntax must be inspected before finalizing parser, not guessed.
- **Proposed behavior:** Background compare and download changed assets only, verify files before atomic activation, preserve last-known-good playlist when offline, show last sync and manual sync in admin; do not interrupt currently playing ads. Support per-device folder/slot mapping, disk quotas and safe deletion policy.
- **Priority / impact:** P2 Medium / High operational scalability. **Compatibility:** Partial (existing Drive integration and ad player require detailed code audit). **Readiness:** Partial; **complexity:** M/L; **confidence:** Medium.
- **Dependencies / risks:** Device identity, existing Drive filename convention, credentials and least-privilege access, storage limits, content corruption, Wi-Fi interruptions, player concurrency, file ownership and playlist updates.
- **Acceptance:** Machine BB01 never downloads BB02 ads; new/updated/deleted content reconciles safely; local playback continues offline; partial downloads never play; weekly refresh and manual sync observable.
- **Execution rank:** Provisional #4, after core stability and higher-priority pricing/camera/demo receipt flows.

## FEAT-005 — Partner-provided self-ordering inside Meong kiosk
- **Status:** DEFERRED / NOT APPROVED FOR IMPLEMENTATION. Submitted: 2026-10-18; strategy confirmed by owner later on 2026-10-18.
- **Owner decision:** For real merchants, **do not develop or maintain a production Meong ordering GUI, menu catalog, cart, checkout, or POS adapters by default**. Merchant owns the live ordering service, menu changes, stock, pricing, payment and POS connection. Meong supplies only a safe entry point / launcher and, where supported, a kiosk-style embedded browser or controlled handoff back to photobooth. **Exception: owner explicitly requests a small, standalone dummy ordering system for sales demonstrations**, without a real POS or live payment.
- **Partner-dependent eligibility:** Only offer self-ordering when the merchant already has a compatible customer-facing web ordering solution or a separately evaluated compatible app; confirm kiosk usability, permissions, supported operating system and payment workflow with each partner. A POS cashier/admin interface must never be exposed to public kiosk users. If incompatible, disable/hide the ordering feature rather than building a full POS.
- **FEAT-005A lightweight demo scope:** Create a **local mini web-ordering demo** on the mini PC with sample menu items, item selection/quantities, simple cart, simulated payment, and demo order confirmation. Launch from a Meong 'Pesan Makanan & Minuman' button in a controlled kiosk view with clear return, inactivity reset and isolation from photobooth sessions. Mark all payment and order screens DEMO; no real orders, payment gateway, POS integration or merchant data. Keep demo isolated and disposable: when a real partner supplies compatible ordering, the same launcher points to partner's own customer ordering service instead of building/maintaining a Meong production POS.
- **Demo cross-promotion requirement (owner confirmed 2026-10-18):** Ordering runs on the same Meong kiosk, so **no receipt scan** is required for the dummy ordering-to-photo promo. After a dummy food order is simulated as successfully paid, generate a single-use, session-bound demo promotion entitlement. Example: qualifying food spend >= Rp50,000 waives one Rp5,000 photo template/session base fee, while Rp5,000 per physical print copy remains payable. Automatically present a photo offer and apply the promo at photo checkout. Ensure promo is not granted for unpaid/cancelled orders, is not duplicated or reused, and expires/resets appropriately on abandoned kiosk sessions. Mark all transactions and discount validations DEMO. This is an **additional path** alongside FEAT-002A's independent external-receipt scanning demo; do not remove FEAT-002A. Confirm final promo threshold and offer wording before implementation.
- **Promo funding model (owner decision 2026-10-18):** The **merchant partner funds the photo-session fee waiver**, because the Meong ordering promotion is designed to lift merchant basket value to the merchant's chosen spending threshold. Example: threshold Rp50,000; qualifying paid food order earns Rp5,000 photo session fee waiver, printing remains customer-paid; merchant owes Meong Rp5,000 per valid redeemed reward (not per merely eligible food order). Keep customer-facing discount and partner reimbursement as separate ledger records. Dummy demo should show a simple partner settlement/reporting view (eligible food orders, redeemed rewards, total subsidy due), all clearly simulated. Production requires contractually agreed threshold, eligible basket basis, redemption criteria, refund/cancellation policy, evidence/audit trail, reconciliation cadence and payment terms; no assumption of automatic real POS integration.
- **FEAT-005B optional:** Deeper POS/API integration only if a real partner's requirements justify it and the owner explicitly approves a separate scope.
- **Business priority / impact:** P2 Medium / High potential partner value. **Compatibility:** Unverified pending partner and operating system. **Readiness:** Blocked until partner capability known. **Complexity:** S/M for supported web kiosk, higher for non-web apps. **Confidence:** Medium.
- **Risks:** Embedded-browser incompatibility, login/session leakage, escape from kiosk, payment handoff, network outages, merchant site UI changes, customer data exposure, OS limitations, and unsupported vendor terms.
- **Acceptance:** Demo can browse sample items, adjust quantities, see cart total, simulate checkout and display an explicitly marked demo order confirmation without external connectivity or actual charge; a qualifying paid demo order automatically offers a photo promotion without receipt scanning, applies a one-time Rp5,000 session-fee waiver (not print fees), and an unpaid/nonqualifying order cannot redeem it; kiosk safely returns to Meong and preserves photobooth functionality. Later, partner's own customer ordering works on target mini PC without exposing cashier/admin functions; merchant menu changes appear without updating Meong code; no shared cart/payment assumptions.
- **Execution rank:** Demo #5 provisional after core stability and earlier features; live partner ordering remains deferred until a compatible partner is found. Explicit implementation approval still required.

## FEAT-006 — Configurable Multi-Theme Kivy GUI
- **Status:** REVIEW / NOT APPROVED FOR IMPLEMENTATION. Owner approved concept 2026-10-18; implementation requires separate explicit authorization.
- **Goal:** Offer multiple attractive Meong GUI visual themes, with a per-machine choice stored persistently and controlled from **Admin Settings** (default interpretation; customer theme switching not in initial scope).
- **Candidate visual presets:** Pastel Cute, Midnight Gold, Mint Fresh, Sakura Pop; names/palette are proposals subject to brand and actual Kivy feasibility review.
- **Scope:** Theme tokens for palette, backgrounds, button styling, accents and light animations; apply consistently to landing/ads, tutorial, layout selection, camera, payment, and settings. Keep Meong logo/brand recognisable, text readable, and touch targets accessible.
- **Architecture:** One shared Kivy screen/navigation/transaction codebase; separate centralized theme definitions and machine-level theme config. Switching theme must **not** change screen layout, camera/print/payment behavior, ordering flow or business logic.
- **Compatibility / dependencies:** Audit existing Kivy widgets, KV rules, asset colors, image backgrounds and dynamic styling before implementation; ensure existing logo and ad media remain legible. Theme testing depends on stable current GUI baseline.
- **Risks:** Styling scattered through code, inconsistent screens, low contrast, theme-specific asset maintenance, animation performance, regression in camera/payment/printing, and visual mismatch with ads.
- **Priority / impact / readiness:** P3 Low-Medium / Medium (partner customization); readiness Partial, technical compatibility Unverified, estimated M. **Execution order:** after critical bug fixes and higher-priority functional features, subject to dynamic re-ranking.
- **Acceptance:** Admin can select a preset and it persists across restarts on that machine; every existing page uses the selected visual style; navigation, photo capture, QRIS and printing regression tests pass across all themes; no customer-facing theme switch.
- **Decision note:** User said "Oke setuju" to theme concept after a question on admin-only vs customer choice; admin-only is the conservative proposed default and should be reconfirmed if scope becomes relevant.

## Milestone framework (provisional)
M1 Core Stability; M2 Operational Reliability; M3 Commercial Readiness; M4 Product Enhancement; M5 Scale & Maintenance. See protocol for freeze and release rules.

## Reprioritization history
| Date | Trigger | Change and rationale |
|---|---|---|
| 2026-10-18 | Backlog framework created | No new ideas ranked; baseline/source audit needed before scheduling |
| 2026-10-18 | FEAT-001 submitted | Provisional feature rank #1 (sole new idea); P1/high impact, partial compatibility; existing defects remain ahead of feature implementation |
| 2026-10-18 | FEAT-001 behavior confirmed | One 3-capture session per selected template; print-copy count only duplicates the same finished layout, not the photo session |

| 2026-10-18 | FEAT-002 submitted | Re-ranked full backlog: FEAT-001 stays #1 as prerequisite; FEAT-002 enters #2 pending merchant validation and pricing integration. Existing bugs still take precedence. |

| 2026-10-18 | FEAT-002 receipt source confirmed | Prioritize existing merchant POS receipt QR/barcode, not custom Meong voucher; readiness remains blocked until actual receipt format and verification method are known; ranks unchanged |

| 2026-10-18 | FEAT-002 staged by owner | FEAT-002A dummy receipt scanner/discount for demo ranked #2; FEAT-002B real POS integration deferred until merchant partnership; no implementation authorized |
| 2026-10-18 | FEAT-002 scanner UX clarified | Replace payment advertisement with camera preview during receipt scanning, detection indicator, validated success/failure and retry; retain payment QRIS visibility; no code authorized |

| 2026-10-18 | FEAT-002 scanner success/failure behavior approved | On validated success close scanner/update amount/resume ad; on failure keep preview open for retry. Documentation only; code implementation not authorized |

| 2026-10-18 | FEAT-003 submitted | Added mirror-only photo preview; ranked #3 provisionally after pricing and demo scanner, with potential to advance on low complexity/high UX impact; no code authorized |

| 2026-10-18 | FEAT-003 scope expanded by owner | All current and future live camera previews mirror by default, including receipt scanner; original frames remain unmirrored for processing and output; rank remains provisional #3 |

| 2026-10-18 | FEAT-004 and FEAT-005 intake | Documented local-first per-machine Drive ad sync and phased merchant self-order kiosk; re-ranked camera preview ahead of receipt scanner dependency; live POS integration deferred until partner. No code changes authorized |

| 2026-10-18 | FEAT-005 simplified by owner | Merchant provides and maintains ordering UI/menu/payment; Meong only hosts/launches compatible customer ordering; no native ordering GUI or custom POS by default; partner-dependent, deferred |

| 2026-10-18 | FEAT-005 demo clarified by owner | Build a small local dummy menu/cart/simulated payment/order demo for partner pitches; production ordering still relies on partner's system. Documentation only; no code implementation authorized |

| 2026-10-18 | FEAT-005A automatic promo demo | Add ordering-to-photo promo handoff on same machine without scanning receipt; require simulated paid qualifying food order; retain separate FEAT-002A receipt-scan demo; documentation only |

| 2026-10-18 | FEAT-005 partner-funded promo | Owner confirms merchant funds Rp5,000 waived photo-session fee in return for basket-value uplift; track redeemed rewards and merchant settlement in demo; documentation only |

| 2026-10-18 | FEAT-006 multi-theme GUI | Owner accepts multi-theme concept; provisionally admin-only selection per machine; visual-only themes, shared GUI code; no implementation authorized |

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


## Proposed backlog additions — 2026-10-18 (owner approved DOCUMENTATION only)
**Governance:** These are candidate requirements, not authorization to implement. Existing blocking bugs (audio/button tests, ad playback, QRIS slip print, blurry prints and flow verification) precede new work. Re-rank on new evidence; never assume submitted order equals execution order. Verify Kivy/Windows hardware/API compatibility and dependencies before coding.

| Dynamic rank | ID | Candidate | Business impact | Priority | Readiness | Complexity | Dependencies / principal risk | Status |
|---|---|---|---|---|---|---|---|---|
| After critical bugs, before new growth features | FEAT-007 | Persistent transaction recovery | Very high: prevents paid-but-unfulfilled orders | P0/P1 | Design needed | L | Trusted payment callback, SQLite state machine, print idempotency | REVIEW |
| After critical bugs, before unattended pilot | FEAT-008 | Device health monitoring | Very high: reduce downtime | P1 | Partial | M | Hardware status support, false alerts, privacy | REVIEW |
| With FEAT-008 | FEAT-009 | Automatic startup and crash recovery | Very high: unattended uptime | P1 | Partial | M | OS startup, watchdog loop prevention, safe transaction resume | REVIEW |
| Before pilot / with FEAT-004 | FEAT-010 | Per-machine remote configuration | High: multi-machine management | P1/P2 | Partial | L | Offline-safe config, authentication, validation, rollback | REVIEW |
| With printer quality bugfix | FEAT-011 | Thermal printer quality profiles | High: core product quality | P1 | Partial | M | Printer media width, dithering, scaling, test prints | REVIEW |
| After FEAT-008 | FEAT-012 | Remote diagnostics and structured logs | High: lower support cost | P2 | Partial | M | Sensitive data redaction, connectivity, log retention | REVIEW |
| With FEAT-002 / FEAT-005 demo | FEAT-013 | Partner promo reporting/dashboard | High: prove merchant value | P2 | Partial | M | Redemption ledger, reliable attribution, settlement reconciliation | REVIEW |
| With FEAT-006 | FEAT-014 | Branded photo frame campaigns | High: sponsor packages | P2 | Partial | S/M | Print readability, logo placement, template compatibility | REVIEW |
| After stable capture/storage | FEAT-015 | Digital photo delivery by QR | Medium-high: sharing/brand reach | P2 | Unverified | L | Consent, expiring links, privacy, deletion, secure hosting | REVIEW |
| After FEAT-007 | FEAT-016 | Paid photo reprint by transaction code | Medium: repeat revenue | P2/P3 | Partial | M | Expiration, customer authorization, duplicate-print controls | REVIEW |
| After FEAT-006 + config | FEAT-017 | Event mode / event-specific campaigns | Medium-high: weddings/corporate | P2 | Partial | M | Theme/layout/price/ad bundles, safe rollback | REVIEW |
| After fleet pilot and FEAT-008/010/012 | FEAT-018 | Multi-machine fleet dashboard | High at scale, limited at one machine | P3 now | Unverified | XL | Secure identity, telemetry, outages, maintenance | REVIEW |

### Technical acceptance and implementation boundaries
- **FEAT-007 — Transaction recovery:** Persist unique order ID, pricing and payment state, capture completion, composed file references, print attempts and final fulfillment locally (e.g., SQLite). Proposed lifecycle CREATED → PAYMENT_PENDING → PAID → CAPTURED → PRINTING → COMPLETED, with explicit failure/retry/cancel states. Only trusted payment confirmation may set PAID in production. On restart recover safely without duplicate charges or uncontrolled duplicate prints; test power loss at each stage. Coordinate with FEAT-001 pricing and QRIS production integration.
- **FEAT-008 — Health monitoring:** Check camera availability, printer connection/status (paper status only if device exposes it), disk capacity, network, ad media integrity and application heartbeat. Separate offline-but-operational from blocking faults. Local operator/admin health panel first, remote alerts later.
- **FEAT-009 — Auto recovery:** OS autostart, crash watchdog with backoff, safe kiosk restoration, restart diagnostics, transaction-aware resume, avoid infinite restart loops. Test unexpected power loss.
- **FEAT-010 — Remote config:** Per-machine ID and validated configuration for prices, ads, themes, promo thresholds and partner URLs; signed/authenticated updates, last-known-good local config, audit trail and rollback. Offline operation must continue.
- **FEAT-011 — Printer quality:** Profiles for printer/media size, resampling, contrast and existing Floyd–Steinberg/Bayer/threshold options; use measured comparison print tests and avoid regressions. Core blurry-output bug should be fixed before expanding profile UI.
- **FEAT-012 — Diagnostics:** Structured local logs, failure categories, exportable support bundle, optional remote upload with opt-in and data minimization; never include QRIS secrets, full personal photos or sensitive tokens in ordinary logs.
- **FEAT-013 — Partner reporting:** Separate eligible orders, *redeemed* one-time photo rewards, customer discount and partner-funded subsidy due; include merchant/outlet/machine/time and reconciliation export. Demonstration uses simulated data. Production attribution requires partner system evidence.
- **FEAT-014 — Branded frames:** Merchant logo/campaign overlay on selectable photo templates, preview and thermal-print legibility checks, expiration and per-machine campaign control.
- **FEAT-015 — Digital delivery:** Optional scan-to-download QR for photos with unguessable expiring links, consent, retention/deletion schedule, access limits and offline fallback; avoid public persistent photo URLs.
- **FEAT-016 — Reprint:** Unique transaction reference and bounded retained output, verification before paid reprint, explicit price, rate/quantity limits, clear customer session isolation.
- **FEAT-017 — Event mode:** Named bundles of themes, photo templates, campaign content, pricing and branding; admin-controlled start/end and reliable restore to normal mode.
- **FEAT-018 — Fleet dashboard:** Inventory and per-machine uptime, health, current config version, ad-sync state, print counts and faults; avoid storing customer photo content centrally by default.

### Business proposals and validation (not app implementation)
- **Revenue model candidates:** Photo session + print charges (FEAT-001); monthly/location-based ad slots (FEAT-004); merchant-funded **redeemed** photo promo subsidies (FEAT-002/005); machine rental, venue revenue-share or hybrid contracts. All pricing/rates require pilot evidence, not assumed as commitments.
- **Unit economics per machine:** Track sessions/day, prints/session, operating days, ad income, redeemed promo subsidy and receivables separately from customer discounts. Subtract consumables, transaction fees, rent/revenue share, electricity, connectivity, field service, depreciation and taxes before claiming profit. Pilot illustrative inputs (12 sessions/day, 26 days, 2 prints, Rp300k ads, 60 redemptions) are **examples only**, not forecasts.
- **Partner offer:** Merchant funds photo-session waiver only when genuinely redeemed; target basket threshold set per partner. Test incremental basket lift against a credible baseline, not just total qualifying orders.
- **Pilot success gates:** (1) Customers use and pay for photos, (2) promo generates incremental merchant spend rather than subsidizing unchanged purchases, (3) machine contribution margin after costs is positive and operational uptime/queues are acceptable. Start with one machine and validate before multi-location expansion.
- **Partner contracts:** Clarify ad inventory/creative approval, subsidy settlement cadence, promotion thresholds and exclusions, refund handling, hardware access, internet/power responsibilities, revenue-share, customer data ownership and support SLA.

### Proposed execution sequence (dynamic, subject to feasibility review)
1. **Fix and regress-test current blocking defects**; do not start broad feature development.
2. Stabilize unattended operations: FEAT-007/008/009, plus FEAT-011 alongside printer defect repair; FEAT-012 as needed.
3. Deliver approved demo scope when separately authorized: FEAT-001/003/002A/005A, with FEAT-013 minimal simulated partner reporting and FEAT-006 themes as capacity permits.
4. Add per-machine configuration and ads (FEAT-010/004), partner-branded frames (FEAT-014) and optional event mode (FEAT-017) according to pilot needs.
5. Consider photo delivery/reprint (FEAT-015/016) only after privacy, payments and retention design; fleet dashboard (FEAT-018) after multi-machine evidence. Real POS integrations remain partner-dependent.

