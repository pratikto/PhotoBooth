# Post-preview QRIS — security and durable state specification

**1 November 2026 | Owner-approved target | DESIGN ONLY / NOT IMPLEMENTED / NOT TESTED.** Primary record: [approved flow and 24 decisions](POST-PREVIEW-QRIS-OWNER-APPROVED.md); [test cases](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md); [Codex roadmap](POST-PREVIEW-QRIS-CODEX-HANDOVER.md).

## 1. Non-negotiable invariants

1. For new orders: gallery -> one private photo session **per selected template**, **3 original images plus at most 1 selected-slot retake per template** -> all designs approved -> final preview -> single logical frozen checkout -> provider-verified PAID -> original Recovery Ticket -> exact paid print jobs and Drive delivery. 1–9 copies in current gallery do not create capture sessions. Retake quotas cannot be pooled/reset through editing, deselection, restart or QR renewal.
2. Separate **unpaid private photo draft** from payment authority, service grant and paid delivery. Private local capture/compose may run before payment; photo-strip printer and publicly readable Drive files/folder QR may not. The existing compose-to-auto-print code path is an implementation gap requiring a hard guard.
3. Independent provider evidence, one logical purchase group across QR1/QR2/QR3, exact settled merchant/booth/amount, idempotent payment-attempt creation, reconciliation after timeout/404, and no double service even if two attempts settle. Only **actively continuing** visitors get automatic replacement after verified terminal unpaid expiry. Abandonment stops renewal and requests guarded cancellation/reconciliation.
4. Separate **secure Checkout Claim Proof** (CCP, offered privately at first QRIS before PAID, no ability to see unpaid photos) from **Recovery Ticket** (original post-PAID service capability), QRIS payment QR, download QR, QRIS Payment Slip, operator QR, merchant promo and Meong Fly test QRs. Never treat a receipt/order number or ordinary payment screenshot as authorization to open photos.
5. Customer returning with original CCP after delayed PAID must pass fresh provider settlement, exact order/draft/booth proof, valid capability and occupancy/fence checks. **PAID_UNCLAIMED** without live owner never publicly prints a ticket/strip or reveals photo. Valid claim while B occupies booth -> WAIT/DEFER. No proof -> redacted support/financial complaint path, never tokenless media restoration. **Customer lost genuinely offered proof alone => NO_AUTO_REFUND_PROOF_LOST** and lost self-service recovery; independent merchant failure and PAID/OWED are evaluated separately, not automatically forfeited.
6. **Encrypted credential escrow** allows recovery of the *same original* CCP/Recovery secret after crash only under identity and scope checks; the historical memory-only prohibition is superseded **only for ciphertext in a controlled OS-/hardware-protected vault**. Keep normal journals/SQLite/logs/screenshots/telemetry free of raw secrets, with verifier hashes, rate limits, access audit, version, revocation, TTL and key lifecycle. No decrypt/show on reboot or automatic reissue. Windows DPAPI, Ubuntu TPM/secret service and Android Keystore are candidates requiring validation rather than assumed installed features.
7. **Verified Drive URL before purchased-strip printing for MVP**, including final 3-photo+real-download-QR format. Verified individual folder URL may exist while uploads pending; truthful background retry continues. If Drive service is known unavailable before QRIS, hold new payable checkout; if exact customer URL remains unverified after PAID, preserve owed service/secure claim and do not invent a URL, print false QR or wait forever. Future stable resolver QR is **not** included in MVP and needs separate backend/hosting/security approval.
8. **Adaptive phase-aware inactivity**, with warning, not a blanket wall-clock cutoff for active multi-template photo work. A live countdown, file write, legitimate preview composition or provider status unknown is not inactivity. Sample pilot thresholds are not approved production constants. Unpaid no-payment drafts may be isolated/cleaned only with safe file-worker proof. Once a payment attempt exists, no deletion or release based solely on local timeout.
9. **Edits only before first QRIS attempt.** Copy quantity re-quotes, adding a design requires its own 3 photos, revisiting existing design does not reset used retake; every change increases draft revision. Freeze exact template IDs/artwork hashes, 3 final image IDs/byte checksums per design, retake lineage, copies, discounts authorized by server, currency, amount and approved preview. Final paid raster may differ from preview only by adding the authorized real download QR; three photos/design/copy commitment must match.
10. **Mandatory parallel Recovery Ticket presentation after verified PAID:** for the authorized still-live original customer, **always** show the same original Recovery Ticket QR/full code on the kiosk for **30 visible seconds + NEXT** AND **concurrently dispatch exactly one print of that ticket** through the exclusive receipt/photo printer lane. The screen is NOT a conditional printer-failure fallback: even with printer SUBMITTED, it remains visible. Never wait for printer ACK to show it; printer unavailable/failed/timed out/UNCERTAIN changes only the print job's recorded state, never triggers a second send or reissued token. One rightful presentation per original credential, no poll/reboot redisplay; PAID_UNCLAIMED/visitor B still receives no old ticket until valid claim/lease. SUBMITTED does not prove physical paper.
11. Print job reservations per original paid template/output/copies, one exclusive printer worker shared by ticket and photos; SENDING/UNCERTAIN is never replayed automatically after timeout/crash. Partial paper output needs exact physical evidence; refund-first can settle a **genuinely irrecoverable confirmed paid service failure**, but NEVER from transport uncertainty alone. Photo composition is not service completion. **Isolation itself is not grounds for refund**, cannot destroy PAID/OWED and cannot be bypassed by a later refund. Merchant refund API remains UNVERIFIED.
12. Prior AR-00–13 and unattended handoff safety remain binding: fence private pixels immediately before Advertising, durable PREPARE/local isolate/ACK/archive when safe, no new payable admission on unresolved original financial state, busy visitor never preempted, historical paid-before-photo orders continue legacy versioned recovery unchanged.

