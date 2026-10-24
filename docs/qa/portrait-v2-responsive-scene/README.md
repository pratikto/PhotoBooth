# Responsive Meong Fly and compact gallery — 2026-10-24

> Subsequent owner report: BUG-015 exposed a temporal regression missed by this static QA. The piecewise approach projection is superseded by uniform motion in 144bd60. Header/gallery follow-up is tracked in [current correction QA](../portrait-v2-motion-correction/README.md); retain the earlier PASS below as historical evidence, not acceptance of wave speed.

Owner requests a unified game scene, real component resizing instead of separate
side filler, simpler price information and removal of the CETAK caption.
Required branch: feature/portrait-kiosk-v2-next. Starting rollback: 87a13b9.
Read-only game reference remains 672e3f7089bb40940e5b41644ceb656aa63aafbb.

## Stage 1: compact gallery

Keep the three strip previews and floating navigation. Replace the dense price
formula and repeated offer sentence with − / selected quantity / +, prominent
TOTAL SIMULASI and two short details: total sheets/sessions and savings when
applicable. Remove CETAK. Quote math, consumed discount and disabled production
payment behavior are unchanged. The card remains 98 logical pixels even with
a discount, returning space to the strip preview.

Local native checks: **20 PASS**, zero skips; see stage1-gallery-tests.txt.
Includes resize bounds at 800×1280, 452×900, 360×640, 452×600 and 800×600,
intact 1:3 strips, visible price labels, MOCK quote consistency and twenty
simulated MOCK visits. An initial test invocation used the wrong class name;
a concurrent render then caused a timed-out test worker. Correct invocation
run alone passed. These are cloud checks, not Windows hardware acceptance.

Stage 2 will replace the rejected separate filler with responsive original-art
composition. Do not treat the earlier filler QA as acceptance of this request.

Reviewed native capture: [winning gallery at 452×900](stage1-gallery-452x900.png),
with Rp7.500 net total and Hemat Rp2.500. Preview strips remain the visual focus.

## Stage 2: responsive original-art scene

The owner rejected the earlier `4896d51` separate Starfield filler. Its bounds
check is historical, not proof of responsive component layout. The adapter now
uses one continuous, cover-cropped original sky over the entire game stage.
Original card/button pixels are grouped and reflowed across available width;
plain panel material expands while central pixel glyphs and edge caps keep
their aspect. Scan input, hover borders and action hitboxes use the same layout.
Vertical extra space is distributed by panel anchors, including scanner effects
and paper positions, rather than resetting the visit on resize.

`game_layout.py` is a compatibility exception required because the original
standalone painter bakes its static controls into one fixed 360×720 poster.
It extracts those exact painter pixels once and caches GPU instructions. No
new glyphs, sprites, game engine, music owner or camera/print animation are
implemented. The original `_draw_game`, `_paint_camera`, `_paint_print_sheets`,
`_advance_printer`, camera/slot contexts and score renderer remain the identical
method objects. All 26 pinned reference files stay byte-identical to `672e3f7`.

The playfield extends horizontally using a cosmetic approach projection. The
collision-near corridor translates camera and obstacles equally; original
sprite sizes, gap height, speed, score and collision physics remain unchanged.
Distant approach positions use the extra width. This is intentionally a layout
extension, not a claim that responsive whole-screen pixels equal the original
fixed poster. Film quads retain original texture/UVs, angle, timing, slot and
depth while their coordinates follow the same projection as the camera.

Native checks cover original layer pixels/emitter poses/film corners across
21 scene/phase fixtures (three sizes), no texture upload on live resize, text
retention, frozen score/game clock during paused resize, full-width controls,
real taps outside the former portrait column, one coherent opaque sky, pointer
cleanup, lifecycle and ledger/discount guards. The screenshot recorder now
waits for the loss result to be drawn after the original impact animation;
its first gameplay capture is an active round, with a separate paused capture.

New [14-item checkbox form with Submit](windows-checklist.html) reuses the
existing local form implementation with fresh storage. Blank items stay blank;
20-cycle items never pass automatically. Chromium checks at 800×1280 and
452×900 exercise storage, Submit, download, reset and the cycle gate. It does
not send messages or connect to a payment service.

### Checkpoints and remaining acceptance

