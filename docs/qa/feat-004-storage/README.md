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


Final UI review follow-up: cache activation now also waits for the original
Device Health panel to close; an idle page with an operator overlay must not be
rebuilt behind the operator. This is a single native guard, with the existing
cache-pinning test extended. The full 823-test run above is at bf9be57, before
this final guard. Subsequent native/CI results are recorded separately rather
than claiming the earlier full suite ran on a later source.

Guard follow-up checks: 57 native cases ran, **55 PASS, two optional cases
skipped** in that invocation; both skipped real-palm/native-audio cases then ran
separately with their assets/flags, **2 PASS / zero skips**. See
[operator/cache native run](operator-cache-tests.txt) and
[explicit native supplement](extra-native-tests.txt). No layout/geometry changed.

## Final source — 53e7b4c16650feb46e3ecb1e0645a11c316da763

The final guard is now also covered by a complete matching-source run:
[**824 Python PASS / zero failures, errors or skips**](head-full-tests.txt),
241.156s; 24 actual-Code.gs VM PASS. Original-v1 GUI, native video/audio and
public real-palm model fixtures were all enabled. [Final code hashes](tested-source-head.json)
separate this result from the earlier bf9be57 run. The actual ordinary launcher
also cold-booted a temporary layout-2 profile: advertising first, 25 empty READY
folders, printer/Drive disabled ([smoke outcome](launcher-smoke.json)).

Matching-source [CI 40273343183](https://github.com/pratikto/PhotoBooth/actions/runs/40273343183):
all **three jobs SUCCESS**. [Run result](ci-result.json) ·
[artifact/source verification](ci-verification.json). The 133 CI PNGs and 14 clean
source reports were checked; delivery 76, Sandbox 139 and health 80 report no
failures/errors/skips. Native CI reports 107 cases with one optional palm-assets
skip; the complete local run above includes and passes that real-model test.
Windows CI uses dummy PCM, so successful audio loading is not speaker acceptance.

[Final screenshot verification](screenshot-verification.json): 28 native PNGs at
800×1280/452×900, source SHA, clean tracked tree, dimensions, nonblack pixels and
SHA256 verified; two browser form views also published. Gallery and settled
result were visually reviewed at both sizes, plus both form views. Additional
advert/consent views were reviewed at bf9be57; the later guard changed no geometry.

A preliminary 800px Window readback still showed the preceding review frame.
That preliminary capture is replaced, not counted as a correct result. The
[reproducible QA driver](strict-render-driver.py.txt) reuses the original P3
recorder/actions, waits for the expected photo phase and exports actual native
Widget FBOs after layout settles. No application or image pixels were edited.
Each of the 16 P3 frames records its verified phase; the gallery/advert captures
use the original recorder. [Browser checks](browser-tests.txt) prove Submit does
not automatically pass unchecked tests; fixture-imported metadata/one synthetic
check in the form pictures is not a Windows observation.

| View | 800×1280 | 452×900 |
| --- | --- | --- |
| Gallery | [PNG](screenshots/04-templates-800x12800001.png) | [PNG](screenshots/04-templates-452x9000001.png) |
| Offline result | [PNG](screenshots/06-local-result-800x12800001.png) | [PNG](screenshots/06-local-result-452x9000001.png) |
| Test form | [PNG](screenshots/windows-form-800x1280.png) | [PNG](screenshots/windows-form-452x900.png) |

Checkpoints: 76bb9a0 foundation → 6e2f777 backend → bf9be57 integration →
53e7b4c operator-overlay guard/final runtime. All were pushed to the required
branch and remote HEAD verified. This subsequent evidence-only publication
uses skip-ci and changes no runtime. Rollback rules and exact Windows/Code.gs
steps are in [SETUP](SETUP.md); preserve all counters, journals, original files
and archive exclusion. Never infer a new print/charge from a recovered queue.

Remaining acceptance: Apps Script/manual root/timer deployment, actual global
sync on each physical booth, live 30-day permanent deletion, phone QR and paper.
No Google credentials/connector was available here; **BUG-009 stays OPEN** until
actual authorized deletion evidence. FEAT-004 is implemented/tested in source,
with real-account acceptance pending. There is no newly known automated/native
layout failure after the corrections above. No production payment/scanner/game
integration, master/default/merge or archive changes occurred.
