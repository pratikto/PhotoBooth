# Meong Photobooth — Documentation Index

The repository-root [README](../README.md) explains setup. **Current source of truth:** `master` (Kivy application); `v1.0.0` is the immutable, published source baseline. The previous `feature/kivy-gui` is preserved as development history, not the primary branch. Dated records remain useful evidence but do not override current status.

> **CURRENT RELEASE BASELINE (2026-10-19):** Default branch `master` contains Meong Photobooth Kivy GUI. Immutable source snapshot `v1.0.0` / `07ce51d2022ab5673a7a27e744e5e5757fbb3d08` is published as a [GitHub pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0). Release-SHA CI: [Kiosk GUI 39185986245](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245) (**233 pass, 2 skipped, 87 synthetic renders, 0 errors**) and [Dither 39185986273](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273) (**48 tests pass**). Linux mock/screenshot QA is **not** certification on Windows hardware or customer deployment. Outstanding: BUG-001/007 audio speaker retest, BUG-009 30-day Drive cloud retention **OPEN**; QRIS is DEMO/non-payable (FEAT-020 not implemented), receipt scanner FEAT-002 not implemented. The earlier `feature/kivy-gui` branch and dated narratives below are **historical** where they conflict with this baseline.


## Start here: current product and operational truth

| What you need | Canonical file | How to interpret it |
| --- | --- | --- |
| Agreed owner rules (commercial policy, pricing goal, advertising entitlements) | [DECISIONS.md](DECISIONS.md) | **Owner-confirmed requirements**; not proof of production implementation |
| Current implementation and known device limitations | [FEATURE_STATUS.md](FEATURE_STATUS.md) | **Source status + owner reports**; device signoff remains separate |
| Active defects, severity, next reproduction | [bug_tracker.md](bug_tracker.md) | Operational priority before any new features |
| Evidence of automated vs physical tests; release checklist | [test_checklist.md](test_checklist.md) | Never transfer historic mock tests into current hardware acceptance |
| Proposed / not-yet-approved feature backlog and monetization ideas | [next_step.md](next_step.md) | One **unified provisional queue**; parked ideas are not scheduled |
| Steps to safely continue engineering | [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) | Current handover section first; old dated notes below remain historic |
| Development approval and test rules | [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) | No app-code changes without explicit owner-approved scope |
| **Reusable prompt for new chats and implementation tracking** | [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md) | Copy/paste the full or quick prompt; defer to the protocol for governance |
| Actual repository/document change history | [CHANGELOG.md](CHANGELOG.md) | Not a release certificate or record of physical success |

## Supporting technical references

- [Architecture](ARCHITECTURE.md) — actual source-level modules vs proposed system design.
- **FEAT-003 live camera mirror:** capture-page GPU preview mirror implemented in `ui_kivy.py`; owner explicitly confirms Windows **TESTED PASS (2026-10-18)**, and [targeted Kivy GPU Actions 39139208320](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320) also **PASS**. Full Kiosk CI/release checks remain separate. FEAT-002 receipt scanner/overlay is unimplemented. [FEAT-003 acceptance checklist](test_checklist.md).
- [Advertising and demo QR payment slip](advertising-and-qris.md) — current playback and printer setup, with **legacy LAN** instructions clearly distinguished from saved GUI printer configuration.
- [QA evidence archive](qa/README.md) — date-specific automated/visual reports that do not override later device failures.
- **[Full Kiosk GUI Regression — verified green CI](qa/KIOSK-GUI-REGRESSION-2026-10-18.md)** — 230 passing / 2 skipped unit tests, 87 render checks, historical FAIL diagnosis and scoped test/CI-only repairs (source SHA `f129dd9e`).
- **[FEAT-001 / BUG-011 print-copy acceptance](qa/FEAT-001-BUG-011-acceptance.md)** — owner accepted DEMO pricing and working Windows physical copy counts after printer RAW fixes, with dated targeted CI, evidence limitations and future regression matrix.
- [Photo retention](photo-retention.md) — 15-day local/30-day Drive targets and associated data-loss considerations.
- [Thermal dithering lab](dither-tuning-lab.md) — the standalone three-algorithm comparison tool originated in `feature/dither-tuning` and was **included in the Kivy code now on `master`**. The owner-approved Floyd preset **is now the default for Kivy photo printing**; lab JSON presets themselves still do not load automatically into `main.py`.
- [Legacy NEXT_STEPS pointer](NEXT_STEPS.md) — retained for older bookmarks; do not edit as a second backlog.

## Current field status and verified CI (as of 2026-10-19)

