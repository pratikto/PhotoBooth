# Meong Photobooth — changelog

## 2026-10-26 — Simpler photo entry with mandatory tutorial

Remove idle CARA PAKAI and its two-column wrapper. Keep the existing full-width
invitation demo control; MULAI FOTO, invitation AYO FOTO and postgame photo
entry retain the existing once-per-visit tutorial gate. Tutorial acknowledgement
and safe return-to-idle reset remain. Reuse current v2 UI/actions/VisitFlow;
no new router or unrelated feature work.
Source `20453fe`: 800 full PASS/zero skips, 217.888s; twelve clean-source PNGs
verified and six affected views reviewed at both required sizes.
Matching-source CI 40248962384 all three jobs SUCCESS; optional native palm-assets
skip covered locally. Documentation/evidence follow-up skips redundant Actions.
[Scope, validation, Windows spot checks and rollback](qa/portrait-v2-photo-entry/README.md).

## 2026-10-25 — Print/Drive stage 2: native automatic fulfillment

Source **266b2c8**, 800 full PASS/zero skips, 15 new-feature focused PASS; CI
40208966127 all three jobs SUCCESS, 133 verified PNGs, required delivery views
reviewed and large QR screenshot pixels decoded. Stage 1 7b691c7 also had
three-job CI SUCCESS. Evidence-only delivery skips Actions; actual paper/phone/
cloud acceptance remains pending.

The v2 host now follows v1 approval → composition → one background print batch,
using existing durable PhotoTest/PhotoJobs. Explicit --drive prepares/resumes the
original isolated queue at startup; consent reflects verified-folder readiness.
Late prep leaves ads intact, progress updates preserve the result page, and the
original worker-encoded QR appears only after file verification. Slow/uncertain
prints, offline retry and retention holds stay explicit; no replay/bypass.
New native cases and seven delivery fixture states at both required sizes, plus
the eleven-item Submit/import form, accompany the existing v1 services.
[Scope, checks, commands and rollback](qa/portrait-v2-print-drive/README.md).

## 2026-10-25 — Print/Drive stage 1: explicit launch and delivery contracts

Owner prioritizes print and Drive only over watchdog; chooses automatic print
as v1 and background Drive. Reuse nine unchanged v1 backend/config/pool/queue/QR
files. Add explicit --print/--drive/--manual-print launch options, safe missing-
configuration code, true pool readiness and worker-encoded cached download QR
only after verified upload. Native auto-print/readiness/QR wiring follows in
stage 2; no actual device/provider/cloud action in fixture QA.
[Current scope/provenance/evidence](qa/portrait-v2-print-drive/README.md).

## 2026-10-25 — BUG-018 owner retest accepted for monitoring

Later targeted R01–R04 report: **4/4 checked, zero unchecked, no issue notes**.
Preserve initial 8/8 plus the hang note; later evidence supports OWNER-REPORTED
PASS / MONITORING for repeated/mixed input, busy close, lifecycle and next input/
restart. Tested HEAD/OS/display/device fields remain unknown; no exact-source
verification, formal closure or external P5 pass is inferred. Documentation-only
record, no runtime changes or new Actions run; prior twenty-cycle reports stand.
[Raw report and assessment](qa/portrait-v2-health-clicks/owner-retest-2026-10-25.json).

## 2026-10-25 — BUG-018 operator repeated-click correction

Source `ebb53fd`, final **785 full PASS / zero failures/errors/skips**, 37 focused
PASS. Matching-source CI 40189694738 all three jobs SUCCESS; 119 PNGs verified,
required operator views reviewed. At source delivery Windows confirmation was
pending; the later owner retest above records 4/4/no issues.
Evidence-only delivery skips CI; original v1 runtime/panel/worker unchanged.

Owner reports an app hang after pressing all health buttons rapidly, despite
eight checked boxes. Preserve the initial raw report and unknown tested HEAD;
H03/H04 prompted the later targeted retest. Three regressions exposed duplicate releases, unbounded fast-result
refreshes and disabled-held release acceptance. The v2 adapter now consumes one
fresh permitted press and drops same-button repeats for 0.75 seconds, with no
deferred actions/SFX. TUTUP remains independent while report/probe I/O is busy.
Original v1 UI/backend/worker stay unchanged; native mixed-pointer heartbeat/
close/reopen coverage and a fresh four-item Submit form accompany the fix.
The MOCK widget wait helper also drains a result completed during its final frame,
without extending its three-second budget or changing checkout runtime.
[Reproduction, validation and rollback](qa/portrait-v2-health-clicks/README.md).

## 2026-10-25 — Documentation consistency audit (English)

