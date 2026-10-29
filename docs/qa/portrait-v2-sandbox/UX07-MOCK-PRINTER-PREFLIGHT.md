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

## 29 October — UX-07 final local validation / CI method reporting

Test source `3a98ed977c86ad9d7eb0f8407103e097f1b9208a`; runtime remains
`2f598fd1136e3d2db0d410a0cdd640c74ef9cf6d`. Final full **1178 run / 1174 PASS /
zero FAIL/ERROR / four optional SKIP**, 594.860s, Python 3.12.14 / Debian 13
software GL/dummy audio. Three native-model skips and one opt-in video skip
remain explicit. Fresh focused **67 PASS**, 23.472s, and **12 PASS**, 1.042s,
zero failure/error/skip. No runtime/tests changed; no full result borrowed from
older evidence. Workflow-only reporting was edited near the end of the full run;
application/tools/tests stayed identical to the tested source throughout.

Four fresh native FBO error/held-retry captures at 800x1280/452x900 visually
PASS: readable message/controls, no clipping/private details/order/QR/customer
media, disabled retry while busy; release creates exactly one nonpayable MOCK
order without admission/print. Initial corrupt Window readbacks rejected.
Raw synthetic captures/reports remain private local work/; paths/SHA-256 and
commands are recorded in [the validation evidence](evidence/ux07-mock-printer-final-validation.json).

CI `40882031887` at `3a98ed9` reports all three jobs SUCCESS. Windows ledger
**123 PASS** (all seven new MOCK and five readiness methods individually ok);
other Windows groups **72/55/103 PASS**, zero skips. Linux pure **129 run/128
PASS/one SKIP**, supervisor **40 PASS**. Linux native step reports success but
its blob-host log/artifact downloads receive proxy CONNECT 403; individual
native execution is **not yet verified** from that run. No blanket PASS claim.

New CI-only reporting reads existing reports and requires the exact 5 readiness,
7 MOCK and 2 native PASS lines before emitting source/digest/method notices via
accessible GitHub check annotations. Actual local reports accepted; removing a
method, skipping it or failing the summary each rejects. Existing assertions,
workflows and safety checks remain. This micro-push's matching CI is PENDING;
next read its notices and publish the final source/remote checkpoint.

UX-07 complete purchased-print payment/device gate remains **NOT_RUN**; matrix
**59 PASS / 0 FAIL / 9 BLOCKED / 1 NOT_RUN**, audit IN_PROGRESS. No physical paper
readiness guarantee; Windows spooler API latency is not bounded by this adapter.
Sandbox printer/Drive OFF. PAY-22/WEB-01–08 and actual merchant/Windows/Ubuntu
hardware/phone/paper/Drive/deletion/privacy/support/release gates remain separate.
No production/OPS/public infrastructure/deployment/default/master operation or
real effects. Only private work/ scratch is untracked outside the repository.
Rollback workflow/docs only, preserving all financial/media/audit records.

## 29 October — UX-07.e final MOCK validation verified

Remote-verified CI source `8d0b9bb7cf125a714e3aeb277e0ce29930b00fb3`;
**CI 40887868676 all three jobs SUCCESS**. Actual check annotations verify five
readiness/seven MOCK methods on Linux, and **both new native configured-factory
printer lifecycle methods PASS** at both portrait sizes. Windows individually
verifies the same five readiness/seven MOCK methods. Linux Sandbox **424 PASS**;
native **113 run / 112 PASS / one SKIP**; pure **129/128/one SKIP**, supervisor
**40 PASS**. Windows groups **123/72/55/103 PASS**, zero FAIL/ERROR/SKIP.
New native methods run on Linux only. The prior 40882031887 native blob-log
restriction is preserved, not relabeled; current notices resolve that evidence
gap at the new exact source. [Full receipts/commands/hashes](evidence/ux07-mock-printer-final-validation.json).

Application/tools/tests trees match local test source `3a98ed9`; runtime remains
`2f598fd`. Fresh focused **67 PASS** and **12 PASS**, zero failure/error/skip.
Final full **1178 run / 1174 PASS / zero FAIL/ERROR / four optional SKIP**,
594.860s, Python 3.12.14 / Debian 13 software GL/dummy audio. Three optional
model checks and one opt-in native-video check skipped, never counted PASS.
Four fresh FBO error/held-retry images at 800x1280/452x900 visually PASS:
readable controls/message, no clipping/private error/order/QR/customer data;
retry single-flight and exactly one nonpayable order after deliberate success.
No runtime/test change or repeated full run for CI/docs-only follow-up.

This validation increment is complete; **UX-07 whole purchased-printer payment/
device gate remains NOT_RUN**, matrix **59 PASS / 0 FAIL / 9 BLOCKED / 1 NOT_RUN**.
Purchased-print prepayment integration and actual Windows/Ubuntu printer/device
acceptance remain uncertified. Route/queue readiness never proves paper; Windows
spooler API latency is not bounded by this adapter. Sandbox printer/Drive OFF.
PAY-22 official Legacy contract and WEB-01–08 infrastructure/operations BLOCKED;
real merchant/phone/paper/Drive/deletion/privacy/support/release gates separate.
Next resolve those exact gates within their scope; no Operator Settings, Emulate
Ticket, public deployment, production payment or unrelated GUI work started.

Only safe workflow reporting/docs changed. Rollback their inverse, retaining all
financial/reward/claim/fence/media/audit/retention records. Private work/ reports,
images and fixture scripts are local-only, not backed up to GitHub; no unpublished
runtime/test patch. Final docs publication SHA is its containing commit from Git
log/remote; prior remote checkpoint is the full `8d0b9bb...` SHA above.
