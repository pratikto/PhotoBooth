#!/usr/bin/env python3
"""Standalone Tk/Pillow thermal-dithering laboratory (no kiosk, camera or printer).

Launch from the repository root: python tools/dither_tuning_gui.py
This is intentionally offline and NEVER submits physical print jobs.
"""

from __future__ import annotations

import queue
import sys
import threading
from pathlib import Path

# Running this script directly makes tools/ sys.path[0], not the repository
# root. Insert the checkout root before importing the shared printer engine.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from photobooth.dither_lab import (
    DitherProfile, load_profile, render_thermal_image, save_profile,
)
from photobooth.printer import DITHER_MODES


def sample_image() -> Image.Image:
    """Synthetic startup chart; no customer image is bundled or uploaded."""
    image = Image.new("RGB", (640, 960), "white")
    draw = ImageDraw.Draw(image)
    for y in range(image.height):
        tone = round(255 * y / (image.height - 1))
        draw.line((0, y, image.width, y), fill=(tone, tone, tone))
    draw.ellipse((80, 130, 560, 620), fill=(178, 145, 115), outline="black", width=7)
    draw.ellipse((195, 315, 250, 360), fill="#1c2d36")
    draw.ellipse((390, 315, 445, 360), fill="#1c2d36")
    draw.arc((220, 355, 435, 485), 10, 170, fill="black", width=10)
    draw.rectangle((70, 695, 570, 795), fill="#f5f5f5", outline="black", width=5)
    draw.text((105, 732), "MEONG DITHER TEST", fill="black")
    return image


