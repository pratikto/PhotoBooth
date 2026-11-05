> **Later R4 execution:** [source-matched simulation campaign](PP07-SIMULATION-CLOSURE-R4-2026-11-05.md), [112-case partial review](evidence/pp07-r4-case-review-2026-11-05.json), [188-row register](evidence/pp07-execution-register-r4-2026-11-05.csv). Historical mappings below remain dated; all full acceptance outcomes are unchanged.

# Detailed PP-001–112 procedures — 5 November 2026

Use the [master plan](PP07-COMPLETE-TEST-PLAN-2026-11-05.md) COMMON protocol, E1–E9 record and referenced group setup for every case. Canonical scenarios and expected results are preserved verbatim from the source-specific review of the [acceptance matrix](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md). All full acceptance outcomes remain **NOT_RUN**. A planning label is not an observed outcome. Existing methods below are partial evidence at `acbac15842b59d5005075f2fbc7e87978323b158`, not proof of the additional steps or hardware/provider lifecycle. The machine-readable companion retains all mapped method IDs.

## PP-001 — One template

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Capture one design through all three slots; attempt a second retake after consuming the first.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: 3 original slots, at most one retake

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_photos.PrivateCaptureTests.test_three_originals_and_independent_retake_per_template`; all mappings are in the JSON review.

## PP-002 — Two templates

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Capture two distinct designs and retake one selected slot in each independently.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: 6 originals, independent retakes

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_photos.PrivateCaptureTests.test_three_originals_and_independent_retake_per_template`; all mappings are in the JSON review.

## PP-003 — Twelve templates

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Select all twelve designs, capture all 36 originals and exercise each independent retake once.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: 36 originals, max 12 retakes

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j01_all_twelve_designs_capture_36_originals_before_one_charge`; all mappings are in the JSON review.

## PP-004 — Multiple paper copies

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Increase copies after capture without adding designs; compare camera counters before and after.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No extra photo sessions

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j02_three_designs_copies_2_1_3_one_charge_three_exact_batches`; all mappings are in the JSON review.

## PP-005 — Crash during save

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Terminate the synthetic saver before write, after write and after commit; restart against the same isolated journal.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No duplicated or lost committed shot

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_photos.PrivateCaptureTests.test_real_process_exits_keep_original_identity_bytes_and_retake_quota`; all mappings are in the JSON review.

## PP-006 — Crash during retake

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Interrupt retake before replacement commit and after quota commit; restore the original slot lineage.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Correct selected slot and quota

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_photos.PrivateCaptureTests.test_real_process_exits_keep_original_identity_bytes_and_retake_quota`; all mappings are in the JSON review.

## PP-007 — Deselect/reselect template

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Consume a retake, deselect the design and reselect it; try another retake.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Consumed retake does not reset

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_photos.PrivateCaptureTests.test_deselection_restart_reselection_preserves_exact_retaken_bytes`; all mappings are in the JSON review.

## PP-008 — Camera disconnect/countdown race

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Disconnect virtual camera at countdown completion and deliver its stale callback after a new generation starts.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No automatic shutter

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j16_invalid_capture_generation_does_not_advance_or_charge`; all mappings are in the JSON review.

## PP-009 — Artwork updated mid-draft

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Change source artwork during draft composition; compare pinned version/hash on recovery.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Pinned version/hash or safe hold

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_photos.PrivateCaptureTests.test_changed_artwork_and_tampered_media_are_held`; all mappings are in the JSON review.

## PP-010 — Compose before payment

Priority: **P1**. Executor: Engineer + device tester. Dependencies: COMMON + G-CAPTURE in the master plan. Next planning state: `HARDWARE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Private synthetic camera fixture first; actual webcam/touchscreen on Windows and Ubuntu separately. Select the specified designs/copies and record slot IDs, committed image hashes and retake counters.

1. Compose an unpaid draft and invoke downstream print/upload/completion callbacks directly.
2. Compare committed slots, chosen images, immutable artwork version and retake counters before/after; count captures separately from paper copies.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No print, paid completion or public upload

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual webcam/touchscreen/orientation, storage/device interruption and owner observation remain HARDWARE_PENDING; mapped tests validate synthetic private capture guards.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j01_all_twelve_designs_capture_36_originals_before_one_charge`; all mappings are in the JSON review.

## PP-011 — Copy change before QRIS

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Change copy counts in final preview, return to checkout and compare quote without taking new photos.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Requote, no new captures

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout.PreviewFreezeTests.test_copy_edit_requotes_without_recapture_or_new_preview`; all mappings are in the JSON review.

## PP-012 — Add template before QRIS

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Add an uncaptured design in preview, finish its three shots and inspect the combined quote.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: New 3-photo session

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout.PreviewFreezeTests.test_every_selected_template_needs_three_photos_and_approval`; all mappings are in the JSON review.

## PP-013 — Remove template before QRIS

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Remove one captured design before checkout and inspect quote and private media retention.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Revised quote, private media remains safe

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_store.PrivateDraftTests.test_deselect_reselect_keeps_lineage`; all mappings are in the JSON review.

## PP-014 — Edit after provider-create intent

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Pause immediately after durable provider-create intent; attempt copy/design/price edits and delayed GUI actions.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Reject; same frozen cart

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout.PreviewFreezeTests.test_edits_and_capture_rejected_after_first_durable_create_prepared`; all mappings are in the JSON review.

## PP-015 — Preview download QR attempted unpaid

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Try opening or scanning unpaid preview download targets from a signed-out test client.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No accessible photo

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout.PreviewFreezeTests.test_private_preview_reuses_renderer_without_delivery_or_completion`; all mappings are in the JSON review.

