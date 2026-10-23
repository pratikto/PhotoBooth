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
from photobooth.dither_autotune import AutoTuneCancelled, tune_dither

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
PIPELINE_SLIDERS = (
    ("clahe_strength", "CLAHE Strength", 0.0, 1.0),
    ("denoise_level", "Median Denoise (0–2)", 0, 2),
    ("tone_strength", "Tone Balance", 0.0, 1.0),
    ("dot_cleanup_level", "Selective Dot Cleanup (0–3)", 0, 3),
    ("edge_refine_level", "Edge Refinement (0–3)", 0, 3),
)
PIPELINE_LEVELS = {"denoise_level", "dot_cleanup_level", "edge_refine_level"}


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
        self.pipeline_controls = {}
        self.pipeline_flags = {}
        self.processing_presets = {}
        self.pipeline_sections = {}
        self.labels = {}
        self.statuses = {}
        self.scroll_canvases = {}
        self.print_events = queue.Queue()
        self.print_busy = False
        # Auto Tune never touches live printing or applies settings silently.
        # Worker events are marshalled to Tk through a queue.
        self.autotune_events = queue.Queue()
        self.autotune_generation = 0
        self.autotune_cancel_event = None
        self.autotune_busy = False
        self.autotune_result = None
        self.autotune_dialog = None
        self.autotune_photos = []
        self.autotune_selected = None
        self._setting_tuned_controls = False
        self.autotune_buttons = {}
        self.autotune_mode = None
        self.autotune_button = None  # compatibility alias for Floyd tests
        self.zoom = tk.IntVar(value=2)
        self.sync = tk.BooleanVar(value=False)
        self.width = tk.StringVar(value="576")
        self.enhanced_floyd = tk.BooleanVar(value=False)
        self.enhanced_dizzy = tk.BooleanVar(value=self.configs.dizzy.enhanced_dizzy)
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
            # Keep each experimental preprocessing switch in its own panel.
            # Sync Parameters applies to tonal sliders, not these checkboxes.
            if mode == "floyd-steinberg":
                ttk.Checkbutton(
                    panel, text="Enhanced Floyd (experimental)",
                    variable=self.enhanced_floyd,
                    command=self.toggle_enhanced,
                ).pack(fill="x", pady=(4, 0))
            elif mode == "dizzy":
                ttk.Checkbutton(
                    panel, text="Enhanced Dizzy (experimental)",
                    variable=self.enhanced_dizzy,
                    command=self.toggle_enhanced_dizzy,
                ).pack(fill="x", pady=(4, 0))

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

            # One-click A/B combinations preserve the manual processing
            # strengths, and can be overridden via the checkboxes below.
            ttk.Label(interior, text="Quick Processing A/B:").pack(
                fill="x", pady=(8, 1))
            preset = tk.StringVar(value="Original")
            self.processing_presets[mode] = preset
            preset_picker = ttk.Combobox(
                interior, textvariable=preset, state="readonly",
                values=("Original", "Smart Enhanced", "Smart + Post", "Post Only"))
            preset_picker.pack(fill="x", pady=(0, 3))
            preset_picker.bind(
                "<<ComboboxSelected>>",
                lambda _event, m=mode: self.processing_preset_changed(m))
            # Processing is opt-in and lane-specific, even when Sync is ON.
            self.pipeline_flags[mode] = {}
            for key, caption in (
                ("smart_enhance", "Smart Enhance (optional)"),
                ("postprocess_enabled", "1-bit Post-Processing (optional)"),
            ):
                enabled = tk.BooleanVar(value=getattr(self.configs.by_mode(mode), key))
                self.pipeline_flags[mode][key] = enabled
                ttk.Checkbutton(
                    interior, text=caption, variable=enabled,
                    command=lambda m=mode, k=key: self.pipeline_toggle(m, k),
                ).pack(fill="x", pady=(6, 0))

            toggle = ttk.Button(interior, text="Image Processing Options ▸")
            toggle.pack(fill="x", pady=(6, 2))
            advanced = ttk.Frame(interior)
            self.pipeline_sections[mode] = (toggle, advanced)
            toggle.configure(command=lambda m=mode: self.toggle_pipeline_options(m))
            self.pipeline_controls[mode] = {}
            for key, caption, lower, upper in PIPELINE_SLIDERS:
                strip = ttk.Frame(advanced)
                strip.pack(fill="x", pady=(4, 0))
                ttk.Label(strip, text=caption).pack(side="left")
                readout = ttk.Label(strip, text="", width=5, anchor="e")
                readout.pack(side="right")
                var = tk.DoubleVar(value=getattr(self.configs.by_mode(mode), key))
                ttk.Scale(
                    advanced, from_=lower, to=upper, variable=var,
                    command=lambda _value, m=mode, k=key: self.pipeline_changed(m, k),
                ).pack(fill="x")
                self.pipeline_controls[mode][key] = (var, readout)
                self.write_pipeline_value(mode, key)
            ttk.Label(
                advanced, text="Only applies when the matching option is checked.",
                wraplength=265, justify="left",
            ).pack(fill="x", pady=(4, 1))
            # Pack actions before the flexible controls grow: buttons and
            # readiness feedback cannot be pushed out of a small window.
            state = ttk.Label(panel, text="Awaiting preview", anchor="center")
            state.pack(side="bottom", fill="x")
            actions = ttk.Frame(panel)
            actions.pack(side="bottom", fill="x", pady=(6, 2))
            button = ttk.Button(
                actions, text="Auto Tune", command=lambda m=mode: self.start_auto_tune(m))
            button.pack(side="left", expand=True, fill="x", padx=(0, 5))
            self.autotune_buttons[mode] = button
            if mode == "floyd-steinberg":
                self.autotune_button = button
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

    def invalidate_auto_tune(self):
        """Cancel or dismiss stale candidate sets whenever tuned input changes."""
        self.autotune_generation += 1
        if self.autotune_cancel_event is not None:
            self.autotune_cancel_event.set()
        self.autotune_cancel_event = None
        self.autotune_busy = False
        self.autotune_result = None
        for button in self.autotune_buttons.values():
            button.configure(text="Auto Tune")
        self.autotune_mode = None
        if self.autotune_dialog is not None:
            if self.autotune_dialog.winfo_exists():
                self.autotune_dialog.destroy()
            self.autotune_dialog = None
        self.autotune_photos = []

    def start_auto_tune(self, mode="floyd-steinberg"):
        """Start a bounded, cancellable search without blocking Tk widgets."""
        if mode not in VISIBLE_MODES:
            raise ValueError("Auto Tune requires a visible algorithm.")
        if self.autotune_busy:
            previous_mode = self.autotune_mode
            self.invalidate_auto_tune()
            if mode == previous_mode:
                self.message.set("Auto Tune cancelled. No settings changed.")
                return
        if self.autotune_result is not None:
            if mode == self.autotune_mode:
                self.show_auto_tune_candidates()
                return
            self.invalidate_auto_tune()
        # System-neutral tuning never reads or changes the manual sliders.
        profile = DitherProfile(mode=mode, width_dots=self.configs.by_mode(mode).width_dots,
                                enhanced_floyd=(mode == "floyd-steinberg"))
        source = self.source.copy()
        self.autotune_generation += 1
        generation = self.autotune_generation
        cancel_event = threading.Event()
        self.autotune_cancel_event = cancel_event
        self.autotune_busy = True
        self.autotune_mode = mode
        self.autotune_buttons[mode].configure(text="Cancel Tune")
        self.message.set(f"Auto Tune: searching {SHORT[mode]} presets...")
        def on_progress(n, phase):
            self.autotune_events.put(
                ("progress", generation, (n, phase)))
        def worker():
            try:
                result = tune_dither(
                    source, profile, should_cancel=cancel_event.is_set,
                    on_progress=on_progress)
                self.autotune_events.put(("complete", generation, result))
            except AutoTuneCancelled:
                self.autotune_events.put(("cancelled", generation, None))
            except Exception as error:
                self.autotune_events.put(("error", generation, str(error)))
        threading.Thread(
            target=worker, daemon=True, name=f"meong-auto-tune-{mode}").start()

    def poll_auto_tune(self):
        while True:
            try:
                event, generation, payload = self.autotune_events.get_nowait()
            except queue.Empty:
                break
            if generation != self.autotune_generation or self.closed:
                continue  # Ignore stale results after change/cancellation.
            if event == "progress":
                evaluated, stage = payload
                self.message.set(f"Auto Tune: {stage} — {evaluated} settings evaluated...")
                continue
            self.autotune_busy = False
            self.autotune_cancel_event = None
            self.autotune_buttons[self.autotune_mode].configure(text="Auto Tune")
            if event == "complete":
                self.autotune_result = payload
                self.message.set(
                    f"Auto Tune ready: {payload.trials} evaluations; "
                    "choose a candidate to apply or save.")
                self.show_auto_tune_candidates()
            elif event == "error":
                self.message.set("Auto Tune failed; manual settings unchanged.")
                messagebox.showerror("Auto Tune failed", payload, parent=self.root)
            elif event == "cancelled":
                self.message.set("Auto Tune cancelled; settings unchanged.")

    def dismiss_auto_tune_candidates(self):
        if self.autotune_dialog is not None:
            if self.autotune_dialog.winfo_exists():
                self.autotune_dialog.destroy()
            self.autotune_dialog = None
            self.autotune_photos = []

    def show_auto_tune_candidates(self):
        """Review three distinct native-dot previews before selecting."""
        if self.autotune_result is None:
            return
        self.dismiss_auto_tune_candidates()
        dialog = tk.Toplevel(self.root)
        self.autotune_dialog = dialog
        dialog.title(f"MEONG | {SHORT[self.autotune_mode]} Auto Tune — 3 candidates")
        dialog.geometry("975x690")
        dialog.minsize(820, 590)
        dialog.protocol("WM_DELETE_WINDOW", self.dismiss_auto_tune_candidates)
        ttk.Label(
            dialog, text="Digital fidelity ranking — NOT calibrated paper quality",
            font=("Segoe UI", 12, "bold")
        ).pack(padx=12, pady=(12, 4))
        ttk.Label(
            dialog, text=f"Auto Tune ignores manual sliders and searches {SHORT[self.autotune_mode]}. "
                         "No changes are applied or printed until you choose Apply. "
                         "Print Test separately to judge real paper.",
            wraplength=820, justify="center"
        ).pack(padx=12, pady=(0, 8))

        baseline = self.autotune_result.baseline
        gain = self.autotune_result.candidates[0].score - baseline.score
        self.autotune_baseline_text = (
            f"System neutral: {baseline.score:.1f}/100. "
            f"Best candidate: {gain:+.2f} points vs neutral. "
            + ("No digital improvement; keep manual settings or compare on paper."
               if gain <= 0 else "Confirm the difference on paper."))
        ttk.Label(dialog, text=self.autotune_baseline_text, wraplength=820,
                  justify="center").pack(padx=12, pady=(0, 8))

        cards = ttk.Frame(dialog, padding=(8, 0, 8, 4))
        cards.pack(fill="both", expand=True)
        self.autotune_selected = tk.IntVar(value=0)
        for index, candidate in enumerate(self.autotune_result.candidates):
            cards.columnconfigure(index, weight=1, uniform="candidate")
            card = ttk.LabelFrame(
                cards, text=f"#{index + 1} • score {candidate.score:.1f}/100",
                padding=8)
            card.grid(row=0, column=index, padx=4, sticky="nsew")
            preview = candidate.raster.convert("L")
            preview.thumbnail((230, 270), Image.Resampling.BOX)
            photo = ImageTk.PhotoImage(preview, master=dialog)
            self.autotune_photos.append(photo)
            ttk.Label(card, image=photo, anchor="center").pack(fill="x")
            ttk.Radiobutton(
                card, text="Select candidate", value=index,
                variable=self.autotune_selected
            ).pack(anchor="w", pady=(7, 2))
            p = candidate.profile
            ttk.Label(
                card,
                text=(f"Brightness {p.brightness:.3f}   Contrast {p.contrast:.3f}\n"
                      f"Gamma {p.gamma:.3f}   Sharpness {p.sharpness:.3f}\n"
                      + (f"Dizzy: {p.dizzy_variant}, enhanced={p.enhanced_dizzy}\n"
                         if p.mode == "dizzy" else "")
                      + (f"Threshold: {p.threshold}\n" if p.mode == "threshold" else "")
                      + (f"Smart: CLAHE {p.clahe_strength:.2f}, Denoise {p.denoise_level}, "
                         f"Tone {p.tone_strength:.2f}\n" if p.smart_enhance
                         else "Smart: OFF\n")
                      + (f"Post: Dots {p.dot_cleanup_level}, Edges {p.edge_refine_level}\n"
                         if p.postprocess_enabled else "Post: OFF\n")
                      + f"Black dots {candidate.black_coverage:.1f}%\n"
                      f"Vs neutral {candidate.score - baseline.score:+.2f} points\n"
                      f"Tonal error {candidate.tone_error:.1f}   "
                      f"Edge error {candidate.edge_error:.1f}"),
                justify="left",
            ).pack(anchor="w", pady=3)
        controls = ttk.Frame(dialog, padding=10)
        controls.pack(fill="x")
        ttk.Button(controls, text="Apply Best",
                   command=lambda: self.apply_auto_tune_candidate(0)).pack(
                       side="left", padx=(0, 6))
        ttk.Button(controls, text="Apply Selected",
                   command=self.apply_auto_tune_candidate).pack(
                       side="left", padx=(0, 6))
        ttk.Button(controls, text="Save Selected Preset",
                   command=self.save_auto_tune_preset).pack(
                       side="left", padx=(0, 6))
        ttk.Button(controls, text="Close",
                   command=self.dismiss_auto_tune_candidates).pack(side="right")

    def chosen_auto_tune_candidate(self, index=None):
        if self.autotune_result is None:
            return None
        if index is None:
            index = self.autotune_selected.get()
        if not (0 <= index < len(self.autotune_result.candidates)):
            return None
        return self.autotune_result.candidates[index]

    def apply_auto_tune_candidate(self, index=None):
        candidate = self.chosen_auto_tune_candidate(index)
        if candidate is None:
            return
        mode = candidate.profile.mode
        # Apply only one lane, regardless of Sync Parameters.
        self.invalidate_auto_tune()
        self._setting_tuned_controls = True
        try:
            self.configs = self.configs.replace_lane(candidate.profile)
            if mode == "floyd-steinberg":
                self.enhanced_floyd.set(candidate.profile.enhanced_floyd)
            if mode == "dizzy":
                self.enhanced_dizzy.set(candidate.profile.enhanced_dizzy)
                self.dizzy_variant.set(candidate.profile.dizzy_variant)
                self.dizzy_seed_label.configure(text=f"Seed: {candidate.profile.dizzy_seed}")
            for key, (var, _label) in self.controls[mode].items():
                var.set(getattr(candidate.profile, key))
                self.write_value(mode, key)
            self.set_pipeline_profile(mode, candidate.profile)
        finally:
            self._setting_tuned_controls = False
        self.schedule(mode)
        self.message.set(
            f"Applied Auto Tune to {SHORT[mode]} only. "
            "Use Save All Configs to keep it; print quality requires paper review.")

    def save_auto_tune_preset(self):
        candidate = self.chosen_auto_tune_candidate()
        if candidate is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"meong-{candidate.profile.mode}-autotune-lab-v5.json",
            filetypes=[("JSON", "*.json")],
            parent=self.autotune_dialog or self.root)
        if not path:
            return
        try:
            # Use the same full comparison schema as "Load All Configs".
            # A saved candidate is NOT implicitly applied to the live GUI.
            saved_configs = self.configs.replace_lane(candidate.profile)
            save_comparison(path, saved_configs)
            self.message.set(
                f"Saved Auto Tune lab config: {path} "
                "(loadable via Load All Configs; no settings applied).")
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Save preset failed", str(error),
                parent=self.autotune_dialog or self.root)

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

    def processing_preset_changed(self, mode):
        """Select baseline, Smart, Smart + Post or post only for one lane."""
        if self._setting_tuned_controls:
            return
        modes = {
            "Original": (False, False),
            "Smart Enhanced": (True, False),
            "Smart + Post": (True, True),
            "Post Only": (False, True),
        }
        selected = self.processing_presets[mode].get()
        if selected not in modes:
            raise ValueError("Unknown processing A/B preset.")
        if self.autotune_mode == mode:
            self.invalidate_auto_tune()
        smart, post = modes[selected]
        self.pipeline_flags[mode]["smart_enhance"].set(smart)
        self.pipeline_flags[mode]["postprocess_enabled"].set(post)
        profile = self.configs.by_mode(mode)
        self.configs = self.configs.replace_lane(replace(
            profile, smart_enhance=smart, postprocess_enabled=post))
        self.schedule(mode)

    def refresh_processing_preset(self, mode):
        smart = self.pipeline_flags[mode]["smart_enhance"].get()
        post = self.pipeline_flags[mode]["postprocess_enabled"].get()
        selected = ("Smart + Post" if smart and post else
                    "Smart Enhanced" if smart else
                    "Post Only" if post else "Original")
        self.processing_presets[mode].set(selected)

    def toggle_pipeline_options(self, mode):
        """Keep advanced sliders compact inside the existing scrollable lane."""
        button, advanced = self.pipeline_sections[mode]
        if advanced.winfo_manager():
            advanced.pack_forget()
            button.configure(text="Image Processing Options ▸")
        else:
            advanced.pack(fill="x", after=button)
            button.configure(text="Image Processing Options ▾")

    def write_pipeline_value(self, mode, key):
        var, label = self.pipeline_controls[mode][key]
        value = var.get()
        label.configure(text=str(int(round(value))) if key in PIPELINE_LEVELS
                        else f"{value:.2f}")

    def set_pipeline_profile(self, mode, profile):
        """Refresh every processing widget without changing other lanes."""
        for key, flag in self.pipeline_flags[mode].items():
            flag.set(getattr(profile, key))
        for key, (var, _readout) in self.pipeline_controls[mode].items():
            var.set(getattr(profile, key))
            self.write_pipeline_value(mode, key)
        self.refresh_processing_preset(mode)

    def pipeline_toggle(self, mode, key):
        if self._setting_tuned_controls:
            return
        if self.autotune_mode == mode:
            self.invalidate_auto_tune()
        profile = self.configs.by_mode(mode)
        self.configs = self.configs.replace_lane(
            replace(profile, **{key: self.pipeline_flags[mode][key].get()}))
        self.refresh_processing_preset(mode)
        self.schedule(mode)

    def pipeline_changed(self, mode, key):
        if self._setting_tuned_controls:
            return
        if self.autotune_mode == mode:
            self.invalidate_auto_tune()
        self.write_pipeline_value(mode, key)
        raw = self.pipeline_controls[mode][key][0].get()
        value = int(round(raw)) if key in PIPELINE_LEVELS else round(raw, 3)
        profile = self.configs.by_mode(mode)
        self.configs = self.configs.replace_lane(replace(profile, **{key: value}))
        self.schedule(mode)

    def toggle_enhanced(self):
        if self.autotune_mode == "floyd-steinberg":
            self.invalidate_auto_tune()
        p = self.configs.floyd
        self.configs = self.configs.replace_lane(replace(p, enhanced_floyd=self.enhanced_floyd.get()))
        self.schedule("floyd-steinberg")

    def toggle_enhanced_dizzy(self):
        if self.autotune_mode == "dizzy":
            self.invalidate_auto_tune()
        profile = self.configs.dizzy
        self.configs = self.configs.replace_lane(
            replace(profile, enhanced_dizzy=self.enhanced_dizzy.get()))
        self.schedule("dizzy")

    def change_dizzy_variant(self, _event=None):
        if self.autotune_mode == "dizzy":
            self.invalidate_auto_tune()
        profile = self.configs.dizzy
        self.configs = self.configs.replace_lane(
            replace(profile, dizzy_variant=self.dizzy_variant.get()))
        self.schedule("dizzy")

    def change_zoom(self, factor):
        self.zoom.set(factor)
        for mode, image in self.results.items():
            self.show_image(mode, image)

    def change_width(self, _event=None):
        self.invalidate_auto_tune()
        # Keep the hidden Threshold profile width aligned for old JSON files;
        # render only the three visible methods.
        for mode in LAB_DITHER_MODES:
            self.configs = self.configs.replace_lane(
                replace(self.configs.by_mode(mode), width_dots=int(self.width.get())))
        for mode in VISIBLE_MODES:
            self.schedule(mode)

    def slider_changed(self, mode, key):
        if self._setting_tuned_controls:
            return
        if self.autotune_mode in (VISIBLE_MODES if self.sync.get() else (mode,)):
            self.invalidate_auto_tune()
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
                    suffix = (
                        f" | {profile.dizzy_variant} / seed {profile.dizzy_seed}"
                        f" | {'enhanced' if profile.enhanced_dizzy else 'baseline'}"
                        if mode == "dizzy" else
                        " | enhanced" if profile.enhanced_floyd else " | baseline"
                    )
                    self.statuses[mode].configure(
                        text=f"Ready{suffix} • {elapsed * 1000:.0f} ms")
            if mode in self.queued or version != self.versions[mode]:
                self.queued.discard(mode)
                if mode in self.timers:
                    self.root.after_cancel(self.timers.pop(mode))
                self.launch(mode)
        self.poll_auto_tune()
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
        self.invalidate_auto_tune()
        self.source, self.source_label = candidate, Path(path).name
        self.refresh_source()
        for mode in VISIBLE_MODES:
            self.schedule(mode)

    def apply_configs(self, configs):
        self.invalidate_auto_tune()
        self._setting_tuned_controls = True
        self.configs = configs
        self.width.set(str(configs.floyd.width_dots))
        self.enhanced_floyd.set(configs.floyd.enhanced_floyd)
        self.enhanced_dizzy.set(configs.dizzy.enhanced_dizzy)
        self.dizzy_variant.set(configs.dizzy.dizzy_variant)
        self.dizzy_seed_label.configure(text=f"Seed: {configs.dizzy.dizzy_seed}")
        for mode in VISIBLE_MODES:
            for key, (var, _label) in self.controls[mode].items():
                var.set(getattr(configs.by_mode(mode), key))
                self.write_value(mode, key)
            self.set_pipeline_profile(mode, configs.by_mode(mode))
            self.schedule(mode)
        self._setting_tuned_controls = False

    def reset(self):
        self.apply_configs(ComparisonProfiles())

    def save_all(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
            initialfile="meong-dither-lab-v5.json", filetypes=[("JSON", "*.json")])
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
            stem = "meong-floyd-{}".format(
                "enhanced" if profile.enhanced_floyd else "baseline")
        elif profile.mode == "dizzy":
            quality = "enhanced" if profile.enhanced_dizzy else "baseline"
            stem = f"meong-dizzy-{profile.dizzy_variant}-seed{profile.dizzy_seed}-{quality}"
        else:
            stem = f"meong-{profile.mode}"
        # Keep legacy default names, but never overwrite saved A/B variants
        # under an indistinguishable filename.
        if profile.smart_enhance:
            stem += "-smart"
        if profile.postprocess_enabled:
            stem += "-post"
        return f"{stem}.png"

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
        self.invalidate_auto_tune()
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
