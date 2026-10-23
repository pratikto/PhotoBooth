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
