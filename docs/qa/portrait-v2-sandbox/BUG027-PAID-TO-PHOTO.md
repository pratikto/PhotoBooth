# BUG-027 — printed recovery receipt, then direct camera


## Owner follow-up — 30-second ticket fallback on printer non-response (future change)

New owner request: if the existing one-and-only recovery-receipt submission
returns unavailable/error or does not respond by the supported printer deadline
(including UNCERTAIN), show the **original paid-order Recovery Ticket QR and full
code on screen for 30 seconds**, with a visible countdown and **NEXT/LANJUT**.
NEXT skips the remaining display interval; a zero countdown advances
automatically. The ordinary acknowledged-print path still goes directly to
camera without an extra screen. Both fallback exits must preserve the original
PAID/grant/allocation/STARTED readiness gates and never resend the receipt,
mint a substitute ticket, bill again, capture automatically or display old
private tickets after restart. QR/plaintext must disappear on navigation/
privacy lock. See the [full design-only specification and test matrix]
(RECOVERY-TICKET-ONSCREEN-FALLBACK.md).

**STATUS: APPROVED REQUIREMENT, NOT IMPLEMENTED / NOT TESTED.** All BUG-027
source, full/CI and owner-laptop records below predate this request and remain
historical evidence only for the existing printed-receipt direct-camera flow.
No printer, payment or GUI source was changed by this documentation addition.


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
application-owned receipt images/spools (the OS printer spool is part of
the authorized print transport). Durable SENDING before transport; interrupted/failed
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

Mounted stage2: integration111 PASS,78.114s; final focused39 PASS,21.703s, zero
fail/error/skip. First failed fixture/context assertions corrected and preserved
in the continuation checkpoint. Both printing switches now explicitly active
only in the dedicated Sandbox GUI; no extra confirmation/ticket screen. Full/
CI/native previews next; actual paper/device/provider still NOT_RUN.

CI41215406163 Windows: one stale crash-fixture expectation FAIL; runtime refuses
restart for printing as required. Reproduced locally5run/oneFAIL, fixed fixture
selects transport-off and adds explicit printing-profile denial. Corrected6PASS,
0.096s; application source unchanged4c74ece. Superseded local full stopped; final
corrected-source full/CI remain pending, no false PASS.

## 31 October — BUG-027 laptop guide synchronized / browser verified

Remote/test source e05a3581963c2fd45e87566672684369598ac2d2, functional
4c74ececb69a84a64a9619fd0d3980e5bdea6fc6. Current CI41215811123 all three jobs
SUCCESS, exact e05a358. Application/tests/tools/workflow unchanged by this
increment. Final full at e05a358 is now **1280 run/1276 PASS/0 FAIL/0 ERROR/
4 optional SKIP**,455.632s. Report work/bug027-final-full.txt, console companion;
raw synthetic reports stay private. Next complete native capture/receipt
in-memory verification and aggregate final evidence; no full rerun for docs.

Corrected preparation/root launch instructions/exported mode to receipt+approved
photo printing, Drive OFF; paper ticket scan and first physical strip verdicts
are explicit. Nine groups/44 steps remain. New form namespace starts NOT_RUN
and leaves old printer-OFF data intact rather than importing old PASS results.
Chromium/Playwright10 meaningful browser scenarios PASS, zero page errors,
800/452/360 widths, mode/export/persistence/clipboard/TXT/reset/storage denial.
Managed browser file:// navigation blocked (not PASS); identical HTML checked
via temporary loopback-only preview. Actual laptop offline-file/paper/provider
acceptance still NOT_RUN. Scope and old failures remain in BUG027 contract.
[Guide evidence](evidence/bug027-guide-verification.json).

Whole UX-07 NOT_RUN; matrix59/0/9/1; AR-13 conditional/audit IN_PROGRESS. PAY-22/
WEB gates, real Windows/Ubuntu/paper/phone/Drive/retention/support/release and OPS
remain separate. No production/provider/physical printer/Drive/delete/deploy/
new branch/master/default action. Private work/ and earlier superseded docs
stash stay local-only; no unpublished application patch. Push this safe docs
increment immediately, verify remote, then continue final verification.

