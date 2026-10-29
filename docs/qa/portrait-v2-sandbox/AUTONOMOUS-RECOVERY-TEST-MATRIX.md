# Autonomous recovery — mandatory fault-injection, QA and acceptance matrix

## 29 October — AR-03.d1 PAY-18 combined lost replies

Base/remote verified `03189012b5f4c6204ef4f8718bb218a1baac32d5`.
**85 focused PASS / zero failure/error/skip**, 12.257s. Two new methods run
**eight actual child exits at four boundaries**: original booth claim, customer
claim, STARTED and COMPLETED committed before local acknowledgment. Same
order/grant/claim operation/allocation/transaction/result; one provider charge,
three synthetic JPEGs/one composition, original OWED and private proof preserved.
Outage HTTP 503/refund HTTP 409 deny cached-PAID recovery; existing bytes remain.
[Contract/commands/provenance](PAY18-SERVICE-REPLIES.md).

Tests/CI/docs only; no runtime defect or application/schema/UI change. Current
CI pending at this containing test commit. Prior full e0dc594 (1117/1114/3) and
native c94696d (28 PNG/four QR) retain original source; no new full/native result.
Matrix **51 PASS / 1 FAIL / 9 BLOCKED / 8 NOT_RUN**; PAY-18 synthetic PASS,
BUG-023 OPEN, overall audit IN_PROGRESS. Next AR-03.d2 completion/archive exits,
then CAP-11–13, CAP-16 pre-request boundary, CAP-20 and AR-09 denial audit.
External/OPS/production gates unchanged; only disposable work/ local, no
unpublished runtime patch. This containing commit is the next micro-push;
resolve its SHA from Git, push and verify remote before continuing.

**Historical CAP-01–05 status, 29 October:** CAP-01–05 actual child-exit coverage verified
at test source `e72e28bdf8b0cbb080ef0c35aa8a1e3906bf55cb`: **66 focused PASS**, matching
CI 40815197373 **three jobs SUCCESS**, Windows payment/allocation group 55 PASS.
Application unchanged from e0dc594; no new full/native/physical result inferred.
[Exact command/trees/limits](evidence/cap01-05-final-verification.json).

Scenario matrix **50 PASS / 1 FAIL / 0 SKIP / 9 BLOCKED / 9 NOT_RUN** (69 IDs).
UX-13/BUG-023 denial audit remains FAIL/OPEN; overall audit IN_PROGRESS.
Next PAY-18 combined lost service replies, then remaining media/disk and AR-09.
Original scenario contract and dated full/native evidence remain below.

## A. Invariants asserted on every relevant transition

`I01` Exactly one internal order and immutable provider order ID for same checkout key.  
`I02` No second charge attempt/new order ID because of timeout/404/late status; never infer failed from timeout alone.  
`I03` Provider evidence matches merchant/booth/order/amount/currency/type/reference and fraud policy; no local payment authority.  
`I04` Exactly one service entitlement/grant and one bound local photo transaction per verified paid order.  
`I05` Any verified paid but undelivered service remains an auditable liability even if UI releases.  
`I06` No overwriting old/orphan original or retake; at most three originals and one retake per selected design.  
`I07` No duplicate composition, printing, upload, backend completion or physical capture from retries/crashes.  
`I08` Only authenticated original customer claim reveals previous photos or resumes camera.  
`I09` All external I/O off Kivy main thread; bounded retries/backpressure; stale callbacks and duplicate taps harmless.  
`I10` No rewinding/deleting/reassigning existing customer IDs, data or claims; original retention deadlines preserved.  
`I11` Sandbox never leaks provider key into GUI or produces real printer/Drive jobs; production disabled.  
`I12` No accidental cross-booth/customer/provider entitlement ownership or path/link traversal.

## B. Payment provider and backend (synthetic)

