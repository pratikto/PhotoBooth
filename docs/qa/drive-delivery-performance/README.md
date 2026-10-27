# FEAT-004 / BUG-009 / FEAT-022 delivery performance — 27 October 2026

Owner authorizes investigation, implementation, tests, documentation and staged
pushes on feature/portrait-kiosk-v2-next. Base/rollback source:
fcabfbb8559778055631ff3a066f14108392ef71 (remote verified unchanged).
No live deployment, cloud deletion, physical print or payment action.

Reviewed before code: AGENTS, root README, documentation index, protocol,
handover, feature status, architecture, decisions, bug register, backlog,
v2 specification/technical design/test ledger, storage layout, drive-photo-layout
QA, FEAT-004 storage QA/setup, photo retention and print/Drive QA.
Current numbered-cloud/offline-admission contracts supersede older linked setup
paragraphs that required an online reserve before consent.

## Findings and scope

The owner reports over five minutes before the large QR, then a disabled Finish
button/processing footer. No session timing log was supplied, so the cause of
that delay is **not proven**. Source confirms synchronous content maintenance,
whole-pool reserve validation after a single claim and a snapshot busy-state
presentation defect. Print was deliberately disabled and stays disabled.

V1 comparison at origin/master 27f3801: `_should_show_result_qr` accepts a real
folder URL before uploads finish; the upload label describes incompleteness.
That explains earlier QR availability, not measured upload throughput. V2 keeps
its stricter UPLOAD_COMPLETE requirement. No v1 early-screen-QR behavior is copied.
The existing v1 upload/checksum/revision engine and QR encoder remain reused.

## Stage 1 — foreground state

PhotoJobs distinguishes foreground commands from background snapshots. A result
rebuilt during a pending snapshot keeps Finish enabled and the footer clear;
foreground commands and uncertain-print guards still block the relevant input.
Snapshot completion updates the footer without rebuilding/reprinting. Result
progress uses real verified-file counts; no percentage/ETA. Only UPLOAD_COMPLETE
can expose the large QR. Safe `delivery_timing` events use a transaction ID and
numeric fields, with a GUI QR-publication event.

Local controlled native regression: one test PASS, 2.080s, Linux/Python 3.12,
Kivy 2.3.1/SDL offscreen/dummy audio. Rebuild during blocked snapshot, disabled
operator printing, restored Finish/footer and return to ads verified. This is
not Windows touchscreen, cloud upload or physical paper acceptance.

Rollback: scoped inverse source commit; preserve photos, counters, claims,
manifest revisions, print/payment journals and original 15/30-day clocks.
