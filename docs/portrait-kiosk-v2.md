# FEAT-022 — GUI v2 specification and roadmap

**27 October operational continuation:** FEAT-009 stages 1–2 add observer,
read-only recovery/startup holds and shared launch ownership, plus generated
Ubuntu graphical-session startup alongside Windows development support. Automatic
restart and all physical/cloud/provider/release gates remain separate.
[Current stage, tests and Ubuntu guide](qa/portrait-v2-recovery/README.md).
The primary working rule is comprehensive documentation review before code and
documentation synchronization after code, persisted in AGENTS/protocol.

Updated **26 October 2026**. Active development and intended future primary
branch: **`feature/portrait-kiosk-v2-next`**. GitHub default remains `master`;
`main.py` remains v1. [Current checkpoint/evidence](FEATURE_STATUS.md) ·
[handover](DEVELOPMENT_HANDOVER.md) · [promotion plan](gui-v2-promotion-plan.md).

GUI v2 owns its portrait UI/audio lifecycle and reuses working camera, capture,
templates, printer, Drive, original game and QRIS services through small adapters.
It is beyond the earlier gallery-only prototype; do not rebuild existing features.

The coordinated FEAT-004 + BUG-009 storage implementation now mounts per-booth
25-slot local reserves, Photo/NN/raw/color/bw and verified global/local caches
in the ordinary launcher. Offline admission does not require a remote slot;
Drive binding/upload and verified QR follow reconnect, without print replay.
Actual Google setup/deployment, expiry and hardware acceptance remain pending.
[Source evidence](qa/feat-004-storage/README.md) · [Setup](qa/feat-004-storage/SETUP.md).

## Product flow

1. Advertising opens first; MULAI FOTO and MAIN MEONG FLY share the same media
   surface. The face invitation is an overlay, with manual entry retained. There
   is no separate CARA PAKAI action: photo entry already requires the tutorial.
2. Tutorial acknowledgement is required once per active visit, including after
   either game result if unseen. Safe return to idle resets transient visit state.
3. Gallery: twelve original 80×240 mm strips, three photo slots plus one download
   QR. Swipe/arrows move the designs; the center strip is emphasized. Quantity
   zero deselects; 1–9 means identical copies from one session per selected design.
4. Local/default: UJI FOTO → consent → three captures with five-second countdowns
   → review/one retake per design → composition/result → advertising. Output is
   local unless the operator opts into --print/--drive: approved strips auto-print
   once/design, the existing queue uploads/resumes in background, and a large
   on-screen download QR appears once the assigned folder is verified, even while
   uploads are pending. Its message suggests checking back in 30 minutes without
   guaranteeing delivery time. Customer uploads run FIFO ahead of old retries
   and maintenance, with bounded failure release. --manual-print
   retains deliberate manual printing.
   Photo areas in v2 review/result/printed/digital strips are mirrored, matching
   live preview; full-resolution JPEG originals stay untouched and template/text/QR stay normal.
5. Game DEMO: intro → manual one-use DEMO code → original game → win/lose →
   tutorial if unseen → gallery. No retry; consumed codes stay consumed after restart.
   Real scanning/POS is not mounted in v2.
6. Opt-in MOCK: nonpayable checkout, locally validated one-use reward/quote and
   one admission to photo consent. A win reduces one order by Rp2,500, capped at subtotal.
7. Opt-in Sandbox: explicit full-price/no-game-promo consent → provider Sandbox
   QR → backend verification/grant → photo consent → durable STARTING → one
   transaction → STARTED ACK → capture → all selected designs → COMPLETED ACK.
   Pending/unknown/paid/recovery is protected from browsing timeout.

Tariff in source: **Rp5,000 per selected design/session + Rp5,000 per copy**.
One design with 1/2/3 copies costs Rp10,000/Rp15,000/Rp20,000; mixed A×2+B×1
costs Rp25,000 with two three-photo sessions. Zero-copy digital-only purchase
and final commercial maximum policies are not implemented/settled by these controls.
Sandbox does not accept the game reward: there is no trusted backend promotion
contract. GUI scores/amounts never authorize a provider discount.
The printed photo-folder QR is separate from the payment QRIS.

## Planned GUI v2 follow-up — QRIS Payment Slip (owner request, 29 October 2026)

**Status: PLANNED / DOCUMENTATION ONLY.** Add an optional customer-facing **CETAK QRIS** action to the native GUI v2 payment screen in a future separately scoped implementation. The printed thermal slip lets a customer scan the **same currently valid Midtrans payment QR** from paper when a phone cannot conveniently scan the kiosk screen. The **on-screen QR must remain visible and usable**; paper is an alternative, not a mandatory step or a new payment transaction.

