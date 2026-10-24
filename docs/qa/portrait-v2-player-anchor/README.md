# BUG-016 — Meong shifts too far right after window resize

Owner report, 2026-10-24: live Meong is too far right at portrait and maximized
landscape sizes. Authorized scope is this P4 layout regression only, on
feature/portrait-kiosk-v2-next. Starting remote/local HEAD:
3ba2e09834ff2889b38b6d4a5521d0c0009e1b09. No P5 or production integration.

Cause: BUG-015 removed nonlinear motion, but aligned the entire original world
to the right edge using the complete surplus width as a translation. That also
moves the player right as the window grows. Prior constant-speed checks passed
without a player-position criterion; those passes do not mean visual acceptance.

Correction: center the complete original gameplay world using one shared
translation. Keep Meong at its original left-side location within that world;
do not move just the mascot or change collision/engine constants. Original
camera, trail, asteroid and film use the same transform. The continuous sky and
responsive full-window HUD/menu remain. On wide windows the original game world
occupies the centered part of the sky; spawn stays at its original world edge,
not at the physical window edge. Do not stretch the approach or add difficulty.

Reference branch feature/meong-flappy-challenge remains read-only at
672e3f7089bb40940e5b41644ceb656aa63aafbb (remote verified this task). Preserve all
26 original source/art/test files, ledger consumption, MOCK guards and audio.

Gate: reproduce current error with a real native camera-layer position check;
then check portrait 800×1280 / 452×900, short 360×640 / 800×900 and landscape
1920×1080. Check balanced gameplay margins, player left of stage center,
unchanged rendered wave velocity/spacing, collision/film alignment and resize
state. Run focused native checks, native screenshots
at the required sizes plus landscape, then commit/push and verify remote HEAD.
After the owner added a same-level mascot/wordmark impact animation, that becomes
a separate second stage. Run the single final full regression after that stage.
Matching-source CI and Windows physical acceptance are separate evidence.

Rollback checkpoint: 3ba2e09 (known right-anchor defect); reverting only this
layout change also restores that defect. Preserve all consumed attempts/orders,
photo and print journals. Never reset ledgers or merge to master for rollback.

## Stage 1 result

The new native regression fails on the old right anchor: [reproduction](reproduction.txt).
With the shared centered translation, **20 focused native tests PASS, zero skips**:
[transcript](focused-tests.txt). Includes actual camera-layer positions, original
26-file hashes, original camera/film geometry, five-size rendered wave travel,
engine timing, pointer, lifecycle and local offer guards. No original engine,
renderer or assets are modified.

[Before](before.json) / [after](after.json) native measurements: at 1920×1080,
Meong body center moves from **80.12% to 43.56%** of stage width; at 800×1280,
43.05% to 31.55%; at 452×900, 30.30% to 27.42%. World velocity and wave spacing
are identical before/after at each size. Numeric coordinates are stage logical
units; the host also scales short windows.

**45 native captures** have verified hashes and dimensions. Active gameplay
visually reviewed at [800×1280](game-800x1280.png), [452×900](game-452x900.png),
and [1920×1080](game-1920x1080.png). [Capture reports](screen-reports.json).
These use injected sample states and are not physical Windows pacing acceptance.

Stage 1 source **848a52d0b5cf5c0986965db0d9c2232309a2ba5b**, normal push and
remote HEAD verified. Matching-source CI 40071831101 has all three jobs SUCCESS.

## Stage 2 — same-level flying mascot and impact spin

Owner additionally asks for Meong level with the centered wordmark, hitting it
and causing a spin, plus moving feet/rear appendage, waving rainbow and printing
photos like the mini-game. This stage reuses original artwork, camera/aperture
composition, paper Quad renderer, film tiles, slot metadata and InstantPhotoEmitter.
Both camera/paper composition methods are the original method objects. No game
engine/flow, scanner, camera or printer is instantiated for the decorative header.
All 26 reference files remain unchanged.

The original game has no independent moving-header/limb renderer. The narrow
brand_flight adapter therefore caches 12 tiny source-derived limb/tilt poses
once, moving only authored source-pixel joint crops clear of the aperture. It
adapts the original five-band wave geometry for a moving header; calling the full
original game draw would also draw HUD/hazards. There are no per-frame Pillow
operations, decodes or texture uploads. Native rectangles and cached textures
render the original camera; original emitter poses and Quad UV crops feed one
photo from the real authored slot, release it and let it fall in header space.
Those photos are decorative, with no actual capture or printing.

The existing flight Animation is the only decorative pose clock. Each pass
has one geometric contact gate at the lettering edge. Both existing pixel
words rotate together around a vertical axis for 0.65 s, with a small tilt,
then return to zero at the unchanged centerline. This keeps the full turn inside
short headers instead of throwing letters over nearby controls. Minimize freezes
flight, pose/film clock and spin; resume finishes the remaining turn. Resize
preserves flight/spin, updates the pivot and retires only decorative sheets whose
coordinate scale changed. Page retirement/close cancels both animations and the
single pending drawing trigger. No background game loop or sound is added.

