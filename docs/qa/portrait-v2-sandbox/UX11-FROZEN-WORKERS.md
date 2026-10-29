# AR-10/12 — UX-11 frozen workers and living-process hold

29 October 2026 (Asia/Jakarta). Base/remote verified
8ca792def8a66595ce8571460533932f42ffa341. UX-07 Sandbox components verified;
purchased-printer gate stays NOT_RUN. Continue independent source validation.
Reviewed governance/checkpoint/handover, AR master/roadmap/privacy/operations,
supervisor contract, original watchdog/recovery runbooks, existing launcher loop,
CrashBudget/LaunchLease/KioskLease, GameJobs/SandboxJobs/PhotoJobs, native privacy
epochs, inherited DriveSyncWorker/retention guard and related existing fixtures.

Contract before code: stalled checkout, QR and upload operations run off the UI
thread; real Kivy Clock must still tick while barriers hold. Duplicate requests
stay single-flight; retirement/minimize fences late callbacks and private media.
Upload must retain original files/counter/queue and finish each original item
once when released, never trigger a new visit/print. Use real existing workers
and fixture transports, no real provider/Drive/printer I/O.

Separately freeze the main thread and checkout worker of a real disposable child
process owning actual payment/launch leases and one PAID/OWED grant. Exercise the
real dedicated launcher monitor with that still-living child and mocked backend/
spawn transport. No crash budget reservation, extra spawn, automatic termination,
journal/paid mutation or lease release during observation. Explicit simulated
operator interruption ends observation; test-only control input unblocks/cleans
its own child afterwards. A blocked-main fixture is not physical OS/GUI hang
certification; native I/O responsiveness and device gates are recorded separately.

Focused tests -> docs/commit/immediate push/remote verification. Register pure
process tests Windows/Linux; native widget/upload-loop evidence Linux virtual
display. Tests-only changes retain 347e502 full runtime provenance; one final
applicable full only if a real runtime defect needs correction. Do not enable
watchdog behavior, kill living customer processes, reset budget or replay effects.
No new branch/master/default/production/OPS/public ingress or external message.
Only synthetic temp profiles; no logs/images/DB/tickets published. Preserve all
financial/action/claim/fence/media/audit data and held live ownership on rollback.

## 29 October — UX-11.a living frozen process hold verified

Base/remote verified `8ca792def8a66595ce8571460533932f42ffa341`.
New real disposable child owns both kernel leases, one PAID grant/OWED ledger,
and blocked main + checkout worker. Real launcher monitor observes it for three
cycles: no budget reservation/extra spawn/automatic stop, unchanged financial
rows/journal bytes and held leases. Simulated explicit operator interrupt ends
observation; only test control input subsequently releases its child. Not a real
OS/Kivy deadlock certification. No hardware/provider or live process killed.
**6 focused PASS / zero failure/error/skip**, 0.246s, Python 3.12.14/Linux.
Command: `.venv/bin/python tools/run_kiosk_unittests.py test_ux11_process_hold test_crash_supervisor`.
Pure process module registered Windows/Linux; current CI pending. Tests/fixture/
workflow/docs only, runtime unchanged at 347e502. Full 1159/1155/4 remains original
source, excludes subsequent tests. UX-11 NOT_RUN until stalled checkout/QR/upload
native responsiveness/privacy and final CI complete. UX-07 whole purchased-
printer gate remains NOT_RUN. Matrix 58/0/9/2 unchanged. Next native I/O barriers
and retained upload queue; no watchdog activation/new runtime behavior.
No production/OPS/public ingress/branch/master/default or actual external effect.
Only work/ scratch local. Rollback tests/docs only; preserve all customer state.

## 29 October — UX-11.b native stalled-I/O evidence verified

First process micro-push `c588d5a635a1f427b997d8b003a13b2aedf732d5` remote
verified. New native checkout/QR barriers prove actual Kivy Clock ticks while
single-flight I/O is blocked; repeated taps do not create another order; privacy
epoch retirement suppresses late QR/payment display and no grant/media admitted.
Real inherited retention-guarded upload queue pauses inside fixture upload_file:
Clock and PhotoJobs metadata remain responsive, original queue/counter/files
preserved, no old active transaction exposed, four files upload exactly once
when released, no print/cleanup/new visit. The actual blocked-main child test
separately holds both leases/PAID/OWED without restart or mutation.
**9 focused PASS / zero failure/error/skip**, 2.979s, Python 3.12.14/Linux software
GL: one process method, two new native checkout/QR methods, one native upload
method, five prior crash-budget/launcher guards. Pure process initial six PASS/
0.246s; native checkout/QR intermediate eight PASS/3.149s. Barriers are bounded
fixture stalls, blocked-main process is synthetic, not real OS hang certification.
Tests/fixtures/docs only, no runtime defect/change; full 1159/1155/4 remains
347e502 and excludes ten later UX-07/UX-11 methods. Current matching CI pending
for containing micro-push: process method Windows/Linux, native methods Linux.
UX-11 stays NOT_RUN until final CI; matrix 58/0/9/2, UX-07 purchased-printer
stronger gate NOT_RUN. Next final current CI/checkpoint and exact remaining
provider/purchased-printer/device/operations/release gate handoff. No watchdog
activation/kill/replay, production/OPS/public ingress/branch/master/default or
real external effect. Only work/ scratch local; rollback tests/docs only, keep
all financial/claim/fence/media/audit records.

