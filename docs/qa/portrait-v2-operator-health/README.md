# GUI v2 operator Device Health — FEAT-008 / FEAT-022

**Completed source increment.** Foundation `4c89e4f`, functional source
`ea394e8`, evidence `5f09eff`. The “planned” section below preserves the original
design sequence; native integration/local report and final local/CI sections
record completion. Actual operator/P5/merchant acceptance is separate.
[Current ledger](../../test_checklist.md).

Owner authorization, **25 Oktober 2026**: continue safe roadmap development in
cloud; do not wait for laptop acceptance, test manually tonight. Current task
ports existing read-only Device Health service and actual panel into GUI v2,
adds a redacted local diagnostic report and automatic recovery/lifecycle checks.
Target **feature/portrait-kiosk-v2-next** only; baseline/rollback **fdafbe2**.
No production/POS/real discount, device switching, merge/default change, cloud
retention deployment or automatic capture/print/restart is authorized here.

## Stage 1 — reuse existing source

Latest remote Device Health reference verified read-only at
**dbbe055bb1281ad065a5ba0c3593cfbfbd388bd3**. Six source files and five original
backend test modules imported byte-for-byte; [provenance/hashes](reused-source.json).
The original panel `HealthPanelMixin.show_health_settings` will be mounted directly,
with small v2 lifecycle/audio/cached-camera adapters. Existing v1 UI/controller
and global device preferences remain untouched. Selection routines are retained
as dependencies of the original observation UI; no staging callback is supplied,
so they cannot change active/saved camera or printer from v2.

Checks are manual, bounded, read-only: existing camera frame, printer route/queue
visibility (zero print bytes), disk, fixed connectivity probe, local media files,
and main-loop heartbeat. Queue/device presence is not paper, motor or physical
operability; READY means only that named observation passed. Network checks do
not verify Midtrans/Drive. Physical/provider/privacy gates remain NOT_RUN.

## Original native integration plan (implemented below)

Operator access on idle advertising: **F12** or hold Meong header, without adding
technical controls to the customer journey. A background worker runs one sweep;
refresh cannot queue duplicates. Close/minimize/stop retire old results, and
operator access cannot interrupt active capture/game/payment work. No second
camera is opened. Export saves only safe metadata and bounded observations to
`data/diagnostics`, with no photos, raw logs, keys, QR/order/merchant references,
network addresses, device serials/queue names or automatic upload.

Native checks and reviewed screenshots at 800×1280 and 452×900 will accompany
implementation. One final full regression after functional changes; physical
Windows tests remain a separate final owner form, not a reason to stop source work.

The v1 async controller method `PhotoBoothApp._refresh_device_health` is also
reused verbatim by extracting it into `v1_health_controller.py` with only its
imports/class shell. Source line range and method hash are recorded. The v1
application is not instantiated/replaced. Its worker lock, async scheduling,
exception redaction and stale/closing guards stay in effect; v2 supplies its
existing scheduling/cached-frame objects. This avoids a second implementation
of the v1 worker while leaving the current v1 launcher unchanged.

Stage 1 verification: **73 focused PASS / 0 failure/error/skip**, Linux Python 3.12; five original backend suites plus byte/method provenance checks. [Output](reuse-tests.txt).

## Native integration and local report

Run the **existing** `python tools/run_portrait_v2.py`. At idle advertising press
**F12**, or hold the Meong header **1.5 seconds**. Short tap/drag/right click do
not enter. A protected Sandbox RECOVERY page also allows observations; pending
checkout, active capture and game cannot be interrupted by this entry.

The actual original `HealthPanelMixin.show_health_settings` and native v1 label
helper are reused. Compatibility seams are limited to the v2 button/audio owner,
Kivy scheduling (`root.after`), cached asynchronous-camera frame and lazy read-only
printer config. No v1 application or second camera is instantiated. No device
staging callback is supplied: PILIH DEVICE stays disabled and saved selections
are not applied/changed by v2. No automatic device restart/hot-swap/watchdog.

Six rows plus OS candidate inventory are scrollable. One original v1 worker lock
prevents overlapping probes; dialog serials and v2 guards discard old results.
Close/minimize retires the popup. Idle ads/audio are retained. Customer buttons
held before opening are retired, while the next genuine single tap works.
Checks run only on manual open/refresh; there is no background polling schedule.
Printer/TCP/spooler observation sends no print payload. Queues are candidates,
not proof of physical paper/cutter. Camera reports a fresh existing mailbox frame,
not a new native-handle probe. Connectivity is not merchant/Drive verification.

**SIMPAN LAPORAN LOKAL** writes unique atomic JSON under
`data/diagnostics/device-health-*.json` using the existing inventory/atomic writer.
It includes source/branch/dirty flag, OS/dependency/display metadata and six
allowlisted status observations. It excludes camera pixels/photos, raw logs,
probe exception messages, keys/tokens, addresses, queue/serial identities,
merchant/order/QR references and journals. Nothing is uploaded. All physical/
provider acceptance fields stay NOT_RUN. It imports into the existing P5 form
or [new eight-item operator form](windows-checklist.html); import never passes a test.

