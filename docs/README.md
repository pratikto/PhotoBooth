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
| Actual repository/document change history | [CHANGELOG.md](CHANGELOG.md) | Not a release certificate or record of physical success |

## Supporting technical references

- [Architecture](ARCHITECTURE.md) — actual source-level modules vs proposed system design.
- [Advertising and demo QR payment slip](advertising-and-qris.md) — current playback and printer setup, with **legacy LAN** instructions clearly distinguished from saved GUI printer configuration.
- [QA evidence archive](qa/README.md) — date-specific automated/visual reports that do not override later device failures.
- [Photo retention](photo-retention.md) — 15-day local/30-day Drive targets and associated data-loss considerations.
- [Legacy NEXT_STEPS pointer](NEXT_STEPS.md) — retained for older bookmarks; do not edit as a second backlog.

## Current field status (2026-10-18)

Operator reports **photo strip paper output works but is blurry**, **payment QR-slip printing fails**, **idle/payment videos do not play**, and **application music plus Settings `Uji` controls remain problematic**. See BUG-001/002/003/004/007; tutorial route and opening-video size also await validation (BUG-005/006).

**Payment remains DEMO (not real QRIS).** Present code uses IDR 5,000 per **independent photo session**; future per-copy billing, merchant promotions, centralized ad inventory and subscription licensing are planned decisions, **not running production features**.

No content in this directory authorizes programming, merging, releasing, running real customer payments or claiming a bug fixed. Ask for owner approval and test the actual target machine.
