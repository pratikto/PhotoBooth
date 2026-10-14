# PhotoBooth

A Python photo booth application built with Tkinter and OpenCV. The repository currently contains an early single-photo prototype; the transaction workflow below documents the agreed product behavior that the application is intended to grow into.

## Current prototype

The code currently:

- Shows a live preview from a built-in or USB camera.
- Captures the current camera frame and saves it as a local JPEG.
- Attempts to upload each captured photo to Google Drive through a Google Apps Script web app.
- Displays a QR code for the individual photo after its upload succeeds.
- Keeps the local photo and displays an error if upload fails.

The complete multi-template, payment, printing, transaction-folder, and offline-reservation flow described below is not implemented yet. In particular, the current QR points to one uploaded photo, not to a transaction folder.

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

Use this folder-name pattern:

**PB001_yymmdd_hhmmss**

The transaction folder contains both:

- The raw photos captured by the camera.
- The final photo output for each template session.

A folder slot must be created before the transaction timestamp is known. When a slot is claimed, record the final transaction name against its Drive folder ID. If the booth is offline, keep that rename request locally and apply it when the connection returns. Keep using the cached Drive folder ID and URL as the stable folder-link destination for the QR.

The application should handle same-second name collisions safely; the Drive folder ID and the local transaction record should remain the unique identifiers.

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

The current prototype uses a local configuration file, `photobooth/local_settings.py`, for the Google Apps Script web app URL and upload token. That file is ignored by Git; keep its credentials private and do not commit it.

Run the current prototype with:

    python main.py

## Troubleshooting

- The application uses camera index 0 by default. If the USB camera is not detected, check the camera index configured in `photobooth/camera.py`.
- On Windows, allow desktop applications to access the camera in Settings > Privacy & security > Camera.
- Close other applications that may be using the camera, such as Zoom, Teams, or Camera.
- If Drive upload fails, the current prototype keeps the JPEG locally and reports the error. Its offline queue and reserved transaction-folder behavior are planned requirements, not current functionality.

## Project structure

- `main.py` starts the application.
- `photobooth/app.py` coordinates the camera, UI, local photo saving, Drive upload, and QR display.
- `photobooth/camera.py` manages the camera connection and frame capture.
- `photobooth/photo_storage.py` saves captured photos locally.
- `photobooth/drive_storage.py` uploads the current prototype's individual photos through Apps Script.
- `photobooth/qr_code.py` creates QR-code images.
- `photobooth/ui_tkinter.py` builds the current Tkinter interface.
- `requirements.txt` lists the Python packages used by the current prototype.
- The `photos` folder, local configuration, and temporary Python files are excluded from Git.
