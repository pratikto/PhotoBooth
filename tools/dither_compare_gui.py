#!/usr/bin/env python3
"""Three-panel, offline thermal-photo tuning studio.

All Tk widgets live on the Tk event thread; workers compute immutable raster
results only. Physical printing is an explicit, confirmed separate action.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageTk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from photobooth.dither_lab import (LAB_DITHER_MODES, ComparisonProfiles, DitherProfile,
                                   load_comparison, render_thermal_image, save_comparison)
from photobooth.dizzy_dither import DIZZY_VARIANTS

# Threshold remains in lab profiles and production backends for backward
# compatibility, but no longer has a visible comparison/print/export panel.
VISIBLE_MODES = ("floyd-steinberg", "bayer", "dizzy")
assert set(VISIBLE_MODES).issubset(LAB_DITHER_MODES)

FIELDS = (
    ("brightness", "Brightness", .5, 1.75),
    ("contrast", "Contrast", .5, 2.5),
    ("gamma", "Gamma", .3, 3),
    ("sharpness", "Sharpness", 0, 3),
)
SHORT = {"floyd-steinberg": "Floyd–Steinberg", "bayer": "Bayer 8×8",
         "dizzy": "Dizzy Dithering"}


def sample_source():
    """Generated neutral grayscale chart; avoids bundling real customer photos."""
    im = Image.new("RGB", (640, 800), "white")
    d = ImageDraw.Draw(im)
    for y in range(im.height):
        shade = round(y * 255 / (im.height - 1))
        d.line((0, y, im.width, y), fill=(shade, shade, shade))
    d.ellipse((90, 120, 550, 590), fill="#b6a38c", outline="black", width=8)
    d.ellipse((205, 310, 260, 355), fill="black")
    d.ellipse((380, 310, 435, 355), fill="black")
    d.arc((240, 395, 400, 490), 0, 180, fill="black", width=8)
    return im


class ComparisonApp:
    def __init__(self, root):
        self.root = root
        root.title("MEONG | Dither Comparison Lab + Dizzy (Experimental)")
        root.geometry("1450x850")
        root.minsize(1050, 620)
        self.source = sample_source()
        self.source_label = "Synthetic sample"
        self.configs = ComparisonProfiles()
        self.results = {}
        self.ready_profiles = {}
        self.versions = {mode: 0 for mode in VISIBLE_MODES}
        self.timers = {}
        self.busy = set()
        self.queued = set()
        self.outcomes = queue.Queue()
        self.closed = False
        self.photos = {}
        self.controls = {}
        self.labels = {}
        self.statuses = {}
        self.scroll_canvases = {}
        self.print_events = queue.Queue()
        self.print_busy = False
        self.zoom = tk.IntVar(value=2)
        self.sync = tk.BooleanVar(value=False)
        self.width = tk.StringVar(value="576")
        self.enhanced_floyd = tk.BooleanVar(value=False)
        self.dizzy_variant = tk.StringVar(value=self.configs.dizzy.dizzy_variant)

        style = ttk.Style(root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", padding=(7, 5))
        header = ttk.Frame(root, padding=12)
        header.pack(fill="x")
        ttk.Label(header, text="MEONG • 3-WAY DITHER LAB",
                  font=("Segoe UI", 19, "bold")).pack(side="left")
        ttk.Label(header, text="Experiment only | no changes to kiosk",
                  font=("Segoe UI", 10)).pack(side="right")

        bar = ttk.Frame(root, padding=(12, 0, 12, 9))
        bar.pack(fill="x")
        for caption, callback in (
            ("Open Image", self.open_source), ("Save All Configs", self.save_all),
            ("Load All Configs", self.load_all), ("Export 3 PNG", self.export_all),
            ("Reset", self.reset),
        ):
            ttk.Button(bar, text=caption, command=callback).pack(side="left", padx=(0, 5))
        ttk.Label(bar, text="Width:").pack(side="left", padx=(9, 4))
        widths = ttk.Combobox(bar, textvariable=self.width, values=("576", "384"),
                              state="readonly", width=6)
        widths.pack(side="left")
        widths.bind("<<ComboboxSelected>>", self.change_width)
        ttk.Checkbutton(bar, text="Enhanced Floyd (experimental)", variable=self.enhanced_floyd,
                        command=self.toggle_enhanced).pack(side="left", padx=8)
        ttk.Checkbutton(bar, text="Sync Parameters", variable=self.sync).pack(
            side="left", padx=12)
        ttk.Label(bar, text="Dot zoom:").pack(side="left")
        zooms = ttk.Combobox(bar, values=("1", "2", "4"), state="readonly", width=4)
        zooms.set("2")
        zooms.pack(side="left", padx=(5, 0))
        zooms.bind("<<ComboboxSelected>>",
                   lambda _event: self.change_zoom(int(zooms.get())))
        ttk.Label(bar, text="Dizzy:").pack(side="left", padx=(10, 3))
        dizzy_variants = ttk.Combobox(
            bar, textvariable=self.dizzy_variant, values=DIZZY_VARIANTS,
            state="readonly", width=15)
        dizzy_variants.pack(side="left")
        dizzy_variants.bind("<<ComboboxSelected>>", self.change_dizzy_variant)
        self.dizzy_seed_label = ttk.Label(bar, text=f"Seed: {self.configs.dizzy.dizzy_seed}")
        self.dizzy_seed_label.pack(side="left", padx=5)

        reference = ttk.LabelFrame(root, text="SOURCE IMAGE", padding=4)
        reference.pack(fill="x", padx=12, pady=(0, 9))
        self.source_photo = None
        self.source_view = ttk.Label(reference, anchor="center")
        self.source_view.pack(fill="x")
        self.source_title = ttk.Label(reference, text="")
        self.source_title.pack()

        columns = ttk.Frame(root, padding=(8, 0, 8, 5))
        columns.pack(fill="both", expand=True)
        for idx, mode in enumerate(VISIBLE_MODES):
            columns.columnconfigure(idx, weight=1, uniform="lane")
            panel = ttk.LabelFrame(columns, text=SHORT[mode], padding=8)
            panel.grid(row=0, column=idx, padx=4, sticky="nsew")
            columns.rowconfigure(0, weight=1)
            # BUG-010: bound the image height; parameter controls get a
            # separate scroll region while print/export actions stay sticky.
            preview_holder = ttk.Frame(panel, height=286)
            preview_holder.pack(fill="x")
            preview_holder.pack_propagate(False)
            output = ttk.Label(preview_holder, text="Rendering preview...", anchor="center")
            output.pack(fill="both", expand=True)
            detail = ttk.Label(panel, text="Actual dots (nearest-neighbor crop)", anchor="center")
            detail.pack(fill="x", pady=2)
            meta = ttk.Label(panel, text="Pending...", anchor="center")
            meta.pack(fill="x")
            self.labels[mode] = (output, detail, meta)

            sliders_host = ttk.Frame(panel)
            sliders_host.pack(fill="both", expand=True, pady=(4, 2))
            canvas = tk.Canvas(sliders_host, highlightthickness=0,
                               borderwidth=0, height=120)
            scroll = ttk.Scrollbar(sliders_host, orient="vertical",
                                   command=canvas.yview)
            canvas.configure(yscrollcommand=scroll.set)
            scroll.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            interior = ttk.Frame(canvas, padding=(3, 2, 6, 3))
            window_id = canvas.create_window((0, 0), window=interior, anchor="nw")
            interior.bind("<Configure>", lambda _event, cv=canvas:
                          cv.configure(scrollregion=cv.bbox("all")))
            canvas.bind("<Configure>", lambda event, cv=canvas, wid=window_id:
                        cv.itemconfigure(wid, width=event.width))
            self.scroll_canvases[mode] = canvas
            self.controls[mode] = {}
            for key, caption, lower, upper in FIELDS:
                strip = ttk.Frame(interior)
                strip.pack(fill="x", pady=(5, 0))
                ttk.Label(strip, text=caption).pack(side="left")
                val_label = ttk.Label(strip, text="", width=7, anchor="e")
                val_label.pack(side="right")
                val = tk.DoubleVar(value=getattr(self.configs.by_mode(mode), key))
                slider = ttk.Scale(interior, from_=lower, to=upper, variable=val,
                                   command=lambda _value, m=mode, k=key:
                                       self.slider_changed(m, k))
                slider.pack(fill="x")
                self.controls[mode][key] = (val, val_label)
                self.write_value(mode, key)
            # Pack actions before the flexible controls grow: buttons and
            # readiness feedback cannot be pushed out of a small window.
            state = ttk.Label(panel, text="Awaiting preview", anchor="center")
            state.pack(side="bottom", fill="x")
            actions = ttk.Frame(panel)
            actions.pack(side="bottom", fill="x", pady=(6, 2))
            ttk.Button(actions, text="Print Test", command=lambda m=mode:
                       self.print_lane(m)).pack(side="left", expand=True, fill="x")
            ttk.Button(actions, text="Save PNG", command=lambda m=mode:
                       self.export_lane(m)).pack(side="left", expand=True, fill="x",
                                                 padx=(5, 0))
            self.statuses[mode] = state

        footer = ttk.Frame(root, padding=(12, 0, 12, 7))
        footer.pack(fill="x")
        self.message = tk.StringVar(value="Lab only: article-8 Dizzy uses axial 1.0 / diagonal 0.1 weights. Native PNG / print remain 1-bit.")
        ttk.Label(footer, textvariable=self.message).pack(side="left")
        ttk.Button(footer, text="Print All (3 jobs)",
                   command=self.print_all).pack(side="right")

        root.bind_all("<MouseWheel>", self._wheel_scroll, add="+")
        root.bind_all("<Button-4>", self._wheel_scroll, add="+")
        root.bind_all("<Button-5>", self._wheel_scroll, add="+")
        self.refresh_source()
        for mode in VISIBLE_MODES:
            self.schedule(mode)
        root.after(80, self.poll)
        root.protocol("WM_DELETE_WINDOW", self.close)

    def _wheel_scroll(self, event):
        """Hit-test the pointer so each lane scrolls only its own parameters."""
        hovered = self.root.winfo_containing(
            self.root.winfo_pointerx(), self.root.winfo_pointery())
        while hovered is not None:
            for canvas in self.scroll_canvases.values():
                if hovered is canvas:
                    if getattr(event, "num", None) == 4:
                        amount = -1
                    elif getattr(event, "num", None) == 5:
                        amount = 1
                    else:
                        amount = -int(event.delta / 120) if event.delta else 0
                        if amount == 0 and event.delta:
                            amount = -1 if event.delta > 0 else 1
                    if amount:
                        canvas.yview_scroll(amount, "units")
                        return "break"
            hovered = hovered.master
        return None

    def write_value(self, mode, key):
        val, label = self.controls[mode][key]
        label.configure(text=f"{val.get():.2f}")

    def toggle_enhanced(self):
        p = self.configs.floyd
        self.configs = self.configs.replace_lane(replace(p, enhanced_floyd=self.enhanced_floyd.get()))
        self.schedule("floyd-steinberg")

    def change_dizzy_variant(self, _event=None):
        profile = self.configs.dizzy
        self.configs = self.configs.replace_lane(
            replace(profile, dizzy_variant=self.dizzy_variant.get()))
        self.schedule("dizzy")

    def change_zoom(self, factor):
        self.zoom.set(factor)
        for mode, image in self.results.items():
            self.show_image(mode, image)

    def change_width(self, _event=None):
        # Keep the hidden Threshold profile width aligned for old JSON files;
        # render only the three visible methods.
        for mode in LAB_DITHER_MODES:
            self.configs = self.configs.replace_lane(
                replace(self.configs.by_mode(mode), width_dots=int(self.width.get())))
        for mode in VISIBLE_MODES:
            self.schedule(mode)

    def slider_changed(self, mode, key):
        self.write_value(mode, key)
        v = self.controls[mode][key][0].get()
        value = round(v, 3)
        targets = VISIBLE_MODES if self.sync.get() else (mode,)
        for target in targets:
            p = self.configs.by_mode(target)
            self.configs = self.configs.replace_lane(replace(p, **{key: value}))
            if target != mode and key in self.controls[target]:
                other = self.controls[target][key][0]
                other.set(value)
                self.write_value(target, key)
            self.schedule(target)

    def schedule(self, mode):
        self.versions[mode] += 1
        if mode in self.timers:
            self.root.after_cancel(self.timers.pop(mode))
        self.timers[mode] = self.root.after(250, lambda m=mode: self.launch(m))
        self.statuses[mode].configure(text="Parameters changed • rendering...")

    def launch(self, mode):
        self.timers.pop(mode, None)
        if mode in self.busy:
            self.queued.add(mode)
            return
        profile = self.configs.by_mode(mode)
        source = self.source.copy()
        version = self.versions[mode]
        self.busy.add(mode)
        def work():
            start = time.perf_counter()
            try:
                raster = render_thermal_image(source, profile)
                coverage = 100 * sum(raster.histogram()[:128]) / (
                    raster.width * raster.height)
                self.outcomes.put((mode, version, profile, raster, coverage,
                                   time.perf_counter() - start, None))
            except Exception as error:
                self.outcomes.put((mode, version, profile, None, 0, 0, str(error)))
        threading.Thread(target=work, daemon=True,
                         name=f"dither-{mode}").start()

    def poll(self):
        if self.closed:
            return
        while True:
            try:
                mode, index, total, success, message = self.print_events.get_nowait()
            except queue.Empty:
                break
            if mode is None:
                self.print_busy = False
                continue
            suffix = " (enhanced)" if mode == "floyd-steinberg" and self.ready_profiles.get(mode, self.configs.floyd).enhanced_floyd else ""
            self.message.set(f"Print {index}/{total} • {SHORT[mode]}{suffix}: {message}")
            if not success:
                messagebox.showwarning("Print stopped",
                    "Print outcome failed/uncertain. Remaining jobs were cancelled.\\n" +
                    message, parent=self.root)
        while True:
            try:
                mode, version, profile, image, coverage, elapsed, error = (
                    self.outcomes.get_nowait())
            except queue.Empty:
                break
            self.busy.discard(mode)
            if version == self.versions[mode]:
                if error:
                    self.statuses[mode].configure(text=f"ERROR: {error}")
                else:
                    self.results[mode] = image
                    self.ready_profiles[mode] = profile
                    self.show_image(mode, image)
                    self.labels[mode][2].configure(
                        text=f"{image.width}×{image.height} dots | black {coverage:.1f}%")
                    suffix = (f" | {profile.dizzy_variant} / seed {profile.dizzy_seed}"
                              if mode == "dizzy" else
                              " | enhanced" if profile.enhanced_floyd else " | baseline")
                    self.statuses[mode].configure(
                        text=f"Ready{suffix} • {elapsed * 1000:.0f} ms")
            if mode in self.queued or version != self.versions[mode]:
                self.queued.discard(mode)
                if mode in self.timers:
                    self.root.after_cancel(self.timers.pop(mode))
                self.launch(mode)
        self.root.after(80, self.poll)

    def show_image(self, mode, raster):
        # Screen preview is necessarily smaller than the 1-bit print raster.
        # NEAREST discards most black dots when shrinking and makes a good
        # physical print look sparse/jagged. BOX averages dot coverage into
        # display grays, approximating perceived tone without changing bytes.
        preview = raster.convert("L")
        preview.thumbnail((370, 268), Image.Resampling.BOX)
        preview = preview.convert("RGB")
        factor = self.zoom.get()
        width, height = raster.size
        w, h = min(130, width, 260 // factor), min(55, height)
        detail = raster.crop(((width - w)//2, (height-h)//2,
                              (width+w)//2, (height+h)//2))
        detail = detail.resize((w*factor, h*factor),
                               Image.Resampling.NEAREST).convert("RGB")
        self.photos[(mode, "full")] = ImageTk.PhotoImage(preview, master=self.root)
        self.photos[(mode, "detail")] = ImageTk.PhotoImage(detail, master=self.root)
        self.labels[mode][0].configure(image=self.photos[(mode, "full")], text="")
        self.labels[mode][1].configure(image=self.photos[(mode, "detail")], text="")

    def refresh_source(self):
        img = self.source.copy()
        img.thumbnail((660, 88), Image.Resampling.LANCZOS)
        self.source_photo = ImageTk.PhotoImage(img, master=self.root)
        self.source_view.configure(image=self.source_photo)
        self.source_title.configure(text=self.source_label)

    def open_source(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Photos", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All files", "*.*")])
        if not path:
            return
        try:
            with Image.open(path) as source:
                source.load()
                candidate = source.convert("RGBA")
        except (OSError, ValueError) as error:
            messagebox.showerror("Image error", str(error), parent=self.root)
            return
        self.source, self.source_label = candidate, Path(path).name
        self.refresh_source()
        for mode in VISIBLE_MODES:
            self.schedule(mode)

    def apply_configs(self, configs):
        self.configs = configs
        self.width.set(str(configs.floyd.width_dots))
        self.enhanced_floyd.set(configs.floyd.enhanced_floyd)
        self.dizzy_variant.set(configs.dizzy.dizzy_variant)
        self.dizzy_seed_label.configure(text=f"Seed: {configs.dizzy.dizzy_seed}")
        for mode in VISIBLE_MODES:
            for key, (var, _label) in self.controls[mode].items():
                var.set(getattr(configs.by_mode(mode), key))
                self.write_value(mode, key)
            self.schedule(mode)

    def reset(self):
        self.apply_configs(ComparisonProfiles())

    def save_all(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
            initialfile="meong-dither-4way.json", filetypes=[("JSON", "*.json")])
        if path:
            try:
                save_comparison(path, self.configs)
                self.message.set(f"Saved lab-only config: {path}")
            except OSError as error:
                messagebox.showerror("Save failed", str(error), parent=self.root)

    def load_all(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                configs = load_comparison(path)
                if len({configs.by_mode(m).width_dots for m in LAB_DITHER_MODES}) != 1:
                    raise ValueError("All lanes must use the same paper width.")
                self.apply_configs(configs)
                self.message.set(f"Loaded lab-only config: {path}")
            except (OSError, TypeError, ValueError) as error:
                messagebox.showerror("Invalid config", str(error), parent=self.root)

    def ready(self, mode):
        profile = self.configs.by_mode(mode)
        return (self.ready_profiles.get(mode) == profile and
                mode not in self.busy and mode not in self.timers and
                mode not in self.queued and mode in self.results)

    def raster_filename(self, profile):
        if profile.mode == "floyd-steinberg":
            return "meong-floyd-{}.png".format(
                "enhanced" if profile.enhanced_floyd else "baseline")
        if profile.mode == "dizzy":
            return f"meong-dizzy-{profile.dizzy_variant}-seed{profile.dizzy_seed}.png"
        return f"meong-{profile.mode}.png"

    def export_lane(self, mode):
        if not self.ready(mode):
            messagebox.showinfo("Rendering", "Wait for the current preview.",
                                parent=self.root)
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
            initialfile=self.raster_filename(self.ready_profiles[mode]), filetypes=[("PNG", "*.png")])
        if path:
            try:
                self.results[mode].save(path, format="PNG")
                self.message.set(f"Exported native 1-bit raster: {path}")
            except OSError as error:
                messagebox.showerror("Export failed", str(error), parent=self.root)

    def export_all(self):
        if not all(self.ready(m) for m in VISIBLE_MODES):
            messagebox.showinfo("Rendering", "Wait for all three previews.",
                                parent=self.root)
            return
        folder = filedialog.askdirectory(title="Export 3 native rasters")
        if folder:
            try:
                for mode in VISIBLE_MODES:
                    self.results[mode].save(
                        Path(folder) / self.raster_filename(self.ready_profiles[mode]), format="PNG")
                self.message.set(f"Exported 3 native 1-bit rasters to {folder}")
            except OSError as error:
                messagebox.showerror("Export failed", str(error), parent=self.root)

    def _start_print(self, modes):
        """Snapshot the currently visible native rasters; never dither twice."""
        if self.print_busy:
            messagebox.showinfo("Printer busy", "A print batch is still running.",
                                parent=self.root)
            return
        if not all(self.ready(mode) for mode in modes):
            messagebox.showinfo("Rendering", "Wait for the latest previews.",
                                parent=self.root)
            return
        from photobooth.printer_settings import load_printer_config
        from photobooth.dither_print import printable_destination
        config = load_printer_config(ROOT / "data" / "printer_settings.json")
        if not printable_destination(config):
            messagebox.showerror(
                "Printer not configured",
                "Set up Windows printer queue or LAN/Wi-Fi printer in the "
                "photobooth Settings and save it before using the lab.",
                parent=self.root)
            return
        labels = ", ".join(SHORT[mode] for mode in modes)
        if not messagebox.askyesno(
            "Confirm physical print",
            f"Print {len(modes)} REAL paper job(s): {labels}\\n"
            "Each job includes its algorithm and parameter header.\\n"
            "If delivery becomes uncertain, remaining jobs will NOT be sent.\\n"
            "Proceed?", parent=self.root):
            return
        # Immutable copies protect the job against later slider edits.
        jobs = [(mode, self.results[mode].copy(), self.ready_profiles[mode])
                for mode in modes]
        self.print_busy = True
        self.message.set(f"Printing {len(jobs)} real paper job(s)...")
        def run():
            from photobooth.dither_print import print_native_raster
            for index, (mode, image, profile) in enumerate(jobs, 1):
                try:
                    outcome = print_native_raster(image, profile, config)
                    status = outcome.user_message
                    ok = outcome.success
                except Exception as error:
                    status, ok = str(error), False
                self.print_events.put((mode, index, len(jobs), ok, status))
                if not ok:
                    break
            self.print_events.put((None, 0, 0, True, "batch finished"))
        threading.Thread(target=run, name="dither-physical-print",
                         daemon=True).start()

    def print_lane(self, mode):
        self._start_print((mode,))

    def print_all(self):
        self._start_print(VISIBLE_MODES)

    def close(self):
        self.closed = True
        for timer in self.timers.values():
            self.root.after_cancel(timer)
        self.root.destroy()


def main():
    root = tk.Tk()
    ComparisonApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
