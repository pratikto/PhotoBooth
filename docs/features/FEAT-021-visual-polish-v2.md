# FEAT-021 — Meong Fly: Visual Polish Specification v2 (HISTORICAL)

> **SUPERSEDED VISUAL SPEC / HISTORICAL IMPLEMENTATION SNAPSHOT (2026-10-21).** This document records the v2 Batch A/B plan and tests **as they were known then**. Since then, **v3 Start/Win/Lose poster code and v4 photo-print animation have been committed** on the existing mini-game feature branch. It is therefore **not correct** to read “Batch C not yet implemented” as a current code inventory, nor to treat later code as visually accepted. The owner has **rejected current visual fidelity** against the latest neon poster.  
> **CURRENT authoritative design/status:** [FEAT-021 Visual Overhaul v5 source audit and per-object requirements](FEAT-021-visual-overhaul-v5.md) + [v5 visual QA matrix](../qa/FEAT-021-visual-v5-acceptance.md) + [current FEAT-021 status](FEAT-021-meong-fly.md). **V5 is documentation only, NOT source implemented or code-approved.** The older 55/55 owner Windows regression applies to the older A/B version, not v4/v5.

**Date of original spec:** 2026-10-21  
**Historical status:** Batch A Start/Scan and Batch B Gameplay were implemented at the time; Batch C was then proposed. **Subsequent v3/v4 changes are documented in the links above**.  
**Scope:** Standalone Meong Fly Kivy mini-game only.  
**Target branch:** `feature/meong-flappy-challenge`  
**Stable baseline:** `master` is read-only; no merge or kiosk integration without explicit approval.  
**References:** Owner-provided five-panel pixel-art mockup and subsequent actual Windows screenshot of the Scan Struk screen.  
**Related:** FEAT-021, BUG-012 (receipt input drawing regression).

## 1. Design brief

**Art direction:** *Pixel Arcade Premium*: a friendly, visually expressive retro-space game featuring the original Meong camera-cat, colorful rainbow exhaust, deep-navy cosmos, ringed planets, and cratered asteroids. The goal is to refine the **same theme**, not redesign it or introduce a different mascot.

The v2 result must have a consistent visual system, a strong focal point on each screen, clearly layered space scenery, clean and readable pixel typography, responsive and usable input/CTAs, and delightful but lightweight motion. All UI must be actual interactive Kivy widgets/hit regions, **not a screenshot with fake controls**.

### Product constraints (binding)

1. One unique valid demo receipt code grants exactly **one attempt**. Claim occurs before gameplay; reuse is rejected after loss, win, back navigation, or app restart. No `MAIN LAGI` button or reset path.
2. The visual `QR` on the Scan page is a **decorative demonstration**, not a scanner. Require typed `DEMO-...` codes until a separately approved real POS flow exists.
3. Win's `Rp2.500` is explicitly **simulated**, not a redeemable payment discount. Both result CTAs and `LANGSUNG FOTO` only exit the standalone demo for now.
4. No modifications to the photobooth kiosk welcome screen, camera, printer, audio, payment, QRIS, real receipts/POS or actual checkout.
5. Preserve approved logo artwork (`photobooth/assets/meong_photobooth_vivid.png`). Do not replace the actual gray camera-cat/blue-lens identity with a synthetic cat or rocket character.
6. Existing FEAT-021 Step 3 operator acceptance is historical. This new visual version requires fresh acceptance on Windows; a rendered Pillow preview is not an interactive Kivy test.

## 2. Audit findings: original mockup versus current v1 UI

| Area | Current observation | Target v2 | Priority |
| --- | --- | --- | --- |
| Overall | Space colors and pixel identity are present; visual density varies widely across pages | Common grid, depth, type hierarchy and predictable contrast | P0 |
| Start | Original logo and basic CTA cards are present; hero depth/promo ticket treatment limited | Intentional logo focal point, restrained sparkle halo, pixel ticket, tactile buttons | P1 |
| Scan | Actual Windows screenshot shows QR illustration, input and actions, but visual rhythm is cramped and the field was previously unusable due to redraw | Purpose-built scan console with safe text field, clear demo state, decorative scanner corners | P0 |
| Gameplay | Static preview appears empty without the live sprite/obstacles; rock obstacles repeat and HUD is sparse | Capture live gameplay screenshots; readable HUD, layered sky, diverse believable rock patterns, expressive motion | P1 |
| Win | Reward is legible but victory reveal is comparatively flat | Hero mascot, layered light rays, restrained pixel confetti, prominent coupon and CTA | P1 |
| Lose | Static mascot and score panel lack distinct emotional personality | Cute crash/exhaustion expression, collision particles, score card, reassuring copy | P1 |
| Typography | All-caps bitmap text tends to carry equal weight | Distinct headline/body/microcopy sizes and strict line limits | P0 |
| Interaction | TextInput rendering BUG-012 previously broke when canvas was cleared | Never clear child widget canvases; preserve focus, text cursor, keyboard input, button press feedback | P0 |