| ID | Fault injection or input | Required proof | Roadmap |
| --- | --- | --- | --- |
| PAY-01 | Kill process after persisting CREATE_PREPARED, before sending POST | One frozen order/key, safe resume and no duplicate charge | AR-01 |
| PAY-02 | Provider accepted POST but response is dropped | Same provider order reconciled; no new ID or charge | AR-01 |
| PAY-03 | Provider never saw POST; GET status not found | Hold CREATE_UNCERTAIN; no invented fail/replacement; documented safe next action | AR-01 |
| PAY-04 | Provider status returns stale/lagging 404 after POST | Bounded retry, no same-order POST unless verified semantics | AR-01 |
| PAY-05 | Two threads retry CREATE concurrently | Unique checkout/order, one logical provider creation, conflict safe | AR-01 |
| PAY-06 | Crash between provider evidence and DB commit | On reboot fresh revalidation, no duplicate entitlement | AR-02 |
| PAY-07 | API timeout while pending | Preserve QR/order; exponential+jitter retry (no hot loop) | AR-02 |
| PAY-08 | Network returns after several failures | Trigger one immediate safe reconciliation; no retry storm | AR-02 |
| PAY-09 | Settlement arrives during cancellation | Same original order becomes paid or formally held, no replacement charge | AR-02 |
| PAY-10 | Duplicate/out-of-order signed webhook | One update, monotonic evidence, no double grant | AR-02/AR-11 |
| PAY-11 | Tampered signed notification, amount/order/merchant mismatch | Reject/quarantine; never grant | AR-02 |
| PAY-12 | Cache says PAID, fresh provider says refund/partial_refund | Revoke new admission, preserve old fulfillment audit | AR-02 |
| PAY-13 | Cache says PAID, provider unreachable | Do not grant new sensitive recovery action; retain liability | AR-02 |
| PAY-14 | Missing optional fraud_status vs present deny/challenge | Contract-compliant decisions; unknown never bypasses validation | AR-00/AR-02 |
| PAY-15 | Provider terminal cancel/expire/fail confirmed | Existing visit closed safely; new checkout allowed only after release | AR-02 |
| PAY-16 | Late settlement for closed/suspended order | Original order/claim retained; never grants next visitor | AR-03 |
| PAY-17 | Two booths / wrong bearer / merchant IDs | No cross-tenant read, cancel, claim or resolve | AR-03 |
| PAY-18 | Lost claim/STARTED/COMPLETED response, retry same action | Same ID, idempotent server ACK; no new session | AR-03 |
| PAY-19 | Mismatched or reused action ID/body | Conflict and no mutation | AR-03 |
| PAY-20 | In-app clock changes or expired GUI timer | Provider evidence still authoritative; retention/expiry not silently extended | AR-02 |
| PAY-21 | Provider endpoint redirects/large body/auth failure | Reject, redact and hold; no secrets sent to redirect | AR-02 |
| PAY-22 | Sandbox-specific provider repeat-charge behavior unknown | Test remains BLOCKED on official contract, no speculative production call | AR-01 |

## C. Durable payment-to-photo binding and local files

| ID | Crash/fault point | Expected outcome | Stage |
| --- | --- | --- | --- |
| CAP-01 | Crash just before allocation intent | No second allocation if unknown; safe original reserve flow | AR-03/04 |
| CAP-02 | Crash after allocation intent, before folder creation | Same operation/ID can be recovered or held, never new unbound ID | AR-03/04 |
| CAP-03 | Crash after local folder creation, before manifest first write | Orphan recognized, original ID preserved, no "latest folder" inference | AR-04 |
| CAP-04 | Crash after initial manifest, before backend STARTED | Reconcile exact order/grant/transaction; no second transaction | AR-03/04 |
| CAP-05 | Crash after STARTED API accepted, before response persisted | Replay same acknowledgment, not service reallocate | AR-03 |
| CAP-06 | Crash after capture intent, before camera frame | Same slot/intent resumes safely; no phantom photo | AR-04 |
| CAP-07 | Crash after temp JPEG, before fsync/rename | Recover temp safely or quarantine; no acknowledged photo | AR-04 |
| CAP-08 | Crash after durable rename, before manifest photo entry | Detect orphan and validate file; no overwrite | AR-04 |
| CAP-09 | Crash after manifest entry, before GUI updates | Manifest is authoritative; exact saved frame restored | AR-04/05 |
| CAP-10 | Resume with photo 1/2/3 present | Correct count, no fourth default shot and no old file replacement | AR-05 |
| CAP-11 | Crash after retake select, before retake frame | Correct selected index and retake allowance; never double consume | AR-05 |
| CAP-12 | Crash after retake frame, before retake manifest/quota commit | Resolve exact retake intent/file or hold; no duplicate retake | AR-04/05 |
| CAP-13 | Crash after retake commit | Used quota remains consumed, original retained and final chosen path matches | AR-05 |
| CAP-14 | Crash during composition temporary output | Validate or recompute only if explicitly safe and no downstream effect; no duplicate output identity | AR-05 |
| CAP-15 | Crash after output committed, before next design | Restore completed design/copies; resume only unfinished design | AR-05 |
| CAP-16 | Crash between final local composition and service COMPLETE API | Reconcile same backend ACK; never repeat capture/print | AR-05 |
| CAP-17 | Another template version/price deployed while order held | Frozen quote/template/copy hashes match historical transaction | AR-03/05 |
| CAP-18 | Missing/corrupt media/manifest, path symlink/junction or wrong booth | Hold reason and preserve evidence; no unsafe restore | AR-04/05 |
| CAP-19 | Duplicate rapid touch, stale Kivy callback or minimized worker response | One valid active operation, no old session reentry | AR-07 |
| CAP-20 | Disk full/permission error on intent, image or manifest | No false commit; paid-unfulfilled remedy retained | AR-04/08 |
| CAP-21 | Local photo deadline passed during suspended visit | No resurrection/expiry extension; original claim and remedy remain | AR-08 |

