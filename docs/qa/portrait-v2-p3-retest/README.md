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
`37e3c9264a595e93774c4ce3892133261f99ef30`.

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

## Stage 2 — face invitation and existing open-palm shutter

The audited pre-fix v2 source did not connect the existing v1 palm service; the
owner's question describes a real missing input, not a failed gesture test.
Restore that optional capture input through the same countdown/camera/quota
checks as SIAP, never a separate capture path. Keep one hold/one shutter and
release-before-next-photo guards. Missing optional MediaPipe/model leaves SIAP
usable, with truthful on-screen status. Face invitation retains its approved
five-second hold and cooldown. Loading/inference must remain off the GUI.
No physical hand/face PASS is claimed before testing the actual Windows setup.

## Remaining Windows evidence

- [ ] Tested HEAD, actual resolution, camera model/index and fresh diagnostic log.
- [ ] Preview and buttons feel responsive, including while face/palm inference runs.
- [ ] Real face five-second hold, invitation controls/timeout/cooldown.
- [ ] Manual and optional open-palm countdown; release latch; retake quota.
- [ ] Camera loss and minimize during countdown; no stale frame/shutter.
- [ ] Unchecked composition, physical print and Drive items from original report.
- [ ] Repeat twenty cycles and restart on the actual new HEAD.
