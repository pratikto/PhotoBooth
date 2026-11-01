# Meong Photobooth — consolidated, no-loss owner decision ledger and precedence map

**Updated:** 1 November 2026. **Applies:** `feature/post-preview-qris-checkout`, NEW post-preview paid photo purchases, while preserving original code/legacy paid-first orders. **OWNER-APPROVED TARGET / DOCUMENTATION ONLY / NOT IMPLEMENTED / NOT TESTED.** This is an exhaustive *crosswalk of the decisions discussed in the post-preview payment, customer recovery, operator escalation, refund-first and lost-proof conversations*, not an assertion that source already behaves this way.

**Canonical policy hierarchy for new orders:**
1. This ledger identifies every decision and its **current**, **conditional**, **historical** or **not-yet-signed-off** scope; not an authorization for deployment.
2. [Master PP-D01..24 and 11 flowcharts](POST-PREVIEW-QRIS-OWNER-APPROVED.md): product flow, camera/preview, QR lifecycle, hardware, ownership.
3. [Refund/lost-proof RF-D01..26](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md): newer owner decision for refund-first on irrecoverably failed paid orders, and **NO automatic refund solely because genuine CCP/ticket was lost**.
4. [Payment/identity/print/Drive security state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) and [Midtrans researched provider limitations](MIDTRANS-PROVIDER-CONTRACT.md): independent authority, authentic settlement, idempotency, exact receipt, physical printing, safe release.
5. [PP-001..112 acceptance matrix](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) and [future Codex plan](POST-PREVIEW-QRIS-CODEX-HANDOVER.md): proposals NOT_RUN until separate coding permission, actual tests and owner acceptance.
6. Historical [UAH](UNATTENDED-SESSION-HANDOFF-OWNER-APPROVED.md), [AR](AUTONOMOUS-RECOVERY-MASTER-PLAN.md), BUG-026/027/028, UX-07, retained initial decisions and code: safety invariants always binding; **old pay-before-camera ordering is LEGACY ONLY**, not competing new-order instruction.

## A. Compact owner decision source map — **nothing silently dropped**

