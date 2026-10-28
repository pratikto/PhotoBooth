# AR-09 — operator exceptions and safe kiosk release

29 October 2026, Asia/Jakarta. Read AGENTS/protocol, master/roadmap/operations/
matrix/provider, original RECOVERY plan, launcher/server/client recovery methods,
store action audit and original native operator-health lifecycle before this stage.
Source base: AR-08.b2, exact SHA in checkpoint. Existing branch only.

AR-09.a contract before code: reuse backend's existing optional eight-digit PIN
and rate-limited booth-authenticated operator routes. Dedicated v2 launcher mints
an independent per-launch PIN, passes it only in backend startup environment,
prints it only to the local operator terminal and removes the parent's copy after
spawn. GUI environment, process args, journals and exported reports never receive
it. Original v1 trial/default launcher behavior stays unchanged without the opt-in
v2 environment factory. A new launch rotates PIN without changing customer rights.
No production/authentication reset or public admin endpoint is added.

Following increments: native PIN entry/metadata inspection and audited exception
controls; durable fenced suspension/release preserving OWED and hashed customer
claim, exact release ACK before allowing another customer. Preserve print-uncertain
and Drive obligations; no automatic refund, customer-data deletion or completion.
Physical/remote-admin/merchant/support acceptance remains separate.

## AR-09.a delivered

Dedicated v2 environment factory now mints a fresh eight-digit operator PIN.
Shared launcher prints it only when that backend opt-in exists, spawns backend,
then removes its local environment copy. GUI environment and both command-line
argument vectors exclude it; inherited PINs are discarded. Original trial
without the v2 factory does not enable recovery. Journals/customer tickets and
merchant credentials are untouched. Native entry/release remains next work.

First isolation test FAIL before source. Final **64 focused PASS / zero
FAIL/ERROR/SKIP**:
`.venv/bin/python tools/run_kiosk_unittests.py test_kiosk_v2_sandbox test_qris_sandbox_launcher test_qris_recovery test_qris_saved_credentials`.
Two new tests cover v2 environment isolation and actual mocked launcher spawn/
private local notice. All launchers use fake processes/credentials, no real
merchant/device. Rotate by restarting the dedicated launcher; no default public
PIN or persisted operator credential is introduced.

AR-09.b contract before code: on held native Sandbox session, operator explicitly
enters the launcher PIN in a masked field; reuse recovery_inspect's fresh provider
check and existing backend rate limit. Clear input immediately on submission,
keep PIN only in the in-flight call, show sanitized payment/service/issue metadata
without original media or identifiers. Inspect grants no customer proof/permit.
Pause/close/exit retires input/report and late callbacks. Busy/stale widget guards
remain. No resolve/reset/complete/refund/release is added by this increment.

## AR-09.b delivered — native metadata inspection

Held customer view now offers explicit operator assistance. Masked PIN entry is
cleared on submit; the existing single-flight worker invokes authenticated
recovery_inspect and fresh provider status. Only sanitized payment/service/OWED/
issue metadata is rendered. Successful inspection creates no customer proof,
resume permit, shutter or service transition. Exit/minimize retires credentials,
report and widget callbacks. Background polling does not interrupt PIN entry.
Source keeps resolve/release/completion absent pending the next reviewed step.

Initial focused attempt: two ERROR (operator fixture lacked explicit Sandbox
mode, plus a mistyped existing operator test module). Corrected fixture explicitly
selects fake Sandbox mode only when its synthetic PIN is configured; production
checks were preserved. Final **64 PASS / zero FAIL/ERROR/SKIP**:
`.venv/bin/python tools/run_kiosk_unittests.py test_kiosk_v2_sandbox_widgets test_qris_recovery test_kiosk_v2_operator_widgets test_customer_claim_session`.
Two new native cases exercise missing/wrong/correct PIN, no old media/grant,
transient input, journal secrecy and retired buttons. Twenty provisional native
PNG fixtures rendered at 800x1280/452x900. Operator entry/status and compact claim
were visually checked without clipping; final pinned AR-12 captures remain due.
No actual merchant or Windows/Ubuntu device result is implied.

AR-09.c1 contract before code: additive per-order service fence with generation,
opaque fencing token and suspended bit; compare-and-swap rotation invalidates old
worker authority. Existing orders without a fence retain original behavior. Every
sensitive store admission/transition checks suspension; service updates against
an active fence must carry its current token. Recheck in the final write after
provider I/O to defeat a release racing a delayed settlement response. Fencing
alone never closes payment/fulfillment, marks delivered, frees the booth or creates
another customer order. No endpoint/UI may rotate a fence yet; the later two-phase
release handshake must fence, stop local workers, durably ACK isolation, and only
then permit a new visit. Returning claim needs atomic reacquisition and new token.
Do not enable release via legacy abandon/reset as a shortcut.