- `87a13b9`: pre-request rollback, retains the rejected fixed center/filler.
- `60ab3cf`: compact gallery stage, 20 local PASS and matching-source portrait
  CI [40055059756](https://github.com/pratikto/PhotoBooth/actions/runs/40055059756)
  SUCCESS. Roll back the responsive game to this code checkpoint if needed;
  preserve consumed DEMO attempts, orders, photo journals and local data.
- Windows 10.1-inch physical touch, frame pacing and speaker checks remain
  pending for this responsive change. Prior P3 owner acceptance remains valid.
  No production payment, discount, scanner, reference-branch write or merge.

### Final local evidence

- **529 tests PASS, 0 failures/errors/skips, 221.469 s**:
  [complete transcript](final-full-tests.txt). Command: activate the cloud venv,
  set PHOTOBOOTH_TEST_GUI=1, PHOTOBOOTH_TEST_AUDIO=1,
  PHOTOBOOTH_TEST_VIDEO=1 and PHOTOBOOTH_PALM_TEST_ASSETS to the installed public
  fixture directory, then run `python tools/run_kiosk_unittests.py`.
  [Tested file hashes](test-source.json) bind this working-tree run to source.
- Earlier [23 focused native PASS](stage2-focused-tests.txt), original source
  hashes and dynamic method identity retained. The full final run includes the
  corrected collision-corridor exit boundary. An earlier broad run was stopped
  after that boundary refinement; it is not counted as a completed PASS.
- **80 actual Kivy PNGs** rendered; dimensions and SHA-256 values verified in
  [reports](screenshot-reports.json). These are synthetic isolated DEMO/MOCK
  fixtures, with no production devices or transaction. Review sheets cover
  intro, input, active game, pause, win, loss and native gallery at
  [800×1280](800x1280-contact.jpg), [452×900](452x900-contact.jpg),
  [800×900](800x900-contact.jpg), [360×640](360x640-contact.jpg).
  Selected full-size evidence: [wide intro](intro-wide-800x900.png),
  [wide active game](game-wide-800x900.png), [800×1280 game](game-800x1280.png),
  [452×900 game](game-452x900.png), [loss](result-452x900.png),
  [800×1280 net-price gallery](gallery-800x1280.png),
  [452×900 net-price gallery](gallery-452x900.png),
  [short window](short-360x640.png). Raw captures remain in the cloud QA folder;
  representative captures and all reports are committed.
- [Browser verification](form-verification.json): 14 checkboxes initially
  empty, storage/reload, Submit, download, reset, 20-cycle gate and no horizontal
  overflow at both required sizes; no page errors.
- Syntax and `git diff --check` pass. No unresolved local test failure. Windows
  resize aesthetics/touch/frame pacing and speaker acceptance remain untested
  for this change; use the new form rather than assuming those items passed.

### Matching-source GitHub verification and final checkpoint

Functional source **5c81ea11a34102496bf5c7523e74a0bf94556c7a** is pushed and its
remote HEAD was verified. The final tested file hashes match that committed
source. [Portrait CI 40056129151](https://github.com/pratikto/PhotoBooth/actions/runs/40056129151)
completed with **all three jobs SUCCESS**: navigation/audio lifecycle, Linux
native GUI/source regression/screenshots, and Windows Python 3.12 native SDL
PCM cycles (dummy output). [Archived job result](final-ci.json).

Downloaded its original screenshot artifact, checked all 50 P4/MOCK PNG hashes
and dimensions against reports carrying the exact source SHA and clean tracked
source, and reviewed [representative CI captures](ci-contact.jpg).
[Verification manifest](ci-screenshot-verification.json). These checks do not
certify physical Windows speaker/touch/performance.

Code checkpoints: `60ab3cf` compact gallery → `5c81ea1` responsive game. Roll back
runtime code to `60ab3cf` if the new layout needs correction, preserving the P4
consumed-attempt/order ledger and P3 photo/print journals. The next commit only
archives CI/QA evidence; it does not change tested runtime or trigger another
GUI workflow. No local test failure remains; await owner Windows acceptance.

After pulling the same branch, run `python tools/run_portrait_v2.py` in the
existing Windows venv. Open `docs/qa/portrait-v2-responsive-scene/windows-checklist.html`
in a browser, fill the actual HEAD/device fields and submit only tested items.
