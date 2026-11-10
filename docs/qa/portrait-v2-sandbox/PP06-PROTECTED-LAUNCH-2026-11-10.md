# Protected original launch ownership — 10 November 2026

Base6e059cd on existing feature/post-preview-qris-checkout. H5-C native checkout
is micro-pushed and remote verified; final source regression/CI is running and
must retain its actual verdict before a later source push supersedes it.

## Contract before source — L1 trusted pre-device owner

Reuse the original LaunchLease on the SAME project root used by ordinary v2,
merchant trial and synthetic pilot BEFORE constructing camera/native providers,
opening legacy history or starting the protected child. The trusted launcher
retains original manager/control-worker and camera handles; GUI gets only the
accepted public control and the SAME camera. No provider, custody, config or
worker-fence key goes into app constructor/attributes. Do not change defaults,
main.py, old pilot or merchant health.

Implement a bounded explicit launch-owner core first, not another provider or
visit engine. Reuse OriginalSandboxVisits/create_visit_control/AsyncCamera and
an explicitly selected EXISTING CheckoutStore. Missing/linked/archive legacy
history holds; never silently create a fresh legacy DB to claim safety. Only an
accepted original READY outcome permits native mounting. Startup timeout/HOLD
retains every original handle and the global lease for truthful stop/retry-stop;
no process kill, root replacement, tokenless boot adoption or key provisioning.

Shutdown requests original control privacy/drain and camera close. Global owner
and legacy DB remain held until original trusted worker/manager/child/collector/
PhotoJobs actually finish AND the actual camera manager thread is dead. A
bounded False is not a safe context-manager exit. A later stop may complete the
same shutdown; no restarted capability. Failed partial startup is also drained.

Tests: occupied global lock before any device/legacy/backend construction;
actual child/control startup with fake external transports; same camera/public
binding; blocked original PhotoJobs/backend and camera thread retain global
lock/legacy handle; actual exit then permits another original LaunchLease;
invalid/absent legacy and unknown original boot owner stay held; no secrets in
repr/error. Native windows and final merchant activation remain separate.

Reviewed original AGENTS/protocol, complete continuation, H4/H5 freeze/handoff,
original bootstrap/host/Ubuntu-vault and product-readiness reports; original
LaunchLease, run_portrait_v2/pilot/merchant launcher, AsyncCamera, app camera
injection/stop, OriginalSandboxVisits, VisitControl/TrustedVisitWorker, collector
ownership and CheckoutStore. L2 must still supply secure original settings,
explicit Sandbox/external consents, native launcher/stop integration and device
preflight. Supported orphan/pre-ACK boot, backup/remedy/status/ops, final2h/4h and
actual account/device acceptance stay open. Commercial NOT_READY.

Rollback: scoped inverse source only; retain original root/DB/WAL/SHM/media,
ciphertext, custody, PAID/OWED, every operation and uncertain output.


## L1 implementation and focused verification

ProtectedSandboxLaunch acquires the original shared global LaunchLease before
legacy/camera/manager/control creation. Deferred imports include no Kivy; an
independent fresh Python import confirms no native import. Exact original child
READY/control/binding and same AsyncCamera are required for public mounting.
Startup failure keeps owner/partial handles, emits a static error and requests
original async drain; a later start cannot replace that context. No context
manager auto-releases a live camera/worker. stop(False) keeps global owner and
legacy DB; stop(True) checks actual control thread, original manager/child and
camera thread completion before closing legacy and the global lease LAST.

Existing path alone was insufficient: a newly expanded test initially had
1 method/2 subtest FAIL1.724s because an empty or foreign SQLite file was upgraded
to empty history. Before mutable CheckoutStore migrations, L1 now inspects the
original checkouts columns using mode=ro, also checking WAL/SHM path boundaries.
The same file bytes remain unchanged when rejected. Missing/archive paths fail
before camera construction. No original DB/key/root is replaced.

