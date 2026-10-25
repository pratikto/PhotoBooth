# Readable native button typography

> **Later owner update:** final visual/audio form is 8/8 followed by “udah clear
> semua”, recorded in [Sandbox owner acceptance](../portrait-v2-sandbox/owner-acceptance.json).
> BUG-017 is now OWNER-REPORTED PASS / MONITORING at unknown HEAD. The earlier
> OPEN/unfixed statements below remain dated observations; no decoder patch or
> measured root cause is inferred.

> **Dated source/QA record, retained for traceability.** Results, “latest/current”,
> OPEN/PENDING labels, next actions and authorization limits below apply to this
> package's recorded source and report date. Later owner reports and source work
> can supersede its status; they do not rewrite these test results. Use
> [current status](../../FEATURE_STATUS.md), [test ledger](../../test_checklist.md)
> and [current handover](../../DEVELOPMENT_HANDOVER.md) for continuation. Historical
> checklists are not an instruction to repeat already accepted tests.

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


## Pushed source

Functional source **d52a7d8dce2b40657888fa38d038f1c1e9cd88e6** is normally
pushed to the required branch and remote HEAD verified. Tested runtime/test
hashes match committed files. [CI 40104190105](https://github.com/pratikto/PhotoBooth/actions/runs/40104190105)
completed SUCCESS at that exact SHA; all three jobs pass.
The companion evidence commit will update only documentation and skip redundant CI.

For Windows, close the running GUI, keep feature/portrait-kiosk-v2-next and the
existing venv; run git pull --ff-only then python tools/run_portrait_v2.py.
Use the fresh [8-item Submit form](windows-checklist.html) if retesting; no new
twenty-cycle requirement. Subjective preference and Windows touch remain pending;
BUG-017 video→video lag is still open. No production payment/scanner is enabled.


## Matching-source CI and final checkpoint

[CI 40104190105](https://github.com/pratikto/PhotoBooth/actions/runs/40104190105)
at **d52a7d8** has **all three jobs SUCCESS**: navigation/audio lifecycle,
native GUI/source-frame/typography checks and captures, and Windows Python 3.12
native SDL audio with dummy output. [Archived result](final-ci.json).
Downloaded its original artifact; **99 PNGs** have verified hashes, dimensions
and clean-source metadata: [verification](ci-screenshot-verification.json),
[reviewed advert/gallery sheet](ci-contact.jpg). Local gate remains 546 PASS,
zero failures/errors/skips. This is source/synthetic evidence; aesthetic
preference, actual Windows touch and speaker behavior remain owner checks.

The final companion commit changes documentation only and skips redundant CI.
Tested runtime files remain byte-identical to d52a7d8. Rollback aee85cd restores
the rejected pixel-caption/icon state, retaining consumed ledgers and journals.
No unresolved automated failure remains. BUG-017 consecutive-video lag is still
OPEN/unfixed; the previous reported twenty cycles remain accepted as reported.
