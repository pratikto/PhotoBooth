# PhotoBooth

A Python photo booth application built with Kivy, OpenCV, and Pillow. The attached procedure document is the functional source of truth. QRIS and printing are intentionally out of the current implementation until those integrations are ready.

## Current implementation: photo and Drive flow

The first implementation milestone includes:

- A welcome screen and a template picker with a cart-style session summary.
- Four sample template cards. Their artwork is illustrative and should be replaced with the final template designs.
- Quantity means separate sessions. Each session captures three new photos and receives one retake of a selected photo.
- A five-second countdown before each capture.
- A final digital photo composition saved locally for each session.
- One transaction folder slot for all sessions in an order, named with the booth ID and an incrementing eight-digit counter, such as PB001_00000001.
- A persistent local pool targeting at least 25 verified Drive folders. Each folder is created with its final incrementing transaction ID, so assignment does not rename it.
- A cached folder ID and URL for each slot, so an assigned transaction can continue offline and show the same folder QR.
- A local manifest and retryable upload queue. Uploads are identified by transaction-relative path, checked by size and checksum, and retained locally until verified in Drive. Direct OAuth uploads are resumable; the Apps Script backend retries whole files idempotently.

QRIS payment and printing are not implemented. The bundled template artwork is illustrative and should be replaced with the final designs before operating the booth.

Payment and printing sections below describe the procedure's target behavior and are not part of this implementation.

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

The retake allowance resets for each new session. It does not reset between attempts within the same session.

### 5. Show progress and finish the order

The interface should show the customer's progress through the order. For orders with quantity greater than one, show both the template and the current session, for example “Template 1 of 2 — Session 1 of 2.”

- Show **Next** only when another ordered session remains.
- On the final session, show **Selesai** instead.
- After completion, show a visible 60-second countdown before returning to the start screen.

### 6. Upload results and provide the folder QR

The QR printed with the photo points to the transaction folder, so the customer can find the raw photos and template results together.

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

The print screen should expose these states:

- **Sedang mencetak** — disable the print action while the printer job is running.
- **Berhasil** — confirm that printing completed.
- **Gagal, coba lagi** — provide a retry path after a failure.

A retry must not create a duplicate print job or duplicate order output. Track each print job so the application can distinguish a retry from a new print request.

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

## Troubleshooting

- The application uses camera index 0 by default. If the USB camera is not detected, check the camera index configured in `photobooth/camera.py`.
- On Windows, allow desktop applications to access the camera in Settings > Privacy & security > Camera.
- Close other applications that may be using the camera, such as Zoom, Teams, or Camera.
- Photos and transaction manifests are stored under `photos/<transaction-id>`. Preserve `data/booth_state.json` and `data/drive_pool.json` with the transaction ledger and folder-link cache.
- If there are no ready Drive slots, check internet access and Apps Script configuration. The deployed Web App must include the actions in `apps_script/Code.gs`; the original upload-only deployment cannot create transaction folders. New transactions remain disabled until a slot is verified.
- An `ACTION_REQUIRED` upload or slot remains on the device for staff attention; the application does not delete Drive content or pending local files.
- QRIS and printer integration are not connected to the current UI.

## Project structure

- main.py starts the application.
- photobooth/app.py coordinates the camera, screens, and session flow.
- photobooth/ui_kivy.py builds the active Kivy interface and adapts controller timers to Kivy Clock.
- photobooth/ui_tkinter.py preserves the previous Tkinter GUI unchanged as history.
- photobooth/catalog.py contains the sample templates and digital photo-strip compositor.
- photobooth/workflow.py expands quantities into sessions and enforces one retake per session.
- photobooth/transaction_store.py reserves transaction IDs and writes local photos and manifests.
- photobooth/camera.py manages the camera connection and frame capture.
- photobooth/drive_storage.py handles Apps Script and direct OAuth Drive operations, sharing, uploads, and verification.
- photobooth/drive_pool.py maintains the local cache of ready and assigned Drive slots.
- photobooth/drive_sync.py syncs slot assignments and pending transaction uploads in the background.
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

Generate the 32 real-widget screenshots and a machine-readable report without
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
