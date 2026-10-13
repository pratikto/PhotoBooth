# Thread runs the Google Drive upload in the background.
# This keeps the camera preview and the application window responsive
# while the photo is being sent over the internet.
from threading import Thread

# tkinter provides the application window, labels, frames, and buttons.
import tkinter as tk

# messagebox displays popup messages when an upload or QR operation fails.
from tkinter import messagebox

# OpenCV reads images from the camera and converts their color format.
import cv2

# Pillow converts camera frames and QR images into images Tkinter can display.
from PIL import Image, ImageTk

# Camera manages opening, reading, and closing the camera device.
from photobooth.camera import Camera

# upload_photo sends a local photo to Apps Script and returns its Drive URL.
# DriveUploadError is the expected error type when that upload fails.
from photobooth.drive_storage import DriveUploadError, upload_photo

# save_photo writes a captured frame into the local photos folder.
from photobooth.photo_storage import save_photo

# create_qr_image converts the Google Drive URL into a QR code image.
from photobooth.qr_code import create_qr_image


class PhotoBoothApp:
    """
    Main application class for the photo booth.

    This class creates the Tkinter window, displays the live camera preview,
    handles photo capture, uploads photos to Google Drive, and displays
    a QR code for each successfully uploaded photo.
    """

    def __init__(self):
        # Create the main Tkinter window.
        # This is the parent window for the preview, button, and status label.
        self.root = tk.Tk()

        # Set the text shown in the window's title bar.
        self.root.title("Photo Booth")

        # Set the initial window size in pixels: width x height.
        self.root.geometry("900x700")

        # Give the main window a dark background color.
        self.root.configure(bg="#111827")

        # Create a Camera object for camera device index 0.
        # Index 0 is usually the laptop's built-in camera or the first USB camera.
        self.camera = Camera(camera_index=0)

        # Store the newest unmodified camera frame here.
        # The capture button uses this frame to save the photo.
        # None means that the camera has not provided a frame yet.
        self.current_frame = None

        # Tkinter needs a persistent reference to images displayed in labels.
        # This variable keeps the current preview image from being removed
        # by Python's automatic memory cleanup.
        self.preview_image = None

        # This flag tells background work not to schedule GUI updates
        # after the user has closed the application.
        self._is_closing = False

        # Create the visible parts of the application:
        # the title, camera preview, capture button, and status text.
        self._create_widgets()

        # Bind the Escape key to the close method.
        # Tkinter passes a keyboard event to the callback, so the lambda
        # accepts "event" and then calls close().
        self.root.bind("<Escape>", lambda event: self.close())

        # Also call close() when the user clicks the X button
        # in the title bar.
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Wait 100 milliseconds before opening the camera.
        # This gives Tkinter a moment to draw the window first.
        self.root.after(100, self._connect_camera)

    def _create_widgets(self):
        """
        Create and position the labels, preview area, and capture button.
        """

        # Create the main heading at the top of the window.
        title = tk.Label(
            self.root,
            text="PHOTO BOOTH",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="#111827",
        )

        # Display the heading and add vertical spacing around it.
        title.pack(pady=(30, 10))

        # Create a fixed-size frame that will hold the camera preview.
        # The frame has a dark background while the camera is connecting.
        preview = tk.Frame(
            self.root,
            width=700,
            height=380,
            bg="#1f2937",
            highlightthickness=1,
            highlightbackground="#374151",
        )

        # Place the preview frame in the center of the window.
        preview.pack(pady=20)

        # By default, Tkinter may resize a frame to fit its contents.
        # Disable that behavior so the preview remains 700 x 380 pixels.
        preview.pack_propagate(False)

        # Create the label that will show either a connection message
        # or the current camera image.
        self.preview_label = tk.Label(
            preview,
            text="CONNECTING TO CAMERA...",
            font=("Arial", 16, "bold"),
            fg="#9ca3af",
            bg="#1f2937",
        )

        # Center the preview label inside its frame.
        self.preview_label.pack(expand=True)

        # Create the button that captures and uploads a photo.
        # It starts disabled and becomes active after the camera connects.
        self.capture_button = tk.Button(
            self.root,
            text="TAKE PHOTO",
            command=self._capture_photo,
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2563eb",
            activebackground="#1d4ed8",
            activeforeground="white",
            disabledforeground="#9ca3af",
            relief=tk.FLAT,
            padx=30,
            pady=12,
            state=tk.DISABLED,
        )

        # Display the capture button beneath the preview.
        self.capture_button.pack(pady=5)

        # Create a label for short messages such as camera status,
        # upload progress, or the name of the saved photo.
        self.status_label = tk.Label(
            self.root,
            text="Starting photo booth...",
            font=("Arial", 11),
            fg="#9ca3af",
            bg="#111827",
        )

        # Display the status label below the capture button.
        self.status_label.pack(pady=10)

    def _connect_camera(self):
        """
        Open the camera and start the live preview if it is available.
        """

        # If the app was closed before this scheduled method ran,
        # there is no reason to continue opening the camera.
        if self._is_closing:
            return

        # Tell the user that the app is currently trying to open the camera.
        self.status_label.config(text="Connecting to camera...")

        # Ask the Camera object to open the selected camera device.
        # If open() returns False, the camera could not be opened.
        if not self.camera.open():
            # Show an error in the status area.
            self.status_label.config(
                text="Camera not detected. Check the camera connection."
            )

            # Replace the connection message in the preview area with an error.
            # Setting image="" removes any image currently shown by the label.
            self.preview_label.config(
                text="CAMERA NOT DETECTED",
                image="",
            )

            # Stop this method. The capture button stays disabled.
            return

        # Tell the user that the camera connection succeeded.
        self.status_label.config(text="Camera connected. Ready to take a photo.")

        # The camera is ready, so allow the user to capture a photo.
        self.capture_button.config(state=tk.NORMAL)

        # Start the repeating process that reads and displays camera frames.
        self._update_preview()

    def _update_preview(self):
        """
        Read one camera frame, display it, and schedule the next frame update.
        """

        # Stop if the app is closing; do not read or schedule more camera frames.
        if self._is_closing:
            return

        # Ask the Camera object for the newest frame from the camera.
        # A successful frame is an image represented as a NumPy array.
        frame = self.camera.read()

        # If the camera did not provide a frame, show a status message
        # and try again shortly.
        if frame is None:
            self.status_label.config(text="Waiting for a frame from the camera...")

            # Try reading again in 250 milliseconds.
            # root.after schedules the retry without pausing the whole GUI.
            self.root.after(250, self._update_preview)
            return

        # Keep the latest camera frame for the capture button.
        # OpenCV supplies the original frame in BGR color order.
        self.current_frame = frame

        # Tkinter/Pillow display colors in RGB order.
        # Convert BGR to RGB so the preview colors look correct.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the NumPy array into a Pillow image.
        preview_image = Image.fromarray(frame_rgb)

        # Shrink the preview image, if needed, to fit inside the preview frame.
        # This changes only the displayed copy; current_frame remains full-size.
        preview_image.thumbnail((700, 380))

        # Convert the Pillow image into a Tkinter-compatible image.
        self.preview_image = ImageTk.PhotoImage(preview_image)

        # Tell the preview label to display the new image.
        # Setting text="" removes the earlier connection message.
        self.preview_label.config(
            image=self.preview_image,
            text="",
        )

        # Schedule the next preview update in 15 milliseconds.
        # This keeps the video preview moving while allowing Tkinter
        # to process button clicks and other window events.
        self.root.after(15, self._update_preview)

    def _capture_photo(self):
        """
        Save the newest camera frame locally, then start its Drive upload.
        """

        # Do not capture if the camera has not supplied any frame yet.
        if self.current_frame is None:
            self.status_label.config(text="No photo is available yet.")
            return

        # Save a copy of the newest frame to the local photos folder.
        # Using copy() keeps the saved image separate from the live preview frame.
        photo_path = save_photo(self.current_frame.copy())

        # save_photo() returns None if writing the file failed.
        # If so, there is no local photo to upload.
        if photo_path is None:
            self.status_label.config(text="Could not save the photo locally.")
            return

        # Disable the button while this photo is being uploaded.
        # This prevents multiple uploads from starting at the same time.
        self.capture_button.config(state=tk.DISABLED)

        # Tell the user that the local save succeeded and upload has started.
        self.status_label.config(
            text=f"Photo saved locally. Uploading {photo_path.name}..."
        )

        # Create a background thread for the internet upload.
        # Without this thread, a slow upload could freeze the camera preview
        # and make the app appear unresponsive.
        upload_thread = Thread(
            # Run this method in the new thread.
            target=self._upload_photo_in_background,

            # Pass the local photo path to the method.
            args=(photo_path,),

            # Let the thread stop when the app closes.
            daemon=True,
        )

        # Start uploading in the background.
        upload_thread.start()

    def _upload_photo_in_background(self, photo_path):
        """
        Upload the photo without blocking the Tkinter event loop.
        """

        # Call upload_photo() from drive_storage.py.
        # It sends the image to Apps Script and returns the Drive link.
        try:
            file_url = upload_photo(photo_path)

        except DriveUploadError as error:
            # This is an expected upload failure, such as a network error,
            # incorrect token, missing setting, or Drive rejection.
            error_message = str(error)

            # Do not change Tkinter widgets directly from this worker thread.
            # Schedule the error handling on Tkinter's main event loop instead.
            #
            # The lambda's default arguments keep these values available
            # until Tkinter runs the callback.
            self._schedule_ui_update(
                lambda message=error_message, path=photo_path:
                    self._show_upload_error(path, message)
            )
            return

        except Exception as error:
            # Catch unexpected errors so the thread does not stop without
            # informing the user.
            error_message = f"Unexpected error: {error}"

            # Schedule the error popup and status update on the GUI thread.
            self._schedule_ui_update(
                lambda message=error_message, path=photo_path:
                    self._show_upload_error(path, message)
            )
            return

        # The upload succeeded. Ask the GUI thread to create and show
        # the QR code for the returned Drive URL.
        self._schedule_ui_update(
            lambda url=file_url, path=photo_path:
                self._show_qr_code(path, url)
        )

    def _schedule_ui_update(self, callback):
        """
        Ask Tkinter to run a callback through the main GUI event loop.
        """

        # Do not queue GUI work after the user has closed the application.
        if self._is_closing:
            return

        # root.after(0, callback) puts the callback into Tkinter's event queue.
        # Tkinter will run it as part of the main GUI loop.
        try:
            self.root.after(0, callback)

        except (tk.TclError, RuntimeError):
            # The window might have closed while the upload was finishing.
            # In that case, Tkinter can reject the callback; nothing else
            # needs to be done because the user has already closed the app.
            pass

    def _show_qr_code(self, photo_path, file_url):
        """
        Create a QR code from the Drive URL and display it in a popup window.
        """

        # Convert the Drive URL into a QR image, then into an image
        # that can be displayed by Tkinter.
        try:
            qr_image = create_qr_image(file_url)
            qr_photo = ImageTk.PhotoImage(qr_image)

        except Exception as error:
            # The photo was uploaded, but QR creation or display failed.
            # Re-enable the capture button so the user can continue.
            self.status_label.config(
                text="Photo uploaded, but the QR code could not be displayed."
            )
            self.capture_button.config(state=tk.NORMAL)

            # Show the link so the photo can still be opened manually.
            messagebox.showerror(
                "QR code could not be displayed",
                f"The photo was uploaded, but the QR code could not be created.\n\n"
                f"Details: {error}\n\n"
                f"Photo link:\n{file_url}",
            )
            return

        # Create a separate popup window for this photo's QR code.
        # The main window and camera preview remain open behind it.
        qr_window = tk.Toplevel(self.root)
        qr_window.title("Scan to view your photo")
        qr_window.configure(bg="#111827")
        qr_window.resizable(False, False)

        # Add a heading to tell the user that the photo is ready.
        title = tk.Label(
            qr_window,
            text="YOUR PHOTO IS READY",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#111827",
        )
        title.pack(padx=24, pady=(20, 10))

        # Create a label that will display the QR image.
        qr_label = tk.Label(
            qr_window,
            image=qr_photo,
            bg="white",
        )

        # Keep a reference to qr_photo on the label.
        # Without a saved reference, Python might delete the image from memory,
        # causing Tkinter to show a blank area instead of the QR code.
        qr_label.image = qr_photo

        # Display the QR image below the heading.
        qr_label.pack(padx=24, pady=10)

        # Tell the guest how to use the QR code.
        instructions = tk.Label(
            qr_window,
            text="Scan this code with your phone to view the photo.",
            font=("Arial", 11),
            fg="white",
            bg="#111827",
        )
        instructions.pack(padx=24, pady=(10, 20))

        # Update the main window's status message.
        self.status_label.config(
            text=f"Photo uploaded: {photo_path.name}"
        )

        # The upload is finished, so allow the user to take another photo.
        self.capture_button.config(state=tk.NORMAL)

    def _show_upload_error(self, photo_path, error_message):
        """
        Tell the user that upload failed while keeping the local photo.
        """

        # The photo was saved locally before upload began.
        # Show its name so the user knows that the local copy still exists.
        self.status_label.config(
            text=f"Upload failed. Local copy kept: {photo_path.name}"
        )

        # Allow the user to continue using the photo booth.
        self.capture_button.config(state=tk.NORMAL)

        # Display the reason for the failure and the local file path.
        messagebox.showerror(
            "Photo upload failed",
            f"{error_message}\n\n"
            f"The photo is still saved locally at:\n{photo_path}",
        )

    def close(self):
        """
        Stop background UI updates, release the camera, and close the window.
        """

        # Tell preview and upload callbacks that the app is closing.
        self._is_closing = True

        # Release the camera so another program can use it after this app exits.
        self.camera.close()

        # Destroy the main Tkinter window and end the GUI session.
        self.root.destroy()

    def run(self):
        """
        Start Tkinter's event loop and keep the window responsive.
        """

        # mainloop waits for events such as button clicks, key presses,
        # and scheduled camera preview updates.
        self.root.mainloop()