# Portrait v2 P3 — camera, photo workflow and service adapters

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

## P3b — next authorized stage

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
not physical camera/printer/Drive acceptance. The native photo pages follow in
the next implementation checkpoint. Rollback before adapters: `579fbf3be7dbb2b3ec4e51e6a9b8454f921e97ee`.

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

Integrate actual preview/countdown/three captures, selected single retake,
composition, physical-copy output and truthful local/Drive results through
existing services. Keep admission explicitly nonfinancial for this P3 test flow;
do not enable the payment/scanner/game controls or mark an order paid. Preserve
original pixels; mirror the live preview only. Printing and uploads must remain
explicit, traceable, isolated from production storage and safe against duplicate
or uncertain sends. No P3b implementation/test PASS is claimed by the P3a commit.

## Windows acceptance remaining

- [ ] Record actual HEAD, screen dimensions/scaling and camera model/index.
- [ ] Initial camera open/reconnect does not freeze idle ads or touch buttons.
- [ ] A real face held for five seconds shows one invitation over the current ad;
  manual Foto/Game/Dismiss work; timeout/cooldown prevent repeated invitations.
- [ ] Tutorial/gallery/game preview and minimize do not accept stale detections.
- [ ] Unplug/replug recovers one camera; close releases the device; manual entry
  remains usable when camera/detector is unavailable.
- [ ] P3b capture/review/print/Drive hardware checks after its implementation.
- [ ] Complete twenty Windows cycles and clean restart for the prior F05/F06 gate.

No native Windows camera, actual face detection, paper output or cloud delivery
is certified by Linux/offscreen or mocked service tests.
