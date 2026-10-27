# Android v2 runtime — camera, printing and Sandbox

Owner continuation, 28 October 2026 (Asia/Jakarta): include QRIS Sandbox,
camera and printing and follow the features currently in GUI v2. Continue on
`feature/portrait-kiosk-android`; no new branch or desktop/master changes.
Base/rollback: f9e1239. Refreshed desktop reference: c001095.

## Review and implementation plan

Reviewed AGENTS, root/index, protocol, decisions, handover, architecture,
feature/bug/backlog/test ledgers, Android A0/A1, v2 product/technical/visual
contracts, branch audit, P3/P5/Sandbox, current printer/Drive/mirroring/storage
contracts and the newer customer FIFO/early-folder-QR and Sandbox-key fixes.
All contents of old remain excluded. Pre-restart local documentation/evidence
is preserved in a named Git stash; recovered A1 final report is 882 run,
879 PASS / 3 optional model skips / zero errors or failures, 266.232s.

Reuse the actual current desktop Python services, UI, original game, all twelve
templates, capture/review/retake/compositor, durable print and payment workers.
Portable delivery changes are taken as exact files from c001095, without a
branch merge. Android-specific camera, permission, lifecycle and configuration
adapters must not instantiate desktop camera drivers. Native camera output must
retain capture resolution and unmirrored originals; only existing display and
compositor paths mirror. Permission denial, pause and disconnect invalidate input
and cancel countdown. Resume never automatically captures or prints.

Printing uses the original ESC/POS renderer and one durable batch per design,
with SENDING before I/O and UNCERTAIN/no replay on ambiguous sends. Network
printing reuses TCP; Android USB requires UsbManager permission/transport rather
than Windows RAW drivers. The actual owner's connection/camera choice is pending.
No actual paper, merchant transaction or cloud deployment is performed in QA.

Sandbox reuses QrisKioskClient/KioskCheckout/SandboxViews over an authenticated
HTTPS backend. Merchant keys stay on the backend, never in the APK. App-private
configuration contains only booth credentials. Persist journals before requests;
STARTED ACK precedes countdown. Existing desktop merchant-trial delivery-off
isolation stays; Android's explicitly configured printer can test the combined
Sandbox/photo/print path under this new owner authorization.

Run focused native-adapter and real reused-UI tests, one final regression and
an actual new arm64 build. Record APK signature/manifest/ELF verification and
truthful device/provider limits. Original A1 artifact evidence remains historical.
Do not call feature parity verified without accounting for face/palm, video,
Drive setup, device transport and actual Android hardware acceptance.

## Progress

Portable synchronization: 106 targeted cases initially had one diagnostic
failure because the matching desktop launcher logging hook was missing. The
exact current launcher was then reused too; all ten diagnostic cases pass on
rerun. Remaining 105 initial cases passed. Raw reports are retained in
qa/android-runtime. Camera choice is built-in; printer choice is USB OTG.

Implementation in progress. No new camera/printing APK or Android hardware PASS
is claimed yet. Rollback uses scoped inverse commits and preserves all private
state, photos, counters, consumed attempts and uncertain payment/print jobs.
