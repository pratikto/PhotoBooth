# Post-preview QRIS — security and durable state specification

**1 November 2026 | Owner-approved target | DESIGN ONLY / NOT IMPLEMENTED / NOT TESTED.** Primary record: [approved flow and 24 decisions](POST-PREVIEW-QRIS-OWNER-APPROVED.md); [test cases](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md); [Codex roadmap](POST-PREVIEW-QRIS-CODEX-HANDOVER.md).

## 1. Non-negotiable invariants

1. For new orders: gallery -> one private photo session **per selected template**, **3 original images plus at most 1 selected-slot retake per template** -> all designs approved -> final preview -> single logical frozen checkout -> provider-verified PAID -> original Recovery Ticket -> exact paid print jobs and Drive delivery. 1–9 copies in current gallery do not create capture sessions. Retake quotas cannot be pooled/reset through editing, deselection, restart or QR renewal.
2. Separate **unpaid private photo draft** from payment authority, service grant and paid delivery. Private local capture/compose may run before payment; photo-strip printer and publicly readable Drive files/folder QR may not. The existing compose-to-auto-print code path is an implementation gap requiring a hard guard.
3. Independent provider evidence, one logical purchase group across QR1/QR2/QR3, exact settled merchant/booth/amount, idempotent payment-attempt creation, reconciliation after timeout/404, and no double service even if two attempts settle. Only **actively continuing** visitors get automatic replacement after verified terminal unpaid expiry. Abandonment stops renewal and requests guarded cancellation/reconciliation.
4. Separate **secure Checkout Claim Proof** (CCP, offered privately at first QRIS before PAID, no ability to see unpaid photos) from **Recovery Ticket** (original post-PAID service capability), QRIS payment QR, download QR, QRIS Payment Slip, operator QR, merchant promo and Meong Fly test QRs. Never treat a receipt/order number or ordinary payment screenshot as authorization to open photos.
5. Customer returning with original CCP after delayed PAID must pass fresh provider settlement, exact order/draft/booth proof, valid capability and occupancy/fence checks. **PAID_UNCLAIMED** with no live owner must not publicly print a ticket, strips or reveal photo. Valid claim while B occupies booth -> WAIT/DEFER. No proof -> redacted support/financial remedy, never tokenless private-media restoration. Lost proof after genuine offer forfeits self-service photo recovery only, not PAID/OWED obligations.
6. **Encrypted credential escrow** allows recovery of the *same original* CCP/Recovery secret after crash only under identity and scope checks; the historical memory-only prohibition is superseded **only for ciphertext in a controlled OS-/hardware-protected vault**. Keep normal journals/SQLite/logs/screenshots/telemetry free of raw secrets, with verifier hashes, rate limits, access audit, version, revocation, TTL and key lifecycle. No decrypt/show on reboot or automatic reissue. Windows DPAPI, Ubuntu TPM/secret service and Android Keystore are candidates requiring validation rather than assumed installed features.
7. **Verified Drive URL before purchased-strip printing for MVP**, including final 3-photo+real-download-QR format. Verified individual folder URL may exist while uploads pending; truthful background retry continues. If URL unverified before QRIS, hold new payable checkout; if unexpectedly unverified after PAID, preserve owed service/secure claim and do not invent a URL, print false QR or wait forever. Future stable resolver QR is **not** included in MVP and needs separate backend/hosting/security approval.
8. **Adaptive phase-aware inactivity**, with warning, not a blanket wall-clock cutoff for active multi-template photo work. A live countdown, file write, legitimate preview composition or provider status unknown is not inactivity. Sample pilot thresholds are not approved production constants. Unpaid no-payment drafts may be isolated/cleaned only with safe file-worker proof. Once a payment attempt exists, no deletion or release based solely on local timeout.
9. **Edits only before first QRIS attempt.** Copy quantity re-quotes, adding a design requires its own 3 photos, revisiting existing design does not reset used retake; every change increases draft revision. Freeze exact template IDs/artwork hashes, 3 final image IDs/byte checksums per design, retake lineage, copies, discounts authorized by server, currency, amount and approved preview. Final paid raster may differ from preview only by adding the authorized real download QR; three photos/design/copy commitment must match.
10. **One original Recovery Ticket after PAID:** once send on configured printer; failed/unavailable/timed out/UNCERTAIN -> offer original QR and full code on-screen for visible 30 seconds and NEXT, exactly-once dismissal, never duplicate/reprint uncertain job. A printer transport SUBMITTED is not proof that a physical paper slip emerged.
11. Print job reservations per original paid template/output/copies, one exclusive printer worker shared by ticket and photos; SENDING/UNCERTAIN is never replayed automatically after timeout/crash. Partial paper output needs physical evidence and operator-last-resort remedy. Photo composition is not service completion. Never automatically refund or destroy PAID/OWED on isolation.
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
Store a securely protected original ticket credential with its exact paid scope, not unencrypted plaintext in journal. Attempt the receipt once with SENDING persisted before external side effect; UNCERTAIN never auto-replayed. If the live owner remains and receipt unavailable, the same ticket appears on-screen for 30s and NEXT. Crash recovery does not automatically show or print secret; original CCP/ticket proof, fresh PAID, valid scope and free booth must gate redemption. If vault/key lost, retain OWED and require authorized remedy.

