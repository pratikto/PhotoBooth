# FEAT-020 main GUI integration - 2026-10-20

Approved branch-only implementation; no master merge or live payments.

`main.py` now selects the QRIS subclass only for explicit qris-mock/qris-sandbox; unknown modes fail closed. `app_qris.py` inherits the accepted main camera/retake/composition/Drive/print flow and replaces payment admission/acknowledgement. `ui_qris.py` uses the existing branded shell and muted payment advertisements. Network status, claims and QR downloads use one worker; Kivy widget/texture updates stay on the GUI thread. The order is persisted before image retrieval; QR response bytes are bounded while streaming. Completion acknowledges the same local transaction/grant before admitting a new visit. Stale DEMO confirmation callbacks cannot bypass admission.

The separate manual preview entrypoint now forwards to the main GUI. `tools/run_qris_mock.py` launches a loopback backend with ephemeral booth credentials and no merchant keys, and disables physical printing unless --allow-print is explicitly selected. See ../QRIS_TRIAL.md for setup and recovery boundaries, including deferred remote payment-QR paper slips.

Before this push: local compileall PASS; Linux/Python 3.13.5 mandatory backend tests **114 PASS / 0 FAIL / 0 SKIP**. Kivy is unavailable in the local execution environment, so the seven new real-widget/controller tests and screenshots are queued for the feature-branch Kiosk GUI CI. They are NOT yet claimed passed. They cover automatic single admission, camera recovery, active-visit isolation, two-template capture/retake/result/completion, stale callback denial, storage-failure hold, and 1200x800/800x600 payment screenshots. The existing full GUI regression is retained.
