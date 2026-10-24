# P4 game follow-up — owner Windows findings, 2026-10-24

Owner reports: fixed portrait scene does not fill the main application; remove
KEMBALI KE IKLAN; right-click leaves a dot; winning discount absent from payment
calculation; use a different, moderately tense game soundtrack.

Target `feature/portrait-kiosk-v2-next`; baseline `b0be59e`. Reuse unchanged Meong
Fly reference `672e3f7`. No master, reference-branch, production payment/discount
or scanner change. All monetary changes below are local DEMO/MOCK calculations.

## Stage 1 — window, navigation and pointer

The game host now fills the current window, using the existing main Starfield
through the original standalone opaque side plate. Artwork, field geometry,
controls and sprites keep uniform aspect scaling. This intentionally extends
the background and clickable flight area; it does not distort or crop the
original fixed-aspect playfield. Native 800×900, 800×1280, 452×900, 360×640 bounds
and side-background pixel tests pass. [Wide screenshot](stage1-wide-intro.png).

Remove the extra return-to-ad footer from intro/receipt/win/loss. Original scan
Back and result photo CTA remain; active gameplay retains its safe AKHIRI GAME
exit. Browsing timeout and one-use ledger are unchanged. Async paths handle the
absence of a footer without failure.

The exact reported red dot is reproduced with the native Kivy mouse provider:
its default right-click emulates a retained multitouch point. The dedicated
v2 launcher configures `mouse,disable_multitouch` before Window import, without
writing global settings or disabling the real touchscreen provider. Right and
middle clicks do not activate kiosk/game actions; left touch and wheel remain.

**18 focused tests PASS**, zero failures/errors/skips:
[transcript](stage1-layout-input-tests.txt). Includes old-marker reproduction,
new native mouse cleanup, fullscreen bounds, removed return footer, side touch,
retired input and fourteen original-scene pixel matches. The parent background
is deliberately excluded from the original-scene comparison because the owner
requested replacing the standalone letterbox. All 26 reference modules/assets/
tests remain byte-identical. This is local source proof, not a Windows retest.

Stage-1 rollback: `b0be59e`; preserve consumed attempts/orders. Next: connect the
winning offer to the displayed simulated total, then dedicated game BGM. One
full final regression follows the completed functional changes.


## Stage 2 — winning quote reaches the gallery and MOCK total

Extract the existing backend flat-discount math into `game_offer.py` and reuse
it in both the gallery preview and authoritative local MOCK creation. The
preview requires the acknowledged persisted result (won, score≥10, attempt ID),
not just a GUI win badge. MOCK still reads/validates the durable ledger and
single-use reservation before creating the order.

One design/one copy: subtotal Rp10.000 − Rp2.500 = Rp7.500. Two copies of that
design: Rp15.000 − Rp2.500 = Rp12.500; two designs/three sheets: Rp25.000 − Rp2.500
= Rp22.500. Discount is once per order, capped at subtotal; empty cart is zero,
loss has no reduction. Display subtotal/discount/net in two lines, preserving
strip focus. [Winning gallery](stage2-win-gallery.png).

A consumed matching win is marked used on admission or authoritative recovered
ADMITTED status, including a lost response; gallery never reapplies it. Cancel/
expiry retains the existing backend rules. Real payments/discounts remain off;
all displayed reductions are explicitly SIMULASI and checkout stays MOCK-only.

**38 targeted tests PASS**, zero skips:
[transcript](stage2-offer-tests.txt). Includes actual gallery-vs-backend totals,
multiple designs/copies, empty/loss, admission/recovery and twenty MOCK visits.
Stage-2 rollback: `4896d51`; retain persistent attempts/orders.


## Stage 3 — dedicated game soundtrack and final regression

New **Asteroid Chase** is an original 30-second minor-key arcade loop at 128 BPM,
using the existing synth's harp/bass/bell instruments with short arpeggios and
soft percussion. No external audio service or sampled recording. Format matches
the existing sound bank: mono signed 16-bit PCM, 22,050 Hz; bounded peaks, quiet
edges. [Provenance/hash](game-music-provenance.json). Generator runs offline;
playback reads the shipped WAV. GUI/v1 song and v1 audio code are unchanged.

The existing single PortraitAudio owner prewarms the game sound silently and
switches tracks before play: game intro/receipt/play/result share ONE game loop;
tutorial/gallery/checkout use the GUI loop; image ads use GUI music, video ads
own their audio. Game-page changes do not restart the game song. Volume zero,
button effects, minimize/restore and close retain established behavior. No extra
mixer or player App is introduced.

**39 focused audio tests PASS**, zero skips:
[transcript](stage3-audio-tests.txt). Native SDL dummy post-mix sampling verifies
nonzero game PCM by itself across twenty cycles, only one active music channel,
normal GUI resumption and final silence. Fake-provider cases verify one loop
across all four game scenes and gain/suspend/restart/close. Actual Windows
speakers still judge audibility, timbre, tension and loudness.

**527 final full tests PASS**, zero failures/errors/skips, with native Kivy,
audio/video and public palm fixtures. [Final transcript](final-full-tests.txt).
Original Meong Fly engine/compositor/animations and 26 reference file hashes
remain unchanged; only the v2 host's background plate differs, with the original
portrait scene compared independently. Legacy camera/photo/printer/workflow and
real payment/scanner are untouched.

Fifty final Kivy captures verified: thirty game states plus twenty MOCK states,
at 800×1280 and 452×900. Reviewed [800 game contact](final-contact-800x1280.jpg),
[452 game contact](final-contact-452x900.jpg) and winning gallery/checkout pairs.
Manifest hashes: [800 game](final-render-800x1280.json),
[452 game](final-render-452x900.json), [800 MOCK](final-checkout-800x1280.json),
[452 MOCK](final-checkout-452x900.json). States are synthetic; precommit SHA and
tracked changes are recorded truthfully. Matching-source CI follows push.

The [28-item Submit checklist](../portrait-v2-p4/windows-checklist.html) now
covers full-window background, removed non-playing footer, right-click cleanup,
gallery/net-MOCK math, spent wins and distinct game music. Fresh storage key
avoids importing old checkmarks. Browser checks revalidated at both sizes:
[report](form-verification.json). P3 owner acceptance remains valid.

## Delivery and Windows retest

- Baseline / stage-1 rollback: `b0be59e`.
- `4896d51`: window/background, footer and native mouse correction (18 PASS).
- `16bc7c6`: shared winning quote and spent-offer correction (38 PASS).
- Stage 3 source: dedicated music, final 527 PASS; CI/HEAD recorded after push.
  Rollback music stage to `16bc7c6` if needed; preserve attempts/orders.

Close the old app, pull `feature/portrait-kiosk-v2-next` with `--ff-only`, then
start the existing `python tools/run_portrait_v2.py` launcher in the Windows
venv. Restart is necessary for the mouse provider configuration and new WAV.
Use a new DEMO code for each play. Check resizing/left touch/right clicks,
minimize/restore, new music and win/loss. Win → one design/one copy must show
Rp10.000 − Rp2.500 = Rp7.500 in BOTH gallery and MOCK checkout (the latter keeps
its existing PHOTOBOOTH_V2_CHECKOUT_MOCK=1 opt-in). Do not enable production.

No known remaining failure in the tested local scenarios. Windows feel/speaker
acceptance and previously open provider Sandbox/merchant gates are not claimed
PASS; all prices/discounts here remain nonfinancial simulations.