**Important source distinction:** `photobooth/meong_fly_painter.py` renders the base 360×720 artwork using Pillow; `photobooth/meong_fly_gui.py` owns Kivy textures, responsive coordinates and real input; `photobooth/meong_fly_flow.py` owns receipt/state rules. An aesthetic change in one layer must not silently change the others.

## 3. Visual system / design tokens

### 3.1 Grid, spacing and dimensions

- **Logical portrait stage:** 360×720 pixels (`W=360`, `H=720`), with crisp nearest-neighbor scaling; reference Windows window 450×900.
- **Safe bounds:** content generally within x=20..340 and y=20..700; use logical 8 px spacing steps, plus 4 px microspacing and 16/24/32 px major breaks.
- **Reusable content widths:** full hero 312 px; content card 288–312 px; primary button 270–292 px; secondary button 232–290 px.
- **Minimum legible physical text:** test on 450×900 and 800×600; no clipping at logical/physical letterbox edges. Prefer a dedicated landscape-responsive layout (e.g., split game art and controls) when a simple portrait letterbox makes inputs or buttons too small.
- **Button active area:** no less than 44×44 physical pixels where practical. Visual rectangles and Kivy event targets must coincide. Distinguish hover, focus, pressed and disabled states (including keyboard activation when relevant).
- Never stretch Meong, the QR illustration, planets or text independently on resize. Keep integer-aligned pixel scaling for bitmap art where possible.

### 3.2 Palette (reuse current source constants, refine application)

| Semantic token | Hex | Role |
| --- | --- | --- |
| Deep space | `#050C2F` | Primary background |
| UI panel | `#0B1543` | Interior cards/HUD |
| Panel edge | `#57499A` | Pixel outlines; not overpowering |
| Ink | `#070D26` | Dark readable button text/shadows |
| White | `#F8F8FF` | Primary text and highlights |
| Pink | `#FF55AB` | Primary CTA/reward accents |
| Cyan | `#58D1FF` | Secondary CTA and HUD target |
| Gold | `#FFDC78` | Reward/score/event highlights |
| Purple | `#B385FF` | Title and decorative effects |

Suggested usage by visual area: ~70% dark space/panels, 20% readable text/UI structure, 10% high-chroma accents. Do not fill every panel with glowing effects: readability takes priority.

### 3.3 Consistent component patterns

**Panels:** pixel-stepped silhouette; 2–3 px outline; 1 px upper-left highlight; 3–4 px lower/right offset shadow; consistent inner padding (12–16 logical px). Reuse helper(s), not manual one-off panel styling per page.

**Primary pink button:** light upper highlight, magenta fill, dark bottom shadow; 1–3 px `pressed` downward shift; aligned icon/pixel text; larger than any neighboring secondary CTA.

**Secondary cyan button:** same depth/material treatment; reserved for safe alternative actions (e.g., `LANGSUNG FOTO`). **Tertiary navy button:** restrained outline and subtle pressed state for `KEMBALI`.

**Typography:** use the existing 5×7 pixel-glyph asset only with a deliberate hierarchy. H1 3–5 logical scale, CTA 2–3, body 1–2, caption 1–2 depending on width. Keep text ≤ one/two lines by role. Ensure exact spelling: `MEONG FLY!`, `SCAN STRUK KAFE`, `VALIDASI DEMO 1X`, `MISSION COMPLETE!`, `GAME OVER`, `LANJUT KE PEMBAYARAN`. Avoid cutting Indonesian text at screen edges. Tiny captions can use a crisp non-pixel UI font if readability is demonstrably better, but do not introduce an unlicensed external font dependency.

