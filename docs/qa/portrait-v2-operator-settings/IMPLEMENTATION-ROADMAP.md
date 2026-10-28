# GUI v2 Operator Settings — future Codex implementation roadmap
**Approved design / future implementation ONLY — 29 October 2026.**
**Authoritative source:** [complete contract](README.md) · [decision register](DECISION-REGISTER.md) · [acceptance matrix](ACCEPTANCE-MATRIX.md) · [Codex handover](CODEX-HANDOVER.md).

## ABSOLUTE PRIORITY OVERRIDE — AR-00 to AR-13 before OPS

1. **The owner's highest development priority remains autonomous QRIS/photobooth recovery, AR-00 → AR-13, in its original dependency order**. Do not rename, truncate, replace, interleave or restart these AR stages to get to the Settings screen. Continue the latest active AR micro-increment by consulting the [real checkpoint](../portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md), [roadmap](../portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md), [handover](../../DEVELOPMENT_HANDOVER.md) and current Git HEAD.
2. These OPS stages are a **queued follow-up design**; writing this roadmap does **not** start code work, change AR acceptance, mark anything implemented, approve a release, turn on real payment or authorize overriding the currently deliberate Midtrans Sandbox printer/Drive-off policy.
3. When AR-13 is reached, document what is complete, VERIFIED or externally BLOCKED with true test evidence. External merchant/Android/paper pilot gates may remain NOT_RUN even though source work progressed; they must not be disguised as completed. Do not use an OPS implementation as a workaround for an unclosed AR gate. Only sequence OPS work when the owner explicitly authorizes its implementation or reprioritizes AR scope.
4. Use **only** existing `feature/portrait-kiosk-v2-next`, no new branches or `master` merge. Every safe micro-increment: inspect HEAD + dirty work → write targeted tests → implement → focused test → docs update → **commit + push immediately** → verify origin HEAD → precise handover. Frequent checked pushes survive the five-hour ChatGPT/Codex limit; do not leave a large unpushed body of work. Stop only dependent steps if hardware/provider evidence is unavailable; do other safe independent tests.

## Planned stage ledger — all NOT_STARTED / NOT_RUN at publication

| Stage | Owner-visible deliverable | Core dependency | Required exit evidence |
| --- | --- | --- | --- |
| **OPS-00** | Pin post-AR source baseline, audit old Device Health, scanners, sound, game, printer, real state contracts | AR-00–AR-13 sequence respected; fresh authorization | Existing behavior and gaps documented; no source change |
| **OPS-01** | SAFE_IDLE/Advertising-only secret entry contract and exception preservation | OPS-00 + AR-09 fencing/lease read | Tests reject every non-ADVERT and unsafe state |
| **OPS-02** | Per-booth offline static operator QR provisioning, hash, rotate/revoke | OPS-01 | Valid same-booth QR accepts, cross-booth/wrong type/revoked fails |
| **OPS-03** | Reused-camera mirrored live operator scanner and authenticated lifecycle | OPS-01/02 | One camera owner; timeout/back/minimize/stale callbacks safe |
| **OPS-04** | Three-tab Settings shell + Device Health reuse | OPS-03 | Health report remains read-only; no BUG-018 input hang |
| **OPS-05** | Persistent Audio Settings buses/master/mute/test | OPS-04 | Settings persist restart; music/game/video lifecycle preserved |
| **OPS-06** | Static DEMO ticket namespace + scenario fixtures | OPS-04 | Static payload stable; type/mode/negative cases correctly checked |
| **OPS-07** | Merchant Promo DEMO mock verdicts, policy and ledger | OPS-06 | Eligible/ineligible/invalid/duplicate + no stacking + no real QRIS pricing |
| **OPS-08** | Meong Fly static DEMO claim per test visit; preserve original engine/ledger | OPS-06 | One attempt per visit despite restart; new visit allowed; original game untouched |
| **OPS-09** | Demo ticket QR preview, thermal print, durable attempt, optional history | OPS-06–08 | Printed QR decodes, no uncertain replay, Sandbox remains isolated |
| **OPS-10** | Cross-module regression, native screenshots, Windows/Ubuntu/tablet/device acceptance, future migration notes | All previous applicable stages | Pinned source + focused/full tests + honest NOT_RUN for external gates |