| Area | Current policy in the new post-preview order version | Historical/conditional distinction / verification |
| --- | --- | --- |
| A01 Deployment | Mobile: standalone Android tablet; fixed booth: Windows used mini PC + touch display. No SBC. | Actual Android build/release separately authorized; no code changes from docs. |
| A02 Kiosk portrait UI | 10.1-inch portrait kiosk, tested synthetic 800×1280 / 452×900; cat-brand GUI, public Advertising. | Device layout tests still needed; app music and idle ads remain historical unaffected requirements. |
| A03 Kiosk entry | Ads/public -> tutorial (once) -> gallery -> capture/review -> final preview -> QRIS -> verified PAID -> ticket screen **and concurrent paper receipt** -> paid strip/Drive -> protected Ads. | Previous QRIS-first/photo-after-payment is LEGACY ONLY. Never force a new legacy paid ticket into an unpaid draft. |
| A04 Templates | Existing 12 thermal 80×240 mm photostrip templates; three photo slots plus one genuine individual download QR. | Before PAID, no real public download QR or strip photo printing. |
| A05 Selections | Select more than one template and copies per design; one logical final cart/charge. | Existing GUI supports 1–9 copies; backend 1–10 is an explicit **implementation mismatch** awaiting correction. |
| A06 Pricing | One template design Rp5,000 plus Rp5,000 per printed copy (example A 2 copies + B 1 copy = Rp25,000). One frozen server-side original quote. | Old tariff examples (1× Rp10k, 2× Rp15k, 3× Rp20k) remain consistent with one-design formula. No source changed. |
| A07 Captures | Every selected template requires **3 initial photos**, each deliberate SIAP/5-second countdown, mirrored preview but original capture not mirrored. | Copy count doesn't multiply captures. No automatic shutter from backend recovery. |
| A08 Retake | Maximum **one retake of one chosen photo slot per selected template**; retake quota per immutable template session lineage. | Remove/reselect, restart, QR expiry/renewal or editing must NOT reset used quota. |
| A09 Final review | Approve each design then final all-design preview; edit designs/copies before first provider `CREATE_PREPARED` intent. | After provider create intent the whole purchase, amount, manifests and quota are immutable—even on lost response/404. |
| A10 Camera readiness | Camera, disk/fsync, artwork, private staging and worker lease must be healthy before unpaid capture. | Offline private capture is allowed. Do not charge for known unserviceable start. |
| A11 Paid checkout readiness | After all photos: verify frozen manifest, quote, printer route, Midtrans transport, authenticated Drive/sharing health and unclaimed 25-READY pool capacity **read-only**. | Do not preclaim customer folder or require customer-specific URL before PAID; those bind after payment. Printer route != paper proof. |
| A12 QR identities | Provider payment QRIS, pre-PAID private Checkout Claim Proof, post-PAID Recovery Ticket, download folder QR, QRIS Payment Slip, operator login and Meong Fly/merchant QR are **different types**; cross-use rejected. | One QR cannot authorize the meaning of another. |
| A13 First claim | Secure high-entropy CCP privately offered at first QRIS/checkout before PAID, bound to logical purchase/draft/booth and proof of opportunity. | CCP never proves PAID or grants unpaid photo media; never store raw tokens in ordinary DB/logs. |
| A14 Payment attempts | QR1 -> QR2 -> QR3 only on verified previous EXPIRED unpaid with same original **actively continuing** customer; no QR4 and no recapture. | Unpaid cancel/abandonment isn't an expiry renewal. Same immutable logical cart/quote throughout. |
| A15 Cancel/race | USER_CANCEL, APP_SUSPENDED/minimize, inactivity warning, INACTIVITY_EXPIRED and proven abandonment are different durable events. | Original provider cancel/status recheck; no second charge from HTTP 404, lost create reply or polling timer. |
| A16 Verified payment | Only fresh authentic merchant/provider settlement with correct amount/currency/booth/order allows one logical paid entitlement. | Unknown/pending -> protected same-order reconciliation; double settlement -> one service, financial review or excess refund only if unambiguous. |
| A17 Original ticket | Right after PAID and **only for rightful live original customer**, Recovery Ticket **screen ALWAYS displayed with QR/full code for 30 genuinely visible seconds and NEXT/LANJUT WHILE one identical original ticket receipt is dispatched concurrently**. | Printer healthy/SUBMITTED does not suppress screen; not failure-only fallback. No other customer receives old ticket. One token/one receipt dispatch; no automatic reprint after SENDING/UNCERTAIN. |
| A18 Ticket custody | Customer responsible for retaining CCP and original Recovery Ticket **only after a genuine opportunity to save**. | Showing QR for 30s must be actually visible; printer SUBMITTED is not physical paper proof. Store proof-offered/visible journal without raw QR. |
| A19 Lost proof | If genuine CCP/ticket was offered and customer discarded/lost it, **self-service protected photo recovery is forfeited**, and **there is NO automatic refund solely for losing that proof**. | This is **not** blanket contractual “all money irreversibly forfeited”; independent Meong failure, support/consumer rights, PAID/OWED and law remain separately governed. No proof-free photo unlock. |
| A20 Proof never offered | If original CCP screen or paid Recovery Ticket screen was never genuinely visible, it is Meong's delivery failure, **not** customer negligence. | Retain PAID/OWED, safe authorized claim/remedy; may qualify for refund if service is independently irrecoverable. |
| A21 Returning late PAID | A pays but leaves -> `PAID_UNCLAIMED` and preserved OWED; kiosk cannot publicly print old ticket/strip or reveal photos. Valid original CCP/Recovery Ticket + fresh PAID + FREE booth permits original claim. | If B occupies booth -> WAIT/DEFER, **not** operator takeover or invalidation. Lost CCP alone does not automatically trigger refund. |
| A22 Safe isolation | Private pixels/callbacks fenced immediately, exact workers quiesce, original local receipt/backend release ACK/archived, `FREE` independently proven before admitting B. | Advertising can be `ADS_PROTECTED`: public appearance **not** authority for new charge. Safe routine isolation automatic, no operator PIN. |
| A23 Customer session timeout | Stage-aware true inactivity warnings in gallery, capture, review/final preview, checkout; active legitimate camera/writes are not cut off by arbitrary hard total visit cap. | Suggested 60–90/120s are pilot parameters, NOT fixed approved production constants; provider PENDING/UNKNOWN isn't generic inactivity. |
| A24 Paid media release | No public photo link/print/download before PAID. Once paid, bind exact folder from READY pool and verify individual customer viewer URL; only then print paid 3-photo+real-QR strip. Upload may be async, truthful pending. | If URL fails, keep PAID/OWED and don't print fake QR. Stable Meong resolver deferred enhancement, hosting not authorized. |
| A25 Drive layout | Global ads/templates mirrored to devices; PB001… per booth Local assets and numbered transaction folders; per transaction Photo/01..0X raw/bw/color, 25 READY reserves. | Actual folder-tree implementation and retention must match existing `docs/photobooth-storage-layout.md` and Apps Script evidence, not an invented alternate tree. |
| A26 Retention | 15 days local paid media, 30 days Drive paid media are historical requirements; unpaid draft TTL and post-preview paid retention anchor require explicit versioned policy. | QR1 created, verified PAID, proof offer, ticket, paid photo and archive timestamps separate. 24h old Sandbox ticket TTL only legacy until separately decided for new order. |
| A27 Thermal printer | POS80 80mm; preference LAN > Wi-Fi > USB; one exclusive printer worker serializes receipt vs purchased strips; 1 design 3 photos+1 QR; dithering Floyd–Steinberg default; other algorithms remain selectable/prototype. | SENDING/UNCERTAIN/partial/physical paper uncertainty never automatic resend. SUBMITTED isn't evidence paper physically left device. |
| A28 Print paper left behind | Privacy isolation includes **physical** old paper slot risk, not just GUI pixel clearing; no old customer strip may be printed for a new visitor or claimed as physically handed over from SUBMITTED only. | Physical device inspection/claim remains exception, even when finance refund automated. |
| A29 Refund-first | **Irrecoverable independently proven merchant service failure** may receive automatic full original-payment refund (MVP preference) instead of calling operator just to reimburse customer, **only if merchant QRIS refund mechanism is active and safe**. | No refund from generic ERROR/timeout/unknown; print/Drive fencing and merchant policy, idempotent original provider refund, refund review fallback required. |
| A30 Partial output | Some strips may have emerged: keep precise/doubtful print evidence and separate paid fulfillment obligations; no auto reprint. | Prefer full goodwill refund **only after safe deterministic case classification**; otherwise physical/finance review. No unsupported paper-count guess. |
| A31 Duplicate charges | If QRIS1/2/3 have multiple unambiguously verified settlement for the same purchase, **one service max** and refund only the verified **excess charge** where provider permits. | Conflict/amount/merchant/identity ambiguous -> review, no auto-refund. |
| A32 Refund authority | Provider settlement and refund are different independently recorded state machines; original refund_key persisted once, reconcile exact status on lost reply, no duplicate refund; money returns to original channel. | Midtrans QRIS POS refund can be disabled by default; no actual refund feature verified, enabled or approved for production. Processing != bank/wallet cash received. |
| A33 Customer abandonment | Declining/restarting an original purchase/losing a claimed ticket does not *itself* authorize refund; PAID_UNCLAIMED remains claimant's rights until applicable lawful outcomes. | Merchant fault independent from loss of proof. No mandatory refund just because private self-recovery is impossible after customer negligence. |
| A34 Operator escalation | Operators/technicians/finance/security distinct roles. Normal verified payment, QR expiry, claim wait, upload retry and safe isolation need no operator; persistent printer ambiguity, failed isolation, wrong media, payment mismatch, vault compromise or provider refund unavailable require scoped human review. | A refund might settle money while kiosk remains unsafe; never force-reset worker or expose customer media. |
| A35 No generic refund | Explicit USER_CANCEL of unpaid order, 404, expiry, customer lost proof or transient printer timeout NEVER auto-refund without independent paid + irrecoverable failure (or duplicate charge). | Existing legacy no-auto-refund rule remains historic; new refund-first is narrowly conditional. |
| A36 Refund customer messaging | UI distinguishes REFUND_ELIGIBLE, INTENT_PREPARED, REQUESTED, PROCESSING, CONFIRMED, REVIEW_REQUIRED. Only share authenticated/redacted reference. | Do not promise money arrived from accepted API, or fabricate refund ETA, support telephone or successful printer paper. |
| A37 Meong Fly | Flappy-like one-time merchant receipt/game demo, valid/used/invalid QR presets, one receipt one attempt; win Rp2,500 discount candidate then template selection. | Discount requires trusted verified backend promo; sandbox DEMO must not reduce real payment; game attempt not reissued by abandoned unpaid checkout. |
| A38 Operator UI | Hidden Settings -> operator login QR only on idle Ads; Device Health, Audio Settings and Emulate Ticket presets; QR operator login, DEMO and Recovery separate. | Operator PIN/QR never unconditionally overrides private-photo, payment or provider evidence. |
| A39 Drive performance | Slow QR/file generation and Apps Script folder provisioning known; preview/print QR and in-app QR timing need fault tests; 25 READY for reducing latency, retention deletion NOT VERIFIED. | Do not label actual cloud deletion verified from readiness-only tests. |
| A40 Return/compensation law | The desired *customer negligence rule* is no automatic refund **solely due to lost genuinely presented proof**, NOT a blanket waiver of refunds or rights. | Indonesia UU 8/1999 Pasal 18/19 and merchant terms/legal review constrain any 'uang hangus' wording. |
| A41 Commercial controls | Confirm merchant-of-record, Midtrans QRIS refund activation, provider status and refund_key, eligible window, abuse thresholds, real printer evidence and remedy channel before live transactions. | Refund-first remains target design; no real transaction/refund changes from this documentation work. |
| A42 Governance | Work on **existing** `feature/post-preview-qris-checkout` only; no new branch, source rewrite, master/default merge, credentials, merchant changes, actual refund, real Drive deletion or unconsented tests. | Use microcommits, Codex future PP-00..PP-07, AR-00–13 safety as binding regression, all new PP tests NOT_RUN. |

