# 9 November 2026 — commercial booth target confirmed

The owner explicitly confirms **Ubuntu on the mini PC** as the commercial
deployment target. Preserve Windows development/support and its existing
evidence. This supersedes generic Windows-booth assumptions in dated summaries;
Android remains outside the current scope. Ubuntu OS-key custody/startup/reboot
and device acceptance must be verified independently.

# 8 November 2026 — paid results automatically return after 30 seconds

Owner explicitly requires **30 seconds on the paid results screen, then automatic
return to the main Advertising page, with no additional finish button**.
This is independent of the original Recovery Ticket's 30 visible seconds/NEXT.
Returning hides private pixels and preserves the original order; public Ads
does not bypass worker isolation/ACK or imply completed delivery/refund.
[Implementation and acceptance boundary](qa/portrait-v2-sandbox/BUG046-RESULT-AUTO-RETURN.md).

# Meong Photobooth — product and technical decisions

## 1 November 2026 — NEWER owner-approved refund-first, lost proof, and operator-last-resort policy (NEW post-preview orders)

**Authority:** [RF-D01–RF-D26 full refund/lost-proof contract](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) · [full 42-area conversation/decision crosswalk](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) · [24 PP decisions, 11 original main flowcharts](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [112 proposed NOT_RUN QA cases](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md).

**Decisions approved by owner:**
1. To minimize human intervention, **refund-first** for an **independently verified PAID and irrecoverably failed merchant service** after bounded original recovery, paid obligation audit and **safe printer/Drive worker fence**. Future MVP preference is one original full-payment refund; physical partial-print uncertainty must be classified first rather than blindly refunded. Safe independently proven extra settled QRIS attempt (same logical order) may refund **only the excess payment**. Merchant QRIS/POS online refund API activation, eligible time window, refund_key semantics and real account support are **UNVERIFIED**, so no actual refund/API was authorized.
2. **Customer losing a genuinely offered CCP or Recovery Ticket is NOT automatically refunded merely because of that loss**. The owner intends that losing the original proof forfeits *self-service photo recovery*; the original user cannot demand an automatic money return solely for their misplaced token. Operator PIN, printed payment QR, order number, DEMO QR or verbal claim must **not** open old private photos. Keep financial history and legally reviewable support claims.
3. **Merchant failure is independent of proof loss.** If CCP or the original Recovery Ticket was never genuinely made visible/available due to Meong's fault, customer negligence cannot be presumed. Likewise, if the underlying paid photos or download/paper service is independently proven permanently unfulfilled, consider the valid refund/remedy path even if the customer also lost the proof. No blanket standard term "semua uang hangus dan tidak dapat di-refund dalam kondisi apa pun"; require legal review (Indonesia UU 8/1999 Pasal 18 and 19).
4. **Original Recovery Ticket is ALWAYS shown** to the rightful first verified-PAID live customer for **30 truly visible seconds + NEXT/LANJUT while the SAME ORIGINAL ticket is printed ONCE concurrently**, regardless of printer SUBMITTED/failed/UNCERTAIN. This display is **not** printer-failure-only fallback. No reissued token, no printer SENDING/UNCERTAIN auto-replay or old customer ticket on Advertising/reboot/B's visit.
5. Only independently verified PAID may be considered for refund. Original PENDING/UNKNOWN/404 uses same-order reconciliation/cancel, not refund; live original verified expiry may QR1→QR2→QR3 with frozen cart/no recapture; departed/cancelled customers cannot renew.
6. Use **separate durable refund states** and original refund intent/key, exact settled provider transaction, no duplicate provider POST on timeout, and truthful `REFUND_REQUESTED` versus `PROCESSING` versus `CONFIRMED`. No return to user-entered arbitrary bank/wallet, fake refund success, invented ETA or unsafe customer-media exposure.
7. Refund **does not** prove machine FREE or automatically clear unsafe printer/camera/Drive workers. Genuine auto-isolation still requires exact PREPARE/fence/local receipt/backend ACK; technician for unsafe lease, physical printer ambiguity or hardware. Security/finance reviewer for fraud, unverified provider amount, unavailable refund channel and wrong original payment. Returning CCP with busy booth is WAIT/DEFER, not operator.
8. **Every older decision retained according to scope:** capture/3+1 per template, one immutable multi-template/cart quote and pre-QRIS edit, original CCP pre-PAID, Drive 25 READY and post-PAID verified customer URL before paid strip, printed QRIS Payment Slip distinct from original ticket, Drive retention/private ownership, Meong Fly one-use/promo backend authority, GUI v2/Android/Windows targets, and AR-00..13/UAH nonnegotiable safety gates. Historical paid-before-camera source/recovery remains for `prepaid_legacy`; new PP and refund-first policies apply only to `post_preview`.

**Supersession:** Earlier unqualified `NO_AUTO_REFUND` rules remain accurate as historical/current legacy source behavior, but **are replaced narrowly** by a merchant-activated, verified, safely fenced refund-first *future design* on this post-preview branch. Earlier printer-success-no-ticket-overlay is also historical legacy only. Do not interpret either as authority to change current source or merchant configuration.

**Implementation:** DOCUMENTATION ONLY. New PP-001..112 **ALL NOT_RUN**, `PP-06R` refund stage planned after safe claim/fulfillment, Midtrans POS Refund API support NOT VERIFIED; no actual refund, source edit, cloud deletion, merchant activation, master or parent branch change.

---


**Post-preview design consistency review:** [K01–K20 reconciled, with remaining non-runtime calibration clearly marked](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-CONSISTENCY-AUDIT.md).

> **New-order design on `feature/post-preview-qris-checkout` (owner-approved 1 November 2026; NOT IMPLEMENTED).** Templates/copies -> 3 photos and max one retake **per template** -> all previews -> edit only before durable provider-create intent -> one frozen QRIS checkout + privately offered **pre-PAID Checkout Claim Proof** -> verified PAID -> original Recovery Ticket ALWAYS displayed 30s+NEXT WHILE the same ticket is printed once concurrently -> photo strips only with verified individual Drive URL; upload may remain pending. Encrypted credential escrow, adaptive inactivity, expiry-only QR1/2/3 for active original customer, distinct cancel/abandonment, PAID_UNCLAIMED/OWED and exact worker-fenced auto-isolation are approved; no unpaid photo printing/download, uncertain print replay, duplicate service or automatic refund.
>
> **Branch authority:** PP-00..07 is the planned implementation workstream here **only when separately authorized**, constrained by all AR-00..13/UAH payment, privacy, machine release, legacy prepaid and physical print safety requirements. Parent `feature/portrait-kiosk-v2-next` continues the original AR roadmap. Historical source/CI statements below retain their original dates/branches; they do not prove the new flow. **All 112 PP tests NOT_RUN; no source, actual provider/Drive, hardware or master changes in this documentation revision.** [Master decisions/11 corrected diagrams](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [security/state](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [112 QA cases](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) · [Codex handover](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-CODEX-HANDOVER.md).


## 1 November 2026 — NEWER owner correction: Recovery Ticket ALWAYS visible + concurrent original paper print (post-preview new orders)

**Owner explicitly changed the previous conditional screen fallback.** In the **new `feature/post-preview-qris-checkout` order version**, once independent Midtrans PAID and rightful live booth lease are verified:

1. **Always present the original Recovery Ticket QR and entire code on the customer-facing screen** for **30 actually visible seconds** with an explicit **LANJUT/NEXT** button; do this **even when the receipt printer is healthy, immediately acknowledges SUBMITTED and produces paper**. This is now the mandatory first paid-ticket screen, NOT a hardware-error fallback.
2. **At the same time**, initiate a single durable printer receipt intent and enqueue/dispatch **exactly one** physical ticket bearing that same original credential; the on-screen QR does not wait for printer status. Physically emitting thermal paper may complete later; one exclusive printer worker serializes ticket/photo-strip sends.
3. Keep screen and receipt journal **independent**. Receipt unavailable/FAILED/SENDING/UNCERTAIN does not suppress, recreate or reset the screen; it never authorizes automatic reprinting. The countdown begins on actual QR/code visibility, not when ticket created or printer I/O starts. NEXT/zero dismisses QR and full code exactly once without cancelling the already-sent single receipt.
4. This is **one authorized initial presentation** for the original live customer. PAID_UNCLAIMED without valid ownership, public Advertising, another user, restart and duplicate callbacks must not automatically reveal/print another customer's original ticket. A returning claimant must prove the original CCP/valid ticket and a free booth; a ticket already genuinely presented is not auto-redisplayed or reissued.
5. **New-order precedence:** this decision supersedes earlier 1 November 'only show onscreen on receipt failure' and 'no mandatory screen after SUBMITTED' instructions **for the post-preview branch only**. Historical paid-before-camera Sandbox/UAH/BUG-027 behavior and its prior CI evidence stay historically scoped unless separately authorized for migration.

**Status:** Owner-approved **documentation design**, **NOT IMPLEMENTED / NOT TESTED**; the 84 PP acceptance scenarios remain NOT_RUN, with PP-041/042/051/079/080 specifically requiring screen+print concurrency. No source code, printer transport, real payment, Drive/retention action, master or parent branch modified. [Updated master flow](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [ticket state/security](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [84 test cases](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md).

---

## 1 November 2026 — Owner approval: unattended handoff, automatic isolation and ticket responsibility (DESIGN ONLY)

**Canonical signed-off target:** [UNATTENDED-SESSION-HANDOFF-OWNER-APPROVED](qa/portrait-v2-sandbox/UNATTENDED-SESSION-HANDOFF-OWNER-APPROVED.md). The owner accepted **all** recommended P0.1–P0.6 stages, the exception policy and the dependency-ordered engineering plan, and specifically asked for **documentation only, no code change**. This records current owner intent, not implementation or new CI/device PASS.

**Decisions:** (1) original Recovery Ticket is attempted on the configured printer once after freshly verified PAID; when not configured, failing, timed out or UNCERTAIN, the **same QR and full ticket code** will be shown for 30 seconds with NEXT/automatic zero exit; no reprint or duplicate credential; (2) after a genuine paper/on-screen opportunity, **the customer is responsible for saving their ticket**; if it is lost or not saved, self-service reopening of a privacy-locked photo session is forfeited; an operator does **not** routinely recover private media without valid original proof; (3) loss of self-service access does **not** erase PAID/OWED, guarantee fulfillment or automatically refund; a separate redacted financial/support remedy may apply; (4) protected old visit -> wipe private data -> **Advertising**, not default SESI TERSIMPAN, with internal ADS_PROTECTED occupancy; (5) new Photo/Game click in ADS_PROTECTED triggers **safe machine-authorized auto-isolation** (PREPARE/fence -> exact local worker isolate -> backend ACK -> durable original archive -> verified free booth) and only then allows new payment, without an operator PIN for strictly safe cases; (6) unfinished PENDING/UNKNOWN or cancellation race requires the original-order provider evidence and safe terminal closure, not generic paid release, reset or a new order; (7) from Advertising, original ticket can claim active-locked or ACKED-archived sessions, but if another visitor is using the booth, **WAIT/DEFER**, never preempt them; (8) operator involvement is exceptional for genuine financial conflict, unsafe print/Drive/lease, data corruption, device/security faults or separately approved financial remedy.

**Precedence:** Supersedes prior target navigation into SESI TERSIMPAN on every lock and proposals for routine ticketless private-photo operator restoration. **Does not supersede** AR-00–AR-13 source invariants, BUG-027/BUG-028 tested live paid-camera behavior, provider evidence requirements, existing PIN-authenticated operator release, irreversible print safety, the 24-hour Sandbox ticket validity, photo retention, or AR-13 conditional production gates. Existing ticket fallback remains NOT IMPLEMENTED. Full flowcharts, 50 new required UAH test cases, role matrix, state transition rules and phased Codex work are in the canonical contract. No code, tests, credentials, production or master changed.

## 1 November — 30-second on-screen Recovery Ticket if printer does not respond (design only)

The owner requests a new **conditional fallback** after fresh PAID: if the one
recovery-receipt printer submission is unavailable, fails or produces no
acknowledgment, show the **same original Recovery Ticket QR and complete code**
on the kiosk screen for **30 seconds with a visible countdown and a NEXT/LANJUT
button**. The button advances immediately; at zero the display closes and
the system advances automatically. Both exits must wait for the same original
local photo allocation/STARTED readiness before opening the camera; no new
payment, grant, ticket, print attempt, automatic shutter or privacy bypass.
An acknowledged receipt retains the direct-to-camera happy path.

This supersedes the prior **no on-screen ticket even on printer failure**
interpretation, but **not** the no-mandatory-ticket-screen happy path or the
one-send/UNCERTAIN/no-reprint rule. Sensitive ticket pixels/code must be
cleared after NEXT, expiry or privacy lock; restart and previously private
sessions still require original proof. **DOCUMENTATION ONLY: not implemented or
tested; do not import old BUG-027 PASS as fallback acceptance.**
[Authoritative contract and acceptance plan](qa/portrait-v2-sandbox/RECOVERY-TICKET-ONSCREEN-FALLBACK.md).


## 31 October — dedicated Sandbox printed recovery receipt and approved photos

Latest owner correction recorded in BUG-027 selects both receipt and photo-strip
printing in this test profile: receipt once after verified PAID, direct camera,
manual SIAP/countdown/review, approved strips automatically. Drive/production
remain OFF. This narrow profile supersedes older blanket Sandbox printer-OFF
and mandatory on-screen ticket-save guidance; ordinary profiles keep opt-ins.
No uncertainty replay, false paper fulfillment, automatic printing-profile
crash restart, commercial release or privacy/financial bypass follows.
[Current contract and source verification](qa/portrait-v2-sandbox/BUG027-PAID-TO-PHOTO.md).

## Owner-approved GUI v2 Operator Settings / Emulate Ticket — 29 October 2026 (future implementation)

The owner approved **all the recorded Settings/QR/audio/demo-ticket recommendations and their subsequent corrections**, requested exhaustive English Codex documentation, and explicitly reaffirmed **AR-00 → AR-13 as highest development priority**. No new Settings source has been implemented under this documentation request. Read the complete [operator Settings decision register](qa/portrait-v2-operator-settings/DECISION-REGISTER.md) with **50 numbered decisions and supersession table**, [master requirements](qa/portrait-v2-operator-settings/README.md), [post-AR implementation roadmap](qa/portrait-v2-operator-settings/IMPLEMENTATION-ROADMAP.md), [QA matrix](qa/portrait-v2-operator-settings/ACCEPTANCE-MATRIX.md) and [Codex handover](qa/portrait-v2-operator-settings/CODEX-HANDOVER.md).

**Final visible Settings tabs:** **Device Health / Audio Settings / Emulate Ticket**; “Ticket Master” was explicitly renamed **Emulate Ticket**. The existing secret F12/header hold must **only** open static Operator QR Login from first-page **Advertising AND SAFE_IDLE**. It no longer opens full Device Health/Settings directly; retain **a separate protected AR-09 Recovery PIN/exception path**. Operator QR is private booth-specific high-entropy static/offline/rotatable for development; future dynamic short-lived QR is **only an operational-phase proposal**. Authenticated Settings logs out on close/minimize/three-minute idle and returns to Advertising; OS maintenance fallback handles broken camera. Use existing one-owner camera, read-only Health and Audio Manager, preserve video/game audio lifecycle; Audio controls are Master, Music, Button SFX, Other SFX, Mute and Test Sound, persisted per booth.

**Emulate Ticket** uses **reusable static DEMO QR** (Merchant Promo and Meong Fly) during development, with eligible/ineligible/invalid and valid/actually-used/invalid test presets, preview/80-mm thermal print, durable print uncertainty and redacted history. Static QR may be used again in a **new test visit**, but not for two rewards/game attempts in one visit (including restart). Never fake an Already Used QR, bypass the old one-use code ledger, stack Merchant Promo + Meong Fly discounts initially, accept DEMO in production or enable the dedicated Midtrans Sandbox printer/Drive. The separate QRIS Payment Slip checkout feature remains planned and does not belong to Emulate Ticket. Customer Recovery Ticket stays unique/private per order. AR-00–13 financial/privacy/device/release gates are **not superseded**. Only the documentation was authorized in this turn; future OPS code follows a separately approved scope, documentation-first and micro-pushed commits.


## Owner Autonomous Recovery continuation — 28 October 2026

The owner explicitly requests continued implementation of AR-00 through AR-13
in dependency order on existing feature/portrait-kiosk-v2-next, preserving payment
integrity, privacy and existing functionality. Small independently tested commits
and immediate pushes/remote verification are required, with durable checkpoints.
This supersedes planning-only scope for safe staged source work. It does not
approve a new branch, master merge, production payments, real refunds or external
deployment; provider/device/security and final release gates remain separate.

## Owner QRIS logo request — 28 October 2026

The owner asks for Meong centered in the v2 Sandbox payment QR like the Drive
download QR, then explicitly reiterates reusing the existing implementation.
Reuse its renderer and approved artwork, without changing the encoded provider
payload or payment state. Keep the original image when equivalence/readability
cannot be verified. [Presentation contract and evidence](qa/portrait-v2-sandbox/QR-LOGO.md).

## Owner saved Sandbox credentials request — 28 October 2026

The owner explicitly requests persisting Merchant ID and Server Key locally,
for example beside Drive settings in ignored `photobooth/local_settings.py`.
This supersedes the earlier prompt/environment-only source restriction. Reuse
the ignored file with separate Sandbox-specific fields; no private values are
written/published by this source change. Preserve backend-only credential
forwarding, fixed Sandbox transport and existing payment/Drive state.
[Implementation and source precedence](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).

## Latest owner delivery instruction — 27 October 2026

Owner authorizes implementation of holding old retries, reserves and content
while customer uploads run, FIFO across waiting sessions and bounded failure
release. A subsequent explicit correction requests the real download QR before
upload success, superseding the former UPLOAD_COMPLETE screen-QR rule. Every
customer keeps a distinct immutable folder and a durable local-file mapping.
The UI suggests checking again in 30 minutes; no unverified upload deadline is
guaranteed. [Contract and evidence](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).

Owner accepts the 27 October recommendation to isolate old failed delivery
retries and add specific safe bind diagnostics. This scope preserves claims,
folder identity and retention; no automatic repair/deletion or batch-upload
protocol is authorized. [Retry continuation](qa/drive-delivery-performance/RETRY.md).

## Owner delivery-performance continuation — 27 October 2026

Owner approves same-branch investigation/implementation/tests/documentation and
staged pushes for Google Drive latency and v2 responsiveness. Subsequently asks
to inspect v1's faster link generation, with no blind port. V1 publishes a real
folder URL before upload completion; v2 keeps the stricter UPLOAD_COMPLETE screen
QR contract, while the strip may use an earlier verified real folder. Preserve
operator-disabled printing, original clocks/claims/checksums/durable queues and
numbered cloud layout. No live Apps Script deployment/cloud deletion is authorized.
[Implementation, limits, comparison and update guide](qa/drive-delivery-performance/README.md).

## Owner working rule and platform — 27 October 2026

Documentation review must be thorough/comprehensive/careful before code changes;
documentation updates follow code. This is the primary rule, persisted in
AGENTS, protocol and continuation prompt. Development runs on Windows; deployment
will use an Ubuntu mini PC. Preserve Windows support and provide target-specific
Ubuntu startup guidance without claiming actual Ubuntu device acceptance.
The next roadmap request continues FEAT-009 with a read-only recovery gate,
per-checkout launch ownership and generated Ubuntu user service. No automatic
restart, replay, service installation or production deployment follows.

## Owner correction — customer Drive folders (26 October 2026)

The owner explicitly clarifies PB001/Photo/00000001/{raw,bw,color}; internal transaction IDs are not customer Drive folder names. This supersedes the previous cloud tree. Preserve local state, QR folder IDs and no print replay.


Updated **26 October 2026**. Decisions establish product direction and scope;
[current status](FEATURE_STATUS.md) and [test ledger](test_checklist.md) establish
implementation/evidence. Preserve historical IDs and separate later authorization
from the original decision. A design decision alone does not authorize new code.

## DEC-023 — GUI v2 development focus and intended primary branch

The owner directs continued development on **`feature/portrait-kiosk-v2-next`**,
with reference to working features on other branches, and intends GUI v2 to
become the primary branch. GitHub default remains `master`; `main.py` remains v1.
No new branch/restart/default change/rename/merge/release/deployment follows from
this direction. [Reference audit](gui-v2-branch-audit.md) · [transition plan](gui-v2-promotion-plan.md).

The owner explicitly approved P3, P4 DEMO/MOCK and then P4b Sandbox/P5 with manual
tests at the end. On 25 October the owner authorized safe source continuation
while laptop checks wait, reusing the actual v1 implementation. The bounded
read-only Device Health/local report increment is now in source. Selection,
production, trusted merchant promotion and repository operations stay separate.
[Operator scope/proof](qa/portrait-v2-operator-health/README.md).

Reuse working UI/controllers/renderers/assets as well as logic; refresh reference
SHA and record concrete adapter exceptions. Avoid redundant successful GUI CI for
documentation. This documentation request authorizes reconciliation in English;
it adds no new application feature approval. [AGENTS.md](../AGENTS.md).

## Product decisions

**Owner storage target, 26 October:** ignore the entire `old` archive without
inspection/change. Requested new data layout is `Photobooth/PB001...PB00X`,
booth-specific assets, at least 25 empty transaction reserves and
`PB001/Photo/00000001/{raw,bw,color}` in Drive (26 October correction). Root `Global_Advertisement` and `Global_Template` are
shared sources with complete offline copies in every booth. The
[audit/target contract](photobooth-storage-layout.md) records current gaps and
reuse; it does not claim implementation or an actual Drive cutover. The owner
selected continued local photo/print if Drive/25 reserves are unavailable, with
upload and QR deferred until online; this requires explicit deferred-binding
state, not silently uploading previously local-only visits. Asset-priority
recommendations are labelled separately.

The owner explicitly links this target to **FEAT-004 ads + BUG-009**. Treat
foldering, global/local caches and photo-retention integration as coordinated
work. Preserve separate source/device/cloud evidence and keep BUG-009 OPEN
until its real deletion gate is verified; do not call the linkage implemented.

**Owner BUG-009 continuation, 26 October:** resume bounded photo-retention
remediation; setup and redeployment have not been confirmed. This supersedes
the earlier deferral for this bug, without starting FEAT-004 advertising sync.
Reuse v1 setup/cleanup/client/configuration, preserve immutable deadlines and
v2 upload holds. Prepare tested source/diagnostics and a concrete activation
guide; installed-account changes/deletion evidence remain separate from source
verification. [Current repair](qa/bug-009-retention/README.md).

**Owner print/Drive priority, 25 October:** after BUG-018's 4/4 monitoring retest,
the owner redirected the next development to these two features only and chose
automatic print after approving photos (v1 behavior), with Drive in background.
Use existing clients/configuration/queues/QR, explicit ordinary-launcher opt-ins,
durable one-batch/uncertainty guards and verified delivery. Watchdog is postponed;
no production/provider/scanner, cloud deletion/deployment or repository operation
follows. [Scope and acceptance](qa/portrait-v2-print-drive/README.md).

| ID | Owner-confirmed decision | Current interpretation / boundary |
| --- | --- | --- |
| DEC-001 | Earlier development targeted `feature/kivy-gui` | Historical; v1 was subsequently released. Continue v2 on its existing branch under DEC-020/023 |
| DEC-002 | Branded colorful Meong Kivy GUI, final cat-camera identity and twelve approved 80 mm designs | Preserve artwork and readable QR; current v2 header/typography follows DEC-022 and later visual corrections |
| DEC-003 | Advertising → acknowledged tutorial once per active visit → template gallery | Applies to direct entry and either game result if unseen; safe idle resets transient state, never consumed game attempts |
| DEC-004 | Image/video advertising with a nearby face held for five seconds inviting entry | Manual Start retained; default offer timeout 15s, cooldown 45s. Presence detection does not recognize identity |
| DEC-005 | Video owns its audio; still ads use GUI BGM; tutorial/gallery/photo use a continuous GUI loop, game a distinct loop; one cue/enabled action | One v2 owner, separate from v1. Muted payment-ad policy applies to v1's placement; native v2 Sandbox has no payment-ad panel |
| DEC-006 | Payment QRIS differs from photo-folder/download QR; separate local MOCK and merchant Sandbox clearly | Backend/client/journal Sandbox source integrated; no production activation or acceptance inferred from QR/GUI clicks |
| DEC-007 | V1 may offer a QR slip without hiding the main QR or extending validity/confirming payment | V1/shared-slip feature, not ported native v2 Sandbox UI. Dedicated merchant trial forces printer/Drive off |
| DEC-008 | Thermal printing supports configured LAN/Wi-Fi/Windows RAW USB and Floyd–Steinberg/Bayer/threshold modes | Existing printer baseline retained; owner reports quality/QR-slip/copy counts passed (BUG-004/003/011), with formal source/device/scan limits preserved. Newer lab UI is separate |
| DEC-009 | Rp5,000 per selected design/three-photo session plus Rp5,000 per identical paper copy | Separate base per design; N image+cut streams in one RAW batch. Zero deselects, 1–9 is current UI range. Digital-only/final commercial maximum policy undecided; Sandbox recomputes server price |
| DEC-010 | Design-only FEAT-002A merchant-style receipt scan/discount at checkout | Replace only payment ads with live preview, preserve QR/order; success closes scanner, failure allows retry. Example Rp50,000 food order waives one Rp5,000 base fee, never print fees; illustrative campaign, not game reward or implemented v2 path |
| DEC-011 | Real FEAT-002B POS integration waits for a partner and receipt/API evidence | Prefer existing POS receipt; detected code is not purchase/eligibility proof. Require one-use/replay-resistant verification |
| DEC-012 | Every implemented live preview is horizontally mirrored; owner extends v2 output on 26 October | V2 review and photo areas in the shared result/printed/digital strip now mirror too. Preserve full-resolution JPEG originals, detector/decoder inputs, template/text/logo/QR orientation. V1 defaults unchanged; earlier 18 October acceptance remains historical |
| DEC-013 | Future ads sync from dedicated Meong Drive into per-machine local media, typically weekly | Proposed FEAT-004, offline/atomic/fallback-safe; not a shipped central ad service |
| DEC-014 | Real merchant ordering uses a compatible customer-facing partner service; do not maintain a full Meong production POS by default | FEAT-005A standalone local DEMO ordering proposal passes a single-use promo on the same kiosk without scanning; external receipts retain their independent path. Ordering not implemented in v2 |
| DEC-015 | Configurable visual themes share one codebase | FEAT-006 proposal; admin-controlled per-machine default remains a recommendation pending final choice |
| DEC-016 | Retention target: 15 days local, 30 days Drive | Local bytes may expire even after failed upload. Cloud schedule/deletion unverified; assess delivery notice/promises before monetized digital delivery |
| DEC-017 | Coordinate BUG-009 cloud retention remediation with future FEAT-004 ads sync | Separate scopes/evidence for photo deletion and ad sync. Existing Apps Script functions may need setup/deployment rather than replacement; no deployment/deletion authorized by docs |
| DEC-018 | Earlier payment deferral has later scoped overrides | P4b Sandbox/P5 explicitly approved 24 October and source delivered; production, paid reprints, real POS/promotion settlement remain separate |
| DEC-019 | Accept FEAT-001 DEMO pricing and BUG-011 physical copy-count owner test; monitor after RAW fixes | Owner's successive confirmations preserved in [QA](qa/FEAT-001-BUG-011-acceptance.md). Focused 15/15 mock CI and paper report are separate; exact device SHA/count matrix missing. Earlier CI failure later repaired; not formally CLOSED or all-device certified |
| DEC-020 | Owner approved old-master backup, tested v1 merge and immutable `v1.0.0` source release on 19 October | Completed source operation; [release notes](releases/v1.0.0.md). Not approval for future v2 merge or hardware/production certification |

DEC-021 is not assigned in this branch's decision log; do not invent or renumber
historical entries. The branch-local FEAT-021 collision is a separate issue.

## DEC-003 addendum — tutorial and visit lifetime

**Owner refinement, 26 October 2026:** remove the separate idle CARA PAKAI
button. MULAI FOTO and invitation AYO FOTO already open the required tutorial
for a fresh visit; keep acknowledgement, cancellation and postgame routing.
This simplifies entry without bypassing or duplicating the existing tutorial gate.
[Scope, checks and rollback](qa/portrait-v2-photo-entry/README.md).

Acknowledgement, not merely rendering the tutorial, sets `tutorial_seen`.
Direct entry and win/lose both route to the original twelve-template picker,
showing the tutorial only if unseen. The game route is intro → manual DEMO input
→ one irreversible attempt → result → tutorial if needed → gallery, without replay
or direct payment jump. Local MOCK validates its reward; Sandbox requires server
verification/grant/ACK and has no trusted game-promo contract.

Reset transient tutorial/cart/reward UI only on safe visit completion/abandonment.
Never reset consumed attempts, pending/unknown/paid orders or uncertain print
state using an idle timer. The original tutorial-gate branch remains historical
design evidence; current VisitFlow integration has since been implemented.

## DEC-022 — approved portrait direction and corrected navigation

Owner selected Pixel Arcade Space / original Meong Fly visuals for a new
portrait-first 10.1-inch UI and independent audio lifecycle. This was a UI rebuild,
not permission to replace working camera/photo/print/templates/Drive services.
[Main artboard](assets/portrait-v2/meong-main-flow-approved.webp) and
[revised game board](assets/portrait-v2/meong-fly-revised-approved.webp) retain
provenance; explicit flow/price corrections override illustrative arrows and text.

Advertising/invitation share one media surface and both entry paths. The game has
its own intro before input. One receipt/code means one consumed attempt; no MAIN
LAGI after either result. Win reward is Rp2,500 per order in local/MOCK simulation;
a future provider promotion needs backend authority. Loss has no reward. Original
80×240 mm strips retain three photos plus one download QR, separate from QRIS.

Later owner typography preference supersedes bitmap main-app captions: use native
readable Roboto without mandatory icons, original game frames, larger animated
Meong and strip-focused gallery. [Visual specification](portrait-kiosk-v2-visual-spec.md).
Current source includes photo workflow, original DEMO game, MOCK/Sandbox and
read-only health/report. [Status](FEATURE_STATUS.md) records current proof;
P0–P2 design-only/no-camera statements apply only to their original snapshots.

## Business/software direction

| ID | Decision | Boundary |
| --- | --- | --- |
| BIZ-001 | Sell complete hardware as well as Meong-operated, rental/managed and contracted revenue-share arrangements | Separate hardware ownership/margin, photo income, service/warranty, operator duties and platform revenue |
| BIZ-002 | Every sold unit has a software tier: Free (Rp0 recurring), Business or Enterprise | Free is valid licensing, not a requirement to pay a subscription; entitlement implementation remains future scope |
| BIZ-003 | Free permits commercial core photo/capture/print operation and charging end customers | No Free revenue cap or disabling core capture/print because tier is unpaid; production gateway remains a separate undelivered capability |
| BIZ-004 | Meong controls all Free ad content | Central per-machine delivery and enforcement not implemented; ordinary operators do not replace/remove Meong inventory under this model |
| BIZ-005 | Business/Enterprise manage their own ads while retaining reserved Meong slots | Reserved share/frequency TBD, not illustrative 20%/10%; disclose terms and venue/competitor exclusions. Enforcement not implemented |
| BIZ-006 | Subsidy applies only to actually redeemed eligible photo discounts | Meong-operated booth may reimburse Meong; sold booth ordinarily reimburses the operator bearing the waived fee, with separate contracted platform fees. Contract controls ownership |
| BIZ-007 | Other monetization ideas are parked for evaluation | Premium content/events/analytics/support/warranty/white-label/ad-network candidates are not priced or approved implementations |

## Open policies and evidence

Graceful paid-tier downgrade to commercially usable Free without interrupting
orders is recommended, not finalized. Paid entitlements/prices/periods, licensing,
Meong slot quotas, venue rights, campaign eligibility/expiry/refunds/stacking,
merchant-of-record/settlement/fees, digital-only purchases, commercial print
limits, warranty/SLA and partner ordering availability remain open. Mixed-template
calculation already exists under DEC-009; future commercial revisions need approval.

BUG-009 remains OPEN. BUG-012/013/014/015/016/017 retain owner-reported monitoring
within their metadata limits; v1 BUG-001/007 are not closed by v2 audio.
Preflight `0dc6555` does not certify new Windows/merchant/paper/Drive/privacy
acceptance. Public webhook deployment, trusted QRIS game promotion, production,
POS/scanning, merge and release are separate scopes, not hidden prerequisites
for a local simulator trial.

[Protocol](DEVELOPMENT_PROTOCOL.md) · [current features](FEATURE_STATUS.md) ·
[backlog](next_step.md) · [handover](DEVELOPMENT_HANDOVER.md) · [changelog](CHANGELOG.md).
