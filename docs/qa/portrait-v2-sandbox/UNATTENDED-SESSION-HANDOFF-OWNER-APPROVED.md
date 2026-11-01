# Unattended session handoff, Recovery Ticket accountability, and automatic isolation

## 1 November 2026 — New-order post-preview version: interpretation/precedence (design only)

**This 541-line contract remains the authoritative historical approved UAH policy and safety design for legacy PAID-before-camera orders,** including original ticket once after PAID, 30s original-token fallback, privacy-locked public Advertising, narrow machine PREPARE/fence/local isolate/ACK/archive, busy WAIT, exact original grant, no tokenless media access, no automatic refund and no uncertain print replay. For **NEW** orders on `feature/post-preview-qris-checkout`, the owner later approved **capture and preview before QRIS**: 3 photos + up to 1 retake **per template**, final edit before provider create, one frozen total charge, original Recovery Ticket only **after PAID**, followed by print/Drive fulfillment rather than camera allocation. **Do not follow the payment->ticket->camera order in Flowchart A/C below for new-order implementation.** Old legacy prepaid transactions must continue to use it with their original grants.

**Newer post-preview decision:** mandatory original ticket screen always appears while its single paper print job is enqueued concurrently, regardless of printer success. The below conditional on-screen fallback is the legacy version only. A separate, privately **pre-PAID Checkout Claim Proof** permits proof-gated late-settlement claims; the live PAID customer does **not** need to rescan CCP. The one original Recovery Ticket is not regenerated; the memory-only prohibition still applies to unencrypted ordinary data, with an owner-approved **narrow ciphertext-only exception** for OS-protected escrow with scoped authentication/audit/expiry. Receipt transport SUBMITTED is not paper proof; receipt SENDING/UNCERTAIN never auto-reprints; a screen fallback is the *same* original ticket once for 30 seconds only when the original live owner can see it. A token not genuinely offered is an owed service failure, not customer negligence. No private photos/ticket shown to a successor. Current UAH source is not implemented; no new PP/UAH acceptance has been executed.

Paid/unknown occupancy still requires durable, original-state-safe worker barrier + scoped ACK before a new visitor. The new CCP, vault, Drive binding, and postpaid print gates are specified in [master 24 decisions + 11 diagrams](POST-PREVIEW-QRIS-OWNER-APPROVED.md), [state/security](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md), and [84 NOT_RUN tests](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md); retain historical UAH-001–050 evidence and all prior AR protections.


## NEWER owner correction — post-preview ticket is ALWAYS shown + printed concurrently (1 November 2026)

**This overrides only the *post-preview new-order* interpretation of the historical UAH-D01/D02, Flowchart A/C and UAH-001..010 old success/failure assertions.** When a new post-preview purchase reaches provider-verified PAID **and the original live customer is authorized**, the system must **always** show the original Recovery Ticket QR and full code on the kiosk with a 30-second **visible** countdown and NEXT/LANJUT, **while one print job for that exact same ticket is dispatched concurrently**. This happens even when the receipt printer is healthy and returns SUBMITTED. The screen is **not** a failure-only fallback. The print outcome never gates first QR visibility, suppresses the screen, resets its timer, or authorizes an extra send. A slow/broken printer leaves the same mandatory screen intact; one printer owner and no auto-resend of SENDING/UNCERTAIN remain binding. A customer pressing NEXT may end the screen before the paper is emitted; printer effects continue only through the original safe journal, with no overlapping photo-strip transmission.

This screen is mandatory only on **one lawful initial presentation**, not on every polling event or after a user changes ownership. PAID_UNCLAIMED, another customer, public Advertising, restart, and a duplicate PAID webhook may **never** automatically disclose the previous ticket or send an old receipt. An original late-paid claimant with CCP still needs proof, fresh PAID, a FREE booth and authorized original credential access; if ticket was genuinely presented already, never restart 30s or reissue it. If QR/code never became visible, do not claim the customer had a genuine opportunity; maintain PAID/OWED plus authorized support/remedy.

**Legacy scope remains unchanged:** Original historical UAH-D01/D02 and UAH-001's *no mandatory ticket overlay when receipt succeeds* remain valid only for the older prepaid source/version. New post-preview acceptance must use [PP-041, PP-042, PP-051, PP-079 and PP-080](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md), plus [owner master Flow G](POST-PREVIEW-QRIS-OWNER-APPROVED.md) and [secure dual-channel state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md). New functionality remains DESIGN ONLY / NOT IMPLEMENTED / NOT TESTED; this correction does not retroactively change legacy CI evidence or source.

---

**Owner decision:** 1 November 2026 (Asia/Jakarta)  
**Status:** OWNER APPROVED — COMPLETE TARGET DESIGN AND FUTURE IMPLEMENTATION CONTRACT  
**Actual source status:** DESIGN AND DOCUMENTATION ONLY; NOT IMPLEMENTED, NOT TESTED, NOT DEPLOYED  
**Read-only baseline:** `feature/portrait-kiosk-v2-next` at `81c3c6a1c67a141c9275c9910c24a6e3daac98ce`  
**Governance:** The owner explicitly requested **documentation updates only**, and expressly prohibited code changes during this discussion. No source, tests, schema, payment configuration, release, production, or default/master branch modifications are authorized by this document.  
**Priority:** Preserve AR-00–AR-13 as financial/privacy/recovery foundation; implement these approved P0 gaps in the dependency sequence in Section 12 **only when coding is separately authorized**. AR-13 remains CONDITIONAL; existing synthetic PASS is not physical acceptance.

> **Design versus reality:** "approved" in this document means owner-approved requirements, **not** proof of runtime delivery. This contract does not erase or weaken durable obligations, payment evidence, camera ownership, printing uncertainty, existing tickets, photo retention, customer privacy or the previously tested AR-00–AR-13 invariants. Source-specific history retains its original meaning.

## 1. Scope, goals and exact owner decisions

### 1.1 Product goals

- Unattended Meong PhotoBooth should resume the **same original** payment/photo session automatically when its identity, evidence and customer ownership remain valid.
- A *new* customer should see familiar Advertising instead of a confusing "SESI TERSIMPAN" screen when an *old* customer is privacy-locked.
- When a new visitor presses **MULAI FOTO** or **MAIN MEONG FLY** while an old protected visit still occupies the booth, the system should **automatically isolate and archive the old visit** if safely provable, then allow a new visit without requiring a local operator PIN.
- Preserve the old paid customer's financial/service rights, saved photos and auditable identity. **Release of booth occupancy is NOT a refund, cancellation, paid fulfillment, deletion or restoration of the previous customer's privacy capability.**
- Self-service recovery requires the customer's original Recovery Ticket. A valid ticket may restore the exact original session **only when the booth is free**, without charging again or interrupting a different customer's session.
- Operators handle only unresolved exceptions; normal retries, network outage, validated same-order reconciliation, safe handoff and a temporarily busy booth are not default operator cases.

### 1.2 Owner-approved decision register

