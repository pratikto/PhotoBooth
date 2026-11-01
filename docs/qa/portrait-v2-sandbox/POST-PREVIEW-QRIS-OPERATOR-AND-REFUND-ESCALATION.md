# Post-preview QRIS — unattended operator escalation, refund-first and proof-loss treatment

**Owner decision:** 1 November 2026. **Order version:** NEW post-preview. **Design approved / NOT IMPLEMENTED / NOT TESTED / not merchant-activated.** This is operational classification and customer privacy policy, not authority for a real merchant refund or privileged kiosk reset.

**Authoritative:** [complete every-decision ledger](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) · [RF-D01–26](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) · [financial/security states](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [Midtrans account gates](MIDTRANS-PROVIDER-CONTRACT.md) · [PP-001..112 test matrix](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md).

## 1. Operating priorities

1. **FULL_AUTO** for original QR expiry renewal only for continuing customers; verified provider status, lost create reply reconciliation, safe photo recovery with authentic CCP, safe unclaimed visit isolation, bounded Drive upload retry. No printer/Drive/finance operator if recovered safely.
2. **WAIT/DEFER** when genuine original claimant returns while B owns the booth, provider is temporarily unknown, original ACK delayed, paid Drive upload delayed but URL verified. Protected Advertising doesn't prove a free backend lease. Do NOT preempt B.
3. **REFUND_FIRST_ELIGIBLE** only for independently verified paid service irrecoverably failing after bounded original recovery, exact original payment and paid/owed proof, physical printer/Drive worker fence, merchant active/eligible refund API, original unique refund key. Prefer FULL original payment amount for MVP; excess verified duplicate-settled QRIS only the excess. Money-back automation and physical kiosk repair are separate tasks.
4. **NO_AUTO_REFUND_PROOF_LOST** for customer's loss of genuinely offered CCP/Recovery Ticket as the *only* problem. This is lost self-service recovery, not permission for no-proof photo access, not a blanket legal denial of remedies or an assertion the service was delivered. Evidence that Meong never offered proof, or independently failed photo service, is a separate refund/owed case.
5. **HUMAN_LAST_RESORT** only when financial identity conflicting, printer physical output ambiguous/unsafe, camera/print worker cannot isolate, corrupt media/Drive binding cannot be safely repaired, provider refund unavailable/ineligible or security vault/claim compromised. Only scoped technician/finance/security support, never a universal operator PIN bypass.

## 2. Operational status labels and actions

| Label | Business meaning | Machine action | Operator/finance scope |
| --- | --- | --- | --- |
| `AUTO_RECOVERING` | Safe original retry in progress | Continue idempotent exact work; no new QR/print | None |
| `WAITING_PROVIDER` | Original PENDING/UNKNOWN or create reply lost | Original status/reconcile; no new paid checkout | Finance only if exhausted conflict |
| `WAITING_CUSTOMER` | Original proof claim awaits free booth | WAIT/DEFER and no B takeover | None |
| `PAID_OWED_DELIVERY` | Paid service temporarily pending | Preserve original grant, verify URL/print/upload truth | None until genuinely irrecoverable |
| `NO_AUTO_REFUND_PROOF_LOST` | Original proof genuinely offered, later lost without separate merchant failure | No no-proof private photo unlock; no refund merely for missing proof | Redacted support for separate verified dispute only |
| `REFUND_ELIGIBLE` | Independent merchant failure/excess settled payment; merchant/safety ready | Freeze original fulfillment, prepare original refund intent | None if truly eligible and activated |
| `REFUND_REQUESTED` | Durable original refund POST sent/accepted | Provider original refund key status tracking | None unless conflict |
| `REFUND_PROCESSING` | Accepted, money not yet provider-confirmed | Honest status reference; no duplicate POST | None |
| `REFUND_CONFIRMED` | Provider independently confirmed refund | Preserve original audit; no old service re-release | None; actual customer balance timing external |
| `REFUND_REVIEW_REQUIRED` | Provider disabled/ineligible/uncertain or disputed order | Financial/support safe review with no invented payment claim | Finance/support |
| `PRINT_INSPECTION_REQUIRED` | Partial paper or SENDING/UNCERTAIN transport | No auto reprint or blind refund, stop new print lane | Onsite operator/technician |
| `DEVICE_MAINTENANCE_REQUIRED` | Camera/printer/disk/power failed | Stop new paid attempts, protect paid obligations | Onsite operator/technician |
| `ISOLATION_HOLD` | Worker, lease or ACK unsafe | Public neutral UI only; no new camera or charge | Backend technician |
| `SECURITY_HOLD` | Compromised secret/forged claim/privacy breach | No private media, token issue or unverified refund | Security/admin |
| `ADS_PROTECTED` | Public Ads while original resources not FREE | Hide old media; reject B's paid entry | No automatic operator needed unless exhausted |

## 3. Exact exception-to-remedy matrix

| Incident | Safe unattended response | Refund? | Human intervention threshold |
| --- | --- | --- | --- |
| QR1/QR2 verified expired unpaid and A still active | QR2/QR3 on same frozen original only | No | None |
| A explicitly cancels or abandons PENDING order | Persist intent, original cancel/GET reconciliation, fence | No refund until independent actual PAID + new failure evidence | Provider cannot reconcile safely |
| PAID but QRIS provider status inconsistent | Financial hold, fresh independent merchant/backend status | No unverified refund | Finance |
| Ticket receipt fails; same original ticket QR/full code was genuinely onscreen 30s and paid printing can finish | Screen always existed; no duplicate ticket; fulfill strips | No refund merely for paper-ticket failure | Hardware if strips cannot print |
| Printer cannot fulfill purchased strips at all, safely quiescent and provider API enabled | Document exact defect/amount, refund-first full amount | Yes, when independently verified eligible | Technician still fixes printer for future use |
| Printer partial physical paper, uncertain dispatch or duplicate strips | Quarantine original print jobs, record possible delivered copies | Not blindly; conditional full goodwill after evidence and safe handling | Onsite physical reviewer if ambiguity |
| Drive exact customer link or private media irrecoverable after PAID | Idempotent bounded retry/owed, then refund eligibility | Full original if verified and safe | Cloud tech on recurring outage |
| Both QRIS1/2 paid, same logical order | One service only, unambiguous excess original charge refund | Excess charge only | Finance if amount/merchant differs |
| A left, later PAID; B uses booth | PAID_UNCLAIMED; no B photo/ticket, WAIT for A CCP | No auto-refund solely for leaving | None for normal wait |
| A lost genuinely offered ticket/CCP, no proof and no separate merchant failure | Reject media restoration without original capability | **NO_AUTO_REFUND_PROOF_LOST** | Support only for independent legitimate complaint |
| A says proof lost, but screen never really displayed (app fault) | PAID/OWED; no customer blame | Refund only for independently irrecoverable service; remedy otherwise | Support if unable to resolve |
| Vault compromised, forged QR, ownership unproven | Contain and audit; no photo exposure | No automatic money movement | Security/admin |
| Isolation/ACK failed after payment refunded | Still ADS_PROTECTED; refund not a release ACK | Financial refund does not free hardware | Technician |

## 4. Customer-visible policy: brief, accurate and not misleading

- **Mandatory paid ticket screen (always):** “SIMPAN RECOVERY TICKET. Kode yang sama juga sedang dicetak. Tiket ini diperlukan jika sesi perlu dipulihkan.” Show original QR/full code for 30 genuinely visible seconds with NEXT, independent of receipt printing.
- **Customer genuinely lost ticket:** “Tiket pemulihan tidak tersedia. Demi keamanan, foto lama tidak dapat dibuka tanpa bukti yang sah. Kehilangan tiket saja tidak diproses sebagai refund otomatis. Jika ada kegagalan layanan lain, gunakan jalur bantuan yang tersedia.”
- **Service failure under eligibility review:** “Layanan belum berhasil diselesaikan. Kami sedang memeriksa status pembayaran dan opsi penyelesaiannya.” Do not promise actual refund before request accepted.
- **Refund provider accepted:** “Permintaan refund telah diajukan. Dana masih diproses oleh penyedia pembayaran.” Do not claim funds have reached user's wallet.
- **Refund provider independently confirmed:** “Refund dikonfirmasi penyedia pembayaran. Waktu dana terlihat di saldo dapat berbeda.”
- **Provider refund unavailable/rejected/unknown:** “Pengembalian dana otomatis belum dapat diproses. Kasus ini tercatat untuk penanganan lanjutan.”

No public order-number proof, fake customer-service phone, fixed SLA, arbitrary user-entered payment destination, printed paper proof derived only from SUBMITTED, or secret/photo logs. Consumer law / merchant policy review required before any public money-forfeiture terms.

## 5. Unattended failure-to-refund diagram

~~~mermaid
flowchart TD
    E([Exception occurs]) --> A{Can original operation recover safely?}
    A -->|Yes| AUTO[Same original idempotent retry, no operator]
    A -->|Temporarily unknown| WAIT[WAIT/DEFER, original provider/worker hold]
    A -->|No, paid service irrecoverable| D{Reason and authentic evidence?}
    D -->|Genuinely lost ticket alone| LOSS[NO_AUTO_REFUND_PROOF_LOST + no private photo unlock]
    D -->|Forged/uncertain payment or worker| REVIEW[Security / finance / technician hold]
    D -->|Verified merchant failure| F{Safe paper/media fence and merchant refund enabled?}
    F -->|No| REVIEW
    F -->|Yes| R[Original idempotent refund intent/key and provider request]
    R --> STATUS{Refund provider outcome?}
    STATUS -->|Accepted/processing| PROCESS[Track, do not claim funds received]
    STATUS -->|Confirmed| DONE[Record refund; separate kiosk hardware release]
    STATUS -->|Unknown| POLL[Reconcile same refund key, no repeated POST]
    POLL --> STATUS
    STATUS -->|Rejected| REVIEW
~~~

**The operator does not approve a ticket-free photo release merely to resolve a lost-proof complaint.** Nor does automatic refund solve unsafe isolation; both responsibilities are independent.

## 6. Status and scope

This is a design-level operations table, not a working dashboard, refund API, actual provider test or financial/legal production policy. **ALL new PP-001..112 acceptance cases NOT_RUN**; physical POS80, Windows/Ubuntu, Midtrans merchant and Drive/security gates open. Historical parent AR/UAH design, original prepaid orders and previous company roles are unaffected. Future work depends on owner-approved PP-06R implementation and actual merchant eligibility.
