# Post-preview QRIS checkout — owner-approved product contract

**Date:** 1 November 2026 (Asia/Jakarta)  
**Target branch:** `feature/post-preview-qris-checkout` (branched from `feature/portrait-kiosk-v2-next` at `97a6c1574f0692d8a3db8b3a4d94778f87937e18`).  
**Status:** **OWNER-APPROVED DESIGN / DOCUMENTATION ONLY / NOT IMPLEMENTED / NOT TESTED**. This document authorizes a detailed documentation baseline, **not** a source-code, API, schema, test, payment, OS-vault, production, hardware, cloud, default-branch or master change.  
**Companions:** [security and state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [acceptance matrix](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) · [Codex handover](POST-PREVIEW-QRIS-CODEX-HANDOVER.md).

> **Branch-specific precedence.** For **new post-preview orders**, this owner approval supersedes the **payment-before-capture ordering** in earlier GUI v2/Sandbox, BUG-026/027/028, AR and unattended-handoff diagrams; **it does not supersede their safety properties**. Existing prepaid customer orders and in-flight legacy PAID -> camera recovery MUST keep their original versioned fulfillment route. Earlier documented CI PASS, on-device reports and historical proofs remain valid only for the old source/flow. Existing AR-00–AR-13/UAH no-double-charge, privacy/fencing, paid/owed, strict provider evidence, no uncertain reprint, retention and operator-last-resort protections stay mandatory. Existing measured production readiness remains CONDITIONAL / NOT APPROVED.

## 1. Owner decision register — final product policy (PP-D01–PP-D24)

| ID | Owner-approved decision | Required clarification / boundary |
| --- | --- | --- |
| PP-D01 | New commercial route: **Gallery -> capture and review all selected designs -> final preview -> one QRIS checkout -> verified PAID -> original Recovery Ticket -> print/Drive fulfillment**. | No paid photo capture before checkout on the new route; no free photo output or public link before verified settlement. |
| PP-D02 | **Exactly 3 initial captures per selected template**, **maximum 1 retake of one slot PER TEMPLATE**. | New template gets its own session; print copy quantities never multiply capture count. Do not pool quotas, erase a used quota by deselect/reselect, or recapture on QR renewal. |
| PP-D03 | One logical cart and total payment for every selected template/copy. | One frozen logical purchase, one legitimate paid fulfillment entitlement; QR replacements are individually journaled provider attempts, not extra purchases. |
| PP-D04 | **Secure Checkout Claim Proof (CCP)** is privately offered **when payable checkout begins, before PAID**. | Random high-entropy original claim capability, bound to booth/logical purchase/frozen draft; hashed verifier, versioned/expiring/rate-limited; never an ordinary order number, QRIS payload, DEMO/operator QR, Recovery Ticket, or proof that money was paid. |
| PP-D05 | CCP enables returning customers to claim **late-settled PAID** orders unattended after fresh independent payment/ownership checks. | Claims do not open unpaid photos; busy booth -> WAIT/DEFER, never preempt; missing customer proof never authorizes private-photo disclosure. |
| PP-D06 | Keep the **separate original Recovery Ticket** after freshly verified PAID, printed once in the ordinary live path. | If unconfigured/failed/timed out/UNCERTAIN, display the same original QR and FULL code for 30 visible seconds + NEXT; no duplicate ticket issuance, no replay of uncertain receipt. Owner responsibility to save only follows a genuine opportunity. |
| PP-D07 | Use **encrypted credential escrow** for crash survivability, with strict access controls and least-privilege redemption. | Do not save plaintext secrets/QR bitmaps in SQLite, journals, logs, screenshots, clipboard, Git or telemetry. An encrypted vault is a narrow exception to historical memory-only rules; it is NOT permission to reveal tickets on reboot or to duplicate prints. |
| PP-D08 | **MVP printing waits for a verified customer download URL**; then final strip has 3 photos + 1 real QR. | Valid verified folder URL may precede upload completion; pending upload can continue in background. No invented QR or exposed public media before PAID. No unbounded paid wait: persist PAID/OWED and provide safe recovery/support path. |
| PP-D09 | Preserve the old **offline local capture** capability. | When internet/Drive link is not ready at charge-readiness, do not knowingly create a payable order. Once PAID, hold printed delivery until QR URL verification; this narrowly changes old immediate-offline-print expectations for the new purchased route. |
| PP-D10 | A future **stable Meong resolver QR** is the preferred follow-on architecture, **not part of MVP**. | No speculative hostname, public resolver, hosting, payment bypass or redirect service may be shipped under this design-only approval. |
| PP-D11 | **Adaptive inactivity timeout** by current phase; no hard cutoff that interrupts an actively capturing multi-template customer. | Camera work/countdown, legitimate busy worker and payment uncertainty are not ordinary UI inactivity. Numeric pilot values are configurable recommendations to validate, not signed-off constants. |
| PP-D12 | **Edits allowed only before creating the first QRIS attempt**, preserving consumed retake quotas and draft ancestry. | Copy-count changes re-quote; newly added template needs its own 3 captures; changing/deselecting/reselecting the same template cannot reset retake. QRIS creation freezes cart, draft revision, promotions, artifacts and amount. |
| PP-D13 | Maintain current **QR1 -> QR2 -> QR3 -> Advertising**, maximum three verified unpaid expirations for an **actively continuing customer**. | Replacement must use the same immutable logical draft and amount, new attempt ID, original status checked, previous safely terminal unpaid; third expires -> safeguarded isolation. No QR4; never renew for an abandoned visitor. |
| PP-D14 | For **abandonment during PENDING/UNKNOWN**, use same-order cancel/reconciliation and safe occupancy isolation, not automatic QR renewal. | Browser timeout, QR countdown, HTTP 404 or old cached UNPAID never equal terminal financial proof. |
| PP-D15 | Customer data stays private in **unpaid draft local staging** before payment. | No customer-facing Drive upload/share/download QR, paid photo print or accidental background auto-print; QRIS payment-slip printing is distinct and allowed only through its own guarded pending-order path if separately implemented. |
| PP-D16 | Preview composition may complete before payment, but **service fulfillment must not**. | `DRAFT_READY` ≠ `PAID` ≠ `FULFILLED`. Final printed strip may replace a prepay QR placeholder with the real paid-only QR, while final three photos/layout/design/copy requirement remain matched. |
| PP-D17 | Before capture check camera/disk/templates/local staging; **before QRIS** verify frozen outputs, local durability, printer-route readiness, payment connectivity, and delivery-URL policy. | Route observation ≠ paper detection; after settlement physical delivery can still fail and needs PAID/OWED recovery. Existing Sandbox trial and purchased-print roles remain distinct. |
| PP-D18 | Automatic session isolation only with proven fence/worker quiescence/backend release or safe local draft closure. | Prior PAID/OWED remains auditable. Protected Advertising is only a public UI, not authority to admit a new charge or show prior media. Operator only for unsafe/ambiguous financial, hardware, security or corrupt-data cases. |
| PP-D19 | One immutable draft-to-paid binding and one entitlement per logical purchase across all QR attempts. | Detect and HOLD multiple settled attempts/amount mismatches; never double-fulfill, silently treat extra payment as a free service or refund automatically. |
| PP-D20 | Purchase printing uses durable job reservations with exact design/output/copies, one printer owner and no uncertain replay. | `SENDING`/`UNCERTAIN` are NOT paper-success evidence; partial print requires separately approved physical inspection/remedy. Printed Recovery Ticket and purchased photo jobs have independent identities, same printer exclusivity. |
| PP-D21 | Google Drive must be gated on authenticated PAID entitlement and exact folder identity. | Use existing `Photobooth/PB001/Photo/00000001/{raw,bw,color}` contract; 25 READY reserves aren't consumed by arbitrary unpaid visitors. Verify anyone-reader link for the right individual customer folder only and use retention guards. |
| PP-D22 | Existing Meong Fly one-use ticket and single-game-attempt ledger remain authoritative. | Unpaid checkout abandonment cannot reset the game or discount. Sandbox reward remains demonstrative/full-price unless a **trusted backend promotion** contract exists. No stacking without separate approval. |
| PP-D23 | Historical prepaid legacy orders remain on their original **PAID -> photo** recovery semantics, versioned separately. | No forced conversion of old paid grants/manifests/print jobs into unpaid drafts. |
| PP-D24 | No automatic refund, production gateway activation, Android rollout, public webhook, customer-data deletion, branch merge or master/default change in this documentation delivery. | AR-13 commercial gates and real Windows/Ubuntu/POS80/provider/cloud/security acceptance remain open. |

### Policy precedence and explicit supersessions

1. **Only on this dedicated branch/new version** the payment-before-camera ordering, paid-camera photo admission as the sole possible route, and mandatory ticket-before-camera diagram are superseded. **Safety guards are preserved and adapted, not bypassed.**
2. Historical BUG-026 automatic QR1/2/3 applies while the **same original checkout remains actively owned**. Abandonment instead requests guarded original-attempt cancellation/reconciliation; no silent renewal for absent customers.
3. Existing original ticket once-after-PAID plus 30s fallback remains approved. On the **new route**, the handoff after ticket is **fulfillment/printing**, not original camera admission; on legacy prepaid orders ticket continues to precede camera.
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
7. Fresh PAID with original live customer -> exact paid draft binding -> original Recovery Ticket printed once; if unavailable/failed/UNCERTAIN show same QR/full code 30s + NEXT; no mandatory ticket-save screen on paper-submitted happy path. Ticket-only print can occur before final Drive URL; final photo strip cannot.
8. Link/folder verified -> final original three-photo strip with genuine link QR -> durable paid photo print job(s) -> background upload and download presentation. Truthfully label pending uploads.
9. Fulfillment/printing unknown -> preserve obligations, private claim and safe machine isolation; no duplicate print. Completed/archived -> wipe private UI before Advertising.

### Flow A: end-to-end happy path and protected entry

~~~mermaid
flowchart TD
    BOOT([Advertising / original kiosk ownership]) --> OCC{Protected prior occupancy?}
    OCC -->|No| ENTRY[New visitor admitted]
    OCC -->|Yes| ISO[Original financial and worker classification]
    ISO --> SAFE{Safe fence and isolation proven?}
    SAFE -->|No| HOLD[Neutral HOLD; original retry/support]
    SAFE -->|Yes| ACK[Local receipt + backend ACK + durable archive]
    ACK --> ENTRY
    ENTRY --> ROUTE{Photo or Meong Fly?}
    ROUTE -->|Game| GAME[One-use ticket -> game result -> tutorial]
    ROUTE -->|Photo| TUT[Tutorial if not seen]
    GAME --> GALLERY[Choose designs and print quantities]
    TUT --> GALLERY
    GALLERY --> PREF[Camera/disk/artwork and staging readiness]
    PREF --> READY{Ready?}
    READY -->|No| RETRY[Retry or safe cancel; no payment]
    RETRY --> PREF
    READY -->|Yes| DRAFT[Create private unpaid draft and exact identities]
    DRAFT --> CAP[Each design: 3 captures, max 1 retake, review]
    CAP --> MORE{More designs?}
    MORE -->|Yes| CAP
    MORE -->|No| FINAL[All-design final preview and optional edit]
    FINAL --> FREEZE[Freeze revision, outputs, copies, price]
    FREEZE --> CHK[Charge readiness incl verified-link policy]
    CHK --> OK{Ready?}
    OK -->|No| PAUSE[Keep draft; no charge; retry]
    PAUSE --> CHK
    OK -->|Yes| CCP[Create payment-group proof + QRIS1]
    CCP --> PAY[Provider reconciliation and guarded renewals]
    PAY --> STATUS{Fresh verified state?}
    STATUS -->|Pending/unknown| PAY
    STATUS -->|Terminal unpaid| EXIT[Safe protected isolation/Advertising]
    STATUS -->|PAID| OWNER{Original visitor owns booth?}
    OWNER -->|No| UNCLAIM[PAID_UNCLAIMED: no public print; claim from ads]
    OWNER -->|Yes| TICKET[One Recovery Ticket receipt / 30s fallback]
    TICKET --> DELIVERY[Verify URL; exact photo jobs + upload]
    DELIVERY --> OBL{All required obligations resolved?}
    OBL -->|No| OWED[Preserve PAID/OWED; recovery and operator-last-resort]
    OBL -->|Yes| DONE[Complete / hide private UI / Advertising]
~~~

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
    I -->|Yes| J[Fresh payment transport, printer readiness and Drive URL policy]
    J --> K{Known-unserviceable or unverified link?}
    K -->|Yes| L[Hold draft; no payable order; retry or safe cancel]
    K -->|No| M[Persist logical checkout and CCP verifier]
    M --> N[Create provider payment attempt; immutable order]
~~~

### Flow D: QR1/2/3 attempts, ambiguous statuses and customer abandonment

~~~mermaid
flowchart TD
    A([Frozen logical purchase + original CCP]) --> B[Persist attempt/key before provider I/O]
    B --> C[Create original provider QRIS attempt]
    C --> D{Provider create reply?}
    D -->|Unknown/lost| R[Same-attempt GET reconciliation; bounded backoff]
    D -->|Valid pending| P[Show same pending QR, quote, expiry, private CCP]
    P --> S{Fresh provider status / customer action}
    S -->|PENDING active visitor| P
    S -->|404/outage/UNKNOWN| R
    S -->|PAID| Z[Exactly one paid entitlement, never second capture]
    S -->|Cancel/inactive| CANCEL[Request original cancel and reconcile]
    CANCEL --> R
    R --> V{Verified provider result?}
    V -->|PAID| Z
    V -->|Unknown| BLOCK[HOLD payment identity; never new charge]
    V -->|Pending| P
    V -->|Terminal unpaid| E[Archive exact old attempt; retain frozen draft]
    S -->|Verified EXPIRED unpaid| E
    E --> ACTIVE{Original visitor still active and requested continuation?}
    ACTIVE -->|No| ISO[Safe unpaid isolation; no renewal]
    ACTIVE -->|Yes| CNT{Attempt number}
    CNT -->|1| TWO[Create QR2 with new key, same purchase, no recapture]
    CNT -->|2| THREE[Create QR3 with new key, same purchase, no recapture]
    CNT -->|3| ISO
    TWO --> P
    THREE --> P
    Z --> OWNER[Check ownership + original entitlement]
~~~

The QR2/QR3 provider create stage must explicitly persist its **own** new attempt ID before provider I/O; diagram arrows to P abbreviate that verified create/receive step. If multiple attempts settle due to a provider race, quarantine excess financial settlement; do not print twice, auto-refund, misattribute photos or ignore liability. Server provider integration details, timeouts and cancellation claims must be verified against the configured Midtrans contract, not invented.

### Flow E: abandoned draft, payment uncertainty and privacy

~~~mermaid
flowchart TD
    A([Inactivity, cancel, minimize, departure]) --> B[Cancel camera timer, fence callbacks, remove private pixels]
    B --> C{Durable stage?}
    C -->|No provider attempt| D[Finish private file writes; isolate unpaid draft safely]
    D --> E[Free camera after exact worker/barrier receipt]
    E --> F[Advertising; TTL cleanup per approved policy]
    C -->|Provider PENDING/UNKNOWN| G[Stop customer renewal; exact-provider cancel/reconciliation]
    G --> H{Terminal unpaid proven?}
    H -->|Yes| I[Archive attempt; protect draft; safely release]
    I --> F
    H -->|No| J[ADS_PROTECTED / neutral hold; preserve payment identity]
    H -->|Late PAID| K[PAID_UNCLAIMED: preserve OWED; no unattended print]
    C -->|Verified PAID| K
    K --> L[Original CCP claim or authorized non-media remedy]
    J --> M[Bounded same-operation retry / support if truly unsafe]
~~~

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

### Flow G: original Recovery Ticket, escrow and crash

~~~mermaid
flowchart TD
    A([Fresh PAID and valid current customer claim]) --> B[Original durable paid binding and one entitlement]
    B --> C[Open protected credential lifecycle; original secret, hash and encrypted escrow]
    C --> D{Ticket receipt job ever sent or uncertain?}
    D -->|No| E[Persist one receipt SENDING intent, then one printer submission]
    E --> F{Submission result}
    F -->|SUBMITTED| G[No mandatory ticket page; paper not proven]
    F -->|Fail/timeout/UNCERTAIN| H[No reprint; show SAME original ticket if live owner]
    D -->|Yes/uncertain| H
    H --> I{Live original customer and secure credential available?}
    I -->|Yes| J[30 visible seconds original QR + full code + NEXT]
    J --> K[Wipe ticket pixels; advance exactly once]
    I -->|No| L[PAID_UNCLAIMED; claim via original CCP, no public exposure]
    G --> M[Paid fulfillment URL/readiness]
    K --> M
    L --> N[On authentic customer claim, vault access is gated; no auto ticket reveal at boot]
~~~

**Crash window:** boot after PAID but before original ticket presentation must preserve OWED and encrypted original credential. Boot itself may NOT decrypt, display or print to the next visitor. An original customer proves CCP or an already-valid Recovery Ticket; only then may scoped vault access occur. Any receipt `SENDING`/`UNCERTAIN` stays non-replayable. A vault failure does not mean unpaid/fulfilled; it is a recorded remediation exception.

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

No raw photo/preview output is publicly available before PAID. The verified folder link itself may exist earlier as an unclaimed READY reserve, but no customer media may be shared, uploaded into a public location, or customer download QR disclosed before verified payment. Do not consume the 25 READY Drive slots merely for anonymous unpaid draft attempts. When verified URL is unavailable at charge-readiness, hold checkout before creating QRIS; when unexpectedly unavailable after PAID, preserve owed service and no guaranteed finish time. The stable resolver QR is future optional infrastructure, **not** an implicit fallback.

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

### Flow J: boot/restart and one-owner worker safety

~~~mermaid
flowchart TD
    A([Process boot or crash restart]) --> B[Acquire exclusive kiosk/worker lease]
    B --> C{Lease conflicting?}
    C -->|Yes| BLOCK[STARTUP_HOLD / no second worker]
    C -->|No| D[Read same original durable journals and manifests]
    D --> E[Hide private pixels by default, fence old callbacks]
    E --> F{Last verified durable state?}
    F -->|Unpaid draft; never payment| G[Quiesce and safe suspend/local isolate]
    G --> ADS[Public Advertising only after safe verified occupancy]
    F -->|Creating/PENDING/UNKNOWN| H[Same-attempt provider reconciliation; no new create]
    H --> I{Fresh terminal unpaid?}
    I -->|Yes| ADS
    I -->|Unknown/PAID| HELD[Protected hold, exact original identity preserved]
    F -->|PAID/OWED| HELD
    F -->|Print SENDING/UNCERTAIN| P[Mark uncertain and quarantine; no replay]
    P --> HELD
    F -->|Drive pending, paid authorized| UP[Resume idempotent upload worker only]
    UP --> ADS
    HELD --> CLAIM[Wait for original customer claim or safe machine release]
~~~

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
    QR --> H[Abandonment never refunds a consumed game attempt]
~~~

## 3. Critical failure decisions and risk register

| Critical point | Threat / failure window | Required protection | Reference acceptance |
| --- | --- | --- | --- |
| K01 Booth ownership | A's draft frame shown to B | Local privacy fence, worker drain, versioned lease/ACK before admitting B | PP-PRIV, PP-HAND |
| K02 Capture durability | crash after 1/2/3 captures or pending retake | Atomic intent/manifest, no duplicate shots, consumed retake lineage | PP-CAP |
| K03 Final preview mutation | cart/copies/photos no longer match price | Frozen revision, exact outputs/assets, server quote, revalidate on resume | PP-FRZ |
| K04 Charge-readiness | sell unserviceable print or unreachable Drive | Two-stage preflight; late hardware failure retains paid owed | PP-READY |
| K05 QR provider uncertainty | duplicate order/charge on timeout/404 | Same original attempt, verification, idempotency journal | PP-PAY |
| K06 QR renewal | delete drafts while old provider settles | Terminal unpaid + active owner + max QR3, same frozen draft | PP-QR |
| K07 CCP late paid | A gone/B present; unauthorized prints | Non-disclosing private claim, PAID_UNCLAIMED, WAIT if busy | PP-CLAIM |
| K08 Ticket escrow | restart after PAID before handoff | Confidential encrypted single credential + gated retrieval | PP-SEC |
| K09 Receipt/photo print | partial paper, print SENDING crash | Exact job journal; UNCERTAIN no replay; distinct ticket/photo | PP-PRINT |
| K10 Drive QR | free download or false QR link | Authenticated paid-only publication; verified URL, held print otherwise | PP-DRIVE |
| K11 Fulfillment owed | COMPOSED incorrectly treated as COMPLETED | Separate paid obligation ledger per design/copies and delivery | PP-OWED |
| K12 Reboot/fencing | stale callback alters next session | Generation+lease checks, protected startup, exact journal restore | PP-CRASH |
| K13 Game promo | discount forgery/attempt reset | Server authority, one-use ledger, no production DEMO | PP-GAME |
| K14 Excessive free use | repeated unpaid captures, storage exhaustion | Adaptive inactivity, rate/resource metrics; no hard cutoff on active work | PP-ABUSE |
| K15 Lost ticket/proof | customer has no original credential | Never expose media without proof; retain financial remedy and evidence of offer | PP-SEC |

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

## 5. Scope exclusions, audit and go/no-go

- **No code changes authorized by this documentation request.** The future implementation must reuse existing `photobooth/kiosk_v2/photos.py` and `photo_views.py`, `sandbox_views.py`, `qris_session.py`, `checkout_backend.py`, `checkout_store.py`, `checkout_release.py`, `delivery_requirements.py`, original printer, Drive, local manifest, worker and AR/UAH primitives; create only minimal versioned adapters where required.
- **Do not change existing legacy PAID capture data** or claim older passing tests prove the new route. No new branch or master merge in this documentation change.
- **No original private ticket, CCP, sensitive user photo, provider secret, encryption key or synthetic-but-redeemable proof** goes into source control, printed docs or test artifacts; testing uses controlled nonredeemable fixtures.
- **Production remains NOT READY:** AR-13, merchant/provider/QRIS official evidence, physical Windows/Ubuntu POS80, tablet/Android, real privacy/Drive upload/deletion, escrow security and customer/support remedies require separate release gates.
- **Documentation definition of done** is this spec plus companion state/test/Codex plan and addenda in old navigation docs. Software tests/new PP acceptance all **NOT_RUN** until separately authorized and executed. Do not mark old CI/device evidence as proof of POSTPAY.