| ID | Approved decision | Non-negotiable qualification |
| --- | --- | --- |
| UAH-D01 | After freshly verified PAID, print the **original Recovery Ticket exactly once** as the normal path | Transport SUBMITTED does not prove the paper physically exited |
| UAH-D02 | On printer unavailable/failure/timeout/UNCERTAIN, display **the same original ticket QR and full code for 30 seconds** plus **LANJUT / NEXT** | No new/reissued ticket and no replay of an uncertain receipt print |
| UAH-D03 | NEXT proceeds immediately; countdown zero auto-proceeds once | No automatic shutter; wait for original allocation and STARTED |
| UAH-D04 | The customer is responsible for saving the genuinely offered ticket | If not saved/lost/ignored, **self-service private-session recovery is forfeited**; no tokenless media access |
| UAH-D05 | A lost ticket is **not by itself** a reason to request operator recovery of protected photos | Financial/support remedies remain a separate truthful path; not an assumed refund |
| UAH-D06 | A privacy-locked old session should lead to **Advertising**, not automatically to SESI TERSIMPAN | Private pixels and callbacks must be retired immediately; ads do not prove backend occupancy has been freed |
| UAH-D07 | Advertising supports internal **ADS_READY** and **ADS_PROTECTED** occupancy modes | Same familiar public ad presentation; protected new-admission gates |
| UAH-D08 | On new visitor's action, run automatic isolation for the prior protected session where safe | No new checkout or capture before final isolation/ACK/archive |
| UAH-D09 | Safe auto-isolation does **not** need an operator PIN | Machine authority must be scoped, authenticated and audited, never a PIN bypass |
| UAH-D10 | A valid customer ticket with booth occupied by another user should be **WAIT/DEFER** | Never preempt the live customer's camera or show old photos |
| UAH-D11 | A valid ticket after safe archive may reacquire exactly the old photo permit if still eligible | Original grant, payment, manifest, retake, printed outcomes and retention remain authoritative |
| UAH-D12 | PENDING/UNKNOWN/CREATING cannot be treated like PAID when releasing occupancy | Same-order reconciliation/cancel with **fresh terminal evidence** before new payable checkout |
| UAH-D13 | If local isolation or backend ACK is uncertain, preserve old state and retry **the same operation identity** | No blind reset, duplicate releases, fresh checkout, media overwrite or print resend |
| UAH-D14 | Auto-isolation preserves PAID and OWED across history/archival | No implied refund, completion or entitlement expiry |
| UAH-D15 | Operator escalation is last resort: financial conflict, corrupt data, physical print ambiguity, unrecoverable isolation, hardware/security faults | Distinct authority for support, technician, finance reviewer, backend admin |
| UAH-D16 | Prior BUG-027 / BUG-028 direct-to-camera behavior remains for the **current original live customer** | Do not lock or isolate a valid PENDING/STARTING visitor just because polling/idle UI is quiet |
| UAH-D17 | Payment QR, Recovery Ticket, photo download QR, operator login QR and game DEMO QR are different identities | Never accept one in another scanner/context |
| UAH-D18 | No automatic refund on isolation, lost ticket, timeout, photo failure or expired QR | Merchant-approved refund/remedy policy remains a separate P2/AR-13 gate |
| UAH-D19 | Keep AR-00–13 as the foundation; regression/actual Windows, POS80 and simulator acceptance precede release | Earlier test successes do not certify new code |
| UAH-D20 | BUG-029 animated header polling reset remains a separate open visual defect | Do not change Meong animation to implement payment isolation |

### 1.3 Opportunity to keep a ticket versus guarantee of successful physical delivery

The owner accepts **customer responsibility to retain the ticket after Meong genuinely presents it**. Presentation must be honest:

1. For a configured receipt printer, persist a single original receipt-print intent before one send; ACK is evidence of transport submission, **not proof of paper in a customer's hand**.
2. If the printer says unavailable, no response, times out, throws, or the print result is uncertain, present the **original** private QR and full code on screen for 30 seconds. This is a planned change, not presently implemented.
3. Before the customer advances, show a clear warning: **"SIMPAN RECOVERY TICKET. Jika sesi terputus, tiket ini wajib untuk memulihkan sesi. Tanpa tiket, foto dari sesi terkunci tidak dapat dibuka kembali."** When displayed on screen, start the actual timer only after the pixels become visible. No forced acknowledgment is required beyond NEXT/timeout.
4. If the customer chooses not to save it or subsequently loses it, do not grant private access, mint a replacement, scan an order reference as proof, or ask an operator to reveal protected photos without authentic original proof.
5. If Meong never genuinely gave the promised opportunity (e.g. known failed print and fallback failed to render), classify it as a **device/service failure**, not customer negligence. An undetected false-positive paper ACK remains a documented hardware acceptance risk.
6. Loss of **self-service photo recovery** is NOT an assertion of payment refund, service completion, legal waiver or absence of a PAID_UNFULFILLED obligation. Support can investigate financial remedy using redacted evidence with authorized merchant workflows, but must not reveal old media without adequate authorization.
7. Ticket expiry and photo deletion are separate: current Sandbox customer capability expiry is 24h after order creation; local/Drive retention follow their independent rules. Neither extends on refresh or restart. **Commercial expiry/consumer-facing remedy policy is still subject to AR-13 approval**.

## 2. Architecture and authoritative identities

Three logically separated layers:

- **Payment ledger — backend authority:** merchant, booth, immutable checkout key/order, amount/currency and provider reference, status, fresh authoritative Midtrans observations, reconciliation revision, closed flag. Never treat QR rendering, simulator success UI, HTTP 200, prior cached PAID or app history as a fresh settlement.
- **Fulfillment ledger — backend/local durable rights:** one fulfillment/grant and one original transaction identity per paid order; OWED/STARTED/COMPOSED/SUSPENDED/PAID_UNFULFILLED, frozen template and copy requirements, capture/retake/media hashes, print/Drive consequences. A suspended/closed checkout can **still** owe service.
- **Booth occupancy and presentation — local UI plus fenced backend authority:** public ads, live customer proof, private media visibility, photo/camera lease and generation. Public navigation does not authorize new payment or any file access.

Never share a customer recovery token with booth credentials, server key or operator PIN. The ticket is a high-entropy customer capability; store only its hash on the server, never the plaintext or QR image in journals/diagnostics. Old-process tokens are not recreated after restart. An authenticated machine release principal is narrower than an operator or customer principal; it cannot mint claims, make refunds, open other customers' photos or approve arbitrary service transitions.

### 2.1 Relevant *actual* code at the read-only baseline

