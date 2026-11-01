# Post-preview QRIS implementation checkpoint

## 2 November 2026 — PP-05.d2d native original paid delivery page (CI pending)

The **existing native checkout fixture**, not the production or legacy GUI, now continues automatically from the verified PAID ticket NEXT into the original paid folder/strip preparation worker. It then displays a native purchased-output result with the **actual verified customer folder URL** QR, separately labeled Drive upload progress (never assumes complete), paid print states and a one-time guarded `CETAK FOTO YANG SUDAH DIBAYAR` button. A transparent `CEK STATUS UPLOAD` checks only the same transaction. Bad Drive binding leaves PAID/OWED on the hold page with a `COBA SIAPKAN DELIVERY` retry; no duplicate provider charge or strip send. The original 30-second ticket and shared printer lane are unchanged. Native tests cover 800x1280 and 452x900 full original paid-ticket→Drive QR→print and offline Drive hold.

**Important:** these new visual tests are synthetic/mocked. This is not a verified physical printer receipt or real Midtrans/Google Drive operation; safe closure/recovery PP-06 and PP-06R/PP-07 are still required before customer-ready UAT.


## 2 November 2026 — PP-05.d2c single-flight checkout-to-delivery service wiring (CI pending)

**Integrated original synthetic purchase:** `PrivateCheckoutService` now has a separately injected paid-delivery owner; only exact same original SQLite entitlement/Drive worker and **the same receipt printer lane** may attach before checkout admission. When customer genuinely saw/dismissed the original Recovery Ticket, `prepare_paid_delivery` binds the original verified Drive transaction and stages exactly the already approved JPEGs/QR strips; `paid_delivery_status` polls worker evidence and `paid_print_next` submits the first remaining original PREPARED paid strip **at most once**. The source stays in `paid_delivery` with PAID/OWED, unresolved paper and uploaded files honestly reported. No parallel printer owner, alternative transaction or auto-reprint is added. Entire route still guarded as fixture/mock-only; no real Sandbox/UAT until recovery and safe release are implemented.

`CheckoutFixture.enable_paid_delivery` is a deliberately no-network synthetic binder and print adapter. Four new `test_post_preview_checkout_delivery` software scenarios verify PAID->ticket->original Drive QR->single batch print without second provider charge, no skipped ticket, fail-closed absent Drive, and no replacement lane. **CI pending**; actual physical POS80, Apps Script, Midtrans sandbox, auto-isolation and full PP-001–112 acceptance still not run.


## 2 November 2026 — PP-05.d2b original upload worker and owed-status monitor (CI pending)

Added a non-public, mock-only `OriginalPaidDeliveryMonitor` which binds the existing post-preview JPEG/verified-folder/QR strip pipeline to the original `BoothDriveWorker` serialized cloud uploader. It can queue a named original transaction only after paid assets and print intents are durably prepared. If no uploader is configured it reports NOT_CONFIGURED, not success. Its status monitor rejects foreign folder/service IDs, changed original print SHA, missing/corrupt local files, forged remote MD5/file ID or mismatched Drive metadata. Only ALL independently VERIFIED uploads with retained Drive retention evidence can advance `pp_paid_services.drive_state` to UPLOADED; **PAID/OWED, paper evidence and privacy fences are preserved**. Five offline tests cover no uploader, complete-only proof, invalid MD5, mismatched folder/strip, idempotent polling. Existing `BoothDriveWorker` is the actual adapter for future authorized Drive deployment; offline fixtures do not call real Google Drive.

This is not a live merchant approval or full safe machine release. PP-06 original proof/auto-isolation, PP-06R refunds and PP-07 physical UAT remain; all PP-001–112 full-case PASS are still withheld until integrated end-to-end tests.


## 2 November 2026 — PP-05.d2a paid Drive completion status (CI pending)

**Bug fixed in original upload status aggregation:** `POST_PREVIEW_PAID` manifests in `READY_FOR_PAID_DELIVERY` may now reach `UPLOAD_COMPLETE` once ALL individual files are independently VERIFIED and the paid media import, exact Drive binding and photo layout evidence are present. The original completed legacy transaction rule is unchanged. Both the Drive worker's `_refresh_upload_status` and the transaction writer's same-revision merge use the identical strictly scoped rule so an app/controller save cannot silently revert verified customer delivery. Any single PENDING/UPLOAD_RETRY/ACTION_REQUIRED file or incomplete original paid gates still prevent completion. Five regression cases added in `test_post_preview_paid_upload_status`.

This enables accurate eventual paid Drive status; it does **not** prove paper exited, grant photo/customer ownership, close PAID/OWED, enable live Midtrans, or authorize merchant refund. The exact containing-source CI is PENDING; full 112 acceptance cases still NOT_RUN.


## 1 November 2026 — PP-05.d1 original purchased copy batching (new; CI pending)

**Original PAID print dispatch is prepared as an isolated mock-only component**, not a customer/Sandbox printer activation. `OriginalPaidPrintDispatcher` validates the paid entitlement, original ticket genuinely displayed/dismissed, receipt no longer SENDING, individual Drive URL and saved 640×1920 output SHA **before** persisting the single original job SENDING. It requires the same external printer lane as the original ticket, then uses the existing calibrated `ThermalPrinter.print_image(path,copies=N)` so purchased duplicate copies form one complete RAW document. Only transport SUBMITTED is recorded on success, UNCERTAIN on any ambiguous failure, NOT_SENT when unavailable; no automatic replay, no false claim of physical paper, PAID/OWED preserved. The print order number is read from the exact persisted paid manifest, **not inferred by sorting template IDs**.

New five test scenarios in `test_post_preview_paid_print` test original ticket gate, one-copy-batched submission, UNCERTAIN no-replay, no device and corrupt bitmap refusal, including callback mock only. This is PP-05.d1 staging and not physical customer UAT, genuine paper evidence, actual printer connection or service completion. CI pending; all PP-001..112 remain NOT_RUN. Next PP-05.d2 paid Drive worker/remaining obligation integration, PP-06 original claim + machine-fenced isolation, PP-06R merchant-gated refund, PP-07 actual owner device acceptance.


## 1 November 2026 — PP-05.c3b after-publish manifest correction (new; CI pending)

CI run `41320578133`: native desktop SUCCESS, Linux **383 tests / 3 ERROR**, Windows cancelled. All three new paid strip cases reached the original successful output compositor but failed recording `paid_strip_bindings` because original `publish_output` reloads `tx.manifest` from durable storage, discarding the empty map just initialized before output. The correction uses `setdefault` **after** the trusted publish/record step so a resumed original manifest has an immutable per-design binding. No photo/QR hash guard, printing, Drive ACL or payment authorization has been relaxed. These tests/real external provider gates remain NOT_RUN for full PP acceptance until rerun succeeds.


## 1 November 2026 — PP-05.c3b verified URL paid strip composition (new; CI pending)

Use the byte-validated original paid media import and **one original authenticated, verified customer Drive URL** to compose 640×1920 purchased strips, one per selected design with its own frozen copy count. `OriginalPaidStripPreparer` records the immutable paid source-photo/retake, URL and original entitlement binding and inserts one durable `pp_paid_strip_jobs` PREPARED intent per design. It reuses the existing `publish_output` and `record_output` journal, recovers only exact STAGED outputs and **does not replay an existing or uncertain output**. After original media and jobs are durable, it enables the paid manifest's background Drive upload intent; no actual uploads, physical printing, refunds, or customer payment activation are performed by this code.

New `tests/test_post_preview_paid_strips.py` covers verified paid QR composition, immutable repeat/resume, and corrupt-output hold. CI pending for this new source SHA; do not claim full PP-001..112 acceptance. This is **PP-05.c staging**, not PP-05.d photo printer integration or physical UAT. Existing legacy prepaid and actual cloud/payment paths stay unchanged.


## 1 November 2026 — PP-05.c3a frozen contract read-only fix (CI pending)

Initial PP-05.c3a CI `41320076932` Linux failed **2 errors / 371 tests** (native desktop SUCCESS; Windows cancelled). Both were triggered because the new import mistakenly called `PrivateDraftPhotos._selected`, whose contract correctly requires **editable** drafts and therefore rejects any post-provider-create paid purchase. This fix replaces that call with an original, non-editing `ledger._owned(lease)` check and direct selected `pp_templates` row verification against the frozen template, approved flag, unchanged lineage and copy quantity. Keep immutable CREATE_PREPARED lock, original source hashes, retake quota and all runtime safety guards unchanged. Recheck CI after push; no full PP acceptance, real Drive or printed photo is claimed.


## 1 November 2026 — PP-05.c3a original PAID raw media import (new; CI pending)

New `OriginalPaidMediaImporter` (isolated synthetic-only) verifies the same immutable provider-paid OWED service, trusted original still-live worker lease and **full frozen source-photo/artwork hashes** before creating an exact paid storage-layout-2 manifest in the **already journaled, remotely verified original folder**. It copies the original three JPEGs per design and any consumed retake as **byte-identical, source-sha-verified immutable files**, with durable per-file PREPARED/COMMITTED import intents, hard-link no-overwrite publication, and recovery that verifies existing outputs rather than creating new transaction identities. Manifest preserves original purchase/entitlement binding, exact copies and retake lineage. `drive_intent=False` and no strip output until verified Drive-link QR composition later; no public upload or print. All financial obligations remain PAID/OWED.

Four new `test_post_preview_paid_media` cases assert original raw copies, no unpaid public effects, byte-identical idempotent restart, damaged source rejection and foreign-manifest hold. CI remains PENDING; no PP full-case PASS, physical UAT, remote real folder, merchant or production action. **Next PP-05.c3b:** use already VERIFIED folder URL to safely compose exact per-design purchased strips with QR and durable original one-job-per-template ledger, without printing until PP-05.d. Crash between original JPEG import and strip output is resumable or safely held; no silent regenerate of uncertain printed output.


## 1 November 2026 — PP-05.c2 CI fixture setup correction (new; rerun pending)

First containing-source CI run `41319419783` **FAILED**: Linux 358 run / 4 ERROR / 0 assertion failures (Windows subsequently cancelled; native SUCCESS). All four new Drive binding tests incorrectly called `CheckoutFixture.enable_paid_ticket()` **after** payment started, which is forbidden by the existing `attach_paid_ticket` security admission guard. Correct only the fixture order: attach the synthetic ticket service before starting a new private visit; leave runtime guard unchanged. The original claim_exact tests and 354 other tests passed on the failing run. Current micro-fix CI is PENDING; this is not a full acceptance PASS or a merchant/Drive device result.


## 1 November 2026 — PP-05.c2 guarded original PAID Drive binding (NEW; CI pending)

