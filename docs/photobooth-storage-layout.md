# FEAT-004 ads + BUG-009 — booth storage and shared content

Owner-requested target, **26 October 2026 (Asia/Jakarta)**. Audited source:
`19e3f4d4f0b4148b5daba6d25f6b5fe0387a4802` on
`feature/portrait-kiosk-v2-next`; functional mirror source remains `fc26e3d`.

**Status: implementation in progress after the owner explicitly requested application and Code.gs changes.**
The initial audit remains available; [staged implementation evidence](qa/feat-004-storage/README.md)
records what is actually delivered versus not yet wired/deployed.

Owner clarification: this foldering/offline-cache request belongs to the
coordinated **FEAT-004 ads + BUG-009** workstream. The per-booth layout, 25-slot
reserve, `Photo/NN/raw,color,bw`, asset sync and retention are shared integration
work, not unrelated new features. Earlier retention-only source repairs did not
implement asset sync; this linkage does not retrospectively claim they did.

| Responsibility | Scope in this workstream | Acceptance |
| --- | --- | --- |
| FEAT-004 ads/content | Root global ads/templates, booth-specific assets, complete verified local caches and offline playback/catalog snapshots | Every booth uses cached content offline; invalid/partial updates retain the last working version |
| BUG-009 photo retention | Registration, owning-account hourly cleanup and 15-day local/30-day Drive deadlines over the new photo paths | Actual authorized synthetic expiry/deletion evidence; source tests/READY alone do not close the bug |
| Shared storage/backend | Booth parents, 25 READY directories, session/raw/color/bw paths, counters, deferred upload/QR and existing Apps Script protocol | No ID reuse, cross-booth mix, duplicate print, expired-photo revival or deletion of assets/READY slots/`old` |

Implement and review these together before switching an operational root or
deployment. Keep evidence separate: successful content sync does not certify
photo deletion, and successful retention setup does not certify asset sync.
The actual Google Drive account was not accessible/configured in this workspace.
Source inspection and isolated fixtures describe code behavior, not the installed
Drive tree. No folders in an account were created, moved, deleted or synchronized.

`old` is an excluded archive: do not inspect its contents, import assets/code
from it, migrate it, change it or include it in discovery, sync or retention.
This rule applies before descending a directory or resolving a shortcut/link.
[Audit evidence](qa/storage-layout-audit-2026-10-26/README.md).

## Requested Drive tree

The two global folders are root siblings of `Photobooth`, not customer-photo
subfolders. IDs below are examples; confirm/configure real parent IDs rather
than relying on globally unique Drive folder names.

```text
Drive root/
├── Global_Advertisement/
├── Global_Template/
└── Photobooth/
    ├── PB001/
    │   ├── Local/
    │   │   ├── Advertisement/
    │   │   └── Template/
    │   ├── PB001_00000001/          # READY: genuinely empty until claimed
    │   ├── PB001_00000002/
    │   └── ...                    # target at least 25 READY transactions
    ├── PB002/
    │   ├── Local/Advertisement/
    │   ├── Local/Template/
    │   └── ...                    # independent transactions/25 READY slots
    └── PB00X/
        └── ...
```

`Local/Advertisement` and `Local/Template` are booth-specific content, distinct
from the shared global sources. Folder names under `Local` are the proposed
concrete spelling for the owner's unspecified local-asset subfolder names.
Keep booth/global asset parents private; retain transaction-specific download
sharing rather than publishing the entire booth parent and other visitors.

After a READY transaction is claimed, create only its actual session directories:

```text
PB001/PB001_00000001/
├── manifest.json
└── Photo/
    ├── 01/
    │   ├── raw/
    │   │   ├── photo_01.jpg
    │   │   ├── photo_02.jpg
    │   │   ├── photo_03.jpg
    │   │   └── retake.jpg          # if the allowed retake was used
    │   ├── color/
    │   │   └── strip.png           # approved RGB composition, before dithering
    │   └── bw/
    │       └── strip.png           # exact final 1-bit printer raster
    └── 02/
        ├── raw/
        ├── color/
        └── bw/
```

