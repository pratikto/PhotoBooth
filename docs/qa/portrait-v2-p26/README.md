# P2.6 local visual evidence — 2026-10-21

> **Dated source/QA record, retained for traceability.** Results, “latest/current”,
> OPEN/PENDING labels, next actions and authorization limits below apply to this
> package's recorded source and report date. Later owner reports and source work
> can supersede its status; they do not rewrite these test results. Use
> [current status](../../FEATURE_STATUS.md), [test ledger](../../test_checklist.md)
> and [current handover](../../DEVELOPMENT_HANDOVER.md) for continuation. Historical
> checklists are not an instruction to repeat already accepted tests.

Baseline / rollback: `e888d9945bc8c0a4c74bd1a8de57e946acb26204`.
Branch: `feature/portrait-kiosk-v2-next` only.

Linux Python 3.12.14, Kivy 2.3.1, SDL offscreen, software GL and dummy audio.
40 portrait navigation/audio/design/widget tests PASS, no skipped tests (see tests.txt).
Both renderer commands completed: six pages at 800×1280 and six at 452×900.
Raw PNGs are preserved here with SHA-256 checksums; these are synthetic renders.

Reviewed all twelve baseline images at their original resolution. Advertising,
inline invitation, tutorial, gallery, copy cart and game placeholder retain their
complete CTAs and stepped cards. The compact tutorial intentionally scrolls;
its lower steps require a separate scroll interaction check in P2.7.
Found low-contrast disabled payment/scanner text: Kivy's default disabled_color
superseded the theme text. Set explicit readable secondary text and opaque
muted button faces; re-rendered both sizes and re-inspected affected pages.
Disabled controls remain disabled. Game/scanner/discount/payment stay disconnected.

**Local evidence only. Matching-SHA GitHub CI and downloaded artifact inspection
are still required by the QA gate. P2.6 is not yet certified PASS.**
No Windows speaker/touch/camera/printer/Drive acceptance is claimed.
