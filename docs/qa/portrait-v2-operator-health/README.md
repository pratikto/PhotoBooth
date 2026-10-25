# GUI v2 operator Device Health — FEAT-008 / FEAT-022

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

## Planned native integration

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
