# Owner retest, larger Meong and original Meong Fly buttons

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

> Superseded caption/icon preference: owner rejects the pixel typography and requests a minimal look. Source d52a7d8 restores native unscaled font rendering and removes main-button icons while preserving this stage's original frames and larger Meong. 546 full PASS and matching three-job CI SUCCESS. [Current proof/preview/form](../portrait-v2-readable-type/README.md).

2026-10-24, branch feature/portrait-kiosk-v2-next. Starting remote/local source
94dbd0322b0a16b582e84d09c42688bb1689e86e; normal staged pushes authorized.

## Owner report and remaining ad issue

[Preserved report fields/check IDs](owner-retest-2026-10-24.json): raw 14/14
checked, twenty P4 cycles completed. This is **OWNER-REPORTED PASS / MONITORING**
for game position/motion, aligned animated header, gallery/pricing and lifecycle.
HEAD/device/resolution/scaling are blank. A01 is checked but its metadata
subclaim is incomplete; do not map the report to 94dbd03/c242b97 or a measured
screen resolution. Do not erase checked results or infer a failed core flow.
The twenty-cycle report stands; P3 acceptance is not reopened. Exact-source
acceptance/production certification remain unverified.

The notes box is empty, but the lag field explicitly reports video→video lag,
while video→image and image→video are okay. **BUG-017 OPEN**, no fix claimed.
The fourteen items do not explicitly measure this transition, so the extra
issue is not contradicted or cleared by 14/14. Existing default payment/scanner
remain disabled; provider Sandbox/merchant/real QRIS are explicitly untested.

Read-only source review: ui_ads.AdvertisementPlayer.next calls _clear_media;
GuardedVideo.retire mutes/stops/unloads the old provider, then a new GuardedVideo
is constructed and Kivy schedules native loading. Both are on the GUI route;
the combined retirement/initialization is a candidate timing hotspot, not a
measured root cause. The same player is reused by v1 and v2. Existing native
video checks establish frames/unload/muting, not Windows video→video latency.
No shared media implementation is changed in this visual task. Before a fix,
measure old-provider retirement, next-provider load/first texture and GUI-frame
gaps on consecutive videos; retain one decoder owner, stale-callback/audio
retirement guards. No speculative decoder thread or third-party player rewrite.

## Approved staged visual follow-up

Owner asks for a larger header Meong, then main-app buttons like the supplied
Meong Fly screenshot. Use the pinned original 672e3f7 renderer/assets; remote
reference remains read-only and was verified this task. No game physics/layout,
P3 workflow, transactions, real discount/scanner or merge scope expansion.

Stage 1: enlarge the decorative camera body to roughly 72% of header height,
with uniform aspect and existing native pose/film/impact animation. Body travels
edge to edge; its longer rainbow enters/leaves through the existing header
stencil. Anchor the body at each turn to avoid a positional jump. Fit the body's
actual width into the approach space before the centered wordmark; do not shrink
the whole rainbow/body to make the trail fit. The header height and wordmark
remain fixed. Eight focused native tests pass, including both real-clock hits,
source/compositor reuse, film, pause/resize/disposal and body bounds.
[Transcript](large-logo-focused-tests.txt). Windows size preference is pending.

Stage 2: reuse actual meong_fly_polish.arcade_button and pixel glyph renderer for
shared ArcadeButton, with native touch/audio/disabled guards. Adapt only native
control sizing/long labels/pressed state; avoid replacing game code or creating
another visual system. Run focused checks and the one final full regression
following this stage; fix failures before source push. Screenshots at 800×1280
and 452×900, plus compact viewport checks. Do not rerun successful broad tests
for documentation-only evidence pushes.

Rollback: 94dbd03 restores the prior accepted-size header. Preserve all consumed
attempt/order records and P3 photo/print journals. Owner report does not certify
new larger-logo/button source before its own device retest.

## Stage 1 pushed checkpoint

