# FEAT-004 ads + BUG-009 — implementation checkpoints

Owner explicitly requested application **and Code.gs implementation** after the
foldering audit. Base **504c6cc9451e652da56ebe8e62a287891bef31a6** on required
`feature/portrait-kiosk-v2-next`; source stays on this branch. Exclude all `old`
contents from reads/writes/discovery/sync/retention. No cloud credentials or
Google connector is present; source/fixture verification is not live deployment.

Approved target/constraints: [storage contract](../../photobooth-storage-layout.md).
Local photo/print continues without Drive or a ready remote slot; upload and real
QR follow reconnect, without rewriting printed images or replaying prints. Keep
v1 defaults and Sandbox isolation, existing renderer/printer/Drive workers,
immutable deadlines, correct QR/art and full-resolution original JPEGs.

## Delivery sequence

1. Local per-booth roots, 25 empty reserves, atomic claims/counters; versioned
   session paths and exact BW render/send separation; local retention paths.
2. Code.gs per-booth roots/reservation/binding, isolated global/local content
   read protocol, matching retention; original client/queue adapters and tests.
3. Background content cache plus native ordinary-launcher/profile wiring;
   offline fallback/retake/print/result/QR lifecycle using these paths.
4. Final complete regression, required native screenshots, CI and Windows/setup
   package. Publish source and evidence separately; no real setup/deletion here.

## Stage 1 — foundation

`BoothWorkspace` uses the original atomic writer/counter/store with per-booth
private ledger and process lock. It prepares 25 genuinely empty transaction
directories locally, atomically claims/refills without network and checkpoints
active counters outside `old`. Versioned store paths use Photo/NN/raw,color,bw;
v1's default layout remains unchanged. Retention handles the new Photo subtree
without traversing archives or deleting asset/cache/reserve folders.

The calibrated production printer render is extracted unchanged to `render_image`;
`print_raster` sends saved 1-bit pixels through the original single-batch/route/
uncertainty handling, without another resize/dither or lab header. The new
foundation is not yet mounted in the ordinary GUI at this checkpoint.

Final focused [stage-1 checks](stage1-tests.txt): **70 PASS / zero failures/errors/skips**,
covering new roots/reserves/restart/isolation, original store/pool/retention,
original transports and saved-raster no-double-dither behavior. Windows CI also
executes the new storage fixtures to check the Windows lock implementation.

Rollback: scoped inverse source changes after inspection. Keep active/previous
counter ledgers, transaction/photo/print/payment state and content; never clear
an uncertain outcome or touch `old`. No source push is a Drive deployment.

## Stage 2 — backend and reconnect adapters

Code.gs now supports manual sibling-root setup, isolated physical booth roots,
empty READY reservations and idempotent offline binding with an ownership digest.
The private local claim token never enters the public manifest. Bound folders
have Photo/NN/raw,color,bw and a safe manifest. Legacy API defaults stay available.
Storage identity PB001V2S2 maps to physical PB001, avoiding ID reuse with legacy
PB001V2 server leases; no legacy/archive counters or transactions are scanned.

Layout-2 client/worker reuses AppsScriptDriveClient, original file verification,
manifest revision merges, immutable retention registration and worker lifecycle.
Missing network/timer never prevents a new local claim and never replays print.
Retried controller saves preserve newer remote bindings. The content API inventories
only four configured source roots and reads checksum-bound 512-KiB ranges.

Cloud cleanup scopes registered booths, protects reserve/assets/archive content,
uses original transaction deadlines even when folders were created on late reconnect,
and validates known descendants before permanent deletion. With the new root enabled,
the legacy upload parent is excluded from this sweep; no migration is inferred.

Focused evidence: [Python 34 PASS / zero skips](stage2-tests.txt),
[actual Code.gs VM 24 PASS / zero skips](stage2-codegs.txt). Fixtures include
25 empty reserves, independent booths, binding retries/conflicts, bytes verification,
archive pruning, range isolation and retention guards. No Google deployment/test.
The ordinary GUI/cache integration follows in stage 3.

## Stage 3 — ordinary GUI integration and atomic content cache

Ordinary `tools/run_portrait_v2.py` defaults to layout 2; dedicated merchant
Sandbox explicitly remains on its prior isolated layout/transports-off profile.
The source reuses v1's original template renderer, ad catalog/player, calibrated
printer, upload verification and durable journal/worker lifecycle. It does not
replace the game or move v1/main.py/master. [Windows + manual Apps Script setup](SETUP.md)
includes the [12-item offline Submit form](windows-checklist.html).

Per-booth local admission no longer depends on Drive. Actual reserved folder
IDs/URLs are cached in the private ledger; unreserved offline visits explicitly
record deferred Drive intent. Reconnect binds the same ID/original clock before
upload and remote reserve refill. Deliberate LOCAL_ONLY never silently uploads.
Original JPEG captures/retake, mirrored-photo color strip and exact final 1-bit
BW raster occupy Photo/NN/raw,color,bw. Print uses the saved BW pixels through
the original batch/uncertainty guard. No reconnect changes existing strip bytes
or replays a print; real on-screen QR follows full file verification.

ContentCache downloads all four namespaces using checksum-bound chunks, validates
complete original-schema packs, rechecks the inventory and atomically replaces
one private pointer. Per-booth version directories keep prior assets intact.
Existing bundled/manual booth content works before initial sync; verified cache
works offline. A native GUI reference swap occurs only at idle; active visitor
selections are pinned. The existing player/audio lifecycle and default twelve
original designs remain available. MOCK quote/template IDs stay isolated.

A broad GUI run exposed a legacy retake regression: the new background-binding
merge initially copied a persisted null folder over v1's controller assignment.
The fix scopes binding merges to layout-2 manifests with an actual folder.
The original v1 same-filename-retake test now passes alongside the new offline
and reconnect tests. Intermediate failed/skipped runs are not final acceptance.
Browser file:// navigation is blocked by this environment's browser policy;
the same offline form was tested over a loopback-only static server instead.

Focused evidence: 42 integration/service tests, 13 merge/native handoff tests
(including the original failed retake), 11 configuration/diagnostic tests and
24 actual-Code.gs VM tests pass with zero failures/errors/skips. The
configuration test covers first-offline missing credentials and proves layout 2
does not fall back to the legacy OAuth parent. Final full regression and clean
source screenshots are recorded below when complete, not inferred from these
focused checks. A verified 12-item browser test covers empty checks, safe metadata
import, partial Submit, local persistence/download and 360/452/800px overflow.

Live limits remain: no Apps Script deployment/root creation/trigger activation,
real Drive file sync/expiry, phone QR or physical paper was performed here.
BUG-009 therefore remains OPEN for actual deletion evidence. Content-cache
old generations are intentionally retained; capacity maintenance needs a
separate operator policy, not photo-retention deletion.

Final stage-3 [full local suite](full-tests.txt): **823 PASS / zero failures,
errors or skips**, 224.496s, with original-v1 GUI, native video/audio and real
public palm-model fixtures enabled. The additional missing-credentials test was
added after full-suite discovery and passed in the recorded 11-test configuration
suite; no later runtime change was made. [Exact tested code hashes](tested-source.json).
This is synthetic/provider-fixture evidence, not physical Windows acceptance.
