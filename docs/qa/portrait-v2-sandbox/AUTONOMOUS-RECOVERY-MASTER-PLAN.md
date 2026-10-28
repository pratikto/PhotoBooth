# Autonomous QRIS and photo-session recovery — master engineering specification

**Status: APPROVED DESIGN DIRECTION / NOT YET IMPLEMENTED**  
**Owner direction:** 28 October 2026; unattended-first, customer-safe, no reduction of existing functionality  
**Development branch:** `feature/portrait-kiosk-v2-next`, no new branch or master merge  
**Audited code baseline:** `2e5efe5d281a93fe8d22e53309a50147764d2939`  
**Implementation authority:** Planning only; staged code work must follow [the roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md), repository rules and separately tested source checkpoints.

## Navigation and order of precedence

1. [Codex execution roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md): dependency-ordered implementable increments.
2. [Provider evidence and verified Midtrans contract](MIDTRANS-PROVIDER-CONTRACT.md): official sources, corrected idempotency caveat and open questions.
3. [Fault-injection and acceptance matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md): mandatory deterministic and on-device gates.
4. [Operational recovery and privacy runbook](AUTONOMOUS-RECOVERY-OPERATIONS.md): customer, operator, offline and incident handling.
5. Original [operator recovery scope](RECOVERY.md), [Sandbox runbook](README.md), [existing FEAT-009 watchdog](../portrait-v2-recovery/README.md), [technical design](../../portrait-kiosk-v2-technical-design.md), [AGENTS](../../../AGENTS.md) and [protocol](../../DEVELOPMENT_PROTOCOL.md).

The 28 October operator-first `RECOVERY.md` records **already authored backend operator APIs** and historical approval; do not delete, rewrite or pretend that the backend and native GUI are fully integrated. This new master plan specifies a **future target** that avoids requiring operator action when fresh payment, local identity and customer ownership evidence suffice. If any source is inconsistent, preserve existing safety guards and explicitly record the unresolved decision before changing runtime code.

## 1. Mission and nonnegotiable principles

**Business outcome:** A customer using an unattended Meong Photobooth should recover from normal QRIS provider delay, network interruption, crash, restart and partial photo workflow **without an operator** when evidence conclusively identifies the original paid order and original photo session. True uncertainty must remain protected while the kiosk can safely recover usability for subsequent visitors **without erasing the previous customer's paid entitlement**.

**Safety properties:**

- **Never bill twice for an ambiguous first charge.** One immutable checkout key -> provider order ID -> server-side order -> amount/merchant/booth. Never regenerate order identity to mask a timeout.
- **Never consume one grant twice.** Each verified paid order issues no more than one durable fulfillment entitlement; a grant cannot allocate a second photo transaction.
- **Never overwrite an uncommitted photo.** A JPEG exists without its matching durable capture intent/manifest acknowledgment -> hold until independently validated.
- **Never reprint an ambiguous job.** `SENDING`/`UNCERTAIN` remains quarantined pending physical evidence or explicitly approved operational remedy.
- **Never expose old private photos to a new customer.** Verified payment alone is insufficient to prove the person standing at the booth owns the original photo session.
- **Never drop a paid obligation.** Leaving/abandoning a kiosk screen does not cancel an accepted payment or fulfill the customer's service.
- **Never use local UI state as payment authority.** QR render, simulator result, API HTTP code, webhook body alone, stale PAID, recovery button and expired countdown are not independent proof of settlement.
- **Never infer provider failure from outage/404 alone.** Safely hold, reconcile and escalate after bounded retries.
- **Do not extend original photo-retention deadlines on resume.** 15-day local and 30-day Drive policy, verified setup, original clock and deletion remain distinct from recovery.
- **Work with existing code.** Preserve isolated MOCK/default, original v1, approved GUI v2, QRIS Sandbox full-price-only (no trusted game promo), original printer/Drive and QR layout. Sandbox launcher continues printer/Drive OFF.

## 2. As-is audit at the pinned SHA

