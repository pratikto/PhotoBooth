# Owner-approved Meong Post-preview QRIS: refund-first and lost-proof policy

**Decision:** 1 November 2026 (Asia/Jakarta). **Branch:** `feature/post-preview-qris-checkout`. **Order version:** NEW post-preview photo purchases. **Status:** OWNER-APPROVED PRODUCT DESIGN; **NOT IMPLEMENTED / NOT TESTED / MIDTRANS REFUND API NOT ACTIVATED OR VERIFIED FOR THE MERCHANT**. This is not a real refund, production authorization, customer-facing legal terms approval, or source-code change.

**Normative relationship:** This file is the **specific new-order refund policy** supplementing the [complete all-decisions ledger](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md), [24 PP product decisions and 11 flowcharts](POST-PREVIEW-QRIS-OWNER-APPROVED.md), [financial/privacy state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md), [provider research](MIDTRANS-PROVIDER-CONTRACT.md), [acceptance](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md), and [Codex handover](POST-PREVIEW-QRIS-CODEX-HANDOVER.md). It supersedes earlier **blanket "no automatic refund" instructions ONLY for narrowly proven, safely refundable failures on the new version**. It does NOT alter the prepaid legacy order, unverified merchant capabilities, or AR/UAH safety protections.

## 1. Decision register (RF-D01–RF-D26)

