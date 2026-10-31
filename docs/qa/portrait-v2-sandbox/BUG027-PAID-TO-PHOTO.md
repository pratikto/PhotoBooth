# BUG-027 — printed recovery receipt, then direct camera

31 October 2026, Asia/Jakarta. Owner sees PAID → mandatory save-ticket screen →
privacy claim. Latest instructions supersede the earlier paid-ticket screen:
minimize tickets, never show a compulsory ticket page; automatically print one
recovery receipt with usage instructions after PAID, then enter photo capture.
No extra save-ticket or photo-confirmation clicks in the normal paid flow.
Manual SIAP/countdown, review/retake and approval remain intentional actions.

Same feature/portrait-kiosk-v2-next branch, base0e58de6. Recovery receipt printing
is now explicitly authorized for the dedicated Sandbox launcher. This narrow
exception supersedes older blanket receipt-printer-OFF guidance; merchant
payments remain Sandbox, Drive OFF. Owner explicitly selects “Tiket pemulihan + hasil foto”: enable both automatic
recovery receipt after PAID and approved photo strips in this dedicated Sandbox
profile. Drive remains OFF; ordinary/default profiles retain their existing
opt-ins. Reuse original one-batch photo transport and no-replay manifest guards.

One receipt per original PAID order, not per poll/rebuild/QR expiration. Print
only with current live ownership, bound capability and reserved original grant.
Never print pending/expired/unknown/review or an unproved reopened order. Existing
internal hash-at-rest and no raw ticket in logs/journals/previews remain. Render
in memory at native printer dots, reuse original ThermalPrinter routes and
ESC/POS encoder/settings. Add an in-memory bitmap entry to avoid saving secret
receipt images/spools. Durable SENDING before transport; interrupted/failed
submission is UNCERTAIN, never auto-reprinted on retry/restart. Submitted is
transport acknowledgment, not a paper sensor or fulfillment of the photo order.

Printed content: Meong/booth, Sandbox paid notice, amount and short order label,
original recovery QR, “Pembayaran sudah diterima. Simpan tiket ini sampai sesi
selesai. Jika aplikasi terputus, scan QR ini untuk melanjutkan pesanan yang sama.
Tidak perlu membayar ulang.” Include actual scan-button guidance, privacy and
24h-from-order-creation Sandbox validity. No merchant credentials/PIN/customer PII.

Then reuse existing photo prepare/allocation/STARTED acknowledgment into the
camera page; no automatic shutter or print of an unapproved photo. Reset old
payment wait idle time when admitted. Temporary minimize before any capture
intent must hide UI while retaining the original live checkout, not demand a
ticket that has not printed. Restart/allocated photos still require proof;
never relax ownership for old private media or invent a new paid entitlement.

Tests first: native receipt QR decode/layout at384/576, bitmap routing and no
disk secret, durable intent/crash/no replay, fresh/unknown/paid/reopened guards,
direct-camera flow at both portrait sizes, old idle/minimize before payment,
private-media pause holds, print failure and delayed worker retirement. Reuse
original HTTP/SQLite/capture fixtures. Focused staged push, final full/matching
CI and native views. Actual owner printer/paper/Midtrans acceptance pending.
No real provider/printer/customer files in cloud QA; no new branch/production/
default/merge/deployment/OPS. Preserve all existing records on rollback.

Reviewed AGENTS, protocol/index/checkpoint/handover/AR roadmap, native/customer
claim/BUG026 contracts, original printer/payment-slip/print-drive source and
Sandbox launch/checkout/photo/busy/privacy/capture fixtures. Do not inspect old
or alter unrelated dirty legacy checkout. Source and verification pending.

First isolated renderer/transport increment: 38 focused PASS,0.378s, zero fail/
error/skip. Five new native-dot/context/route methods, original printer/Windows
RAW/shared payment printer tests. No GUI mount or device activation yet; next
durable worker/native paid-to-camera + explicit photo-print mounting.
