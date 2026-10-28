# AR-11 — public notification backend design and isolated inbox prototype

29 October 2026. Reviewed master/roadmap/operations/provider M01–M09/test matrix,
existing authenticated_notification/process_notification/event ledger/API bounded
JSON/rate limits and HTTP retry fixtures. Source baseline AR-10; no new branch.

Infrastructure scope remains unapproved. Do not expose loopback, start tunnels,
configure merchant callback, deploy HTTPS, switch BI-SNAP, enable production or
claim public ingress acceptance. This stage delivers a reviewed design and an
unmounted opt-in offline inbox library exercised only with synthetic fixtures.
Existing runtime webhook behavior remains unchanged unless infrastructure is later
approved and a separately reviewed integration mounts the library/worker.

Contract before code: validate existing Legacy signature before durable intake;
retain only fixed non-PII transaction/signature fields, deduplicate canonical
payload hash, persist before acceptance, bound capacity. Separate bounded worker
claims with expiring fencing lease, current provider GET through original backend,
monotonic application, retry 10/20/40/60 seconds and quarantine after five failed
attempts. Lost response/event replay never grants a new service or triggers media.
Unknown/mismatched order/amount is held/rejected; duplicate intake does not requeue
APPLIED events. BI-SNAP requires a distinct explicitly approved adapter, not Legacy
headers/signatures with different URLs. No merchant credential is persisted in inbox.

For future public ingress require valid TLS on standard HTTPS, no redirect/auth
wall in provider route, bounded request/body/time, exact signature + amount/order/
merchant scope, durable acknowledgment under five seconds, worker health/backlog/
quarantine alerts, independently authenticated administrator and no public order/
photo/PIN/reset endpoints. Ingress rate limits and origin controls must account
for legitimate provider retries. Reject credentials in URL/redirects/logs. Provider
notification can only signal fresh reconciliation. Signature is not customer proof.

Operational ownership, hosting/TLS/key rotation, backup/WAL/disk/retention, worker
lease duration, retry/poison support, merchant callback and actual provider retry
limits must be confirmed before deployment. Retain financial audit and unknown
paid obligations. Refund and public remote-admin authentication need separate
business/security acceptance. A successful offline fixture is not WEB-01 TLS or
merchant acceptance. Rollback unmounts ingress/worker; preserve durable inbox.

## Design/prototype delivery and evidence

LegacyNotificationInbox is a library with no listener, API mount, environment
activation or automatically started worker. Tests explicitly instantiate it over
a temporary existing CheckoutStore. Durable accept precedes processing, unknown
PII fields are discarded, capacity is bounded, and duplicate APPLIED rows never
requeue. Processing reuses the original signature/GET verification and monotonic
financial ledger; it never claims/grants service. Worker leases fence late ACK,
backoff is bounded, and five failures or expired worker crashes quarantine.
Rollback preserves inbox and financial audit. No production BI-SNAP adapter is
invented. Public infrastructure integration is BLOCKED pending separate approval.

Focused **38 PASS / zero FAIL/ERROR/SKIP**:
`test_notification_inbox test_qris_http_v2 test_checkout_reconciliation test_midtrans_verify`
via tools/run_kiosk_unittests.py. Six inbox cases cover durable dedup/reopen,
no provider wait at intake, private-field exclusion, outage/backoff/quarantine,
expired worker fencing, bad signature/capacity/adapter rejection, stale refund
reconciliation and repeated worker-crash exhaustion. Public HTTPS/TLS/merchant
retry/hosting/remote-admin gates remain NOT_RUN, not inferred from offline tests.
