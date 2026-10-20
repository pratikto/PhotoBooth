# FEAT-020 HTTP v2 integration - 2026-10-20

Approval: audit remediation on `feature/qris-payment`; no merge/live deployment.

## Current server contract

`qris_server:build_sandbox_app --factory` now wires CheckoutBackend + CheckoutStore. Importing the module does not read secrets or open a database. Configure MIDTRANS_SERVER_KEY, MIDTRANS_MERCHANT_ID, MEONG_QRIS_BOOTH_ID and MEONG_QRIS_BOOTH_TOKEN on the server; the kiosk receives only its booth ID/token/API URL. Database closes through ASGI lifespan. The fixed provider endpoint is Sandbox; no production mode exists.

All order/claim calls require X-Booth-ID and Bearer authentication. Create and claim additionally require a persistent Idempotency-Key (16-64 identifier characters). Create only accepts a strict known-template -> integer 1..10 map. Status returns order/key/amount/state/service state; claim returns a stable grant instead of an ambiguous boolean. The service endpoint records STARTED/COMPLETED against the same grant/local transaction ID. Cancel waits for independently verified provider status. HTTP 409 means a conflict/recovery requirement, not permission to retry a different order.

Webhook JSON is read incrementally (16 KiB cap, five-second read deadline), including chunked requests; invalid or duplicate JSON members are rejected. Blocking provider/database service calls use a threadpool. Transient/unapplied notifications receive 503, never a successful 200/false acknowledgement. A bounded per-peer rate limiter is included for single-worker Sandbox trials. Public deployment still requires HTTPS, ingress body/concurrency/rate limits, monitoring and credential rotation.

The kiosk client uses the v2 key/grant contract, rejects redirects and non-Sandbox modes, validates order identity, caps response bytes, and closes responses. The provider transport also refuses redirects and adds the Sandbox cancel endpoint. No merchant key is sent to the kiosk.

## Actual tests before push

Linux/Python 3.13.5, `python tools/run_qris_tests.py`: **102 PASS, 0 FAIL, 0 SKIP**. Includes ten new real HTTP/service/SQLite cases, strict bool/string/float rejection, duplicate JSON rejection, missing webhook recovery, re-claimed grants, service acknowledgement replay, 503 -> successful webhook retry, cross-booth denial, chunked early-stop and a non-blocked health endpoint during slow status I/O. Existing HTTP tests now require dependencies rather than silently skipping. No real provider or hardware was used. The old standalone preview UI is being superseded by the main-GUI integration and should not be used with the v2 contract until that step lands.

References: https://fastapi.tiangolo.com/async/ ; https://docs.pydantic.dev/latest/concepts/strict_mode/ ; https://docs.midtrans.com/reference/best-practices-to-handle-notification .