**Synthetic-only authenticated integration, no live Drive operations:** new `OriginalPaidDriveBinding` checks the independently verified original PAID/OWED entitlement, exact still-live photo/worker lease, frozen media/artwork/checksums, merchant binding and original PB001V2S2 storage namespace. It writes the immutable original `transaction_id` to `pp_paid_services` **before** taking any slot, then calls `BoothWorkspace.claim_exact`. A provider timeout, lost ACK, worker restart or malformed/foreign folder response can never select a different paid transaction ID. Existing `BoothDriveClient.bind_transaction` is the only remote verification boundary; exact transaction ID, fixed Drive folder URL, link_verified and photo layout 1 must all match. Only after the workspace remembers the original claim may the paid service become `drive_state=VERIFIED`. Failures hold OWED/UNKNOWN with original folder identity, never invent a URL.

Five additional synthetic cases cover idempotent original binding, network failure/retry, forged wrong URL, no unpaid folder claim and wrong transaction response. `original_slot` is an exact trust-boundary lookup of local original READY/claimed identity, not a public token API. No paid strip composition, print, photo upload, retention activation or public download has been enabled. **This is not complete PP-05.c**, nor full PP-001–112 acceptance; next create paid transaction manifest and exact verified-URL strip, then ensure serialized printer and isolated background upload. Current code is still mock-only and actual Apps Script Code.gs deployment is unverified. This commit's CI is pending.


## 1 November 2026 — PP-05.c1 original PAID folder claim primitive (new; CI pending)

Extend existing `BoothWorkspace` with `claim_exact(transaction_id, claim_token)` to claim **only** a selected original READY queue-head identity or recover **the same** already-claimed folder after restart. No second allocation, token substitution, foreign booth ID, nonempty pre-claim folder or missing previously claimed folder may silently pass. Its caller must first journal the original paid transaction identity; the method cannot create payment, bind remote Drive, upload media, print or release customer data. Original `claim()` is unchanged.

Added focused `test_post_preview_paid_drive` four cases (restart/original idempotence, foreign token, queue head/nonempty slot and missing claimed folder), registered in Windows/Linux CI. **CI pending**. This is a PP-05.c dependency only: durable PAID→transaction intent, actual authenticated Drive folder binding, verified URL, final QR composition, media upload and purchased-strip delivery remain NOT_IMPLEMENTED. All 112 complete PP cases remain NOT_RUN; no cloud action is enabled.


## 1 November 2026 — PP-05.b3b typed native ticket / independent receipt handoff (NEW; CI pending)

For **explicit incomplete synthetic mock fixture only** the first independently observed original PAID/OWED now queues its original ticket through PhotoJobs, displays the native typed Recovery Ticket card with full-code visibility gate, begins one 30-second monotonic clock only after worker-confirmed genuine UI render, and queues exactly one receipt send through the same serialized worker lane. NEXT/timeout immediately wipes private code/texture even when the printer worker remains in-flight; a deferred original dismissal occurs only after the single-flight worker completes. The late print outcome never rebuilds or restarts the card. Original CCP, legacy/prepaid route, provider, Drive, automatic release and refund stay unchanged.

**Native software tests added:** at 800×1280 and 452×900 prove first paid ticket, full original QR, one in-memory receipt send, 30-second clock and no duplicate after NEXT, and NEXT while an intentionally blocked in-memory printer is sending. The source is deliberately unavailable to default/Sandbox/production launchers; this is not customer physical UAT, real receipt/paper proof or PP-001..112 full-case PASS. Independent Windows/Linux/native CI must finish before claiming regression success. Next PP-05.c requires exact verified Drive binding/URL and PP-05.d paid strip print, then PP-06 recovery, PP-06R and PP-07.


## 1 November 2026 — PP-05.b3a synthetic paid-ticket worker integration (NEW; CI pending)

The isolated noncommercial `PrivateCheckoutService` now accepts an **explicit synthetic-only, same-ledger/matching-merchant** original paid-ticket service and a shared bitmap printer lane. New worker actions `prepare_ticket`, `ticket_visible`, `ticket_send_receipt`, and `ticket_dismiss` preserve PAID/OWED while using the original encrypted credential and one receipt job; no photo print, Drive or payment authority is granted. A failed/hidden original visit cannot offer/print; dismissal is irreversible and cannot restart the ticket. Fixture records only bitmap dimensions, not customer/ticket pixels.

**Software evidence pending:** four new `test_post_preview_checkout_ticket` cases run under Linux/Windows CI in the existing offline private-state group, alongside PP-05.b1/b2 and legacy regressions. This increment intentionally **does not mount the customer UI**: PP-05.b3b must connect the new typed private card + visible timer to the current synthetic native checkout and prove NEXT while receipt is in-flight. Production and Sandbox checkout remain disabled, 112 complete PP cases remain NOT_RUN; actual paper/cloud/provider remain untouched.


## 1 November 2026 — PP-05.b2 native ticket card + visible countdown contract (NEW; CI pending)

**Additive, still disabled from customer payment:** Reuse the original Kivy private CCP render/visibility/redaction gate for the typed PAID Recovery Ticket, maintaining QR bitmap cache bypass and complete code fit at 800×1280 and 452×900. Add a pure UI-only `VisibleTicketWindow` clock: 30 seconds start only after genuine visible offer is acknowledged, provider polling or print ACK never restarts it, NEXT and actual timeout dismiss at most once, pause/retirement cannot re-open. The original CCP title and visual path remain the default; new typed Recovery Ticket Card cannot accept a CCP role. Neither the native view nor countdown provides payment, print, media, or service authority.

**Tests:** `test_post_preview_ticket_view` (native, two portrait sizes, role/hidden gates) and `test_post_preview_ticket_window` (pure clock, early NEXT, timer, replay and retirement). These are component contracts only; **no live ticket screen integration yet**. PP-05.b3 will wire actual PAID→ticket worker→visible callback→receipt job→30s/NEXT→protected paid output hold. PP-05.c verified Drive and PP-05.d purchased strips remain future work. All 112 full PP scenarios NOT_RUN. CI/result for this commit pending verification; earlier PP-05.b1 CI retains its actual source scope.


## 1 November 2026 — PP-05.b1 receipt transport safety micro-increment (NEW; verification pending)

**Scope of this commit:** Add original post-preview ticket in-memory thermal bitmap renderer and a single-use worker-side receipt send contract. Original PAID and a genuinely visible ticket render permit are required. Persist SENDING before any printer bytes; terminal SUBMITTED / NOT_SENT / UNCERTAIN states never replay after crashes, lost ACK or restart. The exact original token is never written as a receipt PNG or stored in ordinary logs; a shared printer transport lock is required before real transmission, and no caller can silently use a separate lane. No new payment, producer output, auto-isolation, Drive upload, merchant activation or legacy ticket change.

**Tests:** Added `test_post_preview_ticket_receipt` to Windows/Linux private-state CI with seven focused cases covering presentation guards, once-only bitmap transport, no-printer, missing shared lane, uncertain print, restart SENDING and wrong credential QR. Tests/CI are **PENDING** for this new SHA and will be reported after completion. Do not count any of PP-001..112 as complete PASS. Native mandatory 30s screen and exact UI-bound parallel dispatch still **NOT_IMPLEMENTED**; this is safe disabled preparation for PP-05.b2. Keep PP-05.a, PP-04.d and other historical evidence unchanged.


Updated 1 November 2026 (Asia/Jakarta). **IN_PROGRESS / NOT_READY_FOR_PHYSICAL_UAT.**

## Authority and exact Git boundary

The owner's uploaded **CODEX MASTER EXECUTION PROMPT — MEONG PHOTOBOOTH**,
received 1 November 2026, explicitly authorizes application/schema/test/docs
implementation, micro-commits and immediate pushes through PP-00..07 (including
PP-06R), only on existing `feature/post-preview-qris-checkout`. This supersedes
the earlier design-only implementation restrictions. All financial/privacy/
worker safeguards remain binding. Production deployment, actual charges/refunds,
merchant activation, live customer/cloud deletion and other branches are excluded.

- Authorized branch: `feature/post-preview-qris-checkout`.
- Latest complete prior 3/3 CI: `2f394e612ed00eff9da72054ee8b1afdaae4bcb6`, run `41319612205` Linux/Windows/private-desktop SUCCESS for PP-05.c2 binding. PP-05.b3b exact ticket GUI also had 3/3 SUCCESS at `27a715a` (run `41318781093`). Later PP-05.c3b corrected source and PP-05.d1 currently have Linux + native SUCCESS, while Windows remains IN_PROGRESS at run `41320976927`. Historical failed test-fault runs and canceled Windows runs remain in individual dated entries.
- Original audited base: `b68e514dd57c989df47fa1b222d45f3f71c38347`.
- Current implementation increment: **PP-05.d1 MOCK-ONLY original paid strip batch submission** at functional source `6c742437ac034a5251322388fbe6176fab687cfe`. Current HEAD also includes docs-only progress micro-push. Components PP-05.a/b/c/d1 exist and are test-covered in isolated fixtures; the latest full containing-source CI is still pending Windows. Next missing work: PP-05.d2 actual safe delivery/upload/fulfillment handoff, followed by PP-06 customer proof and unattended isolation, PP-06R provider-gated refund and PP-07 full UAT.
- Overall: PP-00 original architecture and dependency audit established; PP-01 private capture/review and PP-02 frozen all-design checkout implemented; PP-03 encrypted CCP and PP-04 actual request/readiness/lifecycle/mock payment components implemented and CI tested; PP-05.a original paid entitlement/ticket, b mandatory visible 30s/NEXT and one concurrent receipt, c immutable original folder/verified Drive URL and QR strip preparation, and d1 mock-only one submitted strip/copies journal are implemented, but **the full PAID customer delivery, original proof claim/release, actual Sandbox/Drive/printer and refund are not enabled**. PP-05.d2, PP-06, PP-06R and PP-07 are NOT_IMPLEMENTED/NOT_RUN; entire PP-001..112 complete-case acceptance NOT_RUN. Do not call this physical UAT or production-ready.
- This checkpoint travels with the implementation commit. Resolve its containing
  SHA using `git log -1 --format=%H`; after push independently compare `git
  ls-remote origin refs/heads/feature/post-preview-qris-checkout`. A commit cannot
  truthfully contain its own SHA. The next increment records this verified tip.

## PP-05.a — original paid service and protected ticket foundation

Additive private schema v6 preserves original v1..5 draft/finance/CCP journals and
adds paid service, ticket escrow, independent screen/receipt and purchased-strip
intent tables. Current-schema missing/partial paid journals hold instead of being
recreated. SQL guards bind service to original independently issued entitlement,
frozen hash and first-paid anchor; ticket/service/folder/transaction and print
identities cannot be replaced, and screen/receipt/strip states cannot replay.
No delivery effect is enabled merely by migration or row creation.

