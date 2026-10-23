# FEAT-022 — Approved visual mockups and corrected screen-by-screen UX specification

> **P4 native source update (2026-10-23):** Actual DEMO intro/code/game/result and opt-in MOCK checkout states are connected and reviewed at both target sizes. The revised game result still routes through tutorial-once/gallery; payment artwork is represented only by clearly nonpayable MOCK QR. 42 reviewed P4 captures; no real scanner/payable QR/discount. [Contacts and acceptance form](qa/portrait-v2-p4/README.md).

**Working branch:** feature/portrait-kiosk-v2-next  
**Product:** Meong Photobooth — greenfield portrait Kivy customer GUI v2  
**Status:** APPROVED **visual direction**; complete corrected workflow is a **design target**, not an implemented or production-certified flow  
**Target device:** 10.1-inch portrait touchscreen, reference canvas 800 × 1280; compact 452 × 900 for aligned Xvfb screenshot QA  
**Last reviewed:** 2026-10-21  
**Canonical implementation status:** [FEAT-022 primary specification](portrait-kiosk-v2.md) and [FEATURE_STATUS.md](FEATURE_STATUS.md)

This is the authoritative **visual-to-behavior interpretation** of the approved main artboard and the **latest revised nine-screen Meong Fly artboard** (the earlier eight-screen game diagram is retained only as archived history). Images preserve the agreed cosmic pixel-arcade visual look; **explicit owner flow corrections supersede text, page counts, arrows, sample prices and absent buttons in the artwork**. No mockup constitutes a working UI, paid QRIS, partner POS, printer template, test record or accepted hardware output.

## A. Main photobooth approved concept board

![Approved Meong Photobooth pixel-arcade main UI board; advertising, invitation, tutorial, template carousel, illustrative QR payment, capture, review and final photo strip](assets/portrait-v2/meong-main-flow-approved.webp)

[Open full-resolution main board](assets/portrait-v2/meong-main-flow-approved.webp) · [Asset provenance](assets/portrait-v2/README.md)

**Retain:** dark navy/indigo cosmic background; pixel stars and soft planets; official Meong camera-cat logo with blue lens and rainbow; vibrant cyan/pink/gold buttons; high-contrast information hierarchy; generous portrait touch targets; advertising-led entry; preview of the **vertical three-photo + download-QR strip**; photo-focused live capture and review.

**Required corrections:** the first board does not show the mini-game entry. Put a visible **MAIN MEONG FLY** CTA alongside **MULAI FOTO** on the *same* idle advertising screen and inside its *inline* face invitation. Do not create a second dedicated home and do not mistake face invitation for a separate full-screen route. The concept's Rp25.000 payment example is a placeholder, **not the source-of-truth tariff or proof of a payable gateway**. Use actual approved 12 template masters in production, not the concept's illustrative thumbnails.

## B. Meong Fly approved concept board

![Latest approved nine-screen Meong Fly board including the dedicated MASUK MINI GAME intro before receipt scan, gameplay, win, loss and error concepts](assets/portrait-v2/meong-fly-revised-approved.webp)

[Open full-resolution Meong Fly board](assets/portrait-v2/meong-fly-revised-approved.webp) · [Asset provenance](assets/portrait-v2/README.md)

**Retain:** animated/arcade feel, camera-cat with rainbow movement, asteroid obstacles, score and target in an unobstructed HUD, receipt visual language, clear win/loss feedback, one-attempt rule, and attractive Rp2.500 *proposed* discount announcement.

**Required corrections:** the panel labelled **PROMO DI HOME** is **not** a new home: promotional access belongs to the existing idle/advertising stage and face invitation. The **latest revised nine-screen board now visibly contains MASUK MINI GAME** before receipt scan; this dedicated intro must still be implemented inside the future integrated kiosk. Replace **LANJUT KE PEMBAYARAN** after both Win and Lose with a route to **tutorial (only if unseen)**, then **PILIH TEMPLATE**, where the cart can display a proposed discount. Do not show **MAIN LAGI**, even after a loss. A screen about expired/failed QRIS belongs to the checkout error states, not to the end of a mini-game attempt. A decorative receipt QR is not working receipt verification.

## Non-negotiable visual and interaction rules

