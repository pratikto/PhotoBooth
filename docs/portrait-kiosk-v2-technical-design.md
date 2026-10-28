# FEAT-022 — GUI v2 engineering contracts

V2 Sandbox QR branding directly reuses `qr_code.create_qr_image`: downloaded
provider pixels are decoded locally, significant outer whitespace is rejected
for branding, and the logo candidate must decode to the identical payload.
The existing renderer checks full-size and 180px pixels; original images remain
available on any branding failure. Downloads/errors, raw simulator URL, order
identity and payment verification stay in their existing services. Work runs
on the existing single-flight worker and is cached per order/image identity;
QR texture filtering uses nearest sampling. [Evidence](qa/portrait-v2-sandbox/QR-LOGO.md).

Optional local Sandbox defaults are top-level string literals named
`MIDTRANS_SANDBOX_MERCHANT_ID` and `MIDTRANS_SANDBOX_SERVER_KEY` in ignored
`photobooth/local_settings.py`. The launcher parses these without executing Drive
settings. If either existing MIDTRANS environment value is supplied, the file
is not read and the other value retains its prompt. Otherwise saved values are
used and only missing fields are prompted. Malformed/unreadable/computed settings
stop before subprocess startup with a fixed error; values never enter argv/logs
or the GUI child environment. [Contract/evidence](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).

Sandbox key syntax accepts both `SB-Mid-server-` and `Mid-server-` with a nonempty
printable ASCII suffix, at most 512 characters total. The dashboard key is passed
unchanged to the backend. Environment is fixed by the Sandbox-only transport,
not inferred from the prefix; provider authentication/settlement remain separate.
[28 October correction and evidence](qa/portrait-v2-sandbox/KEY-FORMAT.md).

## Current FEAT-009 stage 2 — 27 October 2026

`recovery.py` performs a bounded, metadata-only read of existing local manifests,
Sandbox journals and MOCK SQLite state. The watchdog child checks this while
holding a native launch lease, before importing Kivy/devices. OPERATOR_REVIEW
exits 3/RECOVERY_HOLD; duplicate/unavailable ownership exits 2/STARTUP_BLOCKED.
All ordinary and merchant-trial GUI launchers share that per-checkout lease
through worker teardown. Direct ordinary launch retains existing operator
recovery; only the watchdog sets the additional journal gate. No payment, printer,
upload or journal reset logic is replaced. Empty reserves/deferred Drive are
distinct from interrupted capture and uncertain paper sends.

Windows development and Ubuntu mini-PC deployment use the same Python launcher;
startup output is cmd versus a graphical-session systemd user unit. Generation
uses explicit POSIX target paths from Windows and never installs or enables a
service. Restart=no and no replay remain intentional. [Contracts/runbook](qa/portrait-v2-recovery/README.md).

## FEAT-009 observation hook — 27 October 2026 (local increment)

The optional `run_portrait_v2_watchdog.py` parent starts the ordinary launcher
in its own process group. Only that parent supplies an ephemeral heartbeat path
and run ID; the ordinary launcher then schedules `AppHeartbeat` on Kivy's main
thread and cancels it before waiting for workers during teardown. An independent
`WatchdogMonitor` validates PID/run/sequence and writes bounded, redacted status
reports. It has no business-state adapter or process kill/restart action.
Default direct launch schedules no extra event. [Scope and startup runbook](qa/portrait-v2-watchdog/README.md).
Updated **25 October 2026** against audit baseline `5f09eff`; latest functional
source `266b2c8` (print/Drive), input correction `ebb53fd`, original operator
`ea394e8`, earlier P5 source `9433010`. Continue on the existing
`feature/portrait-kiosk-v2-next`. [Roadmap](portrait-kiosk-v2.md) ·
[current evidence](FEATURE_STATUS.md) · [architecture](ARCHITECTURE.md).

## Active modules