## D. Kiosk, privacy, customer claim and operational effects

| ID | Scenario | Required assertion | Stage |
| --- | --- | --- | --- |
| UX-01 | App reopens with old PAID order | No old photo on startup; neutral claim screen only | AR-06/07 |
| UX-02 | New passerby taps "Continue" with no token | Denied; cannot expose thumbnails or consume original permit | AR-06 |
| UX-03 | Guessed/expired/replayed/wrong-booth token | Rate-limited denial and no photo data disclosure | AR-06 |
| UX-04 | Original valid claim token after restart | Restore exact order/manifest; user chooses fresh countdown | AR-06/07 |
| UX-05 | User abandons ambiguous payment | Rights retained; new visitor admitted only after safe durable separation | AR-09 |
| UX-06 | PAID with missing camera after settlement | No silent cancellation; customer claim/compensation recorded | AR-08 |
| UX-07 | Camera, disk, template or printer preflight failure | Block charge before QR creation, with clear user message | AR-08 |
| UX-08 | Offline Drive with approved verified reserves | Correct existing offline-safe behavior, no new hard block | AR-08 |
| UX-09 | Printer job SENDING/UNCERTAIN after restart | No automatic second spool/print; operator remedy | AR-09 |
| UX-10 | Drive upload/retry during resume | Existing queue retained; no duplicate customer folder/QR; retention policy unchanged | AR-09 |
| UX-11 | App frozen while upload/QR/checkout worker running | No UI thread blocking; watchdog cannot replay external effects | AR-10 |
| UX-12 | Kill/restart repeatedly, including competing startup processes | Single live lease/fencing and bounded supervisor restart | AR-10 |
| UX-13 | Operator wrong PIN/replay/cross-order resolution | Rate-limited, fully audited denial; same action ID idempotent | AR-09 |
| UX-14 | Operator closes PAID Sandbox test | Ledger remains PAID + UNFULFILLED where appropriate, never fake refund/completion | AR-09 |
| UX-15 | 800×1280 and 452×900 recovery views | Screenshot/readability/copy link/touch safe; no clipping | AR-07 |
| UX-16 | Exit/restart with no active obligation | Ordinary v2/MOCK paths unchanged and stable | AR-12 |
| UX-17 | Server secret/PIN/token in exception/report/process args | No secret exposure; redaction assertions | AR-09/11 |
| UX-18 | Archive folder "old" or linked storage | Excluded from scan, sync, retention and recovery | All |

## E. Webhook backend (only if separately authorized)

`WEB-01` Public HTTPS valid TLS, host/port/redirect/header compatibility.  
`WEB-02` Correct signature verification, exact status/order amount and anti-replay/dedup.  
`WEB-03` Durable inbox acceptance before 2xx, bounded handler latency, background reconciliation.  
`WEB-04` Duplicate/out-of-order notification and provider outage during callback.  
`WEB-05` Crash after inbox insert/before acknowledgment, replay without double grant.  
`WEB-06` Endpoint downtime, retries, poison event quarantine, monitoring/metrics.  
`WEB-07` Legacy-to-BI-SNAP differences explicitly gated; never confuse `X-EXTERNAL-ID`, invoice idempotency header and provider order ID.  
`WEB-08` Public API limits, admin identity/auth, no local debug or public private records.  
All public WEB items are currently **BLOCKED** on infrastructure approval; offline prototype evidence is listed separately in the execution ledger.