## B. What exactly was approved, superseded, or deliberately NOT decided?

| Earlier statement | Current status for NEW post-preview orders | Existing/legacy status |
| --- | --- | --- |
| Customer pays first then takes photo | **SUPERSEDED**: capture all selected designs and review before QRIS | Preserved for already-paid legacy orders |
| Print ticket once and show QR onscreen only when paper print fails | **SUPERSEDED**: the same original ticket ALWAYS onscreen 30 actual seconds + NEXT while printed concurrently ONCE | Historical paid-first receipt fallback behavior preserved |
| Payment QR1/QR2/QR3 auto renews on any expiry | **RESTRICTED**: verified expired unpaid **only** if same visitor actively continues; NEVER on cancel or abandonment | Legacy past evidence remains branch-scoped |
| "No automatic refund ever" | **SUPERSEDED narrowly**: irreversible verified merchant delivery failure/verified excess payment may refund automatically **if provider and safety gates hold** | Current code/old UAH historically no refund issuance |
| Every printer UNCERTAIN means customer deserves auto refund | **NOT APPROVED**: physical outcome uncertain, classify/fence first; no blind reprint or blind refund | Same original safety guard |
| Customer lost genuinely displayed proof, money always legally "hangus" | **NOT APPROVED in absolute sense**; **APPROVED that loss alone => no automatic refund and no tokenless private recovery** | Original UAH responsibility rule preserved |
| Customer did not receive CCP/ticket due to Meong failure, treat as lost | **REJECTED**: never-offered is service failure, preserve owed/remedy | No consumer blame without genuine offer |
| Return valid CCP but booth occupied -> operator | **REJECTED**: WAIT/DEFER, no takeover | Same legacy UAH safe claim |
| Safe auto-isolation must have operator PIN | **REJECTED**: machine-authorized fence/ACK no PIN if proven safe; unsure -> protected hold | Old PIN-based source still not target implementation |
| Paid original photo-strip may print without verified Drive URL | **SUPERSEDED in new paid MVP**: verified exact URL before strip; offline private photo capture still allowed | Original local/legacy print policies retain history |
| Refund means service/booth now safe | **REJECTED**: refund, print/Drive workers, booth lease, financial proof and physical paper are separate axes | Same AR/UAH foundational invariant |
| Use provider refund on every generic ERROR or 24h ticket expiry | **REJECTED**: paid/irrecoverable/merchant-safe gates and legal/customer claims | No automatic refund current source |
| Current Midtrans merchant can refund QRIS over API | **UNVERIFIED** until account/channel tested and activated | Historical documents accurately label unknown |
| Stable Meong resolver URL, permanent ticket reprint, artificial hard cap, auto partial refund | **Future/non-MVP only** pending separate product and legal approval | Not silently added by this ledger |

