# Autonomous recovery — customer, operator and deployment runbook

**Current implementation update, 29 October:** source progressed through AR-09.c1;
[exact commits/tests and unfinished work](CONTINUATION-2026-10-29.md).
Dated design-only/audited-baseline statements below are historical scope; they do
not override current implementation evidence or certify full matrix/device/
production acceptance. Safe release, AR-10–13 and external gates remain pending.

**Status:** DESIGN-ONLY / NOT DEPLOYED, 28 October 2026  
**Source audit:** `2e5efe5d281a93fe8d22e53309a50147764d2939`  
**Links:** [Master](AUTONOMOUS-RECOVERY-MASTER-PLAN.md) · [Roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md) · [Midtrans sources](MIDTRANS-PROVIDER-CONTRACT.md) · [Tests](AUTONOMOUS-RECOVERY-TEST-MATRIX.md)

The procedures below describe the **target future design**; they are not instructions to run nonexistent recovery UI buttons or API paths in the present app. Current actual Sandbox recovery remains operator-held and the native operator integration is incomplete. Never reset journals, erase customer photos or invent Midtrans outcomes to unblock a stalled Sandbox.

## 1. Intended customer journeys

**Normal pending payment:** Visitor selects template -> health gate -> confirmed immutable server quote -> order created once -> QR shown -> poll about every ten seconds / webhook if approved -> fresh provider settlement -> grant once -> customer consents -> exactly three initial photos per design -> optional one retake -> composition -> approved printing/Drive tasks -> separate service acknowledgments -> return to ads. Sandbox: only official simulator, and print/Drive **off**; game demo discount not applied.

**App restart before payment completion:** Persistent checkout key/order recovered; do not generate new order ID. GUI shows neutral `MEMERIKSA PEMBAYARAN` and pending QR if still valid. Provider unavailable -> saved order, retry, customer claim. Expired/cancelled confirmed -> close safely; ambiguous charge -> do not offer fresh payment.

**App restart after verified payment:** Backend checks settlement and unique grant; local photo transaction and manifest reconciled; GUI shows neutral claim page, no old thumbnails. Customer uses secure original recovery capability; resume same photo flow at exact checkpoint and manual shutter countdown. If completion proven -> display receipt/result only to original customer. No operator for conclusive safe case.

**App loses connectivity after payment:** Keep paid entitlement and display redacted retry/claim. If independent evidence cannot be obtained, don't capture or close; allow supervised safe suspension of the old session when backed by unique durable claim and fulfilled restrictions. Connection restoration triggers one bounded reconciliation.

**Customer leaves mid-session:** Do not discard grants or photos. After secure suspension, record claim state and release kiosk lease safely. If no ownership mechanism exists, do not auto-expose existing photos to subsequent visitor. A new customer cannot access or resume old session with a plain 'continue' press.

**Device fails after payment:** Mark a paid-unfulfilled obligation. Customer receives secure claim and a truthful service/compensation path. Never claim payment was refunded or charge again merely because camera/printer/storage failed. Operating staff handle genuine device faults asynchronously under approved policy.

## 2. Intended recovery decision matrix

| Evidence available | Customer screen | Automatic action | Escalation |
| --- | --- | --- | --- |
| Frozen order, pending, valid QR, network healthy | Menunggu pembayaran | Same QR, restrained status polls | None |
| Frozen order, provider creation unknown | Memeriksa transaksi | Same-order status checks/backoff | Operator if provider ambiguity persists; no replacement |
| Provider freshly verified PAID, no photo allocation | Sesi ditemukan, claim required | Reuse one permit | Customer proof; no operator if conclusive |
| Paid + exact valid manifest / partial capture | Sesi ditemukan, claim required | Restore progress, preserve retake | Customer proof and manual countdown |
| Paid + safe completed result, verified service state | Sesi selesai, claim required | Show original result privately | Never auto-print |
| Internet offline / provider unavailable | Mencoba menyambung | Hold old identity, bounded retry, safe claim | Operator if irreversible unresolved state |
| Explicit verified expire/cancel/fail before paid fulfillment | Pesanan ditutup | Close same visit and free new checkout safely | None |
| Refund/review/identity mismatch | Perlu pemeriksaan terbatas | No new service grant, preserve evidence | Authenticated operator |
| Orphan/ambiguous/corrupt photo manifest | Sesi perlu pemeriksaan | Quarantine, never overwrite | Authenticated operator |
| Printer send uncertain | Cetak perlu pemeriksaan | Do not spool same job | Separate physical-paper inspection |
| Paid but camera/storage permanently unavailable | Layanan tertunda | Preserve entitlement and claim/remedy | Customer support/operations |

Never equate provider `200` HTTP/API status with verified QRIS settlement or local `COMPLETED` with verified physical printing/cloud delivery.

## 3. Sandbox operator incident handling — current version

When the current v2 GUI shows `PERLU BANTUAN OPERATOR` and no actions, it is a **known unintegrated recovery state at the audited SHA**. Do **not** alter `visit.json`, `orders.sqlite`, `counter.json`, `manifest.json`, PIN, booth ID, folders or provider transaction; do not delete/copy/recreate a profile to clear it. Preserve original evidence and time. Use the official Sandbox simulator only; never use banking/e-wallet for test payment.

Record, with secrets redacted: local git SHA/dirty state, kiosk OS, launch command, booth profile (redacted where appropriate), exact failure step, provider order ID only in trusted private operational record, current GUI screenshot, sanitized relevant error, latest status source/time and availability of original photo manifest. A source-based response must be distinguished from a verified live provider response. Never paste server key, booth auth token, recovery PIN, customer capability or original customer images into external bug reports.

