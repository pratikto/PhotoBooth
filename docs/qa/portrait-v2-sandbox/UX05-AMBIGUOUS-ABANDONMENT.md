# AR-01/09 — UX-05 ambiguous payment abandonment

29 October 2026 (Asia/Jakarta). Base/remote verified
206f408efd369d85d40774861edd7746c4a6050a; existing feature branch only.
Contract before code. Reviewed governance/protocol/prompt, checkpoint/handover,
current index/status/backlog/decisions/matrix, master/roadmap, AR-01/02 creation/
reconciliation, AR-06 capability, AR-09 operator/release, operations/privacy and
Midtrans provider contract. Reviewed actual backend/store/client/controller/
Sandbox adapter, release worker and existing HTTP/creation/cancel/claim tests.
Reuse tests.qris_v2_fixture and real HTTP/SQLite/controller/worker boundaries.

1. Lost creation reply, outage and repeated provider 404: explicit cancel/leave
   intent cannot replace identity, bill again, close uncertainty, discard claim
   hash/frozen order, release booth or expose prior customer data. Restart keeps
   same identity; operator abandon/release cannot invent a terminal state.
2. Cancel reply/status unavailable and settlement race: keep original claim,
   authoritative paid OWED and one grant, private until fresh original proof.
   Only deliberate typed worker isolation + exact two-phase ACK/archive can
   free occupancy for a new visitor after payment is known paid.
3. Cancellation independently confirmed terminal after restart: evaluate actual
   behavior, require durable local separation before accepting another visit.
   No cancellation from local timeout/QR countdown/404 or stale cached evidence.
   Test archive write failure and exclude any prior paid/grant/photo entitlement
   from an unpaid-terminal shortcut. Never clear ambiguous state to meet UX.

First micro-increment covers conservative uncertainty/race holds; UX-05 remains
NOT_RUN until combined safe release/terminal evidence completes. Tests first,
minimal runtime change only if a defect is reproduced; focused checks/docs/
commit/immediate push/remote verification per increment. Tests-only changes keep
prior full/native source provenance; one full regression after final runtime fix.
Only synthetic fixtures, no actual merchant/charge/cancel, camera/paper/Drive or
production/OPS/public ingress/branch/default/master operation. Reopens are new
controller/DB connections, not a claim of actual power loss. Raw tickets stay in
memory; no logs/images/databases/customer data published. Rollback inverse source
only; preserve all financial/action/claim/fence/manifest/history records.

## 29 October — UX-05.a conservative abandonment holds

Base/remote verified `206f408efd369d85d40774861edd7746c4a6050a`.
Two new real HTTP/SQLite/controller cases cover lost creation reply + repeated
404 + operator abandon/release denial, and cancel outage/reopen/late settlement.
One original order/key/fingerprint/hash/OWED preserved, no replacement POST,
private restart/no QR; original ticket alone later obtains one grant. Expected
409/503 codes asserted, not arbitrary exceptions. Reopen uses explicit lease
retirement (initial fixture attempt two ERROR corrected, no runtime defect).
**33 focused PASS / zero failure/error/skip**, 2.337s, Python 3.12.14/Linux.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_ux05_abandonment test_checkout_creation_attempts test_checkout_release test_release_session test_customer_claim_session` (SDL offscreen/dummy audio).
Tests/workflow/docs only, runtime unchanged at 3822bb0. New module registered
in both Linux/Windows ledger groups; matching CI pending. UX-05 stays NOT_RUN
until confirmed-terminal and combined paid isolation/archive acceptance tested.
Matrix 57/0/9/3 unchanged. Next test confirmed cancellation after restart and
paid proof -> PREPARE -> typed worker isolation -> ACK/archive -> new visitor;
fix only a reproduced defect. No production/OPS/public ingress/new branch/
master/default/device/provider effects. Only work/ scratch local. Rollback
inverse tests/docs only; retain all financial/claim/fence/media/history records.
