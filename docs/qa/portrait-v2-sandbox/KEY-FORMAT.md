# BUG-020 — Sandbox dashboard Server Key format

## Scope and evidence — 28 October 2026 (Asia/Jakarta)

The owner's Windows trial stops immediately after hidden Server Key entry.
A local diagnostic reproduces `ValueError` in `trial_environments`, before any
provider request. The owner then supplies a screenshot showing both the
`dashboard.sandbox.midtrans.com` host and Sandbox environment, with a Server Key
beginning `Mid-server-`. No complete credential is requested, read or retained.
The installed source SHA is unknown; the same local rejection exists at the
verified branch head `a62721fe185d360367472e968ca7ec2f97823c50`.

The earlier advice that this prefix necessarily identifies Production was too
strong. Official [account guidance](https://docs.midtrans.com/docs/midtrans-account)
instructs obtaining keys from the selected environment; the
[authorization guide](https://docs.midtrans.com/docs/api-authorization-headers)
uses an `SB-Mid-server-` example, without establishing that all Sandbox keys must
use it. The screenshot establishes what this dashboard displays, not whether
Midtrans will authenticate the complete key. Actual merchant acceptance remains
pending.

## Reviewed sources before code

Read AGENTS.md; root README; docs/README.md; DEVELOPMENT_PROTOCOL.md;
DEVELOPMENT_HANDOVER.md; ARCHITECTURE.md; portrait-kiosk-v2-technical-design.md;
DECISIONS.md; FEATURE_STATUS.md; portrait-kiosk-v2.md; bug_tracker.md;
next_step.md; test_checklist.md; gui-v2-branch-audit.md; advertising-and-qris.md;
this Sandbox runbook and the pending-acceptance runbook. Inspected the existing
launcher, v2 environment adapter, backend factory, provider transport, tests and
portrait workflow. Remote reference `feature/qris-payment` remains at reused
source `3cc8a8e360e8c2100a3077b755664eb61d0216ea`; no branch switch or merge.

## Bounded correction (plan recorded before code)

Reuse the launcher and Sandbox-only payment services. Accept complete printable
ASCII Server Keys beginning either `SB-Mid-server-` or `Mid-server-`, at most
512 characters. Reject client keys, empty suffixes, whitespace/control characters
and malformed/oversized values without exposing the input. Do not infer provider
environment from key spelling or rewrite the key. Keep the fixed HTTPS Sandbox
host, redirect refusal, server-only credentials, independently verified payment
admission, persistent profiles/journals, and printer/Drive-off trial unchanged.

Reproduce the new-format failure, then check both key formats through launch,
v2 isolation and create/status/cancel transport; run the applicable full local
regression once after the final functional edit and verify matching-source CI.
No real merchant request or payment is performed here. Windows hidden-paste and
official-simulator acceptance require the owner's local test. Roll back only the
scoped source change after inspection; preserve all journals/photos/queues.

## Results

Functional source **`6a271de6bc263851fae6ef688ae99aa063b2ea2a`** is pushed and
remote-verified on `feature/portrait-kiosk-v2-next`. The launcher-only correction
is implemented. The provider, backend factory,
v2 environment adapter and all photo/Drive/payment state services are unchanged.

- [Before](key-before-tests.txt): two tests, two errors at the old prefix guard
  for the reported format. No actual credential or provider request.
- [Focused checks](key-focused-tests.txt): 136 PASS, zero failures/errors/skips,
  0.420s. Both formats preserve server-only credentials and v2 printer/Drive-off
  isolation. Create/status/cancel always target the literal Sandbox HTTPS host
  and preserve the original Basic Auth key; HTTP 401 propagates without any
  Production fallback. Existing independent verification, grant, idempotency,
  cancellation-race and recovery checks also pass.
- [Tested-source hashes and environment](key-tested-source.json) identify seven
  relevant source/test files, including unchanged runtime adapters/transport.
- [Full local regression](key-full-tests.txt): **901 run / 898 PASS / 3 optional
  native palm-assets SKIP / zero failures/errors**, 277.362s. The skipped cases
  are camera-recovery palm inference, v2 palm countdown, and standalone native
  palm inference; none is a credential/payment test.
- Matching-source [CI 40572395949](https://github.com/pratikto/PhotoBooth/actions/runs/40572395949)
  has **all three jobs SUCCESS**: Linux navigation/audio lifecycle, Linux native
  synthetic GUI/Sandbox and Windows portable/native dummy audio. The CI Sandbox
  group has 142 PASS/zero skips. [Exact job summaries](key-ci-result.json).
  The pure job skips one real-Kivy logging integration because Kivy is absent
  there; that case passes in the local full run. Native CI skips its optional
  real-palm model case. No new GUI layout was introduced.

Local checks and CI do not establish actual merchant authentication, official
simulator acceptance or Windows hidden-input behavior; those remain NOT_RUN.

Focused command (existing Kivy venv; offline protocol fixtures):

```text
python tools/run_kiosk_unittests.py test_qris_sandbox_launcher test_midtrans_sandbox test_kiosk_v2_sandbox test_midtrans_verify test_qris_api test_qris_http_v2 test_checkout_backend test_checkout_durability test_booth_auth test_qris_session test_qris_kiosk_client test_qris_images test_payment_quote
```

Final full command: `python tools/run_kiosk_unittests.py`, with
`PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1`, software
OpenGL/offscreen SDL and dummy audio. Local HTTP fixtures require the managed
command's network permission; these checks do not call Midtrans.

## Continue on Windows

Close the GUI and use the existing checkout/Kivy venv:

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
python tools/run_portrait_v2_sandbox.py
```

Use the Merchant ID and complete Server Key from the visibly selected Sandbox
dashboard. Paste the key unchanged into the hidden prompt; never prepend `SB-`.
Local readiness still does not authenticate the merchant. The first actual
Sandbox order checks the key with Midtrans; finish the existing official
simulator trial before recording acceptance. Preserve any pending/recovery
journal; no reset or new payment is a diagnostic workaround.