Naming: **OPS** = Operator Settings, separate from AR numbering and old GUI P0–P5 stage names. OPS dependencies are suggestions for safe ordering, not permission to start early.

## OPS-00 — baseline and explicit source map

**OPS-00.a**: Read `AGENTS.md`, `docs/README.md`, `docs/DEVELOPMENT_HANDOVER.md`, `docs/DECISIONS.md`, `docs/next_step.md`, `docs/FEATURE_STATUS.md`, `docs/portrait-kiosk-v2.md`, the full AR contract and checkpoint, and all five OPS documents. Compare actual branch HEAD to remote, protect dirty user work, record OS/Python/Kivy/provider versions. Exclude protected `old`.

**OPS-00.b**: Inspect exact existing source:

- Secret gesture / F12, operator admission and legacy direct Device Health popup: `photobooth/kiosk_v2/operator_health.py`, `app.py`, `flow.py`. Current direct recovery exception should be preserved in a **separate AR-09 path**.
- Current AR-09 occupancy fencing, native operator PIN, booth-release ACK, customer return and pending service: current `sandbox_views.py`, `sandbox_checkout.py`, `qris_session.py`, backend modules. Trust the latest AR implementation instead of dated summaries.
- Existing asynchronous camera and face invite: `devices.py`, `sensors.py` and photo/QR scanner adapters. Reuse one frame mailbox and handle.
- Health worker/reused v1 controller: `operator_health.py`, `health_service.py`, `health_report.py`, `photobooth/ui_health.py` and Device Health QA. Record already-tested BUG-018 constraints.
- Audio: `audio.py`, `mixer.py`, `game_music.py`, `app.py` and ad-player lifecycle. Identify sound names and native backends rather than assuming example slider values are source defaults.
- Meong Fly: `demo_game.py`, `game_views.py`, original stage/renderer/flow and `GAME_RECEIPT` manual claim. Existing real `DEMO-` one-use ledger is preserved.
- QR/print: `photobooth/qr_code.py`, `photobooth/qris_print.py`, existing photo/thermal printer configuration and optional paper paths. Identify correct DEMO-only preview/print adapter; never couple demo tickets to a Midtrans payment attempt.
- Existing POS promo design (FEAT-002A/B), local mock checkout and server quote trust boundaries. Do not infer that a real merchant scanner is already implemented.

**OPS-00.c**: Write a one-page as-is vs target inventory: state values, auth scope, QR prefixes, background workers, table ownership, flags, device differences, active tests and unresolved policy choices. Do not write runtime code before OPS-00 is verified.

## OPS-01 — only Advertising + SAFE_IDLE

**OPS-01.a**: Model a pure operator-entry admission predicate that reads both current `navigation.page == ADVERT` and **authoritative safe live service ownership**. The screen alone never grants admission. Reevaluate on authenticated transition, not merely on long-press.

**OPS-01.b**: Add table-driven deny tests covering Face Invitation, Tutorial, Templates, Game Preview, Game Receipt, Game Play, Game Result, Mock, Sandbox pending/paid/unknown/RECOVERY, Photo Confirm, Capture, Review, Result, minimized/closing, busy photo worker, uncertain live print, ambiguous active-session claim, stale ownership fence, and new-vs-old-visit race. Test detached background Drive uploads/reconciliations do not block if safely isolated.

**OPS-01.c**: Route the existing F12/touch-hold to **Operator QR Login** in normal Advertising only. Do not remove existing AR-09 emergency/exception path; preserve it behind its own PIN/metadata permission and no tabs. Never reset financial ledgers to force SAFE_IDLE.

**Pass gate:** no customer state interrupted, no private recovery content exposed, no Settings in RECOVERY, no regression in AR-09 operator rescue/release or existing Device Health backends.