| Responsibility | Modules | Contract |
| --- | --- | --- |
| Window/page lifetime | `app.py`, `flow.py`, `viewport.py` | Dedicated launcher, page revision guards; browse timeout only for safe pages |
| Theme/buttons/header | `theme.py`, `button_art.py`, `branding.py`, `brand_flight.py` | Original game materials, native readable main-app captions without required icons; bounded animation lifetime |
| Gallery/warmup | `gallery.py`, `previews.py` | Twelve original strips, worker CPU preparation and five cached neighbour textures; held drag/reversal shows incoming artwork, replacement rather than queued swipe animations |
| Audio | `audio.py`, `mixer.py`, `game_music.py`, `shutter.py` | One v2 owner; separate GUI/video/game ownership and SFX; no parallel v1 AudioManager |
| Camera/sensors/preview | `devices.py`, `sensors.py`, `live_preview.py` | Async camera/frame mailbox, worker detection/conversion; display-only mirror; palm shares manual countdown |
| Photo lifecycle | `photo_views.py`, `photos.py`, `photo_drive.py` | Single-flight PhotoJobs over existing PhotoSession/store/catalog/printer/Drive; preserve originals |
| Game | `game_scene.py`, `game_layout.py`, `game_views.py`, `demo_game.py` | Original Stage/Flow/renderer/emitter; v2 persistent one-use DEMO ledger; no scanner/POS authority |
| Local reward/MOCK | `game_offer.py`, `mock_checkout.py`, `checkout_views.py` | Local verified DEMO outcome/quote/admission; one-use reward; nonpayable QR |
| Sandbox host | `sandbox_checkout.py`, `sandbox_views.py`, `qr_branding.py` | Existing KioskCheckout/QrisKioskClient and single-flight GameJobs; durable photo handoff; verified centered Meong QR; no GUI merchant key |
| Operator health | `health_service.py`, `operator_health.py`, `health_report.py` | Original v1 panel/backend/extracted worker; bounded observations and safe local reports |
| Diagnostics/readiness | `diagnostics.py`, `performance.py`, `readiness.py` | Local diagnostics/timings, safe inventory; preflight performs no device/provider readiness probes |
| Retention diagnosis (shared) | `retention_readiness.py`, `drive_storage.py`; `tools/check_drive_retention.py` | Explicit one-action authenticated status/parent-metadata read through original v1 configuration; no setup/upload/delete; original UTC retention/deletion unchanged |
| Payment service (shared) | `checkout_backend.py`, `checkout_store.py`, `payment_quote.py`, `qris_api.py`, `booth_auth.py` | Backend price, authenticated booth, idempotency, grants and reconciliation |
| Provider/client/journal (shared) | `midtrans_sandbox.py`, `midtrans_verify.py`, `qris_evidence.py`, `qris_images.py`, `qris_kiosk_client.py`, `qris_session.py` | Sandbox-only, independent order/amount/currency/reference validation, bounded/allowlisted I/O, atomic journal and process lease |

V2 filenames are under `photobooth/kiosk_v2/`; shared files under `photobooth/`.
`main.py` and v1 GUI/audio remain separate. Health reuses v1 helpers without
instantiating its application. [Reference map](gui-v2-branch-audit.md).

## Photo data, orientation and output

Local/default requires explicit UJI FOTO consent and creates no payment.
Each selected design has one three-photo session and at most one selected-photo
retake. Zero quantity deselects; 1–9 specifies copies, not capture sessions.
JPEGs preserve capture resolution and original orientation. Live preview uses
the bounded GPU mirror. Owner refinement, 26 October: v2 review thumbnails mirror
and the shared compositor mirrors photo pixels before applying the original masks.
One saved PNG serves result, print and digital strip; template/text/logo/QR stay
normal. Retake preserves replaced originals/history; detector/decoder frames stay
unmirrored. V1 composition defaults and previously saved outputs remain unchanged.

PhotoJobs rejects duplicate work. Minimize/page changes/camera loss cancel
countdown; restore does not automatically capture. Printing requires operator
opt-in and photo approval: --print automatically submits one durable batch/design
through existing PhotoJobs/PhotoTest; --manual-print keeps a separate print action.
Uncertain sends are held for inspection, not automatically retried.
Drive requires configured credentials/isolated pool and retention acknowledgement
before upload. A folder QR is not proof that all files uploaded, download works,
or cloud deletion is active.

With --drive, the ordinary host prepares/resumes the isolated queue at startup;
consent snapshots gate on actual verified-folder readiness. PhotoJobs owns client/
pool initialization and original QR encoding/cache. Photo approval/composition
triggers one optional auto-print outcome; UI rebuild/minimize/status updates do
not print. Result polls update the existing large QR as soon as the verified
assigned destination exists, including during upload. QR visibility never sets
UPLOAD_COMPLETE; the worker still verifies all required file bytes. Customer
uploads run FIFO; old recovery/reserves/content wait at request boundaries,
with bounded short customer retries before background failure release.
[Current scheduling, folder ownership and evidence](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).
Old queue resume creates no new visit/counter. Renderer/runner processes clear
ambient live delivery flags; explicit fixtures supply their own services.
[Print/Drive contracts, checks and rollback](qa/portrait-v2-print-drive/README.md).

Default photo profile: `data/kiosk-v2-p3/`; game/MOCK:
`data/kiosk-v2-p4/`; merchant trial:
`data/kiosk-v2-sandbox/<merchant>/<booth>/`, with `visit.json`, `orders.sqlite`
and photos under `photo-tests/`. Never substitute v1/payment journals to bypass guards.
[Retention](photo-retention.md).

## Pricing and payment authority