## 29 October — UX-11.c portable owned-lease denial fixture

Source `07734b22609cd1740fcfc43e6040507b0a729e0b` pushed/remote verified.
Its CI 40865074759 Windows job 123417828871: 116 run/one fixture FAIL, `2 != 130`;
not a successful matching run. Launcher deliberately maps OSError to generic
setup-stop; Windows mandatory byte locks may reject KioskLease's initial read
with OSError before its later lock-failure RuntimeError wrapper. Historical
inner exception was hidden by the intentional generic launcher response.
Controlled PermissionError injection reproduces exactly `2 != 130` with old
fixture: one expected FAIL/zero error, 0.271s; corrected fixture one PASS/0.239s.
Accept either specific owned-lease denial class (RuntimeError/OSError); retain
actual child-alive, both held leases, no spawn/budget/stop and exact financial/
journal assertions. No exception message/errno guarantee, no broad catch-all,
no production lease/launcher/runtime change. Real Windows retest still required.
**9 focused PASS / zero failure/error/skip**, 3.104s, same checkout/QR/upload
barriers plus real held process. Exact command/source/report digests in
`evidence/ux11-final-verification.json`. This containing tests/docs micro-push
corrects portability; current new CI pending. UX-11 NOT_RUN until current CI,
UX-07 stronger printer gate NOT_RUN; matrix 58/0/9/2. Next verify new Windows/
Linux CI and final safe checkpoint. Retain failed run and controlled evidence.
No runtime/OPS/production/branch/master/default/external effect. Only work/
scratch local; rollback tests/docs only, preserve all financial/media state.

## 29 October — UX-11 verified synthetic worker/hold evidence

Process source `c588d5a635a1f427b997d8b003a13b2aedf732d5`, native test source
`07734b22609cd1740fcfc43e6040507b0a729e0b`, portable fixture source
`7ca46b531bab190cdc61479a3d5d492e7232fa15` pushed/remote verified. First CI
40864175072 CANCELLED/superseded; 40865074759 superseded with recorded Windows
fixture failure (116 run/one FAIL, generic 2 != 130). Controlled Windows-style
PermissionError reproduces old failure, corrected fixture PASS; retains actual
live child, both lease denials, no spawn/budget/automatic stop and exact financial
rows/journal bytes. Runtime lease/authentication behavior never changed.

**9 final focused PASS / zero failure/error/skip**, 3.104s, Python 3.12.14/Linux
software GL. Initial process six PASS/0.246s, native checkout/QR eight PASS/3.149s,
initial combined nine PASS/2.979s retained. **CI 40865822670 all three jobs
SUCCESS**: actual blocked-main/worker process method individually PASS on
Windows/Linux; native checkout/QR and real upload queue methods PASS on Linux.
Clock ticks while I/O barriers hold; duplicate taps stay single-flight; retired
late callbacks cannot show private QR/payment/media. Upload resumes four original
files exactly once with unchanged counter/bytes and no new visit/print. Actual
living fixture process retains PAID/OWED/leases without restart or mutation.
Observation ends by simulated explicit operator interruption; only test control
input subsequently cleans its own disposable child. Bounded stalls and blocked-
main fixture are synthetic, not physical OS/GUI hang or device certification.
[Exact commands/source/results/CI/digests/limits](evidence/ux11-final-verification.json).

No runtime change. App/tools trees match 347e502; old full **1159/1155/4** retains
that provenance and excludes ten later UX-07/UX-11 methods, checked separately.
No repeated full/native export or old result relabeled as current full/device
acceptance. UX-07 component CI 40862328219 separately remains SUCCESS.

**UX-11 synthetic PASS**. Matrix **69 IDs: 59 PASS / 0 FAIL / 9 BLOCKED /
1 NOT_RUN**, audit IN_PROGRESS, AR-13 conditional. Remaining UX-07 whole gate:
purchased-print prepayment path/actual printer readiness is not mounted/certified
in this transport-off Sandbox. Camera/storage/template/isolation/native error/
retry component evidence is verified; preserve printer/Drive OFF. Next work is
the purchased-print contract/integration and target-device evidence, with original
read-only printer services and explicit privacy/payment/physical acceptance.
Do not infer that route/spooler availability proves paper or enable Sandbox
printing to satisfy a gate. PAY-22 official Legacy contract and WEB-01–08 approved
infrastructure/operations remain BLOCKED; real merchant/Windows/Ubuntu hardware,
phone/paper/Drive/deletion/privacy/support/release acceptance remains separate.
No automatic deployment, production payment, OPS, public ingress or branch/
master/default operation. Do not repeat verified UX-05/UX-11 or BUG-023/024.
This containing docs-only push is final safe checkpoint; exact SHA from Git
log/remote. Only work/ scratch local, no unpublished runtime patch. Rollback
inverse tests/docs, retain all financial/action/claim/fence/media/audit records.