| Component | Existing behavior | Missing for this new design |
| --- | --- | --- |
| `photobooth/kiosk_v2/app.py::_tick` and `sandbox_views.py::_sandbox_lock_customer` | Idle privacy lock (60 seconds for eligible live protected states) removes private display; navigation currently goes to Sandbox recovery screen | ADS_PROTECTED route with proven backend occupancy semantics |
| `sandbox_views.py::_sandbox_open_saved` | From Advertising, rejects lookup while `flow.active` | Claim path for a **locked still-active** original visit as well as archived ones |
| `sandbox_views.py::_poll_sandbox` | Same-order polling and BUG-028 live STARTING continuation | Transition to ads/auto isolation without restart/reset regressions |
| `qris_session.py::print_recovery_receipt` | One receipt attempt; NOT_CONFIGURED / UNCERTAIN/ SUBMITTED states; original token in memory | Approved private 30s on-screen fallback; no false received claim |
| `qris_session.py::lock_customer` | Retires plaintext ticket and live ownership on privacy lock | No re-issue; UX must honestly warn prior to customer loss |
| `checkout_release.py::prepare/acknowledge` | PAID + OWED, valid customer capability or explicit legacy Sandbox case, two-phase fenced release | Separately authenticated, narrowly scoped **automatic machine** release; PENDING/UNKNOWN/expired proof paths |
| `qris_api.py` and `qris_kiosk_client.py` | Existing release endpoint requires 8-digit **operator PIN** | Dedicated machine identity/endpoint or proven equivalent, without bypassing guards |
| `kiosk_v2/photos.py::isolate` | Serialized worker receipt, exact ownership, rejects uncertain print/unsafe delivery transports | Safe independent active print and Drive worker isolation for later purchased-print integration |
| `checkout_store.py::begin` | Blocks another active nonterminal checkout at the same booth | Admit only after verified old occupancy release; no second order on ambiguous status |
| `checkout_backend.py` | Refund/partial_refund map to REVIEW_REQUIRED; PAID_UNFULFILLED may be recorded | No merchant refund issuance; financial support remains manual/policy-gated |
| `docs/qa/portrait-v2-sandbox/RECOVERY-TICKET-ONSCREEN-FALLBACK.md` | Existing owner-approved fallback contract, previously documentation-only | Align wording with customer's retention responsibility and this approved handoff |

Code mapping is a read-only source review, not a new test claim.

## 3. User journeys and navigation state machine

### 3.1 State table

| UI / occupancy state | Visibility | Allowed actions | Forbidden |
| --- | --- | --- | --- |
| ADS_READY | Public ads, Meong brand, photo/game/recovery entry | Begin a new photo/game, redeem original ticket only if booth free | Any old customer photos/token |
| ADS_PROTECTED | The **same public advertising experience**, neutral preparation if needed | Request a new visit **via guarded auto-isolation**; open safe original ticket lookup if no other live customer | Creating QRIS order, camera, old images, unverified payment |
| AUTO_ISOLATING | "Menyiapkan photobooth" neutral spinner + bounded retry/status | Retry/requery original action, safe cancel of new-admission intent | Capturing, payment creation, forcing release, changing old checkout key |
| ADS_WAITING_RECOVERY | Neutral busy or deferred note | Inform a ticket holder to try when free; safe operator support only for separate irrecoverable cases | Reusing previous camera lease while a new customer owns booth |
| ORIGINAL_LIVE_PREPHOTO | Original current customer's pending checkout or PAID STARTING | Continue QR/status/allocation; same original order and camera when ready | Unnecessary privacy handoff due to UI polling |
| CUSTOMER_CLAIM | Original private proof entry, no media shown until validated | Exact capability validation, rate-limit, same original provider verification | Accepting operator QR/game DEMO/order number as proof |
| ORIGINAL_RECOVERED | Owner-verified original visit after atomic reacquisition | Original camera checkpoint, manual capture, one retake policy | Second grant, another payment, reused print job |
| EXCEPTION_HOLD | Public-neutral unavailable message, redacted troubleshooting | Bounded status retry, explicit support path | Blind new payment, reset/delete state, printing uncertain job |

**Existing navigation is not yet this table.** `ADS_PROTECTED`, `AUTO_ISOLATING`, and deferred claim route are target states, not shipped functionality.

### 3.2 Flowchart A — complete visitor flow (target)

~~~mermaid
flowchart TD
    START(["Boot / public entry"]) --> OLD{"Old protected/private visit?"}
    OLD -->|None| ADREADY["ADS_READY: public advertising"]
    OLD -->|Exists| PRIV["Fence private UI: wipe photos/ticket/camera callbacks"]
    PRIV --> ADPROT["ADS_PROTECTED: same public advertising"]
    ADREADY --> MENU{"Visitor action"}
    ADPROT --> MENU
    MENU -->|"PUNYA TIKET PEMULIHAN"| CLAIM["Enter or scan original Recovery Ticket"]
    MENU -->|"MULAI FOTO / MAIN MEONG FLY"| OCC{"Unisolated booth occupancy?"}
    CLAIM --> VALID{"Original capability, fresh payment evidence and booth ownership valid?"}
    VALID -->|"Invalid / expired / lost"| NOACCESS["No private-photo access; optional redacted support"]
    VALID -->|"Valid, other customer active"| WAIT["Wait / return later; do not interrupt camera"]
    VALID -->|"Valid, free"| RESTORE["Reacquire original fenced permit and original photo transaction"]
    RESTORE --> PHOTOS["Original camera/photo checkpoint"]
    OCC -->|No| ENTRANCE["New visitor admitted"]
    OCC -->|Yes| CLASSIFY["Classify prior order; safe handoff prerequisites"]
    CLASSIFY --> SAFE{"Safe closure or isolation provable?"}
    SAFE -->|No / unknown| HOLD["Retain old identity; same-operation retry / support"]
    SAFE -->|Yes| ISOLATE["Authenticated auto-isolation; local receipt; backend ACK; archive"]
    ISOLATE --> ACK{"Verified durable release and free booth?"}
    ACK -->|Yes| ENTRANCE
    ACK -->|No| HOLD
    ENTRANCE --> ROUTE{"New visitor chose"}
    ROUTE -->|Photo| TUTORIAL["Tutorial if needed"]
    ROUTE -->|Meong Fly| GAME["DEMO receipt -> game -> Win/Lose"]
    GAME --> TUTORIAL
    TUTORIAL --> TEMPLATE["Template carousel and print quantities"]
    TEMPLATE --> PREFLIGHT["Camera/storage/template preflight + immutable quote"]
    PREFLIGHT --> QR["Original QRIS order/QR"]
    QR --> STATUS{"Fresh provider status?"}
    STATUS -->|PENDING| QR
    STATUS -->|Expiry verified| RENEW["Bounded QR replacement; after third expiry -> ADS"]
    RENEW --> QR
    STATUS -->|UNKNOWN| VERIFY["Reconcile SAME order; never new charge"]
    VERIFY --> STATUS
    STATUS -->|PAID| RECEIPT["Single original Recovery Ticket receipt send"]
    RECEIPT --> POK{"Receipt transport ACK?"}
    POK -->|Yes| PHOTOS
    POK -->|No / UNCERTAIN| ONSCREEN["Original ticket on screen 30s + NEXT"]
    ONSCREEN --> PHOTOS
    PHOTOS --> REVIEW["3 photos; one retake; review"]
    REVIEW --> OUTPUT["Compose; approved print; Drive retry per original policy"]
    OUTPUT --> FINISH["Durable completion and obligations tracked"]
    FINISH --> ADREADY
~~~

**Interpretation:** the PENDING/QR arrow means keep the original pending order, *not* generate a fresh order each loop. ONSCREEN/NEXT must still pass the original STARTED and photo-readiness gates before the camera. A same-customer live prephoto state is exempt from unnecessary abandonment; a restarted old private visit is not.

