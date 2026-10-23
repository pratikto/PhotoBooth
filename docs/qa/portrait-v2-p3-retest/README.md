# P3 Windows retest — responsiveness and optional gesture follow-up

Owner report, 2026-10-23 Asia/Jakarta: **21/34 checked, 13 open**, Windows 11,
100% scaling, laptop speakers, 20 reported cycles. Tested HEAD, resolution and
camera model/index are missing. [Original report](owner-retest-2026-10-23.txt)
and [structured audit](owner-analysis.json) preserve every checkbox unchanged.
A01's metadata is incomplete despite its checkmark. A03/A04, B04/B05, D01–D05
and E01–E04 stay failed OR not tested, not automatically PASS. Review/retake,
new shutter timbre, resize/audio and twenty-cycle/restart checks are owner-reported
passes with unknown HEAD; they do not certify a new source revision.

Scope is the already authorized P3 correction plus the owner's **“lanjuting dong”**
and **“push bertahap aja”**. Use only `feature/portrait-kiosk-v2-next`. No payment,
production transactions, scanner, discount, game integration, master change,
cloud deployment or remote deletion. Pre-fix rollback checkpoint:
`37e3c9264a595e93774c4ce3892133261f99ef30`. Stage 1 was pushed as
`a322237bc82c818b13093fadb0982332e24a82a2`; remote HEAD matched and
[CI 39916946241](https://github.com/pratikto/PhotoBooth/actions/runs/39916946241)
completed all three jobs SUCCESS. This is the rollback checkpoint before stage 2.

## Stage 1 — preview/touch responsiveness (BUG-013, device retest OPEN)

- Prepare bounded RGB preview bytes on a single background worker, with one
  replaceable pending frame and one latest output. No resize/color conversion/
  ndarray packing in the GUI preview callback. Original camera BGR pixels and
  saved-photo orientation/resolution stay intact; only display UVs are mirrored.
- Page revisions, camera loss, minimize and shutdown invalidate old work. Frozen
  frames do not renew their timestamp. Slow converters cannot queue old video.
- Starting photo I/O disables controls and updates one status label while keeping
  the current live panel/strip. Completion performs one page rebuild, retiring
  the old controls; old releases cannot capture the next photo.
- Existing diagnostic log gets aggregate UI-tick/new-frame/preview delivery
  rates, worst tick gap/upload time and page-build/slow-action timings. It writes
  no camera pixels or biometric identity. These rates are observed delivery
  rates, not a certified camera-driver FPS measurement.

[Before](response-baseline.json) / [after](response-preview-worker.json) synthetic
Linux/offscreen measurements use 90 full-HD source frames at 800×1280. Median
GUI preview call: **0.870 → 0.208 ms**; p95 **1.645 → 0.239 ms**. Capture-submit
callback: **5.669 → 0.755 ms**. Worker conversion is outside the measured GUI
callback; these are individual local runs, including differing warm-up/scheduling.
They demonstrate moving work off the GUI, **not** a Windows latency/FPS guarantee
or proof of the owner's hardware root cause. Keep BUG-013 open until device retest.

**77 focused tests PASS**, no skips: [transcript](stage1-tests.txt). Sixteen native P3 screenshots were reviewed at [800×1280](stage1-contact-800x1280.png) and [452×900](stage1-contact-452x900.png). Camera pixels/print transport are synthetic; originals are under `stage1-screenshots`. Actual Windows responsiveness stays open. [Source hashes](stage1-source.json).

## Stage 2 — face invitation and existing open-palm shutter (BUG-014)

The audited pre-fix v2 source did not connect the existing v1 palm service; the
owner's question describes a real missing input, not a failed gesture test.
Restore that optional capture input through the same countdown/camera/quota
checks as SIAP, never a separate capture path. Keep one hold/one shutter and
release-before-next-photo guards. Missing optional MediaPipe/model leaves SIAP
usable, with truthful on-screen status. Face invitation retains its approved
five-second hold and cooldown. Loading/inference must remain off the GUI.
The v2 adapter now connects that service. A deferred initializer imports optional
native packages off the GUI and reports idle/loading/ready/unavailable/disabled.
The real worker performs inference in its existing bounded mailbox; offers are
rate-limited while results are polled promptly. Face hold progress is visible in
the existing ad headline; no timer or confidence threshold is relaxed. Stalled
observations clear stale hold progress. The startup log records only camera
index and enabled flags; detector state changes help diagnose a disabled option.

The capture page shows one compact palm hint: preparing, raise/hold, lower hand,
or unavailable/use SIAP. Both manual and palm input call the same five-second
countdown, fresh-camera and busy checks. Manual presses latch the same release
policy. Page changes, camera loss and minimize invalidate old observations;
one retake per session and all capture storage rules are unchanged.

Open-palm needs the existing optional **MediaPipe 0.10.32** package. If it is not
installed in the Windows virtual environment, run:

```powershell
python -m pip install -r requirements-palm.txt
$env:PHOTOBOOTH_PALM_TRIGGER = "1"
$env:PHOTOBOOTH_FACE_TRIGGER = "1"
python tools/run_portrait_v2.py
```

The existing service caches the pinned public 8 MB model under
`data/models/gesture_recognizer.task`; first setup can need internet. It never
uploads camera images. A missing package/download failure keeps SIAP usable;
there is no fake gesture-ready state. The existing v1 detector/model service,
confidence, hold/release and camera ownership code are reused without edits.
**348 complete tests PASS, zero skips** with the optional native model fixtures:
[transcript](p3-retest-complete-tests.txt). A final **71 focused tests PASS,
zero skips** after the accepted face-inference-delay expiry and diagnostic timing
refinement: [transcript](p3-sensors-final-tests.txt). The final face adapter test
specifically preserves the five-second hold with 300 ms accepted inference delay;
truly stale progress resets without weakening source-time continuity.

[Native model check](p3-palm-native-tests.txt) accepts public open-palm imagery
and rejects fist/thumb-up/pointing/empty frames. A real model/worker also starts
v2's actual countdown from public sample pixels; holding the same hand cannot
start another. These are real native inference with synthetic camera acquisition,
not the owner's Windows hand/camera. [Fixture/model sources and hashes](native-test-assets.json).
Twenty-four fresh native widgets were reviewed at
[800×1280](stage2-contact-800x1280.png) and [452×900](stage2-contact-452x900.png),
including explicitly synthetic face-hold and palm-hold/unavailable/release states.
These status fixtures are not actual camera recognition evidence. Original PNGs
and hash reports are under `stage2-screenshots`; [source hashes](stage2-source.json).
The complete 348-test run preceded the final source-time expiry/logging/hint
refinement; the final 71 focused tests cover that source. No physical hand/face
PASS is claimed before testing the actual Windows setup.

## Remaining Windows evidence

- [ ] Tested HEAD, actual resolution, camera model/index and fresh diagnostic log.
- [ ] Preview and buttons feel responsive, including while face/palm inference runs.
- [ ] Real face five-second hold, invitation controls/timeout/cooldown.
- [ ] Manual and optional open-palm countdown; release latch; retake quota.
- [ ] Camera loss and minimize during countdown; no stale frame/shutter.
- [ ] Unchecked composition, physical print and Drive items from original report.
- [ ] Repeat twenty cycles and restart on the actual new HEAD.

## Final verification and retest form

**349 complete tests PASS, zero skips** at runtime source
`a059d30be8da6a3249f68946b59003c78addfc97`:
[final transcript](final-complete-tests.txt). This final run includes the last
face source-time expiry, camera-unavailable hint and total/audio/callback timing
changes, with both optional native model tests enabled. The earlier 348-test
snapshot above remains historical evidence, not the final count.

[CI 39919633523](https://github.com/pratikto/PhotoBooth/actions/runs/39919633523)
completed all three jobs SUCCESS on that exact source. Its original GitHub ZIP
SHA-256 and 40 main screenshot hashes across six clean-source reports were
verified and visually reviewed: [artifact verification](ci-artifact-verification.json),
[P3 contact sheet](ci-p3-contact.png), [browsing/short-window sheet](ci-browsing-contact.png).
CI's optional palm model fixtures are not installed; native palm inference is
proved by the local public-fixture tests, not falsely attributed to Windows CI.
The online artifact expires after seven days; contact sheets/reports and local
original captures remain committed. [Final source/legacy verification](final-verification.json)
confirms fifteen legacy services/media files remain byte-unchanged.

[Open the new 40-item Windows checklist with Submit Hasil](windows-checklist.html).
It starts unchecked with a new storage key, adds camera/index and where lag
starts, preserves missing metadata in the report, adds six open-palm cases, and
retains the original untested composition/print/Drive gates. G01/G02 still need
a declared twenty cycles; no check is granted automatically. Submit prepares a
prompt for manual paste into chat. Browser behavior was checked at 452 and
360 pixels, including Submit/report, index `0`, storage, metadata, cycle gate and
untested Drive: [browser checks](form-browser-test.json).

Windows update (on the required branch, inside the existing virtual environment):

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
python -m pip install -r requirements-palm.txt
$env:PHOTOBOOTH_PALM_TRIGGER = "1"
$env:PHOTOBOOTH_FACE_TRIGGER = "1"
git rev-parse --short HEAD
python tools/run_portrait_v2.py
```

The optional-package install is needed only if MediaPipe is absent. The first
palm model setup needs internet; already verified cache works offline. If a
problem persists, run `explorer .\data\diagnostics` and send the newest log.
It includes HEAD, enabled flags, model state and aggregate frame/action timings;
no camera images are logged. Note whether lag starts in idle or after capture.
No new Windows PASS is inferred from the report or source fixes. BUG-013 stays
OPEN for device responsiveness, BUG-014 awaits a real Windows palm retest, and
BUG-009 cloud deletion remains OPEN. P4/payment/scanner/game work remains outside
this task. To roll back, close v2 and use the unchanged v1 launcher, preserve all
photo/journal/counter files, and review normal same-branch revert commits rather
than rewriting branch history or deleting runtime data.
