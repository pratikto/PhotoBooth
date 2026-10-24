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