## PP-016 — Preview manifest corrupted

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Corrupt one manifest reference/hash before checkout; request a payment QR.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No charge

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j06_corrupted_saved_source_after_paid_never_prints_different_image`; all mappings are in the JSON review.

## PP-017 — Camera/disk not ready before capture

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Make camera unavailable and disk unwritable in separate fresh fixtures before capture starts.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No payment

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j15_storage_readiness_loss_after_capture_prevents_new_charge`; all mappings are in the JSON review.

## PP-018 — Printer known unavailable pre-charge

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Set printer readiness unhealthy before checkout; request a new payment attempt.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No new charge

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_readiness.TrustedReadinessTests.test_actual_local_media_disk_camera_and_route_recheck_before_charge`; all mappings are in the JSON review.

## PP-019 — Drive API/sharing unavailable or READY reserve pool empty before charge

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Independently fail Drive readiness, sharing and the READY pool before checkout; distinguish availability from postpaid folder binding.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Hold checkout; do not require a bound customer URL pre-PAID

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j15_storage_readiness_loss_after_capture_prevents_new_charge`; all mappings are in the JSON review.

## PP-020 — Server quote/artifact mismatch

Priority: **P0**. Executor: Engineer + integration tester. Dependencies: COMMON + G-FREEZE in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Fresh private draft, all final previews, known quote and readiness adapters. Instrument provider-create calls and frozen manifest digest; test before and after durable create intent.

1. Alter server quote amount or artifact hash versus frozen preview and request checkout.
2. Compare UI total, frozen server amount, cart digest and provider amount; record denied edits and zero unauthorized provider/public-upload calls.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Reject, preserve draft

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual camera/disk/printer route and authenticated deployed Drive capacity require device/account observation; mappings validate local frozen-quote and rejection guards only.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout.PreviewFreezeTests.test_client_amount_mismatch_or_stale_revision_never_prepares_create`; all mappings are in the JSON review.

## PP-021 — Lost POST response after provider created order

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Let fake charge POST commit remotely then drop its response; retry/restart with original identity.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Same attempt, no duplicate

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j12_lost_http_response_and_repeated_poll_never_mint_new_charge`; all mappings are in the JSON review.

## PP-022 — 404 during provider propagation

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Return provider GET 404 after ambiguous creation, then make the same original order visible.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: UNKNOWN, not unpaid

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_lost_post_reply_and_404_reconcile_same_original_after_restart`; all mappings are in the JSON review.

## PP-023 — Duplicate/late webhook

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Replay delayed/duplicate webhooks with conflicting payloads; control the independent fresh provider GET.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Independently verify fresh provider state

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_unsigned_or_stale_notification_never_grants_without_fresh_get`; all mappings are in the JSON review.

## PP-024 — QR1 verified expired, active customer

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Verify QR1 expired/unpaid, keep original visitor active and request continuation.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: QR2 same frozen draft, no recapture

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_qr1_qr2_qr3_require_fresh_expiry_same_customer_and_never_qr4`; all mappings are in the JSON review.

## PP-025 — QR2 verified expired, active customer

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Verify QR2 expired/unpaid with original active visitor; request the third attempt.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: QR3 same frozen draft

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_qr1_qr2_qr3_require_fresh_expiry_same_customer_and_never_qr4`; all mappings are in the JSON review.

## PP-026 — QR3 expired

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Verify QR3 expired; try continuation, rapid taps and stale QR2 callbacks.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No QR4, guarded close

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout_widgets.PrivateCheckoutWidgetTests.test_native_expiry_qr1_qr2_qr3_never_offers_qr4_or_recaptures`; all mappings are in the JSON review.

## PP-027 — Customer abandons PENDING

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Abandon a PENDING checkout then present visitor B before cancellation is independently reconciled.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No automatic renewal; original cancel/reconcile

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_explicit_abandonment_recovers_cancel_intent_after_interrupted_finance_write`; all mappings are in the JSON review.

## PP-028 — Cancel races settlement

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Pause cancel and settle the same original order before its response; deliver both callback orders.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Retain PAID/OWED

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_cancel_racing_settlement_preserves_paid_unclaimed_owed_without_release`; all mappings are in the JSON review.

## PP-029 — QR1 PAID while QR2 creating

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Settle QR1 while QR2 create is in flight; deliver both completions in each order.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: One service; conflict ledger

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_qr1_settles_during_qr2_create_without_second_entitlement`; all mappings are in the JSON review.

## PP-030 — QR2 and QR3 both settle

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Settle QR2 and QR3 against one frozen purchase and repeat reconciliation.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No double printing; financial review

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_duplicate_settlements_get_exactly_one_entitlement_and_record_excess`; all mappings are in the JSON review.

## PP-031 — Restart during CREATE_UNKNOWN

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Kill the client during CREATE_UNKNOWN; query the original order before allowing any new create.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Original identity still authoritative

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payment_crashes.PostPreviewPaymentCrashTests.test_sent_before_remote_commit_is_unknown_and_never_reposted`; all mappings are in the JSON review.

## PP-032 — QR expires after customer departure

Priority: **P0**. Executor: Engineer + provider integration tester. Dependencies: COMMON + G-PAYMENT in the master plan. Next planning state: `PROVIDER_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen private draft with offered CCP; deterministic fake HTTP provider and separate guarded merchant Sandbox profile once available. Preserve original merchant/order/attempt identities.

1. Expire the original QR after visitor departure and advance timers/polling.
2. Record independently verified provider state, create/cancel/status call counts, attempt lineage and entitlement count; webhook payload alone is never payment authority.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No automatic absent-customer renewal

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual post-preview merchant Sandbox launch/profile, credentials and independent merchant/provider evidence remain blocked; local provider and fake HTTP are not account acceptance.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_verified_cancel_or_absent_customer_never_gets_expiry_renewal`; all mappings are in the JSON review.

