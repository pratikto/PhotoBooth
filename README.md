# Meong Photobooth

A Python photo booth application built with Kivy, OpenCV, Pillow, and ESC/POS printing. The attached procedure document is the functional source of truth. Live QRIS payment remains outside the current implementation.

## Illustrated kiosk, animation and audio

The welcome page now explains the workflow with four large native illustrations:
**choose a frame → payment demo → three photos → print and scan**. Short labels
replace the previous paragraphs. Every page has a small animated action symbol
and a brief entry transition. The capture page adds a rotating countdown ring,
one chime per displayed second, and a short flash/shutter cue after a successful
photo save. A prepared retake still waits for the customer to press the shutter
or deliberately hold an open palm.

Template arrows sit on the left and right sides of the receipt preview, centered
vertically. Each selected template in **Pesanan kamu** is a separate touch button.
Tapping it animates the cyclic carousel to that design and updates its name and
quantity controls. It does not add sessions or change the payable total. A click
during a swipe waits for the swipe to finish; stale rows retire with their page.

A gear button stays in the header on all six screens. Its **Suara** menu has
independent **Musik**, **Tombol**, and **Efek kamera** sliders, including 0% mute
and short cue previews. Preferences are saved locally when the menu closes.
The original instrumental loop uses warm plucked notes, a bass line and a light
melody, inspired by the general atmosphere of farm games. It contains no
commercial game recording or copied soundtrack. Music continues across pages
and becomes quieter during the camera countdown. It resumes its selected level
after capture; button and camera cue gains remain independent.

No additional audio package or online service is needed. On first normal
startup, Python generates/cache WAV files under ignored data/audio in a
background worker. Kivy loads and plays them on its main thread. Missing audio
hardware must not prevent photography. PHOTOBOOTH_AUDIO=0 disables playback;
PHOTOBOOTH_ANIMATIONS=0 disables continuous page illustration/countdown motion.
The optional palm shutter is paused while the audio menu is open, so adjusting
volume cannot accidentally start a photograph.

The GUI and folder QR now resolve one logo source in
[photobooth/branding.py](photobooth/branding.py). The final bright-trail source
is **Meong Photobooth’s vivid pixel trails.png**. Its bytes could not be imported
in this editing session because the local file runtime was unavailable.
The earlier full logo is therefore still bundled. Install the approved final
image as photobooth/assets/meong_photobooth_vivid.png, or set
PHOTOBOOTH_LOGO_PATH to that local PNG, then restart the app. Both the header
and newly generated folder QR images will use it. The code does not recolor,
redraw, or download a substitute logo. Payment demo QR codes remain plain.

Implementation and maintenance:

- [photobooth/ui_motion.py](photobooth/ui_motion.py): scalable pictograms, page-scoped animation lifecycle, countdown ring, and capture flash.
- [photobooth/audio.py](photobooth/audio.py): commented original score, deterministic WAV synthesis/cache, three mixer buses, and atomic volume preferences.
- [photobooth/ui_kivy.py](photobooth/ui_kivy.py): illustrated tutorial, persistent audio settings, clickable cart rows and native controls.
- [photobooth/ui_brand.py](photobooth/ui_brand.py): carousel requests, swipe/animation coordination, and stale-page cleanup.
- [tests/test_audio.py](tests/test_audio.py) and [tests/test_kiosk_motion_audio.py](tests/test_kiosk_motion_audio.py): hardware-free sample, gain, navigation, modal and timing regression tests.

Run tests with python -m unittest discover -s tests -v. Enable
PHOTOBOOTH_TEST_GUI=1 for real-widget checks. The added Kiosk GUI regression
workflow also runs the existing controller, storage, QR pixel and layout checks.
Inspect its actual Actions result before treating the update as validated;
speaker audibility, the physical webcam/printer, the final logo PNG, and exact
arrow agreement with the unavailable reference screenshot require device or
asset verification.

Validation of this update uses Python 3.12 and the real Kivy desktop widgets:
**131 automated tests pass**, with two native palm-model checks explicitly
skipped because their opt-in assets are absent. **72 actual widget renders**
cover 800x600, 1200x800 and 1920x1080. They retain the existing QR decoding,
crop, bounds and disabled-text contrast assertions. The render harness waits
for completed entry transitions and stable geometry before measuring pixels.
Audio sample/mixer tests use deterministic fixtures; this is not a physical
speaker, webcam, printer, or live Drive account check.

## MEONG GUI and cyclic template browsing

The interface uses the approved pixel camera-cat and original MEONG PHOTOBOOTH
wordmark. Lens blue, cyan, and cheek pink create a bright theme across the
welcome screen, progress tabs, template selector, capture guidance, and actions.
The GUI and folder QR share the same local logo selection.

The template picker is now a **horizontal, cyclic carousel**. Drag/swipe left
or right, use the **‹ / ›** arrows, or use a mouse wheel over the previews.
Moving past **12 / 12** returns to **01 / 12**; moving left from the first frame
returns to the last. A large center receipt identifies the focused design;
smaller adjacent previews show its cyclic neighbors. The selected name, position
counter, pixel markers, and quantity controls follow the focused frame.

