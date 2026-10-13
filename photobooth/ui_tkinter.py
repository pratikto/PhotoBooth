"""
Tkinter user interface for the PhotoBooth application.

This module contains only the visible interface:
- The main application window
- The camera preview area
- The capture button
- The status message
- The QR-code popup
- Error message dialogs

Camera access, photo saving, and Google Drive uploads are handled by app.py
and the other PhotoBooth modules. Keeping those tasks separate makes it
easier to redesign the screen without changing the photo-taking workflow.
"""

# Callable describes functions that this UI receives from app.py.
# The UI uses these functions when the user clicks Capture or closes the window.
from typing import Callable

# tkinter provides the desktop window, buttons, labels, and popup windows.
import tkinter as tk

# messagebox provides standard popup dialogs for errors and warnings.
from tkinter import messagebox

# Image is used to describe the Pillow image passed into this UI.
# ImageTk converts Pillow images into images that Tkinter can display.
from PIL import Image, ImageTk


# Centralize the main colors so the appearance can be adjusted in one place.
# These values are used throughout this module when creating GUI widgets.
BACKGROUND_COLOR = "#111827"
PREVIEW_BACKGROUND_COLOR = "#1f2937"
PREVIEW_BORDER_COLOR = "#374151"
PRIMARY_TEXT_COLOR = "white"
SECONDARY_TEXT_COLOR = "#9ca3af"
BUTTON_COLOR = "#2563eb"
BUTTON_ACTIVE_COLOR = "#1d4ed8"


