# Owner retest, larger Meong and original Meong Fly buttons

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
