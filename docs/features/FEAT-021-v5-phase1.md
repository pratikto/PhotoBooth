# FEAT-021 / BUG-013 — Visual v5 Phase 1

## Authorization and baseline

Owner approved the reviewed Phase 1 scope on 2026-10-21: **"yes aku stuju scope nya"**. Scope includes implementation, regression tests, documentation, small commits and staged pushes on existing `feature/meong-flappy-challenge`. Baseline: `3368e123ef709bf1ee9f110e505bc0619d3833f4`. No new branch, master merge, production integration, receipt/physics changes, real payment or print. Approval does not accept the finished aesthetics or authorize phases 2–5.

## Delivered architecture

- `meong_fly_sprite.py` is the shared sprite/geometry source. Bundled 224×152 owner artwork is unchanged. The local print outlet is `(108,124)` with a 40-pixel opening; a small generated housing/foreground lip and rear shadow define the aperture. Metadata is transformed through gameplay crop `(64,32,224,144)`, aspect-preserving fit, ±5-degree tilt and viewport scaling. Hero hover moves the entire pose.
- `meong_fly_visual_v3.paint_poster_screen` paints backgrounds only; Start/Win/Lose no longer bake a competing hero. Old animation helpers remain for compatibility/history but are not the live v5 renderer.
- `MeongFlyStage._paint_camera` owns the rear → film → foreground composition for hero and gameplay. No independent second hero renderer. Original logo/GIF bytes are not modified. **External `MEONG_FLY_ANIM_GIF` overrides do not drive this compositor** because arbitrary GIF crops do not have validated slot metadata. Supporting another artwork requires authored metadata, not guessed anchors or silently falling back to old art.
- Film uses cached full textures and changing UV coordinates: its leading bottom edge emerges first, already-exposed image pixels move down, and the paper is not stretched. The body/lip occludes the root. Rotation is around the same slot as the camera.
- `InstantPhotoEmitter`: 0.62 s initial delay, 0.60 s feed, 0.18 s full-sheet hold, then release at the previous attached pose with a new release clock. First detached frame has zero gravity displacement, then falls independently; bounded translation and angular sway. Maximum two simultaneous sheets, one simultaneous on Win; repeat interval 2.15 s. These are animation parameters, not real printer timing.
- Immediate scene cleanup occurs before redraw. Start/Game/Win print; Scan/Lose/Tutorial/Layout do not. Pause freezes both feed and detached motion. Full rotated bounds determine removal before the safe floor.
- Gameplay artwork is fitted inside the same collision rectangle. No engine hitboxes or obstacles changed. Slot-safe film width is narrower than its aperture, including the small game sprite.

## Files and deliberate boundaries

Runtime: `photobooth/meong_fly_sprite.py` (new), `meong_fly_gui.py`, `meong_fly_visual_v3.py`, `meong_fly_print_fx.py`. Existing `meong_fly_game_art.py` geometry/background remain in use; the new shared sprite provider replaces its old pose preparation in the live GUI. `meong_fly_painter.py` needs no interface change. `meong_fly_flow.py`, engine, receipt ledger and production modules unchanged.

Tests: `tests/test_meong_fly_v5.py` (13 new checks), `tests/test_meong_fly_print_fx.py` (existing release duration and non-vacuous pause coverage). Evidence tool: `tools/render_meong_fly_phase1.py` produces deterministic Kivy FBO fixtures with temporary ledger, dimensions, pose data, source SHA and dirty status; never changes the user's tutorial marker.

## Acceptance and outstanding risks

Automatic gates: single hero front texture per result/start scene; no hero loader in background painter; actual authored aperture alpha/rear/lip; crop/tilt metadata; aspect ratio; four-stage lifecycle with a full attached hold; exact release continuity; pause with actual attached/detached sheets; scene cleanup; rotated safe floor; Win cap; no texture upload during warmed print animation; UV orientation/depth ordering; shared viewport transform at 450×900, 800×600 and 1200×800. Full existing Meong Fly suite remains required.

Manual Windows gates **PENDING**: compare moving slot alignment (candidate tolerance ≤1 logical pixel), no ghost/teleport, four-stage video, keyboard/paste/caret, portrait/landscape input, actual gameplay/hitbox feel, ≥30 measured FPS candidate on target device, owner visual approval. Linux Kivy FBO captures are renderer evidence only. The source artwork remains low-resolution; typography, background/asteroid overhaul and defeated/X-eye art are later phases. Phase 1 cannot close all BUG-013 findings or claim complete poster fidelity.

## Validation and rollback

Pre-change HEAD baseline on Linux Python 3.12.14: 78 total / 67 PASS / 11 Kivy SKIP / 0 FAIL/ERROR. Kivy 2.3.1 was then installed successfully; SDL2 and Mesa llvmpipe OpenGL 4.5 available. Working-tree Phase 1 suite: 91 PASS / 0 FAIL/ERROR/SKIP. Exact committed source retest and captures are recorded in the companion QA record.

Commands:

```sh
KIVY_NO_ARGS=1 python -m unittest discover -s tests -p 'test_meong_fly*.py' -v
KIVY_NO_ARGS=1 python -m tools.render_meong_fly_phase1 --output /tmp/meong-phase1
```

Rollback: scoped `git revert` of Phase 1 runtime/test commit on the same feature branch; preserve ledger files and all other work. Do not reset, force-push, modify master or rewrite history. Baseline above is the known pre-Phase-1 revision. Documentation/evidence companion commits describe the tested runtime revision and can be reverted separately if required.