## C. Complete end-to-end and exception/compensation flow

~~~mermaid
flowchart TD
    A([Public Ads: booth FREE verified]) --> B[Template(s), print copies, three photos/template, max one retake/template]
    B --> C[Approve all previews; edit before provider CREATE_PREPARED]
    C --> D[Freeze one immutable quote/media/artwork manifest]
    D --> E[Charge readiness: provider, printer route, Drive health+READY capacity]
    E --> F{Known-serviceable?}
    F -->|No| PRE[Unpaid draft hold, no charge]
    F -->|Yes| G[Issue pre-PAID CCP offer and QRIS1]
    G --> H{Fresh provider status?}
    H -->|PENDING/UNKNOWN| REC[Original order reconciliation; cancel distinct from expiry]
    REC --> H
    H -->|EXPIRED unpaid + active continue + QR less than 3| G
    H -->|CANCELLED or abandoned or third expired| ISO[Safe original isolation, no refund]
    H -->|VERIFIED PAID| I{Original live owner or valid returning private claim?}
    I -->|No| OWED[PAID_UNCLAIMED; no public old ticket/print]
    I -->|Yes| T[ALWAYS SHOW original Recovery Ticket QR/full code 30 visible sec + NEXT]
    I -->|Yes| P[CONCURRENTLY send SAME original ticket receipt ONCE]
    T --> FLOW[After UI dismiss, original printer worker safely serialized]
    P --> FLOW
    FLOW --> URL[Bind paid Drive folder, verify exact customer URL]
    URL --> OUT{Paid fulfillment possible?}
    OUT -->|Yes| PRINT[Paid strips + truthful background upload]
    PRINT --> END([Complete with original privacy/fencing])
    OUT -->|Not yet, recoverable| RETRY[PAID/OWED + bounded original retry and customer claim]
    RETRY --> OUT
    OUT -->|Irrecoverable verified merchant failure| RF[Refund-first eligibility classification]
    RF --> SAFE{Worker fence, original paid evidence, merchant refund support?}
    SAFE -->|No / unresolved| REVIEW[Financial/technical/security review; preserve OWED]
    SAFE -->|Yes| POST[One durable refund intent/key, original provider refund]
    POST --> RES{Provider refund status?}
    RES -->|REQUESTED/PROCESSING/UNKNOWN| POLL[Reconcile original refund key; no duplicate request]
    POLL --> RES
    RES -->|Confirmed| DONE([Refund confirmed; never release media after refund])
    RES -->|Rejected/unsupported| REVIEW
    OWED --> CLAIM[Private original CCP/ticket claim when booth becomes FREE]
    CLAIM --> I
