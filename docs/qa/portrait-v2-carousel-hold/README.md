# Held-drag carousel neighbours — 27 October 2026

Owner supplies two Windows screenshots: dragging/holding left or right leaves
an empty side instead of revealing the next neighbouring strip. Exact device
HEAD is unknown. Base/rollback **e507fa3df89b53e06427b68ef4bdd37be4bb87e9**;
required branch feature/portrait-kiosk-v2-next, clean workspace and matching
remote HEAD verified before work. Source reproduces the missing incoming image.
This is BUG-019 (S2): restore the existing gallery contract, not a new feature.

Before code, reviewed AGENTS, README/index/protocol/current handover, feature/
bug/backlog/test status, architecture/technical design, decisions/specification/
visual contract and branch audit, plus original gallery-focus, motion-correction
and responsive-scene QA. Reused the current StripCarousel, five pooled Images,
slot interpolation/animation, master artwork, preview worker and texture cache.
The earlier gallery source 5a568bf already intended a five-image motion pool;
no alternate gallery or v1 UI port is needed. All archive contents stay excluded.

## Cause and correction

The widget allocated five image slots, but _settle populated only the middle
three and cleared the two outer textures. The application likewise supplied
only previous/current/next. An outer image received a texture only in show after
pointer release, so it was blank during a held drag. Earlier motion tests checked
movement/one selection but did not require the newly exposed picture to exist.

The application now supplies the cached five-picture window (two neighbours on
either side). _settle keeps all five textures; the outer slots stay transparent/
outside the stencil at rest. While dragging or reversing, the same cached
neighbour enters through the existing slot interpolation. Release animates the
old five-picture window, then rebases to the new selection without changing the
incoming image. Widgets are still pooled, with no per-move allocation/decode.
A cold first gallery can prepare up to five previews instead of three; existing
idle/worker warmup and cached navigation remain unchanged.

Selection/caption commits once on valid release. Quantities, quote, one-cue
input, short/vertical rejection, secondary-touch admission, rapid arrow replacement,
resize/minimize/retirement cancellation and the twelve 1:3 designs are preserved.
No Drive/QR/upload/retry, payment, camera, printer or Apps Script change.

## Local reproduction and checks

Two new native tests fail on the unmodified runtime: **121 failed subtests/cases
across two tests**, zero errors (120 held-drag combinations plus reversal).
They check actual MotionEvent input, the incoming picture and viewport intersection
before release, not just offset arithmetic. After correction, the strengthened
frame-settled test also requires the pointer to remain held through two native
render turns. All 12 designs × both directions × five viewports are covered:
800×1280, 452×900, 390×736, 360×640 and 800×600, including wraparound.
Reversal before release, unchanged quantity/selection while held, a single release
commit and the same incoming image through release are checked too.

Three focused native cases PASS, zero skips/failures/errors, 14.814s:

```text
python tools/run_kiosk_unittests.py test_kiosk_v2_widgets.PortraitKivySmokeTests.test_held_carousel_drag_reveals_correct_incoming_neighbour_before_release test_kiosk_v2_widgets.PortraitKivySmokeTests.test_held_carousel_can_reverse_direction_without_empty_neighbour_or_extra_selection test_kiosk_v2_widgets.PortraitKivySmokeTests.test_advert_game_invitation_tutorial_and_real_12_strip_gallery
```

An existing smoke case expected three initially loaded textures and four after
one navigation; it now expects five then six while still asserting that only
one new preview is loaded per step. Its other behavior assertions are retained.
Two preliminary focused runs exposed those two old cache-count assumptions;
no behavioral case was removed. Final additional motion/full/CI evidence follows.

Native FBO screenshots use the actual app, MotionEvent begin/update/reverse/end
and render turns. Early scratch captures were rejected because they were taken
before deferred image/label rendering or without valid pointer ownership; final
captures require correct held state, offset and exact neighbour texture. This
fixture correction changes no production input handler or GUI pixels. Screenshots
are layout evidence, not a Windows touchscreen/frame-pacing acceptance claim.

## Update and short owner check

Close the GUI, keep the existing checkout/environment/data/configuration:

```powershell
git status --short
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
python tools/run_portrait_v2.py --drive
```

Keep the operator's existing launch flags; --drive above matches current use
with printing deliberately disabled. No Apps Script update/redeploy is needed.

1. Hold a horizontal drag in each direction: the newly entering side strip is
   visible before release, and the caption/selection changes once on release.
2. Reverse direction without releasing, then release; check the correct neighbour
   and one selection. Quantity and price must stay unchanged by the gesture.
3. Swipe across the first/last template; verify the wraparound neighbours. Check
   an arrow tap and resize/minimize during a drag retain existing cancellation.

No new twenty-cycle report is required. Actual Windows pointer/touch and Ubuntu
mini-PC acceptance remain separate. Roll back via a scoped inverse source change;
preserve all customer images, counters, claims, upload/print/payment journals.

The existing motion/secondary-touch/real-swipe, preview-worker and navigation
checks also PASS: **17 tests, zero skips/failures/errors, 3.419s**
([report](motion-tests.txt)). Together with the three focused held-drag cases,
these provide 20 distinct targeted checks before source publication.
