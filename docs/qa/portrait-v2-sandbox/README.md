# P4b Sandbox → P5 readiness (FEAT-020 / FEAT-022)

31 October — [expiry renewal/new-ticket/30s idle guide](UX07-LAPTOP-CHECK.md#jika-qr-pembayaran-kedaluwarsa-saat-l02). BUG-026 source verified: full1251/1247PASS/4optionalSKIP; corrected-source CI41205340183 all three SUCCESS. Actual owner simulator/device acceptance remains manual.

**Current owner laptop check:** [44-step beginner guide](UX07-LAPTOP-CHECK.md)
and [offline tick/copy form](windows-checklist-ux07.html). Includes setup, actual
button names, expected results, per-item notes and partial NOT_RUN reporting.
Latest verified l2 fixtures retain ca7827c/full1229/1225 PASS/4optional SKIP and
CI40985975287 all three SUCCESS; actual laptop/merchant and commercial gates
remain separate. See the [current checkpoint](AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 30 October — mock purchased-print chain verified

Seven source/test micro-pushes through2cac0ba (functional e82d0ee); atomic original
order/requirement issuance, mock readiness/purchase, paid print no-replay jobs,
native result-worker fixture and original HTTP/recovery compatibility verified.
Full **1221 run/1217 PASS/4 optional SKIP**, zero failure/error;
CI40970539519 all three jobs SUCCESS,25 pure methods Windows/Linux and2 native
methods Linux. Earlier native-audio full failure retained; isolated unchanged
repeat and final full PASS, initial cause unproven. No runtime guard relaxed.
Whole UX-07 NOT_RUN, matrix59/0/9/1, AR-13 conditional/audit IN_PROGRESS. Next
UX-07.l2 original claim/pause/resume/safe-release lifecycle contract/fixture;
commercial mounting/operating policy and actual devices/provider/release remain.
Sandbox delivery OFF; no production/OPS. [Exact evidence/limits/next](evidence/ux07-paid-chain-final-verification.json).

**Current implementation update, 29 October:** source progressed through AR-09.c1;
[exact commits/tests and unfinished work](CONTINUATION-2026-10-29.md).
Dated design-only/audited-baseline statements below are historical scope; they do
not override current implementation evidence or certify full matrix/device/
production acceptance. Safe release, AR-10–13 and external gates remain pending.

**28 October — BUG-021:** polling retains the verified stored QR image URL when
PENDING status omits actions. Explicit replacements remain validated; expiry,
settlement and uncertain-verification guards remain. [Evidence and limits](QR-POLLING.md).

**28 October — centered Meong QR logo:** v2 reuses the existing Drive renderer
and approved artwork for the independently decoded provider payload. Full-size/
compact checks and an exact-payload guard protect the result; failures retain
the original image. The original download/simulator URL and payment authority
remain unchanged. [Source, tests and native previews](QR-LOGO.md).

**28 October — BUG-020:** the owner's Sandbox dashboard displays a Server Key
beginning `Mid-server-`. The launcher now accepts that format and `SB-Mid-server-`
without rewriting the credential. Copy the complete key from the Sandbox
dashboard; its prefix alone does not prove environment or validity. Requests
remain fixed to `https://api.sandbox.midtrans.com`, with redirects refused.
[Reproduction, tests, update and limits](KEY-FORMAT.md). This supersedes the
older prefix-only expectation at the end of this record.

**Current implementation note.** The adapter and P5 stages described below
were completed; future-tense stage descriptions are the original plan, not
outstanding implementation tasks. P5 source `9433010` and subsequent health
source `ea394e8` have separate evidence packages. Actual merchant simulator
acceptance and trusted QRIS game promotion remain outstanding.
[Current ledger](../../test_checklist.md).

Owner explicitly approved QRIS Sandbox and subsequent P5 preparation on 2026-10-24,
with Windows manual tests at the end. Production payments, scanner activation,
deployment, merge and release remain outside scope. Baseline/rollback:
`d6fb5d4e57c86073437748360576c7e4b8adac8b` on `feature/portrait-kiosk-v2-next`.

The last visual/audio retest is owner-reported **8/8 PASS**, followed by “udah
clear semua”; tested HEAD/device metadata remain unknown. Earlier twenty-cycle
reports remain preserved. BUG-017 is owner-reported PASS / monitoring: no new
decoder patch or measured cause is claimed. See [raw record](owner-acceptance.json).

## Stage 1 — reuse existing payment service

Reuse the latest QRIS branch `3cc8a8e360e8c2100a3077b755664eb61d0216ea` read-only.
[Hashes](reused-source.json) cover the unchanged backend/client/session, launcher
helpers and relevant original tests. No branch merge or v1 GUI replacement.
Server quotes, authenticated booth identity, durable idempotency, one-use grants,
provider reconciliation and restart recovery remain in the original code.

The legacy `app_qris`/`ui_qris` binds v1 capture and layouts. The v2 presentation
adapter will use accepted v2 widgets and the existing payment client/session;
this compatibility exception does not replace backend logic. The original
service has no trusted Meong Fly promotion contract: local wins cannot authorize
a provider discount. Sandbox full-price checkout must show explicit consent
before discarding a local DEMO offer. Trusted merchant promo remains an external
gate. No merchant credentials or external provider calls are used in cloud QA.

Stages: unchanged service + focused tests; native v2 handoff + isolated Sandbox
launcher + focused integration; P5 readiness tooling, one final regression,
800×1280/452×900 evidence and a final Windows form. Real merchant, hardware,
printer/Drive/privacy/retention acceptance cannot be certified by fixtures.

Stage 1 verification: 124 original focused tests PASS (0 errors/failures), Linux Python 3.12; command loads the twelve test modules recorded in reused-source.json. Initial migration-test missing dependency was corrected by retaining unchanged historical `payment_orders.py`; the active backend does not use that prototype. [Output](reuse-tests.txt).

## Stage 2 — native v2 Sandbox adapter

The ordinary `python tools/run_portrait_v2.py` keeps real payments disabled.
New `python tools/run_portrait_v2_sandbox.py` reuses the existing merchant trial
launcher, with only injectable GUI entry/environment/notice arguments added to
that helper. This is the sole reference-file compatibility difference after
Stage 1; all payment service/client/journal files remain byte-identical.

Install in the existing Windows Kivy venv:

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
python -m pip install -r requirements-qris.txt
python tools/run_portrait_v2_sandbox.py
```

Optionally save the Sandbox pair as literal strings in the existing ignored
`photobooth/local_settings.py`, alongside its unchanged Drive settings:

```python
MIDTRANS_SANDBOX_MERCHANT_ID = "YOUR_SANDBOX_MERCHANT_ID"
MIDTRANS_SANDBOX_SERVER_KEY = "YOUR_COMPLETE_SANDBOX_SERVER_KEY"
```

[Saved-settings details, environment precedence and tests](LOCAL-SETTINGS.md).
Complete saved values remove both terminal prompts. Existing MIDTRANS environment
overrides select the pair first and never silently mix accounts with saved values;
missing fields are prompted locally. The launcher reads literal values without
executing the settings file. Never paste keys into chat, command arguments or
tracked files. The GUI child environment receives booth authentication only. The helper owns a loopback backend and
prints the official simulator URL/current verified QR image URL. Do not scan
with a banking/wallet app. Backend readiness does not prove valid merchant
credentials; the actual official simulator trial is a remaining device gate.
Printer and Drive are disabled in this dedicated trial. No production endpoint
is supported. A conflicting MOCK flag/direct merchant key in the GUI fails closed.

Flow: gallery → QRIS SANDBOX → explicit full-price/no-game-promo confirmation →
provider QR → backend verifies settlement → stable one-use grant → existing
explicit P3 photo consent → durable STARTING journal → one local photo transaction
→ server STARTED acknowledgment → manual camera countdown → all photo sessions
complete → server COMPLETED acknowledgment → finish/idle. The Sandbox profile
and photos are isolated under `data/kiosk-v2-sandbox/<merchant>/<booth>/`.
No free-photo test bypass is available in this mode. Existing default P3 and
local MOCK paths retain their prior behavior.

Retry keeps the same checkout key/order. Cancellation racing settlement preserves
the paid permit. Uncertain network status cannot return to gallery or create
another charge. Abort or restart after capture might have started enters operator
RECOVERY; never delete the journal or replay photos/prints to clear it. Operator
checks backend order/service state and the bound local manifest first; no automated
refund, recovery override, capture replay or print replay is supplied.

The new UI adapter uses the accepted native font/frame/audio and existing P3
worker. Payment calls/QR fetching run on reused single-flight GameJobs; checkout
lease closes after worker I/O ends. Pending payment has no browse timeout. Windows
minimize suspends UI input, preserves journals and does not grant another session.

Ten native screenshots (five states at 800×1280/452×900) were visually reviewed:
amount, QR, consent and actions fit; no layout overflow observed. They are offline
HTTP fixtures with an explicitly nonpayable QR, **not** merchant acceptance. Final
P5 evidence will be regenerated at the final functional source.

Stage 2 verification: **195 focused PASS**, 0 failures/errors/skips, 23.535s. Includes unchanged backend/HTTP/session/launcher tests, new HTTP-to-GUI-to-P3 tests, and prior MOCK/navigation/audio regression. [Output](adapter-tests.txt). New screenshot commands: `python tools/render_portrait_sandbox.py --output-dir <folder> --width 800 --height 1280` and repeat at 452×900.

## Sandbox account access clarification — 25 October 2026

Midtrans documents that Sandbox is created automatically at sign-up, for free
test transactions. Production merchant approval is separate. In the existing
account choose Sandbox → Settings → Access Keys; read Merchant ID and Sandbox
Server Key locally (both `SB-Mid-server-...` and `Mid-server-...` syntax are now
accepted; see the 28 October correction above).
[Official guide](https://docs.midtrans.com/docs/midtrans-account). No merchant
credentials or official simulator acceptance have been supplied for this v2
trial. Missing access means NOT_RUN, not simulated merchant PASS.