Backend recovery API built at `2e5efe5` requires separate operator credential but native launcher/UI integration remained pending. Running `python tools/run_portrait_v2_sandbox.py` may show the same hold; this document alone does not fix the runtime. An operator-controlled disposition cannot be treated as a refund or a completed paid service.

## 4. Operator control levels for the planned product

- **Customer self-service:** verify claim token, view own photos/continue one original permit, request safe suspension and truthful status. No provider/admin action, no data deletion.
- **Automatic recovery worker:** authenticated private booth/server, read current provider evidence, reconcile unique orders and validated local intents, retry bounded safe/idempotent transitions. Cannot override mismatch, bypass privacy or trigger unbounded print/charge.
- **On-site operator:** authenticate separately, inspect redacted exact state, resolve safe cases after checks, perform paper/device inspection, create support ticket/compensation request. Cannot fabricate PAID/COMPLETED or silently delete old obligations.
- **Remote administrator (future):** secure role-based access with account identity, audit, reason, privileged multi-factor controls where appropriate, strongly isolated merchant secrets. No unauthenticated public reset page.
- **Financial remedy reviewer (future):** handles payment accepted but service unavailable, refund/compensation only via supported Midtrans channel and business policy; a local kiosk operator cannot impersonate a Midtrans refund.

## 5. Safe kiosk release and concurrency

Proposed separation: keep financial entitlement `SUSPENDED_RECOVERABLE`, record encrypted/hashed customer claim and expiry, flush manifest and fulfillment state, obtain backend acknowledgment and release photo/camera lease by fenced generation. Only then let kiosk return to ads/new purchase. Do not allow a second visitor while original camera ownership is ambiguous. Lost ack -> re-query action identity, no blind re-execution. A second process with old fencing generation has no authority to write media, consume grants or print.

If a customer returns to same booth, validate the claim and original entitlement's state/retention before reacquiring camera. If the booth is busy with another visitor, wait or hand off a service ticket; do not preempt or show old photos.

## 6. Monitoring, service levels and incident response

**Proposed telemetry (no PII/photo/secret in metrics):**
- unresolved provider create attempts by age and booth;
- payment pending beyond expected expiry;
- PAID_UNFULFILLED count, age and operator resolution;
- successful self-service recovery / attempted recovery ratio;
- time from provider settlement to confirmed service start;
- local capture orphan/conflicting manifest count;
- lost acknowledgment retry count and dedup/replay prevention events;
- unknown/uncertain print jobs and Drive failures;
- camera/disk readiness, watchdog health and restart frequency;
- payment and fulfillment state drift, signed callback backlog and stale provider verification time.

**Suggested alerts:** immediate on P0 customer privacy leak, double charge, double fulfillment, file overwrite, missing paid liability or exposure of secrets; high priority on stuck paid fulfillment and repeated kiosk crash; periodic review for unknown creation and ageing claims. Alert channels, numerical SLOs, contact/on-call ownership and merchant remedy SLA are **OPEN OPERATING DECISIONS** and must not be invented.

## 7. Fallback and compensation policy before commercial launch

Define supported choices: original self-service resume, alternative scheduled booth service, customer-service investigation, provider-supported merchant refund, or contractually approved compensation. Record eligibility, immutable evidence, approval responsibility, merchant-of-record and legally required timelines **before** promising them in GUI. A local kiosk 'cancel' means ending the screen interaction only when financial rights are preserved. No automatic refund or erasure is authorized.

## 8. Security and privacy operations

Secure QR recovery credential: high entropy, hashed at rest, short-lived according to approved privacy/business policy, rate-limited redemption, no bare six-digit access to images. Keep only necessary financial evidence in audit and enforce image retention 15 days local/30 days Drive; actual Google deletion is still gated by BUG-009 acceptance. Claims may outlive image bytes as entitlement/remedy metadata, but must not resurrect expired photos. A scan of customer ticket does not authorize production payment or merchant secrets.

Use HTTPS for any non-loopback GUI/backend, verify Midtrans webhook SHA-512 signature and independently query current status when needed; ensure strict host allowlist, no redirects with credentials, secret rotation/rollback and write access controls for local SQLite/storage.

## 9. Operator acceptance checklist (future)

- [ ] Local Sandbox actual simulator successful; separate NOT_RUN/provider evidence before then
- [ ] Old customer photos remain hidden at boot and from new user
- [ ] One paid permit reuses original bound transaction after interruption
- [ ] No duplicate capture/retake/print/Drive job from restart
- [ ] Camera/storage readiness checked before charge; post-paid fault retains claim
- [ ] Uncertain created order does not create a second charge
- [ ] Operator authentication and audit work without exposing PIN
- [ ] Safe suspension can release kiosk only after durable server acknowledgment
- [ ] Windows actual crash/restart validated
- [ ] Ubuntu graphical session/service/hardware validated separately
- [ ] 800×1280 and 452×900 native controls and QR decode validated
- [ ] Provider callback/refund support and production API decision verified before production
- [ ] Full fault-injection matrix and existing affected regressions PASS at exact SHA

## 10. Rollback

Rollback is scoped source inverse commits on the existing branch after inspecting the exact implementation. Never down-migrate or delete customer ledgers to fix a bug; preserve grants, manifests, photo originals, retakes, output, print/Drive claim state and operator action audit. Disable only new unsafe automation paths behind explicit configuration, keep read-only reconciliation where safe, then investigate and fix with deterministic source tests. Production rollback requires an approved data migration/reconciliation plan and a provider-independent financial audit.

## 11. Codex deployment handoff

For each actual stage record the exact GitHub commit, commands, PASS/FAIL/SKIP/NOT_RUN matrix IDs, platform, provider/account source and approved release action. New docs mean **implementation is not started**. No deployment to Midtrans, Cloud, Google Drive or physical devices is implied by documentation publication.