| ID | Owner decision and intended behavior | Boundary / safety qualification |
| --- | --- | --- |
| RF-D01 | **Refund-first** when a PAID photo order is truly impossible to fulfill correctly after bounded automatic recovery; avoid calling an onsite operator merely to return the money. | This is a future refund-eligible path, contingent on merchant activation, lawful policy, provider support and exact order/fulfillment reconciliation. |
| RF-D02 | **Prefer automatic FULL refund of the original order amount for MVP** when the purchased service irretrievably fails; keep proportional partial-delivery refund as future, separate commercial work. | Must determine irreversible merchant failure, preserve truthfully delivered paper/data, and fence unsettled print/Drive work; customer already receiving some output is not automatically a no-service claim. |
| RF-D03 | Permanent printer failure, permanently corrupt paid outputs/manifests, or irrecoverable paid Drive delivery may be refund eligible. | Never from a generic GUI ERROR, temporary offline condition, provider PENDING/UNKNOWN, or an unproven time limit. |
| RF-D04 | When multiple distinct QRIS attempts for **one immutable logical purchase** have *unambiguously* independently settled, automatically refund the **excess verified charge only**, if safe and provider-authorized. | One purchase entitlement, exact attempt/amount/merchant evidence, conflict-fenced; if uncertain or partial, financial reviewer instead. No double fulfillment. |
| RF-D05 | **A customer who loses/discards their genuinely offered original CCP or Recovery Ticket is not entitled to an AUTOMATIC refund solely because they lost proof.** | Treat as customer-responsibility for *self-service private-photo recovery*, not as a blanket extinguishment of legal/financial rights. Operator cannot disclose old photos on verbal request. |
| RF-D06 | When a lost CCP/Recovery Ticket is the **only** complaint, and Meong's initial service was correctly fulfilled or genuinely made available, the automatic policy decision is `NO_AUTO_REFUND_PROOF_LOST`. | Record genuine offer and fulfillment evidence. No generic irreversible `FORFEIT_ALL_MONEY` or deletion of paid/owed accounting. Consumer complaint/legal review remains possible. |
| RF-D07 | **Lost proof cannot mask a separate verified service failure.** If original media, print, upload or ticket presentation actually failed through Meong's fault, classify the failure independently and allow lawful auto-refund or human remedy if eligible. | Customer proof loss does not retroactively prove or disprove merchant fulfillment. |
| RF-D08 | **No genuine opportunity to retain proof** (QR/code never visibly rendered, before-PAID CCP never offered, original ticket screen not displayed, old ownership lost, printer SUBMITTED only) is **merchant delivery failure**, not customer negligence. | Keep original `PAID/OWED`; do not say customer forfeited recovery. If proof never offered, case can qualify for recovery/remedy/auto-refund based on exact conditions. |
| RF-D09 | Distinguish Checkout Claim Proof (CCP) offered privately **at first QRIS before PAID** from Recovery Ticket generated after verified PAID. | CCP is neither paid proof nor a photo download credential. One secret must never be accepted as another type. |
| RF-D10 | **Original Recovery Ticket MUST always appear** on the rightful paid customer's screen for 30 *actually visible* seconds + NEXT/LANJUT, **while the exact SAME ticket is printed once concurrently**. | Printer success does not skip the screen; unavailable/FAILED/SENDING/UNCERTAIN cannot cause extra paper send, screen reset or reissued ticket; no public old ticket on reboot or when B owns the booth. |
| RF-D11 | A genuinely offered but lost ticket/CCP blocks **self-service private-session recovery**, not an authenticated review of payment or a consumer complaint. | No order number, payment receipt image, operator PIN or QRIS payload grants old private-media access. Redacted support may assess rights without exposing photos. |
| RF-D12 | A departed visitor, PAID_UNCLAIMED, failed claim, expired ticket or abandoned session **alone** does NOT trigger a refund. | Preserve PAID/OWED and separate retention clocks; no automatic refund after arbitrary elapsed time if service may still be recoverable. |
| RF-D13 | Distinguish **unpaid cancel/expire** from **refund of a freshly provider-verified settled PAID payment**. | Creating, PENDING, UNKNOWN, response timeout or 404 must reconcile original provider order; do not initiate a refund or assume charge was settled. |
| RF-D14 | Refund must be routed to the **original Midtrans merchant/provider transaction and originating payment instrument** through a provider-approved endpoint. | Never refund to a bank/e-wallet address typed by a public kiosk customer. Support may handle alternate lawful remedies off-booth if API unavailable. |
| RF-D15 | **Provider gates are mandatory:** confirm merchant-specific QRIS/POS Refund API activation, acquirer/issuer, settlement status, available refund window/limit/balance, refund endpoint and official reconciliation behavior. | GoPay QRIS POS documents state online refund via API/dashboard can be disabled by default; neither synthetic tests nor a public reference proves Meong account access. |
| RF-D16 | Persist one original durable **refund intent** and provider request identifier/refund_key *before* external refund I/O; one logical refund outcome per original charge. | Ambiguous timeout/404/restart -> query original refund key and provider transaction; never POST a fresh unrelated refund just to resolve UI uncertainty. Actual Midtrans key semantics/partial/full support require contract verification. |
| RF-D17 | Distinct states: `REFUND_ELIGIBLE`, `REFUND_INTENT_PREPARED`, `REFUND_REQUESTED`, `REFUND_PROCESSING`, `REFUND_CONFIRMED`, `REFUND_REVIEW_REQUIRED`, `REFUND_REJECTED`. | Provider accepted request != confirmed reimbursement != customer's bank/wallet received funds. Merchant must never tell a customer funds are returned before authoritative evidence. |
| RF-D18 | **For full irrecoverable-service refund**, stop/fence further original photo-strip print, Drive publication and stale worker effects before refund submission. **For excess settled payment refund only**, preserve the one rightful original photo order and its printing/delivery; isolate only the duplicate charge. | Preserve original receipt/print/paid ledgers; SENDING/UNCERTAIN printer jobs cannot be magically cancelled or declared unprinted. If safe isolation cannot be proven, hold for physical/technical review; refund does not unlock kiosk. |
| RF-D19 | Printed partial/UNCERTAIN outcome is a **physical evidence exception**: potential customer receipt must be recorded truthfully; no automatic reprint. | Full-refund goodwill is a **conditional policy option**, not automatic from transport timeout alone. Can auto-refund only if proof classification, worker fence and merchant abuse controls make that safe; otherwise review. |
| RF-D20 | **Refund success and repair/occupancy are independent.** A paid customer may be refunded automatically even while the booth remains `ISOLATION_HOLD` for technician work. | Refunding never force-clears camera lease, printer queue, private files, backend ACK or security hold. |
| RF-D21 | Suspected theft, forged proof, compromised vault, wrong merchant/amount, disputed multiple settlements, unverified ownership or irreconcilable partial print -> **NO AUTOMATIC REFUND**; finance/security/technician appropriately reviews. | Never treat lack of a ticket as a license to expose old photos or silently refund any unrelated transaction. |
| RF-D22 | Preserve evidence of **CCP_OFFERED**, mandatory original **TICKET_QR_VISIBLE**, `TICKET_DISMISSED`, one paper-send intent, source settlement, per-design paper/upload and refund status. | Do NOT store original raw CCP/ticket/QR bitmap, user photos, bank credentials, payment signatures or OS vault keys in diagnostic logs. Genuine screen presentation is not proved by ticket generation or printer SUBMITTED. |
| RF-D23 | Technical retry/claim/refund eligibility durations, maximum auto-refund loss budget, incident frequency thresholds and token/retention anchors need separate merchant-approved verified configuration. | No invented refund SLA, legal waiver, hard active photo timeout or blanket auto-refund on 24-hour Sandbox ticket expiry. Prevent repeat-failure abuse. |
| RF-D24 | Customer screen gives a **truthful, non-sensitive refund tracking reference** and the *exact* provider-known refund stage. | `REFUND_REQUESTED` or `REFUND_PROCESSING` must not say "Uang sudah kembali"; show `REFUND_REVIEW_REQUIRED` when merchant API unavailable, without invented support contact/SLA. |
| RF-D25 | Consumer law: "customer lost a genuinely offered proof -> no automatic refund solely for that reason" is a **narrow automation/commercial rule**, not "money irreversibly forfeited in every circumstance." | Indonesia UU 8/1999 Pasal 18 prohibits blanket standard terms refusing returns; Pasal 19(5) can distinguish proved consumer fault. Legal review of final ToS is mandatory before selling; do not implement unconditional `ALL_FUNDS_FORFEITED`. |
| RF-D26 | Historical `NO_AUTO_REFUND` remains accurate for existing source/legacy prepaid version and unknown merchant API. New refund-first policy **does not itself authorize writing code, activating merchant API, issuing money, deployment, data deletion or master merge**. | All new RF/PP tests NOT_RUN; AR-13 remains CONDITIONAL; use current branch and separately authorized implementation only. |