## 2. Source-of-truth domains and fields

| Domain | Mandatory durable identity and metadata | Authoritative writer | Consumer fence |
| --- | --- | --- | --- |
| Booth lease | booth_id, occupancy generation, owner visit_id, camera and printer worker generation, release receipt/ACK | authenticated admission/isolation coordinator | all capture/print/claim callbacks |
| Photo draft | draft_id, revision, template-session lineage, three original slots, selected retake index and consumed flag, raw/preview checksums, status, privacy state | local transactional photo worker | camera, preview and draft cleanup |
| Logical checkout | purchase_group_id, exact frozen draft hash/revision, amounts/copies/artwork hashes, promo authority, one claim verifier | purchase checkout orchestrator | provider payment attempts |
| Payment attempts | attempt_id, checkout_key, provider order_id, creation sent/unknown, expiry/cancel/settlement evidence, retry count, original group identity | payment backend/provider reconciliation | QR renewal, discharge/isolation |
| Paid fulfillment | one grant/paid binding, Recovery Ticket job, per-design raster digest/copied quantities, print outcome, valid Drive folder ID/link, upload checksums, OWED ledger | authenticated service backend + fenced workers | physical print/cloud/public QR |
| Credential vault | encrypted original CCP/ticket ciphertext, token verifier, owner scope, key ID, expiry, issuance/presentation proof, access audit | guarded credential service | customer claim and ticket rendering |

No single GUI flag may override another domain. A new payment attempt must never switch the draft or silently mint a new retake quota. Old paid grant and new unpaid draft versions coexist without cross-state migration.

## 3. Proposed state matrix (NOT current source enum)

| State | Allowed | Forbidden |
| --- | --- | --- |
| SAFE_IDLE | admit a new visitor after verified free booth | show prior private pixels |
| DRAFT_CAPTURING / DRAFT_REVIEW | deliberate capture/one selected-slot retake, local save | QRIS before all designs complete; photo print/public Drive |
| DRAFT_READY | all-design final preview, edit/revision | paid completion or public photo |
| DRAFT_FROZEN | charge readiness, unique payment attempt | quantity/artifact/price mutation |
| CREATE_UNKNOWN / PAYMENT_UNKNOWN | same-attempt GET/reconcile and neutral protected hold | duplicate provider order, treating 404 as unpaid |
| PAYMENT_PENDING | same pending QR/CCP, bounded status and cancel intent | print or download; anonymous new checkout |
| TERMINAL_UNPAID | archive attempt; QR2/3 only with live same visitor and cap | erase unsettled/paid obligation |
| PAID_LIVE | exact paid grant, original ticket then owed fulfillment | second grant, extra capture on new flow |
| PAID_UNCLAIMED | OWED, CCP claim and fenced isolation | print/reveal media to next visitor |
| URL_PENDING | retry paid-only link verification, service hold | print fake QR |
| PRINT_SENDING / PRINT_UNCERTAIN | preserve exact original job; inspect | blind resend |
| UPLOAD_PENDING | idempotent checksum-verified paid file retry | reprint or retention-extension shortcut |
| ADS_PROTECTED / EXCEPTION_HOLD | privacy-safe public UI, bounded original retry/support | unsafe admission or charge |
| COMPLETED | archive completed obligations, privacy fence | erase audit/payment records |

