# Meong Fly latest-source reuse correction

> **Dated source/QA record, retained for traceability.** Results, “latest/current”,
> OPEN/PENDING labels, next actions and authorization limits below apply to this
> package's recorded source and report date. Later owner reports and source work
> can supersede its status; they do not rewrite these test results. Use
> [current status](../../FEATURE_STATUS.md), [test ledger](../../test_checklist.md)
> and [current handover](../../DEVELOPMENT_HANDOVER.md) for continuation. Historical
> checklists are not an instruction to repeat already accepted tests.

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


## Persistent owner rule and CI cost

`fd09c73` records the owner instruction in root [AGENTS.md](../../../AGENTS.md)
and [development protocol](../../DEVELOPMENT_PROTOCOL.md): inspect/reuse working
latest branch features before writing new code; direct imports and narrow
adapters, not an independently recreated GUI. Push logical stages and report
actual evidence. Documentation-only portrait pushes now skip CI, PR/manual
validation remains, and superseded same-ref runs cancel through concurrency.
YAML/trigger examples were checked locally. The policy-only commit explicitly
skipped CI; no application files were included in it.

## Stage 2 — actual original renderer connected

- `kiosk_v2/game_engine.py` is now only compatibility imports: its MeongFly/Pipe
  are the **same class objects** as `photobooth/meong_fly.py`, not another copy.
- `KioskGameStage` derives directly from the unchanged **MeongFlyStage**;
  `_refresh`, `_draw_game`, score drawing, camera/film composition, print
  lifecycle and pose/slot calculations are the **original method objects**.
- `KioskGameFlow` derives from the original **MeongFlyFlow**. The original tick
  is the only physics/score/terminal implementation. A small ledger bridge
  checks the v2 claim acknowledged on a worker before allowing original start,
  and queues result persistence; pending persistence blocks the result CTA.
- Original start/receipt/game/win/loss art, authored camera poses, rainbow,
  parallax, film idle/feed/hold/fall, score particles and 220ms impact are used.
  Keep the stage across game-page transitions so those effects are not reset;
  dispose it, its clock and mouse listener when leaving the game visit.
- Remove the custom game painter and redundant pre-rendered asteroid PNGs.
  There is no second v2 game clock, placeholder tutorial/layout handoff or new
  recreation of the camera/film art. All 26 original reference hashes still match.

Necessary host differences are explicit: extra kiosk exit footer, scaled touch /
hover mapping, shared button SFX and established page-owned BGM, pause/minimize
and retired-input guards, async isolated v2 receipt storage, native v2 tutorial
and actual 12-template gallery. The standalone App, home receipt DB and tutorial
marker are never used. Scanner remains None; no extra camera is opened. Existing
P3 camera/photo/print/Drive and P4b MOCK are unchanged. A validated code starts
immediately, and the original **II** HUD control pauses/resumes, as in the reference.

### Tests and visual evidence

**512 full tests PASS**, zero failures/errors/skips, including native Kivy,
dummy audio/video and public native palm fixtures. [Full transcript](stage2-full-tests.txt).
The earlier targeted run had 43 PASS, zero skips:
[focused transcript](stage2-focused-tests.txt). Those original widget assertions
that assumed the discarded custom buttons/brand widget were replaced by real
reference-stage, input, art and canvas-CTA checks; receipt/lifecycle guards stay.

New integration assertions verify original method/class identity, exact file
hashes, real transformed touches at three sizes, one cue per action, one physics
clock, no standalone/scanner/home-ledger entry, and invalid-code recovery. A
native **14-frame FBO comparison is pixel-identical** to an independent original
MeongFlyStage: Start idle/feed/hold/fall plus Game/Win/Lose, each at 800×1280 and
452×900. [Pixel hashes and cases](native-pixel-parity.json). These compare the
actual game stage at matching fixture state, not the kiosk footer or Windows
hardware behavior. Reference modules/tests remain byte-identical.

**30 actual full-window captures reviewed**, fifteen at each required size:
[800×1280 contact](contact-800x1280.jpg), [452×900 contact](contact-452x900.jpg),
[800 manifest](render-800x1280.json), [452 manifest](render-452x900.json).
They include all four print stages and final loss **after** the original impact
transition. No stale invalid-code warning remains after a valid claim. Game
states are injected, paper clocks controlled for deterministic capture; these
are not human gameplay/FPS or Windows audibility certification. Precommit base
SHA/dirty state are recorded truthfully; matching-source CI follows the push.

The existing [28-item Submit form](../portrait-v2-p4/windows-checklist.html) uses
the original MAIN GAME / VALIDASI DEMO 1X / II / PILIH LAYOUT FOTO labels and a
fresh storage key. Chromium/Playwright at both sizes rechecked Submit, download,
reload, unchecked preservation, twenty-cycle gate, reset and overflow:
[browser report](form-verification.json). P3 owner acceptance is unchanged.

### Checkpoints and remaining device gate

- `89644af`: previous custom P4 view, before this correction.
- `c943446`: unchanged latest reference modules/assets/tests, 98 original PASS.
- `fd09c73`: persistent reuse rule and CI-budget policy (no app changes).
- Stage 2: actual original game UI with narrow v2 host; source SHA in git/CI.

Rollback host integration to `fd09c73` if necessary; preserve
`data/kiosk-v2-p4/demo-attempts.sqlite3` and consumed attempts/orders. Do not erase
it to grant replays. No branch switch/merge/master modification is involved.

Run the existing launcher after pulling the required v2 branch. In the game:
MAIN GAME → new DEMO code → VALIDASI DEMO 1X → original gameplay; II pauses,
AKHIRI GAME exits without another attempt, both result CTAs use the v2 tutorial
and original template gallery. Physical Windows animation/feel/input acceptance
is still needed; provider Sandbox/merchant and production gates remain outside
this correction. Scanner, real payment and actual discounts stay disabled.


## Stage 3 — matching-source CI evidence (documentation only)

Functional correction source **`d267d8908f737d9610c9a67dc4c4dd2d6baa486f`**:
[Actions 40043552747](https://github.com/pratikto/PhotoBooth/actions/runs/40043552747)
**all three jobs SUCCESS**: pure rules/reference hashes, native Linux Kivy /
original game suite, and Windows Python 3.12 SDL dummy audio. The workflow
includes the new reference integration/pixel tests and all original game tests.
[Verification JSON](ci-verification.json).

Downloaded original artifact `12540397094` (7,086,615 bytes); its SHA-256 matches
GitHub's digest `da2f8f5ffd7a20903ccae41fda8a99bd71be6c292013425b1b0c5277a0360112`.
Four fresh reports identify the same commit with **tracked_changes=false**;
all 50 P4 PNG hashes/dimensions verified (30 game plus 20 unchanged MOCK views).
The 30 game captures were visually reviewed in both
[800×1280 CI contact](ci-contact-800x1280.jpg) and
[452×900 CI contact](ci-contact-452x900.jpg).

This evidence commit changes documentation/images only. The new docs-only path
filter prevents another full portrait CI run; no functional checks are waived.
The application remains byte-identical to tested `d267d89`. Native fixtures and
Windows dummy sound are not a claim of physical Windows gameplay/audibility.
