# FEAT-021 — Meong Fly isolated prototype

Status: IN PROGRESS — Visual Polish v2 Batch A (Start/Scan) + Batch B (Gameplay) IN SOURCE; current Windows GUI/visual acceptance PENDING. Batch C (Win/Lose) not yet polished. Historical Step 3 owner 6/6 PASS applies only to the older renderer, NOT this version.
Approved 2026-10-20: isolated prototype in feature/meong-flappy-challenge; no master merge.
Priority: P2 product enhancement, after core operational bugs; commercial integration BLOCKED.

## Scope
An isolated five-screen Kivy arcade mini-game with the approved Meong camera-cat logo crop, rainbow, a ten-point asteroid-gap challenge, pause, score, Win/Lose, and SQLite persistence enforcing a single play per locally entered `DEMO-...` token. Entry point: `python -m photobooth.meong_fly_demo`. QR artwork is decorative, NOT a real scan. There is no verified cafe POS/merchant receipt, redeemable discount, production welcome-screen integration or live Midtrans payment.

## Proposed future business rules (NOT IMPLEMENTED)
Model A: scan valid cafe receipt first, then one game attempt. A win may grant IDR 2,500 off the photobooth total. Subsidy is shared between Meong and cafe; 50:50 is a proposal, not a confirmed split. Only successful paid redemption is eligible for cafe settlement. Receipt validation must use verifiable unique tokens and atomic redemption; never trust GUI score alone.

## Acceptance and test plan
- Offline engine: start, flap, collision, one-time pipe scoring, win, reset.
- On Windows with Kivy: verify 25-second play, tap input, layout scaling, and restart.
- Future phases require GUI regression and device testing, receipt replay tests, transaction/idempotency tests and explicit separate authorization.
- No hardware, POS, or payment acceptance asserted.

## Changes
- `photobooth/meong_fly.py`: isolated simulation engine.
- `photobooth/meong_fly_demo.py`: standalone Kivy visualization.
- `tests/test_meong_fly.py`: offline unit tests.

## Evidence and limitations
Commits: `5499ae1c`, `ba3748df`, `9c43aa9e`.
Tests have NOT been verified passing. Attempted remote Git clone for local test execution failed; follow up with GitHub CI or a checked-out local workspace. No merge to master.

## 2026-10-21 — Space Edition and single-use demo flow
Owner approved implementing the space-themed game and one play per receipt on the isolated feature branch. The game now shows a dark space background, stars, asteroid-field obstacles, pixel camera-cat with blue lens and rainbow exhaust. This is a programmatic approximation of the reference logo, NOT yet the exact approved artwork asset.

The standalone Kivy demo accepts local `DEMO-...` identifiers. `DemoReceiptLedger` stores each consumed identifier in SQLite in the user's home directory; consumption occurs before game start, survives restart, and no retry button is presented. A result is informational only: the prototype DOES NOT create a redeemable voucher, verify a real cafe POS receipt, change QRIS pricing, or integrate with the production welcome screen.

Run: `python -m photobooth.meong_fly_demo`.
Targeted tests: `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts -v`.
Tests and physical GUI verification have NOT yet been executed/confirmed for these commits. Further work must validate the demo engine, actual artwork, kiosk screen scaling and collision fairness. Do not merge to master without owner approval.

## 2026-10-21 — Step 2 visual upgrade (approved)
- Kivy demo now draws an animated parallax starfield, planets, a blue horizon, textured cratered asteroid obstacles, and a wavy five-color rainbow trail.
- Player is a pixel-drawn gray camera-cat with large blue lens, camera flash, ears and pink cheeks. This is a visual approximation of the owner's logo; the exact uploaded GIF has NOT been committed as a sprite asset.
- No game physics, receipt rules, pricing, production welcome screen, or payment behavior changed in this step.
- Visual code commit: `d110af05`. Tests and real Kivy rendering have not been run/verified for this update. Required next: render on actual Windows Kivy, inspect frame sizes and collision fairness, and verify asset fidelity before declaring visual acceptance.

## 2026-10-21 — Step 3 prototype hardening (owner-approved)