| Design property | Required behavior |
| --- | --- |
| Orientation | Portrait-first at 10.1 inches; no assumption that a 16:9 mockup canvas represents the target screen orientation |
| Branding | Use actual bundled Meong camera-cat assets; no mascot redesign, incomplete/ripped rainbow, or distorted logo |
| Style | Pixel-art retro space, restrained layering, pink primary CTA, cyan secondary CTA, navy high-contrast panels, legible Indonesian copy |
| Advertising | Largest media region when idle; preserve aspect ratio of vertical/horizontal creatives, avoid cropping faces/text unintentionally, fallback cleanly if no decoder or offline |
| Face invitation | Nonmodal overlay *on the advertising surface*, without stopping the media unnecessarily; both direct photo and game actions remain available |
| Tap targets | Comfortable large touch targets with clear enabled, focused, pressed, disabled and loading states; no invisible screenshot hotspots |
| Long copy | Scrollable tutorial/order/instructions with the next primary CTA visible or safely reachable |
| Print preview | Actual 12 approved 80 × 240 mm template designs, visual aspect ratio 1:3; exactly 3 stacked portraits + 1 photo-folder QR at the bottom |
| Quantity | Printed copies of *one selected template/session*; not number of extra shutter sessions |
| QR semantics | Checkout QRIS = merchant payment; final strip QR = photo-folder download; never interchange their payloads |
| Prices | Display an amount calculated by the selected checkout mode; never hard-code sample concept-board pricing as a payable price |
| Audio | One owner per page: idle video may play its audio; background music during tutorial/photo UI; payment advertising muted; game audio isolated when integrated |
| Camera | Live preview may be horizontally mirrored for user comfort; saved, printed and uploaded photo bytes must not be mirrored by that view-only transform |
| Results | Distinguish composing/upload/print progress and final/failed states; don't falsely promise a successful Drive upload or paper print |
| Failures | Preserve accessible recovery/cancel/return controls according to transaction safety; do not reset paid/unknown visits via generic timeout |

## C. Corrected navigation — two entry paths, one photo journey

### Direct photography

1. **IDLE / IKLAN**: local advertising player starts by default; **MULAI FOTO**, **MAIN MEONG FLY** and **CARA PAKAI** are accessible without navigating to another home.
2. **FACE INVITATION overlay** (optional): sustained nearby-face presence invites the visitor *on the same screen*; visitors may accept **AYO FOTO**, choose **MAIN MEONG FLY**, or dismiss.
3. **TUTORIAL**: four illustrated steps; must be explicitly acknowledged once per active visit, not automatically counted as viewed merely because its page opened.
4. **PILIH TEMPLATE**: 12 real designs; quantities; cart summary. Each selected design triggers one 3-shot photo session and N identical physical copies, in keeping with the current tariff model.
5. **PEMBAYARAN**: order summary, ad placement and active payment QR. DEMO versus QRIS-MOCK versus MIDTRANS SANDBOX must be conspicuously distinguished; camera admission only after authorized success for that mode.
6. **KAMERA SIAP / COUNTDOWN**: mirror only the preview; capture three source photos with clear 1/3, 2/3, 3/3 indicators, shutter feedback, and camera disconnect handling.
7. **REVIEW & RETAKE**: inspect three shots, select at most one photo for allowed retake; preserve chosen strip design.
8. **PROCESSING / COMPOSING / PRINTING / DELIVERY**: build actual 1:3 strip with download QR, send the correct requested print-copy count, track actual printer job state and upload status.
9. **HASIL / SELESAI**: show full strip and truthful download/print status; return to advertising only after safe completion/appropriate result lifetime.

### Promotional Meong Fly

1. On the **same** IDLE or FACE INVITATION screen, visitor taps **MAIN MEONG FLY**.
2. Open a **dedicated MINI GAME INTRO screen** describing the controls, one-valid-cafe-receipt-one-attempt, potential Rp2.500 reward, and **LANJUT SCAN STRUK / KEMBALI**.
3. Open **SCAN STRUK**. Current standalone FEAT-021 only accepts local **DEMO-** token entry with decorative QR graphic. A real partner QR/POS scanner is a future dependency.
4. Enter **VALIDASI** and distinguish invalid, duplicate/used, ineligible, network error, and valid-unclaimed outcomes; claim a single use before gameplay.
5. Show **GAMEPLAY** with pause, score, actual Meong camera-cat asset, consistent hitboxes, asteroid path, and responsive portrait controls.
6. Show mutually exclusive **MENANG** (proposed Rp2.500 entitlement) or **KALAH** (no discount), with one CTA: **LANJUT PILIH TEMPLATE**. Neither screen offers **MAIN LAGI** or goes directly to payment.
7. The common navigation guard sends the visitor to **TUTORIAL only if tutorial_seen is false**, then to **PILIH TEMPLATE**; otherwise goes straight to **PILIH TEMPLATE**. The game result travels with the active visit.
8. Display discount as a separately named, nonnegative proposed cart line; checkout must later verify source eligibility and compute the authoritative payable total, never trust the Kivy display or a client-provided amount.
9. Continue through the *same* payment, capture, review, print, Drive and completion stages as direct photography.