### Paid Drive and print
Before QRIS, check known route/storage/payment and verified link feasibility; once paid, bind original draft to unique service ID and individual verified Drive folder (existing 25-READY design). The URL itself can be valid before bytes finish uploading; start purchased print only with that true authorized QR and exact printer job. Resume upload by same manifest/checksums after crash, no print replay. Printer route SUBMITTED alone does not prove physical paper.

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
- Receipt `NOT_SENT`, `SENDING`, `SUBMITTED`, `UNCERTAIN`, and customer presentation `NOT_OFFERED`/`OFFERED`/`PRESENTED` are **separate durable dimensions**. One original printer send; SENDING/UNCERTAIN never replay. If the print is unavailable/fails/uncertain and the live original customer can receive the **same** token, show it exactly once for 30 seconds of actual visibility with NEXT. Do not automatically show fallback after SUBMITTED, on polling, or on reboot.
- On service failure before any genuine offer, preserve PAID/OWED and an authorized support/financial remedy; no tokenless private-media restoration, no automatic refund.
- Vault content is protected original credential ciphertext only; the public/ordinary backend holds hash-based verifiers, never plaintext keys or secrets. Decrypt only with specific post-PAID scope and customer authorization; machine escrow is **not** a new recovery-ticket issuance mechanism.

### Drive pool and financial readiness

- Before provider CREATE_PREPARED, observe *availability* of a verified, currently unclaimed 25-READY photo-folder reserve (and individual folder URL) without consuming the reserve or uploading any customer photo. Also check camera/disk and a printer route. **This is an availability signal, not a guaranteed future binding or proof paper will print.**
- After PAID, bind **one** unique exact customer `Photobooth/PB001/Photo/NNNNNNNN` folder and verify its individual viewer URL/permission afresh, then compose final paid-only QR strip. If binding fails, retain PAID/OWED, do not print a false QR or create a second payment. READY pool replenishment uses existing controlled storage procedures.
- Existing dedicated BUG-027 Sandbox (paid-first, receipt/photo printing, Drive OFF) remains legacy regression **only**. Target purchased post-preview synthetic tests use a **separately isolated verified-URL fake** without external publication; it is not live Drive acceptance. Future stable Meong resolver QR is explicitly out-of-scope.
- One internal persistent checkout/attempt key is mandatory. Legacy Midtrans Core `POST /v2/charge` provider-level idempotency header semantics are **UNVERIFIED** and must not be invented; status reconciliation on the same original provider order ID is required on timeout/404.

### Time anchors and retention (explicitly unfinished calibration)

Use separate `draft_created_at`, `checkout_create_intent_at`, `provider_attempt_created_at`, `paid_verified_at`, `ticket_created_at`, `proof_offered_at`, `claim_expires_at`, `transaction_retention_anchor_at`, `last_worker_barrier_at` and `completed_at`. Existing 24-hour Sandbox ticket policy based on original order creation applies to its **legacy version only**. New post-preview CCP/ticket TTL and exact paid-retention anchor are not signed-off numerical requirements yet; document the chosen versioned policy and validate against 15-day local / 30-day Drive storage, avoiding unpaid-draft deletion tied to a generic order timestamp. No automatic clock reset on QR renew, restart or archive. Keep PAID/OWED ledger beyond loss of proof according to authorized financial retention.

### Execution dependency guard

Build the **vault interface/secure CCP contract before** enabling actual late-payment claims. Keep end-to-end claim tests NOT_RUN until payment reconciliation, auth, paid manifest binding, vault, UI and safe release are all present; unit fixture PASS alone never marks the whole flow shipped. All 84 proposed PP acceptance cases remain NOT_RUN as of this documentation-only revision.

## 6. Timeout, physical/security and implementation boundaries

- Suggested **pilot-only** starting points: gallery 60–90s, capture/review 120s, final preview 90–120s of actual inactivity, with warning. These are tunable and NOT fixed owner-approved numbers. No automatic hard cap interrupting active photos; payment uncertainty uses provider reconciliation, never a UI inactivity shortcut.
- CCP and original ticket should use cryptographically secure unpredictable secrets, constant-time comparisons, hashes/verifiers, version/scope/expiry and replay protections; offer CCP privately when QRIS starts, not as the charge QR. Screenshot/payment number is not private-media authorization. Do not treat storing a token server-side as evidence it was presented to the customer.
- Threats: shoulder-surfing, lost proof, duplicate/cross-type QR, stale camera callbacks, accidental old photo thumbnail, malicious kiosk operator, disk theft, malicious OS account, wrong-booth cloud folder, webhook replay, fake settlement, paper left for B, key escrow loss. Appropriate operational monitoring and real device testing required.
- Separate merchant-finance remediation (refund/credit/customer dispute) requires explicit authorization; no auto-refund as a technical timeout response.
- No code, schema, payment credentials, secrets, OS vault provisioning, physical/cloud effects or deployments authorized by these documentation changes. Never inspect or change excluded archive `old`.
