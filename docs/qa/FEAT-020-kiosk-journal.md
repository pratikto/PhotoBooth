# FEAT-020 kiosk journal and explicit mock - 2026-10-20

Approved branch-only audit remediation. No master merge or real payment activation.

KioskCheckout writes its visit key/cart/expected price before network creation, then persists the returned order before downloading any QR image. Retry and restart recover the same visit. A platform file lock prevents two local GUI processes consuming one journal. A lost grant response reuses the server grant. Payment environment and booth/API identity are bound to the journal; environment mismatch fails visibly instead of discarding it. Tokens are not stored in the journal.

Capture admission is recorded STARTING before storage side effects. The local transaction is linked to the grant before the backend STARTED acknowledgement. Completed outputs are retained before the final service acknowledgement. A restart after capture may have started enters RECOVERY, never a new capture or automatic uncertain print retry. Operator inspection is required for these partial sessions; automatic recovery does not certify physical paper delivery.

The persistent MockQrisProvider is explicitly non-payable, defaults to automatic simulation after eight seconds, and supports expiry/rejection/pending trials. The backend AND kiosk must select mock. Sandbox remains the default expected client environment and requires merchant verification. No merchant keys are needed or forwarded in mock mode. The next commit connects this tested state machine to the main GUI.

Actual local validation: `python tools/run_qris_tests.py`, Linux/Python 3.13.5: **114 PASS, 0 FAIL, 0 SKIP**. Twelve added tests cover journal-before-request, lost response/restart, process exclusion, environment mismatch, automatic admission, cancellation/payment race, completed service, partial-capture hold, frozen cart and non-blocking status snapshots during network work. No Kivy or real hardware execution is claimed by this step.