## OPS-02 — secure static per-booth operator credential

**OPS-02.a**: Define QR type/version/booth binding, random high-entropy token, independent hash/verifier, offline local config and provisioning action; include trust boundary and threat model. No static credential checked into source or documentation. No assumption that six-digit PIN, booth ID, recovery ticket or QRIS can authenticate.

**OPS-02.b**: Build secure local provision/rotate/revoke flow, with atomic write and rollback handling; do not print on customer paper or upload to Drive global/local media. Manual secure operator handoff outside kiosk. All secrets redacted from diagnostics/CI outputs/screenshots.

**OPS-02.c**: Focused tests: same-booth accept, unknown booth reject, wrong namespace reject, malformed QR, old rotated secret reject, invalid local config fail closed, restart persistence, offline use, concurrent provisioning guard, rate limiting. Recovery PIN unaffected.

**Pass gate:** no raw operator secret in repository, telemetry or public UI; credential is reusable only until rotation and never overrides SAFE_IDLE.

## OPS-03 — scanner / authentication UI

**OPS-03.a**: UI states `SCANNER_OPEN`, `DECODING`, `VERIFYING`, `AUTHENTICATED`, `ERROR`, `TIMED_OUT`, `CANCELLED`. Use reused existing `AsyncCamera` read-only frames; mirrored **display** but original **QR decode**. One bounded scanner worker/scheduler (~5–10 fps to be tuned for hardware). No second device acquisition.

**OPS-03.b**: Pause ad/video audio and face invitation while scanning, show clear QR scan box/instructions and manual Cancel, timebox scanning (suggest e.g. 30–60 s for UX; owner has not fixed a number). Wrong/wrong-type code is neutral, offers retry, never echoes token. Valid token rechecks source page, SAFE_IDLE, identity, revision and session uniqueness before menu open.

**OPS-03.c**: Close/Back/minimize/suspend/timeout/restart must revoke auth, cancel late worker callbacks and restore Advertising audio + invitation state without a new charge/shutter/print. Test iOS/Android device permissions separately later; no camera breakage.

**Pass gate:** one live camera handle, no locked camera on exit, stale QR does not grant later access, lost-camera OS maintenance fallback remains possible.

## OPS-04 — Settings shell and Device Health reuse

**OPS-04.a**: Exactly three tabs, labels **Device Health**, **Audio Settings**, **Emulate Ticket**. Persistent navigation within current authenticated operator session. Footer Booth ID, version/build, mode and last health time, avoiding identifying network/device secrets. Portrait 800×1280 and 452×900.

**OPS-04.b**: Mount the original health panel/controller in the Device Health tab without changing how read-only checks work; preserve disabled device selection and report export. Guard refresh, rapid input, minimize, stale results and dialog close. Add proposed *Copy Diagnostic Report* through same allowlist as saved JSON, but clipboard must not expose secrets.

**OPS-04.c**: Three-minute inactivity logout, Close/logout, privacy-minimize, return to actual Advertising. Test while background detached upload continues; ensure report save cannot preempt photo or recovery.

**Pass gate:** no input hang after repeated button taps; no new active device switch; exact Settings-only QR auth required for ordinary entrance.

## OPS-05 — Audio Settings

**OPS-05.a**: Add compatible per-booth persisted configuration version and mapping `master`, `music`, `button_sfx`, `other_sfx`, `mute` with bounded percentages. Initial GUI slider defaults are illustrative: inspect actual audio code and preserve audible balanced defaults. Atomic write/restart/corrupt-file fallback, no production key sharing.

**OPS-05.b**: Integrate into existing `PortraitAudio` and advertising player, preserving music/video/game owner isolation, game music stop/resume, Windows SDL idle-channel repair and sound preloading. Use a single gain owner; if video-ad audio cannot be managed safely, record an explicit supported limitation rather than forcibly changing its channel. No duplicated cue on slider/test action.

