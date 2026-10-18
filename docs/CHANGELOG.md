# Meong Photobooth — Documentation and release changelog

This file tracks **actual verified repository/document changes**, not successful live booth operation. Historical test assertions are kept in [FEATURE_STATUS.md](FEATURE_STATUS.md), [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) and [QA evidence](qa/README.md). Application code can be considered released only under [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md).

## [Unreleased] — 2026-10-18

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
