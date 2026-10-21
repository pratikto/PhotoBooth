# FEAT-021 — Visual v5 Acceptance & Regression Matrix

> **2026-10-21 — Scan camera update:** Scan QA amendment: Q18 now checks local DEMO QR decode into editable input, explicit Validate, mirrored display with unmirrored decoder, invalid/used QR handling and camera release. Existing camera-free Q18 wording is historical. Linux 98 PASS; Windows physical acceptance remains NOT RUN. [Scope](../features/FEAT-021-scan-camera.md) · [Evidence](FEAT-021-scan-camera/README.md).

> **2026-10-21 — Visual v5 Phase 1 update:** Phase 1 now has [Linux automated and Kivy FBO evidence](FEAT-021-v5-phase1/README.md): 91 PASS, 0 FAIL/ERROR/SKIP. The NOT RUN entries below continue to mean **Windows/manual v5 acceptance**, not absence of Linux tests. All-phase V01–V16 owner aesthetic gates remain pending; no Windows PASS claimed.

**Prepared 2026-10-21 · STATUS: TEST PLAN ONLY (NOT EXECUTED) · Branch: `feature/meong-flappy-challenge`.**  
Current visual/audit requirements: [FEAT-021 Visual Overhaul v5](../features/FEAT-021-visual-overhaul-v5.md).  
Source **audit baseline** before documentation work: `85a6aaa99356f3825067dfc5b92c6f91933d8519`. Record a **new exact SHA** before any eventual code test or v5 implementation.

> **Evidence rule:** PASS requires actual test execution and traceable logs/screenshots. “Not run” is NOT PASS. A Kivy unit test is NOT owner approval of the rendered scene. “Owner accepts poster fidelity” requires the **current live Windows application**, not a concept image. No production GUI, real printed-paper acceptance or real QRIS claims.

## A. Test history — truth preserved by version

| Recorded evidence | Status, date & environment | Confidence / boundary |
| --- | --- | --- |
| Step 3 standalone GUI manual QA | Owner-reported **6/6 PASS** on Windows, 2026-10-21 | Valid **only** for older Step 3 code; display dimensions and exact SHA not captured |
| Step 3 unit retest | Owner-reported **10/10 PASS** on Windows Python 3.12 | Older engine/receipt tests only |
| Batch A/B automated suite | Owner-pasted **55/55 PASS, 0 failures, 0 skips**, 6.272 s; Python 3.12.10, Kivy 2.3.1, Intel Iris Xe/OpenGL 4.6 | Historical checkout (exact SHA not supplied); no live visual FPS/sign-off |
| Handoff/flow/painter partial retest | Owner-pasted **23/23 PASS**, 1.789 s, 2026-10-21 | Exactly 3 test modules; did not include complete v3/v4/Kivy art |
| Print v4 emitter local-mirror run | Assistant-reported pure Python **10/10 PASS** and compileall | Does not establish passing tests at exact feature branch HEAD or actual Kivy print-mouth alignment |
| **Current v4 physical view** | **NOT VERIFIED** at exact GitHub SHA | No complete Windows after-v4 log, side-by-side video, owner acceptance, measured FPS |
| **Visual Overhaul v5** | **NOT IMPLEMENTED / NOT RUN** | This file defines future gates only; no invented PASS counts |

Historical evidence is not erased; it is **not promoted** to the newer build. Related historical logs: [FEAT-021 engineering log](../features/FEAT-021-meong-fly.md), [global test checklist](../test_checklist.md).

## B. Verification environment and commands

**Branch safety:** do not switch to `master`, create a new feature branch, merge, or reset unrelated work for visual testing. If `git status` shows local edits, preserve them and resolve safely before switching/pulling.

Run in PowerShell at the PhotoBooth repository root:

```powershell
git status --short
git switch feature/meong-flappy-challenge
git fetch origin
git pull --ff-only origin feature/meong-flappy-challenge
git rev-parse HEAD
.\.venv-kivy\Scripts\Activate.ps1
python --version
python -m pip show kivy pillow
python -m unittest discover -s tests -p "test_meong_fly*.py" -v
python -m photobooth.meong_fly_demo
```

If the exact `.venv-kivy` location differs, activate the actual installed project venv; do not silently claim a command was run if it was not. Running this complete suite **after v5 code is implemented** is required for any future acceptance. Current v4 owner retest is also needed.