| Finding | Confirmed current source | Risk / target |
| --- | --- | --- |
| Startup `STARTING`/`STARTED` -> `RECOVERY` and refresh returns old snapshot | `photobooth/qris_session.py` | Dead-end state; add fresh backend reconciliation while preserving original phase/identity |
| Native Sandbox recovery phase has no actions or automatic status polling | `photobooth/kiosk_v2/sandbox_views.py` | Stalled kiosk; safe auto worker, progress UI and restricted fallback |
| Operator inspect/resolve require an 8-digit backend PIN | `qris_api.py`, `checkout_backend.py`, `checkout_store.py`, `qris_kiosk_client.py` | Existing security seam retained; auto-read/auto-resume must use narrower capabilities, never a public operator bypass |
| Launcher does not yet wire operator PIN to child + GUI | `tools/run_qris_sandbox.py`, `tools/run_portrait_v2_sandbox.py` | Complete separate backend/operator integration without leaking merchant credentials |
| Order inserted locally before provider charge | `checkout_store.py` + `checkout_backend.py` | Crash or timeout **before** charge accepted may strand a CREATED order; provider contract for safe same-order resubmission remains unverified |
| Existing `status()` refreshes provider mainly for CREATED/PENDING | `checkout_backend.py` | Before any new recovery entitlement, demand fresh verified evidence even when local PAID was cached |
| JPEG file replace and manifest acknowledgment occur separately | `transaction_store.py` | Crash window leaves orphan or rewrite; use intent, unique capture operation IDs, immutable/orphan quarantine |
| Active photo workflow held in memory | `kiosk_v2/photos.py` + `workflow.py` | Durable reconstruction for per-design 3 initial shots, retake quota, review/output and multi-design progression |
| Existing watchkeeper observes and holds, `Restart=no` | `kiosk_v2/watchdog.py` | Later bounded restart only after business safety predicate; no speculative auto-replay |
| Local photo expiry can run while sessions are abandoned | `retention.py` | Correct policy; recovery must not resuscitate expired photos |
| Local Sandbox loopback cannot accept public Midtrans webhook | `run_qris_sandbox.py` and official Midtrans docs | Local polling first; future HTTPS backend with durable authenticated webhook inbox |
| Backend can `abandon` and close a paid visit while payment remains PAID | `checkout_store.py` | Paid but unfulfilled liability must remain independently tracked and visible to operator/customer |

No actual Midtrans merchant, paper, Windows device, Ubuntu device, remote refund or cloud deletion evidence was generated by this design audit. Do not mark any test passed.

## 3. Three-ledger architecture and boundaries

### A. Payment ledger (backend authority)

Immutable `payment_order_id`, `checkout_key`, `booth_id`, `merchant_id`, frozen monetary quote/fingerprint, provider transaction ID, normalized provider state, proof timestamps, verification source, provider evidence digest/validated fields, expiry and cancellation outcome. Persist a provider request attempt journal `REQUEST_PREPARED -> SENT/UNKNOWN -> VERIFIED/TERMINAL`. A provider timeout is UNKNOWN, **not FAILED**. Reject identity mismatch and maintain monotonic financial entitlement; later verified refunds/reviews trigger a distinct incident without deleting historical service records.

### B. Fulfillment ledger (single-use, durable)

One `fulfillment_id` per paid order, one authenticated reusable grant, frozen template IDs/versions/copies, one fixed local photo transaction ID, required steps, entitlement state, actual capture statuses, retake quotas, output/print/upload status and final service acknowledgment. Local and backend checkpoints form a retry-safe saga: `RESERVED -> ALLOCATION_INTENT -> ALLOCATED -> CAPTURING -> REVIEW -> COMPOSED -> COMPLETING -> FULFILLED`, with separate `SUSPENDED`/`DISPUTED`/`REMEDY_PENDING` states. Do not conflate `COMPOSED` with `FULFILLED`: printed copies, cloud delivery and other contracted obligations must be evaluated separately before final fulfilled acknowledgment.

### C. Kiosk/customer session (ephemeral presentation)