OriginalRecoveryTicketService reuses the actual protected CCP encryption,
constant-time verification, rate limit, in-memory render permit and privacy
retirement implementation through **fixed internal profiles**. CCP retains its
old prefix/table/policy; new ticket is `MEONG:RECOVERY:1:<booth>:<group>:<secret>`
with a separate verifier/table and typed non-media/non-payment verification result.
Encrypted issuance is once per original paid entitlement. Independent recent
original settlement and live original worker are required; no ticket from
pending/unknown/retired visits. No plaintext, QR bitmap or vault key enters DB,
WAL, event/diagnostic metadata or source. Key/journal loss keeps OWED and never
reissues another ticket. A copied/rebooted render permit cannot mark an offer.

Original paid service remains OWED. Ticket generation/decrypt is NOT visible
presentation or receipt submission. Genuine renderer callback atomically records
first TICKET_QR_VISIBLE and original render permit; dismissal is once/idempotent.
Previously visible/dismissed tickets cannot auto-redisplay after restart; receipt
PREPARED/SENDING/SUBMITTED/UNCERTAIN is independent. Receipt dispatch, 30-visible-
second native timer and purchased delivery are the **next** PP-05 increment.
Default customer/Sandbox paid route remains disabled.

Versioned engineering pilot policy: ticket TTL defaults to 24h from original
**first independently observed PAID**, not draft/QR creation. This is a distinct
`post-preview-ticket-paid-anchor-pilot-v1`, not legacy 24h policy adoption or
commercial/legal signoff. Paid service retention anchor is separately recorded
and immutable; actual retention/deletion behavior is not activated by these tables.

Ten new ticket methods cover paid-only binding, same-original encrypted restart,
no offered-ticket replay, separate proof types, DB/WAL plaintext absence, wrong
key/missing journal, privacy retirement, v5 migration, SQL no-replay guards and
multiple-settled attempts preserving one service/ticket. Existing v1/v4 migration
fixtures now reconstruct their true old schema before upgrade, preserving owner,
lineage, original attempt, paid entitlement and CCP ciphertext.
Test-first missing module ERROR, then focused **54 PASS / 0 FAIL / 0 ERROR / 0 SKIP**,
21.625s. Final private/legacy/Drive group **314 PASS / 0 FAIL / 0 ERROR / 0 SKIP**,
62.357s; native group **41 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, 29.924s. Compile/diff
PASS; matching-source CI pending push. No physical/provider/cloud/refund effect.
All 112 complete acceptance cases remain NOT_RUN; only component crosswalk grows.

Reviewed original CCP/vault, schema/migrations, original receipt renderer/
print_bitmap, native CCP visibility, PP ticket/security/refund/UAH/BUG-027 contracts
and existing purchased-print/PhotoTest no-replay integration. Reuse is direct;
legacy paid-first credential/receipt/service code remains unchanged.
Next **PP-05.b**: mandatory original QR/full-code card with independent 30-visible-
second/NEXT clock and one concurrent same-ticket receipt job through a serialized
native printer lane. Then verified paid Drive URL, exact paid strips and durable
remaining obligations; PP-06/06R/07 still required for laptop testing candidate.

## PP-04.d4 — authenticated request and original worker readiness

Owner continuation (1 November, Asia/Jakarta) explicitly requests autonomous
completion to a laptop physical-test candidate, without routine confirmation.
Existing branch/push authorization and production/cloud/refund exclusions persist.

The authenticated begin/continue route establishes a scoped in-memory request
observation only after BoothAuthenticator, strict body parsing and original
worker-lease validation. Local readiness independently reads that observation;
JSON ready flags and direct unauthenticated coordinator calls cannot supply it.
Context is retired on success and failure and carries no bearer credential.
This proves payment-backend availability/booth authorization for the actual
request, not merchant-provider account acceptance or guaranteed settlement.

OriginalWorkerReadiness reuses original LaunchLease, PhotoJobs/PrivatePhotoService,
private generation/contract checks, legacy CheckoutStore/release/fence facts and
read-only recovery review. Missing journals/owner are UNKNOWN; retired/wrong
customer/generation, active capture, unresolved legacy/PP finance and unsafe old
service hold. Existing paid legacy closure needs fulfilled rights or exact ACKED
release/suspended fence evidence; no PIN bypass, new release, claim, cancellation
or reset occurs. Prior PP services remain held until the later PP-05/06 durable
delivery/release integration proves their outcomes.

Local camera readiness now adapts each actual AsyncCamera fresh mailbox read
through the original CachedCamera health adapter; no second handle/open/shutter
or permanently cached frame. Original printer-route probe keeps real defaults;
only explicit synthetic fixtures inject a no-paper dial. Native CheckoutFixture
now mounts actual local/Drive protocol/request/worker checks, including the actual
app PhotoJobs/camera registration, with synthetic provider/vault/cloud responses.
The legacy frozen-preview boolean fixture is not server charge authority.

Test-first missing module ERROR; two new legacy fixture setup errors (quote field
and positional begin signature) corrected without runtime/assertion relaxation.
Seven new authority methods cover authenticated route vs direct call, context
cleanup, wrong owner/generation, missing journal, current capture, closed launch
lease, privacy retirement, unresolved old purchase and stale AsyncCamera mailbox.
Configured private-state/legacy/Drive group **304 PASS / 0 FAIL / 0 ERROR / 0 SKIP**,
61.072s. Native original six-module group **41 PASS / 0 FAIL / 0 ERROR / 0 SKIP**,
25.742s, both portrait sizes in the native fixture. Compile/diff PASS. Tests and
fixture are registered in existing Windows/Linux/native CI; CI pending push.
No merchant/Drive/printer/account action, hosting, raw credential artifact or
customer-data mutation occurred. All 112 complete acceptance cases remain NOT_RUN.

PP-04.d software components are integrated; actual merchant/device/Google account
acceptance and remote-hosted media attestation are not claimed. Customer/Sandbox
checkout stays disabled until PP-05 paid delivery is integrated. Next after this
increment's remote/CI gate: **PP-05.a** bind verified PAID to original media and
one entitlement, original protected Recovery Ticket and durable dual-channel
presentation/receipt intent, then native 30-visible-second/NEXT screen and paid
Drive/strip delivery. PP-06/06R/07 remain required before laptop candidate handoff.

## Historical verified continuation checkpoint — PP-04.d incomplete at ab57cd7

All changes in this continuation were pushed only to the existing authorized
branch, with remote SHA checked after each push. No merge, other branch push,
force-push, default-branch operation, production/deployment, real merchant action,
cloud/customer mutation or paper send occurred.

| Increment | Verified source | CI / exact evidence |
| --- | --- | --- |
| PP-04.d1 lifecycle scheduler | `2dc2f07f91a4e042552ae63beb28d18c7f049d33` | `41307192307` all 3 SUCCESS; local 230 private/legacy + 41 native PASS |
| PP-04.d2 freshness/local checks | `992fd52e9d576a8ac13e186552b57aba367ef60b` | `41307908892` all 3 SUCCESS; local 246 private/legacy + 41 native PASS |
| PP-04.d3 read-only Drive | `f1b2b4c594895e1e2e537bcfe7c402e83d8c251f` | local 297 Python + 34 VM PASS; `41308665185` Linux/native SUCCESS, Windows 1 FAIL/4 ERROR retained |
| Windows fixture/dependency correction | `5ff093e15b7425542fe173082ca55adaf8d95f79` | `41309087008` all 3 SUCCESS; Windows/Linux each 297 PASS, native 41 PASS, VM 34 PASS; zero skips |

Counts overlap and must not be summed as unique full acceptance. The containing
checkpoint commit changes documentation only; runtime/tests/workflow remain
identical to verified `5ff093e`. Its own SHA is obtained from Git log/remote.
All **112 complete PP cases remain NOT_RUN**; customer checkout is still disabled
and NOT_READY_FOR_PHYSICAL_UAT. Code.gs remains source-only NOT_DEPLOYED, real
Drive acceptance NOT_RUN; existing deployed support is an external authorization
and verification gate, never a reason to call a mutating fallback.

**Exact next micro-increment PP-04.d4:** implement independent authenticated
payment-backend availability/authorization and trusted original camera/service/
worker ownership checks, including unresolved legacy/PP visits. Reuse original
BoothAuthenticator/PostPreviewClient, LaunchLease/PhotoJobs and existing recovery/
occupancy journals; do not accept a GUI ready flag or turn public Advertising
into free-booth proof. Integrate the local + read-only Drive + independent probes
into the native synthetic CheckoutFixture. Native AsyncCamera uses a mailbox
adapter rather than the v1 Camera handle shape; reuse the original cached-camera
health adapter and preserve actual observation timestamps. Missing ownership/
legacy state stays UNKNOWN. Test stale/suspended/restarted generations, another
customer, unknown old finance, missing backend authorization and delayed replies
before any new create. Keep all merchant/cloud/hardware gates disabled.

After PP-04.d4 and remaining PP-04.d fault/CI gates, proceed to **PP-05** mandatory
original 30-visible-second ticket screen + concurrent one-time same-ticket receipt,
paid folder/URL binding and purchased-strip journals. Then PP-06, PP-06R and PP-07
in order. They are unfinished software requirements, not merely hardware tests.
No initial ticket, paid delivery, claim/isolation/refund or 112-case PASS was
manufactured by these readiness/scheduler increments.

Scratch logs are retained outside the checkout under `/workspace/work/` and are
not a Git backup or customer deliverable. No local-only source change is intended
at this checkpoint. Resume with clean status, current local/remote SHA inspection,
this document and the exact affected AR/UAH contracts before implementing d4.

## PP-04.d3.ci — Windows coverage correction (1 November 2026)

Published PP-04.d3 `f1b2b4c594895e1e2e537bcfe7c402e83d8c251f`, run
`41308665185`: Linux state and native desktop SUCCESS; actual Code.gs VM passes
on both OSes. Windows Python **297 run / 1 FAIL / 4 ERROR / 0 SKIP**. All new
readiness methods pass; four expanded legacy Drive cases require `tzdata`,
already declared by requirements.txt but omitted from this minimal CI install.
One pre-existing mapping assertion compared Windows 8.3 TEMP spelling with the
worker's canonical long path. No payment/readiness runtime defect is inferred.

Adds declared `tzdata` to the private-state install and compares both **existing
canonical paths** with `resolve(strict=True)`. This preserves the exact original
folder/file-mapping safety assertion, rejects another customer path and requires
both files to exist. No fallback timezone, skipped case, relaxed payment guard,
provider/Drive mutation or runtime module change. `photobooth/` and `apps_script/`
remain byte-identical to PP-04.d3. Focused Linux `python tools/run_kiosk_unittests.py
 test_booth_sync test_post_preview_drive_readiness`: **34 PASS / 0 FAIL / 0 ERROR /
