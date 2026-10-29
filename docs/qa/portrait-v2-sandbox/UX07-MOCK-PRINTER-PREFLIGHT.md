# AR-08 / UX-07 — opt-in MOCK printer preflight

29 October 2026 (Asia/Jakarta). Base and remote HEAD verified:
`605496ef1e0812eb804dfef219a41569d84cbb4e`, existing feature branch.
Reviewed AGENTS, protocol/prompt, current checkpoint/handover/index/status,
decisions/architecture/technical design, AR master/roadmap/readiness/operations,
UX-07/11 evidence, print/Drive and printer setup contracts. Source: original
check_printer/config loader/transport and fixtures, MockCheckoutStore,
MockCheckoutPresentation, CheckoutViews/GameJobs, configured_test/PhotoJobs,
Sandbox begin_ready/delivery isolation and existing native MOCK fixtures.

## Contract recorded before code

The dedicated merchant Sandbox rejects print/Drive opt-ins. It has no approved
purchased-print payment path; do not mount one, print a payment slip, or infer
production permission from this increment. Ordinary local photo/MOCK already
supports explicit printer opt-in. Add a worker-based QA seam there, reusing the
original read-only check_printer and saved configuration, on its existing
single-flight worker before a **new nonpayable MOCK** order/QR is created.

Without PHOTOBOOTH_V2_PRINT=1, do not read printer configuration or probe routes.
With opt-in, load settings afresh for each new order and require the original
probe's READY observation; warning/unavailable/unknown/exception deny with a
fixed error. No driver messages/addresses/paths reach widgets or worker logs.
Do not cache a prior success, instantiate ThermalPrinter, submit bytes, access
Drive, consume a game reward, admit photos or mutate a financial ledger.
An existing active PENDING/UNKNOWN/CONFIRMED MOCK order must recover through
the original store without a new health prerequisite or replacement identity.
Existing idempotency/cart conflict/quote/promo rules remain authoritative.

READY means only route/queue/node observation. It never proves physical printer
or paper readiness. Native tests must show Clock progress during a held probe,
single-flight duplicate input, redacted retryable failure, one deliberate fresh
retry, existing-order recovery, and no retired page callback disclosure at
800x1280 and 452x900. Use synthetic settings/transports only.

Increment 1: causal persistence/config/probe tests, minimal adapter, focused
checks, docs/commit/push/remote verification. Increment 2: native integration,
one final applicable full regression after the final functional change,
matching Windows/Linux CI and final safe checkpoint. No schema/data migration;
rollback is scoped inverse source/tests/docs, preserving every existing journal,
reward, order, claim, manifest and media record. No archive inspection, OPS,
new branch/master/default change, deployment or real external effects.

UX-07 complete purchased-print payment gate remains NOT_RUN; matrix remains
59 PASS / 0 FAIL / 9 BLOCKED / 1 NOT_RUN until its stronger contract and
evidence are satisfied. Device/merchant/paper/Drive/privacy/release gates remain
separate. This record must not be promoted to paid-print acceptance.

## 29 October — UX-07.c opt-in nonpayable MOCK printer gate

Base/remote verified `605496ef1e0812eb804dfef219a41569d84cbb4e`. Ordinary
configured MOCK worker now reuses the original read-only check_printer and saved
settings before a new nonpayable order/QR when PRINT=1. Opt-out never reads
settings/probes; failed/unknown/error observations yield only printer-not-ready,
no new order/reward reservation/admission. Deliberate retry reads current config;
active PENDING/UNKNOWN/CONFIRMED recovers original identity without a new health
prerequisite. No ThermalPrinter/print job/Drive/backend/financial authority added.

**53 focused PASS / zero failure/error/skip**, 0.156s, Python 3.12.14/Linux;
seven new causal methods plus existing MOCK/config/health/isolation regression.
Expected pre-implementation run: seven methods/nine missing-adapter errors
(including subtests), not a discovered production defect. Two runtime adapters,
new test module and both-platform CI registration; no schema/data migration.
[Contract, source, command and safe evidence](evidence/ux07-mock-printer-verification.json).

Native integration/full/current matching CI pending; source is this containing
micro-commit and will be pinned after immediate push/remote verification. Next:
real Kivy Clock while probe held, duplicate/retired callbacks, error/retry at
800x1280/452x900, then one final applicable full and current Windows/Linux CI.
Matrix remains **59 PASS / 0 FAIL / 9 BLOCKED / 1 NOT_RUN**; full UX-07 purchased-
print payment/device gate NOT_RUN. Route/queue READY never proves paper.
Dedicated Sandbox printer/Drive stay OFF; no merchant/production/OPS/public
infrastructure/branch/master/default/deployment or actual external effects.
Only work/ synthetic scratch local. Rollback inverse adapters/tests/docs, retain
all financial/reward/claim/fence/media/audit records and existing original probes.

## 29 October — UX-07.d actual MOCK factory/native worker verified

Functional micro-push `2f598fd1136e3d2db0d410a0cdd640c74ef9cf6d` remote verified.
**67 focused PASS / zero failure/error/skip**, 24.283s, Python 3.12.14/Linux
software GL. Two new native methods use the actual app-configured factory,
with no injected checkout_jobs, at 800x1280 and 452x900. Clock ticks during a
held printer probe, duplicate taps are rejected, unknown result shows fixed
retryable text with no private error/order/QR/admission; deliberate retry creates
one nonpayable original order. Real page-revision retirement hides late result;
explicit recovery finds that same persisted order without another probe.
No runtime edits after 2f598fd. Original TCP checks are bounded per route;
Windows spooler API latency itself is not bounded by this adapter. No paper
readiness guarantee. [Commands/digests/limits](evidence/ux07-mock-printer-verification.json).

This tests/docs-only micro-push registers through the existing native group.
Current first-source CI 40881383641 pending/superseded, not claimed PASS.
Next one final full applicable regression and native error/retry image review,
then matching current Windows/Linux CI/final safe checkpoint. Matrix unchanged
59/0/9/1; UX-07 complete purchased-print payment/device gate NOT_RUN. PAY-22 and
WEB-01..08 BLOCKED, all actual device/provider/privacy/release gates separate.
Dedicated Sandbox printer/Drive OFF; no production/OPS/public ingress/branch/
master/default/deployment or real external effects. Only work/ synthetic scratch
local. Rollback inverse adapters/tests/docs, retain all financial/media records.