**Suggested focused tests (already in current branch):** `tests.test_meong_fly` (physics); `tests.test_meong_fly_receipts` (one-use persistence); `tests.test_meong_fly_flow` (terminal/tutorial/layout); `tests.test_meong_fly_painter`, `tests.test_meong_fly_polish`, `tests.test_meong_fly_game_art`, `tests.test_meong_fly_visual_v3` (art); `tests.test_meong_fly_gui`, `tests.test_meong_fly_gameplay_gui` (Kivy); `tests.test_meong_fly_print_fx` (film lifecycle); `tests.test_meong_fly_photo_handoff` (12 demo card hitboxes). **Their existence is not evidence of execution at this SHA.**

## C. Visual capture protocol

The owner reference is a **five-panel poster** and a **four-stage camera printing storyboard**, not an exact native 360×720 Kivy screenshot. Compare each actual screen to its corresponding *panel* and note justified differences for true responsive UX and owner-approved CTA wording.

1. Capture a real Windows Kivy screenshot for Start, Scan, Gameplay (score 0), Gameplay with asteroid at camera height, Win, Lose, Tutorial and the demo 12-layout page.
2. Record the actual tested SHA, device/OS/monitor size, window dimensions, scaling factor/DPI, screenshot name and date; distinguish a Pillow preview from a Kivy screenshot.
3. Use a **fresh, previously unused** `DEMO-...` code for every attempt (e.g. `DEMO-V5-QA-001`; never treat these as cafe receipts). The same code must be denied on relaunch.
4. Capture at least 4 sequential physical film-print moments: (i) camera hovering empty, (ii) partially emerging paper **still attached**, (iii) full sheet at printer outlet, (iv) detached sheet visibly falling. If necessary record at >=30 frames/s or step through video frame-by-frame.
5. Compare exact artwork details: gray Meong/camera white body, large blue lens, rainbow wave, correct print outlet, bold multicolor/outlined text, neon frames, rich but readable deep-space background and varied asteroid shapes.
6. For each screenshot annotate observed overlaps, clipped text, illegible microcopy, misaligned click target, masking/z-order errors, font aliasing, odd motion, missing objects and whether a feature is only illustrative.
7. Obtain **explicit owner visual acceptance**; neither assistant score nor “the code exists” can replace it.

**Standard form for a screenshot annotation:** `Screen | Window WxH | Commit SHA | Object | Expected from poster | Actual Kivy | PASS/FAIL/BLOCKED | Evidence path | Follow-up ID`.

## D. End-to-end behavioral gate (standalone only)

| QA ID | Case / action | Expected outcome | Current v5 result |
| --- | --- | --- | --- |
| Q01 | Launch the standalone entry point | No crash; Start visible; controls clickable | **NOT RUN** |
| Q02 | Start → MAIN GAME | Open Scan demo only; no receipt claimed at this step | **NOT RUN** |
| Q03 | Scan input click, type, paste, backspace, Enter | Real TextInput caret/text visible; redraw safe (BUG-012) | **NOT RUN** |
| Q04 | Scan → KEMBALI before claim | Return Start; that demo code remains unused | **NOT RUN** |
| Q05 | Validate invalid/missing/non-`DEMO-` code | Clear error; no game start or attempt claim | **NOT RUN** |
| Q06 | Validate unique `DEMO-...` | Atomic claim; enter live Gameplay exactly once | **NOT RUN** |
| Q07 | Restart and re-enter same code | Rejected even after loss/win/app relaunch | **NOT RUN** |
| Q08 | Tap/click Gameplay | Meong reacts; gameplay/graphics align with physics | **NOT RUN** |
| Q09 | Pause/resume Gameplay | Time/asteroids/printed film freeze then resume; no hidden input | **NOT RUN** |
| Q10 | Clear asteroid without touching hitbox | Score increments exactly once, visible `+1` | **NOT RUN** |
| Q11 | Ground/asteroid collision or timeout | Lose with actual score; brief collision feedback; no retry | **NOT RUN** |
| Q12 | Reach target 10 | Win with **demo-only** Rp2.500 and no retry | **NOT RUN** |
| Q13 | Win → PILIH LAYOUT FOTO | Tutorial if unseen, else demo layouts; **not payment** | **NOT RUN** |
| Q14 | Lose → PILIH LAYOUT FOTO | Same route; no discount; no retry | **NOT RUN** |
| Q15 | Start → LANGSUNG FOTO | Skip mini-game; tutorial if unseen, then demo layouts | **NOT RUN** |
| Q16 | Complete tutorial, relaunch | Standalone-only seen flag skips tutorial | **NOT RUN** |
| Q17 | Demo layout grid 1–12 | Twelve separate clickable cards; choosing closes standalone demo | **NOT RUN** |
| Q18 | Scan QR illustration | Decorative ONLY; never claim camera/POS scan succeeded | **NOT RUN** |
| Q19 | Postgame navigate/relaunch, inspect transaction UI | No production camera/print/QRIS/real discount touched | **NOT RUN** |
| Q20 | Keyboard/mouse/window resize | No clipped headings/buttons, broken touch mapping or text-field erasure | **NOT RUN** |

