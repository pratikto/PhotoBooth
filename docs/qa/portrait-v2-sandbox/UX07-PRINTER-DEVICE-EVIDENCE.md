# UX-07.f — explicit read-only printer route evidence

29 October 2026 (Asia/Jakarta). Base/remote verified
`c8f048358aae2d475cd06f3be5269f0f3124d24d`, clean existing feature branch.
The UX-07.e MOCK validation is complete. Purchased-print payment/preflight
integration and real Windows/Ubuntu device acceptance remain NOT_RUN.

## Contract before implementation

Reuse `tools/check_portrait_v2.py` and its existing P5 inventory, source metadata,
atomic JSON writer, original `load_printer_config` and `check_printer`. The
current inventory deliberately never probes devices; preserve that default.
Add only an explicit `--probe-printer` option for an ordinary local diagnostic.
Do not call it automatically from a launcher, GUI, payment or fulfillment path.

Without the option, do not load printer settings or call a printer probe. With
the option, refuse dedicated Sandbox mode before settings/probe access. Otherwise
load the same saved-settings/environment fallback as the app, afresh each time,
and perform the existing read-only route/queue/node observation. Never construct
ThermalPrinter, send print bytes, read orders/photos, call a payment/Drive service,
or change configuration, rewards, financial or fulfillment rights.

Export only an allowlisted status and fixed explanatory text, not the probe's
message, settings, queue/host/address, paths or exception details. Unknown values
and exceptions become generic UNKNOWN. A non-ready or refused requested probe
makes this diagnostic preflight NEEDS_ATTENTION; an omitted probe does not.
Keep every physical/provider acceptance field NOT_RUN and explicitly add the
purchased-print payment/preflight gate as NOT_RUN even if a route is READY.

READY is only a point-in-time route/queue/node observation. It never proves
paper, printable output or purchased QRIS service. Original TCP timeout is per
route; **Windows spooler API latency is not bounded by this adapter**. A slow
spooler may hold this explicit CLI invocation; no GUI/background polling is added.

Reviewed: AGENTS/protocol, index, current checkpoint/handover/status/backlog/bugs,
architecture/decisions/technical design, AR master/roadmap/readiness/operations/
matrix/AR-13, UX-07 MOCK/prepayment contracts and evidence, P5/combined acceptance,
original printer health/settings and inventory/CLI/MOCK/native tests/workflow.

Acceptance: causal tests for default no-probe, Sandbox refusal, fresh config,
original read-only transport reuse, exception/status redaction, immutable
acceptance gates and actual CLI report persistence. Register on Windows/Linux;
focused checks before pushing, one applicable full regression after source is
final, current CI with actual method evidence, then final checkpoint. All local
probes use synthetic transports; real device observations remain NOT_RUN here.

Rollback is inverse diagnostic/CLI/tests/docs only. No schema/data migration;
preserve all financial, claim, fence, media, audit and retention records. No OPS,
new payment path, public infrastructure, branch/default/master change or real
device/provider/print/Drive effect is authorized by this preparation increment.

## Source implementation and focused evidence

The existing `tools/check_portrait_v2.py` now accepts `--probe-printer`; its
no-option behavior still performs no printer configuration/probe access.
The inventory includes a redacted `printer_route` section and a permanently
NOT_RUN `purchased_print_payment_preflight` acceptance field. A requested
non-ready or Sandbox-denied observation sets NEEDS_ATTENTION. No checkout,
payment, photo/print worker, original transport, settings or database changed.

**45 focused PASS / zero FAIL/ERROR/SKIP**, 0.262s, Python 3.12.14/Debian 13.
Seven new causal methods include original fake TCP/Windows queue observations,
close-without-send, byte-identical synthetic settings/financial/media markers,
fresh settings/no cached success, redaction and real CLI JSON persistence.
Default CLI also executes under `python -S` without native/site packages.
Expected pre-implementation: seven methods/twelve missing-interface errors
(including subtests); no production defect inferred. Intermediate 45 PASS/0.275s
precedes the final CLI status line. [Commands/source/digests](evidence/ux07-printer-device-evidence.json).

Registered in Windows ledger/Linux Sandbox CI; the existing Linux annotation
checker now requires these seven method PASS lines as well. Full/current CI
pending for the containing source push; next run one final full at that SHA,
verify both-platform method evidence, and checkpoint. Matrix remains 59/0/9/1;
UX-07 whole gate NOT_RUN. No actual printer was probed in cloud QA.

## Collect evidence on the actual Windows or Ubuntu device

Use the existing environment and ordinary local diagnostic context, with the
GUI closed and no print send in progress. Do not change Sandbox isolation flags
to force a probe; never erase an uncertain print record. First run the default
inventory, then explicitly request a route observation with a new output name:

```text
python tools/check_portrait_v2.py --output data/diagnostics/ux07-inventory-20261029-1.json
python tools/check_portrait_v2.py --probe-printer --output data/diagnostics/ux07-printer-route-20261029-1.json
```

Use a different filename for each later observation to preserve prior evidence.
The same commands work on Windows/Ubuntu; the original adapter selects the OS
routes. No new printer configuration is written. Keep reports private and
check only source/OS/status/limitations; do not paste local settings or driver
output. `ready` confirms a route/queue/node only; `unknown`, `warning`,
`unavailable` or `denied_sandbox` cannot certify readiness. No new flag can
mark paper output or purchased-print payment/preflight acceptance PASS.

This adds a way to collect the still-missing observation; it does not mount a
purchased-print payment path or replace the separately required actual device,
paper, merchant, privacy/support and release acceptance. Original Windows
spooler calls can block this explicit CLI; there is no imposed API deadline.
