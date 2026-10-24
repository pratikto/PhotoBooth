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

Stage 1 source ready for commit/push. Next: the separately requested aligned
mascot/text and impact-spin animation, final full regression, then Windows retest.