## F. Test harness specification

- Use `tempfile.TemporaryDirectory`, fake clock, fault injection at **every** durable write boundary and external request boundary; run isolated process crash/restart cases, not just raised exceptions in memory.
- For DB reliability test SQLite WAL, abrupt exit, connection close/reopen, two concurrent workers, unique indexes, transaction rollback, blocked writer and persistence at new process PID.
- For media use tiny synthetic distinguishable JPEG/PNG assets; verify actual file hashes, content versions, paths, original/retake selection and output IDs. Never place customer photo samples/merchant keys in CI artifacts.
- For GUI use injected Kivy worker outcomes, main-thread update checks, lost callbacks, minimize/restore, 800×1280 + 452×900 native renders. Validate both portrait dimensions, no interaction overlap.
- Mock provider states: pending, settlement, expire, cancel, deny, failure, refund, partial_refund, missing, stale 404, malformed JSON, wrong merchant/order/currency/amount/type/fraud, slow response, timeout and duplicate callback.
- Test each transition at ***before effect / after effect before commit / after commit before reply / after reply*** whenever applicable.
- Record expected/actual backend and local order state, fulfillment state, files present, job counts, customer-visible screen and operator log per test.
- First write tests to reproduce the loophole; implement minimal source fixes; verify no regression in original P3/MOCK/Sandbox and v1.

## Executed evidence ledger — 29 October 2026

Existing test references retain the complete e0dc594 regression evidence.
The six new CAP-01–05/orphan methods are separately verified by the 66-case
focused run and three-job CI at e72e28b; they were absent from that older full run. The older execution baseline was
`f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`,
executed by the full command/environment in [validation](AUTONOMOUS-RECOVERY-VALIDATION.md).
The [safe report](evidence/ar12-final-verification.json) pins test source trees,
full count/skips/digest, CI and native manifests. Abbreviated `module.method`
means that method in `tests/module.py`; PASS references were checked against
the successful final runner output. A NOT_RUN reference is supporting evidence
only, not a pass of the stronger scenario. Public WEB rows remain BLOCKED;
offline inbox prototype assertions do not certify deployed ingress.