## 4. Required race-condition ordering

### Draft before checkout
Persist draft and all 3-photo selected-slot outputs before freezing. Capture and retake operations have durable intent then content/manifest commit. Store exact byte digests of approved photo trio and template assets; reserve no customer-facing Drive entitlement and send no purchased print while unpaid. Deselecting/reselecting is a revision, not a reset of consumed retake.

### Payment create / renewal
Before any Midtrans create request, durably persist the original purchase group and first attempt identity with its idempotency key. A network timeout or 404 must reconcile **the same** attempt, never silently POST a replacement. QR2 and QR3 each have their own durable attempt ID only after prior original terminal unpaid proof, while a continuing customer is active. Any late PAID on an earlier attempt retains exact group and one fulfillment entitlement at most; multiple settled attempts become audited financial conflict, not automatic refund.

### Late PAID and ownership
After A walks away, immediately hide/fence private pixels and retire UI callbacks. Release occupancy only through authorized safe worker isolation and appropriate payment-state-safe closure; public Advertising does not imply backend free. When a late PAID arrives after ownership retirement, persist PAID/OWED and hold fulfillment; never print old secrets into B's kiosk. A later original CCP claim requires new authoritative provider verification and exact booth lease before any private restoration. If B is active, WAIT rather than interrupting B.

### Recovery Ticket / crash
Store the exact original Recovery Ticket credential as protected ciphertext with its paid scope, not plaintext journal. On first valid PAID presentation with original live owner, **start the mandatory 30-second QR+full-code screen and persist/enqueue exactly one receipt-print intent concurrently**; UI must not wait for the printer response. Persist visibility-start time only after QR is actually rendered; NEXT/zero dismisses and securely wipes pixels independent of print outcome. SUBMITTED does not skip screen; failed/unavailable/UNCERTAIN never causes a second print or a second screen. Separate receipt transport journal from customer presentation journal; maintain exclusive printer worker fencing before paid photo strip dispatch. Crash recovery must not auto-display or print the original to a successor; original CCP/ticket proof, fresh PAID, valid scope and FREE booth gate a never-presented original claimant's first safe presentation. Once truly presented, polling/boot does not reset the 30-second opportunity. Vault loss retains OWED and authorized remedy.

### Paid Drive and print
Before QRIS, check known route/storage/payment, Drive API/sharing health and reserve capacity without claiming; once paid, bind original draft to unique service ID and individual verified Drive folder (existing 25-READY design). The URL itself can be valid before bytes finish uploading; start purchased print only with that true authorized QR and exact printer job. Resume upload by same manifest/checksums after crash, no print replay. Printer route SUBMITTED alone does not prove physical paper.

### Protected handoff and old orders
Use exact original release operation, worker fence, typed local receipt, backend ACK and archive; no operator PIN bypass or blanket reset for provider UNKNOWN. A valid ticket/CCP never preempts an occupied camera. Historical paid-first orders use the original PAID -> capture checkpoint and original entitlement, not the new draft route.

## 5. Mandatory transition guards resolving earlier contradictions

**Versioning / source of authority:** These are TARGET rules for `post_preview_v1` orders only. Existing `prepaid_legacy` PAID->camera recovery/UAH receipt and AR states remain versioned and executable for pre-existing orders. Payment receipt, worker states, kiosk occupancy and photo media are independent authority domains; **do not use a single GUI phase as the source of truth for them all**.

### Distinct lifecycle events

