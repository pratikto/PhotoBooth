# BUG-015 — resize-induced asteroid motion regression

Owner reports: game suddenly feels faster, and wave spacing changes from wide
to narrow. Starting source 72fafcd / runtime 5c81ea1 on the mandatory branch
feature/portrait-kiosk-v2-next. The later owner corrections also request centered
quantity/price controls, centered MEONG PHOTOBOOTH, a flying mascot, and the
PILIH TEMPLATE STRIP title as an overlay inside the gallery. Deliver motion first,
then those visual changes in a separately tested/pushed stage.

The 5c81ea1 adapter used a piecewise horizontal projection. Far-right objects
had a larger position scale than nearby objects, while sprite sizes remained
constant. The unchanged physics engine therefore did not protect displayed
speed or wave spacing. Source reproduction is recorded in before-motion.json:
at 800×900, far movement is 2.437× nearby movement; at 800×1280 it is 1.462×.
Prior static screenshots/collision-local checks did not detect this temporal
regression. Their PASS must not be treated as owner acceptance or proof of
constant speed.

Scope: remove position-dependent projection; use one uniform source-world
scale and translation for the entire flight path, including film, trails and
asteroids. Keep a continuous full-window sky and responsive HUD/menu controls.
Do not tune original speed/spawn/difficulty constants or invent another engine.
Reference 672e3f7089bb40940e5b41644ceb656aa63aafbb remains read-only and its
26 original modules/assets/tests must keep matching hashes. Retain ledger,
MOCK, audio, photo and input guards. Production payment/scanner stay disabled.

Tests planned: displayed velocity from actual rendered rectangles across the
whole approach; equal wave distances before/after the old breakpoints; camera,
film and collision geometry agree; differential engine stepping versus original;
resize/pause/state/source guards; native screenshots at 800×1280 and 452×900,
plus wide/short checks. One final full regression after both authorized stages.

Rollback baseline for this task: 72fafcd; it includes this known motion defect.
For pre-regression game layout use 60ab3cf; preserve consumed attempts/orders and
P3 print/photo journals. Never roll back or delete ledgers to obtain more plays.

## Stage 1 result

One translation now applies throughout the original world. The spawn edge is
right-aligned so waves enter the window edge without stretching their approach.
Camera/asteroids/paper keep their source scale; HUD/menu reflow and the full-stage
sky are retained. [After measurements](after-motion.json) show a constant 1.0
position slope and 198-source-unit spacing for 1.6-second waves at every size.

**25 focused native tests PASS, zero skips**: [transcript](stage1-tests.txt).
New coverage measures actual asteroid Rectangle positions as two waves traverse
the former breakpoints, and compares original engine state on every step while
resizing. The first test run had a test-harness Rectangle.x access error; using
its actual pos[0] corrected that harness issue and the final run passed. All
26 reference files and original dynamic draw methods still match.

Thirty native P4 captures had dimensions/hashes checked; active-game layout
reviewed at [800×1280](stage1-game-800x1280.png) and
[452×900](stage1-game-452x900.png). Capture waves are injected samples, not
measurement of live spawn timing; the temporal tests supply that evidence.
Windows physical pace acceptance remains pending. Next is the separately
requested centered/flying brand and gallery arrangement, then final regression.

## Stage 2: centered brand, flying mascot and gallery alignment

Gallery header is now full width: MEONG PHOTOBOOTH remains on the window
centerline. The original transparent 224×152 reference PNG flies left→right
and back above the text, with a small bob. Native Kivy Animation moves the
existing Image and mirrors only its draw transform on return; no replacement
artwork, new game engine or per-frame image decoding is introduced. Travel
recalculates remaining duration after resize. Pause/resume retains its phase;
page retirement and application close cancel the animation. Mini-game original
poster/HUD artwork is unchanged.

PILIH TEMPLATE STRIP floats inside the gallery above the previews. A 26-pixel
inner title lane keeps the selected strip unobscured. The three original strips
and floating navigation remain. Quantity/context and total/savings now each
belong to one of two equal centered columns, with matching vertical padding.
CETAK stays removed. The compact price card is 90 logical pixels high.

**14 focused native checks PASS, zero skips**: [transcript](stage2-focused-tests.txt).
Includes centered native window coordinates at five sizes, title/strip separation,
real Clock movement on advert/tutorial/gallery, pause/resume, five repeated visits,
retirement/close, both flight edges and immutable texture, plus wave/quote guards.
The first edge check found a one-pixel bob overlap with the title bounds; the
mascot lane was adjusted and final checks pass.

A separate native-clock observation measured **66.04 pixels/s** against the
65-pixel/s decorative target, with the wordmark fixed at the center:
[clock samples](real-clock-header-motion.json). The
[phase preview GIF](header-phase-preview.gif) uses synthetic native-rendered
positions to show the whole path; its playback speed is not a real-time timing
measurement. [Midpoint header](header-midpoint.png).

Reviewed native [800×1280 gallery](gallery-800x1280.png),
[452×900 gallery](gallery-452x900.png), [800×1280 advert](advert-800x1280.png)
and [452×900 advert](advert-452x900.png).
[Capture reports](stage2-screen-reports.json) retain injected MOCK/synthetic flags.
The P4 screenshot fixture now uses the real engine's speed × 1.6 seconds for
sample wave spacing, replacing its previously arbitrary close pair.

Reuse the [14-item form with Submit](windows-checklist.html), fresh storage,
unchecked-item preservation and explicit 20-cycle gate. Browser checks at both
required sizes passed: [verification](form-verification.json).

Motion source checkpoint: **144bd60**, normal push and remote HEAD verified;
[matching-source CI 40057871792](https://github.com/pratikto/PhotoBooth/actions/runs/40057871792)
is SUCCESS. Roll back the visual stage to this runtime checkpoint if needed,
preserving the motion correction and all consumed ledgers/photo journals.
Final full regression and the visual source checkpoint follow below.

## Final local gate

**533 tests PASS, 0 failures/errors/skips in 208.824 s**:
[full transcript](final-full-tests.txt). Run after the final functional changes:
activate `/workspace/.photobooth-cloud/activate.sh`; set PHOTOBOOTH_TEST_GUI=1,
PHOTOBOOTH_TEST_AUDIO=1, PHOTOBOOTH_TEST_VIDEO=1 and
PHOTOBOOTH_PALM_TEST_ASSETS=/workspace/.photobooth-cloud/palm-test-assets;
run `python tools/run_kiosk_unittests.py`. Native Linux/software GL, muted PCM,
synthetic camera/print/checkout and installed public palm fixtures, not Windows
hardware acceptance. [Tested file hashes](final-tested-source.json).

**77 final native PNGs** have validated dimensions and hashes:
[reports](final-screen-reports.json). Review sheets show actual native advert,
tutorial, empty/filled gallery, normal-spaced game, win and loss at
[800×1280](final-contact-800x1280.jpg) and
[452×900](final-contact-452x900.jpg). Full game captures:
[800×1280](game-800x1280.png), [452×900](game-452x900.png),
[wide 800×900](game-800x900.png). Screenshots are layout evidence; the added
rendered-motion tests and original-engine differential run provide speed/spawn
evidence. Syntax and whitespace checks pass. No local failing check remains.

Windows retest remains open for actual perceived pace, touch, animation/frame
pacing and speakers. Do not reuse old checkmarks. Default payment/scanner remain
disabled; no production discount, receipt, transaction, merge or deployment.
