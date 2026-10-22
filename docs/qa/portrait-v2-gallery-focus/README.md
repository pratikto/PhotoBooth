# Owner retest and gallery polish — 2026-10-22

Branch: `feature/portrait-kiosk-v2-next`. Starting code/document checkpoint:
`29a34198a4893df6fc399ac64767a04b7401935e`.

## Owner result and limits

Owner reports **41/41 boxes checked**, Windows 11 / laptop speaker / **10 completed
cycles**. Crash gates P01–P03, touch swipes, clicks, image/video music ownership,
minimize/close and reset are positively reported. Follow-up confirms arbitrary
window resizing works; the requested change concerns gallery proportions.

**Do not close the 20-cycle gate:** G03/G06 explicitly require twenty cycles,
while supplied metadata records ten. Tested HEAD, resolution and display scaling
are blank; the follow-up did not supply them. Preserve the raw checked count,
but do not call this final exact-SHA or twenty-cycle acceptance. [Audit](owner-retest.json).

The approved follow-up addresses slight lag after taps, actual strip motion,
and a gallery layout that gives most space to the strip images. Subsequent owner
instructions request mini-game-style Meong typography, floating arrows at the
lower corners of the strip area, and a clean overall composition.

## Response correction

Local Linux/offscreen profile at the starting source measured first gallery
entry **167.398 ms**; uncached template changes **36–62 ms**, dominated by Pillow
artwork decode/resizing. These are callback timings, not Windows input-to-display
or speaker latency and not a guarantee about video decoder shutdown.

- Prepare silent button/music handles during idle. Valid button feedback starts
  before routing; short button feedback survives page handoff, while camera-only
  effects still stop on silent pages and all sounds stop on suspend/close.
- One worker prepares detached RGB previews of the twelve approved masters,
  prioritizing the first gallery's three strips. Only the main thread creates
  GPU textures. Reading the warmup cache never waits; early uncached access keeps
  the existing synchronous fallback. Queued warmup is cancelled on close.
- Copy changes update only the quote/count; they no longer touch image rendering.

**68 focused tests PASS**, including silent/idempotent audio preparation,
feedback-before-callback, no copy-triggered image work, worker priority/failure,
nonblocking cache access, queued-work cancellation and native twenty-cycle PCM.
[Transcript](response-tests.txt).

[Before timings](latency-before.json), [immediate after timings](latency-after-immediate.json)
and [after two seconds idle](latency-after-idle.json). The latter explicitly
waits for background preparation and records ready-preview count; first use
before warmup completes can still decode synchronously. No synthetic timing is
presented as a measurement on the owner's Windows machine.

