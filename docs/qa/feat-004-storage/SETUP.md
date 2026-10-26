# Booth storage v2 — setup and Windows retest

Source on `feature/portrait-kiosk-v2-next`. This document is not evidence that
Google setup, actual deletion, phone download or paper printing has happened.
Use the [12-item offline Submit form](windows-checklist.html); unchecked stays
failed/not run. Submit prepares a chat prompt; it cannot send automatically.

## Windows

Keep the current project/configuration, close the GUI and preserve local edits:

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
git rev-parse HEAD
# Recommended persistent data location, outside the checkout:
$env:PHOTOBOOTH_V2_STORAGE_ROOT = 'C:\MeongData\Photobooth'
$env:PHOTOBOOTH_V2_BOOTH_ID = 'PB001V2'
python tools/run_portrait_v2.py
```

The ordinary launcher defaults to storage layout 2. Local default does not
upload/print. For saved test printer + existing Apps Script configuration:

```powershell
python tools/run_portrait_v2.py --print --drive
```

Add `--manual-print` only if the operator wants the explicit print button.
These options do not enable production payments, scanner or game discounts.
Merchant Sandbox always retains its isolated prior profile and both transports
off. MOCK retains the original quote/template IDs, not remote customer packs.

Without the override, the data root is `<repository>/data/Photobooth`, below data
so it cannot collide with the Python `photobooth` package on Windows. Use one
writer/machine per physical booth. PB001V2 maps to folder PB001; transaction IDs
use **PB001V2S2_00000001** onward in a separate monotonic ledger. This new namespace
avoids reuse of unseen legacy PB001V2 remote leases. PB002V2 maps independently.
Never clear counters/pool/journals to restart numbering. The source directory
and the configured data-root directories/ancestors cannot be `old` or links.

At boot, 25 empty local READY folders are created. Claims and refill use the
existing atomic store with a per-booth process lock. After claim, Photo/01,
Photo/02 etc correspond to designs/sessions, not physical copies. Raw contains
all originals and the retake; color contains the mirrored-photo RGB strip; bw
contains the exact final 1-bit raster produced by the saved v1 print profile.
The original calibrated printer sends that raster, without a second dither.

## Existing Apps Script project

Do these manually as the existing Web App's executing account; no cloud setup
or deployment was performed by Codex. Keep the existing UPLOAD_TOKEN and /exec
URL in the original ignored local settings. Do not paste credentials into chat.

1. Copy [apps_script/Code.gs](../../../apps_script/Code.gs) into that project.
2. In Script Properties optionally set `CONTENT_ROOT_ID` to a dedicated common
   parent; when absent, setup uses the account's Drive root. Run
   **setupBoothStorage** in the editor. It creates/reuses uniquely named siblings
   `Photobooth`, `Global_Advertisement`, `Global_Template` and saves their IDs.
   Preconfigured IDs must point to those named siblings. It does not inspect,
   import, move, migrate or modify `old`; legacy DRIVE_FOLDER_ID remains unchanged.
3. Enable the existing Drive API v3 service/API if necessary. Run
   **setupPhotoRetention** as that same account and authorize. It keeps exactly
   one owning-account hourly CLOCK cleanup trigger. Setup does not delete photos.
4. Deploy → Manage deployments → edit the existing deployment → **New version**.
   Keep execute-as owner/access settings and the existing /exec URL.
5. Launch v2 with `--drive`. The worker creates/registers only its physical booth
   root and Local/Advertisement + Local/Template; it binds existing pending local
   transactions before reserving the next 25 empty remote transaction folders.
6. Run `python tools/check_drive_retention.py`. It defaults to **layout 2** and
   checks that booth parent/clock read-only. `--storage-layout 1` deliberately
   checks the legacy parent. READY is not proof of actual photo deletion.

With PHOTOBOOTH_ROOT_ID enabled, the hourly sweep handles only explicitly
registered PB00X roots. It no longer sweeps legacy DRIVE_FOLDER_ID automatically;
legacy/archive photos are not migrated or adopted into the new root. Finish or
inventory active legacy-v2 deliveries using their original profile before an
operational cutover. Never switch profiles during a pending/uncertain print.
New transactions use their original creation timestamp even if reconnect creates
an entirely new Drive folder later. Local photo bytes expire after 15 days;
Drive photos expire after 30 days. Small local state/tombstones remain to prevent
ID reuse/replay. Retention never authorizes deletion of assets or READY slots.

## Global and booth-local content

Put shared media directly or in nested folders under Global_Advertisement;
put per-booth media under Photobooth/PB001/Local/Advertisement. The existing
player supports PNG/JPEG/WebP and MP4/MKV/MOV/WebM. Optional `playlist.json` uses
the existing advertising JSON schema with relative cached media/poster paths,
durations, placement and schedule. Without it, supported media are ordered by
path and use the existing default duration. Global and local playlists coexist.

For templates, upload a **complete** original-compatible pack with
`layout_80mm.json`, its PNG artwork and all masks directly under Global_Template,
or under a booth's Local/Template. The original bundled
`photobooth/assets/templates` is the schema/example. Masters stay 640×1920,
three bounded photo apertures, matching masks and a bounded QR area. Global packs
replace the bundled gallery; booth-local packs append separate stable IDs. If
there is no downloaded pack, the twelve bundled originals remain available.
Manual offline booth media/packs can also live in local disk Local subfolders.

Each booth independently downloads all four scoped namespaces. Cache paths are
`PB001/Cache/Global_Advertisement/<version>/...`, Global_Template and corresponding
Local_Advertisement/Local_Template copies. `_state/content-current.json` selects
one completely checked generation. Checks include size/MD5, original pack decode,
Windows-safe unique paths and unchanged inventory after download. Downloads use
512-KiB authenticated Drive ranges, not whole-video Apps Script blobs. Limits:
500 files, depth six, 2 GiB/file, 10 GiB/snapshot; exceeding them requires operator
attention and retains the previous snapshot. Initial installation needs a full
sync to have shared files offline. Existing bundled/manual files still work.

Activation occurs at idle; active visitors retain their immutable asset paths.
No cache garbage collector removes an older generation behind a visitor. Plan
local storage maintenance separately: photo retention does not delete content
cache generations. Invalid/incomplete/interrupted content updates retain the
last good generation; source changes are polled in the background about once
per minute while connected. `old` is pruned before descendant access.

## Offline, QR and rollback

With --drive selected, missing network/configuration/ready remote reserves does
not block local photo/print. Transactions record explicit Drive intent and wait
for idempotent binding/upload; deliberate local-only visits never upload later
silently. Existing reserved real folder IDs/URLs are cached and can be printed
while offline. If no real folder was known at composition, paper explicitly
reports pending upload; the verified on-screen QR follows online. Saved paper
pixels cannot acquire a QR later: reconnect never rewrites color/BW or reprints.
Uploaded photos are held until the original retention policy is acknowledged by
an active timer; repeated upload uses the original checksum/revision engine.

If credentials were missing at startup, configure the existing local settings
and restart with --drive; it resumes pending layout-2 visits without a new photo.
Network failures with valid configuration retry automatically. No QR is shown
as verified until every queued raw/color/BW file has a verified acknowledgement.

Rollback checkpoints: foundation **76bb9a0**, backend **6e2f777**; final source is
recorded in README evidence. Revert source in a new scoped commit after review;
never reset/delete state or replay uncertain external actions. Close the GUI
before profile changes. Explicit `$env:PHOTOBOOTH_V2_STORAGE='1'` selects the
previous v2 profile for its own existing queues, counters and paper journal; it
does not migrate layout-2 transactions. To return to current defaults:
`Remove-Item Env:PHOTOBOOTH_V2_STORAGE -ErrorAction SilentlyContinue`. v1 main.py,
master, original game, payment state and `old` remain outside this change.
