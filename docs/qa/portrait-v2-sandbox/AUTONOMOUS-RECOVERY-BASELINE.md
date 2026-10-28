# AR-00 — frozen source contracts and offline fixture baseline

28 October 2026 (Asia/Jakarta). FEAT-007/009/020/022. Owner's current continuation
authorizes AR-00–AR-13 in dependency order, with immediate tested pushes on the
existing `feature/portrait-kiosk-v2-next`. Before: remote/local
`f6736b7c739e3317e3bcc4506edb250f9e47d92b`, clean tree. Runtime baseline remains
`2e5efe5d281a93fe8d22e53309a50147764d2939`.

## Review and acceptance recorded before test/code changes

Read AGENTS, root README, docs index, protocol, development prompt, handover,
architecture, decisions, feature/bug status, unified backlog, test ledger, v2
specification/technical design, all six Autonomous Recovery documents, provider
contract, original RECOVERY/Sandbox runbooks and FEAT-009 stage-2 recovery guide.
Inspected the active checkout store/backend, kiosk journal/client/API, evidence
validator, Sandbox transport/adapter/views, PhotoTest, TransactionStore,
manifest writer, workflow and their existing payment/photo tests. No archive
contents, merchant configuration, customer state or other branch source changed.

AR-00.a freezes actual fields/transitions below. AR-00.b adds deterministic
temporary-profile fixtures, including abrupt child-process exit with real SQLite
reopen. Acceptance: same-order recovery with no second POST, no unpaid grant,
unambiguous fraud-field decisions, and explicit holds after possible capture.
These are characterization checks; they do not certify future autonomous recovery.
No schema migration or runtime change in AR-00. Rollback: inverse only these
docs/tests, preserving all journals/data. External/provider/device checks NOT_RUN.

## Existing payment schema and authority

`CheckoutStore`: SQLite WAL, synchronous FULL, writes under BEGIN IMMEDIATE,
connection-local RLock. No explicit user_version migration marker (currently 0).

| Table | Existing fields and constraints |
| --- | --- |
| checkouts | `id` primary key (provider order ID); `booth_id`, `checkout_key` unique together; `quantities` canonical JSON; positive integer `amount`; `state` default CREATED; `created_at`, `expires_at`, `qr_url`; unique `provider_ref`; `merchant_id`; unique `grant_id`; `service_state` default NONE; `local_transaction_id`; `closed` default 0; `check_after` default 0; `verified_at` |
| checkout_events | `event_id` primary key (payload digest); `order_id`, `provider_state`, `outcome`, `received_at`, `updated_at`; no raw notification |
| checkout_recovery_actions | `action_id` primary key; `order_id`, `booth_id`, `request_hash`, `action`, `reason`, `transaction_id`, `actor`, `created_at`, `prior_payment_state`, `prior_service_state`; index on order/action |

Prototype `orders` rows are imported with `legacy-<id>` checkout key and both
payment/service REVIEW_REQUIRED. Never infer a provider creation attempt from
their presence. Merchant identity is currently bound only by validated provider
evidence, not at initial order insertion. A row with CREATED does not distinguish
crash before POST from lost reply after accepted POST. There is currently no
create-request fingerprint, attempt timestamp or explicit creation phase.

Provider normalization (internal, not new API): pending → PENDING; settlement →
PAID; expire → EXPIRED; cancel → CANCELLED; deny/failure → FAILED;
refund/partial_refund → REVIEW_REQUIRED. REVIEW_REQUIRED is sticky; PAID does
not regress to pending/ordinary terminal. Late settlement after closed/terminal
becomes REVIEW_REQUIRED. Unknown/missing/404/invalid evidence never proves failure.
Fresh verification validates exact ID, integer IDR amount, currency, merchant,
QRIS type, stable provider reference, status/API code and optional fraud_status.
Absent fraud_status is accepted; present null/deny/challenge does not authorize
settlement. Terminal failure may carry fraud deny without becoming paid.

Begin writes immutable key/cart/amount/order before I/O; repeated key polls the
same order. Three-second persisted check reservation bounds ordinary status
calls. Cached PAID is not freshly reconciled by ordinary status/claim: AR-02 gap.
Claim replays one grant (NONE → RESERVED). STARTED requires RESERVED/STARTED and
the same transaction; COMPLETED requires STARTED/COMPLETED. Local transaction ID
is not globally unique across orders: AR-03 gap. Operator inspect/resolve uses
fresh evidence, booth auth plus separately enabled eight-digit backend PIN;
resume/complete needs settlement unless replaying an exact prior action. Actions
are reconcile/resume/abandon/complete; a changed action body conflicts. Abandon
sets only closed=1; it does not satisfy a paid obligation or issue a refund.

