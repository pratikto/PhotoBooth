# Post-preview QRIS implementation checkpoint

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
- Last independently verified remote: `b8655adb834c9b2e612458ba5b46a8cc45e6d8ef` (PP-03.c native private card; verified remote, CI run 41286019681 all three jobs SUCCESS).
- Original audited base: `b68e514dd57c989df47fa1b222d45f3f71c38347`.
- Current micro-increment: **PP-04.a — purchase-group/QRIS attempt coordinator and synthetic financial races**.
- Overall: PP-00 dependency audit continuing; PP-01 private capture and isolated development UI implemented; PP-02 preview/freeze backend and all-design UI implemented, real charge-readiness adapters NOT_IMPLEMENTED; PP-03..07 NOT_STARTED.
- This checkpoint travels with the implementation commit. Resolve its containing
  SHA using `git log -1 --format=%H`; after push independently compare `git
  ls-remote origin refs/heads/feature/post-preview-qris-checkout`. A commit cannot
  truthfully contain its own SHA. The next increment records this verified tip.

## PP-04.a — current purchase/attempt coordinator and evidence

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