~~~

**Note:** Flow diagram is an approved conceptual contract, not an API promise. Payment expiry renewal has separate attempt IDs QR2/QR3; it never posts the identical expired transaction again and never recreates photos. Physical printer jobs are serialized; "concurrent" means screen and single receipt dispatch occur in the same paid-ticket stage, not guaranteed simultaneous paper exit.

## D. Proof loss versus paid service failure — no ambiguous blanket forfeiture

~~~mermaid
flowchart TD
    A([Customer says CCP or Recovery Ticket was lost]) --> B{System actually offered original claim/ticket?}
    B -->|No genuine rendered opportunity| MERCHANT[Merchant proof-delivery failure: PAID/OWED, remedy, no customer blame]
    B -->|Yes, genuine visible 30s ticket/valid CCP opportunity| C{Independent verified failure of purchased service?}
    C -->|No / only ticket lost| NOREF[NO_AUTO_REFUND_PROOF_LOST; no private media access without proof]
    C -->|Yes, cannot be fulfilled| REFUND[Refund-first eligibility, exact paid/worker/provider gates]
    C -->|Uncertain paper/Drive/payment facts| HOLD[Protected review; neither blind refund nor unfounded proof denial]
    MERCHANT --> TRY[Safe original claim remedy; if irreversible service failure then refund policy]
    REFUND --> STATUS[Refund processing or review; never promise funds arrived]
~~~

**What “uang hangus” means here:** no automatic money-back request **solely due to customer's loss of a genuinely offered recovery capability**. It is NOT a contract term surrendering consumer legal rights, nor a replacement for verifying the already paid/photo/printed service. Even when self-service photo unlock is lost, keep non-sensitive financial/support rights according to law and policy. Never use a guessed photo folder or an operator QR/PIN to overcome protected media access.

## E. Failure matrix and who should act

