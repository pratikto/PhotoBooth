# Meong Photobooth — Documentation Index

The repository-root [README](../README.md) explains setup and preserves historical development notes. This `docs/` directory contains the current documentation sources for the Kivy project on **`feature/kivy-gui`**.

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
- [Advertising and demo QR payment slip](advertising-and-qris.md) — current playback and printer setup, with **legacy LAN** instructions clearly distinguished from saved GUI printer configuration.
- [QA evidence archive](qa/README.md) — date-specific automated/visual reports that do not override later device failures.
- **[FEAT-001 / BUG-011 print-copy acceptance](qa/FEAT-001-BUG-011-acceptance.md)** — owner accepted DEMO pricing and working Windows physical copy counts after printer RAW fixes, with dated targeted CI, evidence limitations and future regression matrix.
- [Photo retention](photo-retention.md) — 15-day local/30-day Drive targets and associated data-loss considerations.
- [Thermal dithering lab](dither-tuning-lab.md) — standalone FEAT-011 experiment on `feature/dither-tuning`; has no effect on the production Kivy printer until separately approved.
- [Legacy NEXT_STEPS pointer](NEXT_STEPS.md) — retained for older bookmarks; do not edit as a second backlog.

## Current field status (2026-10-18)

**Most recent owner-tested FEAT-001:** Rp5,000 per selected template/session plus Rp5,000 per requested paper copy is implemented in the Kivy GUI (DEMO). Following the Windows printer job-finalization correction, the owner reports **pricing and physical copy count both work**. **BUG-011 is OWNER REPORTED PASS — MONITORING**, not formally CLOSED. [Focused CI 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) passed **15/15** business/print-spool mock tests; [full Kiosk GUI CI 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) still **failed**. The exact Windows local commit, printer queue and 1/2/3 paper-count measurements were not recorded.

The owner also reports improved Floyd photo quality (BUG-004), payment QR-slip paper output (BUG-003), idle/payment video playback (BUG-002), expected ad/tutorial navigation (BUG-005), advertisement sizing (BUG-006), dithering GUI scrolling (BUG-010) and responsive Settings (BUG-008). These are **owner-reported physical/UI passes**, not complete release verification.

**Intentionally deferred/unresolved:** tutorial/layout background music and `Uji Musik` (BUG-001/007); Google Drive 30-day photo-retention registration (BUG-009, to be coordinated with FEAT-004 advertising media synchronization). **Real payable QRIS (FEAT-020) is NOT implemented**; the onscreen payment QR and simulated checkout remain DEMO, not an authorized merchant charge. Other payment/settlement feature work remains low priority.

For authoritative ongoing status use the [bug tracker](bug_tracker.md), [feature table](FEATURE_STATUS.md), [priority board](next_step.md), [physical acceptance checklist](test_checklist.md) and [FEAT-001 evidence dossier](qa/FEAT-001-BUG-011-acceptance.md). This index grants no authorization to change code, merge, deploy or declare a released build.
