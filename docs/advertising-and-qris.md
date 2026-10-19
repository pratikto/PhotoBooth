# Advertising and QR payment-slip setup

> **CURRENT SOURCE (2026-10-19):** This functionality and related documentation are now part of `master` at the published, immutable `v1.0.0` [source pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0). The previous `feature/kivy-gui` and other feature branches remain historical references. CI passed on the tagged SHA (`07ce51d`, [Kiosk](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245), [Dither](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273)), but physical Windows acceptance is separate. BUG-001/007 audio and BUG-009 Drive retention remain unresolved; payment stays DEMO.

This implementation is part of the source on `master` (tagged as `v1.0.0`). It does
not merge or change the separate `feature/thermal-printer` branch.

## Customer flow

| State | Media | Sound | Exit |
| --- | --- | --- | --- |
| App opening / idle | Idle playlist of videos and/or images | Video's own audio; app music/cues suppressed | Manual Start or face invitation leads to illustrated guide |
| Guide / template selection | Existing Meong UI | Application music and effects | Payment; or 180 seconds inactive back to ads |
| Payment | Independent payment playlist left; stable QR column right | Application audio; advertising forced mute | Explicit demo confirmation, or cancel before editing |
| Capture / review / result | Existing photography workflow | Application music/effects | Last completed result returns to idle advertising |

Both manual Start and acceptance of a face invitation open the illustrated guide; its own Start button leads to layout selection. The invitation needs five seconds of fresh nearby face observations. Brief
detector misses up to 0.65 seconds are tolerated; an inference gap over 0.8
seconds resets the partial hold. A sustained two-second absence or a 45-second
cooldown allows another invitation. No identity is recognized and no camera
images are recorded by face detection. The operator can disable the optional
hint with `PHOTOBOOTH_FACE_TRIGGER=0`; manual entry remains available. Actual
lighting, camera placement and face pose still require on-device validation.

The OpenCV frontal-face model ships with the app: no extra MediaPipe install,
account or first-run model download is needed for the advertising invitation.
The existing optional palm shutter keeps its own detector and dependencies.

## Playlists and schedules

The default configuration is
`photobooth/assets/ads/playlist.json`. Paths resolve relative to that JSON file.
Use `PHOTOBOOTH_AD_CONFIG` to select an operator-owned copy outside the repo.
Edits are picked up when a new idle advertising page opens. The payment
playlist uses the configuration loaded for that customer visit.

Supported images: PNG, JPEG and WebP. Supported video containers: MP4, MOV, MKV
and WebM, subject to the installed decoder. H.264/yuv420p MP4 is the recommended
portable input. The checkout contains still-image posters only. The bundled configuration
automatically discovers supported videos under the repository-root `ad_video/`
directory (MP4, MOV, MKV, WebM), in case-insensitive alphabetical order.
File names may contain spaces and can change without editing JSON. All detected
local videos are placed before bundled still-image fallbacks and play in both
idle and payment placements, with payment audio always muted. Discovery occurs
when a new advertising catalog is created. Explicit `PHOTOBOOTH_AD_CONFIG`
playlists are not mixed with discovered videos. Video files are not uploaded
to GitHub.
Missing or unsupported
video files are skipped and the existing JPEG entries rotate as fallback.
Install video files locally. Original and converted video files are excluded from Git. Media
is fitted without stretching or cropping. A failed item is skipped once per
placement instance. An empty, missing, invalid or unplayable playlist falls
back to a branded Meong poster. A missing decoder cannot block manual entry.

Example scheduled still image, to add to the `ads` array:

```json
{
  "id": "venue-morning",
  "title": "Venue morning campaign",
  "file": "venue-poster.png",
  "placements": ["idle", "payment"],
  "seconds": 8,
  "enabled": true,
  "start": "2026-10-17T00:00:00+07:00",
  "end": "2026-11-01T00:00:00+07:00",
  "hours": ["09:00", "12:00"]
}
```

IDs should be unique. `start` is inclusive; `end` is exclusive. Optional `hours`
use the configuration's timezone (default `Asia/Jakarta`) and support overnight
windows such as `22:00` to `06:00`. Equal start/end hours mean all day. Image
`seconds` defaults to 8; video changes at its actual end. Eligible media rotate
in configuration order. The player's schedule check removes a creative when
its current window ends, including during a longer video.
`requirements.txt` includes `tzdata`, so these venue timezones also work on
Windows installations without a system IANA timezone database.