## PP-033 — Pre-PAID checkout-claim proof offered

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Observe CCP before the first payable QR; compare proof entropy/type/scope privately without saving its value in shared evidence.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Private, distinct, strong token/verifier

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ccp.OriginalCCPTests.test_issue_stores_ciphertext_hash_scope_without_raw_proof_or_offer_claim`; all mappings are in the JSON review.

## PP-034 — Claim proof used before PAID

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Submit a valid CCP while provider remains unpaid and attempt photo access.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Cannot show unpaid photos

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ccp.OriginalCCPTests.test_prepaid_claim_proof_verification_grants_no_media_payment_or_machine_lease`; all mappings are in the JSON review.

## PP-035 — Late PAID after customer goes

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Abandon checkout, settle it later and deliver stale UI/print callbacks while public Ads is visible.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: PAID_UNCLAIMED; no public print

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j14_paid_payment_poll_stress_cannot_change_entitlement_or_photos`; all mappings are in the JSON review.

## PP-036 — Returning original proof with PAID/free booth

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Present original valid proof when free after fresh independent PAID verification; repeat the claim.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: One original entitlement restored

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j17_A_paid_B_captures_A_waits_then_returns_without_new_payment`; all mappings are in the JSON review.

## PP-037 — Returning proof while visitor B active

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Start B then submit A original valid proof without interrupting B.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: WAIT/DEFER, B not preempted

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j17_A_paid_B_captures_A_waits_then_returns_without_new_payment`; all mappings are in the JSON review.

## PP-038 — Wrong booth, forged, expired claim

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Submit wrong-booth, forged, expired and revoked proofs separately; test expiry/revocation across provider GET and occupancy commit (BUG-040).
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Deny private access

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j18_invalid_QR_roles_during_B_never_release_original_paid_A`; all mappings are in the JSON review.

## PP-039 — Replay/brute force attempts

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Repeat guessed/replayed proofs across requests and inspect rate limits and redacted auditing.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Rate-limited, scoped, audited

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ccp.OriginalCCPTests.test_rate_limit_is_durable_across_service_restart_and_window_is_bounded`; all mappings are in the JSON review.

## PP-040 — Customer paid but claim proof never offered

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `CROSS_COMPONENT_OFFER_EVIDENCE_GAP`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Crash prepayment UI before any real CCP offer, then independently settle the original order; inspect owed/remedy classification.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Owed/remedy; no customer blame

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ccp.OriginalCCPTests.test_genuine_offer_requires_original_live_render_permit_and_never_resets_timestamp`; all mappings are in the JSON review.

## PP-041 — Fresh PAID, original customer owns booth, printer healthy and acknowledges SUBMITTED

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Use a healthy fast receipt ACK; measure screen visibility from actual render and verify concurrent single same-token receipt enqueue.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: **Mandatory on-screen original QR + full code with 30s visible timer/NEXT** starts while **one same-token ticket receipt job is enqueued concurrently**, without waiting for ACK; successful printing MUST NOT skip or dismiss screen

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_native_journeys.NativeCustomerJourneyMatrixTests.test_n21_native_three_designs_full_gallery_to_paid_ticket_and_2_1_3_print`; all mappings are in the JSON review.

## PP-042 — Ticket printer unavailable, failed, timeout, delayed SUBMITTED or UNCERTAIN

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Run missing, failed, slow, timeout and UNCERTAIN virtual receipt outcomes; press NEXT and also allow natural expiry.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: **Same mandatory 30s ticket screen shown regardless of print outcome**; no reissue/auto-reprint, no timer reset on late printer callback, correct private cleanup on NEXT/zero

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j11_uncertain_original_receipt_never_gets_resubmitted`; all mappings are in the JSON review.

## PP-043 — Crash after PAID before any genuine first ticket screen became visible / printer SENDING

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Kill after PAID before first lawful visible ticket frame with receipt SENDING; reboot privately and attempt original claimant return.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Vault and owed policy; no public ticket on boot, no duplicate send; first lawful screen requires original customer proof and free booth

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_process_crash.OriginalPrintProcessCrashTests.test_p01_actual_process_exit_during_recovery_receipt_preserves_owed`; all mappings are in the JSON review.

## PP-044 — Crash after ticket SENDING

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Persist ticket SENDING then kill/restart; poll repeatedly and inspect transport sends.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Never auto-reprint

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_process_crash.OriginalPrintProcessCrashTests.test_p01_actual_process_exit_during_recovery_receipt_preserves_owed`; all mappings are in the JSON review.

## PP-045 — Vault key/ciphertext missing

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Remove protected key and corrupt ciphertext in separate disposable fixtures; restart original claim flow.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Fail closed, OWED retained

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ccp.OriginalCCPTests.test_key_loss_or_corrupt_ciphertext_fails_closed_with_original_record_retained`; all mappings are in the JSON review.

## PP-046 — Operator/DEMO/QRIS/download QR as customer proof

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-PROOF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Original A private draft/paid claim as specified, distinct visitor B, distinct CCP and recovery ticket; capture visible-presentation journal and private claim verifier events.

1. Submit operator, DEMO, QRIS and download QR values to the customer claim endpoint.
2. Check original entitlement, proof type/scope/expiry, actual visible timer, no B disclosure and no automatic receipt resend. Preserve PAID/OWED on denial.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Reject cross-type use

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Target OS escrow, complete proof-gated original-worker restart, actual visible presentation/paper opportunity and security/device acceptance remain separate; mapped key/restart tests have their stated synthetic/CI scope.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j18_invalid_QR_roles_during_B_never_release_original_paid_A`; all mappings are in the JSON review.