**28 focused native tests PASS, zero skips**: [transcript](impact-focused-tests.txt).
Tests cover actual Clock contact from both directions, one hit per pass, settling,
pause/resize/resume/disposal, immutable source/aperture, moving joints/rainbow,
original compositor identity, attached versus detached film, and original game
position/motion/ledger guards. An early preview found clearing StencilView's
reserved mask instructions unsafe; art now clears only its child Canvas. Early
test-harness issues (default texture classification and an overly short fixed
wait for contact) were corrected using actual texture exclusion and bounded
native-condition waiting. No failing check is being counted as PASS.

[Live header GIF](header-live-clock.gif) is recorded from the actual native Clock,
not injected animation phases: 76 frames across 10.66 s, hardware/audio disabled.
[Clock/pose/film samples](live-clock.json), [normal](header-level.png),
[impact](header-impact.png), [film phase](header-film.png), [return](header-return.png).
A vertical-axis turn is briefly edge-on by design. The page screenshot tool now
explicitly freezes a neutral header pose before static ink/layout checks;
static captures do not substitute for these real-clock tests/recording.

[14-item Windows form with Submit](windows-checklist.html) uses fresh storage and
preserves unchecked/untested entries. A03 checks the impact, B02/B03 lifecycle,
A01 game position. Twenty-cycle gate remains explicit and never auto-passes.
Final full regression, final static screenshots, source push and CI follow below.

## Full-gate QR test correction

First full gate: **540 tests, 1 failure, 0 errors/skips**, not PASS. It failed
only the old native-scale OpenCV reader test for a randomly generated MOCK QR:
[first full transcript](first-full-tests-failed.txt). The exact failed payload
is reproduced with the existing presentation encoder, without changing QR
pixels: native-scale decode fails; 2× and 3× nearest-neighbour views decode the
exact text. [Reproduction](mock-qr-scale-reproduction.json).

The widget test now reuses the existing bounded pixel reader and explicitly
includes that failed ID plus a second deterministic ID. It still asserts the
whole actual payload. The reader's implementation is unchanged; its docstring
now also documents native MOCK pixel buffers. **4 focused QR checks PASS**,
including rejection of blank and obscured images: [transcript](qr-focused-tests.txt).
The MOCK encoder, ledger, quote and checkout behavior are unchanged. A fresh
full regression was run after this test-only fix; the final-source gate follows.

The [Submit form](windows-checklist.html) passes Chromium/Playwright checks at
800×1280 and 452×900: fresh storage despite old form data, persistence, unchecked
items preserved, explicit 20-cycle gate, Submit/export/reset and no horizontal
overflow/page errors. [Browser result](form-verification.json),
[452×900 screenshot](form-452x900.png).

Header-only rollback checkpoint: **848a52d** preserves the corrected centered
game world. Preserve consumed DEMO/MOCK records and P3 photo/print journals.
Do not revert or delete data to replay a code/order.

## Final visual approach correction

Final neutral screenshots exposed a taller compact-advert header starting with
Meong already over the lettering. That could also miss the first contact gate.
The art's uniform scale now additionally fits the actual left/right approach
space, leaving eight logical pixels before the text at each edge. This preserves
sprite proportions and lets the first/return collisions occur after movement.
A native edge-separation check covers 78/90/104-pixel headers and the real-clock
contact test uses the taller compact-advert geometry. Updated focused suite:
**28 PASS, zero skips**. No weakened collision or layout assertions.

The full run after the QR-only correction passed 540/540, but preceded this
additional visual fix: [historical transcript](before-approach-full-tests.txt).
The final-source full gate is rerun below; do not use that earlier run for it.

Twelve final native page captures are hash/dimension verified; static brand pose
is explicitly neutral/frozen. Visually reviewed advert/tutorial/gallery at both
required sizes: [800×1280 gallery](gallery-800x1280.png),
[452×900 gallery](gallery-452x900.png), [800×1280 advert](advert-800x1280.png),
[452×900 advert](advert-452x900.png). [Reports](final-screen-reports.json).

## Final local gate and Windows retest

**540 tests PASS, 0 failures/errors/skips in 163.945 s** at the final functional
file hashes: [transcript](final-full-tests.txt), [source hashes](tested-source.json).
Command: source /workspace/.photobooth-cloud/activate.sh; enable
PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1;
set PHOTOBOOTH_PALM_TEST_ASSETS=/workspace/.photobooth-cloud/palm-test-assets;
run python tools/run_kiosk_unittests.py. Native Linux/software GL, dummy PCM,
synthetic camera/print/checkout; not physical Windows acceptance. Syntax and
whitespace checks pass. Both the failed QR gate and superseded pre-approach
successful gate remain archived rather than relabelled as final-source PASS.

The final header source is ready for normal commit/push; CI will bind to that
functional SHA. The companion evidence commit can update its SHA/CI results
without changing tested runtime files or triggering another GUI workflow.

Remaining: Windows perception of the game position/pace and header animation,
touch/speakers/frame pacing and explicit twenty-cycle P4 retest. No known failing
local check remains. BUG-016 and BUG-015 are not physically closed by synthetic
QA. P3 owner acceptance is preserved; production payment/scanner stay disabled.

On Windows, keep branch feature/portrait-kiosk-v2-next and the existing venv:
run git pull --ff-only, then python tools/run_portrait_v2.py. Open
[the fresh Submit form](windows-checklist.html), record tested HEAD and check
only completed tests. Close/reopen the GUI to load the updated header.