Initial module import ERROR before source existed; first6 PASS2.729s. Expanded
**38 affected PASS94.981s**, zero failures/errors/skips, including8 new launch
methods and original10 control/20 visits methods. Actual child/native-file worker/
camera-manager-thread and backend stop=False holds exercised; original boot/
foreign ownership remains held in inherited manager tests. Fake external
transports/Linux key lookup only. [Exact source/log hashes](evidence/pp06-launch-l1-2026-11-10.json).
Module added to complete Ubuntu/Windows core registry; all old852 retained.
New860 full backend is running; current-source CI pending. Original unchanged
native98 and Apps Script34 passed at6e059cd; do not claim new-source CI yet.

L1 is a trusted owner core ONLY. L2 executable/native mounting, secure settings
reader/booth identity/printer/legacy selection and explicit account/external
consents remain source work. Default merchant health stays False; original
synthetic pilot remains synthetic-only. Supported boot before ACK, Ubuntu keyring
login/autostart/reboot/backup, remedy/status/ops and final qualification are open.

## Windows fixture correction contract

L1 runtime/testsea2554c: full local860 PASS410.733s. CI42770363978 native98
PASS268.746s; Windows core339 had0 failures/2 ERROR367.015s. Both errors are
WinError32 removing wrong.sqlite3 after the empty/foreign-history subtests.
Ubuntu and Windows delivery were cancelled by matrix failure; NOT PASS.
Completed Windows/native logs inspected. The fixture used sqlite3.Connection's
transaction context manager, which does not close the connection. Runtime's
read-only validation already uses contextlib.closing; no runtime guard change
is indicated. Correct the fixture with explicit closing, keep every assertion,
verify affected methods and matching new-source CI. Do not suppress cleanup,
collect garbage as a workaround, weaken file locks or drop tests.

Fixture corrected with contextlib.closing; all assertions retained. **8 affected
PASS3.510s**, zero failures/errors/skips. Runtime is unchanged fromea2554c's
860 full local PASS; corrected-test exact-source CI pending. First Windows
failure/cancelled jobs remain in [the final record](evidence/pp06-launch-l1-final-2026-11-10.json).
Next verify corrected source CI, then L2 secure executable/native mounting.

## First unfinished source increment after corrected CI — L2

Read this whole report and actual newer remote before changes. Do not rebuild
H4/H5 freeze/recovery/delivery or L1 owner core. Old pilot remains synthetic-only.

Implement a separate explicit Sandbox entry alongside that pilot, reusing
ProtectedSandboxLaunch and ProtectedVisitsApp directly. Acquire the SAME project
global owner before reading secure settings or importing native providers. Reuse
tools.run_qris_sandbox.local_sandbox_credentials (literal-only merchant fields),
original Drive settings/client, original printer_settings.load_printer_config,
original branded_sandbox_qr_image and configure_kivy. Require complete account
pairs, exact booth/mode/root and configured original printer; no dummy provider,
production endpoint, replacement protected key or arbitrary HTTP readiness flags.
Do not expose config/manager/worker/fence keys through App attributes or logs.

Preserve original paper/Drive dual consents from the pilot; do not quietly enable
external effects. Actual merchant Sandbox uses its official simulator, never a
real banking/wallet payment. Check-only must perform no provider/payment/printer/
public-upload/device operation and report syntax versus NOT_CHECKED honestly.
No credentials in argv; no exception/settings/environment dumps. GUI receives
ONLY accepted VisitControl and owner.camera (SAME AsyncCamera), not a closure
holding launch authority/config. Mount the existing original all-design checkout.

Select the ACTUAL existing legacy history, not any convenient empty SQLite DB.
Original v2 merchant trial uses data/kiosk-v2-sandbox/merchant/booth/orders.sqlite
and visit.json; the older v1 trial uses data/qris-sandbox-trial/merchant/booth.
Inspect/reconcile known roots with original read-only recovery guards; do not
skip an unresolved legacy root by picking another. L1 rejects absent/foreign DB;
first-install legacy absence needs a separately specified, tested safe setup,
not an automatic blank replacement. Keep old contents excluded throughout.

GUI exit must drain original auxiliary file/game/health/preview and detector
owners before releasing the global guard as well as L1's camera/control/child.
Original wait_closed often returns None (e.g. GameJobs/AsyncCamera), so verify
actual thread completion, never truthiness/elapsed time alone. No broad force
kill or unconditional with-context global release on stop=False. Keep a static
held state and retry SAME shutdown while original handles live. Preserve original
journals/OWED/uncertain jobs, supported boot holds and every owner observation.

