# Portrait v2 P3 — camera, photo workflow and service adapters

> **Later print/Drive continuation, 25 October:** the owner selected automatic
> print as v1 and background Drive. Use the current ordinary launcher `--print
> --drive`; `--manual-print` is the explicit manual fallback. The old manual-only
> flags/instructions below remain a dated P3 snapshot. [Current runbook, evidence
> and eleven-item form](../portrait-v2-print-drive/README.md).

> **Dated source/QA record, retained for traceability.** Results, “latest/current”,
> OPEN/PENDING labels, next actions and authorization limits below apply to this
> package's recorded source and report date. Later owner reports and source work
> can supersede its status; they do not rewrite these test results. Use
> [current status](../../FEATURE_STATUS.md), [test ledger](../../test_checklist.md)
> and [current handover](../../DEVELOPMENT_HANDOVER.md) for continuation. Historical
> checklists are not an instruction to repeat already accepted tests.

> **Later P3 owner result:** the [focused preview/button record](../portrait-v2-preview-redraw/README.md)
> supersedes the earlier 21/34 report with 16/16 checked and twenty cycles at
> unknown tested HEAD/device metadata. BUG-013/014 are owner-reported monitoring.
> The 34/40-item forms below retain their original scope, not a new required retest.


Owner authorization, 2026-10-23 (Asia/Jakarta): **“oke tolong eksekusi p3”**.
Branch remains `feature/portrait-kiosk-v2-next`; pre-P3 checkpoint:
`419cfedfa63bd53df64831437c6d63f25bc1fb10`.

This explicitly authorizes staged P3a/P3b camera/face/photo/print/Drive adapter
work. It does not authorize real payments, scanner, discounts, game integration,
production transactions, master merge or changes to existing customer records.
Prior Windows F05/F06 twenty-cycle acceptance is still unverified; BUG-012 is
owner-reported PASS / monitoring, not a newly reproduced defect.

## P3a — camera and face invitation

- One `AsyncCamera` adapter reuses `photobooth.camera.Camera`. Opening, initial
  driver read, reconnect and close run on a manager worker. The GUI only polls a
  bounded latest-frame mailbox; pause immediately invalidates its frame. Late
  opens cannot publish after close. Camera service/handle ownership is reused.
- `FaceInviter` reuses `FacePresenceWorker` and `FacePresenceTrigger`, including
  the bundled offline OpenCV detector, five-second hold, fifteen-second overlay
  lifetime and forty-five-second cooldown from the advertising configuration.
  No face identity, recording, image save or model download occurs during idle.
- Only fresh observations from the current advert-page revision can invite.
  Other pages, missing frames, minimize and shutdown pause/invalidate detection.
  Manual entry remains available when camera/detector is unavailable.
- The real invitation overlays the same ad player, preserving playback and
  choosing the existing tutorial/game-preview paths. Retired invitation buttons
  are disabled within that overlay only and cannot emit clicks or navigate.
- `PHOTOBOOTH_CAMERA=0` disables the camera, `PHOTOBOOTH_FACE_TRIGGER=0` disables
  invitations, and `PHOTOBOOTH_CAMERA_INDEX` selects the existing device index.
  Camera and face detection default on in the dedicated launcher; QA captures
  and widget tests explicitly disable hardware. A single camera stream is used.

**86 focused tests PASS**, zero skips: [transcript](p3a-focused-tests.txt).
**321 complete tests run / 319 PASS / 2 optional model skips**, no failures or
errors: [transcript](p3a-complete-tests.txt). Threaded tests cover slow open,
late completion, pause/resume, disconnect/reconnect, stale frames and observations.
Real widgets verify automatic overlay routing, unchanged ad-player identity and
inert retired invitation buttons. Existing face tests load the bundled native
model and verify hold/cooldown behavior; physical positive-face QA remains open.

Twelve fresh audio-enabled captures were reviewed at
[800×1280](p3a-contact-800x1280.png) and [452×900](p3a-contact-452x900.png).
All twelve are pixel-identical to the previous reviewed P2 pages. Native camera
input is disabled in captures; they do not prove actual face-trigger behavior.
[Source hashes and limits](p3a-local-source.json); captures honestly record the
pre-P3 base plus tracked changes. Matching-source CI follows the normal push.

## P3b — connected source implementation

### Service adapter checkpoint

`photos.py` reuses the actual `TransactionStore`, `PhotoSession`, composition and
printer services behind a single-flight worker. The test namespace is
`data/kiosk-v2-p3`, default booth ID `PB001V2`; configured IDs must end in `V2`.
No paid admission or production counters/manifests are touched. Three source
JPEGs and an optional one-photo replacement remain unmirrored; all originals
are preserved. One design creates one session and N copies of the same output.

Printing persists SENDING before one batch, then SUBMITTED or UNCERTAIN.
Repeated sends are rejected, restart never replays jobs, and an uncertain result
requires operator acknowledgement. Paper output is never inferred from send success.
Drive is opt-in and uses a separate pool. Uploads are held until the existing
backend acknowledges retention; no remote cleanup/deployment is attempted.
Default local composition has the existing MODE LOKAL footer, no fake QR.