0 SKIP**, 2.753s. Prior full 297 PASS/34 VM PASS keep their original functional
source scope; no redundant full local rerun for this fixture/dependency correction.
Corrective source `5ff093e15b7425542fe173082ca55adaf8d95f79` remote verified.
CI `41309087008` all three jobs SUCCESS: Linux and Windows each **297 PASS /
0 FAIL / 0 ERROR / 0 SKIP**, native **41 PASS / 0 FAIL / 0 ERROR / 0 SKIP**.
Actual Code.gs VM **34 PASS**; earlier failed run is preserved.

Next remains **PP-04.d4** independent authenticated payment-backend and original
worker/occupancy readiness plus native fixture integration, then PP-05. Real
Windows hardware, merchant provider, deployed Drive, printer and full 112 PP
acceptance remain NOT_RUN; Google source remains NOT_DEPLOYED.

## PP-04.d3 — nonconsuming Drive readiness (1 November 2026)

The existing layout-2 Apps Script gains authenticated `storage_readiness`.
It checks only the requested original unclaimed reserve identities: read-only
Drive API parent metadata/capabilities, exact numeric child/owner marker and claim
verifier, genuinely empty contents, untrashed original parent and actual
Anyone-with-link/Viewer ACL. Claimed/private/nonempty/foreign/wrong-proof/old-name
reserves cannot count READY. No create, bind, assign, rename, move, setSharing,
retention marker, trigger or customer-photo read/write is called. It cannot repair
an old-name reserve. Zero verified candidates is NOT_READY; missing capability or
failed observations stay UNKNOWN. Authentication/types/bounds/duplicates precede
Drive reads. Response excludes URLs, claim tokens/verifiers and account errors.

`BoothDriveClient.storage_readiness` reuses the original authenticated transport,
sends only original candidate ID/proof fields, and strictly checks booth/layout/
protocol/read-only marker and consistent bounded typed state/count evidence.
`ReadOnlyDriveReadiness` compares original workspace/client namespace and physical
booth, reads existing READY slots without replenishment/claim/counter writes,
and makes **one** inspection for the three Drive signals. A slow result retains
its original observation time instead of claiming fresh readiness. Missing old
Web App support, authorization, network or correct scope stays UNKNOWN.
`LocalChargeReadiness` composes these actual observations with local checks;
no bare `ready=true` or guessed customer download link is introduced.

A real authenticated API fixture rejects failed Drive sharing before any payment
attempt, then safely retries the same frozen original purchase when a fresh
inspection succeeds. Original 25-slot pool/counter and all empty reserves remain
unchanged. Its payment-authorization and worker-ownership probes are explicitly
synthetic and remain unfinished production adapters; this is component evidence.

Test-first: new JS behavior initially **30 PASS / 3 FAIL** (the authentication
negative also passed against unsupported action), Python missing adapter ERROR.
Final actual Code.gs offline VM **34 PASS / 0 FAIL / 0 SKIP**, 207.268ms; mutation
methods are forbidden in the readiness fixtures. Final Python affected group
**67 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, 8.755s. Configured private-state/legacy/
Drive regression **297 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, 54.780s. Commands:
`node --check < apps_script/Code.gs`, `node --test tests/test_apps_script_retention.cjs`,
`python tools/run_kiosk_unittests.py test_post_preview_drive_readiness
 test_post_preview_readiness test_booth_sync test_booth_storage test_apps_script_drive
 test_retention_readiness`, and the exact workflow private-state group. Seven
new Python methods and the VM suite registered on Windows/Linux. Restricted
network-profile Node runner initially failed without diagnostics; the same fully
offline VM passes with the execution network profile enabled. No Google request
was made. Compile/diff checks PASS; published source `f1b2b4c` CI
`41308665185` Linux/native SUCCESS, Windows portability failures corrected in
PP-04.d3.ci above.

**Deployment boundary:** this changes source ONLY. Existing Google Web App was
NOT updated/deployed and no account or cloud file was accessed. Actual deployed
readiness support is BLOCKED until separately authorized manual deployment of the
existing project and real-account verification. Software fixtures are PASS only;
real Drive/API/sharing acceptance NOT_RUN. Do not use mutating reserve APIs as a
fallback against an old deployment. Retention behavior and 15d/30d anchors remain
unchanged; original VM retention cases all PASS with synthetic objects only.

Component crosswalk adds PP-019/055/056/081 only, never complete acceptance. All
112 PP full cases still NOT_RUN. Reviewed actual Apps Script layout-2 dispatch,
reserve/bind/ownership/ACL/metadata helpers and VM harness, original client,
BoothWorkspace lock/read/counter contracts, Drive storage-layout/retention policy,
and PP freshness/admission invariants. No actual provider, printer, private
customer media, refund, public hosting or production operation occurred.

**Next PP-04.d4:** independent authenticated payment-backend availability/authority
and authoritative original camera/service/worker ownership + unresolved-visit
readiness, with native checkout fixture mounting and stale/timeout/restart/race
checks. Keep incomplete adapters UNKNOWN; no client readiness authority. Revisit
freshness latency/calibration honestly before real-account/device testing. Then
finish PP-04.d acceptance/CI and proceed to PP-05 mandatory original ticket screen
+ concurrent same-ticket receipt, verified paid folder/URL and exact strip jobs.
PP-06/06R/07 remain unfinished software; all external release gates stay explicit.

## PP-04.d2 — trusted freshness and local readiness (1 November 2026)

`post_preview_readiness` adds original purchase/booth/frozen-contract/generation
scope and typed READY/NOT_READY/UNKNOWN observations. STALE is derived from actual
observation age, never asserted from a successful current callback. Missing,
failed, client-style boolean/dictionary or untyped probes remain UNKNOWN. Future,
nonfinite and boolean timestamps fail closed. Observations retain their timestamps
when cached. Two seconds is a conservative software pilot freshness bound, not
merchant/device calibration. No raw media, proof or exception details are stored.

The trusted same-machine `LocalChargeReadiness` reuses original private photo,
retake, frozen-artwork and PNG/JPEG verification with **repair=False**; a readiness
check cannot repair a staged capture, recreate a missing manifest or allocate a
replacement lineage. Original quote, selected copies, approvals, three final
photos, template/mask hashes and preview digest are checked. Ownership is read
before/after file I/O, which stays outside payment SQL transactions. Existing
capture recovery keeps its original default repair behavior.

Actual private-storage reserve/entry/byte checks plus a uniquely created fsync
probe reuse `PrivateCapturePolicy`; only that temporary probe is removed. Camera
readiness reuses the existing opened handle/latest-frame mailbox (no acquisition
or shutter). Printer readiness reuses original route/queue/device probes, sends
no bytes and claims no physical paper. External authenticated payment, Drive API,
sharing, unclaimed READY capacity and authoritative worker/occupancy probes must
still be installed; absent adapters stay UNKNOWN. No reserve/bind/upload/print
method is available through this adapter. Remote-hosted media attestation is not
implemented by the local adapter.

Payment admission accepts the trusted original-scope report and independently
checks freshness both before preparing a new attempt and immediately before SENT.
**Recovered original PREPARED now requires a new readiness observation**; stale
or failed evidence preserves the same unsent attempt for a deliberate safe retry.
SENT/UNKNOWN still reconcile without readiness or repeat POST. Renewals keep the
same fresh scope checks. Untimestamped `ChargeReadiness` booleans are accepted
only by historical explicitly MOCK synthetic fixtures, never Sandbox admission;
HTTP request `ready=true` is rejected, just like caller amount/status authority.
No customer/Sandbox launcher or merchant request is enabled.

Test-first: initial missing module ERROR; then the nine-method partial scaffold
showed **1 FAIL / 4 ERROR** for missing behavior. Final focused group **72 PASS /
0 FAIL / 0 ERROR / 0 SKIP**, 22.685s, before the last two storage/journal methods;
final configured private-state + legacy group includes all **16** new methods:
**246 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, 46.859s. Native six-module group **41 PASS /
0 FAIL / 0 ERROR / 0 SKIP**, 27.431s, SDL offscreen, both portrait sizes in original
fixtures. Focused command: `python tools/run_kiosk_unittests.py
 test_post_preview_readiness test_post_preview_payments test_post_preview_photos
 test_post_preview_checkout test_post_preview_payment_crashes`; final group is
exactly the workflow private-state command. Compile/diff checks PASS; published
source `992fd52e9d576a8ac13e186552b57aba367ef60b` remote verified; CI
`41307908892` all three jobs SUCCESS. All testing synthetic, no external provider/Drive calls,
real paper/customer data, credential screenshots, refunds or production actions.

Component crosswalk adds PP-009/014/016..020/031/055/063/069/081/083 only; all 112
complete cases remain NOT_RUN. Reviewed original capture/preview repair behavior,
private resource policy, device health/printer route, frozen contracts, actual
BoothWorkspace/BoothDriveClient and Apps Script reserve/sharing implementations,
plus storage layout and UX07/Midtrans/PP contracts. Existing cloud reserve APIs
may create/move folders or change ACL, so they must NOT be reused as readiness.

**Next PP-04.d3:** add a separate authenticated **read-only** layout-2 Drive
readiness action/client over existing exact reserve identities (never reserve,
claim, rename, move or setSharing), verify API/sharing and genuinely unclaimed
capacity, then connect independent payment authorization and authoritative
worker/occupancy probes to the trusted local/native fixture. This remains ordinary
unfinished software, not a hardware blocker. After PP-04.d gates/CI, proceed to
PP-05 same-original ticket screen + concurrent receipt and paid Drive/strip jobs.
PP-06, PP-06R, PP-07 remain unfinished; actual device/provider gates NOT_RUN.

## PP-04.d1 — original-order lifecycle scheduler (1 November 2026)

Adds `post_preview_lifecycle.PostPreviewLifecycleWorker`, owned by the isolated
post-preview API lifespan. Startup runs bounded durable inbox maintenance and
round-robin original-group reconciliation; shutdown drains the worker before
calling ledger shutdown. A timed-out worker remains active and prevents ledger
closure/duplicate worker startup. No application launcher, listener, merchant
configuration or customer checkout gate is enabled by this factory integration.

Reuses existing inbox leases/backoff/quarantine and payment reconciliation leases,
poll pacing, cancellation intents and strict independent provider GET evidence.
Retired and previously terminal attempts remain eligible for late-PAID detection.
Every original attempt is reconciled, with one original entitlement/OWED; no
CREATE, QR renewal, media disclosure, printing, Drive allocation or booth release
runs in the scheduler. Durable USER_CANCEL/ABANDONMENT cancellation is recovered;
SUSPEND and expiry alone never cancel or renew. Per-scope and inbox failures are
contained without logging private exceptions. The scan is bounded and rotates
past historical groups instead of starving newer groups.

