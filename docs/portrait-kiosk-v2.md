# FEAT-022 - Meong Photobooth portrait kiosk GUI v2 (working specification)

**Date:** 2026-10-21
**Status:** APPROVED FOR STAGED DEVELOPMENT; NOT PRODUCTION READY
**Branch:** feature/portrait-kiosk-gui
**Stable base SHA:** 27f3801b235d81dc0a49ab201f3e143b62314413 (master)
**Owner authorization:** Greenfield Kivy GUI and fresh audio lifecycle, portrait-first 10.1-inch, work only on a new branch; do not merge to master without separate approval.

## Product and design baseline

- Meong camera-cat official logo, gray camera, blue lens, rainbow, retro pixel-space style consistent with Meong Fly; do not replace the mascot.
- Target 10.1-inch portrait touch display, e.g. 800 x 1280; also handle 450 x 900 simulation and responsive resizes. Keep hit targets comfortably large.
- Advertising is the default/return screen: reuse trusted local scheduled image/video playlist and its fallback; real face detection invitation remains on **the same advertising screen**, not a separate welcome page.
- From advertising, offer direct photo and optional Meong Fly. No separate replacement mini-game home. The prototype game entry must be visibly labelled unavailable until approved integration.
- Mandatory illustrated tutorial **once per active visitor** before template picking (including after game Win/Lose if not seen). Mark seen on explicit completion, not screen appearance; reset on safe end/abandonment/return to advertising for the next visitor. See DEC-003 addendum in docs/meong-fly-tutorial-gate-20261021 at commit 980af997.
- Real templates are the 12 approved 80 x 240 mm thermal strips, exactly three photos + one photo-download QR; template quantity means paper copies. Do not invent selectable 2- or 4-pose layouts. Preserve full strip ratio (1:3) in a portrait display.
- Main flow target: advertising/invitation -> tutorial once -> 12-template picker/quantities -> payment -> three captures -> selective one-photo retake/review -> photo-strip composition -> print/Drive share -> advertising.
- Game target: advertising/invitation -> Meong Fly -> unique receipt claim -> attempt -> Win/Lose -> tutorial if unseen -> template picker -> normal payment. Result never navigates straight to payment. Win promo Rp2,500 is demo-only until trusted order-side validation and Midtrans tests; lose gets no discount, no retry with same receipt.
- QRIS payment QR and photo-download QR are separate.
- Maintain photo workflow and already working camera, mirroring, template/masks, print transports, Drive and data-store business logic. No printer/purchase workflow rewrites as a consequence of a visual refresh.
- Preserve payment/capture/printing safe lifetimes: browsing inactivity may return to ads, but never kill a paid or uncertain transaction.

## Rebuild boundary

Greenfield means **all customer-facing page layout, page navigation, style components and audio lifecycle are new**. The following existing non-UI services may be reused through adapters: approved logo/receipt artwork, template previews and quotes, local advertisement catalog/player, camera, print and Drive backends. Reusing the already tested advertisement media decoder does not mean reusing the v1 screen arrangement.

The existing python main.py path remains unchanged, running v1. The separate opt-in prototype launcher is python tools/run_portrait_v2.py. Stage-one screens must never silently create transactions, accept payment or print; unsupported CTAs must be explicitly disabled or clearly marked as a demo.

## Staged delivery and gates

| Gate | Deliverable | Definition of Done / evidence |
| --- | --- | --- |
| P0 | New package and visit-state controller | No v1 modifications; pure tests of tutorial-once, idle reset and blocked game integration |
| P1 | New audio controller | Dedicated page-owned music/SFX, unload/stop rules and mock tests; audible Windows speaker validation remains pending |
| P2 | Portrait Kivy shell | Idle advert/player, inline invitation preview, tutorial, real 12-template gallery/copy cart; active buttons, touch/resize review at 450x900 and 800x1280 |
| P3 | Safe backend/photo flow integration | Same exact three captures, retake constraints, print copies and Drive QR; hardware QA required |
| P4 | Mini game + QRIS integration | Receipt verification, single attempt and discount checks tied to authoritative order state; mock and provider Sandbox tests required |
| P5 | Complete Windows kiosk regression | Camera/audio/print/video/device/privacy tests and explicit owner release approval |

## Known blockers/risks

- BUG-001/007 v1 music audible failure: a rewritten audio controller is not proof it is fixed; run on actual Windows speaker with provider diagnostics and genuine WAV playback.
- BUG-009 cloud retention remains unresolved in v1; do not falsely advertise permanent photo URLs.
- QRIS Sandbox lives only on feature/qris-payment and needs careful reconciled integration. No real financial transactions authorized.
- Meong Fly remains on feature/meong-flappy-challenge as a standalone demo. Do not pull it into the kiosk without separate staged integration and hardware checks.
- Duplicate FEAT-021 labels exist on unrelated Meong Fly and Background Studio branches. FEAT-022 is **provisionally reserved for this portrait GUI rebuild**, pending reconciliation of the unified feature register before any merge.
- Never merge to master, delete other feature branches, or claim Windows/thermal/merchant QA on source-only evidence.

## Rollback and evidence

The stable master/v1.0.0 remain unchanged; remove/switch away from feature/portrait-kiosk-gui to return to existing functionality. Each stage gets a separate commit with relevant tests and documentary evidence. Incomplete automated/device checks must remain clearly labelled pending.
