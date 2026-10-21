# Meong Photobooth v2 — approved visual concept assets

Status: **owner-selected visual direction / visual source of truth for the UX redesign**, **not** proof that the depicted controls, prices, labels, screen transitions, discount redemption, QRIS or printed products are implemented.

This folder stores the original main photobooth artboard, the **latest nine-screen revised Meong Fly artboard with the dedicated MASUK MINI GAME intro** (the approved visual reference), and the prior eight-screen game artboard as superseded visual history. All retain the original **1672 × 941** pixel canvas and were transcoded from PNG to high-quality **WebP (quality 92)** for compact GitHub display; no screen was redrawn. The original PNG files remain historical conversation assets.

| Asset | Role | Git blob SHA | Original PNG SHA-256 | Git WebP SHA-256 |
| --- | --- | --- | --- | --- |
| [meong-main-flow-approved.webp](meong-main-flow-approved.webp) | Main photobooth nine-stage conceptual screen board | e2cdc38f45299c95d8295e51f44e8dcf89a4a932 | 8c989f4cd180764e5584c204323bb3e59a1a5304a138d55496b4495dee141022 | 366a8925f255b087b16eac83ea839a085150b298079e8924caaf4ccb3e9ff64f |
| **[meong-fly-revised-approved.webp](meong-fly-revised-approved.webp)** | **Latest primary Meong Fly concept: 9 screens, including MASUK MINI GAME intro** | 427d481e4508ca5a757464e8fd2797c299f7182c | 2437c3b4c5707eb47313ce45f268ec57b340ff621c4e60916ad5e8a49cd98044 | 737864a92d72d10df11072f54d6fa32c7c59955789aedfaeb8432022f0298d8e |
| [meong-fly-flow-approved.webp](meong-fly-flow-approved.webp) | **SUPERSEDED / archival** 8-screen game board that omitted MASUK MINI GAME | 36057ce8dd787dcd5d0bd9f90fd71fc9b060c70f | 2e915f856d46d683939284e57f82442fd7b3a145e7ee748ad6c918a1d417f165 | ecb4b96d4dba5e40784ff5419e2d54a1aa2ef213dbebac170714c501b6f1fc34 |

## Required correction hierarchy

The **approved product-flow decisions supersede the illustrative annotations or missing screen controls inside the images**. In particular:

1. Idle advertising and the inline face invitation each expose direct photo and Meong Fly entry; they are not separate home pages.
2. The **latest nine-screen revised game artboard already includes** the dedicated MASUK MINI GAME intro/rules screen before receipt scan; the v2 source must implement it in a future approved integration stage.
3. After either game result, the user goes to the mandatory tutorial if it has not been completed this visit; otherwise the **12-template picker**. Do **not** route Win/Lose directly to payment.
4. Winning proposes a Rp2,500 per-visit promo to display in the template cart and validate authoritatively before checkout. Losing has no discount. Currently the game/discount integration is **not implemented**.
5. One receipt equals one irreversibly consumed attempt; there must be no **Main Lagi** action after Win or Lose.
6. The existing **12 approved physical templates** (80 × 240 mm, three photos + one customer-photo download QR) remain authoritative. Stylized concept strip pictures and the mockup example payment amount are **not** new product masters or approved commercial pricing.
7. The QR on the thermal strip provides access to the photo folder and is not the QRIS payment code.
8. Payment, capture and printing must not be interrupted by generic idle timeout; no real payment success is assumed based on a visual QR code.

See [visual screen-by-screen specification](../../portrait-kiosk-v2-visual-spec.md) and [primary FEAT-022 specification](../../portrait-kiosk-v2.md). These documents are the **annotated acceptance target**; retain the boards unchanged as visual references while implementing corrected flows.

## Handling

Do not use these artboards as runtime textures or to replace the original logo / print templates. Reuse the official Meong camera-cat assets from the repository and build interactive Kivy components, not clickable regions pasted over a screenshot. Avoid embedding customer personal photos or merchant/payment secrets in new mockup evidence.