The proposed commercial promo settlement share and interactions with FEAT-002 receipt discount remain **undecided**; do not silently stack two merchant discounts or grant a free session on the strength of local demo gameplay.

## D. Screen inventory — more than nine screens

**Implemented** below means present in the **opt-in portrait v2 prototype**. **Target** means planned visual state, not implemented v2 feature.

| ID | Screen/state | Status in current v2 | Essential controls and content |
| --- | --- | --- | --- |
| M00 | Idle / advertising | **Implemented (P2.5 visual polish)** | Actual AdCatalog/AdvertisementPlayer, MULAI FOTO, MAIN MEONG FLY, CARA PAKAI, branded UI and media fallback |
| M01 | Face invitation on idle | **Manual preview only** | AYO FOTO, MAIN MEONG FLY, NANTI SAJA; real detector trigger not connected |
| M02 | Mandatory tutorial | **Implemented (four new vector illustrations)** | Scalable icons, scrollable four steps, explicit LANJUT; once-per-visit state |
| M03 | Template carousel | **Implemented (three visible strip previews + swipe)** | Genuine 12 templates; adjacent/current strip images, horizontal swipe or previous/next, paper-copy count and truthful DEMO quote |
| M04 | Review cart / applied promo | **Target** | Accurate session and copy subtotals; win discount only when eligible and authorized |
| M05 | Payment pending | **Target (legacy/QRIS branches only)** | Stable QR, official mode/status, price, expiry, muted ad and safe order edits |
| M06 | Payment expiry / denied / unknown / recovery | **Target** | Provider-confirmed status, no false admission or duplicate charge, appropriate retries |
| M07 | Camera readiness | **Target** | Mirrored preview, device readiness and a clear start control |
| M08 | Capture countdown × 3 | **Target** | Large countdown, pose count, capture sound and feedback |
| M09 | Review / selective retake | **Target** | Three photos and strip preview, selected single retake, accept |
| M10 | Composition / photo upload / print | **Target** | Distinct processing and failure states; printer/Drive status not conflated |
| M11 | Result and photo-strip download QR | **Target** | 3-photo 80×240 mm strip, QR photo download, printing/result CTA |
| M12 | Safe completion → advertising | **Target** | No race with in-flight print, completed/uncertain payments or residual visit data |
| G00 | Game entry from idle/invitation | **Implemented as placeholder link** | No second homepage |
| G01 | Dedicated game intro/rules | **Implemented as safe visual intro; scanner disabled** | Meong Fly rules and proposed discount in separate intro, blocked scan CTA, safe direct photo / return to ad; no actual game/struk |
| G02 | Receipt scanning / manual DEMO code | **Standalone branch only** | Clearly labelled DEMO until real reader available |
| G03 | Receipt validation/errors | **Target** | Claim once, reject used/invalid, avoid holding a photo checkout |
| G04 | Gameplay | **Standalone branch only** | Score, pause, responsive obstacle/game feedback |
| G05 | Win | **Standalone branch only** | Proposed Rp2.500 and CTA toward tutorial/template |
| G06 | Lose | **Standalone branch only** | No discount, no replay CTA, same routing |
| S00 | Browsing inactivity warning | **Implemented on prototype browsing pages** | Warning 10s before configured timeout, ability to continue |
| S01 | Payment/camera/printer/storage failure | **Target** | Failure-specific safe recovery, never silently reset a paid/unknown session |

**Important:** The v2 prototype still has only **four actual route names**: advert, tutorial, templates and game_preview. The game_preview route now displays a dedicated illustrated *intro* but its scanner/game CTA remains disabled. The remaining entries are screen requirements, overlays or services, **not** pre-existing interactive pages.

## E. Overlay timings, lifecycles and ownership

| Condition | Current v1/advertising baseline | Intended v2 interpretation |
| --- | --- | --- |
| Nearby face invitation | 5 seconds stable presence, 15s auto-dismiss, 45s cooldown in advertising config | Same overlay and timing intent; currently only manual preview in v2 |
| Browsing inactivity | 180s, warning in final 10s | Applies only to pre-payment browsing, not protected payment/capture/result or uncertain paper output |
| Game failure | Receipt attempt consumed before gameplay; no replay | Show final outcome once, then continue to tutorial/template; game timeout policy not yet production-approved |
| Payment waiting/expiry | Defined per active demo/provider attempt, not an arbitrary visitor timeout | Preserve order identity and payment authority; no fake success, no blind replacement |
| Result completion | Existing backend prevents premature cleanup while printing | Adapt without dropping in-flight jobs or promised copies |
| Audio transition | Video may own idle audio; payment advert muted | No music double-play, no leaked music into ad, distinct sound handles, test on Windows speakers |