**Focus contrast:** normal text high contrast; avoid microcopy blending into starfield. Text never overlaps its outline, input, planet, or action target.

## 4. Screen specifications (per page + per object)

### 4A. START SCREEN — hero brand + two choices

**Focal order:** original Meong logo → `MEONG FLY!` → Rp2.500 prize ticket → `MAIN GAME` → `LANGSUNG FOTO`.

| Object | Required visual refinement | Functional guard |
| --- | --- | --- |
| Logo | Render official bitmap with alpha/white-edge cleanup; scale proportionately and keep complete Meong wordmark and ears visible; soft starburst behind (not over) the logo | Never mutate original PNG; do not block start button hitbox |
| Cosmic scenery | Ringed planet at upper-left plus small asteroids at side margins; add 2–3 star depth levels with sparing twinkles | Decorations must remain outside interactive controls |
| Hero title card | Stronger frame + inner highlight, visible gap after logo; `MEONG FLY!` in purple/gold treatment without reducing contrast | Keep subtitle on two centered, readable lines |
| Promo ticket | Gold voucher with pixel notched corners, warm inner gradient/dither, small ticket icon; `Rp2.500` is the main visual | Add `SIMULASI` legible in/near ticket, not misleadingly hidden |
| `MAIN GAME` | Dominant pink CTA with controller icon, shadow and pressed feedback | Opens Scan, not Gameplay directly; does not consume receipt |
| `LANGSUNG FOTO` | Cyan secondary CTA with camera icon, aligned baseline and identical radius/shape language | **Exits demo only**, never invokes production checkout/photo |
| Footer | Small but legible non-payable demo notice | Never show false real discount promise |

**Acceptance:** logo edges intact, no overlapping content at 450×900; pink CTA visibly dominant; button centers clickable on Windows; Start→Scan and Direct Photo→exit routes work.

### 4B. SCAN STRUK — premium scanner console + real text entry

**Focal order:** screen title → QR illustration/scanner → actual `DEMO-...` input → pink Validate CTA → Back.

| Object | Required visual refinement | Functional guard |
| --- | --- | --- |
| Header | Tighter `SCAN STRUK KAFE` panel, with helpful subheading in 1–2 lines | State explicitly that real QR is not connected |
| Scanner frame | 4 bright pink/cyan corner brackets, soft shadow, slow non-obstructive scan line and occasional pixel glint | Decorative only; must not pretend to decode QR |
| QR illustration | Center within frame, consistent white/light plate with ≥12 px inner margin | Clearly labeled `ILUSTRASI QR`; not scannable/validated |
| Entry label | Position outside/above field with ≥8 px gap; no overlay on input border | No hit-target overlap with QR or Validate button |
| Text input | Real Kivy `TextInput`, white console fill, visible hint `DEMO-123`, dark text, high-contrast blinking caret, left padding 12–14 logical px; error focus outline | Cursor, keyboard selection, paste, backspace, Enter all work; text survives background redraw |
| Validation button | Pink wide CTA, pressed state and brief non-blocking busy/feedback when appropriate | Claim demo code atomically ONCE; invalid/used code never starts game |
| Back | Navy tertiary button, visually quieter | Returns to Start without consuming code if no claim |
| Background | Distant Earth partially visible at bottom, but never behind text/input or obscure CTA | Clear touch area remains on portrait and landscape |

**Suggested vertical rhythm (logical coordinates, 360×720):** scanner illustration zone ends around y=432; its label at 442; input label around y=457; actual editable input around y=487–530; validation CTA starts ≥550; Back around 635. Refine precise values via rendered frames and Kivy hitbox tests; do not blindly hard-code positions without checking visual overlap.

**Acceptance:** user clicks the painted field and types a unique `DEMO-V2-001`; characters and caret render immediately, Enter or Validate starts gameplay exactly once; a reused code after relaunch is rejected; invalid input is clearly explained. This is a regression gate for BUG-012.

### 4C. GAMEPLAY — lively arcade, honest obstacle geometry

**Focal order:** moving Meong → playable asteroid gap → Score/Target HUD; scenery secondary.