class PhotoBoothUI:
    """
    Create and manage the PhotoBooth application's visible interface.

    The application logic supplies two callbacks:
    - on_capture: called when the user clicks the capture button
    - on_close: called when the user presses Escape or closes the window

    This class does not open the camera or upload files. It only displays
    information and reports user actions back to the application logic.
    """

    def __init__(
        self,
        root: tk.Tk,
        on_capture: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        """
        Initialize the interface inside an existing Tkinter root window.

        Args:
            root: The main Tkinter window created by app.py.
            on_capture: The app.py method that captures a photo.
            on_close: The app.py method that shuts down the application.
        """

        # Keep the root window so this UI can create widgets inside it
        # and display popup dialogs with the correct parent window.
        self.root = root

        # Save the application callbacks.
        # The UI calls these when the user interacts with the window.
        self._on_capture = on_capture
        self._on_close = on_close

        # Tkinter requires a persistent reference to displayed images.
        # If Python removes the only reference to an image, Tkinter may
        # display a blank area instead of the preview.
        self.preview_photo = None

        # Configure the main window's title, starting size, and background.
        self._configure_main_window()

        # Create and arrange the visible widgets.
        self._create_widgets()

        # Let the Escape key close the application.
        # Tkinter sends a keyboard event to this callback, so the lambda
        # accepts the event and then calls the app.py close method.
        self.root.bind("<Escape>", lambda event: self._on_close())

        # Call the same app.py close method when the user clicks the X
        # button in the window title bar.
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_main_window(self) -> None:
        """
        Set the main window's basic appearance and initial dimensions.
        """

        # Set the text shown in the operating system's window title bar.
        self.root.title("Photo Booth")

        # Set the initial window size in pixels: width x height.
        self.root.geometry("900x700")

        # Use the same dark background as the other interface elements.
        self.root.configure(bg=BACKGROUND_COLOR)

    def _create_widgets(self) -> None:
        """
        Create and position the title, preview area, button, and status text.
        """

        # Create the large heading shown above the camera preview.
        title_label = tk.Label(
            self.root,
            text="PHOTO BOOTH",
            font=("Arial", 28, "bold"),
            fg=PRIMARY_TEXT_COLOR,
            bg=BACKGROUND_COLOR,
        )

        # Place the heading near the top of the window.
        # The first number is the space above it; the second is the space below.
        title_label.pack(pady=(30, 10))

        # Create a fixed-size frame that will contain the camera preview.
        # Its darker background is visible while the camera is connecting
        # or when no preview image is available.
        preview_frame = tk.Frame(
            self.root,
            width=700,
            height=380,
            bg=PREVIEW_BACKGROUND_COLOR,
            highlightthickness=1,
            highlightbackground=PREVIEW_BORDER_COLOR,
        )

        # Center the preview frame in the main window.
        preview_frame.pack(pady=20)

        # Normally, a Tkinter frame can shrink or grow to fit its children.
        # Disable that behavior so the preview area keeps its intended size.
        preview_frame.pack_propagate(False)

        # Create the label that will show the live camera image.
        # Before the camera starts, this label displays a connection message.
        self.preview_label = tk.Label(
            preview_frame,
            text="CONNECTING TO CAMERA...",
            font=("Arial", 16, "bold"),
            fg=SECONDARY_TEXT_COLOR,
            bg=PREVIEW_BACKGROUND_COLOR,
        )

        # Expand the label to use the available preview-frame space
        # and keep its text or image centered.
        self.preview_label.pack(expand=True)

        # Create the button that asks app.py to capture a photo.
        # It starts disabled; app.py enables it after the camera connects.
        self.capture_button = tk.Button(
            self.root,
            text="TAKE PHOTO",
            command=self._on_capture,
            font=("Arial", 16, "bold"),
            fg=PRIMARY_TEXT_COLOR,
            bg=BUTTON_COLOR,
            activebackground=BUTTON_ACTIVE_COLOR,
            activeforeground=PRIMARY_TEXT_COLOR,
            disabledforeground=SECONDARY_TEXT_COLOR,
            relief=tk.FLAT,
            padx=30,
            pady=12,
            state=tk.DISABLED,
        )

        # Place the button below the camera preview.
        self.capture_button.pack(pady=5)

        # Create a text label for short updates from app.py.
        # Examples include "Connecting to camera..." and "Uploading photo...".
        self.status_label = tk.Label(
            self.root,
            text="Starting photo booth...",
            font=("Arial", 11),
            fg=SECONDARY_TEXT_COLOR,
            bg=BACKGROUND_COLOR,
        )

        # Place the status message below the capture button.
        self.status_label.pack(pady=10)

    def set_status(self, message: str) -> None:
        """
        Display a short status message in the main window.

        Args:
            message: The status text that should be shown to the user.
        """

        # Update only the text of the existing status label.
        # Reusing the label avoids creating a new widget every time the
        # application status changes.
        self.status_label.config(text=message)

    def set_capture_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the capture button.

        Args:
            enabled: True enables the button; False disables it.
        """

        # Tkinter expects a state constant rather than a Boolean value.
        # A disabled button cannot be clicked while the camera is unavailable
        # or while an upload is in progress.
        new_state = tk.NORMAL if enabled else tk.DISABLED
        self.capture_button.config(state=new_state)

    def show_preview(self, image: Image.Image) -> None:
        """
        Display a Pillow image in the camera preview area.

        Args:
            image: The current camera frame converted to a Pillow RGB image.
        """

        # Make a copy before resizing so the caller's image is left unchanged.
        # The photo being saved by app.py keeps its original full resolution.
        display_image = image.copy()

        # Shrink the displayed copy only if it exceeds the preview frame.
        # The aspect ratio is kept so the image does not look stretched.
        display_image.thumbnail((700, 380))

        # Convert the Pillow image to a Tkinter-compatible image.
        # Keep this object as an instance variable so Python does not
        # discard it while the label is displaying it.
        self.preview_photo = ImageTk.PhotoImage(display_image)

        # Replace the connection message or previous frame with the new image.
        self.preview_label.config(
            image=self.preview_photo,
            text="",
        )

    def show_preview_message(self, message: str) -> None:
        """
        Show text in the preview area instead of a camera image.

        Args:
            message: The message to display, such as a camera error.
        """

        # Remove the interface's reference to the previous preview image.
        # The label is also explicitly told to stop displaying that image.
        self.preview_photo = None

        # Show the new message and clear the displayed image.
        self.preview_label.config(
            image="",
            text=message,
        )

    def show_qr_code(self, qr_image: Image.Image) -> None:
        """
        Open a popup window that displays a QR code.

        Args:
            qr_image: A Pillow image containing the generated QR code.
        """

        # Create a separate window whose parent is the main application window.
        # This allows the QR popup to stay associated with the PhotoBooth app.
        qr_window = tk.Toplevel(self.root)

        # Configure the popup's title, background, and resizing behavior.
        qr_window.title("Scan to view your photo")
        qr_window.configure(bg=BACKGROUND_COLOR)
        qr_window.resizable(False, False)

        # Create a heading that tells the user the photo is ready.
        title_label = tk.Label(
            qr_window,
            text="YOUR PHOTO IS READY",
            font=("Arial", 18, "bold"),
            fg=PRIMARY_TEXT_COLOR,
            bg=BACKGROUND_COLOR,
        )

        # Add spacing around the heading so it is not crowded by the QR code.
        title_label.pack(padx=24, pady=(20, 10))

        # Convert the Pillow QR image into an image Tkinter can display.
        qr_photo = ImageTk.PhotoImage(qr_image)

        # Create a label that acts as the display area for the QR image.
        qr_label = tk.Label(
            qr_window,
            image=qr_photo,
            bg="white",
        )

        # Store a reference to the QR image on the label itself.
        # The label remains alive while the popup is open, so this reference
        # prevents Python from removing the image from memory.
        qr_label.image = qr_photo

        # Place the QR image below the heading with a white background.
        qr_label.pack(padx=24, pady=10)

        # Explain what the user should do with the QR code.
        instruction_label = tk.Label(
            qr_window,
            text="Scan this code with your phone to view the photo.",
            font=("Arial", 11),
            fg=PRIMARY_TEXT_COLOR,
            bg=BACKGROUND_COLOR,
        )

        # Place the instruction text underneath the QR image.
        instruction_label.pack(padx=24, pady=(10, 20))

    def show_error(self, title: str, message: str) -> None:
        """
        Display an error dialog associated with the main application window.

        Args:
            title: The short heading shown on the dialog.
            message: The detailed explanation shown inside the dialog.
        """

        # parent=self.root keeps the dialog attached to this application
        # and usually places it above the main PhotoBooth window.
        messagebox.showerror(
            title,
            message,
            parent=self.root,
        )