Response source checkpoint: `67e9da8930a3449299b2264c5b5242a990f68114`.
[Exact-SHA CI 39798019411](https://github.com/pratikto/PhotoBooth/actions/runs/39798019411)
completed SUCCESS, all three jobs, including Windows native dummy audio.
[Job metadata](response-ci-jobs.json).

## Preview focus, motion and typography

- One compact brand/title header, a flexible preview card, one compact copy/cart
  card, and the payment/return footer. The selected strip occupies at least 49%
  of window height at all five tested sizes; previous/selected/next remain full
  1:3 images. The gallery removes redundant explanatory rows.
- Previous/next arrows float inside the preview area's lower corners. They do
  not obscure the selected strip or consume a separate navigation row. Copy
  controls, totals and disabled-payment text remain visible.
- Preview source is now 320×960 for the larger display; the twelve approved
  masters and physical print output are unchanged.
- Native image position, scale and opacity interpolate for a 200 ms ease-out.
  Drag follows the finger before release; a horizontal release selects once.
  Short/vertical drags return to the current strip. Five pooled images avoid
  allocating widgets or decoding artwork per animation frame.
- Rapid inputs settle the current logical choice and replace its motion rather
  than queue navigation. Resize, minimize, retirement and close cancel motion
  and release pointer ownership. Copy changes settle motion before updating the
  current choice's quantity.
- MEONG / PHOTOBOOTH uses native 5×7 pixel glyphs and offset shadows. Only the
  nine required glyph data entries and title color/shadow references are copied
  from read-only Meong Fly SHA `672e3f7089bb40940e5b41644ceb656aa63aafbb`.
  No game module is imported. The transparent camera artwork is unchanged.

The final higher-resolution layout's [local callback profile](latency-gallery-final.json)
records all twelve previews ready after two seconds idle: gallery entry
**28.306 ms**, next-template callbacks **0.154–4.786 ms**, copy updates
**0.060–0.149 ms**. The baseline was 167.398 ms / 36–62 ms for entry / uncached
changes. These are Linux/offscreen Python callback measurements; animation,
input-to-display latency, video retirement and Windows speaker timing are not
certified by this profile. First use before warmup can still decode synchronously.

## Verified local results

- **71 focused tests PASS**, zero skips: [transcript](gallery-focused-tests.txt).
  Covers live drag, one selection per swipe, secondary touches, real movement,
  rapid-input replacement, pause/retirement, hero proportions and floating-arrow
  bounds in addition to navigation/audio/worker regressions.
- **306 complete tests run: 304 PASS, 2 optional palm-model skips**, zero failures
  or errors: [transcript](complete-tests.txt).
- **3 fresh-process 150% density checks PASS**: preview/arrow bounds, live resize
  and real pointer coordinates, tutorial scrolling and button targets:
  [transcript](density-150-tests.txt).
- Compile and whitespace checks PASS. The native PCM test probe is installed
  only while sampling, removed before Cython playback calls, to avoid a
  test-only mixer-lock/GIL inversion. Application audio ownership is unchanged
  in the visual stage. Real PCM output remains checked across twenty cycles.

## Screenshot and animation evidence

All thirty native page PNGs were reviewed, six states at each size:
[800×1280](screenshots/contact-800x1280.png),
[452×900](screenshots/contact-452x900.png),
[360×640](screenshots/contact-360x640.png),
[452×600](screenshots/contact-452x600.png),
[800×600](screenshots/contact-800x600.png).
Contact sheets resize the captures for review; originals and PNG hashes are in
each size directory. Tutorial screenshots show the initial scroll position;
automated tests verify that the fourth step can be reached.

- [Gallery 452×900](screenshots/452x900/04-templates-452x9000001.png)
- [Gallery/cart 800×1280](screenshots/800x1280/05-copy-cart-800x12800001.png)
- [Sampled native slide GIF](screenshots/452x900/carousel-452x900.gif)
- [Nine motion frames](screenshots/contact-motion.png) and
  [offset/position/hash record](screenshots/452x900/report-452x900.json)

The GIF samples native widget FBO frames and is not an FPS benchmark. Local
capture manifests honestly record base `67e9da8` plus uncommitted source changes.
[Source hashes](local-source-manifest.json) identify exactly what was tested;
the clean exact-commit CI and original artifact are recorded below.

## Exact-source CI and original artifact review

Visual/motion code checkpoint: **`5a568bf12fa9756d6f233387663c5371b18af491`**.
[Run 39803887478](https://github.com/pratikto/PhotoBooth/actions/runs/39803887478)
completed **SUCCESS, all three jobs**. [Verified metadata](visual-ci.json).

- Navigation/audio/preview job: **49 PASS**, [transcript](pure-ci-tests.txt).
- Desktop job: widget smoke, twenty-cycle native PCM checks and all four
  screenshot captures SUCCESS. Its native PCM process reports 2 PASS.
- Genuine Windows Python 3.12 native SDL job: **31 PASS**, including named DLL
  loading, safe fallback and twenty-cycle PCM: [transcript](windows-ci-tests.txt).
  Dummy output does not certify the owner's physical speaker or Windows GUI.

Original artifact `12436731940`, 3,573,100 bytes, downloaded and its ZIP digest
matched GitHub:
`048302526ca1744e8f46c2208304d97f3d211210d05cf64e18af8bc952b32059`.
All four manifests report the exact checkpoint with **tracked_changes=false**.
All **24 page PNGs and nine motion frames** match their manifest SHA-256 hashes
and were visually reviewed. The tested source-file hashes also match the local
capture manifest; no runtime/renderer changes were made after local validation.

Preserved originals and review sheets:
[800×1280](ci-original/contact-800x1280.png),
[452×900](ci-original/contact-452x900.png),
[360×640](ci-original/contact-360x640.png),
[800×600](ci-original/contact-800x600.png),
[motion frames](ci-original/contact-motion.png),
[original sampled GIF](ci-original/carousel-452x900.gif).
No synthetic visual blocker was found. Windows response/smoothness and the
twenty-cycle owner gate remain separate from this CI/artifact result.

## Checkpoints, remaining work and Windows retest

- Pre-follow-up rollback reference: `29a34198a4893df6fc399ac64767a04b7401935e`.
- Response-only rollback reference: `67e9da8930a3449299b2264c5b5242a990f68114`.
- Visual/motion source and current application rollback checkpoint:
  `5a568bf12fa9756d6f233387663c5371b18af491`, exact-SHA CI SUCCESS and original
  artifact reviewed. Normal push and remote HEAD match were verified at the
  source commit. Later evidence-only commits must not inherit its CI result.

No remaining defect was found in the reviewed synthetic layout or tests.
Windows perceived tap lag, animation smoothness and preference for the new
composition still need owner retest. Cold preview decoding can still pause an
early first entry. Existing project hardware/Drive issues are not closed here.
No game/payment/scanner/backend integration or master change is made.

Record the actual `git rev-parse --short HEAD` when testing. Use the current
[35-item clickable V4 form with Submit Hasil](windows-checklist.html) for the
gallery/animation follow-up. Download the HTML and open it in Edge/Chrome;
after testing, choose **Submit Hasil → Salin prompt**, then paste and send in
chat. The file works offline and cannot send directly to a conversation.
It includes startup, branding, strip layout, motion/swipe, response/clicks,
music, lifecycle, twenty-cycle and prototype-boundary checks.

V4 uses separate storage, starts with every item unchecked, and does not prefill
the tested Windows HEAD. F05–F06 stay unavailable until a whole-number cycle
count of at least twenty is entered; reaching twenty never checks them
automatically. Lowering the count clears those two checks. Missing HEAD and
unmet duration are explicitly qualified in the exported report.
The [old 41-item V3 form](../portrait-v2-start-photo-crash/windows-checklist.html)
remains a historical crash-retest form; its checkmarks are not imported.

Form-only verification on 2026-10-23 (Asia/Jakarta): JavaScript syntax and
**11 DOM behavior checks PASS**, including gate enforcement/restore, missing
HEAD, separate storage, partial Submit, prompt refresh, literal notes, clipboard
API/fallback and UTF-8 download. [Transcript](windows-checklist-tests.txt).
This verifies the form logic, not browser visual rendering or new application
acceptance. Application, renderer and CI configuration are unchanged.

The focused UI checks represented in the form are:

- [ ] New gallery: strip is the main focus, all three full previews are visible;
  arrows float at the lower corners without covering the selected strip.
- [ ] MEONG PHOTOBOOTH typography matches the mini-game style on every page.
- [ ] Arrows and swipes move the images smoothly, one selection per gesture;
  short/vertical motion does not change selection.
- [ ] Rapid taps, copy changes, resize and minimize during motion do not cause
  delayed actions or lose the selected template/cart.
- [ ] Button response feels prompt, including an early first visit and a visit
  after at least two seconds idle; each enabled action clicks once.
- [ ] Finish **at least twenty** full ad → tutorial → gallery → ad cycles;
  verify clicks/music every cycle, image/video ownership, restore and clean exit.

Fresh Windows acceptance for the new source remains OPEN. Ten reported cycles
at an unknown prior HEAD do not close the new version's twenty-cycle gate.