| Object | Required visual refinement | Functional guard |
| --- | --- | --- |
| HUD | Consistent mini-panels: Pause left, Score center, Target 10 right; 2 px borders, adequate horizontal air | Score text must render actual value and not overlap gameplay |
| Pause | Pixel `II` or pause icon with pressed/unpaused states; dim overlay with `PAUSED` in center | When paused no score/physics change and no flap; tap resumes |
| Meong sprite | Preserve original camera-cat silhouette/blue lens/face from brand logo; use nearest-neighbor and transparent edges | Keep visual body within existing engine hitbox, rainbow excluded |
| Movement | Distinct mild rising/falling angles, optional 1–2 px bob; never obscure pupil/lens or break silhouette | Cosmetics cannot alter physics or make hitbox deceptive |
| Rainbow | Taper to the left, smoother wave spacing and 5 consistent vibrant bands, sparse sparkle particles | Cosmetic only, independent of collisions |
| Asteroid obstacles | ≥4 variants (gray, purple, warmer rock, layered craters), varied silhouette INSIDE existing collision rectangles | No opaque protrusions outside collision boundary; gaps visibly fair |
| Cosmic depth | Far faint stars, middle nebula/glow, distant galaxy/planets; 2–3-speed parallax | No flashing overload, stutter, or FPS collapse |
| Score feedback | Small gold +1 sparkle/pop at pass; 150–300 ms and non-blocking | Award score only when entire sprite clears obstacle, once per obstacle |
| Hit feedback | Brief pixel impact/burst and reasonable scene settling before Lose | Do not create second attempt, double record or trigger extra game step |
| Instructions | One compact `TAP UNTUK TERBANG!` hint in empty lower UI area, fade after first input | Keep game area/edge boundaries clearly identifiable |

**Motion budget:** target stable ~30 FPS initially on intended Windows mini-PC. Pre-render static layered backgrounds and reusable asteroid/particle textures; avoid creating PIL images or uploading new GPU textures every frame. Use numeric time-based transforms and modest particle counts. Track worst-case frame time and memory over ≥3 minutes of repeated launches; gameplay per attempt is still time-limited.

**Acceptance:** visible asteroid shape and rectangular physics zone agree; score target is **10** in both UI and engine; ~25-second gameplay rule unchanged unless separately approved; tap/flap/pause are responsive; a still screenshot captured while actually playing shows Meong and obstacles (not the intentionally empty static background template).

### 4D. WIN SCREEN — unmistakable celebration

**Focal order:** `MISSION COMPLETE!` → large celebratory Meong → gold Rp2.500 voucher → pink Continue CTA.

| Object | Required visual refinement | Functional guard |
| --- | --- | --- |
| Header | Chunky stacked retro headline with gold fill, pink/dark pixel drop shadow, small margin from top | No cropped letters at 360×720 |
| Meong | Larger, happy pose/glint, rainbow swirl, distinct personality vs normal gameplay | Use approved logo; no fake reward/payment signal |
| Burst/confetti | Sparse star rays behind Meong and 15–25 pixel confetti pieces, staggered sparkle | Avoid effects covering text/CTA; accessible reduced motion if practical |
| Ticket | Gold bevel/border, obvious small ticket icon and huge `Rp 2.500` | Explicit `SIMULASI - BELUM AKTIF` in readable position |
| Continue CTA | Large pink pressed-state button, clear text | Exits standalone demo; no checkout integration |
| Replay | **ABSENT** | Never render, map or react to `MAIN LAGI` |

**Acceptance:** one win result, no double ledger write, coupon is plainly simulated, Continue works once; no retry route.

### 4E. LOSE SCREEN — playful disappointment, no punishment

**Focal order:** `GAME OVER` → sympathetic Meong/crash → score card → reassurance → pink Continue CTA.

| Object | Required visual refinement | Functional guard |
| --- | --- | --- |
| Header | Bold coral-pink pixel typography with deeper shadow, lighter emotional tone than a harsh red full-screen flash | Retain legibility at all sizes |
| Meong | Gentle defeated/X-eye overlay or tiny dizzy stars, flattened rainbow; mascot should remain recognizable | Do not destroy original asset, keep as overlay/crop |
| Asteroids | A few nearby impact fragments at edges, tasteful darker vignette | No collisions simulated after terminal status |
| Score card | Clear `SCORE 6/10`-style result with real score, centered and padded | Do not hardcode 6/10; use actual `game.score/TARGET_SCORE` |
| Reassurance | `TIDAK APA-APA!` / `KAMU MASIH BISA FOTO DENGAN HARGA NORMAL.` readable over two/three lines | No discount after loss |
| Continue CTA | Same pink material system as Win | Exits demo; **NO MAIN LAGI** |

