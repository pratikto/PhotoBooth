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
- Last independently verified remote: `501254f210a596ce45d8181f35d5a0e7df998f8d` (PP-01.b resources; verified remote, CI run 41283139493 SUCCESS).
- Original audited base: `b68e514dd57c989df47fa1b222d45f3f71c38347`.
- Current micro-increment: **PP-01.c — original PhotoJobs private workflow facade**.
- Overall: PP-00 dependency audit continuing; PP-01 backend capture implemented, GUI NOT_IMPLEMENTED; PP-02 backend boundary implemented, real readiness adapters/GUI NOT_IMPLEMENTED; PP-03..07 NOT_STARTED.
- This checkpoint travels with the implementation commit. Resolve its containing
  SHA using `git log -1 --format=%H`; after push independently compare `git
  ls-remote origin refs/heads/feature/post-preview-qris-checkout`. A commit cannot
  truthfully contain its own SHA. The next increment records this verified tip.

## PP-01.c — current private worker bridge and evidence

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
