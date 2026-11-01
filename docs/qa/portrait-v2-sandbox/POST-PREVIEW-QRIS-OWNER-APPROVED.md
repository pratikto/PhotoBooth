# Post-preview QRIS checkout — owner-approved product contract

**Date:** 1 November 2026 (Asia/Jakarta)  
**Target branch:** `feature/post-preview-qris-checkout` (branched from `feature/portrait-kiosk-v2-next` at `97a6c1574f0692d8a3db8b3a4d94778f87937e18`).  
**Status:** **OWNER-APPROVED DESIGN / DOCUMENTATION ONLY / NOT IMPLEMENTED / NOT TESTED**. This document authorizes a detailed documentation baseline, **not** a source-code, API, schema, test, payment, OS-vault, production, hardware, cloud, default-branch or master change.  
**Companions:** [security and state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [acceptance matrix](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) · [Codex handover](POST-PREVIEW-QRIS-CODEX-HANDOVER.md). · [20-finding consistency reconciliation](POST-PREVIEW-QRIS-CONSISTENCY-AUDIT.md).


> **NEW OWNER-APPROVED REFUND DECISION (same branch, design only):** When paid photos cannot be fulfilled after safe bounded recovery, prefer merchant-authorized auto **FULL refund** of the original settled payment (with exact print/Drive fencing/provider refund-key verification); if two attempts independently settle, return only the **unambiguous excess** charge. **Lost genuinely offered CCP/Recovery Ticket alone never triggers an automatic refund or tokenless media recovery**. Never-offered proof or separately proven merchant failure remain PAID/OWED/remedy candidates. No blanket contractual 'uang hangus' or waiver of Indonesian consumer rights; current Midtrans POS refund capability is **UNVERIFIED**. This newer narrow policy supersedes previous unconditional no-auto-refund prose for NEW orders only. [Complete owner ledger](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) · [refund/proof-loss contract](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md).
> **Branch-specific precedence.** For **new post-preview orders**, this owner approval supersedes the **payment-before-capture ordering** in earlier GUI v2/Sandbox, BUG-026/027/028, AR and unattended-handoff diagrams; **it does not supersede their safety properties**. Existing prepaid customer orders and in-flight legacy PAID -> camera recovery MUST keep their original versioned fulfillment route. Earlier documented CI PASS, on-device reports and historical proofs remain valid only for the old source/flow. Existing AR-00–AR-13/UAH no-double-charge, privacy/fencing, paid/owed, strict provider evidence, no uncertain reprint, retention and operator-last-resort protections stay mandatory. Existing measured production readiness remains CONDITIONAL / NOT APPROVED.

## 1. Owner decision register — final product policy (PP-D01–PP-D24)

| ID | Owner-approved decision | Required clarification / boundary |
| --- | --- | --- |
| PP-D01 | New commercial route: **Gallery -> capture and review all selected designs -> final preview -> one QRIS checkout -> verified PAID -> original Recovery Ticket -> print/Drive fulfillment**. | No paid photo capture before checkout on the new route; no free photo output or public link before verified settlement. |
| PP-D02 | **Exactly 3 initial captures per selected template**, **maximum 1 retake of one slot PER TEMPLATE**. | New template gets its own session; print copy quantities never multiply capture count. Do not pool quotas, erase a used quota by deselect/reselect, or recapture on QR renewal. |
| PP-D03 | One logical cart and total payment for every selected template/copy. | One frozen logical purchase, one legitimate paid fulfillment entitlement; QR replacements are individually journaled provider attempts, not extra purchases. |
| PP-D04 | **Secure Checkout Claim Proof (CCP)** is privately offered **when payable checkout begins, before PAID**. | Random high-entropy original claim capability, bound to booth/logical purchase/frozen draft; hashed verifier, versioned/expiring/rate-limited; never an ordinary order number, QRIS payload, DEMO/operator QR, Recovery Ticket, or proof that money was paid. |
| PP-D05 | CCP enables returning customers to claim **late-settled PAID** orders unattended after fresh independent payment/ownership checks. | Claims do not open unpaid photos; busy booth -> WAIT/DEFER, never preempt; missing customer proof never authorizes private-photo disclosure. |
| PP-D06 | **Always display the original Recovery Ticket screen for a newly verified PAID order with its live rightful customer, while concurrently submitting exactly one print job for that SAME ticket.** | This is the **normal dual-channel presentation**, NOT a printer-failure fallback. Screen shows original QR + FULL code for 30 visible seconds with countdown and NEXT/LANJUT whether printer succeeds, is absent, fails, times out, or returns UNCERTAIN. Launch screen rendering and single authorized print dispatch without waiting for printer ACK; serialize actual printer transport with other photo jobs. Never issue replacement ticket, auto-reprint UNCERTAIN/SENDING, reset the 30s timer on polling, or expose a ticket to a different visitor. Retired PAID_UNCLAIMED requires original CCP/ticket claim and free booth before any screen or printer dispatch. |
| PP-D07 | Use **encrypted credential escrow** for crash survivability, with strict access controls and least-privilege redemption. | Do not save plaintext secrets/QR bitmaps in SQLite, journals, logs, screenshots, clipboard, Git or telemetry. An encrypted vault is a narrow exception to historical memory-only rules; it is NOT permission to reveal tickets on reboot or to duplicate prints. |
| PP-D08 | **MVP printing waits for a verified customer download URL**; then final strip has 3 photos + 1 real QR. | Valid verified folder URL may precede upload completion; pending upload can continue in background. No invented QR or exposed public media before PAID. No unbounded paid wait: persist PAID/OWED and provide safe recovery/support path. |
| PP-D09 | Preserve the old **offline local capture** capability. | When internet/Drive link is not ready at charge-readiness, do not knowingly create a payable order. Once PAID, hold printed delivery until QR URL verification; this narrowly changes old immediate-offline-print expectations for the new purchased route. |
| PP-D10 | A future **stable Meong resolver QR** is the preferred follow-on architecture, **not part of MVP**. | No speculative hostname, public resolver, hosting, payment bypass or redirect service may be shipped under this design-only approval. |
| PP-D11 | **Adaptive inactivity timeout** by current phase; no hard cutoff that interrupts an actively capturing multi-template customer. | Camera work/countdown, legitimate busy worker and payment uncertainty are not ordinary UI inactivity. Numeric pilot values are configurable recommendations to validate, not signed-off constants. |
| PP-D12 | **Edits allowed only before first provider-create intent is durably recorded**, preserving consumed retake quotas and draft ancestry. | A provisional draft snapshot can be revised before that boundary; each change re-quotes/re-freezes. Copy-count changes do not create new captures; newly added template needs its own 3; deselect/reselect cannot reset retake. Once CREATE_PREPARED is persisted, cart, revision, artifacts, promo and amount become immutable even if the provider response is lost or QR is not yet visible. |
| PP-D13 | Maintain current **QR1 -> QR2 -> QR3 -> Advertising**, maximum three verified unpaid expirations for an **actively continuing customer**. | Replacement must use the same immutable logical draft and amount, new attempt ID, original status checked, previous safely terminal unpaid; third expires -> safeguarded isolation. No QR4; never renew for an abandoned visitor. |
| PP-D14 | For **abandonment during PENDING/UNKNOWN**, use same-order cancel/reconciliation and safe occupancy isolation, not automatic QR renewal. | Browser timeout, QR countdown, HTTP 404 or old cached UNPAID never equal terminal financial proof. |
| PP-D15 | Customer data stays private in **unpaid draft local staging** before payment. | No customer-facing Drive upload/share/download QR, paid photo print or accidental background auto-print; QRIS payment-slip printing is distinct and allowed only through its own guarded pending-order path if separately implemented. |
| PP-D16 | Preview composition may complete before payment, but **service fulfillment must not**. | `DRAFT_READY` ≠ `PAID` ≠ `FULFILLED`. Final printed strip may replace a prepay QR placeholder with the real paid-only QR, while final three photos/layout/design/copy requirement remain matched. |
| PP-D17 | Before capture check camera/disk/templates/local staging; **before QRIS** verify frozen outputs, local durability, printer-route readiness, payment connectivity, and delivery-URL policy. | Precharge checks are read-only: authenticated Drive service/sharing capability, available unclaimed READY pool capacity and known delivery health, **without consuming a reserve or assuming that a customer URL already exists before binding**. After PAID atomically bind a customer folder and verify its exact viewer URL; if this fails retain PAID/OWED and withhold photo-strip printing. Route observation ≠ physical paper detection. Isolated legacy Sandbox and future purchased post-preview test profile are distinct. |
| PP-D18 | Automatic session isolation only with proven fence/worker quiescence/backend release or safe local draft closure. | Prior PAID/OWED remains auditable. Protected Advertising is only a public UI, not authority to admit a new charge or show prior media. Operator only for unsafe/ambiguous financial, hardware, security or corrupt-data cases. |
| PP-D19 | One immutable draft-to-paid binding and one entitlement per logical purchase across all QR attempts. | Detect multiple settled attempts/amount mismatches; never double-fulfill or silently treat excess payment as free service. **New refund-first policy:** independently verified unambiguous excess settlement may initiate a **single provider-authorized refund of only the excess charge** after exact identity/worker/merchant gates; ambiguous financial conflicts remain REVIEW. |
| PP-D20 | Purchase printing uses durable job reservations with exact design/output/copies, one printer owner and no uncertain replay. | `SENDING`/`UNCERTAIN` are NOT paper-success evidence; partial print requires independently classified physical evidence, no automatic reprint. **New refund-first:** irrecoverable independently established merchant failure may become FULL refund candidate only after original print/Drive work fenced and merchant refund enabled; uncertain paper alone cannot trigger unconditional refund. Ticket and strips have independent job identities but shared printer exclusivity. |
| PP-D21 | Google Drive must be gated on authenticated PAID entitlement and exact folder identity. | Use existing `Photobooth/PB001/Photo/00000001/{raw,bw,color}` contract; 25 READY reserves must not be consumed by arbitrary unpaid visitors. Verify anyone-reader link for the right individual customer folder only and use retention guards. |
| PP-D22 | Existing Meong Fly one-use ticket and single-game-attempt ledger remain authoritative. | Unpaid checkout abandonment cannot reset the game or discount. Sandbox reward remains demonstrative/full-price unless a **trusted backend promotion** contract exists. No stacking without separate approval. |
| PP-D23 | Historical prepaid legacy orders remain on their original **PAID -> photo** recovery semantics, versioned separately. | No forced conversion of old paid grants/manifests/print jobs into unpaid drafts. |
| PP-D24 | This **documentation-only task does not execute any refund**, activate a production gateway, roll out Android, publish a webhook, delete customer data, modify application code or merge/master. **New owner-approved design, separately:** refund-first for verified irrecoverable merchant service failure or unambiguous excess settlement, but **NO_AUTO_REFUND solely due to genuinely offered CCP/Recovery Ticket being lost**. | Merchant-specific Midtrans refund API activation, provider/merchant/consumer-law compliance and AR-13 external gates remain **NOT VERIFIED / NOT IMPLEMENTED**. Refer to RF-D01..26. |

### Policy precedence and explicit supersessions

1. **Only on this dedicated branch/new version** the payment-before-camera ordering, paid-camera photo admission as the sole possible route, and mandatory ticket-before-camera diagram are superseded. **Safety guards are preserved and adapted, not bypassed.**
2. Historical BUG-026 automatic QR1/2/3 applies while the **same original checkout remains actively owned**. Abandonment instead requests guarded original-attempt cancellation/reconciliation; no silent renewal for absent customers.
3. **New owner correction:** for new post-preview purchases the Recovery Ticket screen **always appears after PAID and at the same time one original ticket print is dispatched**; the old 30-second **printer-failure-only fallback** is superseded for this new route. The UI is always shown with original QR/full code and 30s + NEXT, independent of printer response. After the ticket stage, continue to fulfillment/printing, not new camera admission. Legacy prepaid orders retain their original separate historical policy and PAID->camera route.
4. The previously documented **do-not-persist-raw-ticket** rule remains true for ordinary databases, files, app logs, backups and media. The sole new exception is a **protected encrypted credential vault** with controlled identity binding, access/audit/expiry and policy-gated retrieval.
5. Previous ability to print a strip fully offline persists for ordinary/local nonpayable test profiles. For new **purchased** strips with a customer Drive QR, unknown/unverified URL blocks final printed strip until resolved; a stable resolver is separate future scope.
6. No original PAID/OWED is voided by expiration, privacy isolation, unpaid draft cleanup, loss of a genuinely presented ticket or offline inability to print. Proof absent before it was ever offered is a **service failure/claim problem**, not customer negligence.

## 2. Customer-visible route and identity taxonomy

**QR/payment credentials are not interchangeable:** Payment QRIS (provider charge); Checkout Claim Proof (pre-PAID private claim capability, initially not a photo entitlement); Recovery Ticket (post-PAID original service-recovery capability); photo-folder/download QR (paid authorized delivery URL); QRIS Payment Slip (printed view of active pending payment QR); operator login QR; merchant promo receipt/Meong Fly DEMO QR. Every scanner/endpoint validates its own type, version, scope, validity and provenance; reject cross-use.

**Visible UI sequence:**
1. Public Advertising (option to reclaim original purchase by proof) -> photo/game entry.
2. One-time tutorial -> original 12-design gallery, choose per-design 1–9 copies in current UI.
3. Per selected design: exactly three captures with deliberate 5s SIAP countdown each, optional one selected-slot retake, review and approve. Continue until every design approved; no paper, public link or provider order yet.
4. Final preview across **all** selected designs, transparent total/copies/reward rules; edit allowed only before payment-attempt creation and never replenishes prior used retake.
5. Atomic freeze of draft/revision/templates/assets/copies/output checksums, independent server quote, charge readiness; create original payment attempt and **offer CCP privately on checkout page**.
6. QRIS provider pending: status polling, QR1/2/3 on verified unpaid expiry only while the same visitor is active; unknown/backoff and guarded abandonment; never create second payable attempt from stale/UI-only evidence.
7. Fresh PAID with original live customer -> exact paid draft binding -> **always open the original Recovery Ticket screen and concurrently submit ONE original ticket print job** (same QR/full code on paper and screen). Display the **visible 30-second countdown + NEXT/LANJUT** regardless of printer result, including SUBMITTED. Printer failure does **not** condition ticket screen entry, restart its timer, or authorize reprint. Dismiss on NEXT/zero once; protect privacy if the session retires. Ticket-only print may occur before final Drive URL; purchased photo strip still waits for its verified URL.
8. Link/folder verified -> final original three-photo strip with genuine link QR -> durable paid photo print job(s) -> background upload and download presentation. Truthfully label pending uploads.
9. Fulfillment/printing unknown -> preserve obligations, private claim and safe machine isolation; no duplicate print. Completed/archived -> wipe private UI before Advertising.

### Flow A: end-to-end route, expiry-versus-cancel and protected entry

~~~mermaid
flowchart TD
    BOOT([Public Advertising, hidden old private pixels]) --> OCC{Original booth lease FREE?}
    OCC -->|Yes| ENTRY[Admit new visitor after durable free proof]
    OCC -->|No| ISO[Classify original financial state and worker leases]
    ISO --> SAFE{Safe original isolation + backend ACK proven?}
    SAFE -->|No / unknown| HOLD[ADS_PROTECTED: neutral hold, no new charge]
    SAFE -->|Yes| ENTRY
    ENTRY --> ROUTE{Photo or Meong Fly?}
    ROUTE -->|Game| GAME[One-use game ledger -> tutorial]
    ROUTE -->|Photo| TUT[Tutorial]
    GAME --> GALLERY[Choose templates and copies]
    TUT --> GALLERY
    GALLERY --> PREF[Camera, private disk, artwork readiness]
    PREF --> READY{Ready?}
    READY -->|No| RETRY[Repair or cancel without payment]
    RETRY --> PREF
    READY -->|Yes| DRAFT[Private unpaid draft, each template owns retake quota]
    DRAFT --> CAP[3 shots, optional 1-slot retake, approval per template]
    CAP --> MORE{Another selected template?}
    MORE -->|Yes| CAP
    MORE -->|No| FINAL[Final all-template preview; edit only before CREATE_PREPARED]
    FINAL --> FREEZE[Freeze draft and server-side quote]
    FREEZE --> CHK[Precharge readiness: printer route + authenticated Drive health + unclaimed READY capacity]
    CHK --> OK{Charge-ready?}
    OK -->|No| PAUSE[Hold unpaid draft; revise pre-create or retry]
    PAUSE --> CHK
    OK -->|Yes| CCP[Persist purchase/attempt intent + original private CCP offer]
    CCP --> PAY[QRIS1, exact provider status and active-visitor renewal policy]
    PAY --> STATUS{Authoritative financial outcome?}
    STATUS -->|PENDING / UNKNOWN| GUARD[Original attempt poll/cancel intent; protected hold if unsafe]
    GUARD --> PAY
    STATUS -->|Verified EXPIRED unpaid| RENEW{Same visitor actively continuing and attempt count less than 3?}
    RENEW -->|Yes| PAY
    RENEW -->|No| ENDUNPAID[Terminal unpaid original visit; privacy + worker isolation/ACK]
    STATUS -->|Verified CANCELLED unpaid| ENDUNPAID
    ENDUNPAID --> FREE{Durably FREE with no old in-flight worker?}
    FREE -->|No| HOLD
    FREE -->|Yes| ADS[Safe Advertising and new visitor admission]
    STATUS -->|Verified PAID| OWNER{Original owner still live or valid returning CCP?}
    OWNER -->|No| UNCLAIM[PAID_UNCLAIMED + OWED, private claim only, no old public printing]
    OWNER -->|Yes| TICKET[Always show same Recovery Ticket QR/full code 30s + NEXT; concurrently send ONE ticket print]
    TICKET --> DELIVERY[Bind exact paid Drive folder, verify URL, print strips + upload]
    DELIVERY --> OBL{Original paid obligations resolved?}
    OBL -->|Temporary failure / uncertain| OWED[Keep PAID/OWED; original bounded recovery, no blind refund]
    OBL -->|Verified irrecoverable merchant service failure| RF[Refund-first eligibility: exact paid evidence + safe printer/Drive fence + merchant provider capability]
    RF -->|Eligible and API verified| RFI[One original refund intent/key; REQUESTED/PROCESSING until provider confirmation]
    RF -->|Ambiguous / unsupported| REVIEW[Financial/technical review; preserve owed and audit]
    OBL -->|Yes| DONE[Completed: fence private UI + verified booth release]
    DONE --> ADS
~~~

**Read with Flow D/E:** verified expiry is *not* a request to cancel the customer's continuing checkout. VERIFIED CANCELLED / deliberate USER_CANCEL must not route back to QR2/QR3 even when the customer still stands at the booth. Advertising is a public screen, not a financial or worker release receipt. On PENDING/UNKNOWN, the loop represents bounded original-order reconciliation or hold, not an infinite immediate retry and not permission to create a new QR.

### Flow B: template capture, retake, preview and cart edit

~~~mermaid
flowchart TD
    START([Gallery selection confirmed]) --> D[Persist draft, template session IDs and copy quantities]
    D --> C[Capture-readiness and exclusive camera lease]
    C --> R{Ready?}
    R -->|No| H[Retry without order or photo duplication]
    H --> C
    R -->|Yes| SHOT[Deliberate SIAP -> 5s countdown -> capture intent -> atomic JPEG/manifest]
    SHOT --> COUNT{Three originals durable for this design?}
    COUNT -->|No| SHOT
    COUNT -->|Yes| REVIEW[Show exact three selected slots]
    REVIEW --> TAKE{Retake requested?}
    TAKE -->|Yes| Q{Retake not yet consumed?}
    Q -->|No| REVIEW
    Q -->|Yes| SEL[Persist pending slot and replacement capture]
    SEL --> COMMIT[Atomic retake commit; quota consumed forever on this design session]
    COMMIT --> REVIEW
    TAKE -->|No: approve| COMP[Compose private draft preview; no print/public QR]
    COMP --> VALID{Manifest and output checksum valid?}
    VALID -->|No| BLOCK[Hold/repair original files safely]
    VALID -->|Yes| MORE{Other selected designs?}
    MORE -->|Yes| SHOT
    MORE -->|No| FINAL[Final preview all designs]
    FINAL --> EDIT{Edit before QRIS?}
    EDIT -->|Copies / add / remove| REV[Increment draft revision; preserve existing retake ledger]
    REV --> D
    EDIT -->|Accept| FREEZE[Freeze immutable purchase snapshot]
~~~

**Retake anti-reset invariant:** a session's consumed retake is attached to immutable session lineage, not just a mutable gallery position. Deleting/reselecting the same template in the same logical visit does not create a free quota. A new template must take its own three originals.

### Flow C: two-stage readiness and frozen purchase

~~~mermaid
flowchart TD
    A([Before camera]) --> B[Check camera freshness, disk/fsync, templates/masks, private staging, worker]
    B --> C{All capture prerequisites valid?}
    C -->|No| D[Show actionable error; zero provider calls]
    C -->|Yes| E[Capture and final preview]
    E --> F[Validate 3 final images/template, one retake max, full manifests]
    F --> G[Freeze draft revision and exact preview artifacts]
    G --> H[Independent backend quote and frozen content hashes]
    H --> I{Cart/amount/media match?}
    I -->|No| D
    I -->|Yes| J[Fresh payment transport, printer route and Drive reservation/sharing capability]
    J --> K{Known unserviceable, Drive unreachable or no READY reserve?}
    K -->|Yes| L[Hold draft; no payable order; retry or safe cancel]
    K -->|No| M[Persist logical checkout and CCP verifier]
    M --> N[Create provider payment attempt; immutable order]
~~~

### Flow D: payment attempt ledger, cancellation intent and verified QR renewal

~~~mermaid
flowchart TD
    A([Approved frozen logical purchase, original CCP verifier]) --> B[Persist CREATE_PREPARED with immutable provider order ID and request fingerprint]
    B --> C[Create QRIS1 once; unverified idempotency header is NOT assumed]
    C --> D{Create outcome?}
    D -->|Response lost / 404 / unknown| R[GET/reconcile SAME original provider order; no replacement POST]
    D -->|Confirmed PENDING| P[Show exact pending QRIS and privately offer CCP]
    R --> V{Fresh original provider outcome?}
    V -->|UNKNOWN / not-found| HOLD[Protected bounded retry; no new charge or safe-release assumption]
    V -->|PENDING| P
    V -->|PAID| PAID[One exact original paid service entitlement]
    V -->|Verified EXPIRED unpaid| E[Archive original attempt with expiry evidence]
    V -->|Verified CANCELLED unpaid| CLOSE[Guarded closure: no renewal]
    P --> S{Fresh provider status or distinct visitor event?}
    S -->|PENDING, active visit| P
    S -->|UNKNOWN / lost status reply| R
    S -->|Provider verified PAID| PAID
    S -->|USER_CANCEL| CAN[Persist cancel_intent and fence photo/QR UI]
    S -->|Visitor abandoned after policy| ABAN[Persist abandoned_intent; no renewal]
    CAN --> CANCEL[Request cancel ORIGINAL provider order and reconcile]
    ABAN --> CANCEL
    CANCEL --> CRESULT{Fresh cancellation/settlement evidence?}
    CRESULT -->|UNKNOWN / pending| HOLD
    CRESULT -->|PAID| PAID
    CRESULT -->|Verified terminal unpaid| CLOSE[Safe original draft isolation and booth release protocol]
    S -->|Provider verified CANCELLED unpaid| CLOSE
    S -->|Provider verified EXPIRED unpaid| E
    E --> CAUSE{cancel_intent or abandoned_intent?}
    CAUSE -->|Yes| CLOSE
    CAUSE -->|No, verified expired| CONT{Same visitor actively requests continuation?}
    CONT -->|No| CLOSE
    CONT -->|Yes| IDX{Number of just-expired attempt?}
    IDX -->|1| TWO[Persist new QR2 identity before its first provider call]
    IDX -->|2| THREE[Persist new QR3 identity before its first provider call]
    IDX -->|3| CLOSE
    TWO --> CREATE2[Create QR2 and verify its own response, same frozen group]
    THREE --> CREATE3[Create QR3 and verify its own response, same frozen group]
    CREATE2 --> D2{QR2 response?}
    CREATE3 --> D3{QR3 response?}
    D2 -->|PENDING| P
    D3 -->|PENDING| P
    D2 -->|Unknown| R2[Reconcile own QR2 identity; do not recreate]
    D3 -->|Unknown| R3[Reconcile own QR3 identity; do not recreate]
    R2 --> V2{Fresh QR2 outcome?}
    R3 --> V3{Fresh QR3 outcome?}
    V2 -->|Pending| P
    V2 -->|PAID| PAID
    V2 -->|Verified expired unpaid| E
    V2 -->|Verified cancelled unpaid| CLOSE
    V2 -->|Unknown| HOLD
    V3 -->|Pending| P
    V3 -->|PAID| PAID
    V3 -->|Verified expired unpaid| E
    V3 -->|Verified cancelled unpaid| CLOSE
    V3 -->|Unknown| HOLD
    PAID --> OWNER[Check original customer lease; live -> ticket, absent -> PAID_UNCLAIMED]
~~~

**Critical provider constraint:** the internal attempt key is an application database identity; it is **not evidence that Legacy Midtrans \`POST /v2/charge\` honors any \`Idempotency-Key\` header**. Preserve the same request/order identity and reconcile on ambiguous creation, with provider-specific retry rules verified separately. In QR2/QR3 unknown-create cases, requery their *own* attempt and hold on unresolved uncertainty; the shorthand arrows back to S must not be implemented as assuming a usable QR. No repeated create due to 404, no unverified terminal close, no automatic refund. Simultaneous settlement on multiple attempt IDs remains a financial conflict with **one fulfillment entitlement maximum**.

**Distinct terminal causes:** \`EXPIRED\` with a willing live customer is eligible for a *new* QR attempt up to QR3; \`CANCELLED\`, explicit \`USER_CANCEL\`, or confirmed departure is ineligible regardless of whether the camera still detects a face.

### Flow E: four separate customer/lifecycle events, never one generic cancel

~~~mermaid
flowchart TD
    A([Visitor lifecycle event]) --> EVENT{Exact event type?}
    EVENT -->|USER_CANCEL| C[Persist deliberate cancel_intent; remove private QR/photo pixels]
    EVENT -->|APP_SUSPENDED / minimize| S[Immediately fence private pixels; preserve original active payment and work]
    EVENT -->|INACTIVITY_WARNING| W[Show warning only when genuinely inactive; active camera/worker exempt]
    EVENT -->|INACTIVITY_EXPIRED after warning| I[Durably classify phase and actual customer ownership]
    EVENT -->|VISIT_ABANDONED proven by policy| B[Persist abandoned_intent; stop automatic QR renewal]
    W --> L{User resumes?}
    L -->|Yes| RESUME[Continue EXACT original visit and quota]
    L -->|No, policy deadline| I
    S --> SRET{Same original customer safely resumes?}
    SRET -->|Yes| RESUME
    SRET -->|No / ownership lost| B
    I --> ICLASS{Financial/provider attempt exists?}
    C --> CLASS{Financial/provider attempt exists?}
    B --> CLASS
    ICLASS -->|No| N[Drain local camera/files, persist draft isolation]
    CLASS -->|No| N
    ICLASS -->|Yes| P[Original payment status/cancel intent reconciliation]
    CLASS -->|Yes| P
    P --> PSTATE{Authoritative original provider evidence?}
    PSTATE -->|PAID| OWED[PAID_UNCLAIMED / OWED, never public old printing]
    PSTATE -->|PENDING / UNKNOWN| HOLD[ADS_PROTECTED: same-order bounded retry; no new payable visitor]
    PSTATE -->|Verified terminal unpaid| N
    N --> F[Exact fence, worker quiescence, local receipt + backend ACK if required]
    F --> READY{Durably safe booth free?}
    READY -->|Yes| ADS[Advertising / new visitor eligible]
    READY -->|No| HOLD
    OWED --> PAIDISO[Retain entitlement and original proof; paid-safe isolate separately]
    PAIDISO --> READY
~~~

\`APP_SUSPENDED\` is a privacy event, **not** financial cancellation. \`INACTIVITY_EXPIRED\` only becomes abandonment under its own durable policy; active multi-template capture, five-second shutter countdown, a legitimate busy worker and provider \`UNKNOWN\` are not ordinary inactivity. Confirmed customer cancellation never re-enters QR renewal. Safe public Advertising and safe new-charge admission are separate outcomes.

### Flow F: late PAID, ownership and Checkout Claim Proof

~~~mermaid
sequenceDiagram
    participant A as Visitor A
    participant K as Kiosk
    participant M as Midtrans/backend
    participant B as Visitor B
    A->>K: Approve photos; start checkout
    K->>K: Persist frozen draft + logical group + CCP verifier
    K-->>A: QRIS and private CCP (save opportunity)
    A->>M: Initiates payment
    A-->>K: Walks away before settlement callback
    K->>K: Privacy lock, isolate old worker and hold original attempt
    M-->>K: Late VERIFIED PAID for A's original order
    K->>K: Preserve paid/owed, PAID_UNCLAIMED; no photo or ticket exposed
    B->>K: Begin new visit
    K->>K: Guarded release, lease and PAID/OWED archive check
    K-->>B: Only admit if free booth proven
    A->>K: Return with original CCP
    K->>M: Verify same original settled order
    K->>K: Verify token, amount, draft integrity, claim scope and booth ownership
    alt Booth free and all proofs valid
        K-->>A: Reacquire exact original entitlement, not new charge
        K->>K: Ticket and owed fulfillment per original ledgers
    else Booth busy
        K-->>A: WAIT/DEFER; never interrupt B
    else CCP missing, invalid or paid claim disputed
        K-->>A: Privacy-safe denial and approved financial/support remedy
    end
~~~

**CCP handoff requirement:** creating a token in the database does not mean the customer obtained it. Give a genuine, usable private chance to save an original claim proof when QRIS starts (clearly distinguish it visually and semantically from payment QRIS). Do not claim the customer forfeited recovery if the proof display/print never happened. This feature is an OWNER-APPROVED target; actual paper/screen payload/UI and expiry duration need security QA. A ticket on a shared public screen must never be redisplayed by a new visitor.

### Flow G: mandatory on-screen Recovery Ticket plus concurrent one-time printed ticket

~~~mermaid
flowchart TD
    A([Fresh independently verified PAID + exact paid draft]) --> AUTH{Customer authority still valid?}
    AUTH -->|Live original booth lease| L[Authorize first original ticket presentation; NO CCP re-scan]
    AUTH -->|Prior visit retired| C[Require original private CCP/ticket, fresh PAID and FREE booth]
    C --> VALID{Original claim valid and booth reacquired?}
    VALID -->|No / B active| H[PAID_UNCLAIMED / WAIT; keep secret private; no paper dispatch]
    VALID -->|Yes| L
    L --> B[Load same original ticket from protected escrow; never mint replacement]
    B --> PREV{Was first ticket presentation already completed?}
    PREV -->|Yes| EXIST[Do NOT auto-show/reprint on polling, reboot or stale callbacks; continue exact owed fulfillment]
    PREV -->|No; authorized initial opportunity| OPEN[Persist ticket presentation intent + original receipt job identity]
    OPEN --> SCREEN[UI TRACK: Always render SAME original QR and full code + SIMPAN warning]
    OPEN --> PRINT[PRINT TRACK: In parallel, enqueue exactly one original receipt with same token]
    SCREEN --> VISIBLE{Original customer still live and QR truly visible?}
    VISIBLE -->|No; lease/privacy lost| LOCK[Immediately wipe private pixels; retain original PAID/OWED and audit]
    VISIBLE -->|Yes| TIMER[Start 30 visible seconds; show NEXT / LANJUT]
    TIMER --> END{NEXT or countdown reached zero?}
    END -->|Yes| WIPE[Persist ticket offer/presentation; wipe QR and plaintext once]
    PRINT --> SENT{Original receipt transport state?}
    SENT -->|NOT_SENT: printer unavailable| NOSEND[Record no-send hardware reason; NO new ticket or repeated print]
    SENT -->|SENDING / timeout / UNCERTAIN| QUAR[Quarantine same print job; NO auto-reprint]
    SENT -->|SUBMITTED| SUB[Record submission; paper physically unproven]
    NOSEND --> WORKER[Printer lane must be safe before photo-strip transport]
    QUAR --> WORKER
    SUB --> WORKER
    WIPE --> GATE{UI private ticket dismissed AND original printer lane safely serialized?}
    WORKER --> GATE
    EXIST --> GATE
    GATE -->|No| HOLDWORKER[Keep original owed work and printer journal; do not replay]
    HOLDWORKER --> GATE
    GATE -->|Yes| NEXT[Verify customer Drive URL; then paid photo print and upload as allowed]
~~~

**Definition of concurrency:** display and receipt-print dispatch are *two effects of one verified-PAID initial presentation event*. Do not await printer readiness or acknowledgment before rendering; issue one persistent original print intent and queue the one job while the screen is visible. Physical paper ejection need not happen in the same millisecond as the first visible frame; the single printer worker serializes receipt and photo-strip bytes. UI countdown starts **only when original QR and full code are actually visible** and runs independently of receipt status. Printer `SUBMITTED` does not suppress the screen; printer offline/failed/UNCERTAIN does not cause a second screen or reprint. An early NEXT or timeout retires private pixels but does not cancel/replay an in-flight print; photo-strip printer transport waits for safe same-worker ordering, and any uncertain transport keeps its own obligation/evidence. If the live owner is lost before showing the QR, do not expose/print to B; retain PAID_UNCLAIMED/OWED for original secure claim. A RETURNING verified claimant receives a first lawful presentation **only if never previously presented**; an already presented original ticket is not automatically shown again. One presentation opportunity does not prove physical paper was received.

### Flow H: Drive availability and print-with-real-QR policy

~~~mermaid
flowchart TD
    A([Fresh PAID and valid customer ownership]) --> B[Bind exact draft to one original paid order]
    B --> C{Verified individual customer Drive folder URL?}
    C -->|No| D[Retry verified folder binding with bounded policy]
    D --> E{Link now confirmed?}
    E -->|No| F[Keep paid media private, PAID/OWED and ticket claim; no false print]
    E -->|Yes| G[Freeze final strip with exact photo trio plus valid QR]
    C -->|Yes| G
    G --> H[Reserve per-design paid print jobs; exact copies/digest]
    H --> I[Shared printer single owner; ticket/photo sequencing]
    I --> J[Record SENDING before transport]
    J --> K{Outcome}
    K -->|SUBMITTED| L[Record transport submission, not physical paper proof]
    K -->|Failed/UNCERTAIN| M[Quarantine job; never auto-reprint]
    L --> N[Background upload exact paid files with checksum/retention guards]
    N --> O{Upload verified?}
    O -->|No/offline| P[Same verified folder link, truthful pending notice; retry original upload]
    O -->|Yes| Q[Record verified upload]
    P --> R[Preserve remaining delivery obligations]
    Q --> R
    M --> R
~~~

No raw photo/preview output is publicly available before PAID. The verified folder link itself may exist earlier as an unclaimed READY reserve, but no customer media may be shared, uploaded into a public location, or customer download QR disclosed before verified payment. Do not consume the 25 READY Drive slots merely for anonymous unpaid draft attempts. When Drive API/sharing is known unavailable or no READY reserve can be found at charge-readiness, hold checkout before QRIS; **a customer-specific link is not expected until paid binding**. If exact binding or URL verification fails after PAID, preserve owed service and no guaranteed finish time. The stable resolver QR is future optional infrastructure, **not** an implicit fallback.

### Flow I: returning customer and legacy compatibility

~~~mermaid
flowchart TD
    A([Advertising: original ticket or checkout claim]) --> B[Type-specific validation, rate-limit, original order/booth]
    B --> C{Authentic proof?}
    C -->|No| DENY[No private media; retain possible financial support claim]
    C -->|Yes| D[Fresh authoritative settlement and original entitlement]
    D --> E{PAID with valid rights?}
    E -->|No/unknown| HOLD[Hold original order and reconcile/review]
    E -->|Yes| F{Booth occupied by another visitor?}
    F -->|Yes| WAIT[WAIT/DEFER; no camera takeover]
    F -->|No| G[Acquire exact original fenced owner]
    G --> H{Order flow version}
    H -->|Legacy prepaid| CAP[Restore exact capture/retake checkpoint; manual SIAP]
    H -->|Post-preview paid| PRINT[Restore existing immutable preview and owed print/Drive work]
    PRINT --> CHECK{Print job uncertain?}
    CHECK -->|Yes| INSPECT[Physical evidence; no auto replay]
    CHECK -->|No| CONTINUE[Resume only authorized unfulfilled work]
    CAP --> CONTINUE
~~~

### Flow J: crash recovery and safe admission are independent from public Advertising

~~~mermaid
flowchart TD
    A([App boot / restart]) --> B[Acquire exclusive process, booth and worker fencing]
    B --> C{Conflicting owner or unsafe lease?}
    C -->|Yes| HOLD[STARTUP_HOLD / ADS_PROTECTED; no new charge]
    C -->|No| D[Hide all previous private media, retire stale callbacks]
    D --> E[Read ALL durable photo, provider, fulfillment, ticket, upload and release journals]
    E --> CLASS{Authoritative financial state?}
    CLASS -->|Unpaid, no attempt ever created| U[Quiesce photo writes, preserve retake audit and isolate private draft]
    CLASS -->|CREATE_UNKNOWN / PENDING / UNKNOWN| P[Reconcile SAME original provider attempt]
    P --> Q{Fresh provider result?}
    Q -->|Pending / unknown| HOLD
    Q -->|Verified terminal unpaid| U
    Q -->|Verified PAID| PAID[Preserve original PAID/OWED, require rightful customer claim]
    CLASS -->|Verified PAID / OWED| PAID
    PAID --> FUL[Classify ALL paid print, receipt and upload obligations independently]
    FUL --> PRINT{Any print job SENDING / UNCERTAIN?}
    PRINT -->|Yes| QUAR[Quarantine exact job; never automatically reprint]
    PRINT -->|No| UP{Authorized original Drive upload pending?}
    QUAR --> UP
    UP -->|Yes| RES[Resume only idempotent checksum-verified upload under separated worker lease]
    UP -->|No| REL[Assess protected paid release; OWED remains durable]
    RES --> REL
    REL --> CLAIM{Original customer proof/lease for private continuation?}
    CLAIM -->|Yes, free booth| REST[Reacquire original scoped rights, no charge/reissue]
    CLAIM -->|No / new customer awaiting| ISOP[Attempt PAID/OWED safe machine release with original PREPARE/ACK]
    U --> ISOU[Exact local worker quiescence, ownership fence and typed receipt/ACK]
    ISOU --> G{Durably FREE and no unsafe worker?}
    ISOP --> G
    G -->|Yes| ADS[Public Advertising and new-visitor admission]
    G -->|No| HOLD
    REST --> PRIV[Original private continuation only, never shown on public Ads]
~~~

**Crash-safe release rule:** a provider terminal status is insufficient without exact worker fencing and release acknowledgment. A pending paid Drive upload is not permission to print again, to mark OWED complete, or to admit a visitor before the worker can be separated safely. The public Advertising screen may be shown with protected occupancy, but new camera/charge admission waits for verified FREE. An original customer with CCP who returns while visitor B owns the booth must WAIT and never preempt B.

### Flow K: original Meong Fly into this checkout

~~~mermaid
flowchart TD
    A([Advertising Meong Fly entry]) --> B[Validate correct DEMO/merchant receipt type and one-use identity]
    B --> C{Valid and not consumed?}
    C -->|No| EXIT[Reject/return safely]
    C -->|Yes| D[Persist attempt consumption; original Meong Fly game]
    D --> E{Win or lose?}
    E -->|Win| W[Record proposed 2500 IDR discount candidate]
    E -->|Lose| L[No discount]
    W --> F[Tutorial and same gallery/capture/final preview]
    L --> F
    F --> G{Trusted backend promotion contract available?}
    G -->|No: Sandbox DEMO| FULL[No provider discount; unmodified full-price quote]
    G -->|Yes: separately approved| DISC[Verify reward only once server-side; prevent stacking]
    FULL --> QR[Post-preview frozen checkout and QRIS]
    DISC --> QR
    QR --> H[Game attempt remains consumed on abandonment; **no refund solely for loss/abandonment**. Separately verified merchant PAID-service failure follows full-order refund-first policy]
~~~

## 3. Critical failure decisions and risk register

| Critical point | Threat / failure window | Required protection | Reference acceptance |
| --- | --- | --- | --- |
| K01 Booth ownership | A's draft frame shown to B | Local privacy fence, worker drain, versioned lease/ACK before admitting B | PP-HAND, PP-CRASH |
| K02 Capture durability | crash after 1/2/3 captures or pending retake | Atomic intent/manifest, no duplicate shots, consumed retake lineage | PP-CAP |
| K03 Final preview mutation | cart/copies/photos no longer match price | Frozen revision, exact outputs/assets, server quote, revalidate on resume | PP-FRZ |
| K04 Charge-readiness | sell unserviceable print or unreachable Drive | Two-stage preflight; late hardware failure retains paid owed | PP-READY |
| K05 QR provider uncertainty | duplicate order/charge on timeout/404 | Same original attempt, verification, idempotency journal | PP-PAY |
| K06 QR renewal | delete drafts while old provider settles | Terminal unpaid + active owner + max QR3, same frozen draft | PP-QR |
| K07 CCP late paid | A gone/B present; unauthorized prints | Non-disclosing private claim, PAID_UNCLAIMED, WAIT if busy | PP-CLAIM |
| K08 Ticket escrow | restart after PAID before handoff | Confidential encrypted single credential + gated retrieval | PP-SEC |
| K09 Receipt/photo print | partial paper, print SENDING crash, or onscreen UI accidentally skipped after SUBMITTED | Always show original post-PAID ticket while one receipt is dispatched; exact job journal, single printer, UNCERTAIN no replay | PP-PRINT, PP-SEC |
| K10 Drive QR | free download or false QR link | Authenticated paid-only publication; verified URL, held print otherwise | PP-DRIVE |
| K11 Fulfillment owed | COMPOSED incorrectly treated as COMPLETED | Separate paid obligation ledger per design/copies and delivery | PP-PRINT, PP-DRIVE |
| K12 Reboot/fencing | stale callback alters next session | Generation+lease checks, protected startup, exact journal restore | PP-CRASH |
| K13 Game promo | discount forgery/attempt reset | Server authority, one-use ledger, no production DEMO | PP-GAME |
| K14 Excessive free use | repeated unpaid captures, storage exhaustion | Adaptive inactivity, rate/resource metrics; no hard cutoff on active work | PP-ABUSE |
| K15 Lost ticket/proof | customer has no original credential | **NO_AUTO_REFUND solely for lost genuinely offered proof** and never media without proof. Proof never offered or independent service failure -> PAID/OWED + authorized remedy; record offer evidence | PP-SEC, PP-CLAIM |

## 4. Owner-approved product choices versus engineering parameters not yet calibrated

**Approved product policy:** CCP before PAID; Recovery Ticket after PAID; protected escrow; verified URL before final paid-strip printing; adaptive inactivity (no active hard cap); editing only before first QRIS attempt; existing retake 3+1/template and QR1/2/3 actively-owned rule; owner proof, fencing and privacy remain mandatory.

**Engineering parameters still to design/test (NOT an invitation to contradict policy):**
- Countdown and warning thresholds per gallery/capture/review/final preview; suggestions for pilot include gallery 60–90s, capture/review 120s and final preview 90–120s *of genuine inactivity*, not total active time.
- Provider polling, backoff, QR expiry as supplied by current provider, cancellation verification deadlines and post-abandonment occupancy threshold.
- How a customer actually saves CCP at checkout without confused identity with QRIS; private screen layout/receipt capability, accessibility, and proof-of-offer evidence.
- CCP token expiry/rotation/replay rules and escrow key selection/provisioning/backup/retirement (Windows DPAPI, Android Keystore, Ubuntu TPM/secret service subject to real deployment capability). No plaintext sidecar key.
- Paid wait threshold when Drive URL or printer cannot be made ready, user-facing claims, service remedy/financial role and actual external service-level promises.
- Printer physical proof granularity for multiple copies and exact spool/USB/LAN delivery; calibration on POS80 and actual OS.
- Commercial print maximum, QR expiry/consumer remedy policy, eventual stable resolver, cross-device recovery and production-specific support/privacy obligations.
- Any measured abuse mitigation beyond adaptive inactivity. Hard cutoffs, user identity tracking, biometric recognition or device-facing abuse controls are NOT owner-approved.

### Implementation-critical ordering and normative conflicts resolved

- **Cancel vs expiry:** persist \`USER_CANCEL\` (and separately \`VISIT_ABANDONED\`) before reconciling the original provider attempt. Neither enters QR renewal. QR1→QR2→QR3 is for a willing, actively continuing original customer after a separately *verified expired unpaid* attempt.
- **UI privacy vs occupancy:** minimize, screen timeout and Advertising can hide pixels without cancelling the payment or releasing a booth. **Only** exact worker fence + safe original financial classification + durable isolation/ACK authorize a new visitor.
- **Drive READY pool:** before QRIS, preflight only checks authenticated Drive readiness, sharing capability and unclaimed READY capacity; it does not require a customer-specific verified URL or consume a folder. A paid transaction later atomically binds an original folder and re-verifies exact identity/URL. If that post-paid binding fails, keep PAID/OWED and withhold purchased-strip printing. Unpaid draft must not exhaust the 25 READY reserves.
- **Provider idempotency:** internal checkout keys and persisted immutable provider order identity are mandatory; a Legacy Midtrans Core /v2/charge idempotency header remains **UNVERIFIED** and may not be assumed.
- **Ticket (revised owner policy):** live paid owner does not scan CCP. On every newly verified PAID initial ticket opportunity, the original Recovery Ticket screen **always appears for 30 actually visible seconds with NEXT** while the same ticket's **one print dispatch starts concurrently**; transport SUBMITTED does not skip the screen. A returning original owner needs proof and a FREE booth; receipt SENDING/UNCERTAIN never gets blind replay and a completed original presentation never resets on polling/restart. Track paper transport and customer presentation independently.
- **Timestamps:** retain distinct \`draft_created_at\`, \`payment_attempt_created_at\`, \`paid_verified_at\`, \`ticket_created_at\`, \`proof_offered_at\`, \`claim_expiry_at\`, \`transaction_retention_anchor_at\`, \`last_worker_barrier_at\`, and \`completed_at\`. Existing 24h Sandbox ticket expiry measured from original order creation applies to **legacy** orders; new post-preview expiry/CCP TTL and 15d local/30d Drive retention anchor must be explicitly versioned and verified in PP tests before shipping. **Proposal for future owner validation:** anchor paid photo retention at first genuine paid entitlement, separate unpaid staging TTL, no extension on QR renewal or restart. Do not silently adopt this proposal as a signed-off product value.
- **Target profile:** legacy dedicated Sandbox intentionally keeps Drive OFF while allowing its historically verified receipt/photo printing. Post-preview purchased-flow fixtures require a **separate isolated synthetic verified-URL adapter**, with no real Drive access, and must not be described as live cloud delivery or production print acceptance.

### Ticket presentation correction — explicitly approved

This section supersedes any *printer failure -> screen only* or *SUBMITTED -> skip screen* instructions for **new post-preview orders** appearing in older UAH, receipt fallback, decision summaries, QA plans, or historical source descriptions. For an authorized live freshly-PAID customer, **screen ALWAYS + concurrent one-time paper submission**, same credential. Keep the initial 30-second screen and NEXT; printer failure affects the print lane only. The old dedicated paid-first Sandbox and historical UAH pass/fail/NOT_RUN evidence are not retroactively changed. This owner correction is **design only** until explicitly implemented/tested; the real UI, physical POS80 send and two-track race tests must be verified separately.

### New refund-first policy and evidence hierarchy — binding new-order addendum

**The owner's latest request is to avoid calling an operator just to reimburse a customer for a truly failed paid service.** For **new** orders, keep a safe `REFUND_ELIGIBLE` review gate after fresh verified PAID, bounded original recovery, exact paid photo obligations, worker-safe printer/Drive fencing and merchant-specific Refund API activation. A safe irrecoverable original service may receive an automatic full merchant refund; a second independently proven duplicate-settled attempt may receive a refund of that excess only. This is **not** permission to refund on UI ERROR, timeout, print `UNCERTAIN`, unknown provider status, unverified merchant support, or every physically partial output. Refund accepted/processing/confirmed are distinct; never imply the money is already visible on the customer's payment instrument. Technician may still be needed to repair an unsafe kiosk, independent of financial outcome.

**Customer lost-proof rule:** Meong genuinely offered the pre-PAID CCP and, upon lawful live PAID, **always showed original Recovery Ticket QR/full code for 30 visible seconds + NEXT while sending the same ticket to printer once**. If customer later lost these proofs, **no automatic refund solely due to proof loss**, no operator shortcut to photos, no reissued secret. This does NOT make Meong's own verified paid-service failures go away, does NOT turn a printer SUBMITTED into proof paper delivered, and is not a legal blanket forfeiture of consumer money. If actual claim/ticket was never offered, keep `PAID/OWED` and a legitimate remedy. Indonesian consumer-protection and merchant-specific provider policy require formal validation before public terms.

Canonical detail: [RF-D01–RF-D26 refund/lost-proof](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) · [complete all-decisions crosswalk](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md). **No actual refund implemented or executed.**

## 5. Scope exclusions, audit and go/no-go

- **No code changes authorized by this documentation request.** The future implementation must reuse existing `photobooth/kiosk_v2/photos.py` and `photo_views.py`, `sandbox_views.py`, `qris_session.py`, `checkout_backend.py`, `checkout_store.py`, `checkout_release.py`, `delivery_requirements.py`, original printer, Drive, local manifest, worker and AR/UAH primitives; create only minimal versioned adapters where required.
- **Do not change existing legacy PAID capture data** or claim older passing tests prove the new route. No new branch or master merge in this documentation change.
- **No original private ticket, CCP, sensitive user photo, provider secret, encryption key or synthetic-but-redeemable proof** goes into source control, printed docs or test artifacts; testing uses controlled nonredeemable fixtures.
- **Production remains NOT READY:** AR-13, merchant/provider/QRIS official evidence, physical Windows/Ubuntu POS80, tablet/Android, real privacy/Drive upload/deletion, escrow security and customer/support remedies require separate release gates.
- **Documentation definition of done** is this spec plus companion state/test/Codex plan and addenda in old navigation docs. Software tests/new PP acceptance all **NOT_RUN** until separately authorized and executed. Do not mark old CI/device evidence as proof of POSTPAY.