An active `ui_visit_id` controls touchscreen/camera permission, view revision, countdown, audio and capture. It may be released only by a server-acknowledged safe separation from its payment/fulfillment identities. Pending customer claim or uncertain financial entitlement must persist when the UI returns to advertising. One camera owner/one active local fulfillment lease; never leak previous customer artifacts into default page.

### Durable identity constraints

Unique composite `(merchant_id, booth_id, checkout_key)`; unique `provider_order_id` and provider transaction reference; unique `fulfillment_id` per payment; unique `photo_transaction_id` per fulfillment and vice versa; unique `capture_operation_id` per session index/slot/attempt; unique `print_job_id` for frozen output/copies; immutable correlation of service grant to original order. Use SQLite transactions, unique indexes/CAS compare-and-swap and OS process leases; no bare UI booleans authorize effects. Define a schema migration and backward-readable journal plan; no deletion/migration of the `old` archive.

## 4. Explicit recovery state models

### Payment creation

`NEW -> CREATE_PREPARED (durable order/key/fingerprint) -> CREATE_SENT -> VERIFYING -> PENDING/PAID/TERMINAL`, with `CREATE_UNCERTAIN` for network loss. On uncertain creation: GET status same order, observe provider propagation, bounded retry and no new order ID; check official Midtrans support before repeating charge with the same order ID or adding provider idempotency headers. If no proof, hold and issue customer recovery claim; never call a missing object settled or failed.

### Payment reconciliation

`PENDING`: same QR and order until trustworthy terminal evidence; restrained polling, webhook if enabled, expiry checked with provider.  
`PAID`: verify fresh provider state and immutable identity before first/resumed entitlement; reconcile existing grant, never issue a different one.  
`EXPIRED/FAILED/CANCELLED`: only trusted provider confirmation plus required local closure criteria frees a new payment attempt.  
`REVIEW_REQUIRED/REFUND/PARTIAL_REFUND`: deny new photo admission, preserve evidence and owed remedies.  
`OFFLINE/UNKNOWN`: hold financial uncertainty, preserve identity and schedule bounded retries with jitter; never display a false success/failure.

### Fulfillment transitions on restart

1. No local allocation and **proven no prior intent**: resume original permitted consent and safely allocate exactly once using idempotent operation.
2. Allocation intent exists but photo ID missing: recover from unique persisted allocation mapping/claim and manifest; if still ambiguous **hold**, never allocate a second by default.
3. Local transaction exists and exact backend grant/order binding agrees: reconstruct exact session, count and quota from validated manifest and files.
4. Prior capture file exists without matching manifest entry: orphan checkpoint; quarantine evidence, do not overwrite. Only deterministic identity/hash validation and safe adoption may advance.
5. Three shots or review ready: validate the same three originals, retake choice and quota; expose only after customer ownership proof; manual capture countdown on any new photo.
6. Composed strip with uncertain backend `COMPLETED`: reconcile with the same service state; do not regenerate/print/upload as side effects of status check. Explicit immutable output identity.
7. Print already `SENDING` or `UNCERTAIN`: never auto-resend; preserve paper evidence and offer separate remedy/operational handling.
8. Multiple designs: restore completed designs, copy quantities, current design, remaining capture and retake quotas; no duplicate first design when resuming later design.
9. Local bytes expired/missing/corrupt: do not fabricate a restored session; keep paid-unfulfilled remedy path.

### State ownership and parallelism

One writer per journal, one in-flight provider create/status/resolve per order, one capture consumer per fulfillment, one job per print fulfillment. The operator resolution API is not an unrestricted background job. Async native callback must check current `visit_id`, journal generation/revision, lease and expected stage. Treat stale callbacks and repeated user taps as no-ops returning recorded results.

## 5. Customer recovery proof and privacy

**Decision proposal, not currently implemented:** Issue a recovery credential as early as durable order creation, before/at payment when possible. Provide high-entropy secret as QR/secure URL or equivalent capability, optionally accompanied by a short customer reference number **that alone cannot grant access**. Hash tokens at rest, constrain booth/order/expiry/one-time consume and invalidate on verified completion/remedy. Avoid putting raw token, keys, photos or payment metadata in logs/analytics; require TLS for remote redemption.