## Existing kiosk and photo contracts

`visit.json` version 1: `context` = mode/booth_id/endpoint; `checkout_key`,
`quantities`, `amount`, `phase`, `order` backend snapshot, `transaction_id`.
Atomic file fsync/replace, process lease and single worker. No durable original
recovery phase/reason, customer capability or allocation operation ID yet.
CREATING → WAITING → RESERVED → STARTING → STARTED → COMPLETING → COMPLETED;
CANCELLING → CANCELLED, and RECOVERY for ambiguity. Reopening STARTING/STARTED
changes to RECOVERY; refresh there does no I/O. COMPLETING replays the same ACK.
STARTING is durable before allocation; transaction binding and STARTED ACK follow.
The allocation/binding crash gap is unresolved, never permission to allocate again.

Backend view: order_id/checkout_key/quantities/amount/state/expires_at/qr_url/
grant_id/service_state/local_transaction_id/closed, recovery_abandoned, mode,
verification_pending; mock adds nonpayable qr_payload. Native UNCERTAIN/QUOTE/
IDLE/LOADING are presentation states, not persisted payment authority. Native
polling runs every two seconds in some phases; RECOVERY has no resume action.
Existing copy-link/branding and Sandbox printer/Drive-off must survive integration.

Photo manifest schema_version 1 (Sandbox), or 2 for ordinary BoothWorkspace:
transaction_id/booth_id/created_at, local_retention_days/drive_retention_days/
drive_photos_expire_at, status, drive_folder_id/url/slot_key, upload_status,
upload_files, demo_order_pricing, sessions. Layout 2 adds storage_layout and
claim/binding/intent metadata. PhotoTest adds purpose, payment_enabled=false,
financial_transaction=false and test_print_jobs. These labels describe the local
photo adapter, not absence of backend payment; no payment-to-manifest binding yet.

Session fields: session_id/template_id/template_name, order_number/total_sessions,
template_session_number/count, print_copies, status, raw_photos (path/role),
retake_used, selected_photo (replaced original path), final_photos, output_path;
layout 2 may add bw_path. Upload records: path/content_version/status/size_bytes/
drive_file_id/md5_checksum/upload_session_url. Print records: state/copies/output,
optional reason/operator_checked. SENDING becomes UNCERTAIN at prepare; never
resubmit the same job automatically. SUBMITTED is not physical-paper acceptance.

PhotoTest's current design index, capture/review/result phase, selected retake
before capture and PhotoSession objects live in memory. Capture saves JPEG to
temporary file then replaces target before manifest update; no durable intent,
content hash/decode check, no-overwrite reservation or directory fsync. AR-04/05
must close this gap before reconstruction. Raw file alone must remain held.
One design = three originals/one retake, copies do not add sessions. Review/output
photo pixels mirror, originals/art/QR do not. Local expiry remains 15 days, cloud
policy 30 days; resume cannot extend either. Manifest COMPLETED is composition,
not proof of printing/Drive or backend service fulfillment.

## Frozen next interfaces and migration boundaries

AR-01: additive backend-only attempt table, keyed by existing checkout ID, binds
merchant/booth/order/key/amount/canonical charge-body fingerprint before POST;
records PREPARED → SENT/UNCERTAIN → VERIFIED. SENT means call may have happened,
not proof of wire delivery. Unknown legacy rows receive a conservative hold, no
POST. CAS permits one send only for the original freshly prepared attempt.
Retry/restart uses GET same order; no new idempotency header or repeat charge.
Write migration/rollback tests before schema implementation. Unknown merchant,
fingerprint mismatch or missing record after upgrade must never create a charge.

AR-02: narrow authenticated read-only reconciliation separate from operator
resolve; fresh evidence before resumed admission, bounded per-order backoff.
AR-03: unique payment/fulfillment/local allocation records and frozen template
hashes before effects. AR-04: capture intent/op ID before JPEG I/O and immutable
validated media commit. AR-05: manifest reconstruction only with exact binding.
AR-06 precedes GUI private photo disclosure. Preserve version-1 journals and old
manifests; missing evidence is a held legacy case, not an automatic migration by
folder search. Never down-migrate or delete active evidence on rollback.

## Evidence

Results are recorded in the recovery checkpoint/test ledger after execution.
The fixture provider uses only temporary SQLite and fixed synthetic values;
abrupt exits test process persistence, not power-loss filesystem guarantees.
PAY-01–05 and PAY-14 baseline checks do not satisfy AR-01/02 exit gates. Full
regression, native screenshots and real Windows/Ubuntu/merchant gates remain
NOT_RUN for AR-00. Provider repeat-charge semantics remain BLOCKED on official
Legacy contract plus separately controlled merchant evidence.
