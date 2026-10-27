# Saved local Sandbox credentials

## Owner request and reviewed scope — 28 October 2026 (Asia/Jakarta)

The owner explicitly requests storing Merchant ID and Server Key in the existing
ignored local settings instead of re-entering them in the terminal. This
supersedes the earlier prompt/environment-only credential-source policy. Base
and verified remote head: `c001095c5ca98aae39f7a6c7cdd998e26b2a2573` on
`feature/portrait-kiosk-v2-next`; QRIS reuse reference remains `3cc8a8e`.

Reviewed before code: AGENTS; root README and documentation index; protocol;
handover; architecture/technical contracts; decisions; feature/bug status;
roadmap/backlog; test ledger; branch audit; Sandbox runbook and BUG-020 evidence;
the existing storage setup guide, ignored-settings example, shared launcher,
v2 adapter, Apps Script configuration loader and current tests/workflow.
Earlier documentation was reviewed in this conversation; the additional shared
settings contract and current source were read before this increment.

## Bounded plan

Read two Sandbox-specific literal string assignments from
`photobooth/local_settings.py`, whose exact ignore rule already exists. Preserve
its existing Drive settings and never write or inspect the owner's private file.
Publish only blank optional fields in `photobooth/local_settings.example.py`.

Credential-source precedence is by pair: if either existing MIDTRANS environment
value is supplied, retain the environment/prompt behavior and do not mix in
file credentials. Otherwise use saved Sandbox defaults and prompt only for
missing values. Do not execute/import settings; parse top-level string literals
(including annotated assignments and UTF-8 BOM) without side effects. Bad syntax,
unreadable content or computed credential values stop before child startup with
a fixed, non-secret diagnostic. Keep keys out of GUI environment, argv and logs.

Reuse the current launcher/backend, fixed Sandbox endpoint and both Server Key
formats. Preserve v2 printer/Drive-off isolation, stable merchant/booth profile,
payment verification/journals and no replay. No actual credential, payment,
Google deployment or customer data is used for validation.

Add offline fixture tests for source precedence, no repeated prompts, no settings
execution, safe errors, ignored target and backend-only credentials. Run these
in existing Linux Sandbox CI and Windows stdlib-only CI. The local execution
environment became unavailable before edits; record local checks as NOT_RUN
unless it returns, and use matching-source CI rather than borrowing earlier
901-test results. Preserve all prior source-specific evidence.

## Results

Implementation/CI pending. Windows hidden input, actual merchant authentication
and official simulator acceptance remain separate from automated fixtures.

## Setup after updating

Add to the existing `photobooth/local_settings.py`, keeping its Drive values:

```python
MIDTRANS_SANDBOX_MERCHANT_ID = "YOUR_SANDBOX_MERCHANT_ID"
MIDTRANS_SANDBOX_SERVER_KEY = "YOUR_COMPLETE_SANDBOX_SERVER_KEY"
```

Use the exact key from the Sandbox dashboard; no prefix rewrite. Then launch
`python tools/run_portrait_v2_sandbox.py` as before. No prompts are needed when
both saved values are filled and neither existing MIDTRANS environment value
overrides the pair. Existing environment overrides can be cleared with:

```powershell
Remove-Item Env:MIDTRANS_MERCHANT_ID -ErrorAction SilentlyContinue
Remove-Item Env:MIDTRANS_SERVER_KEY -ErrorAction SilentlyContinue
```

Values must be quoted UTF-8 Python string literals, not imports, function calls
or expressions. The ignored file is plaintext on the machine; Git ignore does
not encrypt it. Do not overwrite an existing settings file with the example or
force-add the private file. Rollback only source after inspection; preserve
private settings and all payment/photo/Drive state.