| ID | Classification | Exact test reference / artifact | Actual scope or missing evidence |
| --- | --- | --- | --- |
| PAY-01 | **PASS** | `test_checkout_creation_attempts.test_pay01_abrupt_exit_after_prepared_does_not_authorize_resubmission` | Real child PREPARED/SENT exit; original order, no resend. |
| PAY-02 | **PASS** | `test_checkout_creation_attempts.test_lost_response_uncertainty_survives_reopen_and_status_recovers` | Synthetic provider accepted/lost reply; same identity after reopen. |
| PAY-03 | **PASS** | `test_checkout_creation_attempts.test_provider_never_received_call_and_repeated_404_remain_uncertain` | Never-received and 404 hold, no replacement. |
| PAY-04 | **PASS** | `test_checkout_creation_attempts.test_provider_never_received_call_and_repeated_404_remain_uncertain` | Repeated lagging 404 cannot authorize POST. |
| PAY-05 | **PASS** | `test_checkout_creation_attempts.test_concurrent_independent_backends_send_once` | Independent concurrent backends send once. |
| PAY-06 | **PASS** | `test_checkout_reconciliation.test_pay06_abrupt_exit_before_evidence_commit_requires_fresh_get_and_one_grant` | Audit increment 2: four real child exits at validated/pre-transaction and SQL/pre-COMMIT boundaries, without/with prior grant; rollback, WAL integrity, lease hold, fresh pending denial then settlement; one original grant/fulfillment. [116-case focused evidence](evidence/ar-audit-payment.json). |
| PAY-07 | **PASS** | `test_checkout_reconciliation.test_retry_backoff_is_durable_bounded_and_not_bypassed_by_duplicate_calls` | Persisted bounded/jittered backoff and no duplicate I/O. |
| PAY-08 | **PASS** | `test_pay08_connectivity.test_pay08_observed_restoration_bypasses_backoff_with_one_get_and_no_new_effects`; native `test_connectivity_edge_runs_on_worker_and_late_result_remains_private` | AR-02.d: repeated provider failures/backoff, passive OS edge on native worker, one same-order GET before retry deadline, duplicate/lease/reopen throttling, no grant/service/media effect, late privacy denial. Actual Windows/Ubuntu/merchant reconnection NOT_RUN; unknown/missing OS hints use polling. [103-case focused evidence](evidence/pay08-integration.json). |
| PAY-09 | **PASS** | `test_checkout_backend.test_cancel_racing_payment_never_discards_paid` | Settlement/cancel race preserves original rights. |
| PAY-10 | **PASS** | `test_checkout_backend.test_duplicate_settlement_and_claim_return_same_grant` | Signed-event dedup and fresh current status also covered by notification inbox tests. |
| PAY-11 | **PASS** | `test_checkout_backend.test_bad_evidence_cannot_unlock` | Identity/amount mismatch rejects; tampered signature tested separately in same module. |
| PAY-12 | **PASS** | `test_checkout_reconciliation.test_cached_paid_refund_reconciles_without_grant_or_service` | Refund denies new grant; partial refund covered by durability module. |
| PAY-13 | **PASS** | `test_checkout_reconciliation.test_cached_paid_outage_is_unknown_never_permission` | Historical PAID liability retained; offline cannot authorize admission. |
| PAY-14 | **PASS** | `test_autonomous_recovery_baseline.test_pay14_absent_fraud_field_and_explicit_accept_are_valid` | Present invalid fraud fields separately denied by the companion autonomous baseline case. |
| PAY-15 | **PASS** | `test_checkout_backend.test_no_new_order_until_provider_cancel_confirmed` | Terminal states and original visit release, no inferred cancellation. |
| PAY-16 | **PASS** | `test_checkout_durability.test_late_paid_is_review_not_next_customer` | Late paid stays original order under review. |
| PAY-17 | **PASS** | `test_qris_http_v2.test_other_booth_cannot_read_or_claim` | Booth authentication plus creation-attempt merchant/mode mismatch tests. |
| PAY-18 | **PASS** | `test_service_crash_recovery.test_pay18_combined_lost_claim_started_completed_replies_restore_original_result_and_ack`; `test_pay18_completed_reply_loss_cannot_use_cached_paid_during_outage_or_refund` | Eight real child exits/four boundaries across original claim/customer proof/STARTED/COMPLETED; same original ACK tuple/operation/allocation, immutable three-JPEG/one-output result and OWED. Fresh outage/refund deny recovery; no repeated charge/media/delivery. [85-case focused evidence](evidence/pay18-replies-verification.json). |
| PAY-19 | **PASS** | `test_qris_recovery.test_changed_action_payload_or_order_cannot_reuse_old_action_id` | Reused action body/order conflicts without mutation. |
| PAY-20 | **PASS** | `test_checkout_reconciliation.test_clock_rollback_holds_without_extending_deadline_indefinitely` | Provider remains authority; clock/credential/retention cases use separate fixed clocks. |
| PAY-21 | **PASS** | `test_checkout_reconciliation.test_pay21_oversized_status_and_auth_failure_hold_and_redact_at_http_boundary`; `test_midtrans_sandbox.test_redirect_is_not_followed` | Audit increment 2: oversized provider status JSON read bounded at 65,537 bytes/response closed; HTTP 401 and oversized responses remain unchecked and deny grant with redacted HTTP/DB evidence. Same-order Sandbox GET only; existing no-redirect guard also PASS. [Focused evidence](evidence/ar-audit-payment.json). |
| PAY-22 | **BLOCKED** | See scope/gate | Official merchant-specific Legacy repeat-charge contract and controlled Sandbox evidence absent; POST retry remains disabled. |
| CAP-01 | **PASS** | `test_fulfillment_crash_recovery.test_cap01_exit_before_local_or_backend_intent_creates_only_first_original_allocation` | Two real child exits before local intent and after it/before backend request; original proof/key/grant/op, first allocation once, no new order/charge/counter. [AR-03.c1 evidence](evidence/cap01-02-verification.json). |
| CAP-02 | **PASS** | `test_fulfillment_crash_recovery.test_cap02_exit_after_backend_commit_recovers_same_allocation_before_first_folder` | Real backend COMMIT/pre-reply/pre-folder exit; exact operation/ID recovered after original proof, first manifest/STARTED reuse, no shutter/render or second allocation. [AR-03.c1 evidence](evidence/cap01-02-verification.json). |
| CAP-03 | **PASS** | `test_fulfillment_crash_recovery.test_cap03_exit_after_empty_folder_before_manifest_initializes_only_original_id`; `test_cap03_orphan_bytes_after_folder_crash_are_held_without_recency_lookup` | Real empty-folder/pre-manifest exit recovers only same RESERVED allocation. Repeated exit + unknown bytes stays held; parent enumeration forbidden, neighbor/original bytes untouched. [AR-03.c2 evidence](evidence/cap01-05-verification.json). |
| CAP-04 | **PASS** | `test_fulfillment_crash_recovery.test_cap04_exit_after_first_manifest_before_started_preserves_manifest_and_same_ack` | Real first-manifest/pre-STARTED exit; original ticket/fresh provider validation, byte-identical manifest, original ACK, zero capture. [AR-03.c2 evidence](evidence/cap01-05-verification.json). |
| CAP-05 | **PASS** | `test_fulfillment_crash_recovery.test_cap05_exit_after_started_acceptance_replays_original_ack_without_capture` | Real backend STARTED/local RESERVED exit, exact original ACK/reopen, same allocation/counter, no capture/render/print. [AR-03.c2 evidence](evidence/cap01-05-verification.json). |
| CAP-06 | **PASS** | `test_capture_journal.test_abrupt_process_exit_at_every_write_boundary_preserves_evidence` | Real child exit at capture intent before frame. |
| CAP-07 | **PASS** | `test_capture_journal.test_abrupt_process_exit_at_every_write_boundary_preserves_evidence` | Real child exit at temporary/staged JPEG boundaries; unacknowledged bytes stay held. |
| CAP-08 | **PASS** | `test_capture_journal.test_abrupt_process_exit_at_every_write_boundary_preserves_evidence` | Real published JPEG/pre-manifest exit, image/hash and no overwrite assertions. |
| CAP-09 | **PASS** | `test_capture_journal.test_abrupt_process_exit_at_every_write_boundary_preserves_evidence` | Real committed exit; reconstruction restores manifest-authorized count. |
| CAP-10 | **PASS** | `test_photo_reconstruction.test_partial_three_capture_states_restore_exact_count_without_new_ids` | Exact 1/2/3 original states; quota and IDs retained. |
| CAP-11 | **NOT_RUN** | `test_photo_reconstruction.test_retake_selected_and_used_restore_without_renewing_quota` | Retake selection/reconstruction passes; retake-specific abrupt child exit absent. |
| CAP-12 | **NOT_RUN** | `test_capture_journal.test_retake_selection_and_consumed_quota_commit_with_same_saved_bytes` | Exception/lost reply and quota pass; child fixture covers originals, not retake frame/pre-quota exit. |
| CAP-13 | **NOT_RUN** | `test_photo_reconstruction.test_retake_selected_and_used_restore_without_renewing_quota` | Committed retake restore passes; exact retake-commit child exit not demonstrated. |
| CAP-14 | **PASS** | `test_output_journal.test_abrupt_output_process_exit_preserves_each_publication_boundary` | Real child output intent/staged/published/committed exits; originals/hash/ACK verified. |
| CAP-15 | **PASS** | `test_photo_reconstruction.test_multiple_designs_resume_only_unfinished_design_and_original_copies` | Saved output/copies retained on reconstruction of next unfinished design. |
| CAP-16 | **NOT_RUN** | `test_customer_claim_session.test_completed_service_can_restore_result_only_without_capture_readmission` | Result-only guard passes; exact final-compose/COMPLETE boundary process kill absent. |
| CAP-17 | **PASS** | `test_photo_allocation.test_mismatched_frozen_contract_does_not_create_media_or_new_id` | Frozen template/cart/hash/copies; changed contract holds. |
| CAP-18 | **PASS** | `test_photo_reconstruction.test_corrupt_media_or_wrong_binding_stays_held_without_data_rewrite` | Corruption/binding denial plus capture symlink/archive tests; real Windows junction acceptance separate. BUG-022 missing committed PNG regression added in [audit increment 3](evidence/ar-audit-missing-output.json), 61 focused PASS. |
| CAP-19 | **PASS** | `test_kiosk_v2_sandbox_widgets.test_real_photo_handoff_completion_and_duplicate_taps` | Duplicate taps, privacy-lock stale callbacks and native ownership gates. |
| CAP-20 | **NOT_RUN** | `test_capture_journal.test_failure_before_publication_never_acknowledges_a_capture` | Image publication failure and low-disk/write-probe denial pass; every intent/manifest ENOSPC/EACCES boundary not demonstrated. |
| CAP-21 | **PASS** | `test_retention.test_expired_controller_capture_cannot_recreate_a_deleted_photo` | Expired media cannot resurrect; retained liability separately asserted. |
| UX-01 | **PASS** | `test_customer_claim_session.test_rebooted_reserved_order_cannot_prepare_without_original_customer_proof` | Private restart hold; native neutral claim screens at both sizes. |
| UX-02 | **PASS** | `test_photo_reconstruction.test_no_permit_inspection_reveals_no_pixels_and_restore_rejects` | No proof means no private pixel/restore permission. |
| UX-03 | **PASS** | `test_customer_capability.test_wrong_short_expired_and_wrong_booth_proofs_cannot_grant` | Replay/action identity and durable failed-attempt budget also tested. |
| UX-04 | **PASS** | `test_kiosk_v2_sandbox_widgets.test_native_claim_and_deliberate_resume_restore_original_capture_without_new_charge` | Original proof, exact saved image count and deliberate countdown; native return screenshots. |
| UX-05 | **NOT_RUN** | `test_checkout_release.test_prepare_holds_booth_and_ack_releases_only_occupancy` | Paid two-phase release is covered; ambiguous creation abandonment/release is deliberately conservative, not blanket certified. |
| UX-06 | **PASS** | `test_kiosk_v2_sandbox_widgets.test_postpaid_camera_fault_records_owed_issue_and_hides_media` | Durable paid-unfulfilled issue; no fabricated cancellation. |
| UX-07 | **NOT_RUN** | `test_recovery_readiness.test_low_disk_or_unwritable_probe_prevents_admission` | Camera/storage/template and accidental delivery opt-in deny; purchased real-printer preflight not certified in transport-off Sandbox. |
| UX-08 | **PASS** | `test_booth_sync.test_configured_layout2_without_credentials_is_offline_ready_and_never_falls_back_to_legacy_oauth` | Offline local progress with deferred Drive and preserved layout/claims. |
| UX-09 | **PASS** | `test_release_session.test_uncertain_print_never_yields_isolation_receipt_or_releases_booth` | Uncertain print remains held, no automatic resend; paper outcome NOT_RUN. |
| UX-10 | **PASS** | `test_booth_sync.test_two_transactions_keep_exact_local_folder_mapping_across_restart` | Immutable delivery mapping/retry/retention fixtures; actual Drive acceptance NOT_RUN. |
| UX-11 | **NOT_RUN** | `test_crash_supervisor.test_normal_operator_hold_or_living_process_never_restarts` | No-kill live-child gate and responsive HTTP tested; actual frozen-worker/GUI hang scenario not exercised. |
| UX-12 | **PASS** | `test_crash_supervisor.test_three_crashes_have_persisted_budget_and_bounded_backoff` | Persisted restart budget; kernel multi-process lease tests, no business replay. |
| UX-13 | **FAIL** | `test_qris_recovery.test_independent_pin_attempt_limit_cannot_block_regular_status`; [audit denial probe](evidence/ar-audit-pin-denials.json) | Rate-limited PIN rejection and action replay/conflict tests PASS, but the stronger fully audited denial requirement fails: wrong PIN returns 401/429 with no durable denial record. Operator budget is process-local; only customer capability attempts persist. BUG-023 OPEN. No authentication bypass observed. |
| UX-14 | **PASS** | `test_checkout_fulfillment.test_abandon_preserves_paid_obligation_and_no_fabricated_refund` | Closure/composition are not liability satisfaction. |
| UX-15 | **PASS** | See scope/gate | Final native manifests: both portrait sizes, 28 hashes/dimensions, four QR decodes; selected layouts inspected. Physical touch/phone tests NOT_RUN. |
| UX-16 | **PASS** | `test_kiosk_v2_recovery.test_empty_install_is_clear_without_creating_files` | Existing default/MOCK/native lifecycle regressions; no new business effect. |
| UX-17 | **PASS** | `test_customer_claim_session.test_original_ticket_is_memory_only_and_cannot_be_redisplayed_after_restart` | Memory-only ticket plus backend-only PIN/argv/export isolation assertions; no blanket forensic log certification. |
| UX-18 | **PASS** | `test_kiosk_v2_recovery.test_old_is_pruned_and_linked_storage_is_rejected_before_descent` | Archive/link exclusion uses synthetic temporary paths only. |
| WEB-01 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |
| WEB-02 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |
| WEB-03 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |
| WEB-04 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |
| WEB-05 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |
| WEB-06 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |
| WEB-07 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |
| WEB-08 | **BLOCKED** | `test_notification_inbox` | Public infrastructure/merchant approval, mounted ingress/worker, TLS and operational acceptance absent. Offline inbox prototype is supporting evidence only. |

