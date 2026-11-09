# PP-04 B3 original receipt RPC and shared printer lane

9 November 2026, feature/post-preview-qris-checkout; basefd0da65.

OriginalRecoveryPresentation now accepts only an explicit exact ThermalPrinter
and shared original lock pair, or neither when no printer is configured. Trusted
Sandbox factory injection owns these dependencies; no HTTP request selects a
printer, payload, copies or payment authority. Host startup/real operator printer
configuration is NOT mounted by this dependency seam alone. Default child still
has no device and records NOT_SENT truthfully. Full customer launcher stays gated.

Authenticated original-owner ticket/receipt delegates to the SAME original
RecoveryTicketService.send_receipt_once. It renders the original on-screen ticket
in memory through the existing renderer/print_bitmap/ESC-POS path, one copy on
the shared lane. Original SQL SENDING commits before any transport; SQL lock is
not held through I/O. The ticket actor serializes concurrent receipt requests.
Repeated/lost-response requests return original job state without a second send;
restarted SENDING, SUBMITTED, NOT_SENT and UNCERTAIN are observation-only. No
fallback after partial write, fabricated paper success, new job or token reissue.

Native typed receipt client validates the exact role/mode/group/booth/generation/
permit/job/state envelope. physical_paper_verified must always be False: SUBMITTED
means transport, not physical acceptance. RemoteRecoveryTicketSession dispatches
through the serialized worker only after backend-visible acknowledgement. Its
native genuine-render clock/poll/NEXT/privacy code never acquires that RPC lock
or printer lane. Screen wipes at30s/NEXT even while the original sender blocks;
later durable dismissal follows worker completion. No ticket/bitmap/raw bytes
are written to disk, ordinary response/log or screenshot.

## Evidence

Test-first five ERRORs (2.000s): original presentation constructor had no printer
seam. A later fixture edit accidentally moved four assertions into another test;
one assertion failure was corrected without weakening source checks. Final
**80 related backend PASS (52.694s), 7 native PASS (9.356s)**, zero failures,
errors/skips. Overlapping groups are not acceptance percentages.

Tests prove auth/current-owner/generation/permit and strict bodies precede paper;
exact original proof enters the real renderer; one original ThermalPrinter fake
network send sees SENDING and the same locked lane; concurrent/repeated requests
send once; partial write remains UNCERTAIN without fallback; no route records
NOT_SENT without later replay; restarted SENDING only observes. Client rejects
cross scope, invalid states and physical-success claims.

Actual separate child/fixed Sandbox transport/HTTP/client/native-card test now
uses the SAME original printer with fake network transport, persists only a
non-secret send count, and observes SUBMITTED after child restart without another
send. The unconfigured child path separately proves NOT_SENT. Four native cases
cover timeout and NEXT while receipt blocks at both800x1280 and452x900. All
provider/Drive/Linux custody/printer transports remain explicit controlled
fixtures. No real merchant, paper or target Ubuntu-device acceptance is claimed.

[Source hashes and exact focused evidence](provider-ticket-2026-11-09/receipt-verification.json).
CI installs the already-existing python-escpos[usb] runtime dependency from the
main kiosk requirements because these tests exercise its real raster builder.
Both new test modules join existing registered backend/native commands. No test
removal, timeout change, suppressed skip or manual unchanged baseline rerun.
Final new-source full regression/current CI remain pending at publication.
Previous3ea1d8c CI42591856392 all three SUCCESS (680 Windows/680 Ubuntu/80 native),
with completed logs inspected, remains at its original source.

Next source: backend paid Drive/approved strip/upload authority and authenticated
native delivery client; original proof-gated claim/WAIT/worker PREPARE/ACK release;
then complete protected customer launcher and secure real printer configuration
in child bootstrap/readiness. Reuse original services through explicit backend
authority, never a dummy provider in GUI or mock-guard removal. Refund/status,
operating package, supported Ubuntu restore and real account/device/qualification
remain unfinished. Commercial status NOT_READY; health fulfillment_enabled=False.

Reviewed current handover/AGENTS/security/ticket/receipt/shared-lane/no-replay
contracts and original printer/config/result/renderer, dispatcher and protected
backend/native source and tests before this extension. Preserve all original
PAID/OWED, encrypted custody/media and SENDING/UNCERTAIN journals. Rollback scoped
source only. No original data/key resets, live money/cloud effects or deployment.