Larger-logo source **c887d30bfddc246433266f7c0da2c77e84a3e97f** is pushed and
remote HEAD verified. [CI 40100048784](https://github.com/pratikto/PhotoBooth/actions/runs/40100048784)
has all three jobs SUCCESS: [archived result](large-logo-ci.json). Existing
8 native focused tests passed; 12 capture hashes/dimensions checked, reviewed
[compact advert](large-logo-advert-452x900.png) and
[portrait gallery](large-logo-gallery-800x1280.png). Header body grows from
39 to 56 logical pixels on the 78-pixel gallery header; taller 104-pixel headers
allow about 72 pixels. Its body stays visible at both ends while the rainbow
can naturally enter/leave through the existing stencil. Photo/impact and both
edge turns keep the original compositor and native animation ownership.

## Stage 2 original button materials and native captions

Shared ArcadeButton now calls the actual original arcade_button painter with
its pink/cyan/dark palette and original full bevel/shadow pixels. Nine-slice
rectangles retain corner proportions as controls resize. Original pixel_text
and camera/gamepad icon functions prepare cached bitmap captions; Kivy's native
Button still owns touch/disabled/state and the existing page/audio callbacks.
No new game renderer or font artwork is authored. All 26 pinned reference files
are unchanged.

The source game has fixed short captions and no disabled style. The small
adapter fits existing native control sizes, wraps at word boundaries, and
reduces size when necessary without dropping text. SEBELUMNYA/BERIKUTNYA stay
whole. Muted controls retain readable text with a subdued version of the original
dark material. Pressed backgrounds dim; original callbacks, disabled guards and
click-once policy stay intact. Material caches are bounded at four; caption
textures at 256. Position/press changes reuse prepared textures. Labels reraster
only when their text/color/line wrapping changes, not every animation frame.

**15 focused tests PASS, zero skips**: [transcript](buttons-focused-tests.txt).
Includes native FBO RGB and alpha comparison against the original reference-size
button for all three variants, full long/disabled captions, whole arrows,
cache reuse, larger-logo impact/film/lifecycle, one-click audio and stale actions.
The first visual preview split long arrow words; wrapping was corrected to keep
words intact and the final checks pass.

**546 final full tests PASS, 0 failures/errors/skips, 169.105 s**:
[transcript](final-full-tests.txt), [tested source hashes](tested-source.json).
Command: source /workspace/.photobooth-cloud/activate.sh; set
PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1 and
PHOTOBOOTH_PALM_TEST_ASSETS=/workspace/.photobooth-cloud/palm-test-assets;
python tools/run_kiosk_unittests.py. Linux Python 3.12/Kivy 2.3.1/software GL,
dummy audio and synthetic hardware; not new Windows hardware acceptance.
Syntax and whitespace checks pass. Matching-source CI follows the source push.

**54 final native PNGs** have verified hashes/dimensions: normal pages at
800×1280/452×900/360×640, P3 synthetic photos and opt-in MOCK at both main sizes.
[Reports](final-screen-reports.json). Reviewed [800×1280 advert](advert-800x1280.png),
[452×900 advert](advert-452x900.png), [800×1280 gallery](gallery-800x1280.png),
[452×900 gallery](gallery-452x900.png), [short gallery](gallery-360x640.png),
[uncertain-print controls](print-uncertain-452x900.png) and
[MOCK pending](mock-pending-452x900.png). Real-clock [larger-header GIF](header-live-clock.gif)
has 89 sampled frames over 12.11 s, no injected animation phases;
[clock samples](live-clock.json). Static page header poses are explicitly frozen.

[New 8-item Submit form](windows-checklist.html) uses separate storage and keeps
unchecked items. It does not require twenty new cycles after the owner's existing
twenty-cycle report. BUG-017 gets an explicit video→video item; leave it unchecked
if lag persists. Chromium/Playwright checks at both required sizes passed:
[verification](form-verification.json). No actual provider test is inferred.

Current runtime rollback for button styling: **c887d30**, retaining the larger
logo. To restore prior logo size use 94dbd03. Preserve all consumed DEMO/MOCK and
P3 journals. Remaining: owner preference/touch QA for the new visual source,
unknown exact HEAD of prior reported passes, and **BUG-017 OPEN/unfixed**.


## Pushed source checkpoints

- Larger Meong: **c887d30**, normal push/remote verified, matching CI 40100048784
  all three jobs SUCCESS.
- Original-style native buttons: **25fd55c8336b2aea0c65eb228895e982c2128097**,
  normal push/remote verified; final 546 local tests pass and hashes match the
  committed files. [CI 40102001442](https://github.com/pratikto/PhotoBooth/actions/runs/40102001442)
  has all three jobs SUCCESS at this exact functional SHA.
- Original reference **672e3f7**, read-only remote verified, 26 file hashes intact.
  Button-only rollback c887d30; prior-size rollback 94dbd03. Preserve journals.

Use the existing Windows venv on feature/portrait-kiosk-v2-next: close the GUI,
git pull --ff-only, then python tools/run_portrait_v2.py. The fresh
[8-item form](windows-checklist.html) preserves blank/untested items and leaves
BUG-017 visible; it does not claim consecutive-video lag is fixed.


## Final matching-source CI and archived evidence

[CI 40102001442](https://github.com/pratikto/PhotoBooth/actions/runs/40102001442)
at **25fd55c** completed **SUCCESS in all three jobs**: navigation/audio lifecycle,
native GUI/button-pixel/source reuse checks and screenshots, and Windows Python
3.12 native SDL audio using dummy output. [Archived result](final-ci.json).
Downloaded its original artifact: **99 PNGs** have verified hashes, dimensions
and clean-source metadata at this exact SHA. [Verification](ci-screenshot-verification.json),
[reviewed advert/gallery sheet](ci-contact.jpg). This is additional source/CI
proof, not Windows screen preference, actual speaker/touch or media-latency QA.

The companion evidence commit is documentation-only and skips redundant CI.
Runtime files still match the final 546-test source hashes. No unresolved
automated failure remains. Larger-logo rollback c887d30, prior-size rollback
94dbd03; preserve consumed ledgers and photo/print journals. BUG-017 remains
OPEN/unfixed. Owner prior 14/14/twenty-cycle report is retained without assigning
it to a guessed HEAD or requiring twenty new cycles for these style changes.