- **Reuse existing source; do not rebuild:** inspect `photobooth/qris_print.py` (`render_payment_slip`, `QrisPrinterWorker`) and the shared configured thermal-printer interfaces before writing v2 adapters. Existing v1/shared payment-slip behavior is not evidence of native GUI v2 integration.
- **Payment and QR identity:** use exactly the active backend/provider-authorized payment QR payload and original merchant/order/amount/expiry; never generate a new charge, modify the QR contents, or prolong QRIS validity just because it was printed. Printing, printer acceptance and a slip on paper **never confirm settlement or authorize photography**.
- **Visibility and controls:** show the print option only for an eligible live `PENDING` payment and configured/ready supported printer. Provide clear disabled/error states and a background print worker; preserve payment status polling, payment QR visibility, copy-link (Sandbox), and the checkout UI lifecycle. Do not print for PAID, EXPIRED, CANCELLED, ambiguous or stale QR evidence.
- **Thermal quality and delivery safety:** preserve readable native ESC/POS QR modules/quiet zone on 80 mm paper; use existing LAN/Wi-Fi/Windows USB configuration as supported by the shared printer. Record a durable **per-order payment-slip print attempt** and cap duplicate taps. A failed/uncertain send must not be silently replayed after a crash; distinguish PREVIEW, SENT/QUEUED and physically verified paper, which the app cannot infer merely from a successful socket send.
- **Separate QR types:** QRIS Payment Slip != customer Recovery Ticket QR != photo Google Drive download QR != merchant receipt promo QR. No raw customer recovery secrets or private photos on payment slips.
- **Current Sandbox restriction:** the dedicated GUI v2 Midtrans Sandbox launcher currently forces printer and Drive **OFF**. This documentation does **not** relax isolation, enable physical printing, activate production payments, or authorize a new release. An isolated print-preview/mock verification may be designed, but any actual paper/provider combination needs a separately approved controlled acceptance mode.
- **Acceptance before calling implemented:** state/identity/expiry tests, fast duplicate taps, fail-before-send and uncertain-after-send, restart/no-double-print, printer offline, payload comparison from screen/printed pixels, both 800x1280 and 452x900 GUI sizes, real configured 80 mm hardware and recorded source SHA. Preserve existing status/settlement and photo-admission gates.

[QRIS scope and implementation backlog](next_step.md) · [Existing owner decision](DECISIONS.md) · [Current feature evidence](FEATURE_STATUS.md).

## Future GUI v2 follow-up — Meong Settings and Emulate Ticket (owner-approved design, 29 October 2026)

**DEVELOPMENT ORDER:** **AR-00 → AR-13 remains the highest priority**. See the [live AR checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md) and [AR roadmap](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md). This Settings/Emulate Ticket proposal is **DOCUMENTATION ONLY**, not implemented by approval or by a docs commit. No interruption/replacement of AR-09 protected operator actions or AR-12/13 validation/readiness.

**Complete canonical contract:** [Meong Settings — operator static QR, Audio and Emulate Ticket](qa/portrait-v2-operator-settings/README.md) · [future OPS-00–OPS-10 roadmap](qa/portrait-v2-operator-settings/IMPLEMENTATION-ROADMAP.md) · [acceptance tests](qa/portrait-v2-operator-settings/ACCEPTANCE-MATRIX.md) · [decision/supersession register](qa/portrait-v2-operator-settings/DECISION-REGISTER.md) · [Codex prompt](qa/portrait-v2-operator-settings/CODEX-HANDOVER.md).

- Preserve current hidden F12/1.5-second Meong-header hold **only on first Advertising + verified SAFE_IDLE** and route it to a live-camera **Operator QR Login**, not the existing direct Health popup. **Static, high-entropy per-booth operator QR for development**, locally hashed/offline, revocable/rotatable. No ordinary Settings PIN, but AR-09 financial operator PIN remains separate. OS-authenticated maintenance fallback for broken camera. Mirrored scanner preview, original QR decode and one existing camera owner. Pause ads/face invite during login; cancel/timeout/close restores Advertising; 3-minute inactivity logout.
- Exactly **three Settings tabs:** (1) **Device Health**, reusing the current read-only health worker/reports and optional redacted copy; (2) **Audio Settings** with per-booth persistent **Master Volume, Music, Button SFX, Other SFX, Mute and Test Sound**, retaining correct normal/game/ad-video audio lifecycle; (3) **Emulate Ticket**, the owner's final name replacing “Ticket Master”.
- **Emulate Ticket** has **Merchant Promo — DEMO** and **Meong Fly Entry — DEMO**. **Static, reusable QR fixtures** during development with Eligible/Not Eligible/Invalid and Valid Entry/Already Used/Invalid test presets. The "already used" test rescans the same **actually consumed** valid QR. Exactly one attempt or promo per logical visit, persisted across restart; same QR can be reused in a genuinely separate test visit. Original game/one-use real receipt semantics remain unchanged. No Merchant Promo + Meong Fly stacking initially; demo reward and illustrated Rp50,000/Rp5,000 waiver are not real merchant offers.
- **Preview / Print DEMO Ticket** uses existing native 80-mm thermal transport with durable, honest attempt status, uncertain/no-auto-replay and bounded non-sensitive test history. **Midtrans Sandbox printer/Drive remain OFF**, no new payment authority, no production DEMO acceptance.
- **QRIS Payment Slip from the preceding section remains separate**: it prints only a valid pending provider QR and is **not** a merchant promo/game/recovery/operator ticket. Customer Recovery Ticket stays securely unique per order. All role namespaces and scanners must be isolated.