Test-first evidence: missing worker import initially ERROR; final worker/payment/
API/child-process group **60 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, 16.184s.
Configured private-state + legacy regression **230 PASS / 0 FAIL / 0 ERROR /
0 SKIP**, 45.987s. Commands: `python tools/run_kiosk_unittests.py
 test_post_preview_lifecycle_worker test_post_preview_payments test_post_preview_api
 test_post_preview_payment_crashes`, then the workflow private-state group.
Ten new worker methods registered in Windows/Linux CI. Initial restricted-network
TestClient run hung and was terminated; the same synthetic loopback tests pass
with the execution network profile enabled. No provider network was contacted.
Two early test assertions incorrectly treated cached inspection as fresh PAID;
corrected the assertions to check durable state/entitlement, retaining the existing
`paid_verified=False` safeguard for cached inspection.

Native group **41 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, 28.303s, using
`SDL_VIDEODRIVER=offscreen` plus the existing software GL/dummy-audio settings.
Local `xvfb-run` is unavailable (initial command exit 127); supported SDL offscreen
ran the original six-module native group without changing assertions or UI.
No credential screenshots saved. Published source `2dc2f07f91a4e042552ae63beb28d18c7f049d33`
verified remote; CI `41307192307` all three jobs SUCCESS.
All 112 full PP cases remain NOT_RUN; component crosswalk extends PP-021/022/023/
027/028/031/032/035/062/074/075/083 only. Real Windows/POS80/webcam/Midtrans/Drive
and public-provider gates NOT_RUN; production and refunds remain disabled.

Sources reviewed: AGENTS, index/protocol/current status/backlog/handover, PP
checkpoint/handover/owner decisions/complete ledger/security/refund/112-case
matrix, unattended handoff, UX07 readiness, provider contract; actual original
payment/inbox/schema/authenticated API and normalized evidence implementations.
No legacy payment/capture/printer/Drive source changed. Rollback is a scoped
inverse code commit preserving every financial/media/credential journal.

**Next exact increment PP-04.d2:** trusted read-only charge-readiness observations
with READY/NOT_READY/UNKNOWN/STALE, original-scope/freshness validation, frozen
media/artwork/quote revalidation, camera/ownership, private disk, printer route,
authenticated payment/Drive and nonconsuming READY capacity adapters. Recheck on
original PREPARED restart admission as well as every new attempt/renewal. Keep
Sandbox/customer route disabled until PP-05 ticket + paid delivery integration.
PP-05/06/06R/07 remain unfinished software, not hardware-only blockers.

## PP-04.c — native authenticated checkout integration fixture

New PrivateCheckoutService extends original PrivatePhotoService/PhotoJobs, reuses
original frozen checkout/CCP/QR renderer and restricted PostPreviewClient. Native
PrivateCheckoutFixtureApp extends the existing private portrait app and shell,
controls, capture/review/gallery and PrivateCCPCard. No replacement visual system.
Only explicit incomplete mock + synthetic vault adapters accepted; Sandbox mode,
implicit activation and non-synthetic protector rejected before local setup. No
launcher mounts this class and default private-preview launcher remains delivery-off.

Flow actually exercised through real HTTP boundary: all-design final preview ->
independently observed readiness -> immutable original freeze -> protected CCP ->
real attached/native QR + full code visibility -> worker-journaled original offer ->
explicit customer continuation -> server's independent readiness recheck -> same
original payment attempt. Initial create/decrypt is never treated as a proof offer.
Original QR renderer moved to non-GUI CCP module and reexported by the old card
module, allowing worker/state tests without a Kivy dependency. No QR/payload cache,
credential screenshot or ordinary secret journal introduced.

Lost HTTP response holds immutable original purchase and reconciles; no new charge
or editable cart. QR image failure leaves original attempt. Original same-proof
redisplay can recover rendering failure before payment without reset/reissue.
Starting payment retires decrypted offer/render permits. Late HTTP/QR worker after
hide cannot restore pixels. Cancel/suspend are distinct; local durable lifecycle
precedes notification and survives backend outage. Suspension never cancels. All
views lack fulfillment authority and paid observation stays OWED/paid_hold, including
when a later HTTP response is lost; ticket/Drive/print integration remains unfinished.

Configurable nonproduction checkout inactivity default 180s with original 15s
warning. Automatic status polling and render callbacks do not count as customer
activity. Actual active shutter/work retains prior no-hard-visit-cutoff behavior.
Expiry hides proof/payment images and retires original visit without automatic
cancellation, booth release or next-customer admission.

**10 worker/API integration methods** and **3 native methods** added. Native
capture/all-design/CCP/payment/PAID-OWED path exercised at **800x1280 and 452x900**;
checks actual durable offered_at only after attached full native presentation.
Minimize during blocked provider create clears QR/full code immediately; late
reply remains private HOLD, with no accidental cancel. Automatic status GET does
not reset inactivity. Native regression group **41 PASS / 0 FAIL / 0 SKIP**, 21.330s,
including original photos/navigation/QR/card. Initial native timer test used the
unspecified small default window, whose clipped proof correctly could not be
marked offered; fixed fixture to request supported 452x900. No proof screenshots
were saved. Later worker paid-HTTP-loss correction is covered by the focused group;
containing-source CI rechecks full native group after push.

Final clean-venv backend/private/legacy group **220 PASS / 0 FAIL / 0 ERROR /
0 SKIP**, 37.651s. Extended checkout-phase inactivity subcases also **4 PASS**,
0.000s. Diff/compile checks PASS. Containing-source CI pending push; previous
348b4cb CI run 41288588935 all three jobs SUCCESS.
Production/Sandbox credentials, merchant charges, real printer/Drive and public
hosting were not used. All 112 complete acceptance cases remain NOT_RUN.

Next: PP-04.d actual trusted read-only readiness and backend lifecycle worker,
then PP-05 original ticket/paid Drive/output integration before allowing any
Sandbox paid path. PP-06 claim/release, PP-06R finance and PP-07 remain software work.

## PP-04.b — historical authenticated boundary and durable webhook delivery

New isolated `post_preview_api.create_app` reuses original BoothAuthenticator,
bounded duplicate-rejecting JSON parser, bounded rate limiter and worker-thread
I/O. Routes accept exact original visit/generation and authenticated booth; no
caller amount, evidence, provider URL, CCP-offer timestamp or fulfillment setter.
Original frozen group supplies quote/context. Strict types reject coercion; errors
do not echo request bodies or credentials. Legacy endpoints are not mounted or
changed. Cached inspection never claims fresh PAID. Reconciliation covers all
original attempts, with existing normal/priority pacing. Financial observations
always have `fulfillment_authorized=False`.

New restricted PostPreviewClient composes original QrisKioskClient TLS/loopback,
timeout, bounded response and redirect safeguards. It validates original group,
booth, version, mode, amount, typed freshness and lack of fulfillment authority.
Merchant keys remain injected server-side only. This factory/client is an isolated
software seam, not a running backend, production deployment or enabled native UI.
Trusted local capture/backend may share the new ledger; remote production server
media/readiness attestation is not implemented or claimed.

Schema v5 adds bounded pp_notification_inbox. Signature and amount verified before
allocation; only authenticated order/group/attempt scope and event digest persist,
not raw signature, key or notification status payload. ACK occurs after FULL/WAL
commit, with no provider GET. Explicit process_one worker independently fetches
original provider status; durable leased claims, exact completion token, bounded
retry/backoff, crash reclaim and quarantine preserve unknown evidence. Inbox
capacity/disk failure returns retryable failure, not false ACK. Missing/partial
current-schema inbox holds instead of recreating. Worker scheduler/listener wiring
is deliberately unfinished; no public callback has been published.

**17 authenticated API/client/inbox methods PASS** in the final focused group; **6 actual child-process
death methods PASS**, 1.963s, using a separate persistent FULL/WAL synthetic provider
ledger. Killed after PREPARED, SENT-before-remote-commit, remote-create-commit,
provider-GET-before-local-apply, remote-cancel-commit and leased inbox claim. Exact
original attempt survives; SENT never re-POSTs; original cancellation never repeats;
paid settlement produces one entitlement; acknowledged notification survives worker
death. No actual payment/refund/provider/Drive operation occurred. Final clean-venv focused group **210 PASS / 0 FAIL / 0 ERROR / 0 SKIP**,
31.718s, including private state/capture/CCP/payment and legacy checkout/workflow
regression. Additive v1/v4 upgrades and missing/partial v5 inbox covered. An initial
migration test fixture retained a v5 table while pretending to be v1; corrected
the fixture to reconstruct actual v1 tables before upgrade. Compile/diff PASS.
Containing-source CI pending push; e7bfca5 CI all three jobs SUCCESS.

Sources reviewed: original qris_api/qris_kiosk_client, booth_auth,
LegacyNotificationInbox lease/backoff, strict qris_evidence and current provider,
PP security/owner contracts and MIDTRANS-PROVIDER-CONTRACT. No legacy payment,
notification, capture, printer or Drive runtime changed.

Next unfinished increment: PP-04.c native checkout/CCP/API worker integration and
actual read-only readiness adapters, then PP-05 original ticket + paid output/Drive,
PP-06 secure claims/worker-fenced release, PP-06R refund guards and PP-07 all 112
cases/UAT runbook. Do not call those unfinished software tasks hardware blockers.

## PP-04.a — historical purchase/attempt coordinator and evidence

Server-side `PostPreviewPayments`, not yet mounted by a native payment/API route.
Reuses original strict provider evidence/signature/Sandbox URL rules and fixed
MidtransSandboxClient. **No actual merchant request or production endpoint is
used.** New schema v4 has original purchase finance, QR1/2/3 attempt, cancellation,
reconciliation reservation/pacing and redacted audit journals. Immutable SQL guards
protect original draft identity, frozen contract, provider attempt, finance context,
single entitlement and first paid observation anchor. Missing/partial journals hold.

Requires original genuinely offered, still-valid scoped CCP and trusted readiness
before preparing a charge. One original provider order is durably PREPARED then
SENT before external I/O. SENT/UNKNOWN never repeats POST, including after lost
create response/404/restart. Valid original create action (including v4 path) stays
bound, but PAID requires independent GET and exact order/merchant/IDR amount/
reference/method checks. No provider idempotency header guarantee is assumed.

QR2/QR3 require a fresh authoritative EXPIRED-unpaid GET, same active original
worker, explicit continuation, same frozen contract/price, no cancel/review/paid
entitlement and maximum three attempts. Reconcile all attempts for late money.
Exactly one entitlement audit ID per logical purchase; independently settled extra
attempts are separately listed for later guarded financial handling, not fulfilled
or refunded here. PAID is monotonic; fresh access evidence remains independent.
Late/stale verified money is retained OWED without claiming fresh service authority.
No camera, printing, media access or booth release is authorized by this coordinator.