### 3.3 Flowchart B — privacy lock, advertising and start request

~~~mermaid
flowchart TD
    EVENT["Protected privacy trigger: idle 60s / minimize / restart / interruption"] --> LIVE{"Same live prephoto checkout still valid?"}
    LIVE -->|"Yes; exact customer and no private allocation"| CONTINUE["Retain original QRIS/STARTING and continue under existing BUG-028 safeguards"]
    LIVE -->|No| HIDE["Hide thumbnails, live frame, download QR, ticket, stale callbacks"]
    HIDE --> ADS["ADS_PROTECTED advertising (not SESI TERSIMPAN)"]
    ADS --> CUSTOMER{"Action"}
    CUSTOMER -->|Recovery Ticket| CLAIM["Verify ticket without showing old photos"]
    CUSTOMER -->|New Photo / Game| CHECK["Check actual backend occupancy and local workers"]
    CHECK -->|Free| NEW["Start new visitor"]
    CHECK -->|Occupied| PREP["Auto-isolation, no operator PIN for safe case"]
    PREP --> PROOF{"Valid local receipt + durable backend ACK + archive?"}
    PROOF -->|Yes| NEW
    PROOF -->|No / unknown| HOLD["Remain neutral; same release identity retry; no new payment"]
~~~

### 3.4 Flowchart C — payment, ticket, camera and interruption

~~~mermaid
flowchart TD
    A["Checkout identity and health preflight"] --> B["Create exactly one pending QRIS order"]
    B --> C{"Fresh provider status"}
    C -->|PENDING| C
    C -->|UNKNOWN / late 404| D["SAME ORDER status/reconciliation, bounded backoff"]
    D --> C
    C -->|Verified unpaid expiry / cancel| E["Safely close/renew original payable attempt per QR1-3 rules"]
    C -->|PAID| F["Exact fulfillment grant, one original receipt intent"]
    F --> G["Attempt to print Recovery Ticket once"]
    G --> H{"Receipt submission?"}
    H -->|Acknowledged| I["Photo allocation / STARTED check"]
    H -->|Unavailable / failure / uncertain| J["Show same original QR + full ticket code on kiosk"]
    J --> K{"NEXT pressed or visible 30s reached zero?"}
    K -->|Yes exactly once| L["Clear token QR/text and retire callback"]
    L --> I
    I --> M{"Backend STARTED, local transaction and camera ready?"}
    M -->|No, temporary| N["Retry original operation; no new allocation"]
    N --> M
    M -->|Yes| O["Manual SIAP -> 5s countdown -> photos"]
    O --> P["Review / one retake / compose / output obligations"]
    P --> Q(["Finish; ads"])
    O -.->|"Privacy lock / app interruption"| R["Protect original obligation; show ADS_PROTECTED"]
~~~

### 3.5 Flowchart D — recovery from advertising

~~~mermaid
flowchart TD
    A["Advertising: PUNYA TIKET PEMULIHAN"] --> B["Enter original full ticket / scan with scoped decoder"]
    B --> C{"Token shape, booth, expiry, rate-limit, order identity valid?"}
    C -->|No| D["Deny private data; ordinary retry limits, no tokenless restore"]
    C -->|Yes| E["Verify fresh provider settlement and original grant/claim"]
    E --> F{"Payment and original rights valid?"}
    F -->|No / uncertain| G["No camera; same-order retry or exception without disclosure"]
    F -->|Yes| H{"Another visitor controls camera?"}
    H -->|Yes| I["Busy: return later, no operator by default"]
    H -->|No| J{"Active locked visit or archived SUSPENDED?"}
    J -->|"Active locked"| K["Prove original ownership and reacquire same active visit"]
    J -->|"Archived and ACKED"| L["Atomic reacquire old release/fence and saved original visit"]
    K --> M["Restore exact same manifest/retake/copy identity"]
    L --> M
    M --> N{"Original media and original photo permit verified?"}
    N -->|Yes| O["Resume at correct checkpoint; no automatic shutter or reprint"]
    N -->|No| P["Retain OWED and offer separate support/remedy; no synthetic photos"]
~~~

### 3.6 Flowchart E — auto-isolation decision and safe release

~~~mermaid
flowchart TD
    A["New visitor requests Photo or Meong Fly"] --> B{"Old visit state?"}
    B -->|"None / safely terminal unpaid"| READY["Verify occupancy free, admit new visitor"]
    B -->|"Original live current visitor"| LIVE["Continue original session; never hijack"]
    B -->|"PENDING / CREATED / UNKNOWN"| P["Try original cancel/status reconciliation; preserve original order"]
    P --> TERM{"Fresh verified terminal unpaid AND durable closure?"}
    TERM -->|Yes| READY
    TERM -->|No / unknown| HELD["Hold new paid checkout; retry bounded; surface support if unresolved"]
    B -->|"PAID + OWED + proof/worker safely eligible"| S["Authenticated machine PREPARE: rotate suspended fence and persist operation ID"]
    S --> LOCAL["Quiesce old camera/print/Drive work; verify exact manifest and isolation receipt"]
    LOCAL --> LOK{"Safe local isolation proven?"}
    LOK -->|No| HELD
    LOK -->|Yes| ACK["ACK same release ID and isolation receipt; archive exact original"]
    ACK --> AOK{"Durable ACK and archival / free occupancy verified?"}
    AOK -->|No / lost reply| REQ["Requery or retry SAME operation identity; no blind second effect"]
    REQ --> AOK
    AOK -->|Yes| READY
    B -->|"REFUND / REVIEW_REQUIRED / corrupt media / uncertain printing"| HELD
~~~

### 3.7 Sequence chart — exact order, actor and acknowledgment

~~~mermaid
sequenceDiagram
    participant U as New visitor / UI
    participant K as Kivy kiosk coordinator
    participant B as Authenticated backend
    participant W as Serialized photo/print/Drive worker
    participant J as Durable local journal
    U->>K: Tap MULAI FOTO or MAIN MEONG FLY
    K->>B: Read original occupancy/order/provider evidence
    B-->>K: Old PAID/OWED and current fence generation
    K->>J: Persist original release intent + immutable operation_id
    K->>B: Machine-authorized PREPARE (exact original order + operation_id)
    B->>B: Validate entitlement, rotate suspended service fence, record PREPARED
    B-->>K: PREPARED + generation / original reference
    K->>W: Stop/cancel stale work; isolate exact bound session
    W->>J: Flush/verify original manifest, external job state and media ownership
    W-->>K: Typed exact isolation receipt or explicit failure
    alt Receipt valid
        K->>B: ACK original operation_id and isolation receipt
        B->>B: Verify fence, mark release ACKED, preserve PAID/OWED
        B-->>K: ACKED/closed original visit
        K->>J: Archive original visit under original immutable identity
        K->>B: Verify released occupancy, no conflicting active lease
        B-->>K: FREE
        K-->>U: New visitor admitted
    else Failure / ambiguous worker / lost ACK
        K->>B: Query same operation_id / original state (bounded)
        B-->>K: PREPARED / ACKED / unknown
        K-->>U: Neutral protected hold; no new payment or photo
    end
~~~

