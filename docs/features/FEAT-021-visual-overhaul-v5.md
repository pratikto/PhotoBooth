# FEAT-021 — Meong Fly Visual Overhaul v5: Canonical Audit and Implementation Specification

> **Current as of 2026-10-21 · DOCUMENTATION / PROPOSAL ONLY · NOT IMPLEMENTED v5**
>
> **Repository:** [pratikto/PhotoBooth](https://github.com/pratikto/PhotoBooth)  
> **Sole working branch:** `feature/meong-flappy-challenge` (no new branch)  
> **Audited source baseline:** `85a6aaa99356f3825067dfc5b92c6f91933d8519` (feature branch HEAD before this documentation-only audit)  
> **Stable branch:** `master`; immutable source release `v1.0.0`; do **not** merge or modify either without separate approval.  
> **Lifecycle:** FEAT-021 IN PROGRESS; standalone gameplay/navigation/visual v4 IN SOURCE; **visual fidelity NOT ACCEPTED**; v5 redesign **SPECIFIED, NOT AUTHORIZED FOR CODE**; production integration **NOT AUTHORIZED**.  
> **Visual reference:** Owner-provided 2026-10-21 five-panel neon pixel-art space poster plus the four-stage strip showing Meong printing an instant photograph; reference was supplied in conversation, **not** committed to the repository as a design asset.
>
> **Reading order:** this file is the **current design/visual-audit source of truth**; [FEAT-021 engineering history](FEAT-021-meong-fly.md) preserves commits and old tests; [v2 specification](FEAT-021-visual-polish-v2.md) is historical; the [v5 QA matrix](../qa/FEAT-021-visual-v5-acceptance.md) owns the detailed acceptance evidence. A documentation specification is not evidence of a functioning UI.

## 1. Executive finding and scope boundary

The existing application implements a **standalone** Kivy mini-game with Start, demo receipt entry, Gameplay, Win, Lose, a one-time standalone tutorial and a **generic** 12-layout preview. The source already contains a space-themed pixel UI, camera-cat assets, a 10-point target, receipt replay prevention and an updated camera-anchored instant-film emitter. **This is not the same as matching the latest poster.**

The owner explicitly rejected the appearance of the most recent build and asked for an object-by-object audit. The audit found unresolved weaknesses in type hierarchy, title styling, asset fidelity, visual density and polish, camera/film alignment, sprite compositing, asteroid silhouette/fairness and result-screen expressions. **No actual post-v4 Windows Kivy screenshots, side-by-side v4 footage, measured FPS, or owner's aesthetic sign-off were provided.** Source-confirmed behavior and risks are recorded separately from unverified on-device artifacts.

**In v5 scope, if later approved:** artwork and renderer improvement in the *same* standalone mini-game branch, reproducible assets, animation refinements, typography, performance, visual regression coverage and accompanying docs. **Out of scope:** production `ui_kivy.py`/welcome-screen integration, real camera or thermal print, approved 12 thermal-template replacement, merchant POS receipt scanning, QRIS, real discounts or settlement, new game attempts, commercial terms and any merge/release.

## 2. Binding owner decisions — do not reinterpret the poster literally

| Decision | Binding interpretation | Current implementation |
| --- | --- | --- |
| Brand | Gray Meong camera-cat, **large blue camera lens**, face/pink cheeks, rainbow trail; **never** a cat riding a rocket | Latest GIF-derived bundled crop exists; visual consistency still needs audit |
| Theme | High-quality retro **pixel-art neon arcade in outer space**, navy/purple/pink/cyan/yellow, planets, galaxies, asteroid field | Thematic elements exist but poster-level art polish is missing |
| Entry | Start: `MAIN GAME` or `LANGSUNG FOTO`; playing requires receipt validation | Standalone paths exist |
| Receipt | **One unique valid cafe receipt = one attempt, no replay after win, loss, back, or restart** | Only atomic SQLite **`DEMO-...`** tokens, NOT real cafe receipt validation |
| Target | **Score 10** for simulated win; one 25-second round | Engine has `TARGET_SCORE=10`, `ROUND_SECONDS=25` |
| Terminal screens | Win: discount **Rp2.500** (simulation only). Lose: no discount. **No `MAIN LAGI`** on either | Source implements demo result states, no retry |
| Destination | Both results use **`PILIH LAYOUT FOTO`**, never payment; `LANGSUNG FOTO` shares the photo path | Standalone tutorial/layout-preview route exists |
| Tutorial | Show the tutorial once if not previously viewed, **before** layout selection | Standalone marker `~/.meong_fly_tutorial_seen`; not linked to production tutorial |
| Layouts | Production will preserve **12 approved thermal vertical layouts**, 80×240 mm / 640×1920 px, three photos vertically and Google Drive folder-download QR at bottom | Standalone shows **12 generic preview cards**, not the actual template assets or print-ready output |
| Delivery boundary | Finish standalone polished mini-game and obtain approval **before** suggesting integration | No production integration approved; keep `master` untouched |

The attached mockup contains visual wording that is **superseded by later owner decisions**. In particular, any mockup button labeled `LANJUT KE PEMBAYARAN` must be `PILIH LAYOUT FOTO`; no sample `MAIN LAGI` must be shipped. The decorative scan QR is **not** a real scanner, and the result voucher is **not** a monetary entitlement. Do not present these limitations as bugs.

## 3. Evidence classification and audited source

| Evidence class | What it supports | What it does NOT support |
| --- | --- | --- |
| **Source inspected on feature branch** at baseline SHA above | Methods, constants, asset paths, source-level drawing order, one-use demo flow, renderer responsibilities | Exact Kivy output, interactive performance, collision feel or aesthetic acceptance |
| **Owner's neon five-panel image** and animation storyboard | Desired visual art direction, expressive character, layout/typography treatment, four-stage physical print behavior | A pixel-perfect functional GUI or implementation approval for payments |
| **Earlier owner's real Windows report**: Step 3 6/6 GUI manual PASS | Historical prior renderer behavior | v4/v5 visual sign-off |
| **Earlier owner's Windows automated output**: 55/55 PASS, Python 3.12.10 / Kivy 2.3.1 / Iris Xe | Targeted Batch A/B tests **at that earlier checkout** | Latest v4 print renderer correctness; exact SHA and physical FPS were not recorded |
| **Earlier owner's partial output**: 23/23 PASS in 1.789 s | Three targeted handoff/flow/painter modules at that earlier checkout | Full poster v3/v4, current Kivy frame quality |
| **Earlier assistant local-mirror print checks**: 10/10 behavior PASS | Deterministic emitter-model sanity | GitHub HEAD tests, physical slot alignment, new frame rendering on Windows |
| **Current v5 documentation work** | Traceable specification and reproducible proposed test plan | New GUI/art/code changes or a passing test run |

Audited files and their current responsibilities:

| File | Existing responsibility | v5 planned treatment |
| --- | --- | --- |
| `photobooth/meong_fly.py` | 480×640 physics, 25-second cap, rectangular asteroid-gap collisions, score 10 | **Protect**: any collision/physics change needs a separately scoped review |
| `photobooth/meong_fly_flow.py` | Receipt claim, one attempt, pause, win/loss, tutorial/layout handoff | **Protect**: no replay/reset/discount changes |
| `photobooth/meong_fly_receipts.py` | SQLite demo receipt ledger; persisted claim/result | **Protect**: never transform demo tokens into POS verification |
| `photobooth/meong_fly_demo.py` | Standalone Kivy entry point | Retain; do not import production kiosk workflow |
| `photobooth/meong_fly_gui.py` | Kivy background textures, input, hitboxes, live sprites, print emitter, screen changes | Refactor composition and introduce testable coordinate system if approved |
| `photobooth/meong_fly_painter.py` | Pillow logical canvas (360×720), bitmap text, action geometry and screen delegation | Introduce coherent style API and typography; keep hitbox mapping accurate |
| `photobooth/meong_fly_polish.py` | v2 Start/Scan materials, scanner illustration | Retain useful shared visual primitives; avoid duplicated bespoke styles |
| `photobooth/meong_fly_game_art.py` | Gameplay background, HUD, five rock textures, three cat poses, hitbox mapping | Rework obstacle appearance/legibility without secretly changing physics |
| `photobooth/meong_fly_visual_v3.py` | Current Start/Win/Lose poster painter, GIF-frame fallback, film sprites/reveal frames | Replace placeholder compositing with deliberate layered asset/art pipeline |
| `photobooth/meong_fly_print_fx.py` | One camera-anchored feed → release → gravity model | Preserve state machine; make print-mouth registration exact |
| `photobooth/meong_fly_photo_handoff.py` | Generic tutorial and 12 illustrative preview buttons | Keep demo-only; not actual production layouts |
| `photobooth/assets/meong_fly_gif_logo.b85` | Latest owner GIF-derived small still image encoded in text | Asset fidelity baseline; NOT the complete animated GIF |
| `photobooth/assets/meong_photobooth_vivid.png` | Older official logo file/fallback | Do not silently use as current brand hero when new one exists |

## 4. Screen-by-screen v5 audit, object inventory and target design

**Interpretation:** “IN SOURCE” denotes an implemented component, not aesthetic approval. “MISMATCH” is a documented difference from the latest supplied poster or a user-reported visual dissatisfaction. “SOURCE RISK” is technically plausible but requires Windows screenshot/video verification. All target changes below are **proposed**, not already coded.

### 4.1 Start — retro arcade brand, minimal text

**Current objects:** star/planet/asteroid background, camera-cat hero, synthesized bobbing, printed photo effect, large `MEONG`/`FLY!` bitmap title, `HINDARI ASTEROID!` subtitle, Rp2.500 demo ticket, pink `MAIN GAME`, cyan `LANGSUNG FOTO`, one-line demo warning.

**Gaps:** poster has an expressive outlined/glowing logo-title and detailed foreground/background cohesion, while the source primarily paints thin enlarged 5×7 bitmap glyphs and simple stepped panels; hero artwork can overlap a separately animated copy. Typography is not a purpose-made outlined arcade font. The print source is approximated and the visible paper may not align with the real outlet. The poster's graphic richness should not become text clutter.

**Target per object:**

1. **Space background:** rich but subdued stars/galaxies, two or three depth layers; edge decoration supports rather than obscures hero/CTA. Keep star movement low-cost.
2. **Hero:** ONE current camera-cat composition; visible blue lens, gray cat, clean rainbow, no black legacy wordmark, correct pixel aspect ratio; no static/dynamic duplicate.
3. **Flying motion:** restrained looping bob/small tilt; camera moves as one rigid sprite with physically registered film outlet; no screenshot replacement masquerading as a control.
4. **Title:** prominent **MEONG FLY!** as bold multi-layer pixel-art lettering (light fill, dark contour, selective cyan/gold accent and short pixel-shadow), easily legible in kiosk size.
5. **Instruction:** **HINDARI ASTEROID!** only, not several lines of explanatory paragraphs.
6. **Reward:** compact yellow ticket; **DISKON Rp2.500** as the clear second focal point; small but legible **SIMULASI** notice.
7. **Buttons:** primary bright pink **MAIN GAME**, secondary cyan **LANGSUNG FOTO**; matching heights/icons, hover/pressed states and actual hitboxes.
8. **Film:** show physically connected paper emerging from Meong, not loose paper around the whole page. Restrict motion to the hero zone.

**Acceptance:** one glance reveals brand → purpose → promotion → decision; no overlapping glyphs, paper/titles, hidden controls or legacy brand content at 450×900 portrait and required landscape windows.

### 4.2 Scan Struk — clear demo validation, not a fake functional scanner

**Current objects:** title, decorative QR square, scanner corners/beam, demo-only warning, real Kivy `TextInput`, `VALIDASI DEMO 1X`, `KEMBALI`, background planets.

**Gaps:** reference has stronger title framing and polished luminous corners; code is fairly plain and uses small bitmap text. GUI input in the past was broken by a canvas-clear regression (**BUG-012**), now fixed at source with `canvas.before`, but every visual refactor must preserve actual typing.

**Target per object:**

1. **Header:** short high-contrast two-line **SCAN STRUK KAFE**, consistent with main-title palette.
2. **QR illustration:** central light panel with crisp checker/grid, four neon scanner brackets, subtle animated beam, and unambiguous **QR ASLI BELUM TERHUBUNG** label. Do not pretend a camera, decoder or POS actually works.
3. **Input:** authentic editable Kivy field with readable font, caret, placeholder `DEMO-123`, focus/error ring and keyboard focus; do not paint fake text over it.
4. **Validation:** one prominent pink CTA, only actually consume a demo code on explicit validation; `KEMBALI` never claims receipt.
5. **Margins/background:** align QR, text, input and both buttons; never crowd bottom decorations into click targets.

**Acceptance:** owner can type/paste and submit, a used code fails after restart, focus/caret remains visible after redraw, scanner beam is cosmetic and does not block touch.

### 4.3 Gameplay — visual clarity first, lively space second

**Current objects:** Pause, SCORE, TARGET 10, asteroid-gap fields, five color variants of 64×64 asteroid texture, camera-cat crop/three tilt poses, waving rainbow, parallax stars, nebula/galaxy/planets, `+1` sparkle and brief loss effect.

**Gaps:** poster depicts visually separate large, expressive asteroids and clearly identifiable Meong; source draws **narrow repeated rock tiles inside tinted rectangular collision belts**. Geometry is honest in code but does not resemble scattered asteroid clusters. Character can look too small/flat versus the target. Scenery density may compete with actual obstacles and print sheets. The “printed photos” must not look like hazards.

**Target per object:**

1. **HUD:** consistent illuminated panel family; pause button visually distinct and accessible; SCORE and TARGET readable at a glance without hiding an asteroid.
2. **Meong:** latest approved camera-cat with recognizable large blue lens; correct collision-sprite relationship; readable at game speed; cosmetic tilt does not lie about physical collision area.
3. **Rainbow:** vivid but thinner than camera body, five recognizable color stripes, smooth wave/taper, no effect on hitbox.
4. **Asteroids:** differentiated silhouette, craters, shading, size/rotation/placement; keep the full **actual** collision region visually communicated. Do **not** make a hidden solid rectangle look like isolated small rocks without corresponding collision review.
5. **Background:** animated parallax with low/mid/high brightness layers, planet orbit and restrained nebula; quiet visual corridor around Meong and obstacles.
6. **Printed instant photo:** tiny, occasional, distinguishable from asteroid and collectible; emerge at real camera slot; fall behind/away without masking gameplay.
7. **Score cue:** compact +1 near camera after legitimate pass; no reward for near-miss or touch.
8. **Pause/crash:** pause freezes simulation/film, clear resume; brief crash effect before Game Over, no hidden click-through.

**Acceptance:** user can identify target, read score, see true gaps and distinguish camera/asteroid/print sheet at speed. Screenshot at score 0, passing obstacle and near collision; video of 10–15 s gameplay; test true collision boundaries.

### 4.4 Win — delightful but unmistakably demo-only

**Current objects:** `SELAMAT!` bitmap heading, radial lines, normal camera-cat asset, simulated Rp2.500 ticket, **PILIH LAYOUT FOTO** CTA and one-print animation.

**Gaps:** source uses simple lines and flat large type; poster has curved/layered dimensional lettering, bright starburst, real celebratory cat pose and stronger placement of the printed film. GIF-derived asset alone does not make a celebration.

**Target per object:** (1) oversized gold `SELAMAT!` with deep outline and rim light; (2) one clear, happy camera-cat/rainbow hero; (3) controlled flare/sparkle behind hero, not over CTA; (4) physical print-outlet effect, at most one sheet; (5) readable yellow reward ticket `DISKON Rp2.500` and `SIMULASI`; (6) cyan **PILIH LAYOUT FOTO** as only terminal action.

**Acceptance:** no real discount claim, no replay, no payment button, CTA moves via tutorial gate to demo layouts; result does not leave “printing” particles on the next page.

### 4.5 Game Over — cute, not punitive

**Current objects:** pink `GAME OVER`, nearly same normal camera-cat image as Win, score card with real score, short reassurance, one `PILIH LAYOUT FOTO` CTA.

**Gaps:** mockup shows Meong's eyes as **X / tired expression**; current renderer does **not** generate that alternate character face. Title is not equivalent to outlined glowing 3D lettering, and the result composition is comparatively flat.

**Target per object:** (1) dramatic but readable pink `GAME OVER`; (2) recognizably the same camera-cat with intentional defeated expression (X eyes), not an unrelated mascot; (3) subdued space accents/asteroids; (4) score **N/10**, no overlap with SCORE heading; (5) kind message **TETAP BISA FOTO!** and **TANPA DISKON**; (6) one cyan **PILIH LAYOUT FOTO**, never `MAIN LAGI`. No new film emitter on this terminal page.

**Acceptance:** correct score and no simulated discount in loss, correct navigation and no retry, legible from the expected kiosk viewing distance.

### 4.6 Tutorial and twelve-layout demo preview (outside five-panel mockup, but in real navigation)

This is an **extra, existing** standalone route. Preserve tutorial-first-if-unseen, readable numbered guidance, generic 12 selection cards and no actual print/payment/camera call. When production integration is separately approved, this **generic** selector must be replaced/routed to the **12 real approved** thermal templates with 3 vertically stacked photos and the bottom Google Drive **download QR** (distinct from POS validation and QRIS). The current selector merely exits the standalone demo on selection; do not claim it opens the production photo capture UI.

## 5. Shared visual system — proposed v5 design contract

- **Logical Kivy stage:** 360×720 portrait, top-origin Pillow/Kivy coordinate mapping; preserve proportional letterboxing for desktop landscape. Keep every visual CTA aligned to shared `ACTIONS` and `DEMO_ENTRY` hitboxes.
- **Design reference:** high-contrast pixel-arcade outline, dimensional typography and layered stars seen in owner's poster, *not* a flat Pillow approximation or a static image with inert hotspots.
- **Color tokens:** deep navy `#050C2F`; panel `#0B1543`; white `#F8F8FF`; pink `#FF55AB`; cyan `#58D1FF`; gold `#FFDC78`; purple `#B385FF`. Proposed secondary neon edges and shaded ramps must pass manual visual review; never depend on hue alone for game state.
- **Typography:** distinct display/title, action, information and fine-print levels. Prefer a newly approved pixel display typeface or locally bundled, legally compatible rendered glyph atlas rather than thickening every 5×7 bitmap letter indiscriminately. No font asset is authorized/committed by this document. Avoid fine-print below comfortable screen readability.
- **Panel/button materials:** systematic outer black contour → neon stroke → main fill → top highlight → lower pixel shadow. Same material across Start, Scan, results and HUD; buttons must have visible pressed, focused and disabled states.
- **Sprites:** nearest-neighbor filtering, crisp pixel alignment, bounded outlines and **aspect-preserving** scaling. Default renderer should not create full-resolution Pillow images per frame.
- **Depth:** keep background visually rich but maintain a low-clutter central gameplay lane. Decorative UI/photos cannot cover input, result CTA or Pause/SCORE/TARGET.
- **Accessibility:** white/cyan/gold readable against navy/panel; primary CTA always high contrast; input caret/focus clearly visible. Validate at minimum 450×900 portrait and 800×600/1200×800 landscape, with physical keyboard and pointer.

## 6. Physical instant-camera printing: required storyboard and contract

**The desired visual is a real-looking instant camera, not confetti or a shower of polaroids.** There is exactly one source of paper creation. The 2026-10-21 owner storyboard has four phases:

| Stage | Must be visible | Geometry/lifecycle rule |
| --- | --- | --- |
| 1. Flying idle | Camera-cat moves through space with rainbow; slot is physically identifiable below/in the instant-camera body | Camera pose transforms sprite and anchor together |
| 2. Feeding | A slim strip **emerges from the slot**, visibly grows and displays photo content gradually, still attached | One local slot coordinate per sprite; masking/reveal, no detached sheet yet |
| 3. Fully extended | Printed film becomes a recognizable cat instant photo, still at the same slot for a moment | Attach/detach boundary stable even while camera moves |
| 4. Release and fall | Sheet detaches once and drops downward with small sway, while Meong can fly elsewhere | Freeze release position in logical screen/world coordinates; gravity, no random reposition |

**Source now:** `InstantPhotoEmitter` has `INITIAL_DELAY=0.62s`, `FEED_SECONDS=0.42s`, `INTERVAL=2.15s`, `MAX_SHEETS=2`, deterministic gravity and max approximately 4 logical-pixel sway, and a pause-aware update. These values describe *current code*, **not a v5 approval** of animation timing or aesthetic quality.

**Source-level issues requiring v5 attention:**
1. `paint_poster_screen()` already paints the hero on the static Pillow texture, while Kivy `_paint_hero()` draws another animated copy on top. This is a **confirmed duplication in draw paths**, with visible ghost/overlap a **runtime verification item**. v5 should have one authoritative hero renderer per scene.
2. `_printer_context()` calculates an outlet with relative constants (e.g., `x + w*0.53`, `y + h*0.78` for results/Start, and `0.42`/`0.87` in Gameplay). They are **estimated anchors**, not an asset-authored slot attachment point; v5 should define a tested anchor in camera local pixel coordinates and transform it consistently through scale/pose.
3. Eight `photo_feed_frames()` stages reveal pixel rows, but the Kivy sheet is drawn at a fixed rectangle. v5 needs an actual **slot aperture/mask**, so exposed film grows *outward* rather than appearing as a clipped picture pasted below the camera.
4. `meong_animation_frames()` reads only the **first frame** of an optional full GIF to avoid duplicate paper, then synthesizes hover frames. **Do not claim full original GIF playback**. Latest owner still is present in `meong_fly_gif_logo.b85`; 26 original animation frames are not bundled.
5. `printed_photo_tile()` is a generic 32×41 pixel cat polaroid, not a real captured photobooth picture. Preserve privacy: demo artwork only.
6. Paper must not spawn at screen-random coordinates, multiply uncontrolled, affect hitboxes, behave as collectibles, block the demo input/HUD/buttons, or survive a transition into Scan/Tutorial/Layouts/Lose.

**Proposed v5 art implementation:** author one clean camera-cat sprite with explicit slot coordinates and distinct Win/Lose expressions; feed through a pre-rendered 8–12 frame film mask or lightweight Kivy clipping; composite film **behind** the foreground camera body and **above** the rear slot shadow; pin the film during feed; release at exact physical location; fade at scene-safe boundary. Test geometry with screenshot/video pairs, including moving Meong during print. If the owner later supplies the original complete animation asset, treat its frame sequence as a reference, not an automatic extra emitter.

## 7. Prioritized visual gap register

| ID | Priority | Evidence now | Gap / proposed correction | Validation gate |
| --- | --- | --- | --- | --- |
| VF-01 | P0 | Confirmed source layering | Duplicated static + dynamic Start/Win hero; select single rendering owner | Compare frames with/without bob; zero ghost silhouette |
| VF-02 | P0 | Confirmed source constant | Estimated film-slot anchor; define local asset coordinate | Film originates at slot within visual tolerance set in QA |
| VF-03 | P0 | Source + owner dissatisfaction | Print looks pasted/unnatural despite emitter lifecycle; add proper slot mask/depth | Four storyboard states accepted on actual video |
| VF-04 | P0 | Owner visual feedback | Thin/unstyled display font | All main titles, buttons and information legible in UI screenshots |
| VF-05 | P1 | Poster-to-source audit | Start layout/title still flat, not visually equivalent | Owner screenshot comparison passes |
| VF-06 | P1 | Source scan renderer | Scanner frame/title/light hierarchy not equivalent | QR disclaimer and real text entry remain clear |
| VF-07 | P1 | Confirmed source mapping | Camera-cat size/silhouette/detail do not reach poster character treatment | Legible blue lens & fair sprite bounds at speed |
| VF-08 | P1 | Confirmed source rock belts | Repeating rectangular asteroid columns not similar to poster | Asteroid art + honest collision silhouette |
| VF-09 | P1 | Source background | Space depth/nebula/rich glow hierarchy too primitive | Gameplay readable while background feels layered |
| VF-10 | P1 | Source Win painter | Basic rays/text rather than cinematic celebration | Gold title, controlled rays, expressive cat |
| VF-11 | P1 | Source Lose painter | Lacks distinct defeated/X-eye pose | Cute X-eye result and correct score, no retry |
| VF-12 | P1 | Source flow vs poster | Generic tutorial/layout vs actual templates | Clearly labelled demo-only; no production claim |
| VF-13 | P1 | BUG-012 history | Kivy redraw may erase TextInput if parent canvas is cleared | Real typing/caret/paste + automated redraw test |
| VF-14 | P1 | Untested latest v4 | Physical FPS, resize and touch hitboxes unverified | Windows test report at exact commit |
| VF-15 | P2 | Source asset packaging | Bundled still vs 26-frame GIF discrepancy | Correct attribution; owner approves final motion |
| VF-16 | P2 | Source UX | Particle/sky density vs distraction and motion comfort | No CTA/HUD/input obstruction |

**P0/P1 above are priorities within FEAT-021 visual acceptance**, not a reprioritization of the production operational backlog. The feature itself remains a P2 product enhancement; BUG-001/007 and BUG-009 operational work is not silently deprioritized.

## 8. Proposed v5 execution phases (code work NOT AUTHORIZED by this spec)

| Gate | Deliverable | Proposed modules | Approval and regression |
| --- | --- | --- | --- |
| **V5-0** | Freeze reference poster, approved latest GIF/frame and one set of cropped hero/slot coordinates; before/after screenshots | Asset/source inventory + design tokens | Confirm source asset provenance and license; doc/design approval |
| **V5-1** | One authoritative hero renderer; physically masked/anchored print film; clean 4-stage animation | `meong_fly_visual_v3.py`, `meong_fly_gui.py`, `meong_fly_print_fx.py` | Preserve one-attempt flow, test exact slot at multiple camera positions; Windows animation clip |
| **V5-2** | Shared neon panel system, bold display text and redesigned Start/Scan | `meong_fly_painter.py`, `meong_fly_polish.py`; candidate asset atlas | Before/after Start/Scan screenshots, TextInput/BUG-012 regression |
| **V5-3** | Gameplay sprite/space/obstacle visual fidelity and fairness, HUD, parallax | `meong_fly_game_art.py`, `meong_fly_gui.py` | Obstacle visible/collision mapping, pause, score, FPS, landscape |
| **V5-4** | Win/Lose expressiveness, payout disclaimer, no retry, tutorial/layout continuity | Visual painter, sprite states and optional cue textures | Win/Lose outcome tests and owner visual sign-off |
| **V5-5** | Full standalone cross-screen regression, evidence, rollback-ready comparison | Tests/docs only unless separately approved fix | Exact-commit Windows logs/video, owner approval before any integration discussion |

Each phase must be separately scoped and reviewable on the **existing** branch. **No source implementation is authorized by the present documentation request.** Preserve app changes already working; never rewrite/force-push this historical feature branch. The earliest priority after authorization should be **V5-1** because unconvincing camera printing was the user's most recent blocking complaint.

## 9. QA, performance and Definition of Done

See the [standalone v5 acceptance matrix](../qa/FEAT-021-visual-v5-acceptance.md). Minimum evidence:

- Exact tested `git rev-parse HEAD`, Python/Kivy/Pillow/Windows/GPU information, command and PASS/FAIL/SKIP counts.
- Static screenshot of **all five** states plus tutorial and 12-layout preview, at real Windows Kivy rendering (not Pillow-generated poster).
- Short actual 30 FPS or better (proposed baseline; measure on target machine) video recording of camera hovering, film partially fed, fully fed, released and falling *without* ghost or teleport.
- Start/Scan UX: real keyboard typing and back/validate, button hitboxes, visual focus, no overlapping fine print; BUG-012 regression.
- Engine/flow: 10-point target, collision fairness, pause, win/loss, persistent one-use SQLite token, no `MAIN LAGI`, no real discount or QR functionality.
- Portrait/landscape: 450×900, 800×600 and 1200×800 (additional actual kiosk screen size if different), nearest-neighbor art without distortion; test pointers.
- Owner explicitly judges **the real live result** against the submitted poster and approves all four print-motion frames. Historical green tests are retained, **not substituted**.

**Definition of Done for v5 visual-only:** source implemented on existing feature branch; clean repeatable asset/art provenance; tests run on exact revision; all P0 visual gaps closed; no S1/S2 standalone blockers; user accepts real Windows screenshots/video; new findings documented with commits; rollback target recorded. **This is NOT a production release or permission to merge.**

## 10. Risks, dependencies and rollback

| Risk | Mitigation |
| --- | --- |
| Duplicate hero layering/black halo from GIF transparent pixels | One compositor, known alpha mask, single frame owner, capture transparency test |
| Camera slot misaligned after resize/tilt | Local normalized slot anchor transformed with pose/scale; pixel-accurate tests |
| Paper hides hazards or looks collectible | Limit count, dedicated z-order, small gameplay size, absence from collision/score |
| Background richness harms performance | Cache textures, cap particles, avoid per-frame Pillow/GIF decoding, profile FPS |
| Fonts too heavy/small for kiosk | Legibility hierarchy + screenshots at smallest window and actual display |
| Obstacle art unfair compared with physics | Preserve clearly shown solid collision region or obtain separate approval to revise hitboxes |
| Regression of BUG-012 | Preserve `canvas.before`; real editable Kivy input and redraw/focus tests |
| Device/session-state leak | Emitter scene reset, pause freeze, one-use demo ledger persistent; no production session writes |
| Inadequate evidence | Record exact SHA, dated screenshots/videos, machine specs, before/after comparison |
| Old visual design historical contradictions | Retain v1–v4 as dated history, point all current docs here |

**Rollback, if/when v5 code is separately approved:** record the exact branch HEAD immediately **before each** v5 phase; use scoped `git revert <commit>` or an approved targeted rollback on feature branch only. **Never rewrite** existing history or touch `master`; camera/receipt/demo assets must be preserved. The audit baseline for this document is `85a6aaa99356f3825067dfc5b92c6f91933d8519`, **not** a promise that it remains the newest commit after docs changes.

## 11. Unresolved items and approval checkpoint

- **Open:** owner visual acceptance of v4 Start/Game/Win and full poster gap comparison, physical FPS, exact post-v4 Windows regression, precise outlet coordinate, future UI asset format/display font, defeated sprite artwork, whether full 26-frame GIF should be imported or recreated as individual alpha sprites.
- **Known accepted behavior:** one attempt per unique receipt in future; demo-only codes today, no retry; score 10, tutorial once, layout after game, thermal template reference unchanged, no real payment.
- **Proposed next implementation:** V5-1 hero/compositor + physical print slot **only after explicit owner permission to change code**. Approval to update these Markdown files does not authorize v5 application-code edits, deploying or merging.
- **Document ownership:** status in [FEATURE_STATUS.md](../FEATURE_STATUS.md); binding decisions in [DECISIONS.md](../DECISIONS.md); defects in [bug_tracker.md](../bug_tracker.md); prioritization in [next_step.md](../next_step.md); actual tests in [test_checklist.md](../test_checklist.md) and [QA matrix](../qa/FEAT-021-visual-v5-acceptance.md); commits in [CHANGELOG.md](../CHANGELOG.md).

## 12. Related links

- [Engineering timeline and earlier commits](FEAT-021-meong-fly.md)
- [Historical Visual Polish v2 proposal](FEAT-021-visual-polish-v2.md)
- [Canonical QA/visual acceptance matrix](../qa/FEAT-021-visual-v5-acceptance.md)
- [Decisions](../DECISIONS.md) · [Bug tracker](../bug_tracker.md) · [Current feature status](../FEATURE_STATUS.md)
- [Protocol](../DEVELOPMENT_PROTOCOL.md) · [Development handover](../DEVELOPMENT_HANDOVER.md)

**No v5 source implementation or Windows v5 test result is claimed by this document.**