## PP-047 — Compose auto-print callback while unpaid

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Invoke paid compose/auto-print callback using an unpaid original manifest.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Block paid photo print

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_paid_drive.OriginalPaidDriveReservationTests.test_unpaid_draft_cannot_claim_any_ready_folder`; all mappings are in the JSON review.

## PP-048 — 3 designs with 2+1+3 copies

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Buy three designs with 2+1+3 copies; compare nine original captures with six paid output copies.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Six paid copies; only 9 captures

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j02_three_designs_copies_2_1_3_one_charge_three_exact_batches`; all mappings are in the JSON review.

## PP-049 — SUBMITTED but no paper physically emerged

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Return transport SUBMITTED while an isolated test printer has no confirmed physical output; inspect user/ledger wording.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Not recorded as physical delivery

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j02_three_designs_copies_2_1_3_one_charge_three_exact_batches`; all mappings are in the JSON review.

## PP-050 — Partial RAW bytes sent then timeout

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Send a partial virtual RAW byte stream then timeout; restart and request continuation.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: UNCERTAIN, no replay

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j07_negative_printer_ack_quarantines_every_remaining_design`; all mappings are in the JSON review.

## PP-051 — Ticket screen shown while thermal printer lane holds original receipt job; NEXT pressed before printer returns

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Hold original receipt transport; press NEXT while screen is live and queue paid strips; release the barrier and inspect serialized sends.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Screen timer operates independently; serialized exclusive original receipt / photo-strip jobs, no lost job, overlapping raw sends or reprint

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout_widgets.PrivateCheckoutWidgetTests.test_next_wipes_qr_while_original_receipt_sender_is_blocked`; all mappings are in the JSON review.

## PP-052 — Design A printed, B uncertain

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Mark design A submitted/delivered and B uncertain; restart/restore and invoke late callbacks.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No A replay or blind B replay

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j08_second_batch_timeout_keeps_prior_submitted_job_immutable`; all mappings are in the JSON review.

## PP-053 — Paid, Drive URL unverified

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Keep paid original Drive URL unverified while attempting strip dispatch.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Hold strip, retain OWED

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j04_paid_drive_outage_then_same_transaction_recovers_without_new_charge`; all mappings are in the JSON review.

## PP-054 — Verified Drive URL, upload pending

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Bind and independently verify original Drive URL but delay uploads; inspect printed QR and truthful upload status.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Real QR, honest upload status

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j04_paid_drive_outage_then_same_transaction_recovers_without_new_charge`; all mappings are in the JSON review.

## PP-055 — Anonymous draft and 25 READY folders

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Visit anonymously with 25 READY folders and abandon unpaid; inspect pool occupancy and public API calls.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No free folder claim/public upload

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_paid_drive.OriginalPaidDriveReservationTests.test_unpaid_draft_cannot_claim_any_ready_folder`; all mappings are in the JSON review.

## PP-056 — Cross-booth/foreign folder

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Supply foreign booth/folder identities during atomic paid folder binding.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Binding rejected

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j05_malicious_drive_url_after_paid_never_releases_paid_print`; all mappings are in the JSON review.

## PP-057 — Crash during upload

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Crash after upload bytes but before acknowledgment; retry same original checksum without resending strips.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Same checksum retry, no reprint

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j04_paid_drive_outage_then_same_transaction_recovers_without_new_charge`; all mappings are in the JSON review.

## PP-058 — Last compose marks payment completed

Priority: **P0**. Executor: Engineer + printer/Drive integration tester. Dependencies: COMMON + G-DELIVERY in the master plan. Next planning state: `HARDWARE_CLOUD_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Frozen original paid draft where required, instrumented serialized virtual printer and private fake Drive; use separately consented isolated physical printer/test Drive only in the external phase.

1. Finish the last compose while required paid obligations remain unresolved.
2. Compare design/copy and transport-send counts with independently inspected paper, original folder binding/checksums and remaining obligations; SUBMITTED is not physical delivery.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Must remain pending paid obligations

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Actual POS80 bytes/paper/cutter, public customer Drive permission/upload and original worker restart require separate hardware/account evidence; mock submission never proves delivery.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_paid_delivery.OriginalPaidDeliveryTests.test_all_verified_files_update_only_drive_state_not_service_or_print`; all mappings are in the JSON review.

## PP-059 — Unpaid draft abandoned, no QR attempt

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Abandon an unpaid draft without ever creating QRIS; request a new visit after privacy fencing.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Privacy fence, safe release

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j20_twelve_rapid_protected_visits_do_not_share_draft_or_charge`; all mappings are in the JSON review.

## PP-060 — Customer actively capturing with slow worker

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Keep capture/write worker actively progressing longer than normal idle warnings; inspect inactivity decisions.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No hard inactivity cutoff

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_idle.PrivateInactivityTests.test_legitimate_countdown_and_slow_worker_have_no_hard_visit_cutoff`; all mappings are in the JSON review.

## PP-061 — Inactive gallery/review/final preview

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Leave each gallery/review/final-preview screen inactive; observe warning, suspend and private pixel cleanup.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Warning, safe suspend

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_idle.PrivateInactivityTests.test_each_phase_warns_before_its_own_configured_expiry`; all mappings are in the JSON review.

## PP-062 — PENDING original checkout and new visitor

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Leave original checkout PENDING and request checkout for a new visitor.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No unsafe new payment

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j19_stalled_worker_blocks_B_and_A_without_consuming_original_proof`; all mappings are in the JSON review.

## PP-063 — Stale A callback during B session

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. After lawful A release and B start, deliver A camera/compose/payment/Drive callbacks.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Fenced; B unaffected

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j17_A_paid_B_captures_A_waits_then_returns_without_new_payment`; all mappings are in the JSON review.