`01 ... 0X` follows session order, **not paper-copy count**. A×2 + B×1 remains
two three-photo sessions and three copies; a retake adds raw history within its
session. Keep stable internal session IDs (`session_001`, etc.) and map them to
`Photo/01` instead of replacing payment/print journal identities.

Raw camera JPEGs remain full-resolution originals. V2 `color/strip.png` contains
the already-approved mirrored photo areas, with normal artwork/text/QR. Save
the final native-width 1-bit raster in `bw`, using the existing printer profile;
do not dither twice or add laboratory comparison headers to customer strips.
One saved raster can serve N copies without extra capture sessions. For example,
the audited 640×1920 RGB master becomes a 576×1728 raster on that printhead;
do not change physical print width/tuning merely to reorganize folders.

## Local disk and offline copies

Keep operational data **outside the source checkout**, for example:

```text
C:\MeongData\Photobooth\PB001\
├── Local\
│   ├── Advertisement\
│   └── Template\
├── Cache\
│   ├── Global_Advertisement\       # local copy of shared ads
│   └── Global_Template\            # local copy of shared template packs
├── _state\                        # private counters, pool/queue, sync versions
├── PB001_00000001\                 # READY: empty
├── PB001_00000002\
└── ...
```

Each physical booth needs its **own** global-content cache and local assets;
it does not need copies of other booths' customer photos. `Cache` and `_state`
above are local implementation directories, not extra global folders to upload.
Never place a `Photobooth` data directory beside the Python package `photobooth`
inside the checkout: these names collide on case-insensitive Windows filesystems.

Every required global asset must finish downloading and validating before its
version is active. Existing verified local copies continue working offline.
A file never downloaded cannot be available offline: first installation needs
an initial sync or approved local seed, retaining the working bundled fallback.

## Source audit: current behavior versus target

| Area | Current active source | Required change |
| --- | --- | --- |
| Booth roots | V2 uses `data/kiosk-v2-p3/photos`; test identity defaults to `PB001V2`. Cloud transactions are direct children of the configured parent | Explicit per-booth data/Drive parent. Do not strip test suffixes or mix v1/Sandbox counters just to match display names |
| Ready pool | Shared v1 pool defaults to 25, but v2 overrides it to **2**; empty local staging is `photos/.pool/<Drive-folder-id>` | At least 25 preallocated READY transaction directories per booth, with stable IDs and a durable external ledger |
| Sessions | `raw/session_001/*.jpg`, `output/session_001.png` | Versioned mapping to `Photo/01/raw`, `color`, `bw` |
| RGB/BW | RGB composition saved; printer renders a 1-bit bitmap in memory and builds ESC/POS bytes | Persist the exact final raster once, then use those same pixels for the print batch |
| Offline uploads | Cached verified Drive slots can be claimed offline. Explicit Drive mode blocks a new visit if none are ready. `LOCAL_ONLY` is not automatically rebound later | Define the empty-cache fallback and explicit deferred-Drive transaction state before promising later upload/QR |
| Advertising | Local playlist plus optional project `ad_video` discovery; external local playlist path already supported | Feed existing player validated local snapshots of global + booth-specific content |
| Templates | Twelve bundled approved designs loaded through `catalog.py` | Validated versioned global/local packs; preserve working twelve-design fallback and old transaction references |
| Global sync | No active implementation of the two requested global sources/caches | Bounded background download, verification, atomic activation and offline fallback |
| Retention | Local cleanup knows `raw`/`output`; cloud adoption recognizes that old active hierarchy and direct parent transactions | Cover new `Photo/*/{raw,color,bw}` and booth parents before cutover, protecting assets, READY slots and `old` |

These findings do not prove how an operator has manually arranged Drive. For
example, today's configured parent could already be a manually created PB001;
the code does not itself establish the complete requested hierarchy.