## 2. Operator policy: avoid human intervention when safe

| Exception | Self-service action | Refund eligibility | Still needs an operator/finance/security? |
| --- | --- | --- | --- |
| QR1/QR2 expired with willing same customer | Safe original status reconciliation and QR2/QR3 | No; no settled paid service | No |
| Customer cancels PENDING/UNKNOWN | Record cancel intent, original order cancel/reconcile | No refund unless subsequent real PAID and separate failure | No for safe resolution |
| Ticket printer fails but **mandatory screen was truly visible** | Customer saves original QR/full code; exact ticket not reprinted | **No refund just for ticket receipt failure** if paid service remains deliverable | Only if physical printer prevents purchased strips |
| Paid printer completely dead after bounded retry | Preserve paid media; safe stop/hold original print lane | **Auto FULL refund candidate** if no safe fulfillment and API eligible | Technician repairs machine, not customer refund |
| One/two photo copies emerged and others uncertain | No blind reprint; original ledger and possible customer evidence | Conditional full goodwill refund **only after safe deterministic handling**; else REVIEW | Physical inspection if ambiguity persists |
| Drive URL cannot be verified after PAID | Retain PAID/OWED, original proof, retry link+upload | Auto FULL refund candidate if irrecoverable within verified policy | Technician if systemic outage |
| Camera/photo manifest permanently corrupt after PAID | Quarantine private media and old worker | Auto FULL refund candidate for paid unserviceable order | Technician for recurring corruption |
| Two QR attempts independently verified settled | One entitlement only; identify original/excess | Refund **excess payment only** if unambiguous | Finance for ambiguous conflict |
| A left and payment later PAID | PAID_UNCLAIMED, proof-gated original claim, no public print | **No refund merely for A leaving or 30s expiry** | Not for safe claim; support on genuine dispute |
| A lost genuinely offered CCP or Recovery Ticket | No proof-free old private photos; show redacted support route | **NO_AUTO_REFUND_PROOF_LOST** when sole complaint | Support only for separate legitimate financial/service claim |
| Proof was NEVER genuinely offered | Paid owed, authorized claim/remedy path | Failure eligible if service cannot be fulfilled | Support if no safe self-service proof route |
| Printer worker/lease cannot isolate safely | Protected public screen, no new charge; preserve original state | May refund eligible failed service independently | **Yes** technical intervention for booth safety |
| Forged claim, vault breach, wrong order/merchant, unresolved payment | Security/finance review; no private media | **No automatic refund** | **Yes** appropriate admin |
| Provider refund API unavailable/ineligible/rejected | Create auditable review/support case; no fake success | Human-approved lawful remedy | Finance/support |

**Do not equate "no onsite operator for money-back" with "never need a technician"**: a refunded malfunctioning kiosk stays out of service until genuinely safe. Do not create an unattended customer refund request that claims to change a user's merchant refund policy without confirmed provider capability.

## 3. Owner decision matrix — what "hangus" means operationally