| Durable input | May hide private media? | May request provider cancellation? | May renew verified-expired QR? | May free camera/accept new customer? |
| --- | --- | --- | --- | --- |
| `USER_CANCEL` (explicit customer intent) | Yes, immediately | Yes, original attempt only; verify outcome | **No**, even if visitor remains near camera | Only after terminal unpaid OR separately safe PAID/OWED isolation + worker fence + ACK |
| `APP_SUSPENDED` / minimized | Yes, immediately | **No**, not by itself | Not automatically; retain original status | Only after separately proven lost ownership and release rules |
| `INACTIVITY_WARNING` | No automatic abandonment | No | Original live visitor retains continuity | No |
| `INACTIVITY_EXPIRED` after warning | Yes | Only after a distinct durable abandonment decision | **No** once abandoned | No until original finance/worker/release proof |
| `VISIT_ABANDONED` (classified) | Yes | Yes, only for current original attempt | **No** | Only on proven safe closure/release |
| `PROVIDER_EXPIRED_UNPAID` | Follow current owner presentation policy | Not required for verified terminal expiry | **Yes only** active original visitor, no cancel/abandon intent, max QR3 | If no continuation, exact safe isolation first |
| `PROVIDER_CANCELLED_UNPAID` | Yes | Already terminal | **No** | Exact safe isolation first |
| `PROVIDER_PAID` | Original customer or claim authorization only | No | No | PAID/OWED safety and worker isolation required |
| `PROVIDER_UNKNOWN` | Yes when private ownership lost | Reconcile original only; no invented final outcome | No | No new payable checkout without separately authorized safe closure |

**Proof ordering:** privacy wipe -> stop stale callbacks -> persist event intent -> provider reconciliation as needed -> worker drain/fence and local receipt -> scoped backend release ACK/archive -> independently verify FREE. Public Advertising/idle rendering may precede this only as `ADS_PROTECTED` with all capture, game and payment-admission triggers guarded. On reboot, even fresh terminal unpaid evidence does **not** skip the worker/lease barrier.

### Original ticket and CCP lifecycle

- `CCP_CREATED` is bound to the original frozen logical group; `CCP_OFFERED` requires genuinely usable private presentation on the QRIS checkout page. A token merely generated or written to a ledger does not prove customer receipt; do not declare forfeiture for a service that never offered proof.
- Original checkout CCP is a **pre-PAID claim capability**, not the customer's Recovery Ticket, photo download permission, or proof of payment. On live PAID with intact owner lease, ticket issuance does **not** require CCP re-scan.
- On returning PAID claim: verify exact original CCP or original still-valid ticket, fresh provider PAID, frozen draft/booth, valid one-grant entitlement, rate limit and exclusive free booth before decrypting any credential or showing private pixels.
- Receipt `NOT_SENT`, `SENDING`, `SUBMITTED`, `UNCERTAIN`, and customer presentation `NOT_OFFERED`/`RENDERING`/`VISIBLE`/`DISMISSED` are **separate durable dimensions**. At first authorized live post-PAID presentation, **always show the original QR + full code on screen and concurrently enqueue one receipt print**, irrespective of printer health. The original screen remains available for 30 seconds of actual visible QR/code (or until NEXT); the visible timer does not start during loading and does not restart on status polling or printer ACK. Receipt SENDING/UNCERTAIN never auto-replays; receipt SUBMITTED never bypasses this first screen. If the customer was privacy-retired before any genuine presentation, keep PAID_UNCLAIMED/OWED and require exact original CCP/valid claim before first lawful rendering. Previously dismissed original ticket is not automatically redisplayed on boot/return.
- On service failure before any genuine offer, preserve PAID/OWED and authorized support/financial remedy; no tokenless private-media restoration. Under RF-D01..26, **if independently proven permanently unfulfillable and merchant refund channel is approved and safe**, the original paid order may be an auto FULL refund candidate. Do not equate never-offered proof, genuinely lost proof, and irrecoverable service failure.
- Vault content is protected original credential ciphertext only; the public/ordinary backend holds hash-based verifiers, never plaintext keys or secrets. Decrypt only with specific post-PAID scope and customer authorization; machine escrow is **not** a new recovery-ticket issuance mechanism.

### Drive pool and financial readiness