| Event | Customer-visible booth state | Refund treatment | Needs human? |
| --- | --- | --- | --- |
| QR expired/unpaid, original customer wants to continue | Original QR2/QR3 | Not applicable | No |
| QR expired/unpaid, customer absent | Safe cancellation/isolation | Not applicable | No |
| QR create response lost/PENDING | Waiting/reconcile same original order | Not yet; no paid evidence | Only permanent provider conflict |
| PAID, original ticket screen showing, printer slow/offline | Mandatory same QR/full code 30s + NEXT | No refund just for receipt failure; bought photo strips still owed | Only if purchased print cannot fulfill |
| PAID, Drive upload delayed, URL verified | Honest pending upload with original QR | Not immediately; bounded retry | Not normally |
| PAID, Drive URL never verified | PAID/OWED hold or original claim | Refund if permanent service failure + provider/support gates | Technician if recurring |
| PAID, irreversible total printer defect | Mark paid OWED; no fake paper | Auto full candidate if safe stop/provider enabled | Technician to repair printer |
| Partial printed/UNCERTAIN | Original paid job quarantined, no replay | Review/deterministic full goodwill candidate, not blind auto | Physical audit if ambiguous |
| PAID, customer leaves then returns with valid CCP | WAIT if B using booth, else exact resume | No refund merely because departed | No safe-case operator |
| PAID, customer genuinely received proof then loses it | Cannot self-recover protected photos | NO AUTO REFUND solely due to loss | Support only separate lawful dispute |
| Meong never offered proof due crash/UI | Merchant failure; retain PAID/OWED | Refund if independent irreversible service failure | Support if no safe way to claim |
| Duplicate settlement, same original cart | One entitlement, excess identified | Refund excess only when provider evidence unambiguous | Finance otherwise |
| Printer/camera lease won't release | Public ADS_PROTECTED, no new charge | May refund failed service, but hardware remains held | Technician |
| Security/token/merchant identity mismatch | Private/security hold | No auto-refund | Security/finance |
| Refund POST uncertain | Redacted processing, original key reconciliation | No second refund | Finance only if permanently ambiguous |

## F. State/identity cross-check and exact precedence

| Plane | Original identity | Must be independent of |
| --- | --- | --- |
| Private photo draft | visit_id, draft_id, revision, template-session lineage, 3 selected slots, one retake quota/template | merchant settlement and payment screen |
| Checkout/payment | purchase_group_id, frozen hash, provider attempt QR1/2/3 and fresh verified settlement | customer-controlled timer and booth face detection |
| Customer claim/credential | original CCP, original Recovery Ticket, verifier, offer log, protected encrypted escrow | operator QR/PIN, payment QR, download QR |
| Ticket presentation | original paid ticket, actual screen-visibility 30s + NEXT, one physical receipt intent | printer transport SUBMITTED vs UNCERTAIN |
| Paid fulfillment | exact paid manifest, verified customer Drive URL, photo print jobs/copies, upload checksum | private ticket possession and physical paper receipt |
| Refund | original settled provider charge, exact refund_intent/refund_key, fee/amount, refund provider state | merchant PAID proof, booth FREE lease and print worker safety |
| Occupancy and hardware | booth lease, camera/printer workers, local fence and backend release ACK | provider refund success, public Advertising and lost customer proof |
| Privacy / retention | private media hash, local and Drive lifecycle, OWED ledger, customer original proof | lost ticket liability or unresolved financial dispute |

**No new order source implementation yet:** PP safety docs remain owner-approved design. For later implementation, build secure authenticated merchant backend refund transport *only after* merchant activation/permission; stage future work behind additional PP-RF acceptance tests, separate operator role gates, source/CI/device verification and production authorization.

## G. Future configuration not silently signed off

- Midtrans merchant-specific POS Refund API activation, original refund_key semantics, settlement/partial refund support, QRIS on-us/off-us/acquirer windows and limits.
- Maximum bounded recovery time per category, abuse threshold/total automatic compensation exposure and review threshold.
- Customer-readable refund tracking/claim endpoint and exact authenticated status response, chargeback/dispute handling.
- Legal-reviewed Indonesian customer terms that explain lost ticket responsibility without illegal blanket waiver.
- New-order CCP/ticket TTL and separate paid-photo retention timestamp anchors; historical 15d local/30d cloud not silently reset by QR renewal.
- Real POS80 printed paper evidence, sensitive print-job SENDING/UNCERTAIN quiescence before refund and physical paper left in slot.
- Multi-template full refund of partially delivered outputs as a measured MVP goodwill policy, with original media/printing controls and safeguards against patterned abuse.

**No prior decision is deleted by this consolidated ledger.** Where two prior statements are incompatible, this table identifies the new-order supersession while preserving old-version semantics and historical CI labels. [Refund and proof-loss source policy](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) and [master PP design](POST-PREVIEW-QRIS-OWNER-APPROVED.md) must be read together; neither is an instruction to issue real money or merge branches.