**74 service tests PASS**, including nine new real JPEG/composition, quota,
failure, single-flight, isolated-ID, print-journal and retention-guard tests:
[transcript](p3b-service-tests.txt). These exercise adapters with fake devices,
not physical camera/printer/Drive acceptance. This checkpoint precedes the native
pages described below. Rollback before adapters: `579fbf3be7dbb2b3ec4e51e6a9b8454f921e97ee`.

### New v2 shutter, 2026-10-23

The owner requests a better camera SFX than v1. V2 now selects the original
`meong-v2-shutter-soft.wav`: a 0.30-second rounded two-curtain click with a soft
spring return, synthesized deterministically by `kiosk_v2/shutter.py`.
The old shutter file and v1 controller are unchanged. **32 audio tests PASS**,
including actual new-shutter PCM at the native SDL dummy mixer output:
[transcript](shutter-tests.txt). This does not certify Windows speaker timbre.

- [ ] Hear the new shutter on Windows after a successful capture/retake.
- [ ] Failed save or cancelled countdown produces no shutter.
- [ ] Accept its volume and timbre with the music playing.

Rollback checkpoint before this audio change: `9e01225180f01bf4a72d2a5927941e6f10d84f38`.
P3a matching-source [CI 39877277390](https://github.com/pratikto/PhotoBooth/actions/runs/39877277390)
completed with all three jobs successful; that run predates the new shutter.

### Native flow and lifecycle

The native gallery now exposes **UJI FOTO** after at least one copy is selected.
A separate **MODE UJI / TANPA PEMBAYARAN** consent page admits the run. Ready
camera → manual five-second countdown for each of three photos → review →
optional selected single retake with a new countdown → actual strip composition
→ explicit optional test print → next selected design or finish to advertising.
Payment remains disabled. There is no fake paid status or production admission.

Only the live camera texture is horizontally mirrored. Saved/reviewed/composed
and queued upload bytes remain in camera orientation. A successful JPEG save
emits the new v2 shutter once; failed saves and interrupted countdowns do not.
Camera loss cancels countdown and requires a fresh manual start. Minimize pauses
audio/camera and cancels countdown; restore cannot execute the old touch event.
Active photo pages are protected from generic browse timeout and idle resets.
Worker outcomes are polled on the GUI and deferred while minimized. The launcher
waits briefly for device and photo I/O shutdown after the window closes, while
its diagnostic log is still open.

The single photo-service environment stays alive after finish/cancel, so its
Drive queue can continue while idle and subsequent visits get fresh photo state.
An hourly local-only retention worker reuses the existing 15-day cleanup under
the isolated P3 photo root. No remote cleanup is called. A new test run never
reuses IDs. Early exit preserves captured files and records that it ended early.
Print or upload errors never silently mark payment, paper or cloud delivery PASS.

### Launch on Windows

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
git rev-parse --short HEAD
python tools/run_portrait_v2.py
```

Activate the existing Windows Kivy virtual environment first. Camera and face
invitation default enabled; use `PHOTOBOOTH_CAMERA_INDEX` for the actual device.
Audio defaults enabled. No new environment or installation is needed if the
previous full v1 environment already includes OpenCV, Pillow, Kivy and the
existing `qrcode[pil]` requirement. A partial GUI-only install must add the
repository requirements before testing actual QR/Drive/printing adapters.

Default photo output: `data/kiosk-v2-p3/photos/PB001V2_########/` with raw JPEGs,
composed PNG and manifest. Default strip footer is **MODE LOKAL**, without a
fake QR. The existing v1 `photos/`, counter/pool and customer records are untouched.
For deliberate **operator device tests only**, set before launching:

```powershell
$env:PHOTOBOOTH_V2_PRINT = "1"  # enables explicit CETAK UJI; does not auto-print
# Optional, only with configured TEST Drive account/backend:
$env:PHOTOBOOTH_V2_DRIVE = "1"
```

Printing reads the existing operator printer settings without rewriting them;
it sends only after CETAK UJI is pressed. Drive reads existing configuration and
uses a separate `PB001V2` pool; an enabled but unavailable/misconfigured Drive
blocks admission instead of pretending a QR is ready. Do not change the booth
ID on an existing counter. `PHOTOBOOTH_V2_BOOTH_ID` must end in `V2` to avoid
claiming the legacy remote namespace. No credentials are committed or displayed.

### Final source QA and screenshots

The final evidence files are `p3b-final-complete-tests.txt`,
`p3b-final-focused-tests.txt`, `p3b-domain-final-tests.txt`, `p3b-form-test.json`
and `p3b-source.json`. **335 complete tests run / 333 PASS / 2 optional-model skips**, no failures or errors. **87 final focused tests PASS**, zero skips, after the final compact-layout/payment-label adjustment. Their exact source limits are recorded there;
they do not certify devices. The domain suite includes **20 complete simulated
photo runs** with unique IDs/fresh quotas and a real adapter sequence from pool
claim → three JPEGs + retake → composition → offline upload → verified retry,
without duplicate uploads or remote cleanup.

Fresh native P3 captures at [800×1280](p3b-contact-800x1280.png) and
[452×900](p3b-contact-452x900.png) cover consent, ready, countdown, review,
retake, local result, uncertain print and unavailable camera. Preview pixels and
print transport are synthetic; the JPEG/PNG storage/composition and native
widgets are real. Review corrected camera containment and compact consent
height before accepting the final captures. Twelve refreshed browsing-page captures were also reviewed at [800×1280](p3b-browsing-contact-800x1280.png) and [452×900](p3b-browsing-contact-452x900.png), preserving full strip focus with the added UJI FOTO CTA and readable disabled payment label. Original image hashes are in
`p3b-screenshots/p3-report-*.json`.

[Open the 34-item Windows form with Submit Hasil](windows-checklist.html).
Submit prepares a prompt for manual paste into chat; it cannot send to the
conversation. Blank items are never PASS. HEAD starts empty, storage is separate
from previous forms, and G01/G02 require a declared twenty cycles before they can
be checked. Browser verification covers Submit, counts, storage, unknown HEAD,
unchecked Drive items, the cycle gate and 360-pixel layout.

### Checkpoints and rollback

| Commit | Purpose |
| --- | --- |
| `419cfedfa63bd53df64831437c6d63f25bc1fb10` | Pre-P3 owner-reported return-to-advert working checkpoint |
| `9e01225180f01bf4a72d2a5927941e6f10d84f38` | P3a asynchronous camera/face invitation |
| `579fbf3be7dbb2b3ec4e51e6a9b8454f921e97ee` | Original v2-only shutter |
| `5c83a26f5fe24f58fe9acf72f88e653376aea98b` | Photo/print/Drive service adapter checkpoint before native pages |
| `c04534fcf3a4026aab00f62b9a606bd72566331d` | Connected native P3 photo pages; CI exposed missing QR dependency |
| `569dbf50a07a2c2154430a762c6fd1c340d8bc59` | CI dependency corrected; exact-source three-job SUCCESS |

All pushes are ordinary pushes to the existing branch, with remote HEAD checked.
[Final verification record](final-verification.json) pins the native source and
[CI 39880474594](https://github.com/pratikto/PhotoBooth/actions/runs/39880474594)
to `569dbf50a07a2c2154430a762c6fd1c340d8bc59`: all three jobs SUCCESS.
[CI test counts](ci-test-counts.json); [artifact digest/hash verification](ci-artifact-verification.json).
The original 4.24 MB GitHub artifact was downloaded, its SHA-256 matched, and
all 40 main screenshots across six clean exact-source reports were hash-checked
and visually reviewed: [P3 contact sheet](ci-p3-contact.png),
[browsing/short-window sheet](ci-browsing-contact.png). The online artifact has
GitHub’s seven-day retention; contact sheets, report JSON and local original PNGs
are committed here. Thirteen legacy/v1 source/media files are byte-unchanged
from the pre-P3 checkpoint. The final documentation-only follow-up does not
change those runtime hashes. Do not force-push, merge master or reset/delete test photos
to roll back. To stop P3 device use, close v2 and run the established v1 launcher;
keep v2 files/manifests/journals for diagnosis. For a reviewed source rollback,
revert the relevant P3 commits on this same branch through the normal tests/push
process; do not rewrite history or erase counters/uncertain print journals.

### Remaining bugs and limits

- **BUG-009 stays OPEN:** no Apps Script deployment or remote 30-day cleanup
  certification was authorized. P3 holds upload without retention acknowledgement;
  backend acknowledgement alone does not prove eventual cloud deletion.
- **BUG-012 remains owner-reported PASS / MONITORING:** no new Windows exact-HEAD
  twenty-cycle result was supplied; do not substitute Linux simulation for it.
- Actual face trigger, Windows camera/USB lifecycle, new shutter timbre, physical
  N-sheet count, QR scan and real account delivery remain **NOT RUN here**.
- Interrupted photo tests are preserved, not automatically resumed. Uncertain
  print jobs are never replayed on restart. Operator must inspect paper/journal;
  no paid recovery, reprint commerce or new administrative feature is implied.
- P4 game/receipt/QRIS and P5 device certification remain separate milestones.

## Windows acceptance remaining

- [ ] Record actual HEAD, screen dimensions/scaling and camera model/index.
- [ ] Initial camera open/reconnect does not freeze idle ads or touch buttons.
- [ ] A real face held for five seconds shows one invitation over the current ad;
  manual Foto/Game/Dismiss work; timeout/cooldown prevent repeated invitations.
- [ ] Tutorial/gallery/game preview and minimize do not accept stale detections.
- [ ] Unplug/replug recovers one camera; close releases the device; manual entry
  remains usable when camera/detector is unavailable.
- [ ] Complete the linked 34-item P3 camera/capture/review/print/Drive Windows form on the actual tested HEAD.
- [ ] Complete twenty Windows cycles and clean restart for the prior F05/F06 gate.

No native Windows camera, actual face detection, paper output or cloud delivery
is certified by Linux/offscreen or mocked service tests.