Shared catalog/workflow tariff: Rp5,000/design/session + Rp5,000/copy. Local/MOCK
win reward: Rp2,500 once/order, capped at subtotal. Backend QRIS accepts quantities
and computes its own full-price quote; it has no trusted Meong Fly promo API.
The native Sandbox requires explicit full-price/no-promo consent before creating
an order. GUI scores, amounts and PAID labels are never provider authority.

`tools/run_portrait_v2_sandbox.py` reuses the existing merchant-trial helper with
injectable v2 entry/environment/notice. Merchant Server Key stays in the backend;
GUI receives booth credentials only. Conflicting modes/inherited merchant keys
fail closed. Backend uses loopback HTTP; the current trial uses status checks/
provider reconciliation, without a public webhook/tunnel/deployment. Readiness
of that local service does not verify account credentials or settlement.

## Durable Sandbox → photo handoff

`CREATING → WAITING → RESERVED → STARTING → STARTED → COMPLETING → COMPLETED`.
Cancellation uses `CANCELLING → CANCELLED`; uncertainty can require `RECOVERY`.

- Persist the atomic journal before the first create request. Retry the same
  checkout key/order; backend reconciles cancellation/settlement races.
- RESERVED → explicit photo consent → durable STARTING → allocate one transaction
  → bind its ID → STARTED ACK. Countdown is unavailable before that ACK.
- Complete all selected designs before COMPLETED ACK. Abort/restart after possible
  capture requires operator reconciliation; never replay photo/charge/print.
- Pending/unknown/paid cannot be discarded by browse timeout or cart changes.
  RECOVERY has no reset-paid-order/refund/replay override.
- Stop waits for worker I/O before releasing the journal lease. Retired page
  callbacks cannot initiate a new action.

[Sandbox runbook](qa/portrait-v2-sandbox/README.md) · [P5 acceptance](qa/portrait-v2-p5/README.md).

## Game, layout and audio

Original game reference `672e3f7` (26 files), QRIS `3cc8a8e`, health `dbbe055`.
Provenance: [game](qa/portrait-v2-meong-reuse/README.md),
[QRIS](qa/portrait-v2-sandbox/reused-source.json),
[health](qa/portrait-v2-operator-health/reused-source.json).
Reference SHAs are dated; refresh before borrowing future changes.

Center the complete game world with uniform travel/spacing. Do not reintroduce
nonlinear far/near projection or right-anchored spawn (BUG-015/016). Resize retains
physics/score/session; game restore requires manual resume. Header animation owns
its own bounded pause/dispose lifetime, not a second physics loop.

Still ads use GUI BGM; videos use their own audio. Tutorial/gallery/photo/checkout
share one GUI loop; game uses its own loop. One enabled action emits one cue.
Minimize/close retires the prior owner/callbacks.

## Operator health seam

Actual `HealthPanelMixin.show_health_settings` and v1 label helper are reused.
The original `_refresh_device_health` method is extracted verbatim into a class
shell; original locks/scheduling/redaction guards stay intact. V2 maps `root.after`
to Kivy Clock, the existing mailbox to a read-only camera view, lazy printer
config to the worker, and buttons to the single v2 audio owner.

F12/header hold opens only idle without an invitation or Sandbox RECOVERY;
active jobs cannot be interrupted. Modal input epochs reject old release events.
Close/minimize/stop retires modal/probe/report callbacks. Manual open/refresh
runs one worker sweep; there is no automatic polling/watchdog, device switching,
second camera, print payload, order mutation or upload.

Operator button actions require a fresh permitted press and consume its release
once. Presses rejected while disabled/cooling down cannot become valid after a
worker finishes. Same-button repeats within 0.75 seconds are dropped, never
queued; callback busy-state claims precede the native SFX. The gate is per
button, so TUTUP remains available during refresh/report I/O. Customer controls
and original v1 panel/worker stay unchanged. [BUG-018](qa/portrait-v2-health-clicks/README.md).

Report JSON allows safe source/OS/dependency/display metadata and six status
observations; excludes photo pixels, keys/tokens, raw errors/logs, network addresses,
serial/queue identities and order/QR references. Physical/provider fields remain
NOT_RUN. READY only means the named bounded observation passed.
[Operator proof/form](qa/portrait-v2-operator-health/README.md).

## Evidence limits

[Current status](FEATURE_STATUS.md) and [test ledger](test_checklist.md) record the
780-test operator checkpoint and earlier 688-test P5 baseline, including CI skips.
Owner preflight `0dc6555` = READY_FOR_MANUAL_TEST, not merchant/hardware acceptance.
BUG-009, current device/provider/Drive/privacy and release gates remain open.
Device staging/switching, AI, WhatsApp and newer lab updates are separate scopes;
read-only Device Health is already in the active inventory above.