Owner-reported Windows manual QA, prior to Step 3: 5/5 PASS (collision, used receipt rejected after restart, new receipt accepted, time limit, win condition). Control direction was observed as unexpected but explicitly accepted for now. This is operator-reported evidence, not an automated test run.

Step 3 isolated branch commits:
- `b74d6926`: collision and scoring boundaries now follow visible camera-cat body (left 24, right 54, bottom 25, top 33 relative to anchor). Decorative rainbow exhaust is intentionally excluded. This can change difficulty; repeat operator QA.
- `ac8b97d0`: terminal receipt outcome is written once per game instead of once per frame; drawing uses uniform scaling and centers game field for landscape without stretching sprites.
- `d32c75d6`, `8f08b8fe`: add boundary collision/scoring regression cases and adjust for frame movement.

**Verification remains pending**: CI and local Windows unit tests have NOT been run for these commits. An attempted clone into the execution environment failed because GitHub host resolution was unavailable. Run `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts -v` and launch `python -m photobooth.meong_fly_demo` on Windows; repeat the five manual QA scenarios, check narrow portrait and 800x600 / 1200x800 / 1920x1080 landscape readability and touch accuracy. Do not infer GUI/hardware PASS from earlier QA after collision changes.

No POS verification, discount, payment flow, welcome-screen wiring, or real receipt barcode scanning was implemented. No master merge. Follow-up before Step 4: record updated Windows regression results and reconsider character movement direction only on owner approval.

## 2026-10-21 — Step 3 Windows regression failure and scoped correction

Operator Windows Python 3.12 unittest run: 10 tests, 7 pass, 1 fail, 2 errors. `test_visible_sprite_bounds` incorrectly assumed the upper-bound collision despite upward movement before collision evaluation. Receipt tests encountered Windows `PermissionError [WinError 32]` when TemporaryDirectory attempted to delete SQLite files still held by connections; using SQLite connection as a context manager commits/rolls back transactions but does not necessarily close the connection.

Fix commits: `c4928576` explicitly closes SQLite connections via `contextlib.closing` while preserving commit/rollback semantics; `3a10577a` adjusts the upper collision input to account for one step of sprite motion. No receipt business rules or payment interactions changed. These are targeted corrections, not yet verified PASS on Windows. Run `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts -v` again and report the complete summary. Earlier operator-reported 5/5 gameplay QA remains historical and does not certify this revision. No merge to master.

## 2026-10-21 — Owner Windows unit retest evidence

Owner reported a successful Windows Python 3.12 run after the scoped SQLite and sprite-boundary test fixes, using `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts -v`. Result: 10 tests run in 0.050 s, all OK, 0 failures, 0 errors. This is owner-supplied terminal output rather than a remotely reproduced run. It supersedes the earlier 7 pass / 1 fail / 2 error run for these targeted tests. Remaining Step 3 acceptance: manual Kivy GUI validation after the hitbox and aspect-ratio changes, including portrait/landscape sizing and collision fairness. This does not authorize Step 4 integration or a master merge.


## 2026-10-21 — Step 3 GUI acceptance (owner-reported)

The owner reports completing all six Windows GUI Step 3 checklist items with **6/6 PASS**: launch/render, visible camera-cat versus asteroid collision (rainbow trail excluded), flap/tap responsiveness, portrait and landscape resizing, demo receipt replay rejection after reopening, and terminal win/loss behavior with no replay button. This is **owner-reported manual Windows Kivy evidence**, not a remotely observed or automated GUI test. Exact screen dimensions, screenshots, Windows build and runtime commit SHA were not supplied; these are not independently verified. Earlier owner-reported Python 3.12 targeted unit retest was **10/10 PASS**. Thus the isolated Step 3 prototype meets owner-reported manual acceptance, while production kiosk integration, real receipt/POS validation, real discount/payment, end-to-end regression, and hardware release remain unverified/not implemented. No merge to master.