**Crash ordering:** actual authoritative implementation must choose recoverable journal/ACK ordering and verify both sides before admitting the next customer. The above diagram is a desired operation narrative, not a claim that all persistence calls already exist.

## 4. Payment-state-aware old-visit release matrix

| Old visit evidence | What unattended kiosk may do | Must not do | Escalate when |
| --- | --- | --- | --- |
| No old checkout / verified free | Start new visit | Reopen other user's photos | Unexpected ledger or camera lease |
| Verified unpaid EXPIRED/CANCELLED/FAILED and no existing fulfillment/grant/media | Finish durable terminal close, free booth | Assume a local UI timer is provider proof | Terminal and journal disagree |
| QR still PENDING and payable | Keep/verify same order; on *new* user intent, attempt authorized cancel and fresh terminal proof before new admission | Open another payable order while first is still active | Provider never proves cancellation/expiry |
| New order POST lost / 404 not proven / ambiguous created | Same-order GET/reconciliation; durable wait/backoff | Re-POST new identity or use 404 as "never charged" | Persistent unknown or mismatch |
| Verified PAID, OWED, exact original grant + valid claim/lease and safe quiescence | Narrow machine PREPARE → local isolate → ACK → archive | Complete/refund/erase original; operator PIN shortcut | Unable to prove worker/file/ACK |
| PAID and current live prephoto STARTING, not privacy-retired | Retry SAME allocation and enter original camera | Kick the paying customer to ads | Original operation inconsistency |
| PAID after receipt status SUBMITTED but paper missing | Preserve receipt evidence and original entitlement; separate documented customer responsibility from physical delivery risk | Claim verified paper based only on SUBMITTED | Customer or hardware reports genuine failure |
| PAID, print SENDING/UNCERTAIN, actively unsafe Drive/print worker or corrupt manifest | Quiesce only when proven safe, otherwise hold | Retry original print or discard photos | Physical paper inspection / data recovery |
| Older ticket expired/revoked, but paid rights remain | Protect original PAID/OWED and use approved specialized release/remedy policy | Mint substitute proof or delete paid obligation | No safe automated aging policy |
| Refund/partial_refund/REVIEW_REQUIRED or provider identity conflict | Preserve audit/evidence; do not issue old service grant; evaluate future separate occupancy release policy | Infer settlement, issue automatic refund or new charge | Financial/backend reviewer |
| Original archived SUSPENDED + ACKED | Allow new visitor; old customer ticket may reacquire only while booth free | Preempt current customer | Original proof/media no longer valid |

**Critical source gaps:** Existing `checkout_release.prepare` is PAID+OWED and valid unexpired capability (or explicit legacy ticketless Sandbox case), operator-authenticated; it cannot be repurposed for unverified unpaid states, expired paid capability or arbitrary release. Existing `photos.isolate` denies unsafe active printer/Drive transports. These are **P0 design dependencies**, not reasons to remove guards.

## 5. Privacy and advertising contract

- On protected idle timeout (current source generally 60s for applicable live states), application minimize/suspend or old private visit after restart, wipe/hide private media *immediately*: camera preview, thumbnails, original ticket QR/plaintext, download QR, private ticket-entry field, input callbacks, pending capture countdown, photo frame cache, operator PIN and stale status callbacks.
- Honor existing BUG-028 live prephoto exception: PENDING checkout or eligible original STARTING may remain in the original safe flow rather than unexpectedly being privacy-locked or moved to ads. Do not lock the current paying visitor based only on provider polling/UI animation.
- Ad playback must not start until protected media is no longer visible; the advertising renderer must not use the previous customer's private photo as ad/preview.
- ADS_PROTECTED is a public **visual presentation only**. The server must still prevent a new checkout until old occupancy release is acknowledged. Disable/guard all entry paths including automated face invitation, game handoff, keyboard shortcuts, delayed touch callbacks and operator demo affordances.
- When the visitor taps to start, display a neutral, bounded status ("Menyiapkan photobooth. Mohon tunggu.") during isolation; no private order reference or original money/identity. If safe isolation cannot finish, offer a neutral unavailable message and retry; do not show old photo/session or ask a new visitor to pay.
- Customer ticket lookup opens a protected customer-claim screen **on explicit customer action only**, not automatically on lock. Old already-private media stays hidden until fresh original proof and camera ownership are confirmed.
- Prevent ad lifecycle from interrupting still-running original print/media worker without a deterministic barrier. Loss of UI state is never proof that payment or print transport stopped.

## 6. Recovery Ticket and self-service entitlement contract

- The original ticket is generated once in original live order creation and hashed at rest. It is a **customer capability**, not an order ID, tokenless PIN, generic demo QR, invoice or payment QR.
- Print once; if failed/uncertain, display full original QR/code 30s. Present genuine, legible QR on 800x1280 and 452x900; provide NEXT and auto-dismiss, no duration reset on polling. No claim of printed paper from a transport-only ACK.
- If customer does not save an offered ticket, **locked photo-session self-service access is lost**, with no entitlement to an operator-free reissued private ticket. Operator cannot manufacture proof or expose existing private images without approved identity/ownership. This is owner-approved UX policy, not automatic disappearance of financial liabilities.
- Private ticket plaintext/QR must be wiped when consumed, timed out, minimized, privacy-locked, restarted or owner changed. Do not persist to disk/SQLite, logs, screenshots, analytics, browser, clipboard or backups.
- Existing Sandbox trial ticket expiry: 24h after original order creation; no restarts/refresh/30s timer extend it. Effective commercial lifetime and financial remedy rights require separate policy.
- Valid original ticket after archive reopens only the **exact original** transaction, manifest, grant, retake quota and existing approved print/Drive history. If booth is already occupied, wait; no operator by default, no camera preemption, no redispatch of ambiguous print.
- No tokenless media recovery via operator PIN, Demo QR or numeric order reference; human support may handle redacted evidence/payment complaint and merchant remedy separately.
- If a customer says receipt paper never emerged despite SUBMITTED, record a real-device incident without assuming their mistake; whether that printer can prove sensor/paper outcome is a separate actual-device acceptance question.

## 7. Operator, technician, administrator and financial reviewer: escalation matrix

**Default levels:** FULL AUTO when verifiable; WAIT/DEFER when recovery depends on time, another customer or reachable provider; HUMAN only for enduring uncertainty, physical inspection or a privileged decision.