At normal desktop sizes payment allocates approximately 65% to advertising and
35% to the QR/order column. At 800×600 the QR column retains a 300-pixel minimum
for scan readability. Below desktop width the existing responsive layout stacks
the panels and provides scrolling. The principal payment QR does not move or
reload when advertising changes; enlargement appears in the advertising area.

The three original sample clips have no audio stream. Their local H.264 copies
remain silent too; use a video containing audio to check the opening-screen
advertising volume. The app does not add a soundtrack to still photos or silent
source video.

The `timing` object controls `face_hold` (5), `offer_timeout` (15),
`face_cooldown` (45), `landing_idle` (180), `idle_warning` (10),
`payment_offer_after` (60), and demo `payment_validity` (900), all in seconds.
These finite, bounded values are read locally; changing code is unnecessary.

## Audio ownership

`data/audio/levels.json` persists the three existing application buses and the
independent `ads` level. The header gear is present on the advertising page too.
Opening/returning to idle suppresses application effects and stops music immediately;
entering the photo workflow fades the music back in. The face invitation lowers
idle video volume while it is visible. Photos have no soundtrack. Payment video
volume is set to zero before decoder loading and stays zero after settings,
backgrounding and resume. Backgrounding pauses both audio owners.

`PHOTOBOOTH_AUDIO=0` silences both video and application audio.
`PHOTOBOOTH_AD_VIDEO=0` shows video posters for repeatable screenshot QA; this
mode is not counted as actual video playback in reports.

All three supplied samples are silent source files. Their lack of sound is not
an application volume failure. The app does not invent an advertising soundtrack.

## Payment, expiry and print offers

**No live payment provider is connected.** Every payment QR payload and printed
slip is explicitly labeled DEMO / NOT FOR TRANSFER. The development confirmation
button remains the only way to simulate successful payment. Paper output,
timeouts and banking-app screenshots are never treated as money received.

The coordinator models one attempt with an ID, payload, amount, creation time,
expiry and status. A local waiting timeout does not create another attempt.
The currently active QR is printed unchanged, without extending expiry. A
confirmed expired QR offers **PERBARUI + CETAK**. Even a still-active QR near
expiry is printed unchanged; the worker rechecks validity before sending it.
Renewal rechecks the final status; paid, pending or unknown status blocks replacement.
Each renewed QR has a different attempt ID and payload, while the amount stays
the same. Photo-transaction/Drive slots are still allocated only after the
explicit demo-payment confirmation.

The automatic print offer appears once per active QR, and a separate renewal
offer may appear when that QR expires. Ignoring an offer for fifteen seconds
closes only that offer. QR validity keeps counting normally. Printing is an
off-thread job and does not use the unanswered-offer timeout. While printing,
the print action is locked; closing its status card does not submit another job.
Cancelled, replaced and retired offer buttons cannot operate a later attempt.

The customer stays on payment while taking the paper and scanning it. Editing
the order cancels the unpaid demo attempt before navigation and invalidates any
not-yet-sent job. A paid/unknown attempt cannot silently return to advertising
or begin another customer order. A print already transmitted to the printer
cannot be physically recalled. Payment success dismisses outstanding offers.

The coordinator has explicit timeout and final-state guards for a future
gateway adapter. A live integration still requires provider credentials,
verified server notifications/status checks and off-thread network handling.
The UI does not offer a way to paste an unverified real payment QR.

## Payment QR thermal printing — current GUI and legacy LAN configuration

**Current (reconciled 2026-10-19):** The GUI passes its saved printer configuration to `QrisPrinterWorker`, sharing the photo-strip transport. **BUG-003 QR-slip printing subsequently received OWNER REPORTED PASS for paper output on Windows.** The earlier failure is historical; exact Windows checkout SHA, per-device receipt photo and phone scannability were not captured. A sent spool or digital decode alone must never be labelled verified paper/phone scan. See [FEATURE_STATUS.md](FEATURE_STATUS.md).

