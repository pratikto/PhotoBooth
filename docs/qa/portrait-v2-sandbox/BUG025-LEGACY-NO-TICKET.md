# BUG-025 — Sandbox legacy session without a recovery ticket

30 October 2026. Base f2099c1 on feature/portrait-kiosk-v2-next.
Owner laptop reports claim page, then authenticated operator PAID/STARTED/OWED,
no issue, disabled ISOLASI; owner confirms no saved recovery ticket. Actual
tested laptop SHA and capability presence are unknown. Source confirms the
native release button excludes a backend order with no bound capability.
Do not assume a screenshot alone proves this is the only possible disabled cause.

## Bounded implementation contract before code

Reuse existing PIN + booth authentication, fresh Sandbox provider verification,
two-phase release fence, serialized transport-off PhotoTest isolation receipt,
ACK and durable original-visit archive. Add an explicit legacy_without_ticket
prepare flag; default release still requires a valid original capability.
The exception requires NO capability row, PAID freshly settled, OWED, original
booth/order and independent operator authentication. Existing revoked/expired
capabilities cannot use this legacy exception. No raw credential is created,
recovered, replaced or displayed, and no customer-photo access is granted.

Record distinct static reason SANDBOX_LEGACY_NO_TICKET in original release audit;
bind operation identity to that reason so retries cannot change intent. Existing
ACK/isolation receipt rules and archive-before-new-visit remain unchanged. A
legacy archived visit cannot be self-claimed without original customer proof;
its retained OWED record requires owner review, not fabricated delivery/refund.

GUI must explain why ordinary isolation is unavailable; offer ARSIPKAN UJI TANPA
TIKET only for explicit backend false capability + PAID Sandbox order. First
click opens explanation/confirmation, performs no backend mutation, clears PIN.
Then re-enter latest local PIN and confirm isolation; after actual worker receipt,
re-enter PIN and LEPAS BOOTH. Cancel/minimize retires confirmation, input and old
widgets. Busy, stale callbacks, wrong PIN, wrong booth, mock/production, provider
outage/refund and SENDING/UNCERTAIN/transport isolation denial remain held.
New Sandbox visits keep mandatory save-ticket screen; printer/Drive remain OFF.
No profile/booth switch, order/file deletion or manual editing is a workaround.

## Validation and delivery

Add meaningful original HTTP/store tests for legacy opt-in, preserved PAID/
STARTED/OWED/frozen identities, no cap issuance, prepare-holds/ACK-frees, intent
replay mismatch, wrong auth/modes/provider failure and existing-capability denial.
Controller tests use original HTTP + typed worker receipt + restart/lost ACK/
archive failure, no new charge/capture. Native tests at 800x1280/452x900 exercise
confirmation cancel/retirement, wrong PIN, isolation/ACK, private original media,
and mandatory ticket screen on a fresh visit. Add actionable owner instructions
to the novice checklist. Focused checks per micro-increment; one final full
regression after functional GUI change, matching CI and final evidence.

Reviewed current AGENTS, README/docs index, protocol, checkpoint/handover,
AR roadmap/operations/operator/native/customer-claim, recovery plan, purchased-print
limits, feature/bug/changelog records and original backend/API/client/controller/
release/photo/native fixtures. Earlier mock purchased-print lifecycle remains
unmounted and its guards are unchanged. OPS remains queued; commercial release,
production, actual merchant/device, Ubuntu, paper/Drive/privacy/compensation and
PAY-22/WEB gates remain separate. Do not alter the authoritative acceptance matrix
based only on this bug fix. Old dirty workspace and private work/ stay untouched.

Status at contract: IN_PROGRESS; new checks NOT_RUN. Rollback by reviewed inverse
source change only; retain all records/media/audit/fences and disable new action.

## Backend checkpoint

Five new checks; focused release/store/controller/HTTP recovery **41 PASS**,
zero failure/error/skip, 2.974s. Raw private report work/bug025-backend.txt.
Initial two failing tests reproduced absent API path. One placement error moved
an unchanged original fixture method into the new class; restored original name
and setup, final focused rerun PASS. GUI/full/current CI still pending.

## Native checkpoint

GUI confirmation/cancel, PIN/receipt/ACK and missing-ticket explanation implemented.
Native group28 PASS, then final compact-layout/normal release pair2 PASS. Six
clean-process native captures at both sizes, private source logs work/bug025-*.
Windows release-session registration added. Final full/current CI pending;
[evidence](evidence/bug025-verification.json). No laptop result claimed.