**Current v1.0.0 quality gate (2026-10-19):** [Kiosk GUI 39185986245](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245) (**233 pass, 2 skipped, 87 synthetic renders, 0 errors**) and [Dither 39185986273](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273) (**48 tests pass**). This covers automated Linux simulations only; physical Windows camera, thermal printer, speaker, codec and real customer experience remain separately assessed. Earlier `c40f33f5` checks are historical.

**Latest owner-tested FEAT-001 / BUG-011:** Rp5.000 per selected template/three-photo session plus Rp5.000 per requested copy is implemented. **Both price and actual copy-count passed the owner's Windows test. BUG-011 = OWNER TESTED PASS — MONITORING**, not formally CLOSED/RELEASED. Focused mock/spool CI [39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) **15/15 PASS**, and later **full Kiosk GUI CI PASS** (above). Exact local device SHA, queue identity and 1/2/3 paper-count case matrix were not provided.

The owner also reports improved Floyd photo quality (BUG-004), payment QR-slip paper output (BUG-003), idle/payment video playback (BUG-002), expected ad/tutorial navigation (BUG-005), advertisement sizing (BUG-006), dithering GUI scrolling (BUG-010) and responsive Settings (BUG-008). These are **owner-reported physical/UI passes**, not complete release verification.

**Intentionally deferred/unresolved:** tutorial/layout background music and `Uji Musik` (BUG-001/007); Google Drive 30-day photo-retention registration (BUG-009, to be coordinated with FEAT-004 advertising media synchronization). **Real payable QRIS (FEAT-020) is NOT implemented**; the onscreen payment QR and simulated checkout remain DEMO, not an authorized merchant charge. Other payment/settlement feature work remains low priority.

For authoritative ongoing status use the [bug tracker](bug_tracker.md), [feature table](FEATURE_STATUS.md), [priority board](next_step.md), [physical acceptance checklist](test_checklist.md) and [FEAT-001 evidence dossier](qa/FEAT-001-BUG-011-acceptance.md). This index does not authorize further code changes, deployments, or upgrading the versioned **source pre-release** into a hardware-certified production release.


### FEAT-022 — comprehensive portrait GUI v2 documentation (2026-10-21)

The current **owner-authorized working branch is feature/portrait-kiosk-v2-next**, derived from the existing feature/portrait-kiosk-gui prototype; **master/v1.0.0 remains unchanged**. Start at the [consolidated FEAT-022 design, current source and QA specification](portrait-kiosk-v2.md).

**Approved mockup artboards (both embedded, full-resolution):**

- [Main photobooth visual flow (actual approved board)](assets/portrait-v2/meong-main-flow-approved.webp)
- [Meong Fly promo/game flow (actual approved board)](assets/portrait-v2/meong-fly-flow-approved.webp)
- [Screen-by-screen visual/interaction interpretation and corrections](portrait-kiosk-v2-visual-spec.md) — *required reading*: idle and face invitation share the entry, game has its own intro, win/lose → tutorial iff unseen → template picker, not payment.
- [Technical architecture and future interface contracts](portrait-kiosk-v2-technical-design.md) — current code vs proposed camera/game/QRIS/Drive adapters and secure session/payment invariants.
- [Mockup asset origin, hashes and scope](assets/portrait-v2/README.md), [CI/hardware QA matrix](test_checklist.md) and [feature implementation truth](FEATURE_STATUS.md).

**Latest verified synthetic evidence:** [portrait v2 workflow 39548798578](https://github.com/pratikto/PhotoBooth/actions/runs/39548798578), code + mockups SHA 6e7f29a7: **21/21** navigation/audio tests, Kivy widget smoke and twelve screenshot states at 800×1280 and 452×900 passed. This is **not** audible Windows music, touchscreen, real Meong Fly, real merchant/POS receipt, camera, payable QRIS, thermal print or Drive hardware verification.

**Try the opt-in prototype:** switch to feature/portrait-kiosk-v2-next, install the existing Kivy dependencies, then run **python tools/run_portrait_v2.py**. **python main.py** still launches the legacy v1 booth. The current v2 game CTA shows an *unavailable placeholder*; it is not an integrated gameplay/discount feature. No code change, merge, release or customer deployment is authorized by this documentation entry.

### FEAT-022 — separate portrait GUI v2 development branch

[Portrait kiosk v2 design/rollback/QA plan](portrait-kiosk-v2.md) records the new opt-in 10.1-inch Pixel Arcade Space GUI, audio lifecycle, tutorial-once gate and approved isolation from released v1. Historical prototype branch: feature/portrait-kiosk-gui; continuing work: feature/portrait-kiosk-v2-next. Development launcher: python tools/run_portrait_v2.py; the default python main.py remains v1. Current source is a partial prototype, NOT an integrated camera/QRIS/mini-game/printing release.