**Next proposed milestone (NOT YET APPROVED):** Step 4 welcome-screen integration design and isolated implementation, with safe skip-to-photo, session ownership, one-attempt persistence, and regression tests. Obtain explicit approval of Step 4 scope before code changes. Visual fidelity to exact logo asset remains a separate polish item.


## 2026-10-21 — Owner-approved revised Step 4: mockup-matched standalone GUI

**This section supersedes the earlier proposed Step 4 welcome-screen integration.** Owner explicitly rejects integration into the existing photobooth GUI until the standalone mini-game visually matches the attached five-panel pixel-art space mockup, and approved proceeding ("oke gas"). Implement **only on `feature/meong-flappy-challenge`**; no `master` merge or changes to production GUI, printer, camera, audio, ads, payment, or real QRIS.

### Screen-by-screen implementation specification
1. **Start:** dark pixel-art starfield, planets, the Meong camera-cat **actual logo asset** (gray cat, white camera, prominent blue lens, waving rainbow, pink accents), `MEONG FLY!` hero panel, Rp2.500 promotional example, pink `MAIN GAME`, cyan `LANGSUNG FOTO`.
2. **Receipt:** `SCAN STRUK KAFE` themed visual, decorative sample QR zone **clearly labeled nonfunctional demo**, manual `DEMO-...` input and an explicit one-use demo validation action, `KEMBALI` without consuming an attempt. NO POS/barcode/camera scanner.
3. **Gameplay:** moving starfield and layered celestial objects, actual logo-derived flying camera-cat sprite, moving asteroid clusters with hitbox-aligned visual boundaries, top `SCORE` / `TARGET` HUD and pause/resume control, tap/click to flap. Retain stable physics and one-attempt receipt ledger; mockup displays a target of 10 (update target and tests together if changed).
4. **Win:** `MISSION COMPLETE!`, celebratory camera-cat and yellow Rp2.500 promotional panel, primary continue CTA. Discount remains simulation only: **no checkout/QRIS integration**.
5. **Lose:** `GAME OVER`, actual score, clear no-discount message and same continue CTA. **No `MAIN LAGI` button on either terminal screen.**

### Navigation / acceptance
`Start -> Receipt -> Gameplay -> Win/Lose -> Exit standalone demo`; `Start -> Direct photo` exits the standalone demo (does not open the production photobooth); `Receipt -> Back` returns to Start before claim. Once a demo receipt is atomically claimed, no button, restart, back navigation, pause, or app relaunch permits playing that code again. Running the demo must work on Windows Kivy at portrait and landscape sizes without stretched sprites or incorrect tap locations. Keep code logic testable independently of Kivy. Record actual testing results, do not report Windows visual pass without an owner rerun. Rollback: restore pre-Step-4 feature branch commit; `master` remains unaffected.

### Deliberately excluded
Real QR scanning/POS validation, redeemable discounts, subsidy settlement, payments, photobooth welcome-screen wiring, shared session state, auto-transition into camera, and any changes to production operational flows.


## 2026-10-21 — Step 4 implementation: five-screen standalone GUI (source committed)

**Approved source scope:** rebuild the isolated demo's visual identity to match the owner's attached five-screen space pixel-art reference. The owner explicitly postponed any integration into the *existing* Kivy photobooth GUI. Old Step 4 integration notes above are **superseded** by this standalone design milestone.

### What is actually implemented in this branch

| Screen | Implementation | What is NOT functional |
| --- | --- | --- |
| Start | Approved bundled `photobooth/assets/meong_photobooth_vivid.png` rendered with transparent, nearest-neighbor display crop; planets, stars, pixel-bitmapped panels, pink MAIN GAME and cyan LANGSUNG FOTO. | Direct Photo only exits demo; it cannot open the production camera |
| Scan | Space-themed QR-illustration frame, focusable `DEMO-...` text input, demo validation button, and pre-claim Back action. | QR illustration is **NOT scannable**, no camera or merchant POS connected |
| Gameplay | Existing physics engine and collision bounds, logo-derived camera-cat body, wavy rainbow trail, parallax stars, visibly occupied textured asteroid belts, score/target HUD, pause/resume and tap-to-fly. | Gameplay is neither launched from photobooth nor tied to checkout |
| Win | MISSION COMPLETE, decorative Meong rainbow, Rp2.500 demo promotional panel and continue CTA. | No redeemable discount, Midtrans, or settlement |
| Lose | GAME OVER, dynamic `score/10`, regular-price copy and same continue CTA; **NO Main Lagi**. | No paid photo order is created |