**Acceptance:** loss feels distinct from Win, actual score is shown, no misrepresented discount, no retry route, screen remains visually calm at 450×900.

## 5. Shared asset/object review checklist

| Shared object | Design checks | Technical checks |
| --- | --- | --- |
| Brand logo | Bright original colors, complete ears/camera/trail/wordmark, no fuzzy crop | `branding.LOGO_PATH` official asset, preserve proportions, do not overwrite PNG |
| Camera-cat sprite | Body visible at small size; blue lens and expression readable | Sprite/hitbox fairness in climb/drop/impact states |
| Rainbow trail | Five coherent bands, taper, wave, sparse pixel sparkles | Cosmetic; not included in obstacle collision |
| Asteroids | Distinct craters and color variations, 3D shading in pixel language | Mask inside real rectangular obstacle bounds |
| Stars/planets/nebula | Composition guides eye rather than filling every empty area | Static/background layers cached, parallax low cost |
| Panels | One border/shadow/highlight standard | No overlap with text, child widgets, or their canvases |
| Buttons/icons | Shared normal/hover/pressed states, aligned glyph+icon | Correct Kivy hit map after every resize; keyboard focus as needed |
| Font | Readable hierarchy and capped text width; no overlong copy | Pixel alignment and fallback glyph support (Rp text, punctuation) |
| Input | Caret/hint/typed text clearly visible, error state, focus indication | Use real `TextInput`; preserve `canvas.before` layering after refresh |
| Scan frame | Good scanner illusion, well-labeled illustration | No camera scanner/QR parser invoked |
| HUD | Score/target/pause instantly readable | Correct score, time and pause state; no invalid touch targets |
| Win/Lose particles | Emotionally appropriate but restrained | Deterministic time-based animation; no game-state change |

## 6. Concrete implementation map (source files)

| File | Work items | Risk / test |
| --- | --- | --- |
| `photobooth/meong_fly_painter.py` | Central design tokens; shared panel, button and type renderer; polished `paint_static_screen` for 5 screens; scanner corners, ticket, HUD, glow motifs; add support for consistent visual states | Pure Pillow snapshot tests and layout assertions; avoid clipped glyphs and UI overlap |
| `photobooth/meong_fly_gui.py` | Render-architecture for fixed layers + timed dynamic overlays; hover/pressed/keyboard mapping; portrait & landscape hitbox correctness; focus/error affordance for receipt input; star/rainbow/particles + status transitions | NEVER regress BUG-012 by calling `self.canvas.clear()` on parent with live children; conditional Kivy tests and Windows operator QA |
| `photobooth/meong_fly_flow.py` | Ideally no visual-only logic changes; expose safe UI state flags if essential (paused, terminal) | One receipt = one attempt, no replay, back before claim only |
| `photobooth/meong_fly.py` | Preserve engine rules, target 10 and current hitboxes; only adjust if visual geometry cannot honestly match existing collision rectangles | Targeted physics/collision tests; no physics change as part of aesthetic-only pass without explicit evidence |
| `photobooth/meong_fly_receipts.py` | No changes expected | SQLite atomicity, reuse rejection across restart |
| `tests/test_meong_fly_painter.py` | New composition/snapshot/label/region checks for five pages (not only pixel equality) | Pillow smoke; compare against approved v2 reference renders |
| `tests/test_meong_fly_gui.py` | Input + caret redraw, touch/resize, action map, visual layer persistence, pause/menu interaction | Run with Kivy on Windows, mock where possible |
| `tests/test_meong_fly_flow.py` | Retain terminal/no-replay and invalid code cases | No accidental restart action |
| `docs/features/FEAT-021-meong-fly.md` | Link to this v2 design spec, versioned v2 milestones, accepted screenshots | Separate planned vs implemented vs verified statuses |
| `docs/test_checklist.md`, `docs/FEATURE_STATUS.md`, `docs/CHANGELOG.md`, `docs/DEVELOPMENT_HANDOVER.md`, `docs/next_step.md` | Record actual implementation phases, tests, commits, risks and next approved step, without duplicate source of truth | Do not claim Windows PASS from artwork previews |