| Class | Examples | Default treatment | Human role if unresolved |
| --- | --- | --- | --- |
| A — Fully automatic | QR status poll, verified unpaid expiry, normal same-order cancellation, original live PAID STARTING, safe paid isolation, resumable provider outage | Persist/retry boundedly; no operator | None |
| B — Wait / defer | Valid ticket but another customer actively using booth; intermittent connectivity; original backend ACK slow; deferred safe upload | Public neutral status; safe retry later | Only if persistent and high impact |
| C1 — Financial conflict | Old charge pending with unprovable cancellation; provider identity/amount mismatch; REVIEW_REQUIRED/refund/partial_refund | Freeze financial authority; preserve exact evidence; no duplicate order | Merchant financial reviewer / authorized backend admin |
| C2 — Data/privacy ownership | Wrong cross-booth token, expired/forgotten original proof, missing/corrupt manifest/photo | No private media; preserve OWED/retention where applicable | Customer support for non-media remedy; technical admin for corruption |
| C3 — Physical print uncertainty | Spool SENDING/UNCERTAIN, no trustworthy physical-paper status | No automatic reprint or fake delivered ACK | On-site operator/technician |
| C4 — Device/storage fault | Camera disconnected after PAID, disk full, lost filesystem permissions, broken receipt printer | Record PAID_UNFULFILLED and isolate if proven; otherwise hold | On-site technician and support |
| C5 — Isolation/worker/fencing conflict | Wrong generation, local receipt mismatch, corrupt archive, unresolved background effect | Hold new purchase, retry exact operation; no broad reset | Technical/backend administrator |
| C6 — Security/availability | Repeated wrong PIN, token replay, secret exposure, multi-process lease or restart loop | Rate-limit/fail-closed, privacy-first | Security/admin/incident response |
| C7 — Remedy/refund | Verified paid but service irretrievably undelivered; customer financial complaint | Keep auditable PAID/OWED until authorized remedy | Merchant support + financial decision maker |

A valid recovery ticket presented while booth is busy is **NOT automatically C**. A missing ticket after genuine offered delivery is **not a mandate to restore the prior customer's private photo**. Do not collapse all humans into the same omnipotent kiosk PIN: separate technician, support, finance and backend/security authority.

## 8. Failure, concurrency and crash consistency requirements

### 8.1 Durable transitions

- At each external effect, persist a uniquely bound intent **before** acting: new QRIS create, paid grant allocation, recovery receipt print, approved photo print, local media capture/retake, Drive upload and kiosk release.
- On any ambiguous timeout, consult original identity and provider/ledger evidence; do not infer the effect never occurred.
- A submitted receipt print is *not* automatically reprinted; an uncertain printed strip must not be replayed. If paper inspection is essential, route to a physical operator.
- New customer admission requires server-confirmed free booth, fenced old authority and durable local journal/worker separation. Exactly one active camera owner; late callbacks from old generation must be ignored.
- If backend ACK succeeded but reply was lost, requery **same release operation** and verify original archive before freeing booth. If local isolation succeeded but ACK failed, remain protected and preserve recoverable state.
- If PREPARE succeeded but local isolate failed, retain backend suspended fence and old rights until a safe same-operation recovery or human correction; never treat PREPARED as ACKED.
- If application restarts between any two steps, do not mint new ticket, order, grant or photo ID; reopen via original journals and verify where authority resides.
- Validate exact original manifest and photo hash, no "newest folder" inference, no directory overwrite; protected archives survive retention rules and financial audit policy.
- Disconnected Google Drive may continue its original immutable-folder retry queue **only after** background ownership and file access are demonstrably separated. Current Sandbox release has no blanket support for such active transports.
- Release of old occupancy and service fulfillment are independent: old PAID/OWED is not marked COMPLETED until appropriate original service checkpoints.

### 8.2 Recovery after losing the original ticket

If the originally offered receipt/fallback was genuinely delivered but the customer discarded it, protected media access is not reopened. Customer service may check order/settlement and decide a **non-media financial remedy** according to approved policy; it may not display saved photos, fabricate a recovery credential or automatically refund. A protected customer capability expiring does not erase photo/financial retention obligations. Current backend cannot automatically isolate an aged PAID order solely by using an expired capability; design a separate auditable, scoped mechanism without weak token checks.

### 8.3 No automatic refund

- `cancel` and `expire` for unpaid orders are not refunds.
- Provider `refund` or `partial_refund` is evidence mapped to `REVIEW_REQUIRED`; current app **does not issue refunds**.
- PAID_UNFULFILLED remains an honest service/remedy liability. Isolation does not settle the obligation or charge again.
- Future actual Midtrans Dashboard/API refund policy, eligibility, partial/full rules, merchant approval, financial reconciliation and customer messaging are separate AR-13 commercial decisions, not authorized by this documentation.

## 9. Suggested customer-facing copy (Indonesian)

| Screen/state | Suggested public message | Interaction |
| --- | --- | --- |
| ADS_READY | "ABADIKAN MOMEN DI GALAKSI" | MULAI FOTO / MAIN MEONG FLY / PUNYA TIKET PEMULIHAN |
| ADS_PROTECTED | Normal advertising, no previous-customer details | Same buttons; new-entry click triggers safe isolation first |
| AUTO_ISOLATING | "Menyiapkan photobooth untuk sesi berikutnya. Mohon tunggu." | No checkout/printing until fully ready |
| Unresolved isolation | "Photobooth sedang menyiapkan sesi. Pembayaran baru belum tersedia. Silakan coba lagi." | Bounded retry; redacted help if needed |
| Receipt fallback | "SIMPAN RECOVERY TICKET KAMU! Tiket ini diperlukan jika sesi foto terputus. Tanpa tiket, sesi yang terkunci tidak dapat dipulihkan." | Original QR/code, visible 30-second countdown, LANJUT |
| On-screen NEXT | "LANJUT" | Continue exact original photo-session preparation immediately |
| Valid ticket, busy booth | "Photobooth sedang digunakan. Silakan gunakan tiket ini setelah sesi saat ini selesai." | No photo disclosure or preemption |
| Invalid/expired ticket | "Tiket tidak dapat diverifikasi untuk membuka sesi foto ini." | Generic retry guidance without token/order enumeration |
| Original recovery temporary wait | "Sedang memeriksa transaksi sebelumnya. Jangan membayar ulang." | Retry same original order |
| Known unpaid expiry | "QR pembayaran kedaluwarsa. Kami menyiapkan QR yang baru." | Bound QR1–QR3; no automatic replacement after verified third expiry |
| PAID service failure | "Pembayaran tercatat, tetapi layanan belum selesai. Simpan bukti pembayaran dan gunakan jalur bantuan yang tersedia." | Support remedy, never "refunded" unless provider confirmed |
| Hardware unavailable before payment | "Kamera / penyimpanan belum siap. Pembayaran belum dimulai." | Do not show a payable QR |

Do not invent a support phone/QR, availability timer, refund promise, photo-recovery extension, paper sensor or real merchant outcome. Kiosk should show only channels that are actually provisioned and approved.

## 10. Test and acceptance matrix — ALL TARGET CASES NOT RUN

Use synthetic images, fake Midtrans Sandbox provider state, ephemeral files and short-lived fake tickets. Include original Windows touchscreen-size acceptance and actual POS80/simulator tests separately; no live merchant or real financial effects. **Status below is REQUIRED / NOT_RUN**, even if earlier AR tests cover a subset. Mark PASS only at the exact tested source SHA.

### A. Receipt, proof and fallback

