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