Current manual reports remain accepted with their existing metadata limits.
[Operator form](windows-checklist.html) does not impose another twenty-cycle
photo/game retest; actual merchant/P5 hardware/retention still use their own gate.

## Focused verification and preview

Twenty-seven focused tests PASS before the final regression, including the
unchanged v1 worker/panel, native twenty open/close cycles with no leaked window
size bindings, hold/F12 guards, stale probe/export callbacks, error redaction,
single-tap/SFX behavior, atomic reports, and real HTTP Sandbox recovery without
order mutation or replay. Initial Kivy test-helper dependency on pytest was
removed by using the project's existing native MotionEvent test pattern.
Screenshots are generated with `tools/render_portrait_health.py` using injected
offline observations; no real device/network/provider probes in the renderer.
Required sizes: 800×1280/452×900; 360×640 also checked. Final full/CI/source and
PNG evidence will be attached before delivery. No physical PASS is claimed.

## Final local regression

**780 tests PASS / 0 failure / 0 error / 0 skip**, 270.671s. Linux/Python 3.12,
Kivy 2.3.1, software GL/offscreen SDL, dummy PCM, synthetic device/payment/print
fixtures and supplied offline face/palm assets. Command:

```text
PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1
PHOTOBOOTH_PALM_TEST_ASSETS=<prepared-offline-assets>
MEONG_CI_TEST_REPORT=<report> python tools/run_kiosk_unittests.py
```

[Full output](full-tests.txt) · [27 focused PASS](focused-tests.txt) ·
[browser form checks](browser-tests.txt) · [functional-source hashes](tested-source-sha256.json).
The browser check verifies eight initially empty boxes, safe operator JSON import
without passing tests, partial Submit 1/8, persistence/download, no new twenty-cycle
gate and 360/452/800px bounds. Fifteen local native PNGs (five states at three
sizes) were dimension/hash checked and visually reviewed. The renderer waits for
the UI to paint after worker delivery so screenshots describe their named state.
Cloud observations are fixtures, not proof of device/provider availability.

[V1 runtime hashes](v1-runtime-unchanged.json) verify fourteen existing launcher,
controller/UI/audio/camera/photo/printer/Drive/retention files unchanged from
fdafbe2. Actual original health UI/backend and extracted worker remain pinned by
[reuse provenance](reused-source.json). No functional changes followed the full
regression; matching-source CI/screenshots will be recorded separately.

Rollback: foundation **4c89e4f** (customer UI unchanged), or baseline **fdafbe2**.
Use scoped inverse code commits on the same authorized branch after inspection;
keep all payment/photo/print journals and reports. Never reset transaction data.

## Final matching-source CI and delivery checkpoint

Functional source **ea394e8ce0b5bcd1a95f46544e6a050494ece733**, pushed and remote
HEAD verified after the local full regression. [CI 40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369)
has all three jobs **SUCCESS**. [Job record](final-ci.json) and [raw reports](ci-reports/):
health 80 PASS/0 skip; Sandbox 139 PASS/0 skip; native 93 cases, 92 PASS/one
optional real-palm-model-assets skip. That model case is covered in the local
780-test full run with supplied assets; the CI skip is preserved, not relabelled.

All **119 PNGs** from artifact **12584847405** have matching source SHA, dimensions
and hashes; the downloaded ZIP matches GitHub's SHA-256 digest too.
[Verification](ci-screenshot-verification.json) paths refer to the artifact tree.
Ten matching-source operator PNGs are preserved in [screenshots/](screenshots/).
[Contact sheet](ci-contact.jpg) was reviewed at 800×1280 and 452×900: source v1
panel, scroll areas, REFRESH/TUTUP/report controls and messages fit; saved/error/
loading views describe their actual state. Local 360×640 previews also reviewed.
All health statuses/screens are offline fixtures; actual probes/hardware/provider
acceptance are NOT_RUN. The existing customer P3/game/MOCK/Sandbox regressions
remain green and original Meong Fly/reference files remain unchanged.

No further functional source edits followed the 780-test regression; the
[tested-source manifest](tested-source-sha256.json) matches committed source.
Foundation **4c89e4f** also had three-job CI SUCCESS (40156142669). Evidence-only
updates skip CI, preserving the owner's Actions budget.

For tonight: pull the required branch, launch the existing v2 launcher, press
F12/hold header on idle, use REFRESH/SIMPAN LAPORAN LOKAL and fill the new eight-item
operator form. Do not repeat old photo/game twenty cycles solely for this form.
P5 merchant/printer/Drive/privacy and production release remain separate gates;
this source increment completed without waiting for laptop testing.
