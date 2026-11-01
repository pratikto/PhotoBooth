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
- Last verified remote base: `b68e514dd57c989df47fa1b222d45f3f71c38347`.
- Current micro-increment: **PP-00.a — private versioned draft foundation**.
- This checkpoint travels with the implementation commit. Resolve its containing
  SHA using `git log -1 --format=%H`; after push independently compare `git
  ls-remote origin refs/heads/feature/post-preview-qris-checkout`. A commit cannot
  truthfully contain its own SHA. The next increment records this verified tip.

## Completed in this increment

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

CI: pending first implementation push. No full regression or native GUI run yet.
**PP-001..112: 112 NOT_RUN as complete acceptance scenarios**; model subassertions
do not imply capture, payment, claim or physical acceptance. No new source/UI
integration is inferred from the historical 81-test legacy baseline.

## Remaining and exact next action

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