- Before provider CREATE_PREPARED, perform a **read-only authenticated Drive/sharing health and unclaimed 25-READY capacity check** without consuming a reserve or uploading any customer photo. Do not require or expose a customer-specific verified URL before PAID: that URL is created/verified when the original paid transaction binds a folder. Check camera/disk and printer route separately. **Capacity/health is only an availability signal, not guaranteed binding or physical paper proof.**
- After PAID, bind **one** unique exact customer `Photobooth/PB001/Photo/NNNNNNNN` folder and verify its individual viewer URL/permission afresh, then compose final paid-only QR strip. If binding fails, retain PAID/OWED, do not print a false QR or create a second payment. READY pool replenishment uses existing controlled storage procedures.
- Existing dedicated BUG-027 Sandbox (paid-first, receipt/photo printing, Drive OFF) remains legacy regression **only**. Target purchased post-preview synthetic tests use a **separately isolated verified-URL fake** without external publication; it is not live Drive acceptance. Future stable Meong resolver QR is explicitly out-of-scope.
- One internal persistent checkout/attempt key is mandatory. Legacy Midtrans Core `POST /v2/charge` provider-level idempotency header semantics are **UNVERIFIED** and must not be invented; status reconciliation on the same original provider order ID is required on timeout/404.

### Time anchors and retention (explicitly unfinished calibration)

Use separate `draft_created_at`, `checkout_create_intent_at`, `provider_attempt_created_at`, `paid_verified_at`, `ticket_created_at`, `proof_offered_at`, `claim_expires_at`, `transaction_retention_anchor_at`, `last_worker_barrier_at` and `completed_at`. Existing 24-hour Sandbox ticket policy based on original order creation applies to its **legacy version only**. New post-preview CCP/ticket TTL and exact paid-retention anchor are not signed-off numerical requirements yet; document the chosen versioned policy and validate against 15-day local / 30-day Drive storage, avoiding unpaid-draft deletion tied to a generic order timestamp. No automatic clock reset on QR renew, restart or archive. Keep PAID/OWED ledger beyond loss of proof according to authorized financial retention.

### Execution dependency guard

Build the **vault interface/secure CCP contract before** enabling actual late-payment claims. Keep end-to-end claim tests NOT_RUN until payment reconciliation, auth, paid manifest binding, vault, UI and safe release are all present; unit fixture PASS alone never marks the whole flow shipped. All 84 proposed PP acceptance cases remain NOT_RUN as of this documentation-only revision.

### Exactly-once dual-channel ticket presentation: UI and paper independent

| Event or race | Screen behavior | Paper/worker behavior |
| --- | --- | --- |
| PAID verified with original live owner and initial ticket never presented | **Mandatory** same original QR + FULL code, 30 visible seconds + NEXT | Persist one original receipt intent and dispatch concurrently; avoid printer ACK/UI coupling |
| Printer `SUBMITTED` promptly | Keep original screen visible for its entire available 30s/NEXT opportunity | No new receipt send; submitted != paper received |
| Printer offline/not configured/fails | Keep screen unchanged | Record NOT_SENT/FAILED; no automatic reprint after recovery |
| Printer `SENDING`/timeout/`UNCERTAIN` | Keep screen unchanged and countdown running | Hold exact original job; no automatic retry; serialize later purchased-strip writes through the same worker |
| Customer presses NEXT before printer completes | Wipe screen once; retain entitlement + proof-of-offer | In-flight single receipt still governed by original journal; do not cancel/replay or overlap competing raw bytes |
| QR never became visible or ownership was lost | Do not claim a genuine presentation; wipe/lock any private pixels | No new printing for a retired owner; preserve PAID_UNCLAIMED/OWED; original claim required |
| New visitor, restart, repeated PAID callback, previous screen already dismissed | **Never** auto-show earlier ticket or restart countdown | No additional ticket print; inspect/restore original journals only |

The requirement is **concurrent screen availability and print dispatch**, not a promise that physical thermal paper exits at an exact instant. There is **one cryptographic original ticket** shared between QR view and receipt, and one authorized initial presentation event. The user-visible ticket page is mandatory even if the receipt printer works perfectly. Legacy paid-before-camera Sandbox/UAH historical evidence remains unaffected; this is a separate new-order version and tests remain NOT_RUN.

## 6. Timeout, physical/security and implementation boundaries

