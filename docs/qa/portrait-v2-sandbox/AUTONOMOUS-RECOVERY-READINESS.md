# AR-08 — prepayment readiness and paid-unfulfilled remedy

29 October 2026, Asia/Jakarta. Read master/operations/matrix/provider, native
AR-07 contract, original device_health/check_disk, AsyncCamera mailbox, template
contract, photo/retention and checkout fulfillment source before this stage.
Existing branch only; Sandbox print/Drive off, no production/refund/deletion.

AR-08.a contract before code: native confirmation obtains a point-in-time fresh
frame observation from the existing nonblocking camera owner. Worker validates
its bounded age, disk capacity using the existing health check, a temporary
exclusive fsynced writable probe in the exact checked photo root, and decode/hash
of every selected artwork/mask. No camera open, photo/shutter/renderer, printer
probe/paper or network/Drive requirement. Sandbox purchased printing is disabled;
reject accidental delivery opt-in. Device health snapshot does not guarantee
future availability or physical service. Probe files contain synthetic bytes only.

Block a new order before flow.begin/provider I/O on missing/stale camera, capacity,
permission or template failure; retain quote with clear corrective message. An
already active order must not be replaced or recharged because readiness fails.
Other modes/default/v1 retain original behavior. Automated synthetic checks and
actual Windows/Ubuntu camera/storage acceptance remain distinct.

AR-08.b following: durable idempotent paid-unfulfilled issue record bound to
original order/booth/grant/allocation, generic allowlisted reason, no raw photo/
secret/customer text. Preserve OWED and all financial/service/media state through
failure/restart; operator may inspect but cannot fabricate refund/completion.

## AR-08.a source and focused evidence

Native new-order confirmation now runs begin_ready on the existing worker.
AsyncCamera's one-second mailbox freshness is observed without camera I/O; worker
allows at most two further seconds for checks and rejects expiration afterwards.
Reuse check_disk's 1 GiB/10% reserve; validate/decode selected template bytes and
perform an exclusive fsynced synthetic probe in the exact checked photo root.
Sandbox delivery opt-ins fail closed. No Drive/network/paper preflight is added.
An active original checkout reuses its identity rather than blocking reconciliation
behind a new readiness test. Failure before flow.begin keeps QUOTE and no order.
Low-level controller/API fixtures remain hardware-independent by design.

Focused **57 PASS / zero FAIL/ERROR/SKIP**:
`.venv/bin/python tools/run_kiosk_unittests.py test_recovery_readiness test_kiosk_v2_sandbox_widgets test_kiosk_v2_sandbox test_device_health`.
Four readiness cases plus native missing-camera/no-charge case cover stale/future
observations, delivery opt-in, low capacity, permission error and missing template.
CI Sandbox group now includes the new readiness module. Physical readiness may
change after observation and still needs Windows/Ubuntu device acceptance.