Only after AR priority and separate code authorization may Codex execute OPS-00–OPS-10, with independent focused checks, small commits and immediate pushes/remote verification, full handover and actual physical acceptance on Windows/Ubuntu and later tablet as applicable.

## Roadmap: implemented source versus remaining evidence

| Stage | Source now | Acceptance boundary |
| --- | --- | --- |
| P0 | VisitFlow/tutorial-once/protected lifecycle | Automated regression recorded |
| P1 | One v2 audio owner, SDL2 WAV loading, SFX/minimize/close | Owner reports v2 audio normal; v1 BUG-001/007 not closed |
| P2/P2.5/P2.6–P2.8 | Responsive advertising/overlay/tutorial/gallery, swipe/transitions, current typography/header | Automated source and dated owner reports; older P2 “no integration” scope is historical |
| P3a | Async camera, mirrored preview, face invitation and optional palm | Owner-reported corrections accepted; missing source/device fields remain unknown; reconnect/current-integration evidence separate |
| P3b | Three originals, one retake/design, composition/result, opt-in auto-print/background Drive with verified result QR | Default local; fixture tests do not certify paper/download/cloud deletion |
| P4a | Original Meong Fly Stage/Flow/render/assets/emitter and one-use DEMO ledger | Owner-reported game/visual PASS; real scanner/POS disabled |
| P4b MOCK | Local quote/reward/admission ledger | Nonpayable simulation |
| P4b Sandbox | Existing service/client/journal plus native v2 host and isolated launcher | Actual merchant simulator/current-device evidence pending; no trusted game promo |
| P5 | Readiness CLI, metadata import/Submit form, regression/screenshots/rollback package | **Ready for acceptance**, not commercial certification; Windows/merchant/paper/Drive/privacy/release gates remain |
| Operator increment | Original v1 read-only health panel/worker + safe reports; BUG-018 input guard at `ebb53fd` | Initial raw 8/8/hang preserved; later [four-item retest](qa/portrait-v2-health-clicks/README.md) 4/4/no issues, OWNER-REPORTED PASS / MONITORING at unknown HEAD; selection disabled |
| Primary branch transition | Owner direction and reference audit recorded | Default/rename/merge/launcher/release operations not performed |

Owner approved P4b/P5 with manual tests at the end, then safe source continuation
while laptop checks wait. Health/report source is complete. The preflight at
`0dc6555` is READY_FOR_MANUAL_TEST, not merchant/hardware acceptance.
[Latest evidence ledger](test_checklist.md) records the 800-test print/Drive
source (266b2c8, matching three-job CI SUCCESS/133 verified PNGs), 785-test BUG-018
correction, 780-test original operator source and earlier 688-test P5 baseline,
including optional CI skips. Later owner BUG-018 retest is 4/4/no issues;
exact tested source/device metadata and external acceptance remain unverified.

Owner then resumed BUG-009 on 26 October: source 887ba39 adds safe retention
diagnosis and follows the actual-CLOCK activation correction 130aae1, reusing
v1 cleanup. **807 full Python PASS/zero skips and 19 Code.gs VM PASS**; actual
Google setup/deployment/timer/deletion remain unverified, and BUG-009 stays OPEN.
[Current activation/evidence package](qa/bug-009-retention/README.md).

## Visual, audio and evidence

Portrait 10.1-inch target; required reference sizes **800×1280** and **452×900**,
with compact/landscape/scaling checks where relevant. Preserve cosmic pixel-space,
original game materials and Meong art. Main-app captions use readable native
Roboto without mandatory icons, with the larger animated mascot and focused strips.

Still advertisements use GUI BGM; video uses its own audio. Tutorial/gallery/
photo/checkout share a GUI loop; game has a separate loop. One enabled action,
one cue; minimize/close retires prior playback/callbacks.

![Approved main artboard](assets/portrait-v2/meong-main-flow-approved.webp)

![Approved revised game artboard](assets/portrait-v2/meong-fly-revised-approved.webp)

[Current visual interpretation](portrait-kiosk-v2-visual-spec.md) ·
[asset provenance](assets/portrait-v2/README.md) ·
[technical contracts](portrait-kiosk-v2-technical-design.md).
Artboard sample prices/arrows/scanner pictures do not override implemented flow.
Use [README launch instructions](../README.md), [P5 form](qa/portrait-v2-p5/windows-checklist.html)
and [operator form](qa/portrait-v2-operator-health/windows-checklist.html).
Production, trusted merchant promo, real scanning/POS, deployment, merge and release remain separate.