**Preferred GUI setup on Windows:** open Settings → **PENGATURAN PRINTER** → **USB Windows**, enter the *actual* Windows printer queue name (the user's environment has used POS80 Printer/POS80ENG), select a suitable printer dot width and save; perform a physical **TEST PRINT** first. Then open demo payment, tap **CETAK QR**, inspect the real paper and scan with a phone to validate QR readability. LAN and Wi-Fi routes may also be configured through the same printer settings. Do **not** infer a successful print from an ESC/POS file or a spooler job alone.

The worker uses the current saved `PrinterConfig` from the Kivy GUI, routes via configured LAN, Wi-Fi or Windows USB spooler, and preserves the active QR payload/amount/expiry. Without any usable configured route, the GUI should show a **preview**, not claim paper was printed. The source code selects among configured routes. **The original device failure was reported resolved by the owner (BUG-003)**; investigate only if a new regression or unverified device mode appears.

**Legacy standalone LAN-only fallback:** Direct `QrisPrinterWorker` callers without the GUI's printer-config provider may configure:

```powershell
$env:PHOTOBOOTH_PRINTER_HOST = "192.168.1.100"
$env:PHOTOBOOTH_PRINTER_PORT = "9100"
$env:PHOTOBOOTH_PRINTER_DOTS = "576"
python main.py
```

Those legacy environment settings must **not** be presented as the sole method for printing from the current GUI. Values shown are examples, not discovered printer settings. For a direct LAN sender the ESC/POS port is commonly 9100; verify printer model/protocol, actual IP and accepted printable width. On Linux, `export` may be used instead of PowerShell assignments.

The QR slip uses an undithered black/white QR, integer-sized modules (at least three printer dots wide) and four-module quiet zone; applying the photo's grayscale dithering or a large logo inside the payment QR can make scanning unreliable. It includes the exact **demo** payment payload, amount, attempt ID and expiry in WIB. The QR may be enlarged on the display without replacing the active payment attempt.

PNG previews and ESC/POS `.bin` spools are written under ignored `data/qris-spool`. A successful `send` indicates transfer to the printer interface, **not** physical paper acceptance or payment. Uncertain partial sends are not retried automatically: inspect the paper first to avoid duplicate output. Track reproducible outcome and paper/scanning evidence in [bug_tracker.md](bug_tracker.md) and [test_checklist.md](test_checklist.md).

## Anonymous playback reports

`data/advertising/events.jsonl` records actual displayed runs, their visible
seconds, completed/partial status, placement and successful entry-button actions.
Paused, hidden, loading, missing and poster-only video time is excluded. The
report records no camera images or face identity. Counts are not unique viewers
or proof of attention; an entry after an invitation is not a paid conversion.

```bash
python tools/ad_report.py --events data/advertising/events.jsonl > ad-report.csv
```

The player retires a creative after a ten-second load timeout or twelve seconds
without decoder progress. A queued load is cancelled on navigation, so even a
fast page change cannot start hidden playback.

CSV columns: `ad_id`, `placement`, `plays`, `completed`, `displayed_seconds`,
`photo_entries`. Keep the JSONL file private to the operator and archive it as
needed; it is intentionally ignored by Git.

## Validation

```bash
python -m pip install -r requirements.txt
python -m compileall -q photobooth tests tools
SDL_VIDEODRIVER=offscreen SDL_AUDIODRIVER=dummy PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1 PHOTOBOOTH_AUDIO=0 PHOTOBOOTH_FACE_TRIGGER=0 PHOTOBOOTH_PALM_TRIGGER=0 PHOTOBOOTH_AD_VIDEO=0 python -m unittest discover -s tests -v
SDL_VIDEODRIVER=offscreen PHOTOBOOTH_AUDIO=0 PHOTOBOOTH_AD_VIDEO=0 python tools/render_gui.py --output-dir /tmp/meong-ad-qa
```

Native video tests generate a tiny H.264/AAC fixture locally with `ffmpeg`, then
enable the real FFmpeg-backed Kivy player. They check textures, video-to-photo
EOS transition, duration accounting, audio ownership, background/resume and
decoder retirement. No video fixtures are committed or uploaded.
Receipt tests independently decode both PNG pixels and reconstructed ESC/POS
raster bytes, and exercise mocked TCP sends/partial failures. Cameras, money,
Drive and physical paper remain outside automated hardware-free validation.
