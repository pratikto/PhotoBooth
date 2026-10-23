# Meong Fly latest-source reuse correction

Date: 2026-10-24 Asia/Jakarta. Owner explicitly rejects the custom P4 game view
and requests the latest existing game code from the Meong Fly branch.

## Diagnosis and binding source

The prior integration reused only the pure physics engine. Its hand-built
`kiosk_v2/game_scene.py` and game views omitted the existing v5 compositor,
authored camera poses/print slot, film feed/hold/fall, parallax/rainbow and score /
impact effects. That was not visual reuse of the latest game.

Remote reference verified read-only: `feature/meong-flappy-challenge`,
**`672e3f7089bb40940e5b41644ceb656aa63aafbb`**. Preserve that branch, master and
all histories; no merge or new branch. Target remains
`feature/portrait-kiosk-v2-next`. Pre-correction rollback: `89644af`.

## Stage 1 — original modules and original tests

Copy the latest reference modules/assets and original tests **byte-for-byte**
into their original package locations; [26-file hash manifest](upstream-reference.json).
Do not launch its standalone App or scanner, instantiate its home ledger, write
its tutorial marker, or use its generic layout preview in the v2 flow.

**98 original tests PASS**, zero failures/errors/skips:
[transcript](stage1-upstream-tests.txt). This stage adds the reusable originals
and CI coverage; the active v2 game view has not been switched yet. Stage 2
will mount the actual existing MeongFlyStage/MeongFlyFlow with a narrow v2
navigation/lifecycle/I/O adapter. Do not recreate the renderer a second time.

Preserve v2's consumed DEMO ledger and asynchronous storage, tutorial-once,
12 original templates, photo/checkout and established audio ownership.
Scanner, real payment and actual discounts remain off. Each stage is tested,
committed, pushed normally and remote HEAD verified before continuing.