**Optional new module:** `photobooth/meong_fly_theme.py` for named visual tokens, if refactoring makes painter/gui constants demonstrably easier to maintain. Avoid adding a new source file purely for decoration.

## 7. Execution batches (small reviewable commits)

### Batch A — Foundation and Scan/Start (P0/P1)

- Define shared spacing/palette/panel/button/type primitives in painter.
- Start logo proportions, premium coupon and differentiated CTAs.
- Scan framing, input spacing, error/focus/pressed states, subtle animated scan line; preserve input fix.
- Add source-level, layout and interactive Kivy tests.
- **Gate A:** both pages visually approved from Windows screenshots, demo code typed/validated, Back leaves receipt unused, and reusing a code fails.

### Batch B — Gameplay and space art (P1)

- Polish HUD, starfield, planets, parallax and consistent rock variants bounded by hitboxes.
- Logo-derived sprite/angle states, refined rainbow trail, score pop, impact feedback.
- Budget animations for real device FPS, no Kivy texture regeneration per frame.
- **Gate B:** screenshots/video at live score 0, midgame and near-obstacle show clear fair geometry; scores/triggers correct; Windows portrait and landscape responsiveness verified.

### Batch C — Win/Lose finishing and full regression (P1/P2)

- Victory burst/ticket/celebration, defeated Meong/score card/reassuring text.
- Button states, animation transitions, final microspacing, no retry pathways.
- Re-run all FEAT-021 tests; capture five on-device screenshots and final acceptance.
- **Gate C:** five-page look-and-feel owner accepted on Windows; full isolated game QA PASS; no production GUI integration.

Each batch must be reviewed, committed to **`feature/meong-flappy-challenge` only**, and documented with actual commit SHAs. Preserve a pre-batch SHA as rollback point. Do not invent test results or merge without authorization.

## 8. Acceptance matrix (release gate for visual polish only)

| ID | Scenario | Pass criteria | Evidence to record |
| --- | --- | --- | --- |
| VP-01 | Start at 450×900 | Logo whole, ticket and both CTAs aligned, no clipping | Windows screenshot + runtime SHA |
| VP-02 | Scan input | Click, caret, paste/type, Enter/Validate all work after repeated repaint | Windows screen/test output |
| VP-03 | Demo code | `DEMO-V2-001` accepted once and rejected after relaunch | Flow test + user observation |
| VP-04 | Back / skip | Back before claim preserves code; Direct Photo exits standalone | Test + observation |
| VP-05 | Gameplay visuals | Active Meong, moving asteroids, parallax and 10-score HUD visible | Active gameplay screenshot/video |
| VP-06 | Collision fairness | Rainbow does not hit; rock silhouettes do not protrude beyond collision boxes | Physics tests + slow manual collision QA |
| VP-07 | Pause | Freeze physics and prevent flap until resume | Unit + Windows UI |
| VP-08 | Win | Simulated Rp2.500 emphasized; no real checkout/redeem, no replay | Windows screenshot + flow test |
| VP-09 | Lose | Actual score, positive message, no voucher, no replay | Windows screenshot + flow test |
| VP-10 | Resize | 450×900 portrait, 800×600 and 1200×800 landscape; legible/unclipped and clickable | Screenshots + hitbox assertions |
| VP-11 | Stability | Animations visually smooth; resource usage stable; no text/caret vanishing | Operator FPS observation / optional profiling |
| VP-12 | Production isolation | No changed `master`, photobooth app, camera, printer or payment code | Git diff/compare verification |

### Test commands (on actual checked-out Windows branch)

```powershell
python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts tests.test_meong_fly_flow tests.test_meong_fly_painter tests.test_meong_fly_gui -v
python -m photobooth.meong_fly_demo
```

Also run the project's applicable regression suite when a batch modifies a shared module. Log the exact SHA, Windows and Python/Kivy/Pillow versions, pass/fail/skip totals, screenshots, and any visible defects. Earlier Step 3 QA does not transfer to this modified GUI.

## 9. Definition of Done and exclusions