class TuningWindow:
    """Debounce live controls and render large rasters off Kivy's UI entirely."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("MEONG | Thermal Dither Lab")
        root.geometry("1230x780")
        root.minsize(940, 600)
        self.source = sample_image()
        self.source_name = "Contoh sintetis (bukan foto pelanggan)"
        self.result: Image.Image | None = None
        self.result_profile: DitherProfile | None = None
        self._render_generation = 0
        self._pending_after: str | None = None
        self._busy = False
        self._queued = False
        self._closed = False
        self._outcomes: queue.Queue = queue.Queue()
        self._original_photo = self._thermal_photo = self._detail_photo = None

        root.configure(bg="#eff8fb")
        style = ttk.Style(root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Lab.TFrame", background="#eff8fb")
        style.configure("Lab.TLabel", background="#eff8fb", foreground="#233448")
        style.configure("Lab.TLabelframe", background="#eff8fb")
        style.configure("Lab.TLabelframe.Label", background="#eff8fb", foreground="#233448")
        style.configure("Accent.TButton", padding=(12, 8))

        top = ttk.Frame(root, style="Lab.TFrame", padding=14)
        top.pack(side="top", fill="x")
        ttk.Label(top, text="MEONG • DITHER LAB",
                  font=("Segoe UI", 19, "bold"), style="Lab.TLabel").pack(side="left")
        ttk.Label(top, text="Eksperimen offline • tidak mencetak otomatis",
                  style="Lab.TLabel").pack(side="right")

        bar = ttk.Frame(root, style="Lab.TFrame", padding=(14, 0, 14, 10))
        bar.pack(fill="x")
        for label, action in (
            ("Buka foto", self.open_image),
            ("Muat preset", self.open_profile),
            ("Simpan preset", self.store_profile),
            ("Ekspor PNG 1-bit", self.export_png),
        ):
            ttk.Button(bar, text=label, command=action,
                       style="Accent.TButton").pack(side="left", padx=(0, 7))

        main = ttk.Panedwindow(root, orient="horizontal")
        main.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        controls = ttk.LabelFrame(main, text="ALGORITMA & TUNING", padding=14)
        view = ttk.LabelFrame(main, text="PREVIEW • raster sesuai lebar printhead", padding=10)
        main.add(controls, weight=1)
        main.add(view, weight=3)

        self.mode = tk.StringVar(value="floyd-steinberg")
        self.width = tk.StringVar(value="576")
        self.values = {
            "brightness": tk.DoubleVar(value=1.0),
            "contrast": tk.DoubleVar(value=1.0),
            "gamma": tk.DoubleVar(value=1.0),
            "sharpness": tk.DoubleVar(value=1.0),
            "threshold": tk.DoubleVar(value=128),
        }
        ttk.Label(controls, text="Metode dithering").pack(anchor="w")
        self.mode_box = ttk.Combobox(controls, textvariable=self.mode,
                                     values=DITHER_MODES, state="readonly")
        self.mode_box.pack(fill="x", pady=(3, 12))
        self.mode_box.bind("<<ComboboxSelected>>", self._mode_changed)
        ttk.Label(controls, text="Lebar printhead (dots)").pack(anchor="w")
        width_box = ttk.Combobox(controls, textvariable=self.width,
                                 values=("576", "384"), state="readonly")
        width_box.pack(fill="x", pady=(3, 10))
        width_box.bind("<<ComboboxSelected>>", lambda _event: self.schedule())

        self.number_labels: dict[str, ttk.Label] = {}
        self.sliders: dict[str, ttk.Scale] = {}
        for key, label, minimum, maximum in (
            ("brightness", "Brightness", 0.5, 1.75),
            ("contrast", "Contrast", 0.5, 2.5),
            ("gamma", "Gamma (>1 lebih terang)", 0.3, 3.0),
            ("sharpness", "Sharpness (1 = asli)", 0.0, 3.0),
            ("threshold", "Threshold (hanya binary)", 0, 255),
        ):
            line = ttk.Frame(controls)
            line.pack(fill="x", pady=(12, 0))
            ttk.Label(line, text=label).pack(side="left")
            readout = ttk.Label(line, text="", width=7, anchor="e")
            readout.pack(side="right")
            slider = ttk.Scale(controls, variable=self.values[key],
                               from_=minimum, to=maximum,
                               command=lambda _value, name=key: self._slider_changed(name))
            slider.pack(fill="x", pady=(5, 0))
            self.sliders[key] = slider
            self.number_labels[key] = readout
            self._show_value(key)

        ttk.Button(controls, text="Reset default",
                   command=self.reset).pack(fill="x", pady=(22, 9))
        ttk.Label(controls,
                  text="Bayer: matriks tetap 8×8. Threshold tidak memengaruhi\n"
                       "Floyd–Steinberg atau Bayer. Output selalu 1-bit.",
                  wraplength=265, justify="left").pack(anchor="w")

        gallery = ttk.Frame(view)
        gallery.pack(fill="both", expand=True)
        for col, title in ((0, "SUMBER"), (1, "RASTER 1-BIT")):
            gallery.columnconfigure(col, weight=1)
            ttk.Label(gallery, text=title,
                      font=("Segoe UI", 11, "bold")).grid(row=0, column=col, pady=7)
        gallery.rowconfigure(1, weight=1)
        self.original_label = ttk.Label(gallery, anchor="center", text="Memuat...")
        self.thermal_label = ttk.Label(gallery, anchor="center", text="Memproses...")
        self.original_label.grid(row=1, column=0, sticky="nsew", padx=8)
        self.thermal_label.grid(row=1, column=1, sticky="nsew", padx=8)
        ttk.Label(gallery, text="ZOOM DOT • crop tengah, tampilan 3× (nearest)").grid(
            row=2, column=0, columnspan=2, pady=(10, 5))
        self.detail_label = ttk.Label(gallery, anchor="center")
        self.detail_label.grid(row=3, column=0, columnspan=2, pady=(0, 9))

        self.status = tk.StringVar(value="Siap.")
        ttk.Label(root, textvariable=self.status,
                  style="Lab.TLabel", padding=(14, 5)).pack(fill="x")

        self._mode_changed()
        self.root.after(75, self._poll_results)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _show_value(self, key: str) -> None:
        value = self.values[key].get()
        self.number_labels[key].configure(
            text=f"{round(value):.0f}" if key == "threshold" else f"{value:.2f}"
        )

    def _slider_changed(self, key: str) -> None:
        self._show_value(key)
        self.schedule()

    def _mode_changed(self, _event=None) -> None:
        self.sliders["threshold"].state(
            ["!disabled"] if self.mode.get() == "threshold" else ["disabled"]
        )
        self.schedule()

    def profile(self) -> DitherProfile:
        return DitherProfile(
            mode=self.mode.get(), width_dots=int(self.width.get()),
            brightness=round(self.values["brightness"].get(), 3),
            contrast=round(self.values["contrast"].get(), 3),
            gamma=round(self.values["gamma"].get(), 3),
            sharpness=round(self.values["sharpness"].get(), 3),
            threshold=round(self.values["threshold"].get()),
        )

    def schedule(self) -> None:
        self._render_generation += 1
        if self._pending_after is not None:
            self.root.after_cancel(self._pending_after)
        self._pending_after = self.root.after(230, self._start_render)

    def _start_render(self) -> None:
        self._pending_after = None
        if self._busy:
            self._queued = True
            return
        try:
            profile = self.profile()
        except ValueError as error:
            self.status.set(f"Parameter tidak valid: {error}")
            return
        generation = self._render_generation
        source = self.source.copy()
        self._busy = True
        self._queued = False
        self.status.set(f"Memproses {self.source_name} • {profile.mode}...")
        def worker() -> None:
            try:
                result = render_thermal_image(source, profile)
                self._outcomes.put((generation, profile, result, None))
            except Exception as error:
                self._outcomes.put((generation, profile, None, str(error)))
        threading.Thread(target=worker, name="meong-dither-preview", daemon=True).start()

    @staticmethod
    def _fit(image: Image.Image, maxsize: tuple[int, int], resample) -> Image.Image:
        copy = image.copy()
        copy.thumbnail(maxsize, resample=resample)
        return copy

    def _show_images(self, result: Image.Image) -> None:
        base = self._fit(self.source.convert("RGB"), (385, 445), Image.Resampling.LANCZOS)
        raster = self._fit(result.convert("RGB"), (385, 445), Image.Resampling.NEAREST)
        # A center crop at native resolution reveals the actual discrete black
        # dot pattern, rather than a smooth downscaled on-screen approximation.
        width, height = result.size
        crop_width, crop_height = min(150, width), min(90, height)
        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        detail = result.crop((left, top, left + crop_width, top + crop_height))
        detail = detail.resize((crop_width * 3, crop_height * 3),
                               Image.Resampling.NEAREST).convert("RGB")
        self._original_photo = ImageTk.PhotoImage(base, master=self.root)
        self._thermal_photo = ImageTk.PhotoImage(raster, master=self.root)
        self._detail_photo = ImageTk.PhotoImage(detail, master=self.root)
        self.original_label.configure(image=self._original_photo, text="")
        self.thermal_label.configure(image=self._thermal_photo, text="")
        self.detail_label.configure(image=self._detail_photo, text="")

    def _poll_results(self) -> None:
        if self._closed:
            return
        while True:
            try:
                generation, profile, result, error = self._outcomes.get_nowait()
            except queue.Empty:
                break
            self._busy = False
            if generation == self._render_generation:
                if error:
                    self.status.set(f"Gagal memproses: {error}")
                else:
                    self.result, self.result_profile = result, profile
                    self._show_images(result)
                    self.status.set(
                        f"Siap • {result.width} × {result.height} dots • "
                        "preview di layar diperbesar/diperkecil; ekspor tetap resolusi asli."
                    )
            if self._queued or generation != self._render_generation:
                self._queued = False
                if self._pending_after is not None:
                    self.root.after_cancel(self._pending_after)
                    self._pending_after = None
                self._start_render()
        self.root.after(75, self._poll_results)

    def open_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Pilih hasil foto asli", filetypes=[
                ("Foto", "*.png *.jpg *.jpeg *.bmp *.webp"), ("Semua file", "*.*")]
        )
        if not path:
            return
        try:
            with Image.open(path) as image:
                image.load()
                self.source = image.convert("RGBA")
        except (OSError, ValueError) as error:
            messagebox.showerror("Gagal membuka foto", str(error), parent=self.root)
            return
        self.source_name = Path(path).name
        self.schedule()

    def reset(self) -> None:
        default = DitherProfile()
        self.apply_profile(default)

    def apply_profile(self, profile: DitherProfile) -> None:
        self.mode.set(profile.mode)
        self.width.set(str(profile.width_dots))
        for key in self.values:
            self.values[key].set(getattr(profile, key))
            self._show_value(key)
        self._mode_changed()

    def store_profile(self) -> None:
        try:
            profile = self.profile()
        except ValueError as error:
            messagebox.showerror("Preset invalid", str(error), parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            title="Simpan preset lab", defaultextension=".json",
            filetypes=[("JSON preset", "*.json")], initialfile="meong-dither-profile.json")
        if path:
            try:
                save_profile(path, profile)
                self.status.set(f"Preset tersimpan: {path} (BELUM dipakai aplikasi kiosk).")
            except OSError as error:
                messagebox.showerror("Gagal menyimpan preset", str(error), parent=self.root)

    def open_profile(self) -> None:
        path = filedialog.askopenfilename(
            title="Muat preset lab", filetypes=[("JSON preset", "*.json")])
        if not path:
            return
        try:
            self.apply_profile(load_profile(path))
            self.status.set(f"Preset dimuat: {path}")
        except (OSError, ValueError, TypeError) as error:
            messagebox.showerror("Preset tidak valid", str(error), parent=self.root)

    def export_png(self) -> None:
        if self.result is None or self.result_profile != self.profile():
            messagebox.showinfo("Tunggu render",
                                "Tunggu preview selesai untuk parameter terbaru.",
                                parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            title="Ekspor raster 1-bit", defaultextension=".png",
            filetypes=[("PNG hitam-putih", "*.png")], initialfile="meong-thermal-preview.png")
        if path:
            try:
                self.result.save(path, format="PNG")
                self.status.set(f"PNG 1-bit tersimpan: {path}; belum dicetak.")
            except OSError as error:
                messagebox.showerror("Gagal ekspor PNG", str(error), parent=self.root)

    def close(self) -> None:
        self._closed = True
        if self._pending_after is not None:
            self.root.after_cancel(self._pending_after)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    TuningWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