**Shared policy:** `TARGET_SCORE = 10` to match the owner's reference (previous demo used 6). 25-second timeout retained. Once an identifier is claimed in SQLite, it remains consumed through a crash, finish or application relaunch. No end-state route or back button restarts a claimed game. The pink `LANJUT KE PEMBAYARAN` CTA closes the standalone demo; the on-screen footer labels the entire flow a demo, so it does **not** perform payment. Window is portrait by default; landscape must letterbox at the correct aspect ratio and share the same logical button hitboxes.

### Source and regression inventory

- `photobooth/meong_fly_painter.py` — pure-Pillow five-screen pixel-art backgrounds and controls, optional white-edge transparency mask of the approved logo, cropped on-screen camera-cat, asteroid tiles; no new logo file.
- `photobooth/meong_fly_flow.py` — Kivy-independent state transitions, irrevocable demo receipt claim, result-once ledger write, and pause.
- `photobooth/meong_fly_gui.py` — standalone Kivy GPU texture stage, real input field, animated asteroid/game layers, proportional touch mapping.
- `photobooth/meong_fly_demo.py` — thin backward-compatible entrypoint.
- `photobooth/meong_fly.py` — isolated 10-point target; no changes to production photobooth modules.
- `tests/test_meong_fly_flow.py`, `tests/test_meong_fly_painter.py` — new headless flow/art regression cases; old engine/receipt tests retained.

Key commits: scope `7c415396`, flow `8194f979`, target `5a2d4f9a`, painter `37e28433`, GUI `1ff153a9`, demo entry `ca134b66`, visual bounds/animation/performance polish `4623a289`, `b6a0802e`, `cbc330f6`, and painter target regression `e4d2de72`. Specific test additions: `796169ff`, `62719e41`.

### How to run the latest standalone GUI

```powershell
git fetch origin
git switch feature/meong-flappy-challenge
git pull origin feature/meong-flappy-challenge
.\.venv-kivy\Scripts\Activate.ps1
python -m photobooth.meong_fly_demo
```

1. Click **MAIN GAME** -> Scan screen.
2. QR artwork is for visual guidance, **NOT a working scanner**. Type a unique `DEMO-MOCKUP-001`, then **VALIDASI DEMO 1X**.
3. Click/tap the game to flap. The actual target is **10**; `II` pauses/resumes.
4. Win/lose shows one continue CTA that **closes the demo** (no production payment). There is no replay.
5. Relaunch; `DEMO-MOCKUP-001` must be rejected. Use `DEMO-MOCKUP-002` for another test.

### Verification truth and remaining gate

**Performed locally in an isolated mirrored source workspace, NOT from a live clone of the GitHub branch:** Python compilation passed; Pillow successfully generated five 360x720 static concept frames using the owner's supplied transparent GIF as a stand-in for the bundled PNG; a local headless smoke script verified demo receipt claim, replay rejection, back/skip, pause, win, 10-point target, 5 screen images, and lack of retry controls. This is **not** a completed GitHub CI or real Kivy GUI test. Environment does **not** have Kivy; neither the new source's real rendering on Windows nor its FPS/resize/touch accuracy has been observed here. The two new test modules have been committed but their exact GitHub-branch execution is **pending**.

**Required owner validation before marking polished UI accepted:** run `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts tests.test_meong_fly_flow tests.test_meong_fly_painter -v` (record full output); launch Kivy on Windows; visually compare **each of five screens** with the supplied mockup; confirm approved logo has no white rectangular background or clipped head/wordmark, sprite/hitbox fairness, stars/asteroids animated, score 0..10, pause/resume, typed demo voucher once only even after restart, terminal CTA closes without checkout, no retry; test portrait plus landscape and capture screenshots/OS/commit hash. Fix visual gaps **on this branch** only after reproducible feedback. Never merge to master before explicit owner approval.