Browsing only changes focus. It never adds a session, changes another design's
quantity, or starts payment. Use **+ / −** to edit the focused template's count.
The complete order and total remain in the blue cart beside the carousel on
desktop. The agreed price stays **Rp5,000 per session**. Returning from dummy
payment preserves the order and focused template. A new customer starts at the
first frame with an empty order.

The layout is checked at **800×600**, **1200×800**, and **1920×1080**. On wide
monitors, content is centered within 1440 dp instead of stretching receipt cards
across the full screen. Narrow windows can stack panels with vertical scrolling.
Actual Android packaging/camera support is a separate integration.

For learning and maintenance:

- [`photobooth/ui_brand.py`](photobooth/ui_brand.py) owns colors, the original-logo lockup, progress tabs, receipt preview slides, and native Kivy carousel behavior.
- [`photobooth/ui_kivy.py`](photobooth/ui_kivy.py) binds carousel focus to quantities and the existing controller callbacks.
- Native Kivy owns swipe thresholds, touch grabs, snapping, and looping. Quantity buttons are outside the swipe surface.
- A desktop container that already fits does not grab vertical scrolling; this lets horizontal swipes reach the carousel immediately.
- Duplicate arrow releases during a short snap are ignored, so repeated clicking cannot continually restart an unfinished animation.
- Leaving the picker retires its animation and touch grabs. Retired arrow callbacks cannot alter payment or a later customer's selection.

See the [GUI evidence and checks](docs/qa/meong-carousel.md) for screenshots,
actual pointer/swipe coverage, and current validation results.

## Current implementation: photo and Drive flow

The first implementation milestone includes:

- A welcome screen and a template picker with a cart-style session summary.
- Twelve approved Meong thermal receipt templates with full-strip gallery previews.
- Automatic placement of each session's three photos inside the selected design, including heart, vintage-label, rounded, and pixel-corner masks.
- Review thumbnails use the same crop and shape as the accepted result, including after a retake.
- Quantity means separate sessions. Each session captures three new photos and receives one retake of a selected photo.
- A five-second countdown before each capture.
- A final digital photo composition saved locally for each session.
- Automatic monochrome ESC/POS printing over configured LAN first, Wi-Fi second, then USB fallback with a result-screen retry action.
- One transaction folder slot for all sessions in an order, named with the booth ID and an incrementing eight-digit counter, such as PB001_00000001.
- A persistent local pool targeting at least 25 verified Drive folders. Each folder is created with its final incrementing transaction ID, so assignment does not rename it.
- A cached folder ID and URL for each slot, so an assigned transaction can continue offline and show the same folder QR.
- A local manifest and retryable upload queue. Uploads are identified by transaction-relative path and checked by size and checksum. Local photo retention is limited to 15 days even when upload has not succeeded. Direct OAuth uploads are resumable; the Apps Script backend retries whole files idempotently.
- Automatic photo retention: 15 days on the booth and 30 days in Google Drive, measured from the transaction start. Drive's independent hourly timer requires the Apps Script setup below.

The dummy payment screen supports testing the complete flow. Live QRIS payment remains pending; physical printing is integrated and can be configured for the iWare J-82ULW.

Payment-related sections below describe the procedure's target behavior; the printer flow is described in the implemented printer setup below.

### Approved 80 mm templates

All twelve designs are included in this repository; no separate template
download or Drive script update is needed. In the GUI, add a quantity beside a
design, continue through the dummy payment, take three pictures, optionally
retake one, and select **GUNAKAN FOTO INI**. Python puts those photos into that
session's selected template and shows the completed strip on the result page.
Use **PERBESAR HASIL** to inspect a larger, vertically scrollable copy.

The result is **640 × 1920 pixels at 203.2 dpi**, corresponding to **80 × 240 mm**
at eight dots/mm. The approved artwork retains its **1 mm paper margins**.
The footer reserves **48 × 48 mm** for the transaction-folder QR, including its
white scan margin. The full Meong logo is centered and monochrome there. Raw
photos retain their original resolution; digital photos inside the strip keep
their colors. The printer adapter converts the saved composition to a
monochrome raster at the configured printer width (576 dots by default).

| Number | Template key | Design |
| --- | --- | --- |
| 01 | template_a | Special Day |
| 02 | template_b | Stitched Hearts |
| 03 | template_c | Memory Pass |
| 04 | template_d | Movie Night |
| 05 | template_e | Cinema Club |
| 06 | template_f | Now Showing |
| 07 | template_g | Cafe Moments |
| 08 | template_h | Scrapbook Memories |
| 09 | template_i | Pixel Arcade |
| 10 | template_j | Bake a Smile |
| 11 | template_k | Date Night |
| 12 | template_l | Celebrate |

Implementation and learning guide:

- [`photobooth/catalog.py`](photobooth/catalog.py) loads the designs and composes photos, masks, and the real folder QR.
- [`photobooth/assets/templates/layout_80mm.json`](photobooth/assets/templates/layout_80mm.json) defines each photo/QR position in millimetres.
- [`photobooth/assets/templates/`](photobooth/assets/templates/) contains the twelve approved masters and 36 explicit clip masks.
- [`photobooth/ui_kivy.py`](photobooth/ui_kivy.py) displays actual template previews and the exact review-frame pixels.
- [`photobooth/app.py`](photobooth/app.py) passes the current session's template and final photo paths, including its replacement photo, into the renderer.