Reviewed active paths: [transaction store](../photobooth/transaction_store.py),
[v2 photo adapter](../photobooth/kiosk_v2/photos.py), [pool](../photobooth/drive_pool.py),
[sync worker](../photobooth/drive_sync.py), [printer](../photobooth/printer.py),
[local ads](../photobooth/advertising.py), [template catalog](../photobooth/catalog.py),
[Apps Script](../apps_script/Code.gs) and [local retention](../photobooth/retention.py).
Their audited hashes are retained with the evidence.

## Durability and content rules

- A READY transaction is physically empty. Keep readiness metadata outside it;
  create `manifest.json` and `Photo/NN` only after an atomic claim. Advance the
  durable booth counter before reuse is possible; interrupted claims must recover.
- Refill toward at least 25 READY slots when online. Twenty-five cached Drive
  slots are finite capacity, not a guarantee of unlimited offline Drive URLs.
  Missing/failing remote verification must not discard existing assignments.
- **Owner-selected empty-pool behavior:** continue local photo/print even when
  Drive is offline and the 25 reserves are exhausted or never synchronized;
  upload and download QR follow after reconnection. This is the approved target,
  not current v2 behavior or a performed cloud operation.
- Record explicit Drive intent for that fallback, e.g.
  `PENDING_DRIVE_BINDING`, separately from deliberate `LOCAL_ONLY`. Bind the same
  booth/transaction ID idempotently on reconnect **before** replenishing remote
  IDs; reconcile server/local high-water marks. Never attach a visitor to another
  ready folder, replay a print, or upload an originally local-only visit silently.
- A previously verified reserved folder can supply a stable QR destination while
  its upload waits. With no known Drive destination, printed paper must clearly
  show download pending, not a fabricated working QR. After binding/verification,
  expose the real QR separately through transaction retrieval; never rewrite the
  original color/BW file used to print or automatically print the sheet again.
  A stable pre-upload QR resolver would be a separate backend/deployment feature.
- Keep queue/counter/journal/config state private and outside customer-download
  content. Preserve original transaction UTC timestamps and 15-day local/30-day
  Drive deadlines even across offline binding; READY-folder age is not photo age.
- Sync global and booth-local assets into separate namespaces. The proposed
  default is shared content plus explicitly enabled local additions, not silent
  replacement of a global file solely because its basename matches.
- A template pack includes artwork, layout/three-aperture masks, QR geometry and
  stable IDs/version hashes, not just PNG files. Validate before activation; pin
  the selected version for an entire visit so sync cannot change an active strip.
- Download to a staged generation, check hashes/sizes/media/layout, then atomically
  activate the complete snapshot. Keep the last verified version on network loss,
  partial download or invalid media. No network/decode bulk work on the GUI thread.
- Reuse existing player/compositor/printer and durable workers. New global asset
  reads do not authorize arbitrary Drive writes, ad pricing, new gameplay,
  production payment/scanning, deployment or deletion.
- `old` is excluded from every traversal/sync/cleanup/cutover. Seed counters from
  trusted active state/ledgers outside the archive, not by scanning `old`.

## Staged implementation and acceptance

| Stage | Concrete work | Evidence before cutover |
| --- | --- | --- |
| 1 | Versioned booth path resolver/state plus 25 empty local reserves | Temporary PB001/PB002 isolation, unique IDs, restart/atomic claim, no `old` access |
| 2 | Integrate `Photo/NN/raw,color,bw` with capture/retake and native raster persistence | Raw hashes/resolution, mirrored color, exact 1-bit print pixels/copies, no duplicate send |
| 3 | Per-booth Drive binding/pool and matching retention scope | Offline cache/exhaustion, reconnect without ID/QR changes, no replay, original deadlines and protected assets |
| 4 | Global/local content download and cached catalog snapshots | Every booth has complete local assets; interrupted/invalid updates retain prior media/template version |
| 5 | Native GUI/operator wiring and Windows/Drive acceptance | Responsive GUI, correct current storage observations, real paper/QR/offline evidence and explicit cloud setup |

Do not switch existing paths or redeploy Apps Script by renaming folders alone.
The current upload protocol already carries relative paths, but manifest, pool,
queue, retention, raster and asset-catalog integration all need coordinated
source changes. Existing `old` and customer data remain untouched by this audit.