**Visual polish DONE only when:** every screen meets the acceptance matrix; full page/object checklist is reviewed on Windows; all relevant isolated unit/GUI tests pass with recorded evidence; navigation remains correct with single-use receipts; both results have exactly one continue CTA and no retry; owner explicitly approves the final five screens. A polished visual alone is insufficient to claim functional or production acceptance.

**Still excluded after v2:** real merchant QR scan, POS integration, genuine Rp2.500 discounts, Midtrans/DOKU payment, cafe subsidy settlement, production photobooth welcome-screen integration, automatic photo flow, and any `master` merge. These require separate scope approval and testing.

**Historical status at first authoring:** this was initially a design-only specification. The dated Batch A and Batch B implementation records below supersede that historical statement; Windows Kivy verification remains pending.
## Batch A implementation record — 2026-10-21

This design document was authored before the code changes. **Batch A is now IN SOURCE on `feature/meong-flappy-challenge`**, but **not yet Windows GUI accepted**. The approved revised visuals are cacheable Pillow Start/Scan artwork in `photobooth/meong_fly_polish.py` (premium stepped cards, voucher, hero halo, scanner brackets, readable spacing and CTA palette) routed through `meong_fly_painter.paint_static_screen`. The Kivy standalone stage in `meong_fly_gui.py` adds a decorative scan sweep, text-field focus/error outline and desktop hover outline while keeping `canvas.before` (BUG-012 remains guarded). Physics, SQLite receipt policy, production kiosk GUI, Midtrans/QRIS and win/lose screens are not changed. No merge to `master`.

**Code commits:** `74bdef6a` (polished art), `cbc74372` (renderer integration), `f8bc996b` (Kivy scanner/focus/hover). **Test commit:** `05fccdd6` (pure Pillow layout checks). Local mirrored Pillow 7/7 PASS; Kivy is not installed in assistant's container, so **no Windows GUI / real text-entry pass can be asserted yet**. Run the exact feature branch `python -m unittest tests.test_meong_fly_polish tests.test_meong_fly_gui tests.test_meong_fly_flow tests.test_meong_fly_receipts tests.test_meong_fly tests.test_meong_fly_painter -v` and manual visual checks on Windows.

**Batch A gate:** Owner accepts Start and Scan screenshots and confirms input typing, Enter/click validation, Back without claim, and single-use receipt across restarts, at portrait and landscape. **Batch B and C remain design-only** until separately authorized or explicitly continued.


## 2026-10-21 — Batch B implemented: standalone Gameplay space art (NOT YET WINDOWS-VERIFIED)

**Authorization:** owner replied "OKE LANJUT" to Batch B after the Batch A report. The implementation was restricted to the `feature/meong-flappy-challenge` standalone mini-game. `master`, the photobooth welcome screen, camera, printer, audio, QRIS, real POS scanning and checkout remain unchanged. The existing approved rules (10-point target, one DEMO code = one play, no retry) remain binding. The earlier Batch A owner visual validation is still not recorded; approving the next code batch does not imply that gate was satisfied.

**In source:**
- `photobooth/meong_fly_game_art.py`: one cached 360×720 deep-space background with shared beveled HUD, layered nebula, spiral galaxy, ringed planets, three-depth star composition, the engine-aligned playing boundary, 5 deterministic RGBA asteroid tiles, 3 cosmetic poses derived from the unchanged approved logo crop, and shared math for the exact top-origin asteroid/cat hitbox rectangles. Commits `72658e55` and `1cea6794` (HUD target reads engine `TARGET_SCORE`).
- `photobooth/meong_fly_painter.py`: Gameplay background delegation to the new pure Pillow renderer; Start, Scan, Win and Lose design paths are preserved. Commit `b60c0d68`.
- `photobooth/meong_fly_gui.py`: preloads asteroid and pose textures only at stage construction (commit `a08952fd`), draws animated star depths, background comet, tinted rock belts with exact scored/collision box edges, a tapered waving five-color rainbow, tilt poses and compact in-game score HUD (commit `7b7b448a`); displays cached score +1 pop and a brief 220 ms impact before Game Over without changing `MeongFlyFlow` or receipt persistence (commit `ad4a2e49`). All live visuals are rendered on `canvas.before`, preserving BUG-012 child `TextInput` canvas safety.
- Regression tests: `tests/test_meong_fly_game_art.py` (`9ed6ab19`) for palette variants, cached canvas, sprite bounds and exact obstacle/cat geometry; `tests/test_meong_fly_gameplay_gui.py` (`f5349bef`) for no per-frame Pillow texture uploads plus optional Kivy gameplay, pause/score and impact checks.