| Genuine CCP presented? | Original Recovery Ticket QR/code genuinely visible and available? | Independent evidence of merchant service failure? | Customer action | Automated financial outcome | Private media |
| --- | --- | --- | --- | --- | --- |
| Yes | Yes | No; order delivered/available as promised | Customer lost both proofs | **NO_AUTO_REFUND_PROOF_LOST**; do not claim legal right to keep money in any other case | No tokenless unlock |
| Yes | Yes | Yes, separately established permanent paid service failure | Lost proof but delivery actually failed | Evaluate refund-first **because of merchant failure**, not proof loss | No tokenless unlock |
| No | Never genuinely offered | Unknown/owed | Customer unable to recover | **NOT** customer-forfeited; protected remedy, eligible refund only after verified failure | No unsafe disclosure |
| Yes | Ticket render failed, printer may have SUBMITTED | Yes or unverified | Customer disputes delivery | Retain PAID/OWED; investigate render/actual printing; refund if proved eligible | Access only with authentic original proof |
| Yes | Yes | Unknown, physical print UNCERTAIN | Customer claims no paper and lost proof | Evidence review/hold; don't blindly refund or declare delivered | No tokenless unlock |
| Yes | Yes | No, digital fulfillment available, no proof | User chose not to save QR/code | No automatic refund solely for loss | No recovery by guessing order number |

**Customer obligation to save:** the first paid ticket screen is **always** shown for 30 actually visible seconds + NEXT while one same ticket print is dispatched. Losing or ignoring genuinely presented proof means the customer cannot invoke unverified self-service photo recovery; it does NOT erase a separately proven PAID/OWED liability or extinguish lawfully reviewable claims. A printed-job ACK by itself is **not** evidence the paper was received.

## 4. Refund state machine

~~~mermaid
flowchart TD
    FAIL([Paid order cannot complete service]) --> PAY{Fresh original provider status?}
    PAY -->|PENDING / UNKNOWN| RECON[Reconcile original order; no refund request]
    PAY -->|Verified SETTLED / PAID| CAUSE{Exact cause?}
    CAUSE -->|Customer lost genuinely offered proof ONLY| LOST[NO_AUTO_REFUND_PROOF_LOST; preserve private media and lawful support]
    CAUSE -->|Departed / expired claim only| CLAIM[PAID_UNCLAIMED / OWED, no automatic refund]
    CAUSE -->|Provider conflict / suspected fraud| FIN[REFUND_REVIEW_REQUIRED; finance/security]
    CAUSE -->|Verified irrecoverable merchant delivery failure| RECOVER[Bounded original retry exhausted; classify print and upload truth]
    RECOVER --> SAFE{Original print/upload/media workers safely fenced or quarantined?}
    SAFE -->|No / uncertain| HOLD[Technician/review; do not force-reset or blindly refund]
    SAFE -->|Yes| ELIG{Merchant refund support and transaction eligibility independently verified?}
    ELIG -->|No / disabled / expired| FIN
    ELIG -->|Yes| INTENT[Persist original refund intent/key, exact paid order and eligible amount]
    INTENT --> POST[Issue provider-approved refund on original transaction ONCE]
    POST --> RESULT{Refund provider result?}
    RESULT -->|Accepted / processing| PROCESS[REFUND_PROCESSING; honest status]
    RESULT -->|Timeout / unknown| SAME[Reconcile SAME original refund intent/key, no new refund POST]
    SAME --> RESULT
    RESULT -->|Rejected / unsupported| FIN
    PROCESS --> CONFIRM{Original refund independently confirmed?}
    CONFIRM -->|Not yet| PROCESS
    CONFIRM -->|Yes| REFUNDED[REFUND_CONFIRMED; preserve financial audit and no duplicate service]
~~~

**Refund creation MUST NOT occur based on a blank UI error alone or merchant account assumptions.** A provider order already PAID is not changed back to unpaid by refund: persist a separate refund subledger/outcome. Different original payment attempts (QR1, QR2, QR3) each require their *own* exact provider reference if refunding an excess transaction.

## 5. Printing, Drive, customer ownership, and refund race

