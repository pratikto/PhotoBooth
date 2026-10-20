# FEAT-021 — Meong Fly isolated prototype

Status: IN PROGRESS — Step 3 standalone GUI owner-reported 6/6 PASS; NOT production/hardware certified.
Approved 2026-10-20: isolated prototype in feature/meong-flappy-challenge; no master merge.
Priority: P2 product enhancement, after core operational bugs; commercial integration BLOCKED.

## Scope
A standalone Kivy mini game inspired by tap-to-fly arcade mechanics, with a gray cat, rainbow trail, pipes, score, loss and win states. Entry point: `python -m photobooth.meong_fly_demo`. No receipt scan, welcome-screen integration, discount, merchant ledger, or Midtrans payment in this prototype.

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