**Actual execution evidence (local mirror, NOT exact GitHub checked-out branch):** Linux container Python 3.13.5, Pillow 12.3.0, Kivy unavailable. `PYTHONPATH=/mnt/data/meong_step4 python -m unittest discover -s /mnt/data/meong_step4/tests -p 'test_meong_fly_*.py' -v` -> **19 tests run: 15 PASS, 4 SKIP (all four require Kivy), 0 FAIL/ERROR**. `python -m compileall -q /mnt/data/meong_step4/photobooth /mnt/data/meong_step4/tests` -> **no errors**. Headless SQLite flow smoke: claim, pause, terminal loss, prevention of replay after restart all PASS. Rendered a sample static frame using a previous uploaded logo stand-in; it is **NOT** a Windows/Kivy live screenshot or the bundled official PNG. Exact GitHub SHA tests and actual Windows Kivy render/performance remain **PENDING**.

**Gate B — REQUIRED manual Windows evidence before visual acceptance:**
- [ ] Fetch latest branch; `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts tests.test_meong_fly_flow tests.test_meong_fly_painter tests.test_meong_fly_polish tests.test_meong_fly_gui tests.test_meong_fly_game_art tests.test_meong_fly_gameplay_gui -v` with actual exit/status and Python/Kivy/Pillow versions.
- [ ] Start -> Scan: input typing and validation still work; a demo receipt is consumed only once and cannot replay after loss, win or restart.
- [ ] Live Gameplay screenshots/video at Score 0, mid-score and near asteroid: approved camera-cat/lens visible; large body and rainbow separate; 5 textured rocks remain visibly inside a full tinted belt corresponding to exact physics boxes (not deceptive).
- [ ] Pause halts physics, resume works, +1 appears only on actual pass, 220 ms crash feedback never accepts a hidden result button or grants another attempt.
- [ ] Check 450×900 portrait and 800×600/1200×800 landscape Kivy letterboxing, pause hitbox, texture clarity and >=30 FPS on target Windows hardware; note device model and frame/touch behavior.
- [ ] Obtain owner acceptance for the live Gameplay look and fairness before Batch C release/polish signoff.

**Rollback:** revert the scoped Batch B commits from pre-Batch-B feature-branch baseline `c1498217c715b4a94a510e5395ea760842ab222e` (do not rewrite `master`). Visual-only changes must never be accepted as production-payment behavior. Batch C Win/Lose polish remains NOT STARTED in this pass.


## 2026-10-21 — Owner-provided Windows Kivy automated regression: **55/55 PASS**

The owner supplied the complete Windows test output for the eight FEAT-021 targeted test modules covering Batch A and Batch B. Result: **`Ran 55 tests in 6.272s` — `OK`**; **55 PASS, 0 FAIL, 0 ERROR, 0 SKIP**. Notably, the 4 previously skipped conditional Kivy Batch B GUI tests and the Kivy receipt-input tests executed and passed on the owner's machine.

**Observed environment in test log:** Windows, Python **3.12.10** (64-bit), Kivy **2.3.1** (SDL2 window provider), OpenGL **4.6** with **Intel Iris Xe Graphics**. The output includes successful tests for background/asteroid/sprite geometry, prepared GPU textures and displayed game screen, scoring/receipt ownership, pause/unpause, collision-result transition, interactive TextInput canvas integrity, hover and scan animation, SQLite single-use receipt persistence, pixel-art painter and Start/Scan visual geometry.

**Evidence classification:** owner-provided real Windows Kivy **automated** tests, not independently re-executed by the assistant. The pasted output does **not include the exact tested Git commit SHA**, Pillow version, manual gameplay screenshots, measured FPS, portrait/landscape visual review, or physical user acceptance of visual fidelity. Therefore the earlier "Windows automated tests pending" gate is now **SATISFIED at reported environment level**, while **manual UI appearance and input experience, collision fairness in gameplay, resizing, frame rate and owner aesthetic approval remain OPEN**. This does not authorize Batch C coding or `master` merge. See [Windows QA checklist](../test_checklist.md).