USER_CANCEL/abandonment record original cancel intent before one original cancel
send, then independent status; lost cancel replies reconcile without another POST.
Suspension/inactivity warning do not cancel. Inactivity expiry requires a distinct
VISIT_ABANDONED decision before cancellation. Crash between lifecycle/finance writes
recovers the same intent. Paid/cancel race preserves PAID_UNCLAIMED/OWED. No event
marks machine FREE. Provider mismatch/refund evidence holds for review. Real
Sandbox polling retains 10s normal pacing, 1s priority pacing and bounded leases;
mocks use explicit zero-delay fixtures. Readiness I/O is outside SQL transactions.

Actual **27 payment fault/race methods PASS**, included in clean-venv group
**187 PASS / 0 FAIL / 0 SKIP**, 25.578s. Covers signed/unsigned/stale webhook and
amount rejection, lost create/404, QR cap, cancel/settle and late-paid races,
cross-connection concurrent starts, QR1 PAID during QR2 create, excess payments,
unknown and stale reconciliation, interrupted cancel intent, no fake freshness,
immutable identity/price/entitlement and paid-anchor nonextension. Compile/diff PASS.
Earlier native private/card/QR/photo/navigation group **38 PASS / 0 FAIL / 0 SKIP**,
13.475s for schema compatibility. Current containing-source CI pending push;
previous card CI 41286019681 all three jobs SUCCESS. Financial fields remain
unmounted/disabled for customers; no real merchant/provider acceptance inferred.

Added [112-case execution ledger](POST-PREVIEW-QRIS-EXECUTION-MATRIX.json): exactly
112 unique canonical cases, all complete-case NOT_RUN, with implemented component
module crosswalk. It explicitly does NOT count module PASS as full acceptance or
label unimplemented software as a physical/provider-only blocker. Historical matrix
and source/CI evidence remain unchanged.

Changed: payment coordinator, schema v4, payment tests, earlier schema assertions,
focused workflow, execution ledger and current status/checkpoint notices. Original
legacy checkout backend/store/session/paid camera/recovery logic unchanged.
Next **PP-04.b**: authenticated backend API/client seam and persistent synthetic
provider plus real child-process restart/unknown/cancel races; then native
checkout/CCP/payment integration. Keep merchant keys server-side, validate actual
frozen media and read-only readiness through trusted adapters, preserve one service
entitlement and no unpaid output. PP-05 ticket/concurrent printer/paid Drive and
strips, PP-06 claim/exact release/health, PP-06R refund and PP-07 full physical-test
candidate/runbook are still ordinary unfinished software. Not ready for UAT.

## PP-03.c — previously delivered private CCP visibility component and evidence

Adds `PrivateCCPCard` and worker-side private QR rendering over the original
independently decoded/branded QR renderer. Concrete reuse adjustment: existing
`create_qr_image` caches recent contents/bitmaps; new explicit `cache=False` bypasses
that cache for credentials while preserving the default public-folder behavior
and the original renderer. No QR/secret bitmap is saved or logged by these tests.

The card signals the original offer only after a current attached visible QR and
full code fit the actual window. Unconstrained text height rejects clipped codes;
loading/unattached/transparent/stale cards never count as offered. Retire/detach
cancels callbacks, wipes code and QR texture, and drops the offer. Native tests
connect the actual visible callback -> original PhotoJobs -> encrypted CCP offer
journal, once, without blocking the GUI on SQLite. No payment/media/booth grant.
This component is not yet mounted in the customer checkout route: the current
private-preview launcher's payment remains disabled pending PP-04 integration.

Actual focused QR/card/CCP group **25 PASS / 0 FAIL / 0 SKIP**, 5.842s; native
private-flow/card/original QR/photo/navigation group **38 PASS / 0 FAIL / 0 SKIP**,
13.809s. New 5 native card methods cover both portrait sizes, real private QR,
shared-cache absence, invalid visibility/clipping/detach cleanup, and genuine
renderer-to-worker-to-journal integration. CCP tests also avoid printing raw
fixture proofs in failure diagnostics. Compile/diff checks PASS.

Initial unpublished card test stalled because Kivy Window.parent is itself;
reproduced explicitly and fixed by stopping ancestor traversal at Window and
rejecting cycles. That run was interrupted, not PASS. Initial native environment
also lacked optional cryptography (15 setup errors); installed the same declared
extra as clean-venv/CI and reran successfully. No runtime safety guard was relaxed.

Previous CCP journal CI 41285153968 all three jobs SUCCESS; current matching-source
CI pending push. Baseline full 1269 PASS/77 SKIP and separate opt-in 120 PASS/3 SKIP
retain their earlier worktree scope, not final PP-07 evidence. Remaining optional
model/video conditions and real OS/device/merchant gates remain explicit.

Changed: shared `qr_code.py` backward-compatible cache option, new native card,
5 new card tests, redacted-proof assertions, desktop CI optional dependency/group,
and current checkpoint notices. No default launcher, actual payment/provider,
printer, Drive or legacy paid-first transition changes. Full 112 acceptance still
NOT_RUN until complete integrated software/provider/device evidence exists.
Next **PP-04.a**: versioned purchase-group/QR1..3 attempt journal, same-order create/
404/unknown reconciliation and one service entitlement with synthetic provider
fault tests. Integrate this card as the private pre-PAID checkout step only when
provider attempt admission can require genuine CCP offer. Then PP-05 mandatory
paid Recovery Ticket plus concurrent same-ticket print and verified Drive/strips,
PP-06 safe proof/release/diagnostics, PP-06R refund, PP-07 complete candidate.

## PP-03.b — previously delivered original CCP journal and evidence

Additive **schema v3** stores one original pre-PAID CCP per frozen purchase group,
with authenticated ciphertext, scope-bound hash verifier, booth/merchant/draft/
contract identity, issuance/expiry, genuine-offer timestamp, rate window and
revocation. No raw token/QR bitmap/key sidecar in SQLite/WAL/events. Legacy paid-first
capability and 24h policy are unchanged. New policy version is explicitly pilot:
default 24h from original CREATE_PREPARED, independent issued/offered timestamps,
8 failed attempts/60s and 60s in-memory render permit. Configurable bounded values
are not signed commercial/legal terms and never extend on renewal/restart/offer.

Issue-once returns metadata only. Original decrypt is limited to an active trusted
checkout worker, using a redacted in-memory typed offer permit. Create/decrypt is
not proof of offer; only a current renderer callback may record CCP_OFFERED once.
Reboot/copied/expired/retired permits cannot do so. Slow decrypt finishing after
privacy retirement cannot resurrect a permit. Correct CCP verification returns
only typed identity metadata with media/payment authority explicitly false.
Wrong QR kind/booth/merchant/group, guessed proof, expiry, clock rollback and
revocation deny. Missing escrow row/table, corrupt ciphertext or lost key fails
closed without second-token reissue; original frozen obligation records remain.

Actual **15 CCP tests PASS / 0 FAIL / 0 SKIP** (14 initial methods plus missing-v3-
journal regression), and combined clean-venv workflow **160 PASS / 0 FAIL / 0 SKIP**,
20.209s. Includes actual encrypted DB/WAL plaintext-absence checks, exact original
recovery/expiry, duplicate offer timestamp, durable rate limit and concurrent
privacy/decrypt race. New matching-source CI pending push. Previous 41284687081
all three jobs SUCCESS; actual DPAPI exercised on Windows, unsupported behavior
on Linux. Native private-flow regression is being rerun for schema compatibility.

Broad earlier-worktree 1346/1269 PASS/77 SKIP is retained as baseline, not final
source evidence. Separate opt-in original GUI/audio group finished **123 run /
120 PASS / 0 FAIL / 3 SKIP**, 167.185s; remaining skips: two opt-in native palm
model methods and native-video opt-in/ffmpeg condition. No actual hardware proof.
These groups overlap and must not be added as unique full-suite counts.

Changed: `post_preview_ccp.py`, additive store schema, draft/checkout schema test
assertions, `test_post_preview_ccp.py`, workflow and checkpoint/current notices.
No native CCP/payment offer is mounted yet; no payment/photo/booth authority from
CCP. Full PP-033/034/038..046 acceptance remains NOT_RUN until later integration.
Next **PP-03.c**: private prepayment native CCP offer with actual render callback
and immediate token/texture cleanup, no raw QR screenshots/logs, unsupported-vault
hold and encrypted same-original restart; then PP-04 safe provider attempts. Keep
real Midtrans/Drive/print/refund activation disabled and complete remaining stages.

## PP-03.a — previously delivered protected vault primitives and evidence

`credential_vault.py`: Windows current-user DPAPI with order-scope optional entropy,
UI_FORBIDDEN, bounded envelopes, no LOCAL_MACHINE broad scope, no plaintext/key-file
fallback, allowlisted errors and ciphertext-redacted repr. Windows API buffers are
zeroed/freed after use; this is not a claim to erase every CPython in-memory copy.
Unsupported/headless Linux fails closed. Ubuntu Secret Service/TPM provisioning/
adapter acceptance is still NOT_IMPLEMENTED, not assumed safe from mock tests.

The explicitly fixture-only AES-GCM adapter uses injected in-memory test keys,
random nonces and authenticated scope. It does not persist its key or claim OS
security. `requirements-post-preview.txt` contains its optional dependency. Existing
legacy capability hash/token flow was reviewed; it remains unchanged. Typed new
CCP issuance/verifier/offer/persistence is next, not yet delivered by this primitive.
No credential is displayed or payment accepted by this increment.

Actual **7 new protector tests PASS / 0 FAIL / 0 SKIP**, including ciphertext/
wrong-scope/key/tampering rejection, bounded inputs, redaction, original recovery
with same fixture key and explicit unsupported-platform behavior. Fresh-venv
combined group **145 PASS / 0 FAIL / 0 SKIP**, 17.169s. Windows CI executes actual
DPAPI protect/unprotect/wrong-entropy tests; Linux executes unsupported behavior.
New matching-source CI pending push. Prior idle CI 41284460093 all three jobs SUCCESS.
No actual device/reinstall/key-loss or production security certification inferred.

Broad regression re-run completed **1346 run / 1269 PASS / 0 FAIL / 77 SKIP**,
316.199s. This worktree preceded the final idle/vault changes, so it is a baseline,
not final-source PP-07 readiness. Skips: opt-in original GUI/audio and optional
native palm assets; the opt-in GUI/audio group is now running separately with
synthetic camera and dummy SDL audio. Never relabel skipped scenarios PASS.
No complete PP-001..112 acceptance is established by these existing regressions.