| ID | Required scenario / assertion |
| --- | --- |
| UAH-001 | Fresh PAID + configured printer ACK: one persisted receipt intent, one transport send, direct camera preparation, no mandatory ticket overlay |
| UAH-002 | Printer missing/not configured: original ticket QR + full code displayed in 30s fallback; no new token, charge or print |
| UAH-003 | Printer exception/timeout/no response: same fallback, original uncertain job retained, no automatic resend |
| UAH-004 | After-send UNCERTAIN survives restart: no second physical send; no raw token recreation or private exposure |
| UAH-005 | Countdown actually displays 30..0 at 800x1280 and 452x900; starts on visible render, never resets on polling |
| UAH-006 | NEXT at second 29, 1 and exact zero race: exactly one exit; no double STARTED or camera admission |
| UAH-007 | Original QR decodes to exact synthetic ticket; full code readable; QR payment/claim/operator/DEMO identities rejected cross-context |
| UAH-008 | Fallback cleared on NEXT/zero/minimize/privacy lock/exit/restart and no stale callback can reveal ticket |
| UAH-009 | Enter camera only after original backend STARTED and local readiness; never auto-trigger shutter |
| UAH-010 | Owner-reported missing real printed paper despite SUBMITTED: real hardware acceptance flags sensor/physical ambiguity; no invented paper-proof status |

### B. Privacy lock and advertising

| ID | Required scenario / assertion |
| --- | --- |
| UAH-011 | Eligible idle 60s during protected photo stage: old pixels wiped immediately; public ADS_PROTECTED shown, not automatic SESI TERSIMPAN |
| UAH-012 | Minimize/resume during protected photo: stale camera preview, token, thumbnail, download QR and old callbacks hidden |
| UAH-013 | Restart with previously locked PAID journal: no old private media or ticket; public advertising with protected occupancy |
| UAH-014 | Original live PENDING and BUG-028 STARTING stay on same valid original flow when eligible; no spurious ad detour |
| UAH-015 | Face invitation, game entry, shortcut, rapid double tap and stale button revision cannot bypass protected admission |
| UAH-016 | ADS_PROTECTED looks like ads yet new QRIS order remains blocked until backend ACK/archive |

### C. Automatic paid release and one-owner fencing

| ID | Required scenario / assertion |
| --- | --- |
| UAH-017 | PAID/OWED, valid original capability, safe local worker: machine PREPARE -> local receipt -> ACK -> archive -> new visit admitted |
| UAH-018 | Auto-release machine principal has exact booth/order/operation scope, auditing and explicit Sandbox guard; operator PIN untouched |
| UAH-019 | PREPARE succeeds / worker isolation fails: old service fence stays suspended, booth remains blocked, OWED survives |
| UAH-020 | Worker isolate succeeds / ACK times out: requery same operation, never create new grant/order/print |
| UAH-021 | ACK succeeds / local reply lost: discover same ACK identity, finish exact archive and free only once |
| UAH-022 | Archive fsync fails after backend ACK: preserve history and block until durable local archival integrity verified |
| UAH-023 | Stale generation/old callback after release: cannot mutate protected media, send print, allocate again or disclose images |
| UAH-024 | Two concurrent new visitors / rapid Photo+Game taps: only one new admission after single valid release |
| UAH-025 | PAID with print SENDING/UNCERTAIN: cannot falsely produce isolation receipt; physical inspection when necessary |
| UAH-026 | Drive or external work active: isolation preserves original queue and immutable folder; no false green while transport unsafe |
| UAH-027 | Expired Sandbox capability with outstanding PAID/OWED: no token invention, no deletion, scoped aged-claim policy holds or escalates safely |

### D. Unpaid/unknown status and payment races

| ID | Required scenario / assertion |
| --- | --- |
| UAH-028 | Verified unpaid terminal cancel/expire/fail with no rights: durable old close, new checkout safe |
| UAH-029 | Old PENDING and new visitor intent: cancel/reconcile **same original order**, release only on fresh terminal provider proof |
| UAH-030 | Old unknown create, lost POST response, 404, provider offline: no new checkout or duplicate charge while ambiguous |
| UAH-031 | Cancel/settlement race: late PAID retained under original identity; never treat cancel request as financial proof |
| UAH-032 | Refund/partial_refund/review and wrong merchant/amount/reference: no old grant, no automatic refund or new unverified admission |
| UAH-033 | QR1/QR2/QR3 verified expiry semantics unchanged and previous order keys not reused |
| UAH-034 | Independent backend/client restart with same original operation remains idempotent, no double billing |

### E. Customer claim and media restoration

| ID | Required scenario / assertion |
| --- | --- |
| UAH-035 | From Ads, valid ticket opens a locked still-active visit only after exact proof and no other camera owner |
| UAH-036 | From Ads, valid ticket reopens archived SUSPENDED+ACKED original claim at exact transaction/retake checkpoint |
| UAH-037 | Valid ticket but other customer active: busy/wait response, no operator by default and no camera preemption |
| UAH-038 | Invalid, guessed, replayed, wrong-booth, expired token or numeric reference: generic denial, rate limit, no photo/token disclosure |
| UAH-039 | Customer did not save offered ticket: no self-service private restoration or substitute token; separate OWED remedy retained |
| UAH-040 | Lost/missing/corrupt manifest, orphan JPEG or stale template: preserve evidence and service claim, never invent photos or overwrite |
| UAH-041 | Restored one/two/three photos and retake quota: correct original frozen template/copies, no double retake or print |

### F. Operations, financial remedy and real device acceptance

| ID | Required scenario / assertion |
| --- | --- |
| UAH-042 | Customer remedy for PAID_UNFULFILLED is distinct from private media recovery and does not falsely claim refund/completion |
| UAH-043 | Financial review, tech inspection, lost ticket support and admin investigation are separately authorized and audited |
| UAH-044 | Full relevant payment/AR-00–13/BUG-027/BUG-028/QR1–QR3/game/photo/Drive/print regression PASS at actual new source SHA |
| UAH-045 | Actual owner Windows, 800x1280 and compact 452x900 (and actual laptop sizing): readable and safe ads, fallback, protected busy/claim |
| UAH-046 | Actual POS80 80mm physical send, paper absent, disconnect/timeout, manual inspect: original-only ticket and no duplicate print |
| UAH-047 | Actual Midtrans Sandbox simulator successful/expired/cancel/timeout/restart same-order lifecycle; never use actual bank payment during tests |
| UAH-048 | Actual webcam/video/Windows minimize/restore/real storage/restart; real private pixels never leak |
| UAH-049 | Real Drive/local retention and signed-out phone download access remain separate external gates; no unapproved deletion |
| UAH-050 | AR-13 pilot/security/support/merchant readiness stays BLOCKED/CONDITIONAL until explicit release authorization |

For every future implementation increment capture prior HEAD, touched files, test commands, exact PASS/FAIL/SKIP/NOT_RUN, crash boundaries, focus device, redacted proof and source SHA. Documentation-only commits do not turn a matrix row to PASS.

## 11. Open implementation and operational risk register