## PP-064 — Crash during release/ACK lost

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Kill at PREPARE, local receipt, ACK reply loss and archive boundaries; retry exact original operation.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Retry exact operation, no broad reset

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_isolation.OriginalMockIsolationTests.test_reuse_rejects_forged_or_unacknowledged_isolation`; all mappings are in the JSON review.

## PP-065 — Reboot with printer SENDING

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Reboot a disposable worker fixture with durable printer SENDING; inspect UNCERTAIN transition and no send replay.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: UNCERTAIN, no replay

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_process_crash.OriginalPrintProcessCrashTests.test_p02_actual_process_exit_during_paid_strip_preserves_sending`; all mappings are in the JSON review.

## PP-066 — Legacy PAID-first unfinished photo

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Open an unfinished legacy paid-first photo transaction with its original proof and checkpoint.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Original capture recovery unchanged

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_paid_starting.StartingRetryTests.test_before_accept_retry_reuses_original_operation_and_allocation`; all mappings are in the JSON review.

## PP-067 — Meong Fly consumed then unpaid abandon

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Consume Meong Fly attempt then abandon an unpaid draft; revisit game entry in the same visit.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No new game attempt

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_kiosk_v2_demo_game.DemoGameTests.test_abandonment_does_not_restore_a_consumed_code`; all mappings are in the JSON review.

## PP-068 — Untrusted game DEMO discount

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Win using DEMO game token, select two designs 2+1 copies and compare gallery/frozen/provider Rp25,000 (BUG-041).
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No real discount without verified backend

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_native_journeys.NativeCustomerJourneyMatrixTests.test_n27_demo_win_retakes_and_paid_delivery_keep_one_consistent_quote`; all mappings are in the JSON review.

## PP-069 — Repeated unpaid visits filling disk

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Repeat isolated unpaid visits until controlled resource pressure; preserve active work and inspect disk/thread/file-handle growth.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Safe resource control, no active hard cutoff

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j20_twelve_rapid_protected_visits_do_not_share_draft_or_charge`; all mappings are in the JSON review.

## PP-070 — Valid proof when booth finally free

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Wait until B safely exits, then re-present A proof and freshly verify original paid entitlement.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Fresh verification, original claim

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j17_A_paid_B_captures_A_waits_then_returns_without_new_payment`; all mappings are in the JSON review.

## PP-071 — New visitor arrives during old worker uncertainty

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Request B admission while A original worker outcome remains unknown.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Neutral HOLD

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j19_stalled_worker_blocks_B_and_A_without_consuming_original_proof`; all mappings are in the JSON review.

## PP-072 — Expired credential and paid liability

Priority: **P0**. Executor: Engineer + security/device tester. Dependencies: COMMON + G-HANDOFF in the master plan. Next planning state: `SECURE_RESTORE_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Separate visitors A/B, original journal and worker generations; run named boundary with virtual workers, then independent processes on protected target OS storage.

1. Expire original credential while original PAID/OWED liability remains unresolved.
2. Compare PREPARE/local receipt/ACK/archive identities, original financial liability, active camera owner and stale-callback rejection; never clear uncertainty to admit B.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No illicit reveal, no erased OWED

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Real camera/printer/Drive-worker lifecycle and protected cross-process restoration remain pending; no new customer may bypass original PREPARE/ACK or financial hold.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_claim.OriginalMockClaimTests.test_ccp_expiring_during_final_settlement_check_cannot_reacquire`; all mappings are in the JSON review.

## PP-073 — QR1 verified expired unpaid while same customer requests continuation

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Expire QR1 unpaid while original visitor explicitly continues; inspect QR2 create and screen transition.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: QR2 via its own guarded provider create; master flow does **not** force Advertising

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.MidtransPostPreviewContractTests.test_sandbox_expiry_contract_creates_qr2_qr3_but_never_qr4`; all mappings are in the JSON review.

## PP-074 — USER_CANCEL with verified cancelled/unpaid while customer remains in front of camera

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Cancel while customer remains present, verify cancelled/unpaid and try automatic or manual renewal.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Persist cancel intent and close safely; **never** QR2/QR3

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_cancel_unpaid_never_renews_even_if_previous_order_later_expires`; all mappings are in the JSON review.

## PP-075 — App minimized while live QRIS PENDING, no cancel action

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Minimize a live PENDING QRIS without cancel intent, resume and compare original order/state.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Privacy fence only; do not invent financial cancellation or renewed order

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_suspend_does_not_cancel_or_renew_and_late_paid_is_private`; all mappings are in the JSON review.

## PP-076 — Inactivity warning during valid camera countdown or ongoing write/compose

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Trigger idle warning while valid countdown or write/compose is actually progressing.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Active work not abandoned; retained original capture/retake quota

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_idle.PrivateInactivityTests.test_legitimate_countdown_and_slow_worker_have_no_hard_visit_cutoff`; all mappings are in the JSON review.

## PP-077 — Restart after terminal unpaid but stale camera/file worker active

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Restart a terminal-unpaid visit while original file/camera worker remains live; request B admission before and after exact ACK.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No new visitor before exact quiescence, fence and durable release ACK

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_worker.PrivateWorkerTests.test_restart_has_no_automatic_photo_restoration_or_new_visitor`; all mappings are in the JSON review.

## PP-078 — Restart during paid authorized upload while a photo print is UNCERTAIN

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Restart a paid visit with authorized upload pending and print UNCERTAIN; resume safe upload only.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Resume only idempotent upload; retain paid/print obligations; no blind print or unsafe release

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j10_direct_dispatcher_honors_durable_sending_other_design`; all mappings are in the JSON review.