Changed: `photobooth/credential_vault.py`, `tests/test_credential_vault.py`, optional
requirements, focused workflow and current documentation. No source credential,
real customer photo, merchant call, production config, refund or live Drive change.
Next **PP-03.b**: versioned original CCP ciphertext/verifier/TTL/rate-limit/offer
journal bound to exact frozen purchase group, with wrong-kind/booth/draft checks,
no raw token in DB/logs and no automatic decrypt/display on reboot. Then genuine
private checkout-screen offer before provider payment, preserving later PP-04..07
and unfinished claims/release/delivery/refund work. No physical-UAT readiness.

## PP-01.e — previously delivered inactivity policy and evidence

Configurable nonproduction phase policy: gallery/consent 90s; capture/review/
per-design result/all-design preview 120s; warning 15s. These are pilot engineering
recommendations, not commercial terms. A live countdown or legitimate I/O worker
extends the activity anchor rather than applying a hard total visit cutoff.
Unknown/payment states are not assigned a generic financial timeout.

The native private profile shows a warning and durably records INACTIVITY_WARNING
without cancelling/abandoning ownership. A delayed UI tick must still offer the
warning interval before privacy retirement. Customer activity clears warning;
active countdown clears it without cancellation. True inactivity expiry hides
private media and records INACTIVITY_EXPIRED, retaining local ownership unresolved;
APP_SUSPENDED and USER_CANCEL remain distinct. No financial action or FREE proof.

Actual focused native/worker/idle/original-photo/navigation group: **40 PASS /
0 FAIL / 0 SKIP**, 14.567s. Fresh-venv backend/legacy workflow: **138 PASS / 0 FAIL /
0 SKIP**, 20.215s. Initial native fixture helper incorrectly classified the
intentional warning as an error; corrected to explicitly permit only that warning,
and private hold now clears stale warning text. No failure is hidden. Compile/
diff PASS. New matching-source CI pending this push; previous private UI run
41284159506 all three jobs SUCCESS (Windows/Ubuntu private state plus native UI).

The first full-suite process lacked permitted local HTTP fixture networking and
stalled; it was terminated without a result and is NOT PASS. The permitted re-run
uses a scratch progress-only adapter over the original test runner, not changed
test semantics; final summary is still pending. Its worktree predates this idle
increment, so do not call it final-source regression without a later matching run.

Changed: new pure idle policy and tests, private App/worker warning integration,
new native warning/countdown/retirement method, workflow and current notices.
Original normal/legacy App, capture, paid service and provider files unchanged.
Next **PP-03.a**: protected OS vault interface, Windows DPAPI implementation,
explicit unsupported-platform hold, typed original CCP/hash verifier and genuine
offer journal; synthetic secure adapter for isolated fault tests. Then PP-04
payment reconciliation, PP-05 mandatory original ticket/paid delivery, PP-06
proof/release/diagnostics, PP-06R refund and PP-07 final candidate. Full PP stages
and 112 acceptance remain incomplete; no physical-UAT readiness claimed.

## PP-01.d / PP-02.b — previously delivered isolated native preview UI and evidence

The separate `PrivatePreviewApp` subclasses/reuses the original portrait App and
PhotoViews. Advertising/tutorial/gallery -> private consent -> 5-second deliberate
capture -> per-design review/retake/approval -> all-design scroll preview -> edit
and return to original gallery while preserving original lineages/quota. GUI
submission binds exact slot/revision/role/generation before worker dispatch.
Disconnected camera cancels countdown without shutter. No private compose callback
can auto-print, upload or mark paid completion. Payment remains visibly disabled.

The profile rejects payment/print/Drive opt-ins. Default/legacy launchers and
runtime modules remain unchanged. Explicit development-only launcher reuses the
original native per-checkout LaunchLease and requires isolated private storage.
[Actual commands and current limits](POST-PREVIEW-QRIS-PRIVATE-PREVIEW-DEVELOPMENT.md).
This is NOT the complete physical-UAT candidate or the final UAT runbook.

Immediate hide clears textures/private snapshots. Late worker replies cannot
reveal media after minimize/cancel; a new regression covers suspension while the
first draft creation is still pending, before its worker lease exists. The
pending lifecycle event persists after exact worker completion. Returning to Ads
from an admitted draft holds instead of fabricating booth FREE. Unresolved reboot
holds. Safe automatic release/claims and full phase-aware inactivity remain work.

Actual native group: **35 PASS / 0 FAIL / 0 SKIP**, 12.094s (4 new native methods,
8 new private-worker and 23 original photo/navigation methods). Native full
multi-design/copy-edit journey at 800x1280 and 452x900; zero payment/public output.
Eight synthetic screenshots rendered in fresh separate processes (4 per size);
both all-design screens visually inspected. Initial widget-FBO export produced
invalid black output and was rejected, not accepted as visual proof. Corrected
capture reuses native Window.screenshot plus EventLoop drawing, matching the
original renderer approach. Exact source/screenshot hashes and result limits:
[evidence JSON](evidence/post-preview-private-preview.json).

Compile/diff and launcher --help PASS. Workflow adds a separate virtual desktop
job with original dependencies, no physical devices, and fresh-process synthetic
screenshot artifacts. Previous worker CI 41283303752 SUCCESS; this source's CI
pending push. Full suite with original default sandbox stalled without progress
and was interrupted; re-run with test-ID progress and permitted local HTTP fixture
networking is underway. No full-suite PASS is claimed before its final summary.

Changed: native subclass, private worker reset/cancel facade, 4 native tests,
development launcher, synthetic renderer, focused CI, development guide/evidence
and current checkpoint notices. No customer credentials/screenshots/real media
are committed. 112 complete PP acceptance cases remain NOT_RUN.

Next: finish private phase-aware inactivity warning/retirement without active
worker/countdown cutoff; then PP-03 protected Windows vault/typed original CCP
and original offer journal, before mounting any charge or returning customer claim.
PP-04..07 and complete physical UAT deliverables remain unfinished software.

## PP-01.c — previously delivered private worker bridge and evidence

`kiosk_v2/post_preview_photos.py` supplies an internal `PrivatePhotoService` for
original `PhotoJobs`; it is NOT mounted in the application yet. It accepts
explicit BGR frame/slot/revision/role/generation commands, reuses private media
and preview adapters, returns mirrored review thumbnails, per-design review and
all-design final preview, and retains lineages/quota when editing the cart.
No service method creates a charge, freezes checkout automatically, prints,
uploads, or supplies a download QR. No ordinary flow or existing launch changes.

Immediate memory-only hide fences even a snapshot already reading images on the
I/O worker. Subsequent snapshots contain only HOLD, and worker retirement records
its distinct lifecycle without marking ownership free. Restart observes unresolved
original ownership and holds with no automatic media restoration or B admission.
Actual customer proof, camera fence/ACK and safe unattended release remain PP-06
integration work. Reuse of PhotoJobs does not imply GUI countdown integration.

Actual **8 new worker methods PASS / 0 FAIL / 0 SKIP** (1.357s); fresh-venv combined
workflow **134 PASS / 0 FAIL / 0 SKIP** (16.737s). Includes exact worker duplicate
submission test, two-design/all-preview flow, preserved retake after cart edit,
stale frame rejection, concurrent late snapshot privacy barrier and reboot hold.
Compile/diff checks PASS. Full existing-environment synthetic regression has
started; result not yet known. Prior resource CI 41283139493 SUCCESS; this worker
commit's matching-source CI pending push. Full 112-case acceptance remains NOT_RUN.

Changed: `photobooth/kiosk_v2/post_preview_photos.py`,
`tests/test_post_preview_worker.py`, focused workflow and current documentation.
Next **PP-01.d / PP-02.b**: subclass/reuse original PhotoViews and native App only
through an explicitly isolated development mode; bind capture metadata on GUI
submission, add all-design preview/edit page, fence private screens on suspend/
retirement, test native countdown/no auto-print at both portrait sizes. Keep
payable route gated pending vault/CCP, provider attempts, paid delivery and exact
machine-isolation implementation. Remaining software is not a hardware blocker.

## PP-01.b — previously delivered capture resource controls and evidence

`PrivateCapturePolicy` adds actual free-disk and bounded private-tree checks,
image decoder limits and an off-GUI fsync write probe. Nonproduction configurable
defaults: 256 MiB free reserve, 512 MiB per-draft private staging, 40 million pixels
per photo (original decoder ceiling), 4096 staging entries. These are engineering
pilot limits, not approved commercial terms or tested device capacity. Before
file save, budget decoded pixels/encoder workspace. No hard visit timer, automatic
media deletion, paid-obligation closure or machine release is introduced.

Low disk/quota/frame limits hold before image write. Existing frames remain exact;
fsync failure cleans only the just-created random probe. Retired worker leases
cannot probe or create storage. Traversal reuses checked_path symlink/junction/
archive rejection; only the current private draft is scanned, with a hard entry
bound. Real camera availability/countdown is still a GUI-worker dependency.

Actual clean-venv **126 PASS / 0 FAIL / 0 SKIP**, 14.807s, including 8 new resource
methods, 37 earlier PP backend methods and 81 original paid-first/capture/quote
regressions. Compile and diff checks PASS. Workflow includes this group. New
matching-source CI pending push. Prior preview/freeze CI run 41282882700 SUCCESS;
prior capture CI 41282667399 SUCCESS on Windows and Ubuntu.

Changed: `photobooth/post_preview_resources.py`, `photobooth/post_preview_photos.py`,
`tests/test_post_preview_resources.py`, workflow/checkpoint/current notices.
Next **PP-01.c**: original PhotoJobs/PhotoViews worker/screen bridge with explicit
camera-slot/revision callback binding, private visibility fence and all-design
final-preview routing. No new payable GUI may be enabled before PP-03..06.
112 complete PP acceptance cases remain NOT_RUN. No physical UAT readiness.

## PP-02.a — previously delivered preview/freeze implementation and evidence

Reuses the original `compose_result` (mirrored photo regions, unchanged raw/art),
`publish_output`, `record_output`, staged recovery and PNG integrity validation.
A separate immutable preview journal per exact input digest supports later
retake without overwriting the earlier preview or completing the unpaid capture
transaction. No download QR is generated and no delivery service is instantiated.
All selected designs need genuine explicit approval after their final trio.

New additive **schema v2** stores exactly one original purchase group, revision,
server-quoted IDR amount, copies, template/mask artwork identity, original final
photo hashes, lineage/retake and preview hashes. First durable `CREATE_PREPARED`
locks edits, captures and retake selection, including after lost/replayed replies
and restart. Existing prepared intent returns the exact original group/contract.
No provider call is mounted; this is not a payment integration or a PAID grant.

Typed trusted readiness observations fail closed for camera/disk/artwork/printer
route/payment transport/Drive authentication/sharing or empty unclaimed READY
capacity. This contract performs no pool reservation. Real health adapters and
observation freshness are NOT_IMPLEMENTED and must exist before any payable GUI.