~~~mermaid
sequenceDiagram
    participant C as Customer
    participant K as Kiosk + durable jobs
    participant P as POS80
    participant D as Drive
    participant M as Merchant payment backend
    C->>K: 3-photo/template capture, final preview, one QRIS
    K->>M: Original payment order and private CCP
    M-->>K: Fresh verified PAID
    K-->>C: ALWAYS screen original ticket 30 visible seconds + NEXT
    par One original receipt job
        K->>P: Enqueue same original ticket print ONCE
    and Original paid service
        K->>D: Bind exact paid customer folder + verify URL
    end
    Note over K,P: Ticket-screen timer is independent of receipt result
    K->>P: Purchased photo strips only with verified Drive URL and safe printer lane
    alt Fulfillment succeeded
        K-->>C: No refund; delivered original service
    else Recoverable delay
        K->>K: PAID/OWED and bounded idempotent recovery
    else Irrecoverable verified service failure
        K->>K: Fence original print/upload/media + preserve truth
        K->>M: Verify refund eligibility, persist unique original intent, request original provider refund
        M-->>K: Processing / confirmed / rejected, asynchronously
        K-->>C: Truthful refund status, reference, no invented completion
    end
    Note over K,M: Customer losing genuinely offered ticket alone NEVER triggers auto-refund
~~~

### Counterexample and safety cases
- Printer receipt SUBMITTED, but photo strips never print: **mandatory ticket screen still happened**; customer ticket loss alone is no refund reason, **but actual photo service failure is an independent refund candidate**.
- QR1 late PAID after A leaves, B is at booth: never show Recovery Ticket or paper to B; archive PAID/OWED and support original CCP claim; no auto-refund simply for absence or lost CCP.
- Original print is SENDING/UNCERTAIN with a live customer, and a **full refund for irrecoverable service** is planned: first block new print transport and classify old in-flight bytes. For **refund of a verified extra settled QRIS attempt only**, preserve the one valid purchase entitlement and its legitimate print/upload work; do not stop original service merely to return excess money. Neither refund permits bypassing unsafe printer fencing or proves paper was not delivered.
- Two attempts both PAID after unknown cancellation: preserve both financial ledger entries, refund verified excess attempt once if independently eligible; never grant two copies of service. Uncertain identity or amount -> finance.
- Refund POST timeout/restart: preserve same refund intent/key, reconcile; no duplicate refund and no already-refunded service delivery on stale asynchronous callback.
- Hardware fixed after a refund: do not resume original paid print job, open original shared Drive URL or re-enter granted paid service without authenticated later merchant remedy policy; old payment ledger is refunded.
- Lost ticket after genuine 30s screen + one printed job: no operator can reconstruct token, no no-proof photo unlock, no automatic refund for that loss alone. If original screen never rendered, it cannot be labeled a genuine offer.

## 6. Customer-facing Indonesian copy (future strings; require merchant/UX review)

| Screen condition | Truthful proposed copy |
| --- | --- |
| Original ticket screen | **"SIMPAN RECOVERY TICKET. Kode yang sama juga sedang dicetak. Tiket ini diperlukan jika sesi perlu dipulihkan."** Show QR, FULL code, actual 30s and NEXT. Do not claim printed successfully just because queued. |
| Only lost proof, no verified service failure | "Tiket pemulihan tidak tersedia. Demi privasi, foto lama tidak dapat dibuka tanpa bukti yang sah. Kehilangan tiket saja tidak menjadi alasan pengembalian dana otomatis. Jika ada kendala layanan lain, gunakan jalur bantuan yang tersedia." |
| Service failure, eligibility still being checked | "Layanan belum berhasil diselesaikan. Kami sedang memeriksa status transaksi dan opsi penyelesaiannya." |
| Refund request durably submitted and provider accepted | "Permintaan refund untuk transaksi ini sudah diajukan. Dana belum tentu langsung masuk. Silakan simpan referensi status refund." |
| Refund processing | "Pengembalian dana sedang diproses oleh penyedia pembayaran. Waktu penyelesaian dapat berbeda menurut metode pembayaran." |
| Refund independently confirmed | "Pengembalian dana telah dikonfirmasi oleh penyedia pembayaran. Waktu dana terlihat pada saldo dapat berbeda." |
| Refund API unavailable/rejected or financial ambiguity | "Pengembalian dana otomatis belum dapat diproses. Kami mencatat kasus ini untuk penanganan lanjutan." |
| Customer abandoned with pending or unknown original payment | "Status pembayaran masih diperiksa. Kami tidak membuat pembayaran baru sebelum transaksi sebelumnya jelas." |

Never display a made-up support number, provider reference, refund promise, bank receipt, fixed SLA, or hidden private photos. A redacted refund-status lookup must be scoped and authenticated to prevent leaking payment/customer data.

