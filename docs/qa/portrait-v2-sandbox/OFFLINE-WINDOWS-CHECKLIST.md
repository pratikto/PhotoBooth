# Offline Windows owner acceptance worksheet

12 November 2026 (WIB). Owner requests a detailed, checkable offline HTML file
that generates a plain-text result/handoff for another Codex account.

## Contract before artifact implementation

Produce one self-contained Indonesian HTML file under artifacts/, with no
external scripts/styles/fonts, network calls, server, credentials or backend
integration. Reuse the current Windows acceptance guide and WN02–WN11 case IDs.
Commands remain manually executed by the owner; worksheet buttons never start
the booth, print/upload/pay, modify customer history or send reports anywhere.

Support per-item PASS/FAIL/BLOCKED/NOT_RUN, checkboxes, local browser autosave,
bounded validated JSON backup/import, print, and generated plain-text download/
copy suitable for a cross-account Codex handoff. Record the actual tested SHA
as unknown unless explicitly provided, independent of the known software
baseline. Distinguish owner observations from independently verified evidence.
Normal-flow completion never means commercial release. Deferred destructive
fault/refund cases remain fixed BLOCKED and cannot be checked as passed.

Issue notes are an OPTIONAL separate personal worksheet feature, not a change
to the existing strict/redacted official acceptance journal. Explain that
distinction. Redact recognized proof/key/URL/path patterns before persistence
and export, require reviewing output before sharing, and do not claim complete
PII/secret detection. Never render imported user data as HTML. Reject malformed,
oversized, wrong-version or unknown-item imports without replacing valid state.
Clear only this worksheet's local browser state with explicit confirmation;
never touch the original customer root or application data.

Verify in Chromium with networking disabled: check/uncheck and case aggregation,
autosave/reload, localStorage refusal fallback, TXT/JSON generation/download,
valid and invalid imports, redaction, locked deferred gates, no injected HTML,
print and narrow/wide layout. Application runtime is unchanged; do not rerun
the completed application CI suites for a documentation/artifact-only change.

Deliver the standalone file, micro-push to the existing authorized branch and
verify remote SHA. No publishing/deployment, real devices/accounts or refunds.


## Delivered artifact and verification

[Standalone Indonesian HTML](artifacts/meong-windows-acceptance-offline.html):
110 items in13 groups, including104 active items and6 fixed deferred/BLOCKED
items. Formal WN02–WN11 aggregation requires every subitem to pass. Software
baseline is explicitly separate from the owner's actual tested Git SHA.

Open the HTML in Chrome/Edge. Check actual observations, select FAIL/BLOCKED as
needed, and optionally enter a short issue note without private information.
Use **Buat teks untuk Codex**, **Salin teks**, or **Unduh .txt** to share a full
or concise report. Those actions always regenerate current results, even if an
older preview exists. Top shortcut and sidebar link reach the report directly.
JSON export/import backs up answers when changing browser/file location.
Autosave is browser-local, not embedded into the HTML file. No report is sent
automatically. This personal worksheet does not replace Action Record/Show in
the strict original acceptance journal. Completion never enables commercial use.

Final66 automated browser checks PASS, networking disabled, zero external
resource requests. Checkboxes/case aggregation, current TXT download/copy,
JSON round-trip/rejected versions/unknown IDs/oversize/deferred PASS, autosave,
storage refusal, pattern redaction and bounded notes, literal imported HTML,
print/PDF and375/768/1440 layouts verified. Initial narrow viewport revealed an
unbroken static simulator URL overflow; fixed with text wrapping. One cosmetic
stale label on reset corrected. The final suite passes with zero page errors.

Managed Chromium blocks direct file:// navigation by administrator policy;
QA fulfilled the identical standalone document at a loopback origin in an
OFFLINE browser context, with no listening server/network. Actual Windows
file-opening/storage/clipboard/device acceptance is not independently certified.
The clipboard API test captures the exact report payload; fallback leaves a
selectable preview and TXT download when automatic clipboard access is denied.
Recognized redaction patterns help but cannot guarantee all personal/secret
content is removed. Owner must review the generated preview before sharing.

Developer reproduction (Playwright and Chromium already installed in the QA
environment; owner HTML needs neither Python nor these packages):

```bash
.venv/bin/python docs/qa/portrait-v2-sandbox/artifacts/verify_offline_checklist.py
```

Optional MEONG_CHROMIUM selects a Chromium executable. The verifier creates
only synthetic local test output under /tmp; no booth/provider/Drive effects.
[Exact source hashes and66 checks](evidence/offline-windows-checklist-2026-11-12.json).
Application runtime/tests/workflow are unchanged; do not rerun their completed
CI suites for this documentation-only artifact. Merchant, refund, recovery,
original-root and commercial gates from the current checkpoint remain intact.