Actual tests: **12 preview/freeze methods PASS / 0 FAIL / 0 SKIP**; combined
clean-venv workflow group **118 PASS / 0 FAIL / 0 SKIP**, 14.870s. Covers multiple
selected approvals, server amount/stale revision rejection, no unpaid QR,
no completion/public output, immutable replay/restart, post-boundary edit/shutter
rejection, copy requote without recapture, retake revision preview ancestry,
corrupt preview hold, lost-render-reply exact-byte recovery and v1->v2 migration.
Compile/import and `git diff --check` PASS. No full/native/physical acceptance.
Remote **PP-01.a CI run 41282667399: Windows and Ubuntu both SUCCESS** (106-test
workflow group); PP-02.a matching-source CI pending the containing push.

Changed: `photobooth/post_preview_checkout.py`, `photobooth/post_preview_store.py`,
`tests/test_post_preview_checkout.py`, schema assertions in draft tests, workflow,
this checkpoint and current status notices. Legacy runtime/GUI/transports stay
unchanged. All 112 full acceptance cases remain NOT_RUN; backend subassertions
are traceable to PP-001..007/009..016/018..020/047/055/058/063/081 only, not a
complete acceptance pass.

Next: **PP-01.b/PP-02.b** explicit capture-resource preflight and GUI worker bridge,
using original camera/countdown/screens and redacted diagnostics. Read original
GUI/camera ownership contracts before mounting. The new customer route remains
disabled pending proof/payment/fulfillment/worker integration. Do not present
ordinary unimplemented work as a physical/provider-only blocker.

## PP-01.a — previously delivered capture and evidence

`photobooth/post_preview_photos.py` reuses the original TransactionStore protocol-1
capture journal, PhotoSession, artwork contract and staged-file recovery helper.
New unpaid storage is isolated under a caller-selected private root, with one
retained lineage transaction per template. It never uses the paid Drive READY
pool, starts delivery workers, creates provider orders, prints, or calls paid
completion. Paid storage layout remains unchanged.

Three explicit original slots and one durable retake selection per template;
quota commits before any retake shutter/file I/O. Deselect/reselect, copy changes
and restart retain original lineage, photos and consumed quota. Every callback
has exact slot/role/revision/worker ownership. Duplicate/lost replies return the
original saved bytes rather than silently capturing the next slot. Fresh stale
callbacks are rejected after retirement. This is an internal trusted-worker API,
not the later customer-return proof flow.

Artwork/mask contracts are pinned by hash; updates hold the draft. Original
capture orientation is preserved. Saved JPEG hashes/path/intent/quota are checked
before restoration; known STAGED bytes recover without capture; unhashed temp or
foreign files hold without overwrite. Retention reuses the existing 15-day local
maximum for this disabled nonproduction adapter; unpaid resource cleanup/quota
and final new-order TTL policy remain work, not production-validated terms.

Tests actually run: **13 new private-capture methods PASS / 0 FAIL / 0 SKIP**,
including **10 actual abrupt child exits** (original and retake at intent,
temporary, staged, published, committed). The existing-environment first run
had one fixture assertion failure (expected no allocation directory after an
invalid slot); corrected to verify no image/shutter effect. No product guard
was relaxed. A fresh venv with exactly the workflow dependencies then ran
**106 PASS / 0 FAIL / 0 SKIP** in 10.383s:

```bash
python tools/run_kiosk_unittests.py test_post_preview_store test_post_preview_photos test_checkout_backend test_checkout_durability test_payment_quote test_workflow test_capture_journal test_photo_reconstruction
```

CI run 41282314675 at 770d318 failed on missing `cv2` in existing QR-renderer
fixtures (93 run, 0 assertion failures, 13 import-error results); Windows was
matrix-cancelled, not PASS. Workflow now installs `opencv-python-headless>=4.10,<5`
and includes private-capture tests. Fresh-venv pass verifies this actual correction;
remote CI for the containing commit is pending. No full/native/Windows/paper/
provider acceptance is inferred. All 112 full PP acceptance scenarios remain
NOT_RUN; these are backend subassertions for PP-001..007/009/010/063 only.

Changed this increment: `photobooth/post_preview_photos.py`,
`tests/test_post_preview_photos.py`, `tests/post_preview_crash_fixture.py`, focused
workflow and this checkpoint/current handover notices. Original shared capture,
legacy recovery, printer, Drive, payment and GUI modules are unchanged.

Exact next action: **PP-01.b/PP-02.a** — integrate a private all-template review/
approval adapter and immutable media/artwork quote boundary, then GUI worker/
countdown bridge. Validate camera/disk/resources, private preview and no compose
completion or auto-print. PP-01 is not complete until actual GUI admission,
countdown/camera fencing and resource controls exist. Do not skip this to enable
payable QRIS. No customer GUI/launch candidate/runbook is ready yet.

No local-only application changes intentionally remain after this micro-commit;
disposable test logs/clean venv are `/workspace/work`, not committed artifacts.

## PP-00.a — previously delivered foundation

- Clean local checkout now tracks the existing authorized GitHub branch and
  exactly matched the base before edits. The environment initially had only a
  `work` checkout and a master-only fetch refspec; no other branch was modified.
- Network initially failed within the command sandbox. Using the execution
  tool's network-enabled permission profile fixed fetch without changing proxy
  configuration or weakening TLS. Use that profile for future fetch/push.
- New independent `post_preview_v1` SQLite WAL/FULL ledger; additive schema
  version, local owner/generation, optimistic cart revision, durable lifecycle
  events and persistent per-template lineage. No legacy record migration.
- New-order 1..9 copy quote uses original pricing. Legacy backend 1..10 stays
  unchanged. No extra session for extra paper copies.
- Cancel, suspend, inactivity expiry and classified abandonment persist distinct
  events and fence the old generation. A warning alone leaves ownership intact.
  No event fabricates booth FREE, financial cancellation or a release ACK.
- Focused Linux/Windows CI for this branch; documentation-only pushes skip CI.
  No production configuration, GUI routing or transport is enabled by this work.

Changed paths: `photobooth/post_preview_store.py`,
`tests/test_post_preview_store.py`, `.github/workflows/post-preview-qris.yml`,
this checkpoint and linked notices in `docs/DEVELOPMENT_HANDOVER.md`,
`docs/FEATURE_STATUS.md`, `docs/next_step.md` and PP Codex handover.

## Actual source audit / dependency order

Baseline source inspected at b68e514: `kiosk_v2/photos.py` automatically marks the
last composed transaction complete and can notify Drive; `photo_views.py` owns
auto-print. Never route an unpaid draft through that completion/delivery path.
Reuse `TransactionStore(capture_protocol=1)`, `capture_journal` immutable JPEG/
PNG publication and `PhotoSession` slot/retake semantics behind a private adapter.
`photo_recovery.reconstruct` is currently bound specifically to legacy PAID
contracts; unpaid reconstruction needs an explicit new versioned adapter.
`payment_quote.quote_checkout` accepts 10; gallery caps 9. Use the new versioned
quote rather than changing existing paid contracts. Existing backend journals,
provider evidence and AR ownership/release remain the later integration seams.

Reviewed current contracts: root `AGENTS.md`, documentation index/protocol/current
handover/status/backlog, complete PP decision ledger, owner-approved flow,
refund/proof-loss and operator escalation policies, security/state specification,
112-case acceptance matrix, PP handover, consistency audit and Midtrans provider
contract. Historical source/CI/device results remain scoped to their original
versions. PP-00 source audit is not yet complete for all later integration seams;
read affected AR/UAH/UX-07/BUG-026..028/Drive/printer contracts before changing them.

## Tests actually run

Linux Python in existing `.venv`, synthetic fixtures only:

| Command | PASS | FAIL | SKIP | BLOCKED | NOT_RUN |
| --- | ---: | ---: | ---: | ---: | ---: |
| `python -m unittest tests.test_post_preview_store -v` | 12 | 0 | 0 | 0 | 0 |
| `python tools/run_kiosk_unittests.py test_checkout_backend test_checkout_durability test_payment_quote test_workflow test_capture_journal test_photo_reconstruction` (base) | 81 | 0 | 0 | 0 | 0 |

Exact configured CI group additionally executed locally: **93 PASS / 0 FAIL / 0 SKIP** (8.400s), including all 12 new plus 81 legacy tests. CI dependency inspection added NumPy, which the existing photo-reconstruction fixtures require. First attempted push was rejected by automatic approval review; the owner then explicitly approved branch pushes in chat. Local foundation commit is `b15b29016af78c44c2a0702739521c4a2379f785`; this companion CI correction is being pushed with it. CI is pending first implementation push. No full regression or native GUI run yet.
**PP-001..112: 112 NOT_RUN as complete acceptance scenarios**; model subassertions
do not imply capture, payment, claim or physical acceptance. No new source/UI
integration is inferred from the historical 81-test legacy baseline.

## Remaining roadmap (PP-00 historical next action below is superseded by PP-01.a above)

Next **PP-01.a**: private media adapter over the original capture journal. Persist
three originals and one durable per-template retake; pin artwork, recover exact
saved bytes, preserve lineage through deselect/reselect and restart, reject stale
worker callbacks, and never print/upload/complete an unpaid transaction. Add
focused synthetic JPEG/crash tests, then update this checkpoint and micro-push.
PP-00 remaining source-seam audit progresses with dependency-specific work.

Then PP-02 all-design preview/freeze/readiness, PP-03 vault/CCP, PP-04 reconciled
attempts, PP-05 mandatory concurrent ticket/paid Drive and print, PP-06 original
claim/exact isolation/diagnostics, PP-06R refund state, PP-07 native end-to-end,
regression/package/Windows launch/runbook/112-case actual evidence.

Known limits: the ledger is an internal trusted-worker API, not customer
authentication; its owner row is not backend machine occupancy. There is no
proof-gated restart, safe local close, media capture, checkout or customer GUI
integration yet. Never expose its inspect API to untrusted callers. No hardware,
Midtrans merchant, Drive, vault or refund activation acceptance is established.
No ordinary unimplemented software requirement is labeled a hardware blocker.

## Exact resume commands

```bash
cd /workspace/PhotoBooth
git status --short
git branch --show-current
git fetch origin refs/heads/feature/post-preview-qris-checkout:refs/remotes/origin/feature/post-preview-qris-checkout
git rev-parse HEAD origin/feature/post-preview-qris-checkout
git log -5 --oneline
cat docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md
source /workspace/.photobooth-cloud/activate.sh
python -m unittest tests.test_post_preview_store -v
```

Fetch/push require the execution tool's network permission profile in this cloud
session. If the remote advances, inspect before editing; do not merge/rebase/reset
or force-push. Preserve unrelated work. No local-only application changes are
intentionally left outside the containing micro-commit. Disposable audit/test
scratch exists in `/workspace/work`, outside the repository, and is not a backup.
