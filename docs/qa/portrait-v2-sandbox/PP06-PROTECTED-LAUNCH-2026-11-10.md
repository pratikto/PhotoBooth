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
