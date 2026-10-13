"""
Application controller for the PhotoBooth project.

This module connects the main parts of the application:

* ``Camera`` reads frames from the connected camera.
* ``PhotoBoothUI`` creates the Tkinter window and displays the interface.
* ``photo_storage`` saves each captured photo on this computer.
* ``drive_storage`` uploads the saved photo to Google Drive through the
  configured web app.
* ``qr_code`` creates a QR image from the uploaded photo's Drive URL.

The user interface is deliberately kept in ``ui_tkinter.py``. This class
controls the application workflow and asks the UI object to display things,
but it does not create individual Tkinter labels, buttons, or pop-up windows.
"""

from threading import Thread
import tkinter as tk

import cv2
from PIL import Image

from photobooth.camera import Camera
from photobooth.drive_storage import DriveUploadError, upload_photo
from photobooth.photo_storage import save_photo
from photobooth.qr_code import create_qr_image
from photobooth.ui_tkinter import PhotoBoothUI


class PhotoBoothApp:
    """Coordinate the camera, interface, local storage, and Drive upload."""

    def __init__(self):
        """Prepare the app's shared objects and schedule camera startup.

        The Tkinter root window must be created before ``PhotoBoothUI`` can
        use it. The camera and ``current_frame`` also belong to the application
        controller because they are used by the capture and preview workflow.
        """

        # Create the single main Tkinter window.
        # PhotoBoothUI receives this existing window and adds the interface to it.
        self.root = tk.Tk()

        # Create the camera controller. Camera() uses the default camera device
        # configured by photobooth/camera.py (commonly camera index 0).
        self.camera = Camera()

        # No frame is available until the camera is opened and the first frame
        # is successfully read by _update_preview().
        self.current_frame = None

        # Background upload work must not schedule new UI updates after shutdown.
        self._is_closing = False

        # Create the user interface and connect its button/window events to
        # the application actions defined in this class.
        self.ui = PhotoBoothUI(
            root=self.root,
            on_capture=self._capture_photo,
            on_close=self.close,
        )

        # Wait briefly before opening the camera. This gives Tkinter time to
        # create and draw the main window before camera setup begins.
        self.root.after(100, self._connect_camera)

    def _connect_camera(self):
        """Open the camera and begin updating the live preview.

        This method is scheduled by Tkinter after the main window is created.
        If the camera cannot be opened, the UI explains the problem and leaves
        the Capture button disabled.
        """

        # The scheduled callback may run after shutdown was requested.
        # In that case, do not try to access the camera or update the interface.
        if self._is_closing:
            return

        # Let the user know that the application is trying to open the camera.
        self.ui.set_status("Connecting to camera...")

        # Ask the Camera object to open the configured camera device.
        # Camera.open() is expected to return True on success and False on failure.
        if not self.camera.open():
            # Display a clear message in both the status area and preview area.
            self.ui.set_status(
                "Camera not detected. Check the camera connection."
            )
            self.ui.show_preview_message("CAMERA NOT DETECTED")

            # Capturing is not possible until a camera is available.
            self.ui.set_capture_enabled(False)
            return

        # The camera is ready, so allow the user to take a photo.
        self.ui.set_status("Camera connected. Ready to take a photo.")
        self.ui.set_capture_enabled(True)

        # Start the repeating camera-read and preview-display cycle.
        self._update_preview()

    def _update_preview(self):
        """Read one camera frame, display it, and schedule the next frame.

        Tkinter's ``after`` method schedules the next update without blocking
        the GUI event loop. That allows the window to keep responding to clicks
        while the camera preview is refreshed.
        """

        # Stop the preview loop when the user closes the application.
        if self._is_closing:
            return

        # Read the newest frame from the camera. The Camera class returns a
        # NumPy array on success, or None when no frame is currently available.
        frame = self.camera.read()

        if frame is None:
            # A temporary missing frame can happen while a camera starts up.
            # Show a short status message and retry after a small delay.
            self.ui.set_status("Waiting for a frame from the camera...")
            self.root.after(250, self._update_preview)
            return

        # Keep the most recent frame so the Capture button can save it.
        # OpenCV represents camera images in BGR color order by default.
        self.current_frame = frame

        # Pillow and Tkinter expect the usual RGB color order. Convert the frame
        # before displaying it so red and blue are not swapped in the preview.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the RGB NumPy array to a Pillow image. The UI class handles
        # resizing the image to fit its preview area and displaying it.
        preview_image = Image.fromarray(frame_rgb)
        self.ui.show_preview(preview_image)

        # Schedule the next preview frame. A 15 ms interval aims for a smooth
        # preview while still giving Tkinter time to process other events.
        self.root.after(15, self._update_preview)

    def _capture_photo(self):
        """Save the latest camera frame locally and start its Drive upload.

        This method runs on Tkinter's main thread because it is called by the
        Capture button. The network upload itself is started on a background
        thread so a slow connection does not freeze the window or preview.
        """

        # Do not try to save an image before the camera has provided a frame.
        if self.current_frame is None:
            self.ui.set_status("No photo is available yet.")
            return

        # Save a copy so later camera updates cannot change the image being saved.
        # save_photo() returns a path on success, or None if saving failed.
        photo_path = save_photo(self.current_frame.copy())

        if photo_path is None:
            # The image could not be written to local storage, so there is
            # nothing available to upload. Keep the app ready for another try.
            self.ui.set_status("Could not save the photo locally.")
            return

        # Disable the Capture button until this upload finishes. This prevents
        # a second click from starting another upload at the same time.
        self.ui.set_capture_enabled(False)

        # Confirm that the local copy exists and tell the user which file is
        # currently being uploaded.
        self.ui.set_status(
            f"Photo saved locally. Uploading {photo_path.name}..."
        )

        # Network requests can take a while. Run the upload in a daemon thread
        # so the Tkinter event loop remains free to update the screen. A daemon
        # thread will not keep the Python process alive after the app closes.
        upload_thread = Thread(
            target=self._upload_photo_in_background,
            args=(photo_path,),
            daemon=True,
        )
        upload_thread.start()

    def _upload_photo_in_background(self, photo_path):
        """Upload one local photo and schedule the result for the UI thread.

        Tkinter widgets should only be changed by the thread running Tkinter's
        event loop. Therefore, this worker method performs the network request,
        then asks ``_schedule_ui_update`` to run the appropriate result handler.
        """

        try:
            # upload_photo() sends the local file to the configured web app and
            # returns the resulting Google Drive URL when it succeeds.
            file_url = upload_photo(photo_path)

        except DriveUploadError as error:
            # DriveUploadError represents an expected upload problem, such as
            # a network issue, invalid configuration, or a rejected request.
            error_message = str(error)

            # Queue the error handling on Tkinter's main thread. Default values
            # in the lambda preserve the current path and message until the
            # callback runs.
            self._schedule_ui_update(
                lambda message=error_message, path=photo_path:
                    self._show_upload_error(path, message)
            )
            return

        except Exception as error:
            # Handle unexpected errors too, so the user is not left with a
            # disabled button and no explanation if another failure occurs.
            error_message = f"Unexpected error: {error}"

            # The error dialog and status message must be shown on the Tkinter
            # thread, so schedule the existing UI handler rather than calling
            # it directly from this worker thread.
            self._schedule_ui_update(
                lambda message=error_message, path=photo_path:
                    self._show_upload_error(path, message)
            )
            return

        # The upload succeeded. Schedule QR creation and display on the GUI
        # thread because displaying the QR code uses Tkinter UI components.
        self._schedule_ui_update(
            lambda url=file_url, path=photo_path:
                self._show_qr_code(path, url)
        )

    def _schedule_ui_update(self, callback):
        """Queue a callback to run in Tkinter's main event loop.

        This helper is used by the background upload thread. Calling Tkinter
        widgets directly from a worker thread can cause intermittent errors,
        so the callback is handed back to the main window with ``after``.
        """

        # Ignore results that arrive after the user has closed the application.
        if self._is_closing:
            return

        try:
            # A delay of zero means Tkinter should run the callback as soon as
            # it can process it on the main GUI event loop.
            self.root.after(0, callback)

        except (tk.TclError, RuntimeError):
            # The window may have been destroyed just as the upload completed.
            # In that case, Tkinter cannot accept the callback and no UI update
            # is needed because the application is already closing.
            pass

    def _show_qr_code(self, photo_path, file_url):
        """Create and display a QR code for the successfully uploaded photo.

        This callback runs on Tkinter's main thread. ``PhotoBoothUI`` creates
        the QR pop-up; this method only prepares the image and updates status.
        """

        try:
            # Convert the Drive URL into a QR-code image that Pillow can handle.
            qr_image = create_qr_image(file_url)

            # Ask the UI class to create its QR pop-up and show the image.
            self.ui.show_qr_code(qr_image)

        except Exception as error:
            # The photo has already uploaded, but QR generation or display did
            # not work. Keep the Drive link available to the user as a fallback.
            self.ui.set_status(
                "Photo uploaded, but the QR code could not be displayed."
            )
            self.ui.set_capture_enabled(True)
            self.ui.show_error(
                "QR code could not be displayed",
                "The photo was uploaded, but the QR code could not be created.\n\n"
                f"Details: {error}\n\n"
                f"Photo link:\n{file_url}",
            )
            return

        # Tell the user which photo was uploaded and allow another capture.
        self.ui.set_status(f"Photo uploaded: {photo_path.name}")
        self.ui.set_capture_enabled(True)

    def _show_upload_error(self, photo_path, error_message):
        """Show an upload failure while preserving the local photo copy.

        This method is scheduled on Tkinter's main thread. The local image was
        saved before uploading began, so an upload failure does not delete it.
        """

        # Make clear that the photo is still available on this computer.
        self.ui.set_status(
            f"Upload failed. Local copy kept: {photo_path.name}"
        )

        # Re-enable capture so the user can continue using the photo booth.
        self.ui.set_capture_enabled(True)

        # Display both the reason for the upload failure and the local path.
        self.ui.show_error(
            "Photo upload failed",
            f"{error_message}\n\n"
            f"The photo is still saved locally at:\n{photo_path}",
        )

    def close(self):
        """Stop future updates, release the camera, and close the window."""

        # Make shutdown idempotent: if close is requested more than once,
        # do not try to release the camera or destroy the window a second time.
        if self._is_closing:
            return

        # Tell preview callbacks and upload-result callbacks to stop scheduling
        # work for a window that is about to be destroyed.
        self._is_closing = True

        try:
            # Release the camera device so another application can use it.
            self.camera.close()
        finally:
            # Always close the Tkinter window, even if camera cleanup fails.
            try:
                self.root.destroy()
            except tk.TclError:
                # The root may already have been destroyed by Tkinter.
                pass

    def run(self):
        """Start Tkinter's event loop and keep the application running."""

        # mainloop() waits for user actions and scheduled callbacks. It also
        # allows the camera preview and upload-result callbacks to be processed.
        self.root.mainloop()