## AR-09.c1 delivered — dormant service fence foundation

Additive checkout_service_fences stores durable generation/token/suspended state.
Internal CAS rotation rejects stale generations. Suspended grants, allocations,
customer redemption and service transitions are denied; an active fence requires
its current token for service updates. The final SQLite write rechecks authority
after provider I/O; legacy operator resume/complete cannot bypass a fence. Fencing
preserves order, grant, original transaction and OWED, and does not unblock another
checkout. Orders without fence rows retain existing behavior. No HTTP/native action
rotates or activates this foundation yet. It is not a completed release protocol.
Rollback retains this additive table and fail-closed guards; never erase a fence
to regain authority. Two-phase release/reacquisition remains the next source task.

Initial five tests ERROR before source. Focused **86 PASS / zero FAIL/ERROR/SKIP**:
`.venv/bin/python tools/run_kiosk_unittests.py test_service_fencing test_checkout_fulfillment test_fulfillment_issues test_customer_capability test_checkout_backend test_qris_recovery test_qris_session test_qris_http_v2`.
Five new cases cover migration, stale CAS/token, restart, no new visitor from a
fence alone, and delayed provider response racing suspension. CI registration
included. No actual operator release, restart supervisor or production enabled.

AR-09.c2 contract before code (29 October continuation): PREPARE release atomically
rotates a suspended fence and records an immutable operation/actor; booth remains
occupied. Only after local workers retire their exact session and write an
isolation receipt may PIN-authenticated ACK close the visit for occupancy purposes.
OWED, grant, media, capability and financial/service states remain intact. Lost
responses replay the same operation. No public reset, refund or fake completion.
Returning original proof atomically reacquires only an ACKED release with no other
active visit, rotates the fence again, and reuses original allocation. Stale tokens
cannot START/COMPLETE even after reacquisition. Local exact archived journal lookup
uses checkout key from the ticket, never latest-folder selection. Sandbox transport
isolation and one-process kernel leases remain mandatory. Tests precede activation.
AR-09.c2 core delivered (not yet mounted): additive immutable checkout_releases
records PREPARED/ACKED/REACQUIRED with original actor, operation/generation and
isolation receipt. PREPARED keeps occupancy, ACK closes occupancy only, valid
original claim reacquires atomically only while booth is free and rotates token.
Existing PAID + ACKED suspension retains financial PAID on fresh settlement;
legacy abandon, late unexpected settlement and refund REVIEW remain conservative.
No HTTP/UI release action exists in this core increment. Preserve both tables on
rollback. Four tests initially ERROR before schema integration; final **48 PASS,
zero FAIL/ERROR/SKIP**: `test_checkout_release test_service_fencing test_customer_capability test_checkout_fulfillment test_checkout_backend` via tools/run_kiosk_unittests.py.
Actual merchant/device/paper/cloud NOT_RUN. Next: authenticated release/token API.
AR-09.c3 delivered: PIN + booth-authenticated strict /recovery/release accepts
original operation for PREPARE and exact isolation receipt for ACK. PREPARE checks
fresh settlement; ACK records completed isolation without another provider call.
The API grants no local worker-stop proof by itself: trusted operator/UI must
perform isolation before sending ACK, enforced by the following native seam.
Service API/client accept optional current fence; legacy unfenced requests retain
original shape. Reacquired fenced services reject omitted/old token. No native
release control mounted yet. Focused **58 PASS / zero FAIL/ERROR/SKIP**:
`test_checkout_release test_service_fencing test_qris_recovery test_qris_api test_qris_http_v2 test_qris_kiosk_client` via tools/run_kiosk_unittests.py.
New authenticated HTTP test verifies denied missing PIN, PREPARE occupancy hold,
ACK closure and old-token denial/current-token STARTED. No production/deployment.
AR-09.c4 delivered (controller/worker seam, native mount next): release intent and
isolation identity are fsynced before requests; typed short-lived one-use isolation
receipt comes from the serialized transport-off photo worker, never GUI boolean.
Worker refuses uncertain print jobs/wrong ownership, retires in-memory session
without deleting bytes, and ACK archives per-operation journal plus exact-key
lookup index before marking SUSPENDED. A lost ACK repeats original IDs. Archived
lookup validates bounded context/key/quote, preserves original claim operation,
checks fresh customer proof and restores only original allocation with current
service token. No newest-folder scan or raw secret/PIN persistence. New customer
cannot preempt an active one. Focused **37 PASS / zero FAIL/ERROR/SKIP**:
`test_release_session test_customer_claim_session test_qris_session test_photo_reconstruction`.
Three new real-HTTP/synthetic-photo cases cover old media preservation, release/
new visit/return, lost ACK identity and boolean-receipt denial. No hardware effect.
