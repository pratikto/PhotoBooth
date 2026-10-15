# Desktop GUI verification

Layout baseline: `c518e91df5a8311a08a167043e0f1e74aa50555c` on `feature/kivy-gui`.
The frame-recovery follow-up starts from `a6707e6c7168248c7b80b1b36c8042cd7de1f20f`.
The screen-action/selection follow-up starts from `26e27a722ab965e62d78b572b9c1b1e39634e6ff`.
The original working copy was left untouched. Source files in the separate
checkout were checked against the freshly fetched GitHub blobs before editing.

The previous 800x600 layout put a 420px payment card inside a roughly 210px
viewport. The QR was clipped, the review selection buttons were below the visible
area, and the order total could disappear with a full cart. The revised layout
fits the desktop stage at both supported sizes and gives long lists their own
scrolling area. Payment back-navigation also retains the customer's quantities.

| Check | 1200x800 | 800x600 |
| --- | --- | --- |
| Welcome and start action fit | Passed | Passed |
| Cart total visible with all four templates | Passed | Passed |
| Last template controls reachable by scrolling | Passed | Passed |
| Payment demo QR decoded from screen pixels | Passed | Passed |
| Camera preview and countdown fit | Passed | Passed |
| Three review selectors and both actions visible | Passed | Passed |
| Folder QR decoded from screen pixels | Passed | Passed |
| Offline notice and completion timer fit | Passed | Passed |
| Existing cart survives a window resize | Passed | Passed |
| Real pointer taps respect disabled camera/payment controls | Passed | Passed |
| Waiting-camera and used-retake messages fit | Passed | Passed |
| Preview and waiting overlay stay inside their image slot | Passed | Passed |
| Selected-card feedback matches nonzero quantities | Passed | Passed |
| Empty quantities disable the decrement control | Passed | Passed |

The image sheets below contain the six main screens. The reproducible renderer
also includes countdown, bottom-of-gallery, retake-used, local-only, and next-session
states, camera-waiting capture/payment/review, and empty/partly selected carts:
**32 full-size PNGs** in total.
The JSON [report](report.json) records each
render and the QR text decoded from its actual screen pixels. Full-size renders
are produced by the command below; only the compact sheets are committed here.

![Six screens at 800x600](overview-800x600.png)

![Six screens at 1200x800](overview-1200x800.png)

## Unavailable-camera and used-retake states

Previously, a stale camera mailbox left the badge marked ready and could leave
payment confirmation permanently disabled after a controller rejection. The
new tests first reproduced these failures, then checked recovery without losing
quantities, allocating a duplicate transaction, or consuming a failed retake.
A separate regression rejects a late release from an old payment after an order
edit. Actual Window pointer events also verify disabled controls at both sizes.

The preview no longer presents a frozen frame or a blank white null texture as
live video. Its waiting overlay is explicitly anchored within the camera slot.
Retake guidance distinguishes an unavailable camera from an exhausted allowance.

![Waiting-camera and used-retake states at 800x600](states-800x600.png)

![Waiting-camera and used-retake states at 1200x800](states-1200x800.png)

## Selection feedback and retired page actions

Nonzero quantities now receive a thin inset outline and pale tint, without
changing card dimensions. Returning to zero removes the visual selection and
disables decrement. The screenshots compare an empty cart, two sessions of one
template (Rp10.000), all four templates, and the last template after scrolling.
The report records selected IDs and quantities and asserts that they agree.

![Template selection states at 800x600](selection-800x600.png)

![Template selection states at 1200x800](selection-1200x800.png)

Regression tests first reproduced delayed **Ubah pesanan** restoring an old cart,
delayed **Selesai** ending a different transaction, and a disabled button delivering
a queued callback. Page actions are now bound to their exact screen revision.
Modal close is deliberately exempt from that page lifetime and is tested with
a real error popup while its underlying page changes.

The controller separately rejects completion during capture or at an intermediate
result. The test then advances both sessions and all 60 completion ticks, proving
that the final automatic return still works and does not wait for Drive upload.

## Reproduce

Python 3.12.14, Kivy 2.3.1, OpenCV 5.0.0, SDL2 offscreen, and Mesa llvmpipe were used. No webcam,
payment provider, printer, or live Google service was contacted.

```bash
SDL_VIDEODRIVER=offscreen PHOTOBOOTH_TEST_GUI=1 python -m unittest discover -s tests -v
SDL_VIDEODRIVER=offscreen python tools/render_gui.py --output-dir /tmp/photobooth-gui-qa
```

The suite passed **38 tests**. Its controller/storage checks include two-session
orders, one retake per session, local PNG and manifest persistence, cached folder
allocation, an offline upload failure followed by retry, and skipping verified
uploads. Camera acquisition and Drive access use deterministic fakes. The layout
regression test verifies clipping ancestors and decodes the payment/folder QR from
the exported UI, which catches a hidden QR even when its source texture is valid.
The synthetic camera-recovery tests hold controller timers for deterministic
manual ticks; the pointer and layout tests use Kivy's real event and canvas loop.
Recovery means fresh frames resume on an existing handle. USB hotplug, driver
reopening, startup failure recovery, and real-device latency remain unverified.

The tariff is unchanged: Rp5.000 per session; quantity 2 totals Rp10.000. QRIS
remains explicitly simulated, printing is not connected, and `ui_tkinter.py` is
unchanged. These renders use generated geometric illustrations and fixture URLs;
they contain no customer images, credentials, or transaction data.