## 31 October — BUG-027 final regression, native evidence and owner handoff

Tested GitHub source **e05a3581963c2fd45e87566672684369598ac2d2**, functional **4c74ececb69a84a64a9619fd0d3980e5bdea6fc6**;
first verified guide micro-push **e71aa1923f9df2f9d4fd4e58709c360f888db7fd**. No application/test/tool/
workflow changes in this continuation. Final full **1280 run/1276 PASS/0 FAIL/
0 ERROR/4 optional SKIP**,455.632s, process exit0. Python3.12.14/Kivy2.3.1/
ffpyplayer4.5.3, Linux softwareGL/dummy audio, GUI/audio opt-ins. Skips: three
native palm-assets cases and one native-video opt-in, never counted PASS.

**CI 41215811123 all three jobs SUCCESS**, exact e05a358, verified actual job
metadata/logs: 12 receipt methods and 6 crash-policy methods individually PASS
Windows/Linux; 7 paid-camera methods individually PASS Linux within recovery 521.
Windows ledger 208 PASS, Linux recovery 521 PASS; separate native 121/120 PASS/
one optional palm SKIP. Source 4c74ece CI 41215406163 one stale crash-fixture FAIL
retained; runtime correctly denies printing profile restart. Corrected test-only
source e05a358 preserves that guard. Superseded 4c full has no final PASS.

Eight actual App.run synthetic screens reviewed at 800x1280 and 452x900: one
receipt submission then direct camera; approved strip once with truthful
SUBMITTED; private claim after pause; readable unknown-receipt warning without
resend. Original HTTP/controller/photo/printer choreography used, injected sender
only. Both native-dot 384/576 receipt QR payloads match original public test
context in memory with safe ink margins; no receipt bitmap/token exported.
Guide/form 9 groups/44 steps match exactly. Chromium 10 browser scenarios PASS,
zero page errors; new namespace prevents old printer-OFF passes being imported.
Managed browser blocked file:// (not PASS); identical HTML verified over local
preview; actual offline-file laptop use still manual. One scratch import-path
error corrected without application change, not a runtime regression.
[Exact source/results/CI/hashes/screens/limits](evidence/bug027-final-verification.json).

Approved current test profile: verified Sandbox PAID → one recovery receipt →
direct camera → deliberate SIAP/countdown/review/retake → approved photo-strip
print. Drive OFF, no production. No receipt/strip automatic replay on restore;
SENDING/UNCERTAIN retains inspection hold, SUBMITTED is not proof of paper or
satisfied OWED. Printing profile cannot reserve automatic crash restart.
Older blanket Sandbox printer-OFF/mandatory-ticket-screen guidance is historical.

**Next:** Owner Windows laptop + configured printer/paper + official Midtrans simulator retest using the updated nine-group/44-step guide/form. Confirm exactly one recovery receipt after verified PAID, direct camera with deliberate SIAP, one approved strip batch with original copy count, no reprint/recharge on privacy/restart. Record exact laptop SHA and actual PASS/FAIL/NOT_RUN. Do not repeat completed synthetic work or enable production/Drive/OPS. Genuine device/provider failures get a new isolated regression before any source fix.
Whole UX-07 NOT_RUN;69 IDs remain 59 PASS/0 FAIL/9 BLOCKED/1 NOT_RUN. AR-13
conditional/audit IN_PROGRESS. Stronger purchased-print prepayment/paper and
commercial/operating acceptance are not closed by this Sandbox mount. All safe
progress is in the same branch; this containing docs/artifact publication is the
final safe checkpoint (resolve containing SHA through Git/remote). Only private
synthetic work/ and prior superseded docs stash stay local; no unpublished
application patch. No new branch/master/default/deploy/production/Drive/deletion/
OPS or real provider/physical printer operation. Rollback scoped reviewed inverse
code only; retain all financial, receipt/print, claim, audit and media records.