## 7. Merchant/provider and Indonesian legal gates

1. **Midtrans official GoPay QRIS POS:** https://docs.midtrans.com/docs/gopay-qris-pos-integration — POS online refund via API/dashboard *not automatically allowed*; contact Midtrans merchant support/account contact.
2. **Midtrans refund transaction API:** https://docs.midtrans.com/reference/refund-transaction — Core refund path, eligibility/settlement, refund identifier semantics, some acquirer-specific refund windows and refund feature activation.
3. **Midtrans supported refund methods and windows:** https://docs.midtrans.com/docs/metode-pembayaran-apa-yang-memiliki-fitur-refund — QRIS issuer/acquirer differences, off-us return time, partial/full possible where supported. **Do not hard-code historical provider figures in checkout as guarantees.**
4. **Indonesia UU No. 8 Tahun 1999 Pasal 18(1)(c) and Pasal 19:** https://peraturan.bpk.go.id/Home/Download/33784/UU%20Nomor%208%20Tahun%201999.pdf — standard terms cannot categorically refuse return of money; proof of customer mistake may affect liability. Final customer-facing contract must be reviewed for consumer-law compliance.
5. **Gates before any real automatic refund:** merchant activation + trusted refund status query + refund_key semantics + eligible amount/window + merchant-funded balance, refund event audit, finance approval policy, safe print/Drive worker compensation/stop, abuse thresholds, testing with nonproduction fixtures, owner acceptance and a distinct production authorization. Refund may require an authorized support workflow when online refund is unavailable; never pretend an unsupported refund request succeeded.

## 8. Versioning, precedence, and implementation matrix

| Existing historical text | New-order resolution | Legacy treatment |
| --- | --- | --- |
| "No automatic refund under any circumstances" | **Superseded** by *verified irrecoverable merchant failure -> refund-first candidate* with provider/worker/legal gates | Remains historical/current source behavior; no existing code refund |
| "Lost/ignored genuinely offered ticket forfeits self-service recovery" | **Still APPROVED**; no automatic refund merely for lost proof and no tokenless media access | Remains protected |
| "Money forfeited even if Meong caused non-delivery" | **Never approved**; independent service failure must be evaluated, legal rights preserved | Not authorized |
| "Refund on every error or after fixed timer" | **Rejected**; settle + irrecoverability + idempotent provider + safety evidence required | No automatic refunds |
| "Print receipt failure triggers ticket screen" | **Superseded** in new order: screen ALWAYS + concurrent one-time paper regardless of printer result | Legacy original paid-first flow remains historical |
| "Midtrans POS refund API available by default" | **False / UNVERIFIED**: require account-specific activation and channel testing | All historical merchant capability unknown |
| "Refunded == booth safe to admit B" | **Rejected**: print/camera/Drive release and backend ACK independently required | Old AR/UAH handoff unchanged |
| "Provider accepted refund == funds received" | **Rejected**: distinct request/processing/provider-confirmed/cash-visible statuses | No legacy refund code |

**Refund support does not supersede mandatory Recovery Ticket screen + concurrently printed same token, frozen multi-design quote, 3+1 retake/template, active-only QR1–3, late-PAID/CCP, Drive verified URL, offline capture, print UNCERTAIN no-replay, security vault, privacy fencing, photo-retention policy, Meong Fly one-use promo rules or original legacy paid-capture recovery.** These are all separately maintained in the [complete owner-decision ledger](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md).

**Status at writing:** policy recorded, all new refund QA **NOT_RUN**, source unchanged, merchant refund API not proven available, no real refund issued.

## 2 November 2026 — Software-only refund assessment supplement (NOT merchant activation)

`photobooth/post_preview_refund_assessment.py` introduces the initial pure PP-06R1 **nonbinding evidence classifier** and ten offline regression cases. It returns candidate classifications but **cannot issue a refund** (`can_issue_refund=False`), never contacts Midtrans, changes SQL, invents refund keys, prints, changes customer rights or triggers public upload. The original independently verified charge and any separately verified excess attempts must match exact merchant/IDR amount and have distinct provider references. Potential full refund requires permanent merchant failure, PAID/OWED, quiescent workers and no ambiguous paper/public upload. Lost genuinely offered proof alone cannot trigger an auto-refund. **Actual merchant API refund integration and legal/commercial activation remain UNVERIFIED/BLOCKED**, pending separate approved implementation and safe end-to-end contract checks. This supplements rather than supersedes RF-D01–RF-D26.