On restart: automatically reconcile financial state **in private**. Do not automatically display old photos or start camera. Show a neutral page such as `SESI SEBELUMNYA DITEMUKAN` and ask for original token/adequate ownership proof before showing personal photos, retake controls or continuing. Resume countdown only after fresh customer action. A new passerby cannot obtain prior customer photos by pressing `LANJUTKAN`.

If owner leaves, transfer an **authenticated, durably suspended** claim to the fulfillment service and release camera/UI lease only when verified safe. Define default claim timeout, off-booth redemption and privacy retention policy before production; avoid blindly freeing a booth from a payment still unknown to provider. A ticket does not guarantee all original customer capture steps can be resumed on a different physical booth without verified media transfer; scope same-booth first.

## 6. Device readiness and failure after settlement

Before payment: perform **pre-payment health gate** for camera availability/fresh frame, disk capacity and writable state, template/render readiness, relevant device permits, and printer if printing is part of the purchase. Drive health must follow established offline reserve and retention contract: offline upload itself is not necessarily blocking if already approved; a missing verified customer link may be. Avoid declaring provider API reachability as proof of camera readiness.

After PAID: camera/storage/printer can still fail. Mark entitlement `PAID_UNFULFILLED` or `SUSPENDED_RECOVERABLE`, offer delayed continuation and customer claim, maintain a clear remedy/compensation ledger with ticket/notification capability. Never automatically refund without approved Midtrans merchant support and operational policy, nor falsely mark paid orders cancelled.

Health probes have freshness and degraded states; no blocking Kivy UI thread, hidden external operations or duplicate camera handles.

## 7. Provider retries, hooks and status policies

- Official MIDTRANS constraints and documentation caveats: [provider contract](MIDTRANS-PROVIDER-CONTRACT.md).
- Sandbox loopback: use backend GET status after restart and every ~10 seconds while awaiting payment; propose on errors 10/20/40/60s capped backoff with jitter and bounded calls. These numbers are product defaults proposed for validation, **not provider SLA**. Immediate single refresh on network restoration and webhook receipt; stop normal polling after settled but require fresh check before sensitive recovery decisions.
- Future public backend: HTTPS webhook, verified signed input, durable inbox, quick 2xx only after durable acceptance, idempotent reconciliation workers, out-of-order evidence protection and event auditing. No exposure of local database, PIN or merchant key to customer GUI.
- Multiple instances: per-booth fencing token and generation, durable leases with expiration/fencing, exactly-one logical writer. Process locks alone are not enough for tablet + mini PC or a remote backend.
- Backpressure: keep bounded queue, health metrics and per-order rate budgets; manual operator actions restricted and audited.
- Status `PAID` in an old database is **not** permission to infer current provider state for a newly resumed operation.

## 8. Operator/admin exception workflow

Operator is last resort for inconclusive payment, identity mismatch, damaged files, unresolved created charge, refund/partial refund, uncertain print, inconsistent backend/grant, device hardware loss or retention-expired media. Existing audited `recovery/inspect`/`resolve` endpoints use booth auth and separate local operator PIN. Complete native/launcher integration later without sharing the PIN with customer GUI. For production replace ephemeral local PIN with appropriately protected, rate-limited authenticated operator action; audit principal, order, reason, decision ID, old/new states, timestamps and outcome. Never print credentials in logs; avoid placing secret in process argv.

**Important:** existing Sandbox `abandon` sets `closed=1` but does **not** refund, cancel or complete a paid order. New design must prohibit treating `closed=1` as `LIABILITY_SATISFIED`. Log unresolved paid claims to an operator reconciliation queue. Manual `abandon` is an archival/disposition action with traceable reason, not a customer refund or right to erase photos.

## 9. GUI states and semantics