- Suggested **pilot-only** starting points: gallery 60–90s, capture/review 120s, final preview 90–120s of actual inactivity, with warning. These are tunable and NOT fixed owner-approved numbers. No automatic hard cap interrupting active photos; payment uncertainty uses provider reconciliation, never a UI inactivity shortcut.
- CCP and original ticket should use cryptographically secure unpredictable secrets, constant-time comparisons, hashes/verifiers, version/scope/expiry and replay protections; offer CCP privately when QRIS starts, not as the charge QR. Screenshot/payment number is not private-media authorization. Do not treat storing a token server-side as evidence it was presented to the customer.
- Threats: shoulder-surfing, lost proof, duplicate/cross-type QR, stale camera callbacks, accidental old photo thumbnail, malicious kiosk operator, disk theft, malicious OS account, wrong-booth cloud folder, webhook replay, fake settlement, paper left for B, key escrow loss. Appropriate operational monitoring and real device testing required.
- **New refund-first policy, strictly gated (new post-preview orders only):** genuine irrecoverable independently proven paid delivery failure can trigger an automatic full original-provider refund only after merchant refund API activation/eligibility verification, durable original refund intent, print/Drive safe fence and exact provider response handling; unambiguous duplicate-settled excess charge may refund excess only. No auto-refund **solely from a technical timeout, customer-lost proof, abandoned session, unknown provider, or UNCERTAIN paper**. Finance/merchant/legal/production activation remain separately required; legacy code still issues no refunds.
- No code, schema, payment credentials, secrets, OS vault provisioning, physical/cloud effects or deployments authorized by these documentation changes. Never inspect or change excluded archive `old`.

## 7. Refund, lost proof, and financial fulfillment separation (new owner-approved design)

**Authoritative detail:** [RF-D01–RF-D26 refund-first and lost-proof policy](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md), [all owner decisions](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md). All states in this section are **PROPOSED / NOT IMPLEMENTED**; the merchant Refund API has not been enabled/tested.

### Cross-product outcome: refund is a separate axis, not a payment-state rewrite

| Original provider payment | Service fulfillment | Refund subledger | Meaning and permitted next action |
| --- | --- | --- | --- |
| PENDING / UNKNOWN | Private draft frozen | NONE | Same original cancel/status reconciliation, no refund |
| PAID | Original paid service available/delivered | NONE | No refund merely due to lost CCP/ticket; no tokenless media unlock |
| PAID | Original OWED, safely recoverable | NONE | Continue bounded original recovery with honest pending state |
| PAID | Independently proven irrecoverable merchant failure | ELIGIBILITY_REVIEW | Verify full-payment refund support, original print/Drive quiescence and merchant guard |
| PAID | Independently proven unambiguous duplicate-settled *excess attempt* | EXCESS_REFUND_ELIGIBLE | Refund the excess settled attempt only; preserve exactly one paid service entitlement |
| PAID | Original media/print worker SENDING/UNCERTAIN | ON_HOLD | No blind reprint/refund/assumed zero physical paper; safe physical/technical classification |
| PAID | Customer genuinely lost valid proof, no separately proven merchant fault | NO_AUTO_REFUND_PROOF_LOST | No self-service photo recovery and no automatic refund *solely for proof loss*. Preserve financial audit and lawful complaint handling |
| PAID | CCP/ticket never genuinely offered, original service uncertain | PAID_OWED_REMEDY | No consumer blame; original safe claim/remedy and refund if separately proven irrecoverable |
| PAID | Safe classified irrecoverable service | REFUND_INTENT_PREPARED / REQUESTED / PROCESSING | Original provider refund key, same-original reconciliation; service delivery stays fenced |
| PAID | Safe failure / duplicate excess and independently confirmed refund | REFUND_CONFIRMED | Record original provider/refund evidence; never auto-unlock original paid print or media afterward |
| PAID | Refund API disabled/rejected or conflicting financial facts | REFUND_REVIEW_REQUIRED | Authenticated finance/support/security, no fabricated successful refund |

**Never mutate PAID back to UNPAID** merely because refund was requested or confirmed. Maintain original paid financial identity and immutable fulfillment obligations with a separate refund audit ledger; closure/waiver only upon verified delivered/replaced/refunded amount according to approved accounting and consumer rules. A refund does **not** release machine occupancy or erase physical print SENDING/UNCERTAIN.

### Required refund journal, identifiers and provider verification