### Invariants and reliability cross-check

I01–I04: creation attempts, backend reconciliation and fulfillment identity tests;
I05: paid issue/OWED and release tests; I06: capture/output/reconstruction tests;
I07: no-replay source assertions only, with missing exact child/paper effects
retained above; I08: capability/permit/privacy tests; I09: native stale callback,
worker/event-loop tests (actual frozen-worker gate NOT_RUN); I10: immutable
identity/retention/archive tests; I11: Sandbox launcher/credential/delivery-off
tests; I12: booth authentication, frozen merchant and checked-path tests.
These are supporting PASS assertions, not a proof of every real-world transition.

WAL/FULL PREPARE/ACK child exits and integrity_check plus locked-writer BEGIN
rollback are PASS in `test_autonomous_recovery_faults`; stale fences in
`test_service_fencing`; paid-but-unfulfilled durability in `test_fulfillment_issues`;
PNG INTENT/STAGED/PUBLISHED/COMMITTED child exits in `test_output_journal`;
JPEG five-boundary child exits in `test_capture_journal`; archived completed
result-only return in `test_release_session`. Windows native CI passes these
portable checks, not physical power loss or Python directory-fsync equivalence.
Offline mapping/retention are synthetic; actual Drive deletion remains BLOCKED.

Every original PAY/CAP/UX/WEB ID appears once here. Full-suite optional model
SKIPs are recorded separately in validation; they are not silently counted as
matrix PASS or used to waive device/merchant requirements.