- `MENGHUBUNGKAN ULANG...` / RECONNECTING: background attempts only, never unlock.
- `MEMERIKSA PEMBAYARAN...` / VERIFYING: fresh provider check, preserve old order.
- `MEMULIHKAN SESI FOTO...` / RECOVERING: local manifests and backend grant checked.
- `SESI SEBELUMNYA DITEMUKAN` / CLAIM_REQUIRED: neutral; request ownership token, reveal no private artifacts.
- `LANJUTKAN SESI FOTO` / RESUME_READY: only after verified payment, manifest and customer claim. Camera still requires manual countdown.
- `BELUM BISA DIPASTIKAN` / RETRYING: reconnect, show safe status and claim instructions; never new charge.
- `SESI DISIMPAN UNTUK PEMULIHAN` / SUSPENDED: customer can leave with secure claim; kiosk released only after durable acknowledgement.
- `BANTUAN TERBATAS DIPERLUKAN` / OPERATOR_REQUIRED: specific redacted reason and authenticated escalation.
- `SELESAI` / CLOSED: payment/service/print/Drive fulfillment checkpoints and retention semantics accurate, not mere composition.

Render both portrait targets 800×1280 and 452×900; honor app suspend/minimize, input revision, screen readers/contrast/QR scanning and no spinner-only permanent dead end. Do not invent support contact or claim delivery/refund without proof.

## 10. Security, privacy and resilience safeguards

- Confidential merchant server key solely in backend process; immutable Sandbox host, no redirects, strict response schema and URL allowlist.
- Separate customer capability from booth bearer, operator PIN and provider credentials. Short numeric display reference is **not** an authentication secret.
- QRIS payment code and Google Drive download code are different objects; QR branding may never alter decoded payload.
- Redact keys, auth headers, PINs, recovery capability tokens, signed URLs and private photos from evidence and telemetry.
- Validate paths against traversal/symlinks/junctions, `old` archive, cross-booth folders and oversized/corrupt files. Do not search newest folder to infer visit ownership.
- Encrypt sensitive local storage or implement OS access controls and encrypted backups as appropriate to deployment; measure boot recovery and disk integrity.
- Freeze quote/template/copies; store template version/content hash so later catalog changes do not reprice or silently recomposite past paid orders.
- Keep monotonic and wall clocks separate. Persist provider expiry/UTC retention dates; detect clock rollback/skew. Recovery cannot renew retention.
- Preserve evidence for disputes but apply documented retention/redaction and data deletion policies; photo retention and financial evidence retention have different requirements.
- Maintain audit log for every external effect, state transition, operator decision, exception and customer claim redemption. Avoid logging full PII/provider payload.

## 11. Explicit non-goals and future decisions

Not authorized by this documentation: production Midtrans activation, BI-SNAP migration, refund automation, direct customer SMS/WhatsApp, customer identity recognition, paid reprints, new physical service worker, automatic watchdog kill/restart, cloud retention deployment, printer/Drive on Sandbox, trusted game discount, new branch, merge/default switch/release, historical data deletion, reset of payment identifiers or opening local servers publicly. Future production acceptance must separately resolve merchant-of-record, contractual remedy, consent, support escalation, refund/consumer and privacy requirements.

## 12. Definition of success

1. Every recoverable outage/restart preserves the same order/entitlement and restores permitted customer continuation with no operator after ownership proof.
2. The unrecoverable/ambiguous original claim is durably isolated; future customers can be admitted only when payment/fulfillment/camera leases are safely separated, not after a dangerous reset.
3. Every persisted byte/transaction/grant/print effect survives injected crashes without duplicate billing, capture, retake, output, printing or unauthorized disclosure.
4. All deterministic gates in the [test matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md) pass at exact code SHA; real Sandbox/Windows/Ubuntu/device/provider gates remain independently recorded as PASS/FAIL/SKIP/NOT_RUN.
5. Recovery is observably safe (bounded retries, queue age, overdue liabilities, recovery success rate), and rollback preserves journals and customer rights.

Follow the [roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md) exactly, with one focused logical commit/push at a time and a final complete regression only after final functional change.