| Risk | Effect if ignored | Required treatment / priority |
| --- | --- | --- |
| Ticket transport ACK but no physical paper | Customer lacks recovery proof despite code's SUBMITTED state | Distinguish transport from paper, real POS80 sensor/paper acceptance; P0.1 device gate |
| Ticket never presented and privacy lock occurs | Paid customer cannot self-recover | Implement 30s fallback and private warning before any auto-isolation; P0.1 |
| 24h Sandbox claim expired while PAID/OWED | Current release prepare rejects valid-capability requirement | Separate aged-claim release design without fabricated claim/waived liability; P0.3 |
| PENDING/UNKNOWN incorrectly closed | Double charge or financial discrepancy | Fresh original evidence, atomic terminal close, quarantine ambiguous cases; P0.4 |
| Ads displayed while backend occupied | New customer may be incorrectly charged | ADS_PROTECTED payment admission guard; P0.2 |
| Local release ACK not durable or wrong fence generation | Old and new users can touch same camera/media | Exact operation/receipt, crash recovery, free-booth proof; P0.3 |
| Print/Drive worker not isolated | Old print leaks or gets repeated during new visit | Worker fencing, no UNCERTAIN re-send, independent queue design; P0.3/4 |
| Ticket valid while another customer uses booth | Cross-customer disclosure / interruption | WAIT/DEFER, no preemption; P0.5 |
| Runtime status differs from docs after implementation | False release confidence | Focused/full/CI and owner actual tests, update docs only after proof; P0.6 |
| Refund policy mistaken for session release | Financial liability silently erased | No auto refund; separate approved financial reviewer/merchant policy; P2 |
| Polled QRIS view refresh resets Meong animation | Visual inconsistency; BUG-029 | Keep separate bug priority; do not conflate with isolation; P1 |

## 12. Dependency-ordered Codex implementation backlog (not authorized yet)

**Only begin coding on a future explicit development instruction** and after checking repository rules, current source, live branch HEAD, user data/ledger backups and authoritative prior AR safety contracts. Keep small independently reviewable commits and immediate pushes **to the same existing branch**; no new branch, merge, master, production, real refunds or external deployment. First write failing regression tests for each new gap. 

| Sequence | Work package / priority | Exact deliverable | Exit evidence |
| --- | --- | --- | --- |
| UAH-00 (docs, current) | Contract and state freeze — approved | This comprehensive owner decision, flowcharts, risks, QA matrix and cross-links | Documentation-only Git commit; no source/CI PASS |
| UAH-01 (P0.1) | Original Recovery Ticket fallback | Renderer, visible 30s + NEXT, cleanup, one original token, no reprint, correct camera gate | UAH-001..010 focused/native + real printer gate NOT_RUN until executed |
| UAH-02 (P0.2) | Privacy lock -> ADS_READY/ADS_PROTECTED | Public safe display, reset private widgets, protected admission gate, live-prephoto exemption | UAH-011..016 |
| UAH-03 (P0.3) | Scoped PAID machine PREPARE/ACK | Backend auth scope + audit, durable release op, fencing, exact local worker receipt, same-ACK archive | UAH-017..027 excluding device-specific external |
| UAH-04 (P0.4) | Safe UNPAID/UNKNOWN occupancy handling | Original-order cancel/reconciliation, classified terminal close, no new order on ambiguity, aged-ticket exception policy | UAH-027..034 |
| UAH-05 (P0.5) | Ticket recovery from Advertising | Active locked and ACKED archived original lookup, busy defer, no tokenless photo recovery | UAH-035..041 |
| UAH-06 (P0.6) | Full fault injection, Windows, printer, Midtrans, Drive/retention acceptance | Complete regression, physical owner checklist, redacted evidence, update status only after matching source tests | UAH-042..050 |
| UAH-07 (P1) | BUG-029 visual header animation | Preserve flight phase through polling without financial state changes; separate micro-commit | Exact Windows visual and payment regression |
| UAH-08 (P1) | UX-07/AR-12 acceptance | Actual owner laptop/POS80/webcam/Midtrans retest and remaining matrix gaps | Source-pinned owner/device evidence, no false PASS |
| UAH-09 (P2) | Financial remedy, monitoring, AR-13 release gate | Human approval roles, merchant refund policy/manual dashboard procedures, monitoring/support terms, actual pilot approval | Explicit separate owner/commercial authorization |

**Dependency notes:** UAH-03 must not weaken the current operator PIN-authenticated release. UAH-01's receipt fallback is required before unattended protected-session handoff, but a lost original proof after genuine presentation is not a reason to bypass token rules. UAH-04 is not a blanket authority to close unknown payments. UAH-05 cannot preempt another visitor. AR-00–13/PAY/CAP/UX bug fix history remains preserved.

## 13. Definition of done / go-no-go for the new design

### Software acceptance

- [ ] Original ticket printed once when configured; fallback render/30s/NEXT implemented for failure; no raw token leakage.
- [ ] Previous protected session enters safe advertising without exposing photos or accidentally releasing backend occupancy.
- [ ] New Photo/Game attempt automatically isolates eligible PAID old sessions **without operator PIN**, with prepared fence/local receipt/verified backend ACK/archive and original OWED preserved.
- [ ] Unpaid/unknown and expiry/cancel/settlement race protect against second payable order and account for original provider state.
- [ ] Saved original ticket accepts live locked and isolated archived proof, with busy wait and exact original media restoration; no lost-ticket private recovery.
- [ ] Refunds/credits are never implied by isolation, timeout or expiration.
- [ ] Every UAH targeted test and applicable earlier AR/BUG tests are documented against the exact implementation SHA.
- [ ] All operator exception paths have least-privilege authority, redacted audit, and no unsupported promise of automatic refund or paper-delivery proof.
- [ ] Real Windows/POS80/Midtrans, media/Drive/retention and merchant/privacy approvals remain separately recorded; no synthetic PASS becomes live PASS.
- [ ] Repository docs/decisions/handover/status/acceptance ledger updated **after** each real code stage, not prematurely.

### Explicit non-goals

No mobile Android implementation, production QRIS activation, public webhook, real customer data cleanup, printer spool replay, arbitrary early account cancellation, private ticket regeneration, tokenless photo access, new branch, master merge, automatic refund, operator QR Settings implementation, new advertisement feature, speculative URL hosting or general storage redesign is authorized by this contract.

## 14. Reference and precedence index

- [Canonical AR-00–13 master specification](AUTONOMOUS-RECOVERY-MASTER-PLAN.md)
- [AR execution roadmap and micro-commit protocol](AUTONOMOUS-RECOVERY-ROADMAP.md)
- [AR-13 conditional readiness and external acceptance](AR13-READINESS.md)
- [Existing fallback ticket owner contract](RECOVERY-TICKET-ONSCREEN-FALLBACK.md)
- [Current AR-09 operator and existing release](AUTONOMOUS-RECOVERY-OPERATOR.md)
- [Existing AR fault-injection and safety matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md)
- [Operations and support role separation](AUTONOMOUS-RECOVERY-OPERATIONS.md)
- [BUG-027 original paid ticket/print camera path](BUG027-PAID-TO-PHOTO.md)
- [BUG-028 live STARTING ownership](BUG028-PAID-STARTING.md)
- [Existing source status](../../FEATURE_STATUS.md)
- [Owner decisions](../../DECISIONS.md)
- [Development backlog](../../next_step.md)
- [BUG-029 separate open visual defect](../../bug_tracker.md)

**Change control:** Any modification of these owner-approved behaviors must be recorded as a new owner decision with a clear supersession entry. This document was authored as documentation only; no code/tests/GUI were run or changed by its publication.
