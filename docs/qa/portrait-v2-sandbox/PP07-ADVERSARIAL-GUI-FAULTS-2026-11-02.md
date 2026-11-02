# PP-07 adversarial native-GUI fault injection — 2 November 2026

## Latest verified automated test evidence (same code as current branch)

**Code SHA:** [`0548bc894fd19064984122bed04860d207e1ed51`](https://github.com/pratikto/PhotoBooth/commit/0548bc894fd19064984122bed04860d207e1ed51)  
**Source-matched GitHub Actions:** [#41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134), **COMPLETED SUCCESS, 3/3 jobs**.

| Runner | Tests | Failures | Errors | Skips | Verified result |
| --- | ---: | ---: | ---: | ---: | --- |
| Windows private-state | **494** | 0 | 0 | 0 | **PASS** |
| Ubuntu private-state | **494** | 0 | 0 | 0 | **PASS** |
| Ubuntu native Kivy + Xvfb | **54** | 0 | 0 | 0 | **PASS** |
| **Total executions** | **1,042** | **0** | **0** | **0** | **3/3 SUCCESS** |

These are repeated automatic test executions across environments, not 1,042 unique user acceptance scenarios. Two newly added native P0 GUI tests, one new backend restart-state test, and the pre-existing regression suite all pass on the tested code. No real customer photos, Midtrans charges/refunds, physical POS80 paper, actual cloud upload, true OS process-kill receipt uncertainty or actual 30-second customer observation was performed. All 112 canonical PP acceptance cases and the 26 owner Windows UAT cases remain separate `NOT_RUN` at their full acceptance scope.

**Historical failed run remains documented below:** first F3 test attempt at `7f018dba` failed on a test-only `KeyError` due to expecting a deliberately omitted private QR key. The corrected assertion `0548bc89` passed 3/3 without weakening payment/privacy guards. GitHub HEAD after that code SHA contains documentation-only updates.

---
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

## Second P0 simulation increment — late duplicate PAID and persisted printer SENDING

**Previous source validation:** [CI 41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221) at `c86a8e64` has **493 Windows + 493 Ubuntu + 53 native Kivy = 1,039 test executions PASS**, all 3 jobs SUCCESS, no failures/errors/skips. This validates the two earlier new GUI tests and their protective fixes, not the new tests below.

**New exact-source test commit:** `9220940e` and `7f018dba` (test-only source additions, no merchant code/payment/refund production changes). First matching-source [CI 41403886185](https://github.com/pratikto/PhotoBooth/actions/runs/41403886185) at `7f018dba` **FAILED native** on the test-only assertion described next; corrected source `0548bc89` passed [CI 41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) **3/3 SUCCESS**.

**Failed first attempt and correction (transparent evidence):** [CI 41403886185](https://github.com/pratikto/PhotoBooth/actions/runs/41403886185) at `7f018dba` failed its native step because the new test accessed `app._photo_view['payment_qr']` after the already-verified `paid_hold` state intentionally omitted that private QR field. This produced `KeyError` in the test itself, not a second charge, privacy leak or merchant API failure. Test-only micro-commit `0548bc89` now uses `.get('payment_qr')` to assert the QR is absent whether the key is omitted or set to `None`. No payment behavior was weakened. [Latest exact-source CI 41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) is **VERIFIED 3/3 SUCCESS** with 494 Windows + 494 Ubuntu + 54 native PASS and no failures/errors/skips. This supersedes the first failed test run, which remains an audit record.

### F3 — original expired QR1 pays late while QR2 is pending

**PP mapping:** PP-021, PP-024, PP-028–030 and the no-second-service invariants in PP-035.  
**New native test:** `test_native_late_qr1_paid_while_qr2_active_never_grants_twice`.

It completes two original three-photo design sessions, offers the original CCP, creates synthetic QR1, receives verified `expire`, continues to QR2, then marks QR1 as independently `settlement` **while QR2 remains active**. Native GUI must leave the pending QR, return to private `paid_hold` and show an `OWED` original entitlement, without recharging, recapturing, releasing photos to another person, or creating another paid service. A later independent QR2 settlement must preserve the exact first entitlement and record **one excess paid attempt** for separate finance/refund evaluation; it must not grant second photos or a second ticket. All settlement values are from the in-memory synthetic provider. This test does **not** authorize or execute a refund.

### F4 — durable SENDING journal after printer-worker death

**PP mapping:** PP-050, PP-052, PP-065, PP-078, PP-095 and print no-replay requirements.  
**New backend test:** `test_persisted_sending_after_worker_crash_blocks_new_dispatcher_replay`.

This test **injects** a durable original paid-strip `SENDING` row at the precise crash seam after journal commit and before physical printer acknowledgment. It instantiates a **new** `OriginalPaidPrintDispatcher` against the existing same ledger/preparer and asserts that replay is denied, no `print_image` call occurs, the job remains `SENDING`, and service stays `OWED`. It is a persistent-state restart **model**, **not** a verified OS-level process kill or real printer power-loss experiment. The latter remain future test gates.

### Remaining after F1–F4

Even when all above tests pass, complete owner PP-001–112 acceptance and 26-case Windows physical UAT are separate `NOT_RUN`; the next fault-injection stage should exercise actual process termination/reopen with original journal files, queued receipt-vs-strip lane behavior and pending paid upload, plus a live webcam/Drive/POS80 test under explicit consent. Never promote a synthetic provider duplicate to proof of genuine merchant refund capability.

## Required execution and remaining P0 gaps

The matching-source GitHub Actions [run 41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221) is **completed SUCCESS** on all 3 jobs. Both newly added native tests are present in the output and all 53 native tests PASS. Windows and Ubuntu each execute 493 backend regression tests with zero failures/errors/skips. Do not promote these to physical/merchant or full PP-001..112 acceptance. If a test fails, fix root cause, micro-push and rerun exact-source CI. Older full 112 PP matrix and 26 owner Windows UAT cases remain **NOT_RUN** at their acceptance scope, despite individual automated coverage.

Next **independent** P0 candidates: actual process death/reopen while original ticket receipt or purchased strip is SENDING; provider QR2 late-settles while QR3 is pending; A/B return while B's capture or old A's upload remains active; worker fence/ACK failure injection. The committed F4 test models an existing SENDING journal but does **not** itself kill a process. Device gates remain explicit: POS80, webcam/touchscreen, real Drive ACL/upload/retention, and separately authorized merchant Midtrans Sandbox and refund API.