## PP-079 — Receipt SUBMITTED early while first mandatory 30s screen active, then polling/restart/returning claimant

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. ACK receipt early, poll, dismiss ticket, restart and return with original proof; count first presentation and ensure it never resets.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: First screen remains visible independent of SUBMITTED; when dismissed, never automatically re-display or reset countdown on provider/paper callback, polling, reboot or returning claim; preserve exact original presentation journal

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ticket.OriginalPaidTicketTests.test_restart_recovers_same_protected_original_but_never_redisplays_offered_ticket`; all mappings are in the JSON review.

## PP-080 — Live paid owner has intact original booth lease, no CCP scan

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Keep the live original paid lease intact without a CCP scan; dispatch first screen and same receipt once.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Open **mandatory** original Recovery Ticket screen and dispatch **same ticket receipt** concurrently once; no extra claim/CCP step

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j03_paid_delivery_blocked_before_original_ticket_dismissal`; all mappings are in the JSON review.

## PP-081 — Precharge sees healthy Drive and available unclaimed READY pool, but atomic customer folder binding/URL verification fails after PAID

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Pass precharge Drive readiness but fail atomic postpaid folder binding/URL verification.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No paid strip or invented QR; PAID/OWED retained; no unpaid READY consumption

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j15_storage_readiness_loss_after_capture_prevents_new_charge`; all mappings are in the JSON review.

## PP-082 — Legacy Sandbox Drive OFF vs new purchased synthetic verified-link profile

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Run legacy BUG-027/028 Drive-OFF and isolated purchased fake-link profiles separately; inspect labels and unchanged legacy behavior.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Existing BUG-027/028 profile unchanged; isolated fake link never represented as real cloud evidence

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_paid_drive.OriginalPaidDriveReservationTests.test_missing_remote_binding_never_fabricates_customer_url`; all mappings are in the JSON review.

## PP-083 — Attempt-create timed out; provider Legacy /v2/charge idempotency-header behavior unknown

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Lose charge POST response while documented header semantics remain unknown; inspect that no invented idempotency header or repeated POST is used.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No unverified provider header or repeated POST; same original identity/status reconciliation

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.MidtransPostPreviewContractTests.test_sandbox_lost_create_and_http404_restart_never_reposts_original`; all mappings are in the JSON review.

## PP-084 — Draft/QR1/QR2/PAID/ticket timestamps across restart and expiry

Priority: **P0**. Executor: Engineer + cross-component integration tester. Dependencies: COMMON + G-BOUNDARY in the master plan. Next planning state: `INTEGRATION_PENDING`. Full acceptance: **NOT_RUN**.

Preconditions: Use original draft/order, controlled provider/clock/worker barriers and distinct A/B visitors; select legacy or post-preview profile explicitly before running.

1. Advance controlled clock across distinct approved draft, attempt, paid/ticket 15/30-day anchors and restart; compare legacy 24-hour scope separately.
2. Capture cross-component journal ordering, actual owner lease, frozen cart, original provider identities and safe release; timers/TTL use the approved versioned contract.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Different versioned TTL and 15-day/30-day anchors; no silent extension, deletion or mixing legacy 24h Sandbox claim rule

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Mapped guards are executable software subassertions only; target-platform restart, original worker generations, actual provider/Drive and retention policy/deletion remain separately unverified.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_original_paid_anchor_never_extends_on_status_poll_or_restart`; all mappings are in the JSON review.

## PP-085 — CCP genuinely visible/offered at first QRIS, later lost, original PAID service fully delivered

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Genuinely offer CCP, finish all paid service, then remove customer access to their saved proof.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: `NO_AUTO_REFUND_PROOF_LOST`; cannot self-restore old photos without valid capability; no blanket legal waiver

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_lost_genuinely_offered_proof_never_auto_refunds_alone`; all mappings are in the JSON review.

## PP-086 — Mandatory 30-visible-second ticket with full QR/code + same concurrent paper ticket, customer discards both, no independent service failure

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Genuinely display original recovery screen for 30 visible seconds with same receipt, deliver paid service, then simulate loss of both proofs.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No automatic refund solely from customer-lost proof; no operator tokenless media unlock

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_lost_genuinely_offered_proof_never_auto_refunds_alone`; all mappings are in the JSON review.

## PP-087 — First CCP never offered due prepay UI crash; original charge later independently PAID

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `CROSS_COMPONENT_OFFER_EVIDENCE_GAP`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Never render first CCP because of UI crash, then verify original late PAID; inspect evidence and remedy.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Not labeled customer negligence; PAID/OWED and secure claim/remedy, no fake proof-presented evidence

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ccp.OriginalCCPTests.test_copied_permit_reboot_or_retired_ui_cannot_record_offer`; all mappings are in the JSON review.

## PP-088 — After PAID printer SUBMITTED but mandatory Recovery Ticket screen never rendered/never visibly displayed

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `CROSS_COMPONENT_OFFER_EVIDENCE_GAP`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. ACK receipt SUBMITTED without ever visibly rendering mandatory screen; inspect proof-offer journal and remedy.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Printer ACK is not genuine screen offer; preserve claim/remedy, no customer-forfeiture

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_checkout_widgets.PrivateCheckoutWidgetTests.test_native_original_paid_ticket_30_seconds_and_one_receipt_at_both_sizes`; all mappings are in the JSON review.