Try your own existing photos without opening the camera or GUI:

```bash
python tools/compose_template.py --list
python tools/compose_template.py --template 02 --photos one.jpg two.jpg three.jpg --output preview.png
```

Supply an actual HTTPS folder destination using `--folder-url` to embed its QR.
The helper does not upload files. Without that option, the output says **MODE
LOKAL** and contains no dummy download QR. The normal application supplies the
transaction's cached folder URL automatically. Source files are never edited.

The PNG's physical dimensions describe the design. A real printer must support
the required printable width and dot density to preserve its 1 mm margins;
physical printer and phone-camera checks remain to be performed on the device.

## Agreed product workflow

### 1. Prepare the booth and reserve storage folders

Before accepting a customer transaction or starting a photo session, the Python application should prepare and check its storage pool:

- Keep at least 25 unused transaction-folder slots available in Google Drive and on the booth's internal SD card.
- Each slot consists of a pre-created Drive folder and its matching local directory or local reservation record.
- Store the Drive folder ID and URL on the booth so the folder QR can be generated without an internet connection.
- Configure and verify the Drive folder's sharing permission while online as **Anyone with the link**.
- Refill the pool while the internet is available so the number of unused slots returns to at least 25.
- If no unused slot remains, stop accepting new transactions. Resume only after internet access returns and the pool has been replenished.

The folder is allocated before the transaction and before taking photos. One transaction uses one folder, even when its order includes multiple templates or sessions.

### 2. Select templates, quantities, and pay

The customer selects one or more templates and a quantity for each template.

- One unit of quantity means one separate photo session for that template.
- For example, quantity 2 for one template gives the customer two independent sessions. Each session has its own three new photos and its own retake allowance.
- Calculate the payment from the total number of ordered sessions and the configured price per session.
- The payment screen should show the order total and a clear QRIS state, such as waiting for payment, verified, or expired.
- Do not start photography until the payment provider confirms payment.
- If the customer changes the cart after a payment QR is created, invalidate or cancel that QR and create a new one for the updated amount.

The QRIS payment code and the folder-access QR code are different codes and must be labelled clearly. The offline payment policy is still to be decided: a cached folder link is not payment confirmation, and the app cannot assume that a newly created QRIS payment can be verified while offline.

### 3. Assign one transaction folder

Use an incrementing transaction ID for the folder name:

**PB001_00000001**

- **PB001** identifies the booth.
- **00000001** is an eight-digit transaction sequence, incremented for each new transaction.

Assign the next ID when a pre-created folder slot is claimed for a transaction, before taking photos. Store the counter and the assigned transaction ID durably on the internal SD card so they remain available offline and survive application restarts. Allocate each ID only once; never reuse it after cancellation, failure, or restart. Gaps in the sequence are acceptable.

The transaction folder contains both:

- The raw photos captured by the camera.
- The final photo output for each template session.

Each Drive folder slot is created with its final incrementing transaction ID and cached folder link. Claiming a slot records the transaction against that existing ID; the folder name does not change. If the booth is offline, continue to use the cached Drive folder ID and URL for the QR.

### 4. Take photos and allow retakes per session

For every ordered session:

1. Capture three new photos. Photos from another template or quantity session are not reused.
2. Let the customer choose which captured photo to use.
3. Allow at most one retake in that session. The retake replaces the selected photo.
4. Keep the retake button disabled until a photo is selected, and show the selected photo and remaining retake allowance.
5. **RETAKE FOTO TERPILIH** opens the replacement-photo camera preview without starting a timer. Let the customer pose, then start the five-second countdown by pressing **AMBIL FOTO PENGGANTI** or deliberately holding an open palm when the optional gesture input is ready. The allowance is consumed only when the replacement is saved successfully.

The retake allowance resets for each new session. It does not reset between attempts within the same session.

#### Optional open-palm shutter

The photo button remains available. On a capture page, the customer may instead
show an open palm to the camera for approximately **one second**, then lower the
hand during the normal **five-second countdown**. This also works on the prepared
retake page; gestures never select a photo, pay, navigate, or enter retake.

Install the optional detector in the same Python 3.12 environment used by Kivy:

```powershell
.\.venv-kivy\Scripts\python.exe -m pip install -r requirements-palm.txt
.\.venv-kivy\Scripts\python.exe main.py
```

On its first run, a background worker downloads the approximately 8 MB public
MediaPipe gesture model into `data/models/gesture_recognizer.task`. The GUI says
the gesture input is being prepared, and button capture stays available. The
download is pinned to model version 1 and checked against its size and SHA-256
before atomic publication. Later runs use the cached model offline. Camera
frames stay on the device; no recognition service or API key is used.

The preview's guidance shows hold progress. One sustained palm produces one
shutter; after either a button or gesture shutter, a non-palm interval of at
least 0.4 seconds is required to re-arm gestures. Gaps, duplicate camera arrays,
old-page results, and stale observations cannot accumulate a hold. Capture and
retake still share the existing readiness, countdown, and quota checks.

