# Midtrans QRIS provider contract and research register

**Document status:** DESIGN REFERENCE / RESEARCH; not implementation proof or provider certification  
**Date:** 28 October 2026 (Asia/Jakarta)  
**Repository scope:** `pratikto/PhotoBooth`, `feature/portrait-kiosk-v2-next`  
**Source-code audit baseline:** `2e5efe5d281a93fe8d22e53309a50147764d2939`  
**Applies to:** existing isolated Legacy Core QRIS Sandbox trial and future separately approved production adapter  
**Companion documents:** [Master plan](AUTONOMOUS-RECOVERY-MASTER-PLAN.md) · [Codex roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md) · [Failure-injection matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md) · [Operational runbook](AUTONOMOUS-RECOVERY-OPERATIONS.md)

> This document distinguishes **MIDTRANS DOCUMENTED** behavior, **MEONG DESIGN DECISION**, **CURRENT SOURCE**, and **OPEN VERIFICATION**. Do not turn a hypothesis or sample value into a provider guarantee. Recheck official documentation and actual merchant-account behavior at each integration gate. The earlier operator-first [RECOVERY.md](RECOVERY.md) remains a historical implementation/scope record; this package defines the future unattended-first target.

## 1. Official source register (checked 28 October 2026)

| ID | Official Midtrans source | Why it matters |
| --- | --- | --- |
| M01 | [GoPay QRIS POS Integration](https://docs.midtrans.com/docs/gopay-qris-pos-integration) | Specifically covers custom POS/software/hardware/IoT, server-side charge, payment QR, notifications, polling, order identity, QRIS expiry and POS refund limits |
| M02 | [Get Transaction Status](https://docs.midtrans.com/reference/get-transaction-status) | Legacy GET `/v2/{order_id OR transaction_id}/status` and fields used to reconcile |
| M03 | [HTTP(S) Notification / Webhooks](https://docs.midtrans.com/docs/https-notification-webhooks) | Public callback reachability, authentication, idempotency, status checking and failure/retry behavior |
| M04 | [Best Practices to Handle Notification](https://docs.midtrans.com/reference/best-practices-to-handle-notification) | Signed callbacks, out-of-order/duplicate delivery, expected notification lag, status reconciliation and prompt acknowledgment |
| M05 | [Charge Transactions](https://docs.midtrans.com/reference/charge-transactions-1) | Legacy `POST /v2/charge` request, QRIS support, metadata and custom expiry |
| M06 | [Technical FAQ](https://docs.midtrans.com/docs/technical-faq) | Notification debugging, localhost limitations, general idempotency-key use cases |
| M07 | [Moving to BI-SNAP-based Core API](https://docs.midtrans.com/reference/moving-to-snap-based-core-api) | Differences in host, credentials, identifiers, idempotency and response statuses; separate future migration |
| M08 | [Create Invoice](https://docs.midtrans.com/reference/create-invoice) | The **invoice-specific** `X-Idempotency-Key` five-minute example, not automatically a Legacy `/v2/charge` guarantee |
| M09 | [GET Status API Requests](https://docs.midtrans.com/docs/get-status-api-requests) | Legacy order/transaction identifier and returned reconciliation fields |

Provider notes below are summaries of those sources, not copied documentation.

## 2. Confirmed provider behavior

### 2.1 Creation, QR display and settlement

- **MIDTRANS DOCUMENTED:** For POS/IoT, the merchant backend invokes `POST /v2/charge` with `payment_type=qris`, unique order ID and amount; the response can include a `generate-qr-code` URL and `qr_string`. A charge creation response with `status_code=201` and `transaction_status=pending` is **not** a paid order (M01, M05).
- **MIDTRANS DOCUMENTED:** The customer/app receipt or a QR image appearing on screen is not payment authority. QRIS fulfillment follows confirmed `transaction_status=settlement` for the correct transaction and valid fraud status (M01, M03, M04).
- **MIDTRANS DOCUMENTED:** If `fraud_status` exists, success requires `accept`; the general webhook guide says it may be ignored when absent. Do not interpret a present `deny`/`challenge` as valid acceptance (M03). QRIS-specific behavior must remain constrained to the verified provider method; do not generalize card `capture` to QRIS.
- **MEONG DESIGN:** Verify merchant ID, order ID, transaction/provider reference, currency IDR, exact integer IDR amount, payment type/acquirer where supported and any fraud field. Reject inconsistent responses or place them in manual review; provider API `status_code` alone cannot release a photo session.

### 2.2 Webhook and GET status

- **MIDTRANS DOCUMENTED:** Midtrans can send notifications late, more than once or out of order. Verify the signature; parse JSON tolerantly to unknown additional fields; use the status API to reconcile actual state and suppress stale events (M03, M04).
- **MIDTRANS DOCUMENTED:** Notification endpoint must be publicly reachable using HTTPS/valid TLS, standard port, and no redirect/auth wall; Midtrans cannot call localhost directly. A tunnel is a **development-only** alternative; no localhost tunnel by itself constitutes production reliability (M03, M06).
- **MIDTRANS DOCUMENTED:** Target a response under approximately five seconds; acknowledge only after receiving and durably accepting the event for processing. Notification delivery can be retried by Midtrans when failures occur (M03, M04). Do not perform slow camera/Drive/printing work inside the callback.
- **MIDTRANS DOCUMENTED:** The POS guide permits periodic Get Status checks if a webhook is not received, with **about 10 seconds** given as a restrained example (M01). This is guidance, not an exact universal rate limit.
- **MEONG DESIGN:** For the current `127.0.0.1` Sandbox backend, no remote webhook arrives without explicit public exposure. Use periodic backend status checks and a fresh reconciliation after restart; implement the public webhook receiver only for a separately deployed HTTPS backend.
- **MEONG DESIGN:** Each webhook is a **signal to reconcile**, never a direct trigger to capture, grant service repeatedly, reprint or upload photos. Ensure idempotent inbox/processing and durable status/event history.

### 2.3 Timeout, expiry and cancellation

- **MIDTRANS DOCUMENTED:** Customer-side failed attempts can leave QRIS `pending`; they do not necessarily create an immediate merchant-side failure event. A standard QRIS expiry can be around 15 minutes, and scheduled expiry can lag (M01).
- **MIDTRANS DOCUMENTED:** The POS guide discourages configured expiry shorter than 15 minutes where reliable scheduler expiry is expected; for immediate termination of a pending order, use cancellation/expiry API and verify the outcome (M01).
- **MEONG DESIGN:** A GUI countdown, timeout, tab closure, lost reply, unavailable status API or apparent QR expiry never proves that payment failed. Keep the old order reference and reconcile.
- **MEONG DESIGN:** On a cancel-versus-settlement race, fresh verified settlement wins for financial entitlement. A late paid notification must stay tied to its original order, never be silently reassigned to a new visitor.

### 2.4 Refund/compensation

- **MIDTRANS DOCUMENTED:** For POS, online refund via API/dashboard is not necessarily enabled by default; consult the Midtrans account contact/support to establish the available process (M01).
- **MEONG DESIGN:** A paid order closed as a kiosk interaction does not extinguish its fulfillment/compensation obligation. Maintain `PAID_UNFULFILLED`/claim history until delivery, approved remedy or verified provider refund. Do not automatically initiate a refund, invent successful refund state or promise an unavailable API.

### 2.5 Idempotency — important correction to earlier planning

- **MIDTRANS DOCUMENTED:** Legacy Core API migration guidance describes an `Idempotency-Key` concept and BI-SNAP `X-EXTERNAL-ID` correlation semantics (M07). The technical FAQ describes retries using the **same** key versus deliberate new attempts using a **different** key (M06).
- **MIDTRANS DOCUMENTED FOR A DIFFERENT ENDPOINT:** The five-minute `X-Idempotency-Key` rule on the **Create Invoice** API (M08) is **not evidence** that Legacy QRIS `POST /v2/charge` has the same exact header, TTL, response replay or 404 behavior. Earlier conversational wording treating five minutes as a general Core QRIS guarantee is superseded by this qualified register.
- **OPEN VERIFICATION — REQUIRED BEFORE IMPLEMENTATION:** Confirm whether this merchant's active Legacy `POST /v2/charge` accepts `Idempotency-Key`, the exact spelling, key scope/TTL, behavior for request-body mismatch, response replay and timeout-before-creation with official reference and controlled Sandbox tests. Treat optional keys as extra protection, not the sole mechanism.
- **MEONG DESIGN (provider-independent):** Persist one internal checkout key, one immutable provider order ID and one immutable request fingerprint before I/O. Use the **same order identity** for safe status recovery. Never send a fresh charge with a new order ID to resolve an ambiguous charge. An inconclusive provider `404/not-found` is not proof of safe replacement.
- **OPEN VERIFICATION:** Document Midtrans behavior for repeat `POST /v2/charge` with the *same order ID* before retrying after an uncertain creation. A repeat charge must be disabled until provider behavior and explicit safe criteria are verified.

### 2.6 Future BI-SNAP migration

- **MIDTRANS DOCUMENTED:** BI-SNAP Core has different hosts, credentials, signature/auth, response status encodings and identity rules; `X-EXTERNAL-ID` is not interchangeable with the legacy order ID (M07).
- **MEONG DESIGN:** Build a provider adapter and a normalized internal payment-evidence contract. Keep the current Sandbox Legacy adapter unchanged until staged replacement is authorized and tested. Any account-specific mandatory migration date, QRIS eligibility and support for the intended merchant require current confirmation; no production access is authorized by this document.

## 3. Source-specific audit against the Meong baseline

| Observed code path | Current behavior at audited SHA | Design gap / safeguard |
| --- | --- | --- |
| `photobooth/midtrans_sandbox.py` | Legacy `/v2/charge`, `/v2/{order}/status`, cancel; fixed Sandbox URL and rejected redirects | No confirmed provider-level charge idempotency handling; do not assert invoice header compatibility |
| `photobooth/checkout_store.py` | Persists order ID and checkout key before provider call; unique checkout key; grants and durable recovery action audit | Distinguish `CREATE_UNCERTAIN` from truly provider-not-created; closure and paid-unfulfilled obligations need independent tracking |
| `photobooth/checkout_backend.py` | Fresh provider read for operator recovery, monotonic paid evidence, signatures for notification | Normal `status()` does not always perform fresh provider read for already-PAID states; new unattended recovery must not rely on a stale cached grant |
| `photobooth/qris_evidence.py` | Validates amount/order/merchant/type/currency/status/ref; verifies SHA-512 notification signature | Reconcile optional fraud-field semantics and provider-specific state mapping; reject identity mismatch |
| `photobooth/qris_api.py` | Authenticated booth APIs, backend-protected operator recovery API and notification handler | Public webhook ingress requires own deployed HTTPS configuration, durable inbox and audit; never open sensitive booth recovery to anonymous clients |
| `photobooth/qris_session.py` | Atomic `visit.json`; restart STARTING/STARTED enters RECOVERY; `refresh` stops there | Need crash-phase/identity recovery without replaying charge/service/photos |
| `photobooth/kiosk_v2/sandbox_views.py` | Manual status button, short polling of some phases; no RECOVERY UI action | Unattended policy, bounded retry, customer proof and privacy-safe held sessions not yet implemented |
| `tools/run_portrait_v2_sandbox.py` | Isolated loopback child backend/GUI; printer and Drive forced off | Operator backend PIN was added to API but not yet wired through launcher/UI at audited SHA |

This table is a **read-only source audit**, not a claim that the defects were reproduced on a live account.

## 4. Provider-facing behavioral invariants

1. No customer service from `pending`, `created`, `unknown`, stale `paid`, invalid signature, amount mismatch or unverified response.
2. Every provider order belongs to one immutable merchant, booth and customer visit; no identity swapping.
3. A retry or delayed webhook cannot create a second entitlement, second camera session or second print submission.
4. Success must be verified by a trusted provider/merchant backend path and the correct order; GUI text does not authorize fulfillment.
5. If the provider cannot be reached, retain payment ambiguity and retry safely; no fabricated `failed`/`paid`.
6. Refund/review/chargeback-like states revoke new entitlement and create a documented incident; they never erase audit evidence or already consumed fulfillment.
7. All external requests have bounded timeouts and allowlisted destinations, keep secrets server-side, redact logs and must not block the Kivy UI thread.
8. Merchant acceptance, actual callback delivery, refund support, production API migration and device behavior are separate **NOT VERIFIED** gates.

## 5. Open provider questions — record evidence, not guesses

| Question | Required evidence / closure |
| --- | --- |
| Does active Legacy QRIS `/v2/charge` support the proposed `Idempotency-Key` header? | Exact official reference plus Sandbox request/response logs with secrets redacted |
| What is the supported safe path for charge timeout before provider creation? | Controlled test: order persisted; no provider object, eventual status/creation resolution; never a new order silently |
| What does Midtrans return on status GET immediately after uncertain charge? | Distinguish propagation delay, not-found, unauthenticated response, terminal and transient outage |
| What are merchant's QRIS expiry and cancellation guarantees? | Dashboard config and controlled simulator/status/cancel race |
| Which refund/void/claim channels are available for merchant POS? | Merchant-specific provider confirmation; approved operational policy |
| Is a live public callback URL/merchant integration supported and configured? | HTTPS hostname, signature verification, dashboard notification history and duplicate/out-of-order tests |
| Is BI-SNAP migration required before launch? | Account-specific Midtrans guidance and acceptance of target adapter |
| What payment/consumer-support obligations apply? | Merchant-of-record, refund/remedy terms and local legal review before monetized launch |

## 6. Safe implementation sequence for Codex

Read this register **before** modifying provider calls. Implement local state durability and simulated uncertain outcomes without assuming new Midtrans headers. Validate contracts with offline fixtures, then separately perform owner-controlled real Sandbox checks. Record source documents, actual test output and *unknowns* in [roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md); no paid production operations or merchant dashboard changes from this design-only publication.