## G. Evidence and acceptance sheet

| Gate | Evidence required | Current |
| --- | --- | --- |
| Source unit/integration | Exact SHA, OS, command, full count PASS/FAIL/SKIP, fixtures and no secret leakage | PASS at e0dc594: 1117 run / 1114 PASS / 3 optional palm SKIP |
| Crash/restart fault-injection | Every PAY/CAP/UX applicable ID mapped to test output | NOT_RUN for complete gate; see explicit missing exact windows above |
| Complete GUI regression | One final applicable full suite after last functional change; no borrowed old pass | PASS at e0dc594; three optional palm SKIPs, native video PASS in same run |
| GUI screenshot/pixels | Tested exact source 800×1280 and 452×900, readability and QR identity | PASS for 28 clean c94696d scenes / four QR checks; retake/multi-design visual scenes NOT_RUN |
| Windows booth | Real camera/storage, app close/reopen/power interruption, native touch/keyboard | NOT_RUN |
| Ubuntu mini PC | Actual graphical session service, permissions, startup, real camera/print hardware | NOT_RUN |
| Android/tablet | Separate build/lifecycle/provider and storage behavior; if targeted, actual device evidence | NOT_RUN |
| Merchant Sandbox | Owner controlled simulator, actual status/poll/cancel/late settlement; no bank/wallet | NOT_RUN |
| Production QRIS | Account/BI-SNAP decision, webhook, merchant terms, refund/compensation, security | NOT AUTHORIZED |
| Paper/Drive/retention | Real paper/phone/cloud access and authorized deletion test when separately in scope | NOT_RUN |

**Blocker policy:** Any unresolved P0 no-double-charge, no-double-fulfillment, photo overwrite, privacy leak, financial liability loss, or unproven provider creation outcome blocks unattended release. A test running successfully is not a real-device/merchant certification. Do not mark new tests PASS without execution.

## H. Owner handoff

For each stage add a row to implementation evidence documenting `AR-XX`, source SHA, test IDs, counts, CI run, device/provider acceptance and known risks. Historical [P5 acceptance](../portrait-v2-pending-acceptance/README.md) is retained; these new cases supplement it and do not require retesting unrelated already-stable photo/game cycles without a code-affecting regression.