The game mockup's **30-second timeout numeral** is an illustrative visual, not an accepted globally applicable timer. Current v2 UI uses the actual ad catalog timing configuration rather than this illustration.

## F. Render-to-implementation acceptance checklist

- [ ] Same Meong brand assets across every screen: camera-cat head/body fully visible, large blue lens, continuous rainbow, pixel typography, accurate contrast.
- [ ] Portrait at 800×1280 with safe margins and a functioning touch UI; synthetic 452×900 regression is auxiliary evidence, not hardware approval.
- [ ] Actual ad image/video preserves aspect ratio and shows both Foto and Meong Fly CTA; invite remains on its ad surface.
- [ ] Tutorial appears once (after direct photo entry or game), never silently skipped, and resets when a new visitor starts.
- [ ] Full set of 12 genuine strip previews, with each strip showing exactly 3 photos + photo-download QR; no concept art master substitution.
- [ ] Game intro exists *before* struk; used/invalid tokens rejected, one receipt cannot replay after win/loss or restart.
- [ ] Win and Lose return to template selection (via tutorial if unseen), not to QRIS payment; Win-only promo appears in cart and is independently verified by the server when integrated.
- [ ] All photos, screenshot previews, result rendering and thermal printer output preserve correct mirror and orientation rules.
- [ ] Payment display, real provider states, and customer photo QR are unambiguously distinct.
- [ ] Advertising audio, Kivy music, game sounds, countdown/shutter and payment-mute behavior are confirmed audible/silent as designed **on the operator's real Windows speaker**, not merely unit-tested.
- [ ] UI never implies physical printing, cloud upload, real payment or merchant subsidy success without the corresponding verified backend state.
- [ ] App can safely return to advertising only when the visit has legitimately ended.

## G. Cross-reference and change management

- [Primary staged feature specification](portrait-kiosk-v2.md) — implemented scope, engineering boundaries and acceptance gates.
- [Current technical architecture](ARCHITECTURE.md) and [FEAT-022 engineering contracts](portrait-kiosk-v2-technical-design.md).
- [DEC-003 tutorial-once decision and other product decisions](DECISIONS.md).
- [Feature-status truth](FEATURE_STATUS.md), [test evidence/checklist](test_checklist.md), and [development handover](DEVELOPMENT_HANDOVER.md).
- [Asset manifests and original-file checksums](assets/portrait-v2/README.md).

**No new bitmap or diagram is approved just by editing this document.** Preserve both artboards as visual references until the owner explicitly requests a new mockup revision. Implementation requires separately approved work scope, branch-specific commits, screenshot regression and actual hardware acceptance; no merge to master is authorized here.

## H. P2.5 implementation versus approved mockups (2026-10-21)

**Current visual QA:** [GitHub Actions 39555036023](https://github.com/pratikto/PhotoBooth/actions/runs/39555036023), code SHA c4e4703a, both jobs SUCCESS, 21 pure tests and 12 800×1280/452×900 synthetic screenshots. Direct visual comparison to the original approved boards was performed as a **synthetic UX inspection**, not hardware acceptance.

- **Idle / invitation:** Branded PixelCard ad heading and themed two customer entry CTAs; Cara Pakai invokes the real mandatory tutorial; manual invitation overlay retains Foto and Meong Fly. Real camera face presence still unavailable.
- **Tutorial:** four illustrated Kivy-vector cards (template strip, symbolic payment, camera and print/photo QR) in a ScrollView; the underlying once-per-visit VisitFlow remains unchanged. Compact height scrolls to lower cards.
- **Template carousel:** selected actual full-strip master preview flanked by prior/next real strip previews, working arrow buttons and **horizontal touch-swipe handler**; source catalog, three photographs and photo-download QR unchanged. Swipe direction logic has automated regression; physical touchscreen swipe acceptance remains pending.
- **Meong Fly:** distinct, responsive full-screen intro with mascot and owner-approved rules; explicit unavailable scanner and skip-to-photo continue flow. The on-screen promo text is *potential discount*, not an issued voucher. The actual gameplay/receipt claim/Win-Lose/checkout are deliberately NOT integrated.
- **Remaining design gap:** portrait Kivy fonts remain non-pixel default, some pixel art and animation detail from the approved reference has not yet been recreated, and target QRIS/capture/review/result pages are future P3/P4 stages.

**Implementation reference:** [FEAT-022 primary specification, P2.5 source map](portrait-kiosk-v2.md). Preserve both latest approved mockup images; no artwork was redrawn in this code stage.