## PP-089 — Customer lost genuinely offered ticket AND paid photo strips genuinely failed permanently

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Lose genuinely offered proof AND independently make paid strip service irrecoverable; inspect separate fault classification (BUG-042).
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Do not refuse compensation on proof-loss ground; independently evaluate merchant service failure and refund

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_lost_proof_cannot_mask_independent_irrecoverable_service_failure`; all mappings are in the JSON review.

## PP-090 — Customer disappears after PAID; valid CCP exists; claim window/onscreen screen timer expires

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Let paid claimant depart and expire the display/claim window; retain original financial obligations.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No automatic refund merely on absence/expiry; retain paid/owed, lawful remedy and original claim rules

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_suspend_does_not_cancel_or_renew_and_late_paid_is_private`; all mappings are in the JSON review.

## PP-091 — Recovery-ticket receipt printer broken but same original 30s screen displayed, purchased photo strips can still be safely fulfilled

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Fail only receipt printer while mandatory screen is genuinely offered and paid strips remain safely fulfillable.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Do not auto-refund solely because paper ticket failed; still permit genuine service

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_ticket_receipt.TicketReceiptTests.test_missing_printer_records_not_sent_and_never_retries`; all mappings are in the JSON review.

## PP-092 — PAID original order, printer failed irrecoverably after bounded retry, worker safely fenced, provider refund enabled

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Verify original PAID, irrecoverable strip failure and safely fenced worker; evaluate full-amount candidate in mocks only.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Refund-first full original amount candidate exactly once, not operator money-back prerequisite

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_eligible_full_is_only_nonbinding_candidate_not_payment`; all mappings are in the JSON review.

## PP-093 — PAID, paid customer Drive URL cannot be bound/verified after bounded recovery and refund channel enabled

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Exhaust bounded approved paid Drive recovery without a valid original URL; evaluate safe remedy eligibility.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: PAID/OWED -> eligible full refund after safe cleanup; never issue false QR or duplicate print

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j04_paid_drive_outage_then_same_transaction_recovers_without_new_charge`; all mappings are in the JSON review.

## PP-094 — Corrupt/missing paid manifest makes purchased service impossible; no safe restoration

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Make paid manifest irrecoverably missing/corrupt with no lawful restoration; preserve evidence and evaluate original obligation.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Independently verified unrecoverable merchant fault -> refund eligibility, preserve private photo evidence

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j06_corrupted_saved_source_after_paid_never_prints_different_image`; all mappings are in the JSON review.

## PP-095 — One photo strip SENDING/UNCERTAIN and paper may have emerged

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Leave one strip SENDING/UNCERTAIN with possible physical delivery; evaluate review and prohibit blind resend/refund.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No blind retry or blind auto-refund; physical outcome/worker fence classified, conditional review

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j09_new_dispatcher_cannot_bypass_uncertain_A_to_send_B`; all mappings are in the JSON review.

## PP-096 — Three templates, some purchased strips already delivered, other outputs permanently fail

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Deliver some purchased strips then permanently fail others; assess policy-approved full-goodwill preference and abuse/physical constraints.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Full-goodwill-refund preference only when deterministically safe, valid merchant policy and bounded abuse controls; preserve partial paper truth

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j08_second_batch_timeout_keeps_prior_submitted_job_immutable`; all mappings are in the JSON review.

## PP-097 — QR1 and QR2 both freshly verified PAID on same frozen logical purchase, same merchant and exact amount

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Independently verify two same-merchant exact-amount settled attempts for one purchase; identify only excess original charge.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: One service entitlement; refund the unambiguously excess settled attempt only, one original refund key

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.CustomerJourneyMatrixTests.test_j13_full_three_renewals_all_settle_late_only_one_entitlement`; all mappings are in the JSON review.

## PP-098 — Two QR attempts PAID but merchant/order/amount differ or conflict

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Provide two settled attempts with conflicting merchant/order/amount and request financial action.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No automatic refund or duplicate service; secure financial review

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_payments.PostPreviewPaymentTests.test_amount_or_merchant_mismatch_enters_review_without_service_or_new_charge`; all mappings are in the JSON review.

## PP-099 — Midtrans create/status PENDING, 404, UNKNOWN, CANCELLED unpaid, or EXPIRED unpaid

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Evaluate PENDING, UNKNOWN, 404, cancelled-unpaid and expired-unpaid states separately against refund request guards.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: **No refund request**, original cancel/status reconciliation only

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_unverified_original_or_wrong_merchant_does_not_refund`; all mappings are in the JSON review.

## PP-100 — Merchant GoPay QRIS POS Refund API not activated or disabled

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Disable actual merchant refund capability while a paid service fault exists; inspect truthful review-required messaging.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No pretend auto-refund; `REFUND_REVIEW_REQUIRED` with redacted truthful support remedy

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_merchant_feature_policy_or_abuse_gate_missing_holds`; all mappings are in the JSON review.

## PP-101 — QRIS refund window elapsed or issuer/acquirer/merchant balance makes provider refund ineligible

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Simulate ineligible refund window, issuer/acquirer rejection and insufficient merchant balance separately in future fake transport.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No refund API retry loop or false success; lawful approved support/manual remedy

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Refund-window/issuer/acquirer/balance eligibility is not modeled by the current classifier; merchant capability contract and source implementation are missing.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-102 — Provider account refund activation, documented API endpoint, status and refund_key semantics unknown

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Remove authoritative account activation/endpoint/status/key semantics; inspect feature gate and zero real refund calls.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Production/refund API feature gate remains disabled; synthetic mocks do not authorize live money

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_eligible_full_is_only_nonbinding_candidate_not_payment`; all mappings are in the JSON review.

## PP-103 — Forged CCP, vault compromise, mismatched provider settlement or suspected refund fraud

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Inject forged proof, compromised vault indication, settlement mismatch and fraud flags separately.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Security/finance HOLD, no private photo release, no automatic money return

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_journey_matrix.MultiVisitorJourneyMatrixTests.test_j18_invalid_QR_roles_during_B_never_release_original_paid_A`; all mappings are in the JSON review.