## E. Per-screen/object aesthetic gate (owner approval required)

| QA ID | Screen/object | Target evidence | Accept only when |
| --- | --- | --- | --- |
| V01 | Start hero | Screenshot + hovering frames | Latest camera-cat appears **once**, clean alpha, blue lens and rainbow identifiable |
| V02 | Start title | 450×900 and 800×600 captures | MEONG FLY! bold, multi-layer outlined and readable without black-on-navy legacy lettering |
| V03 | Start promo | Screenshot | Rp2.500 focal yet unmistakably **SIMULASI**, no crowded copy |
| V04 | Start CTA pair | Screenshot + taps | Pink/cyan buttons have equal material styling, icons and accurate hitboxes |
| V05 | Scan title/frame | Screenshot | Strong two-line header, neon scanner frame, readable caution |
| V06 | Scan input | Video of typing/focus | True caret, high contrast, error/disabled states and no overlap with scanner beam |
| V07 | Gameplay HUD | Score 0, midscore screenshots | Pause/Score/Target 10 immediately readable |
| V08 | Gameplay cat | Live capture screenshot | Camera-cat large enough to see expression, lens, rainbow, no trail-as-hitbox deception |
| V09 | Gameplay asteroids | Screenshot + test collision | Multiple varied rock silhouettes; visually communicated hitbox is fair |
| V10 | Gameplay depth | 10–15 s clip | Rich galaxy/planets without obscuring obstacles/camera |
| V11 | Win heading/hero | Screenshot | Celebratory gold SELAMAT!, expressive Meong and controlled flare |
| V12 | Win reward/CTA | Screenshot + tap | Correct demo Rp2.500; single PILIH LAYOUT FOTO |
| V13 | Lose character | Screenshot | Distinct cute defeated/X-eye expression while keeping Meong's identity |
| V14 | Lose score/CTA | Screenshot + tap | Correct N/10, no text overlap, no replay and only layout CTA |
| V15 | Tutorial/layouts | Screenshots | Legible one-time tutorial and **generic** 12 demo cards, not mislabeled thermal templates |
| V16 | Neon/typography consistency | Five actual Kivy captures | Shared panels/button/material, strong hierarchy, no tiny unreadable footnotes |

All V01–V16 are **PENDING** for v5. Source and old screenshots must not be described as a completed v5 visual pass.

## F. Camera instant-print animation — four-stage frame matrix

| QA ID | Expected camera relative pose | Failure signatures to check | Current v5 result |
| --- | --- | --- | --- |
| A01 — idle | Animated camera-cat floats normally, slot physically located under body | Redundant static shadow/duplicate camera art, distorted frame crop | **NOT RUN** |
| A02 — feed starts | Paper visible **only through/at the slot**, progressive reveal while still attached | Sheet appears far from camera, whole polaroid pops in instantly, floats in front of lens | **NOT RUN** |
| A03 — feed complete | Photo legible, still precisely attached to camera body even when Meong moves | Revealed texture stretches/slides sideways, paper stays fixed on screen while attached | **NOT RUN** |
| A04 — release | Sheet detaches **at its last attached world position** then falls with small natural sway | Teleports with Meong, spreads randomly, heads upward, blocks the UI | **NOT RUN** |
| A05 — z-order | Film emerges behind foreground camera face/slot trim and above background | Camera “printed” photo appears glued over the lens; two competing emitters | **NOT RUN** |
| A06 — finite & clean | Maximum two at once (one on Win), sheet fades before scene-sensitive bottom | Unbounded confetti, film over CTA/HUD/input, leftover photos after navigation | **NOT RUN** |
| A07 — pause | Gameplay pause freezes paper reveal, gravity and Meong/obstacles | Sheet keeps dropping behind PAUSED overlay | **NOT RUN** |
| A08 — active screen policy | Start, Gameplay, Win may print; Scan, Lose, Tutorial, Layout do not initiate prints | Invisible unintended emitters or photos retained on terminal/layout | **NOT RUN** |
| A09 — asset coherence | One latest approved camera sprite and clean source for print effect | Fallback to old logo, duplicate baked GIF paper, unbundled 26-frame claim | **NOT RUN** |
| A10 — resizing | Anchored outlet stays registered at 450×900/800×600/1200×800 | Paper origin shifts, crop/stretch due to letterbox/DPI | **NOT RUN** |