**OPS-05.c**: UI numerical labels, Master/Music/Button/Other/Mute/Test. Test changing each bus separately, mute restore, missing file/provider, rapid slider, restart, ad video transition, game, snapshot photo countdown and close/suspend.

**Pass gate:** per-booth saved volume and one sound owner; no crashes, phantom music/video or unintended audible SFX.

## OPS-06 — Static test ticket fixture contracts

**OPS-06.a**: Define explicitly versioned prefixes/role types `MEONG-DEMO-PROMO-V1` and `MEONG-DEMO-FLY-V1` (proposals; validate current project conventions), test-mode authority, deterministic static payload rules and distinct negative fixtures. Production server always denies DEMO namespace; Sandbox provider status is never altered.

**OPS-06.b**: Implement fixture resolver by (category, preset, booth config) with **identical QR payload on repeated Preview/Print**. No per-print transaction ID inside QR. Provide QR module-level decode tests, unmirrored output, image/color/thermal readability, and safe mocked receipt scanner adapter. A private operator QR, recovery token, payment QRIS, photo download QR or other category cannot be redeemed.

**OPS-06.c**: Add Negative Preset validation that does not accidentally pass through a permissive fallback path; QR may contain invalid sample payload, but report fail reason. For Already Used, reuse previously accepted valid payload, not new pre-invalidated QR.

**Pass gate:** QR namespace separation, reproducible static fixture, no production merchant effect.

## OPS-07 — Merchant Promo DEMO

**OPS-07.a**: Implement Mock/DEMO-only entitlement evaluator for Eligible (e.g. illustrative Rp50,000 purchase waiving one Rp5,000 base/design fee), Not Eligible (below threshold), Invalid (bad role/proof); do not use unverified bank QR or let a GUI-set amount authorize merchant Sandbox payment.

**OPS-07.b**: Bind promo consumption atomically to **test visit**; one promotional effect per visit, no double waiver with repeated scans or restart, and ensure the initial owner-recommended **no Merchant Promo + Meong Fly stacking** policy. Multiple selected designs/copies preserve quote rules and print fees.

**OPS-07.c**: Log safe verdict events, test duplicate/race/cross-booth, malformed payload, expired test visit, discount cap and no negative subtotal. Keep original trusted QRIS merchant validation as separately approved future scope.

**Pass gate:** no price changes in Midtrans Sandbox/production and no reward stacking/duplication in local mock.

## OPS-08 — Meong Fly DEMO

**OPS-08.a**: Preserve original game's one-entry/one-result flow, renderer, assets, physics, music, rainbow/camera-cat artwork, previous tutorial/discount and result-to-template behavior. Do not recreate Meong Fly.

**OPS-08.b**: Map **static reusable fixture** to an atomic per-test-visit admission (reusing current durable ledger), instead of turning an existing globally one-use `DEMO-` code into a universally reusable transaction ID. Within visit A, first scan opens game, second scan—even after app restart—rejects. In a genuinely new visit B, same static QR can open **one** game attempt. If visit A survives pending/recovery, it is not a new visit and does not regain an attempt.

**OPS-08.c**: Test Valid Entry, actual Already Used result, Invalid Entry, two simultaneous scans, exit/lose/win, cancel, restart after claim, resume, pending game DB error, no "MAIN LAGI" and existing Rp2,500 MOCK-only win entitlement. Keep backend trusted rewards separate.

**Pass gate:** no duplicate attempt and no regression of original Meong Fly game state, time/scoring or transition.

## OPS-09 — print / preview / history

**OPS-09.a**: Render a readable static QR preview for each preset, with clear **DEMO — NOT FOR PAYMENT** graphics. Test same QR payload across repeated preview, restart and prints; print output QR unmirrored and independently decodable.

**OPS-09.b**: Reuse 80-mm thermal, LAN/Wi-Fi/USB configuration and worker lifecycle; operator explicitly requests Print; serialize/bound taps, report Preview only when unavailable, and record durable print attempt before send. Distinguish UNCERTAIN from SENT from physical observed paper. **Do not auto-retry after uncertain delivery** or silently alter a customer strip/QRIS payment slip.