## 2026-10-21 — BUG-012: scan-demo input canvas regression (source fix, Windows QA pending)
Owner screenshot of the new mockup-styled `SCAN STRUK KAFE` page shows the white field but typing appears impossible. In `MeongFlyStage._refresh`, `self.canvas.clear()` removed child `TextInput` canvas instructions while the fake painted input box remained visible. Scoped fix: repaint static/dynamic scene using `self.canvas.before.clear()` and `with self.canvas.before`, preserving the real child input's text/cursor rendering. **Code:** `974b8c7c`; **new regression tests:** `38d00d41` (`tests/test_meong_fly_gui.py`). Root cause is supported by source inspection; the precise Windows symptom is owner-reported, and **the fix has not yet been operator-verified**. Demo input should accept `DEMO-INPUT-001` in a fresh receipt and reject its reuse across restarts. No real scanner, production GUI, or payment changes.


## 2026-10-21 — Approved Visual Polish v2, Batch A source delivered (Start + Scan only)

The owner approved continuing **Batch A** after reviewing the pixel-arcade v2 specification. The original visual identity stays intact: dark navy retro space, bundled camera-cat logo, rainbow motif, asteroid planets and pink/cyan/gold controls. **This is strictly a standalone mini-game feature branch and not a production photobooth GUI integration.**

The complete [Visual Polish Spec v2](FEAT-021-visual-polish-v2.md) is now tracked on GitHub. Source changes:
- `photobooth/meong_fly_polish.py` (`74bdef6a`, refined `e18a0936`): pure-Pillow v2 Start and Scan art, shared stepped arcade panel/button helper, behind-logo star halo, legible mock voucher, space accent motifs, scanner corner brackets and QR simulation labels. Start and Scan preserve their existing `ACTIONS`/input geometry.
- `photobooth/meong_fly_painter.py` (`cbc74372`): delegate only Start/Scan backgrounds to v2 renderer; Gameplay, Win and Lose artwork unchanged in this batch.
- `photobooth/meong_fly_gui.py` (`f8bc996b`, cleanup `f7b0598e`): lightweight Kivy scan-beam animation (decorative), focus/error outline for real editable `TextInput`, optional hover highlight using the SAME hitboxes, and listener/Clock cleanup on app stop. Preserve BUG-012 `canvas.before` layering.
- `tests/test_meong_fly_polish.py` (`05fccdd6`) and `tests/test_meong_fly_gui.py` (`6df4d498`): pure Pillow canvas/contrast/button/input geometry and optional Kivy hover/input redraw regression.

**Evidence:** 7/7 pure-Pillow standalone visual-layout tests PASS on assistant-side local source mirror; the module compiles in that local container. Kivy is NOT installed in that execution environment. New exact GitHub branch SHA, Windows Kivy GUI, real logo asset rendering/interactive input and window resizing **NOT VERIFIED**. The local preview uses a previously supplied logo/GIF frame as stand-in; production game uses existing bundled `meong_photobooth_vivid.png`. Do not transfer old Step 3 6/6 Windows acceptance to this new design.

**Acceptance gate:** owner must test Windows Start and Scan at portrait/landscape, verify no text overlapping cards, input cursor/typing and Enter/Validate work, Back before claim leaves receipt unused, and codes are rejected after use/restart. The mock QR does not scan. One receipt = one attempt and no replay remain unchanged. Batch B Gameplay and Batch C Win/Lose still require a separate continuation; no `master` merge.


## 2026-10-21 — Visual Polish v2 Batch B source and pending GUI acceptance

