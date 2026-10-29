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

## 29 October — UX-07.f full-run fixture correction focused-verified

Collector source `45b0b30`, CI **40893472588 all three jobs SUCCESS**; seven new
methods individually PASS Windows/Linux (groups 130/431 PASS; native 112/one
SKIP). Full at that source: **1185 run / 1180 PASS / zero FAIL / one ERROR /
four SKIP**, 534.098s. Error is original ad-player retirement fixture: fixed
0.1s pump can end before positive exposure, then events.write.call_args is None.
No collector method failed. Failed full remains evidence, never promoted PASS.

Reviewed original ad accounting/lifecycle contracts and code. Tests/CI-only
correction waits for a real positive tick within a bounded wait, preserves all
old assertions, adds positive-before-close and exactly-once recording checks.
Old delayed/cold-frame fixture fails; corrected delayed case PASS; held-tick
negative control still FAILS as required. **49 focused PASS / zero skip**, 1.390s.
Original ad GUI/runtime unchanged; no image/decoder/accounting behavior patched.
Four original ad-player tests now registered/opted in and method-checked in
Linux native CI. Next repeat the applicable full and current CI at this tests-
only micro-push, then final checkpoint. [Exact history/control evidence](evidence/ux07-printer-device-evidence.json).
UX-07 whole gate NOT_RUN; matrix **59/0/9/1**, all actual hardware/merchant/
paper/privacy/release gates remain separate. No financial/media records touched.

## 29 October — UX-07.f device evidence collector verified

Functional source `45b0b3058720ac71875240a9d4e2edf449ecc843`; corrected test/CI
source `b6c3d015f85100939c86925155e7a1b0f6e5b09f`. Final full **1185 run / 1181 PASS /
zero FAIL/ERROR / 4 optional SKIP**, 504.379s, Python 3.12.14 /
Debian 13 software GL/dummy audio. Fresh corrected focused **49 PASS**, 1.390s,
zero failure/error/skip; initial collector focused 45 PASS remains historical.
**CI 40896422532 all three jobs SUCCESS** at the corrected source: seven new
collector methods individually PASS Windows/Linux, four original ad-player
methods individually PASS Linux. Windows groups **130/72/55/103 PASS**, zero skips;
Linux Sandbox **431 PASS**, native **116 PASS/1 SKIP**, pure
**128 PASS/1 SKIP**, supervisor **40 PASS**. Actual method receipts
verified via logs/check annotations. [Commands/source/digests/history](evidence/ux07-printer-device-evidence.json).

The first full at 45b0b30 remains **1185/1180/one ERROR/four SKIP**, 534.098s:
original ad fixture's fixed 0.1s pump could close before a positive exposure
interval. Test-only bounded causal wait preserves original assertions and adds
positive duration/exactly-once recording; delayed case passes and held-tick
negative control still fails. All ad GUI/runtime and collector code remain
unchanged by that correction. Four ad tests are now actually registered/opted
in in Linux CI; prior successful CI did not run that module.

Existing P5 CLI now offers `--probe-printer`: default no printer access, dedicated
Sandbox refusal before settings/probe; original saved config/route probe reused,
status-only redacted report. Requested non-ready probe requires attention.
Even READY leaves paper and purchased-payment acceptance NOT_RUN. No order,
print bytes, payment/Drive action or financial/media mutation; no GUI mounting.
Route/queue/node never proves paper; Windows spooler API latency remains
unbounded. [Actual-device command and contract](UX07-PRINTER-DEVICE-EVIDENCE.md).

This software preparation increment is verified. **UX-07 whole purchased-print
payment/device gate remains NOT_RUN**, matrix **59 PASS / 0 FAIL / 9 BLOCKED /
1 NOT_RUN**, audit IN_PROGRESS. Actual Windows/Ubuntu printer observations and
purchased-print prepayment integration remain missing; keep Sandbox printer/
Drive OFF. PAY-22/WEB-01–08 and actual merchant/paper/phone/Drive/deletion/
privacy/support/release gates remain separate. No OPS/public/production deployment or new branch/default/master change. Next collect real read-only evidence and resolve the
purchased-print path within its scope; never infer paid-print acceptance.

No new local screenshot review: CLI/test-only scope; prior GUI images retain
original source/hashes. Rollback the diagnostic/test/CI/docs inverse only,
preserving every financial/reward/claim/fence/media/audit/retention record.
Private work/ reports/fixture-control scripts are local-only, not backed up to
GitHub; no unpublished runtime patch. Final docs SHA is its containing Git
commit; last verified source checkpoint is the full b6c3d01 SHA above.
