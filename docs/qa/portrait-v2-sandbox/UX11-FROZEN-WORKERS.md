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
