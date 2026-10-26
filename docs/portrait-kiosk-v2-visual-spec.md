# FEAT-022 — GUI v2 visual and interaction specification

Updated **26 October 2026**. Branch `feature/portrait-kiosk-v2-next`; latest
functional source `20453fe`. This document separates owner design decisions,
implemented UI and acceptance. [Roadmap](portrait-kiosk-v2.md) · [status](FEATURE_STATUS.md).

## Approved concept boards

![Approved main concept](assets/portrait-v2/meong-main-flow-approved.webp)

![Approved revised game concept](assets/portrait-v2/meong-fly-revised-approved.webp)

[Provenance/hashes](assets/portrait-v2/README.md). Boards provide visual direction.
Their sample Rp25,000 amount, game-to-payment arrows and scanner illustrations do
not establish tariff, production integration or the current screen inventory.

## Current design decisions

| Area | Requirement and implementation |
| --- | --- |
| Identity | Cosmic navy pixel-space, cyan/pink/gold, original game frames and Meong art |
| Typography | Pixel wordmark; **main-app captions use readable native Roboto without mandatory icons**. Rejected stretched bitmap captions are historical |
| Header | Centered wordmark and larger animated Meong at the same level; limbs/rainbow/print motion and a contact-gated single wordmark spin |
| First page | Media plus direct photo/game entry and UNDANGAN (DEMO); invitation overlays the same advertising surface. No separate CARA PAKAI action |
| Tutorial | Four illustrated steps, vertical scroll and explicit acknowledgement once per visit; reset only on safe idle return |
| Gallery | Twelve original 1:3 strips, three full previews with center focus; floating PILIH TEMPLATE STRIP title |
| Navigation | Floating lower-corner arrows; drag follows image and settles with real sliding; short/vertical gestures do not change selection |
| Summary | Centered minus/count/plus at left; brief copies/session and total/savings at right; removed CETAK caption stays removed |
| Game | Actual original Stage/Flow/render/assets; unified window scene, centered complete world, uniform speed/spacing; Meong stays left of center |
| Game actions | Intro/input/result omit KEMBALI KE IKLAN; active game retains AKHIRI GAME. Either result → unseen tutorial → gallery; no MAIN LAGI |
| Mouse | Right-click creates neither multitouch markers nor accepted actions |
| Audio | Still ads + GUI BGM; video + own audio; distinct game loop; one cue/enabled action; no leftover sound on minimize/close |
| Price | One session/design + N copies; one MOCK win reward; Sandbox explicit full-price/no-promo consent |
| Camera/results | Display-only live mirror; originals/review/print unchanged; one selected-photo retake/design |
| Operator | Hidden F12/1.5-second header-hold access at safe states; original six-row health panel, scrolling, disabled selection and local report action |

Indonesian UI labels are quoted exactly so operators can find the actual controls;
they are not instructions to translate application source.

## Navigation

Direct: advertising/invitation → tutorial if unseen → gallery.
Game: advertising/invitation → intro → **manual one-use DEMO code** → gameplay →
win/lose → tutorial if unseen → gallery. Real scanner/POS remains disabled in v2;
standalone scanner support on the game branch is a different scope.

Gallery local mode uses UJI FOTO/consent. MOCK uses nonpayable checkout. Sandbox
uses explicit price consent, provider QR, backend verification/grant and photo
consent. No manual PAID override is shown in Sandbox.
[Engineering contracts](portrait-kiosk-v2-technical-design.md).

## Screen/state inventory

| ID | State | Current source |
| --- | --- | --- |
| M00 | Advertising | Image/video/fallback, direct photo/game actions and invitation demo |
| M01 | Inline invitation | Optional face inviter/manual demo; same ad surface |
| M02 | Tutorial | Four steps, scroll, acknowledgement |
| M03/M04 | Gallery/cart/reward | Original templates, swipe, copies/quote, local reward validation |
| M05 | Payment waiting | Explicitly distinguished MOCK or Sandbox opt-in; default off |
| M06 | Cancel/unknown/recovery | Protected order state; not an unrestricted idle return |
| M07 | Photo consent/camera ready | Local test or Sandbox grant; actual camera readiness still required |
| M08 | Countdown/capture ×3 | Five seconds, shutter after successful save |
| M09 | Review/retake | One replacement of one photo per design |
| M10 | Composition/delivery/print | Default local; operator opt-ins, truthful uncertain-send state |
| M11 | Result/download QR | Folder QR only when a valid assigned destination exists, not payment QR |
| M12 | Safe finish/idle | Reset transient visitor/cart only when protected work permits |
| G00/G01 | Game intro/rules | Original renderer, one chance and simulated reward |
| G02 | DEMO receipt input | Manual code/duplicate rejection; real scanning disabled |
| G03 | Gameplay/pause | Original physics/art through responsive host |
| G04/G05 | Win/lose | No replay; result-to-tutorial/gallery, no payment authority |
| O00 | Operator Device Health | Six observations/inventory/refresh/report; safe idle or Sandbox RECOVERY only |

## Visual QA and acceptance

Required views: **800×1280** and **452×900**; also compact 360×640, short/landscape
windows and actual Windows scaling when relevant. Preserve strip proportions,
readable in-frame captions, reachable actions and visit state during resize.

Latest [operator package](qa/portrait-v2-operator-health/README.md): 119 PNGs
verified, required views reviewed. Earlier [P5 package](qa/portrait-v2-p5/README.md):
109 verified PNGs. Fixture screenshots do not certify hardware/provider behavior.
Owner final visual/audio 8/8 at unknown HEAD stays owner-reported;
[P5 form](qa/portrait-v2-p5/windows-checklist.html) and
[operator form](qa/portrait-v2-operator-health/windows-checklist.html) remain separate.
