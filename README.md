# PhotoBooth

A Python photo booth application built with Tkinter, OpenCV, and Pillow. The attached procedure document is the functional source of truth. QRIS and printing are intentionally out of the current implementation until those integrations are ready.

## Current implementation: photo and Drive flow

The first implementation milestone includes:

- A welcome screen and a template picker with a cart-style session summary.
- Four sample template cards. Their artwork is illustrative and should be replaced with the final template designs.
- Quantity means separate sessions. Each session captures three new photos and receives one retake of a selected photo.
- A five-second countdown before each capture.
- A final digital photo composition saved locally for each session.
- One transaction folder slot for all sessions in an order, named with the booth ID and an incrementing eight-digit counter, such as PB001_00000001.
- A persistent local pool targeting at least 25 verified, pre-created Drive folders. New transactions are blocked when no ready slot is available.
- A cached folder ID and URL for each slot, so an assigned transaction can continue offline and show the same folder QR.
- A local manifest and resumable upload queue. Uploads are identified by transaction-relative path, checked by size and checksum, and retained locally until verified in Drive.

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

The Drive folder slot exists before it has a transaction ID. When a slot is claimed, record the assigned ID and final folder name against its Drive folder ID. If the booth is offline, keep that rename request locally and apply it when the connection returns. Keep using the cached Drive folder ID and URL as the stable folder-link destination for the QR.

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
- Show the completed folder QR after upload succeeds.

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

Configure these environment variables for the booth:

- `PHOTOBOOTH_ID` — booth code, default `PB001`.
- `PHOTOBOOTH_DRIVE_PARENT_ID` — Drive folder ID where the application creates its slot folders.
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, and `GOOGLE_OAUTH_REFRESH_TOKEN` — OAuth credentials authorized for Google Drive API access.
- `PHOTOBOOTH_CAMERA_INDEX` — camera index, default `0`.

Enable the Google Drive API and authorize the OAuth refresh token with Drive access for the intended account. The account needs permission to create folders, set link sharing, rename folders, and upload files under the configured parent. Keep OAuth credentials outside the repository. On startup, the app verifies the cached pool, creates and validates folders to restore the target of 25 ready slots, and resumes pending folder renames and uploads.

For UI and camera development without Drive credentials, set `PHOTOBOOTH_LOCAL_ONLY=1`. This mode stores results only on the device and does not produce a Drive QR; do not use it for booth operations.

Run the local MVP with:

    python main.py

## Troubleshooting

- The application uses camera index 0 by default. If the USB camera is not detected, check the camera index configured in `photobooth/camera.py`.
- On Windows, allow desktop applications to access the camera in Settings > Privacy & security > Camera.
- Close other applications that may be using the camera, such as Zoom, Teams, or Camera.
- Photos and transaction manifests are stored under `photos/<transaction-id>`. Preserve `data/booth_state.json` and `data/drive_pool.json` with the transaction ledger and folder-link cache.
- If there are no ready Drive slots, check internet access, OAuth credentials, the configured parent folder, Drive API access, and available storage quota. New transactions remain disabled until a slot is verified.
- An `ACTION_REQUIRED` upload or slot remains on the device for staff attention; the application does not delete Drive content or pending local files.
- QRIS and printer integration are not connected to the current UI.

## Project structure

- main.py starts the application.
- photobooth/app.py coordinates the camera, screens, and session flow.
- photobooth/ui_tkinter.py builds the Tkinter interface styled after the procedure mockups.
- photobooth/catalog.py contains the sample templates and digital photo-strip compositor.
- photobooth/workflow.py expands quantities into sessions and enforces one retake per session.
- photobooth/transaction_store.py reserves transaction IDs and writes local photos and manifests.
- photobooth/camera.py manages the camera connection and frame capture.
- photobooth/drive_storage.py handles Drive folder creation, sharing, resumable uploads, and verification.
- photobooth/drive_pool.py maintains the local cache of ready and assigned Drive slots.
- photobooth/drive_sync.py resumes folder renames and pending transaction uploads in the background.
- photobooth/qr_code.py creates the transaction folder QR shown on the result screen.
- requirements.txt lists the Python packages used by the project.
- photos/, data/, local configuration, and temporary Python files are excluded from Git.
