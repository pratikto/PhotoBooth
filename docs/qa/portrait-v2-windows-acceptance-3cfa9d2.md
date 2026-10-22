# Windows acceptance feedback — audited 3cfa9d2

**Owner report received 2026-10-22; branch `feature/portrait-kiosk-v2-next`.**
Reported completion is **29/38**. This is owner-supplied Windows evidence,
not a cloud rerun or complete hardware acceptance. Retain the exact audited
SHA `3cfa9d2efc1060405db86d51627a8406ab86e2bb` as the pre-fix rollback.

## Results exactly as reported

| Group | Checked by owner | Unchecked / awaiting evidence |
| --- | --- | --- |
| A Installation/startup | A01, A02, A03, A04 | None |
| B Advertising/inline invitation | B01, B02, B03, B04, B05 | None |
| C Tutorial | C01, C03, C04, C05 | C02 four-step order |
| D Gallery/cart | D01, D02, D03, D05, D06, D07, D08 | D04 horizontal/vertical/short swipes |
| E Game preview | E01, E02, E03, E04, E05 | None |
| F Audio | None formally checked | F01, F02, F03, F04, F05, F06 |
| G Stability | G01, G02, G03, G04 | G05 close/reopen |

Unchecked does not automatically mean failed. Owner explicitly reports horizontal
swipe does not change a template. Notes also report audible music on entry from
advertising to tutorial and onward to templates; those observations do not silently
check F01/F02 or certify the other six audio cases. Five repeated cycles and the
portrait touchscreen's basic layout/CTA operation were checked by the owner.

## Follow-up authorized by this feedback

- Make every enabled button emit exactly one click, including advertising and
  preview routes. Disabled/stale actions must remain silent and inert.
- Repair real horizontal swipe input, rejecting vertical and short drags.
- Improve the visual brand using the read-only Meong Fly artwork reference and
  display it on every implemented page, preserving approved source artwork.
- Connect desktop minimize/restore to sound and advertising suspend/resume.
- Latest audio preference: video ads own their source audio (no GUI music);
  image/fallback ads use GUI music. This supersedes the earlier ad-silent rule
  for still images only. Click feedback is permitted on every page.

Payment is still intentionally unavailable in v2. Reporting its absence does not
authorize connecting real payment, scanner, discount, capture/printing or game
services. The Meong Fly branch is visual reference only.

## Input/audio correction — synthetic evidence, Windows retest required

Initial real-widget regressions failed for uncentralized button clicks, missing
pointer grabs at both portrait sizes, and absent desktop minimize binding.

Changes: page-owned clicks run once after a valid action; no duplicate click in
copy/arrows. Gallery grabs the native pointer stream, uses normalized window
movement, releases once and disposes grabs on retirement. Desktop minimize/restore
bind/unbind with application lifecycle. Optional ad-media callbacks stop GUI music
before video construction and enable music for a verified image/fallback.
Legacy ad callers keep their existing behavior; payment ads remain muted.

50 targeted navigation/audio/design/widget tests PASS, zero skips. Includes
real pointer dispatch at 800×1280 and 452×900, click counts on ads/preview/navigation,
stale/disabled silence, native minimize events and image→video→image ownership.
Native SDL2 dummy-device smoke PASS: image/video ownership, clicks on idle and
preview, suspend/resume and cleanup. Full regression: 285 run, 283 PASS, 2 optional
native-model asset skips, zero failures/errors. Twelve renderer states generated
at both portrait sizes. [Test transcripts](portrait-v2-windows-followup/).
Neither cloud check certifies audible Windows speaker output.

## Focused Windows retest

- [ ] D04: swipe over center and adjacent strip images left/right, then short,
      vertical and out-of-bounds drags; each valid gesture changes exactly once.
- [ ] F04: hear a single click from every enabled action, including advertising,
      invitation close, game-preview return, copy ± and template arrows.
- [ ] F01/F02/F05: image-ad music → tutorial → gallery; video-ad audio without GUI
      soundtrack; image-ad music returns when the playlist returns to a still.
- [ ] F03: Test Music audibly restarts the soundtrack on the chosen speaker.
- [ ] F06/G05: minimize/restore on image, video and tutorial; close/reopen without
      orphan music, stale tap or retained camera/video decoder.
- [ ] C02: confirm the visible order 01 template, 02 payment, 03 three photos,
      04 print/download QR. Tutorial text describes future flow, not enabled payment.

Keep the original 29 checks associated with 3cfa9d2; record the new tested SHA,
OS/display/provider details and individual retest results before changing them.

## Branding and tutorial-order follow-up

Use the exact transparent Meong Fly reference artwork (unchanged bytes) in a shared
native brand component on each implemented page. No white image plate or game code
is imported. 52 targeted tests and twelve local screenshots passed; final complete regression
is 287 run / 285 PASS / 2 optional model-asset skips. Actual wordmark
pixels and four-step tutorial order are now checked in addition to geometry.
[Updated screenshots and evidence](portrait-v2-windows-followup/README.md).
Windows aesthetics, audible sound and repaired swipe still require owner retest.
