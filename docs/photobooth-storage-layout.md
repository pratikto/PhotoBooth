# FEAT-004 + BUG-009 — customer photo storage

Updated 26 October 2026 (Asia/Jakarta) after the owner's actual Drive/QR failure.
This correction supersedes the earlier transaction-root / Photo/NN cloud tree.
The owner explicitly requires the following **Google Drive** tree:

```text
Drive root/
├── Global_Advertisement/
├── Global_Template/
└── Photobooth/
    └── PB001/
        ├── Local/Advertisement/
        ├── Local/Template/
        └── Photo/
            ├── 00000001/
            │   ├── raw/
            │   ├── bw/
            │   ├── color/
            │   └── manifest.json
            ├── 00000002/
            └── ...
```

At least 25 genuinely empty numbered reserves belong beneath each booth's
`Photo`, before claim. The raw/color/bw directories appear only after binding.
The download QR points at `Photo/00000001`, not PB001 or an asset directory.
Numbering uses the durable transaction suffix. Internal `PB001V2S2_00000001`
identities remain in private counters/claims/journals; they are not the new
Drive folder names. Never reset counters to get back to 00000001.

All sessions in one transaction share these three directories. Prefix filenames
with their stable session ID to avoid overwriting another design's files:
`raw/session_001_photo_01.jpg`, `raw/session_001_retake.jpg`,
`color/session_001_strip.png`, `bw/session_001_strip.png`.
Paper-copy quantity does not create more capture sessions or folders.
Original JPEGs stay full resolution/unmirrored, color photo areas mirror as
approved, and BW remains the exact once-dithered printer raster.

The existing private **local** workspace, manifests and upload-relative paths
are preserved for recovery. BoothDriveClient translates local
`Photo/01/color/strip.png` to remote `color/session_001_strip.png` while reusing
original checksum/size verification. This change does not relocate local data.
Complete verified global/local content caches remain per booth and offline-safe.

## QR and delivery invariants

- Never publish the booth/Photo/assets parent. Only an individual numbered
  customer folder receives Anyone with the link / Viewer.
- Reserve and bind responses must acknowledge the numbered layout and actual
  sharing verification. Python rejects older/private responses before composing
  a new QR. Previously cached unverified reserve URLs are withheld.
- Result-screen QR appears only after all saved bytes are verified in Drive.
  Automatic physical printing remains independent of network availability.
- A missing folder URL produces download-pending paper, never a fabricated QR.
  Existing printed pixels are never rewritten and prints are never replayed.
- Binding/setup failures persist a safe error category for the result GUI;
  retention failures retain the existing upload hold and operator message.

## Recovery and retention

The backend can recover an **exact claimed, empty, app-owned** legacy reserve
from the same booth parent into Photo and rename it to its numeric suffix.
The claim digest must match. Folder ID and any printed QR URL remain identical.
A retry after interrupted move/rename finds the same folder. Foreign, ambiguous,
nonempty or mismatched folders stop for operator review. No broad migration,
archive scan, automatic deletion or unrelated asset cleanup is performed.

The 15-day local and 30-day Drive deadlines remain based on the original
transaction time. Numbered-cloud cleanup validates the stored internal identity,
physical booth, numeric suffix and exact retention marker before deletion;
READY reserves and unrelated content have no valid expiry authorization.
BUG-009 remains OPEN until installed-account expiry evidence is supplied.

`old` is excluded before descent from every inspection/sync/cleanup. V1 and
merchant Sandbox retain their existing profiles. Global/Local content behavior,
payment, printer transport and game behavior are outside this correction.

## Source versus live account

The 26 October read-only Meong Drive inspection found
`Photobooth/PB001/PB001V2S2_00000003` empty, with no anyone-reader permission;
PB001 also contained Photo plus legacy/local asset naming variants. No contents
of old were read. No live folders, permissions or scripts were changed.

The corrected source and fixture tests do not update an existing Apps Script
Web App deployment. Follow [repair setup](qa/drive-photo-layout/README.md).
Do not mark live upload/phone scanning or actual cloud deletion PASS from source tests.
