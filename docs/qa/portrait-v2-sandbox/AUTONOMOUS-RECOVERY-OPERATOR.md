# AR-09 — operator exceptions and safe kiosk release

29 October 2026, Asia/Jakarta. Read AGENTS/protocol, master/roadmap/operations/
matrix/provider, original RECOVERY plan, launcher/server/client recovery methods,
store action audit and original native operator-health lifecycle before this stage.
Source base: AR-08.b2, exact SHA in checkpoint. Existing branch only.

AR-09.a contract before code: reuse backend's existing optional eight-digit PIN
and rate-limited booth-authenticated operator routes. Dedicated v2 launcher mints
an independent per-launch PIN, passes it only in backend startup environment,
prints it only to the local operator terminal and removes the parent's copy after
spawn. GUI environment, process args, journals and exported reports never receive
it. Original v1 trial/default launcher behavior stays unchanged without the opt-in
v2 environment factory. A new launch rotates PIN without changing customer rights.
No production/authentication reset or public admin endpoint is added.

Following increments: native PIN entry/metadata inspection and audited exception
controls; durable fenced suspension/release preserving OWED and hashed customer
claim, exact release ACK before allowing another customer. Preserve print-uncertain
and Drive obligations; no automatic refund, customer-data deletion or completion.
Physical/remote-admin/merchant/support acceptance remains separate.

## AR-09.a delivered

Dedicated v2 environment factory now mints a fresh eight-digit operator PIN.
Shared launcher prints it only when that backend opt-in exists, spawns backend,
then removes its local environment copy. GUI environment and both command-line
argument vectors exclude it; inherited PINs are discarded. Original trial
without the v2 factory does not enable recovery. Journals/customer tickets and
merchant credentials are untouched. Native entry/release remains next work.

First isolation test FAIL before source. Final **64 focused PASS / zero
FAIL/ERROR/SKIP**:
`.venv/bin/python tools/run_kiosk_unittests.py test_kiosk_v2_sandbox test_qris_sandbox_launcher test_qris_recovery test_qris_saved_credentials`.
Two new tests cover v2 environment isolation and actual mocked launcher spawn/
private local notice. All launchers use fake processes/credentials, no real
merchant/device. Rotate by restarting the dedicated launcher; no default public
PIN or persisted operator credential is introduced.
