# Readable native button typography

Owner rejects the pixel button typography ("typografi nya jadi jelek bgt") and
asks for an aesthetic/minimal result without mandatory button icons. Authorized
scope: main-app typography/icon correction on feature/portrait-kiosk-v2-next.
Starting local/remote HEAD aee85cd74adb0068b5aaa66ac8b2d57f1a76d846.

Reuse the earlier working native Roboto renderer, original Meong Fly frame
material and existing Button touch/audio/disabled behavior. Remove stretched
bitmap captions and button icons; use native glyph metrics and modest 18-point
requested text, with interior spacing and word wrapping when needed. Keep native
texture dimensions intact: no nearest-neighbour font magnification or shrinking
of a pre-rendered glyph bitmap. Original frame RGB/alpha remains unchanged.
Large Meong and the original game source are outside this correction.

Nine focused native checks PASS: frame RGB/alpha identity, native unscaled font,
one-line arrows, punctuation preservation, no embedded icons, bounded long and
disabled labels, cached frame/press state, single click/audio and stale-action
guards. [Transcript](focused-tests.txt). Next: reviewed required-size captures,
one final full regression, source commit/push and matching-source CI. Do not
count synthetic checks as owner approval of aesthetics or physical Windows QA.

Rollback: aee85cd restores the rejected pixel typography/icon version. Preserve
all consumed DEMO/MOCK records and P3 photo/print journals. BUG-017 consecutive
video latency remains OPEN/unfixed; this task changes no media decoder code.
The earlier owner 14/14/twenty-cycle report is retained at unknown tested HEAD;
these style changes do not impose a new twenty-cycle test requirement.

## Reviewed visual and form evidence

**54 native PNGs** have verified hashes/dimensions: normal pages at 800×1280,
452×900 and 360×640, synthetic P3 photo and opt-in MOCK at the two main sizes.
[Capture reports](screen-reports.json). Reviewed [800×1280 advert](advert-800x1280.png),
[452×900 advert](advert-452x900.png), [800×1280 gallery](gallery-800x1280.png),
[452×900 gallery](gallery-452x900.png), [short gallery](gallery-360x640.png),
[review controls](review-452x900.png), [MOCK controls](mock-pending-452x900.png).
Static header poses are frozen for layout QA, not motion measurements.

[Fresh 8-item Submit form](windows-checklist.html) checks clean native typography
and icon-free buttons instead of the rejected pixel-caption requirement.
Chromium/Playwright verifies blank/separate storage, persistence, unchecked
preservation, Submit/download/reset and no horizontal overflow/page errors at
both required sizes: [result](form-verification.json). The existing reported
twenty cycles are retained; no new twenty-cycle gate is imposed by this form.
BUG-017 remains explicitly open and represented in V01.

The original game frame material and all 26 reference files remain unchanged.
Main-app caption rendering delegates to native Button/Label.texture_update with
the real font metrics. Fonts are drawn into their intrinsic native texture size;
no bitmap caption scale, no caption/icon caches, and no main-button icons remain.
Whole-word wrapping and interior bounds are checked, with reduction of requested
font size only where a long label would otherwise overflow. Touch, one-click
feedback, disabled and stale-page guards are the existing implementations.
No changes to the media player, checkout rules, game engine or printer service.

## Final local gate

**546 tests PASS, 0 failures/errors/skips, 168.435 s**:
[transcript](full-tests.txt), [tested file hashes](tested-source.json).
Activate /workspace/.photobooth-cloud/activate.sh; set PHOTOBOOTH_TEST_GUI=1,
PHOTOBOOTH_TEST_AUDIO=1, PHOTOBOOTH_TEST_VIDEO=1 and
PHOTOBOOTH_PALM_TEST_ASSETS=/workspace/.photobooth-cloud/palm-test-assets;
run python tools/run_kiosk_unittests.py. Linux Python 3.12/Kivy 2.3.1/software GL,
dummy audio and synthetic camera/printing/checkout. Syntax/whitespace checks pass.
No subjective aesthetic or actual Windows acceptance is inferred from this gate.
Source commit/push and matching-source CI follow; no remaining automated failure.
