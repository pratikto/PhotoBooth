# FEAT-020 final boundary and GUI checks - 2026-10-20

Current verified code checkpoint: `95011d1a536fdf429354bb22c5cbfdf2fb60bf42`.

- Backend CI run 39366730248: **114 PASS, 0 FAIL, 0 SKIP**. Artifact 12240021089 was downloaded; every tracked source file matched the locally tested copy byte-for-byte.
- Kiosk CI run 39366730262: **356 tests: 354 PASS, 2 SKIP, 0 FAIL/ERROR**. All seven new QRIS controller tests passed, including automatic admission, camera recovery and two-template capture/retake/completion. Existing visual report: **87 renders, 0 errors**. No physical devices or real payments were used.
- The first new QRIS unit-test screenshot was visually inspected and found invalid (unattached widget tree, incomplete texture/layout drawing). It is NOT accepted visual evidence. A dedicated running-Kivy-host renderer now checks six QRIS scenes and decodes exact QR payloads from screenshot pixels at 1200x800 and 800x600. Its CI result must be verified after this commit.
- Actual loopback HTTP smoke (Uvicorn, not TestClient), Linux/Python 3.13.5: create -> automatic grant -> grant replay -> STARTED -> COMPLETED PASS, with a persistent kiosk journal. No Midtrans requests or merchant keys.

## Additional contract fixes

The Midtrans technical FAQ distinguishes API action status_code from transaction_status. Successful GET status does not mean payment succeeded; status_code 407 is accepted only for expire, never settlement. An independently verified fraud-denied transaction can become FAILED, never PAID. Four new service tests cover these distinctions, and a kiosk test ensures a Sandbox client rejects a mock backend. Five QR image tests cover exact image bytes, trusted origin, no redirects, early streaming size limits and dimension limits.

Before push: `python tools/run_qris_tests.py` on Linux/Python 3.13.5: **124 PASS, 0 FAIL, 0 SKIP**. Compileall PASS. Actual merchant Sandbox, physical Windows hardware, production ingress/secret rotation and manual partial-session recovery procedures remain acceptance gates. No master merge, production payment activation or public deployment.

References: https://docs.midtrans.com/docs/technical-faq ; https://docs.midtrans.com/reference/expire-api ; https://docs.midtrans.com/docs/https-notification-webhooks .
