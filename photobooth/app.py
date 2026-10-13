import tkinter as tk

import cv2
from PIL import Image, ImageTk

from photobooth.camera import Camera
from photobooth.photo_storage import save_photo


class PhotoBoothApp:
    """Manage the window, camera preview, and photo button."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Photo Booth")
        self.root.geometry("900x700")
        self.root.configure(bg="#111827")

        self.camera = Camera(camera_index=0)
        self.current_frame = None
        self.preview_image = None

        self._create_widgets()

        self.root.bind("<Escape>", lambda event: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self._connect_camera)

    def _create_widgets(self):
        title = tk.Label(
            self.root,
            text="PHOTO BOOTH",
            font=("Arial", 32, "bold"),
            fg="white",
            bg="#111827",
        )
        title.pack(pady=(30, 10))

        preview = tk.Frame(
            self.root,
            width=700,
            height=380,
            bg="#1f2937",
        )
        preview.pack(pady=20)
        preview.pack_propagate(False)

        self.preview_label = tk.Label(
            preview,
            text="CONNECTING TO CAMERA...",
            font=("Arial", 18),
            fg="#9ca3af",
            bg="#1f2937",
        )
        self.preview_label.pack(expand=True)

        self.capture_button = tk.Button(
            self.root,
            text="TAKE PHOTO",
            font=("Arial", 18, "bold"),
            command=self._capture_photo,
            padx=30,
            pady=12,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            state=tk.DISABLED,
        )
        self.capture_button.pack(pady=5)

        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12),
            fg="#d1d5db",
            bg="#111827",
        )
        self.status_label.pack(pady=10)

    def _connect_camera(self):
        self.status_label.config(text="Connecting to camera...")

        if not self.camera.open():
            self.status_label.config(
                text=(
                    "Camera not detected. Check camera permissions "
                    "or try a different camera index."
                )
            )
            self.preview_label.config(
                image="",
                text="CAMERA NOT DETECTED",
                fg="#fca5a5",
            )
            return

        self.status_label.config(
            text="Camera connected. Press TAKE PHOTO to capture an image."
        )
        self.capture_button.config(state=tk.NORMAL)
        self._update_preview()

    def _update_preview(self):
        frame = self.camera.read()

        if frame is None:
            self.status_label.config(
                text="Camera is connected, but no frame could be read."
            )
            self.root.after(250, self._update_preview)
            return

        self.current_frame = frame

        # OpenCV returns BGR, while Pillow expects RGB for correct colors.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        image.thumbnail((700, 380))

        self.preview_image = ImageTk.PhotoImage(image)
        self.preview_label.config(image=self.preview_image, text="")

        # Keep a reference to the image so Tkinter can continue displaying it.
        self.root.after(15, self._update_preview)

    def _capture_photo(self):
        if self.current_frame is None:
            self.status_label.config(text="No camera frame is available yet.")
            return

        photo_path = save_photo(self.current_frame.copy())

        if photo_path is None:
            self.status_label.config(text="Failed to save the photo.")
            return

        self.status_label.config(
            text=f"Photo saved: photos/{photo_path.name}"
        )

    def close(self):
        self.camera.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