- Original `refund_intent_id`, merchant ID, booth ID, purchase_group_id, **exact provider payment attempt/order/transaction ID** (important for QR1/QR2/QR3), settled original amount/currency, eligible refund amount, reason, copy/print/Drive outcome, original refund_key and API schema version, timestamps, authorization and current verified refund state.
- First independently verify original provider SETTLEMENT. Never refund on PENDING/UNKNOWN/CREATE_UNCERTAIN, local timer expiry, GUI ERROR or mere abandoned claim.
- For **full refund of irrecoverable merchant delivery failure**, prove bounded original recovery exhausted, exact entitlement missing, authorized policy and safe original worker/paper/Drive stop or quarantine. If a paper job is UNCERTAIN and could still eject, classify/hold instead of pretending the refund stops hardware. For **verified duplicate excess-only refund**, preserve the one rightful original service/print/upload while reconciling and refunding only the excess paid attempt. Never globally halt valid paid work because a duplicate charge is returned.
- Persist one uniquely keyed refund intent **before provider I/O**. Lost response/timeout/restart/409 -> reconcile same original key/reference; no second random refund POST. Do not assume Midtrans Core refund semantics without official merchant verification.
- Official GoPay QRIS POS may have online refund **disabled by default**; time windows, issuer/on-us/off-us, merchant balance and status can prevent online automatic refund. An ineligible case goes `REFUND_REVIEW_REQUIRED`, not fake `REFUND_CONFIRMED`. Never automatically send money to a user-entered account at a public kiosk.
- Frontend refund statuses distinguish intent, provider accepted, processing and provider confirmed; customer bank/wallet funds visible is a separate real-world outcome. Never promise fixed return-time or successful automatic refund without real provider evidence.
- Refund decision after genuinely lost CCP/Recovery Ticket when **no independent merchant failure** is explicitly `NO_AUTO_REFUND_PROOF_LOST`, not `REFUND_ELIGIBLE`. A generated but never-visible QR, printer receipt merely SUBMITTED, or crash before genuine offer cannot be classified as genuine customer loss.
- Suspected forged claim, compromised escrow, disputed refund, two settlements with mismatching merchant/amount, false fulfillment or unsafe machine fencing require proper scoped human review. Support may review redacted money/status but cannot manufacture customer secret or reveal protected photos.
- Consumer-protection terms require legal-reviewed wording. No automatic refund **solely** for losing a genuinely offered proof is a narrow policy, not an unconditional "money can never be refunded" waiver.

### Refund eligibility decision diagram

~~~mermaid
flowchart TD
    F([Original paid service problem]) --> P{Fresh independently verified SETTLED?}
    P -->|No / UNKNOWN| RECON[Same original provider reconciliation; no refund]
    P -->|Yes| CAUSE{Evidence-backed cause?}
    CAUSE -->|Lost genuinely offered CCP/ticket only| LOST[NO_AUTO_REFUND_PROOF_LOST; no photo unlock]
    CAUSE -->|Departed / late PAID / recoverable hold| WAIT[PAID_UNCLAIMED / OWED; original claim and bounded retry]
    CAUSE -->|Fraud / payment conflicts / refund not enabled| REVIEW[FINANCIAL / SECURITY REVIEW]
    CAUSE -->|Irrecoverable merchant delivery failure| FENCE[Quarantine exact original print/upload/media]
    CAUSE -->|Independently proved duplicate settled excess| EXCESS[Refund excess attempt ONLY; rightful single paid service continues]
    FENCE --> SAFE{Original worker/physical outcome safe and merchant API eligible?}
    SAFE -->|No| REVIEW
    SAFE -->|Yes| ELIG[Full original-payment refund eligible]
    EXCESS --> ELIG2[Exact excess payment eligible; no extra service]
    ELIG --> INTENT[Persist original refund intent/key]
    ELIG2 --> INTENT
    INTENT --> POST[Request original merchant-provider refund ONCE]
    POST --> R{Provider refund status?}
    R -->|Processing| PENDING[REFUND_PROCESSING; no claim money arrived]
    R -->|Unknown| REC[Reconcile SAME refund key, no duplicate]
    REC --> R
    R -->|Provider confirmed| CONF[REFUND_CONFIRMED; independent paid/worker ledger preserved]
    R -->|Rejected / unsupported| REVIEW
    PENDING --> R
~~~

**External and production acceptance:** refund-first remains **not executable until separate permission**, source update, provider Refund API activation, protected backend, refund reconciliation, true printer/Drive failure tests, merchant limits/legal review and recorded sign-off. [Refund decision details](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md).