## PP-104 — Permanent service fault triggers refund; app crashes before external refund POST

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. In future durable protocol fixture, crash before original refund POST and restore the same original intent/key.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Durable unique original refund intent/key survives; continue/reconcile same original one only

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: NOT_IMPLEMENTED: durable refund intent/status transport, refund worker fencing and authenticated refund-status UI do not exist. No test of an unrelated classifier is counted as execution of this protocol.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-105 — Provider refund POST response lost/timeout or webhook repeats

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. In future transport fixture, accept refund POST then lose response; replay webhook and reconcile same original key.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Reconcile SAME refund intent/key, do not issue second unique refund or double payout

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: NOT_IMPLEMENTED: durable refund intent/status transport, refund worker fencing and authenticated refund-status UI do not exist. No test of an unrelated classifier is counted as execution of this protocol.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-106 — Provider accepts refund request but money remains in process

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. In future transport fixture, return requested/processing before independent final confirmation; inspect wording and ledger state.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Only `REQUESTED`/`PROCESSING`, not `REFUND_CONFIRMED` nor claim funds in customer's balance

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: NOT_IMPLEMENTED: durable refund intent/status transport, refund worker fencing and authenticated refund-status UI do not exist. No test of an unrelated classifier is counted as execution of this protocol.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-107 — Provider independently confirms original refund, then stale print callback arrives

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Confirm original refund in future protocol then deliver stale print, grant and Drive callbacks.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: No old photo-strip reprint, no fresh Drive release or duplicated grant; ledger remains auditable

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: NOT_IMPLEMENTED: durable refund intent/status transport, refund worker fencing and authenticated refund-status UI do not exist. No test of an unrelated classifier is counted as execution of this protocol.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-108 — Refund intent races in-flight printer receipt or Drive upload worker

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Race future original refund intent against receipt send and Drive upload barriers in both completion orders.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Fence/quarantine exact original work and physical paper possibilities; no blind refund/admission while unsafe

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: NOT_IMPLEMENTED: durable refund intent/status transport, refund worker fencing and authenticated refund-status UI do not exist. No test of an unrelated classifier is counted as execution of this protocol.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-109 — Verified refund completed but old camera/print lease/backend ACK still uncertain

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Confirm refund while original lease/backend release ACK remains uncertain; request a new visitor.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Booth remains `ADS_PROTECTED` / `ISOLATION_HOLD`; technician if needed, never free from financial status alone

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: NOT_IMPLEMENTED: durable refund intent/status transport, refund worker fencing and authenticated refund-status UI do not exist. No test of an unrelated classifier is counted as execution of this protocol.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-110 — Customer checks refund status and receipt reference

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. In future authenticated status UI, query requested/processing/confirmed references and attempt anonymous/foreign-order access.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Distinct state texts, authenticated/redacted reference, no fake contact/ETA, no media or credential leakage

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: NOT_IMPLEMENTED: durable refund intent/status transport, refund worker fencing and authenticated refund-status UI do not exist. No test of an unrelated classifier is counted as execution of this protocol.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.

## PP-111 — Multiple real paid attempts, original order IDs, partial/different refund provider references

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `REFUND_PROTOCOL_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Create multiple settled attempts with partial/different refund references; bind each requested refund to exact original merchant charge.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Refund exactly the intended original settled provider charge; no cross-merchant or wrong-attempt payout

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Only guarded fulfillment/proof facts or a nonbinding classifier are executable. Refund transport, durable refund journal, merchant capability and legal/financial activation are absent or unverified; no actual refund is enabled.

Existing partial software evidence: `AUTOMATED_VERIFIED` / `PARTIAL_GUARDS_OR_CLASSIFIER_ONLY`. Representative mapped method: `test_post_preview_refund_assessment.RefundAssessmentTests.test_duplicate_verified_charge_only_selects_excess_not_original`; all mappings are in the JSON review.

## PP-112 — Policy customer copy says "uang hangus, tidak pernah bisa refund" despite system failure or statutory rights

Priority: **P0**. Executor: Engineer + security/finance integration reviewer. Dependencies: COMMON + G-REFUND in the master plan. Next planning state: `IMPLEMENTATION_OR_EXTERNAL_REVIEW_BLOCKED`. Full acceptance: **NOT_RUN**.

Preconditions: Synthetic independently verified settlement and original service/worker facts; refund transport disabled. Classifier evidence is nonbinding. Future transport tests require implemented durable protocol and merchant-specific capability.

1. Review every refund/lost-proof customer message with merchant/legal reviewers against genuine offer, independent service fault and statutory rights.
2. Compare original merchant/charge/amount, service outcome and genuine proof-offer evidence; record decision and exactly-once intent/fencing. No classifier result proves payout or customer bank balance.
3. Repeat relevant late/duplicate callback and restart boundary in an isolated fixture; reconcile original journals and record observed versus expected without clearing prior state.

Pass criterion: Reject blanket waiver; narrow proof-lost NO_AUTO_REFUND policy only; legal/provider/merchant gate required

Evidence: E1–E9, especially the step-2 observables and case-specific outcome. Remaining: Legal-approved commercial terms/customer refund copy and independent merchant/legal review are not executable software acceptance; no full legal PASS is inferred.

Existing partial software evidence: `NOT_RUN` / `UNIMPLEMENTED_OR_EXTERNAL_SCOPE`. No mapped executable method; implement/resolve the required scope before claiming a run.
