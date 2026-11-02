# PP-07 adversarial native-GUI fault injection — 2 November 2026

## Source, authority, and evidence boundary

- **Authorized branch:** `feature/post-preview-qris-checkout` only. No new branch, master merge, deployment, merchant charge, refund, physical paper or external cloud request.
- **Code increment:** `1bc5c02d` native regression for two previously missing P0 GUI paths; `0e7a1f0b` backend paid-print quarantine; `c86a8e64` customer UI guard. Refer to the exact commit SHA and associated CI run for test evidence; source commits alone are **not PASS**.
- **Previously verified baseline:** [CI 41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509), code `67dc3eb5`, 493 Windows + 493 Ubuntu + 51 headless native, all PASS. These counts do **not** cover the two new GUI cases.
- **New matching-source CI:** [CI 41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221) at `c86a8e64`. **VERIFIED 3/3 SUCCESS**: native Kivy 53/53, Windows 493/493, Ubuntu 493/493 PASS, zero failures/errors/skips, 1,039 total test executions (not distinct scenarios). Older CI cannot verify the new changes.
- **Original specifications reviewed:** [approved owner flow](POST-PREVIEW-QRIS-OWNER-APPROVED.md), [complete decision ledger](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md), [financial/privacy state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md), [112-case acceptance matrix](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md), [Windows pilot worksheet](PP07-SUPERVISED-WINDOWS-UAT.md), `AGENTS.md` and `docs/DEVELOPMENT_PROTOCOL.md`. Later approval of implementation supersedes earlier dated DESIGN ONLY status declarations; all original owner policy remains binding.

## Gap F1 — terminal third QR expiry must not invite a QR4

**Acceptance crosswalk:** PP-024, PP-025, PP-026, PP-027, PP-073; active owner continuity and original fixed frozen purchase.

**Prior condition (source-reviewed):** Backend `PostPreviewPayments.continue_expired` already refused a fourth attempt. However, `PrivateCheckoutFixtureApp._build_photo_page` still offered the actionable `LANJUTKAN PESANAN ASLI` button whenever provider state was `EXPIRED_UNPAID`, including after QR3 expiry. A customer could press a button that could not lawfully succeed, receiving an avoidable worker error instead of a clear terminal message.

**Implementation:**
- The original button is only displayed with verified `EXPIRED_UNPAID` and fewer than three durable attempts.
- After QR3 expiry the UI displays a truthful three-QR limit notice and no next-charge button, without claiming cancellation, unpaid deletion, new photograph requirement or automatic fourth order.
- Backend provider-create fences, provider identities and payment reconciliation logic are unchanged.

**New native test:** `test_native_expiry_qr1_qr2_qr3_never_offers_qr4_or_recaptures` (in `tests/test_post_preview_checkout_widgets.py`).
- Capture two designs, six synthetic JPEGs; one original prepayment CCP and frozen group.
- Create QR1 in a synthetic HTTP/provider fixture, explicitly mark it `expire`, press `PERIKSA STATUS`, and continue the exact original customer order into QR2.
- Repeat QR2 verified expiry into QR3. Mark QR3 `expire`, verify no actionable QR4 continuation in the native Kivy widget tree.
- Assert three distinct provider order IDs, exactly three **synthetic** charges (one per authorized expired QR), same group/amount and unchanged captured originals; no `OWED` is fabricated for entirely unpaid expiries.

**Not proven:** real Midtrans verified expiry, merchant timing, webhook ordering, real customer presence after timeout, actual device visual fit, or a production terminal hold workflow.

## Gap F2 — uncertain design A must quarantine remaining purchased print batches

**Acceptance crosswalk:** PP-049–052, PP-065, PP-078, PP-095, and ticket/printer-lane overlap PP-051.

**Prior condition (source-reviewed):** The original print dispatcher correctly durably marked an uncertain transport and rejected same-design replay. But `PrivateCheckoutService.paid_print_next` still selected any **other** `PREPARED` design, while the native UI kept the print-next button enabled if one PREPARED job remained. Therefore an unclassified partial output for A could immediately be followed by a new send for B.

**Implementation:**
- Before any additional paid print command, the service independently inspects original persistent jobs and raises `DraftHeld` when any job requires `needs_operator_review` (SENDING/UNCERTAIN). This guard cannot be bypassed by invoking the backend directly instead of clicking UI.
- The native print-next button is disabled during the same review-required state, even if another template is `PREPARED`.
- No automatic print replay, refund, new photo, customer release or job-status rewrite was introduced. The existing truth-preserving `OWED` and `physical_paper_verified=False` remain mandatory.
- Clearing/reclassifying an uncertain physical job is **not authorized** by this increment; requires a separate safe human/device evidence pathway.

**New native test:** `test_native_uncertain_design_print_quarantines_remaining_batches`.
- Complete two-template mock PAID, original visibly offered Recovery Ticket (once), advance to paid Drive QR fixture.
- Simulate `TimeoutError` from first design's printer transport (paper **may** have emerged). Assert A=`UNCERTAIN`, B=`PREPARED`, and needs-operator-review.
- Assert no enabled print-next button, backend print-next is rejected, no second transport call occurs even after refreshing upload status, exactly one original synthetic provider charge, original ticket receipt once, financial `OWED` retained and no falsely verified physical paper.

**Not proven:** actual POS80 partial bytes/paper/cutter state, thermal printer jam recovery, operator reconciliation, safe resume after technician classification, or true concurrency with background workers on hardware.

## Required execution and remaining P0 gaps

The matching-source GitHub Actions [run 41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221) is **completed SUCCESS** on all 3 jobs. Both newly added native tests are present in the output and all 53 native tests PASS. Windows and Ubuntu each execute 493 backend regression tests with zero failures/errors/skips. Do not promote these to physical/merchant or full PP-001..112 acceptance. If a test fails, fix root cause, micro-push and rerun exact-source CI. Older full 112 PP matrix and 26 owner Windows UAT cases remain **NOT_RUN** at their acceptance scope, despite individual automated coverage.

Next **independent** P0 candidates: power-loss/restart while original ticket receipt or purchased strip is SENDING (no replay); end-to-end late provider settlement during QR2/3 continuation; A/B return during active B photo work and old PAID upload; true machine-fence/ACK failure injection. Device gates remain explicit: POS80, webcam/touchscreen, real Drive ACL/upload/retention, and separately authorized merchant Midtrans Sandbox and refund API.