Stage 1 [`da375b3`](https://github.com/pratikto/PhotoBooth/commit/da375b3ace7048785bc558e45d10cf5a859709a1)
reconciles current README/index/roadmap/status/architecture/handover/backlog/test
ledger: latest operator source ea394e8 versus earlier P5 9433010. Older status
narratives remain available through immutable pre-audit Git links.

Stage 2 [`e4d0e89`](https://github.com/pratikto/PhotoBooth/commit/e4d0e8947c82821f5480615c0f689630a438d425)
reconciles technical/visual contracts, decisions/governance, branch applicability
and current bug context. The final stage labels historical
QA/blueprint stop gates; fixes obsolete
Device Health and BUG-017 pointers; distinguishes shared v1 guides from v2; and
provides English current P5/operator forms while retaining IDs/storage/cycle
logic. Detailed [findings, inventory and validation](qa/documentation-consistency-2026-10-25.md).
No application source, dependencies, workflows, assets or raw test evidence changed.


## 2026-10-25 — Operator increment final evidence

4c89e4f reused v1 foundation (73 focused PASS), then ea394e8 mounted the original
UI/worker with safe local reports. Final 780 full PASS/0 skips; CI 40157638369 all
three jobs SUCCESS, 119 PNGs verified and required views reviewed. Original v1 fourteen core files
unchanged. Eight-item operator Submit/import form verified; actual laptop and
merchant/P5 gates still pending. [Proof, commands and rollback](qa/portrait-v2-operator-health/README.md).


## 2026-10-25 — v1 operator panel/worker mounted in v2

Read-only Device Health reuse now has native v2 entry (F12/header hold), original
panel/label/worker, cached-frame/lazy-config adapters, safe local JSON export and
stale-input/probe/export lifecycle guards. No v1 app change, second camera,
settings mutation, order replay or production. Original 71 tests + provenance
and native fixtures retained. [Scope/proof/form](qa/portrait-v2-operator-health/README.md).


## 2026-10-25 — FEAT-008 operator health foundation reused for v2

Owner requests safe further source development while laptop tests wait, explicitly
reuse v1 to avoid duplicate work. Import latest read-only Device Health backend,
actual panel and original backend tests from dbbe055; extract the original v1
async refresh method verbatim with provenance. No current v1 application,
selection preference or customer flow changes. [Scope and proof](qa/portrait-v2-operator-health/README.md).


## 2026-10-25 — Earlier GUI v2 consolidation / reference audit

Owner requested GUI v2 documentation using each branch as a reference and named
v2 as the intended future primary branch. `ae90269` pinned 19 remote tips and
reference hashes; `fdafbe2` consolidated the current launch/roadmap/design/status/
QA/handover/backlog/decision/protocol guidance. The candidate classification of
Device Health applied at that point and was subsequently superseded by the
approved read-only operator increment above.

Owner preflight `0dc6555` ready was recorded without inventing metadata or passing
merchant/hardware. The earlier audit checked links/JSON/pinned refs and 208 P5
functional hashes; it did not rerun app tests, modify runtime/workflows or alter
master/default/reference branches. [Earlier QA](qa/gui-v2-docs-2026-10-25.md).


## Historical development entries

Entries below retain their original source/date. Former “current/latest”, next
steps and pending labels do not supersede the current status/test ledger.

> P5: add read-only readiness inventory/CLI using existing diagnostics, primary Windows display metadata, secret-free JSON import into reused Submit form, and focused/full unittest runner selection with native CI report artifacts. No provider/device acceptance fabricated. [Instructions](qa/portrait-v2-p5/README.md).


Add opt-in native Sandbox adapter, original HTTP/client/journal admission to existing P3 photo worker, isolated launcher/profile, recovery holds and offline end-to-end tests/screenshots. Default payments unchanged; local game promo never authorizes QRIS discount. [Details](qa/portrait-v2-sandbox/README.md).

# P4b Sandbox reuse — 2026-10-24

FEAT-020/022: import unchanged active QRIS backend/client/journal and relevant original tests from 3cc8a8e. Archive final owner 8/8 acceptance; BUG-017 monitoring. No payment mode enabled by default. [Scope/provenance](qa/portrait-v2-sandbox/README.md).

# Meong Photobooth — Documentation and release changelog

> 2026-10-24 — Restore native font rendering for main-app button captions, remove decorative button icons and unused bitmap caption generation, retain original Meong Fly frame material. Nine focused native checks PASS; Source d52a7d8 pushed/remote-verified; 546 final full PASS/zero skips, matching-source CI 40104190105 three-job SUCCESS and 99 artifact PNGs verified. [Evidence](qa/portrait-v2-readable-type/README.md).

> 2026-10-24 — Reuse actual original Meong Fly arcade_button/pixel_text/icons for main-app native buttons, with cached nine-slice material, readable whole-word captions and existing touch/audio/disabled guards. Larger Meong source c887d30 pushed/remote-verified/CI SUCCESS. Button source 25fd55c pushed/remote-verified; CI 40102001442 three-job SUCCESS. Final combined 546 full PASS, 15 focused PASS, 54 local captures and 99 CI PNGs verified; BUG-017 remains open. [Evidence](qa/portrait-v2-native-controls/README.md).

> 2026-10-24 — Archive owner 14/14/twenty-cycle retest at unknown HEAD; BUG-017 records video→video lag. Enlarge decorative header body using existing animation/film compositor; body stays in the header and turns without jumping. Eight focused native PASS, twelve PNGs verified and portrait screenshots reviewed. Next approved stage: original mini-game button style. [Evidence](qa/portrait-v2-native-controls/README.md).

> 2026-10-24 — Owner-requested animated header: same-level Meong and centered pixel lettering, one impact spin per pass, cached source-pixel limb poses, waving original-style trail and original camera/film compositor/emitter. Native pause/resize/retirement guards; 28 focused + 540 final full PASS, zero skips, actual Clock preview and twelve final native page captures. Source c242b97 pushed/remote-verified; matching-source CI 40073923004 all three jobs SUCCESS, 99 CI PNGs verified. [Evidence](qa/portrait-v2-player-anchor/README.md).

> 2026-10-24 — BUG-016: replace right-aligned original gameplay world with a centered shared translation. Add native player-position and landscape motion checks. 20 focused PASS; 45 synthetic native captures verified, required portrait and landscape reviewed. [Details](qa/portrait-v2-player-anchor/README.md).

> BUG-015/header/gallery final source b6a730a: matching-source CI 40059427863 all three jobs SUCCESS. Archive CI, source-bound test hashes and verified 50-image P4/MOCK artifact; runtime unchanged. [Evidence](qa/portrait-v2-motion-correction/README.md).

> 2026-10-24 owner correction: preserve original asteroid tempo/spacing (144bd60), center the MEONG PHOTOBOOTH wordmark, animate the existing mascot across its own header lane, float the gallery title above intact strips, and center both quote columns. Final 533 full local PASS, zero skips; [proof/form/rollback](qa/portrait-v2-motion-correction/README.md).

> BUG-015: remove nonlinear asteroid position mapping introduced by responsive layout; uniform full-path speed/spacing, unchanged original engine. 25 focused native tests PASS. [QA](qa/portrait-v2-motion-correction/README.md).

> Responsive source 5c81ea1: matching-source portrait CI 40056129151 all three jobs SUCCESS. CI evidence and checkpoint archived; runtime unchanged. [Proof](qa/portrait-v2-responsive-scene/README.md).

> 2026-10-24: replace separate game filler/fixed poster layout with cached responsive original-art components and one source sky; align hitboxes/film, retain original engine/compositor. Gallery quantity/total simplified, CETAK removed. 529 full local PASS, zero skips; [QA/screenshots/rollback](qa/portrait-v2-responsive-scene/README.md).

> Compact gallery quantity controls and prominent simulated total; remove CETAK and repeated price prose. 20 native focused checks PASS. See [current QA](qa/portrait-v2-responsive-scene/README.md).

> **P4 follow-up CI evidence (2026-10-24, docs only):** Three jobs SUCCESS at `f3172a5`; original artifact digest and all fifty P4 PNG hashes/dimensions verified, game contacts reviewed. No runtime change or new hardware PASS. [Verification](qa/portrait-v2-game-followup/README.md).

> **P4 game soundtrack/final regression (2026-10-24):** Add original 128 BPM minor-key game loop using existing synth instruments and single-owner GUI/game track switching. Preserve click, gain, video exclusivity, minimize/restore and close. Final 527 full PASS; native PCM and 39 focused audio PASS. Fifty game/MOCK captures checked. [Evidence](qa/portrait-v2-game-followup/README.md).

> **P4 winning quote, stage 2 (2026-10-24):** Share existing MOCK amount math with gallery preview, show subtotal/game reduction/net, and stop reapplying consumed wins including recovered admission. 38 targeted tests PASS. All reductions remain local SIMULASI. [Evidence](qa/portrait-v2-game-followup/README.md).

> **P4 Windows follow-up, stage 1 (2026-10-24):** Fill game host/background with current window, preserve original playfield proportions, remove non-playing return footer and disable mouse multitouch simulation in the v2 launcher. Native red-dot reproduction and 18 focused tests PASS; scanner/payment remain off. [Evidence](qa/portrait-v2-game-followup/README.md).

> **Meong reuse CI evidence (2026-10-24, docs only):** Three jobs SUCCESS at `d267d89`; original artifact digest matched, four clean-source reports and all fifty P4 image hashes/dimensions checked; thirty game captures reviewed. Documentation-only filter avoids repeating GUI CI for this archive. [Verification](qa/portrait-v2-meong-reuse/README.md).

> **Meong Fly reuse, stage 2 (2026-10-24):** Replace custom v2 game view with direct original MeongFlyStage/MeongFlyFlow; engine becomes compatibility imports of the same class. Preserve original pose/film/parallax/rainbow/score/impact and async v2 routing guards. Remove redundant asteroid assets; fix stale invalid-code warning. 512 full PASS, 14 native pixel-identical fixtures and 30 reviewed captures. [Evidence](qa/portrait-v2-meong-reuse/README.md).

> **Meong Fly reuse correction, stage 1 (2026-10-24):** Prior v2 reused physics but recreated the view. Add latest reference modules/assets/tests byte-for-byte from `672e3f7`; 98 original tests PASS. Actual renderer wiring follows as a separate push. [Diagnosis/provenance](qa/portrait-v2-meong-reuse/README.md).

> **P4 source evidence archived (2026-10-23, docs only):** All three CI jobs SUCCESS at `97b5596` ([39973934595](https://github.com/pratikto/PhotoBooth/actions/runs/39973934595)). Original artifact digest matches GitHub; four clean-source reports and all 42 P4 image hashes/dimensions verified, contact sheets reviewed. No runtime change or Windows/provider certification. [Evidence/checkpoints](qa/portrait-v2-p4/README.md).

> **P4b MOCK (2026-10-23):** Add local authoritative quote, conditional simulated promo, stable-key orders, protected pending/unknown/expiry/recovery and atomic one-use handoff to P3 consent. Default checkout entry off; nonpayable text QR and explicit simulation controls only. Fix compact pending overflow found during review. 406 full PASS, 20 final checkout captures and a tested 28-item Submit form. [Evidence and limits](qa/portrait-v2-p4/README.md).

> **P4a (2026-10-23):** Add native manual-code/game/result pages, fixed-canvas asteroid display and safe tutorial/gallery handoff. Guard stale input, pause/minimize and durable consumed attempts; preserve existing gallery amounts. 377 full PASS and 22 reviewed screenshots. [Tests/provenance/rollback](qa/portrait-v2-p4/README.md).

> **P4 stage 1 (2026-10-23):** Owner-approved continuation after P3 acceptance. Copy the audited pure game engine without merging the reference branch; add local DEMO-only SQLite claim/result records and single-flight background jobs. 56 targeted tests PASS. GUI integration follows; no real scanner, payable QR or redeemable discount enabled. [Scope/tests/provenance](qa/portrait-v2-p4/README.md).

> **P3 Windows owner result recorded (2026-10-23, documentation only):** Preserve the focused 16/16 report, twenty cycles and no issue notes. Preview/button lag becomes OWNER-REPORTED PASS / MONITORING; physical print batch/uncertain-restart checks are now explicitly owner-reported passes. Keep HEAD/device metadata unknown, A01 metadata incomplete and unrelated full-P3/Drive-retention gates open. No application change or new test run is implied. [Report and audit](qa/portrait-v2-preview-redraw/README.md).

> **P3 preview/first-use correction (2026-10-23):** Reproduce missing redraw with actual window flips/pixel readback (baseline FAIL → fixed PASS), then request redraw per new reused camera texture as v1 does (`0d08f07`, 350 full PASS). Prepare one ready strip texture or silent camera effect per idle turn (`ef0fcb0`, 353 full PASS). Preserve owner raw 36/40 report and contradictions, add focused Submit form and printer opt-in instructions. Windows lag/physical print gates remain OPEN. [Evidence and rollback](qa/portrait-v2-preview-redraw/README.md).

> **P3 stage 3 (2026-10-23):** Archive final 349/349 native-fixture regression and 71 focused passes, matching-source three-job CI at `a059d30`, verified original artifact digest and 40 image hashes/contact sheets. Add a browser-verified 40-item Windows form with Submit, camera/index/lag fields, missing-metadata status, separate storage and preserved twenty-cycle gate. Document owner raw 21/34, open device bugs, optional dependency setup and rollback checkpoints; no runtime or legacy-service change in this stage. [Final verification](qa/portrait-v2-p3-retest/final-verification.json).


> **P3 staged follow-up (2026-10-23, stage 2):** Restore optional v1 open-palm input in v2, sharing the manual countdown/quota and release latch. Load native detectors off GUI, rate-limit offers, preserve stale-page checks and show face/palm progress/fallback hints. Log input flags and include audio time in slow-action diagnostics. Existing v1 services/models unchanged. 348 full tests PASS with native fixtures; final 71 focused PASS. [Source/device limits](qa/portrait-v2-p3-retest/README.md).


> **P3 staged follow-up (2026-10-23, stage 1):** Add bounded worker-owned RGB preview conversion and aggregate diagnostic timings. Preserve the current view while photo I/O runs, disable controls and rebuild once on completion; stale releases remain inert. Record owner’s 21/34 Windows result with unknown tested HEAD; open BUG-013/014. 77 focused PASS, simulated timing improvement; Windows performance is not certified. [Evidence and rollback](qa/portrait-v2-p3-retest/README.md).


## 2026-10-23 — P3 exact-source CI and evidence archived

- `569dbf5` passes all three jobs in [CI 39880474594](https://github.com/pratikto/PhotoBooth/actions/runs/39880474594), including Windows SDL dummy audio, real widget tests, isolated photo/Drive tests and 40 main synthetic screenshots. This supersedes the failed CI install at `c04534f`.
- Downloaded original artifact, matched archive SHA-256, verified six clean-source reports and all 40 main image hashes, reviewed native P3 and browsing/short-window contact sheets. Source/media hash checks confirm 13 legacy v1 files unchanged.
- Preserve physical device gates and BUG-009/012 status; add operator entry instructions and [final verification](qa/portrait-v2-p3/final-verification.json). No runtime changes in this documentation follow-up.


## 2026-10-23 — P3 CI QR dependency correction

- Exact-source CI at `c04534f` correctly failed the Drive-enabled composition test because the minimum desktop install omitted the existing `qrcode[pil]` dependency. Add it to the CI install; runtime code and assertions unchanged.
- Rechecked 11 photo adapter tests locally; replacement exact-source CI is required before declaring the workflow PASS. [Failure/correction record](qa/portrait-v2-p3/ci-dependency-correction.json).


## 2026-10-23 — P3b native photo test flow

- Gallery UJI FOTO opens explicit nonfinancial consent, live mirrored camera, five-second countdown, three unmirrored originals, one selected retake per session and full strip results.
- Reuse existing composition, local retention, print-copy and Drive services under isolated v2 storage/IDs. Worker-owned I/O, stale-touch guards, interrupted-countdown cancellation and bounded post-window device cleanup.
- Test prints persist before send, reject duplicate retries and require operator acknowledgement for uncertainty; Drive holds uploads without backend retention acknowledgement. Default local mode has no fake download QR.
- Original v2 shutter plays only after successful capture/retake save. Add native P3 screenshot recorder and 34-item Windows form with Submit.
- [QA evidence, limitations and rollback](qa/portrait-v2-p3/README.md); physical device acceptance remains open.


## 2026-10-23 — Portrait v2 original shutter

- New 0.30 s mechanical shutter with a soft release, selected only by v2; v1 audio bytes/controller unchanged.
- 32 audio tests PASS, including native SDL dummy PCM for the new file. Speaker timbre remains an operator check.
- Evidence and rollback: [P3 QA](qa/portrait-v2-p3/README.md).


This file tracks **actual verified repository/document changes**, not successful live booth operation. Historical test assertions are kept in [FEATURE_STATUS.md](FEATURE_STATUS.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and [QA evidence](qa/README.md). Application code can be considered released only under [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md).

## [Unreleased — P3 authorized; P3a asynchronous camera and face invitation] — 2026-10-23

- Owner authorizes P3a/P3b on the existing v2 branch. Add one asynchronous camera adapter using the existing camera service and local face worker/hold policy; no idle recording or model download.
- Connect fresh same-page face observations to the existing advert overlay, preserving ad playback, manual entry, cooldown and lifecycle ownership. Disable retired overlay buttons without affecting sibling ad controls.
- 86 focused PASS; full 321 run / 319 PASS / 2 optional skips; twelve fresh captures reviewed and pixel-identical to prior pages. P3a camera/face hardware acceptance remains open; P3b follows as a separately tested stage within the same authorization. [Evidence and scope](qa/portrait-v2-p3/README.md).

## [Unreleased — owner confirms return-to-advert flow working] — 2026-10-23

- Record the owner's follow-up “sudah oke” after the correction/diagnostic retest instructions. BUG-012 becomes OWNER-REPORTED PASS / MONITORING; no further crash patch is planned while it works.
- Preserve unknown post-update tested HEAD/cycle count and the unchecked F05/F06 twenty-cycle gate. Do not convert the earlier five-cycle report or this brief confirmation into exact-source / full-duration acceptance. Documentation-only update; runtime, existing test transcripts and source CI results unchanged. [Confirmation and limits](qa/portrait-v2-return-ad-crash/owner-confirmation.json).

## [Unreleased — return-to-advert crash investigation and diagnostics] — 2026-10-23

- Preserve the owner's raw V4 33/35 checked result at five cycles and unknown HEAD; the explicit crash on return overrides overall navigation acceptance. Track BUG-012 OPEN; F05/F06 remain unverified.
- Reproduce and correct Kivy Video's MP4-as-still-image probe while preserving real decoding and explicit posters. This fixes the demonstrated loader error; it does not establish the cause of the owner's process exit.
- Add per-run local diagnostic logs before native provider imports, source HEAD at startup, page-stage breadcrumbs, Python/worker tracebacks and available fatal native stacks. Keep startup usable if logs cannot be created. Seven focused diagnostic checks and the video regression are included in CI.
- Local 79 focused PASS; full 314 run / 312 PASS / 2 optional model skips. Twenty native-video/audio cycles complete before and after on Linux; real dedicated-launcher startup/teardown also passes. Code `bef4014` passes exact-SHA CI 39869369246, all three jobs, including 38 Windows native audio/diagnostic tests. Original artifact ZIP digest and 24 page / nine motion PNGs verified and reviewed. Windows crash is not reproduced and remains BLOCKED pending diagnostic retest. [Evidence, limitations and next Windows check](qa/portrait-v2-return-ad-crash/README.md).

## [Unreleased — gallery and animation Windows checklist V4] — 2026-10-23

- Add a clickable 35-item form for the latest gallery, pixel branding, swipe/motion, response, audio and lifecycle. Submit Hasil prepares a prompt for manual copy/send; download, print and separate local persistence are retained.
- F05–F06 cannot pass without at least twenty reported cycles; reaching twenty never auto-passes them. Exports explicitly qualify missing tested HEAD and unmet duration. JavaScript syntax and 11 DOM behavior checks PASS. [Form, evidence and usage](qa/portrait-v2-gallery-focus/README.md). Application source and existing Windows acceptance are unchanged.

## [Unreleased — gallery focus, moving strips and pixel typography] — 2026-10-22

- Give the vertical strips most of the gallery, keep previous/current/next fully visible, and float the arrows in the preview's lower corners. Compact the header, copy summary and footer; raise preview resolution without changing print masters.
- Slide actual images for 200 ms and follow finger drags. Pool the image widgets, replace motion on rapid input, select once per gesture, and cancel motion on resize/minimize/retirement. Match the read-only mini-game's pixel title with display-only glyph data.
- 71 focused tests PASS; full suite 306 run / 304 PASS / 2 optional model skips; three fresh-process 150% density checks PASS. Thirty local page PNGs and nine motion frames reviewed, including 800×1280 and 452×900. Source `5a568bf` passes exact-SHA CI 39803887478 (all three jobs, including 31 native Windows audio tests); original artifact ZIP digest, 24 page PNGs and nine motion hashes verified and reviewed. [Evidence, GIF, source hashes and Windows retest](qa/portrait-v2-gallery-focus/README.md). Windows preference/response and twenty-cycle owner acceptance remain open.

## [Unreleased — owner retest and button response] — 2026-10-22

- Record 41 checked boxes with ten completed Windows cycles and an unknown tested HEAD; G03/G06 twenty-cycle acceptance stays open. Owner confirms resize works and requests larger strip previews and visible sliding motion.
- Warm silent WAV handles and CPU strip previews outside button callbacks; play a valid click before navigation, preserve it across page handoffs, and keep camera effects/suspend/close ownership. Copy changes only update order text.
- 68 focused tests PASS, including worker cancellation/nonblocking access and native PCM checks. Exact response source `67e9da8` passes all three CI jobs (39798019411). Local timings and hardware limits are preserved in the [current evidence](qa/portrait-v2-gallery-focus/README.md).

## [Unreleased — post-crash Windows checklist form] — 2026-10-22

- Add a clickable 41-item retest form beginning with startup / MULAI FOTO / tutorial-to-gallery crash checks, plus cycle-count metadata and the existing audio/resize checks. Submit Hasil prepares a prompt for manual paste into chat; separate storage keeps earlier checkmarks from passing the new gate.
- JavaScript syntax and DOM behavior checks PASS. [Form and usage](qa/portrait-v2-start-photo-crash/windows-checklist.html). Application source and existing device-acceptance status are unchanged.

## [Unreleased — Windows MULAI FOTO crash correction] — 2026-10-22

- Owner log identifies Windows Python 3.12 TypeError from CDLL(None, handle=...) in the previous correction, followed by a native ffpyplayer channel-layout error and reported app exit.
- Name the already loaded SDL2 mixer DLL explicitly. Default Windows WAV fallback tries plain SDL2 and otherwise returns unavailable audio; it no longer automatically opens a second FFmpeg WAV decoder after that failure. Explicit provider overrides remain respected.
- 62 focused checks PASS, five audio-enabled start-button visits, native 20-cycle PCM checks, complete regression 297 run / 295 PASS / 2 optional skips and twelve reviewed screenshots. Genuine Windows CI now passes 29 audio tests; exact code SHA `471bbd9`, run 39742760872, all three jobs SUCCESS. Physical operator retest remains open. [Diagnosis, evidence, checkpoints and retest](qa/portrait-v2-start-photo-crash/README.md).

## [Unreleased — live window scaling and repeat-use retest] — 2026-10-22

- Scale the entire v2 page to retain its minimum content budget in short/high-DPI windows, preserving gallery previews, cart state, media and audio ownership during live resize. Match native touch/swipe coordinates and discard resize-interrupted drags.
- Review 30 synthetic screenshots across five sizes, including 800×1280 and 452×900. 55 focused tests PASS; full suite 290 run / 288 PASS / 2 optional model skips; two fresh-process 150% density checks PASS.
- Exact-SHA CI also succeeds for audio `16f7918` (39738222976) and layout `2deefd8` (39739671551), both jobs each. Final original CI artifact digest, 24 PNG hashes and clean-source manifests verified. Windows ffpyplayer wheel inspection confirms its SDL_mixer backend; this is not execution on owner hardware.
- Add a separate 38-item repeat/resize retest HTML with Submit Hasil, prepared prompt, local persistence and copy/download; DOM checks PASS. [Evidence, source hashes, screenshots and rollback](qa/portrait-v2-retest-9a9e18e/README.md). Owner Windows acceptance stays open.

## [Unreleased — repeated Windows audio correction] — 2026-10-22

- Record owner retest at `9a9e18e`: 27/32 checklist total, single-flow C/D success qualified by repeated music/click loss; B01–B05 untested because gallery was not visible.
- Reproduce silent SDL channel reuse despite state=play and positive WAV gain. Restore unused channel gains before v2 WAV allocation, preserving playing ad channels and explicit provider overrides.
- 54 focused tests PASS, including native post-mix PCM across 20 repeated visits and silence after close. [Evidence, rollback and device retest](qa/portrait-v2-retest-9a9e18e/README.md). Windows repeated-use acceptance stays open; responsive layout follow-up is next.

## [Unreleased — Windows visual branding follow-up] — 2026-10-22

- Reuse exact transparent camera-cat artwork from the read-only Meong Fly reference in a native shared Meong lockup. Add it to every implemented page, including the template gallery; replace the game preview white plate with one hero brand. No game code or v1/QR logo changes.
- Check real rendered wordmark pixels per screenshot, preserve artwork provenance and add ordered tutorial/brand bounds regressions. 52 targeted tests PASS; complete regression 287 run / 285 PASS / 2 optional model-asset skips; twelve screenshots reviewed at both portrait sizes. [Evidence and Windows retest](qa/portrait-v2-windows-followup/README.md).
- Both source checkpoints independently pass CI: input/audio `37c0024` / run 39710969312 and shared brand `faa1c7d` / run 39711930820. Remote HEADs were verified after each push. Owner Windows acceptance remains 29/38 at the audited version until retested.

## [Unreleased — Windows input/audio follow-up] — 2026-10-22

- Record owner Windows audit at `3cfa9d2`: 29/38 checked, with D04 swipe explicitly failing and audio/order/relaunch checks still open. Preserve positive device observations without claiming complete acceptance.
- Fix pointer-grab/normalized-coordinate swipe ownership and desktop minimize/restore bindings. Centralize one click per enabled action on every page; stale/disabled actions remain silent.
- Honor latest owner policy: image/fallback ads use GUI music, video ads use their own audio; notify music ownership before a decoder can start. The optional shared-player callback preserves legacy callers and muted payment ads.
- 50 targeted synthetic tests PASS; full suite 285 run / 283 PASS / 2 optional model-asset skips. Native SDL2 dummy-audio lifecycle PASS and twelve portrait states rendered. [Audit, rollback and retest](qa/portrait-v2-windows-acceptance-3cfa9d2.md). Native/device evidence remains distinguished.

## [Unreleased — P2.6–P2.8 non-hardware gates closed] — 2026-10-22

- Downloaded P2.7/P2.8 original CI artifacts after network publication; verified both ZIP digests, all dimensions and P2.8 clean-source/PNG manifests. Reviewed every page at 800×1280 and 452×900; no remaining synthetic visual blocker.
- Exact milestone SHAs and both jobs pass CI. Final local suites: 45 PASS, no failures/errors/skips. Archive original CI PNGs, manifests, hashes, metadata and closure transcript; update QA gate, Windows checklist and final rollback checkpoint `0fbf158`.
- [Final report](qa/portrait-v2-p28/README.md). Windows audio/touch and BUG-001/007/009 remain open; no master merge, gameplay, scanner, discount or production payment enablement.

## [Unreleased — post-publish P2 QA verification] — 2026-10-22

- Verified exact-SHA CI SUCCESS and both jobs for P2.6, P2.7 and P2.8. Downloaded P2.6 artifact, verified its ZIP digest and inspected all twelve original CI screenshots at 800×1280 and 452×900; P2.6 non-hardware gate PASS.
- Re-ran 45 tests and both renderer viewports on clean published `0fbf158`; all local checks passed. Preserve CI metadata, original P2.6 PNGs, hashes and post-publish manifests. [Evidence](qa/portrait-v2-ci/README.md).
- P2.7/P2.8 artifact downloads require two additional GitHub storage hosts; exact domains saved to draft. Their visual gate remains BLOCKED. No application/renderer changes or hardware acceptance.

## [Unreleased — P2.8 evidence checkpoint, BLOCKED] — 2026-10-21

- Harden screenshot recording with sequential scheduling, expected-route and dimension validation, and per-viewport SHA-256/source manifests. 45 portrait tests and twelve rerenders passed locally; all pixels match the reviewed P2.7 images.
- Document exact published checkpoints, verified P2.6 CI, pending P2.7 CI, blocked artifact download and unrun Windows acceptance checklist. [Evidence report](qa/portrait-v2-p28/README.md). P2.8 is **not complete**; no production/hardware claims.

## [Unreleased — P2.7 portrait lifecycle] — 2026-10-21

- Retire page-owned button/swipe callbacks; block input and browsing timeout while suspended, refresh inactivity on resume, and ignore resume after app stop.
- Stop effects as well as music during suspend and silent-page handoff; game preview owns no GUI audio. Increase small CTA heights to 48dp.
- 45 local portrait tests PASS, real touch/scroll checks at both target sizes, native SDL2 dummy-audio smoke PASS, twelve new synthetic screenshots. [Evidence and rollback](qa/portrait-v2-p27/README.md). Hardware and matching-SHA CI artifact gate remain open.

## [Unreleased — P2.6 portrait QA] — 2026-10-21

- Readable disabled payment/scanner labels in GUI v2; preserve unavailable actions and shared pixel palette.
- Added a real-widget regression; 40 portrait tests passed locally, and twelve synthetic screenshots were generated at both target sizes. Evidence: [P2.6 local review](qa/portrait-v2-p26/README.md). Matching-SHA CI remains pending; no hardware acceptance claimed.
- Rollback before this milestone: `e888d9945bc8c0a4c74bd1a8de57e946acb26204`.

## [Unreleased — docs-only, post-v1.0.0] — 2026-10-19

- Owner approved a **documentation-only** reconciliation on a dedicated `docs/post-v1-release-reconciliation-20261019` branch. Update current README/index, source status, bug/backlog, decisions, QA and technical-guide headings to match the already tagged GitHub `v1.0.0` pre-release. Preserve earlier dated test/failure history and explicit hardware acceptance gaps. The documentation PR is **not part of the immutable v1 tag**; review and merge it without rewriting the release.
- CI evidence at the immutable v1 SHA: [Kiosk GUI Actions 39185986245](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245) **233 pass / 2 skips / 87 renders / 0 errors** and [Dither 39185986273](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273) **48 pass**. **No new hardware test**, no Python production-source, printer, ads, QRIS, Apps Script or customer cloud changes.

## [v1.0.0] — 2026-10-19 (Kivy source baseline)

- **Approved promotion:** owner explicitly approved the version-one baseline process: preserve the old `master` tip, make `feature/kivy-gui` the new `master`, then tag the tested merged source as `v1.0.0`. Backup: `backup/master-pre-v1-20261019` at `d4852cb5`.
- **CI controls:** enable Kiosk GUI and Dither workflows for pushes to `master`, and correct Kiosk pull-request target from nonexistent `main` to `master`. A one-time GitHub release workflow publishes the v1 tag only after both tests have passed on the exact `master` release-baseline commit (including any release-workflow correction).
- **Status:** release notes and known limitations are in [releases/v1.0.0.md](releases/v1.0.0.md). This denotes an **auditable versioned source baseline**, not real QRIS, verified Drive retention, or physical Windows production acceptance. Tag/ref and GitHub pre-release **verified**: [v1.0.0](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0), SHA `07ce51d2022ab5673a7a27e744e5e5757fbb3d08`. Historical statements below that the tag had not been published are superseded.
- The older sections titled **Unreleased** below are dated **pre-v1 historical development records**. Their statements that no branch merge or release had been authorized were true when written, and are superseded only for this specifically approved version promotion.

## [Unreleased] — 2026-10-19

### QA-QR-001 — stabilize flaky DEMO QR screenshot regression (CI-only)

- **Owner field report:** QR works normally on the Windows laptop; no user-facing QR change requested or made. GitHub Kiosk CI had intermittent QRCodeDetector failures while decoding screenshots of the **same production source** (example [39176198126](https://github.com/pratikto/PhotoBooth/actions/runs/39176198126): initial FAIL and subsequent success). A changing `uuid4` DEMO attempt ID and a one-scale detector are supported contributors; there is no evidence of an actual booth QR failure.
- **Test-only commit [`e46812b8`](https://github.com/pratikto/PhotoBooth/commit/e46812b8c9f66c548bccebb1e9fc45e3c89afeef):** `tools/render_gui.py` now creates stable unique synthetic DEMO IDs, while `tools/ci_qr_pixels.py` strictly decodes the **on-screen captured crop** at 1x/2x/3x nearest-neighbour scales. `tests/test_ci_qr_pixels.py` adds three positive/negative tests including a covered or blank QR which cannot pass. Exact payload checks were not relaxed.
- **Verification:** [Kiosk GUI Actions 39178452927](https://github.com/pratikto/PhotoBooth/actions/runs/39178452927) **3 consecutive SUCCESS attempts at identical SHA**: each 235 total unit tests (**233 PASS, 2 SKIP, no errors**) and **87 screenshot renders / 0 errors**. [Dither 39178452898](https://github.com/pratikto/PhotoBooth/actions/runs/39178452898) also SUCCESS.
- **Scope:** no `photobooth/` production changes, no payment or printer transport modifications, no workflow YAML change, no branch merge to `master`. Label **QA-QR-001 MONITORING**, not proof all possible QR screenshots will pass forever. A subsequent documentation-only HEAD still requires its own CI status.


### Owner-approved documentation reconciliation — active Kivy status and preserved history

- **Scope:** documentation only on `feature/kivy-gui`, with **no Kivy source edits**, Apps Script deployment, new feature, branch merge, print-spool change or production QRIS integration. Current **default repository branch remains `master` and is intentionally unmerged**.
- **Source/test baseline:** audited `c40f33f5` with [Kiosk GUI CI 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762) **SUCCESS** (230 PASS, 2 skipped, 87 renders / 0 errors) and [Dither CI 39145145764](https://github.com/pratikto/PhotoBooth/actions/runs/39145145764) **SUCCESS**. The *new documentation-only HEAD* must pass its own Actions run before claiming current-HEAD CI green.
- **Status normalization:** FEAT-001 DEMO fee per selected template plus requested print copies and FEAT-003 capture mirroring **OWNER TESTED PASS**; BUG-011 real Windows copy count **OWNER TESTED PASS / MONITORING**; BUG-002/003/004/005/006/008/010 owner-reported PASS; BUG-001/007 audio deferred, BUG-009 Drive 30-day cleanup **OPEN / not deployed-verified**, FEAT-002 scanner and FEAT-020 real QRIS deferred/not implemented.
- **Historical evidence preservation:** current status banners and dated **HISTORICAL / SUPERSEDED** labels added to README, canonical status/bug/backlog, architecture, handover, checklist, technical printer/ads/dither/retention guides, QA dossier/index and asset READMEs. Prior FEAT-011 experiment and earlier failed CI/printer/QR/video reports kept with timestamps; they do not override subsequent owner results or fixes.
- **Scoped documentation commits:** [README/index `8a142bc`](https://github.com/pratikto/PhotoBooth/commit/8a142bc1113874542b46ce3020d62b9524f92b10), [architecture/status/backlog `d177f54`](https://github.com/pratikto/PhotoBooth/commit/d177f54197fc35b56d9b6ffe0a143f684955d1fe), [handover/checklist/governance `8b65b26`](https://github.com/pratikto/PhotoBooth/commit/8b65b26757b479f4403ada51c56952dfd4fb20ec), [technical guides `1261791`](https://github.com/pratikto/PhotoBooth/commit/1261791d6c93f5cf1f632f944572d67d558324d3), [dated QA reports `00c084a`](https://github.com/pratikto/PhotoBooth/commit/00c084a3eb0b24c10d96bd1ef911aad4cb3d1fa3), plus this final changelog/asset documentation commit.
- **CI configuration observation, not changed here:** `.github/workflows/kiosk-gui.yml` has a historical PR trigger on `main` despite the actual default branch being `master`. Correcting it is **a separate CI-code change requiring explicit owner approval**; ordinary pushes to `feature/kivy-gui` already trigger full GUI QA.
- **Release caution:** `OWNER REPORTED`, `OWNER TESTED`, mocked CI and explicit Windows per-case records have different evidence levels. No hardware test matrix is invented, and the app is not marked RELEASED.

## [Unreleased] — 2026-10-18

### QA — Kiosk GUI Regression green after targeted legacy test reconciliation

- **Owner-approved QA remediation, no production code changes.** Kiosk GUI had a longstanding failed full `unittest` job whose tracebacks were hidden by Kivy logging. Diagnostic-runner commits [`28745cda`](https://github.com/pratikto/PhotoBooth/commit/28745cdabdee69bcd7c21e79aba611c2d2aa4dc8), [`9dcebfd2`](https://github.com/pratikto/PhotoBooth/commit/9dcebfd27d9e0f22688cecf9842fef9764fd2978), [`b5a9ee1a`](https://github.com/pratikto/PhotoBooth/commit/b5a9ee1a6bb0e09a2af78ec31ed0389a1f8d1d92), [`2efb76d7`](https://github.com/pratikto/PhotoBooth/commit/2efb76d796b120fe400361044c427dccce19f827) make existing unittest discovery and failures reliably visible/artifact-backed.
- **Actual root causes:** original restored suite had 17 failing assertions: stale FEAT-001 base/session + print-copy price and capture count, pre-tutorial ad navigation, old Settings shortcut, obsolete music audition/no-restart expectation, asynchronous printer's protected NEXT/SELESAI actions and Windows printer simulation incorrectly running down the Linux USB path. None warranted reverting owner-tested application functionality.
- **Scoped test-only changes:** `tests/test_camera_recovery.py` [`9e252f66`](https://github.com/pratikto/PhotoBooth/commit/9e252f6690d16d90a3402fad3bf8dd2bba0c60ac) and [`9826d3cf`](https://github.com/pratikto/PhotoBooth/commit/9826d3cf95bdde0f297bb26af6ada914f0a396a5); `test_carousel.py` [`0a765189`](https://github.com/pratikto/PhotoBooth/commit/0a7651895f4951177f814122b6e7031bd30b705e); `test_kiosk_motion_audio.py` [`26ac53e4`](https://github.com/pratikto/PhotoBooth/commit/26ac53e43735b0126d96c9f111486f5ab887fb92), [`35b2c1f3`](https://github.com/pratikto/PhotoBooth/commit/35b2c1f3d038ef95a41f76e9da36e17b34c26246), [`f129dd9e`](https://github.com/pratikto/PhotoBooth/commit/f129dd9ecb14b2d554dd83022745452764f5282d); `test_kiosk_advertising.py` and `test_kiosk_controller.py` for tutorial flow/camera-ready gate; `test_shared_printer_payment.py` for Windows driver fake. The test validations were **not skipped or suppressed**.
- **Verification:** [Kiosk GUI Actions 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476) at `f129dd9e`: **SUCCESS**. Python compile PASS; `232` unit tests (**230 PASS / 2 SKIP / 0 FAIL / 0 ERROR**); **87 screenshots / 0 render/QR errors**. An intermediate 800×600 enlarged DEMO QR decode failure did not recur in the complete final render; no production rendering fix was made. [Full QA dossier](qa/KIOSK-GUI-REGRESSION-2026-10-18.md). This is desktop Linux synthetic QA, **not** Windows hardware certification or a release.
- **Risk preservation:** no change to `photobooth/`, Windows RAW `EndDocPrinter`, Floyd printer profile, FEAT-003 mirror UVs, ads, audio manager, QRIS DEMO or `apps_script/Code.gs`. BUG-009 Drive retention and audio BUG-001/007 remain unresolved/deferred.

### FEAT-003 — owner confirms Windows live-camera mirror PASS (docs only)

- **Owner test confirmation (2026-10-18):** Following the FEAT-003 capture mirror rollout, owner reports **"sip udah sesuai. PASS"**. Record **OWNER TESTED PASS** for the implemented capture preview (initial/live/countdown/retake); the actual hardware result is a user report, while the [dedicated synthetic Kivy GPU Actions run 39139208320](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320) independently **PASSED**. Do not fabricate local checkout SHA, exact per-case results, printer photos or an overall Kiosk GUI PASS.
- **Scope boundaries:** Original stored/printed photographs, QR/text, face/palm input are deliberately unmirrored. FEAT-002 receipt scanner/overlay remains deferred and **not** exercised by this acceptance. The update is **documentation only**; no source code, camera driver, payment, printer, `Code.gs`, branch merge or deployment change.
- See [FEAT-003 backlog specification](next_step.md), [feature status](FEATURE_STATUS.md), [checklist](test_checklist.md), [DEC-012](DECISIONS.md) and [handover](DEVELOPMENT_HANDOVER.md).

### HISTORICAL FEAT-003 implementation-stage note — subsequently OWNER TESTED PASS

- **Owner authorization:** Proceed with FEAT-003 on existing `feature/kivy-gui` after BUG-011 owner-tested PASS. Source baseline: [`c0cb0d84`](https://github.com/pratikto/PhotoBooth/commit/c0cb0d846512233ebff3f625e3c002e2c942485c).
- [`6f8c8ddf`](https://github.com/pratikto/PhotoBooth/commit/6f8c8ddfcb53d35070213c6fda72b8485232f280): shared `ui_kivy._new_display_texture` retains vertical UV correction and applies horizontal flip **only** for live camera view; both initial Pillow/ready/retake and streaming BGR use the same orientation without CPU flipping. **Raw frames, face/palm inference, saved JPEG/review, composed photo, print, QR/text/logo remain unmirrored.** No change to `app.py`/printer/Drive/QRIS/ads/audio code.
- [`e99cbb26`](https://github.com/pratikto/PhotoBooth/commit/e99cbb26b485d7497642953c04e09c223dab0c6c) plus [`1698bd94`](https://github.com/pratikto/PhotoBooth/commit/1698bd942fb21a85266b84a33495165b55e086bf): Kivy GPU regression covers first frame, stream texture reuse, large-frame resize, countdown/retake, unchanged BGR/Pillow and ordinary saved/review/result orientation.
- [`307e779e`](https://github.com/pratikto/PhotoBooth/commit/307e779e271ba6deb439b3bbf91343d02c9b30c7): isolated [`feat003-mirror.yml`](../.github/workflows/feat003-mirror.yml). [Actions run 39139208320](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320) **PASS** (1 focused Kivy GPU test plus source/test compile, synthetic data, Ubuntu/Python 3.12/Xvfb). **Not physical Windows camera acceptance** and not a full GUI regression PASS.
- The existing camera preview belongs only to the capture/retake workflow. **FEAT-002 receipt scanner does not yet exist**; that later preview must reuse the same mirror renderer but decode unmirrored originals and map overlays correctly when separately approved. Do not claim scanner tests or production release.
- Documented affected module, dependencies, rollback and owner hardware checklist in [next_step.md](next_step.md), [FEATURE_STATUS.md](FEATURE_STATUS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [test_checklist.md](test_checklist.md) and [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md).

### Owner accepts FEAT-001 pricing and BUG-011 physical-copy correction (documentation-only status update)

### Follow-up owner verification — BUG-011 explicitly tested and passed (documentation only)

- **2026-10-18:** After the prior printer repair and initial **"sip udah bener"** response, the owner expressly confirmed **"bug 11 udah aku test dan lolos"**. Record **OWNER TESTED PASS** for the actual Windows copy-quantity defect, and keep **MONITORING** only for future regression. Pricing was already confirmed correct. This supersedes weaker previous wording **OWNER REPORTED PASS** for this specific bug, but does **not** imply full device matrix coverage, CLOSED/RELEASED status or a green Kiosk GUI CI workflow.
- Source of operational evidence: owner's own hands-on statement (no instrumented local test log, exact local SHA, copy-count case table or driver name supplied). Independent source CI remains [15/15 focused PASS](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707); [full Kiosk GUI CI](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) remains separately **FAIL** on the checked baseline. **No app/printer code, branch merge, new CI execution or deployment** in this documentation follow-up.

- **2026-10-18 Windows-owner evidence:** The owner first confirmed DEMO pricing was correct and reported the number of physically printed copies was wrong; after the existing Windows RAW fix and copy-count retest, the owner responded **"sip udah bener"**. Record **FEAT-001 core behavior OWNER REPORTED PASS**, and reclassify **BUG-011 to OWNER REPORTED PASS — MONITORING** (removed from active fix work, *not formally CLOSED or RELEASED*). The exact selected-vs-printed counts, device SHA, queue name and paper images were not provided, so none are fabricated.
- **No new source changes in this documentation event.** The functional fixes were already committed: [`4608fcc9`](https://github.com/pratikto/PhotoBooth/commit/4608fcc9ec96c8eabeb01ddbd64059830af2bf62) repeats complete image+cut sequences in one RAW payload; [`e6d2f684`](https://github.com/pratikto/PhotoBooth/commit/e6d2f6840d4b5838e719f904bcc3b8443291193a) switches from N Windows jobs to one batch; [`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93) fixes omitted `EndDocPrinter` and duplicate `ClosePrinter`.
- **Independent automated evidence:** [targeted Actions 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707), at `41a51b5b`, **PASS 11 business/manifest + 4 mock transport/Windows spool tests**. This does not itself establish physical output. [Dither lab Actions 39135186017](https://github.com/pratikto/PhotoBooth/actions/runs/39135186017) **PASS**, while [Kiosk GUI Actions 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) at `f2f52e33` **FAIL** at the full unittest step. Do not infer the source or cause of the GUI failure from the owner paper success.
- **New canonical QA dossier:** [FEAT-001 / BUG-011 Acceptance](qa/FEAT-001-BUG-011-acceptance.md) includes scenario targets, test dates/SHAs, original bug mechanism, source map, residual risks, manual follow-up evidence and rollback boundaries. Cross-linked from the current bug tracker, feature status, execution board, technical architecture and handover.
- **Scope limit:** real QRIS FEAT-020, FEAT-007 paid-state recovery, ads/Drive sync and audio BUG-001/007 are unaffected; no Code.gs update, printer-code rework, rollout, release, merge or physical test was executed by this documentation task.

### BUG-011 — historical initial physical print-copy mismatch (superseded by latest owner PASS above)

- **Owner feedback:** checkout/demo pricing is correct, but the Windows thermal printer physically produced a different number of sheets from the selected copy count. Requested/printed counts have not yet been captured; do **not** mark resolved.
- **Confirmed source bug:** `ThermalPrinter._send_windows_raw` previously **called `ClosePrinter` twice instead of `EndDocPrinter` + `ClosePrinter`**. Fixed RAW job finalization order in [`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93) so Windows can finalize the document correctly and close the handle exactly once.
- **Multi-copy handling improvement:** [`4608fcc9`](https://github.com/pratikto/PhotoBooth/commit/4608fcc9ec96c8eabeb01ddbd64059830af2bf62) repeats the byte-identical ESC/POS image+cut stream `copies` times **inside one RAW transport payload**. [`e6d2f684`](https://github.com/pratikto/PhotoBooth/commit/e6d2f6840d4b5838e719f904bcc3b8443291193a) changes the worker to submit just that one batch and report completion as transport acceptance, not confirmed paper. No auto-retry on a partial/uncertain job; manual print remains operator-controlled.
- **Regression:** updated controller flow in [`0e91d9a2`](https://github.com/pratikto/PhotoBooth/commit/0e91d9a220bca4df67bd0adbb7b7490f9dce3430); new byte-level LAN/USB cut and invalid-copy cases in [`58c98f79`](https://github.com/pratikto/PhotoBooth/commit/58c98f79e13a5101a67438389e9a1b1d7fcdd430); Windows RAW fake spooler lifecycle check in [`4653719f`](https://github.com/pratikto/PhotoBooth/commit/4653719f5e1b01c22d1afd9cbfd5cfe475adedac). Expanded focused CI in [`dbeab0e7`](https://github.com/pratikto/PhotoBooth/commit/dbeab0e70cdb75e015f34066561b181967f7a16d).
- **Verification evidence:** [FEAT-001 CI run 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) **PASS** for pricing/manifest and mocked multi-copy/Windows RAW tests following the lifecycle fix. Initial expanded run failed on the *missing EndDoc* assertion, pinpointing the source defect; it was fixed, **not hidden by skipping the test**. Actual Windows POS80 printer paper count, physical cut and full Kiosk GUI regression still require operator evidence. No QRIS/provider, pricing constants, ad player or dither tuning changed.

### FEAT-001 — DEMO session fee plus individual printed copies (owner-approved scoped source change)

- **Owner authorization:** implement FEAT-001 on existing `feature/kivy-gui` as a narrow exception to the deferred QRIS/payment work queue. Base before changes: [`5842a09f`](https://github.com/pratikto/PhotoBooth/commit/5842a09f6a4c6c771ef7f5f0d1a330d0b1040b42). **Live QRIS provider FEAT-020 is NOT included.**
- `photobooth/catalog.py`: add `PRICE_PER_PRINT_COPY = 5000` alongside session base IDR 5,000; `workflow.py`: one planned 3-shot session per nonzero template, `print_copies` retained and `quote_order` computes correct mixed-template total.
- `photobooth/ui_kivy.py` and `app.py`: display copy counts and fee breakdown, preserve edit-cart flow, send the same completed PNG N times as a serialized batch using current printer configuration. On first failed/uncertain send, halt later sheets and require explicit operator retry; photo session is not recaptured or recomposed.
- `photobooth/transaction_store.py`: add `print_copies` per session and additive `demo_order_pricing` manifest metadata. This metadata describes a **simulated** order, not verified payment or a complete durable financial ledger (future FEAT-007).
- Updated `tests/test_workflow.py`, `tests/test_controller_flow.py`, `tests/test_kivy_gui.py`, and `tools/render_gui.py` to align prices, one-session semantics, print batching and fail-stop behavior. Source/tests were committed in separately reviewable stages; physical Windows 80mm paper acceptance remains outstanding.
- Source/test commits: [`aca7b621`](https://github.com/pratikto/PhotoBooth/commit/aca7b621e6d6259f2253e7afb623600dc0aa4552), [`b28af936`](https://github.com/pratikto/PhotoBooth/commit/b28af936b6201aca525cf46e6418add996e30b06), [`98b31641`](https://github.com/pratikto/PhotoBooth/commit/98b31641ad185542d6b38d39bc3ef4496f958285), [`343181bd`](https://github.com/pratikto/PhotoBooth/commit/343181bd11d7a1a0d89211c0d0e9b8bc736718d1), [`90657c51`](https://github.com/pratikto/PhotoBooth/commit/90657c5173d1271507197e2c9eac2342036c38c7), [`cc84f9ee`](https://github.com/pratikto/PhotoBooth/commit/cc84f9ee8be2c0f2555c8a57ab5435c2c51fcf73), [`9bd36137`](https://github.com/pratikto/PhotoBooth/commit/9bd3613742f80e31229a48fb5216ce60edc8314e), [`93344c52`](https://github.com/pratikto/PhotoBooth/commit/93344c523b8d5e79069ab9aaa46c1e67fb41a9a3), [`c65b399a`](https://github.com/pratikto/PhotoBooth/commit/c65b399af68f7e84c7cbbebf7ebff1882beb4a57), [`9dacc5ad`](https://github.com/pratikto/PhotoBooth/commit/9dacc5ad2465ccc224becd35fbcd5e8ba9068a8d), [`e36662c0`](https://github.com/pratikto/PhotoBooth/commit/e36662c0f6aa70ccfc6a6caba14e82d720e6771d).
- **FEAT-001 follow-up safeguards/tests:** `ui_kivy.py` locks the result-page next/finish action during a printer batch ([`2ec40578`](https://github.com/pratikto/PhotoBooth/commit/2ec40578ed2c98cca0d05a4302176d4fb408b940)); `test_controller_flow.py` makes navigation tests deterministic without real printer timing ([`d48b0685`](https://github.com/pratikto/PhotoBooth/commit/d48b06859059b41c6991fb76d700a32118c09796)); `test_kivy_gui.py` checks the busy/unlock behavior ([`9a574fef`](https://github.com/pratikto/PhotoBooth/commit/9a574fef80dca1f87086e313820c57ace04c1ff7)). Dedicated headless pure-domain Actions workflow added in [commit `35775128`](https://github.com/pratikto/PhotoBooth/commit/357751288092f0c590c0e845a6f46c9666b8834); its completed CI run result must be checked separately.
- **Targeted automated verification:** [FEAT-001 Pricing and Copy-Count Actions run 39131731784](https://github.com/pratikto/PhotoBooth/actions/runs/39131731784) at [commit `dfd6e5fb`](https://github.com/pratikto/PhotoBooth/commit/dfd6e5fbef3d0b41d61c4597b40e218f6af24ef1) ran **11 workflow/session/manifest tests, all PASS** with Python compile PASS. The earlier initial lightweight run failed because a separate QR decoder test needed OpenCV; narrowed headless CI is intentionally not full QR or Kivy coverage. Dither tuning CI remained passing. **Kiosk GUI full-suite and Windows actual paper output remain NOT VERIFIED / previously failing**; no real payment, camera or physical print was performed by this chat.

### QRIS future feature FEAT-020 and payment-related P3 reprioritization (docs only)
- Owner confirmed that **all transaction/payment/checkout/pricing/merchant-promo settlement implementations should move to LOW execution priority** because production QRIS has not yet been integrated. Added **FEAT-020** as the distinct future real QRIS provider/verified-settlement feature (also **P3 / deferred**) and rearranged the unified backlog to prioritize FEAT-008/009/003/012/010/004 before that phase.
- **Payment remains explicitly DEMO/non-payable**; no provider selected, real merchant charge accepted, terminal configured, signed callback integrated or production financial operation claimed. Payment-related existing requirements remain documented and must align with QRIS before any actual money flow.
- Previously recorded BUG-009 deferral to FEAT-004 remains intact; unresolved Google Drive photo-retention risk is not downgraded by this **separate** QRIS scheduling decision.
- Associated documentation commits: [docs/next_step.md `c13e8f88`](https://github.com/pratikto/PhotoBooth/commit/c13e8f8846bc1daa0133447b8406f8be09ef5e16); [docs/DECISIONS.md `39a1aee9`](https://github.com/pratikto/PhotoBooth/commit/39a1aee9c95122f3d42f011d3481d0f5b6671550); [docs/FEATURE_STATUS.md `785bc6b0`](https://github.com/pratikto/PhotoBooth/commit/785bc6b03b1600d476612f2ae4e303ff6a563eaf); [docs/DEVELOPMENT_HANDOVER.md `e40f0515`](https://github.com/pratikto/PhotoBooth/commit/e40f05152fa1d16779f106d0359c5e81b823fc42). **No app or Apps Script code, API credentials, merchant service, QRIS integration, tests, hardware config, merge or deployment were changed/performed.**

### Owner-scheduled FEAT-004 / BUG-009 combined Google Apps Script phase (docs only)
- Logged the owner decision to **defer BUG-009** (Google Drive 30-day photo retention still unverified) and coordinate later remediation with **FEAT-004** per-machine Google Drive video/image ad sync. This is an integration/deployment planning decision, not approval to implement, deploy or delete files.
- The current repository `apps_script/Code.gs` already contains retention setup/registration/cleanup; actual trigger and deployed Web App remain unverified. The future ad-sync API is still proposed. Keep customer photo folders separate from ad media and test the two workflows independently with authorized synthetic data.
- Related documentation-only commits: `docs/bug_tracker.md` [`bb2326de`](https://github.com/pratikto/PhotoBooth/commit/bb2326dee165e1cf570485d41d9d0768630dd902); `docs/next_step.md` [`7c4d73a2`](https://github.com/pratikto/PhotoBooth/commit/7c4d73a257c584e3ef7f1f0d225d24231dc14078); `docs/DECISIONS.md` [`f1e72bf6`](https://github.com/pratikto/PhotoBooth/commit/f1e72bf6fc99c76cc1e7baf29a5a77a530d139d6). No Python/Apps Script source files changed; no new automated or device tests were run for this entry.

### Owner-approved GUI merge and default Floyd photo profile
- Fast-forwarded `feature/kivy-gui` to the existing tested `feature/dither-tuning` head `f3d836d`, retaining the 3-way standalone lab, its tests and documentation. This does not merge to `main`.
- For ordinary **photo composition** printing with configured Floyd–Steinberg and native width 384/576 dots, apply the user-selected lab profile: B 0.652, C 2.104, gamma 2.352, sharpness 2.073, threshold 128. Other dithering modes, explicitly requested comparison jobs, and QRIS slip generation are not modified.
- Rollback: launch with `PHOTOBOOTH_PHOTO_TUNING=legacy` to use the previous Floyd preprocessing without reverting printer settings. Physical thermal print acceptance still pending.



### BUG-010 — Dither GUI scroll accessibility
- Added per-column vertical parameter scrolling and mouse-wheel routing.
- Reduced on-screen preview height; Print Test and Save PNG remain outside scroll container.
- No source changes to dithering or production printing; Windows GUI acceptance pending.



### Approved staged 3-way tuning lab continuation
- Stage 1 `9f73f6e`: independent comparison profiles and schema validation; initial CI failure from literal newline in JSON, fixed in stage 2.
- Stage 2 `15f87a7`: `tools/dither_compare_gui.py` with original plus three live dithering columns, independently tunable sliders, optional sync controls, zoomed dot crop, runtime/coverage information, save/load all configurations and native 1-bit exports. Dedicated CI passed.
- Stage 3 `03e7ddf`: labeled, confirmed physical Print Test and Print All via `photobooth/dither_print.py`, submitting the preview's exact one-bit raster without re-dithering, halting uncertain batches. Dedicated CI passed; **physical print and Windows GUI are not yet verified**. The primary current GUI is `python tools/dither_compare_gui.py`; original single-lane GUI remains as a legacy lab utility.
- Stage 4: updated [operator lab guide](dither-tuning-lab.md), bug/feature status and real-device acceptance checklist; no production kiosk code touched.


### Owner-approved standalone thermal dithering lab (FEAT-011 / BUG-004)
- **New experimental branch:** [`feature/dither-tuning`](https://github.com/pratikto/PhotoBooth/tree/feature/dither-tuning), forked from GUI baseline [`5e0a898`](https://github.com/pratikto/PhotoBooth/commit/5e0a8980968430b85f04ebac1b6c1574c2191a69); source commit [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229).
- Added `photobooth/dither_lab.py` with calibrated 1-bit thermal previews, adjustable brightness/contrast/gamma/sharpness, mode/width/threshold controls and validated atomic JSON profiles. Reuses existing `photobooth.printer.dither_image`; defaults preserve current native printer raster behavior.
- Added standalone `tools/dither_tuning_gui.py` (Tkinter GUI with side-by-side before/after, 3× detail crop, debounce/background render, photo open, JSON preset load/save and 1-bit export); synthetic example only, no customer data sent or real printer submitted.
- Added targeted `tests/test_dither_lab.py`, separate `.github/workflows/dither-lab.yml`, and [operator usage guide](dither-tuning-lab.md). [CI 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) **PASS** for compile and targeted tests; Windows live Tk UI and real paper/quality **NOT VERIFIED**.
- **Scope boundary:** existing `photobooth/printer.py` and Kivy app are **unchanged** in this source commit; no main-branch merge, app integration or production release authorized. BUG-004 is not fixed merely by creating a tuning lab.



### Approved application audio remediation (BUG-001 / BUG-007; Windows verification pending)
- **Base/rollback commit:** [`06dd977c`](https://github.com/pratikto/PhotoBooth/commit/06dd977c06657c9b56e1de0ad18042b65515bd64); implementation and associated docs/tests are in the current audio commit on `feature/kivy-gui`. No branch creation or merge.
- `photobooth/audio.py`: reacquire a native music channel at saved full gain when the ad fade finishes; add an operator-forced music audition that cannot be skipped by a stale `state=play` report and obeys normal mute/pause/ad gates.
- `photobooth/ui_kivy.py`: each Sound Settings Uji control plays its intended sample without a preceding generic button click; refresh feedback displays a true newline and distinguishes playback request from confirmed audible sound.
- `tests/test_audio.py` and `tests/test_kivy_gui.py`: add regression coverage for forced music retry, fade replay and exclusive per-button sample routing.
- Reconcile latest owner-reported device passes for BUG-002/003/005/006 separately from BUG-001/007 audio acceptance in `bug_tracker.md`, `FEATURE_STATUS.md`, `test_checklist.md` and `DEVELOPMENT_HANDOVER.md`.
- **Tests (after code commit [`b69d3837`](https://github.com/pratikto/PhotoBooth/commit/b69d3837de6220d27a477a10a807fdbdd799cb0b)):** [GitHub Actions run 39104614520](https://github.com/pratikto/PhotoBooth/actions/runs/39104614520) **FAIL overall**; Python compile **PASS**; full `unittest discover` **FAIL** (exit 1; test name not captured); 87 GUI renders **PASS**, no reported render errors; visual summary **PASS**. Baseline also failed discovery on [run 39101639665](https://github.com/pratikto/PhotoBooth/actions/runs/39101639665). Audio-only tests not separately executed, and **no sound physically verified yet**. This status was recorded in a linked documentation follow-up commit.

### Owner Windows unit-test confirmation (BUG-001 / BUG-007; docs only)
- Owner shared direct Windows PowerShell results for `python -m unittest tests.test_audio -v`: **14 run, 13 PASS, 1 SKIP, 0 FAIL** (2.539 s) on Python 3.12.10 / Kivy 2.3.1. Both music-fade and explicit music-audition regressions passed; actual native audio test remains skipped and music audibility in the running kiosk still needs owner confirmation. The checked-out commit SHA was not included in the terminal output. This entry records observed test evidence without application-code changes.

### Mandatory development documentation workflow (docs only)
- Added [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md): copy/paste full and quick prompts for new development conversations, with branch/SHA inspection, scope approval, severity/dependency review, code/test boundaries, GitHub documentation mapping and final traceability report. Commit [`de0886b`](https://github.com/pratikto/PhotoBooth/commit/de0886b9fdf491d7e21db403c234656044f9b67b).
- Updated [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) to require the relevant feature/bug/status/test/handover/changelog documents to be kept aligned with **approved** code changes, in the same or a clearly linked companion commit; false claims of physical acceptance remain forbidden. Commit [`5800c56`](https://github.com/pratikto/PhotoBooth/commit/5800c561006966b90dc316f404ec1ddbd9743328).
- Linked the canonical prompt in [docs/README.md](README.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and the repository-root [README.md](../README.md). The handover now points to one maintained prompt rather than duplicating its full operating rules.
- **Scope:** Markdown documentation only; no Kivy/Python application code, media, hardware configuration or runtime behavior changed. No automated or physical booth test executed for this documentation change.


### Documentation governance and folder housekeeping (docs only)
- Introduced the development protocol with approval gates, dynamic bug/feature prioritization, regression evidence levels and rollback requirements.
- Added independent bug register, feature backlog and verification checklist without representing reports as fixes.
- Renamed the technical continuation document to `docs/DEVELOPMENT_HANDOVER.md`; retained `docs/NEXT_STEPS.md` as a legacy-link pointer, not a duplicate backlog.
- Moved the five planning/operations Markdown files from root to `docs/`: `DEVELOPMENT_PROTOCOL.md`, `bug_tracker.md`, `next_step.md`, `test_checklist.md` and `CHANGELOG.md`. Root `README.md` remains at root.
- Added [documentation index](README.md), updated root README links and aligned major internal documentation references.

### Product/business specification intake (documentation only)
- Recorded FEAT-001 base IDR 5,000/session + IDR 5,000/physical-copy target, independent of three-photo capture count. **Current source tariff is unchanged.**
- Documented demo merchant receipt scan, demo ordering-to-photo promotion, mirror-only camera preview, per-machine local-first ad delivery, theme ideas and reliability/scale candidates FEAT-002–018.
- Added BIZ-001/FEAT-019: hardware sales, mandatory assigned **Free/Business/Enterprise** tier including IDR 0 Free, Free fully commercial operation, Meong-controlled Free advertising and Meong-reserved ad slots in Business/Enterprise; reserved percentages/prices remain undecided.
- Parked additional monetization candidates for later owner evaluation without scheduling implementation.

### Latest documentation reconciliation — four successive stages (docs only)
1. **Decisions:** Reconciled owner decisions, existing code versus desired behavior and open contractual/commercial terms in `DECISIONS.md`; distinguished operator photo income from Meong subscription/advertising and merchant subsidy.
2. **Architecture/status/guide:** Aligned `ARCHITECTURE.md`, `FEATURE_STATUS.md`, `advertising-and-qris.md`, and root `README.md` with the source-level printer integration (including shared Windows QR-slip config), existing demo payment, current IDR 5,000/session implementation and live-device failures. Kept historical QA evidence labelled as historical.
3. **Bug/test evidence:** Kept stable BUG-001 through BUG-006, introduced **BUG-007** specifically for unresponsive Music/Button Settings tests and separated audio-output failure. `test_checklist.md` now distinguishes reported physical passes/failures, historical mocked tests, and tests still unverified.
4. **Unified roadmap/handover:** Created one provisional feature execution board covering FEAT-001–019 and deferred POS stages; marked all feature implementations unapproved, fixed model-dependent merchant subsidy recipient, and updated `DEVELOPMENT_HANDOVER.md` so latest blockers and approval gates precede older technical notes.

**No Python, application resources, pricing logic, runtime audio/video/printing, payment gateway or subscription enforcement were changed in these documentation steps. No new automated or physical kiosk test run is claimed.**

## Historical application changes

For changes made before the documentation effort, inspect Git commits and the dated QA evidence. Existing user-confirmed working thermal photo paper output **does not** prove acceptable image quality or QR-slip paper output. Historic sound/video mocked test passes **do not** resolve present Windows audio/video reports. Current defects remain in [bug_tracker.md](bug_tracker.md).


## [Unreleased — FEAT-022 portrait GUI v2 standalone foundation] — 2026-10-21

- Owner approved rebuilding the customer-facing Kivy GUI and audio controller from scratch on **feature/portrait-kiosk-gui**, preserving the working v1 backend and immutable v1.0.0. Initial master base SHA 27f3801b.
- New independent Python visit navigation, audio lifecycle with bundled WAV files, Pixel Arcade Space design components, opt-in launcher, actual idle playlist widget, inline invitation **visual preview only**, mandatory tutorial per visit, and a picker of the existing 12 approved 3-photo + photo-QR thermal strips with copy counts and DEMO quote.
- A Meong Fly entry notice is displayed, **not an integrated gameplay/scanner/discount**. QRIS/capture/printing/Drive checkout are not wired into v2 yet; the default main.py is unchanged.
- Added isolated pure navigation/audio unit tests, optional real-widget Kivy smoke test and a new branch-only CI workflow. Synthetic, physical and Windows results remain to be recorded; no master merge.
- Design/rollback and acceptance plan: portrait-kiosk-v2.md. This entry tracks source changes, not release or physical certification.


## [Unreleased — FEAT-022 portrait v2 audio hardening on new branch] — 2026-10-21

- Created `feature/portrait-kiosk-v2-next` from existing opt-in `feature/portrait-kiosk-gui` scaffold. `master`, v1.0.0, `main.py` and legacy audio are unchanged.
- `ab551ba3`: enable the existing portrait CI workflow for the new working branch.
- `2b743da0`: favor SDL2 on desktop for bundled PCM WAV, preserve explicit Kivy audio-provider overrides, reject/unload invalid native handles, and avoid reporting successful playback if the native handle remains stopped.
- `caad0e0d`: add provider-fallback/duration/failed-play unit cases to the isolated v2 audio suite.
- Design, test limitations, and Windows-speaker acceptance remain in [portrait-kiosk-v2.md](portrait-kiosk-v2.md). These commits do **not** certify audio audibility, restore audio in v1, implement payments or connect actual photography services. New-branch CI is not yet verified at time of this entry.


## [Unreleased — FEAT-022 complete mockup + branch documentation reconciliation] — 2026-10-21

**Approval and scope:** owner requested **comprehensive GitHub documentation for feature/portrait-kiosk-v2-next, including the last approved mockup images**. This work is **DOCS AND IMAGE-ASSET ONLY** after the previously committed GUI v2 / audio prototype. It does **not** modify production Python, legacy main.py, payments, camera, printer, Drive, QRIS credentials, receipt logic, release tag or master.

### Exact design assets now stored in repository

- [6e7f29a7](https://github.com/pratikto/PhotoBooth/commit/6e7f29a769b2ca19d09efa99b3bef21fb7b8bc86) — initially archived the full-resolution main UI and earlier eight-screen game boards as high-quality WebP under docs/assets/portrait-v2/.
- [7b927526](https://github.com/pratikto/PhotoBooth/commit/7b927526d9edc157e73aa82bc4525486da02048b) — **archived the *latest revised nine-screen Meong Fly board*** with the dedicated **MASUK MINI GAME** intro. This is now the **primary approved game visual**; the eight-screen predecessor remains traceable archival art.
- [Image asset provenance/checksums](assets/portrait-v2/README.md) includes original PNG SHA-256, exported WebP SHA-256, Git blob SHAs and exact visual correction precedence. No image was redrawn during this documentation stage.

### Canonical documentation updated

- [portrait-kiosk-v2.md](portrait-kiosk-v2.md) — comprehensive owner-approved flow, both actual embedded latest artboards, current v2 implementation matrix, audio/QRIS/game/printing boundaries, staged delivery and actual CI evidence.
- **New** [portrait-kiosk-v2-visual-spec.md](portrait-kiosk-v2-visual-spec.md) — annotated boards, full direct-photo / Meong Fly paths, >9 screen/overlay inventory, UI design rules, accessible touch/portrait behaviors, 80×240 mm 3-photo/1-QR print preview requirements and image-versus-source corrections.
- **New** [portrait-kiosk-v2-technical-design.md](portrait-kiosk-v2-technical-design.md) — present package/module map vs **proposed** typed service adapters; once-per-visit tutorial/receipt ledger/discount lifecycle; payment/safety invariants; audio page ownership, Windows acceptance, phased dependencies and rollback.
- [DECISIONS.md](DECISIONS.md) — DEC-022 greenfield GUI + approved artboards, with DEC-003 tutorial-once addendum preserved. Both CTA paths share the idle/face invitation; dedicated game intro before receipt, one receipt one chance/no replay, Win/Lose → tutorial iff unseen → template selection, not immediate payment, Rp2.500 eligibility requires future verified checkout.
- [ARCHITECTURE.md](ARCHITECTURE.md) — isolated current v2 modules and backend adapter boundaries; no missing integrated game/QRIS/camera/print/Drive features claimed.
- [FEATURE_STATUS.md](FEATURE_STATUS.md) — current v2 four-route prototype, manual invite preview, unavailable game placeholder, no provider/camera/print integration, actual CI status.
- [next_step.md](next_step.md) — owner-selected stage, dynamic delivery re-ranking and conflict/dependency review (including duplicate FEAT-021 IDs and FEAT-002/Meong Fly promo overlap).
- [test_checklist.md](test_checklist.md) — exact CI evidence and detailed on-device / feature integration / release acceptance matrices, with runnable Windows commands.
- [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) — new up-front current handover, next safe action, evidence and explicit no-merge rule.
- [docs/README.md](README.md) — entry point and links to all above documents and the **latest revised game** artboard.

### Evidence and non-claims

- [FEAT-022 source/mockup CI 39548798578](https://github.com/pratikto/PhotoBooth/actions/runs/39548798578), SHA **6e7f29a7** — Python compile PASS, **21/21 pure navigation/audio tests PASS**, real Kivy widget smoke PASS under Linux/Xvfb, and 12 synthetic screenshots at 800×1280 and 452×900; **two jobs SUCCESS**. A deliberately failing mock audio provider is part of a **passing** fallback test.
- Later assets and Markdown commits change no application source. Workflow results on later documentation SHAs, when present, must be checked separately; **there was no new Windows/hardware testing during these documentation commits**.
- **Still pending/not implemented:** real Windows audible background music and ad audio, actual 10.1-inch touch acceptance, genuine face invitation, receipt scanner/POS verification, playable game inside the kiosk, real Rp2.500 voucher redemption, server-authoritative QRIS, actual photo capture/retake, physical paper and digital Drive delivery in v2. No security/financial/customer deployment approved.
- **Rollback:** switch back to stable master/v1.0.0. Do not merge to master without a new explicit owner decision; do not delete other branches or journals. BUG-001/007 and BUG-009 remain operationally open.

## [Unreleased — FEAT-022 P2.5 interactive portrait GUI polish] — 2026-10-21

**Branch only:** `feature/portrait-kiosk-v2-next`; **NO master merge**, v1 main.py / camera / order / audio / printer / Drive core unaffected. This entry tracks actual opt-in new Kivy UI source changes, not a released or physically certified system.

- [80f085e0](https://github.com/pratikto/PhotoBooth/commit/80f085e0fe2d33faefbe8b7d4785a34a61976cc0) — new lightweight Kivy-vector four-step tutorial illustrations, decorative and non-scannable.
- [f935ef34](https://github.com/pratikto/PhotoBooth/commit/f935ef34eea3378c31ff65c65936208723840365) — brighter Pixel Arcade Space stars and accented PixelCards/native Buttons (pressed/disabled color states).
- [d4a9acaa](https://github.com/pratikto/PhotoBooth/commit/d4a9acaa8315d53c2ade201ec94e75b2e8b08e7d) — ad-dominant idle and face invite styling, visible customer photo/game entry on the same ad surface, extra working Cara Pakai button into mandatory tutorial.
- [a74377d0](https://github.com/pratikto/PhotoBooth/commit/a74377d0e80a145f82dd8cd8808e53a07349d097) — four illustrated, scrollable once-per-visit tutorial cards; retains audio diagnostic and visit state.
- [39edb3ab](https://github.com/pratikto/PhotoBooth/commit/39edb3ab4f8a9b7f126258be9ed19b7512cbf43a) — three-strip gallery with genuine previous/current/next approved 1:3 thermal preview textures and DEMO printed-copy totals, without altering master print outputs.
- [38d86d0d](https://github.com/pratikto/PhotoBooth/commit/38d86d0dcb8b2c157b3bf077c2cdecff569554ba), [0e496280](https://github.com/pratikto/PhotoBooth/commit/0e496280e57efe9e9521c7644ccb77fa204df841) — dedicated safe Meong Fly intro/rules with potential Rp2.500 reward but **disabled** receipt scanner, compact-height responsive mascot.
- [e33cbe98](https://github.com/pratikto/PhotoBooth/commit/e33cbe9846fbc2d314543f5652c62c25b86bf8cd) — real gallery horizontal swipe handler, rejects short/vertical drags.
- [8647b5e7](https://github.com/pratikto/PhotoBooth/commit/8647b5e7e70ca73a891222ed1b2e1052f9d63dd8), [c4e4703a](https://github.com/pratikto/PhotoBooth/commit/c4e4703ac076d5eed2cd1b88c7ccd19fa4916cd3) — regression tests updated for all four icons, same-ad dual entry, safe game intro, adjacent real-strip cache and swipe threshold.

**Verified code-level QA:** [GitHub Actions 39555036023](https://github.com/pratikto/PhotoBooth/actions/runs/39555036023) at code/test SHA **c4e4703a**: **21/21** pure tests PASS; Kivy widget smoke PASS; 12 synthetic portrait screenshots PASS at 800×1280 and 452×900; two jobs SUCCESS. An earlier CI run between gallery changes and updated assertions failed due *stale test expectation* of 1 texture; after updating test to cover 3 previews the current run succeeded. Screenshot artifacts visually inspected, including legible compact-height game introduction. No new device/hardware tests were performed.

**Explicitly NOT delivered:** Real face detection, playable Meong Fly/POS struk/one-attempt backend and redeemable discount, provider QRIS, camera capture, thermal paper print and Drive delivery inside v2. Remaining P2.5 design pixel-font/animation polish plus physical Windows 10.1-inch audio/video and touch/swipe acceptance are still open; owner approval is required before master promotion.