Test actual entry/native/child at both sizes, existing controls and no-capture
before accepted startup, actual global contention, missing/locked custody,
redacted bad settings/partial account pairs, legacy holds, blocked auxiliary/
camera/file/backend work and real thread exit. Only after final functional
mounting run one full source-matched regression and measured2h qualification.
Pre-ACK/orphan secure boot, backup/reinstall, refund/status/ops and actual Ubuntu
login/autostart/reboot/camera/POS80/Drive-phone/merchant/4h acceptance remain open.

Current cloud presence checks: ignored local_settings absent, merchant/Drive env
pairs absent, explicit printer route absent. No secret values read or printed.
These prevent actual external qualification; they do not substitute for the
remaining L2 and boot/remedy source work. Commercial remains NOT_READY.


## Final L1 verification and portable checkpoint

Runtimeea2554cc828257e8b6157d3cfd8277240f76fdc3; corrected fixture/source
34726b70c45f4f152f49844fa25b899a25fed36e, both pushed/remote SHA verified.
Runtime unchanged by the fixture correction.860 full local backend PASS410.733s
at runtime source; corrected8 affected PASS3.510s. Original native sources/test
command unchanged since6e059cd's98 full local PASS287.963s/34 Apps Script PASS.

[CI42771399228](https://github.com/pratikto/PhotoBooth/actions/runs/42771399228)
at exact34726b7 is **ALL FOUR SUCCESS**: Ubuntu860/330.454s, Windows
core339/293.076s +delivery521/637.201s (860 total), native98/263.836s. All four
completed logs inspected; zero unit failures/errors/skips. All8 new L1 methods
execute on Ubuntu and Windows core. Original owner Windows setup/check-only,
Linux preflight and synthetic screenshot steps passed. Earlier339/2 cleanup
ERROR and cancelled jobs remain recorded, not relabelled PASS. No timeout or
assertion weakened. [Exact source/log/case evidence](evidence/pp06-launch-l1-final-2026-11-10.json).

No runtime/test WIP or active local test/backend remains; only the lab X11 display
is intentionally available. Private local work/logs/screenshots and superseded
old privacy stash/patch are not Git backups and must not be applied over H4.
This containing publication is documentation-only (obtain SHA from Git history);
no successful source workflow needs rerunning for it. L1 core is delivered,
NOT a completed executable/customer launcher. FIRST next implementation is L2
above; no new onboarding regression of this unchanged baseline. All actual
account/device/boot/remedy/status/ops/qualification gates stay open; commercial
NOT_READY, default fulfillment_enabled=False. Rollback source only, retain every
original journal/key/media/paid right/uncertain job.

## Owner priority update — Windows first, 10 November 2026

Owner explicitly defers the Ubuntu launcher and requests continued development
for Windows execution first. Preserve Linux support/tests already delivered, but
do not build Ubuntu service/autostart packaging ahead of Windows. Existing
Start-PostPreviewDeviceTest.ps1 remains the working synthetic-camera trial.
It must not silently become a merchant entry or adopt its old synthetic roots.

L2-A: reuse the existing literal-only Sandbox settings parser for both merchant
and Drive fields, original printer configuration and L1 global owner. Configuration
must be read only after the exact active global owner exists, with complete
pairs selected from environment OR original ignored settings, never partial
account mixing. Return a redacted trusted bundle, never hand it to GUI. Require
explicit usable POS80 route and fixed Sandbox identity/storage. Inspect the
canonical existing v2 legacy database read-only, plus original project recovery
review and older v1 history boundary. Unknown/missing/foreign history holds;
this increment must not manufacture an empty legacy DB or replace custody.

Test settings/partial pairs/invalid identity/archive/link/legacy holds, redacted
errors, actual original file bytes unchanged and no network/device/native imports.
Then L2-B explicit Windows PowerShell/Python entry, original native app and full
shutdown drain. First-install history initialization is a separate explicit
reviewed setup, not a bypass. No merchant/default activation, actual provider
operation, payment, paper, public upload or deployment in cloud development.

L2-A must also compare canonical journal status with actual legacy SQL finance/
release history. Reproduce terminal-looking CANCELLED journal + active original
checkout; loading must hold without changing file bytes. Extract/reuse the exact
OriginalWorkerReadiness legacy closed/terminal/FULFILLED-or-original-ACK+fence
checks into one read-only SQL helper shared with settings. No new financial
classification, mock provider or release authority; original readiness keeps all
scope/native/media/worker guards. Verify original authority/checkout-release
regression alongside new settings cases. Initial37 settings/launcher/L1 PASS is
before this additional historical-state denial, not the final scope.

L2-A implemented: exact active global owner before settings, complete environment
OR original literal local pairs, original saved POS80 configuration, redacted
private bundle and canonical read-only legacy history. Original merchant parser
is reused/extracted for named Drive fields without executing local_settings.py.
Original legacy closed/terminal/paid obligation/release-fence guard now has one
shared read-only implementation for startup and charge readiness. Active SQL
order behind a terminal-looking journal first reproduced1 FAIL; fixed without
changing original finance/release/media guards. Original PAID/OWED survives ACK;
a mismatched fence denies. **69 affected PASS24.536s**,10 new settings methods,
zero failures/errors/skips. Original21 launcher methods also registered in CI
because its literal reader is shared; every old860 execution retained.
[Exact hashes/scope](evidence/pp06-windows-settings-2026-11-10.json). NEXT L2-B
explicit Windows Python/PowerShell entry and original native shutdown drain.
Ubuntu packaging deferred by owner. Full final-source regression/CI pending.

L2-B before source: add a SEPARATE Start-PostPreviewSandbox.ps1 / Python entry,
leaving the original synthetic device helper unchanged. Reuse its dependency
setup/check-only, L1 owner/L2-A settings, original native app and QR loader.
Require explicit Sandbox and BOTH original paper/Drive consent pairs for a run;
check-only is local settings/history validation, not credential/device readiness.
Manual camera/audio profile, face/palm disabled as the existing Windows trial;
no Ubuntu service/autostart work. No fixture/provider/test flag in production GUI.
Keep the original global lease while original auxiliary game/report/preview/health
threads stop, then actual L1 control/collector/PhotoJobs/child/camera shutdown.
Use actual thread objects, not wait_closed's None or elapsed time. A held drain
keeps the SAME process/owner until it finishes, never force kills or frees booth.
Missing first-install history remains an explicit setup gate; no blank fallback.
Test exact native control/camera injection, local-only preflight/lock conflict/
consents, actual child start/stop, blocked auxiliary threads and both-size UI.

L2-B implemented: separate Python/PowerShell protected entry, original dependency
setup reuse, explicit Sandbox + BOTH original external consent pairs, local-only
settings/history check and exact native control/camera injection. Original Windows
manual environment helper removes inherited offscreen/dummy drivers. GUI never
receives the settings/manager/worker/key. Auxiliary game/report/preview/health
actual threads must finish before L1 releases global/camera/child ownership.
Blocked original game I/O and preview pool remain held after nonblocking close.
**24 affected backend PASS4.412s +1 new native method PASS12.117s** at BOTH sizes,
zero failures/errors/skips. Actual original child/control plus original native
capture→freeze→CCP→QRIS→ticket→automatic2+1 output exercised, OWED retained.
Windows test fixtures preserve OS runtime variables without merchant credentials.
[Commands/source/log hashes](evidence/pp06-windows-entry-2026-11-10.json).
Native/source modules registered; new full backend897/native99 and exact-source
CI pending. Windows CI also invokes the actual PowerShell entry and expects a
redacted BLOCKED2 without account configuration, after original venv setup.
[Windows guide](WINDOWS-PROTECTED-QUICK-START.md). Old synthetic entry unchanged.

Remaining: explicit first-install/legacy migration policy, supported original
pre-ACK/orphan/normal interrupted-visit boot and complete operational remedies.
Normal close during an unresolved visit also preserves a held owner for next
startup; do not imply transparent restart from this entry. No root/key reset to
make it start. Actual Windows camera/POS80/DPAPI restart/account/phone acceptance
and final qualification remain open; commercial NOT_READY, health False. Ubuntu
launcher/autostart packaging deferred by the owner.