The detector owns a separate thread and a latest-frame mailbox, with at most ten
inferences per second on a copy resized within 480x360. Photo storage keeps the
original camera resolution. Missing MediaPipe, unsupported native binaries, a
model download error, or inference failure leaves the normal button usable.
To disable gesture initialization in a PowerShell session:

```powershell
$env:PHOTOBOOTH_PALM_TRIGGER="0"
```

The optional dependency is pinned to MediaPipe 0.10.32, which provides a Windows
x64 wheel for the current laptop workflow. This does not establish compatibility
with ODROID XU4's ARM32 platform; use base requirements/button input there until
a native backend is verified. Base requirements use `opencv-contrib-python`,
the same OpenCV distribution required by MediaPipe, instead of `opencv-python`.
Keep only the contrib distribution in a clean environment. If an older setup
contains both distributions and OpenCV becomes inconsistent, uninstall both and
reinstall `requirements-palm.txt` to restore a single `cv2` provider.

Implementation and setup references:
[MediaPipe Python guide](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python),
[model and gesture labels](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer#models),
and [pinned package wheels](https://pypi.org/project/mediapipe/0.10.32/#files).

### 5. Show progress and finish the order

The interface should show the customer's progress through the order. For orders with quantity greater than one, show both the template and the current session, for example “Template 1 of 2 — Session 1 of 2.”

- Show **Next** only when another ordered session remains.
- On the final session, show **Selesai** instead.
- After completion, show a visible 60-second countdown before returning to the start screen.

### 6. Upload results and provide the folder QR

The QR printed with the photo points to the transaction folder, so the customer can find the raw photos and template results together.

#### Full-logo folder QR

The result-screen QR and the QR embedded in every newly saved three-photo
composition now use the approved **full MEONG PHOTOBOOTH logo inside the QR**.
The earlier complete camera-cat, grayscale trail, and wordmark are bundled in
[`photobooth/assets/meong_photobooth.png`](photobooth/assets/meong_photobooth.png).
The application and composition titles also use **MEONG**, without an S.

[`photobooth/qr_code.py`](photobooth/qr_code.py) generates the QR automatically
from the transaction's cached folder URL. No manual QR editing, new Drive
configuration, or internet connection is needed to insert the logo. Different
transactions encode their own folder URLs; the artwork stays the same.

The helper uses high error correction, a small white logo plate at the **exact
geometric center**, and a four-module white scan margin. Logo placement does not
move with URL length. Corner finders and timing patterns stay outside the plate.
OpenCV independently checks the actual rendered QR and its 180px screen preview;
if the automatic encoding mask is hard to read beneath the logo, the helper
tries another permitted mask with the same URL, version, and dimensions. It
never moves the logo to obtain a passing scan. These checks use existing local
dependencies and never open the URL or contact a scan service.
The composition requests its final pixel size directly, keeping each data
module an integer number of pixels wide. See the
[centering correction](docs/qa/centered-qr.md) for pixel-level regression checks.

The ESC/POS adapter prints the saved composition, including its real folder QR,
as a monochrome raster. It scales the 640 px-wide master to the configured
print-head width while preserving aspect ratio. A physical print should still
be checked for QR readability and darkness after the printer is configured.
Payment-demo codes remain plain and separate from the customer folder QR.
See the [branded QR verification](docs/qa/branded-qr.md) for examples, test
commands, and the limits of the digital checks.

**When online:**

- Upload the transaction's files to its assigned Drive folder.
- Show the cached transaction-folder QR immediately on the result screen. Upload status is displayed separately; the folder can be empty or incomplete until synchronization succeeds.

**When offline:**

- Save the transaction's files in its assigned local SD-card folder and queue them for upload.
- Use the cached Drive folder URL to generate the same folder QR without internet access.
- Tell the customer that the internet is disconnected and the photos will be uploaded when the connection returns.
- The QR can be printed while offline. The Drive folder may be empty or incomplete until synchronization finishes, so the notice must set that expectation.
- When internet returns, upload the queued files to the same assigned folder. Keep the folder link unchanged so the QR already printed continues to work.

Upload retries should be safe to repeat and must not create duplicate copies of the same file in Drive.

### 7. Print safely

The app automatically sends the saved composition when its result screen opens.
Configured raw ESC/POS TCP routes are tried in this order: LAN, then Wi-Fi.
USB is used if the configured network connections cannot be opened. The J-82ULW
supports USB, Wi-Fi, and LAN; see the thermal printer setup guide for setting
the IP address and the three connection routes.

The result screen shows print status and disables CETAK ULANG while a job is in
flight. If a network connection opens but writing fails, the print status is
uncertain and the same job is not automatically sent through another route.
The customer or operator can deliberately retry the saved image. Status
confirms that job bytes were sent; it cannot confirm paper movement without
printer feedback.

### 8. Clean up local storage without deleting Drive files

A separate scheduled cleanup program may remove old files from the booth's SD card to manage local storage.

- Never delete customer folders or files from Google Drive.
- Keep local files for transactions that are unfinished or still waiting to upload.
- Only remove local photo files after the corresponding Drive upload has been confirmed.
- Keep the local folder-link/reservation records needed to manage the pool and generate QR codes.

The cleanup schedule and local retention period still need to be configured.

## Google Drive access

Transaction folders should use **Anyone with the link** access so customers can open the folder by scanning the QR code. The link is not limited to a specific customer account. Apply and verify this permission when the folder pool is prepared online, before relying on a folder while offline.

## Setup

Install the Python dependencies from the project folder:

    python -m pip install -r requirements.txt

Configure LAN, Wi-Fi, and USB fallback as described in the thermal printer setup guide.

The existing Apps Script Web App setup is supported. Keep `WEB_APP_URL` and `UPLOAD_TOKEN` in the ignored `photobooth/local_settings.py` file. A safe starter file is provided as `photobooth/local_settings.example.py`; copy it to `photobooth/local_settings.py` and fill in the existing values.

The Web App must run the transaction-folder API in [`apps_script/Code.gs`](apps_script/Code.gs). In the Apps Script project's **Script Properties**, keep the existing `UPLOAD_TOKEN` and `DRIVE_FOLDER_ID`. Update the existing Web App deployment to a new version, with **Execute as: Me** and access allowed to **Anyone**. The deployment URL ending in `/exec` stays in `local_settings.py`. On startup, the booth requests 25 verified, empty folder slots; each slot is assigned a unique final name such as `PB001_00000001` when it is created. The slot's name does not change when a customer claims it.

Alternatively, installations using direct Drive API OAuth can configure these environment variables:

- `PHOTOBOOTH_ID` — booth code, default `PB001`.
- `PHOTOBOOTH_DRIVE_PARENT_ID` — Drive folder ID where the application creates its slot folders.
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, and `GOOGLE_OAUTH_REFRESH_TOKEN` — OAuth credentials authorized for Google Drive API access.
- `PHOTOBOOTH_CAMERA_INDEX` — camera index, default `0`.

Enable the Google Drive API and authorize the OAuth refresh token with Drive access for the intended account. The account needs permission to create folders, set link sharing, and upload files under the configured parent. Keep OAuth credentials outside the repository. Apps Script settings take precedence when both configuration methods are present.

For UI and camera development without Drive credentials, set `PHOTOBOOTH_LOCAL_ONLY=1`. This mode stores results only on the device and does not produce a Drive QR; do not use it for booth operations.

Run the local MVP with:

    python main.py

## Photo retention: 15 days locally, 30 days in Drive

| Storage | Photo lifetime | Cleanup |
| --- | --- | --- |
| Booth / platform (`photos/`) | 15 days from transaction start | At application startup and hourly while running |
| Google Drive transaction folder | 30 days from transaction start | Independent hourly Apps Script trigger after activation |

Both raw captures (including retakes) and final compositions expire. Upload
retries and old pre-created empty slots do not restart the clock. Offline or
failed uploads also lose their local photo bytes at 15 days. Small manifests,
transaction counters, and folder-slot ledgers remain so expired uploads cannot
resume or transaction IDs be reused. Cleanup occurs on the first scheduled pass
at or after the deadline; a powered-off booth cleans its local files on restart.

**Activate the cloud schedule in the existing Apps Script project:** update
[`apps_script/Code.gs`](apps_script/Code.gs), enable **Drive API v3** in
**Services**, run **`setupPhotoRetention`** once as the folder owner and authorize
it, then update the existing Web App deployment to a **new version**. Preserve
`UPLOAD_TOKEN`, `DRIVE_FOLDER_ID`, and the `/exec` URL. Updating Python alone
does not install the cloud timer. Cloud cleanup permanently deletes expired
managed folders, and their QR links stop working afterwards.

See [photo retention setup and recovery](docs/photo-retention.md) for preview,
existing-photo migration, activation verification, and the direct-OAuth limitation.

## Troubleshooting

- The application uses camera index 0 by default. If the USB camera is not detected, check the camera index configured in `photobooth/camera.py`.
- On Windows, allow desktop applications to access the camera in Settings > Privacy & security > Camera.
- Close other applications that may be using the camera, such as Zoom, Teams, or Camera.
- Photos and transaction manifests are stored under `photos/<transaction-id>`. Preserve `data/booth_state.json` and `data/drive_pool.json` with the transaction ledger and folder-link cache.
- If there are no ready Drive slots, check internet access and Apps Script configuration. The deployed Web App must include the actions in `apps_script/Code.gs`; the original upload-only deployment cannot create transaction folders. New transactions remain disabled until a slot is verified.
- An `ACTION_REQUIRED` upload requires staff attention before its 15-day local photo deadline. Failed/pending uploads do not extend retention. Empty reserved slots, configuration, counters, and manifests are preserved.
- If the log says `Run setupPhotoRetention and redeploy the Web App`, activate the cloud schedule above. Check Apps Script **Executions** for permission/API errors and `drive_retention_error` in the transaction manifest for registration failures.
- Live QRIS payment remains disconnected; thermal printing is integrated into the current UI.

## Project structure

- main.py starts the application.
- photobooth/app.py coordinates the camera, screens, and session flow.
- photobooth/ui_kivy.py builds the active Kivy interface and adapts controller timers to Kivy Clock.
- photobooth/ui_tkinter.py preserves the previous Tkinter GUI unchanged as history.
- photobooth/catalog.py contains the sample templates and digital photo-strip compositor.
- photobooth/workflow.py expands quantities into sessions and enforces one retake per session.
- photobooth/transaction_store.py reserves transaction IDs and writes local photos and manifests.
- photobooth/camera.py manages the camera connection and frame capture.
- photobooth/palm_gesture.py implements optional local recognition, the hold/release gate, model caching, and its nonblocking worker.
- photobooth/drive_storage.py handles Apps Script and direct OAuth Drive operations, sharing, uploads, and verification.
- photobooth/drive_pool.py maintains the local cache of ready and assigned Drive slots.
- photobooth/drive_sync.py syncs slot assignments and pending transaction uploads in the background.
- photobooth/retention.py enforces local photo expiry and registers the original transaction deadline with Drive.
- photobooth/qr_code.py creates the transaction folder QR shown on the result screen.
- requirements.txt lists the Python packages used by the project.
- photos/, data/, local configuration, and temporary Python files are excluded from Git.

## Kivy GUI migration

The active entry point remains `python main.py`. Install/update dependencies in
an activated virtual environment first:

```bash
python -m pip install -r requirements.txt
python main.py
```

The migration is based on `feature/local-photo-session-mvp`, which contains the
multi-session workflow and Apps Script folder API. Keep your ignored
`photobooth/local_settings.py`, `data/`, and `photos/` when updating an existing
installation. Credentials and existing transaction records must not be replaced.
The Apps Script deployment is unchanged by this migration.

`ui_kivy.py` owns screen layouts, Pillow-to-texture conversion, modal errors,
and the Kivy application host. `app.py` still owns transaction rules and camera
capture. Timers use cancellable Kivy Clock events; Drive work remains in its
background worker. The old `ui_tkinter.py` is preserved byte-for-byte and is no
longer imported by the active controller.

Folder QR generation is independent of upload verification. A real cached
`drive_folder_url` is required. Local-only development mode intentionally has no
Drive QR. If a folder QR is missing, check the transaction's manifest and the
Drive-slot configuration; a local filesystem path is not a customer Drive link.
QR pixels use nearest-neighbor filtering and retain their white quiet zone.

This is a desktop GUI migration, **not a finished Android APK**. Android camera
permissions, camera/USB/Bluetooth adapters, native dependency packaging, and
pause/resume behavior still require implementation and device testing.

Run the storage/workflow tests with `python -m unittest discover -s tests -v`.
To include real-widget GUI regression checks on a desktop, set
`PHOTOBOOTH_TEST_GUI=1`. On a Linux machine with Mesa offscreen support:

```bash
SDL_VIDEODRIVER=offscreen PHOTOBOOTH_TEST_GUI=1 python -m unittest discover -s tests -v
```

### Drive pool recovery

Use Python 3.12 for the tested Kivy desktop environment. Kivy 2.3.1 does not
provide Python 3.15 wheels for this setup.

An unused folder already has a transaction ID before it is claimed. A temporary
pool verification error must not permanently protect that unused slot as if it
were a customer assignment. The client now revalidates unused staging slots
when the backend returns them as verified READY, while preserving actual claims,
nonempty staging directories, and transaction directories. Do not reset the
counter, delete the cache, or manually mark unverified folders READY.

If Apps Script returns a success response without a `slots` list, the client
reports a protocol error before changing the pool. Update the existing Apps
Script deployment to the repository's `apps_script/Code.gs` using a new version,
and verify the configured `/exec` URL. The current repository backend returns
`slots` for `ensure_folder_pool`; a missing list alone does not prove which
backend or deployment was contacted.

## Dummy payment screen

Template selection now opens a payment simulation before camera capture.
The agreed price is IDR 5,000 per template session (one unit of quantity).
The gallery, cart, and payment use the same tariff from `catalog.py`. The QR contains demo
text, is NOT valid QRIS, and must not be used to transfer money. Only the clearly
labelled simulation button advances to capture. No provider verification or real
payment integration is implemented.

The result screen displays the transaction-folder QR separately from payment.
Its image has a fixed minimum display area inside a scrollable result panel,
so short windows cannot collapse it behind its caption. Printing remains
unimplemented; this is the digital result screen, not printer confirmation.

## Kiosk interface redesign and verification

The Kivy screens now use warm paper backgrounds, sage accents, consistent rounded
cards, a persistent step indicator, and bounded touch controls. Template selection
has a separate order summary; camera capture emphasizes the live image; review
clearly marks the retake target. Critical order, payment, review, and result actions
stay outside scrolling panels. Result QR content is anchored to the top of its
card and retains its quiet zone. All six screens were rendered at 1200x800 and
800x600 during visual QA; small windows use scrollable content instead of overlap.

Controller guards ignore stale payment confirmation and session-acceptance events.
The historical `ui_tkinter.py` remains unchanged.

Validation: 23 automated tests passed with real Kivy widgets and offscreen Mesa.
This includes complete controller orders, per-session retakes, countdown ticks,
local output/manifest persistence, cached Drive folder allocation, offline retry,
unchanged folder QR pixels through an outage, and skipping verified files on retry.
Camera acquisition is tested with a blocking simulated device. QR pixels are
read back from an actual Kivy texture and decoded with OpenCV.

External limitations: the webcam and live Google Apps Script service were not
available to the automated tests; these integrations use deterministic fakes.
Real-device preview latency and account-specific upload permissions still require
operator verification. QRIS remains an explicit simulation, physical printing is
not implemented, and Android packaging/device integration remains out of scope.
The four bundled template artworks are still sample artwork, not final designs.

### Folder QR embedded in the saved output

Every newly composed session PNG now embeds the cached transaction-folder URL
in a dedicated footer. The QR is not merely a GUI widget; it is part of the
same PNG recorded in the manifest and queued for Drive upload. All templates
reserve separate space for photos, IDs, captions, and a black-on-white QR quiet
zone. Integer module scaling prevents resampling blur. No online request is
needed to render the QR, so an offline upload retry keeps the same destination.
Local-only sessions explicitly omit a QR because no Drive URL exists. Existing
saved outputs are not regenerated or overwritten by this change. Physical
printing and thermal-native QR sizing remain part of the future printer adapter.

Validation now includes 24 tests: QR decoding from the saved result of all four
templates and from a controller-generated offline transaction, in addition to
widget, workflow, storage, camera-thread, and retry tests.

### Desktop clipping and order-editing fixes

At 800x600 the previous outer scroll cropped the payment QR, camera preview,
review selection buttons, and result details. Short windows now use smaller
header/heading spacing, content-sized cards, and one row for related actions.
The template gallery and order item lists scroll independently; the payable total
and main actions remain visible. All four order lines are measured at their
natural height instead of clipping the final line. Returning from payment via
**Ubah pesanan** preserves quantities and recalculates the next payment amount.
The tariff remains IDR 5,000 per session; quantity 2 is IDR 10,000.

Validation: **26 tests passed**, including layout bounds and QR decoding from
actual exported screens at 1200x800 and 800x600. The checks also cover scrolling
to the last template, resizing an existing cart, editing payment quantities,
controller capture/retake flow, storage persistence, and offline upload retries.
See [visual evidence and reproduction instructions](docs/qa/README.md).

Generate the 34 real-widget screenshots and a machine-readable report without
camera hardware or Drive credentials:

```bash
SDL_VIDEODRIVER=offscreen python tools/render_gui.py --output-dir /tmp/photobooth-gui-qa
```

On a normal Windows desktop, run `python tools/render_gui.py` without the Linux
environment prefix. Its default output directory is under the system temporary
folder. All illustrated people and Drive destinations in these renders are test
fixtures. Webcam latency and live Drive access were not tested in this run;
QRIS is still a clearly labelled simulation and physical printing is not connected.

### Camera-frame recovery and explicit retake states

Frame availability now updates the camera badge and the welcome, cart, payment,
capture, and retake action gates without rebuilding the screen or losing an order.
An unavailable frame clears the frozen preview and shows an intentional waiting
message. When fresh frames resume, the same session can continue. A failed retake
capture does not consume its allowance. Once that allowance is used, the review
labels the replacement **DIGANTI** and explains **Retake sudah digunakan** instead
of inviting another retake.

Payment confirmation is tied to its original button and order. A late callback
from a payment screen replaced by an edited order cannot submit old quantities.
A rejected confirmation can be retried after camera recovery, while successful
submissions remain one-shot. The unpaid cart remains editable while waiting for
the camera; creating a transaction still requires a fresh frame.

Validation: **32 tests passed**, including real pointer events on both desktop
sizes, synthetic frame loss/recovery, a failed-then-successful retake, payment
retry, stale payment callbacks, and the existing controller/storage/Drive retry
checks. **28 real-widget renders** include waiting-camera and exhausted-retake
states; the camera overlay is checked against its own bounds as well as the
window. Updated [visual evidence](docs/qa/README.md) contains these extra states.

This recovery applies when an already-open camera starts delivering fresh frames
again. Reopening a lost USB handle is not implemented or tested; a physical
disconnect may still need operator intervention. All camera and Drive scenarios
in automated validation use fakes, not a live webcam or Google account.

### Selection feedback and retired-action safety

The template gallery now derives a subtle selected outline/tint from each
nonzero quantity. Decreasing a quantity to zero removes the highlight and disables
its minus button. The cart total and the agreed IDR 5,000/session tariff are
unchanged; two sessions still total IDR 10,000. New renders cover empty, partly
selected, fully selected, and scrolled galleries at both supported desktop sizes.

Every page button belongs to that exact screen revision. Disabled controls and
late releases from retired pages are ignored, even when a new order displays
another page with the same name. This prevents an old **Ubah pesanan** from
restoring stale quantities or an old **Selesai** from ending the next customer's
order. Modal close buttons remain tied to their own popup, so error dialogs can
still be dismissed after the underlying page changes.

The controller independently permits completion only on the last accepted
result, after all ordered sessions have local outputs. Pending Drive uploads do
not block completion. Validation: **38 tests passed** and **32 real-widget renders**
completed, including the 60-second automatic return, stale navigation/completion,
popup dismissal, selected-card state, and the existing capture/storage/retry and
painted-QR checks. See the updated [visual evidence](docs/qa/README.md).

### Review matches the final photo crop

Review previously displayed the full camera frame, while the saved composition
center-cropped each photo into a 470x500 aperture. Content visible at the edges
during review could therefore disappear after acceptance. Review now uses the
same crop function as composition, including the replacement photo after a
retake. All three thumbnails keep that aspect ratio without stretching.

The live camera still shows its full field of view; its caption directs the
customer to check the final crop during review. Raw photos remain full-sized,
and the established output crop, 1800x1000 composition, folder QR, pricing,
and previously saved results are unchanged.

Validation: **40 tests passed** and **32 real-widget renders** completed at both
desktop sizes. New checks compare GPU review pixels with saved output frames
before/after retake, using landscape, portrait, and square sources. They also
verify that source files and existing output bytes are not modified by review.
The render report records exact crop agreement in all six review states.
Camera and Drive checks still use fakes; no live-device claim is implied.

### Upload progress follows the saved file revision

A save retry can replace a retake or output at the same relative path. Previously,
merging the worker's old record could copy its `VERIFIED` flag onto different
local bytes. This was reproduced through the controller after a simulated failure
to record retake metadata, as well as with a delayed upload response.

Each new app save now carries a local `content_version`. Controller and worker
merges retain progress only for that revision. Old success, failure, and resumable
URLs cannot certify or block its replacement. Existing manifests without the field
remain readable; unchanged verified files are not uploaded again. Folder names,
transaction IDs, relative paths, and QR destinations are unchanged.

The backend policy still matters: direct Drive API uploads can update the existing
file; the current Apps Script deliberately returns a conflict for different bytes
at an existing path. That case now stays `ACTION_REQUIRED`, with the new photo
retained locally, instead of falsely claiming it was uploaded. This does not
bypass the backend's overwrite protection or require a new Apps Script deployment.

Validation: **48 tests passed**, including same-path save retries, late success and
failure callbacks, legacy records, output replacement, and the controller failure
path. **32 real-widget renders** passed at 1200x800 and 800x600; their report and all
six contact sheets are byte-identical to the previous visual evidence, so no
cosmetic layout changes were made. All camera and Drive scenarios still use fakes.

### Readable disabled controls

Disabled labels still explain important states such as **DIGANTI**, **Tersimpan**,
and **RETAKE SUDAH DIGUNAKAN**. Their old translucent default background and faint
text produced only about 1.44–1.85:1 contrast in targeted rendered samples. Disabled
controls now use a flat muted fill and darker ink; enabled primary/secondary colors
return when the same widget becomes available again. Sizes, positions, camera
gates, retake quota, and disabled-click protection are unchanged.

Validation: **49 tests passed** and **32 real-widget renders** completed. The render
report samples actual painted pixels for **28 visible disabled labels**, measuring
about **5.14–5.22:1** against the background. The project's regression threshold is
4.5:1; this targeted text-color check is not a full accessibility audit. Updated
state/selection sheets show the change; the six-main-screen overview sheets remain
byte-identical. Price remains Rp5.000/session, including Rp10.000 for quantity 2.

The renderer now schedules each capture after its own setup instead of queuing
all deadlines before startup. This avoids a slow font/plugin initialization
executing setup and capture in the same frame. Layout, QR decoding, and crop
assertions remain strict. Camera/Drive checks still use fakes; QRIS is simulated
and physical printing is not connected.

### Complete diagnostics without a crowded footer

Long storage/backend messages previously wrapped into a fixed-height footer and
were silently cropped. A reproduced 800x600 diagnostic needed 105px of text in a
26px row; the same message also exceeded the 34px row at 1200x800. The footer now
shows one line with an ellipsis and a compact **DETAIL** action only when needed.
It opens the existing scrollable dialog with the complete message. Normal short
statuses reserve no extra button or spacing.

The public status text remains complete for camera-loss/recovery bookkeeping.
Details are a read-only snapshot; opening, scrolling, or closing them does not
rebuild the cart or change storage gates. Font extents are measured on the CPU
instead of creating a potentially oversized single-line graphics texture. The
action also appears/disappears in place when a window resize changes available
width, without oscillating near the breakpoint.

Validation: **51 tests passed** and **34 real-widget renders** completed at both
desktop sizes. Tests cover full-message access, scrolling to the end, animated
dismissal, breakpoint stability, and storage recovery with the same two-session
cart (Rp10.000). New [diagnostic sheets](docs/qa/README.md) compare unavailable
storage with a ready cart. All six earlier contact sheets remain byte-identical.
Camera and Drive scenarios still use fakes, not live devices/services.

### Alpha-correct visual evidence

The compact QA sheets previously pasted RGBA widget exports directly into RGB.
That discarded the transparent rounded shell corners and exposed their hidden
black channels as marks. The sheet builder now composites onto its paper
background before resizing, including partially transparent edge pixels.
Full-size source renders are not rewritten, and no application layout changed.

Validation: **52 tests passed** and **34 real-widget renders** completed at both
desktop sizes. A new regression first failed at both sizes, then passed for
transparent, partially transparent, and opaque RGB input while checking source
bytes remain untouched. All eight sheets were inspected visually. Pixel
comparison confines their changes to rounded corners; their content and the
machine-readable layout/QR report remain identical. See the updated
[evidence and validation details](docs/qa/README.md). Camera and Drive still use
fakes, QRIS is simulated, and physical printing is not connected.