**Suggested deterministic unit checks when v5 is implemented:** camera-local slot coordinate/pose transform, single hero canvas, visible partial film masked by slot, exact fixed release point, bounded sway, grounded gravity, scene reset, no emitter on Scan/Lose, pause and Win cap. Current pure emitter tests should be kept; they **do not** verify actual asset-local outlet placement. A frame-level simulated visual test can supplement but never replace Windows Kivy video.

## G. Stability, performance and fairness

**Proposed performance target:** smooth game on actual Windows mini-PC / Intel Iris Xe-class GPU, **>=30 measured FPS** in a representative 25 s round, with no recurring stall caused by image loading, GIF decoding or repeated Pillow allocation in the Kivy update loop. Record minimum/average FPS, GPU/CPU, frame drops, memory drift and tested screen size; treat 30 FPS as a **candidate quality gate** until ratified on the final booth hardware.

**Collision fidelity:** physics currently uses rectangle bounds defined in `meong_fly.py` and mapped in `meong_fly_game_art.py`. Rendering irregular craters inside a broad tinted belt is acceptable only if users understand the full blocking area. Any approved rework of collision geometry needs its own engine and edge-case tests: apparent touch → Game Over, clear gap → survives, rainbow trail non-collidable, score once only after passing fully. Never silently change difficulty to “look nicer”.

**GUI regression:** reuse old tests for input canvas preservation (`canvas.before`), correct pause/action hit boxes, letterboxing, demo receipt replay across restarts, terminal single CTA and tutorial-seen flag. Run from the **exact future v5 SHA** and preserve full console output.

## H. Manual report form (fill only after real execution)

| Field | Value (leave blank until measured) |
| --- | --- |
| Evaluation date/time/timezone | |
| Feature branch and commit (`git rev-parse HEAD`) | |
| Windows edition/build | |
| Python / Kivy / Pillow / GPU versions | |
| Window sizes / DPI scaling | |
| Automated command and raw output location | |
| Total PASS / FAIL / ERROR / SKIP | |
| First 2–3 rendered screenshots and source of images | |
| 4-stage animation video and FPS report | |
| Q01–Q20 outcome / issue links | |
| V01–V16 visual acceptance per screen | |
| A01–A10 print animation acceptance | |
| Owner sign-off: APPROVED / REJECTED / NEEDS CHANGES | |
| Approval date and clear authorizing quote | |
| Remaining blockers / approved next commit scope | |

**Status vocabulary:** `NOT RUN` → `TESTED FAIL` / `TESTED PASS` (with evidence) → `OWNER ACCEPTED` (explicit). `BLOCKED` must state cause; `N/A` must have a rationale. Acceptance never means production release. Do not mark DOC-only modifications as app tests.

## I. Closure, regression and release boundaries

A future **v5 visual QA pass** requires: Q01–Q20 relevant behavior, V01–V16 and A01–A10 (with justified N/A only), stable tests on exact branch, no open source-level P0 visual defects, real screenshot/video side-by-side with the owner reference, and explicit owner approval of aesthetics. A production merge, real merchant scan, real discounts or actual thermal/camera output remain separate projects and **cannot** be inferred from this QA.

If a case fails: record screen/time/source SHA and minimal repro in [bug tracker](../bug_tracker.md), link its VF/QA ID, fix on the **existing feature branch only after authorization**, rerun affected tests and the complete regression, then amend [engineering status](../features/FEAT-021-meong-fly.md) and [changelog](../CHANGELOG.md). Keep test history intact and record the reversible commit baseline.

**No v5 code/tests executed while authoring this document.**
