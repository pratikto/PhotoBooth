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