Owner authorized continuing Gameplay aesthetics after Batch A. New [v2 Batch B art/status](FEAT-021-visual-polish-v2.md): added `photobooth/meong_fly_game_art.py` (cached cosmos background, five asteroid color/crater variants, three cosmetic approved-logo camera-cat poses, shared exact hitbox mapping) and routed only the Gameplay background through it; `photobooth/meong_fly_gui.py` now renders parallax stars, the rock belts, waving/tapered rainbow, score +1 glint, pause highlight and 220 ms collision burst before the Game Over page. Engine physics, `TARGET_SCORE = 10`, one-receipt-one-attempt ledger, no retry, Start/Scan/Win/Lose layouts, real QR/POS/payment restrictions, and `master` stay unchanged. Source commits `72658e55`, `b60c0d68`, `a08952fd`, `7b7b448a`, `ad4a2e49`, `1cea6794`. Test commits `9ed6ab19`, `f5349bef`.

**Testing truth:** local mirrored Python/Pillow test run 19 total / 15 PASS / 4 Kivy SKIP, compileall success and a headless receipt-flow smoke success. These are not GitHub CI or Windows GUI verification; exact-branch and owner Gameplay screenshots, collisions/FPS/pause/replay QA remain pending. Related BUG-012 TextInput canvas rendering fix remains untouched and must be retested after pulling this version.


## 2026-10-21 — Owner-provided targeted Windows Kivy Batch A/B regression PASS

The owner pasted Windows console output confirming **`Ran 55 tests in 6.272s` / `OK`** across eight FEAT-021 test modules (55 PASS, zero FAIL/ERROR/SKIP). Real Kivy **2.3.1** on Python **3.12.10** used Intel Iris Xe/OpenGL 4.6. All relevant Kivy gameplay-pause-score-hit transition checks, receipt TextInput canvas tests, demo receipt single-use tests, geometry and painter regressions passed. The previous Linux local-mirror **4 Kivy skips** are superseded **only for the executed targeted Windows suite**. The exact tested Git SHA and Pillow version were not supplied; visual/manual screenshots and FPS remain pending. Status: **owner-reported Windows automated acceptance PASSED, manual aesthetic/kiosk QA NOT VERIFIED**. No code change, no checkout integration, no merge to `master`. See [QA checklist](../test_checklist.md).


## 2026-10-21 — Owner-approved photo-layout navigation after Meong Fly

**Approved product flow:** Win and Lose screens must offer **PILIH LAYOUT FOTO**, not payment. The Start **LANGSUNG FOTO** path also skips the game, but the user must see the tutorial once if not yet completed. Correct destination ordering: `Start -> [Scan -> Game -> Win/Lose OR Direct Photo] -> Tutorial if unseen -> Layout Selection -> (future approved photobooth checkout/capture)`. One receipt = one attempt; **no retry**; win demo discount is an in-memory session hint only, not a monetary entitlement. The existing production 12 thermal layouts remain untouched.

**Implemented on isolated branch only (not kiosk integrated):**
- `photobooth/meong_fly_flow.py` commit `1f00af59`: `continue_from_result()` and `direct_photo()` route via one-time tutorial flag to `layouts`; preserve terminal win/loss and demo discount metadata without claiming production checkout; `finish_tutorial()` and `select_layout(1..12)` enforce state and no replay.
- `photobooth/meong_fly_photo_handoff.py` commit `5da9abd0`: explicitly labelled **standalone DEMO** tutorial and generic 12-pattern layout preview; not the approved production thermal template renderer, not print ready.
- `photobooth/meong_fly_painter.py` commit `20b6d2c0`: Win and Lose CTA text becomes `PILIH LAYOUT FOTO`; registers tutorial/layout hitboxes and painted screens.
- `photobooth/meong_fly_gui.py` commit `45056a8f`: handles tutorial and selection buttons, retains the `canvas.before` input fix; demo tutorial completion marker `~/.meong_fly_tutorial_seen`, independent of production tutorial preferences. Choosing a demo layout **exits** the isolated demo; no production session is started.
- `tests/test_meong_fly_flow.py` commit `8112e700`: rework existing start/direct-photo/win/loss tests to expect tutorial/layout navigation, verify tutorial-seen bypass and demo discount metadata. No code/tests on `master` changed.

**Known constraint:** this is an *isolated UI/navigation prototype*, not actual photobooth main-GUI layout integration; no real full session, payment, printer or hardware output. Needs owner Windows GUI and exact-branch tests before acceptance. Future actual integration requires separate approval.