**OPS-09.c**: Display bounded history: category/preset, event time, print attempt/outcome, scan verdict, game/promo consumed per visit and reason code; do not retain raw operator QR, recovery token, payment credentials or private customer data. Cleanup only DEMO history, never financial/image state.

**OPS-09.d**: Never enable physically printing from the dedicated Midtrans Sandbox launcher under its printer OFF policy. A separately approved DEMO-local print mode must be isolated from provider tests.

**Pass gate:** no unauthorized physical output, no duplicate print on restart, readable 80-mm paper on separately approved device test, honest status labels.

## OPS-10 — final validation and acceptance

**OPS-10.a**: Run all [acceptance cases](ACCEPTANCE-MATRIX.md), every relevant inherited AR/Device Health/Meong Fly/QRIS/photo regression, independent decode of pixel/thermal QR, static payload hash comparison, lifecycle/fault/restart tests. Final full applicable regression only after final runtime change.

**OPS-10.b**: Capture native 800×1280 and 452×900 screen samples: Advertising secret entry, operator scanner, wrong QR, three Settings tabs, four/five audio controls, eligible/ineligible/invalid promo and valid/used/invalid game, preview, print warning, logout and audio return. Do not expose operator QR secret in screenshots.

**OPS-10.c**: Physical Windows camera/thermal printer checks, Ubuntu used mini-PC startup/audio/camera, and future Android tablet camera-position/permissions/performance checks are **separate**: mark evidence PASS/FAIL/SKIP/NOT_RUN based on actual tested device. Never infer production readiness from Kivy mocks.

**OPS-10.d**: Update feature status, README, decision register, test ledger, GUI v2 roadmap, handover and release/rollback record with verified SHA, last tested source, unresolved defects. No automatic deploy, merger, master promotion, production gateway enablement or merchant configuration.

**Pass gate:** owner-facing explicit acceptance report and independent decision; stage remains IMPLEMENTED/TESTED, not RELEASED until authorization.

---

## Future operational migration (separate roadmap, not OPS code authorization)

- Replace static operator QR with authenticated dynamic short-lived single-use QR per operator and booth, with optional challenge-response and role/audit. Keep offline emergency OS path.
- Replace static merchant DEMO claims with real receipt schema, receipt signature/server-side POS verification, replay-resistant unique transaction IDs, merchant consent/settlement, configurable discount campaigns and refund rules.
- Replace reusable Meong Fly DEMO with unique merchant-issued entry tickets validated server-side once, with one chance, authoritative paid quote and promo stacking rules explicitly approved.
- Define external QR scanning UX and photo booth camera mount on Android tablet and mini-PC, privacy/retention and remote diagnostics policies.
- Verify test-fixture hard OFF boundary in production builds and merchant Sandbox, including migration from existing `DEMO-` one-use storage and backward-compatible ledger fields.
- Do not infer release from passing test fixtures or generate actual customer credentials in Emulate Ticket.

## Mandatory stage checkpoint template

```text
Branch: feature/portrait-kiosk-v2-next
Priority check: AR-00..AR-13 status + exact unfinished AR step
Stage/substep: OPS-XX.y (only after authorized post-AR start)
Pre-source SHA / working tree / remote HEAD:
Edited files and deliberate non-changes:
Contract preserved + reversible migration:
Focused test command, OS, PASS / FAIL / SKIP / NOT_RUN:
QR/phone/physical printer/provider test evidence:
Screenshots/devices/version (no private token):
New commit SHA, pushed and remote verified YES/NO:
Outstanding risks/blocked/deferred:
Local-only changes (not backed up to GitHub):
Exact next action and rollback target:
```

Keep the owner’s **frequent micro-commit plus immediate push** rule in force; update documentation and [handover](../../DEVELOPMENT_HANDOVER.md) after each safe stage. Do not claim an empty docs-only commit proves any behavior.
